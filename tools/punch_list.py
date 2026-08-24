"""Deterministic checks and session digest for `docs/PUNCH_LIST.md`.

Grooming a punch list is two different jobs. One half is mechanical: an id
used twice, an entry that has outgrown its brief, an item still marked
blocked by something that already landed. Those are decidable by reading the
file, so they are checked here and never left to a human or a model to
notice. The other half is judgment - whether the top `P1` is still the right
next thing, whether an entry should be split - which this tool deliberately
does not attempt. It only detects the conditions that make that judgment
worth spending a session on, and says so.

Two modes:

- `check`   full report. Errors exit non-zero and gate `make check`;
            grooming advisories are informational and never fail a build.
- `digest`  the few lines injected at session start by the `SessionStart`
            hook, including an advisory count when grooming is due.

Standard library only, so the session-start hook does not depend on the
project virtualenv being synced.
"""

from __future__ import annotations

import argparse
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

PRIORITIES = ("P0", "P1", "P2", "P3")
EFFORTS = ("S", "M", "L")
STATUSES = ("ready", "needs-decision", "blocked")

# Classes whose subject matter is safety-critical under CLAUDE.md, and so may
# not sit in the lower priority bands however small the task looks.
SAFETY_CLASSES = ("safety", "science")

# A brief longer than this has stopped being a brief; the excess is narrative
# and belongs in docs/WORKING_NOTES.md. The file asks for roughly twenty
# lines; this leaves real headroom above that, because an advisory that
# fires on a one-line edit is an advisory that gets ignored.
MAX_ENTRY_LINES = 28

# Beyond this the queue is too long to be a queue.
MAX_OPEN_ITEMS = 18
MAX_COMPLETED_ITEMS = 10

# An item nobody has touched in this long is either not real or mis-prioritized.
STALE_AFTER_DAYS = 120

ENTRY_RE = re.compile(r"^### (PL-(\d+))\s+(.+?)\s*$")
BAND_RE = re.compile(r"^##\s+(P[0-3])\b")
COMPLETED_RE = re.compile(r"^-\s+(PL-\d+)\b")
REFERENCE_RE = re.compile(r"\bPL-\d+\b")
ADDED_RE = re.compile(r"\badded (\d{4}-\d{2}-\d{2})\b")
BLOCKED_BY_RE = re.compile(r"\*\*Blocked by\.\*\*(.+?)(?=\n\*\*|\Z)", re.DOTALL)
CODE_TOKEN_RE = re.compile(r"`([^`]+)`")


@dataclass(frozen=True)
class Entry:
    """One punch-list item, as parsed from its heading and metadata line."""

    identifier: str
    number: int
    title: str
    priority: str
    effort: str
    status: str
    classes: tuple[str, ...]
    added: date | None
    band: str
    line: int
    body: str

    @property
    def line_count(self) -> int:
        return len(self.body.splitlines())

    @property
    def blockers(self) -> tuple[str, ...]:
        """Items this one waits on.

        Read from the `**Blocked by.**` line when there is one, so that a
        passing mention of another item elsewhere in the brief is not
        mistaken for a dependency.
        """
        declared = BLOCKED_BY_RE.search(self.body)
        source = declared.group(1) if declared else self.body
        return tuple(ref for ref in REFERENCE_RE.findall(source) if ref != self.identifier)

    @property
    def model_guidance(self) -> str | None:
        """Whether CLAUDE.md's model-matching rule flags this item.

        Mirrors "Session and tool-use efficiency": a safety- or
        science-classed item, or one still at `needs-decision`, is
        reasoning-heavy work that warrants the strongest available model at
        high effort - not the default model used for routine execution.
        Returns the trigger as a short label, or None when routine
        execution is expected to suffice. This exists so the
        recommendation does not depend on a session remembering to apply
        the rule by hand each time.
        """
        safety = [c for c in self.classes if c in SAFETY_CLASSES]
        if safety:
            return f"{'/'.join(safety)}-tagged"
        if self.status == "needs-decision":
            return "open design decision"
        return None


@dataclass
class Report:
    """Findings, split by whether a machine or a human has to resolve them."""

    entries: list[Entry] = field(default_factory=list)
    completed: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    advisories: list[str] = field(default_factory=list)

    @property
    def counts(self) -> dict[str, int]:
        return {p: sum(1 for e in self.entries if e.priority == p) for p in PRIORITIES}


def _parse_metadata(line: str) -> tuple[str, str, str, tuple[str, ...], date | None]:
    """Pull priority, effort, status, classes, and date out of a metadata line.

    Parsed by token rather than by position so that reordering or adding a
    class does not silently change what is read.
    """
    tokens = CODE_TOKEN_RE.findall(line)
    priority = next((t for t in tokens if t in PRIORITIES), "")
    effort = next((t for t in tokens if t in EFFORTS), "")
    classes = tuple(t for t in tokens if t not in PRIORITIES and t not in EFFORTS)
    status = next((s for s in STATUSES if re.search(rf"(?<![\w-]){s}(?![\w-])", line)), "")
    match = ADDED_RE.search(line)
    added = date.fromisoformat(match.group(1)) if match else None
    return priority, effort, status, classes, added


