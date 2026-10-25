"""The guards' refusal log, and `tools/hook_blocks.py`, which copies and counts it (`PL-SG93`).

The direction that matters is a refusal that is not counted. A guard that
refuses without logging, or a copy that drops a session's lines, would make a
guard look as if it blocked nothing, and that is the reading that retires it.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
from hook_blocks import BLOCKS_DIR, BLOCKS_HEADER, copy, count

REPO = Path(__file__).resolve().parents[2]
HOOKS = REPO / ".claude" / "hooks"


def _log(path: Path, *lines: str) -> Path:
    path.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")
    return path


def test_a_refusing_guard_logs_its_name_rule_and_session(tmp_path: Path) -> None:
    log = tmp_path / "blocks.tsv"
    payload = json.dumps(
        {
            "session_id": "cse_abc",
            "tool_name": "Bash",
            "tool_input": {"command": "python3 -m compileall src/"},
        }
    )
    result = subprocess.run(
        ["bash", str(HOOKS / "floor-interpreter-guard.sh")],
        input=payload.encode(),
        capture_output=True,
        timeout=20,
        check=False,
        env={**os.environ, "HOOK_BLOCK_LOG": str(log)},
    )
    decision = json.loads(result.stdout)["hookSpecificOutput"]
    assert decision["permissionDecision"] == "deny"
    (line,) = log.read_text(encoding="utf-8").split("\n")[:-1]
    _, session, guard, rule = line.split("\t")
    assert (session, guard, rule) == ("cse_abc", "floor-interpreter-guard", "floor-interpreter")
    assert "compileall" not in line


def test_the_pull_request_email_guard_logs_its_refusal(tmp_path: Path) -> None:
    """`pr-body-email-guard.sh` refuses through `tools/pr_body_check.py --screen`,
    which built its own refusal and so logged nothing (`PL-HHKC`)."""
    log = tmp_path / "blocks.tsv"
    payload = json.dumps(
        {
            "session_id": "cse_abc",
            "tool_name": "mcp__github__create_pull_request",
            "tool_input": {"title": "t", "body": "Asked by a.person@example.org."},
        }
    )
    result = subprocess.run(
        ["bash", str(HOOKS / "pr-body-email-guard.sh")],
        input=payload.encode(),
        capture_output=True,
        timeout=20,
        check=False,
        env={**os.environ, "HOOK_BLOCK_LOG": str(log)},
    )
    decision = json.loads(result.stdout)["hookSpecificOutput"]
    assert decision["permissionDecision"] == "deny"
    (line,) = log.read_text(encoding="utf-8").split("\n")[:-1]
    _, session, guard, rule = line.split("\t")
    assert (session, guard, rule) == ("cse_abc", "pr-body-email-guard", "email-address")
    assert "example.org" not in line


def test_every_python_refusal_is_built_by_deny() -> None:
    """A refusal built anywhere but `hook_input.deny` is a refusal the log never
    counts, which is how `PL-HHKC` went unseen. The shell guards' fallbacks for
    a missing python3 cannot reach `deny` and are not read here."""
    found = [
        path.relative_to(REPO).as_posix()
        for tree in (HOOKS, REPO / "tools")
        for path in sorted(tree.glob("*.py"))
        if path.name != "hook_input.py"
        and '"permissionDecision"' in path.read_text(encoding="utf-8")
    ]

    assert found == []


def test_a_log_that_cannot_be_written_still_refuses(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import hook_input

    blocker = tmp_path / "a-file"
    blocker.write_text("", encoding="utf-8")
    monkeypatch.setenv("HOOK_BLOCK_LOG", str(blocker / "under-a-file.tsv"))
    out = json.loads(hook_input.deny("g", "r", "Refused.", "{}"))
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert out["hookSpecificOutput"]["permissionDecisionReason"] == "Refused."


def test_copy_writes_only_what_the_repository_lacks_into_the_branch_s_file(tmp_path: Path) -> None:
    log = _log(
        tmp_path / "log.tsv",
        "2026-10-24T09:00:00.000001+00:00\tcse_a\tno-prune-guard\tremove",
        "2026-10-25T10:00:00.000001+00:00\tcse_a\tno-prune-guard\tprune",
        "2026-10-25T10:01:00.000001+00:00\tcse_b\tpush-check-guard\tchecks-failed",
        "2026-10-25T10:02:00.000001+00:00\t\towner_ask_guard\tbare-read-ask",
        "a line with too few fields",
    )
    # Another branch's file, already merged, holds the first line.
    other = tmp_path / BLOCKS_DIR / "claude-other.tsv"
    other.parent.mkdir(parents=True)
    other.write_text(
        f"{BLOCKS_HEADER}\n2026-10-24T09:00:00.000001+00:00\tcse_a\tno-prune-guard\tremove\n"
    )
    (line,) = copy(log, tmp_path, "claude/pl-b7k2-x")
    assert line == f"hook blocks: copied 2 refusals into {BLOCKS_DIR}/claude-pl-b7k2-x.tsv"
    mine = tmp_path / BLOCKS_DIR / "claude-pl-b7k2-x.tsv"
    assert mine.read_text(encoding="utf-8").split("\n") == [
        BLOCKS_HEADER,
        "2026-10-25T10:00:00.000001+00:00\tcse_a\tno-prune-guard\tprune",
        "2026-10-25T10:01:00.000001+00:00\tcse_b\tpush-check-guard\tchecks-failed",
        "",
    ]
    # The other branch's file is left as it was, and a second copy finds nothing new.
    assert len(other.read_text(encoding="utf-8").split("\n")) == 3
    assert copy(log, tmp_path, "claude/pl-b7k2-x") == []


def test_a_detached_head_copies_nothing_and_says_so(tmp_path: Path) -> None:
    log = _log(tmp_path / "log.tsv", "2026-10-25T10:00:00.000001+00:00\tcse_a\tg\tr")
    (line,) = copy(log, tmp_path, "")
    assert "on no branch" in line
    assert not (tmp_path / BLOCKS_DIR).exists()


def test_a_guard_run_by_hand_is_not_logged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A payload with no session id is a probe, and counting it would inflate the guard."""
    import hook_input

    log = tmp_path / "blocks.tsv"
    monkeypatch.setenv("HOOK_BLOCK_LOG", str(log))
    out = json.loads(hook_input.deny("g", "r", "Refused.", '{"tool_name": "Bash"}'))
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert not log.exists()


