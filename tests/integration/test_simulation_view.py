"""The dashboard, driven headless against real runs.

`app/run_view.py` and `app/simulation_view.py` are the toolkit half of the
dashboard: every string and every per-tick claim is settled in
`app/dashboard_frame.py` without a toolkit, and `tests/unit/test_dashboard_frame.py`
holds it there. These tests hold the other half - that the widgets say what
the frame said, that a control a reader moves reaches the run it belongs to
and no other, that the two timer slots keep stepping and drawing apart, that
a refusal is a notice and a raise is a halt - against real
`SimulationController`s, under the `offscreen` platform `tests/conftest.py`
selects.

Ported by claim from the Flet suite this file replaces (`PL-25KS`), keeping
each surviving test's name where a closed item's verify line greps for it.
What is not carried is Flet's own mechanism: wire-protocol patch counts,
per-point tooltip objects, control identity across frames. The one count
that survives is `SimulationView.presented_frames`, which is what the
coalescing rule (`PL-R2YM`) is about.

The dashboard is shown at one fixed size before its first presentation,
because a frame is assembled from the plot's laid-out width and a widget
with no size has no pixels for the hover to measure against.
"""

import importlib
import re
from collections.abc import Iterator, Sequence

import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QComboBox,
    QDialog,
    QLabel,
    QLayout,
    QScrollArea,
    QSplitter,
    QWidget,
)

from anesthesia_sim.app import control_timeline as control_timeline_module
from anesthesia_sim.app import run_view as run_view_module
from anesthesia_sim.app import theme
from anesthesia_sim.app.chart_frame import (
    COMPARED_COMPARTMENT_CAP,
    HOVER_INSTANT_RESOLUTION_S,
    format_trace_hover,
)
from anesthesia_sim.app.chart_time_base import (
    FIT_RUN_KEY,
    SELECTABLE_TIME_BASES,
    time_base_for_span,
)
from anesthesia_sim.app.control_record import ControlChange
from anesthesia_sim.app.control_timeline import ControlAdjustment, group_adjustments
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import (
    INTERPRETATION_DISCLAIMER_TEXT,
    KEEP_CURRENT_CASE_TEMPLATE,
    MAX_DISPLAYED_RUNS,
    NEW_CASE_CARRYOVER_TEMPLATE,
    NEW_CASE_IS_NOT_A_VIEW_TEXT,
    NO_TRACES_SHOWN_TEXT,
    READOUT_PANELS,
    RUNNING_AGENT_LOCK_TEXT,
    SIMULATION_STEP_S,
    SIMULATION_TICK_INTERVAL_S,
    START_NEW_CASE_TEMPLATE,
    slider_position,
)
from anesthesia_sim.app.formatting import (
    CONCENTRATION_DISPLAY_DECIMALS,
    FLOW_DISPLAY_DECIMALS,
    format_case_discard_warning,
    format_elapsed,
    format_flow,
    format_mac_awake_reference,
    format_mac_multiple,
    format_mac_reference,
    format_percent,
    format_playback_rate,
    format_time_base,
    format_wash_in_ratio,
)
from anesthesia_sim.app.playback import (
    DEFAULT_PLAYBACK_RATE,
    SUPPORTED_PLAYBACK_RATES,
    PlaybackRate,
    playback_rate_for,
)
from anesthesia_sim.app.qt_widgets import ParameterSlider
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity
from anesthesia_sim.app.run_view import RunView
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.theme import (
    ACCENT_TEXT,
    AGENT_COLOR_SCHEMES,
    AGENT_SELECTOR_WIDTH,
    INK,
    MUTED,
    PANEL,
    WARNING,
)
from anesthesia_sim.app.wash_in import read_wash_in
from anesthesia_sim.app_metadata import APP_DISPLAY_NAME
from anesthesia_sim.core.concentration import Fraction
from anesthesia_sim.core.exceptions import (
    SimulationConfigurationError,
    SimulationDomainLimitError,
    SimulationExecutionError,
    SimulationNumericalError,
)
from anesthesia_sim.core.parameters import AGENT_DATA_FILENAMES, load_agent_parameters
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MINIMUM_CARDIAC_OUTPUT_L_MIN,
    MINIMUM_FRESH_GAS_FLOW_L_MIN,
)
from anesthesia_sim.core.tissue import TissueGroup
from anesthesia_sim.core.uptake_system import MAXIMUM_SIMULATION_STEP_S, AgentUptakeSystem

# The size every dashboard here is shown at: wide enough for the seven
# readouts to stand side by side and for a chart column with pixels to
# measure hover distances in.
_WINDOW_WIDTH_PX = 1400
_WINDOW_HEIGHT_PX = 1000

#: The two required glosses, restated rather than imported so an edit to the
#: application cannot move both sides of the assertion at once.
_ALVEOLAR_METRIC_QUALIFIER = "end-tidal-equivalent"
#: Any spelling of end-tidal not followed by the hedge, anywhere on screen.
_UNHEDGED_END_TIDAL = re.compile(r"end[\s-]?tidal(?!-equivalent)", re.IGNORECASE)

#: The index of each readout panel in the row, from the table the widgets are
#: built from, so a test names a compartment rather than a column number.
_READOUT_INDEX = {panel.quantity: index for index, panel in enumerate(READOUT_PANELS)}
_CLOCK_INDEX = _READOUT_INDEX[None]


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


#: The dashboards `_shown_view` built and has not yet deleted. A view left to
#: the garbage collector is deleted whenever a collection happens to run -
#: inside a later test's `show()`, or at interpreter shutdown after Qt's own
#: statics have gone - and either is a fatal error rather than a failure. So
#: a view is held here and deleted deliberately: before the next dashboard is
#: shown, and the last one in `_torn_down_views`, each time with the event
#: loop still able to deliver the deferred deletion. One at a time rather
#: than all at the end, because draining a hundred deferred deletions in one
#: call took twenty seconds where one takes twenty milliseconds.
_SHOWN_VIEWS: list[SimulationView] = []


def _delete_shown_views(application: QApplication) -> None:
    for view in _SHOWN_VIEWS:
        view.stop_timers()
        view.close()
        view.deleteLater()

    _SHOWN_VIEWS.clear()
    application.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    application.processEvents()


@pytest.fixture(scope="module", autouse=True)
def _torn_down_views(application: QApplication) -> Iterator[None]:
    yield

    _delete_shown_views(application)


# ------------------------------------------------------------------ helpers


def _advance(controller: SimulationController, seconds: float) -> None:
    for _ in range(round(seconds / SIMULATION_STEP_S)):
        controller.advance(SIMULATION_STEP_S)


def _advance_to(controller: SimulationController, elapsed_s: float) -> None:
    while controller.snapshot().elapsed_s < elapsed_s - SIMULATION_STEP_S / 2.0:
        controller.advance(SIMULATION_STEP_S)


def _shown_view(
    application: QApplication, *controllers: SimulationController, width_px: int = _WINDOW_WIDTH_PX
) -> SimulationView:
    """A dashboard over these runs, shown at the fixed size and presented once.

    The order is the one `main.py` follows: show, let the layout settle, then
    present, because the first frame reads the plot's laid-out width.
    """

    _delete_shown_views(application)
    view = SimulationView(controllers)
    _SHOWN_VIEWS.append(view)
    view.resize(width_px, _WINDOW_HEIGHT_PX)
    view.show()
    application.processEvents()
    view.present(False)

    return view


def _settle(application: QApplication) -> None:
    """Deliver the deferred deletions and events an action has posted."""

    application.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    application.processEvents()


def _widest_chord_px(view: SimulationView) -> int:
    """The widest gap, in plot pixels, between two consecutive drawn alveolar instants."""

    chart = view._concentration_chart
    times, percents = chart.drawn_points(0, RecordedQuantity.ALVEOLAR)
    xs = [
        chart.plot_pixel(time_s, percent)[0]
        for time_s, percent in zip(times, percents, strict=True)
    ]

    return max(right - left for left, right in zip(xs, xs[1:], strict=False))


def _page_of(view: SimulationView) -> QWidget:
    """The scrolling page the dashboard lays itself out on."""

    scroll = view.findChild(QScrollArea)
    assert scroll is not None, "the dashboard has no scroll area"
    page = scroll.widget()
    assert page is not None, "the scroll area holds no page"

    return page


def _stacked_sections(view: SimulationView) -> QSplitter:
    """The vertical splitter of readouts, settings and the chart row."""

    vertical = [
        splitter
        for splitter in view.findChildren(QSplitter)
        if splitter.orientation() == Qt.Orientation.Vertical
    ]
    assert len(vertical) == 1, "the dashboard stacks its sections in exactly one splitter"

    return vertical[0]


def _steps(run: RunView, ticks: int) -> None:
    for _ in range(ticks):
        run.step_tick()


def _readout_value(run: RunView, quantity: RecordedQuantity) -> str:
    return run._readout_row.panels[_READOUT_INDEX[quantity]].value_label.text()


def _readout_secondary(run: RunView, quantity: RecordedQuantity) -> str:
    return run._readout_row.panels[_READOUT_INDEX[quantity]].secondary_label.text()


def _drag(control: ParameterSlider, value: float, decimals: int) -> None:
    """Move a slider the way a reader's drag reaches it: through the QSlider itself.

    Through the control the run actually holds and the signal it actually
    wired, so the tests assert the wiring as well as the effect: a handler
    bound to the wrong run is exactly the mistake a comparison of two runs
    has to be proof against.
    """

    control.slider.setValue(slider_position(value, decimals))


def _set_fresh_gas_flow(run: RunView, flow_l_min: float) -> None:
    _drag(run._fresh_gas_flow_slider, flow_l_min, FLOW_DISPLAY_DECIMALS)


def _set_delivered_percent(run: RunView, percent: float) -> None:
    _drag(run._delivered_concentration_slider, percent, CONCENTRATION_DISPLAY_DECIMALS)


def _select_playback_rate(run: RunView, multiplier: int) -> None:
    combo = run._playback_rate_dropdown
    index = combo.findData(multiplier)
    assert index >= 0, f"the playback control does not offer {multiplier}x"
    combo.setCurrentIndex(index)


def _select_time_base(view: SimulationView, key: str) -> None:
    combo = view._time_base_dropdown
    index = combo.findData(key)
    assert index >= 0, f"the time-base control does not offer {key!r}"
    combo.setCurrentIndex(index)


def _set_trace_shown(
    application: QApplication, view: SimulationView, quantity: RecordedQuantity, shown: bool
) -> None:
    """Check or uncheck one compartment in the legend, as a reader clicking would.

    Through the box rather than through `set_shown`, because the two are
    different acts once the two-compartment cap is holding: a click keeps
    what was just asked for and drops the longest-standing selection, where
    a bulk set has no order of preference to read.
    """

    view._legend.set_compartment_shown(quantity, shown)
    application.processEvents()


def _paused_run_with_history(elapsed_s: float = 60.0) -> SimulationController:
    """A real, paused run holding both elapsed time and a recorded input.

    Both halves deliberately: `SimulationSnapshot.has_recorded_run` reads
    the two together, and a fixture carrying only one would leave the other
    unexercised by every test built on it.
    """

    controller = SimulationController()
    controller.start()
    _advance_to(controller, elapsed_s)
    controller.set_fresh_gas_flow(2.0)
    controller.pause()

    return controller


def _select_agent(run: RunView, agent_id: str) -> None:
    """Pick an agent from the selector, through the combo's own signal."""

    combo = run._agent_dropdown
    index = combo.findData(agent_id)
    assert index >= 0, f"the selector does not offer {agent_id!r}"

    if index == combo.currentIndex():
        # A combo reports no change on the same item, and a reader opening
        # and closing it on the running agent still reaches the handler.
        run._handle_agent_change(index)
    else:
        combo.setCurrentIndex(index)


