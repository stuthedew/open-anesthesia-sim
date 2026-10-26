import copy
import pickle
from dataclasses import astuple, replace
from fractions import Fraction
from math import inf, nan

import pytest

from anesthesia_sim.core.agent_simulation_validation import (
    AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L,
    AGENT_ACCOUNTING_RELATIVE_TOLERANCE,
    MINIMUM_RELATIVE_SCALE_L,
    AgentSimulationValidationResult,
    AgentSimulationValidator,
)
from anesthesia_sim.core.exceptions import (
    AgentSimulationValidationError,
    AnesthesiaSimulationError,
    SimulationConfigurationError,
    SimulationExecutionError,
    SimulationNumericalError,
)
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

# These are the three constants that set how far a run's numbers may drift
# before `require_valid_agent_accounting()` halts the run. They are restated
# here rather than imported. Every test below uses these restated values and
# never the imported names. A boundary case measured against the constant it
# tests would move with that constant wherever it moved, so it could never
# catch a change to it. That was the whole defect in `PL-B7ZV`. Moving one of
# the constants in `core/` therefore fails
# `test_the_accounting_tolerances_are_the_documented_release_tolerances`,
# which is the only place that compares the two sets of values.
# `tests/reference/test_coupled_dynamics.py` uses the same idiom twice: for
# the model's supported input ranges and for the interface's displayed
# resolution.
#
# `docs/MODEL.md` § "Mass-balance identity" documents all three. It calls the
# first two release tolerances. It states the third inline, in the denominator
# `max(initial + delivered, 1e-15 L)`, which keeps the relative error finite
# before any agent has been delivered.
DOCUMENTED_ABSOLUTE_TOLERANCE_L = 1e-12
DOCUMENTED_RELATIVE_TOLERANCE = 1e-9
DOCUMENTED_MINIMUM_RELATIVE_SCALE_L = 1e-15

# These set how far on either side of a threshold the boundary cases probe.
# 10% is far enough out that the floating-point error in building the residual
# cannot carry a case across the threshold from either side. That error is at
# most 4.1e-8 relative, measured across the four cases. 10% is also close
# enough in that a tolerance loosened by the orders of magnitude that
# `PL-B7ZV` measured cannot still fall between the two probes.
INSIDE_THE_THRESHOLD = 0.9
OUTSIDE_THE_THRESHOLD = 1.1

# These are the delivered amounts that each pair of boundary cases is measured
# against. Each amount puts the other branch of the pass condition out of
# reach. Each case therefore probes one threshold, rather than the disjunction
# of two (a pass on either branch). Each case asserts that the other branch is
# out of reach rather than assuming it.
#
# With 1 L delivered, a residual at the relative threshold is near 1e-9 L.
# That is three orders of magnitude above the absolute tolerance, so only the
# relative branch can pass it. 1 µL is about what an accounting period a few
# steps old has delivered. With 1 µL delivered, a residual at the absolute
# threshold is near 1e-6 relative. That is three orders above the relative
# tolerance, so only the absolute branch can pass it. Any delivered amount
# less than 9e-4 L would serve for the second pair. 1 µL keeps the arithmetic
# easy to read.
RELATIVE_BRANCH_DELIVERED_L = 1.0
ABSOLUTE_BRANCH_DELIVERED_L = 1e-6


# This pattern matches the end of a shared guard's error message. The message
# names the refused value and the reason it was refused (`PL-T137`). The
# guard's own tests pin each reason. The tests here pin the field's name.
REFUSAL_REASON = r", and [^ ]+ is (?:not finite|not greater than zero|negative)$"


