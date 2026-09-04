"""Tests for milestones, version inference, and the bump."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from docket.model import Item
from docket.release import (
    Readiness,
    already_released,
    is_untagged,
    milestones,
    outstanding_roadmap_edits,
    prepare_bump,
    read_version,
    release_notes,
    suggest_version,
    version_key,
)
from docket.roadmap import Wave, wave

TODAY = date(2026, 8, 24)


def _item(
    identifier: str,
    *,
    status: str = "done",
    milestone: str = "v0.3.0",
    classes: tuple[str, ...] = ("defect",),
    pr: str | None = None,
) -> Item:
    return Item(
        identifier=identifier,
        title=f"Item {identifier}",
        priority="P2",
        effort="S",
        status=status,
        classes=classes,
        touches=(),
        blocked_by=(),
        feature="",
        milestone=milestone,
        added=date(2026, 8, 1),
        closed=TODAY if status == "done" else None,
        commit="abc1234" if status == "done" else "",
        pr=pr if pr is not None else ("48" if status == "done" else ""),
        reason="",
        body="**Problem.** x\n**Why it matters.** y\n**Done when.** z\n",
    )


def test_versions_sort_numerically() -> None:
    assert version_key("v0.10.0") > version_key("v0.9.0")


def test_a_milestone_is_complete_only_when_nothing_is_open() -> None:
    finished = milestones([_item("PL-1111")])["v0.3.0"]
    unfinished = milestones([_item("PL-1111"), _item("PL-2222", status="ready")])["v0.3.0"]

    assert finished.is_complete
    assert not unfinished.is_complete
    assert len(unfinished.outstanding) == 1


def test_new_functionality_is_a_minor_bump() -> None:
    assert (
        suggest_version("0.2.2", [_item("PL-1111", classes=("feature",))], ("feature",)) == "0.3.0"
    )


def test_everything_else_is_a_patch_bump() -> None:
    assert (
        suggest_version("0.2.2", [_item("PL-1111", classes=("defect",))], ("feature",)) == "0.2.3"
    )


def test_a_major_bump_is_never_inferred() -> None:
    """Breaking an interface is a decision, not a fact derivable from a label."""
    assert (
        suggest_version("1.4.2", [_item("PL-1111", classes=("feature",))], ("feature",)) == "1.5.0"
    )


def test_bump_rewrites_the_single_source_and_not_before_it_is_written(tmp_path: Path) -> None:
    """Preparing proves the bump; nothing reaches the file until it is written."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "x"\nversion = "0.2.2"\n', encoding="utf-8")

    prepared = prepare_bump(pyproject, "0.3.0")
    assert read_version(pyproject) == "0.2.2"

    assert prepared.write() == "0.2.2"
    assert read_version(pyproject) == "0.3.0"


def test_release_notes_are_generated_from_the_items() -> None:
    """So the notes cannot claim something the items do not."""
    milestone = milestones([_item("PL-1111"), _item("PL-2222", classes=("perf",))])["v0.3.0"]
    notes = release_notes(milestone, TODAY)

    assert "## v0.3.0 - 2026-08-24" in notes
    assert "PL-1111" in notes and "PL-2222" in notes
    assert "#48" in notes


def test_finished_work_is_unreleased_until_a_version_stamps_it() -> None:
    """The default state of closed work, so nobody has to predict its release."""
    from docket.release import unreleased

    fresh = _item("PL-1111", milestone="")
    shipped = _item("PL-2222", milestone="v0.2.2")

    assert [i.identifier for i in unreleased([fresh, shipped])] == ["PL-1111"]


def test_readiness_reports_what_would_ship_and_what_it_completes() -> None:
    from docket.plan import Feature  # noqa: F401  (documents the coupling)
    from docket.release import readiness

    done = _item("PL-1111", milestone="")
    done = done.__class__(**{**done.__dict__, "feature": "alpha"})
    ready = readiness([done], "0.2.2", ("feature",))

    assert [i.identifier for i in ready.shippable] == ["PL-1111"]
    assert ready.completed_features == ["alpha"]
    assert ready.suggested_version == "0.2.3"


def test_a_completed_feature_is_worth_raising_on_its_own() -> None:
    """Even one item, if it finishes something describable."""
    from docket.release import Readiness

    small = Readiness([_item("PL-1111")], ["alpha"], [], "0.2.2", "0.2.3")
    trivial = Readiness([_item("PL-1111")], [], [], "0.2.2", "0.2.3")

    assert small.is_worth_cutting
    assert not trivial.is_worth_cutting


