"""Verify the propagator against solutions written out by hand.

Every expected value below is an analytic solution of the same system, not a
second run of the code under test. The solutions are a scalar decay, the
closed form of two well-mixed volumes exchanging with each other, the exact
integral of a constant rate, and the semigroup identity that the exponential
of a constant matrix must satisfy. One test applies that identity to the
shipped uptake system. It checks that the propagator the system caches
belongs to the step the system is asked to take.

The tests also check what the module promises beyond accuracy, on the class
of matrix for which the promise is made. The promise is an entrywise
nonnegative propagator. With it, an exact step cannot carry a compartment
below zero through a rounding artifact, which would then be reported as a
numerical failure of the model.
"""

from math import exp, expm1, isclose

import pytest

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.matrix_exponential import (
    MAXIMUM_SERIES_ARGUMENT_NORM,
    MAXIMUM_SQUARINGS,
    Matrix,
    matrix_exponential,
    multiply,
    propagate,
)
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

WORST_RELATIVE_ERROR_MEASURED = {
    0.1: 2.3e-16,
    1.0: 1.8e-15,
    37.5: 3.4e-15,
    60.0: 2.5e-14,
    600.0: 4.5e-14,
    3600.0: 2.0e-12,
}
"""The worst relative difference from the analytic result, for each interval.

The figures were measured on 2026-09-06 across every comparison in this
file. They grow with the interval because the number of squarings grows
with it. There are none at 0.1 s and sixteen at 3600 s, and each squaring can
at most double the relative error. One flat tolerance would therefore either pass a real
regression at 0.1 s or fail correct arithmetic at 3600 s. The module's
truncation error is ten orders of magnitude below all of these figures (see
its docstring). So what is bounded here is the roundoff from squaring and
nothing else.
"""

TOLERANCE_MARGIN = 20.0
"""The factor by which the tests' tolerance exceeds the measured error.

The margin is wide enough that a different machine's rounding does not fail
the suite, and narrow enough that losing an order of magnitude of accuracy
does.
"""


def _relative_tolerance(interval_s: float) -> float:
    return WORST_RELATIVE_ERROR_MEASURED[interval_s] * TOLERANCE_MARGIN


def _identity(size: int) -> Matrix:
    return tuple(tuple(float(row == column) for column in range(size)) for row in range(size))


def _two_compartment_exchange(rate_left: float, rate_right: float) -> Matrix:
    """Return the matrix of two well-mixed volumes exchanging with each other.

    The equations are `d x0/dt = rate_left (x1 - x0)` and
    `d x1/dt = rate_right (x0 - x1)`. They are the circuit and alveolar pair
    of `docs/MODEL.md`, with ventilation as the only transfer between them.
    A test below writes out their closed form.
    """

    return ((-rate_left, rate_left), (rate_right, -rate_right))


def test_zero_matrix_propagates_nothing() -> None:
    assert matrix_exponential(((0.0, 0.0), (0.0, 0.0)), 12.5) == _identity(2)


@pytest.mark.parametrize("interval_s", [0.1, 1.0, 60.0, 3600.0])
def test_diagonal_matrix_matches_scalar_decay(interval_s: float) -> None:
    """A diagonal matrix decouples, so each entry is a scalar exponential."""

    rates = (-0.5, -0.0125, 0.0)
    matrix = tuple(
        tuple(rate if row == column else 0.0 for column in range(3))
        for row, rate in enumerate(rates)
    )

    propagator = matrix_exponential(matrix, interval_s)

    for row, rate in enumerate(rates):
        for column in range(3):
            expected = exp(rate * interval_s) if row == column else 0.0
            assert propagator[row][column] == pytest.approx(
                expected, rel=_relative_tolerance(interval_s), abs=1e-300
            )


