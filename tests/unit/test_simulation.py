import copy
import pickle
from dataclasses import replace

import pytest

from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError, SimulationDomainLimitError
from anesthesia_sim.core.numerical_envelope import CompartmentVolume
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    MAXIMUM_STEP_COUNT,
    AlveolarVentilation,
    CardiacOutput,
    CaseInstant,
    FreshGasFlow,
    StepCount,
)
from anesthesia_sim.core.uptake_system import AgentUptakeSystem


def _advance_for(state: SimulationState, duration_s: int) -> None:
    """Advance the state by `duration_s`, a whole number of seconds, one step at a time.

    A simulated time is reached by taking the run's one step, not by asking
    for one large step. `SIMULATION_STEP_S` is the interval over which the
    settings are held constant. A caller that wants 10 s of simulated time
    takes 10 steps rather than one.
    """

    for _ in range(duration_s // SIMULATION_STEP_S):
        state.advance()


def test_advance_updates_time_and_complete_uptake_system() -> None:
    state = SimulationState()

    _advance_for(state, duration_s=3)

    assert state.elapsed_s == 3
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
    _advance_for(state, duration_s=10)

    state.reset()

    assert state.elapsed_s == 0
    assert state.uptake_system.circuit.inspired_partial_pressure_fraction == 0.0
    assert state.uptake_system.alveoli.partial_pressure_fraction == 0.0
    assert state.uptake_system.patient.total_agent_amount_l == 0.0

    assert state.uptake_system.circuit.circuit_volume_l == 5.0
    assert state.uptake_system.circuit.fresh_gas_flow_l_min == 3.0
    assert state.uptake_system.circuit.delivered_concentration_percent == 6.0
    assert state.uptake_system.alveoli.alveolar_ventilation_l_min == 5.5
    assert state.uptake_system.patient.cardiac_output_l_min == 6.0


def test_a_run_cannot_be_asked_for_a_step_of_another_length() -> None:
    """`advance` takes no step, and a state has no step to write, so every step is one second.

    Until `PL-SZ6G` a caller chose the step, and the state refused a step
    outside the supported range and a second step of a different length. Now
    a caller cannot hand in a step at all. Elapsed time must not move for a
    step that was never simulated. `SimulationState` is the class that owns
    simulated time. So without the refusal, a caller that caught and ignored
    the exception and then read `elapsed_s` would be told that the run had
    advanced by a step for which nothing was calculated.
    """

    state = SimulationState()
    state.advance()
    stored_before = state.uptake_system.capture_state()

    with pytest.raises(TypeError, match="advance"):
        state.advance(0.5)  # type: ignore[call-arg]

    with pytest.raises(AttributeError, match="simulation_step_s"):
        state.simulation_step_s = 0.5  # type: ignore[attr-defined]

    assert state.step_count == 1
    assert state.elapsed_s == 1
    assert state.uptake_system.capture_state() == stored_before


def test_elapsed_time_is_the_count_of_steps_in_whole_seconds() -> None:
    """Simulated time is the number of steps taken, and each step is one second.

    Ten steps are 10 s, as a whole number. Before `PL-VM40`, this class added
    the step to a running total at each step. The step was then 0.1 s, and ten
    of those additions reach 0.9999999999999999, not 1.0. Such a total depends
    on the order and number of the additions, not on how far the run has gone.
    The gap was nanoseconds, and nothing displayed could show it. What it cost
    was the element-wise comparison of one run against another, which a
    replayed or forked run depends on. The expected time here is the count of
    steps that the test itself takes.
    """

    state = SimulationState()

    for _ in range(10):
        state.advance()

    assert state.step_count == 10
    assert state.elapsed_s == 10
    assert isinstance(state.elapsed_s, int)


def test_a_state_built_part_way_through_a_run_reads_its_count_as_seconds() -> None:
    """A state built at a count of 600 steps stands at 600 s, which is ten minutes.

    The state is constructed at the count rather than stepped 600 times,
    because the claim is about the clock and not about the model. Until
    `PL-SZ6G` such a state also had to say what step it took, and its time
    was the count times that step, a rounded product. It now needs only the
    count.
    """

    state = SimulationState(step_count=StepCount(600))

    assert state.elapsed_s == 600
    assert type(state.elapsed_s) is CaseInstant


def test_reset_returns_the_clock_to_zero_and_the_run_can_be_stepped_again() -> None:
    state = SimulationState()
    state.advance()

    state.reset()

    assert state.step_count == 0
    assert state.elapsed_s == 0

    state.advance()

    assert state.elapsed_s == 1


def test_a_reset_run_matches_a_fresh_run() -> None:
    """A reset run must reach the same state as a fresh run that takes the same steps.

    `reset()` clears the compartments but leaves the uptake system's cached
    propagator in place. So the reset run takes its steps with the propagator
    that it built before the reset, and the fresh run builds its own.

    The expected state is a fresh run, which was never reset. Both runs start
    from empty compartments with the same settings and take the same steps,
    so they must agree exactly.
    """

    reset_run = SimulationState()

    for _ in range(10):
        reset_run.advance()

    reset_run.reset()
    fresh_run = SimulationState()

    for _ in range(20):
        reset_run.advance()
        fresh_run.advance()

    assert reset_run.elapsed_s == fresh_run.elapsed_s == 20
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

    state.advance()

    assert type(state.step_count) is StepCount
    assert type(state.elapsed_s) is CaseInstant

    state.reset()

    assert type(state.step_count) is StepCount
    assert type(state.elapsed_s) is CaseInstant


# --- The supported run length (PL-Y5WR) -------------------------------------
#
# `core/supported_ranges.py` owns the number and the refusal. These tests
# check that the limit is enforced *here*, the only place where a run length
# exists. They start at the boundary rather than running up to it, because
# 86 400 steps is a real run but an unusable test. So each state is
# constructed part-way through a run and stepped across the edge.
# `SimulationState` supports that construction explicitly.


def test_a_run_may_be_advanced_up_to_the_supported_run_length() -> None:
    """The last supported step completes and lands on the declared boundary."""

    state = SimulationState(step_count=StepCount(MAXIMUM_STEP_COUNT - 1))

    state.advance()

    assert state.step_count == MAXIMUM_STEP_COUNT
    assert state.elapsed_s == MAXIMUM_ELAPSED_SIMULATION_TIME_S


def test_the_step_past_the_supported_run_length_is_refused() -> None:
    """Beyond the boundary the model is not claimed to represent a patient."""

    state = SimulationState(step_count=StepCount(MAXIMUM_STEP_COUNT))

    with pytest.raises(SimulationDomainLimitError, match="supported run length"):
        state.advance()


def test_a_refused_step_leaves_the_run_exactly_where_it_was() -> None:
    """The step is refused before anything advances, so the run can still be read.

    The interface depends on this property. A run stopped at the limit
    displays a completed step at a simulated time inside the supported span,
    not a partial step and not an extrapolated one. The test compares the
    compartment state as well as the clock. A step that ran and was then
    rejected would leave the clock unchanged and the compartments moved.
    """

    state = SimulationState(step_count=StepCount(MAXIMUM_STEP_COUNT))
    stored_before = state.uptake_system.total_stored_agent_l
    alveolar_before = state.uptake_system.alveoli.partial_pressure_fraction

    with pytest.raises(SimulationDomainLimitError):
        state.advance()

    assert state.step_count == MAXIMUM_STEP_COUNT
    assert state.elapsed_s == MAXIMUM_ELAPSED_SIMULATION_TIME_S
    assert state.uptake_system.total_stored_agent_l == stored_before
    assert state.uptake_system.alveoli.partial_pressure_fraction == alveolar_before


def test_reset_returns_a_run_stopped_at_the_limit_to_a_startable_one() -> None:
    """Reset is the way out, and it has to actually clear the count."""

    state = SimulationState(step_count=StepCount(MAXIMUM_STEP_COUNT))

    state.reset()
    state.advance()

    assert state.step_count == 1


# --- Built part-way through a run (PL-BMY5) ----------------------------------
#
# A branch is built at its parent's step count. So construction is where a run
# is handed a point on the span, rather than reaching that point by stepping.
# The limit is `MAXIMUM_STEP_COUNT` steps of one second, which is the supported
# run length exactly.


def test_a_state_may_be_built_standing_on_the_supported_run_length() -> None:
    """A run may stop on the last supported count, so a state may be built at that count.

    Refusing it would refuse a branch taken where its parent stopped at the
    limit. Only the next step from that count is refused, by `advance()`.
    """

    state = SimulationState(step_count=StepCount(MAXIMUM_STEP_COUNT))

    assert state.elapsed_s == MAXIMUM_ELAPSED_SIMULATION_TIME_S

    with pytest.raises(SimulationDomainLimitError):
        state.advance()


def test_a_state_past_the_supported_run_length_is_refused_at_construction() -> None:
    """One count past the limit is refused where it is built, not by its first advance.

    The error is a configuration error rather than the domain limit. The
    count handed in is what is wrong, because no run reaches it by stepping.
    """

    with pytest.raises(SimulationConfigurationError, match="supported run length"):
        SimulationState(step_count=StepCount(MAXIMUM_STEP_COUNT + 1))


def test_the_state_measured_past_the_limit_is_refused() -> None:
    """The regression case is a state standing at 100 000 s, which is 27.8 hours.

    On 2026-09-14 this state was measured being constructed without complaint
    and reporting an `elapsed_s` of 100 000 s. It was then 1 000 000 steps of
    0.1 s, and it is now 100 000 steps of one second. Every reader of the
    state, such as a snapshot, a readout or a chart axis, would have presented
    it as an ordinary run until something tried to step it. The test writes
    the count as its distance past the limit, 13 600 steps. That is the
    measured state while the limit is 24 hours, and it stays past the limit
    wherever the limit is set.
    """

    step_count = MAXIMUM_STEP_COUNT + 13_600

    with pytest.raises(SimulationConfigurationError, match="supported run length"):
        SimulationState(step_count=StepCount(step_count))


# --- Written onto a built state (PL-8W1W) --------------------------------------
#
# Nothing in `src/` writes the count outside `advance` and `reset`, and
# `mypy --strict` refuses such an assignment there. Only a caller that `mypy`
# does not check can make the write. The write must pass the same checks that
# the constructor applies.


def test_a_count_written_onto_a_built_state_is_refused_at_the_write() -> None:
    """The run's clock moves only to a count that the simulator checked (`PL-8W1W`).

    Until `PL-8W1W`, only the constructor checked the count. A fresh state
    accepted a bare count of 5 that was not built as a `StepCount`, and a
    bare count of -3 after it. The state's `__setattr__` now runs the
    constructor's checks at the write, with the constructor's messages. When
    it refuses, the field keeps its old value. Each refusal below is
    therefore the one that the constructor gives for the same count. A
    checked count inside the run length is accepted whoever writes it.
    `dataclasses.replace`, a copy and a pickle all write through the same
    path. The copy and the pickle do so because the state is a `slots=True`
    dataclass, whose state is restored one field at a time.
    """

    state = SimulationState()
    fresh_count = state.step_count

    with pytest.raises(TypeError, match="step_count of 5 was not built as StepCount"):
        state.step_count = 5  # type: ignore[assignment]

    assert state.step_count is fresh_count
    assert state.elapsed_s == 0

    state.advance()
    held_count = state.step_count

    with pytest.raises(TypeError, match="step_count of -3 was not built as StepCount"):
        state.step_count = -3  # type: ignore[assignment]

    assert state.step_count is held_count
    assert state.elapsed_s == 1

    with pytest.raises(SimulationConfigurationError, match="supported run length"):
        state.step_count = StepCount(MAXIMUM_STEP_COUNT + 1)

    assert state.step_count is held_count
    assert state.elapsed_s == 1

    state.step_count = StepCount(2)

    assert state.elapsed_s == 2

    state.advance()

    assert state.step_count == 3

    state.reset()

    assert state.step_count == 0

    with pytest.raises(TypeError, match="step_count of 5 was not built as StepCount"):
        replace(state, step_count=5)  # type: ignore[arg-type]

    smuggled = copy.copy(state)
    object.__setattr__(smuggled, "step_count", 5)

    with pytest.raises(TypeError, match="step_count of 5 was not built as StepCount"):
        copy.copy(smuggled)

    with pytest.raises(TypeError, match="step_count of 5 was not built as StepCount"):
        pickle.loads(pickle.dumps(smuggled))
