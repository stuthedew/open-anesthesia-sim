"""The concentration chart and the wash-in plot, drawn with pyqtgraph.

The toolkit half of the chart. Everything a frame *claims* - which
compartment a curve carries, where the references stand, which instants are
drawn, what a hover says - is settled in `app/chart_frame.py` without a
toolkit, and this module only moves pyqtgraph items to match a `ChartFrame`.
Nothing here reads simulation state, formats a value, or decides a
coordinate: a widget that computed a number a reader interprets would put a
clinical value beyond the reach of `tests/unit/test_chart_frame.py`, which
is where those claims are held.

**Items are moved, never rebuilt.** Every curve, mark and reference is built
once and updated per frame, for the reason the Flet chart reused its point
controls (`PL-010`): a frame costs what it draws rather than what it
constructs. The pools are the sizes `chart_frame` states - a fixed number
of control marks and wash-in stretches - and an unused member is hidden,
which costs nothing per frame.

**Both axes are ruled where they are labelled, by construction.** Each axis
is given its ticks explicitly, from the frame, and pyqtgraph draws its
gridlines at the ticks the axis carries, so the ruling and the labelling
cannot describe two scales (`PL-Q4VH`).

**The hover answers whenever the pointer is over a drawn point, running or
paused** (`docs/MODEL.md` § "The chart's hover readout: what the tooltip may
show"). It is a readout over the plot's *drawn points* - the states the run
was evaluated at - never over a position between two of them, and its text
is `chart_frame`'s, produced by `app/formatting.py` and never by the chart
library's coordinate formatter. It costs per pointer event rather than per
point, so there is no mode to withdraw it in and no caption to write. It is
not a default, though: `pyqtgraph.ScatterPlotItem` ships `hoverable` off and
a plotted line carries no hover at all, so this module builds the affordance
rather than inheriting it (`PL-YVHK`).

**Every colour is `app/theme.py`'s.** This module declares no colour of its
own, so `tools/contrast_check.py`'s palette stays the one that is drawn.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import ceil
from typing import Any, Final

import pyqtgraph as pg
from PySide6.QtCore import QPointF, QSize, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QImage, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from anesthesia_sim.app.chart_frame import (
    COMPARED_COMPARTMENT_CAP,
    COMPARTMENT_TRACES,
    MAX_CHART_CONTROL_MARKS,
    MAX_CHART_WASH_IN_SEGMENTS,
    WASH_IN_AXIS_MAXIMUM,
    ChartFrame,
    HoverTarget,
    TraceStyle,
    compared_compartments,
    nearest_trace_point,
    nearest_wash_in_point,
    run_trace_style,
    trace_style,
    wash_in_axis_ticks,
)
from anesthesia_sim.app.dashboard_frame import (
    BRANCH_POINT_LEGEND_LABEL,
    COMPARED_TRACE_LEGEND_CAPTION,
    CONTROL_MARK_LEGEND_LABEL,
    EQUILIBRIUM_LEGEND_LABEL,
    MAC_AWAKE_BAND_LEGEND_LABEL,
    MAX_DISPLAYED_RUNS,
    TRACE_TOGGLE_ACCESSIBLE_NAME_TEMPLATE,
    WASH_IN_TRACE_LEGEND_LABEL,
    compared_trace_legend_label,
    run_label,
    trace_legend_label,
)
from anesthesia_sim.app.formatting import format_chart_time_label
from anesthesia_sim.app.qt_widgets import FlowLayout, declare_interface_colours
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity
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
    LEGEND_SWATCH_HEIGHT,
    LEGEND_SWATCH_WIDTH,
    MAC_AWAKE_BAND_COLOR,
    MAC_AWAKE_BAND_EDGE_STROKE_WIDTH,
    MAC_AWAKE_BAND_FILL_OPACITY,
    MUTED,
    ONE_MAC_LINE_COLOR,
    ONE_MAC_LINE_DASH_PATTERN,
    ONE_MAC_LINE_STROKE_WIDTH,
    PANEL,
    WASH_IN_CHART_HEIGHT,
    WASH_IN_COLOR,
    WASH_IN_STROKE_WIDTH,
)
from anesthesia_sim.app.wash_in import WASH_IN_EQUILIBRIUM_RATIO

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

# How far, in pixels, the pointer may be from a drawn point and still be
# answered. About the width of a fingertip's worth of cursor travel: wide
# enough that a reader aiming at a curve lands on it, narrow enough that a
# pointer parked in clear space between two traces reports neither rather
# than whichever is nearer.
HOVER_RADIUS_PIXELS: Final = 12.0


# The dot on the wash-in stretch's last point when it stopped by crossing
# equilibrium. A line that simply stops is indistinguishable from a line the
# frame cut off, and this one stops while still climbing steeply, which is the
# shape that reads as clipped. A terminal dot is the ordinary scientific-
# plotting answer: it says the series ends here rather than continuing out of
# view. Seven pixels across, the 3.5 px radius the Flet chart drew it at.
_WASH_IN_TERMINUS_DIAMETER: Final = 7.0

# The dot the hover puts on the point it is reporting, so a reader can see
# which drawn state the text describes.
_HOVER_DOT_DIAMETER: Final = 8.0

# Drawing order. Marks first - behind the references and behind every trace -
# because a vertical rule crossing the whole plot is the one annotation that
# can obscure all six compartments at the moment a reader is trying to see
# what the change did to them. References next, so every trace is drawn over
# them: a compartment obscured by a reference band would be the annotation
# hiding the run it annotates. The hover sits over everything.
_Z_GRIDLINE: Final = -50
_Z_CONTROL_MARK: Final = -30
_Z_REFERENCE_BAND: Final = -20
_Z_REFERENCE_LINE: Final = -10
_Z_HOVER: Final = 10


def trace_pen(style: TraceStyle) -> QPen:
    """The pen one compartment trace is drawn with, on the chart and in the legend.

    One constructor for both, so the legend swatch is drawn in the trace's
    own pattern rather than as a solid bar describing a dashed line
    (`PL-THXF`): a reader compares a mark to a curve rather than a phrase to
    a curve.

    Args:
        style: The trace.

    Returns:
        A pen in the trace's colour, width and dash pattern.
    """

    return dashed_pen(style.color, style.stroke_width, style.dash_pattern)


def dashed_pen(color: str, stroke_width: float, dash_pattern: Sequence[int] | None) -> QPen:
    """A pen with a dash pattern stated in display pixels.

    Qt states a dash pattern in units of the pen's width, and `app/theme.py`
    and `chart_frame.COMPARTMENT_TRACES` state theirs in pixels - the unit
    `docs/MODEL.md` § "The six compartment traces" tabulates - so the
    conversion is made once, here, rather than at each of the seven pens
    that carry a pattern. A pattern copied across without it draws every
    dash the pen's width times too long, which is what the spike did.

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


