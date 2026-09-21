"""Tests for the near-duplicate search `bin/docket new` runs as it files."""

from __future__ import annotations

from datetime import date

from docket.duplicates import DISPLAY_FLOOR, anchor, near_duplicates, similarity
from docket.model import Item


def _item(
    identifier: str,
    title: str,
    *,
    touches: tuple[str, ...],
    status: str = "ready",
    recurrences: tuple[str, ...] = (),
) -> Item:
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
        recurrences=recurrences,
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
    Measured 2026-09-20, a floor of zero prints candidates on every one of the
    321 open items probed as a simulated capture - a warning that fires every
    run without changing a decision, which `CLAUDE.md` calls a defect in the
    check rather than coverage.
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


def test_the_recurrence_anchors_on_the_item_already_carrying_one() -> None:
    """Without this the count fragments across a cluster and never reaches three.

    Measured by replaying the two real clusters through the search as if it
    had existed when they were filed: each new capture is most similar to the
    *previous* capture rather than to the diagnosis at the head of the cluster,
    so the five suppression-check filings spread as 2 + 1 + 1 and peak at two.
    Anchoring collects 3 on `PL-5MFL` and crosses the threshold. A cluster
    whose evidence is split three ways is a cluster nothing surfaces.

    Both candidates were already selected and already printed, so this
    reorders a shortlist rather than extending one - it cannot invent a
    cluster, only decide which member of one the evidence lands on.
    """
    closest = _item(
        "PL-AAAA",
        "verify's suppression check reads every added line as code",
        touches=("subprojects/docket/src/docket/verify.py",),
    )
    already = _item(
        "PL-BBBB",
        "verify's suppression check reads prose as code",
        touches=("subprojects/docket/src/docket/verify.py",),
        recurrences=("2026-09-19 PL-CCCC",),
    )

    found = near_duplicates(
        "verify's suppression check reads every added line as code, again",
        ("subprojects/docket/src/docket/verify.py",),
        [closest, already],
    )

    assert found[0].item.identifier == "PL-AAAA", "the ranking still puts the closest title first"
    picked = anchor(found)
    assert picked is not None
    assert picked.item.identifier == "PL-BBBB"


def test_a_withdrawn_entry_does_not_pull_the_next_capture_onto_the_same_item() -> None:
    """The one way a single false match could compound into a cluster.

    `anchor` prefers a candidate already carrying recurrences, so an entry a
    reader has disowned would keep sending captures to the item the reader just
    said they do not belong on - and three of those is the generator threshold,
    reached entirely on evidence nobody believes (`PL-34BG`).
    """
    closest = _item(
        "PL-AAAA",
        "verify's suppression check reads every added line as code",
        touches=("subprojects/docket/src/docket/verify.py",),
    )
    disowned = _item(
        "PL-BBBB",
        "verify's suppression check reads prose as code",
        touches=("subprojects/docket/src/docket/verify.py",),
        recurrences=("2026-09-19 PL-CCCC withdrawn 2026-09-21 PL-DDDD",),
    )

    found = near_duplicates(
        "verify's suppression check reads every added line as code, again",
        ("subprojects/docket/src/docket/verify.py",),
        [closest, disowned],
    )

    picked = anchor(found)
    assert picked is not None
    assert picked.item.identifier == "PL-AAAA", "a withdrawn entry still won the anchor"


def test_anchoring_an_empty_shortlist_names_nothing() -> None:
    """No candidates means no recurrence, rather than a guess at which item."""
    assert anchor(()) is None


def test_a_cluster_is_still_caught_at_its_second_filing() -> None:
    """The property `DISPLAY_FLOOR` was chosen to preserve, rather than its value.

    `PL-DGP0` raised the floor from 0.10 to 0.15 on the finding that the
    candidates between them are all false. That is true of *clusters* and not
    of *pairs*: 0.15 drops two real pairs, `PL-5MFL`/`PL-4FD2` at 0.147 and
    `PL-5QLP`/`PL-QMC0` at 0.143, and drops no cluster, because every one is
    still caught when it first repeats and `anchor` accumulates from there.

    So this pins the thing that would be a real defect if it broke - the second
    filing of a cluster finding the first - using the slug-rename cluster's own
    titles, which score 0.200 against each other. A floor raised past that
    would pass `test_an_unrelated_title_sharing_a_path_is_not_offered` and
    silently stop the mechanism working.
    """
    first = _item(
        "PL-AAAA",
        "docket record renames an item file as a side effect of writing a field",
        touches=("subprojects/docket/src/docket/store.py",),
    )

    found = near_duplicates(
        "A field write renames the item file, so the rename lands in a diff about something else",
        ("subprojects/docket/src/docket/store.py",),
        [first],
    )

    assert [candidate.item.identifier for candidate in found] == ["PL-AAAA"]
