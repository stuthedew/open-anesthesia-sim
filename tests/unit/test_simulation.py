import pytest

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.respiratory_system import RespiratorySystem
from anesthesia_sim.core.simulation import SimulationState


def test_advance_updates_time_and_complete_respiratory_system() -> None:
    state = SimulationState()

    state.advance(2.5)

    assert state.elapsed_s == pytest.approx(2.5)
    assert state.circuit.circuit_concentration_fraction > 0.0
    assert state.alveoli.concentration_fraction > 0.0
    assert state.patient.total_agent_amount_l > 0.0
    assert state.respiratory_system.agent_simulation_validation.passes_validation


def test_reset_preserves_settings_and_clears_dynamic_state() -> None:
    system = RespiratorySystem.default()
    system.circuit.set_circuit_volume(5.0)
    system.set_fresh_gas_flow(3.0)
    system.set_delivered_concentration(0.06)
    system.set_alveolar_ventilation(5.5)
    system.set_cardiac_output(6.0)

    state = SimulationState(respiratory_system=system)
    state.advance(10.0)

    state.reset()

    assert state.elapsed_s == 0.0
    assert state.circuit.circuit_concentration_fraction == 0.0
    assert state.alveoli.concentration_fraction == 0.0
    assert state.patient.total_agent_amount_l == 0.0

    assert state.circuit.circuit_volume_l == 5.0
    assert state.circuit.fresh_gas_flow_l_min == 3.0
    assert state.circuit.delivered_concentration_fraction == 0.06
    assert state.alveoli.alveolar_ventilation_l_min == 5.5
    assert state.patient.cardiac_output_l_min == 6.0


@pytest.mark.parametrize("simulation_step_s", [0.0, -0.1, float("nan")])
def test_rejects_invalid_simulation_step(simulation_step_s: float) -> None:
    with pytest.raises(SimulationConfigurationError):
        SimulationState().advance(simulation_step_s)


@pytest.mark.parametrize("elapsed_s", [-0.1, float("nan")])
def test_rejects_invalid_initial_elapsed_time(elapsed_s: float) -> None:
    with pytest.raises(SimulationConfigurationError):
        SimulationState(elapsed_s=elapsed_s)
