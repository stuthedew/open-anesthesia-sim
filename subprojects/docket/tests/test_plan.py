"""Tests for work selection.

The rule under test is the one that stops a project accumulating fifteen
features at five percent each: finishing something already started outranks
starting something new of equal priority.
"""

from __future__ import annotations

from datetime import date

from docket.model import Item
from docket.plan import (
    effort_total,
    features,
    gate,
    placement_clause,
    placement_line,
    placement_mark,
    promotable,
    recommend,
    recurring,
    set_aside,
)
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
    root_cause_of: tuple[str, ...] = (),
    generator: str = "",
    impairs_generators: str = "",
    verify: str = "",
    payoff: str = "",
    blocked_by: tuple[str, ...] = (),
    recurrences: tuple[str, ...] = (),
) -> Item:
    return Item(
        identifier=identifier,
        title=f"Item {identifier}",
        priority=priority,
        effort=effort,
        status=status,
        classes=classes,
        touches=touches,
        blocked_by=blocked_by,
        feature=feature,
        milestone="",
        added=date(2026, 8, 1),
        closed=None,
        commit="abc1234" if status == "done" else "",
        reason="",
        body="**Problem.** x\n**Why it matters.** y\n**Done when.** z\n",
        root_cause_of=root_cause_of,
        generator=generator,
        impairs_generators=impairs_generators,
        payoff=payoff,
        verify=verify,
        recurrences=recurrences,
    )


def test_a_third_recurrence_surfaces_a_promotion_candidate() -> None:
    """Three filings of one defect is the evidence the generator tier ranks on.

    `CLAUDE.md` pulls a root cause rather than queueing it because "every
    session it stands through pays it again", and a re-filing is that sentence
    happening once: a session hit the defect, had no idea an item existed, and
    paid the diagnosis again.

    An item at three recurrences is past the floor rather than at it - the
    boundary itself is `test_the_floor_is_two_recurrences_because_the_item_is_
    the_first_filing` below. Both are kept: this one is what `PL-X5JR`'s
    `verify:` was run against and its claim is still true, and a closed
    command is a record of what was run rather than a statement about today.
    """
    at_three = _item(
        "PL-2222", recurrences=("2026-09-18 PL-CCCC", "2026-09-19 PL-DDDD", "2026-09-20 PL-GGGG")
    )

    assert [item.identifier for item in recurring([at_three])] == ["PL-2222"]


def test_the_floor_is_two_recurrences_because_the_item_is_the_first_filing() -> None:
    """The generator rule's own number, counted in filings rather than in items.

    A generator is the root cause of three or more *items*. The item carrying
    the recurrences is itself the first filing, so two recurrences is three
    filings of one defect - the same cluster size. Written as a literal three,
    the counter would have demanded a fourth filing, which is a stricter bar
    than the rule it borrows its number from: measured over the five recorded
    clusters, the slug-rename one (`PL-LBR6` with `PL-5QLP` and `PL-QMC0`,
    recorded as a generator by hand) peaks at two and would never have
    surfaced (project owner, 2026-09-20, ratified).
    """
    at_one = _item("PL-1111", recurrences=("2026-09-18 PL-8888",))
    at_two = _item("PL-2222", recurrences=("2026-09-18 PL-BBBB", "2026-09-19 PL-CCCC"))

    assert [item.identifier for item in recurring([at_one, at_two])] == ["PL-2222"]


def test_a_repeated_capture_id_does_not_reach_the_threshold() -> None:
    """Counted over distinct captures, as the generator floor counts distinct ids.

    Three entries spelling one capture name one filing, and a floor a
    repetition defeats is not a floor.
    """
    repeated = _item(
        "PL-1111", recurrences=("2026-09-18 PL-8888", "2026-09-19 PL-8888", "2026-09-20 PL-8888")
    )

    assert recurring([repeated]) == []


def test_an_item_already_recorded_as_a_generator_is_not_offered_again() -> None:
    """It is on the tier already, so naming it as a candidate changes no decision."""
    known = _item(
        "PL-1111",
        root_cause_of=("PL-8888", "PL-BBBB", "PL-CCCC"),
        recurrences=("2026-09-18 PL-8888", "2026-09-19 PL-BBBB", "2026-09-20 PL-CCCC"),
    )
    members = [_item(i) for i in ("PL-8888", "PL-BBBB", "PL-CCCC")]

    assert recurring([known, *members]) == []


def test_a_closed_item_stops_being_a_candidate() -> None:
    """The defect it absorbed is fixed, so the cluster is no longer anybody's to pull."""
    closed = _item(
        "PL-1111",
        status="done",
        recurrences=("2026-09-18 PL-8888", "2026-09-19 PL-BBBB", "2026-09-20 PL-CCCC"),
    )

    assert recurring([closed]) == []


def test_an_item_in_flight_is_not_offered_for_promotion() -> None:
    """The window `root-cause-of:` acts in has closed, so the offer cannot be taken.

    A promotion moves a queue position and nothing else, and `recommend`
    excludes an in-flight id from the set it ranks - so a reader who confirms
    this cluster writes a claim nothing reads. `PL-W7WL` was ratified onto the
    tier on 2026-09-21 while it was being implemented, and the write would have
    been a no-op; `PL-GYRX` was dropped on the same reasoning about the sibling
    field (`PL-CJ5R`).
    """
    working = _item(
        "PL-1111", recurrences=("2026-09-18 PL-8888", "2026-09-19 PL-BBBB", "2026-09-20 PL-CCCC")
    )

    assert recurring([working], {"PL-1111"}) == []
    assert [item.identifier for item in recurring([working])] == ["PL-1111"]


