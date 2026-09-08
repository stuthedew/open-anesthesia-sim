"""Assemble the compartment chart's traces and redraw them from the run.

The shaping layer between the controller's evaluated window and the chart
control: which instants a trace draws is `core/run_score.py`'s, what a
trace *is* and how a frame updates it is this module's, and the dashboard
that owns the chart is `simulation_view.py`'s. Nothing here reads
simulation state, holds a setting, or performs a physiological or unit
calculation beyond the fraction-to-percent conversion the axis is labelled
in. The one derived quantity it draws, the wash-in ratio, is computed and
bounded by `app/wash_in.py` and only *placed* here.

It is separate from the view because what a trace draws is a
presentation-correctness concern rather than a layout one. Plotting one
compartment's values on another compartment's line would misstate the run
as surely as a wrong number would, so the pairing is passed in as one
`PlottedSeries` table the caller declares beside its traces, where it can
be audited at a glance, rather than being spread across a dashboard. The
table is not type-enforced - `flet_charts` ships no stubs, so a chart
series is `Any` to the checker - and `tests/unit/test_simulation_view.py`'s
`test_chart_traces_stay_bound_to_their_own_compartment` is what holds it.

**Every drawn point is a state of the run at the instant it is drawn at.**
Nothing in this module interpolates, extrapolates or synthesizes a value:
the coordinates it writes are the ones `DrawnWindow` carries, evaluated
from the run's score at instants chosen so that no sharp feature falls
between two of them (`PL-2FM6`). The straight segment the chart rules
between two points is the chart's own rendering, and it is honest here
because a control event always gets its own column.
"""

from collections.abc import Iterable, Sequence
from typing import Final

import flet_charts as fch

from anesthesia_sim.app.controller import DrawnWindow, RecordedSeries
from anesthesia_sim.app.wash_in import is_wash_in

__all__ = [
    "CHART_COLUMN_BUDGET_PER_SERIES",
    "PARKED_CONTROL_MARK_X",
    "PlottedSeries",
    "WASH_IN_TERMINUS_MARKER",
    "apply_point_tooltips",
    "build_control_mark",
    "build_point",
    "build_reference_line",
    "build_series",
    "park_control_mark",
    "park_series",
    "redraw_control_mark",
    "redraw_points",
    "redraw_reference_band",
    "redraw_reference_line",
    "redraw_series",
    "redraw_visible_window",
    "redraw_wash_in_segments",
]

# Per-trace ceiling on the *grid columns* an axis is divided into, which the
# chart's evaluated instants are placed on. The count of points follows from
# it rather than being set: the grid columns inside the drawn range, plus the
# two ends of that range, plus one column per control event in the window -
# bounded in turn by the marks the chart already draws
# (`simulation_view.MAX_CHART_CONTROL_MARKS`).
#
# It was a bucket count while the chart selected recorded samples, and a point
# ceiling before that when the algorithm was min/max envelope decimation. It
# is now the resolution the run is *evaluated* at, which is the first time the
# number has meant a spacing rather than a summary (`PL-2FM6`).
#
# 150 columns across a chart a few hundred pixels wide is already finer than
# the display can resolve.
#
# What this ceiling does *not* bound is how many drawn points move on a frame.
# That is a property of where the columns sit: `RunScore.evaluate_anchored`
# anchors them to multiples of the spacing measured from `t = 0`, so a window
# following the run keeps every interior column and moves only its right-hand
# end. PL-Q197 found every drawn point moving on every frame, and 1 788 of
# them at 5 Hz saturated the Flutter client while Python idled;
# `tests/integration/test_chart_patching.py` is what keeps that fixed.
#
# **What it does bound is the frame, and this number is the only lever on
# it.** Decided by the project owner on 2026-09-08, closing `PL-YDKJ`: the
# chart goes on patching one Flet control per plotted point, and the ceiling
# that buys is accepted rather than engineered around. Flet's `object_patch`
# walks every control on the page on every `page.update()` whether or not any
# of them moved - `PL-YSZN` measured an idle update at the cost of a full
# frame, both linear in the point count at about 24.5 us each - so the
# chart's share of a frame is this budget times the traces drawn times that
# constant, and nothing about where the columns sit can reduce it.
#
# So the ceiling this budget sizes against is a frame, not a wire. Halving
# this number halves the chart's share of one: measured 2026-09-08, a
# saturated frame at 300x fell from 42.8 ms to 28.3 ms at 75 columns, against
# a 200 ms budget. That is the trade to make if a future chart wants more
# traces or a faster cadence - fewer columns, and less trace resolution for
# them - and it is the whole of what is available, because the two routes
# that would remove the per-point cost were measured and both lose.
# `docs/WORKING_NOTES.md` § "Measured and answered: a server-rendered chart
# is not the way out" carries those measurements and why option 4, a sweep
# display, buys this path nothing: the walk is indifferent to what moved.
CHART_COLUMN_BUDGET_PER_SERIES: Final = 150

