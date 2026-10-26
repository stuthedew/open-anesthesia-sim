import copy
import pickle
from dataclasses import replace

import pytest

from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError, SimulationDomainLimitError
from anesthesia_sim.core.numerical_envelope import CompartmentVolume
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.simulation_step import MAXIMUM_SIMULATION_STEP_S, SimulationStep
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    AlveolarVentilation,
    CardiacOutput,
    CaseInstant,
    FreshGasFlow,
    StepCount,
    maximum_step_count,
)
from anesthesia_sim.core.uptake_system import AgentUptakeSystem


def _advance_for(state: SimulationState, duration_s: float) -> None:
    """Advance the state by `duration_s` in steps of the largest supported size.

    A simulated time is reached by taking supported steps, not by asking for
    one large step. `MAXIMUM_SIMULATION_STEP_S` is the longest interval over
    which the settings are held constant. A caller that wants 10 s of
    simulated time takes 100 steps rather than one.
    """

    for _ in range(round(duration_s / MAXIMUM_SIMULATION_STEP_S)):
        state.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))


def test_advance_updates_time_and_complete_uptake_system() -> None:
    state = SimulationState()

    _advance_for(state, duration_s=2.5)

    assert state.elapsed_s == 2.5
    assert state.uptake_system.circuit.inspired_partial_pressure_fraction > 0.0
    assert state.uptake_system.alveoli.partial_pressure_fraction > 0.0
    assert state.uptake_system.patient.total_agent_amount_l > 0.0
    assert state.uptake_system.agent_simulation_validation.passes_validation


def test_reset_preserves_settings_and_clears_dynamic_state() -> None:
    system = AgentUptakeSystem.default()
    system.circuit.set_circuit_volume(CompartmentVolume(5.0))
    system.set_fresh_gas_flow(FreshGasFlow(3.0))
    system.set_delivered_concentration_percent(Percent(6.0))
    system.set_alveolar_ventilation(AlveolarVentilation(5.5))
    system.set_cardiac_output(CardiacOutput(6.0))

    state = SimulationState(uptake_system=system)
    _advance_for(state, duration_s=10.0)

    state.reset()

    assert state.elapsed_s == 0.0
    assert state.uptake_system.circuit.inspired_partial_pressure_fraction == 0.0
    assert state.uptake_system.alveoli.partial_pressure_fraction == 0.0
    assert state.uptake_system.patient.total_agent_amount_l == 0.0

    assert state.uptake_system.circuit.circuit_volume_l == 5.0
    assert state.uptake_system.circuit.fresh_gas_flow_l_min == 3.0
    assert state.uptake_system.circuit.delivered_concentration_percent == 6.0
    assert state.uptake_system.alveoli.alveolar_ventilation_l_min == 5.5
    assert state.uptake_system.patient.cardiac_output_l_min == 6.0


@pytest.mark.parametrize("simulation_step_s", [0.0, -0.1, float("nan")])
def test_rejects_invalid_simulation_step(simulation_step_s: float) -> None:
    with pytest.raises(SimulationConfigurationError):
        SimulationState().advance(SimulationStep(simulation_step_s))


@pytest.mark.parametrize("simulation_step_s", [0.0, -0.1, float("nan"), float("inf")])
def test_an_invalid_initial_step_is_refused_before_a_run_length_is_read_from_it(
    simulation_step_s: float,
) -> None:
    """The state checks the step before it derives the supported run length from it.

    The run-length guard divides the span by the step. If that guard ran
    first, a zero step would raise `ZeroDivisionError` and `nan` would raise
    `ValueError`. A negative step would get a run-length refusal, and an
    infinite step would get no refusal at all. None of these is the refusal
    naming the step that the state's write guard promises (`PL-BMY5`).
    `PL-8W1W` moved that guard from `__post_init__` to `__setattr__`.
    """

    with pytest.raises(SimulationConfigurationError, match="simulation_step_s"):
        SimulationState(
            step_count=StepCount(0), simulation_step_s=SimulationStep(simulation_step_s)
        )


def test_rejects_a_step_above_the_maximum_simulation_step() -> None:
    """Elapsed time must not move for a step that was never simulated.

    `SimulationState` is the class that owns simulated time. This is
    therefore the one place where the refusal has a consequence beyond the
    uptake system. Without it, a caller that caught and ignored the exception
    and then read `elapsed_s` would be told that the run had advanced by a
    step for which nothing was calculated.
    """

    state = SimulationState()
    state.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))
    before_s = state.elapsed_s

    with pytest.raises(SimulationConfigurationError, match="largest supported step"):
        state.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S * 10.0))

    assert state.elapsed_s == before_s


