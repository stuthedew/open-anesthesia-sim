"""The concentration chart and the wash-in plot, drawn with pyqtgraph.

This module is the toolkit half of the chart. `app/chart_frame.py` settles,
without a toolkit, everything a frame *claims*: which compartment a curve
shows, where the references are drawn, which instants are drawn, and what a
hover says. This module only moves pyqtgraph items to match a `ChartFrame`.
Nothing here reads simulation state, formats a value, or decides a
coordinate. A widget that computed a number a reader interprets would put a
clinical value outside the coverage of `tests/unit/test_chart_frame.py`,
which is where those claims are tested.

**Items are moved, never rebuilt.** Every curve, mark and reference is built
once and then updated on each frame. The Flet chart reused its point
controls for the same reason (`PL-010`): a frame then costs what it draws
rather than what it constructs. The pools have the sizes that `chart_frame`
states, which are a fixed number of control marks and of wash-in stretches.
An unused member of a pool is hidden, which costs nothing per frame.

**Both axes have gridlines exactly where they have labels, by construction.**
Each axis is given its ticks explicitly, from the frame, and the gridlines
are drawn at the same ticks that the axis is labelled at. So the gridlines and
the labels cannot describe two different scales (`PL-Q4VH`).

**The hover shows a readout whenever the pointer is over a drawn point,
whether the run is playing or paused** (`docs/MODEL.md` § "The chart's hover
readout: what the tooltip may show"). The readout is for the plot's *drawn
points*, which are the states at which the run was evaluated. It is never for
a position between two of them. Its text is the text that `chart_frame`
produces through `app/formatting.py`, and never the text of the chart
library's coordinate formatter. The hover costs work per pointer event rather
than per point, so there is no mode in which to withdraw it and no caption to
write about such a mode. It is not a library default, though.
`pyqtgraph.ScatterPlotItem` ships with `hoverable` off, and a plotted line has
no hover at all, so this module builds the hover rather than inheriting it
(`PL-YVHK`).

**Every colour comes from `app/theme.py`.** This module declares no colour of
its own, so the palette that `tools/contrast_check.py` measures stays the
palette that is drawn.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import ceil
from typing import Any, Final, cast

import pyqtgraph as pg
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
from PySide6.QtGui import QBrush, QColor, QImage, QMouseEvent, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
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
    ChartFrame,
    HoverTarget,
    RunCount,
    RunIndex,
    TraceStyle,
    nearest_trace_point,
    nearest_wash_in_point,
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
    MAC_AWAKE_BAND_LEGEND_LABEL,
    MAX_DISPLAYED_RUNS,
    TRACE_TOGGLE_ACCESSIBLE_NAME_TEMPLATE,
    WASH_IN_TRACE_LEGEND_LABEL,
    compared_trace_legend_label,
    trace_legend_label,
)
from anesthesia_sim.app.display_units import DisplayUnit
from anesthesia_sim.app.formatting import format_chart_time_label, format_time_base
from anesthesia_sim.app.qt_widgets import FlowLayout, declare_interface_colours
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.app.stylesheets import foreground_stylesheet, selector_stylesheet
from anesthesia_sim.app.theme import (
    BAND_SWATCH_HEIGHT,
    BAND_SWATCH_WIDTH,
    BRANCH_POINT_STROKE_WIDTH,
    CHART_HEIGHT,
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
    TIME_BASE_SELECTOR_WIDTH,
    WASH_IN_CHART_HEIGHT,
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
    "MAC_AWAKE_BAND_LEGEND_LABEL",
    "WASH_IN_TRACE_LEGEND_LABEL",
    "BandMark",
    "ConcentrationChart",
    "LegendMark",
    "TraceLegend",
    "WashInChart",
    "WashInLegend",
    "dashed_pen",
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
    """A pen with a dash pattern stated in display pixels.

    Qt states a dash pattern in units of the pen's width. `app/theme.py` and
    `chart_frame.COMPARTMENT_TRACES` state theirs in pixels, which is the unit
    that `docs/MODEL.md` § "The six compartment traces" tabulates. So the
    conversion is made once, here, rather than at each of the seven pens that
    have a pattern. A pattern copied across without the conversion draws every
    dash too long by a factor of the pen's width, which is what the spike did.

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

    return pen


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

    if run_index >= run_count:
        raise ValueError(
            f"run {run_index} is not one of the {run_count} runs on the plot; a trace "
            "is drawn at the width of a run that is being drawn"
        )

    widened = run_count > 1 and run_index == 0
    width = WASH_IN_STROKE_WIDTH + (COMPARED_RUN_WIDTH_STEP if widened else 0)

    return dashed_pen(WASH_IN_COLOR, width, None)


