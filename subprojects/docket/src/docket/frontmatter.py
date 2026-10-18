"""Where a Markdown file's YAML front matter ends, and where each key in it does.

The front matter Claude Code reads on a rule or a skill: a first line of `---`,
then YAML, then a closing `---`. This is the one reading of it (`PL-R417`):
`tools/rules_paths_check.py` reads a rule's `paths:` through it,
`tools/doc_check.py` whether a rule declares one and each key's value as a
statement of its own, `docket.instructions` each key's dated sentences,
`docket.notes` where a notes file's Markdown begins, and
`tools/fixture_id_check.py` which quoted scalar a line break is escaped in,
and `tools/required_checks_check.py` and `tools/doc_check.py` a workflow's
lines, keys and quoted scalars, and which node a value opens (`PL-8MHZ`), and
`tools/doc_check.py` where a YAML file's comments open (`comments`, `PL-W9VC`).
Each of those read the block its own way, a physical line at a time or as
Markdown, where YAML 1.2.2 carries a value across lines: a quoted scalar to its
closing quote (§ 7.3.1, § 7.3.2), a flow collection to its closing bracket
(§ 7.4), and a block scalar, a block collection or a plain scalar over the lines
indented under its key (§ 8.1, § 8.2, § 7.3.3). So a `#`-led line inside a
quoted glob was read as a comment, a line opening `paths:` inside another key's
quoted value as that key (`PL-BM8T`), and the block as one Markdown paragraph,
which dated every key by the newest date in any of them (`PL-2MLT`).

**Where each top-level key's value ends is what this reads, and no value.** A
value runs over the lines indented under its key, and where its key holds
nothing on its own line, over `- ` items at the key's column too (§ 8.2.1). A
quoted scalar or a flow collection runs to its close, however much shallower
than its opening the lines below it are, so the key such a line looks like is
no key. Each of those lines must still be indented past the column of the key
or `- ` holding the node. PyYAML 6.0 reads one at the first column as the
node's, but YAML 1.2.2 refuses the file (§ 6.3), and so does this reader
(`PL-P6LL`). That holds wherever one opens, on the key's own
line or below it - alone on the line under a key or list entry holding nothing,
after a list entry's `- `, or after a nested key's `:` (§ 8.2.1, § 8.2.2). Below
the key's line it was once followed by indentation alone, so a first-column
line inside it read as a key (`PL-YQ9G`). A block scalar's lines and a plain
scalar's continuation lines are text, so a quote opening one of them opens
nothing; `quoted` hands back the quoted scalars this reading does follow, each
where it opens and closes (`PL-S4JL`). A line at the first column that opens no
key raises `Unread` naming it, as does an indented line above the first key,
since no value holds either and a reader passing over one would hand on the key
above it short.

**What YAML refuses in the forms read here is refused, not passed over**
(`PL-P6LL`). A value's lines are held to the block collections open above
them (§ 8.2). A node is held to what may follow its close (§ 6.6, § 7.4), and
to what may open it on its key's line (§ 8.2.2). A plain scalar's continuation
lines and a block scalar's opening lines are held to their own rules (§ 7.3.3,
§ 8.1.1). Each breach raises `Unread`, because a rule whose front matter YAML
refuses may have no `paths:` read from it by Claude Code while it passes every
check here. What a value holds past that is still its reader's to decide, and
`rules_paths_check.entries` decides `paths:`'s. Where each value ends, and
where each quoted scalar opens and closes, is held to PyYAML's reading over a
generated corpus by `subprojects/docket/tests/test_frontmatter_reference.py`.
What it refuses is held to the YAML Test Suite's in-domain cases by
`subprojects/docket/tests/test_frontmatter_suite.py`, since PyYAML implements
YAML 1.1 and accepts some of what the suite refuses.

**A line's own grammar is read here too, once** (`PL-8MHZ`): where its comment
opens (`uncommented`), the key it opens (`key`), what a quoted scalar holds
(`unquote`), whether a node is a plain scalar (`plain`), and a block scalar's
header (`BLOCK_SCALAR_RE`), with where the content under it ends
(`block_content`, `PL-W9VC`). The checks that read
a workflow or a rule each spelt them beside this module, and parted on the
first input one had not been written for: `[a, "b # c"]` lost its scalar's tail
here, `don 't # x` kept its comment in `required_checks_check`, `"a\\"b":`
named a key with its backslash here, and `'it''s'` kept both quotes in
`rules_paths_check`.

Not docket's own item front matter, which is not YAML: its grammar is
`docket.model`'s. Standard library only, as the rest of the package is.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field

#: The line that opens a front matter, and the line that closes it.
FENCE = "---"

#: What opens a node other than a plain scalar (YAML 1.2.2 § 5.3), so a line
#: opening with one opens no plain key: `-`, `?` and `:` only where white space
#: or the line's end follows them.
INDICATORS = frozenset("-?:,[]{}#&*!|>'\"%@`")
#: What opens a node that runs to a close of its own rather than over the lines
#: indented under it: a quoted scalar (§ 7.3.1, § 7.3.2) or a flow collection
#: (§ 7.4).
CLOSED_NODES = frozenset("'\"[{")
#: What follows an indicator for it to be one rather than a plain scalar's first
#: character, and what follows a key's `:` (§ 7.3.3, § 8.2.2).
BLANKS = ("", " ", "\t")
#: Each escape a double-quoted scalar may hold, by the character after its
#: backslash, and what it stands for (YAML 1.2.2 § 5.7). A tab is escaped as
#: `\t` or as a backslash before a literal tab.
ESCAPES = {
    "0": "\0",
    "a": "\a",
    "b": "\b",
    "t": "\t",
    "\t": "\t",
    "n": "\n",
    "v": "\v",
    "f": "\f",
    "r": "\r",
    "e": "\x1b",
    " ": " ",
    '"': '"',
    "/": "/",
    "\\": "\\",
    "N": "\x85",
    "_": "\xa0",
    "L": "\u2028",
    "P": "\u2029",
}
#: The escapes that name a code point in hexadecimal, by how many digits follow.
HEX_ESCAPES = {"x": 2, "u": 4, "U": 8}
HEX_DIGITS = frozenset("0123456789abcdefABCDEF")
#: The largest code point, past which a `\U` escape names no character.
MAX_CODE_POINT = 0x10FFFF
#: A block scalar's header, matched whole (§ 8.1.1): `|` for a literal block or
#: `>` for a folded one, then an indentation indicator and a chomping indicator
#: in either order, each optional, then an optional comment. `width` or `late`
#: is the indentation indicator, whichever order it was written in. The one
#: spelling: `docket.model` declines an item field holding one through it, and
#: `tools/doc_check.py` reads a workflow's `run:` header through it, where it
#: spelt the same grammar beside this one (`PL-8MHZ`).
BLOCK_SCALAR_RE = re.compile(
    r"(?P<style>[|>])(?:(?P<width>[1-9])?[-+]?|[-+](?P<late>[1-9]))(?:[ \t]+#.*)?"
)


class Unread(ValueError):
    """A front matter this reader cannot split into its keys, the line named in the message.

    `key` is the top-level key whose value holds that line, where one does.
    """

    key: str | None = None


class Misindented(Unread):
    """A line of a value at an indentation YAML refuses for it (§ 8.2), `line` its index.

    Raised apart from its parent so that a reader of one key, such as
    `rules_paths_check` reading `paths:`, can say how to indent its own list.
    """

    def __init__(self, message: str, line: int) -> None:
        super().__init__(message)
        self.line = line


@dataclass(frozen=True)
class Key:
    """One top-level key: its name, what follows its `:`, and the lines its value takes.

    `line` is the index of the key's own line in the block and `end` the index
    past the last line of its value. Every indented line under the key is its
    value's, a `#`-led one included, since a quoted or block scalar holds a `#`
    as content, and so is a first-column line inside a quoted scalar or a flow
    collection the value opens; blank lines and first-column comments after it
    are no part of it. `inline` is the rest of the key's line after the `:`, as
    written, comment and all.
    """

    name: str
    inline: str
    line: int
    end: int


@dataclass(frozen=True)
class Quoted:
    """One quoted scalar a value holds: its quote, and where it opens and closes.

    `line` and `column` place its opening quote in the block, and `end_line`
    and `end_column` its closing one, so a double-quoted scalar's escapes
    (§ 7.3.1) can be read between them and nowhere else (`PL-S4JL`).
    """

    quote: str
    line: int
    column: int
    end_line: int
    end_column: int


def opens(lines: Sequence[str]) -> bool:
    """Whether `lines` open with a front matter's `---`."""
    return bool(lines) and lines[0].strip() == FENCE


