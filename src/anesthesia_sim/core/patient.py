"""The patient-side compartments, coupled through cardiac output and each tissue's share of it.

The compartments are the vessel-rich, muscle, and fat tissue groups
(`tissue.py`) and mixed-venous blood (`blood.py`). Each tissue group receives
its perfusion fraction of the cardiac output.

`PatientCompartments` holds those compartments and the flow allocation between
them, and it has no method that steps them. It once had one, `advance()`,
which stepped the three tissue groups and then mixed their end-of-step return
into the venous pool. That was an operator split rather than a closed form.
`core/__init__.py` has the measurement, and `PL-74R0` has the decision.
Nothing outside the governing equations may move agent between two modelled
compartments. `alveolar.py` states the same rule, for the same reason.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from anesthesia_sim.core.blood import VenousBloodCompartment, VenousBloodCompartmentState
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.numerical_envelope import PartitionCoefficient
from anesthesia_sim.core.parameters import (
    AgentParameters,
    ReferenceAdultParameters,
    require_perfusion_fractions_sum_to_one,
)
from anesthesia_sim.core.supported_ranges import CardiacOutput, require_cardiac_output
from anesthesia_sim.core.tissue import TissueGroup, TissueGroupState

_TISSUE_GROUP_FIELDS = ("vessel_rich", "muscle", "fat")
"""The patient's tissue group fields, in the order `PatientCompartments.tissues` gives them."""


@dataclass(frozen=True, slots=True)
class PatientCompartmentsState:
    """The patient side's run state, one entry per compartment.

    Each compartment has a named field rather than a place in a tuple, so that
    restoring cannot silently pair a snapshot with the wrong tissue group.
    Cardiac output is absent because it is a setting, not part of the
    trajectory.
    """

    vessel_rich: TissueGroupState
    muscle: TissueGroupState
    fat: TissueGroupState
    venous_blood: VenousBloodCompartmentState


