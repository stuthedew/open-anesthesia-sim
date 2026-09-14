"""Tests for the conflict graph.

The asymmetry is the thing worth protecting: overlap proves contention, but
absence of declared overlap proves nothing. Tests assert both halves, so a
later change cannot quietly turn the advisory into a guarantee.
"""

from __future__ import annotations

from datetime import date

from docket.concurrency import (
    ORDERING,
    SAME_AREA,
    SAME_FILE,
    conflicts_for,
    observed_conflicts,
    parallel_batch,
    refusals,
    sequenceable,
    shared_by_path,
    shared_paths,
    undeclared,
)
from docket.model import Item
from docket.vcs import BranchFiles, FlightFiles


def _item(
    identifier: str,
    touches: tuple[str, ...] = (),
    blocked_by: tuple[str, ...] = (),
    priority: str = "P2",
) -> Item:
    return Item(
        identifier=identifier,
        title=f"Item {identifier}",
        priority=priority,
        effort="S",
        status="ready",
        classes=("perf",),
        touches=touches,
        blocked_by=blocked_by,
        feature="",
        milestone="",
        added=date(2026, 8, 1),
        closed=None,
        commit="",
        reason="",
        body="**Problem.** x\n**Why it matters.** y\n**Done when.** z\n",
    )


def test_identical_paths_overlap() -> None:
    assert shared_paths(_item("PL-1111", ("a/b.py",)), _item("PL-2222", ("a/b.py",))) == ("a/b.py",)


def test_a_directory_covers_what_is_beneath_it() -> None:
    one = _item("PL-1111", ("src/app/",))
    other = _item("PL-2222", ("src/app/view.py",))

    assert shared_paths(one, other) == ("src/app/",)


def test_unrelated_paths_do_not_overlap() -> None:
    assert shared_paths(_item("PL-1111", ("a.py",)), _item("PL-2222", ("b.py",))) == ()


def test_a_sibling_path_is_not_a_parent() -> None:
    """`src/app` must not be read as covering `src/application`."""
    assert (
        shared_paths(_item("PL-1111", ("src/app",)), _item("PL-2222", ("src/application/x.py",)))
        == ()
    )


def test_shared_files_are_a_conflict() -> None:
    one = _item("PL-1111", ("a.py",))
    (conflict,) = conflicts_for(one, [one, _item("PL-2222", ("a.py",))])

    assert conflict.reason == "edits the same file"
    assert conflict.paths == ("a.py",)


def test_two_items_naming_the_same_file_are_not_a_refusal() -> None:
    """`PL-VRMK`: a shared file orders work, it does not forbid it.

    27 of Gate 1's 112 open entries declared `docs/MODEL.md`, so reading this
    as a refusal excluded the gate's whole science half from every batch.
    """
    one = _item("PL-1111", ("docs/MODEL.md",))
    conflicts = conflicts_for(one, [one, _item("PL-2222", ("docs/MODEL.md",))])

    assert [c.strength for c in conflicts] == [SAME_FILE]
    assert refusals(conflicts) == []


def test_a_covering_directory_is_weaker_evidence_than_a_shared_file() -> None:
    """An item declaring `tests/` has not said it edits any particular file."""
    one = _item("PL-1111", ("tests/",))
    (conflict,) = conflicts_for(one, [one, _item("PL-2222", ("tests/unit/test_x.py",))])

    assert conflict.strength == SAME_AREA
    assert conflict.reason == "declares an area covering it"
    assert refusals([conflict]) == []


def test_an_ordering_edge_is_the_only_refusal() -> None:
    blocked = _item("PL-1111", ("a.py",), blocked_by=("PL-2222",))
    conflicts = conflicts_for(blocked, [_item("PL-2222", ("b.py",))])

    assert [c.strength for c in conflicts] == [ORDERING]
    assert refusals(conflicts) == conflicts


def test_a_blocker_is_a_conflict_in_both_directions() -> None:
    blocked = _item("PL-1111", ("a.py",), blocked_by=("PL-2222",))
    blocker = _item("PL-2222", ("b.py",))

    assert conflicts_for(blocked, [blocker])[0].reason == "blocks this item"
    assert conflicts_for(blocker, [blocked])[0].reason == "waits on this item"


