"""A failed run's banner in plain words, and the details under it for a report (`PL-XWCH`).

A run halts on any exception. The banner names the kind of failure in words a
user reads, and the exception's own message, which is written for a
developer, is kept behind "Show details". The details can be copied, and the
line under them links the project's issue page.
"""

import pytest
from PySide6.QtWidgets import QApplication

from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.failures import FailureKind
from anesthesia_sim.app.theme import INK
from anesthesia_sim.app_metadata import APP_BUILD_VERSION
from anesthesia_sim.core.exceptions import SimulationConfigurationError, SimulationExecutionError
from anesthesia_sim.core.supported_ranges import CardiacOutput
from tests.integration.simulation_view.simulation_view_support import (
    _branched_case,
    _case_view,
    _real_step_failure,
    _settle,
    _shown_view,
    _StepFailingController,
    _steps,
    _take_fork,
    _with_stale_tissue_flows,
)


def _expected_details(reason: str) -> str:
    """The details of a lone run that `reason` stopped, under a test, which keeps no log."""

    return (
        f"Open Anesthesia Simulator — Version {APP_BUILD_VERSION}\n"
        f"What stopped the run: {reason}\n"
        "Failure log: none is kept this session, because the data folder could not be used"
    )


#: The banner for the numerical failure that `_real_step_failure` raises.
_NUMERICAL_BANNER = (
    "Simulation stopped — the model produced a value it cannot hold, such as a negative "
    "amount of agent. This is a fault in the simulator, not a change in the patient. "
    "The values shown are the last completed step. Reset to start a new run."
)


def test_a_failed_step_is_worded_for_the_user_and_its_message_kept_in_the_details(
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
    assert details.details() == _expected_details(f"SimulationNumericalError: {error}")


def test_show_details_reveals_the_details_copy_and_the_report_line(
    application: QApplication,
) -> None:
    """Pressing the toggle shows the details, the copy button and the issue page's link."""

    error = _real_step_failure()
    controller = _StepFailingController(error)
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()
    _steps(run, 3)
    details = run._failure_details

    details.toggle.click()
    _settle(application)

    assert details.toggle.text() == "Hide details"
    assert details.details_text.isVisible()
    assert details.details_text.text() == _expected_details(f"SimulationNumericalError: {error}")
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
    error = _real_step_failure()
    controller = _StepFailingController(error)
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()
    _steps(run, 3)
    details = run._failure_details
    QApplication.clipboard().setText("something else")

    details.toggle.click()
    details.copy_button.click()

    assert QApplication.clipboard().text() == _expected_details(
        f"SimulationNumericalError: {error}"
    )


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

    assert details.details() == _expected_details("TypeError: a second fault")
    assert details.details() != first
    assert details.toggle.isChecked() is False
    assert details.details_text.isHidden()


@pytest.mark.parametrize(
    ("error", "words"),
    [
        (
            SimulationConfigurationError("a settings record the step refused"),
            "one part of the simulator gave another a value that it does not accept.",
        ),
        (
            SimulationExecutionError("the run could not go on"),
            "the simulator could not continue the run safely.",
        ),
        (
            KeyError("tidal volume"),
            "an unexpected error occurred in the simulator, and its cause is not known.",
        ),
    ],
    ids=["configuration", "execution", "unexpected"],
)
def test_a_halt_of_each_kind_is_worded_by_its_kind_and_named_in_the_details(
    application: QApplication, error: Exception, words: str
) -> None:
    """A real halt through the run's own path gives each kind's words, and the error's name below.

    The numerical and accounting kinds are halted by a real step above and in
    `test_an_accounting_halt_tells_the_user_in_words_and_logs_the_totals`.
    """

    controller = _StepFailingController(error)
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()

    _steps(run, 3)

    assert run._notice_text.notice() == (
        f"Simulation stopped — {words} This is a fault in the simulator, not a change in the "
        "patient. The values shown are the last completed step. Reset to start a new run."
    )
    assert run._failure_details.details() == _expected_details(f"{type(error).__name__}: {error}")


def test_a_reset_refused_after_an_earlier_failure_is_named_in_the_details(
    application: QApplication,
) -> None:
    """A controller keeps its first failure, so the refusal is added to the details below it."""

    controller = _StepFailingController(_real_step_failure())
    controller.set_cardiac_output(CardiacOutput(6.0))
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()
    _steps(run, 3)
    _with_stale_tissue_flows(controller, 5.0)

    run._reset_button.click()
    _settle(application)

    details = run._failure_details.details()
    assert details is not None
    lines = details.splitlines()
    assert lines[1].startswith("What stopped the run: SimulationNumericalError: ")
    assert lines[2].startswith(
        "Reset was then refused: SimulationConfigurationError: the tissue groups are perfused "
        "at 5.0 L/min in total but cardiac output is 6.0 L/min"
    )


def test_the_details_of_a_compared_run_name_the_run(application: QApplication) -> None:
    """With two runs drawn, the copied details say which run stopped."""

    case = _branched_case()
    view = _case_view(application, case)
    _take_fork(view, 60.0)
    branch = view.runs[-1]
    branch.halt(_real_step_failure())
    view.present(False)
    _settle(application)

    details = branch._failure_details.details()
    assert details is not None
    assert details.splitlines()[1] == "Stopped run: Run 2"
    # Two runs' buttons read alike, so a screen reader hears the run's name.
    assert branch._failure_details.toggle.accessibleName() == "Show details for Run 2"
    assert branch._failure_details.copy_button.accessibleName() == "Copy details for Run 2"
    assert view.runs[0]._failure_details.details() is None
    assert view.runs[0]._halt_banner.isHidden()
