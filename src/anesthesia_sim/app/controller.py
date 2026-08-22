from dataclasses import dataclass

from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.simulation import SimulationState


@dataclass(frozen=True, slots=True)
class SimulationSnapshot:
    """Read-only simulation data exposed to the user interface."""

    is_running: bool
    elapsed_s: float
    circuit_volume_l: float
    fresh_gas_flow_l_min: float
    delivered_concentration_fraction: float
    circuit_concentration_fraction: float
    circuit_time_constant_s: float
    concentration_history: tuple[tuple[float, float], ...]


class SimulationController:
    """Own run controls and concentration history for one app session."""

    def __init__(
        self,
        circuit_volume_l: float = 6.0,
        fresh_gas_flow_l_min: float = 4.0,
        delivered_concentration_fraction: float = 0.08,
    ) -> None:
        circuit = BreathingCircuit(
            circuit_volume_l=circuit_volume_l,
            fresh_gas_flow_l_min=fresh_gas_flow_l_min,
            delivered_concentration_fraction=(delivered_concentration_fraction),
        )
        self._state = SimulationState(circuit=circuit)
        self._is_running = False
        self._concentration_history: list[tuple[float, float]] = [(0.0, 0.0)]

    @property
    def is_running(self) -> bool:
        return self._is_running

    def snapshot(self) -> SimulationSnapshot:
        circuit = self._state.circuit

        return SimulationSnapshot(
            is_running=self._is_running,
            elapsed_s=self._state.elapsed_s,
            circuit_volume_l=circuit.circuit_volume_l,
            fresh_gas_flow_l_min=circuit.fresh_gas_flow_l_min,
            delivered_concentration_fraction=(circuit.delivered_concentration_fraction),
            circuit_concentration_fraction=(circuit.circuit_concentration_fraction),
            circuit_time_constant_s=circuit.time_constant_s,
            concentration_history=tuple(self._concentration_history),
        )

    def start(self) -> None:
        self._is_running = True

    def pause(self) -> None:
        self._is_running = False

    def reset(self) -> None:
        self.pause()
        self._state.reset()
        self._concentration_history = [(0.0, 0.0)]

    def set_circuit_volume(
        self,
        circuit_volume_l: float,
    ) -> None:
        self._state.circuit.set_circuit_volume(circuit_volume_l)

    def set_fresh_gas_flow(
        self,
        fresh_gas_flow_l_min: float,
    ) -> None:
        self._state.circuit.set_fresh_gas_flow(fresh_gas_flow_l_min)

    def set_delivered_concentration(
        self,
        delivered_concentration_fraction: float,
    ) -> None:
        self._state.circuit.set_delivered_concentration(delivered_concentration_fraction)

    def advance(self, simulation_step_s: float) -> None:
        if not self._is_running:
            return

        self._state.advance(simulation_step_s)
        self._concentration_history.append(
            (
                self._state.elapsed_s,
                self._state.circuit.circuit_concentration_fraction,
            )
        )
