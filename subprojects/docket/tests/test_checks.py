"""Tests for validation and grooming.

A checker that has only ever run against a clean store proves nothing, so
every rule has a test that constructs the broken input and asserts the rule
notices.
"""

from __future__ import annotations

from datetime import date

from docket.checks import analyze
from docket.config import Config
from docket.model import Item
from docket.plan import OfferedReport
from docket.vcs import (
    BaseRecord,
    ClosureReport,
    LostItem,
    LostReport,
    PullRequestHistory,
    RecordReport,
)
from docket.verify import LandedReport, SlowCommand

TODAY = date(2026, 8, 24)
BRIEF = "**Problem.** x\n**Why it matters.** y\n**Done when.** z\n"


def _offering(*ids: str, declined: str = "") -> OfferedReport:
    """What `next` is about to offer, and how completely that was settled."""
    return OfferedReport(frozenset(ids), declined)


def _item(identifier: str = "PL-K7QX", **overrides: object) -> Item:
    base: dict[str, object] = dict(
        identifier=identifier,
        title="Do the thing",
        priority="P2",
        effort="S",
        status="ready",
        classes=("perf",),
        touches=("a.py",),
        blocked_by=(),
        feature="",
        milestone="",
        added=date(2026, 8, 1),
        closed=None,
        commit="",
        reason="",
        body=BRIEF,
    )
    base.update(overrides)
    # Splatting `dict[str, object]` matches `object` against every field's type; the
    # alternatives are `dict[str, Any]` or an `Unpack[TypedDict]` restating all of
    # `Item`'s fields, both wider than this line-scoped ignore.
    return Item(**base)  # type: ignore[arg-type]


def _errors(*items: Item) -> list[str]:
    return analyze(list(items), TODAY).errors


def _has(messages: list[str], needle: str) -> bool:
    return any(needle in message for message in messages)


def test_a_valid_item_raises_nothing() -> None:
    report = analyze([_item()], TODAY)

    assert report.errors == []
    assert report.advisories == []


def test_a_missing_id_is_an_error() -> None:
    assert _has(_errors(_item(identifier="")), "no `id`")


def _shipped(**overrides: object) -> Item:
    """A closed item, which is the only kind that may carry a milestone."""
    base: dict[str, object] = dict(status="done", closed=date(2026, 8, 30), commit="abc1234")
    base.update(overrides)
    return _item(**base)


def test_a_milestone_on_unfinished_work_is_an_error() -> None:
    """`milestone:` records the release an item went out in, so it cannot precede one."""
    assert _has(_errors(_item(status="ready", milestone="v0.2.8")), "cannot have shipped")
    assert _has(_errors(_item(status="needs-decision", milestone="v0.2.8")), "cannot have shipped")


def test_a_milestone_naming_a_release_that_has_not_been_cut_is_an_error() -> None:
    """PL-HXYY: ten items carried `milestone: v0.2.8` while the project was on 0.2.7.

    `release.unreleased` selects finished work with no milestone, so each was
    invisible to the release that would have shipped it - omitted from its own
    notes, which a tag then makes permanent.
    """
    report = analyze([_shipped(milestone="v0.2.8")], TODAY, version="0.2.7")

    assert _has(report.errors, "names a release later than the current version (0.2.7)")


def test_a_milestone_naming_a_release_already_cut_is_not() -> None:
    """The state every stamped item is in after `docket release` has run."""
    assert analyze([_shipped(milestone="v0.2.7")], TODAY, version="0.2.7").errors == []
    assert analyze([_shipped(milestone="v0.2.7")], TODAY, version="0.3.0").errors == []


def test_a_milestone_is_not_judged_where_the_comparison_cannot_be_made() -> None:
    """A version this rule cannot read is left alone rather than failed.

    `None` is a caller that did not ask, an empty string is a project with no
    version file, and anything outside `major.minor.patch` - on either side of
    the comparison - is a naming scheme the rule has no opinion about.
    """
    assert analyze([_shipped(milestone="v9.9.9")], TODAY).errors == []
    assert analyze([_shipped(milestone="v9.9.9")], TODAY, version="").errors == []
    assert analyze([_shipped(milestone="v9.9.9")], TODAY, version="2026.08").errors == []
    assert analyze([_shipped(milestone="2026.08")], TODAY, version="0.2.7").errors == []


def test_a_malformed_id_is_an_error() -> None:
    assert _has(_errors(_item(identifier="PL-1")), "not a valid item id")


def test_a_duplicate_id_is_an_error() -> None:
    """The collision this scheme is built to avoid is still reported if it happens."""
    assert _has(_errors(_item(), _item()), "used by more than one file")


def test_a_misspelled_field_is_rejected_rather_than_ignored() -> None:
    item = _item()
    broken = Item(**{**item.__dict__, "unknown_fields": ("priorty",)})

    assert _has(_errors(broken), "unrecognized field")


def test_an_unknown_status_is_an_error() -> None:
    assert _has(_errors(_item(status="wip")), "is not one of")


def test_an_open_item_needs_a_priority_and_an_effort() -> None:
    messages = _errors(_item(priority="", effort=""))

    assert _has(messages, "no priority")
    assert _has(messages, "no effort")


def test_an_open_item_needs_the_brief_a_stranger_would_read() -> None:
    assert _has(_errors(_item(body="**Problem.** only this\n")), "brief is missing")


def test_a_heading_may_be_elaborated_past_the_words_the_check_looks_for() -> None:
    """`PL-921W`, whose better heading the literal test rejected.

    It was captured as `**Why it matters, and why it is not new.**`, reads as
    the required section to anyone, and had to be flattened to satisfy the
    check. Editing prose that was already right is not what this check is for.
    """
    elaborated = _item(
        body=("**Problem.** x\n**Why it matters, and why it is not new.** y\n**Done when.** z\n")
    )

    assert _errors(elaborated) == []


def test_a_required_heading_with_nothing_under_it_is_not_a_brief() -> None:
    """The other direction, and the one that costs someone else's time."""
    messages = _errors(_item(body="**Problem.** x\n\n**Why it matters.**\n\n**Done when.** z\n"))

    assert _has(messages, "brief has nothing under **Why it matters.**")
    assert not _has(messages, "brief is missing")


def test_a_stub_above_a_real_brief_does_not_satisfy_the_check() -> None:
    """`PL-RWZV`'s own shape, and why the *first* heading is the one judged.

    Four empty headings echoing the format, with the real brief written under
    a second set below them. Judging any occurrence with text under it would
    pass exactly this, which is the hole rather than the fix.
    """
    messages = _errors(
        _item(
            body=(
                "**Problem.** x\n\n"
                "**Why it matters.**\n\n"
                "**Done when.**\n\n"
                "**Problem.** the real one\n\n"
                "**Why it matters.** because\n\n"
                "**Done when.** it holds\n"
            )
        )
    )

    assert _has(messages, "brief has nothing under **Why it matters.**, **Done when.**")


def test_an_empty_section_is_reported_as_empty_rather_than_missing() -> None:
    """Two failures, two messages: the fix for one is not the fix for the other."""
    messages = _errors(_item(body="**Problem.**\n"))

    assert _has(messages, "brief has nothing under **Problem.**")
    assert _has(messages, "brief is missing **Why it matters.**, **Done when.**")


def test_a_blocked_item_needs_no_done_when() -> None:
    """It cannot state its closing condition until its blocker resolves."""
    blocker = _item("PL-B1B1")
    blocked = _item(
        "PL-C2C2",
        status="blocked",
        blocked_by=("PL-B1B1",),
        body="**Problem.** x\n**Why it matters.** y\n",
    )

    assert _errors(blocker, blocked) == []


def test_a_blocked_item_must_name_a_blocker() -> None:
    assert _has(
        _errors(_item(status="blocked", body="**Problem.** x\n**Why it matters.** y\n")),
        "names no blocking item",
    )


def test_a_blocker_that_is_not_an_item_is_an_error() -> None:
    assert _has(
        _errors(
            _item(
                status="blocked",
                blocked_by=("PL-Z9Z9",),
                body="**Problem.** x\n**Why it matters.** y\n",
            )
        ),
        "which is not an item",
    )


def test_an_item_cannot_block_itself() -> None:
    assert _has(
        _errors(
            _item(
                status="blocked",
                blocked_by=("PL-K7QX",),
                body="**Problem.** x\n**Why it matters.** y\n",
            )
        ),
        "lists itself",
    )


DEPENDS_BRIEF = "**Problem.** Depends on `PL-0002`.\n**Why it matters.** y\n**Done when.** z\n"


