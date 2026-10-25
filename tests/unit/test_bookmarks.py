"""Test what a mark rejects, and how the two collections keep the two kinds of mark apart.

`app/bookmarks.py` decides nothing about a run. It decides what a learner is
allowed to have *asked*. So the claims here are all about the boundary: which
values are refused, and with what message. They are also about the two
collections keeping the two kinds of mark separable, which is the property
`PL-LPLD` was scoped on.

Crossing detection arrived with `PL-CTD7` and is tested here too, in two
halves that stay apart. The predicates and the standings (each mark's status in
a run) are pure functions: two readings go in, and a result comes out. So they
are asserted directly, including the boundary cases that no live run
reproduces on demand. The halt itself is a property of the advance loop rather
than of a value. So it is asserted against a real `SimulationController`
stepped at 1× and at 300×. The claim that `PL-CTD7` exists to make is that
those two agree, and only running them can show it.
"""

import math

import pytest

from anesthesia_sim.app.bookmarks import (
    BookmarkCrossing,
    BookmarkSet,
    MacTarget,
    MarkStanding,
    TimeBookmark,
)
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.formatting import mac_multiple
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity
from anesthesia_sim.core.concentration import MacMultiple, Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.supported_ranges import MAXIMUM_ELAPSED_SIMULATION_TIME_S, CaseInstant

#: The step at which every run in this file is taken, matching the interface's own step.
STEP_S = SimulationStep(0.1)

#: The burst of steps that one tick advances at 300× real time. That is the
#: coarsest rate that `app/playback.py` offers, and the worst case that `PL-CTD7`
#: is about: 30 simulated seconds with nothing serviced between the steps.
STEPS_PER_TICK_AT_300X = 300


def _target(
    quantity: RecordedQuantity = RecordedQuantity.VESSEL_RICH,
    multiple: float = 0.8,
    label: str | None = None,
) -> MacTarget:
    """Build a MAC target with defaults, so that a test states only the field it is about."""

    return MacTarget(quantity, MacMultiple(multiple), label)


# ------------------------------------------------------------ time bookmarks


def test_a_time_bookmark_holds_its_instant_and_no_name_by_default() -> None:
    bookmark = TimeBookmark(CaseInstant(600.0))

    assert bookmark.instant_s == 600.0
    assert bookmark.label is None


def test_a_time_bookmark_keeps_the_name_it_was_given_without_surrounding_space() -> None:
    assert TimeBookmark(CaseInstant(600.0), "  intubation  ").label == "intubation"


@pytest.mark.parametrize(
    "instant_s", [-1.0, math.inf, -math.inf, math.nan, MAXIMUM_ELAPSED_SIMULATION_TIME_S + 1.0]
)
def test_an_instant_no_case_reaches_cannot_be_marked(instant_s: float) -> None:
    """No mark can be made before the case opens, at an instant no clock reaches, or past the span.

    `PL-CN5S`: the mark is built from a `CaseInstant`, which refuses each of
    these instants with a message that names the supported run length. So no set
    ever holds such a mark.
    """

    with pytest.raises(SimulationConfigurationError, match="outside the supported run length"):
        CaseInstant(instant_s)


@pytest.mark.parametrize("instant_s", [600.0, math.nan])
def test_a_time_bookmark_refuses_an_instant_not_built_as_a_case_instant(instant_s: float) -> None:
    """The instant is refused whatever its value, because nothing has checked it (`PL-CN5S`)."""

    with pytest.raises(TypeError, match="instant_s of .* was not built as CaseInstant"):
        TimeBookmark(instant_s)  # type: ignore[arg-type]


def test_the_case_opening_itself_is_a_markable_instant() -> None:
    assert TimeBookmark(CaseInstant(0.0)).instant_s == 0.0


def test_a_blank_name_is_refused_rather_than_read_as_no_name() -> None:
    # An empty row in a list is indistinguishable from a rendering failure,
    # and `None` already means "list it under its own value".
    with pytest.raises(SimulationConfigurationError, match="blank"):
        TimeBookmark(CaseInstant(600.0), "   ")


def test_no_mark_of_either_kind_carries_a_crossing_direction() -> None:
    # The minimum scope, taken from the reference simulator, included a crossing
    # direction. The project owner removed it on 2026-09-20. A height is a
    # height, and a run that passes through it going up, and again coming down,
    # has reached the marked height both times.
    assert not hasattr(TimeBookmark(CaseInstant(600.0)), "direction")
    assert not hasattr(_target(), "direction")


# --------------------------------------------------------------- MAC targets


def test_a_mac_target_names_the_compartment_it_is_read_against() -> None:
    target = _target(RecordedQuantity.MUSCLE)

    assert target.quantity is RecordedQuantity.MUSCLE
    assert target.mac_multiple == 0.8


@pytest.mark.parametrize("quantity", COMPARTMENT_QUANTITIES)
def test_every_drawn_compartment_may_carry_a_target(quantity: RecordedQuantity) -> None:
    # The minimum scope covers the six graphed compartments, not the alveolar
    # trace alone (`PL-LPLD`). So these six are everything a picker may offer.
    assert _target(quantity).quantity is quantity


def test_the_wash_in_ratio_may_not_carry_a_target() -> None:
    # The wash-in ratio is a quotient of two compartments rather than a
    # concentration. So a multiple of MAC of it is not a quantity that the model
    # represents. It is also the one member of `RecordedQuantity` that a
    # compartment picker could offer by mistake.
    with pytest.raises(SimulationConfigurationError, match="not one of"):
        _target(RecordedQuantity.WASH_IN_RATIO)


