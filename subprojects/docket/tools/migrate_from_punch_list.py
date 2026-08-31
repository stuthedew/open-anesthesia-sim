"""One-time conversion of `docs/PUNCH_LIST.md` and `docs/inbox/` into `docs/items/`.

Kept in the repository rather than run and thrown away, so that the mapping
from the old store to the new one is auditable: every id that used to exist
still exists, and it is possible to check that claim rather than trust it.

Existing sequential ids are preserved exactly. They are cited from
`ROADMAP.md`, from commit subjects, and from each other, and renumbering them
into the new random scheme would break every one of those references for no
benefit. Inbox notes, which never had ids, get new ones.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# Both imports follow the path insertion above and have to stay below it.
from docket.model import Item
from docket.store import new_id, write_item

ENTRY_RE = re.compile(r"^### (PL-(\d+)) (.+)$")
BAND_RE = re.compile(r"^## (P[0-3])\b")
RESOLVED_RE = re.compile(r"^- (PL-\d+) (.+?)(?: — `([0-9a-f]{7,40})`)?$")
CODE_TOKEN_RE = re.compile(r"`([^`]+)`")
ADDED_RE = re.compile(r"\badded (\d{4}-\d{2}-\d{2})\b")
CLOSED_RE = re.compile(r"\bclosed (\d{4}-\d{2}-\d{2})\b")
PATH_RE = re.compile(r"`([^`]+\.(?:py|json|md|toml|yml|yaml|sh|lock))`")
PRIORITIES = ("P0", "P1", "P2", "P3")
EFFORTS = ("S", "M", "L")
STATUSES = ("ready", "needs-decision", "blocked")


def resolve_path(raw: str, root: Path) -> str:
    """Turn a path as written in a brief into one that exists in the tree.

    Briefs name modules the way the architecture document draws them
    (`app/simulation_view.py`), which is relative to the package rather than
    to the repository. The conflict graph needs real paths, so each candidate
    is tried and the one that exists wins. A path that resolves to nothing is
    kept verbatim: it may name a file the work will create.
    """
    candidates = [raw, f"src/anesthesia_sim/{raw}"]
    for candidate in candidates:
        if (root / candidate).exists():
            return candidate
    return raw


def touches_from(body: str, root: Path) -> tuple[str, ...]:
    """Read the file list out of a `**Where.**` field written as prose."""
    match = re.search(r"\*\*Where\.\*\*(.+?)(?=\n\*\*|\Z)", body, re.DOTALL)
    if match is None:
        return ()
    seen = {resolve_path(path, root) for path in PATH_RE.findall(match.group(1))}
    return tuple(sorted(seen))


def blockers_from(body: str, identifier: str) -> tuple[str, ...]:
    match = re.search(r"\*\*Blocked by\.\*\*(.+?)(?=\n\*\*|\Z)", body, re.DOTALL)
    source = match.group(1) if match else ""
    return tuple(sorted({ref for ref in re.findall(r"PL-\d+", source) if ref != identifier}))


def convert_open(text: str, root: Path) -> list[Item]:
    """Every open entry, band by band."""
    items: list[Item] = []
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
        if (band_match := BAND_RE.match(line)) is not None:
            band = band_match.group(1)
        elif line.startswith("## "):
            band = ""
        entry = ENTRY_RE.match(line)
        if entry is None or not band:
            index += 1
            continue

        identifier, _, title = entry.groups()
        body_lines: list[str] = []
        index += 1
        while index < len(lines) and not lines[index].startswith(("### ", "## ")):
            body_lines.append(lines[index])
            index += 1
        metadata = next((entry for entry in body_lines if entry.strip()), "")
        tokens = CODE_TOKEN_RE.findall(metadata)
        body = "\n".join(body_lines[1:]).strip()
        added = ADDED_RE.search(metadata)
        items.append(
            Item(
                identifier=identifier,
                title=title,
                priority=next((t for t in tokens if t in PRIORITIES), band),
                effort=next((t for t in tokens if t in EFFORTS), "M"),
                status=next(
                    (s for s in STATUSES if re.search(rf"(?<![\w-]){s}(?![\w-])", metadata)),
                    "ready",
                ),
                classes=tuple(t for t in tokens if t not in PRIORITIES and t not in EFFORTS),
                touches=touches_from(body, root),
                blocked_by=blockers_from(body, identifier),
                feature="",
                milestone="",
                added=date.fromisoformat(added.group(1)) if added else None,
                closed=None,
                commit="",
                reason="",
                body=body + "\n",
            )
        )
    return items


def strip_fences(text: str) -> str:
    """Remove fenced blocks, so the header's format example is not read as data."""
    kept: list[str] = []
    fenced = False
    for line in text.splitlines():
        if line.startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            kept.append(line)
    return "\n".join(kept)


