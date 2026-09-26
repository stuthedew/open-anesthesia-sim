"""Tests for milestones, version inference, and the bump."""

from __future__ import annotations

import os
import subprocess
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest

from docket.claims import CUTOVER_MARKER, SESSION_VARIABLE
from docket.cli import main
from docket.model import RELEASE_TRAIN, Item, parse_item, render_item
from docket.release import (
    SPAN_HEADING,
    Readiness,
    already_released,
    below_current,
    is_untagged,
    milestones,
    notes_claims,
    outstanding_roadmap_edits,
    prepare_bump,
    read_version,
    reference,
    release_notes,
    restate_references,
    suggest_version,
    unreferenced,
    unreferenced_by_version,
    version_key,
)
from docket.roadmap import CLEAR, IMPLEMENT, RELEASE, SCOPE, Wave, wave

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


def test_a_resumed_cut_folds_its_own_stamps_back_in() -> None:
    """PL-1MKQ: without this the re-run ships only what the first run missed."""
    from docket.release import unreleased

    fresh = _item("PL-1111", milestone="")
    stamped = _item("PL-2222", milestone="v0.2.6")
    other = _item("PL-3333", milestone="v0.2.5")

    assert [i.identifier for i in unreleased([fresh, stamped, other])] == ["PL-1111"]
    assert [i.identifier for i in unreleased([fresh, stamped, other], "v0.2.6")] == [
        "PL-1111",
        "PL-2222",
    ]


def test_notes_are_read_from_the_bullet_leader_and_not_from_the_whole_line(tmp_path: Path) -> None:
    """An item's title quotes other ids, and every one of them is not a claim.

    Reading every id in the file made 20 of this project's 37 healthy releases
    read as inconsistent, because a title like "PL-2GQW PL-L9JS's reason rests
    on the claim PL-20CQ disproved" names three items and ships one.
    """
    from docket.release import notes_by_version

    notes = tmp_path / "docs" / "releases"
    notes.mkdir(parents=True)
    (notes / "v0.2.6.md").write_text(
        "## v0.2.6 - 2026-08-24\n\n### defect\n\n"
        "- PL-1111 PL-2222's reasoning rests on what PL-3333 disproved - #48\n",
        encoding="utf-8",
    )

    assert notes_by_version(tmp_path) == {"v0.2.6": frozenset({"PL-1111"})}


def test_a_project_with_no_notes_directory_reads_as_having_written_none(tmp_path: Path) -> None:
    from docket.release import notes_by_version

    assert notes_by_version(tmp_path) == {}


def test_a_milestone_no_notes_file_records_is_an_interrupted_cut() -> None:
    from docket.release import unrecorded_milestones

    items = [_item("PL-1111", milestone="v0.2.6")]
    notes = {"v0.2.5": frozenset({"PL-9999"})}

    assert unrecorded_milestones(items, notes, "0.2.5") == ["v0.2.6"]
    assert unrecorded_milestones(items, {"v0.2.6": frozenset({"PL-1111"})}, "0.2.5") == []


def test_a_release_cut_before_the_project_wrote_notes_is_not_judged() -> None:
    """This project's v0.2.2 shipped eleven items before `docs/releases/` existed."""
    from docket.release import unrecorded_milestones

    items = [_item("PL-1111", milestone="v0.2.2")]

    assert unrecorded_milestones(items, {"v0.2.3": frozenset()}, "0.4.15") == []


def test_a_first_release_interrupted_before_any_notes_exist_is_still_found() -> None:
    """The directory offers no floor on a first cut, so the version is the floor."""
    from docket.release import unrecorded_milestones

    items = [_item("PL-1111", milestone="v0.2.6"), _item("PL-2222", milestone="v0.1.0")]

    assert unrecorded_milestones(items, {}, "0.2.5") == ["v0.2.6"]


def test_nothing_is_judged_with_neither_notes_nor_a_version_to_measure_against() -> None:
    from docket.release import unrecorded_milestones

    assert unrecorded_milestones([_item("PL-1111", milestone="v0.2.6")], {}, "") == []


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


def test_versions_are_ordered_as_numbers_not_as_text() -> None:
    """PL-3DN1: 0.10.0 is ahead of 0.9.3, though it sorts below it as a string."""
    assert below_current("0.10.0", "0.9.3", "pyproject.toml") == ""
    assert below_current("v0.9.3", "0.10.0", "pyproject.toml") == (
        "0.9.3 is below 0.10.0, the version pyproject.toml declares"
    )


def test_the_current_version_is_not_below_itself() -> None:
    """PL-3DN1: equal is decided, not left to fall out of the comparison.

    The resume of a cut interrupted after its bump asks for exactly the current
    number and has to get through; a re-cut of a shipped one is left to
    `already_released`, which names its evidence.
    """
    assert below_current("0.2.5", "0.2.5", "pyproject.toml") == ""
    assert below_current("v0.2.5", "0.2.5", "pyproject.toml") == ""


def test_a_number_that_does_not_parse_is_not_compared() -> None:
    """A version field with no version in it stays `prepare_bump`'s to refuse."""
    assert below_current("0.2.0", "", "pyproject.toml") == ""


def test_notes_cite_the_pull_request_in_preference_to_the_commit() -> None:
    """A squash-merge discards the branch commit; the number outlives it."""
    milestone = milestones([_item("PL-1111")])["v0.3.0"]

    assert " — #48" in release_notes(milestone, TODAY)


def test_notes_fall_back_to_the_commit_for_an_item_closed_before_the_field() -> None:
    milestone = milestones([_item("PL-1111", pr="")])["v0.3.0"]

    assert " — `abc1234`" in release_notes(milestone, TODAY)


def test_an_angle_bracket_placeholder_in_a_title_survives_the_rendered_notes() -> None:
    """`PL-PRSF`: `refs/pull/<n>/head` shipped in v0.5.9's notes as `refs/pull//head`.

    The bullet copied the title verbatim, and GitHub read `<n>` as an HTML tag
    and dropped it. CommonMark renders a backslash-escaped `<` as itself, so
    the escaped bullet prints the placeholder; one inside a code span already
    survives, and escaping there would print the backslash instead.
    """
    from docket.release import NOTES_ENTRY_RE

    title = (
        "PL-VV4D's check rests on refs/pull/<n>/head, and `git show <base>:<path>` reads v<version>"
    )
    item = replace(_item("PL-LF2C"), title=title)

    notes = release_notes(milestones([item])["v0.3.0"], TODAY)

    (bullet,) = [line for line in notes.splitlines() if line.startswith("- PL-LF2C ")]
    assert bullet == (
        "- PL-LF2C PL-VV4D's check rests on refs/pull/\\<n>/head, and "
        "`git show <base>:<path>` reads v\\<version> — #48"
    )
    # The readers of a cut's notes still find the bullet's id and its reference.
    assert NOTES_ENTRY_RE.findall(notes) == ["PL-LF2C"]
    assert unreferenced(notes) == ()


def test_a_title_escaped_by_hand_or_holding_no_placeholder_is_left_as_it_stands() -> None:
    """Escaping twice would print a backslash and bring the tag back; nothing else moves."""
    from docket.release import markdown_title

    assert markdown_title("already \\<n> escaped") == "already \\<n> escaped"
    assert markdown_title("a plain title, with `code` and a -> arrow") == (
        "a plain title, with `code` and a -> arrow"
    )
    assert markdown_title("an unclosed ` span <n>") == "an unclosed ` span \\<n>"
    assert markdown_title("``double <n> span`` then <m>") == "``double <n> span`` then \\<m>"


# --- bullets that shipped before their number existed ------------------------
#
# `PL-W7WL`: the cut rendered the notes and `docket record` wrote `pr`
# afterwards, so an item that merged just before a cut shipped a bullet naming
# no pull request, and re-cutting a shipped version to regenerate it is refused.
# 128 of 853 bullets across 22 of this project's releases were in that state
# when this was written, every one recoverable from a number the store by then
# held. Since `PL-HMZZ` the number is on the closure before it merges, so the
# shape recurs only through a closure that reached the base past its check,
# and `docket record N --merge SHA` is what restates the bullet then.

#: One release's notes as the cut wrote them, with `PL-2222` missing the
#: reference its siblings carry. The shape is `release_notes`' own output.
SHIPPED = """## v0.3.0 - 2026-08-24

### defect

- PL-1111 Item PL-1111 — #48
- PL-2222 Item PL-2222
- PL-3333 Item PL-3333 — `abc1234`
"""


def _unreferenced_item(identifier: str) -> Item:
    """A closure carrying neither number nor commit, which is how one lands."""
    return replace(_item(identifier), pr="", commit="")


def test_unreferenced_names_only_the_bullets_with_no_route_back() -> None:
    assert unreferenced(SHIPPED) == ("PL-2222",)