def run_trace_pen(quantity: RecordedQuantity, run_index: int, run_count: int) -> QPen:
    """The pen one run draws a compartment with, on the chart and in the legend.

    `chart_frame.run_trace_style` decides it and this only builds it, so the
    run's width channel is settled once, without a toolkit, where
    `tests/unit/test_chart_frame.py` can hold it.

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
    """The pen a fork is marked with: upright and solid where a control mark is dashed.

    Both marks name an instant and both are vertical, so what separates them
    is the dash pattern and the words in the legend - two channels, neither
    of them colour. It reuses the control mark's colour deliberately rather
    than declaring one: the pair is already measured against the panel, and
    a mark a reader must not read as a control change should not rest on a
    hue at all.
    """

    pen: QPen = pg.mkPen(CONTROL_MARK_COLOR, width=BRANCH_POINT_STROKE_WIDTH)

    return pen


def _wash_in_pen(run_index: int = 0, run_count: int = 1) -> QPen:
    """The pen one run's F_A/F_I trace is drawn with, on the plot and in its legend.

    One constructor for both, as `trace_pen` is for the compartments, so the
    legend swatch cannot describe a line the plot is not drawing.

    **The run's width channel reaches this plot too.** It draws one trace per
    run in one colour and one dash pattern, so two runs here are not merely
    hard to tell apart - they are identical but for their values, which is
    the failure the compartment chart's cap and width levels exist to
    prevent. The same step separates them, and for the same reason the same
    run is the wider: the two ratios also coincide exactly before the fork.

    Args:
        run_index: Which run, as a position in the frame's runs.
        run_count: How many runs are on the plot.

    Returns:
        The pen.

    Raises:
        ValueError: If `run_index` does not address one of `run_count` runs.
    """

    if run_count < 1 or not 0 <= run_index < run_count:
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

    Nothing a reader can pan, zoom or pop a menu on: the window is the time
    base's and the range is the axis's, and a plot a reader could drag off
    its labelled range would show a slope that meant something different
    from the one beside it.
    """

    plot = pg.PlotWidget(background=background)
    item = plot.getPlotItem()
    item.setMenuEnabled(False)
    item.hideButtons()
    item.setMouseEnabled(x=False, y=False)
    item.disableAutoRange()

    # Axis lines in the gridline colour and labels in the interface's label
    # colour, which `tools/contrast_check.py` measures as text. pyqtgraph's
    # own grid is deliberately not switched on: it is painted by the axis
    # item *over* the plot, so at full opacity a gridline erases the pixel
    # row of every trace and reference it crosses - measured 2026-09-14, the
    # 1 MAC line vanished under the 2% rule it stands on - and at partial
    # opacity it tints them. `_GridLines` rules the plot from underneath
    # instead, at exactly the ticks each axis is labelled at.
    for name in ("left", "bottom", "right"):
        axis = item.getAxis(name)
        axis.setPen(pg.mkPen(GRIDLINE))
        axis.setTextPen(pg.mkPen(MUTED))

    return plot


def _hover_items() -> tuple[Any, Any]:
    """The dot and the text box a hover shows, hidden until one answers."""

    dot = pg.ScatterPlotItem(size=_HOVER_DOT_DIAMETER, pen=None, brush=pg.mkBrush(INK))
    dot.setZValue(_Z_HOVER)
    dot.hide()
    text = pg.TextItem(color=INK, fill=pg.mkBrush(PANEL), border=pg.mkPen(MUTED), anchor=(0, 1))
    text.setZValue(_Z_HOVER)
    text.hide()

    return dot, text


class _GridLines:
    """The plot's ruling, drawn under everything at the ticks its axes carry.

    One line per tick on each axis, from the same tick lists the axes are
    labelled from, so the ruling and the labelling cannot describe two
    scales (`PL-Q4VH`). Pools that grow to the widest window drawn and are
    never shrunk; an unused line is hidden.
    """

    def __init__(self, item: Any) -> None:
        self._item = item
        self._pen = pg.mkPen(GRIDLINE, width=1)
        self._vertical: list[Any] = []
        self._horizontal: list[Any] = []

    def place(self, x_ticks: Sequence[float], y_ticks: Sequence[float]) -> None:
        """Rule the plot at these positions, and hide the rest of the pools."""

        self._rule(self._vertical, 90, x_ticks)
        self._rule(self._horizontal, 0, y_ticks)

    def _rule(self, pool: list[Any], angle: int, positions: Sequence[float]) -> None:
        while len(pool) < len(positions):
            line = pg.InfiniteLine(pos=0.0, angle=angle, pen=self._pen, movable=False)
            line.setZValue(_Z_GRIDLINE)
            self._item.addItem(line, ignoreBounds=True)
            pool.append(line)

        _place_marks(pool, positions)


