"""`tools/assertion_probe.py` must name an assertion that never decides a result, and no other.

Three of its rules decide what a reviewer is told. The rewrite must keep each
assertion on its own line and still let the test carry on past a failure, or
the kill matrix is built from the wrong runs. The verdict must name an
assertion only when every mutant it catches also fails another assertion, or a
limit that does decide is reported as dead. And a run that raised outside an
assertion must be left out, because the assertions after the raise never ran.

None of these tests runs mutmut, which is installed only with the `mutation`
dependency group. The end-to-end test stands in a module that reads the active
mutant from the environment for mutmut's trampolines, as they do in mutmut
3.8.0's `mutmut/mutation/trampoline.py`.
"""

from __future__ import annotations

import builtins
import json
from pathlib import Path

import assertion_probe
import pytest
from assertion_probe import (
    MUTANT_ENV,
    MUTANTS_ENV,
    OUT_ENV,
    PROBE,
    PROBE_CALL,
    PROBE_RAISES,
    PROBES,
    RUN_COMPLETED,
    RUN_RAISED,
    RUN_TIMED_OUT,
    NeverDecides,
    install,
    mutants_by_function,
    read_records,
    report,
    rewrite,
    rewrite_tree,
    verdicts,
)

pytest_plugins = ["pytester"]

#: A test file with each kind of assertion the rewrite takes.
SOURCE = """\
import numpy as np
import pytest


def test_kinds(value):
    # A comment with a non-ASCII character, which moves the byte columns: µg.
    label = "µg"; assert value == 1, f"{value} {label}"
    assert (
        value
        < 2
    )
    np.testing.assert_allclose(value, 1.0)
    with pytest.raises(ValueError, match="no"):
        raise ValueError("no")


class TestKinds:
    assert_in_class_body = print("class body")

    def test_method(self):
        self.assertEqual(1, 1)
"""


def test_the_rewrite_keeps_every_line_and_names_each_assertion_by_it() -> None:
    rewritten = rewrite("tests/unit/test_x.py", SOURCE)

    assert len(rewritten.source.splitlines()) == len(SOURCE.splitlines())
    assert rewritten.assertions == (
        "tests/unit/test_x.py:7:19",
        "tests/unit/test_x.py:8:4",
        "tests/unit/test_x.py:12:4",
        "tests/unit/test_x.py:13:9",
        "tests/unit/test_x.py:21:8",
    )
    lines = rewritten.source.splitlines()
    assert lines[6] == (
        "    label = \"µg\"; assert __probe__('tests/unit/test_x.py:7:19', "
        '(value == 1)), f"{value} {label}"'
    )
    assert lines[7:10] == [
        "    assert (",
        "        __probe__('tests/unit/test_x.py:8:4', (value",
        "        < 2))",
    ]
    assert lines[10] == "    )"
    assert lines[11] == (
        "    __probe_call__('tests/unit/test_x.py:12:4', "
        "lambda: np.testing.assert_allclose(value, 1.0))"
    )
    assert lines[12] == (
        "    with __probe_raises__('tests/unit/test_x.py:13:9', "
        'pytest.raises(ValueError, match="no")):'
    )
    # A call in a class body cannot be moved into a lambda, which would not
    # see the class's names, so it stays as it was.
    assert lines[17] == '    assert_in_class_body = print("class body")'
    compile(rewritten.source, "test_x.py", "exec")


def test_the_rewrite_leaves_an_awaited_assertion_call_alone() -> None:
    source = "async def test_a(client):\n    await client.assert_ready()\n    assert True\n"

    rewritten = rewrite("t.py", source)

    assert rewritten.assertions == ("t.py:3:4",)
    assert rewritten.source.splitlines()[1] == "    await client.assert_ready()"


def test_a_file_whose_rewrite_would_not_compile_is_named_and_left_alone(tmp_path: Path) -> None:
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_good.py").write_text("def test_a():\n    assert 1\n", encoding="utf-8")
    (tests / "test_bad.py").write_text("def test_a(:\n", encoding="utf-8")

    refused = rewrite_tree(tests, tmp_path)

    assert refused == ["tests/test_bad.py"]
    assert "__probe__('tests/test_good.py:2:4'" in (tests / "test_good.py").read_text("utf-8")
    assert (tests / "test_bad.py").read_text("utf-8") == "def test_a(:\n"


@pytest.fixture
def probes(monkeypatch: pytest.MonkeyPatch) -> None:
    """The probe names in `builtins` and an empty record, both undone after the test."""
    for name in (PROBE, PROBE_CALL, PROBE_RAISES):
        monkeypatch.setattr(builtins, name, None, raising=False)
    monkeypatch.setenv(MUTANT_ENV, "")
    install()
    PROBES.reset()


