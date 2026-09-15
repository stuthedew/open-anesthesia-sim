"""What one frame of the concentration chart and the wash-in plot draws.

The chart's model: everything a frame puts on either plot, as plain values,
evaluated from the run and independent of the toolkit that paints it.
`app/qt_chart.py` reads a `ChartFrame` and moves pyqtgraph items to match;
nothing here imports Qt, Flet or numpy, and nothing here holds a widget.
The split is the one `app/formatting.py` makes for a displayed string: what
the chart *claims* - which compartment a curve carries, where the 1 MAC line
stands, which instants are drawn, what a hover says - is a
presentation-correctness question, and it is readable and testable without
a display. `tests/unit/test_chart_frame.py` holds it that way.

**Every drawn point is a state of the run at the instant it is drawn at.**
`SimulationController.drawn_window` evaluates the run's definition at the
columns the axis is divided into, plus one column per control event in the
window and the two ends of the drawn range (`PL-2FM6`), so nothing here
interpolates, extrapolates or synthesizes a value. The straight segment a
plot rules between two points is the plot's own rendering, and it is honest
twice over: a control event always gets its own column, and the columns are
one per pixel of the plot they are drawn on (`chart_columns`, `PL-GS3R`), so
no segment is wider than a pixel of time.

**One evaluation serves every trace of a run.** A state carries every
compartment at once, so a frame reads the window once per run and every
trace of that run draws the same instants. Two traces of one run cannot come
from different instants, and the wash-in stretches are formed from the very
columns the compartment chart drew, so the two plots cannot differ even by
a step the run took in between.

**Six compartment traces, and the table that binds each to what it draws.**
`COMPARTMENT_TRACES` is the one place a compartment meets its colour, its
dash pattern, its legend words and the gloss its hover carries. Plotting one
compartment's values on another's line misstates the run exactly as a wrong
number does, so the pairing is one record per trace rather than parallel
lists, and `app/qt_chart.py` draws its curves and its legend from this one
rather than keeping a second copy (`PL-2CS8`).

**The window is a viewport and the run fills it.** The axis a frame draws
is decided here from the selected time base and the longest run on the
chart - fitted to the run under "Fit run", or held at the chosen width and
following the newest instant - and every run draws into that one window.
`app/chart_time_base.py` carries both rules and why they are not one.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass
from math import ceil, floor, isfinite, sqrt
from types import MappingProxyType
from typing import Final

from anesthesia_sim.app.chart_time_base import (
    ChartTimeBase,
    fit_to_run,
    fitted_window,
    following_window,
    tick_times,
)
from anesthesia_sim.app.control_timeline import ControlAdjustment
from anesthesia_sim.app.controller import (
    COMPARTMENT_QUANTITIES,
    DrawnWindow,
    RecordedQuantity,
    RecordedSeries,
    SimulationController,
    SimulationSnapshot,
)
from anesthesia_sim.app.formatting import (
    chart_axis_top_percent,
    chart_grid_interval_percent,
    format_elapsed,
    format_mac_multiple,
    format_percent,
    format_wash_in_ratio,
    mac_awake_band_percent,
    mac_axis_ticks,
)
from anesthesia_sim.app.theme import (
    ALVEOLAR_COLOR,
    CIRCUIT_COLOR,
    FAT_COLOR,
    MIXED_VENOUS_COLOR,
    MUSCLE_COLOR,
    VESSEL_RICH_COLOR,
)
from anesthesia_sim.app.wash_in import WASH_IN_EQUILIBRIUM_RATIO, is_wash_in
from anesthesia_sim.core.concentration import Fraction, Percent, percent_from_fraction
from anesthesia_sim.core.uptake_system import MAXIMUM_SIMULATION_STEP_S

__all__ = [
    "CHART_COLUMN_BUDGET_PER_SERIES",
    "COMPARTMENT_TRACES",
    "HOVER_INSTANT_RESOLUTION_S",
    "MAX_CHART_CONTROL_MARKS",
    "MAX_CHART_WASH_IN_SEGMENTS",
    "WASH_IN_AXIS_MAXIMUM",
    "WASH_IN_GRID_INTERVAL",
    "WASH_IN_HOVER_LABEL",
    "WASH_IN_TERMINUS_CEILING",
    "ChartFrame",
    "HoverTarget",
    "RunFrame",
    "RunInput",
    "TraceStyle",
    "WashInStretch",
    "assemble_chart_frame",
    "chart_columns",
    "format_trace_hover",
    "format_wash_in_hover",
    "nearest_trace_point",
    "nearest_wash_in_point",
    "percent_axis_ticks",
    "trace_style",
    "wash_in_axis_ticks",
    "wash_in_stretches",
]

# Floor on the *grid columns* an axis is divided into, which the chart's
# evaluated instants are placed on. The count a frame actually uses is decided
# by `chart_columns` from the width of the plot in pixels - one column per
# pixel boundary, so that no chord ruled between two drawn instants is wider
# than a pixel of time (`PL-GS3R`, decided 2026-09-14) - and this is what it
# answers for a plot narrower than 150 px, or one not yet laid out. The count
# of points follows from it rather than being set: the grid columns inside
# the drawn range, plus the two ends of that range, plus one column per
# control event in the window - bounded in turn by the marks the chart already
# draws (`MAX_CHART_CONTROL_MARKS`).
#
# It was a bucket count while the chart selected recorded samples, a point
# ceiling before that when the algorithm was min/max envelope decimation, and
# a fixed budget from `PL-2FM6` until `PL-GS3R`: 150 columns at every width,
# which at the 12-hour base ruled a 290 s chord through the steep early
# wash-in and drew the alveolar trace up to 0.53 pp (sevoflurane 2% to 4%)
# and 3.8 pp (a desflurane overpressure induction) below the run. The floor
# stays at the number the fixed budget was because nothing narrower has been
# measured: it is the count the Flet chart, which could afford no more
# (`PL-YSZN`, `PL-YDKJ`), drew at until `PL-25KS` retired it.
CHART_COLUMN_BUDGET_PER_SERIES: Final = 150

# How many control marks the chart can stand at once. A fixed pool rather than
# a mark per adjustment, so a run full of adjustments costs no per-frame
# construction and the bound is stated: what the pool cannot show is counted
# on the display rather than dropped in silence (`docs/MODEL.md` § "The
# control-input timeline", "Bounds are displayed, not silent").
MAX_CHART_CONTROL_MARKS: Final = 24

# Gridlines at quarter-fractions, which is the ruling every published wash-in
# figure carries and the spacing a reader compares against. The axis is
# labelled at exactly these values rather than at whatever interval a plot
# would choose for itself: a rule at 0.25 beside a label at 0.2 puts two
# different scales on one axis, and a reader taking a value off the nearest
# gridline would take it off the wrong one. The same rule holds the
# compartment chart's percent axis to its own gridlines - `percent_axis_ticks`
# - which is what `PL-Q4VH` asked for.
WASH_IN_GRID_INTERVAL: Final = 0.25

# The wash-in axis stands above equilibrium rather than at it, which is a
# legibility requirement rather than a spare margin. The trace ends where it
# crosses `WASH_IN_EQUILIBRIUM_RATIO`, and with the axis topping out there
# that ending lands on the frame - where a line that stopped and a line the
# plot cut off look exactly alike. Lifting the axis puts clear space above the
# ending, so the stop is visibly the trace's own. 1.15 leaves that space
# without adding a fifth labelled interval: the ruling and the labels stop at
# 1.00, which is where the readable scale ends.
WASH_IN_AXIS_MAXIMUM: Final = 1.15

# How far past equilibrium the trace may be drawn so that its ending lands on
# the line rather than a step short of it. `wash_in_stretches` carries the
# whole reasoning, including why the bound is stated rather than taken from
# the measured 1.00235 a 0.1 s step actually produces. Set below
# `WASH_IN_AXIS_MAXIMUM` rather than at it, so even the widest crossing this
# admits still has clear space above it.
WASH_IN_TERMINUS_CEILING: Final = 1.05

# How many separated stretches of wash-in the plot can draw at once. The trace
# breaks wherever the ratio leaves the domain `app/wash_in.py` states - a
# vaporizer turned off and later reopened is two stretches, not one line drawn
# through the washout between them - and the pool is fixed for the reason the
# control-mark pool is. Eight is more stretches than a taught case produces
# inside one chart window; what does not fit is counted and said, never
# dropped in silence.
MAX_CHART_WASH_IN_SEGMENTS: Final = 8

# The second line of the wash-in trace's hover readout: what the value is.
# The parenthesis is the caption `app/wash_in.py` already carries, for the
# reason stated there - F_I is the modelled circuit rather than the vaporizer
# dial - and `docs/MODEL.md` § "The chart's hover readout: what the tooltip
# may show" is where the three-line form is derived. A solidus rather than
# a division sign, because every non-ASCII character that reaches a reader
# has to have been rendered and seen first (`tools/glyph_check.py`).
WASH_IN_HOVER_LABEL: Final = "Wash-in F_A/F_I (alveolar / modelled circuit)"

# The resolution the hover states its instant at: the step the run advances
# by, which is also the clock's own resolution and the finest a control stamp
# carries. A drawn column sits wherever the anchored grid puts it - 410.7383 s
# on a thirty-minute axis - and the state reported is the state at exactly
# that instant, evaluated in closed form; but printing the instant to four
# decimals would claim a resolution no other display on the screen has and
# none a reader can use. Rounded to the tenth the clock steps at, the
# instant differs from the drawn one by at most 0.05 s, over which no
# compartment moves by a hundredth of a percent. Taken from the core's
# declared ceiling rather than written as a digit, for the reason the
# dashboard's own step is: the shipped step sits at that ceiling
# deliberately, and a second literal would drift from it silently.
HOVER_INSTANT_RESOLUTION_S: Final = MAXIMUM_SIMULATION_STEP_S

# The word that opens every hover readout. On every hover rather than only on
# the two compartments with a measured twin, because the readout is detached
# from the heading that would otherwise carry it: `docs/MODEL.md` § "The
# chart's hover readout" derives why the qualifiers precede the number.
_HOVER_MODELLED_MARKER: Final = "Modelled"


@dataclass(frozen=True, slots=True)
class TraceStyle:
    """One compartment trace: what it draws, how it is drawn, what it is called.

    Everything that has to agree about a single compartment, held in one
    record. Before `PL-G59B` the same trace was described in three places -
    the colour and dash pattern where the series was built, the compartment
    it draws in the `PlottedSeries` table, and the name and line-style words
    in a legend row six hundred lines away - and keeping them in agreement
    was left to whoever remembered. A legend that names a line the chart is
    not drawing misstates the run as surely as a wrong number does.

    Attributes:
        quantity: The one recorded quantity this trace draws.
            `DrawnWindow.compartment_fractions` resolves it to a state
            index, so this table keeps no second copy of that pairing.
        label: The compartment's name, as the legend and the hover say it.
        gloss: The clinical hedge the readout row draws under the name,
            or `None` where it draws none. Not decoration: "end-tidal-
            equivalent" and "inspired" are required hedges (`PL-NV9W`,
            `PL-8M05`), because what the model computes is a compartment
            and what a clinician would set beside it on a monitor is a
            different, measured thing. The hover readout carries it for the
            reason `docs/MODEL.md` § "The chart's hover readout" gives: a
            floating box has no readout row beside it to supply the hedge.
        color: The trace's line colour, from `app/theme.py`, and its legend
            swatch's.
        stroke_width: Line width in display pixels.
        dash_pattern: Alternating dash and gap lengths in display pixels, or
            `None` for a solid line. The separating channel rather than
            decoration: `theme.py` records that the four simulated
            colour-vision models put pairs of these six colours as close as
            1.01, far under the 3:1 that would make colour sufficient, and
            `docs/MODEL.md` § "The six compartment traces" carries the table
            this pattern is read off.
        line_style: The dash pattern in words, for the legend. Kept beside
            the pattern it describes rather than in the legend's own code,
            so "dotted" cannot come to describe a line that is not.
    """

    quantity: RecordedQuantity
    label: str
    gloss: str | None
    color: str
    stroke_width: float
    dash_pattern: tuple[int, ...] | None
    line_style: str


# The six compartment traces, in the order they are drawn and listed.
#
# **Six patterns, all different, because the line style is what actually
# separates these curves.** The colours cannot: the closest pair sits at 1.01
# for normal colour vision and no palette reaches 3:1. Circuit and vessel-rich
# were both solid until `PL-GVXP`, which made the second channel redundant in
# name only for the one pair - and a reader who takes a value off the wrong
# curve has misread a clinical quantity, not a decoration.
#
# **Which style goes on which trace is decided by the colours, not chosen
# freely.** The two traces a reader can least separate by colour get the two
# marks they can most separate by shape, and so on outward. So the closest
# pairs - vessel-rich against fat at 1.01, and mixed venous against fat at
# 1.02 under simulated deuteranopia - are an even dash against an alternating
# dash-dot, and a short uniform dash against that same dash-dot: each differs
# from its partner in mark length, in gap length and in rhythm at once. The
# one genuinely confusable pair in the set, the 2 px dots against the 4 px
# short dash, is spent on mixed venous against muscle, which is the *widest*
# separation any pair of these six has (1.45). `docs/MODEL.md` carries the
# matrix this was read off.
#
# The vessel-rich trace's equal mark and gap is the one rhythm no other trace
# here has: the other four dashed traces all draw more ink than gap.
# Deliberately not a second long dash - at [8, 8] it read as the alveolar
# trace's [10, 4] with wider gaps, and those two sit at 1.08 under simulated
# deuteranopia, which is no place to put a pair that has to be told apart by
# mark length alone.
COMPARTMENT_TRACES: Final[tuple[TraceStyle, ...]] = (
    TraceStyle(RecordedQuantity.CIRCUIT, "Circuit", "inspired", CIRCUIT_COLOR, 3, None, "solid"),
    TraceStyle(
        RecordedQuantity.ALVEOLAR,
        "Alveolar",
        "end-tidal-equivalent",
        ALVEOLAR_COLOR,
        3,
        (10, 4),
        "long dash",
    ),
    TraceStyle(
        RecordedQuantity.MIXED_VENOUS,
        "Mixed venous",
        None,
        MIXED_VENOUS_COLOR,
        2,
        (4, 3),
        "short dash",
    ),
    TraceStyle(
        RecordedQuantity.VESSEL_RICH, "Vessel-rich", None, VESSEL_RICH_COLOR, 2, (6, 6), "even dash"
    ),
    TraceStyle(RecordedQuantity.MUSCLE, "Muscle", None, MUSCLE_COLOR, 2, (2, 3), "dotted"),
    TraceStyle(RecordedQuantity.FAT, "Fat", None, FAT_COLOR, 2, (12, 4, 2, 4), "dash-dot"),
)

_TRACE_STYLE_BY_QUANTITY: Final[Mapping[RecordedQuantity, TraceStyle]] = MappingProxyType(
    {style.quantity: style for style in COMPARTMENT_TRACES}
)


def trace_style(quantity: RecordedQuantity) -> TraceStyle:
    """The one trace that draws this compartment.

    Args:
        quantity: The recorded quantity to find the trace for.

    Returns:
        Its style record.

    Raises:
        KeyError: If no trace draws it - `RecordedQuantity.WASH_IN_RATIO`,
            which is a derived quantity with its own plot rather than a
            compartment on this one, or a quantity the table has lost.
    """

    return _TRACE_STYLE_BY_QUANTITY[quantity]


def chart_columns(plot_width_px: float) -> int:
    """Grid columns the axis is divided into, for a plot this many pixels wide.

    One column per pixel boundary - `plot_width_px` intervals across the
    axis, so one more column than that - floored at
    `CHART_COLUMN_BUDGET_PER_SERIES`. The rule `PL-GS3R` chose: hold the
    chord at one pixel of time, whatever the time base. Between two drawn
    instants no more than a pixel apart, both exact, a monotone run and the
    straight segment ruled between them cross every level inside the same
    pixel, so the drawn line is within a pixel of time of the run everywhere
    and on it at every drawn instant. The count therefore follows the plot
    rather than the span: a twelve-hour axis on a 1 000 px plot draws 1 001
    columns at a 43 s chord, and a fifteen-minute axis on the same plot draws
    1 001 columns at 0.9 s. `docs/MODEL.md` § "What the chart draws" carries
    the guarantee, what it leaves between drawn instants, and what was
    measured against it.

    The width is in logical pixels, as Qt lays the plot out, which is the
    resolution the axis is ruled and labelled at; a high-DPI display draws
    each chord across its device-pixel ratio's worth of device pixels.

    Args:
        plot_width_px: The width of the plot area the axis spans, in logical
            pixels. Zero for a plot not yet laid out, which answers the
            floor. A fractional width is rounded up.

    Returns:
        The number of grid columns, at least `CHART_COLUMN_BUDGET_PER_SERIES`.

    Raises:
        ValueError: If the width is negative or not finite. A caller that
            has no width says so by passing zero, not by passing whatever
            it holds.
    """

    if not isfinite(plot_width_px) or plot_width_px < 0.0:
        raise ValueError(
            f"a plot is a nonnegative, finite number of pixels wide, not {plot_width_px}"
        )

    return max(CHART_COLUMN_BUDGET_PER_SERIES, ceil(plot_width_px) + 1)


@dataclass(frozen=True, slots=True)
class WashInStretch:
    """One contiguous stretch of the F_A/F_I trace, as drawn.

    Attributes:
        times_s: The drawn instants, ascending, in simulated seconds.
        ratios: F_A/F_I at each, dimensionless, one per entry of `times_s`.
        ends_above_equilibrium: Whether the last point is the crossing
            column - the one drawn past equilibrium so the curve meets the
            reference line - rather than the live end of the run. Only a
            stretch that *stopped* carries the terminus marker; the growing
            right-hand end of a run is not an ending.
    """

    times_s: tuple[float, ...]
    ratios: tuple[float, ...]
    ends_above_equilibrium: bool


@dataclass(frozen=True, slots=True)
class RunFrame:
    """One run's part of a frame: its drawn states, stretches and marks.

    Attributes:
        agent_id: The substance every value here belongs to, under the
            identifier the run records it by.
        agent_display_name: The same agent as the hover names it.
        mac_percent: The agent's 1 MAC as a percent of one atmosphere - the
            divisor every MAC multiple in the hover is produced from, carried
            beside the values it scales so a readout cannot pair one agent's
            concentration with another's MAC.
        elapsed_s: The run's reach, in simulated seconds.
        times_s: The drawn instants, ascending, in simulated seconds. Shared
            by every compartment trace of this run, which is what makes it
            structurally impossible for two of them to come from different
            instants.
        fractions: Each compartment's value at every drawn instant, as a
            fraction of one atmosphere, keyed by the quantity the trace
            draws. Every compartment is present whether or not it is shown,
            because what a trace *draws* does not change with whether it is
            currently on the chart.
        wash_in: The F_A/F_I stretches drawn, oldest first - the most recent
            that fit the pool.
        undrawn_wash_in_stretches: How many stretches inside the window the
            pool could not draw. Displayed rather than hidden.
        control_marks_s: The simulated times marked, ascending - the most
            recent adjustments that fit the pool, so a reader watching a run
            is reading the change they just made against the curve it
            moved.
        undrawn_control_marks: How many adjustments inside the window the
            pool could not mark. Displayed rather than hidden.
    """

    agent_id: str
    agent_display_name: str
    mac_percent: float
    elapsed_s: float
    times_s: tuple[float, ...]
    fractions: Mapping[RecordedQuantity, tuple[float, ...]]
    wash_in: tuple[WashInStretch, ...]
    undrawn_wash_in_stretches: int
    control_marks_s: tuple[float, ...]
    undrawn_control_marks: int

    def percents(self, quantity: RecordedQuantity) -> tuple[float, ...]:
        """One trace's drawn values in the unit the percent axis is labelled in.

        The one fraction-to-percent conversion the chart makes, here rather
        than in the toolkit layer, so a factor of a hundred can be wrong in
        one place rather than in seven.

        Args:
            quantity: Which compartment.

        Returns:
            One percent per entry of `times_s`.
        """

        return tuple(
            percent_from_fraction(Fraction(fraction)) for fraction in self.fractions[quantity]
        )


@dataclass(frozen=True, slots=True)
class ChartFrame:
    """Everything one frame puts on the concentration chart and the wash-in plot.

    Attributes:
        time_base: The width the frame is drawn at, and the interval it is
            ruled at.
        fitted: Whether the width was derived from the run ("Fit run") or
            chosen by the reader. The caption states which, because the same
            plot showing fifteen minutes and twelve hours is two different
            claims about what a flat trace means.
        start_s: Left edge of the window, in simulated seconds.
        stop_s: Right edge of the window, in simulated seconds.
        tick_times_s: Where the gridlines and axis labels fall, on both
            plots - multiples of the interval measured from the case's zero,
            so the grid stands still as the window slides.
        columns: The grid columns the window was divided into: one per
            pixel boundary of `plot_width_px`, floored, per `chart_columns`.
        plot_width_px: The width of the plot the frame was drawn for, in
            logical pixels. Recorded so a frame says what it was drawn for,
            which is what makes its chord width checkable after the fact.
        mac_percent: The agent's 1 MAC as a percent of one atmosphere, the
            divisor every MAC-denominated mark below is placed against.
        axis_top_percent: Top of the compartment chart's percent axis.
        grid_interval_percent: Spacing of its horizontal rules.
        percent_ticks: Its left axis's labels, each at a gridline.
        mac_ticks: Its right axis's labels, as (percent position, MAC text).
        one_mac_percent: Where the 1 MAC line stands.
        mac_awake_band_percent: The MAC-awake band's lower and upper edges.
        visible: Which compartments are drawn, in table order. Presentation
            state only: it is never read by the simulation.
        runs: One `RunFrame` per run on the chart, in drawing order.
    """

    time_base: ChartTimeBase
    fitted: bool
    start_s: float
    stop_s: float
    tick_times_s: tuple[float, ...]
    columns: int
    plot_width_px: float
    mac_percent: float
    axis_top_percent: float
    grid_interval_percent: float
    percent_ticks: tuple[tuple[float, str], ...]
    mac_ticks: tuple[tuple[float, str], ...]
    one_mac_percent: float
    mac_awake_band_percent: tuple[float, float]
    visible: tuple[RecordedQuantity, ...]
    runs: tuple[RunFrame, ...]


@dataclass(frozen=True, slots=True)
class RunInput:
    """One run to draw, with the snapshot the same frame formats it from.

    Attributes:
        controller: The run.
        snapshot: Its state, read once by the caller for this frame and
            handed down here, so a run's readouts and the traces beside them
            are one instant of one run rather than two reads that happened
            to agree.
        adjustments: The run's control timeline, grouped into the acts a
            reader sees. The caller's `control_timeline.AdjustmentGrouping`
            supplies it, so a frame that recorded nothing regroups nothing.
    """

    controller: SimulationController
    snapshot: SimulationSnapshot
    adjustments: tuple[ControlAdjustment, ...]


def assemble_chart_frame(
    runs: Sequence[RunInput],
    time_base: ChartTimeBase | None,
    shown: Collection[RecordedQuantity],
    *,
    plot_width_px: float,
) -> ChartFrame:
    """Read every run once and settle everything the frame draws.

    Four steps, in an order that makes two runs one picture rather than
    two: the shared ruler is set from the reference run, the window is
    chosen so that it contains every run, the references are placed across
    that window, and only then does each run evaluate its own states into
    it.

    Args:
        runs: Every run on the chart, in drawing order, with the snapshot
            each is drawn from.
        time_base: The width the reader chose, or `None` for "Fit run".
        shown: The compartments the reader has left drawn.
        plot_width_px: The width of the plot the frame will be drawn on, in
            logical pixels - the wider of the two where both plots draw it,
            since the wash-in stretches are formed from the same columns.
            `ConcentrationChart.plot_width_px` and `WashInChart.plot_width_px`
            report it. Required rather than defaulted: a frame drawn for a
            width nobody stated would be drawn at the floor, silently.

    Returns:
        The frame.

    Raises:
        ValueError: If the width is negative or not finite (see
            `chart_columns`); if no run is given; or if the runs are not all
            on one agent. One ×MAC ruler, one MAC-awake band and one 1 MAC line are
            drawn across a chart every run shares, and all three are the
            agent's own published values; two agents on one axis would have
            one run's traces read against the other's divisor - a correct
            number under the wrong label, which `CLAUDE.md`'s
            safety-critical standard treats as a failure of the value.
    """

    if not runs:
        raise ValueError("a chart draws at least one run; none was given")

    agent_ids = {run.snapshot.agent_id for run in runs}

    if len(agent_ids) > 1:
        raise ValueError(
            "every run on the chart must be on the same agent, because they share one MAC "
            f"axis and one set of clinical references; given {', '.join(sorted(agent_ids))}"
        )

    reference = runs[0].snapshot
    elapsed_s = max(run.snapshot.elapsed_s for run in runs)

    # The visible window, and the two modes it can be in. "Fit run" derives
    # the width from the run so the whole of it is drawn, pinned at zero; a
    # chosen width is held exactly and follows the newest instant, so a
    # trace's slope on the plot means the same thing at every moment.
    if time_base is None:
        base = fit_to_run(elapsed_s)
        start_s, stop_s = fitted_window(base)
    else:
        base = time_base
        start_s, stop_s = following_window(base, elapsed_s)

    columns = chart_columns(plot_width_px)
    mac_percent = reference.agent_mac_percent
    top_percent = chart_axis_top_percent(mac_percent)
    grid_percent = chart_grid_interval_percent(mac_percent)
    mac_awake = reference.agent_mac_awake

    return ChartFrame(
        time_base=base,
        fitted=time_base is None,
        start_s=start_s,
        stop_s=stop_s,
        tick_times_s=tick_times(start_s, stop_s, base.tick_interval_s),
        columns=columns,
        plot_width_px=plot_width_px,
        mac_percent=mac_percent,
        axis_top_percent=top_percent,
        grid_interval_percent=grid_percent,
        percent_ticks=percent_axis_ticks(top_percent, grid_percent),
        mac_ticks=mac_axis_ticks(top_percent, mac_percent),
        one_mac_percent=mac_percent,
        mac_awake_band_percent=mac_awake_band_percent(
            fraction_of_mac=mac_awake.fraction_of_mac,
            standard_deviation_fraction_of_mac=mac_awake.standard_deviation_fraction_of_mac,
            mac_percent=mac_percent,
        ),
        visible=tuple(style.quantity for style in COMPARTMENT_TRACES if style.quantity in shown),
        runs=tuple(_run_frame(run, start_s, stop_s, columns) for run in runs),
    )


def _run_frame(run: RunInput, start_s: float, stop_s: float, columns: int) -> RunFrame:
    """Evaluate one run into the window every run shares."""

    snapshot = run.snapshot
    # Drawn under the agent this frame's readouts were formatted from, so a
    # run and the traces of it cannot come from different agents: a snapshot
    # naming an agent the window does not describe raises in
    # `DrawnWindow.compartment_fractions` rather than drawing whatever the
    # run does hold.
    window = run.controller.drawn_window(start_s, stop_s, columns)
    fractions = {
        quantity: tuple(window.compartment_fractions(RecordedSeries(snapshot.agent_id, quantity)))
        for quantity in COMPARTMENT_QUANTITIES
    }
    stretches = _drawn_wash_in(window, snapshot.agent_id)
    inside = tuple(
        adjustment.started_at_s
        for adjustment in run.adjustments
        if start_s <= adjustment.started_at_s <= stop_s
    )
    marks = inside[-MAX_CHART_CONTROL_MARKS:]

    return RunFrame(
        agent_id=snapshot.agent_id,
        agent_display_name=snapshot.agent_display_name,
        mac_percent=snapshot.agent_mac_percent,
        elapsed_s=snapshot.elapsed_s,
        times_s=window.times_s,
        fractions=MappingProxyType(fractions),
        wash_in=stretches[-MAX_CHART_WASH_IN_SEGMENTS:],
        undrawn_wash_in_stretches=max(0, len(stretches) - MAX_CHART_WASH_IN_SEGMENTS),
        control_marks_s=marks,
        undrawn_control_marks=len(inside) - len(marks),
    )


def _drawn_wash_in(window: DrawnWindow, substance_id: str) -> tuple[WashInStretch, ...]:
    """Every wash-in stretch inside the window, oldest first.

    Formed from the very columns the compartment chart draws, so the two
    plots cannot differ by a step the run took in between, and a stretch
    boundary can fall only on an instant the chart actually plots.
    """

    quotients = window.wash_in_quotients(substance_id)
    stretches = []

    for start, stop in wash_in_stretches(quotients, WASH_IN_TERMINUS_CEILING):
        # Every column of a stretch has a quotient: the anchors are inside the
        # domain, and the one extending column at each end was chosen for
        # having one. `wash_in_stretches` is where that holds.
        columns = [
            (window.times_s[column], quotient)
            for column in range(start, stop)
            if (quotient := quotients[column]) is not None
        ]
        last = quotients[stop - 1]
        stretches.append(
            WashInStretch(
                times_s=tuple(time_s for time_s, _ in columns),
                ratios=tuple(ratio for _, ratio in columns),
                ends_above_equilibrium=last is not None and not is_wash_in(last),
            )
        )

    return tuple(stretches)


def wash_in_stretches(
    quotients: Sequence[float | None], extension_ceiling: float
) -> list[tuple[int, int]]:
    """The stretches the wash-in plot draws, as ranges over the drawn columns.

    A column *anchors* a stretch when its quotient is inside the wash-in
    domain `app/wash_in.py` states. A column *extends* one when it has a
    quotient at all - its denominator was above the display floor - that
    quotient is no higher than `extension_ceiling`, and it neighbours an
    anchor. So a stretch is a run of in-domain columns plus, at each end,
    the one crossing column that shows where the curve left the domain and
    that the plot can still show.

    **Why a stretch is extended at all.** Without the crossing column the
    curve stops at the last column at or below equilibrium, short of the
    boundary it stopped at, and a trace halting in clear space short of a
    line reads as clipped rather than finished. With it the curve meets the
    equilibrium reference and ends on it.

    **Why the extension has a ceiling.** A run stepped at 0.1 s crosses
    equilibrium by a hair - measured across every agent and every supported
    alveolar ventilation and cardiac output at the maximum fresh gas flow,
    the first sample above it reaches 1.00235 - but the ratio is not
    continuous in general: `BreathingCircuit.set_circuit_volume` conserves
    the agent in the circuit while changing the volume it is divided by, so
    a circuit volume doubled between two steps halves F_I and doubles the
    ratio. No interface control does that today, and a rule that holds only
    because a slider is missing is not one to rely on. A crossing column
    above the ceiling is therefore not drawn, and the stretch ends where it
    did before: not clamped to the ceiling, not interpolated onto it -
    simply a point outside what this plot can show.

    **A single polyline through every in-domain sample would draw a straight
    line across the stretch it skipped** - a segment joining two real points
    through values the run never produced, which is the synthesized trace
    this module never creates. A broken line asserts nothing about the gap.

    Computed over the drawn columns rather than maintained as the run
    records samples (`PL-2FM6`): there are only the columns being drawn, so
    classifying all of them is proportional to the frame rather than to the
    run, and a boundary can fall only on an instant the chart actually
    plots. Two anchor runs separated by a single extendable column both
    reach it, and it is drawn once as each stretch's endpoint - the honest
    rendering of a run that left the domain and returned within one column,
    and the only case where one column appears twice.

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