def _control_mark_pen() -> QPen:
    """The pen every control mark is drawn with, on both plots and in both legends."""

    return dashed_pen(CONTROL_MARK_COLOR, CONTROL_MARK_STROKE_WIDTH, CONTROL_MARK_DASH_PATTERN)


def _plot(background: str) -> Any:
    """One plot widget, with the interaction and the furniture every plot here shares.

    A reader cannot pan, zoom or open a menu on the plot. The time base sets
    the window and the axis sets the range. A plot that a reader could drag
    off its labelled range would show a slope that meant something different
    from the slope on the plot beside it.
    """

    plot = pg.PlotWidget(background=background)
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
        axis.setPen(pg.mkPen(GRIDLINE))
        axis.setTextPen(pg.mkPen(MUTED))

    return plot


def _hover_items() -> tuple[Any, Any]:
    """The dot and the text box that a hover shows, hidden until there is a readout."""

    dot = pg.ScatterPlotItem(size=_HOVER_DOT_DIAMETER, pen=None, brush=pg.mkBrush(INK))
    dot.setZValue(_Z_HOVER)
    dot.hide()
    text = pg.TextItem(color=INK, fill=pg.mkBrush(PANEL), border=pg.mkPen(MUTED), anchor=(0, 1))
    text.setZValue(_Z_HOVER)
    text.hide()

    return dot, text


