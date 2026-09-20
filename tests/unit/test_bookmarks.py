"""What a mark refuses, and what the two collections hold apart.

`app/bookmarks.py` decides nothing about a run: it decides what a learner is
allowed to have *asked*. So the claims here are all about the boundary — which
values are refused and with what message — and about the collections keeping
the two kinds separable, which is the property `PL-LPLD` was scoped on.

Detection arrived with `PL-CTD7` and is tested here too, in two halves that
stay apart. The predicates and the standings are pure — two readings in, an
answer out — so they are asserted directly, including the boundary cases no
live run reproduces on demand. The halt itself is a property of the advance
loop rather than of a value, so it is asserted against a real
`SimulationController` stepped at 1× and at 300×: the claim `PL-CTD7` exists
to make is that those two agree, and nothing short of running them can say so.
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
from anesthesia_sim.core.concentration import Fraction, MacMultiple
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.supported_ranges import MAXIMUM_ELAPSED_SIMULATION_TIME_S

#: The step every run in this file is taken at, matching the interface's own.
STEP_S = 0.1

#: A burst of steps one tick advances at 300× real time, which is the coarsest
#: rung `app/playback.py` offers and the worst case `PL-CTD7` is about: 30
#: simulated seconds with nothing serviced between the steps.
STEPS_PER_TICK_AT_300X = 300


def _target(
    quantity: RecordedQuantity = RecordedQuantity.VESSEL_RICH,
    multiple: float = 0.8,
    label: str | None = None,
) -> MacTarget:
    """A MAC target, so a test states only the field it is about."""

    return MacTarget(quantity, MacMultiple(multiple), label)


# ------------------------------------------------------------ time bookmarks


def test_a_time_bookmark_holds_its_instant_and_no_name_by_default() -> None:
    bookmark = TimeBookmark(600.0)

    assert bookmark.instant_s == 600.0
    assert bookmark.label is None


def test_a_time_bookmark_keeps_the_name_it_was_given_without_surrounding_space() -> None:
    assert TimeBookmark(600.0, "  intubation  ").label == "intubation"


def test_a_time_bookmark_before_the_case_opened_is_refused() -> None:
    with pytest.raises(SimulationConfigurationError, match="opening at 0 s"):
        TimeBookmark(-1.0)


@pytest.mark.parametrize("instant_s", [math.inf, -math.inf, math.nan])
def test_a_time_bookmark_at_an_instant_no_clock_reaches_is_refused(instant_s: float) -> None:
    with pytest.raises(SimulationConfigurationError, match="finite instant"):
        TimeBookmark(instant_s)


def test_the_case_opening_itself_is_a_markable_instant() -> None:
    assert TimeBookmark(0.0).instant_s == 0.0


def test_a_blank_name_is_refused_rather_than_read_as_no_name() -> None:
    # An empty row in a list is indistinguishable from a rendering failure,
    # and `None` already means "list it under its own value".
    with pytest.raises(SimulationConfigurationError, match="blank"):
        TimeBookmark(600.0, "   ")


def test_no_mark_of_either_kind_carries_a_crossing_direction() -> None:
    # The scope floor took one from the reference simulator and the project
    # owner removed it on 2026-09-20: a height is a height, and a run that
    # passes through it going up and again coming down has reached what was
    # marked both times.
    assert not hasattr(TimeBookmark(600.0), "direction")
    assert not hasattr(_target(), "direction")


# --------------------------------------------------------------- MAC targets


def test_a_mac_target_names_the_compartment_it_is_read_against() -> None:
    target = _target(RecordedQuantity.MUSCLE)

    assert target.quantity is RecordedQuantity.MUSCLE
    assert target.mac_multiple == 0.8


@pytest.mark.parametrize("quantity", COMPARTMENT_QUANTITIES)
def test_every_drawn_compartment_may_carry_a_target(quantity: RecordedQuantity) -> None:
    # The scope floor is the six graphed compartments rather than the alveolar
    # trace alone (`PL-LPLD`), so this is the whole of what a picker may offer.
    assert _target(quantity).quantity is quantity


def test_the_wash_in_ratio_may_not_carry_a_target() -> None:
    # It is a quotient of two compartments rather than a concentration, so a
    # multiple of MAC of it is not a quantity the model holds - and it is the
    # one member of `RecordedQuantity` a compartment picker could offer by
    # mistake.
    with pytest.raises(SimulationConfigurationError, match="not one of"):
        _target(RecordedQuantity.WASH_IN_RATIO)


@pytest.mark.parametrize("multiple", [0.0, -0.5, math.inf, math.nan])
def test_a_target_at_a_height_no_compartment_can_cross_is_refused(multiple: float) -> None:
    # Zero goes with the negatives: a compartment opens at zero, so every run
    # would stand on such a target before it began.
    with pytest.raises(SimulationConfigurationError, match="height above zero"):
        _target(multiple=multiple)


def test_a_target_refusal_names_the_height_that_failed() -> None:
    # `.claude/rules/sources-and-docstrings.md`: a refusal names what was
    # refused, so a rejected setting stays traceable to the input behind it.
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
    marks = BookmarkSet().with_time_bookmark(TimeBookmark(600.0)).with_mac_target(_target())

    assert marks.time_bookmarks == (TimeBookmark(600.0),)
    assert marks.mac_targets == (_target(),)
    assert not marks.is_empty


def test_adding_a_mark_leaves_the_set_it_was_added_to_alone() -> None:
    before = BookmarkSet()
    after = before.with_time_bookmark(TimeBookmark(600.0))

    assert before.time_bookmarks == ()
    assert after.time_bookmarks == (TimeBookmark(600.0),)


def test_marks_are_listed_in_the_order_they_were_added() -> None:
    marks = (
        BookmarkSet()
        .with_time_bookmark(TimeBookmark(600.0))
        .with_time_bookmark(TimeBookmark(120.0))
    )

    assert [bookmark.instant_s for bookmark in marks.time_bookmarks] == [600.0, 120.0]


def test_an_instant_already_marked_may_not_be_marked_again() -> None:
    marks = BookmarkSet().with_time_bookmark(TimeBookmark(600.0))

    with pytest.raises(SimulationConfigurationError, match="marked once"):
        marks.with_time_bookmark(TimeBookmark(600.0, "second thoughts"))


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
    marks = BookmarkSet().with_time_bookmark(TimeBookmark(600.0)).with_mac_target(_target())
    after = marks.without_time_bookmark(TimeBookmark(600.0))

    assert after.time_bookmarks == ()
    assert after.mac_targets == (_target(),)


def test_a_time_bookmark_is_removed_by_its_instant_rather_than_by_its_name() -> None:
    marks = BookmarkSet().with_time_bookmark(TimeBookmark(600.0, "intubation"))

    assert marks.without_time_bookmark(TimeBookmark(600.0)).time_bookmarks == ()


def test_a_target_is_removed_by_its_crossing_rather_than_by_its_name() -> None:
    marks = BookmarkSet().with_mac_target(_target(label="wash-in"))

    assert marks.without_mac_target(_target()).mac_targets == ()


def test_removing_a_time_bookmark_that_is_not_there_is_refused() -> None:
    # Removing nothing silently would leave a panel reporting a deletion that
    # did not happen.
    with pytest.raises(SimulationConfigurationError, match="none to remove"):
        BookmarkSet().without_time_bookmark(TimeBookmark(600.0))


def test_removing_a_target_that_is_not_there_is_refused() -> None:
    with pytest.raises(SimulationConfigurationError, match="none to remove"):
        BookmarkSet().without_mac_target(_target())


def test_a_removal_refusal_names_the_crossing_it_could_not_find() -> None:
    with pytest.raises(SimulationConfigurationError, match="vessel_rich"):
        BookmarkSet().without_mac_target(_target())


def test_a_set_built_directly_from_repeated_marks_is_refused_too() -> None:
    # The invariant is the collection's rather than the adder's, so a caller
    # constructing one cannot get round it.
    with pytest.raises(SimulationConfigurationError, match="marked once"):
        BookmarkSet((TimeBookmark(600.0), TimeBookmark(600.0)))


# ------------------------------------------------------- crossing predicates
#
# A crossing is a transition between two readings rather than a comparison at
# one (project owner, 2026-09-20). Everything below turns on that: the
# boundary cases are where a comparison-at-one-reading rule would either stall
# a run forever on a height it settled at, or halt it again the moment it was
# resumed.


def _readings(**multiples: float) -> dict[RecordedQuantity, MacMultiple]:
    """One side of a step, naming every compartment a target could be set on.

    Unnamed compartments read zero, which is where a case opens, so a test
    states only the compartment it is about.
    """

    readings = {quantity: MacMultiple(0.0) for quantity in COMPARTMENT_QUANTITIES}
    readings.update(
        {RecordedQuantity(name): MacMultiple(value) for name, value in multiples.items()}
    )

    return readings


def test_a_time_bookmark_is_crossed_by_the_step_that_reaches_it() -> None:
    bookmark = TimeBookmark(30.0)

    assert bookmark.crossed_between(29.9, 30.0)
    assert bookmark.crossed_between(29.95, 30.05)


def test_a_time_bookmark_is_not_crossed_again_by_the_step_after_it() -> None:
    """The span is closed above and open below, so one instant is reached once."""

    bookmark = TimeBookmark(30.0)

    assert not bookmark.crossed_between(30.0, 30.1)
    assert not bookmark.crossed_between(29.8, 29.9)


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
    """The case a comparison at one reading could never let a run past.

    Tested as "the reading is at or above the height", every subsequent step
    of a run sitting exactly on the height would report a crossing and the run
    could not be advanced at all.
    """

    target = _target(multiple=0.8)

    assert target.crossed_between(MacMultiple(0.79), MacMultiple(0.80))
    assert not target.crossed_between(MacMultiple(0.80), MacMultiple(0.80))


def test_a_target_is_not_crossed_by_leaving_its_height_in_either_direction() -> None:
    """Which is what makes a halt resumable without re-halting on the same step."""

    target = _target(multiple=0.8)

    assert not target.crossed_between(MacMultiple(0.80), MacMultiple(0.81))
    assert not target.crossed_between(MacMultiple(0.80), MacMultiple(0.79))


def test_a_step_that_crossed_nothing_is_reported_as_no_crossing() -> None:
    marks = BookmarkSet().with_time_bookmark(TimeBookmark(30.0)).with_mac_target(_target())

    assert (
        marks.crossings_between(
            before_s=10.0,
            after_s=10.1,
            before=_readings(vessel_rich=0.1),
            after=_readings(vessel_rich=0.2),
        )
        is None
    )


def test_one_step_can_cross_a_marked_instant_and_a_marked_height_at_once() -> None:
    target = _target(multiple=0.8)
    marks = BookmarkSet().with_time_bookmark(TimeBookmark(30.0)).with_mac_target(target)

    crossing = marks.crossings_between(
        before_s=29.9,
        after_s=30.0,
        before=_readings(vessel_rich=0.79),
        after=_readings(vessel_rich=0.81),
    )

    assert crossing == BookmarkCrossing(30.0, (TimeBookmark(30.0),), (target,))


def test_a_reading_missing_a_marked_compartment_is_refused() -> None:
    marks = BookmarkSet().with_mac_target(_target(RecordedQuantity.FAT))
    short = {RecordedQuantity.VESSEL_RICH: MacMultiple(0.1)}

    with pytest.raises(SimulationConfigurationError, match="no fat compartment"):
        marks.crossings_between(before_s=0.0, after_s=0.1, before=short, after=short)


def test_a_crossing_naming_no_mark_at_all_is_refused() -> None:
    with pytest.raises(SimulationConfigurationError, match="at least one mark"):
        BookmarkCrossing(30.0)


# ------------------------------------------------------------------ standings


def _standings(
    marks: BookmarkSet,
    *,
    reached_instants_s: frozenset[float] = frozenset(),
    reached_crossings: frozenset[tuple[RecordedQuantity, float]] = frozenset(),
    opened_at_s: float = 0.0,
    stopped_at_cap: bool = False,
) -> object:
    """This set's standings, so a test states only the fact it is about."""

    return marks.standings(
        reached_instants_s=reached_instants_s,
        reached_crossings=reached_crossings,
        opened_at_s=opened_at_s,
        run_length_cap_s=MAXIMUM_ELAPSED_SIMULATION_TIME_S,
        stopped_at_cap=stopped_at_cap,
    )


