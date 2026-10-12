"""Where a Markdown file's YAML front matter ends, and where each key in it does.

The front matter Claude Code reads on a rule or a skill: a first line of `---`,
then YAML, then a closing `---`. This is the one reading of it (`PL-R417`):
`tools/rules_paths_check.py` reads a rule's `paths:` through it,
`tools/doc_check.py` whether a rule declares one and each key's value as a
statement of its own, `docket.instructions` each key's dated sentences,
`docket.notes` where a notes file's Markdown begins, and
`tools/fixture_id_check.py` which quoted scalar a line break is escaped in,
and `tools/required_checks_check.py` and `tools/doc_check.py` a workflow's
lines, keys and quoted scalars, and which node a value opens (`PL-8MHZ`).
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
quoted scalar or a flow collection runs to its close however the lines below it
are indented: PyYAML 6.0 reads a continuation at the first column that way where
a strict YAML 1.2.2 reader refuses the file (§ 6.3), and either way the key such
a line looks like is no key. That holds wherever one opens, on the key's own
line or below it - alone on the line under a key or list entry holding nothing,
after a list entry's `- `, or after a nested key's `:` (§ 8.2.1, § 8.2.2). Below
the key's line it was once followed by indentation alone, so a first-column
line inside it read as a key (`PL-YQ9G`). A block scalar's lines and a plain
scalar's continuation lines are text, so a quote opening one of them opens
nothing; `quoted` hands back the quoted scalars this reading does follow, each
where it opens and closes (`PL-S4JL`). Nothing inside a value is checked, so a
value YAML refuses can still be passed over here: what a value holds is its
reader's to decide, and `rules_paths_check.entries` decides `paths:`'s. A line
at the first column that opens no key raises `Unread` naming it, as does an
indented line above the first key, since no value holds either and a reader
passing over one would hand on the key above it short. Where each value ends,
and where each quoted scalar opens and closes, is held to PyYAML's reading over
a generated corpus by `subprojects/docket/tests/test_frontmatter_reference.py`.

**A line's own grammar is read here too, once** (`PL-8MHZ`): where its comment
opens (`uncommented`), the key it opens (`key`), what a quoted scalar holds
(`unquote`) and whether a node is a plain scalar (`plain`). The checks that read
a workflow or a rule each spelt them beside this module, and parted on the
first input one had not been written for: `[a, "b # c"]` lost its scalar's tail
here, `don 't # x` kept its comment in `required_checks_check`, `"a\\"b":`
named a key with its backslash here, and `'it''s'` kept both quotes in
`rules_paths_check`.

Not docket's own item front matter, which is not YAML: its grammar is
`docket.model`'s. Standard library only, as the rest of the package is.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

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


class Unread(ValueError):
    """A front matter this reader cannot split into its keys, the line named in the message."""


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


def keys(block: Sequence[str]) -> tuple[Key, ...]:
    """Each top-level key of `block`, a front matter's lines between its fences, in order.

    A key written twice comes back twice, since which one counts is its
    reader's to decide, or to refuse. Raises `Unread` naming a first-column
    line that opens no key, an indented line above the first key, and a quoted
    scalar or flow collection that nothing in the block closes.
    """
    return _keys(block, [])


def quoted(block: Sequence[str]) -> tuple[Quoted, ...]:
    """Each quoted scalar the values of `block`'s top-level keys hold, in order.

    Found where `keys` follows each one to its close, so a quote opening a
    block scalar's line or a plain scalar's continuation line, which is text
    (§ 8.1.1, § 7.3.3), opens none (`PL-S4JL`). A quoted key closes on its own
    line, as an implicit key must (§ 8.2.2), and is not one of them. Raises
    `Unread` where `keys` does.
    """
    quotes: list[Quoted] = []
    _keys(block, quotes)
    return tuple(quotes)


def _keys(block: Sequence[str], quotes: list[Quoted]) -> tuple[Key, ...]:
    """`keys`, adding each quoted scalar a value holds to `quotes` on the way."""
    found: list[Key] = []
    index = 0
    while index < len(block):
        text = block[index].strip()
        if not text or text.startswith("#"):
            index += 1
            continue
        if block[index][:1] in (" ", "\t"):
            raise Unread(f"`{text}` is indented above the first key, so no value holds it")
        opened = key(block[index])
        if opened is None:
            raise Unread(f"`{text}` sits at the first column and opens no key")
        name, at = opened
        end = _value_end(block, index, at, quotes)
        found.append(Key(name, block[index][at:], index, end))
        index = end
    return tuple(found)


def statements(block: Sequence[str]) -> list[tuple[int, int]]:
    """Each statement of `block`, a front matter's lines between its fences, in order.

    A key's value is one, ending where `keys` ends it, so what one key leaves
    open - a backtick, a quotation - pairs with nothing in the next, and a date
    in one dates no other (`PL-2MLT`, `PL-WX79`). Every other line is one
    alone: a comment between keys, and each line of a block `keys` cannot split,
    so that none of their text is read with another's, and a record wrapped
    across two of them is read from its first line until the block is mended.
    Each is the index of its first line and one past its last.

    `key_statements` is the same reading without that fallback, for a reader
    that names a block it cannot split rather than reading around it
    (`PL-J8ML`).
    """
    try:
        return key_statements(block)
    except Unread:
        return [(index, index + 1) for index, line in enumerate(block) if line.strip()]


def key_statements(block: Sequence[str]) -> list[tuple[int, int]]:
    """`statements` of a block `keys` can split: each key's value, and each comment between keys.

    Raises `Unread` where `keys` does.
    """
    spans = [(key.line, key.end) for key in keys(block)]
    held = {index for first, end in spans for index in range(first, end)}
    alone = [(index, index + 1) for index, line in enumerate(block) if line.strip()]
    return sorted(spans + [span for span in alone if span[0] not in held])


def _value_end(block: Sequence[str], index: int, at: int, quotes: list[Quoted]) -> int:
    """The index past the last line of the value of the key `block[index]` opens at column 0.

    The value is every line indented under the key, and every `- ` item at its
    column where the key holds nothing on its own line. Its lines are read for
    where a node opens - after a `- ` or a nested key's `:`, or alone on the
    line under a key or entry holding nothing - so a quoted scalar or a flow
    collection opening there is followed to its close, a first-column line
    included. A block scalar's lines and a plain scalar's continuation lines,
    indented past the entry that opens it (§ 8.1.1, § 7.3.3), are text, and
    are read for nothing.
    """
    node = _node(block[index], at)
    bare = not node
    # Lines indented past `literal` are a scalar's text; None while none is open.
    literal = None if bare or node[0] in CLOSED_NODES else 0
    # The column of the entry holding nothing on its line, whose node opens below it.
    holder = 0
    line = _past(block, index, at, quotes)
    last = line - 1
    while line < len(block):
        text = block[line]
        content = text.strip()
        indent = len(text) - len(text.lstrip(" \t"))
        if not content or (indent == 0 and content.startswith("#")):
            line += 1
            continue
        if indent == 0 and not (bare and is_item(text)):
            break
        last = line
        line += 1
        if content.startswith("#") or (literal is not None and indent > literal):
            continue
        literal = None
        entry, position = holder, indent
        while is_item(text[position:]):
            entry = position
            position = _skip_blanks(text, position + 1)
        nested = _key_span(text[position:])
        if nested is not None:
            entry = position
            position = _skip_blanks(text, position + nested[1])
        opened = _node(text, position)
        if opened[:1] in CLOSED_NODES:
            last = _past(block, last, position, quotes) - 1
            line = last + 1
        elif opened:
            literal = entry
        else:
            holder = entry
    return last + 1


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
    block: Sequence[str], line: int, position: int, quotes: list[Quoted]
) -> tuple[int, int]:
    """The line and column of the quote closing the scalar `block[line][position]` opens.

    The scalar is added to `quotes`.
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
        found = _scan_quote(block[line], 0, quote)
    quotes.append(Quoted(quote, first, position, line, found))
    return line, found


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


