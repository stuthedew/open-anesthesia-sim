"""Tests for milestones, version inference, and the bump."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from docket.model import Item
from docket.release import (
    bump_version,
    is_untagged,
    milestones,
    outstanding_roadmap_edits,
    read_version,
    release_notes,
    suggest_version,
    version_key,
)

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


def test_bump_rewrites_the_single_source(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "x"\nversion = "0.2.2"\n', encoding="utf-8")

    assert bump_version(pyproject, "0.3.0") == "0.2.2"
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
        bump_version(target, "0.3.0")


def test_a_shipped_version_with_no_tag_is_reported() -> None:
    assert is_untagged("0.2.5", frozenset({"v0.2.3", "v0.2.4"}))


def test_a_tagged_version_is_not() -> None:
    assert not is_untagged("0.2.5", frozenset({"v0.2.5"}))


def test_a_tag_written_without_its_v_still_counts() -> None:
    assert not is_untagged("0.2.5", frozenset({"0.2.5"}))


def test_a_project_that_has_never_tagged_is_not_taught_to() -> None:
    """Emptiness says the project does not tag, not that every release is missing one."""
    assert not is_untagged("0.2.5", frozenset())


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