def test_rejects_a_step_below_the_minimum_simulation_step() -> None:
    """Reject the step that PL-YZ17 was filed for, taken as a fresh run's first step.

    The step's guard used to accept 5e-324 s. The run-length guard then
    divided the 86 400 s span by it, which overflows, so `advance()` raised a
    bare `OverflowError`. That is not one of the simulator's own exceptions,
    so a caller catching `AnesthesiaSimulationError` did not catch it at all.
    The minimum-step check now refuses the step first, and the run records no
    step.
    """

    state = SimulationState()

    with pytest.raises(SimulationConfigurationError, match="smallest supported step"):
        state.advance(SimulationStep(5e-324))

    assert state.elapsed_s == 0.0
    assert state.simulation_step_s is None


def test_elapsed_time_is_the_step_count_times_the_step() -> None:
    """Simulated time is computed from the number of steps taken, not by adding them up.

    Ten steps of 0.1 s are 1.0 s. Before `PL-VM40`, this class accumulated
    them instead, with `elapsed_s += simulation_step_s` at each step. That
    sum reaches 0.9999999999999999. The value depends on the order and number
    of the additions, not on how far the run has gone. The gap is
    nanoseconds, and nothing displayed can show it. What it costs is the
    element-wise comparison of one run against another, which a replayed or
    forked run depends on.

    The test uses the literal step that the interface ships rather than
    `MAXIMUM_SIMULATION_STEP_S`, because the arithmetic asserted here belongs
    to that step: at any other step, 10 steps do not make 1.0 s.
    """

    state = SimulationState()

    for _ in range(10):
        state.advance(SimulationStep(0.1))

    assert state.step_count == 10
    assert state.elapsed_s == 1.0


def test_elapsed_time_holds_where_an_accumulated_sum_has_drifted() -> None:
    """Compare one minute of stepping with the sum that the old formulation reached.

    The comparison is the point. The sum is what this class would report
    after the same 600 steps, and it is not 60 s. The state is constructed
    at the count rather than stepped 600 times, because the claim is about
    the arithmetic and not about the model.
    """

    accumulated_s = 0.0

    for _ in range(600):
        accumulated_s += 0.1

    state = SimulationState(step_count=StepCount(600), simulation_step_s=SimulationStep(0.1))

    assert state.elapsed_s == 60.0
    assert accumulated_s != 60.0


def test_a_run_keeps_the_step_it_started_at() -> None:
    """A second step size would make the recorded history non-uniform.

    The change is refused rather than accommodated. `elapsed_s` has one step
    to multiply by, and every reader that maps a sample index to a time
    treats the spacing as a constant of the run.
    """

    state = SimulationState()
    state.advance(SimulationStep(0.1))

    with pytest.raises(SimulationConfigurationError, match="cannot switch"):
        state.advance(SimulationStep(0.05))

    assert state.step_count == 1
    assert state.elapsed_s == 0.1


def test_reset_frees_the_step_so_a_fresh_run_may_take_a_different_one() -> None:
    state = SimulationState()
    state.advance(SimulationStep(0.1))

    state.reset()

    assert state.step_count == 0
    assert state.simulation_step_s is None
    assert state.elapsed_s == 0.0

    state.advance(SimulationStep(0.05))

    assert state.elapsed_s == 0.05


def test_a_run_reset_to_a_new_step_matches_a_fresh_run_at_that_step() -> None:
    """A reset run that takes a new step must reach the same state as a fresh run.

    This is the route that `advance()`'s own refusal recommends: "reset it to
    run at a different step". `reset()` clears the compartments but leaves
    the uptake system's cached propagator in place. The run is therefore
    correct only while the cache key includes the step. If the step were left
    out of the key, the reset run would take each 0.05 s step with the 0.1 s
    propagator. It would then report 1.0 s of elapsed time for 2.0 s of
    physics, with an alveolar fraction 3.9 times the fresh run's, and the
    accounting check would still pass (`PL-4H4T`).

    The expected state is a fresh run built at the new step, which never held
    another step's propagator. Both runs start from empty compartments with
    the same settings and take the same steps, so they must agree exactly.
    """

    reset_run = SimulationState()

    for _ in range(10):
        reset_run.advance(SimulationStep(0.1))

    reset_run.reset()
    fresh_run = SimulationState()

    for _ in range(20):
        reset_run.advance(SimulationStep(0.05))
        fresh_run.advance(SimulationStep(0.05))

    assert reset_run.elapsed_s == fresh_run.elapsed_s == 1.0
    assert reset_run.uptake_system.capture_state() == fresh_run.uptake_system.capture_state()


