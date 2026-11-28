"""The concentration chart and the wash-in plot, drawn with pyqtgraph.

This module is the toolkit half of the chart. `app/chart_frame.py` decides,
without any toolkit, everything a frame claims: which compartment a curve
shows, where the references are drawn, which instants are drawn, and what a
hover says. This module only moves pyqtgraph items to match a `ChartFrame`.
Nothing here reads simulation state, formats a value, or decides a
coordinate. If a widget computed a number that a reader interprets, that
clinical value would fall outside the coverage of
`tests/unit/test_chart_frame.py`, which is where those claims are tested.

**Items are moved, never rebuilt.** Every curve, mark and reference is built
once and then updated on each frame. The Flet chart reused its point
controls for the same reason (`PL-010`). A frame then costs what it draws
rather than what it constructs. The items are kept in pools of fixed size,
and `chart_frame` states the sizes: a fixed number of control marks and a
fixed number of wash-in stretches. An unused member of a pool is hidden,
which costs nothing per frame.

**Both axes have gridlines exactly where they have labels, by construction.**
Each axis is given its ticks explicitly, from the frame, and the gridlines
are drawn at the same ticks that the axis is labelled at. So the gridlines and
the labels cannot describe two different scales (`PL-Q4VH`).

**The hover shows a readout whenever the pointer is over a drawn point,
whether the run is playing or paused** (`docs/INTERFACE.md` § "The chart's hover
readout: what the tooltip may show"). The readout is for the plot's *drawn
points*, which are the states that the run stored for the drawn seconds. It
is never for a position between two of them. Its text is the text that `chart_frame`
produces through `app/formatting.py`, and never the text of the chart
library's coordinate formatter. The hover's cost grows with pointer events,
not with the number of points. So the chart needs no mode that turns the
hover off, and no caption to explain such a mode. The hover is not a
pyqtgraph default, though. `pyqtgraph.ScatterPlotItem` ships with `hoverable`
off, and a plotted line has no hover at all, so this module builds the hover
rather than inheriting it (`PL-YVHK`).

**Points reach pyqtgraph by its documented fast path.** Every curve and dot is
handed `numpy.ndarray`s of `float64`, as pyqtgraph's performance guidance asks,
and every curve is drawn with `skipFiniteCheck`. That flag is safe only because
`ChartFrame` guarantees that every coordinate is finite (`app/chart_frame.py`,
`PL-TCNT`). `_plot_coordinates` is the one place that builds those arrays, and
`_draw_curve` is the one place that sets that flag.

**Every colour comes from `app/theme.py`.** This module declares no colour of
its own, so the palette that `tools/contrast_check.py` measures stays the
palette that is drawn.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from html import escape
from math import ceil
from typing import Any, Final, cast

import numpy as np
import pyqtgraph as pg
from numpy.typing import NDArray
from PySide6.QtCore import (
    QEvent,
    QObject,
    QPointF,
    QRectF,
    QSize,
    Qt,
    QTimer,
    Signal,
    SignalInstance,
)
from PySide6.QtGui import (
    QAccessible,
    QAccessibleEvent,
    QBrush,
    QColor,
    QFontMetrics,
    QImage,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPen,
)
from PySide6.QtWidgets import (
    QAccessibleWidget,
    QCheckBox,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from anesthesia_sim.app.chart_frame import (
    COMPARED_COMPARTMENT_CAP,
    COMPARTMENT_TRACES,
    MAX_CHART_CONTROL_MARKS,
    MAX_CHART_WASH_IN_SEGMENTS,
    WASH_IN_AXIS_MAXIMUM,
    WASH_IN_RATIO_NAME,
    ChartFrame,
    HoverTarget,
    RunCount,
    RunIndex,
    RunPreview,
    TraceStyle,
    nearest_trace_point,
    nearest_wash_in_point,
    preview_stroke_width,
    preview_trace_style,
    resample_owed,
    run_trace_style,
    trace_style,
    wash_in_axis_ticks,
)
from anesthesia_sim.app.chart_time_base import (
    FIT_RUN_KEY,
    SELECTABLE_TIME_BASES,
    ChartTimeBase,
    time_base_for_span,
)
from anesthesia_sim.app.compartment_selection import (
    INITIAL_COMPARTMENT_SELECTION,
    CompartmentSelection,
)
from anesthesia_sim.app.dashboard_frame import (
    BRANCH_POINT_LEGEND_LABEL,
    COMPARED_TRACE_LEGEND_CAPTION,
    CONTROL_MARK_LEGEND_LABEL,
    EQUILIBRIUM_LEGEND_LABEL,
    FIT_RUN_LABEL,
    MAC_AWAKE_BAND_LEGEND_NAME,
    MAC_AWAKE_BAND_LEGEND_TEMPLATE,
    MAX_DISPLAYED_RUNS,
    ONE_MAC_LINE_LEGEND_NAME,
    ONE_MAC_LINE_LEGEND_TEMPLATE,
    TIME_AXIS_TITLE,
    TIME_AXIS_TITLE_TEMPLATE,
    TRACE_TOGGLE_ACCESSIBLE_NAME_TEMPLATE,
    WASH_IN_TRACE_LEGEND_LABEL,
    compared_trace_legend_label,
    concentration_chart_description,
    concentration_chart_name,
    control_name,
    trace_legend_label,
)
from anesthesia_sim.app.display_units import DisplayUnit
from anesthesia_sim.app.formatting import ChartCeiling, format_chart_time_label, format_time_base
from anesthesia_sim.app.qt_widgets import (
    ClauseWrappingLabel,
    FlowLayout,
    SelectorComboBox,
    clause_lines,
    declare_interface_colours,
)
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.app.stylesheets import foreground_stylesheet, selector_stylesheet
from anesthesia_sim.app.theme import (
    BAND_SWATCH_HEIGHT,
    BAND_SWATCH_WIDTH,
    BRANCH_POINT_STROKE_WIDTH,
    CHART_CEILING_SELECTOR_WIDTH,
    CHART_HEIGHT,
    CHART_LEAST_HEIGHT,
    COMPARED_RUN_WIDTH_STEP,
    CONTROL_MARK_COLOR,
    CONTROL_MARK_DASH_PATTERN,
    CONTROL_MARK_STROKE_WIDTH,
    CONTROL_MARK_SWATCH_HEIGHT,
    CONTROL_MARK_SWATCH_WIDTH,
    EQUILIBRIUM_LINE_COLOR,
    EQUILIBRIUM_LINE_DASH_PATTERN,
    EQUILIBRIUM_LINE_STROKE_WIDTH,
    GRIDLINE,
    INK,
    LEGEND_ENTRY_SPACING,
    LEGEND_LINE_SPACING,
    LEGEND_SWATCH_HEIGHT,
    LEGEND_SWATCH_SPACING,
    LEGEND_SWATCH_WIDTH,
    MAC_AWAKE_BAND_COLOR,
    MAC_AWAKE_BAND_EDGE_STROKE_WIDTH,
    MAC_AWAKE_BAND_FILL_OPACITY,
    MUTED,
    ONE_MAC_LINE_COLOR,
    ONE_MAC_LINE_DASH_PATTERN,
    ONE_MAC_LINE_STROKE_WIDTH,
    PANEL,
    PREVIEW_REGION_COLOR,
    PREVIEW_REGION_EDGE_STROKE_WIDTH,
    PREVIEW_REGION_FILL_OPACITY,
    TIME_BASE_SELECTOR_WIDTH,
    WASH_IN_CHART_HEIGHT,
    WASH_IN_CHART_LEAST_HEIGHT,
    WASH_IN_COLOR,
    WASH_IN_STROKE_WIDTH,
)
from anesthesia_sim.app.wash_in import WASH_IN_EQUILIBRIUM_RATIO
from anesthesia_sim.core.units import MILLISECONDS_PER_SECOND

__all__ = [
    "BRANCH_POINT_LEGEND_LABEL",
    "CONTROL_MARK_LEGEND_LABEL",
    "EQUILIBRIUM_LEGEND_LABEL",
    "HOVER_RADIUS_PIXELS",
    "WASH_IN_TRACE_LEGEND_LABEL",
    "BandMark",
    "ConcentrationChart",
    "LegendMark",
    "TraceLegend",
    "WashInChart",
    "WashInLegend",
    "dashed_pen",
    "on_screen",
    "preview_trace_pen",
    "run_trace_pen",
    "trace_pen",
]

# How far, in pixels, the pointer may be from a drawn point and still get a
# readout. The radius is about a fingertip's width of cursor travel. It is
# wide enough that a reader aiming at a curve lands on it. It is narrow enough
# that a pointer resting in clear space between two traces reports neither of
# them, rather than whichever is nearer.
HOVER_RADIUS_PIXELS: Final = 12.0

# pyqtgraph's `InfiniteLine` takes its angle in degrees. An angle of 90 gives a
# vertical line, which marks a time. An angle of 0 gives a horizontal line, which
# marks a value. Every vertical line on both plots uses 90, whether it is a
# gridline, a control mark or a fork mark. Every horizontal line uses 0.
_VERTICAL_LINE_ANGLE_DEG: Final = 90
_HORIZONTAL_LINE_ANGLE_DEG: Final = 0


def _plot_coordinates(values: Sequence[float]) -> NDArray[np.float64]:
    """Return one axis of a frame's points as the array pyqtgraph draws from.

    pyqtgraph's `PlotDataItem` documentation, under "Performance", says to
    "use `numpy.ndarray` instead of python's built-in lists"
    (https://pyqtgraph.readthedocs.io/en/latest/api_reference/graphicsItems/plotdataitem.html).
    A list given to `setData` is copied into an array on every call anyway.
    The conversion changes no coordinate. A Python `float` and a numpy
    `float64` are both IEEE 754 doubles, so every coordinate is carried over
    bit for bit.
    """

    return np.fromiter(values, dtype=np.float64, count=len(values))


def _draw_curve(curve: Any, times_s: Sequence[float], values: Sequence[float]) -> None:
    """Hand one curve a frame's points, without pyqtgraph's per-frame finiteness check.

    By default `PlotCurveItem` scans every point for NaN and infinity each
    time it builds its path, so that it can leave gaps. Its documentation
    says that `skipFiniteCheck` "can speed up plotting by not checking and
    compensating for NaN values", and that non-finite data then gives
    unpredictable results
    (https://pyqtgraph.readthedocs.io/en/latest/api_reference/graphicsItems/plotcurveitem.html).
    Every point here comes from a `ChartFrame`, which cannot hold a
    non-finite coordinate. The frame checks each value where it is built
    and raises an error that names the value. The view then halts the run
    (`app/chart_frame.py`, `PL-TCNT`). So the scan could never find
    anything, and it is skipped.

    Args:
        curve: The `pyqtgraph.PlotCurveItem` to move.
        times_s: The drawn instants, in simulated seconds.
        values: One value per instant, in the unit of the curve's axis.
    """

    curve.setData(_plot_coordinates(times_s), _plot_coordinates(values), skipFiniteCheck=True)


# The dot on the last point of a wash-in stretch that stopped because it
# crossed equilibrium. A line that simply stops looks the same as a line that
# the frame cut off. This line stops while it is still climbing steeply, which
# is the shape that looks clipped. A terminal dot is the ordinary remedy in
# scientific plotting: it says that the series ends here rather than
# continuing out of view. The dot is seven pixels across, which matches the
# 3.5 px radius at which the Flet chart drew it.
_WASH_IN_TERMINUS_DIAMETER: Final = 7.0

# The dot the hover puts on the point it is reporting, so a reader can see
# which drawn state the text describes.
_HOVER_DOT_DIAMETER: Final = 8.0

# The most hover updates per second that a pointer moving over a plot can
# cause, whatever rate its device reports moves at. The first move is handled
# at once, and then the newest move at the end of each cooldown
# (`_PointerMoves`).
_HOVER_ANSWERS_PER_SECOND: Final = 60

# The most lines a hover box on each plot can hold, which sets the least
# height that holds it whole (`_HoverReadout.hold_the_tallest_box`). A
# concentration box names the agent and then gives one line per reading in
# reach. A single run gives a reading for each of the six compartments where
# all six start together. Compared runs give one for each run and each
# compartment drawn, at most `COMPARED_COMPARTMENT_CAP` of them.
# A wash-in box gives two lines and then one per run in reach
# (`chart_frame.format_compared_wash_in_hover`).
_TRACE_HOVER_MOST_LINES: Final = 1 + max(
    len(COMPARTMENT_TRACES), MAX_DISPLAYED_RUNS * COMPARED_COMPARTMENT_CAP
)
_WASH_IN_HOVER_MOST_LINES: Final = 2 + MAX_DISPLAYED_RUNS

# Drawing order. Control marks are drawn first, behind the references and
# behind every trace. A vertical line across the whole plot is the one
# annotation that can hide all six compartments at the moment a reader is
# trying to see what the change did to them. References come next, so every
# trace is drawn over them. A compartment hidden by a reference band would be
# the annotation hiding the run it annotates. The hover is drawn over
# everything.
_Z_GRIDLINE: Final = -50
_Z_CONTROL_MARK: Final = -30
_Z_REFERENCE_BAND: Final = -20
_Z_REFERENCE_LINE: Final = -10
_Z_PREVIEW_LABEL: Final = 5
_Z_HOVER: Final = 10


def trace_pen(style: TraceStyle) -> QPen:
    """The pen one compartment trace is drawn with, on the chart and in the legend.

    One constructor serves both, so the legend swatch is drawn in the trace's
    own pattern rather than as a solid bar standing for a dashed line
    (`PL-THXF`). A reader then compares a mark with a curve, rather than a
    phrase with a curve.

    Args:
        style: The trace.

    Returns:
        A pen in the trace's colour, width and dash pattern.
    """

    return dashed_pen(style.color, style.stroke_width, style.dash_pattern)


def dashed_pen(color: str, stroke_width: float, dash_pattern: Sequence[int] | None) -> QPen:
    """Return a pen whose dash pattern is given in display pixels.

    Qt states a dash pattern in units of the pen's width. `app/theme.py` and
    `chart_frame.COMPARTMENT_TRACES` state theirs in pixels, which is the unit
    that `docs/INTERFACE.md` § "The six compartment traces" tabulates. So the
    conversion is made once, here, rather than at each of the seven pens that
    have a pattern. A pattern copied across without the conversion draws every
    dash too long by a factor of the pen's width, which is what the spike did.

    A dashed pen also gets a flat cap. Qt's default square cap extends every
    dash by half the pen's width at each end. So a 3 px pen with a 10/4 pattern
    paints 13 px on and 1 px off, and the dashed compartment traces look almost
    solid. The dash is the only thing that tells some compartments apart for a
    reader with a colour-vision deficiency (`PL-88MK`). `pg.mkPen` sets a round
    cap only on pens wider than 4 px, so on these pens it leaves Qt's default
    square cap in place.

    Args:
        color: Hexadecimal line colour.
        stroke_width: Line width in display pixels.
        dash_pattern: Alternating dash and gap lengths in display pixels,
            or `None` for a solid line.

    Returns:
        The pen.
    """

    pen: QPen = pg.mkPen(color, width=stroke_width)

    if dash_pattern is not None:
        pen.setDashPattern([length / stroke_width for length in dash_pattern])
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)

    return pen


def on_screen(pen: QPen, device_pixel_ratio: float) -> QPen:
    """Return a copy of a chart pen that draws at its width on a screen of this pixel ratio.

    Every width and dash length in this module is in device-independent
    pixels, the unit that `docs/INTERFACE.md` tabulates and that Qt lays out
    every widget in. Every pen here is cosmetic, because the curves are drawn
    in data coordinates whose two axes scale differently. Qt draws a cosmetic
    pen's width in device pixels, after the scaling to the screen. So on a
    screen at 200% a 3 px pen drew 1.5 px wide, and at 125% it drew 2.4 px
    wide. Multiplying the width by the device pixel ratio undoes that. Qt
    states a dash pattern in units of the pen's width, so the dashes scale
    with it.

    This is the one place that conversion is made. `_ScreenPens` applies it to
    every chart item, and the legend swatches apply it when they paint.

    A non-cosmetic pen is returned unchanged, because Qt already scales its
    width to the screen, and multiplying it here would draw it too wide.

    Args:
        pen: The pen as specified, in device-independent pixels.
        device_pixel_ratio: Device pixels per device-independent pixel on the
            screen the pen will draw on, such as 1.0, 1.25 or 2.0.

    Returns:
        A copy of the pen, with a cosmetic pen's width in device pixels.

    Raises:
        ValueError: If the ratio is not a finite number above zero.
    """

    if not np.isfinite(device_pixel_ratio) or device_pixel_ratio <= 0:
        raise ValueError(
            f"a device pixel ratio is a finite number above zero, not {device_pixel_ratio}"
        )

    drawn = QPen(pen)

    if not pen.isCosmetic():
        return drawn

    drawn.setWidthF(pen.widthF() * device_pixel_ratio)

    return drawn


def _set_drawn_pen(item: Any, pen: QPen) -> None:
    """Give one pyqtgraph item a pen, through whichever setter its type has.

    An axis's `setPen` also sets its title's colour to the pen's colour, and the
    title is drawn in `MUTED` while the axis line is drawn in `GRIDLINE`. So the
    title's style is put back after the pen is set.
    """

    if isinstance(item, pg.LinearRegionItem):
        for line in item.lines:
            line.setPen(pen)
    elif isinstance(item, pg.TextItem):
        item.border = pen
        item.update()
    elif isinstance(item, pg.AxisItem):
        title_style = dict(item.labelStyle)
        item.setPen(pen)
        item.labelStyle = title_style
        item._updateLabel()  # pyqtgraph's own refresh of the title, as setLabel calls it.
    else:
        item.setPen(pen)


class _ScreenPens(QObject):
    """Every line pen of one plot, drawn at its specified width on the screen the plot is on.

    An item is given its pen through `hold`, which keeps the pen as specified
    and gives the item `on_screen`'s copy for the widget's current device pixel
    ratio. When the window moves to a screen with another ratio, Qt sends each
    widget a `DevicePixelRatioChange` event, and every held item is given its
    pen again at the new ratio. The ratio is read again when the widget is
    shown, because a widget built before `main()` places its window can be
    shown on a screen other than the one it was built for.

    Items here are built once and moved, never rebuilt, so the record grows
    only while a plot builds items for a new run.
    """

    def __init__(self, widget: QWidget) -> None:
        super().__init__(widget)
        self._widget = widget
        self._ratio = widget.devicePixelRatioF()
        self._held: dict[int, tuple[Any, QPen]] = {}
        widget.installEventFilter(self)

    def hold(self, item: Any, pen: QPen) -> None:
        """Draw this item with this pen, given in device-independent pixels, on every screen."""

        self._held[id(item)] = (item, QPen(pen))
        _set_drawn_pen(item, on_screen(pen, self._ratio))

    def specified(self, item: Any) -> QPen:
        """The pen this item was given, in device-independent pixels.

        Raises:
            KeyError: If the item was never given a pen through `hold`.
        """

        return QPen(self._held[id(item)][1])

    def holds(self, item: Any) -> bool:
        """Whether this item's pen is kept at its width on every screen."""

        return id(item) in self._held

    @property
    def device_pixel_ratio(self) -> float:
        """The ratio the held items' pens were last drawn for."""

        return self._ratio

    def follow_screen(self) -> None:
        """Draw every held pen again if the widget's device pixel ratio has changed."""

        ratio = self._widget.devicePixelRatioF()

        if ratio == self._ratio:
            return

        self._ratio = ratio

        for item, pen in self._held.values():
            _set_drawn_pen(item, on_screen(pen, ratio))

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # Qt spells this in camelCase.
        if watched is self._widget and event.type() in (
            QEvent.Type.DevicePixelRatioChange,
            QEvent.Type.Show,
        ):
            self.follow_screen()

        return False


def run_trace_pen(quantity: RecordedQuantity, run_index: RunIndex, run_count: RunCount) -> QPen:
    """The pen one run draws a compartment with, on the chart and in the legend.

    `chart_frame.run_trace_style` decides the pen, and this function only
    builds it. So the width that tells runs apart is settled once, without a
    toolkit, where `tests/unit/test_chart_frame.py` can test it.

    Args:
        quantity: Which compartment.
        run_index: Which run, as a position in the frame's runs.
        run_count: How many runs are on the chart.

    Returns:
        The pen, in the compartment's colour and dash pattern at the run's
        width.
    """

    return trace_pen(run_trace_style(quantity, run_index, run_count))


def preview_trace_pen(quantity: RecordedQuantity, run_index: RunIndex, run_count: RunCount) -> QPen:
    """Return the pen for one run's preview of a compartment (`chart_frame.preview_trace_style`).

    Args:
        quantity: Which compartment.
        run_index: Which run, as a position in the frame's runs.
        run_count: How many runs are on the chart.

    Returns:
        The pen, in the compartment's colour and dash pattern at the preview's
        width.
    """

    return trace_pen(preview_trace_style(quantity, run_index, run_count))


def _branch_point_pen() -> QPen:
    """The pen for a fork mark, which is vertical and solid where a control mark is dashed.

    Both marks name an instant and both are vertical. So the dash pattern and
    the words in the legend are what separate them. Those are two channels,
    and neither of them is colour. The pen reuses the control mark's colour on
    purpose rather than declaring a new one. That colour has already been
    measured against the panel, and a mark that a reader must not take for a
    control change should not depend on a hue at all.
    """

    pen: QPen = pg.mkPen(CONTROL_MARK_COLOR, width=BRANCH_POINT_STROKE_WIDTH)

    return pen


#: The position and the count of the one run that a plot draws when it is
#: not comparing runs. `_wash_in_pen` uses them as its defaults for that run.
_LONE_RUN_INDEX: Final = RunIndex(0)
_LONE_RUN_COUNT: Final = RunCount(1)


def _wash_in_pen(
    run_index: RunIndex = _LONE_RUN_INDEX, run_count: RunCount = _LONE_RUN_COUNT
) -> QPen:
    """The pen one run's F_A/F_I trace is drawn with, on the plot and in its legend.

    One constructor for both, as `trace_pen` is for the compartments, so the
    legend swatch cannot describe a line the plot is not drawing.

    **The width that tells runs apart applies to this plot too.** This plot
    draws one trace per run, in one colour and one dash pattern. So two runs
    here are not merely hard to tell apart: they are identical except for
    their values. That is the failure that the compartment chart's cap and
    width levels exist to prevent. The same width step separates the runs
    here. The same run is the wider one, for the same reason as on that
    chart: the two ratios also coincide exactly before the fork.

    Args:
        run_index: Which run, as a position in the frame's runs.
        run_count: How many runs are on the plot.

    Returns:
        The pen.

    Raises:
        ValueError: If `run_index` does not address one of `run_count` runs.
    """

    return dashed_pen(WASH_IN_COLOR, _wash_in_width(run_index, run_count), None)


def _wash_in_preview_pen(run_index: RunIndex, run_count: RunCount) -> QPen:
    """Return the pen for one run's predicted F_A/F_I, thinner than any run's own.

    The width is based on the width used when only one run is drawn, for the
    reason that `chart_frame.preview_trace_style` gives. In compare mode, a
    preview must not be wider than the other run's real trace inside its
    region.

    Raises:
        ValueError: As `_wash_in_pen`.
    """

    _wash_in_width(run_index, run_count)

    return dashed_pen(
        WASH_IN_COLOR, preview_stroke_width(_wash_in_width(_LONE_RUN_INDEX, _LONE_RUN_COUNT)), None
    )


def _wash_in_width(run_index: RunIndex, run_count: RunCount) -> float:
    """The width one run's F_A/F_I trace is drawn at, in display pixels.

    Raises:
        ValueError: If `run_index` does not address one of `run_count` runs.
    """

    if run_index >= run_count:
        raise ValueError(
            f"run {run_index} is not one of the {run_count} runs on the plot; a trace "
            "is drawn at the width of a run that is being drawn"
        )

    widened = run_count > 1 and run_index == 0

    return WASH_IN_STROKE_WIDTH + (COMPARED_RUN_WIDTH_STEP if widened else 0)


def _control_mark_pen() -> QPen:
    """The pen every control mark is drawn with, on both plots and in both legends."""

    return dashed_pen(CONTROL_MARK_COLOR, CONTROL_MARK_STROKE_WIDTH, CONTROL_MARK_DASH_PATTERN)


def _plot(background: str) -> tuple[Any, _ScreenPens]:
    """One plot widget, and the record of its line pens, with the furniture every plot shares.

    Every line the plot draws is given its pen through the returned
    `_ScreenPens`, so that each line keeps its specified width on any screen.

    A reader cannot pan, zoom or open a menu on the plot. The time base sets
    the window and the axis sets the range. A plot that a reader could drag
    off its labelled range would show a slope that meant something different
    from the slope on the plot beside it.

    So no key does anything on the plot either, and the plot is not a Tab
    stop. A keyboard user would otherwise land on it and see nothing happen
    (`PL-63FQ`).
    """

    plot = pg.PlotWidget(background=background)
    pens = _ScreenPens(plot)
    plot.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    plot.viewport().setFocusPolicy(Qt.FocusPolicy.NoFocus)
    item = plot.getPlotItem()
    item.setMenuEnabled(False)
    item.hideButtons()
    item.setMouseEnabled(x=False, y=False)
    item.disableAutoRange()

    # Axis lines are drawn in the gridline colour, and labels in the
    # interface's label colour, which `tools/contrast_check.py` measures as
    # text. pyqtgraph's own grid is deliberately left off. The axis item
    # paints that grid *over* the plot. At full opacity, a gridline erases the
    # pixel row of every trace and reference it crosses. This was measured on
    # 2026-09-14, when the 1 MAC line vanished under the 2% gridline it sits
    # on. At partial opacity, the grid tints those traces and references
    # instead. So `_GridLines` draws the gridlines from underneath the plot,
    # at exactly the ticks at which each axis is labelled.
    for name in ("left", "bottom", "right"):
        axis = item.getAxis(name)
        pens.hold(axis, pg.mkPen(GRIDLINE))
        axis.setTextPen(pg.mkPen(MUTED))

    # Each axis's range ends at a labelled tick, and a label is centred on its
    # tick. With pyqtgraph's 1 px top margin, the top label's upper half fell
    # outside the widget and was cut off, so a "6" could read as a "0"
    # (`PL-571L`). Half a line of the plot's font above the plot keeps it whole.
    top_px = ceil(QFontMetrics(plot.font()).height() / 2)
    item.layout.setContentsMargins(1, max(1, top_px), 1, 1)

    return plot, pens


def _text_box_pen() -> QPen:
    """The pen that outlines the hover's text box and a preview's label."""

    pen: QPen = pg.mkPen(MUTED)

    return pen


def _hover_items() -> tuple[Any, Any]:
    """The dot and the text box that a hover shows, hidden until there is a readout.

    The box's outline is drawn with `_text_box_pen` as specified. The hover
    that shows the box gives it that pen again through its `_ScreenPens`, so it
    keeps its width on any screen.
    """

    dot = pg.ScatterPlotItem(size=_HOVER_DOT_DIAMETER, pen=None, brush=pg.mkBrush(INK))
    dot.setZValue(_Z_HOVER)
    dot.hide()
    text = pg.TextItem(color=INK, fill=pg.mkBrush(PANEL), border=_text_box_pen(), anchor=(0, 0))
    text.setZValue(_Z_HOVER)
    text.hide()

    return dot, text


class _GridLines:
    """The plot's gridlines, drawn under everything at the ticks its axes carry.

    The lines stand at ticks that an axis is labelled from: the time axis's,
    and on the compartment chart the MAC axis's. So the gridlines and the
    labels cannot describe two different scales (`PL-Q4VH`). The pools of
    lines grow to fit the widest window drawn, and they never shrink. An
    unused line is hidden.
    """

    def __init__(self, item: Any, pens: _ScreenPens) -> None:
        self._item = item
        self._pens = pens
        self._pen = pg.mkPen(GRIDLINE, width=1)
        self._vertical: list[Any] = []
        self._horizontal: list[Any] = []

    def place(self, x_ticks: Sequence[float], y_ticks: Sequence[float]) -> None:
        """Draw gridlines at these positions, and hide the rest of each pool."""

        self._rule(self._vertical, _VERTICAL_LINE_ANGLE_DEG, x_ticks)
        self._rule(self._horizontal, _HORIZONTAL_LINE_ANGLE_DEG, y_ticks)

    def _rule(self, pool: list[Any], angle: int, positions: Sequence[float]) -> None:
        while len(pool) < len(positions):
            line = pg.InfiniteLine(pos=0.0, angle=angle, movable=False)
            self._pens.hold(line, self._pen)
            line.setZValue(_Z_GRIDLINE)
            self._item.addItem(line, ignoreBounds=True)
            pool.append(line)

        _place_marks(pool, positions)

    def horizontal_positions(self) -> tuple[float, ...]:
        """Where the shown horizontal gridlines stand, in the value axis's units."""

        return tuple(float(line.value()) for line in self._horizontal if line.isVisible())


class _PointerMoves(QObject):
    """Where the pointer moves over one plot, in scene coordinates, at most sixty times a second.

    The moves are read from the plot's viewport, before pyqtgraph's scene sees
    them. The scene passes a move on only when 10 ms have passed since the
    last move it passed on, which is its `mouseRateLimit` of 100 a second as
    shipped. The scene drops the other moves and delivers nothing after them.
    So the move that a pointer stopped on could get no readout, and the box
    could keep the readout for a move or two earlier (`PL-TCR5`). This class
    delivers the first move at once. Of any moves that follow it inside the
    cooldown, it delivers the newest when the cooldown ends. A delivery starts
    the cooldown, and a move never restarts it. `pg.SignalProxy` restarts its
    timer on every signal. So moves less than a millisecond apart, as a 1 kHz
    mouse reports them, held back its delivery for as long as the pointer
    kept moving.

    **A pointer that leaves is delivered at once, as `None`** (`PL-LTKL`).
    Leaving the widget sends no move to it, only a `Leave` event. So a
    position kept from moves alone outlived the pointer. The box stayed up at
    the last point, and each later frame showed a readout for that point
    again. While a run played, each frame gave a new instant, so a modelled
    value climbed with the run for a pointer that had gone. The `Leave` event
    also drops any move still waiting out the cooldown. Otherwise that move
    would put the box back up when the cooldown ended.
    """

    # The payload is `object` because it is a `QPointF` or `None`. A signal
    # declared as `QPointF` does not reject `None`. Instead it delivers the
    # scene's origin in its place, with nothing but a line on standard error
    # to say so.
    moved = Signal(object)

    def __init__(self, plot: Any) -> None:
        super().__init__(plot)
        self._newest: QPointF | None = None
        self._cooldown = QTimer(self)
        self._cooldown.setSingleShot(True)
        self._cooldown.setInterval(ceil(MILLISECONDS_PER_SECOND / _HOVER_ANSWERS_PER_SECOND))
        self._cooldown.timeout.connect(self._deliver)
        plot.viewport().installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # Qt spells this in camelCase.
        if isinstance(event, QMouseEvent) and event.type() == QEvent.Type.MouseMove:
            view = cast(QGraphicsView, self.parent())
            self._newest = QPointF(view.mapToScene(event.position().toPoint()))

            if not self._cooldown.isActive():
                self._deliver()
        elif event.type() == QEvent.Type.Leave:
            # The cooldown is stopped as well as emptied, so a pointer that
            # comes back gets a readout on its first move.
            self._newest = None
            self._cooldown.stop()
            self.moved.emit(None)

        return False

    def _deliver(self) -> None:
        if self._newest is None:
            return

        position, self._newest = self._newest, None
        self._cooldown.start()
        self.moved.emit(position)


class _HoverReadout:
    """The hover's mechanics, shared by both plots.

    It keeps the last pointer position, so a frame drawn under a resting
    pointer shows a fresh readout rather than going blank. At high playback
    speed the reported value moves as the run does. `docs/INTERFACE.md` § "When
    the hover readout appears" says that this is correct, not a defect to
    design around. It keeps `None` once the pointer has left the plot, so a frame drawn after
    that shows no readout (`PL-LTKL`).
    """

    def __init__(self, plot: Any, pens: _ScreenPens, least_height_px: int, most_lines: int) -> None:
        self._plot = plot
        self._least_height_px = least_height_px
        self._most_lines = most_lines
        self._dot, self._text = _hover_items()
        pens.hold(self._text, _text_box_pen())
        plot.getPlotItem().addItem(self._dot, ignoreBounds=True)
        # The box belongs to the scene, not to the view box. A view box clips
        # what it holds to the plot inside the axes, so a box taller than
        # that plot lost its last value line, which is the line the reader
        # came for (`PL-HXSD`). In the scene the box may lie over the axes,
        # and `show` keeps it whole inside the widget.
        plot.scene().addItem(self._text)
        self._scene_position: QPointF | None = None
        # A child of the plot, so Qt keeps it for as long as the plot lives.
        self._moves = _PointerMoves(plot)
        self.hold_the_tallest_box()

    def hold_the_tallest_box(self) -> None:
        """Draw the box in the plot's font, and keep the plot at least as tall as the tallest box.

        The plot's least height is its theme height, or the tallest box's if
        that is taller. The tallest box has the plot's most lines, and its
        height follows the font. So a chart calls this again when its font
        changes. A text item keeps the font it was built with, so without
        that call the box would keep the old font. At the container's font
        and at a 13-pixel font the theme height is the taller (`PL-HXSD`),
        and the floor changes nothing. A larger font, such as a reader
        enlarging the desktop's text, makes the box taller than the theme
        height. The plot then grows, rather than cutting off the box's last
        value line.
        """

        self._text.setFont(self._plot.font())
        _, probe = _hover_items()
        probe.setFont(self._plot.font())
        self._plot.scene().addItem(probe)
        probe.setText("\n".join("0" * self._most_lines))
        tallest_px = ceil(probe.boundingRect().height())
        self._plot.scene().removeItem(probe)
        self._plot.setMinimumHeight(max(self._least_height_px, tallest_px))

    @property
    def moved(self) -> SignalInstance:
        """Each new pointer position over the plot, in scene coordinates, or `None` once it leaves.

        The plot connects a slot of its own to this signal. The slot stores
        the position and then shows the readout for it. With only one slot,
        nothing can show a readout before the position is stored. A second,
        direct slot on the scene's signal did exactly that (`PL-TCR5`). The
        slot is not handed to this object to keep. A method kept here would
        hold the plot's widget in a reference cycle. Such a widget is freed
        whenever the garbage collector next runs, which can be in the middle
        of the widget's own paint. That was measured, and it caused a
        segmentation fault.
        """

        return self._moves.moved

    def move_to(self, scene_position: QPointF | None) -> None:
        """Take the pointer's new position, in scene coordinates, or `None` once it has left."""

        self._scene_position = scene_position

    def scene_position(self) -> QPointF | None:
        """Where the pointer last was, in scene coordinates, if it is over the widget."""

        return self._scene_position

    def show(self, target: HoverTarget, x_range: tuple[float, float]) -> None:
        """Put a dot on every point in the readout, and put the text beside them.

        There is one dot per reading rather than one for the box. Every run
        *and* every compartment inside the radius is in the readout
        (`chart_frame.HoverTarget`). A single dot would mark one curve while
        the box gave values for several. That is the attribution failure that
        `PL-MN4J` closed, coming back through the marker instead of through
        the text. The dots have covered several compartments since `PL-0RZ0`.
        So a reader whose pointer is between two closely packed traces sees
        both marked, rather than being told which one the arithmetic
        preferred.
        """

        self._dot.setData(
            _plot_coordinates([reading.time_s for reading in target.readings]),
            _plot_coordinates([reading.value for reading in target.readings]),
        )
        self._text.setText(target.readout)
        # The box sits to the right of the anchor and above it, unless that
        # would put it off the plot. Past the middle of the window, it goes to
        # the left. Where the room above the anchor is less than the box's
        # height, it goes below. A following window keeps its newest point at
        # the right edge, and that is where a reader most often hovers. So the
        # flip is the common case rather than a rare one. The vertical flip is
        # decided in pixels, because the box's height is fixed in pixels while
        # the plot's height is whatever its Area leaves it. Deciding it at a
        # fraction of the axis put the box partly above a short plot
        # (`PL-9BVQ`). A plot shorter than the box's height on both sides of
        # the anchor, as a View at its least height can leave it, gets the box
        # with its top at the plot's top (`PL-CBYS`). There the box is almost
        # as tall as the plot. Beside the anchor it hid the curve on that
        # side, which is what the value is read against, so it goes to the far
        # edge of the plot instead, on the side away from the anchor
        # (`PL-YJ7N`). A box wider than the room between that edge and the
        # anchor would lie over the hovered point there, so it stays beside
        # the anchor.
        anchor = self._pixel(target.anchor.time_s, target.anchor.value)
        past_middle = target.anchor.time_s > (x_range[0] + x_range[1]) / 2.0
        plot = _plot_area(self._plot)
        height_px = self._box_height_px()
        # Which of the box's sides is at `x_px`: its left side (0) or its
        # right side (1). The box is placed by that side rather than by a
        # width, so the width it is drawn at is the width it is placed by.
        side = 1 if past_middle else 0
        x_px = anchor.x()

        if anchor.y() - plot.top() >= height_px:
            top_px = anchor.y() - height_px
        elif plot.bottom() - anchor.y() >= height_px:
            top_px = anchor.y()
        else:
            top_px = plot.top()
            # Past the middle the anchor is in the right half, so the box takes
            # the left edge, and the other way round.
            far_side = 0 if past_middle else 1
            far_edge = self._pixel(x_range[far_side], 0.0).x()

            if self._box_width_px() <= abs(anchor.x() - far_edge):
                side = far_side
                x_px = far_edge

        # A box taller than the plot, as a narrow plot whose time-axis title
        # wraps or a larger desktop font can make it, is moved up until all of
        # it is inside the widget, over the time axis if need be. This is the
        # shift that tooltip libraries make at a window's edge (Floating UI's
        # `shift`). The widget is never shorter than the tallest box
        # (`hold_the_tallest_box`), so no line of the box is cut off.
        bottom_px = float(self._plot.viewport().height())
        top_px = max(0.0, min(top_px, bottom_px - height_px))
        # On a narrow plot a box can be wider than the room beside its point.
        # It then goes to the other side of the point, as tooltip libraries
        # flip one (Floating UI's `flip`). Where it fits on neither side, it is
        # moved across until all of it is inside the widget, even though it
        # then covers the point, because a value cut off at the widget's edge
        # can be misread and a covered point cannot (`PL-HXSD`).
        width_px = self._box_width_px()
        right_px = float(self._plot.viewport().width())
        left_px = x_px - side * width_px

        if left_px < 0.0 or left_px + width_px > right_px:
            flipped_px = x_px - (1 - side) * width_px

            if 0.0 <= flipped_px and flipped_px + width_px <= right_px:
                side = 1 - side
            else:
                x_px = max(0.0, min(left_px, right_px - width_px)) + side * width_px

        self._text.setAnchor((side, 0))
        self._text.setPos(self._plot.viewportTransform().inverted()[0].map(QPointF(x_px, top_px)))

        self._dot.show()
        # This uses `setVisible` rather than `show`. `show` goes straight to
        # Qt's own method, and so it skips pyqtgraph's override. That override
        # is what orients the box for the view. A box shown through `show` is
        # oriented only at its next paint, so if it is measured before then it
        # can come out thousands of pixels tall (`PL-J0F7`).
        self._text.setVisible(True)

    def _pixel(self, time_s: float, value: float) -> QPointF:
        """Return where a plot position lies in the plot widget's pixels."""

        view_box = self._plot.getPlotItem().getViewBox()
        scene_point: QPointF = view_box.mapViewToScene(QPointF(time_s, value))

        return QPointF(self._plot.viewportTransform().map(scene_point))

    def _box_height_px(self) -> float:
        """Return the box's height in pixels, for the text it now holds.

        The height is read from the text item's own rectangle, which is in
        pixels at any view scale. It is not read from the box's position in
        the scene, which is only correct once the box has been oriented for
        the view (`PL-J0F7`).
        """

        return float(self._text.boundingRect().height())

    def _box_width_px(self) -> float:
        """Return the box's width in pixels, for the text it now holds, read as its height is."""

        return float(self._text.boundingRect().width())

    def hide(self) -> None:
        self._dot.hide()
        self._text.hide()

    def shown_text(self) -> str | None:
        """What the hover currently says, or `None` while it is hidden."""

        return str(self._text.textItem.toPlainText()) if self._text.isVisible() else None

    def shown_box(self) -> QRectF | None:
        """Where the box is in the plot widget's pixels, or `None` while it is hidden."""

        if not self._text.isVisible():
            return None

        return QRectF(self._plot.viewportTransform().mapRect(self._text.sceneBoundingRect()))


class _RunPens:
    """One run's pens, built on first use and kept.

    Once more than one run is drawn, a trace's width identifies the *run*
    (`chart_frame.run_trace_style`). So a pen depends on how many runs are on
    the chart as well as on the compartment, and that count changes when a
    reader forks a run. The pens are rebuilt only when the count changes, and
    they are then cached. So the cost per frame stays what it was: items are
    moved, never rebuilt.
    """

    def __init__(self, run_index: RunIndex) -> None:
        self._run_index = run_index
        self._pens: dict[tuple[RecordedQuantity, RunCount], QPen] = {}
        self._penned_for: RunCount | None = None

    def changed_for(self, run_count: RunCount) -> bool:
        """Whether the pens in use were built for another run count, and record this one."""

        if self._penned_for == run_count:
            return False

        self._penned_for = run_count

        return True

    def of(self, quantity: RecordedQuantity, run_count: RunCount) -> QPen:
        """This run's pen for a compartment, when this many runs are drawn."""

        key = (quantity, run_count)

        if key not in self._pens:
            self._pens[key] = run_trace_pen(quantity, self._run_index, run_count)

        return self._pens[key]


def _branch_point_mark(item: Any, pens: _ScreenPens) -> Any:
    """One run's fork mark: hidden, full height, and drawn over the gridlines.

    There is one mark per run rather than one per plot, because a fork
    belongs to the run that started at it. A trunk run, which did not start
    at a fork, simply never shows its mark.
    """

    mark = pg.InfiniteLine(pos=0.0, angle=_VERTICAL_LINE_ANGLE_DEG, movable=False)
    pens.hold(mark, _branch_point_pen())
    mark.setZValue(_Z_CONTROL_MARK)
    mark.hide()
    item.addItem(mark, ignoreBounds=True)

    return mark


def _place_branch_point(mark: Any, time_s: float | None) -> None:
    """Place a run's fork mark at its instant, or hide the mark if the run has no fork."""

    if time_s is None:
        mark.hide()

        return

    mark.setPos(time_s)
    mark.show()


class _PreviewMarks:
    """One run's preview region and its label on one plot, hidden until a drag is held.

    The region runs from the run's reach to the axis's right edge. It is drawn
    beneath every trace, as the MAC-awake band is. Its left edge is a stroke at
    the reach, where the run stands now. The label sits inside the region, at
    the top, in the same kind of box as the hover's text. So a screenshot
    taken during a drag says in words that the curves there did not happen
    (`PL-5B1N`).
    """

    def __init__(self, item: Any, pens: _ScreenPens) -> None:
        fill = QColor(PREVIEW_REGION_COLOR)
        fill.setAlphaF(PREVIEW_REGION_FILL_OPACITY)
        self.region = pg.LinearRegionItem(
            values=(0.0, 0.0), orientation="vertical", movable=False, brush=pg.mkBrush(fill)
        )
        pens.hold(
            self.region, pg.mkPen(PREVIEW_REGION_COLOR, width=PREVIEW_REGION_EDGE_STROKE_WIDTH)
        )
        self.region.setZValue(_Z_REFERENCE_BAND)
        self.region.hide()
        item.addItem(self.region, ignoreBounds=True)
        self.label = pg.TextItem(color=INK, fill=pg.mkBrush(PANEL), anchor=(0, 0))
        pens.hold(self.label, _text_box_pen())
        self.label.setZValue(_Z_PREVIEW_LABEL)
        self.label.hide()
        item.addItem(self.label, ignoreBounds=True)

    def place(self, preview: RunPreview | None, top: float) -> None:
        """Show the region and the label for a preview, or hide both where there is none.

        Args:
            preview: The run's preview, or `None`.
            top: The top of the plot's value axis, where the label is hung.
        """

        if preview is None:
            self.hide()
            return

        start_s, _ = preview.region_s
        self.region.setRegion(preview.region_s)
        self.region.show()
        self.label.setText(preview.label)
        self.label.setPos(start_s, top)
        # `setVisible` rather than `show`, for the reason `_HoverReadout.show`
        # gives: it orients the box for the view at once (`PL-J0F7`).
        self.label.setVisible(True)

    def hide(self) -> None:
        self.region.hide()
        self.label.hide()

    def shown_region(self) -> tuple[float, float] | None:
        if not self.region.isVisible():
            return None

        start, stop = self.region.getRegion()

        return float(start), float(stop)

    def shown_label(self) -> str | None:
        return str(self.label.textItem.toPlainText()) if self.label.isVisible() else None


class _RunItems:
    """One run's items on the concentration chart: its curves, its fork, its marks, its preview."""

    def __init__(self, item: Any, run_index: RunIndex, screen_pens: _ScreenPens) -> None:
        self._run_index = run_index
        self._screen_pens = screen_pens
        self.pens = _RunPens(run_index)
        self.curves: dict[RecordedQuantity, Any] = {}
        self.preview_curves: dict[RecordedQuantity, Any] = {}

        for style in COMPARTMENT_TRACES:
            curve = pg.PlotCurveItem(antialias=True)
            screen_pens.hold(curve, trace_pen(style))
            item.addItem(curve)
            self.curves[style.quantity] = curve

        for style in COMPARTMENT_TRACES:
            curve = pg.PlotCurveItem(antialias=True)
            screen_pens.hold(curve, trace_pen(style))
            curve.hide()
            item.addItem(curve)
            self.preview_curves[style.quantity] = curve

        self.preview = _PreviewMarks(item, screen_pens)
        self.branch_point = _branch_point_mark(item, screen_pens)
        self.marks = _control_mark_pool(item, screen_pens)

    def repen(self, run_count: RunCount) -> None:
        """Give every curve and preview curve its pen for this many runs."""

        for quantity, curve in self.curves.items():
            self._screen_pens.hold(curve, self.pens.of(quantity, run_count))

        for quantity, curve in self.preview_curves.items():
            self._screen_pens.hold(curve, preview_trace_pen(quantity, self._run_index, run_count))

    def hide(self) -> None:
        for curve in (*self.curves.values(), *self.preview_curves.values()):
            curve.hide()

        self.preview.hide()
        self.branch_point.hide()

        for mark in self.marks:
            mark.hide()


def _control_mark_pool(item: Any, pens: _ScreenPens) -> list[Any]:
    """A fixed pool of vertical marks, all hidden, for one run on one plot.

    Being vertical is what identifies the mark, because no trace or
    reference on either plot is vertical. So the orientation survives
    greyscale and every colour-vision deficiency. The only other vertical
    lines are the gridlines and the fork mark, which is solid where a control
    mark is dashed. The mark also takes no colour from a palette that six
    traces have already used up. The marks are full height by
    construction, because the time a mark shows has to be readable against
    every trace.
    """

    pen = _control_mark_pen()
    marks = []

    for _ in range(MAX_CHART_CONTROL_MARKS):
        mark = pg.InfiniteLine(pos=0.0, angle=_VERTICAL_LINE_ANGLE_DEG, movable=False)
        pens.hold(mark, pen)
        mark.setZValue(_Z_CONTROL_MARK)
        mark.hide()
        item.addItem(mark, ignoreBounds=True)
        marks.append(mark)

    return marks


def _place_marks(marks: Sequence[Any], times_s: Sequence[float]) -> None:
    """Place the pool's marks at these times, and hide the rest."""

    for mark, time_s in zip(marks, times_s, strict=False):
        mark.setPos(time_s)
        mark.show()

    for mark in marks[len(times_s) :]:
        mark.hide()


def _set_time_axis(item: Any, frame: ChartFrame) -> None:
    """Set the range and the labelled ticks of the bottom axis for the window the frame draws.

    The tick positions come from `chart_time_base.tick_times`, and their
    wording from `formatting.format_chart_time_label`. Both are settled in
    the frame, and this function hands them to the axis. Every tick label
    carries its unit, such as `45s`, `3m` or `1h30m`. This axis spans
    anything from a minute to half a day. A bare `600` means seconds at one
    width but would be read as minutes at another, while looking identical
    at both.
    """

    item.setXRange(frame.start_s, frame.stop_s, padding=0)
    item.getAxis("bottom").setTicks(
        [[(tick, format_chart_time_label(tick)) for tick in frame.tick_times_s]]
    )


class _ConcentrationChartAccessible(QAccessibleWidget):
    """Describe the concentration chart to a screen reader, as an image with a text alternative.

    Qt describes a plain widget as a client area, which VoiceOver on macOS
    passes over, and pyqtgraph gives none of its plot items to assistive
    technology. So the chart reports the role of a graphic, which AT-SPI, UI
    Automation and macOS each report as an image. Its name and long
    description are `dashboard_frame`'s, written from the frame the chart
    last drew (`PL-T9RB`). Both are written when a screen reader asks for
    them. A screen reader that keeps the texts it has read, as the AT-SPI
    client library on Linux does, reads them again when told that they
    changed, so the chart reports each change (`ConcentrationChart.draw`).
    """

    def __init__(self, chart: ConcentrationChart) -> None:
        super().__init__(chart, QAccessible.Role.Graphic)
        self._chart = chart

    def text(self, kind: QAccessible.Text) -> str:
        """Return the chart's name or long description, or Qt's own text for anything else."""

        if kind is QAccessible.Text.Name:
            return concentration_chart_name(self._chart.frame)

        if kind is QAccessible.Text.Description:
            return concentration_chart_description(self._chart.frame)

        return QAccessibleWidget.text(self, kind)


def _concentration_chart_accessible(
    key: str, widget: QObject
) -> _ConcentrationChartAccessible | None:
    """Return the accessible interface for a concentration chart, and nothing for any other object.

    Qt asks each installed factory as `qt_widgets._setting_slider_accessible`
    describes, and keeps the first interface returned.
    """

    if isinstance(widget, ConcentrationChart):
        return _ConcentrationChartAccessible(widget)

    return None


# Whether `_concentration_chart_accessible` is installed. Qt keeps one list of
# factories for the process, so one installation serves every chart.
_chart_accessibility_installed = False


def _install_concentration_chart_accessibility() -> None:
    """Install `_concentration_chart_accessible` the first time a chart is built.

    PySide6 installs a factory only once a `QApplication` exists, as
    `qt_widgets._install_setting_slider_accessibility` records, and a chart
    cannot be built before one.
    """

    global _chart_accessibility_installed

    if _chart_accessibility_installed:
        return

    QAccessible.installFactory(_concentration_chart_accessible)
    _chart_accessibility_installed = True


class ConcentrationChart(QWidget):
    """The six compartment traces, both clinical references, both axes, and the marks.

    The chart is built once, and `draw` redraws it on each frame from a
    `ChartFrame` that the dashboard assembles. It keeps nothing about the run
    except the last frame it drew, which the hover reads.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        _install_concentration_chart_accessibility()
        self._plot, self._pens = _plot(PANEL)
        self._plot.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._plot)
        item = self._plot.getPlotItem()
        item.setLabel("left", DisplayUnit.CONCENTRATION.axis_title, color=MUTED)
        self._time_title = _TimeAxisTitle(item, self._plot)
        item.showAxis("right")
        item.getAxis("right").setLabel(DisplayUnit.MAC_MULTIPLE.axis_title, color=MUTED)

        # The band and the line are drawn under the traces, so a reference
        # never hides a trace. Both are placed from the frame's own MAC and
        # MAC-awake values, so neither can be drawn at another agent's height.
        # The band is two stroked edges with a light fill between them. Both
        # strokes sit on the published boundaries, so the drawn extent is
        # exactly the data extent. A band drawn thicker than its two edges
        # would claim a wider population spread than the literature supports
        # (`PL-90Y6`).
        band_color = QColor(MAC_AWAKE_BAND_COLOR)
        band_color.setAlphaF(MAC_AWAKE_BAND_FILL_OPACITY)
        self._band = pg.LinearRegionItem(
            values=(0.0, 0.0), orientation="horizontal", movable=False, brush=pg.mkBrush(band_color)
        )
        self._pens.hold(
            self._band, pg.mkPen(MAC_AWAKE_BAND_COLOR, width=MAC_AWAKE_BAND_EDGE_STROKE_WIDTH)
        )
        self._band.setZValue(_Z_REFERENCE_BAND)
        item.addItem(self._band, ignoreBounds=True)
        self._one_mac_line = pg.InfiniteLine(
            pos=0.0, angle=_HORIZONTAL_LINE_ANGLE_DEG, movable=False
        )
        self._pens.hold(
            self._one_mac_line,
            dashed_pen(ONE_MAC_LINE_COLOR, ONE_MAC_LINE_STROKE_WIDTH, ONE_MAC_LINE_DASH_PATTERN),
        )
        self._one_mac_line.setZValue(_Z_REFERENCE_LINE)
        item.addItem(self._one_mac_line, ignoreBounds=True)
        self._grid = _GridLines(item, self._pens)

        self._runs: list[_RunItems] = []
        self._frame: ChartFrame | None = None
        # The name and description last reported to assistive technology.
        self._accessible_texts = (
            concentration_chart_name(None),
            concentration_chart_description(None),
        )
        self._hover = _HoverReadout(
            self._plot, self._pens, CHART_LEAST_HEIGHT, _TRACE_HOVER_MOST_LINES
        )
        self._hover.moved.connect(self._on_pointer)
        # Whether the box goes above or below its point depends on the plot's
        # height in pixels. So a resize places the box again, even while the
        # pointer rests and no frame is drawn (`PL-9BVQ`).
        item.getViewBox().sigResized.connect(self._refresh_hover)

    def draw(self, frame: ChartFrame) -> None:
        """Move every item to match one frame.

        Args:
            frame: What to draw. A run beyond the items already built gets
                its own items when it first appears. The items of a run that
                the frame no longer has are hidden.
        """

        item = self._plot.getPlotItem()
        _set_time_axis(item, frame)
        # The ceiling and the gridlines move with the agent, because both are
        # multiples of its 1 MAC. That is exactly what keeps the *scale*
        # still: at the top the reader chose, a MAC multiple is drawn at the
        # same height whichever agent is running. Each gridline stands at a
        # label of the right, MAC, axis. The left axis is labelled at round
        # percentages, each at its own tick mark, and draws no gridline
        # (`PL-BNMZ`).
        item.setYRange(0.0, frame.axis_top_percent, padding=0)
        item.getAxis("left").setTicks([list(frame.percent_ticks)])
        item.getAxis("right").setTicks([list(frame.mac_ticks)])
        self._grid.place(frame.tick_times_s, [position for position, _ in frame.mac_ticks])
        self._one_mac_line.setPos(frame.one_mac_percent)
        self._band.setRegion(frame.mac_awake_band_percent)
        self._one_mac_line.show()
        self._band.show()

        while len(self._runs) < len(frame.runs):
            self._runs.append(_RunItems(item, RunIndex(len(self._runs)), self._pens))

        # Each run's items are added to the plot in turn, so a later run is
        # drawn over an earlier one. That order matters and is not
        # incidental. A branch reproduces its parent up to the fork, so before
        # the branch point the two curves coincide exactly. Drawing the
        # narrower second run last is what keeps both visible there
        # (`theme.COMPARED_RUN_WIDTH_STEP`).
        run_count = frame.run_count

        for items, run in zip(self._runs, frame.runs, strict=False):
            if items.pens.changed_for(run_count):
                items.repen(run_count)

            for quantity, curve in items.curves.items():
                if quantity in frame.visible:
                    # Only the traces that the reader has left shown are
                    # written. A hidden trace costs nothing per frame and
                    # keeps the points of the frame it was last drawn in.
                    # That is why it is hidden rather than emptied, and why
                    # it is redrawn here before it is shown again.
                    _draw_curve(curve, run.times_s, run.percents(quantity))
                    curve.show()
                else:
                    curve.hide()

            # A preview is drawn with the same compartments as the run, and
            # only while a drag is held on this run (`PL-5B1N`).
            for quantity, curve in items.preview_curves.items():
                if run.preview is not None and quantity in frame.visible:
                    _draw_curve(curve, run.preview.times_s, run.preview.percents(quantity))
                    curve.show()
                else:
                    curve.hide()

            items.preview.place(run.preview, frame.axis_top_percent)
            _place_branch_point(items.branch_point, run.branch_point_s)
            _place_marks(items.marks, run.control_marks_s)

        for items in self._runs[len(frame.runs) :]:
            items.hide()

        self._frame = frame
        self._report_text_changes()
        self._refresh_hover()

    def _report_text_changes(self) -> None:
        """Tell assistive technology that the chart's name or description changed, if either did.

        Qt sends these events for its own widgets when their text changes, as
        `QLabel.setText` does. A screen reader that keeps the texts it has
        read reads them again on these events. Without them it would go on
        reading the values of an earlier frame (`PL-T9RB`).
        """

        texts = (
            concentration_chart_name(self._frame),
            concentration_chart_description(self._frame),
        )
        events = (QAccessible.Event.NameChanged, QAccessible.Event.DescriptionChanged)

        for event, before, now in zip(events, self._accessible_texts, texts, strict=True):
            if now != before:
                QAccessible.updateAccessibility(QAccessibleEvent(self, event))

        self._accessible_texts = texts

    def withhold(self) -> None:
        """Empty the plot: no trace, no mark and no clinical reference, until the next frame.

        A frame is withheld when the run has started over, or a run was
        removed, since the last frame that drew (`run_presentation.ShownFrame`).
        The traces, the 1 MAC line and the MAC-awake band of that frame
        describe a run that is gone, or another agent, so none of them stays
        on the plot. The axes lose their labels and gridlines too. The percent
        labels fall at multiples of the agent's 1 MAC, and the time labels
        and the time axis's title describe the window of a run that is gone.
        """

        for items in self._runs:
            items.hide()

        self._one_mac_line.hide()
        self._band.hide()
        _clear_axes(self._plot.getPlotItem(), self._grid, self._time_title, ("left", "right"), ())
        self._frame = None
        self._report_text_changes()
        self._refresh_hover()

    @property
    def frame(self) -> ChartFrame | None:
        """The frame last drawn, or `None` before the first and after `withhold`."""

        return self._frame

    def preview_points(
        self, run: int, quantity: RecordedQuantity
    ) -> tuple[tuple[float, ...], tuple[float, ...]]:
        """The instants and percents of one run's preview of a compartment, read from the plot item.

        Returns:
            Times in simulated seconds and values in percent. Both are empty
            where no preview of that compartment is drawn.
        """

        curve = self._runs[run].preview_curves[quantity]

        if not curve.isVisible():
            return (), ()

        times, values = curve.getData()

        return tuple(float(t) for t in times), tuple(float(v) for v in values)

    def preview_pen(self, run: int, quantity: RecordedQuantity) -> QPen:
        """The pen one run's preview of a compartment is drawn with, as specified.

        The width is in device-independent pixels. The curve draws it at that
        width on any screen, through `on_screen`.
        """

        return self._pens.specified(self._runs[run].preview_curves[quantity])

    def preview_region(self, run: int) -> tuple[float, float] | None:
        """Where one run's preview region is drawn, in simulated seconds, or None if hidden."""

        return self._runs[run].preview.shown_region()

    def preview_label(self, run: int) -> str | None:
        """What one run's preview label says, or None while it is hidden."""

        return self._runs[run].preview.shown_label()

    def changeEvent(self, event: QEvent) -> None:  # Qt spells this in camelCase.
        """Hold the tallest hover box again when the font, and so its height, changes."""

        super().changeEvent(event)

        if event.type() == QEvent.Type.FontChange:
            self._hover.hold_the_tallest_box()
            # A box on show has the new font, and so a new size, but stays
            # where the old size put it until it is placed again.
            self._refresh_hover()

    def sizeHint(self) -> QSize:  # Qt spells this in camelCase.
        """As wide as the plot asks and `theme.CHART_HEIGHT` tall.

        The chart grows into spare height. In a View too short for this
        height it shrinks to `theme.CHART_LEAST_HEIGHT`, or to the tallest
        hover box's height where a large font makes that the taller
        (`_HoverReadout.hold_the_tallest_box`).
        """

        return _preferred_size(self._plot, CHART_HEIGHT)

    def plot_width_px(self) -> float:
        """The width of the plot area in logical pixels, for `assemble_chart_frame`.

        The dashboard samples one frame at the widest of its charts' widths,
        so that no chart draws a chord wider than a pixel (`PL-GS3R`).
        """

        return _plot_width_px(self._plot)

    @property
    def owes_a_frame(self) -> bool:
        """Whether this plot is now wider than the width its last frame was sampled for.

        The dashboard's render tick reads this property from every chart. So
        a chart whose Area a reader widens is redrawn on the next tick, even
        when the window kept its size (`resample_owed`, `PL-9LNF`).
        """

        return resample_owed(self._frame, self.plot_width_px())

    def drawn_points(
        self, run: int, quantity: RecordedQuantity
    ) -> tuple[tuple[float, ...], tuple[float, ...]]:
        """The instants and percents with which one run's curve for a compartment is drawn.

        The values are read back from the curve item itself rather than from
        the frame. So a test can compare what the toolkit holds with what the
        frame said.

        Args:
            run: Which run, as a position in the frame's runs.
            quantity: Which compartment.

        Returns:
            Times in simulated seconds and values in percent. Both are empty
            for a curve that is hidden.

        Raises:
            IndexError: If no items have been built for that run.
            KeyError: If `quantity` is not a compartment on this chart.
        """

        curve = self._runs[run].curves[quantity]

        if not curve.isVisible():
            return (), ()

        times, values = curve.getData()

        return tuple(float(t) for t in times), tuple(float(v) for v in values)

    def drawn_pen(self, run: int, quantity: RecordedQuantity) -> QPen:
        """The pen one run's curve for a compartment is drawn with, as specified.

        The pen is the one the curve item was last given, rather than one
        recomputed here. So a test can compare what the chart is drawing with
        what `chart_frame` said it should draw. Its width is in
        device-independent pixels, and the curve draws it at that width on any
        screen, through `on_screen`.
        """

        return self._pens.specified(self._runs[run].curves[quantity])

    def branch_point_time(self, run: int) -> float | None:
        """Where one run's fork is marked, in simulated seconds, or None if unmarked."""

        mark = self._runs[run].branch_point

        return float(mark.value()) if mark.isVisible() else None

    def control_mark_times(self, run: int) -> tuple[float, ...]:
        """Where one run's visible control marks are, in simulated seconds."""

        return tuple(float(mark.value()) for mark in self._runs[run].marks if mark.isVisible())

    def mac_awake_band(self) -> tuple[float, float]:
        """The band's lower and upper edges as drawn, in percent."""

        lower, upper = self._band.getRegion()

        return float(lower), float(upper)

    def one_mac_line(self) -> float:
        """Where the 1 MAC line is drawn, in percent."""

        return float(self._one_mac_line.value())

    def axis_ticks(self, name: str) -> tuple[tuple[float, str], ...]:
        """The ticks one axis is labelled at, as (position, label)."""

        return _axis_ticks(self._plot.getPlotItem().getAxis(name))

    def horizontal_gridlines(self) -> tuple[float, ...]:
        """Where the plot's horizontal gridlines stand, in percent."""

        return self._grid.horizontal_positions()

    def tick_label_rects(self, name: str) -> tuple[tuple[str, QRectF], ...]:
        """Each tick label one axis paints, with its box in the pixels of `painted`."""

        return _tick_label_rects(self._plot, name)

    def axis_titles(self) -> tuple[str, ...]:
        """The titles of the chart's axes, so a walk over the whole interface finds them."""

        return _axis_titles(self._plot, self._time_title.words)

    def show_time_window(self, window: str) -> None:
        """Write the window the plot shows into the time axis's title.

        Args:
            window: What `dashboard_frame.time_axis_caption` says of the
                frame just drawn.
        """

        self._time_title.show(window)

    @property
    def time_axis_title(self) -> str:
        """The time axis's title on one line, however the axis breaks it."""

        return self._time_title.words

    @property
    def time_axis_lines(self) -> tuple[str, ...]:
        """The time axis's title as the axis draws it, one line at a time."""

        return self._time_title.lines

    @property
    def time_axis_title_offset_px(self) -> float:
        """How far the title's centre is from the time axis's centre, in px."""

        return self._time_title.offset_px

    def painted(self) -> QImage:
        """The chart as painted, so a test can check what is on screen."""

        return _render(self)

    def plot_pixel(self, time_s: float, percent: float) -> tuple[int, int]:
        """Which pixel of `painted` a plot position lands on."""

        return _plot_pixel(self._plot, time_s, percent)

    def plot_area(self) -> QRectF:
        """The plot inside its axes, in the pixels of `painted`, which holds any box that fits."""

        return _plot_area(self._plot)

    def readout_at(self, time_s: float, percent: float) -> str | None:
        """What the hover would say for a pointer at this plot position.

        This is the same lookup that the pointer triggers. It is exposed so a
        test can check the rendered readout against the frame without
        synthesizing mouse events. The widget has to be shown and laid out
        first, because the tolerance is in pixels, and a plot with no size has
        no pixels.

        Args:
            time_s: The pointer's position along the time axis.
            percent: The pointer's position on the percent axis.

        Returns:
            The three-line readout, or `None` when no drawn point is within
            `HOVER_RADIUS_PIXELS`.
        """

        target = self._target_at(time_s, percent)

        return None if target is None else target.readout

    def _target_at(self, time_s: float, percent: float) -> HoverTarget | None:
        if self._frame is None:
            return None

        seconds_per_pixel, percent_per_pixel = self._plot.getPlotItem().getViewBox().viewPixelSize()

        return nearest_trace_point(
            self._frame, time_s, percent, seconds_per_pixel, percent_per_pixel, HOVER_RADIUS_PIXELS
        )

    def _on_pointer(self, scene_position: QPointF | None) -> None:
        self._hover.move_to(scene_position)
        self._refresh_hover()

    def _refresh_hover(self) -> None:
        """Show the readout for wherever the pointer is, or hide it when no point is near."""

        position = self._hover.scene_position()
        view_box = self._plot.getPlotItem().getViewBox()

        if (
            self._frame is None
            or position is None
            or not view_box.sceneBoundingRect().contains(position)
        ):
            self._hover.hide()
            return

        point = view_box.mapSceneToView(position)
        target = self._target_at(point.x(), point.y())

        if target is None:
            self._hover.hide()
        else:
            self._hover.show(target, (self._frame.start_s, self._frame.stop_s))

    def hover_text(self) -> str | None:
        """What the hover box currently shows, or `None` while it is hidden."""

        return self._hover.shown_text()

    def hover_box(self) -> QRectF | None:
        """Where the hover box is in the pixels of `painted`, or `None` while it is hidden."""

        return self._hover.shown_box()


class _WashInRunItems:
    """One run's items on the wash-in plot: its stretches, their ends, its fork, its marks."""

    def __init__(self, item: Any, run_index: RunIndex, pens: _ScreenPens) -> None:
        self._run_index = run_index
        self._pens = pens
        self._penned_for: RunCount | None = None
        pen = _wash_in_pen()
        self.stretches = []

        for _ in range(MAX_CHART_WASH_IN_SEGMENTS):
            stretch = pg.PlotCurveItem(antialias=True)
            pens.hold(stretch, pen)
            stretch.hide()
            item.addItem(stretch)
            self.stretches.append(stretch)

        # One scatter item holds every terminus dot of the run, in the trace's
        # own colour. A dot says that the series ends here rather than
        # continuing out of view, and only a stretch that *stopped* gets one
        # for that reason. A stretch of one point gets one too, because a
        # line needs two points (`WashInStretch.has_end_dot`).
        self.termini = pg.ScatterPlotItem(
            size=_WASH_IN_TERMINUS_DIAMETER, pen=None, brush=pg.mkBrush(WASH_IN_COLOR)
        )
        item.addItem(self.termini, ignoreBounds=True)
        self.preview_stretches = []

        for _ in range(MAX_CHART_WASH_IN_SEGMENTS):
            stretch = pg.PlotCurveItem(antialias=True)
            pens.hold(stretch, pen)
            stretch.hide()
            item.addItem(stretch)
            self.preview_stretches.append(stretch)

        # A predicted stretch that stops gets its dot too, by the same rule as
        # the run's, so a preview that crosses equilibrium reads as ended.
        self.preview_termini = pg.ScatterPlotItem(
            size=_WASH_IN_TERMINUS_DIAMETER, pen=None, brush=pg.mkBrush(WASH_IN_COLOR)
        )
        item.addItem(self.preview_termini, ignoreBounds=True)
        self.preview = _PreviewMarks(item, pens)
        self.branch_point = _branch_point_mark(item, pens)
        self.marks = _control_mark_pool(item, pens)

    def repen(self, run_count: RunCount) -> None:
        """Give every stretch a new pen when the number of runs on the plot has changed."""

        if self._penned_for == run_count:
            return

        self._penned_for = run_count
        pen = _wash_in_pen(self._run_index, run_count)
        preview_pen = _wash_in_preview_pen(self._run_index, run_count)

        for stretch in self.stretches:
            self._pens.hold(stretch, pen)

        for stretch in self.preview_stretches:
            self._pens.hold(stretch, preview_pen)

    def hide(self) -> None:
        for stretch in (*self.stretches, *self.preview_stretches):
            stretch.hide()

        self.termini.setData(_plot_coordinates(()), _plot_coordinates(()))
        self.preview_termini.setData(_plot_coordinates(()), _plot_coordinates(()))
        self.preview.hide()
        self.branch_point.hide()

        for mark in self.marks:
            mark.hide()


class WashInChart(QWidget):
    """The F_A/F_I plot: the stretches, the equilibrium line, the marks, and its axis.

    The plot is a View of its own, and it keeps its own time window
    (`PL-L59K`). It shows the compartment chart's alveolar and circuit traces
    as one number, so the Induction Workspace places it beside that chart.
    While the two plots show the same window, they draw the same `ChartFrame`
    (`AreaLayout.frame_requests`), so they show the same instants.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._plot, self._pens = _plot(PANEL)
        self._plot.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._plot)
        item = self._plot.getPlotItem()
        item.setLabel("left", WASH_IN_RATIO_NAME, color=MUTED)
        self._time_title = _TimeAxisTitle(item, self._plot)
        # The axis is fixed rather than fitted to the data. It is labelled at
        # its own gridlines, at its own resolution, as `docs/INTERFACE.md`
        # § "F_A/F_I as a displayed ratio" specifies.
        item.setYRange(0.0, WASH_IN_AXIS_MAXIMUM, padding=0)
        item.getAxis("left").setTicks([list(wash_in_axis_ticks())])

        # The curve's asymptote, drawn as the reference it is. It is fixed by
        # definition rather than measured with a spread, so it is a line and
        # not a band. It belongs to the plot rather than to any run, because
        # F_A = F_I is a property of the ratio. So there is one line,
        # whatever the plot holds.
        self._equilibrium_line = pg.InfiniteLine(
            pos=WASH_IN_EQUILIBRIUM_RATIO, angle=_HORIZONTAL_LINE_ANGLE_DEG, movable=False
        )
        self._pens.hold(
            self._equilibrium_line,
            dashed_pen(
                EQUILIBRIUM_LINE_COLOR, EQUILIBRIUM_LINE_STROKE_WIDTH, EQUILIBRIUM_LINE_DASH_PATTERN
            ),
        )
        self._equilibrium_line.setZValue(_Z_REFERENCE_LINE)
        item.addItem(self._equilibrium_line, ignoreBounds=True)
        self._grid = _GridLines(item, self._pens)

        self._runs: list[_WashInRunItems] = []
        self._frame: ChartFrame | None = None
        self._hover = _HoverReadout(
            self._plot, self._pens, WASH_IN_CHART_LEAST_HEIGHT, _WASH_IN_HOVER_MOST_LINES
        )
        self._hover.moved.connect(self._on_pointer)
        # Whether the box goes above or below its point depends on the plot's
        # height in pixels. So a resize places the box again, even while the
        # pointer rests and no frame is drawn (`PL-9BVQ`).
        item.getViewBox().sigResized.connect(self._refresh_hover)

    def draw(self, frame: ChartFrame) -> None:
        """Move every item to match one frame.

        Args:
            frame: What to draw. While the compartment chart shows the same
                window, this is the frame that it drew, so the two plots
                share their instants and not merely their axis numbers.
        """

        item = self._plot.getPlotItem()
        _set_time_axis(item, frame)
        self._grid.place(frame.tick_times_s, [position for position, _ in wash_in_axis_ticks()])

        while len(self._runs) < len(frame.runs):
            self._runs.append(_WashInRunItems(item, RunIndex(len(self._runs)), self._pens))

        for items, run in zip(self._runs, frame.runs, strict=False):
            items.repen(frame.run_count)
            ends_x: list[float] = []
            ends_y: list[float] = []

            for curve, stretch in zip(items.stretches, run.wash_in, strict=False):
                _draw_curve(curve, stretch.times_s, stretch.ratios)
                curve.show()

                if stretch.has_end_dot:
                    ends_x.append(stretch.times_s[-1])
                    ends_y.append(stretch.ratios[-1])

            for curve in items.stretches[len(run.wash_in) :]:
                curve.hide()

            items.termini.setData(_plot_coordinates(ends_x), _plot_coordinates(ends_y))
            predicted = () if run.preview is None else run.preview.wash_in
            ends_x, ends_y = [], []

            for curve, stretch in zip(items.preview_stretches, predicted, strict=False):
                _draw_curve(curve, stretch.times_s, stretch.ratios)
                curve.show()

                if stretch.has_end_dot:
                    ends_x.append(stretch.times_s[-1])
                    ends_y.append(stretch.ratios[-1])

            items.preview_termini.setData(_plot_coordinates(ends_x), _plot_coordinates(ends_y))

            for curve in items.preview_stretches[len(predicted) :]:
                curve.hide()

            items.preview.place(run.preview, WASH_IN_AXIS_MAXIMUM)
            _place_branch_point(items.branch_point, run.branch_point_s)
            _place_marks(items.marks, run.control_marks_s)

        for items in self._runs[len(frame.runs) :]:
            items.hide()

        self._frame = frame
        self._refresh_hover()

    def withhold(self) -> None:
        """Empty the plot until the next frame, as `ConcentrationChart.withhold` does.

        The F_A/F_I axis keeps its labels and gridlines, because they do not
        depend on the run or the agent. The time axis loses its labels, its
        gridlines and the window in its title.
        """

        for items in self._runs:
            items.hide()

        _clear_axes(
            self._plot.getPlotItem(),
            self._grid,
            self._time_title,
            (),
            [position for position, _ in wash_in_axis_ticks()],
        )
        self._frame = None
        self._refresh_hover()

    @property
    def frame(self) -> ChartFrame | None:
        """The frame last drawn, or `None` before the first and after `withhold`."""

        return self._frame

    def changeEvent(self, event: QEvent) -> None:  # Qt spells this in camelCase.
        """Hold the tallest hover box again when the font, and so its height, changes."""

        super().changeEvent(event)

        if event.type() == QEvent.Type.FontChange:
            self._hover.hold_the_tallest_box()
            # A box on show has the new font, and so a new size, but stays
            # where the old size put it until it is placed again.
            self._refresh_hover()

    def sizeHint(self) -> QSize:  # Qt spells this in camelCase.
        """As wide as the plot asks, and `theme.WASH_IN_CHART_HEIGHT` tall.

        In a View too short for this height the chart shrinks to
        `theme.WASH_IN_CHART_LEAST_HEIGHT`, or to the tallest hover box's
        height where a large font makes that the taller
        (`_HoverReadout.hold_the_tallest_box`).
        """

        return _preferred_size(self._plot, WASH_IN_CHART_HEIGHT)

    def plot_width_px(self) -> float:
        """The width of the plot area in logical pixels, for `assemble_chart_frame`.

        The dashboard samples one frame at the widest of its charts' widths,
        so that no chart draws a chord wider than a pixel (`PL-GS3R`).
        """

        return _plot_width_px(self._plot)

    @property
    def owes_a_frame(self) -> bool:
        """Whether this plot is now wider than the width its last frame was sampled for.

        The dashboard's render tick reads this property from every chart. So
        a chart whose Area a reader widens is redrawn on the next tick, even
        when the window kept its size (`resample_owed`, `PL-9LNF`).
        """

        return resample_owed(self._frame, self.plot_width_px())

    def drawn_stretches(self, run: int) -> tuple[tuple[tuple[float, float], ...], ...]:
        """Each visible stretch of one run, as its drawn (time, ratio) points."""

        drawn = []

        for curve in self._runs[run].stretches:
            if not curve.isVisible():
                continue

            times, ratios = curve.getData()
            drawn.append(tuple((float(t), float(r)) for t, r in zip(times, ratios, strict=True)))

        return tuple(drawn)

    def preview_stretches(self, run: int) -> tuple[tuple[tuple[float, float], ...], ...]:
        """Each visible predicted stretch of one run, as its drawn (time, ratio) points."""

        drawn = []

        for curve in self._runs[run].preview_stretches:
            if not curve.isVisible():
                continue

            times, ratios = curve.getData()
            drawn.append(tuple((float(t), float(r)) for t, r in zip(times, ratios, strict=True)))

        return tuple(drawn)

    def preview_pen(self, run: int) -> QPen:
        """The pen one run's predicted stretches are drawn with, as specified (see `drawn_pen`)."""

        return self._pens.specified(self._runs[run].preview_stretches[0])

    def preview_region(self, run: int) -> tuple[float, float] | None:
        """Where one run's preview region is drawn, in simulated seconds, or None if hidden."""

        return self._runs[run].preview.shown_region()

    def preview_label(self, run: int) -> str | None:
        """What one run's preview label says, or None while it is hidden."""

        return self._runs[run].preview.shown_label()

    def terminus_points(self, run: int) -> tuple[tuple[float, float], ...]:
        """Where one run's terminus dots are drawn, as (time, ratio)."""

        times, ratios = self._runs[run].termini.getData()

        return tuple((float(t), float(r)) for t, r in zip(times, ratios, strict=True))

    def preview_terminus_points(self, run: int) -> tuple[tuple[float, float], ...]:
        """Where one run's predicted stretches end in a dot, as (time, ratio)."""

        times, ratios = self._runs[run].preview_termini.getData()

        return tuple((float(t), float(r)) for t, r in zip(times, ratios, strict=True))

    def drawn_pen(self, run: int) -> QPen:
        """The pen one run's stretches are drawn with, as specified.

        The pen is the one the first stretch was last given. Its width is in
        device-independent pixels, and the stretch draws it at that width on
        any screen, through `on_screen`.
        """

        return self._pens.specified(self._runs[run].stretches[0])

    def branch_point_time(self, run: int) -> float | None:
        """Where one run's fork is marked, in simulated seconds, or None if unmarked."""

        mark = self._runs[run].branch_point

        return float(mark.value()) if mark.isVisible() else None

    def control_mark_times(self, run: int) -> tuple[float, ...]:
        """Where one run's visible control marks are, in simulated seconds."""

        return tuple(float(mark.value()) for mark in self._runs[run].marks if mark.isVisible())

    def equilibrium_line(self) -> float:
        """Where the equilibrium line is drawn, as a ratio."""

        return float(self._equilibrium_line.value())

    def axis_ticks(self, name: str) -> tuple[tuple[float, str], ...]:
        """The ticks one axis is labelled at, as (position, label)."""

        return _axis_ticks(self._plot.getPlotItem().getAxis(name))

    def tick_label_rects(self, name: str) -> tuple[tuple[str, QRectF], ...]:
        """Each tick label one axis paints, with its box in the pixels of `painted`."""

        return _tick_label_rects(self._plot, name)

    def axis_titles(self) -> tuple[str, ...]:
        """The titles of the plot's axes, so a walk over the whole interface finds them."""

        return _axis_titles(self._plot, self._time_title.words)

    def show_time_window(self, window: str) -> None:
        """Write the window the plot shows into the time axis's title.

        Args:
            window: What `dashboard_frame.time_axis_caption` says of the
                frame just drawn.
        """

        self._time_title.show(window)

    @property
    def time_axis_title(self) -> str:
        """The time axis's title on one line, however the axis breaks it."""

        return self._time_title.words

    @property
    def time_axis_lines(self) -> tuple[str, ...]:
        """The time axis's title as the axis draws it, one line at a time."""

        return self._time_title.lines

    @property
    def time_axis_title_offset_px(self) -> float:
        """How far the title's centre is from the time axis's centre, in px."""

        return self._time_title.offset_px

    def painted(self) -> QImage:
        """The plot as painted, so a test can check what is on screen."""

        return _render(self)

    def plot_pixel(self, time_s: float, ratio: float) -> tuple[int, int]:
        """Which pixel of `painted` a plot position lands on."""

        return _plot_pixel(self._plot, time_s, ratio)

    def plot_area(self) -> QRectF:
        """The plot inside its axes, in the pixels of `painted`, which holds any box that fits."""

        return _plot_area(self._plot)

    def readout_at(self, time_s: float, ratio: float) -> str | None:
        """What the hover would say for a pointer at this plot position.

        This works as `ConcentrationChart.readout_at` does, on the ratio axis.

        Args:
            time_s: The pointer's position along the time axis.
            ratio: The pointer's position on the ratio axis.

        Returns:
            The three-line readout, or `None`.
        """

        target = self._target_at(time_s, ratio)

        return None if target is None else target.readout

    def _target_at(self, time_s: float, ratio: float) -> HoverTarget | None:
        if self._frame is None:
            return None

        seconds_per_pixel, ratio_per_pixel = self._plot.getPlotItem().getViewBox().viewPixelSize()

        return nearest_wash_in_point(
            self._frame, time_s, ratio, seconds_per_pixel, ratio_per_pixel, HOVER_RADIUS_PIXELS
        )

    def _on_pointer(self, scene_position: QPointF | None) -> None:
        self._hover.move_to(scene_position)
        self._refresh_hover()

    def _refresh_hover(self) -> None:
        position = self._hover.scene_position()
        view_box = self._plot.getPlotItem().getViewBox()

        if (
            self._frame is None
            or position is None
            or not view_box.sceneBoundingRect().contains(position)
        ):
            self._hover.hide()
            return

        point = view_box.mapSceneToView(position)
        target = self._target_at(point.x(), point.y())

        if target is None:
            self._hover.hide()
        else:
            self._hover.show(target, (self._frame.start_s, self._frame.stop_s))

    def hover_text(self) -> str | None:
        """What the hover box currently shows, or `None` while it is hidden."""

        return self._hover.shown_text()

    def hover_box(self) -> QRectF | None:
        """Where the hover box is in the pixels of `painted`, or `None` while it is hidden."""

        return self._hover.shown_box()


def _axis_titles(plot: Any, time_title: str) -> tuple[str, ...]:
    """The non-empty axis titles of a plot, in left, bottom, right order.

    The time axis's title is given on one line, as `_TimeAxisTitle.words`
    states it. The axis itself may hold it broken across lines.
    """

    item = plot.getPlotItem()
    left, right = (str(item.getAxis(name).labelText) for name in ("left", "right"))
    return tuple(title for title in (left, time_title, right) if title)


class _TimeAxisTitle:
    """The title of a plot's time axis, which names the axis and states the window shown.

    The window had a line of its own above the plot, which took the plot's
    height at 1366 by 768 (`PL-K4CZ`). The title keeps to one line where the
    axis is wide enough. On a narrower axis it breaks after a comma, as the
    MAC-awake legend entry does, so a span never loses its unit. The title is
    broken again whenever the axis changes width.

    The title stops listening to the axis when the plot widget that holds the
    axis is destroyed (`PL-9RZJ`). Qt can report a geometry change on the axis
    while the axis itself is being deleted, after its Python side is gone. A
    title still listening then raised "Internal C++ object (AxisItem) already
    deleted", once for each such report. The plot widget's `destroyed` signal
    comes before its scene, and so the axis, is deleted.

    Args:
        item: The plot whose bottom axis is the time axis.
        plot: The widget that draws `item`, whose deletion deletes the axis.
    """

    def __init__(self, item: Any, plot: QWidget) -> None:
        self._item = item
        self._axis = item.getAxis("bottom")
        self._words = TIME_AXIS_TITLE
        self._lines: tuple[str, ...] = ()
        self._width = -1.0
        self._axis.geometryChanged.connect(self._refit)
        plot.destroyed.connect(self._stop_refitting)
        self._write()

    @property
    def words(self) -> str:
        """The title on one line."""

        return self._words

    @property
    def lines(self) -> tuple[str, ...]:
        """The title as the axis draws it, one line at a time."""

        return self._lines

    @property
    def offset_px(self) -> float:
        """How far the title's centre is from the axis's centre, in px."""

        label = self._axis.label
        centre = label.pos().x() + label.boundingRect().width() / 2

        return float(centre - self._axis.size().width() / 2)

    def clear(self) -> None:
        """Name the axis alone, with no window, as before the first frame."""

        if self._words != TIME_AXIS_TITLE:
            self._words = TIME_AXIS_TITLE
            self._write()

    def show(self, window: str) -> None:
        """Name the axis and state `window` after the name."""

        words = TIME_AXIS_TITLE_TEMPLATE.format(window=window)

        if words != self._words:
            self._words = words
            self._write()

    def _stop_refitting(self) -> None:
        self._axis.geometryChanged.disconnect(self._refit)

    def _refit(self) -> None:
        # Writing the title changes the axis's height and never its width, so
        # this runs once for each new width and does not loop.
        if self._axis.size().width() != self._width:
            self._write()

    def _write(self) -> None:
        self._width = self._axis.size().width()
        label = self._axis.label
        room = int(self._width - 2 * label.document().documentMargin())
        self._lines = tuple(clause_lines(self._words, QFontMetrics(label.font()), room))
        title = "<br>".join(escape(line) for line in self._lines)
        self._item.setLabel("bottom", title, color=MUTED)
        # pyqtgraph centres the title only when the axis is resized, and a new
        # title with as many lines as the old one does not resize it. The
        # axis's own resize handler places the title again.
        self._axis.resizeEvent()


def _clear_axes(
    item: Any,
    grid: _GridLines,
    title: _TimeAxisTitle,
    value_axes: Sequence[str],
    value_rules: Sequence[float],
) -> None:
    """Take the labels and gridlines of a withheld frame off a plot's axes.

    The time axis always loses its labels, its gridlines and the window in its
    title, because they describe the window of the frame that was withheld.

    Args:
        item: The plot.
        grid: The plot's gridlines.
        title: The time axis's title.
        value_axes: The names of the value axes whose labels came from the
            withheld frame, such as "left" and "right". Each loses its labels.
        value_rules: Where the horizontal gridlines stay, because no frame
            placed them. Every other horizontal gridline is hidden.
    """

    item.getAxis("bottom").setTicks([[]])

    for name in value_axes:
        item.getAxis(name).setTicks([[]])

    grid.place((), value_rules)
    title.clear()


def _axis_ticks(axis: Any) -> tuple[tuple[float, str], ...]:
    """The major ticks an axis was given, as (position, label)."""

    ticks = axis._tickLevels

    if not ticks:
        return ()

    return tuple((float(position), str(label)) for position, label in ticks[0])


def _tick_label_rects(plot: Any, name: str) -> tuple[tuple[str, QRectF], ...]:
    """Each tick label one axis paints, with its box in the widget's pixels."""

    axis = plot.getPlotItem().getAxis(name)
    image = QImage(1, 1, QImage.Format.Format_ARGB32)
    painter = QPainter(image)
    painter.setFont(plot.font())
    try:
        _, _, texts = axis.generateDrawSpecs(painter)
    finally:
        painter.end()
    transform = plot.viewportTransform()
    return tuple(
        (str(text), QRectF(transform.mapRect(axis.mapRectToScene(rect)))) for rect, _, text in texts
    )


def _render(widget: QWidget) -> QImage:
    """The widget as it is painted, for a rendering check."""

    return widget.grab().toImage()


def _preferred_size(plot: Any, height_px: int) -> QSize:
    """The size a chart asks its layout for: the plot's own width and the theme's height.

    The height comes from the theme rather than the toolkit. A graphics view
    asks for 480 px on its own, which is no chart's height. That request made
    the page a quarter of a screen taller than the page it replaced. The plot still
    grows past this height, because it expands in both directions, so a
    taller window lengthens the traces. The plot's minimum height is a smaller
    theme height, such as `CHART_LEAST_HEIGHT`, unless the tallest hover box
    is taller (`_HoverReadout.hold_the_tallest_box`).
    """

    return QSize(plot.sizeHint().width(), height_px)


def _plot_width_px(plot: Any) -> float:
    """The width of `plot`'s plot area in logical pixels, for `chart_columns`.

    The width is the view box's rather than the widget's. The axes and their
    labels take the rest of the widget, and the time axis spans the view
    box. The width is read from the geometry that Qt laid out. So before a
    chart is shown, this returns whatever default size the toolkit gave the
    unshown widget. That is why the caller draws its first frame after the
    chart is shown, and why `chart_columns` applies a minimum to the width it
    is handed.
    """

    return float(plot.getPlotItem().getViewBox().width())


def _plot_pixel(plot: Any, x: float, y: float) -> tuple[int, int]:
    """The pixel of `plot` a plot position lands on, for a rendering check.

    The plot widget fills its chart widget edge to edge with no margins, so
    the pixel in the plot is the pixel in the widget that owns it.
    """

    scene_point = plot.getPlotItem().getViewBox().mapViewToScene(QPointF(x, y))
    view_point = plot.mapFromScene(scene_point)

    return round(view_point.x()), round(view_point.y())


def _plot_area(plot: Any) -> QRectF:
    """The view box of `plot`, which is the plot inside its axes, in its widget's pixels.

    These are also the pixels of the chart that owns the plot, for the reason
    that `_plot_pixel` gives.
    """

    return QRectF(
        plot.viewportTransform().mapRect(plot.getPlotItem().getViewBox().sceneBoundingRect())
    )


class _LineSwatch(QWidget):
    """A legend mark drawn with the same pen that its series is drawn with.

    The mark is horizontal for a trace or a reference line. It is vertical
    for a control mark or a fork mark, because those marks are vertical on
    the chart, and no trace or reference there is. The swatch's size never changes with
    what it shows. It sits beside a control that a reader clicks repeatedly,
    and a row that reflowed under the cursor would move the next box out from
    under it. So an *empty* swatch, for a trace that is hidden, paints
    nothing at the same size.
    """

    def __init__(self, pen: QPen, width: int, height: int, *, vertical: bool = False) -> None:
        super().__init__()
        self._pen = pen
        self._vertical = vertical
        self._filled = True
        self.setFixedSize(width, height)

    def set_filled(self, filled: bool) -> None:
        """Draw the mark, or draw nothing at the same size."""

        self._filled = filled
        self.update()

    def set_pen(self, pen: QPen) -> None:
        """Paint this mark with another pen, for a swatch whose series changes.

        The compare-mode row's entries are a fixed pool that stands for
        whichever traces are drawn. So a swatch has to be able to take the
        pen of the curve it currently describes. The size never changes with
        the pen, for the reason the class docstring gives.
        """

        self._pen = pen
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # Qt spells this in camelCase.
        del event

        if not self._filled:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # The ratio is read from the device the paint engine draws on, which
        # is the screen's backing store or, for a grab, the image. The
        # painter's own `device()` is this widget even during a grab, so it
        # would give the screen's ratio for an image at another ratio.
        painter.setPen(
            on_screen(self._pen, painter.paintEngine().paintDevice().devicePixelRatioF())
        )

        if self._vertical:
            x = self.width() / 2.0
            painter.drawLine(QPointF(x, 0.0), QPointF(x, float(self.height())))
        else:
            y = self.height() / 2.0
            painter.drawLine(QPointF(0.0, y), QPointF(float(self.width()), y))

        painter.end()


class _BandSwatch(QWidget):
    """The MAC-awake band's legend mark: a fill with a line along both edges, as on the chart.

    A band's extent is exactly what distinguishes it from a line. So this is
    the one legend mark that is not drawn at the shared swatch size. It has a
    line along both edges, because a swatch with a line along one edge would
    teach the reader the wrong mark for the band on the chart (`PL-90Y6`).
    """

    def __init__(self) -> None:
        super().__init__()
        fill = QColor(MAC_AWAKE_BAND_COLOR)
        fill.setAlphaF(MAC_AWAKE_BAND_FILL_OPACITY)
        self._fill = QBrush(fill)
        self._edge_pen: QPen = pg.mkPen(
            MAC_AWAKE_BAND_COLOR, width=MAC_AWAKE_BAND_EDGE_STROKE_WIDTH
        )
        self.setFixedSize(BAND_SWATCH_WIDTH, BAND_SWATCH_HEIGHT)

    @property
    def edge_pen(self) -> QPen:
        """The pen that both edges are drawn with."""

        return self._edge_pen

    @property
    def fill_brush(self) -> QBrush:
        """The brush the band between the edges is filled with."""

        return self._fill

    def paintEvent(self, event: QPaintEvent) -> None:  # Qt spells this in camelCase.
        del event

        painter = QPainter(self)
        painter.fillRect(self.rect(), self._fill)
        painter.setPen(
            on_screen(self._edge_pen, painter.paintEngine().paintDevice().devicePixelRatioF())
        )
        width = float(self.width())
        inset = MAC_AWAKE_BAND_EDGE_STROKE_WIDTH / 2.0
        painter.drawLine(QPointF(0.0, inset), QPointF(width, inset))
        painter.drawLine(QPointF(0.0, self.height() - inset), QPointF(width, self.height() - inset))
        painter.end()


def _legend_row(caption: str | None, entries: Sequence[tuple[QWidget, QWidget]]) -> FlowLayout:
    """One legend row: a caption, where the row has one, then swatch-and-label pairs.

    The row wraps, as the Flet build's legend rows did. So the entries reflow
    under a narrow chart, rather than forcing the chart column to be as wide
    as all of them together. The caption is laid out first and the entries
    follow it. Each entry is a swatch-and-label pair that is never split, and
    a pair that would run past the right edge starts the next line.
    """

    row = FlowLayout(horizontal_spacing=LEGEND_ENTRY_SPACING, vertical_spacing=LEGEND_LINE_SPACING)

    if caption is not None:
        row.addWidget(legend_caption(caption))

    for swatch, label in entries:
        row.addWidget(_legend_entry(swatch, label))

    return row


class _PooledEntry:
    """One legend entry whose swatch and words are rewritten rather than rebuilt.

    The compare-mode rows name every curve actually on the plot. Which curves
    those are changes with the reader's selection and with how many runs are
    drawn. Instead of rebuilding a row on every change, the legend writes to
    and hides the entries of a fixed pool. The pool has room for the most
    entries that can be shown, which is `COMPARED_COMPARTMENT_CAP`
    compartments times `MAX_DISPLAYED_RUNS` runs. The plots keep fixed pools
    of marks and stretches for the same reason.
    """

    def __init__(self, row: FlowLayout) -> None:
        self.swatch = _LineSwatch(_control_mark_pen(), LEGEND_SWATCH_WIDTH, LEGEND_SWATCH_HEIGHT)
        self.label = _legend_label("")
        self.widget = _legend_entry(self.swatch, self.label)
        self.widget.setHidden(True)
        row.addWidget(self.widget)

    def show(self, pen: QPen, text: str) -> None:
        """Describe this curve, with its own pen and the words that name it."""

        self.swatch.set_pen(pen)
        self.label.setText(text)
        self.widget.setHidden(False)

    def hide(self) -> None:
        """Show nothing, and take no space."""

        self.widget.setHidden(True)


def legend_caption(text: str) -> QLabel:
    """A legend row's caption, in the muted colour that every row's caption uses.

    The caption has its own constructor because a row that has to hide its
    caption needs to keep the widget, rather than find it again in the
    layout. The compare row is such a row: it hides entirely when a single
    run is drawn.
    """

    label = QLabel(text)
    label.setStyleSheet(foreground_stylesheet(MUTED))

    return label


def _legend_entry(swatch: QWidget, label: QWidget) -> QWidget:
    """A swatch beside its words, as one item that a legend row wraps as a whole."""

    entry = QWidget()
    pair = QHBoxLayout(entry)
    pair.setContentsMargins(0, 0, 0, 0)
    pair.setSpacing(LEGEND_SWATCH_SPACING)
    pair.addWidget(swatch, alignment=Qt.AlignmentFlag.AlignVCenter)
    pair.addWidget(label, alignment=Qt.AlignmentFlag.AlignVCenter)

    return entry


class TimeBaseSelector(SelectorComboBox):
    """The time-base control, which offers "Fit run" and the selectable widths.

    The window belongs to the chart View that holds this control
    (`PL-L59K`), not to the control. `show_time_base` hands the control the
    window that the chart last drew, and the control shows it. When a reader
    picks another window, the control asks for it through
    `time_base_requested`. So when a frame fails, the control still names the
    window that is on the plot (`PL-G3K7`).

    Attributes:
        time_base_requested: Emitted with the `ChartTimeBase` a reader
            picked, or None for "Fit run". Never emitted by `show_time_base`.
    """

    time_base_requested = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(TIME_BASE_SELECTOR_WIDTH)
        self.setStyleSheet(selector_stylesheet())
        self.addItem(FIT_RUN_LABEL, userData=FIT_RUN_KEY)

        for time_base in SELECTABLE_TIME_BASES:
            self.addItem(format_time_base(time_base.span_s), userData=str(time_base.span_s))

        self._showing = False
        self.currentIndexChanged.connect(self._handle_pick)

    def show_time_base(self, time_base: ChartTimeBase | None) -> None:
        """Show this time base, or "Fit run" for None, without treating it as a request.

        Raises:
            ValueError: `time_base` is not one this control offers. If the
                two tables disagree, that is a defect to report, not a width
                to show as something else.
        """

        key = FIT_RUN_KEY if time_base is None else str(time_base.span_s)
        index = self.findData(key)

        if index < 0:
            raise ValueError(f"the time-base control does not offer a {key} s width")

        self._showing = True

        try:
            self.setCurrentIndex(index)
        finally:
            self._showing = False

    def _handle_pick(self, index: int) -> None:
        """Ask for the width the reader picked.

        Raises:
            ValueError: The control offers a width not on the ladder
                (`time_base_for_span`).
        """

        key = self.itemData(index)

        if self._showing or key is None:
            return

        picked = None if key == FIT_RUN_KEY else time_base_for_span(float(key))
        self.time_base_requested.emit(picked)


class ChartCeilingSelector(SelectorComboBox):
    """The control that sets the top of the MAC axis, from `ChartCeiling`.

    It works as `TimeBaseSelector` does. Every concentration chart View and
    the compartment schematic View holds one. The top is the reader's
    preference, shared by all of them (`PL-7LZ7`). The View hands the control
    the top it drew through `show_ceiling`, and a reader's pick is asked for
    through `ceiling_requested`. So when a frame fails, the control still names
    the top that is on the plot.

    A pick is read from Qt's `activated` signal, which a reader's choice sends
    even when it is the top already shown, and which `setCurrentIndex` never
    sends. So a reader who is told that a saved top was refused can keep
    3 xMAC by picking it (`preferences.chart_ceiling_notice`). The time base
    selector reads `currentIndexChanged`, because picking its shown base
    again has nothing to replace.

    Attributes:
        ceiling_requested: Emitted with the `ChartCeiling` a reader picked.
            Never emitted by `show_ceiling`.
    """

    ceiling_requested = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(CHART_CEILING_SELECTOR_WIDTH)
        self.setStyleSheet(selector_stylesheet())

        for ceiling in ChartCeiling:
            self.addItem(ceiling.label, userData=ceiling.name)

        self.activated.connect(self._handle_pick)

    def show_ceiling(self, ceiling: ChartCeiling) -> None:
        """Show this top without treating it as a request."""

        self.setCurrentIndex(self.findData(ceiling.name))

    def _handle_pick(self, index: int) -> None:
        key = self.itemData(index)

        if key is None:
            return

        self.ceiling_requested.emit(ChartCeiling[key])


class TraceLegend(QWidget):
    """This widget shows the chart's four legend rows, and its compartment row is also a control.

    The rows are the references, the compartments, the compared runs and the
    run record. The compared-runs row is empty, and takes no height, when a
    single run is drawn.

    **The legend shows a compartment selection and asks for changes to it,
    but it does not own one** (`PL-VN6M`). The selection is a
    `CompartmentSelection` that its owner hands to `show_selection`. The
    owner is the dashboard, and the selection is the same value that the
    plot's frame is assembled from. So a layout that closes this widget, or
    shows a second one, leaves the selection as it was. A reader's click is
    emitted as `compartment_requested`, and the boxes move when the owner
    responds.

    Every compartment entry, meaning its box, its swatch and its label, is
    written from that one value. That is what makes the legend's agreement
    with the plot a property of the code rather than of somebody's care. Two
    lists of the same six compartments is exactly how a legend comes to name
    a line the chart is not drawing. So no box keeps a state it was not
    handed, and a click that nobody responds to is undone.

    Each swatch is painted with the pen the chart draws that series with. So
    a dashed trace has a dashed swatch (`PL-THXF`), and the band has a band
    as its swatch. The references and the control mark get their own rows
    rather than joining the six compartments. They are not compartments, and
    a single row would invite reading them as a seventh and an eighth trace.

    An entry stays on screen when its trace is off, and it keeps the words
    that describe its line style (`PL-YTX9`). The unchecked box and the empty
    swatch already say that the line is not drawn. Those are two channels,
    and neither of them is colour. The words describe what switching the
    trace on will draw.
    """

    compartment_requested = Signal(object, bool)
    """Emitted when a reader shows or hides a compartment: the compartment, and whether to draw it.

    This is a request rather than a change. The boxes move when the
    selection's owner responds through `show_selection`. The signal is never
    emitted for a selection that arrives that way, even one that unchecks a
    box. That change is the owner's, and so is drawing the frame that the
    change requires, once the owner's run set is complete (`PL-B1R9`).
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._boxes: dict[RecordedQuantity, QCheckBox] = {}
        self._swatches: dict[RecordedQuantity, _LineSwatch] = {}
        self._band_swatch = _BandSwatch()
        compartments: list[tuple[QWidget, QWidget]] = []

        for style in COMPARTMENT_TRACES:
            swatch = _LineSwatch(
                trace_pen(style),
                LEGEND_SWATCH_WIDTH,
                max(LEGEND_SWATCH_HEIGHT, ceil(style.stroke_width)),
            )
            box = QCheckBox(trace_legend_label(style))
            box.setChecked(True)
            box.setStyleSheet(foreground_stylesheet(INK))
            # The stylesheet sets the label's colour. The *indicator* is drawn
            # from the palette's `Base` and `Text` roles, which the stylesheet
            # does not affect. So under a dark host appearance, the box was a
            # dark square, and its tick was INK on near-black at a contrast of
            # 1.35:1 (`PL-7W9N`).
            declare_interface_colours(box)
            box.toggled.connect(
                lambda checked, quantity=style.quantity: self._on_toggled(quantity, checked)
            )
            self._boxes[style.quantity] = box
            self._swatches[style.quantity] = swatch
            compartments.append((swatch, box))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(LEGEND_LINE_SPACING)
        # Each reference names the compartment it is read against.
        # `docs/INTERFACE.md` § "Interface boundary" requires that of a
        # reference, in the same passage that exempts a reference from the
        # drawn-trace rule. The band names vessel-rich, not alveolar. The
        # model has no effect-site compartment, and it defines the arterial
        # fraction as the alveolar one. So the alveolar trace is the fastest
        # patient trace on the chart, and the furthest from where
        # responsiveness returns. The 1 MAC line names alveolar, because MAC is defined for
        # the alveolar concentration.
        #
        # Each entry also states its reference's value, from `show_references`.
        # The values had a line each above the legend, which repeated the
        # entries' names and took the plot's height at 1366 by 768
        # (`PL-K4CZ`). The row comes first in the legend, so where the box
        # above the plot is squeezed to its first two rows, the 1 MAC value
        # is still on screen, as it was on its own line. Its 1 MAC entry
        # comes first, because the band's fraction is a fraction of that
        # 1 MAC. The band's entry is the longest in the legend, so its words
        # wrap in a narrow View rather than set the View's least width.
        self._one_mac_label = _legend_label(
            ONE_MAC_LINE_LEGEND_TEMPLATE.format(reference=ONE_MAC_LINE_LEGEND_NAME)
        )
        self._band_label = ClauseWrappingLabel(
            MAC_AWAKE_BAND_LEGEND_TEMPLATE.format(reference=MAC_AWAKE_BAND_LEGEND_NAME), color=INK
        )
        layout.addLayout(
            _legend_row(
                "Clinical references:",
                [
                    (
                        _LineSwatch(
                            dashed_pen(
                                ONE_MAC_LINE_COLOR,
                                ONE_MAC_LINE_STROKE_WIDTH,
                                ONE_MAC_LINE_DASH_PATTERN,
                            ),
                            LEGEND_SWATCH_WIDTH,
                            LEGEND_SWATCH_HEIGHT,
                        ),
                        self._one_mac_label,
                    ),
                    (self._band_swatch, self._band_label),
                ],
            )
        )
        layout.addLayout(_legend_row("Compartments:", compartments))
        # The compare row has one entry per curve actually drawn, and each
        # entry names both the compartment and the run. Once a curve stands
        # for two things, a legend that names only one of them identifies
        # nothing. The row is empty and takes no height when a single run is
        # drawn, because the row above already names every drawn curve
        # completely.
        self._compared_row = _legend_row(None, [])
        self._compared_caption = legend_caption(COMPARED_TRACE_LEGEND_CAPTION)
        self._compared_row.addWidget(self._compared_caption)
        self._compared_entries = [
            _PooledEntry(self._compared_row)
            for _ in range(COMPARED_COMPARTMENT_CAP * MAX_DISPLAYED_RUNS)
        ]
        layout.addLayout(self._compared_row)
        # A third row, because a control mark is neither of the two kinds
        # above it. A compartment trace is a modelled quantity, and a
        # clinical reference is a published constant. A control mark is a
        # record of something the *user* did.
        self._branch_swatch = _LineSwatch(
            _branch_point_pen(),
            CONTROL_MARK_SWATCH_WIDTH,
            CONTROL_MARK_SWATCH_HEIGHT,
            vertical=True,
        )
        self._branch_label = _legend_label(BRANCH_POINT_LEGEND_LABEL)
        self._branch_entry = _legend_entry(self._branch_swatch, self._branch_label)
        self._branch_entry.setHidden(True)
        run_record = _legend_row("Run record:", [_control_mark_entry()])
        run_record.addWidget(self._branch_entry)
        layout.addLayout(run_record)
        # The selection last handed to `show_selection`. It is kept so the
        # boxes can be written back to it after a request that nobody
        # responds to. It is the owner's value as last shown, and nothing
        # here changes it.
        self._selection: CompartmentSelection = INITIAL_COMPARTMENT_SELECTION
        # True while the boxes are being written from a selection, so a box
        # that toggles during that pass is repainted and not taken for a
        # click.
        self._showing = False
        # What each drawn run is called, from the last `show_run_names`.
        self._run_names: tuple[str, ...] = ()
        self.name_boxes(None)
        self.show_selection(INITIAL_COMPARTMENT_SELECTION)

    def name_boxes(self, which: str | None) -> None:
        """Name each compartment's box for a screen reader, adding `which` where it is not None.

        `which` names the Area that holds the chart, where another Area shows
        a concentration chart too, such as "Concentrations 2" (`PL-XV64`).
        Only a name that differs is written, so a screen reader is sent no
        change while the Area keeps its name.
        """

        for style in COMPARTMENT_TRACES:
            box = self._boxes[style.quantity]
            name = control_name(
                TRACE_TOGGLE_ACCESSIBLE_NAME_TEMPLATE.format(label=style.label), which
            )

            if box.accessibleName() != name:
                box.setAccessibleName(name)

    @property
    def shown(self) -> tuple[RecordedQuantity, ...]:
        """The compartments currently checked, in table order.

        This is what the boxes show, for a check that they show the selection
        they were handed. Nothing reads the selection back from here, because
        the dashboard draws from its own (`PL-VN6M`).
        """

        return tuple(
            style.quantity
            for style in COMPARTMENT_TRACES
            if self._boxes[style.quantity].isChecked()
        )

    def show_selection(self, selection: CompartmentSelection) -> None:
        """Show this selection: check exactly its compartments, and name its runs' curves.

        This is how the owner responds to `compartment_requested`, and also
        how it tells the legend that the run set has changed. The boxes are
        written from `selection.shown`, which is exactly what a frame
        assembled from the same selection draws. So the boxes a reader sees
        checked are the curves on the plot.

        **It announces nothing, even when it unchecks a box** (`PL-B1R9`).
        The change is the owner's, made while it changes the selection or the
        run set, and the owner already has to draw the frame that shows the
        change. When the change was announced from here, the cap that a
        second run brings drew that frame too early. It drew it from inside
        the dashboard's method that renamed the runs, before the wash-in legend or either
        run had been told there were two runs. The fork that caused the cap
        then drew its own frame.

        Args:
            selection: The selection to show.
        """

        self._selection = selection
        self._check_exactly(selection.shown)
        self._branch_entry.setHidden(selection.run_count <= 1)
        self._refresh_compared_row()

    def show_run_names(self, names: tuple[str, ...]) -> None:
        """Name the runs' curves as the runs' own panels name them, in drawing order.

        This is how the dashboard responds to a frame drawn over a new run
        set. The dashboard calls it before it hands over the selection that
        the frame was drawn from. So each compared entry names its run by the
        run's identity rather than by where it is drawn (`PL-7Z84`).

        Args:
            names: What each drawn run is called, from `run_label`.
        """

        self._run_names = names
        self._refresh_compared_row()

    def _check_exactly(self, shown: tuple[RecordedQuantity, ...]) -> None:
        """Check exactly these compartments' boxes, without treating the change as a request."""

        showing = self._showing
        self._showing = True

        try:
            for quantity, box in self._boxes.items():
                box.setChecked(quantity in shown)
        finally:
            self._showing = showing

    @property
    def _run_count(self) -> RunCount:
        """How many runs are drawn for the selection that this legend shows."""

        return self._selection.run_count

    def set_compartment_shown(self, quantity: RecordedQuantity, shown: bool) -> None:
        """Show or hide one compartment, by the route a reader's click takes through the legend.

        That makes it a request. The box moves, `compartment_requested` is
        emitted, and the box ends up showing what the selection's owner
        responds with. Where nobody responds, the box ends up showing what it
        showed before.

        Args:
            quantity: Which compartment.
            shown: Whether to draw it.

        Raises:
            KeyError: If `quantity` is not a compartment on this chart.
        """

        self._boxes[quantity].setChecked(shown)

    def swatch_pen(self, quantity: RecordedQuantity) -> QPen:
        """The pen one compartment's swatch is painted with."""

        return self._swatches[quantity]._pen

    @property
    def compared_marks(self) -> tuple[LegendMark, ...]:
        """The compare row's entries as drawn: each curve's words and its own pen.

        The result is empty when a single run is drawn, because the
        compartment row then already names every drawn curve completely.
        """

        return tuple(
            _drawn_mark(entry.label, entry.swatch)
            for entry in self._compared_entries
            if not entry.widget.isHidden()
        )

    @property
    def branch_mark(self) -> LegendMark | None:
        """The fork's legend entry as it is drawn, or None while it is not shown."""

        if self._branch_entry.isHidden():
            return None

        return _drawn_mark(self._branch_label, self._branch_swatch)

    def _refresh_compared_row(self) -> None:
        """Write one entry per drawn curve, and hide the rest of the pool."""

        drawn = self._selection.shown
        # The entries are drawn only once both counts agree. Between a
        # selection over a new run set and the names of its runs, an entry
        # would otherwise give a curve a name that is not its own.
        named = len(self._run_names) == self._run_count
        entries = (
            []
            if self._run_count <= 1 or not named
            else [
                (
                    run_trace_pen(quantity, RunIndex(index), self._run_count),
                    compared_trace_legend_label(
                        trace_legend_label(trace_style(quantity)), self._run_names[index]
                    ),
                )
                # Grouped by compartment rather than by run, so the two
                # entries a reader compares sit beside each other, exactly
                # as the two curves they name do.
                for quantity in drawn
                for index in range(self._run_count)
            ]
        )
        self._compared_caption.setHidden(not entries)

        for entry, (pen, text) in zip(self._compared_entries, entries, strict=False):
            entry.show(pen, text)

        for entry in self._compared_entries[len(entries) :]:
            entry.hide()

    def show_references(self, one_mac: str, mac_awake: str) -> None:
        """Write each clinical reference's value into its entry.

        Args:
            one_mac: The 1 MAC line's value, as `mac_reference_caption` writes
                it, such as "1 MAC sevoflurane (age 40) = 1.8%".
            mac_awake: The band's fraction, centre and edges, as
                `mac_awake_caption` writes them.
        """

        self._one_mac_label.setText(ONE_MAC_LINE_LEGEND_TEMPLATE.format(reference=one_mac))
        self._band_label.setText(MAC_AWAKE_BAND_LEGEND_TEMPLATE.format(reference=mac_awake))

    @property
    def one_mac_text(self) -> str:
        """The 1 MAC line's entry words, as they are drawn."""

        return self._one_mac_label.text()

    @property
    def band_mark(self) -> BandMark:
        """The MAC-awake band's entry: its words, its edge pen and its fill."""

        return BandMark(
            self._band_label.words(), self._band_swatch.edge_pen, self._band_swatch.fill_brush
        )

    @property
    def band_swatch(self) -> QWidget:
        """The widget the band's mark is painted on, for a rendering check to grab."""

        return self._band_swatch

    def _on_toggled(self, quantity: RecordedQuantity, checked: bool) -> None:
        self._swatches[quantity].set_filled(checked)
        self._boxes[quantity].setStyleSheet(foreground_stylesheet(INK if checked else MUTED))

        # A box written from a selection that this legend was handed also
        # arrives here. It is only repainted, because that change is the
        # owner's and not a request.
        if self._showing:
            return

        self.compartment_requested.emit(quantity, checked)
        # An owner connected directly has responded by now, and its response
        # has already written the boxes, so this call changes nothing. Where
        # nobody responded, the call puts the clicked box back to the
        # selection last shown. Otherwise a box would keep a state that no
        # selection gave it, which is how a legend begins to name a curve the
        # plot is not drawing.
        self._check_exactly(self._selection.shown)


def _control_mark_entry() -> tuple[_LineSwatch, QLabel]:
    """The control mark's legend entry, the same on both legends: a vertical line in its own pen."""

    return (
        _LineSwatch(
            _control_mark_pen(),
            CONTROL_MARK_SWATCH_WIDTH,
            CONTROL_MARK_SWATCH_HEIGHT,
            vertical=True,
        ),
        _legend_label(CONTROL_MARK_LEGEND_LABEL),
    )


@dataclass(frozen=True)
class LegendMark:
    """One legend entry as it is drawn: its words, its pen, and which way its line runs.

    This is what a test reads back from a legend. It lets the test check the
    words and the mark against the plot's own pens without reaching into a
    widget.
    """

    label: str
    pen: QPen
    vertical: bool


@dataclass(frozen=True)
class BandMark:
    """The MAC-awake band's legend entry as it is drawn: its words, its edges and its fill.

    The swatch has a line along both edges and a fill between them, as the
    band on the chart does (`PL-90Y6`). A test reads this back to check the
    swatch against the chart's own mark.
    """

    label: str
    edge_pen: QPen
    fill: QBrush


class WashInLegend(QWidget):
    """The wash-in plot's legend row: the ratio trace, its asymptote, the control mark.

    The legend has one row rather than three, and no caption, because the
    wash-in plot has one trace and one reference. The row is clear without
    captions. It sits under the plot's heading and its two label lines, which
    say what the ratio is and is not (`PL-F9TQ`). Each swatch is painted with
    the pen that the plot draws that mark with. The trace is at its own
    stroke width, the equilibrium line is in its wide dash, and the control
    mark is vertical and finely dashed. So the swatch and the words describe
    the mark in two channels (`PL-THXF`). On screen, a per-run state sentence
    follows this row. The dashboard places that sentence, because it is
    written on each tick from the frame.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        trace_swatch = _LineSwatch(
            _wash_in_pen(),
            LEGEND_SWATCH_WIDTH,
            max(LEGEND_SWATCH_HEIGHT, ceil(WASH_IN_STROKE_WIDTH)),
        )
        equilibrium_swatch = _LineSwatch(
            dashed_pen(
                EQUILIBRIUM_LINE_COLOR, EQUILIBRIUM_LINE_STROKE_WIDTH, EQUILIBRIUM_LINE_DASH_PATTERN
            ),
            LEGEND_SWATCH_WIDTH,
            LEGEND_SWATCH_HEIGHT,
        )
        mark_swatch, mark_label = _control_mark_entry()
        entries: list[tuple[_LineSwatch, QLabel]] = [
            (trace_swatch, _legend_label(WASH_IN_TRACE_LEGEND_LABEL)),
            (equilibrium_swatch, _legend_label(EQUILIBRIUM_LEGEND_LABEL)),
            (mark_swatch, mark_label),
        ]
        self._marks = tuple(_drawn_mark(label, swatch) for swatch, label in entries)
        self._trace_swatch = trace_swatch
        self._trace_label = entries[0][1]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        row = _legend_row(None, entries)
        # This plot draws one trace per run, in one colour and one dash
        # pattern. So the run's width is the only thing that separates two of
        # them, and the row has to say which width is which. A fork entry
        # joins the row for the same reason it joins the chart's legend
        # above.
        self._branch_swatch = _LineSwatch(
            _branch_point_pen(),
            CONTROL_MARK_SWATCH_WIDTH,
            CONTROL_MARK_SWATCH_HEIGHT,
            vertical=True,
        )
        self._branch_label = _legend_label(BRANCH_POINT_LEGEND_LABEL)
        self._branch_entry = _legend_entry(self._branch_swatch, self._branch_label)
        self._branch_entry.setHidden(True)
        row.addWidget(self._branch_entry)
        self._compared_entries = [_PooledEntry(row) for _ in range(MAX_DISPLAYED_RUNS)]
        layout.addLayout(row)
        self._run_names: tuple[str, ...] = ()

    def show_run_names(self, names: tuple[str, ...]) -> None:
        """Tell the legend which runs are drawn, and name each one's trace by its run's name.

        Args:
            names: What each run the dashboard is displaying is called, in
                drawing order, from `run_label` (`PL-7Z84`).

        Raises:
            ValueError: If no run is named (`RunCount`).
        """

        run_count = RunCount(len(names))

        if names == self._run_names:
            return

        self._run_names = names
        comparing = run_count > 1
        # The single entry that names no run is hidden while the per-run
        # entries take its place. Two entries naming the same trace, one of
        # them saying nothing about which run, is the ambiguity that this row
        # is meant to remove.
        self._trace_swatch.setHidden(comparing)
        self._trace_label.setHidden(comparing)
        self._branch_entry.setHidden(not comparing)

        for index, entry in enumerate(self._compared_entries):
            if index < run_count and comparing:
                entry.show(
                    _wash_in_pen(RunIndex(index), run_count),
                    compared_trace_legend_label(WASH_IN_TRACE_LEGEND_LABEL, names[index]),
                )
            else:
                entry.hide()

    @property
    def marks(self) -> tuple[LegendMark, ...]:
        """The three entries in row order, each with the pen its swatch is painted with."""

        return self._marks

    @property
    def compared_marks(self) -> tuple[LegendMark, ...]:
        """One entry per run while more than one is drawn, each in that run's own pen."""

        return tuple(
            _drawn_mark(entry.label, entry.swatch)
            for entry in self._compared_entries
            if not entry.widget.isHidden()
        )

    @property
    def branch_mark(self) -> LegendMark | None:
        """The fork's legend entry as it is drawn, or None while it is not shown."""

        if self._branch_entry.isHidden():
            return None

        return _drawn_mark(self._branch_label, self._branch_swatch)


def _drawn_mark(label: QLabel, swatch: _LineSwatch) -> LegendMark:
    """Read one legend entry back as it is drawn: the label's words and the swatch's pen."""

    return LegendMark(label.text(), swatch._pen, swatch._vertical)


def _legend_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet(foreground_stylesheet(INK))

    return label