def _prose(
    text: str, *, blocked_by: tuple[str, ...] = (), blocker_status: str = "ready"
) -> list[str]:
    """Advisories raised for one item whose brief says `text` about `PL-0002`."""
    subject = _item(
        "PL-0001",
        blocked_by=blocked_by,
        body=f"**Problem.** {text}\n**Why it matters.** y\n**Done when.** z\n",
    )
    blocker = _item("PL-0002", status=blocker_status, closed=date(2026, 8, 2))
    return analyze([subject, blocker], TODAY).advisories


def test_prose_dependency_without_an_edge_raises_an_advisory() -> None:
    """The rule itself: the body names a prerequisite the front matter does not."""
    advisories = _prose("This depends on `PL-0002` for the unit.")
    assert _has(advisories, "names PL-0002 as a prerequisite in prose")
    # The item, the blocker and the sentence, so it can be judged without
    # opening the file - and the fix, which is either of two answers.
    assert _has(advisories, "PL-0001")
    assert _has(advisories, "This depends on `PL-0002` for the unit.")
    assert _has(advisories, "reword the sentence if it is not a prerequisite")


def test_the_advisory_names_the_field_that_actually_changes_the_ranking() -> None:
    """`next` filters on `status`, never on `blocked-by`, so an advisory that
    asked only for the edge would name a fix that does not fix the thing it
    says it fixes - which is the failure mode this whole check is against."""
    assert _has(_prose("This depends on `PL-0002`."), "set `status: blocked`")


def test_a_prose_dependency_that_is_declared_is_silent() -> None:
    assert _prose("This depends on `PL-0002`.", blocked_by=("PL-0002",)) == []


def test_a_prose_dependency_on_closed_work_is_history_rather_than_a_defect() -> None:
    """Most in-body mentions name work that has since closed; firing on those
    would make the advisory unreadable within a week."""
    assert _prose("This depends on `PL-0002`.", blocker_status="done") == []


def test_the_heading_form_fires_despite_the_period_inside_it() -> None:
    """`**Depends on.**` is the item format's own heading, so the period that
    closes it must not read as a sentence break."""
    assert _has(_prose("**Depends on.** `PL-0002` for the ratios."), "names PL-0002")


def test_an_item_that_says_it_depends_on_nothing_stays_silent() -> None:
    """The reason the window refuses `.`: `PL-GNN1` says exactly this, and a
    rule that read across the break would fire on the sentence denying it."""
    assert _prose("**Depends on.** Nothing. `PL-0002` should be re-read after this.") == []


def test_a_reversed_sequencing_sentence_is_not_reported_as_a_dependency() -> None:
    """`before` and `follows` name the edge backwards, so they are not cues.
    Telling an item to declare a blocker it actually blocks would be a wrong
    answer in the tool's own voice."""
    assert _prose("**Worth doing before `PL-0002`, not after.**") == []
    assert _prose("The call sites can follow with `PL-0002`.") == []


def test_a_narrated_after_is_not_read_as_a_prerequisite() -> None:
    """`after` points the right way and still cannot be used: the phrasing that
    states a prerequisite is the phrasing that narrates one."""
    assert _prose("**Amended 2026-09-03, after `PL-0002` merged (#263).**") == []


def test_a_cue_does_not_reach_across_a_clause_into_an_unrelated_mention() -> None:
    assert _prose("which needs no history at all) and `PL-0002` (the other one)") == []
    assert _prose("is the machinery this item needs; `PL-0002` decides how.") == []


def test_a_blocker_named_repeatedly_is_reported_once() -> None:
    advisories = _prose("Depends on `PL-0002`. It waits on `PL-0002` for the unit.")
    assert len(advisories) == 1


def _compound(text: str, *, blocked_by: tuple[str, ...] = ()) -> list[str]:
    """Advisories for one item whose brief says `text` about two open blockers."""
    subject = _item(
        "PL-0001",
        blocked_by=blocked_by,
        body=f"**Problem.** {text}\n\n**Why it matters.** y\n\n**Done when.** z\n",
    )
    return analyze([subject, _item("PL-0002"), _item("PL-0003")], TODAY).advisories


def test_a_second_prerequisite_in_a_compound_sentence_is_reported() -> None:
    """`PL-GGCN`: the cue introduces the first blocker and "and on" carries the
    second, so reading only the first left a real open edge invisible while the
    check reported clean. `PL-VZL0` is the instance, and it wraps mid-sentence
    across a parenthetical - which is why the anchor is the paragraph and not
    the line."""
    advisories = _compound(
        "**Blocked on `PL-0002`** (the exact step, which changes what is left\n"
        "here) **and on `PL-0003`** (the citation check reads no docstrings).",
        blocked_by=("PL-0002",),
    )
    assert _has(advisories, "names PL-0003 as a prerequisite in prose")


def test_both_halves_of_a_compound_sentence_are_reported_when_neither_is_declared() -> None:
    advisories = _compound("Blocked on `PL-0002` and on `PL-0003`.")
    assert _has(advisories, "names PL-0002 as a prerequisite in prose")
    assert _has(advisories, "names PL-0003 as a prerequisite in prose")


def test_an_and_on_with_no_cue_in_its_paragraph_is_ordinary_prose() -> None:
    """The reason "and on" is not simply another cue. Unanchored it reads a
    sentence that reports on two items as declaring a prerequisite on the
    second, which is a wrong answer in the tool's own voice."""
    assert _compound("The advisory reports on `PL-0002` and on `PL-0003` alike.") == []


def test_a_cue_does_not_license_an_and_on_in_a_later_paragraph() -> None:
    """One real dependency must not admit every continuation in the rest of the
    brief - the anchor is the paragraph the cue fired in, nothing wider."""
    advisories = _compound(
        "Depends on `PL-0002` for the unit.\n\nSeparately it reports on the "
        "circuit and on `PL-0003` at once.",
        blocked_by=("PL-0002",),
    )
    assert advisories == []


def test_a_closed_item_is_not_asked_to_declare_its_prerequisites() -> None:
    subject = _item("PL-0001", status="done", closed=date(2026, 8, 2), pr="7", body=DEPENDS_BRIEF)
    assert analyze([subject, _item("PL-0002")], TODAY).advisories == []


def test_an_undeclared_prerequisite_never_fails_the_build() -> None:
    """Whether the sentence states a prerequisite is judgment, so this reports
    and never refuses."""
    report = analyze([_item("PL-0001", body=DEPENDS_BRIEF), _item("PL-0002")], TODAY)
    assert report.errors == []
    assert _has(report.advisories, "names PL-0002 as a prerequisite in prose")


def test_needs_decision_must_state_the_decision() -> None:
    assert _has(_errors(_item(status="needs-decision")), "states no decision to make")


def test_needs_decision_passes_when_it_states_one() -> None:
    assert (
        _errors(_item(status="needs-decision", body=BRIEF + "**Decision needed.** Which?\n")) == []
    )


def test_safety_work_may_not_sit_in_a_low_band() -> None:
    assert _has(_errors(_item(classes=("safety",), priority="P2")), "starts at P0 or P1")


def test_blocked_anticipated_safety_work_may_sit_anywhere() -> None:
    """A blocked item is not in the set `next` chooses from, so a band is a claim
    about work nobody can start. Forcing one here is what drives an item to be
    re-classed out of `safety` to satisfy the checker, which is the failure the
    rule exists to prevent."""
    blocked = _item(
        classes=("safety", "anticipated"), priority="P3", status="blocked", blocked_by=("PL-0001",)
    )

    assert not _has(_errors(blocked), "starts at P0 or P1")


def test_the_exemption_is_claimed_rather_than_inferred() -> None:
    """Fail closed. Reading a *missing* class as the anticipated case would make
    forgetting to write one the way to obtain the exemption, so a blocked safety
    item that claims nothing keeps the strict band - and is told how to claim."""
    silent = _item(classes=("safety",), priority="P3", status="blocked", blocked_by=("PL-0001",))
    messages = _errors(silent)

    assert _has(messages, "starts at P0 or P1")
    assert _has(messages, "class it `anticipated`")


def test_a_misspelled_exemption_fails_closed() -> None:
    """The same property under PL-MVC2's undeclared vocabulary: a typo cannot
    buy the exemption, because only the exact class grants it."""
    typo = _item(
        classes=("safety", "anticpated"), priority="P3", status="blocked", blocked_by=("PL-0001",)
    )

    assert _has(_errors(typo), "starts at P0 or P1")