def _colour_name(value: object) -> str:
    """One spelling for a colour however the widget layer stores it."""

    if isinstance(value, QBrush):
        value = value.color()

    if isinstance(value, QColor):
        return value.name().lower()

    return QColor(str(value)).name().lower()


def _identity_controls(run: RunView) -> tuple[QWidget, ...]:
    """The six controls `_apply_agent_color_scheme` writes, and nothing else."""

    return (
        run._agent_header_badge,
        run._subtitle_text,
        run._running_agent_display,
        run._running_agent_text,
        run._running_agent_lock_text,
        run._agent_dropdown,
    )


def _interface_strings(view: SimulationView) -> set[str]:
    return set(view.interface_strings())


def _strings_of(widget: QWidget, skip: Sequence[QWidget]) -> set[str]:
    """Every string a widget subtree shows, skipping `skip` by identity."""

    strings: set[str] = set()
    widgets = [widget, *widget.findChildren(QWidget)]

    for child in widgets:
        if any(child is skipped for skipped in skip):
            continue

        if isinstance(child, QLabel | QAbstractButton):
            strings.add(child.text())
        elif isinstance(child, QComboBox):
            strings.update(child.itemText(index) for index in range(child.count()))

    return strings


def _strings_between(
    after: QWidget | None, before: QWidget, *, skip: Sequence[QWidget] = ()
) -> set[str]:
    """The strings laid out between two widgets of one column, in layout order.

    Walks the layout of the widget that holds `before`, recursing into
    nested layouts and into any widget that contains a boundary, so the
    result is what a reader passes between the two on screen.
    """

    column = before.parentWidget()
    assert column is not None, "the plot has no parent to walk"
    layout = column.layout()
    assert layout is not None, "the plot's parent has no layout to walk"
    strings: set[str] = set()
    collecting = after is None

    def contains(widget: QWidget, boundary: QWidget) -> bool:
        return widget is boundary or widget.isAncestorOf(boundary)

    def walk(items: QLayout) -> bool:
        nonlocal collecting

        for index in range(items.count()):
            item = items.itemAt(index)
            if item is None:
                continue
            nested = item.layout()
            widget = item.widget()

            if nested is not None:
                if walk(nested):
                    return True
                continue

            if widget is None:
                continue

            if widget is before:
                return True

            if after is not None and widget is after:
                collecting = True
                continue

            if contains(widget, before) or (after is not None and contains(widget, after)):
                inner = widget.layout()
                assert inner is not None
                if walk(inner):
                    return True
                continue

            if collecting:
                strings.update(_strings_of(widget, skip))

        return False

    assert walk(layout), "the walk never reached the plot it was to stop at"

    return strings


def _real_step_failure() -> SimulationNumericalError:
    """Capture the exception the core actually raises on a broken step.

    Reusing the real exception rather than inventing one keeps these tests
    tied to what `core/` does: if the core stopped raising a
    `SimulationNumericalError` here, this helper fails rather than letting
    the interface tests pass against a fiction. The failure is injected,
    because the exact propagator cannot carry a compartment out of range on
    its own (`PL-GS5X`); what is stood in for is what the guard remains
    cover for.
    """

    system = AgentUptakeSystem.for_agent("isoflurane")
    original = system.patient.fat

    class _FatThatRefusesTheStep(TissueGroup):
        def set_partial_pressure_fraction(self, partial_pressure_fraction: Fraction) -> None:
            super().set_partial_pressure_fraction(Fraction(-1.0))

    system.patient.fat = _FatThatRefusesTheStep(
        name=original.name,
        volume_l=original.volume_l,
        perfusion_fraction=original.perfusion_fraction,
        blood_gas_partition_coefficient=original.blood_gas_partition_coefficient,
        tissue_gas_partition_coefficient=original.tissue_gas_partition_coefficient,
        blood_flow_l_min=original.blood_flow_l_min,
    )

    try:
        system.advance(MAXIMUM_SIMULATION_STEP_S)
    except SimulationNumericalError as error:
        return error

    raise AssertionError("expected the coupled step to be refused by the fat compartment")


class _StepFailingController(SimulationController):
    """A real controller whose next `advance()` raises, once."""

    def __init__(self, error: Exception) -> None:
        super().__init__()
        self._pending_error: Exception | None = error

    def advance(self, simulation_step_s: float) -> None:
        if self._pending_error is not None:
            error, self._pending_error = self._pending_error, None
            raise error

        super().advance(simulation_step_s)


# ------------------------------------------------------- the constructor


def test_a_dashboard_refuses_to_be_built_with_no_run() -> None:
    """A dashboard with no run has no agent, no ruler and nothing to draw."""

    with pytest.raises(
        ValueError, match=re.escape("a dashboard displays at least one run; none was given")
    ):
        SimulationView(())


def test_a_dashboard_refuses_more_runs_than_may_be_displayed() -> None:
    """`ROADMAP.md` bounds the comparison at two, and the cap is why.

    At three runs the encoding that tells one from another has nothing left:
    colour and line style carry the compartment and line width is a two-level
    channel. A third curve would be drawn with nothing identifying it.
    """

    assert MAX_DISPLAYED_RUNS == 2

    with pytest.raises(
        ValueError,
        match=re.escape(f"3 runs given; at most {MAX_DISPLAYED_RUNS} may be displayed at once"),
    ):
        SimulationView(tuple(SimulationController() for _ in range(MAX_DISPLAYED_RUNS + 1)))


def test_a_dashboard_refuses_two_runs_on_different_agents() -> None:
    """One ×MAC ruler and one set of references cannot describe two agents.

    Two agents on one chart would leave one run's traces read against the
    other's divisor - a correct number under the wrong label, which
    `CLAUDE.md`'s standard treats as a failure of the value.
    """

    with pytest.raises(
        ValueError,
        match=re.escape(
            "every displayed run must be on the same agent, because they share one MAC axis "
            "and one set of clinical references; given desflurane, sevoflurane"
        ),
    ):
        SimulationView((SimulationController(), SimulationController(agent_id="desflurane")))


# --------------------------------------------------------- the transport


def test_every_transport_button_declares_its_own_foreground(application: QApplication) -> None:
    """None of the three is left to take its label colour from the host palette.

    `PL-DHBX`: a button that declares no foreground is drawn in Qt's palette
    `ButtonText` role, which follows the host appearance rather than this
    interface, and went near-white under macOS Dark while every surface around
    it stayed this light theme's. Both states are asserted because the defect
    arrived twice - declaring `:enabled` alone left the *unavailable* button
    still absent on the project owner's screen.

    `transport_button_stylesheet` carries the colours; this holds `RunView` to
    applying them, which is the half a test of the helper alone would not catch.
    """

    view = _shown_view(application, SimulationController())
    run = view.runs[0]
    transport = (run._start_button, run._pause_button, run._reset_button)

    for button in transport:
        sheet = button.styleSheet()

        assert f"QPushButton:enabled {{ color: {INK}; }}" in sheet
        assert f"QPushButton:disabled {{ color: {MUTED}; }}" in sheet
        assert f"background-color: {PANEL}" in sheet


def test_start_pause_reset_handlers_drive_the_real_controller(application: QApplication) -> None:
    """Each button reaches the run through its own click, and draws its own frame."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    presented = view.presented_frames

    run._start_button.click()

    assert controller.is_running is True
    assert run._status_text.text() == "Running"
    assert run._start_button.isEnabled() is False
    assert run._pause_button.isEnabled() is True
    assert view.presented_frames == presented + 1

    _steps(run, 10)
    run._pause_button.click()

    assert controller.is_running is False
    assert run._status_text.text() == "Paused"
    assert view.presented_frames == presented + 2

    run._reset_button.click()

    assert controller.snapshot().elapsed_s == 0.0
    assert run._elapsed_time_text.text() == "0s"
    assert view.presented_frames == presented + 3


def test_the_status_word_is_drawn_in_its_own_emphasis(application: QApplication) -> None:
    """Running in accent, paused in muted: the word and its colour move together."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]

    assert MUTED in run._status_text.styleSheet()

    run._start_button.click()

    assert ACCENT_TEXT in run._status_text.styleSheet()
    assert MUTED not in run._status_text.styleSheet()


# ------------------------------------------------------------ the sliders


def test_the_integer_sliders_span_the_supported_input_ranges(application: QApplication) -> None:
    """Read off the constructed controls, not off module constants."""

    run = _shown_view(application, SimulationController()).runs[0]

    for control, minimum, maximum in (
        (run._fresh_gas_flow_slider, MINIMUM_FRESH_GAS_FLOW_L_MIN, MAXIMUM_FRESH_GAS_FLOW_L_MIN),
        (
            run._alveolar_ventilation_slider,
            MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
            MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
        ),
        (run._cardiac_output_slider, MINIMUM_CARDIAC_OUTPUT_L_MIN, MAXIMUM_CARDIAC_OUTPUT_L_MIN),
    ):
        assert control.slider.minimum() == slider_position(minimum, FLOW_DISPLAY_DECIMALS)
        assert control.slider.maximum() == slider_position(maximum, FLOW_DISPLAY_DECIMALS)


def test_every_slider_endpoint_reaches_the_core_and_is_accepted(application: QApplication) -> None:
    """The interface must not offer a position the model refuses."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]

    for control in (
        run._fresh_gas_flow_slider,
        run._alveolar_ventilation_slider,
        run._cardiac_output_slider,
        run._delivered_concentration_slider,
    ):
        for endpoint in (control.slider.minimum(), control.slider.maximum()):
            control.slider.setValue(endpoint)

            assert run._rejected_setting_notice is None, (
                f"the core refused {endpoint}, an endpoint of a slider the interface offers: "
                f"{run._rejected_setting_notice}"
            )


def test_fresh_gas_flow_slider_forwards_value_to_controller(application: QApplication) -> None:
    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]

    _set_fresh_gas_flow(run, 7.0)

    assert controller.snapshot().fresh_gas_flow_l_min == 7.0
    assert run._fresh_gas_flow_slider.value_label.text() == "7.0 L/min"


def test_the_delivered_dial_reaches_the_core_as_a_fraction(application: QApplication) -> None:
    """The dial is in percent; the model is set in fractions of one atmosphere."""

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]

    _set_delivered_percent(run, 6.5)

    assert controller.snapshot().delivered_partial_pressure_fraction == pytest.approx(0.065)
    assert run._delivered_concentration_slider.value_label.text() == "6.50%"


def test_alveolar_ventilation_slider_forwards_value_to_controller(
    application: QApplication,
) -> None:
    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]

    _drag(run._alveolar_ventilation_slider, 8.0, FLOW_DISPLAY_DECIMALS)

    assert controller.snapshot().alveolar_ventilation_l_min == 8.0
    assert run._alveolar_ventilation_slider.value_label.text() == "8.0 L/min"


def test_cardiac_output_slider_forwards_value_to_controller(application: QApplication) -> None:
    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]

    _drag(run._cardiac_output_slider, 6.5, FLOW_DISPLAY_DECIMALS)

    assert controller.snapshot().cardiac_output_l_min == 6.5
    assert run._cardiac_output_slider.value_label.text() == "6.5 L/min"


def test_the_sliders_declare_an_adjustment_boundary_when_a_drag_begins(
    application: QApplication,
) -> None:
    """Without it two turns of one dial are one adjustment on the record.

    Each slider's press is wired to the boundary, so a second act on the
    same control after a press is a second adjustment. Observed through the
    controller rather than by inspecting the connection, which PySide6 does
    not expose.
    """

    for slider_name in (
        "_fresh_gas_flow_slider",
        "_delivered_concentration_slider",
        "_alveolar_ventilation_slider",
        "_cardiac_output_slider",
    ):
        controller = SimulationController()
        run = _shown_view(application, controller).runs[0]
        controller.start()
        controller.set_fresh_gas_flow(3.0)
        controller.advance(SIMULATION_STEP_S)

        control: ParameterSlider = getattr(run, slider_name)
        control.slider.sliderPressed.emit()
        controller.set_fresh_gas_flow(2.0)

        assert {change.adjustment for change in controller.snapshot().control_timeline} == {1, 2}, (
            f"{slider_name}'s press did not declare an adjustment boundary"
        )


def test_a_declared_boundary_reaches_the_controller(application: QApplication) -> None:
    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]

    controller.start()
    controller.set_fresh_gas_flow(3.0)
    controller.advance(SIMULATION_STEP_S)
    run._handle_adjustment_start()
    controller.set_fresh_gas_flow(2.0)

    assert {change.adjustment for change in controller.snapshot().control_timeline} == {1, 2}


def test_a_drag_of_one_slider_is_marked_and_listed_once(application: QApplication) -> None:
    """One act by the person, however many settings the model was stepped under."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()
    _advance(controller, 10.0)

    run._delivered_concentration_slider.slider.sliderPressed.emit()

    for percent in (3.0, 3.5, 4.0):
        _set_delivered_percent(run, percent)
        controller.advance(SIMULATION_STEP_S)

    view.present(False)

    assert len(run._control_timeline_text.text().splitlines()) == 1
    assert view._concentration_chart.control_mark_times(0) == (pytest.approx(10.0),)
    assert view._wash_in_chart.control_mark_times(0) == (pytest.approx(10.0),)


