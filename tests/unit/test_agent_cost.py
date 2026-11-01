"""What the agent cost View shows for one run, and its cost, checked against values found apart.

`app/agent_cost.py` turns a snapshot into the delivered agent in millilitres
of liquid equivalent and in litres of vapour (`PL-B396`). The expected values
here come from a closed form and from transcribed constants, never from the
conversion under test. The delivered vapour is the dial times the fresh gas
flow times the time. The vapour-to-liquid factor is worked out here from each
agent's liquid density at 20 °C and its molar mass, as `docs/MODEL.md`
§ "Agent amount" tabulates them (Laster, Fang and Eger's densities, and
formula masses), and from the ideal-gas molar volume at 20 °C and 1 atm,
written out from R.

The cost at the reader's price (`PL-1P15`) is checked the same way. The
expected cost is the liquid volume worked out here times the bottle price over
the bottle volume, divided here, and printed in this file's own format.
"""

import ast
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from anesthesia_sim.app.agent_cost import (
    COST_NOT_COMPUTED_TEXT,
    COST_NOT_CONVERTED_TEXT,
    COST_ROUNDED_TEXT,
    NO_PRICE_TEXT,
    NOT_CONVERTED_TEXT,
    PRICE_PER_ML_NOT_SHOWN_TEXT,
    REFUSED_PRICE_TEXT,
    UNIT_CHOICES,
    WITHHELD_COST,
    WITHHELD_DELIVERED,
    DeliveredShown,
    cost_shown,
    delivered_liquid_ml,
    delivered_shown,
    price_from_entry,
)
from anesthesia_sim.app.controller import SimulationController, SimulationSnapshot
from anesthesia_sim.app.dashboard_frame import SIMULATION_STEP_S
from anesthesia_sim.app.formatting import AgentAmountUnit, format_delivered_agent
from anesthesia_sim.app.preferences import (
    AGENT_COST_VIEW_UNITS,
    AgentPrice,
    Preferences,
    RefusedEntry,
)
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.supported_ranges import FreshGasFlow

#: Each agent's liquid density at 20 °C in g/mL and molar mass in g/mol,
#: transcribed from `docs/MODEL.md` § "Agent amount", the table under "Why
#: 20 °C". The densities are Laster, Fang and Eger's.
_DENSITY_AND_MOLAR_MASS = {
    "sevoflurane": (1.5203, 200.05),
    "isoflurane": (1.5019, 184.49),
    "desflurane": (1.4651, 168.04),
}

#: The molar gas constant in J/(mol K), 0 °C in kelvin, and one standard
#: atmosphere in Pa (CODATA 2022 and the SI's definitions).
_R = 8.314462618
_KELVIN_AT_20_C = 293.15
_ONE_ATM_PA = 101_325.0

#: Gas Man's millilitres of vapour from 1 mL of liquid, for each agent, at
#: 20 °C. Gas Man prints 183, 196 and 209 (Philip JH, *Workbook for Gas Man*,
#: chapter 10, printed pp. 103-105).
_GAS_MAN_VAPOUR_PER_LIQUID = {"sevoflurane": 183.0, "isoflurane": 196.0, "desflurane": 209.0}

_SECONDS_PER_MINUTE = 60.0
_SRC = Path(__file__).resolve().parents[2] / "src" / "anesthesia_sim"


def _vapour_ml_per_liquid_ml(agent_id: str) -> float:
    """Work out the millilitres of vapour from 1 mL of liquid, apart from the code under test."""

    density_g_ml, molar_mass_g_mol = _DENSITY_AND_MOLAR_MASS[agent_id]
    molar_volume_ml = _R * _KELVIN_AT_20_C / _ONE_ATM_PA * 1.0e6

    return density_g_ml / molar_mass_g_mol * molar_volume_ml


def _run(
    agent_id: str, dial_percent: float, flow_l_min: float, minutes: float
) -> SimulationSnapshot:
    controller = SimulationController(agent_id=agent_id)
    controller.set_fresh_gas_flow(FreshGasFlow(flow_l_min))
    controller.set_delivered_concentration_percent(Percent(dial_percent))
    controller.start()

    for _ in range(round(minutes * _SECONDS_PER_MINUTE / SIMULATION_STEP_S)):
        controller.advance(SIMULATION_STEP_S)

    return controller.snapshot()