def test_a_title_quoting_another_id_is_not_read_as_that_item_s_bullet() -> None:
    """Same anchoring as `NOTES_ENTRY_RE`, and for the same reason it exists."""
    text = "- PL-1111 Why PL-9999's claim fails\n"

    assert unreferenced(text) == ("PL-1111",)


def test_restating_appends_the_number_the_store_now_records() -> None:
    restated, repaired = restate_references(SHIPPED, {"PL-2222": _item("PL-2222")})

    assert repaired == ("PL-2222",)
    assert "- PL-2222 Item PL-2222 — #48" in restated


def test_a_restated_bullet_is_byte_for_byte_what_the_cut_would_have_written() -> None:
    """The property the repair rests on, and why `reference` is one function.

    A line appended afterwards and a line generated at the cut have to be
    indistinguishable, or the notes carry two spellings of one fact and the
    next reader cannot tell a repaired release from a clean one.
    """
    item = _item("PL-1111")
    as_cut = release_notes(milestones([item])["v0.3.0"], TODAY)
    without = release_notes(milestones([_unreferenced_item("PL-1111")])["v0.3.0"], TODAY)

    assert restate_references(without, {"PL-1111": item})[0] == as_cut


def test_restating_leaves_a_bullet_that_already_cites_its_pull_request() -> None:
    """Idempotent, which is what lets this sit in `make fix` without a diff."""
    restated, repaired = restate_references(SHIPPED, {"PL-1111": _item("PL-1111")})

    assert repaired == ()
    assert restated == SHIPPED


def test_restating_leaves_the_title_exactly_as_it_shipped() -> None:
    """A bullet records the title of the day it went out; retitling is not a defect.

    So the repair is matched on the reference's shape rather than against the
    item's current title. An equality test would refuse the append here and go
    on refusing it forever, which is an advisory that fires every run and
    changes no decision.
    """
    text = "- PL-2222 The title this shipped under\n"
    renamed = replace(_item("PL-2222"), title="What it is called now")

    restated, repaired = restate_references(text, {"PL-2222": renamed})

    assert repaired == ("PL-2222",)
    assert restated == "- PL-2222 The title this shipped under — #48\n"


def test_a_bullet_whose_item_records_nothing_is_left_alone() -> None:
    """This supplies a fact or it does nothing; there is no third thing to write."""
    restated, repaired = restate_references(SHIPPED, {"PL-2222": _unreferenced_item("PL-2222")})

    assert repaired == ()
    assert restated == SHIPPED


def test_a_bullet_naming_an_item_the_store_has_dropped_is_left_alone() -> None:
    restated, repaired = restate_references(SHIPPED, {})

    assert repaired == ()
    assert restated == SHIPPED


def test_reference_prefers_the_pull_request_and_falls_back_to_the_commit() -> None:
    assert reference(_item("PL-1111")) == " — #48"
    assert reference(_item("PL-1111", pr="")) == " — `abc1234`"
    assert reference(_unreferenced_item("PL-1111")) == ""


def test_unreferenced_by_version_reports_only_the_releases_with_a_gap(tmp_path: Path) -> None:
    (tmp_path / "docs" / "releases").mkdir(parents=True)
    (tmp_path / "docs" / "releases" / "v0.3.0.md").write_text(SHIPPED, encoding="utf-8")
    (tmp_path / "docs" / "releases" / "v0.2.9.md").write_text(
        "- PL-4444 Item PL-4444 — #12\n", encoding="utf-8"
    )

    assert unreferenced_by_version(tmp_path) == {"v0.3.0": ("PL-2222",)}


def test_a_project_that_writes_no_notes_reports_nothing_rather_than_raising(tmp_path: Path) -> None:
    assert unreferenced_by_version(tmp_path) == {}


# --- the pointer section, which is not a claim -------------------------------

POINTED = (
    SHIPPED
    + f"\n{SPAN_HEADING}\n\n"
    + "`git describe --contains` resolves these commits to v0.3.0, but this cut did\n"
    + "not stamp them, so each is described in the release named beside it.\n\n"
    + "- PL-4444 - #52 - described in v0.3.1\n"
)


def test_notes_claims_splits_a_file_into_its_claims_and_its_pointer() -> None:
    """Both halves back, so a writer can put the second one down byte for byte."""
    claims, pointer = notes_claims(POINTED)

    assert claims + pointer == POINTED
    assert pointer.startswith(SPAN_HEADING)
    assert "PL-4444" not in claims


def test_a_file_with_no_pointer_section_is_all_claims() -> None:
    assert notes_claims(SHIPPED) == (SHIPPED, "")


def test_a_pointed_item_is_not_read_as_shipped_by_the_release_pointing_at_it(
    tmp_path: Path,
) -> None:
    """`PL-P669`: the pointer names work *another* cut stamped, which is its content.

    Read as a claim it is the exact shape `_check_release_notes` reports as the
    notes and the store disagreeing - so every pointer would redden the tree it
    was added to repair.
    """
    from docket.release import notes_by_version

    notes = tmp_path / "docs" / "releases"
    notes.mkdir(parents=True)
    (notes / "v0.3.0.md").write_text(POINTED, encoding="utf-8")

    assert notes_by_version(tmp_path) == {"v0.3.0": frozenset({"PL-1111", "PL-2222", "PL-3333"})}


def test_a_pointed_bullet_is_not_reported_as_missing_a_reference(tmp_path: Path) -> None:
    """It carries the number already, in the grammar the pointer uses rather than the cut's."""
    notes = tmp_path / "docs" / "releases"
    notes.mkdir(parents=True)
    (notes / "v0.3.0.md").write_text(POINTED, encoding="utf-8")

    assert unreferenced_by_version(tmp_path) == {"v0.3.0": ("PL-2222",)}


def test_restating_leaves_the_pointer_section_byte_for_byte() -> None:
    """Otherwise `make fix` appends a second reference to a line that has one.

    `- PL-4444 - #52 - described in v0.3.1` ends in prose rather than in
    `REFERENCED_RE`'s tail, so a restate reading the whole file would write
    `... - described in v0.3.1 — #52` and the pointer would stop being one.
    """
    restated, repaired = restate_references(POINTED, {"PL-4444": _item("PL-4444")})

    assert repaired == ()
    assert restated.endswith("- PL-4444 - #52 - described in v0.3.1\n")


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


#: The table above with a release train beside it: a shipped milestone, a
#: section-bearing `—` row numbered as the next patch, and a milestone ahead.
PORT_CUT_ROADMAP = ROADMAP.replace(
    "## Current baseline: v0.2.5",
    """## The plan

### The timeline

| # | Step | What it is | Size |
| --- | --- | --- | --- |
| 1 | **v0.2.4 — the one before** | Shipped. | — |
| — | **v0.2.6 — the interface port** | Scoped below. | 1 L |
| 2 | **v0.3.0 — the foundation** | Not yet scoped. | — |

## v0.2.6 - the interface port

### Goal

Move the dashboard.

## Current baseline: v0.2.5""",
)


def test_a_cut_reaching_a_milestone_section_is_named() -> None:
    """`PL-Y1L0`: a patch cut at the port's own number, and one cut past it.
    The hand-off named the table row, the baseline mark and the baseline
    heading, and said nothing about the milestone whose number the cut had
    taken - so the plan was stepped past the port with no statement to act
    on. A number the cut has exactly reached is ambiguous from the file alone,
    and the statement says which edit each reading owes."""
    reached = outstanding_roadmap_edits(PORT_CUT_ROADMAP, "0.2.6")
    passed = outstanding_roadmap_edits(PORT_CUT_ROADMAP, "0.2.7")

    (at_number,) = [s for s in reached if s.startswith("v0.2.6 — the interface port (")]
    assert "timeline line " in at_number and ", section line " in at_number
    assert "which the project has reached with no v0.2.6 release" in at_number
    assert "its table row is owed if this release is that milestone" in at_number

    (behind,) = [s for s in passed if s.startswith("v0.2.6 — the interface port (")]
    assert "which the project has passed with no v0.2.6 release" in behind
    assert "owe a number the project has not passed" in behind

    # The shipped milestone is in the table and the one ahead is ahead: neither
    # is named, and a cut the table already records owes nothing at all.
    assert not any("v0.2.4" in s or "v0.3.0" in s for s in reached + passed)
    assert outstanding_roadmap_edits(PORT_CUT_ROADMAP, "0.2.5") == []


