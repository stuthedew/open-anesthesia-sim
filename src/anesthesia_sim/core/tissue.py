"""One perfusion-limited tissue group (e.g. vessel-rich, muscle, fat):
exchanges agent with arterial blood in proportion to its own blood flow,
independently of every other tissue group.
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
PERFUSION_FRACTION_UPPER_BOUND = 1.0


@dataclass(frozen=True, slots=True)
class TissueGroupState:
    """One tissue group's run state: what a step can change.

    Name, volume, perfusion fraction, partition coefficients and blood flow
    are absent for the reason given on `BreathingCircuitState`: they are
    parameters and settings, not trajectory. Blood flow in particular is
    derived from cardiac output by `PatientCompartments`, and restoring it
    from a snapshot would undo a cardiac-output change the user made.
    """

    agent_amount_l: float


@dataclass(slots=True)
class TissueGroup:
    """One ideal, perfusion-limited tissue group."""

    name: str
    volume_l: float
    perfusion_fraction: float
    blood_gas_partition_coefficient: float
    tissue_gas_partition_coefficient: float
    blood_flow_l_min: float = 0.0
    agent_amount_l: float = 0.0

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise SimulationConfigurationError("name must be a nonempty string")

        require_positive_finite("volume_l", self.volume_l)
        require_positive_finite("perfusion_fraction", self.perfusion_fraction)

        if self.perfusion_fraction > PERFUSION_FRACTION_UPPER_BOUND:
            raise SimulationConfigurationError("perfusion_fraction must not exceed 1")

        require_positive_finite(
            "blood_gas_partition_coefficient", self.blood_gas_partition_coefficient
        )
        require_positive_finite(
            "tissue_gas_partition_coefficient", self.tissue_gas_partition_coefficient
        )
        require_nonnegative_finite("blood_flow_l_min", self.blood_flow_l_min)
        require_nonnegative_finite("agent_amount_l", self.agent_amount_l)

        if self.agent_amount_l > self.capacity_l:
            raise SimulationConfigurationError(
                "agent_amount_l exceeds the tissue capacity for a concentration fraction of 1"
            )

    @property
    def capacity_l(self) -> float:
        """Equivalent gas capacity at a tissue fraction of one."""

        return self.volume_l * self.tissue_gas_partition_coefficient

    @property
    def tissue_blood_partition_coefficient(self) -> float:
        """Return the tissue:blood partition coefficient."""

        return self.tissue_gas_partition_coefficient / self.blood_gas_partition_coefficient

    @property
    def partial_pressure_fraction(self) -> float:
        """Return the tissue partial-pressure-equivalent fraction."""

        return self.agent_amount_l / self.capacity_l

    @property
    def venous_outflow_fraction(self) -> float:
        """Return blood partial-pressure fraction leaving the tissue."""

        return self.partial_pressure_fraction

    @property
    def time_constant_s(self) -> float:
        """Return the perfusion-limited tissue time constant."""

        if self.blood_flow_l_min == 0.0:
            return inf

        return (
            SECONDS_PER_MINUTE
            * self.volume_l
            * self.tissue_blood_partition_coefficient
            / self.blood_flow_l_min
        )

    def set_blood_flow(self, blood_flow_l_min: float) -> None:
        """Change tissue blood flow without changing stored agent."""

        require_nonnegative_finite("blood_flow_l_min", blood_flow_l_min)
        self.blood_flow_l_min = blood_flow_l_min

    def set_partial_pressure_fraction(self, partial_pressure_fraction: float) -> None:
        """Set tissue state from a partial-pressure-equivalent fraction."""

        require_concentration_fraction("partial_pressure_fraction", partial_pressure_fraction)
        self.agent_amount_l = self.capacity_l * partial_pressure_fraction

    def advance(self, arterial_fraction: float, simulation_step_s: float) -> float:
        """Advance exactly for constant arterial fraction and blood flow.

        Returns the signed change in tissue agent amount. A positive value
        represents uptake by the tissue. A negative value represents return
        from the tissue to blood.
        """

        require_concentration_fraction("arterial_fraction", arterial_fraction)
        require_positive_finite("simulation_step_s", simulation_step_s)

        if self.blood_flow_l_min == 0.0:
            return 0.0

        initial_amount_l = self.agent_amount_l
        fraction_remaining = exp(-simulation_step_s / self.time_constant_s)
        initial_fraction = self.partial_pressure_fraction

        next_fraction = (
            arterial_fraction + (initial_fraction - arterial_fraction) * fraction_remaining
        )

        self.agent_amount_l = self.capacity_l * next_fraction

        return self.agent_amount_l - initial_amount_l

    def capture_state(self) -> TissueGroupState:
        """Record run state so a failed step can be rolled back."""

        return TissueGroupState(agent_amount_l=self.agent_amount_l)

    def restore_state(self, state: TissueGroupState) -> None:
        """Restore run state previously captured by `capture_state()`.

        Assigns the field directly, so that rolling back cannot itself
        raise; see `BreathingCircuit.restore_state()`.
        """

        self.agent_amount_l = state.agent_amount_l

    def reset(self) -> None:
        """Clear stored agent while preserving tissue parameters."""

        self.agent_amount_l = 0.0
