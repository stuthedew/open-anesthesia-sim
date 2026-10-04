"""Where a Markdown document's blocks are: the one reading every block reader here takes.

A reader that judges prose has to know where each statement of a document
starts and ends, and which lines are a literal it should not judge at all, and
for both it has to know what holds a line: a block quote, a list item, a fence,
a comment. Readers that answered it a physical line at a time met CommonMark's
forms one capture at a time (`PL-R417`): a heading inside a comment opened a
section, a fence behind a block quote's `>` opened none, a list item's second
paragraph belonged to no entry, a table row without its outer pipe ended the
table. So the block structure is read once, here, the way CommonMark 0.31.2's
appendix "A parsing strategy" reads it: each line is matched against the
containers still open, then read for the containers and the leaf block it
opens, and a line that opens nothing carries the open paragraph on - lazily,
where its containers did not match. A table is GitHub Flavored Markdown 0.29's
(§ 4.10), read where cmark-gfm reads one: its header row is a paragraph line,
not a lazy one, under which a delimiter row of as many cells opens the table,
which then runs to a blank line or another block's start.

`read` hands back every leaf block, as its kind, its span of lines and how many
containers hold it, and every list item the same way. `fences`,
`statement_lines`, the heading and table readers below and the list walker in
`roadmap` are views of it, so they cannot disagree about where a block is.
Checked against markdown-it-py 4.2.0 on every tracked Markdown file on
2026-10-04.

Three departures, each deliberate:

- **A fence, or an HTML block of § 4.6's kinds 1 to 5, that nothing closes
  before the document ends is read as written** (`PL-92MY`). CommonMark runs it
  to the end, and every reader here skips a literal, so CommonMark's reading
  would skip the rest of the file silently; read as written, an unclosed block
  costs at worst a loud false error on a literal, repaired by closing it. A
  block its container's end closes is closed. Every fence after an unclosed one
  is read as written too, as `fences` has always read them.
- Tabs are expanded to four-column stops before a line is read, which puts a
  tab after a block quote's `>` a column later than § 2.2's partial tab.
- A link reference definition is read as the paragraph it is written as.

A line is what `str.splitlines()` cuts, and an index is 0-based. Standard
library only, and it imports nothing from docket, so `fences` can stand on it.
"""

from __future__ import annotations

import re
from collections.abc import Collection, Iterator, Sequence
from dataclasses import dataclass
from functools import lru_cache

#: The kinds of leaf block (§ 4).
PARAGRAPH = "paragraph"
HEADING = "heading"
TABLE = "table"
FENCE = "fence"
CODE = "code"
HTML = "html"
BREAK = "break"


@dataclass(frozen=True)
class Block:
    """One leaf block: its kind, its span of lines, and how many containers hold it."""

    kind: str
    #: The index of its first line and one past its last. A setext heading
    #: spans its underline, a closed fence its closing line, and an indented
    #: code block ends at its last line holding anything.
    start: int
    end: int
    #: How many block quotes and list items hold it; 0 at the top level.
    depth: int
    #: A heading's level, 1 to 6; 0 for every other kind.
    level: int = 0


@dataclass(frozen=True)
class Item:
    """One list item (§ 5.2): its span of lines, its depth, and its first lazy line."""

    #: The index of its marker's line, and one past its last line holding anything.
    start: int
    end: int
    #: How many block quotes and list items hold it; 0 for a top-level item.
    depth: int
    #: The first line carrying one of its paragraphs on from the margin - a lazy
    #: continuation line (§ 5.2) with no indent at all - or -1 where none does.
    lazy: int = -1


@dataclass(frozen=True)
class Document:
    """A document's leaf blocks and list items, each in the order it opens."""

    blocks: tuple[Block, ...]
    items: tuple[Item, ...]


@dataclass(frozen=True)
class Heading:
    """A top-level heading: the index of its first line, its level and its text."""

    line: int
    level: int
    title: str


@dataclass(frozen=True)
class Table:
    """A top-level table: its header row's index and cells, and each body row's."""

    line: int
    header: tuple[str, ...]
    rows: tuple[tuple[int, tuple[str, ...]], ...]


