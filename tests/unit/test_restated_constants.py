"""Tests for `tools/restated_constants.py`, the scheduled search for tests that copy a limit.

The tool runs the whole suite once per constant, which is far too slow for a
unit test. So these tests pin the parts of it that decide the answer: which
constants it moves and to what, which file counts as importing a constant,
how a JUnit report becomes node ids, and which failures the report names.
The `restated-constants` job in `.github/workflows/drift.yml` runs the rest.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from restated_constants import (
    RANGES_SOURCE,
    TRIPWIRES,
    Constant,
    Failure,
    Finding,
    failures_in,
    imports_name,
    is_zero_floor,
    numeric_constants,
    parse_perturbation,
    perturbed_tree,
    report,
    restating,
    starts_a_subprocess,
    widened,
)

NAME = "MAXIMUM_ELAPSED_SIMULATION_TIME_S"

#: A test that copies the limit's value as text. It fails when the limit
#: moves, and the module it imports does import the name.
COPIES_THE_VALUE = """\
from anesthesia_sim.app.formatting import format_supported_run_length


def test_the_run_stops_at_one_day() -> None:
    assert format_supported_run_length() == "24 hours"
"""

#: A test that imports the limit's name. It also fails when the limit moves,
#: because it pins the value on purpose.
IMPORTS_THE_NAME = f"""\
from anesthesia_sim.core.supported_ranges import {NAME}


def test_the_limit_is_one_day() -> None:
    assert {NAME} == 86_400.0
