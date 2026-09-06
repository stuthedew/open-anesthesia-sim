"""Which items can be worked at the same time.

Two items can share a session-week if nothing forces them into an order and
they will not fight over the same lines of the same file. Both halves of
that are already written down: `blocked-by` gives the ordering, and
`touches` gives the files. This module reads them as a graph and reports the
independent sets.

**What this can and cannot tell you.** `touches` is a prediction made when
the item was written, so it is reliable in one direction only. When two
items name overlapping paths they really will contend, and that is worth
acting on. When they do not, all that has been established is that nobody
foresaw a collision - the work may still wander into a shared file. So this
rules pairs *out*, and never certifies a pair as safe. Presenting a
heuristic as a guarantee would be exactly the failure this package is
otherwise built to avoid.

**Declared overlap is half the question, and the weaker half.** `touches` is
written before the work, so it goes stale the moment a branch wanders outside
it, and two sessions can pass every declared check and still meet in a file
neither predicted - which is how the collision that produced `PL-MC8Z`
happened. `observed_conflicts` reads the other half from the branches
themselves: what work already underway has actually changed. It is exact where
`touches` is a guess and blind to the future where `touches` is not, so the two
are reported side by side rather than merged into one verdict.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

from .model import Item
from .vcs import FlightFiles


def _covers(one: str, other: str) -> bool:
    """Whether two declared paths can touch the same file.

    A directory covers everything beneath it, so an item declaring
    `src/anesthesia_sim/app/` contends with one declaring a single view
    module inside it.
    """
    first, second = PurePosixPath(one.strip("/")), PurePosixPath(other.strip("/"))
    return first == second or first in second.parents or second in first.parents


def _overlaps(one: Item, other: Item) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """The declared overlap, split by how strong the evidence is.

    Returns the paths both items name identically, then the paths where one
    item's directory merely covers the other's. They are different claims and
    were reported as one: 38 of this store's open items declare a directory,
    so an item naming `tests/` read as contending with every test change, in
    the same words as two items naming the same module.
    """
    identical: set[str] = set()
    covering: set[str] = set()
    for left in one.touches:
        for right in other.touches:
            if not _covers(left, right):
                continue
            if PurePosixPath(left.strip("/")) == PurePosixPath(right.strip("/")):
                identical.add(left)
            else:
                covering.add(min(left, right, key=len))
    return tuple(sorted(identical)), tuple(sorted(covering))


def shared_paths(one: Item, other: Item) -> tuple[str, ...]:
    """Every declared path the two items could both reach."""
    identical, covering = _overlaps(one, other)
    return tuple(sorted(set(identical) | set(covering)))


ORDERING = "ordering"
SAME_FILE = "same file"
SAME_AREA = "same area"


@dataclass(frozen=True)
class Conflict:
    """What stands between two items being worked at the same time.

    `strength` separates the one kind that is a refusal from the two that are
    not, and the distinction is the whole point of the field. An ordering edge
    - `blocked-by`, in either direction - means the work cannot be done yet. A
    shared file means the second branch to merge resolves against the first,
    which is ordinary: two unrelated items legitimately touch one file, and
    the working practice this package documents is to land the smaller change
    first rather than to pick something else.

    Reporting all three as "cannot run alongside" cost a real answer on
    2026-09-06 (`PL-VRMK`): 27 of Gate 1's 112 open entries declare
    `docs/MODEL.md`, so the gate's science half - its most expensive work -
    excluded itself from every batch, and a session asked for three concurrent
    gate items withheld the strongest one it had.
    """

    other: Item
    reason: str
    strength: str = SAME_FILE
    paths: tuple[str, ...] = ()

    def describe(self) -> str:
        if self.paths:
            return f"{self.other.identifier} ({self.reason}: {', '.join(self.paths)})"
        return f"{self.other.identifier} ({self.reason})"


def conflicts_for(item: Item, candidates: list[Item]) -> list[Conflict]:
    """Everything that stands between this item and each of the others.

    Tiered by `Conflict.strength`; use `refusals` for the subset that actually
    forbids concurrent work.
    """
    found: list[Conflict] = []
    for other in candidates:
        if other.identifier == item.identifier:
            continue
        if other.identifier in item.blocked_by:
            found.append(Conflict(other, "blocks this item", ORDERING))
            continue
        if item.identifier in other.blocked_by:
            found.append(Conflict(other, "waits on this item", ORDERING))
            continue
        identical, covering = _overlaps(item, other)
        if identical:
            found.append(Conflict(other, "edits the same file", SAME_FILE, identical))
        elif covering:
            found.append(Conflict(other, "declares an area covering it", SAME_AREA, covering))
    return found


def refusals(conflicts: list[Conflict]) -> list[Conflict]:
    """The conflicts that forbid concurrent work rather than order it."""
    return [conflict for conflict in conflicts if conflict.strength == ORDERING]


@dataclass(frozen=True)
class Observed:
    """A branch that is already changing a file this item declares.

    Distinct from `Conflict`, which reads one item's `touches` against
    another's. This reads an item's `touches` against what a branch has
    actually done, so it fires only where work is underway and it fires on the
    real file rather than on the prediction. `paths` therefore carries the
    files the *branch* changed, not the declaration they matched: telling a
    session that `subprojects/docket/` collides is telling it nothing it can
    open.
    """

    branch: str
    item_ids: tuple[str, ...]
    paths: tuple[str, ...]

    def describe(self) -> str:
        who = ", ".join(self.item_ids) if self.item_ids else "no item id"
        return f"{self.branch} ({who})"


def observed_conflicts(item: Item, files: FlightFiles) -> list[Observed]:
    """Every in-flight branch already changing a file this item declares.

    The item's own branch is excluded: an item in flight on a branch is not in
    contention with itself, and reporting it would train a reader to skim the
    section where somebody else's branch also appears.

    Like everything else here this rules work out and never certifies it. An
    empty answer means no branch has *yet* touched a file the item declares -
    which leaves a branch that will touch one in its next commit, and every
    file the item touches without having declared it.
    """
    found: list[Observed] = []
    for entry in files.branches:
        if item.identifier in entry.item_ids:
            continue
        overlap = tuple(
            sorted(
                {
                    changed
                    for declared in item.touches
                    for changed in entry.paths
                    if _covers(declared, changed)
                }
            )
        )
        if overlap:
            found.append(Observed(branch=entry.branch, item_ids=entry.item_ids, paths=overlap))
    return sorted(found, key=lambda entry: entry.branch)


def undeclared(items: list[Item]) -> list[Item]:
    """Open items that declare no paths, and so cannot be reasoned about.

    These are not safe by default. An item with an empty `touches` is an item
    nobody has said anything about, and treating silence as "touches nothing"
    would turn a gap in the data into a false assurance.
    """
    return [item for item in items if not item.touches]


def parallel_batch(items: list[Item], limit: int | None = None) -> list[Item]:
    """A set of items that can be worked at once, best-first.

    Greedy in priority order rather than maximal by size: the largest
    independent set is the wrong objective when the items are not equally
    worth doing. Taking the most important item and then everything
    compatible with it beats taking four trivial items that happen not to
    overlap.

    Two passes, because "at once" has two answers and only the first is
    unqualified. The first takes items contending with nothing already
    chosen. The second fills the remaining slots with items whose only
    contention is a declared path - work that proceeds and resolves at merge
    rather than work that waits - and runs only when a `limit` has asked for a
    batch of a given size. Unlimited, the batch stays the independent set it
    has always been: filling it would print most of the queue, and every item
    added past the first pass costs the reader a judgment about order.
    """
    chosen: list[Item] = []
    taken: set[str] = set()
    for item in items:
        if not item.touches:
            continue
        if any(conflicts_for(item, [picked]) for picked in chosen):
            continue
        chosen.append(item)
        taken.add(item.identifier)
        if limit is not None and len(chosen) >= limit:
            return chosen
    if limit is None:
        return chosen
    for item in items:
        if not item.touches or item.identifier in taken:
            continue
        if any(refusals(conflicts_for(item, [picked])) for picked in chosen):
            continue
        chosen.append(item)
        taken.add(item.identifier)
        if len(chosen) >= limit:
            break
    return chosen


def sequenceable(items: list[Item], batch: list[Item]) -> list[Item]:
    """What a shared file alone kept out of the batch.

    Not in the batch, because a batch is offered as work that needs no
    thought about order. Not refused either, which is the distinction the
    batch's own line cannot carry: these are startable today against anything
    above them, provided the smaller change lands first.
    """
    taken = {item.identifier for item in batch}
    return [
        item
        for item in items
        if item.touches
        and item.identifier not in taken
        and not any(refusals(conflicts_for(item, [picked])) for picked in batch)
    ]
