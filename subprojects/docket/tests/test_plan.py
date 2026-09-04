"""Tests for work selection.

The rule under test is the one that stops a project accumulating fifteen
features at five percent each: finishing something already started outranks
starting something new of equal priority.
"""

from __future__ import annotations

from datetime import date

from docket.model import Item
from docket.plan import effort_total, features, gate, recommend, set_aside
from docket.roadmap import Scope, milestone_scope, parse_milestones


def _item(
    identifier: str,
    *,
    priority: str = "P2",
    status: str = "ready",
    feature: str = "",
    effort: str = "S",
    classes: tuple[str, ...] = ("perf",),
    touches: tuple[str, ...] = ("a.py",),
) -> Item:
    return Item(
        identifier=identifier,
        title=f"Item {identifier}",
        priority=priority,
        effort=effort,
        status=status,
        classes=classes,
        touches=touches,
        blocked_by=(),
        feature=feature,
        milestone="",
        added=date(2026, 8, 1),
        closed=None,
        commit="abc1234" if status == "done" else "",
        reason="",
        body="**Problem.** x\n**Why it matters.** y\n**Done when.** z\n",
    )


def test_features_group_their_items() -> None:
    grouped = features([_item("PL-1111", feature="alpha"), _item("PL-2222", feature="alpha")])

    assert list(grouped) == ["alpha"]
    assert len(grouped["alpha"].items) == 2


def test_a_feature_is_underway_only_when_partly_done() -> None:
    started = features(
        [_item("PL-1111", feature="a", status="done"), _item("PL-2222", feature="a")]
    )
    untouched = features([_item("PL-3333", feature="b")])

    assert started["a"].is_underway
    assert not untouched["b"].is_underway


def test_p0_outranks_everything() -> None:
    picks = recommend(
        [
            _item("PL-1111", priority="P2", feature="a", status="done"),
            _item("PL-2222", priority="P2", feature="a"),
            _item("PL-3333", priority="P0"),
        ]
    )

    assert picks[0].item.identifier == "PL-3333"
    assert "P0" in picks[0].reason


def test_finishing_a_started_feature_beats_equal_priority_new_work() -> None:
    items = [
        _item("PL-1111", priority="P2", feature="alpha", status="done"),
        _item("PL-2222", priority="P2", feature="alpha"),
        _item("PL-3333", priority="P2"),
    ]
    picks = recommend(items)

    assert picks[0].item.identifier == "PL-2222"
    assert "Finishes 'alpha'" in picks[0].reason


def test_the_feature_nearest_completion_outranks_a_smaller_item() -> None:
    """The case that exposed PL-B0YN, in the shape it was observed.

    Two ready items of equal band, each in an underway feature, and the
    *smaller* one is in the feature with further to go. Before the fix the tie
    fell through to effort, so `alpha` at one item from done lost to `beta`
    with three left - while the rationale line printed beside the winner was
    the argument for the loser.
    """
    items = [
        _item("PL-1111", feature="alpha", status="done"),
        _item("PL-2222", feature="alpha", effort="M"),
        _item("PL-3333", feature="beta", status="done"),
        _item("PL-4444", feature="beta", effort="S"),
        _item("PL-5555", feature="beta", effort="S"),
        _item("PL-6666", feature="beta", effort="S"),
    ]

    assert recommend(items)[0].item.identifier == "PL-2222"


def test_an_item_with_others_open_does_not_claim_to_finish_the_feature() -> None:
    """PL-G1MF: a sentence may not assert and then withdraw the same claim."""
    items = [
        _item("PL-1111", feature="alpha", status="done"),
        _item("PL-2222", feature="alpha"),
        _item("PL-3333", feature="alpha"),
    ]
    (reason,) = {p.reason for p in recommend(items) if p.item.identifier == "PL-2222"}

    assert "Finishes" not in reason
    assert "Advances 'alpha'" in reason
    assert "2 items left" in reason


def test_the_last_open_item_is_still_described_as_finishing_its_feature() -> None:
    items = [_item("PL-1111", feature="alpha", status="done"), _item("PL-2222", feature="alpha")]
    (pick,) = recommend(items, limit=1)

    assert "Finishes 'alpha' - its last open item." in pick.reason