def convert_resolved(text: str, root: Path) -> list[Item]:
    """Completed and archived entries, which keep their ids and their reasons."""
    text = strip_fences(text)
    items: list[Item] = []
    for heading, status in (("## Recently completed", "done"), ("## Archive", "dropped")):
        if heading not in text:
            continue
        section = text.split(heading, 1)[1]
        for stop in ("\n## ",):
            if stop in section:
                section = section.split(stop, 1)[0]
        for line in section.splitlines():
            match = RESOLVED_RE.match(line.strip())
            if match is None:
                continue
            identifier, title, commit = match.groups()
            closed = CLOSED_RE.search(title)
            reason = ""
            if status == "dropped":
                title, _, reason = title.partition(" — ")
                reason = reason or "closed without action"
            items.append(
                Item(
                    identifier=identifier,
                    title=title.strip(" —"),
                    priority="",
                    effort="",
                    status="done" if commit else status,
                    classes=(),
                    touches=(),
                    blocked_by=(),
                    feature="",
                    milestone="",
                    added=None,
                    closed=date.fromisoformat(closed.group(1)) if closed else date(2026, 8, 24),
                    commit=commit or "",
                    reason=reason,
                    body=f"**Problem.** {title.strip(' —')}\n",
                )
            )
    return items


def convert_inbox(directory: Path, taken: set[str], root: Path) -> list[Item]:
    """Inbox notes become untriaged items, which is what they already were."""
    items: list[Item] = []
    if not directory.is_dir():
        return items
    for path in sorted(directory.glob("*.md")):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        title = next(
            (line[2:].strip() for line in text.splitlines() if line.startswith("# ")), path.stem
        )
        body = text.split("\n", 1)[1].strip() if "\n" in text else ""
        captured = re.match(r"(\d{4}-\d{2}-\d{2})", path.name)
        identifier = new_id(taken)
        taken.add(identifier)
        items.append(
            Item(
                identifier=identifier,
                title=title,
                priority="",
                effort="",
                status="untriaged",
                classes=(),
                touches=touches_from(body, root),
                blocked_by=(),
                feature="",
                milestone="",
                added=date.fromisoformat(captured.group(1)) if captured else date.today(),
                closed=None,
                commit="",
                reason="",
                body=body + "\n",
            )
        )
    return items


def main() -> int:
    root = Path(__file__).resolve().parents[3]
    punch = root / "docs" / "PUNCH_LIST.md"
    text = punch.read_text(encoding="utf-8")
    target = root / "docs" / "items"

    items = convert_open(text, root)
    items += convert_resolved(text, root)
    taken = {item.identifier for item in items}
    items += convert_inbox(root / "docs" / "inbox", taken, root)

    for item in items:
        write_item(target, item)

    print(f"wrote {len(items)} items to {target.relative_to(root)}")
    for status in ("untriaged", "ready", "needs-decision", "blocked", "done", "dropped"):
        count = sum(1 for item in items if item.status == status)
        if count:
            print(f"  {status}: {count}")
    with_paths = sum(1 for item in items if item.touches)
    print(f"  carrying a `touches` list: {with_paths}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
