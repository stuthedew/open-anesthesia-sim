"""`core/rounding.py` states each bound and each fixed allowance, and nothing else in `src/` does.

The expected values here are worked out in the tests themselves, from powers
of two and from the supported ranges, and not read back from the module.
"""

import ast
import math
from decimal import ROUND_CEILING, ROUND_FLOOR, Context, Decimal, localcontext
from pathlib import Path

import pytest
from hypothesis import given, settings, target
from hypothesis import strategies as st
from test_generated_runs import _COEFFICIENTS, _POSITIONS, _VOLUMES_L, ONE_STEP, Plan, _build
from test_numerical_envelope import _decimal_exponential, _squarings
from test_numerical_envelope_sweep import CEILING, Corner

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import (
    DELIVERED_AGENT_L,
    STATE_SIZE,
    UNIT_STATE,
    build_system_matrix,
)
from anesthesia_sim.core.matrix_exponential import (
    MAXIMUM_SERIES_ARGUMENT_NORM,
    MAXIMUM_SQUARINGS,
    SERIES_TERMS,
    matrix_exponential,
    propagate,
)
from anesthesia_sim.core.rounding import (
    AGENT_ACCOUNTING_RELATIVE_TOLERANCE,
    FLOW_FRACTION_TOLERANCE,
    MACHINE_EPSILON,
    PROPAGATOR_ROUNDING_UNITS,
    RUNNING_TOTAL_ROUNDING,
    SMALLEST_FULL_PRECISION_MAGNITUDE,
    WHOLE_COUNT_TOLERANCE,
    propagator_rounding,
    run_rounding,
)
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_STEP_COUNT,
    MINIMUM_COMPARTMENT_STEP_S,
    StepCount,
)

SOURCE_ROOT = Path(__file__).resolve().parents[2] / "src" / "anesthesia_sim"

STEPS_IN_THE_LONGEST_RUN = int(MAXIMUM_STEP_COUNT)
"""The most steps a run can take: one for each second of the longest supported run."""

MOST_SQUARINGS_IN_A_SHIPPED_STEP = 3
"""The most squarings that a shipped agent's one-second step needs.

`tests/unit/test_numerical_envelope_sweep.py` counts them at every corner of
the supported flows and fails when a shipped agent needs more.
"""

_INTERVALS_S = st.sampled_from(
    (float(SIMULATION_STEP_S), 0.1, MINIMUM_COMPARTMENT_STEP_S)
) | st.floats(MINIMUM_COMPARTMENT_STEP_S, float(SIMULATION_STEP_S))
"""The interval of one propagator, from a millisecond to the one-second step that a run takes.

A run steps by one second, and `RunDefinition.state_at` forms a propagator
over any interval. The bound is stated for a propagator, so these steps are
drawn across the intervals that the envelope was measured for.
"""


def test_the_arithmetic_constants_are_those_of_a_64_bit_float() -> None:
    """The spacing above 1 is 2**-52, and full precision ends at 2**-1022 divided by that."""

    assert MACHINE_EPSILON == 2.0**-52
    assert SMALLEST_FULL_PRECISION_MAGNITUDE == 2.0**-970
    assert RUNNING_TOTAL_ROUNDING == 2.0**-51


@pytest.mark.parametrize("squarings", [0, 1, 16, 19, MAXIMUM_SQUARINGS])
def test_one_propagator_is_bounded_by_ten_times_the_doubled_spacing(squarings: int) -> None:
    """The bound is 10 times 2**squarings times 2**-52.

    Ten is exact in binary and the other factors are powers of two, so the
    product is exact and the comparison needs no tolerance.
    """

    assert PROPAGATOR_ROUNDING_UNITS == 10.0
    assert propagator_rounding(squarings) == 10.0 * 2.0 ** (squarings - 52)