#: `PORT_CUT_ROADMAP` with the port scoped in full - a frozen list, a Required
#: scope, a definition of done and an out-of-scope list - so `wave` gives it a
#: beat: `release v0.2.6` once both ids are closed, `implement` while the
#: Required scope is still open.
SCOPED_PORT_ROADMAP = PORT_CUT_ROADMAP.replace(
    "Move the dashboard.\n",
    """Move the dashboard.

### Debt gate: the frozen list

**Frozen 2026-08-25.** One entry.

- PL-GT01 (M) The frozen entry

### Required scope

- The port (queue item PL-PT01).

### Definition of done

Nothing a learner can do is lost.

### Explicitly out of scope for v0.2.6

A restyle.
""",
)
SCOPED_PORT_IDS = frozenset({"PL-GT01", "PL-PT01"})


def test_the_reached_number_statement_reads_the_plan() -> None:
    """`PL-YS9F`: the plan read before the bump decides which edit is owed.

    At the hand-off the version table lacks the cut's own row by construction,
    so a milestone number the cut has exactly reached reads two ways from the
    file: this release is that milestone, or a patch has taken its number. The
    plan computed before the bump knows which - a `release` beat asking for the
    cut's version is the first, any other beat the second - and without one
    the statement still names both. Nothing else the hand-off states moves.
    """
    releasing = wave(SCOPED_PORT_ROADMAP, "0.2.5", SCOPED_PORT_IDS, SCOPED_PORT_IDS, {})
    building = wave(SCOPED_PORT_ROADMAP, "0.2.5", frozenset({"PL-GT01"}), SCOPED_PORT_IDS, {})
    assert (releasing.beat, releasing.release_version) == (RELEASE, (0, 2, 6))
    assert building.beat == IMPLEMENT

    def owed(plan: Wave | None) -> tuple[str, list[str]]:
        statements = outstanding_roadmap_edits(SCOPED_PORT_ROADMAP, "0.2.6", plan)
        (at_number,) = [s for s in statements if s.startswith("v0.2.6 — the interface port (")]
        return at_number, [s for s in statements if s != at_number]

    released, rest = owed(releasing)
    patched, patched_rest = owed(building)
    undecided, undecided_rest = owed(None)

    reached = "which the project has reached with no v0.2.6 release in the version table: "
    assert reached + "the plan was releasing it, so this release is that milestone" in released
    assert released.endswith("and its table row is owed")
    assert reached + "the plan was not releasing it, so a patch has taken its number" in patched
    assert patched.endswith("the row and its section owe a new one")
    assert undecided.endswith(
        reached + "its table row is owed if this release is that milestone, and a new number"
        " if it is not"
    )
    assert rest == patched_rest == undecided_rest
    assert "the version table has no row for v0.2.6" in rest


def test_a_release_beat_asking_for_another_number_is_the_second_reading() -> None:
    """Only a `release` beat asking for the cut's own number is the first reading.

    The beat's number is replaced by hand, so the rule is shown reading the
    number rather than the word: a plan releasing some other version says this
    cut took the port's number. And a number the cut has passed is the one
    statement no plan changes.
    """
    releasing = wave(SCOPED_PORT_ROADMAP, "0.2.5", SCOPED_PORT_IDS, SCOPED_PORT_IDS, {})
    elsewhere = replace(releasing, release_version=(0, 3, 0))

    reached = outstanding_roadmap_edits(SCOPED_PORT_ROADMAP, "0.2.6", elsewhere)
    passed = outstanding_roadmap_edits(SCOPED_PORT_ROADMAP, "0.2.7", releasing)

    (at_number,) = [s for s in reached if s.startswith("v0.2.6 — the interface port (")]
    assert "the plan was not releasing it, so a patch has taken its number" in at_number
    (behind,) = [s for s in passed if s.startswith("v0.2.6 — the interface port (")]
    assert behind.endswith("the row and its section owe a number the project has not passed")


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
    return wave(PLAN_ROADMAP, version, closed, KNOWN_IDS, {})


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


def test_digest_and_status_render_one_reserved_verdict() -> None:
    """One verdict, one arrangement, both surfaces - which is the assertion
    neither surface's own test can make.

    `format_status` carried a second independent branch on `offer.kind` and a
    refusal of its own wording, so a change to the digest's left the survey
    printing the old one and nothing failed. Both are checked against the same
    expected clause here rather than against a literal each, because a literal
    each is exactly what the defect was (`PL-C6XD`).

    Only the pointer differs, which is the one part each surface is entitled
    to: the digest prints the beat directly beneath and says so, the survey
    does not and names the command that would print it.
    """
    from docket.checks import Report
    from docket.render import format_digest, format_status

    report = Report(items=[_item("PL-4444")])
    ready, plan = _ready("0.2.7", "0.2.8"), _plan("0.2.7")
    refusal = (
        'No release to offer: the roadmap gives 0.2.8 to "the workflow works", which is unfinished'
    )

    digest = format_digest(report, None, ready, plan)
    status = format_status(report, ready, None, plan)

    assert f"{refusal} - the beat below is what is due." in digest
    assert f"{refusal} - `docket wave` for what is due." in status
    assert "Next version would be" not in status


def test_the_digest_names_the_branch_already_cutting_instead_of_offering_a_release() -> None:
    """PL-66FP: the offer is where a duplicate release starts, so it stops here.

    Refusing at `docket release` alone leaves the second session having
    already raised it and been approved; the owner is then asked twice for one
    release.
    """
    from docket.checks import Report
    from docket.render import format_digest
    from docket.vcs import BranchCut, CutsInFlight

    digest = format_digest(
        Report(items=[_item("PL-4444")]),
        None,
        _ready("0.2.8", "0.2.9"),
        _plan("0.2.8", KNOWN_IDS),
        cuts=CutsInFlight(branches=(BranchCut(ref="origin/claude/a", versions=("0.2.9",)),)),
    )

    assert "A release is already being cut on origin/claude/a (v0.2.9)" in digest
    assert "Offer" not in digest


def test_this_checkouts_own_cut_does_not_withhold_the_digest_offer() -> None:
    from docket.checks import Report
    from docket.render import format_digest
    from docket.vcs import BranchCut, CutsInFlight

    digest = format_digest(
        Report(items=[_item("PL-4444")]),
        None,
        _ready("0.2.8", "0.2.9"),
        _plan("0.2.8", KNOWN_IDS),
        cuts=CutsInFlight(branches=(BranchCut(ref="claude/mine", versions=("0.2.9",), mine=True),)),
    )

    assert "already being cut" not in digest
    assert "Offer 0.3.0" in digest


def test_the_digest_offers_the_planned_version_over_the_bumps_guess() -> None:
    from docket.checks import Report
    from docket.render import format_digest

    digest = format_digest(
        Report(items=[_item("PL-4444")]), None, _ready("0.2.8", "0.2.9"), _plan("0.2.8", KNOWN_IDS)
    )

    assert "Offer 0.3.0 before taking new work - the version the plan names" in digest
    assert "not the 0.2.9 a bump arrives at" in digest


# --- what `status` says about the plan (`PL-BZCM`) ---------------------------

#: A roadmap whose current milestone records a gate *and* a scope of its own,
#: which is the arrangement that makes every mark reachable: an entry on the
#: frozen list, an id the same milestone's `Required scope` names and clearing
#: the gate comes before, an id a later milestone places, and an id no section
#: holds at all.
MARKED_ROADMAP = """# Roadmap

## The plan

### The timeline

| # | Step | What it is | Size |
| --- | --- | --- | --- |
| 1 | **v0.2.8 — the workflow works** | Scoped below. | 2 M |
| 2 | **v0.4.0 — the teachable case** | Scoped below. | 5 M |

## Next release: v0.2.8 - the workflow works

### Goal

Fix the machinery first.

### Debt gate: the frozen list

**Frozen 2026-08-31.** One entry.

- PL-GT01 (S) The frozen entry

### Required scope

- The run becomes teachable (queue item PL-SC02).

### Definition of done

Both closed.

### Explicitly out of scope for v0.2.8

The simulator.

## Milestone after next: v0.4.0 - the teachable case

### Goal

Make the model teachable.

### Required scope

- One case (queue item PL-LT03).

### Definition of done

The learner can run it.

### Explicitly out of scope for v0.4.0

Forking.
"""

#: `PL-NN04` is deliberately absent from every section above, which is what
#: makes it the unmarked case the legend has to define.
MARKED_IDS = frozenset({"PL-GT01", "PL-SC02", "PL-LT03", "PL-NN04"})


def _marked_plan() -> Wave:
    """The beat at v0.2.7: v0.2.8's gate is open, so the beat is to clear it."""
    return wave(MARKED_ROADMAP, "0.2.7", frozenset(), MARKED_IDS, {})


def _open(identifier: str, feature: str = "", status: str = "ready") -> Item:
    from docket.model import parse_item

    return parse_item(
        "---\n"
        f"id: {identifier}\n"
        f"title: Work on {identifier}\n"
        "priority: P2\n"
        "effort: S\n"
        f"status: {status}\n"
        + (f"feature: {feature}\n" if feature else "")
        + ("closed: 2026-08-24\npr: 48\n" if status == "done" else "")
        + "---\n\n**Problem.** x\n**Why it matters.** y\n**Done when.** z\n"
    )