class _HoverReadout:
    """The hover's mechanics, shared by both plots.

    Holds the last pointer position so a frame drawn under a resting pointer
    re-answers rather than going quiet: at high playback the reported value
    moves as the run does, which `docs/MODEL.md` § "When it answers" says is
    correct rather than a defect to design around.
    """

    def __init__(self, plot: Any) -> None:
        self._plot = plot
        self._dot, self._text = _hover_items()
        plot.getPlotItem().addItem(self._dot, ignoreBounds=True)
        plot.getPlotItem().addItem(self._text, ignoreBounds=True)
        self._scene_position: QPointF | None = None
        # Rate-limited, so a pointer sweeping across the plot costs at most
        # sixty lookups a second whatever the event rate; the proxy has to
        # be held, or it is collected and the signal goes nowhere.
        self._proxy = pg.SignalProxy(
            plot.scene().sigMouseMoved, rateLimit=60, slot=self._on_mouse_moved
        )

    def _on_mouse_moved(self, event: tuple[Any, ...]) -> None:
        self._scene_position = event[0]

    def scene_position(self) -> QPointF | None:
        """Where the pointer last was, in scene coordinates, if over the widget."""

        return self._scene_position

    def show(self, target: HoverTarget, x_range: tuple[float, float], y_top: float) -> None:
        """Put a dot on every point that answered and the text beside them.

        One dot per reading rather than one for the box, because every run
        inside the radius answers (`chart_frame.HoverTarget`) and a single
        dot would put a mark on one run's curve while the box read for
        several - the attribution failure `PL-MN4J` closed, arriving through
        the marker instead of through the text.
        """

        self._dot.setData(
            [reading.time_s for reading in target.readings],
            [reading.value for reading in target.readings],
        )
        self._text.setText(target.readout)
        # The box sits to the right of the anchor and above it, unless that
        # would run it off the plot: past the middle of the window it goes to
        # the left, and in the top quarter of the axis it goes below. The
        # newest point of a following window is at the right edge, which is
        # where a reader most often hovers, so the flip is the common case
        # rather than an edge one.
        anchor = target.anchor
        past_middle = anchor.time_s > (x_range[0] + x_range[1]) / 2.0
        near_top = anchor.value > 0.75 * y_top
        self._text.setAnchor((1 if past_middle else 0, 0 if near_top else 1))
        self._text.setPos(anchor.time_s, anchor.value)
        self._dot.show()
        self._text.show()

    def hide(self) -> None:
        self._dot.hide()
        self._text.hide()

    def shown_text(self) -> str | None:
        """What the hover currently says, or `None` while it is hidden."""

        return str(self._text.textItem.toPlainText()) if self._text.isVisible() else None


class _RunPens:
    """One run's pens, built on first use and kept.

    A trace's width carries the *run* once more than one is drawn
    (`chart_frame.run_trace_style`), so a pen depends on how many runs are
    on the chart as well as on the compartment - and that count changes when
    a reader forks. Rebuilt only when it changes, and then cached, so the
    per-frame cost stays what it was: items are moved, never rebuilt.
    """

    def __init__(self, run_index: int) -> None:
        self._run_index = run_index
        self._pens: dict[tuple[RecordedQuantity, int], QPen] = {}
        self._penned_for: int | None = None

    def changed_for(self, run_count: int) -> bool:
        """Whether the pens in use are not this many runs' pens, and record that they are."""

        if self._penned_for == run_count:
            return False

        self._penned_for = run_count

        return True

    def of(self, quantity: RecordedQuantity, run_count: int) -> QPen:
        """This run's pen for a compartment, with this many runs drawn."""

        key = (quantity, run_count)

        if key not in self._pens:
            self._pens[key] = run_trace_pen(quantity, self._run_index, run_count)

        return self._pens[key]


def _branch_point_mark(item: Any) -> Any:
    """One run's fork mark, hidden, full height and drawn over the gridlines.

    One per run rather than one per plot: a fork belongs to the run that
    opened at it, and a trunk simply never shows its own.
    """

    mark = pg.InfiniteLine(pos=0.0, angle=90, pen=_branch_point_pen(), movable=False)
    mark.setZValue(_Z_CONTROL_MARK)
    mark.hide()
    item.addItem(mark, ignoreBounds=True)

    return mark


def _place_branch_point(mark: Any, time_s: float | None) -> None:
    """Stand a run's fork mark at its instant, or hide it where there is none."""

    if time_s is None:
        mark.hide()

        return

    mark.setPos(time_s)
    mark.show()