# Each pattern is matched where a line's containers end, so its indent is
# counted from there.
_QUOTE = re.compile(r" {0,3}>")
_MARKER = re.compile(r" {0,3}(?:[-+*]|(?P<number>\d{1,9})[.)])(?=[ \t]|$)")
_ATX = re.compile(r" {0,3}(?P<hashes>#{1,6})(?:[ \t]|$)")
_ATX_CLOSE = re.compile(r"(?:^|[ \t]+)#+[ \t]*$")
_BREAK = re.compile(r" {0,3}(?:(?:-[ \t]*){3,}|(?:\*[ \t]*){3,}|(?:_[ \t]*){3,})$")
_SETEXT = re.compile(r" {0,3}(?P<rule>=+|-+)[ \t]*$")
#: A backtick fence's info string holds no backtick (§ 4.5), which is what
#: keeps a code span wrapped to a line's start from opening one.
_FENCE = re.compile(r" {0,3}(?P<fence>`{3,}(?=[^`]*$)|~{3,})")
_FENCE_CLOSE = re.compile(r" {0,3}(?P<fence>`{3,}|~{3,})[ \t]*$")
#: § 4.6's kinds 1 to 5: the line opening each, and the marker ending it, which
#: may sit on the opening line itself, as `<!-- absent: ... -->` does.
_HTML_ENDED = (
    (
        re.compile(r" {0,3}<(?i:pre|script|style|textarea)(?:[ \t>]|$)"),
        re.compile(r"</(?i:pre|script|style|textarea)>"),
    ),
    (re.compile(r" {0,3}<!--"), re.compile(r"-->")),
    (re.compile(r" {0,3}<\?"), re.compile(r"\?>")),
    (re.compile(r" {0,3}<![A-Za-z]"), re.compile(r">")),
    (re.compile(r" {0,3}<!\[CDATA\["), re.compile(r"\]\]>")),
)
#: Kind 6, a block-level tag, which runs to a blank line.
_HTML_BLOCK_TAG = re.compile(
    r" {0,3}</?(?i:address|article|aside|basefont|base|blockquote|body|caption|center"
    r"|colgroup|col|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer"
    r"|form|frameset|frame|h[1-6]|head|header|hr|html|iframe|legend|link|li|main"
    r"|menuitem|menu|nav|noframes|ol|optgroup|option|param|p|search|section|summary"
    r"|table|tbody|td|tfoot|th|thead|title|track|tr|ul)(?:[ \t>]|/>|$)"
)
#: Kind 7, any other complete tag alone on its line, which runs to a blank line
#: and is the one kind that cannot interrupt a paragraph.
_HTML_TAG_LINE = re.compile(
    r" {0,3}(?:<(?!(?i:pre|script|style|textarea)(?![A-Za-z0-9-]))[A-Za-z][A-Za-z0-9-]*"
    r"(?:[ \t]+[A-Za-z_:][A-Za-z0-9_.:-]*"
    r"(?:[ \t]*=[ \t]*(?:[^ \t\"'=<>`]+|'[^']*'|\"[^\"]*\"))?)*"
    r"[ \t]*/?>"
    r"|</(?!(?i:pre|script|style|textarea)(?![A-Za-z0-9-]))[A-Za-z][A-Za-z0-9-]*[ \t]*>)"
    r"[ \t]*$"
)
#: The characters a block's start can open with, past its indent; a line
#: opening with any other carries a paragraph on or opens one.
_STARTS = frozenset("#`~<>-+*_=0123456789")
_DELIMITER_CELL = re.compile(r":?-+:?")
#: A pipe no backslash escapes, which is where a table row splits.
_CELL_BREAK = re.compile(r"(?<!\\)\|")
_SETEXT_LEVEL = "setext"


class _Container:
    """A block quote or list item still open while the document is read."""

    __slots__ = ("depth", "empty", "last", "lazy", "quote", "start", "width")

    def __init__(
        self, quote: bool, start: int, depth: int, width: int = 0, empty: bool = False
    ) -> None:
        self.quote = quote
        self.start = start
        self.depth = depth
        #: A list item's content column, counted from where its container's
        #: content starts.
        self.width = width
        #: Whether the item opened on an empty marker line, which a blank line
        #: straight after ends (§ 5.2: an item begins with at most one).
        self.empty = empty
        self.last = start
        self.lazy = -1


class _Leaf:
    """The leaf block open while the document is read."""

    __slots__ = ("depth", "fence", "kind", "last", "level", "start", "until")

    def __init__(self, kind: str, start: int, depth: int) -> None:
        self.kind = kind
        self.start = start
        self.last = start
        self.depth = depth
        self.level = 0
        #: A fence's opening run of backticks or tildes.
        self.fence = ""
        #: An HTML block's end marker; `None` for one that runs to a blank line.
        self.until: re.Pattern[str] | None = None


