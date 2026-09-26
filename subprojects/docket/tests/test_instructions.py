"""The instruction-set parser: which lines carry a date, and which date counts.

Every date here is synthetic. The point of the item this file was written for
is that the advisory reading this parser must be proven working before the
tree is old enough to fire it - so nothing below waits on a real file ageing,
and the boundaries are exercised now rather than in ten weeks.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from docket.instructions import Assertion, parse, read

TODAY = date(2026, 12, 1)


def _file(tmp_path: Path, name: str, text: str) -> Path:
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_a_line_carrying_a_date_is_one_assertion() -> None:
    rows = parse("CLAUDE.md", "Measured 2026-09-04: the egress policy refuses doi.org.\n")

    assert rows == [
        Assertion(
            file="CLAUDE.md",
            line=1,
            when=date(2026, 9, 4),
            text="Measured 2026-09-04: the egress policy refuses doi.org.",
        )
    ]


def test_a_line_carrying_no_date_is_not_an_assertion() -> None:
    """Most of an instruction file is undated prose, and none of it ages."""
    assert parse("CLAUDE.md", "Keep simulation code independent of the UI toolkit.\n") == []


def test_the_newest_date_on_a_line_is_the_one_that_counts() -> None:
    """The property that lets a record be discharged without being falsified.

    Counted per date occurrence, the 2026-08-31 below would keep reporting
    itself after the re-verification was written, and no honest edit would
    ever clear it - an advisory that cannot reach zero. Reading the newest
    date makes "re-verified <today>" the discharge for both kinds of line.
    """
    rows = parse("CLAUDE.md", "(project owner, 2026-08-31; re-verified 2026-11-20)\n")

    assert [row.when for row in rows] == [date(2026, 11, 20)]


def test_the_line_number_is_where_the_reader_goes() -> None:
    text = "one\ntwo\nthree, measured 2026-09-04\n"

    assert [(row.line, row.when) for row in parse("r.md", text)] == [(3, date(2026, 9, 4))]


def test_a_date_inside_a_code_fence_is_skipped() -> None:
    """A dated example command is a template, not a claim about the world.

    Naming one puts an entry in the report that cannot honestly be cleared,
    since clearing it means editing the example to say something it does not
    mean - and one permanent undischargeable entry is what stops a report
    reaching zero.
    """
    text = '```\nbin/docket new "the captures standing in the queue on 2026-09-21"\n```\n'

    assert parse("capture.md", text) == []


def test_a_date_after_a_closed_fence_is_read_again() -> None:
    """The fence toggles; it does not silence the rest of the file."""
    text = "```\n2026-01-01\n```\nMeasured 2026-09-04.\n"

    assert [row.when for row in parse("r.md", text)] == [date(2026, 9, 4)]


def test_a_tilde_fence_closes_the_way_a_backtick_fence_does() -> None:
    text = "~~~\n2026-01-01\n~~~\nMeasured 2026-09-04.\n"

    assert [row.when for row in parse("r.md", text)] == [date(2026, 9, 4)]


def test_a_code_span_at_a_line_start_hides_no_date_below_it() -> None:
    """A backtick fence's info string holds no backtick, so this line opens nothing.

    Read as a toggle, it opened a fence the next real one closed, and the
    dated line between the two went unread (`PL-92MY`).
    """
    text = "Match on\n``` `x` ```, then.\nMeasured 2026-09-04.\n```\n2026-01-01\n```\n"

    assert [row.when for row in parse("r.md", text)] == [date(2026, 9, 4)]


def test_an_opener_nothing_closes_hides_no_date_below_it() -> None:
    """A fence nothing closes is not a fence, so the audit still reads past it."""
    text = "```\nan example never closed\nMeasured 2026-09-04.\n"

    assert [row.when for row in parse("r.md", text)] == [date(2026, 9, 4)]


def test_something_shaped_like_a_date_and_not_being_one_is_dropped() -> None:
    """A typo takes its own line out of the audit, never the whole file."""
    text = "A typo, 2026-13-45, and a real one, 2026-09-04.\nAnd 2026-02-30 alone.\n"

    assert [(row.line, row.when) for row in parse("r.md", text)] == [(1, date(2026, 9, 4))]


def test_a_timestamp_is_not_a_dated_assertion() -> None:
    """`\\b` at the end refuses a date that something else continues."""
    assert parse("r.md", "at 2026-09-04T09:00Z\n") == []


def test_age_counts_days_since_the_newest_date() -> None:
    row = Assertion("CLAUDE.md", 1, date(2026, 9, 4), "x")

    assert row.age(TODAY) == 88


def test_a_line_dated_in_the_future_is_simply_not_yet_due() -> None:
    """This repository dates a cutover setting a day ahead, deliberately."""
    row = Assertion("docket.toml", 1, date(2026, 12, 4), "x")

    assert row.age(TODAY) == -3


def test_read_walks_a_directory_and_takes_a_named_file_as_it_stands(tmp_path: Path) -> None:
    _file(tmp_path, "CLAUDE.md", "Measured 2026-09-04.\n")
    _file(tmp_path, "rules/one.md", "Measured 2026-09-05.\n")
    _file(tmp_path, "rules/deep/two.md", "Measured 2026-09-06.\n")
    _file(tmp_path, "rules/notes.txt", "Measured 2026-09-07.\n")

    rows = read(tmp_path, ("CLAUDE.md", "rules"))

    assert [row.file for row in rows] == ["CLAUDE.md", "rules/deep/two.md", "rules/one.md"]


def test_read_takes_a_file_named_twice_only_once(tmp_path: Path) -> None:
    """A project naming both a directory and a file inside it reads it once."""
    _file(tmp_path, "rules/one.md", "Measured 2026-09-05.\n")

    assert len(read(tmp_path, ("rules", "rules/one.md"))) == 1


def test_read_skips_a_path_that_is_not_there(tmp_path: Path) -> None:
    """A moved or deleted instruction file must not take a grooming pass down."""
    _file(tmp_path, "CLAUDE.md", "Measured 2026-09-04.\n")

    assert [row.file for row in read(tmp_path, ("CLAUDE.md", "gone.md", "gone/"))] == ["CLAUDE.md"]


def test_read_of_nothing_declared_is_empty(tmp_path: Path) -> None:
    assert read(tmp_path, ()) == ()
