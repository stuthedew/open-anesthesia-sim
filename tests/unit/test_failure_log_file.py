"""The file that a launch logs failures to, and how a failure's details find it (`PL-XWCH`).

`tests/integration/test_failure_log.py` holds a run's failure record reaching
the file. These tests hold the file's own settings: where it is made, how it
is rotated and encoded, how each record is written, and that the details of
a failure name the same file. The `tests/conftest.py` fixture removes each
handler a test adds.
"""

import io
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

import pytest

from anesthesia_sim.app.failures import (
    FAILURE_LOG_MAX_BYTES,
    FAILURE_LOG_NAME,
    failure_log_path,
    open_failure_log,
)
from anesthesia_sim.layout.store import USER_DIRECTORY_VARIABLE


def _file_handler() -> RotatingFileHandler:
    handlers = [
        handler
        for handler in logging.getLogger("anesthesia_sim").handlers
        if isinstance(handler, RotatingFileHandler)
    ]

    assert len(handlers) == 1

    return handlers[0]


def test_the_log_is_made_in_the_platform_s_folder_with_any_missing_parents(tmp_path: Path) -> None:
    """With no override, the platform's folder is used, and each missing folder is made."""

    standard = tmp_path / "not" / "yet" / "made"

    path = open_failure_log(str(standard), {})

    assert path == standard / FAILURE_LOG_NAME
    assert path.is_file()


def test_the_log_keeps_one_earlier_file_and_writes_utf_8(tmp_path: Path) -> None:
    """The file rotates at its size limit into one earlier file, and is written as UTF-8."""

    open_failure_log("", {USER_DIRECTORY_VARIABLE: str(tmp_path)})
    handler = _file_handler()

    assert handler.maxBytes == FAILURE_LOG_MAX_BYTES
    assert handler.backupCount == 1
    assert handler.encoding == "utf-8"


def test_the_log_is_utf_8_where_the_platform_s_default_encoding_is_not(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The file's encoding is named, so a record holding "µg" is written the same on every platform.

    This container runs Python in UTF-8 mode, where the default would be
    UTF-8 anyway. The platform's default is replaced by a Windows code page
    here, as on a Windows launch outside UTF-8 mode.
    """

    def windows_default(encoding: str | None, stacklevel: int = 2) -> str:
        return encoding or "cp1252"

    monkeypatch.setattr(io, "text_encoding", windows_default)
    open_failure_log("", {USER_DIRECTORY_VARIABLE: str(tmp_path)})

    assert _file_handler().encoding == "utf-8"


def test_each_record_is_written_with_its_time_logger_and_level(tmp_path: Path) -> None:
    path = open_failure_log("", {USER_DIRECTORY_VARIABLE: str(tmp_path)})
    assert path is not None

    logging.getLogger("anesthesia_sim.app.run_view").error("Run 1 stopped: %s", "µg")
    _file_handler().flush()

    text = path.read_text("utf-8")
    assert text.endswith("\n")
    day, time, name, level, message = text.removesuffix("\n").split(" ", 4)
    datetime.strptime(f"{day} {time}", "%Y-%m-%d %H:%M:%S,%f")
    assert (name, level, message) == ("anesthesia_sim.app.run_view", "ERROR", "Run 1 stopped: µg")


def test_the_details_name_the_file_the_package_logs_to_and_the_root_logger_is_left_alone(
    tmp_path: Path,
) -> None:
    """The handler goes on the package's logger, which is where the details look for it."""

    root_before = list(logging.getLogger().handlers)
    path = open_failure_log("", {USER_DIRECTORY_VARIABLE: str(tmp_path)})

    assert failure_log_path() == path
    assert logging.getLogger().handlers == root_before


def test_no_file_is_named_while_none_is_kept() -> None:
    assert failure_log_path() is None
