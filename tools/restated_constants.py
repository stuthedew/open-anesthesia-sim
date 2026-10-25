#!/usr/bin/env python3
"""Name each test that copies a supported-range limit's value instead of importing its name.

A test that writes `86_400.0` where it means
`MAXIMUM_ELAPSED_SIMULATION_TIME_S` passes on every run until the limit moves.
Then it fails for a reason that is not a defect, and that is the kind of
failure that teaches a session to edit the test rather than the code.
`PL-T5J5` found eight such tests by hand. It set the limit to 48 h and read
which tests broke: 9 of 3,670 failed, and 8 of those failures were spurious.
This script runs that method on a schedule (`PL-0Z0F`).

**What it does.** It reads `src/anesthesia_sim/core/supported_ranges.py` with
`ast` and lists each public module-level name bound to a number. For each one
it runs the tests under `tests/` once, with the constant set to a wrong value
through the `PERTURBED_CONSTANT_VARIABLE` environment variable, which
`tests/conftest.py` reads. It collects the tests that fail. A failing test
whose file imports the constant by name is expected to fail, such as the pin
in `tests/unit/test_supported_ranges.py` that asserts the limit is 86,400 s.
Any other failing test is reported, after one more run without the
perturbation confirms that the test passes there. The script exits non-zero
when it reports a test.

**Which way a value moves.** A wrong value widens the supported interval by
its own width. A `MAXIMUM_` name moves up by the distance between it and its
paired `MINIMUM_` name. A maximum with no paired minimum is measured from
zero, so `MAXIMUM_ELAPSED_SIMULATION_TIME_S` doubles to 48 h, as in
`PL-T5J5`. Narrowing the interval would instead fail every test that uses an
ordinary setting near the limit, which says nothing about whether the test
restates it. Widening fails a test that asserts a value past the old limit is
refused, or that otherwise depends on where the limit sits.

A `MINIMUM_` name moves down by the same distance, but never below zero. A
floor at zero is not moved at all, and the report says so without failing.
Every quantity the module bounds is a flow or a time, which cannot be
negative, so admitting a negative value breaks the model's own arithmetic.
Measured on 2026-10-25, lowering the three zero floors failed 52 tests, and
the three that did not import the floor's name failed for that reason or
through a subprocess, not because they copied a zero. A test that copies a
floor of zero writes `0.0`, which no perturbation can tell from an ordinary
zero setting such as apnoea.

**What it cannot see.** It reports what it could not judge rather than
dropping it, and each of these makes the run fail:

- a constant that no rule above can move, such as a name with neither prefix;
- a run of the suite that pytest did not finish, or whose output does not
  show that the perturbation was applied;
- a test that fails without the perturbation too.

A failing test whose file imports `subprocess` is listed as not judged, and
does not fail the run. The process it starts imports the unperturbed module,
so it can fail by comparing the two processes, as
`tests/integration/test_cross_process_determinism.py` does, without copying
anything. A restating test in such a file is listed among them, not named.

Two kinds of restating test pass the perturbed run and so are never named. A
test that reads the constant only through a subprocess it starts sees the
unperturbed module. A test that copies the value only as a value just inside
the limit still passes, because the limit moved outwards.

A test listed in `TRIPWIRES` for the constant being moved is reported as
failing on purpose and does not fail the run. Each one either holds a literal
measured at the current limit and checks it against the limit that the
simulator computes, or pins a refusal message whole as a test's expected
value. Its failure asks for a re-measurement or a rewrite rather than showing
a copy.

**How a test is judged.** A failing test counts as reading the constant when
its file imports it, by `from anesthesia_sim.core.supported_ranges import
NAME` or by importing the module and reading `NAME` as an attribute, and the
test itself uses it. The test uses it when its body, its decorators or its
class's decorators name it, or name a function, class, fixture or constant
defined in the same file that uses it. So a test that copies the value is
named even when other tests in its file import the name. A test that gets
the value through a helper module or a `conftest.py` fixture is also named.
The cases of one parametrized test are judged together, so a case that
copies the value beside a case that names the constant is not seen. Whether
a reported test should change is left to the session that reads the report.

The suite takes several minutes for each constant, so this runs in the
`restated-constants` job of `.github/workflows/drift.yml` and not in
`make check`. `--constant NAME` limits a run to the named constants. Standard
library only, like every tool under `tools/`, though it runs pytest from the
project's environment as a subprocess.
"""