def _period_short_by(
    delivered_agent_l: float, residual_l: float
) -> tuple[AgentSimulationValidator, AgentSimulationValidationResult]:
    """Return a completed accounting period whose store is short by `residual_l`.

    The validator is returned with its result so that a case can pass the same
    store, `check.currently_stored_agent_l`, back through
    `require_valid_agent_accounting()`. That guard is what actually halts a
    run, so it is what these cases test. The guard recomputes the check from
    the validator it is called on. Reading the store back from the result keeps
    the two calls measuring the same accounting period.

    The residual is built by subtraction, so the value the check sees matches
    the requested value only to within rounding. This function asserts that
    match rather than assuming it. If a constructed residual landed on the
    wrong side of a threshold, its case would pass or fail for a reason that
    has nothing to do with the guard, and would still look correct. Measured
    across the four boundary cases, the constructed residual is within 4.1e-8
    relative of the requested value. The probes sit 10% on either side of a
    threshold.
    """

    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(
        delivered_agent_l=delivered_agent_l, exhausted_agent_l=0.0
    )
    check = validator.check_agent_accounting(
        currently_stored_agent_l=delivered_agent_l - residual_l
    )

    assert check.absolute_error_l == pytest.approx(residual_l, rel=1e-6)

    return validator, check


def test_exact_accounting_passes_validation() -> None:
    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(delivered_agent_l=1.0, exhausted_agent_l=0.25)

    check = validator.check_agent_accounting(currently_stored_agent_l=0.75)

    assert check.unaccounted_agent_l == pytest.approx(0.0)
    assert check.absolute_error_l == pytest.approx(0.0)
    assert check.passes_validation is True


def test_missing_agent_fails_validation() -> None:
    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(delivered_agent_l=1.0, exhausted_agent_l=0.25)

    check = validator.check_agent_accounting(currently_stored_agent_l=0.70)

    assert check.unaccounted_agent_l == pytest.approx(0.05)
    assert check.absolute_error_l == pytest.approx(0.05)
    assert check.passes_validation is False


def test_unexpected_extra_agent_fails_validation() -> None:
    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(delivered_agent_l=1.0, exhausted_agent_l=0.25)

    check = validator.check_agent_accounting(currently_stored_agent_l=0.80)

    assert check.unaccounted_agent_l == pytest.approx(-0.05)
    assert check.absolute_error_l == pytest.approx(0.05)
    assert check.passes_validation is False


def test_initial_agent_is_included_in_accounting() -> None:
    validator = AgentSimulationValidator(initial_agent_l=0.5)

    check = validator.check_agent_accounting(currently_stored_agent_l=0.5)

    assert check.unaccounted_agent_l == pytest.approx(0.0)
    assert check.passes_validation is True


def test_require_valid_raises_specific_project_exception() -> None:
    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(delivered_agent_l=1.0, exhausted_agent_l=0.25)

    with pytest.raises(AgentSimulationValidationError, match="Agent accounting validation failed"):
        validator.require_valid_agent_accounting(currently_stored_agent_l=0.70)


def test_require_valid_agent_accounting_reads_the_validators_own_state() -> None:
    """The verdict and the halt message describe the validator the guard is called on.

    The guard used to take a completed `AgentSimulationValidationResult` and
    read only that result, never `self`. So one validator could silently judge
    another validator's accounting period. The halt message would then have
    named that other period's totals, and that message is the only explanation
    a reader gets of why a run stopped (`PL-X204`). The guard now takes the
    store instead. That makes the mismatch impossible to express, not merely
    absent from the current callers, because there is no result to pass in.

    The test shows this with two accounting periods and one store. Both
    validators are checked against the same store of 0.75 L. That store
    balances the first period exactly and leaves the second period a litre
    short. So the store alone decides nothing, and each validator's own state
    decides everything.
    """

    balanced = AgentSimulationValidator()
    balanced.record_external_agent_transfer(delivered_agent_l=1.0, exhausted_agent_l=0.25)

    short = AgentSimulationValidator()
    short.record_external_agent_transfer(delivered_agent_l=2.0, exhausted_agent_l=0.25)

    passing = balanced.require_valid_agent_accounting(currently_stored_agent_l=0.75)

    assert passing.passes_validation is True
    assert passing.delivered_agent_l == 1.0
    assert passing.currently_stored_agent_l == 0.75

    with pytest.raises(AgentSimulationValidationError) as raised:
        short.require_valid_agent_accounting(currently_stored_agent_l=0.75)

    assert "delivered=2.000000e+00 L" in str(raised.value)
    assert "unaccounted=1.000000e+00 L" in str(raised.value)