def test_a_count_that_is_not_whole_and_nonnegative_cannot_be_built() -> None:
    """A bad count is refused when it is built, before any state holds it (`PL-CN5S`).

    A count below zero would be a time before the run began, so it is
    refused as an invalid setting is. A count that is not whole lands on a
    time that no sequence of steps reaches. `True` is an `int` to Python but
    is not a count of anything. Since `PL-LLMN`, both of these are refused as
    the programming errors they are. They raise a `TypeError` whose wording
    `tests/unit/test_supported_ranges.py` pins.
    """

    with pytest.raises(SimulationConfigurationError, match="whole, nonnegative number of steps"):
        StepCount(-1)

    for not_a_count in (2.5, True):
        with pytest.raises(TypeError, match="not int"):
            StepCount(not_a_count)  # type: ignore[arg-type]


@pytest.mark.parametrize("step_count", [0, 10, -1])
def test_a_state_refuses_a_count_not_built_as_a_step_count(step_count: int) -> None:
    """A plain integer is refused whatever its value, because nothing has checked it (`PL-CN5S`)."""

    with pytest.raises(TypeError, match="step_count of .* was not built as StepCount"):
        SimulationState(step_count=step_count)  # type: ignore[arg-type]


def test_a_state_keeps_the_checked_types_through_every_move() -> None:
    """`advance` and `reset` store a `StepCount`, and `elapsed_s` is a `CaseInstant`.

    Arithmetic on either type returns a plain number. A count one step on,
    or the product that gives the clock, therefore carries no proof of a
    check until the state builds it as the type again. A run that stored the
    plain number would hand an unchecked value to every reader of the state
    (`PL-CN5S`).
    """

    state = SimulationState()

    assert type(state.elapsed_s) is CaseInstant

    state.advance(SimulationStep(0.1))

    assert type(state.step_count) is StepCount
    assert type(state.elapsed_s) is CaseInstant

    state.reset()

    assert type(state.step_count) is StepCount
    assert type(state.elapsed_s) is CaseInstant


def test_rejects_a_step_count_with_no_step_to_multiply_it_by() -> None:
    """A state part-way through a run has to say what step it took."""

    with pytest.raises(SimulationConfigurationError, match="simulation_step_s"):
        SimulationState(step_count=StepCount(10))


def test_rejects_an_initial_step_above_the_largest_supported_one() -> None:
    """The step that a state is constructed with must meet the same bound.

    Otherwise a state could be built at a step that `advance()` would
    refuse, and every later step would be checked against that step.
    """

    with pytest.raises(SimulationConfigurationError, match="largest supported step"):
        SimulationState(
            step_count=StepCount(1),
            simulation_step_s=SimulationStep(MAXIMUM_SIMULATION_STEP_S * 10.0),
        )


@pytest.mark.parametrize("simulation_step_s", [5e-324, 4e-304, 1e-12])
def test_rejects_an_initial_step_below_the_smallest_supported_one(simulation_step_s: float) -> None:
    """Reject the state in which PL-YZ17 was found, and steps between it and the minimum.

    `SimulationState(step_count=0, simulation_step_s=5e-324)` raised
    `OverflowError` from `maximum_step_count`, as did every step below about
    4.8e-304 s. A state at 1e-12 s could be built. At that step, a day is
    more steps than a float can count exactly, so `elapsed_s` would round
    the count before multiplying it. The step's own guard now refuses all
    three, before any run length is read from the step.
    """

    with pytest.raises(SimulationConfigurationError, match="smallest supported step"):
        SimulationState(
            step_count=StepCount(0), simulation_step_s=SimulationStep(simulation_step_s)
        )


# --- The supported run length (PL-Y5WR) -------------------------------------
#
# `core/supported_ranges.py` owns the number and the refusal. These tests
# check that the limit is enforced *here*, the only place where a run length
# exists. They start at the boundary rather than running up to it, because
# 864 000 steps is a real run but an unusable test. So each state is
# constructed part-way through a run and stepped across the edge.
# `SimulationState` supports that construction explicitly.


def test_a_run_may_be_advanced_up_to_the_supported_run_length() -> None:
    """The last supported step completes and lands on the declared boundary."""

    state = SimulationState(
        step_count=StepCount(maximum_step_count(MAXIMUM_SIMULATION_STEP_S) - 1),
        simulation_step_s=SimulationStep(MAXIMUM_SIMULATION_STEP_S),
    )

    state.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert state.step_count == maximum_step_count(MAXIMUM_SIMULATION_STEP_S)
    assert state.elapsed_s == MAXIMUM_ELAPSED_SIMULATION_TIME_S


