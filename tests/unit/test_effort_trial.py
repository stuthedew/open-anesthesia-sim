"""Tests for `tools/effort_trial.py`, which assigns each cloud session's effort arm.

The tests pin what the analysis depends on. The arm is a fixed function of the
hook's session id, so a resumed session keeps it, and about one session in
two gets `xhigh`. Nothing is written before the start time or outside a cloud
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
# sha256sum`, end in 0x4b (75, which is odd) and in 0xb0 (176, which is
# even), so they fall in the `high` and `xhigh` arms.
HIGH_ID = "0ab1bc6b-c99e-5501-9804-99cdd5de3c71"
XHIGH_ID = "c2bd5b4d-bd26-512d-9475-541af23fdd0e"


def _hook_input(session_id: str) -> str:
    return json.dumps(
        {"hook_event_name": "SessionStart", "source": "startup", "session_id": session_id}
    )


def _copy_tool(tmp_path: Path) -> None:
    """Copy this script, and the hook module it reads the thread's entry point from."""
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "effort_trial.py").write_text(TOOL.read_text())
    (tmp_path / ".claude" / "hooks").mkdir(parents=True)
    hook_input = HOOK.parent / "hook_input.py"
    (tmp_path / ".claude" / "hooks" / "hook_input.py").write_text(hook_input.read_text())


def _run_hook(tmp_path: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    """Run the real session-start hook in a checkout holding only this script and its import.

    The hook stops after the trial's line, at its check for `bin/docket`.
    """
    _copy_tool(tmp_path)
    (tmp_path / "bin").mkdir()
    (tmp_path / "bin" / "python3").symlink_to(sys.executable)
    return subprocess.run(
        ["bash", str(HOOK)],
        cwd=tmp_path,
        env={
            "CLAUDE_PROJECT_DIR": str(tmp_path),
            "CLAUDE_CODE_REMOTE": "true",
            "PATH": f"{tmp_path / 'bin'}:/usr/bin:/bin:/usr/local/bin",
            "HOME": str(tmp_path),
            **env,
        },
        input=_hook_input(XHIGH_ID),
        capture_output=True,
        text=True,
        check=False,
    )


def test_the_arm_is_the_sha256_rule_on_the_session_id() -> None:
    assert effort_trial.arm_for(HIGH_ID) == "high"
    assert effort_trial.arm_for(XHIGH_ID) == "xhigh"


def test_about_one_session_id_in_two_is_xhigh() -> None:
    ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"session-{index}")) for index in range(4000)]
    arms = [effort_trial.arm_for(session_id) for session_id in ids]
    # A fixed set of ids, so this cannot flake. The bounds are 4.4 standard
    # deviations of a binomial(4000, 0.5) count either side of its mean.
    assert 0.465 < arms.count("xhigh") / len(arms) < 0.535
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
        "effortTrial": {"session_id": XHIGH_ID, "drawn": "xhigh", "level": "xhigh", "reason": None},
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
    """The real hook, given a session id, caps the session and prints that arm."""
    result = _run_hook(tmp_path, {})
    settings = json.loads((tmp_path / ".claude" / "settings.local.json").read_text())
    assert settings["effortLevel"] == settings["maxEffortLevel"] == "xhigh"
    assert result.stdout.splitlines() == [effort_trial.arm_line("xhigh")]


def test_a_projects_thread_writes_nothing_and_is_in_neither_arm(tmp_path: Path) -> None:
    """A thread never reads `.claude/settings.local.json`, so no arm can be claimed for it."""
    settings = tmp_path / "settings.local.json"
    line = effort_trial.session_start(AFTER, _hook_input(XHIGH_ID), True, settings, thread=True)
    assert line.startswith("Effort trial: this session is in neither arm, because")
    assert "Projects thread" in line
    assert "xhigh arm" not in line
    assert not settings.exists()
    status, moved = effort_trial.move("xhigh", "generator cause", XHIGH_ID, True, settings, True)
    assert status == 0
    assert "in neither arm" in moved
    assert not settings.exists()


def test_a_generator_cause_session_is_left_out_of_both_arms(tmp_path: Path) -> None:
    """The owner's rule of 2026-11-02 runs that work at `xhigh` whatever the draw (`PL-6LVZ`).

    The move is recorded beside the cap, and its line says the session is left
    out of both arms, for a session drawn `xhigh` as much as one drawn `high`.
    """
    for session_id, drawn in ((HIGH_ID, "high"), (XHIGH_ID, "xhigh")):
        settings = tmp_path / f"{drawn}.json"
        effort_trial.session_start(AFTER, _hook_input(session_id), True, settings)
        status, line = effort_trial.move("xhigh", "generator cause", session_id, True, settings)
        assert status == 0
        assert line == (
            f"Effort trial: this session drew the {drawn} arm and was then moved to xhigh by "
            "hand, because generator cause. Its effort is capped at xhigh for the rest of the "
            "session, and the trial's review leaves it out of both arms. Tell the owner this in "
            "your next reply."
        )
        assert json.loads(settings.read_text()) == {
            "effortLevel": "xhigh",
            "maxEffortLevel": "xhigh",
            "effortTrial": {
                "session_id": session_id,
                "drawn": drawn,
                "level": "xhigh",
                "reason": "generator cause",
            },
        }


