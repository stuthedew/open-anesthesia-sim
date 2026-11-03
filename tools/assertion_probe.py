"""Name each assertion of a simulator test that never decides whether the test fails.

Mutation testing, as `tools/diff_mutation.py` runs it, asks whether some
assertion catches each mutant. It never asks whether each assertion catches a
mutant that the others miss. So a limit that another assertion of the same test
always overrules goes unnoticed. The step-size test's 0.5% limit sat beside a
stricter 1e-14 limit for two months that way, until a rewrite of its prose found
it (`PL-VXM0`). This tool finds such assertions, and `PL-TN0G` has the design.

**One run per mutant and test gives every assertion's answer at once.** The
tool rewrites each assertion in a copy of the test files so that it records a
failure and lets the test carry on. Each rewrite keeps every line number.

- `assert cond, msg` becomes `assert __probe__("id", (cond)), msg`.
- A call statement whose function name starts with `assert`, such as
  `np.testing.assert_allclose(...)`, or is `raises`, becomes
  `__probe_call__("id", lambda: <call>)`.
- A `with` item that calls `raises` or an `assert...` method, such as
  `pytest.raises(ValueError)`, becomes `__probe_raises__("id", <item>)`.

A run of one test under one mutant then gives the set of assertions that
failed. Those sets, over every mutant, form the kill matrix with assertions as
rows. Kurtz, Ammann, Delamaro, Offutt and Deng define the same matrix with tests
as rows ("Mutant subsumption graphs", ICST Workshops 2014, pp. 176-185,
https://doi.org/10.1109/ICSTW.2014.20).

**The mutants switch inside one pytest process per group of test files.**
mutmut's trampolines read the active mutant from `MUTANT_UNDER_TEST` at each
call (mutmut 3.8.0, `mutmut/mutation/trampoline.py`), so the plugin in this
module sets that variable and reruns the test, with no new process per mutant.
For each test, `_probe_item` takes these steps:

1. It runs the test under the mutant name `stats`, which makes each trampoline
   record the function it belongs to, so the test's reachable mutants are
   known.
2. It runs the test with no mutant, and goes no further unless the test passes
   with every assertion true and reaches at least two assertions.
3. It runs the test under each mutant of the functions it reached. Each run
   sets the test's fixtures up again, so a fixture computed from simulator code
   is computed under the mutant too. Each run has a time limit of ten times the
   clean run plus 2 s.
4. It runs the test with no mutant again. If that run fails, a mutant left
   state behind, and the test's results are marked unreliable.

Each result is written as one JSON line as soon as it is known, so a crash keeps
what was done.

**The verdict per assertion** (`verdicts`). Only a run that completed counts. A
run that raised outside an assertion, or timed out, is counted and left out,
because the assertions after the raise were never evaluated. The runs of a
parametrized test's cases count together.

- An assertion *decides* when some mutant fails it and no other assertion of
  its test.
- An assertion *never decides* when it fails for at least one mutant and every
  one of those mutants also fails another assertion of its test. This is the
  warning. It names the assertions that cover it, and says when one of them
  catches all of its mutants and more, which is the `PL-VXM0` pattern.
- An assertion that *fails for no mutant* is counted, not named. mutmut never
  changes the data files or module-level constants, so most of these guard
  values that no mutant can reach.

**What the probe cannot see.** The test modules are imported once, with no
mutant applied. So an expected value that a test module computes at import
time from simulator code is the unmutated one. That gives an assertion a kill
that a real fault might not give, which is the false kill that
`docs/mutation-testing.md` § "Pitfalls" describes. It errs toward fewer
warnings. A test that reads its own source, or another test file's, may fail
its clean run on the rewritten copy, and it is then reported as not measured.

`python3 tools/assertion_probe.py TEST...` probes the named test files or test
ids. `--sweep` probes every simulator test file under `tests/unit/` and
`tests/reference/`. `docs/mutation-testing.md` § "Assertions that never decide
a result" records what the first sweep found. The tool needs pytest and mutmut,
so run it as `uv run --group mutation python tools/assertion_probe.py`.

Exits 0 when the probe ran and its results were read, and 1 when they could
not be: the mutants could not be generated, or a pytest process failed before
it wrote a result.
"""

from __future__ import annotations

import argparse
import ast
import builtins
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from collections import Counter
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from types import FrameType, TracebackType

