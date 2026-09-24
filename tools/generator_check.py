"""Surface the clusters worth a session's judgment about a root cause.

`CLAUDE.md` makes a mechanism that causes three or more items a *generator*,
which ranks above everything but `P0`. The claim is a **recorded fact**: a
session that identifies one writes `root-cause-of:` on the causing item, naming
the items it explains, and `docket next` ranks it from that field. Nothing
infers it, and this script is not an exception - it reports candidates and
decides nothing.

**Why it cannot be the verdict.** The two things that can be measured here are
both close to causation without being it:

- *A self-generation ratio over a `touches` path* measures how often work on a
  file hands back more work on that same file. It is a real signal and it is
  not the definition. Measured 2026-09-17, the ratio reported **no** cluster on
  this tree while `PL-6ZQY` had already named **six** under one root cause,
  `PL-BHVM` among them at nineteen items.
- *Citation density* measures how often other items name this one. Items cited
  by more than two other open items number 33 here, and an item is cited for
  context, for provenance, and for a stale line reference as readily as for
  cause. Promoting 33 items above `P1` would mean nothing.

Both are inputs to a judgment, which is the half `CLAUDE.md` refuses to script.

**What changed, and why the old gate was wrong.** This script used to report
`r >= 1.0` as a verdict, behind a floor of eight closures on the path. Under
the recorded definition that floor is backwards: a generator is a mechanism
three *open* items stand on, and eight closures is a state a cluster reaches
only after it has been worked at length. A test that can fire only then reports
the weed once it has seeded. The floor here is instead the definition's own -
three open items on the cluster - and it selects what to *show*, never what is
true.

**How a spawn is attributed**, for the ratio column. `CLAUDE.md` requires every
commit subject to lead with the id of the item being worked, and `bin/docket
new` writes each captured item as a file in that same commit. So the commit
that *adds* an item file names, in its subject, the item whose work produced
it; where the leading ids are the new item's own, the commit is a plain capture
and the item has no parent. Only a child that also declares the same `touches`
path is counted, because a session closing an item captures whatever else it
noticed and those captures attribute to the item it was working - counting all
of them rates any heavily-worked file a generator. Where git will not give that
history, the column reads `r unmeasured` rather than zero and the run says so
before anything else (`PL-1PBV`).

**What it can and cannot see.** A cluster is one declared `touches` path, so a
family whose members share a *kind of claim* rather than a file is visible only
where the claim concentrates on a path. `PL-G424`'s apparatus-drift family is
the measured case (2026-09-19, 21 members): 8 declare `docs/WORKING_NOTES.md`
and 5 `docs/items`, so those two clusters carry it; 6 declare a single item
file each and 6 more scatter across four apparatus paths under `MIN_OPEN`, and
nothing here can gather those - a sweep that reads the briefs is the only
detector for that shape, and `PL-4YJK` records what one costs. The store paths
used to be excluded from clustering on the ground that every capture would
otherwise read as one enormous cluster. That is true of `docket trend`'s churn
share, which counts the files a *commit* changes and so meets `docs/items` in
every capture, and the exclusion was borrowed from there; on this axis a
capture declares `touches` on its subject, and 24, 18 and 0 open items declared
`docs/items`, `docs/WORKING_NOTES.md` and `docs/dead-ends.md` when the
exclusion was measured and removed (`PL-LSR0`).

Advisory, and it exits 0 whatever it finds. There is no state of this tree that
this script can call an error, because the thing it looks for is not something
it can decide.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.store import ID_PATTERN  # noqa: E402

ITEM_DIR = Path("docs/items")

#: A `touches` entry is compared after stripping any trailing separator:
#: `docs/items/` and `docs/items` are the same cluster.
OPEN_STATUSES = {"ready", "blocked", "needs-decision", "untriaged"}

#: The floor for showing a cluster, and it is the recorded definition's own:
#: `CLAUDE.md` calls a mechanism causing three or more items a generator, so a
#: path with fewer than three open items cannot host one. It selects what to
#: print and asserts nothing about what is printed.
MIN_OPEN = 3

#: How many other open items have to name an id before its citation count is
#: worth showing. Three for the same reason as `MIN_OPEN`, and it is emphatically
#: not a promotion rule - 33 items clear it on this tree.
CITED_BY = 3

#: The ratio at which a cluster is not shrinking: each closure hands back at
#: least one new item in the same cluster. It was this script's whole verdict
#: and is now one of three signals, none of which decides anything.
NOT_SHRINKING = 1.0

#: How many clusters to print. A display limit; the rest are counted.
SHOW = 6

#: The store's own grammar, borrowed rather than restated. The pattern this
#: replaced was `PL-[A-Z0-9]{4}`, which is blind to the 43 historical
#: three-digit ids `store.ID_PATTERN` still accepts: 219 citation edges and
#: 44 item filenames went unread, so `citations` undercounted exactly the
#: oldest items and `creation_parents` attributed none of them (`PL-KYW3`).
ID_RE = re.compile(ID_PATTERN)
LEADING_IDS_RE = re.compile(rf"^((?:{ID_PATTERN})(?:\s*,\s*(?:{ID_PATTERN}))*)\s*:")


class GitUnanswered(Exception):
    """The item history spawn attribution rests on, which git did not give, and why."""


@dataclass(frozen=True)
class Cluster:
    """One `touches` path, with every signal measured about it and no verdict.

    Each field is a separate reading, deliberately not folded into a score. A
    composite would rank these against each other on a number, and a number is
    exactly what wins an argument on fluency rather than on merit here - which
    is the trap `.claude/rules/expert-review.md` names. A reader comparing three
    columns has to think; a reader handed one has been given an answer.
    """

    path: str
    open_ids: list[str]
    closed: int
    #: Children of this cluster's closed items that landed back in it, or
    #: `None` where the history that attributes them could not be read.
    produced: int | None
    #: The most common `feature` among the open items, and how many carry it.
    feature: str
    feature_count: int
    #: Open items here that three or more other open items name.
    cited: list[str]
    #: Open items here already inside a recorded `root-cause-of:`, either
    #: carrying one or named by one.
    recorded: list[str]

    @property
    def signals(self) -> tuple[str, ...]:
        """The reasons this cluster is worth a look, or `()`.

        Size alone is not one of them. A large file honestly attracts many
        items, and ranking by open count would put `docs/MODEL.md`'s 40 at the
        top of every run forever - a check that fires every run without
        changing a decision, which `CLAUDE.md` calls a defect in the check.
        What makes a cluster worth judgment is *concentration*: items that are
        one problem, named as one problem, or naming each other.
        """
        reasons = []
        if self.feature_count >= MIN_OPEN:
            reasons.append(f"{self.feature_count} share feature '{self.feature}'")
        if self.cited:
            reasons.append(f"{len(self.cited)} cited by {CITED_BY}+ open items")
        if self.ratio is not None and self.ratio >= NOT_SHRINKING:
            reasons.append(f"r = {self.ratio:.2f}, so it is not shrinking")
        return tuple(reasons)

    @property
    def ratio(self) -> float | None:
        """Children per closure, or `None` where it was not measured.

        `None` rather than `0.0`: a cluster with no closures has not been
        measured, and printing a zero would say it was measured and came back
        clean. That is the apparatus floor - an answer is true or says it could
        not answer - on one column of one advisory. The same holds where the
        history was never read, which printed `r = 0.00` on every cluster that
        had closed anything until `PL-1PBV`.
        """
        if self.produced is None or not self.closed:
            return None
        return self.produced / self.closed


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
    """Map each item id to the ids of the items whose work created its file.

    Raises `GitUnanswered` where git will not give the history - no repository,
    no git, a log that failed. An empty map would say the history was read and
    no item had a parent, and every cluster's spawn count would then print as
    measured and zero (`PL-1PBV`).
    """
    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "--diff-filter=A",
                "--name-only",
                "--format=\x01%s",
                "--",
                str(ITEM_DIR),
            ],
            capture_output=True,
            text=True,
            cwd=repo,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise GitUnanswered(f"`git log` could not run: {error}") from error
    if result.returncode != 0:
        said = next((line.strip() for line in result.stderr.splitlines() if line.strip()), "")
        raise GitUnanswered(
            f"`git log` exited {result.returncode}: {said or 'with nothing on stderr'}"
        )
    out = result.stdout
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


def citations(repo: Path, open_ids: set[str]) -> Counter[str]:
    """How many *other open* items name each id, anywhere in their file.

    Counted over open items only, in both directions. A closed item's citation
    is history: it names something that was relevant to work already finished,
    and it cannot be evidence that a mechanism is still standing.
    """
    counts: Counter[str] = Counter()
    for path in sorted((repo / ITEM_DIR).glob("PL-*.md")):
        fields = read_front_matter(path)
        source = fields.get("id", "")
        if source not in open_ids:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for target in set(ID_RE.findall(text)) & open_ids:
            if target != source:
                counts[target] += 1
    return counts


def clusters(repo: Path, *, attributed: bool = True) -> list[Cluster]:
    """Every `touches` path with at least `MIN_OPEN` open items, best-signalled first.

    Raises `GitUnanswered` where the history `creation_parents` reads cannot be
    read. `attributed=False` does without it: every spawn count is then
    unmeasured and signals nothing, which is how `main` still reports the two
    signals that need no history.
    """
    items: dict[str, dict[str, str]] = {}
    for path in sorted((repo / ITEM_DIR).glob("PL-*.md")):
        fields = read_front_matter(path)
        if fields.get("id"):
            items[fields["id"]] = fields

    parents = creation_parents(repo) if attributed else {}
    open_ids = {i for i, f in items.items() if f.get("status") in OPEN_STATUSES}
    cited = citations(repo, open_ids)

    # Ids already inside a recorded claim - carrying `root-cause-of:` or named
    # by one. Those clusters have had the judgment made and are marked rather
    # than dropped: a recorded claim can be wrong, and hiding the evidence
    # under it is how it would stay wrong.
    claimants = {i for i, f in items.items() if f.get("root-cause-of", "").strip()}
    explained = {
        part.strip()
        for i in claimants
        for part in items[i].get("root-cause-of", "").split(",")
        if part.strip()
    }
    in_a_claim = claimants | explained

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
            if touch:
                by_path[touch].append(identifier)

    found: list[Cluster] = []
    for touch, ids in by_path.items():
        here = sorted(i for i in ids if i in open_ids)
        if len(here) < MIN_OPEN:
            continue
        closed = [i for i in ids if items[i].get("status") == "done"]
        features = Counter(items[i].get("feature", "") for i in here if items[i].get("feature"))
        name, count = features.most_common(1)[0] if features else ("", 0)
        found.append(
            Cluster(
                path=touch,
                open_ids=here,
                closed=len(closed),
                produced=sum(spawned[i][touch] for i in closed) if attributed else None,
                feature=name,
                feature_count=count,
                cited=[i for i in here if cited[i] >= CITED_BY],
                recorded=[i for i in here if i in in_a_claim],
            )
        )
    # Concentration first - the most open items sharing one `feature`, which is
    # the project's own name for "these are one problem" - then how many of them
    # three or more other open items name, then how much open work sits on the
    # path, then the path so two runs agree. Size is not a signal, so it breaks
    # ties only after both readings that are: measured 2026-09-19, the
    # `docs/WORKING_NOTES.md` cluster carrying 8 of `PL-G424`'s members sat
    # ninth on size, behind clusters nobody cited, under a display limit of six
    # (`PL-LSR0`). Deliberately not a composite of the three signals: a score
    # would rank these against each other on a number, and a number wins an
    # argument on fluency rather than on merit, which is the trap
    # `.claude/rules/expert-review.md` names.
    found = [c for c in found if c.signals]
    found.sort(key=lambda c: (-c.feature_count, -len(c.cited), -len(c.open_ids), c.path))
    return found


def _line(cluster: Cluster) -> str:
    if cluster.produced is None:
        ratio = "r unmeasured"
    elif cluster.ratio is None:
        ratio = "no closures yet"
    else:
        ratio = f"r = {cluster.ratio:.2f}"
    parts = [f"{len(cluster.open_ids)} open", f"{ratio} over {cluster.closed} closed"]
    parts.extend(cluster.signals)
    if cluster.recorded:
        parts.append(f"{len(cluster.recorded)} already inside a recorded root cause")
    return "  ·  ".join(parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=Path("."))
    args = parser.parse_args(argv)

    try:
        found = clusters(args.repo)
    except GitUnanswered as silence:
        # Said first, and whatever follows it: with no ratio measured, a
        # cluster only `r` would have surfaced is missing below, so an empty
        # list here is not a clean one (`PL-1PBV`).
        print(f"generator candidates: the item history could not be read - {silence}")
        print("  No cluster's r was measured, so none can signal on it, and a cluster only")
        print("  r would have surfaced is not shown.")
        print()
        found = clusters(args.repo, attributed=False)
    if not found:
        print("generator candidates: no cluster shows concentration worth a look.")
        return 0

    print("Clusters worth a look for one root cause. None of these is a generator:")
    print()
    for cluster in found[:SHOW]:
        print(f"  {cluster.path}")
        print(f"    {_line(cluster)}")
        print(f"      {', '.join(cluster.open_ids[:6])}")
        if len(cluster.open_ids) > 6:
            print(f"      ... and {len(cluster.open_ids) - 6} more")
        print()
    if len(found) > SHOW:
        print(f"  ... and {len(found) - SHOW} more clusters with a signal.")
        print()
    # The placeholders are the ones `docket set --root-cause-of` already prints
    # as its metavar, and they are in `store.ID_ALPHABET`. Both halves matter:
    # the alphabet is Crockford base32 *minus the vowels*, so `PL-AAAA` is an id
    # the store can never mint, and an example is copied - `PL-GXPP` spent 261
    # substitutions removing that literal from the test tree. Agreeing with the
    # other half of the same field's interface is what keeps one placeholder set
    # to recognise rather than two (`PL-DPY6`).
    print(
        "A ratio, a shared feature and a citation count are evidence, not causation.\n"
        "Where one mechanism really explains three or more of these, record it:\n"
        "`root-cause-of: PL-XXXX, PL-YYYY, PL-ZZZZ` on the item that causes them.\n"
        "`docket check` holds the ids to existing. Under three, it is an ordinary item.\n"
        "\n"
        "Recording it does not rank it. Add `generator: live - <why the store is\n"
        "still handing this mechanism members>` and `docket next` ranks it above\n"
        "every band but P0; `generator: spent - <why it can no longer produce one>`\n"
        "keeps the record for the audit and leaves it on its own band.\n"
        "\n"
        "Either way, add `misread: <the one fact its members misread>` - one line,\n"
        "naming the fact rather than the reader. `docket check` requires it on every\n"
        "head, and `docket generators --misread` compares it with the other heads'."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