def test_untriaged_and_blocked_clusters_are_still_offered() -> None:
    """Their window has not opened rather than closed, which is the opposite case.

    `_startable` excludes both, so neither ranks today - but a claim written
    onto an untriaged item ranks the moment triage seats it, and is exactly
    what a triage pass wants before choosing a band; one on a blocked item
    ranks when its blocker clears. Suppressing these to fix `PL-CJ5R` would
    trade that defect for the same defect pointing the other way.
    """
    filings = ("2026-09-18 PL-8888", "2026-09-19 PL-BBBB", "2026-09-20 PL-CCCC")
    untriaged = _item("PL-1111", status="untriaged", recurrences=filings)
    blocked = _item("PL-2222", status="blocked", recurrences=filings)

    assert [item.identifier for item in recurring([untriaged, blocked])] == ["PL-1111", "PL-2222"]


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


def test_a_recommendation_leads_with_what_the_work_buys() -> None:
    """Consequence above the ranking's own reason (`PL-WYKF`).

    The title names what the work does and `reason` says why it ranked; neither
    answers "why would I want this", which is the question an offer is read
    for. So the payoff sits between them rather than at the end.
    """
    payoff = "a renamed CI job stops blocking merges on a check that cannot arrive"
    (pick,) = recommend([_item("PL-1111", payoff=payoff)], limit=1)
    lines = pick.describe().splitlines()

    assert f"    payoff: {payoff}" in lines
    assert lines.index(f"    payoff: {payoff}") < len(lines) - 1


def test_a_recommendation_with_no_payoff_reads_as_it_always_did() -> None:
    """The field is adopted item by item, so its absence must cost nothing."""
    (pick,) = recommend([_item("PL-1111")], limit=1)

    assert "payoff" not in pick.describe()
    assert len(pick.describe().splitlines()) == 2


#: A store position that qualifies under every clause of `Item.delegability`:
#: `ready`, no safety or science class, a command that proves it, `S` effort,
#: and one declared path outside both lists below.
_DELEGABLE = {"verify": "pytest -q", "touches": ("tools/x.py",)}
_PROTECTED = ("src/core",)
_GATES = ("Makefile",)


def test_a_recommendation_offers_a_cheaper_model_when_the_item_qualifies() -> None:
    """The offer `docket list` already prints, on the command that recommends.

    `delegable` was derivable from the store the whole time and `docket next`
    said nothing about it, so the queue answered "what should I work on" and
    "what may a cheaper model work" in two different places (`PL-4MVC`).
    """
    (pick,) = recommend(
        [_item("PL-1111", **_DELEGABLE)], limit=1, protected_paths=_PROTECTED, gate_paths=_GATES
    )

    assert pick.delegable
    assert "cheaper model" in pick.describe()


def test_a_recommendation_offers_no_cheaper_model_where_nothing_is_protected() -> None:
    """Fail closed, and from the caller's end as well as `delegability`'s.

    A caller that threads no configuration has not said which of its files
    produce consequential output, and the safe reading of that silence is to
    offer nothing rather than to offer everything.
    """
    (pick,) = recommend([_item("PL-1111", **_DELEGABLE)], limit=1)

    assert not pick.delegable
    assert "cheaper model" not in pick.describe()


def test_the_strongest_model_mark_wins_over_the_cheaper_one() -> None:
    """One model answer per item, and the safety-classed answer is the one.

    `delegability` already returns the guidance string for a `safety`-classed
    item, so the two can never both be true; this is the regression test for a
    describe() that grew a second `if` and printed both.
    """
    (pick,) = recommend(
        [_item("PL-1111", classes=("safety",), priority="P1", **_DELEGABLE)],
        limit=1,
        protected_paths=_PROTECTED,
        gate_paths=_GATES,
    )

    said = pick.describe()
    assert "strongest model" in said
    assert "cheaper model" not in said


def test_an_item_touching_a_protected_path_is_not_offered_cheaply() -> None:
    """The partition that keeps clinical values off a delegated diff."""
    (pick,) = recommend(
        [_item("PL-1111", verify="pytest -q", touches=("src/core/pk.py",))],
        limit=1,
        protected_paths=_PROTECTED,
        gate_paths=_GATES,
    )

    assert not pick.delegable


def test_nothing_startable_yields_no_recommendations() -> None:
    assert recommend([]) == []


# --- what the plan says about an item, and what that does to the order ------

STEP = "v0.2.8 — the workflow works"


def _scope(
    *,
    current: tuple[str, ...] = (),
    later: dict[str, str] | None = None,
    excluded: tuple[str, ...] = (),
    step_label: str = "",
    clearing: bool = False,
    anchor: str = STEP,
) -> Scope:
    return Scope(
        anchor=anchor,
        current=frozenset(current),
        later=later or {},
        excluded=frozenset(excluded),
        step_label=step_label,
        clearing=clearing,
    )


