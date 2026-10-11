"""Tests for the apparatus inflow report.

The rules under test are the ones a wrong answer would hide: the store is not
apparatus inflow, a short final period is compared per day, and a sweep's own
filings are counted apart from the inflow the question is about.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from docket.cli import main
from docket.config import Config
from docket.inflow import UNBANDED, analyze
from docket.model import Item

CONFIG = Config(
    items_dir="docs/items",
    notes_file="docs/WORKING_NOTES.md",
    workflow_paths=("tools", ".claude", "docs/items", "docs/WORKING_NOTES.md"),
)


def _item(
    identifier: str,
    added: date,
    *,
    touches: tuple[str, ...] = ("tools/x.py",),
    priority: str = "P2",
    closed: date | None = None,
    root_cause_of: tuple[str, ...] = (),
) -> Item:
    return Item(
        identifier=identifier,
        title=f"Item {identifier}",
        priority=priority,
        effort="S",
        status="done" if closed else "ready",
        classes=("defect",),
        touches=touches,
        blocked_by=(),
        feature="",
        milestone="",
        added=added,
        closed=closed,
        commit="",
        reason="",
        body="",
        root_cause_of=root_cause_of,
    )


def test_a_filing_naming_only_the_store_is_not_apparatus_inflow() -> None:
    """Every capture writes the store, so counting it reads product work as apparatus."""
    report = analyze(
        [
            _item("PL-0001", date(2026, 9, 1), touches=("docs/items/PL-0002-x.md",)),
            _item("PL-0002", date(2026, 9, 1), touches=("docs/WORKING_NOTES.md", "src/a.py")),
            _item("PL-0003", date(2026, 9, 1), touches=("docs/items", "tools/x.py")),
        ],
        CONFIG,
        today=date(2026, 9, 7),
    )

    (period,) = report.periods
    assert period.filed == 1
    assert period.new_paths == 1  # tools/x.py; the store path is not surface


def test_a_short_final_period_is_compared_per_day() -> None:
    """Seven filings in two days is faster than seven in seven, and /day must say so."""
    items = [_item(f"PL-1{n:03d}", date(2026, 9, 1)) for n in range(7)]
    items += [_item(f"PL-2{n:03d}", date(2026, 9, 8)) for n in range(7)]

    full, short = analyze(items, CONFIG, today=date(2026, 9, 9)).periods

    assert (full.days, short.days) == (7, 2)
    assert full.per_day == pytest.approx(1.0)
    assert short.per_day == pytest.approx(3.5)


def test_a_member_filed_while_its_head_was_open_is_counted_apart() -> None:
    """A sweep's filings are not inflow; a member arriving after the head closed is."""
    head = _item(
        "PL-HEAD",
        date(2026, 9, 2),
        closed=date(2026, 9, 4),
        root_cause_of=("PL-0BEF", "PL-0DUR", "PL-0AFT"),
    )
    report = analyze(
        [
            head,
            _item("PL-0BEF", date(2026, 9, 1)),  # the cluster that revealed it
            _item("PL-0DUR", date(2026, 9, 3)),  # the sweep's own
            _item("PL-0AFT", date(2026, 9, 6), priority="P3"),  # a fix that did not hold
        ],
        CONFIG,
        today=date(2026, 9, 7),
    )

    (period,) = report.periods
    assert (period.filed, period.by_head) == (3, 1)
    assert period.priorities == {"P2": 2, "P3": 1}


def test_a_path_is_new_only_in_the_period_that_first_names_it() -> None:
    report = analyze(
        [
            _item("PL-0001", date(2026, 9, 1), touches=("tools/a.py", "tools/b.py")),
            _item("PL-0002", date(2026, 9, 9), touches=("tools/a.py", "tools/c.py")),
        ],
        CONFIG,
        today=date(2026, 9, 14),
    )

    assert [p.new_paths for p in report.periods] == [2, 1]
    assert [p.new_paths_per_item for p in report.periods] == [2.0, 1.0]


def test_an_untriaged_filing_is_shown_in_the_mix_rather_than_dropped() -> None:
    report = analyze([_item("PL-0001", date(2026, 9, 1), priority="")], CONFIG)

    assert report.periods[0].priorities == {UNBANDED: 1}


def test_the_command_refuses_without_workflow_paths(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """No boundary means no filing is an apparatus filing, and answering would invent one."""
    items = tmp_path / "docs" / "items"
    items.mkdir(parents=True)
    (items.parent / "docket.toml").write_text("[docket]\n", encoding="utf-8")

    assert main(["inflow", "--items", str(items), "--today", "2026-09-05"]) == 1
    assert "no `workflow_paths` are declared" in capsys.readouterr().out
