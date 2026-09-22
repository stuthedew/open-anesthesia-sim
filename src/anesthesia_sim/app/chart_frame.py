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

from bisect import bisect_left
from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass, replace
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
from anesthesia_sim.app.controller import SimulationController, SimulationSnapshot
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
from anesthesia_sim.app.run_series import (
    COMPARTMENT_QUANTITIES,
    DrawnWindow,
    RecordedQuantity,
    RecordedSeries,
)
from anesthesia_sim.app.theme import (
    ALVEOLAR_COLOR,
    CIRCUIT_COLOR,
    COMPARED_RUN_WIDTH_STEP,
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
    "COMPARED_COMPARTMENT_CAP",
    "COMPARTMENT_TRACES",
    "HOVER_INSTANT_RESOLUTION_S",
    "MAX_CHART_CONTROL_MARKS",
    "MAX_CHART_WASH_IN_SEGMENTS",
    "WASH_IN_AXIS_MAXIMUM",
    "WASH_IN_GRID_INTERVAL",
    "WASH_IN_HOVER_LABEL",
    "WASH_IN_TERMINUS_CEILING",
    "ChartFrame",
    "HoverReading",
    "HoverTarget",
    "RunFrame",
    "RunInput",
    "TraceStyle",
    "WashInStretch",
    "assemble_chart_frame",
    "chart_columns",
    "compared_compartments",
    "format_compared_trace_hover",
    "format_compared_wash_in_hover",
    "format_trace_hover",
    "format_wash_in_hover",
    "nearest_trace_point",
    "nearest_wash_in_point",
    "percent_axis_ticks",
    "run_trace_style",
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

# How many compartments may be drawn while more than one run is on the chart.
#
# **The load-bearing half of `PL-HLD5`'s encoding rather than a nicety.** At six
# compartments every line-level channel is already spent - line style carries
# the compartment across six patterns, colour is its second cue, and width
# varies 2 px to 3 px across the six - so nothing is free for the run until the
# cap frees it. Two compartments times two runs is four curves, which is what
# the run's two width levels have to separate.
#
# It is a colour-capacity limit on the *chart* and never a reduction of what the
# display owes: `docs/MODEL.md` § "Minimum displayed outputs" requires all six
# compartment readouts to stay on screen for both runs while comparing, and says
# so naming this cap. What the cap removes is four curves; the readouts are what
# keep those four values displayed.
COMPARED_COMPARTMENT_CAP: Final = 2

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

# What separates the tokens of the hover's run-context line. One constant
# rather than a literal per join, so a line assembled from three tokens or
# from four is punctuated identically.
_HOVER_CONTEXT_SEPARATOR: Final = " · "


@dataclass(frozen=True, slots=True)
class TraceStyle:
    """One compartment trace: what it draws, how it is drawn, what it is called.

    Everything that has to agree about a single compartment, held in one
    record. Before `PL-G59B` the same trace was described in three places -
    the colour and dash pattern where the series was built, the compartment
    it draws in the Flet chart's series table (deleted with that chart in
    `PL-25KS`), and the name and line-style words in a legend row six hundred
    lines away - and keeping them in agreement was left to whoever
    remembered. A legend that names a line the chart is not drawing misstates
    the run as surely as a wrong number does.

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


def run_trace_style(quantity: RecordedQuantity, run_index: int, run_count: int) -> TraceStyle:
    """The trace one run draws a compartment with: its own style, at its run's width.

    The whole of the run's visual channel, in one place, so that the chart,
    the legend swatch and any later view read one answer rather than three.
    Everything about the compartment - colour, dash pattern, the words for
    both - is `trace_style`'s and is returned unchanged, because nothing
    about a compartment's appearance may change on entering compare mode
    (`PL-HLD5`): colour means "compartment" on the single-run chart, and a
    channel that meant something else either side of a mode change is a
    misread of a clinical value waiting to happen.

    **The run is on line width, at two levels, read locally.** The
    distinction only has to be made between two curves of the *same*
    compartment, which are adjacent by construction, rather than decoded
    across the plot; `app/theme.py`'s `COMPARED_RUN_WIDTH_STEP` carries why
    the first run is the wider of the two and why widening beats narrowing.
    A single run is drawn exactly as it always was, so the width channel
    does not exist until there is a second run to tell apart.

    Args:
        quantity: Which compartment.
        run_index: Which run, as a position in the frame's runs.
        run_count: How many runs are on the chart.

    Returns:
        The compartment's style, with `stroke_width` set for this run.

    Raises:
        KeyError: If no trace draws `quantity` (see `trace_style`).
        ValueError: If `run_index` does not address one of `run_count` runs.
            A style asked for a run the chart is not drawing would answer
            with a width nothing on screen carries.
    """

    if run_count < 1 or not 0 <= run_index < run_count:
        raise ValueError(
            f"run {run_index} is not one of the {run_count} runs on the chart; a trace "
            "is drawn at the width of a run that is being drawn"
        )

    style = trace_style(quantity)
    widened = run_count > 1 and run_index == 0

    if not widened:
        return style

    return replace(style, stroke_width=style.stroke_width + COMPARED_RUN_WIDTH_STEP)


def compared_compartments(
    shown: Collection[RecordedQuantity], run_count: int
) -> tuple[tuple[RecordedQuantity, ...], int]:
    """The compartments a frame draws for this many runs, and how many it could not.

    The cap applied, in the one place that decides what the chart draws, so
    that no view can hold a selection the plot is not honouring.
    `COMPARED_COMPARTMENT_CAP` carries why capping is what frees the width
    channel for the run.

    Kept in table order and taken from the top of it rather than in the
    order a reader clicked, so the drawn pair is the same pair whichever
    route reached the selection - and so the circuit and alveolar traces,
    which lead that table, are what a reader who has chosen nothing sees.

    Args:
        shown: The compartments the reader has left drawn.
        run_count: How many runs are on the chart. One run is uncapped: the
            six-trace encoding works as it always has, and it is a second
            run that spends the channel the cap frees.

    Returns:
        The compartments drawn, in table order, and the count of selected
        compartments the cap left undrawn. The second is displayed rather
        than dropped in silence, per `docs/MODEL.md` § "The control-input
        timeline", "Bounds are displayed, not silent".
    """

    selected = tuple(style.quantity for style in COMPARTMENT_TRACES if style.quantity in shown)

    if run_count <= 1:
        return selected, 0

    return selected[:COMPARED_COMPARTMENT_CAP], max(0, len(selected) - COMPARED_COMPARTMENT_CAP)


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
        label: What this run is called in text, as the legend and every
            readout that names a run say it. Handed in rather than derived
            from a position here, so one run is called the same thing on
            the chart, in the legend and on its own panel, and so a view
            that drew a different subset could not rename it
            (`.claude/rules/ui-areas.md`). `docs/MODEL.md` § "Minimum
            displayed outputs" requires the run to be named in text: colour
            is spent on the compartment, and position alone fails the
            reader who has looked away and back.
        branch_point_s: The instant this run forked from the run it opened
            out of, in simulated seconds, or `None` for a run that is not a
            branch or whose fork lies outside the drawn window. The one
            instant at which two compared runs stop being the same run, so
            it is marked rather than left for the reader to find by
            following two coincident curves until they part.
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

    label: str
    branch_point_s: float | None
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
            state only: it is never read by the simulation. With more than
            one run this is the reader's selection under
            `COMPARED_COMPARTMENT_CAP`, which `compared_compartments`
            applies.
        undrawn_compartments: How many selected compartments the cap left
            undrawn. Zero on a single run, which is uncapped. Displayed
            rather than hidden: a selection the chart is not honouring, said
            nowhere, is a legend naming a line that is not there.
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
    undrawn_compartments: int
    runs: tuple[RunFrame, ...]


@dataclass(frozen=True, slots=True)
class RunInput:
    """One run to draw, with the snapshot the same frame formats it from.

    Attributes:
        label: What this run is called in text. The caller's, because the
            same word has to appear on the run's own panel beside the
            settings that produced it, and a name the chart invented would
            be the chart's alone.
        controller: The run.
        snapshot: Its state, read once by the caller for this frame and
            handed down here, so a run's readouts and the traces beside them
            are one instant of one run rather than two reads that happened
            to agree.
        adjustments: The run's control timeline, grouped into the acts a
            reader sees. The caller's `control_timeline.AdjustmentGrouping`
            supplies it, so a frame that recorded nothing regroups nothing.
    """

    label: str
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
    # The cap is applied here rather than where a reader clicks, so that what
    # the chart draws is capped however the selection was reached - by a
    # legend, by a restored layout, or by a second view that has no legend of
    # its own (`.claude/rules/ui-areas.md`).
    drawn, capped = compared_compartments(shown, len(runs))
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
        visible=drawn,
        undrawn_compartments=capped,
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
    # Marked only where it can be seen. A fork the window has scrolled past
    # is not drawn at the edge, which would put the one instant two runs stop
    # agreeing at a time it did not happen.
    opened_from = run.controller.opened_from
    branch_point_s = (
        opened_from.elapsed_s
        if opened_from is not None and start_s <= opened_from.elapsed_s <= stop_s
        else None
    )

    return RunFrame(
        label=run.label,
        branch_point_s=branch_point_s,
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


def format_trace_hover(
    run: RunFrame, quantity: RecordedQuantity, index: int, run_count: int
) -> str:
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
        run_count: How many runs are on the chart. The first line names the
            run while more than one is drawn; `_hover_context` carries why.

    Returns:
        The readout, three lines joined by newlines.

    Raises:
        KeyError: If `quantity` is not a compartment on this chart.
        IndexError: If `index` is outside the drawn points.
        ValueError: If `run_count` is less than one.
    """

    return "\n".join(
        (
            _hover_context(run, run.times_s[index], run_count),
            _hover_subject(quantity),
            _hover_value(run, quantity, index),
        )
    )


def format_wash_in_hover(run: RunFrame, stretch: WashInStretch, index: int, run_count: int) -> str:
    """The three lines a hover over one drawn point of the wash-in trace says.

    The same form as `format_trace_hover`, in the ratio's own units: F_A/F_I
    is dimensionless and has neither a percent nor a MAC reading, so the
    third line is `format_wash_in_ratio`'s number alone.

    Args:
        run: The run the stretch belongs to.
        stretch: The stretch the point is on.
        index: Which drawn point, as a position in `stretch.times_s`.
        run_count: How many runs are on the chart, as `format_trace_hover`
            takes it and for the same reason.

    Returns:
        The readout, three lines joined by newlines.

    Raises:
        IndexError: If `index` is outside the stretch's points.
        ValueError: If `run_count` is less than one.
    """

    return "\n".join(
        (
            _hover_context(run, stretch.times_s[index], run_count),
            WASH_IN_HOVER_LABEL,
            format_wash_in_ratio(stretch.ratios[index]),
        )
    )


def _hover_context(run: RunFrame, time_s: float, run_count: int) -> str:
    """The first line of every hover: the modelled marker, the agent, the run, the instant.

    The run is named while more than one is drawn and omitted while one is
    (project owner, 2026-09-17, ratified, over a fourth line of its own and
    over leaving the curve's line width to carry it). `docs/MODEL.md` § "The
    chart's hover readout" -> "The hover and the run it belongs to" is the
    derivation; in short, this is the line that specification already calls
    *run context*, and while two runs are compared the run is the only token
    on it that tells them apart - `assemble_chart_frame` refuses a frame whose
    runs differ on agent, so the agent is a constant across the runs here.

    It is conditional for the reason the width channel is
    (`run_trace_style`): a single run has nothing to be told apart from, and
    a name on the only run drawn implies a comparison that is not on screen.
    The condition is not a hidden mode - a second run brings a second legend
    entry and a second readout panel with it.

    Args:
        run: The run the point belongs to.
        time_s: The point's simulated time.
        run_count: How many runs are on the chart.

    Returns:
        The run-context line: three tokens while one run is drawn, four while
        more than one is.

    Raises:
        ValueError: If `run_count` is less than one. A hover is answered from
            a chart that is drawing something, and a readout that named no
            run while claiming to compare would be the failure this names the
            run to prevent.
    """

    if run_count < 1:
        raise ValueError(
            f"a chart draws at least one run; a hover cannot be answered for {run_count}"
        )

    tokens = [_hover_agent(run)]

    if run_count > 1:
        tokens.append(run.label)

    tokens.append(_hover_instant(time_s))

    return _HOVER_CONTEXT_SEPARATOR.join(tokens)


def format_compared_trace_hover(
    answering: Sequence[tuple[RunFrame, RecordedQuantity, int]], run_count: int
) -> str:
    """What a hover says where more than one drawn point is within reach of the pointer.

    `docs/MODEL.md` § "The chart's hover readout" -> "Where more than one
    trace answers" is the specification, and `PL-JVHL` is why there is one: the
    three-line form settled which run a reader was shown by which drawn point
    was marginally nearer, so a 2 px hand movement swapped it silently. Every
    run inside the radius answers instead, and the box carries a value line
    per run. `PL-0RZ0` extended that to the compartment, which the same axis
    compression leaves contending just as often.

    **Two forms, and the first is exactly what it always was.** Where every
    reading is of one compartment - which `PL-0RZ0` measured at 54.3-99.5% of
    hovers - the form is the three-line one with its third line repeated: the
    modelled marker and the agent, then the compartment, then one line per
    run. Where the readings span compartments the heading cannot stand for
    them all, so it goes and each value line opens with its own compartment,
    then its run while more than one is drawn. The qualifiers still precede
    the numbers in both, which is the safety argument the order carries.

    **The instant is stated per line rather than once for the box.** Every
    compartment of one run answers at one instant (`nearest_trace_point`,
    `PL-1K9G`), but two runs need not: each draws the columns its own control
    events fall on (`SimulationController.drawn_window`) and a branch draws
    none before its fork, so the instants nearest one pointer can differ
    between runs - by up to a grid column where both are drawn, 4 s on the
    60-minute axis and 48 s on the 12-hour one, both of which `format_elapsed`
    shows. A single instant above a column of values would assert a
    simultaneity the readings do not have, which `CLAUDE.md`'s safety-critical
    standard counts as a failure of the value rather than of its presentation.

    Args:
        answering: Every drawn point within reach, in the frame's own drawing
            order - compartment by `ChartFrame.visible`, run by
            `ChartFrame.runs` - each with the compartment its trace draws and
            which of the run's drawn points answers, as a position in the
            run's `times_s`. Ordered by the frame rather than by distance, so
            that nothing about the box moves with a hand movement too small to
            aim with - which is the whole of `PL-JVHL` and `PL-0RZ0`.
        run_count: How many runs the chart draws. The value lines name the
            run while more than one is, on `_hover_context`'s rule and for its
            reason; it is the chart's count rather than the answering one,
            because a run that is drawn but out of reach is still a run the
            reader can see.

    Returns:
        The readout: the agent, then the compartment where one is shared, then
        one line per reading, joined by newlines.

    Raises:
        KeyError: If a quantity is not a compartment on this chart.
        IndexError: If an index is outside its run's drawn points.
        ValueError: If no reading is given, if `run_count` is less than the
            readings' own runs need, or if the runs are not all on one agent.
            The agent is named once, above the values, because
            `assemble_chart_frame` refuses a frame whose runs differ on it;
            naming one run's agent over another run's concentration would be
            the correct number under the wrong label.
    """

    if not answering:
        raise ValueError("a hover is answered for at least one drawn point; none was given")

    if run_count < 1:
        raise ValueError(
            f"a chart draws at least one run; a hover cannot be answered for {run_count}"
        )

    agents = {run.agent_display_name for run, _, _ in answering}

    if len(agents) > 1:
        raise ValueError(
            "every run a hover answers for must be on the same agent, because the readout "
            f"names it once above their values; given {', '.join(sorted(agents))}"
        )

    quantities = tuple(dict.fromkeys(quantity for _, quantity, _ in answering))

    if len(quantities) == 1:
        return "\n".join(
            (
                _hover_agent(answering[0][0]),
                _hover_subject(quantities[0]),
                *(
                    _hover_compared_value(
                        run, run.times_s[index], _hover_value(run, quantity, index)
                    )
                    for run, quantity, index in answering
                ),
            )
        )

    return "\n".join(
        (
            _hover_agent(answering[0][0]),
            *(
                _hover_contended_value(run, quantity, index, run_count)
                for run, quantity, index in answering
            ),
        )
    )


def format_compared_wash_in_hover(answering: Sequence[tuple[RunFrame, WashInStretch, int]]) -> str:
    """`format_compared_trace_hover` for the wash-in plot, in the ratio's own units.

    The same form and the same reasons, with `format_wash_in_hover`'s third
    line in place of the compartment's: F_A/F_I is dimensionless and has
    neither a percent nor a MAC reading.

    Args:
        answering: Every run within reach, in `ChartFrame.runs` order, each
            with the stretch its answering point is on and which point that
            is as a position in the stretch's `times_s`.

    Returns:
        The readout, two lines plus one per run, joined by newlines.

    Raises:
        IndexError: If an index is outside its stretch's points.
        ValueError: If no run is given, or if the runs are not all on one
            agent - as `format_compared_trace_hover` raises, and for the
            same reason.
    """

    if not answering:
        raise ValueError("a hover is answered for at least one run; none was given")

    agents = {run.agent_display_name for run, _, _ in answering}

    if len(agents) > 1:
        raise ValueError(
            "every run a hover answers for must be on the same agent, because the readout "
            f"names it once above their values; given {', '.join(sorted(agents))}"
        )

    return "\n".join(
        (
            _hover_agent(answering[0][0]),
            WASH_IN_HOVER_LABEL,
            *(
                _hover_compared_value(
                    run, stretch.times_s[index], format_wash_in_ratio(stretch.ratios[index])
                )
                for run, stretch, index in answering
            ),
        )
    )


def _hover_agent(run: RunFrame) -> str:
    """The modelled marker and the agent - the part of the context every form opens with."""

    return f"{_HOVER_MODELLED_MARKER} {run.agent_display_name.lower()}"


def _hover_instant(time_s: float) -> str:
    """A drawn point's instant, at the step the run advances by.

    A drawn column sits wherever the anchored grid puts it, and the state
    reported is the state at exactly that instant, but printing it to four
    decimals would claim a resolution no other display on the screen has.
    """

    return format_elapsed(round(time_s / HOVER_INSTANT_RESOLUTION_S) * HOVER_INSTANT_RESOLUTION_S)


def _hover_subject(quantity: RecordedQuantity) -> str:
    """What the value is: the compartment, with its gloss where the readout row has one."""

    style = trace_style(quantity)

    return style.label if style.gloss is None else f"{style.label} ({style.gloss})"


def _hover_value(run: RunFrame, quantity: RecordedQuantity, index: int) -> str:
    """One drawn point in both units the chart carries.

    The one place either form produces a compartment number, so a hover
    answering for one run and a hover answering for three cannot format the
    same state differently. The MAC multiple resolves against this run's own
    `mac_percent`, exactly as the MAC axis and the readout row do.
    """

    fraction = Fraction(run.fractions[quantity][index])

    return f"{format_percent(fraction)}   {format_mac_multiple(fraction, Percent(run.mac_percent))}"


def _hover_compared_value(run: RunFrame, time_s: float, value: str) -> str:
    """One run's line of a compared readout: whose value it is, when, and what it is."""

    context = _HOVER_CONTEXT_SEPARATOR.join((run.label, _hover_instant(time_s)))

    return f"{context}   {value}"


def _hover_contended_value(
    run: RunFrame, quantity: RecordedQuantity, index: int, run_count: int
) -> str:
    """One line of a readout whose pointer is in reach of more than one compartment.

    The compartment leads, because it is what the heading carried while the
    readings shared one and a value line that did not name it would leave the
    reader to infer which trace it came from - which is exactly the inference
    `PL-0RZ0` found a 2 px hand movement falsifying. It keeps the gloss
    `_hover_subject` gives it: `docs/MODEL.md` requires that hedge wherever
    the compartment is named, and a form that dropped it to stay narrow would
    be trading a required qualifier for a column of whitespace.

    The run follows while more than one is drawn and is omitted while one is,
    which is `_hover_context`'s rule rather than a second one - a name on the
    only run drawn implies a comparison that is not on screen.
    """

    tokens = [_hover_subject(quantity)]

    if run_count > 1:
        tokens.append(run.label)

    tokens.append(_hover_instant(run.times_s[index]))

    return f"{_HOVER_CONTEXT_SEPARATOR.join(tokens)}   {_hover_value(run, quantity, index)}"


@dataclass(frozen=True, slots=True)
class HoverReading:
    """One drawn point a hover answers for: whose it is, what it is, and where.

    Attributes:
        run: Which run, as a position in `ChartFrame.runs`.
        quantity: Which trace the point is on - a compartment, or
            `RecordedQuantity.WASH_IN_RATIO` on the wash-in plot. Carried per
            reading rather than once for the box because more than one
            compartment answers where two compressed traces are inside one
            radius of each other, and a value whose trace the reader has to
            infer is the failure `PL-0RZ0` closes.
        time_s: The point's simulated time: its run's drawn instant nearest
            the pointer in time, which every reading of one run shares
            (`PL-1K9G`). Two runs can still differ here - each also draws the
            columns its own control events fall on, and a branch draws none
            before its fork - which is why the readout states the instant per
            reading rather than once for the box.
        value: The point's height in the plot's own unit: percent on the
            compartment chart, the dimensionless ratio on the wash-in plot.
    """

    run: int
    quantity: RecordedQuantity
    time_s: float
    value: float


@dataclass(frozen=True, slots=True)
class HoverTarget:
    """Every drawn point a pointer is within reach of, and what the hover says of them.

    **Every run inside the radius answers, rather than the nearest one**
    (project owner, 2026-09-19, ratified, over breaking the tie toward the
    trunk and over deferring to the axis-compression fix). `PL-JVHL` measured
    the alternatives: with two runs on one axis the two runs' points for a
    slow compartment are inside the 12 px radius over essentially the whole
    of the hoverable band, so keeping the single nearest point let a 2 px
    hand movement swap which run's value was read, silently and on 75.4-99.9%
    of the fat axis. Preferring the curve nearest along its length and
    requiring the pointer inside a run's own band were both measured and both
    changed nothing; answering for every run is the only rule that took the
    swap rate to zero, because nothing is then settled by which point is
    marginally nearer.

    **Every compartment inside the radius answers too, on the same rule**
    (project owner, 2026-09-20, ratified, over recording the measurement and
    leaving the flip to the axis fix, `PL-QYBW`). That rule left distance to
    settle which *compartment* answered, on the reasoning that a reader aims
    at a curve; `PL-0RZ0` measured what the same axis compression does to
    that. Two or more compartments are inside the radius over 15.2-45.7% of
    the hoverable area on the two-run chart and 37.0% on the single-run one,
    and a 2 px move changed which one answered on 6.6-13.6% of contended
    pointer pairs - printing a different number on 99.9% of them, by a median
    17.1-17.9x for muscle against fat. The box does not move when it happens:
    the two winning points are a median 0.9 px apart, so only the words and
    the numbers change. There is no aim to respect at that separation, which
    is `PL-QYBW`'s own second consequence, so a rule that picked would be
    picking arbitrarily rather than honouring an aim.

    Attributes:
        quantities: Every trace within reach, in the frame's drawing order
            and never empty: compartments, or `RecordedQuantity.WASH_IN_RATIO`
            alone on the wash-in plot, which draws one trace and so has no
            compartment for distance to settle.
        readings: One per run and compartment within reach, in the frame's own
            drawing order - compartment by `ChartFrame.visible`, run by
            `ChartFrame.runs` - and never empty. Ordered by the frame rather
            than by distance, so that no part of the readout moves with a hand
            movement too small to aim with.
        readout: The text to show: the three-line form while one point
            answers, and `format_compared_trace_hover`'s while more than one
            does.
    """

    quantities: tuple[RecordedQuantity, ...]
    readings: tuple[HoverReading, ...]
    readout: str

    @property
    def anchor(self) -> HoverReading:
        """The reading the box is hung from: the first, in the frame's drawing order.

        A position rather than a value, and chosen by drawing order for the
        same reason `readings` is ordered that way - a box that hung from
        whichever point was nearest would jump with a movement too small to
        aim with, which is the defect this class exists to remove wearing
        its layout's clothes.
        """

        return self.readings[0]


def nearest_trace_point(
    frame: ChartFrame,
    time_s: float,
    percent: float,
    seconds_per_pixel: float,
    percent_per_pixel: float,
    radius_pixels: float,
) -> HoverTarget | None:
    """Which drawn compartment points, at the instant a pointer names, are within its reach.

    Distance is measured in pixels rather than in axis units, because the
    two axes are in different units and a reader's hand is in neither: a
    tolerance stated in seconds would be a hair at the 12-hour base and a
    whole window at the one-minute one. The caller supplies the scale of
    the view it is drawing.

    **The pointer's position along the time axis names the instant, and
    distance decides only what is in reach** (`PL-1K9G`). Each run answers at
    its drawn instant nearest the pointer in time, ties to the earlier, and
    every compartment of it whose point there is inside the radius answers -
    so every compartment of one run answers at one instant, and a hand
    movement up or down the percent axis can change what is in reach but
    never the instant a value is labelled with. Taking each trace's nearest
    point in both dimensions instead let the pointer's height choose the
    column on a sloped trace: on the single-run chart 70.1% of the boxes
    holding two or more of one run's readings carried two instants, up to
    72 s apart on the 60-minute axis and fifteen minutes on the 12-hour one.
    The radius is measured to the point at the named instant rather than to
    the nearest of the trace's points, so every value reported is at that
    instant *and* within reach of the pointer; the cost is aim beside a steep
    segment, and no drawn instant becomes unreachable. `docs/MODEL.md` §
    "Where more than one trace answers" carries the measurement.

    **Distance settles nothing between traces either.** Every run and every
    compartment whose point is inside the radius answers, so no hand movement
    can change which of them the box reports without also changing what is in
    reach. `HoverTarget` carries why, `PL-JVHL` the run measurements and
    `PL-0RZ0` the compartment ones.

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
        Every run's and compartment's drawn point at the named instant that
        is within the radius, or `None` when none is that close.
    """

    columns = [_nearest_column(run.times_s, time_s) for run in frame.runs]
    answering: list[tuple[int, RunFrame, RecordedQuantity, int]] = []

    # In the frame's own drawing order - compartment by the trace table, run
    # by the chart - because it is what the readout's lines are ordered by,
    # and a readout whose lines could reorder under the pointer would be this
    # defect in its layout.
    for quantity in frame.visible:
        for run_index, (run, column) in enumerate(zip(frame.runs, columns, strict=True)):
            if column is None:
                continue

            distance = _pixel_distance(
                time_s,
                percent,
                run.times_s[column],
                percent_from_fraction(Fraction(run.fractions[quantity][column])),
                seconds_per_pixel,
                percent_per_pixel,
            )

            if distance <= radius_pixels:
                answering.append((run_index, run, quantity, column))

    if not answering:
        return None

    first_run, first_quantity, first_column = answering[0][1:]

    return HoverTarget(
        quantities=tuple(dict.fromkeys(quantity for _, _, quantity, _ in answering)),
        readings=tuple(
            HoverReading(
                run=run_index,
                quantity=quantity,
                time_s=run.times_s[column],
                value=percent_from_fraction(Fraction(run.fractions[quantity][column])),
            )
            for run_index, run, quantity, column in answering
        ),
        readout=(
            format_trace_hover(first_run, first_quantity, first_column, len(frame.runs))
            if len(answering) == 1
            else format_compared_trace_hover(
                [(run, quantity, column) for _, run, quantity, column in answering], len(frame.runs)
            )
        ),
    )


def nearest_wash_in_point(
    frame: ChartFrame,
    time_s: float,
    ratio: float,
    seconds_per_pixel: float,
    ratio_per_pixel: float,
    radius_pixels: float,
) -> HoverTarget | None:
    """Which drawn wash-in points, at the instant a pointer names, are within its reach.

    `nearest_trace_point` for the wash-in plot, on the same rules: the pointer
    names the instant, each run answers at its drawn wash-in instant nearest
    it in time if that point is inside the radius, and every run in reach
    answers. A run's stretches are one set of drawn instants with gaps where
    the ratio left its domain, so the instant named across a gap is the
    nearer end of either stretch. One plot-wide trace rather than six, so
    there is no compartment for distance to settle - but the retired
    two-dimensional distance still let a vertical 2 px movement move the one
    instant this reports, on 23.9-44.4% of such movements (`PL-1K9G`). The
    equilibrium line and the control marks are not candidates.

    Args:
        frame: The frame on the plot.
        time_s: The pointer's position along the time axis.
        ratio: The pointer's position on the ratio axis.
        seconds_per_pixel: The time axis's scale.
        ratio_per_pixel: The ratio axis's scale.
        radius_pixels: How far, in pixels, a point may be from the pointer
            and still answer.

    Returns:
        Every run whose drawn wash-in point at the named instant is within
        the radius, or `None`.
    """

    answering: list[tuple[int, RunFrame, WashInStretch, int]] = []

    # In drawing order, for the reason `nearest_trace_point` states.
    for run_index, run in enumerate(frame.runs):
        named = _nearest_wash_in_point(run.wash_in, time_s)

        if named is None:
            continue

        stretch, column = named
        distance = _pixel_distance(
            time_s,
            ratio,
            stretch.times_s[column],
            stretch.ratios[column],
            seconds_per_pixel,
            ratio_per_pixel,
        )

        if distance <= radius_pixels:
            answering.append((run_index, run, stretch, column))

    if not answering:
        return None

    return HoverTarget(
        quantities=(RecordedQuantity.WASH_IN_RATIO,),
        readings=tuple(
            HoverReading(
                run=run_index,
                quantity=RecordedQuantity.WASH_IN_RATIO,
                time_s=stretch.times_s[column],
                value=stretch.ratios[column],
            )
            for run_index, _, stretch, column in answering
        ),
        readout=(
            format_wash_in_hover(answering[0][1], answering[0][2], answering[0][3], len(frame.runs))
            if len(answering) == 1
            else format_compared_wash_in_hover(
                [(run, stretch, column) for _, run, stretch, column in answering]
            )
        ),
    )


def _nearest_column(times_s: Sequence[float], time_s: float) -> int | None:
    """The drawn column nearest `time_s` in time, or `None` where nothing is drawn.

    The instants are ascending, so this is one bisection rather than a scan
    of the run: a pointer moving at sixty events a second over two runs is
    otherwise a comparison per drawn point per event. A tie goes to the
    earlier column, so the answer is a function of the instant alone rather
    than of which neighbour a search happened to reach first.
    """

    after = bisect_left(times_s, time_s)

    if after == len(times_s):
        return after - 1 if times_s else None

    if after == 0 or times_s[after] - time_s < time_s - times_s[after - 1]:
        return after

    return after - 1


def _nearest_wash_in_point(
    stretches: Sequence[WashInStretch], time_s: float
) -> tuple[WashInStretch, int] | None:
    """A run's drawn wash-in point nearest `time_s` in time, across every stretch it draws.

    A tie goes to the earlier stretch, as it goes to the earlier column
    within one - which is also where a column drawn twice, as the shared end
    of two stretches, is read from.
    """

    named: tuple[float, WashInStretch, int] | None = None

    for stretch in stretches:
        column = _nearest_column(stretch.times_s, time_s)

        if column is None:
            continue

        apart_s = abs(stretch.times_s[column] - time_s)

        if named is None or apart_s < named[0]:
            named = (apart_s, stretch, column)

    return None if named is None else (named[1], named[2])


def _pixel_distance(
    x: float, y: float, drawn_x: float, drawn_y: float, x_per_pixel: float, y_per_pixel: float
) -> float:
    """How far apart two plot positions are on screen, in pixels."""

    return sqrt(((x - drawn_x) / x_per_pixel) ** 2 + ((y - drawn_y) / y_per_pixel) ** 2)
