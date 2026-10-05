"""No reader in the apparatus splits text with `str.splitlines()`.

`splitlines()` breaks at `\\x0b`, `\\x0c`, `\\x1c`-`\\x1e`, `\\x85`, U+2028 and
U+2029 as well as at a newline, and no format these trees read ends a line
there: git's records, a JSON-lines transcript, the item-read log and Python
source all end one at `\\n` once Python has decoded the text, and so do
Markdown, YAML and a Makefile (`docket.lines` names the specifications). Four
sessions reached for it at four readers and each read one record as two
(`PL-139L`, `PL-PK4B`, `PL-K1D6`, `PL-LRBV`, under the head `PL-4YVK`).
Converting those four left every next reader free to pick it again, so this
refuses the call itself: `docket.lines.split_lines` is the replacement, or
`str.split("\\n")` and `str.partition("\\n")` in a tool that does not import
docket. The Markdown readers were exempt until `PL-BBYJ` converted them
together, because their line indices pair with `docket/fences.py`'s; no file
is exempt now.

The rule is the call, read from the syntax tree, so a docstring or comment
naming `splitlines()` is not one.

**The decoding half** (`PL-0R4M`). A `subprocess` call that turns text mode on -
`text=`, `universal_newlines=`, `encoding=` or `errors=` - translates `\\r\\n`
and a lone `\\r` into `\\n` before any split sees the output, so a commit
subject holding a raw `\\r` read as two lines however it was split afterwards.
So a runner reads bytes, decodes git's own records with
`docket.lines.record_text` and translates only file content with `file_text`,
and a call that turns text mode on is refused unless `TEXT_MODE_RUNNERS` names
it with its reason. It reads `.py` files, so the Python embedded in
`.claude/hooks/push-check-guard.sh` is outside its reach; that file's reads are
`rev-parse` paths and `status --porcelain` without `-z`, which git C-quotes, so
no raw `\\r` reaches them.
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

#: The trees whose readers this holds: every reader `PL-4YVK` counted.
TREES = ("tools", "subprojects/docket/src/docket", ".claude/hooks")


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


def test_no_reader_calls_splitlines() -> None:
    offenders = [f"{path}:{line}" for path, lines in calls_by_file().items() for line in lines]
    assert not offenders, (
        "str.splitlines() also breaks at \\x0b, \\x0c, \\x1c-\\x1e, \\x85, U+2028 and U+2029, "
        "where no format read here ends a line; split with docket.lines.split_lines, or "
        'str.split("\\n") in a tool that does not import docket (PL-4YVK): ' + ", ".join(offenders)
    )


# --- The decoding half: no runner turns text mode on unasked (`PL-0R4M`).

#: The `subprocess` functions that take text mode's keywords.
SUBPROCESS_RUNNERS = frozenset({"run", "Popen", "check_output", "check_call", "call"})

#: The keywords any one of which turns text mode on, and its newline translation.
TEXT_MODE_KEYWORDS = frozenset({"text", "universal_newlines", "encoding", "errors"})

#: The calls left in text mode, each with why: none reads a git record that can
#: hold a raw `\r`, so the translation costs none of them a line.
TEXT_MODE_RUNNERS: dict[tuple[str, str], str] = {
    (
        "subprojects/docket/src/docket/cli.py",
        "_run_forge_command",
    ): "runs a project's configured forge command, whose answer is the forge's, not git's",
    (
        "subprojects/docket/src/docket/verify.py",
        "_run",
    ): "runs recorded shell commands, and its git reads print hashes, C-quoted paths, "
    "blobs and patches",
    ("tools/doc_check.py", "measure_digest"): "runs the session-start hook under bash to size it",
    ("tools/ignore_check.py", "run_mypy"): "runs mypy, whose report is its own and not git's",
}


def text_mode_calls(source: str) -> list[tuple[str, int]]:
    """Each `subprocess` call in one module that turns text mode on: its function and line.

    The function is the innermost `def` enclosing the call, or `<module>`. A
    keyword passed as the constant `False` or `None` leaves text mode off, so
    only another value counts.
    """
    found: list[tuple[str, int]] = []

    def visit(node: ast.AST, owner: str) -> None:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            owner = node.name
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "subprocess"
            and node.func.attr in SUBPROCESS_RUNNERS
            and any(
                keyword.arg in TEXT_MODE_KEYWORDS
                and not (
                    isinstance(keyword.value, ast.Constant) and keyword.value.value in (False, None)
                )
                for keyword in node.keywords
            )
        ):
            found.append((owner, node.lineno))
        for child in ast.iter_child_nodes(node):
            visit(child, owner)

    visit(ast.parse(source), "<module>")
    return found


def text_mode_calls_by_file() -> dict[str, list[tuple[str, int]]]:
    found: dict[str, list[tuple[str, int]]] = {}
    for tree in TREES:
        for path in sorted((REPO_ROOT / tree).rglob("*.py")):
            calls = text_mode_calls(path.read_text(encoding="utf-8"))
            if calls:
                found[path.relative_to(REPO_ROOT).as_posix()] = calls
    return found


def test_the_text_mode_rule_reads_the_keyword_and_not_a_mention() -> None:
    source = (
        '"""`subprocess.run(args, text=True)` in prose."""\n'
        "import subprocess\n"
        "def counted():\n"
        "    subprocess.run(['git'], text=True)\n"
        "def also_counted():\n"
        "    subprocess.Popen(['git'], encoding='utf-8')\n"
        "def not_counted():\n"
        "    subprocess.run(['git'], text=False, capture_output=True)\n"
        "    subprocess.check_output(['git'], errors=None)\n"
    )
    assert text_mode_calls(source) == [("counted", 4), ("also_counted", 6)]


def test_no_subprocess_call_turns_text_mode_on_outside_its_exemptions() -> None:
    offenders = [
        f"{path}:{line} ({owner})"
        for path, calls in text_mode_calls_by_file().items()
        for owner, line in calls
        if (path, owner) not in TEXT_MODE_RUNNERS
    ]
    assert not offenders, (
        "text mode translates \\r\\n and a lone \\r into \\n before any split, so a raw \\r in a "
        "commit subject, a body or a -z path reads as a line end; read bytes and decode git's "
        "records with docket.lines.record_text, translating file content - a blob or a patch - "
        "with file_text, or list a runner that reads no git in TEXT_MODE_RUNNERS with its "
        "reason (PL-0R4M): " + ", ".join(offenders)
    )


def test_every_text_mode_exemption_is_still_needed() -> None:
    found = {
        (path, owner) for path, calls in text_mode_calls_by_file().items() for owner, _ in calls
    }
    spent = sorted(key for key in TEXT_MODE_RUNNERS if key not in found)
    assert not spent, f"no longer turns text mode on, so drop it from TEXT_MODE_RUNNERS: {spent}"