class _GridLines:
    """The plot's gridlines, drawn under everything at the ticks its axes carry.

    Each axis gets one line per tick, from the same tick lists that the axes
    are labelled from. So the gridlines and the labels cannot describe two
    different scales (`PL-Q4VH`). The pools of lines grow to fit the widest
    window drawn, and they never shrink. An unused line is hidden.
    """

    def __init__(self, item: Any) -> None:
        self._item = item
        self._pen = pg.mkPen(GRIDLINE, width=1)
        self._vertical: list[Any] = []
        self._horizontal: list[Any] = []

    def place(self, x_ticks: Sequence[float], y_ticks: Sequence[float]) -> None:
        """Draw gridlines at these positions, and hide the rest of each pool."""

        self._rule(self._vertical, _VERTICAL_LINE_ANGLE_DEG, x_ticks)
        self._rule(self._horizontal, _HORIZONTAL_LINE_ANGLE_DEG, y_ticks)

    def _rule(self, pool: list[Any], angle: int, positions: Sequence[float]) -> None:
        while len(pool) < len(positions):
            line = pg.InfiniteLine(pos=0.0, angle=angle, pen=self._pen, movable=False)
            line.setZValue(_Z_GRIDLINE)
            self._item.addItem(line, ignoreBounds=True)
            pool.append(line)

        _place_marks(pool, positions)


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
    speed the reported value moves as the run does. `docs/MODEL.md` § "When
    it answers" says that this is correct, not a defect to design around. It
    keeps `None` once the pointer has left the plot, so a frame drawn after
    that shows no readout (`PL-LTKL`).
    """

    def __init__(self, plot: Any) -> None:
        self._plot = plot
        self._dot, self._text = _hover_items()
        plot.getPlotItem().addItem(self._dot, ignoreBounds=True)
        plot.getPlotItem().addItem(self._text, ignoreBounds=True)
        self._scene_position: QPointF | None = None
        # A child of the plot, so Qt keeps it for as long as the plot lives.
        self._moves = _PointerMoves(plot)

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
            [reading.time_s for reading in target.readings],
            [reading.value for reading in target.readings],
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
        # (`PL-9BVQ`).
        anchor = target.anchor
        past_middle = anchor.time_s > (x_range[0] + x_range[1]) / 2.0
        below = self._room_above_px(anchor.time_s, anchor.value) < self._box_height_px()
        self._text.setAnchor((1 if past_middle else 0, 0 if below else 1))
        self._text.setPos(anchor.time_s, anchor.value)
        self._dot.show()
        # This uses `setVisible` rather than `show`. `show` goes straight to
        # Qt's own method, and so it skips pyqtgraph's override. That override
        # is what orients the box for the view. A box shown through `show` is
        # oriented only at its next paint, so if it is measured before then it
        # can come out thousands of pixels tall (`PL-J0F7`).
        self._text.setVisible(True)

    def _room_above_px(self, time_s: float, value: float) -> float:
        """Return how many pixels lie between a plot position and the top of the plot."""

        view_box = self._plot.getPlotItem().getViewBox()
        anchor = self._plot.mapFromScene(view_box.mapViewToScene(QPointF(time_s, value)))
        top = self._plot.viewportTransform().mapRect(view_box.sceneBoundingRect()).top()

        return float(anchor.y() - top)

    def _box_height_px(self) -> float:
        """Return the box's height in pixels, for the text it now holds.

        The height is read from the text item's own rectangle, which is in
        pixels at any view scale. It is not read from the box's position in
        the scene, which is only correct once the box has been oriented for
        the view (`PL-J0F7`).
        """

        return float(self._text.boundingRect().height())

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


def _branch_point_mark(item: Any) -> Any:
    """One run's fork mark: hidden, full height, and drawn over the gridlines.

    There is one mark per run rather than one per plot, because a fork
    belongs to the run that started at it. A trunk run, which did not start
    at a fork, simply never shows its mark.
    """

    mark = pg.InfiniteLine(
        pos=0.0, angle=_VERTICAL_LINE_ANGLE_DEG, pen=_branch_point_pen(), movable=False
    )
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


class _RunItems:
    """One run's items on the concentration chart: its curves, its fork, its marks."""

    def __init__(self, item: Any, run_index: RunIndex) -> None:
        self.pens = _RunPens(run_index)
        self.curves: dict[RecordedQuantity, Any] = {}

        for style in COMPARTMENT_TRACES:
            curve = pg.PlotCurveItem(pen=trace_pen(style), antialias=True)
            item.addItem(curve)
            self.curves[style.quantity] = curve

        self.branch_point = _branch_point_mark(item)
        self.marks = _control_mark_pool(item)

    def hide(self) -> None:
        for curve in self.curves.values():
            curve.hide()

        self.branch_point.hide()

        for mark in self.marks:
            mark.hide()


def _control_mark_pool(item: Any) -> list[Any]:
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
        mark = pg.InfiniteLine(pos=0.0, angle=_VERTICAL_LINE_ANGLE_DEG, pen=pen, movable=False)
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


