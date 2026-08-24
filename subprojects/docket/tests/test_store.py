"""Tests for the item directory and id allocation.

The property under test throughout is that nothing here reads shared state to
decide what to write. That is what makes two branches safe to write at once,
and it is invisible in ordinary use - it only shows up as a collision months
later - so it is asserted directly.
"""

from __future__ import annotations

import random
from datetime import date
from pathlib import Path

from docket.model import Item
from docket.store import ID_RE, filename_for, find_item, new_id, read_items, slugify, write_item


def _item(identifier: str = "PL-K7QX", title: str = "Do the thing") -> Item:
    return Item(
        identifier=identifier,
        title=title,
        priority="P2",
        effort="S",
        status="ready",
        classes=("perf",),
        touches=(),
        blocked_by=(),
        feature="",
        milestone="",
        added=date(2026, 8, 1),
        closed=None,
        commit="",
        reason="",
        body="**Problem.** x\n**Why it matters.** y\n**Done when.** z\n",
    )


def test_new_ids_are_valid_and_unique() -> None:
    taken: set[str] = set()
    for _ in range(200):
        identifier = new_id(taken)
        assert ID_RE.match(identifier), identifier
        assert identifier not in taken
        taken.add(identifier)


def test_a_new_id_does_not_depend_on_what_else_exists() -> None:
    """The property that makes concurrent capture safe: no shared counter."""
    empty = new_id(set(), random.Random(7))
    crowded = new_id({f"PL-{n:03d}" for n in range(500)}, random.Random(7))

    assert empty == crowded


def test_new_id_avoids_a_collision_when_one_occurs() -> None:
    first = new_id(set(), random.Random(1))
    second = new_id({first}, random.Random(1))

    assert second != first


def test_historical_sequential_ids_stay_valid() -> None:
    """They are cited from commits and from each other; renumbering breaks that."""
    assert ID_RE.match("PL-001")
    assert ID_RE.match("PL-K7QX")
    assert not ID_RE.match("PL-1")
    assert not ID_RE.match("XX-0001")


def test_slugify_is_filename_safe_and_bounded() -> None:
    assert slugify("Decide what the interface shows") == "decide-what-the-interface-shows"
    assert slugify("Reject `unknown` keys!") == "reject-unknown-keys"
    assert slugify("") == "item"
    assert len(slugify("word " * 40)) <= 48


def test_filename_leads_with_the_id() -> None:
    """So a file is findable from a commit subject without knowing the title."""
    assert filename_for(_item()).startswith("PL-K7QX-")


def test_write_then_read_round_trips(tmp_path: Path) -> None:
    write_item(tmp_path, _item())
    (restored,) = read_items(tmp_path)

    assert restored.identifier == "PL-K7QX"
    assert restored.title == "Do the thing"


def test_renaming_removes_the_file_the_item_used_to_live_in(tmp_path: Path) -> None:
    original = write_item(tmp_path, _item(title="Old title"))
    write_item(tmp_path, _item(title="New title"), replace=original)

    assert not original.exists()
    assert len(read_items(tmp_path)) == 1


def test_a_readme_in_the_store_is_not_an_item(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# How this directory works\n", encoding="utf-8")
    write_item(tmp_path, _item())

    assert [i.identifier for i in read_items(tmp_path)] == ["PL-K7QX"]


def test_read_items_is_empty_without_a_directory(tmp_path: Path) -> None:
    assert read_items(tmp_path / "absent") == []


def test_find_item_tolerates_case_and_a_missing_prefix() -> None:
    items = [_item()]

    assert find_item(items, "pl-k7qx") is not None
    assert find_item(items, "K7QX") is not None
    assert find_item(items, "PL-0000") is None
