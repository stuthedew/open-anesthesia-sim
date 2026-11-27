"""Tests that every chart line keeps its specified width and dashes on any screen scale.

`docs/INTERFACE.md` § "The six compartment traces: what separates them" gives
each line's width and dash pattern in device-independent pixels, the unit Qt
lays out every widget in. Qt draws a cosmetic pen's width in device pixels,
so before `PL-FSRR` every chart line drew at 1/ratio of its width: 1.5 px for a
3 px trace on a Retina screen, and 2.4 px on a Windows screen at 125%.

The ratios tested are the scales a user meets: 100%, 125% and 150% on Windows,
200% on a Retina Mac, and 300% on some high-density panels. A `QImage` given a
device pixel ratio is painted through the same scaling as a screen at that
ratio, so the painting tests run in this process. The last test starts a
process whose screen is at each ratio, because a widget's own ratio comes from
its screen and is fixed for the life of the process.
"""

import json
import os
import subprocess
import sys
from collections.abc import Iterator
from math import ceil
from pathlib import Path

import pyqtgraph as pg
import pytest
from PySide6.QtCore import QEvent, QPoint, QPointF
from PySide6.QtGui import QColor, QImage, QPainter, QPen, QRegion
from PySide6.QtWidgets import QApplication, QWidget

from anesthesia_sim.app.chart_frame import (
    COMPARTMENT_TRACES,
    ChartFrame,
    RunInput,
    assemble_chart_frame,
)
from anesthesia_sim.app.control_timeline import AdjustmentGrouping
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import run_label
from anesthesia_sim.app.qt_chart import (
    ConcentrationChart,
    TraceLegend,
    WashInChart,
    WashInLegend,
    _LineSwatch,
    dashed_pen,
    on_screen,
    trace_pen,
)
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES
from anesthesia_sim.app.theme import (
    CONTROL_MARK_COLOR,
    CONTROL_MARK_DASH_PATTERN,
    CONTROL_MARK_STROKE_WIDTH,
    MUTED,
)
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.layout.run_identity import RunId, SessionToken

#: Screen scales a user meets, as device pixels per device-independent pixel.
RATIOS = (1.0, 1.25, 1.5, 2.0, 3.0)

#: Every pen with a dash pattern that the chart draws, with the pattern in
#: device-independent pixels as `docs/INTERFACE.md` tabulates it.
_DASHED = (
    *((style.dash_pattern, trace_pen(style)) for style in COMPARTMENT_TRACES),
    (
        CONTROL_MARK_DASH_PATTERN,
        dashed_pen(CONTROL_MARK_COLOR, CONTROL_MARK_STROKE_WIDTH, CONTROL_MARK_DASH_PATTERN),
    ),
)

_SESSION = SessionToken("0" * 32)


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


def _painted(pen: QPen, ratio: float, *, antialiased: bool) -> QImage:
    """Paint a horizontal line 300 px long on a transparent image at this device pixel ratio."""

    width_px, height_px = 300, 30
    image = QImage(ceil(width_px * ratio), ceil(height_px * ratio), QImage.Format.Format_ARGB32)
    image.setDevicePixelRatio(ratio)
    image.fill(0)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, antialiased)
    painter.setPen(on_screen(pen, ratio))
    painter.drawLine(QPointF(0.0, height_px / 2), QPointF(float(width_px), height_px / 2))
    painter.end()

    return image


def _thickness_device_px(image: QImage, *, vertical: bool = False) -> float:
    """A line's painted thickness in device pixels: the most coverage summed across it.

    The coverage is summed down each column of a horizontal line, or along each
    row of a vertical one, and the largest sum is taken, so a dashed line is
    measured through a dash rather than through a gap.
    """

    if vertical:
        return max(
            sum(QColor.fromRgba(image.pixel(x, y)).alphaF() for x in range(image.width()))
            for y in range(image.height())
        )

    return max(
        sum(QColor.fromRgba(image.pixel(x, y)).alphaF() for y in range(image.height()))
        for x in range(image.width())
    )


def _coverage_limit_device_px(width_device_px: float) -> float:
    """The most that 8-bit coverage can move a summed thickness, in device pixels.

    This is a numerical limit, from rounding. Each pixel's coverage is stored
    as a whole number of 255ths, so it is off by at most 1/510, and the line
    covers at most its width rounded up plus one partly covered pixel at each
    edge.
    """

    return (ceil(width_device_px) + 2) / 510


def _runs_device_px(image: QImage) -> list[int]:
    """The on and off run lengths along the line's centre row, in device pixels."""

    y = image.height() // 2
    row = [QColor.fromRgba(image.pixel(x, y)).alpha() > 0 for x in range(image.width())]
    runs: list[int] = []
    current, length = row[0], 0

    for painted in row:
        if painted == current:
            length += 1
        else:
            runs.append(length)
            current, length = painted, 1

    return runs