def closing(lines: Sequence[str]) -> int | None:
    """The index of the `---` closing the front matter `lines` open, or `None`.

    `None` both where `lines` open none and where nothing closes the one they
    open, which `opens` tells apart for a caller that reports the second. It
    closes on a line that is `---` from its first column, white space after it
    allowed: an indented one is a line of the value above it, which YAML carries
    a block scalar on past, and read as the close it cut the block short
    (`PL-R417`). A first-column `---` closes it wherever it falls, since YAML
    1.2.2 lets no scalar hold one (§ 9.1.2).
    """
    if not opens(lines):
        return None
    for index in range(1, len(lines)):
        if lines[index].rstrip() == FENCE:
            return index
    return None


def body_lines(lines: Sequence[str]) -> list[str]:
    """`lines` with a closed front matter blanked, both its `---` lines included.

    What a reader of a document's Markdown reads, every line in its place. A
    front matter is no Markdown: read as Markdown, a fence-shaped line in a
    block scalar opened a fence that ran on into the body and hid its prose
    (`PL-WX79`), and its keys were one paragraph that its closing `---`
    underlined as a heading (`PL-2MLT`). `tools/doc_check.py`,
    `docket.instructions` and `docket.notes` each blanked it inline before
    this (`PL-NNVJ`).
    """
    fence = closing(lines)
    return list(lines) if fence is None else [""] * (fence + 1) + list(lines[fence + 1 :])