def test_an_id_the_anchor_rules_out_says_so_and_ranks_below_the_undecided() -> None:
    """The fourth placement, which is `PL-6P9Y`.

    An id under the anchor's own `Explicitly out of scope` heading used to
    answer `unplaced` - the same answer as an id the roadmap has never
    considered - so it ranked between in-scope and out-of-scope work with no
    marking at all, while the section had actually taken a decision about it.

    Ranked *below* out-of-scope work rather than beside it: an out-of-scope id
    is waiting for its own step to come round, and this one has been ruled out.
    Both sentences say which, because the out-of-scope wording - "the current
    step has not reached it" - would be false here.
    """
    scope = _scope(current=("PL-2222",), later={"PL-3333": "v0.4.0"}, excluded=("PL-1111",))

    assert placement_line(scope, "PL-1111") == f"explicitly out of scope for {STEP}"
    assert placement_mark(scope, "PL-1111") == "[ruled out]"

    picks = recommend([_item("PL-1111"), _item("PL-3333")], scope=scope)

    assert [pick.item.identifier for pick in picks] == ["PL-3333", "PL-1111"]
    assert f"Explicitly out of scope for {STEP}" in picks[1].reason
    # Nothing *places* it, so the field that names a placing milestone is empty.
    assert picks[1].scoped_to == ""


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
    assert "the project stands on v0.3.0 — the foundation" in pick.reason
    assert "the step the project is on" not in pick.reason


def test_the_gate_reason_says_which_step_is_current_not_which_clears_the_gate() -> None:
    """`PL-TNB6`: the clause read "v0.4.x — the code is the model clears it" of
    a whole frozen gate. `ROADMAP.md`'s timeline makes the gate a row of its
    own after the patch track, and "The cadence" has cleared gate work ship
    inside the milestone that recorded it - so the line contradicted the plan
    on the one question the cadence exists to settle, in the command every
    session opens with. The row the project stands on is still worth naming;
    what it may not do is claim to clear anything."""
    scope = _scope(current=("PL-1111",), step_label="v0.4.x — the code is the model", clearing=True)

    (pick,) = recommend([_item("PL-1111")], scope=scope, limit=1)

    assert "clears it" not in pick.reason
    assert f"recorded under {STEP}, which clears before that milestone is implemented" in (
        pick.reason
    )
    assert "the project stands on v0.4.x — the code is the model" in pick.reason


def test_a_milestone_clearing_its_own_gate_still_reads_as_the_current_step() -> None:
    """The self-gating arrangement, where the two labels really are the same
    milestone and there is nothing to distinguish."""
    scope = _scope(current=("PL-1111",), clearing=True)

    (pick,) = recommend([_item("PL-1111")], scope=scope, limit=1)

    assert f"On the debt gate recorded under {STEP}, the step the project is on" in pick.reason
    # The regression `PL-MN0F` records: this is the branch that fires for a
    # milestone clearing its own gate, which is the ordinary arrangement, and
    # it used to be the only placement wording in the project that never said
    # "gate". Pinned here rather than left to the phrase above, so a reword
    # that drops the noun fails on the sentence that says why it matters.
    assert "debt gate" in pick.reason
    assert "frozen list" not in pick.reason


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
    """No roadmap, an unreadable one, or a plan with no milestone to anchor on.

    The third case is what `anchor=""` says, and until `PL-J790` the default
    helper stood in for it. That conflated two different silences: a plan that
    does not exist has nothing to say about where an id sits, while a plan that
    exists and places the id in no section is stating a fact. The test below
    pins the second; this one keeps the first reading exactly as it did.
    """
    items = [_item("PL-1111", priority="P1"), _item("PL-2222", priority="P3")]

    assert [p.item.identifier for p in recommend(items)] == ["PL-1111", "PL-2222"]
    assert recommend(items, scope=_scope(anchor=""))[0].reason == recommend(items)[0].reason


def test_an_unplaced_item_says_the_roadmap_places_it_nowhere() -> None:
    """The third placement spoke for the first time in `PL-J790`.

    `docket next` wrote a sentence for `IN_SCOPE` and for `OUT_OF_SCOPE` and
    nothing for `UNPLACED`, so a reason line carrying no gate sentence could
    not be told from a session that had never looked. The wording stays
    narrow deliberately: `Scope` reads a section's frozen list and its
    `Required scope` and nothing else, so a timeline row places nothing here
    and the claim is about sections rather than about the whole roadmap.
    """
    (pick,) = recommend([_item("PL-1111")], scope=_scope(current=("PL-2222",)), limit=1)

    assert f"Placed by no section of {STEP}" in pick.reason
    assert "ranks on its band alone" in pick.reason
    assert "A timeline row or prose may still place it." in pick.reason
    # Still not a verdict about exclusion, which is what `scoped_to` carries.
    assert pick.scoped_to == ""