def read(lines: Sequence[str]) -> Document:
    """Every leaf block and list item of the document `lines` holds."""
    return _read(tuple(lines))


@lru_cache(maxsize=16)
def _read(lines: tuple[str, ...]) -> Document:
    """`read`, kept for the readers that ask it of one document in turn.

    A block nothing closes before the end is read as written by reading the
    document again without it, as many times as there are such blocks.
    """
    fence_from = len(lines)
    unread: frozenset[int] = frozenset()
    while True:
        blocks, items, unclosed = _parse(lines, fence_from, unread)
        if unclosed is None:
            return Document(tuple(blocks), tuple(items))
        kind, start = unclosed
        if kind == FENCE:
            fence_from = start
        else:
            unread |= {start}


def statement_lines(lines: Sequence[str]) -> Iterator[tuple[int, int]]:
    """Each statement of a Markdown document, as its span of `lines` (`PL-R417`).

    A statement is a paragraph, with every line CommonMark 0.31.2 carries it
    onto - a soft break's (§ 6.7) and a lazy continuation line's (§ 5.2) - or a
    block of its own: a heading, a thematic break, an HTML block, each run of an
    indented code block's lines between blank ones, and each row of a table. A
    list item's paragraph is one, so a list is as many statements as it has
    paragraphs. A fence is a literal rather than prose and is none. Each pair is
    the index of the statement's first line and one past its last.
    """
    for block in read(lines).blocks:
        if block.kind == FENCE:
            continue
        if block.kind == TABLE:
            yield from ((index, index + 1) for index in range(block.start, block.end))
        elif block.kind == CODE:
            first = block.start
            for index in range(block.start, block.end):
                if not lines[index].strip():
                    if first < index:
                        yield first, index
                    first = index + 1
            yield first, block.end
        else:
            yield block.start, block.end


def block_lines(lines: Sequence[str], kinds: Collection[str]) -> frozenset[int]:
    """The index of every line of a block of one of `kinds`, at any depth."""
    return frozenset(
        index
        for block in read(lines).blocks
        if block.kind in kinds
        for index in range(block.start, block.end)
    )


def headings(lines: Sequence[str]) -> list[Heading]:
    """Every top-level heading, ATX (§ 4.2) and setext (§ 4.3), in order.

    An ATX heading's title loses its closing run of `#`s; a setext heading's is
    its paragraph's lines, joined with the space a soft break renders as.
    """
    found: list[Heading] = []
    for block in read(lines).blocks:
        if block.kind != HEADING or block.depth:
            continue
        if block.end - block.start == 1:
            line = lines[block.start].expandtabs(4)
            opening = _ATX.match(line)
            assert opening is not None
            title = _ATX_CLOSE.sub("", line[opening.end() :].strip())
        else:
            title = " ".join(line.strip() for line in lines[block.start : block.end - 1])
        found.append(Heading(block.start, block.level, title.strip()))
    return found


def tables(lines: Sequence[str]) -> list[Table]:
    """Every top-level table, its header row and each body row split into cells."""
    return [
        Table(
            block.start,
            cells(lines[block.start]),
            tuple((index, cells(lines[index])) for index in range(block.start + 2, block.end)),
        )
        for block in read(lines).blocks
        if block.kind == TABLE and not block.depth
    ]


def cells(row: str) -> tuple[str, ...]:
    """A table row's cells, split as GitHub Flavored Markdown 0.29 § 4.10 splits them.

    At each pipe no backslash escapes, the outer pipes optional, and `\\|` read
    as a pipe inside its cell, which is where markdown-it-py's `escapedSplit`
    splits too.
    """
    parts = _CELL_BREAK.split(row.strip())
    if parts and parts[0] == "":
        parts.pop(0)
    if parts and parts[-1] == "":
        parts.pop()
    return tuple(part.replace("\\|", "|").strip() for part in parts)