def test_accounting_exception_inherits_project_hierarchy() -> None:
    error = AgentSimulationValidationError("test failure")

    assert isinstance(error, SimulationNumericalError)
    assert isinstance(error, SimulationExecutionError)
    assert isinstance(error, AnesthesiaSimulationError)


def test_reset_clears_recorded_external_agent() -> None:
    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(delivered_agent_l=1.0, exhausted_agent_l=0.25)

    validator.reset(initial_agent_l=0.2)

    assert validator.initial_agent_l == 0.2
    assert validator.delivered_agent_l == 0.0
    assert validator.exhausted_agent_l == 0.0


@pytest.mark.parametrize("total", ["initial_agent_l", "delivered_agent_l", "exhausted_agent_l"])
@pytest.mark.parametrize(
    ("value", "error", "message"),
    [
        pytest.param(
            -0.1,
            SimulationConfigurationError,
            " must be nonnegative and finite" + REFUSAL_REASON,
            id="negative",
        ),
        pytest.param(
            nan,
            SimulationConfigurationError,
            " must be nonnegative and finite" + REFUSAL_REASON,
            id="nan",
        ),
        pytest.param(
            inf,
            SimulationConfigurationError,
            " must be nonnegative and finite" + REFUSAL_REASON,
            id="infinite",
        ),
        pytest.param("1", TypeError, " of '1' has type str", id="str"),
        pytest.param(True, TypeError, " of True has type bool", id="bool"),
    ],
)
def test_a_direct_write_is_held_to_the_constructors_checks(
    total: str, value: object, error: type[Exception], message: str
) -> None:
    """An assignment after construction is refused for each value the constructor refuses.

    Until `PL-19Y0`, only `__post_init__` checked the three totals. A negative
    or infinite total assigned to a validator after construction was stored,
    and every later check of the identity used it. When a value is refused,
    nothing is written.
    """

    validator = AgentSimulationValidator(
        initial_agent_l=0.31, delivered_agent_l=0.79, exhausted_agent_l=0.17
    )
    held = astuple(validator)

    with pytest.raises(error, match=f"^{total}{message}"):
        setattr(validator, total, value)

    assert astuple(validator) == held


def test_a_total_that_overflows_is_refused_where_it_is_written() -> None:
    """A running total above the largest float is refused when written, not stored as infinity.

    `record_external_agent_transfer` checks each transfer that it receives.
    Until `PL-19Y0`, nothing checked the sum that it stored, so two transfers
    of 1.7e308 L made an infinity. No run delivers anywhere near that amount.
    The write now applies the same check to the total that the constructor
    applies, and a refused write leaves the total as it was.
    """

    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(delivered_agent_l=1.7e308, exhausted_agent_l=0.0)

    with pytest.raises(
        SimulationConfigurationError,
        match="^delivered_agent_l must be nonnegative and finite" + REFUSAL_REASON,
    ):
        validator.record_external_agent_transfer(delivered_agent_l=1.7e308, exhausted_agent_l=0.0)

    assert validator.delivered_agent_l == 1.7e308


def test_a_copy_of_the_validator_is_held_to_the_same_checks() -> None:
    """`replace`, a copy and a pickle each write through `__setattr__`, so they refuse what it does.

    `dataclasses.replace` builds a new validator through the writes that its
    constructor makes. A copy and a pickle restore the totals one at a time
    through `__setattr__`. So a total planted by bypassing the guard is refused
    when a copy or a pickle is made (`PL-19Y0`).
    """

    validator = AgentSimulationValidator(
        initial_agent_l=0.31, delivered_agent_l=0.79, exhausted_agent_l=0.17
    )
    refused = "^exhausted_agent_l must be nonnegative and finite" + REFUSAL_REASON

    with pytest.raises(SimulationConfigurationError, match=refused):
        replace(validator, exhausted_agent_l=-0.17)

    smuggled = copy.copy(validator)
    object.__setattr__(smuggled, "exhausted_agent_l", -0.17)

    with pytest.raises(SimulationConfigurationError, match=refused):
        copy.copy(smuggled)

    with pytest.raises(SimulationConfigurationError, match=refused):
        pickle.loads(pickle.dumps(smuggled))


