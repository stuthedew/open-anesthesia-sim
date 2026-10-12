"""Tests for the apparatus inflow report.

The rules under test are the ones a wrong answer would hide: the store is not
apparatus inflow, a short final period is compared per day, and a sweep's own
filings are counted apart from the inflow the question is about.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from docket.cli import _missed_expectations, main
from docket.config import Config
from docket.inflow import UNBANDED, analyze, missed
from docket.model import Item, reentry_faults

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
    reenters: tuple[str, ...] = (),
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
        reenters=reenters,
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
        "PL-HD00",
        date(2026, 9, 2),
        closed=date(2026, 9, 4),
        root_cause_of=("PL-0BFR", "PL-0DRN", "PL-0FTR"),
    )
    report = analyze(
        [
            head,
            _item("PL-0BFR", date(2026, 9, 1)),  # the cluster that revealed it
            _item("PL-0DRN", date(2026, 9, 3)),  # the sweep's own
            _item("PL-0FTR", date(2026, 9, 6), priority="P3"),  # a fix that did not hold
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


#: A shipped fix outside the apparatus, so it anchors no window of its own.
FIXED = _item("PL-FXD0", date(2026, 8, 20), touches=("src/a.py",), closed=date(2026, 8, 25))


def test_a_reentry_is_counted_in_the_period_it_was_filed() -> None:
    """Counted where the fix failed to hold, and not for a sweep's own filings."""
    head = _item(
        "PL-HD00",
        date(2026, 9, 9),
        touches=("src/b.py",),
        root_cause_of=("PL-0SWD", "PL-0SWB", "PL-0SWC"),
    )
    report = analyze(
        [
            FIXED,
            head,
            _item("PL-0NN1", date(2026, 9, 1), reenters=("PL-FXD0",)),
            _item("PL-0TW2", date(2026, 9, 9), reenters=("PL-FXD0",)),
            _item("PL-0SWD", date(2026, 9, 10), reenters=("PL-FXD0",)),  # the sweep's own
            _item("PL-0SWB", date(2026, 9, 10)),
            _item("PL-0SWC", date(2026, 9, 10)),
        ],
        CONFIG,
        today=date(2026, 9, 21),
    )

    assert [p.reentries for p in report.periods] == [1, 1, 0]
    assert report.reentered == {}  # two re-entries no head explains, under the floor of three


def test_a_closed_item_three_filings_reenter_is_named() -> None:
    filings = [
        _item(f"PL-0RX{n}", date(2026, 9, n), reenters=("PL-FXD0", "PL-FXD0")) for n in (1, 2, 3)
    ]

    report = analyze([FIXED, *filings], CONFIG, today=date(2026, 9, 7))

    assert report.reentered == {"PL-FXD0": ("PL-0RX1", "PL-0RX2", "PL-0RX3")}


def test_a_reentry_must_name_a_fix_shipped_before_the_filing() -> None:
    """Counted as a fix that failed, an open, dropped or later-closed id is a fabrication."""
    by_id = {
        "PL-DNNN": _item("PL-DNNN", date(2026, 8, 1), closed=date(2026, 9, 1)),
        "PL-KTTT": _item("PL-KTTT", date(2026, 8, 1), closed=date(2026, 9, 5)),
        "PL-PNNN": _item("PL-PNNN", date(2026, 8, 1)),
    }
    good = _item("PL-0NWW", date(2026, 9, 1), reenters=("PL-DNNN",))
    bad = _item("PL-0BDD", date(2026, 9, 1), reenters=("PL-KTTT", "PL-PNNN", "PL-GNNN", "PL-0BDD"))

    assert reentry_faults(good, by_id) == ()
    faults = " ".join(reentry_faults(bad, by_id))
    for named in ("itself", "PL-GNNN", "PL-PNNN", "PL-KTTT"):
        assert named in faults


def test_the_release_report_is_silent_when_every_prediction_holds() -> None:
    """One new path in ten filings and no P1; the week still being filed into is not read."""
    quiet = [_item(f"PL-1{n:03d}", date(2026, 9, 1), touches=("tools/a.py",)) for n in range(10)]
    today = date(2026, 9, 8)
    loud = _item("PL-2000", today, touches=("tools/b.py",), priority="P1")

    assert missed(analyze([*quiet, loud], CONFIG, today=today), today) == ()


def test_the_release_report_names_each_prediction_the_last_week_broke() -> None:
    today = date(2026, 9, 15)
    items = [
        FIXED,
        _item("PL-1000", date(2026, 9, 1)),
        _item("PL-2000", date(2026, 9, 8), touches=("tools/b.py",), priority="P1"),
        _item("PL-2001", date(2026, 9, 9), reenters=("PL-FXD0",)),
    ]

    head = _item(
        "PL-2002", date(2026, 9, 9), priority="P1", root_cause_of=("PL-00B1", "PL-00B2", "PL-00B3")
    )

    paths, band, reentry = missed(analyze([*items, head], CONFIG, today=today), today)

    assert "1 new apparatus paths over 3 filings, 0.33 a filing" in paths
    assert "1 P1 apparatus filing" in band  # the head's P1 is a rank, not a severity
    assert "1 re-entries against 0" in reentry


def test_a_cut_prints_the_broken_predictions_and_nothing_when_none_broke() -> None:
    today = date(2026, 9, 15)
    broken = [_item("PL-1000", date(2026, 9, 1)), _item("PL-2000", date(2026, 9, 8), priority="P1")]

    assert "1 P1 apparatus filing" in _missed_expectations(broken, CONFIG, today)
    assert _missed_expectations(broken[:1], CONFIG, today) == ""
    assert _missed_expectations(broken, Config(items_dir="docs/items"), today) == ""
