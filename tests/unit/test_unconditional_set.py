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
    SubstanceInstance,
    Tier,
    UnconditionalValue,
    compartment_value,
    unconditional_set,
)

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
