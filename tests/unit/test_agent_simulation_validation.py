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
    SimulationExecutionError,
    SimulationNumericalError,
)

# The three constants that set how far a run's numbers may drift before
# `require_valid_agent_accounting()` halts it, restated here rather than
# imported. Everything below uses these restatements and never the imported
# names beside them: a boundary case measured against the constant it is
# testing would follow that constant wherever it moved, which is the whole
# defect (`PL-B7ZV`). Moving one in `core/` therefore fails
# `test_the_accounting_tolerances_are_the_documented_release_tolerances`,
# which is the only place the two are compared. This is the idiom
# `tests/reference/test_coupled_dynamics.py` uses twice, for the model's
# supported input ranges and for the interface's displayed resolution.
#
# `docs/MODEL.md` § "Mass-balance identity" is the documented basis. It calls
# the first two release tolerances, and states the third inline as the
# `max(initial + delivered, 1e-15 L)` denominator that keeps the relative
# error finite before anything has been delivered.
DOCUMENTED_ABSOLUTE_TOLERANCE_L = 1e-12
DOCUMENTED_RELATIVE_TOLERANCE = 1e-9
DOCUMENTED_MINIMUM_RELATIVE_SCALE_L = 1e-15

# How far either side of a threshold the boundary cases probe. 10% is far
# enough out that the floating-point error in constructing the residual — 4.1e-8
# relative at worst, measured across the four cases — cannot reach the
# threshold from either side, and close enough in that a tolerance loosened by
# the orders of magnitude `PL-B7ZV` measured cannot straddle it.
INSIDE_THE_THRESHOLD = 0.9
OUTSIDE_THE_THRESHOLD = 1.1

# The delivered amount each pair of boundary cases is measured against, chosen
# so that the other branch of the pass condition is out of reach and the case
# therefore probes one threshold rather than the disjunction of two. Each case
# asserts that isolation rather than assuming it.
#
# 1 L delivered puts a residual at the relative threshold near 1e-9 L, three
# orders of magnitude above the absolute tolerance, so only the relative branch
# can pass it. 1 µL delivered — an accounting period a few steps old — puts a
# residual at the absolute threshold near 1e-6 relative, three orders above the
# relative tolerance, so only the absolute branch can. Any delivered amount
# below 9e-4 L would serve the second; 1 µL keeps the arithmetic legible.
RELATIVE_BRANCH_DELIVERED_L = 1.0
ABSOLUTE_BRANCH_DELIVERED_L = 1e-6


def _period_short_by(
    delivered_agent_l: float, residual_l: float
) -> tuple[AgentSimulationValidator, AgentSimulationValidationResult]:
    """A completed accounting period whose store is short by `residual_l`.

    The validator is returned alongside its result so that a case can put the
    result back through `require_valid_agent_accounting()`, which is what
    actually halts a run and therefore what these cases are about.

    The residual is built by subtraction, so the value the check sees is the
    one asked for only to a rounding. That is asserted here rather than
    assumed: a case whose constructed residual landed on the wrong side of a
    threshold would pass or fail for a reason that has nothing to do with the
    guard, and would go on looking correct. Measured across the four boundary
    cases, the construction lands within 4.1e-8 relative of the value asked
    for, against probes placed 10% either side of a threshold.
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
    check = validator.check_agent_accounting(currently_stored_agent_l=0.70)

    with pytest.raises(AgentSimulationValidationError, match="Agent accounting validation failed"):
        validator.require_valid_agent_accounting(check)


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


def test_the_accounting_tolerances_are_the_documented_release_tolerances() -> None:
    """The guard's three sensitivity constants are the ones the model documents.

    `require_valid_agent_accounting()` stops a run whose numbers can no longer
    be trusted, and these three decide how far the numbers must drift before it
    does. Until this test, nothing in `tests/`, `tools/` or `docs/` named any of
    them: measured 2026-09-03, the relative tolerance could be loosened to 1e-3,
    the absolute tolerance to 1e-3 L and the scale floor to 1e3 L, one at a
    time, with the whole suite still green (`PL-B7ZV`). At 1e-3 relative an
    eight-hour case at the envelope corner, which delivers 384 L, would carry
    0.38 L unaccounted — roughly a fifth of the circuit and alveolar store —
    with the guard silent.

    So the values are pinned rather than described. The boundary cases below
    prove the guard turns at whatever these are set to; this proves they are
    still what the specification says they are.
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
    """9e-10 of 1 L delivered passes, and only the relative branch can pass it.

    At 9e-10 L the residual is 900 times the absolute tolerance, so this is
    the relative threshold on its own — which is the branch that governs any
    real case, because a case delivering litres reaches an absolute residual
    of 1e-12 L within its first minute.
    """

    residual_l = INSIDE_THE_THRESHOLD * DOCUMENTED_RELATIVE_TOLERANCE * RELATIVE_BRANCH_DELIVERED_L

    validator, check = _period_short_by(RELATIVE_BRANCH_DELIVERED_L, residual_l)

    assert check.absolute_error_l > DOCUMENTED_ABSOLUTE_TOLERANCE_L
    assert check.relative_error < DOCUMENTED_RELATIVE_TOLERANCE
    assert check.passes_validation is True
    validator.require_valid_agent_accounting(check)  # Does not raise.