def test_both_renderers_read_a_real_readiness() -> None:
    """PL-WFJ9: `render.py` took `ready` as `object` and read it through 11
    `type: ignore[attr-defined]` and two `getattr` guards, so nothing exercised
    the coupling between the dataclass and the two lines that print it. These
    are the release lines in the digest and in `status` - the first thing a
    session reads and the answer to "what next" - and a renamed field on
    `Readiness` would have reached both without a checker or a test objecting.
    """
    from docket.checks import Report
    from docket.release import Readiness
    from docket.render import format_digest, format_status

    ready = Readiness(
        shippable=[_item("PL-1111"), _item("PL-2222"), _item("PL-3333")],
        completed_features=["alpha"],
        partial_features=[],
        current_version="0.2.2",
        suggested_version="0.2.3",
    )
    report = Report(items=[_item("PL-4444")])

    digest = format_digest(report, None, ready, None)
    status = format_status(report, ready, None)

    assert "Releasable: 3 finished item(s) since 0.2.2, completing alpha." in digest
    assert "Offer 0.2.3 before taking new work." in digest
    assert "Unreleased: 3 finished item(s) since 0.2.2, completing alpha." in status
    assert "Next version would be 0.2.3." in status


def test_stamping_records_the_release_without_touching_anything_else() -> None:
    from docket.release import stamp

    (stamped,) = stamp([_item("PL-1111", milestone="")], "v0.2.3")

    assert stamped.milestone == "v0.2.3"
    assert stamped.status == "done"
    assert stamped.commit == "abc1234"


def test_a_missing_version_file_reads_as_no_version(tmp_path: Path) -> None:
    """A store can be consulted on its own, away from any project."""
    assert read_version(tmp_path / "absent.toml") == ""


def test_bumping_a_missing_version_still_fails_loudly(tmp_path: Path) -> None:
    """Reading tolerates absence; writing a version that is not there does not."""
    target = tmp_path / "no-version.toml"
    target.write_text('[project]\nname = "x"\n', encoding="utf-8")

    with pytest.raises(ValueError):
        prepare_bump(target, "0.3.0")
    with pytest.raises(OSError):
        prepare_bump(tmp_path / "absent.toml", "0.3.0")


def test_a_shipped_version_with_no_tag_is_reported() -> None:
    assert is_untagged("0.2.5", frozenset({"v0.2.3", "v0.2.4"}))


def test_a_tagged_version_is_not() -> None:
    assert not is_untagged("0.2.5", frozenset({"v0.2.5"}))


def test_a_tag_written_without_its_v_still_counts() -> None:
    assert not is_untagged("0.2.5", frozenset({"0.2.5"}))


def test_a_project_that_has_never_tagged_is_not_taught_to() -> None:
    """Emptiness says the project does not tag, not that every release is missing one."""
    assert not is_untagged("0.2.5", frozenset())


def test_a_version_whose_notes_are_on_the_base_has_already_gone_out() -> None:
    """PL-66FP: the notes file is the direct evidence a maintainer can go and look at."""
    assert already_released(
        "0.3.7", frozenset({"v0.3.6.md", "v0.3.7.md"}), "0.3.6", "pyproject.toml"
    ) == ["docs/releases/v0.3.7.md is on it"]


def test_a_base_already_bumped_to_the_version_has_too() -> None:
    """A release landed by hand, or notes kept somewhere this does not read."""
    assert already_released("0.3.7", frozenset(), "0.3.7", "pyproject.toml") == [
        "its pyproject.toml already reads 0.3.7"
    ]


def test_both_facts_are_reported_when_both_hold() -> None:
    """Two statements a reader can check, rather than one verdict they cannot."""
    assert len(already_released("0.3.7", frozenset({"v0.3.7.md"}), "0.3.7", "pyproject.toml")) == 2


def test_a_leading_v_is_the_same_version_however_it_is_written() -> None:
    assert already_released("v0.3.7", frozenset({"v0.3.7.md"}), "v0.3.7", "pyproject.toml")


def test_a_free_version_is_free_even_where_the_base_has_shipped_others() -> None:
    assert not already_released(
        "0.4.0", frozenset({"v0.3.7.md", "v0.3.8.md"}), "0.3.8", "pyproject.toml"
    )


def test_a_base_a_release_ahead_does_not_report_the_version_being_cut() -> None:
    """Only the number about to be written is the question; ordering is not."""
    assert not already_released("0.3.9", frozenset({"v0.4.0.md"}), "0.4.0", "pyproject.toml")


def test_an_empty_version_reports_nothing_rather_than_matching_an_empty_base() -> None:
    """A store with no version must not read as a duplicate of a base with none."""
    assert not already_released("", frozenset(), "", "pyproject.toml")


def test_notes_cite_the_pull_request_in_preference_to_the_commit() -> None:
    """A squash-merge discards the branch commit; the number outlives it."""
    milestone = milestones([_item("PL-1111")])["v0.3.0"]

    assert " — #48" in release_notes(milestone, TODAY)