def percent_axis_ticks(
    top_percent: float, interval_percent: float
) -> tuple[tuple[float, str], ...]:
    """Label the compartment chart's percent axis at exactly its gridlines.

    The ruling and the labelling describe one scale, by construction: both
    are multiples of `interval_percent`, so a reader taking a value off the
    nearest rule takes it off a labelled one. The Flet chart left the axis
    to label itself, at a different interval from the rules it drew
    (`PL-Q4VH`); this is the fix that port carries.

    Args:
        top_percent: Top of the axis.
        interval_percent: Spacing of its horizontal rules.

    Returns:
        Ticks from zero upward, each as (percent position, label). The label
        is the position at the shortest exact decimal form, so an agent
        whose half-MAC is 0.575% is labelled `0.575` rather than rounded off
        the gridline it stands on.

    Raises:
        ValueError: If either argument is not strictly positive; an axis of
            no height or a rule spacing of zero would place every label
            somewhere meaningless rather than failing.
    """

    if not top_percent > 0.0:
        raise ValueError(f"top_percent must be strictly positive, got {top_percent!r}")

    if not interval_percent > 0.0:
        raise ValueError(f"interval_percent must be strictly positive, got {interval_percent!r}")

    # `floor` with a hair of tolerance, so a top that is an exact multiple of
    # the interval keeps its last tick through floating-point rounding.
    count = floor(top_percent / interval_percent + 1e-9)

    return tuple(
        (index * interval_percent, f"{index * interval_percent:g}") for index in range(count + 1)
    )


