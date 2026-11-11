"""`core/rounding.py` states each bound and each fixed allowance, and nothing else in `src/` does.

The expected values here are worked out in the tests themselves, from powers
of two and from the supported ranges, and not read back from the module.
"""

import ast
import math
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.matrix_exponential import MAXIMUM_SQUARINGS
from anesthesia_sim.core.rounding import (
    AGENT_ACCOUNTING_RELATIVE_TOLERANCE,
    FLOW_FRACTION_TOLERANCE,
    HEIGHT_BAND,
    LIVE_READING_GAP,
    MACHINE_EPSILON,
    PROPAGATOR_MARGIN,
    RUNNING_TOTAL_ROUNDING,
    SMALLEST_FULL_PRECISION_MAGNITUDE,
    WHOLE_COUNT_TOLERANCE,
    clock_rounding,
    propagator_rounding,
    run_rounding,
)
from anesthesia_sim.core.simulation_step import MINIMUM_SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import MAXIMUM_ELAPSED_SIMULATION_TIME_S

SOURCE_ROOT = Path(__file__).resolve().parents[2] / "src" / "anesthesia_sim"

STEPS_IN_THE_LONGEST_RUN = round(MAXIMUM_ELAPSED_SIMULATION_TIME_S / MINIMUM_SIMULATION_STEP_S)
"""The most steps a run can take: the longest supported run at the shortest supported step."""


def test_the_arithmetic_constants_are_those_of_a_64_bit_float() -> None:
    """The spacing above 1 is 2**-52, and full precision ends at 2**-1022 divided by that."""

    assert MACHINE_EPSILON == 2.0**-52
    assert SMALLEST_FULL_PRECISION_MAGNITUDE == 2.0**-970
    assert RUNNING_TOTAL_ROUNDING == 2.0**-51


@pytest.mark.parametrize("squarings", [0, 1, 16, 19, MAXIMUM_SQUARINGS])
def test_one_propagator_is_bounded_by_three_times_the_doubled_spacing(squarings: int) -> None:
    """The bound is 3 times 2**squarings times 2**-52, the leading term with its margin of three.

    Every factor is a power of two or three, so the product is exact and the
    comparison needs no tolerance.
    """

    assert PROPAGATOR_MARGIN == 3.0
    assert propagator_rounding(squarings) == 3.0 * 2.0 ** (squarings - 52)


def test_the_bound_at_the_cap_on_squarings_is_under_three_parts_in_a_million() -> None:
    """At 32 squarings the bound is 3 times 2**-20, which is 2.86e-6."""

    assert MAXIMUM_SQUARINGS == 32
    assert propagator_rounding(MAXIMUM_SQUARINGS) == 3.0 * 2.0**-20
    assert propagator_rounding(MAXIMUM_SQUARINGS) < 3e-6


@pytest.mark.parametrize("squarings", [-1, MAXIMUM_SQUARINGS + 1, 51])
def test_no_bound_is_stated_outside_the_squarings_a_propagator_can_have(squarings: int) -> None:
    """A negative count is not a count, and a propagator above the cap is never built."""

    with pytest.raises(SimulationConfigurationError, match="squarings"):
        propagator_rounding(squarings)

    with pytest.raises(SimulationConfigurationError, match="squarings"):
        run_rounding(squarings, 1)


@pytest.mark.parametrize("not_a_count", [True, 1.0, "1", None])
def test_a_count_that_is_not_an_int_is_refused(not_a_count: object) -> None:
    """A `bool` or a `float` is refused, so `True` and `2.5` cannot stand in for a count."""

    with pytest.raises(TypeError, match="squarings must be an int"):
        propagator_rounding(not_a_count)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="steps must be an int"):
        run_rounding(0, not_a_count)  # type: ignore[arg-type]


def test_a_negative_number_of_steps_is_refused() -> None:
    with pytest.raises(SimulationConfigurationError, match="steps must be at least zero"):
        run_rounding(0, -1)