def test_placement_line_answers_for_each_of_the_three_placements() -> None:
    """What `bin/docket show` prints, which said nothing at all before."""
    on_gate = _scope(current=("PL-1111",), clearing=True)
    assert placement_line(on_gate, "PL-1111") == f"on the debt gate recorded under {STEP}"

    in_scope = _scope(current=("PL-1111",))
    assert placement_line(in_scope, "PL-1111") == f"in scope for {STEP}"

    later = _scope(current=("PL-2222",), later={"PL-1111": "v0.4.0"})
    assert placement_line(later, "PL-1111") == f"outside what {STEP} names; placed by v0.4.0"

    unplaced = _scope(current=("PL-2222",))
    assert "placed by no section" in placement_line(unplaced, "PL-1111")


def test_placement_line_is_silent_when_there_is_no_plan_to_relate_to() -> None:
    """A missing or unreadable roadmap has no relation to state, unlike a gate."""
    assert placement_line(None, "PL-1111") == ""
    assert placement_line(_scope(anchor=""), "PL-1111") == ""


def test_placement_line_does_not_say_a_milestone_is_outside_itself() -> None:
    """While a gate is open, `later` also holds the anchor's own scope.

    `Scope.milestone` answers with a bare `v0.2.8` where `anchor` carries the
    roadmap's label, so the naive comparison never matched and the line read
    "outside what v0.2.8 - the workflow works names; placed by v0.2.8".
    """
    scope = _scope(current=("PL-2222",), later={"PL-1111": STEP.split()[0]}, clearing=True)

    assert placement_line(scope, "PL-1111") == (
        f"in the scope of {STEP}, which clearing its gate comes before"
    )


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
        _item("PL-PR0D", touches=("src/core/blood.py",)),
        _item("PL-W0RK", touches=("tools/doc_check.py",)),
    ]

    product = recommend(items, lane="product", workflow_paths=WORKFLOW)
    workflow = recommend(items, lane="workflow", workflow_paths=WORKFLOW)

    assert [p.item.identifier for p in product] == ["PL-PR0D"]
    assert [p.item.identifier for p in workflow] == ["PL-W0RK"]


def test_no_lane_ranks_the_whole_queue_exactly_as_before() -> None:
    """The unfiltered answer is the default and is not changed by the split existing."""
    items = [
        _item("PL-PR0D", touches=("src/core/blood.py",)),
        _item("PL-W0RK", touches=("tools/doc_check.py",)),
        _item("PL-B0TH", touches=("tools/doc_check.py", "src/core/blood.py")),
    ]

    picks = recommend(items, workflow_paths=WORKFLOW)

    assert {p.item.identifier for p in picks} == {"PL-PR0D", "PL-W0RK", "PL-B0TH"}


def test_work_reaching_both_halves_is_offered_to_neither_lane() -> None:
    items = [_item("PL-B0TH", touches=("tools/doc_check.py", "src/core/blood.py"))]

    assert recommend(items, lane="product", workflow_paths=WORKFLOW) == []
    assert recommend(items, lane="workflow", workflow_paths=WORKFLOW) == []


def test_a_lane_filters_and_never_reorders() -> None:
    """A lane changes what is eligible, not what the project's priorities are."""
    items = [
        _item("PL-L0W5", priority="P3", touches=("tools/a.py",)),
        _item("PL-H0T5", priority="P0", touches=("tools/b.py",)),
        _item("PL-M1D5", priority="P2", touches=("tools/c.py",)),
    ]

    picks = recommend(items, lane="workflow", workflow_paths=WORKFLOW)

    assert [p.item.identifier for p in picks] == ["PL-H0T5", "PL-M1D5", "PL-L0W5"]


def test_feature_progress_is_read_from_the_whole_store_not_from_the_lane() -> None:
    """How near a feature is to done is a fact about the feature, not about who asks.

    Counting only the lane's items would make the same feature report a
    different completion in each session, and the ranking rests on that number.
    """
    items = [
        _item("PL-D0N3", status="done", feature="alpha", touches=("src/core/a.py",)),
        _item("PL-0P3N", feature="alpha", touches=("tools/a.py",)),
        _item("PL-4L0N", touches=("tools/b.py",)),
    ]

    picks = recommend(items, lane="workflow", workflow_paths=WORKFLOW)

    assert picks[0].item.identifier == "PL-0P3N"
    assert "Finishes 'alpha'" in picks[0].reason


def test_set_aside_names_what_a_lane_could_not_claim_and_why() -> None:
    """A filter that silently drops a fifth of the queue is how work goes missing."""
    items = [
        _item("PL-PR0D", touches=("src/core/blood.py",)),
        _item("PL-B0TH", touches=("tools/a.py", "src/core/b.py")),
        _item("PL-N0N3", touches=()),
    ]

    held = set_aside(items, workflow_paths=WORKFLOW)

    assert [i.identifier for i in held.crossing] == ["PL-B0TH"]
    assert [i.identifier for i in held.unplaced] == ["PL-N0N3"]
    assert held.total == 2


def test_set_aside_applies_the_same_exclusions_the_ranking_did() -> None:
    """A count drawn from a different population describes a different ranking."""
    items = [
        _item("PL-B0TH", touches=("tools/a.py", "src/core/b.py")),
        _item("PL-FLY5", touches=("tools/c.py", "src/core/d.py")),
        _item("PL-B1G5", effort="L", touches=("tools/e.py", "src/core/f.py")),
        _item("PL-BL0K", status="blocked", touches=("tools/g.py", "src/core/h.py")),
    ]

    held = set_aside(items, {"PL-FLY5"}, workflow_paths=WORKFLOW, effort="S")

    assert [i.identifier for i in held.crossing] == ["PL-B0TH"]