@pytest.mark.parametrize("multiple", [0.0, -0.5, math.inf, math.nan])
def test_a_target_at_a_height_no_compartment_can_cross_is_refused(multiple: float) -> None:
    # Zero is rejected along with the negatives. Every compartment starts at
    # zero, so every run would already be at such a target before it began.
    with pytest.raises(SimulationConfigurationError, match="height above zero"):
        _target(multiple=multiple)


def test_a_target_refusal_names_the_height_that_failed() -> None:
    # `.claude/rules/sources-and-docstrings.md` requires a refusal to name what
    # was refused, so that a rejected setting stays traceable to the input
    # behind it.
    with pytest.raises(SimulationConfigurationError, match=r"-0\.5"):
        _target(multiple=-0.5)


def test_two_targets_differing_only_in_label_name_one_crossing() -> None:
    assert _target(label="wash-in").crossing_key == _target(label="emergence").crossing_key


def test_a_different_height_on_one_compartment_is_a_different_crossing() -> None:
    assert _target(multiple=0.8).crossing_key != _target(multiple=0.5).crossing_key


# ------------------------------------------------------------- the two sets


def test_a_fresh_set_is_empty_in_both_collections() -> None:
    marks = BookmarkSet()

    assert marks.is_empty
    assert marks.time_bookmarks == ()
    assert marks.mac_targets == ()


def test_the_two_kinds_are_listed_apart_rather_than_filtered_out_of_one_list() -> None:
    marks = (
        BookmarkSet()
        .with_time_bookmark(TimeBookmark(CaseInstant(600.0)))
        .with_mac_target(_target())
    )

    assert marks.time_bookmarks == (TimeBookmark(CaseInstant(600.0)),)
    assert marks.mac_targets == (_target(),)
    assert not marks.is_empty


def test_adding_a_mark_leaves_the_set_it_was_added_to_alone() -> None:
    before = BookmarkSet()
    after = before.with_time_bookmark(TimeBookmark(CaseInstant(600.0)))

    assert before.time_bookmarks == ()
    assert after.time_bookmarks == (TimeBookmark(CaseInstant(600.0)),)


def test_marks_are_listed_in_the_order_they_were_added() -> None:
    marks = (
        BookmarkSet()
        .with_time_bookmark(TimeBookmark(CaseInstant(600.0)))
        .with_time_bookmark(TimeBookmark(CaseInstant(120.0)))
    )

    assert [bookmark.instant_s for bookmark in marks.time_bookmarks] == [600.0, 120.0]


def test_an_instant_already_marked_may_not_be_marked_again() -> None:
    marks = BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(600.0)))

    with pytest.raises(SimulationConfigurationError, match="marked once"):
        marks.with_time_bookmark(TimeBookmark(CaseInstant(600.0), "second thoughts"))


def test_the_repeated_instant_refusal_is_pinned_whole() -> None:
    """Pin the whole sentence that the bookmark dialog shows when an instant is marked twice.

    The test above matches only "marked once", which would pass even with the
    instant missing from the message (`PL-79PK`). The matching MAC-target message
    is not pinned. It names its crossing by the Python repr of an enum member,
    which is a defect of its own rather than a sentence to freeze.
    """

    marks = BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(600.0)))

    with pytest.raises(SimulationConfigurationError) as refusal:
        marks.with_time_bookmark(TimeBookmark(CaseInstant(600.0), "second thoughts"))

    assert str(refusal.value) == (
        "an instant is marked once: a second time bookmark naming 600.0 would be a row no "
        "run could stop at on its own account"
    )


def test_a_crossing_already_marked_may_not_be_marked_again() -> None:
    marks = BookmarkSet().with_mac_target(_target())

    with pytest.raises(SimulationConfigurationError, match="marked once"):
        marks.with_mac_target(_target(label="again"))


def test_two_heights_on_one_compartment_are_two_crossings() -> None:
    marks = BookmarkSet().with_mac_target(_target(multiple=0.8))
    both = marks.with_mac_target(_target(multiple=0.5))

    assert len(both.mac_targets) == 2


def test_the_same_height_on_another_compartment_is_a_different_crossing() -> None:
    marks = BookmarkSet().with_mac_target(_target(RecordedQuantity.VESSEL_RICH))
    both = marks.with_mac_target(_target(RecordedQuantity.FAT))

    assert len(both.mac_targets) == 2


def test_removing_a_time_bookmark_leaves_the_targets_alone() -> None:
    marks = (
        BookmarkSet()
        .with_time_bookmark(TimeBookmark(CaseInstant(600.0)))
        .with_mac_target(_target())
    )
    after = marks.without_time_bookmark(TimeBookmark(CaseInstant(600.0)))

    assert after.time_bookmarks == ()
    assert after.mac_targets == (_target(),)


def test_a_time_bookmark_is_removed_by_its_instant_rather_than_by_its_name() -> None:
    marks = BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(600.0), "intubation"))

    assert marks.without_time_bookmark(TimeBookmark(CaseInstant(600.0))).time_bookmarks == ()


def test_a_target_is_removed_by_its_crossing_rather_than_by_its_name() -> None:
    marks = BookmarkSet().with_mac_target(_target(label="wash-in"))

    assert marks.without_mac_target(_target()).mac_targets == ()


def test_removing_a_time_bookmark_that_is_not_there_is_refused() -> None:
    # Removing nothing silently would leave a panel reporting a deletion that
    # did not happen.
    with pytest.raises(SimulationConfigurationError, match="none to remove"):
        BookmarkSet().without_time_bookmark(TimeBookmark(CaseInstant(600.0)))


def test_removing_a_target_that_is_not_there_is_refused() -> None:
    with pytest.raises(SimulationConfigurationError, match="none to remove"):
        BookmarkSet().without_mac_target(_target())


