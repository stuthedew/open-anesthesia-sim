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

The `Makefile` exports `PYTHONDONTWRITEBYTECODE` to carry the same guard to its
recipes that are not pytest runs, such as `bin/docket check` under `make
docket`, which imports the `docket` package from source (`PL-01GD`). That line
shipped with no test, in a file nobody reads top to bottom, where a tidy
removes it without anything saying so (`PL-H9GV`). The last two tests hold it
the way a recipe meets it: a probe recipe, read after the `Makefile` from a
second `-f`, prints the variable as its own shell sees it, so a value `make`
holds without exporting it does not pass. This run exports the variable
itself, so the probe runs in an environment without it, and the same probe
without the `Makefile` is the control showing it did.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT_CONFTEST = Path(__file__).resolve().parents[2] / "conftest.py"
MAKEFILE = ROOT_CONFTEST.parent / "Makefile"

#: `$$` hands the recipe's shell the variable to expand, so the probe reads what
#: the recipe was exported rather than a value `make` holds and never passes on.
_PROBE = 'probe-bytecode-guard:\n\t@printf "%s\\n" "$$PYTHONDONTWRITEBYTECODE"\n'

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


def _seen_by_a_recipe(*makefiles: Path) -> str:
    """What a recipe's shell reads for `PYTHONDONTWRITEBYTECODE`, read after these makefiles.

    The environment drops the variable, which this run exports, and every
    `MAKE*` variable, which an enclosing `make check` would pass down - among
    them `MAKEFILES`, which names makefiles to read before any `-f`.
    """
    make = shutil.which("make")
    assert make is not None, "no `make` on PATH, so no recipe exists to read the variable from"
    environment = {
        name: value
        for name, value in os.environ.items()
        if name != "PYTHONDONTWRITEBYTECODE" and not name.startswith(("MAKE", "MFLAGS"))
    }
    files = [argument for makefile in makefiles for argument in ("-f", str(makefile))]
    result = subprocess.run(
        [make, "--silent", *files, "-f", "-", "probe-bytecode-guard"],
        input=_PROBE,
        cwd=MAKEFILE.parent,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"make could not run the probe: {result.stderr}"
    return result.stdout.strip()


def test_without_the_makefile_a_recipe_sees_no_bytecode_setting() -> None:
    assert _seen_by_a_recipe() == ""


def test_the_makefile_turns_bytecode_writing_off_for_its_recipes() -> None:
    assert _seen_by_a_recipe(MAKEFILE) == "1"
