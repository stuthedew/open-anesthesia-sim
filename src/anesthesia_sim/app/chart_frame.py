"""What one frame of the concentration chart and the wash-in plot draws.

This module is the chart's model. It describes everything a frame puts on
either plot as plain values, evaluated from the run and independent of the
toolkit that paints them. `app/qt_chart.py` reads a `ChartFrame` and moves
pyqtgraph items to match. Nothing here imports Qt, Flet or numpy, and nothing
here keeps a widget. The split is the same one that `app/formatting.py` makes
for a displayed string. What the chart *claims* is a presentation-correctness
question: which compartment a curve shows, where the 1 MAC line sits, which
instants are drawn, and what a hover says. Kept here, those claims can be read
and tested without a display, and `tests/unit/test_chart_frame.py` tests them
that way.

**Every drawn point is a state of the run at the instant where it is drawn.**
`SimulationController.drawn_window` evaluates the run's definition at the
columns the axis is divided into. It adds one column per control event in the
window and one column at each end of the drawn range (`PL-2FM6`). So nothing
here interpolates, extrapolates or synthesizes a value. The plot itself draws
the straight segment between two points, and that segment is honest for two
reasons. A control event always gets its own column. And the columns are one
per pixel of the plot they are drawn on (`chart_columns`, `PL-GS3R`), so no
segment spans more than a pixel of time.

**One evaluation serves every trace of a run.** A state carries every
compartment at once, so a frame reads the window once per run, and every trace
of that run draws the same instants. Two traces of one run therefore cannot
come from different instants. The wash-in stretches are built from the same
columns that the compartment chart drew, so the two plots cannot differ even
by a step that the run took in between.

**Six compartment traces, and the table that ties each one to what it draws.**
`COMPARTMENT_TRACES` is the one place where a compartment is paired with its
colour, its dash pattern, its legend words and the gloss its hover shows.
Plotting one compartment's values on another's line misstates the run as
surely as a wrong number does. So the pairing is one record per trace rather
than parallel lists. `app/qt_chart.py` draws its curves and its legend from
this table rather than keeping a second copy (`PL-2CS8`).

**The window is a viewport, and the run fills it.** This module decides the
axis a frame draws from the selected time base and from the newest instant
that any run on the chart has reached. Under "Fit run" the axis is fitted to
that instant. Otherwise the axis keeps the chosen width and follows that
instant. Every run draws into that one window. `app/chart_time_base.py`
describes both rules and explains why they are not one rule.
"""

from __future__ import annotations

from bisect import bisect_left
from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass, replace
from math import ceil, floor, isfinite, sqrt
from types import MappingProxyType
from typing import Final

from anesthesia_sim.app.chart_time_base import (
    CHART_GRID_RESOLUTIONS_S,
    ChartTimeBase,
    fit_to_run,
    fitted_window,
    following_window,
    preview_window,
    tick_times,
)
from anesthesia_sim.app.control_timeline import ControlAdjustment
from anesthesia_sim.app.controller import SettingPreview, SimulationController, SimulationSnapshot
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
    COMPARTMENT_FRACTION_NAMES,
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
    MINIMUM_TRACE_STROKE_WIDTH,
    MIXED_VENOUS_COLOR,
    MUSCLE_COLOR,
    PREVIEW_WIDTH_STEP,
    VESSEL_RICH_COLOR,
)
from anesthesia_sim.app.wash_in import WASH_IN_EQUILIBRIUM_RATIO, is_wash_in
from anesthesia_sim.core.concentration import Fraction, MacPercent, Percent, percent_from_fraction
from anesthesia_sim.core.supported_ranges import CaseInstant, require_case_instant

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
    "WASH_IN_HOVER_PAST_EQUILIBRIUM_TEXT",
    "WASH_IN_TERMINUS_CEILING",
    "ChartFrame",
    "HoverReading",
    "HoverTarget",
    "PreviewRequest",
    "RunFrame",
    "RunInput",
    "RunPreview",
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
    "preview_stroke_width",
    "preview_trace_style",
    "resample_owed",
    "run_trace_style",
    "trace_style",
    "wash_in_axis_ticks",
    "wash_in_stretches",
]

# The minimum number of *grid columns* an axis is divided into. The chart's
# evaluated instants are placed on these columns. `chart_columns` decides the
# count a frame actually uses from the plot's width in pixels. It uses one
# column per pixel boundary, so that no chord between two drawn instants
# spans more than a pixel of time (`PL-GS3R`, decided 2026-09-14). This
# constant is what `chart_columns` returns for a plot narrower than 150 px, or
# for one not yet laid out. The number of points is not set directly but
# follows from the columns. It is the grid columns inside the drawn range, plus
# the two ends of that range, plus one column per control event in the window.
# That last term has no cap. `MAX_CHART_CONTROL_MARKS` limits the marks drawn,
# not the event columns. `RunDefinition._anchored_columns` adds an event column
# for every setting change inside the window.
#
# This constant has changed meaning over time. It was a bucket count while the
# chart selected recorded samples, and a point ceiling before that, when the
# algorithm was min/max envelope decimation. From `PL-2FM6` until `PL-GS3R` it
# was a fixed budget of 150 columns at every width. At the 12-hour base, that
# budget drew a 290 s chord through the steep early wash-in. The alveolar trace
# was then drawn up to 0.53 pp below the run (sevoflurane 2% to 4%), and up to
# 3.8 pp below it (a desflurane overpressure induction). The minimum stays at
# the fixed budget's number because nothing narrower has been measured. It is
# the count the Flet chart drew at until `PL-25KS` retired that chart, and the
# Flet chart could afford no more (`PL-YSZN`, `PL-YDKJ`).
CHART_COLUMN_BUDGET_PER_SERIES: Final = 150

# How many control marks the chart can show at once. The marks come from a
# fixed pool rather than one mark per adjustment. So a run full of adjustments
# costs no construction per frame, and the bound is stated: the display counts
# what the pool cannot show rather than dropping it silently (`docs/MODEL.md`
# § "The control-input timeline", "Bounds are displayed, not silent").
MAX_CHART_CONTROL_MARKS: Final = 24

# How many compartments may be drawn while more than one run is on the chart.
#
# **This cap is the part of `PL-HLD5`'s encoding that the rest depends on, not a
# nicety.** With six compartments, every line-level channel is already used.
# Line style shows the compartment across six patterns, colour is its second
# cue, and width varies from 2 px to 3 px across the six. So no channel is free
# to show the run until the cap frees one. Two compartments times two runs is
# four curves, and the run's two width levels have to tell those four apart.
#
# The cap is a colour-capacity limit on the *chart*. It never reduces what the
# display must show. `docs/MODEL.md` § "Minimum displayed outputs" requires all
# six compartment readouts to stay on screen for both runs while comparing, and
# it names this cap when it says so. The cap removes four curves, and the
# readouts keep those four values on screen.
COMPARED_COMPARTMENT_CAP: Final = 2

# Gridlines fall at quarter fractions. Every published wash-in figure uses this
# ruling, and it is the spacing a reader compares against. The axis is labelled
# at exactly these values rather than at whatever interval the plot would choose
# for itself. A rule at 0.25 beside a label at 0.2 puts two different scales on
# one axis, and a reader who takes a value off the nearest gridline would take
# it off the wrong one. The same rule keeps the compartment chart's percent axis
# labelled at its own gridlines (`percent_axis_ticks`), as `PL-Q4VH` asked.
WASH_IN_GRID_INTERVAL: Final = 0.25

# The wash-in axis extends above equilibrium rather than stopping at it. This
# is a legibility requirement, not a spare margin. The trace ends where it
# crosses `WASH_IN_EQUILIBRIUM_RATIO`. If the axis topped out there, that ending
# would land on the frame, where a line that stopped and a line the plot cut
# off look exactly alike. Raising the axis leaves clear space above the ending,
# so the reader can see that the trace itself stopped. 1.15 leaves that space
# without adding a fifth labelled interval. The ruling and the labels stop at
# 1.00, which is where the readable scale ends.
WASH_IN_AXIS_MAXIMUM: Final = 1.15

# How far past equilibrium the trace may be drawn, so that its ending lands on
# the line rather than a step short of it. `wash_in_stretches` gives the whole
# reasoning, including why the bound is stated rather than taken from the
# measured 1.00235 that a 0.1 s step actually produces. It is set below
# `WASH_IN_AXIS_MAXIMUM` rather than at it, so that even the widest crossing it
# allows still has clear space above it.
WASH_IN_TERMINUS_CEILING: Final = 1.05

# How many separate stretches of wash-in the plot can draw at once. The trace
# breaks wherever the ratio leaves the domain that `app/wash_in.py` states. For
# example, a vaporizer turned off and later reopened gives two stretches, not
# one line drawn through the washout between them. The pool is fixed for the
# same reason the control-mark pool is. Eight is more stretches than a taught
# case produces inside one chart window. What does not fit is counted and
# shown, never dropped silently.
MAX_CHART_WASH_IN_SEGMENTS: Final = 8