def _delimiter_columns(text: str) -> int:
    """How many columns a delimiter row declares, or 0 where `text` is none.

    Pipes, hyphens, colons and spaces only, never opening like a list item, and
    each cell `:?-+:?` with none empty but an outer one, as markdown-it-py reads
    it. A bare run of hyphens is a setext underline instead, as cmark-gfm reads
    it, because that start is tried before a table's.
    """
    text = text.strip()
    if text.strip("|-: \t") or len(text) < 2 or (text[0] == "-" and text[1] in " \t"):
        return 0
    if "|" not in text and ":" not in text:
        return 0
    found = text.split("|")
    count = 0
    for position, cell in enumerate(found):
        cell = cell.strip()
        if not cell:
            if position in (0, len(found) - 1):
                continue
            return 0
        if _DELIMITER_CELL.fullmatch(cell) is None:
            return 0
        count += 1
    return count


def _indent(line: str, position: int) -> int:
    """How many spaces stand at `position` in `line`."""
    end = position
    while end < len(line) and line[end] == " ":
        end += 1
    return end - position


def _after_quote(line: str, end: int) -> int:
    """Where a block quote's content starts: past its `>` and one space after it."""
    return end + 1 if line[end : end + 1] == " " else end


def _inside(line: str, containers: Sequence[_Container]) -> str | None:
    """`line` with `containers`' markers and indents taken off, or `None` where one ends."""
    line = line.expandtabs(4) if "\t" in line else line
    position = 0
    for container in containers:
        if container.quote:
            quote = _QUOTE.match(line, position)
            if quote is None:
                return None
            position = _after_quote(line, quote.end())
        elif line[position:].strip():
            if _indent(line, position) < container.width:
                return None
            position += container.width
    return line[position:]


def _opens_table(
    lines: Sequence[str], index: int, text: str, containers: Sequence[_Container]
) -> bool:
    """Whether `text`, read at `lines[index]`, is a table's header row (§ 4.10).

    It holds a pipe, and the next line, inside the same containers and less
    than four columns into them, is a delimiter row declaring as many columns
    as `text` has cells.
    """
    if "|" not in text or index + 1 >= len(lines):
        return False
    under = _inside(lines[index + 1], containers)
    if under is None or _indent(under, 0) >= 4:
        return False
    columns = _delimiter_columns(under)
    return columns > 0 and columns == len(cells(text))


def _html_end(line: str, at: int) -> re.Pattern[str] | None:
    """The end marker of the HTML block of kinds 1 to 5 `line` opens at `at`, or `None`."""
    for opening, closing in _HTML_ENDED:
        if opening.match(line, at):
            return closing
    return None


def _touch(stack: Sequence[_Container], index: int) -> None:
    """Record `index` as the last line holding anything in each list item open."""
    for container in stack:
        if not container.quote:
            container.last = index