def test_a_failed_assertion_is_recorded_and_the_test_carries_on(probes: None) -> None:
    rewritten = rewrite(
        "t.py", "def check(v):\n    assert v == 1\n    assert v > 0\n    return 'on'\n"
    )
    scope: dict[str, object] = {}
    exec(compile(rewritten.source, "t.py", "exec"), scope)

    assert scope["check"](2) == "on"  # type: ignore[operator]
    assert PROBES.evaluated == {"t.py:2:4", "t.py:3:4"}
    assert PROBES.failed == {"t.py:2:4"}


#: A function holding one `pytest.raises` block, around the statement `body`.
RAISES_CHECK = """\
import pytest
def check():
    with pytest.raises(ValueError, match="no"):
        {body}
"""


@pytest.mark.parametrize(
    ("body", "failed"),
    [
        ("raise ValueError('no')", False),
        ("pass", True),
        ("raise ValueError('yes')", True),
        ("raise KeyError('no')", True),
    ],
)
def test_a_raises_block_records_each_way_it_fails(probes: None, body: str, failed: bool) -> None:
    source = RAISES_CHECK.format(body=body)
    scope: dict[str, object] = {}
    exec(compile(rewrite("t.py", source).source, "t.py", "exec"), scope)

    scope["check"]()  # type: ignore[operator]

    assert PROBES.failed == ({"t.py:3:9"} if failed else set())


def test_an_assertion_call_that_fails_is_recorded(probes: None) -> None:
    source = "import numpy as np\ndef check():\n    np.testing.assert_allclose(1.0, 2.0)\n"
    scope: dict[str, object] = {}
    exec(compile(rewrite("t.py", source).source, "t.py", "exec"), scope)

    scope["check"]()  # type: ignore[operator]

    assert PROBES.failed == {"t.py:3:4"}


def _lines(*records: dict[str, object]) -> list[str]:
    return [json.dumps(record) for record in records]


def _case(test: str, assertions: list[str], runs: dict[str, tuple[str, list[str]]]) -> list[str]:
    """The records of one test case: its head, each mutant's run, and the check after."""
    return _lines(
        {"test": test, "assertions": assertions, "mutants": len(runs), "clean_s": 0.01},
        *(
            {"test": test, "mutant": mutant, "outcome": outcome, "failed": failed}
            for mutant, (outcome, failed) in runs.items()
        ),
        {"test": test, "reliable": True},
    )


LOOSE, STRICT = "t.py:5:4", "t.py:6:4"


def test_a_looser_limit_that_a_stricter_one_overrules_never_decides() -> None:
    # The PL-VXM0 pattern: the strict limit fails for every mutant the loose
    # one fails for, and for one more.
    lines = _case(
        "t.py::test_step",
        [LOOSE, STRICT],
        {
            "m1": (RUN_COMPLETED, [LOOSE, STRICT]),
            "m2": (RUN_COMPLETED, [LOOSE, STRICT]),
            "m3": (RUN_COMPLETED, [STRICT]),
            "m4": (RUN_COMPLETED, []),
        },
    )

    found = verdicts(read_records(lines))

    assert found.never == [NeverDecides("t.py::test_step", LOOSE, 2, ((STRICT, 2),), (STRICT,), ())]
    assert found.decides == 1
    assert found.never[0].sentence() == (
        "t.py:5 in t.py::test_step never decides a result: each of the 2 mutants it catches "
        "also fails t.py:6 (2 of 2). t.py:6 alone catches all of them and more, so this "
        "assertion is the looser of the two."
    )


def test_two_assertions_that_each_catch_a_mutant_alone_both_decide() -> None:
    lines = _case(
        "t.py::test_pair",
        [LOOSE, STRICT],
        {
            "m1": (RUN_COMPLETED, [LOOSE]),
            "m2": (RUN_COMPLETED, [STRICT]),
            "m3": (RUN_COMPLETED, [LOOSE, STRICT]),
        },
    )

    found = verdicts(read_records(lines))

    assert found.never == []
    assert found.decides == 2


def test_two_assertions_that_always_fail_together_are_both_named() -> None:
    lines = _case("t.py::test_same", [LOOSE, STRICT], {"m1": (RUN_COMPLETED, [LOOSE, STRICT])})

    found = verdicts(read_records(lines))

    assert [(never.assertion, never.equal, never.stricter) for never in found.never] == [
        (LOOSE, (STRICT,), ()),
        (STRICT, (LOOSE,), ()),
    ]


def test_a_run_that_raised_or_timed_out_is_left_out_of_the_verdict() -> None:
    # Without the raised run, which failed only the loose limit before it
    # raised, the loose limit would decide.
    lines = _case(
        "t.py::test_raise",
        [LOOSE, STRICT],
        {
            "m1": (RUN_COMPLETED, [LOOSE, STRICT]),
            "m2": (RUN_RAISED, [LOOSE]),
            "m3": (RUN_TIMED_OUT, [LOOSE]),
            "m4": (RUN_COMPLETED, [STRICT]),
        },
    )

    found = verdicts(read_records(lines))

    assert [never.assertion for never in found.never] == [LOOSE]
    assert found.outcomes == {RUN_COMPLETED: 2, RUN_RAISED: 1, RUN_TIMED_OUT: 1}