# At desflurane's 18% vaporizer maximum and 10 L/min of fresh gas, one step at
# the 1 ms step floor delivers 0.18 * 10 L/min * (1 ms / 60,000 ms/min) = 3e-5 L.
# The step floor is the shortest step the model allows. A longer step transfers
# more, but the floor gives a 24 h run the most steps, and so the most additions
# that can round. That makes it the worst case for the running totals. The
# value is computed here rather than read from the model.
WORST_CASE_TRANSFER_PER_STEP_L = 0.18 * 10.0 / 60_000.0

# Delivering that amount at every step for 24 h adds up to 2592 L. These cases
# start the totals at 2500 L, because rounding loses the most when the totals
# are largest. At 2500 L, one unit in the last place is 4.5e-13 L.
LATE_IN_A_DAY_LONG_RUN_L = 2500.0

# 200,000 steps keeps the case under a second. Over that many steps from
# 2500 L, plain addition drifted 1.2e-11 relative to the exact sum, measured
# 2026-10-25 (`PL-XST1`).
STEPS_IN_THE_SAMPLE = 200_000

# Kahan summation's error bound is 2u + O(n u^2) relative to the sum of the
# addends, where u = 2**-53 (Higham, *Accuracy and Stability of Numerical
# Algorithms*, 2nd ed., SIAM, 2002, equation 4.8). Over the 8.64e7 steps of a
# day, the O(n u^2) term is about 1e-24, so 2u is the bound at every supported
# run length. That bound is about 450,000 times smaller than a tenth of
# `DOCUMENTED_RELATIVE_TOLERANCE`.
COMPENSATED_SUM_BOUND = 2 * 2.0**-53


def _relative_drift(total_l: float, exact_l: Fraction) -> float:
    return float(abs(Fraction(total_l) - exact_l) / exact_l)


def test_the_running_agent_totals_stay_within_a_tenth_of_the_accounting_tolerance() -> None:
    """Each running total stays within Kahan summation's bound of the exact sum.

    Until `PL-XST1`, each step's transfer was added to its total with a plain
    `+=`. Each addition could then round by up to half a unit in the last
    place, always in the same direction for a nearly constant transfer. Over a
    24 h run at the 1 ms step floor, that drift brought the residual of a
    correct run within a few percent of the relative tolerance at which the
    run is halted (`docs/MODEL.md` § "Mass-balance identity"). The residual is
    the gap between the two sides of the accounting identity. The expected
    sums are computed exactly, with `Fraction`, rather than by the code under
    test. The test also computes the plain sum of the same transfers, which
    drifts from the exact sum by many orders of magnitude more than the bound.
    This shows that the test would fail if the code returned to plain addition.
    """

    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(
        delivered_agent_l=LATE_IN_A_DAY_LONG_RUN_L, exhausted_agent_l=LATE_IN_A_DAY_LONG_RUN_L
    )
    exhausted_per_step_l = WORST_CASE_TRANSFER_PER_STEP_L * 0.97
    plain_delivered_l = LATE_IN_A_DAY_LONG_RUN_L

    for _ in range(STEPS_IN_THE_SAMPLE):
        validator.record_external_agent_transfer(
            delivered_agent_l=WORST_CASE_TRANSFER_PER_STEP_L, exhausted_agent_l=exhausted_per_step_l
        )
        plain_delivered_l += WORST_CASE_TRANSFER_PER_STEP_L

    exact_delivered_l = (
        Fraction(LATE_IN_A_DAY_LONG_RUN_L)
        + Fraction(WORST_CASE_TRANSFER_PER_STEP_L) * STEPS_IN_THE_SAMPLE
    )
    exact_exhausted_l = (
        Fraction(LATE_IN_A_DAY_LONG_RUN_L) + Fraction(exhausted_per_step_l) * STEPS_IN_THE_SAMPLE
    )

    assert _relative_drift(validator.delivered_agent_l, exact_delivered_l) <= (
        COMPENSATED_SUM_BOUND
    )
    assert _relative_drift(validator.exhausted_agent_l, exact_exhausted_l) <= (
        COMPENSATED_SUM_BOUND
    )
    assert _relative_drift(plain_delivered_l, exact_delivered_l) > 1e4 * COMPENSATED_SUM_BOUND
    assert COMPENSATED_SUM_BOUND < DOCUMENTED_RELATIVE_TOLERANCE / 10