def test_the_bound_at_the_cap_on_squarings_is_under_one_part_in_100_000() -> None:
    """At 32 squarings the bound is 10 times 2**-20, which is 9.54e-6."""

    assert MAXIMUM_SQUARINGS == 32
    assert propagator_rounding(MAXIMUM_SQUARINGS) == 10.0 * 2.0**-20
    assert propagator_rounding(MAXIMUM_SQUARINGS) < 1e-5


_DOWNWARD = Context(prec=40, rounding=ROUND_FLOOR)
"""Decimal arithmetic that rounds down, for a denominator under an upper bound."""


def _exp_upper_bound(x: Decimal) -> Decimal:
    """Return an upper bound on e**x for 0 <= x < 1: e**x <= 1 / (1 - x), because e**-x >= 1 - x."""

    return 1 / _DOWNWARD.subtract(1, x)


def _derived_step_error_in_leading_terms(squarings: int) -> Decimal:
    """Return the derived bound on one step's error, in units of 2**squarings times 2**-52.

    This is the derivation in the docstring of `PROPAGATOR_ROUNDING_UNITS`,
    computed here from the matrix exponential module's constants and the size
    of the state, and not read from `core/rounding.py`. Every quantity is
    nonnegative, so a relative bound on each number carries through sums and
    products. A product of m rounded results lies within (1 + u)**m - 1 of the
    exact one, where u = 2**-53. Errors are measured in the row sums of the
    fraction rows, with the forcing column divided by the delivered fraction.
    Every operation rounds up, and each denominator rounds down, so the result
    is an upper bound on the derivation's figure.
    """

    with localcontext(Context(prec=40, rounding=ROUND_CEILING)):
        u = Decimal(2) ** -53
        # The scaled argument's rows sum to at most 1/16. The fraction rows may
        # add up to 2**-9 of agent over the step, and the squarings' rounding
        # adds a few parts in 10**15 to the norm. 0.065 is above all three.
        theta = Decimal("0.065")
        assert Decimal(MAXIMUM_SERIES_ARGUMENT_NORM) + Decimal(2) ** -9 < Decimal("0.0646")
        # Agent created at a rate r with r * dt <= 2**-9 lets the exact
        # propagator's rows sum to e**(r * dt) over the step.
        creation = Decimal(2) ** -9

        # One compensated sum of n nonnegative terms lies within
        # u + gamma_(n-1)**2 of the exact sum (Ogita, Rump and Oishi,
        # Proposition 4.5). One entry of a product of nonnegative matrices
        # rounds each product and then the sum.
        gamma = (STATE_SIZE - 1) * u / _DOWNWARD.subtract(1, (STATE_SIZE - 1) * u)
        compensated = u + gamma * gamma
        product = (1 + u) * (1 + compensated) - 1

        # The series. For each order, term k has four roundings of at most u
        # (the shift, the scaling by the interval, the product and the
        # division by k) and one compensated sum. It then passes through
        # SERIES_TERMS - k + 1 plain additions. The identity term passes
        # through every addition.
        series = (1 + u) ** SERIES_TERMS - 1

        for order in range(1, SERIES_TERMS + 1):
            rounding = (1 + u) ** (3 * order + SERIES_TERMS + 1) * (1 + compensated) ** order - 1
            series += rounding * theta**order / math.factorial(order)

        truncation = (
            theta ** (SERIES_TERMS + 1)
            / math.factorial(SERIES_TERMS + 1)
            / _DOWNWARD.subtract(1, _DOWNWARD.divide(theta, SERIES_TERMS + 2))
        )

        # The decay factor: the argument rounds once, `exp` is within one unit
        # in the last place (2u), and the product with the series rounds once.
        decay = _exp_upper_bound(theta * u) * (1 + 2 * u) * (1 + u) - 1
        error = decay * (_exp_upper_bound(creation) + series) + series + truncation

        # Squaring k multiplies two copies of the propagator over 2**k scaled
        # intervals, whose rows sum to at most e**(r * dt * 2**(k - s)).
        for squaring in range(squarings):
            growth = _exp_upper_bound(creation / 2 ** (squarings - squaring))
            error = error * (2 * growth + error) + product * (growth + error) ** 2

        # Applying the propagator to the state is one more product.
        error += product * (_exp_upper_bound(creation) + error)

        leading_term: Decimal = 2**squarings * Decimal(2) ** -52
        bound: Decimal = error / leading_term

        return bound