def test_the_cases_of_a_parametrized_test_count_together() -> None:
    # The loose limit decides in the second case only, so it decides.
    lines = [
        *_case(
            "t.py::test_p[a]",
            [LOOSE, STRICT],
            {"m1": (RUN_COMPLETED, [LOOSE, STRICT]), "m2": (RUN_COMPLETED, [STRICT])},
        ),
        *_case("t.py::test_p[b]", [LOOSE, STRICT], {"m1": (RUN_COMPLETED, [LOOSE])}),
    ]

    found = verdicts(read_records(lines))

    assert found.never == []
    assert found.decides == 2
    assert found.tests == 1


def test_a_case_a_mutant_left_broken_or_that_never_finished_is_left_out() -> None:
    broken = _case("t.py::test_b", [LOOSE, STRICT], {"m1": (RUN_COMPLETED, [LOOSE, STRICT])})
    broken[-1] = json.dumps({"test": "t.py::test_b", "reliable": False})
    unfinished = _case("t.py::test_u", [LOOSE, STRICT], {"m1": (RUN_COMPLETED, [LOOSE, STRICT])})[
        :-1
    ]

    records = read_records([*broken, *unfinished])

    assert records.matrices == {}
    assert records.unreliable == ["t.py::test_b"]
    assert records.unfinished == ["t.py::test_u"]
    text = report(records, verdicts(records))
    assert "  t.py::test_b" in text
    assert "  t.py::test_u" in text


def test_an_assertion_no_mutant_fails_is_counted_and_not_named() -> None:
    lines = _case("t.py::test_n", [LOOSE, STRICT], {"m1": (RUN_COMPLETED, [STRICT])})

    found = verdicts(read_records(lines))

    assert found.never == []
    assert (found.decides, found.fails_for_none) == (1, 1)


def test_mutants_are_grouped_by_the_function_they_mutate() -> None:
    names = ["pkg.mod.x_dose__mutmut_1", "pkg.mod.xǁPǁrun__mutmut_1", "pkg.mod.x_dose__mutmut_2"]

    assert mutants_by_function(names) == {
        "pkg.mod.x_dose": [names[0], names[2]],
        "pkg.mod.xǁPǁrun": [names[1]],
    }


#: A test module whose function under test reads the active mutant from the
#: environment, as mutmut's trampolines do. One mutant fails both limits, one
#: fails only the strict one, and one raises before either is checked.
END_TO_END = """\
import os


def value():
    mutant = os.environ.get("MUTANT_UNDER_TEST", "")
    if mutant == "pkg.mod.x_value__mutmut_1":
        return 2.0
    if mutant == "pkg.mod.x_value__mutmut_2":
        return 1.0 + 1e-9
    if mutant == "pkg.mod.x_value__mutmut_3":
        raise RuntimeError("the mutant raised")
    return 1.0


def test_step():
    found = value()
    assert abs(found - 1.0) < 5e-3
    assert abs(found - 1.0) < 1e-14
"""


def test_the_plugin_builds_the_matrix_and_names_the_looser_limit(
    pytester: pytest.Pytester, probes: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    listed = pytester.path / "mutants.json"
    names = [f"pkg.mod.x_value__mutmut_{number}" for number in (1, 2, 3)]
    listed.write_text(json.dumps(mutants_by_function(names)), encoding="utf-8")
    monkeypatch.setenv(MUTANTS_ENV, str(listed))
    pytester.makepyfile(test_step=rewrite("test_step.py", END_TO_END).source)
    out = pytester.path / "records.jsonl"
    monkeypatch.setenv(OUT_ENV, str(out))
    # mutmut's `stats` run is what names the functions a test reaches.
    monkeypatch.setattr(assertion_probe, "reached", lambda item: ["pkg.mod.x_value"])

    result = pytester.runpytest_inprocess("-p", "assertion_probe", "-p", "no:randomly")

    assert result.ret == 0
    records = read_records(out.read_text(encoding="utf-8").splitlines())
    found = verdicts(records)
    assert [(never.assertion, never.stricter) for never in found.never] == [
        ("test_step.py:17:4", ("test_step.py:18:4",))
    ]
    assert found.decides == 1
    assert found.outcomes == {RUN_COMPLETED: 2, RUN_RAISED: 1}
    raised = [json.loads(line) for line in out.read_text("utf-8").splitlines() if "error" in line]
    assert "the mutant raised" in raised[0]["error"]
