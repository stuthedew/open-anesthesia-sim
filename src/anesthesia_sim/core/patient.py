"""Patient-side compartments: the vessel-rich, muscle, and fat tissue groups
(`tissue.py`) plus mixed-venous blood (`blood.py`), coupled through cardiac
output and each tissue's perfusion fraction of it.
"""

from __future__ import annotations

from dataclasses import dataclass

from anesthesia_sim.core.blood import (
    VenousBloodCompartment,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.parameters import (
    AgentParameters,
    ReferenceAdultParameters,
)
from anesthesia_sim.core.tissue import TissueGroup
from anesthesia_sim.core.validation import (
    require_concentration_fraction,
    require_nonnegative_finite,
    require_positive_finite,
)

FLOW_FRACTION_TOLERANCE = 1e-12


@dataclass(slots=True)
class PatientCompartments:
    """VRG, muscle, fat, and mixed-venous blood."""

    cardiac_output_l_min: float
    vessel_rich: TissueGroup
    muscle: TissueGroup
    fat: TissueGroup
    venous_blood: VenousBloodCompartment

    def __post_init__(self) -> None:
        require_nonnegative_finite(
            "cardiac_output_l_min",
            self.cardiac_output_l_min,
        )

        if abs(self.total_perfusion_fraction - 1.0) > FLOW_FRACTION_TOLERANCE:
            raise SimulationConfigurationError("tissue perfusion fractions must sum to 1")

        self._update_blood_flows()

    @classmethod
    def from_parameters(
        cls,
        agent: AgentParameters,
        patient: ReferenceAdultParameters,
    ) -> PatientCompartments:
        """Construct the v0.1.0 reference patient."""

        blood_gas = agent.blood_gas_partition_coefficient

        return cls(
            cardiac_output_l_min=(patient.default_cardiac_output_l_min),
            vessel_rich=TissueGroup(
                name="vessel_rich",
                volume_l=patient.vessel_rich_volume_l,
                perfusion_fraction=(patient.vessel_rich_perfusion_fraction),
                blood_gas_partition_coefficient=blood_gas,
                tissue_gas_partition_coefficient=(
                    agent.vessel_rich_tissue_gas_partition_coefficient
                ),
            ),
            muscle=TissueGroup(
                name="muscle",
                volume_l=patient.muscle_volume_l,
                perfusion_fraction=(patient.muscle_perfusion_fraction),
                blood_gas_partition_coefficient=blood_gas,
                tissue_gas_partition_coefficient=(agent.muscle_tissue_gas_partition_coefficient),
            ),
            fat=TissueGroup(
                name="fat",
                volume_l=patient.fat_volume_l,
                perfusion_fraction=(patient.fat_perfusion_fraction),
                blood_gas_partition_coefficient=blood_gas,
                tissue_gas_partition_coefficient=(agent.fat_tissue_gas_partition_coefficient),
            ),
            venous_blood=VenousBloodCompartment(
                volume_l=patient.venous_blood_volume_l,
                blood_gas_partition_coefficient=blood_gas,
                blood_flow_l_min=(patient.default_cardiac_output_l_min),
            ),
        )

    @property
    def tissues(self) -> tuple[TissueGroup, ...]:
        return (
            self.vessel_rich,
            self.muscle,
            self.fat,
        )

    @property
    def total_perfusion_fraction(self) -> float:
        """Sum tissue-group perfusion fractions; must equal 1 within tolerance."""

        return sum(tissue.perfusion_fraction for tissue in self.tissues)

    @property
    def tissue_return_fraction(self) -> float:
        """Return flow-weighted tissue outflow fraction."""

        return sum(
            tissue.perfusion_fraction * tissue.venous_outflow_fraction for tissue in self.tissues
        )

    @property
    def mixed_venous_fraction(self) -> float:
        """Return the venous blood concentration."""

        return self.venous_blood.concentration_fraction

    @property
    def total_agent_amount_l(self) -> float:
        return (
            sum(tissue.agent_amount_l for tissue in self.tissues) + self.venous_blood.agent_amount_l
        )

    def set_cardiac_output(
        self,
        cardiac_output_l_min: float,
    ) -> None:
        """Change cardiac output without changing stored agent."""

        require_nonnegative_finite(
            "cardiac_output_l_min",
            cardiac_output_l_min,
        )
        self.cardiac_output_l_min = cardiac_output_l_min
        self._update_blood_flows()

    def advance(
        self,
        arterial_fraction: float,
        simulation_step_s: float,
    ) -> float:
        """Advance tissues and venous blood.

        Returns the signed change in total patient agent.
        """

        require_concentration_fraction(
            "arterial_fraction",
            arterial_fraction,
        )
        require_positive_finite(
            "simulation_step_s",
            simulation_step_s,
        )

        initial_amount_l = self.total_agent_amount_l

        for tissue in self.tissues:
            tissue.advance(
                arterial_fraction=arterial_fraction,
                simulation_step_s=simulation_step_s,
            )

        self.venous_blood.advance(
            tissue_return_fraction=(self.tissue_return_fraction),
            simulation_step_s=simulation_step_s,
        )

        return self.total_agent_amount_l - initial_amount_l

    def reset(self) -> None:
        """Clear all patient agent while preserving settings."""

        for tissue in self.tissues:
            tissue.reset()

        self.venous_blood.reset()

    def _update_blood_flows(self) -> None:
        for tissue in self.tissues:
            tissue.set_blood_flow(self.cardiac_output_l_min * tissue.perfusion_fraction)

        self.venous_blood.set_blood_flow(self.cardiac_output_l_min)
