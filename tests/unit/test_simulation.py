import pytest

from anesthesia_sim.core.exceptions import SimulationConfigurationError, SimulationDomainLimitError
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    maximum_step_count,
)
from anesthesia_sim.core.uptake_system import MAXIMUM_SIMULATION_STEP_S, AgentUptakeSystem


def _advance_for(state: SimulationState, duration_s: float) -> None:
    """Advance to `duration_s` at the largest supported step.

    Simulated time is reached by taking supported steps rather than by
    asking for one large one: `MAXIMUM_SIMULATION_STEP_S` is the longest
    interval settings are held constant over, and a caller that wants 10 s of
    simulated time steps 100 times rather than once.
    """

    for _ in range(round(duration_s / MAXIMUM_SIMULATION_STEP_S)):
        state.advance(MAXIMUM_SIMULATION_STEP_S)


def test_advance_updates_time_and_complete_uptake_system() -> None:
    state = SimulationState()

    _advance_for(state, duration_s=2.5)

    assert state.elapsed_s == 2.5
    assert state.uptake_system.circuit.circuit_concentration_fraction > 0.0
    assert state.uptake_system.alveoli.concentration_fraction > 0.0
    assert state.uptake_system.patient.total_agent_amount_l > 0.0
    assert state.uptake_system.agent_simulation_validation.passes_validation


def test_reset_preserves_settings_and_clears_dynamic_state() -> None:
    system = AgentUptakeSystem.default()
    system.circuit.set_circuit_volume(5.0)
    system.set_fresh_gas_flow(3.0)
    system.set_delivered_concentration(0.06)
    system.set_alveolar_ventilation(5.5)
    system.set_cardiac_output(6.0)

    state = SimulationState(uptake_system=system)
    _advance_for(state, duration_s=10.0)

    state.reset()

    assert state.elapsed_s == 0.0
    assert state.uptake_system.circuit.circuit_concentration_fraction == 0.0
    assert state.uptake_system.alveoli.concentration_fraction == 0.0
    assert state.uptake_system.patient.total_agent_amount_l == 0.0

    assert state.uptake_system.circuit.circuit_volume_l == 5.0
    assert state.uptake_system.circuit.fresh_gas_flow_l_min == 3.0
    assert state.uptake_system.circuit.delivered_concentration_fraction == 0.06
    assert state.uptake_system.alveoli.alveolar_ventilation_l_min == 5.5
    assert state.uptake_system.patient.cardiac_output_l_min == 6.0


@pytest.mark.parametrize("simulation_step_s", [0.0, -0.1, float("nan")])
def test_rejects_invalid_simulation_step(simulation_step_s: float) -> None:
    with pytest.raises(SimulationConfigurationError):
        SimulationState().advance(simulation_step_s)


def test_rejects_a_step_above_the_maximum_simulation_step() -> None:
    """Elapsed time must not move for a step that was never simulated.

    `SimulationState` is the class that owns simulated time, so this is the
    one place the refusal has a consequence beyond the uptake system:
    a caller that swallowed the raise and read `elapsed_s` would otherwise
    be told the run had advanced by a step nothing was calculated for.
    """

    state = SimulationState()
    state.advance(MAXIMUM_SIMULATION_STEP_S)
    before_s = state.elapsed_s

    with pytest.raises(SimulationConfigurationError, match="largest supported step"):
        state.advance(MAXIMUM_SIMULATION_STEP_S * 10.0)

    assert state.elapsed_s == before_s


def test_elapsed_time_is_the_step_count_times_the_step() -> None:
    """Simulated time is a function of the steps taken, not of the additions.

    Ten steps of 0.1 s are 1.0 s. Accumulating them instead - `elapsed_s +=
    simulation_step_s` per step, which this class did before `PL-VM40` -
    reaches 0.9999999999999999, a value set by the order and number of the
    additions that produced it rather than by how far the run has gone. The
    gap is nanoseconds and nothing displayed can show it; what it costs is
    the element-wise comparison of one run against another that a replayed
    or forked run rests on.

    Written with the literal step the interface ships rather than with
    `MAXIMUM_SIMULATION_STEP_S`, because the arithmetic asserted here is
    that step's: at any other step, 10 of them are not 1.0 s.
    """

    state = SimulationState()

    for _ in range(10):
        state.advance(0.1)

    assert state.step_count == 10
    assert state.elapsed_s == 1.0


def test_elapsed_time_holds_where_an_accumulated_sum_has_drifted() -> None:
    """One minute of stepping, against the sum the old formulation reached.

    The comparison is the point: the sum is what this class would report
    after the same 600 steps, and it is not 60 s. Constructed at the count
    rather than stepped 600 times, since the claim is about the arithmetic
    and not about the model.
    """

    accumulated_s = 0.0

    for _ in range(600):
        accumulated_s += 0.1

    state = SimulationState(step_count=600, simulation_step_s=0.1)

    assert state.elapsed_s == 60.0
    assert accumulated_s != 60.0


