"""Tests for `.claude/hooks/direct-merge-guard.sh`, the gate on a session's own merge (`PL-NXRJ`).

A session merges by arming auto-merge, and squash-merges a pull request GitHub
will not arm because it is already green and current only while the base
branch's protection binds an admin, so that GitHub itself refuses a stale or
red merge (`PL-NXRJ`, reopening `PL-V2X5`). What is pinned is that every MCP
tool reaches the hook, that the script picks out a merge whatever its tool is
called and lets every other call through unread (`PL-NZJG`), that only a merge
into this repository is judged, which the hook reads from `origin` (`PL-L08H`),
that the record
read at the call decides in both
directions, that the base is read from the pull request rather than assumed,
and which way each unreadable payload, unanswered read and failed python3 step
fails. GitHub is served from files through the hook's `DIRECT_MERGE_GUARD_API`,
so no test reaches the network. `origin` is served by a git directory of its own
through `GIT_DIR`, so no test depends on how this checkout was cloned.
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
ORIGIN = f"https://github.com/{OWNER}/{NAME}.git"
# The private references corpus: no branch protection and no CI (`PL-L08H`).
CORPUS = "open-anesthesia-sim-references"


def _git_dir(root: Path, origin: str) -> Path:
    """A git directory whose `origin` is `origin`, for the hook to read through `GIT_DIR`."""
    root.mkdir(parents=True)
    # Without the `GIT_DIR` another test's fixture set, which git would write to instead.
    env = {key: value for key, value in os.environ.items() if key != "GIT_DIR"}
    for args in (["init", "-q"], ["remote", "add", "origin", origin]):
        subprocess.run(["git", *args], cwd=root, env=env, check=True, capture_output=True)
    return root / ".git"


@pytest.fixture(autouse=True)
def _origin(tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> None:
    """Every test's hook reads this repository's GitHub URL as `origin`, unless it sets another."""
    monkeypatch.setenv("GIT_DIR", str(_git_dir(tmp_path_factory.mktemp("origin") / "c", ORIGIN)))


def _github(root: Path, levels: dict[str, str], base: str = "main", name: str = NAME) -> Path:
    """A file tree the hook reads as the GitHub API: the pull's base, and each branch's level."""
    repository = root / "repos" / OWNER / name
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


def test_the_hook_is_wired_on_every_mcp_tool() -> None:
    """A matcher naming the merge tool stops the guard silently when GitHub renames it.

    The GitHub server has already folded its issue and review tools into
    `issue_write` and `pull_request_review_write`, so a renamed or folded merge
    tool must still reach the hook, on any server (`PL-NZJG`). A matcher naming
    no tool at all passes every other test here and refuses nothing in practice.
    """
    matchers = [
        entry.get("matcher", "")
        for entry in json.loads(SETTINGS.read_text())["hooks"]["PreToolUse"]
        if any("direct-merge-guard.sh" in hook["command"] for hook in entry["hooks"])
    ]
    assert len(matchers) == 1
    (matcher,) = matchers
    for tool in (
        MERGE,
        "mcp__github__merge_pr",
        "mcp__github__pull_request_write",
        "mcp__plugin_engineering_github__merge_pull_request",
    ):
        assert _matches(matcher, tool), tool
    assert not _matches(matcher, "Bash")


@pytest.mark.parametrize(
    ("tool", "extra"),
    [
        ("mcp__github__merge_pr", {}),
        ("mcp__github__pull_request_merge", {}),
        ("mcp__github__pull_request_write", {"method": "merge"}),
    ],
    ids=["renamed", "reordered", "folded-into-a-write-tool"],
)
def test_a_merge_under_another_name_is_judged(
    tool: str, extra: dict[str, str], tmp_path: Path
) -> None:
    """A renamed merge tool is refused while admins are exempt, and passes once they are bound."""
    payload = json.dumps({"tool_name": tool, "tool_input": {**MERGE_INPUT, **extra}})
    reason = _refusal(_decision(payload, _github(tmp_path / "unbound", {"main": "non_admins"})))
    assert "`enforcement_level: non_admins`" in reason
    assert _decision(payload, _github(tmp_path / "bound", {"main": "everyone"})) is None


@pytest.mark.parametrize(
    ("tool", "arguments"),
    [
        ("mcp__github__enable_pr_auto_merge", {**MERGE_INPUT, "mergeMethod": "MERGE"}),
        ("mcp__github__disable_pr_auto_merge", MERGE_INPUT),
        ("mcp__github__update_pull_request_branch", MERGE_INPUT),
        ("mcp__github__pull_request_read", {**MERGE_INPUT, "method": "get"}),
        ("mcp__github__pull_request_review_write", {**MERGE_INPUT, "method": "create"}),
        ("mcp__github__list_commits", {"owner": OWNER, "repo": NAME}),
        ("mcp__hearthbot__post_message", {"text": "Reply Merge it if you agree."}),
    ],
    ids=["arm", "disarm", "update-branch", "read", "review", "no-pull-number", "thread-post"],
)
def test_a_call_that_is_not_a_merge_is_let_through_unread(
    tool: str, arguments: dict[str, object], tmp_path: Path
) -> None:
    """Every MCP call reaches the hook, so only a merge may be asked about or refused.

    No GitHub records are served here, so a call taken for a merge would be
    refused for want of an answer. Arming carries "merge" in its name and may
    ask for a merge commit, and still is not a merge.
    """
    payload = json.dumps({"tool_name": tool, "tool_input": arguments})
    assert _decision(payload, tmp_path) is None


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


def test_a_merge_in_another_repository_is_let_through_unread(tmp_path: Path) -> None:
    """A merge elsewhere cannot leave this repository's `main` stale, so it is not asked about.

    The corpus is served exempting admins, and this repository's `main` is too.
    The corpus merge passes, and this repository's merge is still refused.
    """
    api = _github(tmp_path, {"main": "non_admins"})
    _github(tmp_path, {"main": "non_admins"}, name=CORPUS)
    corpus = json.dumps({"tool_name": MERGE, "tool_input": {**MERGE_INPUT, "repo": CORPUS}})
    assert _decision(corpus, api) is None
    assert "`enforcement_level: non_admins`" in _refusal(_decision(MERGE_CALL, api))


@pytest.mark.parametrize(
    ("origin", "judged"),
    [
        (f"git@github.com:{OWNER.upper()}/{NAME}.git", NAME),
        (f"https://github.com/{OWNER}/{CORPUS}", CORPUS),
        ("/srv/mirrors/open-anesthesia-sim.git", CORPUS),
    ],
    ids=["same-repository-other-spelling", "corpus-checkout", "origin-not-on-github"],
)
def test_a_merge_in_this_repository_is_judged_by_its_own_origin(
    origin: str, judged: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Which repository is this one is read from `origin`, and an unreadable one judges every merge.

    GitHub ignores case in owner and repository names, so another spelling of
    this repository is still this repository. A checkout of the corpus would
    judge the corpus's merges. An `origin` that names no GitHub repository
    leaves the hook unable to tell, and it judges the corpus merge too.
    """
    monkeypatch.setenv("GIT_DIR", str(_git_dir(tmp_path / "checkout", origin)))
    api = _github(tmp_path / "api", {"main": "non_admins"}, name=judged)
    call = json.dumps({"tool_name": MERGE, "tool_input": {**MERGE_INPUT, "repo": judged}})
    assert "`enforcement_level: non_admins`" in _refusal(_decision(call, api))


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
    # Every MCP call reaches the hook, so a failed step must not block the rest.
    read = json.dumps({"tool_name": "mcp__github__pull_request_read", "tool_input": MERGE_INPUT})
    assert _decision(read, api, path=str(tools)) is None