@dataclass
class _Passed:
    """What a reading of a block passes on the way to each key's end."""

    #: Each quoted scalar a value holds, which `quoted` hands back.
    quotes: list[Quoted] = field(default_factory=list)
    #: Each comment, as its line and its `#`'s column, which `comments` hands back.
    comments: list[tuple[int, int]] = field(default_factory=list)


def keys(block: Sequence[str]) -> tuple[Key, ...]:
    """Each top-level key of `block`, a front matter's lines between its fences, in order.

    A key written twice comes back twice, since which one counts is its
    reader's to decide, or to refuse. Raises `Unread` naming a first-column
    line that opens no key, an indented line above the first key, a quoted
    scalar or flow collection that nothing in the block closes, and any other
    line YAML refuses in the forms this reads (`PL-P6LL`). The refusal's `key`
    names the key whose value holds the line, and a `Misindented` one gives the
    line's index too.
    """
    return _keys(block, _Passed())


def quoted(block: Sequence[str]) -> tuple[Quoted, ...]:
    """Each quoted scalar the values of `block`'s top-level keys hold, in order.

    Found where `keys` follows each one to its close, so a quote opening a
    block scalar's line or a plain scalar's continuation line, which is text
    (§ 8.1.1, § 7.3.3), opens none (`PL-S4JL`). A quoted key closes on its own
    line, as an implicit key must (§ 8.2.2), and is not one of them. Raises
    `Unread` where `keys` does.
    """
    passed = _Passed()
    _keys(block, passed)
    return tuple(passed.quotes)


def comments(block: Sequence[str]) -> tuple[tuple[int, int], ...]:
    """Where each comment in `block` opens, as its line's index and its `#`'s column, in order.

    A comment opens at a `#` that opens its line or follows white space,
    outside every scalar (§ 6.6), so the walk `keys` takes finds each one: a
    quoted scalar's lines and a block scalar's content hold a `#` as text,
    which a reading a physical line at a time took for a comment (§ 7.3,
    `block_content`, `PL-W9VC`), and a flow collection holds one wherever white
    space comes before it (§ 7.4). A line YAML refuses, deeper than the node
    holding a block scalar and short of its content, is passed over as `keys`
    passes it. Raises `Unread` where `keys` does.
    """
    passed = _Passed()
    _keys(block, passed)
    return tuple(sorted(set(passed.comments)))


def block_content(
    block: Sequence[str], line: int, holder: int, header: str
) -> tuple[int, int] | None:
    """Where the content of the block scalar `header` opens on `block[line]` sits, and its end.

    `holder` is the column of the node holding the scalar - the key whose
    value it is, or the list entry's `-` - which its content sits past: by the
    header's indentation indicator, or, without one, as deep as the first line
    holding anything other than spaces, as PyYAML 6.0's
    `scan_block_scalar_indentation` reads it, a line of spaces before it as
    deep as its spaces (§ 8.1.1.1). The content runs to the first line holding
    anything short of that indentation, a `#` included, since a comment less
    indented than the content ends it and every comment after that is one at
    any depth (§ 8.1.1.2, `l-trail-comments`). The end is that line's index,
    or the block's length. `None` where `header`, a node as `_node` reads it,
    is none YAML reads (`docket.model.BLOCK_SCALAR_RE`).
    """
    form = BLOCK_SCALAR_RE.fullmatch(header)
    if form is None:
        return None
    width = form["width"] or form["late"]
    if width:
        indent = holder + int(width)
    else:
        indent = holder + 1
        for text in block[line + 1 :]:
            spaces = len(text) - len(text.lstrip(" "))
            indent = max(indent, spaces)
            if spaces < len(text):
                break
    end = line + 1
    while end < len(block) and not block[end][:indent].strip(" "):
        end += 1
    return indent, end


def _keys(block: Sequence[str], passed: _Passed) -> tuple[Key, ...]:
    """`keys`, adding each quoted scalar a value holds and each comment to `passed` on the way."""
    found: list[Key] = []
    index = 0
    while index < len(block):
        text = block[index].strip()
        if not text or text.startswith("#"):
            if text:
                passed.comments.append((index, block[index].index("#")))
            index += 1
            continue
        if block[index][:1] in (" ", "\t"):
            raise Unread(f"`{text}` is indented above the first key, so no value holds it")
        opened = key(block[index])
        if opened is None:
            raise Unread(f"`{text}` sits at the first column and opens no key")
        name, at = opened
        try:
            end = _value_end(block, index, at, passed)
        except Unread as refused:
            refused.key = name
            raise
        found.append(Key(name, block[index][at:], index, end))
        index = end
    return tuple(found)


