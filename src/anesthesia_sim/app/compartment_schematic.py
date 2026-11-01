"""What each container of the compartment schematic is filled to and labelled with.

`docs/MODEL.md` § "The compartment schematic: what its heights, amounts and
share bar assert" specifies the schematic (`PL-2881`). This module turns one
snapshot into one reading per container, and the View draws the readings
(`PL-RNYV`). Nothing here imports Qt, so every number a reader interprets is
computed and tested apart from the drawing.

A container's fill is the compartment's tension on the concentration chart's
own scale, from zero to `chart_axis_top_percent`. It is not an amount. A
tension above that top fills the container and is marked off the scale, and
the label still prints the tension. Each label is the compartment's name, its
tension as its readout prints it, and its amount from the snapshot's record of
each compartment's agent (`PL-KFTM`). So a label and a readout cannot disagree,
and the schematic computes no amount of its own.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from anesthesia_sim.app.chart_frame import percent_axis_ticks
from anesthesia_sim.app.controller import SimulationSnapshot
from anesthesia_sim.app.dashboard_frame import (
    READOUT_PANELS,
    WIDEST_COMPARTMENT_VALUE,
    compartment_fraction,
)
from anesthesia_sim.app.display_units import DisplayUnit
from anesthesia_sim.app.formatting import (
    CHART_AXIS_TOP_MAC,
    MAC_UNIT_SUFFIX,
    chart_axis_top_percent,
    chart_grid_interval_percent,
    format_compartment_amount,
    format_percent,
)
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.core.concentration import percent_from_fraction

__all__ = [
    "CONTAINER_ORDER",
    "OFF_SCALE_LINE_TEMPLATE",
    "SCALE_CAPTION_TEMPLATE",
    "SCHEMATIC_HEADING",
    "WIDEST_LABELS",
    "ContainerReading",
    "container_readings",
    "off_scale_line",
    "scale_caption",
]

#: The compartments the schematic draws, in the order its containers stand:
#: the readout row's order, read from the readout panels so the two cannot
#: disagree.
CONTAINER_ORDER: Final[tuple[RecordedQuantity, ...]] = tuple(
    panel.quantity for panel in READOUT_PANELS if panel.quantity is not None
)

#: The schematic's heading. The wording is a placeholder.
SCHEMATIC_HEADING: Final = "Where the agent is: each compartment's tension and amount"

#: The caption that says what a container's height means. A height is a
#: tension on the concentration chart's scale, so the caption names that scale
#: and says that a height is not an amount (`docs/MODEL.md` § "The compartment
#: schematic: what its heights, amounts and share bar assert"). It is two lines
#: rather than one wrapped line, because Qt does not count a wrapped label's
#: extra lines in the least size a View declares, and the containers' labels
#: would then lose the room their amounts are printed in. The wording is a
#: placeholder; what it must say is not.
SCALE_CAPTION_TEMPLATE: Final = (
    "Fill height is tension, on the concentration chart's scale: 0 to {top}{unit} ({top_mac}).\n"
    "A container's height is its tension, not its amount of agent."
)

#: The lines naming the containers whose tension is above the top of the scale.
#: Each such container is drawn full and marked, and its label still prints its
#: tension. The lines say so in words, so the mark is never read by colour or
#: shape alone. Two lines, for the reason the scale caption gives. The wording
#: is a placeholder.
OFF_SCALE_LINE_TEMPLATE: Final = (
    "Above the top of the scale: {compartments}.\n"
    "Each is drawn full, and its label gives its tension."
)

#: The label texts whose width each container's column reserves, so that a
#: column does not widen while a run fills. A tension is reserved as the
#: readouts reserve it. An amount is reserved at the floor's form and at a
#: five-figure amount, each written by the formatter that prints it. The View
#: also widens a column for any label wider than these, so none is clipped.
WIDEST_LABELS: Final[tuple[str, ...]] = (
    *(panel.name for panel in READOUT_PANELS if panel.quantity is not None),
    WIDEST_COMPARTMENT_VALUE,
    format_compartment_amount(1e-9),
    format_compartment_amount(88.0),
)


@dataclass(frozen=True, slots=True)
class ContainerReading:
    """One container of the schematic, as one snapshot fills and labels it.

    Attributes:
        quantity: The compartment the container stands for.
        name: The compartment's name, as its readout panel names it.
        fill: The share of the container's height that is filled, from 0 to
            1. It is the tension over the chart's axis top, and it is 1 for a
            tension above the top.
        off_scale: Whether the tension is above the chart's axis top. The
            View then marks the container as off the scale.
        tension: The tension, written as the compartment's readout writes it.
        amount: The compartment's agent, in millilitres of vapour.
    """

    quantity: RecordedQuantity
    name: str
    fill: float
    off_scale: bool
    tension: str
    amount: str


def container_readings(snapshot: SimulationSnapshot) -> tuple[ContainerReading, ...]:
    """Return one reading per container, in the order in which agent reaches the compartments.

    The order and the names are the readout panels' own, so the schematic and
    the readout row list the six compartments alike. Every container of the
    run fills against one top, read once from this snapshot's MAC, so two
    containers can never be drawn against two agents' scales.

    Args:
        snapshot: The run's state at the instant drawn.

    Returns:
        Six readings: the circuit, the alveoli, venous blood, the vessel-rich
        group, muscle and fat.

    Raises:
        TypeError: If the snapshot's `agent_mac_percent` was not built as a
            `MacPercent` (`chart_axis_top_percent`).
        ValueError: If a compartment's recorded amount is negative or not
            finite (`format_compartment_amount`).
    """

    top_percent = chart_axis_top_percent(snapshot.agent_mac_percent)
    readings: list[ContainerReading] = []

    for panel in READOUT_PANELS:
        if panel.quantity is None:
            continue

        fraction = compartment_fraction(snapshot, panel.quantity)
        height = percent_from_fraction(fraction) / top_percent
        readings.append(
            ContainerReading(
                quantity=panel.quantity,
                name=panel.name,
                fill=min(height, 1.0),
                off_scale=height > 1.0,
                tension=format_percent(fraction),
                amount=format_compartment_amount(
                    snapshot.compartment_agent_amounts.of(panel.quantity)
                ),
            )
        )

    return tuple(readings)


def scale_caption(snapshot: SimulationSnapshot) -> str:
    """Return the caption naming the scale that every container of this run fills against.

    The top is written as the concentration chart labels its own top
    gridline (`percent_axis_ticks`), so the caption and the chart's axis
    cannot print the same scale two ways.

    Raises:
        TypeError: If the snapshot's `agent_mac_percent` was not built as a
            `MacPercent` (`chart_axis_top_percent`).
    """

    mac_percent = snapshot.agent_mac_percent
    ticks = percent_axis_ticks(
        chart_axis_top_percent(mac_percent), chart_grid_interval_percent(mac_percent)
    )

    return SCALE_CAPTION_TEMPLATE.format(
        top=ticks[-1][1],
        unit=DisplayUnit.CONCENTRATION.axis_title,
        top_mac=f"{CHART_AXIS_TOP_MAC:g}{MAC_UNIT_SUFFIX}",
    )


def off_scale_line(readings: tuple[ContainerReading, ...]) -> str | None:
    """Return the line naming each container above the scale, or None when none is above it."""

    above = [reading.name for reading in readings if reading.off_scale]

    if not above:
        return None

    return OFF_SCALE_LINE_TEMPLATE.format(compartments=", ".join(above))