class _RunItems:
    """One run's items on the concentration chart: its curves, its fork, its marks."""

    def __init__(self, item: Any, run_index: int) -> None:
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

    Vertical is the mark's own channel: nothing else on either plot is, so
    the orientation survives greyscale and every colour-vision deficiency,
    and the mark competes for nothing in a palette six traces have already
    exhausted. Full height by construction, because the time it marks has
    to be readable against every trace.
    """

    pen = _control_mark_pen()
    marks = []

    for _ in range(MAX_CHART_CONTROL_MARKS):
        mark = pg.InfiniteLine(pos=0.0, angle=90, pen=pen, movable=False)
        mark.setZValue(_Z_CONTROL_MARK)
        mark.hide()
        item.addItem(mark, ignoreBounds=True)
        marks.append(mark)

    return marks


def _place_marks(marks: Sequence[Any], times_s: Sequence[float]) -> None:
    """Stand the pool's marks at these times, and hide the rest."""

    for mark, time_s in zip(marks, times_s, strict=False):
        mark.setPos(time_s)
        mark.show()

    for mark in marks[len(times_s) :]:
        mark.hide()


def _set_time_axis(item: Any, frame: ChartFrame) -> None:
    """Rule and label the bottom axis for the window the frame draws.

    The placement is `chart_time_base.tick_times` and the wording is
    `formatting.format_chart_time_label`, both settled in the frame; this
    hands them to the axis. Every tick carries its unit - `45s`, `3m`,
    `1h30m` - because this axis spans anything from a minute to half a day
    and a bare `600` means seconds on one width and would be read as minutes
    on another while looking identical on both.
    """

    item.setXRange(frame.start_s, frame.stop_s, padding=0)
    item.getAxis("bottom").setTicks(
        [[(tick, format_chart_time_label(tick)) for tick in frame.tick_times_s]]
    )


