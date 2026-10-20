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
what the formatters say, and that its box, driven to the compartment
chart's four corners and the wash-in plot's two ends, is painted inside the
plot, hiding what is drawn beneath it, its text in `INK`. A pixel snapshot
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
from PySide6.QtGui import QColor, QFontMetrics, QImage, QMouseEvent
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
from anesthesia_sim.app.theme import AGENT_COLOR_SCHEMES, INK, MUTED, ONE_MAC_LINE_COLOR, PANEL
from anesthesia_sim.app.view_registry import AGENT_ACCOUNTING, CONCENTRATION_CHART, WASH_IN
from anesthesia_sim.app.views import ConcentrationView, WashInView
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.layout.model import LayoutModel
from anesthesia_sim.layout.tree import Area, AreaId, Orientation, Split, Window
from anesthesia_sim.layout.workspace import Origin, Workspace, WorkspaceName, WorkspaceSet

#: One Workspace that holds the charts and the accounting. Each test then finds
#: the View it reads, whichever Workspace is shipped first. The concentration
#: chart sits over the F_A/F_I plot, beside the accounting. That was the
#: dashboard's layout before it began opening on the shipped Workspaces
#: (`PL-2KXB`). These tests read no setting control, so the parameter controls
#: are left out and the plots keep the height they were drawn at then.
_EVERY_VIEW = WorkspaceSet(
    (
        Workspace(
            WorkspaceName("Charts and accounting"),
            Origin.mine(),
            LayoutModel(
                (
                    Window(
                        Split(
                            Orientation.ROW,
                            (0.82, 0.18),
                            (
                                Split(
                                    Orientation.COLUMN,
                                    (0.55, 0.45),
                                    (
                                        Area(AreaId(1), CONCENTRATION_CHART),
                                        Area(AreaId(3), WASH_IN),
                                    ),
                                ),
                                Area(AreaId(2), AGENT_ACCOUNTING),
                            ),
                        )
                    ),
                ),
                AreaId(4),
            ),
        ),
    ),
    0,
)

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

#: The run that the hover-box test uses to reach the plot's edges. Sevoflurane
#: is dialled to 8%, its maximum delivered concentration, for twenty minutes,
#: and the run is drawn in the 15-minute width. A chosen width follows the run,
#: so its newest points sit at the right edge. At 8% the circuit and alveolar
#: traces climb to the top of the axis, where there is no room above a point
#: for the box. The right edge and the top of the axis are the two places
#: where the box flips.
_INDUCTION_DIAL_PERCENT = 8.0
_INDUCTION_S = 1200.0
_FOLLOWING_WIDTH_S = 15 * 60

#: How far the box may cross the plot's edge, in pixels: the two rectangles
#: are mapped in floating point, and a box anchored on a point at the edge
#: lands on the edge itself, measured outside by under 0.05 px (`PL-J0F7`).
_EDGE_TOLERANCE_PX = 0.5

#: How many drawn points apart the least-height hover test samples the
#: F_A/F_I stretch: about one point every 25 px of a 1600 px window.
_LEAST_HEIGHT_POINT_STRIDE = 20

#: The height of the tall concentration chart that the resize hover test
#: shrinks, in pixels: tall enough for the box to fit above a point at 0.88
#: of the axis top.
_TALL_CHART_HEIGHT_PX = 700

#: How far inside the box's edge its colours are read: past the one-pixel
#: border and the anti-aliasing either side of it.
_BOX_BORDER_INSET_PX = 2

#: How much of what is drawn beneath a box may still show through it: the
#: text's own pixels land on a few. Measured 0 to 1% with the fill, and 56 to
#: 100% with the fill taken away (`PL-J0F7`).
_SHOWING_THROUGH_FRACTION = 0.05