def test_a_removal_refusal_names_the_crossing_it_could_not_find() -> None:
    with pytest.raises(SimulationConfigurationError, match="vessel_rich"):
        BookmarkSet().without_mac_target(_target())


def test_a_set_built_directly_from_repeated_marks_is_refused_too() -> None:
    # The collection enforces the invariant, not the method that adds a mark.
    # So a caller that constructs a set directly cannot get round it.
    with pytest.raises(SimulationConfigurationError, match="marked once"):
        BookmarkSet((TimeBookmark(CaseInstant(600.0)), TimeBookmark(CaseInstant(600.0))))


# ------------------------------------------------------- crossing predicates
#
# A crossing is a transition between two readings, not a comparison made at one
# reading (project owner, 2026-09-20). Everything below depends on that. At the
# boundary cases, a rule that compared a single reading would either stall a run
# forever on a height it settled at, or halt it again the moment it was resumed.


def _readings(**multiples: float) -> dict[RecordedQuantity, MacMultiple]:
    """Build the readings on one side of a step, for every compartment a target could use.

    Compartments that are not named read zero, which is where a case opens. So a
    test states only the compartment it is about.
    """

    readings = {quantity: MacMultiple(0.0) for quantity in COMPARTMENT_QUANTITIES}
    readings.update(
        {RecordedQuantity(name): MacMultiple(value) for name, value in multiples.items()}
    )

    return readings


def test_a_time_bookmark_is_crossed_by_the_step_that_reaches_it() -> None:
    bookmark = TimeBookmark(CaseInstant(30.0))

    assert bookmark.crossed_between(29.9, 30.0)
    assert bookmark.crossed_between(29.95, 30.05)


def test_a_time_bookmark_is_not_crossed_again_by_the_step_after_it() -> None:
    """Each step covers an interval open below and closed above, so an instant is reached once."""

    bookmark = TimeBookmark(CaseInstant(30.0))

    assert not bookmark.crossed_between(30.0, 30.1)
    assert not bookmark.crossed_between(29.8, 29.9)


# ----------------------------------------------- the step that reaches a mark
#
# `TimeBookmark.steps_to_reach` is the inverse of `crossed_between`. The count it
# returns is the step that the predicate names as the crossing step. So that
# count is where a halt stops and where `resumed_at_mark` forks (`PL-W4XQ`). The
# tests below check it against the predicate itself, at the grid products (step
# count times step size) that `SimulationState.elapsed_s` forms. They do not
# check it against a second formula for the same step.


def _reaching_step_is_the_crossing_one(instant_s: float, step: SimulationStep) -> bool:
    """Return whether `steps_to_reach` names the step that `crossed_between` says reaches it."""

    bookmark = TimeBookmark(CaseInstant(instant_s))
    count = bookmark.steps_to_reach(step)

    if count == 0:
        return instant_s == 0.0

    return bookmark.crossed_between(CaseInstant((count - 1) * step), CaseInstant(count * step))


def test_every_instant_a_learner_can_type_is_reached_on_the_step_the_halt_names() -> None:
    """Check all 36 001 one-decimal instants up to an hour, the dialog's own resolution.

    12 767 of them are not a whole number of 0.1 s steps in binary. For example,
    `453 x 0.1` is 45.300000000000004. So a fork instant built from the typed
    value would be refused, and one built by rounding would sometimes land a step
    early. Each instant is reached by exactly the step that `crossed_between`
    picks.
    """

    misses = [
        tenths / 10
        for tenths in range(36_001)
        if not _reaching_step_is_the_crossing_one(tenths / 10, STEP_S)
    ]

    assert misses == []


def test_every_grid_instant_is_reached_by_the_step_that_lands_on_it() -> None:
    """Check the grid products themselves, the instants where a halted run and its branches sit."""

    misses = [
        count
        for count in range(1, 36_001)
        if TimeBookmark(CaseInstant(count * STEP_S)).steps_to_reach(STEP_S) != count
    ]

    assert misses == []


def test_a_quotient_rounded_up_does_not_place_the_mark_a_step_late() -> None:
    """`0.30000000000000004 / 0.1` is 3.0000000000000004, whose ceiling is 4.

    The third step lands exactly on that instant, so the third step is the one
    that reaches it. Trusting the ceiling would fork one step after the halt.
    """

    instant_s = 3 * STEP_S

    assert math.ceil(instant_s / STEP_S) == 4, "the premise: the quotient rounds up"
    assert TimeBookmark(CaseInstant(instant_s)).steps_to_reach(STEP_S) == 3


def test_a_mark_inside_a_step_is_reached_at_the_step_s_end_and_not_rounded_back() -> None:
    """Rounding would put 45.35 s on the step ending at 45.3 s, before the mark.

    No halt stops there. At the interface's own 0.1 s step, the step that
    reaches the mark is the one ending at 45.4 s. At the finer 0.05 s step,
    45.35 s is a step's end, and the step that reaches the mark is the one
    ending at 45.35 s.
    """

    inside = TimeBookmark(CaseInstant(45.35))

    assert inside.steps_to_reach(STEP_S) == 454
    assert inside.steps_to_reach(SimulationStep(0.05)) == 907
    assert _reaching_step_is_the_crossing_one(45.35, SimulationStep(0.05))


@pytest.mark.parametrize("step_s", [0.001, 0.025, 0.05, 0.1])
def test_off_grid_instants_are_reached_on_the_crossing_step_at_every_step(step_s: float) -> None:
    """Check instants between grid points, at steps across the supported range."""

    step = SimulationStep(step_s)
    instants = [round(k * 0.137, 6) for k in range(1, 2001)]

    assert [s for s in instants if not _reaching_step_is_the_crossing_one(s, step)] == []