def test_a_level_set_mid_session_survives_compaction(tmp_path: Path) -> None:
    """A compaction keeps the owner's move instead of writing the drawn cap back (`PL-WBW3`)."""
    settings = tmp_path / "settings.local.json"
    effort_trial.session_start(AFTER, _hook_input(HIGH_ID), True, settings)
    assert json.loads(settings.read_text())["effortTrial"]["reason"] is None
    _, moved = effort_trial.move("xhigh", "the owner moved it", HIGH_ID, True, settings)
    compacted = json.dumps({"source": "compact", "session_id": HIGH_ID})
    assert effort_trial.session_start(AFTER, compacted, True, settings) == moved
    written = json.loads(settings.read_text())
    assert written["maxEffortLevel"] == written["effortLevel"] == "xhigh"
    assert written["effortTrial"]["reason"] == "the owner moved it"


def test_a_move_recorded_for_another_session_does_not_carry_over(tmp_path: Path) -> None:
    """A new session id, as after `/clear`, gets its own draw and a fresh record."""
    settings = tmp_path / "settings.local.json"
    effort_trial.move("max", "the owner moved it", XHIGH_ID, True, settings)
    line = effort_trial.session_start(AFTER, _hook_input(HIGH_ID), True, settings)
    assert line == effort_trial.arm_line("high")
    written = json.loads(settings.read_text())
    assert written["maxEffortLevel"] == "high"
    assert written["effortTrial"] == {
        "session_id": HIGH_ID,
        "drawn": "high",
        "level": "high",
        "reason": None,
    }


def test_a_move_is_refused_without_a_level_a_reason_or_a_session(tmp_path: Path) -> None:
    settings = tmp_path / "settings.local.json"
    cases = (
        ("highest", "generator cause", XHIGH_ID, "not an effort level"),
        ("xhigh", "  ", XHIGH_ID, "give the reason"),
        ("xhigh", "generator cause", None, "CLAUDE_CODE_SESSION_ID"),
    )
    for level, reason, session_id, said in cases:
        status, line = effort_trial.move(level, reason, session_id, True, settings)
        assert status == 1
        assert said in line
    assert not settings.exists()


def test_outside_a_cloud_session_a_move_writes_nothing(tmp_path: Path) -> None:
    settings = tmp_path / "settings.local.json"
    status, line = effort_trial.move("xhigh", "generator cause", XHIGH_ID, False, settings)
    assert status == 0
    assert "not a cloud session" in line
    assert not settings.exists()


def test_the_session_start_hook_in_a_projects_thread_names_no_arm(tmp_path: Path) -> None:
    """The real hook reads the thread from `CLAUDE_CODE_ENTRYPOINT` and writes no cap."""
    result = _run_hook(tmp_path, {"CLAUDE_CODE_ENTRYPOINT": "remote_projects"})
    assert result.stdout.splitlines() == [effort_trial.no_arm_line(effort_trial.THREAD_REASON)]
    assert not (tmp_path / ".claude" / "settings.local.json").exists()


def test_the_move_command_reads_the_session_id_from_the_environment(tmp_path: Path) -> None:
    """`move` names the session by `CLAUDE_CODE_SESSION_ID`, and refuses a bad level."""
    _copy_tool(tmp_path)
    env = {"CLAUDE_CODE_REMOTE": "true", "CLAUDE_CODE_SESSION_ID": HIGH_ID, "PATH": "/usr/bin:/bin"}
    script = str(tmp_path / "tools" / "effort_trial.py")
    moved = subprocess.run(
        [sys.executable, script, "move", "--to", "xhigh", "--reason", "generator cause"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert moved.returncode == 0
    assert moved.stdout.strip() == effort_trial.moved_line("high", "xhigh", "generator cause")
    written = json.loads((tmp_path / ".claude" / "settings.local.json").read_text())
    assert written["effortTrial"]["session_id"] == HIGH_ID
    refused = subprocess.run(
        [sys.executable, script, "move", "--to", "highest", "--reason", "x"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert refused.returncode == 2
