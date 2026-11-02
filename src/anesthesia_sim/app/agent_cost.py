"""Compute what the agent cost View shows for one run: the agent it has delivered.

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
vapour converted with desflurane's ratio gives a result about 13 % too low. So
`delivered_liquid_ml` takes the snapshot, and reads the amount and the ratio
from that one record. The snapshot carries the ratio beside the agent it
belongs to (`SimulationSnapshot.agent_vapour_per_liquid`). No other module in
`app/` calls `liquid_volume_ml`, and a test checks that.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from anesthesia_sim.app.controller import SimulationSnapshot
from anesthesia_sim.app.dashboard_frame import WITHHELD_ELAPSED_TIME_TEXT
from anesthesia_sim.app.formatting import (
    AGENT_AMOUNT_UNIT_DISPLAY,
    AgentAmountUnit,
    format_delivered_agent,
    format_elapsed,
)
from anesthesia_sim.app.preferences import AGENT_COST_VIEW_UNITS
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.liquid_agent import liquid_volume_ml

__all__ = [
    "AGENT_COST_HEADING",
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
    """

    instant: str
    label: str
    amounts: tuple[str, ...]
    captions: tuple[str, ...]

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


def _liquid_text(snapshot: SimulationSnapshot) -> str:
    """Return the delivered liquid equivalent with its unit, or say it cannot be shown."""

    try:
        millilitres = delivered_liquid_ml(snapshot)
    except SimulationConfigurationError:
        return NOT_CONVERTED_TEXT

    return format_delivered_agent(millilitres, AgentAmountUnit.MILLILITRES_OF_LIQUID)


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

    amounts = {
        AgentAmountUnit.MILLILITRES_OF_LIQUID: _liquid_text(snapshot),
        AgentAmountUnit.LITRES_OF_VAPOUR: format_delivered_agent(
            snapshot.delivered_agent_l, AgentAmountUnit.LITRES_OF_VAPOUR
        ),
    }

    return DeliveredShown(
        format_elapsed(snapshot.elapsed_s),
        DELIVERED_LABEL_TEMPLATE.format(agent=snapshot.agent_display_name),
        tuple(amounts[unit] for unit in AGENT_COST_VIEW_UNITS),
        _captions(snapshot.agent_display_name.lower()),
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
)