# The second line of the wash-in trace's hover readout, which says what the
# value is. The parenthesis repeats the caption that `app/wash_in.py` already
# uses, for the reason given there: F_I is the modelled circuit, not the
# vaporizer dial. `docs/MODEL.md` § "The chart's hover readout: what the tooltip
# may show" derives the three-line form. The label uses a solidus rather than a
# division sign, because every non-ASCII character shown to a reader must first
# have been rendered and checked by eye (`tools/glyph_check.py`).
WASH_IN_HOVER_LABEL: Final = "Wash-in F_A/F_I (alveolar / modelled circuit)"

# The text that the wash-in hover prints, instead of a number, at a column past
# equilibrium. The crossing column, where the trace passes equilibrium, is drawn only
# so that the line meets the reference. Its quotient is above 1. Rule 2 of
# `app/wash_in.py` and `docs/MODEL.md` § "F_A/F_I as a displayed ratio" do not allow
# such a quotient to be shown as a wash-in fraction (`PL-YH6Z`). Printed under the
# wash-in label, it would suggest that wash-in can go past completion. It would do so
# at the dot that a reader is most likely to point at.
WASH_IN_HOVER_PAST_EQUILIBRIUM_TEXT: Final = "Past equilibrium: not a wash-in fraction"

# The resolution to which the hover rounds the instant it prints. It is the finest
# grid that a drawn column can sit on, a hundredth of a second. So the instant
# printed is the instant whose state is printed beside it (`PL-T5NJ`). Columns used
# to sit wherever the plot's width put them, such as at 410.7383 s, and the hover
# rounded that to the clock's tenth of a second. The state printed was still the
# state at 410.7383 s, up to 0.05 s from the printed instant. Early in a fast
# induction that difference matters. Desflurane at 18% and 10 L/min takes the
# circuit from 2.68% at 6.00 s to 2.70% at 6.04 s. So the hover at "6s" could print
# 2.70% while the readout row at 6 s showed 2.68%.
# `chart_time_base.grid_spacing_s` now rounds the column spacing down onto whole
# hundredths of a second. It rounds onto tenths instead wherever that adds few
# columns. Every other drawn instant (a bound, a control event, a fork) falls on a
# simulation step. Rounding to this resolution therefore removes only
# floating-point noise. The value is read from the grid's own declaration rather
# than written as a digit, so the two cannot drift apart.
HOVER_INSTANT_RESOLUTION_S: Final = CHART_GRID_RESOLUTIONS_S[-1]

# The word that opens every hover readout. It appears on every hover, not only
# on the two compartments that have a measured twin, because the readout is
# separate from the heading that would otherwise carry the word.
# `docs/MODEL.md` § "The chart's hover readout" explains why the qualifiers
# come before the number.
_HOVER_MODELLED_MARKER: Final = "Modelled"

# What separates the tokens of the hover's run-context line. It is one constant
# rather than a literal at each join, so a line built from three tokens or from
# four is punctuated the same way.
_HOVER_CONTEXT_SEPARATOR: Final = " · "

# `percent_axis_ticks` divides the top of the percent axis by its tick interval.
# Floating-point rounding can leave the result slightly less than a whole number.
# When the result falls short by no more than this tolerance, it counts as that
# whole number. So a top that is an exact multiple of the interval keeps its last
# tick. The tolerance is a billionth of one interval, so a tick kept this way is
# never more than that far above the top of the axis.
_PERCENT_TICK_COUNT_TOLERANCE: Final = 1e-9


