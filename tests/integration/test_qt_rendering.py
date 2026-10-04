"""The whole dashboard rendered headless at one fixed size, and read back as pixels.

`tests/integration/test_simulation_view.py` holds what the dashboard's
widgets say; these tests hold what the dashboard *paints*, against a real
run advanced several simulated minutes, under the `offscreen` platform
`tests/conftest.py` selects. They are what lets a session in the web
container review a presentation change at all (`PL-YCWZ`, closing
`PL-2QMK`): the same grab a test reads is the screenshot `docs/worker.md`
tells a session how to write.

What is asserted is chosen for durability rather than pixel-exactness: that
the agent badge is filled in the agent's own colour, that the 1 MAC line is
painted on the row the axis maps its value to, that the alveolar trace stays
inside the plot, that no readout is clipped by its panel, that the row and
the sidebar sit inside the page, that the hover on the shipped chart says
what the formatters say, and that its box, driven to every edge of both
plots, is painted inside the plot in `INK` on `PANEL`. A pixel snapshot
would be brittle across Qt versions and font stacks and would hold nothing
a reader interprets.

The dashboard is shown once for the module, at a size wide enough for the
seven readouts and the sidebar to stand side by side without a horizontal
scroll, and closed at the end. The hover-box test shows one of its own, at
the same size, over a run that reaches the plot's edges.
"""

from collections import Counter
from collections.abc import Callable, Iterable, Iterator
from math import ceil, floor
from pathlib import Path

import pytest
from PySide6.QtCore import QDeadlineTimer, QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QFontMetrics, QImage, QMouseEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel, QScrollArea, QWidget

from anesthesia_sim.app.chart_frame import ChartFrame, format_trace_hover
from anesthesia_sim.app.chart_time_base import SELECTABLE_TIME_BASES
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import SIMULATION_STEP_S
from anesthesia_sim.app.qt_chart import ConcentrationChart, WashInChart
from anesthesia_sim.app.qt_widgets import MetricPanel
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.theme import AGENT_COLOR_SCHEMES, INK, ONE_MAC_LINE_COLOR, PANEL
from anesthesia_sim.core.concentration import Percent

#: The size the dashboard is rendered at. Wide enough that the page's own
#: minimum width - the seven readout panels beside one another, then the
#: chart column beside the sidebar - fits inside the viewport, so the row
#: and the sidebar are asserted inside the page rather than sized to it.
#: The page is taller than this and scrolls; the grab shows its top.
_WINDOW_WIDTH_PX = 1600
_WINDOW_HEIGHT_PX = 1000

#: How far inside the badge's left edge the fill is sampled: past the
#: one-pixel border and before the padding ends and the text begins.
_BADGE_SAMPLE_INSET_PX = 3

#: How many pixels apart the blankness check samples the grab.
_SAMPLE_STRIDE_PX = 8

_AGENT_ID = "sevoflurane"
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

#: The run the hover-box test drives to the plot's edges: sevoflurane dialled
#: to 8%, its maximum delivered concentration, for twenty minutes, then drawn
#: in the 15-minute width. A chosen width follows the run, so its newest
#: points stand at the right edge, and at 8% the circuit and alveolar traces
#: climb into the top quarter of the axis - the two places the box flips.
_INDUCTION_DIAL_PERCENT = 8.0
_INDUCTION_S = 1200.0
_FOLLOWING_WIDTH_S = 15 * 60

#: How far the box may cross the plot's edge, in pixels: the two rectangles
#: are mapped in floating point, and a box anchored on a point at the edge
#: lands on the edge itself, measured outside by under 0.05 px (`PL-J0F7`).
_EDGE_TOLERANCE_PX = 0.5

#: How far inside the box's edge its colours are read: past the one-pixel
#: border and the anti-aliasing either side of it.
_BOX_BORDER_INSET_PX = 2

#: Sixty times the rate-limited hover proxy's own 1/60 s, the longest it
#: holds a pointer position before delivering it from its timer.
_HOVER_DELIVERY_MS = 1000


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


def _advance(controller: SimulationController, seconds: float) -> None:
    for _ in range(round(seconds / SIMULATION_STEP_S)):
        controller.advance(SIMULATION_STEP_S)