def test_a_mark_the_run_can_still_reach_stands_as_still_running() -> None:
    bookmark = TimeBookmark(600.0)
    target = _target()
    marks = BookmarkSet().with_time_bookmark(bookmark).with_mac_target(target)

    standings = _standings(marks)

    assert standings.of_time_bookmark(bookmark) is MarkStanding.STILL_RUNNING
    assert standings.of_mac_target(target) is MarkStanding.STILL_RUNNING


def test_a_mark_the_run_halted_on_stands_as_reached() -> None:
    bookmark = TimeBookmark(600.0)
    target = _target()
    marks = BookmarkSet().with_time_bookmark(bookmark).with_mac_target(target)

    standings = _standings(
        marks,
        reached_instants_s=frozenset({600.0}),
        reached_crossings=frozenset({target.crossing_key}),
    )

    assert standings.of_time_bookmark(bookmark) is MarkStanding.REACHED
    assert standings.of_mac_target(target) is MarkStanding.REACHED


def test_a_relabelled_mark_keeps_what_the_run_did_with_it() -> None:
    """Matched the way `without_mac_target` matches, so a rename is not a new question."""

    renamed = _target(label="second gas on")
    marks = BookmarkSet().with_mac_target(renamed)

    standings = _standings(marks, reached_crossings=frozenset({_target().crossing_key}))

    assert standings.of_mac_target(renamed) is MarkStanding.REACHED