@pytest.mark.parametrize("interval_s", [0.1, 37.5, 600.0])
def test_two_compartment_exchange_matches_its_closed_form(interval_s: float) -> None:
    """Compare against the analytic solution of the same pair.

    Two volumes exchanging with each other relax towards a common equilibrium
    with the single rate constant `rate_left + rate_right`. The equilibrium is
    the flow-weighted mean of their starting values. The test writes that
    closed form out here, and the module under test never sees it.
    """

    rate_left, rate_right = 0.0111, 0.0267
    total_rate = rate_left + rate_right
    start = (0.05, 0.0)

    equilibrium = (rate_right * start[0] + rate_left * start[1]) / total_rate
    remaining = exp(-total_rate * interval_s)
    expected = (
        equilibrium + (start[0] - equilibrium) * remaining,
        equilibrium + (start[1] - equilibrium) * remaining,
    )

    advanced = propagate(
        matrix_exponential(_two_compartment_exchange(rate_left, rate_right), interval_s), start
    )

    assert advanced == pytest.approx(expected, rel=_relative_tolerance(interval_s))


def test_a_constant_forcing_row_integrates_exactly() -> None:
    """An augmented constant state turns an affine system into a linear one.

    `d x/dt = k`, with the constant carried as a state of its own, is the form
    that every accumulator row of the uptake system uses. Its exact solution
    over the interval is `k * interval_s`, with no approximation anywhere in it.
    """

    rate = 0.00333
    interval_s = 90.0
    propagator = matrix_exponential(((0.0, rate), (0.0, 0.0)), interval_s)

    advanced = propagate(propagator, (0.0, 1.0))

    assert advanced[0] == pytest.approx(rate * interval_s, rel=1e-14)


FORCED_DECAY_LEVEL = 0.04
"""The level at which `_forced_decay` settles: the forcing column's exact long-run entry."""


def _forced_decay(rate_per_s: float) -> Matrix:
    """Return the matrix of `d x/dt = rate (level - x)`, with the level carried by a constant state.

    Every forcing term in the uptake system has this form: a state driven
    toward a level that the constant state supplies, as the circuit is driven
    toward the dialled fraction. Starting from `x = 0`, its closed form over an
    interval `t` is `x(t) = level (1 - exp(-rate t))`. That is the forcing
    column's entry, and the constant's row is the identity's row.
    """

    return ((-rate_per_s, rate_per_s * FORCED_DECAY_LEVEL), (0.0, 0.0))


@pytest.mark.parametrize(
    ("matrix", "interval_s"),
    [
        (((-0.5, 0.5, 0.0), (0.0125, -0.0125, 0.0), (0.0, 0.0, 0.0)), 0.1),
        (((-0.5, 0.5, 0.0), (0.0125, -0.0125, 0.0), (0.0, 0.0, 0.0)), 60.0),
        (((-0.5, 0.5, 0.0), (0.0125, -0.0125, 0.0), (0.0, 0.0, 0.0)), 3600.0),
        (_forced_decay(1e4), 60.0),
        (_forced_decay(1e7), 1.0),
        (_forced_decay(2e8), 0.1),
        (_forced_decay(2.0**28), 1.0),
    ],
)
def test_a_zero_row_propagates_to_its_exact_basis_row(matrix: Matrix, interval_s: float) -> None:
    """`PL-2MD9`: a state that nothing moves stays exactly unchanged over any interval.

    A zero row of `A` is a zero row of every power of `A`, so the same row of
    `exp(A * t)` is exactly the identity's row. The shift used to recover
    that row as a product of two rounded factors, `1 + delta`, and the
    squarings raised the product to `(1 + delta) ** 2**s`. The last four cases
    take 24, 28, 29 and 32 squarings, the most the module performs. The first
    three of those are where the drift was measured before the fix:
    0.9999999981 at 24, 0.99999997 at 28 and 0.99999994 at 29. Yet
    `governing_equations.UNIT_STATE`'s guarantee is that no step can perturb
    the constant state.
    """

    constant_row = len(matrix) - 1
    basis_row = tuple(float(column == constant_row) for column in range(len(matrix)))

    assert matrix_exponential(matrix, interval_s)[constant_row] == basis_row