def test_a_live_blocked_safety_defect_keeps_its_band() -> None:
    """The case the exemption must not swallow: something is wrong now and the
    blocker is only sequencing, so the band still stands."""
    live = _item(
        classes=("safety", "defect"), priority="P3", status="blocked", blocked_by=("PL-0001",)
    )

    assert _has(_errors(live), "starts at P0 or P1")


def test_unblocking_safety_work_re_fires_the_band_rule() -> None:
    """The exemption must not become a way to park safety work at P3 forever:
    the moment the item is workable, the band is owed again, and the checker
    asks rather than anyone having to remember."""
    unblocked = _item(
        classes=("safety", "anticipated"), priority="P3", status="ready", verify="pytest"
    )

    assert _has(_errors(unblocked), "starts at P0 or P1")


def test_a_blocked_item_may_not_outrank_its_blocker() -> None:
    """A P1 waiting on a P3 promises a schedule the blocker does not keep, and is
    how a live safety defect goes quiet while passing every other rule."""
    blocked = _item("PL-AAAA", priority="P1", status="blocked", blocked_by=("PL-BBBB",))
    blocker = _item("PL-BBBB", priority="P3", verify="pytest")

    assert _has(_errors(blocked, blocker), "raise PL-BBBB to P1 or above")


def test_waiting_on_equal_or_higher_rank_is_fine() -> None:
    blocked = _item("PL-AAAA", priority="P2", status="blocked", blocked_by=("PL-BBBB",))
    blocker = _item("PL-BBBB", priority="P1", verify="pytest")

    assert not _has(_errors(blocked, blocker), "or above")


def test_a_closed_blocker_holds_nothing_up() -> None:
    """It is already done, and a done item's priority is often cleared outright."""
    blocked = _item("PL-AAAA", priority="P1", status="blocked", blocked_by=("PL-BBBB",))
    closed = _item(
        "PL-BBBB", priority="", effort="", status="done", closed=TODAY, pr="7", added=None
    )

    assert not _has(_errors(blocked, closed), "or above")


def test_a_done_item_records_its_date() -> None:
    """The `closed` date is answerable from the store, so it is owed unconditionally.

    Its `pr` is not: the number does not exist until the pull request is open,
    so that half is owed only once the closure has landed and lives with the
    `ClosureReport` tests below.
    """
    messages = _errors(_item(status="done", priority="", effort="", added=None))

    assert _has(messages, "records no `closed` date")
    assert not _has(messages, "records no `pr`")


def test_a_done_item_needs_no_commit() -> None:
    """It is kept where it is to hand, but a squash discards it, so `pr` carries
    the provenance instead - see the `ClosureReport` tests for when it is owed."""
    closed = _item(status="done", pr="48", closed=TODAY, added=None, priority="", effort="")

    assert _errors(closed) == []


def test_a_dropped_item_records_why() -> None:
    """Without the reason, the same finding gets raised again."""
    assert _has(
        _errors(_item(status="dropped", closed=TODAY, priority="", effort="", added=None)),
        "records no `reason`",
    )


def test_a_closed_item_needs_no_added_date() -> None:
    """Items closed before this format existed cannot acquire one."""
    closed = _item(
        status="done", commit="abc1234", pr="48", closed=TODAY, added=None, priority="", effort=""
    )

    assert _errors(closed) == []


def test_an_untriaged_item_needs_only_a_title_and_a_body() -> None:
    """Demanding a priority at capture time is how ideas stop being written down."""
    captured = _item(
        status="untriaged",
        priority="",
        effort="",
        classes=(),
        touches=(),
        body="Half an idea, written down anyway.\n",
    )

    assert _errors(captured) == []


def test_an_untriaged_item_still_needs_a_body() -> None:
    assert _has(_errors(_item(status="untriaged", priority="", effort="", body="")), "no body")


def test_a_stale_capture_is_a_grooming_advisory() -> None:
    old = _item(
        status="untriaged",
        priority="",
        effort="",
        added=date(2026, 7, 1),
        body="Captured and forgotten.\n",
    )

    assert _has(analyze([old], TODAY).advisories, "triage or drop them")


def test_a_blocked_item_whose_blocker_closed_is_flagged_for_promotion() -> None:
    done = _item("PL-B1B1", status="done", commit="abc1234", closed=TODAY, priority="", effort="")
    blocked = _item(
        "PL-C2C2",
        status="blocked",
        blocked_by=("PL-B1B1",),
        body="**Problem.** x\n**Why it matters.** y\n",
    )

    assert _has(analyze([done, blocked], TODAY).advisories, "every blocker has closed")


def test_an_overfull_top_band_is_an_advisory() -> None:
    band = [_item(f"PL-B1B{n}", priority="P1") for n in range(7)]

    assert _has(analyze(band, TODAY).advisories, "a session can choose between at a glance")


def test_a_top_band_padded_with_blocked_items_is_not_overfull() -> None:
    """Blocked work is in the band and is not a choice a session can make.

    The checker's own blocker-band rule puts it there: an item may not wait on
    one in a lower band, so gating a `P1` on a `P2` raises the blocker rather
    than lowering the blocked. Counting both would then report an overfull band
    that nobody over-prioritized and nobody can drain (`PL-P23D`).
    """
    startable = [_item(f"PL-B1B{n}", priority="P1") for n in range(4)]
    blocked = [
        _item(f"PL-C2C{n}", priority="P1", status="blocked", blocked_by=("PL-B1B0",))
        for n in range(3)
    ]

    advisories = analyze(startable + blocked, TODAY).advisories

    assert not _has(advisories, "a session can choose between at a glance")


def test_a_top_band_of_mostly_open_decisions_is_an_advisory() -> None:
    band = [
        _item(
            "PL-B1B1",
            priority="P1",
            status="needs-decision",
            body=BRIEF + "**Decision needed.** ?\n",
        ),
        _item(
            "PL-C2C2",
            priority="P1",
            status="needs-decision",
            body=BRIEF + "**Decision needed.** ?\n",
        ),
        _item("PL-D3D3", priority="P1"),
    ]

    assert _has(analyze(band, TODAY).advisories, "schedule the decisions")


def test_process_work_crowding_the_top_band_is_an_advisory() -> None:
    band = [
        _item("PL-B1B1", priority="P1", classes=("session-cost",)),
        _item("PL-C2C2", priority="P1", classes=("docs",)),
        _item("PL-D3D3", priority="P1", classes=("perf",)),
    ]

    assert _has(analyze(band, TODAY).advisories, "outnumbers")


def test_a_multiline_verify_command_is_rejected() -> None:
    """A `verify:` that is not one command is a check nobody can reproduce."""
    item = _item(verify="pytest\nmypy")
    report = analyze([item], TODAY)
    assert any("single-line command" in e for e in report.errors)


def test_not_delegable_holding_a_boolean_is_rejected() -> None:
    """The field holds the reason, not a flag; `not-delegable: no` reads as a grant.

    Someone writing `not-delegable: no` almost certainly means "this is fine to
    delegate", which the field cannot express and must not be read as. Rejecting
    it outright is the only reading that cannot be silently wrong.
    """
    report = analyze([_item(not_delegable="no")], TODAY)
    assert any("holds the reason" in e for e in report.errors)


def test_a_verify_command_without_touches_is_rejected() -> None:
    item = _item(verify="pytest tests/unit/test_x.py", touches=())
    report = analyze([item], TODAY)
    assert any("declares no `touches`" in e for e in report.errors)


def test_a_verify_command_with_touches_is_accepted() -> None:
    item = _item(verify="pytest tests/unit/test_x.py", touches=("tests/unit/test_x.py",))
    assert analyze([item], TODAY).errors == []


CUTOVER = Config(verify_required_from=date(2026, 8, 1))


def test_a_ready_item_must_name_the_command_that_proves_it_done() -> None:
    """The gate is at `ready`, where the item has become a commitment to work."""
    report = analyze([_item(added=date(2026, 8, 2))], TODAY, CUTOVER)

    assert _has(report.errors, "names no `verify:` command")


def test_a_ready_item_may_record_why_no_command_can_prove_it_instead() -> None:
    """Some work is only provable by doing it; saying so is a specification."""
    item = _item(added=date(2026, 8, 2), not_delegable="proving it means cutting a release")

    assert analyze([item], TODAY, CUTOVER).errors == []


def test_a_verify_command_satisfies_the_requirement() -> None:
    item = _item(added=date(2026, 8, 2), verify="uv run pytest")

    assert analyze([item], TODAY, CUTOVER).errors == []


def test_capture_is_never_asked_for_a_verify_command() -> None:
    """Demanding one at capture is how ideas stop being written down."""
    item = _item(status="untriaged", priority="", effort="", added=date(2026, 8, 2))

    assert not _has(analyze([item], TODAY, CUTOVER).errors, "verify")