# ---------------------------------------------- refusals, and the halt


def test_a_refused_setting_is_reported_without_stopping_the_run(application: QApplication) -> None:
    """Isoflurane's vaporizer stops at 5%, so 50% must be refused.

    Called on the handler rather than dragged, because the slider's own
    ceiling keeps 50% unreachable on the control - which is exactly why the
    handler needs its own cover.
    """

    controller = SimulationController(agent_id="isoflurane")
    run = _shown_view(application, controller).runs[0]
    controller.start()
    delivered_before = controller.snapshot().delivered_partial_pressure_fraction

    run._handle_delivered_concentration_change(50.0)

    assert controller.is_running is True
    assert controller.has_failed is False
    assert run._status_text.text() == "Running"
    assert run._notice_text.isHidden() is False
    notice = run._notice_text.notice()
    assert notice is not None
    assert "Setting refused" in notice
    assert "vaporizer maximum" in notice

    # The control must not keep showing a dial position the simulation is
    # not running at: that is the correct number under the wrong label.
    assert controller.snapshot().delivered_partial_pressure_fraction == delivered_before
    assert run._delivered_concentration_slider.value() == pytest.approx(delivered_before * 100.0)


def test_a_refusal_notice_clears_once_a_setting_is_accepted(application: QApplication) -> None:
    controller = SimulationController(agent_id="isoflurane")
    run = _shown_view(application, controller).runs[0]

    run._handle_delivered_concentration_change(50.0)
    assert run._notice_text.isHidden() is False

    run._handle_delivered_concentration_change(2.0)

    assert run._notice_text.isHidden() is True
    assert controller.snapshot().delivered_partial_pressure_fraction == pytest.approx(0.02)


@pytest.mark.parametrize(
    ("handler_name", "slider_name"),
    [
        ("_handle_fresh_gas_flow_change", "_fresh_gas_flow_slider"),
        ("_handle_alveolar_ventilation_change", "_alveolar_ventilation_slider"),
        ("_handle_cardiac_output_change", "_cardiac_output_slider"),
    ],
)
def test_every_slider_handler_refuses_without_escaping_into_the_toolkit(
    application: QApplication, handler_name: str, slider_name: str
) -> None:
    """No setting slot may let a core raise reach Qt's dispatcher.

    The sliders' own bounds keep a negative flow unreachable in the running
    app, which is exactly why the guard needs its own cover: an exception
    escaping a slot is lost under PySide6 rather than shown.
    """

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    controller.start()

    getattr(run, handler_name)(-1.0)

    assert controller.is_running is True
    assert controller.has_failed is False
    assert run._notice_text.isHidden() is False
    notice = run._notice_text.notice()
    assert notice is not None
    assert "Setting refused" in notice
    control: ParameterSlider = getattr(run, slider_name)
    assert control.value() >= 0.0


def test_a_refused_setting_reaches_the_notice_through_apply_setting(
    application: QApplication,
) -> None:
    """A `SimulationConfigurationError` is a refusal: the run is untouched."""

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    controller.start()

    def refuse() -> None:
        raise SimulationConfigurationError("a value the core refused")

    run._apply_setting(refuse)

    assert controller.has_failed is False
    assert controller.is_running is True
    assert run._rejected_setting_notice == "Setting refused — a value the core refused"


def test_an_execution_error_in_a_setting_halts_the_run_through_apply_setting(
    application: QApplication,
) -> None:
    """`PL-V6M0`: an execution error is not a refusal and must not read as one."""

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    controller.start()

    def explode() -> None:
        raise SimulationExecutionError("the run cannot continue safely")

    run._apply_setting(explode)

    assert controller.snapshot().failure_reason == (
        "SimulationExecutionError: the run cannot continue safely"
    )
    assert controller.is_running is False
    assert run._rejected_setting_notice is None


def test_a_domain_limit_in_a_setting_reaches_the_supported_limit_channel_through_apply_setting(
    application: QApplication,
) -> None:
    """A domain limit stops the run as a limit, never as a failure (`PL-Y5WR`)."""

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    controller.start()

    def limit() -> None:
        raise SimulationDomainLimitError("this run has reached 86400 s of simulated time")

    run._apply_setting(limit)

    assert controller.snapshot().supported_limit_reason == (
        "this run has reached 86400 s of simulated time"
    )
    assert controller.has_failed is False
    assert controller.is_running is False
    assert run._rejected_setting_notice is None


def test_a_type_error_in_a_setting_halts_the_run_through_apply_setting(
    application: QApplication,
) -> None:
    """`PL-YK2V`: a raise from outside the project hierarchy still halts the run."""

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    controller.start()

    def explode() -> None:
        raise TypeError("a future refactor changed a signature")

    run._apply_setting(explode)

    assert controller.snapshot().failure_reason == (
        "TypeError: a future refactor changed a signature"
    )
    assert controller.is_running is False
    assert run._rejected_setting_notice is None


def test_halt_run_stops_the_session_and_records_the_exception_type(
    application: QApplication,
) -> None:
    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    controller.start()

    run._halt_run(ValueError("mass balance violated"))

    assert controller.snapshot().failure_reason == "ValueError: mass balance violated"
    assert controller.is_running is False


def test_halt_run_survives_a_render_failure_and_leaves_the_run_stopped(
    application: QApplication,
) -> None:
    """A halt that cannot draw its frame is still a halt."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()

    def explode() -> None:
        raise RuntimeError("the page is gone")

    view._refresh_view = explode  # type: ignore[method-assign]

    run._halt_run(ValueError("mass balance violated"))

    assert controller.snapshot().failure_reason == "ValueError: mass balance violated"
    assert controller.is_running is False


# -------------------------------------------------------------- the loops


def test_simulation_loop_advances_without_rendering(application: QApplication) -> None:
    """Stepping must not be gated on drawing."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()
    presented = view.presented_frames

    _steps(view.runs[0], 3)

    assert controller.snapshot().elapsed_s > 0.0
    assert view.presented_frames == presented


def test_render_loop_draws_without_advancing(application: QApplication) -> None:
    """Drawing must not move simulation time."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()
    presented = view.presented_frames

    view.render_tick()
    view.render_tick()

    assert controller.snapshot().elapsed_s == 0.0
    assert view.presented_frames >= presented + 1


def test_neither_loop_does_anything_while_paused(application: QApplication) -> None:
    controller = SimulationController()
    view = _shown_view(application, controller)
    presented = view.presented_frames

    _steps(view.runs[0], 2)
    view.render_tick()

    assert controller.snapshot().elapsed_s == 0.0
    assert view.presented_frames == presented


def test_a_dragged_slider_leaves_its_frame_to_the_render_tick(application: QApplication) -> None:
    """`PL-R2YM`: a drag updates its own readout at once and defers the frame.

    What must still be immediate is the view beside the dial, which has to
    agree with the snapshot the moment the setting is applied (`PL-018`).
    What waits is the presentation - chart assembly, draw and captions.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()
    presented = view.presented_frames

    _set_fresh_gas_flow(run, 7.0)

    assert controller.snapshot().fresh_gas_flow_l_min == 7.0
    assert run._fresh_gas_flow_slider.value_label.text() == "7.0 L/min"
    assert view.presented_frames == presented
    assert view._render_pending is True


def test_a_refused_slider_change_draws_its_own_frame(application: QApplication) -> None:
    """The one state the coalescing rule may not defer.

    A refused setting is the only case where the dial on screen and the
    simulation disagree; waiting even a tick there leaves a control stating
    a setting the run is not using.
    """

    controller = SimulationController(agent_id="isoflurane")
    view = _shown_view(application, controller)
    run = view.runs[0]
    presented = view.presented_frames

    run._handle_delivered_concentration_change(50.0)

    assert run._notice_text.isHidden() is False
    assert view.presented_frames == presented + 1
    assert view._render_pending is False


def test_the_frame_that_clears_a_refusal_is_drawn_too(application: QApplication) -> None:
    """The same fault backwards: a notice left up after it stopped being true."""

    controller = SimulationController(agent_id="isoflurane")
    view = _shown_view(application, controller)
    run = view.runs[0]

    run._handle_delivered_concentration_change(50.0)
    presented = view.presented_frames

    run._handle_delivered_concentration_change(2.0)

    assert run._notice_text.isHidden() is True
    assert view.presented_frames == presented + 1


def test_a_discrete_action_still_draws_its_own_frame(application: QApplication) -> None:
    """Only a control that reports continuously coalesces."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    presented = view.presented_frames

    view.runs[0]._start_button.click()

    assert controller.is_running
    assert view.presented_frames == presented + 1
    assert view._render_pending is False


def test_the_render_tick_draws_a_pending_change_while_the_run_is_stopped(
    application: QApplication,
) -> None:
    """The bound has to hold on the pause-change-resume route as well.

    Paused there is no run to draw, but there is still a dial moving, so the
    tick fires for a change that is owed a frame - and stops once it has.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)

    _set_fresh_gas_flow(view.runs[0], 7.0)
    assert view._render_pending is True
    presented = view.presented_frames

    view.render_tick()

    assert view.presented_frames == presented + 1
    assert view._render_pending is False

    view.render_tick()

    assert view.presented_frames == presented + 1, (
        "the tick kept drawing a paused run with nothing owed"
    )


def test_simulation_time_does_not_depend_on_render_cadence(application: QApplication) -> None:
    """Identical step counts must give identical results, however drawing goes.

    `PL-VM40`: simulation time is a function of steps taken, never of the
    wall clock or of how many frames were drawn between them.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()

    for _ in range(5):
        view.runs[0].step_tick()
        view.render_tick()

    steps_taken = round(controller.snapshot().elapsed_s / SIMULATION_STEP_S)
    reference = SimulationController()
    reference.start()
    _advance(reference, steps_taken * SIMULATION_STEP_S)

    assert controller.snapshot().elapsed_s == reference.snapshot().elapsed_s
    assert (
        controller.snapshot().alveolar_partial_pressure_fraction
        == reference.snapshot().alveolar_partial_pressure_fraction
    )


def test_the_run_loop_takes_one_step_per_tick_at_real_time_and_never_catches_up(
    application: QApplication,
) -> None:
    """A late tick must cost the run real time, never change its trajectory.

    How many steps a tick takes is the reader's playback setting rather
    than a function of how long the tick took, so a host that wakes it late
    leaves the run behind the wall clock and it stays behind.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()

    ticks = 7
    _steps(view.runs[0], ticks)

    assert controller.snapshot().elapsed_s == ticks * SIMULATION_STEP_S
    assert round(controller.snapshot().elapsed_s / SIMULATION_STEP_S) == ticks