def test_another_tool_is_let_through(tmp_path: Path) -> None:
    """Wired to the wrong matcher, the hook refuses nothing rather than everything."""
    payload = json.dumps({"tool_name": "mcp__github__enable_pr_auto_merge", "tool_input": {}})
    assert _decision(payload, tmp_path) is None


def test_a_payload_laid_out_across_lines_is_read_as_json(tmp_path: Path) -> None:
    """A name on the line after its key is the same member (RFC 8259 § 2), read as `json` reads it.

    Read by a sed a line at a time it was no name, so the call of another tool
    went on to the merge check and was refused (`PL-CXK6`).
    """
    laid_out = (
        '{\n  "session_id":\n    "abc-123",\n  "tool_name":\n    "Edit",\n'
        '  "tool_input": {"file_path": "x"}\n}\n'
    )
    assert _decision(laid_out, tmp_path) is None


@pytest.mark.parametrize(
    "payload",
    ['{"tool_input": {"pullNumber": 1224}, "note": "MERGE"}', "merge_pull_request, not json"],
    ids=["no-name", "not-json"],
)
def test_a_payload_naming_no_tool_that_mentions_a_merge_is_refused(
    payload: str, tmp_path: Path
) -> None:
    """Every call the script takes for a merge contains "merge", so an unjudged one fails closed."""
    _refusal(_decision(payload, _github(tmp_path, {"main": "everyone"})))


@pytest.mark.parametrize("payload", ["", "not json", "{}"], ids=["empty", "not-json", "no-name"])
def test_a_payload_naming_no_tool_and_no_merge_is_let_through(payload: str, tmp_path: Path) -> None:
    """Every MCP call reaches the hook, so it refuses an unjudged call only if it names a merge."""
    assert _decision(payload, _github(tmp_path, {"main": "everyone"})) is None
