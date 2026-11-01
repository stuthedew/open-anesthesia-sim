"""What the agent cost View shows for one run, checked against values worked out independently.

`app/agent_cost.py` turns a snapshot into the delivered agent in millilitres
of liquid equivalent and in litres of vapour (`PL-B396`). The expected values
here come from a closed form and from transcribed constants, never from the
conversion under test. The delivered vapour is the dial times the fresh gas
flow times the time. The vapour-to-liquid factor is worked out here from each
agent's liquid density at 20 °C and its molar mass, as `docs/MODEL.md`
§ "Agent amount" tabulates them (Laster, Fang and Eger's densities, and
formula masses), and from the ideal-gas molar volume at 20 °C and 1 atm,
written out from R.
"""

import ast
from pathlib import Path

import pytest

from anesthesia_sim.app.agent_cost import (
    NOT_CONVERTED_TEXT,
    UNIT_CHOICES,
    WITHHELD_DELIVERED,
    delivered_liquid_ml,
    delivered_shown,
)
from anesthesia_sim.app.controller import SimulationController, SimulationSnapshot
from anesthesia_sim.app.dashboard_frame import SIMULATION_STEP_S
from anesthesia_sim.app.formatting import AgentAmountUnit, format_delivered_agent
from anesthesia_sim.app.preferences import AGENT_COST_VIEW_UNITS
from anesthesia_sim.core.concentration import Percent
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
        f"{liquid_ml:.1f} mL liquid equiv."
    )
    assert shown.amount_in(AgentAmountUnit.LITRES_OF_VAPOUR) == f"{vapour_l:.1f} L vapour"


def test_sevoflurane_at_2_percent_and_4_l_min_for_an_hour_is_26_3_ml_of_liquid() -> None:
    """A worked case: 4.8 L of vapour is 4800 / 182.8 = 26.3 mL of liquid sevoflurane."""

    shown = delivered_shown(_run("sevoflurane", 2.0, 4.0, 60.0))

    assert shown.label == "Sevoflurane delivered"
    assert shown.amount_in(AgentAmountUnit.MILLILITRES_OF_LIQUID) == "26.3 mL liquid equiv."
    assert shown.amount_in(AgentAmountUnit.LITRES_OF_VAPOUR) == "4.8 L vapour"
    assert shown.instant == "1h"


def test_each_caption_names_its_unit_and_says_what_it_measures() -> None:
    shown = delivered_shown(_run("isoflurane", 1.2, 2.0, 1.0))
    liquid = shown.caption_in(AgentAmountUnit.MILLILITRES_OF_LIQUID)
    vapour = shown.caption_in(AgentAmountUnit.LITRES_OF_VAPOUR)

    assert liquid.startswith("mL liquid equiv.: the volume of liquid isoflurane")
    assert "20 degrees C" in liquid
    assert vapour.startswith("L vapour: pure isoflurane vapour at 20 degrees C and 1 atm")
    assert "the vaporizer's output" in liquid
    assert "the vaporizer's output" in vapour


def test_a_run_that_has_delivered_nothing_shows_zero_and_a_trace_shows_below_resolution() -> None:
    controller = SimulationController()
    start = delivered_shown(controller.snapshot())
    controller.start()
    controller.advance(SIMULATION_STEP_S)
    trace = delivered_shown(controller.snapshot())

    assert start.amount_in(AgentAmountUnit.MILLILITRES_OF_LIQUID) == "0.0 mL liquid equiv."
    assert start.amount_in(AgentAmountUnit.LITRES_OF_VAPOUR) == "0.0 L vapour"
    assert trace.amount_in(AgentAmountUnit.MILLILITRES_OF_LIQUID) == "<0.1 mL liquid equiv."
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
        "mL liquid equiv."
    )
    assert WITHHELD_DELIVERED.amount_in(AgentAmountUnit.LITRES_OF_VAPOUR).endswith("L vapour")
    assert WITHHELD_DELIVERED.label == "Agent delivered"

    for agent_id in _DENSITY_AND_MOLAR_MASS:
        assert agent_id not in " ".join(WITHHELD_DELIVERED.captions).lower()


def test_the_selector_offers_the_units_the_preferences_accept_the_default_first() -> None:
    assert tuple(unit for unit, _ in UNIT_CHOICES) == AGENT_COST_VIEW_UNITS
    assert UNIT_CHOICES[0] == (
        AgentAmountUnit.MILLILITRES_OF_LIQUID,
        "millilitres of liquid equivalent",
    )


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
        (0.0, AgentAmountUnit.MILLILITRES_OF_LIQUID, "0.0 mL liquid equiv."),
        (0.04, AgentAmountUnit.MILLILITRES_OF_LIQUID, "<0.1 mL liquid equiv."),
        (0.06, AgentAmountUnit.MILLILITRES_OF_LIQUID, "0.1 mL liquid equiv."),
        (26.26, AgentAmountUnit.MILLILITRES_OF_LIQUID, "26.3 mL liquid equiv."),
        (240.0, AgentAmountUnit.MILLILITRES_OF_LIQUID, "240.0 mL liquid equiv."),
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
