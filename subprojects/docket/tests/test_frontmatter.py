"""`docket.frontmatter`: where a YAML front matter ends, and where each key's value does.

Each extent below is the one PyYAML 6.0 composes for the same block, measured
when the reader was written (`PL-R417`).
"""

from __future__ import annotations

import pytest

from docket.frontmatter import (
    Unread,
    closing,
    closing_quote,
    key,
    keys,
    plain,
    statements,
    uncommented,
    unquote,
)


def _extents(text: str) -> list[tuple[str, int, int]]:
    return [(key.name, key.line, key.end) for key in keys(text.split("\n"))]


def test_it_closes_on_a_first_column_fence_and_never_on_an_indented_one() -> None:
    lines = ["---", "description: |", "  ---", "  more", "---  ", "body"]

    assert closing(lines) == 4
    assert closing(["---", "a: 1"]) is None
    assert closing(["a: 1", "---"]) is None


def test_a_quoted_value_runs_to_its_close_past_its_key_s_column() -> None:
    """The line it carries onto is no key, though it opens like one (`PL-BM8T`)."""
    text = 'description: "Loads at launch, since no\n paths: key defers it"\nname: x'

    assert _extents(text) == [("description", 0, 2), ("name", 2, 3)]


def test_a_flow_collection_runs_to_its_close_past_a_quote_its_word_holds() -> None:
    assert _extents("paths: [don't, 'x,\n y']\nnext: z") == [("paths", 0, 2), ("next", 2, 3)]


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


def test_statements_hands_back_why_it_read_a_block_a_line_at_a_time() -> None:
    """The fallback was silent, so a caller could not tell the two readings apart (`PL-JTP1`)."""
    spans, declined = statements(['description: "a record', '  wrapped"', "", "# why", "b: 1"])
    assert (spans, declined) == ([(0, 2), (3, 4), (4, 5)], None)

    spans, declined = statements(["a: 1", "not a key", "  b"])
    assert spans == [(0, 1), (1, 2), (2, 3)]
    assert str(declined) == "`not a key` sits at the first column and opens no key"


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


@pytest.mark.parametrize(
    ("line", "kept"),
    [
        ('paths: [a, "b # c"] # why', 'paths: [a, "b # c"] '),
        ("name: don 't # why", "name: don 't "),
        ('- "a # b" # why', '- "a # b" '),
        ("- &a 'x # y' # why", "- &a 'x # y' "),
        ('k: a - "b # c"', 'k: a - "b '),
    ],
)
def test_a_quote_opens_a_scalar_only_where_a_node_opens(line: str, kept: str) -> None:
    """A line's comment is where YAML ends its content (`PL-8MHZ`).

    Following only a quote that opened the text, this cut the first inside its
    quoted scalar; taking a quote after any white space for one,
    `required_checks_check` kept the second's comment as the name `don 't # why`.
    """
    assert uncommented(line) == kept


def test_a_quoted_key_is_read_as_yaml_unquotes_it() -> None:
    """This named the key `a\\"b` and `required_checks_check` refused it (`PL-8MHZ`)."""
    assert key('"a\\"b": 1') == ('a"b', 7)
    assert key("'it''s': 1") == ("it's", 8)


def test_a_key_written_as_a_flow_collection_is_named_by_no_reader() -> None:
    """`required_checks_check` named this key `[a]`, where YAML's is a sequence (`PL-8MHZ`)."""
    assert key("[a]: b") is None


@pytest.mark.parametrize(
    ("token", "held"),
    [
        ("'it''s'", "it's"),
        ('"a\\"b"', 'a"b'),
        ('"a\\\\b"', "a\\b"),
        ('"\\x41\\t\\u00e9\\U0001F600\\/"', "A\té\U0001f600/"),
        ("'a\\nb'", "a\\nb"),
    ],
)
def test_unquote_reads_the_escapes_yaml_defines(token: str, held: str) -> None:
    """`rules_paths_check` kept `'it''s'` whole and the backslash of `"a\\"b"` (`PL-8MHZ`)."""
    assert unquote(token) == held


@pytest.mark.parametrize("token", ['"a\\qb"', '"\\x4"', '"\\U00110000"', '"a" b', "plain"])
def test_unquote_refuses_what_yaml_refuses(token: str) -> None:
    with pytest.raises(Unread):
        unquote(token)


@pytest.mark.parametrize(
    ("text", "is_plain"),
    [
        ("x", True),
        ("-x", True),
        (":x", True),
        ("- x", False),
        (": x", False),
        ("|x", False),
        (">", False),
        ("'x'", False),
        ("[x]", False),
        ("", False),
    ],
)
def test_plain_reads_a_node_by_its_first_character(text: str, is_plain: bool) -> None:
    """`|x` is a block scalar's header YAML refuses, which `doc_check` read as plain (`PL-8MHZ`)."""
    assert plain(text) is is_plain