def statements(block: Sequence[str]) -> tuple[list[tuple[int, int]], Unread | None]:
    """Each statement of `block`, a front matter's lines between its fences, and its decline.

    A key's value is one, ending where `keys` ends it, so what one key leaves
    open - a backtick, a quotation - pairs with nothing in the next, and a date
    in one dates no other (`PL-2MLT`, `PL-WX79`). Every other line is one
    alone: a comment between keys, and each line of a block `keys` cannot split,
    so that none of their text is read with another's, and a record wrapped
    across two of them is read from its first line until the block is mended.
    Each is the index of its first line and one past its last, in order.

    The `Unread` naming why a block was read a line at a time comes back
    second, and `None` where `keys` split it. The fallback was silent, so a
    caller could not tell the two readings apart (`PL-JTP1`).
    `key_statements` is the same reading without that fallback, for a reader
    that names a block it cannot split rather than reading around it
    (`PL-J8ML`).
    """
    try:
        return key_statements(block), None
    except Unread as refusal:
        alone = [(index, index + 1) for index, line in enumerate(block) if line.strip()]
        return alone, refusal


def key_statements(block: Sequence[str]) -> list[tuple[int, int]]:
    """`statements` of a block `keys` can split: each key's value, and each comment between keys.

    Raises `Unread` where `keys` does.
    """
    spans = [(key.line, key.end) for key in keys(block)]
    held = {index for first, end in spans for index in range(first, end)}
    alone = [(index, index + 1) for index, line in enumerate(block) if line.strip()]
    return sorted(spans + [span for span in alone if span[0] not in held])


def _value_end(block: Sequence[str], index: int, at: int, passed: _Passed) -> int:
    """The index past the last line of the value of the key `block[index]` opens at column 0.

    The value is every line indented under the key, and every `- ` item at its
    column where the key holds nothing on its own line. Its lines are read for
    where a node opens - after a `- ` or a nested key's `:`, or alone on the
    line under a key or entry holding nothing - so a quoted scalar or a flow
    collection opening there is followed to its close, a first-column line
    included. A block scalar's lines and a plain scalar's continuation lines,
    indented past the entry that opens it (§ 8.1.1, § 7.3.3), are text, and
    are read for nothing but a comment: none in a block scalar's content
    (`block_content`), and one at a `#` after white space in a plain scalar's
    line, which no plain scalar holds (§ 7.3.3). Each comment the value holds
    is added to `passed`.

    Each line's indentation is held to the block collections open above it
    (§ 8.2): an entry sits at its collection's column, and a line deeper than
    every open collection must open the node of an entry holding nothing on its
    line. A plain scalar's continuation line holds no `: `, and none follows a
    comment, which ends the scalar (§ 7.3.3). `Unread` names a line breaking
    either, and a node `_refusal` refuses, since YAML refuses the block
    (`PL-P6LL`).
    """
    _refuse(block[index], at, after_key=True)
    node = _node(block[index], at)
    bare = not node
    # Lines indented past `literal` are a scalar's text; None while none is open.
    literal = None if bare or node[0] in CLOSED_NODES else 0
    # The index past a block scalar's content while one is open, and 0 while a
    # plain scalar is, whose lines may hold a comment.
    content = _block_end(block, index, 0, node)
    # Whether a comment has ended the plain scalar open past `literal`.
    ended = literal is not None and not content and _commented(block[index], at)
    # The column of the entry holding nothing on its line, whose node opens below it.
    holder = 0
    # That column while the next line may still open the node, and None once it has.
    slot: int | None = 0 if bare else None
    # Whether that entry's line holds an anchor or a tag, which its node takes.
    propped = bare and _properties(block[index], at)
    # Each block collection open, as its column and whether it is a sequence.
    levels = [(0, False)]
    line = _past(block, index, at, 0, passed)
    last = line - 1
    while line < len(block):
        text = block[line]
        stripped = text.strip()
        indent = len(text) - len(text.lstrip(" \t"))
        if not stripped or (indent == 0 and stripped.startswith("#")):
            if stripped:
                passed.comments.append((line, 0))
                ended = True
            line += 1
            continue
        if indent == 0 and not (bare and is_item(text)):
            break
        last = line
        line += 1
        if literal is not None and indent > literal:
            opens = None
            if last >= content and (not content or stripped.startswith("#")):
                opens = next((at for at in range(indent, len(text)) if _comment_at(text, at)), None)
                if opens is not None:
                    passed.comments.append((last, opens))
            if not content:
                _carry_plain(text, indent, opens, ended)
                ended = ended or opens is not None
            continue
        if stripped.startswith("#"):
            passed.comments.append((last, indent))
            continue
        literal = None
        ended = False
        while levels[-1][0] > indent:
            levels.pop()
        column, sequence = levels[-1]
        item = is_item(text[indent:])
        if column == indent and sequence and not item and levels[-2:-1] == [(indent, False)]:
            levels.pop()
            sequence = False
        if column == indent:
            if item and not sequence:
                if slot != indent:
                    raise Misindented(
                        f"`{stripped}` opens a list entry at a mapping's column", last
                    )
                levels.append((indent, True))
            elif sequence and not item:
                raise Misindented(
                    f"`{stripped}` sits at a list's column and is no entry of it", last
                )
        elif slot is None or indent <= slot:
            raise Misindented(
                f"`{stripped}` is indented as no entry above it is, under a node that already "
                "holds its value",
                last,
            )
        elif item:
            levels.append((indent, True))
        entry, position = holder if slot is None else slot, indent
        while is_item(text[position:]):
            entry = position
            if levels[-1] != (position, True):
                levels.append((position, True))
            position = _skip_blanks(text, position + 1)
        start = _node_start(text, position)
        nested = _key_span(text[start:])
        if (
            text[position : position + 1] in ("?", ":")
            and text[position + 1 : position + 2] in BLANKS
        ):
            # An explicit key or its value (§ 8.2.2), whose node follows the indicator.
            nested = ("", position + 1 - start)
        if nested is not None:
            if levels[-1] != (position, False):
                levels.append((position, False))
            entry = position
            position = _skip_blanks(text, start + nested[1])
        elif column == indent and not item:
            raise Misindented(f"`{stripped}` sits at a mapping's column and opens no key", last)
        elif propped and not item and start > position and _node(text, position):
            raise Unread(f"`{stripped}` gives a node a second anchor or tag")
        _refuse(text, position, after_key=nested is not None)
        slot, propped = None, False
        opened = _node(text, position)
        if opened[:1] in CLOSED_NODES:
            last = _past(block, last, position, entry, passed) - 1
            line = last + 1
            continue
        _past(block, last, position, entry, passed)
        if opened:
            literal = entry
            content = _block_end(block, last, entry, opened)
            ended = not content and _commented(text, position)
        else:
            holder = slot = entry
            propped = _properties(text, position)
    return last + 1


