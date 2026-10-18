"""`docket.frontmatter.keys` ends each key where PyYAML does, over generated front matters.

`keys` reads where each top-level key of a rule's or skill's front matter ends,
by hand, because docket runs on the standard library alone (`PL-R417`). Its one
measured miss was `PL-YQ9G`: a quoted scalar or a flow collection opened on the
line below its key, the value itself or a list entry, was followed by
indentation alone, so a first-column line inside it read as a key. A corpus
like this one found it, run once in the parsing review of 2026-10-10 (C1); this
runs one on every pull request, held to PyYAML 6.0, a dev dependency, as
`test_markdown_reference.py` holds `docket.markdown` to markdown-it-py.

Hypothesis draws the front matters, derandomized, so a red run reproduces
exactly and the suite stays deterministic. Each is YAML PyYAML composes into
one mapping, built from the forms a front matter here writes and the ones that
broke a reader: plain, quoted, flow and block scalar values, lists at the key's
column and under it, nested mappings and a mapping in a list entry, comments,
anchors and tags, and every node that runs to a close of its own opened on the
key's line, alone on the line under a key or entry, after a list entry's `- `
and after a nested key's `:`, its later lines carried on at any indent past
the column of the key or entry holding it, which YAML asks of them
(`PL-P6LL`), shallower than the node's own opening included, and shaped like a
key or a list entry there. Some end with YAML's document-end marker, `...`,
and blank or comment lines after it (`PL-G8ZN`). A block
scalar's lines and a plain scalar's continuation lines are drawn in the same
shapes, since a reader that took them for structure would read a key out of
them. The helpers take the one `draw` and build no strategy of their own, which
keeps the corpus to a few seconds.

For each, the keys `keys` reads, by name and line, must be PyYAML's top-level
keys, and each value must end on the line PyYAML's node ends on, past only
blank lines and `#`-led ones, which PyYAML reads as nothing and `keys` hands to
the value above them. And the quoted scalars `quoted` places must be the ones
PyYAML's scanner reads, each opening and closing where PyYAML's does, so that a
quote opening a block scalar's line or a plain scalar's continuation line,
which the corpus draws, is none (`PL-S4JL`).

And the comments `comments` places must be the ones PyYAML reads, where no
reader keeps one: a `#` opens a comment exactly where the text from it to its
line's end can be written otherwise and PyYAML still loads the same document,
so a `#` in a block scalar's content or a quoted scalar's line opens none, and
one after a block scalar's content opens one at any depth (`PL-W9VC`). The
corpus draws those, a comment in a flow collection and on a plain scalar's
continuation line among them.

Two more corpora hold a line's own grammar to PyYAML's scanner (`PL-8MHZ`):
`uncommented` must end a line where PyYAML's last token on it ends, over lines
whose quotes stand where a node opens and where it does not, and `unquote` must
read a quoted scalar as PyYAML loads it, every escape YAML 1.2.2 § 5.7 defines
among them.
"""

from __future__ import annotations

import itertools
import operator
import re

import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

from docket.frontmatter import comments, keys, quoted, uncommented, unquote

