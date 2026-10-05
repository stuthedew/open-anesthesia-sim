"""Patient-side compartments: the vessel-rich, muscle, and fat tissue groups
(`tissue.py`) plus mixed-venous blood (`blood.py`), coupled through cardiac
output and each tissue's perfusion fraction of it.

`PatientCompartments` holds those compartments and the flow allocation
between them, and holds no method that steps them. It had one - `advance()`,
which stepped the three tissue groups and then mixed their end-of-step return
into the venous pool - and that was an operator split rather than a closed
form: `core/__init__.py` carries the measurement and `PL-74R0` the decision.
Nothing outside the governing equations may move agent between two modelled
compartments, which is the rule `alveolar.py` states for the same reason.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from anesthesia_sim.core.blood import VenousBloodCompartment, VenousBloodCompartmentState
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.parameters import (
    FLOW_FRACTION_TOLERANCE,
    AgentParameters,
    ReferenceAdultParameters,
)
from anesthesia_sim.core.supported_ranges import CardiacOutput, require_cardiac_output
from anesthesia_sim.core.tissue import TissueGroup, TissueGroupState


@dataclass(frozen=True, slots=True)
class PatientCompartmentsState:
    """The patient side's run state, one entry per compartment.

    Named per compartment rather than held as a tuple, so that restoring
    cannot silently pair a snapshot with the wrong tissue group; cardiac
    output is absent because it is a setting, not trajectory.
    """

    vessel_rich: TissueGroupState
    muscle: TissueGroupState
    fat: TissueGroupState
    venous_blood: VenousBloodCompartmentState


@dataclass(slots=True)
class PatientCompartments:
    """VRG, muscle, fat, and mixed-venous blood."""

    cardiac_output_l_min: CardiacOutput
    vessel_rich: TissueGroup
    muscle: TissueGroup
    fat: TissueGroup
    venous_blood: VenousBloodCompartment

    def __post_init__(self) -> None:
        # The cardiac output's type was required as the constructor wrote the
        # field, by `__setattr__` below.
        if abs(self.total_perfusion_fraction - 1.0) > FLOW_FRACTION_TOLERANCE:
            raise SimulationConfigurationError("tissue perfusion fractions must sum to 1")

        self._update_blood_flows()

    if not TYPE_CHECKING:  # pragma: no branch - TYPE_CHECKING is False at run time
        # Hidden from `mypy` on purpose. A class that defines `__setattr__` is
        # one `mypy` lets assign any attribute name, typed by the method's
        # `value`, so with the guard in view a misspelt field written in `src/`
        # would pass `--strict` and fail at run time against the slots - on
        # these three classes alone. Hidden, `mypy` reads the dataclass's
        # fields and their types as before, and this is the runtime half for
        # the callers it does not read; its three lines are checked by their
        # tests rather than by `mypy` (`PL-LBQY`, found at review).

        def __setattr__(self, name: str, value: object) -> None:
            """Write a field, refusing a cardiac output that was not built as a `CardiacOutput`.

            The one place a cardiac output is stored on the patient is this field,
            so its type is required here, for the constructor, `set_cardiac_output`
            and an assignment made past both alike, as
            `BreathingCircuit.__setattr__` explains (`PL-LBQY`). Nothing is written
            when it is refused. The type is all it requires: a checked output
            written past the setter leaves every tissue's blood flow at the old
            output, which is the relation `set_cardiac_output` keeps and
            `UptakeEquationSettings` refuses at the next step, as the
            `SimulationNumericalError` `advance()` restates every guard reached
            inside a step as, and at Reset, where `SimulationController.reset()`
            rebuilds the record and the view handles no refusal (`PL-M4M0`;
            `PL-Z0T3` records the one copy that reaches it).

            Raises:
                TypeError: `name` is `cardiac_output_l_min` and `value` was not
                    built as a `CardiacOutput` (`require_cardiac_output`).
            """

            if name == "cardiac_output_l_min":
                require_cardiac_output(value)

            super().__setattr__(name, value)

    @classmethod
    def from_parameters(
        cls, agent: AgentParameters, patient: ReferenceAdultParameters
    ) -> PatientCompartments:
        """Construct the v0.1.0 reference patient.

        The data file's default cardiac output is parsed into its checked type
        here, where the patient is built from it, so a file naming one outside
        the supported range is refused in the words a refused control uses
        (`core/supported_ranges.py`); `core/parameters.py` checks the value
        for sign and finiteness alone and holds no copy of the range.

        Raises:
            SimulationConfigurationError: the file's default cardiac output is
                outside the supported range.
        """

        blood_gas = agent.blood_gas_partition_coefficient

        return cls(
            cardiac_output_l_min=CardiacOutput(patient.default_cardiac_output_l_min),
            vessel_rich=TissueGroup(
                name="vessel_rich",
                volume_l=patient.vessel_rich_volume_l,
                perfusion_fraction=patient.vessel_rich_perfusion_fraction,
                blood_gas_partition_coefficient=blood_gas,
                tissue_gas_partition_coefficient=(
                    agent.vessel_rich_tissue_gas_partition_coefficient
                ),
            ),
            muscle=TissueGroup(
                name="muscle",
                volume_l=patient.muscle_volume_l,
                perfusion_fraction=patient.muscle_perfusion_fraction,
                blood_gas_partition_coefficient=blood_gas,
                tissue_gas_partition_coefficient=agent.muscle_tissue_gas_partition_coefficient,
            ),
            fat=TissueGroup(
                name="fat",
                volume_l=patient.fat_volume_l,
                perfusion_fraction=patient.fat_perfusion_fraction,
                blood_gas_partition_coefficient=blood_gas,
                tissue_gas_partition_coefficient=agent.fat_tissue_gas_partition_coefficient,
            ),
            venous_blood=VenousBloodCompartment(
                volume_l=patient.venous_pool_volume_l,
                blood_gas_partition_coefficient=blood_gas,
                blood_flow_l_min=patient.default_cardiac_output_l_min,
            ),
        )

    @property
    def tissues(self) -> tuple[TissueGroup, ...]:
        return (self.vessel_rich, self.muscle, self.fat)

    @property
    def total_perfusion_fraction(self) -> float:
        """Sum tissue-group perfusion fractions; must equal 1 within tolerance."""

        return sum(tissue.perfusion_fraction for tissue in self.tissues)

    @property
    def tissue_return_partial_pressure_fraction(self) -> float:
        """The flow-weighted partial-pressure fraction returning to the venous pool.

        Each group contributes its venous outflow in proportion to its share
        of cardiac output; `TissueGroup.venous_outflow_partial_pressure_fraction`
        is why that outflow equals the group's own fraction.
        """

        return sum(
            tissue.perfusion_fraction * tissue.venous_outflow_partial_pressure_fraction
            for tissue in self.tissues
        )

    @property
    def mixed_venous_partial_pressure_fraction(self) -> float:
        """The mixed-venous partial-pressure-equivalent fraction $`F_v`$.

        Not the venous *concentration*, which is this times
        $`\\lambda_{b:g}`$; `docs/MODEL.md` § "Concentrations" is why every
        compartment here is stated as a partial-pressure-equivalent fraction.
        """

        return self.venous_blood.partial_pressure_fraction

    @property
    def total_agent_amount_l(self) -> float:
        return (
            sum(tissue.agent_amount_l for tissue in self.tissues) + self.venous_blood.agent_amount_l
        )

    def set_cardiac_output(self, cardiac_output_l_min: CardiacOutput) -> None:
        """Change cardiac output without changing stored agent.

        The output arrives checked against the supported range, which its
        type was built through and nothing here checks again
        (`core/supported_ranges.py`); that it was built as the type is
        required by the write itself, in `__setattr__`. Every tissue's blood
        flow is then its perfusion fraction of the new value.

        Raises:
            TypeError: `cardiac_output_l_min` was not built as a
                `CardiacOutput`. Nothing is written when it is refused.
        """

        self.cardiac_output_l_min = cardiac_output_l_min
        self._update_blood_flows()

    def capture_state(self) -> PatientCompartmentsState:
        """Record run state so a failed step can be rolled back."""

        return PatientCompartmentsState(
            vessel_rich=self.vessel_rich.capture_state(),
            muscle=self.muscle.capture_state(),
            fat=self.fat.capture_state(),
            venous_blood=self.venous_blood.capture_state(),
        )

    def restore_state(self, state: PatientCompartmentsState) -> None:
        """Restore run state previously captured by `capture_state()`."""

        self.vessel_rich.restore_state(state.vessel_rich)
        self.muscle.restore_state(state.muscle)
        self.fat.restore_state(state.fat)
        self.venous_blood.restore_state(state.venous_blood)

    def reset(self) -> None:
        """Clear all patient agent while preserving settings."""

        for tissue in self.tissues:
            tissue.reset()

        self.venous_blood.reset()

    def _update_blood_flows(self) -> None:
        for tissue in self.tissues:
            tissue.set_blood_flow(self.cardiac_output_l_min * tissue.perfusion_fraction)

        self.venous_blood.set_blood_flow(self.cardiac_output_l_min)