import pytest

#: The names the rewritten assertions call, which the plugin puts in `builtins`
#: so that no import line is added to a rewritten file.
PROBE = "__probe__"
PROBE_CALL = "__probe_call__"
PROBE_RAISES = "__probe_raises__"
#: The environment variable that mutmut 3.8.0's trampolines read the active
#: mutant from, at each call. An empty value runs the unmutated code.
MUTANT_ENV = "MUTANT_UNDER_TEST"
#: The mutant name that makes each trampoline record its function as reached.
STATS = "stats"
#: Where the plugin writes its JSON lines, and the most seconds of mutant runs
#: that one test may take before it is reported as not measured.
OUT_ENV = "ASSERTION_PROBE_OUT"
BUDGET_ENV = "ASSERTION_PROBE_BUDGET"
#: Where the plugin reads every mutant's name from, by the function it mutates.
#: The driver writes it from mutmut's `.meta` files, so the plugin needs nothing
#: but the standard library and pytest.
MUTANTS_ENV = "ASSERTION_PROBE_MUTANTS"
#: A mutant run's time limit is this many times the clean run, plus `SLACK_S`.
#: mutmut's own limit is the clean run's duration scaled the same way.
LIMIT_FACTOR = 10
SLACK_S = 2.0
#: The time limit of the two clean runs and the stats run of one test.
CLEAN_LIMIT_S = 900.0
#: The separator mutmut 3.8.0 puts between a function's mangled name and the
#: number of one of its mutants, as in `pkg.mod.x_dose__mutmut_3`.
MUTANT_SEPARATOR = "__mutmut_"
#: The outcomes of one run of one test.
RUN_COMPLETED = "completed"
RUN_RAISED = "raised"
RUN_TIMED_OUT = "timeout"
RUN_SKIPPED = "skipped"
#: The test trees `--sweep` probes.
SWEEP_TREES = ("tests/unit", "tests/reference")
#: How many covering assertions a warning names before it counts the rest.
NAMED_COVERERS = 3


# --- The rewrite --------------------------------------------------------------


def _call_name(node: ast.expr) -> str:
    """The name a call's function goes by: `assert_allclose` for `np.testing.assert_allclose`."""
    if isinstance(node, ast.Call):
        node = node.func
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
    return ""


def _is_assertion_name(name: str) -> bool:
    """Whether a call of this name is an assertion: `assert...`, or pytest's `raises`."""
    return name.startswith("assert") or name == "raises"


#: Nodes that cannot be moved into a lambda without changing what they do.
_NOT_IN_LAMBDA = (ast.Await, ast.Yield, ast.YieldFrom, ast.NamedExpr)


@dataclass(frozen=True)
class Rewritten:
    """A test file with each assertion rewritten to record its failure, and their ids."""

    source: str
    #: Each rewritten assertion's id, `path:line:column`, in file order.
    assertions: tuple[str, ...]


class _Finder(ast.NodeVisitor):
    """Collect the edits that rewrite each assertion, with the scope each one sits in."""

    def __init__(self, path: str) -> None:
        self.path = path
        #: (line, byte column, order, text). At one position, a closing edit
        #: (order 0) goes before an opening one (order 1).
        self.edits: list[tuple[int, int, int, str]] = []
        self.assertions: list[tuple[int, int, str]] = []
        self.scopes: list[ast.AST] = []

    def _ident(self, node: ast.stmt | ast.expr) -> str:
        ident = f"{self.path}:{node.lineno}:{node.col_offset}"
        self.assertions.append((node.lineno, node.col_offset, ident))
        return ident

    def _wrap(self, node: ast.expr, prefix: str, suffix: str) -> None:
        assert node.end_lineno is not None and node.end_col_offset is not None
        self.edits.append((node.lineno, node.col_offset, 1, prefix))
        self.edits.append((node.end_lineno, node.end_col_offset, 0, suffix))

    def _scoped(self, node: ast.AST) -> None:
        self.scopes.append(node)
        self.generic_visit(node)
        self.scopes.pop()

    visit_FunctionDef = visit_AsyncFunctionDef = visit_ClassDef = visit_Lambda = _scoped

    def visit_Assert(self, node: ast.Assert) -> None:
        ident = self._ident(node)
        self._wrap(node.test, f"{PROBE}({ident!r}, (", "))")
        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> None:
        call = node.value
        in_class = bool(self.scopes) and isinstance(self.scopes[-1], ast.ClassDef)
        if (
            isinstance(call, ast.Call)
            and _is_assertion_name(_call_name(call))
            and not in_class
            and not any(isinstance(inner, _NOT_IN_LAMBDA) for inner in ast.walk(call))
        ):
            ident = self._ident(node)
            self._wrap(call, f"{PROBE_CALL}({ident!r}, lambda: ", ")")
        self.generic_visit(node)

    def _visit_with(self, node: ast.With | ast.AsyncWith) -> None:
        for item in node.items:
            if _is_assertion_name(_call_name(item.context_expr)):
                ident = self._ident(item.context_expr)
                self._wrap(item.context_expr, f"{PROBE_RAISES}({ident!r}, ", ")")
        self.generic_visit(node)

    visit_With = visit_AsyncWith = _visit_with


