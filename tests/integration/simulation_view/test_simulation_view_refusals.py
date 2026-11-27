"""The dashboard, driven headless against real runs.

These tests cover refusals shown as notices, and the halt.

`simulation_view_support.py` describes the whole suite.
"""

import dataclasses
import logging

import pytest
from PySide6.QtWidgets import QApplication

from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import slider_position
from anesthesia_sim.app.formatting import FLOW_DISPLAY_DECIMALS
from anesthesia_sim.app.qt_widgets import ParameterSlider
from anesthesia_sim.core import uptake_system
from anesthesia_sim.core.exceptions import (
    SimulationConfigurationError,
    SimulationDomainLimitError,
    SimulationExecutionError,
)
from anesthesia_sim.core.numerical_envelope import CompartmentVolume
from anesthesia_sim.core.parameters import load_reference_adult_parameters
from tests.integration.announcement_support import ASSERTIVE, Announcement, record_announcements
from tests.integration.simulation_view.simulation_view_support import (
    _advance,
    _concentration,
    _dials,
    _hold_thumb,
    _shown_view,
)

# ---------------------------------------------- refusals, and the halt


# The whole banner a user reads for each refused vaporizer setting. Each is typed
# by hand: isoflurane's vaporizer maximum is 5% (`data/agents/isoflurane.json`), and
# the banner writes each value exactly, as Python's `repr` writes it, so a value
# just past a limit never reads as equal to it. The developer's message is the one
# the core raises, and it
# reaches the failure log rather than the banner (`PL-8QFW`).
_UNCHANGED = "The simulation is unchanged and still running its previous setting."


@pytest.mark.parametrize(
    ("dialled_percent", "banner", "logged"),
    [
        (
            50.0,
            "Setting refused — the vaporizer setting cannot be 50.0%, because this agent's "
            f"vaporizer delivers at most 5.0%. {_UNCHANGED}",
            "delivered_concentration_percent exceeds the vaporizer maximum "
            "(50% requested, 5% maximum)",
        ),
        (
            150.0,
            "Setting refused — the vaporizer setting cannot be 150.0%, because a "
            f"concentration can only be from 0.0% to 100.0%. {_UNCHANGED}",
            "delivered_concentration_percent of 150.0 is outside 0 to 100",
        ),
    ],
    ids=["above the vaporizer maximum", "outside any percent"],
)
def test_a_refused_setting_is_reported_without_stopping_the_run(
    application: QApplication,
    caplog: pytest.LogCaptureFixture,
    dialled_percent: float,
    banner: str,
    logged: str,
) -> None:
    """Isoflurane's vaporizer stops at 5%, so 50% must be refused, and 150% is not a percent.

    The test calls the handler rather than dragging the slider, because the
    slider's own maximum makes both values unreachable on the control. That is
    exactly why the handler needs its own test. The two values are refused in
    different places. The circuit refuses 50% against the vaporizer maximum,
    and `Percent` refuses 150% when the handler builds it. So the handler
    builds the `Percent` inside the setting it applies, and names it. If the
    `Percent` were built before, its refusal would escape the handler, and no
    banner would say that the setting was refused (`PL-4R3W`).

    The banner names the setting by the vaporizer's label, and the core's
    message, which names it by its field in the code, goes to the log. Before
    `PL-8QFW` the banner read "Setting refused — delivered_concentration_percent
    exceeds the vaporizer maximum (50% requested, 5% maximum)".
    """

    controller = SimulationController(agent_id="isoflurane")
    run = _shown_view(application, controller).runs[0]
    controller.start()
    delivered_before = controller.snapshot().delivered_concentration_percent

    with caplog.at_level(logging.ERROR, logger="anesthesia_sim"):
        run._handle_delivered_concentration_change(dialled_percent)

    assert controller.is_running is True
    assert controller.has_failed is False
    assert run._status_text.text() == "Running"
    assert run._notice_text.isHidden() is False
    assert run._notice_text.notice() == banner
    assert [record.levelno for record in caplog.records] == [logging.ERROR]
    assert logged in caplog.records[0].getMessage()

    # The control must not keep showing a dial position the simulation is
    # not running at: that is the correct number under the wrong label.
    assert controller.snapshot().delivered_concentration_percent == delivered_before
    assert _dials(run)._delivered_concentration_slider.value() == pytest.approx(delivered_before)