def test_an_item_does_not_conflict_with_itself() -> None:
    one = _item("PL-1111", ("a.py",))

    assert conflicts_for(one, [one]) == []


def test_items_declaring_nothing_are_reported_not_assumed_safe() -> None:
    """Silence about files is a gap in the data, not an assurance."""
    silent = _item("PL-1111")

    assert undeclared([silent, _item("PL-2222", ("a.py",))]) == [silent]


def test_an_unlimited_batch_stays_the_independent_set() -> None:
    """Unlimited, the batch is still work that needs no thought about order."""
    items = [_item("PL-1111", ("a.py",)), _item("PL-2222", ("a.py",)), _item("PL-3333", ("b.py",))]

    assert [i.identifier for i in parallel_batch(items)] == ["PL-1111", "PL-3333"]


def test_a_limited_batch_fills_out_with_items_that_only_share_a_file() -> None:
    """Asked for three, the batch offers three rather than one (`PL-VRMK`).

    The independent set here is one item deep, because all three declare the
    same file - which is the shape of Gate 1's science half.
    """
    items = [_item(f"PL-{n}{n}{n}{n}", ("docs/MODEL.md",)) for n in (1, 2, 3)]

    batch = parallel_batch(items, limit=3)

    assert [i.identifier for i in batch] == ["PL-1111", "PL-2222", "PL-3333"]


def test_a_limited_batch_still_stops_at_an_ordering_edge() -> None:
    """Filling relaxes the file rule and never the `blocked-by` one."""
    first = _item("PL-1111", ("docs/MODEL.md",))
    waits = _item("PL-2222", ("docs/MODEL.md",), blocked_by=("PL-1111",))

    assert [i.identifier for i in parallel_batch([first, waits], limit=3)] == ["PL-1111"]


def test_sequenceable_names_what_a_shared_file_kept_out_of_the_batch() -> None:
    items = [_item("PL-1111", ("a.py",)), _item("PL-2222", ("a.py",)), _item("PL-3333", ("b.py",))]
    batch = parallel_batch(items)

    assert [i.identifier for i in sequenceable(items, batch)] == ["PL-2222"]


def test_sequenceable_excludes_what_an_ordering_edge_refuses() -> None:
    first = _item("PL-1111", ("a.py",))
    waits = _item("PL-2222", ("a.py",), blocked_by=("PL-1111",))

    assert sequenceable([first, waits], parallel_batch([first, waits])) == []


def test_a_batch_never_includes_an_item_declaring_no_paths() -> None:
    assert parallel_batch([_item("PL-1111")]) == []


def test_a_batch_prefers_priority_over_size() -> None:
    """Four trivial items that fit together are worth less than the important one."""
    items = [
        _item("PL-1111", ("shared.py",), priority="P1"),
        _item("PL-2222", ("shared.py",), priority="P3"),
        _item("PL-3333", ("shared.py",), priority="P3"),
    ]
    batch = parallel_batch(sorted(items, key=lambda i: i.sort_key()))

    assert [i.identifier for i in batch] == ["PL-1111"]


def test_a_batch_honors_its_limit() -> None:
    items = [_item(f"PL-{n}{n}{n}{n}", (f"{n}.py",)) for n in range(1, 5)]

    assert len(parallel_batch(items, limit=2)) == 2


def _files(*branches: tuple[str, tuple[str, ...], tuple[str, ...]]) -> FlightFiles:
    return FlightFiles(
        branches=tuple(
            BranchFiles(branch=name, item_ids=ids, paths=paths) for name, ids, paths in branches
        ),
        base="origin/main",
    )


