"""Tests for `.claude/hooks/direct-merge-guard.sh`, which refuses a session's own merge (`PL-S17R`).

A session merges only by arming auto-merge, and a pull request already green and
current is the owner's Squash and merge (`PL-V2X5`). The hook refuses the GitHub
server's merge tool outright, so what is pinned is that the matcher reaches the
tool at all, what the refusal tells the session, and which way each unreadable
payload fails.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "direct-merge-guard.sh"
SETTINGS = REPO / ".claude" / "settings.json"

MERGE = "mcp__github__merge_pull_request"
MERGE_INPUT = {"owner": "stuthedew", "repo": "open-anesthesia-sim", "pullNumber": 1224}


def _decision(payload: str) -> dict[str, str] | None:
    """The hook's `hookSpecificOutput` for one call, or `None` if it let the call through."""
    result = subprocess.run(
        ["bash", str(HOOK)], input=payload, capture_output=True, text=True, timeout=30, check=False
    )
    assert result.returncode == 0, result.stderr
    if not result.stdout.strip():
        return None
    output: dict[str, dict[str, str]] = json.loads(result.stdout)
    return output["hookSpecificOutput"]


def _matches(matcher: str, tool: str) -> bool:
    """Claude Code's matcher rule (https://code.claude.com/docs/en/hooks, read 2026-09-30).

    `*` or an empty matcher matches every tool. One made only of letters,
    digits, `_`, `-`, spaces, `,` and `|` is a list of exact names; anything
    else is a JavaScript regular expression tested unanchored, which
    `re.search` reproduces for the patterns wired here.
    """
    if matcher in ("", "*"):
        return True
    if re.fullmatch(r"[A-Za-z0-9_\- ,|]*", matcher):
        return tool in {name.strip() for name in re.split(r"[|,]", matcher)}
    return re.search(matcher, tool) is not None


def test_the_matcher_reaches_the_merge_tool_and_nothing_else() -> None:
    """A matcher naming no tool passes every other test here and refuses nothing in practice."""
    matchers = [
        entry.get("matcher", "")
        for entry in json.loads(SETTINGS.read_text())["hooks"]["PreToolUse"]
        if any("direct-merge-guard.sh" in hook["command"] for hook in entry["hooks"])
    ]
    assert len(matchers) == 1
    (matcher,) = matchers
    assert _matches(matcher, MERGE)
    for other in (
        "mcp__github__enable_pr_auto_merge",
        "mcp__github__update_pull_request_branch",
        "mcp__github__pull_request_read",
        "Bash",
    ):
        assert not _matches(matcher, other), other


@pytest.mark.parametrize(
    "payload",
    [
        json.dumps({"tool_name": MERGE, "tool_input": MERGE_INPUT}),
        json.dumps({"tool_name": MERGE, "tool_input": MERGE_INPUT}, indent=2),
        # A commit message quoting another tool's name must not supply the tool.
        json.dumps(
            {
                "tool_name": MERGE,
                "tool_input": {**MERGE_INPUT, "commit_message": '{"tool_name": "Bash"}'},
            }
        ),
    ],
    ids=["compact", "indented", "quoted-name-in-message"],
)
def test_a_merge_call_is_refused_with_the_route_the_owner_decided(payload: str) -> None:
    decision = _decision(payload)
    assert decision is not None
    assert decision["hookEventName"] == "PreToolUse"
    assert decision["permissionDecision"] == "deny"
    reason = decision["permissionDecisionReason"]
    # The route a session has, and the one PL-V2X5 leaves the owner.
    assert "`enable_pr_auto_merge`" in reason
    assert '"you can merge directly" is not addressed to a session' in reason
    assert "the Squash and merge is theirs" in reason
    assert "`docs/maintainer.md`" in reason
    assert "`PL-V2X5`" in reason


def test_another_tool_is_let_through() -> None:
    """Wired to the wrong matcher, the hook refuses nothing rather than everything."""
    payload = json.dumps({"tool_name": "mcp__github__enable_pr_auto_merge", "tool_input": {}})
    assert _decision(payload) is None


@pytest.mark.parametrize("payload", ["", "not json", "{}"], ids=["empty", "not-json", "no-name"])
def test_a_payload_naming_no_tool_is_refused(payload: str) -> None:
    """The matcher has already chosen a merge call, so an unreadable one fails closed."""
    decision = _decision(payload)
    assert decision is not None
    assert decision["permissionDecision"] == "deny"