"""


def test_a_test_restating_a_constant_is_named_and_one_importing_it_is_not(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_copies.py").write_text(COPIES_THE_VALUE, encoding="utf-8")
    (tmp_path / "tests" / "test_imports.py").write_text(IMPORTS_THE_NAME, encoding="utf-8")
    both_failed = [
        Failure("tests/test_copies.py::test_the_run_stops_at_one_day", "tests/test_copies.py"),
        Failure("tests/test_imports.py::test_the_limit_is_one_day", "tests/test_imports.py"),
    ]

    named = restating(both_failed, NAME, lambda file: (tmp_path / file).read_text("utf-8"))

    assert [failure.nodeid for failure in named] == [
        "tests/test_copies.py::test_the_run_stops_at_one_day"
    ]


@pytest.mark.parametrize(
    "source",
    [
        f"from anesthesia_sim.core.supported_ranges import {NAME} as LIMIT\n",
        "from anesthesia_sim.core.supported_ranges import *\n",
        f"from anesthesia_sim.core import supported_ranges\nsupported_ranges.{NAME}\n",
        f"from anesthesia_sim.core import supported_ranges as ranges\nranges.{NAME}\n",
        f"import anesthesia_sim.core.supported_ranges\n"
        f"anesthesia_sim.core.supported_ranges.{NAME}\n",
        f"import anesthesia_sim.core.supported_ranges as ranges\nranges.{NAME}\n",
    ],
)
def test_each_way_of_importing_the_name_counts(source: str) -> None:
    assert imports_name(source, NAME)


@pytest.mark.parametrize(
    "source",
    [
        "from anesthesia_sim.core.supported_ranges import MAXIMUM_CARDIAC_OUTPUT_L_MIN\n",
        f'TEXT = "{NAME}"\n',
        f"from anesthesia_sim.core import supported_ranges\nother.{NAME}\n",
        f"from elsewhere import {NAME}\n",
    ],
)
def test_another_name_a_string_or_another_module_does_not_count(source: str) -> None:
    assert not imports_name(source, NAME)


def test_a_junit_report_gives_each_failed_test_its_node_id() -> None:
    xml = """<testsuites><testsuite>
    <testcase classname="tests.unit.test_a" name="test_f" file="tests/unit/test_a.py">
      <failure/></testcase>
    <testcase classname="tests.unit.test_a.TestK" name="test_g[a b - c]"
      file="tests/unit/test_a.py"><failure/></testcase>
    <testcase classname="tests.unit.test_a" name="test_e" file="tests/unit/test_a.py">
      <error/></testcase>
    <testcase classname="" name="tests.unit.test_b" file="tests/unit/test_b.py"><error/></testcase>
    <testcase classname="tests.unit.test_a" name="test_ok" file="tests/unit/test_a.py"/>
    <testcase classname="tests.unit.test_a" name="test_s" file="tests/unit/test_a.py">
      <skipped/></testcase>
    </testsuite></testsuites>"""

    assert [failure.nodeid for failure in failures_in(xml)] == [
        "tests/unit/test_a.py::test_f",
        "tests/unit/test_a.py::TestK::test_g[a b - c]",
        "tests/unit/test_a.py::test_e",
        "tests/unit/test_b.py",
    ]


def test_each_constant_widens_its_interval_by_its_width() -> None:
    constants = [
        Constant("MINIMUM_FLOW", 1.0),
        Constant("MAXIMUM_FLOW", 4.0),
        Constant("MAXIMUM_TIME", 10.0),
        Constant("MINIMUM_ALONE", 1.0),
        Constant("STEP", 2.0),
        Constant("MINIMUM_RATE", 0.0),
        Constant("MAXIMUM_RATE", 5.0),
    ]

    assert [widened(constant, constants) for constant in constants] == [
        0.0,
        7.0,
        20.0,
        None,
        None,
        None,
        10.0,
    ]
    assert [constant.name for constant in constants if is_zero_floor(constant)] == ["MINIMUM_RATE"]


def test_every_constant_on_this_tree_can_be_moved() -> None:
    """A constant no rule can move fails the scheduled job, so it is caught here first."""

    constants = numeric_constants(RANGES_SOURCE.read_text(encoding="utf-8"))

    assert NAME in {constant.name for constant in constants}
    assert all(
        is_zero_floor(constant) or widened(constant, constants) is not None
        for constant in constants
    )


def test_a_file_that_imports_subprocess_is_told_apart() -> None:
    assert starts_a_subprocess("import subprocess\n")
    assert starts_a_subprocess("from subprocess import run\n")
    assert not starts_a_subprocess(IMPORTS_THE_NAME)


def test_the_perturbed_tree_replaces_the_one_binding_and_refuses_anything_else() -> None:
    source = "A = 1.0\nB: float = 2.0\nC = A * 2\n"
    namespace: dict[str, object] = {}

    exec(compile(perturbed_tree(source, "A", 5.0), "<test>", "exec"), namespace)

    assert (namespace["A"], namespace["C"]) == (5.0, 10.0)
    assert isinstance(perturbed_tree(source, "B", 3.0).body[1], ast.AnnAssign)
    for missing in ("C", "D"):
        with pytest.raises(ValueError, match="0 times"):
            perturbed_tree(source, missing, 1.0)


@pytest.mark.parametrize("text", ["NAME", "=1.0", "NAME=", "NAME=x", "NAME=nan", "NAME=inf"])
def test_a_malformed_perturbation_is_refused(text: str) -> None:
    with pytest.raises(ValueError, match="NAME=VALUE"):
        parse_perturbation(text)


def test_a_run_without_an_answer_fails_the_report() -> None:
    answered = Finding(Constant(NAME, 1.0), 2.0, failed=1)
    declined = Finding(Constant(NAME, 1.0), 2.0, declined="pytest exited with status 2")

    assert report([answered], [])[1] is False
    assert report([declined], [])[1] is True
    assert report([answered], [Constant("STEP", 2.0)])[1] is True
    assert report([answered], [], [Constant("MINIMUM_RATE", 0.0)])[1] is False


def test_a_tripwire_is_listed_without_failing_the_report() -> None:
    nodeid = next(iter(TRIPWIRES))
    tripped = Finding(Constant(NAME, 1.0), 2.0, failed=1, tripwires=(nodeid,))
    restated = Finding(Constant(NAME, 1.0), 2.0, failed=1, restating=(nodeid,))

    text, failing = report([tripped], [])
    assert failing is False
    assert f"fails on purpose, because {TRIPWIRES[nodeid]}: {nodeid}" in text
    assert report([restated], [])[1] is True


def test_each_tripwire_names_a_test_that_exists() -> None:
    root = Path(__file__).resolve().parents[2]
    for nodeid in TRIPWIRES:
        file, _, function = nodeid.partition("::")
        tree = ast.parse((root / file).read_text(encoding="utf-8"))
        defined = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
        assert function in defined, nodeid