#: One chart trace bound to the recorded series it draws.
#:
#: The series names a substance as well as a compartment (`RecordedSeries`),
#: so the pairing this table exists to make auditable covers both: a line
#: carrying another substance's values is the same class of misstatement as
#: one carrying another compartment's.
type PlottedSeries = tuple[fch.LineChartData, RecordedSeries]


def build_point(x: float, y: float) -> fch.LineChartDataPoint:
    """One chart point, built without the library's default tooltip.

    **The single constructor of a plotted point in this application**, so
    that what a point carries is decided once. `fch.LineChartDataPoint`
    defaults `tooltip` to a `LineChartDataPointTooltip`, which itself holds
    a full seventeen-field `ft.TextStyle`, and Flet's `object_patch`
    descends into both on every point on every frame. Measured 2026-09-08
    on a saturated chart at 300x: `page.update()` fell from 42.8 ms to
    22.5 ms with those objects gone, against a 200 ms frame - roughly half
    the cost of a frame, for a tooltip nothing here ever writes text into
    (`PL-KP7H`).

    The cost is the *walk* rather than the patch: the same measurement
    found `page.update()` on a chart where nothing had changed since the
    last one costing what a full frame costs, and both linear in the number
    of point controls on the page at about 24.5 us each. So it is paid on
    every frame whether or not a trace moved, which is why a point that
    carries nothing it does not need is worth the constructor
    (`PL-YSZN`).

    Points are built without one and given one back by
    `apply_point_tooltips` while the run is paused, which is where the
    interface offers the hover. Building them the other way round - with a
    tooltip, stripped while running - would mean every point appended
    mid-run arrived carrying the cost this exists to remove.

    Args:
        x: Horizontal coordinate, in the chart's own axis units.
        y: Vertical coordinate, in the chart's own axis units.

    Returns:
        A Flet chart point that answers no hover until one is applied.
    """

    return fch.LineChartDataPoint(x, y, tooltip=None)