@pytest.mark.parametrize("ratio", RATIOS)
def test_each_trace_is_painted_at_its_specified_width_at_every_screen_scale(
    application: QApplication, ratio: float
) -> None:
    """`PL-FSRR`: a 3 px trace covers 3 device-independent pixels at every ratio.

    Before the fix the circuit trace painted 1.5 px wide at a ratio of 2.
    """

    for style in COMPARTMENT_TRACES:
        width_device_px = style.stroke_width * ratio
        painted = _thickness_device_px(_painted(trace_pen(style), ratio, antialiased=True))

        assert abs(painted - width_device_px) <= _coverage_limit_device_px(width_device_px), (
            style.quantity
        )


@pytest.mark.parametrize("ratio", RATIOS)
def test_each_dash_and_gap_is_painted_at_its_specified_length_at_every_screen_scale(
    application: QApplication, ratio: float
) -> None:
    """`PL-FSRR`: each dash and gap keeps its length in device-independent pixels.

    The dash pattern is what separates the compartment traces for a reader with
    a colour-vision deficiency. Painted without antialiasing, each edge of a
    dash falls on a whole device pixel, so a run can differ from its length by
    at most one device pixel, and the rounding does not add up over a period.
    """

    for pattern, pen in _DASHED:
        assert pattern is not None or pen.dashPattern() == []

        if pattern is None:
            continue

        runs = _runs_device_px(_painted(pen, ratio, antialiased=False))
        periods = (len(runs) - 1) // len(pattern)

        assert periods >= 2

        for index, run in enumerate(runs[: periods * len(pattern)]):
            assert abs(run - pattern[index % len(pattern)] * ratio) <= 1, (pattern, index)

        assert abs(sum(runs[: len(pattern)]) - sum(pattern) * ratio) <= 1, pattern


def test_a_pen_qt_scales_itself_and_a_ratio_that_is_not_a_scale_are_handled(
    application: QApplication,
) -> None:
    """A non-cosmetic pen is left as it is, and a ratio that no screen has is refused."""

    geometric = QPen(QColor("#000000"), 3.0)

    assert on_screen(geometric, 2.0).widthF() == 3.0
    assert on_screen(pg.mkPen("#000000", width=3), 1.25).widthF() == 3.75

    for ratio in (0.0, -1.0, float("nan"), float("inf")):
        with pytest.raises(ValueError, match="device pixel ratio"):
            on_screen(pg.mkPen("#000000", width=3), ratio)


