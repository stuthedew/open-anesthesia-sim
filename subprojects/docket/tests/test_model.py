"""Tests for the item format.

The format is the contract between a tool that reads state and a person who
reads prose, so both directions are tested: what a malformed file yields, and
that a file the tool writes reads back identically.
"""

from __future__ import annotations

from datetime import date

import pytest

from docket.model import (
    LANE_CROSSING,
    LANE_PRODUCT,
    LANE_UNPLACED,
    LANE_WORKFLOW,
    Item,
    block_list_keys,
    generator_defect_faults,
    impairs_generators_soundly,
    is_generator,
    live_recurrences,
    parse_front_matter,
    parse_item,
    recurrence_count,
    recurrence_faults,
    recurrences_of,
    render_item,
    repeated_front_matter_keys,
    root_cause_faults,
    with_front_matter_field,
    with_front_matter_value,
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


# --- adding a field without rewriting the block (PL-7K8Y)
#
# `render_item` normalises a whole file, which is right when the caller
# changed a field and wrong when it added one: the normalisation lands as
# removed lines in a diff about something else, and `sanctioned_queue_edit`
# reads any removal as an ordinary content edit. These pin the other writer.

#: Everything `render_item` would normalise, in one file: `verify:` and
#: `status:` sit ahead of keys `FIELD_ORDER` puts before them, `reason:` runs
#: over a continuation line, and `notes:` is not a field at all. Written the
#: way the 118 hand-typed blocks in this store were.
SCRAMBLED = (
    "---\n"
    "id: PL-C3C3\n"
    "title: A hand-written item\n"
    "verify: true\n"
    "status: done\n"
    "touches: a.py\n"
    "reason: it turned out to be two problems, and the second one\n"
    "  is already covered by PL-B2B2\n"
    "closed: 2026-09-01\n"
    "---\n"
    "\n"
    "**Problem.** x\n"
)


def test_a_field_added_to_a_hand_written_block_removes_nothing() -> None:
    """The defect: `record` re-rendered the file, and a removal is a content edit.

    `verify.sanctioned_queue_edit` exempts the backfill the close-out is told
    to make only where the diff removes nothing at all, so a reorder or a
    reflowed value turned a correct close-out into a `REJECT` - and because it
    reads the per-commit diffs rather than the net tree, putting the order
    back in a later commit left both the removal and its undo on the branch.
    """
    written = with_front_matter_field(SCRAMBLED, "pr", "495")

    assert written == SCRAMBLED.replace("closed: 2026-09-01\n", "closed: 2026-09-01\npr: 495\n")
    assert set(SCRAMBLED.splitlines()) <= set(written.splitlines()), "a line was removed"


def test_a_continuation_line_survives_a_field_being_added() -> None:
    """The half the item's own framing did not reach, and it comes free.

    `_front_matter_pairs` matches `key: value` lines and passes over the
    indented lines that continue one, so a round trip through `parse_item` and
    `render_item` deletes them - 12 files in this store carry 3 to 15 such
    lines. Inserting a line cannot, because nothing has to know they are there.
    """
    written = with_front_matter_field(SCRAMBLED, "pr", "495")

    assert "  is already covered by PL-B2B2\n" in written


def test_the_added_field_lands_where_render_item_would_have_put_it() -> None:
    """The guard against the two writers drifting apart.

    `FIELD_ORDER` is the single source both read, and this is what says so:
    on a block `render_item` already agrees with, adding a field by insertion
    and adding it by re-rendering produce the same bytes. Measured across the
    store on 2026-09-20 - all 377 canonical files of the 495 not yet recording
    a `pr`, and a pure insertion on the other 118.
    """
    canonical = render_item(_item(status="done", closed=date(2026, 9, 1)))

    inserted = with_front_matter_field(canonical, "pr", "495")

    assert inserted == render_item(_item(status="done", closed=date(2026, 9, 1), pr="495"))


def test_a_field_already_present_is_refused_rather_than_doubled() -> None:
    """Two `pr:` lines is the exact shape `repeated_front_matter_keys` exists to report.

    An insert has no way to express a replacement, so it says so instead of
    guessing. Both callers in `cmd_record` establish the field is absent
    first - a number that disagrees is sorted into its own report - so
    reaching this is a bug rather than a state to paper over.
    """
    once = with_front_matter_field(SCRAMBLED, "pr", "495")

    with pytest.raises(ValueError, match="already records"):
        with_front_matter_field(once, "pr", "496")


def test_an_appended_entry_extends_the_line_and_removes_nothing_else() -> None:
    """The second and later filings, held to the same standard as the first.

    `bin/docket new` writes a `recurrences:` entry onto the item a capture
    matched, and after the first there is a line to extend rather than a field
    to insert. Re-rendering the file to do it would normalise the whole block,
    and `verify.sanctioned_queue_edit` reads every normalised line as a
    removal - which is what `PL-7K8Y` cost and why the append lands here
    rather than in `rewrite_item`.
    """
    once = with_front_matter_field(SCRAMBLED, "recurrences", "2026-09-19 PL-A1A1")

    twice = with_front_matter_field(once, "recurrences", "2026-09-20 PL-B2B2", append=True)

    assert "recurrences: 2026-09-19 PL-A1A1, 2026-09-20 PL-B2B2\n" in twice
    assert twice.count("recurrences:") == 1
    assert set(SCRAMBLED.splitlines()) <= set(twice.splitlines()), "a line was removed"


def test_an_append_to_a_field_spelled_twice_is_refused_rather_than_guessed_at() -> None:
    """Two lines and no way to say which one grows, which is a doubled key's own defect.

    The shape `repeated_front_matter_keys` exists to report: two branches
    inserting the same field at different positions merge without conflicting,
    and every reader downstream then takes a value nobody chose. Appending to
    one of them would pick a winner silently, which is the defect rather than
    the repair.
    """
    doubled = SCRAMBLED.replace(
        "status: done\n",
        "status: done\nrecurrences: 2026-09-19 PL-A1A1\nrecurrences: 2026-09-20 PL-B2B2\n",
    )

    with pytest.raises(ValueError, match="spells `recurrences` 2 times"):
        with_front_matter_field(doubled, "recurrences", "2026-09-21 PL-C3C3", append=True)


def test_a_withdrawn_entry_is_kept_on_the_record_and_out_of_the_count() -> None:
    """Both halves of what a withdrawal is: the entry stays, the arithmetic drops it.

    A deletion would give the second half alone, and give it by making the file
    read as though `docket new` had never matched anything - the one event in
    this mechanism's life with no record (`PL-34BG`).
    """
    item = _item(
        recurrences=("2026-09-20 PL-B2B2 withdrawn 2026-09-21 PL-C3C3", "2026-09-20 PL-D4D4")
    )

    assert recurrence_count(item) == 1
    assert [found.identifier for found in live_recurrences(item)] == ["PL-D4D4"]
    withdrawn = next(found for found in recurrences_of(item) if found.withdrawn)
    assert withdrawn.identifier == "PL-B2B2"
    assert withdrawn.withdrawn == date(2026, 9, 21)
    assert withdrawn.withdrawn_by == "PL-C3C3"


def test_a_tail_nothing_can_read_as_a_withdrawal_still_counts_and_is_reported() -> None:
    """The direction a mis-typed withdrawal has to fail in.

    Reading a half-written tail as a withdrawal would cancel a filing nobody
    withdrew, and do it silently. So the entry stays live - the count is then
    too high, which is the loud direction - and `docket check` says why.
    """
    item = _item(recurrences=("2026-09-20 PL-B2B2 withdrawn yesterday PL-C3C3",))

    assert recurrence_count(item) == 1
    faults = recurrence_faults(item, {"PL-B2B2", "PL-C3C3", "PL-K7QX"})
    assert any("does not read as `withdrawn DATE PL-XXXX`" in fault for fault in faults)


def test_a_withdrawal_citing_no_item_in_the_store_is_reported() -> None:
    """The pointer is the whole audit trail, so a dangling one is a fault.

    Held exactly as the capture id is held. A withdrawal whose brief cannot be
    opened is a correction nobody can check, which is the state the field was
    in before the command existed.
    """
    item = _item(recurrences=("2026-09-20 PL-B2B2 withdrawn 2026-09-21 PL-Z9Z9",))

    faults = recurrence_faults(item, {"PL-B2B2", "PL-K7QX"})

    assert any("is withdrawn by PL-Z9Z9" in fault for fault in faults)


def test_a_replaced_value_changes_one_line_and_leaves_the_rest_alone() -> None:
    """A withdrawal edits a line that is already there, so it cannot be an insert.

    The byte-faithfulness `PL-7K8Y` bought for the append is what this keeps
    for the edit: a re-render normalises key order and reflows the multi-line
    `reason:` on the way past, and every one of those lines is a removal in a
    diff about something else.
    """
    once = with_front_matter_field(SCRAMBLED, "recurrences", "2026-09-19 PL-A1A1")

    withdrawn = with_front_matter_value(
        once, "recurrences", "2026-09-19 PL-A1A1 withdrawn 2026-09-21 PL-B2B2"
    )

    assert "recurrences: 2026-09-19 PL-A1A1 withdrawn 2026-09-21 PL-B2B2\n" in withdrawn
    assert withdrawn.count("recurrences:") == 1
    assert set(SCRAMBLED.splitlines()) <= set(withdrawn.splitlines()), "a line was removed"


def test_replacing_a_value_the_file_does_not_carry_is_refused() -> None:
    """No line to change is a caller bug, not a field to invent.

    `cmd_withdraw` establishes the entry is recorded before it writes, so
    reaching this means the store and the command disagree about what is in
    the file - which is worth an exception rather than a silent insert.
    """
    with pytest.raises(ValueError, match="records no `recurrences`"):
        with_front_matter_value(SCRAMBLED, "recurrences", "2026-09-19 PL-A1A1")


def test_a_file_with_no_front_matter_is_refused_rather_than_given_some() -> None:
    with pytest.raises(ValueError, match="no front matter"):
        with_front_matter_field("**Problem.** x\n", "pr", "495")


def test_an_unknown_field_name_is_refused() -> None:
    """The same rule `docket set` holds a typed field to: no reader would see it."""
    with pytest.raises(ValueError, match="not a front-matter field"):
        with_front_matter_field(SCRAMBLED, "prr", "495")


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
# Every test below asserts a *refusal* except the few pinning where a refusal
# stops. That ratio is deliberate and
# it is the property worth protecting: the rule is a gate, and a gate is tested
# by what it turns away. A regression that made everything delegable would pass
# a suite written the other way round.

PROTECTED = ("src/anesthesia_sim/core", "docs/MODEL.md")
# A second list, and a second kind of prohibition: the files that measure the
# work rather than the files that produce a clinical value. Kept short and
# unlike the real one, so a test asserting a reason string is asserting the
# rule rather than this repository's configuration.
GATES = ("Makefile", ".claude", "docket.toml")


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
    assert _delegable().delegability(PROTECTED, GATES) is None


def test_a_safety_classed_item_is_never_delegable() -> None:
    item = _delegable(classes=("safety",))
    assert item.delegability(PROTECTED, GATES) == "safety-tagged"


def test_a_science_classed_item_is_never_delegable() -> None:
    assert _delegable(classes=("science",)).delegability(PROTECTED, GATES) == "science-tagged"


def test_an_open_decision_is_never_delegable() -> None:
    item = _delegable(status="needs-decision")
    assert item.delegability(PROTECTED, GATES) == "status is needs-decision, not ready"


def test_an_item_touching_a_protected_directory_is_not_delegable() -> None:
    item = _delegable(touches=("src/anesthesia_sim/core/blood.py",))
    assert item.delegability(PROTECTED, GATES) == (
        "touches protected path(s) src/anesthesia_sim/core/blood.py"
    )


def test_an_item_touching_a_protected_file_is_not_delegable() -> None:
    item = _delegable(touches=("docs/MODEL.md",))
    assert item.delegability(PROTECTED, GATES) == "touches protected path(s) docs/MODEL.md"


def test_one_protected_path_among_several_is_enough_to_refuse() -> None:
    item = _delegable(touches=("tests/unit/test_blood.py", "src/anesthesia_sim/core/blood.py"))
    assert item.delegability(PROTECTED, GATES) is not None


def test_a_protected_prefix_does_not_match_a_merely_similar_path() -> None:
    """`core` must not protect `core_helpers`, nor `MODEL.md` protect `MODEL.md.bak`.

    Matching by bare string prefix would over-protect here and, in a project
    whose protected list happened to be a suffix of a real path, under-protect.
    """
    assert (
        _delegable(touches=("src/anesthesia_sim/core_helpers.py",)).delegability(PROTECTED, GATES)
        is None
    )
    assert _delegable(touches=("docs/MODEL.md.bak",)).delegability(PROTECTED, GATES) is None


def test_an_item_touching_the_checks_themselves_is_not_delegable() -> None:
    """`docket verify` refuses such a diff, so offering the work refuses it later.

    The two commands disagreed until `PL-S2L4`: `delegable` read only the
    protected paths while `verify`'s "the checks themselves are unedited"
    audit read the gate paths, so fifteen of the eighty-six items offered on
    2026-09-08 were work that would have been REJECTed once a worker finished
    it.
    """
    item = _delegable(touches=("docket.toml",))
    assert item.delegability(PROTECTED, GATES) == "touches the checks themselves: docket.toml"


def test_a_gate_directory_covers_the_files_beneath_it() -> None:
    """Seven of the fifteen declared a file under `.claude/`, not `.claude` itself."""
    item = _delegable(touches=(".claude/skills/docket/SKILL.md",))
    assert item.delegability(PROTECTED, GATES) == (
        "touches the checks themselves: .claude/skills/docket/SKILL.md"
    )


def test_a_protected_path_is_reported_ahead_of_a_gate_path() -> None:
    """Both refuse, and the clinical one is the reason worth reading first."""
    item = _delegable(touches=("docket.toml", "docs/MODEL.md"))
    assert item.delegability(PROTECTED, GATES) == "touches protected path(s) docs/MODEL.md"


def test_a_gate_prefix_does_not_match_a_merely_similar_path() -> None:
    """`.claude` must not cover `.claudeignore`, nor `Makefile` cover `Makefile.bak`."""
    assert _delegable(touches=(".claudeignore",)).delegability(PROTECTED, GATES) is None
    assert _delegable(touches=("Makefile.bak",)).delegability(PROTECTED, GATES) is None


def test_an_empty_gate_list_does_not_withhold_the_way_an_empty_protected_list_does() -> None:
    """The asymmetry is deliberate, and it turns on which list has a default.

    An empty `protected_paths` means a project never said which files produce
    consequential output, and silence there is read as "offer nothing". An
    empty `gate_paths` can only be a project that cleared a real default -
    telling `verify` to stop auditing its checks, which is not a request for
    this to start.
    """
    assert _delegable(touches=("docket.toml",)).delegability(PROTECTED, ()) is None


def test_an_item_without_a_verify_command_is_not_delegable() -> None:
    assert _delegable(verify="").delegability(PROTECTED, GATES) == "no `verify:` command"


def test_an_item_declaring_no_touches_is_not_delegable() -> None:
    """No declared scope means no bound on the diff, so nothing to verify against."""
    assert _delegable(touches=()).delegability(PROTECTED, GATES) == "declares no `touches`"


def test_an_l_effort_item_is_not_delegable() -> None:
    assert _delegable(effort="L").delegability(PROTECTED, GATES) == "effort L is not S or M"


def test_not_delegable_withholds_an_otherwise_qualifying_item() -> None:
    item = _delegable(not_delegable="the message wording needs a judgement call")
    assert item.delegability(PROTECTED, GATES) == (
        "withheld: the message wording needs a judgement call"
    )


def test_nothing_is_delegable_when_no_protected_paths_are_configured() -> None:
    """Fail closed: an unconfigured project gets no lane rather than an unguarded one."""
    assert _delegable().delegability((), GATES) == "no protected paths configured"


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


def test_a_payoff_round_trips_through_the_file() -> None:
    """One line of prose, and the commas in it are not a list (`PL-WYKF`)."""
    payoff = "the queue stops reading as arbitrary, so an offer can be weighed"
    item = _item(payoff=payoff)

    assert parse_item(render_item(item)).payoff == payoff


def test_the_payoff_is_written_with_the_prose_fields_not_the_scan_fields() -> None:
    """Position is a readability choice, and the diff of a rewrite depends on it.

    `id`, `priority`, `effort`, `status` and the rest are tokens a reader
    scans; `reason`, `payoff` and `verify` are sentences. Keeping the two
    groups apart is what stops one long line breaking the block a reader skims.
    """
    rendered = render_item(_item(payoff="sessions stop re-deriving the reason", verify="pytest -q"))
    keys = [line.split(":")[0] for line in rendered.splitlines() if ": " in line]

    assert keys.index("payoff") > keys.index("status")
    assert keys.index("payoff") < keys.index("verify")


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


# `PL-9HD1`: the three defects one skipped line produced, and the cases that
# decide how far the repair may reach. The fixture below is the shape `PL-9HDH`
# carries - a `reason:` hand-wrapped over continuation lines - because that is
# the file a `rewrite_item` round trip was measured taking from 27 lines to 18,
# deleting 9 of its 10 recorded lines and exiting 0.
WRAPPED = (
    "---\n"
    "id: PL-9HDH\n"
    "title: t\n"
    "status: dropped\n"
    "reason: Would reintroduce the defect PL-3V8K and PL-0ZP8 both diagnosed\n"
    "  independently. The `pull_request` trigger excludes `edited` on purpose,\n"
    "  because a title edit re-runs the whole suite.\n"
    "not-delegable: The judgment is which of two costs to pay.\n"
    "---\n"
    "Body\n"
)


def test_a_wrapped_value_is_read_whole_rather_than_truncated_at_its_first_line() -> None:
    """`PL-5B39`: every reader was handed the first line as if it were the value."""
    item = parse_item(WRAPPED)

    assert item.reason.startswith("Would reintroduce the defect PL-3V8K")
    assert "excludes `edited` on purpose" in item.reason
    assert item.reason.endswith("because a title edit re-runs the whole suite.")


def test_a_multi_line_front_matter_value_survives_a_round_trip() -> None:
    """`PL-5B39`: `render_item` wrote the parsed value, so the rest left the file.

    The round trip still reflows the field onto one line, which is a diff to
    read. What it no longer does is shorten it.
    """
    once = parse_item(WRAPPED)
    twice = parse_item(render_item(once))

    assert twice.reason == once.reason
    assert twice.not_delegable == once.not_delegable
    assert "a title edit re-runs the whole suite." in render_item(once)


def test_a_wrapped_list_field_keeps_every_entry() -> None:
    item = parse_item("---\nid: PL-K7QX\ntitle: t\ntouches: a/b.py,\n  c/d.py\n---\nBody\n")

    assert item.touches == ("a/b.py", "c/d.py")


def test_a_line_at_column_zero_continues_nothing_as_it_continues_nothing_in_yaml() -> None:
    """Indentation is what makes a line a continuation, so an outdented one is not."""
    item = parse_item("---\nid: PL-K7QX\ntitle: t\nstray text\n---\nBody\n")

    assert item.title == "t"
    assert item.unknown_fields == ()


def test_a_list_field_written_as_a_block_list_is_refused_rather_than_read() -> None:
    """`PL-FX0K`: it parsed to an empty tuple, so the item reached no lane."""
    text = "---\nid: PL-K7QX\ntitle: t\ntouches:\n  - a/b.py\n  - c/d.py\n---\nBody\n"
    item = parse_item(text)

    assert block_list_keys(text) == ("touches",)
    assert item.block_list_fields == ("touches",)
    assert item.touches == ()


def test_every_list_field_is_refused_in_the_block_form_not_only_touches() -> None:
    text = (
        "---\nid: PL-K7QX\ntitle: t\n"
        "classes:\n  - safety\n"
        "touches:\n  - a/b.py\n"
        "blocked-by:\n  - PL-0001\n"
        "---\nBody\n"
    )

    assert parse_item(text).block_list_fields == ("blocked-by", "classes", "touches")


def test_a_block_list_classes_cannot_hand_a_safety_item_an_empty_class_silently() -> None:
    """`PL-FX0K`, which is `PL-MVC2` arriving through the parser.

    `checks.py` seats a `safety`-classed item in the top bands only when it can
    see the class, and an empty `classes` is what defeats that. The field still
    arrives empty - nothing here guesses at the entries - but it arrives with
    the fact that it could not be read, which is what `checks.py` reports.
    """
    item = parse_item(
        "---\nid: PL-K7QX\ntitle: t\nstatus: ready\npriority: P3\nclasses:\n  - safety\n---\nB\n"
    )

    assert item.safety_classes == ()
    assert item.block_list_fields == ("classes",)


def test_a_dash_continuation_under_a_prose_field_is_prose_not_a_block_list() -> None:
    """The refusal is scoped to `LIST_FIELDS`, which is where two spellings collide.

    An argument licenses the narrowest rule that removes the hazard. Under a
    prose field there is no second spelling to be ambiguous with, so a dash
    folds like any other continuation.
    """
    item = parse_item(
        "---\nid: PL-K7QX\ntitle: t\n"
        "reason: dropped in favour of PL-0001\n  - the measurement never reproduced\n"
        "---\nBody\n"
    )

    assert item.block_list_fields == ()
    assert item.reason == "dropped in favour of PL-0001 - the measurement never reproduced"


def test_a_value_quoted_the_way_yaml_requires_parses_to_the_unquoted_string() -> None:
    """`PL-V6CR`: the quotes became the first and last characters of the title."""
    text = (
        "---\nid: PL-K7QX\n"
        'title: "The wiring is untested: every test reads the controller"\n---\nBody\n'
    )
    item = parse_item(text)

    assert item.title == "The wiring is untested: every test reads the controller"
    assert parse_item(render_item(item)).title == item.title


def test_a_single_quoted_scalar_collapses_yamls_doubled_quote_escape() -> None:
    item = parse_item(
        "---\nid: PL-T531\ntitle: 'Decide isoflurane''s blood:gas coefficient'\n---\nBody\n"
    )

    assert item.title == "Decide isoflurane's blood:gas coefficient"


def test_a_quoted_verify_command_parses_to_something_a_shell_can_run() -> None:
    """`PL-MZH2` was this defect on one item, repaired there by hand.

    A shell reads the quoted form as a single word and exits 127 having run
    nothing, so the command can never accept the work it was written for.
    Three more arrived in the store after that repair.
    """
    item = parse_item(
        "---\nid: PL-K7QX\ntitle: t\nverify: '! grep -rq \"Workflow work\" CLAUDE.md'\n---\nBody\n"
    )

    assert item.verify == '! grep -rq "Workflow work" CLAUDE.md'


def test_a_value_that_merely_opens_with_a_quote_is_taken_verbatim() -> None:
    """`PL-XF5V`'s `payoff:`, and why the pair has to close at the last character.

    A rule stripping the ends of anything that begins and ends with a quote
    would rewrite this into a string nobody wrote.
    """
    item = parse_item(
        "---\nid: PL-XF5V\ntitle: t\n"
        "payoff: 'are the generators dealt with' is answered by a command\n---\nBody\n"
    )

    assert item.payoff == "'are the generators dealt with' is answered by a command"


def test_a_pair_that_closes_early_is_taken_verbatim_though_both_ends_match() -> None:
    item = parse_item("---\nid: PL-K7QX\ntitle: t\nverify: 'a' && 'b'\n---\nBody\n")

    assert item.verify == "'a' && 'b'"


def test_an_unterminated_quote_is_taken_verbatim_rather_than_guessed_at() -> None:
    item = parse_item('---\nid: PL-K7QX\ntitle: "unclosed\n---\nBody\n')

    assert item.title == '"unclosed'


def test_a_backslash_is_read_as_an_escape_only_before_a_quote_or_a_backslash() -> None:
    """Turning a backslash-n into a newline would invent a character the file lacks."""
    item = parse_item('---\nid: PL-K7QX\ntitle: "a\\nb and \\"c\\""\n---\nBody\n')

    assert item.title == 'a\\nb and "c"'


WORKFLOW = ("tools", ".claude", "docs/items", "CLAUDE.md")


def test_an_item_wholly_inside_the_apparatus_is_workflow_work() -> None:
    item = _item(touches=("tools/doc_check.py", ".claude/skills/docket/SKILL.md"))

    assert item.lane(WORKFLOW) == LANE_WORKFLOW


def test_an_item_touching_none_of_the_apparatus_is_product_work() -> None:
    item = _item(touches=("src/anesthesia_sim/core/blood.py", "docs/MODEL.md"))

    assert item.lane(WORKFLOW) == LANE_PRODUCT


def test_an_item_reaching_both_halves_is_neither_lane_s_to_take() -> None:
    """The case the split exists for: two sessions must not both be offered it."""
    item = _item(touches=("tools/doc_check.py", "docs/MODEL.md"))

    assert item.lane(WORKFLOW) == LANE_CROSSING


def test_an_item_declaring_no_touches_cannot_be_placed() -> None:
    """Silence is not 'product'. Guessing here is how a lane hands over the wrong work."""
    assert _item(touches=()).lane(WORKFLOW) == LANE_UNPLACED


def test_no_declared_boundary_leaves_every_item_unplaced() -> None:
    """Fail closed, exactly as an unconfigured `protected_paths` refuses delegation."""
    assert _item(touches=("tools/doc_check.py",)).lane(()) == LANE_UNPLACED


def test_a_workflow_prefix_does_not_match_a_merely_similar_path() -> None:
    """`tools` must not claim `toolsmith.py`, nor `CLAUDE.md` claim `CLAUDE.md.bak`."""
    assert _item(touches=("toolsmith.py",)).lane(WORKFLOW) == LANE_PRODUCT
    assert _item(touches=("CLAUDE.md.bak",)).lane(WORKFLOW) == LANE_PRODUCT
    assert _item(touches=("tools/doc_check.py",)).lane(WORKFLOW) == LANE_WORKFLOW


def test_a_declared_path_is_placed_whatever_its_classes_say() -> None:
    """`classes` describes the kind of work; only `touches` says which half it is in.

    A defect in this repository's tooling and a defect in the simulator carry
    the same label, which is why the lane is not read from `classes` (`PL-8165`).
    """
    tooling = _item(classes=("defect",), touches=("tools/doc_check.py",))
    simulator = _item(classes=("docs",), touches=("docs/MODEL.md",))

    assert tooling.lane(WORKFLOW) == LANE_WORKFLOW
    assert simulator.lane(WORKFLOW) == LANE_PRODUCT


# `root-cause-of:`: the one field in the store that buys a queue position.
#
# `root_cause_faults` is deliberately shared with `checks.py` and `plan.py`, so
# these tests are the contract both of them read. What they pin is the
# fail-closed direction: a claim that is short, mistyped or self-referential is
# not a claim, because `docket check` runs separately and the ranking would
# otherwise act on it first.

KNOWN = {"PL-K7QX", "PL-E1E1", "PL-E2E2", "PL-E3E3"}
EXPLAINS = ("PL-E1E1", "PL-E2E2", "PL-E3E3")


def test_a_root_cause_round_trips_through_the_file() -> None:
    written = render_item(_item(root_cause_of=EXPLAINS))

    assert "root-cause-of: PL-E1E1, PL-E2E2, PL-E3E3" in written
    assert parse_item(written).root_cause_of == EXPLAINS


def test_a_sound_root_cause_has_no_faults() -> None:
    item = _item(root_cause_of=EXPLAINS)

    assert root_cause_faults(item, KNOWN) == ()
    assert is_generator(item, KNOWN)


def test_an_item_making_no_claim_is_not_a_generator() -> None:
    """No field is silence, not a fault - and silence is not a claim either."""
    item = _item()

    assert root_cause_faults(item, KNOWN) == ()
    assert not is_generator(item, KNOWN)


def test_a_root_cause_naming_fewer_than_three_items_is_an_ordinary_item() -> None:
    item = _item(root_cause_of=EXPLAINS[:2])

    (fault,) = root_cause_faults(item, KNOWN)
    assert "names 2 item(s)" in fault
    assert not is_generator(item, KNOWN)


def test_repeating_one_id_does_not_reach_the_floor() -> None:
    """Counted over distinct ids: a floor a repetition defeats is not a floor."""
    item = _item(root_cause_of=("PL-E1E1", "PL-E1E1", "PL-E1E1"))

    (fault,) = root_cause_faults(item, KNOWN)
    assert "names 1 item(s)" in fault


def test_a_root_cause_naming_an_id_no_item_carries_is_refused() -> None:
    item = _item(root_cause_of=(*EXPLAINS, "PL-NOPE"))

    (fault,) = root_cause_faults(item, KNOWN)
    assert "PL-NOPE" in fault
    assert not is_generator(item, KNOWN)


def test_a_typo_and_a_short_list_stay_two_findings() -> None:
    """Two repairs, so two messages.

    The count reads over what is *written* rather than over what resolved, so
    a field naming two ids one of which is a typo says both things. Counting
    resolved ids instead would report "names 1 item(s)" and hide the typo
    behind a number.
    """
    faults = root_cause_faults(_item(root_cause_of=("PL-E1E1", "PL-NOPE")), KNOWN)

    assert len(faults) == 2
    assert "PL-NOPE" in faults[0]
    assert "names 2 item(s)" in faults[1]


def test_an_item_cannot_be_its_own_root_cause() -> None:
    item = _item(root_cause_of=("PL-K7QX", *EXPLAINS))

    (fault,) = root_cause_faults(item, KNOWN)
    assert "lists itself" in fault


# `generator_defect_faults` is the tier's other entrance and is shared by the
# same two readers. What these pin is the same fail-closed direction, plus the
# one property that makes the design honest: `touches` refutes a claim and
# never establishes one, because the machinery lives inside files that do many
# other things (36 of this project's 322 open items touch them, 2026-09-19).

MACHINERY = ("subprojects/docket/src/docket/plan.py", "tools/generator_check.py")
WHY = "root_cause_faults is never called, so no claim is ever ranked"


def test_a_claim_touching_the_machinery_is_sound() -> None:
    item = _item(touches=("subprojects/docket/src/docket/plan.py",), impairs_generators=WHY)

    assert generator_defect_faults(item, MACHINERY) == ()
    assert impairs_generators_soundly(item, MACHINERY)


def test_a_claim_reaching_the_machinery_by_a_directory_prefix_is_sound() -> None:
    """`is_under` compares path segments, so a declared directory covers its files."""
    item = _item(touches=("tools/generator_check.py",), impairs_generators=WHY)

    assert generator_defect_faults(item, ("tools",)) == ()


def test_an_item_making_no_claim_has_no_faults_and_is_not_a_machinery_defect() -> None:
    """No field is silence, not a fault - and silence is not a claim either."""
    item = _item()

    assert generator_defect_faults(item, MACHINERY) == ()
    assert not impairs_generators_soundly(item, MACHINERY)


def test_a_claim_touching_none_of_the_machinery_is_refuted() -> None:
    item = _item(touches=("src/anesthesia_sim/core/blood.py",), impairs_generators=WHY)
    (fault,) = generator_defect_faults(item, MACHINERY)

    assert "none of which is inside" in fault
    assert not impairs_generators_soundly(item, MACHINERY)


def test_a_claim_declaring_no_touches_is_refuted() -> None:
    """Reported separately: 'declares nothing' and 'declares the wrong thing' repair differently."""
    item = _item(touches=(), impairs_generators=WHY)
    (fault,) = generator_defect_faults(item, MACHINERY)

    assert "declares no `touches`" in fault


def test_a_boolean_is_not_a_reason() -> None:
    """The field lifts an item above every band, so a reader is owed which function broke."""
    item = _item(touches=("subprojects/docket/src/docket/plan.py",), impairs_generators="yes")
    faults = generator_defect_faults(item, MACHINERY)

    assert any("not a boolean" in fault for fault in faults)


def test_a_project_declaring_no_machinery_refutes_every_claim() -> None:
    """Fail closed, and say which file to repair - the config, not the item."""
    item = _item(touches=("subprojects/docket/src/docket/plan.py",), impairs_generators=WHY)
    (fault,) = generator_defect_faults(item, ())

    assert "declares no `generator_paths`" in fault