def test_a_transfer_whose_second_total_is_refused_writes_neither_total() -> None:
    """A refused transfer leaves both totals and both compensations as they were.

    Until `PL-XST1`, the delivered total was written before the exhausted total
    was checked. So a transfer whose exhausted total overflowed had already
    added to the delivered total when it was refused.
    """

    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(delivered_agent_l=0.79, exhausted_agent_l=1.7e308)
    held = astuple(validator)

    with pytest.raises(
        SimulationConfigurationError,
        match="^exhausted_agent_l must be nonnegative and finite" + REFUSAL_REASON,
    ):
        validator.record_external_agent_transfer(delivered_agent_l=0.11, exhausted_agent_l=1.7e308)

    assert astuple(validator) == held


@pytest.mark.parametrize("term", ["delivered_compensation_l", "exhausted_compensation_l"])
@pytest.mark.parametrize("value", [nan, inf, -inf])
def test_a_compensation_term_must_be_finite(term: str, value: float) -> None:
    """A compensation term that is not finite is refused, and nothing is written.

    A term may be negative, because rounding can leave a total too small as
    well as too large. A term that is not finite would make the next total
    that it corrects not finite either.
    """

    validator = AgentSimulationValidator()
    setattr(validator, term, -1e-17)
    held = astuple(validator)

    with pytest.raises(SimulationConfigurationError, match=f"^{term} must be finite, and "):
        setattr(validator, term, value)

    assert astuple(validator) == held


def test_reset_clears_the_compensation_terms() -> None:
    """A new accounting period starts with no rounding carried over from the last one."""

    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(delivered_agent_l=2500.0, exhausted_agent_l=2500.0)
    validator.record_external_agent_transfer(
        delivered_agent_l=WORST_CASE_TRANSFER_PER_STEP_L,
        exhausted_agent_l=WORST_CASE_TRANSFER_PER_STEP_L,
    )

    assert validator.delivered_compensation_l != 0.0

    validator.reset(initial_agent_l=0.2)

    assert validator.delivered_compensation_l == 0.0
    assert validator.exhausted_compensation_l == 0.0


@pytest.mark.parametrize("initial_agent_l", [-0.1, nan, inf])
def test_a_refused_reset_changes_nothing(initial_agent_l: float) -> None:
    """`reset` writes the new initial total first, so a refused reset clears neither other total.

    Since `PL-19Y0`, the write itself makes the check, and `reset` makes no
    check of its own. Suppose a reset cleared the two transfer totals and then
    refused the initial total. It would leave a validator that describes no
    accounting period.
    """

    validator = AgentSimulationValidator(
        initial_agent_l=0.31, delivered_agent_l=0.79, exhausted_agent_l=0.17
    )
    held = astuple(validator)

    with pytest.raises(
        SimulationConfigurationError,
        match="^initial_agent_l must be nonnegative and finite" + REFUSAL_REASON,
    ):
        validator.reset(initial_agent_l)

    assert astuple(validator) == held