def test_priority_still_wins_over_feature_progress() -> None:
    """Finishing things matters, but not more than the band does."""
    items = [
        _item("PL-1111", priority="P3", feature="alpha", status="done"),
        _item("PL-2222", priority="P3", feature="alpha"),
        _item("PL-3333", priority="P1"),
    ]

    assert recommend(items)[0].item.identifier == "PL-3333"


def test_work_already_in_flight_is_excluded() -> None:
    """Recommending what someone is doing is worse than recommending nothing."""
    items = [_item("PL-1111", priority="P1"), _item("PL-2222", priority="P2")]
    picks = recommend(items, in_flight={"PL-1111"})

    assert [p.item.identifier for p in picks] == ["PL-2222"]


def test_blocked_and_untriaged_work_is_never_recommended() -> None:
    items = [_item("PL-1111", status="blocked"), _item("PL-2222", status="untriaged")]

    assert recommend(items) == []


def test_effort_filters_to_what_fits_the_time_available() -> None:
    items = [
        _item("PL-1111", priority="P1", effort="L"),
        _item("PL-2222", priority="P2", effort="S"),
    ]

    assert [p.item.identifier for p in recommend(items, effort="S")] == ["PL-2222"]


def test_a_recommendation_says_which_model_the_work_warrants() -> None:
    (pick,) = recommend([_item("PL-1111", classes=("safety",), priority="P1")], limit=1)

    assert "strongest model" in pick.describe()


def test_nothing_startable_yields_no_recommendations() -> None:
    assert recommend([]) == []


# --- what the plan says about an item, and what that does to the order ------

STEP = "v0.2.8 — the workflow works"


def _scope(
    *,
    current: tuple[str, ...] = (),
    later: dict[str, str] | None = None,
    step_label: str = "",
    clearing: bool = False,
) -> Scope:
    return Scope(
        anchor=STEP,
        current=frozenset(current),
        later=later or {},
        step_label=step_label,
        clearing=clearing,
    )


def test_next_marks_a_suggestion_scoped_to_a_milestone_this_step_has_not_reached() -> None:
    """The fact the ranking is missing, stated on the line rather than acted on."""
    scope = _scope(later={"PL-1111": "v0.4.0"})

    (pick,) = recommend([_item("PL-1111")], scope=scope, limit=1)

    assert pick.scoped_to == "v0.4.0"
    assert "scoped to v0.4.0, not this step" in pick.describe()
    assert "the current step has not reached" in pick.reason


def test_next_does_not_mark_work_the_current_step_scopes() -> None:
    (pick,) = recommend([_item("PL-1111")], scope=_scope(current=("PL-1111",)), limit=1)

    assert pick.scoped_to == ""
    assert f"In scope for {STEP}" in pick.reason


def test_next_leaves_an_item_unmarked_when_no_milestone_section_scopes_it() -> None:
    """Most of the queue is named nowhere, and silence is not a verdict."""
    (pick,) = recommend([_item("PL-1111")], scope=_scope(current=("PL-2222",)), limit=1)

    assert pick.scoped_to == ""
    assert "scoped to" not in pick.describe()


# The paragraph that found this, quoted from `ROADMAP.md`'s v0.2.8 section as
# it stood on 2026-09-01, with one entry of the same frozen list above it.
# Quoted here rather than read from the file, so the case outlives the release
# that rewrites the section.
EXCLUDING_ROADMAP = """# Roadmap

## Next release: v0.2.8 - the workflow works

### Debt gate: the frozen list

- PL-1TPM (S) `docket next` ranks work the current milestone excludes, with no
  sign that it does

PL-68XK (check that a recorded commit hash resolves) is a different case and is
*not* admitted by this rule: it predates the freeze and was excluded from the
approved list deliberately.
"""


