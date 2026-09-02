"""Tests for the item format.

The format is the contract between a tool that reads state and a person who
reads prose, so both directions are tested: what a malformed file yields, and
that a file the tool writes reads back identically.
"""

from __future__ import annotations

from datetime import date

from docket.model import (
    Item,
    parse_front_matter,
    parse_item,
    render_item,
    repeated_front_matter_keys,
)

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
    # Splatting `dict[str, object]` matches `object` against every field's type; the
    # alternatives are `dict[str, Any]` or an `Unpack[TypedDict]` restating all of
    # `Item`'s fields, both wider than this line-scoped ignore.
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


# Delegability: whether an item may be handed to a cheaper model.
#
# Every test below asserts a *refusal* except one. That ratio is deliberate and
# it is the property worth protecting: the rule is a gate, and a gate is tested
# by what it turns away. A regression that made everything delegable would pass
# a suite written the other way round.

PROTECTED = ("src/anesthesia_sim/core", "docs/MODEL.md")


def _delegable(**overrides: object) -> Item:
    """An item meeting every condition, so each test can break exactly one."""
    base: dict[str, object] = dict(
        classes=("test", "infra"),
        touches=("tests/unit/test_alveolar.py",),
        effort="S",
        status="ready",
        verify="uv run pytest tests/unit/test_alveolar.py",
    )
    base.update(overrides)
    return _item(**base)


def test_an_item_meeting_every_condition_is_delegable() -> None:
    assert _delegable().delegability(PROTECTED) is None


def test_a_safety_classed_item_is_never_delegable() -> None:
    item = _delegable(classes=("safety",))
    assert item.delegability(PROTECTED) == "safety-tagged"


def test_a_science_classed_item_is_never_delegable() -> None:
    assert _delegable(classes=("science",)).delegability(PROTECTED) == "science-tagged"


def test_an_open_decision_is_never_delegable() -> None:
    item = _delegable(status="needs-decision")
    assert item.delegability(PROTECTED) == "status is needs-decision, not ready"


def test_an_item_touching_a_protected_directory_is_not_delegable() -> None:
    item = _delegable(touches=("src/anesthesia_sim/core/blood.py",))
    assert item.delegability(PROTECTED) == (
        "touches protected path(s) src/anesthesia_sim/core/blood.py"
    )


def test_an_item_touching_a_protected_file_is_not_delegable() -> None:
    item = _delegable(touches=("docs/MODEL.md",))
    assert item.delegability(PROTECTED) == "touches protected path(s) docs/MODEL.md"


def test_one_protected_path_among_several_is_enough_to_refuse() -> None:
    item = _delegable(touches=("tests/unit/test_blood.py", "src/anesthesia_sim/core/blood.py"))
    assert item.delegability(PROTECTED) is not None


def test_a_protected_prefix_does_not_match_a_merely_similar_path() -> None:
    """`core` must not protect `core_helpers`, nor `MODEL.md` protect `MODEL.md.bak`.

    Matching by bare string prefix would over-protect here and, in a project
    whose protected list happened to be a suffix of a real path, under-protect.
    """
    assert (
        _delegable(touches=("src/anesthesia_sim/core_helpers.py",)).delegability(PROTECTED) is None
    )
    assert _delegable(touches=("docs/MODEL.md.bak",)).delegability(PROTECTED) is None


def test_an_item_without_a_verify_command_is_not_delegable() -> None:
    assert _delegable(verify="").delegability(PROTECTED) == "no `verify:` command"


def test_an_item_declaring_no_touches_is_not_delegable() -> None:
    """No declared scope means no bound on the diff, so nothing to verify against."""
    assert _delegable(touches=()).delegability(PROTECTED) == "declares no `touches`"


def test_an_l_effort_item_is_not_delegable() -> None:
    assert _delegable(effort="L").delegability(PROTECTED) == "effort L is not S or M"


def test_not_delegable_withholds_an_otherwise_qualifying_item() -> None:
    item = _delegable(not_delegable="the message wording needs a judgement call")
    assert item.delegability(PROTECTED) == ("withheld: the message wording needs a judgement call")


def test_nothing_is_delegable_when_no_protected_paths_are_configured() -> None:
    """Fail closed: an unconfigured project gets no lane rather than an unguarded one."""
    assert _delegable().delegability(()) == "no protected paths configured"


def test_there_is_no_field_that_grants_delegability() -> None:
    """The only writable control withholds. Nothing can mark its own work eligible.

    A worker editing front matter can at worst refuse itself work. This is the
    asymmetry the whole safeguard rests on, so it is asserted rather than
    assumed: `delegable` is not a field the parser knows, and setting it is a
    validation error rather than a grant.
    """
    text = (
        "---\nid: PL-K7QX\ntitle: T\nstatus: ready\npriority: P2\neffort: S\n"
        "delegable: yes\ntouches: tests/unit/test_x.py\nverify: pytest\n"
        "added: 2026-08-01\n---\n\n" + BRIEF
    )
    parsed = parse_item(text)
    assert "delegable" in parsed.unknown_fields
    assert parsed.not_delegable == ""


def test_verify_and_not_delegable_round_trip_through_the_file() -> None:
    item = _delegable(verify="make check", not_delegable="needs judgement")
    assert parse_item(render_item(item)).verify == "make check"
    assert parse_item(render_item(item)).not_delegable == "needs judgement"


def test_a_repeated_front_matter_key_is_reported_not_collapsed_away() -> None:
    """The shape a clean merge of two branches produces.

    Both sessions answered the same advisory by writing `pr:` in, at different
    line positions, so git took both lines and neither branch conflicted. The
    dict keeps the last; this is what makes the loss visible (`PL-BR4G`).
    """
    text = "---\nid: PL-X0RG\ntitle: t\npr: 187\nclosed: 2026-09-02\npr: 999\n---\nBody\n"

    assert repeated_front_matter_keys(text) == ("pr",)
    assert parse_item(text).duplicate_fields == ("pr",)
    assert parse_front_matter(text)[0]["pr"] == "999"


def test_repeated_keys_are_reported_once_each_and_sorted() -> None:
    text = "---\nid: PL-K7QX\nid: PL-AAA1\nid: PL-BBB2\ntitle: a\ntitle: b\n---\nBody\n"

    assert repeated_front_matter_keys(text) == ("id", "title")


def test_a_file_with_no_repeated_key_reports_none() -> None:
    assert repeated_front_matter_keys("---\nid: PL-K7QX\ntitle: t\n---\nBody\n") == ()
    assert repeated_front_matter_keys("# Just a heading\n") == ()
    assert parse_item("---\nid: PL-K7QX\ntitle: t\n---\nBody\n").duplicate_fields == ()