@dataclass(slots=True)
class PatientCompartments:
    """The vessel-rich group (VRG), muscle, fat, and mixed-venous blood of one patient."""

    cardiac_output_l_min: CardiacOutput
    vessel_rich: TissueGroup
    muscle: TissueGroup
    fat: TissueGroup
    venous_blood: VenousBloodCompartment

    def __post_init__(self) -> None:
        """Refuse fractions that do not sum to 1, or a tissue:blood coefficient out of range.

        Each tissue group's blood flow is its perfusion fraction of the
        cardiac output, and the venous pool's flow is the whole cardiac output
        (`docs/MODEL.md` § "Tissue groups"). No compartment stores a flow.
        Each flow is formed from this patient's own cardiac output wherever it
        is read (`TissueGroup.blood_flow_l_min_at`, `PL-HQF5`). So the cardiac
        output is the one stored copy, and the only relation left to check is
        that the fractions sum to 1. A tissue group rejects a second write of
        its fraction (`PL-Z0HN`). `__setattr__` makes the same sum check when a
        tissue group of a built patient is replaced. So the relation checked
        here still applies for the patient's whole life.

        The patient holds one blood:gas partition coefficient, in its venous
        pool (`PL-DQL9`). Each tissue group's tissue:blood coefficient is its
        tissue:gas coefficient divided by that one. Each quotient must lie
        inside the numerical envelope (`core/numerical_envelope.py`), and it is
        checked here, because no tissue group stores the divisor.
        `__setattr__` checks the quotient again when a tissue group is
        replaced.

        Raises:
            SimulationConfigurationError: the tissue perfusion fractions do not
                sum to 1, or a tissue group's tissue:blood coefficient lies
                outside the numerical envelope.
        """

        # `__setattr__` below already checked the cardiac output's type when
        # the constructor wrote the field.
        require_perfusion_fractions_sum_to_one(self.total_perfusion_fraction)

        for tissue in self.tissues:
            tissue.tissue_blood_partition_coefficient_for(self.blood_gas_partition_coefficient)

    if not TYPE_CHECKING:  # pragma: no branch - TYPE_CHECKING is False at run time
        # Hidden from `mypy` on purpose. When a class defines `__setattr__`,
        # `mypy` lets code assign any attribute name, typed by the method's
        # `value` parameter. So with this guard visible, a misspelt field
        # written in `src/` would pass `--strict` and fail at run time against
        # the slots. That happens only on the classes that define
        # `__setattr__`. With the guard hidden, `mypy` checks the dataclass's
        # fields and their types as before. This guard is the runtime check for
        # the callers that `mypy` does not check. Tests check these lines,
        # because `mypy` does not (`PL-LBQY`, found at review).

        def __setattr__(self, name: str, value: object) -> None:
            """Write a field, refusing a cardiac output or a tissue group the patient cannot take.

            The patient stores its cardiac output only in this field, so this
            method checks every write to it. That covers the constructor,
            `set_cardiac_output`, and a direct assignment that bypasses both,
            as `BreathingCircuit.__setattr__` explains (`PL-LBQY`). Nothing is
            written when a value is refused.

            Every compartment's blood flow is computed from this field each
            time the flow is read, so no flow can be left at an old cardiac
            output. A new output written straight to the field of a built
            patient is still refused. The refusal names `set_cardiac_output`,
            which is the one way to change it (`PL-KFNP`). Before `PL-HQF5`,
            that refusal kept stored flows matched to the output. It is kept so
            that there is only one way to set a cardiac output. Writing the
            value the field already holds is accepted. The constructor, a copy
            and a pickle write the field onto a patient that has none yet, so
            only its type is checked there.

            A tissue group written to a built patient replaces a group whose
            perfusion fraction the patient has already checked. So the new
            group is refused unless the three fractions still sum to 1, as
            `__post_init__` requires (`PL-Z0HN`). The constructor, a copy and
            a pickle each write a tissue group for the first time, onto a
            patient that has none. This method leaves those writes to
            `__post_init__`. The new group's tissue:blood coefficient must also
            lie inside the numerical envelope. That coefficient is computed
            from the venous pool's blood:gas coefficient.

            A venous pool written to a built patient is refused unless its
            blood:gas coefficient equals the one the patient holds (`PL-DQL9`).
            Every tissue group's tissue:blood coefficient is computed from that
            one coefficient. Once, a replacement pool with a coefficient of 0.1,
            beside tissue groups built for sevoflurane at 0.65, let the run keep
            going with uptake curves that looked plausible and were wrong.

            Raises:
                TypeError: `name` is `cardiac_output_l_min` and `value` was not
                    built as a `CardiacOutput` (`require_cardiac_output`). Also
                    raised when `name` names a tissue group and `value` is not
                    a `TissueGroup`, or when `name` is `venous_blood` and
                    `value` is not a `VenousBloodCompartment`.
                SimulationConfigurationError: `name` is `cardiac_output_l_min`
                    on a built patient and `value` differs from the output it
                    holds. Also raised when `name` names a tissue group of a
                    built patient and, with `value` in its place, the tissue
                    perfusion fractions would not sum to 1 or the new group's
                    tissue:blood coefficient would lie outside the numerical
                    envelope. Also raised when `name` is `venous_blood` on a
                    built patient and the new pool's blood:gas coefficient
                    differs from the one the patient holds.
            """

            if name == "cardiac_output_l_min":
                require_cardiac_output(value)

                if hasattr(self, name) and value != self.cardiac_output_l_min:
                    raise SimulationConfigurationError(
                        f"a cardiac output of {value} L/min written straight onto the patient "
                        "was refused. The patient keeps its cardiac output of "
                        f"{self.cardiac_output_l_min} L/min. Change the output with "
                        "set_cardiac_output, the one way a cardiac output is changed "
                        '(docs/MODEL.md, "Tissue groups")'
                    )
            elif name in _TISSUE_GROUP_FIELDS and hasattr(self, name):
                if not isinstance(value, TissueGroup):
                    raise TypeError(
                        f"{name} of {value!r} has type {type(value).__name__}, not TissueGroup"
                    )

                require_perfusion_fractions_sum_to_one(
                    sum(
                        (value if field == name else getattr(self, field)).perfusion_fraction
                        for field in _TISSUE_GROUP_FIELDS
                    )
                )
                value.tissue_blood_partition_coefficient_for(self.blood_gas_partition_coefficient)
            elif name == "venous_blood" and hasattr(self, name):
                if not isinstance(value, VenousBloodCompartment):
                    raise TypeError(
                        f"venous_blood of {value!r} has type {type(value).__name__}, "
                        "not VenousBloodCompartment"
                    )

                if value.blood_gas_partition_coefficient != self.blood_gas_partition_coefficient:
                    raise SimulationConfigurationError(
                        "a venous pool with a blood:gas partition coefficient of "
                        f"{value.blood_gas_partition_coefficient} was refused. The patient "
                        f"holds {self.blood_gas_partition_coefficient}, and every tissue "
                        "group's tissue:blood coefficient is formed from it (docs/MODEL.md, "
                        '"Blood compartments"): build a new system for another agent'
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
        here, where the patient is built from it. So a file that names a value
        outside the supported range is rejected with the same message used when
        a control's value is rejected (`core/supported_ranges.py`).
        `core/parameters.py` checks the value only for sign and finiteness, and
        keeps no copy of the range.

        The agent's blood:gas coefficient is written once, into the venous pool,
        which is the patient's blood. The tissue groups store none (`PL-DQL9`).

        Raises:
            SimulationConfigurationError: the file's default cardiac output is
                outside the supported range.
        """

        cardiac_output_l_min = CardiacOutput(patient.default_cardiac_output_l_min)

        return cls(
            cardiac_output_l_min=cardiac_output_l_min,
            vessel_rich=TissueGroup(
                name="vessel_rich",
                volume_l=patient.vessel_rich_volume_l,
                perfusion_fraction=patient.vessel_rich_perfusion_fraction,
                tissue_gas_partition_coefficient=(
                    agent.vessel_rich_tissue_gas_partition_coefficient
                ),
            ),
            muscle=TissueGroup(
                name="muscle",
                volume_l=patient.muscle_volume_l,
                perfusion_fraction=patient.muscle_perfusion_fraction,
                tissue_gas_partition_coefficient=agent.muscle_tissue_gas_partition_coefficient,
            ),
            fat=TissueGroup(
                name="fat",
                volume_l=patient.fat_volume_l,
                perfusion_fraction=patient.fat_perfusion_fraction,
                tissue_gas_partition_coefficient=agent.fat_tissue_gas_partition_coefficient,
            ),
            venous_blood=VenousBloodCompartment(
                volume_l=patient.venous_pool_volume_l,
                blood_gas_partition_coefficient=agent.blood_gas_partition_coefficient,
            ),
        )

    @property
    def blood_gas_partition_coefficient(self) -> PartitionCoefficient:
        """Return the patient's one blood:gas partition coefficient, $`\\lambda_{b:g}`$.

        The venous pool stores it, because it is a property of the blood
        (`PL-DQL9`). The lung's uptake term and every tissue group's
        tissue:blood coefficient read it from here.
        """

        return self.venous_blood.blood_gas_partition_coefficient

    @property
    def tissues(self) -> tuple[TissueGroup, ...]:
        return tuple(getattr(self, field) for field in _TISSUE_GROUP_FIELDS)

    @property
    def total_perfusion_fraction(self) -> float:
        """Return the sum of the tissue perfusion fractions, which must be 1 within tolerance."""

        return sum(tissue.perfusion_fraction for tissue in self.tissues)

    @property
    def tissue_return_partial_pressure_fraction(self) -> float:
        """The flow-weighted partial-pressure fraction returning to the venous pool.

        Each group contributes its venous outflow in proportion to its share
        of cardiac output. `TissueGroup.venous_outflow_partial_pressure_fraction`
        explains why that outflow equals the group's own fraction.
        """

        return sum(
            tissue.perfusion_fraction * tissue.venous_outflow_partial_pressure_fraction
            for tissue in self.tissues
        )

    @property
    def mixed_venous_partial_pressure_fraction(self) -> float:
        """The mixed-venous partial-pressure-equivalent fraction $`F_v`$.

        This is not the venous *concentration*, which is this fraction times
        $`\\lambda_{b:g}`$. `docs/MODEL.md` § "Concentrations" explains why
        every compartment here is stated as a partial-pressure-equivalent
        fraction.
        """

        return self.venous_blood.partial_pressure_fraction

    @property
    def total_agent_amount_l(self) -> float:
        return (
            sum(tissue.agent_amount_l for tissue in self.tissues) + self.venous_blood.agent_amount_l
        )

    def set_cardiac_output(self, cardiac_output_l_min: CardiacOutput) -> None:
        """Change cardiac output without changing stored agent.

        The output arrives already checked against the supported range,
        because its type can only be built through that check. Nothing here
        checks it again (`core/supported_ranges.py`). Every compartment's blood
        flow is formed from the output when it is read, so writing the field
        changes them all (`PL-HQF5`). This method is the one way to change the
        output of a built patient, since `__setattr__` rejects a new output
        written to the field directly (`PL-KFNP`).

        Raises:
            TypeError: `cardiac_output_l_min` was not built as a
                `CardiacOutput`. Nothing is written when it is refused.
        """

        require_cardiac_output(cardiac_output_l_min)
        # Bypass `__setattr__`, which rejects a new output written to the field
        # directly, so that this method stays the one way to change it.
        object.__setattr__(self, "cardiac_output_l_min", cardiac_output_l_min)

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
