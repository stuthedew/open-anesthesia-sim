"""Where a Markdown file's YAML front matter ends, and where each key in it does.

The front matter Claude Code reads on a rule or a skill: a first line of `---`,
then YAML, then a closing `---`. This is the one reading of it (`PL-R417`):
`tools/rules_paths_check.py` reads a rule's `paths:` through it,
`tools/doc_check.py` whether a rule declares one, `docket.instructions` each
key's dated sentences, and `docket.notes` where a notes file's Markdown begins.
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
quoted scalar or a flow collection the key's own line opens runs to its close
however the lines below it are indented: PyYAML 6.0 reads a continuation at the
first column that way where a strict YAML 1.2.2 reader refuses the file (§ 6.3),
and either way the key such a line looks like is no key. A node opening below
the key's line is followed by indentation alone, which is where YAML 1.2.2 puts
every line of it. Nothing inside a value is checked, so a value YAML refuses can
still be passed over here: what a value holds is its reader's to decide, and
`rules_paths_check.entries` decides `paths:`'s. A line at the first column that
opens no key raises `Unread` naming it, as does an indented line above the first
key, since no value holds either and a reader passing over one would hand on the
key above it short.

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


class Unread(ValueError):
    """A front matter this reader cannot split into its keys, the line named in the message."""


@dataclass(frozen=True)
class Key:
    """One top-level key: its name, what follows its `:`, and the lines its value takes.

    `line` is the index of the key's own line in the block and `end` the index
    past the last line of its value. Every indented line under the key is its
    value's, a `#`-led one included, since a quoted or block scalar holds a `#`
    as content; blank lines and first-column comments after it are no part of
    it. `inline` is the rest of the key's line after the `:`, as written,
    comment and all.
    """

    name: str
    inline: str
    line: int
    end: int


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
    scalar or flow collection a key's line opens that nothing in the block
    closes.
    """
    found: list[Key] = []
    index = 0
    while index < len(block):
        text = block[index].strip()
        if not text or text.startswith("#"):
            index += 1
            continue
        if block[index][:1] in (" ", "\t"):
            raise Unread(f"`{text}` is indented above the first key, so no value holds it")
        opened = _key(block[index])
        if opened is None:
            raise Unread(f"`{text}` sits at the first column and opens no key")
        name, at = opened
        inline = block[index][at:]
        start = index
        last = _past(block, index, at) - 1
        # A key holding nothing on its own line may hold a list at its column.
        bare = not uncommented(inline).strip()
        index = last + 1
        while index < len(block):
            line = block[index]
            text = line.strip()
            if (line[:1] in (" ", "\t") and text) or (bare and is_item(line)):
                last = index
            elif text and not text.startswith("#"):
                break
            index += 1
        found.append(Key(name, inline, start, last + 1))
        index = last + 1
    return tuple(found)


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
    """`text`, a node as a line holds it, without its comment (§ 6.6).

    A comment opens at a `#` that opens the node or follows white space, and
    never inside a quoted scalar opening it, so `"/src/**" # why` is the glob
    `"/src/**"` and `"a # b"` is all scalar. A quoted scalar its line does not
    close leaves the line as it is, since what follows is the scalar's.
    """
    start = len(text) - len(text.lstrip(" \t"))
    if text[start : start + 1] in ("'", '"'):
        end = closing_quote(text, start)
        if end < 0:
            return text
        start = end + 1
    for index in range(start, len(text)):
        if text[index] == "#" and (index == 0 or text[index - 1] in " \t"):
            return text[:index]
    return text


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


def _quote_end(block: Sequence[str], line: int, position: int) -> tuple[int, int]:
    """The line and column of the quote closing the scalar `block[line][position]` opens."""
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
    return line, found


def _key(line: str) -> tuple[str, int] | None:
    """The key `line` opens at its first column, and the index past its `:`.

    A plain or quoted scalar ended by a `:` that white space or the line's end
    follows (§ 7.3, § 8.2.2). `None` where `line` opens none: a comment, an
    indicator, or text no such `:` ends.
    """
    if line[:1] in ("'", '"'):
        end = closing_quote(line)
        colon = end + 1
        while 0 < colon < len(line) and line[colon] in " \t":
            colon += 1
        if (
            end < 0
            or line[colon : colon + 1] != ":"
            or line[colon + 1 : colon + 2] not in ("", " ", "\t")
        ):
            return None
        name = line[1:end]
        return (name.replace("''", "'") if line[0] == "'" else name), colon + 1
    if line[:1] in INDICATORS and not (line[:1] in "-?:" and line[1:2] not in ("", " ", "\t")):
        return None
    for index, char in enumerate(line):
        if char == "#" and line[index - 1] in " \t":
            return None
        if char == ":" and line[index + 1 : index + 2] in ("", " ", "\t"):
            return line[:index].rstrip(), index + 1
    return None


def _past(block: Sequence[str], index: int, at: int) -> int:
    """The index past the line on which the node opening at `block[index][at:]` ends.

    The next line, unless the node is a quoted scalar or a flow collection that
    line does not close, which is followed to its close across the lines below.
    An anchor or a tag before the node names it and changes nothing in it
    (§ 6.9).
    """
    text = block[index]
    while True:
        while at < len(text) and text[at] in " \t":
            at += 1
        if text[at : at + 1] not in ("&", "!"):
            break
        while at < len(text) and text[at] not in " \t":
            at += 1
    if text[at : at + 1] in ("'", '"'):
        return _quote_end(block, index, at)[0] + 1
    if text[at : at + 1] in ("[", "{"):
        return _flow_end(block, index, at) + 1
    return index + 1


def _flow_end(block: Sequence[str], index: int, at: int) -> int:
    """The index of the line closing the flow collection `block[index][at]` opens (§ 7.4).

    A quote inside it opens a quoted scalar only where a node can open, after a
    bracket, a `,` or a `:`, so the `'` in `[don't]` is a character, and a `#`
    after white space comments out the rest of its line.
    """
    depth = 0
    node = True
    line, position = index, at
    while line < len(block):
        text = block[line]
        while position < len(text):
            char = text[position]
            if char == "#" and (position == 0 or text[position - 1] in " \t"):
                break
            if char in ("'", '"') and node:
                line, position = _quote_end(block, line, position)
                text = block[line]
                node = False
            elif char in "[{":
                depth, node = depth + 1, True
            elif char in "]}":
                depth, node = depth - 1, False
                if depth == 0:
                    return line
            elif char in ",:":
                node = True
            elif char not in " \t":
                node = False
            position += 1
        line, position = line + 1, 0
    raise Unread(
        f"`{block[index].strip()}` opens a flow collection that nothing in the front matter closes"
    )
