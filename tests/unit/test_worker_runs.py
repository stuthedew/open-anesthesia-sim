"""Tests for `tools/worker_runs.py`, the repository's record of each headless worker run.

The runner's own test, in `test_headless_worker.py`, commits a record from a
fake run. These pin the format's refusals and the review command, which is what
keeps a worker's branch from merging before its review is written (`PL-87BR`).
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from worker_runs import RECORDS_DIR, check, main, review, write

RUN = {
    "item": "PL-B7K2",
    "model": "claude-opus-5-5",
    "effort": "high",
    "branch": "claude/pl-b7k2-worker",
    "started": "2026-10-19T19:17:44.512000+00:00",
    "finished": "2026-10-19T19:41:02+00:00",
    "exit_code": 0,
    "cost_usd": 2.1,
    "is_error": False,
    "subtype": "success",
    "turns": 45,
    "denials": 0,
    "reason": None,
    "input_tokens": 40,
    "cache_read_tokens": 9000,
    "cache_write_tokens": 700,
    "output_tokens": 1200,
}


def test_a_written_record_is_named_for_its_run_and_fails_the_check_until_reviewed(
    tmp_path: Path,
) -> None:
    path = write(tmp_path, RUN)
    assert path == tmp_path / RECORDS_DIR / "pl-b7k2-worker-20261019T191744.json"
    count, found = check(tmp_path)
    assert count == 1
    assert len(found) == 1
    assert "has no review" in found[0]
    review(path, "fixed", "Two missing workflow_paths entries,\n added.", date(2026, 10, 19))
    assert check(tmp_path) == (1, [])
    written = json.loads(path.read_text(encoding="utf-8"))["review"]
    assert written == {
        "outcome": "fixed",
        "note": "Two missing workflow_paths entries, added.",
        "reviewed": "2026-10-19",
    }


def test_a_record_is_reviewed_once(tmp_path: Path) -> None:
    path = write(tmp_path, RUN)
    review(path, "accepted", "Merged as left.", date(2026, 10, 19))
    with pytest.raises(ValueError, match="already has a review"):
        review(path, "sent-back", "Changed my mind.", date(2026, 10, 20))


@pytest.mark.parametrize(
    ("change", "problem"),
    [
        ({"turns": True}, "turns is true, not a whole number or null"),
        ({"cost_usd": "2.10"}, 'cost_usd is "2.10"'),
        ({"branch": "pl-b7k2-worker"}, "does not start with claude/"),
        ({"finished": "2026-10-19T19:41:02"}, "not an ISO 8601 time with its UTC offset"),
        ({"clone": "/Users/x/workers/run"}, "fields the format does not have: clone"),
    ],
    ids=["bool-for-int", "text-for-number", "branch", "offsetless-time", "extra-field"],
)
def test_a_malformed_run_field_is_refused_by_the_writer_and_the_check(
    tmp_path: Path, change: dict[str, object], problem: str
) -> None:
    with pytest.raises(ValueError, match="not a run record"):
        write(tmp_path, {**RUN, **change})
    path = write(tmp_path, RUN)
    review(path, "accepted", "Merged as left.", date(2026, 10, 19))
    record = json.loads(path.read_text(encoding="utf-8"))
    path.write_text(json.dumps({**record, **change}), encoding="utf-8")
    [found] = check(tmp_path)[1]
    assert problem in found


@pytest.mark.parametrize(
    ("written", "problem"),
    [
        ({"outcome": "merged", "note": "x", "reviewed": "2026-10-19"}, "is not one of"),
        ({"outcome": "fixed", "note": " ", "reviewed": "2026-10-19"}, "one line of text"),
        ({"outcome": "fixed", "note": "x", "reviewed": "19 Oct"}, "is not YYYY-MM-DD"),
        ({"outcome": "fixed"}, "must hold exactly"),
    ],
    ids=["outcome", "blank-note", "date", "missing-fields"],
)
def test_a_malformed_review_is_refused(
    tmp_path: Path, written: dict[str, object], problem: str
) -> None:
    path = write(tmp_path, RUN)
    record = json.loads(path.read_text(encoding="utf-8"))
    path.write_text(json.dumps({**record, "review": written}), encoding="utf-8")
    [found] = check(tmp_path)[1]
    assert problem in found


def test_a_renamed_record_or_a_stray_file_is_refused(tmp_path: Path) -> None:
    path = write(tmp_path, RUN)
    review(path, "accepted", "Merged as left.", date(2026, 10, 19))
    path.rename(path.with_name("pl-b7k2.json"))
    (path.parent / "notes.md").write_text("x", encoding="utf-8")
    (path.parent / "README.md").write_text("What the records are.", encoding="utf-8")
    (path.parent / "broken.json").write_text("{", encoding="utf-8")
    found = check(tmp_path)[1]
    assert [line.split(": ", 1)[0].rsplit("/", 1)[1] for line in found] == [
        "broken.json",
        "notes.md",
        "pl-b7k2.json",
    ]
    assert "should be named pl-b7k2-worker-20261019T191744.json" in found[2]


def test_the_check_command_fails_on_an_unreviewed_record_and_passes_on_none(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["check"], root=tmp_path) == 0
    assert "0 record(s)" in capsys.readouterr().out
    path = write(tmp_path, RUN)
    assert main(["check"], root=tmp_path) == 1
    assert "has no review" in capsys.readouterr().err
    assert main(["review", str(path), "--outcome", "accepted", "--note", "Fine."]) == 0
    assert main(["check"], root=tmp_path) == 0
