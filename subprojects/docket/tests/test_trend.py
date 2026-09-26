"""Tests for the workflow-to-product trend.

The rule under test is that the report answers with the same boundary
`Item.lane` answers with, and that it never turns three measures into one.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from docket.cli import main
from docket.config import Config
from docket.model import Item
from docket.render import format_trend
from docket.trend import (
    APPARATUS,
    BY_DAY,
    BY_WEEK,
    CHURN_NOT_ASKED,
    CHURN_READ,
    QUEUE,
    ROADMAP,
    SIM_CODE,
    SIM_DOCS,
    analyze,
    bucket,
)
from docket.vcs import Churn, Runner, _numstat_path, churn

ROOT = Path("/repo")

CONFIG = Config(
    items_dir="docs/items",
    workflow_paths=("tools", ".claude", "docs/items", "Makefile"),
    code_paths=("src", "tests"),
    roadmap_file="ROADMAP.md",
)


def _item(
    identifier: str,
    *,
    touches: tuple[str, ...] = ("src/core.py",),
    effort: str = "S",
    status: str = "done",
    closed: date | None = date(2026, 8, 25),
    priority: str = "P2",
) -> Item:
    return Item(
        identifier=identifier,
        title=f"Item {identifier}",
        priority=priority,
        effort=effort,
        status=status,
        classes=("perf",),
        touches=touches,
        blocked_by=(),
        feature="",
        milestone="",
        added=date(2026, 8, 20),
        closed=closed,
        commit="",
        reason="",
        body="**Problem.** x\n**Why it matters.** y\n**Done when.** z\n",
    )


# --- which half a changed file sits in ---------------------------------------


def test_the_queue_store_is_its_own_bucket_though_it_is_inside_workflow_paths() -> None:
    """The distinction the churn column depends on being able to make.

    `docs/items` is declared apparatus and belongs there, but it is also
    written by every session that captures a finding while doing something
    else. Counted as apparatus, a product session reads as a workflow one.
    """
    assert bucket("docs/items/PL-K7QX-a-thing.md", CONFIG) == QUEUE
    assert bucket("tools/doc_check.py", CONFIG) == APPARATUS


def test_the_roadmap_is_product_though_it_is_documentation() -> None:
    """Product *direction* is product work, which is why it is not in workflow_paths."""
    assert bucket("ROADMAP.md", CONFIG) == ROADMAP
    assert bucket("docs/releases/v0.3.0.md", CONFIG) == ROADMAP


def test_code_and_prose_are_separated_within_the_product_half() -> None:
    assert bucket("src/anesthesia_sim/core/tissue.py", CONFIG) == SIM_CODE
    assert bucket("tests/unit/test_tissue.py", CONFIG) == SIM_CODE
    assert bucket("docs/MODEL.md", CONFIG) == SIM_DOCS


def test_an_undeclared_path_is_product_prose_rather_than_apparatus() -> None:
    """The remainder falls to the product side, which is the fail-safe direction.

    An unrecognized path counted as apparatus would let the apparatus grow
    without the report showing it. Counted as product it can only understate
    the apparatus, which is the error a reader can catch.
    """
    assert bucket("uv.lock", Config(workflow_paths=("tools",))) == SIM_DOCS


# --- reading the history -----------------------------------------------------


def _runner(output: str) -> tuple[Runner, list[list[str]]]:
    """A git that answers with `output`, and the argument lists it was asked."""
    asked: list[list[str]] = []

    def run(args: list[str], root: Path) -> str:
        asked.append(args)
        return output

    return run, asked


def test_churn_sums_additions_and_deletions_by_day() -> None:
    run, _ = _runner(
        "\x012026-08-25\n10\t2\tsrc/core.py\n1\t1\ttools/x.py\n\x012026-08-26\n5\t0\tsrc/core.py\n"
    )
    report = churn(ROOT, runner=run)

    assert report.by_day[date(2026, 8, 25)] == {"src/core.py": 12, "tools/x.py": 2}
    assert report.by_day[date(2026, 8, 26)] == {"src/core.py": 5}


def test_churn_excludes_merges_so_a_merged_change_is_not_counted_twice() -> None:
    """A merge's numstat repeats its branch's lines; here every change is merged."""
    run, asked = _runner("")
    churn(ROOT, runner=run)

    assert "--no-merges" in asked[0]


def test_a_binary_file_is_skipped_rather_than_counted_as_zero() -> None:
    run, _ = _runner("\x012026-08-25\n-\t-\tassets/logo.png\n3\t1\tsrc/core.py\n")

    assert churn(ROOT, runner=run).by_day[date(2026, 8, 25)] == {"src/core.py": 4}


def test_a_checkout_that_cannot_run_git_reports_nothing_rather_than_failing() -> None:
    assert not churn(ROOT, runner=_runner("")[0])


def test_a_renamed_path_is_read_as_the_name_it_now_has() -> None:
    """Both notations git writes, neither of which is a prefix of the new path."""
    assert _numstat_path("old.py => new.py") == "new.py"
    assert _numstat_path("docs/{old.md => new.md}") == "docs/new.md"
    assert _numstat_path("{tools => .claude/hooks}/patch.py") == ".claude/hooks/patch.py"
    assert _numstat_path("src/core.py") == "src/core.py"


def test_a_move_into_a_directory_does_not_leave_a_doubled_separator() -> None:
    """`{ => sub}` names an empty original, which would otherwise join to `a//b`."""
    assert _numstat_path("docs/{ => sub}/x.md") == "docs/sub/x.md"


# --- the report --------------------------------------------------------------


def test_closures_are_counted_in_the_lane_their_touches_place_them() -> None:
    report = analyze(
        [
            _item("PL-0001", touches=("src/core.py",)),
            _item("PL-0002", touches=("tools/x.py",)),
            _item("PL-0003", touches=("tools/x.py", "src/core.py")),
            _item("PL-0004", touches=()),
        ],
        Churn(),
        CONFIG,
        today=date(2026, 8, 27),
    )

    assert report.periods[0].closed == {"product": 1, "workflow": 1, "crossing": 1, "unplaced": 1}


def test_the_share_counts_only_what_a_lane_could_place() -> None:
    """Crossing and unplaced work is reported and never folded into a side."""
    period = analyze(
        [
            _item("PL-0001", touches=("src/core.py",)),
            _item("PL-0002", touches=("tools/x.py",)),
            _item("PL-0003", touches=("tools/x.py", "src/core.py")),
        ],
        Churn(),
        CONFIG,
        today=date(2026, 8, 27),
    ).periods[0]

    assert period.closed_share == 0.5


def test_a_period_with_nothing_in_it_has_no_share_rather_than_zero_percent() -> None:
    """`0%` would read as a period of pure product work."""
    period = analyze(
        [_item("PL-0001", status="ready", closed=None)],
        Churn({date(2026, 8, 25): {"src/core.py": 4}}),
        CONFIG,
        today=date(2026, 8, 27),
    ).periods[0]

    assert period.closed_share is None


def test_bigger_items_weigh_more_than_the_count_of_them() -> None:
    """The correction item counts need: apparatus work arrives in smaller pieces."""
    period = analyze(
        [
            _item("PL-0001", touches=("src/core.py",), effort="M"),
            _item("PL-0002", touches=("tools/x.py",), effort="S"),
            _item("PL-0003", touches=("tools/y.py",), effort="S"),
        ],
        Churn(),
        CONFIG,
        today=date(2026, 8, 27),
    ).periods[0]

    assert period.closed_share == 2 / 3
    assert period.weighted == {"product": 3, "workflow": 2}
    assert period.weighted_share == 0.4


def test_an_unsized_item_counts_as_the_smallest_thing_it_could_be() -> None:
    period = analyze(
        [_item("PL-0001", touches=("tools/x.py",), effort="")],
        Churn(),
        CONFIG,
        today=date(2026, 8, 27),
    ).periods[0]

    assert period.weighted == {"workflow": 1}


def test_the_queue_store_is_left_out_of_the_churn_share() -> None:
    period = analyze(
        [],
        Churn(
            {
                date(2026, 8, 25): {
                    "docs/items/PL-K7QX-x.md": 900,
                    "tools/x.py": 10,
                    "src/core.py": 30,
                }
            }
        ),
        CONFIG,
        today=date(2026, 8, 27),
    ).periods[0]

    assert period.churn == {QUEUE: 900, APPARATUS: 10, SIM_CODE: 30}
    assert period.apparatus_lines == 10
    assert period.product_lines == 30
    assert period.churn_share == 0.25


def test_periods_are_anchored_at_the_first_day_rather_than_counted_back() -> None:
    """Two runs a day apart must agree about what happened in August."""
    report = analyze(
        [_item("PL-0001", closed=date(2026, 8, 21))],
        Churn({date(2026, 8, 21): {"src/core.py": 1}}),
        CONFIG,
        by=BY_WEEK,
        today=date(2026, 9, 7),
    )

    assert [p.label for p in report.periods] == ["2026-08-21..08-27"]


def test_an_empty_period_is_dropped_rather_than_printed_as_a_row_of_zeroes() -> None:
    report = analyze(
        [_item("PL-0001", closed=date(2026, 8, 21))],
        Churn({date(2026, 9, 5): {"src/core.py": 1}}),
        CONFIG,
        by=BY_WEEK,
        today=date(2026, 9, 7),
    )

    assert [p.label for p in report.periods] == ["2026-08-21..08-27", "2026-09-04..09-07"]


def test_days_are_their_own_windows_and_carry_no_range() -> None:
    report = analyze(
        [_item("PL-0001", closed=date(2026, 8, 25))],
        Churn(),
        CONFIG,
        by=BY_DAY,
        today=date(2026, 8, 27),
    )

    assert [p.label for p in report.periods] == ["2026-08-25"]


def test_the_open_backlog_is_reported_beside_the_history_it_lags() -> None:
    report = analyze(
        [
            _item("PL-0001", touches=("src/core.py",), status="ready", closed=None),
            _item("PL-0002", touches=("tools/x.py",), status="ready", closed=None),
            _item("PL-0003", touches=("src/core.py",), status="done"),
        ],
        Churn(),
        CONFIG,
        today=date(2026, 8, 27),
    )

    assert report.open_lanes == {"product": 1, "workflow": 1}


def test_the_top_band_named_is_the_highest_one_anything_is_actually_in() -> None:
    """`P0` is a hotfix band and empty in a healthy store; naming it says nothing."""
    report = analyze(
        [
            _item("PL-0001", touches=("src/core.py",), status="ready", closed=None, priority="P1"),
            _item("PL-0002", touches=("tools/x.py",), status="ready", closed=None, priority="P2"),
        ],
        Churn(),
        CONFIG,
        today=date(2026, 8, 27),
    )

    assert report.top_band_name == "P1"
    assert report.top_band == {"product": 1}


def test_a_store_with_no_history_at_all_produces_no_periods() -> None:
    assert analyze([], Churn(), CONFIG, today=date(2026, 8, 27)).periods == ()


# --- what the key says about a run without churn ----------------------------


def _no_git_trend(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> str:
    """The key of a `--no-git` run over two closures, whitespace folded.

    Folded because the assertions are about what the key says, not about where
    its lines happen to wrap.
    """
    items = tmp_path / "docs" / "items"
    items.mkdir(parents=True)
    (items.parent / "docket.toml").write_text(
        '[docket]\nworkflow_paths = ["tools"]\n', encoding="utf-8"
    )
    for ident, touches, closed in (
        ("PL-4401", "src/core.py", "2026-08-25"),
        ("PL-4402", "tools/x.py", "2026-09-02"),
    ):
        (items / f"{ident}-x.md").write_text(
            f"---\nid: {ident}\ntitle: Item {ident}\npriority: P2\neffort: S\n"
            f"status: done\nclasses: perf\ntouches: {touches}\nadded: 2026-08-01\n"
            f"closed: {closed}\n---\n\n**Problem.** P\n**Why it matters.** W\n"
            "**Done when.** D\n",
            encoding="utf-8",
        )

    assert main(["trend", "--items", str(items), "--no-git", "--today", "2026-09-05"]) == 0
    return " ".join(capsys.readouterr().out.split())


def test_no_git_says_churn_was_not_asked_for(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The flag is a choice, not a fault, and the key must not report it as one.

    It said "git could not be read in this checkout" under `--no-git`, where
    nothing had been asked of git at all (`PL-F5NV`).
    """
    key = _no_git_trend(tmp_path, capsys)

    assert "churn not shown: not asked for, so this run read nothing from git." in key
    assert "could not be read" not in key


