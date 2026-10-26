"""Tests for `.claude/hooks/thread_hooks.py`, which gives a Projects thread the repository's hooks.

The hook writes the user settings that Claude Code reads for the rest of the
session, so the failures worth guarding are the quiet ones: a write in a
session that already loads the repository's settings, which would run every
guard twice; a write that drops the user's other settings or the hook's own
entry, which would switch the bridge off for the next start; and a second run
of the session-start commands on a start that already ran them. The setup
script is tested by running it, since the owner pastes it into a box where
nothing checks it.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import thread_hooks

REPO = Path(__file__).resolve().parents[2]

#: A repository settings file in the shape `.claude/settings.json` has: one
#: guard on Bash, and a session-start command that prints a line.
PROJECT = {
    "effortLevel": "high",
    "hooks": {
        "SessionStart": [{"hooks": [{"type": "command", "command": "echo digest-ran"}]}],
        "PreToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": "bash guard.sh"}]}
        ],
    },
}


def _checkout(tmp_path: Path, settings: dict[str, object] = PROJECT) -> Path:
    root = tmp_path / "checkout"
    (root / ".claude").mkdir(parents=True)
    (root / ".claude" / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
    return root


def _start(
    root: Path, user_path: Path, source: str = "startup", entrypoint: str = "remote_projects"
) -> str:
    return thread_hooks.main(
        json.dumps({"source": source}), entrypoint=entrypoint, root=root, user_path=user_path
    )


def test_a_project_thread_gets_the_repository_hooks_in_its_user_settings(tmp_path: Path) -> None:
    root = _checkout(tmp_path)
    user_path = tmp_path / "home" / ".claude" / "settings.json"

    printed = _start(root, user_path)

    user = json.loads(user_path.read_text(encoding="utf-8"))
    assert user["hooks"]["PreToolUse"] == PROJECT["hooks"]["PreToolUse"]
    # The repository's entry, and then the hook's own, so the next start runs it again.
    starts = user["hooks"]["SessionStart"]
    assert starts[0] == PROJECT["hooks"]["SessionStart"][0]
    assert starts[1]["hooks"][0]["command"] == thread_hooks.BOOTSTRAP_COMMAND
    # Only the hooks are copied: the repository's other settings stay its own.
    assert "effortLevel" not in user
    # The first write runs the repository's session-start command and passes its output on.
    assert printed == "digest-ran\n"


def test_a_later_start_with_the_hooks_in_place_writes_and_runs_nothing(tmp_path: Path) -> None:
    root = _checkout(tmp_path)
    user_path = tmp_path / "home" / ".claude" / "settings.json"
    _start(root, user_path)
    written = user_path.stat().st_mtime_ns

    # Claude Code runs the copied session-start entry itself on this start.
    assert _start(root, user_path, source="compact") == ""
    assert user_path.stat().st_mtime_ns == written


def test_the_user_s_other_settings_and_the_setup_script_s_entry_survive_the_write(
    tmp_path: Path,
) -> None:
    root = _checkout(tmp_path)
    user_path = tmp_path / "home" / ".claude" / "settings.json"
    user_path.parent.mkdir(parents=True)
    own_entry = {"hooks": [{"type": "command", "command": "python3 /x/thread_hooks.py"}]}
    user_path.write_text(
        json.dumps({"theme": "dark", "hooks": {"SessionStart": [own_entry], "Stop": []}}),
        encoding="utf-8",
    )

    _start(root, user_path)

    user = json.loads(user_path.read_text(encoding="utf-8"))
    assert user["theme"] == "dark"
    # The entry the setup script wrote is the one kept, in its own wording, once.
    assert user["hooks"]["SessionStart"] == [PROJECT["hooks"]["SessionStart"][0], own_entry]
    # The hooks block becomes the repository's: a hook the user file held alone goes.
    assert "Stop" not in user["hooks"]


def test_a_change_to_the_repository_hooks_reaches_the_user_settings_at_the_next_start(
    tmp_path: Path,
) -> None:
    user_path = tmp_path / "home" / ".claude" / "settings.json"
    _start(_checkout(tmp_path), user_path)
    changed = {"hooks": {**PROJECT["hooks"], "PreToolUse": []}}
    (tmp_path / "checkout" / ".claude" / "settings.json").write_text(
        json.dumps(changed), encoding="utf-8"
    )

    _start(tmp_path / "checkout", user_path)

    assert json.loads(user_path.read_text(encoding="utf-8"))["hooks"]["PreToolUse"] == []


@pytest.mark.parametrize("entrypoint", ["remote_desktop", "cli", None])
def test_outside_a_project_thread_it_writes_nothing(tmp_path: Path, entrypoint: str | None) -> None:
    """Those sessions load `.claude/settings.json` themselves.

    A copy in the user settings would run each hook twice.
    """
    user_path = tmp_path / "home" / ".claude" / "settings.json"

    assert _start(_checkout(tmp_path), user_path, entrypoint=entrypoint) == ""
    assert not user_path.exists()


def test_a_checkout_with_no_readable_hooks_writes_nothing(tmp_path: Path) -> None:
    root = tmp_path / "checkout"
    (root / ".claude").mkdir(parents=True)
    (root / ".claude" / "settings.json").write_text("{not json", encoding="utf-8")
    user_path = tmp_path / "home" / ".claude" / "settings.json"

    assert _start(root, user_path) == ""
    assert not user_path.exists()


def test_a_failing_session_start_command_is_named_in_what_the_start_prints(tmp_path: Path) -> None:
    settings = {"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "exit 3"}]}]}}
    root = _checkout(tmp_path, settings)

    printed = _start(root, tmp_path / "home" / ".claude" / "settings.json")

    assert printed == thread_hooks.COMMAND_FAILED.format(command="exit 3", reason="exit 3") + "\n"


@pytest.mark.parametrize(
    ("matcher", "source", "runs"),
    [
        (None, "compact", True),
        ("*", "resume", True),
        ("startup|resume", "startup", True),
        ("startup|resume", "compact", False),
        ("(", "startup", False),
    ],
)
def test_a_session_start_command_runs_only_on_the_starts_its_matcher_names(
    matcher: str | None, source: str, runs: bool
) -> None:
    group: dict[str, object] = {"hooks": [{"type": "command", "command": "echo x"}]}
    if matcher is not None:
        group["matcher"] = matcher

    commands = thread_hooks.start_commands({"SessionStart": [group]}, source)

    assert commands == ([("echo x", float(thread_hooks.COMMAND_TIMEOUT_S))] if runs else [])


def test_the_setup_script_adds_the_entry_once_and_keeps_what_the_file_held(tmp_path: Path) -> None:
    home = tmp_path / "home"
    (home / ".claude").mkdir(parents=True)
    (home / ".claude" / "settings.json").write_text(json.dumps({"theme": "dark"}), encoding="utf-8")
    script = thread_hooks.setup_script()

    for _ in range(2):
        result = subprocess.run(
            ["bash", "-c", script], env={"HOME": str(home), "PATH": "/usr/bin:/bin"}, check=False
        )
        assert result.returncode == 0

    user = json.loads((home / ".claude" / "settings.json").read_text(encoding="utf-8"))
    assert user["theme"] == "dark"
    commands = [
        hook["command"] for group in user["hooks"]["SessionStart"] for hook in group["hooks"]
    ]
    assert commands == [thread_hooks.BOOTSTRAP_COMMAND]


def test_the_owner_s_copy_of_the_setup_script_is_the_one_the_hook_prints() -> None:
    """`docs/maintainer.md` carries the script the owner pastes.

    So it must not drift from the script the hook prints.
    """
    maintainer = (REPO / "docs" / "maintainer.md").read_text(encoding="utf-8")

    assert f"```bash\n{thread_hooks.setup_script()}```" in maintainer