def test_a_mark_at_the_case_s_opening_is_reached_by_no_step() -> None:
    """A run is already at that instant before it steps, and `crossed_between` never fires there."""

    assert TimeBookmark(CaseInstant(0.0)).steps_to_reach(STEP_S) == 0


def test_the_last_supported_instant_is_reached_on_the_last_supported_step() -> None:
    """At the far boundary, the count stays inside the supported span and does not run past it."""

    last = TimeBookmark(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S))
    count = last.steps_to_reach(STEP_S)

    assert count * STEP_S == MAXIMUM_ELAPSED_SIMULATION_TIME_S
    assert _reaching_step_is_the_crossing_one(MAXIMUM_ELAPSED_SIMULATION_TIME_S, STEP_S)


def test_steps_to_reach_refuses_a_step_not_built_as_one() -> None:
    """A bare float has passed no range check, and a zero step would divide by zero."""

    with pytest.raises(TypeError):
        TimeBookmark(CaseInstant(30.0)).steps_to_reach(0.1)  # type: ignore[arg-type]


def test_a_held_bookmark_is_found_by_its_instant_and_returned_as_the_set_holds_it() -> None:
    """The lookup returns the bookmark as the set stores it, with its label.

    The standings are keyed by the stored bookmark, label included, so that is the
    bookmark a caller needs in order to look up its standing.
    """

    marks = BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(600.0), "intubation"))

    assert marks.held_time_bookmark(TimeBookmark(CaseInstant(600.0))) == TimeBookmark(
        CaseInstant(600.0), "intubation"
    )


def test_a_bookmark_the_set_does_not_hold_is_refused_by_its_instant() -> None:
    with pytest.raises(SimulationConfigurationError, match="no time bookmark stands at 600.0 s"):
        BookmarkSet().held_time_bookmark(TimeBookmark(CaseInstant(600.0)))


def test_a_target_is_crossed_by_the_step_that_reaches_its_height() -> None:
    target = _target(multiple=0.8)

    assert target.crossed_between(MacMultiple(0.79), MacMultiple(0.81))
    assert target.crossed_between(MacMultiple(0.79), MacMultiple(0.80))


def test_a_target_is_crossed_going_down_as_well_as_going_up() -> None:
    """A target carries no direction, so a wash-out crosses it as a wash-in does."""

    target = _target(multiple=0.8)

    assert target.crossed_between(MacMultiple(0.81), MacMultiple(0.79))
    assert target.crossed_between(MacMultiple(0.81), MacMultiple(0.80))


def test_a_target_a_run_settles_exactly_on_is_crossed_once_and_not_again() -> None:
    """This is the case in which a rule comparing one reading would never let a run past.

    If the rule were "the reading is at or above the height", every later step of
    a run sitting exactly on the height would report a crossing, and the run
    could not be advanced at all.
    """

    target = _target(multiple=0.8)

    assert target.crossed_between(MacMultiple(0.79), MacMultiple(0.80))
    assert not target.crossed_between(MacMultiple(0.80), MacMultiple(0.80))


def test_a_target_is_not_crossed_by_leaving_its_height_in_either_direction() -> None:
    """Leaving the height is not a crossing, so a halted run resumes without halting there again."""

    target = _target(multiple=0.8)

    assert not target.crossed_between(MacMultiple(0.80), MacMultiple(0.81))
    assert not target.crossed_between(MacMultiple(0.80), MacMultiple(0.79))


def test_a_step_that_crossed_nothing_is_reported_as_no_crossing() -> None:
    marks = (
        BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(30.0))).with_mac_target(_target())
    )

    assert (
        marks.crossings_between(
            before_s=CaseInstant(10.0),
            after_s=CaseInstant(10.1),
            before=_readings(vessel_rich=0.1),
            after=_readings(vessel_rich=0.2),
        )
        is None
    )


def test_one_step_can_cross_a_marked_instant_and_a_marked_height_at_once() -> None:
    target = _target(multiple=0.8)
    marks = (
        BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(30.0))).with_mac_target(target)
    )

    crossing = marks.crossings_between(
        before_s=CaseInstant(29.9),
        after_s=CaseInstant(30.0),
        before=_readings(vessel_rich=0.79),
        after=_readings(vessel_rich=0.81),
    )

    assert crossing == BookmarkCrossing(
        CaseInstant(30.0), (TimeBookmark(CaseInstant(30.0)),), (target,)
    )


def test_a_reading_missing_a_marked_compartment_is_refused() -> None:
    marks = BookmarkSet().with_mac_target(_target(RecordedQuantity.FAT))
    short = {RecordedQuantity.VESSEL_RICH: MacMultiple(0.1)}

    with pytest.raises(SimulationConfigurationError, match="no fat compartment"):
        marks.crossings_between(
            before_s=CaseInstant(0.0), after_s=CaseInstant(0.1), before=short, after=short
        )


def test_a_crossing_naming_no_mark_at_all_is_refused() -> None:
    with pytest.raises(SimulationConfigurationError, match="at least one mark"):
        BookmarkCrossing(CaseInstant(30.0))


def test_a_crossing_refuses_an_instant_not_built_as_a_case_instant() -> None:
    """A run stores the crossing it halted on, so the crossing checks its instant (`PL-CN5S`)."""

    with pytest.raises(TypeError, match="instant_s of 30.0 was not built as CaseInstant"):
        BookmarkCrossing(30.0, (TimeBookmark(CaseInstant(30.0)),))  # type: ignore[arg-type]


# ------------------------------------------------------------------ standings


