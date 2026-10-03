"""Tests for `.claude/hooks/direct-merge-guard.sh`, the gate on a session's own merge (`PL-NXRJ`).

A session merges by arming auto-merge, and squash-merges a pull request GitHub
will not arm because it is already green and current only while the base
branch's protection binds an admin, so that GitHub itself refuses a stale or
red merge (`PL-NXRJ`, reopening `PL-V2X5`). What is pinned is that the matcher
reaches the tool at all, that the record read at the call decides in both
directions, that the base is read from the pull request rather than assumed,
and which way each unreadable payload, unanswered read and failed python3 step
fails. GitHub is served from files through the hook's `DIRECT_MERGE_GUARD_API`,
so no test reaches the network.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "direct-merge-guard.sh"
SETTINGS = REPO / ".claude" / "settings.json"
BASH = shutil.which("bash") or "bash"

MERGE = "mcp__github__merge_pull_request"
OWNER, NAME, NUMBER = "stuthedew", "open-anesthesia-sim", 1224
MERGE_INPUT = {"owner": OWNER, "repo": NAME, "pullNumber": NUMBER}
MERGE_CALL = json.dumps({"tool_name": MERGE, "tool_input": MERGE_INPUT})


def _github(root: Path, levels: dict[str, str], base: str = "main") -> Path:
    """A file tree the hook reads as the GitHub API: the pull's base, and each branch's level."""
    repository = root / "repos" / OWNER / NAME
    (repository / "pulls").mkdir(parents=True)
    (repository / "pulls" / str(NUMBER)).write_text(json.dumps({"base": {"ref": base}}))
    (repository / "branches").mkdir()
    for branch, level in levels.items():
        checks = {"enforcement_level": level, "contexts": ["checks", "pr-title"]}
        record = {"protection": {"enabled": True, "required_status_checks": checks}}
        (repository / "branches" / branch).write_text(json.dumps(record))
    return root


def _decision(payload: str, api: Path, path: str | None = None) -> dict[str, str] | None:
    """The hook's `hookSpecificOutput` for one call, or `None` if it let the call through."""
    env = {**os.environ, "DIRECT_MERGE_GUARD_API": api.as_uri()}
    if path is not None:
        env["PATH"] = path
    result = subprocess.run(
        [BASH, str(HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    if not result.stdout.strip():
        return None
    output: dict[str, dict[str, str]] = json.loads(result.stdout)
    return output["hookSpecificOutput"]


def _refusal(decision: dict[str, str] | None) -> str:
    """The reason a refusal gives, after checking it is one."""
    assert decision is not None
    assert decision["hookEventName"] == "PreToolUse"
    assert decision["permissionDecision"] == "deny"
    return decision["permissionDecisionReason"]


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
        MERGE_CALL,
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
def test_a_merge_is_let_through_while_the_base_binds_admins(payload: str, tmp_path: Path) -> None:
    """`everyone` means GitHub refuses a stale or red merge itself, so the hook does not."""
    assert _decision(payload, _github(tmp_path, {"main": "everyone"})) is None


def test_a_merge_is_refused_while_the_base_exempts_admins(tmp_path: Path) -> None:
    reason = _refusal(_decision(MERGE_CALL, _github(tmp_path, {"main": "non_admins"})))
    assert "`enforcement_level: non_admins`" in reason
    # The route that stays: arm while a check runs, or the owner's click.
    assert "`enable_pr_auto_merge`" in reason
    assert "the Squash and merge is theirs" in reason
    assert "`docs/maintainer.md`" in reason


def test_the_base_is_read_from_the_pull_request(tmp_path: Path) -> None:
    """A pull request into a branch that exempts admins is refused while `main` binds them."""
    api = _github(tmp_path, {"main": "everyone", "release": "non_admins"}, base="release")
    assert "`release`" in _refusal(_decision(MERGE_CALL, api))


def test_a_merge_is_refused_where_github_does_not_answer(tmp_path: Path) -> None:
    """No record to read is a refusal, never a pass."""
    assert "GitHub did not answer" in _refusal(_decision(MERGE_CALL, tmp_path))


def test_a_failed_python3_step_is_refused(tmp_path: Path) -> None:
    """A python3 that fails before deciding has read nothing, so the merge is refused."""
    tools = tmp_path / "bin"
    tools.mkdir()
    for name in ("cat", "sed", "head"):
        found = shutil.which(name)
        assert found is not None, name
        (tools / name).symlink_to(found)
    (tools / "python3").write_text("#!/bin/sh\nexit 1\n")
    (tools / "python3").chmod(0o755)
    api = _github(tmp_path / "api", {"main": "everyone"})
    assert "python3" in _refusal(_decision(MERGE_CALL, api, path=str(tools)))


def test_another_tool_is_let_through(tmp_path: Path) -> None:
    """Wired to the wrong matcher, the hook refuses nothing rather than everything."""
    payload = json.dumps({"tool_name": "mcp__github__enable_pr_auto_merge", "tool_input": {}})
    assert _decision(payload, tmp_path) is None


@pytest.mark.parametrize("payload", ["", "not json", "{}"], ids=["empty", "not-json", "no-name"])
def test_a_payload_naming_no_tool_is_refused(payload: str, tmp_path: Path) -> None:
    """The matcher has already chosen a merge call, so an unreadable one fails closed."""
    _refusal(_decision(payload, _github(tmp_path, {"main": "everyone"})))