def test_an_item_still_being_decided_is_not_asked_for_one() -> None:
    """What would prove it done is not answerable while the decision is open."""
    item = _item(
        status="needs-decision",
        added=date(2026, 8, 2),
        body=BRIEF + "\n**Decision needed.** which way\n",
    )

    assert not _has(analyze([item], TODAY, CUTOVER).errors, "verify")


OLD = date(2026, 7, 31)


def test_items_captured_before_the_cutover_are_advised_rather_than_failed() -> None:
    """47 errors on the day the rule lands is a checker nobody runs again."""
    report = analyze([_item(added=OLD)], TODAY, CUTOVER, offered=_offering("PL-K7QX"))

    assert report.errors == []
    assert _has(report.advisories, "names no `verify:` command")


def test_a_grandfathered_item_nobody_is_about_to_be_offered_is_not_raised() -> None:
    """An advisory naming the whole backlog cannot reach zero, so it gets skimmed.

    The cost of that is not the items it names but the next advisory, which is
    then read the same way; `docket check`'s advisories are grooming's only
    channel.
    """
    report = analyze([_item(added=OLD)], TODAY, CUTOVER, offered=_offering())

    assert report.errors == []
    assert report.advisories == []


def test_the_advisory_carries_how_many_are_still_outstanding() -> None:
    """Narrowing it must not hide the size of the set it is drawn from."""
    backlog = [_item(f"PL-000{n}", added=OLD) for n in range(1, 4)]
    report = analyze(backlog, TODAY, CUTOVER, offered=_offering("PL-0001"))

    assert _has(report.advisories, "PL-0001 is next to be offered")
    assert _has(report.advisories, "1 of 3 ready item(s)")


def test_the_advisory_reaches_zero_once_the_offered_items_name_a_command() -> None:
    """The whole point: a normal day ends with nothing pending, backlog or not."""
    backlog = [_item(f"PL-000{n}", added=OLD) for n in (2, 3)]
    started = _item("PL-0001", added=OLD, verify="uv run pytest")
    report = analyze([started, *backlog], TODAY, CUTOVER, offered=_offering("PL-0001"))

    assert report.advisories == []


def test_an_offered_item_held_to_the_rule_is_left_to_the_error() -> None:
    """A post-cutover item is already an error; advising as well would double it."""
    item = _item(added=date(2026, 8, 2))
    report = analyze([item], TODAY, CUTOVER, offered=_offering("PL-K7QX"))

    assert _has(report.errors, "names no `verify:` command")
    assert report.advisories == []


def test_an_offered_item_that_names_a_command_is_not_advised() -> None:
    item = _item(added=OLD, verify="uv run pytest")

    assert analyze([item], TODAY, CUTOVER, offered=_offering("PL-K7QX")).advisories == []


def test_a_project_that_has_not_adopted_the_rule_hears_nothing_about_it() -> None:
    report = analyze([_item(added=date(2026, 8, 2))], TODAY)

    assert report.errors == []
    assert report.advisories == []


def test_a_pull_request_number_is_recorded_bare() -> None:
    errors = _errors(_item(status="done", pr="#71", closed=TODAY))

    assert any("`pr` is '#71'" in e for e in errors)


def _history(*numbers: int) -> PullRequestHistory:
    return PullRequestHistory(numbers=frozenset(numbers))


def test_a_recorded_pull_request_the_default_branch_does_not_name_is_an_error() -> None:
    item = _item(status="done", pr="12", closed=TODAY)
    report = analyze([item], TODAY, history=_history(11, 13))

    assert any("records pull request #12" in e for e in report.errors)


def test_a_pull_request_that_has_merged_is_accepted() -> None:
    item = _item(status="done", pr="12", closed=TODAY)
    report = analyze([item], TODAY, history=_history(11, 12, 13))

    assert report.errors == [] and report.declined == []


def test_a_pull_request_not_yet_merged_is_not_yet_wrong() -> None:
    """An item is closed on the branch that carries it, before its own merge."""
    item = _item(status="done", pr="87", closed=TODAY)

    assert analyze([item], TODAY, history=_history(85, 86)).errors == []


def test_a_checkout_that_cannot_answer_declines_rather_than_failing() -> None:
    """A shallow clone is missing exactly the oldest, best-established work."""
    item = _item(status="done", pr="12", closed=TODAY)
    declined = PullRequestHistory(declined="the checkout is a shallow clone")

    report = analyze([item], TODAY, history=declined)

    assert report.errors == []
    assert report.declined == ["recorded pull requests: the checkout is a shallow clone"]


def test_a_caller_that_did_not_ask_is_told_nothing_either_way() -> None:
    """Only `check` pays for the git read; the rest must not report on one."""
    report = analyze([_item(status="done", pr="12", closed=TODAY)], TODAY)

    assert report.errors == [] and report.declined == []


def test_an_offering_ranked_on_refs_that_went_unread_says_so() -> None:
    """`PL-3576`: `check` was the seventh reader of the flight answer, left out.

    The advisories below name whichever item the ranking put first, and the
    ranking excludes work already in flight - so a ref this checkout could not
    walk can move which item is named, or empty the advisory entirely.
    """
    partial = _offering("PL-K7QX", declined="1 ref could not be compared with origin/main")

    report = analyze([_item()], TODAY, offered=partial)

    assert report.errors == []
    assert report.declined == [
        "whether the grooming advisories name the items `next` will really offer: "
        "1 ref could not be compared with origin/main"
    ]


def test_an_offering_that_read_every_ref_declines_nothing() -> None:
    """The ordinary case, and the one a full clone is always in."""
    report = analyze([_item()], TODAY, offered=_offering("PL-K7QX"))

    assert report.declined == []


# An open item whose own `verify:` command already passes. The reporting half
# is pure - it is handed a `LandedReport` - so these assert what is said about
# a given result; `test_verify.py` covers producing one by running commands.
# An error rather than an advisory since `PL-71P4`.


def _landed(**overrides: object) -> LandedReport:
    base: dict[str, object] = dict(
        passing=("PL-K7QX",),
        shared=(),
        vacuous=(),
        timed_out=(),
        unavailable=(),
        considered=4,
        slow=(),
        typical=0.5,
        elapsed=10.0,
        serial=42.0,
        slowest=SlowCommand("PL-K7QX", 4.0),
        workers=8,
        declined="",
    )
    base.update(overrides)
    # Splatting `dict[str, object]` matches `object` against every field's type; the
    # alternatives are `dict[str, Any]` or an `Unpack[TypedDict]` restating all of
    # `LandedReport`'s fields, both wider than this line-scoped ignore.
    return LandedReport(**base)  # type: ignore[arg-type]


def _advisories(landed: LandedReport | None) -> list[str]:
    return analyze([_item()], TODAY, landed=landed).advisories


def _landed_errors(landed: LandedReport | None) -> list[str]:
    return analyze([_item()], TODAY, landed=landed).errors


def _selects_nothing(landed: LandedReport, offered: OfferedReport) -> list[str]:
    """The selects-no-test advisory is scoped to what `next` would offer."""
    return analyze([_item()], TODAY, landed=landed, offered=offered).advisories


def test_an_item_whose_work_has_landed_is_an_error() -> None:
    """`PL-71P4`: a plain error, affordable because `PL-L9JS` cleaned the store first."""
    messages = _landed_errors(_landed())
    assert _has(messages, "PL-K7QX")
    assert _has(messages, "already passes")
    assert not _has(_advisories(_landed()), "already passes")


def test_a_landed_item_is_reported_as_two_readings_not_a_verdict() -> None:
    # It must not claim the work landed. A passing command is also what a
    # command that does not discriminate looks like, and on this store that
    # was every instance found, so a report saying "landed" would have been
    # wrong seven times out of seven. Being an error changes the force of the
    # sentence, not its honesty: both readings are named, and both are work.
    messages = _landed_errors(_landed())
    assert _has(messages, "Either the work landed")
    assert _has(messages, "does not discriminate")


def test_a_landed_item_names_the_delegation_gate_it_leaves_open() -> None:
    """The consequence is what makes this an error: `docket verify` says ACCEPT."""
    assert _has(_landed_errors(_landed()), "ACCEPT")


def test_a_landed_item_sharing_a_command_is_named_as_proving_nothing() -> None:
    messages = _landed_errors(
        _landed(passing=("PL-K7QX", "PL-B1C2"), shared=("PL-K7QX", "PL-B1C2"))
    )
    assert _has(messages, "share a command with another open item")
    assert _has(messages, "give each its own")