from __future__ import annotations

import argparse
import ast
import math
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ElementTree
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: The module whose constants are perturbed, by import name and by path.
RANGES_MODULE = "anesthesia_sim.core.supported_ranges"
RANGES_SOURCE = ROOT / "src" / "anesthesia_sim" / "core" / "supported_ranges.py"

#: The one environment variable `tests/conftest.py` reads, holding `NAME=VALUE`.
PERTURBED_CONSTANT_VARIABLE = "ANESTHESIA_SIM_PERTURB_CONSTANT"

#: The test tree that is run. `subprojects/docket/tests` never imports the
#: simulator, so a constant cannot change its result.
SUITE = "tests"

#: Tests that fail on purpose when a limit moves, keyed by the limit and by
#: the test function, with the reason. A key names the function, so it covers
#: every parametrized case of it. Two kinds are listed. One holds a literal
#: measured at the current limit, such as the length of a published-fit
#: washout, and checks it against the limit read from the simulator. The other
#: pins a refusal message whole, as `.claude/rules/test-oracles.md` asks of a
#: message a learner sees, so its expected text is written out rather than
#: built from the limit. Either failure is the prompt to re-measure or rewrite,
#: not a copy of the limit, so the report lists it and does not fail the run.
_PINNED_MESSAGE = (
    "it pins the refusal message whole, as .claude/rules/test-oracles.md asks, so a "
    "moved limit means rewriting the message it expects"
)
TRIPWIRES: Mapping[tuple[str, str], str] = {
    (
        "MAXIMUM_ELAPSED_SIMULATION_TIME_S",
        "tests/reference/test_late_washout_against_published_fits.py"
        "::test_the_run_ends_at_the_supported_run_length",
    ): (
        "its tables were measured over ELIMINATION_DURATION_MIN, which it checks against "
        "maximum_step_count, so a new run length means re-measuring them"
    ),
    (
        "MAXIMUM_ELAPSED_SIMULATION_TIME_S",
        "tests/integration/test_controller.py"
        "::test_the_refusal_to_branch_at_the_supported_run_length_is_pinned_whole",
    ): _PINNED_MESSAGE,
    **{
        (
            name,
            "tests/unit/test_supported_ranges.py::test_a_setting_s_range_refusal_is_pinned_whole",
        ): (_PINNED_MESSAGE)
        for name in (
            "MAXIMUM_FRESH_GAS_FLOW_L_MIN",
            "MAXIMUM_ALVEOLAR_VENTILATION_L_MIN",
            "MAXIMUM_CARDIAC_OUTPUT_L_MIN",
        )
    },
    (
        "MAXIMUM_FRESH_GAS_FLOW_L_MIN",
        "tests/unit/test_dashboard_frame.py"
        "::test_an_opening_fresh_gas_flow_off_the_slider_grid_is_refused",
    ): _PINNED_MESSAGE,
    **{
        (
            name,
            "tests/unit/test_dashboard_frame.py"
            "::test_an_opening_ventilation_or_cardiac_output_off_the_slider_grid_is_refused",
        ): _PINNED_MESSAGE
        for name in ("MAXIMUM_ALVEOLAR_VENTILATION_L_MIN", "MAXIMUM_CARDIAC_OUTPUT_L_MIN")
    },
}


def tripwire_reason(name: str, nodeid: str) -> str | None:
    """Why the test `nodeid` fails on purpose when `name` moves, or `None` if it is not listed.

    The parameters in brackets after the function's name are dropped, so a
    listed function covers each of its cases.
    """

    return TRIPWIRES.get((name, nodeid.partition("[")[0]))


