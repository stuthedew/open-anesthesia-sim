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

The agent accounting is deliberately not here. It is required to be
reachable, not to be visible, so it belongs to the View registry (`PL-50PZ`).

**Each top-level window's region holds part of the set** (`PL-W54S`).
`docs/MODEL.md` § "What a second top-level window owes, and it is not the
whole set" splits the set by the reason each tier is required. Every window
carries the invariant tier, because a concentration drawn with no time, run
state or drug is misread in whatever window it is drawn. Once a second window
is open, every window also names the run it shows. The per-substance tier and
the control-input record are statements about the whole run, so they live
once, in the main window. `window_region` returns what one window owes.

Nothing here imports a toolkit, so the declaration is tested without a
`QApplication` and read by the widgets that draw it.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final

from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.layout.model import MAIN_WINDOW

__all__ = [
    "CONTROL_RECORD_TIER",
    "INHALED_AGENT",
    "INVARIANT_TIER",
    "RUN_NAME_TIER",
    "SubstanceInstance",
    "Tier",
    "UnconditionalSet",
    "UnconditionalValue",
    "compartment_value",
    "unconditional_set",
    "window_region",
]


class Tier(StrEnum):
    """Which part of the unconditional set a value belongs to."""

    INVARIANT = "invariant"
    """True of every run, whatever substance it models."""

    PER_SUBSTANCE = "per-substance"
    """Chosen by the substance the run models; never true of every run."""

    CONTROL_RECORD = "control-input record"
    """The settings changed during the run, stated apart from both tiers."""

    RUN_NAME = "run name"
    """The name of the run a window shows, owed once a second window is open."""


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
    RUN_NAME = "run_name"

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
        UnconditionalValue.RUN_NAME: Tier.RUN_NAME,
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

#: The run's name. No window owes it while the main window is the only one,
#: because there is no other window to tell its run apart from.
RUN_NAME_TIER: Final[tuple[UnconditionalValue, ...]] = (UnconditionalValue.RUN_NAME,)


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


def window_region(
    run_set: UnconditionalSet, window: int, window_count: int
) -> tuple[UnconditionalValue, ...]:
    """The values one top-level window's unconditional region must hold.

    `docs/MODEL.md` § "What a second top-level window owes, and it is not the
    whole set" decides the split (project owner, 2026-09-16, ratified). Every
    window holds the invariant tier, and also the run's name once more than
    one window is open. Only the main window, `MAIN_WINDOW`, holds the
    per-substance tier and the control-input record.

    Args:
        run_set: The unconditional set of the run the window shows.
        window: The window's index in `LayoutModel.windows`.
        window_count: How many top-level windows the layout holds.

    Returns:
        The values in the order the region draws them: the invariant tier,
        then the run's name when several windows are open, then, in the main
        window only, the per-substance tier and the control-input record.

    Raises:
        ValueError: `window_count` is less than 1, because a layout always
            holds the main window, or `window` is not the index of one of the
            layout's windows.
    """

    if window_count < 1:
        raise ValueError(f"a layout holds at least one window, the main window, not {window_count}")

    if not 0 <= window < window_count:
        raise ValueError(f"window {window} is not one of the layout's {window_count} windows")

    named = RUN_NAME_TIER if window_count > 1 else ()

    if window == MAIN_WINDOW:
        return (*run_set.invariant, *named, *run_set.per_substance.values, *run_set.control_record)

    return (*run_set.invariant, *named)