@pytest.fixture(scope="module")
def dashboard(application: QApplication) -> Iterator[SimulationView]:
    """The dashboard over one run, five minutes in, a dial change, three more, shown once.

    The order is the one `main.py` follows: show, let the layout settle,
    then present, because the first frame reads the plot's laid-out width.
    """

    controller = SimulationController(agent_id=_AGENT_ID)
    controller.start()
    _advance(controller, 300.0)
    controller.begin_control_adjustment()
    controller.set_delivered_concentration_percent(
        controller.snapshot().delivered_concentration_percent * 1.5
    )
    _advance(controller, 180.0)
    view = SimulationView((controller,))
    view.resize(_WINDOW_WIDTH_PX, _WINDOW_HEIGHT_PX)
    view.show()
    application.processEvents()
    view.present(False)
    application.processEvents()

    yield view

    view.close()


def _page(view: SimulationView) -> tuple[QScrollArea, QWidget]:
    scroll = view.findChild(QScrollArea)
    assert scroll is not None
    page = scroll.widget()
    assert page is not None

    return scroll, page


def _drawn_frame(view: SimulationView) -> ChartFrame:
    frame = view._concentration_chart.frame
    assert frame is not None

    return frame


def _distinct_colours(image: QImage) -> set[str]:
    return {
        image.pixelColor(x, y).name()
        for x in range(0, image.width(), _SAMPLE_STRIDE_PX)
        for y in range(0, image.height(), _SAMPLE_STRIDE_PX)
    }


def _advance_px(label: QLabel) -> int:
    return QFontMetrics(label.font()).horizontalAdvance(label.text())


def _within(widget: QWidget, page: QWidget) -> bool:
    left = widget.mapTo(page, QPoint(0, 0)).x()

    return 0 <= left and left + widget.width() <= page.width()


def _move_pointer(chart: ConcentrationChart | WashInChart, pixel: QPoint) -> None:
    """Move the pointer onto one pixel of a chart, as the platform delivers a move.

    To the widget under that pixel rather than through `QTest.mouseMove`,
    which moves the platform cursor: the offscreen platform gives that move to
    a window it finds at the screen position, and the module's own dashboard
    stands at the same place.
    """

    under = chart.childAt(pixel)
    local = QPointF(under.mapFrom(chart, pixel))
    move = QMouseEvent(
        QEvent.Type.MouseMove,
        local,
        under.mapToGlobal(local),
        Qt.MouseButton.NoButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
    )
    QApplication.sendEvent(under, move)


def _wait_for(condition: Callable[[], bool]) -> None:
    """Run the event loop until `condition` holds or `_HOVER_DELIVERY_MS` has passed.

    The way `QTRY_COMPARE` waits: the pointer's position reaches the hover
    through pyqtgraph's rate-limited `SignalProxy`, which delivers from a
    timer rather than inside the move, and the caller asserts what then holds.
    """

    deadline = QDeadlineTimer(_HOVER_DELIVERY_MS)

    while not condition() and not deadline.hasExpired():
        QTest.qWait(10)


def _hover_over(chart: ConcentrationChart | WashInChart, time_s: float, value: float) -> None:
    """Take the pointer off the plot, then onto one drawn point, and wait for the box to answer.

    Off first, so that the answer waited for cannot be the previous case's
    box still standing.
    """

    _move_pointer(chart, QPoint(1, 1))
    _wait_for(lambda: chart.hover_text() is None)
    _move_pointer(chart, QPoint(*chart.plot_pixel(time_s, value)))
    _wait_for(lambda: chart.hover_text() is not None)


@pytest.fixture
def induction_dashboard(application: QApplication) -> Iterator[SimulationView]:
    """`_INDUCTION_DIAL_PERCENT` for `_INDUCTION_S`, paused, in the following 15-minute width.

    Paused, so that no frame is drawn while the pointer waits on the event
    loop and the points it is aimed at stay where they were.
    """

    controller = SimulationController(agent_id=_AGENT_ID)
    controller.begin_control_adjustment()
    controller.set_delivered_concentration_percent(Percent(_INDUCTION_DIAL_PERCENT))
    controller.start()
    _advance(controller, _INDUCTION_S)
    controller.pause()
    view = SimulationView((controller,))
    view.resize(_WINDOW_WIDTH_PX, _WINDOW_HEIGHT_PX)
    view.show()
    application.processEvents()
    view.present(False)
    width = next(base for base in SELECTABLE_TIME_BASES if base.span_s == _FOLLOWING_WIDTH_S)
    selector = view._time_base_dropdown
    index = selector.findData(str(width.span_s))
    assert index >= 0, "the time-base control does not offer the 15-minute width"
    selector.setCurrentIndex(index)
    view.present(False)
    application.processEvents()
    # A first paint settles the layout, and the plots in it, before a pixel is
    # read off them.
    view.grab()
    application.processEvents()

    yield view

    view.close()


