"""`docket.frontmatter`: where a YAML front matter ends, and where each key's value does.

Each extent below is the one PyYAML 6.0 composes for the same block, measured
when the reader was written (`PL-R417`).
"""

from __future__ import annotations

import pytest

from docket.frontmatter import Unread, closing, closing_quote, keys, uncommented


def _extents(text: str) -> list[tuple[str, int, int]]:
    return [(key.name, key.line, key.end) for key in keys(text.split("\n"))]


def test_it_closes_on_a_first_column_fence_and_never_on_an_indented_one() -> None:
    lines = ["---", "description: |", "  ---", "  more", "---  ", "body"]

    assert closing(lines) == 4
    assert closing(["---", "a: 1"]) is None
    assert closing(["a: 1", "---"]) is None


def test_a_quoted_value_runs_to_its_close_at_any_indentation() -> None:
    """The line it carries onto is no key, though it opens like one (`PL-BM8T`)."""
    text = 'description: "Loads at launch, since no\npaths: key defers it"\nname: x'

    assert _extents(text) == [("description", 0, 2), ("name", 2, 3)]


def test_a_flow_collection_runs_to_its_close_past_a_quote_its_word_holds() -> None:
    assert _extents("paths: [don't, 'x,\ny']\nnext: z") == [("paths", 0, 2), ("next", 2, 3)]


def test_a_block_scalar_holds_every_indented_line_a_comment_shaped_one_included() -> None:
    text = "description: |\n  text\n  # content\nnext: x"

    assert _extents(text) == [("description", 0, 3), ("next", 3, 4)]


def test_a_key_holding_nothing_on_its_line_holds_a_list_at_its_column() -> None:
    text = "paths:\n- /a/**\n# why\n- /b/**\nother: 1"

    assert _extents(text) == [("paths", 0, 4), ("other", 4, 5)]


def test_blank_lines_and_first_column_comments_after_a_value_are_no_part_of_it() -> None:
    assert _extents("a: 1\n\n# trailing\n\nb: 2") == [("a", 0, 1), ("b", 4, 5)]


def test_a_quoted_key_is_read_without_its_quotes() -> None:
    assert _extents("\"paths\": x\n'it''s': y") == [("paths", 0, 1), ("it's", 1, 2)]


@pytest.mark.parametrize(
    ("text", "named"),
    [
        ("a: 1\nnot a key", "`not a key` sits at the first column and opens no key"),
        ("- a\n- b", "`- a` sits at the first column and opens no key"),
        ("  a: 1", "`a: 1` is indented above the first key, so no value holds it"),
        ('paths: "/src/**\n  more', '`paths: "/src/**` opens a quoted scalar that nothing'),
        ("paths: [a,\n  b", "`paths: [a,` opens a flow collection that nothing"),
    ],
)
def test_a_block_it_cannot_split_is_refused_naming_the_line(text: str, named: str) -> None:
    with pytest.raises(Unread, match=named.replace("[", r"\[").replace("*", r"\*")):
        keys(text.split("\n"))


@pytest.mark.parametrize(
    ("text", "node"),
    [
        ('"/src/**" # why', '"/src/**" '),
        ('"a # b"', '"a # b"'),
        ("/src/#x", "/src/#x"),
        ("/src/** # why", "/src/** "),
        ('"/src/** # still open', '"/src/** # still open'),
    ],
)
def test_a_comment_opens_after_white_space_and_outside_a_quote(text: str, node: str) -> None:
    assert uncommented(text) == node


def test_a_quote_closes_past_its_escapes() -> None:
    assert closing_quote('"a \\" b" c') == 7
    assert closing_quote("'it''s' x") == 6
    assert closing_quote('"open') == -1