@dataclass(frozen=True, slots=True)
class TraceStyle:
    """One compartment trace: what it draws, how it is drawn and what it is called.

    This record keeps together everything that has to agree about a single
    compartment. Before `PL-G59B`, the same trace was described in three
    places. The colour and dash pattern were where the series was built. The
    compartment it draws was in the Flet chart's series table, which was
    deleted with that chart in `PL-25KS`. The name and line-style words were in
    a legend row six hundred lines away. Keeping them in agreement was left to
    whoever remembered. A legend that names a line the chart is not drawing
    misstates the run as surely as a wrong number does.

    Attributes:
        quantity: The one recorded quantity this trace draws.
            `DrawnWindow.compartment_fractions` maps it to a state index, so
            this table keeps no second copy of that pairing.
        label: The compartment's name, as the legend and the hover show it.
        gloss: The clinical hedge that the readout row shows under the name,
            or `None` where it shows none. The gloss is not decoration.
            "end-tidal-equivalent" and "inspired" are required hedges
            (`PL-NV9W`, `PL-8M05`). What the model computes is a compartment,
            and what a clinician would compare it with on a monitor is a
            different, measured thing. The hover readout shows the gloss for
            the reason `docs/MODEL.md` § "The chart's hover readout" gives: a
            floating box has no readout row beside it to supply the hedge.
        color: The colour of the trace's line and of its legend swatch, from
            `app/theme.py`.
        stroke_width: Line width in display pixels.
        dash_pattern: Alternating dash and gap lengths in display pixels, or
            `None` for a solid line. The dash pattern is the channel that
            separates the traces, not decoration. `theme.py` records that the
            four simulated colour-vision models put pairs of these six colours
            as close as 1.01, far less than the 3:1 that would make colour
            sufficient. `docs/MODEL.md` § "The six compartment traces" has the
            table that this pattern is taken from.
        line_style: The dash pattern in words, for the legend. It is kept
            beside the pattern it describes rather than in the legend's own
            code, so that "dotted" cannot come to describe a line that is not
            dotted.
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
# **The six line styles are all different, because line style is what actually
# separates these curves.** The colours cannot: the closest pair sits at 1.01
# for normal colour vision, and no palette reaches 3:1. The circuit and
# vessel-rich traces were both solid until `PL-GVXP`. While they were, only
# colour separated that pair, so the redundant second channel existed in name
# only. A reader who takes a value off the wrong curve has misread a clinical
# quantity, not a decoration.
#
# **Which style goes on which trace is decided by the colours, not chosen
# freely.** The two traces that a reader can least separate by colour get the
# two marks that are easiest to separate by shape, and so on outward. The
# closest pairs are vessel-rich against fat at 1.01, and mixed venous against
# fat at 1.02 under simulated deuteranopia. So they get an even dash against an
# alternating dash-dot, and a short uniform dash against that same dash-dot.
# Each style differs from its partner in mark length, in gap length and in
# rhythm at once. The one genuinely confusable pair of styles in the set is the
# 2 px dots against the 4 px short dash. That pair is assigned to mixed venous
# against muscle, which has the *widest* colour separation of any pair of these
# six (1.45). `docs/MODEL.md` carries the matrix these choices were taken from.
#
# The vessel-rich trace's equal mark and gap is a rhythm that no other trace
# here has, because the other four dashed traces all draw more ink than gap.
# It is deliberately not a second long dash. At [8, 8] it looked like the
# alveolar trace's [10, 4] with wider gaps. Those two traces sit at 1.08 under
# simulated deuteranopia, which is no place for a pair that would have to be
# told apart by mark length alone.
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
    """Return the one trace that draws this compartment.

    Args:
        quantity: The recorded quantity to find the trace for.

    Returns:
        The style record of that trace.

    Raises:
        KeyError: If no trace draws the quantity. That is the case for
            `RecordedQuantity.WASH_IN_RATIO`, a derived quantity with its own
            plot rather than a compartment on this one. It is also the case
            for a quantity the table has lost.
    """

    return _TRACE_STYLE_BY_QUANTITY[quantity]


class RunCount(int):
    """The number of runs a chart draws, checked when built to be a whole number of at least one.

    A chart that draws no run has no trace, hover or legend entry to style,
    so code that uses the count may assume there is at least one run. That
    is the only property a count can be checked for on its own.
    `CompartmentSelection` checks how many runs the dashboard may draw at
    once, against `MAX_DISPLAYED_RUNS`. Arithmetic on a `RunCount` returns a
    plain `int`, as it does on any `int` subclass. So code that derives a new
    count builds it as a `RunCount` again where it uses it.

    Raises:
        TypeError: `run_count` is not an `int`, or is a `bool`. A `float` or
            a `bool` passed as a count is a programming error in the caller,
            not a count to reject.
        ValueError: `run_count` is less than one.
    """

    __slots__ = ()

    def __new__(cls, run_count: int) -> RunCount:
        if isinstance(run_count, bool) or not isinstance(run_count, int):
            raise TypeError(f"a run count is an int, not {type(run_count).__name__}")

        if run_count < 1:
            raise ValueError(f"a chart draws at least one run, not {run_count}")

        return super().__new__(cls, run_count)


class RunIndex(int):
    """The position of one run among a frame's runs, checked to be a whole number of zero or more.

    This type exists to reject a negative position. Python treats `-1` as
    the last run, so an unchecked negative index would draw the last run's
    values under the name of the run the caller meant. `CLAUDE.md`'s
    safety-critical standard counts that as a presentation failure
    (`PL-7694`). This type cannot check that the index names one of the
    runs, because that depends on the run count or the frame. The function
    that holds both makes that check.

    Raises:
        TypeError: `run_index` is not an `int`, or is a `bool`.
        ValueError: `run_index` is negative.
    """

    __slots__ = ()

    def __new__(cls, run_index: int) -> RunIndex:
        if isinstance(run_index, bool) or not isinstance(run_index, int):
            raise TypeError(f"a run index is an int, not {type(run_index).__name__}")

        if run_index < 0:
            raise ValueError(
                f"a run index is a position among the chart's runs, counted from 0, not {run_index}"
            )

        return super().__new__(cls, run_index)


def run_trace_style(quantity: RecordedQuantity, run_index: int, run_count: int) -> TraceStyle:
    """Return the style one run draws a compartment with, at that run's line width.

    The whole of the run's visual channel is decided here, in one place, so
    the chart, the legend swatch and any later view read one result rather
    than three. Everything about the compartment comes from `trace_style` and
    is returned unchanged: its colour, its dash pattern and the words for both.
    A compartment's appearance must not change on entering compare mode
    (`PL-HLD5`). Colour means "compartment" on the single-run chart, and a
    channel that meant something different on each side of a mode change
    would invite a misread clinical value.

    **The run is shown by line width, at two levels, and compared locally.**
    The distinction only has to be made between two curves of the *same*
    compartment. Those curves are next to each other by construction, so the
    reader does not have to decode the width across the plot.
    `app/theme.py`'s `COMPARED_RUN_WIDTH_STEP` explains why the first run is
    the wider of the two and why widening is better than narrowing. A single
    run is drawn exactly as it always was, so the width channel does not
    exist until there is a second run to tell apart.

    Args:
        quantity: Which compartment.
        run_index: Which run, as a position in the frame's runs.
        run_count: How many runs are on the chart.

    Returns:
        The compartment's style, with `stroke_width` set for this run.

    Raises:
        KeyError: If no trace draws `quantity` (see `trace_style`).
        TypeError: If `run_index` or `run_count` is not an `int` (`RunIndex`,
            `RunCount`).
        ValueError: If `run_index` does not address one of `run_count` runs.
            A style requested for a run the chart is not drawing would return
            a width that nothing on screen has.
    """

    not_drawn = ValueError(
        f"run {run_index} is not one of the {run_count} runs on the chart; a trace "
        "is drawn at the width of a run that is being drawn"
    )

    try:
        index, count = RunIndex(run_index), RunCount(run_count)
    except ValueError as error:
        raise not_drawn from error

    if index >= count:
        raise not_drawn

    style = trace_style(quantity)
    widened = count > 1 and index == 0

    if not widened:
        return style

    return replace(style, stroke_width=style.stroke_width + COMPARED_RUN_WIDTH_STEP)


def preview_stroke_width(run_stroke_width: float) -> float:
    """Return how wide a preview is drawn, given the width of the run's own curve.

    The preview is one `PREVIEW_WIDTH_STEP` thinner than the run's curve, so a
    prediction never carries the visual weight of the run that happened. It is
    never thinner than `MINIMUM_TRACE_STROKE_WIDTH`. An antialiased line thinner
    than that has a contrast ratio less than the 3:1 minimum against the panel
    (`docs/MODEL.md` § "The six compartment traces").

    Args:
        run_stroke_width: The width of the narrowest real curve drawn for the
            same compartment, in display pixels.

    Returns:
        The preview's width, in display pixels.
    """

    return max(MINIMUM_TRACE_STROKE_WIDTH, run_stroke_width - PREVIEW_WIDTH_STEP)


def preview_trace_style(quantity: RecordedQuantity, run_index: int, run_count: int) -> TraceStyle:
    """Return the style in which one run's preview of a compartment is drawn.

    It is the compartment's `trace_style`, with the width that
    `preview_stroke_width` gives and nothing else changed. The width is based
    on the width the compartment's curve has when only one run is drawn, not
    on the previewing run's own width. In compare mode the first run is drawn
    one step wider, and the other run's real curves can lie inside the
    preview's region. A preview based on the first run's width would then be
    wider than those real curves. The width cue would then make the prediction
    look heavier than a run that happened.

    The colour and the dash pattern stay the compartment's own, deliberately.
    They are what tells the six traces apart (`PL-GVXP`), and inside the
    preview they have to do the same work (`PL-5B1N`, project owner,
    2026-09-27, ratified). That decision was chosen over drawing the run solid
    and the preview dotted. A dotted preview would be confused with the muscle
    trace, which is drawn with dots.

    Args:
        quantity: Which compartment.
        run_index: Which run, as a position in the frame's runs.
        run_count: How many runs are on the chart.

    Returns:
        The compartment's style at the preview's width.

    Raises:
        KeyError, TypeError, ValueError: As `run_trace_style`.
    """

    run_trace_style(quantity, run_index, run_count)
    style = trace_style(quantity)

    return replace(style, stroke_width=preview_stroke_width(style.stroke_width))


def compared_compartments(
    shown: Collection[RecordedQuantity], run_count: int
) -> tuple[tuple[RecordedQuantity, ...], int]:
    """Return the compartments a frame draws for this many runs, and how many it cannot draw.

    The cap is applied here, in the one place that decides what the chart
    draws, so that no view can keep a selection the plot is not honouring.
    `COMPARED_COMPARTMENT_CAP` explains why the cap is what frees the width
    channel for the run.

    The compartments are kept in table order and taken from the top of the
    table, not in the order a reader clicked them. So the drawn pair is the
    same pair whatever route reached the selection. It also means that a
    reader who has chosen nothing sees the circuit and alveolar traces, which
    lead the table.

    Args:
        shown: The compartments the reader has left drawn.
        run_count: How many runs are on the chart. One run is not capped: the
            six-trace encoding works as it always has, and only a second run
            uses the channel that the cap frees.

    Returns:
        The compartments drawn, in table order, and the number of selected
        compartments that the cap left undrawn. The display shows the second
        value rather than dropping it silently, per `docs/MODEL.md` § "The
        control-input timeline", "Bounds are displayed, not silent".
    """

    selected = tuple(style.quantity for style in COMPARTMENT_TRACES if style.quantity in shown)

    if run_count <= 1:
        return selected, 0

    return selected[:COMPARED_COMPARTMENT_CAP], max(0, len(selected) - COMPARED_COMPARTMENT_CAP)


def chart_columns(plot_width_px: float) -> int:
    """Return the number of grid columns the axis is divided into, for a plot this wide.

    There is one column per pixel boundary: `plot_width_px` intervals across
    the axis, so one more column than that. The count is never less than
    `CHART_COLUMN_BUDGET_PER_SERIES`. This is the rule `PL-GS3R` chose: keep
    the chord at one pixel of time, whatever the time base. Take two drawn
    instants no more than a pixel apart, both exact. A monotone run and the
    straight segment drawn between them cross every level inside the same
    pixel. So the drawn line is within a pixel of time of the run everywhere,
    and on the run at every drawn instant. The count therefore follows the
    plot, not the span. A twelve-hour axis on a 1 000 px plot draws 1 001
    columns at a 43 s chord, and a fifteen-minute axis on the same plot draws
    1 001 columns at 0.9 s. `docs/MODEL.md` § "What the chart draws" states
    the guarantee, what it leaves between drawn instants, and what was
    measured against it.

    The width is in logical pixels, as Qt lays the plot out, which is the
    resolution at which the axis is ruled and labelled. A high-DPI display
    draws each chord across as many device pixels as its device-pixel ratio.

    Args:
        plot_width_px: The width of the plot area the axis spans, in logical
            pixels. Pass zero for a plot not yet laid out, which returns the
            minimum. A fractional width is rounded up.

    Returns:
        The number of grid columns, at least `CHART_COLUMN_BUDGET_PER_SERIES`.

    Raises:
        ValueError: If the width is negative or not finite. A caller that
            has no width says so by passing zero, not by passing whatever
            value it has.
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
        ratios: F_A/F_I at each instant, dimensionless, one per entry of
            `times_s`.
        ends_above_equilibrium: Whether the last point is the crossing
            column rather than the live end of the run. The crossing column
            is the one drawn past equilibrium so that the curve meets the
            reference line. Only a stretch that *stopped* carries the
            terminus marker, because the growing right-hand end of a run is
            not an ending.
    """

    times_s: tuple[float, ...]
    ratios: tuple[float, ...]
    ends_above_equilibrium: bool


@dataclass(frozen=True, slots=True)
class RunPreview:
    """The trajectory one run would take under a setting the reader is trying, as drawn.

    **This is a prediction, a third kind of value beside a modelled state and
    a measurement** (`docs/MODEL.md` § "A preview of an unapplied setting").
    It depends on a setting that the learner has not applied and may never
    apply. So everything that draws it marks it as a prediction. It lies in a
    region of its own, which the run that happened never enters. It is
    labelled in the plot, and it is drawn thinner than the run (`PL-5B1N`).
    The hover never shows its values, because the hover reads only
    `RunFrame.times_s` and `RunFrame.wash_in`.

    Attributes:
        label: The text the plot draws for the preview. It names the run when
            more than one run is drawn, the control and the value tried, and
            it says that the value is not applied. It is drawn inside the
            region, so a screenshot taken during a drag includes it.
        region_s: Where the region lies, in simulated seconds. It starts at
            the run's reach, which is the instant the run has reached so far.
            It ends at the axis's right edge, or at the end of the supported
            run length if that comes first.
        times_s: The predicted instants, ascending, in simulated seconds. The
            first is the run's reach, where the prediction meets the run.
        fractions: Each compartment's predicted value at every instant, as a
            fraction of one atmosphere. Each value is built as a `Fraction`
            labelled with its compartment's name, as in `RunFrame.fractions`.
        wash_in: The predicted F_A/F_I stretches, oldest first. They are the
            most recent stretches that fit the pool.
    """

    label: str
    region_s: tuple[float, float]
    times_s: tuple[float, ...]
    fractions: Mapping[RecordedQuantity, tuple[Fraction, ...]]
    wash_in: tuple[WashInStretch, ...]

    def percents(self, quantity: RecordedQuantity) -> tuple[float, ...]:
        """Return one predicted trace in percent, by the conversion `RunFrame.percents` makes."""

        return tuple(percent_from_fraction(fraction) for fraction in self.fractions[quantity])


@dataclass(frozen=True, slots=True)
class RunFrame:
    """One run's part of a frame: its drawn states, stretches and marks.

    Attributes:
        label: What this run is called in text, as the legend and every
            readout that names a run show it. The caller passes it in, rather
            than this module deriving it from a position. So one run has the
            same name on the chart, in the legend and on its own panel, and a
            view that drew a different subset could not rename it
            (`.claude/rules/ui-areas.md`). `docs/MODEL.md` § "Minimum
            displayed outputs" requires the run to be named in text. Colour
            is used for the compartment, and position alone fails a reader
            who has looked away and back.
        branch_point_s: The instant at which this run forked from the run it
            was opened from, in simulated seconds. It is `None` for a run
            that is not a branch, or whose fork lies outside the drawn
            window. The fork is the one instant at which two compared runs
            stop being the same run. So it is marked, rather than left for
            the reader to find by following two coincident curves until they
            part.
        agent_id: The substance every value here belongs to, under the
            identifier the run records it by.
        agent_display_name: The same agent, as the hover names it.
        mac_percent: The agent's 1 MAC as a percent of one atmosphere. It is
            the divisor from which every MAC multiple in the hover is
            produced. It is kept beside the values it scales, so a readout
            cannot pair one agent's concentration with another agent's MAC.
        elapsed_s: How far the run has reached, in simulated seconds.
        times_s: The drawn instants, ascending, in simulated seconds. Every
            compartment trace of this run shares them, which makes it
            structurally impossible for two of those traces to come from
            different instants.
        fractions: Each compartment's value at every drawn instant, as a
            fraction of one atmosphere, keyed by the quantity the trace
            draws. Every compartment is present whether or not it is shown,
            because what a trace *draws* does not change with whether it is
            currently on the chart. Each value was built as a `Fraction`
            under its compartment's name when the frame was assembled
            (`_run_frame`). So nothing that reads a value can reject it after
            a frame exists: not the conversion to percent, not the hover and
            not the cursor readouts (`PL-7DJK`).
        wash_in: The F_A/F_I stretches drawn, oldest first. They are the most
            recent stretches that fit the pool.
        undrawn_wash_in_stretches: How many stretches inside the window the
            pool could not draw. The display shows this count rather than
            hiding it.
        control_marks_s: The simulated times marked, ascending. They are the
            most recent adjustments that fit the pool, so a reader watching a
            run sees the change they just made against the curve it moved.
        undrawn_control_marks: How many adjustments inside the window the
            pool could not mark. The display shows this count rather than
            hiding it.
        preview: The trajectory this run would take under a setting the
            reader is dragging, or `None` while no drag is held on this run.
    """

    label: str
    branch_point_s: CaseInstant | None
    agent_id: str
    agent_display_name: str
    mac_percent: MacPercent
    elapsed_s: CaseInstant
    times_s: tuple[float, ...]
    fractions: Mapping[RecordedQuantity, tuple[Fraction, ...]]
    wash_in: tuple[WashInStretch, ...]
    undrawn_wash_in_stretches: int
    control_marks_s: tuple[float, ...]
    undrawn_control_marks: int
    preview: RunPreview | None = None

    def percents(self, quantity: RecordedQuantity) -> tuple[float, ...]:
        """Return one trace's drawn values in the unit the percent axis is labelled in.

        This is the one fraction-to-percent conversion the chart makes. It is
        here rather than in the toolkit layer, so that a factor of a hundred
        can be wrong in one place rather than in seven. It cannot reject a
        value. Every entry is a `Fraction` that the frame built, and
        `percent_from_fraction` rejects no `Fraction`. So a toolkit that
        converts trace by trace cannot be left with some traces redrawn and
        others not (`PL-7DJK`).

        Args:
            quantity: Which compartment.

        Returns:
            One percent per entry of `times_s`.
        """

        return tuple(percent_from_fraction(fraction) for fraction in self.fractions[quantity])


@dataclass(frozen=True, slots=True)
class ChartFrame:
    """Everything one frame puts on the concentration chart and the wash-in plot.

    Attributes:
        time_base: The width the frame is drawn at, and the interval at which
            it is ruled.
        fitted: Whether the width was derived from the run ("Fit run") or
            chosen by the reader. The caption states which, because the same
            plot showing fifteen minutes and showing twelve hours makes two
            different claims about what a flat trace means.
        start_s: Left edge of the window, in simulated seconds.
        stop_s: Right edge of the window, in simulated seconds.
        tick_times_s: Where the gridlines and axis labels fall, on both
            plots. They are multiples of the interval measured from the
            case's zero, so the grid stays still as the window slides.
        columns: The number of grid columns the window was divided into. It
            is one per pixel boundary of `plot_width_px`, with a minimum, per
            `chart_columns`.
        plot_width_px: The width of the plot the frame was drawn for, in
            logical pixels. It is recorded so that a frame says what it was
            drawn for, which makes its chord width checkable afterwards.
        mac_percent: The agent's 1 MAC as a percent of one atmosphere. It is
            the divisor against which every MAC-denominated mark below is
            placed.
        axis_top_percent: The top of the compartment chart's percent axis.
            It is built as a `Percent` when the frame is assembled. So the
            off-scale notice, which converts it back, cannot reject it after
            the chart has drawn (`PL-7DJK`).
        grid_interval_percent: The spacing of the compartment chart's
            horizontal rules.
        percent_ticks: The labels on that chart's left axis, each at a
            gridline.
        mac_ticks: The labels on its right axis, as (percent position, MAC
            text).
        one_mac_percent: Where the 1 MAC line is drawn.
        mac_awake_band_percent: The MAC-awake band's lower and upper edges.
        visible: Which compartments are drawn, in table order. This is
            presentation state only, and the simulation never reads it. With
            more than one run, it is the reader's selection limited by
            `COMPARED_COMPARTMENT_CAP`, which `compared_compartments`
            applies.
        undrawn_compartments: How many selected compartments the cap left
            undrawn. It is zero for a single run, which is not capped. The
            display shows this count rather than hiding it. A selection that
            the chart is not honouring, mentioned nowhere, amounts to a
            legend naming a line that is not there.
        runs: One `RunFrame` per run on the chart, in drawing order.
    """

    time_base: ChartTimeBase
    fitted: bool
    start_s: float
    stop_s: float
    tick_times_s: tuple[float, ...]
    columns: int
    plot_width_px: float
    mac_percent: MacPercent
    axis_top_percent: Percent
    grid_interval_percent: float
    percent_ticks: tuple[tuple[float, str], ...]
    mac_ticks: tuple[tuple[float, str], ...]
    one_mac_percent: float
    mac_awake_band_percent: tuple[float, float]
    visible: tuple[RecordedQuantity, ...]
    undrawn_compartments: int
    runs: tuple[RunFrame, ...]

    @property
    def run_count(self) -> RunCount:
        """How many runs the frame draws, as the checked count that its users take.

        `assemble_chart_frame` rejects a frame with no run, so building the
        count cannot fail.
        """

        return RunCount(len(self.runs))


@dataclass(frozen=True, slots=True)
class PreviewRequest:
    """A setting a reader is dragging on one run, and the label the plot gives it.

    Attributes:
        setting: The control and the value tried.
        label: The label the plot draws in the preview's region.
            `dashboard_frame.preview_label` writes it from the same name and
            value text that the slider beside it prints.
    """

    setting: SettingPreview
    label: str


@dataclass(frozen=True, slots=True)
class RunInput:
    """One run to draw, with the snapshot the same frame formats it from.

    Attributes:
        label: What this run is called in text. The caller supplies it,
            because the same word has to appear on the run's own panel beside
            the settings that produced it, and a name the chart invented
            would appear only on the chart.
        controller: The run.
        snapshot: The run's state, read once by the caller for this frame and
            passed down here. So a run's readouts and the traces beside them
            show one instant of one run, rather than two reads that happened
            to agree.
        adjustments: The run's control timeline, grouped into the acts a
            reader sees. The caller's `control_timeline.AdjustmentGrouping`
            supplies it, so a frame that recorded nothing regroups nothing.
        preview: The setting a reader is dragging on this run, or `None`.
    """

    label: str
    controller: SimulationController
    snapshot: SimulationSnapshot
    adjustments: tuple[ControlAdjustment, ...]
    preview: PreviewRequest | None = None


def resample_owed(frame: ChartFrame | None, plot_width_px: float) -> bool:
    """Return whether a plot this wide needs a frame sampled more finely than `frame`.

    A frame drawn on a plot wider than the width it was sampled for leaves
    chords wider than a pixel, which `chart_columns` exists to prevent
    (`PL-GS3R`). A plot narrower than that width needs nothing new: its
    columns are closer than a pixel apart, and the guarantee still holds. So
    this function asks whether the plot needs more columns than the frame
    has, not whether the widths are equal. A plot that has drawn no frame
    needs one.

    Each chart asks this about its own width. So when a reader widens a
    chart's Area, that chart needs a new frame from the dashboard even when
    the window kept its size (`PL-9LNF`).

    Args:
        frame: The frame the plot drew last, or None before its first.
        plot_width_px: The plot's width now, in logical pixels.

    Returns:
        True when the plot needs a frame with more columns than `frame`.

    Raises:
        ValueError: If the width is negative or not finite (`chart_columns`).
    """

    if frame is None:
        return True

    return chart_columns(plot_width_px) > frame.columns


def assemble_chart_frame(
    runs: Sequence[RunInput],
    time_base: ChartTimeBase | None,
    shown: Collection[RecordedQuantity],
    *,
    plot_width_px: float,
) -> ChartFrame:
    """Read every run once and work out everything the frame draws.

    The work takes four steps, in an order that makes two runs one picture
    rather than two. First the shared ruler is set from the reference run.
    Next the window is chosen so that it contains every run. Then the
    references are placed across that window. Only then does each run
    evaluate its own states into it.

    Args:
        runs: Every run on the chart, in drawing order, with the snapshot
            each is drawn from.
        time_base: The width the reader chose, or `None` for "Fit run".
        shown: The compartments the reader has left drawn.
        plot_width_px: The width of the plot the frame will be drawn on, in
            logical pixels. Where more than one plot draws the frame, it is
            the widest of them. The wash-in stretches are formed from the
            same columns, and a narrower plot loses nothing to columns that
            are closer than a pixel (`resample_owed`).
            `ConcentrationChart.plot_width_px` and `WashInChart.plot_width_px`
            report it. It is required rather than defaulted, because a frame
            drawn for a width nobody stated would silently be drawn at the
            minimum column count.

    Returns:
        The frame.

    Raises:
        ValueError: If the width is negative or not finite (see
            `chart_columns`), if no run is given, or if the runs are not all
            on one agent. A chart that every run shares draws one ×MAC ruler,
            one MAC-awake band and one 1 MAC line. All three are the agent's
            own published values. With two agents on one axis, one run's
            traces would be read against the other agent's divisor. That is a
            correct number under the wrong label, which `CLAUDE.md`'s
            safety-critical standard treats as a failure of the value.
        SimulationConfigurationError: If a drawn compartment value is outside
            0 to 1, and the error then names the compartment. It is also
            raised if the axis top is above 100% of an atmosphere, which
            happens for an agent whose MAC is above a third of an atmosphere.
            Every value the frame draws is built as its checked type here,
            before the frame exists. So a rejection leaves nothing half-drawn,
            and the interface halts every run on the chart (`PL-7DJK`). No
            supported setting reaches either limit (`core/concentration.py`).
        TypeError: If the newest run's `elapsed_s` was not built as a
            `CaseInstant`. Then nothing has checked the instant that the
            window is placed from against the supported run length
            (`PL-9DF9`).
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
    newest_instant_s = max(run.snapshot.elapsed_s for run in runs)
    require_case_instant("newest_instant_s", newest_instant_s)

    # The visible window has two modes. "Fit run" derives the width from the
    # newest instant, so that the whole case is drawn, starting at zero. A
    # chosen width is kept exactly and follows that instant, so that a trace's
    # slope on the plot means the same thing at every moment.
    #
    # A preview overrides both while a drag is held. The window keeps the
    # width and slides so that the previewing run's reach sits at mid-plot
    # (`preview_window`). A run that has stopped refuses every setting, so it
    # previews nothing, and the window does not move for it.
    previewing = [run for run in runs if _held_preview(run) is not None]

    if time_base is None:
        base = fit_to_run(newest_instant_s)
        start_s, stop_s = fitted_window(base)
    else:
        base = time_base
        start_s, stop_s = following_window(base, newest_instant_s)

    if previewing:
        start_s, stop_s = preview_window(base, max(run.controller.reached_s for run in previewing))

    columns = chart_columns(plot_width_px)
    # The cap is applied here rather than where a reader clicks. So what the
    # chart draws is capped however the selection was reached: by a legend, by
    # a restored layout, or by a second view that has no legend of its own
    # (`.claude/rules/ui-areas.md`).
    drawn, capped = compared_compartments(shown, len(runs))
    mac_percent = reference.agent_mac_percent
    top_percent = Percent(chart_axis_top_percent(mac_percent), name="axis_top_percent")
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
    """Evaluate one run into the window every run shares.

    Raises:
        SimulationConfigurationError: If a drawn value is outside 0 to 1,
            and the error names its compartment. The window evaluates the
            closed form at instants where no step of the run produced a
            compartment state. So each value is built as a `Fraction` here, under the name
            a step would give it (`run_series.COMPARTMENT_FRACTION_NAMES`),
            and the rejection comes before any `RunFrame` exists (`PL-7DJK`).
    """

    snapshot = run.snapshot
    # The traces are drawn under the agent that this frame's readouts were
    # formatted from, so a run's readouts and its traces cannot come from
    # different agents. If the snapshot names an agent that the window does not
    # describe, `DrawnWindow.compartment_fractions` raises rather than drawing
    # whatever the run does hold.
    window = run.controller.drawn_window(start_s, stop_s, columns)
    held = _held_preview(run)
    fractions = {
        quantity: tuple(
            Fraction(fraction, name=COMPARTMENT_FRACTION_NAMES[quantity])
            for fraction in window.compartment_fractions(
                RecordedSeries(snapshot.agent_id, quantity)
            )
        )
        for quantity in COMPARTMENT_QUANTITIES
    }
    stretches = _drawn_wash_in(window, snapshot.agent_id)
    inside = tuple(
        adjustment.started_at_s
        for adjustment in run.adjustments
        if start_s <= adjustment.started_at_s <= stop_s
    )
    marks = inside[-MAX_CHART_CONTROL_MARKS:]
    # The fork is marked only where it can be seen. A fork that the window has
    # scrolled past is not drawn at the edge. Drawing it there would place the
    # one instant at which two runs stop agreeing at a time when it did not
    # happen.
    opened_from = run.controller.opened_from
    branch_point_s = (
        opened_from.fork.instant_s
        if opened_from is not None and start_s <= opened_from.fork.instant_s <= stop_s
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
        preview=None if held is None else _run_preview(run, held, start_s, stop_s, columns),
    )