def wash_in_axis_ticks() -> tuple[tuple[float, str], ...]:
    """Label the wash-in axis at its own gridlines, in its own resolution.

    Nothing about this axis depends on the agent or on the run - it is a
    dimensionless 0 to 1 under every setting, which is the property that
    makes the plot comparable across agents in the first place. The labels
    go through `format_wash_in_ratio`, so the axis a value is read against
    and the reading printed beside the plot cannot be at two different
    resolutions. The ruling and the labels stop at equilibrium, which is
    where the readable scale ends; the axis itself stands higher for the
    reason `WASH_IN_AXIS_MAXIMUM` gives.

    Returns:
        One tick per gridline, from 0 to equilibrium.
    """

    count = round(WASH_IN_EQUILIBRIUM_RATIO / WASH_IN_GRID_INTERVAL)

    return tuple(
        (index * WASH_IN_GRID_INTERVAL, format_wash_in_ratio(index * WASH_IN_GRID_INTERVAL))
        for index in range(count + 1)
    )


def format_trace_hover(run: RunFrame, quantity: RecordedQuantity, index: int) -> str:
    """The three lines a hover over one drawn point of a compartment trace says.

    `docs/MODEL.md` § "The chart's hover readout: what the tooltip may show"
    is the specification: run context, then what the value is, then the
    value in both units the chart carries - and every number through
    `app/formatting.py`, never the chart library's own formatter, at the
    resolution the readouts derive and with the below-resolution forms
    intact. The order carries the safety argument: the qualifiers precede
    the number, so a reader reaches it through "modelled" and through the
    compartment it belongs to rather than meeting them afterwards.

    Args:
        run: The run the point belongs to.
        quantity: The compartment the trace draws.
        index: Which drawn point, as a position in `run.times_s`.

    Returns:
        The readout, three lines joined by newlines.

    Raises:
        KeyError: If `quantity` is not a compartment on this chart.
        IndexError: If `index` is outside the drawn points.
    """

    style = trace_style(quantity)
    fraction = Fraction(run.fractions[quantity][index])
    what = style.label if style.gloss is None else f"{style.label} ({style.gloss})"
    value = (
        f"{format_percent(fraction)}   {format_mac_multiple(fraction, Percent(run.mac_percent))}"
    )

    return "\n".join((_hover_context(run, run.times_s[index]), what, value))