def _feature_rows(*identifiers: str) -> str:
    """`format_status` over one open item per id, each alone in its own feature.

    Every feature is given a closed item too, so that it counts as `underway`
    and prints the `next:` row this item is about - a feature with nothing done
    lands in `Not started`, which names no item at all.
    """
    from docket.checks import Report
    from docket.render import format_status

    items: list[Item] = []
    for index, identifier in enumerate(identifiers):
        items.append(_open(identifier, feature=f"feature-{index}"))
        items.append(_open(f"PL-DN0{index}", feature=f"feature-{index}", status="done"))
    return format_status(Report(items=items), None, None, _marked_plan())


def test_status_marks_the_next_item_the_open_gate_names() -> None:
    """`PL-BZCM`: the survey the queue skill says to lead with listed the current
    step's work in the same undifferentiated column as everything else."""
    status = _feature_rows("PL-GT01")

    assert "next: PL-GT01 [gate]" in status
    assert "Plan: clearing the debt gate recorded under v0.2.8 — the workflow works." in status
    assert "[gate] on its frozen list" in status


def test_status_marks_the_anchors_own_scope_as_coming_after_the_gate() -> None:
    """A different statement from "a later milestone names this": `Required
    scope` is this milestone's own, and clearing its gate comes first."""
    status = _feature_rows("PL-SC02")

    assert "next: PL-SC02 [after the gate]" in status
    assert "[after the gate] in its Required scope, which clearing the gate comes before" in status


def test_status_names_the_later_milestone_that_places_an_item() -> None:
    status = _feature_rows("PL-LT03")

    assert "next: PL-LT03 [v0.4.0]" in status
    assert "[v0.4.0] placed by that later milestone" in status


def test_status_defines_the_unmarked_row_rather_than_leaving_it_silent() -> None:
    """`PL-J790`'s point, met with a legend rather than a sentence per row: an
    unmarked row has to be distinguishable from one nobody looked at."""
    status = _feature_rows("PL-GT01", "PL-NN04")

    assert "next: PL-NN04 Work on PL-NN04" in status
    assert "PL-NN04 [" not in status
    assert "unmarked, no section of the roadmap places the id" in status


def test_status_marks_the_items_outside_any_feature_too() -> None:
    """They are listed work like any other, and marking only the feature rows
    would make an unmarked entry here read as unplaced when it is on the gate."""
    from docket.checks import Report
    from docket.render import format_status

    status = format_status(
        Report(items=[_open("PL-GT01"), _open("PL-NN04")]), None, None, _marked_plan()
    )

    assert "P2 PL-GT01 [gate]" in status
    assert "P2 PL-NN04 Work on" in status


def test_status_says_nothing_about_the_plan_when_there_is_none() -> None:
    """A project with no roadmap is a legitimate state, and a legend defining
    marks that were never drawn is noise in every one of those sessions."""
    from docket.checks import Report
    from docket.render import format_status

    status = format_status(Report(items=[_open("PL-GT01")]), None, None, None)

    assert "Plan:" not in status
    assert "[gate]" not in status


# --- the release a finished milestone leaves (`PL-KD98`) --------------------

#: The live shape: a milestone recording a gate **and** a `Required scope` of
#: its own, with the project standing on the patch-track row beneath it. Both
#: v0.4.0 and v0.5.0 are this shape, and it is the one no arrangement could
#: reach a `release` beat for.
GATED_SCOPE_ROADMAP = """# Roadmap

## The plan

### The timeline

| # | Step | What it is | Size |
| --- | --- | --- | --- |
| 1 | **v0.3.0 — the foundation** | Gate 0's frozen list. | 2 M |
| — | **v0.3.x — a readability pass** | A patch, not a milestone. | — |
| 2 | **v0.4.0 — the teachable case** | Scoped below. | 5 M |

## Completed: v0.3.0 - the foundation

### Goal

Clear the backlog.

### Definition of done

Every entry on the list below is closed.

### Explicitly out of scope for v0.3.0

New capability.

## Next milestone: v0.4.0 - the teachable case

### Goal

Make the model teachable.

### Debt gate: the frozen list

**Frozen 2026-08-25.** One entry.

- PL-GT01 (M) The frozen entry

### Required scope

- A displayed clinical unit (queue item PL-SC02).

### Definition of done

The learner can run one case.

### Explicitly out of scope for v0.4.0

Forking.
"""

#: The same roadmap with the patch track removed, which puts the step on the
#: v0.4.0 milestone row itself - the arrangement in which the bump's own
#: arithmetic arrives at a number the roadmap has already spent, and so the one
#: that produced the wrong digest line the item was filed on.
ON_THE_MILESTONE_ROW = GATED_SCOPE_ROADMAP.replace(
    "| — | **v0.3.x — a readability pass** | A patch, not a milestone. | — |\n", ""
)

GATED_SCOPE_IDS = frozenset({"PL-GT01", "PL-SC02"})

#: The same roadmap with the milestone's `Required scope` subsection removed,
#: which is v0.2.8's shape: the frozen list is the whole of the section's
#: content, so clearing it finishes the milestone. `_release_due` used to say
#: so only where the project stood on that milestone's own row, and here it
#: stands on the patch track beneath the milestone before it (`PL-J45M`).
GATE_ONLY_ROADMAP = GATED_SCOPE_ROADMAP.replace(
    """### Required scope

- A displayed clinical unit (queue item PL-SC02).

""",
    "",
)


def _gated(version: str, closed: frozenset[str], roadmap: str = GATED_SCOPE_ROADMAP) -> Wave:
    return wave(roadmap, version, closed, GATED_SCOPE_IDS, {})


def test_the_offer_names_the_milestone_the_beat_releases_not_the_patch_track() -> None:
    """The patch-track row carries `(0, 3, -1)`, a track marker rather than a
    number anything can be cut at - so an offer read off `step` falls back to
    the bump's arithmetic and contradicts the beat printed beside it."""
    from docket.release import PLANNED, release_offer

    plan = _gated("0.3.0", GATED_SCOPE_IDS)
    offer = release_offer(_ready("0.3.0", "0.3.1"), plan)

    assert plan.beat == RELEASE and plan.subject == "v0.4.0 — the teachable case"
    assert (offer.kind, offer.version, offer.milestone) == (PLANNED, "0.4.0", "the teachable case")


def test_the_digest_offers_the_release_the_beat_asks_for() -> None:
    """The two lines are read one above the other, so they have to agree."""
    from docket.checks import Report
    from docket.render import format_digest

    plan = _gated("0.3.0", GATED_SCOPE_IDS)
    digest = format_digest(Report(items=[_item("PL-4444")]), None, _ready("0.3.0", "0.3.1"), plan)

    assert "Offer 0.4.0 before taking new work - the version the plan names" in digest
    assert "No release to offer" not in digest


def test_the_digest_stops_declining_a_release_for_a_finished_milestone() -> None:
    """`PL-KD98`'s "Done when", stated directly.

    The step is the v0.4.0 row and the bump arrives at 0.4.0, which is the
    arrangement that produced `No release to offer: the roadmap gives 0.4.0 to
    "the teachable case", which is unfinished` while twelve of thirteen scope
    entries were done. The milestone is finished here, so nothing declines.
    """
    from docket.checks import Report
    from docket.render import format_digest

    plan = _gated("0.3.0", GATED_SCOPE_IDS, roadmap=ON_THE_MILESTONE_ROW)
    digest = format_digest(Report(items=[_item("PL-4444")]), None, _ready("0.3.9", "0.4.0"), plan)

    assert plan.step is not None and plan.step.version == (0, 4, 0)
    assert "No release to offer" not in digest
    assert "Offer 0.4.0 before taking new work." in digest


def test_the_digest_still_declines_while_the_scope_is_unfinished() -> None:
    """The decline was always the right answer; only its grounds were missing.
    With the scope open it stands, and now rests on a counted fact."""
    from docket.checks import Report
    from docket.render import format_digest

    plan = _gated("0.3.0", frozenset({"PL-GT01"}), roadmap=ON_THE_MILESTONE_ROW)
    digest = format_digest(Report(items=[_item("PL-4444")]), None, _ready("0.3.9", "0.4.0"), plan)

    assert plan.beat == IMPLEMENT
    assert 'No release to offer: the roadmap gives 0.4.0 to "the teachable case"' in digest