def test_the_step_past_the_supported_run_length_is_refused() -> None:
    """Beyond the boundary the model is not claimed to represent a patient."""

    state = SimulationState(
        step_count=StepCount(maximum_step_count(MAXIMUM_SIMULATION_STEP_S)),
        simulation_step_s=SimulationStep(MAXIMUM_SIMULATION_STEP_S),
    )

    with pytest.raises(SimulationDomainLimitError, match="supported run length"):
        state.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))


def test_a_refused_step_leaves_the_run_exactly_where_it_was() -> None:
    """The step is refused before anything advances, so the run can still be read.

    The interface depends on this property. A run stopped at the limit
    displays a completed step at a simulated time inside the supported span,
    not a partial step and not an extrapolated one. The test compares the
    compartment state as well as the clock. A step that ran and was then
    rejected would leave the clock unchanged and the compartments moved.
    """

    state = SimulationState(
        step_count=StepCount(maximum_step_count(MAXIMUM_SIMULATION_STEP_S)),
        simulation_step_s=SimulationStep(MAXIMUM_SIMULATION_STEP_S),
    )
    stored_before = state.uptake_system.total_stored_agent_l
    alveolar_before = state.uptake_system.alveoli.partial_pressure_fraction

    with pytest.raises(SimulationDomainLimitError):
        state.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert state.step_count == maximum_step_count(MAXIMUM_SIMULATION_STEP_S)
    assert state.elapsed_s == MAXIMUM_ELAPSED_SIMULATION_TIME_S
    assert state.uptake_system.total_stored_agent_l == stored_before
    assert state.uptake_system.alveoli.partial_pressure_fraction == alveolar_before


def test_reset_returns_a_run_stopped_at_the_limit_to_a_startable_one() -> None:
    """Reset is the way out, and it has to actually clear the count."""

    state = SimulationState(
        step_count=StepCount(maximum_step_count(MAXIMUM_SIMULATION_STEP_S)),
        simulation_step_s=SimulationStep(MAXIMUM_SIMULATION_STEP_S),
    )

    state.reset()
    state.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert state.step_count == 1


# --- Built part-way through a run (PL-BMY5) ----------------------------------
#
# A branch is built at its parent's step count. So construction is where a run
# is handed a point on the span, rather than reaching that point by stepping.
# The limit is a whole number of steps of whatever size the run takes. So the
# tests use the shipped step, a step that does not divide 24 hours evenly
# (0.07 s), and one that does (0.025 s). They also use the two computed steps
# whose quotient gave the wrong number of steps before `PL-8H2R`. At
# 0.07680000000000001 s it gave one step too many, which ended at
# 86400.00000000001 s. At 0.02304 s it gave one step too few.

STEPS_A_RUN_MAY_TAKE_S = (MAXIMUM_SIMULATION_STEP_S, 0.07, 0.025, 768 / 1_000_000 * 100, 0.02304)


@pytest.mark.parametrize("simulation_step_s", STEPS_A_RUN_MAY_TAKE_S)
def test_a_state_may_be_built_standing_on_the_supported_run_length(
    simulation_step_s: float,
) -> None:
    """A run may stop on the last supported count, so a state may be built at that count.

    Refusing it would refuse a branch taken where its parent stopped at the
    limit. Only the next step from that count is refused, by `advance()`.
    """

    state = SimulationState(
        step_count=StepCount(maximum_step_count(simulation_step_s)),
        simulation_step_s=SimulationStep(simulation_step_s),
    )

    assert state.elapsed_s <= MAXIMUM_ELAPSED_SIMULATION_TIME_S

    with pytest.raises(SimulationDomainLimitError):
        state.advance(SimulationStep(simulation_step_s))


@pytest.mark.parametrize("simulation_step_s", STEPS_A_RUN_MAY_TAKE_S)
def test_a_state_past_the_supported_run_length_is_refused_at_construction(
    simulation_step_s: float,
) -> None:
    """One count past the limit is refused where it is built, not by its first advance.

    The error is a configuration error rather than the domain limit. The
    count handed in is what is wrong, because no run reaches it by stepping.
    """

    with pytest.raises(SimulationConfigurationError, match="supported run length"):
        SimulationState(
            step_count=StepCount(maximum_step_count(simulation_step_s) + 1),
            simulation_step_s=SimulationStep(simulation_step_s),
        )


