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

The tests import only the agent loader and the conversion.
`docs/ARCHITECTURE.md` § "Tests (`tests/`)" lets a test in this directory
import a parameter loader but not use a solver in `core/`. The conversion is a
closed-form expression, not a solver.
"""

from __future__ import annotations

import pytest

from anesthesia_sim.core.liquid_agent import liquid_volume_ml
from anesthesia_sim.core.parameters import load_agent_parameters

# Biro P. Calculation of volatile anaesthetics consumption from agent
# concentration and fresh gas flow. Acta Anaesthesiol Scand. 2014;58(8):968-72.
# doi:10.1111/aas.12374. Abstract: "The amount of volatile agent vapour deriving
# from 1 ml of fluid volatile agent are for halothane 229 ml, isoflurane 195 ml,
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
    0.1 % is recorded rather than explained (`docs/MODEL.md` § "Agent amount").

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