def test_the_reservation_reads_the_milestone_the_beat_names_not_only_the_step() -> None:
    """`PL-6T4L`: the branch `PL-KD98` fixed for the release beat and not here.

    The project stands on the patch-track row, whose `(0, 3, -1)` is a track
    marker rather than a number anything can be cut at - so a guard comparing
    the bump against `step` alone matches nothing, and the offer stands on the
    very version the roadmap has given to the milestone the beat is asking to
    implement.
    """
    from docket.release import RESERVED, release_offer

    plan = _gated("0.3.0", frozenset({"PL-GT01"}))
    offer = release_offer(_ready("0.3.9", "0.4.0"), plan)

    assert plan.beat == IMPLEMENT
    assert plan.step is not None and plan.step.version == (0, 3, -1)
    assert (offer.kind, offer.version, offer.milestone) == (RESERVED, "0.4.0", "the teachable case")


def test_the_reservation_holds_while_the_gate_under_that_milestone_is_open() -> None:
    """The same carrier one beat earlier, where the number is spoken for twice
    over: the gate that guards v0.4.0 is open *and* its scope is untouched."""
    from docket.release import RESERVED, release_offer

    plan = _gated("0.3.0", frozenset())
    offer = release_offer(_ready("0.3.9", "0.4.0"), plan)

    assert plan.beat == CLEAR
    assert (offer.kind, offer.version, offer.milestone) == (RESERVED, "0.4.0", "the teachable case")


def test_the_digest_stops_offering_the_version_of_the_milestone_it_says_to_implement() -> None:
    """The two lines of one digest the item was filed on, read together.

    `Offer 0.4.0 before taking new work` sat directly above a beat counting
    that same milestone's scope as unfinished - and the offer is the only line
    in the digest that tells a session to do something.
    """
    from docket.checks import Report
    from docket.render import format_digest

    plan = _gated("0.3.0", frozenset({"PL-GT01"}))
    digest = format_digest(Report(items=[_item("PL-4444")]), None, _ready("0.3.9", "0.4.0"), plan)

    assert "Offer 0.4.0 before taking new work" not in digest
    assert 'No release to offer: the roadmap gives 0.4.0 to "the teachable case"' in digest
    assert "implement v0.4.0 — the teachable case" in digest


def test_a_finished_gate_only_milestone_is_offered_as_the_release_it_is() -> None:
    """`PL-J45M`: a gate-only section whose frozen list has cleared, reached
    from the patch track beneath it. `_release_due` compared positions and fell
    through to `implement`, so this guard carried an exemption for a beat that
    counted nothing - "which is unfinished" would otherwise have been printed
    against a milestone that was done. The arrangement is read from the row
    now and the beat is `release`, which the offer answers on its own terms;
    the exemption is gone with the fall-through."""
    from docket.release import PLANNED, STANDS, release_offer

    plan = _gated("0.3.0", frozenset({"PL-GT01"}), roadmap=GATE_ONLY_ROADMAP)

    assert plan.beat == RELEASE and plan.own_scope is None
    assert plan.gate is not None and plan.gate.is_clear
    assert plan.release_version == (0, 4, 0)
    offer = release_offer(_ready("0.3.9", "0.4.0"), plan)
    assert (offer.kind, offer.version) == (STANDS, "0.4.0")
    corrected = release_offer(_ready("0.3.9", "0.3.10"), plan)
    assert (corrected.kind, corrected.version) == (PLANNED, "0.4.0")


#: `GATED_SCOPE_ROADMAP` with a section-bearing `—` row between the patch track
#: and the gated milestone - the Qt port's shape after `PL-RKWB` moved it ahead
#: of v0.5.0 and numbered it as a patch.
PORTED_ROADMAP = GATED_SCOPE_ROADMAP.replace(
    "| 2 | **v0.4.0 — the teachable case** |",
    "| — | **v0.3.5 — the interface port** | Scoped below. | 1 L |\n"
    "| 2 | **v0.4.0 — the teachable case** |",
).replace(
    "## Next milestone: v0.4.0 - the teachable case",
    """## v0.3.5 - the interface port

### Goal

Move the dashboard.

### Required scope

- The chart (queue item PL-PT03).

### Definition of done

Parity.

### Explicitly out of scope for v0.3.5

Compare mode.

## Next milestone: v0.4.0 - the teachable case""",
)


def test_the_reservation_reads_the_row_the_beat_anchors_on_before_the_gated_milestone() -> None:
    """`PL-188T`'s arrangement, answered by `PL-FWJF` binding the beat's
    milestone to the port's section: a patch bump arriving at the port's own
    number is reserved while the port's scope is open, where reading the gated
    milestone alone offered it as free. The guard is unchanged - it reads
    `plan.milestone`, and `wave` now binds that to the row the timeline puts
    first."""
    from docket.release import RESERVED, release_offer

    plan = wave(PORTED_ROADMAP, "0.3.0", frozenset({"PL-GT01"}), GATED_SCOPE_IDS | {"PL-PT03"}, {})
    offer = release_offer(_ready("0.3.0", "0.3.5"), plan)

    assert plan.beat == IMPLEMENT
    assert plan.milestone is not None and plan.milestone.version == (0, 3, 5)
    assert (offer.kind, offer.version, offer.milestone) == (RESERVED, "0.3.5", "the interface port")


def test_a_version_named_ahead_of_the_current_one_is_reserved() -> None:
    """`PL-188T`: a patch cut mid-port, offered the port's own number as free.

    The port has both a timeline row and a section, and neither of the two
    objects the guard used to read reached it: the project stands on the patch
    track, and the beat is the open gate recorded under the milestone *after*
    the port, so `wave` binds `step = v0.3.x` and `milestone = v0.4.0`. This is
    the arrangement measured on `origin/main` at `0.4.25`, where a `0.4.26`
    bump - the Qt port's own number - came back `stands`.

    Distinct from the port test below it, which reaches the same section
    through `plan.milestone` once the gate is clear. Here the gate is open, so
    that binding is on something else entirely and the reservation rests on the
    roadmap naming the number rather than on anything `wave` bound.
    """
    from docket.release import RESERVED, release_offer

    plan = wave(PORTED_ROADMAP, "0.3.0", frozenset(), GATED_SCOPE_IDS | {"PL-PT03"}, {})
    offer = release_offer(_ready("0.3.0", "0.3.5"), plan)

    assert plan.beat == CLEAR
    assert plan.step is not None and plan.step.version == (0, 3, -1)
    assert plan.milestone is not None and plan.milestone.version == (0, 4, 0)
    assert (offer.kind, offer.version, offer.milestone) == (RESERVED, "0.3.5", "the interface port")


#: `GATED_SCOPE_ROADMAP` with its gated milestone shipped and a further one
#: placed on the timeline but not yet scoped, a boundary marker between them.
#: That is the state every milestone passes through between being placed and
#: being scoped, and `ROADMAP.md` had two rows in it the day this was found.
UNSCOPED_AHEAD_ROADMAP = GATED_SCOPE_ROADMAP.replace(
    "| 2 | **v0.4.0 — the teachable case** | Scoped below. | 5 M |",
    "| 2 | **v0.4.0 — the teachable case** | Scoped below. | 5 M |\n"
    "| — | **MVP complete** | A learner can run one case. | — |\n"
    "| 3 | **v0.5.0 — the schematic** | Not scoped yet, and has no section. | — |",
)


def test_a_timeline_row_with_no_section_reserves_its_version() -> None:
    """`PL-VFD8`: the milestone that is placed but not yet scoped.

    `wave` has no section to bind, so `plan.milestone` is `None`; the row the
    project stands on is the boundary marker, which carries no version at all.
    Both of the objects the guard used to read hold nothing, and the digest
    offered the number the roadmap had already given to "the schematic" -
    `Offer 0.5.0 before taking new work` above a beat asking for that same
    milestone to be *scoped*.

    The marker row is what makes it this defect rather than the one before it:
    without it the project would stand on the v0.5.0 row and the old `step`
    carrier would have caught the collision.
    """
    from docket.release import RESERVED, release_offer

    plan = wave(UNSCOPED_AHEAD_ROADMAP, "0.4.0", GATED_SCOPE_IDS, GATED_SCOPE_IDS, {})
    offer = release_offer(_ready("0.4.0", "0.5.0"), plan)

    assert plan.beat == SCOPE
    assert plan.milestone is None
    assert plan.step is not None and plan.step.version is None
    assert (offer.kind, offer.version, offer.milestone) == (RESERVED, "0.5.0", "the schematic")


def test_the_digest_declines_the_number_of_a_milestone_it_says_to_scope() -> None:
    """The two contradicting lines of the digest this was filed on, read
    together: a release offer for the very version the beat under it is asking
    somebody to go and scope."""
    from docket.checks import Report
    from docket.render import format_digest

    plan = wave(UNSCOPED_AHEAD_ROADMAP, "0.4.0", GATED_SCOPE_IDS, GATED_SCOPE_IDS, {})
    digest = format_digest(Report(items=[_item("PL-4444")]), None, _ready("0.4.0", "0.5.0"), plan)

    assert "Offer 0.5.0 before taking new work" not in digest
    assert 'No release to offer: the roadmap gives 0.5.0 to "the schematic"' in digest


