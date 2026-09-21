"""Tests for `tools/context_reading.py`, the live read of a session's own context.

Five defects are pinned here, and each is one this script would otherwise have
shipped with, because each arises from the transcript's real shape rather than
from a hypothetical one.

Three would *inflate* the reading and so would make a session hand off early,
which is the failure with no symptom - the work simply does not get done and
nothing says why. The harness writes one assistant record per content block and
they all repeat the same `requestId` and the same usage, so counting records
instead of requests triples a normal turn. A subagent's records are marked
`isSidechain`, and counting them charges this session for context that was
never in its window - the specific thing `CLAUDE.md` recommends subagents *for*.
A tool result arrives as a `user` record, so counting user records as turns
reports a turn per tool call.

The other two are the apparatus standard's floor rather than arithmetic:
what this prints has to be true or has to say what it could not read. A record
that will not parse, or an assistant record with no usage block, is excluded
and counted back on an `unread` line - dropping it silently would hand over a
partial reading as a complete one. And a missing transcript exits non-zero:
zero context is a reading a session would act on, and "I could not find the
file" is not that.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parents[2] / "tools" / "context_reading.py"

sys.path.insert(0, str(TOOL.parent))

import context_reading  # noqa: E402


def assistant(request_id: str, context: int, *, sidechain: bool = False) -> str:
    """One assistant record, billed `context` tokens spread over the usage fields."""
    row = {
        "type": "assistant",
        "requestId": request_id,
        "timestamp": "2026-09-21T03:07:11.000Z",
        "message": {
            "usage": {
                "input_tokens": 2,
                "cache_read_input_tokens": context - 2 - 100,
                "cache_creation_input_tokens": 100,
                "output_tokens": 50,
            }
        },
    }
    if sidechain:
        row["isSidechain"] = True
    return json.dumps(row)


def user(text: str = "hello", *, tool_result: bool = False) -> str:
    row: dict[str, object] = {"type": "user", "message": {"content": text}}
    if tool_result:
        row["toolUseResult"] = {"stdout": "ok"}
    return json.dumps(row)


def test_repeated_request_id_is_one_request_not_three() -> None:
    """The harness writes a record per content block; they are one request."""
    reading = context_reading.read(
        "\n".join(
            [
                user(),
                assistant("req_1", 81_048),
                assistant("req_1", 81_048),
                assistant("req_1", 81_048),
                assistant("req_2", 88_100),
            ]
        )
    )

    assert len(reading.requests) == 2
    assert reading.baseline == 81_048
    assert reading.context == 88_100
    assert reading.spend == 7_052


def test_subagent_records_are_not_this_session_s_context() -> None:
    """A sidechain transcript never entered this window, so it is not spend."""
    reading = context_reading.read(
        "\n".join(
            [
                user(),
                assistant("req_1", 81_048),
                assistant("side_1", 400_000, sidechain=True),
                assistant("req_2", 88_100),
            ]
        )
    )

    assert [request.context for request in reading.requests] == [81_048, 88_100]
    assert reading.spend == 7_052


def test_tool_results_do_not_count_as_turns() -> None:
    """A whole item worked in one turn reports one turn, however many tools ran."""
    reading = context_reading.read(
        "\n".join(
            [
                user(),
                assistant("req_1", 81_048),
                user(tool_result=True),
                assistant("req_2", 84_856),
                user(tool_result=True),
                assistant("req_3", 88_100),
            ]
        )
    )

    assert reading.turns == 1
    assert len(reading.requests) == 3


def test_unreadable_records_are_counted_back_not_dropped() -> None:
    """A partial read must not leave here dressed as a complete one."""
    reading = context_reading.read(
        "\n".join(
            [
                user(),
                assistant("req_1", 81_048),
                "{not json at all",
                json.dumps({"type": "assistant", "requestId": "req_x", "message": {}}),
                assistant("req_2", 88_100),
            ]
        )
    )

    assert reading.unread == 2
    assert reading.spend == 7_052
    assert any("unread" in line for line in context_reading.report(reading))


def test_a_comfortable_reading_says_nothing_about_unread() -> None:
    """The unread line is a real finding, so it must not fire on every run."""
    reading = context_reading.read("\n".join([user(), assistant("req_1", 81_048)]))

    assert reading.unread == 0
    assert not any("unread" in line for line in context_reading.report(reading))


@pytest.mark.parametrize(
    ("session_id", "make_transcript"),
    [("sess_missing", False), ("", False)],
    ids=["no-transcript", "no-session-id"],
)
def test_a_missing_reading_exits_non_zero_rather_than_reporting_zero(
    tmp_path: Path, session_id: str, make_transcript: bool
) -> None:
    """Zero context is a reading a session would act on; not finding the file is not."""
    (tmp_path / "projects" / "-some-repo").mkdir(parents=True)

    result = subprocess.run(
        [sys.executable, str(TOOL)],
        capture_output=True,
        text=True,
        env={
            "PATH": "/usr/bin:/bin",
            "HOME": str(tmp_path),
            "CLAUDE_CONFIG_DIR": str(tmp_path),
            "CLAUDE_CODE_SESSION_ID": session_id,
        },
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert "No reading was taken" in result.stderr


def test_it_reads_a_transcript_it_is_pointed_at(tmp_path: Path) -> None:
    """End to end: the session id locates the file, whatever the directory is called."""
    project = tmp_path / "projects" / "-home-user-open-anesthesia-sim"
    project.mkdir(parents=True)
    (project / "sess_abc.jsonl").write_text(
        "\n".join([user(), assistant("req_1", 81_048), assistant("req_2", 112_857)]),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(TOOL), "--json"],
        capture_output=True,
        text=True,
        env={
            "PATH": "/usr/bin:/bin",
            "HOME": str(tmp_path),
            "CLAUDE_CONFIG_DIR": str(tmp_path),
            "CLAUDE_CODE_SESSION_ID": "sess_abc",
        },
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {
        "session_id": "sess_abc",
        "transcript": str(project / "sess_abc.jsonl"),
        "context": 112_857,
        "baseline": 81_048,
        "spend": 31_809,
        "turns": 1,
        "requests": 2,
        "unread": 0,
    }