#: The fewest pixels that must be drawn beneath a box before the test checks the box's fill. With
#: fewer, the test fails, because it could not tell a fill from no fill. When this was set at 100,
#: the six cases had 239 to 3,271 such pixels each. The "top left" box hangs below the circuit
#: trace, so the trace runs along the box's top border. Sub-pixel placement decides whether the
#: trace's pixels fall inside the area the test reads. Rendered in DejaVu Sans alone, that case had
#: 228 pixels beneath the box on `main`. It had 45 once `PL-L59K` moved each run's off-scale and
#: wash-in lines out of the band above the plots and made the plot 25 px taller. CI measured the
#: same 45. With the minimum at 40, the 5% limit still allows only 2 pixels to show through.
_DRAWN_BENEATH_MIN_PX = 40

#: Sixty times the hover's own cooldown of 1/60 s, the longest it holds a
#: pointer position before answering it.
_HOVER_DELIVERY_MS = 1000


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


def _concentration(view: SimulationView) -> ConcentrationView:
    """The concentration chart View in the dashboard's first Area that shows one."""

    return next(v for v in view.layout_container.views() if isinstance(v, ConcentrationView))


def _wash_in(view: SimulationView) -> WashInView:
    """The F_A/F_I View in the dashboard's first Area that shows one."""

    return next(v for v in view.layout_container.views() if isinstance(v, WashInView))


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
        Percent(controller.snapshot().delivered_concentration_percent * 1.5)
    )
    _advance(controller, 180.0)
    view = SimulationView((controller,), workspaces=_EVERY_VIEW)
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
    frame = _concentration(view).chart.frame
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

    The way `QTRY_COMPARE` waits: a move inside the hover's cooldown is
    answered when the cooldown ends, from a timer rather than inside the move,
    and the caller asserts what then holds.
    """

    deadline = QDeadlineTimer(_HOVER_DELIVERY_MS)

    while not condition() and not deadline.hasExpired():
        QTest.qWait(10)


def _painted_with_the_pointer_off(chart: ConcentrationChart | WashInChart) -> QImage:
    """The chart as painted once the pointer has left the plot and the box has gone.

    Over the axis rather than outside the widget, so the move is the plot's
    own and the box answers it by hiding.
    """

    _move_pointer(chart, QPoint(1, 1))
    _wait_for(lambda: chart.hover_text() is None)

    return chart.painted()


def _hover_on(chart: ConcentrationChart | WashInChart, time_s: float, value: float) -> None:
    """Move the pointer onto one drawn point, and wait for the box to answer it."""

    _move_pointer(chart, QPoint(*chart.plot_pixel(time_s, value)))
    _wait_for(lambda: chart.hover_text() is not None)


def _distance(colour: QColor, to: str) -> float:
    other = QColor(to)

    return (
        float(
            (colour.red() - other.red()) ** 2
            + (colour.green() - other.green()) ** 2
            + (colour.blue() - other.blue()) ** 2
        )
        ** 0.5
    )


#: How many paints the page's height is followed for after the first frame.
_FOLLOWED_PAINTS = 5


def _induction_view(application: QApplication) -> SimulationView:
    """`_INDUCTION_DIAL_PERCENT` for `_INDUCTION_S`, paused, in the following 15-minute width.

    The view is paused so that no frame is drawn while the pointer waits on the
    event loop. The points that the pointer is aimed at then stay where they
    were. The view is shown and drawn, and no event-loop pass follows the last
    frame.
    """

    controller = SimulationController(agent_id=_AGENT_ID)
    controller.begin_control_adjustment()
    controller.set_delivered_concentration_percent(Percent(_INDUCTION_DIAL_PERCENT))
    controller.start()
    _advance(controller, _INDUCTION_S)
    controller.pause()
    view = SimulationView((controller,), workspaces=_EVERY_VIEW)
    view.resize(_WINDOW_WIDTH_PX, _WINDOW_HEIGHT_PX)
    view.show()
    application.processEvents()
    view.present(False)
    width = next(base for base in SELECTABLE_TIME_BASES if base.span_s == _FOLLOWING_WIDTH_S)
    # Each chart holds its own window (`PL-L59K`), so both are set, as one
    # shared control set them before.
    for selector in (_concentration(view).time_base_selector, _wash_in(view).time_base_selector):
        index = selector.findData(str(width.span_s))
        assert index >= 0, "the time-base control does not offer the 15-minute width"
        selector.setCurrentIndex(index)

    view.present(False)

    return view


@pytest.fixture
def induction_dashboard(application: QApplication) -> Iterator[SimulationView]:
    """`_induction_view`, painted once, so the plots' pixel mapping is the one drawn."""

    view = _induction_view(application)
    # pyqtgraph's view box updates its mapping from data to pixels only when
    # it is next painted, so the page is painted before a pixel is read.
    view.grab()
    application.processEvents()

    yield view

    view.close()


