"""What kind of failure stopped a run, and the file that records each failure for a developer.

A run halts on any exception (`dashboard_frame.halt_disposition`). The learner
is told in plain words what kind of fault it was, and the exception's own
message, which is written for a developer, goes to the failure log and to the
details under the banner (`PL-TWZY`, `PL-XWCH`). This module loads no toolkit,
so the controller, the banner's wording and the launch can all read it.
"""

import logging
from collections.abc import Mapping
from enum import Enum
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Final

from anesthesia_sim.core.exceptions import (
    AgentSimulationValidationError,
    SimulationConfigurationError,
    SimulationExecutionError,
    SimulationNumericalError,
)
from anesthesia_sim.layout.exceptions import LayoutRefused
from anesthesia_sim.layout.store import user_data_directory

FAILURE_LOG_NAME: Final = "failures.log"
"""The file that a launch's failure records are written to, in the reader's data directory."""

FAILURE_LOG_MAX_BYTES: Final = 1_000_000
"""The size at which the failure log is moved aside and a new one started.

A failure that repeats on every tick could otherwise fill the disk. One
megabyte holds a few hundred failures with their tracebacks.
"""

PACKAGE_LOGGER_NAME: Final = "anesthesia_sim"
"""The logger that every module's logger in the package reports to."""


class FailureKind(Enum):
    """Each kind of failure that the simulator can tell apart by the exception's type.

    Microsoft's guidance on error messages asks for a different message for
    each cause that can be detected, and for an unknown error to say that its
    cause is not known rather than guess at one. `PL-XWCH` quotes it.
    `dashboard_frame.FAILURE_CAUSE_TEXTS` gives the words for each kind.
    """

    #: The agent accounting check failed, and the step was rolled back.
    ACCOUNTING = "accounting"
    #: A step or a prediction produced a state the model cannot hold, from
    #: valid inputs, such as a negative amount or a fraction above 1.
    NUMERICAL = "numerical"
    #: The model was given a value it does not accept while a run stepped or
    #: drew. A setting the reader chose is refused before it is applied, and is
    #: not a failure.
    CONFIGURATION = "configuration"
    #: The run could not continue safely for another reason that the core
    #: names, other than reaching the supported run length.
    EXECUTION = "execution"
    #: An exception that the simulator does not raise on purpose, such as a
    #: `TypeError` from a later change to the code.
    UNEXPECTED = "unexpected"


def failure_kind(error: BaseException) -> FailureKind:
    """Return the kind of failure that `error` reports, the most specific type first.

    The accounting check's error is a numerical error too, so it is tested
    first. A run that reached its supported run length did not fail, and
    `dashboard_frame.halt_disposition` never records a failure for it.

    Args:
        error: The exception that stopped the run.
    """

    if isinstance(error, AgentSimulationValidationError):
        return FailureKind.ACCOUNTING

    if isinstance(error, SimulationNumericalError):
        return FailureKind.NUMERICAL

    if isinstance(error, SimulationConfigurationError):
        return FailureKind.CONFIGURATION

    if isinstance(error, SimulationExecutionError):
        return FailureKind.EXECUTION

    return FailureKind.UNEXPECTED


def open_failure_log(standard_location: str, environment: Mapping[str, str]) -> Path | None:
    """Write the package's error records to `failures.log` in the reader's data directory.

    The handler is added to the `anesthesia_sim` logger, so every module's
    logger under it reaches the file. The file is moved aside to
    `failures.log.1` when it reaches `FAILURE_LOG_MAX_BYTES`, and a new one is
    started.

    Args:
        standard_location: As `main.open_workspaces` takes it.
        environment: As `main.open_workspaces` takes it.

    Returns:
        The file's path, or None where neither the override nor the platform
        names a directory, or where the file cannot be opened there. The
        records then reach standard error only. The log exists to help find a
        fault, so a directory it cannot use never stops the application from
        opening. The Workspace and preference stores treat such a directory in
        the same way.
    """

    try:
        directory = user_data_directory(standard_location, environment)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / FAILURE_LOG_NAME
        handler = RotatingFileHandler(
            path, maxBytes=FAILURE_LOG_MAX_BYTES, backupCount=1, encoding="utf-8"
        )
    except LayoutRefused, OSError:
        return None

    handler.setLevel(logging.ERROR)
    handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
    package = logging.getLogger(PACKAGE_LOGGER_NAME)
    package.addHandler(handler)
    # Python's last-resort handler prints to standard error only while no
    # handler is set anywhere on the way up. With the file's handler added,
    # standard error is added back explicitly.
    package.addHandler(logging.StreamHandler())

    return path


def failure_log_path() -> Path | None:
    """Return the file that failures are logged to now, or None if no file is kept.

    The path is read from the handler that `open_failure_log` added, so it is
    the file the records actually reach. A launch whose data directory could
    not be used, and a dashboard that a test builds without a launch, keep no
    file.
    """

    for handler in logging.getLogger(PACKAGE_LOGGER_NAME).handlers:
        if isinstance(handler, RotatingFileHandler):
            return Path(handler.baseFilename)

    return None