def _held_preview(run: RunInput) -> PreviewRequest | None:
    """Return the preview a run draws, or `None`.

    A run draws one while a drag is held on it and it still accepts settings.
    A stopped run refuses every setting, so a preview there would show a
    future the run cannot have (`SimulationController.refuses_settings`).
    """

    if run.preview is None or run.controller.refuses_settings:
        return None

    return run.preview


def _run_preview(
    run: RunInput, request: PreviewRequest, start_s: float, stop_s: float, columns: int
) -> RunPreview:
    """Evaluate the trajectory a run would take under the setting being dragged on it.

    The prediction comes from `SimulationController.preview_window`. That
    method reads the run without changing it, at the run's own model and
    version. The prediction's values are built as `Fraction`s labelled with
    each compartment's name, as the run's own values are (`_run_frame`). Its
    wash-in stretches come from `_drawn_wash_in`, the same function that
    produces the run's own stretches. So the two plots cannot disagree about
    the prediction, just as they cannot disagree about the run.

    Raises:
        SimulationConfigurationError: As `preview_window`, or if a predicted
            value is outside 0 to 1.
    """

    snapshot = run.snapshot
    window = run.controller.preview_window(request.setting, start_s, stop_s, columns)
    reached_s = run.controller.reached_s
    fractions = {
        quantity: tuple(
            Fraction(fraction, name=COMPARTMENT_FRACTION_NAMES[quantity])
            for fraction in window.compartment_fractions(
                RecordedSeries(snapshot.agent_id, quantity)
            )
        )
        for quantity in COMPARTMENT_QUANTITIES
    }
    stretches = _drawn_wash_in(window, snapshot.agent_id)

    return RunPreview(
        label=request.label,
        region_s=(reached_s, window.times_s[-1] if window.times_s else reached_s),
        times_s=window.times_s,
        fractions=MappingProxyType(fractions),
        wash_in=stretches[-MAX_CHART_WASH_IN_SEGMENTS:],
    )


