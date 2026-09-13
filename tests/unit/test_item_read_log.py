"""Tests for `.claude/hooks/item_read_log.py` and `tools/item_reads.py`.

The hook runs after every Read, Grep and Glob a session makes, so two
properties matter more than what it records. It must never fail loudly - a hook
that errors interrupts the session it is measuring - and it must ignore
everything that is not an item, or the log becomes a transcript and the
measurement drowns.

The summariser's one non-obvious claim is edge traversal: a session reaching an
item it had already reached a citation to. That is the number the store's
design arguments have been assuming, so it is tested against a real pair of
items rather than a stub.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import item_read_log

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "item_read_log.py"


def payload(tool: str, session: str = "s1", **tool_input: str) -> str:
    return json.dumps({"session_id": session, "tool_name": tool, "tool_input": tool_input})


def run_hook(stdin: str, project: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=stdin,
        capture_output=True,
        text=True,
        env={"CLAUDE_PROJECT_DIR": str(project), "PATH": "/usr/bin:/bin"},
    )


def log_lines(project: Path) -> list[str]:
    log = project / item_read_log.LOG_NAME
    return log.read_text(encoding="utf-8").splitlines() if log.exists() else []


def test_reading_an_item_is_recorded(tmp_path: Path) -> None:
    result = run_hook(payload("Read", file_path="/repo/docs/items/PL-K7QX-a-thing.md"), tmp_path)
    assert result.returncode == 0
    assert len(log_lines(tmp_path)) == 1
    assert "PL-K7QX" in log_lines(tmp_path)[0]


def test_searching_for_an_id_is_recorded(tmp_path: Path) -> None:
    """A grep for an id is the traversal shape, and a path-only test would miss it."""
    run_hook(payload("Grep", pattern="PL-K7QX"), tmp_path)
    assert len(log_lines(tmp_path)) == 1


def test_reading_anything_else_is_not_recorded(tmp_path: Path) -> None:
    run_hook(payload("Read", file_path="/repo/src/anesthesia_sim/core/tissue.py"), tmp_path)
    run_hook(payload("Grep", pattern="def compute"), tmp_path)
    assert log_lines(tmp_path) == []


def test_malformed_input_is_silent(tmp_path: Path) -> None:
    for stdin in ("", "   ", "not json", "[]", '{"tool_name": 7}', "null"):
        result = run_hook(stdin, tmp_path)
        assert result.returncode == 0, stdin
        assert result.stderr == "", stdin
    assert log_lines(tmp_path) == []


def test_a_missing_session_id_still_records(tmp_path: Path) -> None:
    run_hook(
        json.dumps(
            {"tool_name": "Read", "tool_input": {"file_path": "/repo/docs/items/PL-K7QX-x.md"}}
        ),
        tmp_path,
    )
    assert "unknown" in log_lines(tmp_path)[0]


def test_a_tab_in_a_pattern_does_not_shift_the_columns(tmp_path: Path) -> None:
    run_hook(payload("Grep", pattern="PL-K7QX\tand\tmore"), tmp_path)
    assert len(log_lines(tmp_path)[0].split("\t")) == 4


def test_writing_stops_at_the_cap_rather_than_rotating(tmp_path: Path) -> None:
    """Truncating the front would destroy the sequence the traversal count needs."""
    log = tmp_path / item_read_log.LOG_NAME
    log.write_text("x" * (item_read_log.MAX_LOG_BYTES + 1), encoding="utf-8")
    before = log.stat().st_size
    run_hook(payload("Read", file_path="/repo/docs/items/PL-K7QX-x.md"), tmp_path)
    assert log.stat().st_size == before


def test_an_unwritable_log_does_not_fail_the_session(tmp_path: Path) -> None:
    (tmp_path / item_read_log.LOG_NAME).mkdir()
    result = run_hook(payload("Read", file_path="/repo/docs/items/PL-K7QX-x.md"), tmp_path)
    assert result.returncode == 0


def test_the_summariser_reports_nothing_when_no_log_exists() -> None:
    result = subprocess.run(
        [sys.executable, str(REPO / "tools" / "item_reads.py")],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0
    assert "No reads recorded yet" in result.stdout or "Sample:" in result.stdout


def test_the_summariser_counts_a_real_citation_edge(tmp_path: Path, monkeypatch, capsys) -> None:
    """Read an item, then reach an id it cites: one traversal."""
    import item_reads

    items = tmp_path / "docs" / "items"
    items.mkdir(parents=True)
    (items / "PL-AAAA-cites-another.md").write_text(
        "---\nid: PL-AAAA\nstatus: ready\n---\n\n**Problem.** See `PL-BBBB`.\n", encoding="utf-8"
    )
    (items / "PL-BBBB-the-cited-one.md").write_text(
        "---\nid: PL-BBBB\nstatus: done\n---\n\n**Problem.** Nothing.\n", encoding="utf-8"
    )
    log = tmp_path / ".docket-reads.log"
    log.write_text(
        "2026-09-13T00:00:00+00:00\ts1\tRead\tdocs/items/PL-AAAA-cites-another.md\n"
        "2026-09-13T00:00:01+00:00\ts1\tGrep\tPL-BBBB\n"
        "2026-09-13T00:00:02+00:00\ts2\tRead\tdocs/items/PL-BBBB-the-cited-one.md\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(item_reads, "LOG", log)
    monkeypatch.setattr(item_reads, "ITEMS", items)

    # In-process, deliberately: the module resolves LOG and ITEMS from its own
    # location, so a subprocess would re-resolve them to the real repository
    # and read the real store no matter what was patched here.
    assert item_reads.main() == 0
    out = capsys.readouterr().out
    assert "Citation edges traversed      1" in out
    assert "in 1 session" in out
    # s1 reached PL-BBBB having read PL-AAAA, which cites it; s2 reached one
    # item and traversed nothing.
    assert "Distinct items reached        2 of 2" in out
