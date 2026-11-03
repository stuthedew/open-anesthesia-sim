#!/usr/bin/env python3
"""Refuse a regular expression written without a reason beside it, and say what to try first.

Regular expressions have been a steady source of defects here. About 60 items
in the queue name one, and `PL-9HD1` traced three of them to one pattern that
read item front matter a line at a time. The project owner asked on 2026-11-03
that a session stop each time it reaches for one, consider whether a parser or
a string method does the job better, look up the best practice for the task,
and use the regular expression only where it is still the right tool
(`PL-7JYV`).

Whether a regular expression is the right tool is a judgment, so this check
does not make it. It enforces that the judgment was made and written down.
Each call that builds or applies a pattern through the `re` module, or the
third-party `regex` module, needs a comment that starts with `regex:` and
gives the reason. The comment goes at the end of one of the statement's lines,
or in the comment lines directly above the statement. `GUIDANCE` is what a
session reads when this check or the edit hook stops it.

The hook `.claude/hooks/regex_guard.py` uses `added_uses` to refuse the edit
that writes such a call. This check is the backstop for what the hook cannot
see: an edit made through a shell command, and a thread where the
repository's hooks do not run.

The calls the tree held on 2026-11-03 are in `tools/regex_baseline.py`, keyed
by file, enclosing function and call, and never by line. That baseline only
shrinks. A count above an entry fails, and so does an entry the tree no longer
fills, so a call that is removed or given a reason cannot come back unseen.

Not read, and why:

- `re.escape`, which turns text into a pattern that matches only that text.
  It makes a pattern safer and decides nothing about using one.
- A method called on a compiled pattern, such as `ID_RE.match(text)`. The
  decision was made where the pattern was compiled, and that call is read.
- pytest's `match=` argument. It is a regular expression too, but the
  repository passes one about 900 times, and its usual alternative is already
  `re.escape`. A stop at each new test would fire without changing a decision.
- Patterns in shell scripts, Makefiles and workflow files. The hooks written
  in shell held no `grep -E`, `sed` or `=~` pattern on 2026-11-03.

Every tracked Python file is read, so this check runs under the project's
interpreter. Under an older bare `python3`, a file that uses newer syntax does
not parse, and the check reports it as unread and fails rather than passing it.

Standard library only and floor-parseable, like every tool under `tools/`.
"""

from __future__ import annotations

import ast
import io
import sys
import tokenize
from collections import Counter
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from docket.lines import split_lines  # noqa: E402
from docket.vcs import Unlisted, tracked_under  # noqa: E402

from check_support import (  # noqa: E402
    Baseline,
    Overflow,
    ScopedVisitor,
    Stale,
    overflows,
    run_report,
    stale_entries,
    stale_lines,
)
from regex_baseline import GRANDFATHERED_REGEX  # noqa: E402

#: The modules whose calls build or apply a regular expression.
REGEX_MODULES = frozenset({"re", "regex"})

#: The functions of those modules that take a pattern. `prefixmatch` is the
#: name Python 3.15 gives `match`.
PATTERN_FUNCTIONS = frozenset(
    {
        "compile",
        "search",
        "match",
        "prefixmatch",
        "fullmatch",
        "sub",
        "subn",
        "split",
        "findall",
        "finditer",
    }
)

#: How a reason comment starts, after its `#`.
REASON_TAG = "regex:"

#: Modules that already read a format this repository holds. Each is the one
#: reading of its format, so a new reader of that text calls it rather than
#: matching the text again. `tests/unit/test_regex_check.py` imports each, so
#: a renamed module fails a test instead of leaving `GUIDANCE` pointing at
#: nothing.
KNOWN_READERS: tuple[tuple[str, str], ...] = (
    ("docket.model", "an item file and its front matter"),
    ("docket.frontmatter", "the front matter of a rule or skill file"),
    ("docket.markdown", "the blocks of a Markdown document"),
    ("docket.fences", "a fenced block in Markdown"),
    ("docket.shell", "the words of a shell command"),
    ("docket.python", "Python source, one statement at a time"),
    ("docket.roadmap", "the tables and milestones in ROADMAP.md"),
    ("docket.digits", "a whole number written in digits"),
    ("docket.release", "a release version such as v0.7.0"),
    ("docket.store", "an item id"),
)

_READER_LINES = "\n".join(f"     - `{module}` reads {what}." for module, what in KNOWN_READERS)

