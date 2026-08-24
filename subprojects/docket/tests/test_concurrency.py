"""Tests for the conflict graph.

The asymmetry is the thing worth protecting: overlap proves contention, but
absence of declared overlap proves nothing. Tests assert both halves, so a
later change cannot quietly turn the advisory into a guarantee.
"""

from __future__ import annotations

from datetime import date

from docket.concurrency import conflicts_for, parallel_batch, shared_paths, undeclared
from docket.model import Item


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

    assert conflict.reason == "shares files"
    assert conflict.paths == ("a.py",)


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


def test_a_batch_excludes_items_that_share_files() -> None:
    items = [_item("PL-1111", ("a.py",)), _item("PL-2222", ("a.py",)), _item("PL-3333", ("b.py",))]

    assert [i.identifier for i in parallel_batch(items)] == ["PL-1111", "PL-3333"]


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
