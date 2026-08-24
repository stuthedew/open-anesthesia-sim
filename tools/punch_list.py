"""Deterministic checks and session digest for `docs/PUNCH_LIST.md`.

Grooming a punch list is two different jobs. One half is mechanical: an id
used twice, an entry that has outgrown its brief, an item still marked
blocked by something that already landed. Those are decidable by reading the
file, so they are checked here and never left to a human or a model to
notice. The other half is judgment - whether the top `P1` is still the right
next thing, whether an entry should be split - which this tool deliberately
does not attempt. It only detects the conditions that make that judgment
worth spending a session on, and says so.

An item leaves the queue in one of two ways, and both are recorded rather
than deleted: it is completed with a commit reference, or it is closed
without action - dropped, folded into another entry, superseded. Ids in
either record still resolve, so a `PL-` reference from `ROADMAP.md` or
`docs/WORKING_NOTES.md` does not dangle once the item has been archived.

Three modes:

- `check`   full report. Errors exit non-zero and gate `make check`;
            grooming advisories are informational and never fail a build.
- `digest`  the few lines injected at session start by the `SessionStart`
            hook, including an advisory count when grooming is due and, when
            `--branch` names a branch that cannot carry an item id, where to
            put the id instead.
- `list`    one line per open item. The cheap way to see the whole queue:
            reading the file itself costs roughly twenty-five times as much,
            and most of that is brief prose that only matters once an item
            has been chosen.

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

# Classes that describe work on the development process rather than on the
# simulator: the punch list itself, the checkers, the documentation about how
# to work here. An entry counts as process work only when every one of its
# classes is in this set, so a `science`-and-`infra` item is still science.
#
# These are worth doing - their payoff compounds across sessions, which is why
# the capture rule promotes them - but the promotion has no natural ceiling,
# and left unchecked they colonize the top band ahead of the product work.
PROCESS_CLASSES = ("session-cost", "docs", "infra")

# A brief longer than this has stopped being a brief; the excess is narrative
# and belongs in docs/WORKING_NOTES.md. The file asks for roughly twenty
# lines; this leaves real headroom above that, because an advisory that
# fires on a one-line edit is an advisory that gets ignored.
MAX_ENTRY_LINES = 28

# Beyond this the queue has probably stopped being a queue and started being a
# backlog. This is deliberately loose: a long *accurate* queue is not itself a
# problem, and an advisory that fires on a healthy file is one that gets
# ignored. What actually makes a queue unreadable is the shape of its top band,
# which the three checks below measure directly.
MAX_OPEN_ITEMS = 25

# How many items the top band can hold before "what is next?" stops having an
# answer. Nobody reads a queue by its total; they read the band at the top.
MAX_BAND_ITEMS = 5

# A branch whose name leads with a punch-list id keeps the work findable from
# the entry long after the branch itself is gone. Not every surface allows it:
# a branch generated for a session before that session starts - Claude Code on
# the web derives one from the opening message - is fixed before the queue has
# been read, so an item chosen mid-session can never reach it. The digest
# detects that case and points the session at the artifacts it *can* still
# name. Requiring the hyphen keeps a random branch suffix from matching.
BRANCH_ID = re.compile(r"\bpl-\d+", re.IGNORECASE)

# Beyond this, "Recently completed" has stopped being recent. The excess moves
# to the permanent archive ledger rather than being deleted, so the ids keep
# resolving.
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
    archived: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    advisories: list[str] = field(default_factory=list)

    @property
    def resolved(self) -> set[str]:
        """Every id that has left the queue, however it left.

        A reference resolves against this rather than against the recent
        completions alone, so aging an item out of "Recently completed" or
        closing one without action never turns a live cross-reference into a
        build error.
        """
        return set(self.completed) | set(self.archived)

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
    """Parse the punch list into open entries and resolved ids.

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
            if line.startswith("## Recently completed"):
                band = "completed"
            elif line.startswith("## Archive"):
                band = "archive"
            else:
                band = ""

        if band in ("completed", "archive"):
            resolved_match = COMPLETED_RE.match(line)
            if resolved_match:
                target = report.completed if band == "completed" else report.archived
                target.append(resolved_match.group(1))
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


def _is_process_work(entry: Entry) -> bool:
    """Whether this item improves how the project is developed, not the app."""
    return bool(entry.classes) and all(c in PROCESS_CLASSES for c in entry.classes)


def _groom_top_band(report: Report) -> None:
    """Flag a top band that has stopped answering "what should we do next?".

    Total queue length is a weak proxy for that question: a session reads the
    band it would pick from, not the whole file. Three things make that band
    unreadable, and each is checked directly - it is too wide, too little of it
    can actually be started, or process work has crowded out the product.
    """
    band = next((p for p in ("P0", "P1") if any(e.priority == p for e in report.entries)), None)
    if band is None:
        return
    items = [e for e in report.entries if e.priority == band]

    if len(items) > MAX_BAND_ITEMS:
        report.advisories.append(
            f"{band}: {len(items)} items in the top band; more than about {MAX_BAND_ITEMS} "
            'and "what is next?" has no answer - demote the ones that are not'
        )

    undecided = [e for e in items if e.status == "needs-decision"]
    startable = [e for e in items if e.status == "ready"]
    if undecided and len(undecided) >= len(startable):
        report.advisories.append(
            f"{band}: {len(undecided)} of {len(items)} items are needs-decision and only "
            f"{len(startable)} ready; schedule the decisions, they are the work"
        )

    process = [e for e in items if _is_process_work(e)]
    if len(process) > len(items) - len(process):
        report.advisories.append(
            f"{band}: {len(process)} of {len(items)} items are process work "
            f"({', '.join(e.identifier for e in process)}); CLAUDE.md ranks the "
            "simulator's correctness above the workflow that builds it"
        )