def test_a_history_git_did_not_answer_still_says_it_could_not_be_read() -> None:
    """The other cause keeps its own wording, so the two cannot collapse into one."""
    report = analyze(
        [_item("PL-0001")],
        Churn(declined="git did not answer 1 of the 1 questions this read put to it"),
        CONFIG,
        today=date(2026, 8, 27),
    )
    key = " ".join(format_trend(report).split())

    assert "churn not shown: git could not be read in this checkout." in key
    assert "not asked for" not in key


def test_a_history_git_answered_with_no_line_counts_is_not_read_as_not_asked() -> None:
    """Only the command knows whether it asked git, so the key takes its word (`PL-PWH6`).

    An empty, undeclined reading is what a repository whose every commit is a
    merge, empty or binary-only gives back, and it read as a `--no-git` run
    while the cause was inferred from the reading's shape. Git answered, so the
    columns are drawn, at zero; only a caller that asked nothing says so, by
    passing no reading at all.
    """
    answered = analyze([_item("PL-0001")], Churn(), CONFIG, today=date(2026, 8, 27))
    key = " ".join(format_trend(answered).split())

    assert answered.churn_reading == CHURN_READ
    assert "not asked for" not in key
    assert "could not be read" not in key
    unasked = analyze([_item("PL-0001")], None, CONFIG, today=date(2026, 8, 27))
    assert unasked.churn_reading == CHURN_NOT_ASKED


def test_no_git_names_the_day_its_windows_are_anchored_at(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """And why a run that reads git puts the same closures in other periods.

    Without git the first commit is unknown, so the windows start at the first
    closure; a run that reads git starts them at the first commit, and every
    item column re-bucketed with nothing saying why (`PL-F5NV`).
    """
    key = _no_git_trend(tmp_path, capsys)

    assert "anchored at 2026-08-25, the first closure." in key
    assert "A run that reads git anchors at the first commit to change a line instead" in key
