"""Reading Python source a statement at a time, as the tokenizer reads it.

Python continues a statement across physical lines after a backslash, inside
brackets and inside a triple-quoted string, and ends it at the end of the
logical line (Python Language Reference § 2.1). A reader that takes a physical
line for a statement reads a fragment of one: a `def` inside a docstring
defines nothing, a marker split over two lines is on neither, and a docstring
line opening with `assert` asserts nothing (`PL-R417`). This module is docket's
one reading of where a Python statement starts and ends, which `verify`'s two
integrity checks and `tools/doc_check.py`'s definition readers take.

**The tokenizer, not the parser, and that is the point of it rather than a
shortcut.** `bin/docket` runs on the bare `python3`, which can be older than
the project's own, and each syntax the project has adopted past 3.11 adds
grammar rather than tokens: 3.11's tokenizer reads
`src/anesthesia_sim/app_metadata.py` (PEP 758) and
`src/anesthesia_sim/app/bookmarks.py` (PEP 695) whole, into the logical lines
3.14's does, where 3.11's parser reads neither (`PL-TC2D`). What the tokenizer
cannot read it refuses, and a caller reads that file another way and says so.
What it reads without refusing can still differ from a newer interpreter's
reading in one place: a formatted string nesting its own quote (PEP 701)
mis-tokenizes on 3.11 without an error, so a caller that could not parse a file
names it on its page even where this read it.
"""

from __future__ import annotations

import io
import tokenize
from collections.abc import Sequence
from dataclasses import dataclass

#: The token types that hold no code: a comment, and the layout between
#: lines and blocks. `NEWLINE`, which ends a logical line, is read as that.
_LAYOUT = frozenset(
    {
        tokenize.COMMENT,
        tokenize.NL,
        tokenize.INDENT,
        tokenize.DEDENT,
        tokenize.ENCODING,
        tokenize.ENDMARKER,
    }
)

#: The tokens that open and close a formatted string, by name, since no
#: constant exists for them before 3.12 (`FSTRING_*`) and 3.14 (`TSTRING_*`).
#: From those versions the tokenizer hands such a string over in parts, with
#: each replacement field's code as tokens of its own, where 3.11 hands over
#: one `STRING`. Read as one piece either way, cut from the source as written,
#: so a file reads the same under the bare `python3` docket runs on and under
#: the project's own interpreter.
_STRING_OPENS = ("FSTRING_START", "TSTRING_START")
_STRING_CLOSES = ("FSTRING_END", "TSTRING_END")

#: What reading a file raises where the tokenizer refuses it: `TokenError` for
#: a string or a bracket still open at the end, `SyntaxError` for a dedent to no
#: outer level and for what 3.12's tokenizer refuses outright, and `ValueError`
#: - `UnicodeDecodeError` among them - for text a caller could not decode.
#:
#: **An error token is a refusal too.** 3.11's tokenizer hands back as an
#: `ERRORTOKEN` what 3.12's raises - an unterminated quote, a null byte, a
#: formatted string's field continued across lines - and reads on past it, so a
#: reading that kept going would differ by interpreter. It is raised here as a
#: `TokenError`, which makes every interpreter refuse the same files.
UNTOKENIZABLE = (tokenize.TokenError, SyntaxError, ValueError)


@dataclass(frozen=True)
class Piece:
    """One token of a statement's code, or one string however the tokenizer split it."""

    #: The token as written, or `""` for a string, which holds no code.
    code: str
    #: Its source as written.
    text: str
    #: Where it starts and ends, as `(row, column)`: rows from 1, ended at each
    #: "\\n" alone, as `io.StringIO.readline` hands them to the tokenizer.
    start: tuple[int, int]
    end: tuple[int, int]


@dataclass(frozen=True)
class LogicalLine:
    """One logical line of Python source, as the tokenizer builds it from physical ones.

    The unit every reader here takes: a suppression is written in one - a
    decorator, an assignment, a call (`PL-CFWP`) - an assertion is one, and a
    definition is the one its `def` or `class` opens, its signature however
    many physical lines it was wrapped over (`PL-V2HK`, `PL-TC2D`).
    """

    #: Its code and strings, comments and layout left out, in order.
    pieces: tuple[Piece, ...]
    #: Those pieces as written: what makes two the same line to a fold, so a
    #: re-wrap, a re-indent or a changed comment is no change.
    tokens: str
    #: The same with each string blanked whole and each dotted name joined
    #: however it was split: what a pattern over code is matched against.
    code: str
    #: Its source as written, on one line: what a report prints.
    shown: str
    #: The physical rows it spans, whole, from `first`: what `text` cuts.
    rows: tuple[str, ...]

    @property
    def first(self) -> int:
        """The physical row it opens on, counted from 1."""
        return self.pieces[0].start[0]

    @property
    def last(self) -> int:
        """The physical row it closes on."""
        return self.pieces[-1].end[0]

    @property
    def indent(self) -> int:
        """The column it opens at, which is how far its block is indented."""
        return self.pieces[0].start[1]

    def text(self, start: tuple[int, int], end: tuple[int, int]) -> str:
        """Its source as written from `start` to `end`, positions as its pieces carry them."""
        return _cut(self.rows, start, end, self.first)