class ConcentrationChart(QWidget):
    """The six compartment traces, both clinical references, both axes, and the marks.

    The chart is built once, and `draw` redraws it on each frame from a
    `ChartFrame` that the dashboard assembles. It keeps nothing about the run
    except the last frame it drew, which the hover reads.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._plot = _plot(PANEL)
        self._plot.setMinimumHeight(CHART_HEIGHT)
        self._plot.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._plot)
        item = self._plot.getPlotItem()
        item.setLabel("left", DisplayUnit.CONCENTRATION.axis_title, color=MUTED)
        item.setLabel("bottom", "simulated time", color=MUTED)
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
            values=(0.0, 0.0),
            orientation="horizontal",
            movable=False,
            brush=pg.mkBrush(band_color),
            pen=pg.mkPen(MAC_AWAKE_BAND_COLOR, width=MAC_AWAKE_BAND_EDGE_STROKE_WIDTH),
        )
        self._band.setZValue(_Z_REFERENCE_BAND)
        item.addItem(self._band, ignoreBounds=True)
        self._one_mac_line = pg.InfiniteLine(
            pos=0.0,
            angle=_HORIZONTAL_LINE_ANGLE_DEG,
            pen=dashed_pen(
                ONE_MAC_LINE_COLOR, ONE_MAC_LINE_STROKE_WIDTH, ONE_MAC_LINE_DASH_PATTERN
            ),
            movable=False,
        )
        self._one_mac_line.setZValue(_Z_REFERENCE_LINE)
        item.addItem(self._one_mac_line, ignoreBounds=True)
        self._grid = _GridLines(item)

        self._runs: list[_RunItems] = []
        self._frame: ChartFrame | None = None
        self._hover = _HoverReadout(self._plot)
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
        # still: 0 to 3 MAC, with a gridline every half MAC, whichever agent
        # is running. The left axis is labelled at exactly the values where
        # it has gridlines. The right axis is labelled at round MAC values
        # over the same range.
        item.setYRange(0.0, frame.axis_top_percent, padding=0)
        item.getAxis("left").setTicks([list(frame.percent_ticks)])
        item.getAxis("right").setTicks([list(frame.mac_ticks)])
        self._grid.place(frame.tick_times_s, [position for position, _ in frame.percent_ticks])
        self._one_mac_line.setPos(frame.one_mac_percent)
        self._band.setRegion(frame.mac_awake_band_percent)

        while len(self._runs) < len(frame.runs):
            self._runs.append(_RunItems(item, RunIndex(len(self._runs))))

        # Each run's items are added to the plot in turn, so a later run is
        # drawn over an earlier one. That order matters and is not
        # incidental. A branch reproduces its parent up to the fork, so before
        # the branch point the two curves coincide exactly. Drawing the
        # narrower second run last is what keeps both visible there
        # (`theme.COMPARED_RUN_WIDTH_STEP`).
        run_count = frame.run_count

        for items, run in zip(self._runs, frame.runs, strict=False):
            repen = items.pens.changed_for(run_count)

            for quantity, curve in items.curves.items():
                if repen:
                    curve.setPen(items.pens.of(quantity, run_count))

                if quantity in frame.visible:
                    # Only the traces that the reader has left shown are
                    # written. A hidden trace costs nothing per frame and
                    # keeps the points of the frame it was last drawn in.
                    # That is why it is hidden rather than emptied, and why
                    # it is redrawn here before it is shown again.
                    curve.setData(list(run.times_s), list(run.percents(quantity)))
                    curve.show()
                else:
                    curve.hide()

            _place_branch_point(items.branch_point, run.branch_point_s)
            _place_marks(items.marks, run.control_marks_s)

        for items in self._runs[len(frame.runs) :]:
            items.hide()

        self._frame = frame
        self._refresh_hover()

    @property
    def frame(self) -> ChartFrame | None:
        """The frame last drawn, or `None` before the first."""

        return self._frame

    def sizeHint(self) -> QSize:  # Qt spells this in camelCase.
        """As wide as the plot asks and `theme.CHART_HEIGHT` tall. It grows into spare height."""

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
        """The pen one run's curve for a compartment is drawn with.

        The pen is read from the curve item rather than recomputed. So a test
        can compare what the toolkit is painting with what `chart_frame` said
        it should paint.
        """

        pen: QPen = self._runs[run].curves[quantity].opts["pen"]

        return pen

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

    def axis_titles(self) -> tuple[str, ...]:
        """The titles of the chart's axes, so a walk over the whole interface finds them."""

        return _axis_titles(self._plot)

    def painted(self) -> QImage:
        """The chart as painted, so a test can check what is on screen."""

        return _render(self)

    def plot_pixel(self, time_s: float, percent: float) -> tuple[int, int]:
        """Which pixel of `painted` a plot position lands on."""

        return _plot_pixel(self._plot, time_s, percent)

    def plot_area(self) -> QRectF:
        """The plot inside its axes, in the pixels of `painted`, where the hover box has to stay."""

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

    def __init__(self, item: Any, run_index: RunIndex) -> None:
        self._run_index = run_index
        self._penned_for: RunCount | None = None
        pen = _wash_in_pen()
        self.stretches = []

        for _ in range(MAX_CHART_WASH_IN_SEGMENTS):
            stretch = pg.PlotCurveItem(pen=pen, antialias=True)
            stretch.hide()
            item.addItem(stretch)
            self.stretches.append(stretch)

        # One scatter item holds every terminus dot of the run, in the trace's
        # own colour. A dot says that the series ends here rather than
        # continuing out of view, and only a stretch that *stopped* gets one.
        self.termini = pg.ScatterPlotItem(
            size=_WASH_IN_TERMINUS_DIAMETER, pen=None, brush=pg.mkBrush(WASH_IN_COLOR)
        )
        item.addItem(self.termini, ignoreBounds=True)
        self.branch_point = _branch_point_mark(item)
        self.marks = _control_mark_pool(item)

    def repen(self, run_count: RunCount) -> None:
        """Give every stretch a new pen when the number of runs on the plot has changed."""

        if self._penned_for == run_count:
            return

        self._penned_for = run_count
        pen = _wash_in_pen(self._run_index, run_count)

        for stretch in self.stretches:
            stretch.setPen(pen)

    def hide(self) -> None:
        for stretch in self.stretches:
            stretch.hide()

        self.termini.setData([], [])
        self.branch_point.hide()

        for mark in self.marks:
            mark.hide()


