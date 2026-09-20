"""Tests for the near-duplicate search `bin/docket new` runs at capture time."""

from __future__ import annotations

from docket.duplicates import (
    DEFAULT_LIMIT,
    MIN_SIMILARITY,
    content_words,
    near_duplicates,
    similarity,
)
from docket.model import Item


def _item(identifier: str, title: str, touches: str = "a.py", status: str = "ready") -> Item:
    return Item(
        identifier=identifier,
        title=title,
        priority="P2",
        effort="S",
        status=status,
        classes=(),
        touches=tuple(part for part in touches.split(",") if part),
        blocked_by=(),
        feature="",
        milestone="",
        added=None,
        closed=None,
        commit="",
        reason="",
        body="",
    )


def test_a_title_keeps_the_words_that_say_what_it_is_about() -> None:
    """Case, punctuation and possessives are noise; the domain words are not."""
    assert content_words("Docket verify's check reads PROSE as code!") == {
        "docket",
        "verify",
        "check",
        "reads",
        "prose",
        "code",
    }


def test_function_words_are_dropped_and_domain_words_are_not() -> None:
    """A stopword list that ate `new` or `item` would blind the ranking."""
    words = content_words("The new item is in the store and it was not read")
    assert "new" in words and "item" in words and "store" in words
    assert not words & {"the", "is", "in", "and", "it", "was", "not"}


def test_similarity_is_symmetric_and_bounded() -> None:
    one, other = "verify reads prose as code", "code that verify reads"
    assert similarity(one, other) == similarity(other, one)
    assert 0.0 < similarity(one, other) < 1.0
    assert similarity(one, one) == 1.0


def test_two_titles_sharing_no_content_words_do_not_divide_by_zero() -> None:
    assert similarity("and the of", "but it is") == 0.0
    assert similarity("alpha beta", "gamma delta") == 0.0


def test_the_shared_path_selects_and_the_title_only_ranks() -> None:
    """The measured design: a near-identical title in another file is not a match.

    This is the property the whole module turns on. Title similarity alone was
    measured and refused - it caught none of the known duplicate pairs at any
    usable threshold - so a title that matches perfectly but declares a
    different file has to score nothing at all.
    """
    elsewhere = _item("PL-AAAA", "verify reads prose as code", touches="other.py")
    here = _item("PL-BBBB", "verify reads prose as code", touches="a.py")

    found = near_duplicates("verify reads prose as code", ("a.py",), [elsewhere, here])

    assert [match.item.identifier for match in found] == ["PL-BBBB"]


def test_a_directory_declaration_covers_a_file_beneath_it() -> None:
    """One spelling of "these paths overlap", shared with `docket concurrent`."""
    broad = _item("PL-AAAA", "verify reads prose as code", touches="src/docket")

    found = near_duplicates("verify reads prose as code too", ("src/docket/verify.py",), [broad])

    assert [match.item.identifier for match in found] == ["PL-AAAA"]
    assert found[0].paths == ("src/docket",)


def test_closed_items_are_not_offered() -> None:
    """A triage pass or a release cut is `done` within hours.

    Scoring against open items alone is what drops the recurring-by-design
    clusters - sixteen "Triage the N captures on DATE" - for free.
    """
    done = _item("PL-AAAA", "Triage the 9 captures on 2026-09-19", status="done")
    dropped = _item("PL-BBBB", "Triage the 9 captures on 2026-09-18", status="dropped")
    live = _item("PL-CCCC", "Triage the 9 captures on 2026-09-17")

    found = near_duplicates("Triage the 9 captures on 2026-09-20", ("a.py",), [done, dropped, live])

    assert [match.item.identifier for match in found] == ["PL-CCCC"]


def test_candidates_rank_closest_first() -> None:
    far = _item("PL-AAAA", "verify greps an added line for three markers")
    near = _item("PL-BBBB", "verify reads prose as code in a brief")

    found = near_duplicates("verify reads prose as code", ("a.py",), [far, near], floor=0.0)

    assert [match.item.identifier for match in found] == ["PL-BBBB", "PL-AAAA"]
    assert found[0].score > found[1].score


def test_a_tie_breaks_on_the_identifier_so_two_runs_agree() -> None:
    """The store is read from a directory listing; nothing else here fixes the order."""
    first = _item("PL-ZZZZ", "verify reads prose as code")
    second = _item("PL-AAAA", "verify reads prose as code")

    found = near_duplicates("verify reads prose as code", ("a.py",), [first, second])

    assert [match.item.identifier for match in found] == ["PL-AAAA", "PL-ZZZZ"]


def test_a_weak_match_is_below_the_floor_and_is_not_printed() -> None:
    """An advisory that fires on every filing is one a session learns to skim."""
    unrelated = _item("PL-AAAA", "The vaporizer dial moves in real increments")

    assert near_duplicates("verify reads prose as code", ("a.py",), [unrelated]) == []
    assert near_duplicates("verify reads prose as code", ("a.py",), [unrelated], floor=0.0) != []


def test_no_candidate_paths_means_no_search_rather_than_a_title_search() -> None:
    """A fresh capture carries no `touches`, and title similarity was refused.

    `PL-THLT` is the item that supplies paths from the working tree; until it
    lands the honest answer here is nothing, never a title-only guess.
    """
    twin = _item("PL-AAAA", "verify reads prose as code")

    assert near_duplicates("verify reads prose as code", (), [twin]) == []


def test_at_most_the_limit_is_returned() -> None:
    crowd = [_item(f"PL-{n:04d}", "verify reads prose as code") for n in range(9)]

    assert len(near_duplicates("verify reads prose as code", ("a.py",), crowd)) == DEFAULT_LIMIT
    assert len(near_duplicates("verify reads prose as code", ("a.py",), crowd, limit=2)) == 2


def test_the_recorded_duplicate_clusters_are_caught_at_their_second_filing() -> None:
    """The regression the constants were set against.

    Each pair is a real filing from this project's history, with the
    similarity it actually scores. They are what `MIN_SIMILARITY` must not be
    raised past without a fresh count: every one of them is a diagnosis that
    was paid for twice.
    """
    recorded = [
        (
            "verify's suppression check reads prose as code, so a brief's own words are flagged",
            "docket verify's suppression check reads every added line as code, prose included",
        ),
        ("Cut the v0.4.31 release and tag it", "Cut and tag the v0.4.31 release"),
    ]
    for existing, filing in recorded:
        twin = _item("PL-AAAA", existing)
        found = near_duplicates(filing, ("a.py",), [twin])
        assert found, f"{filing!r} should have matched {existing!r}"
        assert found[0].score >= MIN_SIMILARITY
