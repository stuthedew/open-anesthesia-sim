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
    "build_series",
    "circuit_value",
    "fat_value",
    "mixed_venous_value",
    "muscle_value",
    "redraw_series",
    "redraw_visible_window",
    "sample_elapsed_s",
    "vessel_rich_value",
]

# Per-trace ceiling on points handed to the chart. Each point is a Flet
# control, so this ceiling — not the length of the run — sets the cost of a
# frame: `redraw_series` moves the points already drawn rather than
# rebuilding them (PL-010), which leaves the per-frame work proportional to
# this number rather than to it times the cost of a construction. 300 points
# across a chart a few hundred pixels wide is already finer than the display
# can resolve.
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

    visible = history[first_index_at_or_after(history, window_start_s, sample_elapsed_s) :]

    for series, value_for in plotted:
        redraw_series(series, visible, value_for)


def redraw_series(
    series: fch.LineChartData, visible: tuple[SimulationHistorySample, ...], value_for: SampleValue
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
    """

    values = [value_for(sample) for sample in visible]
    # Both raise before anything is written, so a trace is never left
    # holding half of one frame and half of the next.
    indices = select_envelope_indices(values, MAX_CHART_POINTS_PER_SERIES)

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