def _drawn_wash_in(window: DrawnWindow, substance_id: str) -> tuple[WashInStretch, ...]:
    """Return every wash-in stretch inside the window, oldest first.

    The stretches are built from the same columns that the compartment chart
    draws. So the two plots cannot differ by a step the run took in between,
    and a stretch boundary can fall only on an instant the chart actually
    plots.
    """

    quotients = window.wash_in_quotients(substance_id)
    stretches = []

    for start, stop in wash_in_stretches(quotients, WASH_IN_TERMINUS_CEILING):
        # Every column of a stretch has a quotient. The anchors are inside the
        # domain, and the one extending column at each end was chosen because
        # it has one. `wash_in_stretches` is where that is enforced.
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
    """Return the stretches that the wash-in plot draws, as ranges over the drawn columns.

    A column *anchors* a stretch when its quotient is inside the wash-in
    domain that `app/wash_in.py` states. A column *extends* a stretch when
    all three of these hold:

    - it has a quotient at all, because its denominator was at least one
      displayed unit (rule 1 of `app/wash_in.py`);
    - that quotient is no higher than `extension_ceiling`;
    - it is next to an anchor.

    So a stretch is a run of in-domain columns plus one crossing column at
    each end. The crossing column shows where the curve left the domain,
    provided the plot can still show that column.

    **Why a stretch is extended at all.** Without the crossing column, the
    curve stops at the last column at or below equilibrium. That column is
    short of the boundary the curve crossed, and a trace that halts in clear
    space short of a line looks clipped rather than finished. With the
    crossing column, the curve meets the equilibrium reference line and ends
    on it.

    **Why the extension has a ceiling.** A run stepped at 0.1 s crosses
    equilibrium by only a hair. This was measured across every agent and
    every supported alveolar ventilation and cardiac output, at the maximum
    fresh gas flow. The state at the first step above equilibrium reaches
    1.00235. That measurement was taken step by step. A drawn column falls
    wherever the column spacing puts it, so a column can land on a later
    state of the run, which the measurement did not cover. The ratio is also
    not continuous in general. `BreathingCircuit.set_circuit_volume`
    conserves the agent in the circuit while it changes the volume that the
    agent is divided by. So a circuit volume doubled between two steps halves
    F_I and doubles the ratio. No interface control does that today, but a
    rule that holds only because a slider is missing is not one to rely on.
    So a crossing column above the ceiling is not drawn, and the stretch
    ends where it would have ended without the extension. The column is not
    clamped to the ceiling or interpolated onto it. It is simply a point
    outside what this plot can show.

    **A single polyline through every in-domain column would draw a straight
    line across the stretch it skipped.** That segment would join two real
    points through values the run never produced. It would be a synthesized
    trace, which this module never creates. A broken line asserts nothing
    about the gap.

    The stretches are computed from the drawn columns, not kept up to date as
    the run advances (`PL-2FM6`). Only the drawn columns are needed, so
    classifying all of them costs time in proportion to the frame rather than
    to the run. It also means that a boundary can fall only on an instant the
    chart actually plots. When a single extendable column separates two runs
    of anchors, both stretches extend to it. The column then appears once in
    each stretch, as its endpoint. That is the honest rendering of a run that
    left the domain and returned within one column, and it is the only case
    in which one column appears twice.

    Args:
        quotients: One entry per drawn column, `None` where the column has
            no quotient at all.
        extension_ceiling: The highest quotient that a crossing column may
            have and still extend a stretch.

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
    """Return whether the column at `column` is the crossing point to draw.

    `None` marks a column with no quotient at all, under `app/wash_in.py`'s
    rule 1: there is no agent in the circuit yet, so there is nothing to draw.
    Every other out-of-domain column crossed equilibrium, and it is drawn
    when it is close enough to stay on the plot. A column outside the window
    extends nothing. The bounds check returns that result rather than raising
    an error, because a stretch running to the edge of the frame simply has
    no crossing column on that side yet.
    """

    if not 0 <= column < len(quotients):
        return False

    quotient = quotients[column]

    return quotient is not None and quotient <= extension_ceiling


def percent_axis_ticks(
    top_percent: float, interval_percent: float
) -> tuple[tuple[float, str], ...]:
    """Label the compartment chart's percent axis at exactly its gridlines.

    The ruling and the labels describe one scale by construction, because
    both are multiples of `interval_percent`. So a reader who takes a value
    off the nearest rule takes it off a labelled one. The Flet chart left the
    axis to label itself, at a different interval from the rules it drew
    (`PL-Q4VH`). This function is the fix, carried over in the port.

    Args:
        top_percent: Top of the axis.
        interval_percent: Spacing of its horizontal rules.

    Returns:
        Ticks from zero upward, each as (percent position, label). The label
        is the position in its shortest exact decimal form. So an agent whose
        half-MAC is 0.575% is labelled `0.575`, rather than with a rounded
        value that sits off the gridline it labels.

    Raises:
        ValueError: If either argument is not strictly positive. An axis of
            no height or a rule spacing of zero would place every label
            somewhere meaningless rather than failing.
    """

    if not top_percent > 0.0:
        raise ValueError(f"top_percent must be strictly positive, got {top_percent!r}")

    if not interval_percent > 0.0:
        raise ValueError(f"interval_percent must be strictly positive, got {interval_percent!r}")

    count = floor(top_percent / interval_percent + _PERCENT_TICK_COUNT_TOLERANCE)

    return tuple(
        (index * interval_percent, f"{index * interval_percent:g}") for index in range(count + 1)
    )


def wash_in_axis_ticks() -> tuple[tuple[float, str], ...]:
    """Label the wash-in axis at its own gridlines, in its own resolution.

    Nothing about this axis depends on the agent or on the run. It is a
    dimensionless 0 to 1 under every setting, and that property is what makes
    the plot comparable across agents in the first place. The labels go
    through `format_wash_in_ratio`, so the axis that a value is read against
    and the reading printed beside the plot cannot be at two different
    resolutions. The ruling and the labels stop at equilibrium, which is
    where the readable scale ends. The axis itself extends higher, for the
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
    """Return the three-line hover readout for one drawn point of a compartment trace.

    `docs/MODEL.md` § "The chart's hover readout: what the tooltip may show"
    is the specification. The first line gives the run context, the second
    says what the value is, and the third gives the value in both units the
    chart uses. Every number goes through `app/formatting.py`, never through
    the chart library's own formatter. So each number appears at the
    resolution the readouts derive, with the below-resolution forms intact.
    The order carries the safety argument. The qualifiers come before the
    number, so a reader reaches the number through "modelled" and through
    the compartment it belongs to, rather than meeting them afterwards.

    Args:
        run: The run the point belongs to.
        quantity: The compartment the trace draws.
        index: Which drawn point, as a position in `run.times_s`.
        run_count: How many runs are on the chart. This function builds it
            as a `RunCount`, which checks it. The first line names the run
            only when more than one run is drawn. `_hover_context` explains
            why.

    Returns:
        The readout, three lines joined by newlines.

    Raises:
        KeyError: If `quantity` is not a compartment on this chart.
        IndexError: If `index` is outside the drawn points.
        TypeError: If `run_count` is not an `int` (`RunCount`).
        ValueError: If `run_count` is less than one (`RunCount`).
    """

    return "\n".join(
        (
            _hover_context(run, run.times_s[index], RunCount(run_count)),
            _hover_subject(quantity),
            _hover_value(run, quantity, index),
        )
    )