@pytest.mark.parametrize(
    "rate",
    SUPPORTED_PLAYBACK_RATES,
    ids=[f"{rate.multiplier}x" for rate in SUPPORTED_PLAYBACK_RATES],
)
def test_the_run_loop_takes_the_playback_rates_steps_per_tick(
    application: QApplication, rate: PlaybackRate, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The multiplier is steps per tick, and the step never moves (`PL-SN2C`)."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    view.runs[0]._playback_rate = rate
    controller.start()

    steps_requested: list[float] = []
    advance = controller.advance

    def recording_advance(simulation_step_s: float) -> None:
        steps_requested.append(simulation_step_s)
        advance(simulation_step_s)

    monkeypatch.setattr(controller, "advance", recording_advance)

    ticks = 3
    _steps(view.runs[0], ticks)

    steps_per_tick = rate.steps_per_tick(
        tick_interval_s=SIMULATION_TICK_INTERVAL_S, simulation_step_s=SIMULATION_STEP_S
    )
    expected_steps = ticks * steps_per_tick

    assert steps_per_tick == rate.multiplier
    assert len(steps_requested) == expected_steps
    assert set(steps_requested) == {SIMULATION_STEP_S}
    assert controller.snapshot().elapsed_s == expected_steps * SIMULATION_STEP_S
    assert round(controller.snapshot().elapsed_s / SIMULATION_STEP_S) == expected_steps


def test_a_failed_step_abandons_the_rest_of_its_tick(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A burst is not a licence to step past a step the core could not take.

    The run must stop on the last completed step, exactly as it does at real
    time, and nothing after the raise runs in this tick or the next.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    view.runs[0]._playback_rate = playback_rate_for(60)
    controller.start()

    calls = 0
    advance = controller.advance

    def failing_advance(simulation_step_s: float) -> None:
        nonlocal calls
        calls += 1

        if calls == 5:
            raise _real_step_failure()

        advance(simulation_step_s)

    monkeypatch.setattr(controller, "advance", failing_advance)

    _steps(view.runs[0], 2)

    assert calls == 5
    assert controller.snapshot().elapsed_s == 4 * SIMULATION_STEP_S
    assert controller.is_running is False


def test_a_failed_step_stops_the_run_instead_of_killing_the_loop(application: QApplication) -> None:
    """`PL-018`: a core failure must never leave a stale "Running" display."""

    controller = _StepFailingController(_real_step_failure())
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()
    presented = view.presented_frames

    _steps(run, 3)

    assert controller.is_running is False
    assert controller.has_failed is True
    assert run._status_text.text() == "Stopped — simulation error"
    assert WARNING in run._status_text.styleSheet()
    assert run._notice_text.isHidden() is False
    notice = run._notice_text.notice()
    assert notice is not None
    assert "SimulationNumericalError" in notice
    # The failure was drawn, not just recorded.
    assert view.presented_frames >= presented + 1


def test_the_simulation_loop_survives_a_failure_so_reset_can_restart_it(
    application: QApplication,
) -> None:
    """The tick slot must keep working after a halt, or Reset restarts nothing."""

    controller = _StepFailingController(_real_step_failure())
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()

    _steps(run, 3)
    assert controller.has_failed is True

    run._reset_button.click()
    run._start_button.click()
    _steps(run, 3)

    assert controller.has_failed is False
    assert controller.snapshot().elapsed_s > 0.0
    assert run._status_text.text() == "Running"
    assert run._notice_text.isHidden() is True


def test_a_failed_render_stops_the_run_rather_than_freezing_the_display(
    application: QApplication,
) -> None:
    """A dead render loop over a live simulation is the mirror failure."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()

    real_refresh_view = view._refresh_view
    failures_left = [1]

    def failing_refresh_view() -> None:
        if failures_left[0]:
            failures_left[0] -= 1
            raise RuntimeError("chart series could not be updated")

        real_refresh_view()

    view._refresh_view = failing_refresh_view  # type: ignore[method-assign]

    view.render_tick()
    view.render_tick()

    assert controller.is_running is False
    assert controller.has_failed is True
    assert run._status_text.text() == "Stopped — simulation error"
    notice = run._notice_text.notice()
    assert notice is not None
    assert "RuntimeError" in notice


def test_a_frame_that_cannot_be_drawn_on_a_discrete_action_halts_every_run(
    application: QApplication,
) -> None:
    """A discrete action presents through a signal, and a slot's raise is printed and dropped.

    So the immediate presentation guards itself as the render tick does:
    without that, a frame that could not be drawn for a playback change
    would leave every run advancing behind a display that had stopped.
    """

    first = SimulationController()
    second = SimulationController()
    first.start()
    second.start()
    view = _shown_view(application, first, second)

    real_refresh_view = view._refresh_view
    failures_left = [1]

    def failing_refresh_view() -> None:
        if failures_left[0]:
            failures_left[0] -= 1
            raise RuntimeError("the frame could not be built")

        real_refresh_view()

    view._refresh_view = failing_refresh_view  # type: ignore[method-assign]

    _select_playback_rate(view.runs[0], SUPPORTED_PLAYBACK_RATES[-1].multiplier)

    assert failures_left == [0], "the playback change did not present at once"

    for controller in (first, second):
        assert controller.is_running is False
        assert controller.has_failed is True
        assert controller.snapshot().failure_reason == "RuntimeError: the frame could not be built"

    for run in view.runs:
        assert run._status_text.text() == "Stopped — simulation error"
        notice = run._notice_text.notice()
        assert notice is not None
        assert "RuntimeError" in notice


def test_a_halt_whose_frame_cannot_be_drawn_is_still_shown_on_every_run(
    application: QApplication,
) -> None:
    """The frame is the shared render path, and a halt for its raise cannot wait for it.

    Every controller is failed; what a reader has to see is the status word
    and the banner saying so, which need no frame. With one run's refresh
    raising on every attempt, the halt's own presentation raises too and is
    swallowed - and before `present_halt`, both status words went on
    reading the state before the raise with no banner under either.
    """

    first = SimulationController()
    second = SimulationController()
    first.start()
    second.start()
    view = _shown_view(application, first, second)

    def failing_refresh(snapshot: object, frame: object, run_index: int) -> None:
        raise RuntimeError("this run's widgets could not be written")

    view.runs[0].refresh = failing_refresh  # type: ignore[method-assign]

    view.render_tick()

    for controller in (first, second):
        assert controller.is_running is False
        assert controller.has_failed is True

    for run in view.runs:
        assert run._status_text.text() == "Stopped — simulation error"
        notice = run._notice_text.notice()
        assert notice is not None
        assert "RuntimeError: this run's widgets could not be written" in notice
        assert run._pause_button.isEnabled() is False
        assert run._start_button.isEnabled() is False


def test_two_runs_that_come_to_be_on_different_agents_halt_visibly(
    application: QApplication,
) -> None:
    """The same failure through a real refusal rather than a patched one.

    `assemble_chart_frame` refuses two runs on two agents on every attempt,
    so the halt it causes can never be drawn as a frame; each run still says
    it stopped, and why, from its own snapshot.
    """

    first = SimulationController()
    second = SimulationController()
    view = _shown_view(application, first, second)
    second.set_agent("desflurane")
    first.start()

    view.render_tick()

    for controller in (first, second):
        assert controller.is_running is False
        assert controller.has_failed is True
        reason = controller.snapshot().failure_reason
        assert reason is not None
        assert reason.startswith("ValueError")

    for run in view.runs:
        assert run._status_text.text() == "Stopped — simulation error"
        notice = run._notice_text.notice()
        assert notice is not None
        assert "ValueError" in notice


def test_a_resize_while_paused_redraws_the_frame_for_the_new_width(
    application: QApplication,
) -> None:
    """`PL-GS3R`: no chord wider than a pixel, at the width the plot has now.

    A frame is assembled for the width it is drawn on, so the one on screen
    is right for that width only. Paused, with nothing owed, nothing would
    redraw after a resize, and the columns drawn for the narrow plot would
    stand on the wide one at twice the chord.
    """

    controller = _paused_run_with_history()
    view = _shown_view(application, controller, width_px=800)
    presented = view.presented_frames

    view.resize(1600, _WINDOW_HEIGHT_PX)
    application.processEvents()

    assert _widest_chord_px(view) > 1, "the resize did not widen the plot under the old frame"

    view.render_tick()

    assert view.presented_frames == presented + 1
    assert _widest_chord_px(view) <= 1

    view.render_tick()

    assert view.presented_frames == presented + 1, "the tick kept drawing with nothing owed"


# ---------------------------------------------------------- the playback


def test_the_default_playback_rate_is_real_time(application: QApplication) -> None:
    run = _shown_view(application, SimulationController()).runs[0]

    assert run._playback_rate == DEFAULT_PLAYBACK_RATE
    assert run._playback_rate.multiplier == 1


def test_every_supported_playback_rate_is_offered_by_the_control(application: QApplication) -> None:
    combo = _shown_view(application, SimulationController()).runs[0]._playback_rate_dropdown

    assert [combo.itemData(index) for index in range(combo.count())] == [
        rate.multiplier for rate in SUPPORTED_PLAYBACK_RATES
    ]
    assert [combo.itemText(index) for index in range(combo.count())] == [
        format_playback_rate(rate.multiplier) for rate in SUPPORTED_PLAYBACK_RATES
    ]


def test_the_control_and_the_clock_state_the_rate_identically(application: QApplication) -> None:
    run = _shown_view(application, SimulationController()).runs[0]
    combo = run._playback_rate_dropdown
    offered = {combo.itemData(index): combo.itemText(index) for index in range(combo.count())}

    _select_playback_rate(run, 60)

    assert run._playback_rate_text.text() == offered[60]


def test_selecting_a_rate_changes_the_loop_and_the_readout_together(
    application: QApplication,
) -> None:
    run = _shown_view(application, SimulationController()).runs[0]

    _select_playback_rate(run, 60)

    assert run._playback_rate.multiplier == 60
    assert run._playback_rate_text.text() == format_playback_rate(60)

    _select_playback_rate(run, 1)

    assert run._playback_rate.multiplier == 1
    assert run._playback_rate_text.text() == format_playback_rate(1)


def test_the_mounted_interface_states_the_playback_rate(application: QApplication) -> None:
    view = _shown_view(application, SimulationController())

    assert format_playback_rate(1) in _interface_strings(view)


def test_the_playback_control_is_never_disabled(application: QApplication) -> None:
    """A view control stays live while the run's own controls lock."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()
    view.present(False)

    assert view.runs[0]._agent_dropdown.isEnabled() is False
    assert view.runs[0]._playback_rate_dropdown.isEnabled() is True


def test_reset_leaves_the_playback_rate_alone(application: QApplication) -> None:
    run = _shown_view(application, SimulationController()).runs[0]

    _select_playback_rate(run, 20)
    run._reset_button.click()

    assert run._playback_rate == playback_rate_for(20)
    assert run._playback_rate_text.text() == format_playback_rate(20)


# ---------------------------------------------------- the agent selector


def test_agent_dropdown_options_pair_every_color_with_the_agent_name(
    application: QApplication,
) -> None:
    """Colour is a redundant cue: every option pairs the name with its ISO 5360 pair."""

    combo = _shown_view(application, SimulationController()).runs[0]._agent_dropdown
    keys = [combo.itemData(index) for index in range(combo.count())]

    assert keys == list(AGENT_DATA_FILENAMES)
    assert set(keys) == set(AGENT_COLOR_SCHEMES)

    for index, agent_id in enumerate(keys):
        scheme = AGENT_COLOR_SCHEMES[agent_id]

        assert combo.itemText(index) == load_agent_parameters(agent_id).display_name
        assert _colour_name(combo.itemData(index, Qt.ItemDataRole.BackgroundRole)) == (
            _colour_name(scheme.fill)
        )
        assert _colour_name(combo.itemData(index, Qt.ItemDataRole.ForegroundRole)) == (
            _colour_name(scheme.foreground)
        )


def test_refresh_view_shows_current_agent_in_subtitle_and_dropdown(
    application: QApplication,
) -> None:
    run = _shown_view(application, SimulationController(agent_id="isoflurane")).runs[0]
    scheme = AGENT_COLOR_SCHEMES["isoflurane"]

    assert "Isoflurane" in run._subtitle_text.text()
    assert run._agent_dropdown.currentData() == "isoflurane"
    assert scheme.fill in run._agent_header_badge.styleSheet()
    assert scheme.foreground in run._subtitle_text.styleSheet()
    assert scheme.fill in run._agent_dropdown.styleSheet()
    assert scheme.foreground in run._agent_dropdown.styleSheet()


@pytest.mark.parametrize("agent_id", list(AGENT_COLOR_SCHEMES))
def test_refresh_view_applies_current_agent_color_to_control_and_header(
    application: QApplication, agent_id: str
) -> None:
    run = _shown_view(application, SimulationController(agent_id=agent_id)).runs[0]
    scheme = AGENT_COLOR_SCHEMES[agent_id]

    assert run._agent_dropdown.currentData() == agent_id
    assert scheme.fill in run._agent_dropdown.styleSheet()
    assert scheme.foreground in run._agent_dropdown.styleSheet()
    assert scheme.fill in run._agent_header_badge.styleSheet()
    assert scheme.foreground in run._subtitle_text.styleSheet()
    assert load_agent_parameters(agent_id).display_name in run._subtitle_text.text()


@pytest.mark.parametrize("agent_id", list(AGENT_COLOR_SCHEMES))
def test_agent_header_badge_is_bordered_against_the_panel(
    application: QApplication, agent_id: str
) -> None:
    """Sevoflurane's fill is 1.37:1 on the panel, so the badge carries a border."""

    run = _shown_view(application, SimulationController(agent_id=agent_id)).runs[0]
    scheme = AGENT_COLOR_SCHEMES[agent_id]

    assert re.search(
        rf"border:\s*1px solid {re.escape(scheme.foreground)}", run._agent_header_badge.styleSheet()
    ), run._agent_header_badge.styleSheet()


@pytest.mark.parametrize("agent_id", list(AGENT_COLOR_SCHEMES))
def test_every_agent_has_render_objects_in_its_own_identification_color(
    application: QApplication, agent_id: str
) -> None:
    """The six identity controls carry the running agent's pair, and only its pair."""

    run = _shown_view(application, SimulationController(agent_id=agent_id)).runs[0]
    scheme = AGENT_COLOR_SCHEMES[agent_id]

    for control in _identity_controls(run):
        assert scheme.fill in control.styleSheet(), control
        assert scheme.foreground in control.styleSheet(), control

        for other_id, other in AGENT_COLOR_SCHEMES.items():
            if other_id != agent_id and other.fill != scheme.fill:
                assert other.fill not in control.styleSheet(), (control, other_id)


def test_switching_agent_repaints_the_header_badge_and_the_dropdown(
    application: QApplication,
) -> None:
    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    scheme = AGENT_COLOR_SCHEMES["desflurane"]

    _select_agent(run, "desflurane")

    assert controller.snapshot().agent_id == "desflurane"
    assert run._agent_dropdown.currentData() == "desflurane"
    assert "Desflurane" in run._subtitle_text.text()

    for control in _identity_controls(run):
        assert scheme.fill in control.styleSheet(), control
        assert scheme.foreground in control.styleSheet(), control


def test_refresh_view_disables_agent_dropdown_while_running(application: QApplication) -> None:
    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()
    view.present(False)

    assert view.runs[0]._agent_dropdown.isEnabled() is False
    assert view.runs[0]._agent_dropdown.isHidden() is True


@pytest.mark.parametrize("agent_id", list(AGENT_COLOR_SCHEMES))
def test_the_agent_name_stays_legible_while_the_run_disables_the_selector(
    application: QApplication, agent_id: str
) -> None:
    """`PL-61WW`: a disabled selector repaints the identity colour in a theme grey.

    So while the run locks the selector, the agent is named by a chip that
    is neither disabled nor greyed, in the agent's own pair, where the
    selector stood.
    """

    controller = SimulationController(agent_id=agent_id)
    view = _shown_view(application, controller)
    run = view.runs[0]
    scheme = AGENT_COLOR_SCHEMES[agent_id]
    controller.start()
    view.present(False)

    assert run._running_agent_display.isHidden() is False
    assert run._running_agent_display.isEnabled() is True
    assert scheme.fill in run._running_agent_display.styleSheet()
    assert run._running_agent_text.text() == load_agent_parameters(agent_id).display_name
    assert scheme.foreground in run._running_agent_text.styleSheet()
    assert scheme.foreground in run._running_agent_lock_text.styleSheet()
    assert run._agent_dropdown.isHidden() is True


@pytest.mark.parametrize("running", [False, True])
def test_exactly_one_of_the_selector_and_the_running_agent_display_is_shown(
    application: QApplication, running: bool
) -> None:
    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]

    if running:
        controller.start()
        view.present(False)

    assert run._agent_dropdown.isHidden() is not run._running_agent_display.isHidden()
    assert run._running_agent_display.isHidden() is not running


def test_the_running_agent_display_says_why_the_selector_is_gone(application: QApplication) -> None:
    controller = SimulationController(agent_id="desflurane")
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()
    view.present(False)

    assert run._running_agent_text.text() == "Desflurane"
    assert run._running_agent_lock_text.text() == RUNNING_AGENT_LOCK_TEXT
    assert run._running_agent_display.minimumWidth() == AGENT_SELECTOR_WIDTH
    assert run._running_agent_display.maximumWidth() == AGENT_SELECTOR_WIDTH
    assert run._agent_dropdown.minimumWidth() == AGENT_SELECTOR_WIDTH
    assert run._agent_dropdown.maximumWidth() == AGENT_SELECTOR_WIDTH


def test_the_running_agent_display_is_already_correct_before_it_is_shown(
    application: QApplication,
) -> None:
    """The chip is written every tick, so the frame that shows it has nothing to fix."""

    run = _shown_view(application, SimulationController(agent_id="isoflurane")).runs[0]
    scheme = AGENT_COLOR_SCHEMES["isoflurane"]

    assert run._running_agent_display.isHidden() is True
    assert scheme.fill in run._running_agent_display.styleSheet()
    assert run._running_agent_text.text() == "Isoflurane"
    assert scheme.foreground in run._running_agent_text.styleSheet()


def test_building_a_run_view_opens_no_window_of_its_own(application: QApplication) -> None:
    """A widget shown before a layout adopts it is a top-level window.

    The selector and the chip have their visibility written as the view is
    built, before any layout places them, so each is built with the view as
    its parent; a parentless one shown there opened a window of its own
    beside the dashboard (`PL-25KS`).
    """

    host = QWidget()
    windows_before = len(application.topLevelWindows())

    run = RunView(SimulationController(), host)
    application.processEvents()

    assert len(application.topLevelWindows()) == windows_before
    assert run.parent() is host

    host.deleteLater()
    _settle(application)


def test_the_delivered_label_on_screen_names_the_current_agent(application: QApplication) -> None:
    """Regression for a label hardcoded to "Delivered sevoflurane"."""

    run = _shown_view(application, SimulationController(agent_id="desflurane")).runs[0]

    assert run._delivered_concentration_slider.name_label.text() == "Delivered desflurane"


def test_a_built_in_agent_without_an_identification_colour_fails_at_import() -> None:
    """Adding an agent without its ISO 5360 colour must stop the app starting.

    The guard runs at module scope, so covering it means re-executing the
    module body with the colour table short one entry, and reloading again
    afterwards so the genuine table is what every later test sees.
    """

    original = dict(theme.AGENT_COLOR_SCHEMES)
    theme.AGENT_COLOR_SCHEMES.pop(next(iter(original)))
    try:
        with pytest.raises(
            RuntimeError,
            match="^AGENT_COLOR_SCHEMES must define exactly the built-in volatile agents$",
        ):
            importlib.reload(run_view_module)
    finally:
        theme.AGENT_COLOR_SCHEMES.clear()
        theme.AGENT_COLOR_SCHEMES.update(original)
        importlib.reload(run_view_module)


# ---------------------------------------------------- the new-case flow


def test_agent_dropdown_handler_switches_the_real_controller(application: QApplication) -> None:
    """A never-started run has nothing to lose, so the switch is immediate."""

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")

    assert controller.snapshot().agent_id == "desflurane"
    assert run._agent_dropdown.currentData() == "desflurane"
    assert "Desflurane" in run._subtitle_text.text()
    assert run._new_case_dialog is None


def test_a_recorded_run_is_not_discarded_before_the_reader_has_answered(
    application: QApplication,
) -> None:
    """`PL-R3KB`: selecting an agent rebuilds nothing until it is confirmed."""

    controller = _paused_run_with_history()
    before = controller.snapshot()
    run_before = (controller.snapshot().elapsed_s, controller.run_segments)
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")

    after = controller.snapshot()
    assert after.agent_id == before.agent_id
    assert after.elapsed_s == before.elapsed_s
    assert (controller.snapshot().elapsed_s, controller.run_segments) == run_before
    assert run._new_case_dialog is not None
    assert run._new_case_dialog.isVisible() is True
    # The selector reads the agent that is actually running, not the one
    # being offered, for as long as the question is open.
    assert run._agent_dropdown.currentData() == before.agent_id


def test_a_declined_agent_change_leaves_the_run_and_the_selector_untouched(
    application: QApplication,
) -> None:
    """Declining costs nothing: the run, its history and the selector stand."""

    controller = _paused_run_with_history()
    before = controller.snapshot()
    run_before = (controller.snapshot().elapsed_s, controller.run_segments)
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    assert dialog.keep_button.text() == KEEP_CURRENT_CASE_TEMPLATE.format(agent="sevoflurane")
    dialog.keep_button.click()

    after = controller.snapshot()
    assert after.agent_id == "sevoflurane"
    assert after.elapsed_s == before.elapsed_s
    assert after.control_timeline == before.control_timeline
    assert (controller.snapshot().elapsed_s, controller.run_segments) == run_before
    assert run._agent_dropdown.currentData() == "sevoflurane"
    assert "Sevoflurane" in run._subtitle_text.text()
    assert dialog.isVisible() is False
    assert run._new_case_dialog is None


def test_a_confirmed_agent_change_starts_the_new_case(application: QApplication) -> None:
    """Confirming does what the selector used to do on its own."""

    controller = _paused_run_with_history()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    assert dialog.discard_button.text() == START_NEW_CASE_TEMPLATE.format(agent="desflurane")
    dialog.discard_button.click()

    after = controller.snapshot()
    assert after.agent_id == "desflurane"
    assert after.elapsed_s == 0.0
    assert after.control_timeline == ()
    assert run._agent_dropdown.currentData() == "desflurane"
    assert run._delivered_concentration_slider.name_label.text() == "Delivered desflurane"
    assert dialog.isVisible() is False
    assert run._new_case_dialog is None


def test_the_dismissal_that_follows_a_confirmed_switch_does_not_undo_it(
    application: QApplication,
) -> None:
    """A dialog reports its close after the button that closed it.

    That report reaches the declining branch, so without the guard in
    `_resolve_new_case` it would run over the case that had just started.
    """

    controller = _paused_run_with_history()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    dialog.accept()

    run._resolve_new_case(False)

    assert controller.snapshot().agent_id == "desflurane"
    assert run._agent_dropdown.currentData() == "desflurane"


def test_dismissing_the_confirmation_keeps_the_current_case(application: QApplication) -> None:
    """A dialog closed by anything but its buttons has chosen nothing."""

    controller = _paused_run_with_history()
    before = controller.snapshot()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    dialog.reject()

    assert controller.snapshot().agent_id == before.agent_id
    assert controller.snapshot().elapsed_s == before.elapsed_s
    assert run._agent_dropdown.currentData() == before.agent_id
    assert run._new_case_dialog is None


@pytest.mark.parametrize("answer", ["keep", "discard"])
def test_an_answered_confirmation_is_gone_from_the_view_and_its_strings(
    application: QApplication, answer: str
) -> None:
    """A question that has been answered is not part of the interface.

    Deleted once its `finished` has been read, or every confirmation ever
    asked stays a child of the run: its title on `interface_strings` and its
    widgets in every walk of the tree (`PL-25KS`).
    """

    controller = _paused_run_with_history()
    view = _shown_view(application, controller)
    run = view.runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    title = dialog.windowTitle()
    assert title in view.interface_strings()

    (dialog.keep_button if answer == "keep" else dialog.discard_button).click()
    _settle(application)

    assert run.findChildren(QDialog) == []
    assert title not in view.interface_strings()
    assert controller.snapshot().agent_id == ("sevoflurane" if answer == "keep" else "desflurane")


def test_a_selection_while_a_confirmation_is_open_does_not_retarget_its_answer(
    application: QApplication,
) -> None:
    """The open dialog names one agent, and its answer starts that agent and no other.

    A second selection while the question stands is reverted and not
    answered; before the guard it opened a second dialog and moved the
    pending agent, so the first dialog's discard started the second agent.
    """

    controller = _paused_run_with_history()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    first = run._new_case_dialog
    assert first is not None

    _select_agent(run, "isoflurane")

    assert run._new_case_dialog is first
    assert run.findChildren(QDialog) == [first]
    assert run._agent_dropdown.currentData() == "sevoflurane"

    first.discard_button.click()

    assert controller.snapshot().agent_id == "desflurane"


def test_reselecting_the_running_agent_discards_nothing_and_asks_nothing(
    application: QApplication,
) -> None:
    """A selector opened and closed on the same option reports a selection."""

    controller = _paused_run_with_history()
    before = controller.snapshot()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "sevoflurane")

    after = controller.snapshot()
    assert after.agent_id == before.agent_id
    assert after.elapsed_s == before.elapsed_s
    assert after.control_timeline == before.control_timeline
    assert run._new_case_dialog is None