class WashInChart(QWidget):
    """The F_A/F_I plot: the stretches, the equilibrium line, the marks, and its axis.

    The plot sits under the compartment chart rather than beside it, on the
    same time window, because it shows that chart's alveolar and circuit
    traces as one number. It draws the window of the same `ChartFrame`, so
    the two plots can never show different spans of the run.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._plot = _plot(PANEL)
        self._plot.setMinimumHeight(WASH_IN_CHART_HEIGHT)
        self._plot.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._plot)
        item = self._plot.getPlotItem()
        item.setLabel("left", "F_A/F_I", color=MUTED)
        item.setLabel("bottom", "simulated time", color=MUTED)
        # The axis is fixed rather than fitted to the data. It is labelled at
        # its own gridlines, at its own resolution, as `docs/MODEL.md`
        # § "F_A/F_I as a displayed ratio" specifies.
        item.setYRange(0.0, WASH_IN_AXIS_MAXIMUM, padding=0)
        item.getAxis("left").setTicks([list(wash_in_axis_ticks())])

        # The curve's asymptote, drawn as the reference it is. It is fixed by
        # definition rather than measured with a spread, so it is a line and
        # not a band. It belongs to the plot rather than to any run, because
        # F_A = F_I is a property of the ratio. So there is one line,
        # whatever the plot holds.
        self._equilibrium_line = pg.InfiniteLine(
            pos=WASH_IN_EQUILIBRIUM_RATIO,
            angle=_HORIZONTAL_LINE_ANGLE_DEG,
            pen=dashed_pen(
                EQUILIBRIUM_LINE_COLOR, EQUILIBRIUM_LINE_STROKE_WIDTH, EQUILIBRIUM_LINE_DASH_PATTERN
            ),
            movable=False,
        )
        self._equilibrium_line.setZValue(_Z_REFERENCE_LINE)
        item.addItem(self._equilibrium_line, ignoreBounds=True)
        self._grid = _GridLines(item)

        self._runs: list[_WashInRunItems] = []
        self._frame: ChartFrame | None = None
        self._hover = _HoverReadout(self._plot)
        self._hover.moved.connect(self._on_pointer)
        # Whether the box goes above or below its point depends on the plot's
        # height in pixels. So a resize places the box again, even while the
        # pointer rests and no frame is drawn (`PL-9BVQ`).
        item.getViewBox().sigResized.connect(self._refresh_hover)

    def draw(self, frame: ChartFrame) -> None:
        """Move every item to match one frame.

        Args:
            frame: What to draw. This is the same frame that the
                compartment chart drew, so the two plots share their
                instants and not merely their axis numbers.
        """

        item = self._plot.getPlotItem()
        _set_time_axis(item, frame)
        self._grid.place(frame.tick_times_s, [position for position, _ in wash_in_axis_ticks()])

        while len(self._runs) < len(frame.runs):
            self._runs.append(_WashInRunItems(item, RunIndex(len(self._runs))))

        for items, run in zip(self._runs, frame.runs, strict=False):
            items.repen(frame.run_count)
            ends_x: list[float] = []
            ends_y: list[float] = []

            for curve, stretch in zip(items.stretches, run.wash_in, strict=False):
                curve.setData(list(stretch.times_s), list(stretch.ratios))
                curve.show()

                if stretch.ends_above_equilibrium and stretch.times_s:
                    ends_x.append(stretch.times_s[-1])
                    ends_y.append(stretch.ratios[-1])

            for curve in items.stretches[len(run.wash_in) :]:
                curve.hide()

            items.termini.setData(ends_x, ends_y)
            _place_branch_point(items.branch_point, run.branch_point_s)
            _place_marks(items.marks, run.control_marks_s)

        for items in self._runs[len(frame.runs) :]:
            items.hide()

        self._frame = frame
        self._refresh_hover()

    @property
    def frame(self) -> ChartFrame | None:
        """The frame last drawn, or `None` before the first."""

        return self._frame

    def sizeHint(self) -> QSize:  # Qt spells this in camelCase.
        """As wide as the plot asks, and `theme.WASH_IN_CHART_HEIGHT` tall."""

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

    def terminus_points(self, run: int) -> tuple[tuple[float, float], ...]:
        """Where one run's terminus dots are drawn, as (time, ratio)."""

        times, ratios = self._runs[run].termini.getData()

        return tuple((float(t), float(r)) for t, r in zip(times, ratios, strict=True))

    def drawn_pen(self, run: int) -> QPen:
        """The pen one run's stretches are drawn with, read from the plot item."""

        pen: QPen = self._runs[run].stretches[0].opts["pen"]

        return pen

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

    def axis_titles(self) -> tuple[str, ...]:
        """The titles of the plot's axes, so a walk over the whole interface finds them."""

        return _axis_titles(self._plot)

    def painted(self) -> QImage:
        """The plot as painted, so a test can check what is on screen."""

        return _render(self)

    def plot_pixel(self, time_s: float, ratio: float) -> tuple[int, int]:
        """Which pixel of `painted` a plot position lands on."""

        return _plot_pixel(self._plot, time_s, ratio)

    def plot_area(self) -> QRectF:
        """The plot inside its axes, in the pixels of `painted`, where the hover box has to stay."""

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