def test_the_dashboard_page_keeps_its_height_from_its_first_paint(
    application: QApplication,
) -> None:
    """`PL-MXMG`: the page has its final height as soon as a frame is drawn.

    Before the fix, the page sized the Areas from what each View needed before
    Qt had handled the layout requests that the View's frame posted. At that
    point, a per-run line that a chart shows and then hides on its first frame
    still counted. So the page measured 15 px taller for its first paints and
    then shrank. A pixel read off a plot therefore depended on when it was read.
    """

    view = _induction_view(application)

    try:
        _, page = _page(view)
        heights = [page.height()]

        for _ in range(_FOLLOWED_PAINTS):
            view.grab()
            application.processEvents()
            heights.append(page.height())
    finally:
        view.close()

    assert heights == [heights[0]] * len(heights)


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

    chart = _concentration(dashboard).chart
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
    chart = _concentration(dashboard).chart
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


def test_no_readout_value_is_clipped_once_a_run_is_going(dashboard: SimulationView) -> None:
    """The agent-accounting panel gets its whole height once a run is going (`PL-TZNM`).

    A running case writes the lines of the litres readout into the panel. A
    panel laid out from a size hint taken before those lines arrived would
    cut off its last line. The expected heights are the panel's and the
    readout's own size hints, not values read from the layout under test.
    """

    panels = dashboard.runs[0]._accounting_panels

    assert panels

    for panel in panels:
        amounts = panel._agent_amounts_text
        needed_px = (
            amounts.heightForWidth(amounts.width())
            if amounts.wordWrap()
            else amounts.sizeHint().height()
        )

        assert panel.isVisible()
        assert amounts.text()
        assert panel.sizeHint().height() <= panel.height()
        assert needed_px <= amounts.height(), amounts.text()


def test_the_readout_row_and_the_sidebar_are_inside_the_page(dashboard: SimulationView) -> None:
    """Nothing a reader is meant to see is laid out beyond the page's right edge.

    The page is the whole dashboard column: the region pinned above the
    scrolling middle, the middle and the disclaimer below it (`PL-NNML`). It is
    asserted no wider than the window, and the scrolling middle no wider than
    its viewport, so a row that fits only because the page grew past the
    window cannot pass.
    """

    scroll, middle = _page(dashboard)
    page = dashboard.findChild(QWidget, "dashboardPage")
    run = dashboard.runs[0]
    accounting_panel = run._accounting_panels[0]._agent_accounting_status_text.parentWidget()
    timeline_panel = run._control_timeline_text.parentWidget()

    assert page is not None
    assert accounting_panel is not None
    assert timeline_panel is not None
    assert scroll.horizontalScrollBar().maximum() == 0
    assert middle.width() <= scroll.viewport().width()
    assert page.width() <= dashboard.width()
    assert all(_within(panel, page) for panel in run._readout_row.panels)
    assert _within(accounting_panel, page)
    assert _within(timeline_panel, page)


# ------------------------------------------------------------- the hover


