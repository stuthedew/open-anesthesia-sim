"""Mutation-test the functions a branch changes, and print the mutants that its tests miss.

A mutant is a copy of the code with one small fault in it, such as `+` in place
of `-` or `<` in place of `<=`. The tests kill a mutant when at least one of
them fails on it. A mutant that every test passes has survived, and it points at
a fault that the tests would not catch. This tool runs mutmut over the
functions that the current branch changes and prints each survivor with its
diff, so the question is asked at review while the change is fresh. The tool
itself exits 0 whatever survives. The project owner chose this over a mutation
score to reach (project owner, 2026-10-17, ratified, `PL-Y1PS`).

**`--verdict` is the one gate, and it is narrower than a score.** It prints, as
JSON, the mutants of the lines the branch changed that the tests did not catch,
and `docket verify` refuses the branch while there are any. A survivor on a line
the branch left alone is reported and not counted. This replaced verify's check
that no existing assertion was removed, which read the diff's text and was
waived about 15 times in 17 (project owner, 2026-10-19, ratified, over making
that check an advisory and over keeping it, `PL-CZXN`). `verdict` states the
rule.

**`--verdict` runs only the mutants that can change it** (`PL-88HC`). Before
mutmut runs, `listing` generates the mutants of the changed functions and
places each on its line, as `verdict` does. A mutant whose changed lines the
branch left alone is not run, and a note counts it. A mutant that cannot be
placed still runs, so it can still refuse the branch. A run without
`--verdict` still runs every mutant of each changed function, so a reviewer
still sees the survivors on its unchanged lines.

**`--verdict` also compares each changed simulator unit test with its base
version.** A mutant of the code cannot show that a branch weakened a test,
because the test is what changed. So `compare_tests` runs the mutants of the
display modules under `app/`, and of each `core/` module the test imports by
name, against the base version of each changed test and against the branch's
version. A mutant that only the base version catches goes into the same
`uncaught` list (project owner, 2026-10-24, ratified, over leaving those tests
unmeasured, `PL-7FPD` and `PL-H57W`). `compare_tests` says what it leaves out.

`--all` runs every mutant instead and prints the kill rate of each module.
`docs/mutation-testing.md` records the baseline that such a run measured, and
says how to read a survivor. mutmut is in the `mutation` dependency group, so
`make mutate` runs this tool through `uv run --group mutation`.

**mutmut takes its settings from `pyproject.toml`'s `[tool.mutmut]` table,**
which says why each one is set. This tool decides three things that the table
cannot.

- **Which tests run.** The table names an `@` file as the test selection, and
  pytest reads one path per line from it. This tool writes that file into
  `mutants/` before mutmut starts. It lists every test file under `tests/unit/`
  that imports the simulator, by the rule in `docket.arming` that
  `tools/workflow_paths_check.py` also applies. A test file of the tooling
  covers no simulator function, and many of them fail inside mutmut's copy of
  the tree. Integration and reference tests are left out because their
  24-hour runs would make the run take hours.
- **Which functions changed.** The diff runs from the commit where the branch
  forked from the default branch to the working tree, and includes files that
  git does not track yet. A function changed when a changed line falls inside
  it, decorators included. mutmut mutates top-level functions and the methods
  of top-level classes, so a change elsewhere, such as to a constant, is
  reported as a change outside any function.
- **What a "timeout" was.** mutmut runs a mutant's tests by their node ids,
  and pytest refuses the run when it cannot collect one of them. A mutant
  causes that when it raises while a test module is imported, or when it
  changes a test's parameters and so the test's id. mutmut then records exit
  status 255 and reports a timeout, though nothing timed out. This tool runs
  each such mutant's test files again, whole, and reports what they say. The
  files first run once with no mutant applied, and must pass.

**Every run starts with an empty `mutants/` directory.** mutmut keeps each
verdict until the source of the mutated function changes. A test added since
the last run would therefore never run against a mutant that it now kills, and
the old "survived" verdict would be reported again (mutmut 3.8.0,
`collect_or_load_stats` in `mutmut/__main__.py`). A fresh run costs about two
and a half minutes of coverage collection before the first mutant, which is
the price of an answer that is true.

Exits 0 when the run finished and its results were read, and 1 when they
could not be read: the base branch is unknown, mutmut failed, or the table is
missing.
"""

from __future__ import annotations

import argparse
import ast
import copy
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import TypeGuard

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.arming import TESTS, imports_product, is_test_file  # noqa: E402
from docket.lines import split_lines  # noqa: E402
from docket.vcs import (  # noqa: E402
    GitUnanswered,
    default_base,
    listed_paths,
    read_git,
    resolved,
    tracked_under,
    untracked_path_args,
)

import doc_check  # noqa: E402
from product_paths import PACKAGE  # noqa: E402

