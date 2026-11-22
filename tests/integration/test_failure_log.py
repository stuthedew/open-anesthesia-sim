"""The failure log that a launch keeps in the reader's data directory (`PL-TWZY`).

The halt banner words a failure for the learner and can leave out the
exception's own message. That message is written for a developer, so the
launch keeps it in a file, where it survives a session started from an icon
with no terminal.
"""

import logging
from collections.abc import Iterator
from pathlib import Path

import pytest

from anesthesia_sim.app.main import FAILURE_LOG_NAME, open_failure_log
from anesthesia_sim.layout.store import USER_DIRECTORY_VARIABLE


@pytest.fixture
def package_handlers() -> Iterator[None]:
    """Remove each handler that a test added to the package's logger, and close it."""

    package = logging.getLogger("anesthesia_sim")
    before = list(package.handlers)
    yield

    for handler in package.handlers[len(before) :]:
        package.removeHandler(handler)
        handler.close()


@pytest.mark.usefixtures("package_handlers")
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


@pytest.mark.usefixtures("package_handlers")
def test_no_data_directory_keeps_no_file_and_adds_no_handler() -> None:
    """With no directory to write to, the records reach standard error only."""

    package = logging.getLogger("anesthesia_sim")
    before = list(package.handlers)

    assert open_failure_log("", {}) is None
    assert package.handlers == before
