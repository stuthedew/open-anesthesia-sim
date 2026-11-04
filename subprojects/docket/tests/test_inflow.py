"""Tests for the apparatus inflow report.

The rules under test are the ones a wrong answer would hide: the store is not
apparatus inflow, a short final period is compared per day, and a sweep's own
filings are counted apart from the inflow the question is about.
"""

from __future__ import annotations

import subprocess
from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path

import pytest

from docket.cli import _missed_expectations, main
from docket.config import Config
from docket.inflow import UNBANDED, analyze, missed
from docket.model import LANE_PRODUCT, Item, reentry_faults
from docket.render import format_inflow
from docket.vcs import FilingParents

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
    classes: tuple[str, ...] = ("defect",),
    no_successor: tuple[str, ...] = (),
    sweep: str = "",
) -> Item:
    return Item(
        identifier=identifier,
        title=f"Item {identifier}",
        priority=priority,
        effort="S",
        status="done" if closed else "ready",
        classes=classes,
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
        no_successor=no_successor,
        sweep=sweep,
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


def test_a_line_a_successor_head_answers_names_it() -> None:
    """A head whose `reenters:` names the line answers it, and is listed apart.

    Under one heading, a line a successor already answered read exactly as one
    nobody had (`PL-0WT0`). A claim `model.is_generator` refuses - two members,
    under the floor - answers nothing, so its line stays open.
    """
    other = _item("PL-FXD1", date(2026, 8, 20), touches=("src/a.py",), closed=date(2026, 8, 25))
    members = [_item(f"PL-0MB{n}", date(2026, 9, 1), touches=("src/c.py",)) for n in (1, 2, 3)]
    head = _item(
        "PL-0HD1",
        date(2026, 9, 3),
        reenters=("PL-FXD0",),
        root_cause_of=("PL-0MB1", "PL-0MB2", "PL-0MB3"),
    )
    unsound = _item(
        "PL-0NS1", date(2026, 9, 3), reenters=("PL-FXD1",), root_cause_of=("PL-0MB1", "PL-0MB2")
    )
    filings = [
        _item(f"PL-0R{n}B", date(2026, 9, n), reenters=("PL-FXD0", "PL-FXD1")) for n in (1, 2)
    ]

    report = analyze(
        [FIXED, other, *members, head, unsound, *filings], CONFIG, today=date(2026, 9, 7)
    )

    assert report.reentered == {
        "PL-FXD0": ("PL-0R1B", "PL-0R2B", "PL-0HD1"),
        "PL-FXD1": ("PL-0R1B", "PL-0R2B", "PL-0NS1"),
    }
    assert report.successors == {"PL-FXD0": (head,)}
    text = format_inflow(report)
    unanswered, answered = text.split("a generator whose fix did not hold:")[1].split("answered by")
    assert "PL-FXD1" in unanswered and "PL-FXD0" not in unanswered
    assert "PL-FXD0  by PL-0R1B, PL-0R2B, PL-0HD1" in answered
    assert "successor PL-0HD1 (ready)" in answered


def test_a_line_re_entered_after_its_successors_closed_lists_as_open_again() -> None:
    """`PL-SFW9`: a closed successor answers a line only until three later filings.

    A successor's answer held whatever its status, so `PL-5DZ8` read as settled
    by `PL-4S6C` (done) while `PL-TSXD` re-entered it. The count runs from the
    last successor's close. An open successor answers whatever comes after it.
    """
    members = [_item(f"PL-0MB{n}", date(2026, 9, 1), touches=("src/c.py",)) for n in (1, 2, 3)]
    first = _item(
        "PL-0HD1",
        date(2026, 9, 3),
        closed=date(2026, 9, 5),
        reenters=("PL-FXD0",),
        root_cause_of=("PL-0MB1", "PL-0MB2", "PL-0MB3"),
    )
    second = _item(
        "PL-0HD2",
        date(2026, 9, 6),
        closed=date(2026, 9, 9),
        reenters=("PL-FXD0",),
        root_cause_of=("PL-0MB1", "PL-0MB2", "PL-0MB3"),
    )
    early = [_item(f"PL-0RC{n}", date(2026, 9, n), reenters=("PL-FXD0",)) for n in (1, 2)]
    # Filed after the first successor closed but not after the second.
    between = [_item(f"PL-0RD{n}", date(2026, 9, n), reenters=("PL-FXD0",)) for n in (7, 8)]
    later = [_item(f"PL-0RF{n - 9}", date(2026, 9, n), reenters=("PL-FXD0",)) for n in (10, 11, 12)]
    store = [FIXED, *members, first, second, *early, *between]

    settled = analyze([*store, *later[:2]], CONFIG, today=date(2026, 9, 14))
    assert settled.successors == {"PL-FXD0": (first, second)}

    reopened = analyze([*store, *later], CONFIG, today=date(2026, 9, 14))
    assert "PL-FXD0" in reopened.reentered
    assert reopened.successors == {}
    text = format_inflow(reopened)
    assert "PL-FXD0  by" in text.split("a generator whose fix did not hold:")[1]
    assert "answered by a successor" not in text

    still_open = _item(
        "PL-0HD2",
        date(2026, 9, 6),
        reenters=("PL-FXD0",),
        root_cause_of=("PL-0MB1", "PL-0MB2", "PL-0MB3"),
    )
    working = [FIXED, *members, first, still_open, *early, *between, *later]
    assert analyze(working, CONFIG, today=date(2026, 9, 14)).successors == {
        "PL-FXD0": (first, still_open)
    }


def test_a_line_answered_with_no_successor_is_listed_apart() -> None:
    """`PL-C4F0`: an item whose `no-successor:` names the line answers it, until three more.

    The answer lived only in `PL-4097`'s prose, so every run listed `PL-61FT`
    as a generator whose fix did not hold. Three filings that re-enter the
    line after the answer's date list it as open again, since the mechanism
    has then started producing again.
    """
    filings = [_item(f"PL-0RQ{n}", date(2026, 9, n), reenters=("PL-FXD0",)) for n in (1, 2, 3)]
    answer = _item("PL-0NSW", date(2026, 9, 2), closed=date(2026, 9, 4), no_successor=("PL-FXD0",))

    report = analyze([FIXED, *filings, answer], CONFIG, today=date(2026, 9, 7))

    assert report.answered == {"PL-FXD0": (answer,)}
    text = format_inflow(report)
    assert "a generator whose fix did not hold:" not in text
    assert "PL-FXD0  by PL-0RQ1, PL-0RQ2, PL-0RQ3" in text.split("no successor owed")[1]
    assert "answered by PL-0NSW (done)" in text

    later = [_item(f"PL-0RT{n}", date(2026, 9, n), reenters=("PL-FXD0",)) for n in (5, 6, 7)]
    reopened = analyze([FIXED, *filings, answer, *later], CONFIG, today=date(2026, 9, 14))

    assert reopened.answered == {}
    closed_later = _item(
        "PL-0NSW", date(2026, 9, 2), closed=date(2026, 9, 10), no_successor=("PL-FXD0",)
    )
    still_open = analyze([FIXED, *filings, closed_later, *later], CONFIG, today=date(2026, 9, 14))
    assert still_open.answered == {}  # closing the answer does not move its date
    text = format_inflow(reopened)
    assert "PL-FXD0  by" in text.split("a generator whose fix did not hold:")[1]
    assert "no successor owed" not in text


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


def test_the_new_paths_ceiling_breaks_only_when_the_count_did_not_fall() -> None:
    """A week of fewer filings and fewer new paths can read above the ceiling per filing.

    The week from 2026-10-26 named 11 new paths over 19 filings, after 34 over
    117, and was reported as growth (`PL-2T7X`). Here three new paths over ten
    filings are followed by two over four: 0.50 a filing, but fewer new paths.
    """
    first = [
        _item(f"PL-1{n:03d}", date(2026, 9, 1), touches=(f"tools/a{n % 3}.py",)) for n in range(10)
    ]
    fewer = [
        _item(f"PL-2{n:03d}", date(2026, 9, 8), touches=(f"tools/b{n % 2}.py",)) for n in range(4)
    ]
    today = date(2026, 9, 15)

    assert missed(analyze([*first, *fewer], CONFIG, today=today), today) == ()

    as_many = [*fewer, _item("PL-2009", date(2026, 9, 9), touches=("tools/b2.py",))]
    (line,) = missed(analyze([*first, *as_many], CONFIG, today=today), today)
    assert "3 new apparatus paths over 5 filings, 0.60 a filing" in line
    assert "against 3 new the period before" in line


def test_a_cut_prints_the_broken_predictions_and_nothing_when_none_broke() -> None:
    today = date(2026, 9, 15)
    broken = [_item("PL-1000", date(2026, 9, 1)), _item("PL-2000", date(2026, 9, 8), priority="P1")]

    assert "1 P1 apparatus filing" in _missed_expectations(broken, CONFIG, today)
    assert _missed_expectations(broken[:1], CONFIG, today) == ""
    assert _missed_expectations(broken, Config(items_dir="docs/items"), today) == ""


def _severe(items: list[Item], week: date) -> dict[str, int]:
    """The unexpected bands `analyze` counts for the week starting `week`."""
    periods = analyze(items, CONFIG, today=week + timedelta(days=7)).periods
    return dict(next(p for p in periods if p.start == week).severe)


def test_a_crossing_item_s_p1_is_not_an_unexpected_band() -> None:
    """A band on an item that also edits the product says nothing about the apparatus.

    `PL-HQF5` and `PL-4RL2` declared a rule file beside simulator files
    (`PL-00TR`). `PL-M85T`, `PL-RNYV` and `PL-S79P` declared a tool or an
    apparatus test beside them, and the week to 2026-10-25 reported all three
    as a broken prediction (`PL-P6KV`). A pinned or unpinned P1 in the
    workflow lane still counts.
    """
    week = date(2026, 9, 7)
    on_a_rule = _item(
        "PL-3000",
        week,
        touches=("src/core.py", ".claude/rules/core-domain.md"),
        priority="P1",
        classes=("defect", "safety"),
    )
    with_a_tool = _item(
        "PL-3003",
        week,
        touches=("src/app.py", "tools/contrast_check.py"),
        priority="P1",
        classes=("safety", "anticipated"),
    )
    unpinned_crossing = _item("PL-3004", week, touches=("src/a.py", "tools/a.py"), priority="P1")
    in_a_tool = _item(
        "PL-3001", week, touches=("tools/a.py",), priority="P1", classes=("defect", "safety")
    )
    unpinned = _item("PL-3002", week, touches=(".claude/rules/x.md",), priority="P1")

    assert _severe([on_a_rule, with_a_tool, unpinned_crossing], week) == {}
    assert _severe([on_a_rule, in_a_tool], week) == {"P1": 1}
    assert _severe([unpinned], week) == {"P1": 1}


def test_an_owner_set_p1_is_not_an_unexpected_band() -> None:
    """The owner placed `PL-JRVV` at P1, which records an order, not a severity (`PL-P6KV`).

    A record naming another band describes a decision the item no longer
    carries, so that item still counts.
    """
    week = date(2026, 9, 7)
    placed = replace(_item("PL-3005", week, priority="P1"), owner_priority="P1, 2026-09-08")
    stale = replace(placed, identifier="PL-3006", owner_priority="P2, 2026-09-08")

    assert _severe([placed], week) == {}
    assert _severe([stale], week) == {"P1": 1}


def test_a_missed_prediction_says_where_to_file_its_investigation() -> None:
    """A miss names where to look for an investigation and how to file one (`PL-P6KV`).

    Four cuts printed the week of 2026-10-19's misses and none filed an item.
    """
    filings = [
        _item(f"PL-0PT{n}", date(2026, 9, n), touches=(f"tools/t{n}.py",), priority="P1")
        for n in range(7, 14)
    ]

    shown = _missed_expectations(filings, CONFIG, date(2026, 9, 14))

    assert "bin/docket feature convergence-visibility" in shown
    assert 'bin/docket new --feature convergence-visibility "..."' in shown


def test_product_lane_counts_a_product_reentry() -> None:
    """`PL-K5CX`: a product head whose fix did not hold was never listed.

    The apparatus report counts only filings with an apparatus path, so three
    product defects re-entering a closed product head read as no inflow at
    all. The product lane counts the product work triage's generator check
    asks about, and leaves a filing classed only as new work out.
    """
    fixed = _item("PL-FXP0", date(2026, 8, 20), touches=("src/a.py",), closed=date(2026, 8, 25))
    filings = [
        _item(f"PL-0PR{n}", date(2026, 9, n), touches=("src/a.py",), reenters=("PL-FXP0",))
        for n in (1, 2, 3)
    ]
    feature = _item("PL-0FT1", date(2026, 9, 2), touches=("src/b.py",), classes=("feature",))
    items = [fixed, *filings, feature]

    product = analyze(items, CONFIG, today=date(2026, 9, 7), lane=LANE_PRODUCT)
    apparatus = analyze(items, CONFIG, today=date(2026, 9, 7))

    assert product.reentered == {"PL-FXP0": ("PL-0PR1", "PL-0PR2", "PL-0PR3")}
    assert sum(p.filed for p in product.periods) == 4  # the feature is left out
    assert apparatus.periods == ()
    shown = format_inflow(product)
    assert "the first product\nfiling: an item whose `touches` name a product path" in shown
    assert "PL-FXP0  by PL-0PR1, PL-0PR2, PL-0PR3" in shown


def test_the_release_report_never_reads_the_product_lane() -> None:
    """`PL-04KR`'s predictions are about the apparatus, so a product report breaks none."""
    filings = [
        _item(f"PL-0PS{n}", date(2026, 9, n), touches=("src/a.py",), priority="P1")
        for n in range(1, 9)
    ]

    report = analyze(filings, CONFIG, today=date(2026, 9, 21), lane=LANE_PRODUCT)

    assert report.periods
    assert missed(report, date(2026, 9, 21)) == ()


# `PL-CJGH`: a sweep recorded only by `sweep:`, which no head's `root-cause-of:`
# names. `PL-SWP0` is the sweep, open from 2026-09-02 to 09-04; the fix three
# of its findings re-enter shipped before it.
SWEPT_FIX = _item("PL-FX00", date(2026, 8, 20), touches=("src/a.py",), closed=date(2026, 8, 25))
SWEEP = _item(
    "PL-SWP0",
    date(2026, 9, 2),
    touches=("src/a.py",),
    closed=date(2026, 9, 4),
    sweep="inventories every reader of one fact and files each finding",
    classes=("planning",),
)


def _sweep_store() -> tuple[list[Item], FilingParents]:
    found = [
        _item(f"PL-0SW{n}", date(2026, 9, 3), reenters=("PL-FX00",), priority="P1")
        for n in (1, 2, 3)
    ]
    items = [
        SWEPT_FIX,
        SWEEP,
        *found,
        _item("PL-0RD1", date(2026, 9, 3), reenters=("PL-FX00",)),  # another item's capture
        _item("PL-0LT1", date(2026, 9, 6)),  # a correction under the sweep's id, after it closed
    ]
    filing = FilingParents(
        parents={
            **{item.identifier: frozenset({"PL-SWP0"}) for item in found},
            "PL-0RD1": frozenset({"PL-WRK1"}),
            "PL-0LT1": frozenset({"PL-SWP0"}),
        }
    )
    return items, filing


def test_a_sweep_s_filings_are_counted_apart_from_inflow() -> None:
    """A week spent finding instances on purpose is not a week of rising inflow.

    `PL-K88Z`'s inventory was recorded only by its feature, so its 9 filings in
    the week of 2026-10-19 counted as ordinary inflow and its 5 re-entries as
    fixes failing.
    """
    items, filing = _sweep_store()

    (period,) = analyze(items, CONFIG, today=date(2026, 9, 7), filing=filing).periods

    assert (period.filed, period.by_head, period.by_sweep) == (2, 0, 3)
    assert period.reentries == 1
    assert period.priorities == {"P2": 2}
    assert period.total == 5


def test_a_sweep_s_filings_leave_the_three_filings_list() -> None:
    """Three findings re-entering one fix are what the sweep was asked to find."""
    items, filing = _sweep_store()

    swept = analyze(items, CONFIG, today=date(2026, 9, 7), filing=filing)
    unswept = analyze(
        [replace(item, sweep="") for item in items], CONFIG, today=date(2026, 9, 7), filing=filing
    )

    assert swept.reentered == {}
    assert unswept.reentered == {"PL-FX00": ("PL-0RD1", "PL-0SW1", "PL-0SW2", "PL-0SW3")}


def test_a_filing_a_head_also_names_is_counted_once_under_the_head() -> None:
    head = _item("PL-HD01", date(2026, 9, 2), root_cause_of=("PL-0SW1", "PL-0SW2", "PL-0SW3"))
    items, filing = _sweep_store()

    (period,) = analyze([*items, head], CONFIG, today=date(2026, 9, 7), filing=filing).periods

    assert (period.by_head, period.by_sweep) == (3, 0)


def test_a_sweep_git_could_not_attribute_says_so() -> None:
    """The floor: a column nobody could read prints `?`, and the report says why."""
    items, _ = _sweep_store()
    shallow = FilingParents(declined="the checkout is a shallow clone")

    report = analyze(items, CONFIG, today=date(2026, 9, 7), filing=shallow)
    shown = format_inflow(report)

    (period,) = report.periods
    assert (period.filed, period.by_sweep) == (5, 0)
    assert report.sweeps_unread == "the checkout is a shallow clone"
    assert "      ?" in shown.splitlines()[1]
    assert "  the checkout is a shallow clone." in shown
    assert analyze(items, CONFIG, today=date(2026, 9, 7)).sweeps_unread


def test_a_store_with_no_sweep_needs_no_attribution() -> None:
    report = analyze(
        [SWEPT_FIX, _item("PL-0RD1", date(2026, 9, 3))], CONFIG, today=date(2026, 9, 7)
    )

    assert not report.sweeps_unread
    assert "?" not in format_inflow(report).splitlines()[1]


def test_a_miss_says_when_a_sweep_could_not_be_told_apart() -> None:
    """A broken prediction may be the sweep's own filings, so the cut says it could not tell."""
    items, _ = _sweep_store()
    shallow = FilingParents(declined="the checkout is a shallow clone")

    lines = missed(
        analyze(items, CONFIG, today=date(2026, 9, 14), filing=shallow), date(2026, 9, 14)
    )
    attributed = missed(
        analyze(items, CONFIG, today=date(2026, 9, 14), filing=_sweep_store()[1]), date(2026, 9, 14)
    )

    assert any("3 P1 apparatus filing(s)" in line for line in lines)
    assert lines[-1].endswith(
        "could not be told apart, so these counts include them: the checkout is a shallow clone"
    )
    assert not any("P1" in line or "told apart" in line for line in attributed)


def test_the_command_counts_a_sweep_from_the_commit_that_filed_its_findings(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """End to end, on real git: the commit led by the sweep's id is what attributes a filing."""
    root = tmp_path
    (root / "docket.toml").write_text(
        'items_dir = "docs/items"\nworkflow_paths = ["tools", "docs/items"]\n'
    )
    store = root / "docs" / "items"
    store.mkdir(parents=True)

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)

    def write(identifier: str, extra: str = "") -> None:
        (store / f"{identifier}-x.md").write_text(
            f"---\nid: {identifier}\ntitle: Item {identifier}\nstatus: untriaged\n"
            f"touches: tools/x.py\nadded: 2026-09-03\n{extra}---\n\nBody.\n"
        )

    subprocess.run(["git", "-c", "init.defaultBranch=main", "init", "-q", str(root)], check=True)
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        git("config", name, value)
    write("PL-SWP0", "sweep: inventories every reader of one fact\n")
    git("add", "-A")
    git("commit", "-qm", "PL-SWP0: capture the sweep")
    for identifier in ("PL-0SW1", "PL-0SW2"):
        write(identifier)
    git("add", "-A")
    git("commit", "-qm", "PL-SWP0: file what the inventory found")
    write("PL-0RD1")
    git("add", "-A")
    git("commit", "-qm", "PL-WRK1: capture a finding")

    assert main(["inflow", "--items", str(store), "--today", "2026-09-05"]) == 0
    row = capsys.readouterr().out.splitlines()[1].split()

    # period, filed, /day, re-entry, +head, +sweep: the sweep and PL-0RD1 are ordinary
    assert row[1] == "2" and row[5] == "2"
