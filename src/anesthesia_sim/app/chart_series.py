"""Assemble the compartment chart's traces and redraw them from the run.

The shaping layer between the controller's recorded history and the chart
control: which sample a trace draws is `chart_downsampling.py`'s, what a
trace *is* and how a frame updates it is this module's, and the dashboard
that owns the chart is `simulation_view.py`'s. Nothing here reads
simulation state, holds a setting, or performs a physiological or unit
calculation beyond the fraction-to-percent conversion the axis is labelled
in.

It is separate from the view for the reason `chart_downsampling.py` is:
what a trace draws is a presentation-correctness concern rather than a
layout one. Plotting one compartment's values on another compartment's
line would misstate the run as surely as a wrong number would, so the
pairing is passed in as one `PlottedSeries` table the caller declares
beside its traces, where it can be audited at a glance, rather than being
spread across a dashboard. The table is not type-enforced - `flet_charts`
ships no stubs, so a chart series is `Any` to the checker - and
`tests/unit/test_simulation_view.py`'s
`test_chart_traces_stay_bound_to_their_own_compartment` is what holds it.

Every drawn point remains a recorded sample. Nothing in this module
interpolates, extrapolates, or synthesizes a value, and the controller's
own history is read but never modified.
"""

from collections.abc import Callable, Sequence
from typing import Final

import flet_charts as fch

from anesthesia_sim.app.chart_downsampling import first_index_at_or_after, select_envelope_indices
from anesthesia_sim.app.controller import SimulationHistorySample

__all__ = [
    "MAX_CHART_POINTS_PER_SERIES",
    "PlottedSeries",
    "SampleValue",
    "alveolar_value",
    "build_control_mark",
    "build_reference_line",
    "build_series",
    "circuit_value",
    "fat_value",
    "PARKED_CONTROL_MARK_X",
    "mixed_venous_value",
    "muscle_value",
    "park_control_mark",
    "redraw_control_mark",
    "redraw_reference_band",
    "redraw_reference_line",
    "redraw_series",
    "redraw_visible_window",
    "sample_elapsed_s",
    "vessel_rich_value",
]

# Per-trace ceiling on points handed to the chart. Each point is a Flet
# control, and `redraw_series` moves the points already drawn rather than
# rebuilding them (PL-010), which keeps a frame's Python work proportional to
# this number rather than to it times the cost of a construction. 300 points
# across a chart a few hundred pixels wide is already finer than the display
# can resolve.
#
# What this ceiling does *not* bound is the traffic the client is sent. That
# is the count of points whose chosen sample moved, which is a property of
# the decimation rather than of this number: PL-Q197 found every drawn point
# moving on every frame, and 1 788 of them at 5 Hz saturated the Flutter
# client while Python idled. `chart_downsampling.py` is where that is held
# down, and `tests/integration/test_chart_patching.py` is what keeps it there.
MAX_CHART_POINTS_PER_SERIES: Final = 300

#: Reads one quantity out of one recorded sample, in the sample's own units.
type SampleValue = Callable[[SimulationHistorySample], float]

#: One chart trace bound to the quantity it draws.
type PlottedSeries = tuple[fch.LineChartData, SampleValue]


# One named reader per plotted quantity. Named rather than inline so that the
# trace-to-quantity pairing a caller builds reads as an explicit table:
# plotting a compartment's values on another compartment's line would be a
# presentation-correctness failure, and a table is auditable at a glance.
def sample_elapsed_s(sample: SimulationHistorySample) -> float:
    return sample.elapsed_s


def circuit_value(sample: SimulationHistorySample) -> float:
    return sample.circuit_concentration_fraction


def alveolar_value(sample: SimulationHistorySample) -> float:
    return sample.alveolar_concentration_fraction


def mixed_venous_value(sample: SimulationHistorySample) -> float:
    return sample.mixed_venous_concentration_fraction


def vessel_rich_value(sample: SimulationHistorySample) -> float:
    return sample.vessel_rich_partial_pressure_fraction


def muscle_value(sample: SimulationHistorySample) -> float:
    return sample.muscle_partial_pressure_fraction


def fat_value(sample: SimulationHistorySample) -> float:
    return sample.fat_partial_pressure_fraction


def build_series(
    color: str, stroke_width: float, dash_pattern: list[int] | None = None
) -> fch.LineChartData:
    """Build one visual series for the compartment chart.

    Args:
        color: Hexadecimal line color.
        stroke_width: Line width in display pixels.
        dash_pattern: Optional alternating dash and gap lengths
            in display pixels.

    Returns:
        Configured Flet line-chart series.
    """

    return fch.LineChartData(
        points=[fch.LineChartDataPoint(0.0, 0.0)],
        color=color,
        stroke_width=stroke_width,
        dash_pattern=dash_pattern,
        curved=False,
        point=False,
    )


