"""Compute what the agent cost View shows for one run: the agent it has delivered, and its cost.

`ROADMAP.md` § "v0.7.0 - the schematic", entry 8, specifies the View
(`PL-B396`). It shows the delivered agent in millilitres of liquid equivalent
by default, or in litres of vapour if the reader chooses. The unit is printed
with the value, so a reader never has to remember which unit they picked. This
module turns one snapshot into the texts for both units. The View shows the one
the reader chose. Nothing here imports Qt.

**Why the delivered agent.** It is what left the vaporizer, and so it is what
left the bottle (`ROADMAP.md`, planned-milestone item 28, and `PL-H4N8`). The
model computes it as the vaporizer's setting times the fresh gas flow, summed
over the run, in litres of vapour (`docs/MODEL.md` § "Agent amount"). No
partition coefficient enters the calculation.

**Why the liquid figure is exact.** The delivered agent is gas at room
temperature, which is the model's reference condition of 20 °C. So
`core/liquid_agent.py` converts it to liquid exactly. The agent held in the
body is at body temperature, and the same conversion would give a figure 5.8 %
too high for it. This module therefore converts only the delivered agent, and
nothing else.

**Why the conversion takes a snapshot.** `liquid_volume_ml` takes a bare
volume of vapour and a bare ratio. Given those, a caller could convert one
agent's vapour with another agent's ratio after an agent change. Sevoflurane
vapour converted with desflurane's ratio gives a liquid figure about 13 % too
low. So `delivered_liquid_ml` takes the snapshot, and reads the amount and the
ratio from that one record. The snapshot carries the ratio beside the agent it
belongs to (`SimulationSnapshot.agent_vapour_per_liquid`). No other module in
`src/` calls `liquid_volume_ml`, and a test checks that.

**The cost at the reader's price** (`PL-1P15`). `docs/MODEL.md` § "A cost at
the reader's price" specifies it. The cost is the delivered liquid volume
times the price per millilitre of liquid. That price is the reader's bottle
price divided by the bottle volume (`AgentPrice.price_per_liquid_ml`). The
project ships no price, so for a run whose agent has no price, the readout
shows why there is no cost instead. `cost_shown` builds every line of the cost
readout from one `DeliveredShown` and one price record. So the cost and the
figures shown beside it cannot come from two different instants, agents or
prices. Beside the cost, the readout shows the two figures that were multiplied
to give it, the liquid volume and the price per millilitre. It also shows the
bottle price, bottle volume, currency and date that the price came from, and
words that say the price is the reader's. The cost is computed from the
unrounded figures, so the readout also says that the figures shown are rounded.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from math import isfinite
from typing import Final

from anesthesia_sim.app.controller import SimulationSnapshot
from anesthesia_sim.app.dashboard_frame import WITHHELD_ELAPSED_TIME_TEXT
from anesthesia_sim.app.display_units import DisplayUnit
from anesthesia_sim.app.formatting import (
    AGENT_AMOUNT_UNIT_DISPLAY,
    AgentAmountUnit,
    format_agent_cost,
    format_delivered_agent,
    format_elapsed,
    format_entered_figure,
    format_price_per_liquid_ml,
)
from anesthesia_sim.app.preferences import AGENT_COST_VIEW_UNITS, AgentPrice, Preferences
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.liquid_agent import liquid_volume_ml

__all__ = [
    "AGENT_COST_HEADING",
    "COST_LABEL_TEMPLATE",
    "COST_ROUNDED_TEXT",
    "WITHHELD_COST",
    "CostShown",
    "cost_shown",
    "price_from_entry",
    "DELIVERED_LABEL_TEMPLATE",
    "LIQUID_CAPTION_TEMPLATE",
    "NOT_CONVERTED_TEXT",
    "UNIT_CHOICE_LABEL",
    "UNIT_CHOICES",
    "VAPOUR_CAPTION_TEMPLATE",
    "WITHHELD_AGENT_NAME",
    "WITHHELD_DELIVERED",
    "DeliveredShown",
    "delivered_liquid_ml",
    "delivered_shown",
]

#: The View's heading. The wording is a placeholder.
AGENT_COST_HEADING: Final = "Vaporizer output"

#: How the label and the captions name the agent while the values are withheld.
WITHHELD_AGENT_NAME: Final = "Agent"

#: The label over the delivered amount. It names the agent, because the
#: amount means nothing without it. The wording is a placeholder.
DELIVERED_LABEL_TEMPLATE: Final = "{agent} delivered"

#: The caption that says what the liquid figure measures. The figure comes from the liquid
#: agent that the vaporizer used, and the caption says so. The wording is a placeholder, but
#: what the caption must say is not (`PL-B396`).
LIQUID_CAPTION_TEMPLATE: Final = "Liquid used by the vaporizer, at 20 degrees C."

#: What the vapour figure is. The wording is a placeholder.
VAPOUR_CAPTION_TEMPLATE: Final = "Vapour put out by the vaporizer, at 20 degrees C and 1 atm."

#: What the View shows in place of a liquid figure that cannot be computed.
#: The conversion fails only on a ratio or an amount that is not finite, which
#: no supported run produces. The wording is a placeholder.
NOT_CONVERTED_TEXT: Final = "Cannot show this as liquid: the conversion did not give a finite value"

#: The label of the View's unit selector, and the name of each unit in it, in
#: the order `AGENT_COST_VIEW_UNITS` lists them. The wording is a placeholder.
UNIT_CHOICE_LABEL: Final = "Show as"
UNIT_CHOICES: Final[tuple[tuple[AgentAmountUnit, str], ...]] = tuple(
    (unit, name)
    for unit, name in zip(
        AGENT_COST_VIEW_UNITS, ("millilitres of liquid", "litres of vapour"), strict=True
    )
)


@dataclass(frozen=True, slots=True)
class DeliveredShown:
    """What one run's agent cost panel shows, in each unit the reader can choose.

    Attributes:
        instant: The simulated instant the values are for, as the clock
            prints it.
        label: The line over the amount, which names the agent.
        amounts: The delivered amount in each unit of `AGENT_COST_VIEW_UNITS`,
            with the unit named on it, in that order.
        captions: What each amount is, in the same order.
        agent_id: The agent the run delivered, or None while the values are
            withheld. The cost readout uses it to look up the reader's price.
        agent_name: The agent's display name in lower case, as the captions
            print it.
        liquid_ml: The delivered agent in millilitres of liquid, unrounded,
            or None when it could not be converted or is withheld. The cost
            is computed from it, never from the rounded text.
    """

    instant: str
    label: str
    amounts: tuple[str, ...]
    captions: tuple[str, ...]
    agent_id: str | None
    agent_name: str
    liquid_ml: float | None

    def amount_in(self, unit: AgentAmountUnit) -> str:
        """Return the delivered amount in `unit`, with the unit named on it.

        Raises:
            ValueError: If `unit` is not one of `AGENT_COST_VIEW_UNITS`.
        """

        return self.amounts[AGENT_COST_VIEW_UNITS.index(unit)]

    def caption_in(self, unit: AgentAmountUnit) -> str:
        """Return what the amount in `unit` is.

        Raises:
            ValueError: If `unit` is not one of `AGENT_COST_VIEW_UNITS`.
        """

        return self.captions[AGENT_COST_VIEW_UNITS.index(unit)]


def delivered_liquid_ml(snapshot: SimulationSnapshot) -> float:
    """Return the millilitres of liquid agent that the run's delivered vapour came from.

    The amount and the ratio are read from the one snapshot, so they belong to
    the same agent. The result is exact, because the delivered agent is gas at
    20 °C (the module docstring says why).

    Raises:
        SimulationConfigurationError: As `liquid_volume_ml` raises it, for an
            amount or a ratio that is negative or not finite.
        TypeError: As `liquid_volume_ml` raises it.
    """

    return liquid_volume_ml(snapshot.delivered_agent_l, snapshot.agent_vapour_per_liquid)


def _converted_liquid_ml(snapshot: SimulationSnapshot) -> float | None:
    """Return the delivered liquid equivalent, or None when it cannot be converted."""

    try:
        return delivered_liquid_ml(snapshot)
    except SimulationConfigurationError:
        return None


def _captions(agent: str) -> tuple[str, ...]:
    """Return what each unit's amount is, for `agent`, in the order of `AGENT_COST_VIEW_UNITS`."""

    templates = {
        AgentAmountUnit.MILLILITRES_OF_LIQUID: LIQUID_CAPTION_TEMPLATE,
        AgentAmountUnit.LITRES_OF_VAPOUR: VAPOUR_CAPTION_TEMPLATE,
    }

    return tuple(
        templates[unit].format(unit=AGENT_AMOUNT_UNIT_DISPLAY[unit].label, agent=agent)
        for unit in AGENT_COST_VIEW_UNITS
    )


