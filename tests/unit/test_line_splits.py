"""No reader in the apparatus splits text with `str.splitlines()`.

`splitlines()` breaks at `\\x0b`, `\\x0c`, `\\x1c`-`\\x1e`, `\\x85`, U+2028 and
U+2029 as well as at a newline, and no format these trees read ends a line
there: git's records, a JSON-lines transcript, the item-read log and Python
source all end one at `\\n` once Python has decoded the text. Four sessions
reached for it at four readers and each read one record as two (`PL-139L`,
`PL-PK4B`, `PL-K1D6`, `PL-LRBV`, under the head `PL-4YVK`). Converting those four
left every next reader free to pick it again, so this refuses the call itself:
`docket.lines.split_lines` is the replacement, or `str.split("\\n")` and
`str.partition("\\n")` in a tool that does not import docket.

The rule is the call, read from the syntax tree, so a docstring or comment
naming `splitlines()` is not one.
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

#: The trees whose readers this holds: every reader `PL-4YVK` counted.
TREES = ("tools", "subprojects/docket/src/docket", ".claude/hooks")

#: The Markdown readers, exempt until `PL-BBYJ` converts them together. They
#: read CommonMark, which ends no line at those characters either, but their
#: line indices pair with `docket/fences.py`'s, so converting one file alone
#: would leave two readers of one document disagreeing on which line is which.
#: A file, not a call, so a rewrite such as `#1358` (`PL-R417`'s Markdown
#: readers) cannot make this list stale; it took the last call out of
#: `tools/core_vocabulary_check.py`, which the test below caught.
MARKDOWN_READERS = frozenset(
    {
        "subprojects/docket/src/docket/checks.py",
        "subprojects/docket/src/docket/fences.py",
        "subprojects/docket/src/docket/instructions.py",
        "subprojects/docket/src/docket/notes.py",
        "subprojects/docket/src/docket/render.py",
        "subprojects/docket/src/docket/roadmap.py",
        "tools/dead_ends.py",
        "tools/doc_check.py",
    }
)


def splitlines_calls(source: str) -> list[int]:
    """The line of every `.splitlines(...)` call in one module."""
    return [
        node.lineno
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "splitlines"
    ]


def calls_by_file() -> dict[str, list[int]]:
    found: dict[str, list[int]] = {}
    for tree in TREES:
        for path in sorted((REPO_ROOT / tree).rglob("*.py")):
            lines = splitlines_calls(path.read_text(encoding="utf-8"))
            if lines:
                found[path.relative_to(REPO_ROOT).as_posix()] = lines
    return found


def test_the_rule_reads_a_call_and_not_a_mention() -> None:
    source = '"""`text.splitlines()` in prose."""\n# and .splitlines() here\nx = "a".splitlines()\n'
    assert splitlines_calls(source) == [3]


def test_no_reader_outside_the_markdown_readers_calls_splitlines() -> None:
    offenders = [
        f"{path}:{line}"
        for path, lines in calls_by_file().items()
        if path not in MARKDOWN_READERS
        for line in lines
    ]
    assert not offenders, (
        "str.splitlines() also breaks at \\x0b, \\x0c, \\x1c-\\x1e, \\x85, U+2028 and U+2029, "
        "where no format read here ends a line; split with docket.lines.split_lines, or "
        'str.split("\\n") in a tool that does not import docket (PL-4YVK): ' + ", ".join(offenders)
    )


def test_every_exempt_file_still_needs_its_exemption() -> None:
    found = calls_by_file()
    spent = sorted(path for path in MARKDOWN_READERS if path not in found)
    assert not spent, f"no longer calls splitlines(), so drop it from MARKDOWN_READERS: {spent}"