def test_an_undeclared_boundary_places_nothing_in_a_lane() -> None:
    """Fail closed: with no boundary, no item is on either side of it."""
    items = [_item("PL-W0RK", touches=("tools/doc_check.py",))]

    assert recommend(items, lane="workflow") == []
    assert recommend(items, lane="product") == []


# `root-cause-of:` and the rank it buys.
#
# The project owner decided on 2026-09-17 that a generator ranks above
# everything but `P0`, and reaffirmed it when asked whether the clinical bands
# should be exempt: they are not. So the test that matters most here is
# `test_a_generator_outranks_a_safety_classed_p1` - it pins a decision that was
# put twice and refused twice, and a later session reading only `plan.py` would
# have every reason to think it was an oversight.
#
# The rest are the fail-closed half. `docket check` is a separate command, so a
# store is routinely ranked before it is validated; an unsound claim that
# ranked anyway would outrank a clinical defect on a typo.

GENERATOR = ("PL-G1G1", "PL-G2G2", "PL-G3G3")

# The recurrence verdict, which from `PL-T7QR` is the second of the two tests a
# generator has to pass to rank: the count decides that one is *recorded*, and
# this decides whether it ranks above every band but `P0`. Written out at every
# call site that means a ranking generator rather than defaulted in `_item`,
# because a test asserting the tier is asserting both halves and a default
# would hide one of them.
LIVE = "live - two more captures matched onto this path after the cluster was recorded"
SPENT = "spent - the parse every member stood on was deleted, so no new one can arrive"


def _explained() -> list[Item]:
    return [_item(identifier, priority="P3") for identifier in GENERATOR]


def test_a_spent_generator_ranks_on_its_own_band() -> None:
    """The recurrence test, which is the whole of what `PL-T7QR` added.

    The count and the verdict sit on different axes (project owner,
    2026-09-21, ratified): three items standing on one mechanism is what makes
    it *recorded*, and whether the store is still handing it members is what
    makes it *rank*. A cluster whose mechanism is spent did its damage and
    cannot do more, so it competes on its band like any other item - and the
    `safety`-classed `P1` below it goes first, which is the outcome the
    decision exists to produce.

    Recorded all the same: the claim is still sound, `clusters` still counts
    it, and `generators_explaining` still names it above its members. Only the
    rank moved.
    """
    picks = recommend(
        [
            _item("PL-1111", priority="P1", classes=("safety",)),
            _item("PL-5555", priority="P2", root_cause_of=GENERATOR, generator=SPENT),
            *_explained(),
        ],
        limit=2,
    )

    assert [p.item.identifier for p in picks] == ["PL-1111", "PL-5555"]


def test_a_recorded_generator_with_no_verdict_does_not_rank() -> None:
    """Opt-in, because `docket check` runs separately from `docket next`.

    A store is routinely ranked before it is validated - the argument
    `root_cause_faults` already makes about a mistyped id - so the unqualified
    state has to be the one that cannot buy a promotion over a clinical defect.
    The cost of that default is a live generator waiting on its band until the
    checker is run, which is recoverable and which `docket check` reports; the
    cost the other way is a spent cluster outranking a `safety`-classed `P1`,
    which is what the ratified decision removed.
    """
    picks = recommend(
        [
            _item("PL-1111", priority="P1", classes=("safety",)),
            _item("PL-5555", priority="P2", root_cause_of=GENERATOR),
            *_explained(),
        ],
        limit=2,
    )

    assert [p.item.identifier for p in picks] == ["PL-1111", "PL-5555"]


def test_a_spent_generator_is_not_told_it_ranked_as_one() -> None:
    """The reason line has to match the rank, or it teaches a reader to discount it.

    `recommend` says "Ranked as a generator" in those words so that a `P2` at
    the top of a list with `P1`s below it reads as the ranking meaning it. Said
    of an item that ranked on its band, the sentence asserts a promotion that
    did not happen - and `placement_line`'s "ranks on its band alone" clause,
    which a generator must not carry, is true of this one and must stay.
    """
    (pick,) = recommend(
        [_item("PL-5555", priority="P2", root_cause_of=GENERATOR, generator=SPENT), *_explained()],
        limit=1,
    )

    assert "Ranked as a generator" not in pick.reason
    assert pick.generator == 0


def test_a_generator_outranks_a_safety_classed_p1() -> None:
    """Asked and answered twice: a generator ranks above everything but P0."""
    picks = recommend(
        [
            _item("PL-9999", priority="P0"),
            _item("PL-1111", priority="P1", classes=("safety",)),
            _item("PL-5555", priority="P2", root_cause_of=GENERATOR, generator=LIVE),
            *_explained(),
        ],
        limit=3,
    )

    assert [p.item.identifier for p in picks] == ["PL-9999", "PL-5555", "PL-1111"]