MINIMUM_PREFIX = "MINIMUM_"
MAXIMUM_PREFIX = "MAXIMUM_"


@dataclass(frozen=True)
class Constant:
    """A public module-level name bound to a number."""

    name: str
    value: float


def _number(node: ast.expr) -> float | None:
    """The value of a number literal, negated or not, or `None` for anything else."""

    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        inner = _number(node.operand)
        return None if inner is None else -inner
    if (
        isinstance(node, ast.Constant)
        and isinstance(node.value, (int, float))
        and not isinstance(node.value, bool)
    ):
        return float(node.value)
    return None


def _bound_name(node: ast.stmt) -> tuple[str, ast.expr] | None:
    """The name and value of a module-level binding of one name, or `None`."""

    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        target = node.targets[0]
        if isinstance(target, ast.Name):
            return target.id, node.value
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value:
        return node.target.id, node.value
    return None


def numeric_constants(source: str) -> list[Constant]:
    """Each public upper-case module-level name in `source` bound to a number literal."""

    constants = []
    for node in ast.parse(source).body:
        bound = _bound_name(node)
        if bound is None:
            continue
        name, value = bound
        number = _number(value)
        if number is not None and name.isupper() and not name.startswith("_"):
            constants.append(Constant(name, number))
    return constants


def widened(constant: Constant, constants: Sequence[Constant]) -> float | None:
    """The wrong value that widens `constant`'s interval by its width, or `None`.

    The module docstring gives the rule. `None` means that no rule moves this
    constant, or that its interval has no width to widen by.
    """

    values = {each.name: each.value for each in constants}
    if constant.name.startswith(MAXIMUM_PREFIX):
        partner = MINIMUM_PREFIX + constant.name.removeprefix(MAXIMUM_PREFIX)
        width = constant.value - values.get(partner, 0.0)
        return constant.value + width if width > 0 else None
    if constant.name.startswith(MINIMUM_PREFIX) and not is_zero_floor(constant):
        partner = MAXIMUM_PREFIX + constant.name.removeprefix(MINIMUM_PREFIX)
        if partner not in values:
            return None
        width = values[partner] - constant.value
        return max(constant.value - width, 0.0) if width > 0 else None
    return None


def is_zero_floor(constant: Constant) -> bool:
    """Whether `constant` is a floor at zero, which the module docstring says is not moved."""

    return constant.name.startswith(MINIMUM_PREFIX) and constant.value == 0.0


def parse_perturbation(text: str) -> tuple[str, float]:
    """Read `NAME=VALUE` from the environment variable, refusing any other shape."""

    name, sign, value = text.partition("=")
    try:
        number = float(value)
    except ValueError:
        number = math.nan
    if not sign or not name or not math.isfinite(number):
        raise ValueError(
            f"{PERTURBED_CONSTANT_VARIABLE}={text!r} is not NAME=VALUE with a finite "
            f"number, such as MAXIMUM_ELAPSED_SIMULATION_TIME_S=172800.0"
        )
    return name, number


def perturbed_tree(source: str, name: str, value: float) -> ast.Module:
    """`source` parsed, with the one module-level binding of `name` set to `value`.

    Raises `ValueError` unless exactly one module-level statement binds `name`
    to a number literal, so a perturbation that would reach nothing fails
    instead of running an unperturbed suite.
    """

    tree = ast.parse(source)
    replaced = 0
    for node in tree.body:
        bound = _bound_name(node)
        if bound is None or bound[0] != name or _number(bound[1]) is None:
            continue
        literal = ast.copy_location(ast.Constant(value), bound[1])
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            node.value = literal
        replaced += 1
    if replaced != 1:
        raise ValueError(
            f"{RANGES_MODULE} binds {name} to a number {replaced} times at module level, "
            "and a perturbation needs exactly one such binding to replace"
        )
    return ast.fix_missing_locations(tree)