@given(st.integers(0, MAXIMUM_SQUARINGS), st.integers(0, STEPS_IN_THE_LONGEST_RUN))
def test_a_run_is_bounded_by_the_sum_of_its_steps_bounds(squarings: int, steps: int) -> None:
    """The bound for n steps is n times the bound for one, and no steps carry no rounding.

    The count is below 2**53 and the other factors are powers of two and
    three, so the product is rounded once. The expected value is formed in a
    different order, so the comparison allows that one rounding.
    """

    expected = 3.0 * steps * 2.0 ** (squarings - 52)

    assert run_rounding(squarings, steps) == pytest.approx(expected, rel=2.0**-52, abs=0.0)
    assert run_rounding(squarings, 0) == 0.0


def test_clock_rounding_is_one_unit_in_the_last_place_of_the_instant_over_the_interval() -> None:
    """Near 238.2 s the floats are 2**-45 s apart, so over a 0.5 s interval the share is 2**-44."""

    assert clock_rounding(238.2, 0.5) == 2.0**-44
    assert clock_rounding(0.0, 1.0) == 5e-324


@pytest.mark.parametrize(
    ("instant_s", "interval_s"),
    [(1.0, 0.0), (1.0, -1.0), (1.0, math.inf), (1.0, math.nan), (-1.0, 1.0), (math.inf, 1.0)],
)
def test_clock_rounding_refuses_an_instant_or_an_interval_it_cannot_bound(
    instant_s: float, interval_s: float
) -> None:
    with pytest.raises(SimulationConfigurationError, match="must be finite"):
        clock_rounding(instant_s, interval_s)


def test_the_agent_balance_limit_is_below_the_summed_bound_of_the_longest_run() -> None:
    """The fixed limit of one part in 10**9 is about a 58th of the summed bound for 8.64e7 steps.

    The limit is written here as a literal, so that a change to it fails this
    test. `docs/MODEL.md` § "Mass-balance identity" publishes it. The ratio is
    3 times 8.64e7 times 2**-52 over 1e-9, which is 57.6. A longer run limit or
    a shorter step floor moves it, and the statement in `core/rounding.py` that
    the balance does not use the summed bound must then be read again.
    """

    assert AGENT_ACCOUNTING_RELATIVE_TOLERANCE == 1e-9
    assert STEPS_IN_THE_LONGEST_RUN == 86_400_000

    ratio = run_rounding(0, STEPS_IN_THE_LONGEST_RUN) / 1e-9

    assert 57.0 < ratio < 58.0


def test_the_reading_allowance_is_ten_times_the_summed_bound_of_the_longest_run() -> None:
    """A stepped reading's allowance stays at least ten times the bound for the longest run.

    The bound is for steps that need no squaring, which is every shipped
    agent's step (`tests/unit/test_numerical_envelope_sweep.py` fails when one
    needs a squaring). A longer run limit or a shorter step floor that brings
    the bound within a factor of ten fails this test, and a person then
    chooses a new allowance. The band around a MAC target must be wider than
    the allowance, or the zones around its two edges would meet.
    """

    assert run_rounding(0, STEPS_IN_THE_LONGEST_RUN) * 10.0 <= LIVE_READING_GAP
    assert LIVE_READING_GAP * 10.0 <= HEIGHT_BAND * (1.0 + MACHINE_EPSILON)


def test_the_perfusion_allowance_admits_rounding_and_refuses_a_transcription_error() -> None:
    """The stored fractions pass, and the fractions De Wolf et al. print do not.

    0.76, 0.18 and 0.06 are the stored fractions, and 0.758, 0.18 and 0.06 are
    the printed ones, which sum to 0.998 (both from the `sources` note in
    `data/patients/reference_adult.json`). The first sum is within a few
    roundings of 1, and the second is 0.002 away.
    """

    assert abs((0.76 + 0.18 + 0.06) - 1.0) <= 4.0 * MACHINE_EPSILON
    assert 4.0 * MACHINE_EPSILON < FLOW_FRACTION_TOLERANCE
    assert abs((0.758 + 0.18 + 0.06) - 1.0) > FLOW_FRACTION_TOLERANCE


