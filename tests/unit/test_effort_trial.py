"""Tests for `tools/effort_trial.py`, which assigns each cloud session's effort arm.

The model review recomputes every session's arm from the ledger by calling
`arm_for`. So the tests pin the function to hashes worked out with `sha256sum`,
outside Python: a change to it would silently move sessions between arms and
make the analysis compare the wrong groups. The other tests pin what the script
does to the settings file before and after the start time, and when the file
or the session id is not what it expects.
"""

from __future__ import annotations

import json
import sys
from datetime import timedelta
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parents[2] / "tools" / "effort_trial.py"

sys.path.insert(0, str(TOOL.parent))

import effort_trial  # noqa: E402

BEFORE = effort_trial.TRIAL_START - timedelta(seconds=1)
AFTER = effort_trial.TRIAL_START
SESSION = {effort_trial.SESSION_ID_VARIABLE: "cse_0004"}


def test_arm_matches_hashes_computed_outside_python() -> None:
    # `printf %s 0004 | sha256sum` starts 0591b59c, below 0x40000000.
    # `printf %s 0003 | sha256sum` starts 446e21f2, above it.
    assert effort_trial.arm_for("cse_0004") == "xhigh"
    assert effort_trial.arm_for("cse_0003") == "high"


def test_both_id_forms_give_the_same_arm() -> None:
    for suffix in ("0003", "0004", "01AyBidZWEWx4vfGKZs9NrGA"):
        assert effort_trial.arm_for(f"cse_{suffix}") == effort_trial.arm_for(f"session_{suffix}")


def test_about_one_session_in_four_draws_xhigh() -> None:
    arms = [effort_trial.arm_for(f"cse_{n:06d}") for n in range(4000)]
    assert 0.22 < arms.count("xhigh") / len(arms) < 0.28


def test_an_id_with_nothing_after_its_prefix_is_refused() -> None:
    with pytest.raises(ValueError, match="nothing after its prefix"):
        effort_trial.arm_for("cse_")


def test_before_the_start_it_logs_and_writes_no_settings(tmp_path: Path) -> None:
    settings, log = tmp_path / "settings.local.json", tmp_path / "trial.log"
    assert effort_trial.run(BEFORE, SESSION, settings, log) == 0
    assert not settings.exists()
    fields = log.read_text().rstrip("\n").split("\t")
    assert fields[1:4] == ["cse_0004", "xhigh", "recomputable"]
    assert fields[4].startswith("not-written")


def test_from_the_start_it_caps_the_level_and_keeps_other_keys(tmp_path: Path) -> None:
    settings, log = tmp_path / "settings.local.json", tmp_path / "trial.log"
    settings.write_text(json.dumps({"effortLevel": "medium", "theme": "dark"}))
    assert effort_trial.run(AFTER, SESSION, settings, log) == 0
    assert json.loads(settings.read_text()) == {
        "effortLevel": "xhigh",
        "maxEffortLevel": "xhigh",
        "theme": "dark",
    }


def test_settings_that_are_not_an_object_are_left_alone(tmp_path: Path) -> None:
    settings, log = tmp_path / "settings.local.json", tmp_path / "trial.log"
    settings.write_text("[]")
    assert effort_trial.run(AFTER, SESSION, settings, log) == 1
    assert settings.read_text() == "[]"
    assert "not-written" in log.read_text()


def test_a_missing_id_draws_anyway_and_says_it_cannot_be_recomputed(tmp_path: Path) -> None:
    settings, log = tmp_path / "settings.local.json", tmp_path / "trial.log"
    assert effort_trial.run(AFTER, {}, settings, log) == 0
    fields = log.read_text().rstrip("\n").split("\t")
    assert fields[1] == "no-id"
    assert fields[2] in effort_trial.ARMS
    assert fields[3] == "not-recomputable"
    assert json.loads(settings.read_text())["maxEffortLevel"] == fields[2]