def perturbation_line(name: str, value: float) -> str:
    """The line `tests/conftest.py` prints in pytest's header when it perturbs a constant."""

    return f"{PERTURBED_CONSTANT_VARIABLE}: {RANGES_MODULE}.{name} = {value!r}"


def _dotted(node: ast.expr) -> str | None:
    """`a.b.c` for a chain of attribute reads on a name, or `None`."""

    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        head = _dotted(node.value)
        return None if head is None else f"{head}.{node.attr}"
    return None


def imports_name(source: str, name: str) -> bool:
    """Whether `source` imports `name` from the ranges module, or reads it from that module."""

    package, _, leaf = RANGES_MODULE.rpartition(".")
    module_names: set[str] = set()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level == 0:
            if node.module == RANGES_MODULE and any(
                alias.name in (name, "*") for alias in node.names
            ):
                return True
            if node.module == package:
                module_names.update(
                    alias.asname or leaf for alias in node.names if alias.name == leaf
                )
        elif isinstance(node, ast.Import):
            module_names.update(
                alias.asname or RANGES_MODULE for alias in node.names if alias.name == RANGES_MODULE
            )
    return any(
        isinstance(node, ast.Attribute)
        and node.attr == name
        and _dotted(node.value) in module_names
        for node in ast.walk(tree)
    )


@dataclass(frozen=True)
class Failure:
    """A test that failed or errored, by its pytest node id and its file."""

    nodeid: str
    file: str


def failures_in(junit_xml: str) -> list[Failure]:
    """The failed and errored tests in a JUnit report written with `junit_family=xunit1`.

    `xunit1` is the family that records each test's file. A module that failed
    to collect is reported as its file.
    """

    found: dict[str, Failure] = {}
    for case in ElementTree.fromstring(junit_xml).iter("testcase"):
        if case.find("failure") is None and case.find("error") is None:
            continue
        file = case.get("file", "")
        classname = case.get("classname", "")
        if not classname:
            nodeid = file
        else:
            module = file.removesuffix(".py").replace("/", ".")
            classes = classname[len(module) + 1 :].split(".") if classname != module else []
            nodeid = "::".join([file, *classes, case.get("name", "")])
        found.setdefault(nodeid, Failure(nodeid, file))
    return list(found.values())


def _references(node: ast.AST) -> set[str]:
    """Every name `node` reads, as a bare name, an attribute or a parameter."""

    found: set[str] = set()
    for inner in ast.walk(node):
        if isinstance(inner, ast.Name):
            found.add(inner.id)
        elif isinstance(inner, ast.Attribute):
            found.add(inner.attr)
        elif isinstance(inner, ast.arg):
            found.add(inner.arg)
    return found


def _module_readers(tree: ast.Module, name: str) -> set[str]:
    """The module-level functions, classes and assignments that read `name`, directly or not.

    A test's parameter counts as a reference, so a fixture defined in the same
    file that reads `name` makes the test that asks for it a reader too.
    """

    defined: dict[str, set[str]] = {}
    for statement in tree.body:
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.setdefault(statement.name, set()).update(_references(statement))
        elif isinstance(statement, (ast.Assign, ast.AnnAssign)):
            targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
            for target in targets:
                for bound in ast.walk(target):
                    if isinstance(bound, ast.Name):
                        defined.setdefault(bound.id, set()).update(_references(statement))
    readers = {key for key, refs in defined.items() if name in refs}
    while True:
        more = {key for key, refs in defined.items() if key not in readers and refs & readers}
        if not more:
            return readers
        readers |= more