def parse(text: str) -> Report:
    """Parse the punch list into entries and completed ids.

    Fenced blocks are skipped so the entry-format example in the file's own
    header is never mistaken for a real item.
    """
    report = Report()
    lines = text.splitlines()
    band = ""
    fenced = False
    index = 0

    while index < len(lines):
        line = lines[index]

        if line.startswith("```"):
            fenced = not fenced
            index += 1
            continue
        if fenced:
            index += 1
            continue

        band_match = BAND_RE.match(line)
        if band_match:
            band = band_match.group(1)
        elif line.startswith("## "):
            band = "completed" if line.startswith("## Recently completed") else ""

        if band == "completed":
            completed_match = COMPLETED_RE.match(line)
            if completed_match:
                report.completed.append(completed_match.group(1))
            index += 1
            continue

        entry_match = ENTRY_RE.match(line)
        if not entry_match:
            index += 1
            continue

        heading_line = index + 1
        identifier, number, title = entry_match.groups()

        body_lines: list[str] = []
        index += 1
        while index < len(lines) and not lines[index].startswith(("### ", "## ")):
            body_lines.append(lines[index])
            index += 1
        body = "\n".join(body_lines)

        metadata = next((entry for entry in body_lines if entry.strip()), "")
        priority, effort, status, classes, added = _parse_metadata(metadata)

        report.entries.append(
            Entry(
                identifier=identifier,
                number=int(number),
                title=title,
                priority=priority,
                effort=effort,
                status=status,
                classes=classes,
                added=added,
                band=band,
                line=heading_line,
                body=body,
            )
        )

    return report


def _check_entry(entry: Entry, report: Report) -> None:
    """Validate one entry against the format the punch list documents."""
    where = f"{entry.identifier} (line {entry.line})"

    if not entry.priority:
        report.errors.append(f"{where}: no priority; expected one of {', '.join(PRIORITIES)}")
    elif entry.band and entry.band != entry.priority:
        report.errors.append(
            f"{where}: filed under the {entry.band} section but marked {entry.priority}"
        )

    if not entry.effort:
        report.errors.append(f"{where}: no effort estimate; expected one of {', '.join(EFFORTS)}")
    if not entry.status:
        report.errors.append(f"{where}: no status; expected one of {', '.join(STATUSES)}")
    if entry.added is None:
        report.errors.append(f"{where}: no 'added YYYY-MM-DD' date")

    required = ["**Problem.**", "**Why it matters.**", "**Where.**"]
    if entry.status != "blocked":
        required.append("**Done when.**")
    missing = [marker for marker in required if marker not in entry.body]
    if missing:
        report.errors.append(f"{where}: brief is missing {', '.join(missing)}")

    if entry.status == "blocked" and not entry.blockers:
        report.errors.append(f"{where}: marked blocked but names no blocking PL- item")

    if entry.status == "needs-decision" and not re.search(
        r"\*\*(Decision needed|Open questions?)\.?\*\*", entry.body
    ):
        report.errors.append(
            f"{where}: marked needs-decision but states no decision to make; "
            "add a **Decision needed.** line so a later session can answer it"
        )

    safety = [c for c in entry.classes if c in SAFETY_CLASSES]
    if safety and entry.priority in ("P2", "P3"):
        report.errors.append(
            f"{where}: class '{', '.join(safety)}' sits at {entry.priority}; "
            "safety-critical work starts at P0 or P1 per CLAUDE.md"
        )


def _groom(report: Report, today: date, related: dict[Path, str]) -> None:
    """Flag the conditions that make a grooming pass worth a session."""
    completed = set(report.completed)

    for entry in report.entries:
        if entry.line_count > MAX_ENTRY_LINES:
            report.advisories.append(
                f"{entry.identifier}: brief has grown to {entry.line_count} lines; "
                "move the narrative to docs/WORKING_NOTES.md"
            )
        if entry.status == "blocked":
            landed = [ref for ref in entry.blockers if ref in completed]
            if landed:
                report.advisories.append(
                    f"{entry.identifier}: blocked by {', '.join(landed)}, which has landed; "
                    "promote it to ready"
                )
        if entry.effort == "L" and entry.priority != "P3":
            report.advisories.append(
                f"{entry.identifier}: sized L outside the icebox; "
                "scope it into a ROADMAP.md milestone or demote it"
            )
        if entry.added is not None and entry.priority in ("P1", "P2"):
            age = (today - entry.added).days
            if age > STALE_AFTER_DAYS:
                report.advisories.append(
                    f"{entry.identifier}: {age} days old and still {entry.priority}; "
                    "do it, demote it, or drop it"
                )

    if len(report.entries) > MAX_OPEN_ITEMS:
        report.advisories.append(
            f"queue: {len(report.entries)} open items; a queue this long stops being read"
        )
    if len(report.completed) > MAX_COMPLETED_ITEMS:
        report.advisories.append(
            f"archive: {len(report.completed)} completed items; trim the ones that have "
            "stopped being useful history"
        )
    if not any(
        e.effort == "S" and e.status == "ready" and e.priority != "P3" for e in report.entries
    ):
        report.advisories.append(
            "queue: nothing is both ready and sized S, so a short session has nothing to "
            "pick up; consider splitting a larger item"
        )

    known = {e.identifier for e in report.entries} | completed
    for path, text in related.items():
        for reference in sorted(set(REFERENCE_RE.findall(text))):
            if reference not in known:
                report.errors.append(
                    f"{path}: references {reference}, which is in neither the queue nor "
                    "the completed archive"
                )
            elif reference in completed and path.name == "WORKING_NOTES.md":
                report.advisories.append(
                    f"{path}: still carries a thread for {reference}, which is completed; "
                    "delete it rather than leaving it stale"
                )


