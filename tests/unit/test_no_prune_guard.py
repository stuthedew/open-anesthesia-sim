"""Tests for `.claude/hooks/no-prune-guard.sh`, the remote-ref prune refusal.

`PL-JK0M` routed this rule out of `CLAUDE.md`, where it was ten resident lines
every session carried before it had read anything, into the hook that decides
it. What the prose bought was a session remembering; what this buys is a
refusal, so the tests that matter are about what it refuses and - more
delicately - what it lets through. A guard on a command string is one
over-broad pattern away from blocking the repository's own documentation of the
rule, which is why the heredoc and quoted-argument cases below are here.

Nothing in this file runs git. The hook decides on the command text alone.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "no-prune-guard.sh"


def _decision(command: str, *, tool: str = "Bash") -> dict[str, str] | None:
    """The hook's `hookSpecificOutput` for one tool call, or `None` if it stayed quiet."""
    payload = json.dumps({"tool_name": tool, "tool_input": {"command": command}})
    result = subprocess.run(
        ["bash", str(HOOK)], input=payload, capture_output=True, text=True, timeout=20
    )
    assert result.returncode == 0, result.stderr
    if not result.stdout.strip():
        return None
    return json.loads(result.stdout)["hookSpecificOutput"]


PRUNING = (
    "git fetch --prune",
    "git fetch -p origin",
    "git fetch origin --prune-tags",
    "git remote prune origin",
    "git remote update --prune",
    "git config remote.origin.prune true",
    "git config --global fetch.prune true",
    "git fetch origin && git fetch --prune",
    "GIT_TRACE=1 git fetch --prune",
)


@pytest.mark.parametrize("command", PRUNING)
def test_a_pruning_call_is_denied(command: str) -> None:
    """Every spelling that deletes a remote-tracking ref is refused."""
    decision = _decision(command)
    assert decision is not None, f"{command!r} was allowed"
    assert decision["permissionDecision"] == "deny"
    assert decision["hookEventName"] == "PreToolUse"


def test_the_refusal_answers_the_question_the_caller_had() -> None:
    """A denial that only says no leaves the session to invent the safe form."""
    reason = _decision("git fetch --prune")["permissionDecisionReason"]
    assert "bin/docket stranded" in reason
    assert "git branch -dr origin/<branch>" in reason
    assert "git checkout -B <branch> origin/main" in reason


ALLOWED = (
    # The fetch every session runs, and the one `docket branch` runs for it.
    "git fetch origin",
    "git fetch origin main",
    "git fetch --tags",
    # A branch name is not a flag, however much of one it contains.
    "git fetch origin my-prefix-branch",
    "git fetch origin claude/pl-jk0m-prune-guard",
    # `-p` means something else on every other subcommand.
    "git log --oneline -p HEAD",
    "git show -p HEAD",
    # The safe restart the deny message recommends must not itself be denied.
    "git branch -dr origin/x && git fetch origin main",
    # Reading and writing *about* the rule. The repository does this constantly:
    # this file, the hook, `docs/resident-instructions.md`, the item.
    "grep -n -- --prune tools/doc_check.py",
    'echo "never git fetch --prune"',
    "cat > f.md <<'EOF'\ngit fetch --prune\nEOF",
)


@pytest.mark.parametrize("command", ALLOWED)
def test_an_innocent_call_is_untouched(command: str) -> None:
    """Silence, not an allow: the hook must never grant a permission either."""
    assert _decision(command) is None, f"{command!r} was denied"


def test_another_tool_is_not_this_hook_s_business() -> None:
    """The matcher is `Bash`; a payload from anything else is passed over."""
    assert _decision("git fetch --prune", tool="Edit") is None


def test_an_unreadable_payload_fails_open() -> None:
    """A guard that breaks the session costs more than the ref it protects."""
    result = subprocess.run(
        ["bash", str(HOOK)], input="not json", capture_output=True, text=True, timeout=20
    )
    assert result.returncode == 0
    assert not result.stdout.strip()


def test_the_hook_is_wired_into_the_settings_it_guards() -> None:
    """An unwired hook is prose with extra steps, and nothing would say so."""
    settings = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
    commands = [
        hook["command"]
        for entry in settings["hooks"]["PreToolUse"]
        if entry.get("matcher") == "Bash"
        for hook in entry["hooks"]
    ]
    assert any("no-prune-guard.sh" in command for command in commands)