def rewrite(path: str, source: str) -> Rewritten:
    """Rewrite each assertion in `source` to record its failure and let the test carry on.

    `path` goes into each assertion's id. The rewritten source has the same
    lines as `source`, each assertion on the line it started on, so a
    traceback and an id name the line a reader sees. `SyntaxError` where
    `source` does not parse.
    """
    finder = _Finder(path)
    finder.visit(ast.parse(source))
    # The columns that `ast` gives are byte offsets into each UTF-8 line. Python
    # also ends a line at a lone carriage return, which this split would not.
    data = source.encode("utf-8")
    if b"\r" in data.replace(b"\r\n", b""):
        raise SyntaxError(f"{path} ends a line with a lone carriage return")
    lines = [line + b"\n" for line in data.split(b"\n")]
    lines[-1] = lines[-1][:-1]
    for line, column, _, text in sorted(finder.edits, reverse=True):
        row = lines[line - 1]
        lines[line - 1] = row[:column] + text.encode("utf-8") + row[column:]
    found = tuple(ident for *_, ident in sorted(finder.assertions))
    return Rewritten(b"".join(lines).decode("utf-8"), found)


def rewrite_tree(tests: Path, root: Path) -> list[str]:
    """Rewrite every Python file under `tests` in place, and name each one that would not compile.

    `root` is the directory the ids are relative to. A file that does not parse,
    or whose rewrite does not compile, is left as it was.
    """
    # `diff_mutation` puts `docket` on the path, so it is imported first.
    import diff_mutation  # noqa: F401, I001
    from docket.vcs import tracked_under

    refused: list[str] = []
    for file in tracked_under(root, tests.relative_to(root), ".py"):
        name = file.relative_to(root).as_posix()
        source = file.read_text(encoding="utf-8")
        try:
            rewritten = rewrite(name, source)
            compile(rewritten.source, name, "exec")
        except SyntaxError:
            refused.append(name)
            continue
        if rewritten.assertions:
            file.write_text(rewritten.source, encoding="utf-8")
    return refused


# --- What the rewritten assertions call ---------------------------------------


@dataclass
class Probes:
    """The assertions evaluated, and the ones that failed, in the current run."""

    evaluated: set[str] = field(default_factory=set)
    failed: set[str] = field(default_factory=set)

    def reset(self) -> None:
        self.evaluated.clear()
        self.failed.clear()


#: The one record that the rewritten assertions of a pytest process write to.
PROBES = Probes()


def probe(ident: str, value: object) -> bool:
    """Record whether the assertion `ident` held, and return True so the test carries on."""
    PROBES.evaluated.add(ident)
    if not value:
        PROBES.failed.add(ident)
    return True


def probe_call(ident: str, call: Callable[[], object]) -> None:
    """Run an assertion call, and record that `ident` failed where it raised its failure."""
    PROBES.evaluated.add(ident)
    try:
        call()
    except (AssertionError, pytest.fail.Exception):
        PROBES.failed.add(ident)


class ProbeRaises:
    """A `pytest.raises` block that records its failure and lets the test carry on.

    The block fails when nothing is raised, when the exception raised does not
    match, and when a `match=` pattern does not match its message.
    """

    def __init__(self, ident: str, manager: object) -> None:
        self.ident = ident
        self.manager = manager

    def __enter__(self) -> object:
        PROBES.evaluated.add(self.ident)
        return self.manager.__enter__()  # type: ignore[attr-defined]

    def __exit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        try:
            handled = bool(self.manager.__exit__(kind, error, traceback))  # type: ignore[attr-defined]
        except (AssertionError, pytest.fail.Exception):
            PROBES.failed.add(self.ident)
            return True
        if kind is not None and not handled and issubclass(kind, Exception):
            # An exception of another type than the block expects.
            PROBES.failed.add(self.ident)
            return True
        return handled


