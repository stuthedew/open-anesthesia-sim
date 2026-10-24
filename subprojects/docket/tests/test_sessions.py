"""Tests for the join from a closed item to the sessions that worked it (`PL-70M6`).

Each test builds a scratch repository with real git, because the join reads
the squash commit's message off the default branch, and runs `docket show`
end to end. The ledger rows are written here, so every expected value is the
fixture's, not one read back from the code under test.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from docket import sessions
from docket.cli import main
from docket.model import parse_item

LEDGER_HEADER = (
    "session_id\ttitle\tcreated_at\tupdated_at\tstatus\torigin\tparent_session_id\t"
    "configured_model\tcontext_model\tlast_served_model\tuser_switched_model\teffort_level\t"
    "input_tokens\toutput_tokens\tcache_read_tokens\tcache_write_tokens\tcost_usd\t"
    "context_used_tokens\trow_written"
)

#: A configured model that differs from the served one, and a title with a
#: bare double quote, which a CSV reader would take for the start of a field.
ROW_A = (
    'session_01AAAA\tPL-0001 "fix" it\t2026-10-01T00:00:00Z\t2026-10-01T01:00:00Z\tarchived\t'
    "web_claude_ai\t\tclaude-opus-5-5[1m]\tclaude-opus-5-5\tclaude-opus-5-5\t\thigh\t"
    "10\t20\t30\t40\t12.3456\t\t2026-10-19"
)

ROW_C = (
    "session_01CCCC\tOther work\t2026-10-01T00:00:00Z\t2026-10-01T01:00:00Z\tarchived\t"
    "desktop_app\t\tclaude-sonnet-5-5\tclaude-sonnet-5-5\tclaude-sonnet-5-5\t\tmedium\t"
    "1\t2\t3\t4\t0.5\t\t2026-10-19"
)


def _item(identifier: str, *, status: str = "done", pr: str | None = "12") -> str:
    closing = "closed: 2026-10-02\n" if status == "done" else ""
    number = f"pr: {pr}\n" if pr is not None else ""
    return (
        f"---\nid: {identifier}\ntitle: Work for {identifier}\npriority: P2\neffort: S\n"
        f"status: {status}\nclasses: infra\ntouches: a.py\nadded: 2026-10-01\n{closing}{number}"
        "---\n\n**Problem.** x\n"
    )


def _repo(tmp_path: Path, *items: str, ledger: str | None = None) -> Path:
    """A repository on `main` holding `items` under `docs/items`, and the ledger text if given."""
    root = tmp_path / "repo"
    store = root / "docs" / "items"
    store.mkdir(parents=True)
    (root / "docket.toml").write_text("[docket]\n", encoding="utf-8")
    for text in items:
        item = parse_item(text)
        (store / f"{item.identifier}-work.md").write_text(text, encoding="utf-8")
    if ledger is not None:
        (root / sessions.LEDGER_NAME).write_text(ledger, encoding="utf-8")
    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", "-q", str(root)],
        check=True,
        capture_output=True,
    )
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        _git(root, "config", name, value)
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base")
    return root


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def _squash(root: Path, message: str) -> None:
    """A commit on `main` with `message`, as a squash merge lands one."""
    (root / "a.py").write_text(message, encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", message)


def _show(root: Path, identifier: str, capsys: pytest.CaptureFixture[str]) -> str:
    items = str(root / "docs" / "items")
    assert main(["--items", items, "--today", "2026-10-20", "show", identifier]) == 0
    return capsys.readouterr().out


def test_show_prints_each_joined_session_and_names_one_the_ledger_lacks(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The joined case and the missing-row case, read from the squash commit's message.

    The trailer and the bare URL in the pull request body both name a session,
    and the second has no ledger row. It is listed as having none, not dropped.
    """
    root = _repo(tmp_path, _item("PL-0001"), ledger=f"{LEDGER_HEADER}\n{ROW_A}\n{ROW_C}\n")
    _squash(
        root,
        "PL-0001: do the work (#12)\n\nThe body.\nhttps://claude.ai/code/session_01BBBB\n\n"
        "Claude-Session: https://claude.ai/code/session_01AAAA\n",
    )

    out = _show(root, "PL-0001", capsys)

    section = out[out.index(sessions.SECTION_HEADING) :].splitlines()
    assert section[0].startswith(f"{sessions.SECTION_HEADING} (#12, read from squash commit ")
    assert section[0].endswith("; rows from docs/session-ledger.tsv):")
    assert section[1] == "  session_01BBBB · no row in docs/session-ledger.tsv"
    assert section[2] == (
        "  session_01AAAA · claude-opus-5-5 (configured claude-opus-5-5[1m]) · effort high · $12.35"
    )
    assert "session_01CCCC" not in out