def test_two_refusals_in_one_second_stay_two_lines(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import hook_input

    log = tmp_path / "blocks.tsv"
    monkeypatch.setenv("HOOK_BLOCK_LOG", str(log))
    for _ in range(2):
        hook_input.deny("g", "r", "Refused.", '{"session_id": "cse_a"}')
    assert len(set(log.read_text(encoding="utf-8").split("\n")[:-1])) == 2
    copy(log, tmp_path, "b")
    assert count(tmp_path) == ["g\tr\t2 refusals\t1 sessions"]


def test_count_gives_refusals_and_sessions_per_guard_and_rule(tmp_path: Path) -> None:
    log = _log(
        tmp_path / "log.tsv",
        "2026-10-25T10:00:00+00:00\tcse_a\tno-prune-guard\tprune",
        "2026-10-25T10:05:00+00:00\tcse_a\tno-prune-guard\tprune",
        "2026-10-25T10:06:00+00:00\tcse_b\tno-prune-guard\tprune",
    )
    assert count(tmp_path) == [f"hook blocks: {BLOCKS_DIR} holds no refusals yet"]
    copy(log, tmp_path, "b")
    # A line another branch's file also holds is the same refusal, counted once.
    (tmp_path / BLOCKS_DIR / "c.tsv").write_text(
        f"{BLOCKS_HEADER}\n2026-10-25T10:00:00+00:00\tcse_a\tno-prune-guard\tprune\n"
    )
    assert count(tmp_path) == ["no-prune-guard\tprune\t3 refusals\t2 sessions"]


def test_the_missing_log_copies_nothing(tmp_path: Path) -> None:
    assert copy(tmp_path / "absent.tsv", tmp_path, "b") == []


def test_record_runs_the_copy() -> None:
    """`docket.toml` names the copy as `record_command`, so `record` makes it."""
    from docket.config import load

    assert load(REPO).record_command == "python3 tools/hook_blocks.py copy"
