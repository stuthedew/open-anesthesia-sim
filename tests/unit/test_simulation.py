import pytest

from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.simulation import SimulationState


def test_advance_updates_time_and_circuit_together() -> None:
    state = SimulationState(circuit=BreathingCircuit(delivered_concentration_fraction=0.08))

    state.advance(2.5)

    assert state.elapsed_s == pytest.approx(2.5)
    assert state.circuit.circuit_concentration_fraction > 0.0


def test_reset_preserves_settings_and_clears_dynamic_state() -> None:
    state = SimulationState(
        circuit=BreathingCircuit(
            circuit_volume_l=5.0,
            fresh_gas_flow_l_min=3.0,
            delivered_concentration_fraction=0.06,
        )
    )
    state.advance(10.0)

    state.reset()

    assert state.elapsed_s == 0.0
    assert state.circuit.circuit_concentration_fraction == 0.0
    assert state.circuit.circuit_volume_l == 5.0
    assert state.circuit.fresh_gas_flow_l_min == 3.0
    assert state.circuit.delivered_concentration_fraction == 0.06


@pytest.mark.parametrize(
    "simulation_step_s",
    [0.0, -0.1, float("nan")],
)
def test_rejects_invalid_simulation_step(
    simulation_step_s: float,
) -> None:
    with pytest.raises(ValueError):
        SimulationState().advance(simulation_step_s)
