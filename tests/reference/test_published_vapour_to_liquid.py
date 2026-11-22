"""Compare the vapour-to-liquid conversion with published figures that it was not derived from.

`core/liquid_agent.py` derives each agent's millilitres of vapour per
millilitre of liquid from the stored liquid density and molar mass
(`PL-KZ99`). Two sources publish that ratio directly, and one of them also
publishes worked costs that depend on it. None of them supplied a stored
value, so each is an independent check:

- Biro 2014, which gives one ratio per agent, with no temperature stated in
  the abstract.
- The Gas Man Workbook, which gives one ratio per agent, rounded to a whole
  millilitre and stated at 20 °C.
- The Gas Man Workbook's Exercises 14-1 and 14-2, which print the cost of the
  isoflurane delivered in two hour-long anesthetics.

The last test checks the figures that `docs/PARAMETERS.md` § "Agent amount"
prints from these comparisons: its two tables, the ranges it states and the
sevoflurane example. It reads each published input from the section, as
`tests/reference/test_known_limitations_figures.py` does.

The tests import only the agent loader, the conversion and its physical
constants. `docs/ARCHITECTURE.md` § "Tests (`tests/`)" lets a test in this directory
import a parameter loader but not use a solver in `core/`. The conversion is a
closed-form expression, not a solver.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from anesthesia_sim.core import liquid_agent
from anesthesia_sim.core.liquid_agent import liquid_volume_ml
from anesthesia_sim.core.parameters import load_agent_parameters
from anesthesia_sim.core.units import LITRES_PER_CUBIC_METRE

# Biro P. Calculation of volatile anaesthetics consumption from agent
# concentration and fresh gas flow. Acta Anaesthesiol Scand. 2014;58(8):968-72.
# doi:10.1111/aas.12374. Abstract: "The amount of volatile agent vapour deriving
# from 1 ml of fluid agent are for halothane 229 ml, isoflurane 195 ml,
# sevoflurane 184 m[l], and desflurane 210 ml." Read from PubMed (PMID
# 25060161) on 2026-10-26, abstract only.
BIRO_2014_VAPOUR_ML_PER_LIQUID_ML = {"sevoflurane": 184.0, "isoflurane": 195.0, "desflurane": 210.0}

# Philip JH. Workbook for Gas Man. Chapter 10, printed p. 104: "Desflurane 1 mL
# liquid = 209 mL vapor ... Isoflurane 1 mL liquid = 196 mL vapor, Sevoflurane
# 1 mL liquid = 183 mL vapor". Appendix C, printed pp. 171-172, gives the same
# numbers under `Volatility`, "Vapor/Liquid volume ratio (20'C)". Read in full
# from the private reference corpus on 2026-10-26.
GAS_MAN_VAPOUR_ML_PER_LIQUID_ML = {"sevoflurane": 183.0, "isoflurane": 196.0, "desflurane": 209.0}

# Gas Man Workbook, Appendix C, printed p. 171: isoflurane "BottleCost=20.47",
# "BottleSize=100", a bottle price in US dollars and a bottle volume in mL.
# Chapter 14 says the exercises' costs "are based on a bottle cost of US$20.47
# per 100 ml" (printed p. 134).
GAS_MAN_ISOFLURANE_USD_PER_ML = 20.47 / 100.0

AGENTS = ("sevoflurane", "isoflurane", "desflurane")


@pytest.mark.parametrize("agent_id", AGENTS)
def test_the_derived_ratio_is_within_one_percent_of_biros_published_constant(agent_id: str) -> None:
    """Each derived ratio is within 1 % of Biro 2014's.

    The largest difference is sevoflurane's: 182.8 derived against 184
    published, 0.65 %. Biro's abstract states no temperature, so the test
    cannot tell whether the difference comes from the model or from Biro.

    This test detects an error of more than about 1 % in the ratio. That
    includes converting at 37 °C instead of 20 °C (5.8 % high), using the
    molar volume at 0 °C (6.8 % low), swapping the density and the molar
    mass, and a slip of a factor of ten or a thousand. It cannot detect a
    stored density or molar mass that is wrong by less than about 1 %. The
    tests in `tests/unit/test_parameters.py` that compare each stored value
    with its source cover that.
    """

    ratio = load_agent_parameters(agent_id).vapour_volume_per_liquid_volume

    assert ratio == pytest.approx(BIRO_2014_VAPOUR_ML_PER_LIQUID_ML[agent_id], rel=0.01)


@pytest.mark.parametrize("agent_id", AGENTS)
def test_the_derived_ratio_is_within_half_a_percent_of_gas_mans_20_celsius_constant(
    agent_id: str,
) -> None:
    """Each derived ratio is within 0.5 % of Gas Man's, which is stated at 20 °C.

    Gas Man rounds each ratio to a whole millilitre, which can change these
    ratios by up to 0.27 %. The sevoflurane and isoflurane differences are
    within that rounding: 182.8 against 183, and 195.8 against 196. Desflurane
    is 209.7 against 209, a difference of 0.35 %, which is more than rounding
    explains. The Workbook does not give the density it used, so the remaining
    0.1 % is recorded rather than explained (`docs/PARAMETERS.md` § "Agent amount").

    This test detects an error of more than about 0.5 % in the ratio. That
    includes every error that the comparison with Biro detects.
    """

    ratio = load_agent_parameters(agent_id).vapour_volume_per_liquid_volume

    assert ratio == pytest.approx(GAS_MAN_VAPOUR_ML_PER_LIQUID_ML[agent_id], rel=0.005)


@pytest.mark.parametrize(
    ("stretches", "printed_cost_usd"),
    [
        # Exercise 14-1, printed pp. 133-134, delivers isoflurane at 2 % and 8 L/min.
        # At 13 minutes "the delivered cost ... so far was $2.17". The vaporizer is
        # then set to 1.5 % until 60 minutes, for "a delivered cost of $8.06".
        pytest.param(((8.0, 2.0, 13.0),), 2.17, id="exercise 14-1 at 13 min"),
        pytest.param(((8.0, 2.0, 13.0), (8.0, 1.5, 47.0)), 8.06, id="exercise 14-1 at 60 min"),
        # Exercise 14-2, printed pp. 135-136, delivers isoflurane at 5 % and 1 L/min.
        # At 13 minutes "delivered cost so far was $0.68". The vaporizer is then
        # set to 2.7 % until 60 minutes: "At the end of 1 hour, delivered cost was $2.00".
        pytest.param(((1.0, 5.0, 13.0),), 0.68, id="exercise 14-2 at 13 min"),
        pytest.param(((1.0, 5.0, 13.0), (1.0, 2.7, 47.0)), 2.00, id="exercise 14-2 at 60 min"),
    ],
)
def test_the_conversion_reproduces_gas_mans_published_delivered_costs(
    stretches: tuple[tuple[float, float, float], ...], printed_cost_usd: float
) -> None:
    """This model's liquid volume reproduces Gas Man's printed costs for delivered isoflurane.

    The project owner asked on 2026-10-26 for a sanity check on a calculated
    price. This test applies that check to the part of the price that
    `PL-KZ99` builds, which converts delivered vapour into liquid. `PL-1P15`
    builds the price on screen and checks it end to end against the same
    four figures.

    Gas Man computes the delivered amount as "the product of fresh gas flow
    (FGF) and the vaporizer setting (DEL)" (Chapter 14, printed p. 132), and
    the cost as "DELIVERED Flow x Cost/mL vapor" (Appendix D, printed
    p. 174). So the test works out the delivered vapour by hand. Each stretch
    is a period of fixed flow and setting, given as its flow in L/min, its
    setting in percent and its length in minutes.

    The first assertion checks that the test reads the exercise correctly.
    With Gas Man's own ratio, 196, the calculation must give the printed cost
    to the cent. The second assertion checks this model's conversion. Gas
    Man's 196 is rounded to a whole millilitre, which can move a cost by up to
    0.26 %, and the printed cost is rounded to the cent. So the model's cost
    may differ from the printed one by that much. With this model's ratio,
    195.8, the two hour-long costs come out at $8.07 and $2.01.

    This test detects an error of more than about 0.3 % in the liquid volume
    at the largest cost, such as a reference temperature of 37 °C (5.8 %) or
    a molar volume at 0 °C (6.8 %).
    """

    delivered_vapour_l = sum(
        flow_l_min * setting_percent / 100.0 * minutes
        for flow_l_min, setting_percent, minutes in stretches
    )

    gas_man_cost_usd = delivered_vapour_l * 1000.0 / 196.0 * GAS_MAN_ISOFLURANE_USD_PER_ML
    assert round(gas_man_cost_usd, 2) == printed_cost_usd

    isoflurane = load_agent_parameters("isoflurane")
    liquid_ml = liquid_volume_ml(delivered_vapour_l, isoflurane.vapour_volume_per_liquid_volume)
    model_cost_usd = liquid_ml * GAS_MAN_ISOFLURANE_USD_PER_ML

    allowed_usd = 0.005 + printed_cost_usd * 0.5 / 196.0
    assert abs(model_cost_usd - printed_cost_usd) <= allowed_usd


PARAMETERS_PATH = Path(__file__).resolve().parents[2] / "docs" / "PARAMETERS.md"
AGENT_AMOUNT_HEADING = "## Agent amount"
BODY_TEMPERATURE_CELSIUS = 37.0
MILLILITRES_PER_LITRE = 1000.0

# The two agents in the section's Gas Man table that this model does not carry.
# Laster MJ, Fang Z, Eger EI. Specific gravities of desflurane, enflurane,
# halothane, isoflurane, and sevoflurane. Anesth Analg. 1994;78(6):1152-3.
# doi:10.1213/00000539-199406000-00022. Abstract: "enflurane 1.5230 +/- 0.0003
# g/mL (mean +/- SD); halothane 1.8680 +/- 0.0007 g/mL", at 20 degrees C. Read
# from PubMed (PMID 8198275) on 2026-11-22, abstract only. The molar masses are
# ChEMBL's full molecular weights for CHEMBL931 (halothane, C2HBrClF3) and
# CHEMBL1257 (enflurane, C3H2ClF5O), read through the ChEMBL connector on
# 2026-11-22.
UNCARRIED_AGENTS_DENSITY_AND_MOLAR_MASS = {
    "halothane": (1.8680, 197.38),
    "enflurane": (1.5230, 184.49),
}


def _agent_amount_text() -> str:
    """`docs/PARAMETERS.md` § "Agent amount", with each run of whitespace made one space."""

    text = PARAMETERS_PATH.read_text(encoding="utf-8")
    start = text.index(AGENT_AMOUNT_HEADING)
    end = text.find("\n## ", start + len(AGENT_AMOUNT_HEADING))

    return " ".join(text[start : end if end >= 0 else None].split())


def _printed(pattern: str) -> tuple[str, ...]:
    """The groups of the one match of `pattern` in the section, or a failure naming it."""

    # regex: a search for one sentence's or row's figures through the section's prose.
    matches = re.findall(pattern, _agent_amount_text())
    assert len(matches) == 1, f"the section matches {pattern!r} {len(matches)} times: {matches}"
    found = matches[0]

    return found if isinstance(found, tuple) else (found,)


def _places(value: float, printed: str) -> str:
    """`value` to as many decimal places as `printed` has."""

    places = len(printed.split(".")[1]) if "." in printed else 0

    return f"{value:.{places}f}"


def _molar_volume_l_mol(celsius: float) -> float:
    """V_m = R T / p at one standard atmosphere, in litres per mole."""

    kelvin = celsius + liquid_agent.CELSIUS_ZERO_K

    return (
        liquid_agent.MOLAR_GAS_CONSTANT_J_MOL_K
        * kelvin
        / liquid_agent.STANDARD_ATMOSPHERE_PA
        * LITRES_PER_CUBIC_METRE
    )


def _vapour_ml_per_liquid_ml(density_g_ml: float, molar_mass_g_mol: float, celsius: float) -> float:
    """Millilitres of vapour from 1 mL of liquid: density over molar mass times V_m."""

    return density_g_ml / molar_mass_g_mol * _molar_volume_l_mol(celsius) * MILLILITRES_PER_LITRE


def _signed_percent(derived: float, published: float) -> float:
    return (derived / published - 1.0) * 100.0


def test_the_agent_amount_section_prints_what_its_inputs_give() -> None:
    """Every figure in the section's two tables and its ranges follows from its inputs.

    The molar volumes are R T / p at 20 and 37 °C. Each derived ratio is the
    agent's density over its molar mass times a molar volume. The carried
    agents' densities and molar masses must be the stored ones, and their
    published constants must be the ones this module transcribed. Biro's and
    Gas Man's constants for the two agents this model does not carry are read
    from the section. A figure printed to more places than its inputs support,
    or one left behind when an input changed, fails at the decimals printed.
    """

    at_20 = _molar_volume_l_mol(20.0)
    at_37 = _molar_volume_l_mol(BODY_TEMPERATURE_CELSIUS)
    (printed_20,) = _printed(r"At that condition the ideal-gas molar volume is (\d+\.\d+) L/mol")
    printed_37, factor = _printed(
        r"molar volume is (\d+\.\d+) L/mol at 37 °C, so declaring 37 °C instead would change "
        r"each converted amount by a factor of (\d\.\d+)"
    )
    assert _places(at_20, printed_20) == printed_20
    assert at_20 == pytest.approx(liquid_agent.REFERENCE_MOLAR_VOLUME_L_MOL, rel=1e-12)
    assert _places(at_37, printed_37) == printed_37
    assert _places(at_37 / at_20, factor) == factor

    biro_gaps, biro_gaps_37 = [], []
    for agent_id in AGENTS:
        agent = load_agent_parameters(agent_id)
        density, molar_mass, derived_20, biro, derived_37 = _printed(
            rf"\| {agent_id.capitalize()} \| (\d\.\d+) \| (\d+\.\d+) \| (\d+\.\d) \| (\d+) \| "
            r"(\d+\.\d) \|"
        )
        assert float(density) == float(agent.liquid_density.g_ml)
        assert float(molar_mass) == float(agent.molar_mass_g_mol)
        assert float(biro) == BIRO_2014_VAPOUR_ML_PER_LIQUID_ML[agent_id]
        ratio_20 = _vapour_ml_per_liquid_ml(float(density), float(molar_mass), 20.0)
        ratio_37 = _vapour_ml_per_liquid_ml(
            float(density), float(molar_mass), BODY_TEMPERATURE_CELSIUS
        )
        assert _places(ratio_20, derived_20) == derived_20, f"{agent_id} at 20 °C: {ratio_20!r}"
        assert _places(ratio_37, derived_37) == derived_37, f"{agent_id} at 37 °C: {ratio_37!r}"
        biro_gaps.append(abs(_signed_percent(ratio_20, float(biro))))
        biro_gaps_37.append(_signed_percent(ratio_37, float(biro)))
    within, low, high = _printed(
        r"derivation reproduces all three within (\d\.\d) %\. At 37 °C it runs "
        r"(\d\.\d)–(\d\.\d) % high"
    )
    # "Within" is a bound, so the largest gap may round below it, but not exceed it.
    assert max(biro_gaps) <= float(within), f"the 20 °C gaps from Biro are {biro_gaps}"
    assert (_places(min(biro_gaps_37), low), _places(max(biro_gaps_37), high)) == (low, high)

    fewer, sevoflurane_20, sevoflurane_37 = _printed(
        r"print consumption figures (\d\.\d) % below the published ones\. .*? For sevoflurane, "
        r"1 L of vapour comes from (\d\.\d+) mL of liquid at 20 °C, and would come from "
        r"(\d\.\d+) mL at 37 °C"
    )
    sevoflurane = load_agent_parameters("sevoflurane")
    density_g_ml = float(sevoflurane.liquid_density.g_ml)
    molar_mass_g_mol = float(sevoflurane.molar_mass_g_mol)
    assert _places((1.0 - at_20 / at_37) * 100.0, fewer) == fewer
    for celsius, printed in ((20.0, sevoflurane_20), (BODY_TEMPERATURE_CELSIUS, sevoflurane_37)):
        millilitres = MILLILITRES_PER_LITRE / _vapour_ml_per_liquid_ml(
            density_g_ml, molar_mass_g_mol, celsius
        )
        assert _places(millilitres, printed) == printed, f"at {celsius} °C: {millilitres!r} mL"

    gas_man_gaps, gas_man_gaps_37 = [], []
    inputs = {
        agent_id: (
            float(load_agent_parameters(agent_id).liquid_density.g_ml),
            float(load_agent_parameters(agent_id).molar_mass_g_mol),
        )
        for agent_id in AGENTS
    } | UNCARRIED_AGENTS_DENSITY_AND_MOLAR_MASS
    for agent_id, (density_g_ml, molar_mass_g_mol) in inputs.items():
        gas_man, derived_20, gap_20, derived_37, gap_37 = _printed(
            rf"\| {agent_id.capitalize()} \| (\d+) \| (\d+\.\d) \(([−+]\d\.\d+) %\) \| "
            r"(\d+\.\d) \(\+(\d\.\d) %\) \|"
        )
        if agent_id in GAS_MAN_VAPOUR_ML_PER_LIQUID_ML:
            assert float(gas_man) == GAS_MAN_VAPOUR_ML_PER_LIQUID_ML[agent_id]
        ratio_20 = _vapour_ml_per_liquid_ml(density_g_ml, molar_mass_g_mol, 20.0)
        ratio_37 = _vapour_ml_per_liquid_ml(
            density_g_ml, molar_mass_g_mol, BODY_TEMPERATURE_CELSIUS
        )
        signed_20 = _signed_percent(ratio_20, float(gas_man))
        signed_37 = _signed_percent(ratio_37, float(gas_man))
        assert _places(ratio_20, derived_20) == derived_20, f"{agent_id} at 20 °C: {ratio_20!r}"
        assert _places(ratio_37, derived_37) == derived_37, f"{agent_id} at 37 °C: {ratio_37!r}"
        assert _places(signed_20, gap_20).replace("-", "−") == gap_20.replace("+", ""), (
            f"{agent_id}: {signed_20!r} % from Gas Man at 20 °C"
        )
        assert _places(signed_37, gap_37) == gap_37, f"{agent_id}: {signed_37!r} % at 37 °C"
        gas_man_gaps.append(abs(signed_20))
        gas_man_gaps_37.append(signed_37)
    within, low, high = _printed(
        r"printed vapour-to-liquid constants within (\d\.\d+) %, and the 37 °C derivation runs "
        r"(\d\.\d)–(\d\.\d) % high"
    )
    assert max(gas_man_gaps) <= float(within), f"the 20 °C gaps from Gas Man are {gas_man_gaps}"
    assert (_places(min(gas_man_gaps_37), low), _places(max(gas_man_gaps_37), high)) == (low, high)