def test_the_bound_is_the_derivation_rounded_up_to_a_whole_number() -> None:
    """The derivation gives at most 9.13 leading terms at any number of squarings, rounded up to 10.

    A change to the series, its scaling or the size of the state changes the
    derivation, and this test then fails until the constant is derived again.
    """

    derived = [_derived_step_error_in_leading_terms(s) for s in range(MAXIMUM_SQUARINGS + 1)]

    assert Decimal("9.11") < derived[0] < Decimal("9.12")
    assert max(derived) < Decimal("9.13")
    assert math.ceil(max(derived)) == PROPAGATOR_ROUNDING_UNITS


WORST_STEPS_FOUND = (
    # Found by the blind review of the rounding module: 5 squarings, 3.35.
    (
        Corner(
            circuit_l=918.8696053890402,
            alveolar_l=1662.2739873313274,
            venous_l=0.013309137204588203,
            tissue_l=0.05379281056928648,
            blood_gas=775.1252855300395,
            tissue_blood=1.453520370492207,
        ),
        (0.4428973210177197, 0.42985577848716605, 1.0),
        0.1,
    ),
    # 4 squarings, 3.33.
    (
        Corner(
            circuit_l=0.01,
            alveolar_l=0.145075755865501,
            venous_l=5.7161830603660375,
            tissue_l=10000.0,
            blood_gas=0.397271461156513,
            tissue_blood=0.5074610095330717,
        ),
        (0.33396054011682375, 0.17749199346523858, 0.7383306882317353),
        0.1,
    ),
    # 7 squarings, 3.47, the largest found.
    (
        Corner(
            circuit_l=10000.0,
            alveolar_l=0.03119749772434302,
            venous_l=96.08952938553124,
            tissue_l=0.01,
            blood_gas=0.07344877286040184,
            tissue_blood=0.015801676017017346,
        ),
        (1.0, 1.0, 1.0),
        0.006962811064408954,
    ),
    # 9 squarings, 3.24.
    (
        Corner(
            circuit_l=272.1103431518297,
            alveolar_l=0.01,
            venous_l=54.72899174820302,
            tissue_l=0.01,
            blood_gas=305.7960665790651,
            tissue_blood=4.740562115912101,
        ),
        (0.0651042623088064, 0.02944111131744198, 0.0610483163381339),
        0.08528640004880768,
    ),
)
"""The steps with the largest propagator error among 240 000 drawn across the numerical envelope.

Each entry gives the volumes and coefficients, the three flows as shares of
their supported ranges, and the propagator's interval in seconds. The comment
on each gives the squarings that the propagator needs and its error on
2026-11-11, in leading terms. The intervals are those of the search, which
drew them from 1 ms to 0.1 s.
"""


def _propagator_error_in_leading_terms(
    corner: Corner, flows: tuple[float, float, float], step_s: float
) -> float:
    """Return the largest error in one fraction's row of the propagator, in leading terms.

    The propagator is compared with a 50-digit evaluation of the same
    exponential. A row's error is the sum of its entries' errors, which bounds
    how far the row can move a fraction, as a share of the largest value in
    the state. One leading term is 2**squarings times 2**-52. The squarings
    are counted by `test_numerical_envelope._squarings`, independently of the
    module under test.
    """

    system = _build(Plan(None, corner, 0.5, flows, 0.5, ONE_STEP))
    matrix = build_system_matrix(system.equation_settings())
    computed = matrix_exponential(matrix, step_s)
    exact = _decimal_exponential(matrix, str(Decimal(step_s)))
    leading_term = 2.0 ** (_squarings(matrix, step_s) - 52)

    return (
        max(
            float(
                sum(
                    abs(Decimal(value) - reference)
                    for value, reference in zip(row, exact_row, strict=True)
                )
            )
            for row, exact_row in zip(
                computed[:DELIVERED_AGENT_L], exact[:DELIVERED_AGENT_L], strict=True
            )
        )
        / leading_term
    )