def test_the_test_s_own_factor_agrees_with_gas_man_s_published_constants() -> None:
    """The factor worked out here is within 0.5 % of each constant Gas Man prints.

    This checks the oracle itself, from a source that shares no code with it.
    """

    for agent_id, published in _GAS_MAN_VAPOUR_PER_LIQUID.items():
        assert _vapour_ml_per_liquid_ml(agent_id) == pytest.approx(published, rel=0.005)


@pytest.mark.parametrize(
    ("agent_id", "dial_percent", "flow_l_min", "minutes"),
    [
        ("sevoflurane", 2.0, 4.0, 60.0),
        ("isoflurane", 1.2, 1.0, 45.0),
        ("desflurane", 6.0, 1.0, 30.0),
    ],
)
def test_the_delivered_agent_is_the_dial_times_the_flow_times_the_time_in_liquid(
    agent_id: str, dial_percent: float, flow_l_min: float, minutes: float
) -> None:
    """The liquid figure is the delivered vapour divided by the agent's own factor.

    The test uses three agents, so a factor taken from the wrong agent cannot
    pass. The two nearest factors differ by 6 %, far more than the 1e-9
    tolerance.
    """

    snapshot = _run(agent_id, dial_percent, flow_l_min, minutes)
    vapour_l = dial_percent / 100.0 * flow_l_min * minutes
    liquid_ml = vapour_l * 1000.0 / _vapour_ml_per_liquid_ml(agent_id)
    shown = delivered_shown(snapshot)

    assert delivered_liquid_ml(snapshot) == pytest.approx(liquid_ml, rel=1e-9)
    assert shown.amount_in(AgentAmountUnit.MILLILITRES_OF_LIQUID) == (
        f"{liquid_ml:.1f} mL of liquid"
    )
    assert shown.amount_in(AgentAmountUnit.LITRES_OF_VAPOUR) == f"{vapour_l:.1f} L vapour"


def test_sevoflurane_at_2_percent_and_4_l_min_for_an_hour_is_26_3_ml_of_liquid() -> None:
    """A worked case: 4.8 L of vapour is 4800 / 182.8 = 26.3 mL of liquid sevoflurane."""

    shown = delivered_shown(_run("sevoflurane", 2.0, 4.0, 60.0))

    assert shown.label == "Sevoflurane delivered"
    assert shown.amount_in(AgentAmountUnit.MILLILITRES_OF_LIQUID) == "26.3 mL of liquid"
    assert shown.amount_in(AgentAmountUnit.LITRES_OF_VAPOUR) == "4.8 L vapour"
    assert shown.instant == "1h"


def test_each_caption_says_what_its_unit_measures() -> None:
    shown = delivered_shown(_run("isoflurane", 1.2, 2.0, 1.0))
    liquid = shown.caption_in(AgentAmountUnit.MILLILITRES_OF_LIQUID)
    vapour = shown.caption_in(AgentAmountUnit.LITRES_OF_VAPOUR)

    assert liquid == "Liquid used by the vaporizer, at 20 degrees C."
    assert vapour == "Vapour put out by the vaporizer, at 20 degrees C and 1 atm."


def test_a_run_that_has_delivered_nothing_shows_zero_and_a_trace_shows_below_resolution() -> None:
    controller = SimulationController()
    start = delivered_shown(controller.snapshot())
    controller.start()
    controller.advance(SIMULATION_STEP_S)
    trace = delivered_shown(controller.snapshot())

    assert start.amount_in(AgentAmountUnit.MILLILITRES_OF_LIQUID) == "0.0 mL of liquid"
    assert start.amount_in(AgentAmountUnit.LITRES_OF_VAPOUR) == "0.0 L vapour"
    assert trace.amount_in(AgentAmountUnit.MILLILITRES_OF_LIQUID) == "<0.1 mL of liquid"
    assert trace.amount_in(AgentAmountUnit.LITRES_OF_VAPOUR) == "<0.1 L vapour"