def build_reference_line(
    color: str, stroke_width: float, dash_pattern: list[int] | None = None
) -> fch.LineChartData:
    """Build one horizontal reference mark for the compartment chart.

    A reference is not a trace, and the difference is the reason this is a
    separate constructor rather than `build_series` with two points. A trace
    draws recorded samples; a reference draws a published constant at a
    height the chart's own axis gives meaning to, and it carries no
    `SampleValue` because there is no sample to read. Keeping the two apart
    is what stops a reference being added to the `PlottedSeries` table, where
    every entry is checked against the compartment it draws.

    Two points are enough for a horizontal line, and
    `redraw_reference_line` moves them rather than rebuilding them, for the
    reason `redraw_series` gives.

    Args:
        color: Hexadecimal line color.
        stroke_width: Line width in display pixels.
        dash_pattern: Optional alternating dash and gap lengths
            in display pixels.

    Returns:
        Configured two-point Flet line-chart series.
    """

    return fch.LineChartData(
        points=[fch.LineChartDataPoint(0.0, 0.0), fch.LineChartDataPoint(0.0, 0.0)],
        color=color,
        stroke_width=stroke_width,
        dash_pattern=dash_pattern,
        curved=False,
        point=False,
    )


def redraw_reference_line(
    series: fch.LineChartData, start_x: float, end_x: float, y: float
) -> None:
    """Span one reference mark across the visible window at a constant height.

    Both endpoints are moved on every frame rather than only when the window
    scrolls. The height depends on the running agent, so a reference left at
    the previous agent's value would sit at a wrong height on a labelled
    axis — the correct number in the wrong context that `CLAUDE.md` treats
    as a safety failure — and four in-place assignments per frame is not a
    cost worth trading a staleness class against. `redraw_series` records
    why an in-place assignment reaches the client.

    Args:
        series: Reference mark to move. Its two points are mutated.
        start_x: Left edge of the visible window, in simulated seconds.
        end_x: Right edge of the visible window, in simulated seconds.
        y: Constant height, in the chart's own percent unit.
    """

    left, right = series.points
    left.x = start_x
    left.y = y
    right.x = end_x
    right.y = y


def redraw_reference_band(
    series: fch.LineChartData, start_x: float, end_x: float, lower_y: float, upper_y: float
) -> None:
    """Span one reference *band* across the visible window between two heights.

    The band is one series drawn at its upper edge with the area beneath it
    filled down to `lower_y`: `below_line_cutoff_y` is what makes the fill a
    bounded band rather than everything under a line. The stroke stays on the
    upper edge, so the fill's own boundary is what marks the lower one.

    Args:
        series: Band to move. Its two points are mutated, and its fill
            cutoff is set to the lower edge.
        start_x: Left edge of the visible window, in simulated seconds.
        end_x: Right edge of the visible window, in simulated seconds.
        lower_y: Lower edge of the band, in the chart's percent unit.
        upper_y: Upper edge of the band, in the chart's percent unit.
    """

    redraw_reference_line(series, start_x, end_x, upper_y)
    series.below_line_cutoff_y = lower_y


def build_control_mark(
    color: str, stroke_width: float, dash_pattern: list[int] | None = None
) -> fch.LineChartData:
    """Build one vertical mark for a recorded control change.

    A third kind of series, and separate from both constructors above for
    the same reason they are separate from each other. A trace draws
    recorded samples; a reference draws a published constant; a control
    mark draws neither - it says only that the run's inputs changed here,
    which is an event on the time axis rather than a value on the
    concentration one. It carries no `SampleValue`, so it can never join
    the `PlottedSeries` table, and its two points are moved rather than
    rebuilt for the reason `redraw_series` gives.

    What separates it visually from every other series is its
    *orientation*: nothing else on this chart is vertical. That is the
    non-colour channel `.claude/rules/ui-color.md`'s judgment 2 requires
    of an encoding carrying meaning, and it survives greyscale and every
    colour-vision deficiency, so the mark is not competing for separation
    in a palette that six traces have already exhausted.

    Args:
        color: Hexadecimal line color.
        stroke_width: Line width in display pixels.
        dash_pattern: Optional alternating dash and gap lengths
            in display pixels.

    Returns:
        Configured two-point Flet line-chart series.
    """

    return fch.LineChartData(
        points=[fch.LineChartDataPoint(0.0, 0.0), fch.LineChartDataPoint(0.0, 0.0)],
        color=color,
        stroke_width=stroke_width,
        dash_pattern=dash_pattern,
        curved=False,
        point=False,
    )


def redraw_control_mark(series: fch.LineChartData, x: float, top_y: float) -> None:
    """Stand one control mark at a simulated time, spanning the plot height.

    Full height rather than a tick at the axis, because the time it marks
    has to be readable against every trace: a change to cardiac output
    shows in the vessel-rich curve and a change to fresh gas flow in the
    circuit curve, and a mark a reader has to project upwards from the
    axis is one they will project onto the wrong point of the wrong trace.

    Args:
        series: Mark to move. Its two points are mutated.
        x: Simulated time the change took effect, in seconds.
        top_y: Top of the plotted range, in the chart's own percent unit.
    """

    bottom, top = series.points
    bottom.x = x
    bottom.y = 0.0
    top.x = x
    top.y = top_y


