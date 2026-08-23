from dataclasses import dataclass

from anesthesia_sim.core.exceptions import (
    SimulationConfigurationError,
)
from anesthesia_sim.core.respiratory_system import RespiratorySystem
from anesthesia_sim.core.simulation import SimulationState


@dataclass(frozen=True, slots=True)
class SimulationHistorySample:
    """Read-only concentrations recorded at one simulation time."""

    elapsed_s: float
    circuit_concentration_fraction: float
    alveolar_concentration_fraction: float
    mixed_venous_concentration_fraction: float
    vessel_rich_partial_pressure_fraction: float
    muscle_partial_pressure_fraction: float
    fat_partial_pressure_fraction: float


@dataclass(frozen=True, slots=True)
class SimulationSnapshot:
    """Read-only simulation data exposed to the user interface."""

    is_running: bool
    elapsed_s: float
    circuit_volume_l: float
    fresh_gas_flow_l_min: float
    delivered_concentration_fraction: float
    alveolar_ventilation_l_min: float
    cardiac_output_l_min: float
    circuit_concentration_fraction: float
    alveolar_concentration_fraction: float
    mixed_venous_concentration_fraction: float
    vessel_rich_partial_pressure_fraction: float
    muscle_partial_pressure_fraction: float
    fat_partial_pressure_fraction: float
    circuit_time_constant_s: float
    delivered_agent_l: float
    exhausted_agent_l: float
    stored_agent_l: float
    unaccounted_agent_l: float
    agent_accounting_absolute_error_l: float
    agent_accounting_passes_validation: bool
    concentration_history: tuple[SimulationHistorySample, ...]


class SimulationController:
    """Own run controls and read-only history for one app session."""

    def __init__(
        self,
        circuit_volume_l: float = 6.0,
        fresh_gas_flow_l_min: float = 4.0,
        delivered_concentration_fraction: float = 0.08,
        alveolar_ventilation_l_min: float = 4.0,
        cardiac_output_l_min: float = 5.0,
    ) -> None:
        respiratory_system = RespiratorySystem.default()
        respiratory_system.circuit.set_circuit_volume(circuit_volume_l)
        respiratory_system.set_fresh_gas_flow(fresh_gas_flow_l_min)
        respiratory_system.set_delivered_concentration(delivered_concentration_fraction)
        respiratory_system.set_alveolar_ventilation(alveolar_ventilation_l_min)
        respiratory_system.set_cardiac_output(cardiac_output_l_min)

        self._state = SimulationState(respiratory_system=respiratory_system)
        self._is_running = False
        self._concentration_history: list[SimulationHistorySample] = [self._build_history_sample()]

    @property
    def is_running(self) -> bool:
        return self._is_running

    def snapshot(self) -> SimulationSnapshot:
        """Build a fresh, read-only view of current simulation state."""

        system = self._state.respiratory_system
        circuit = system.circuit
        alveoli = system.alveoli
        patient = system.patient
        accounting = system.agent_simulation_validation

        return SimulationSnapshot(
            is_running=self._is_running,
            elapsed_s=self._state.elapsed_s,
            circuit_volume_l=circuit.circuit_volume_l,
            fresh_gas_flow_l_min=circuit.fresh_gas_flow_l_min,
            delivered_concentration_fraction=(circuit.delivered_concentration_fraction),
            alveolar_ventilation_l_min=(alveoli.alveolar_ventilation_l_min),
            cardiac_output_l_min=patient.cardiac_output_l_min,
            circuit_concentration_fraction=(circuit.circuit_concentration_fraction),
            alveolar_concentration_fraction=(alveoli.concentration_fraction),
            mixed_venous_concentration_fraction=(patient.mixed_venous_fraction),
            vessel_rich_partial_pressure_fraction=(patient.vessel_rich.partial_pressure_fraction),
            muscle_partial_pressure_fraction=(patient.muscle.partial_pressure_fraction),
            fat_partial_pressure_fraction=(patient.fat.partial_pressure_fraction),
            circuit_time_constant_s=circuit.time_constant_s,
            delivered_agent_l=accounting.delivered_agent_l,
            exhausted_agent_l=accounting.exhausted_agent_l,
            stored_agent_l=accounting.currently_stored_agent_l,
            unaccounted_agent_l=accounting.unaccounted_agent_l,
            agent_accounting_absolute_error_l=(accounting.absolute_error_l),
            agent_accounting_passes_validation=(accounting.passes_validation),
            concentration_history=tuple(self._concentration_history),
        )

    def start(self) -> None:
        self._is_running = True

    def pause(self) -> None:
        self._is_running = False

    def reset(self) -> None:
        """Stop the run and clear dynamic state while preserving settings."""

        self.pause()
        self._state.reset()
        self._concentration_history = [self._build_history_sample()]

    def set_circuit_volume(
        self,
        circuit_volume_l: float,
    ) -> None:
        """Change volume without creating or losing stored agent."""

        circuit = self._state.circuit
        stored_agent_l = circuit.agent_amount_l

        if stored_agent_l > circuit_volume_l:
            raise SimulationConfigurationError("circuit_volume_l is smaller than stored agent")

        circuit.set_circuit_volume(circuit_volume_l)
        circuit.set_agent_amount(stored_agent_l)

    def set_fresh_gas_flow(
        self,
        fresh_gas_flow_l_min: float,
    ) -> None:
        self._state.respiratory_system.set_fresh_gas_flow(fresh_gas_flow_l_min)

    def set_delivered_concentration(
        self,
        delivered_concentration_fraction: float,
    ) -> None:
        self._state.respiratory_system.set_delivered_concentration(delivered_concentration_fraction)

    def set_alveolar_ventilation(
        self,
        alveolar_ventilation_l_min: float,
    ) -> None:
        self._state.respiratory_system.set_alveolar_ventilation(alveolar_ventilation_l_min)

    def set_cardiac_output(
        self,
        cardiac_output_l_min: float,
    ) -> None:
        self._state.respiratory_system.set_cardiac_output(cardiac_output_l_min)

    def advance(self, simulation_step_s: float) -> None:
        """No-op while paused; otherwise advance state and record history."""

        if not self._is_running:
            return

        self._state.advance(simulation_step_s)
        self._concentration_history.append(self._build_history_sample())

    def _build_history_sample(
        self,
    ) -> SimulationHistorySample:
        system = self._state.respiratory_system

        return SimulationHistorySample(
            elapsed_s=self._state.elapsed_s,
            circuit_concentration_fraction=(system.circuit.circuit_concentration_fraction),
            alveolar_concentration_fraction=(system.alveoli.concentration_fraction),
            mixed_venous_concentration_fraction=(system.patient.mixed_venous_fraction),
            vessel_rich_partial_pressure_fraction=(
                system.patient.vessel_rich.partial_pressure_fraction
            ),
            muscle_partial_pressure_fraction=(system.patient.muscle.partial_pressure_fraction),
            fat_partial_pressure_fraction=(system.patient.fat.partial_pressure_fraction),
        )