def test_an_agent_change_converts_with_the_new_agent_s_factor() -> None:
    """After a switch, the snapshot's factor is the new agent's, checked against a fresh run."""

    switched = SimulationController(agent_id="sevoflurane")
    switched.set_agent("desflurane")
    fresh = SimulationController(agent_id="desflurane")

    assert switched.snapshot().agent_vapour_per_liquid == pytest.approx(
        _vapour_ml_per_liquid_ml("desflurane"), rel=1e-4
    )
    assert switched.snapshot().agent_vapour_per_liquid == fresh.snapshot().agent_vapour_per_liquid


def test_a_delivered_amount_that_cannot_be_converted_is_named_rather_than_shown() -> None:
    snapshot = SimulationController().snapshot()
    broken = snapshot.__class__(
        **{field: getattr(snapshot, field) for field in snapshot.__dataclass_fields__}
        | {"agent_vapour_per_liquid": float("inf")}
    )

    shown = delivered_shown(broken)

    assert shown.amount_in(AgentAmountUnit.MILLILITRES_OF_LIQUID) == NOT_CONVERTED_TEXT
    assert shown.amount_in(AgentAmountUnit.LITRES_OF_VAPOUR) == "0.0 L vapour"


def test_the_withheld_panel_names_no_agent_and_no_amount_but_keeps_each_unit() -> None:
    for unit in AGENT_COST_VIEW_UNITS:
        assert WITHHELD_DELIVERED.amount_in(unit).startswith("— ")

    assert WITHHELD_DELIVERED.amount_in(AgentAmountUnit.MILLILITRES_OF_LIQUID).endswith(
        "mL of liquid"
    )
    assert WITHHELD_DELIVERED.amount_in(AgentAmountUnit.LITRES_OF_VAPOUR).endswith("L vapour")
    assert WITHHELD_DELIVERED.label == "Agent delivered"

    for agent_id in _DENSITY_AND_MOLAR_MASS:
        assert agent_id not in " ".join(WITHHELD_DELIVERED.captions).lower()


def test_the_selector_offers_the_units_the_preferences_accept_the_default_first() -> None:
    assert tuple(unit for unit, _ in UNIT_CHOICES) == AGENT_COST_VIEW_UNITS
    assert UNIT_CHOICES[0] == (AgentAmountUnit.MILLILITRES_OF_LIQUID, "millilitres of liquid")


def test_a_unit_the_view_does_not_offer_is_refused() -> None:
    shown = delivered_shown(SimulationController().snapshot())

    with pytest.raises(ValueError):
        shown.amount_in(AgentAmountUnit.MILLILITRES_OF_VAPOUR)

    with pytest.raises(ValueError):
        shown.caption_in(AgentAmountUnit.MILLILITRES_OF_VAPOUR)


def test_only_the_agent_cost_module_converts_vapour_to_liquid() -> None:
    """No other module under `src/` names `liquid_volume_ml`, so no caller pairs bare numbers.

    `liquid_volume_ml` takes a bare amount and a bare ratio. The agent cost
    module reads both from one snapshot, and converts only the delivered
    agent, which the conversion gives exactly (`PL-B396`). A second caller
    could convert the agent held in a compartment, which comes out 5.8 % too
    high, or pair one agent's vapour with another's ratio. This test makes that
    caller fail here first. It reads names, attributes and imported names, so
    an import under another name is found too. The module that defines the
    function is left out.
    """

    callers = []

    for path in sorted(_SRC.rglob("*.py")):
        if path == _SRC / "core" / "liquid_agent.py":
            continue

        tree = ast.parse(path.read_text(encoding="utf-8"))
        names = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                names.add(node.id)
            elif isinstance(node, ast.Attribute):
                names.add(node.attr)
            elif isinstance(node, ast.ImportFrom):
                names.update(alias.name for alias in node.names)

        if "liquid_volume_ml" in names:
            callers.append(path.relative_to(_SRC).as_posix())

    assert callers == ["app/agent_cost.py"]


