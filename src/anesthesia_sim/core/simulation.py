"""SimulationState: owns elapsed simulation time alongside the respiratory
system, so simulated time is explicit, deterministic state rather than
derived from the wall clock (see CLAUDE.md's architecture discipline).
"""

from dataclasses import dataclass, field

from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.patient import PatientCompartments
from anesthesia_sim.core.respiratory_system import (
    RespiratoryStepResult,
    RespiratorySystem,
)
from anesthesia_sim.core.validation import (
    require_nonnegative_finite,
    require_positive_finite,
)


@dataclass(slots=True)
class SimulationState:
    """Own elapsed time and the complete respiratory simulation."""

    respiratory_system: RespiratorySystem = field(default_factory=RespiratorySystem.default)
    elapsed_s: float = 0.0

    def __post_init__(self) -> None:
        require_nonnegative_finite("elapsed_s", self.elapsed_s)

    @property
    def circuit(self) -> BreathingCircuit:
        return self.respiratory_system.circuit

    @property
    def alveoli(self) -> AlveolarCompartment:
        return self.respiratory_system.alveoli

    @property
    def patient(self) -> PatientCompartments:
        return self.respiratory_system.patient

    def advance(
        self,
        simulation_step_s: float,
    ) -> RespiratoryStepResult:
        """Advance the complete system and time as one operation."""

        require_positive_finite(
            "simulation_step_s",
            simulation_step_s,
        )

        result = self.respiratory_system.advance(simulation_step_s)
        self.elapsed_s += simulation_step_s

        return result

    def reset(self) -> None:
        """Clear dynamic state while preserving user settings."""

        self.elapsed_s = 0.0
        self.respiratory_system.reset()