def test_notes_fall_back_to_the_commit_for_an_item_closed_before_the_field() -> None:
    milestone = milestones([_item("PL-1111", pr="")])["v0.3.0"]

    assert " — `abc1234`" in release_notes(milestone, TODAY)


# --- what a release leaves the roadmap owing ---------------------------------

ROADMAP = """# Roadmap

## Versioning decision

| Version | Status | Milestone |
| --- | --- | --- |
| v0.2.4 | Completed | The one before. |
| v0.2.5 | Completed / current baseline | The current one. |

## Current baseline: v0.2.5

What it is.
"""


def test_a_roadmap_already_naming_the_new_version_owes_nothing() -> None:
    assert outstanding_roadmap_edits(ROADMAP, "v0.2.5") == []


def test_a_release_with_no_row_of_its_own_is_named() -> None:
    """The v0.2.7 cut: pyproject moved, the table did not, and `make check` broke."""
    owed = outstanding_roadmap_edits(ROADMAP, "0.2.6")

    assert "the version table has no row for v0.2.6" in owed


def test_the_previous_baseline_mark_left_behind_is_named_with_its_line() -> None:
    owed = outstanding_roadmap_edits(ROADMAP, "0.2.6")

    assert any("v0.2.5 row (line 8) is still marked" in statement for statement in owed)


def test_the_baseline_heading_left_behind_is_named_with_its_line() -> None:
    owed = outstanding_roadmap_edits(ROADMAP, "0.2.6")

    assert any("baseline heading (line 10) still names v0.2.5" in statement for statement in owed)


def test_a_row_that_exists_but_carries_no_baseline_mark_is_named() -> None:
    """The half-done edit: the row was added and the mark was not moved."""
    roadmap = ROADMAP.replace(
        "| v0.2.5 | Completed / current baseline | The current one. |",
        "| v0.2.5 | Completed | The current one. |\n| v0.2.6 | Completed | The new one. |",
    )
    owed = outstanding_roadmap_edits(roadmap, "0.2.6")

    assert any('v0.2.6 row (line 9) is not marked "current baseline"' in s for s in owed)


def test_a_missing_baseline_heading_is_named() -> None:
    owed = outstanding_roadmap_edits(
        ROADMAP.replace("## Current baseline: v0.2.5", "## Where"), "0.2.5"
    )

    assert owed == ['there is no "Current baseline: vX.Y.Z" heading']


def test_a_roadmap_with_no_version_table_says_so_rather_than_listing_nothing() -> None:
    """Silence would read as "nothing owed", which is the opposite of the truth."""
    owed = outstanding_roadmap_edits("# Roadmap\n\nNo table here.\n", "0.2.6")

    assert owed == ['there is no version table under "Versioning decision"']


# --- the offer, once the roadmap has had its say -----------------------------

# Two milestones that record a frozen list, and a third step between them whose
# content is the second one's list. That middle row is what makes this fixture
# worth its length: it is the shape the real roadmap uses for Gate 0, and it is
# the only one in which the version to cut and the milestone recording the gate
# are different numbers.
PLAN_ROADMAP = """# Roadmap

## The plan

### The timeline

| # | Step | What it is | Size |
| --- | --- | --- | --- |
| 1 | **v0.2.8 — the workflow works** | Scoped below. | 2 M |
| 2 | **v0.3.0 — the foundation** | Gate 0's list, recorded under v0.4.0. | 3 M |
| 3 | **v0.4.0 — the teachable case** | Scoped below. | 5 M |

## Next release: v0.2.8 - the workflow works

### Goal

Fix the machinery before two long milestones are run through it.

### Debt gate: the frozen list

**Frozen 2026-08-31.** Two entries.

- PL-DDDD (S) A first entry
- PL-BBBB (S) A second entry

### Required scope

The frozen list above is the scope.

### Definition of done

Both entries closed.

### Explicitly out of scope for v0.2.8

The simulator.

## Milestone after next: v0.4.0 - the teachable case

### Goal

Make the model teachable.

### Debt gate: the frozen list

**Frozen 2026-09-01.** One entry, released as v0.3.0 by the recorded exception.

- PL-CCCC (M) Gate 0's only entry

### Required scope

One case.

### Definition of done

The learner can run it.

### Explicitly out of scope for v0.4.0

Forking.
"""

KNOWN_IDS = frozenset({"PL-DDDD", "PL-BBBB", "PL-CCCC"})


def _plan(version: str, closed: frozenset[str] = frozenset()) -> Wave:
    return wave(PLAN_ROADMAP, version, closed, KNOWN_IDS)