def test_the_worst_steps_found_pass_three_leading_terms_and_stay_inside_the_derived_bound() -> None:
    """The derived bound of 10 holds at the worst steps found, which reach about a third of it.

    The 10 and the 3 are literals here. The largest error must pass 3 leading
    terms. That shows these steps still measure what they were listed for, and
    that the derived bound is within a factor of about three of an error that
    correct arithmetic makes. The comparison with 3 is made on the largest of
    the four and not on each, because another computer's `exp` may round one
    entry differently.
    """

    errors = [_propagator_error_in_leading_terms(*step) for step in WORST_STEPS_FOUND]

    assert all(error <= 10.0 for error in errors), errors
    assert max(errors) > 3.0, errors


@st.composite
def _one_step_from_a_drawn_state(
    draw: st.DrawFn,
) -> tuple[Corner, tuple[float, float, float], float, float, tuple[float, ...]]:
    """Draw a system inside the numerical envelope, an interval and a state of its fractions.

    The volumes, coefficients, flows and dial are drawn as the generated runs
    draw them, and the interval from `_INTERVALS_S`. Each fraction is drawn on
    its own, from 0 to the input ceiling, so the state need not be one that a
    run reaches.
    """

    corner = Corner(
        draw(_VOLUMES_L), draw(_VOLUMES_L), draw(_VOLUMES_L), draw(_VOLUMES_L), *draw(_COEFFICIENTS)
    )
    flows = (draw(_POSITIONS), draw(_POSITIONS), draw(_POSITIONS))
    fractions = tuple(draw(_POSITIONS) * CEILING for _ in range(DELIVERED_AGENT_L))

    return corner, flows, draw(_POSITIONS), draw(_INTERVALS_S), fractions


@settings(max_examples=200)
@given(_one_step_from_a_drawn_state())
def test_a_step_drawn_across_the_envelope_stays_inside_the_derived_bound(
    drawn: tuple[Corner, tuple[float, float, float], float, float, tuple[float, ...]],
) -> None:
    """One step's error in every fraction stays within 10 leading terms of the scale.

    The expected state is a 50-digit evaluation of the same exponential,
    applied to the same state. The scale is the larger of the largest fraction
    in the state and the delivered fraction, which is what the bound is stated
    against. One leading term is 2**squarings times 2**-52, with the squarings
    counted by `test_numerical_envelope._squarings`. On 2026-11-14 the largest
    error among 240 000 such steps, each from four drawn states, was 3.5
    leading terms.
    """

    corner, flows, dial, step_s, fractions = drawn
    system = _build(Plan(None, corner, 0.5, flows, dial, ONE_STEP))
    settings_now = system.equation_settings()
    matrix = build_system_matrix(settings_now)
    state = (*fractions, 0.0, 0.0, 1.0)
    assert len(state) == STATE_SIZE and state[UNIT_STATE] == 1.0
    scale = max(*fractions, settings_now.delivered_partial_pressure_fraction)

    stepped = propagate(matrix_exponential(matrix, step_s), state)
    exact = _decimal_exponential(matrix, str(Decimal(step_s)))
    leading_term = 2.0 ** (_squarings(matrix, step_s) - 52)

    if scale == 0.0:
        assert stepped[:DELIVERED_AGENT_L] == (0.0,) * DELIVERED_AGENT_L
        return

    error = max(
        abs(
            Decimal(stepped[row])
            - sum(exact[row][column] * Decimal(state[column]) for column in range(STATE_SIZE))
        )
        for row in range(DELIVERED_AGENT_L)
    )
    in_leading_terms = float(error) / scale / leading_term

    target(in_leading_terms, label="one step's error, in leading terms")
    assert in_leading_terms <= PROPAGATOR_ROUNDING_UNITS