def install() -> None:
    """Put the three names the rewritten assertions call into `builtins`."""
    setattr(builtins, PROBE, probe)
    setattr(builtins, PROBE_CALL, probe_call)
    setattr(builtins, PROBE_RAISES, ProbeRaises)


# --- The pytest plugin, loaded with `-p assertion_probe` ------------------------


class ProbeTimeout(BaseException):
    """A run passed its time limit. A `BaseException`, so `except Exception` cannot swallow it."""


@dataclass(frozen=True)
class Run:
    """One run of one test: how it ended, its failed assertions, and how long it took."""

    outcome: str
    failed: frozenset[str]
    evaluated: frozenset[str]
    seconds: float
    #: The first line of what a run that raised outside an assertion raised.
    error: str = ""


def mutants_by_function(names: Iterable[str]) -> dict[str, list[str]]:
    """Each mutant's name, by the name of the function it mutates, in the order given."""
    found: dict[str, list[str]] = {}
    for name in names:
        found.setdefault(name.rpartition(MUTANT_SEPARATOR)[0], []).append(name)
    return found


def run_once(item: pytest.Item, mutant: str, limit: float) -> Run:
    """Run `item` once under `mutant`, its fixtures set up afresh, within `limit` seconds."""
    from _pytest.runner import runtestprotocol

    timed_out = False

    def alarm(signum: int, frame: FrameType | None) -> None:
        nonlocal timed_out
        timed_out = True
        raise ProbeTimeout

    os.environ[MUTANT_ENV] = mutant
    PROBES.reset()
    previous = signal.signal(signal.SIGALRM, alarm)
    start = time.monotonic()
    reports = []
    try:
        signal.setitimer(signal.ITIMER_REAL, limit)
        # `nextitem=None` tears every fixture down after the run, so the next
        # run builds each one again under its own mutant.
        reports = runtestprotocol(item, log=False, nextitem=None)
    except ProbeTimeout:
        # The limit passed between two phases of the run, outside pytest's own
        # handling, so the fixtures still set up are torn down here.
        try:
            item.session._setupstate.teardown_exact(None)
        except Exception:
            # A fixture's own teardown failing changes nothing about this run.
            pass
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
        os.environ[MUTANT_ENV] = ""
    seconds = time.monotonic() - start
    error = next((_first_line(report) for report in reports if report.failed), "")
    if timed_out:
        outcome = RUN_TIMED_OUT
    elif any(report.failed for report in reports):
        outcome = RUN_RAISED
    elif any(report.skipped for report in reports):
        outcome = RUN_SKIPPED
    else:
        outcome = RUN_COMPLETED
    return Run(outcome, frozenset(PROBES.failed), frozenset(PROBES.evaluated), seconds, error)


def _first_line(report: pytest.TestReport) -> str:
    """What a failed phase of a run raised: the exception and its message, on one line."""
    crash = getattr(report.longrepr, "reprcrash", None)
    text = getattr(crash, "message", None) or str(report.longrepr)
    return " ".join(text.split())[:300]


def reached(item: pytest.Item) -> list[str]:
    """The mutated functions that `item` calls, by mutmut's `stats` run."""
    from mutmut.state import state

    state()._stats.clear()
    run_once(item, STATS, CLEAN_LIMIT_S)
    found = sorted(state()._stats)
    state()._stats.clear()
    return found