def _cut(rows: Sequence[str], start: tuple[int, int], end: tuple[int, int], first: int = 1) -> str:
    """The source between two positions the tokenizer gave, `rows` opening on row `first`."""
    (first_row, first_column), (last_row, last_column) = start, end
    cut = list(rows[first_row - first : last_row - first + 1])
    cut[-1] = cut[-1][:last_column]
    cut[0] = cut[0][first_column:]
    return "\n".join(cut)


def read_logical_lines(source: str) -> tuple[LogicalLine, ...]:
    """Every logical line `source` holds, in order.

    Raises one of `UNTOKENIZABLE` where the tokenizer refuses the file, an
    error token included, so that the caller can read it another way and say
    that it did. It does not parse: whether `source` is valid Python is the
    parser's question, and a caller that needs it answered asks the parser.
    """
    # The rows `readline` hands the tokenizer, which splits on "\n" alone.
    physical = source.split("\n")
    found: list[LogicalLine] = []
    pieces: list[Piece] = []
    opened = (0, 0)  # where the formatted string being read opened
    depth = 0
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.ERRORTOKEN:
            # Named by the text it opens, since 3.11 hands back the space
            # before what it cannot read as an error token of its own.
            at = token.line[token.start[1] :].strip()[:20] or token.string
            raise tokenize.TokenError(f"an error token at {at!r}", token.start)
        if token.type == tokenize.NEWLINE:
            if pieces:
                found.append(_logical_line(pieces, physical))
            pieces = []
            continue
        if token.type in _LAYOUT:
            continue
        kind = tokenize.tok_name[token.type]
        if kind in _STRING_OPENS:
            opened = token.start if not depth else opened
            depth += 1
        elif kind in _STRING_CLOSES:
            depth -= 1
            if not depth:
                pieces.append(Piece('""', _cut(physical, opened, token.end), opened, token.end))
        elif not depth:
            code = '""' if token.type == tokenize.STRING else token.string
            pieces.append(Piece(code, token.string, token.start, token.end))
    return tuple(found)


def _logical_line(pieces: Sequence[Piece], physical: Sequence[str]) -> LogicalLine:
    code = pieces[0].code
    for before, piece in zip(pieces, pieces[1:], strict=False):
        # A dotted name is one name however it was split, and a decorator's `@`
        # belongs to the name after it. Every other pair keeps a space, so a
        # binary `@` before a name starting `skip` is not read as `@skip`.
        joined = "." in (before.code, piece.code) or (before.code == "@" and code == "@")
        code += piece.code if joined else f" {piece.code}"
    first, last = pieces[0].start, pieces[-1].end
    return LogicalLine(
        tuple(pieces),
        " ".join(piece.text for piece in pieces),
        code,
        " ".join(_cut(physical, first, last).split()),
        tuple(physical[first[0] - 1 : last[0]]),
    )


def definition(line: LogicalLine) -> tuple[str, str]:
    """The keyword and the name a `def`, `async def` or `class` statement defines.

    `("", "")` for any other statement, and `"def"` for an `async def`. A
    definition opens its logical line - a decorator is a statement of its own,
    and no compound statement follows a colon on its line - so its first words
    are all this reads, and a `def` inside a string is that string's text
    rather than a word of the statement around it (`PL-V2HK`).
    """
    words = [piece.code for piece in line.pieces[:3]]
    if words[:1] == ["async"]:
        words = words[1:]
    if len(words) > 1 and words[0] in ("def", "class") and words[1].isidentifier():
        return words[0], words[1]
    return "", ""


def refusal(error: Exception) -> str:
    """What the tokenizer said in refusing a file, and on which line, as a page prints it."""
    if isinstance(error, UnicodeDecodeError):
        return "not UTF-8"
    if isinstance(error, SyntaxError):
        return f"{error.msg}, line {error.lineno}" if error.lineno else str(error.msg)
    message, *rest = error.args or (type(error).__name__,)
    where = rest[0] if rest and isinstance(rest[0], tuple) and rest[0] else ()
    return f"{message}, line {where[0]}" if where else str(message)
