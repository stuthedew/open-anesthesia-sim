"""The dashboard, driven headless against real runs.

These tests cover its constructor, transport, sliders and playback.

`simulation_view_support.py` describes the whole suite.
"""

import re
from enum import Enum

import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QProxyStyle,
    QSlider,
    QStyle,
    QStyleFactory,
    QStyleHintReturn,
    QStyleOption,
    QStyleOptionSlider,
    QWidget,
)

from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import MAX_DISPLAYED_RUNS, slider_position
from anesthesia_sim.app.formatting import (
    CONCENTRATION_DISPLAY_DECIMALS,
    FLOW_DISPLAY_DECIMALS,
    format_flow,
    format_playback_rate,
)
from anesthesia_sim.app.playback import (
    DEFAULT_PLAYBACK_RATE,
    SUPPORTED_PLAYBACK_RATES,
    playback_rate_for,
)
from anesthesia_sim.app.qt_widgets import ParameterSlider
from anesthesia_sim.app.run_view import RunView
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.theme import ACCENT_TEXT, INK, MUTED, PANEL
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MINIMUM_CARDIAC_OUTPUT_L_MIN,
    MINIMUM_FRESH_GAS_FLOW_L_MIN,
    FreshGasFlow,
)
from tests.integration.simulation_view.simulation_view_support import (
    _advance,
    _concentration,
    _dials,
    _drag,
    _select_playback_rate,
    _set_delivered_percent,
    _set_fresh_gas_flow,
    _shown_view,
    _steps,
    _visible_strings,
    _wash_in,
)

# ------------------------------------------------------- the constructor


def test_a_dashboard_refuses_to_be_built_with_no_run() -> None:
    """A dashboard with no run has no agent, no ruler and nothing to draw."""

    with pytest.raises(
        ValueError,
        match=re.escape(f"the dashboard displays 1 to {MAX_DISPLAYED_RUNS} runs at once, not 0"),
    ):
        SimulationView(())


def test_a_dashboard_refuses_more_runs_than_may_be_displayed() -> None:
    """`ROADMAP.md` limits the comparison to two runs, for the reason below.

    With three runs, no visual channel is left to tell one run from another.
    Colour and line style carry the compartment, and line width has only two
    levels. A third curve would be drawn with nothing to identify it.
    """

    assert MAX_DISPLAYED_RUNS == 2

    with pytest.raises(
        ValueError,
        match=re.escape(f"the dashboard displays 1 to {MAX_DISPLAYED_RUNS} runs at once, not 3"),
    ):
        SimulationView(tuple(SimulationController() for _ in range(MAX_DISPLAYED_RUNS + 1)))


def test_a_dashboard_refuses_two_runs_on_different_agents() -> None:
    """One ×MAC ruler and one set of references cannot describe two agents.

    With two agents on one chart, one run's traces would be read against the
    other agent's divisor. That gives a correct number under the wrong label,
    which `CLAUDE.md`'s standard treats as a failure of the value.
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

    `PL-DHBX`: a button that declares no foreground is drawn in the colour of
    Qt's palette `ButtonText` role. That role follows the host appearance
    rather than this interface. Under macOS Dark it went near-white, while
    every surface around it kept this light theme's colours. Both states are
    checked because the defect arrived twice. Declaring `:enabled` alone still
    left the *unavailable* button invisible on the project owner's screen.

    `transport_button_stylesheet` carries the colours. This test checks that
    `RunView` applies them, which a test of the helper alone would not catch.
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
    """Each button acts on the run through its own click, and draws its own frame."""

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
    """Running is drawn in the accent colour and Paused in muted, so word and colour agree."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]

    assert MUTED in run._status_text.styleSheet()

    run._start_button.click()

    assert ACCENT_TEXT in run._status_text.styleSheet()
    assert MUTED not in run._status_text.styleSheet()


# ------------------------------------------------------------ the sliders


def test_the_integer_sliders_span_the_supported_input_ranges(application: QApplication) -> None:
    """The ranges are read from the constructed controls, not from module constants."""

    run = _shown_view(application, SimulationController()).runs[0]

    for control, minimum, maximum in (
        (
            _dials(run)._fresh_gas_flow_slider,
            MINIMUM_FRESH_GAS_FLOW_L_MIN,
            MAXIMUM_FRESH_GAS_FLOW_L_MIN,
        ),
        (
            _dials(run)._alveolar_ventilation_slider,
            MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
            MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
        ),
        (
            _dials(run)._cardiac_output_slider,
            MINIMUM_CARDIAC_OUTPUT_L_MIN,
            MAXIMUM_CARDIAC_OUTPUT_L_MIN,
        ),
    ):
        assert control.slider.minimum() == slider_position(minimum, FLOW_DISPLAY_DECIMALS)
        assert control.slider.maximum() == slider_position(maximum, FLOW_DISPLAY_DECIMALS)