def _ready(current: str, suggested: str) -> Readiness:
    return Readiness(
        shippable=[_item("PL-1111"), _item("PL-2222"), _item("PL-3333")],
        completed_features=["alpha"],
        partial_features=[],
        current_version=current,
        suggested_version=suggested,
    )


def test_the_offer_stands_when_no_plan_can_be_read() -> None:
    """A project with no roadmap, or one `wave` declined to parse, is a real state."""
    from docket.release import STANDS, release_offer

    offer = release_offer(_ready("0.2.7", "0.2.8"), None)

    assert (offer.kind, offer.version) == (STANDS, "0.2.8")


def test_no_version_is_offered_while_the_roadmap_still_owns_it() -> None:
    """PL-D2GW: the digest offered 0.2.8 above a beat saying v0.2.8 was unfinished.

    Cutting it would have stamped the finished half of a thirty-seven entry
    milestone with that milestone's own version and tagged it, which no later
    release can take back.
    """
    from docket.release import RESERVED, release_offer

    offer = release_offer(_ready("0.2.7", "0.2.8"), _plan("0.2.7"))

    assert offer.kind == RESERVED
    assert offer.version == "0.2.8"
    assert offer.milestone == "the workflow works"


def test_the_reservation_holds_where_the_gate_is_recorded_under_another_version() -> None:
    """Gate 0's shape: the step to cut is v0.3.0, the gate sits under v0.4.0.

    The collision is with the *step*, not with the section recording the gate,
    so a test reading only the gate's own version would pass here and the
    digest would still offer to ship a half-cleared Gate 0 as "the foundation".
    """
    from docket.release import RESERVED, release_offer

    plan = _plan("0.2.8", frozenset({"PL-DDDD", "PL-BBBB"}))
    offer = release_offer(_ready("0.2.8", "0.3.0"), plan)

    assert (offer.kind, offer.version, offer.milestone) == (RESERVED, "0.3.0", "the foundation")


def test_a_version_the_plan_has_not_claimed_is_offered_as_before() -> None:
    """A patch of unrelated finished work is legitimate while a gate is open."""
    from docket.release import STANDS, release_offer

    offer = release_offer(_ready("0.2.7", "0.2.7.1"), _plan("0.2.7"))

    assert offer.kind == STANDS


def test_the_plan_names_the_version_when_it_is_the_one_asking_for_a_release() -> None:
    """The opposite failure: the number is free, and is the wrong one to cut.

    With Gate 0 clear the beat is "release v0.3.0", while a bump from 0.2.8
    over defect-classed work arrives at 0.2.9. Offering that would ship the
    gate's whole content as a patch and leave v0.3.0 with nothing in it.
    """
    from docket.release import PLANNED, release_offer

    offer = release_offer(_ready("0.2.8", "0.2.9"), _plan("0.2.8", KNOWN_IDS))

    assert (offer.kind, offer.version, offer.milestone) == (PLANNED, "0.3.0", "the foundation")


def test_nothing_is_corrected_when_the_bump_already_agrees_with_the_plan() -> None:
    from docket.release import STANDS, release_offer

    offer = release_offer(_ready("0.2.8", "0.3.0"), _plan("0.2.8", KNOWN_IDS))

    assert (offer.kind, offer.version) == (STANDS, "0.3.0")


def test_the_digest_withholds_the_offer_and_says_which_step_owns_the_version() -> None:
    """The two lines the item is about, read together off one render."""
    from docket.checks import Report
    from docket.render import format_digest

    digest = format_digest(
        Report(items=[_item("PL-4444")]), None, _ready("0.2.7", "0.2.8"), _plan("0.2.7")
    )

    assert "Offer 0.2.8" not in digest
    assert 'No release to offer: the roadmap gives 0.2.8 to "the workflow works"' in digest
    assert "Beat: clear the gate - 2 entries of 2 still open" in digest


def test_the_digest_offers_the_planned_version_over_the_bumps_guess() -> None:
    from docket.checks import Report
    from docket.render import format_digest

    digest = format_digest(
        Report(items=[_item("PL-4444")]), None, _ready("0.2.8", "0.2.9"), _plan("0.2.8", KNOWN_IDS)
    )

    assert "Offer 0.3.0 before taking new work - the version the plan names" in digest
    assert "not the 0.2.9 a bump arrives at" in digest


def test_status_stops_predicting_a_version_the_roadmap_has_spent() -> None:
    """The same wrong statement in the command the queue skill sends a reader to."""
    from docket.checks import Report
    from docket.render import format_status

    status = format_status(
        Report(items=[_item("PL-4444")]), _ready("0.2.7", "0.2.8"), None, _plan("0.2.7")
    )

    assert "Next version would be" not in status
    assert 'Not 0.2.8: the roadmap gives that version to "the workflow works"' in status