def _properties(text: str, at: int) -> bool:
    """Whether an anchor or a tag stands before the node opening at `text[at:]` (§ 6.9)."""
    return _node_start(text, at) > _skip_blanks(text, at)


def _commented(text: str, at: int) -> bool:
    """Whether the line `text` ends in a comment past the node opening at `text[at:]`."""
    rest = text[at:]
    return uncommented(rest).rstrip() != rest.rstrip()


#: A `:` that white space or the line's end follows, which no plain scalar holds (§ 7.3.3).
_MAPPING_INDICATOR = re.compile(r":(?:[ \t]|$)")


def _carry_plain(text: str, indent: int, opens: int | None, ended: bool) -> None:
    """Refuse the plain scalar's continuation line `text` where YAML does (§ 7.3.3).

    `opens` is where a comment opens on it, and `ended` whether a comment has
    ended the scalar already. A line opening with `#` is a comment and is not
    refused.
    """
    if opens == indent:
        return
    words = text[indent:opens].rstrip()
    if ended:
        raise Unread(f"`{words}` carries on a plain scalar past the comment that ended it")
    if _MAPPING_INDICATOR.search(words):
        raise Unread(
            f"`{words}` carries on a plain scalar with a `: `, which no plain scalar holds"
        )


def _refusal(text: str, at: int, after_key: bool) -> str | None:
    """Why YAML refuses the node opening at `text[at:]`, or `None` where it does not.

    An anchor or a tag never names an alias (§ 7.1), and `,`, `]`, `}`, `%`,
    `@` and a backtick open no node in a block (§ 5.3). After a key's `:` on
    the key's own line, a node opens no block collection: no `- ` entry, no
    `? ` or `: ` explicit entry, and no plain scalar holding a `: ` (§ 8.2.2).
    """
    start = _node_start(text, at)
    node = uncommented(text[start:]).strip()
    if not node:
        return None
    if node[0] == "*" and start > _skip_blanks(text, at):
        return "gives an alias an anchor or a tag"
    if node[0] in ",]}%@`":
        return f"opens with `{node[0]}`, which opens no node here"
    if after_key and (is_item(node) or (node[0] in "?:" and node[1:2] in BLANKS)):
        return "opens a block collection on its key's line"
    if after_key and plain(node) and _MAPPING_INDICATOR.search(node):
        return "holds a second key on its key's line"
    return None


def _refuse(text: str, at: int, after_key: bool) -> None:
    """Raise `Unread` naming `text` where `_refusal` refuses its node at `at`."""
    reason = _refusal(text, at, after_key)
    if reason is not None:
        raise Unread(f"`{text.strip()}` {reason}")