def test_nothing_is_said_when_no_open_item_has_landed() -> None:
    assert _advisories(_landed(passing=(), shared=())) == []
    assert not _has(_landed_errors(_landed(passing=(), shared=())), "already passes")


def test_a_landed_check_that_could_not_run_is_reported_as_not_checked() -> None:
    # The failure this shares with the provenance check: an empty result that
    # means "could not look" must never render as "looked, found nothing".
    report = analyze([_item()], TODAY, landed=LandedReport(declined="no git here"))
    assert report.advisories == []
    assert _has(report.declined, "no git here")


def test_a_caller_that_did_not_ask_about_landed_work_is_told_nothing() -> None:
    report = analyze([_item()], TODAY, landed=None)
    assert report.advisories == []
    assert report.declined == []


# An item whose command could not answer. Reported under "not checked" rather
# than as an advisory, because the run was stopped rather than having found
# something - the per-item form of the refusal `declined` makes for a whole run.


def test_an_item_whose_command_was_killed_is_reported_as_not_checked() -> None:
    report = analyze(
        [_item()], TODAY, landed=_landed(passing=(), timed_out=("PL-K7QX",), limit=120.0)
    )

    assert report.advisories == []
    assert _has(report.declined, "PL-K7QX")
    assert _has(report.declined, "killed at the 120s limit")


def test_a_killed_command_is_reported_even_when_nothing_else_passed() -> None:
    # The ordering that matters: the report is owed whether or not some other
    # item happened to pass, so it cannot sit behind the `passing` guard.
    report = analyze([_item()], TODAY, landed=_landed(passing=(), timed_out=("PL-K7QX",)))

    assert _has(report.declined, "PL-K7QX")


def test_a_killed_command_names_the_limit_the_run_actually_used() -> None:
    # Not the module default: a reader is being told which number to change.
    report = analyze(
        [_item()], TODAY, landed=_landed(passing=(), timed_out=("PL-K7QX",), limit=30.0)
    )

    assert _has(report.declined, "30s limit")


def test_a_killed_command_offers_both_readings_rather_than_a_verdict() -> None:
    report = analyze([_item()], TODAY, landed=_landed(passing=(), timed_out=("PL-K7QX",)))

    assert _has(report.declined, "too slow")
    assert _has(report.declined, "hangs")


def test_an_item_whose_command_was_not_found_is_reported_as_not_checked() -> None:
    report = analyze([_item()], TODAY, landed=_landed(passing=(), unavailable=("PL-K7QX",)))

    assert report.advisories == []
    assert _has(report.declined, "PL-K7QX")
    assert _has(report.declined, "not found by the shell")


def test_nothing_is_said_about_not_checked_items_when_every_command_answered() -> None:
    report = analyze([_item()], TODAY, landed=_landed(timed_out=(), unavailable=()))

    assert report.declined == []


# What a command cost. The pool's wall clock is its slowest member, so one
# heavy `verify:` sets the floor for every `make check` from the day it is
# written, and only the session that wrote it can reconsider it (`PL-VG7G`).


def _slow(landed: LandedReport) -> list[str]:
    return analyze([_item()], TODAY, landed=landed).advisories


def test_a_command_that_dominates_the_run_is_named() -> None:
    messages = _slow(
        _landed(passing=(), slow=(SlowCommand("PL-K7QX", 59.3),), typical=0.7, elapsed=63.2)
    )

    assert _has(messages, "PL-K7QX")
    assert _has(messages, "59s")


def test_the_cost_is_given_against_what_normal_looks_like() -> None:
    # A bare duration cannot be read. The median and the run's own total are
    # what turn it into a number somebody can act on.
    messages = _slow(
        _landed(passing=(), slow=(SlowCommand("PL-K7QX", 59.3),), typical=0.7, elapsed=63.2)
    )

    assert _has(messages, "0.7s median")
    assert _has(messages, "63s for the whole run")


def test_the_advisory_bounds_what_narrowing_would_leave() -> None:
    # The claim it replaced - that the named command "sets the floor" - was
    # true only while the rest of the work fit underneath it, and this store
    # outgrew that: removing the named command measured 28.6s to 23.7s, a
    # sixth of what that sentence invites a reader to expect (`PL-FRGP`). So
    # the run says what narrowing cannot buy, computed rather than asserted.
    messages = _slow(
        _landed(
            passing=(),
            slow=(SlowCommand("PL-K7QX", 27.0),),
            considered=78,
            serial=175.0,
            workers=8,
            elapsed=28.6,
        )
    )

    # (175.0 - 27.0) / 8 workers = 18.5s of work left whatever happens here.
    assert _has(messages, "cannot take the run below about 18s")
    assert _has(messages, "77 commands are 148s of work across 8 workers")


def test_the_bound_is_a_lower_bound_rather_than_a_prediction() -> None:
    # A pool never packs perfectly, so the real run lands above this. Saying
    # what narrowing cannot buy is honest; predicting what it will is what the
    # old wording did wrong, and doing it more precisely would repeat it.
    messages = _slow(
        _landed(passing=(), slow=(SlowCommand("PL-K7QX", 27.0),), serial=175.0, workers=8)
    )

    assert _has(messages, "cannot take the run below")
    assert not _has(messages, "will take")


def test_the_bound_removes_every_named_command_not_only_the_worst() -> None:
    # Narrowing one of two heavy commands leaves the other where it was, so a
    # bound computed against only the worst would not be a bound at all.
    messages = _slow(
        _landed(
            passing=(),
            slow=(SlowCommand("PL-K7QX", 30.0), SlowCommand("PL-B1C2", 30.0)),
            considered=42,
            serial=100.0,
            workers=4,
        )
    )

    # (100.0 - 60.0) / 4 workers = 10s, not (100.0 - 30.0) / 4 = 17.5s.
    assert _has(messages, "cannot take the run below about 10s")
    assert _has(messages, "40 commands are 40s of work")


def test_a_run_that_did_not_say_how_wide_it_was_claims_no_bound() -> None:
    # Dividing by a width nobody recorded would be the invented number this
    # module refuses everywhere else. The sentence stops early instead.
    messages = _slow(
        _landed(passing=(), slow=(SlowCommand("PL-K7QX", 59.3),), serial=175.0, workers=0)
    )

    assert _has(messages, "PL-K7QX")
    assert not _has(messages, "cannot take the run below")


def test_a_command_that_is_the_whole_run_claims_no_bound() -> None:
    # Nothing is left once it is removed, so there is no remainder to divide
    # and "below about 0s" would be a sentence that says nothing.
    messages = _slow(
        _landed(passing=(), slow=(SlowCommand("PL-K7QX", 59.3),), serial=59.3, workers=8)
    )

    assert not _has(messages, "cannot take the run below")


def test_the_advisory_offers_both_outcomes_rather_than_demanding_one() -> None:
    # A coverage item's command is a full-suite run by necessity, so "narrow
    # it" is not always available and accepting a known cost is a real answer.
    messages = _slow(_landed(passing=(), slow=(SlowCommand("PL-K7QX", 59.3),)))

    assert _has(messages, "narrow the command")
    assert _has(messages, "accept the cost")


def test_every_dominating_command_is_named_not_only_the_worst() -> None:
    # Narrowing one of two heavy commands changes nothing: the floor is
    # wherever the other one is.
    messages = _slow(
        _landed(passing=(), slow=(SlowCommand("PL-K7QX", 59.3), SlowCommand("PL-B1C2", 55.0)))
    )

    assert _has(messages, "PL-K7QX")
    assert _has(messages, "PL-B1C2")


def test_nothing_is_said_when_no_command_dominates() -> None:
    assert _slow(_landed(passing=(), slow=())) == []


def test_a_run_that_could_not_execute_says_nothing_about_cost() -> None:
    # Durations from a run that declined would be about the machine, not the
    # store, and the same refusal covers them as covers the findings.
    report = analyze([_item()], TODAY, landed=LandedReport(declined="no toolchain here"))

    assert report.advisories == []


def test_a_caller_that_did_not_ask_is_told_nothing_about_cost() -> None:
    assert analyze([_item()], TODAY, landed=None).advisories == []


# What the run cost, reported every run as a fact rather than as a finding.
# Two comments in `verify.py` carried these figures by hand and both went stale
# inside a fortnight; the reason neither was caught is that a healthy store
# printed no cost at all, so nobody could notice the number had moved
# (`PL-9NKK`).


def _cost(landed: LandedReport | None) -> str:
    return analyze([_item()], TODAY, landed=landed).cost


