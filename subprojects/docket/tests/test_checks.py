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

TODAY = date(2026, 8, 24)
BRIEF = "**Problem.** x\n**Why it matters.** y\n**Done when.** z\n"


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


def test_a_done_item_records_its_pull_request_and_date() -> None:
    """The pull request rather than the commit: a squash discards the commit."""
    messages = _errors(_item(status="done", priority="", effort="", added=None))

    assert _has(messages, "records no `pr`")
    assert _has(messages, "records no `closed` date")


def test_a_done_item_needs_no_commit() -> None:
    """It is kept where it is to hand, but it is not what makes a closure traceable."""
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


def test_items_captured_before_the_cutover_are_advised_rather_than_failed() -> None:
    """47 errors on the day the rule lands is a checker nobody runs again."""
    report = analyze([_item(added=date(2026, 7, 31))], TODAY, CUTOVER)

    assert report.errors == []
    assert _has(report.advisories, "predate the `verify:` requirement")


def test_a_project_that_has_not_adopted_the_rule_hears_nothing_about_it() -> None:
    report = analyze([_item(added=date(2026, 8, 2))], TODAY)

    assert report.errors == []
    assert report.advisories == []


def test_a_pull_request_number_is_recorded_bare() -> None:
    errors = _errors(_item(status="done", commit="abc1234", closed=TODAY, pr="#71"))

    assert any("`pr` is '#71'" in e for e in errors)


def test_a_recorded_pull_request_the_default_branch_does_not_name_is_an_error() -> None:
    item = _item(status="done", commit="abc1234", closed=TODAY, pr="12")
    report = analyze([item], TODAY, merged_prs=frozenset({11, 13}))

    assert any("records pull request #12" in e for e in report.errors)


def test_a_pull_request_that_has_merged_is_accepted() -> None:
    item = _item(status="done", commit="abc1234", closed=TODAY, pr="12")

    assert analyze([item], TODAY, merged_prs=frozenset({11, 12, 13})).errors == []


def test_a_pull_request_not_yet_merged_is_not_yet_wrong() -> None:
    """An item is closed on the branch that carries it, before its own merge."""
    item = _item(status="done", commit="abc1234", closed=TODAY, pr="87")

    assert analyze([item], TODAY, merged_prs=frozenset({85, 86})).errors == []


def test_provenance_is_not_checked_when_git_cannot_be_trusted() -> None:
    """A shallow clone is missing exactly the oldest, best-established work."""
    item = _item(status="done", commit="abc1234", closed=TODAY, pr="12")

    assert analyze([item], TODAY, merged_prs=None).errors == []
    assert analyze([item], TODAY).errors == []
