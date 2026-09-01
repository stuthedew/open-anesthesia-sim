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

Three checks, matching that subproject's: the formatter target agrees with the
declared floor, every file here parses at it, and nothing here imports a
package that exists only inside the project virtualenv. The pinned target is
what removes the syntax hazard; these tests are what notice if the pin is lost,
or if an import reaches past what a bare checkout holds.
"""

from __future__ import annotations

import ast
import re
import sys
import tomllib
from collections.abc import Iterator
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
SOURCES = sorted(TOOLS_ROOT.rglob("*.py"))

#: Importable here despite not being in the standard library, because a bare
#: checkout carries it too. `tools/doc_check.py` reads the release-train
#: grammar and the tag list from `docket`, in-tree under
#: `subprojects/docket/src` and itself standard-library-only, by inserting that
#: path rather than by installing anything. Anything else added to this set
#: has to meet the same bar: present in a fresh clone, and no dependencies of
#: its own outside the standard library.
VENDORED = frozenset({"docket"})


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


def _imported_roots(tree: ast.Module) -> Iterator[str]:
    """The top-level module name of every absolute import in `tree`.

    `import a.b` and `from a.b import c` both reach `a`, which is the name that
    has to be resolvable; the submodule cannot be present without it. Relative
    imports are skipped: `tools/` is a directory of scripts with no package
    around them, so a relative import there resolves to nothing and fails on
    the first run rather than only in a bare checkout, which is the failure
    this test exists to catch.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            yield (node.module or "").split(".")[0]


def test_no_tool_imports_outside_the_standard_library() -> None:
    """The no-dependency promise is what lets a bare checkout run these.

    `make check` ends with `python3 tools/doc_check.py check` under whatever
    interpreter is on PATH, with no virtualenv and no install step, so an
    import satisfied only by `uv sync` turns that line into a
    `ModuleNotFoundError` in a file the whole suite has just passed - the
    import twin of the `SyntaxError` above.

    `sys.stdlib_module_names` rather than a hand-written allowlist: it is a
    frozenset the interpreter maintains, so nothing here goes stale as the
    standard library grows. Its one bound is that it answers for the
    interpreter running this test - the project virtualenv, on the version
    `pyproject.toml` pins - and not for the floor. A module added to the
    standard library after the floor is therefore allowed here and absent
    there; `annotationlib` and `compression` are the live examples at 3.14
    against a 3.11 floor. That direction is narrow and the reverse fails
    safe, but it is the gap this check does not close.
    """
    allowed = sys.stdlib_module_names | VENDORED

    for path in SOURCES:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for root in _imported_roots(tree):
            assert root in allowed, (
                f"{path.relative_to(REPO_ROOT)} imports '{root}', which is neither in the "
                f"standard library nor in-tree; `python3 {path.relative_to(REPO_ROOT)}` "
                "cannot run in a checkout with no virtualenv"
            )
