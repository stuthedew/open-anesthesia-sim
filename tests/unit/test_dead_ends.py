"""Tests for `tools/dead_ends.py`, the always-loaded dead-ends record and its budget.

`.claude/hooks/docket-digest.sh` emits this file's entries at session start and
a `SessionStart` hook's output is resent on every turn, so an entry added
without a thought for the budget is paid by every session forever.

What is tested is the split between the two kinds of finding, because getting
it wrong in either direction is a live failure. Size only ever *warns* - and
warns at 80% of budget, before the decision is forced on whoever trips the cap
mid-task - because a red gate on an unrelated commit is how a session learns to
raise the cap, which is the one repair that is never right. A structural fault
*does* fail, because a dangling id or a wrapped entry is silent otherwise. The
third case matters as much as either: a comfortable file must say nothing at
all, or the advisory fires every run and trains a reader to skim past it.

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


def test_size_never_fails_the_build() -> None:
    """A blocked commit on an unrelated task is how a session learns to raise the cap."""
    text = PREAMBLE + "".join(
        entry(f"Approach {n}", "refuted. `PL-D188`") for n in range(dead_ends.MAX_ENTRIES + 1)
    )
    assert dead_ends.check(text) == []


def test_over_budget_warns_and_names_all_three_repairs() -> None:
    text = PREAMBLE + "".join(
        entry(f"Approach {n}", "refuted. `PL-D188`") for n in range(dead_ends.MAX_ENTRIES + 1)
    )
    advisories = dead_ends.budget(text)
    assert any("over budget" in a for a in advisories)
    joined = " ".join(advisories)
    assert "shorten" in joined and "merge" in joined and "drop" in joined


def test_over_the_byte_budget_warns() -> None:
    text = PREAMBLE + entry("A long one", "x" * (dead_ends.MAX_EMITTED_BYTES + 1))
    assert any("over budget" in a for a in dead_ends.budget(text))


def test_the_nudge_fires_before_the_budget_is_reached() -> None:
    """The whole point: the decision arrives with slack, not at the cap."""
    count = int(dead_ends.MAX_ENTRIES * dead_ends.NUDGE_FRACTION)
    text = PREAMBLE + "".join(entry(f"Approach {n}", "refuted. `PL-D188`") for n in range(count))
    advisories = dead_ends.budget(text)
    assert any("near budget" in a for a in advisories)
    assert not any("over budget" in a for a in advisories)


def test_a_comfortable_file_says_nothing_at_all() -> None:
    """An advisory that fires every run trains a reader to skim the output."""
    text = PREAMBLE + entry("One", "refuted. `PL-D188`")
    assert dead_ends.budget(text) == []


def test_the_shipped_file_is_not_yet_in_the_nudge_band() -> None:
    assert dead_ends.budget(dead_ends.DEAD_ENDS.read_text(encoding="utf-8")) == []


def test_a_preamble_may_be_long_without_breaching_the_byte_budget() -> None:
    """The point of the split: explaining the file costs a reader nothing."""
    text = ("x" * (dead_ends.MAX_EMITTED_BYTES * 3)) + "\n\n" + entry("One", "refuted. `PL-D188`")
    assert dead_ends.check(text) == []
    assert dead_ends.budget(text) == []


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


def test_an_entry_citing_a_token_the_store_could_not_mint_says_nothing() -> None:
    """`PL-[A-Z0-9]{3,4}` read three letters as an id; only three *digits* is one.

    The store mints four characters from Crockford base32 minus the vowels, or
    three digits, and nothing else. A looser reader here turns an ordinary
    hyphenated word into "cites X, which is not an item" - a hard failure on
    prose that named no item at all (`PL-KYW3`).
    """
    text = PREAMBLE + entry("An approach", "refuted at the PL-CAP stage")  # not-an-id

    assert dead_ends.check(text) == []