LETTERS = "abcdefghijklmnopqrstuvwxyz"
#: A word of a plain scalar in a block, which may hold no `: ` and no ` #`.
WORD = st.builds(
    operator.add, st.sampled_from(LETTERS), st.text(LETTERS + "0123456789./()*_", max_size=5)
)
WORDS = st.lists(WORD, min_size=1, max_size=4).map(" ".join)
NAME = st.builds(
    operator.add, st.sampled_from(LETTERS), st.text(LETTERS + "0123456789_", max_size=7)
)
#: Text that opens like structure: a key, a list entry, a comment, a collection.
SHAPES = st.sampled_from(
    ("name: value", "paths: x", "- item", "-", "key:", "# hash", "[open", "{open", "? q")
)
#: A quoted scalar's lines, and a block scalar's.
QUOTED_TEXT = st.lists(st.one_of(WORDS, SHAPES), min_size=1, max_size=4)
BLOCK_TEXT = st.one_of(WORDS, SHAPES, st.sampled_from(('"open', "'open")))
#: An entry of a flow collection: a plain scalar, which may hold no indicator, or a quoted one.
FLOW_ITEM = st.one_of(
    st.text(LETTERS + "0123456789", min_size=1, max_size=6),
    st.sampled_from(('"a, ]b"', "'c} d'", '"e: #f"')),
)
#: What a plain scalar's continuation line may open with.
CONTINUED = st.one_of(
    WORDS, st.sampled_from(('"open', "'open", "- item", "[open", "{open", "| bar"))
)
#: How far past its holder's column a quoted scalar's or a flow collection's later line is indented.
CARRIED = st.sampled_from((1, 1, 2, 3, 5))
#: What may follow a node's close on its line.
AFTER = st.sampled_from(("", " # after"))
#: An anchor or a tag before a node, which names it and changes nothing in it.
PREFIX = st.sampled_from(("", "", "", "&anchor ", "!!str "))
QUOTE = st.sampled_from(("'", '"'))
HEADER = st.sampled_from(("|", ">", "|-", ">+", "| # why"))
DEEPER = st.sampled_from((0, 0, 2))
NODE = st.sampled_from(("plain", "quoted", "flow", "block"))
BELOW = st.sampled_from(("plain", "quoted", "flow"))
BELOW_COLUMN = st.sampled_from((1, 2, 4))
#: How a list entry or a nested key holds its node; one at the top level may hold a collection.
ENTRY = st.sampled_from(("same", "same", "below", "empty"))
TOP_ITEM = st.sampled_from(("same", "same", "below", "empty", "mapping"))
TOP_KEY = st.sampled_from(("same", "same", "below", "empty", "list"))
VALUE = st.sampled_from(("inline", "inline", "below", "list", "mapping", "empty"))
LIST_COLUMN = st.sampled_from((0, 2))
MAPPING_COLUMN = st.sampled_from((2, 4))
BETWEEN = st.sampled_from(("", "# between keys"))
DOCUMENT_END = st.sampled_from(("...", "... # end", "...  "))


def _quoted(draw: st.DrawFn, column: int, holder: int) -> list[str]:
    """A quoted scalar opening at `column`, its later lines carried on past `holder`."""
    quote = draw(QUOTE)
    pieces = draw(QUOTED_TEXT)
    if quote == "'" and draw(st.booleans()):
        pieces[0] += " it''s"
    lines = [" " * column + quote + pieces[0]]
    lines.extend(" " * (holder + draw(CARRIED)) + piece for piece in pieces[1:])
    lines[-1] += quote + draw(AFTER)
    return lines


def _flow(draw: st.DrawFn, column: int, holder: int) -> list[str]:
    """A flow sequence or mapping opening at `column`, its later lines carried on past `holder`."""
    entries = draw(st.lists(FLOW_ITEM, min_size=1, max_size=4))
    mapping = draw(st.booleans())
    if mapping:
        names = draw(st.lists(NAME, min_size=len(entries), max_size=len(entries), unique=True))
        entries = [f"{name}: {entry}" for name, entry in zip(names, entries, strict=True)]
    lines = [" " * column + ("{" if mapping else "[")]
    for index, entry in enumerate(entries):
        if index and draw(st.booleans()):
            lines[-1] += draw(AFTER)
            lines.append(" " * (holder + draw(CARRIED)))
        lines[-1] += entry + ("," if index < len(entries) - 1 else "")
    lines[-1] += ("}" if mapping else "]") + draw(AFTER)
    return lines


def _plain(draw: st.DrawFn, column: int, holder: int) -> list[str]:
    """A plain scalar at `column`, carried on over lines indented past `holder`."""
    lines = [" " * column + draw(WORDS)]
    for _ in range(draw(st.integers(0, 2))):
        lines.append(" " * (holder + draw(st.integers(1, 3))) + draw(CONTINUED))
    lines[-1] += draw(AFTER)
    return lines