class ConcentrationChart(QWidget):
    """The six compartment traces, both clinical references, both axes, the marks.

    Built once and redrawn per frame by `draw`, from a `ChartFrame` the
    dashboard assembles. Holds nothing about the run but the last frame it
    drew, which the hover reads.
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
        item.setLabel("left", "% of 1 atm", color=MUTED)
        item.setLabel("bottom", "simulated time", color=MUTED)
        item.showAxis("right")
        item.getAxis("right").setLabel("×MAC", color=MUTED)

        # The band and the line are drawn under the traces, so a trace is
        # never hidden behind a reference. Both are placed from the frame's
        # own MAC and MAC-awake, so neither can stand at another agent's
        # height. The band is two stroked edges with a light fill between
        # them: both strokes sit on the published boundaries, so the drawn
        # extent is the data extent exactly - a band drawn thicker than its
        # two edges would assert a wider population spread than the
        # literature supports (`PL-90Y6`).
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
            angle=0,
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
        self._plot.scene().sigMouseMoved.connect(self._on_pointer)

    def draw(self, frame: ChartFrame) -> None:
        """Move every item to match one frame.

        Args:
            frame: What to draw. Runs beyond the items already built get
                their own items on first sight; runs the frame no longer
                carries are hidden.
        """

        item = self._plot.getPlotItem()
        _set_time_axis(item, frame)
        # The ceiling and the rules move with the agent because both are
        # multiples of its 1 MAC - which is exactly what keeps the *scale*
        # still: 0 to 3 MAC, ruled every half MAC, whichever agent is
        # running. The left axis is labelled at exactly the values it rules,
        # and the right axis at round MAC values against the same range.
        item.setYRange(0.0, frame.axis_top_percent, padding=0)
        item.getAxis("left").setTicks([list(frame.percent_ticks)])
        item.getAxis("right").setTicks([list(frame.mac_ticks)])
        self._grid.place(frame.tick_times_s, [position for position, _ in frame.percent_ticks])
        self._one_mac_line.setPos(frame.one_mac_percent)
        self._band.setRegion(frame.mac_awake_band_percent)

        while len(self._runs) < len(frame.runs):
            self._runs.append(_RunItems(item, len(self._runs)))

        # Each run's items are added to the plot in turn, so a later run draws
        # over an earlier one. That order is load-bearing rather than
        # incidental: a branch reproduces its parent up to the fork, so before
        # the branch point the two curves coincide exactly, and it is the
        # narrower second run drawn last that keeps both visible there
        # (`theme.COMPARED_RUN_WIDTH_STEP`).
        run_count = len(frame.runs)

        for items, run in zip(self._runs, frame.runs, strict=False):
            repen = items.pens.changed_for(run_count)

            for quantity, curve in items.curves.items():
                if repen:
                    curve.setPen(items.pens.of(quantity, run_count))

                if quantity in frame.visible:
                    # Only the traces the reader has left shown are written:
                    # a hidden trace costs nothing per frame and holds the
                    # points of the frame it was last drawn in, which is why
                    # it is hidden rather than emptied - and why it is
                    # redrawn before it is shown again, below.
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
        """As wide as the plot asks and `theme.CHART_HEIGHT` tall; it grows into spare height."""

        return _preferred_size(self._plot, CHART_HEIGHT)

    def plot_width_px(self) -> float:
        """The width of the plot area in logical pixels, for `assemble_chart_frame`.

        Hand `chart_frame` the wider of this and the other plot's, so that
        neither draws a chord wider than a pixel (`PL-GS3R`).
        """

        return _plot_width_px(self._plot)

    def drawn_points(
        self, run: int, quantity: RecordedQuantity
    ) -> tuple[tuple[float, ...], tuple[float, ...]]:
        """The instants and percents one run's curve for a compartment is drawn with.

        Read back off the curve item itself rather than off the frame, so a
        test can hold what the toolkit holds against what the frame said.

        Args:
            run: Which run, as a position in the frame's runs.
            quantity: Which compartment.

        Returns:
            Times in simulated seconds and values in percent; both empty
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

        Read off the curve item rather than recomputed, so a test holds what
        the toolkit is painting against what `chart_frame` said it should.
        """

        pen: QPen = self._runs[run].curves[quantity].opts["pen"]

        return pen

    def branch_point_time(self, run: int) -> float | None:
        """Where one run's fork is marked, in simulated seconds, or None if unmarked."""

        mark = self._runs[run].branch_point

        return float(mark.value()) if mark.isVisible() else None

    def control_mark_times(self, run: int) -> tuple[float, ...]:
        """Where one run's shown control marks stand, in simulated seconds."""

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
        """The titles the chart's axes carry, so a whole-interface walk reaches them."""

        return _axis_titles(self._plot)

    def painted(self) -> QImage:
        """The chart as painted, so a test can hold what is on screen."""

        return _render(self)

    def plot_pixel(self, time_s: float, percent: float) -> tuple[int, int]:
        """Which pixel of `painted` a plot position lands on."""

        return _plot_pixel(self._plot, time_s, percent)

    def readout_at(self, time_s: float, percent: float) -> str | None:
        """What the hover would say for a pointer at this plot position.

        The same lookup the pointer triggers, exposed so a test can hold the
        rendered readout against the frame without synthesizing mouse
        events. The widget has to be shown and laid out first: the tolerance
        is in pixels, and a plot with no size has no pixels.

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

    def _on_pointer(self, scene_position: QPointF) -> None:
        del scene_position

        self._refresh_hover()

    def _refresh_hover(self) -> None:
        """Answer for wherever the pointer is, or hide when it is nowhere near."""

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
            self._hover.show(
                target, (self._frame.start_s, self._frame.stop_s), self._frame.axis_top_percent
            )

    def hover_text(self) -> str | None:
        """What the hover box currently shows, or `None` while it is hidden."""

        return self._hover.shown_text()


class _WashInRunItems:
    """One run's items on the wash-in plot: its stretches, their ends, its fork, its marks."""

    def __init__(self, item: Any, run_index: int) -> None:
        self._run_index = run_index
        self._penned_for: int | None = None
        pen = _wash_in_pen()
        self.stretches = []

        for _ in range(MAX_CHART_WASH_IN_SEGMENTS):
            stretch = pg.PlotCurveItem(pen=pen, antialias=True)
            stretch.hide()
            item.addItem(stretch)
            self.stretches.append(stretch)

        # One scatter item for every terminus dot of the run, in the trace's
        # own colour: it says the series ends here rather than continuing
        # out of view, and only a stretch that *stopped* gets one.
        self.termini = pg.ScatterPlotItem(
            size=_WASH_IN_TERMINUS_DIAMETER, pen=None, brush=pg.mkBrush(WASH_IN_COLOR)
        )
        item.addItem(self.termini, ignoreBounds=True)
        self.branch_point = _branch_point_mark(item)
        self.marks = _control_mark_pool(item)

    def repen(self, run_count: int) -> None:
        """Re-pen every stretch when the number of runs on the plot has changed."""

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
    """The F_A/F_I plot: the stretches, the equilibrium line, the marks, its axis.

    Under the compartment chart rather than beside it, on the same time
    window, because it is that chart's alveolar and circuit traces expressed
    as one number. The window it draws is the same `ChartFrame`'s, so the
    two plots can never be showing different spans of the run.
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
        # Fixed rather than fitted, and labelled at its own gridlines, in its
        # own resolution: `docs/MODEL.md` § "F_A/F_I as a displayed ratio".
        item.setYRange(0.0, WASH_IN_AXIS_MAXIMUM, padding=0)
        item.getAxis("left").setTicks([list(wash_in_axis_ticks())])

        # The curve's asymptote, drawn as the reference it is: a definitional
        # anchor rather than a measured value with spread, so a line and not
        # a band. It belongs to the plot rather than to any run - F_A = F_I is
        # a property of the ratio - so there is one whatever the plot holds.
        self._equilibrium_line = pg.InfiniteLine(
            pos=WASH_IN_EQUILIBRIUM_RATIO,
            angle=0,
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
        self._plot.scene().sigMouseMoved.connect(self._on_pointer)

    def draw(self, frame: ChartFrame) -> None:
        """Move every item to match one frame.

        Args:
            frame: What to draw - the same frame the compartment chart drew,
                so the two plots share their instants and not merely their
                axis numbers.
        """

        item = self._plot.getPlotItem()
        _set_time_axis(item, frame)
        self._grid.place(frame.tick_times_s, [position for position, _ in wash_in_axis_ticks()])

        while len(self._runs) < len(frame.runs):
            self._runs.append(_WashInRunItems(item, len(self._runs)))

        for items, run in zip(self._runs, frame.runs, strict=False):
            items.repen(len(frame.runs))
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

        Hand `chart_frame` the wider of this and the other plot's, so that
        neither draws a chord wider than a pixel (`PL-GS3R`).
        """

        return _plot_width_px(self._plot)

    def drawn_stretches(self, run: int) -> tuple[tuple[tuple[float, float], ...], ...]:
        """Each shown stretch of one run, as its drawn (time, ratio) points."""

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
        """The pen one run's stretches are drawn with, read off the plot item."""

        pen: QPen = self._runs[run].stretches[0].opts["pen"]

        return pen

    def branch_point_time(self, run: int) -> float | None:
        """Where one run's fork is marked, in simulated seconds, or None if unmarked."""

        mark = self._runs[run].branch_point

        return float(mark.value()) if mark.isVisible() else None

    def control_mark_times(self, run: int) -> tuple[float, ...]:
        """Where one run's shown control marks stand, in simulated seconds."""

        return tuple(float(mark.value()) for mark in self._runs[run].marks if mark.isVisible())

    def equilibrium_line(self) -> float:
        """Where the equilibrium line is drawn, as a ratio."""

        return float(self._equilibrium_line.value())

    def axis_ticks(self, name: str) -> tuple[tuple[float, str], ...]:
        """The ticks one axis is labelled at, as (position, label)."""

        return _axis_ticks(self._plot.getPlotItem().getAxis(name))

    def axis_titles(self) -> tuple[str, ...]:
        """The titles the plot's axes carry, so a whole-interface walk reaches them."""

        return _axis_titles(self._plot)

    def painted(self) -> QImage:
        """The plot as painted, so a test can hold what is on screen."""

        return _render(self)

    def plot_pixel(self, time_s: float, ratio: float) -> tuple[int, int]:
        """Which pixel of `painted` a plot position lands on."""

        return _plot_pixel(self._plot, time_s, ratio)

    def readout_at(self, time_s: float, ratio: float) -> str | None:
        """What the hover would say for a pointer at this plot position.

        As `ConcentrationChart.readout_at`, on the ratio axis.

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

    def _on_pointer(self, scene_position: QPointF) -> None:
        del scene_position

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
            self._hover.show(
                target, (self._frame.start_s, self._frame.stop_s), WASH_IN_AXIS_MAXIMUM
            )

    def hover_text(self) -> str | None:
        """What the hover box currently shows, or `None` while it is hidden."""

        return self._hover.shown_text()


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
    """The size a chart asks its layout for: the plot's own width, the theme's height.

    The height is the theme's rather than the toolkit's: a graphics view
    asks for 480 px of its own accord, which is no chart's height and made
    the page a quarter of a screen taller than the one it replaced. The
    plot still grows past this - it expands in both directions - so a
    taller window lengthens the traces; the minimum is the same theme
    height, set on the plot.
    """

    return QSize(plot.sizeHint().width(), height_px)


def _plot_width_px(plot: Any) -> float:
    """The width of `plot`'s plot area in logical pixels, for `chart_columns`.

    The view box rather than the widget: the axes and their labels take the
    rest, and it is the view box the time axis spans. Read from the geometry
    Qt laid out, so before a chart is shown it answers whatever default size
    the toolkit gave the unshown widget - which is why the caller draws its
    first frame after the chart is shown, and why `chart_columns` floors
    what it is handed.
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