def _axis_titles(plot: Any) -> tuple[str, ...]:
    """The non-empty axis titles of a plot, in left, bottom, right order."""

    item = plot.getPlotItem()
    titles = (str(item.getAxis(name).labelText) for name in ("left", "bottom", "right"))
    return tuple(title for title in titles if title)


def _axis_ticks(axis: Any) -> tuple[tuple[float, str], ...]:
    """The major ticks an axis was given, as (position, label)."""

    ticks = axis._tickLevels

    if not ticks:
        return ()

    return tuple((float(position), str(label)) for position, label in ticks[0])


def _render(widget: QWidget) -> QImage:
    """The widget as it is painted, for a rendering check."""

    return widget.grab().toImage()


def _preferred_size(plot: Any, height_px: int) -> QSize:
    """The size a chart asks its layout for: the plot's own width and the theme's height.

    The height comes from the theme rather than the toolkit. A graphics view
    asks for 480 px on its own, which is no chart's height. That request made
    the page a quarter of a screen taller than the page it replaced. The plot still
    grows past this height, because it expands in both directions, so a
    taller window lengthens the traces. The plot's minimum height is the same
    theme height, set on the plot.
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
        painter.setPen(self._pen)

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
        painter.setPen(self._edge_pen)
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


class TimeBaseSelector(QComboBox):
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


class TraceLegend(QWidget):
    """This widget shows the chart's four legend rows, and its compartment row is also a control.

    The rows are the compartments, the compared runs, the references and the
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
            box.setAccessibleName(TRACE_TOGGLE_ACCESSIBLE_NAME_TEMPLATE.format(label=style.label))
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
        # Each reference names the compartment it is read against.
        # `docs/MODEL.md` § "Interface boundary" requires that of a
        # reference, in the same passage that exempts a reference from the
        # drawn-trace rule. The band names vessel-rich, not alveolar. The
        # model has no effect-site compartment, and it defines the arterial
        # fraction as the alveolar one. So the alveolar trace is the fastest
        # curve on the chart, and the furthest from where responsiveness
        # returns. The 1 MAC line names alveolar, because MAC is defined for
        # the alveolar concentration.
        layout.addLayout(
            _legend_row(
                "Clinical references:",
                [
                    (self._band_swatch, _legend_label(MAC_AWAKE_BAND_LEGEND_LABEL)),
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
                        _legend_label("1 MAC, reference adult (alveolar) (wide dash)"),
                    ),
                ],
            )
        )
        # A third row, because a control mark is neither of the two kinds
        # above it. A compartment trace is a modelled quantity, and a
        # clinical reference is a published constant. A control mark is a
        # record of something the *user* did.
        branch_swatch = _LineSwatch(
            _branch_point_pen(),
            CONTROL_MARK_SWATCH_WIDTH,
            CONTROL_MARK_SWATCH_HEIGHT,
            vertical=True,
        )
        self._branch_entry = _legend_entry(branch_swatch, _legend_label(BRANCH_POINT_LEGEND_LABEL))
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
        self.show_selection(INITIAL_COMPARTMENT_SELECTION)

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
        `SimulationView._rename_runs`, before the wash-in legend or either
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
            LegendMark(entry.label.text(), entry.swatch._pen, entry.swatch._vertical)
            for entry in self._compared_entries
            if not entry.widget.isHidden()
        )

    @property
    def branch_mark(self) -> LegendMark | None:
        """The fork's legend entry, or None while it is not shown."""

        if self._branch_entry.isHidden():
            return None

        return LegendMark(BRANCH_POINT_LEGEND_LABEL, _branch_point_pen(), True)

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

    @property
    def band_mark(self) -> BandMark:
        """The MAC-awake band's entry: its words, its edge pen and its fill."""

        return BandMark(
            MAC_AWAKE_BAND_LEGEND_LABEL, self._band_swatch.edge_pen, self._band_swatch.fill_brush
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
        self._marks = tuple(
            LegendMark(label.text(), swatch._pen, swatch._vertical) for swatch, label in entries
        )
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
        self._branch_entry = _legend_entry(
            self._branch_swatch, _legend_label(BRANCH_POINT_LEGEND_LABEL)
        )
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
            LegendMark(entry.label.text(), entry.swatch._pen, entry.swatch._vertical)
            for entry in self._compared_entries
            if not entry.widget.isHidden()
        )


def _legend_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet(foreground_stylesheet(INK))

    return label