def analyze(text: str, today: date, related: dict[Path, str] | None = None) -> Report:
    """Parse, validate, and groom in one pass."""
    report = parse(text)

    seen: dict[str, Entry] = {}
    for entry in report.entries:
        if entry.identifier in seen:
            report.errors.append(
                f"{entry.identifier} (line {entry.line}): id already used at line "
                f"{seen[entry.identifier].line}; ids are never reused"
            )
        else:
            seen[entry.identifier] = entry
        _check_entry(entry, report)

    for identifier in report.completed:
        if identifier in seen:
            report.errors.append(
                f"{identifier}: listed as completed but still open at line {seen[identifier].line}"
            )

    _groom(report, today, related or {})
    return report


def _plural(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}"


def format_check(report: Report) -> str:
    """Render the full report."""
    counts = report.counts
    lines = [
        f"docs/PUNCH_LIST.md: {len(report.entries)} open "
        f"({', '.join(f'{n} {p}' for p, n in counts.items())}), "
        f"{_plural(len(report.errors), 'error', 'errors')}, "
        f"{_plural(len(report.advisories), 'advisory', 'advisories')}"
    ]
    if report.errors:
        lines.append("")
        lines.append("Errors (the file is wrong; fix before committing):")
        lines.extend(f"  {message}" for message in report.errors)
    if report.advisories:
        lines.append("")
        lines.append(
            "Grooming advisories (judgment needed; run the punch-list skill's groom mode):"
        )
        lines.extend(f"  {message}" for message in report.advisories)
    if not report.errors and not report.advisories:
        lines.append("No errors, nothing due for grooming.")
    return "\n".join(lines)


def _with_guidance(line: str, entry: Entry) -> str:
    """Append the model-matching note to a digest line, if the entry has one."""
    if entry.model_guidance is None:
        return line
    return f"{line} - {entry.model_guidance}: use opusplan or your strongest model, high effort"


def format_digest(report: Report) -> str:
    """Render the few lines injected into session context at startup.

    Kept short on purpose: this text is resent on every turn of the session.
    """
    if not report.entries:
        return ""

    counts = report.counts
    lines = [
        f"Punch list (docs/PUNCH_LIST.md): {len(report.entries)} open - "
        f"{', '.join(f'{n} {p}' for p, n in counts.items())}."
    ]

    for entry in (e for e in report.entries if e.priority == "P0"):
        lines.append(
            _with_guidance(
                f"  P0 (hotfix, before feature work): {entry.identifier} {entry.title} "
                f"({entry.effort}, {entry.status})",
                entry,
            )
        )

    top = next((e for e in report.entries if e.priority == "P1"), None)
    if top is not None:
        lines.append(
            _with_guidance(
                f"  Top P1: {top.identifier} {top.title} ({top.effort}, {top.status})", top
            )
        )

    if report.errors:
        lines.append(
            f"  {_plural(len(report.errors), 'format error', 'format errors')} in the "
            "punch list itself; run `make punch-list`."
        )
    if report.advisories:
        lines.append(
            f"  Grooming due: {_plural(len(report.advisories), 'advisory', 'advisories')} "
            "(`make punch-list` to see them). Offer a grooming pass before taking new work."
        )

    lines.append(
        "Read the file before recommending what to work on. Any finding not fixed this "
        "session gets an entry there before the session ends."
    )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("mode", choices=("check", "digest"))
    parser.add_argument("--file", type=Path, default=None, help="path to the punch list")
    parser.add_argument("--today", type=date.fromisoformat, default=None, help="reference date")
    args = parser.parse_args(argv)

    path = args.file or Path(__file__).resolve().parent.parent / "docs" / "PUNCH_LIST.md"
    if not path.is_file():
        # A checkout without a punch list is not an error, especially at
        # session start where this must never be noise.
        return 0

    # Resolved relative to the punch list being checked, not to this file, so
    # that checking a copy elsewhere does not cross-reference the repository's
    # own notes against it.
    docs = path.resolve().parent
    related = {
        candidate: candidate.read_text(encoding="utf-8")
        for candidate in (docs / "WORKING_NOTES.md", docs.parent / "ROADMAP.md")
        if candidate.is_file()
    }
    report = analyze(path.read_text(encoding="utf-8"), args.today or date.today(), related)

    if args.mode == "digest":
        digest = format_digest(report)
        if digest:
            print(digest)
        return 0

    print(format_check(report))
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
