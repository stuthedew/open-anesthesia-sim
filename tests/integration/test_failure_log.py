"""The failure log that a launch keeps in the reader's data directory (`PL-TWZY`).

The halt banner words a failure for the learner and can leave out the
exception's own message. That message is written for a developer, so the
launch keeps it in a file, where it survives a session started from an icon
with no terminal.
"""

import logging
from pathlib import Path

from anesthesia_sim.app.failures import FAILURE_LOG_NAME, open_failure_log
from anesthesia_sim.layout.store import USER_DIRECTORY_VARIABLE


def test_a_failure_logged_by_a_run_reaches_the_file_in_the_data_directory(tmp_path: Path) -> None:
    """A record that a run's halt logs is written to `failures.log` in the data directory."""

    path = open_failure_log("", {USER_DIRECTORY_VARIABLE: str(tmp_path / "data")})

    assert path == tmp_path / "data" / FAILURE_LOG_NAME

    logging.getLogger("anesthesia_sim.app.run_view").error(
        "Run 1 stopped on a failure: %s", "unaccounted=6.000000e+00 L"
    )

    for handler in logging.getLogger("anesthesia_sim").handlers:
        handler.flush()

    assert "Run 1 stopped on a failure: unaccounted=6.000000e+00 L" in path.read_text("utf-8")


def test_no_data_directory_keeps_no_file_and_adds_no_handler() -> None:
    """With no directory to write to, the records reach standard error only."""

    package = logging.getLogger("anesthesia_sim")
    before = list(package.handlers)

    assert open_failure_log("", {}) is None
    assert package.handlers == before


def test_a_data_directory_that_cannot_be_made_keeps_no_file_and_lets_the_launch_go_on(
    tmp_path: Path,
) -> None:
    """A data directory named by an existing file adds no handler and raises nothing.

    The log helps a developer find a fault, so a directory it cannot use never
    stops the application from opening. Before the fix, `mkdir` raised
    `FileExistsError` out of `main()`.
    """

    occupied = tmp_path / "data"
    occupied.write_text("not a directory", "utf-8")
    package = logging.getLogger("anesthesia_sim")
    before = list(package.handlers)

    assert open_failure_log("", {USER_DIRECTORY_VARIABLE: str(occupied)}) is None
    assert package.handlers == before