def test_the_whole_count_allowance_separates_rounding_from_a_fractional_count() -> None:
    """0.7 over 0.1 is just below 7 and counts as 7, and two and a half steps do not count as 3.

    The quotient 0.7 / 0.1 is 6.999999999999999 in 64-bit floats, one unit in
    the last place below 7.
    """

    quotient = 0.7 / 0.1

    assert quotient == math.nextafter(7.0, 0.0)
    assert math.floor(quotient + WHOLE_COUNT_TOLERANCE) == 7
    assert math.isclose(quotient, 7, rel_tol=WHOLE_COUNT_TOLERANCE)
    assert not math.isclose(2.5, 3, rel_tol=WHOLE_COUNT_TOLERANCE)
    assert math.floor(2.5 + WHOLE_COUNT_TOLERANCE) == 2


@given(st.lists(st.floats(0.0, 1e3), min_size=1, max_size=2_000))
def test_a_compensated_total_stays_inside_the_running_total_allowance(terms: list[float]) -> None:
    """Kahan's sum of nonnegative terms lies within the allowance of the exactly rounded sum.

    The sum is formed here by the textbook algorithm, and `math.fsum` gives
    the exactly rounded sum to compare it with.
    """

    total = 0.0
    compensation = 0.0

    for term in terms:
        corrected = term - compensation
        summed = total + corrected
        compensation = (summed - total) - corrected
        total = summed

    exact = math.fsum(terms)

    assert abs(total - exact) <= RUNNING_TOTAL_ROUNDING * exact


def test_a_plain_running_total_leaves_the_allowance() -> None:
    """Ten thousand additions of 0.1 by plain `+` leave the allowance by a factor of over 100.

    The allowance therefore tells plain addition from compensated addition.
    """

    total = 0.0

    for _ in range(10_000):
        total += 0.1

    exact = math.fsum([0.1] * 10_000)

    assert abs(total - exact) > 100.0 * RUNNING_TOTAL_ROUNDING * exact


_ALLOWANCE_WORDS = ("TOLERANCE", "ALLOWANCE", "ROUNDING", "EPSILON")
"""A module-level name holding one of these words is treated as a rounding allowance."""


def _module_level_names(path: Path) -> list[str]:
    """Return every name that the module at `path` assigns at its top level."""

    names = []

    for statement in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(statement, ast.Assign):
            targets = statement.targets
        elif isinstance(statement, ast.AnnAssign):
            targets = [statement.target]
        else:
            continue

        names.extend(target.id for target in targets if isinstance(target, ast.Name))

    return names


def test_no_other_module_in_core_or_app_defines_a_rounding_allowance() -> None:
    """Each allowance has one definition, in `core/rounding.py`.

    The test reads every module under `core/` and `app/` for a module-level
    name that says it is a tolerance, an allowance or a rounding figure, or
    that `core/rounding.py` already defines. It finds an allowance by its
    name, so one given another kind of name passes it.
    `MINIMUM_RELATIVE_SCALE_L` guards a division by zero and allows for no
    rounding, so it stays in `core/agent_simulation_validation.py`.
    """

    stated = set(_module_level_names(SOURCE_ROOT / "core" / "rounding.py"))
    elsewhere = []

    assert "AGENT_ACCOUNTING_RELATIVE_TOLERANCE" in stated
    assert "WHOLE_COUNT_TOLERANCE" in stated
    assert "HEIGHT_BAND" in stated

    for package in ("core", "app"):
        for path in sorted((SOURCE_ROOT / package).glob("*.py")):
            if path.name == "rounding.py":
                continue

            for name in _module_level_names(path):
                if name in stated or any(word in name for word in _ALLOWANCE_WORDS):
                    elsewhere.append(f"{package}/{path.name}: {name}")

    assert elsewhere == []
