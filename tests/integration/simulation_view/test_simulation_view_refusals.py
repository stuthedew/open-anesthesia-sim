"""The dashboard, driven headless against real runs.

These tests cover refusals shown as notices, and the halt.

`simulation_view_support.py` describes the whole suite.
"""

import pytest
from PySide6.QtWidgets import QApplication

from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.qt_widgets import ParameterSlider
from anesthesia_sim.core.exceptions import (
    SimulationConfigurationError,
    SimulationDomainLimitError,
    SimulationExecutionError,
)
from tests.integration.simulation_view.simulation_view_support import _dials, _shown_view

# ---------------------------------------------- refusals, and the halt


@pytest.mark.parametrize(
    ("dialled_percent", "refusal"),
    [
        (50.0, "vaporizer maximum"),
        (150.0, "delivered_concentration_percent of 150.0 is outside 0 to 100"),
    ],
    ids=["above the vaporizer maximum", "outside any percent"],
)
def test_a_refused_setting_is_reported_without_stopping_the_run(
    application: QApplication, dialled_percent: float, refusal: str
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
    """

    controller = SimulationController(agent_id="isoflurane")
    run = _shown_view(application, controller).runs[0]
    controller.start()
    delivered_before = controller.snapshot().delivered_concentration_percent

    run._handle_delivered_concentration_change(dialled_percent)

    assert controller.is_running is True
    assert controller.has_failed is False
    assert run._status_text.text() == "Running"
    assert run._notice_text.isHidden() is False
    notice = run._notice_text.notice()
    assert notice is not None
    assert "Setting refused" in notice
    assert refusal in notice

    # The control must not keep showing a dial position the simulation is
    # not running at: that is the correct number under the wrong label.
    assert controller.snapshot().delivered_concentration_percent == delivered_before
    assert _dials(run)._delivered_concentration_slider.value() == pytest.approx(delivered_before)


def test_a_refusal_notice_clears_once_a_setting_is_accepted(application: QApplication) -> None:
    controller = SimulationController(agent_id="isoflurane")
    run = _shown_view(application, controller).runs[0]

    run._handle_delivered_concentration_change(50.0)
    assert run._notice_text.isHidden() is False

    run._handle_delivered_concentration_change(2.0)

    assert run._notice_text.isHidden() is True
    assert controller.snapshot().delivered_concentration_percent == 2.0


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
    """No setting slot may let an exception raised by the core reach Qt's dispatcher.

    The sliders' own bounds make a negative flow unreachable in the running
    app. That is exactly why the guard needs its own test: under PySide6, an
    exception that escapes a slot is lost rather than shown.
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