def test_next_claims_no_scope_for_an_id_the_step_names_for_its_exclusion() -> None:
    """The whole path, because the reason string is what a session acts on.

    Roadmap prose to parse to ranking to the printed reason, which is where
    this went wrong: `docket next` on `main` ranked PL-68XK second under "In
    scope for v0.2.8 — the workflow works", read out of the paragraph below
    saying PL-68XK is not admitted. Above three genuine entries, with a reason
    stating the opposite of its source.
    """
    (section,) = parse_milestones(EXCLUDING_ROADMAP)
    scope = milestone_scope([section], section)

    picks = {
        pick.item.identifier: pick
        for pick in recommend([_item("PL-68XK"), _item("PL-1TPM")], scope=scope)
    }

    assert f"In scope for {STEP}" in picks["PL-1TPM"].reason
    assert "In scope" not in picks["PL-68XK"].reason
    assert picks["PL-68XK"].scoped_to == ""


def test_in_scope_work_outranks_out_of_scope_work_across_bands_not_within_one() -> None:
    """Absolute, because the band cannot express the phase.

    `docket check` pins `safety` and `science` items to P1, so the top band is
    product work by construction: a preference that only broke ties inside a
    band would never fire in the case this exists for.
    """
    items = [_item("PL-1111", priority="P1"), _item("PL-2222", priority="P3")]
    scope = _scope(current=("PL-2222",), later={"PL-1111": "v0.4.0"})

    assert [p.item.identifier for p in recommend(items, scope=scope)] == ["PL-2222", "PL-1111"]


def test_work_no_section_names_ranks_between_in_scope_and_out_of_scope_work() -> None:
    items = [
        _item("PL-1111", priority="P1"),
        _item("PL-2222", priority="P3"),
        _item("PL-3333", priority="P1"),
    ]
    scope = _scope(current=("PL-2222",), later={"PL-1111": "v0.4.0"})

    picks = [p.item.identifier for p in recommend(items, scope=scope)]

    assert picks == ["PL-2222", "PL-3333", "PL-1111"]


def test_out_of_scope_work_is_still_offered_when_no_in_scope_work_is_ready() -> None:
    """Marking is a fact the tool can support; hiding would be a verdict it cannot."""
    scope = _scope(current=("PL-9999",), later={"PL-1111": "v0.4.0", "PL-2222": "v0.4.0"})

    picks = recommend([_item("PL-1111"), _item("PL-2222")], scope=scope)

    assert [p.item.identifier for p in picks] == ["PL-1111", "PL-2222"]
    assert all(p.scoped_to == "v0.4.0" for p in picks)


def test_a_gate_shipping_as_another_version_is_not_called_the_current_step() -> None:
    """PL-1J0P: `next` said "the step the project is on" of the milestone that
    *records* the gate, while `wave` named a different step in the same
    session. The two commands a session reads at its start contradicted each
    other about which release the project was working on, for every entry of
    the release."""
    scope = _scope(current=("PL-1111",), step_label="v0.3.0 — the foundation", clearing=True)

    (pick,) = recommend([_item("PL-1111")], scope=scope, limit=1)

    assert f"On the debt gate recorded under {STEP}" in pick.reason
    assert "v0.3.0 — the foundation clears it" in pick.reason
    assert "the step the project is on" not in pick.reason


def test_a_milestone_clearing_its_own_gate_still_reads_as_the_current_step() -> None:
    """The self-gating arrangement, where the two labels really are the same
    milestone and there is nothing to distinguish."""
    scope = _scope(current=("PL-1111",), clearing=True)

    (pick,) = recommend([_item("PL-1111")], scope=scope, limit=1)

    assert f"On {STEP}'s frozen list, the step the project is on" in pick.reason


def test_in_scope_work_outside_a_gate_never_claims_a_step_it_is_not() -> None:
    """The third arrangement: the gate is clear, so the anchor's own scope is
    current work, but the row the project stands on is still an earlier one."""
    scope = _scope(current=("PL-1111",), step_label="v0.3.0 — the foundation")

    (pick,) = recommend([_item("PL-1111")], scope=scope, limit=1)

    assert f"In scope for {STEP}" in pick.reason
    assert "v0.3.0 — the foundation) comes before" in pick.reason
    assert "debt gate" not in pick.reason


def test_p0_outranks_in_scope_work_because_a_hotfix_outranks_the_phase() -> None:
    items = [_item("PL-1111", priority="P3"), _item("PL-2222", priority="P0")]
    scope = _scope(current=("PL-1111",), later={"PL-2222": "v0.4.0"})

    picks = recommend(items, scope=scope)

    assert picks[0].item.identifier == "PL-2222"
    assert "P0" in picks[0].reason and picks[0].scoped_to == "v0.4.0"