def _block_scalar(draw: st.DrawFn, holder: int) -> list[str]:
    """A block scalar's header, and its lines indented past `holder`, the first least."""
    lines = [draw(HEADER)]
    indent = holder + draw(st.integers(1, 3))
    for index in range(draw(st.integers(1, 3))):
        deeper = draw(DEEPER) if index else 0
        lines.append(" " * (indent + deeper) + draw(BLOCK_TEXT))
        if draw(st.integers(0, 4)) == 0:
            lines.append("")
    if draw(st.integers(0, 2)) == 0:
        # A comment short of the content ends it, and one after that is one at any depth.
        lines.append(" " * draw(st.integers(0, indent - 1)) + "# trail")
        lines.append(" " * (indent + draw(DEEPER)) + "# deeper")
    return lines


def _node(draw: st.DrawFn, holder: int) -> list[str]:
    """A node opening on its entry's own line, the entry at column `holder`.

    Its first line is the text after the entry's `:` or `- `, and the rest are
    the lines under it.
    """
    kind = draw(NODE)
    if kind == "plain":
        lines = _plain(draw, 0, holder)
    elif kind == "quoted":
        lines = _quoted(draw, 0, holder)
    elif kind == "flow":
        lines = _flow(draw, 0, holder)
    else:
        lines = _block_scalar(draw, holder)
    return [draw(PREFIX) + lines[0], *lines[1:]]


def _below(draw: st.DrawFn, column: int, holder: int) -> list[str]:
    """A node alone on the line under an entry at `holder`, opening at `column`."""
    kind = draw(BELOW)
    if kind == "plain":
        return _plain(draw, column, holder)
    return _quoted(draw, column, holder) if kind == "quoted" else _flow(draw, column, holder)


def _entry(draw: st.DrawFn, column: int, indicator: str, nested: bool = True) -> list[str]:
    """A list entry (`-`) or a nested key (`name:`) at `column`, and its node.

    A `nested` one may hold a collection of its own: a mapping in a list entry,
    or a list under a nested key, whose entries hold none.
    """
    lead = " " * column + indicator
    form = draw((TOP_ITEM if indicator == "-" else TOP_KEY) if nested else ENTRY)
    if form == "empty":
        return [lead]
    if form == "below":
        return [lead, *_below(draw, column + draw(st.integers(1, 3)), column)]
    if form == "mapping":
        names = draw(st.lists(NAME, min_size=1, max_size=3, unique=True))
        first = _entry(draw, column + 2, f"{names[0]}:", nested=False)
        lines = [lead + " " + first[0].lstrip(" "), *first[1:]]
        for name in names[1:]:
            lines.extend(_entry(draw, column + 2, f"{name}:", nested=False))
        return lines
    if form == "list":
        inner = column + draw(LIST_COLUMN)
        lines = [lead]
        for _ in range(draw(st.integers(1, 3))):
            lines.extend(_entry(draw, inner, "-", nested=False))
        return lines
    first, *under = _node(draw, column)
    return [f"{lead} {first}", *under]


def _value(draw: st.DrawFn) -> list[str]:
    """A top-level key's value: the rest of the key's line, then the lines under it."""
    form = draw(VALUE)
    if form == "empty":
        return [""]
    if form == "inline":
        first, *under = _node(draw, 0)
        return [f" {first}", *under]
    if form == "below":
        return ["", *_below(draw, draw(BELOW_COLUMN), 0)]
    lines = [""]
    if form == "list":
        column = draw(LIST_COLUMN)
        for _ in range(draw(st.integers(1, 3))):
            lines.extend(_entry(draw, column, "-"))
            if draw(st.integers(0, 5)) == 0:
                lines.append(" " * max(column, 1) + "# between")
        return lines
    column = draw(MAPPING_COLUMN)
    for name in draw(st.lists(NAME, min_size=1, max_size=3, unique=True)):
        lines.extend(_entry(draw, column, f"{name}:"))
    return lines


@st.composite
def front_matters(draw: st.DrawFn) -> list[str]:
    """A front matter's lines between its fences, each anchor in it named once."""
    block: list[str] = []
    for name in draw(st.lists(NAME, min_size=1, max_size=4, unique=True)):
        if block and draw(st.integers(0, 4)) == 0:
            block.append(draw(BETWEEN))
        first, *under = _value(draw)
        block.extend([f"{name}:{first}", *under])
    if draw(st.integers(0, 5)) == 0:
        # YAML's document-end marker, after which only comments may follow (`PL-G8ZN`).
        block.append(draw(DOCUMENT_END))
        block.extend(draw(st.lists(st.sampled_from(("", "# after", "  # indented")), max_size=2)))
    numbers = itertools.count()
    return [re.sub("&anchor", lambda _: f"&a{next(numbers)}", line) for line in block]