def test_observed_overlap_reports_the_branch_changing_the_file() -> None:
    """The file the branch actually changed, not the declaration that matched.

    `PL-MC8Z`'s own case: an item declaring `subprojects/docket/` learns which
    file is being edited, which is what it can open.
    """
    item = _item("PL-1111", ("subprojects/docket/",))
    files = _files(("origin/other", ("PL-2222",), ("subprojects/docket/src/docket/checks.py",)))

    found = observed_conflicts(item, files)

    assert [entry.branch for entry in found] == ["origin/other"]
    assert found[0].paths == ("subprojects/docket/src/docket/checks.py",)
    assert found[0].describe() == "origin/other (PL-2222)"


def test_observed_overlap_ignores_a_branch_changing_nothing_this_item_declares() -> None:
    item = _item("PL-1111", ("src/app/view.py",))

    assert (
        observed_conflicts(item, _files(("origin/other", ("PL-2222",), ("docs/MODEL.md",)))) == []
    )


def test_an_item_does_not_collide_with_its_own_branch() -> None:
    item = _item("PL-1111", ("src/app/view.py",))

    assert (
        observed_conflicts(item, _files(("origin/mine", ("PL-1111",), ("src/app/view.py",)))) == []
    )


def test_an_item_declaring_nothing_observes_nothing() -> None:
    """Silence in `touches` is a gap in the evidence, and stays one here."""
    item = _item("PL-1111")

    assert observed_conflicts(item, _files(("origin/other", ("PL-2222",), ("a.py",)))) == []


# --- the shared-file tier, regrouped ----------------------------------------
#
# `PL-PGZK`. The tier reported one line per item, so a hub path every item
# declares and a path two items declare read identically and the whole list had
# to be read to find the strong evidence. Measured 2026-09-13 across the store:
# 237 open items declare 136 paths, the largest at 32 items, and 72 of the 136
# are declared by exactly one open item.


def test_shares_a_file_groups_by_path() -> None:
    """One line per path, rarest first, with nothing dropped.

    The ordering is the point rather than a tidy-up: the hub goes last because
    it is weak evidence, and the path two items declare goes first because it
    is the collision most likely to be real.
    """
    item = _item("PL-1111", ("docs/MODEL.md", "src/app/view.py", "src/core/tissue.py"))
    others = [
        _item("PL-2222", ("docs/MODEL.md",)),
        _item("PL-3333", ("docs/MODEL.md",)),
        _item("PL-4444", ("docs/MODEL.md", "src/app/view.py")),
        _item("PL-5555", ("src/core/tissue.py",)),
    ]

    groups = shared_by_path(conflicts_for(item, others))

    assert groups == [
        ("src/app/view.py", ("PL-4444",)),
        ("src/core/tissue.py", ("PL-5555",)),
        ("docs/MODEL.md", ("PL-2222", "PL-3333", "PL-4444")),
    ]


def test_the_regrouped_tier_drops_no_item() -> None:
    """Ordering the evidence is not filtering it, so the contract is unchanged.

    An item sharing two paths appears under both, which is what keeps a reader
    from concluding from one line that a collision is confined to one file.
    """
    item = _item("PL-1111", ("docs/MODEL.md", "src/app/view.py"))
    others = [_item("PL-2222", ("docs/MODEL.md", "src/app/view.py"))]

    groups = shared_by_path(conflicts_for(item, others))

    assert {identifier for _, identifiers in groups for identifier in identifiers} == {"PL-2222"}
    assert [path for path, _ in groups] == ["docs/MODEL.md", "src/app/view.py"]


def test_only_the_shared_file_tier_is_grouped() -> None:
    """A refusal and a coarser declaration are other tiers and stay in them.

    Grouping an `ORDERING` edge under a path would put a conflict that forbids
    the work into a tier headed "proceed, and land the smaller change first".
    """
    item = _item("PL-1111", ("src/app/view.py",), blocked_by=("PL-2222",))
    others = [_item("PL-2222", ("src/app/view.py",)), _item("PL-3333", ("src/app",))]

    assert shared_by_path(conflicts_for(item, others)) == []


def test_an_item_with_no_shared_file_groups_nothing() -> None:
    assert (
        shared_by_path(conflicts_for(_item("PL-1111", ("a.py",)), [_item("PL-2222", ("b.py",))]))
        == []
    )
