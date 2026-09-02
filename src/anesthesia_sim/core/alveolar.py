"""The alveolar gas compartment: one ideal, perfectly mixed lung-gas volume
that exchanges agent with the breathing circuit (ventilation) and with
pulmonary blood (uptake), sitting between `circuit.py` and `patient.py`.
"""

from dataclasses import dataclass

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.supported_ranges import require_supported_alveolar_ventilation
from anesthesia_sim.core.validation import (
    require_concentration_fraction,
    require_nonnegative_finite,
    require_positive_finite,
)


@dataclass(frozen=True, slots=True)
class AlveolarCompartmentState:
    """The alveolar compartment's run state: what a step can change.

    Gas volume and alveolar ventilation are absent for the reason given on
    `BreathingCircuitState`: they are settings, not trajectory.
    """

    agent_amount_l: float


@dataclass(slots=True)
class AlveolarCompartment:
    """One ideal, perfectly mixed alveolar gas compartment."""

    gas_volume_l: float = 2.5
    alveolar_ventilation_l_min: float = 4.0
    agent_amount_l: float = 0.0

    def __post_init__(self) -> None:
        require_positive_finite("gas_volume_l", self.gas_volume_l)
        require_supported_alveolar_ventilation(self.alveolar_ventilation_l_min)
        require_nonnegative_finite("agent_amount_l", self.agent_amount_l)

        if self.agent_amount_l > self.gas_volume_l:
            raise SimulationConfigurationError(
                "agent_amount_l exceeds the alveolar capacity for a concentration fraction of 1"
            )

    @property
    def concentration_fraction(self) -> float:
        """Return the current alveolar concentration fraction."""

        return self.agent_amount_l / self.gas_volume_l

    def set_alveolar_ventilation(self, alveolar_ventilation_l_min: float) -> None:
        """Change ventilation without changing stored alveolar agent.

        Rejects a ventilation outside the supported range rather than
        clamping it; see `core/supported_ranges.py`.
        """

        require_supported_alveolar_ventilation(alveolar_ventilation_l_min)
        self.alveolar_ventilation_l_min = alveolar_ventilation_l_min

    def set_concentration_fraction(self, concentration_fraction: float) -> None:
        """Set alveolar state from a concentration fraction."""

        require_concentration_fraction("concentration_fraction", concentration_fraction)
        self.agent_amount_l = self.gas_volume_l * concentration_fraction

    def apply_blood_uptake(self, blood_uptake_l: float) -> None:
        """Apply a signed alveolar-to-blood transfer.

        Positive values remove agent from alveolar gas.
        Negative values return agent from blood to alveolar gas.
        """

        if not isinstance(blood_uptake_l, (int, float)):
            raise SimulationConfigurationError("blood_uptake_l must be a number")

        require_nonnegative_finite("resulting_agent_amount_l", self.agent_amount_l - blood_uptake_l)

        resulting_amount_l = self.agent_amount_l - blood_uptake_l

        if resulting_amount_l > self.gas_volume_l:
            raise SimulationConfigurationError("blood transfer would exceed alveolar capacity")

        self.agent_amount_l = resulting_amount_l

    def capture_state(self) -> AlveolarCompartmentState:
        """Record run state so a failed step can be rolled back."""

        return AlveolarCompartmentState(agent_amount_l=self.agent_amount_l)

    def restore_state(self, state: AlveolarCompartmentState) -> None:
        """Restore run state previously captured by `capture_state()`.

        Assigns the field directly rather than going through
        `apply_blood_uptake()`, so that rolling back cannot itself raise;
        see `BreathingCircuit.restore_state()`.
        """

        self.agent_amount_l = state.agent_amount_l

    def reset(self) -> None:
        """Clear alveolar agent while preserving settings."""

        self.agent_amount_l = 0.0