def _probe_item(
    item: pytest.Item, mutants: Mapping[str, Sequence[str]], budget: float
) -> Iterator[dict[str, object]]:
    """The JSON records of one test's runs: its clean run, each mutant's, and the check after."""
    test = item.nodeid
    functions = reached(item)
    clean = run_once(item, "", CLEAN_LIMIT_S)
    assertions = sorted(clean.evaluated)
    names = [name for function in functions for name in mutants.get(function, ())]
    head: dict[str, object] = {"test": test, "assertions": assertions, "mutants": len(names)}
    if clean.outcome != RUN_COMPLETED or clean.failed:
        failed = f", and these assertions failed: {', '.join(sorted(clean.failed))}"
        yield head | {
            "skipped": f"its run with no mutant {clean.outcome}" + failed * bool(clean.failed)
        }
        return
    if len(assertions) < 2:
        yield head | {"skipped": "it evaluates fewer than two assertions"}
        return
    if not names:
        yield head | {"skipped": "it reaches no mutated function"}
        return
    estimate = clean.seconds * len(names)
    if estimate > budget:
        yield head | {
            "skipped": f"its {len(names)} mutants would take about {estimate:.0f} s, more than "
            f"the budget of {budget:.0f} s"
        }
        return
    yield head | {"clean_s": round(clean.seconds, 4)}
    limit = LIMIT_FACTOR * clean.seconds + SLACK_S
    for name in names:
        run = run_once(item, name, limit)
        record: dict[str, object] = {
            "test": test,
            "mutant": name,
            "outcome": run.outcome,
            "failed": sorted(run.failed),
        }
        yield record | ({"error": run.error} if run.error else {})
    after = run_once(item, "", CLEAN_LIMIT_S)
    yield {"test": test, "reliable": after.outcome == RUN_COMPLETED and not after.failed}


def pytest_configure(config: pytest.Config) -> None:
    """Give the rewritten assertions the names they call."""
    install()


@pytest.hookimpl(tryfirst=True)
def pytest_runtestloop(session: pytest.Session) -> bool:
    """Probe each collected test in place of pytest's own run, and write the records."""
    if session.testsfailed and not session.config.option.continue_on_collection_errors:
        raise session.Interrupted(f"{session.testsfailed} errors during collection")
    if session.config.option.collectonly:
        return True
    out = Path(os.environ[OUT_ENV])
    budget = float(os.environ.get(BUDGET_ENV, "inf"))
    mutants = json.loads(Path(os.environ[MUTANTS_ENV]).read_text(encoding="utf-8"))
    with out.open("a", encoding="utf-8") as handle:
        for item in session.items:
            for record in _probe_item(item, mutants, budget):
                handle.write(json.dumps(record) + "\n")
                handle.flush()
    return True


# --- The verdict --------------------------------------------------------------


def _function(test: str) -> str:
    """A test id without its parameters: the cases of a parametrized test count together."""
    return test.partition("[")[0]


def _line(ident: str) -> str:
    """An assertion's id as a reader finds it: its file and line."""
    path, line, _ = ident.rsplit(":", 2)
    return f"{path}:{line}"


@dataclass
class Matrix:
    """One test's kill matrix: the assertions that failed in each completed mutant run."""

    test: str
    assertions: set[str] = field(default_factory=set)
    #: The failed assertions of each completed run, by (test case, mutant).
    runs: dict[tuple[str, str], frozenset[str]] = field(default_factory=dict)
    outcomes: Counter[str] = field(default_factory=Counter)


@dataclass
class Records:
    """What the plugin wrote: each test's matrix, and each test case it could not measure."""

    matrices: dict[str, Matrix] = field(default_factory=dict)
    #: Why each test case was not measured, by its id.
    skipped: dict[str, str] = field(default_factory=dict)
    #: The test cases whose second clean run failed, which are left out.
    unreliable: list[str] = field(default_factory=list)
    #: The test cases that started and never reached their second clean run.
    unfinished: list[str] = field(default_factory=list)


def read_records(lines: Sequence[str]) -> Records:
    """Build each test's kill matrix from the plugin's JSON lines."""
    found = Records()
    cases: dict[str, Matrix] = {}
    done: dict[str, bool] = {}
    for line in lines:
        if not line.strip():
            continue
        record = json.loads(line)
        test = record["test"]
        if "skipped" in record:
            found.skipped[test] = record["skipped"]
        elif "assertions" in record:
            cases[test] = Matrix(test, set(record["assertions"]))
        elif "mutant" in record:
            case = cases[test]
            case.outcomes[record["outcome"]] += 1
            if record["outcome"] == RUN_COMPLETED:
                case.runs[(test, record["mutant"])] = frozenset(record["failed"])
        elif "reliable" in record:
            done[test] = bool(record["reliable"])
    for test, case in cases.items():
        if test not in done:
            found.unfinished.append(test)
            continue
        if not done[test]:
            found.unreliable.append(test)
            continue
        whole = found.matrices.setdefault(_function(test), Matrix(_function(test)))
        whole.assertions |= case.assertions
        whole.runs |= case.runs
        whole.outcomes += case.outcomes
    return found


