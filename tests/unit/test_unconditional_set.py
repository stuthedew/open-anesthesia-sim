"""The declaration of `docs/MODEL.md`'s unconditional set, held without a toolkit.

Each expected value below is transcribed from `docs/MODEL.md` § "Minimum
displayed outputs" -> "What this list requires once the layout is the
reader's", not read back from `app/unconditional_set.py`, so a value dropped
from or added to the declaration fails here (`PL-NWTM`).
"""

import pytest

from anesthesia_sim.app.dashboard_frame import READOUT_PANELS
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.app.unconditional_set import (
    CONTROL_RECORD_TIER,
    INHALED_AGENT,
    INVARIANT_TIER,
    RUN_NAME_TIER,
    SubstanceInstance,
    Tier,
    UnconditionalValue,
    compartment_value,
    unconditional_set,
    window_region,
)
from anesthesia_sim.layout.model import MAIN_WINDOW

#: "Simulated time; the rate it is advancing at; run state; why a run
#: halted, when one has; what is being administered" - the invariant tier,
#: in that document's order. The run's name joins it only once a second
#: top-level window can exist, which v0.6.0 does not build.
_INVARIANT_TIER_AS_DOCUMENTED = (
    UnconditionalValue.SIMULATED_TIME,
    UnconditionalValue.PLAYBACK_RATE,
    UnconditionalValue.RUN_STATE,
    UnconditionalValue.HALT_REASON,
    UnconditionalValue.ADMINISTERED_SUBSTANCE,
)

#: "the delivered concentration and the six compartment concentrations, in
#: both units, with that agent's 1 MAC in percent stated" - the inhaled
#: instance. The six compartments are the readouts the minimum list names:
#: circuit, alveolar, mixed-venous, vessel-rich, muscle and fat.
_INHALED_CONCENTRATIONS_AS_DOCUMENTED = (
    UnconditionalValue.DELIVERED_CONCENTRATION,
    UnconditionalValue.CIRCUIT_CONCENTRATION,
    UnconditionalValue.ALVEOLAR_CONCENTRATION,
    UnconditionalValue.MIXED_VENOUS_CONCENTRATION,
    UnconditionalValue.VESSEL_RICH_CONCENTRATION,
    UnconditionalValue.MUSCLE_CONCENTRATION,
    UnconditionalValue.FAT_CONCENTRATION,
)

#: What only an inhaled agent from a vaporizer has: "no vaporizer dial, no
#: circuit concentration and no MAC multiple".
_INHALED_ONLY = (
    UnconditionalValue.DELIVERED_CONCENTRATION,
    UnconditionalValue.CIRCUIT_CONCENTRATION,
    UnconditionalValue.ONE_MAC,
)


def test_the_invariant_tier_is_the_five_values_docs_model_names() -> None:
    """Five values that depend on nothing the run models, and none that does."""

    assert INVARIANT_TIER == _INVARIANT_TIER_AS_DOCUMENTED
    assert all(value.tier is Tier.INVARIANT for value in INVARIANT_TIER)


def test_the_inhaled_run_still_returns_the_seven_concentrations_and_their_divisor() -> None:
    """Today's instance: seven concentrations, then the 1 MAC that divides them."""

    tier = unconditional_set(INHALED_AGENT).tier(Tier.PER_SUBSTANCE)

    assert tier == (*_INHALED_CONCENTRATIONS_AS_DOCUMENTED, UnconditionalValue.ONE_MAC)
    assert len(tier) - 1 == 7


def test_a_run_with_no_volatile_agent_owes_no_vaporizer_circuit_or_mac_value() -> None:
    """The tier is chosen by the substance, so none of the inhaled instance leaks into the set.

    The instance is a hypothetical intravenous drug with no tier of its own
    written yet: `docs/MODEL.md` says such a run "owes its own instance of the
    same test instead, named where that substance's model is specified", and
    no such model is specified. What this holds is that nothing outside the
    instance - the invariant tier and the record - carries a value only a
    volatile agent has, so a later intravenous run is never asked for one.
    """

    intravenous = SubstanceInstance("an intravenous drug by infusion (hypothetical)", ())
    values = unconditional_set(intravenous).values

    for value in _INHALED_ONLY:
        assert value not in values

    assert values == (*_INVARIANT_TIER_AS_DOCUMENTED, UnconditionalValue.CONTROL_INPUT_RECORD)


def test_the_control_input_record_is_unconditional_and_in_neither_tier() -> None:
    """The record itself is required; its chart marks are not, and are not here."""

    assert CONTROL_RECORD_TIER == (UnconditionalValue.CONTROL_INPUT_RECORD,)
    assert UnconditionalValue.CONTROL_INPUT_RECORD.tier is Tier.CONTROL_RECORD
    assert UnconditionalValue.CONTROL_INPUT_RECORD in unconditional_set(INHALED_AGENT).values


def test_the_set_holds_no_accounting_value() -> None:
    """The accounting tier is reachable rather than visible, so the region does not owe it."""

    names = {value.value for value in UnconditionalValue}

    assert not any("accounting" in name or "residual" in name for name in names)