def test_a_refused_setting_and_a_halt_are_read_out_at_once_and_once_only(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A screen reader is interrupted for each, and not told again on the frames after (`PL-J7Z5`).

    The refusal's banner is the one the test above pins, typed here again. A
    halt writes its banner before its frame and again from the frame, and only
    the banner that stands once the halt is over is read. Before `PL-J7Z5`
    neither banner reached a screen reader at all.
    """

    recorded = record_announcements(monkeypatch)
    controller = SimulationController(agent_id="isoflurane")
    view = _shown_view(application, controller)
    controller.start()

    view.runs[0]._handle_delivered_concentration_change(50.0)

    for _ in range(3):
        application.processEvents()
        view.present(False)

    application.processEvents()

    assert recorded == [
        Announcement(
            "Setting refused — the vaporizer setting cannot be 50.0%, because this agent's "
            f"vaporizer delivers at most 5.0%. {_UNCHANGED}",
            ASSERTIVE,
        )
    ]

    recorded.clear()
    halted = SimulationController()
    run = _shown_view(application, halted).runs[0]
    halted.start()
    application.processEvents()

    run._halt_run(ValueError("mass balance violated"))
    application.processEvents()

    assert [announcement.politeness for announcement in recorded] == [ASSERTIVE]
    assert recorded[0].message == run._notice_text.notice()
    assert recorded[0].message.startswith(
        "Simulation stopped — an unexpected error occurred in the simulator"
    )


def test_a_refusal_notice_clears_once_a_setting_is_accepted(application: QApplication) -> None:
    controller = SimulationController(agent_id="isoflurane")
    run = _shown_view(application, controller).runs[0]

    run._handle_delivered_concentration_change(50.0)
    assert run._notice_text.isHidden() is False

    run._handle_delivered_concentration_change(2.0)

    assert run._notice_text.isHidden() is True
    assert controller.snapshot().delivered_concentration_percent == 2.0


def test_a_preview_rebuilt_on_changed_data_names_the_dial_in_the_banner_until_the_release(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """A dial held on a run whose patient file changed says in the banner why no preview is drawn.

    A preview rebuilds the run and reads the patient file again, so a file
    edited after the run began gives the preview another patient, and the
    controller refuses the preview. The banner used to say nothing, so the
    preview simply did not appear (`PL-412F`). The banner now names the dial
    while the thumb is held, and the failure log records each value that
    differs once for the drag, not on every move. The release applies the
    value through the run's own setter, which rebuilds nothing, so the value
    is accepted, the banner says so while the thumb is held, and the notice
    ends with the drag. The banner's text is typed by hand.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 300)
    controller.pause()
    held_flow = controller.settings().fresh_gas_flow_l_min
    view = _shown_view(application, controller)
    run = view.runs[0]
    control = _dials(run)._fresh_gas_flow_slider
    on_file = load_reference_adult_parameters()
    edited = dataclasses.replace(
        on_file, muscle_volume_l=CompartmentVolume(on_file.muscle_volume_l + 1.0)
    )
    monkeypatch.setattr(uptake_system, "load_reference_adult_parameters", lambda: edited)

    with caplog.at_level(logging.ERROR, logger="anesthesia_sim"):
        _hold_thumb(control, 6.0, FLOW_DISPLAY_DECIMALS)
        view.render_tick()
        control.slider.setSliderPosition(slider_position(7.0, FLOW_DISPLAY_DECIMALS))
        view.render_tick()

    assert held_flow not in (6.0, 7.0)
    assert controller.settings().fresh_gas_flow_l_min == held_flow
    assert _concentration(view).chart.preview_label(0) is None
    assert run._notice_text.isHidden() is False
    assert run._notice_text.notice() == (
        "Preview not drawn — the fresh gas flow preview would not start from the values "
        "this run holds, so it would predict a different case. The simulator's data may "
        "have changed since this run began, or the simulator may have a fault. Reopen the "
        "simulator and run the case again to preview a setting. If this notice comes back, "
        "the cause is a fault in the simulator. Releasing the dial still applies the new "
        "setting."
    )
    (logged,) = caplog.records
    assert logged.levelno == logging.ERROR
    assert (
        f"muscle volume_l is {on_file.muscle_volume_l!r} in this run and "
        f"{edited.muscle_volume_l!r} in the preview"
    ) in logged.getMessage()

    control.slider.setSliderDown(False)

    assert controller.settings().fresh_gas_flow_l_min == 7.0
    assert run._notice_text.isHidden() is True


@pytest.mark.parametrize(
    ("handler_name", "slider_name", "refused"),
    [
        (
            "_handle_fresh_gas_flow_change",
            "_fresh_gas_flow_slider",
            "the fresh gas flow setting cannot be -1.0 L/min, because the model covers only "
            "0.0 L/min to 10.0 L/min",
        ),
        (
            "_handle_alveolar_ventilation_change",
            "_alveolar_ventilation_slider",
            "the alveolar ventilation setting cannot be -1.0 L/min, because the model covers "
            "only 0.0 L/min to 12.0 L/min",
        ),
        (
            "_handle_cardiac_output_change",
            "_cardiac_output_slider",
            "the cardiac output setting cannot be -1.0 L/min, because the model covers only "
            "0.0 L/min to 10.0 L/min",
        ),
    ],
)
def test_every_slider_handler_refuses_without_escaping_into_the_toolkit(
    application: QApplication, handler_name: str, slider_name: str, refused: str
) -> None:
    """No setting slot may let an exception raised by the core reach Qt's dispatcher.

    The sliders' own bounds make a negative flow unreachable in the running
    app. That is exactly why the guard needs its own test: under PySide6, an
    exception that escapes a slot is lost rather than shown.

    The banner names each control by its label (`PL-8QFW`). Each interval is
    copied by hand from `docs/INTERFACE.md` § "Supported input ranges": 0 to
    10 L/min of fresh gas, 0 to 12 L/min of alveolar ventilation and 0 to
    10 L/min of cardiac output.
    """

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    controller.start()

    getattr(run, handler_name)(-1.0)

    assert controller.is_running is True
    assert controller.has_failed is False
    assert run._notice_text.isHidden() is False
    assert run._notice_text.notice() == (
        f"Setting refused — {refused}. The simulation is unchanged and still running its "
        "previous setting."
    )
    control: ParameterSlider = getattr(_dials(run), slider_name)
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
    """`PL-V6M0`: an execution error is not a refusal and must not be shown as one."""

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
    """`PL-YK2V`: an exception from outside the project's hierarchy still halts the run."""

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