#: Where a mark with nothing to mark is put. A negative simulated time is
#: outside the plotted range under every window the chart shows - its left
#: edge is `max(0.0, ...)` and so never negative - and it is a *constant*,
#: which is the property that matters. Parking relative to the moving window
#: instead would rewrite both points of every unused mark on every frame of a
#: scrolling run: 48 client operations a frame with nothing on screen to show
#: for them, which is what `test_a_scrolling_window_rebuilds_only_at_a_bucket_boundary`
#: caught (PL-Q197's budget, measured against 24 parked marks).
PARKED_CONTROL_MARK_X: Final = -1.0


def park_control_mark(series: fch.LineChartData) -> None:
    """Move one control mark out of sight, for a frame with no change to mark.

    Parked rather than removed: the pool of marks is fixed at construction
    and its members are moved from frame to frame, exactly as the traces
    are, so that a run full of adjustments costs no per-frame control
    construction. A parked mark is collapsed to a single point *and* put
    outside the plotted range, so it draws nothing whether the client
    clips first or renders a degenerate segment first.

    Parking is idempotent: an already-parked mark is written the same
    values, Flet's diff sees no change, and the client is sent nothing. A
    frame with no adjustments to mark therefore costs nothing at all.

    Args:
        series: Mark to park. Its two points are mutated.
    """

    for point in series.points:
        point.x = PARKED_CONTROL_MARK_X
        point.y = 0.0


def redraw_visible_window(
    plotted: Sequence[PlottedSeries],
    history: tuple[SimulationHistorySample, ...],
    window_start_s: float,
) -> None:
    """Redraw every trace from the samples inside the visible window.

    Only samples the chart can actually show are sent, and that window is
    decimated to a fixed per-trace budget, so the render payload is
    bounded by the window and the budget rather than by how long the
    simulation has been running. The controller's own history is read but
    never modified.

    Args:
        plotted: Every trace to redraw, each paired with the quantity it
            draws.
        history: Immutable simulation samples, oldest first, with elapsed
            time in seconds and compartment values as fractions.
        window_start_s: Earliest simulated time the chart displays, in
            seconds. Samples older than this are outside the plotted axis
            range and are not sent.
    """

    window_start_index = first_index_at_or_after(history, window_start_s, sample_elapsed_s)
    visible = history[window_start_index:]

    for series, value_for in plotted:
        redraw_series(series, visible, value_for, window_start_index)


def redraw_series(
    series: fch.LineChartData,
    visible: tuple[SimulationHistorySample, ...],
    value_for: SampleValue,
    index_offset: int = 0,
) -> None:
    """Set one trace to its visible samples, bounded and in percent.

    The points a series already holds are reused: their `x` and `y` are
    overwritten in place, and the list is extended or truncated only for
    the difference in count. Building a fresh `fch.LineChartDataPoint`
    per drawn sample per frame is what PL-010 removed - it cost about
    6 us each against 0.8 us to move an existing one, and at the
    per-trace ceiling across six traces that was substantially the whole
    frame.

    Reuse is only safe because Flet's diff reports an in-place mutation:
    it records the assignment on the point itself, so the client is sent
    the moved coordinate rather than nothing. PL-001 declined this
    optimization while that was unconfirmed, since a mutation the diff
    missed would leave the chart drawing the previous frame beneath the
    current frame's readouts. `tests/integration/test_chart_patching.py`
    holds the guarantee against the real Flet session and says how it
    was confirmed against a browser.

    Every drawn point remains a recorded sample: values are converted
    from fraction to percent, never interpolated or synthesized, and the
    controller's own history is read but not modified.

    Args:
        series: Trace to redraw. Its existing points are mutated.
        visible: Simulation samples inside the plotted time range.
        value_for: Function selecting one fraction from a sample.
        index_offset: Absolute index, within the whole recorded run, of
            `visible[0]`. Passed through so that decimation anchors its
            buckets to the run rather than to the window, which is what
            keeps a point's chosen sample - and therefore the patch the
            client is sent - unchanged from one frame to the next.
    """

    values = [value_for(sample) for sample in visible]
    # Both raise before anything is written, so a trace is never left
    # holding half of one frame and half of the next.
    indices = select_envelope_indices(values, MAX_CHART_POINTS_PER_SERIES, index_offset)

    points = series.points
    reused = min(len(points), len(indices))

    for position in range(reused):
        index = indices[position]
        point = points[position]
        point.x = visible[index].elapsed_s
        point.y = values[index] * 100.0

    if len(indices) > reused:
        points.extend(
            fch.LineChartDataPoint(visible[index].elapsed_s, values[index] * 100.0)
            for index in indices[reused:]
        )
    elif len(points) > reused:
        # Points past the drawn count are the previous frame's samples,
        # carrying their own time and value. Left in place the chart
        # would draw them as part of the current trace.
        del points[reused:]
