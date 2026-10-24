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
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

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
#: status. Under `-x` a test module that raises while it is imported stops the
#: run with status 1, as a failed test does. Any other status, such as 2 for an
#: interrupted run, is reported as it is, because it says nothing about the
#: mutant.
RERUN_STATUS = {0: "survived", 1: "killed"}
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
    #: A mutant measures the code, so nothing here measures whether one of
    #: these still catches what it caught before, and `verdict` says so.
    tests: list[str] = field(default_factory=list)


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
    return Change(against, changed, outside, changed_by_file, tests)


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


def run(root: Path, patterns: Sequence[str], table: Mapping[str, object]) -> tuple[int, Path]:
    """Empty `mutants/`, write the test selection into it, and run mutmut on `patterns`."""
    mutants = root / MUTANTS
    shutil.rmtree(mutants, ignore_errors=True)
    mutants.mkdir()
    tests = simulator_unit_tests(root)
    (mutants / selection_file(table)).write_text("".join(f"{t}\n" for t in tests), "utf-8")
    log = mutants / RUN_LOG
    # To stderr, so that stdout holds only the report, or under `--verdict` the JSON.
    print(
        f"Running mutmut against the {len(tests)} simulator test files under {UNIT_TESTS}/. "
        f"Its progress goes to {log.relative_to(root)}.",
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


def verdict(root: Path, change: Change, found: Mapping[str, str]) -> dict[str, object]:
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
    function, a changed function with no mutants, a changed line that carries
    `# pragma: no mutate`, and each changed test file that imports the
    simulator. A mutant measures the code, so it cannot say whether a changed
    test still catches what it caught before.
    """
    caught = 0
    uncaught: list[str] = []
    undecided: list[str] = []
    elsewhere: list[str] = []
    notes: list[str] = []
    files = {path: split_lines((root / path).read_text(encoding="utf-8")) for path in change.rows}
    if not change.units:
        notes.append(f"No function that mutmut mutates changed against {change.against}.")
    for unit in change.units:
        names = sorted(name for name in found if fnmatch.fnmatch(name, unit.pattern))
        if not names:
            notes.append(f"Not mutated: {unit.label} changed and has no mutants. {NO_MUTANTS}")
        rows = change.rows.get(unit.path)
        for name in names:
            status = found[name]
            if status in CAUGHT:
                caught += 1
                continue
            shown = _mutmut(root, "show", name)
            placed = (
                mutated_rows(unit, files[unit.path], shown.stdout) if not shown.returncode else None
            )
            if rows is not None and placed is None:
                undecided.append(f"{unit.path}: {name} - {status}, on a line not placed")
                continue
            if rows is not None and placed is not None and not placed & rows:
                elsewhere.append(name)
                continue
            where = f"{unit.path}:{min(placed)}" if placed else unit.path
            entry = "\n".join([f"{where} {name} - {status}", *_edited_lines(shown.stdout)])
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
    if elsewhere:
        notes.append(
            f"Not counted: {len(elsewhere)} mutants that the tests did not catch, on lines of the "
            f"changed functions that this branch did not change: {_listed(elsewhere)}."
        )
    if change.tests:
        notes.append(
            f"Not measured: whether {len(change.tests)} changed test files that import the "
            "simulator still catch what they caught before, since a mutant changes the code "
            f"and not a test: {_listed(change.tests)}."
        )
    if change.units:
        notes.append(TIERS_NOT_RUN)
    return {"caught": caught, "uncaught": uncaught, "undecided": undecided, "notes": notes}


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

    def answer(change: Change, found: Mapping[str, str]) -> str:
        if args.verdict:
            # ASCII, so the reader decodes it the same under any locale.
            return json.dumps(verdict(root, change, found), indent=1)
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
        code, log = run(root, [unit.pattern for unit in change.units], table)
        if code and NOTHING_MATCHES in log.read_text(encoding="utf-8", errors="replace"):
            print(answer(change, {}))
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
        print(answer(change, settle(root, found, codes)))
        return 0
    except (Refusal, GitUnanswered, OSError, SyntaxError, ValueError, KeyError) as error:
        reason = str(error) if isinstance(error, Refusal) else repr(error)
        print(f"diff_mutation: no answer: {reason}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