@dataclass(frozen=True)
class NeverDecides:
    """An assertion whose every caught mutant another assertion of its test also catches."""

    test: str
    assertion: str
    #: How many completed mutant runs it failed.
    caught: int
    #: Each other assertion that failed in some of those runs, with how many,
    #: most first.
    coverers: tuple[tuple[str, int], ...]
    #: The assertions that fail in every one of its runs and in more besides.
    stricter: tuple[str, ...]
    #: The assertions that fail in exactly the same runs.
    equal: tuple[str, ...]

    def sentence(self) -> str:
        """The warning, as one sentence a reviewer can act on."""
        named = ", ".join(
            f"{_line(other)} ({shared} of {self.caught})"
            for other, shared in self.coverers[:NAMED_COVERERS]
        )
        more = len(self.coverers) - NAMED_COVERERS
        named += f", and {more} more" if more > 0 else ""
        text = (
            f"{_line(self.assertion)} in {self.test} never decides a result: each of the "
            f"{self.caught} mutants it catches also fails {named}."
        )
        if self.stricter:
            text += (
                f" {_line(self.stricter[0])} alone catches all of them and more, so this "
                "assertion is the looser of the two."
            )
        elif self.equal:
            text += f" {_line(self.equal[0])} catches exactly the same mutants."
        return text


@dataclass
class Verdicts:
    """Each assertion that never decides, and how many assertions took each verdict."""

    never: list[NeverDecides] = field(default_factory=list)
    decides: int = 0
    #: Assertions that no completed mutant run failed.
    fails_for_none: int = 0
    #: Tests with fewer than two assertions, which take no verdict.
    single: int = 0
    tests: int = 0
    outcomes: Counter[str] = field(default_factory=Counter)


def verdicts(records: Records) -> Verdicts:
    """Give each assertion of each test with two or more assertions its verdict."""
    found = Verdicts()
    for name, matrix in sorted(records.matrices.items()):
        found.outcomes += matrix.outcomes
        if len(matrix.assertions) < 2:
            found.single += 1
            continue
        found.tests += 1
        caught_by = {
            assertion: {run for run, failed in matrix.runs.items() if assertion in failed}
            for assertion in matrix.assertions
        }
        for assertion in sorted(matrix.assertions):
            runs = caught_by[assertion]
            if not runs:
                found.fails_for_none += 1
                continue
            if any(matrix.runs[run] == {assertion} for run in runs):
                found.decides += 1
                continue
            shared = Counter(
                other for run in runs for other in matrix.runs[run] if other != assertion
            )
            whole = [other for other, count in shared.items() if count == len(runs)]
            found.never.append(
                NeverDecides(
                    name,
                    assertion,
                    len(runs),
                    tuple(sorted(shared.items(), key=lambda pair: (-pair[1], pair[0]))),
                    tuple(sorted(o for o in whole if len(caught_by[o]) > len(runs))),
                    tuple(sorted(o for o in whole if len(caught_by[o]) == len(runs))),
                )
            )
    return found


def report(records: Records, found: Verdicts) -> str:
    """The report: each assertion that never decides, then the counts and what was not measured."""
    lines = [
        f"Assertions that never decide a result, in {found.tests} tests with two or more "
        "assertions:",
        "",
    ]
    lines += [f"  {never.sentence()}" for never in found.never] or ["  None."]
    runs = ", ".join(f"{count} {outcome}" for outcome, count in sorted(found.outcomes.items()))
    lines += [
        "",
        f"Assertions: {found.decides} decide a result, {len(found.never)} never decide, and "
        f"{found.fails_for_none} fail for no mutant. {found.single} tests have fewer than two "
        "assertions.",
        f"Mutant runs: {runs or 'none'}. Only completed runs count.",
    ]
    reasons = Counter(_reason(reason) for reason in records.skipped.values())
    if reasons:
        lines += ["", f"Not measured: {len(records.skipped)} test cases."]
        lines += [f"  {count}: {reason}" for reason, count in reasons.most_common()]
        timed = [test for test, reason in records.skipped.items() if "budget" in reason]
        lines += [f"  Over the budget: {test}" for test in timed]
    for label, tests in (
        (
            "Left out, because a mutant left state behind that failed the run after",
            records.unreliable,
        ),
        ("Left out, because the run stopped before it finished", records.unfinished),
    ):
        if tests:
            lines += ["", f"{label}: {len(tests)} test cases."]
            lines += [f"  {test}" for test in tests]
    return "\n".join(lines)


