"""The one shell reader the guard hooks and docket share: what a guard's import of it costs.

Every Bash call runs four PreToolUse guards, each a fresh `python3` that
imports `.claude/hooks/shell_split.py`, and that module reads a command through
docket's `subprojects/docket/src/docket/shell.py`, putting docket's `src` on
`sys.path` from its own place (`PL-JNYL`). Two failures would pass every other
test here unseen. A guard whose import fails passes every command, as each
hook's header says, and the guard suites run the hooks in a child process where
pytest's `pythonpath` does not reach, so a broken path turns each refusal they
pin into a pass - which only this file names as the cause. And an import that
loads `dataclasses`, `inspect`, `pathlib` or `typing` again slows every Bash
call by several milliseconds per guard with nothing failing. Measured on
2026-10-10 with `python3 -X importtime`, medians of nine after the guards' own
imports: `shell_split` with its own lexer cost 5.3 ms under python3 3.11.17
and 5.5 ms under 3.13.16, `docket` and `docket.shell` as they stood would have
added 19.7 and 23.0, and the reader importing only the modules below costs 1.3
and 2.0. A timing would be the direct test and a flaky one; the module set is
its deterministic half.

The interpreter is the bare `python3` on PATH that `.claude/settings.json` runs
each guard with, isolated (`-I`) so that no `PYTHONPATH` stands in for the path
the module finds itself, and run from a directory outside the repository.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
import shell_split
from docket import shell

REPO = Path(__file__).resolve().parents[2]
HOOKS = REPO / ".claude" / "hooks"

#: What each guard imports before `shell_split`, as its own first line does.
GUARD_IMPORTS = "import json, os, re, sys"

#: The modules a guard's import of `shell_split` may add to those.
LOADED = ["docket", "docket.shell", "shell_split"]


def _bare(script: str, cwd: Path) -> str:
    """What `script` prints, run by the bare `python3` a guard runs, isolated, from `cwd`."""
    python = shutil.which("python3")
    assert python, "no python3 on PATH, which every guard hook runs"
    done = subprocess.run(
        [python, "-I", "-c", f"{GUARD_IMPORTS}\nsys.path.insert(0, {str(HOOKS)!r})\n{script}"],
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=20,
        check=False,
    )
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


def test_a_guard_finds_docket_s_lexer_from_a_bare_interpreter(tmp_path: Path) -> None:
    """`shell_split` reaches `subprojects/docket/src` from its own place, whatever the cwd."""
    found = _bare("import shell_split, docket.shell\nprint(docket.shell.__file__)", tmp_path)

    assert Path(found) == REPO / "subprojects" / "docket" / "src" / "docket" / "shell.py"


def test_a_guard_s_import_loads_only_the_reader_and_docket_s_lexer(tmp_path: Path) -> None:
    """`PL-JNYL`: nothing a guard has not already loaded, but the reader and its lexer."""
    loaded = _bare(
        "before = set(sys.modules)\nimport shell_split\n"
        "print(' '.join(sorted(set(sys.modules) - before)))",
        tmp_path,
    )

    assert loaded.split() == LOADED


@pytest.mark.parametrize("operator", sorted(shell.OPERATORS))
def test_the_hooks_read_the_one_operators_table(operator: str) -> None:
    """`PL-P72R`: docket's `OPERATORS` is the only spelling, and the hooks read each one whole.

    `shell_split` held a table of its own, which differed from docket's by
    `<<-` until `PL-Q9LK`, and nothing held the two together.
    """
    tokens = shell_split.words(f"a {operator} b")

    assert not hasattr(shell_split, "OPERATORS")
    assert tokens == ["a", operator, "b"]
    assert isinstance(tokens[1], shell_split.Operator)