#: What a session reads when this check or the edit hook stops it.
GUIDANCE = f"""\
Stop before writing this regular expression. Each one in this repository needs
a written reason, because regular expressions have caused repeated defects here.

  1. Say in one sentence what the code has to recognise or change.
  2. Check whether the repository already reads this text. Call the module that
     owns the format rather than matching the text a second time:
{_READER_LINES}
  3. Check for a parser of the format: `ast` or `tokenize` for Python, `tomllib`
     for TOML, `json`, `shlex` for shell words, `urllib.parse` for URLs,
     `datetime.fromisoformat` or `strptime` for dates, `html.parser` for HTML,
     and `pathlib` or `fnmatch` for paths and globs.
  4. Check whether a string method does it: `in`, `startswith`, `endswith`,
     `partition`, `split`, `removeprefix`, `replace` or `translate`.
  5. Where the format or library is unfamiliar, read its specification or
     documentation before choosing. Python's Regular Expression HOWTO, section
     "Use string methods", is the starting point:
     https://docs.python.org/3/howto/regex.html

A regular expression is the right tool when no parser reads the format and the
pattern is flat: a token with a fixed shape, a search through free prose, or a
lexer's table of tokens. Nested or quoted structure, such as Markdown, YAML,
TOML, HTML, shell or Python, wants a parser. Where the regular expression is
still the right tool:

  - Write a comment that starts with `# {REASON_TAG}` and says what the pattern
    matches and why no parser, existing reader or string method fits. Put it
    on the line above the statement, or at the end of one of its lines.
  - Compile it once, at module level, under a name that says what it matches.
  - Use `fullmatch` to test a whole value, so that a prefix cannot pass.
  - Use `re.VERBOSE` with comments for anything longer than a short token.
  - Avoid a repeated group that itself repeats, such as `(a+)+`, which can take
    exponential time on text that almost matches.
  - Test text it must accept and text it must refuse."""


class Use(NamedTuple):
    """One call that builds or applies a regular expression."""

    #: The line the call starts on.
    line: int
    #: The dotted name of the function or class around the call, or `<module>`.
    scope: str
    #: The function called, such as `compile`.
    function: str
    #: The call as `ast.unparse` writes it, which ignores layout and comments.
    text: str
    #: Whether a `regex:` comment gives a reason for it.
    reasoned: bool


def _reason_lines(source: str) -> set[int]:
    """Return the line numbers that hold a comment starting with `regex:` and a reason."""

    lines = set()

    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type != tokenize.COMMENT:
            continue

        for part in token.string.split("#"):
            text = part.strip()

            if text.startswith(REASON_TAG) and text[len(REASON_TAG) :].strip():
                lines.add(token.start[0])

    return lines


def _comment_block_above(source_lines: Sequence[str], first: int) -> range:
    """Return the line numbers of the comment-only lines directly above line `first`."""

    top = first

    while top > 1 and source_lines[top - 2].lstrip().startswith("#"):
        top -= 1

    return range(top, first)


class _Finder(ScopedVisitor):
    """Collect each call of a pattern function, with its scope and its statement."""

    def __init__(self, modules: set[str], functions: dict[str, str]) -> None:
        super().__init__()
        self.modules = modules
        self.functions = functions
        self.statements: list[ast.stmt] = []
        self.found: list[tuple[ast.Call, str, str, ast.stmt]] = []

    def visit(self, node: ast.AST) -> object:
        if not isinstance(node, ast.stmt):
            return super().visit(node)

        self.statements.append(node)

        try:
            return super().visit(node)
        finally:
            self.statements.pop()

    def visit_Call(self, node: ast.Call) -> None:
        function = self._pattern_function(node.func)

        if function is not None and self.statements:
            scope = ".".join(self.scope) or "<module>"
            self.found.append((node, scope, function, self.statements[-1]))

        self.generic_visit(node)

    def _pattern_function(self, func: ast.expr) -> str | None:
        if (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id in self.modules
            and func.attr in PATTERN_FUNCTIONS
        ):
            return func.attr

        if isinstance(func, ast.Name):
            return self.functions.get(func.id)

        return None


def uses(source: str) -> list[Use]:
    """Return each call in `source` that builds or applies a regular expression.

    Raises `SyntaxError` where `source` does not parse, so a caller can say it
    could not read the file rather than report it clean.
    """

    tree = ast.parse(source)
    modules: set[str] = set()
    functions: dict[str, str] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(
                alias.asname or alias.name for alias in node.names if alias.name in REGEX_MODULES
            )
        elif isinstance(node, ast.ImportFrom) and node.module in REGEX_MODULES:
            functions.update(
                (alias.asname or alias.name, alias.name)
                for alias in node.names
                if alias.name in PATTERN_FUNCTIONS
            )

    if not modules and not functions:
        return []

    finder = _Finder(modules, functions)
    finder.visit(tree)
    reasons = _reason_lines(source)
    source_lines = split_lines(source)
    found = []

    for call, scope, function, statement in finder.found:
        first = statement.lineno
        last = call.end_lineno or call.lineno
        covered = set(range(first, last + 1)) | set(_comment_block_above(source_lines, first))
        found.append(Use(call.lineno, scope, function, ast.unparse(call), bool(covered & reasons)))

    return found


