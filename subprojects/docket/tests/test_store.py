"""Tests for the item directory and id allocation.

The property under test throughout is that nothing here reads shared state to
decide what to write. That is what makes two branches safe to write at once,
and it is invisible in ordinary use - it only shows up as a collision months
later - so it is asserted directly.
"""

from __future__ import annotations

import ast
import random
import re
from collections.abc import Iterator
from dataclasses import replace
from datetime import date
from pathlib import Path

from docket.model import Item
from docket.store import (
    ID_RE,
    filename_for,
    find_item,
    new_id,
    read_items,
    rewrite_item,
    slugify,
    write_item,
)


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
    """The property that makes concurrent capture safe: no shared counter.

    The seeded `random.Random` is what makes the assertion possible: two
    allocations from the same seed must agree, which is only observable if
    the generator is reproducible. `new_id` defaults to `random.SystemRandom`
    in production and takes the generator as a parameter precisely so a test
    can pass a seeded one - swapping this for the unseeded default would not
    harden anything and would delete the property under test.
    """
    empty = new_id(set(), random.Random(7))
    crowded = new_id({f"PL-{n:03d}" for n in range(500)}, random.Random(7))

    assert empty == crowded


def test_new_id_avoids_a_collision_when_one_occurs() -> None:
    # Seeded so both calls draw the same first candidate and the collision
    # this test is about actually happens - see the test above.
    first = new_id(set(), random.Random(1))
    second = new_id({first}, random.Random(1))

    assert second != first


def test_historical_sequential_ids_stay_valid() -> None:
    """They are cited from commits and from each other; renumbering breaks that."""
    assert ID_RE.match("PL-001")
    assert ID_RE.match("PL-K7QX")
    assert not ID_RE.match("PL-1")  # not-an-id
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


def test_rewrite_item_keeps_the_file_it_came_from(tmp_path: Path) -> None:
    """A title edit through `write_item` renames; a field write through this never does.

    A rename arriving as a side effect of a field write lands in a diff about
    something else and conflicts against whoever else holds the file (`PL-LBR6`).
    """
    original = write_item(tmp_path, _item(title="Old title"))
    (restored,) = read_items(tmp_path)

    target = rewrite_item(tmp_path, replace(restored, title="New title"))

    assert target == original
    assert [p.name for p in tmp_path.glob("*.md")] == [original.name]
    assert "title: New title" in original.read_text(encoding="utf-8")


# A fixture id is a value a test hands to the store; an id named in prose is
# not. `f"PL-B1B{n}"` mints `PL-B1B0`, so a hole stands for the digits it will
# be given - one, or the width an explicit format spec asks for. Dropping them
# instead would report `PL-B1B` as three characters, and a check with a false
# positive that obvious is one nobody leaves switched on.
_CANDIDATE_RE = re.compile(r"PL-[A-Za-z0-9]+")
_SPEC_WIDTH_RE = re.compile(r"0(\d+)d\Z")
_DOCSTRING_HOLDERS = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def _hole_width(hole: ast.FormattedValue) -> int:
    """How many digits one `{...}` will contribute, read from its format spec."""
    spec = hole.format_spec
    if isinstance(spec, ast.JoinedStr):
        literal = "".join(
            part.value
            for part in spec.values
            if isinstance(part, ast.Constant) and isinstance(part.value, str)
        )
        found = _SPEC_WIDTH_RE.search(literal)
        if found:
            return int(found.group(1))
    return 1


def _rendered(node: ast.JoinedStr) -> str:
    """One f-string as the id it will mint, holes filled with their digits."""
    parts: list[str] = []
    for part in node.values:
        if isinstance(part, ast.Constant) and isinstance(part.value, str):
            parts.append(part.value)
        elif isinstance(part, ast.FormattedValue):
            parts.append("0" * _hole_width(part))
    return "".join(parts)


def _values(node: ast.AST) -> Iterator[tuple[int, str]]:
    """Every string a test *uses*, with the line it starts on.

    An f-string short-circuits its own children: its fragments are pieces of
    the value yielded for the whole, and yielding them again is what would
    turn every `f"PL-B1B{n}"` into a finding.
    """
    if isinstance(node, ast.JoinedStr):
        yield node.lineno, _rendered(node)
        return
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str):
            yield node.lineno, node.value
        return
    for child in ast.iter_child_nodes(node):
        yield from _values(child)


def _without_docstrings(tree: ast.Module) -> ast.Module:
    """The same tree with every docstring dropped, so prose is not scanned."""
    for node in ast.walk(tree):
        if not isinstance(node, _DOCSTRING_HOLDERS) or not node.body:
            continue
        first = node.body[0]
        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            node.body = node.body[1:]
    return tree


def test_every_fixture_id_is_one_the_store_could_mint() -> None:
    """A fixture outside the alphabet is a test that silently exercises nothing.

    `read_items` takes the `id` field verbatim, so `PL-STUV` parses and behaves
    like any other fixture right up to the moment it reaches something that
    applies `ID_PATTERN` - and then it matches nothing at all. A test asserting
    that an id is absent from a listing, excluded from a pick, or unrecognised
    in prose then passes against a broken implementation as readily as a
    correct one. `test_roadmap.py` asserted for seventeen days that a prose
    mention is placed nowhere while naming an id the parser could never have
    placed; breaking the placement rule left it green (`PL-GXPP`).

    Values only. Comments never reach the tree and docstrings are dropped, so
    an id discussed in writing needs nothing. A fixture malformed on purpose -
    the rejection tests need one - says so with a `not-an-id` comment on the
    line its literal opens. That marker is inline rather than a list kept here,
    because a list can name a literal the tree no longer holds and nothing
    would ever say so.
    """
    tests = sorted(Path(__file__).parent.glob("*.py"))
    assert tests, "no test modules found; the glob is wrong"

    offenders: list[str] = []
    for path in tests:
        lines = path.read_text(encoding="utf-8").splitlines()
        tree = _without_docstrings(ast.parse("\n".join(lines), filename=str(path)))
        for line_number, value in _values(tree):
            if "not-an-id" in lines[line_number - 1]:
                continue
            for found in _CANDIDATE_RE.finditer(value):
                if not ID_RE.match(found.group(0)):
                    offenders.append(f"{path.name}:{line_number} {found.group(0)}")

    assert not offenders, (
        "these fixture ids are outside the alphabet the store mints, so anything "
        "applying `ID_PATTERN` to one matches nothing and any assertion resting on "
        "that passes vacuously: " + ", ".join(offenders)
    )