def test_the_dialog_quotes_the_time_and_the_changes_the_panel_shows(
    application: QApplication,
) -> None:
    """What is about to be lost is stated in the run's own displayed terms."""

    controller = _paused_run_with_history(elapsed_s=125.0)
    snapshot = controller.snapshot()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    warning = dialog.body_labels[1].text()

    assert warning == format_case_discard_warning(
        "Sevoflurane", snapshot.elapsed_s, len(group_adjustments(snapshot.control_timeline))
    )
    assert format_elapsed(snapshot.elapsed_s) in warning


def test_the_dialog_names_both_agents_and_what_survives_the_switch(
    application: QApplication,
) -> None:
    controller = _paused_run_with_history()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    body = [label.text() for label in dialog.body_labels]

    assert dialog.title_label.text() == "Start a new desflurane case?"
    assert body[0] == NEW_CASE_IS_NOT_A_VIEW_TEXT
    assert "sevoflurane" in body[1]
    assert body[2] == NEW_CASE_CARRYOVER_TEMPLATE.format(agent="desflurane")
    assert dialog.isModal() is True


def test_the_open_confirmations_buttons_carry_both_outcomes_and_default_to_keeping(
    application: QApplication,
) -> None:
    """The press a reader makes without reading keeps their case."""

    controller = _paused_run_with_history()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None

    assert dialog.discard_button.text() == "Discard and start desflurane"
    assert dialog.keep_button.text() == "Keep the sevoflurane case"
    assert dialog.keep_button.isDefault() is True
    assert dialog.discard_button.isDefault() is False