def _block_end(block: Sequence[str], line: int, holder: int, node: str) -> int:
    """The index past a block scalar's content where `node`, on `block[line]`, is its header.

    0 where `node` opens none. Raises `Unread` where it is a header YAML
    refuses, such as `|x` or `>#x`, and where a line of spaces before the
    content is deeper than the content's first line (§ 8.1.1.1) or a tab
    stands in the content's indentation (§ 6.1), since YAML refuses each
    (`PL-P6LL`).
    """
    if node[:1] not in ("|", ">"):
        return 0
    content = block_content(block, line, holder, node)
    if content is None:
        raise Unread(f"`{block[line].strip()}` opens a block scalar with a header YAML refuses")
    indent, end = content
    after = block[end] if end < len(block) else ""
    spaces = len(after) - len(after.lstrip(" "))
    if not after.strip() and "\t" in after:
        raise Unread(f"`{block[line].strip()}` is followed by a tab where its content is indented")
    leading = [len(text) for text in block[line + 1 : end] if not text.strip(" ")]
    if all(not text.strip(" ") for text in block[line + 1 : end]) and holder < spaces < max(
        leading, default=0
    ):
        raise Unread(
            f"`{after.strip()}` is shallower than a line of spaces that opens the block "
            "scalar above it"
        )
    if after.strip() and holder < spaces < indent and not after.lstrip().startswith("#"):
        raise Unread(f"`{after.strip()}` stands deeper than its key and short of its block scalar")
    return end


def _skip_blanks(text: str, position: int) -> int:
    """Past the spaces and tabs at `position`."""
    while position < len(text) and text[position] in " \t":
        position += 1
    return position


def _node_start(text: str, at: int) -> int:
    """Where the node opening at `text[at:]` starts, past white space, anchors and tags (§ 6.9)."""
    while True:
        at = _skip_blanks(text, at)
        if text[at : at + 1] not in ("&", "!"):
            return at
        while at < len(text) and text[at] not in " \t":
            at += 1


def _node(text: str, at: int) -> str:
    """The node at `text[at:]`, past anchors and tags, without its comment or white space."""
    return uncommented(text[_node_start(text, at) :]).strip()


def is_item(text: str) -> bool:
    """Whether `text`, a line or what follows its indent, opens a block list entry (§ 8.2.1)."""
    return text == "-" or text[:2] in ("- ", "-\t")


def closing_quote(text: str, start: int = 0) -> int:
    """Where the quote closing the scalar `text[start]` opens sits on its line, or -1.

    A backslash escapes the character after it in a double-quoted scalar
    (§ 7.3.1), and `''` is one quote in a single-quoted one (§ 7.3.2).
    """
    return _scan_quote(text, start + 1, text[start])


def uncommented(text: str) -> str:
    """`text`, a line or a node as a line holds it, without its comment (§ 6.6).

    A comment opens at a `#` that opens the text or follows white space, and
    never inside a quoted scalar. A quote opens one only where a node can open
    (§ 7.3): where the text opens; after a list entry's `-` or an explicit key's
    `?` and the white space after it; after a key's `:` and the white space
    after it; after an anchor or a tag (§ 6.9); and inside a flow collection
    where `_flow_node` says (§ 7.4). Anywhere else it is a plain scalar's
    character. So `"/src/**" # why` is the glob `"/src/**"`, `"a # b"` and
    `[a, "b # c"]` are all node, and `don 't # x` is the plain scalar `don 't`
    - the third lost its tail here when only a quote opening the text was
    followed, and the fourth kept its comment in `required_checks_check`, which
    took any quote after white space for one (`PL-8MHZ`). A quoted scalar its
    line does not close leaves the line as it is, since what follows is the
    scalar's.
    """
    # Whether a node can open here, whether a quoted scalar or a collection
    # closed just before it, and how many flow collections are open.
    node, closed, depth = True, False, 0
    index = 0
    while index < len(text):
        char = text[index]
        if _comment_at(text, index):
            return text[:index]
        if node and char in ("'", '"'):
            end = closing_quote(text, index)
            if end < 0:
                return text
            index, node, closed = end + 1, False, True
            continue
        if node and char in "&!":
            while index < len(text) and text[index] not in " \t":
                index += 1
            continue
        indicator = text[index + 1 : index + 2] in BLANKS
        if depth:
            depth += (char in "[{") - (char in "]}")
            node = _flow_node(text, index, node, closed)
            closed = char in "]}" or (closed and char in " \t")
        elif node and char in "[{":
            depth, closed = 1, False
        elif (char == ":" or (node and char in "-?")) and indicator:
            node = True
        else:
            node = node and char in " \t"
        index += 1
    return text


def plain(text: str) -> bool:
    """Whether the node `text` opens with, from its first character, is a plain scalar (§ 7.3.3).

    Every indicator (§ 5.3) opens some other node, or none, except `-`, `?` and
    `:` with something other than white space after them, which open a plain
    scalar such as `-x`. So `|x` is no plain scalar but a block scalar's header
    YAML refuses, which `doc_check` handed bash as the command `|x` while
    `required_checks_check` refused it (`PL-8MHZ`).
    """
    return bool(text) and (
        text[0] not in INDICATORS or (text[0] in "-?:" and text[1:2] not in BLANKS)
    )