@pytest.mark.parametrize(
    ("amount", "unit", "expected"),
    [
        (0.0, AgentAmountUnit.MILLILITRES_OF_LIQUID, "0.0 mL of liquid"),
        (0.04, AgentAmountUnit.MILLILITRES_OF_LIQUID, "<0.1 mL of liquid"),
        (0.06, AgentAmountUnit.MILLILITRES_OF_LIQUID, "0.1 mL of liquid"),
        (26.26, AgentAmountUnit.MILLILITRES_OF_LIQUID, "26.3 mL of liquid"),
        (240.0, AgentAmountUnit.MILLILITRES_OF_LIQUID, "240.0 mL of liquid"),
        (0.0, AgentAmountUnit.LITRES_OF_VAPOUR, "0.0 L vapour"),
        (0.04, AgentAmountUnit.LITRES_OF_VAPOUR, "<0.1 L vapour"),
        (4.8, AgentAmountUnit.LITRES_OF_VAPOUR, "4.8 L vapour"),
    ],
)
def test_the_delivered_agent_is_shown_to_a_tenth_with_its_unit_named(
    amount: float, unit: AgentAmountUnit, expected: str
) -> None:
    """A tenth is the precision `docs/MODEL.md` § "Displayed precision" derives in both units."""

    assert format_delivered_agent(amount, unit) == expected


@pytest.mark.parametrize("amount", [-0.1, float("nan"), float("inf")])
def test_a_negative_or_non_finite_delivered_amount_is_refused(amount: float) -> None:
    with pytest.raises(ValueError, match="must be finite and not negative"):
        format_delivered_agent(amount, AgentAmountUnit.MILLILITRES_OF_LIQUID)


def test_a_delivered_amount_that_is_not_a_number_or_has_no_unit_is_refused() -> None:
    with pytest.raises(TypeError, match="is a number"):
        format_delivered_agent(True, AgentAmountUnit.LITRES_OF_VAPOUR)

    with pytest.raises(TypeError, match="is an AgentAmountUnit"):
        format_delivered_agent(1.0, "mL")  # type: ignore[arg-type]


def test_a_unit_with_no_derived_precision_for_the_delivered_agent_is_refused() -> None:
    with pytest.raises(ValueError, match="No displayed precision is derived"):
        format_delivered_agent(1.0, AgentAmountUnit.MILLILITRES_OF_VAPOUR)


#: Gas Man's isoflurane price, as its parameter file holds it: US$20.47 for a
#: 100 mL bottle, "as of March 5, 2008" (Philip JH, *Workbook for Gas Man*,
#: Appendix C, printed p. 171, and printed p. 105).
_GAS_MAN_ISOFLURANE = AgentPrice("isoflurane", 20.47, 100.0, "USD", date(2008, 3, 5))


def _priced(*prices: AgentPrice) -> Preferences:
    preferences = Preferences()

    for price in prices:
        preferences = preferences.with_price(price)

    return preferences


def _shown_with_liquid(liquid_ml: float | None) -> DeliveredShown:
    """An isoflurane panel's values, with the unrounded liquid figure set directly."""

    return replace(delivered_shown(_run("isoflurane", 0.0, 1.0, 0.0)), liquid_ml=liquid_ml)


def test_the_cost_is_the_delivered_liquid_times_the_bottle_price_over_the_bottle_volume() -> None:
    """Gas Man's Exercise 14-1 to 13 min: 2 % isoflurane at 8 L/min, 2.08 L of vapour.

    The cost worked out here is 2080 / 195.8 x 20.47 / 100 = USD 2.17, which
    is the book's printed $2.17 (printed p. 133). The readout shows the
    figures it multiplied, the price they came from, words that say the price
    is the reader's, and that the figures are rounded.
    """

    snapshot = _run("isoflurane", 2.0, 8.0, 13.0)
    liquid_ml = 2.0 / 100.0 * 8.0 * 13.0 * 1000.0 / _vapour_ml_per_liquid_ml("isoflurane")
    expected_usd = liquid_ml * (20.47 / 100.0)
    cost = cost_shown(delivered_shown(snapshot), _priced(_GAS_MAN_ISOFLURANE))

    assert expected_usd == pytest.approx(2.17, abs=0.005)
    assert cost.cost == f"USD {expected_usd:.2f}"
    assert cost.label == "Cost of the delivered isoflurane, at your price"
    assert cost.working == (
        f"{liquid_ml:.1f} mL of liquid delivered x USD 0.2047 per mL of liquid"
    )
    assert cost.price == (
        "Your price, not one the project supplies: USD 20.47 per bottle of 100 mL of liquid, "
        "as of 2008-03-05."
    )
    assert cost.rounded == COST_ROUNDED_TEXT