@pytest.mark.parametrize(("rate_per_s", "interval_s"), [(1e4, 60.0), (1e7, 1.0), (2e8, 0.1)])
def test_the_forcing_integral_does_not_carry_the_constant_rows_drift(
    rate_per_s: float, interval_s: float
) -> None:
    """The drift reached every state that reads the constant, not only the constant.

    Each squaring multiplies the constant's entry into the forcing column.
    Before `PL-2MD9`, this column was therefore off by the same factor as the
    constant: -1.9e-9, -3.0e-8 and -6.0e-8 relative error in these three
    cases. The result was a delivered fraction scaled without any setting
    changing. With the row restored, the column is within 1.4e-15 of the
    closed form in all three cases, measured on 2026-10-03. The tolerance
    below is ten times above that and five orders of magnitude below the
    drift.
    """

    propagator = matrix_exponential(_forced_decay(rate_per_s), interval_s)

    assert propagator[0][1] == pytest.approx(
        FORCED_DECAY_LEVEL * -expm1(-rate_per_s * interval_s), rel=1.4e-14
    )


@pytest.mark.parametrize(
    ("first_s", "second_s", "horizon_s"),
    [(0.1, 0.1, 1.0), (0.1, 3599.9, 3600.0), (12.0, 48.0, 60.0)],
)
def test_propagating_twice_matches_propagating_once(
    first_s: float, second_s: float, horizon_s: float
) -> None:
    """exp(A s) exp(A t) = exp(A (s + t)) for a constant A, at any split.

    This identity is what lets the interval be an argument rather than a
    fixed step. A caller taking many small steps and a caller asking for the
    whole horizon at once must reach the same state.

    `horizon_s` selects the row of `WORST_RELATIVE_ERROR_MEASURED` whose
    tolerance this pair must meet. It is the nearest measured interval at or
    above the total, because the total sets how many squarings are done.
    """

    matrix = (
        (-0.0333, 0.0222, 0.0, 0.004),
        (0.0111, -0.0484, 0.0342, 0.0),
        (0.0, 0.0238, -0.0238, 0.0),
        (0.0, 0.0, 0.0, 0.0),
    )
    composed = multiply(matrix_exponential(matrix, second_s), matrix_exponential(matrix, first_s))
    direct = matrix_exponential(matrix, first_s + second_s)
    tolerance = _relative_tolerance(horizon_s)

    for row in range(4):
        for column in range(4):
            assert composed[row][column] == pytest.approx(
                direct[row][column], rel=tolerance, abs=1e-300
            )


def test_many_small_steps_match_one_long_one() -> None:
    """Stepping is exact, so repeating the step must reach the exact horizon.

    A shipped run depends on this property, and an operator split does not
    have it. Taking 600 steps of 0.1 s lands on the same state as a single
    60 s propagation, within rounding rather than within a step-size error.
    """

    matrix = _two_compartment_exchange(0.0111, 0.0267)
    step = matrix_exponential(matrix, 0.1)

    state: tuple[float, ...] = (0.05, 0.0)

    for _ in range(600):
        state = propagate(step, state)

    assert state == pytest.approx(
        propagate(matrix_exponential(matrix, 60.0), (0.05, 0.0)), rel=_relative_tolerance(60.0)
    )


