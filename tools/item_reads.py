"""Answer, from `.docket-reads.log`, what sessions actually do with the item store.

`.claude/hooks/item_read_log.py` records one line per read or id-search that
touched `docs/items/`. This turns that into the three numbers the store's
design arguments have been assuming rather than measuring:

1. **How many distinct items are opened**, against how many exist. The store's
   whole cost is carried for the ones nobody opens.
2. **What share of those are closed.** No `docket` command reads a closed
   item's body - established 2026-09-13, and true. Commands were never the
   reader in question. A session is.
3. **Whether a citation edge is ever traversed** - a session reading item A and
   then, within the same session, reading or searching for an id that A's body
   cites. 86.1% of items cite another and there are 2,773 edges, all written at
   authoring time. Whether any is ever *followed* decides whether that graph is
   doing work or is an artifact of how items get written.

**Read the output as one checkout's sessions, never as the project's.** The log
is untracked and a container is ephemeral, so it holds what this machine has
done since the file appeared. It says so in its own header, because the failure
mode here is a small sample read as a finding.

**It reports and decides nothing.** Whether a low traversal count means the
graph is decorative, or means sessions cannot find what they need, or means the
sample is too small, is judgment - and the third possibility is why this prints
the sample size first. `PL-VV16`.

Standard library only, and parses at the floor
`tests/unit/test_tools_portability.py` holds this directory to.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LOG = REPO / ".docket-reads.log"
ITEMS = REPO / "docs" / "items"

ITEM_ID = re.compile(r"\bPL-[A-Z0-9]{3,4}\b")
CLOSED = ("status: done", "status: dropped")


def store() -> tuple[dict[str, Path], set[str]]:
    """Return `{id: path}` for every item, and the set of ids that are closed."""
    paths: dict[str, Path] = {}
    closed: set[str] = set()
    for path in ITEMS.glob("*.md"):
        parts = path.name.split("-")
        if len(parts) < 2:
            continue
        identifier = f"{parts[0]}-{parts[1]}"
        paths[identifier] = path
        head = path.read_text(encoding="utf-8")[:400]
        if any(marker in head for marker in CLOSED):
            closed.add(identifier)
    return paths, closed


def citations(path: Path, self_id: str) -> set[str]:
    text = path.read_text(encoding="utf-8")
    body = text.split("---", 2)[2] if text.startswith("---") else text
    return set(ITEM_ID.findall(body)) - {self_id}


def parse_log() -> list[tuple[str, str, str, str]]:
    if not LOG.exists():
        return []
    rows = []
    for line in LOG.read_text(encoding="utf-8", errors="replace").splitlines():
        fields = line.split("\t")
        if len(fields) == 4:
            rows.append((fields[0], fields[1], fields[2], fields[3]))
    return rows


def main() -> int:
    rows = parse_log()
    if not rows:
        print("No reads recorded yet. `.docket-reads.log` is written by")
        print("`.claude/hooks/item_read_log.py` and is local to this checkout.")
        return 0

    paths, closed = store()

    # Per session, in order, the ids touched - by an opened path or by a
    # searched-for id. Both count as reaching an item; only the order matters
    # for the traversal question below.
    per_session: dict[str, list[str]] = defaultdict(list)
    for _stamp, session, _tool, target in rows:
        for identifier in ITEM_ID.findall(target):
            per_session[session].append(identifier)

    touched = {i for seq in per_session.values() for i in seq}
    known = touched & set(paths)

    traversals = 0
    traversing_sessions = 0
    for seq in per_session.values():
        found_here = 0
        seen: list[str] = []
        for identifier in seq:
            for earlier in seen:
                if earlier in paths and identifier in citations(paths[earlier], earlier):
                    found_here += 1
                    break
            seen.append(identifier)
        traversals += found_here
        if found_here:
            traversing_sessions += 1

    closed_touched = known & closed

    print(f"Sample: {len(rows)} recorded reads across {len(per_session)} session(s),")
    print("one checkout only - this log is untracked and the container is ephemeral.")
    print()
    print(f"Distinct items reached        {len(known)} of {len(paths)} in the store")
    if known:
        share = 100 * len(closed_touched) / len(known)
        print(f"  of which closed             {len(closed_touched)} ({share:.0f}%)")
    print(f"Citation edges traversed      {traversals}, in {traversing_sessions} session(s)")
    print()
    print("A traversal is one session reaching an item it had already reached a")
    print("citation to. Low counts have three readings - the graph is decorative,")
    print("sessions cannot find what they need, or the sample is too small - and")
    print("this tool does not choose between them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