def test_the_cost_is_computed_from_the_unrounded_figures_not_the_ones_shown() -> None:
    """`docs/MODEL.md`'s desflurane case: USD 115.13 per 240 mL, 6 % at 1 L/min for 60 min.

    The cost is 3600 / 209.7 x 115.13 / 240 = USD 8.23. The figures shown
    beside it, 17.2 mL and USD 0.4797 per mL, multiply to USD 8.25. So the
    readout says that the figures are rounded.
    """

    price = AgentPrice("desflurane", 115.13, 240.0, "USD", date(2026, 11, 1))
    snapshot = _run("desflurane", 6.0, 1.0, 60.0)
    liquid_ml = 3600.0 / _vapour_ml_per_liquid_ml("desflurane")
    cost = cost_shown(delivered_shown(snapshot), _priced(price))

    assert f"{liquid_ml * 115.13 / 240.0:.2f}" == "8.23"
    assert cost.cost == "USD 8.23"
    assert cost.working == "17.2 mL of liquid delivered x USD 0.4797 per mL of liquid"
    assert f"{17.2 * 0.4797:.2f}" == "8.25"
    assert cost.rounded == COST_ROUNDED_TEXT


def test_each_run_is_priced_at_its_own_agent_s_price() -> None:
    """Two prices in two currencies, so a price taken from the wrong agent cannot pass."""

    sevoflurane = AgentPrice("sevoflurane", 240.34, 250.0, "EUR", date(2026, 1, 2))
    preferences = _priced(_GAS_MAN_ISOFLURANE, sevoflurane)
    switched = SimulationController(agent_id="isoflurane")
    switched.set_agent("sevoflurane")
    switched.set_fresh_gas_flow(FreshGasFlow(4.0))
    switched.set_delivered_concentration_percent(Percent(2.0))
    switched.start()

    for _ in range(round(60.0 * _SECONDS_PER_MINUTE / SIMULATION_STEP_S)):
        switched.advance(SIMULATION_STEP_S)

    cost = cost_shown(delivered_shown(switched.snapshot()), preferences)
    liquid_ml = 4800.0 / _vapour_ml_per_liquid_ml("sevoflurane")

    assert cost.cost == f"EUR {liquid_ml * 240.34 / 250.0:.1f}"
    assert cost.cost == "EUR 25.2"
    assert "EUR 0.9614 per mL of liquid" in cost.working
    assert "sevoflurane" in cost.label
    assert "USD" not in " ".join((cost.cost, cost.working, cost.price))


def test_a_run_that_has_delivered_nothing_costs_zero_at_a_set_price() -> None:
    snapshot = SimulationController(agent_id="isoflurane").snapshot()

    cost = cost_shown(delivered_shown(snapshot), _priced(_GAS_MAN_ISOFLURANE))

    assert cost.cost == "USD 0"
    assert cost.working.startswith("0.0 mL of liquid delivered")


def test_no_cost_is_shown_until_the_reader_sets_a_price() -> None:
    """The project ships no price, so a reader with no preferences sees why, and no number."""

    cost = cost_shown(delivered_shown(_run("isoflurane", 2.0, 8.0, 13.0)), Preferences())

    assert cost.cost == NO_PRICE_TEXT.format(agent="isoflurane")
    assert not any(character.isdigit() for character in cost.cost)
    assert (cost.working, cost.price, cost.rounded) == ("", "", "")