def _parse(
    lines: Sequence[str], fence_from: int, unread: Collection[int]
) -> tuple[list[Block], list[Item], tuple[str, int] | None]:
    """One reading of `lines`, and the block left open at the end, as its kind and line.

    A fence opening at `fence_from` or later, and an HTML block of kinds 1 to 5
    opening on a line in `unread`, is read as written: `_read` passes each block
    this returns back in, until none is left open.
    """
    blocks: list[Block] = []
    items: list[Item] = []
    stack: list[_Container] = []
    leaf: _Leaf | None = None

    def finish() -> None:
        nonlocal leaf
        assert leaf is not None
        blocks.append(Block(leaf.kind, leaf.start, leaf.last + 1, leaf.depth, leaf.level))
        leaf = None

    def unwind(keep: int) -> None:
        while len(stack) > keep:
            container = stack.pop()
            if not container.quote:
                end = container.last + 1
                items.append(Item(container.start, end, container.depth, container.lazy))

    for index, raw in enumerate(lines):
        line = raw.expandtabs(4) if "\t" in raw else raw

        # Match the line against each container still open, outermost first.
        position = matched = 0
        for container in stack:
            if container.quote:
                quote = _QUOTE.match(line, position)
                if quote is None:
                    break
                position = _after_quote(line, quote.end())
            elif line[position:].strip():
                if _indent(line, position) < container.width:
                    break
                position += container.width
            elif container.empty and index == container.start + 1:
                break
            matched += 1
        rest = line[position:]
        blank = not rest.strip()
        held = matched == len(stack)

        # A fence, an HTML block and an indented code block take a line whole
        # while every container holds it; a container's end ends them, and a
        # table, all the same.
        if leaf is not None and leaf.kind in (FENCE, HTML, CODE, TABLE) and not held:
            finish()
        elif leaf is not None and leaf.kind == FENCE:
            leaf.last = index
            closing = _FENCE_CLOSE.match(rest)
            if (
                closing is not None
                and closing["fence"][0] == leaf.fence[0]
                and len(closing["fence"]) >= len(leaf.fence)
            ):
                finish()
            if not blank:
                _touch(stack, index)
            continue
        elif leaf is not None and leaf.kind == HTML and (leaf.until is not None or not blank):
            leaf.last = index
            if leaf.until is not None and leaf.until.search(rest):
                finish()
            if not blank:
                _touch(stack, index)
            continue
        elif leaf is not None and leaf.kind == CODE:
            if blank:
                continue
            if _indent(rest, 0) >= 4:
                leaf.last = index
                _touch(stack, index)
                continue
            finish()

        if blank:
            if leaf is not None:
                finish()
            unwind(matched)
            continue

        # Read the containers and the leaf block the line opens, if it opens any.
        paragraph = leaf is not None and leaf.kind == PARAGRAPH
        opened: list[_Container] = []
        at = position
        kind = ""
        level = 0
        fence = ""
        until: re.Pattern[str] | None = None
        while True:
            carried = paragraph and not opened
            interrupting = carried and held
            indent = _indent(line, at)
            if at + indent >= len(line):
                break
            if indent >= 4:
                kind = "" if carried else CODE
                break
            if line[at + indent] not in _STARTS:
                break
            if (quote := _QUOTE.match(line, at)) is not None:
                opened.append(_Container(True, index, matched + len(opened)))
                at = _after_quote(line, quote.end())
                continue
            if (atx := _ATX.match(line, at)) is not None:
                kind, level = HEADING, len(atx["hashes"])
                break
            if index < fence_from and (opening := _FENCE.match(line, at)) is not None:
                kind, fence = FENCE, opening["fence"]
                break
            if index not in unread and (until := _html_end(line, at)) is not None:
                kind = HTML
                break
            if _HTML_BLOCK_TAG.match(line, at) or (not carried and _HTML_TAG_LINE.match(line, at)):
                kind = HTML
                break
            if interrupting and (rule := _SETEXT.match(line, at)) is not None:
                kind, level = _SETEXT_LEVEL, 1 if rule["rule"][0] == "=" else 2
                break
            if _BREAK.match(line, at):
                kind = BREAK
                break
            if (marker := _MARKER.match(line, at)) is not None:
                after = marker.end()
                gap = _indent(line, after)
                empty = after + gap >= len(line)
                number = marker["number"]
                if interrupting and (empty or (number is not None and int(number) != 1)):
                    break
                if empty or gap > 4:
                    gap = 1
                width = after + gap - at
                opened.append(_Container(False, index, matched + len(opened), width, empty))
                at = min(after + gap, len(line))
                continue
            break

        if kind == _SETEXT_LEVEL:
            # The paragraph above, in the same containers, becomes the heading.
            assert leaf is not None
            leaf.kind, leaf.level, leaf.last = HEADING, level, index
            finish()
            _touch(stack, index)
            continue

        if not kind and not opened:
            # A text line: a table's row, a paragraph's, or a new paragraph's or table's.
            if leaf is not None and leaf.kind == TABLE:
                leaf.last = index
                _touch(stack, index)
                continue
            if leaf is not None and not (held and _opens_table(lines, index, rest, stack)):
                for container in stack[matched:]:
                    if not container.quote and container.lazy < 0 and raw[:1] not in " \t":
                        container.lazy = index
                leaf.last = index
                _touch(stack, index)
                continue

        if leaf is not None:
            finish()
        unwind(matched)
        stack.extend(opened)
        _touch(stack, index)
        depth = len(stack)
        if kind in (HEADING, BREAK):
            blocks.append(Block(kind, index, index + 1, depth, level))
        elif kind:
            leaf = _Leaf(kind, index, depth)
            leaf.fence, leaf.until = fence, until
            if until is not None and until.search(line, at):
                finish()
        elif line[at:].strip():
            table = _opens_table(lines, index, line[at:], stack)
            leaf = _Leaf(TABLE if table else PARAGRAPH, index, depth)

    unclosed = None
    if leaf is not None:
        if leaf.kind == FENCE or (leaf.kind == HTML and leaf.until is not None):
            unclosed = (leaf.kind, leaf.start)
        finish()
    unwind(0)
    items.sort(key=lambda item: (item.start, item.depth))
    return blocks, items, unclosed