def test_the_reserved_set_carries_every_version_the_plan_names_ahead() -> None:
    """What makes the guard terminate, stated on its own: the answer is the
    roadmap's list of unspent numbers rather than whichever object `wave`
    bound. The patch track is absent by kind - `v0.3.x` promises no particular
    number, so it reserves none - and so is everything at or below the current
    version, which is released and which no bump can suggest."""
    plan = wave(UNSCOPED_AHEAD_ROADMAP, "0.4.0", GATED_SCOPE_IDS, GATED_SCOPE_IDS, {})

    assert [(entry.version, entry.name) for entry in plan.reserved] == [
        ((0, 5, 0), "the schematic")
    ]

    early = wave(UNSCOPED_AHEAD_ROADMAP, "0.3.0", GATED_SCOPE_IDS, GATED_SCOPE_IDS, {})

    assert [(entry.version, entry.name) for entry in early.reserved] == [
        ((0, 4, 0), "the teachable case"),
        ((0, 5, 0), "the schematic"),
    ]


def test_wave_prints_every_reserved_version_and_not_only_the_colliding_one() -> None:
    """`reserved` did not occur in `render.py` at all, so the only reserved
    version a session could see was whichever one a bump happened to land on,
    named in prose by the refusal above. The guard's answer was legible and the
    evidence behind it was not, which is what `PL-SYG4` needs to reason about a
    patch cut on a track running alongside a reserved milestone (`PL-C6XD`).

    Withheld rather than printed empty where the roadmap names nothing ahead:
    the current version is the last row `PLAN_ROADMAP` has, so there is no
    number to report and a bare label would report one anyway.
    """
    from docket.render import format_wave

    ahead = wave(UNSCOPED_AHEAD_ROADMAP, "0.3.0", GATED_SCOPE_IDS, GATED_SCOPE_IDS, {})

    assert "Reserved  0.4.0, 0.5.0 - spent by ROADMAP.md, nearest first" in format_wave(ahead)
    assert "Reserved" not in format_wave(_plan("0.4.0", KNOWN_IDS))


def test_wave_reports_the_scope_split_once_the_gate_is_clear() -> None:
    from docket.render import format_wave

    printed = format_wave(_gated("0.3.0", frozenset({"PL-GT01"})))

    assert "Scope     the Required scope of v0.4.0 — the teachable case (1 id)" in printed
    assert "0 closed, 1 open" in printed
    assert "PL-SC02" in printed
    assert "implement v0.4.0 — the teachable case - its gate is clear, 0 of 1 " in printed


def test_wave_says_the_scope_closed_when_it_reports_a_release() -> None:
    from docket.render import format_wave

    printed = format_wave(_gated("0.3.0", GATED_SCOPE_IDS))

    assert "1 closed, 0 open" in printed
    assert "its gate is clear and all 1 Required scope id have closed" in printed


def test_wave_withholds_the_scope_split_while_the_gate_is_open() -> None:
    """A few lines read beside the digest rather than studied: while the beat is
    `clear`, the gate block above already says what is due and the scope is work
    the step has not reached."""
    from docket.render import format_wave

    printed = format_wave(_gated("0.3.0", frozenset()))

    assert "clear the gate" in printed
    assert "Scope" not in printed


# --- the release train: filing and cutting under a claim (`PL-331V`) ----------
#
# A cut's own commits carry no item id, so the release guard reads the release
# item's instead: whoever claims an item carrying `resource: release-train`
# holds the train, and `new --resource` and `release` refuse a second holder.
# Real git, dated explicitly, because what is under test is which claims
# `claims.holdings` reads as live at the instant the command names.

TRAIN_T0 = datetime(2026, 9, 1, 12, 0, tzinfo=UTC)
TRAIN_NOW = (TRAIN_T0 + timedelta(hours=2)).isoformat()


@pytest.fixture
def _no_session(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the session running the suite from deciding `mine` for any claim read here."""
    monkeypatch.delenv(SESSION_VARIABLE, raising=False)


def _train_item(identifier: str, status: str = "untriaged", resource: str = RELEASE_TRAIN) -> str:
    """A release item as `new --resource` files it, or closed where `status` says so."""
    closed = "closed: 2026-09-01\ncommit: abc1234\n" if status == "done" else ""
    stamp = f"resource: {resource}\n" if resource else ""
    return (
        f"---\nid: {identifier}\ntitle: Cut the release\nstatus: {status}\n{stamp}"
        f"added: 2026-08-01\n{closed}---\n\n**Problem.** Cut the release\n"
    )


class _TrainRepo:
    """A tagged v0.2.5 with one finished item on `main`, and branches that claim release items.

    Every commit is dated, and the base sits a month before `TRAIN_T0`, so a
    lease is live exactly when a test's claim says it is.
    """

    def __init__(self, root: Path) -> None:
        self.root = root
        self.items = root / "items"
        self.items.mkdir(parents=True)
        self.git("-c", "init.defaultBranch=main", "init", "-q")
        for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
            self.git("config", name, value)
        self.commit(
            "base",
            when=TRAIN_T0 - timedelta(days=30),
            files={
                "items/PL-D1D1-shipped.md": _train_item("PL-D1D1", "done", resource=""),
                "pyproject.toml": '[project]\nversion = "0.2.5"\n',
                CUTOVER_MARKER: "# the claim reader\n",
            },
        )
        self.git("tag", "v0.2.5")

    def git(self, *args: str, when: datetime | None = None) -> str:
        env = None
        if when is not None:
            env = os.environ | {
                "GIT_AUTHOR_DATE": when.isoformat(),
                "GIT_COMMITTER_DATE": when.isoformat(),
            }
        done = subprocess.run(
            ["git", *args], cwd=self.root, check=True, capture_output=True, text=True, env=env
        )
        return done.stdout

    def commit(self, message: str, *, when: datetime, files: dict[str, str] | None = None) -> None:
        for path, text in (files or {}).items():
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", message, when=when)

    def hold(self, branch: str, identifier: str, *, when: datetime = TRAIN_T0) -> None:
        """Branch from `main`, file a release item and claim it, as release mode does."""
        self.git("checkout", "-q", "-b", branch, "main")
        self.commit(
            f"{identifier}: file the release",
            when=when,
            files={f"items/{identifier}-cut.md": _train_item(identifier)},
        )
        self.commit(f"{identifier}: start\n\nClaim: {identifier} {branch}", when=when)

    def run(self, *argv: str) -> int:
        return main([*argv, "--items", str(self.items), "--now", TRAIN_NOW])

    def version(self) -> str:
        return (self.root / "pyproject.toml").read_text(encoding="utf-8")


@pytest.mark.usefixtures("_no_session")
def test_filing_a_release_item_is_refused_while_another_branch_holds_the_release_train(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`PL-MFM4`: two release items filed for one release, each passing every guard.

    Refused at filing, with nothing written, so there is no second item to
    discard at the merge.
    """
    repo = _TrainRepo(tmp_path / "repo")
    repo.hold("claude/pl-tr4n-cut", "PL-TR4N")
    repo.git("checkout", "-q", "-b", "claude/second", "main")
    before = sorted(path.name for path in repo.items.iterdir())

    code = repo.run("new", "--resource", RELEASE_TRAIN, "--no-fetch", "Cut v0.2.6")

    out = capsys.readouterr().out
    assert code == 3
    assert "another session is preparing a release" in out
    assert "claude/pl-tr4n-cut holds the release train through PL-TR4N" in out
    assert sorted(path.name for path in repo.items.iterdir()) == before


@pytest.mark.usefixtures("_no_session")
def test_filing_a_second_release_item_on_the_branch_holding_the_release_train_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _TrainRepo(tmp_path / "repo")
    repo.hold("claude/pl-tr4n-cut", "PL-TR4N")
    before = sorted(path.name for path in repo.items.iterdir())

    code = repo.run("new", "--resource", RELEASE_TRAIN, "--no-fetch", "Cut v0.2.6")

    assert code == 3
    assert "this branch already holds the release train through PL-TR4N" in (
        capsys.readouterr().out
    )
    assert sorted(path.name for path in repo.items.iterdir()) == before


@pytest.mark.usefixtures("_no_session")
def test_filing_a_release_item_nobody_holds_stamps_the_release_train(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _TrainRepo(tmp_path / "repo")
    repo.git("checkout", "-q", "-b", "claude/first", "main")

    assert repo.run("new", "--resource", RELEASE_TRAIN, "--no-fetch", "Cut v0.2.6") == 0

    identifier = capsys.readouterr().out.split()[0]
    [filed] = repo.items.glob(f"{identifier}-*.md")
    assert parse_item(filed.read_text(encoding="utf-8")).resource == RELEASE_TRAIN


@pytest.mark.parametrize(
    ("extra", "said"),
    [(("--no-git",), "`--no-git` asks git nothing"), (("Two", "Three"), "was given 3 titles")],
)
def test_a_release_train_filing_that_cannot_be_checked_is_a_usage_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], extra: tuple[str, ...], said: str
) -> None:
    repo = _TrainRepo(tmp_path / "repo")

    assert repo.run("new", "--resource", RELEASE_TRAIN, "Cut v0.2.6", *extra) == 2

    assert said in capsys.readouterr().out
    assert sorted(path.name for path in repo.items.iterdir()) == ["PL-D1D1-shipped.md"]