def test_a_run_keeps_the_step_it_started_at() -> None:
    """A second cadence would make the recorded history non-uniform.

    Refused rather than accommodated: `elapsed_s` has one step to multiply
    by, and every reader that maps a sample index to a time reads the
    spacing as a constant of the run.
    """

    state = SimulationState()
    state.advance(0.1)

    with pytest.raises(SimulationConfigurationError, match="cannot switch"):
        state.advance(0.05)

    assert state.step_count == 1
    assert state.elapsed_s == 0.1


def test_reset_frees_the_step_so_a_fresh_run_may_take_a_different_one() -> None:
    state = SimulationState()
    state.advance(0.1)

    state.reset()

    assert state.step_count == 0
    assert state.simulation_step_s is None
    assert state.elapsed_s == 0.0

    state.advance(0.05)

    assert state.elapsed_s == 0.05


def test_rejects_a_negative_initial_step_count() -> None:
    with pytest.raises(SimulationConfigurationError, match="step_count"):
        SimulationState(step_count=-1)


def test_rejects_a_fractional_initial_step_count() -> None:
    """A count that is not whole reaches a time no sequence of steps does."""

    with pytest.raises(SimulationConfigurationError, match="step_count"):
        SimulationState(step_count=2.5)  # type: ignore[arg-type]


def test_rejects_a_step_count_with_no_step_to_multiply_it_by() -> None:
    """A state part-way through a run has to say what step it took."""

    with pytest.raises(SimulationConfigurationError, match="simulation_step_s"):
        SimulationState(step_count=10)


def test_rejects_an_initial_step_above_the_largest_supported_one() -> None:
    """The step a state is constructed with is held to the same bound.

    Otherwise a state could be built at a step `advance()` would refuse, and
    every step it then took would be measured against it.
    """

    with pytest.raises(SimulationConfigurationError, match="largest supported step"):
        SimulationState(step_count=1, simulation_step_s=MAXIMUM_SIMULATION_STEP_S * 10.0)


# --- The supported run length (PL-Y5WR) -------------------------------------
#
# `core/supported_ranges.py` owns the number and the refusal; these are the
# tests for enforcing it *here*, which is the only place a run length exists.
# They run at the boundary rather than to it: 864 000 steps is a real run and
# an unusable test, so the state is constructed part-way through - which
# `SimulationState` supports explicitly - and stepped across the edge.


def test_a_run_may_be_advanced_up_to_the_supported_run_length() -> None:
    """The last supported step completes and lands on the declared boundary."""

    state = SimulationState(
        step_count=maximum_step_count(MAXIMUM_SIMULATION_STEP_S) - 1,
        simulation_step_s=MAXIMUM_SIMULATION_STEP_S,
    )

    state.advance(MAXIMUM_SIMULATION_STEP_S)

    assert state.step_count == maximum_step_count(MAXIMUM_SIMULATION_STEP_S)
    assert state.elapsed_s == MAXIMUM_ELAPSED_SIMULATION_TIME_S


def test_the_step_past_the_supported_run_length_is_refused() -> None:
    """Beyond the boundary the model is not claimed to represent a patient."""

    state = SimulationState(
        step_count=maximum_step_count(MAXIMUM_SIMULATION_STEP_S),
        simulation_step_s=MAXIMUM_SIMULATION_STEP_S,
    )

    with pytest.raises(SimulationDomainLimitError, match="supported run length"):
        state.advance(MAXIMUM_SIMULATION_STEP_S)


def test_a_refused_step_leaves_the_run_exactly_where_it_was() -> None:
    """Refused before anything advances, so the run is still readable.

    The property the interface rests on: a run stopped at the limit is
    displaying a completed step at a simulated time inside the supported
    span, not a partial one and not an extrapolated one. Compartment state
    is compared as well as the clock, because a step that ran and was then
    rejected would leave the second unchanged and the first moved.
    """

    state = SimulationState(
        step_count=maximum_step_count(MAXIMUM_SIMULATION_STEP_S),
        simulation_step_s=MAXIMUM_SIMULATION_STEP_S,
    )
    stored_before = state.uptake_system.total_stored_agent_l
    alveolar_before = state.uptake_system.alveoli.concentration_fraction

    with pytest.raises(SimulationDomainLimitError):
        state.advance(MAXIMUM_SIMULATION_STEP_S)

    assert state.step_count == maximum_step_count(MAXIMUM_SIMULATION_STEP_S)
    assert state.elapsed_s == MAXIMUM_ELAPSED_SIMULATION_TIME_S
    assert state.uptake_system.total_stored_agent_l == stored_before
    assert state.uptake_system.alveoli.concentration_fraction == alveolar_before


def test_reset_returns_a_run_stopped_at_the_limit_to_a_startable_one() -> None:
    """Reset is the way out, and it has to actually clear the count."""

    state = SimulationState(
        step_count=maximum_step_count(MAXIMUM_SIMULATION_STEP_S),
        simulation_step_s=MAXIMUM_SIMULATION_STEP_S,
    )

    state.reset()
    state.advance(MAXIMUM_SIMULATION_STEP_S)

    assert state.step_count == 1
