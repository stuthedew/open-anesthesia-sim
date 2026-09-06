"""Verification of the propagator against solutions written out by hand.

Every expected value below is an analytic solution of the same system rather
than a second run of the code under test: a scalar decay, the closed form of
two well-mixed volumes exchanging, the exact integral of a constant rate, and
the semigroup identity the exponential of a constant matrix must satisfy.

What the module promises beyond accuracy is checked too, on the matrix class
the promise is made for: an entrywise nonnegative propagator, so that an exact
step cannot carry a compartment below zero through a rounding artifact and be
reported as a numerical failure of the model.
"""

from math import exp, isclose, ulp

import pytest

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.matrix_exponential import (
    MAXIMUM_SERIES_ARGUMENT_NORM,
    Matrix,
    matrix_exponential,
    multiply,
    propagate,
)

WORST_RELATIVE_ERROR_MEASURED = {
    0.1: 2.3e-16,
    1.0: 1.8e-15,
    37.5: 3.4e-15,
    60.0: 2.5e-14,
    600.0: 4.5e-14,
    3600.0: 2.0e-12,
}
"""Worst relative disagreement with the analytic answer, per interval.

Measured 2026-09-06 across every comparison in this file. The figures grow
with the interval because the number of squarings does - none at 0.1 s, and
sixteen at 3600 s, each of which can at most double the relative error - so
one flat tolerance would either pass a real regression at 0.1 s or fail
correct arithmetic at 3600 s. The module's truncation is ten orders below all
of these (see its docstring), so what is being bounded here is squaring
roundoff and nothing else.
"""

TOLERANCE_MARGIN = 20.0
"""How far above the measured error the tests fail.

Wide enough that a different machine's rounding does not fail the suite,
narrow enough that losing an order of magnitude of accuracy does.
"""


def _relative_tolerance(interval_s: float) -> float:
    return WORST_RELATIVE_ERROR_MEASURED[interval_s] * TOLERANCE_MARGIN


def _identity(size: int) -> Matrix:
    return tuple(tuple(float(row == column) for column in range(size)) for row in range(size))


def _two_compartment_exchange(rate_left: float, rate_right: float) -> Matrix:
    """Return the matrix of two well-mixed volumes exchanging with each other.

    `d x0/dt = rate_left (x1 - x0)`, `d x1/dt = rate_right (x0 - x1)`, which is
    the circuit and alveolar pair of `docs/MODEL.md` with ventilation as the
    only transfer between them. Its closed form is written out below.
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

    Two volumes exchanging relax towards a common equilibrium with the single
    rate constant `rate_left + rate_right`, the equilibrium being the
    flow-weighted mean of where they started. That closed form is written out
    here; the module under test never sees it.
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

    `d x/dt = k`, with the constant carried as a state of its own, is the shape
    every accumulator row of the uptake system uses. Its exact solution over
    the interval is `k * interval_s`, with no approximation anywhere in it.
    """

    rate = 0.00333
    interval_s = 90.0
    propagator = matrix_exponential(((0.0, rate), (0.0, 0.0)), interval_s)

    advanced = propagate(propagator, (0.0, 1.0))

    assert advanced[0] == pytest.approx(rate * interval_s, rel=1e-14)


@pytest.mark.parametrize("interval_s", [0.1, 60.0, 3600.0])
def test_the_constant_state_survives_the_shift(interval_s: float) -> None:
    """Bound the one cost the module's shift is documented as having.

    A state whose own rate is far below the shift - the constant forcing
    state, whose exact propagator entry is 1 - is recovered as a product of
    two separately rounded factors rather than landing on 1 exactly. It must
    stay within a few units in the last place, because every accumulator row
    integrates against it: a constant that drifted would scale delivered agent
    with it.
    """

    matrix = ((-0.5, 0.5, 0.0), (0.0125, -0.0125, 0.0), (0.0, 0.0, 0.0))

    constant = matrix_exponential(matrix, interval_s)[2][2]

    assert abs(constant - 1.0) <= 8.0 * ulp(1.0)


@pytest.mark.parametrize(
    ("first_s", "second_s", "horizon_s"),
    [(0.1, 0.1, 1.0), (0.1, 3599.9, 3600.0), (12.0, 48.0, 60.0)],
)
def test_propagating_twice_matches_propagating_once(
    first_s: float, second_s: float, horizon_s: float
) -> None:
    """exp(A s) exp(A t) = exp(A (s + t)) for a constant A, at any split.

    This is the identity that makes the interval an argument rather than a
    fixed step: a caller taking many small steps and a caller asking for the
    whole horizon at once must reach the same state.

    `horizon_s` is the row of `WORST_RELATIVE_ERROR_MEASURED` this pair is held
    to - the nearest measured interval at or above the total, since it is the
    total that sets how many squarings are done.
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

    This is the property a shipped run depends on and the one an operator
    split does not have: 600 steps of 0.1 s land on the same state as a single
    60 s propagation, to rounding rather than to a step-size error.
    """

    matrix = _two_compartment_exchange(0.0111, 0.0267)
    step = matrix_exponential(matrix, 0.1)

    state: tuple[float, ...] = (0.05, 0.0)

    for _ in range(600):
        state = propagate(step, state)

    assert state == pytest.approx(
        propagate(matrix_exponential(matrix, 60.0), (0.05, 0.0)), rel=_relative_tolerance(60.0)
    )


@pytest.mark.parametrize("interval_s", [0.1, 1.0, 100.0, 100000.0])
def test_propagator_of_a_transfer_system_is_entrywise_nonnegative(interval_s: float) -> None:
    """The guarantee the shift exists to provide, on a stiff, sparse system.

    The rates below span five orders of magnitude, which is where a series in
    the unshifted matrix cancels hardest. Nothing here may be negative: a
    negative entry is what would carry a compartment below zero and be
    reported as a numerical failure of the model rather than of the summation.
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
    """Cross the documented bound and the answer must not move.

    Two intervals either side of `MAXIMUM_SERIES_ARGUMENT_NORM / ||B||` take
    different paths through the routine - no squarings and one - so agreement
    across the boundary is what says the scaling is undone correctly.
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

    The nonnegativity guarantee holds for Metzler matrices only, so accepting
    one outside that class would return a propagator that quietly no longer
    carries the property the rest of `core/` relies on. Moler and Van Loan's
    own Method 1 counterexample is such a matrix, which is the reminder that
    the class is a real restriction rather than a formality.
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
