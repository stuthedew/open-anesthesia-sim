"""Tests for `tools/dead_ends.py`, which prints the dead-ends list for the session-start digest.

`.claude/hooks/docket-digest.sh` prints this file's entries at session start and
a `SessionStart` hook's output is resent on every turn, so an entry added
without a thought for the budget is paid by every session forever.

Two things are tested. The first is what `emit` prints: the entries and never
the preamble, which explains how to add an entry and which a session reading
the entries never needs. The second is the budget: the shipped file stays
below `NUDGE_FRACTION` of 30 entries and 4,000 printed bytes, so a session that
adds an entry makes room for it in the same commit. This test is the budget's
only enforcement since `PL-8F5B` removed the tool's `check` subcommand.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import dead_ends

REPO = Path(__file__).resolve().parents[2]

PREAMBLE = """# Dead ends

Prose that explains how to add an entry. Not emitted, not budgeted.

- a plain prose bullet, which is not an entry

## A section

"""


def entry(what: str, why: str) -> str:
    return f"- **{what}** — {why}\n"


def printed(text: str) -> list[str]:
    """The lines `emit` prints under its header for the file `text`."""
    return dead_ends.emitted(text).splitlines()[1:]


def test_the_shipped_file_is_below_the_nudge_on_both_budgets() -> None:
    """Adding an entry that reaches 80% of either budget fails here, in the commit that adds it."""
    text = dead_ends.DEAD_ENDS.read_text(encoding="utf-8")

    assert len(printed(text)) < dead_ends.MAX_ENTRIES * dead_ends.NUDGE_FRACTION
    size = len(dead_ends.emitted(text).encode("utf-8"))
    assert size < dead_ends.MAX_EMITTED_BYTES * dead_ends.NUDGE_FRACTION


def test_emit_excludes_the_preamble_and_prose_bullets() -> None:
    text = PREAMBLE + entry("An approach", "why it failed. `PL-D188`")

    assert printed(text) == ["- **An approach** — why it failed. `PL-D188`"]


def test_a_preamble_may_be_long_without_counting_against_the_byte_budget() -> None:
    """The point of the split: explaining the file costs a reader nothing."""
    text = ("x" * (dead_ends.MAX_EMITTED_BYTES * 3)) + "\n\n" + entry("One", "refuted. `PL-D188`")

    assert len(dead_ends.emitted(text).encode("utf-8")) < 200


def test_a_file_with_no_entry_prints_nothing_not_even_the_header() -> None:
    assert dead_ends.emitted(PREAMBLE) == ""


def test_an_entry_wrapped_onto_an_indented_line_is_printed_whole() -> None:
    """`PL-F5B9`: indented, the second line is the entry's, so it is printed joined."""
    text = PREAMBLE + "- **One shared\n  queue document** — rejected. `PL-D188`\n"

    assert printed(text) == ["- **One shared queue document** — rejected. `PL-D188`"]


def test_an_entry_carried_on_from_the_margin_is_not_printed_short() -> None:
    """`PL-DQ9C`: the digest names an entry the walker declined, rather than printing it short.

    Printed as the walker reads it, this entry ended at `holds is`, with its
    retrieval id lost on the declined line.
    """
    text = PREAMBLE + (
        "- **An index committed beside the items** - rejected: anything an index holds is\n"
        "recomputable, and an index is one more thing two branches conflict over. `PL-KM3X`\n"
    )

    assert printed(text) == [
        "- docs/dead-ends.md:9: not printed, since line 10 carries it on from the margin "
        "and it would read short; read it in the file."
    ]


def test_a_following_bullet_or_heading_carries_no_entry_on() -> None:
    text = (
        PREAMBLE
        + entry("One", "refuted. `PL-D188`")
        + entry("Two", "also refuted. `PL-D188`")
        + "## Another section\n"
    )

    assert printed(text) == [
        "- **One** — refuted. `PL-D188`",
        "- **Two** — also refuted. `PL-D188`",
    ]


def test_a_line_separator_in_an_entry_carries_nothing_on() -> None:
    """A U+2028 ends no line in CommonMark (0.31.2 § 2.1), so an entry holding one is one line.

    Cut by `str.splitlines()`, what followed it was read as a line carrying the
    entry on from the margin (`PL-BBYJ`).
    """
    text = (
        PREAMBLE
        + entry("An approach", "refuted twice. `PL-D188`")
        + entry("Two", "also refuted. `PL-D188`")
    )

    assert dead_ends._printed(text) == [
        "- **An approach** — refuted twice. `PL-D188`",
        "- **Two** — also refuted. `PL-D188`",
    ]


def test_a_retired_entry_is_not_printed() -> None:
    """The retired section records where an entry went, and no session needs it on every turn."""
    text = PREAMBLE + f"\n{dead_ends.RETIRED}\n\n" + entry("Gone", "retired: its code was removed.")

    assert dead_ends.emitted(text) == ""


def test_emit_runs_under_a_bare_interpreter_and_prints_the_shipped_entries() -> None:
    """No virtualenv: the session-start hook invokes it bare."""
    result = subprocess.run(
        [sys.executable, str(REPO / "tools" / "dead_ends.py"), "emit"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )

    assert result.returncode == 0, result.stderr
    shipped = dead_ends.emitted(dead_ends.DEAD_ENDS.read_text(encoding="utf-8"))
    assert result.stdout == shipped + "\n"
    assert result.stdout.startswith(dead_ends.HEADER)