def test_the_state_measured_past_the_limit_is_refused() -> None:
    """The regression case is 1 000 000 steps of 0.1 s, which is 27.8 hours.

    On 2026-09-14 this state was measured being constructed without complaint
    and reporting an `elapsed_s` of 100 000 s. Every reader of the state,
    such as a snapshot, a readout or a chart axis, would have presented it as
    an ordinary run until something tried to step it. The test writes the
    count as its distance past the limit, 136 000 steps. That is the measured
    state while the limit is 24 hours, and it stays past the limit wherever
    the limit is set.
    """

    step_count = maximum_step_count(0.1) + 136_000

    with pytest.raises(SimulationConfigurationError, match="supported run length"):
        SimulationState(step_count=StepCount(step_count), simulation_step_s=SimulationStep(0.1))


# --- Written onto a built state (PL-8W1W) --------------------------------------
#
# Nothing in `src/` writes either field outside `advance` and `reset`, and
# `mypy --strict` refuses such an assignment there. Only a caller that `mypy`
# does not check can make the write. The write must pass the same checks that
# the constructor applies.


def test_a_count_or_a_step_written_onto_a_built_state_is_refused_at_the_write() -> None:
    """The run's clock moves only to a count and a step the simulator checked (`PL-8W1W`).

    Until `PL-8W1W`, only the constructor checked the pair. A fresh state
    accepted a bare count of 5 and read 0 s. One step on from there, it
    accepted a bare float step of 0.5 s and read 3.0 s for a system advanced
    0.1 s. A count of -3 was refused only when `elapsed_s` was next read, as
    a run-length error naming an instant nobody handed in. The state's
    `__setattr__` now runs the constructor's checks at the write, with the
    constructor's messages. When it refuses, the field keeps its old value.
    Each refusal below is therefore the one that the constructor gives for
    the same pair. A checked count inside the run length is accepted
    whoever writes it. Beyond the types, the write checks only the pair, so
    keeping one step size per run is still `advance`'s own refusal.
    `dataclasses.replace`, a copy and a pickle all write through the same
    path. The copy and the pickle do so because the state is a `slots=True`
    dataclass, whose state is restored one field at a time.
    """

    state = SimulationState()
    fresh_count = state.step_count

    with pytest.raises(TypeError, match="step_count of 5 was not built as StepCount"):
        state.step_count = 5  # type: ignore[assignment]

    assert state.step_count is fresh_count
    assert state.elapsed_s == 0.0

    with pytest.raises(SimulationConfigurationError, match="no simulation_step_s"):
        state.step_count = StepCount(5)

    assert state.step_count is fresh_count
    assert state.elapsed_s == 0.0

    state.advance(SimulationStep(0.1))
    held_count = state.step_count
    held_step = state.simulation_step_s

    with pytest.raises(TypeError, match="simulation_step_s of 0.5 was not built as SimulationStep"):
        state.simulation_step_s = 0.5  # type: ignore[assignment]

    assert state.simulation_step_s is held_step
    assert state.elapsed_s == 0.1

    with pytest.raises(TypeError, match="step_count of -3 was not built as StepCount"):
        state.step_count = -3  # type: ignore[assignment]

    assert state.step_count is held_count
    assert state.elapsed_s == 0.1

    with pytest.raises(SimulationConfigurationError, match="no simulation_step_s"):
        state.simulation_step_s = None

    assert state.simulation_step_s is held_step

    with pytest.raises(SimulationConfigurationError, match="supported run length"):
        state.step_count = StepCount(maximum_step_count(SimulationStep(0.1)) + 1)

    assert state.step_count is held_count
    assert state.elapsed_s == 0.1

    standing_at_the_limit = SimulationState(
        step_count=StepCount(maximum_step_count(SimulationStep(0.025))),
        simulation_step_s=SimulationStep(0.025),
    )

    with pytest.raises(SimulationConfigurationError, match="supported run length"):
        standing_at_the_limit.simulation_step_s = SimulationStep(0.1)

    assert standing_at_the_limit.simulation_step_s == 0.025
    assert standing_at_the_limit.elapsed_s == MAXIMUM_ELAPSED_SIMULATION_TIME_S

    state.step_count = StepCount(2)

    assert state.elapsed_s == 0.2

    state.advance(SimulationStep(0.1))

    assert state.step_count == 3

    state.reset()

    assert state.step_count == 0
    assert state.simulation_step_s is None

    with pytest.raises(TypeError, match="step_count of 5 was not built as StepCount"):
        replace(state, step_count=5)  # type: ignore[arg-type]

    smuggled = copy.copy(state)
    object.__setattr__(smuggled, "step_count", 5)

    with pytest.raises(TypeError, match="step_count of 5 was not built as StepCount"):
        copy.copy(smuggled)

    with pytest.raises(TypeError, match="step_count of 5 was not built as StepCount"):
        pickle.loads(pickle.dumps(smuggled))