def _standings(
    marks: BookmarkSet,
    *,
    reached_instants_s: frozenset[float] = frozenset(),
    reached_crossings: frozenset[tuple[RecordedQuantity, float]] = frozenset(),
    opened_at_s: float = 0.0,
    elapsed_s: float | None = None,
    stopped_at_cap: bool = False,
    run_failed: bool = False,
) -> object:
    """Compute this set's standings with defaults, so that a test states only the fact it is about.

    `elapsed_s` defaults to the run's own opening, which describes a run that has
    not stepped. Every marked instant is still ahead of such a run. So a test
    about something other than the clock does not get its result quietly from the
    clock. The instants are built as `CaseInstant`s here, as a run's own clock
    builds them, so that a test can state them as plain numbers.
    """

    return marks.standings(
        reached_instants_s=frozenset(CaseInstant(instant_s) for instant_s in reached_instants_s),
        reached_crossings=reached_crossings,
        opened_at_s=CaseInstant(opened_at_s),
        elapsed_s=CaseInstant(opened_at_s if elapsed_s is None else elapsed_s),
        stopped_at_cap=stopped_at_cap,
        run_failed=run_failed,
    )


def test_a_mark_the_run_can_still_reach_stands_as_still_running() -> None:
    bookmark = TimeBookmark(CaseInstant(600.0))
    target = _target()
    marks = BookmarkSet().with_time_bookmark(bookmark).with_mac_target(target)

    standings = _standings(marks)

    assert standings.of_time_bookmark(bookmark) is MarkStanding.STILL_RUNNING
    assert standings.of_mac_target(target) is MarkStanding.STILL_RUNNING


def test_a_height_the_run_halted_on_stands_as_reached() -> None:
    """`REACHED` is a target's own standing, and only a target can have it.

    A height is not ordered by a clock. A compartment arrives at it, leaves it,
    and may arrive again. So the only thing that can be said of a height is what
    the run *did*, and that is what `REACHED` says.
    """

    target = _target()
    marks = BookmarkSet().with_mac_target(target)

    standings = _standings(marks, reached_crossings=frozenset({target.crossing_key}))

    assert standings.of_mac_target(target) is MarkStanding.REACHED


def test_an_instant_the_run_halted_on_stands_as_passed_rather_than_reached() -> None:
    """The two kinds of mark use different standings, and this is where they could be confused.

    The run halted on this instant, which is the historical claim that `REACHED`
    makes. But the standing is still the positional one. A clock taken backwards
    would revoke the history, while the mark stayed perfectly reachable
    (`PL-3K9B`).
    """

    bookmark = TimeBookmark(CaseInstant(600.0))
    marks = BookmarkSet().with_time_bookmark(bookmark)

    standings = _standings(marks, reached_instants_s=frozenset({600.0}))

    assert standings.of_time_bookmark(bookmark) is MarkStanding.PASSED
    assert standings.of_time_bookmark(bookmark) is not MarkStanding.REACHED


def test_a_relabelled_mark_keeps_what_the_run_did_with_it() -> None:
    """The mark is matched the way `without_mac_target` matches, so a rename is not a new mark."""

    renamed = _target(label="second gas on")
    marks = BookmarkSet().with_mac_target(renamed)

    standings = _standings(marks, reached_crossings=frozenset({_target().crossing_key}))

    assert standings.of_mac_target(renamed) is MarkStanding.REACHED


def test_a_target_still_outstanding_at_the_supported_run_length_says_it_was_not_reached() -> None:
    """A threshold above a compartment's asymptote, which is never reached.

    The run stops at the limit in `docs/MODEL.md` § "Supported run length", and
    by then it has answered the question. So the row must not go on saying that
    the run is still working on it.
    """

    above_the_asymptote = _target(multiple=0.95)
    marks = BookmarkSet().with_mac_target(above_the_asymptote)

    standings = _standings(marks, stopped_at_cap=True)

    assert standings.of_mac_target(above_the_asymptote) is MarkStanding.NOT_REACHED_WITHIN_CAP


def test_a_bookmark_before_a_branch_fork_reads_apart_from_the_cap_case() -> None:
    """The fourth outcome, and the reason there are four rather than three.

    A branch inherits its trunk's marks. So a bookmark before the fork is carried
    over, and the branch can never reach it going forward. Reporting it as "not
    reached within the cap" would say that running longer might reach it, which
    is false.
    """

    inherited = TimeBookmark(CaseInstant(120.0))
    marks = BookmarkSet().with_time_bookmark(inherited)

    standings = _standings(marks, opened_at_s=300.0)

    assert standings.of_time_bookmark(inherited) is MarkStanding.BEFORE_THIS_BRANCH
    assert standings.of_time_bookmark(inherited) is not MarkStanding.NOT_REACHED_WITHIN_CAP


def test_a_mark_outstanding_on_a_failed_run_is_not_reported_as_still_reachable() -> None:
    """The sixth outcome (`PL-N3N5`), for the state that the other five cannot express.

    `SimulationController.start` refuses a failed session with "cannot resume a
    failed simulation ... reset it first", because its next step would raise as
    its last one did. `STILL_RUNNING` says that the run *can still reach* the
    mark and has not reached it yet. The first half of that is false for every
    mark that such a run has not reached.

    Both kinds of mark are asserted, because the failure ends a clock and a
    height alike. That is why the outcome is a standing for both kinds rather
    than for the bookmark alone.
    """

    bookmark = TimeBookmark(CaseInstant(600.0))
    target = _target()
    marks = BookmarkSet().with_time_bookmark(bookmark).with_mac_target(target)

    standings = _standings(marks, run_failed=True)

    assert standings.of_time_bookmark(bookmark) is MarkStanding.NOT_REACHED_BEFORE_FAILURE
    assert standings.of_mac_target(target) is MarkStanding.NOT_REACHED_BEFORE_FAILURE