def test_a_price_for_another_agent_prices_nothing() -> None:
    sevoflurane = AgentPrice("sevoflurane", 240.34, 250.0, "USD", date(2026, 1, 2))

    cost = cost_shown(delivered_shown(_run("isoflurane", 2.0, 8.0, 13.0)), _priced(sevoflurane))

    assert cost.cost == NO_PRICE_TEXT.format(agent="isoflurane")


def test_a_price_refused_when_the_file_was_read_is_named_and_never_replaced() -> None:
    refused = Preferences(
        refused_prices=(RefusedEntry({"agent": "isoflurane"}, "a reason", "isoflurane"),)
    )

    cost = cost_shown(delivered_shown(_run("isoflurane", 2.0, 8.0, 13.0)), refused)

    assert cost.cost == REFUSED_PRICE_TEXT.format(agent="isoflurane")
    assert cost.working == ""


@pytest.mark.parametrize(
    ("bottle_price", "bottle_volume_ml", "liquid_ml", "reason"),
    [
        pytest.param(1e308, 0.5, 26.0, PRICE_PER_ML_NOT_SHOWN_TEXT, id="price per mL overflows"),
        pytest.param(1e-300, 1e300, 26.0, PRICE_PER_ML_NOT_SHOWN_TEXT, id="price per mL is zero"),
        pytest.param(1e308, 1.0, 26.0, COST_NOT_COMPUTED_TEXT, id="cost overflows"),
        pytest.param(5e-324, 1.0, 0.4, COST_NOT_COMPUTED_TEXT, id="cost underflows to zero"),
        pytest.param(20.47, 100.0, None, COST_NOT_CONVERTED_TEXT, id="amount not converted"),
    ],
)
def test_no_cost_is_shown_where_one_cannot_be_trusted(
    bottle_price: float, bottle_volume_ml: float, liquid_ml: float | None, reason: str
) -> None:
    """Each case that `docs/MODEL.md` lists shows its reason and no number.

    § "A cost at the reader's price", under "When no cost is shown", lists
    them.
    """

    price = AgentPrice("isoflurane", bottle_price, bottle_volume_ml, "USD", date(2026, 1, 2))

    cost = cost_shown(_shown_with_liquid(liquid_ml), _priced(price))

    assert cost.cost == reason.format(agent="isoflurane")
    assert (cost.working, cost.price, cost.rounded) == ("", "", "")


def test_the_withheld_cost_names_no_agent_and_no_figure() -> None:
    cost = cost_shown(WITHHELD_DELIVERED, _priced(_GAS_MAN_ISOFLURANE))

    assert cost == WITHHELD_COST
    assert cost.cost == "\u2014"
    assert "isoflurane" not in cost.label


def test_a_price_entered_as_the_reader_types_it_is_read_exactly() -> None:
    price = price_from_entry("isoflurane", " 20.47 ", "100", "USD", date(2008, 3, 5))

    assert price == _GAS_MAN_ISOFLURANE


@pytest.mark.parametrize(
    ("bottle_price", "bottle_volume_ml", "currency", "message"),
    [
        pytest.param("20,47", "100", "USD", "at most one decimal point", id="decimal comma"),
        pytest.param("1,250", "100", "USD", "at most one decimal point", id="thousands separator"),
        pytest.param("-20", "100", "USD", "at most one decimal point", id="a sign"),
        pytest.param("2e1", "100", "USD", "at most one decimal point", id="an exponent"),
        pytest.param("", "100", "USD", "bottle price", id="an empty price"),
        pytest.param("20.47", "", "USD", "bottle volume", id="an empty volume"),
        pytest.param("0", "100", "USD", "positive", id="a price of zero"),
        pytest.param("20.47", "0.0", "USD", "positive", id="a volume of zero"),
        pytest.param("20.47", "100", "usd", "three capital letters", id="a lower-case code"),
        pytest.param("20.47", "100", "$", "three capital letters", id="a sign for the currency"),
    ],
)
def test_an_entry_that_is_not_a_plain_positive_price_is_refused_with_its_reason(
    bottle_price: str, bottle_volume_ml: str, currency: str, message: str
) -> None:
    with pytest.raises(SimulationConfigurationError, match=message):
        price_from_entry("isoflurane", bottle_price, bottle_volume_ml, currency, date(2026, 1, 2))