def test_a_target_still_outstanding_at_the_supported_run_length_says_it_was_not_reached() -> None:
    """A threshold above a compartment's asymptote, which is never reached.

    The run stops at `docs/MODEL.md` § "Supported run length" having answered
    the question, so the row must not go on saying the run is still working
    on it.
    """

    above_the_asymptote = _target(multiple=0.95)
    marks = BookmarkSet().with_mac_target(above_the_asymptote)

    standings = _standings(marks, stopped_at_cap=True)

    assert standings.of_mac_target(above_the_asymptote) is MarkStanding.NOT_REACHED_WITHIN_CAP


def test_a_bookmark_before_a_branch_fork_reads_apart_from_the_cap_case() -> None:
    """The fourth outcome, and the reason there are four rather than three.

    A branch inherits its trunk's marks, so a bookmark before the fork comes
    across and can never be reached going forward. Reporting it as "not
    reached within the cap" would say that running longer might reach it,
    which is false.
    """

    inherited = TimeBookmark(120.0)
    marks = BookmarkSet().with_time_bookmark(inherited)

    standings = _standings(marks, opened_at_s=300.0)

    assert standings.of_time_bookmark(inherited) is MarkStanding.BEFORE_THIS_BRANCH
    assert standings.of_time_bookmark(inherited) is not MarkStanding.NOT_REACHED_WITHIN_CAP