#: The directory mutmut copies the tree into and runs the tests in. mutmut
#: 3.8.0 fixes the name, relative to the directory it runs from.
MUTANTS = "mutants"
#: The test tree whose simulator tests run against each mutant.
UNIT_TESTS = "tests/unit"
#: mutmut's progress output, which this tool keeps out of its own report.
RUN_LOG = "diff_mutation.log"
#: What mutmut 3.8.0 says when no mutant matches the names it was given.
NOTHING_MATCHES = "Filtered for specific mutants, but nothing matches"
#: One line of `mutmut results --all true`: a mutant's name and its status.
RESULT_RE = re.compile(r"^\s+(\S+): (.+)$")
#: The exit status mutmut 3.8.0 records when its pytest run raised instead of
#: returning. Its worker catches the exception and exits with -1.
RAISED = 255
#: What a run of whole test files under one mutant says, by pytest's exit
#: status. Any other status, such as 2 for an interrupted run, is reported as
#: it is, because it says nothing about the mutant. A test module that raises
#: while it is imported is the exception, because pytest gives it status 2 as
#: well. `_pytest_in_mutants` reads that case from pytest's output instead.
RERUN_STATUS = {0: "survived", 1: "killed"}
#: pytest's exit status for an interrupted run, `ExitCode.INTERRUPTED`.
INTERRUPTED = 2
#: What pytest 9 prints, between rows of "!", when it ends a run because a test
#: module raised while it was collected: "Interrupted: 1 error during
#: collection". The files ran cleanly with no mutant applied first, so the
#: mutant caused the raise (`PL-N3YB`).
COLLECTION_ERROR_RE = re.compile(r"Interrupted: \d+ errors? during collection")
#: How long that run may take before its mutant is reported as a timeout.
RERUN_TIMEOUT_S = 900
#: Why a run whose results list is empty is refused rather than reported.
LISTING_UNREAD = (
    "Its output may have changed shape, and a report built from it would call every "
    "function untested."
)
#: The order the report counts statuses in. Others follow, sorted.
STATUS_ORDER = ("killed", "survived", "timeout", "no tests")
#: The last line of every report, because no run reaches the slower test trees.
TIERS_NOT_RUN = (
    "Integration and reference tests did not run against these mutants, so one of them may "
    'still catch a survivor. docs/mutation-testing.md, section "Second tier", says how to '
    "run a survivor against the whole suite."
)
#: The statuses that mean the tests caught a mutant. A timeout counts, as PIT
#: and Stryker count it, because the mutant made a test run past its limit.
#: mutmut reports "segfault" when a signal killed the test process, which a
#: reader sees as plainly as a failed test.
CAUGHT = frozenset({"killed", "timeout", "caught by type check", "segfault"})
#: The statuses that mean the tests did not catch a mutant: every test that
#: reaches its function passed, or no test reaches the function at all. Any
#: status in neither set is one this tool could not decide, such as
#: "unsettled" or mutmut's "suspicious".
MISSED = frozenset({"survived", "no tests"})
#: Why a changed function can have no mutants.
NO_MUTANTS = (
    "mutmut does not mutate a decorated function (other than a staticmethod or classmethod), "
    "__new__, __setattr__ or __getattribute__, and a function may hold nothing it can change."
)
#: How many names a note lists before it counts the rest.
NOTE_NAMES = 5
#: The package whose mutants measure every changed test. A test of what the
#: interface displays exists to catch a fault in the display code, so all of
#: these mutants run against the two versions of a changed test (`PL-7FPD`).
DISPLAY_PACKAGE = f"{PACKAGE}.app"
#: The package whose mutants measure a changed test only where it imports the
#: module by name. A test that builds a run reaches most of `core/`, and all of
#: those mutants would take 9 to 16 minutes for each version of the test, so
#: only the modules the test names run (`PL-H57W`).
CORE_PACKAGE = f"{PACKAGE}.core"
#: How long a run of a changed test's base version, with no mutant applied,
#: may take before the file is reported as not compared.
CLEAN_TIMEOUT_S = 900
#: The script `listing` runs to generate mutants without running any test, and
#: to print each listed mutant's diff, as JSON keyed by name. It calls the
#: steps mutmut 3.8.0's `run` takes before it collects coverage, which is the
#: slow part, and the function `mutmut show` prints from. They are mutmut's
#: internals rather than its command line, so the pinned version in
#: `pyproject.toml` is what keeps them. `listing` falls back to running every
#: mutant when the script fails.
LIST_SCRIPT = """
import fnmatch, json, shutil, sys
from pathlib import Path
from mutmut.__main__ import create_mutants
from mutmut.mutation.data import SourceFileMutationData
from mutmut.mutation.diff_apply import get_diff_for_mutant
from mutmut.mutation.trampoline import set_mutant_under_test
from mutmut.utils.file_utils import (
    copy_also_copy_files, copy_src_dir, setup_source_paths, walk_mutatable_files,
)
shutil.rmtree("mutants", ignore_errors=True)
Path("mutants").mkdir()
set_mutant_under_test("mutant_generation")
copy_src_dir()
copy_also_copy_files()
setup_source_paths()
create_mutants(1)
patterns = sys.argv[1:]
shown = {}
for path in walk_mutatable_files():
    data = SourceFileMutationData(path=path)
    data.load()
    for name in data.exit_code_by_key:
        if any(fnmatch.fnmatch(name, pattern) for pattern in patterns):
            shown[name] = get_diff_for_mutant(name, path=path)
print(json.dumps(shown))
"""
#: One hunk header of the diff `mutmut show` prints. Its old side numbers the
#: lines of the function's own text, from 1.
SHOWN_HUNK_RE = re.compile(r"^@@ -(\d+)(?:,\d+)? \+\d+(?:,\d+)? @@")


@dataclass(frozen=True)
class Unit:
    """A function or method that mutmut mutates, with its file and the lines it spans."""

    path: str
    cls: str | None
    name: str
    first: int
    last: int

    @property
    def label(self) -> str:
        """The unit's dotted name, as a reader would write it."""
        return ".".join(part for part in (module_name(self.path), self.cls, self.name) if part)

    @property
    def pattern(self) -> str:
        """The glob that matches this unit's mutants and no other unit's."""
        mangled = f"xǁ{self.cls}ǁ{self.name}" if self.cls else f"x_{self.name}"
        return f"{module_name(self.path)}.{mangled}__mutmut_*"


class Refusal(Exception):
    """A run that cannot give a true answer, with the reason."""


def mutmut_table(root: Path) -> Mapping[str, object]:
    """`pyproject.toml`'s `[tool.mutmut]` table, or `Refusal` where there is none."""
    with (root / "pyproject.toml").open("rb") as handle:
        table = tomllib.load(handle).get("tool", {}).get("mutmut")
    if not isinstance(table, dict):
        raise Refusal("pyproject.toml has no [tool.mutmut] table")
    return table


def _strings(table: Mapping[str, object], key: str) -> list[str]:
    value = table.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise Refusal(f"[tool.mutmut] {key} is not a list of strings")
    return list(value)


def selection_file(table: Mapping[str, object]) -> str:
    """The file, relative to `mutants/`, that the table tells pytest to read its tests from."""
    files = [
        arg[1:] for arg in _strings(table, "pytest_add_cli_args_test_selection") if arg[:1] == "@"
    ]
    if len(files) != 1:
        raise Refusal(
            "[tool.mutmut] pytest_add_cli_args_test_selection must name exactly one @ file, "
            f"which this tool writes; it names {len(files)}"
        )
    return files[0]


def deselected(table: Mapping[str, object]) -> frozenset[str]:
    """The test ids that the table's `--deselect` arguments leave out of every mutmut run."""
    args = _strings(table, "pytest_add_cli_args_test_selection")
    return frozenset(
        value for flag, value in zip(args, args[1:], strict=False) if flag == "--deselect"
    )


def is_mutated(path: str, table: Mapping[str, object]) -> bool:
    """Whether mutmut mutates the file at `path`, by the rule it applies to the table.

    A Python file under one of `source_paths`, matching an `only_mutate` glob
    where there are any, and matching no `do_not_mutate` glob. mutmut matches
    the globs with `fnmatch` against the path as its walk of `source_paths`
    spells it, which is the path relative to the repository root.
    """
    sources = [PurePosixPath(source) for source in _strings(table, "source_paths")]
    only = _strings(table, "only_mutate")
    never = _strings(table, "do_not_mutate")
    return (
        path.endswith(".py")
        and any(PurePosixPath(path).is_relative_to(source) for source in sources)
        and (not only or any(fnmatch.fnmatch(path, glob) for glob in only))
        and not any(fnmatch.fnmatch(path, glob) for glob in never)
    )


def module_name(path: str) -> str:
    """The dotted module name mutmut gives the file at `path`, as `get_mutant_name` builds it."""
    dotted = PurePosixPath(path).with_suffix("").as_posix().replace("/", ".")
    return dotted.removeprefix("src.").removesuffix(".__init__")