def _core(block: list[str], last: int) -> int:
    """The last line at or before `last` holding something other than white space or a comment."""
    while last >= 0 and (not block[last].strip() or block[last].lstrip().startswith("#")):
        last -= 1
    return last


def _pyyaml_reading(block: list[str]) -> list[tuple[str, int, int]]:
    """Each top-level key PyYAML composes: its name, its line, and its value's last line."""
    document = yaml.compose("\n".join(block) + "\n", Loader=yaml.SafeLoader)
    assert isinstance(document, yaml.MappingNode), "the strategy drew no mapping"
    found = []
    for key, value in document.value:
        mark = value.end_mark
        end = mark.line if mark.column else mark.line - 1
        found.append((key.value, key.start_mark.line, _core(block, max(end, key.start_mark.line))))
    return found


@settings(derandomize=True, database=None, deadline=None, max_examples=2000)
@given(front_matters())
def test_keys_end_each_value_where_pyyaml_does(block: list[str]) -> None:
    expected = _pyyaml_reading(block)

    found = [(key.name, key.line, _core(block, key.end - 1)) for key in keys(block)]

    assert found == expected, "\n".join(block)


def _pyyaml_quoted(block: list[str]) -> list[tuple[str, int, int, int, int]]:
    """Each quoted scalar PyYAML scans: its quote, and where its opening and closing quotes sit."""
    return [
        (
            token.style,
            token.start_mark.line,
            token.start_mark.column,
            token.end_mark.line,
            token.end_mark.column - 1,
        )
        for token in yaml.scan("\n".join(block) + "\n", Loader=yaml.SafeLoader)
        if isinstance(token, yaml.ScalarToken) and token.style in ("'", '"')
    ]


@settings(derandomize=True, database=None, deadline=None, max_examples=2000)
@given(front_matters())
def test_quoted_places_each_quoted_scalar_where_pyyaml_does(block: list[str]) -> None:
    expected = _pyyaml_quoted(block)

    found = [(at.quote, at.line, at.column, at.end_line, at.end_column) for at in quoted(block)]

    assert found == expected, "\n".join(block)


def _shape(node: yaml.Node) -> object:
    """What PyYAML composed, less where it stands: each node's tag, style and value."""
    if isinstance(node, yaml.ScalarNode):
        return node.tag, node.style, node.value
    if isinstance(node, yaml.SequenceNode):
        return node.tag, tuple(_shape(item) for item in node.value)
    return node.tag, tuple((_shape(key), _shape(value)) for key, value in node.value)


def _composed(block: list[str]) -> object:
    """The document PyYAML composes from `block`, as `_shape` reads it, or `None` if it refuses."""
    try:
        return _shape(yaml.compose("\n".join(block) + "\n", Loader=yaml.SafeLoader))
    except yaml.YAMLError:
        return None


def _pyyaml_comments(block: list[str]) -> list[tuple[int, int]]:
    """Each comment PyYAML reads in `block`, as its line and its `#`'s column.

    PyYAML keeps no comment, so each `#` is tried: one opens a comment where
    writing other text from it to its line's end leaves the document PyYAML
    composes as it was, and none earlier on its line does.
    """
    document = _composed(block)
    assert document is not None, "the strategy drew no YAML"
    found = []
    for line, text in enumerate(block):
        for column in (at for at, char in enumerate(text) if char == "#"):
            if _composed([*block[:line], text[:column] + "#zq", *block[line + 1 :]]) == document:
                found.append((line, column))
                break
    return found


@settings(derandomize=True, database=None, deadline=None, max_examples=1000)
@given(front_matters())
def test_comments_places_each_comment_where_pyyaml_reads_one(block: list[str]) -> None:
    assert list(comments(block)) == _pyyaml_comments(block), "\n".join(block)


