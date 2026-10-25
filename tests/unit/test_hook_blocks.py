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


def test_copy_writes_each_session_its_own_file_and_keeps_what_it_held(tmp_path: Path) -> None:
    log = _log(
        tmp_path / "log.tsv",
        "2026-10-25T10:00:00+00:00\tcse_a\tno-prune-guard\tprune",
        "2026-10-25T10:01:00+00:00\tcse_b\tpush-check-guard\tchecks-failed",
        "2026-10-25T10:02:00+00:00\t\towner_ask_guard\tbare-read-ask",
        "a line with too few fields",
    )
    held = tmp_path / BLOCKS_DIR / "cse_a.tsv"
    held.parent.mkdir(parents=True)
    held.write_text(f"{BLOCKS_HEADER}\n2026-10-24T09:00:00+00:00\tcse_a\tno-prune-guard\tremove\n")
    report = copy(log, tmp_path)
    assert len(report) == 3
    assert held.read_text(encoding="utf-8").split("\n") == [
        BLOCKS_HEADER,
        "2026-10-24T09:00:00+00:00\tcse_a\tno-prune-guard\tremove",
        "2026-10-25T10:00:00+00:00\tcse_a\tno-prune-guard\tprune",
        "",
    ]
    assert (tmp_path / BLOCKS_DIR / "no-session.tsv").is_file()
    # A second copy finds nothing new, and changes nothing.
    assert copy(log, tmp_path) == []


def test_a_session_id_that_is_not_a_file_name_is_reported_and_skipped(tmp_path: Path) -> None:
    log = _log(tmp_path / "log.tsv", "2026-10-25T10:00:00+00:00\t../x\tg\tr")
    (line,) = copy(log, tmp_path)
    assert "is not a file name" in line
    assert not (tmp_path / BLOCKS_DIR).exists()


def test_count_gives_refusals_and_sessions_per_guard_and_rule(tmp_path: Path) -> None:
    log = _log(
        tmp_path / "log.tsv",
        "2026-10-25T10:00:00+00:00\tcse_a\tno-prune-guard\tprune",
        "2026-10-25T10:05:00+00:00\tcse_a\tno-prune-guard\tprune",
        "2026-10-25T10:06:00+00:00\tcse_b\tno-prune-guard\tprune",
    )
    assert count(tmp_path) == [f"hook blocks: {BLOCKS_DIR} holds no refusals yet"]
    copy(log, tmp_path)
    assert count(tmp_path) == ["no-prune-guard\tprune\t3 refusals\t2 sessions"]


def test_the_missing_log_copies_nothing(tmp_path: Path) -> None:
    assert copy(tmp_path / "absent.tsv", tmp_path) == []


def test_record_runs_the_copy() -> None:
    """`docket.toml` names the copy as `record_command`, so `record` makes it."""
    from docket.config import load

    assert load(REPO).record_command == "python3 tools/hook_blocks.py copy"
