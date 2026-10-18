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

_TISSUE_GROUP_FIELDS = ("vessel_rich", "muscle", "fat")
"""The patient's tissue group fields, in the order `PatientCompartments.tissues` gives them."""


def _require_fractions_sum_to_one(total_perfusion_fraction: float) -> None:
    """Refuse tissue perfusion fractions whose sum is not 1.

    Raises:
        SimulationConfigurationError: the sum differs from 1 by more than
            `FLOW_FRACTION_TOLERANCE`.
    """

    if abs(total_perfusion_fraction - 1.0) > FLOW_FRACTION_TOLERANCE:
        raise SimulationConfigurationError("tissue perfusion fractions must sum to 1")


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
        """Refuse tissue perfusion fractions that do not sum to 1.

        Each tissue group's blood flow is its perfusion fraction of the
        cardiac output, and the venous pool's is the whole of it
        (`docs/MODEL.md` § "Tissue groups"). No compartment stores a flow:
        each is formed from this patient's own output wherever it is read
        (`TissueGroup.blood_flow_l_min_at`, `PL-HQF5`). So the cardiac output
        is the one stored copy, and the fractions summing to 1 is the only
        relation left to check. A tissue group refuses a second write of its
        fraction (`PL-Z0HN`), and `__setattr__` makes the same check when a
        tissue group of a built patient is replaced, so the relation checked
        here holds for the patient's whole life.

        Raises:
            SimulationConfigurationError: the tissue perfusion fractions do not
                sum to 1.
        """

        # The cardiac output's type was required as the constructor wrote the
        # field, by `__setattr__` below.
        _require_fractions_sum_to_one(self.total_perfusion_fraction)

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
            """Write a field, refusing a cardiac output or a tissue group the patient cannot take.

            The patient stores its cardiac output only in this field, so this
            method checks every write to it. That covers the constructor,
            `set_cardiac_output`, and a direct assignment that bypasses both,
            as `BreathingCircuit.__setattr__` explains (`PL-LBQY`). Nothing is
            written when a value is refused.

            The type is the whole check. Every compartment's blood flow is
            formed from this field when it is read, so a new output moves
            every flow with it and no flow can be left at the old output.
            Before `PL-HQF5` each compartment stored its own flow, and this
            method also refused an output that the stored flows did not match
            (`PL-KFNP`). Before that, the mismatch was refused only when the
            settings record was next built, at the next step or at Reset
            (`PL-M4M0`).

            A tissue group written to a built patient replaces one whose
            perfusion fraction the patient has already checked. So the new
            group is refused unless the three fractions still sum to 1, as
            `__post_init__` requires (`PL-Z0HN`). The constructor, a copy and
            a pickle write each tissue group first onto a patient that has
            none, and those writes are left to `__post_init__`.

            Raises:
                TypeError: `name` is `cardiac_output_l_min` and `value` was not
                    built as a `CardiacOutput` (`require_cardiac_output`), or
                    `name` names a tissue group and `value` is not a
                    `TissueGroup`.
                SimulationConfigurationError: `name` names a tissue group of a
                    built patient, and with `value` in its place the tissue
                    perfusion fractions would not sum to 1.
            """

            if name == "cardiac_output_l_min":
                require_cardiac_output(value)
            elif name in _TISSUE_GROUP_FIELDS and hasattr(self, name):
                if not isinstance(value, TissueGroup):
                    raise TypeError(
                        f"{name} of {value!r} has type {type(value).__name__}, not TissueGroup"
                    )

                _require_fractions_sum_to_one(
                    sum(
                        (value if field == name else getattr(self, field)).perfusion_fraction
                        for field in _TISSUE_GROUP_FIELDS
                    )
                )

            super().__setattr__(name, value)

        def __delattr__(self, name: str) -> None:
            """Refuse to delete any field.

            The fraction-sum check above applies only to a patient that
            already has the group. A group deleted and written again would
            bypass it (`PL-Z0HN`, found at review). No field of a built
            patient is ever meant to be absent, so every deletion is refused.

            Raises:
                SimulationConfigurationError: always.
            """

            raise SimulationConfigurationError(
                f"the patient's {name} cannot be deleted, because a value written after it "
                "would bypass the checks made when the patient is built: build a new patient"
            )

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
                volume_l=patient.venous_pool_volume_l, blood_gas_partition_coefficient=blood_gas
            ),
        )

    @property
    def tissues(self) -> tuple[TissueGroup, ...]:
        return tuple(getattr(self, field) for field in _TISSUE_GROUP_FIELDS)

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
        (`core/supported_ranges.py`). Every compartment's blood flow is formed
        from the output when it is read, so writing the field moves them all
        (`PL-HQF5`).

        Raises:
            TypeError: `cardiac_output_l_min` was not built as a
                `CardiacOutput`. Nothing is written when it is refused.
        """

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