def test_every_slider_endpoint_reaches_the_core_and_is_accepted(application: QApplication) -> None:
    """The interface must not offer a position the model refuses."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]

    for control in (
        _dials(run)._fresh_gas_flow_slider,
        _dials(run)._alveolar_ventilation_slider,
        _dials(run)._cardiac_output_slider,
        _dials(run)._delivered_concentration_slider,
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
    assert _dials(run)._fresh_gas_flow_slider.value_label.text() == "7.0 L/min"


def test_the_delivered_dial_reaches_the_core_as_the_percent_dialled(
    application: QApplication,
) -> None:
    """The dial is in percent and so is what the core holds (`PL-NJPB`).

    The model treats that value as a fraction of one atmosphere, and the
    second assertion checks that magnitude.
    """

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]

    _set_delivered_percent(run, 6.5)

    assert controller.snapshot().delivered_concentration_percent == 6.5
    assert controller.snapshot().delivered_partial_pressure_fraction == pytest.approx(0.065)
    assert _dials(run)._delivered_concentration_slider.value_label.text() == "6.50%"


def test_alveolar_ventilation_slider_forwards_value_to_controller(
    application: QApplication,
) -> None:
    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]

    _drag(_dials(run)._alveolar_ventilation_slider, 8.0, FLOW_DISPLAY_DECIMALS)

    assert controller.snapshot().alveolar_ventilation_l_min == 8.0
    assert _dials(run)._alveolar_ventilation_slider.value_label.text() == "8.0 L/min"


def test_cardiac_output_slider_forwards_value_to_controller(application: QApplication) -> None:
    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]

    _drag(_dials(run)._cardiac_output_slider, 6.5, FLOW_DISPLAY_DECIMALS)

    assert controller.snapshot().cardiac_output_l_min == 6.5
    assert _dials(run)._cardiac_output_slider.value_label.text() == "6.5 L/min"


def test_the_sliders_declare_an_adjustment_boundary_when_a_drag_begins(
    application: QApplication,
) -> None:
    """Without the boundary, two turns of one dial would be recorded as one adjustment.

    Each slider's press is wired to the boundary, so a second act on the
    same control after a press is a second adjustment. The test observes this
    through the controller rather than by inspecting the connection, because
    PySide6 does not expose the connection.
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
        controller.set_fresh_gas_flow(FreshGasFlow(3.0))
        controller.advance()

        control: ParameterSlider = getattr(_dials(run), slider_name)
        control.slider.sliderPressed.emit()
        controller.set_fresh_gas_flow(FreshGasFlow(2.0))

        assert {change.adjustment for change in controller.snapshot().control_timeline} == {1, 2}, (
            f"{slider_name}'s press did not declare an adjustment boundary"
        )


def test_a_declared_boundary_reaches_the_controller(application: QApplication) -> None:
    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]

    controller.start()
    controller.set_fresh_gas_flow(FreshGasFlow(3.0))
    controller.advance()
    run.start_adjustment()
    controller.set_fresh_gas_flow(FreshGasFlow(2.0))

    assert {change.adjustment for change in controller.snapshot().control_timeline} == {1, 2}


