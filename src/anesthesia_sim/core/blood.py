"""The mixed-venous blood compartment: pools flow-weighted outflow from every
tissue group (see `patient.py`) before it returns to the alveoli as the
arterial input, under this model's flow-limited arterial simplification.
"""

from dataclasses import dataclass
from math import exp, inf

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.validation import (
    require_concentration_fraction,
    require_nonnegative_finite,
    require_positive_finite,
)

SECONDS_PER_MINUTE = 60.0


@dataclass(frozen=True, slots=True)
class VenousBloodCompartmentState:
    """The venous pool's run state: what a step can change.

    Volume, partition coefficient and blood flow are absent for the reason
    given on `TissueGroupState`.
    """

    agent_amount_l: float


@dataclass(slots=True)
class VenousBloodCompartment:
    """One ideal, well-mixed venous blood compartment."""

    volume_l: float
    blood_gas_partition_coefficient: float
    blood_flow_l_min: float
    agent_amount_l: float = 0.0

    def __post_init__(self) -> None:
        require_positive_finite("volume_l", self.volume_l)
        require_positive_finite(
            "blood_gas_partition_coefficient", self.blood_gas_partition_coefficient
        )
        require_nonnegative_finite("blood_flow_l_min", self.blood_flow_l_min)
        require_nonnegative_finite("agent_amount_l", self.agent_amount_l)

        if self.agent_amount_l > self.capacity_l:
            raise SimulationConfigurationError("agent_amount_l exceeds venous blood capacity")

    @property
    def capacity_l(self) -> float:
        """Equivalent gas capacity at a fraction of one."""

        return self.volume_l * self.blood_gas_partition_coefficient

    @property
    def concentration_fraction(self) -> float:
        """Return partial-pressure-equivalent venous fraction."""

        return self.agent_amount_l / self.capacity_l

    @property
    def time_constant_s(self) -> float:
        """Return the venous mixing time constant."""

        if self.blood_flow_l_min == 0.0:
            return inf

        return SECONDS_PER_MINUTE * self.volume_l / self.blood_flow_l_min

    def set_blood_flow(self, blood_flow_l_min: float) -> None:
        """Change blood flow without changing stored agent."""

        require_nonnegative_finite("blood_flow_l_min", blood_flow_l_min)
        self.blood_flow_l_min = blood_flow_l_min

    def set_concentration_fraction(self, concentration_fraction: float) -> None:
        """Set venous state from an equilibrium fraction."""

        require_concentration_fraction("concentration_fraction", concentration_fraction)
        self.agent_amount_l = self.capacity_l * concentration_fraction

    def advance(self, tissue_return_fraction: float, simulation_step_s: float) -> float:
        """Mix tissue return into venous blood exactly.

        Returns the signed change in venous agent amount.
        """

        require_concentration_fraction("tissue_return_fraction", tissue_return_fraction)
        require_positive_finite("simulation_step_s", simulation_step_s)

        if self.blood_flow_l_min == 0.0:
            return 0.0

        initial_amount_l = self.agent_amount_l
        initial_fraction = self.concentration_fraction
        fraction_remaining = exp(-simulation_step_s / self.time_constant_s)

        next_fraction = (
            tissue_return_fraction
            + (initial_fraction - tissue_return_fraction) * fraction_remaining
        )

        self.agent_amount_l = self.capacity_l * next_fraction

        return self.agent_amount_l - initial_amount_l

    def capture_state(self) -> VenousBloodCompartmentState:
        """Record run state so a failed step can be rolled back."""

        return VenousBloodCompartmentState(agent_amount_l=self.agent_amount_l)

    def restore_state(self, state: VenousBloodCompartmentState) -> None:
        """Restore run state previously captured by `capture_state()`.

        Assigns the field directly, so that rolling back cannot itself
        raise; see `BreathingCircuit.restore_state()`.
        """

        self.agent_amount_l = state.agent_amount_l

    def reset(self) -> None:
        """Clear venous agent while preserving parameters."""

        self.agent_amount_l = 0.0
