"""Tests for the item format.

The format is the contract between a tool that reads state and a person who
reads prose, so both directions are tested: what a malformed file yields, and
that a file the tool writes reads back identically.
"""

from __future__ import annotations

from datetime import date

from docket.model import Item, parse_front_matter, parse_item, render_item

BRIEF = "**Problem.** It is wrong.\n**Why it matters.** It has a cost.\n**Done when.** Fixed.\n"


def _item(**overrides: object) -> Item:
    base: dict[str, object] = dict(
        identifier="PL-K7QX",
        title="Do the thing",
        priority="P1",
        effort="M",
        status="ready",
        classes=("perf",),
        touches=("src/app/view.py",),
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


def test_front_matter_splits_fields_from_body() -> None:
    fields, body = parse_front_matter("---\nid: PL-001\ntitle: A thing\n---\n\nBody text.\n")

    assert fields == {"id": "PL-001", "title": "A thing"}
    assert body.strip() == "Body text."


def test_a_file_without_front_matter_yields_no_fields() -> None:
    fields, body = parse_front_matter("# Just a heading\n")

    assert fields == {}
    assert body == "# Just a heading\n"


def test_list_fields_are_split_on_commas() -> None:
    item = parse_item("---\nid: PL-001\nclasses: safety, ux\ntouches: a.py, b.py\n---\n\nBody\n")

    assert item.classes == ("safety", "ux")
    assert item.touches == ("a.py", "b.py")


def test_missing_fields_come_back_empty_rather_than_defaulted() -> None:
    """A wrong-but-plausible default is worse than an obvious absence."""
    item = parse_item("---\nid: PL-001\n---\n\nBody\n")

    assert (item.priority, item.effort, item.status) == ("", "", "")
    assert item.added is None


def test_an_unparseable_date_is_absent_not_guessed() -> None:
    item = parse_item("---\nid: PL-001\nadded: last tuesday\n---\n\nBody\n")

    assert item.added is None


def test_unknown_fields_are_recorded_so_a_typo_can_be_reported() -> None:
    item = parse_item("---\nid: PL-001\npriorty: P1\n---\n\nBody\n")

    assert item.unknown_fields == ("priorty",)


def test_render_then_parse_round_trips() -> None:
    original = _item(
        classes=("safety", "ux"), blocked_by=("PL-002",), feature="halted-step", milestone="v0.3.0"
    )
    restored = parse_item(render_item(original))

    for name in (
        "identifier",
        "title",
        "priority",
        "effort",
        "status",
        "classes",
        "touches",
        "blocked_by",
        "feature",
        "milestone",
        "added",
    ):
        assert getattr(restored, name) == getattr(original, name), name


def test_render_omits_empty_fields() -> None:
    rendered = render_item(_item())

    assert "milestone:" not in rendered
    assert "commit:" not in rendered
    assert "reason:" not in rendered


def test_rendering_is_stable_so_rewriting_produces_no_diff() -> None:
    once = render_item(_item(milestone="v0.3.0"))

    assert render_item(parse_item(once)) == once


def test_safety_classes_are_recognized() -> None:
    assert _item(classes=("safety", "ux")).safety_classes == ("safety",)
    assert _item(classes=("perf",)).safety_classes == ()


def test_process_work_needs_every_class_to_be_process() -> None:
    assert _item(classes=("session-cost", "docs")).is_process_work
    assert not _item(classes=("science", "infra")).is_process_work


def test_model_guidance_flags_safety_and_open_decisions() -> None:
    assert _item(classes=("science",)).model_guidance == "science-tagged"
    assert _item(status="needs-decision").model_guidance == "open design decision"
    assert _item().model_guidance is None


def test_untriaged_items_sort_after_everything_triaged() -> None:
    """They are candidates for a decision, not for work."""
    triaged = _item(priority="P3", effort="L")
    captured = _item(priority="", status="untriaged")

    assert triaged.sort_key() < captured.sort_key()