def test_a_failed_run_reads_apart_from_one_that_ran_out_of_supported_time() -> None:
    """The two refusals stop a run for opposite reasons, so they are two different standings.

    At the cap, the model has answered the question, and a longer run would not
    change the answer. In a failure, the model could not answer at all. Reporting
    a failure as the cap would tell a learner that the mark lies beyond what the
    model supports. That is a claim about the model rather than about this run. A
    fresh run, started by the reset that the failure demands, would show the
    claim to be false.
    """

    bookmark = TimeBookmark(CaseInstant(600.0))
    marks = BookmarkSet().with_time_bookmark(bookmark)

    failed = _standings(marks, run_failed=True)

    assert failed.of_time_bookmark(bookmark) is MarkStanding.NOT_REACHED_BEFORE_FAILURE
    assert failed.of_time_bookmark(bookmark) is not MarkStanding.NOT_REACHED_WITHIN_CAP
    assert _standings(marks, stopped_at_cap=True).of_time_bookmark(bookmark) is (
        MarkStanding.NOT_REACHED_WITHIN_CAP
    )


def test_the_cap_answers_for_a_run_standing_at_it_that_then_failed() -> None:
    """A run that carries both refusals reports the cap, and this is why.

    `SimulationController.advance` takes no step on a stopped run. So a run that
    stands at the cap and has failed was failed by a setting *after* it ran out
    of supported time. The cap is the limit within which the mark went unreached,
    and the failure came after the question had been answered. The cap is also
    the more durable of the two, because it is the one that the reset would not
    clear.
    """

    bookmark = TimeBookmark(CaseInstant(600.0))
    target = _target()
    marks = BookmarkSet().with_time_bookmark(bookmark).with_mac_target(target)

    standings = _standings(marks, stopped_at_cap=True, run_failed=True)

    assert standings.of_time_bookmark(bookmark) is MarkStanding.NOT_REACHED_WITHIN_CAP
    assert standings.of_mac_target(target) is MarkStanding.NOT_REACHED_WITHIN_CAP


def test_a_failure_stops_a_clock_without_taking_it_back() -> None:
    """A failure does not revoke the two standings that describe what has already happened.

    A marked instant at or behind the clock was passed, and a height the run
    halted on was reached, whatever stopped the run afterwards. Reporting either
    as unreached would withdraw a true claim about the case. That would be the
    mirror image of the defect that this outcome was added for.
    """

    passed = TimeBookmark(CaseInstant(30.0))
    reached = _target()
    marks = BookmarkSet().with_time_bookmark(passed).with_mac_target(reached)

    standings = _standings(
        marks, elapsed_s=60.0, reached_crossings=frozenset({reached.crossing_key}), run_failed=True
    )

    assert standings.of_time_bookmark(passed) is MarkStanding.PASSED
    assert standings.of_mac_target(reached) is MarkStanding.REACHED


def test_an_inherited_bookmark_on_a_failed_branch_still_reads_before_the_branch() -> None:
    """The statically decidable standing takes precedence over the failure, as it does over the cap.

    This branch could not have reached an instant before the fork even if it had
    run perfectly. So naming the failure would suggest that the failure is the
    reason. A reset also returns a branch to its fork rather than to the case's
    opening, so the next run of the branch cannot reach the instant either.
    """

    inherited = TimeBookmark(CaseInstant(120.0))
    marks = BookmarkSet().with_time_bookmark(inherited)

    standings = _standings(marks, opened_at_s=300.0, run_failed=True)

    assert standings.of_time_bookmark(inherited) is MarkStanding.BEFORE_THIS_BRANCH


def test_a_mark_the_run_has_passed_does_not_read_as_still_reachable() -> None:
    """Test the defect that `PL-3K9B` names, at the comparison that caused it.

    `STILL_RUNNING` says that the run can still reach the mark. A clock only
    increases, so an instant at or behind it can never be reached again, whatever
    put the clock there. Both halves are asserted, because the failure was a row
    that showed the wrong one of the two standings, not a row that showed
    nothing.
    """

    at_the_fork = TimeBookmark(CaseInstant(300.0))
    behind_the_clock = TimeBookmark(CaseInstant(120.0))
    marks = BookmarkSet().with_time_bookmark(at_the_fork).with_time_bookmark(behind_the_clock)

    standings = _standings(marks, elapsed_s=300.0)

    assert standings.of_time_bookmark(at_the_fork) is MarkStanding.PASSED
    assert standings.of_time_bookmark(at_the_fork) is not MarkStanding.STILL_RUNNING
    assert standings.of_time_bookmark(behind_the_clock) is MarkStanding.PASSED
    assert standings.of_time_bookmark(behind_the_clock) is not MarkStanding.STILL_RUNNING


def test_a_bookmark_at_a_branch_s_own_fork_instant_reads_passed() -> None:
    """Case A: the branch opens exactly at the mark, so no step it takes can cross the mark.

    `TimeBookmark.crossed_between` needs `before_s < instant_s`, and the branch's
    first `before_s` is the fork itself. So the halt set can never acquire this
    instant, however long the branch runs. The clock comparison is what decides
    this standing.
    """

    at_the_fork = TimeBookmark(CaseInstant(300.0))
    marks = BookmarkSet().with_time_bookmark(at_the_fork)

    standings = _standings(marks, opened_at_s=300.0, elapsed_s=300.0)

    assert standings.of_time_bookmark(at_the_fork) is MarkStanding.PASSED