def _reason(reason: str) -> str:
    """A skip reason with its numbers taken out, so the same reason counts together."""
    if "budget" in reason:
        return "its mutants would take longer than the budget"
    return reason.partition(", and these")[0]


# --- The driver ---------------------------------------------------------------


@dataclass
class Probed:
    """What a probe run wrote, and what it could not measure."""

    lines: list[str]
    #: Test files whose rewrite would not compile, which ran unrewritten.
    refused: list[str]


def _parts(tests: Sequence[str], jobs: int, root: Path) -> list[list[str]]:
    """Split `tests` into at most `jobs` groups of similar size, largest file first.

    The size of a test file stands in for its cost. Each file goes to the group
    with the least so far, which is Graham's longest-processing-time-first rule.
    """
    parts: list[list[str]] = [[] for _ in range(max(1, min(jobs, len(tests))))]
    sizes = [0] * len(parts)

    def size(test: str) -> int:
        file = root / test.partition("::")[0]
        return file.stat().st_size if file.is_file() else 0

    for test in sorted(tests, key=size, reverse=True):
        least = sizes.index(min(sizes))
        parts[least].append(test)
        sizes[least] += size(test)
    return [part for part in parts if part]


def run_probe(
    root: Path,
    tests: Sequence[str],
    table: Mapping[str, object],
    *,
    jobs: int = 1,
    budget: float = float("inf"),
    out: Path | None = None,
) -> Probed:
    """Probe `tests`, test files or ids under `root`, and return the plugin's JSON lines.

    The tree is copied to a scratch directory, mutmut generates every mutant
    there, and the copied test files are rewritten. Then `jobs` pytest
    processes probe the tests between them. Each writes its records to a file
    in `out`, or in the scratch directory where `out` is `None`.
    """
    # `diff_mutation` puts `docket` on the path, so it is imported first.
    import diff_mutation  # noqa: I001
    from docket.lines import split_lines

    with tempfile.TemporaryDirectory(prefix="assertion_probe_") as scratch:
        tree = Path(scratch, "tree")
        diff_mutation.copy_tree(root, tree, table)
        generated = subprocess.run(
            [sys.executable, "-c", diff_mutation.GENERATE_SCRIPT],
            cwd=tree,
            capture_output=True,
            check=False,
        )
        if generated.returncode:
            told = generated.stderr.decode("utf-8", errors="replace").strip()[-2000:]
            raise diff_mutation.Refusal(f"mutmut could not generate the mutants: {told}")
        mutants = tree / diff_mutation.MUTANTS
        refused = rewrite_tree(mutants / "tests", mutants)
        records = out or Path(scratch, "records")
        records.mkdir(parents=True, exist_ok=True)
        names = diff_mutation.recorded_exit_codes(tree, diff_mutation.mutated_files(root, table))
        listed = Path(scratch, "mutants.json")
        listed.write_text(json.dumps(mutants_by_function(names)), encoding="utf-8")
        # The plugin is this file, found on the path before the tree's own copy
        # of `tools/`, so a checkout older than this file can still be probed.
        environment = {
            **os.environ,
            "PYTHONPATH": os.pathsep.join(["src", str(Path(__file__).resolve().parent)]),
            BUDGET_ENV: str(budget),
            MUTANTS_ENV: str(listed),
            MUTANT_ENV: "",
        }
        deselect = [arg for test in diff_mutation.deselected(table) for arg in ("--deselect", test)]
        command = [
            sys.executable,
            "-m",
            "pytest",
            "--rootdir=.",
            "-q",
            # pytest's own traceback reads each frame's source with `ast` to
            # find its statement, which took 185 ms of a 190 ms run on a
            # mutated file. mutmut runs its tests with `--tb=native` too.
            "--tb=native",
            "-p",
            "no:cacheprovider",
            "-p",
            "no:randomly",
            "-p",
            "assertion_probe",
            *deselect,
        ]
        running = []
        for number, part in enumerate(_parts(tests, jobs, root)):
            target = records / f"part-{number}.jsonl"
            target.unlink(missing_ok=True)
            log = (records / f"part-{number}.log").open("w", encoding="utf-8")
            process = subprocess.Popen(
                [*command, *part],
                cwd=mutants,
                env={**environment, OUT_ENV: str(target)},
                stdout=log,
                stderr=subprocess.STDOUT,
            )
            running.append((process, target, log, part))
        lines: list[str] = []
        for process, target, log, part in running:
            code = process.wait()
            log.close()
            if not target.is_file():
                tail = Path(log.name).read_text(encoding="utf-8", errors="replace")[-2000:]
                raise diff_mutation.Refusal(
                    f"pytest exited {code} on {', '.join(part)} before it wrote a result:\n{tail}"
                )
            lines += split_lines(target.read_text(encoding="utf-8"))
        return Probed(lines, refused)