def test_a_generator_outranks_work_the_current_step_includes() -> None:
    """Above `PLACEMENT_ORDER` too, which is what "every band" has to mean.

    Placement sits above band in the ranking, so a generator ranked only above
    `band` would still lose to any in-scope `P3`.
    """
    picks = recommend(
        [
            _item("PL-1111", priority="P1"),
            _item("PL-5555", priority="P3", root_cause_of=GENERATOR, generator=LIVE),
            *_explained(),
        ],
        scope=_scope(current=("PL-1111",)),
        limit=2,
    )

    assert [p.item.identifier for p in picks] == ["PL-5555", "PL-1111"]


def test_the_reason_says_it_was_ranked_as_a_generator() -> None:
    """A `P2` above a `P1` has to say the ranking meant it."""
    (pick,) = recommend(
        [_item("PL-5555", priority="P2", root_cause_of=GENERATOR, generator=LIVE), *_explained()],
        limit=1,
    )

    assert "Ranked as a generator" in pick.reason
    assert "root cause of 3 items" in pick.reason
    assert "PL-G1G1" in pick.reason
    assert pick.generator == 3
    assert "root cause of 3 items" in pick.describe()


def test_a_claim_naming_too_few_items_ranks_on_its_band() -> None:
    picks = recommend(
        [
            _item("PL-1111", priority="P1"),
            _item("PL-5555", priority="P2", root_cause_of=GENERATOR[:2]),
            *_explained(),
        ],
        limit=2,
    )

    assert [p.item.identifier for p in picks] == ["PL-1111", "PL-5555"]
    assert picks[1].generator == 0


def test_a_claim_naming_an_id_no_item_carries_ranks_on_its_band() -> None:
    """Fail closed: `docket check` runs separately, so a typo must not promote."""
    picks = recommend(
        [
            _item("PL-1111", priority="P1"),
            _item("PL-5555", priority="P2", root_cause_of=(*GENERATOR[:2], "PL-N0P3")),
            *_explained(),
        ],
        limit=2,
    )

    assert [p.item.identifier for p in picks] == ["PL-1111", "PL-5555"]


def test_a_claim_does_not_decay_as_the_items_it_explains_close() -> None:
    """A root cause still explains an item that has since closed."""
    closed = [_item(identifier, status="done") for identifier in GENERATOR]
    picks = recommend(
        [
            _item("PL-1111", priority="P1"),
            _item("PL-5555", root_cause_of=GENERATOR, generator=LIVE),
            *closed,
        ],
        limit=2,
    )

    assert [p.item.identifier for p in picks] == ["PL-5555", "PL-1111"]


def test_a_generator_in_flight_is_still_excluded() -> None:
    """The rank changes what is offered, never whether somebody else has it."""
    picks = recommend(
        [
            _item("PL-1111", priority="P1"),
            _item("PL-5555", root_cause_of=GENERATOR, generator=LIVE),
            *_explained(),
        ],
        {"PL-5555"},
        limit=2,
    )

    assert [p.item.identifier for p in picks] == ["PL-1111", "PL-G1G1"]


def test_a_generator_is_not_also_told_it_ranks_on_its_band_alone() -> None:
    """One reason line, one claim about how the item ranked.

    The unplaced-scope clause closes with "ranks on its band alone", which is
    true of everything except the one kind of item that does not: a generator
    ranked above every band. Both sentences in one line is the apparatus floor
    broken where a reader can see both at once.
    """
    (pick,) = recommend(
        [_item("PL-5555", priority="P2", root_cause_of=GENERATOR, generator=LIVE), *_explained()],
        scope=_scope(current=("PL-1111",)),
        limit=1,
    )

    assert "Placed by no section of" in pick.reason
    assert "ranks on its band alone" not in pick.reason
    assert "above every band but P0" in pick.reason


def test_an_ordinary_unplaced_item_still_says_it_ranks_on_its_band() -> None:
    (pick,) = recommend(
        [_item("PL-5555", priority="P2")], scope=_scope(current=("PL-1111",)), limit=1
    )

    assert "ranks on its band alone" in pick.reason


# --- the tier's other entrance: a defect in the machinery itself ------------

MACHINERY = ("subprojects/docket/src/docket/plan.py",)
IMPAIRS = "docket show prints no reverse edge, so a member cannot see its head"


def test_a_generator_machinery_defect_ranks_with_a_generator() -> None:
    """Project owner, 2026-09-19: the same priority as a generator, not below it.

    Both entrances feed one rank term, so the two are genuinely on a tier and
    the ordinary terms settle which comes first - here the band, since neither
    is placed and neither is in an underway feature. A design ordering them
    against each other would have been a sub-order nobody asked for.
    """
    picks = recommend(
        [
            _item("PL-9999", priority="P0"),
            _item("PL-1111", priority="P1", classes=("safety",)),
            _item("PL-5555", priority="P2", root_cause_of=GENERATOR, generator=LIVE),
            _item("PL-7777", priority="P2", touches=MACHINERY, impairs_generators=IMPAIRS),
            *_explained(),
        ],
        limit=4,
        generator_paths=MACHINERY,
    )

    assert [p.item.identifier for p in picks][:3] == ["PL-9999", "PL-5555", "PL-7777"]
    assert picks[3].item.identifier == "PL-1111"