def _two_run_frame() -> ChartFrame:
    """A frame of two runs, each with a dial change, so every kind of chart line is drawn."""

    grouping = AdjustmentGrouping()
    runs = []

    for number in (1, 2):
        controller = SimulationController()
        controller.start()

        for _ in range(300 // SIMULATION_STEP_S):
            controller.advance()

        controller.begin_control_adjustment()
        controller.set_delivered_concentration_percent(
            Percent(controller.snapshot().delivered_concentration_percent * 1.5)
        )

        for _ in range(300 // SIMULATION_STEP_S):
            controller.advance()

        snapshot = controller.snapshot()
        runs.append(
            RunInput(
                run_label(RunId(_SESSION, number)),
                controller,
                snapshot,
                grouping.of(snapshot.control_timeline),
            )
        )

    return assemble_chart_frame(
        runs, None, COMPARTMENT_QUANTITIES, plot_width_px=900.0, held_start_s=None
    )


def _line_items(chart: ConcentrationChart | WashInChart) -> list[tuple[object, QPen]]:
    """Each item of the plot that strokes a line, with the pen it strokes with.

    A region's two edges are its own lines, and they are reported under the
    region that was given their pen.
    """

    found: list[tuple[object, QPen]] = []

    for item in chart._plot.scene().items():
        if isinstance(item, pg.PlotCurveItem):
            found.append((item, item.opts["pen"]))
        elif isinstance(item, pg.InfiniteLine):
            owner = item.parentItem()
            found.append((owner if isinstance(owner, pg.LinearRegionItem) else item, item.pen))
        elif isinstance(item, pg.AxisItem) and item.isVisible():
            found.append((item, item.pen()))
        elif isinstance(item, pg.TextItem):
            found.append((item, item.border))

    return found


def _assert_every_line_drawn_for(chart: ConcentrationChart | WashInChart, ratio: float) -> int:
    """Every line the plot strokes is held, and is stroked at its specified width for `ratio`."""

    pens = chart._pens
    items = _line_items(chart)

    assert pens.device_pixel_ratio == ratio

    for item, drawn in items:
        assert pens.holds(item), f"{type(item).__name__} draws a line no one keeps to scale"
        specified = pens.specified(item)

        assert drawn.widthF() == specified.widthF() * ratio, type(item).__name__
        assert drawn.dashPattern() == specified.dashPattern(), type(item).__name__

    return len(items)


@pytest.mark.parametrize("chart_type", [ConcentrationChart, WashInChart])
def test_every_line_on_a_plot_is_kept_to_scale_and_follows_a_move_to_another_screen(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, chart_type: type
) -> None:
    """`PL-FSRR`: no line escapes the conversion, and a new screen's ratio redraws them all.

    Qt sends `DevicePixelRatioChange` to every widget of a window that moves to
    a screen with another ratio. This process has one screen, so the test gives
    the plot a new ratio and sends the event itself. The axis titles are read
    as well, because pyqtgraph sets an axis title's colour when its pen is set.
    """

    chart = chart_type()
    chart.resize(900, 400)
    chart.show()
    chart.draw(_two_run_frame())
    application.processEvents()

    try:
        assert _assert_every_line_drawn_for(chart, 1.0) > 20

        for ratio in RATIOS[1:]:
            monkeypatch.setattr(chart._plot, "devicePixelRatioF", lambda ratio=ratio: ratio)
            QApplication.sendEvent(chart._plot, QEvent(QEvent.Type.DevicePixelRatioChange))
            _assert_every_line_drawn_for(chart, ratio)

            axis = chart._plot.getPlotItem().getAxis("left")

            assert axis.labelStyle["color"] == MUTED
    finally:
        chart.close()
        chart.deleteLater()
        application.processEvents()


def _swatch_thickness_logical_px(swatch: _LineSwatch, ratio: float) -> float:
    """Render one legend swatch at this ratio and return its mark's thickness across the mark."""

    image = QImage(
        ceil(swatch.width() * ratio), ceil(swatch.height() * ratio), QImage.Format.Format_ARGB32
    )
    image.setDevicePixelRatio(ratio)
    image.fill(0)
    # Without the window's background, so only the mark covers the image.
    swatch.render(image, QPoint(), QRegion(), QWidget.RenderFlag.DrawChildren)
    across = _thickness_device_px(image, vertical=swatch._vertical)

    return across / ratio


@pytest.mark.parametrize("ratio", RATIOS)
def test_each_legend_swatch_is_painted_at_its_line_s_width_at_every_screen_scale(
    application: QApplication, ratio: float
) -> None:
    """`PL-FSRR`: each key of both legends keeps the width of the line it stands for.

    A swatch converts its pen when it paints, at the ratio of the device it
    paints on, so rendering it into an image at a ratio is what a screen at
    that ratio shows.
    """

    legends = (TraceLegend(), WashInLegend())

    try:
        swatches = [swatch for legend in legends for swatch in legend.findChildren(_LineSwatch)]

        assert len(swatches) >= len(COMPARTMENT_TRACES) + 2

        for swatch in swatches:
            width = swatch._pen.widthF()
            thickness = _swatch_thickness_logical_px(swatch, ratio)
            limit = _coverage_limit_device_px(width * ratio) / ratio

            assert abs(thickness - width) <= limit, (width, swatch._vertical, thickness)
    finally:
        for legend in legends:
            legend.deleteLater()

        application.processEvents()


# A script for a process whose screen is at a given ratio. It draws both plots
# and prints what each line is stroked with. Its argument is this file's folder.
_ON_A_SCALED_SCREEN = """
import json
import sys
from PySide6.QtWidgets import QApplication
app = QApplication([])
sys.path.insert(0, sys.argv[1])
from test_chart_screen_scale import _line_items, _two_run_frame
from anesthesia_sim.app.qt_chart import ConcentrationChart, WashInChart
report = {"screen": app.primaryScreen().devicePixelRatio(), "plots": []}
frame = _two_run_frame()
for chart in (ConcentrationChart(), WashInChart()):
    chart.resize(900, 400)
    chart.show()
    chart.draw(frame)
    app.processEvents()
    pens = chart._pens
    report["plots"].append(
        {
            "ratio": pens.device_pixel_ratio,
            "lines": [
                [type(item).__name__, pens.holds(item), drawn.widthF(),
                 pens.specified(item).widthF() if pens.holds(item) else None]
                for item, drawn in _line_items(chart)
            ],
        }
    )
print(json.dumps(report))
"""


@pytest.mark.parametrize("ratio", RATIOS[1:])
def test_on_a_screen_at_each_scale_both_plots_stroke_every_line_at_its_width(ratio: float) -> None:
    """`PL-FSRR`: on a scaled screen, every line of both plots is stroked for that screen.

    `QT_SCALE_FACTOR` sets the offscreen screen's ratio, which Qt's high-DPI
    documentation lists for testing (https://doc.qt.io/qt-6/highdpi.html). A
    widget reads its ratio from its screen, so this needs a process of its own
    for each ratio.
    """

    done = subprocess.run(
        [sys.executable, "-c", _ON_A_SCALED_SCREEN, str(Path(__file__).parent)],
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen", "QT_SCALE_FACTOR": str(ratio)},
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )

    assert done.returncode == 0, done.stderr
    report = json.loads(done.stdout.strip().splitlines()[-1])

    assert report["screen"] == ratio
    assert len(report["plots"]) == 2

    for plot in report["plots"]:
        assert plot["ratio"] == ratio
        assert len(plot["lines"]) > 20

        for name, held, drawn, specified in plot["lines"]:
            assert held, f"{name} draws a line no one keeps to scale"
            assert drawn == specified * ratio, name