def units(path: str, source: str) -> list[Unit]:
    """Every function and method in `source` that mutmut can mutate, with its span.

    mutmut 3.8.0 mutates top-level functions and the methods of top-level
    classes. A nested function is mutated as part of the function around it,
    so its lines count as that function's. A span starts at the first
    decorator, because a changed decorator changes the function.
    """

    def span(node: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[int, int]:
        first = min([node.lineno, *(decorator.lineno for decorator in node.decorator_list)])
        return first, node.end_lineno or node.lineno

    found: list[Unit] = []
    for node in ast.parse(source).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            found.append(Unit(path, None, node.name, *span(node)))
        elif isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    found.append(Unit(path, node.name, child.name, *span(child)))
    return found


def changed_rows(patch: str) -> set[int] | None:
    """The working-tree lines that a `-U0` patch changes, or `None` where the whole file is new.

    A file that git does not track has no patch at all, so an empty patch also
    means a new file. A hunk that only deletes lines names the line after
    which they stood, so that line and the next both count. Either may fall in
    the function that lost the lines, and counting one function too many costs
    only its mutants.
    """
    if not patch or doc_check.NEW_FILE_RE.search(patch):
        return None
    rows: set[int] = set()
    for hunk in doc_check.HUNK_RE.finditer(patch):
        first = int(hunk.group(3))
        count = int(hunk.group(4) or 1)
        rows.update(range(first, first + count) if count else (first, first + 1))
    return rows


@dataclass
class Change:
    """What the branch changed in the files that mutmut mutates."""

    against: str
    units: list[Unit]
    #: Lines changed outside any unit, by file, for the report.
    outside: dict[str, list[int]]
    #: The lines changed in each file that mutmut mutates, or `None` where the
    #: whole file is new. `verdict` counts a mutant only on one of these.
    rows: dict[str, set[int] | None] = field(default_factory=dict)
    #: The changed test files that import the simulator, deleted ones included.
    #: A mutant of the code cannot say whether one of these still catches what
    #: it caught before, so `compare_tests` runs both versions of each.
    tests: list[str] = field(default_factory=list)
    #: The commit the diff starts from, where the branch forked.
    fork: str = ""


def _imports_simulator(root: Path, fork: str, path: str) -> bool:
    """Whether a test file imports the simulator, read from the fork's copy where it is deleted."""
    if (root / path).is_file():
        source = (root / path).read_text(encoding="utf-8")
    else:
        source = read_git(["show", f"{fork}:{path}"], root)
    return imports_product(ast.parse(source))


def branch_change(root: Path, base: str, table: Mapping[str, object]) -> Change:
    """The units that changed between the fork from `base` and the working tree."""
    fork, against = doc_check._diff_from(root, base)
    changed: list[Unit] = []
    outside: dict[str, list[int]] = {}
    changed_by_file: dict[str, set[int] | None] = {}
    tests: list[str] = []
    for path in doc_check._changed_paths(root, fork):
        if (
            path.startswith(TESTS)
            and is_test_file(PurePosixPath(path).name)
            and _imports_simulator(root, fork, path)
        ):
            tests.append(path)
        if not is_mutated(path, table) or not (root / path).is_file():
            continue
        found = units(path, (root / path).read_text(encoding="utf-8"))
        rows = changed_rows(read_git(["diff", "-U0", fork, "--", path], root))
        changed_by_file[path] = rows
        if rows is None:
            changed.extend(found)
            continue
        changed.extend(
            unit for unit in found if any(unit.first <= row <= unit.last for row in rows)
        )
        left = sorted(row for row in rows if not any(u.first <= row <= u.last for u in found))
        if left:
            outside[path] = left
    return Change(against, changed, outside, changed_by_file, tests, fork)


def working_files(root: Path, tree: str) -> list[str]:
    """The Python files under `tree` in the working tree, tracked or not, but not ignored."""
    names = {path.relative_to(root).as_posix() for path in tracked_under(root, tree, ".py")}
    prefix = tree.strip("/") + "/"
    names.update(
        name
        for name in listed_paths(read_git(untracked_path_args(), root))
        if name.startswith(prefix) and name.endswith(".py")
    )
    return sorted(names)


def simulator_unit_tests(root: Path) -> list[str]:
    """Every test file under `tests/unit/` that imports the simulator."""
    return [
        name
        for name in working_files(root, UNIT_TESTS)
        if is_test_file(PurePosixPath(name).name)
        and imports_product(ast.parse((root / name).read_text(encoding="utf-8")))
    ]


def _mutmut(root: Path, *args: str, log: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Run one mutmut command in `root`, its output to `log` where one is given."""
    environment = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    command = [sys.executable, "-m", "mutmut", *args]
    if log is None:
        return subprocess.run(
            command, cwd=root, capture_output=True, encoding="utf-8", env=environment, check=False
        )
    with log.open("w", encoding="utf-8") as output:
        return subprocess.run(
            command,
            cwd=root,
            stdout=output,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
            env=environment,
            check=False,
        )


@dataclass(frozen=True)
class Listing:
    """The mutants of the changed functions, listed before the run, and the ones to run."""

    #: Each listed mutant's diff, as `mutmut show` prints it, by name.
    shown: Mapping[str, str]
    #: The names that run: those on a changed line, and those not placed.
    run: frozenset[str]


def listing(root: Path, change: Change) -> Listing | None:
    """List the changed functions' mutants and keep the ones that can change the verdict.

    A mutant runs when a line it changes is one the branch changed, or when it
    cannot be placed. In a new file every line is changed, so all of them run.
    `None` where the mutants could not be listed, and then every mutant of the
    changed functions runs, as it did before this listing existed.
    """
    patterns = [unit.pattern for unit in change.units]
    environment = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    listed = subprocess.run(
        [sys.executable, "-c", LIST_SCRIPT, *patterns],
        cwd=root,
        capture_output=True,
        encoding="utf-8",
        env=environment,
        check=False,
    )
    try:
        shown = json.loads(split_lines(listed.stdout)[-1]) if not listed.returncode else None
    except (IndexError, ValueError):
        shown = None
    if not isinstance(shown, dict):
        return None
    files = {path: split_lines((root / path).read_text(encoding="utf-8")) for path in change.rows}
    selected: set[str] = set()
    for unit in change.units:
        rows = change.rows.get(unit.path)
        for name, text in shown.items():
            if not fnmatch.fnmatch(name, unit.pattern):
                continue
            placed = None if rows is None else mutated_rows(unit, files[unit.path], text)
            if rows is None or placed is None or placed & rows:
                selected.add(name)
    return Listing(shown, frozenset(selected))


def run(
    root: Path,
    patterns: Sequence[str],
    table: Mapping[str, object],
    tests: Sequence[str] | None = None,
) -> tuple[int, Path]:
    """Empty `mutants/`, write the test selection into it, and run mutmut on `patterns`.

    The selection is `tests`, as files or test ids, and every simulator unit
    test file where it is `None`. An empty selection would make pytest run all
    of `testpaths`, so the caller never passes one.
    """
    mutants = root / MUTANTS
    shutil.rmtree(mutants, ignore_errors=True)
    mutants.mkdir()
    if tests is None:
        tests = simulator_unit_tests(root)
        what = f"the {len(tests)} simulator test files under {UNIT_TESTS}/"
    else:
        what = f"{len(tests)} selected tests or test files"
    (mutants / selection_file(table)).write_text("".join(f"{t}\n" for t in tests), "utf-8")
    log = mutants / RUN_LOG
    # To stderr, so that stdout holds only the report, or under `--verdict` the JSON.
    print(
        f"Running mutmut in {root} against {what}. Its progress goes to {log}.",
        file=sys.stderr,
        flush=True,
    )
    return _mutmut(root, "run", *patterns, log=log).returncode, log


def statuses(root: Path) -> dict[str, str]:
    """Every mutant's status, from `mutmut results --all true`."""
    listing = _mutmut(root, "results", "--all", "true")
    if listing.returncode:
        raise Refusal(f"`mutmut results` exited {listing.returncode}: {listing.stderr.strip()}")
    return {m[1]: m[2] for line in split_lines(listing.stdout) if (m := RESULT_RE.match(line))}


def recorded_exit_codes(root: Path, paths: Iterable[str]) -> dict[str, int]:
    """The exit status mutmut recorded for each mutant of the files at `paths`.

    Read from the `.meta` file mutmut 3.8.0 writes beside each mutated file,
    because `mutmut results` prints a status, and two exit statuses print as
    the same one.
    """
    codes: dict[str, int] = {}
    for path in paths:
        meta = root / MUTANTS / f"{path}.meta"
        if meta.is_file():
            codes.update(json.loads(meta.read_text(encoding="utf-8"))["exit_code_by_key"])
    return codes


def _test_files(root: Path, name: str) -> list[str]:
    """The test files holding the tests that mutmut runs against mutant `name`."""
    listing = _mutmut(root, "tests-for-mutant", name)
    if listing.returncode:
        raise Refusal(f"`mutmut tests-for-mutant {name}` exited {listing.returncode}")
    return sorted({line.partition("::")[0] for line in split_lines(listing.stdout) if line})


def _pytest_in_mutants(root: Path, files: Sequence[str], mutant: str) -> int | None:
    """Run whole test files in `mutants/` under `mutant`, or none for `""`; `None` on a timeout.

    The mutated copy of the source comes first on the import path, and mutmut's
    trampolines read which mutant to run from the environment, as its own
    workers do.

    A run that stopped because a test module raised while it was collected
    returns 1, the status of a failed test. pytest gives that run status 2, the
    status of an interrupted run, and `settle` counts a raise at import as a
    kill.
    """
    environment = {**os.environ, "MUTANT_UNDER_TEST": mutant, "PYTHONPATH": "src"}
    command = [sys.executable, "-m", "pytest", "--rootdir=.", "-x", "-q", "-p", "no:cacheprovider"]
    try:
        done = subprocess.run(
            [*command, *files],
            cwd=root / MUTANTS,
            env=environment,
            capture_output=True,
            timeout=RERUN_TIMEOUT_S,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None
    if done.returncode == INTERRUPTED and COLLECTION_ERROR_RE.search(
        done.stdout.decode("utf-8", errors="replace")
    ):
        return 1
    return done.returncode


def settle(root: Path, found: Mapping[str, str], codes: Mapping[str, int]) -> dict[str, str]:
    """`found`, with each mutant whose pytest run raised given the status of a whole-file run.

    A raise while a test module is imported fails the collection, which is a
    kill. A changed test id can hide a survivor, and a run of the whole files
    tells the two apart. The files first run once with no mutant applied, so
    that a failure of this way of running them is never counted as a kill.
    """
    settled = dict(found)
    raised = sorted(name for name in found if codes.get(name) == RAISED)
    files = {name: _test_files(root, name) for name in raised}
    every = sorted({file for named in files.values() for file in named})
    if every and _pytest_in_mutants(root, every, "") != 0:
        for name in raised:
            settled[name] = "unsettled, its test files fail with no mutant applied"
        return settled
    for name in raised:
        if not files[name]:
            # pytest given no file runs the whole of `testpaths`.
            settled[name] = "unsettled, mutmut names no test for it"
            continue
        code = _pytest_in_mutants(root, files[name], name)
        settled[name] = (
            "timeout"
            if code is None
            else RERUN_STATUS.get(code, f"unsettled, pytest exited {code}")
        )
    return settled


def _tail(log: Path, lines: int = 30) -> str:
    return "\n".join(split_lines(log.read_text(encoding="utf-8", errors="replace"))[-lines:])


def counts(found: Iterable[str]) -> str:
    """How many mutants have each status, in the report's order."""
    counted = Counter(found)
    named = [status for status in STATUS_ORDER if counted[status]]
    named += sorted(status for status in counted if status not in STATUS_ORDER)
    return ", ".join(f"{counted[status]} {status}" for status in named) or "none"


def unit_lines(change: Change, found: Mapping[str, str]) -> tuple[list[str], dict[str, str]]:
    """A line for each changed unit and each file's changes outside one, and the units' mutants."""
    lines: list[str] = []
    mine: dict[str, str] = {}
    for unit in change.units:
        names = sorted(name for name in found if fnmatch.fnmatch(name, unit.pattern))
        mine.update((name, found[name]) for name in names)
        if names:
            lines.append(f"  {unit.label}: {len(names)} mutants - {counts(mine[n] for n in names)}")
        else:
            lines.append(f"  {unit.label}: no mutants. {NO_MUTANTS}")
    for path, rows in change.outside.items():
        lines.append(
            f"  {path}: {len(rows)} changed lines outside any function, from line {rows[0]} "
            f"to {rows[-1]}. mutmut never mutates module-level code or class attributes."
        )
    return lines, mine


def report_branch(root: Path, change: Change, found: Mapping[str, str]) -> str:
    """The report of a run on the changed units: each unit, then each survivor's diff."""
    listed, mine = unit_lines(change, found)
    lines = [f"Mutation run on the functions changed against {change.against}.", "", *listed]
    lines += ["", f"All: {len(mine)} mutants - {counts(mine.values())}."]
    for name in sorted(name for name, status in mine.items() if status == "survived"):
        shown = _mutmut(root, "show", name)
        lines += ["", (shown.stdout or shown.stderr).rstrip()]
    others = sorted(name for name, status in mine.items() if status not in {"killed", "survived"})
    if others:
        lines += ["", "Neither killed nor survived:"]
        lines += [f"  {name}: {mine[name]}" for name in others]
    lines += ["", TIERS_NOT_RUN]
    return "\n".join(lines)


def mutated_rows(unit: Unit, lines: Sequence[str], shown: str) -> set[int] | None:
    """The lines of `unit`'s file that one mutant changes, placed from `mutmut show`'s diff.

    `mutmut show` diffs the function's own text, whose line 1 is the first
    line libcst prints for it: its first decorator or its `def`, or a comment
    or blank line directly above them, which libcst counts as part of the
    function. So the diff's context and removed lines are tried at each offset
    that puts line 1 between `unit.first` and the comments above it. Each is
    compared with the file's line there, both stripped, because a method
    prints one indent shallower than it stands in its class. Exactly one
    offset must fit every line, and the removed lines placed at it are the
    answer. `None` where no offset fits, or more than one does.
    """
    named: list[tuple[int, str, bool]] = []
    at: int | None = None
    for line in split_lines(shown):
        hunk = SHOWN_HUNK_RE.match(line)
        if hunk:
            at = int(hunk.group(1))
        elif at is not None and line[:1] in (" ", "-"):
            named.append((at, line[1:].strip(), line[:1] == "-"))
            at += 1
    if not any(removed for _, _, removed in named):
        return None
    above = unit.first - 1
    while above > 0 and lines[above - 1].strip()[:1] in ("", "#"):
        above -= 1
    fits = [
        offset
        for offset in range(above, unit.first)
        if all(
            0 < row + offset <= len(lines) and lines[row + offset - 1].strip() == text
            for row, text, _ in named
        )
    ]
    if len(fits) != 1:
        return None
    return {row + fits[0] for row, _, removed in named if removed}


def _edited_lines(shown: str) -> list[str]:
    """The removed and added lines of `mutmut show`'s diff, indented for a note."""
    lines = split_lines(shown)
    start = next((at for at, line in enumerate(lines) if SHOWN_HUNK_RE.match(line)), len(lines))
    return [f"    {line}" for line in lines[start:] if line[:1] in ("-", "+")]


def _listed(names: Sequence[str]) -> str:
    """The first `NOTE_NAMES` of `names`, then a count of the rest."""
    shown = ", ".join(names[:NOTE_NAMES])
    return shown + (f", and {len(names) - NOTE_NAMES} more" if len(names) > NOTE_NAMES else "")


def verdict(
    root: Path,
    change: Change,
    found: Mapping[str, str],
    compared: Compared | None = None,
    listed: Listing | None = None,
) -> dict[str, object]:
    """What `docket verify` reads: the mutants of changed lines that the tests did not catch.

    A mutant counts only where a line it changes is one the branch changed.
    One the tests caught, by `CAUGHT`, is counted and needs no line. One they
    missed, by `MISSED`, or whose status decides nothing, is placed with
    `mutated_rows`. On a changed line it goes into `uncaught` or `undecided`.
    On a line the branch did not change it is named in a note and not
    counted, because that line was not this branch's to test. One that cannot
    be placed is `undecided`, because a guess at its line could pass a branch
    on a line it wrote. In a new file every line is changed, so nothing needs
    placing.

    `notes` says what the run did not measure: a changed line outside any
    function, a changed function with no mutants, and a changed line that
    carries `# pragma: no mutate`. `compared` is what `compare_tests` found
    for the changed tests, and its lists are added to these.

    `listed` is what `listing` chose before the run. A listed mutant that did
    not run changes only lines the branch did not change, so a note counts it,
    and a listed diff is used in place of a `mutmut show` call.
    """
    caught = 0
    uncaught: list[str] = []
    undecided: list[str] = []
    elsewhere: list[str] = []
    not_run: list[str] = []
    notes: list[str] = []
    pool = set(found) | set(listed.shown if listed is not None else ())
    files = {path: split_lines((root / path).read_text(encoding="utf-8")) for path in change.rows}
    if not change.units:
        notes.append(f"No function that mutmut mutates changed against {change.against}.")
    for unit in change.units:
        names = sorted(name for name in pool if fnmatch.fnmatch(name, unit.pattern))
        if not names:
            notes.append(f"Not mutated: {unit.label} changed and has no mutants. {NO_MUTANTS}")
        rows = change.rows.get(unit.path)
        for name in names:
            if listed is not None and name not in listed.run:
                not_run.append(name)
                continue
            status = found.get(name, "not in mutmut's results after the run")
            if status in CAUGHT:
                caught += 1
                continue
            if listed is not None and name in listed.shown:
                text, readable = listed.shown[name], True
            else:
                shown = _mutmut(root, "show", name)
                text, readable = shown.stdout, not shown.returncode
            placed = mutated_rows(unit, files[unit.path], text) if readable else None
            if rows is not None and placed is None:
                undecided.append(f"{unit.path}: {name} - {status}, on a line not placed")
                continue
            if rows is not None and placed is not None and not placed & rows:
                elsewhere.append(name)
                continue
            where = f"{unit.path}:{min(placed)}" if placed else unit.path
            entry = "\n".join([f"{where} {name} - {status}", *_edited_lines(text)])
            (uncaught if status in MISSED else undecided).append(entry)
    for path, outside in change.outside.items():
        notes.append(
            f"Not mutated: {len(outside)} changed lines of {path} outside any function, from "
            f"line {outside[0]} to {outside[-1]}, since mutmut never mutates module-level code "
            "or class attributes."
        )
    for path, rows in change.rows.items():
        lines = files[path]
        for row in sorted(range(1, len(lines) + 1) if rows is None else rows):
            if (
                row <= len(lines)
                and "# pragma:" in lines[row - 1]
                and "no mutate" in lines[row - 1]
            ):
                notes.append(f"Exempted by `# pragma: no mutate` on a changed line: {path}:{row}")
    if not_run:
        notes.append(
            f"Not run: {len(not_run)} mutants of the changed functions that change only lines "
            f"this branch did not change, so they cannot change this verdict: {_listed(not_run)}."
        )
    if elsewhere:
        notes.append(
            f"Not counted: {len(elsewhere)} mutants that the tests did not catch, on lines of the "
            f"changed functions that this branch did not change: {_listed(elsewhere)}."
        )
    if compared is not None:
        uncaught += compared.uncaught
        undecided += compared.undecided
        notes += compared.notes
    if change.units:
        notes.append(TIERS_NOT_RUN)
    return {"caught": caught, "uncaught": uncaught, "undecided": undecided, "notes": notes}


@dataclass
class Compared:
    """What `compare_tests` found, in the lists `verdict` prints."""

    uncaught: list[str] = field(default_factory=list)
    undecided: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


#: The module-level names that pytest reads by convention, where no test names
#: them, so a change to one can change every test in the file.
PYTEST_NAMES = frozenset(
    {
        "pytestmark",
        "pytest_plugins",
        "setup_module",
        "teardown_module",
        "setup_function",
        "teardown_function",
        "setUpModule",
        "tearDownModule",
    }
)
#: The built-in calls that read a module's names without naming them, or run
#: code that can. A test file that makes one is compared whole.
DYNAMIC_CALLS = frozenset({"globals", "eval", "exec"})
#: The built-in calls that read the current scope when they are given no
#: argument, which at module level is the module's names.
SCOPE_CALLS = frozenset({"vars", "locals"})


class _Whole(Exception):
    """A test file whose tests `_definitions` cannot tell apart, so it is compared whole."""


@dataclass(frozen=True)
class _Statement:
    """One module-level statement, as `_signature` compares it."""

    #: Where it stands in the module, which orders the statements of a signature.
    position: int
    #: Its syntax tree, without docstrings, line numbers or comments.
    dump: str
    #: Every name it reads, including the parameters of each function in it,
    #: since pytest passes a fixture to the parameter of the same name.
    reads: frozenset[str]


@dataclass
class _Definitions:
    """One version of a test file, as the parts whose change can change one of its tests."""

    #: Each test by pytest id. A method's statement holds its class too.
    tests: dict[str, _Statement] = field(default_factory=dict)
    #: The statement that binds each module-level name, other than an import.
    bound: dict[str, _Statement] = field(default_factory=dict)
    #: What each imported name is bound to.
    imports: dict[str, set[str]] = field(default_factory=dict)
    #: The statements that can change any test without a test naming them,
    #: such as a fixture, a pytest hook or a module-level call.
    shared: list[str] = field(default_factory=list)


def _without_docstrings(node: ast.AST) -> ast.AST:
    """A copy of `node` with the docstring of each function and class in it removed."""
    copied = copy.deepcopy(node)
    for inner in ast.walk(copied):
        if isinstance(inner, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if inner.body and _is_string(inner.body[0]):
                inner.body = inner.body[1:]
    return copied


def _is_string(node: ast.stmt) -> bool:
    """Whether `node` is a bare string, which is a docstring and does nothing."""
    return (
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    )


def _statement(position: int, node: ast.AST, keep_docstrings: bool) -> _Statement:
    reads = frozenset(
        inner.id if isinstance(inner, ast.Name) else inner.arg
        for inner in ast.walk(node)
        if isinstance(inner, (ast.Name, ast.arg))
    )
    shown = node if keep_docstrings else _without_docstrings(node)
    return _Statement(position, ast.dump(shown), reads)


def _is_fixture(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Whether a decorator of `node` is `pytest.fixture`, called or not."""
    return any(
        ast.unparse(decorator.func if isinstance(decorator, ast.Call) else decorator)
        in ("pytest.fixture", "fixture")
        for decorator in node.decorator_list
    )


def _is_test_method(node: ast.stmt) -> TypeGuard[ast.FunctionDef | ast.AsyncFunctionDef]:
    """Whether pytest collects `node`, in a test class, as a test, by its default `test*` name."""
    return isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(
        "test"
    )


def _is_test_class(node: ast.ClassDef) -> bool:
    """Whether pytest collects tests from the class, by its default `Test*` name."""
    return node.name.startswith("Test")


def _definitions(path: str, source: str) -> _Definitions:
    """The tests and module-level statements of one version of a test file.

    Raises `_Whole` where a test can depend on a part of the file that it does
    not name: a call that reads the module's names, such as `globals()`; a
    star import; a name bound twice; or a test class that inherits, takes
    keywords or holds a class, since its tests' ids name only its own methods.
    """
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and (node.func.id in DYNAMIC_CALLS or (node.func.id in SCOPE_CALLS and not node.args))
        ) or (isinstance(node, ast.Name) and node.id == "__name__"):
            raise _Whole
        if isinstance(node, ast.Attribute) and node.attr == "__globals__":
            raise _Whole
    # A test that reads a docstring can change when the docstring does.
    keep = any(
        isinstance(node, ast.Attribute) and node.attr == "__doc__" for node in ast.walk(tree)
    )
    found = _Definitions()

    def bind(name: str, statement: _Statement) -> None:
        if name in found.bound or name in found.imports:
            raise _Whole
        found.bound[name] = statement

    for position, node in enumerate(tree.body):
        if _is_string(node):
            continue
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.ImportFrom) and node.module == "__future__":
                found.shared.append(ast.dump(node))
                continue
            for alias in node.names:
                if alias.name == "*":
                    raise _Whole
                if isinstance(node, ast.Import):
                    name = alias.asname or alias.name.partition(".")[0]
                    target = f"import {alias.name} as {alias.asname}"
                else:
                    name = alias.asname or alias.name
                    target = f"from {'.' * node.level}{node.module or ''} import {alias.name}"
                # Two `import a.b` and `import a.c` both bind `a` to `a`.
                plain = isinstance(node, ast.Import) and alias.asname is None
                held = found.imports.setdefault(name, set())
                if name in found.bound or (held and not plain) or target in held:
                    raise _Whole
                held.add(target)
            continue
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            statement = _statement(position, node, keep)
            if node.name.startswith("test"):
                found.tests["::".join((path, node.name))] = statement
            elif _is_fixture(node) or node.name in PYTEST_NAMES or node.name.startswith("pytest_"):
                found.shared.append(statement.dump)
            bind(node.name, statement)
            continue
        if isinstance(node, ast.ClassDef):
            if _is_test_class(node):
                if node.bases or node.keywords:
                    raise _Whole
                if any(isinstance(child, ast.ClassDef) for child in node.body):
                    raise _Whole
                methods = [child for child in node.body if _is_test_method(child)]
                # A method's test is the method and the rest of its class: the
                # class's decorators, attributes, fixtures and helpers.
                rest = ast.ClassDef(
                    name=node.name,
                    bases=[],
                    keywords=[],
                    body=[child for child in node.body if not _is_test_method(child)],
                    decorator_list=node.decorator_list,
                    type_params=node.type_params,
                )
                for method in methods:
                    whole = ast.Module(body=[rest, method], type_ignores=[])
                    found.tests["::".join((path, node.name, method.name))] = _statement(
                        position, whole, keep
                    )
            bind(node.name, _statement(position, node, keep))
            continue
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
            targets = [node.target]
        elif isinstance(node, ast.TypeAlias):
            targets = [node.name]
        names = [
            inner.id
            for target in targets
            for inner in ast.walk(target)
            if isinstance(inner, ast.Name)
        ]
        simple = targets and all(
            isinstance(inner, (ast.Name, ast.Tuple, ast.List, ast.Starred, ast.Store))
            for target in targets
            for inner in ast.walk(target)
        )
        if not simple or any(name in PYTEST_NAMES for name in names):
            # An `if`, `try`, call or other statement that is not a definition,
            # or an assignment to an attribute or an item.
            found.shared.append(ast.dump(node))
            continue
        statement = _statement(position, node, keep)
        for name in names:
            bind(name, statement)
    return found


def _signature(found: _Definitions, test: str) -> tuple[object, ...]:
    """What one test does, as the parts of its file version that it can reach.

    That is the test, every module-level statement that binds a name it reads,
    and those statements' names in turn, in module order, what each imported
    name it reads is bound to, and the statements every test shares. Two
    versions of a test with the same signature run the same code.
    """
    reached: set[str] = set()
    waiting = list(found.tests[test].reads)
    while waiting:
        name = waiting.pop()
        if name in reached:
            continue
        reached.add(name)
        if name in found.bound:
            waiting.extend(found.bound[name].reads)
    statements = sorted(
        {found.bound[name] for name in reached if name in found.bound},
        key=lambda statement: statement.position,
    )
    imports = {name: frozenset(found.imports[name]) for name in reached if name in found.imports}
    return (
        found.tests[test].dump,
        tuple(statement.dump for statement in statements),
        imports,
        tuple(found.shared),
    )


def changed_tests(path: str, base: str, branch: str) -> tuple[list[str], list[str]] | None:
    """The tests of each version of a test file that can behave differently in the other.

    Two lists of pytest ids, the base version's first, each in file order. A
    test is in its list where the other version has no test of that id, or
    where the two `_signature`s differ. So a changed helper selects only the
    tests that reach it, and a docstring, a comment, a new import or a new
    helper selects none. `None` where `_definitions` cannot tell the tests
    apart, and then the whole file is compared.

    Importing a module that the other version does not import is taken to
    change no test, since it only binds a name. A module whose import changed
    what an unrelated test does would be missed, and
    `docs/mutation-testing.md` lists that among what the check leaves
    unmeasured.
    """
    try:
        before, after = _definitions(path, base), _definitions(path, branch)
    except _Whole:
        return None

    def differs(here: _Definitions, there: _Definitions, test: str) -> bool:
        return test not in there.tests or _signature(here, test) != _signature(there, test)

    return (
        [test for test in before.tests if differs(before, after, test)],
        [test for test in after.tests if differs(after, before, test)],
    )


def base_selection(path: str, base: str, branch: str | None) -> tuple[str, ...]:
    """The tests of a changed test file's base version that the branch changed, by pytest id.

    The branch changed a test where `changed_tests` says the two versions can
    differ. The whole file is the answer where it cannot tell, and where the
    branch deleted the file. A file that only gained tests has nothing in its
    base version to compare, so the answer is empty.
    """
    if branch is None:
        return (path,)
    changed = changed_tests(path, base, branch)
    return (path,) if changed is None else tuple(changed[0])


def branch_selection(path: str, base: str | None, branch: str) -> tuple[str, ...]:
    """The tests of a changed test file's branch version that the branch changed or added.

    The branch run tries these first, because a test that the branch rewrote
    or moved is where a mutant its base version caught is likeliest to be
    caught again. The whole file where the base version had no such file, or
    where `changed_tests` cannot tell.
    """
    if base is None:
        return (path,)
    changed = changed_tests(path, base, branch)
    return (path,) if changed is None else tuple(changed[1])


def copy_tree(root: Path, tree: Path, table: Mapping[str, object]) -> None:
    """Copy into `tree` what mutmut copies from `root`, so that mutmut can run there."""
    names = {*_strings(table, "source_paths"), *_strings(table, "also_copy"), TESTS}
    for name in sorted(names):
        source = root / name
        if source.is_dir():
            ignore = shutil.ignore_patterns("__pycache__", MUTANTS)
            shutil.copytree(source, tree / name, ignore=ignore, dirs_exist_ok=True)
        elif source.is_file():
            (tree / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, tree / name)
    shutil.copy2(root / "pyproject.toml", tree / "pyproject.toml")


def _clean_run(tree: Path, tests: Sequence[str]) -> int | None:
    """pytest's exit status for `tests` in `tree`, with no mutant applied; `None` on a timeout."""
    environment = {**os.environ, "PYTHONPATH": "src"}
    command = [sys.executable, "-m", "pytest", "--rootdir=.", "-x", "-q", "-p", "no:cacheprovider"]
    try:
        done = subprocess.run(
            [*command, *tests],
            cwd=tree,
            env=environment,
            capture_output=True,
            timeout=CLEAN_TIMEOUT_S,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None
    return done.returncode


def core_imports(source: str) -> set[str]:
    """The names under `CORE_PACKAGE` that the test file `source` imports, as dotted modules.

    `from anesthesia_sim.core.dosing import x` names `anesthesia_sim.core.dosing`,
    and so does `from anesthesia_sim.core import dosing` or `import
    anesthesia_sim.core.dosing`. An import inside a function counts too. A name
    that is not a module, such as a class that the package exports, matches no
    mutated file, so the caller drops it.
    """
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            module = node.module
            if module == CORE_PACKAGE or module.startswith(f"{CORE_PACKAGE}."):
                names.add(module)
                names.update(f"{module}.{alias.name}" for alias in node.names)
        elif isinstance(node, ast.Import):
            names.update(
                alias.name for alias in node.names if alias.name.startswith(f"{CORE_PACKAGE}.")
            )
    return names


def _compared_statuses(
    tree: Path,
    patterns: Sequence[str],
    tests: Sequence[str],
    table: Mapping[str, object],
    files: Sequence[str],
) -> dict[str, str]:
    """Run mutmut in `tree` on `patterns` against `tests`, and settle the mutants of `files`.

    `files` are the compared modules, read from the checkout, since a copied
    tree holds the same source and is not a checkout. A mutant of any other
    module is left out.
    """
    code, log = run(tree, patterns, table, tests)
    if code:
        raise Refusal(f"mutmut exited {code} in {tree}. The end of {log}:\n{_tail(log)}")
    modules = {module_name(path) for path in files}
    found = {
        name: status
        for name, status in statuses(tree).items()
        if name.rpartition(".")[0] in modules
    }
    return settle(tree, found, recorded_exit_codes(tree, files))


def compare_tests(root: Path, change: Change, table: Mapping[str, object]) -> Compared:
    """The mutants that a changed test's base version kills and the branch's version misses.

    A mutant of the code cannot show that a branch weakened a test, because
    the test is what changed. So the two versions of each changed simulator
    unit test run against the same mutants, both on the branch's source, and
    a mutant has the same name in both runs. The mutants are those of
    `DISPLAY_PACKAGE`, and of each module of `CORE_PACKAGE` that either
    version of a compared file imports by name, by `core_imports`.

    Each run happens in a copy of the tree, so the main run's `mutants/` is
    left alone. In the base copy, every file the branch changed under `tests/`
    has its base version. mutmut runs there on the base tests that the branch
    changed, by `base_selection`. The branch copy then runs only the mutants
    that the base run caught. It runs them first against the tests that the
    branch changed or added, by `branch_selection`, and then the ones those
    miss against the branch's version of every changed unit test file, whole.
    A test that fails in the smaller run fails in the whole file too, so the
    first run changes the cost and not the answer. It exists because a mutant
    re-imports its test files and runs every test of them that reaches it, and
    a large file made the whole-file run take hours (`PL-D59R`). A mutant the
    base caught and the branch missed goes into `uncaught`. One whose status
    decides nothing goes into `undecided`.

    A file whose base tests fail on the branch's source with no mutant applied
    is named in a note and not compared, because the branch changed what the
    test checks. A test outside `tests/unit/` is named in a note too. The
    project owner chose this check on 2026-10-24 (ratified, over leaving these
    tests unmeasured, `PL-7FPD`), and its core modules the same day (ratified,
    over leaving core unit tests unmeasured and over comparing every mutant a
    changed test reaches, `PL-H57W`).
    """
    compared = Compared()
    unit_tests = [path for path in change.tests if path.startswith(f"{UNIT_TESTS}/")]
    others = [path for path in change.tests if path not in unit_tests]
    if others:
        compared.notes.append(
            f"Not measured: whether {len(others)} changed test files outside {UNIT_TESTS}/ "
            f"still catch what they caught before: {_listed(others)}."
        )
    if not unit_tests:
        return compared
    changed = [
        path for path in doc_check._changed_paths(root, change.fork) if path.startswith(TESTS)
    ]
    listing = read_git(["ls-tree", "-r", "--name-only", "-z", change.fork, "--", *changed], root)
    base = {
        path: read_git(["show", f"{change.fork}:{path}"], root) for path in listed_paths(listing)
    }
    # A test the table deselects never runs under mutmut, and a selection of
    # nothing but such tests would collect none.
    skipped = deselected(table)
    selections: list[tuple[str, tuple[str, ...]]] = []
    imported: dict[str, set[str]] = {}
    first: list[str] = []
    for path in unit_tests:
        here = root / path
        branch = here.read_text(encoding="utf-8") if here.is_file() else None
        if branch is not None:
            first += [t for t in branch_selection(path, base.get(path), branch) if t not in skipped]
        if path not in base:
            continue
        imported[path] = core_imports(base[path]) | core_imports(branch or "")
        selection = base_selection(path, base[path], branch)
        selections.append((path, tuple(t for t in selection if t not in skipped)))
    on_branch = [path for path in unit_tests if (root / path).is_file()]
    mutated = [
        name
        for source in _strings(table, "source_paths")
        for name in working_files(root, source)
        if is_mutated(name, table)
    ]
    displays = [name for name in mutated if module_name(name).startswith(f"{DISPLAY_PACKAGE}.")]
    with tempfile.TemporaryDirectory(prefix="diff_mutation_") as scratch:
        base_tree, branch_tree = Path(scratch, "base"), Path(scratch, "branch")
        copy_tree(root, base_tree, table)
        for path in changed:
            if path in base:
                (base_tree / path).parent.mkdir(parents=True, exist_ok=True)
                (base_tree / path).write_text(base[path], encoding="utf-8")
            else:
                (base_tree / path).unlink(missing_ok=True)
        tests: list[str] = []
        files: list[str] = []
        for path, selection in selections:
            if not selection:
                continue
            if _clean_run(base_tree, selection) != 0:
                compared.notes.append(
                    f"Not compared: {path}, because the tests of its base version that this "
                    "branch changed fail on this branch's source with no mutant applied, so "
                    "the branch changed what they check."
                )
                continue
            tests.extend(selection)
            files.append(path)
        if not tests:
            return compared
        named = set().union(*(imported[path] for path in files))
        cores = [name for name in mutated if module_name(name) in named]
        modules = [module_name(name) for name in cores]
        # A module's own mutants are `x_` and `xǁ` names. `module.*` would also
        # take every submodule's when the module is a package such as
        # `anesthesia_sim.core` itself.
        patterns = [
            f"{DISPLAY_PACKAGE}.*",
            *(pattern for module in modules for pattern in (f"{module}.x_*", f"{module}.xǁ*")),
        ]
        scope = DISPLAY_PACKAGE + (f" and of {_listed(modules)}" if modules else "")
        compared_files = [*displays, *cores]
        caught = sorted(
            name
            for name, status in _compared_statuses(
                base_tree, patterns, tests, table, compared_files
            ).items()
            if status in CAUGHT
        )
        if not caught:
            compared.notes.append(
                f"Compared: the base version of {_listed(files)} catches no mutant of "
                f"{scope}, so the branch's version has nothing to keep catching."
            )
            return compared
        narrowed = bool(on_branch and first and first != on_branch)
        after: dict[str, str] = {}
        retried: list[str] = []
        if on_branch:
            copy_tree(root, branch_tree, table)
            if narrowed:
                after = _compared_statuses(branch_tree, caught, first, table, compared_files)
            retried = [name for name in caught if after.get(name) not in CAUGHT]
            if retried:
                again = _compared_statuses(branch_tree, retried, on_branch, table, compared_files)
                # `again` lists every mutant of the compared modules, and ran
                # only the retried ones, so only theirs replace the first run's.
                after = {name: status for name, status in after.items() if name not in retried}
                after |= {name: again[name] for name in retried if name in again}
        shown_in = branch_tree if on_branch else base_tree
        for name in caught:
            status = after.get(name, "no tests")
            if status in CAUGHT:
                continue
            shown = _mutmut(shown_in, "show", name)
            entry = "\n".join(
                [
                    f"{_listed(files)}: {name} - caught by the base version, {status} on this "
                    "branch's version",
                    *_edited_lines(shown.stdout),
                ]
            )
            (compared.uncaught if status in MISSED else compared.undecided).append(entry)
    compared.notes.append(
        f"Compared: {len(caught)} mutants of {scope} that the base version of "
        f"{_listed(files)} catches, run against this branch's version of "
        f"{_listed(on_branch) or 'no file, since it deleted them'}"
        + (
            f", first against the {len(first)} tests and test files it changed or added, "
            f"and then the {len(retried)} mutants that those missed against the whole files"
            if narrowed
            else ""
        )
        + f". Whether a changed test still catches a fault elsewhere, such as in a module "
        f"of {CORE_PACKAGE} that it does not import by name, is not measured."
    )
    return compared


def report_all(found: Mapping[str, str]) -> str:
    """The report of a run on every mutant: the kill rate of each module, then the totals."""
    # A mutant's name is its module, a dot, and the mangled name of its
    # function, which holds no dot.
    by_module: dict[str, list[str]] = {}
    for name, status in found.items():
        by_module.setdefault(name.rpartition(".")[0], []).append(status)
    lines = ["Kill rate by module, as killed / (killed + survived):", ""]
    for module, found_here in sorted(by_module.items()):
        killed = found_here.count("killed")
        tested = killed + found_here.count("survived")
        rate = f"{100 * killed / tested:.0f}%" if tested else "no mutant tested"
        lines.append(f"  {module}: {killed} / {tested} ({rate}); {counts(found_here)}")
    lines += ["", f"All: {len(found)} mutants - {counts(found.values())}.", "", TIERS_NOT_RUN]
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.partition("\n")[0])
    parser.add_argument("--root", type=Path, default=ROOT, help="repository to run in")
    parser.add_argument("--base", help="branch to diff against; the default branch by default")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--all", action="store_true", help="run every mutant, not the changed ones")
    modes.add_argument(
        "--verdict",
        action="store_true",
        help="print, as JSON for docket verify, the changed lines' mutants the tests missed",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()

    def answer(change: Change, found: Mapping[str, str], listed: Listing | None = None) -> str:
        if args.verdict:
            # ASCII, so the reader decodes it the same under any locale.
            compared = compare_tests(root, change, table)
            return json.dumps(verdict(root, change, found, compared, listed), indent=1)
        return report_branch(root, change, found)

    try:
        table = mutmut_table(root)
        if args.all:
            code, log = run(root, (), table)
            if code:
                raise Refusal(f"mutmut exited {code}. The end of {log}:\n{_tail(log)}")
            files = [
                name
                for source in _strings(table, "source_paths")
                for name in working_files(root, source)
                if is_mutated(name, table)
            ]
            found = statuses(root)
            if not found:
                raise Refusal(
                    f"mutmut ran, but `mutmut results` listed no mutant. {LISTING_UNREAD}"
                )
            print(report_all(settle(root, found, recorded_exit_codes(root, files))))
            return 0
        base = args.base or default_base(root)
        if args.base is None and not resolved(base):
            raise Refusal(f"the default branch could not be established ({base!r} is a guess)")
        change = branch_change(root, base, table)
        if not change.units:
            if args.verdict:
                print(answer(change, {}))
                return 0
            print(f"No function that mutmut mutates changed against {change.against}.")
            for path, rows in change.outside.items():
                print(f"  {path}: {len(rows)} changed lines outside any function.")
            return 0
        listed = listing(root, change) if args.verdict else None
        if listed is not None and not listed.run:
            print(answer(change, {}, listed))
            return 0
        patterns = sorted(listed.run) if listed else [unit.pattern for unit in change.units]
        code, log = run(root, patterns, table)
        if code and NOTHING_MATCHES in log.read_text(encoding="utf-8", errors="replace"):
            print(answer(change, {}, listed))
            return 0
        if code:
            raise Refusal(f"mutmut exited {code}. The end of {log}:\n{_tail(log)}")
        found = statuses(root)
        if not any(fnmatch.fnmatch(name, unit.pattern) for name in found for unit in change.units):
            # mutmut exits 0 only when a pattern matched a mutant.
            raise Refusal(
                "mutmut ran, but `mutmut results` listed no mutant of the changed functions. "
                + LISTING_UNREAD
            )
        codes = recorded_exit_codes(root, {unit.path for unit in change.units})
        print(answer(change, settle(root, found, codes), listed))
        return 0
    except (Refusal, GitUnanswered, OSError, SyntaxError, ValueError, KeyError) as error:
        reason = str(error) if isinstance(error, Refusal) else repr(error)
        print(f"diff_mutation: no answer: {reason}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
