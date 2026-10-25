"""`docket record N` runs the project's `record_command` once the number is written (`PL-SG93`)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from docket import cli
from docket.config import load


def test_the_setting_is_read_and_empty_by_default(tmp_path: Path) -> None:
    assert load(tmp_path).record_command == ""
    (tmp_path / "docket.toml").write_text(
        '[docket]\nrecord_command = "python3 copy.py"\n', encoding="utf-8"
    )
    assert load(tmp_path).record_command == "python3 copy.py"


def test_the_command_s_output_is_printed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    program = tmp_path / "copy.py"
    program.write_text("print('copied 2 refusals')\n", encoding="utf-8")
    cli._run_record_command(f"{sys.executable} {program}", tmp_path)
    assert capsys.readouterr().out == "copied 2 refusals\n"


def test_a_failing_command_is_reported_and_raises_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    program = tmp_path / "copy.py"
    program.write_text("import sys\nsys.exit('disk full')\n", encoding="utf-8")
    cli._run_record_command(f"{sys.executable} {program}", tmp_path)
    assert "exited 1: disk full" in capsys.readouterr().out


def test_no_command_runs_nothing(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cli._run_record_command("", tmp_path)
    assert capsys.readouterr().out == ""