class _LineSwatch(QWidget):
    """A legend mark drawn with the very pen its series is drawn with.

    Horizontal for a trace or a reference line, vertical for a control mark,
    whose own channel on the chart is that it is the only vertical thing
    there. Its size never changes with what it shows - this sits beside a
    control a reader clicks repeatedly, and a row that reflowed under the
    cursor would move the next box out from under it - so an *empty* swatch,
    for a trace that is hidden, paints nothing at the same size.
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
        whichever traces are drawn, so a swatch has to be able to take the
        pen of the curve it currently describes. The size never changes with
        it, for the reason the class docstring gives.
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
    """The MAC-awake band's legend mark: a fill ruled on both edges, as on the chart.

    A band's extent is exactly what distinguishes it from a line, so this is
    the one legend mark not drawn at the shared swatch size - and it is
    ruled on both edges because a swatch ruled on one would teach the reader
    the wrong mark for the one on the chart (`PL-90Y6`).
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
        """The pen both edges are ruled with."""

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

    A wrapping row, as the Flet build's legend rows were, so the entries
    reflow under a narrow chart rather than holding the chart column to
    their summed width: the caption is laid first and the entries follow it,
    each an unbreakable swatch-and-label pair, and a pair that would overrun
    the right edge starts the next line.
    """

    row = FlowLayout(horizontal_spacing=16, vertical_spacing=6)

    if caption is not None:
        row.addWidget(legend_caption(caption))

    for swatch, label in entries:
        row.addWidget(_legend_entry(swatch, label))

    return row


class _PooledEntry:
    """One legend entry whose swatch and words are rewritten rather than rebuilt.

    The compare-mode rows name every curve actually on the plot, and which
    curves those are changes with the reader's selection and with how many
    runs are drawn. A fixed pool the size of the most that can be shown -
    `COMPARED_COMPARTMENT_CAP` compartments times `MAX_DISPLAYED_RUNS` runs -
    is written and hidden instead of a row rebuilt on every change, which is
    the same reason the plots keep fixed pools of marks and stretches.
    """

    def __init__(self, row: FlowLayout) -> None:
        self.swatch = _LineSwatch(_control_mark_pen(), LEGEND_SWATCH_WIDTH, LEGEND_SWATCH_HEIGHT)
        self.label = _legend_label("")
        self.widget = _legend_entry(self.swatch, self.label)
        self.widget.setHidden(True)
        row.addWidget(self.widget)

    def show(self, pen: QPen, text: str) -> None:
        """Stand for this curve: its own pen, and the words that name it."""

        self.swatch.set_pen(pen)
        self.label.setText(text)
        self.widget.setHidden(False)

    def hide(self) -> None:
        """Show nothing, and take no space."""

        self.widget.setHidden(True)


def legend_caption(text: str) -> QLabel:
    """A legend row's caption, in the muted role every row's caption takes.

    Its own constructor because a row that has to hide its caption - the
    compare row, which stands down entirely on a single run - needs to hold
    the widget rather than fish it back out of the layout.
    """

    label = QLabel(text)
    label.setStyleSheet(f"color: {MUTED};")

    return label


def _legend_entry(swatch: QWidget, label: QWidget) -> QWidget:
    """A swatch beside its words, as one item a legend row wraps whole."""

    entry = QWidget()
    pair = QHBoxLayout(entry)
    pair.setContentsMargins(0, 0, 0, 0)
    pair.setSpacing(6)
    pair.addWidget(swatch, alignment=Qt.AlignmentFlag.AlignVCenter)
    pair.addWidget(label, alignment=Qt.AlignmentFlag.AlignVCenter)

    return entry


class TraceLegend(QWidget):
    """The chart's three legend rows, of which the compartment row is also a control.

    The compartment entry *is* the state: its box, its swatch and its label
    are written from one flag, which is what makes the legend's agreement
    with the plot a property of the code rather than of somebody's
    diligence. Two lists of the same six compartments is exactly how a
    legend comes to name a line the chart is not drawing.

    Each swatch is painted with the pen the chart draws that series with,
    so a dashed trace has a dashed swatch (`PL-THXF`) and the band is a
    band. The references and the control mark get their own rows rather
    than joining the six compartments: they are not compartments, and one
    row would invite reading them as a seventh and eighth trace.

    An entry stays on screen when its trace is off, and keeps its line-style
    words while it is off (`PL-YTX9`): the unchecked box and the empty
    swatch already say the line is not drawn, in two channels neither of
    which is colour, and the words are what switching it on will draw.
    """

    visibility_changed = Signal()
    """Emitted after a reader shows or hides a compartment."""

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
            box.setStyleSheet(f"color: {INK};")
            # The label's colour is the stylesheet's; the *indicator* is drawn
            # from palette `Base` and `Text`, which the stylesheet does not
            # reach - so under a dark host appearance the box was a dark square
            # and its tick was INK on near-black at 1.35:1 (`PL-7W9N`).
            declare_interface_colours(box)
            box.toggled.connect(
                lambda checked, quantity=style.quantity: self._on_toggled(quantity, checked)
            )
            self._boxes[style.quantity] = box
            self._swatches[style.quantity] = swatch
            compartments.append((swatch, box))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addLayout(_legend_row("Compartments:", compartments))
        # The compare row: one entry per curve actually drawn, naming both the
        # compartment and the run, because once a curve carries two dimensions
        # a legend that names one of them attributes nothing. It is empty and
        # takes no height on a single run, where the row above already names
        # every drawn curve completely.
        self._compared_row = _legend_row(None, [])
        self._compared_caption = legend_caption(COMPARED_TRACE_LEGEND_CAPTION)
        self._compared_row.addWidget(self._compared_caption)
        self._compared_entries = [
            _PooledEntry(self._compared_row)
            for _ in range(COMPARED_COMPARTMENT_CAP * MAX_DISPLAYED_RUNS)
        ]
        layout.addLayout(self._compared_row)
        # Each reference names the compartment it is read against, which
        # `docs/MODEL.md` § "Interface boundary" requires of a reference in
        # the same breath as it exempts one from the drawn-trace rule.
        # Vessel-rich for the band, not alveolar: the model has no effect-site
        # compartment and defines the arterial fraction as the alveolar one,
        # so the alveolar trace is the fastest curve on the chart and the
        # furthest from where responsiveness returns. Alveolar for 1 MAC,
        # because that is what MAC is defined for.
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
        # above it: a compartment trace is a modelled quantity and a clinical
        # reference is a published constant; this is a record of something
        # the *user* did.
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
        self._run_count = 1
        self._check_order: list[RecordedQuantity] = list(COMPARTMENT_QUANTITIES)
        self._adjusting = False
        self._refresh_compared_row()

    @property
    def shown(self) -> tuple[RecordedQuantity, ...]:
        """The compartments currently checked, in table order."""

        return tuple(
            style.quantity
            for style in COMPARTMENT_TRACES
            if self._boxes[style.quantity].isChecked()
        )

    def set_shown(self, shown: Sequence[RecordedQuantity]) -> None:
        """Check exactly these compartments, as a reader clicking would.

        Written as one act rather than six clicks: the cap is not applied
        between the boxes, so a caller may pass a set that is briefly over it
        without the legend unchecking something in the middle of the pass,
        and the change is announced once rather than once per box.

        A bulk set that is over the cap is reduced by
        `compared_compartments` - the top of the compartment table - because
        a set arriving whole carries no order of preference for this class to
        read. `set_compartment_shown` is the one-at-a-time route, and it
        keeps what was just asked for instead.
        """

        wanted = tuple(shown)

        while True:
            self._adjusting = True

            try:
                for quantity, box in self._boxes.items():
                    box.setChecked(quantity in wanted)
            finally:
                self._adjusting = False

            drawn, over = compared_compartments(self.shown, self._run_count)

            if not over:
                break

            wanted = drawn

        self._refresh_compared_row()
        self.visibility_changed.emit()

    def set_compartment_shown(self, quantity: RecordedQuantity, shown: bool) -> None:
        """Show or hide one compartment, by exactly the route a reader's click takes.

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

    def set_run_count(self, run_count: int) -> None:
        """Tell the legend how many runs are drawn, and hold the selection to the cap.

        The cap is `chart_frame`'s and is applied there to what the chart
        draws whatever route reached the selection. This is the same rule
        arriving at the *control*, so that the boxes a reader sees checked
        are the curves the plot is drawing: a legend left showing four
        checked boxes against two curves is the disagreement this class
        exists to make impossible.

        Args:
            run_count: How many runs the dashboard is displaying.

        Raises:
            ValueError: If fewer than one run is given. A legend for no runs
                would cap a selection against nothing.
        """

        if run_count < 1:
            raise ValueError(f"a legend describes at least one run, not {run_count}")

        if run_count == self._run_count:
            return

        self._run_count = run_count
        drawn, over = compared_compartments(self.shown, run_count)

        self._branch_entry.setHidden(run_count <= 1)

        if over:
            # Reduced to exactly what the chart will draw, rather than to some
            # other pair this class chose: `compared_compartments` is the one
            # rule, and a legend applying a second one is how a checked box
            # comes to name a curve that is not on the plot. `set_shown`
            # refreshes the compare row and announces the change.
            self.set_shown(drawn)
        else:
            self._refresh_compared_row()

    @property
    def compared_marks(self) -> tuple[LegendMark, ...]:
        """The compare row's entries as drawn: each curve's words and its own pen.

        Empty on a single run, where the compartment row already names every
        drawn curve completely.
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

    def _drop_oldest_over_cap(self) -> None:
        """Uncheck the longest-standing selections until the cap is met again.

        The oldest rather than the newest, so the compartment a reader just
        asked for is the one they get: a cap that refused the click instead
        would leave them clicking a box that does not respond, which is the
        worse of the two surprises. Only reached from a *check*, so it never
        runs while a reader is putting compartments away.

        It leaves the selection at or inside the cap, which is what makes
        `compared_compartments` the identity on everything this legend hands
        out afterwards - so the boxes and the curves cannot disagree.
        """

        if not compared_compartments(self.shown, self._run_count)[1]:
            return

        self._adjusting = True

        try:
            while compared_compartments(self.shown, self._run_count)[1]:
                self._boxes[self._check_order[0]].setChecked(False)
        finally:
            self._adjusting = False

    def _refresh_compared_row(self) -> None:
        """Write one entry per drawn curve, and hide the rest of the pool."""

        drawn, _ = compared_compartments(self.shown, self._run_count)
        entries = (
            []
            if self._run_count <= 1
            else [
                (
                    run_trace_pen(quantity, index, self._run_count),
                    compared_trace_legend_label(
                        trace_legend_label(trace_style(quantity)), run_label(index)
                    ),
                )
                # Grouped by compartment rather than by run, so the two
                # entries a reader compares stand beside each other exactly
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
        self._boxes[quantity].setStyleSheet(f"color: {INK if checked else MUTED};")

        if quantity in self._check_order:
            self._check_order.remove(quantity)

        if checked:
            self._check_order.append(quantity)

        # A box this legend unchecked itself, holding the selection to the
        # cap, reaches here too: it repaints and takes its place in the order,
        # and the pass that unchecked it reports the change once rather than
        # once per box.
        if self._adjusting:
            return

        if checked:
            self._drop_oldest_over_cap()

        self._refresh_compared_row()
        self.visibility_changed.emit()


def _control_mark_entry() -> tuple[_LineSwatch, QLabel]:
    """The control mark's legend entry, the same on both legends: upright, in its own pen."""

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

    What a test reads back from a legend, so that the words and the mark can
    be held against the plot's own pens without reaching into a widget.
    """

    label: str
    pen: QPen
    vertical: bool


@dataclass(frozen=True)
class BandMark:
    """The MAC-awake band's legend entry as it is drawn: its words, its edges and its fill.

    Ruled on both edges and filled between, as the band on the chart is
    (`PL-90Y6`); what a test reads back to hold the swatch to the chart's
    own mark.
    """

    label: str
    edge_pen: QPen
    fill: QBrush


class WashInLegend(QWidget):
    """The wash-in plot's legend row: the ratio trace, its asymptote, the control mark.

    One row rather than three, and no caption, because the wash-in plot has
    one trace and one reference and the row reads without them; it sits
    under the plot's heading and its two label lines, which say what the
    ratio is and is not (`PL-F9TQ`). Each swatch is painted with the pen the
    plot draws that mark with - the trace at its own stroke width, the
    equilibrium line in its wide dash, the control mark upright and finely
    dashed - so the swatch and the words describe the mark in two channels
    (`PL-THXF`). The per-run state sentence that follows this row on screen is
    the dashboard's to place, since it is written per tick from the frame.
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
        # This plot draws one trace per run in one colour and one dash
        # pattern, so the run's width is the only thing separating two of
        # them and the row has to name which width is which. A fork entry
        # joins it for the same reason it joins the chart's legend above.
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
        self._run_count = 1

    def set_run_count(self, run_count: int) -> None:
        """Tell the legend how many runs are drawn, and name each one's trace.

        Args:
            run_count: How many runs the dashboard is displaying.

        Raises:
            ValueError: If fewer than one run is given.
        """

        if run_count < 1:
            raise ValueError(f"a legend describes at least one run, not {run_count}")

        if run_count == self._run_count:
            return

        self._run_count = run_count
        comparing = run_count > 1
        # The single unqualified entry stands down while the per-run entries
        # stand in for it: two entries naming the same trace, one of them
        # saying nothing about which run, is the ambiguity this row is
        # being given to remove.
        self._trace_swatch.setHidden(comparing)
        self._trace_label.setHidden(comparing)
        self._branch_entry.setHidden(not comparing)

        for index, entry in enumerate(self._compared_entries):
            if index < run_count and comparing:
                entry.show(
                    _wash_in_pen(index, run_count),
                    compared_trace_legend_label(WASH_IN_TRACE_LEGEND_LABEL, run_label(index)),
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
    label.setStyleSheet(f"color: {INK};")

    return label