def apply_point_tooltips(series: Iterable[fch.LineChartData], *, enabled: bool) -> None:
    """Give every point of these series a hover tooltip, or take it away.

    The mechanical half of the paused-only hover; `SimulationView`'s
    `_apply_chart_tooltips` is the one caller and decides *when*. Writing
    the same value a point already holds is free on the wire - Flet's diff
    compares values rather than trusting an assignment - so this may be
    called on every frame without the running frames paying for it in
    traffic.

    A tooltip is built per point rather than shared between them: they are
    identical today, and one instance behind two thousand points is a
    footgun the moment `PL-YLKR` gives a point its own text.

    Args:
        series: The chart series to write across. Every point of each is
            written, drawn or parked, so a series is never half in one
            state.
        enabled: Whether a hover over these points should answer.
    """

    for one in series:
        for point in one.points:
            point.tooltip = fch.LineChartDataPointTooltip() if enabled else None


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
        points=[build_point(0.0, 0.0)],
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
    height the chart's own axis gives meaning to, and it names no
    `RecordedSeries` because there is no sample to read. Keeping the two apart
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
        points=[build_point(0.0, 0.0), build_point(0.0, 0.0)],
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
    upper_edge: fch.LineChartData,
    lower_edge: fch.LineChartData,
    start_x: float,
    end_x: float,
    lower_y: float,
    upper_y: float,
) -> None:
    """Span one reference *band* across the visible window between two heights.

    The band is drawn as **two stroked edges** with a light fill between
    them: the upper series carries the fill, cut off at `lower_y` by
    `below_line_cutoff_y` so it is a bounded band rather than everything
    under a line, and the lower series strokes the boundary that cut-off
    makes. Both strokes sit on the published boundaries, so the drawn extent
    is the data extent exactly - a band drawn thicker than its two edges
    would assert a wider population spread than the literature supports,
    which is why the fix for a band too thin to read is a second stroke and
    never a minimum height (`PL-90Y6`).

    Stroking only the upper edge is what made the mark read as a line. A
    stroked top over an unstroked fill is the geometry of a line with a
    shadow under it, whatever the fill's extent; two strokes with a gap
    between them is the geometry of an interval, and stays one at any
    thickness the axis leaves.

    Args:
        upper_edge: Series drawn at the band's upper boundary, carrying the
            fill. Its two points are mutated, and its fill cutoff is set to
            the lower boundary.
        lower_edge: Series drawn at the band's lower boundary. Its two
            points are mutated.
        start_x: Left edge of the visible window, in simulated seconds.
        end_x: Right edge of the visible window, in simulated seconds.
        lower_y: Lower edge of the band, in the chart's percent unit.
        upper_y: Upper edge of the band, in the chart's percent unit.
    """

    redraw_reference_line(upper_edge, start_x, end_x, upper_y)
    upper_edge.below_line_cutoff_y = lower_y
    redraw_reference_line(lower_edge, start_x, end_x, lower_y)


