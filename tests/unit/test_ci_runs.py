"""Tests for `tools/ci_runs.py`, which keeps the CI run history past GitHub's 90 days.

The model review scores an item partly by the red CI runs on its pull request,
so the history must outlive GitHub's retention (`PL-4SFQ`).
"""

from __future__ import annotations

import importlib.util
from datetime import date
from pathlib import Path
from types import ModuleType

import pytest

TOOL = Path(__file__).resolve().parents[2] / "tools" / "ci_runs.py"


def _tool() -> ModuleType:
    spec = importlib.util.spec_from_file_location("ci_runs", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CI_RUNS = _tool()


def _run(run_id: int, day: str, **fields: object) -> dict[str, object]:
    """One run as GitHub's listing describes it, created at noon on `day`."""

    run: dict[str, object] = {
        "id": run_id,
        "name": "quality",
        "run_number": run_id,
        "run_attempt": 1,
        "event": "pull_request",
        "head_branch": "claude/x",
        "head_sha": "a" * 40,
        "pull_requests": [{"number": 7}],
        "status": "completed",
        "conclusion": "success",
        "created_at": f"{day}T12:00:00Z",
        "updated_at": f"{day}T12:05:00Z",
    }
    run.update(fields)
    return run


def _reader(runs: list[dict[str, object]], page: int = 100):
    """A stand-in for GitHub's run listing that answers from `runs`, `page` runs at a time."""

    asked: list[dict[str, str | int]] = []

    def read(query: dict[str, str | int]) -> dict[str, object]:
        asked.append(query)
        day = [run for run in runs if str(run["created_at"]).startswith(str(query["created"]))]
        start = (int(query["page"]) - 1) * page
        return {"total_count": len(day), "workflow_runs": day[start : start + page]}

    read.asked = asked  # type: ignore[attr-defined]
    return read


def test_a_refresh_adds_each_finished_run_from_the_day_before_the_newest_row() -> None:
    """A run in progress waits for a later refresh, and earlier days are not asked again."""

    rows = [CI_RUNS.row_of(_run(1, "2026-10-20"))]
    runs = [
        _run(1, "2026-10-20"),
        _run(2, "2026-10-21"),
        _run(3, "2026-10-22", status="in_progress", conclusion=None),
    ]
    read = _reader(runs)

    fresh, added, updated = CI_RUNS.refresh(rows, read, date(2026, 10, 22))

    assert sorted(row["run_id"] for row in fresh) == ["1", "2"]
    assert (added, updated) == (1, 0)
    assert [query["created"] for query in read.asked] == [
        "2026-10-19",
        "2026-10-20",
        "2026-10-21",
        "2026-10-22",
    ]


def test_a_later_attempt_replaces_its_row_but_never_drops_a_known_pull_request() -> None:
    """GitHub unlinks a run from its pull request once the branch is deleted."""

    rows = [CI_RUNS.row_of(_run(1, "2026-10-20", conclusion="failure"))]
    rerun = _run(1, "2026-10-20", run_attempt=2, pull_requests=[])

    fresh, added, updated = CI_RUNS.refresh(rows, _reader([rerun]), date(2026, 10, 20))

    assert (added, updated) == (0, 1)
    assert fresh[0]["attempt"] == "2"
    assert fresh[0]["conclusion"] == "success"
    assert fresh[0]["pull_requests"] == "7"


def test_a_row_github_no_longer_lists_is_kept() -> None:
    rows = [CI_RUNS.row_of(_run(1, "2026-10-20")), CI_RUNS.row_of(_run(9, "2026-08-01"))]

    fresh, _, _ = CI_RUNS.refresh(rows, _reader([]), date(2026, 10, 20))

    assert sorted(row["run_id"] for row in fresh) == ["1", "9"]


def test_a_day_is_read_a_page_at_a_time_to_its_short_page() -> None:
    runs = [_run(index, "2026-10-20") for index in range(1, 151)]
    read = _reader(runs, page=CI_RUNS.PAGE)

    assert len(CI_RUNS.runs_on(date(2026, 10, 20), read)) == 150
    assert [query["page"] for query in read.asked] == [1, 2]


def test_a_day_at_the_listing_cap_is_refused_rather_than_read_short() -> None:
    def full(query: dict[str, str | int]) -> dict[str, object]:
        return {"total_count": CI_RUNS.LISTING_CAP, "workflow_runs": []}

    with pytest.raises(CI_RUNS.RefreshFailed, match="at most 1000"):
        CI_RUNS.runs_on(date(2026, 10, 20), full)


def test_the_file_round_trips_in_creation_order(tmp_path: Path) -> None:
    path = tmp_path / "ci-runs.tsv"
    rows = [CI_RUNS.row_of(_run(2, "2026-10-21")), CI_RUNS.row_of(_run(1, "2026-10-20"))]

    CI_RUNS.write_rows(path, rows)

    assert path.read_text(encoding="utf-8").splitlines()[0].split("\t") == list(CI_RUNS.COLUMNS)
    assert [row["run_id"] for row in CI_RUNS.read_rows(path)] == ["1", "2"]


def test_a_file_with_other_columns_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "ci-runs.tsv"
    path.write_text("run_id\tsomething\n1\tx\n", encoding="utf-8")

    with pytest.raises(CI_RUNS.RefreshFailed, match="does not have the columns"):
        CI_RUNS.read_rows(path)


def test_the_real_file_has_the_columns_the_tool_writes() -> None:
    assert CI_RUNS.read_rows(CI_RUNS.RUNS)