def format_wash_in_hover(run: RunFrame, stretch: WashInStretch, index: int, run_count: int) -> str:
    """Return the three-line hover readout for one drawn point of the wash-in trace.

    It has the same form as `format_trace_hover`, in the ratio's own units.
    F_A/F_I is dimensionless and has neither a percent nor a MAC reading, so
    the third line is `format_wash_in_ratio`'s number alone. At a column past
    equilibrium the third line says so instead of printing a quotient above 1
    (`WASH_IN_HOVER_PAST_EQUILIBRIUM_TEXT`).

    Args:
        run: The run the stretch belongs to.
        stretch: The stretch the point is on.
        index: Which drawn point, as a position in `stretch.times_s`.
        run_count: How many runs are on the chart, taken as
            `format_trace_hover` takes it and for the same reason.

    Returns:
        The readout, three lines joined by newlines.

    Raises:
        IndexError: If `index` is outside the stretch's points.
        TypeError: If `run_count` is not an `int` (`RunCount`).
        ValueError: If `run_count` is less than one (`RunCount`).
    """

    return "\n".join(
        (
            _hover_context(run, stretch.times_s[index], RunCount(run_count)),
            WASH_IN_HOVER_LABEL,
            _wash_in_hover_value(stretch.ratios[index]),
        )
    )


def _wash_in_hover_value(ratio: float) -> str:
    """Return the ratio as the hover prints it, or a notice where it is not wash-in.

    The stretch's crossing column, where the trace passes equilibrium, has a quotient
    above 1. That is elimination rather than wash-in, so no number is printed for it
    (`PL-YH6Z`).
    """

    if not is_wash_in(ratio):
        return WASH_IN_HOVER_PAST_EQUILIBRIUM_TEXT

    return format_wash_in_ratio(ratio)


