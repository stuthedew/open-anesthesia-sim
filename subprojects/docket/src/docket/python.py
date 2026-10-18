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

import ast
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


def places(lines: Sequence[LogicalLine]) -> tuple[str, ...]:
    """The definition each of `lines` belongs to, as the names of it and those holding it.

    Joined with `::`, outermost first, as pytest names a test, and `""` for a
    statement no definition holds. A `def` or `class` belongs to itself and
    holds every statement indented past the column it opens at, as a block's
    statements are indented under it, until one opens at that column or
    before it. A decorator belongs to the definition it decorates - the next
    statement at its column that is no decorator - as `ast` holds a decorator
    in its definition's node: read in the definition around it, a marker moved
    from one test onto the next was the same statement in the same place
    (`PL-W6ZD`).
    """
    found: list[str] = []
    scopes: list[tuple[int, str]] = []  # each open class and function: its indent and name
    for line in lines:
        while scopes and scopes[-1][0] >= line.indent:
            scopes.pop()
        if name := definition(line)[1]:
            scopes.append((line.indent, name))
        found.append("::".join(scope for _, scope in scopes))
    # From the end, so each decorator of a stack reaches the definition under it.
    for at in range(len(lines) - 2, -1, -1):
        line, after = lines[at], lines[at + 1]
        if _decorates(line) and after.indent == line.indent:
            if definition(after)[1] or _decorates(after):
                found[at] = found[at + 1]
    return tuple(found)


def _decorates(line: LogicalLine) -> bool:
    """Whether `line` is a decorator, which only a decorator's `@` can open."""
    return line.pieces[0].code == "@"


def refusal(error: Exception) -> str:
    """What the tokenizer said in refusing a file, and on which line, as a page prints it."""
    if isinstance(error, UnicodeDecodeError):
        return "not UTF-8"
    if isinstance(error, SyntaxError):
        return f"{error.msg}, line {error.lineno}" if error.lineno else str(error.msg)
    message, *rest = error.args or (type(error).__name__,)
    where = rest[0] if rest and isinstance(rest[0], tuple) and rest[0] else ()
    return f"{message}, line {where[0]}" if where else str(message)


# --- what a parsed module documents and imports (`PL-8W1J`) -----------------
#
# These two read a parsed tree rather than tokens. Each is the one reading of
# its fact for docket and `tools/`. Until `PL-8W1J` three checks each decided
# which strings are docstrings, and two decided which modules a file imports,
# and they disagreed on an attribute docstring and on `importlib.import_module`.


def docstrings(tree: ast.AST) -> list[ast.Constant]:
    """Every string that is a statement of its own, which is every docstring there is.

    A module, class or function docstring is one, and so is an attribute
    docstring: the string a statement after an assignment holds, as PEP 257
    § "What is a Docstring?" describes. Defining a docstring by its position
    as the first statement of a scope would miss the attribute docstring,
    which no scope opens with. So a string is documentation when it stands
    alone as a statement, wherever it stands. Returned in `ast.walk` order.
    """
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    ]


#: The call names whose first argument, where it is a literal string, names a
#: module: `importlib.import_module` and the builtin `__import__`.
DYNAMIC_IMPORTERS = frozenset({"import_module", "__import__"})


@dataclass(frozen=True)
class Imported:
    """One import statement found in one module, and every dotted name it makes available."""

    names: tuple[str, ...]
    line: int
    statement: str

    def reaches(self, package: str) -> bool:
        """Does any name equal `package`, or continue it past a dot?"""
        return any(name == package or name.startswith(package + ".") for name in self.names)


def _dynamic_name(node: ast.Call) -> str | None:
    """The module a dynamic import names, where the name is a literal.

    Returns `None` for anything undecidable by reading the source: a computed
    name, a keyword-only call, or a relative name, which resolves against a
    `package` argument this does not evaluate.
    """
    function = node.func
    if isinstance(function, ast.Attribute):
        name = function.attr
    elif isinstance(function, ast.Name):
        name = function.id
    else:
        return None
    if name not in DYNAMIC_IMPORTERS or not node.args:
        return None
    first = node.args[0]
    if not (isinstance(first, ast.Constant) and isinstance(first.value, str)):
        return None
    if first.value.startswith("."):
        return None
    return first.value or None


def _resolve(module: str | None, level: int, package: str | None) -> str | None:
    """The absolute module a `from` statement names, relative or not.

    importlib's own rule. `None` where it cannot be decided: a relative import
    read without the importing module's package, or one climbing past the top
    of it, which would fail at import time anyway.
    """
    if not level:
        return module
    if not package:
        return None
    bits = package.rsplit(".", level - 1)
    if len(bits) < level:
        return None
    return f"{bits[0]}.{module}" if module else bits[0]


def imports(tree: ast.AST, package: str | None = None) -> tuple[Imported, ...]:
    """Every import one module makes, by any form this can decide.

    `import x`, `from x import y` and a dynamic import of a literal name all
    count. A relative import resolves against `package`, the importing
    module's package, `anesthesia_sim.core` for `core/x.py`, and is left out
    where no package is given, since it cannot then be decided. The result has
    one entry per import, in source order, each carrying every dotted name the
    import makes available.
    """
    found: list[Imported] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.append(Imported((alias.name,), node.lineno, f"import {alias.name}"))
        elif isinstance(node, ast.ImportFrom):
            module = _resolve(node.module, node.level, package)
            if module is None:
                continue
            members = [alias.name for alias in node.names if alias.name != "*"]
            names = (module, *(f"{module}.{member}" for member in members))
            written = "." * node.level + (node.module or "")
            imported = ", ".join(alias.name for alias in node.names)
            found.append(Imported(names, node.lineno, f"from {written} import {imported}"))
        elif isinstance(node, ast.Call):
            name = _dynamic_name(node)
            if name is not None:
                found.append(Imported((name,), node.lineno, f"a dynamic import of {name!r}"))
    return tuple(sorted(found, key=lambda entry: (entry.line, entry.statement)))
