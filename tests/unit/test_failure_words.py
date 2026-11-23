"""What a failed run tells the learner, and what it keeps for a report of the fault (`PL-XWCH`).

A run halts on any exception. Before `PL-XWCH`, every failure banner other
than the accounting check's printed the exception's class name and its
message, which is written for a developer. The banner now gives plain words
for the kind of failure, and the message goes to the details under the
banner. Each expected text here is a literal, so a change to the words fails
here and is read again.
"""

from pathlib import Path

import pytest

from anesthesia_sim.app.controller import RunStatus, SimulationController
from anesthesia_sim.app.dashboard_frame import (
    failure_details,
    halt_notice,
    notice,
    refused_reset_exit,
    report_fault_text,
    shown_failure_reason,
)
from anesthesia_sim.app.failures import FailureKind, failure_kind
from anesthesia_sim.app_metadata import (
    APP_BUILD_VERSION,
    ISSUES_URL_LABEL,
    labelled_url,
    project_url,
)
from anesthesia_sim.core.exceptions import (
    AgentSimulationValidationError,
    SimulationConfigurationError,
    SimulationDomainLimitError,
    SimulationExecutionError,
    SimulationNumericalError,
)

FAULT = "This is a fault in the simulator, not a change in the patient."


def _failed(reason: str, kind: FailureKind) -> RunStatus:
    return RunStatus(
        is_running=False,
        supported_limit_reason=None,
        failure_reason=reason,
        failure_kind=kind,
        rejected_accounting=None,
    )


@pytest.mark.parametrize(
    ("error", "kind"),
    [
        (AgentSimulationValidationError("the totals did not balance"), FailureKind.ACCOUNTING),
        (SimulationNumericalError("a fraction of -1.0"), FailureKind.NUMERICAL),
        (SimulationConfigurationError("a flow of -1 L/min"), FailureKind.CONFIGURATION),
        (SimulationExecutionError("the run could not go on"), FailureKind.EXECUTION),
        (SimulationDomainLimitError("past the supported run length"), FailureKind.EXECUTION),
        (TypeError("boom"), FailureKind.UNEXPECTED),
        (KeyError("tidal volume"), FailureKind.UNEXPECTED),
    ],
    ids=["accounting", "numerical", "configuration", "execution", "domain limit", "type", "key"],
)
def test_each_failure_is_sorted_by_its_most_specific_type(
    error: BaseException, kind: FailureKind
) -> None:
    """The accounting check's error is a numerical error too, and keeps its own kind.

    A run that reaches its supported run length is not recorded as a failure
    (`halt_disposition`), so its type falls under the execution errors only
    if it is ever recorded as one.
    """

    assert failure_kind(error) is kind


@pytest.mark.parametrize(
    ("kind", "words"),
    [
        (
            FailureKind.ACCOUNTING,
            "the agent accounting check failed: the rejected step created or lost "
            "anesthetic agent.",
        ),
        (
            FailureKind.NUMERICAL,
            "the model produced a value it cannot hold, such as a negative amount of agent.",
        ),
        (
            FailureKind.CONFIGURATION,
            "one part of the simulator gave another a value that it does not accept.",
        ),
        (FailureKind.EXECUTION, "the simulator could not continue the run safely."),
        (
            FailureKind.UNEXPECTED,
            "an unexpected error occurred in the simulator, and its cause is not known.",
        ),
    ],
)
def test_each_kind_of_failure_has_its_own_plain_words_and_no_developer_message(
    kind: FailureKind, words: str
) -> None:
    """The banner says what kind of fault stopped the run, and never the exception's message.

    Microsoft's guidance asks for a different message for each cause that can
    be detected, and for an unknown error to say so (`PL-XWCH` quotes it).
    """

    reason = "SimulationNumericalError: fraction of -1.0 is outside 0 to 1"
    status = _failed(reason, kind)

    assert shown_failure_reason(status) == f"{words} {FAULT.removesuffix('.')}"
    banner = notice(status, None)
    assert banner == (
        f"Simulation stopped — {words} {FAULT} The values shown are the last completed step. "
        "Reset to start a new run."
    )
    assert reason not in banner
    assert "Error" not in banner
    undrawn = halt_notice(status)
    assert undrawn is not None
    assert undrawn.startswith(f"Simulation stopped — {words} {FAULT} ")
    assert reason not in undrawn