def _hover_context(run: RunFrame, time_s: float, run_count: RunCount) -> str:
    """Return a hover's first line: the modelled marker, the agent, the run and the instant.

    The run is named while more than one run is drawn, and omitted while only
    one is (project owner, 2026-09-17, ratified, over giving the run a fourth
    line of its own and over leaving the curve's line width to show it).
    `docs/MODEL.md` § "The chart's hover readout" -> "The hover and the run it
    belongs to" is the derivation. In short, this is the line that the
    specification already calls *run context*. While two runs are compared,
    the run is the only token on this line that tells them apart.
    `assemble_chart_frame` rejects a frame whose runs differ on agent, so the
    agent is the same for every run here.

    The run name is conditional for the same reason the width channel is
    (`run_trace_style`). A single run has nothing to be told apart from, and
    a name on the only run drawn implies a comparison that is not on screen.
    The condition is not a hidden mode, because a second run also brings a
    second legend entry and a second named value in each readout panel.

    Args:
        run: The run the point belongs to.
        time_s: The point's simulated time.
        run_count: How many runs are on the chart.

    Returns:
        The run-context line: three tokens while one run is drawn, four while
        more than one is.
    """

    tokens = [_hover_agent(run)]

    if run_count > 1:
        tokens.append(run.label)

    tokens.append(_hover_instant(time_s))

    return _HOVER_CONTEXT_SEPARATOR.join(tokens)


def format_compared_trace_hover(
    answering: Sequence[tuple[RunFrame, RecordedQuantity, int]], run_count: int
) -> str:
    """Return what a hover shows where more than one drawn point is within the pointer's reach.

    `docs/MODEL.md` § "The chart's hover readout" -> "Where more than one
    trace answers" is the specification, and `PL-JVHL` is why there is one.
    With the three-line form, the run a reader was shown depended on which
    drawn point was marginally nearer, so a 2 px hand movement could swap it
    silently. Instead, every run inside the radius is reported, and the box
    has a value line for each run. `PL-0RZ0` extended that rule to the
    compartment, because the same axis compression leaves compartments
    competing for the pointer just as often.

    **There are two forms, and the first is exactly what it always was.** When
    every reading is of one compartment, the form is the three-line one with
    its third line repeated: the modelled marker and the agent, then the
    compartment, then one line per run. `PL-0RZ0` measured this case at
    54.3-99.5% of hovers. When the readings span compartments, one heading
    cannot stand for them all, so the heading is dropped. Each value line
    then opens with its own compartment, followed by its run while more than
    one run is drawn. In both forms the qualifiers still come before the
    numbers, which is the safety argument that the order carries.

    **The instant is stated on each line rather than once for the box.**
    Every compartment of one run is read at one instant
    (`nearest_trace_point`, `PL-1K9G`), but two runs need not be. Each run
    draws the columns its own control events fall on
    (`SimulationController.drawn_window`), and a branch draws none before its
    fork. So the instants nearest one pointer can differ between runs. Where
    both runs are drawn, they can differ by up to a grid column: 4 s on the
    60-minute axis and 48 s on the 12-hour one, and `format_elapsed` shows
    both. A single instant above a column of values would assert a
    simultaneity that the readings do not have. `CLAUDE.md`'s safety-critical
    standard counts that as a failure of the value rather than of its
    presentation.

    Args:
        answering: Every drawn point within reach, in the frame's own drawing
            order: compartment by `ChartFrame.visible`, then run by
            `ChartFrame.runs`. Each comes with the compartment its trace draws
            and the position of the reported point in the run's `times_s`.
            The points are ordered by the frame rather than by distance, so
            that nothing about the box moves with a hand movement too small to
            aim with. That is the whole point of `PL-JVHL` and `PL-0RZ0`.
        run_count: How many runs the chart draws. The value lines name the
            run while more than one is drawn, by `_hover_context`'s rule and
            for its reason. This is the chart's count rather than the count of
            runs in reach, because a run that is drawn but out of reach is
            still a run the reader can see.

    Returns:
        The readout: the agent, then the compartment where one is shared, then
        one line per reading, joined by newlines.

    Raises:
        KeyError: If a quantity is not a compartment on this chart.
        IndexError: If an index is outside its run's drawn points.
        TypeError: If `run_count` is not an `int` (`RunCount`).
        ValueError: If no reading is given, if `run_count` is less than one
            (`RunCount`), or if the runs are not all on one agent. The agent
            is named once, above the values, because `assemble_chart_frame`
            rejects a frame whose runs differ on agent. Naming one run's agent
            over another run's concentration would be the correct number under
            the wrong label.
    """

    if not answering:
        raise ValueError("a hover is answered for at least one drawn point; none was given")

    count = RunCount(run_count)

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
                _hover_contended_value(run, quantity, index, count)
                for run, quantity, index in answering
            ),
        )
    )


def format_compared_wash_in_hover(answering: Sequence[tuple[RunFrame, WashInStretch, int]]) -> str:
    """Return `format_compared_trace_hover`'s readout for the wash-in plot, in the ratio's units.

    It has the same form for the same reasons, with `format_wash_in_hover`'s
    third line in place of the compartment's. F_A/F_I is dimensionless and has
    neither a percent nor a MAC reading.

    Args:
        answering: Every run within reach, in `ChartFrame.runs` order. Each
            comes with the stretch that its reported point is on, and the
            position of that point in the stretch's `times_s`.

    Returns:
        The readout, two lines plus one per run, joined by newlines.

    Raises:
        IndexError: If an index is outside its stretch's points.
        ValueError: If no run is given, or if the runs are not all on one
            agent. `format_compared_trace_hover` raises in these cases too,
            for the same reason.
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
                    run, stretch.times_s[index], _wash_in_hover_value(stretch.ratios[index])
                )
                for run, stretch, index in answering
            ),
        )
    )


def _hover_agent(run: RunFrame) -> str:
    """Return the modelled marker and the agent, which every hover form opens with."""

    return f"{_HOVER_MODELLED_MARKER} {run.agent_display_name.lower()}"


def _hover_instant(time_s: float) -> str:
    """Return a drawn point's instant, formatted the way the clock and the axis show time.

    Every drawn instant is a whole multiple of `HOVER_INSTANT_RESOLUTION_S`. So the
    rounding removes only floating-point noise, and the printed instant is the one
    whose state the hover prints.
    """

    return format_elapsed(round(time_s / HOVER_INSTANT_RESOLUTION_S) * HOVER_INSTANT_RESOLUTION_S)


def _hover_subject(quantity: RecordedQuantity) -> str:
    """Return what the value is: the compartment, with its gloss where the readout row has one."""

    style = trace_style(quantity)

    return style.label if style.gloss is None else f"{style.label} ({style.gloss})"


def _hover_value(run: RunFrame, quantity: RecordedQuantity, index: int) -> str:
    """Return one drawn point's value in both units the chart uses.

    This is the one place where either hover form produces a compartment
    number. So a hover reporting one run and a hover reporting three cannot
    format the same state differently. The MAC multiple is computed from this
    run's own `mac_percent`, exactly as the MAC axis and the readout row are.
    """

    fraction = run.fractions[quantity][index]

    return f"{format_percent(fraction)}   {format_mac_multiple(fraction, run.mac_percent)}"


def _hover_compared_value(run: RunFrame, time_s: float, value: str) -> str:
    """Return one run's line of a compared readout: whose value it is, when, and what it is."""

    context = _HOVER_CONTEXT_SEPARATOR.join((run.label, _hover_instant(time_s)))

    return f"{context}   {value}"


def _hover_contended_value(
    run: RunFrame, quantity: RecordedQuantity, index: int, run_count: RunCount
) -> str:
    """Return one line of a readout whose pointer is within reach of more than one compartment.

    The compartment comes first, because the heading named it while the
    readings shared one compartment. A value line that did not name it would leave the
    reader to infer which trace it came from, and `PL-0RZ0` found that a 2 px
    hand movement made that inference wrong. The line keeps the gloss that
    `_hover_subject` gives the compartment. `docs/MODEL.md` requires that
    hedge wherever the compartment is named, and a form that dropped it to
    stay narrow would be trading a required qualifier for a column of
    whitespace.

    The run follows while more than one run is drawn, and is omitted while
    only one is. This is `_hover_context`'s rule, not a second one: a name on
    the only run drawn implies a comparison that is not on screen.
    """

    tokens = [_hover_subject(quantity)]

    if run_count > 1:
        tokens.append(run.label)

    tokens.append(_hover_instant(run.times_s[index]))

    return f"{_HOVER_CONTEXT_SEPARATOR.join(tokens)}   {_hover_value(run, quantity, index)}"