def added_uses(before: str, after: str) -> list[Use]:
    """Return the calls without a reason that `after` holds and `before` did not.

    A call is the same call when `ast.unparse` writes it the same way, so
    moving or reformatting one adds nothing, and changing its pattern adds one.
    Raises `SyntaxError` where either text does not parse.
    """

    earlier = Counter(use.text for use in uses(before) if not use.reasoned)
    added = []

    for use in uses(after):
        if use.reasoned:
            continue

        if earlier[use.text]:
            earlier[use.text] -= 1
        else:
            added.append(use)

    return added


def describe(use: Use, limit: int = 100) -> str:
    """Return one line naming a call, shortened to `limit` characters."""

    text = use.text if len(use.text) <= limit else use.text[: limit - 3] + "..."
    return f"line {use.line}, in {use.scope}: {text}"


@dataclass
class Report:
    """What the check found across the tree."""

    over: list[Overflow[Use]] = field(default_factory=list)
    stale: list[Stale] = field(default_factory=list)
    unread: list[tuple[str, str]] = field(default_factory=list)
    files: int = 0
    reasoned: int = 0
    allowed: int = 0

    @property
    def errors(self) -> int:
        return (
            sum(len(entry.found) - entry.allowed for entry in self.over)
            + len(self.stale)
            + len(self.unread)
        )


def _sites(root: Path, paths: Iterable[Path]) -> Iterator[tuple[str, list[Use] | None, str]]:
    """Yield each file's relative path, its calls, and why it could not be read."""

    for path in paths:
        relative = path.relative_to(root).as_posix()

        try:
            yield relative, uses(path.read_text(encoding="utf-8")), ""
        except (SyntaxError, UnicodeDecodeError, ValueError) as error:
            yield relative, None, f"{type(error).__name__}: {error}"


def analyze(root: Path, baseline: Baseline = GRANDFATHERED_REGEX) -> Report:
    """Check every tracked Python file under `root` against `baseline`."""

    report = Report(allowed=sum(sum(entries.values()) for entries in baseline.values()))
    sites: dict[tuple[str, tuple[str, str]], list[Use]] = {}
    found: dict[str, Counter[tuple[str, str]]] = {}

    try:
        paths = tracked_under(root, "", ".py")
    except Unlisted as error:
        report.unread.append((".", str(error)))
        return report

    for relative, file_uses, problem in _sites(root, paths):
        report.files += 1

        if file_uses is None:
            report.unread.append((relative, problem))
            continue

        for use in file_uses:
            if use.reasoned:
                report.reasoned += 1
                continue

            key = (use.scope, use.function)
            sites.setdefault((relative, key), []).append(use)
            found.setdefault(relative, Counter())[key] += 1

    report.over = overflows(sorted(sites.items()), baseline)
    unread = {path for path, _ in report.unread}
    report.stale = stale_entries(root, baseline, found, unread)
    return report


def format_report(report: Report) -> str:
    """Return the report a session reads, with `GUIDANCE` where something new was found."""

    lines = [
        f"regex_check: {report.files} Python files read, {report.reasoned} regular "
        f"expressions with a reason, {report.allowed} without one allowed by the baseline, "
        f"{report.errors} errors"
    ]

    if report.over:
        lines += ["", "Regular expressions with no `regex:` reason beside them:"]

        for entry in report.over:
            lines.append(
                f"  {entry.path}: {len(entry.found)} {entry.key[1]} call(s) in {entry.key[0]}, "
                f"and the baseline allows {entry.allowed}"
            )
            lines += [f"    {describe(use)}" for use in entry.found]

        lines += ["", GUIDANCE, "", "The baseline does not grow."]

    lines += stale_lines(report.stale, lambda key: f"{key[1]} in {key[0]}")

    if report.unread:
        lines += [
            "",
            "Could not read, so this check cannot vouch for them. Run it under the "
            "project's interpreter, `uv run python tools/regex_check.py`:",
        ]
        lines += [f"  {path}: {problem}" for path, problem in report.unread]

    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    return run_report(argv, __doc__ or "", analyze, format_report)


if __name__ == "__main__":
    sys.exit(main())