def test_show_reads_the_body_record_when_the_squash_commit_names_no_session(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repo(tmp_path, _item("PL-0001"), ledger=f"{LEDGER_HEADER}\n{ROW_C}\n")
    records = root / "docs" / "pr-bodies"
    records.mkdir(parents=True)
    (records / "12.md").write_text(
        "---\npr: 12\n---\n\n_Generated by [Claude Code](https://claude.ai/code/session_01CCCC)_\n",
        encoding="utf-8",
    )
    _squash(root, "PL-0001: do the work (#12)")

    out = _show(root, "PL-0001", capsys)

    assert f"{sessions.SECTION_HEADING} (#12, read from docs/pr-bodies/12.md;" in out
    assert "  session_01CCCC · claude-sonnet-5-5 · effort medium · $0.50" in out


def test_show_says_why_no_session_joined_rather_than_printing_an_empty_list(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The unjoined cases: no `pr:`, and a pull request no commit or record names.

    A commit that mentions `(#12)` only in its body is not #12's squash commit,
    and `(#120)` is another pull request.
    """
    root = _repo(
        tmp_path, _item("PL-0001"), _item("PL-0002", pr=None), ledger=f"{LEDGER_HEADER}\n{ROW_A}\n"
    )
    _squash(
        root, "PL-0009: other work (#13)\n\nFollows (#12).\nhttps://claude.ai/code/session_01AAAA\n"
    )
    _squash(root, "PL-0010: more (#120)\n\nhttps://claude.ai/code/session_01AAAA\n")

    out = _show(root, "PL-0001", capsys)
    assert (
        f"{sessions.SECTION_HEADING}: none joined, because no squash commit on the default branch "
        "has a subject ending (#12), and there is no docs/pr-bodies/12.md."
    ) in out
    assert "session_01AAAA" not in out

    out = _show(root, "PL-0002", capsys)
    assert (
        f"{sessions.SECTION_HEADING}: none joined, because it has no `pr:`, "
        "so there is no pull request to join."
    ) in out


def test_show_says_the_ledger_was_not_read_rather_than_that_it_lacks_the_session(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repo(tmp_path, _item("PL-0001"))
    _squash(
        root, "PL-0001: do the work (#12)\n\nClaude-Session: https://claude.ai/code/session_01AAAA"
    )

    out = _show(root, "PL-0001", capsys)

    assert (
        "  session_01AAAA · ledger not read: "
        "docs/session-ledger.tsv does not exist in this checkout"
    ) in out


def test_show_prints_no_section_for_an_open_item(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repo(tmp_path, _item("PL-0001", status="ready", pr=None))

    assert sessions.SECTION_HEADING not in _show(root, "PL-0001", capsys)


def test_item_sessions_is_the_join_the_model_review_calls(tmp_path: Path) -> None:
    """The function, called directly, joins the item as `show` does, with one ledger read."""
    root = _repo(tmp_path, _item("PL-0001"), ledger=f"{LEDGER_HEADER}\n{ROW_A}\n")
    _squash(root, "PL-0001: do the work (#12)\n\nhttps://claude.ai/code/session_01AAAA")
    ledger = sessions.read_ledger(root)

    joined = sessions.item_sessions(parse_item(_item("PL-0001")), root, ledger=ledger)

    assert joined.pr == 12
    assert [(s.session_id, s.row) for s in joined.sessions] == [
        ("session_01AAAA", ledger.rows["session_01AAAA"])
    ]
    assert ledger.rows["session_01AAAA"].effort_level == "high"


def test_read_ledger_refuses_a_ledger_missing_a_column_it_reads(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / sessions.LEDGER_NAME).write_text("session_id\tcost_usd\n", encoding="utf-8")

    ledger = sessions.read_ledger(tmp_path)

    assert ledger.rows == {}
    assert ledger.declined == (
        "docs/session-ledger.tsv has no configured_model, last_served_model, effort_level column"
    )
