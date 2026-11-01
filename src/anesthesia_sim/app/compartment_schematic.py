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

from anesthesia_sim.app.controller import SimulationSnapshot
from anesthesia_sim.app.dashboard_frame import READOUT_PANELS, compartment_fraction
from anesthesia_sim.app.formatting import (
    chart_axis_top_percent,
    format_compartment_amount,
    format_percent,
)
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.core.concentration import percent_from_fraction

__all__ = ["ContainerReading", "container_readings"]


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
