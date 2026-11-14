"""Compute how each container of the compartment schematic is filled and labelled.

`docs/INTERFACE.md` § "The compartment schematic: what its heights, amounts and
share bar assert" specifies the schematic (`PL-2881`). This module turns one
snapshot into one reading per container. A reading says how full the container
is and what its label prints. The schematic's View draws the readings
(`PL-RNYV`). Nothing here imports Qt, so every number a reader interprets is
computed and tested apart from the drawing.

A container's fill is the compartment's tension, on the concentration chart's
own scale, from zero to `chart_axis_top_percent`. The fill is not an amount. A
tension above the top of that scale fills the container, and the container is
marked as off the scale. Its label still prints the tension. Each label gives
the compartment's name, its tension as its readout prints it, and its amount.
The amount comes from the snapshot's record of the agent in each compartment
(`PL-KFTM`). So a label cannot disagree with its readout, and the schematic
computes no amount of its own.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Final

from anesthesia_sim.app.chart_frame import percent_axis_ticks
from anesthesia_sim.app.controller import SimulationSnapshot
from anesthesia_sim.app.dashboard_frame import (
    READOUT_PANELS,
    WIDEST_COMPARTMENT_VALUE,
    WITHHELD_CONCENTRATION_TEXT,
    WITHHELD_ELAPSED_TIME_TEXT,
    above_the_axis_top,
    compartment_fraction,
)
from anesthesia_sim.app.display_units import (
    BODY_STORES_CONDITION_LINES,
    REFERENCE_CONDITION_LABEL,
    DisplayUnit,
)
from anesthesia_sim.app.formatting import (
    CHART_AXIS_TOP_MAC,
    MAC_UNIT_SUFFIX,
    chart_axis_top_percent,
    chart_grid_interval_percent,
    format_compartment_amount,
    format_compartment_share,
    format_elapsed,
    format_percent,
)
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.core.concentration import percent_from_fraction

__all__ = [
    "COMPARED_INSTANT_LINE_TEMPLATE",
    "CONTAINER_ORDER",
    "INSTANT_LINE_TEMPLATE",
    "OFF_SCALE_LINE_TEMPLATE",
    "AMOUNT_CONDITION_LINES",
    "SCALE_CAPTION_TEMPLATE",
    "SCHEMATIC_HEADING",
    "SHARE_LINE_TEMPLATE",
    "SHARE_SEGMENT_TEMPLATE",
    "NO_AGENT_SHARE_LINE",
    "WIDEST_LABELS",
    "WITHHELD_AMOUNT_TEXT",
    "WITHHELD_SCHEMATIC",
    "ContainerReading",
    "SchematicShown",
    "ShareSegment",
    "container_readings",
    "instant_line",
    "schematic_shown",
    "off_scale_line",
    "scale_caption",
    "share_line",
    "share_segments",
]

#: The compartments the schematic draws, in the order its containers stand:
#: the readout row's order, read from the readout panels so the two cannot
#: disagree.
CONTAINER_ORDER: Final[tuple[RecordedQuantity, ...]] = tuple(
    panel.quantity for panel in READOUT_PANELS if panel.quantity is not None
)

#: The line over each run's schematic: the run's name while runs are compared,
#: and the instant it shows. The wording is a placeholder.
INSTANT_LINE_TEMPLATE: Final = "At {instant} of simulated time"
COMPARED_INSTANT_LINE_TEMPLATE: Final = "{run}, at {instant} of simulated time"

#: The schematic's heading. The wording is a placeholder.
SCHEMATIC_HEADING: Final = "Where the agent is: each compartment's tension and amount"

#: The caption that says what a container's height means. A height is a
#: tension on the concentration chart's scale. So the caption names that scale
#: and says that a height is not an amount (`docs/INTERFACE.md` § "The compartment
#: schematic: what its heights, amounts and share bar assert"). The caption is
#: two lines rather than one wrapped line. Qt leaves a wrapped label's extra
#: lines out of the minimum size that a View declares, so the containers'
#: labels would lose the room in which their amounts are printed. The wording
#: is a placeholder, but what the caption must say is not.
SCALE_CAPTION_TEMPLATE: Final = (
    "Fill height is tension, on the concentration chart's scale: 0 to {top}{unit} ({top_mac}).\n"
    "A container's height is its tension, not its amount of agent."
)

#: The lines under the scale caption that name the unit of the amounts and the
#: temperature and pressure they are stated at, once for every container
#: (`PL-HQPF`). Five of the six containers hold agent in the body, so the second
#: line says that their amounts read high at that condition. The lines are
#: explicit for the same reason as the scale caption's. The wording is a
#: placeholder, but the condition and its effect must be on screen.
AMOUNT_CONDITION_LINES: Final = (
    f"Amounts are {DisplayUnit.AGENT_VAPOUR_MILLILITRES.recorded} at {REFERENCE_CONDITION_LABEL}.\n"
    f"{BODY_STORES_CONDITION_LINES}"
)

#: The lines that name the containers whose tension is above the top of the
#: scale. Each such container is drawn full and marked, and its label still
#: prints its tension. The lines say this in words, so that a reader never has
#: to tell an off-scale container by colour or shape alone. The text is two
#: lines for the same reason as the scale caption. The wording is a placeholder.
OFF_SCALE_LINE_TEMPLATE: Final = (
    "Above the top of the scale: {compartments}.\n"
    "Each is drawn full, and its label gives its tension."
)

#: The label texts that set the width of each container's column, so that a
#: column does not widen while a run fills. Room for a tension is reserved in the
#: same way as the readouts reserve it. Room for an amount is reserved for two
#: texts: an amount below the display floor, and a five-figure amount. The
#: formatter that prints amounts writes both texts. The View also widens a
#: column for any label wider than these, so that no label is clipped.
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
        quantity: The compartment that the container stands for.
        name: The compartment's name, as its readout panel names it.
        fill: The share of the container's height that is filled, from 0 to
            1. It is the tension divided by the top of the chart's axis, and
            it is 1 for a tension above the top.
        off_scale: Whether the tension is above the top of the chart's axis
            by more than the smallest step that the readouts show. The test is
            `above_the_axis_top`, the same one that the chart's off-scale
            notice uses. When it is true, the View marks the container as off
            the scale.
        tension: The tension, written as the compartment's readout writes it.
        amount: The amount of agent in the compartment, written in millilitres
            of vapour.
    """

    quantity: RecordedQuantity
    name: str
    fill: float
    off_scale: bool
    tension: str
    amount: str