def test_a_step_size_change_within_one_system_obeys_the_semigroup_property() -> None:
    """Two half steps of one uptake system reach where one whole step does.

    `AgentUptakeSystem` keeps the propagator it built for one step and reuses
    it while its cache key is unchanged. The step is part of that key. If the
    step were left out, a system that changed its step would go on using the
    old step's exp(A dt), and every value it reported would belong to a later
    instant than the one reported. No guard and no accounting check would
    notice, because the delivered and exhausted agent come from the same
    wrong propagator (`PL-4H4T`).

    The expected value does not depend on the cache. For a constant matrix,
    exp(A x 0.05) squared equals exp(A x 0.1), so a system that takes two
    0.05 s steps must reach the state that an identical system reaches after
    one 0.1 s step. Both systems first take 600 steps of 0.1 s, so the first
    one holds a 0.1 s propagator when its step changes.

    The worst relative difference on the shipped code was 5.4e-16, measured
    on 2026-10-17. A system that reused the 0.1 s propagator for the half
    steps would advance 0.2 s instead of 0.1 s, and its alveolar fraction
    would be 1.8e-3 of its value too high.
    """

    halves = AgentUptakeSystem.for_agent("sevoflurane")
    whole = AgentUptakeSystem.for_agent("sevoflurane")

    for _ in range(600):
        halves.advance(SimulationStep(0.1))
        whole.advance(SimulationStep(0.1))

    halves.advance(SimulationStep(0.05))
    halves.advance(SimulationStep(0.05))
    whole.advance(SimulationStep(0.1))

    assert halves.state_vector() == pytest.approx(whole.state_vector(), rel=1e-12, abs=1e-18)


@pytest.mark.parametrize("interval_s", [0.1, 1.0, 100.0, 100000.0])
def test_propagator_of_a_transfer_system_is_entrywise_nonnegative(interval_s: float) -> None:
    """Check the guarantee that the shift exists to provide, on a stiff, sparse system.

    The rates below span five orders of magnitude, which is where a series in
    the unshifted matrix cancels hardest. No entry may be negative. A
    negative entry is what would carry a compartment below zero, and that
    would be reported as a numerical failure of the model rather than of the
    summation.
    """

    fast, slow = 5.0, 5e-5
    matrix = (
        (-fast, fast, 0.0, 0.0),
        (slow, -(slow + fast), fast, 0.0),
        (0.0, slow, -(slow + slow), slow),
        (0.0, 0.0, slow, -slow),
    )

    for row in matrix_exponential(matrix, interval_s):
        for value in row:
            assert value >= 0.0


def test_the_scaling_threshold_is_what_decides_a_squaring() -> None:
    """Crossing the documented bound must not change the result.

    Two intervals on either side of `MAXIMUM_SERIES_ARGUMENT_NORM / ||B||`
    take different paths through the routine. One takes no squarings and the
    other takes one. Agreement across the boundary is what shows that the
    scaling is undone correctly.
    """

    matrix = _two_compartment_exchange(0.5, 0.5)
    boundary_s = MAXIMUM_SERIES_ARGUMENT_NORM

    below = matrix_exponential(matrix, boundary_s * 0.999)
    above = matrix_exponential(matrix, boundary_s * 1.001)

    assert isclose(below[0][0], above[0][0], rel_tol=2e-3)
    assert below[0][0] == pytest.approx(0.5 * (1.0 + exp(-boundary_s * 0.999)), rel=1e-14)
    assert above[0][0] == pytest.approx(0.5 * (1.0 + exp(-boundary_s * 1.001)), rel=1e-14)


@pytest.mark.parametrize(
    ("matrix", "message"),
    [
        ((), "^matrix has no rows$"),
        (((0.0, 0.0),), "^matrix has 1 rows but row 0 has 2 entries, so it is not square$"),
        (((float("nan"),),), r"^matrix\[0\]\[0\] is nan, which is not finite$"),
        (((float("inf"),),), r"^matrix\[0\]\[0\] is inf, which is not finite$"),
    ],
)
def test_rejects_a_matrix_it_cannot_exponentiate(matrix: Matrix, message: str) -> None:
    with pytest.raises(SimulationConfigurationError, match=message):
        matrix_exponential(matrix, 0.1)


