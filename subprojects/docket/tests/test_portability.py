"""The package must stay runnable by the interpreter that actually runs it.

The session-start hook invokes this package with whatever bare `python3` is on
PATH - no virtualenv, no install step - which is the whole reason it depends
on nothing outside the standard library. That promise is easy to break
silently, and it was broken once: the repository around this package targets a
newer Python, and a formatter set to that target rewrote
`except (OSError, TimeoutError):` into PEP 758's unparenthesized form, which
older interpreters cannot parse. The hook discards errors by design, so the
only symptom was a digest that quietly stopped appearing.

These tests hold the two halves of that promise: the declared floor and the
tooling target agree, and nothing here imports a third-party package. A third
holds what happens below the floor: the command says so in one line.
"""

from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
SOURCES = sorted((PACKAGE_ROOT / "src" / "docket").glob("*.py"))

#: Modules the package is allowed to import. Standard library only.
ALLOWED_IMPORTS = {
    "argparse",
    "ast",
    "collections",
    "collections.abc",
    "concurrent",
    "dataclasses",
    "datetime",
    "locale",
    "os",
    "pathlib",
    "random",
    "re",
    "shlex",
    "statistics",
    "subprocess",
    "sys",
    "tempfile",
    "time",
    "tomllib",
    "typing",
    "unicodedata",
    "warnings",
    "__future__",
    "docket",
}


def _floor() -> tuple[int, int]:
    """The oldest Python this package claims to support."""
    with (PACKAGE_ROOT / "pyproject.toml").open("rb") as handle:
        requires = tomllib.load(handle)["project"]["requires-python"]
    match = re.search(r">=\s*(\d+)\.(\d+)", requires)
    assert match is not None, requires
    return int(match.group(1)), int(match.group(2))


def _ruff_target() -> tuple[int, int]:
    """The Python version the formatter is allowed to emit syntax for."""
    with (PACKAGE_ROOT / "ruff.toml").open("rb") as handle:
        target = tomllib.load(handle)["target-version"]
    match = re.fullmatch(r"py(\d)(\d+)", target)
    assert match is not None, target
    return int(match.group(1)), int(match.group(2))


def test_the_formatter_target_matches_the_declared_floor() -> None:
    """A formatter aimed past the floor rewrites the source into syntax it cannot run."""
    assert _ruff_target() == _floor()


def test_there_are_sources_to_check() -> None:
    assert SOURCES, "no package sources found; the glob is wrong"


def test_every_module_parses() -> None:
    for path in SOURCES:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_nothing_imports_outside_the_standard_library() -> None:
    """The no-dependency promise is what lets a bare checkout run this."""
    for path in SOURCES:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [(node.module or "").split(".")[0]] if node.level == 0 else []
            else:
                continue
            for name in names:
                assert name in ALLOWED_IMPORTS, f"{path.name} imports '{name}'"


def test_an_interpreter_below_the_floor_names_the_floor_and_itself() -> None:
    """Below the floor, `python -m docket` says so in one line and exits non-zero (`PL-LKGW`).

    CI has no interpreter that old, so a fresh one of this version stands in:
    `sys.version_info` is set one minor below the declared floor, and
    `docket.cli` is made unimportable, which is what an old interpreter does to
    it - 3.10 fails on its `from datetime import UTC`. A check that ran after
    that import would therefore fail here the way the item reproduced it, with
    a traceback, rather than pass. The floor is read from `pyproject.toml`, so
    `__main__.FLOOR` drifting either way from `requires-python` fails too.
    """
    major, minor = _floor()
    below = (major, minor - 1, 12, "final", 0)
    script = "\n".join(
        (
            "import runpy, sys",
            f"sys.version_info = {below!r}",
            "sys.modules['docket.cli'] = None",
            "runpy.run_module('docket', run_name='__main__', alter_sys=True)",
        )
    )
    env = {**os.environ, "PYTHONPATH": str(PACKAGE_ROOT / "src")}
    done = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, env=env, text=True, check=False
    )

    assert done.returncode != 0
    assert done.stdout == ""
    assert done.stderr == (
        f"docket needs Python {major}.{minor} or newer; "
        f"this is Python {major}.{minor - 1}.12, at {sys.executable}\n"
    )