def test_a_seeded_halt_answers_a_fork_that_opened_just_past_its_own_mark() -> None:
    """Case B: the one case that the clock comparison cannot detect.

    A halt lands on the step that *crossed* the mark. So an instant that is not a
    multiple of the step in binary is crossed by a step that lands a few parts in
    1e16 past it: 45.3 marked, 45.300000000000004 forked at. The branch then
    opens after its own mark, and `opened_at_s <= instant_s` is false. Only the
    crossing seeded from the fork records that the two are one crossing. Without
    that seeded crossing, the row would read `before this branch opened`, while
    the identical act one step-grid over would read `passed`. Both rows render
    their instant as `45.3s`.
    """

    marked = 45.3
    forked_at = 45.300000000000004
    assert forked_at > marked

    off_grid = TimeBookmark(CaseInstant(marked))
    marks = BookmarkSet().with_time_bookmark(off_grid)

    seeded = _standings(
        marks, reached_instants_s=frozenset({marked}), opened_at_s=forked_at, elapsed_s=forked_at
    )
    unseeded = _standings(marks, opened_at_s=forked_at, elapsed_s=forked_at)

    assert seeded.of_time_bookmark(off_grid) is MarkStanding.PASSED
    assert unseeded.of_time_bookmark(off_grid) is MarkStanding.BEFORE_THIS_BRANCH


def test_a_bookmark_at_the_case_s_opening_reads_passed_on_an_ordinary_trunk() -> None:
    """The same arithmetic with no branch in it at all.

    `crossed_between` needs `before_s < 0.0`, and no run's clock is negative. So
    a mark at induction could never enter the halt set either. It is a strange
    thing to mark, but not an impossible one.
    """

    induction = TimeBookmark(CaseInstant(0.0))
    marks = BookmarkSet().with_time_bookmark(induction)

    assert _standings(marks, elapsed_s=60.0).of_time_bookmark(induction) is MarkStanding.PASSED


def test_a_clock_standing_before_its_own_run_s_opening_is_refused() -> None:
    """The standings are refused rather than placing every row against a run that does not exist.

    The opening and the clock are one run's own numbers. If they are crossed
    over, they must come from two different runs. Clamping would give a
    plausible result, and the safety-critical standard prefers an obvious
    failure to that outcome.
    """

    marks = BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(120.0)))

    with pytest.raises(SimulationConfigurationError, match="at or after its own beginning"):
        _standings(marks, opened_at_s=300.0, elapsed_s=299.9)


def test_a_bookmark_at_the_end_of_the_run_length_waits_for_the_run_to_get_there() -> None:
    """The far end is markable and reachable, so nothing about it is decided early.

    A mark past the span was once given `NOT_REACHED_WITHIN_CAP` immediately, so
    that a learner was not left waiting out a simulated day for it. Since
    `PL-CN5S`, no such mark can be made, because the `CaseInstant` it would be
    built from is refused. So the mark left at the edge is the span's own end,
    which a run reaches and crosses like any other mark.
    """

    at_the_end = TimeBookmark(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S))
    marks = BookmarkSet().with_time_bookmark(at_the_end)
    at_the_cap = _standings(marks, stopped_at_cap=True, elapsed_s=MAXIMUM_ELAPSED_SIMULATION_TIME_S)

    assert _standings(marks).of_time_bookmark(at_the_end) is MarkStanding.STILL_RUNNING
    assert at_the_cap.of_time_bookmark(at_the_end) is MarkStanding.PASSED


def test_a_standing_asked_for_a_mark_that_was_never_evaluated_is_refused() -> None:
    """The request is refused, because a default would draw a row for a mark nobody evaluated."""

    standings = _standings(BookmarkSet())

    with pytest.raises(SimulationConfigurationError, match="does not hold the MAC target"):
        standings.of_mac_target(_target())

    with pytest.raises(SimulationConfigurationError, match="does not hold the time bookmark"):
        standings.of_time_bookmark(TimeBookmark(CaseInstant(30.0)))


# ---------------------------------------------------- halting on a crossing
#
# This is the half that has to be run rather than asserted directly. `PL-CTD7`
# claims that the halt lands on the step that crossed, whatever the playback
# multiplier. So these tests drive a real `SimulationController` the way
# `run_view.step_tick` drives one: a burst of steps with nothing serviced
# between them.


def _step_until_halt(run: SimulationController, *, limit: int = 20_000) -> BookmarkCrossing | None:
    """Advance one step at a time until the run halts, or `limit` steps pass.

    Returns:
        The crossing that the run halted on, or `None` if it never halted. It
        returns `None` rather than raising, so that a test can assert that a run
        was *not* stopped.
    """

    for _ in range(limit):
        run.advance(STEP_S)

        if not run.is_running:
            return run.snapshot().bookmark_halt

    return None


def _tick_until_halt(
    run: SimulationController, *, steps_per_tick: int, limit: int = 20_000
) -> BookmarkCrossing | None:
    """Advance in whole bursts, the way a tick at `multiplier ×` does, until the run halts.

    Nothing is read between the steps of a burst. That is exactly the condition
    that made per-frame detection overshoot: the run is asked whether it is still
    running only after the burst has finished.
    """

    for _ in range(0, limit, steps_per_tick):
        for _ in range(steps_per_tick):
            run.advance(STEP_S)

        if not run.is_running:
            return run.snapshot().bookmark_halt

    return None


def _alveolar_mac_multiple(run: SimulationController) -> MacMultiple:
    """Return what the alveolar readout beside the target would show, in the target's unit."""

    snapshot = run.snapshot()

    return mac_multiple(snapshot.alveolar_partial_pressure_fraction, snapshot.agent_mac_percent)