def uses_name(source: str, nodeid: str, name: str) -> bool:
    """Whether the test `nodeid` in `source` reads `name` from the ranges module.

    The file must import `name`, and the test itself must read it: in its own
    body, its decorators, its class's decorators, or through a function,
    class, fixture or constant defined in the same file that reads it. A test
    whose file imports the name for other tests and that copies the value is
    so still named. A test that is not found in its file is judged not to read
    it, so it is named and a person looks at it.
    """

    if not imports_name(source, name):
        return False
    tree = ast.parse(source)
    path = [part.partition("[")[0] for part in nodeid.split("::")[1:]]
    scope: Sequence[ast.stmt] = tree.body
    references: set[str] = set()
    found = False
    for depth, part in enumerate(path):
        match = next(
            (
                node
                for node in scope
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                and node.name == part
            ),
            None,
        )
        if match is None:
            return False
        if depth == len(path) - 1:
            references |= _references(match)
            found = True
        else:
            for decorator in match.decorator_list:
                references |= _references(decorator)
            scope = match.body
    if not found:
        return False
    return name in references or bool(references & _module_readers(tree, name))


def restating(failures: Sequence[Failure], name: str, read: Callable[[str], str]) -> list[Failure]:
    """The failures that do not read `name` themselves, their files read through `read(file)`."""

    return [
        failure for failure in failures if not uses_name(read(failure.file), failure.nodeid, name)
    ]


def starts_a_subprocess(source: str) -> bool:
    """Whether `source` imports `subprocess`, so a test in it can start a process."""

    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import) and any(a.name == "subprocess" for a in node.names):
            return True
        if isinstance(node, ast.ImportFrom) and node.module == "subprocess":
            return True
    return False


@dataclass(frozen=True)
class SuiteRun:
    """One run of pytest: its exit status, its failures, and what it printed."""

    status: int
    failures: list[Failure]
    output: str


def run_suite(targets: Sequence[str], workers: str, environment: Mapping[str, str]) -> SuiteRun:
    """Run pytest over `targets` with `environment`, and read its JUnit report."""

    with tempfile.TemporaryDirectory() as scratch:
        report = Path(scratch) / "junit.xml"
        command = [
            sys.executable,
            "-m",
            "pytest",
            *targets,
            "-n",
            workers,
            "--dist",
            "worksteal",
            "-p",
            "no:cacheprovider",
            "--continue-on-collection-errors",
            f"--junitxml={report}",
            "-o",
            "junit_family=xunit1",
        ]
        done = subprocess.run(
            command, cwd=ROOT, env=dict(environment), capture_output=True, check=False
        )
        text = report.read_text(encoding="utf-8") if report.exists() else ""
    failures = failures_in(text) if text else []
    output = (done.stdout + done.stderr).decode("utf-8", errors="replace")
    return SuiteRun(done.returncode, failures, output)


@dataclass
class Finding:
    """What one constant's perturbed run showed."""

    constant: Constant
    value: float
    failed: int = 0
    restating: tuple[str, ...] = ()
    #: Tests that also fail without the perturbation, so were not judged.
    unjudged: tuple[str, ...] = ()
    #: Tests in a file that imports `subprocess`, which were not judged.
    through_subprocess: tuple[str, ...] = ()
    #: Tests on `TRIPWIRES`, which fail on purpose when the limit moves.
    tripwires: tuple[str, ...] = ()
    #: Why the run gave no answer, or an empty string when it gave one.
    declined: str = ""