def test_a_ranking_given_no_plan_reads_as_it_did_before_there_was_one() -> None:
    """No roadmap, an unreadable one, or a plan with no milestone to anchor on."""
    items = [_item("PL-1111", priority="P1"), _item("PL-2222", priority="P3")]

    assert [p.item.identifier for p in recommend(items)] == ["PL-1111", "PL-2222"]
    assert recommend(items, scope=_scope())[0].reason == recommend(items)[0].reason


DEBT_CLASSES = ("defect", "safety", "science", "refactor", "perf")


def _debt_item(identifier: str, **overrides: object) -> Item:
    base: dict[str, object] = dict(
        identifier=identifier,
        title=identifier,
        priority="P2",
        effort="S",
        status="ready",
        classes=("defect",),
        touches=(),
        blocked_by=(),
        feature="",
        milestone="",
        added=date(2026, 8, 1),
        closed=None,
        commit="",
        reason="",
        body="",
    )
    base.update(overrides)
    # Splatting `dict[str, object]` matches `object` against every field's type; the
    # alternatives are `dict[str, Any]` or an `Unpack[TypedDict]` restating all of
    # `Item`'s fields, both wider than this line-scoped ignore.
    return Item(**base)  # type: ignore[arg-type]


def test_the_gate_splits_debt_by_whether_the_milestone_clears_it() -> None:
    """Debt inside the milestone's own scope is cleared by it, not before it."""
    items = [
        _debt_item("PL-0001", feature="teachable-case"),
        _debt_item("PL-0002"),
        _debt_item("PL-0003", classes=("feature",)),
    ]

    computed = gate(items, "teachable-case", DEBT_CLASSES)

    assert [i.identifier for i in computed.inside] == ["PL-0001"]
    assert [i.identifier for i in computed.outside] == ["PL-0002"]


def test_feature_and_planning_work_is_not_debt() -> None:
    """Counting it would make the rule say 'do everything before doing anything'."""
    items = [
        _debt_item("PL-0001", classes=("feature",)),
        _debt_item("PL-0002", classes=("planning",)),
    ]

    assert gate(items, "", DEBT_CLASSES).items == []


def test_an_unanswered_decision_is_debt_whatever_it_is_about() -> None:
    """A decision left open stops being one anybody can make."""
    item = _debt_item("PL-0001", classes=("feature",), status="needs-decision")

    assert gate([item], "", DEBT_CLASSES).items == [item]


def test_closed_work_is_not_debt() -> None:
    items = [
        _debt_item("PL-0001", status="done", commit="abc1234", closed=date(2026, 8, 2)),
        _debt_item("PL-0002", status="dropped", reason="no", closed=date(2026, 8, 2)),
    ]

    assert gate(items, "", DEBT_CLASSES).items == []


def test_the_effort_total_reads_largest_first_and_names_what_is_unsized() -> None:
    items = [
        _debt_item("PL-0001", effort="M"),
        _debt_item("PL-0002"),
        _debt_item("PL-0003", effort=""),
    ]

    assert effort_total(items) == "1 M, 1 S, 1 unsized"


def test_the_gate_is_stable_for_a_given_store() -> None:
    """A list that reorders between runs cannot be compared with the recorded one."""
    items = [_debt_item("PL-0003"), _debt_item("PL-0001", priority="P1"), _debt_item("PL-0002")]

    first = [i.identifier for i in gate(items, "", DEBT_CLASSES).items]

    assert first == [i.identifier for i in gate(list(reversed(items)), "", DEBT_CLASSES).items]
    assert first == ["PL-0001", "PL-0002", "PL-0003"]


WORKFLOW = ("tools", ".claude")


def test_a_lane_offers_only_its_own_half_of_the_project() -> None:
    """The whole point: two sessions asking at once must not be handed one item."""
    items = [
        _item("PL-PROD", touches=("src/core/blood.py",)),
        _item("PL-WORK", touches=("tools/doc_check.py",)),
    ]

    product = recommend(items, lane="product", workflow_paths=WORKFLOW)
    workflow = recommend(items, lane="workflow", workflow_paths=WORKFLOW)

    assert [p.item.identifier for p in product] == ["PL-PROD"]
    assert [p.item.identifier for p in workflow] == ["PL-WORK"]