def test_a_target_halts_on_every_crossing_in_either_direction() -> None:
    """Rising through 0.5 ×MAC and falling back through it stops the run twice.

    This follows the decision of 2026-09-20: a target carries no crossing
    direction. So a case that passes through a marked height on the way up, and
    again on the way down, has reached what the learner marked both times.
    Halting only once would make `MacTarget`'s own docstring false for the second
    crossing.
    """

    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.5))
    run = SimulationController()
    run.add_mac_target(target)

    run.start()
    rising = _step_until_halt(run)

    assert rising is not None
    assert rising.mac_targets == (target,)

    # Turn the vaporizer off, so that the same height is crossed again coming down.
    run.set_delivered_concentration_percent(Percent(0.0))
    run.start()
    falling = _step_until_halt(run)

    assert falling is not None
    assert falling.mac_targets == (target,)
    assert falling.instant_s > rising.instant_s


def test_a_halt_lands_on_the_same_step_at_1x_and_at_300x() -> None:
    """The whole claim of `PL-CTD7`: the playback rate does not move the halt.

    A crossing tested once per rendered frame would land up to
    `multiplier × 0.1` s late, which is 30 simulated seconds at 300×. The two
    runs below would then stop at different concentrations from one another,
    while both claimed to have stopped at 0.5 ×MAC.
    """

    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.5))

    real_time = SimulationController()
    real_time.add_mac_target(target)
    real_time.start()
    at_1x = _step_until_halt(real_time)

    fast = SimulationController()
    fast.add_mac_target(target)
    fast.start()
    at_300x = _tick_until_halt(fast, steps_per_tick=STEPS_PER_TICK_AT_300X)

    assert at_1x is not None
    assert at_1x == at_300x
    assert _alveolar_mac_multiple(real_time) == _alveolar_mac_multiple(fast)


def test_a_halt_leaves_the_run_paused_on_the_crossing_step() -> None:
    """A halt pauses the run, so a control change made then acts where the learner was looking.

    A setting changed while the run plays first takes effect at a tick boundary
    (`PL-NBWP`). At 300× that is up to 30 simulated seconds after the value on
    screen. No step is taken while the run is paused. So a halt that pauses makes
    the pause, change and resume route automatic, rather than something the
    learner has to know.
    """

    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.5))
    run = SimulationController()
    run.add_mac_target(target)
    run.start()

    halt = _tick_until_halt(run, steps_per_tick=STEPS_PER_TICK_AT_300X)
    snapshot = run.snapshot()

    assert halt is not None
    assert not snapshot.is_running
    assert snapshot.elapsed_s == halt.instant_s
    # The halt is neither a failure nor the end of the supported domain. It is an ordinary pause.
    assert snapshot.failure_reason is None
    assert snapshot.supported_limit_reason is None
    assert snapshot.bookmark_standings.of_mac_target(target) is MarkStanding.REACHED


def test_a_run_that_settles_exactly_on_a_target_halts_once_and_then_advances() -> None:
    """The boundary case, with the height taken from the run itself so the run lands on it exactly.

    A rule closed on both sides would report a crossing on every step from
    here on, and the run could never be advanced past the target at all.
    """

    measuring = SimulationController()
    measuring.start()

    for _ in range(600):
        measuring.advance(STEP_S)

    height = _alveolar_mac_multiple(measuring)

    run = SimulationController()
    run.add_mac_target(MacTarget(RecordedQuantity.ALVEOLAR, height))
    run.start()
    halt = _step_until_halt(run)

    assert halt is not None
    assert halt.instant_s == pytest.approx(60.0)
    assert _alveolar_mac_multiple(run) == height

    run.start()
    assert _step_until_halt(run, limit=600) is None
    assert run.is_running


def test_a_time_bookmark_halts_the_run_on_the_step_that_reaches_it() -> None:
    run = SimulationController()
    run.add_time_bookmark(TimeBookmark(CaseInstant(30.0)))
    run.start()

    halt = _tick_until_halt(run, steps_per_tick=STEPS_PER_TICK_AT_300X)

    assert halt == BookmarkCrossing(CaseInstant(30.0), (TimeBookmark(CaseInstant(30.0)),))
    assert run.snapshot().elapsed_s == pytest.approx(30.0)


def test_an_unmarked_run_takes_the_same_trajectory_as_one_that_halted() -> None:
    """Detection observes the run and does not change it.

    The marked run is stepped to the same instant through a halt and a resume,
    and it has to end where the unmarked run ends. `CLAUDE.md` requires
    deterministic results for identical inputs, and a halt is not an input.
    """

    marked = SimulationController()
    marked.add_time_bookmark(TimeBookmark(CaseInstant(30.0)))
    marked.start()

    for _ in range(600):
        marked.advance(STEP_S)

        if not marked.is_running:
            marked.start()

    unmarked = SimulationController()
    unmarked.start()

    for _ in range(600):
        unmarked.advance(STEP_S)

    assert marked.snapshot().elapsed_s == unmarked.snapshot().elapsed_s
    assert _alveolar_mac_multiple(marked) == _alveolar_mac_multiple(unmarked)


def test_resetting_forgets_what_the_run_did_with_the_marks_and_keeps_the_marks() -> None:
    bookmark = TimeBookmark(CaseInstant(30.0))
    run = SimulationController()
    run.add_time_bookmark(bookmark)
    run.start()
    _step_until_halt(run)

    run.reset()
    snapshot = run.snapshot()

    assert snapshot.bookmarks.time_bookmarks == (bookmark,)
    assert snapshot.bookmark_halt is None
    assert snapshot.bookmark_standings.of_time_bookmark(bookmark) is MarkStanding.STILL_RUNNING


def test_unmarking_the_instant_a_run_is_halted_on_clears_the_halt() -> None:
    """A halt naming a row nobody can see is stale state rather than a record."""

    bookmark = TimeBookmark(CaseInstant(30.0))
    run = SimulationController()
    run.add_time_bookmark(bookmark)
    run.start()

    assert _step_until_halt(run) is not None

    run.remove_time_bookmark(bookmark)

    assert run.snapshot().bookmark_halt is None