def delivered_shown(snapshot: SimulationSnapshot) -> DeliveredShown:
    """Return what one run's agent cost panel shows for `snapshot`.

    Raises:
        TypeError: As `format_delivered_agent` raises it.
        ValueError: As `format_delivered_agent` raises it, for a delivered
            amount that is negative or not finite. The model never produces
            one, so such an amount is a defect, and the run halts rather than
            show a plausible number.
    """

    liquid_ml = _converted_liquid_ml(snapshot)
    amounts = {
        AgentAmountUnit.MILLILITRES_OF_LIQUID: (
            NOT_CONVERTED_TEXT
            if liquid_ml is None
            else format_delivered_agent(liquid_ml, AgentAmountUnit.MILLILITRES_OF_LIQUID)
        ),
        AgentAmountUnit.LITRES_OF_VAPOUR: format_delivered_agent(
            snapshot.delivered_agent_l, AgentAmountUnit.LITRES_OF_VAPOUR
        ),
    }

    agent_name = snapshot.agent_display_name.lower()

    return DeliveredShown(
        format_elapsed(snapshot.elapsed_s),
        DELIVERED_LABEL_TEMPLATE.format(agent=snapshot.agent_display_name),
        tuple(amounts[unit] for unit in AGENT_COST_VIEW_UNITS),
        _captions(agent_name),
        snapshot.agent_id,
        agent_name,
        liquid_ml,
    )