def _groom(report: Report, today: date, related: dict[Path, str]) -> None:
    """Flag the conditions that make a grooming pass worth a session."""
    resolved = report.resolved

    for entry in report.entries:
        if entry.line_count > MAX_ENTRY_LINES:
            report.advisories.append(
                f"{entry.identifier}: brief has grown to {entry.line_count} lines; "
                "move the narrative to docs/WORKING_NOTES.md"
            )
        if entry.status == "blocked":
            landed = [ref for ref in entry.blockers if ref in resolved]
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

    _groom_top_band(report)

    if len(report.entries) > MAX_OPEN_ITEMS:
        report.advisories.append(
            f"queue: {len(report.entries)} open items; consider whether P3 has stopped "
            "being an icebox and become a backlog"
        )
    if len(report.completed) > MAX_COMPLETED_ITEMS:
        report.advisories.append(
            f"archive: {len(report.completed)} items under 'Recently completed'; move the "
            "ones that have stopped being recent to the 'Archive' ledger"
        )
    if not any(
        e.effort == "S" and e.status == "ready" and e.priority != "P3" for e in report.entries
    ):
        report.advisories.append(
            "queue: nothing is both ready and sized S, so a short session has nothing to "
            "pick up; consider splitting a larger item"
        )

    known = {e.identifier for e in report.entries} | resolved
    for path, text in related.items():
        for reference in sorted(set(REFERENCE_RE.findall(text))):
            if reference not in known:
                report.errors.append(
                    f"{path}: references {reference}, which is in neither the queue nor the archive"
                )
            elif reference in resolved and path.name == "WORKING_NOTES.md":
                report.advisories.append(
                    f"{path}: still carries a thread for {reference}, which has left the "
                    "queue; delete it rather than leaving it stale"
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

    records = [(i, "completed") for i in report.completed]
    records += [(i, "archived") for i in report.archived]
    for identifier, disposal in records:
        if identifier in seen:
            report.errors.append(
                f"{identifier}: listed as {disposal} but still open at line {seen[identifier].line}"
            )

    for identifier in sorted(set(report.completed) & set(report.archived)):
        report.errors.append(
            f"{identifier}: recorded under both 'Recently completed' and 'Archive'; "
            "an item is recorded once, in one of them"
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


def format_list(report: Report) -> str:
    """Render one line per open item: the queue without the briefs.

    This is the cheap way to see the whole queue. Reading the file itself
    costs roughly twenty-five times as much, and almost all of that is brief
    prose a session choosing between items does not need. Every field the
    punch-list skill's recommendation actually branches on - band, effort,
    status, and whether CLAUDE.md's model-matching rule applies - is here.

    It is deliberately not enough to work from. The closing line says so,
    because a one-line title is exactly the kind of thing that looks
    actionable and is not: the brief is what makes an item startable cold.
    """
    if not report.entries:
        return ""

    counts = report.counts
    lines = [
        f"Punch list (docs/PUNCH_LIST.md): {len(report.entries)} open - "
        f"{', '.join(f'{n} {p}' for p, n in counts.items())}."
    ]
    width = max(len(e.identifier) for e in report.entries)
    for entry in report.entries:
        marks = [entry.effort, entry.status]
        if entry.model_guidance is not None:
            marks.append(f"{entry.model_guidance}, strongest model")
        lines.append(
            f"{entry.priority} {entry.identifier:<{width}} {entry.title} ({', '.join(marks)})"
        )
    lines.append("Read an entry's brief before starting it; this listing is for choosing.")
    return "\n".join(lines)


def _with_guidance(line: str, entry: Entry) -> str:
    """Append the model-matching note to a digest line, if the entry has one."""
    if entry.model_guidance is None:
        return line
    return f"{line} - {entry.model_guidance}: use opusplan or your strongest model, high effort"


def format_branch_note(branch: str | None) -> str:
    """Render the naming reminder for a branch that cannot carry an item id.

    Empty unless the reminder is still actionable: no branch was supplied,
    the checkout is on `main`, or the name already leads with an id. The
    digest is resent on every turn, so a line that cannot be acted on is a
    line that should not be there.
    """
    name = (branch or "").strip()
    if not name or name in ("main", "HEAD") or BRANCH_ID.search(name):
        return ""
    return (
        f"  Branch `{name}` carries no PL id: if this session works a punch-list item, "
        "lead every commit subject and the pull request title with the id instead. "
        "Those outlive the branch; say in your reply that you did it."
    )


def format_digest(report: Report, branch: str | None = None) -> str:
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

    note = format_branch_note(branch)
    if note:
        lines.append(note)

    lines.append(
        "`python3 tools/punch_list.py list` shows the queue; read an entry's brief before "
        "starting it, and the whole file only when grooming. Any finding not fixed this "
        "session gets an entry there before the session ends."
    )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("mode", choices=("check", "digest", "list"))
    parser.add_argument("--file", type=Path, default=None, help="path to the punch list")
    parser.add_argument("--today", type=date.fromisoformat, default=None, help="reference date")
    parser.add_argument(
        "--branch",
        default=None,
        help="current git branch; the digest checks whether it carries an item id",
    )
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

    if args.mode in ("digest", "list"):
        rendered = (
            format_digest(report, args.branch) if args.mode == "digest" else format_list(report)
        )
        if rendered:
            print(rendered)
        return 0

    print(format_check(report))
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