def test_a_machinery_defect_outranks_a_safety_classed_p1() -> None:
    """The consequence the owner accepted for generators, inherited by the child rule."""
    picks = recommend(
        [
            _item("PL-1111", priority="P1", classes=("safety",)),
            _item("PL-7777", priority="P3", touches=MACHINERY, impairs_generators=IMPAIRS),
        ],
        limit=2,
        generator_paths=MACHINERY,
    )

    assert [p.item.identifier for p in picks] == ["PL-7777", "PL-1111"]


def test_a_claim_touching_none_of_the_machinery_ranks_on_its_band() -> None:
    """The falsifier. `docket check` runs separately, so a false claim must not promote."""
    picks = recommend(
        [
            _item("PL-1111", priority="P1"),
            _item(
                "PL-7777",
                priority="P2",
                touches=("src/anesthesia_sim/core/blood.py",),
                impairs_generators=IMPAIRS,
            ),
        ],
        limit=2,
        generator_paths=MACHINERY,
    )

    assert [p.item.identifier for p in picks] == ["PL-1111", "PL-7777"]
    assert not picks[1].impairs_generators


def test_a_claim_is_unsound_where_the_project_declares_no_machinery() -> None:
    """Fail closed, like `protected_paths` and `workflow_paths` before it.

    With nothing declared, no item can be shown to touch the machinery, so
    every claim is unsound. Defaulting the other way would hand the tier to
    any project that never read the setting.
    """
    picks = recommend(
        [
            _item("PL-1111", priority="P1"),
            _item("PL-7777", priority="P2", touches=MACHINERY, impairs_generators=IMPAIRS),
        ],
        limit=2,
    )

    assert [p.item.identifier for p in picks] == ["PL-1111", "PL-7777"]


def test_the_reason_quotes_the_declared_prose_rather_than_asserting_the_promotion() -> None:
    """The prose is the only evidence a reader has, so the line that acts on it shows it."""
    (pick,) = recommend(
        [_item("PL-7777", priority="P2", touches=MACHINERY, impairs_generators=IMPAIRS)],
        limit=1,
        generator_paths=MACHINERY,
    )

    assert "Ranked as a defect in the generator machinery" in pick.reason
    assert "reverse edge" in pick.reason
    assert "above every band but P0" in pick.reason
    assert pick.impairs_generators
    assert pick.generator == 0
    assert "root cause of" not in pick.describe()
    assert "defect in the generator machinery" in pick.describe()


def test_an_unplaced_machinery_defect_does_not_claim_to_rank_on_its_band() -> None:
    """Same falsehood the generator tail already refuses - it did not rank on its band."""
    (pick,) = recommend(
        [_item("PL-7777", priority="P2", touches=MACHINERY, impairs_generators=IMPAIRS)],
        scope=_scope(current=("PL-1111",)),
        limit=1,
        generator_paths=MACHINERY,
    )

    assert "Placed by no section of" in pick.reason
    assert "ranks on its band alone" not in pick.reason


def test_the_plan_line_does_not_tell_a_tier_item_it_ranks_on_its_band() -> None:
    """`docket show`'s header, which asserted this on every generator in the store.

    `recommend` has refused the sentence since the tier existed, but that
    wording only reaches a session that asked for a ranking. Naming an item
    reaches `placement_line` instead - the path the project owner usually
    starts work on.
    """
    unplaced = _scope(current=("PL-2222",))

    assert "ranks on its band alone" in placement_line(unplaced, "PL-1111")
    above = placement_line(unplaced, "PL-1111", ranks_above_bands=True)
    assert "ranks on its band alone" not in above
    assert "ranks above every band but P0" in above


# --- placement_clause: the relation in the fewest plain words ---------------
#
# `PL-Z27P`. The two lines that name an item with no room for a sentence -
# `docket next`'s `Lane of this answer:` and the digest's `By lane:` - printed
# a bare id, so the project owner met the workflow lane once per command and
# once per session with nothing saying why anything ranked. These pin the
# clause that replaced it, and in particular that it agrees with the sentence
# `placement_line` prints for the same item.


def test_the_clause_names_the_gate_while_a_gate_is_open() -> None:
    scope = _scope(current=("PL-1111",), clearing=True)

    assert placement_clause(scope, "PL-1111") == "on the debt gate"
    assert placement_clause(scope, "PL-2222") == "not on the gate"


def test_the_clause_never_names_a_gate_once_the_gate_is_clear() -> None:
    """With nothing frozen there is no gate to be off, so "not on the gate"
    would be true of every item in the store and informative about none."""
    scope = _scope(current=("PL-1111",))

    assert placement_clause(scope, "PL-1111") == f"in scope for {STEP}"
    assert "gate" not in placement_clause(scope, "PL-2222")


def test_the_clause_separates_the_anchor_s_own_scope_from_a_later_release() -> None:
    """While a gate is open the anchor's own `Required scope` is mapped to the
    anchor, and that says "this is what the gate clears the way for" rather
    than "a later release owns this" - the distinction `placement_line` draws
    on the same test."""
    anchor_version = STEP.split()[0]
    scope = _scope(later={"PL-1111": anchor_version, "PL-2222": "v0.9.0"}, clearing=True)

    assert (
        placement_clause(scope, "PL-1111")
        == "not on the gate; it is what the gate clears the way for"
    )
    assert placement_clause(scope, "PL-2222") == "not on the gate; placed by v0.9.0"


