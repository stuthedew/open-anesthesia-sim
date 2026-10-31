"""Tests for the thread-probe test plugin under `plugins/thread-probe/` (`PL-SQV9`).

The plugin is a test the owner runs once, in a Projects thread, after adding
it in Project settings > Plugins. A defect in it would cost that test without
saying so: a hook file in a shape Claude Code does not load, a marketplace
entry that points nowhere, or a hook that refuses the wrong commands. So the
tests run the hook as Claude Code would and read the files it would read.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PLUGIN = REPO / "plugins" / "thread-probe"
PROBE = PLUGIN / "hooks" / "probe.py"


def run(event: str, payload: dict[str, object], project: Path) -> str:
    """Run the hook for one event with `project` as `CLAUDE_PROJECT_DIR`."""
    result = subprocess.run(
        [sys.executable, str(PROBE), event],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=True,
        env={"CLAUDE_PROJECT_DIR": str(project), "CLAUDE_PLUGIN_ROOT": str(PLUGIN)},
    )
    return result.stdout


def test_the_sentinel_command_is_refused_and_names_the_repository_settings() -> None:
    out = run("pre-tool-use", {"tool_input": {"command": "echo thread-probe-sentinel"}}, REPO)
    decision = json.loads(out)["hookSpecificOutput"]
    assert decision["permissionDecision"] == "deny"
    assert (
        "repository .claude/settings.json: readable, hook events"
        in decision["permissionDecisionReason"]
    )
    assert "PreToolUse" in decision["permissionDecisionReason"]


def test_any_other_command_passes(tmp_path: Path) -> None:
    assert run("pre-tool-use", {"tool_input": {"command": "uv run pytest -q"}}, tmp_path) == ""


def test_session_start_says_when_the_repository_settings_cannot_be_read(tmp_path: Path) -> None:
    out = run("session-start", {}, tmp_path)
    assert out.startswith("thread-probe: the plugin's SessionStart hook ran.")
    assert "not readable (FileNotFoundError)" in out


def test_the_hook_file_has_the_wrapper_claude_code_requires() -> None:
    # A hooks file without the top-level "hooks" key fails to load
    # (https://code.claude.com/docs/en/plugins-reference.md, § "hooks").
    hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text())
    assert set(hooks) == {"hooks"}
    assert set(hooks["hooks"]) == {"SessionStart", "PreToolUse"}


def test_the_marketplace_entry_points_at_the_plugin() -> None:
    marketplace = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text())
    (entry,) = marketplace["plugins"]
    manifest = json.loads((REPO / entry["source"] / ".claude-plugin" / "plugin.json").read_text())
    assert entry["name"] == manifest["name"] == "thread-probe"
    assert (REPO / entry["source"] / "skills" / "thread-probe" / "SKILL.md").is_file()