def format_wash_in_hover(run: RunFrame, stretch: WashInStretch, index: int) -> str:
    """The three lines a hover over one drawn point of the wash-in trace says.

    The same form as `format_trace_hover`, in the ratio's own units: F_A/F_I
    is dimensionless and has neither a percent nor a MAC reading, so the
    third line is `format_wash_in_ratio`'s number alone.

    Args:
        run: The run the stretch belongs to.
        stretch: The stretch the point is on.
        index: Which drawn point, as a position in `stretch.times_s`.

    Returns:
        The readout, three lines joined by newlines.

    Raises:
        IndexError: If `index` is outside the stretch's points.
    """

    return "\n".join(
        (
            _hover_context(run, stretch.times_s[index]),
            WASH_IN_HOVER_LABEL,
            format_wash_in_ratio(stretch.ratios[index]),
        )
    )


def _hover_context(run: RunFrame, time_s: float) -> str:
    """The first line of every hover: the modelled marker, the agent, the instant."""

    instant_s = round(time_s / HOVER_INSTANT_RESOLUTION_S) * HOVER_INSTANT_RESOLUTION_S

    return (
        f"{_HOVER_MODELLED_MARKER} {run.agent_display_name.lower()} · {format_elapsed(instant_s)}"
    )


@dataclass(frozen=True, slots=True)
class HoverTarget:
    """The drawn point a pointer is nearest to, and what the hover says of it.

    Attributes:
        run: Which run, as a position in `ChartFrame.runs`.
        quantity: Which trace - a compartment, or
            `RecordedQuantity.WASH_IN_RATIO` on the wash-in plot.
        time_s: The point's simulated time.
        value: The point's height in the plot's own unit: percent on the
            compartment chart, the dimensionless ratio on the wash-in plot.
        readout: The three-line text to show.
    """

    run: int
    quantity: RecordedQuantity
    time_s: float
    value: float
    readout: str