def test_a_bookmark_at_the_fork_instant_itself_is_not_called_unreachable() -> None:
    """The branch opens standing on it, so the run has not been put past it."""

    at_the_fork = TimeBookmark(300.0)
    marks = BookmarkSet().with_time_bookmark(at_the_fork)

    assert _standings(marks, opened_at_s=300.0).of_time_bookmark(at_the_fork) is (
        MarkStanding.STILL_RUNNING
    )


def test_a_bookmark_beyond_the_run_length_says_so_before_the_run_gets_there() -> None:
    """Decidable at once, so a learner is not left waiting out a simulated day."""

    beyond = TimeBookmark(MAXIMUM_ELAPSED_SIMULATION_TIME_S + 1.0)
    marks = BookmarkSet().with_time_bookmark(beyond)

    assert _standings(marks).of_time_bookmark(beyond) is MarkStanding.NOT_REACHED_WITHIN_CAP


def test_a_standing_asked_for_a_mark_that_was_never_evaluated_is_refused() -> None:
    """Rather than defaulting, which would draw a row asserting an answer nobody has."""

    standings = _standings(BookmarkSet())

    with pytest.raises(SimulationConfigurationError, match="does not hold the MAC target"):
        standings.of_mac_target(_target())

    with pytest.raises(SimulationConfigurationError, match="does not hold the time bookmark"):
        standings.of_time_bookmark(TimeBookmark(30.0))


# ---------------------------------------------------- halting on a crossing
#
# The half that has to be run rather than asserted. `PL-CTD7`'s claim is that
# the halt lands on the step that crossed, whatever the playback multiplier,
# so these drive a real `SimulationController` the way `run_view.step_tick`
# drives one: a burst of steps with nothing serviced between them.