def test_every_compartment_readout_carries_a_value_of_the_inhaled_tier() -> None:
    """Each of the six compartment panels the readout row draws is a required value."""

    compartments = [panel.quantity for panel in READOUT_PANELS if panel.quantity is not None]

    assert len(compartments) == 6

    for quantity in compartments:
        assert compartment_value(quantity) in INHALED_AGENT.values


def test_the_wash_in_ratio_is_not_a_readout_value() -> None:
    """F_A/F_I is a chart surface, which `docs/MODEL.md` makes conditional."""

    with pytest.raises(KeyError):
        compartment_value(RecordedQuantity.WASH_IN_RATIO)


def test_an_instance_refuses_a_value_from_another_tier() -> None:
    """An invariant value in a substance's tier would be required twice, and named wrongly."""

    with pytest.raises(ValueError, match="simulated_time, which is not a per-substance value"):
        SubstanceInstance("a substance", (UnconditionalValue.SIMULATED_TIME,))

    with pytest.raises(ValueError, match="control_input_record, which is not"):
        SubstanceInstance("a substance", (UnconditionalValue.CONTROL_INPUT_RECORD,))


def test_an_instance_refuses_a_value_named_twice() -> None:
    with pytest.raises(ValueError, match="names a value twice"):
        SubstanceInstance(
            "a substance",
            (UnconditionalValue.FAT_CONCENTRATION, UnconditionalValue.FAT_CONCENTRATION),
        )


#: The layouts a window's region is checked in: the main window alone, and the
#: main window with one, two and three more beside it.
_WINDOW_COUNTS = (1, 2, 3, 4)


@pytest.mark.parametrize("window_count", _WINDOW_COUNTS)
def test_every_window_region_carries_the_invariant_tier_and_its_run_name(window_count: int) -> None:
    """Every window holds the five invariant values, and names its run once it has company.

    `docs/MODEL.md` § "What a second top-level window owes, and it is not the
    whole set": "Every top-level window the application owns carries the
    invariant tier ... together with the name of the run that window is
    showing". A lone main window has no other window to tell its run apart
    from, so it owes no name (`PL-W54S`).
    """

    run_set = unconditional_set(INHALED_AGENT)

    for window in range(window_count):
        region = window_region(run_set, window, window_count)

        assert region[: len(_INVARIANT_TIER_AS_DOCUMENTED)] == _INVARIANT_TIER_AS_DOCUMENTED
        assert (UnconditionalValue.RUN_NAME in region) is (window_count > 1)


@pytest.mark.parametrize("window_count", _WINDOW_COUNTS)
def test_the_per_substance_tier_and_the_record_live_only_in_the_main_window(
    window_count: int,
) -> None:
    """The concentrations, the 1 MAC and the control-input record have one home.

    `docs/MODEL.md`: "The per-substance tier lives once, in the main window".
    The record goes with it, being a statement about the whole run rather
    than about one surface. A broken-out window holds only the invariant tier
    and the run's name, so a small window is not squeezed by seven
    concentrations in two units.
    """

    run_set = unconditional_set(INHALED_AGENT)
    main = window_region(run_set, MAIN_WINDOW, window_count)

    assert main == (
        *_INVARIANT_TIER_AS_DOCUMENTED,
        *(RUN_NAME_TIER if window_count > 1 else ()),
        *_INHALED_CONCENTRATIONS_AS_DOCUMENTED,
        UnconditionalValue.ONE_MAC,
        UnconditionalValue.CONTROL_INPUT_RECORD,
    )

    for window in range(1, window_count):
        assert window_region(run_set, window, window_count) == (
            *_INVARIANT_TIER_AS_DOCUMENTED,
            UnconditionalValue.RUN_NAME,
        )


def test_the_lone_main_window_owes_exactly_the_whole_set() -> None:
    """With one window, the main window's region is the run's set, so nothing moves out of it."""

    run_set = unconditional_set(INHALED_AGENT)

    assert window_region(run_set, MAIN_WINDOW, 1) == run_set.values


def test_the_run_name_is_in_no_tier_of_the_run_s_set() -> None:
    """The name is owed by a window, not by the run, so `UnconditionalSet` never holds it."""

    assert UnconditionalValue.RUN_NAME.tier is Tier.RUN_NAME
    assert UnconditionalValue.RUN_NAME not in unconditional_set(INHALED_AGENT).values
    assert UnconditionalValue.RUN_NAME not in INVARIANT_TIER


@pytest.mark.parametrize(
    ("window", "window_count", "message"),
    [
        (0, 0, "at least one window, the main window, not 0"),
        (0, -1, "at least one window, the main window, not -1"),
        (1, 1, "window 1 is not one of the layout's 1 windows"),
        (-1, 2, "window -1 is not one of the layout's 2 windows"),
    ],
)
def test_a_window_outside_the_layout_is_refused(
    window: int, window_count: int, message: str
) -> None:
    """A region is never returned for a window the layout does not hold."""

    with pytest.raises(ValueError, match=message):
        window_region(unconditional_set(INHALED_AGENT), window, window_count)