def nearest_trace_point(
    frame: ChartFrame,
    time_s: float,
    percent: float,
    seconds_per_pixel: float,
    percent_per_pixel: float,
    radius_pixels: float,
) -> HoverTarget | None:
    """Which drawn compartment point, if any, a pointer is within reach of.

    Distance is measured in pixels rather than in axis units, because the
    two axes are in different units and a reader's hand is in neither: a
    tolerance stated in seconds would be a hair at the 12-hour base and a
    whole window at the one-minute one. The caller supplies the scale of
    the view it is drawing.

    Only the compartments the frame draws are candidates, so a hidden trace
    answers nothing, and only the six compartments are - the clinical
    references and the control marks are not drawn points and never answer,
    for the interaction reason `docs/MODEL.md` § "The chart's hover readout"
    gives. Every candidate is a point the plot actually draws: the readout
    reports a state of the run, never a position between two of them.

    Args:
        frame: The frame on the plot.
        time_s: The pointer's position along the time axis.
        percent: The pointer's position on the percent axis.
        seconds_per_pixel: The time axis's scale.
        percent_per_pixel: The percent axis's scale.
        radius_pixels: How far, in pixels, a point may be from the pointer
            and still answer.

    Returns:
        The nearest point within the radius, or `None` when no drawn point
        is that close.
    """

    best: tuple[float, HoverTarget] | None = None

    for run_index, run in enumerate(frame.runs):
        for column in _columns_within(run.times_s, time_s, radius_pixels * seconds_per_pixel):
            for quantity in frame.visible:
                drawn_percent = percent_from_fraction(Fraction(run.fractions[quantity][column]))
                distance = _pixel_distance(
                    time_s,
                    percent,
                    run.times_s[column],
                    drawn_percent,
                    seconds_per_pixel,
                    percent_per_pixel,
                )

                if distance <= radius_pixels and (best is None or distance < best[0]):
                    best = (
                        distance,
                        HoverTarget(
                            run=run_index,
                            quantity=quantity,
                            time_s=run.times_s[column],
                            value=drawn_percent,
                            readout=format_trace_hover(run, quantity, column),
                        ),
                    )

    return None if best is None else best[1]


