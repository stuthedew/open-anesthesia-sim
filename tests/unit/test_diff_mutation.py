"""`tools/diff_mutation.py` must run the mutants of what a branch changed, and report them truly.

Three of its rules decide what a reader is told. Which functions changed
decides which mutants run, and a function missed there drops out of the report
with nothing to say so. Which test files run decides whether a mutant can be
killed at all. And a mutant whose pytest run raised inside mutmut is run again,
so a rerun that fails for some other reason must never count as a kill.

None of these tests runs mutmut, which is installed only with the `mutation`
dependency group. The mutant names they expect are mutmut 3.8.0's, as
`mangle_function_name` and `get_mutant_name` in `mutmut/__main__.py` build them.
"""

from __future__ import annotations

import fnmatch
import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import diff_mutation
import pytest
from diff_mutation import (
    NOTHING_MATCHES,
    TIERS_NOT_RUN,
    Change,
    Compared,
    Refusal,
    Unit,
    base_selection,
    branch_change,
    changed_rows,
    compare_tests,
    counts,
    edited_rows,
    is_mutated,
    main,
    module_name,
    mutated_rows,
    mutmut_table,
    recorded_exit_codes,
    report_all,
    report_branch,
    selection_file,
    settle,
    simulator_unit_tests,
    statuses,
    units,
    verdict,
    working_files,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

TABLE: dict[str, object] = {
    "source_paths": ["src/"],
    "only_mutate": ["src/pkg/core/*", "src/pkg/app/formatting.py"],
    "do_not_mutate": ["src/pkg/core/generated.py"],
    "pytest_add_cli_args_test_selection": [
        "@selected-tests.txt",
        "--deselect",
        "tests/unit/test_slow.py::test_walk",
    ],
}

TABLE_TOML = """\
[tool.mutmut]
source_paths = ["src/"]
only_mutate = ["src/pkg/core/*"]
pytest_add_cli_args_test_selection = ["@selected-tests.txt"]
"""

#: A module holding each kind of definition that `units` must tell apart. The
#: line numbers in the tests count from the first line of this string.
SOURCE = """\
import functools

LIMIT = 3


@functools.cache
def decorated(x):
    return x + 1


def outer(x):
    def inner(y):
        return y * 2

    return inner(x)


class Model:
    rate = 0.5

    def step(self, dt):
        return self.rate * dt

    @staticmethod
    def make():
        return Model()

    class Nested:
        def hidden(self):
            return 1


async def fetch():
    return 1
"""


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout


def _write(root: Path, path: str, text: str) -> None:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text, encoding="utf-8")


