"""Tests for `.claude/hooks/gh_write_guard.py`, which keeps `gh` in Bash to reads (`PL-3986`).

The email guard reads MCP calls only, so a pull request body published
through `gh` in Bash never met it. What is
pinned: the three spellings `PL-3986` names are refused, the search the
harness hands a session `gh` for is not, each refusal names the MCP route,
and the hook is wired on Bash and refuses from its own script.
"""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

import gh_write_guard
import guard as entry_point
import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "guard.sh"
#: The guard's own name, which selects it alone in `guard.sh`.
GUARD = "gh-write-guard"


def _payload(command: str) -> str:
    return json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})


def _verdict(command: str) -> str | None:
    return gh_write_guard.judge(_payload(command))


#: Each `gh` call that changes GitHub, and each one this hook cannot show only
#: reads. The first three are `PL-3986`'s.
WRITES = (
    "gh pr merge 1991 --squash",
    "gh api -X PUT repos/stuthedew/open-anesthesia-sim/pulls/1991/merge",
    "gh pr create --title t --body 'Asked by someone.'",
    "gh pr edit 1991 --body b",
    "gh pr comment 1991 -b b",
    "gh pr review 1991 --approve",
    "gh issue create -t t -b b",
    "gh release create v1",
    "gh gist create notes.md",
    "gh api repos/o/r/issues -f title=t",
    "gh api repos/o/r/issues --input body.json",
    "gh api --method=PATCH repos/o/r/pulls/1",
    "gh api -XDELETE repos/o/r/git/refs/heads/x",
    "gh api graphql -f query='mutation { x }'",
    "gh api -X $METHOD repos/o/r",
    "gh $COMMAND list",
    "gh -R o/r pr list",
    "gh pr",
    "echo 1991 | xargs gh pr merge",
    "echo -X PUT | xargs gh api repos/o/r/pulls/1/merge",
    "timeout 60 gh pr merge 1991",
    "/usr/local/bin/gh pr merge 1991",
    "cd /tmp && gh pr merge 1991",
    "echo $(gh pr merge 1991)",
)


@pytest.mark.parametrize("command", WRITES)
def test_a_gh_call_that_could_write_is_refused(command: str) -> None:
    refusal = _verdict(command)

    assert refusal is not None, command
    decision = json.loads(refusal)["hookSpecificOutput"]
    assert decision["permissionDecision"] == "deny"
    assert "merge_pull_request" in decision["permissionDecisionReason"]


#: Each `gh` call that only reads, the search the harness gives first.
READS = (
    "gh api -X GET search/code -f q='expiry' --paginate",
    "gh api -X GET search/issues -f q='repo:o/r is:pr'",
    "gh api --method GET search/commits -F q=x",
    "gh api repos/o/r/pulls",
    "gh api user -q .login",
    "gh api -i -H 'Accept: application/json' repos/o/r",
    "gh search code expiry",
    "gh pr view 1991 --json state",
    "gh pr list --state open",
    "gh pr checks 1991",
    "gh run list -L 5",
    "gh auth status",
    "gh --version",
    "gh pr merge --help",
    "gh",
    "git log --oneline | head",
    "echo gh pr merge",
    "cat <<'EOF'\ngh pr merge 1\nEOF",
)


@pytest.mark.parametrize("command", READS)
def test_a_read_or_a_call_that_runs_no_gh_is_let_through(command: str) -> None:
    assert _verdict(command) is None, command


def test_the_refusal_names_each_call_it_refused() -> None:
    reason = json.loads(_verdict("gh pr view 1 && gh pr merge 1") or "{}")["hookSpecificOutput"][
        "permissionDecisionReason"
    ]

    assert "`gh pr merge 1`" in reason
    assert "`gh pr view 1`" not in reason


@pytest.mark.parametrize(("command", "refused"), [("gh pr merge 1", True), ("git status", False)])
def test_a_call_the_hook_cannot_read_is_refused_only_where_it_names_gh(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], command: str, refused: bool
) -> None:
    """A guard that breaks must not let a `gh` write through unread, nor block every other call."""

    def broken(payload: str) -> str | None:
        raise RuntimeError("reader broke")

    monkeypatch.setattr(gh_write_guard, "judge", broken)
    monkeypatch.setattr(sys, "stdin", io.StringIO(_payload(command)))

    assert entry_point.main([GUARD]) == 0
    decided = json.loads(capsys.readouterr().out)["hookSpecificOutput"]
    assert ("permissionDecision" in decided) is refused
    said = decided.get("permissionDecisionReason") or decided["additionalContext"]
    assert "reader broke" in said


@pytest.mark.parametrize(
    ("command", "names"),
    [("gh pr merge 1", True), ("x=1; /usr/local/bin/gh api", True), ("git log ghost", False)],
)
def test_names_gh_reads_words_and_paths(command: str, names: bool) -> None:
    assert gh_write_guard.names_gh(command) is names


def test_the_hook_is_wired_on_bash_and_refuses_from_its_script() -> None:
    settings = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
    wired = {
        hook["command"]: entry["matcher"]
        for entry in settings["hooks"]["PreToolUse"]
        for hook in entry["hooks"]
    }
    assert wired['bash "$CLAUDE_PROJECT_DIR/.claude/hooks/guard.sh" pre-bash'] == "Bash"
    assert GUARD in {guard.name for guard in entry_point.GROUPS["pre-bash"]}

    ran = subprocess.run(
        ["bash", str(HOOK), GUARD],
        input=_payload("gh pr merge 1991"),
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO,
    )
    assert json.loads(ran.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_the_script_lets_a_read_through() -> None:
    """Run as Claude Code runs it, with only its own directory on the path, a read passes.

    A reader that fails to load would refuse every `gh` call as unjudged, and
    the refusal test above would still pass.
    """
    ran = subprocess.run(
        ["bash", str(HOOK), GUARD],
        input=_payload("gh pr view 1991"),
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO,
    )
    assert ran.stdout == ""
