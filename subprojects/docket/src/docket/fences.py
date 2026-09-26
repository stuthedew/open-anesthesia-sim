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

It is CommonMark's, in three rules and one refusal:

- three or more backticks or tildes open a block, at any indentation, since a
  fence under a list item is indented to sit inside it;
- a backtick opener's info string holds no backtick, which is what keeps a
  wrapped code span like `PL-6SRZ`'s from opening one;
- a bare run of the same character, at least as long, closes it;
- and **a fence nothing closes is not a fence**. The opener and every line after
  it are read as written, where CommonMark runs the block to the end of the
  document. Every reader here skips a literal, so CommonMark's reading would
  skip the rest of the file silently, which is the defect this module exists to
  remove; read as written, an unclosed fence costs at worst a loud false error on
  a literal, repaired by closing the fence the document needs anyway.

A line is what `str.splitlines()` cuts, and an index is 0-based.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

#: A fenced block's opening line. The lookahead is the info-string rule: a
#: backtick run followed anywhere on its line by another backtick is a code
#: span's delimiter, not a fence.
OPEN_RE = re.compile(r"^[ \t]*(?P<fence>`{3,}(?=[^`]*$)|~{3,})")

#: A line that can close a block: a bare run, with nothing after it but spaces
#: or tabs. Whether it closes *this* block is `blocks`'s question, since the run
#: has to be the opener's character and at least as long.
CLOSE_RE = re.compile(r"^[ \t]*(?P<fence>`{3,}|~{3,})[ \t]*$")


@dataclass(frozen=True)
class Block:
    """One closed fenced block: the indices of its opening and its closing fence line."""

    start: int
    end: int


def blocks(text: str) -> list[Block]:
    """Every closed fenced block in `text`, in order.

    An opener nothing closes opens none, and nothing after it is a block either:
    its lines are read as written, and a fence-shaped line among them is one of
    them.
    """
    found: list[Block] = []
    fence = ""
    start = 0
    for index, line in enumerate(text.splitlines()):
        if fence:
            closing = CLOSE_RE.match(line)
            if closing and closing["fence"].startswith(fence):
                found.append(Block(start, index))
                fence = ""
        elif opening := OPEN_RE.match(line):
            fence, start = opening["fence"], index
    return found


def fenced_lines(text: str) -> frozenset[int]:
    """The index of every line of a closed block, both fence lines included."""
    return frozenset(index for block in blocks(text) for index in range(block.start, block.end + 1))


def without_fences(text: str) -> str:
    """`text` with every line of a closed block blanked, offsets and line breaks kept.

    Each such line becomes as many spaces as it held characters and keeps its own
    terminator, the one `str.splitlines()` cut. So a form feed or a U+2028 is not
    blanked into the line, and every offset and line number past it still holds,
    whether a reader counts lines as `splitlines()` does or by newlines.
    """
    fenced = fenced_lines(text)
    out: list[str] = []
    for index, line in enumerate(text.splitlines(keepends=True)):
        if index in fenced:
            content = line.splitlines()[0]
            out.append(" " * len(content) + line[len(content) :])
        else:
            out.append(line)
    return "".join(out)