def sweep_tests(root: Path) -> list[str]:
    """Every test file under `SWEEP_TREES` that imports the simulator."""
    # `diff_mutation` puts `docket` on the path, so it is imported first.
    import diff_mutation  # noqa: I001
    from docket.arming import imports_product, is_test_file

    return [
        name
        for tree in SWEEP_TREES
        for name in diff_mutation.working_files(root, tree)
        if is_test_file(PurePosixPath(name).name)
        and imports_product(ast.parse((root / name).read_text(encoding="utf-8")))
    ]


def notes(root: Path, tests: Sequence[str], table: Mapping[str, object]) -> list[str]:
    """The notes `--verdict` prints for `tests`: each assertion that never decides, and counts."""
    if not tests:
        return []
    probed = run_probe(root, tests, table)
    records = read_records(probed.lines)
    found = verdicts(records)
    shown = [f"Never decides: {never.sentence()}" for never in found.never]
    summary = (
        f"Probed each assertion of {len(tests)} changed tests and test files: "
        f"{found.decides} decide a result, {len(found.never)} never decide, and "
        f"{found.fails_for_none} fail for no mutant."
    )
    if records.skipped or records.unreliable or records.unfinished:
        left = len(records.skipped) + len(records.unreliable) + len(records.unfinished)
        summary += f" {left} test cases were not measured; `tools/assertion_probe.py` names them."
    if probed.refused:
        summary += (
            f" Not rewritten, since the rewrite would not compile: {', '.join(probed.refused)}."
        )
    return [*shown, summary]


def main(argv: Sequence[str] | None = None) -> int:
    # `diff_mutation` puts `docket` on the path, so it is imported first.
    import diff_mutation  # noqa: I001
    from docket.lines import split_lines

    parser = argparse.ArgumentParser(description=__doc__.partition("\n")[0])
    parser.add_argument("tests", nargs="*", help="test files or test ids to probe")
    parser.add_argument("--root", type=Path, default=diff_mutation.ROOT, help="tree to probe")
    parser.add_argument("--sweep", action="store_true", help="probe every simulator test file")
    parser.add_argument("--jobs", type=int, default=1, help="pytest processes to run at once")
    parser.add_argument(
        "--budget",
        type=float,
        default=float("inf"),
        help="most seconds of mutant runs for one test case, estimated from its clean run",
    )
    parser.add_argument("--out", type=Path, help="directory to keep the JSON lines in")
    parser.add_argument(
        "--report",
        type=Path,
        nargs="+",
        help="report on JSON lines already written, and run nothing",
    )
    args = parser.parse_args(argv)
    try:
        if args.report:
            lines = [line for path in args.report for line in split_lines(path.read_text("utf-8"))]
            refused: list[str] = []
        else:
            root = args.root.resolve()
            tests = sweep_tests(root) if args.sweep else list(args.tests)
            if not tests:
                parser.error("name the tests to probe, or pass --sweep")
            table = diff_mutation.mutmut_table(root)
            probed = run_probe(root, tests, table, jobs=args.jobs, budget=args.budget, out=args.out)
            lines, refused = probed.lines, probed.refused
        records = read_records(lines)
        print(report(records, verdicts(records)))
        if refused:
            print(f"\nNot rewritten, since the rewrite would not compile: {', '.join(refused)}.")
        return 0
    except (diff_mutation.Refusal, OSError, ValueError, KeyError) as error:
        reason = str(error) if isinstance(error, diff_mutation.Refusal) else repr(error)
        print(f"assertion_probe: no answer: {reason}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