def test_the_accounting_tolerances_are_the_documented_release_tolerances() -> None:
    """The guard's three sensitivity constants are the ones the model documents.

    `require_valid_agent_accounting()` stops a run whose numbers can no longer
    be trusted. These three constants decide how far the numbers must drift
    before it stops the run. Until this test existed, nothing in `tests/`,
    `tools/` or `docs/` named any of them. A measurement on 2026-09-03 found
    that each could be loosened, one at a time, with the whole suite still
    passing: the relative tolerance to 1e-3, the absolute tolerance to 1e-3 L
    and the scale floor to 1e3 L (`PL-B7ZV`). At 1e-3 relative, an eight-hour
    case at the envelope corner delivers 384 L and would carry 0.38 L
    unaccounted for, with the guard silent. That is roughly a fifth of the
    agent stored in the circuit and the alveoli.

    So this test pins the values rather than describing them. The boundary
    cases below prove that the guard changes its verdict at whatever values
    these constants are set to. This test proves that the values are still the
    ones the specification gives.
    """

    assert (
        AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L,
        AGENT_ACCOUNTING_RELATIVE_TOLERANCE,
        MINIMUM_RELATIVE_SCALE_L,
    ) == (
        DOCUMENTED_ABSOLUTE_TOLERANCE_L,
        DOCUMENTED_RELATIVE_TOLERANCE,
        DOCUMENTED_MINIMUM_RELATIVE_SCALE_L,
    ), (
        "the conservation guard's sensitivity has changed; a deliberate change "
        'revises docs/MODEL.md § "Mass-balance identity" — which states both '
        "release tolerances and the scale floor that keeps the relative error "
        "finite — and updates these restated values with it"
    )


def test_a_residual_inside_the_relative_tolerance_passes_on_the_relative_branch() -> None:
    """A residual of 9e-10 of 1 L delivered passes, and only the relative branch can pass it.

    At 9e-10 L the residual is 900 times the absolute tolerance, so this case
    tests the relative threshold on its own. The relative branch is the one
    that decides any real case. A case that delivers litres of agent reaches an
    absolute residual of 1e-12 L within its first minute.
    """

    residual_l = INSIDE_THE_THRESHOLD * DOCUMENTED_RELATIVE_TOLERANCE * RELATIVE_BRANCH_DELIVERED_L

    validator, check = _period_short_by(RELATIVE_BRANCH_DELIVERED_L, residual_l)

    assert check.absolute_error_l > DOCUMENTED_ABSOLUTE_TOLERANCE_L
    assert check.relative_error < DOCUMENTED_RELATIVE_TOLERANCE
    assert check.passes_validation is True
    validator.require_valid_agent_accounting(check.currently_stored_agent_l)  # Does not raise.


def test_a_residual_outside_the_relative_tolerance_halts_the_run() -> None:
    """A residual of 1.1e-9 of 1 L delivered fails, because neither branch can pass it."""

    residual_l = OUTSIDE_THE_THRESHOLD * DOCUMENTED_RELATIVE_TOLERANCE * RELATIVE_BRANCH_DELIVERED_L

    validator, check = _period_short_by(RELATIVE_BRANCH_DELIVERED_L, residual_l)

    assert check.absolute_error_l > DOCUMENTED_ABSOLUTE_TOLERANCE_L
    assert check.relative_error > DOCUMENTED_RELATIVE_TOLERANCE
    assert check.passes_validation is False
    with pytest.raises(AgentSimulationValidationError, match="Agent accounting validation failed"):
        validator.require_valid_agent_accounting(check.currently_stored_agent_l)


def test_a_residual_inside_the_absolute_tolerance_passes_on_the_absolute_branch() -> None:
    """A residual of 9e-13 L passes against 1 µL delivered, with the relative branch out of reach.

    The relative error here is 9e-7, nine hundred times the relative
    tolerance. So this residual passes only because `check_agent_accounting()`
    passes a residual that meets either branch. A rounding error at the scale
    of a few steps' delivery is not a conservation failure, and the absolute
    branch is what lets it pass.
    """

    residual_l = INSIDE_THE_THRESHOLD * DOCUMENTED_ABSOLUTE_TOLERANCE_L

    validator, check = _period_short_by(ABSOLUTE_BRANCH_DELIVERED_L, residual_l)

    assert check.relative_error > DOCUMENTED_RELATIVE_TOLERANCE
    assert check.absolute_error_l < DOCUMENTED_ABSOLUTE_TOLERANCE_L
    assert check.passes_validation is True
    validator.require_valid_agent_accounting(check.currently_stored_agent_l)  # Does not raise.