def test_the_run_reports_what_it_cost() -> None:
    cost = _cost(_landed(considered=78, elapsed=28.8, slowest=SlowCommand("PL-GS5X", 27.4)))

    assert "78 commands" in cost
    assert "28.8s" in cost


def test_the_serial_total_is_reported_beside_the_wall_clock() -> None:
    # Reporting only the wall clock would hide exactly the growth this exists
    # to expose: the pool holds that number flat while the queue climbs.
    assert "175.5s serially" in _cost(_landed(serial=175.5))


def test_the_costliest_command_is_given_against_the_limit_that_bounds_it() -> None:
    # A bare duration cannot be read for the question `LANDED_TIMEOUT` answers,
    # which is how much margin is left before a real command starts being
    # killed and the check starts declining instead of answering.
    cost = _cost(_landed(slowest=SlowCommand("PL-GS5X", 27.4), limit=120.0))

    assert "PL-GS5X" in cost
    assert "27.4s" in cost
    assert "120s limit" in cost


def test_the_costliest_command_is_named_where_no_command_is_an_outlier() -> None:
    # The slow-command advisory fires on a ratio against the median, so it is
    # silent on a store where everything is uniformly heavy - which is the
    # store whose margin against the limit is closing fastest.
    report = analyze(
        [_item()], TODAY, landed=_landed(slow=(), slowest=SlowCommand("PL-GS5X", 27.4))
    )

    assert "PL-GS5X" in report.cost
    assert not any("waits for" in message for message in report.advisories)


def test_the_cost_is_not_reported_as_something_to_resolve() -> None:
    # Nobody is asked to act on it, so it must not sit among the findings that
    # do - that is what makes a line printed every run affordable.
    report = analyze([_item()], TODAY, landed=_landed())

    assert report.cost
    assert not any("serially" in message for message in report.advisories + report.errors)


def test_a_run_that_could_not_execute_reports_no_cost() -> None:
    # Durations from a run that declined would be about the machine rather than
    # the store, and printing them would be the empty-result-as-measured-result
    # error this module exists to refuse.
    assert _cost(LandedReport(declined="no toolchain here")) == ""


def test_a_caller_that_did_not_ask_reports_no_cost() -> None:
    assert _cost(None) == ""


def test_a_store_with_no_command_to_run_reports_no_cost() -> None:
    assert _cost(_landed(considered=0, slowest=None)) == ""


def test_one_command_is_not_reported_as_commands() -> None:
    assert "1 command in" in _cost(_landed(considered=1))


# An open item whose own `verify:` command selects no test. The counterpart to
# the block above and the reason it is needed: pytest exits 5 having collected
# nothing, 5 is not 0, and so the already-passes check reads such a command as
# one that correctly fails. `test_verify.py` covers reading the exit code.


OFFERED = _offering("PL-K7QX")


def test_an_item_whose_command_selects_no_test_is_reported() -> None:
    messages = _selects_nothing(_landed(passing=(), vacuous=("PL-K7QX",)), OFFERED)
    assert _has(messages, "PL-K7QX")
    assert _has(messages, "selects no test")


def test_a_selects_no_test_advisory_is_distinct_from_one_that_fails() -> None:
    # The whole finding: a command that ran nothing must not read as one that
    # failed. The two share an exit status and mean opposite things, so the
    # sentence has to name pytest's own code as the evidence.
    messages = _selects_nothing(_landed(passing=(), vacuous=("PL-K7QX",)), OFFERED)
    assert _has(messages, "exited 5, which is not 0")
    assert not _has(messages, "already passes")


def test_a_selects_no_test_advisory_counts_the_queue_it_searched() -> None:
    # `PL-D2GW`'s was found by hand and nothing said it was the only one, so
    # the scale of the finding travels with the item that can be acted on.
    messages = _selects_nothing(
        _landed(passing=(), vacuous=("PL-K7QX", "PL-B1C2"), considered=9), OFFERED
    )
    assert _has(messages, "1 of 2 open item(s) whose command selects nothing, 9 checked")


def test_a_selects_no_test_advisory_asks_rather_than_condemns() -> None:
    # A selector naming a test the work has yet to write is the shape the
    # docket skill recommends. Only the item's author can tell that from a
    # selector no work will ever satisfy, so the advisory must not decide it.
    messages = _selects_nothing(_landed(passing=(), vacuous=("PL-K7QX",)), OFFERED)
    assert _has(messages, "check that the name each selector matches")


def test_an_item_that_both_passes_and_selects_nothing_cannot_happen_but_reads_apart() -> None:
    # Distinct populations, distinct sentences: one report carrying both must
    # produce two findings, not one merged claim. They now land in different
    # sections - a passing command is an error since `PL-71P4`, a selector
    # matching nothing stays an advisory because only the item's author can
    # say which repair it wants - which separates them further rather than
    # merging them.
    report = analyze(
        [_item()],
        TODAY,
        landed=_landed(passing=("PL-B1C2",), vacuous=("PL-K7QX",)),
        offered=OFFERED,
    )
    assert len([m for m in report.errors if "already passes" in m]) == 1
    assert len([m for m in report.advisories if "selects no test" in m]) == 1


def test_nothing_is_said_when_no_open_item_selects_no_test() -> None:
    assert _selects_nothing(_landed(passing=(), vacuous=()), OFFERED) == []


def test_a_selects_no_test_item_nobody_is_about_to_start_is_not_named() -> None:
    # The whole of this item: eighteen of thirty-one open items select no test
    # because `-k <the name the work will add>` is the recommended shape, and
    # an advisory naming all of them cannot be discharged short of a campaign.
    messages = _selects_nothing(_landed(passing=(), vacuous=("PL-B1C2",)), OFFERED)
    assert messages == []


def test_the_store_wide_total_rides_along_with_the_item_that_is_due() -> None:
    # Narrowing must not lose the count. It is what `PL-5QKT` measured and the
    # reason the check exists, so it travels in the sentence rather than in a
    # line of its own that would fire on every run.
    vacuous = ("PL-K7QX", "PL-B1C2", "PL-C3D4")
    messages = _selects_nothing(_landed(passing=(), vacuous=vacuous, considered=31), OFFERED)
    assert _has(messages, "1 of 3 open item(s)")
    assert not _has(messages, "PL-B1C2")


def test_a_caller_that_asked_for_no_ranking_is_told_nothing_about_selectors() -> None:
    # `offered` is supplied by the commands that put advisories in front of a
    # person. One that did not rank the queue is not owed a ranking-dependent
    # advisory - the same rule the unspecified-command advisory follows.
    assert _advisories(_landed(passing=(), vacuous=("PL-K7QX",))) == []


def test_a_selects_no_test_check_that_could_not_run_says_so_once() -> None:
    # One execution of one set of commands, so one refusal. Two lines would
    # read as two checks having failed to run.
    report = analyze([_item()], TODAY, landed=LandedReport(declined="no toolchain here"))
    assert report.advisories == []
    assert len(report.declined) == 1
    assert _has(report.declined, "no toolchain here")


# --- a closure's `pr`, and when it is owed -----------------------------------
#
# The rule is not "a done item names a pull request" but "a done item that has
# *landed* names one", because the number does not exist until the pull request
# is open. `analyze` is pure here too - it is handed a `ClosureReport` - so what
# these assert is the judgment, not the git reading behind it.


def _closures(
    *landed: str,
    base: str = "origin/main",
    declined: str = "",
    derived: tuple[tuple[str, int], ...] = (),
    shallow: bool | None = False,
) -> ClosureReport:
    """A closure report over a complete checkout unless a case says otherwise.

    `shallow=False` rather than the type's own `None` default: most of these
    cases are about the judgment on a history that *can* be read, and the
    type defaults to claiming nothing, which is right for it and wrong here.
    The cases that turn it on are the last two below.
    """
    return ClosureReport(
        base=base, landed=frozenset(landed), derived=derived, shallow=shallow, declined=declined
    )


def test_a_closure_on_the_base_without_a_pr_is_an_error() -> None:
    # A complete history that names no number is the one state where the way
    # back from the closure to the work genuinely does not exist.
    item = _item(status="done", closed=TODAY)
    report = analyze([item], TODAY, closures=_closures("PL-K7QX"))

    assert any("marked done on `origin/main` but records no `pr`" in e for e in report.errors)


