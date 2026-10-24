"""Tests for `tools/effort_trial.py`, which assigns each cloud session's effort arm.

The tests pin what the analysis depends on. The arm is a fixed function of the
hook's session id, so a resumed session keeps it, and about one session in
four gets `xhigh`. Nothing is written before the start time or outside a cloud
session. From the start, both `effortLevel` and `maxEffortLevel` are written,
because `effortLevel` alone loses to the app's picker. Settings the script
cannot read are left alone. And the printed line names the arm it wrote, or
says plainly why there is none, since that line is the trial's only record of
the arm.

The last test runs the real session-start hook. The cap and the line must come
from one command, because Claude Code runs a session's hooks in parallel
(`PL-8MZ9`).
"""

from __future__ import annotations

import json
import subprocess
import sys
import uuid
from datetime import timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "effort_trial.py"
HOOK = REPO / ".claude" / "hooks" / "docket-digest.sh"

sys.path.insert(0, str(TOOL.parent))

import effort_trial  # noqa: E402

BEFORE = effort_trial.TRIAL_START - timedelta(seconds=1)
AFTER = effort_trial.TRIAL_START

# Two real transcript ids. Their SHA-256 digests, from `printf '%s' ID |
# sha256sum`, end in 0x4b (75, which leaves 3 when divided by 4) and in 0xb0
# (176, which 4 divides), so they fall in the `high` and `xhigh` arms.
HIGH_ID = "0ab1bc6b-c99e-5501-9804-99cdd5de3c71"
XHIGH_ID = "c2bd5b4d-bd26-512d-9475-541af23fdd0e"


def _hook_input(session_id: str) -> str:
    return json.dumps(
        {"hook_event_name": "SessionStart", "source": "startup", "session_id": session_id}
    )


def test_the_arm_is_the_sha256_rule_on_the_session_id() -> None:
    assert effort_trial.arm_for(HIGH_ID) == "high"
    assert effort_trial.arm_for(XHIGH_ID) == "xhigh"


def test_about_one_session_id_in_four_is_xhigh() -> None:
    ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"session-{index}")) for index in range(4000)]
    arms = [effort_trial.arm_for(session_id) for session_id in ids]
    # A fixed set of ids, so this cannot flake. The bounds are 4.4 standard
    # deviations of a binomial(4000, 0.25) count either side of its mean.
    assert 0.22 < arms.count("xhigh") / len(arms) < 0.28
    assert set(arms) == set(effort_trial.ARMS)


def test_a_resumed_session_writes_the_same_arm_again(tmp_path: Path) -> None:
    settings = tmp_path / "settings.local.json"
    first = effort_trial.session_start(AFTER, _hook_input(XHIGH_ID), True, settings)
    resumed = json.dumps({"source": "resume", "session_id": XHIGH_ID})
    assert effort_trial.session_start(AFTER, resumed, True, settings) == first
    assert json.loads(settings.read_text())["maxEffortLevel"] == "xhigh"


def test_from_the_start_it_caps_the_level_and_keeps_other_keys(tmp_path: Path) -> None:
    settings = tmp_path / "settings.local.json"
    settings.write_text(json.dumps({"effortLevel": "medium", "theme": "dark"}))
    line = effort_trial.session_start(AFTER, _hook_input(XHIGH_ID), True, settings)
    assert json.loads(settings.read_text()) == {
        "effortLevel": "xhigh",
        "maxEffortLevel": "xhigh",
        "theme": "dark",
    }
    assert line.startswith("Effort trial: this session is in the xhigh arm.")
    assert "capped its effort at xhigh" in line


def test_before_the_start_it_writes_and_prints_nothing(tmp_path: Path) -> None:
    settings = tmp_path / "settings.local.json"
    assert effort_trial.session_start(BEFORE, _hook_input(XHIGH_ID), True, settings) == ""
    assert not settings.exists()


def test_outside_a_cloud_session_it_writes_and_prints_nothing(tmp_path: Path) -> None:
    """The owner's own computer is not in the trial, and its settings are left alone."""
    settings = tmp_path / "settings.local.json"
    assert effort_trial.session_start(AFTER, _hook_input(HIGH_ID), False, settings) == ""
    assert not settings.exists()


def test_without_a_session_id_it_draws_nothing_and_says_why(tmp_path: Path) -> None:
    settings = tmp_path / "settings.local.json"
    for hook_input in ("", "not json", json.dumps({"source": "startup"})):
        line = effort_trial.session_start(AFTER, hook_input, True, settings)
        assert line.startswith("Effort trial: this session is in neither arm, because")
        assert "no session id" in line
    assert not settings.exists()


def test_settings_that_are_not_an_object_are_left_alone(tmp_path: Path) -> None:
    """The reason is the real one, not a claim that the file sets no cap."""
    settings = tmp_path / "settings.local.json"
    settings.write_text("[]")
    line = effort_trial.session_start(AFTER, _hook_input(HIGH_ID), True, settings)
    assert settings.read_text() == "[]"
    assert "in neither arm" in line
    assert "could not write the effort cap" in line
    assert "not a JSON object" in line
    assert "sets no maxEffortLevel" not in line


def test_the_session_start_hook_writes_the_cap_then_names_it(tmp_path: Path) -> None:
    """The real hook, given a session id, caps the session and prints that arm.

    The checkout is a temporary one holding only this script, so the hook stops
    after the trial's line, at its check for `bin/docket`.
    """
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "effort_trial.py").write_text(TOOL.read_text())
    (tmp_path / "bin").mkdir()
    (tmp_path / "bin" / "python3").symlink_to(sys.executable)
    result = subprocess.run(
        ["bash", str(HOOK)],
        cwd=tmp_path,
        env={
            "CLAUDE_PROJECT_DIR": str(tmp_path),
            "CLAUDE_CODE_REMOTE": "true",
            "PATH": f"{tmp_path / 'bin'}:/usr/bin:/bin:/usr/local/bin",
            "HOME": str(tmp_path),
        },
        input=_hook_input(XHIGH_ID),
        capture_output=True,
        text=True,
        check=False,
    )
    settings = json.loads((tmp_path / ".claude" / "settings.local.json").read_text())
    assert settings == {"effortLevel": "xhigh", "maxEffortLevel": "xhigh"}
    assert result.stdout.splitlines() == [effort_trial.arm_line("xhigh")]
