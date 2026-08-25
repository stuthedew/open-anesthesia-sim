"""Tests for milestones, version inference, and the bump."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from docket.model import Item
from docket.release import (
    bump_version,
    milestones,
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
    assert "`abc1234`" in notes


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


def test_stamping_records_the_release_without_touching_anything_else() -> None:
    from docket.release import stamp

    (stamped,) = stamp([_item("PL-1111", milestone="")], "v0.2.3")

    assert stamped.milestone == "v0.2.3"
    assert stamped.status == "done"
    assert stamped.commit == "abc1234"