# ------------------------------------------------------- the readouts


def test_the_readouts_say_they_are_model_outputs_beside_the_values(
    application: QApplication,
) -> None:
    """`PL-2K1R`: the interpretation line sits on the readout section's heading row.

    Once, beside the values it qualifies, rather than at the foot of the
    page where a repeated disclaimer stops being read.
    """

    run = _shown_view(application, SimulationController()).runs[0]

    assert run._interpretation_text.text() == INTERPRETATION_DISCLAIMER_TEXT
    heading_row = run._interpretation_text.parentWidget()
    assert heading_row is not None
    assert run._compartment_substance_text.parentWidget() is heading_row
    assert run._readout_row.parentWidget() in (heading_row, heading_row.parentWidget()), (
        "the interpretation line is not in the section that holds the readout row"
    )


def test_the_hover_readout_states_the_agent_compartment_and_both_units(
    application: QApplication,
) -> None:
    """`PL-YVHK`: a hover over a drawn point names what it is, in both units.

    Through the dashboard rather than the bare chart, so the shipped
    composition is what answers, and against the frame it drew, so the
    readout is the state the run was evaluated at rather than a position
    between two. A drawn instant is a grid column's rather than a step's,
    so the time the readout states is the instant at the hover's own
    resolution, not the column's raw time.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    view = _shown_view(application, controller)
    chart = view._concentration_chart
    frame = chart.frame
    assert frame is not None
    run = frame.runs[0]
    index = len(run.times_s) // 2
    time_s = run.times_s[index]
    fraction = run.fractions[RecordedQuantity.ALVEOLAR][index]

    readout = chart.readout_at(time_s, run.percents(RecordedQuantity.ALVEOLAR)[index])

    assert readout is not None
    assert readout == format_trace_hover(run, RecordedQuantity.ALVEOLAR, index)
    context, what, value = readout.splitlines()
    instant_s = round(time_s / HOVER_INSTANT_RESOLUTION_S) * HOVER_INSTANT_RESOLUTION_S
    assert "sevoflurane" in context
    assert format_elapsed(instant_s) in context
    assert "Alveolar" in what
    assert _ALVEOLAR_METRIC_QUALIFIER in what
    assert format_percent(fraction) in value
    assert format_mac_multiple(fraction, controller.snapshot().agent_mac_percent) in value


def test_hiding_a_trace_changes_only_what_is_drawn(application: QApplication) -> None:
    """Unchecking a compartment takes its curve off and touches nothing else."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 120.0)
    view = _shown_view(application, controller)
    run = view.runs[0]
    chart = view._concentration_chart
    snapshot = controller.snapshot()
    before = {
        quantity: chart.drawn_points(0, quantity)
        for quantity in COMPARTMENT_QUANTITIES
        if quantity is not RecordedQuantity.FAT
    }

    _set_trace_shown(application, view, RecordedQuantity.FAT, False)

    assert chart.drawn_points(0, RecordedQuantity.FAT) == ((), ())

    for quantity, (times, percents) in before.items():
        redrawn_times, redrawn_percents = chart.drawn_points(0, quantity)

        assert redrawn_times == pytest.approx(times)
        assert redrawn_percents == pytest.approx(percents)

    assert _readout_value(run, RecordedQuantity.CIRCUIT) == format_percent(
        snapshot.inspired_partial_pressure_fraction
    )
    assert _readout_value(run, RecordedQuantity.MUSCLE) == format_percent(
        snapshot.muscle_partial_pressure_fraction
    )
    assert _readout_value(run, RecordedQuantity.FAT) == format_percent(
        snapshot.fat_partial_pressure_fraction
    )


def test_the_hidden_traces_advisory_is_present_always_and_shown_only_when_nothing_is_drawn(
    application: QApplication,
) -> None:
    """A plot missing all six is a blank panel, and a blank panel reads as a failure."""

    view = _shown_view(application, SimulationController())

    assert view._hidden_traces_text.isHidden() is True
    assert NO_TRACES_SHOWN_TEXT in _interface_strings(view)

    view._legend.set_shown(())
    application.processEvents()

    assert view._hidden_traces_text.isHidden() is False
    frame = view._concentration_chart.frame
    assert frame is not None
    assert frame.visible == ()

    _set_trace_shown(application, view, RecordedQuantity.ALVEOLAR, True)

    assert view._hidden_traces_text.isHidden() is True


def test_a_trace_above_the_axis_is_reported_on_the_run_that_drew_it(
    application: QApplication,
) -> None:
    """The off-scale notice is a per-run advisory, written from the drawn frame.

    Sevoflurane's 8% dial is 4 MAC against a 3 MAC ceiling: after ten
    minutes the circuit is above the axis and the alveolar trace is inside
    it, so the notice names one and not the other.
    """

    controller = SimulationController()
    controller.start()
    controller.set_delivered_partial_pressure_fraction(Fraction(0.08))
    _advance(controller, 600.0)
    view = _shown_view(application, controller)
    run = view.runs[0]

    assert run._off_scale_text.isHidden() is False
    assert "Circuit" in run._off_scale_text.text()
    assert "Alveolar" not in run._off_scale_text.text()
    assert "readouts above" in run._off_scale_text.text()

    _set_trace_shown(application, view, RecordedQuantity.CIRCUIT, False)

    assert run._off_scale_text.isHidden() is True