def _completed(
    stdout: str = "", returncode: int = 0, stderr: str = ""
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([], returncode, stdout=stdout, stderr=stderr)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A repository with `SOURCE` committed on `main`."""
    _git(tmp_path, "init", "-q", "-b", "main")
    for key, value in (("user.email", "t@example.com"), ("user.name", "T")):
        _git(tmp_path, "config", key, value)
    _write(tmp_path, "src/pkg/core/model.py", SOURCE)
    _write(tmp_path, "src/pkg/other.py", "def f():\n    return 1\n")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "seed")
    return tmp_path


def test_units_are_the_top_level_functions_and_the_methods_of_top_level_classes() -> None:
    found = [(u.cls, u.name, u.first, u.last) for u in units("src/pkg/core/model.py", SOURCE)]
    # A nested function is part of the function around it, and mutmut never
    # mutates a nested class. A span starts at the first decorator.
    assert found == [
        (None, "decorated", 6, 8),
        (None, "outer", 11, 15),
        ("Model", "step", 21, 22),
        ("Model", "make", 24, 26),
        (None, "fetch", 33, 34),
    ]


@pytest.mark.parametrize(
    ("patch", "rows"),
    [
        ("@@ -7 +7 @@\n-a\n+b\n", {7}),
        ("@@ -12,0 +13,2 @@\n+a\n+b\n", {13, 14}),
        # Lines deleted after line 19 count against the lines on both sides.
        ("@@ -20,2 +19,0 @@\n-a\n-b\n", {19, 20}),
        ("@@ -3 +3 @@\n-a\n+b\n@@ -30,2 +30,3 @@\n-c\n-d\n+e\n+f\n+g\n", {3, 30, 31, 32}),
    ],
)
def test_changed_rows_are_the_new_lines_of_each_hunk(patch: str, rows: set[int]) -> None:
    assert changed_rows(patch) == rows


@pytest.mark.parametrize(
    "patch", ["", "--- /dev/null\n+++ b/src/pkg/core/new.py\n@@ -0,0 +1,2 @@\n+a\n+b\n"]
)
def test_a_new_file_changes_every_line(patch: str) -> None:
    # An untracked file has no patch at all.
    assert changed_rows(patch) is None


def test_branch_change_reads_from_the_fork_to_the_working_tree(repo: Path) -> None:
    model = repo / "src/pkg/core/model.py"
    _git(repo, "checkout", "-qb", "work")
    model.write_text(SOURCE.replace("self.rate * dt", "self.rate * dt * 2"), encoding="utf-8")
    _git(repo, "commit", "-qam", "change step")
    # main moves on after the fork, in a function the branch never touched.
    _git(repo, "checkout", "-q", "main")
    model.write_text(SOURCE.replace("y * 2", "y * 3"), encoding="utf-8")
    _git(repo, "commit", "-qam", "change inner on main")
    _git(repo, "checkout", "-q", "work")
    # An uncommitted change outside any function, a module git does not track
    # yet, and a change to a file that mutmut does not mutate.
    model.write_text(
        model.read_text(encoding="utf-8").replace("LIMIT = 3", "LIMIT = 4"), encoding="utf-8"
    )
    _write(repo, "src/pkg/core/fresh.py", "def new():\n    return 1\n")
    _write(repo, "src/pkg/other.py", "def f():\n    return 2\n")

    change = branch_change(repo, "main", TABLE)

    assert [unit.label for unit in change.units] == [
        "pkg.core.fresh.new",
        "pkg.core.model.Model.step",
    ]
    assert change.outside == {"src/pkg/core/model.py": [3]}


@pytest.mark.parametrize(
    ("path", "mutated"),
    [
        ("src/pkg/core/model.py", True),
        ("src/pkg/app/formatting.py", True),
        ("src/pkg/core/generated.py", False),
        ("src/pkg/app/other.py", False),
        ("src/pkg/core/notes.txt", False),
    ],
)
def test_is_mutated_applies_the_tables_globs(path: str, mutated: bool) -> None:
    assert is_mutated(path, TABLE) is mutated


def test_is_mutated_needs_a_source_path_where_no_glob_narrows_it() -> None:
    table: dict[str, object] = {"source_paths": ["src/"]}
    assert is_mutated("src/pkg/model.py", table)
    assert not is_mutated("tools/model.py", table)


def test_mutant_names_follow_mutmuts_naming() -> None:
    path = "src/anesthesia_sim/core/uptake.py"
    assert module_name(path) == "anesthesia_sim.core.uptake"
    assert module_name("src/anesthesia_sim/core/__init__.py") == "anesthesia_sim.core"
    method = Unit(path, "UptakeSystem", "step", 3, 4)
    assert Unit(path, None, "step", 1, 2).pattern == "anesthesia_sim.core.uptake.x_step__mutmut_*"
    assert method.pattern == "anesthesia_sim.core.uptake.xǁUptakeSystemǁstep__mutmut_*"
    assert method.label == "anesthesia_sim.core.uptake.UptakeSystem.step"


def test_a_units_pattern_matches_no_other_units_mutants() -> None:
    step = Unit("src/pkg/core/model.py", None, "step", 1, 2).pattern
    assert fnmatch.fnmatch("pkg.core.model.x_step__mutmut_12", step)
    assert not fnmatch.fnmatch("pkg.core.model.x_step_size__mutmut_1", step)
    assert not fnmatch.fnmatch("pkg.core.model.xǁModelǁstep__mutmut_1", step)


def test_selection_file_is_the_one_at_file_the_table_names() -> None:
    assert selection_file(TABLE) == "selected-tests.txt"


@pytest.mark.parametrize("args", [["--deselect", "x"], ["@a.txt", "@b.txt"]])
def test_selection_file_refuses_anything_but_one_at_file(args: list[str]) -> None:
    with pytest.raises(Refusal, match="exactly one @ file"):
        selection_file({"pytest_add_cli_args_test_selection": args})


def test_every_glob_in_the_repositorys_table_matches_a_module() -> None:
    # A module renamed under a stale glob would silently stop being mutated.
    table = mutmut_table(REPO_ROOT)
    assert selection_file(table) == "selected-tests.txt"
    sources = working_files(REPO_ROOT, "src")
    for glob in diff_mutation._strings(table, "only_mutate"):
        assert any(fnmatch.fnmatch(name, glob) for name in sources), glob


def test_the_tests_that_run_are_the_unit_tests_that_import_the_simulator(repo: Path) -> None:
    _write(repo, "tests/unit/test_core.py", "from anesthesia_sim.core import uptake\n")
    _write(repo, "tests/unit/test_tool.py", "import doc_check\n")
    _write(repo, "tests/unit/helpers.py", "import anesthesia_sim\n")
    _write(repo, "tests/integration/test_run.py", "import anesthesia_sim\n")
    _write(repo, "tests/unit/test_gone.py", "import anesthesia_sim\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "tests")
    # A test file that nobody has committed yet runs too, and one deleted from
    # the working tree but still tracked does not.
    _write(repo, "tests/unit/test_new.py", "import anesthesia_sim.app\n")
    (repo / "tests/unit/test_gone.py").unlink()

    assert simulator_unit_tests(repo) == ["tests/unit/test_core.py", "tests/unit/test_new.py"]


def _stub_reruns(
    monkeypatch: pytest.MonkeyPatch, files: dict[str, list[str]], exits: dict[str, int | None]
) -> list[tuple[tuple[str, ...], str]]:
    """Answer `settle`'s two subprocess helpers from tables, and record each pytest run."""
    runs: list[tuple[tuple[str, ...], str]] = []

    def pytest_in_mutants(root: Path, named: list[str], mutant: str) -> int | None:
        runs.append((tuple(named), mutant))
        return exits[mutant]

    monkeypatch.setattr(diff_mutation, "_test_files", lambda root, name: files[name])
    monkeypatch.setattr(diff_mutation, "_pytest_in_mutants", pytest_in_mutants)
    return runs


def test_settle_reruns_each_mutant_whose_pytest_run_raised(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    raised = [f"m.x_f__mutmut_{n}" for n in range(1, 6)]
    found = dict.fromkeys([*raised, "m.x_h__mutmut_1", "m.x_k__mutmut_1"], "timeout")
    found["m.x_g__mutmut_1"] = "killed"
    codes = dict.fromkeys([*raised, "m.x_k__mutmut_1"], 255)
    codes |= {"m.x_g__mutmut_1": 1, "m.x_h__mutmut_1": -24}
    files = dict.fromkeys(raised, ["tests/unit/test_f.py"])
    files |= {"m.x_f__mutmut_2": ["tests/unit/test_e.py", "tests/unit/test_f.py"]}
    files |= {"m.x_k__mutmut_1": []}
    exits = dict(zip(["", *raised], [0, 1, 0, None, 2, 4], strict=True))
    runs = _stub_reruns(monkeypatch, files, exits)

    assert settle(tmp_path, found, codes) == {
        "m.x_f__mutmut_1": "killed",
        "m.x_f__mutmut_2": "survived",
        "m.x_f__mutmut_3": "timeout",
        "m.x_f__mutmut_4": "unsettled, pytest exited 2",
        "m.x_f__mutmut_5": "unsettled, pytest exited 4",
        # Only status 255 is rerun, so a real timeout keeps its verdict.
        "m.x_g__mutmut_1": "killed",
        "m.x_h__mutmut_1": "timeout",
        # pytest given no file would run the whole suite instead.
        "m.x_k__mutmut_1": "unsettled, mutmut names no test for it",
    }
    # The control run comes first, over every file, with no mutant applied.
    assert runs[0] == (("tests/unit/test_e.py", "tests/unit/test_f.py"), "")
    assert sorted(mutant for _, mutant in runs[1:]) == raised


def test_settle_counts_no_kill_when_the_files_fail_with_no_mutant(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    found = {"m.x_f__mutmut_1": "timeout", "m.x_g__mutmut_1": "survived"}
    codes = {"m.x_f__mutmut_1": 255, "m.x_g__mutmut_1": 0}
    files = {"m.x_f__mutmut_1": ["tests/unit/test_f.py"]}
    runs = _stub_reruns(monkeypatch, files, {"": 1, "m.x_f__mutmut_1": 1})

    assert settle(tmp_path, found, codes) == {
        "m.x_f__mutmut_1": "unsettled, its test files fail with no mutant applied",
        "m.x_g__mutmut_1": "survived",
    }
    assert runs == [(("tests/unit/test_f.py",), "")]


def test_settle_runs_nothing_when_no_pytest_run_raised(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    runs = _stub_reruns(monkeypatch, {}, {})
    found = {"m.x_f__mutmut_1": "survived"}
    assert settle(tmp_path, found, {"m.x_f__mutmut_1": 0}) == found
    assert runs == []


def test_statuses_reads_the_results_listing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    listing = (
        "    pkg.core.model.x_f__mutmut_1: killed\n"
        "    pkg.core.model.xǁModelǁstep__mutmut_2: no tests\n"
    )
    monkeypatch.setattr(diff_mutation, "_mutmut", lambda root, *a, log=None: _completed(listing))
    assert statuses(tmp_path) == {
        "pkg.core.model.x_f__mutmut_1": "killed",
        "pkg.core.model.xǁModelǁstep__mutmut_2": "no tests",
    }


def test_statuses_refuses_a_failed_listing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    failed = _completed(returncode=1, stderr="no stats\n")
    monkeypatch.setattr(diff_mutation, "_mutmut", lambda root, *a, log=None: failed)
    with pytest.raises(Refusal, match="exited 1: no stats"):
        statuses(tmp_path)


def test_test_files_are_the_files_of_the_tests_mutmut_names(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    listing = "tests/unit/test_b.py::test_z\ntests/unit/test_a.py::test_x[1]\n"
    listing += "tests/unit/test_a.py::test_y\n"
    monkeypatch.setattr(diff_mutation, "_mutmut", lambda root, *a, log=None: _completed(listing))
    assert diff_mutation._test_files(tmp_path, "m.x_f__mutmut_1") == [
        "tests/unit/test_a.py",
        "tests/unit/test_b.py",
    ]


def test_recorded_exit_codes_reads_each_files_meta(tmp_path: Path) -> None:
    meta = tmp_path / "mutants/src/pkg/core/model.py.meta"
    meta.parent.mkdir(parents=True)
    codes = {"pkg.core.model.x_f__mutmut_1": 255}
    meta.write_text(json.dumps({"exit_code_by_key": codes}), encoding="utf-8")
    # A file that mutmut wrote no meta for adds no codes.
    paths = ["src/pkg/core/model.py", "src/pkg/core/absent.py"]
    assert recorded_exit_codes(tmp_path, paths) == codes


def test_counts_puts_the_known_statuses_first() -> None:
    found = ["timeout", "odd", "killed", "survived", "killed"]
    assert counts(found) == "2 killed, 1 survived, 1 timeout, 1 odd"
    assert counts([]) == "none"


def test_the_branch_report_names_each_unit_and_shows_only_its_survivors(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    shown: list[str] = []

    def mutmut(root: Path, *args: str, log: Path | None = None) -> subprocess.CompletedProcess[str]:
        shown.append(args[1])
        return _completed(f"# {args[1]}: survived\n--- diff of {args[1]}\n")

    monkeypatch.setattr(diff_mutation, "_mutmut", mutmut)
    path = "src/pkg/core/model.py"
    step = Unit(path, "Model", "step", 21, 22)
    change = Change("main", [step, Unit(path, None, "decorated", 6, 8)], {path: [3, 4]})
    found = {
        "pkg.core.model.xǁModelǁstep__mutmut_1": "killed",
        "pkg.core.model.xǁModelǁstep__mutmut_2": "survived",
        "pkg.core.model.xǁModelǁstep__mutmut_3": "unsettled, pytest exited 4",
        "pkg.core.other.x_f__mutmut_1": "survived",
    }

    report = report_branch(tmp_path, change, found).splitlines()

    tally = "1 killed, 1 survived, 1 unsettled, pytest exited 4"
    assert report[0] == "Mutation run on the functions changed against main."
    assert f"  pkg.core.model.Model.step: 3 mutants - {tally}" in report
    assert any(line.startswith("  pkg.core.model.decorated: no mutants.") for line in report)
    assert (
        "  src/pkg/core/model.py: 2 changed lines outside any function, from line 3 to 4. "
        "mutmut never mutates module-level code or class attributes."
    ) in report
    assert f"All: 3 mutants - {tally}." in report
    # Only this change's survivor is shown, not another module's.
    assert shown == ["pkg.core.model.xǁModelǁstep__mutmut_2"]
    assert "--- diff of pkg.core.model.xǁModelǁstep__mutmut_2" in report
    assert "  pkg.core.model.xǁModelǁstep__mutmut_3: unsettled, pytest exited 4" in report
    assert report[-1] == TIERS_NOT_RUN


def test_the_whole_tree_report_gives_each_modules_kill_rate() -> None:
    found = {
        "a.b.x_f__mutmut_1": "killed",
        "a.b.x_f__mutmut_2": "survived",
        "a.b.xǁCǁm__mutmut_1": "killed",
        "a.b.xǁCǁm__mutmut_2": "timeout",
        "a.c.x_g__mutmut_1": "no tests",
    }
    report = report_all(found).splitlines()
    assert "  a.b: 2 / 3 (67%); 2 killed, 1 survived, 1 timeout" in report
    assert "  a.c: 0 / 0 (no mutant tested); 1 no tests" in report
    assert "All: 5 mutants - 2 killed, 1 survived, 1 timeout, 1 no tests." in report


@pytest.fixture
def tabled(repo: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """`repo` with a `[tool.mutmut]` table, where the branch changed one function."""
    _write(repo, "pyproject.toml", TABLE_TOML)
    unit = Unit("src/pkg/core/model.py", None, "outer", 11, 15)
    changed = Change("main", [unit], {})
    monkeypatch.setattr(diff_mutation, "branch_change", lambda root, base, table: changed)
    return repo


def _stub_run(monkeypatch: pytest.MonkeyPatch, root: Path, code: int, log_text: str) -> None:
    log = root / "run.log"
    log.write_text(log_text, encoding="utf-8")
    monkeypatch.setattr(diff_mutation, "run", lambda root, patterns, table: (code, log))


def test_main_refuses_to_report_when_mutmut_fails(
    tabled: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _stub_run(monkeypatch, tabled, 1, "failed to run clean test\n")
    assert main(["--root", str(tabled), "--base", "main"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "no answer: mutmut exited 1" in captured.err
    assert "failed to run clean test" in captured.err


def test_main_reports_no_mutants_when_no_pattern_matched(
    tabled: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _stub_run(monkeypatch, tabled, 1, f"AssertionError: {NOTHING_MATCHES}\n")
    assert main(["--root", str(tabled), "--base", "main"]) == 0
    assert "  pkg.core.model.outer: no mutants." in capsys.readouterr().out


def test_main_refuses_a_listing_that_names_no_changed_mutant(
    tabled: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _stub_run(monkeypatch, tabled, 0, "done\n")
    monkeypatch.setattr(
        diff_mutation, "statuses", lambda root: {"pkg.other.x_f__mutmut_1": "killed"}
    )
    assert main(["--root", str(tabled), "--base", "main"]) == 1
    assert "listed no mutant of the changed functions" in capsys.readouterr().err


def test_main_all_refuses_an_empty_listing(
    tabled: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _stub_run(monkeypatch, tabled, 0, "done\n")
    monkeypatch.setattr(diff_mutation, "statuses", lambda root: {})
    assert main(["--root", str(tabled), "--all"]) == 1
    assert "listed no mutant" in capsys.readouterr().err


def test_main_refuses_a_tree_with_no_table(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write(tmp_path, "pyproject.toml", '[project]\nname = "x"\n')
    assert main(["--root", str(tmp_path), "--base", "main"]) == 1
    assert "no [tool.mutmut] table" in capsys.readouterr().err


def _shown(name: str, hunk: str, *lines: str) -> str:
    """What `mutmut show` prints for one mutant: its status, two headers, then one hunk."""
    path = "src/pkg/core/model.py"
    return "\n".join([f"# {name}: survived", f"--- {path}", f"+++ {path}", hunk, *lines]) + "\n"


#: `Model.step` of `SOURCE` with its body's one line mutated, as `mutmut show`
#: prints a method: one indent shallower than it stands in the class.
STEP_SHOWN = _shown(
    "pkg.core.model.xǁModelǁstep__mutmut_1",
    "@@ -1,2 +1,2 @@",
    " def step(self, dt):",
    "-    return self.rate * dt",
    "+    return self.rate / dt",
)

#: A function with a comment directly above it, which libcst prints as its first line.
COMMENTED = "X = 1\n\n\n# The doubling.\ndef double(x):\n    y = x * 2\n    return y\n"


def test_a_mutant_is_placed_on_the_line_of_the_file_it_changes() -> None:
    step = Unit("src/pkg/core/model.py", "Model", "step", 21, 22)
    assert mutated_rows(step, SOURCE.splitlines(), STEP_SHOWN) == {22}


def test_a_comment_above_the_function_is_its_first_line_in_the_diff() -> None:
    double = Unit("src/pkg/core/model.py", None, "double", 5, 7)
    shown = _shown(
        "pkg.core.model.x_double__mutmut_1",
        "@@ -1,4 +1,4 @@",
        " # The doubling.",
        " def double(x):",
        "-    y = x * 2",
        "+    y = x / 2",
        "     return y",
    )
    assert mutated_rows(double, COMMENTED.splitlines(), shown) == {6}


@pytest.mark.parametrize(
    ("unit", "lines", "hunk"),
    [
        # The removed line reads as nothing in the function.
        (
            Unit("src/pkg/core/model.py", "Model", "step", 21, 22),
            SOURCE.splitlines(),
            ["@@ -2 +2 @@", "-    return self.rate - dt", "+    return 0"],
        ),
        # Two offsets fit, so the line it changes cannot be told.
        (
            Unit("src/pkg/core/model.py", None, "f", 3, 5),
            ["", "", "def f():", "    pass", "    pass"],
            ["@@ -3 +3 @@", "-    pass", "+    ..."],
        ),
    ],
)
def test_a_mutant_no_single_offset_places_is_not_placed(
    unit: Unit, lines: list[str], hunk: list[str]
) -> None:
    assert mutated_rows(unit, lines, _shown("pkg.core.model.x_f__mutmut_1", *hunk)) is None


@pytest.fixture
def judged(repo: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """`mutmut show`'s output by mutant name, answered from this table during the test."""
    shown: dict[str, str] = {}

    def mutmut(root: Path, *args: str, log: Path | None = None) -> subprocess.CompletedProcess[str]:
        assert args[0] == "show"
        return _completed(shown[args[1]])

    monkeypatch.setattr(diff_mutation, "_mutmut", mutmut)
    return shown


STEP = Unit("src/pkg/core/model.py", "Model", "step", 21, 22)
OUTER = Unit("src/pkg/core/model.py", None, "outer", 11, 15)


def _outer_shown(name: str) -> str:
    """A mutant of `outer`'s last line, which the tests in `verdict`'s table did not change."""
    return _shown(
        name,
        "@@ -3,3 +3,3 @@",
        "         return y * 2",
        " ",
        "-    return inner(x)",
        "+    return None",
    )


def test_the_verdict_counts_only_a_mutant_of_a_changed_line(
    repo: Path, judged: dict[str, str]
) -> None:
    judged["pkg.core.model.xǁModelǁstep__mutmut_1"] = STEP_SHOWN
    judged["pkg.core.model.x_outer__mutmut_1"] = _outer_shown("pkg.core.model.x_outer__mutmut_1")
    judged["pkg.core.model.xǁModelǁstep__mutmut_3"] = STEP_SHOWN
    change = Change(
        "main", [OUTER, STEP], {}, {"src/pkg/core/model.py": {12, 22}}, ["tests/unit/test_m.py"]
    )
    found = {
        "pkg.core.model.xǁModelǁstep__mutmut_1": "survived",
        "pkg.core.model.xǁModelǁstep__mutmut_2": "killed",
        "pkg.core.model.xǁModelǁstep__mutmut_3": "unsettled, pytest exited 4",
        "pkg.core.model.x_outer__mutmut_1": "survived",
        "pkg.core.model.x_outer__mutmut_2": "timeout",
    }

    found_verdict = verdict(repo, change, found)

    # A timeout is a catch, as PIT and Stryker count one.
    assert found_verdict["caught"] == 2
    assert found_verdict["uncaught"] == [
        "src/pkg/core/model.py:22 pkg.core.model.xǁModelǁstep__mutmut_1 - survived\n"
        "    -    return self.rate * dt\n"
        "    +    return self.rate / dt"
    ]
    assert [entry.splitlines()[0] for entry in found_verdict["undecided"]] == [
        "src/pkg/core/model.py:22 pkg.core.model.xǁModelǁstep__mutmut_3 - "
        "unsettled, pytest exited 4"
    ]
    notes = found_verdict["notes"]
    # `outer`'s survivor is on line 15, which the branch did not change.
    assert (
        "Not counted: 1 mutants that the tests did not catch, on lines of the changed "
        "functions that this branch did not change: pkg.core.model.x_outer__mutmut_1."
    ) in notes
    assert notes[-1] == TIERS_NOT_RUN


def test_a_mutant_whose_line_cannot_be_placed_is_undecided(
    repo: Path, judged: dict[str, str]
) -> None:
    judged["pkg.core.model.xǁModelǁstep__mutmut_1"] = _shown(
        "pkg.core.model.xǁModelǁstep__mutmut_1", "@@ -9 +9 @@", "-    nowhere", "+    else"
    )
    change = Change("main", [STEP], {}, {"src/pkg/core/model.py": {22}})
    found = {"pkg.core.model.xǁModelǁstep__mutmut_1": "survived"}
    found_verdict = verdict(repo, change, found)
    assert found_verdict["uncaught"] == []
    assert found_verdict["undecided"] == [
        "src/pkg/core/model.py: pkg.core.model.xǁModelǁstep__mutmut_1 - survived, "
        "on a line not placed"
    ]


def test_every_mutant_of_a_new_file_is_on_a_changed_line(
    repo: Path, judged: dict[str, str]
) -> None:
    # Placing is not needed, so a diff no offset fits still counts the mutant.
    judged["pkg.core.model.x_outer__mutmut_1"] = _shown(
        "pkg.core.model.x_outer__mutmut_1", "@@ -9 +9 @@", "-    nowhere", "+    else"
    )
    change = Change("main", [OUTER], {}, {"src/pkg/core/model.py": None})
    found = {"pkg.core.model.x_outer__mutmut_1": "no tests"}
    entries = verdict(repo, change, found)["uncaught"]
    assert [entry.splitlines()[0] for entry in entries] == [
        "src/pkg/core/model.py pkg.core.model.x_outer__mutmut_1 - no tests"
    ]


def test_the_verdict_names_what_the_run_did_not_measure(repo: Path, judged: dict[str, str]) -> None:
    model = repo / "src/pkg/core/model.py"
    model.write_text(
        SOURCE.replace("return self.rate * dt", "return self.rate * dt  # pragma: no mutate"),
        encoding="utf-8",
    )
    change = Change(
        "main",
        [Unit("src/pkg/core/model.py", None, "decorated", 6, 8)],
        {"src/pkg/core/model.py": [3]},
        {"src/pkg/core/model.py": {3, 22}},
    )
    notes = verdict(repo, change, {})["notes"]
    assert notes[0].startswith("Not mutated: pkg.core.model.decorated changed and has no mutants.")
    assert notes[1].startswith("Not mutated: 1 changed lines of src/pkg/core/model.py outside")
    assert "Exempted by `# pragma: no mutate` on a changed line: src/pkg/core/model.py:22" in notes


def test_main_prints_a_verdict_where_nothing_mutmut_mutates_changed(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _write(repo, "pyproject.toml", TABLE_TOML)
    _write(repo, "tests/unit/test_core.py", "import anesthesia_sim\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "table and test")
    _git(repo, "checkout", "-qb", "work")
    # A deleted simulator test is read from the fork's copy, and still named.
    # A test of the tooling is not the simulator's.
    (repo / "tests/unit/test_core.py").unlink()
    _write(repo, "tests/unit/test_tool.py", "import doc_check\n")
    # The deleted file holds no test, so its base version collects none.
    monkeypatch.setattr(diff_mutation, "_clean_run", lambda tree, tests: 5)

    assert main(["--root", str(repo), "--base", "main", "--verdict"]) == 0

    printed = json.loads(capsys.readouterr().out)
    assert printed["caught"] == 0
    assert printed["uncaught"] == printed["undecided"] == []
    assert printed["notes"][0] == "No function that mutmut mutates changed against main."
    assert "tests/unit/test_core.py" in printed["notes"][1]
    assert "tests/unit/test_tool.py" not in printed["notes"][1]


#: A display test file. The selection tests below change one part of it each.
DISPLAY_TEST = """\
from anesthesia_sim.app import formatting


def helper():
    return 1


def test_label():
    assert formatting.label() == "MAC"
    assert formatting.unit() == "%"


class TestReadout:
    def test_value(self):
        assert formatting.value() == 1.0
"""
#: The line `test_label` loses on the weakening branch below.
UNIT_ASSERTION = '    assert formatting.unit() == "%"\n'
UNIT_MUTANT = "anesthesia_sim.app.formatting.x_unit__mutmut_1"
LABEL_MUTANT = "anesthesia_sim.app.formatting.x_label__mutmut_1"


def _patch(base: str, branch: str, tmp_path: Path) -> str:
    """The `-U0` patch that git writes from `base` to `branch`."""
    (tmp_path / "a.py").write_text(base, encoding="utf-8")
    (tmp_path / "b.py").write_text(branch, encoding="utf-8")
    return subprocess.run(
        ["git", "diff", "--no-index", "-U0", "a.py", "b.py"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    ).stdout


@pytest.mark.parametrize(
    ("old", "new", "selected"),
    [
        # A loosened assertion selects the test that held it.
        (UNIT_ASSERTION, "", ("tests/unit/test_d.py::test_label",)),
        # A line added to a test selects the base test of the same name.
        (
            "        assert formatting.value() == 1.0\n",
            "        assert formatting.value() == 1.0\n        return\n",
            ("tests/unit/test_d.py::TestReadout::test_value",),
        ),
        # A changed helper can change every test, so the whole file is selected.
        ("    return 1\n", "    return 2\n", ("tests/unit/test_d.py",)),
        # A new test leaves the base version's tests as they were.
        ("", "\n\ndef test_more():\n    assert formatting.more()\n", ()),
        # A comment cannot change what a test does.
        ("def test_label():\n", "# Pins the label.\ndef test_label():\n", ()),
    ],
)
def test_base_selection_is_the_base_tests_the_branch_changed(
    old: str, new: str, selected: tuple[str, ...], tmp_path: Path
) -> None:
    branch = DISPLAY_TEST.replace(old, new) if old else DISPLAY_TEST + new
    patch = _patch(DISPLAY_TEST, branch, tmp_path)
    assert base_selection("tests/unit/test_d.py", DISPLAY_TEST, branch, patch) == selected


def test_a_deleted_test_file_is_compared_whole() -> None:
    assert base_selection("tests/unit/test_d.py", DISPLAY_TEST, None, "") == (
        "tests/unit/test_d.py",
    )


def test_edited_rows_leave_out_blank_lines_and_comments(tmp_path: Path) -> None:
    branch = DISPLAY_TEST.replace("    return 1\n", "    # One.\n\n    return 1\n")
    patch = _patch(DISPLAY_TEST, branch, tmp_path)
    assert edited_rows(patch, DISPLAY_TEST.splitlines(), branch.splitlines()) == (set(), set())


@dataclass
class Runs:
    """What the stubbed mutmut runs of `compare_tests` report, and what they were asked."""

    base: dict[str, str] = field(default_factory=dict)
    branch: dict[str, str] = field(default_factory=dict)
    clean: int = 0
    #: Each run's tree name, patterns, tests, and the changed test file's text there.
    asked: list[tuple[str, list[str], list[str], str]] = field(default_factory=list)


@pytest.fixture
def runs(repo: Path, monkeypatch: pytest.MonkeyPatch) -> Runs:
    """`repo` with a display test on `main` and a branch `work`, and mutmut runs stubbed."""
    _write(repo, "pyproject.toml", TABLE_TOML)
    _write(repo, "tests/unit/test_d.py", DISPLAY_TEST)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "display test")
    _git(repo, "checkout", "-qb", "work")
    stubbed = Runs()

    def display_statuses(
        tree: Path, patterns: list[str], tests: list[str], table: object, files: object
    ) -> dict[str, str]:
        text = (tree / "tests/unit/test_d.py").read_text(encoding="utf-8")
        stubbed.asked.append((tree.name, list(patterns), list(tests), text))
        return stubbed.base if tree.name == "base" else stubbed.branch

    shown = "@@ -1,1 +1,1 @@\n-    return unit\n+    return None\n"
    monkeypatch.setattr(diff_mutation, "_display_statuses", display_statuses)
    monkeypatch.setattr(diff_mutation, "_clean_run", lambda tree, tests: stubbed.clean)
    monkeypatch.setattr(diff_mutation, "_mutmut", lambda root, *a, log=None: _completed(shown))
    return stubbed


def _weakened(repo: Path) -> Change:
    """The branch's change once it drops the unit assertion from `test_label`."""
    _write(repo, "tests/unit/test_d.py", DISPLAY_TEST.replace(UNIT_ASSERTION, ""))
    return branch_change(repo, "main", mutmut_table(repo))


def test_a_branch_that_weakens_a_display_test_is_refused(repo: Path, runs: Runs) -> None:
    runs.base = {
        UNIT_MUTANT: "killed",
        LABEL_MUTANT: "killed",
        "anesthesia_sim.app.formatting.x_value__mutmut_1": "survived",
    }
    runs.branch = {UNIT_MUTANT: "survived", LABEL_MUTANT: "killed"}
    change = _weakened(repo)

    found = verdict(repo, change, {}, compare_tests(repo, change, mutmut_table(repo)))

    # The base run holds the base version, and runs every display mutant
    # against the test the branch changed. The branch run takes only the
    # mutants that the base run caught, against the whole changed file.
    assert runs.asked == [
        ("base", ["anesthesia_sim.app.*"], ["tests/unit/test_d.py::test_label"], DISPLAY_TEST),
        (
            "branch",
            [LABEL_MUTANT, UNIT_MUTANT],
            ["tests/unit/test_d.py"],
            DISPLAY_TEST.replace(UNIT_ASSERTION, ""),
        ),
    ]
    assert found["uncaught"] == [
        f"tests/unit/test_d.py: {UNIT_MUTANT} - caught by the base version, survived on this "
        "branch's version\n"
        "    -    return unit\n"
        "    +    return None"
    ]
    assert found["undecided"] == []


def test_a_branch_whose_changed_test_still_catches_every_mutant_passes(
    repo: Path, runs: Runs
) -> None:
    runs.base = runs.branch = {UNIT_MUTANT: "killed"}

    compared = compare_tests(repo, _weakened(repo), mutmut_table(repo))

    assert compared.uncaught == compared.undecided == []
    assert compared.notes[-1].startswith("Compared: 1 mutants of anesthesia_sim.app")


@pytest.mark.parametrize(
    ("status", "uncaught"), [("no tests", True), ("suspicious", False), ("timeout", None)]
)
def test_the_branch_runs_status_decides_where_a_mutant_goes(
    repo: Path, runs: Runs, status: str, uncaught: bool | None
) -> None:
    runs.base = {UNIT_MUTANT: "killed"}
    runs.branch = {UNIT_MUTANT: status}

    compared = compare_tests(repo, _weakened(repo), mutmut_table(repo))

    # A timeout is a catch on the branch's side too, and an unknown status
    # decides nothing.
    assert len(compared.uncaught) == (uncaught is True)
    assert len(compared.undecided) == (uncaught is False)


def test_a_mutant_the_branch_run_does_not_list_counts_as_untested(repo: Path, runs: Runs) -> None:
    runs.base = {UNIT_MUTANT: "killed"}

    compared = compare_tests(repo, _weakened(repo), mutmut_table(repo))

    assert compared.uncaught[0].startswith(f"tests/unit/test_d.py: {UNIT_MUTANT} - caught by")
    assert "no tests on this branch's version" in compared.uncaught[0]


def test_a_base_test_that_fails_on_the_branchs_source_is_not_compared(
    repo: Path, runs: Runs
) -> None:
    runs.clean = 1

    compared = compare_tests(repo, _weakened(repo), mutmut_table(repo))

    assert runs.asked == []
    assert compared == Compared(
        notes=[
            "Not compared: tests/unit/test_d.py, because the tests of its base version that "
            "this branch changed fail on this branch's source with no mutant applied, so the "
            "branch changed what they check."
        ]
    )


def test_a_branch_that_only_adds_a_test_runs_nothing(repo: Path, runs: Runs) -> None:
    _write(repo, "tests/unit/test_d.py", DISPLAY_TEST + "\n\ndef test_more():\n    assert 1\n")
    change = branch_change(repo, "main", mutmut_table(repo))

    assert compare_tests(repo, change, mutmut_table(repo)) == Compared()
    assert runs.asked == []


def test_a_changed_test_outside_the_unit_tests_is_named_and_not_compared(
    repo: Path, runs: Runs
) -> None:
    _write(repo, "tests/integration/test_run.py", "import anesthesia_sim\n")
    change = branch_change(repo, "main", mutmut_table(repo))

    compared = compare_tests(repo, change, mutmut_table(repo))

    assert compared.notes == [
        "Not measured: whether 1 changed test files outside tests/unit/ still catch what they "
        "caught before: tests/integration/test_run.py."
    ]
    assert runs.asked == []