def test_a_drag_of_one_slider_is_marked_and_listed_once(application: QApplication) -> None:
    """One drag is one mark and one entry, at its release, however long the thumb was held.

    The run goes on stepping while the thumb is moved through three values.
    None of them is applied until the release (`PL-5B1N`), so the record
    holds one change, from the setting before the drag to the released value.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()
    _advance(controller, 10)
    slider = _dials(run)._delivered_concentration_slider.slider

    slider.setSliderDown(True)

    for percent in (3.0, 3.5, 4.0):
        slider.setSliderPosition(slider_position(percent, CONCENTRATION_DISPLAY_DECIMALS))
        controller.advance()

    slider.setSliderDown(False)
    view.present(False)
    released_at_s = 10 + 3 * SIMULATION_STEP_S

    assert len(run._control_timeline_text.text().splitlines()) == 1
    assert controller.record().control_timeline[0].new_value == 4.0
    assert _concentration(view).chart.control_mark_times(0) == (pytest.approx(released_at_s),)
    assert _wash_in(view).chart.control_mark_times(0) == (pytest.approx(released_at_s),)


# --------------------------------------- a press on a slider, on each platform


class _MacSliderHints(QProxyStyle):
    """Qt's Fusion style, with the two slider hints that Qt's macOS style returns.

    Qt's source at tag v6.11.2 was read on 2026-11-22. In
    `src/plugins/styles/mac/qmacstyle_mac.mm`, `SH_Slider_AbsoluteSetButtons`
    is `Qt::LeftButton|Qt::MiddleButton` and `SH_Slider_PageSetButtons` is 0.
    In `src/widgets/styles/qcommonstyle.cpp`, which Fusion inherits, they are
    `Qt::MiddleButton` and `Qt::LeftButton`. So on macOS a left click on the
    track moves the handle to the pointer, and under Fusion it steps one page.
    """

    def styleHint(  # Qt spells this in camelCase.
        self,
        hint: QStyle.StyleHint,
        option: QStyleOption | None = None,
        widget: QWidget | None = None,
        returnData: QStyleHintReturn | None = None,
    ) -> int:
        if hint == QStyle.StyleHint.SH_Slider_AbsoluteSetButtons:
            return Qt.MouseButton.LeftButton.value | Qt.MouseButton.MiddleButton.value

        if hint == QStyle.StyleHint.SH_Slider_PageSetButtons:
            return 0

        return super().styleHint(hint, option, widget, returnData)


class _Platform(Enum):
    """The slider hints a test gives a slider."""

    FUSION = "Fusion"
    MACOS = "macOS hints"


#: Every style a test gives a slider. A widget does not own its style, so each
#: is kept here for as long as the module runs.
_STYLES_IN_USE: list[QStyle] = []


def _style_slider(slider: QSlider, platform: _Platform) -> None:
    """Give one slider Fusion, or Fusion with the macOS slider hints."""

    fusion = QStyleFactory.create("Fusion")
    style = fusion if platform is _Platform.FUSION else _MacSliderHints(fusion)
    _STYLES_IN_USE.append(style)
    slider.setStyle(style)


def _handle_rect(slider: QSlider) -> tuple[int, int, int]:
    """The handle's left edge, centre and right edge, in the slider's pixels."""

    options = QStyleOptionSlider()
    slider.initStyleOption(options)
    handle = slider.style().subControlRect(
        QStyle.ComplexControl.CC_Slider, options, QStyle.SubControl.SC_SliderHandle, slider
    )

    return handle.left(), handle.center().x(), handle.right()


def _flow_slider_at_four(
    application: QApplication, platform: _Platform
) -> tuple[SimulationController, SimulationView, RunView, ParameterSlider, list[object]]:
    """A run paused at 300 s at 4.0 L/min, its flow slider styled, and a list of its signals."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 300)
    controller.pause()
    view = _shown_view(application, controller)
    run = view.runs[0]
    control = _dials(run)._fresh_gas_flow_slider
    _style_slider(control.slider, platform)
    assert controller.settings().fresh_gas_flow_l_min == 4.0
    signals: list[object] = []
    control.value_changed.connect(lambda value: signals.append(("applied", value)))
    control.preview_moved.connect(lambda value: signals.append(("preview", value)))
    control.preview_ended.connect(lambda: signals.append("preview ended"))

    return controller, view, run, control, signals