# -------------------------------------------------------------- the grab


def test_the_dashboard_renders_headless_at_a_fixed_size(dashboard: SimulationView) -> None:
    _, page = _page(dashboard)
    image = dashboard.grab().toImage()

    assert page.minimumSizeHint().width() <= _WINDOW_WIDTH_PX
    assert (image.width(), image.height()) == (_WINDOW_WIDTH_PX, _WINDOW_HEIGHT_PX)
    assert len(_distinct_colours(image)) > 1


def test_a_screenshot_of_the_running_interface_can_be_written(
    dashboard: SimulationView, tmp_path: Path
) -> None:
    path = tmp_path / "dashboard.png"

    assert dashboard.grab().save(str(path))
    assert path.stat().st_size > 0
    assert path.read_bytes().startswith(_PNG_SIGNATURE)


# ------------------------------------------------------------ the pixels


def test_the_agent_badge_is_painted_in_the_agents_own_fill(dashboard: SimulationView) -> None:
    badge = dashboard.runs[0]._agent_header_badge
    image = dashboard.grab().toImage()
    sample = badge.mapTo(dashboard, QPoint(_BADGE_SAMPLE_INSET_PX, badge.height() // 2))

    assert image.pixelColor(sample).name() == AGENT_COLOR_SCHEMES[_AGENT_ID].fill.lower()


def test_the_one_mac_line_is_painted_where_the_axis_says(dashboard: SimulationView) -> None:
    """The dashed line stands on the row `plot_pixel` maps `mac_percent` to, three rows deep."""

    chart = dashboard._concentration_chart
    frame = _drawn_frame(dashboard)
    image = chart.painted()
    left_x, y = chart.plot_pixel(frame.start_s, frame.mac_percent)
    right_x, _ = chart.plot_pixel(frame.stop_s, frame.mac_percent)
    along: Counter[str] = Counter()

    for row in (y - 1, y, y + 1):
        along.update(image.pixelColor(x, row).name() for x in range(left_x + 2, right_x - 2))

    # A dash pattern leaves gaps, so a quarter of the row is the bar rather
    # than the whole of it; a single anti-aliased crossing would not reach it.
    assert along[ONE_MAC_LINE_COLOR.lower()] >= (right_x - left_x) // 4, along


def test_the_alveolar_trace_is_drawn_inside_the_plot(dashboard: SimulationView) -> None:
    chart = dashboard._concentration_chart
    frame = _drawn_frame(dashboard)
    times, percents = chart.drawn_points(0, RecordedQuantity.ALVEOLAR)

    assert times
    assert all(0.0 <= percent <= frame.axis_top_percent for percent in percents)

    for time_s, percent in zip(times, percents, strict=True):
        x, y = chart.plot_pixel(time_s, percent)

        assert 0 <= x < chart.width()
        assert 0 <= y < chart.height()


# ------------------------------------------------------------ the layout


def test_no_readout_value_is_clipped_by_its_panel(dashboard: SimulationView) -> None:
    """`PL-3355`: every value and every second unit fits the width its panel gives it."""

    panels = dashboard.runs[0]._readout_row.panels

    assert panels

    for panel in panels:
        assert isinstance(panel, MetricPanel)
        assert panel.minimum_value_width_px <= panel.width()

        for label in (panel.value_label, panel.secondary_label):
            assert label.sizeHint().width() <= label.width(), label.text()
            assert _advance_px(label) <= label.width(), label.text()


def test_the_readout_row_and_the_sidebar_are_inside_the_page(dashboard: SimulationView) -> None:
    """Nothing a reader is meant to see is laid out beyond the page's right edge.

    The page is asserted no wider than the viewport as well, so a row that
    fits the page only because the page grew past the window cannot pass.
    """

    scroll, page = _page(dashboard)
    run = dashboard.runs[0]
    accounting_panel = run._agent_accounting_status_text.parentWidget()
    timeline_panel = run._control_timeline_text.parentWidget()

    assert accounting_panel is not None
    assert timeline_panel is not None
    assert scroll.horizontalScrollBar().maximum() == 0
    assert page.width() <= scroll.viewport().width()
    assert all(_within(panel, page) for panel in run._readout_row.panels)
    assert _within(accounting_panel, page)
    assert _within(timeline_panel, page)


# ------------------------------------------------------------- the hover


def test_the_hover_reports_the_drawn_state_on_the_shipped_chart(dashboard: SimulationView) -> None:
    """A hover on the dashboard's own chart says agent, compartment gloss and both units."""

    chart = dashboard._concentration_chart
    frame = _drawn_frame(dashboard)
    run = frame.runs[0]
    index = len(run.times_s) // 3

    readout = chart.readout_at(run.times_s[index], run.percents(RecordedQuantity.ALVEOLAR)[index])

    assert readout == format_trace_hover(run, RecordedQuantity.ALVEOLAR, index, len(frame.runs))
    assert readout is not None
    context, what, value = readout.splitlines()
    assert context.startswith(f"Modelled {run.agent_display_name.lower()} · ")
    assert what == "Alveolar (end-tidal-equivalent)"
    assert "%" in value
    assert value.endswith(" ×MAC")


def test_the_hover_box_stays_inside_the_plot_at_every_edge(
    induction_dashboard: SimulationView,
) -> None:
    """`PL-J0F7`: at every edge of both plots the box is painted inside the plot, `INK` on `PANEL`.

    The box stands to the right of its point and above it, and flips to the
    left past the middle of the window and below it in the top quarter of the
    axis, so the corners are where a wrong flip would cut it off - the right
    edge most of all, where a following window keeps its newest point and a
    reader's pointer spends most of its time. Each case moves the pointer and
    reads the box back as painted, since pyqtgraph places it for the view only
    as it paints it. Each case is a point a pointer can rest on, its whole
    pixel inside the plot: the window's first instant stands on the left edge,
    where its pixel can fall a fraction outside and rightly no hover answers.
    """

    chart = induction_dashboard._concentration_chart
    wash_in = induction_dashboard._wash_in_chart
    frame = _drawn_frame(induction_dashboard)
    middle = (frame.start_s + frame.stop_s) / 2.0
    quarter = frame.axis_top_percent / 4.0

    def restable(
        plot: ConcentrationChart | WashInChart, points: Iterable[tuple[float, float]]
    ) -> list[tuple[float, float]]:
        area = plot.plot_area()

        return [point for point in points if area.contains(QPointF(*plot.plot_pixel(*point)))]

    def drawn(quantity: RecordedQuantity) -> list[tuple[float, float]]:
        return restable(chart, zip(*chart.drawn_points(0, quantity), strict=True))

    stretch = restable(wash_in, wash_in.drawn_stretches(0)[0])
    cases: dict[str, tuple[ConcentrationChart | WashInChart, tuple[float, float]]] = {
        "top right": (chart, drawn(RecordedQuantity.ALVEOLAR)[-1]),
        "top left": (chart, drawn(RecordedQuantity.CIRCUIT)[0]),
        "bottom right": (chart, drawn(RecordedQuantity.MUSCLE)[-1]),
        "bottom left": (chart, drawn(RecordedQuantity.MUSCLE)[0]),
        "wash-in right": (wash_in, stretch[-1]),
        "wash-in left": (wash_in, stretch[0]),
    }

    # Each point is where its case says, or the case tests nothing.
    for name, (_, (time_s, value)) in cases.items():
        assert (time_s > middle) == name.endswith("right"), name

        if name.startswith("top"):
            assert value > frame.axis_top_percent - quarter, name
        elif name.startswith("bottom"):
            assert value < quarter, name

    for name, (plot, (time_s, value)) in cases.items():
        _hover_over(plot, time_s, value)
        image = plot.painted()
        box = plot.hover_box()
        area = plot.plot_area()

        assert box is not None, f"{name}: no hover answered"
        assert area.adjusted(
            -_EDGE_TOLERANCE_PX, -_EDGE_TOLERANCE_PX, _EDGE_TOLERANCE_PX, _EDGE_TOLERANCE_PX
        ).contains(box), f"{name}: the box {box} is not inside the plot {area}"

        inset = _BOX_BORDER_INSET_PX
        colours = Counter(
            image.pixelColor(x, y).name()
            for x in range(ceil(box.left()) + inset, floor(box.right()) - inset)
            for y in range(ceil(box.top()) + inset, floor(box.bottom()) - inset)
        )

        # The fill is what most of the box is; the text's anti-aliased edges
        # are blends, but where a glyph covers a pixel whole it is the ink.
        assert colours.most_common(1)[0][0] == PANEL.lower(), (name, colours.most_common(3))
        assert colours[INK.lower()] > 0, f"{name}: no pixel of the text is painted in INK"
