"""Compute how each container of the compartment schematic is filled and labelled.

`docs/INTERFACE.md` § "The compartment schematic: what its heights, amounts and
share bar assert" specifies the schematic (`PL-2881`). This module turns one
snapshot into one reading per container. A reading says how full the container
is and what its label prints. The schematic's View draws the readings
(`PL-RNYV`). Nothing here imports Qt, so every number a reader interprets is
computed and tested apart from the drawing.

A container's fill is the compartment's tension, on the concentration chart's
scale, from zero to `chart_axis_top_percent` at the top that the reader chose
(`ChartCeiling`). The reader chooses one top for every concentration chart and
every schematic (`PL-7LZ7`), and the dashboard passes it here. So a tension
is above the top on the schematic exactly when it is above the top of every
chart's plot. The chart's off-scale notice covers more time than the
schematic does. It names each shown compartment whose trace is above the top
anywhere in the chart's window, and the schematic marks each compartment that
is above the top at the instant it shows. The fill is not an amount. A
tension above the top of the scale fills the container, and the container is
marked as off the scale. Its label
still prints the tension. Each container carries a mark at each MAC value that
the chart's MAC axis labels at that top, so a fill level is read against the
container's own marks. Each label gives
the compartment's name, its tension as its readout prints it, its amount, and
its share of all the agent that the six compartments hold. The amount comes
from the snapshot's record of the agent in each compartment (`PL-KFTM`). So a
label cannot disagree with its readout, and the schematic computes no amount of
its own. A short bar under each label draws its share, on one scale for all six
bars (`PL-8PL4`).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Final

from anesthesia_sim.app.controller import SimulationSnapshot
from anesthesia_sim.app.dashboard_frame import (
    COMPARTMENT_PANELS,
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
    MAC_UNIT_SUFFIX,
    ChartCeiling,
    chart_axis_top_percent,
    format_compartment_amount,
    format_compartment_share,
    format_elapsed,
    format_percent,
    mac_axis_ticks,
    reference_percent_digits,
)
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.core.concentration import percent_from_fraction

__all__ = [
    "COMPARED_INSTANT_LINE_TEMPLATE",
    "CONTAINER_ORDER",
    "CUT_CONTAINERS_TEXT",
    "INSTANT_LINE_TEMPLATE",
    "NO_AGENT_SHARE_CAPTION",
    "NO_SHARE_TEXT",
    "OFF_SCALE_LINE_TEMPLATE",
    "AMOUNT_UNIT_TEXT",
    "SCALE_CAPTION_TEMPLATE",
    "SCHEMATIC_HEADING",
    "SHARE_CAPTION",
    "SHARE_TEMPLATE",
    "TENSION_UNIT_TEXT",
    "WIDEST_LABELS",
    "WITHHELD_AMOUNT_TEXT",
    "WITHHELD_SCHEMATIC",
    "ContainerReading",
    "SchematicShown",
    "container_readings",
    "instant_line",
    "schematic_shown",
    "off_scale_line",
    "scale_caption",
    "scale_marks",
    "share_caption",
]

#: The compartments the schematic draws, in the order its containers stand:
#: the readout row's order, read from the readout panels so the two cannot
#: disagree.
CONTAINER_ORDER: Final[tuple[RecordedQuantity, ...]] = tuple(
    panel.compartment() for panel in COMPARTMENT_PANELS
)

#: The line over each run's schematic: the run's name while runs are compared,
#: and the instant it shows. The wording is a placeholder.
INSTANT_LINE_TEMPLATE: Final = "At {instant} of simulated time"
COMPARED_INSTANT_LINE_TEMPLATE: Final = "{run}, at {instant} of simulated time"

#: The line that names the unit of every tension a container's label prints.
#: Each label prints its tension with "%" alone, because the full unit would
#: widen every column. The View keeps this line above the box that scrolls it,
#: so the unit is on screen wherever any tension is (`PL-3NGZ`), as
#: `AMOUNT_UNIT_TEXT` says for the amounts.
TENSION_UNIT_TEXT: Final = f"Tensions are in {DisplayUnit.CONCENTRATION.axis_title}."

#: The schematic's heading. The wording is a placeholder.
SCHEMATIC_HEADING: Final = "Where the agent is: each compartment's tension and amount"

#: The caption that says what a container's height means. A height is a
#: tension, as a share of the concentration chart's range. So the caption names
#: that range, says what the marks stand for, and says that a height is not an
#: amount (`docs/INTERFACE.md` § "The compartment schematic: what its
#: heights, amounts and share bar assert"). A container is a few tens of pixels
#: tall and the chart's plot is several hundred, and a Workspace can show the
#: two side by side. A fill level read across to the chart's gridlines would give the wrong
#: tension. So each container carries a mark at each labelled MAC value of the
#: chart's scale (`scale_marks`), and is read against its own marks
#: (`PL-8W1B`). The caption names the scale's top in percent and in MAC, so a
#: Workspace that shows no chart still says what the heights are measured
#: against. The caption is separate lines rather than one wrapped line. Qt leaves a wrapped label's
#: extra lines out of the minimum size that a View declares, so the containers'
#: labels would lose the room in which their amounts are printed. The wording
#: is a placeholder, but what the caption must say is not.
SCALE_CAPTION_TEMPLATE: Final = (
    "Fill height is tension, on a scale of 0 to {top}{unit} ({top_mac}).\n"
    "Marks stand every {step_mac}.\n"
    "A container's height is its tension, not its amount of agent."
)

#: The line that names the unit of every amount a container's label prints,
#: and the temperature and pressure the amounts are stated at (`PL-HQPF`). Each
#: label prints its amount in "mL vapour", which does not name the condition.
#: The View keeps this line above the box that scrolls it, beside the tensions'
#: unit, so the unit and its condition are on screen wherever any amount is
#: (`PL-3NGZ`). NUREG-0700 Rev. 3
#: guideline 1.5-15 asks that a scrolled display keep all of its labelling
#: information, and guideline 1.2.2-4 that a unit shared by every cell be part
#: of the labels (O'Hara, US Nuclear Regulatory Commission, 2020, pp. 1-59 and
#: 1-17).
AMOUNT_UNIT_TEXT: Final = (
    f"Amounts are {DisplayUnit.AGENT_VAPOUR_MILLILITRES.recorded} at {REFERENCE_CONDITION_LABEL}."
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

#: The line that the schematic paints in place of its containers while any of
#: them is cut off, by a run's pinned heading or by the edge of the box or page
#: that scrolls it (`PL-GWTR`). A container shows its tension as the height of
#: its fill, so a container shown in part could look full, or empty, at a
#: tension it does not hold. So the containers are drawn only whole. The line
#: says what is hidden and why, then what brings the containers back, as
#: NUREG-0700 Rev. 3 guidelines 2.7.3-1 and 10.3.4-8 ask (O'Hara, US Nuclear
#: Regulatory Commission, 2020, pp. 2-86 and 10-14). It names the condition and
#: then the verdict, as the schematic's other captions do. "Scroll" is the
#: remedy because the line is painted only where the box is tall enough for a
#: scroll to bring the containers into view whole: where it is not, the Area
#: shows its too-small notice in place of the View.
CUT_CONTAINERS_TEXT: Final = (
    "The containers are not wholly in view, so the schematic hides them. Scroll to see them."
)

#: Each container's label ends with this line, which gives the compartment's
#: share of all the agent that the six containers hold at the instant shown
#: (`PL-8PL4`). Each share sits in the label of its own container, so no share
#: is told apart by colour and no key is needed to name it. The line is kept no
#: wider than a compartment's name or amount, so it adds no width to a column.
#: Worded "of the agent", it was the widest label, and under the font that CI
#: draws in, the Maintenance Workspace then scrolled sideways at 1366 by 768.
#: The wording is a placeholder.
SHARE_TEMPLATE: Final = "{share} of agent"

#: The share line shows this text while no share exists, which is while the run
#: holds no agent and while its values are withheld. The line stays, so the
#: labels keep their height when the first agent arrives. The dash is the mark
#: the readouts use for a value they do not show. The wording is a placeholder.
NO_SHARE_TEXT: Final = "\u2014 of agent"

#: This caption line says what every share is a part of, which is the agent that
#: the six containers hold at the instant shown. The project owner first read the
#: old single bar's heading, "Share of the agent the run holds", as agent counted
#: over the whole run (`PL-8PL4`), so the line names the instant. It names the six
#: containers rather than the circuit and body, because the model leaves out lung
#: tissue, a vessel-poor group and the circuit's plastics. A patient's body holds
#: agent there that no share counts (`docs/MODEL.md` § "What the model does not
#: represent", `PL-KQ0S`). The wording is a placeholder, but the instant and the
#: six containers as the whole must be on screen.
SHARE_CAPTION: Final = "Shares are of all the agent in the six containers at this instant."

#: The caption line shows this text while the run holds no agent. No share
#: exists then, so each label shows `NO_SHARE_TEXT`, and this line says why,
#: rather than the labels showing six zeros as if they were shares. It is one
#: line, as `SHARE_CAPTION` is, so the schematic keeps its height when the first
#: agent arrives. The wording is a placeholder.
NO_AGENT_SHARE_CAPTION: Final = "No shares yet: the six containers hold no agent."

#: The label texts that set the width of each container's column, so that a
#: column does not widen while a run fills. Room for a tension is reserved in the
#: same way as the readouts reserve it. Room for an amount is reserved for two
#: texts: an amount below the display floor, and a five-figure amount. The
#: formatter that prints amounts writes both texts. Room for a share is reserved
#: for the share below 1%, the share just below the whole, the whole, and the
#: text shown while no share exists. The View also widens a column for any label
#: wider than these, so that no label is clipped. Each share bar is as long as
#: the widest label its column reserves or shows (`SchematicCanvas.share_bar`).
WIDEST_LABELS: Final[tuple[str, ...]] = (
    *(panel.name for panel in COMPARTMENT_PANELS),
    WIDEST_COMPARTMENT_VALUE,
    format_compartment_amount(1e-9),
    format_compartment_amount(88.0),
    *(
        SHARE_TEMPLATE.format(share=format_compartment_share(share))
        for share in (1e-9, 1.0 - 1e-9, 1.0)
    ),
    NO_SHARE_TEXT,
)


@dataclass(frozen=True, slots=True)
class ContainerReading:
    """One container of the schematic, as one snapshot fills and labels it.

    Attributes:
        quantity: The compartment that the container stands for.
        name: The compartment's name, as its readout panel names it.
        fill: The share of the container's height that is filled, from 0 to
            1. It is the tension divided by the top of the chart's scale at
            the top the reader chose, and it is 1 for a tension above that
            top.
        off_scale: Whether the tension is above the top of the scale
            by more than the smallest step that the readouts show. The test is
            `above_the_axis_top`, the same one that the chart's off-scale
            notice uses. When it is true, the View marks the container as off
            the scale.
        tension: The tension, written as the compartment's readout writes it.
        amount: The amount of agent in the compartment, written in millilitres
            of vapour.
        share: The compartment's amount divided by `stored_agent_l`, all the
            agent that the six compartments hold, from 0 through 1. The
            container's share bar is filled to this share of its length. It is
            None while the run holds no agent, because no share exists then,
            and while the values are withheld.
    """

    quantity: RecordedQuantity
    name: str
    fill: float
    off_scale: bool
    tension: str
    amount: str
    share: float | None

    @property
    def share_text(self) -> str:
        """Return the share as the label's last line prints it.

        It is `SHARE_TEMPLATE` with the share in whole percent, as
        `format_compartment_share` writes it, or `NO_SHARE_TEXT` while `share`
        is None. It is worked out from `share` each time, so the label and the
        bar under it cannot disagree.
        """

        return _share_text(self.share)


def container_readings(
    snapshot: SimulationSnapshot, ceiling: ChartCeiling
) -> tuple[ContainerReading, ...]:
    """Return one reading per container, in the readout row's order.

    The schematic uses the readout panels' own order and names, so the
    schematic and the readout row list the six compartments in the same way.
    Every container of the run fills against one top of scale. The top is
    computed once from this snapshot's MAC and `ceiling`, so no two containers
    can be drawn against two different agents' scales or two different tops.
    Each share is the compartment's amount divided by the snapshot's
    `stored_agent_l`. The six amounts sum to that total exactly, so the six shares make up the whole
    (`docs/INTERFACE.md` § "The compartment schematic: what its heights, amounts
    and share bar assert"). While the run holds no agent, no share exists, and
    each reading's share is None, rather than a division by zero or six zeros.

    Args:
        snapshot: The run's state at the instant drawn.
        ceiling: The top the reader chose for every concentration chart and
            schematic, as the dashboard holds it in the reader's preferences.

    Returns:
        Six readings: the circuit, the alveoli, venous blood, the vessel-rich
        group, muscle and fat.

    Raises:
        TypeError: If the snapshot's `agent_mac_percent` was not built as a
            `MacPercent`, or if `ceiling` is not a `ChartCeiling`.
            `chart_axis_top_percent` raises it.
        ValueError: If a compartment's recorded amount is negative or not
            finite, which `format_compartment_amount` raises. If
            `stored_agent_l` is negative or not finite, or if a share falls
            outside 0 through 1, which `format_compartment_share` rejects.
            Either of the last two faults means that the amounts and their
            total disagree.
    """

    top_percent = chart_axis_top_percent(snapshot.agent_mac_percent, ceiling)
    total_l = snapshot.stored_agent_l

    if not isfinite(total_l) or total_l < 0.0:
        raise ValueError(
            f"the run's stored agent must be finite and not negative, not {total_l!r} L"
        )

    readings: list[ContainerReading] = []

    for panel in COMPARTMENT_PANELS:
        quantity = panel.compartment()
        fraction = compartment_fraction(snapshot, quantity)
        percent = percent_from_fraction(fraction)
        amount_l = snapshot.compartment_agent_amounts.of(quantity)
        share = None if total_l == 0.0 else amount_l / total_l
        readings.append(
            ContainerReading(
                quantity=quantity,
                name=panel.name,
                fill=min(percent / top_percent, 1.0),
                off_scale=above_the_axis_top(percent, top_percent),
                tension=format_percent(fraction),
                amount=format_compartment_amount(amount_l),
                share=share,
            )
        )

    return tuple(readings)


def _share_text(share: float | None) -> str:
    """Return the label's share line for `share`, or `NO_SHARE_TEXT` when no share exists."""

    if share is None:
        return NO_SHARE_TEXT

    return SHARE_TEMPLATE.format(share=format_compartment_share(share))


def _scale_ticks(
    snapshot: SimulationSnapshot, ceiling: ChartCeiling
) -> tuple[tuple[float, str], ...]:
    """Return the chart's MAC ticks at `ceiling`, for this snapshot's agent.

    The ticks come from `mac_axis_ticks`, as the chart's own MAC axis takes
    them. So the schematic's marks and its caption describe one scale, and it
    is the scale the chart draws at the same top.

    Raises:
        TypeError: If the snapshot's `agent_mac_percent` was not built as a
            `MacPercent`, or if `ceiling` is not a `ChartCeiling`.
            `chart_axis_top_percent` raises it.
    """

    mac_percent = snapshot.agent_mac_percent

    return mac_axis_ticks(chart_axis_top_percent(mac_percent, ceiling), mac_percent)


def scale_marks(snapshot: SimulationSnapshot, ceiling: ChartCeiling) -> tuple[float, ...]:
    """Return the height of each mark on a container, as a share of the container's height.

    A mark stands at each MAC value that the chart labels at `ceiling`,
    between the bottom and the top of the scale. The bottom and the top are
    the container's own edges, so they carry no mark. A container filled to a
    mark shows the tension at that MAC value (`PL-8W1B`).

    Returns:
        The heights from the lowest mark upward, each greater than 0 and less
        than 1.

    Raises:
        TypeError: As `_scale_ticks` raises it.
    """

    top_percent = chart_axis_top_percent(snapshot.agent_mac_percent, ceiling)

    return tuple(
        position / top_percent
        for position, _ in _scale_ticks(snapshot, ceiling)
        if 0.0 < position < top_percent
    )


def scale_caption(snapshot: SimulationSnapshot, ceiling: ChartCeiling) -> str:
    """Return the caption naming the scale that every container of this run fills against.

    The caption names the top of the scale in percent and in MAC, and the
    spacing of the marks in MAC, as the chart's MAC axis labels them
    (`_scale_ticks`). The top's percent goes through
    `reference_percent_digits`, so it is the value that the chart's
    off-scale notice gives for the same top, at the 1 MAC line's precision.
    The caption ends with the lines that say the amounts held in the body
    read high at the condition `AMOUNT_UNIT_TEXT` names.

    Raises:
        TypeError: As `_scale_ticks` raises it.
    """

    ticks = _scale_ticks(snapshot, ceiling)
    top_percent = chart_axis_top_percent(snapshot.agent_mac_percent, ceiling)

    scale = SCALE_CAPTION_TEMPLATE.format(
        top=reference_percent_digits(top_percent),
        unit=DisplayUnit.CONCENTRATION.axis_title,
        top_mac=ceiling.label,
        step_mac=f"{ticks[1][1]}{MAC_UNIT_SUFFIX}",
    )

    return f"{scale}\n{BODY_STORES_CONDITION_LINES}"


def off_scale_line(readings: tuple[ContainerReading, ...]) -> str | None:
    """Return the line naming each container above the scale, or None when none is above it."""

    above = [reading.name for reading in readings if reading.off_scale]

    if not above:
        return None

    return OFF_SCALE_LINE_TEMPLATE.format(compartments=", ".join(above))


def share_caption(readings: tuple[ContainerReading, ...]) -> str:
    """Return the caption line that says what the shares are of, or why there are none."""

    if any(reading.share is None for reading in readings):
        return NO_AGENT_SHARE_CAPTION

    return SHARE_CAPTION


@dataclass(frozen=True, slots=True)
class SchematicShown:
    """Everything one run's schematic shows at one instant, as plain values.

    Attributes:
        instant: The simulated time at which the values are read, as the
            readouts' clock prints it. Two runs that are compared can be at
            different times, so each schematic says which instant it shows.
        readings: One reading per container, in `CONTAINER_ORDER`.
        marks: The height of each mark on every container, as a share of the
            container's height (`scale_marks`). It is empty while the values
            are withheld, because the marks may belong to the agent that was
            discarded.
        scale_caption: The caption naming the scale that the containers fill
            against, or None while the values are withheld.
        off_scale_line: The lines naming each container that is above the
            scale. It is None when no container is above the scale or the values
            are withheld.
        share_caption: The line saying what the shares are of, or that the
            run holds no agent yet (`share_caption`), or None while the values
            are withheld.
        ceiling: The top that the containers are filled against, or None
            while the values are withheld. The View's axis-top control shows
            it, so the control names the top that the containers show.
    """

    instant: str
    readings: tuple[ContainerReading, ...]
    marks: tuple[float, ...]
    scale_caption: str | None
    off_scale_line: str | None
    share_caption: str | None
    ceiling: ChartCeiling | None


def schematic_shown(snapshot: SimulationSnapshot, ceiling: ChartCeiling) -> SchematicShown:
    """Return what one run's schematic shows for `snapshot`, filled against `ceiling`.

    Raises:
        TypeError: As `container_readings`, `scale_marks` and `scale_caption` raise it.
        ValueError: As `container_readings` raises it.
    """

    readings = container_readings(snapshot, ceiling)

    return SchematicShown(
        format_elapsed(snapshot.elapsed_s),
        readings,
        scale_marks(snapshot, ceiling),
        scale_caption(snapshot, ceiling),
        off_scale_line(readings),
        share_caption(readings),
        ceiling,
    )


#: What an amount label shows while the run's values are withheld.
WITHHELD_AMOUNT_TEXT: Final = f"\u2014 {DisplayUnit.AGENT_VAPOUR_MILLILITRES.label}"

#: What a run's schematic shows while its values are withheld. They are withheld
#: after a Reset or an agent change, until a frame has been drawn. The readouts
#: are withheld at the same moments, with the same mark (`RunView`). Every
#: container is drawn empty, with no marks and no caption, because the marks and
#: the caption's scale may belong to the agent that was discarded. Every share
#: bar is drawn empty and every share line shows the dash, because the shares
#: would be the discarded run's.
WITHHELD_SCHEMATIC: Final = SchematicShown(
    WITHHELD_ELAPSED_TIME_TEXT,
    tuple(
        ContainerReading(
            quantity=panel.compartment(),
            name=panel.name,
            fill=0.0,
            off_scale=False,
            tension=WITHHELD_CONCENTRATION_TEXT,
            amount=WITHHELD_AMOUNT_TEXT,
            share=None,
        )
        for panel in COMPARTMENT_PANELS
    ),
    (),
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