def test_the_control_timeline_is_not_regrouped_when_it_has_not_grown(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`PL-1PSX`: a frame in which nobody touched a control pays nothing for the record."""

    controller = SimulationController()
    controller.start()

    for index in range(4):
        controller.begin_control_adjustment()
        controller.set_fresh_gas_flow(4.0 - (index + 1) * 0.1)
        _advance(controller, 1.0)

    view = _shown_view(application, controller)

    regroups = 0
    real = control_timeline_module.group_adjustments

    def counted(recorded: Sequence[ControlChange]) -> tuple[ControlAdjustment, ...]:
        nonlocal regroups
        regroups += 1
        return real(recorded)

    monkeypatch.setattr(control_timeline_module, "group_adjustments", counted)

    view.present(False)
    view.present(False)
    view.present(False)

    assert regroups == 0
    # The panel is still written from the grouping, so this is a cache
    # serving the right answer rather than a frame that stopped drawing.
    assert view.runs[0]._control_timeline_text.text().splitlines()[0].startswith("3s")


# ------------------------------------------------ the charts, integrated


def test_the_chart_defaults_to_fitting_the_whole_run(application: QApplication) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 1200.0)
    view = _shown_view(application, controller)
    frame = view._concentration_chart.frame

    assert view._time_base_dropdown.currentData() == FIT_RUN_KEY
    assert view._time_base is None
    assert frame is not None
    assert frame.fitted is True
    assert frame.start_s == 0.0
    assert frame.stop_s >= 1200.0


def test_the_time_base_selector_offers_fit_run_and_the_settled_widths(
    application: QApplication,
) -> None:
    combo = _shown_view(application, SimulationController())._time_base_dropdown

    assert [combo.itemData(index) for index in range(combo.count())] == [
        FIT_RUN_KEY,
        *(str(time_base.span_s) for time_base in SELECTABLE_TIME_BASES),
    ]
    assert [combo.itemText(index) for index in range(combo.count())] == [
        "Fit run",
        *(format_time_base(time_base.span_s) for time_base in SELECTABLE_TIME_BASES),
    ]


def test_selecting_a_time_base_makes_the_window_exactly_that_wide(
    application: QApplication,
) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    view = _shown_view(application, controller)

    for time_base in SELECTABLE_TIME_BASES:
        _select_time_base(view, str(time_base.span_s))
        frame = view._concentration_chart.frame

        assert frame is not None
        assert frame.fitted is False
        assert frame.stop_s - frame.start_s == pytest.approx(time_base.span_s)
        assert view._time_base == time_base_for_span(time_base.span_s)


def test_a_run_shorter_than_the_selected_time_base_shows_whole(application: QApplication) -> None:
    """`PL-SSBP`: a chosen width wider than the run draws the run from zero."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    view = _shown_view(application, controller)

    _select_time_base(view, "900.0")
    frame = view._concentration_chart.frame

    assert frame is not None
    assert frame.start_s == 0.0
    assert frame.stop_s == 900.0
    assert view._concentration_chart.drawn_points(0, RecordedQuantity.ALVEOLAR)[0][0] == (
        pytest.approx(0.0)
    )


def test_both_plots_are_labelled_from_the_same_ticks(application: QApplication) -> None:
    """One frame, both charts: the ticks cannot disagree because there is one list."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 1800.0)
    view = _shown_view(application, controller)

    assert view._wash_in_chart.frame is view._concentration_chart.frame
    assert view._wash_in_chart.axis_ticks("bottom") == view._concentration_chart.axis_ticks(
        "bottom"
    )


def test_the_wash_in_plot_spans_the_same_window_as_the_chart_above_it(
    application: QApplication,
) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    view = _shown_view(application, controller)

    for key in (FIT_RUN_KEY, "900.0", "43200.0"):
        _select_time_base(view, key)

        assert view._wash_in_chart.frame is view._concentration_chart.frame


def test_the_time_axis_caption_on_screen_states_the_span_and_the_mode(
    application: QApplication,
) -> None:
    """The width is a mode (`PL-012`), so the caption says which and how wide."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 7200.0)
    view = _shown_view(application, controller)
    frame = view._concentration_chart.frame
    assert frame is not None

    assert "whole run so far" in view._time_axis_caption.text()
    assert f"{format_time_base(frame.time_base.span_s)} shown" in view._time_axis_caption.text()
    assert "simulated seconds" not in view._time_axis_caption.text()

    _select_time_base(view, "7200.0")

    assert view._time_axis_caption.text() == "2 hours shown"


def test_choosing_a_time_base_changes_nothing_the_run_recorded(application: QApplication) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 20.0)
    view = _shown_view(application, controller)
    recorded = (controller.snapshot().elapsed_s, controller.run_segments)

    for key in (*(str(time_base.span_s) for time_base in SELECTABLE_TIME_BASES), FIT_RUN_KEY):
        _select_time_base(view, key)

        assert (controller.snapshot().elapsed_s, controller.run_segments) == recorded


def test_the_time_base_is_never_disabled(application: QApplication) -> None:
    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()
    view.present(False)

    assert view.runs[0]._agent_dropdown.isEnabled() is False
    assert view._time_base_dropdown.isEnabled() is True


def test_reset_leaves_the_selected_time_base_alone(application: QApplication) -> None:
    view = _shown_view(application, SimulationController())

    _select_time_base(view, "1800.0")
    view.runs[0]._reset_button.click()

    assert view._time_base == time_base_for_span(1800.0)
    assert view._time_base_dropdown.currentData() == "1800.0"


def test_the_mac_axis_and_references_follow_the_agent(application: QApplication) -> None:
    """The divisor line, the 1 MAC line and the right axis are the running agent's."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    chart = view._concentration_chart

    assert view._mac_reference_text.text() == format_mac_reference("Sevoflurane", 2.0)
    assert chart.one_mac_line() == 2.0
    assert chart.axis_ticks("right")[-1][1] == "3.0"
    assert chart.axis_ticks("right")[-1][0] == pytest.approx(6.0)

    _select_agent(view.runs[0], "desflurane")
    snapshot = controller.snapshot()
    mac_awake = snapshot.agent_mac_awake

    assert view._mac_reference_text.text() == format_mac_reference("Desflurane", 6.0)
    assert view._mac_awake_reference_text.text() == format_mac_awake_reference(
        "Desflurane",
        fraction_of_mac=mac_awake.fraction_of_mac,
        standard_deviation_fraction_of_mac=mac_awake.standard_deviation_fraction_of_mac,
        mac_percent=6.0,
    )
    assert chart.one_mac_line() == 6.0
    assert chart.axis_ticks("right")[-1][1] == "3.0"
    assert chart.axis_ticks("right")[-1][0] == pytest.approx(18.0)


def test_a_recorded_change_is_marked_on_the_chart_at_its_own_time(
    application: QApplication,
) -> None:
    """`PL-DR1Z`: the mark stands at the change's instant on both plots."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 600.0)
    controller.begin_control_adjustment()
    controller.set_fresh_gas_flow(2.0)
    _advance(controller, 600.0)
    view = _shown_view(application, controller)

    assert view._concentration_chart.control_mark_times(0) == (pytest.approx(600.0),)
    assert view._wash_in_chart.control_mark_times(0) == (pytest.approx(600.0),)
    assert view.runs[0]._control_timeline_text.text().startswith(format_elapsed(600.0))


def test_a_real_run_draws_the_ratio_of_its_own_recorded_compartments(
    application: QApplication,
) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 60.0)
    view = _shown_view(application, controller)
    snapshot = controller.snapshot()
    reading = read_wash_in(
        snapshot.alveolar_partial_pressure_fraction, snapshot.inspired_partial_pressure_fraction
    )
    assert reading.plotted_ratio is not None

    stretches = view._wash_in_chart.drawn_stretches(0)
    assert stretches
    last_time, last_ratio = stretches[-1][-1]

    assert last_time == pytest.approx(snapshot.elapsed_s)
    assert last_ratio == pytest.approx(reading.plotted_ratio)
    assert format_wash_in_ratio(last_ratio) in view.runs[0]._wash_in_state_text.text()


# ------------------------------------------- the whole interface, walked


def test_the_header_shows_the_application_name_from_app_metadata(application: QApplication) -> None:
    """`PL-HK75`: the name on screen is the one `app_metadata` declares."""

    view = _shown_view(application, SimulationController())

    assert APP_DISPLAY_NAME in _interface_strings(view)


def test_no_interface_string_drops_the_end_tidal_equivalent_hedge(
    application: QApplication,
) -> None:
    """`PL-NV9W`: nothing on screen says "end-tidal" without "-equivalent"."""

    strings = _interface_strings(_shown_view(application, SimulationController()))

    for value in strings:
        assert _UNHEDGED_END_TIDAL.search(value) is None, value

    assert _ALVEOLAR_METRIC_QUALIFIER in strings, (
        "the interface walk did not reach the concentration readouts, so the assertion "
        "above proved nothing"
    )


def test_the_interface_states_the_mac_divisor_and_writes_the_unit_as_a_ratio(
    application: QApplication,
) -> None:
    view = _shown_view(application, SimulationController())
    strings = _interface_strings(view)

    assert "1 MAC sevoflurane = 2.0%" in " ".join(sorted(strings))
    # The readouts write the unit as a ratio, never as a bare "MAC".
    assert any(value.endswith(" ×MAC") for value in strings)


def test_the_screen_states_the_band_fraction_and_the_divisor_for_every_agent(
    application: QApplication,
) -> None:
    """`PL-F52R`: both free parameters are named on screen, for every agent."""

    for agent_id in AGENT_DATA_FILENAMES:
        agent = load_agent_parameters(agent_id)
        view = _shown_view(application, SimulationController(agent_id=agent_id))
        strings = _interface_strings(view)

        assert (
            format_mac_awake_reference(
                agent.display_name,
                fraction_of_mac=agent.mac_awake.fraction_of_mac,
                standard_deviation_fraction_of_mac=agent.mac_awake.standard_deviation_fraction_of_mac,
                mac_percent=agent.mac_percent,
            )
            in strings
        )
        assert format_mac_reference(agent.display_name, agent.mac_percent) in strings


def test_the_interface_says_which_trace_the_band_is_read_against(application: QApplication) -> None:
    prose = " ".join(_interface_strings(_shown_view(application, SimulationController())))

    assert "vessel-rich trace" in prose
    assert "±1 SD" in prose
    assert "population" in prose


def test_nothing_between_the_chart_heading_and_the_plot_is_a_sentence(
    application: QApplication,
) -> None:
    """`PL-6580`: the panel above the compartment plot is legend and labels, not prose.

    The two state advisories are exempt and skipped by identity: they are
    empty here and speak only when they apply, which is the distinction
    being drawn - a message at the moment of need is not a standing
    paragraph.
    """

    view = _shown_view(application, SimulationController())
    strings = _strings_between(
        None,
        view._concentration_chart,
        skip=(view._hidden_traces_text, view.runs[0]._off_scale_text),
    )

    for value in strings:
        assert ". " not in value, value
        assert not value.rstrip().endswith("."), value

    joined = " ".join(sorted(strings))
    assert "1 MAC sevoflurane = 2.0%" in joined
    assert "read against vessel-rich trace" in joined
    assert "1 MAC, reference adult (alveolar)" in joined
    assert "Compartments:" in joined
    assert "Clinical references:" in joined
    assert "Run record:" in joined
    assert "Time base" in joined


def test_nothing_between_the_wash_in_heading_and_its_plot_is_a_sentence(
    application: QApplication,
) -> None:
    """`PL-F9TQ`: the same rule as the panel above, applied to the panel below."""

    view = _shown_view(application, SimulationController())
    strings = _strings_between(
        view._concentration_chart, view._wash_in_chart, skip=(view.runs[0]._wash_in_state_text,)
    )

    for value in strings:
        assert ". " not in value, value
        assert not value.rstrip().endswith("."), value

    joined = " ".join(sorted(strings))
    assert "not the vaporizer dial" in joined
    assert "Modelled, not measured" in joined
    assert "dimensionless ratio" not in joined


def test_the_wash_in_plot_says_what_its_denominator_is(application: QApplication) -> None:
    """`PL-F9TQ`: F_I is the modelled circuit, and the plot says so where it is read."""

    prose = " ".join(_interface_strings(_shown_view(application, SimulationController())))

    assert "not the vaporizer dial" in prose
    assert "denominator moving" in prose
    assert "Equilibrium, F_A = F_I" in prose


def test_the_screen_says_a_control_mark_is_an_input_not_a_measurement(
    application: QApplication,
) -> None:
    prose = " ".join(_interface_strings(_shown_view(application, SimulationController())))

    assert "Settings only — not a measurement." in prose
    assert "Control change" in prose
    assert "Run record:" in prose