def test_a_closure_whose_merge_commit_names_its_number_is_an_advisory_not_an_error() -> None:
    # The normal shape of a successful merge. The closure travels in the same
    # commit as its work, so it cannot carry a number that does not yet exist,
    # and erroring here turned `main` red on the completion of every item.
    item = _item(status="done", closed=TODAY)
    report = analyze([item], TODAY, closures=_closures("PL-K7QX", derived=(("PL-K7QX", 148),)))

    assert report.errors == []
    assert _has(report.advisories, "recoverable from its merge commit")


def test_the_advisory_names_the_number_and_the_command_that_writes_it() -> None:
    # An advisory a reader has to go and look something up to act on is one
    # they defer, so the exact remedy is in the sentence. It is a command
    # rather than a line to type: retyping a number by hand is what put two
    # sessions on `#229` and `#230` for one identical insertion (`PL-QTSB`).
    item = _item(status="done", closed=TODAY)
    report = analyze([item], TODAY, closures=_closures("PL-K7QX", derived=(("PL-K7QX", 148),)))

    assert _has(report.advisories, "#148")
    assert _has(report.advisories, "`docket record` writes it")


def test_the_advisory_says_to_let_the_write_ride_the_next_commit() -> None:
    # The cost this removed was never the typing; it was the commit the typing
    # needed, and often a pull request with it. An advisory that named the line
    # to write instead of the command would put that cost straight back.
    item = _item(status="done", closed=TODAY)
    report = analyze([item], TODAY, closures=_closures("PL-K7QX", derived=(("PL-K7QX", 148),)))

    assert _has(report.advisories, "ride the commit you are already making")


def test_a_derived_number_for_another_item_does_not_excuse_this_one() -> None:
    # The mapping is per item; borrowing a neighbour's number would record
    # provenance that leads to the wrong work, which is worse than none.
    item = _item(status="done", closed=TODAY)
    report = analyze([item], TODAY, closures=_closures("PL-K7QX", derived=(("PL-B1C2", 148),)))

    assert report.advisories == []
    assert any("records no `pr`" in e for e in report.errors)


def test_a_closure_not_yet_on_the_base_is_accepted() -> None:
    """The window this rule used to hold open.

    An item closed in the same commit as its work has no pull request number
    yet, and demanding one forced the closure into a second push that a merge
    could arrive inside - taking the work and stranding the closure.
    """
    item = _item(status="done", closed=TODAY)
    report = analyze([item], TODAY, closures=_closures())

    assert report.errors == [] and report.declined == []


def test_a_landed_closure_that_records_its_pr_is_accepted() -> None:
    item = _item(status="done", pr="12", closed=TODAY)
    report = analyze([item], TODAY, closures=_closures("PL-K7QX"))

    assert report.errors == [] and report.declined == []


def test_a_checkout_that_cannot_read_the_base_declines_rather_than_guessing() -> None:
    """Neither erroring nor passing: the check did not run, and says so."""
    item = _item(status="done", closed=TODAY)
    report = analyze([item], TODAY, closures=ClosureReport(declined="no default branch here"))

    assert report.errors == []
    assert report.declined == ["closures recording no `pr`: no default branch here"]


def test_a_caller_that_does_not_ask_is_not_told() -> None:
    item = _item(status="done", closed=TODAY)
    report = analyze([item], TODAY)

    assert report.errors == [] and report.declined == []


def test_a_missing_pr_declines_on_a_shallow_clone() -> None:
    """The conflation that turned `main` red twice on 2026-09-01.

    CI checked out at `fetch-depth: 1`, so a closure carrying no `pr` read as
    an advisory on its own merge commit - the one commit present - and became
    an error on the very next merge, when the commit naming its number
    dropped out of the clone. Nothing about the provenance had changed; only
    what the checkout could see had. `PL-99Y4`.
    """
    item = _item(status="done", closed=TODAY)
    report = analyze([item], TODAY, closures=_closures("PL-K7QX", shallow=True))

    assert report.errors == []
    assert _has(report.declined, "PL-K7QX")
    assert _has(report.declined, "shallow clone")
    assert _has(report.declined, "absence proves nothing")


def test_a_missing_pr_declines_when_git_will_not_say_whether_the_clone_is_complete() -> None:
    # `is_shallow` has three answers, and the third forbids inferring anything
    # from absence just as firmly as the second does.
    item = _item(status="done", closed=TODAY)
    report = analyze([item], TODAY, closures=_closures("PL-K7QX", shallow=None))

    assert report.errors == []
    assert _has(report.declined, "git cannot say whether this checkout is complete")


def test_a_shallow_clone_still_advises_where_the_number_was_found() -> None:
    """Truncation qualifies an absence, never a hit.

    A derived number is proof the commit was there to read, so depth cannot
    make it less true - and suppressing it would take the one line that says
    which number is owed and how to write it.
    """
    item = _item(status="done", closed=TODAY)
    report = analyze(
        [item], TODAY, closures=_closures("PL-K7QX", derived=(("PL-K7QX", 148),), shallow=True)
    )

    assert report.errors == [] and report.declined == []
    assert _has(report.advisories, "`docket record` writes it")


def test_an_item_a_merge_removed_is_an_error_carrying_the_command_that_recovers_it() -> None:
    """Data loss, so it fails the store rather than asking a person to notice a note."""
    report = analyze(
        [_item()],
        TODAY,
        lost=LostReport(
            items=(
                LostItem(
                    identifier="PL-K7QX",
                    path="docs/items/PL-K7QX-a-lost-capture.md",
                    blob="1a2b3c4d",
                ),
            ),
            ref="HEAD",
        ),
    )

    assert any("PL-K7QX is in HEAD's history and absent from its tree" in e for e in report.errors)
    assert any("git cat-file -p 1a2b3c4d" in e for e in report.errors)


def test_a_clean_lost_answer_from_a_truncated_clone_is_not_claimed_as_clean() -> None:
    report = analyze([_item()], TODAY, lost=LostReport(ref="HEAD", truncated=True))

    assert report.errors == []
    assert any("history is truncated" in d for d in report.declined)


def test_a_clean_lost_answer_from_a_full_clone_says_nothing() -> None:
    report = analyze([_item()], TODAY, lost=LostReport(ref="HEAD"))

    assert report.errors == []
    assert report.declined == []


def test_a_lost_check_that_could_not_run_is_reported_as_unasked() -> None:
    report = analyze([_item()], TODAY, lost=LostReport(declined="no items found on HEAD"))

    assert report.errors == []
    assert any("items a merge removed: no items found on HEAD" in d for d in report.declined)


def test_a_repeated_front_matter_key_is_an_error() -> None:
    """`PL-BR4G`: the parser keeps the last, so nobody chose the surviving value."""
    errors = _errors(_item(duplicate_fields=("pr",)))

    assert any("appear more than once" in e and "pr" in e for e in errors)


def test_no_duplicate_key_error_on_a_clean_item() -> None:
    assert not any("appear more than once" in e for e in _errors(_item()))


def test_a_class_outside_the_declared_vocabulary_is_an_error() -> None:
    """`PL-MVC2`: `classes` fails open, so an unknown label matches no rule."""
    errors = _errors(_item(classes=("safey",)))

    assert any("not in the declared vocabulary" in e and "safey" in e for e in errors)


def test_a_misspelled_safety_class_is_caught_even_though_the_pin_cannot_fire() -> None:
    """The case the check exists for, asserted end to end.

    `safey` is not in `safety_classes`, so the pin refusing to seat
    safety-critical work below P1 does not fire and cannot. Before this check
    the item sat at P3 with zero errors reported.
    """
    errors = _errors(_item(priority="P3", classes=("safey",)))

    assert any("not in the declared vocabulary" in e for e in errors)
    assert not any("safety-critical work starts at" in e for e in errors)


def test_a_correctly_spelled_safety_class_still_reaches_the_pin() -> None:
    errors = _errors(_item(priority="P3", classes=("safety",)))

    assert not any("not in the declared vocabulary" in e for e in errors)
    assert any("safety-critical work starts at" in e for e in errors)


def test_the_derived_vocabulary_covers_every_class_the_checker_branches_on() -> None:
    """`anticipated` is read by the safety-band exemption and named by no list."""
    assert "anticipated" in Config().vocabulary()
    errors = _errors(
        _item(status="blocked", blocked_by=("PL-BBB2",), classes=("safety", "anticipated")),
        _item("PL-BBB2"),
    )

    assert not any("not in the declared vocabulary" in e for e in errors)
    assert not any("safety-critical work starts at" in e for e in errors)


def test_a_declared_vocabulary_replaces_the_derived_one() -> None:
    config = Config(known_classes=("perf",))

    assert config.vocabulary() == {"perf"}
    assert any(
        "not in the declared vocabulary" in e
        for e in analyze([_item(classes=("safety",), priority="P1")], TODAY, config).errors
    )