#: What the panel shows while the run's values are withheld. They are withheld
#: after a Reset or an agent change, until a frame has drawn the new state. The
#: panel names no agent and no amount, because either could belong to the run
#: that was discarded. Each unit is still named, so the reader's choice of unit
#: stays visible.
WITHHELD_DELIVERED: Final = DeliveredShown(
    WITHHELD_ELAPSED_TIME_TEXT,
    DELIVERED_LABEL_TEMPLATE.format(agent=WITHHELD_AGENT_NAME),
    tuple(f"\u2014 {AGENT_AMOUNT_UNIT_DISPLAY[unit].label}" for unit in AGENT_COST_VIEW_UNITS),
    _captions(WITHHELD_AGENT_NAME.lower()),
    None,
    WITHHELD_AGENT_NAME.lower(),
    None,
)


#: The line over the cost. It says in words that the price is the reader's,
#: not only through a colour or a style, so that no reader misses the statement
#: (`docs/MODEL.md` § "A cost at the reader's price", item 6). The wording is a
#: placeholder, but what it must say is not.
COST_LABEL_TEMPLATE: Final = "Cost of the {agent}, at your price"

#: The calculation shown beside the cost, which is the liquid volume times the
#: price per millilitre. The volume is always shown in liquid equivalent, even
#: when the reader has chosen litres of vapour for the View's amounts, because
#: the cost is computed from that figure (item 1). The wording is a placeholder.
COST_WORKING_TEMPLATE: Final = "{volume} x {price_per_ml}"

#: Where the price per millilitre came from. The wording is a placeholder.
COST_PRICE_TEMPLATE: Final = (
    "Your price: {currency} {bottle_price} for {bottle_volume} {unit}, as of {applies_on}."
)

#: Why the figures beside a cost may not multiply to it. The cost is computed
#: from the unrounded volume and price, so the product of the rounded figures
#: can differ from it (`docs/MODEL.md` § "Displayed precision" says by how much).
#: The wording is a placeholder.
COST_ROUNDED_TEXT: Final = "Rounded, so the figures may not multiply exactly."

#: Why no cost is shown, in each case that `docs/MODEL.md` § "A cost at the
#: reader's price" lists. The wording is a placeholder.
NO_PRICE_TEXT: Final = "No cost: set your price for {agent} below."
REFUSED_PRICE_TEXT: Final = "No cost: your saved price for {agent} was refused. Set it again below."
PRICE_PER_ML_NOT_SHOWN_TEXT: Final = (
    "No cost: your bottle price and volume for {agent} do not give a usable price per mL."
)
COST_NOT_COMPUTED_TEXT: Final = (
    "No cost: the cost of the {agent} is too large or too small to compute."
)
COST_NOT_CONVERTED_TEXT: Final = "No cost: the {agent} could not be converted to liquid."


@dataclass(frozen=True, slots=True)
class CostShown:
    """What one run's cost readout shows, which is a cost and its calculation or why there is none.

    Attributes:
        label: The line over the cost, which says the price is the reader's.
        cost: The cost with its currency code, or the reason no cost is
            shown.
        working: The liquid volume times the price per millilitre, or ""
            when no cost is shown.
        price: The bottle price, bottle volume, currency and date that the
            price per millilitre came from, or "" when no cost is shown.
        rounded: `COST_ROUNDED_TEXT` when a cost is shown, or "" when none is.
    """

    label: str
    cost: str
    working: str
    price: str
    rounded: str


#: What the cost readout shows while the run's values are withheld. It names no
#: agent and no figure, because each could belong to the run that was discarded.
WITHHELD_COST: Final = CostShown(
    COST_LABEL_TEMPLATE.format(agent=WITHHELD_AGENT_NAME.lower()), "\u2014", "", "", ""
)