def build_control_mark(
    color: str, stroke_width: float, dash_pattern: list[int] | None = None
) -> fch.LineChartData:
    """Build one vertical mark for a recorded control change.

    A third kind of series, and separate from both constructors above for
    the same reason they are separate from each other. A trace draws
    recorded samples; a reference draws a published constant; a control
    mark draws neither - it says only that the run's inputs changed here,
    which is an event on the time axis rather than a value on the
    concentration one. It names no `RecordedSeries`, so it can never join
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
        points=[build_point(0.0, 0.0), build_point(0.0, 0.0)],
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


def redraw_visible_window(plotted: Sequence[PlottedSeries], window: DrawnWindow) -> None:
    """Redraw the traces the caller is drawing, from the window it asked for.

    The window arrives already cut to the axis the caller is about to draw:
    the controller answers `drawn_window` with the part of that axis the run
    covers, so nothing outside the plotted range crosses that boundary in
    the first place and there is nothing to slice off here (`PL-0VM7`).
    Every trace draws the same instants - one evaluation of the score
    serves all of them, because a state carries every compartment at
    once - so a frame costs what it draws rather than what the window
    spans, and two traces cannot come from different instants.

    **The caller passes the traces it is drawing, not all of them.** A trace
    left out is *not blanked*: it keeps the points of the frame it was last
    passed in, which is deliberate - a trace a reader has hidden costs
    nothing per frame, and costs nothing to restore. The obligation that
    comes with it is the caller's: a trace it stops passing must also come
    off the chart's own series list, or the chart goes on drawing a curve
    that has stopped advancing while the readouts beside it have not.
    `simulation_view.py`'s `_visible_plotted_series` and `_chart_data_series`
    are built from one flag for exactly that reason (`PL-CG7J`).

    Args:
        plotted: Every trace to draw this frame, each paired with the
            series it draws. A trace omitted is left holding its previous
            points.
        window: The states this frame draws, evaluated from the run's score.
    """

    for series, recorded in plotted:
        redraw_series(series, window, recorded)


def redraw_series(series: fch.LineChartData, window: DrawnWindow, recorded: RecordedSeries) -> None:
    """Set one trace to its evaluated columns, in percent.

    `redraw_points` does the writing and records why the points a series
    already holds are reused rather than rebuilt.

    **Every drawn point is a state of the run at the instant it is drawn
    at**, evaluated from the score rather than selected from recorded
    samples (`PL-2FM6`). Nothing between two drawn points is interpolated
    by this code - the straight segment the chart rules between them is the
    chart's own rendering - and the columns are placed so that no sharp
    feature falls between them: `RunScore.evaluate_anchored` puts one on
    every control event in the window, and between events the trajectory
    is a sum of exponentials with no hidden transients.

    That is what `PL-4RBD` asked for and could not get from a selection of
    recorded extremes: a dial change that left the trace rising was not an
    extreme of anything, so no selection rule reached it and the polyline
    was drawn straight through the one instant a reader was looking for.

    Args:
        series: Trace to redraw. Its existing points are mutated.
        window: The states this frame draws.
        recorded: Which substance's quantity this trace draws. Raises
            through `DrawnWindow.compartment_fractions` if the window
            describes another substance, rather than drawing whichever one
            it does hold.
    """

    # Raises before anything is written, so a trace is never left holding
    # half of one frame and half of the next.
    fractions = window.compartment_fractions(recorded)

    redraw_points(
        series,
        [
            (elapsed_s, fraction * 100.0)
            for elapsed_s, fraction in zip(window.times_s, fractions, strict=True)
        ],
    )


def redraw_points(series: fch.LineChartData, coordinates: Sequence[tuple[float, float]]) -> None:
    """Set one series to exactly these points, reusing the ones it holds.

    The mechanical half of `redraw_series`, factored out because the
    wash-in ratio is drawn in its own dimensionless unit rather than in
    percent: the conversion into the axis's unit belongs to the caller
    that knows which axis it is drawing against, and the point reuse
    below belongs to every caller equally.

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

    Args:
        series: Series to redraw. Its existing points are mutated.
        coordinates: Every point to draw, in the chart's own axis units,
            ordered along the x axis.
    """

    points = series.points
    reused = min(len(points), len(coordinates))

    for position in range(reused):
        x, y = coordinates[position]
        point = points[position]
        point.x = x
        point.y = y

    if len(coordinates) > reused:
        points.extend(build_point(x, y) for x, y in coordinates[reused:])
    elif len(points) > reused:
        # Points past the drawn count are the previous frame's samples,
        # carrying their own time and value. Left in place the chart
        # would draw them as part of the current trace.
        del points[reused:]


def park_series(series: fch.LineChartData) -> None:
    """Draw nothing for this series, without discarding its point controls.

    The counterpart of `park_control_mark` for a trace: the pool of
    wash-in segments is fixed at construction and its members are moved
    from frame to frame, so an unused one is emptied rather than removed.
    Truncating to zero points is what makes it draw nothing; the series
    itself stays in the chart's `data_series`, where the next frame can
    fill it again without constructing anything.

    Parking is idempotent - an already-parked series is left with the
    same empty point list, Flet's diff sees no change, and the client is
    sent nothing.

    Args:
        series: Series to empty. Its point list is mutated.
    """

    redraw_points(series, ())


def redraw_wash_in_segments(
    segment_series: Sequence[fch.LineChartData],
    window: DrawnWindow,
    substance_id: str,
    extension_ceiling: float,
) -> int:
    """Draw F_A/F_I over the visible window, broken where it is not defined.

    One series per *contiguous* stretch of samples inside the wash-in
    domain `app/wash_in.py` states, rather than one series over every
    such sample. The difference is the whole reason this function
    exists: a single polyline through the drawn samples would draw a
    straight line across the stretch it skipped - a segment joining two
    real points through values the run never produced, which is the
    synthesized trace this module is careful never to create. A broken
    line asserts nothing about the gap.

    Which columns those are is decided here, from the quotient at each
    drawn instant: there are only the columns being drawn, so classifying
    all of them is proportional to the frame rather than to the run.

    **A stretch is extended by its crossing column at each end**, where
    one exists inside the window and within `extension_ceiling`. Without
    it the curve stops at the last column at or below equilibrium, short
    of the boundary it stopped at, and a trace halting in
    clear space short of a line reads as clipped rather than finished.
    With it the curve meets the equilibrium reference and ends on it.

    The ceiling is what keeps that one out-of-domain point on the plot.
    A run stepped at 0.1 s crosses equilibrium by a hair - measured
    across every agent and every supported alveolar ventilation and
    cardiac output at the maximum fresh gas flow, the first sample above
    it reaches 1.00235 - but the ratio is not continuous in general:
    `BreathingCircuit.set_circuit_volume` conserves the agent in the
    circuit while changing the volume it is divided by, so a circuit
    volume doubled between two steps halves F_I and doubles the ratio.
    No interface control does that today, and a rule that holds only
    because a slider is missing is not one to rely on. A crossing sample
    above the ceiling is therefore not drawn, and the stretch ends where
    it did before: not clamped to the ceiling, not interpolated onto it -
    simply a point outside what this plot can show.

    Every segment draws the window's own columns, so a stretch that is not
    changing keeps the same instants from frame to frame - the anchoring
    `RunScore.evaluate_anchored` provides, and the property that keeps the
    client from being sent points that did not move. There is no budget to
    split between segments: they all read one evaluation of the score, so
    what a point sits at cannot depend on how many *other* segments happen
    to be on screen.

    A stretch one sample long draws a single point and so shows nothing,
    which is correct: at a 0.1 s step it is a stretch too short for the
    chart to resolve, and inventing an extent for it would overstate it.

    Args:
        segment_series: Fixed pool of traces to draw the segments into.
            Every member is mutated - filled with a segment, or emptied.
        window: The part of the run inside the plotted time range.
            Already cut to the axis by the controller (`PL-0VM7`), so
            nothing outside the plotted range reaches here to be sliced
            off.
        substance_id: Whose F_A/F_I. The quotient is formed from one
            substance's own two fractions, so it is that substance's
            trace and its own stretches that are drawn here.
        extension_ceiling: Highest ratio a crossing sample may carry and
            still be drawn, in the chart's own dimensionless unit. The
            caller owns it because it is a property of the axis rather
            than of the model.

    Returns:
        How many segments inside the window the pool could not draw. The
        pool holds the most recent that fit, so what is dropped is the
        oldest; a caller displaying the trace must say so rather than
        letting the curve end without explanation.
    """

    quotients = window.wash_in_quotients(substance_id)
    segments = _wash_in_segments(quotients, extension_ceiling)
    drawn = segments[-len(segment_series) :] if segment_series else []

    for series, (start, stop) in zip(segment_series, drawn, strict=False):
        # Every column of a stretch has a quotient: the anchors are inside
        # the domain, and the one extending column at each end was chosen
        # for having one. `_wash_in_segments` is where that holds.
        ratios = [quotients[column] for column in range(start, stop)]
        redraw_points(
            series,
            [
                (window.times_s[column], ratio)
                for column, ratio in zip(range(start, stop), ratios, strict=True)
                if ratio is not None
            ],
        )
        last = ratios[-1]
        _mark_wash_in_terminus(
            series, ends_above_equilibrium=last is not None and not is_wash_in(last)
        )

    for series in segment_series[len(drawn) :]:
        park_series(series)

    return len(segments) - len(drawn)


#: The dot a wash-in stretch ends on when it stopped by crossing equilibrium.
#:
#: A line that simply stops is indistinguishable from a line the frame cut
#: off, and this one stops while still climbing steeply, which is the shape
#: that reads as clipped. A terminal dot is the ordinary scientific-plotting
#: answer: it says the series ends here rather than continuing out of view.
#: It takes the trace's own colour from the chart, so it declares no pair of
#: its own for `tools/contrast_check.py`.
WASH_IN_TERMINUS_MARKER: Final = fch.ChartCirclePoint(radius=3.5)


def _mark_wash_in_terminus(series: fch.LineChartData, ends_above_equilibrium: bool) -> None:
    """Put the terminus dot on this stretch's last point, or on none of them.

    Every other point is cleared first, because `redraw_points` reuses the
    point objects a series already holds: a marker left on whichever index
    was last in the previous frame would sit in the middle of a stretch
    that has since grown. The clear reads every point and writes only
    where a marker is actually set, so a frame that changes nothing sends
    nothing.

    Args:
        series: Stretch to mark. Its points' markers are mutated.
        ends_above_equilibrium: Whether this stretch's last point is the
            crossing sample rather than the live end of the run. Only a
            stretch that *stopped* is marked; the growing right-hand end
            of a run is not an ending, and a dot there would move every
            frame while saying nothing.
    """

    for point in series.points:
        if point.point is not None:
            point.point = None

    if ends_above_equilibrium and series.points:
        series.points[-1].point = WASH_IN_TERMINUS_MARKER


def _wash_in_segments(
    quotients: Sequence[float | None], extension_ceiling: float
) -> list[tuple[int, int]]:
    """The stretches the chart draws, as ranges over the drawn columns.

    A column *anchors* a stretch when its quotient is inside the wash-in
    domain `app/wash_in.py` states. A column *extends* one when it has a
    quotient at all - its denominator was above the display floor - that
    quotient is no higher than `extension_ceiling`, and it neighbours an
    anchor. So a stretch is a run of in-domain columns plus, at each end,
    the one crossing column that shows where the curve left the domain and
    that the plot can still show.

    **Computed over the drawn columns rather than maintained as the run
    records samples** (`PL-2FM6`). The run kept these stretches
    incrementally because reclassifying every sample a window spanned was
    work proportional to the run; there are now only the columns being
    drawn, so classifying all of them is proportional to the frame. It is
    also the stronger guarantee: a boundary can fall only on an instant the
    chart actually plots.

    Two anchor runs separated by a single extendable column both reach it,
    and it is drawn once as each stretch's endpoint. That is the honest
    rendering of a run that left the domain and returned within one column,
    and it is the only case where one column appears twice.

    Args:
        quotients: One entry per drawn column, `None` where the column has
            no quotient at all.
        extension_ceiling: Highest quotient a crossing column may carry and
            still extend a stretch.

    Returns:
        One `(start, stop)` pair of column indices per stretch, oldest
        first, extended within the window.
    """

    segments: list[tuple[int, int]] = []
    start: int | None = None

    for column, quotient in enumerate(quotients):
        anchors = quotient is not None and is_wash_in(quotient)

        if anchors and start is None:
            start = column
        elif not anchors and start is not None:
            segments.append((start, column))
            start = None

    if start is not None:
        segments.append((start, len(quotients)))

    return [
        (
            start - 1 if _extends_a_stretch(quotients, start - 1, extension_ceiling) else start,
            stop + 1 if _extends_a_stretch(quotients, stop, extension_ceiling) else stop,
        )
        for start, stop in segments
    ]


def _extends_a_stretch(
    quotients: Sequence[float | None], column: int, extension_ceiling: float
) -> bool:
    """Whether the column at `column` is the crossing point to draw.

    `None` is how a column with no quotient at all is carried -
    `app/wash_in.py`'s rule 1, no agent in the circuit yet - and there is
    nothing there to draw. Every other out-of-domain column crossed
    equilibrium, and it is drawn when it is close enough to stay on the
    plot. A column outside the window extends nothing, which is what the
    bounds check answers rather than an error: a stretch running to the
    edge of the frame simply has no crossing column on that side yet.
    """

    if not 0 <= column < len(quotients):
        return False

    quotient = quotients[column]

    return quotient is not None and quotient <= extension_ceiling