def _past(block: Sequence[str], index: int, at: int, quotes: list[Quoted]) -> int:
    """The index past the line on which the node opening at `block[index][at:]` ends.

    The next line, unless the node is a quoted scalar or a flow collection that
    line does not close, which is followed to its close across the lines below.
    An anchor or a tag before the node names it and changes nothing in it
    (§ 6.9). Each quoted scalar followed is added to `quotes`.
    """
    text = block[index]
    at = _node_start(text, at)
    if text[at : at + 1] in ("'", '"'):
        return _quote_end(block, index, at, quotes)[0] + 1
    if text[at : at + 1] in ("[", "{"):
        return _flow_end(block, index, at, quotes) + 1
    return index + 1


def _flow_end(block: Sequence[str], index: int, at: int, quotes: list[Quoted]) -> int:
    """The index of the line closing the flow collection `block[index][at]` opens (§ 7.4).

    A quote inside it opens a quoted scalar only where a node can open, as
    `_flow_node` says, so the `'` in `[don't]` is a character, and a `#` after
    white space comments out the rest of its line. A line break is white space.
    """
    depth = 0
    node, closed = True, False
    line, position = index, at
    while line < len(block):
        text = block[line]
        while position < len(text):
            char = text[position]
            if _comment_at(text, position):
                break
            if char in ("'", '"') and node:
                line, position = _quote_end(block, line, position, quotes)
                text = block[line]
                node, closed = False, True
            else:
                depth += (char in "[{") - (char in "]}")
                if depth == 0:
                    return line
                node = _flow_node(text, position, node, closed)
                closed = char in "]}" or (closed and char in " \t")
            position += 1
        line, position = line + 1, 0
    raise Unread(
        f"`{block[index].strip()}` opens a flow collection that nothing in the front matter closes"
    )