def test_the_interface_never_predicts_a_time_to_wake_up(application: QApplication) -> None:
    """`PL-F52R`: the claim the band exists *instead of*, checked against the whole tree.

    A readout of the form "time to wake-up: 14 min" reads as a per-patient
    prediction this model does not support, and no surrounding disclaimer
    undoes that.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 600.0)
    strings = _interface_strings(_shown_view(application, controller))
    prose = " ".join(strings).lower()

    duration = re.compile(
        r"\d+(?:\.\d+)?\s*(?:s|sec|secs|second|seconds|min|mins|minute|minutes|h|hr|hour|hours)\b"
    )

    for value in strings:
        lowered = value.lower()
        if any(word in lowered for word in ("wake", "awaken", "arousal", "emergence")):
            assert duration.search(lowered) is None, value

    for forbidden in (
        "time to wake",
        "time to awaken",
        "wake-up time",
        "wakeup time",
        "emergence time",
        "time to emergence",
        "predicted wake",
        "will wake",
    ):
        for match in re.finditer(re.escape(forbidden), prose):
            preceding = prose[max(0, match.start() - 12) : match.start()]
            assert "not " in preceding, (forbidden, preceding)

    assert "population" in prose
    assert "±1 sd" in prose


# ---------------------------------------------------------------- the page


def test_the_dashboard_fits_its_window_without_a_horizontal_scrollbar(
    application: QApplication,
) -> None:
    """Nothing holds the page wider than the window: the sidebar and every slider are on screen.

    The readout row reports a one-column minimum and the legend rows wrap,
    so the page's minimum is well inside the window and the scroll area
    never widens it; the chart column alone asks for less than a thousand
    pixels.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    scroll = view.findChild(QScrollArea)
    assert scroll is not None
    page = _page_of(view)

    assert page.minimumSizeHint().width() <= scroll.viewport().width()
    assert page.width() == scroll.viewport().width()
    assert scroll.horizontalScrollBar().maximum() == 0
    assert view._chart_column.minimumSizeHint().width() < 1000

    for slider in view.runs[0]._sliders():
        right_edge = slider.mapTo(page, slider.rect().bottomRight()).x()

        assert right_edge <= page.width(), "a setting control is laid beyond the page"

    accounting_panel, timeline_panel = view.runs[0].build_sidebar_panels()

    for panel in (accounting_panel, timeline_panel):
        assert panel.mapTo(page, panel.rect().bottomRight()).x() <= page.width()


def test_spare_height_goes_to_the_plots_and_not_to_the_readouts(application: QApplication) -> None:
    """The readout and setting sections stand at their own height; the chart row takes the rest.

    At the fixed test size the page is taller than the window and there is
    no spare; a window taller than the page's own hint has some, and every
    pixel of it lengthens the chart row while the two rows above it do not
    move.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    stacked = _stacked_sections(view)
    readout_section, settings, chart_row = (stacked.widget(index) for index in range(3))
    page = _page_of(view)

    assert abs(readout_section.height() - readout_section.sizeHint().height()) <= 2
    assert abs(settings.height() - settings.sizeHint().height()) <= 2
    assert chart_row.height() >= chart_row.sizeHint().height() - 2 * stacked.handleWidth()

    settled_chart_row_height = chart_row.height()
    spare = 400
    view.resize(_WINDOW_WIDTH_PX, page.sizeHint().height() + spare)
    application.processEvents()

    assert abs(readout_section.height() - readout_section.sizeHint().height()) <= 2
    assert abs(settings.height() - settings.sizeHint().height()) <= 2
    assert chart_row.height() >= settled_chart_row_height + spare - 2
    assert chart_row.height() > chart_row.sizeHint().height()

    view.resize(_WINDOW_WIDTH_PX, _WINDOW_HEIGHT_PX)
    application.processEvents()


# ------------------------------------------------------------- two runs


def test_two_run_views_drive_two_controllers(application: QApplication) -> None:
    """`PL-B9PY`: two runs, two controllers, and neither states the other's numbers.

    A regression here would look like one branch's readouts standing over
    the other branch's numbers, which is the wrong-patient-context failure
    `CLAUDE.md`'s safety-critical standard names.
    """

    lean = SimulationController()
    generous = SimulationController()
    view = _shown_view(application, lean, generous)
    lean_run, generous_run = view.runs

    _set_fresh_gas_flow(lean_run, 1.0)
    _set_fresh_gas_flow(generous_run, 6.0)

    lean.start()
    generous.start()
    _advance_to(lean, 120.0)
    _advance_to(generous, 60.0)
    view.present(False)

    assert lean.snapshot().fresh_gas_flow_l_min == pytest.approx(1.0)
    assert generous.snapshot().fresh_gas_flow_l_min == pytest.approx(6.0)

    assert lean_run._fresh_gas_flow_slider.value_label.text() == format_flow(1.0)
    assert generous_run._fresh_gas_flow_slider.value_label.text() == format_flow(6.0)
    assert lean_run._elapsed_time_text.text() == format_elapsed(120.0)
    assert generous_run._elapsed_time_text.text() == format_elapsed(60.0)

    chart = view._concentration_chart
    lean_times, lean_percents = chart.drawn_points(0, RecordedQuantity.ALVEOLAR)
    generous_times, generous_percents = chart.drawn_points(1, RecordedQuantity.ALVEOLAR)

    assert lean_percents and generous_percents
    assert lean_times[-1] == pytest.approx(120.0)
    assert generous_times[-1] == pytest.approx(60.0)
    assert lean_percents[-1] != pytest.approx(generous_percents[-1])


def test_each_run_draws_only_its_own_recorded_values(application: QApplication) -> None:
    """The pairing hazard, doubled: a line must carry its run and its compartment.

    The model is linear in partial pressure, so a run at twice the dial
    reaches exactly twice every compartment at every instant: a line
    carrying the wrong run's values is visible in the drawn points rather
    than inferred.
    """

    single = SimulationController()
    double = SimulationController()
    double.set_delivered_partial_pressure_fraction(Fraction(0.04))
    single.start()
    double.start()
    _advance(single, 60.0)
    _advance(double, 60.0)
    view = _shown_view(application, single, double)
    chart = view._concentration_chart

    frame = chart.frame
    assert frame is not None
    # Every compartment the cap leaves drawn, which is what "each run draws
    # its own values" has to hold for; the cap itself is `PL-8PSW`'s own test.
    assert frame.visible

    for quantity in frame.visible:
        single_times, single_percents = chart.drawn_points(0, quantity)
        double_times, double_percents = chart.drawn_points(1, quantity)

        assert single_percents, f"{quantity} drew nothing on the first run"
        assert single_times == pytest.approx(double_times)
        assert double_percents == pytest.approx(tuple(2.0 * p for p in single_percents), rel=1e-9)


def test_one_compartment_selection_applies_to_every_run(application: QApplication) -> None:
    """`PL-HLD5`: unchecking a compartment takes it off the chart for both runs at once."""

    first = SimulationController()
    second = SimulationController()
    first.start()
    second.start()
    _advance(first, 60.0)
    _advance(second, 60.0)
    view = _shown_view(application, first, second)
    chart = view._concentration_chart
    # One of the two the cap leaves drawn, so what is being tested is the
    # selection reaching both runs rather than the cap removing a trace.
    quantity = RecordedQuantity.ALVEOLAR

    _set_trace_shown(application, view, quantity, False)

    assert chart.drawn_points(0, quantity) == ((), ())
    assert chart.drawn_points(1, quantity) == ((), ())

    _set_trace_shown(application, view, quantity, True)

    assert chart.drawn_points(0, quantity)[0]
    assert chart.drawn_points(1, quantity)[0]


def test_two_runs_cap_the_chart_at_two_compartments_and_say_so(application: QApplication) -> None:
    """`PL-8PSW`: the cap holds the selection, the boxes agree with it, and it is stated.

    The cap is what frees the line width for the run, so it is the half of
    the encoding that must hold whatever a reader does - including checking
    a third compartment, which takes the longest-standing one off rather
    than being silently ignored.
    """

    first = SimulationController()
    second = SimulationController()
    first.start()
    second.start()
    _advance(first, 60.0)
    _advance(second, 60.0)
    single = _shown_view(application, first)

    assert single._legend.shown == COMPARTMENT_QUANTITIES
    assert single._capped_traces_text.isHidden() is True

    view = _shown_view(application, first, second)
    chart = view._concentration_chart
    frame = chart.frame

    assert frame is not None
    # Reduced from six on the way in, to the top of the compartment table.
    assert view._legend.shown == (RecordedQuantity.CIRCUIT, RecordedQuantity.ALVEOLAR)
    assert frame.visible == (RecordedQuantity.CIRCUIT, RecordedQuantity.ALVEOLAR)
    assert view._capped_traces_text.isHidden() is False
    assert str(COMPARED_COMPARTMENT_CAP) in view._capped_traces_text.text()

    _set_trace_shown(application, view, RecordedQuantity.FAT, True)

    # The third check is honoured and the oldest selection makes room for it,
    # so the boxes never name more curves than the plot draws.
    assert len(view._legend.shown) == COMPARED_COMPARTMENT_CAP
    assert RecordedQuantity.FAT in view._legend.shown
    assert view._concentration_chart.frame is not None
    assert view._concentration_chart.frame.visible == view._legend.shown

    for quantity in COMPARTMENT_QUANTITIES:
        drawn = bool(chart.drawn_points(0, quantity)[0])

        assert drawn is (quantity in view._legend.shown)


def test_the_window_fits_the_longer_of_two_runs(application: QApplication) -> None:
    """One window, wide enough for both, or one run is compared half-drawn."""

    short = SimulationController()
    long = SimulationController()
    short.start()
    long.start()
    _advance_to(short, 60.0)
    _advance_to(long, 600.0)
    view = _shown_view(application, short, long)
    frame = view._concentration_chart.frame

    assert frame is not None
    assert frame.stop_s >= 600.0
    assert view._wash_in_chart.frame is frame
    assert view._concentration_chart.drawn_points(1, RecordedQuantity.ALVEOLAR)[0][-1] == (
        pytest.approx(600.0)
    )


def test_halting_one_run_leaves_the_other_advancing(application: QApplication) -> None:
    """A raise out of one run's step says nothing about the other run."""

    halted = SimulationController()
    untouched = SimulationController()
    halted.start()
    untouched.start()
    view = _shown_view(application, halted, untouched)

    view.runs[0]._halt_run(ValueError("mass balance violated"))

    assert halted.snapshot().failure_reason == "ValueError: mass balance violated"
    assert halted.is_running is False
    assert untouched.has_failed is False
    assert untouched.has_reached_supported_limit is False
    assert untouched.is_running is True

    _steps(view.runs[1], 1)

    assert untouched.snapshot().elapsed_s == SIMULATION_STEP_S


def test_a_frame_that_cannot_be_drawn_halts_every_run(application: QApplication) -> None:
    """The render loop draws all of them, so a raise out of it is nobody's."""

    first = SimulationController()
    second = SimulationController()
    first.start()
    second.start()
    view = _shown_view(application, first, second)

    view._halt_every_run(ValueError("the frame could not be built"))

    assert first.snapshot().failure_reason == "ValueError: the frame could not be built"
    assert second.snapshot().failure_reason == "ValueError: the frame could not be built"
    assert first.is_running is False
    assert second.is_running is False


def test_the_interface_walk_reaches_the_axis_titles_and_the_accessible_names(
    application: QApplication,
) -> None:
    """The whole-interface walk covers what the Flet walk covered: axis titles too.

    The hedge and the wake-time walks guarantee only what the walk reaches,
    and the plots' axis titles and the legend boxes' accessible names are
    standing text a reader or a screen reader meets; both are on the walk
    (`PL-25KS`).
    """

    from anesthesia_sim.app.chart_frame import COMPARTMENT_TRACES
    from anesthesia_sim.app.dashboard_frame import TRACE_TOGGLE_ACCESSIBLE_NAME_TEMPLATE

    view = _shown_view(application, SimulationController())
    strings = set(view.interface_strings())

    assert {"% of 1 atm", "simulated time", "×MAC", "F_A/F_I"} <= strings
    assert {
        TRACE_TOGGLE_ACCESSIBLE_NAME_TEMPLATE.format(label=style.label)
        for style in COMPARTMENT_TRACES
    } <= strings


def test_the_dashboard_carries_the_educational_disclaimer(application: QApplication) -> None:
    """`PL-GMM7`: the educational disclaimer is on the dashboard, verbatim.

    `test_the_educational_disclaimer_says_what_the_tool_is_not` pins the
    words; this holds that the dashboard places them where a reader meets
    them, at the foot of the page, so the string the project's regulatory
    posture rests on cannot silently leave the screen.
    """

    from anesthesia_sim.app.dashboard_frame import USE_DISCLAIMER_TEXT

    view = _shown_view(application, SimulationController())

    assert USE_DISCLAIMER_TEXT in view.interface_strings()