def _step_until_halt(run: SimulationController, *, limit: int = 20_000) -> BookmarkCrossing | None:
    """Advance one step at a time until the run halts, or `limit` steps pass.

    Returns:
        What the run halted on, or `None` where it never halted. `None` rather
        than raising, so a test can assert that a run was *not* stopped.
    """

    for _ in range(limit):
        run.advance(STEP_S)

        if not run.is_running:
            return run.snapshot().bookmark_halt

    return None


def _tick_until_halt(
    run: SimulationController, *, steps_per_tick: int, limit: int = 20_000
) -> BookmarkCrossing | None:
    """The same, advanced in whole bursts the way a tick at `multiplier ×` does.

    Nothing is read between the steps of a burst, which is exactly the
    condition that made per-frame detection overshoot: the run is only asked
    whether it is still running once the burst has finished.
    """

    for _ in range(0, limit, steps_per_tick):
        for _ in range(steps_per_tick):
            run.advance(STEP_S)

        if not run.is_running:
            return run.snapshot().bookmark_halt

    return None


def _alveolar_mac_multiple(run: SimulationController) -> MacMultiple:
    """What the alveolar readout beside the target would say, in the target's unit."""

    snapshot = run.snapshot()

    return mac_multiple(snapshot.alveolar_partial_pressure_fraction, snapshot.agent_mac_percent)


def test_a_target_halts_on_every_crossing_in_either_direction() -> None:
    """Up through 0.5 ×MAC and back down through it stops the run twice.

    The decision of 2026-09-20: a target carries no crossing direction, so a
    case that passes through a marked height on the way up and again on the
    way down has reached what the learner marked both times. Halting only
    once would make `MacTarget`'s own docstring false for the second crossing.
    """

    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.5))
    run = SimulationController()
    run.add_mac_target(target)

    run.start()
    rising = _step_until_halt(run)

    assert rising is not None
    assert rising.mac_targets == (target,)

    # The vaporizer off, and the same height crossed again coming down.
    run.set_delivered_partial_pressure_fraction(Fraction(0.0))
    run.start()
    falling = _step_until_halt(run)

    assert falling is not None
    assert falling.mac_targets == (target,)
    assert falling.instant_s > rising.instant_s


def test_a_halt_lands_on_the_same_step_at_1x_and_at_300x() -> None:
    """The whole of `PL-CTD7`: the playback rate does not move the halt.

    A crossing tested once per rendered frame would land up to
    `multiplier × 0.1` s late — 30 simulated seconds at 300× — so the two runs
    below would stop at different concentrations from one another while both
    claimed to have stopped at 0.5 ×MAC.
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
    """So a control change made from the halt acts where the learner was looking.

    A setting changed while the run plays first acts at a tick boundary
    (`PL-NBWP`), which at 300× is up to 30 simulated seconds after the value
    on screen. No step is taken while paused, so a halt that pauses makes the
    pause-change-resume route automatic rather than something to know.
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
    # Neither a failure nor the end of the supported domain: an ordinary pause.
    assert snapshot.failure_reason is None
    assert snapshot.supported_limit_reason is None
    assert snapshot.bookmark_standings.of_mac_target(target) is MarkStanding.REACHED


def test_a_run_that_settles_exactly_on_a_target_halts_once_and_then_advances() -> None:
    """The boundary case, taken from the run itself so the height is landed on exactly.

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
    run.add_time_bookmark(TimeBookmark(30.0))
    run.start()

    halt = _tick_until_halt(run, steps_per_tick=STEPS_PER_TICK_AT_300X)

    assert halt == BookmarkCrossing(30.0, (TimeBookmark(30.0),))
    assert run.snapshot().elapsed_s == pytest.approx(30.0)


def test_an_unmarked_run_takes_the_same_trajectory_as_one_that_halted() -> None:
    """Detection observes the run; it does not change it.

    The marked run is stepped to the same instant through a halt and a resume,
    and has to stand where the unmarked one stands. `CLAUDE.md` requires
    deterministic results for identical inputs, and a halt is not an input.
    """

    marked = SimulationController()
    marked.add_time_bookmark(TimeBookmark(30.0))
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
    bookmark = TimeBookmark(30.0)
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

    bookmark = TimeBookmark(30.0)
    run = SimulationController()
    run.add_time_bookmark(bookmark)
    run.start()

    assert _step_until_halt(run) is not None

    run.remove_time_bookmark(bookmark)

    assert run.snapshot().bookmark_halt is None