def test_rejects_a_negative_off_diagonal_entry() -> None:
    """A negative transfer rate is refused, not shifted around.

    The nonnegativity guarantee applies to Metzler matrices only. Accepting a
    matrix outside that class would return a propagator that silently lacks
    the property the rest of `core/` relies on. Moler and Van Loan's own
    counterexample for Method 1 is such a matrix. It is a reminder that the
    class is a real restriction rather than a formality.
    """

    with pytest.raises(
        SimulationConfigurationError,
        match=(
            r"^matrix\[1\]\[0\] is -64\.0, but an off-diagonal entry is a transfer rate "
            "and must not be negative$"
        ),
    ):
        matrix_exponential(((-49.0, 24.0), (-64.0, 31.0)), 1.0)


@pytest.mark.parametrize("interval_s", [0.0, -0.1, float("nan"), float("inf")])
def test_rejects_an_interval_that_is_not_a_positive_duration(interval_s: float) -> None:
    with pytest.raises(SimulationConfigurationError, match="interval_s"):
        matrix_exponential(((0.0,),), interval_s)


def test_propagate_rejects_a_state_of_the_wrong_length() -> None:
    with pytest.raises(
        SimulationConfigurationError, match="^state has 3 entries but the propagator is 2x2$"
    ):
        propagate(_identity(2), (0.0, 0.0, 0.0))


def test_propagate_rejects_a_non_finite_state_entry() -> None:
    with pytest.raises(
        SimulationConfigurationError, match=r"^state\[1\] is nan, which is not finite$"
    ):
        propagate(_identity(2), (0.0, float("nan")))


def test_multiply_rejects_operands_of_different_sizes() -> None:
    with pytest.raises(
        SimulationConfigurationError,
        match="^cannot multiply a 2x2 matrix by a 3x3 one; the sizes must match$",
    ):
        multiply(_identity(2), _identity(3))


def test_multiply_rejects_a_ragged_operand() -> None:
    with pytest.raises(
        SimulationConfigurationError,
        match="^right has 2 rows but row 1 has 1 entries, so it is not square$",
    ):
        multiply(_identity(2), ((0.0, 0.0), (0.0,)))


# `PL-3PRZ`: the squarings can produce a result that is finite and entrywise
# nonnegative but is still not a propagator. `_require_finite` accepted both of
# the states below. `AgentUptakeSystem` then stepped on them and reported a
# concentration of exactly zero while its mass-balance check passed.


def test_refuses_the_zero_matrix_the_squarings_can_produce() -> None:
    """Every mode decays below the smallest subnormal, in a system with no constant state.

    Over 100 s the two modes fall to `exp(-1000)` and `exp(-900)`, and eleven
    squarings carry both below the smallest subnormal. The zero matrix is
    finite and entrywise nonnegative, so it satisfies both properties that
    this module states.

    The zero matrix was first reached at an alveolar volume of 1e-300 L
    (`PL-3PRZ`). Since `PL-2MD9`, that case stops earlier, at
    `MAXIMUM_SQUARINGS`. A matrix with a constant state no longer reaches the
    zero matrix at all, because that state's row is kept as the identity's row.
    """

    with pytest.raises(
        SimulationConfigurationError,
        match=(
            r"^the propagator is the 2x2 zero matrix, which is singular and so is the "
            r"exponential of nothing; its entries have underflowed and it no longer "
            r"solves the system$"
        ),
    ):
        matrix_exponential(((-10.0, 0.0), (0.0, -9.0)), 100.0)