def test_a_residual_outside_the_absolute_tolerance_halts_the_run() -> None:
    """A residual of 1.1e-12 L fails against 1 µL delivered, because neither branch can pass it."""

    residual_l = OUTSIDE_THE_THRESHOLD * DOCUMENTED_ABSOLUTE_TOLERANCE_L

    validator, check = _period_short_by(ABSOLUTE_BRANCH_DELIVERED_L, residual_l)

    assert check.relative_error > DOCUMENTED_RELATIVE_TOLERANCE
    assert check.absolute_error_l > DOCUMENTED_ABSOLUTE_TOLERANCE_L
    assert check.passes_validation is False
    with pytest.raises(AgentSimulationValidationError, match="Agent accounting validation failed"):
        validator.require_valid_agent_accounting(check.currently_stored_agent_l)


def test_the_absolute_tolerance_admits_a_residual_exactly_at_the_threshold() -> None:
    """A residual of exactly 1e-12 L passes, because the specification is inclusive.

    `docs/MODEL.md` § "Mass-balance test" writes the condition as
    |epsilon_M| <= epsilon_absolute,max, so a residual exactly equal to the
    tolerance passes. Tightening the comparison to `<` would change the
    documented condition rather than a value. The cases above sit 10% on either
    side of the threshold, so they cannot detect that change. This is the only
    case that can.

    The residual is built exactly rather than approximately, which is what
    makes an equality boundary testable at all. With a picolitre delivered,
    nothing exhausted and nothing stored, the residual is the delivered amount
    itself. No nearly equal quantities are subtracted, so nothing is rounded,
    and the residual is the same double as the tolerance. The relative branch
    is far out of reach, at a relative error of 1.
    """

    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(
        delivered_agent_l=DOCUMENTED_ABSOLUTE_TOLERANCE_L, exhausted_agent_l=0.0
    )

    check = validator.check_agent_accounting(currently_stored_agent_l=0.0)

    assert check.absolute_error_l == DOCUMENTED_ABSOLUTE_TOLERANCE_L
    assert check.relative_error > DOCUMENTED_RELATIVE_TOLERANCE
    assert check.passes_validation is True
    validator.require_valid_agent_accounting(check.currently_stored_agent_l)  # Does not raise.


def test_the_relative_tolerance_admits_a_residual_exactly_at_the_threshold() -> None:
    """A relative residual of exactly 1e-9 passes, because this condition is inclusive too.

    This residual is also built exactly, by a different route. A litre
    delivered and a litre exhausted cancel to zero, so the residual is the
    nanolitre left in the store, and nothing is rounded. Dividing that residual
    by an accounting scale of exactly 1 L gives the same double as the
    tolerance. The obvious construction would store a litre less a nanolitre.
    That would round the residual by about 5e-17, and the case would land on
    whichever side of the threshold the rounding happened to put it.

    The residual is negative here. The store holds agent that the identity
    says should not be there. Both branches use `absolute_error_l`, so the
    guard treats a surplus and a shortfall alike. The tests above approach each
    threshold from the other side.
    """

    residual_l = DOCUMENTED_RELATIVE_TOLERANCE * RELATIVE_BRANCH_DELIVERED_L

    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(
        delivered_agent_l=RELATIVE_BRANCH_DELIVERED_L, exhausted_agent_l=RELATIVE_BRANCH_DELIVERED_L
    )

    check = validator.check_agent_accounting(currently_stored_agent_l=residual_l)

    assert check.unaccounted_agent_l == -residual_l
    assert check.relative_error == DOCUMENTED_RELATIVE_TOLERANCE
    assert check.absolute_error_l > DOCUMENTED_ABSOLUTE_TOLERANCE_L
    assert check.passes_validation is True
    validator.require_valid_agent_accounting(check.currently_stored_agent_l)  # Does not raise.


