"""Tests for `tools/effort_trial.py`, which assigns each cloud session's effort arm.

The tests pin what the analysis depends on. The draw gives `xhigh` to about one
session in four. Nothing is written to the settings before the start time. From
the start, both `effortLevel` and `maxEffortLevel` are written, because
`effortLevel` alone loses to the app's picker. Settings the script cannot read
are left alone. And the digest line names the arm the settings hold, or says
plainly that there is none, since that line is the trial's only record of the
arm.
"""

from __future__ import annotations

import json
import sys
from datetime import timedelta
from pathlib import Path

TOOL = Path(__file__).resolve().parents[2] / "tools" / "effort_trial.py"

sys.path.insert(0, str(TOOL.parent))

import effort_trial  # noqa: E402

BEFORE = effort_trial.TRIAL_START - timedelta(seconds=1)
AFTER = effort_trial.TRIAL_START


def test_about_one_draw_in_four_is_xhigh() -> None:
    arms = [effort_trial.draw() for _ in range(4000)]
    # The bounds are 4.4 standard deviations of a binomial(4000, 0.25) count
    # either side of its mean, so a correct draw fails here about once in
    # 80,000 runs.
    assert 0.22 < arms.count("xhigh") / len(arms) < 0.28
    assert set(arms) == set(effort_trial.ARMS)


def test_before_the_start_it_logs_and_writes_no_settings(tmp_path: Path) -> None:
    settings, log = tmp_path / "settings.local.json", tmp_path / "trial.log"
    assert effort_trial.assign(BEFORE, "xhigh", settings, log) == 0
    assert not settings.exists()
    fields = log.read_text().rstrip("\n").split("\t")
    assert fields[1] == "xhigh"
    assert fields[2].startswith("not-written")


def test_from_the_start_it_caps_the_level_and_keeps_other_keys(tmp_path: Path) -> None:
    settings, log = tmp_path / "settings.local.json", tmp_path / "trial.log"
    settings.write_text(json.dumps({"effortLevel": "medium", "theme": "dark"}))
    assert effort_trial.assign(AFTER, "xhigh", settings, log) == 0
    assert json.loads(settings.read_text()) == {
        "effortLevel": "xhigh",
        "maxEffortLevel": "xhigh",
        "theme": "dark",
    }


def test_settings_that_are_not_an_object_are_left_alone(tmp_path: Path) -> None:
    settings, log = tmp_path / "settings.local.json", tmp_path / "trial.log"
    settings.write_text("[]")
    assert effort_trial.assign(AFTER, "high", settings, log) == 1
    assert settings.read_text() == "[]"
    assert "not-written" in log.read_text()


def test_the_digest_is_silent_before_the_start(tmp_path: Path) -> None:
    settings = tmp_path / "settings.local.json"
    settings.write_text(json.dumps({"maxEffortLevel": "xhigh"}))
    assert effort_trial.digest_line(BEFORE, "high", settings) == ""


def test_the_digest_names_the_arm_the_settings_cap(tmp_path: Path) -> None:
    settings = tmp_path / "settings.local.json"
    settings.write_text(json.dumps({"effortLevel": "high", "maxEffortLevel": "xhigh"}))
    line = effort_trial.digest_line(AFTER, "xhigh", settings)
    assert line.startswith("Effort trial arm: xhigh.")
    assert "running at xhigh" in line


def test_the_digest_says_when_there_is_no_arm(tmp_path: Path) -> None:
    missing = effort_trial.digest_line(AFTER, "", tmp_path / "absent.json")
    assert missing.startswith("Effort trial arm: none (")
    unreadable = tmp_path / "settings.local.json"
    unreadable.write_text("[]")
    assert "not a JSON object" in effort_trial.digest_line(AFTER, "", unreadable)