def test_one_feature_spelled_two_ways_is_an_error() -> None:
    """`PL-MVC2`: `docket next` groups on the literal string."""
    errors = _errors(
        _item("PL-K7QX", feature="dev-tooling"), _item("PL-BBB2", feature="Dev_Tooling")
    )

    assert any("differ only in case or separator" in e for e in errors)


def test_genuinely_different_features_are_left_alone() -> None:
    errors = _errors(_item("PL-K7QX", feature="dev-tooling"), _item("PL-BBB2", feature="docket"))

    assert not any("differ only in case or separator" in e for e in errors)


# The closing half of the same rule. The dates matter to the point being made:
# `added` sits before `verify_required_from`, so every item below is one the
# opening gate grandfathers and would never ask for a command.
CLOSE_CUTOVER = Config(
    verify_required_from=date(2026, 8, 1), verify_required_at_close_from=date(2026, 8, 20)
)


def test_closing_a_grandfathered_item_demands_the_command_the_ready_gate_never_could() -> None:
    """The point of the closing gate, and the only reason it is keyed on `closed`.

    An item captured before `verify_required_from` is exempt at `ready` and
    stays exempt however long it sits there, so nothing but a grooming
    advisory ever asks it for a command. Closing it is the first moment the
    command can be written having been run, which is the objection that
    earned the exemption - so that is where the exemption lapses.
    """
    item = _item(status="done", added=date(2026, 7, 1), closed=date(2026, 8, 24), pr="48")

    assert _has(analyze([item], TODAY, CLOSE_CUTOVER).errors, "is done but names no `verify:`")


def test_closing_an_item_may_record_why_no_command_can_prove_it() -> None:
    """The same escape the opening gate allows; what is refused is silence."""
    item = _item(
        status="done",
        added=date(2026, 7, 1),
        closed=date(2026, 8, 24),
        pr="48",
        not_delegable="proving it means cutting a release",
    )

    assert not _has(analyze([item], TODAY, CLOSE_CUTOVER).errors, "is done but names no")


def test_an_item_closed_before_the_cutover_is_left_alone() -> None:
    """History is not backfilled, for the reason the grandfathering exists.

    A command written for work that has already merged has nothing left to run
    it against, which is the failure the opening gate's exemption avoids. This
    end of the item's life inherits it.
    """
    item = _item(status="done", added=date(2026, 7, 1), closed=date(2026, 8, 19), pr="48")

    assert not _has(analyze([item], TODAY, CLOSE_CUTOVER).errors, "is done but names no")


def test_a_dropped_item_is_never_asked_what_proved_it() -> None:
    """Nothing was done, so there is nothing a command could have proved."""
    item = _item(
        status="dropped",
        added=date(2026, 7, 1),
        closed=date(2026, 8, 24),
        priority="",
        effort="",
        reason="superseded by PL-AAAA",
    )

    assert not _has(analyze([item], TODAY, CLOSE_CUTOVER).errors, "is done but names no")


def test_the_closing_gate_is_off_when_a_project_declares_no_cutover() -> None:
    """A project that never turned the rule on is not retroactively holding it."""
    off = Config(verify_required_from=date(2026, 8, 1))
    item = _item(status="done", added=date(2026, 7, 1), closed=date(2026, 8, 24), pr="48")

    assert not _has(analyze([item], TODAY, off).errors, "is done but names no")


# --- a closed item's `verify:` is a record, not a live command ---------------
#
# The decision `PL-JZ1D` settled. A closed command stops resolving as a matter
# of course - 14 of the 179 carrying one in this store already do, and every
# one of the 14 is later work correctly consuming what its predecessor
# established. So the rot is not the defect; the helpful repair is, because
# re-pointing the command replaces the one that proved the work with one that
# never ran it. `analyze` is pure here too - it is handed a `RecordReport` -
# so what these assert is the judgment, not the git reading behind it.


def _records(
    *pairs: tuple[str, str], base: str = "origin/main", declined: str = ""
) -> RecordReport:
    return RecordReport(
        base=base,
        records=tuple(BaseRecord(identifier=i, verify=v) for i, v in pairs),
        declined=declined,
    )


def test_rewriting_a_closed_item_s_verify_is_an_error() -> None:
    # The whole finding. `PL-MJ7B` closed carrying a command that named a test
    # `PL-D9WD` deleted hours later; the next session to meet it will want to
    # re-point it, and doing so turns a true record into a false one.
    item = _item(status="done", closed=TODAY, pr="148", verify="pytest new_thing")
    report = analyze([item], TODAY, records=_records(("PL-K7QX", "pytest old_thing")))

    assert _has(report.errors, "record of what was run, not a live command")
    assert _has(report.errors, "pytest old_thing")


def test_the_error_names_reopening_as_the_way_out() -> None:
    # The one legitimate reason to rewrite the field is that the item is not
    # actually done, and saying so in the status is what makes that visible.
    item = _item(status="done", closed=TODAY, pr="148", verify="pytest new_thing")
    report = analyze([item], TODAY, records=_records(("PL-K7QX", "pytest old_thing")))

    assert _has(report.errors, "reopen it")


def test_a_closed_item_keeping_its_recorded_command_passes() -> None:
    item = _item(status="done", closed=TODAY, pr="148", verify="pytest a")
    report = analyze([item], TODAY, records=_records(("PL-K7QX", "pytest a")))

    assert report.errors == []


def test_backfilling_a_command_onto_an_item_closed_without_one_is_an_error() -> None:
    # Items closed before `verify_required_at_close_from` carry no command and
    # are meant to keep carrying none: writing one after the merge means
    # writing a command with nothing left to run it against.
    item = _item(status="done", closed=TODAY, pr="148", verify="pytest a")
    report = analyze([item], TODAY, records=_records(("PL-K7QX", "")))

    assert _has(report.errors, "nothing left to run the command against")


def test_a_reopened_item_may_have_its_command_rewritten() -> None:
    # The escape hatch, and it needs no flag. An item whose status admits the
    # work is unfinished is no longer claiming the old command proved it.
    item = _item(status="ready", verify="pytest new_thing")
    report = analyze([item], TODAY, records=_records(("PL-K7QX", "pytest old_thing")))

    assert report.errors == []


def test_an_item_the_base_records_nothing_for_is_left_alone() -> None:
    # A closure travelling in the same commit as its work is the expected
    # shape, and its command is still the session's to write.
    item = _item(status="done", closed=TODAY, pr="148", verify="pytest a")
    report = analyze([item], TODAY, records=_records())

    assert report.errors == []


def test_a_record_read_that_declined_says_so_rather_than_reporting_clean() -> None:
    item = _item(status="done", closed=TODAY, pr="148", verify="pytest new_thing")
    report = analyze([item], TODAY, records=_records(declined="no default branch to read"))

    assert report.errors == []
    assert _has(report.declined, "recorded `verify:` was rewritten")


def test_a_caller_that_did_not_ask_gets_no_answer() -> None:
    # Every command but `check` passes `None`, and a line saying the read did
    # not run would be an advisory nobody acts on.
    item = _item(status="done", closed=TODAY, pr="148", verify="pytest a")
    report = analyze([item], TODAY)

    assert report.errors == []
    assert not _has(report.declined, "recorded `verify:` was rewritten")


# A scoped replay, and the property that makes it safe to have one: a narrowed
# run must never be readable as a clean whole-store answer (`PL-SDHR`).


def test_a_scoped_run_says_what_it_was_scoped_to() -> None:
    cost = _cost(_landed(considered=1, scope="9 item(s) this branch changed against origin/main"))

    assert "scoped to 9 item(s) this branch changed against origin/main" in cost


def test_a_whole_store_run_claims_no_scope() -> None:
    # The other half of the same property: the unscoped line must not acquire a
    # qualifier that would make a complete answer look partial.
    assert "scoped" not in _cost(_landed(considered=78))


def test_a_scope_holding_no_command_still_says_it_was_scoped() -> None:
    # The case the whole field exists for. A branch that changed no open item
    # runs nothing, so there is no cost to report - and an absent line reads as
    # a store with no commands in it rather than as a run that was narrowed
    # past everything.
    cost = _cost(LandedReport(scope="3 item(s) this branch changed against origin/main"))

    assert "no command to run in 3 item(s) this branch changed" in cost


def test_a_whole_store_run_with_nothing_to_run_still_reports_nothing() -> None:
    # Unscoped, the absent line is the honest one: nothing was narrowed, so
    # there is nothing a reader could mistake.
    assert _cost(LandedReport()) == ""