#: What opens a line before its node: nothing, a list entry, an explicit key, or a key.
LINE_LEAD = st.sampled_from(("", "- ", "? ", "- - ", "key: ", "- key: ", '"k # y": ', "'it''s': "))
#: A plain scalar's word, whose quote, bracket, comma or `#` opens nothing, no blank before it.
PLAIN_WORD = st.builds(
    operator.add, st.sampled_from(LETTERS), st.text(LETTERS + "'\"#,[]{}-", max_size=5)
)
#: What may stand between a plain scalar's words: an indicator, or a quote or a bracket
#: after white space, none of which opens anything inside a plain scalar.
PLAIN_GAP = st.sampled_from((" ", " - ", " ? ", ", ", " '", ' "', " ["))
#: The pieces of a quoted scalar written on one line, by its quote.
DOUBLE_PIECE = st.sampled_from(
    (
        "a",
        " ",
        "# x",
        "'",
        ": y",
        "[,]",
        '\\"',
        "\\\\",
        "\\/",
        "\\t",
        "\\\t",
        "\\n",
        "\\0",
        "\\a",
        "\\b",
        "\\v",
        "\\f",
        "\\r",
        "\\e",
        "\\ ",
        "\\N",
        "\\_",
        "\\L",
        "\\P",
        "\\x41",
        "\\u00e9",
        "\\U0001F600",
    )
)
SINGLE_PIECE = st.sampled_from(("a", " ", "# x", '"', "''", ": y", "[,]", "\\", "\\n"))
#: What follows a node on its line.
TRAILER = st.sampled_from(("", " # tail", "  #"))
PROPERTY = st.sampled_from(("", "", "&a ", "!!str "))


@st.composite
def one_line_quoted(draw: st.DrawFn) -> str:
    """A quoted scalar closing on its own line, its quotes included."""
    quote = draw(QUOTE)
    pieces = draw(st.lists(DOUBLE_PIECE if quote == '"' else SINGLE_PIECE, max_size=6))
    return quote + "".join(pieces) + quote


@st.composite
def one_line_flow(draw: st.DrawFn) -> str:
    """A flow sequence or mapping closing on its own line, a quoted entry's `#` its content."""
    entries = draw(st.lists(st.one_of(NAME, one_line_quoted()), min_size=1, max_size=3))
    if draw(st.booleans()):
        return "[" + ", ".join(entries) + "]"
    names = draw(st.lists(NAME, min_size=len(entries), max_size=len(entries), unique=True))
    pairs = [
        f'"{name}":{entry}' if entry[:1] == '"' else f"{name}: {entry}"
        for name, entry in zip(names, entries, strict=True)
    ]
    return "{" + ", ".join(pairs) + "}"


@st.composite
def yaml_lines(draw: st.DrawFn) -> str:
    """One line of YAML: a lead, perhaps an anchor or a tag, a node, and perhaps a comment."""
    kind = draw(st.sampled_from(("plain", "quoted", "flow")))
    if kind == "plain":
        words = draw(st.lists(PLAIN_WORD, min_size=1, max_size=4))
        node = words[0] + "".join(draw(PLAIN_GAP) + word for word in words[1:])
    else:
        node = draw(one_line_quoted() if kind == "quoted" else one_line_flow())
    return draw(LINE_LEAD) + draw(PROPERTY) + node + draw(TRAILER)


def _pyyaml_content_end(line: str) -> int:
    """Where PyYAML's last token on `line` ends, which is where its comment, if any, may open."""
    return max(
        token.end_mark.index
        for token in yaml.scan(line + "\n", Loader=yaml.SafeLoader)
        if not isinstance(token, yaml.StreamEndToken | yaml.BlockEndToken)
    )


@settings(derandomize=True, database=None, deadline=None, max_examples=2000)
@given(yaml_lines())
def test_uncommented_ends_a_line_where_pyyaml_ends_its_content(line: str) -> None:
    assert uncommented(line).rstrip() == line[: _pyyaml_content_end(line)], line


@settings(derandomize=True, database=None, deadline=None, max_examples=500)
@given(one_line_quoted())
def test_unquote_reads_a_quoted_scalar_as_pyyaml_loads_it(token: str) -> None:
    assert unquote(token) == yaml.safe_load(f"k: {token}")["k"], token
