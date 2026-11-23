"""A failed run's banner in plain words, and the details under it for a report (`PL-XWCH`).

A run halts on any exception. The banner names the kind of failure in words a
learner reads, and the exception's own message, which is written for a
developer, is kept behind "Show details". The details can be copied, and the
line under them links the project's issue page.
"""

import pytest
from PySide6.QtWidgets import QApplication

from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.failures import FailureKind
from anesthesia_sim.app.theme import INK
from tests.integration.simulation_view.simulation_view_support import (
    _real_step_failure,
    _settle,
    _shown_view,
    _StepFailingController,
    _steps,
)

#: The banner for the numerical failure that `_real_step_failure` raises.
_NUMERICAL_BANNER = (
    "Simulation stopped — the model produced a value it cannot hold, such as a negative "
    "amount of agent. This is a fault in the simulator, not a change in the patient. "
    "The values shown are the last completed step. Reset to start a new run."
)


def test_a_failed_step_is_worded_for_the_learner_and_its_message_kept_in_the_details(
    application: QApplication,
) -> None:
    """The banner gives the kind of failure, and only the details name the exception.

    Before `PL-XWCH`, the banner printed "SimulationNumericalError:" and the
    core's message, which names an internal state and a documentation path.
    """

    error = _real_step_failure()
    controller = _StepFailingController(error)
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()

    _steps(run, 3)
    _settle(application)

    assert run._notice_text.notice() == _NUMERICAL_BANNER
    details = run._failure_details
    assert details.isVisible()
    assert details.toggle.text() == "Show details"
    assert details.details_text.isHidden()
    assert details.copy_button.isHidden()
    assert details.report_text.isHidden()
    shown = details.details()
    assert shown is not None
    assert f"What stopped the run: SimulationNumericalError: {error}" in shown.splitlines()


def test_show_details_reveals_the_details_copy_and_the_report_line(
    application: QApplication,
) -> None:
    """Pressing the toggle shows the details, the copy button and the issue page's link."""

    controller = _StepFailingController(_real_step_failure())
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()
    _steps(run, 3)
    details = run._failure_details

    details.toggle.click()
    _settle(application)

    assert details.toggle.text() == "Hide details"
    assert details.details_text.isVisible()
    assert details.details_text.text() == details.details()
    assert details.copy_button.isVisible()
    assert details.report_text.isVisible()
    assert details.report_text.text() == (
        "To report this fault, copy the details and paste them into a new issue on the "
        '<a href="https://github.com/stuthedew/open-anesthesia-sim/issues" '
        f'style="color: {INK};">project\'s issue page</a>.'
    )

    details.toggle.click()

    assert details.toggle.text() == "Show details"
    assert details.details_text.isHidden()


def test_copy_details_puts_the_details_on_the_clipboard_as_plain_text(
    application: QApplication,
) -> None:
    controller = _StepFailingController(_real_step_failure())
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()
    _steps(run, 3)
    details = run._failure_details
    QApplication.clipboard().setText("something else")

    details.toggle.click()
    details.copy_button.click()

    assert QApplication.clipboard().text() == details.details()


def test_a_run_that_has_not_failed_shows_no_details(application: QApplication) -> None:
    """The details and the banner take no room until a run fails (`PL-T91K`)."""

    view = _shown_view(application, SimulationController())
    run = view.runs[0]

    assert run._failure_details.details() is None
    assert run._failure_details.isHidden()
    assert run._halt_banner.isHidden()


@pytest.mark.parametrize("shown_before", [False, True], ids=["folded", "shown"])
def test_new_details_are_folded_away_so_they_are_not_read_as_the_last_ones(
    application: QApplication, shown_before: bool
) -> None:
    """A Reset and a second failure fold the details, whether or not they were shown."""

    controller = _StepFailingController(_real_step_failure())
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()
    _steps(run, 3)
    details = run._failure_details
    first = details.details()

    if shown_before:
        details.toggle.click()

    run._reset_button.click()
    _settle(application)

    assert details.details() is None
    assert details.isHidden()

    controller.fail("TypeError: a second fault", kind=FailureKind.UNEXPECTED)
    view.present(False)
    _settle(application)

    assert details.details() != first
    assert details.toggle.isChecked() is False
    assert details.details_text.isHidden()