@pytest.mark.parametrize("squarings", [-1, MAXIMUM_SQUARINGS + 1, 51])
def test_no_bound_is_stated_outside_the_squarings_a_propagator_can_have(squarings: int) -> None:
    """A negative count is not a count, and a propagator above the cap is never built."""

    with pytest.raises(SimulationConfigurationError, match="squarings"):
        propagator_rounding(squarings)

    with pytest.raises(SimulationConfigurationError, match="squarings"):
        run_rounding(squarings, StepCount(1))


@pytest.mark.parametrize("not_a_count", [True, 1.0, "1", None])
def test_a_count_that_is_not_an_int_is_refused(not_a_count: object) -> None:
    """A `bool` or a `float` is refused, so `True` and `2.5` cannot stand in for a count."""

    with pytest.raises(TypeError, match="squarings must be an int"):
        propagator_rounding(not_a_count)  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        run_rounding(0, not_a_count)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("squarings", "message"),
    [
        (-1, "squarings must be at least zero, and -1 is not"),
        (
            33,
            "squarings must be at most 32, and 33 is not; core/matrix_exponential.py refuses "
            "a propagator that needs more, so its rounding has no stated bound",
        ),
    ],
)
def test_a_refused_number_of_squarings_is_named_with_its_limit(
    squarings: int, message: str
) -> None:
    """The refusal gives the condition, the value that failed it and where the cap is set."""

    with pytest.raises(SimulationConfigurationError) as refusal:
        propagator_rounding(squarings)

    assert str(refusal.value) == message


def test_a_count_of_the_wrong_type_is_named_by_its_type() -> None:
    with pytest.raises(TypeError) as refusal:
        propagator_rounding(2.5)  # type: ignore[arg-type]

    assert str(refusal.value) == "squarings must be an int, not a float"


def test_a_number_of_steps_not_built_as_a_step_count_is_refused() -> None:
    """A bare `int` carries no proof that it is whole and nonnegative, so it is refused."""

    with pytest.raises(TypeError, match="StepCount"):
        run_rounding(0, 5)  # type: ignore[arg-type]


@given(st.integers(0, MAXIMUM_SQUARINGS), st.integers(0, STEPS_IN_THE_LONGEST_RUN))
def test_a_run_is_bounded_by_the_sum_of_its_steps_bounds(squarings: int, steps: int) -> None:
    """The bound for n steps is n times the bound for one, and no steps carry no rounding.

    Ten times the count is below 2**53 and the other factors are powers of
    two, so the product is exact in either order and the comparison needs no
    tolerance.
    """

    expected = steps * 10.0 * 2.0 ** (squarings - 52)

    bound = run_rounding(squarings, StepCount(steps))

    assert bound == expected
    assert run_rounding(squarings, StepCount(0)) == 0.0


def test_the_agent_balance_limit_is_two_thirds_of_the_summed_bound_of_the_longest_run() -> None:
    """The fixed limit of one part in 10**9 is below the summed bound for 86 400 shipped steps.

    The limit is written here as a literal, so that a change to it fails this
    test. `docs/MODEL.md` § "Mass-balance identity" publishes it. A shipped
    agent's step needs at most three squarings, so the bound for the longest
    run is 10 times 2**3 times 86 400 times 2**-52, which is 1.53e-9 and 1.53
    times the limit. A longer run limit or a fourth squaring moves the ratio,
    and the statement in `core/rounding.py` that the balance does not use the
    summed bound must then be read again.
    """

    assert AGENT_ACCOUNTING_RELATIVE_TOLERANCE == 1e-9
    assert STEPS_IN_THE_LONGEST_RUN == 86_400

    bound = run_rounding(MOST_SQUARINGS_IN_A_SHIPPED_STEP, StepCount(STEPS_IN_THE_LONGEST_RUN))

    assert 1.53 < bound / 1e-9 < 1.54


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