def unquote(token: str) -> str:
    """What the quoted scalar `token`, written whole on one line, holds (§ 7.3.1, § 7.3.2).

    `token` carries its quotes. `''` is one quote in a single-quoted scalar, and
    a backslash opens an escape in a double-quoted one, read as § 5.7 defines
    it (`ESCAPES`, `HEX_ESCAPES`), so `'it''s'` holds `it's` and `"a\\"b"`
    holds `a"b`. `rules_paths_check` kept both quotes of the first and the
    backslash of the second, and `required_checks_check` refused every escape
    (`PL-8MHZ`). Raises `Unread` naming an escape § 5.7 does not define, which
    YAML refuses, and a `token` its last character does not close.

    Not the item front matter's reading, which is not YAML: `docket.model`
    reads two escapes there and keeps every other backslash as written.
    """
    if token[:1] not in ("'", '"') or closing_quote(token) != len(token) - 1:
        raise Unread(f"`{token}` is not one quoted scalar that its last character closes")
    body = token[1:-1]
    if token[0] == "'":
        return body.replace("''", "'")
    out: list[str] = []
    index = 0
    while index < len(body):
        if body[index] != "\\":
            out.append(body[index])
            index += 1
            continue
        code = body[index + 1 : index + 2]
        if code in ESCAPES:
            out.append(ESCAPES[code])
            index += 2
            continue
        width = HEX_ESCAPES.get(code, 0)
        digits = body[index + 2 : index + 2 + width]
        if width and len(digits) == width and all(digit in HEX_DIGITS for digit in digits):
            point = int(digits, 16)
            if point <= MAX_CODE_POINT:
                out.append(chr(point))
                index += 2 + width
                continue
        raise Unread(
            f"`{token}` holds `\\{code}{digits}`, which is no escape YAML 1.2.2 § 5.7 defines"
        )
    return "".join(out)


def _comment_at(text: str, index: int) -> bool:
    """Whether a comment opens at `text[index]`: a `#` opening it or after white space (§ 6.6)."""
    return text[index] == "#" and (index == 0 or text[index - 1] in " \t")


def _flow_node(text: str, position: int, node: bool, closed: bool) -> bool:
    """Whether a node can open past `text[position]`, inside a flow collection (§ 7.4).

    `node` is whether one could at it, and `closed` whether a quoted scalar or
    a collection closed before it with only white space between. One can after
    a bracket opening a collection or a `,`, and after a `:` that white space, a
    flow indicator or the line's end follows, or that follows such a close, as
    JSON writes a key (§ 7.4.2): PyYAML reads `{a:b}` as the one key `a:b`, and
    `{"a":"b"}` as `a` holding `b`. White space keeps what came before, and any
    other character is a plain scalar's.
    """
    char = text[position]
    if char in "[{,":
        return True
    if char == ":":
        return closed or text[position + 1 : position + 2] in (*BLANKS, *"[]{},")
    return node and char in " \t"


def _scan_quote(text: str, position: int, quote: str) -> int:
    """The index of the first `quote` at or after `position` that closes a scalar, or -1."""
    while position < len(text):
        char = text[position]
        if quote == '"' and char == "\\":
            position += 2
            continue
        if char == quote:
            if quote == "'" and text[position + 1 : position + 2] == "'":
                position += 2
                continue
            return position
        position += 1
    return -1


def _quote_end(
    block: Sequence[str], line: int, position: int, holder: int, quotes: list[Quoted]
) -> tuple[int, int]:
    """The line and column of the quote closing the scalar `block[line][position]` opens.

    The scalar is added to `quotes`. Each later line is held to `_carried`
    under `holder`, the column of the entry whose node it is.
    """
    first, quote = line, block[line][position]
    found = _scan_quote(block[line], position + 1, quote)
    while found < 0:
        line += 1
        if line == len(block):
            raise Unread(
                f"`{block[first].strip()}` opens a quoted scalar that nothing in the front "
                "matter closes"
            )
        _carried(block[line], holder)
        found = _scan_quote(block[line], 0, quote)
    quotes.append(Quoted(quote, first, position, line, found))
    return line, found


def _carried(text: str, holder: int) -> None:
    """Refuse `text`, a later line of a quoted scalar or a flow collection, short of its node.

    Its spaces must reach past `holder`, the column of the entry whose node it
    is, as YAML 1.2.2's flow line prefix asks (§ 6.3, § 8.2.2), and a tab is no
    indentation (§ 6.1). A line of white space alone is an empty line, which
    may stand shallower (§ 6.5). PyYAML 6.0 reads such a line at the first
    column as the node's, where a conformant reader refuses the block
    (`PL-P6LL`).
    """
    if text.strip() and len(text) - len(text.lstrip(" ")) <= holder:
        raise Unread(
            f"`{text.strip()}` carries a quoted scalar or a flow collection on at or before the "
            "column of the key or `- ` holding it, which YAML refuses; indent it past that column"
        )


