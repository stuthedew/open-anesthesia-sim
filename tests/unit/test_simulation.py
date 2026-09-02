import pytest

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.uptake_system import MAXIMUM_SIMULATION_STEP_S, AgentUptakeSystem


def _advance_for(state: SimulationState, duration_s: float) -> None:
    """Advance to `duration_s` at the largest supported step.

    Simulated time is reached by taking supported steps rather than by
    asking for one large one: `MAXIMUM_SIMULATION_STEP_S` is the operator
    split's applicability domain, and a caller that wants 10 s of simulated
    time steps 100 times rather than once.
    """

    for _ in range(round(duration_s / MAXIMUM_SIMULATION_STEP_S)):
        state.advance(MAXIMUM_SIMULATION_STEP_S)


def test_advance_updates_time_and_complete_uptake_system() -> None:
    state = SimulationState()

    _advance_for(state, duration_s=2.5)

    assert state.elapsed_s == pytest.approx(2.5)
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

    with pytest.raises(SimulationConfigurationError, match="applicability domain"):
        state.advance(MAXIMUM_SIMULATION_STEP_S * 10.0)

    assert state.elapsed_s == before_s


@pytest.mark.parametrize("elapsed_s", [-0.1, float("nan")])
def test_rejects_invalid_initial_elapsed_time(elapsed_s: float) -> None:
    with pytest.raises(SimulationConfigurationError):
        SimulationState(elapsed_s=elapsed_s)
