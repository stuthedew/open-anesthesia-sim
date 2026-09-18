"""Find the clusters that generate more work than they close.

`CLAUDE.md` already says that friction which compounds is recommended the
moment it is found rather than filed. That rule is prose, and prose needs a
session to notice: `PL-BHVM` recorded a cluster whose own brief measured it
generating more items than it closed, and it then sat in `P2` - a band of 187
items - for days, because nothing ranked it above any other `P2`. A flat band
is where a generator hides. This check is that rule made decidable, so the
noticing does not depend on which session happens to read which item.

**What a generator is.** Not a file with many items - a large file honestly
attracts many. A generator is a cluster where working an item *produces* more
items than it closes, so effort spent on it does not reduce the remaining
work. That is a ratio, and the project can already measure it exactly.

**How a spawn is attributed.** `CLAUDE.md` requires every commit subject to
lead with the id of the item being worked, and `bin/docket new` writes each
captured item as a file in that same commit. So the commit that *adds* an
item file names, in its subject, the item whose work produced it. Where the
leading ids are the new item's own, the commit is a plain capture and the
item has no parent. This is the method `PL-6ZQY` used by hand on 2026-09-12;
here it is one `git log` call rather than a session's afternoon.

**The rule.** For a path `p` that items declare in `touches`:

    r(p) = items spawned by work on p's closed items that ALSO declare p
           / p's closed items

`r >= 1.0` means the cluster is not shrinking: each closure hands back at
least one new item *in the same cluster*.

The "also declare p" half is what makes this a generator rather than a
busy file. A session closing an item captures whatever else it noticed, and
those captures are attributed to the item it was working - so counting every
spawned child rates any heavily-worked file a generator. Measured
2026-09-17, that error put `src/anesthesia_sim/core` at r = 5.08 and
`docs/ARCHITECTURE.md` at 2.96, neither of which reproduces into itself at
anything like that rate. Only a child that lands back in the same cluster is
evidence that the mechanism there is unsettled.

A cluster is reported when `r >= 1.0`, it has at least
`MIN_CLOSED` closures behind that ratio, and it still has open items - a
generator that has already been fully closed out is history, not friction.

**Advisory, not a failure.** `CLAUDE.md` reserves hard failure for exact
rules and requires a check to change a decision every run or be retired.
Whether a generator is worth a design round is a judgment about the
mechanism underneath it, which this cannot make. What it can do, and what no
session reliably does, is refuse to let the ratio go unsaid - and name the
open items that carry it, so raising them is one command away.

Store paths are excluded from clustering: `docs/items` sits inside
`workflow_paths`, so every capture made while doing something else would
otherwise read as one enormous cluster. `docket trend` excludes them from its
churn share for the same reason.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ITEM_DIR = Path("docs/items")
STORE_PATHS = {"docs/items", "docs/WORKING_NOTES.md", "docs/dead-ends.md"}

#: A `touches` entry is compared after stripping any trailing separator:
#: `docs/items/` and `docs/items` are the same cluster and both are the store.
OPEN_STATUSES = {"ready", "blocked", "needs-decision", "untriaged"}
TOP_BAND = {"P0", "P1"}

#: Below this many closures a ratio is noise: one item spawning two children
#: reaches r = 1.0 on a cluster of two. Eight is the smallest count at which a
#: single unlucky item cannot carry the cluster over the line on its own.
MIN_CLOSED = 8

ID_RE = re.compile(r"\bPL-[A-Z0-9]{4}\b")
LEADING_IDS_RE = re.compile(r"^((?:PL-[A-Z0-9]{4})(?:\s*,\s*PL-[A-Z0-9]{4})*)\s*:")


def read_front_matter(path: Path) -> dict[str, str]:
    """Return an item file's front matter as plain strings.

    Deliberately not a YAML parser: the store is flat `key: value` pairs and a
    dependency here would stop this running from a bare checkout.
    """
    fields: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return fields
    if not lines or lines[0].strip() != "---":
        return fields
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, sep, value = line.partition(":")
        if sep and not key.startswith(" "):
            fields[key.strip()] = value.strip()
    return fields


def creation_parents(repo: Path) -> dict[str, set[str]]:
    """Map each item id to the ids of the items whose work created its file."""
    out = subprocess.run(
        ["git", "log", "--diff-filter=A", "--name-only", "--format=\x01%s", "--", str(ITEM_DIR)],
        capture_output=True,
        text=True,
        cwd=repo,
    ).stdout
    parents: dict[str, set[str]] = {}
    for block in out.split("\x01")[1:]:
        subject, _, body = block.partition("\n")
        match = LEADING_IDS_RE.match(subject.strip())
        leading = set(ID_RE.findall(match.group(1))) if match else set()
        created = set()
        for line in body.splitlines():
            line = line.strip()
            if not line.startswith(f"{ITEM_DIR}/"):
                continue
            found = ID_RE.search(Path(line).name.upper().replace("_", "-"))
            if found:
                created.add(found.group(0))
        # A capture commit leads with the ids of the items it is creating, and
        # `bin/docket new` takes several titles at once - so every id this
        # commit creates is excluded, not just the one being attributed.
        # Otherwise two items captured together become each other's parent.
        for identifier in created:
            parents.setdefault(identifier, leading - created)
    return parents


def clusters(repo: Path) -> list[tuple[float, str, int, int, list[tuple[str, str, str]]]]:
    items: dict[str, dict[str, str]] = {}
    for path in sorted((repo / ITEM_DIR).glob("PL-*.md")):
        fields = read_front_matter(path)
        if fields.get("id"):
            items[fields["id"]] = fields

    parents = creation_parents(repo)

    def declared(identifier: str) -> set[str]:
        raw = items.get(identifier, {}).get("touches", "")
        return {t.strip().rstrip("/") for t in raw.split(",") if t.strip()}

    #: ancestor -> path -> number of children that landed in that same cluster.
    spawned: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for child, ancestors in parents.items():
        shared = declared(child)
        for ancestor in ancestors:
            if ancestor not in items:
                continue
            for touch in shared & declared(ancestor):
                spawned[ancestor][touch] += 1

    by_path: dict[str, list[str]] = defaultdict(list)
    for identifier, fields in items.items():
        for raw in fields.get("touches", "").split(","):
            touch = raw.strip().rstrip("/")
            if touch and touch not in STORE_PATHS:
                by_path[touch].append(identifier)

    reported = []
    for touch, ids in by_path.items():
        closed = [i for i in ids if items[i].get("status") == "done"]
        open_ids = [i for i in ids if items[i].get("status") in OPEN_STATUSES]
        if len(closed) < MIN_CLOSED or not open_ids:
            continue
        produced = sum(spawned[i][touch] for i in closed)
        ratio = produced / len(closed)
        if ratio < 1.0:
            continue
        carriers = sorted(
            (items[i].get("priority", "--"), i, items[i].get("title", "")) for i in open_ids
        )
        reported.append((ratio, touch, produced, len(closed), carriers))
    reported.sort(reverse=True)
    return reported


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=Path("."))
    args = parser.parse_args(argv)

    reported = clusters(args.repo)
    if not reported:
        print("generator check: no open cluster closes less work than it creates.")
        return 0

    print("Clusters that generate at least as much work as they close:")
    print()
    for ratio, touch, produced, closed, carriers in reported:
        unranked = [c for c in carriers if c[0] not in TOP_BAND]
        print(f"  {touch}")
        print(
            f"    r = {ratio:.2f}  ({closed} closed produced {produced} new)"
            f"  ·  {len(carriers)} open, {len(unranked)} below P1"
        )
        for priority, identifier, title in carriers[:6]:
            print(f"      {priority}  {identifier}  {title[:76]}")
        if len(carriers) > 6:
            print(f"      ... and {len(carriers) - 6} more")
        print()
    print(
        "Effort on these does not reduce what is left. Decide the mechanism under\n"
        "one, or say why the ratio is acceptable - do not work the items singly."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