def key(line: str) -> tuple[str, int] | None:
    """The key `line` opens at its first column, and the index past its `:`.

    A plain or quoted scalar ended by a `:` that white space or the line's end
    follows (§ 7.3, § 8.2.2), a quoted one read as `unquote` reads it, so `on :`
    and `"on":` name the key `on` and `"a\\"b":` the key `a"b`, where this
    reader named it `a\\"b` (`PL-8MHZ`). `None` where `line` opens none: a
    comment, a node other than a plain or quoted scalar (`plain`), or text no
    such `:` ends. Raises `Unread` where `unquote` does.
    """
    span = _key_span(line)
    if span is None:
        return None
    name, colon = span
    return (unquote(name) if name[:1] in ("'", '"') else name), colon


def _key_span(line: str) -> tuple[str, int] | None:
    """`key`, with a quoted key as written, its quotes kept, so that nothing is unquoted.

    For reading inside a value, where what a key holds is its reader's to
    decide and a key YAML refuses is passed over like the rest of the value.
    """
    if line[:1] in ("'", '"'):
        end = closing_quote(line)
        colon = end + 1
        while 0 < colon < len(line) and line[colon] in " \t":
            colon += 1
        if end < 0 or line[colon : colon + 1] != ":" or line[colon + 1 : colon + 2] not in BLANKS:
            return None
        return line[: end + 1], colon + 1
    if not plain(line):
        return None
    for index, char in enumerate(line):
        if _comment_at(line, index):
            return None
        if char == ":" and line[index + 1 : index + 2] in BLANKS:
            return line[:index].rstrip(), index + 1
    return None


def _past(block: Sequence[str], index: int, at: int, holder: int, passed: _Passed) -> int:
    """The index past the line on which the node opening at `block[index][at:]` ends.

    The next line, unless the node is a quoted scalar or a flow collection that
    line does not close, which is followed to its close across the lines below.
    An anchor or a tag before the node names it and changes nothing in it
    (§ 6.9). Each quoted scalar followed is added to `passed`, and so is the
    comment on the line the node ends on, past its end. `holder` is the column
    of the entry whose node it is, which each later line of one followed is
    indented past (`_carried`). Raises `Unread` where anything but a comment
    after white space follows the close, which YAML refuses (§ 6.6).
    """
    text = block[index]
    at = _node_start(text, at)
    if text[at : at + 1] in ("'", '"'):
        index, close = _quote_end(block, index, at, holder, passed.quotes)
    elif text[at : at + 1] in ("[", "{"):
        index, close = _flow_end(block, index, at, holder, passed)
    else:
        close = at - 1
    rest = block[index][close + 1 :]
    if close >= at and rest.strip() and not (rest[:1] in BLANKS and rest.lstrip()[:1] == "#"):
        raise Unread(
            f"`{block[index].strip()}` holds `{rest.strip()}` after its closing quote or bracket, "
            "which YAML refuses"
        )
    kept = uncommented(rest)
    if len(kept) < len(rest):
        passed.comments.append((index, close + 1 + len(kept)))
    return index + 1


def _flow_end(
    block: Sequence[str], index: int, at: int, holder: int, passed: _Passed
) -> tuple[int, int]:
    """The line and column of the bracket closing the flow collection `block[index][at]` opens.

    A quote inside it opens a quoted scalar only where a node can open, as
    `_flow_node` says, so the `'` in `[don't]` is a character, and a `#` after
    white space comments out the rest of its line, which is added to `passed`
    (§ 7.4). A line break is white space. Each later line but a comment is
    held to `_carried` under `holder`. Raises `Unread` where a node follows a
    closed one, or a plain scalar a comment ended, with no `,` between, which
    YAML refuses (§ 7.4).
    """
    depth = 0
    node, closed = True, False
    # Whether a comment ended a plain scalar, which nothing but an indicator may follow.
    ended = False
    line, position = index, at
    while line < len(block):
        text = block[line]
        if line > index and not text.lstrip(" \t").startswith("#"):
            _carried(text, holder)
        while position < len(text):
            char = text[position]
            if _comment_at(text, position):
                passed.comments.append((line, position))
                ended = ended or not (node or closed)
                break
            if (closed or ended) and char not in " \t,]}:":
                raise Unread(
                    f"`{text.strip()}` holds a node that no `,` parts from the one before it"
                )
            ended = ended and char in " \t"
            if char in ("'", '"') and node:
                line, position = _quote_end(block, line, position, holder, passed.quotes)
                text = block[line]
                node, closed = False, True
            else:
                depth += (char in "[{") - (char in "]}")
                if depth == 0:
                    return line, position
                node = _flow_node(text, position, node, closed)
                closed = char in "]}" or (closed and char in " \t")
            position += 1
        line, position = line + 1, 0
    raise Unread(
        f"`{block[index].strip()}` opens a flow collection that nothing in the front matter closes"
    )