def test_the_scale_floor_carries_the_relative_error_before_anything_is_delivered() -> None:
    """`MINIMUM_RELATIVE_SCALE_L` is the denominator when the accounting scale is zero.

    A period with no initial agent and nothing delivered has an accounting
    scale of zero, so without the floor the relative error would be 0/0. The
    test has two cases. The first is an exact accounting, which is the
    division that would raise. The second is a store with agent unaccounted
    for, whose relative error is the residual divided by the floor and nothing
    else.

    The floor decides no verdict here, and cannot. With the scale at 1e-15 L,
    the relative branch passes only a residual at or below 1e-24 L, and the
    absolute branch at 1e-12 L already passes any such residual. So there is no
    pass/fail boundary on either side of the floor to probe. The floor's job is
    to keep the reported relative error finite and meaningful. These assertions
    enforce that job. Moving the floor by the twelve orders of magnitude that
    `PL-B7ZV` measured moves the relative error in the second assertion by the
    same twelve.
    """

    validator = AgentSimulationValidator()

    exact = validator.check_agent_accounting(currently_stored_agent_l=0.0)

    assert exact.absolute_error_l == 0.0
    assert exact.relative_error == 0.0

    residual_l = 1e-13
    unaccounted = validator.check_agent_accounting(currently_stored_agent_l=residual_l)

    assert unaccounted.absolute_error_l == pytest.approx(residual_l)
    assert unaccounted.relative_error == pytest.approx(
        residual_l / DOCUMENTED_MINIMUM_RELATIVE_SCALE_L
    )


def test_an_annihilated_propagator_cannot_reach_the_accounting_check(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression test for `PL-3PRZ`, at an alveolar volume of 1e-300 L.

    The accounting identity tested above is not what failed here, and making
    it stricter would not have helped. At 1e-300 L the repeated squarings drove
    the propagator to the zero matrix, and `propagate()` returned the zero
    state vector. The identity was then given 0 + 0 - 0 - 0. It balanced
    correctly, on totals that had all been wiped out together. Nothing was
    delivered, exhausted or stored, and the reported alveolar fraction was
    exactly 0.0. That is the plausible-looking number that `CLAUDE.md` ranks
    as worse than every other failure, and every guard in the path was
    satisfied when it was produced.

    The fix is upstream, in `core/matrix_exponential.py`, which refused a zero
    propagator because `exp(A*dt)` is nonsingular. Since `PL-2MD9`, the run at
    this volume stops earlier, at `MAXIMUM_SQUARINGS`. The constant state can
    also no longer be wiped out with the rest. That is why the cap is needed:
    restoring the constant state alone let this volume advance again with
    every other entry destroyed. This test pins the end of the path rather than
    either refusal, so it still fails if the arithmetic goes back to returning
    a value.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    system.alveoli.gas_volume_l = 1e-300

    with pytest.raises(SimulationNumericalError, match="could not be completed"):
        system.advance(SimulationStep(0.1))

    assert system.alveoli.agent_amount_l == 0.0
    assert system.agent_simulation_validator.delivered_agent_l == 0.0


def test_a_propagator_wrong_in_every_entry_cannot_reach_the_accounting_check() -> None:
    """Regression test for `PL-2MD9`, at an alveolar volume of 1e-18 L.

    At that volume the propagator needs 58 squarings, and each squaring can
    double the error that the scaled propagator carries. Before the cap, every
    entry came back wrong by about 100%, and the run advanced three steps with
    its accounting check passing. It recorded 6.4e-32 L delivered where the
    vaporizer had delivered 0.0004 L, and the stored and exhausted totals were
    destroyed to match. That is the same failure as `PL-3PRZ`: a residual
    formed from quantities that one failure corrupted together. The step is
    now refused before any arithmetic runs.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    system.alveoli.gas_volume_l = 1e-18

    with pytest.raises(SimulationNumericalError, match="could not be completed"):
        system.advance(SimulationStep(0.1))

    assert system.agent_simulation_validator.delivered_agent_l == 0.0


def test_an_alveolar_volume_the_model_can_still_step_is_not_refused() -> None:
    """The fix for the regressions above must not have moved this boundary.

    1e-6 L is four orders of magnitude less than any real lung volume, and the
    model steps it without complaint. `PL-3PRZ`'s table recorded that behaviour
    before the fix. A guard that also refused this volume would have traded a
    silent wrong answer for a refusal of the model's own working range.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    system.alveoli.gas_volume_l = 1e-6

    result = system.advance(SimulationStep(0.1))

    assert result.agent_accounting.passes_validation
    assert result.fresh_gas_exchange.delivered_agent_l > 0.0