def test_refuses_an_interval_needing_more_squarings_than_its_error_bound_allows() -> None:
    """`PL-2MD9`: past `MAXIMUM_SQUARINGS` the result is refused, not returned.

    Each squaring can double the error that the scaled propagator carries.
    Past 32 squarings, that error bound exceeds one part in a million. A rate
    of 2**29 per second over 1 s needs 33. The refusal comes before any
    arithmetic. That is what stops an alveolar volume of 1e-18 L from
    returning a propagator that is wrong in every entry.
    """

    with pytest.raises(
        SimulationConfigurationError,
        match=(
            r"^the shifted matrix has a row sum of 536870912\.0 over 1\.0 s, which takes "
            r"33 squarings to scale to the series bound of 0\.0625; past 32 the rounding "
            r"error they amplify can exceed one part in a million, so the result could not "
            r"be established in double precision$"
        ),
    ):
        matrix_exponential(((-(2.0**29), 0.0), (0.0, 0.0)), 1.0)


def test_the_most_squarings_the_module_performs_are_still_performed() -> None:
    """Test the boundary of the refusal above, from the side that it must not catch.

    A rate of 2**28 per second over 1 s needs exactly `MAXIMUM_SQUARINGS`
    squarings, and it is propagated. Its decaying mode is far below the
    smallest subnormal, and its constant state's row is the identity's row.
    """

    shifted_row_sum = 2.0**28

    assert MAXIMUM_SQUARINGS == 32
    assert shifted_row_sum / MAXIMUM_SERIES_ARGUMENT_NORM == 2.0**MAXIMUM_SQUARINGS
    assert matrix_exponential(((-shifted_row_sum, 0.0), (0.0, 0.0)), 1.0) == (
        (0.0, 0.0),
        (0.0, 1.0),
    )


def test_a_single_mode_decaying_past_the_subnormal_floor_is_not_refused() -> None:
    """This is a case that the refusal of the zero matrix above must not catch.

    `exp(-0.5 * 3600)` is a real number that no double can hold, so 0.0 is
    the correct entry for that mode over that horizon. What separates this
    case from the failure is that the undamped mode beside it still
    propagates.
    """

    propagator = matrix_exponential(((-0.5, 0.0), (0.0, 0.0)), 3600.0)

    assert propagator[0][0] == 0.0
    assert propagator[1][1] == 1.0


def test_refuses_a_matrix_whose_scaled_norm_overflows_rather_than_raising_overflowerror() -> None:
    """`ceil(log2(inf))` raises `OverflowError`, which no caller here keys on.

    The row sum is finite, at 1.3e+307 over 0.1 s. The division by
    `MAXIMUM_SERIES_ARGUMENT_NORM` is what reaches `inf`. The model reached
    this case at an alveolar volume of 1e-309 L.
    """

    with pytest.raises(
        SimulationConfigurationError,
        match=(
            r"^the shifted matrix has a row sum of 1\.3000000000000002e\+307 over 0\.1 s, "
            r"and scaling it to the series bound of 0\.0625 overflows, so the number of "
            r"squarings is not computable; the rates in this matrix are too large to "
            r"propagate in double precision$"
        ),
    ):
        matrix_exponential(((-1.3e308, 0.0), (0.0, 0.0)), 0.1)


def test_propagate_sums_each_row_with_the_compensation_sum_provides() -> None:
    """`PL-R460`: the property that let the inner product be rewritten without changing results.

    `propagate()` sums each row's products with the built-in `sum`, whose
    float path is Neumaier-compensated. The products below are `1.0`, `1e16`
    and `-1e16`. A naive left fold loses the `1.0` when it adds it to `1e16`,
    and returns `0.0`. `sum` returns the exact `1.0`.

    That is why `sum(map(mul, row, state))` and the generator over
    `range(size)` that it replaced are bit-identical rather than merely close.
    Both hand `sum` the same floats, and the compensation makes the result
    independent of how they were produced. A rewrite to an explicit
    accumulator loop would be neither bit-identical nor close. It would change
    a safety-critical result without failing a test that only checked the
    products. This test pins the property.
    """

    ones = ((1.0, 1.0, 1.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0))

    advanced = propagate(ones, (1.0, 1e16, -1e16))

    assert advanced[0] == 1.0
    assert advanced[1] == 1.0
    assert advanced[2] == -1e16