def test_a_run_that_has_not_failed_shows_no_failure_words_or_details() -> None:
    """A paused run and a run at the supported run length did not fail."""

    for status in (
        SimulationController().status(),
        RunStatus(
            is_running=False,
            supported_limit_reason="this run has reached 86400 s of simulated time",
            failure_reason=None,
            failure_kind=None,
            rejected_accounting=None,
        ),
    ):
        assert shown_failure_reason(status) is None
        assert (
            failure_details(
                status, Path("/data/failures.log"), run_name=None, refused_reset_reason=None
            )
            is None
        )


def test_the_details_name_the_build_the_message_and_the_log(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The details hold what a report of the fault needs, one fact a line.

    The log's path is written from the home folder, because the report line
    asks the learner to paste the details into a public issue and the full
    path holds their login name.
    """

    monkeypatch.setenv("HOME", str(tmp_path))
    reason = "SimulationNumericalError: fraction of -1.0 is outside 0 to 1"
    log = tmp_path / ".local" / "share" / "Open Anesthesia Simulator" / "failures.log"

    details = failure_details(
        _failed(reason, FailureKind.NUMERICAL), log, run_name=None, refused_reset_reason=None
    )

    assert details == (
        f"Open Anesthesia Simulator — Version {APP_BUILD_VERSION}\n"
        f"What stopped the run: {reason}\n"
        "Failure log: ~/.local/share/Open Anesthesia Simulator/failures.log"
    )
    assert str(tmp_path) not in details


def test_a_log_outside_the_home_folder_is_given_in_full(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    log = tmp_path / "elsewhere" / "failures.log"

    details = failure_details(
        _failed("TypeError: boom", FailureKind.UNEXPECTED),
        log,
        run_name=None,
        refused_reset_reason=None,
    )

    assert details is not None
    assert details.splitlines()[-1] == f"Failure log: {log}"


def test_the_details_name_the_run_while_two_are_drawn_and_a_later_refused_reset() -> None:
    """Copied details say which run stopped, and a refused Reset is not lost to the first failure.

    A controller keeps its first failure, so without the last line a Reset
    refused after an earlier failure would be named only in the log.
    """

    first = "SimulationNumericalError: fraction of -1.0 is outside 0 to 1"
    refusal = (
        "SimulationConfigurationError: the tissue groups are perfused at 5.0 L/min in total "
        "but cardiac output is 6.0 L/min"
    )

    details = failure_details(
        _failed(first, FailureKind.NUMERICAL),
        None,
        run_name="Branch 1",
        refused_reset_reason=refusal,
    )

    assert details == (
        f"Open Anesthesia Simulator — Version {APP_BUILD_VERSION}\n"
        "Stopped run: Branch 1\n"
        f"What stopped the run: {first}\n"
        f"Reset was then refused: {refusal}\n"
        "Failure log: none is kept this session, because the data folder could not be used"
    )


def test_a_refused_reset_that_stopped_the_run_is_named_once() -> None:
    refusal = "SimulationConfigurationError: the tissue groups are perfused at 5.0 L/min"

    details = failure_details(
        _failed(refusal, FailureKind.CONFIGURATION),
        None,
        run_name=None,
        refused_reset_reason=refusal,
    )

    assert details is not None
    assert details.count("perfused") == 1
    assert "Reset was then refused" not in details


def test_the_details_say_when_no_failure_log_is_kept() -> None:
    """A data folder that could not be used keeps no log, and the details do not name one."""

    details = failure_details(
        _failed("TypeError: boom", FailureKind.UNEXPECTED),
        None,
        run_name=None,
        refused_reset_reason=None,
    )

    assert details is not None
    assert details.splitlines()[-1] == (
        "Failure log: none is kept this session, because the data folder could not be used"
    )


def test_the_report_line_links_the_issue_page_escaped_and_in_the_given_colour() -> None:
    """The link is written as the page's address, and a quote in it cannot end the attribute."""

    line = report_fault_text('https://example.org/issues?a="b"&c', link_colour="#1F2933")

    assert line == (
        "To report this fault, copy the details and paste them into a new issue on the "
        '<a href="https://example.org/issues?a=&quot;b&quot;&amp;c" style="color: #1F2933;">'
        "project's issue page</a>."
    )


def test_a_quote_in_the_link_colour_cannot_end_its_attribute_either() -> None:
    line = report_fault_text("https://example.org/issues", link_colour="#1F2933\" x='y")

    assert 'style="color: #1F2933&quot; x=&#x27;y;"' in line


def test_a_build_with_no_issue_page_says_to_send_the_details_instead() -> None:
    assert report_fault_text(None, link_colour="#1F2933") == (
        "To report this fault, copy the details and send them to the project's maintainers."
    )


def test_the_installed_metadata_names_the_project_s_issue_page() -> None:
    """`pyproject.toml`'s `[project.urls]` is the one place the address is written."""

    assert project_url(ISSUES_URL_LABEL) == (
        "https://github.com/stuthedew/open-anesthesia-sim/issues"
    )
    assert project_url("No such label") is None


def test_a_url_s_label_ends_at_the_first_comma_so_a_url_may_hold_one() -> None:
    lines = [
        "Repository, https://example.org/repository",
        "Issues, https://example.org/issues?labels=a,b",
    ]

    assert labelled_url(lines, "Issues") == "https://example.org/issues?labels=a,b"
    assert labelled_url(lines, "Repository") == "https://example.org/repository"
    assert labelled_url(["Issues,  "], "Issues") is None


def test_a_refused_reset_after_an_earlier_failure_names_its_own_kind_once() -> None:
    """The way out already says only a fault causes it, so the fault sentence is not repeated."""

    error = SimulationConfigurationError("the tissue groups are perfused at 5.0 L/min in total")

    exit_text = refused_reset_exit(
        error, recorded_failure_reason="SimulationNumericalError: an earlier failure"
    )

    assert exit_text.startswith(
        "Reset was refused — one part of the simulator gave another "
        "a value that it does not accept. No setting can "
        "repair this"
    )
    assert "perfused" not in exit_text
    assert "not a change in the patient" not in exit_text


@pytest.mark.parametrize(
    ("reason", "kind"),
    [("TypeError: boom", None), (None, FailureKind.UNEXPECTED)],
    ids=["reason without kind", "kind without reason"],
)
def test_a_status_refuses_a_failure_reason_without_its_kind(
    reason: str | None, kind: FailureKind | None
) -> None:
    """A banner with no words for its failure, or words for no failure, cannot be built."""

    with pytest.raises(
        ValueError,
        match=(
            r"^a run's failure needs both its reason and its kind, but it has "
            r"failure_reason=.* and failure_kind=.*$"
        ),
    ):
        RunStatus(
            is_running=False,
            supported_limit_reason=None,
            failure_reason=reason,
            failure_kind=kind,
            rejected_accounting=None,
        )


def test_a_controller_keeps_the_kind_of_its_first_failure() -> None:
    """The banner names the failure that stopped the run, not a later one."""

    controller = SimulationController()

    controller.fail("SimulationNumericalError: first", kind=FailureKind.NUMERICAL)
    controller.fail("TypeError: second", kind=FailureKind.UNEXPECTED)

    status = controller.status()
    assert status.failure_reason == "SimulationNumericalError: first"
    assert status.failure_kind is FailureKind.NUMERICAL
