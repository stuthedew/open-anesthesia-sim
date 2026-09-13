"""Tests for `tools/dead_ends.py`, the always-loaded dead-ends record and its budget.

The budget is the whole mechanism. `.claude/hooks/docket-digest.sh` emits this
file's entries at session start and a `SessionStart` hook's output is resent on
every turn, so an entry added without a thought for the cap is paid by every
session forever. A cap nothing enforces is a comment, so what is tested here is
that each way of breaching it actually fails.

The emit/check split is the second thing under test: the preamble explains how
to add an entry, which a session *reading* entries never needs, so it must not
be emitted and must not count against the budget. Getting that backwards is
what the first draft of this tool did.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import dead_ends
import pytest

REPO = Path(__file__).resolve().parents[2]

PREAMBLE = """# Dead ends

Prose that explains how to add an entry. Not emitted, not budgeted.

- a plain prose bullet, which is not an entry

## A section

"""


def entry(what: str, why: str) -> str:
    return f"- **{what}** — {why}\n"


def test_the_shipped_file_is_inside_its_own_budget() -> None:
    """The file in the tree must pass, or `make check` is red for everyone."""
    assert dead_ends.check(dead_ends.DEAD_ENDS.read_text(encoding="utf-8")) == []


def test_emit_excludes_the_preamble_and_prose_bullets() -> None:
    text = PREAMBLE + entry("An approach", "why it failed. `PL-D188`")
    emitted = dead_ends.emitted(text)
    assert "Prose that explains" not in emitted
    assert "a plain prose bullet" not in emitted
    assert "An approach" in emitted


def test_prose_bullets_do_not_count_against_the_entry_budget() -> None:
    text = PREAMBLE + entry("One", "only entry. `PL-D188`")
    assert len(dead_ends.entries(text)) == 1


def test_too_many_entries_fails() -> None:
    text = PREAMBLE + "".join(
        entry(f"Approach {n}", "refuted. `PL-D188`") for n in range(dead_ends.MAX_ENTRIES + 1)
    )
    problems = dead_ends.check(text)
    assert any("over the" in p and "budget" in p for p in problems)


def test_too_many_emitted_bytes_fails() -> None:
    text = PREAMBLE + entry("A long one", "x" * (dead_ends.MAX_EMITTED_BYTES + 1))
    problems = dead_ends.check(text)
    assert any("bytes" in p for p in problems)


def test_a_preamble_may_be_long_without_breaching_the_byte_budget() -> None:
    """The point of the split: explaining the file costs a reader nothing."""
    text = ("x" * (dead_ends.MAX_EMITTED_BYTES * 3)) + "\n\n" + entry("One", "refuted. `PL-D188`")
    assert dead_ends.check(text) == []


def test_an_entry_citing_an_unknown_id_fails() -> None:
    problems = dead_ends.check(PREAMBLE + entry("An approach", "refuted. `PL-ZZZZ`"))
    assert any("PL-ZZZZ" in p and "not an item" in p for p in problems)


def test_an_entry_citing_a_real_id_passes() -> None:
    known = next(iter(dead_ends.known_ids()))
    assert dead_ends.check(PREAMBLE + entry("An approach", f"refuted. `{known}`")) == []


def test_an_entry_with_no_id_at_all_passes() -> None:
    """Not every dead end has an item - some are only recorded in source comments."""
    assert dead_ends.check(PREAMBLE + entry("An approach", "refuted, see store.py")) == []


def test_a_wrapped_entry_is_refused() -> None:
    text = PREAMBLE + entry("An approach", "refuted. `PL-D188`") + "and here is the rest of it\n"
    problems = dead_ends.check(text)
    assert any("continuation" in p for p in problems)


def test_a_following_bullet_or_heading_is_not_a_continuation() -> None:
    text = (
        PREAMBLE
        + entry("One", "refuted. `PL-D188`")
        + entry("Two", "also refuted. `PL-D188`")
        + "## Another section\n"
    )
    assert dead_ends.check(text) == []


@pytest.mark.parametrize("command", ["emit", "check"])
def test_the_script_runs_under_a_bare_interpreter(command: str) -> None:
    """No virtualenv: `make check` and the session-start hook both invoke it bare."""
    result = subprocess.run(
        [sys.executable, str(REPO / "tools" / "dead_ends.py"), command],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, result.stderr


def test_emit_prints_the_header_and_every_entry() -> None:
    result = subprocess.run(
        [sys.executable, str(REPO / "tools" / "dead_ends.py"), "emit"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    shipped = dead_ends.entries(dead_ends.DEAD_ENDS.read_text(encoding="utf-8"))
    assert "bin/docket show" in result.stdout
    assert result.stdout.count("\n") == len(shipped) + 1