def judge(constant: Constant, value: float, workers: str) -> Finding:
    """Run the suite with `constant` set to `value`, and name the tests that restate it."""

    finding = Finding(constant, value)
    environment = {**os.environ, PERTURBED_CONSTANT_VARIABLE: f"{constant.name}={value!r}"}
    run = run_suite([SUITE], workers, environment)
    if run.status not in (0, 1):
        finding.declined = f"pytest exited with status {run.status}:\n{run.output[-2000:]}"
        return finding
    if perturbation_line(constant.name, value) not in run.output:
        finding.declined = "pytest's output does not show the perturbation was applied"
        return finding
    finding.failed = len(run.failures)
    sources: dict[str, str] = {}

    def read(file: str) -> str:
        if file not in sources:
            sources[file] = (ROOT / file).read_text(encoding="utf-8")
        return sources[file]

    candidates = []
    through_subprocess = []
    for failure in restating(run.failures, constant.name, read):
        if starts_a_subprocess(read(failure.file)):
            through_subprocess.append(failure.nodeid)
        else:
            candidates.append(failure)
    finding.through_subprocess = tuple(through_subprocess)
    if not candidates:
        return finding
    plain = {key: text for key, text in os.environ.items() if key != PERTURBED_CONSTANT_VARIABLE}
    rerun = run_suite([failure.nodeid for failure in candidates], workers, plain)
    if rerun.status not in (0, 1):
        finding.declined = (
            f"the rerun without the perturbation exited with status {rerun.status}:\n"
            f"{rerun.output[-2000:]}"
        )
        return finding
    still = {failure.nodeid for failure in rerun.failures}
    restated = [f.nodeid for f in candidates if f.nodeid not in still]
    on_purpose = {nodeid for nodeid in restated if tripwire_reason(constant.name, nodeid)}
    finding.restating = tuple(nodeid for nodeid in restated if nodeid not in on_purpose)
    finding.tripwires = tuple(nodeid for nodeid in restated if nodeid in on_purpose)
    finding.unjudged = tuple(f.nodeid for f in candidates if f.nodeid in still)
    return finding


def report(
    findings: Sequence[Finding], unmoved: Sequence[Constant], floors: Sequence[Constant] = ()
) -> tuple[str, bool]:
    """The report's text, and whether it names anything that fails the run.

    `unmoved` holds the constants no rule could move, which fail the run, and
    `floors` the floors at zero, which are left alone by rule and do not.
    """

    lines = []
    failing = bool(unmoved)
    for finding in findings:
        constant = finding.constant
        head = f"{constant.name} {constant.value!r} -> {finding.value!r}"
        if finding.declined:
            failing = True
            lines.append(f"{head}: no answer, because {finding.declined}")
            continue
        lines.append(
            f"{head}: {finding.failed} tests failed, {len(finding.restating)} of them named "
            "as restating it"
        )
        lines.extend(f"  restates it: {nodeid}" for nodeid in finding.restating)
        lines.extend(
            f"  fails on purpose, because {tripwire_reason(constant.name, nodeid)}: {nodeid}"
            for nodeid in finding.tripwires
        )
        lines.extend(
            f"  not judged, fails without the perturbation too: {nodeid}"
            for nodeid in finding.unjudged
        )
        lines.extend(
            f"  not judged, its file imports subprocess: {nodeid}"
            for nodeid in finding.through_subprocess
        )
        failing = failing or bool(finding.restating or finding.unjudged)
    lines.extend(
        f"{constant.name}: not perturbed, because no rule widens it; teach `widened` one"
        for constant in unmoved
    )
    lines.extend(
        f"{constant.name}: not perturbed, because it is a floor at zero" for constant in floors
    )
    lines.append(
        "Not seen by this run: a test that reads a constant only through a subprocess, "
        "a test that copies only a value just inside a limit, and a parametrized case "
        "that copies a value while another case of the same test names the constant."
    )
    return "\n".join(lines), failing


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "--constant",
        action="append",
        metavar="NAME",
        help="perturb only this constant; repeat for more. The default is every one.",
    )
    parser.add_argument(
        "--workers", default="auto", help="pytest-xdist's -n for each run (default: auto)"
    )
    options = parser.parse_args(argv)

    constants = numeric_constants(RANGES_SOURCE.read_text(encoding="utf-8"))
    known = {constant.name for constant in constants}
    unknown = sorted(set(options.constant or ()) - known)
    if unknown:
        parser.error(f"{RANGES_MODULE} has no numeric constant named {', '.join(unknown)}")
    chosen = [c for c in constants if not options.constant or c.name in options.constant]

    findings = []
    unmoved = []
    floors = []
    for constant in chosen:
        if is_zero_floor(constant):
            floors.append(constant)
            continue
        value = widened(constant, constants)
        if value is None:
            unmoved.append(constant)
            continue
        print(f"perturbing {constant.name} to {value!r}", flush=True)
        findings.append(judge(constant, value, options.workers))

    text, failing = report(findings, unmoved, floors)
    print(text)
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