@pytest.mark.usefixtures("_no_session")
def test_a_cut_is_refused_on_a_rival_release_train_holder_that_has_cut_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Both sessions filed before either pushed a claim; the one ordering second stops here."""
    repo = _TrainRepo(tmp_path / "repo")
    repo.hold("claude/pl-tr4n-cut", "PL-TR4N")
    repo.hold("claude/pl-bcdf-cut", "PL-BCDF", when=TRAIN_T0 + timedelta(hours=1))

    assert repo.run("release", "0.2.6", "--no-fetch") == 1

    out = capsys.readouterr().out
    assert "A release is already being prepared on a branch nothing has merged" in out
    assert (
        "claude/pl-tr4n-cut holds the release train for PL-TR4N (claimed 2026-09-01), "
        "and has cut nothing yet"
    ) in out
    assert 'version = "0.2.5"' in repo.version()


@pytest.mark.usefixtures("_no_session")
def test_a_cut_proceeds_where_head_holds_the_release_train_first(tmp_path: Path) -> None:
    """The other side of the same order: the branch claiming first has no rival."""
    repo = _TrainRepo(tmp_path / "repo")
    repo.hold("claude/pl-bcdf-cut", "PL-BCDF", when=TRAIN_T0 + timedelta(hours=1))
    repo.hold("claude/pl-tr4n-cut", "PL-TR4N")

    repo.git("checkout", "-q", "claude/pl-bcdf-cut")
    assert repo.run("release", "0.2.6", "--no-fetch") == 1
    repo.git("checkout", "-q", "claude/pl-tr4n-cut")
    assert repo.run("release", "0.2.6", "--no-fetch") == 0
    assert 'version = "0.2.6"' in repo.version()


@pytest.mark.usefixtures("_no_session")
def test_the_hand_off_reads_the_plan_from_before_the_bump(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`PL-YS9F`, end to end: a cut at the port's own number is the port.

    Before the bump the plan's beat is `release v0.2.6`; after it the version
    file reads 0.2.6 and the plan has moved on to scoping v0.3.0, which would
    read the same cut as a patch that took the port's number. So the hand-off
    names the first reading only if `cmd_release` read the plan first.
    """
    repo = _TrainRepo(tmp_path / "repo")
    repo.commit(
        "scope the port",
        when=TRAIN_T0 - timedelta(days=29),
        files={
            "ROADMAP.md": SCOPED_PORT_ROADMAP,
            **{
                f"items/{ident}-scoped.md": _train_item(ident, "done", resource="")
                for ident in SCOPED_PORT_IDS
            },
        },
    )
    repo.hold("claude/pl-tr4n-cut", "PL-TR4N")

    assert repo.run("release", "0.2.6", "--no-fetch") == 0

    out = capsys.readouterr().out
    assert "Stale in ROADMAP.md, and owed by hand:" in out
    assert "the plan was releasing it, so this release is that milestone" in out
    assert "the plan was not releasing it" not in out


