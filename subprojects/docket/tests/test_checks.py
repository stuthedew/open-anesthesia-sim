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
from docket.vcs import ClosureReport, PullRequestHistory
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


def test_needs_decision_must_state_the_decision() -> None:
    assert _has(_errors(_item(status="needs-decision")), "states no decision to make")


def test_needs_decision_passes_when_it_states_one() -> None:
    assert (
        _errors(_item(status="needs-decision", body=BRIEF + "**Decision needed.** Which?\n")) == []
    )


def test_safety_work_may_not_sit_in_a_low_band() -> None:
    assert _has(_errors(_item(classes=("safety",), priority="P2")), "starts at P0 or P1")


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


# An open item whose own `verify:` command already passes. The advisory half
# is pure - it is handed a `LandedReport` - so these assert what is said about
# a given result; `test_verify.py` covers producing one by running commands.


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
        declined="",
    )
    base.update(overrides)
    # Splatting `dict[str, object]` matches `object` against every field's type; the
    # alternatives are `dict[str, Any]` or an `Unpack[TypedDict]` restating all of
    # `LandedReport`'s fields, both wider than this line-scoped ignore.
    return LandedReport(**base)  # type: ignore[arg-type]


def _advisories(landed: LandedReport | None) -> list[str]:
    return analyze([_item()], TODAY, landed=landed).advisories


def _selects_nothing(landed: LandedReport, offered: OfferedReport) -> list[str]:
    """The selects-no-test advisory is scoped to what `next` would offer."""
    return analyze([_item()], TODAY, landed=landed, offered=offered).advisories


def test_an_item_whose_work_has_landed_is_named_as_a_candidate() -> None:
    messages = _advisories(_landed())
    assert _has(messages, "PL-K7QX")
    assert _has(messages, "already passes")


def test_a_landed_candidate_is_offered_as_two_readings_not_a_verdict() -> None:
    # The advisory must not claim the work landed. A passing command is also
    # what a command that does not discriminate looks like, and on this store
    # that was every instance found, so a report saying "landed" would be
    # wrong eight times out of eight.
    messages = _advisories(_landed())
    assert _has(messages, "either the work landed")
    assert _has(messages, "does not discriminate")


def test_a_landed_candidate_sharing_a_command_is_named_as_proving_nothing() -> None:
    messages = _advisories(_landed(passing=("PL-K7QX", "PL-B1C2"), shared=("PL-K7QX", "PL-B1C2")))
    assert _has(messages, "share a command with another open item")
    assert _has(messages, "give each its own")


def test_nothing_is_said_when_no_open_item_has_landed() -> None:
    assert _advisories(_landed(passing=(), shared=())) == []


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


def test_the_advisory_says_why_one_command_sets_the_floor() -> None:
    messages = _slow(_landed(passing=(), slow=(SlowCommand("PL-K7QX", 59.3),)))

    assert _has(messages, "cannot finish before its slowest member")


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
    # produce two advisories, not one merged claim.
    messages = _selects_nothing(_landed(passing=("PL-B1C2",), vacuous=("PL-K7QX",)), OFFERED)
    assert len([m for m in messages if "already passes" in m]) == 1
    assert len([m for m in messages if "selects no test" in m]) == 1


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


def test_the_advisory_names_the_number_to_write_and_where() -> None:
    # An advisory a reader has to go and look something up to act on is one
    # they defer, so the exact line to write is in the sentence.
    item = _item(status="done", closed=TODAY)
    report = analyze([item], TODAY, closures=_closures("PL-K7QX", derived=(("PL-K7QX", 148),)))

    assert _has(report.advisories, "#148")
    assert _has(report.advisories, "write `pr: 148` into the item")


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
    which number to write.
    """
    item = _item(status="done", closed=TODAY)
    report = analyze(
        [item], TODAY, closures=_closures("PL-K7QX", derived=(("PL-K7QX", 148),), shallow=True)
    )

    assert report.errors == [] and report.declined == []
    assert _has(report.advisories, "write `pr: 148` into the item")