def test_the_clause_reports_a_ruled_out_id_as_a_decision_taken() -> None:
    scope = _scope(excluded=("PL-1111",), clearing=True)

    assert placement_clause(scope, "PL-1111") == f"ruled out of {STEP}"


def test_the_clause_is_empty_without_a_roadmap_so_the_band_stands_alone() -> None:
    """Fail quiet rather than asserting a relation nothing established."""
    assert placement_clause(None, "PL-1111") == ""
    assert placement_clause(_scope(anchor=""), "PL-1111") == ""


def test_the_clause_and_the_sentence_agree_about_gate_membership() -> None:
    """Three renderers of one relation, and the risk is that they drift: the
    defect this feature started from was `docket next` alone calling the debt
    gate a "frozen list" (`PL-MN0F`)."""
    scope = _scope(current=("PL-1111",), clearing=True)

    assert "debt gate" in placement_clause(scope, "PL-1111")
    assert "debt gate" in placement_line(scope, "PL-1111")
    assert placement_mark(scope, "PL-1111") == "[gate]"


def test_an_item_whose_every_blocker_has_closed_is_reported_promotable() -> None:
    """The defect `PL-6T44` was filed for: `_startable` filters on `status` and
    never opens `blocked_by`, so an item ranked as unstartable long after the
    thing it waited for closed. `docket check` derived this all along and
    `docket next` never showed it."""
    closed = _item("PL-1111", status="done")
    waiting = _item("PL-2222", status="blocked", blocked_by=("PL-1111",))

    assert [i.identifier for i in promotable([closed, waiting])] == ["PL-2222"]


def test_a_dropped_blocker_counts_as_closed_like_a_done_one() -> None:
    """`dropped` sits beside `done` in `CLOSED_STATUSES`, and an item dropped
    with a reason is as finished as one that was built."""
    dropped = _item("PL-1111", status="dropped")
    waiting = _item("PL-2222", status="blocked", blocked_by=("PL-1111",))

    assert [i.identifier for i in promotable([dropped, waiting])] == ["PL-2222"]


def test_one_blocker_still_open_holds_the_whole_item() -> None:
    closed = _item("PL-1111", status="done")
    still_open = _item("PL-3333", status="ready")
    waiting = _item("PL-2222", status="blocked", blocked_by=("PL-1111", "PL-3333"))

    assert promotable([closed, still_open, waiting]) == []


def test_an_unknown_blocker_is_read_as_unresolved_rather_than_absent() -> None:
    """Fail-closed: a `blocked-by` the store cannot place is not evidence that
    the blocker closed, and saying otherwise on a field deciding what may be
    started is the wrong way to fail."""
    waiting = _item("PL-2222", status="blocked", blocked_by=("PL-9999",))

    assert promotable([waiting]) == []


def test_a_milestone_blocker_is_left_to_the_roadmap() -> None:
    """A milestone blocker clears when a scoping round happens, not when an
    item closes, so it takes the roadmap to answer. `checks.py` keeps that
    branch; `PL-162Y` is whether `next` should name those too."""
    closed = _item("PL-1111", status="done")
    waiting = _item("PL-2222", status="blocked", blocked_by=("PL-1111", "v0.6.0"))

    assert promotable([closed, waiting]) == []


def test_an_item_declaring_no_blocker_at_all_is_not_promotable() -> None:
    """`status: blocked` with an empty `blocked-by` is a different defect, and
    `checks.py` already errors on it by name. Reporting it here would tell a
    session to promote an item whose reason for waiting nobody wrote down."""
    assert promotable([_item("PL-2222", status="blocked")]) == []


def test_only_a_blocked_item_is_promotable() -> None:
    """A `ready` item carrying a closed edge is already rankable, and a
    `needs-decision` one is waiting on an answer rather than on a blocker."""
    closed = _item("PL-1111", status="done")
    ready = _item("PL-2222", status="ready", blocked_by=("PL-1111",))
    deciding = _item("PL-3333", status="needs-decision", blocked_by=("PL-1111",))

    assert promotable([closed, ready, deciding]) == []


def test_promotable_items_are_named_but_never_ranked() -> None:
    """The decision `PL-6T44` records. Of 13 items reached this way across two
    grooming passes, 6 were genuinely startable; ranking the rest would have
    put an unbuildable item into `P1` and onto the debt gate, because leaving
    `blocked` is what ends the `anticipated` exemption. So `recommend` still
    excludes them and the caller names them instead."""
    closed = _item("PL-1111", status="done")
    waiting = _item("PL-2222", status="blocked", blocked_by=("PL-1111",))
    items = [closed, waiting]

    assert [i.identifier for i in promotable(items)] == ["PL-2222"]
    assert [pick.item.identifier for pick in recommend(items)] == []


def test_the_report_is_ordered_so_two_readers_see_one_answer() -> None:
    """`docket check` and `docket next` print the same set, so the set has to
    come back in the same order however the store was loaded."""
    closed = _item("PL-1111", status="done")
    first = _item("PL-2222", status="blocked", blocked_by=("PL-1111",))
    second = _item("PL-3333", status="blocked", blocked_by=("PL-1111",))

    assert [i.identifier for i in promotable([second, closed, first])] == ["PL-2222", "PL-3333"]
