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
from anesthesia_sim.core.governing_equations import TISSUE_BLOOD_FLOW_STATED_DECIMALS
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
        """Refuse compartments that are not perfused at this patient's own output.

        Each tissue group's blood flow is its perfusion fraction of cardiac
        output, and the venous pool's is the whole of it (`docs/MODEL.md`
        § "Tissue groups"). That relation is checked here and nothing is
        written, because the compartments a patient is handed need not be its
        alone: `dataclasses.replace` hands its copy the original's own, and
        setting the copy's flows on them would leave the original perfused at
        the copy's output (`PL-Z0T3`). `from_parameters` builds each
        compartment at its flow, and `set_cardiac_output` moves them together.
        Both compute the product the check does, so the comparison is exact.
        `__setattr__` makes the same check, with a message of its own, when a
        new cardiac output is assigned to a built patient (`PL-KFNP`).

        Raises:
            SimulationConfigurationError: the tissue perfusion fractions do not
                sum to 1, or a compartment's blood flow is not its share of
                this patient's cardiac output.
        """

        # The cardiac output's type was required as the constructor wrote the
        # field, by `__setattr__` below.
        if abs(self.total_perfusion_fraction - 1.0) > FLOW_FRACTION_TOLERANCE:
            raise SimulationConfigurationError("tissue perfusion fractions must sum to 1")

        unmatched = self._compartment_not_perfused_at(self.cardiac_output_l_min)

        if unmatched is not None:
            compartment, blood_flow_l_min, own_blood_flow_l_min = unmatched
            raise SimulationConfigurationError(
                f"{compartment} is perfused at {blood_flow_l_min} L/min, but this patient's "
                f"cardiac output of {self.cardiac_output_l_min} L/min gives it "
                f'{own_blood_flow_l_min} L/min (docs/MODEL.md, "Tissue groups"): compartments '
                "perfused at another output are another patient's, as a dataclasses.replace "
                "copy's are, so copy a patient whole with copy.deepcopy and change its output "
                "with set_cardiac_output"
            )

    if not TYPE_CHECKING:  # pragma: no branch - TYPE_CHECKING is False at run time
        # Hidden from `mypy` on purpose. A class that defines `__setattr__` is
        # one `mypy` lets assign any attribute name, typed by the method's
        # `value`, so with the guard in view a misspelt field written in `src/`
        # would pass `--strict` and fail at run time against the slots - on
        # the classes that define one alone. Hidden, `mypy` reads the
        # dataclass's fields and their types as before, and this is the
        # runtime half for the callers it does not read. Tests check these
        # lines, because `mypy` does not (`PL-LBQY`, found at review).

        def __setattr__(self, name: str, value: object) -> None:
            """Write a field, but refuse a cardiac output that the blood flows do not match.

            The patient stores its cardiac output only in this field, so this
            method checks every write to it. That covers the constructor,
            `set_cardiac_output`, and a direct assignment that bypasses both,
            as `BreathingCircuit.__setattr__` explains (`PL-LBQY`). Every
            write must be a `CardiacOutput`. When the patient already has an
            output, the new value must also match the compartments' blood
            flows, which is the check that `__post_init__` makes. A direct
            assignment that bypasses `set_cardiac_output` would leave every
            compartment at the flows of the old output, so it is refused, and
            the message names `set_cardiac_output` as the way to change the
            output. An assignment of an output that the flows already match is
            accepted, because the check is on the values and not on the caller
            (`PL-KFNP`). Nothing is written when a value is refused. Before
            `PL-KFNP` this method checked only the type, and the mismatch was
            refused only when the settings record was next built, at the next
            step or at Reset (`PL-M4M0`).

            The first write is checked for its type alone, because no
            compartment exists yet to compare it with. The constructor,
            `dataclasses.replace`, a copy and a pickle all write the output
            before any compartment. For the constructor and
            `dataclasses.replace`, `__post_init__` then makes the check, so a
            `dataclasses.replace` copy at a different output is refused and
            the original is unchanged. A copy at the same output, made by
            `dataclasses.replace` or `copy.copy`, shares the original's
            compartments, so changing the copy's output also changes the
            original's flows (`PL-Z0T3`). A compartment does not know which
            patient it belongs to, so a tissue's or the venous pool's blood
            flow, and a tissue's perfusion fraction, can still be changed
            without this check (`PL-HQF5`, `PL-Z0HN`).

            Raises:
                TypeError: `name` is `cardiac_output_l_min` and `value` was not
                    built as a `CardiacOutput` (`require_cardiac_output`).
                SimulationConfigurationError: `name` is `cardiac_output_l_min`,
                    the patient already has an output, and a compartment's
                    blood flow does not match `value`.
            """

            if name == "cardiac_output_l_min":
                require_cardiac_output(value)

                if hasattr(self, name):
                    self._require_rewrite_perfused_at(value)

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
        for sign and finiteness alone and holds no copy of the range. Each
        compartment is built perfused at its share of that output, which the
        constructor checks rather than sets.

        Raises:
            SimulationConfigurationError: the file's default cardiac output is
                outside the supported range.
        """

        blood_gas = agent.blood_gas_partition_coefficient
        cardiac_output_l_min = CardiacOutput(patient.default_cardiac_output_l_min)

        return cls(
            cardiac_output_l_min=cardiac_output_l_min,
            vessel_rich=TissueGroup(
                name="vessel_rich",
                volume_l=patient.vessel_rich_volume_l,
                perfusion_fraction=patient.vessel_rich_perfusion_fraction,
                blood_gas_partition_coefficient=blood_gas,
                tissue_gas_partition_coefficient=(
                    agent.vessel_rich_tissue_gas_partition_coefficient
                ),
                blood_flow_l_min=cardiac_output_l_min * patient.vessel_rich_perfusion_fraction,
            ),
            muscle=TissueGroup(
                name="muscle",
                volume_l=patient.muscle_volume_l,
                perfusion_fraction=patient.muscle_perfusion_fraction,
                blood_gas_partition_coefficient=blood_gas,
                tissue_gas_partition_coefficient=agent.muscle_tissue_gas_partition_coefficient,
                blood_flow_l_min=cardiac_output_l_min * patient.muscle_perfusion_fraction,
            ),
            fat=TissueGroup(
                name="fat",
                volume_l=patient.fat_volume_l,
                perfusion_fraction=patient.fat_perfusion_fraction,
                blood_gas_partition_coefficient=blood_gas,
                tissue_gas_partition_coefficient=agent.fat_tissue_gas_partition_coefficient,
                blood_flow_l_min=cardiac_output_l_min * patient.fat_perfusion_fraction,
            ),
            venous_blood=VenousBloodCompartment(
                volume_l=patient.venous_pool_volume_l,
                blood_gas_partition_coefficient=blood_gas,
                blood_flow_l_min=cardiac_output_l_min,
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
        (`core/supported_ranges.py`). The method first checks that the value
        was built as a `CardiacOutput`, so a value of another type changes
        nothing. It then sets each tissue group's blood flow to its perfusion
        fraction times the new output, and the venous pool's flow to the new
        output. It writes the field last, when the flows already match the
        new output, so the check in `__setattr__` passes (`PL-KFNP`). Nothing
        can fail after the first flow has changed, because a `CardiacOutput`
        times a perfusion fraction is finite and not negative, which is all
        that a compartment's blood flow requires.

        Raises:
            TypeError: `cardiac_output_l_min` was not built as a
                `CardiacOutput`. Nothing is written when it is refused.
        """

        require_cardiac_output(cardiac_output_l_min)
        self._update_blood_flows(cardiac_output_l_min)
        self.cardiac_output_l_min = cardiac_output_l_min

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

    def _update_blood_flows(self, cardiac_output_l_min: CardiacOutput) -> None:
        for tissue in self.tissues:
            tissue.set_blood_flow(cardiac_output_l_min * tissue.perfusion_fraction)

        self.venous_blood.set_blood_flow(cardiac_output_l_min)

    def _compartment_not_perfused_at(
        self, cardiac_output_l_min: CardiacOutput
    ) -> tuple[str, float, float] | None:
        """Return the first compartment whose blood flow does not match `cardiac_output_l_min`.

        This is the only place the relation is written. Each tissue group's
        blood flow must equal its perfusion fraction times the cardiac output,
        and the venous pool's blood flow must equal the cardiac output. The
        result is the compartment's name, its blood flow and the flow that
        `cardiac_output_l_min` gives it, all in L/min. It is `None` when
        every compartment matches.
        """

        shares = [
            (tissue.name, tissue.blood_flow_l_min, cardiac_output_l_min * tissue.perfusion_fraction)
            for tissue in self.tissues
        ]
        shares.append(("venous_blood", self.venous_blood.blood_flow_l_min, cardiac_output_l_min))

        for compartment, blood_flow_l_min, own_blood_flow_l_min in shares:
            if blood_flow_l_min != own_blood_flow_l_min:
                return compartment, blood_flow_l_min, own_blood_flow_l_min

        return None

    def _require_rewrite_perfused_at(self, cardiac_output_l_min: CardiacOutput) -> None:
        """Refuse a new cardiac output that the compartments' blood flows do not match.

        `__setattr__` calls this before it writes an output to a patient that
        already has one. The message names the refused output, the output
        that the patient keeps, and `set_cardiac_output` as the way to change
        it. It rounds the two blood flows to
        `TISSUE_BLOOD_FLOW_STATED_DECIMALS`, because a product such as
        6.0 × 0.76 has a floating-point rounding error in its last digits.

        Raises:
            SimulationConfigurationError: a compartment's blood flow is not
                the flow that `cardiac_output_l_min` gives it.
        """

        unmatched = self._compartment_not_perfused_at(cardiac_output_l_min)

        if unmatched is not None:
            compartment, blood_flow_l_min, own_blood_flow_l_min = unmatched
            raise SimulationConfigurationError(
                f"a cardiac output of {cardiac_output_l_min} L/min was refused, because the "
                f"compartments' blood flows do not match it. The {compartment} compartment "
                f"receives {round(blood_flow_l_min, TISSUE_BLOOD_FLOW_STATED_DECIMALS)} L/min, "
                f"but {cardiac_output_l_min} L/min would give it "
                f"{round(own_blood_flow_l_min, TISSUE_BLOOD_FLOW_STATED_DECIMALS)} L/min. The "
                f"patient keeps its cardiac output of {self.cardiac_output_l_min} L/min. Change "
                "the output with set_cardiac_output, which sets every compartment's blood flow "
                'from the new output (docs/MODEL.md, "Tissue groups")'
            )
