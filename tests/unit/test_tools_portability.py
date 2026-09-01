"""`tools/` must stay runnable by the interpreter that actually runs it.

`make check` invokes `python3 tools/doc_check.py check` with whatever bare
`python3` is on PATH - no virtualenv, no install step - and CI does the same.
This suite, by contrast, runs under the project virtualenv on the version
`pyproject.toml` requires, so a tool that has become unparseable by the older
interpreter passes every test and fails only at the end of `make check`, with a
`SyntaxError` in a file nothing appeared to have touched.

That is not hypothetical. The repository targets 3.14, where PEP 758 makes the
parentheses in `except (OSError, TimeoutError):` redundant; `ruff format` at
that target removes them, and 3.11 cannot parse the result.
`subprojects/docket/` was broken this exact way once and now carries its own
`ruff.toml` and `tests/test_portability.py`. `tools/` makes the same promise
and, until this file, had the same exposure with the guard written for one file
and one construct.

Two halves, matching that subproject's: the formatter target agrees with the
declared floor, and every file here parses at it. The pinned target is what
removes the hazard; these tests are what notice if the pin is lost.
"""

from __future__ import annotations

import ast
import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
SOURCES = sorted(TOOLS_ROOT.rglob("*.py"))


def _bare_python_floor() -> tuple[int, int]:
    """The oldest interpreter anything under `tools/` may assume.

    Read from `subprojects/docket/pyproject.toml` rather than declared again
    here: `tools/doc_check.py` imports `docket.roadmap`, so the interpreter that
    can run the tools is exactly the interpreter that can run that package.
    Raising the floor there raises it here, and reading it is what keeps the two
    from drifting apart the way the guard itself did.
    """
    with (REPO_ROOT / "subprojects" / "docket" / "pyproject.toml").open("rb") as handle:
        requires = tomllib.load(handle)["project"]["requires-python"]
    match = re.search(r">=\s*(\d+)\.(\d+)", requires)
    assert match is not None, requires
    return int(match.group(1)), int(match.group(2))


def _ruff_target() -> tuple[int, int]:
    """The Python version the formatter may emit syntax for under `tools/`."""
    with (TOOLS_ROOT / "ruff.toml").open("rb") as handle:
        target = tomllib.load(handle)["target-version"]
    match = re.fullmatch(r"py(\d)(\d+)", target)
    assert match is not None, target
    return int(match.group(1)), int(match.group(2))


def test_the_formatter_target_matches_the_declared_floor() -> None:
    """A formatter aimed past the floor rewrites the source into syntax it cannot run."""
    assert _ruff_target() == _bare_python_floor()


def test_there_are_sources_to_check() -> None:
    assert SOURCES, "no tools found; the glob is wrong"


def test_every_tool_parses_under_the_interpreter_that_actually_runs_it() -> None:
    """Every file under `tools/`, not the one that broke.

    `feature_version` is not a full older-interpreter parser - it gates the
    syntax CPython's own parser version-checks, PEP 758 among them - so this
    catches the rewrite that has actually happened here rather than proving
    compatibility in general.
    """
    floor = _bare_python_floor()

    for path in SOURCES:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path), feature_version=floor)