def test_a_residual_outside_the_relative_tolerance_halts_the_run() -> None:
    """1.1e-9 of 1 L delivered fails, with neither branch able to admit it."""

    residual_l = OUTSIDE_THE_THRESHOLD * DOCUMENTED_RELATIVE_TOLERANCE * RELATIVE_BRANCH_DELIVERED_L

    validator, check = _period_short_by(RELATIVE_BRANCH_DELIVERED_L, residual_l)

    assert check.absolute_error_l > DOCUMENTED_ABSOLUTE_TOLERANCE_L
    assert check.relative_error > DOCUMENTED_RELATIVE_TOLERANCE
    assert check.passes_validation is False
    with pytest.raises(AgentSimulationValidationError, match="Agent accounting validation failed"):
        validator.require_valid_agent_accounting(check)


def test_a_residual_inside_the_absolute_tolerance_passes_on_the_absolute_branch() -> None:
    """9e-13 L passes against 1 µL delivered, with the relative branch out of reach.

    The relative error here is 9e-7, nine hundred times the relative
    tolerance, so the disjunction in `check_agent_accounting()` is what admits
    this residual: a rounding at the scale of a few steps' delivery is not a
    conservation failure, and the absolute branch is what says so.
    """

    residual_l = INSIDE_THE_THRESHOLD * DOCUMENTED_ABSOLUTE_TOLERANCE_L

    validator, check = _period_short_by(ABSOLUTE_BRANCH_DELIVERED_L, residual_l)

    assert check.relative_error > DOCUMENTED_RELATIVE_TOLERANCE
    assert check.absolute_error_l < DOCUMENTED_ABSOLUTE_TOLERANCE_L
    assert check.passes_validation is True
    validator.require_valid_agent_accounting(check)  # Does not raise.


def test_a_residual_outside_the_absolute_tolerance_halts_the_run() -> None:
    """1.1e-12 L fails against 1 µL delivered, with neither branch able to admit it."""

    residual_l = OUTSIDE_THE_THRESHOLD * DOCUMENTED_ABSOLUTE_TOLERANCE_L

    validator, check = _period_short_by(ABSOLUTE_BRANCH_DELIVERED_L, residual_l)

    assert check.relative_error > DOCUMENTED_RELATIVE_TOLERANCE
    assert check.absolute_error_l > DOCUMENTED_ABSOLUTE_TOLERANCE_L
    assert check.passes_validation is False
    with pytest.raises(AgentSimulationValidationError, match="Agent accounting validation failed"):
        validator.require_valid_agent_accounting(check)


def test_the_absolute_tolerance_admits_a_residual_exactly_at_the_threshold() -> None:
    """A residual of exactly 1e-12 L passes, because the specification is inclusive.

    `docs/MODEL.md` § "Mass-balance test" writes the condition as
    |epsilon_M| <= epsilon_absolute,max, so a residual of exactly the tolerance
    is a pass. Tightening the comparison to `<` would change the documented
    condition rather than a value, and the cases above — placed 10% either side
    — cannot see it; this is the only case that can.

    The construction is exact rather than approximate, which is what makes an
    equality boundary testable at all. A picolitre delivered, nothing exhausted
    and nothing stored leaves the residual as the delivered amount itself: no
    subtraction of neighbouring quantities, so nothing is rounded, and the
    result is the same double the tolerance is written as. The relative branch
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
    validator.require_valid_agent_accounting(check)  # Does not raise.


def test_the_relative_tolerance_admits_a_residual_exactly_at_the_threshold() -> None:
    """A relative residual of exactly 1e-9 passes, on the same inclusive reading.

    Exact for the same reason, by a different route: a litre delivered and a
    litre exhausted cancel to zero, so the residual is the nanolitre left in
    the store and nothing is rounded, and dividing it by an accounting scale of
    exactly 1 L leaves the same double the tolerance is written as. Building it
    the obvious way — storing a litre less a nanolitre — would round the
    residual by about 5e-17 and settle the case on whichever side of the
    threshold that rounding happened to fall.

    The residual is negative here: agent in the store that the identity says
    should not be there. Both branches read `absolute_error_l`, so the guard is
    symmetric, and the tests above approach each threshold from the other side.
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
    validator.require_valid_agent_accounting(check)  # Does not raise.


def test_the_scale_floor_carries_the_relative_error_before_anything_is_delivered() -> None:
    """`MINIMUM_RELATIVE_SCALE_L` is the denominator when the accounting scale is zero.

    A period with nothing initial and nothing delivered has an accounting
    scale of zero, so the relative error is 0/0 without the floor. Two cases:
    an exact accounting, which is the division that would raise; and an
    unaccounted store, whose relative error is the residual over the floor and
    nothing else.

    The floor decides no verdict here, and cannot. With the scale at 1e-15 L
    the relative branch admits only a residual at or below 1e-24 L, which the
    absolute branch at 1e-12 L already admits — so there is no pass/fail
    boundary either side of the floor to probe, and its job is to keep the
    reported relative error finite and meaningful. These assertions are what
    hold it to that: moving the floor by the twelve orders of magnitude
    `PL-B7ZV` measured moves the second one by the same twelve.
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