def _no_cost(delivered: DeliveredShown, reason: str) -> CostShown:
    """Return a readout that shows `reason`, formatted for the run's agent, and no cost."""

    return CostShown(
        COST_LABEL_TEMPLATE.format(agent=delivered.agent_name),
        reason.format(agent=delivered.agent_name),
        "",
        "",
        "",
    )


def cost_shown(delivered: DeliveredShown, preferences: Preferences) -> CostShown:
    """Return what the cost readout shows for one run, at the reader's price for its agent.

    The price is the one stored for the agent that `delivered` is for, so a
    run after an agent change is priced at the new agent's price. Every line
    is built from `delivered` and that one price record. The readout shows no
    cost when the run has no valid price, when the price per millilitre or the
    cost is not a positive finite number, or when the delivered agent could
    not be converted to liquid. In each of these cases, it says why. A cost of
    zero is shown only for a run that has delivered no agent.

    Args:
        delivered: What the run's panel shows, from one snapshot.
        preferences: The reader's preferences, which hold the prices.

    Returns:
        The lines of the cost readout.
    """

    agent_id = delivered.agent_id

    if agent_id is None:
        return WITHHELD_COST

    price = preferences.price_for(agent_id)

    if price is None:
        refused = any(entry.agent_id == agent_id for entry in preferences.refused_prices)
        return _no_cost(delivered, REFUSED_PRICE_TEXT if refused else NO_PRICE_TEXT)

    if delivered.liquid_ml is None:
        return _no_cost(delivered, COST_NOT_CONVERTED_TEXT)

    price_per_ml = price.price_per_liquid_ml

    if not isfinite(price_per_ml) or price_per_ml <= 0.0:
        return _no_cost(delivered, PRICE_PER_ML_NOT_SHOWN_TEXT)

    cost = delivered.liquid_ml * price_per_ml

    # A product of two positive finite floats can overflow to infinity, or
    # underflow to zero, which would show a run that has delivered agent as
    # costing nothing.
    if not isfinite(cost) or (cost == 0.0 and delivered.liquid_ml > 0.0):
        return _no_cost(delivered, COST_NOT_COMPUTED_TEXT)

    return CostShown(
        COST_LABEL_TEMPLATE.format(agent=delivered.agent_name),
        format_agent_cost(cost, price.currency),
        COST_WORKING_TEMPLATE.format(
            volume=delivered.amount_in(AgentAmountUnit.MILLILITRES_OF_LIQUID),
            price_per_ml=format_price_per_liquid_ml(price_per_ml, price.currency),
        ),
        COST_PRICE_TEMPLATE.format(
            currency=price.currency,
            bottle_price=format_entered_figure(price.bottle_price),
            bottle_volume=format_entered_figure(price.bottle_volume_ml),
            unit=DisplayUnit.AGENT_LIQUID_MILLILITRES.label,
            applies_on=price.applies_on.isoformat(),
        ),
        COST_ROUNDED_TEXT,
    )


# A figure that the reader types into the price entry may hold only digits,
# with at most one decimal point. A sign, an exponent, a thousands separator
# or a decimal comma is refused rather than guessed at, because "1,250" could
# mean 1250 or 1.25 (`PL-1P15`).
_ENTERED_FIGURE_PATTERN: Final = re.compile(r"[0-9]+(\.[0-9]*)?|\.[0-9]+")


def _entered_figure(text: str, what: str) -> float:
    """Return the number the reader typed for `what`.

    Raises:
        SimulationConfigurationError: If `text`, without surrounding spaces,
            is not digits with at most one decimal point.
    """

    figure = text.strip()

    if _ENTERED_FIGURE_PATTERN.fullmatch(figure) is None:
        raise SimulationConfigurationError(
            f"write the {what} as a number with digits and at most one decimal point, such as "
            f"20.47, not {text!r}"
        )

    return float(figure)


def price_from_entry(
    agent_id: str, bottle_price: str, bottle_volume_ml: str, currency: str, applies_on: date
) -> AgentPrice:
    """Return the price the reader entered, or refuse it with the reason.

    The texts are as the reader typed them. `AgentPrice` then applies every
    check that `docs/MODEL.md` § "A cost at the reader's price" lists, the
    same checks it applies when the preferences file is read. A refused entry
    changes nothing, so the stored price, if any, stays in force.

    Raises:
        SimulationConfigurationError: If a figure is not a plain number, or
            if `AgentPrice` refuses the price. The message says which field
            and why.
    """

    return AgentPrice(
        agent_id,
        _entered_figure(bottle_price, "bottle price"),
        _entered_figure(bottle_volume_ml, "bottle volume"),
        currency.strip(),
        applies_on,
    )