@pytest.mark.usefixtures("_no_session")
def test_a_cut_is_refused_where_head_holds_no_release_train_claim(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _TrainRepo(tmp_path / "repo")
    repo.git("checkout", "-q", "-b", "claude/unclaimed", "main")

    assert repo.run("release", "0.2.6", "--no-fetch") == 1

    out = capsys.readouterr().out
    assert "Cannot cut v0.2.6 here: this branch holds no claim on the release train." in out
    assert 'bin/docket new --resource release-train "Cut v0.2.6 from the 1 items' in out
    assert "bin/docket set ID --resource release-train" in out
    assert 'version = "0.2.5"' in repo.version()


@pytest.mark.usefixtures("_no_session")
def test_a_dry_run_warns_that_head_holds_no_release_train_and_still_shows_the_notes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _TrainRepo(tmp_path / "repo")
    repo.git("checkout", "-q", "-b", "claude/unclaimed", "main")

    assert repo.run("release", "0.2.6", "--no-fetch", "--dry-run") == 0

    out = capsys.readouterr().out
    assert "this branch holds no claim on the release train" in out
    assert "PL-D1D1" in out
    assert "Dry run: nothing was changed." in out


@pytest.mark.usefixtures("_no_session")
def test_a_release_item_closed_on_this_branch_has_released_the_release_train(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _TrainRepo(tmp_path / "repo")
    repo.hold("claude/pl-tr4n-cut", "PL-TR4N")
    repo.commit(
        "PL-TR4N: close it",
        when=TRAIN_T0 + timedelta(hours=1),
        files={"items/PL-TR4N-cut.md": _train_item("PL-TR4N", "done")},
    )

    assert repo.run("release", "0.2.6", "--no-fetch", "--dry-run") == 0

    out = capsys.readouterr().out
    assert "PL-TR4N is done on this branch, which released its claim on the train" in out


@pytest.mark.usefixtures("_no_session")
@pytest.mark.parametrize("ending", ["yield", "close"])
def test_a_rival_whose_release_train_claim_ended_no_longer_refuses(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], ending: str
) -> None:
    """A `Yield:` or the item closed on its own branch releases the train, so a later claim cuts."""
    repo = _TrainRepo(tmp_path / "repo")
    repo.hold("claude/pl-tr4n-cut", "PL-TR4N")
    later = TRAIN_T0 + timedelta(minutes=30)
    if ending == "yield":
        repo.commit("PL-TR4N: stop\n\nYield: PL-TR4N claude/pl-tr4n-cut", when=later)
    else:
        repo.commit(
            "PL-TR4N: close it",
            when=later,
            files={"items/PL-TR4N-cut.md": _train_item("PL-TR4N", "dropped")},
        )
    repo.hold("claude/pl-bcdf-cut", "PL-BCDF", when=TRAIN_T0 + timedelta(hours=1))

    assert repo.run("release", "0.2.6", "--no-fetch") == 0

    assert "release train" not in capsys.readouterr().out
    assert 'version = "0.2.6"' in repo.version()


def test_the_digest_names_a_release_train_holder_that_has_cut_nothing_yet() -> None:
    """The offer stops as soon as a release item is claimed, not only once it is cut."""
    from docket.checks import Report
    from docket.render import format_digest
    from docket.vcs import BranchCut, CutsInFlight

    digest = format_digest(
        Report(items=[_item("PL-4444")]),
        None,
        _ready("0.2.8", "0.2.9"),
        _plan("0.2.8", KNOWN_IDS),
        cuts=CutsInFlight(
            branches=(
                BranchCut(
                    ref="origin/claude/pl-tr4n-cut",
                    versions=(),
                    cut=date(2026, 9, 1),
                    item="PL-TR4N",
                ),
            )
        ),
    )

    assert (
        "PL-TR4N holds the release train, nothing cut yet (origin/claude/pl-tr4n-cut); "
        "do not offer another until it merges."
    ) in digest
    assert "already being cut" not in digest
    assert "Offer" not in digest


def test_a_resource_outside_the_known_set_is_a_check_error() -> None:
    """`Holdings.holder` matches exactly, so a misspelt resource would hold nothing, silently."""
    from docket.checks import analyze

    misspelt = parse_item(_train_item("PL-TR4N", resource="release_train"), "PL-TR4N-cut.md")
    stamped = parse_item(_train_item("PL-TR4N"), "PL-TR4N-cut.md")

    [error] = [e for e in analyze([misspelt], TODAY).errors if "resource" in e]
    assert "resource 'release_train' is not one of release-train" in error
    assert not [e for e in analyze([stamped], TODAY).errors if "resource" in e]


def test_the_resource_field_round_trips_after_touches() -> None:
    item = replace(_item("PL-TR4N", status="ready", milestone=""), resource=RELEASE_TRAIN)
    item = replace(item, touches=("a.py",))

    text = render_item(item)

    assert parse_item(text).resource == RELEASE_TRAIN
    assert "touches: a.py\nresource: release-train\n" in text
    assert render_item(parse_item(text)) == text


@pytest.mark.usefixtures("_no_session")
def test_a_rival_whose_branch_this_one_merged_still_refuses_the_cut(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The train is mine by branch name, so a contained cut does not hide its holder.

    `cuts_in_flight` marks a cut `HEAD` contains as `mine`; before this, the
    rival's entry was deduplicated against it and then dropped with it, so
    `release` cut while `new` refused on the same branch.
    """
    repo = _TrainRepo(tmp_path / "repo")
    repo.hold("claude/x", "PL-XXXX")
    repo.commit(
        "PL-XXXX: cut",
        when=TRAIN_T0 + timedelta(minutes=10),
        files={"docs/releases/v0.2.6.md": "# v0.2.6\n"},
    )
    repo.hold("claude/y", "PL-YYYY", when=TRAIN_T0 + timedelta(hours=1))
    repo.git("merge", "-q", "--no-edit", "claude/x", when=TRAIN_T0 + timedelta(hours=1))

    assert repo.run("release", "0.2.7", "--no-fetch") == 1

    out = capsys.readouterr().out
    assert "claude/x is cutting v0.2.6" in out
    assert 'version = "0.2.5"' in repo.version()
    assert repo.run("new", "--resource", RELEASE_TRAIN, "--no-fetch", "Cut v0.2.7") == 3


@pytest.mark.usefixtures("_no_session")
def test_a_rival_already_listed_for_its_cut_is_named_once(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _TrainRepo(tmp_path / "repo")
    repo.hold("claude/pl-tr4n-cut", "PL-TR4N")
    repo.commit(
        "PL-TR4N: cut",
        when=TRAIN_T0 + timedelta(minutes=10),
        files={"docs/releases/v0.2.6.md": "# v0.2.6\n"},
    )
    repo.git("checkout", "-q", "-b", "claude/second", "main")

    assert repo.run("release", "0.2.6", "--no-fetch", "--dry-run") == 0

    out = capsys.readouterr().out
    assert out.count("claude/pl-tr4n-cut") == 1
    assert "claude/pl-tr4n-cut is cutting v0.2.6" in out


@pytest.mark.usefixtures("_no_session")
def test_a_lapsed_release_train_claim_on_this_branch_is_revived_not_filed_again(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A second release item on one branch is the thing filing refuses, lapsed or not."""
    repo = _TrainRepo(tmp_path / "repo")
    repo.hold("claude/x", "PL-XXXX", when=TRAIN_T0 - timedelta(days=9))
    before = sorted(path.name for path in repo.items.iterdir())

    assert repo.run("new", "--resource", RELEASE_TRAIN, "--no-fetch", "Cut v0.2.6") == 3
    filed = capsys.readouterr().out
    assert repo.run("release", "0.2.6", "--no-fetch") == 1
    refused = capsys.readouterr().out

    assert "PL-XXXX, whose claim on the release train is lapsed" in filed
    assert "`bin/docket claim PL-XXXX` revives it." in filed
    assert sorted(path.name for path in repo.items.iterdir()) == before
    assert "PL-XXXX is this branch's release item, and its claim is lapsed" in refused
    assert "file a new one" not in refused


@pytest.mark.usefixtures("_no_session")
def test_a_filing_names_a_claim_record_it_could_not_parse(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """What the read could not see is said before the answer, as `claim` says it."""
    repo = _TrainRepo(tmp_path / "repo")
    repo.git("checkout", "-q", "-b", "claude/x", "main")
    repo.commit(
        "PL-XXXX: file the release",
        when=TRAIN_T0,
        files={"items/PL-XXXX-cut.md": _train_item("PL-XXXX")},
    )
    repo.commit("PL-XXXX: start\n\nClaim: PL-XXXX", when=TRAIN_T0)
    repo.git("checkout", "-q", "-b", "claude/z", "main")

    repo.run("new", "--resource", RELEASE_TRAIN, "--no-fetch", "Cut v0.2.6")

    out = capsys.readouterr().out
    assert "note: not a claim record, so not read: " in out
    assert "on claude/x: Claim: PL-XXXX" in out


@pytest.mark.usefixtures("_no_session")
@pytest.mark.parametrize("command", ["new", "release"])
def test_a_declined_holdings_read_refuses_a_filing_and_a_cut(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    command: str,
) -> None:
    """A missing hold proves nothing when git would not answer, so neither goes through."""
    from docket import cli
    from docket.claims import Holdings

    repo = _TrainRepo(tmp_path / "repo")
    repo.hold("claude/pl-tr4n-cut", "PL-TR4N")
    before = sorted(path.name for path in repo.items.iterdir())
    monkeypatch.setattr(cli, "holdings", lambda *_, **__: Holdings(declined="git said no"))

    if command == "new":
        code = repo.run("new", "--resource", RELEASE_TRAIN, "--no-fetch", "Cut v0.2.6")
        said = "declined to read who holds the release train - git said no"
    else:
        code = repo.run("release", "0.2.6", "--no-fetch")
        said = "Cannot check whether another session is already cutting: git said no."

    assert code == 1
    assert said in capsys.readouterr().out
    assert sorted(path.name for path in repo.items.iterdir()) == before
    assert 'version = "0.2.5"' in repo.version()


@pytest.mark.usefixtures("_no_session")
def test_the_digest_reads_a_release_train_holder_from_the_refs(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """End to end: `_cuts` asks `holdings`, so a claim alone stops the offer."""
    repo = _TrainRepo(tmp_path / "repo")
    repo.git("checkout", "-q", "main")
    repo.commit(
        "two more finished",
        when=TRAIN_T0 - timedelta(days=20),
        files={
            f"items/{key}-shipped.md": _train_item(key, "done", resource="")
            for key in ("PL-D2D2", "PL-D3D3")
        },
    )
    repo.hold("claude/pl-tr4n-cut", "PL-TR4N")
    repo.git("checkout", "-q", "-b", "claude/second", "main")

    assert repo.run("digest") == 0

    out = capsys.readouterr().out
    assert "PL-TR4N holds the release train, nothing cut yet (claude/pl-tr4n-cut)" in out
    assert "Offer" not in out


@pytest.mark.usefixtures("_no_session")
def test_a_version_below_the_current_one_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """PL-3DN1: a typed 0.2.0 over 0.2.5 used to be cut, bumping the version backwards.

    Refused in a dry run too, which used to print `0.2.5 -> 0.2.0` and exit 0:
    it is the wrong number, not a state a dry run exists to review.
    """
    repo = _TrainRepo(tmp_path / "repo")
    repo.hold("claude/pl-tr4n-cut", "PL-TR4N")
    shipped = repo.items / "PL-D1D1-shipped.md"
    before = shipped.read_text(encoding="utf-8")

    assert repo.run("release", "0.2.0", "--no-fetch", "--dry-run") == 1
    assert repo.run("release", "0.2.0", "--no-fetch") == 1

    out = capsys.readouterr().out
    assert (
        "Cannot cut v0.2.0: 0.2.0 is below 0.2.5, the version pyproject.toml declares. "
        "Nothing was stamped and nothing was written." in out
    )
    assert "name a number above 0.2.5" in out
    assert "0.2.5 -> 0.2.0" not in out
    assert 'version = "0.2.5"' in repo.version()
    assert shipped.read_text(encoding="utf-8") == before
    assert not (repo.root / "docs" / "releases" / "v0.2.0.md").exists()


@pytest.mark.usefixtures("_no_session")
def test_a_cut_of_the_current_version_is_left_to_the_guard_that_names_its_evidence(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The equal case end to end: refused as already out, not as below itself."""
    repo = _TrainRepo(tmp_path / "repo")
    repo.hold("claude/pl-tr4n-cut", "PL-TR4N")

    assert repo.run("release", "0.2.5", "--no-fetch") == 1

    out = capsys.readouterr().out
    assert "its pyproject.toml already reads 0.2.5" in out
    assert "Cannot cut v0.2.5" not in out


@pytest.mark.usefixtures("_no_session")
def test_a_cut_interrupted_after_its_bump_is_resumed_rather_than_refused_as_current(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The resume the ordering guard must let through: version field and stamps, no notes."""
    repo = _TrainRepo(tmp_path / "repo")
    repo.hold("claude/pl-tr4n-cut", "PL-TR4N")
    shipped = _train_item("PL-D1D1", "done", resource="").replace(
        "status: done\n", "status: done\nmilestone: v0.2.6\n"
    )
    repo.commit(
        "cut v0.2.6, stopped before its notes",
        when=TRAIN_T0 + timedelta(minutes=30),
        files={
            "items/PL-D1D1-shipped.md": shipped,
            "pyproject.toml": '[project]\nversion = "0.2.6"\n',
        },
    )

    assert repo.run("release", "0.2.6", "--no-fetch") == 0

    out = capsys.readouterr().out
    assert "Resuming an interrupted cut of v0.2.6" in out
    assert "Cannot cut" not in out
    assert (repo.root / "docs" / "releases" / "v0.2.6.md").exists()
