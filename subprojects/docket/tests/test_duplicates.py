"""Tests for the near-duplicate search `bin/docket new` runs as it files."""

from __future__ import annotations

from datetime import date

from docket.duplicates import DISPLAY_FLOOR, near_duplicates, similarity
from docket.model import Item


def _item(identifier: str, title: str, *, touches: tuple[str, ...], status: str = "ready") -> Item:
    return Item(
        identifier=identifier,
        title=title,
        priority="P2",
        effort="S",
        status=status,
        classes=("defect",),
        touches=touches,
        blocked_by=(),
        feature="",
        milestone="",
        added=date(2026, 9, 1),
        closed=None,
        commit="",
        reason="",
        body="",
    )


def test_a_shared_path_selects_and_the_title_only_orders() -> None:
    """The key the measurement chose, in the one test that would catch its loss.

    Title similarity across the store catches 0 of 13 known duplicate pairs and
    fires on the sixteen triage passes instead (`PL-TZ7T`), so an implementation
    that scored titles first and used the path to break ties would pass a naive
    "did it find the duplicate" test and be the refuted design. This pins both
    halves: the item with the closest title is not offered when it declares a
    different path, and the item that does declare the path is.
    """
    store = [
        _item(
            "PL-AAAA",
            "verify's suppression check reads prose as code",
            touches=("subprojects/docket/src/docket/verify.py",),
        ),
        _item(
            "PL-BBBB",
            "verify's suppression check reads prose as code, exactly",
            touches=("src/anesthesia_sim/core/tissue.py",),
        ),
    ]

    found = near_duplicates(
        "verify's suppression check reads every added line as code",
        ("subprojects/docket/src/docket/verify.py",),
        store,
    )

    assert [candidate.item.identifier for candidate in found] == ["PL-AAAA"]
    assert found[0].shared == ("subprojects/docket/src/docket/verify.py",)


def test_an_unrelated_title_sharing_a_path_is_not_offered() -> None:
    """The floor's whole job, and the reason it is not zero.

    Most of this store's open items declare `cli.py` or `verify.py`, so the
    shared-path key alone selects 34 to 83 candidates for a typical capture.
    Measured 2026-09-20, a floor of zero prints three of them on 323 of 325
    captures - a warning that fires every run without changing a decision,
    which `CLAUDE.md` calls a defect in the check rather than coverage.
    """
    store = [
        _item(
            "PL-AAAA",
            "Make the session-start digest name both lanes",
            touches=("subprojects/docket/src/docket/verify.py",),
        )
    ]

    found = near_duplicates(
        "verify's suppression check reads every added line as code",
        ("subprojects/docket/src/docket/verify.py",),
        store,
    )

    assert found == ()
    assert (
        similarity(
            "Make the session-start digest name both lanes",
            "verify's suppression check reads every added line as code",
        )
        <= DISPLAY_FLOOR
    )


def test_a_closed_item_is_not_offered() -> None:
    """What drops the items meant to recur, without a rule naming them.

    A triage pass, a release cut and a tag are titled almost identically every
    time and are `done` within hours, and they are the only clusters title
    similarity finds at a usable threshold. Scoring open items alone is what
    keeps the warning off them, so this is the rule that would silently readmit
    sixteen "Triage the N captures on DATE" if it were dropped.
    """
    store = [
        _item(
            "PL-AAAA",
            "Triage the 12 untriaged captures standing in the queue",
            touches=("docs/items",),
            status="done",
        )
    ]

    found = near_duplicates(
        "Triage the 9 untriaged captures standing in the queue", ("docs/items",), store
    )

    assert found == ()


def test_a_declared_directory_reaches_a_module_inside_it() -> None:
    """A capture declaring a directory shares with an item declaring a file in it.

    38 of this store's open items declare a directory rather than a module, so
    comparing the two as strings would drop the shared path on every one of
    them - and a dropped path is a candidate that is never scored at all,
    which is the silent half of the failure.
    """
    store = [
        _item(
            "PL-AAAA",
            "verify's suppression check reads prose as code",
            touches=("subprojects/docket/tests/test_verify.py",),
        )
    ]

    found = near_duplicates(
        "verify's suppression check reads prose as code again", ("subprojects/docket/tests",), store
    )

    assert [candidate.item.identifier for candidate in found] == ["PL-AAAA"]


def test_two_sessions_filing_the_same_title_get_the_same_order() -> None:
    """Ties break on the id, so the answer does not depend on directory order.

    `read_items` walks the filesystem, so items arrive in whatever order the
    store yields them. Two equally-scoring candidates ordered by arrival would
    give two sessions filing the same capture two different top candidates -
    and with `PL-X5JR` the top candidate is the item the recurrence is recorded
    onto, so the count would land on a different item each time.
    """
    title = "verify's suppression check reads prose as code"
    store = [
        _item("PL-ZZZZ", title, touches=("subprojects/docket/src/docket/verify.py",)),
        _item("PL-AAAA", title, touches=("subprojects/docket/src/docket/verify.py",)),
    ]

    forwards = near_duplicates(title, ("subprojects/docket/src/docket/verify.py",), store)
    backwards = near_duplicates(
        title, ("subprojects/docket/src/docket/verify.py",), list(reversed(store))
    )

    assert [candidate.item.identifier for candidate in forwards] == ["PL-AAAA", "PL-ZZZZ"]
    assert [candidate.item.identifier for candidate in backwards] == ["PL-AAAA", "PL-ZZZZ"]


def test_a_capture_declaring_nothing_searches_nothing() -> None:
    """No paths means no answer, rather than a title-only search.

    The fallback that looks conservative is the refuted key: scoring titles
    across the store with no path to narrow on catches none of the known
    duplicates and finds the recurring-by-design items instead. `PL-THLT` is
    what keeps a fresh capture out of this case, by reading the paths off the
    working tree.
    """
    store = [
        _item(
            "PL-AAAA",
            "verify's suppression check reads prose as code",
            touches=("subprojects/docket/src/docket/verify.py",),
        )
    ]

    assert near_duplicates("verify's suppression check reads prose as code", (), store) == ()
