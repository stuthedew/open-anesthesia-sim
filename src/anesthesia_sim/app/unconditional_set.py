"""The values no Workspace may remove: `docs/MODEL.md`'s unconditional set, as data.

`docs/MODEL.md` § "Minimum displayed outputs" -> "What this list requires
once the layout is the reader's" divides the required display in three. The
unconditional part is the set a reader could misread the run's other
displayed numbers without. It sits outside the area system, so no split,
join, close or Workspace switch can take it off the screen. This module
states that set in code, so the region that holds it and the tests that
check the region are built from one declaration rather than from a list
written out twice (`PL-NWTM`).

The set has two tiers, plus the control-input record:

- **The invariant tier** does not depend on what is being simulated:
  simulated time, the rate it advances at, run state, why a run halted, and
  what is being administered.
- **The per-substance tier** is chosen by the substance the run models. For
  the inhaled-agent model it is the delivered concentration, the six
  compartment concentrations in both units, and the agent's 1 MAC stated.
  A run with no volatile agent owes none of those, so the tier is passed in
  as a `SubstanceInstance` rather than written into the set.
- **The control-input record** is unconditional on its own terms: the list
  of settings changed during the run, which `docs/MODEL.md` states apart from
  both tiers ("The control-input timeline splits the same way").

Two things are deliberately not here. The agent accounting is required to be
reachable, not to be visible, so it belongs to the View registry (`PL-50PZ`).
The name of the run a window shows joins the invariant tier only once more
than one top-level window can exist, and which tier each window carries is
`PL-W54S`'s.

Nothing here imports a toolkit, so the declaration is tested without a
`QApplication` and read by the widgets that draw it.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final

from anesthesia_sim.app.run_series import RecordedQuantity

__all__ = [
    "CONTROL_RECORD_TIER",
    "INHALED_AGENT",
    "INVARIANT_TIER",
    "SubstanceInstance",
    "Tier",
    "UnconditionalSet",
    "UnconditionalValue",
    "compartment_value",
    "unconditional_set",
]


class Tier(StrEnum):
    """Which part of the unconditional set a value belongs to."""

    INVARIANT = "invariant"
    """True of every run, whatever substance it models."""

    PER_SUBSTANCE = "per-substance"
    """Chosen by the substance the run models; never true of every run."""

    CONTROL_RECORD = "control-input record"
    """The settings changed during the run, stated apart from both tiers."""


class UnconditionalValue(StrEnum):
    """One value the unconditional set can require, under a stable identifier."""

    SIMULATED_TIME = "simulated_time"
    PLAYBACK_RATE = "playback_rate"
    RUN_STATE = "run_state"
    HALT_REASON = "halt_reason"
    ADMINISTERED_SUBSTANCE = "administered_substance"
    DELIVERED_CONCENTRATION = "delivered_concentration"
    CIRCUIT_CONCENTRATION = "circuit_concentration"
    ALVEOLAR_CONCENTRATION = "alveolar_concentration"
    MIXED_VENOUS_CONCENTRATION = "mixed_venous_concentration"
    VESSEL_RICH_CONCENTRATION = "vessel_rich_concentration"
    MUSCLE_CONCENTRATION = "muscle_concentration"
    FAT_CONCENTRATION = "fat_concentration"
    ONE_MAC = "one_mac"
    CONTROL_INPUT_RECORD = "control_input_record"

    @property
    def tier(self) -> Tier:
        """The part of the set this value belongs to."""

        return _TIERS[self]


_TIERS: Final[Mapping[UnconditionalValue, Tier]] = MappingProxyType(
    {
        UnconditionalValue.SIMULATED_TIME: Tier.INVARIANT,
        UnconditionalValue.PLAYBACK_RATE: Tier.INVARIANT,
        UnconditionalValue.RUN_STATE: Tier.INVARIANT,
        UnconditionalValue.HALT_REASON: Tier.INVARIANT,
        UnconditionalValue.ADMINISTERED_SUBSTANCE: Tier.INVARIANT,
        UnconditionalValue.DELIVERED_CONCENTRATION: Tier.PER_SUBSTANCE,
        UnconditionalValue.CIRCUIT_CONCENTRATION: Tier.PER_SUBSTANCE,
        UnconditionalValue.ALVEOLAR_CONCENTRATION: Tier.PER_SUBSTANCE,
        UnconditionalValue.MIXED_VENOUS_CONCENTRATION: Tier.PER_SUBSTANCE,
        UnconditionalValue.VESSEL_RICH_CONCENTRATION: Tier.PER_SUBSTANCE,
        UnconditionalValue.MUSCLE_CONCENTRATION: Tier.PER_SUBSTANCE,
        UnconditionalValue.FAT_CONCENTRATION: Tier.PER_SUBSTANCE,
        UnconditionalValue.ONE_MAC: Tier.PER_SUBSTANCE,
        UnconditionalValue.CONTROL_INPUT_RECORD: Tier.CONTROL_RECORD,
    }
)

#: The readout each compartment concentration is drawn on, by the quantity
#: that readout reads. `RecordedQuantity.WASH_IN_RATIO` is absent: F_A/F_I is
#: a chart surface, and `docs/MODEL.md` makes it conditional.
_COMPARTMENT_VALUES: Final[Mapping[RecordedQuantity, UnconditionalValue]] = MappingProxyType(
    {
        RecordedQuantity.CIRCUIT: UnconditionalValue.CIRCUIT_CONCENTRATION,
        RecordedQuantity.ALVEOLAR: UnconditionalValue.ALVEOLAR_CONCENTRATION,
        RecordedQuantity.MIXED_VENOUS: UnconditionalValue.MIXED_VENOUS_CONCENTRATION,
        RecordedQuantity.VESSEL_RICH: UnconditionalValue.VESSEL_RICH_CONCENTRATION,
        RecordedQuantity.MUSCLE: UnconditionalValue.MUSCLE_CONCENTRATION,
        RecordedQuantity.FAT: UnconditionalValue.FAT_CONCENTRATION,
    }
)

#: The invariant tier, in the order the region draws it.
INVARIANT_TIER: Final[tuple[UnconditionalValue, ...]] = tuple(
    value for value, tier in _TIERS.items() if tier is Tier.INVARIANT
)

#: The control-input record, which is one value.
CONTROL_RECORD_TIER: Final[tuple[UnconditionalValue, ...]] = (
    UnconditionalValue.CONTROL_INPUT_RECORD,
)


def compartment_value(quantity: RecordedQuantity) -> UnconditionalValue:
    """The unconditional value a compartment's readout carries.

    Raises:
        KeyError: `quantity` is `RecordedQuantity.WASH_IN_RATIO`, which no
            readout draws.
    """

    return _COMPARTMENT_VALUES[quantity]


@dataclass(frozen=True, slots=True)
class SubstanceInstance:
    """The per-substance tier for one kind of modelled substance.

    `docs/MODEL.md` states the tier as a test, not as a list: a value belongs
    to it when a reader could misread the run's other numbers without it.
    Each substance model answers that test once, where its own model is
    specified, and this value is that answer.

    Attributes:
        substance_model: What the run models, in words a reader would use.
        values: The values the test selects for it, in the order the region
            draws them.

    Raises:
        ValueError: A value is not in the per-substance tier, or appears
            twice. An invariant value here would be required twice, and a
            per-substance value of one model must not reach the invariant
            tier, where every run would owe it.
    """

    substance_model: str
    values: tuple[UnconditionalValue, ...]

    def __post_init__(self) -> None:
        misplaced = [value for value in self.values if value.tier is not Tier.PER_SUBSTANCE]

        if misplaced:
            verdict = (
                "is not a per-substance value"
                if len(misplaced) == 1
                else "are not per-substance values"
            )
            raise ValueError(
                f"the per-substance tier for {self.substance_model} holds "
                f"{', '.join(value.value for value in misplaced)}, which {verdict}"
            )

        if len(set(self.values)) != len(self.values):
            raise ValueError(
                f"the per-substance tier for {self.substance_model} names a value twice"
            )


#: The tier for the inhaled-agent model `docs/MODEL.md` specifies: the
#: delivered concentration and the six compartment concentrations, each in
#: percent and as a multiple of 1 MAC, and that agent's 1 MAC stated in
#: percent so the multiples carry their divisor. Every agent this build loads
#: is an inhaled agent, so every run selects it.
INHALED_AGENT: Final = SubstanceInstance(
    "an inhaled agent from a vaporizer",
    (
        UnconditionalValue.DELIVERED_CONCENTRATION,
        *(_COMPARTMENT_VALUES[quantity] for quantity in _COMPARTMENT_VALUES),
        UnconditionalValue.ONE_MAC,
    ),
)


@dataclass(frozen=True, slots=True)
class UnconditionalSet:
    """Every value one run's unconditional region must hold, by tier.

    Attributes:
        invariant: `INVARIANT_TIER`.
        per_substance: The tier chosen by the substance the run models.
        control_record: `CONTROL_RECORD_TIER`.
    """

    invariant: tuple[UnconditionalValue, ...]
    per_substance: SubstanceInstance
    control_record: tuple[UnconditionalValue, ...]

    @property
    def values(self) -> tuple[UnconditionalValue, ...]:
        """Every value in the set, invariant tier first."""

        return (*self.invariant, *self.per_substance.values, *self.control_record)

    def tier(self, tier: Tier) -> tuple[UnconditionalValue, ...]:
        """The values of one tier."""

        return tuple(value for value in self.values if value.tier is tier)


def unconditional_set(substance: SubstanceInstance) -> UnconditionalSet:
    """The unconditional set for a run modelling `substance`.

    Args:
        substance: The per-substance tier the run's substance model selects;
            `INHALED_AGENT` for every run this build makes.

    Returns:
        The invariant tier, that substance's tier and the control-input
        record.
    """

    return UnconditionalSet(INVARIANT_TIER, substance, CONTROL_RECORD_TIER)