@pytest.mark.parametrize(
    ("platform", "button", "applied"),
    [
        (_Platform.FUSION, Qt.MouseButton.LeftButton, 4.1),
        (_Platform.MACOS, Qt.MouseButton.LeftButton, 10.0),
        (_Platform.FUSION, Qt.MouseButton.MiddleButton, 10.0),
    ],
    ids=["Fusion left button", "macOS left button", "Fusion middle button"],
)
def test_a_click_on_a_slider_s_track_applies_at_once_and_draws_no_preview(
    application: QApplication, platform: _Platform, button: Qt.MouseButton, applied: float
) -> None:
    """A click on the track is one input on each platform, so it applies and previews nothing.

    The click is at the track's right end, well clear of the handle. Under
    Fusion a left click steps one page, which is one count of 0.1 L/min. On
    macOS a left click, and under Fusion a middle click, moves the handle to
    the pointer, which is the slider's maximum of 10.0 L/min
    (`MAXIMUM_FRESH_GAS_FLOW_L_MIN` in `core/supported_ranges.py`). Before
    the fix, the jump applied 10.0 L/min, and the chart then labelled it
    "Preview: Fresh gas flow 10.0 L/min, not applied" for as long as the
    button was down (`PL-57LD`).
    """

    controller, view, _, control, signals = _flow_slider_at_four(application, platform)
    slider = control.slider
    _, _, handle_right = _handle_rect(slider)
    track_end = QPoint(slider.width() - 1, slider.height() // 2)
    assert track_end.x() > handle_right + 50, "the click must land well clear of the handle"
    plots = (_concentration(view).chart, _wash_in(view).chart)

    QTest.mousePress(slider, button, Qt.KeyboardModifier.NoModifier, track_end)
    view.render_tick()
    held = (
        controller.settings().fresh_gas_flow_l_min,
        len(controller.record().control_timeline),
        [plot.preview_label(0) for plot in plots],
        [plot.preview_region(0) for plot in plots],
    )
    # The button is released before any assertion, so that a failure here
    # leaves no button held for the tests that follow.
    QTest.mouseRelease(slider, button, Qt.KeyboardModifier.NoModifier, track_end)
    view.render_tick()

    assert held == (applied, 1, [None, None], [None, None])
    assert controller.settings().fresh_gas_flow_l_min == applied
    assert len(controller.record().control_timeline) == 1
    assert [plot.preview_label(0) for plot in plots] == [None, None]
    assert ("applied", applied) in signals
    assert not [
        signal for signal in signals if isinstance(signal, tuple) and signal[0] == "preview"
    ]


@pytest.mark.parametrize("platform", list(_Platform), ids=[p.value for p in _Platform])
def test_a_press_on_the_handle_off_its_centre_released_unmoved_applies_nothing(
    application: QApplication, platform: _Platform
) -> None:
    """A press on the handle grabs it, previews the setting in force, and applies nothing.

    The press is 3 px right of the handle's centre. One count of the flow
    slider is about 2 px wide here, so with the macOS hints Qt's own press
    moved the handle a count to 4.1 L/min and applied it before any drag
    (`PL-57LD`). Under either style the press now previews 4.0 L/min, the
    setting in force, and the release leaves it in force.
    """

    controller, view, _, control, signals = _flow_slider_at_four(application, platform)
    slider = control.slider
    _, handle_centre, handle_right = _handle_rect(slider)
    off_centre = QPoint(handle_centre + 3, slider.height() // 2)
    assert off_centre.x() < handle_right, "the press must land on the handle"
    chart = _concentration(view).chart

    QTest.mousePress(slider, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, off_centre)
    view.render_tick()
    held_label = chart.preview_label(0)
    QTest.mouseRelease(
        slider, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, off_centre
    )
    view.render_tick()

    assert held_label == "Preview: Fresh gas flow 4.0 L/min, not applied"
    assert controller.settings().fresh_gas_flow_l_min == 4.0
    assert controller.record().control_timeline == ()
    assert chart.preview_label(0) is None
    assert signals == [("preview", 4.0), "preview ended"]


def test_a_drag_that_follows_a_jump_to_the_pointer_previews_and_applies_at_release(
    application: QApplication,
) -> None:
    """With the macOS hints, a click on the track applies the jump, and a drag after it previews.

    The jump to 10.0 L/min is one input and is applied at the press. The
    button stays down and the pointer moves left, which is a drag: it
    previews the value under the handle, and applies that value only at
    the release, as a drag that started on the handle does (`PL-57LD`).
    """

    controller, view, _, control, _ = _flow_slider_at_four(application, _Platform.MACOS)
    slider = control.slider
    track_end = QPoint(slider.width() - 1, slider.height() // 2)
    middle = QPoint(slider.width() // 2, slider.height() // 2)
    chart = _concentration(view).chart

    QTest.mousePress(slider, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, track_end)
    QTest.mouseMove(slider, middle)
    view.render_tick()
    held_label = chart.preview_label(0)
    held_flow = controller.settings().fresh_gas_flow_l_min
    QTest.mouseRelease(slider, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, middle)
    view.render_tick()
    released = controller.settings().fresh_gas_flow_l_min

    assert held_flow == 10.0
    assert 4.0 < released < 10.0
    assert held_label == f"Preview: Fresh gas flow {format_flow(released)}, not applied"
    assert controller.record().control_timeline[-1].new_value == released
    assert chart.preview_label(0) is None


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

    assert format_playback_rate(1) in _visible_strings(view)


def test_the_playback_control_is_never_disabled(application: QApplication) -> None:
    """A view control stays enabled while the run's own controls are locked."""

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
