"""Where a fenced block is: the one reading every reader in docket and `tools/` takes.

A fenced block holds a literal - a command, an example, the capture template
quoted, a citation shown as broken - and every reader that judges prose reads
past it. There used to be five spellings of where one is, in `checks.py`,
`instructions.py` and three in `tools/doc_check.py`, and they disagreed on a
triple-backtick code span wrapped to a line's start, on tildes, and on a fence
left open. `PL-6SRZ`'s brief wraps such a span, and doc_check read it as an
opener nothing closed, so the rest of that brief was never read for line
citations while `make check` passed (`PL-92MY`). So there is one reading, here,
and `tools/doc_check.py` takes it through the import it already makes.

It is CommonMark 0.31.2's (§ 4.5), read by `markdown`, which knows what holds
each line (`PL-J0C6`), in four rules and one refusal:

- three or more backticks or tildes open a block at most three columns into
  the block quote or list item holding the line, or into the margin, so a fence
  under a list item is indented to sit inside it and one indented four columns
  past its container is a line of an indented code block or a paragraph;
- a backtick opener's info string holds no backtick, which is what keeps a
  wrapped code span like `PL-6SRZ`'s from opening one;
- a bare run of the same character, at least as long and at most three columns
  into the same containers, closes it;
- the end of the block quote or list item holding it closes it too;
- and **a fence nothing closes before the document ends is not a fence**. The
  opener and every line after it are read as written, where CommonMark runs the
  block to the end of the document. Every reader here skips a literal, so
  CommonMark's reading would skip the rest of the file silently, which is the
  defect this module exists to remove; read as written, an unclosed fence costs
  at worst a loud false error on a literal, repaired by closing the fence the
  document needs anyway.

A line is what `lines.split_lines` cuts - the text broken at `\\n` alone, which
on text decoded as Python decodes it is where CommonMark ends one - and an
index is 0-based.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import markdown
from .lines import split_lines


@dataclass(frozen=True)
class Block:
    """One closed fenced block: the indices of its opening line and its last line.

    The last is its closing fence line, or, where its container's end closed
    it, the last line its container held.
    """

    start: int
    end: int


def blocks(text: str) -> list[Block]:
    """Every closed fenced block in `text`, in order.

    An opener nothing closes opens none, and nothing after it is a block either:
    its lines are read as written, and a fence-shaped line among them is one of
    them.
    """
    return [
        Block(block.start, block.end - 1)
        for block in markdown.read(split_lines(text)).blocks
        if block.kind == markdown.FENCE
    ]


def fenced_lines(text: str) -> frozenset[int]:
    """The index of every line of a closed block, both fence lines included."""
    return frozenset(index for block in blocks(text) for index in range(block.start, block.end + 1))


def without_fences(text: str) -> str:
    """`text` with every line of a closed block blanked, offsets and line breaks kept.

    Each such line becomes as many spaces as it held characters and keeps its
    `\\n`, so every offset and line number past it still holds. A form feed or a
    U+2028 inside a fenced line ends no line, so it is one of the characters
    blanked (`PL-BBYJ`).
    """
    fenced = fenced_lines(text)
    out: list[str] = []
    for index, line in enumerate(split_lines(text, keepends=True)):
        if index in fenced:
            content = line.removesuffix("\n")
            out.append(" " * len(content) + line[len(content) :])
        else:
            out.append(line)
    return "".join(out)