def test_the_hover_reports_the_drawn_state_on_the_shipped_chart(dashboard: SimulationView) -> None:
    """A hover on the dashboard's own chart says agent, compartment gloss and both units."""

    chart = _concentration(dashboard).chart
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
    """`PL-J0F7`: at each corner and end the box is painted inside the plot, over what lies beneath.

    The box sits to the right of its point and above it. It flips to the
    left past the middle of the window. It flips below the point where the
    room above the point is less than the box's height (`PL-9BVQ`). So a
    wrong flip would cut the box off at the compartment chart's four
    corners. The right edge matters most, because a following window keeps
    its newest point there and a reader's pointer spends most of its time
    there. The wash-in plot is tested at its two ends, where the left-right
    flip happens. Each case is a point a pointer
    can rest on, its pixel inside the plot: the window's first instant stands
    on the left edge, where its pixel can fall outside and rightly no hover
    answers.

    The plot's background is `PANEL` too, so the fill is held by what it
    hides - the plot painted with the pointer off it, against the plot with
    the box up - and the text by its darkest pixel, which a glyph's stem
    paints in `INK` or close to it in any font, rather than by a count of
    exact `INK` pixels, which a font rendered with sub-pixel smoothing can
    leave at none.
    """

    chart = _concentration(induction_dashboard).chart
    wash_in = _wash_in(induction_dashboard).chart
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
        beneath = _painted_with_the_pointer_off(plot)
        _hover_on(plot, time_s, value)
        unpainted = plot.hover_box()
        shown = plot.painted()
        box = plot.hover_box()
        area = plot.plot_area()

        assert box is not None, f"{name}: no hover answered"
        # The box is placed for the view as it is shown, not at its next paint.
        assert unpainted == box, f"{name}: the box measured {unpainted} before its paint"
        assert area.adjusted(
            -_EDGE_TOLERANCE_PX, -_EDGE_TOLERANCE_PX, _EDGE_TOLERANCE_PX, _EDGE_TOLERANCE_PX
        ).contains(box), f"{name}: the box {box} is not inside the plot {area}"

        inset = _BOX_BORDER_INSET_PX
        inside = [
            (x, y)
            for x in range(ceil(box.left()) + inset, floor(box.right()) - inset)
            for y in range(ceil(box.top()) + inset, floor(box.bottom()) - inset)
        ]
        drawn_beneath = [
            (x, y) for x, y in inside if beneath.pixelColor(x, y).name() != PANEL.lower()
        ]
        showing_through = [
            (x, y) for x, y in drawn_beneath if shown.pixelColor(x, y) == beneath.pixelColor(x, y)
        ]
        colours = Counter(shown.pixelColor(x, y).name() for x, y in inside)
        darkest = min((shown.pixelColor(x, y) for x, y in inside), key=lambda c: c.lightness())

        assert len(drawn_beneath) >= _DRAWN_BENEATH_MIN_PX, f"{name}: too little beneath the box"
        assert len(showing_through) <= _SHOWING_THROUGH_FRACTION * len(drawn_beneath), (
            f"{name}: {len(showing_through)} of {len(drawn_beneath)} pixels show through the box"
        )
        assert colours.most_common(1)[0][0] == PANEL.lower(), (name, colours.most_common(3))
        assert _distance(darkest, INK) < _distance(darkest, MUTED), (
            f"{name}: the text's darkest pixel {darkest.name()} is nearer MUTED than INK"
        )