@dataclass(frozen=True, slots=True)
class HoverReading:
    """One drawn point that a hover reports: whose it is, what it is, and where.

    Attributes:
        run: Which run, as a position in `ChartFrame.runs`.
        quantity: Which trace the point is on: a compartment, or
            `RecordedQuantity.WASH_IN_RATIO` on the wash-in plot. It is stored
            on each reading rather than once for the box. More than one
            compartment is reported where two compressed traces lie within
            one radius of each other, and a value whose trace the reader has
            to infer is the failure that `PL-0RZ0` fixes.
        time_s: The point's simulated time. It is the run's drawn instant
            nearest the pointer in time, and every reading of one run shares
            it (`PL-1K9G`). Two runs can still differ here. Each run also
            draws the columns its own control events fall on, and a branch
            draws none before its fork. That is why the readout states the
            instant on each reading rather than once for the box.
        value: The point's height in the plot's own unit: percent on the
            compartment chart, and the dimensionless ratio on the wash-in
            plot.
    """

    run: int
    quantity: RecordedQuantity
    time_s: float
    value: float


@dataclass(frozen=True, slots=True)
class HoverTarget:
    """Every drawn point within the pointer's reach, and what the hover says about them.

    **Every run inside the radius is reported, not just the nearest one**
    (project owner, 2026-09-19, ratified, over breaking the tie toward the
    trunk and over waiting for the axis-compression fix). `PL-JVHL` measured
    the alternatives. With two runs on one axis, the two runs' points for a
    slow compartment are inside the 12 px radius over almost the whole
    hoverable band. Keeping only the single nearest point let a 2 px hand
    movement swap which run's value was read. That happened silently, on
    75.4-99.9% of the fat axis. Two other rules were measured, and neither
    changed anything: preferring the curve nearest along its length, and
    requiring the pointer to be inside a run's own band. Reporting every run
    was the only rule that brought the swap rate to zero, because nothing
    then depends on which point is marginally nearer.

    **Every compartment inside the radius is reported too, by the same rule**
    (project owner, 2026-09-20, ratified, over recording the measurement and
    leaving the flip to the axis fix, `PL-QYBW`). The run rule above still let
    distance decide which *compartment* was reported, on the reasoning that a
    reader aims at a curve. `PL-0RZ0` measured what the same axis compression
    does to that reasoning. Two or more compartments are inside the radius
    over 15.2-45.7% of the hoverable area on the two-run chart, and over
    37.0% on the single-run chart. A 2 px move changed which compartment was
    reported on 6.6-13.6% of contended pointer pairs. On 99.9% of those pairs
    it printed a different number, differing by a median of 17.1-17.9x for
    muscle against fat. The box does not move when this happens, because the
    two winning points are a median of 0.9 px apart. Only the words and the
    numbers change. At that separation there is no aim to respect, which is
    `PL-QYBW`'s own second consequence. So a rule that picked one compartment
    would be picking arbitrarily rather than honouring the reader's aim.

    Attributes:
        quantities: Every trace within reach, in the frame's drawing order,
            and never empty. These are compartments, or
            `RecordedQuantity.WASH_IN_RATIO` alone on the wash-in plot, which
            draws one trace and so has no compartments for distance to choose
            between.
        readings: One per run and compartment within reach, in the frame's own
            drawing order (compartment by `ChartFrame.visible`, then run by
            `ChartFrame.runs`), and never empty. They are ordered by the frame
            rather than by distance, so that no part of the readout moves with
            a hand movement too small to aim with.
        readout: The text to show: the three-line form while one point is
            reported, and `format_compared_trace_hover`'s form while more than
            one is.
    """

    quantities: tuple[RecordedQuantity, ...]
    readings: tuple[HoverReading, ...]
    readout: str

    @property
    def anchor(self) -> HoverReading:
        """Return the reading the box is anchored to: the first in the frame's drawing order.

        The anchor is chosen by position rather than by value, and by drawing
        order for the same reason that `readings` is ordered that way. A box
        anchored to whichever point was nearest would jump with a movement
        too small to aim with. That would be the defect this class exists to
        remove, showing up in its layout instead.
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
    """Return the drawn compartment points, at the instant the pointer names, that are in reach.

    Distance is measured in pixels rather than in axis units. The two axes
    are in different units, and a reader's hand works in neither. A tolerance
    stated in seconds would be a hair at the 12-hour base and a whole window
    at the one-minute one. The caller supplies the scale of the view it is
    drawing.

    **The pointer's position along the time axis names the instant, and
    distance decides only what is in reach** (`PL-1K9G`). Each run is read at
    its drawn instant nearest the pointer in time, and a tie goes to the
    earlier instant. Every compartment of that run whose point at that
    instant is inside the radius is reported. So every compartment of one
    run is reported at one instant. A hand movement up or down the percent
    axis can change what is in reach, but never the instant a value is
    labelled with. The earlier rule took each trace's nearest point in both
    dimensions instead, which let the pointer's height choose the column on
    a sloped trace. On the single-run chart, 70.1% of the boxes that held two
    or more of one run's readings showed two instants. Those instants were up
    to 72 s apart on the 60-minute axis and fifteen minutes apart on the
    12-hour one. The radius is measured to the point at the named instant,
    not to the nearest of the trace's points. So every value reported is at
    that instant *and* within reach of the pointer. The cost is that a reader
    must aim more carefully beside a steep segment, but no drawn instant
    becomes unreachable. `docs/MODEL.md` § "Where more than one trace
    answers" has the measurement.

    **Distance does not decide between traces either.** Every run and every
    compartment whose point is inside the radius is reported. So no hand
    movement can change which of them the box reports without also changing
    what is in reach. `HoverTarget` explains why, `PL-JVHL` has the run
    measurements, and `PL-0RZ0` has the compartment ones.

    Only the compartments that the frame draws are candidates, so a hidden
    trace is never reported. Only the six compartments are candidates at
    all. The clinical references and the control marks are not drawn points
    and are never reported, for the interaction reason that `docs/MODEL.md`
    § "The chart's hover readout" gives. Every candidate is a point that the
    plot actually draws, so the readout reports a state of the run, never a
    position between two states.

    Args:
        frame: The frame on the plot.
        time_s: The pointer's position along the time axis.
        percent: The pointer's position on the percent axis.
        seconds_per_pixel: The time axis's scale.
        percent_per_pixel: The percent axis's scale.
        radius_pixels: How far, in pixels, a point may be from the pointer
            and still be reported.

    Returns:
        Every run's and compartment's drawn point at the named instant that
        is within the radius, or `None` when no point is that close.
    """

    columns = [_nearest_column(run.times_s, time_s) for run in frame.runs]
    answering: list[tuple[int, RunFrame, RecordedQuantity, int]] = []

    # Loop in the frame's own drawing order: compartment by the trace table,
    # then run by the chart. The readout's lines are ordered that way, and a
    # readout whose lines could reorder under the pointer would show this same
    # defect in its layout.
    for quantity in frame.visible:
        for run_index, (run, column) in enumerate(zip(frame.runs, columns, strict=True)):
            if column is None:
                continue

            distance = _pixel_distance(
                time_s,
                percent,
                run.times_s[column],
                percent_from_fraction(run.fractions[quantity][column]),
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
                value=percent_from_fraction(run.fractions[quantity][column]),
            )
            for run_index, run, quantity, column in answering
        ),
        readout=(
            format_trace_hover(first_run, first_quantity, first_column, frame.run_count)
            if len(answering) == 1
            else format_compared_trace_hover(
                [(run, quantity, column) for _, run, quantity, column in answering], frame.run_count
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
    """Return the drawn wash-in points, at the instant the pointer names, that are in reach.

    This is `nearest_trace_point` for the wash-in plot, with the same rules.
    The pointer names the instant. Each run is read at its drawn wash-in
    instant nearest the pointer in time, if that point is inside the radius,
    and every run in reach is reported. A run's stretches form one set of
    drawn instants, with gaps where the ratio left its domain. So the instant
    named across a gap is the nearer end of either stretch. The plot has one
    trace rather than six, so there are no compartments for distance to
    choose between. But the retired two-dimensional distance still let a
    vertical 2 px movement shift the one instant this function reports, on
    23.9-44.4% of such movements (`PL-1K9G`). The equilibrium line and the
    control marks are not candidates.

    Args:
        frame: The frame on the plot.
        time_s: The pointer's position along the time axis.
        ratio: The pointer's position on the ratio axis.
        seconds_per_pixel: The time axis's scale.
        ratio_per_pixel: The ratio axis's scale.
        radius_pixels: How far, in pixels, a point may be from the pointer
            and still be reported.

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

    first_run, first_stretch, first_column = answering[0][1:]

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
            format_wash_in_hover(first_run, first_stretch, first_column, frame.run_count)
            if len(answering) == 1
            else format_compared_wash_in_hover(
                [(run, stretch, column) for _, run, stretch, column in answering]
            )
        ),
    )


def _nearest_column(times_s: Sequence[float], time_s: float) -> int | None:
    """Return the drawn column nearest `time_s` in time, or `None` where nothing is drawn.

    The instants are ascending, so this is one bisection rather than a scan
    of the run. Otherwise, a pointer moving at sixty events a second over two
    runs would cost a comparison per drawn point per event. A tie goes to the
    earlier column, so the result depends only on the instant, not on which
    neighbour a search happened to reach first.
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
    """Return a run's drawn wash-in point nearest `time_s` in time, across all its stretches.

    A tie goes to the earlier stretch, as a tie goes to the earlier column
    within one stretch. So a column drawn twice, as the shared end of two
    stretches, is read from the earlier stretch.
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