def nearest_wash_in_point(
    frame: ChartFrame,
    time_s: float,
    ratio: float,
    seconds_per_pixel: float,
    ratio_per_pixel: float,
    radius_pixels: float,
) -> HoverTarget | None:
    """Which drawn wash-in point, if any, a pointer is within reach of.

    `nearest_trace_point` for the wash-in plot: the same pixel-space rule,
    over every drawn stretch of every run. The equilibrium line and the
    control marks are not candidates.

    Args:
        frame: The frame on the plot.
        time_s: The pointer's position along the time axis.
        ratio: The pointer's position on the ratio axis.
        seconds_per_pixel: The time axis's scale.
        ratio_per_pixel: The ratio axis's scale.
        radius_pixels: How far, in pixels, a point may be from the pointer
            and still answer.

    Returns:
        The nearest point within the radius, or `None`.
    """

    best: tuple[float, HoverTarget] | None = None

    for run_index, run in enumerate(frame.runs):
        for stretch in run.wash_in:
            for column in _columns_within(
                stretch.times_s, time_s, radius_pixels * seconds_per_pixel
            ):
                distance = _pixel_distance(
                    time_s,
                    ratio,
                    stretch.times_s[column],
                    stretch.ratios[column],
                    seconds_per_pixel,
                    ratio_per_pixel,
                )

                if distance <= radius_pixels and (best is None or distance < best[0]):
                    best = (
                        distance,
                        HoverTarget(
                            run=run_index,
                            quantity=RecordedQuantity.WASH_IN_RATIO,
                            time_s=stretch.times_s[column],
                            value=stretch.ratios[column],
                            readout=format_wash_in_hover(run, stretch, column),
                        ),
                    )

    return None if best is None else best[1]


def _columns_within(times_s: Sequence[float], time_s: float, reach_s: float) -> range:
    """The drawn columns whose instant is within `reach_s` of `time_s`.

    The instants are ascending, so this is two bisections rather than a
    scan of the run: a pointer moving at sixty events a second over two
    runs of six traces is otherwise a distance computation per drawn point
    per event.
    """

    return range(bisect_left(times_s, time_s - reach_s), bisect_right(times_s, time_s + reach_s))


def _pixel_distance(
    x: float, y: float, drawn_x: float, drawn_y: float, x_per_pixel: float, y_per_pixel: float
) -> float:
    """How far apart two plot positions are on screen, in pixels."""

    return sqrt(((x - drawn_x) / x_per_pixel) ** 2 + ((y - drawn_y) / y_per_pixel) ** 2)