def container_readings(snapshot: SimulationSnapshot) -> tuple[ContainerReading, ...]:
    """Return one reading per container, in the readout row's order.

    The schematic uses the readout panels' own order and names, so the
    schematic and the readout row list the six compartments in the same way.
    Every container of the run fills against one top of scale. The top is
    computed once from this snapshot's MAC, so no two containers can be drawn
    against two different agents' scales.

    Args:
        snapshot: The run's state at the instant drawn.

    Returns:
        Six readings: the circuit, the alveoli, venous blood, the vessel-rich
        group, muscle and fat.

    Raises:
        TypeError: If the snapshot's `agent_mac_percent` was not built as a
            `MacPercent`. `chart_axis_top_percent` raises it.
        ValueError: If a compartment's recorded amount is negative or not
            finite. `format_compartment_amount` raises it.
    """

    top_percent = chart_axis_top_percent(snapshot.agent_mac_percent)
    readings: list[ContainerReading] = []

    for panel in READOUT_PANELS:
        if panel.quantity is None:
            continue

        fraction = compartment_fraction(snapshot, panel.quantity)
        percent = percent_from_fraction(fraction)
        readings.append(
            ContainerReading(
                quantity=panel.quantity,
                name=panel.name,
                fill=min(percent / top_percent, 1.0),
                off_scale=above_the_axis_top(percent, top_percent),
                tension=format_percent(fraction),
                amount=format_compartment_amount(
                    snapshot.compartment_agent_amounts.of(panel.quantity)
                ),
            )
        )

    return tuple(readings)