def test_the_hover_box_stays_inside_a_plot_at_its_least_height(
    application: QApplication, induction_dashboard: SimulationView
) -> None:
    """Every hover box stays inside the F_A/F_I plot at the plot's smallest height (`PL-9BVQ`).

    A reader can drag an Area down to its View's smallest size, which leaves
    the F_A/F_I plot only a few box heights tall. The box goes below its
    point when the room above the point is less than the box's height. When
    the flip was decided at a fraction of the axis instead, a point just
    below the top quarter put the box partly above the plot. The induction
    run's wash-in stretch climbs through that band. So the test hovers over
    sampled points of the stretch, and its highest point, each at a pixel
    inside the plot.
    """

    frame = _wash_in(induction_dashboard).chart.frame
    assert frame is not None
    chart = WashInChart()
    chart.resize(_WINDOW_WIDTH_PX, chart.minimumSizeHint().height())
    chart.show()
    application.processEvents()
    chart.draw(frame)
    chart.grab()
    application.processEvents()
    area = chart.plot_area()
    restable = [
        point
        for point in chart.drawn_stretches(0)[0]
        if area.contains(QPointF(*chart.plot_pixel(*point)))
    ]
    # Every twentieth point, and the stretch's highest, which has the least
    # room above it.
    points = [*restable[::_LEAST_HEIGHT_POINT_STRIDE], max(restable, key=lambda point: point[1])]
    box_height = None
    escaped = []

    for time_s, ratio in points:
        # Off the plot first, so the box measured below is the one this point
        # raised rather than the last point's.
        _painted_with_the_pointer_off(chart)
        _hover_on(chart, time_s, ratio)
        box = chart.hover_box()
        assert box is not None, f"no hover answered at {time_s} s"
        box_height = box.height()

        if not area.adjusted(
            -_EDGE_TOLERANCE_PX, -_EDGE_TOLERANCE_PX, _EDGE_TOLERANCE_PX, _EDGE_TOLERANCE_PX
        ).contains(box):
            escaped.append((time_s, ratio, box))

    # The plot is short enough that a fraction of the axis would have put the
    # box outside it, or the test proves nothing about the flip.
    assert box_height is not None
    assert area.height() < 4 * box_height, (area.height(), box_height)
    assert not escaped, (
        f"{len(escaped)} of {len(points)} boxes leave the plot {area}: {escaped[:3]}"
    )


def test_no_hover_box_is_left_outside_a_plot_that_shrinks_under_a_resting_pointer(
    application: QApplication, induction_dashboard: SimulationView
) -> None:
    """A plot that shrinks under a resting pointer places its hover box again (`PL-9BVQ`).

    On a tall plot there is room for the box above a point high on the axis.
    The reader then shrinks the Area while the run is paused and the pointer
    rests, so no frame is drawn and no pointer event arrives. Before the fix
    the box stayed where the tall plot had put it, with its top cut off above
    the short plot. Now the hover is answered again for the pointer's
    position. That position may no longer be near any drawn point, and then
    no box is the correct result. Either way, no box stands outside the plot.
    """

    frame = _concentration(induction_dashboard).chart.frame
    assert frame is not None
    chart = ConcentrationChart()
    chart.resize(_WINDOW_WIDTH_PX, _TALL_CHART_HEIGHT_PX)
    chart.show()
    application.processEvents()
    chart.draw(frame)
    chart.grab()
    application.processEvents()
    area = chart.plot_area()
    top = frame.axis_top_percent
    # The highest drawn point below 0.88 of the axis top. The tall plot has
    # room above it for the box, and the shortest plot does not.
    time_s, percent = max(
        (
            (time_s, percent)
            for quantity in frame.visible
            for time_s, percent in zip(*chart.drawn_points(0, quantity), strict=True)
            if percent < 0.88 * top and area.contains(QPointF(*chart.plot_pixel(time_s, percent)))
        ),
        key=lambda point: point[1],
    )
    _hover_on(chart, time_s, percent)
    tall_box = chart.hover_box()
    assert tall_box is not None
    assert tall_box.center().y() < chart.plot_pixel(time_s, percent)[1], (
        "the tall plot put it below"
    )

    chart.resize(_WINDOW_WIDTH_PX, chart.minimumSizeHint().height())
    application.processEvents()
    chart.grab()
    application.processEvents()

    short_area = chart.plot_area()
    short_box = chart.hover_box()
    assert short_area.height() < area.height()
    assert short_box is None or short_area.adjusted(
        -_EDGE_TOLERANCE_PX, -_EDGE_TOLERANCE_PX, _EDGE_TOLERANCE_PX, _EDGE_TOLERANCE_PX
    ).contains(short_box), (short_area, short_box)
