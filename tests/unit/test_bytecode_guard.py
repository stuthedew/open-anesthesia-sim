"""Hold the root `conftest.py` to writing no bytecode, and show what it guards.

`conftest.py` turns bytecode writing off for every pytest run, because CPython
accepts a cached `.pyc` whose recorded source size and whole-second mtime
match, so an equal-length edit reverted inside one second keeps running from
the cache (`PL-0MLZ`; the mechanism is in that file's docstring). The cycle
below makes that deterministic rather than a race: it pins the mutated and the
restored file's mtimes into one whole second with `os.utime`, where a real
mutation test lands there only when it runs fast enough - 11 times in 12,
measured.

Each import runs in a fresh interpreter started with `-E`, which ignores every
`PYTHON*` variable. That matters under `make check`, whose recipes export
`PYTHONDONTWRITEBYTECODE`: without `-E` the unguarded run would inherit it and
stop demonstrating anything, and the guarded run would pass whether or not the
root `conftest.py` did its job.

The unguarded case asserts CPython's own behaviour. If it ever fails, the
interpreter has stopped serving a same-second cache, and the guard may no
longer be needed - which is worth knowing, rather than a reason to delete it.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT_CONFTEST = Path(__file__).resolve().parents[2] / "conftest.py"

#: One whole second well in the past, so neither write lands on "now".
_SECOND = 1_700_000_000


def _value_after_import(directory: Path, *, guarded: bool) -> str:
    """What `pinned.VALUE` reads in a fresh interpreter, run after the root conftest or not."""
    prelude = f"import runpy; runpy.run_path({str(ROOT_CONFTEST)!r}); " if guarded else ""
    code = (
        prelude
        + f"import sys; sys.path.insert(0, {str(directory)!r}); "
        + "import pinned; print(pinned.VALUE)"
    )
    result = subprocess.run(
        [sys.executable, "-E", "-c", code],
        cwd=directory,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _mutate_import_restore(directory: Path, *, guarded: bool) -> tuple[str, str]:
    """Mutate, import, restore inside one second and import again: what each import ran."""
    module = directory / "pinned.py"
    module.write_text("VALUE = 2\n")
    os.utime(module, (_SECOND + 0.1, _SECOND + 0.1))
    mutated = _value_after_import(directory, guarded=guarded)
    module.write_text("VALUE = 1\n")
    os.utime(module, (_SECOND + 0.6, _SECOND + 0.6))
    return mutated, _value_after_import(directory, guarded=guarded)


def test_this_run_writes_no_bytecode_and_neither_do_its_subprocesses() -> None:
    assert sys.dont_write_bytecode
    assert os.environ.get("PYTHONDONTWRITEBYTECODE") == "1"


def test_an_unguarded_interpreter_runs_the_mutation_after_a_same_second_restore(
    tmp_path: Path,
) -> None:
    assert _mutate_import_restore(tmp_path, guarded=False) == ("2", "2")
    assert (tmp_path / "__pycache__").is_dir()


def test_a_same_second_restore_runs_the_restored_source(tmp_path: Path) -> None:
    assert _mutate_import_restore(tmp_path, guarded=True) == ("2", "1")
    assert not (tmp_path / "__pycache__").exists()