def scale_caption(snapshot: SimulationSnapshot) -> str:
    """Return the caption naming the scale that every container of this run fills against.

    The caption writes the top of the scale in the same way as the concentration
    chart labels its own top gridline, through `percent_axis_ticks`. So the
    caption and the chart's axis cannot print the same scale in two ways.

    Raises:
        TypeError: If the snapshot's `agent_mac_percent` was not built as a
            `MacPercent`. `chart_axis_top_percent` raises it.
    """

    mac_percent = snapshot.agent_mac_percent
    ticks = percent_axis_ticks(
        chart_axis_top_percent(mac_percent), chart_grid_interval_percent(mac_percent)
    )

    scale = SCALE_CAPTION_TEMPLATE.format(
        top=ticks[-1][1],
        unit=DisplayUnit.CONCENTRATION.axis_title,
        top_mac=f"{CHART_AXIS_TOP_MAC:g}{MAC_UNIT_SUFFIX}",
    )

    return f"{scale}\n{AMOUNT_CONDITION_LINES}"


def off_scale_line(readings: tuple[ContainerReading, ...]) -> str | None:
    """Return the line naming each container above the scale, or None when none is above it."""

    above = [reading.name for reading in readings if reading.off_scale]

    if not above:
        return None

    return OFF_SCALE_LINE_TEMPLATE.format(compartments=", ".join(above))


#: The lines under the share bar. They name every segment in text, so no compartment
#: is told apart by colour alone. There are always three lines. The first is the
#: heading, and each of the other two names three segments. The count is fixed
#: because Qt leaves a wrapped label's extra lines out of a View's minimum size,
#: as the scale caption's comment explains. The wording is a placeholder.
SHARE_LINE_TEMPLATE: Final = "Share of the agent the run holds:\n{first},\n{second}."
SHARE_SEGMENT_TEMPLATE: Final = "{name} {share}"

#: The lines under the share bar while the run holds no agent. No share exists
#: then, so the bar is drawn empty, and the lines say why rather than showing
#: six zeros as if they were shares. They are three lines, as many as the
#: shares take, so the schematic keeps its size when the first agent arrives.
#: The wording is a placeholder.
NO_AGENT_SHARE_LINE: Final = (
    "Share of the agent the run holds:\nnone yet, because the run holds no agent,\n"
    "so the bar is empty."
)


@dataclass(frozen=True, slots=True)
class ShareSegment:
    """One compartment's segment of the share bar, sized and labelled from one snapshot.

    Attributes:
        quantity: The compartment that the segment stands for.
        name: The compartment's name, as its readout panel names it.
        share: The compartment's amount divided by `stored_agent_l`, all the
            agent that the run holds. It runs from 0 through 1. The segment's
            length is this share of the bar's length.
        text: The share in whole percent, as `format_compartment_share`
            writes it.
    """

    quantity: RecordedQuantity
    name: str
    share: float
    text: str


def share_segments(snapshot: SimulationSnapshot) -> tuple[ShareSegment, ...] | None:
    """Return the share bar's six segments, or None while the run holds no agent.

    The segments are in the same order as the containers. Each share is the
    compartment's amount from the snapshot's per-compartment record
    (`PL-KFTM`), divided by the snapshot's `stored_agent_l`. The six
    amounts sum to that total exactly, so the six shares fill the bar
    (`docs/INTERFACE.md` § "The compartment schematic: what its heights, amounts
    and share bar assert"). When the run holds no agent, no share exists. The
    function then returns None, rather than dividing by zero or returning six
    zeros.

    Raises:
        ValueError: If `stored_agent_l` is negative or not finite, or if a
            share falls outside 0 through 1, which `format_compartment_share`
            rejects. Either fault means that the amounts and their total
            disagree.
    """

    total = snapshot.stored_agent_l

    if not isfinite(total) or total < 0.0:
        raise ValueError(f"the run's stored agent must be finite and not negative, not {total!r} L")

    if total == 0.0:
        return None

    return tuple(
        ShareSegment(
            quantity=panel.quantity,
            name=panel.name,
            share=(share := snapshot.compartment_agent_amounts.of(panel.quantity) / total),
            text=format_compartment_share(share),
        )
        for panel in READOUT_PANELS
        if panel.quantity is not None
    )


