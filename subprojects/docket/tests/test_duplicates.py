"""Tests for the near-duplicate search `bin/docket new` runs as it files."""

from __future__ import annotations

from dataclasses import replace
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
    feature: str = "",
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
        feature=feature,
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
            "PL-8888",
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

    assert [candidate.item.identifier for candidate in found] == ["PL-8888"]
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
            "PL-8888",
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

    The two share a feature, so a subject selects the pair and the status is
    the only thing left to drop it: sharing `docs/items` alone no longer
    selects anything (`PL-SV0D`), which would let this pass with the rule gone.
    """
    store = [
        _item(
            "PL-8888",
            "Triage the 12 untriaged captures standing in the queue",
            touches=("docs/items",),
            status="done",
            feature="queue-triage",
        )
    ]

    found = near_duplicates(
        "Triage the 9 untriaged captures standing in the queue",
        ("docs/items",),
        store,
        feature="queue-triage",
    )

    assert found == ()
    reopened = near_duplicates(
        "Triage the 9 untriaged captures standing in the queue",
        ("docs/items",),
        [replace(store[0], status="ready")],
        feature="queue-triage",
    )
    assert [candidate.item.identifier for candidate in reopened] == ["PL-8888"]


def test_a_declared_directory_reaches_a_module_inside_it() -> None:
    """A capture declaring a directory shares with an item declaring a file in it.

    38 of this store's open items declare a directory rather than a module, so
    comparing the two as strings would drop the shared path on every one of
    them - and a dropped path is a candidate that is never scored at all,
    which is the silent half of the failure.
    """
    store = [
        _item(
            "PL-8888",
            "verify's suppression check reads prose as code",
            touches=("subprojects/docket/tests/test_verify.py",),
        )
    ]

    found = near_duplicates(
        "verify's suppression check reads prose as code again", ("subprojects/docket/tests",), store
    )

    assert [candidate.item.identifier for candidate in found] == ["PL-8888"]


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
        _item("PL-8888", title, touches=("subprojects/docket/src/docket/verify.py",)),
    ]

    forwards = near_duplicates(title, ("subprojects/docket/src/docket/verify.py",), store)
    backwards = near_duplicates(
        title, ("subprojects/docket/src/docket/verify.py",), list(reversed(store))
    )

    assert [candidate.item.identifier for candidate in forwards] == ["PL-8888", "PL-ZZZZ"]
    assert [candidate.item.identifier for candidate in backwards] == ["PL-8888", "PL-ZZZZ"]


def test_a_capture_declaring_nothing_searches_nothing() -> None:
    """No subject means no answer, rather than a title-only search.

    The fallback that looks conservative is the refuted key: scoring titles
    across the store with nothing to narrow on catches none of the known
    duplicates and finds the recurring-by-design items instead. `PL-THLT` is
    what keeps a fresh capture out of this case, by reading the paths off the
    working tree; an id in the title or a `--feature` is what a capture on a
    clean tree can still name.
    """
    store = [
        _item(
            "PL-8888",
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
        "PL-8888",
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

    assert found[0].item.identifier == "PL-8888", "the ranking still puts the closest title first"
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
        "PL-8888",
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
    assert picked.item.identifier == "PL-8888", "a withdrawn entry still won the anchor"


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
        "PL-8888",
        "docket record renames an item file as a side effect of writing a field",
        touches=("subprojects/docket/src/docket/store.py",),
    )

    found = near_duplicates(
        "A field write renames the item file, so the rename lands in a diff about something else",
        ("subprojects/docket/src/docket/store.py",),
        [first],
    )

    assert [candidate.item.identifier for candidate in found] == ["PL-8888"]


# The four instances `PL-0HLS` was opened on, one test each, with the titles,
# paths and features as filed: three pairs the path-only key missed, and the
# false recurrence it recorded.

YZ17 = (
    "A simulation step below about 4.8e-304 s makes maximum_step_count raise OverflowError,"
    " outside the simulator's exception hierarchy, because 86 400 s divided by the step"
    " overflows to infinity; require_supported_simulation_step accepts every positive finite"
    " step up to 0.1 s, so the model declares no smallest supported step"
)
F76 = (
    "A simulation step below about 4.8e-304 s, or a step count too long to print, fails"
    " SimulationState construction with OverflowError or ValueError rather than"
    " SimulationConfigurationError"
)


def test_an_untriaged_capture_meets_an_untriaged_item() -> None:
    """`PL-TS7L`'s instance: two captures of one overflow, neither declaring a path.

    `PL-YZ17` was filed on 2026-10-03 into a store already holding `PL-5F76`.
    Both were untriaged, so neither declared `touches`, and the path-only key
    skipped every candidate without them; both carried `feature:
    numerical-domain`, which is the subject they share.

    Shown, and not recorded: two items one feature groups were grouped on
    purpose, so the feature alone is never evidence that a defect fired again.
    """
    earlier = _item("PL-5F76", F76, touches=(), status="untriaged", feature="numerical-domain")

    found = near_duplicates(YZ17, (), [earlier], feature="numerical-domain", items_dir="docs/items")

    assert [candidate.item.identifier for candidate in found] == ["PL-5F76"]
    assert found[0].feature == "numerical-domain"
    assert anchor(found) is None, "the feature alone recorded a recurrence"


def test_an_untriaged_item_without_touches_is_a_candidate() -> None:
    """The candidate side of `PL-TS7L`: a capture with a path meets an item with none.

    Capture leaves `touches` unset until triage, so skipping every open item
    declaring none skipped exactly the same-day captures duplicates cluster in,
    whatever paths the second capture declared or inferred.
    """
    store = [
        _item(
            "PL-8888",
            "verify's suppression check reads prose as code",
            touches=(),
            status="untriaged",
            feature="suppression-check",
        )
    ]

    found = near_duplicates(
        "verify's suppression check reads every added line as code",
        ("subprojects/docket/src/docket/verify.py",),
        store,
        feature="suppression-check",
        items_dir="docs/items",
    )

    assert [candidate.item.identifier for candidate in found] == ["PL-8888"]


def test_a_clean_tree_capture_meets_the_item_its_title_names() -> None:
    """`PL-9VPH`'s instance: a capture with no paths, paired by the id in its title.

    The housekeeping recipe files before the work starts, so the tree is clean
    and `PL-THLT` reads nothing. `PL-4CPP` named `PL-54V0`, and `PL-BYN2`, open
    with the same job, declared `PL-54V0`'s file. Both name one item, so the
    match is recorded as well as shown.
    """
    earlier = _item(
        "PL-BYN2",
        "A project-owner ratification on PL-54V0 exists only on"
        " origin/claude/upbeat-rubin-v1dktv, whose session has completed with no pull request"
        " open, so the one carrier of that decision is an unmerged branch",
        touches=("docs/items/PL-54V0-resumed-at-refuses-an-unkeyframed-instant-with.md",),
    )

    found = near_duplicates(
        "Carry PL-54V0's owner-ratification record across from claude/upbeat-rubin-v1dktv,"
        " where it was pushed after #844 merged and no pull request ever took it",
        (),
        [earlier],
        items_dir="docs/items",
    )

    assert [candidate.item.identifier for candidate in found] == ["PL-BYN2"]
    assert found[0].named == ("PL-54V0",)
    picked = anchor(found)
    assert picked is not None
    assert picked.item.identifier == "PL-BYN2"


def test_an_item_file_is_compared_by_its_id_and_not_its_slug() -> None:
    """A slug that drifted still names its item, read off the working tree here.

    `docket check` only advises on a stale slug, so a declared item file can
    outlive its title; compared as a path, the two would share nothing.
    """
    store = [
        _item(
            "PL-BBBB",
            "Carry the ratification on PL-8888 across from a branch no pull request took",
            touches=("docs/items/PL-8888-an-older-title.md",),
        )
    ]

    found = near_duplicates(
        "Carry the ratification record across from the stranded branch",
        ("docs/items/PL-8888-the-title-it-has-now.md",),
        store,
        items_dir="docs/items",
    )

    assert [candidate.item.identifier for candidate in found] == ["PL-BBBB"]
    assert found[0].named == ("PL-8888",)


def test_a_shared_feature_survives_a_file_move() -> None:
    """`PL-6SV4`'s instance: the earlier item still declared the file its section left.

    `PL-VYK1` declared `.claude/skills/docket/SKILL.md`; the release section
    moved to `modes/release.md` (`PL-2XM2`), which is what `PL-6SV4` declared,
    so the two shared no path. Both carried `feature: release-process`.
    """
    earlier = _item(
        "PL-VYK1",
        "The docket skill's release handover tags at origin/main rather than at the cut's own"
        " merge commit, so a re-run of the three commands tags whatever merged next",
        touches=(".claude/skills/docket/SKILL.md",),
        feature="release-process",
    )

    found = near_duplicates(
        "The tag commands the release mode prescribes tag origin/main, which is the release's"
        " merge commit only until the next merge lands: with sibling sessions merging minutes"
        " apart a tag can land on a later commit, and doc_check's version test cannot tell it"
        " apart because that commit still declares the same version",
        (".claude/skills/docket/modes/release.md", "subprojects/docket/src/docket/cli.py"),
        [earlier],
        feature="release-process",
        items_dir="docs/items",
    )

    assert [candidate.item.identifier for candidate in found] == ["PL-VYK1"]
    assert found[0].shared == ()
    assert found[0].feature == "release-process"


def test_sharing_only_the_item_store_is_not_a_recurrence() -> None:
    """`PL-SV0D`'s instance: `PL-DHGC` was recorded on `PL-JLBD` through `docs/items` alone.

    The capture's working tree held two item files and nothing else, and
    `PL-JLBD` declared the store directory beside two docket modules. Every
    branch that files an item changes the directory, so sharing it says nothing
    about a mechanism. The titles clear the floor, so the store rule is what
    drops the pair, and a shared module still selects it.
    """
    title = (
        "Ten reads parse item front matter by hand instead of through docket.model, and one is"
        " wrong today: item_reads looks for status: done in a file's first 400 characters, so"
        " it reads 20 of 1,624 closed items as open; the others are generator_check's own"
        " parser, open-status set, list splits and a closure count that misses dropped,"
        " item_reads's --- split, and model's own parser restating FIELD_ORDER and LIST_FIELDS"
    )
    unrelated = _item(
        "PL-JLBD",
        "PL-MT3R is done and bin/docket generators lists it drained, yet its front matter still"
        " carries generator: live and docket check is silent, so the field and the register"
        " disagree about one head while the pause rule reads only open items",
        touches=(
            "subprojects/docket/src/docket/checks.py",
            "subprojects/docket/tests/test_checks.py",
            "docs/items",
        ),
    )
    tree = (
        "docs/items/PL-KGYT-six-readers-found-2026-10-01-respell-facts.md",
        "docs/items/PL-4NG0-thirteen-reads-ask-git-for-facts-docket-vcs.md",
    )

    found = near_duplicates(
        title, tree, [unrelated], feature="read-facts-through-docket", items_dir="docs/items"
    )

    assert similarity(title, unrelated.title) > DISPLAY_FLOOR
    assert found == ()
    assert anchor(found) is None
    above = replace(unrelated, touches=("docs",))
    assert near_duplicates(title, ("docs",), [unrelated], items_dir="docs/items") == ()
    assert near_duplicates(title, tree, [above], items_dir="docs/items") == ()
    through_code = near_duplicates(
        title,
        (*tree, "subprojects/docket/src/docket/checks.py"),
        [unrelated],
        items_dir="docs/items",
    )
    assert [candidate.item.identifier for candidate in through_code] == ["PL-JLBD"]
    assert through_code[0].shared == ("subprojects/docket/src/docket/checks.py",)