def test_no_lane_ranks_the_whole_queue_exactly_as_before() -> None:
    """The unfiltered answer is the default and is not changed by the split existing."""
    items = [
        _item("PL-PROD", touches=("src/core/blood.py",)),
        _item("PL-WORK", touches=("tools/doc_check.py",)),
        _item("PL-BOTH", touches=("tools/doc_check.py", "src/core/blood.py")),
    ]

    picks = recommend(items, workflow_paths=WORKFLOW)

    assert {p.item.identifier for p in picks} == {"PL-PROD", "PL-WORK", "PL-BOTH"}


def test_work_reaching_both_halves_is_offered_to_neither_lane() -> None:
    items = [_item("PL-BOTH", touches=("tools/doc_check.py", "src/core/blood.py"))]

    assert recommend(items, lane="product", workflow_paths=WORKFLOW) == []
    assert recommend(items, lane="workflow", workflow_paths=WORKFLOW) == []


def test_a_lane_filters_and_never_reorders() -> None:
    """A lane changes what is eligible, not what the project's priorities are."""
    items = [
        _item("PL-LOW", priority="P3", touches=("tools/a.py",)),
        _item("PL-HOT", priority="P0", touches=("tools/b.py",)),
        _item("PL-MID", priority="P2", touches=("tools/c.py",)),
    ]

    picks = recommend(items, lane="workflow", workflow_paths=WORKFLOW)

    assert [p.item.identifier for p in picks] == ["PL-HOT", "PL-MID", "PL-LOW"]


def test_feature_progress_is_read_from_the_whole_store_not_from_the_lane() -> None:
    """How near a feature is to done is a fact about the feature, not about who asks.

    Counting only the lane's items would make the same feature report a
    different completion in each session, and the ranking rests on that number.
    """
    items = [
        _item("PL-DONE", status="done", feature="alpha", touches=("src/core/a.py",)),
        _item("PL-OPEN", feature="alpha", touches=("tools/a.py",)),
        _item("PL-ALON", touches=("tools/b.py",)),
    ]

    picks = recommend(items, lane="workflow", workflow_paths=WORKFLOW)

    assert picks[0].item.identifier == "PL-OPEN"
    assert "Finishes 'alpha'" in picks[0].reason


def test_set_aside_names_what_a_lane_could_not_claim_and_why() -> None:
    """A filter that silently drops a fifth of the queue is how work goes missing."""
    items = [
        _item("PL-PROD", touches=("src/core/blood.py",)),
        _item("PL-BOTH", touches=("tools/a.py", "src/core/b.py")),
        _item("PL-NONE", touches=()),
    ]

    held = set_aside(items, workflow_paths=WORKFLOW)

    assert [i.identifier for i in held.crossing] == ["PL-BOTH"]
    assert [i.identifier for i in held.unplaced] == ["PL-NONE"]
    assert held.total == 2


def test_set_aside_applies_the_same_exclusions_the_ranking_did() -> None:
    """A count drawn from a different population describes a different ranking."""
    items = [
        _item("PL-BOTH", touches=("tools/a.py", "src/core/b.py")),
        _item("PL-FLY", touches=("tools/c.py", "src/core/d.py")),
        _item("PL-BIG", effort="L", touches=("tools/e.py", "src/core/f.py")),
        _item("PL-BLOK", status="blocked", touches=("tools/g.py", "src/core/h.py")),
    ]

    held = set_aside(items, {"PL-FLY"}, workflow_paths=WORKFLOW, effort="S")

    assert [i.identifier for i in held.crossing] == ["PL-BOTH"]


def test_an_undeclared_boundary_places_nothing_in_a_lane() -> None:
    """Fail closed: with no boundary, no item is on either side of it."""
    items = [_item("PL-WORK", touches=("tools/doc_check.py",))]

    assert recommend(items, lane="workflow") == []
    assert recommend(items, lane="product") == []