def share_line(segments: tuple[ShareSegment, ...] | None) -> str:
    """Return the lines that name every segment of the share bar, or say the run holds no agent."""

    if segments is None:
        return NO_AGENT_SHARE_LINE

    named = [
        SHARE_SEGMENT_TEMPLATE.format(name=segment.name, share=segment.text) for segment in segments
    ]
    half = len(named) // 2

    return SHARE_LINE_TEMPLATE.format(first=", ".join(named[:half]), second=", ".join(named[half:]))


@dataclass(frozen=True, slots=True)
class SchematicShown:
    """Everything one run's schematic shows at one instant, as plain values.

    Attributes:
        instant: The simulated time at which the values are read, as the
            readouts' clock prints it. Two runs that are compared can be at
            different times, so each schematic says which instant it shows.
        readings: One reading per container, in `CONTAINER_ORDER`.
        scale_caption: The caption naming the scale that the containers fill
            against, or None while the values are withheld.
        off_scale_line: The lines naming each container that is above the
            scale. It is None when no container is above the scale or the values
            are withheld.
        shares: The share bar's segments, or None while the run holds no
            agent or the values are withheld. The bar is then drawn empty.
        share_line: The line naming each segment, or saying that the run holds
            no agent, or None while the values are withheld.
    """

    instant: str
    readings: tuple[ContainerReading, ...]
    scale_caption: str | None
    off_scale_line: str | None
    shares: tuple[ShareSegment, ...] | None
    share_line: str | None


def schematic_shown(snapshot: SimulationSnapshot) -> SchematicShown:
    """Return what one run's schematic shows for `snapshot`.

    Raises:
        TypeError: As `container_readings` and `scale_caption` raise it.
        ValueError: As `container_readings` and `share_segments` raise it.
    """

    readings = container_readings(snapshot)
    segments = share_segments(snapshot)

    return SchematicShown(
        format_elapsed(snapshot.elapsed_s),
        readings,
        scale_caption(snapshot),
        off_scale_line(readings),
        segments,
        share_line(segments),
    )


#: What an amount label shows while the run's values are withheld.
WITHHELD_AMOUNT_TEXT: Final = f"\u2014 {DisplayUnit.AGENT_VAPOUR_MILLILITRES.label}"

#: What a run's schematic shows while its values are withheld. They are withheld
#: after a Reset or an agent change, until a frame has been drawn. The readouts
#: are withheld at the same moments, with the same mark (`RunView`). Every
#: container is drawn empty and no caption is shown, because the caption's scale
#: may belong to the agent that was discarded. The share bar is drawn empty with
#: no line under it, because its shares would be the discarded run's.
WITHHELD_SCHEMATIC: Final = SchematicShown(
    WITHHELD_ELAPSED_TIME_TEXT,
    tuple(
        ContainerReading(
            quantity=panel.quantity,
            name=panel.name,
            fill=0.0,
            off_scale=False,
            tension=WITHHELD_CONCENTRATION_TEXT,
            amount=WITHHELD_AMOUNT_TEXT,
        )
        for panel in READOUT_PANELS
        if panel.quantity is not None
    ),
    None,
    None,
    None,
    None,
)


def instant_line(instant: str, run_name: str | None) -> str:
    """Return the line above one run's schematic.

    The line gives the instant that the schematic shows. A lone run is not
    named, just as its own panels are not. While runs are compared, the line
    also names the run, because the order in which the schematics are stacked
    cannot say which run a tension belongs to.
    """

    if run_name is None:
        return INSTANT_LINE_TEMPLATE.format(instant=instant)

    return COMPARED_INSTANT_LINE_TEMPLATE.format(run=run_name, instant=instant)
