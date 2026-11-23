"""The simulation controller, driven against real runs.

These tests cover a mark the run is at, behind, or has passed and returns to.

`controller_support.py` holds what several of these files share.
"""

import pytest

from anesthesia_sim.app.bookmarks import BookmarkCrossing, MacTarget, MarkStanding, TimeBookmark
from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.controller import (
    BranchedCase,
    HereForkPoint,
    MarkForkPoint,
    SimulationController,
)
from anesthesia_sim.app.failures import FailureKind
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.core.concentration import MacMultiple, Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import (
    AlveolarVentilation,
    CardiacOutput,
    CaseInstant,
    FreshGasFlow,
)
from tests.integration.controller.controller_support import (
    _advance_for,
    _advance_through_halts,
    _advance_until_halted,
    _described,
    _states_agree_after_the_fork,
    _trunk_halted_on_a_bookmark,
    _trunk_paused_past_a_change,
    _trunk_with_two_changes,
)

# ------------------------------------------- a mark the run is at or behind
#
# These are six of `PL-3K9B`'s seven measured cases. Case B was a mark off the
# step grid, and no mark can be off it since `PL-SZ6G`. They run end to end
# rather than being asserted against `BookmarkSet.standings` directly, because
# the defect was never in that function. It was in what the controller passed
# to it. Each case makes the same claim. `STILL_RUNNING` says the run can
# still reach the mark, and in none of these cases could any step ever make
# that true.


def test_a_branch_forked_at_a_mark_on_the_step_grid_reads_it_as_passed() -> None:
    """Case A: a mark is a whole second, and a step ends on every whole second.

    The branch's first `before_s` is the fork itself, and `before_s` only
    increases. Because `crossed_between` uses a strict `<`, no step the branch
    ever takes can cross this instant. The test steps well past it to show
    that.
    """

    marked = SimulationController()
    on_the_grid = TimeBookmark(CaseInstant(30), "induction complete")
    marked.add_time_bookmark(on_the_grid)
    marked.start()
    _advance_until_halted(marked, limit_s=60)

    assert marked.snapshot().elapsed_s == 30.0

    branch = marked.resumed_here()
    branch.start()
    _advance_for(branch, duration_s=60)

    assert branch.snapshot().bookmark_standings.of_time_bookmark(on_the_grid) is (
        MarkStanding.PASSED
    )


def test_a_trunk_and_its_branch_agree_about_the_height_that_separated_them() -> None:
    """Case C, the worst of the seven by consequence.

    The branch's whole identity is *the management taken at this height*.
    Suppose a panel showed the trunk's row as reached and the branch's row as
    still running. The two runs would then disagree about the one instant that
    they share by construction. A target has no clock time to compare against,
    so this is the case that the seeded crossing is carried for.
    """

    marked = SimulationController()
    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.4), "the decision point")
    marked.add_mac_target(target)
    marked.start()
    _advance_until_halted(marked, limit_s=400)

    # A height stops the run as an instant does, and the offered fork point
    # says so in the same way.
    assert marked.here_fork_point == HereForkPoint(
        marked.snapshot().elapsed_s, stopped_on_mark=True
    )

    branch = marked.resumed_here()
    branch.start()
    _advance_for(branch, duration_s=300)

    assert marked.snapshot().bookmark_standings.of_mac_target(target) is MarkStanding.REACHED
    assert branch.snapshot().bookmark_standings.of_mac_target(target) is MarkStanding.REACHED


def test_a_mark_added_behind_a_running_trunk_is_not_called_still_reachable() -> None:
    """Case D, with no branch in it at all.

    A learner marks an instant the case has just run past when something
    interesting has already happened, and nothing refuses that. The instant
    can never enter the halt set, because the clock is already past it. So the
    halt set cannot decide the mark's standing.
    """

    run = SimulationController()
    run.start()
    _advance_for(run, duration_s=60)

    behind_the_clock = TimeBookmark(CaseInstant(30), "when the pressure dropped")
    run.add_time_bookmark(behind_the_clock)

    assert run.snapshot().bookmark_standings.of_time_bookmark(behind_the_clock) is (
        MarkStanding.PASSED
    )

    _advance_for(run, duration_s=120)

    assert run.snapshot().bookmark_standings.of_time_bookmark(behind_the_clock) is (
        MarkStanding.PASSED
    )


def test_a_branch_taken_at_a_control_event_agrees_with_its_trunk_about_a_mark_there() -> None:
    """Case E, at the fork method that predates bookmark forks entirely.

    The trunk halted on the mark, and a setting was then changed there, so the
    halt is a keyframe too. Like `resumed_here`, `resumed_at` asks the step
    that ends at the keyframe what it crossed. So the branch opens at the
    halt's crossing rather than at no crossing (`PL-1ZQ4`, case 3).
    """

    marked = SimulationController()
    at_the_keyframe = TimeBookmark(CaseInstant(30), "the decision point")
    marked.add_time_bookmark(at_the_keyframe)
    marked.start()
    _advance_until_halted(marked, limit_s=60)
    marked.set_fresh_gas_flow(FreshGasFlow(3.0))

    branch = marked.resumed_at(CaseInstant(30))

    assert branch.opened_from is not None
    assert branch.snapshot().bookmark_halt == BookmarkCrossing(CaseInstant(30), (at_the_keyframe,))
    assert branch.opened_from == marked.resumed_here().opened_from
    assert marked.snapshot().bookmark_standings.of_time_bookmark(at_the_keyframe) is (
        MarkStanding.PASSED
    )
    assert branch.snapshot().bookmark_standings.of_time_bookmark(at_the_keyframe) is (
        MarkStanding.PASSED
    )


def test_a_mark_removed_and_re_added_at_a_branch_s_fork_instant_still_reads_passed() -> None:
    """Case F: `_forget_unmarked` drops the run's record of the mark, and the clock still decides.

    Removing a mark clears the run's record of it, which is right, because the
    row is gone. An equal mark added afterwards is a new question about the
    same instant, and the run's clock is still at that instant.
    """

    marked = SimulationController()
    at_the_fork = TimeBookmark(CaseInstant(30))
    marked.add_time_bookmark(at_the_fork)
    marked.start()
    _advance_until_halted(marked, limit_s=60)

    branch = marked.resumed_here()
    branch.remove_time_bookmark(at_the_fork)
    re_added = TimeBookmark(CaseInstant(30), "asked again")
    branch.add_time_bookmark(re_added)

    assert branch.snapshot().bookmark_standings.of_time_bookmark(re_added) is MarkStanding.PASSED


def test_resetting_a_branch_leaves_it_standing_on_the_crossing_it_opened_at() -> None:
    """Case G: the crossing a branch opened at must survive a reset, or the defect returns.

    A branch's reset returns it to its fork, which is the crossing it opens
    at. So the halt it is stopped at, and what it has crossed, are part of
    where it is, not of what an earlier run did. `_open_at` is the path for
    both a reset and a fork, which is why the two end in identical states.
    """

    marked = SimulationController()
    at_the_fork = TimeBookmark(CaseInstant(30))
    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.15))
    marked.add_time_bookmark(at_the_fork)
    marked.add_mac_target(target)
    marked.start()
    _advance_until_halted(marked, limit_s=60)

    branch = marked.resumed_here()
    branch.start()
    _advance_for(branch, duration_s=30)
    branch.reset()
    after = branch.snapshot()

    assert after.elapsed_s == branch.began_at_s
    assert after.bookmark_halt is not None
    assert after.bookmark_standings.of_time_bookmark(at_the_fork) is MarkStanding.PASSED


def test_a_mark_unmarked_on_a_branch_does_not_come_back_with_its_reset() -> None:
    """The crossing a branch is stopped at is filtered by what is marked *now*, not by what was.

    A halt that names a row the panel no longer draws is the stale state that
    `_forget_unmarked` exists to prevent. A reset that starts again from the
    fork is the one place where that state could have come back.
    """

    marked = SimulationController()
    at_the_fork = TimeBookmark(CaseInstant(30))
    marked.add_time_bookmark(at_the_fork)
    marked.start()
    _advance_until_halted(marked, limit_s=60)

    branch = marked.resumed_here()
    branch.remove_time_bookmark(at_the_fork)
    branch.reset()

    assert branch.snapshot().bookmark_halt is None


def test_a_control_moved_before_a_bookmark_branch_steps_opens_a_segment_at_the_fork() -> None:
    """The bookmark analogue of reopening a branch's first segment in place.

    A branch forked at a control event opens its definition at the fork. So a
    dial turned before it steps rewrites that one segment, and the branch
    still has one segment. A bookmark branch has already reached past its
    definition's opening. So the change opens a second segment at the fork
    instead, carrying the fork's own state. That keeps the branch from
    propagating its parent's keyframe forward under settings the parent never
    used. The branch's two records still agree: the control timeline's time
    stamps are exactly the segment openings after the first.
    """

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    fork_state = marked._state.stored_states.state_at(CaseInstant(fork_s))
    branch = marked.resumed_here()

    branch.set_alveolar_ventilation(AlveolarVentilation(6.0))

    assert [segment.opened_at_s for segment in branch.run_segments] == [30.0, fork_s]
    assert branch._state.stored_states.state_at(branch.run_segments[1].opened_at_s) == fork_state
    assert [change.elapsed_s for change in branch.snapshot().control_timeline] == [
        segment.opened_at_s for segment in branch.run_segments
    ][1:]
    # And it is still drawn from the fork rather than from the earlier keyframe.
    assert branch.drawn_window(0.0, fork_s, 150).times_s == (fork_s,)


def test_a_bookmark_branch_draws_one_column_its_parent_does_not_and_it_is_the_fork() -> None:
    """`PL-2R2C`'s comparison property, and the one instant a bookmark fork adds to it.

    A branch is drawn on the trunk's own columns so the two traces can be read
    against each other. A fork at a control event adds nothing, because a
    control event is already a drawn instant on both. A bookmark's instant
    between two of the axis's columns is not, so the branch draws its own
    first point there and the trunk does not. The axis here has columns 10 s
    apart, and the mark is at 45 s.
    That is one vertex, at the instant the two runs stop being the same run,
    with the value both runs have there. The test pins this rather than
    leaving it implicit, so a later change that adds more such columns fails
    here rather than coming as a surprise.
    """

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    branch = marked.resumed_here()

    marked.start()
    _advance_for(marked, duration_s=30)
    branch.start()
    _advance_for(branch, duration_s=30)

    # Thirteen columns across 120 s are 10 s apart. The fork is not a multiple
    # of 10 s. If it were, it would be a column on the trunk too, and the test
    # would show nothing.
    assert fork_s % 10 != 0

    trunk_columns = set(marked.drawn_window(0.0, 120.0, 13).times_s)
    branch_columns = set(branch.drawn_window(0.0, 120.0, 13).times_s)

    assert branch_columns - trunk_columns == {fork_s}
    assert len(branch_columns & trunk_columns) > 2


def test_a_case_refuses_a_fork_where_its_trunk_stands_while_the_trunk_is_going() -> None:
    """The refusal passes through `BranchedCase` as the keyframe refusal does, and the offer too."""

    trunk = _trunk_with_two_changes()
    case = BranchedCase(trunk)

    assert case.here_fork_point == HereForkPoint(trunk.snapshot().elapsed_s, stopped_on_mark=False)

    trunk.start()

    assert case.here_fork_point is None

    with pytest.raises(SimulationConfigurationError, match="is still going"):
        case.fork_here()

    assert case.branches == ()


def test_a_bookmark_halt_is_not_one_of_the_fork_points_the_case_offers() -> None:
    """The two fork methods stay separate, which keeps the list of fork points stable.

    `fork_points_s` is the trunk's keyframes, and a halt records none. So the
    list does not change its members as the run halts and resumes. A caller
    holding an instant from the list cannot ask for a fork at a mark that the
    run has since stepped past.
    """

    marked = _trunk_halted_on_a_bookmark()
    case = BranchedCase(marked)
    fork_s = marked.snapshot().elapsed_s

    assert case.fork_points_s == (0.0, 30.0)
    assert fork_s not in case.fork_points_s

    # The halt can still be forked, by the other fork method.
    assert case.fork_here().began_at_s == fork_s


def test_two_branches_may_be_taken_at_one_bookmark() -> None:
    """The comparison the milestone is named for: one decision point, two managements.

    A learner marks the instant they want to decide at, the run stops there,
    and both managements are taken from that one state. Nothing about a
    bookmark fork makes it unique, exactly as nothing about a control-event
    fork does.
    """

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    case = BranchedCase(marked)

    first = case.fork_here()
    second = case.fork_here()

    assert first is not second
    assert case.branches == (first, second)
    assert first.began_at_s == second.began_at_s == fork_s
    assert first._state.stored_states.state_at(
        first.run_segments[0].opened_at_s
    ) == second._state.stored_states.state_at(second.run_segments[0].opened_at_s)
    # The trunk is still stopped at its halt. It was read twice and written
    # neither time.
    assert marked.snapshot().elapsed_s == fork_s
    assert marked.snapshot().bookmark_halt is not None


def test_a_branch_standing_on_its_own_halt_cannot_be_forked_either() -> None:
    """The flat shape still applies to the newer fork method, with the same message."""

    marked = _trunk_halted_on_a_bookmark()
    branch = marked.resumed_here()
    branch.add_time_bookmark(TimeBookmark(CaseInstant(branch.began_at_s + 5)))
    branch.start()
    _advance_until_halted(branch, limit_s=30)

    assert branch.snapshot().bookmark_halt is not None

    assert branch.here_fork_point is None

    with pytest.raises(SimulationConfigurationError, match="branch of a branch"):
        branch.resumed_here()


def test_a_setting_changed_while_halted_is_carried_by_the_halt_fork_and_the_keyframe_fork() -> None:
    """A branch at a halt and one at a control event agree after a change at that instant.

    A halt is an ordinary pause, and the setters apply unconditionally. So a
    learner may stop on a mark and dial something before branching. The
    change starts a new stretch at the halt instant, so the halt is now a
    keyframe as well. Both ways of branching at that instant name the same
    stretch as their provenance. It is the stretch that the halting step ran
    under (`PL-ZR49`). Both branches run under the change, which is what the
    dial shows at that instant. Each records the change in its own timeline
    (project owner, 2026-10-26). Both match, element for element, the trunk
    that made the change.
    """

    marked = SimulationController()
    marked.add_time_bookmark(TimeBookmark(CaseInstant(45), "the decision point"))
    marked.start()
    _advance_until_halted(marked, limit_s=60)

    fork_s = marked.snapshot().elapsed_s
    dialled = marked.snapshot().delivered_concentration_percent
    marked.set_delivered_concentration_percent(Percent(4.0))

    assert [segment.opened_at_s for segment in marked.run_segments] == [0.0, fork_s]
    assert marked.snapshot().bookmark_halt is not None

    here = marked.resumed_here()
    at_the_keyframe = marked.resumed_at(fork_s)

    assert here.opened_from == at_the_keyframe.opened_from
    assert here.opened_from is not None
    assert here.opened_from.segment == marked.run_segments[0]

    for branch in (here, at_the_keyframe):
        assert branch.snapshot().delivered_concentration_percent == 4.0
        assert _described(branch.snapshot().control_timeline) == [
            (fork_s, ControlInput.DELIVERED, dialled, 4.0)
        ]

    marked.start()
    _advance_for(marked, duration_s=30)

    for branch in (here, at_the_keyframe):
        branch.start()
        _advance_for(branch, duration_s=30)

        _states_agree_after_the_fork(branch, marked, fork_s, steps=30)


def test_two_reversible_acts_in_either_order_leave_one_branch() -> None:
    """Where a branch's definition opens cannot depend on the order of a dial and a reset.

    "Dial, dial back, reset" and "dial, reset, dial back" end at one branch:
    the same settings, live state, run definition and control timeline. Suppose
    the reset used the settings in place at that moment to decide where the
    definition opens. The second sequence would then open at the fork rather
    than at the parent's keyframe. It would restart from two propagations where
    the parent took one, and quietly stop reproducing the parent in 40 of 45
    elements, with nothing on screen to show it. Instead, `_open_at` records
    the dialled settings as a change at the fork, and `record_change`'s own
    collapse rule notices the dial-back.
    """

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    original = marked.snapshot().cardiac_output_l_min

    untouched = marked.resumed_here()
    dialled_back_first = marked.resumed_here()
    reset_first = marked.resumed_here()

    marked.start()
    _advance_for(marked, duration_s=60)
    marked.pause()

    dialled_back_first.set_cardiac_output(CardiacOutput(4.0))
    dialled_back_first.set_cardiac_output(CardiacOutput(original))
    dialled_back_first.reset()

    reset_first.set_cardiac_output(CardiacOutput(4.0))
    reset_first.reset()
    reset_first.set_cardiac_output(CardiacOutput(original))

    for branch in (untouched, dialled_back_first, reset_first):
        assert branch.snapshot().cardiac_output_l_min == original
        assert branch.run_segments[0].opened_at_s == 30.0
        assert len(branch.run_segments) == 1

        branch.start()
        _advance_for(branch, duration_s=60)
        branch.pause()

    for steps_past_fork in range(0, 61):
        case_s = fork_s + steps_past_fork * SIMULATION_STEP_S
        expected = marked._state.stored_states.state_at(CaseInstant(case_s))

        for name, branch in (
            ("untouched", untouched),
            ("dialled back before the reset", dialled_back_first),
            ("dialled back after the reset", reset_first),
        ):
            assert branch._state.stored_states.state_at(CaseInstant(case_s)) == expected, (
                f"the branch {name} differs from its parent at {case_s} s"
            )


def test_a_branch_reset_under_new_settings_records_them_at_its_fork() -> None:
    """Check the structure that the reset leaves, which is why the order does not matter.

    The parent's stretch, with its keyframe and its settings, stays the
    parent's. What the learner has dialled is a change the branch made at its
    own beginning. The keyframe that opens with that change is the fork's own
    state, so the trace starts where the readouts say the branch is.
    """

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    fork_state = marked._state.stored_states.state_at(CaseInstant(fork_s))
    branch = marked.resumed_here()

    branch.set_cardiac_output(CardiacOutput(4.0))
    branch.reset()

    assert [segment.opened_at_s for segment in branch.run_segments] == [30.0, fork_s]
    assert branch.run_segments[0].settings == marked.run_segments[-1].settings
    assert branch._state.stored_states.state_at(branch.run_segments[1].opened_at_s) == fork_state
    assert branch._state.stored_states.state_at(CaseInstant(fork_s)) == fork_state
    assert branch.drawn_window(0.0, fork_s, 150).times_s == (fork_s,)


def test_a_mark_set_behind_the_clock_can_be_returned_to() -> None:
    """`PL-W4XQ`'s deliverable: an instant marked after the run passed it, and returned to.

    When the item was filed, both fork methods refused it. The trunk has no
    keyframe there, and no step ever crossed a mark set after the clock had
    gone by. The branch opens where a halt would have stopped the run, from
    the state the trunk stored there. It reproduces the trunk element-wise
    from that instant on, and it leaves the trunk exactly the case it was.
    Since `PL-FST0`, `resumed_at` opens the same branch when it is given the
    mark's second.
    """

    trunk = _trunk_paused_past_a_change()
    mark = TimeBookmark(CaseInstant(60), "what if")
    trunk.add_time_bookmark(mark)
    keyframes = [
        (segment.opened_at_s, trunk._state.stored_states.state_at(segment.opened_at_s))
        for segment in trunk.run_segments
    ]

    assert 60 not in [instant_s for instant_s, _state in keyframes]

    # The paused trunk's own position is a separate fork point, and it is not the mark.
    here = trunk.here_fork_point

    assert here is not None
    assert here.fork_s == trunk.snapshot().elapsed_s != 60.0

    branch = trunk.resumed_at_mark(mark)

    assert trunk.resumed_at(CaseInstant(60)).opened_from == branch.opened_from

    assert branch.began_at_s == branch.snapshot().elapsed_s == 60.0
    assert branch.opened_from is not None
    assert branch.opened_from.fork.state == trunk._state.stored_states.state_at(CaseInstant(60))
    assert branch.snapshot().bookmark_standings.of_time_bookmark(mark) is MarkStanding.PASSED
    # The branch's definition opens at the trunk's own keyframe before the mark,
    # and nothing was recorded on the trunk to make one where it was marked.
    assert branch.run_segments[0].opened_at_s == 30.0
    assert [
        (segment.opened_at_s, trunk._state.stored_states.state_at(segment.opened_at_s))
        for segment in trunk.run_segments
    ] == keyframes
    assert trunk.snapshot().elapsed_s == 180.0

    branch.start()
    _advance_for(branch, duration_s=60)
    branch.pause()

    for steps_past_fork in range(0, 61):
        case_s = 60 + steps_past_fork * SIMULATION_STEP_S

        assert branch._state.stored_states.state_at(
            CaseInstant(case_s)
        ) == trunk._state.stored_states.state_at(CaseInstant(case_s)), (
            f"the branch and the trunk it returned to differ at {case_s} s"
        )


def test_a_mark_set_behind_the_clock_forks_where_its_halt_would_have() -> None:
    """Marking late changes when the mark was set, and nothing about the branch.

    The same case is run twice. In the first run, the mark is set before the
    clock reaches 45 s, so the run halts there and is forked at the halt. In
    the second, the mark is set only after the clock has passed it. No step
    crosses it, and the fork comes through `resumed_at_mark`. The two branches
    open at the same instant, 45 s, which is the end of the step that reached
    the mark. They open from the same state, inside the same stretch, at the
    same crossing.
    """

    at_the_halt = _trunk_halted_on_a_bookmark().resumed_here()

    late = SimulationController()
    late.start()
    _advance_for(late, duration_s=30)
    late.set_delivered_concentration_percent(Percent(4.0))
    _advance_for(late, duration_s=60)
    late.pause()
    late.add_time_bookmark(TimeBookmark(CaseInstant(45), "the decision point"))

    behind_the_clock = late.resumed_at_mark(TimeBookmark(CaseInstant(45)))

    assert behind_the_clock.began_at_s == 45
    assert behind_the_clock.opened_from is not None
    assert behind_the_clock.opened_from == at_the_halt.opened_from


def test_a_mark_the_run_halted_on_is_returned_to_alike_before_and_after_it_steps_on() -> None:
    """A step uses up the halt, but not the mark that the run stopped at.

    While the trunk is at the halt, both fork methods give the same branch.
    Once the trunk steps on, `resumed_here` opens where the trunk then is, as
    it should. The mark still gives the branch that the halt gave.
    """

    marked = _trunk_halted_on_a_bookmark()
    mark = TimeBookmark(CaseInstant(45))
    at_the_halt = marked.resumed_here()

    assert marked.resumed_at_mark(mark).opened_from == at_the_halt.opened_from

    marked.start()
    _advance_for(marked, duration_s=30)
    marked.pause()

    assert marked.resumed_here().began_at_s == marked.snapshot().elapsed_s > mark.instant_s
    assert marked.resumed_at_mark(mark).opened_from == at_the_halt.opened_from


def test_a_branch_returned_to_a_mark_opens_on_it_and_reads_it_as_passed() -> None:
    """A branch returned to a mark opens on the mark's own instant, and a reset returns it there.

    A mark is a whole number of seconds and a step ends on every whole second.
    So the branch opens on the mark, never just past it (`PL-SZ6G`). The
    branch reads the mark as passed, because the mark and the fork are one
    event (`PL-3K9B`), and a reset keeps that reading.

    The mark is at 47 s because 47 is prime, so no step longer than a second
    and shorter than the mark ends on it. With such a step the branch would
    open after its own mark. This test then fails, as the clock rule in
    `app/bookmarks.py` (`_time_bookmark_standing`) says it must.
    """

    trunk = _trunk_paused_past_a_change()
    mark = TimeBookmark(CaseInstant(47))
    trunk.add_time_bookmark(mark)

    branch = trunk.resumed_at_mark(mark)

    assert branch.began_at_s == 47
    assert branch.snapshot().bookmark_standings.of_time_bookmark(mark) is MarkStanding.PASSED

    branch.start()
    _advance_for(branch, duration_s=10)

    assert branch.snapshot().elapsed_s == 57

    branch.reset()

    assert branch.snapshot().elapsed_s == 47
    assert branch.snapshot().bookmark_standings.of_time_bookmark(mark) is MarkStanding.PASSED


def test_a_height_crossed_on_the_step_that_reached_a_passed_mark_is_stood_on_too() -> None:
    """The crossing is reconstructed by the rule that halts a run, so it names every mark crossed.

    One run finds the step on which a height is crossed, by halting there. A
    second, identical run marks that instant and that height only after its
    clock is well past both, so no step halted on either. Returning to the
    instant opens the branch at a crossing that names both, as a halt there
    would have.
    """

    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.4), "the decision point")
    finder = SimulationController()
    finder.add_mac_target(target)
    finder.start()
    _advance_until_halted(finder, limit_s=400)
    crossed_at_s = finder.snapshot().elapsed_s

    late = SimulationController()
    late.start()

    for _ in range(finder._state.step_count + 60):
        late.advance()

    late.pause()
    instant = TimeBookmark(CaseInstant(crossed_at_s))
    late.add_time_bookmark(instant)
    late.add_mac_target(target)

    branch = late.resumed_at_mark(instant)

    assert branch.opened_from is not None
    assert branch.snapshot().bookmark_halt == BookmarkCrossing(crossed_at_s, (instant,), (target,))
    assert branch.snapshot().bookmark_standings.of_mac_target(target) is MarkStanding.REACHED


def test_a_mark_added_after_the_step_that_crossed_it_reads_alike_on_every_run() -> None:
    """One result per mark, whichever run is asked and whichever order the mark and branch came in.

    These are the three cases that `PL-1ZQ4` reproduced. Each is built on the
    step on which a 0.3 xMAC alveolar target is crossed. A finder run halts
    there to identify that step. Each case asks that one step about marks
    added after it was taken:

    1. A trunk paused on the step, with the target added afterwards, showed
       the target as still running, while a branch opened there showed it as
       reached. They still disagreed 300 s later.
    2. A trunk halted on the step by a time mark. A target added before
       `fork_here` showed as reached on the branch. A target added to both
       runs after `fork_here` showed as still running.
    3. The same halt with a setting changed on it, so the halt is a keyframe
       too. `fork_at` there opened at no crossing, while `fork_here` opened at
       the halt's crossing.

    Every run here is stopped on that step or opened on it, so each mark that
    the step reached counts as crossed by it: the time mark as passed, and the
    target as reached (`docs/INTERFACE.md` § "Halting on a marked crossing").
    A step is one second, so the only instant that it can reach is the one it
    ends on. The time mark is therefore at that instant. In case 1 it is added
    after the pause, with the target.
    """

    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.3))
    finder = SimulationController()
    finder.add_mac_target(target)
    finder.start()
    _advance_until_halted(finder, limit_s=400)
    crossing_steps = finder._state.step_count
    crossed_at_s = finder.snapshot().elapsed_s
    # The crossing step ends at `crossed_at_s`, and this mark halts a run there.
    halting = TimeBookmark(CaseInstant(crossed_at_s), "halts the run")

    def standings(run: SimulationController) -> tuple[MarkStanding, ...]:
        answers = run.snapshot().bookmark_standings

        return (answers.of_time_bookmark(halting), answers.of_mac_target(target))

    def halted_on_the_step() -> SimulationController:
        run = SimulationController()
        run.add_time_bookmark(halting)
        run.start()
        _advance_until_halted(run, limit_s=400)
        assert run.snapshot().elapsed_s == crossed_at_s, "the premise: the halt is the step's"

        return run

    def add_the_late_target(*runs: SimulationController) -> None:
        for run in runs:
            run.add_mac_target(target)

    reached = (MarkStanding.PASSED, MarkStanding.REACHED)

    # Case 1: a plain pause, with the target added afterwards. The time mark
    # is added with it, so every run is asked about the same two marks.
    paused = SimulationController()
    paused.start()

    for _ in range(crossing_steps):
        paused.advance()

    paused.pause()
    paused.add_time_bookmark(halting)
    add_the_late_target(paused)
    from_the_pause = BranchedCase(paused).fork_here()

    assert standings(paused) == standings(from_the_pause) == reached

    for run in (paused, from_the_pause):
        run.start()
        _advance_for(run, duration_s=300)
        run.pause()

    assert paused.snapshot().elapsed_s == from_the_pause.snapshot().elapsed_s
    assert standings(paused) == standings(from_the_pause) == reached

    # Case 2: one trunk gets the late target before it is branched. The other is branched
    # first, and then both runs get the target.
    marked_first = halted_on_the_step()
    add_the_late_target(marked_first)
    branched_after_marking = BranchedCase(marked_first).fork_here()

    branched_first = halted_on_the_step()
    branched_before_marking = BranchedCase(branched_first).fork_here()
    add_the_late_target(branched_first, branched_before_marking)

    assert standings(marked_first) == standings(branched_after_marking) == reached
    assert standings(branched_first) == standings(branched_before_marking) == reached

    # Case 3: a setting change makes the halt a keyframe, then both fork methods are used.
    changed_on_the_halt = halted_on_the_step()
    changed_on_the_halt.set_fresh_gas_flow(FreshGasFlow(3.0))
    add_the_late_target(changed_on_the_halt)
    case = BranchedCase(changed_on_the_halt)
    at_the_keyframe = case.fork_at(CaseInstant(crossed_at_s))
    where_it_stands = case.fork_here()

    assert at_the_keyframe.opened_from is not None
    assert at_the_keyframe.snapshot().bookmark_halt == BookmarkCrossing(
        CaseInstant(crossed_at_s), (halting,), (target,)
    )
    assert at_the_keyframe.opened_from == where_it_stands.opened_from
    assert standings(changed_on_the_halt) == reached
    assert standings(at_the_keyframe) == standings(where_it_stands) == reached


def test_a_mark_at_the_case_s_opening_returns_to_induction_with_no_crossing() -> None:
    """No step reaches it, because the run is at it from the start, so the fork is the opening.

    The branch is the one that `resumed_at` gives at the opening keyframe, and
    the clock alone shows the mark as passed there.
    """

    trunk = _trunk_paused_past_a_change()
    at_induction = TimeBookmark(CaseInstant(0), "induction")
    trunk.add_time_bookmark(at_induction)

    returned = trunk.resumed_at_mark(at_induction)

    assert returned.opened_from is not None
    assert returned.snapshot().bookmark_halt is None
    assert returned.opened_from == trunk.resumed_at(CaseInstant(0)).opened_from
    assert returned.snapshot().bookmark_standings.of_time_bookmark(at_induction) is (
        MarkStanding.PASSED
    )


def test_a_mark_is_returned_to_by_its_instant_whatever_label_the_caller_holds() -> None:
    """The mark is matched as removal matches it, and the crossing carries the run's own copy."""

    trunk = _trunk_paused_past_a_change()
    held = TimeBookmark(CaseInstant(60), "what if")
    trunk.add_time_bookmark(held)

    branch = trunk.resumed_at_mark(TimeBookmark(CaseInstant(60)))

    assert branch.opened_from is not None
    halt = branch.snapshot().bookmark_halt
    assert halt is not None
    assert halt.time_bookmarks == (held,)


def test_a_mark_still_ahead_of_the_clock_cannot_be_returned_to() -> None:
    """The case has no state there yet, and a fork there would be a prediction drawn as a run."""

    trunk = _trunk_paused_past_a_change()
    ahead = TimeBookmark(CaseInstant(600))
    trunk.add_time_bookmark(ahead)

    with pytest.raises(SimulationConfigurationError, match="short of the mark at 10m"):
        trunk.resumed_at_mark(ahead)

    assert trunk.mark_fork_points == ()


def test_an_instant_nobody_marked_cannot_be_returned_to_as_a_mark() -> None:
    """The method takes a mark the run has, so the learner must mark the instant first."""

    trunk = _trunk_paused_past_a_change()

    with pytest.raises(SimulationConfigurationError, match="no time bookmark stands at 1m,"):
        trunk.resumed_at_mark(TimeBookmark(CaseInstant(60)))


def test_a_branch_cannot_be_returned_to_a_mark_it_has_passed() -> None:
    """The flat shape still applies to the third fork method, with the same message."""

    trunk = _trunk_paused_past_a_change()
    mark = TimeBookmark(CaseInstant(60))
    trunk.add_time_bookmark(mark)
    branch = trunk.resumed_at_mark(mark)
    branch.start()
    _advance_for(branch, duration_s=30)
    branch.pause()
    later = TimeBookmark(CaseInstant(75))
    branch.add_time_bookmark(later)

    with pytest.raises(SimulationConfigurationError, match="branch of a branch"):
        branch.resumed_at_mark(later)


def test_the_marks_a_trunk_can_be_returned_to_are_the_ones_its_standings_call_passed() -> None:
    """The marks come earliest first, each with the instant a branch opens at, none ahead."""

    trunk = _trunk_paused_past_a_change()
    later = TimeBookmark(CaseInstant(120), "added first")
    ahead = TimeBookmark(CaseInstant(600))
    earlier = TimeBookmark(CaseInstant(45))

    for mark in (later, ahead, earlier):
        trunk.add_time_bookmark(mark)

    snapshot = trunk.snapshot()

    assert trunk.mark_fork_points == (
        MarkForkPoint(earlier, CaseInstant(45)),
        MarkForkPoint(later, CaseInstant(120)),
    )
    assert {point.bookmark for point in trunk.mark_fork_points} == {
        mark
        for mark in snapshot.bookmarks.time_bookmarks
        if snapshot.bookmark_standings.of_time_bookmark(mark) is MarkStanding.PASSED
    }


def test_a_trunk_that_has_not_stepped_can_be_returned_only_to_a_mark_at_its_opening() -> None:
    """With no step taken, no mark can be reached, and the run is still at its opening."""

    trunk = SimulationController()
    at_induction = TimeBookmark(CaseInstant(0))
    ahead = TimeBookmark(CaseInstant(30))
    trunk.add_time_bookmark(at_induction)
    trunk.add_time_bookmark(ahead)

    assert trunk.mark_fork_points == (MarkForkPoint(at_induction, CaseInstant(0)),)
    assert trunk.resumed_at_mark(at_induction).began_at_s == 0.0

    with pytest.raises(SimulationConfigurationError, match="short of the mark at 30s"):
        trunk.resumed_at_mark(ahead)


def test_a_case_keeps_a_branch_returned_to_a_mark_its_trunk_has_passed() -> None:
    """The case-level method keeps the branch and adds no instant to `fork_points_s`."""

    trunk = _trunk_paused_past_a_change()
    mark = TimeBookmark(CaseInstant(60))
    trunk.add_time_bookmark(mark)
    case = BranchedCase(trunk)

    assert case.mark_fork_points == trunk.mark_fork_points

    branch = case.fork_at_mark(mark)

    assert case.branches == (branch,)
    assert branch.began_at_s == 60.0
    assert case.fork_points_s == (0.0, 30.0)
    assert trunk.snapshot().elapsed_s == 180.0


def test_a_case_refuses_a_mark_its_trunk_has_not_reached_and_keeps_nothing() -> None:
    """The refusal passes through `BranchedCase`, as the other two fork methods' refusals do."""

    trunk = _trunk_paused_past_a_change()
    ahead = TimeBookmark(CaseInstant(600))
    trunk.add_time_bookmark(ahead)
    case = BranchedCase(trunk)

    with pytest.raises(SimulationConfigurationError, match="short of the mark"):
        case.fork_at_mark(ahead)

    assert case.branches == ()


# ------------------------------- what the run did with a mark, as it moves on
#
# A MAC target has no clock time, so its standing is only what the run did:
# the heights it halted on, and the step it stands on while it is stopped. The
# tests below hold that record to the run's history. Each expected standing
# comes from an unmarked run of the same case, or from a run that halts on the
# height to find the step that crosses it.


def _mac_multiple_of(fraction: float, mac_percent: float) -> float:
    """Return a compartment fraction as a multiple of the agent's MAC, worked out here.

    The MAC is a percent of one atmosphere, so dividing it by 100 gives it as
    the same kind of fraction as the compartment's.
    """

    return fraction / (mac_percent / 100.0)


def _steps_to_cross(target: MacTarget) -> int:
    """Return how many steps a default run takes to cross `target`, found by halting a run there."""

    finder = SimulationController()
    finder.add_mac_target(target)
    finder.start()
    _advance_until_halted(finder, limit_s=400)

    return finder._state.step_count


def test_a_height_the_run_halted_on_stays_reached_after_it_halts_on_a_higher_one() -> None:
    """A target that halted the run reads reached for the rest of the run.

    The run halts on a 0.3 ×MAC alveolar target, is started again, halts on a
    0.5 ×MAC alveolar target, and is started again. It is paused 30 s later,
    on a step that crosses neither height. A height has no clock time, so only
    the run's record of the heights it halted on can say that the first target
    was reached. A record that kept only the latest halt would show the first
    target as one the run can still reach, which a learner would read as a
    level the patient has not yet been at.

    The expected standings come from an unmarked run of the same length. Its
    alveolar reading ends above both heights, and under one set of settings
    it rises the whole way, so it passed each height once.
    """

    lower = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.3), "first")
    higher = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.5), "second")
    marked = SimulationController()
    marked.add_mac_target(lower)
    marked.add_mac_target(higher)
    marked.start()
    _advance_until_halted(marked, limit_s=400)
    marked.start()
    _advance_until_halted(marked, limit_s=400)
    marked.start()
    _advance_for(marked, duration_s=30)
    marked.pause()

    unmarked = SimulationController()
    unmarked.start()
    _advance_for(unmarked, duration_s=marked._state.step_count)
    at_the_end = unmarked.snapshot()
    mac_percent = at_the_end.agent_mac_percent

    assert at_the_end.elapsed_s == marked.snapshot().elapsed_s
    assert _mac_multiple_of(at_the_end.alveolar_partial_pressure_fraction, mac_percent) > 0.5

    standings = marked.snapshot().bookmark_standings

    assert standings.of_mac_target(lower) is MarkStanding.REACHED
    assert standings.of_mac_target(higher) is MarkStanding.REACHED


def test_removing_one_mark_leaves_the_standing_of_every_other_mark_as_it_was() -> None:
    """Removing a mark forgets what the run did with that mark and with no other.

    The run holds time marks at 30 s and 600 s, a 0.3 ×MAC alveolar target
    and a 0.5 ×MAC fat target, and runs to 200 s. Then one more mark of each
    kind is removed. The removal must not turn a mark the run has not reached
    into one it has. A row that read passed or reached for a mark still ahead
    would tell the learner that the patient had already been there.

    The expected standings are worked out apart from the controller. The clock
    stands at 200 s, so the mark at 30 s is behind it and the mark at 600 s is
    ahead. An unmarked run of the same 200 s has an alveolar reading above
    0.3 ×MAC and a fat reading below 0.5 ×MAC. Both rise the whole way under
    one set of settings.
    """

    behind = TimeBookmark(CaseInstant(30), "behind")
    ahead = TimeBookmark(CaseInstant(600), "ahead")
    removed_instant = TimeBookmark(CaseInstant(60), "removed")
    reached = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.3), "reached")
    not_reached = MacTarget(RecordedQuantity.FAT, MacMultiple(0.5), "not reached")
    removed_height = MacTarget(RecordedQuantity.MUSCLE, MacMultiple(0.9), "removed")
    run = SimulationController()

    for bookmark in (behind, ahead, removed_instant):
        run.add_time_bookmark(bookmark)

    for target in (reached, not_reached, removed_height):
        run.add_mac_target(target)

    _advance_through_halts(run, duration_s=200)
    run.pause()
    run.remove_time_bookmark(removed_instant)
    run.remove_mac_target(removed_height)

    unmarked = SimulationController()
    unmarked.start()
    _advance_for(unmarked, duration_s=200)
    at_200_s = unmarked.snapshot()
    mac_percent = at_200_s.agent_mac_percent

    assert run.snapshot().elapsed_s == at_200_s.elapsed_s == 200
    assert _mac_multiple_of(at_200_s.alveolar_partial_pressure_fraction, mac_percent) > 0.3
    assert _mac_multiple_of(at_200_s.fat_partial_pressure_fraction, mac_percent) < 0.5

    standings = run.snapshot().bookmark_standings

    assert standings.of_time_bookmark(behind) is MarkStanding.PASSED
    assert standings.of_time_bookmark(ahead) is MarkStanding.STILL_RUNNING
    assert standings.of_mac_target(reached) is MarkStanding.REACHED
    assert standings.of_mac_target(not_reached) is MarkStanding.STILL_RUNNING


def test_a_height_crossed_by_the_last_step_reads_reached_only_while_the_run_is_stopped() -> None:
    """A run stands on its last step only while it is stopped and has not failed.

    A finder run halts on a 0.3 ×MAC alveolar target to find the step that
    crosses it. Four runs of the same case then end on that step, and the
    target is added to each only afterwards, so no step halted on it.

    1. A trunk that is still going stands on no step, because its position
       moves with every step. The target is still to come.
    2. The same trunk, once paused, stands on the step, so the target reads
       reached.
    3. A trunk that failed on that step is not paused (`RunStatus.failure_reason`),
       so the target reads not reached before the failure.
    4. A branch opened at 60 s that steps on to the same step and is paused
       stands on that step, as the trunk does. Its own fork lies far below the
       height, so only the step it stands on can reach the target.
    """

    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.3))
    crossing_steps = _steps_to_cross(target)

    def on_the_crossing_step() -> SimulationController:
        run = SimulationController()
        run.start()
        _advance_for(run, duration_s=crossing_steps)

        return run

    going = on_the_crossing_step()
    going.add_mac_target(target)

    assert going.is_running
    assert going.snapshot().bookmark_standings.of_mac_target(target) is MarkStanding.STILL_RUNNING

    going.pause()

    assert going.snapshot().bookmark_standings.of_mac_target(target) is MarkStanding.REACHED

    failed = on_the_crossing_step()
    failed.fail("a step raised", kind=FailureKind.UNEXPECTED)
    failed.add_mac_target(target)

    assert failed.snapshot().bookmark_standings.of_mac_target(target) is (
        MarkStanding.NOT_REACHED_BEFORE_FAILURE
    )

    trunk = SimulationController()
    trunk.start()
    _advance_for(trunk, duration_s=60)
    trunk.pause()
    branch = trunk.resumed_here()
    branch.start()
    _advance_for(branch, duration_s=crossing_steps - 60)
    branch.pause()
    branch.add_mac_target(target)

    assert branch.snapshot().elapsed_s == crossing_steps * SIMULATION_STEP_S
    assert branch.snapshot().bookmark_standings.of_mac_target(target) is MarkStanding.REACHED


def test_a_mark_added_on_the_step_a_learner_paused_on_does_not_make_the_pause_a_halt() -> None:
    """The halt record names a mark only where a run stopped on it, never where it was paused.

    A trunk is paused by hand on the step that crosses a 0.3 ×MAC alveolar
    target, and the target is added afterwards. The target reads reached,
    because the run stands on the step that crossed it. But no mark stopped
    the run, so there is no halt record, and the place offered for a branch
    is not a stop on a mark. A banner that called the pause a halt would tell
    the learner that the run had stopped itself at a height they marked.
    """

    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.3))
    crossing_steps = _steps_to_cross(target)
    paused = SimulationController()
    paused.start()
    _advance_for(paused, duration_s=crossing_steps)
    paused.pause()
    paused.add_mac_target(target)

    snapshot = paused.snapshot()

    assert snapshot.bookmark_standings.of_mac_target(target) is MarkStanding.REACHED
    assert snapshot.bookmark_halt is None
    assert paused.here_fork_point == HereForkPoint(snapshot.elapsed_s, stopped_on_mark=False)


# --- A removed mark put back by Undo (PL-5GX4) --------------------------------
#
# Removing a mark drops the run's record of what it did with the mark
# (`_forget_unmarked`). An Undo puts the record back, but only into the run
# that made it.


def test_a_reached_target_put_back_after_its_removal_reads_reached_where_it_was() -> None:
    """An undone removal restores the target's row and its standing, after the run moved on.

    The run halts on the target and then runs on past it, so the only record
    that it reached the target is the one that a removal drops. While the run
    still stands on the halt, the halt alone shows the target as reached. The
    expected values are the ones the run showed before the removal. A target
    added back as new instead goes to the end of the list and reads as still
    to come.
    """

    controller = SimulationController()
    below = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.10))
    crossed = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.15), "the one stopped on")
    above = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(1.5))

    for target in (below, crossed, above):
        controller.add_mac_target(target)

    controller.start()
    _advance_until_halted(controller, limit_s=60)
    controller.start()
    _advance_until_halted(controller, limit_s=60)
    controller.start()
    _advance_for(controller, duration_s=10)
    before = controller.snapshot()
    assert before.bookmark_standings.of_mac_target(crossed) is MarkStanding.REACHED
    assert before.bookmark_halt is None

    removed = controller.remove_mac_target(crossed)
    controller.restore_mark(removed)
    after = controller.snapshot()

    assert after.bookmarks == before.bookmarks
    assert after.bookmark_standings == before.bookmark_standings


def test_a_target_reached_by_the_step_a_paused_run_stands_on_is_reached_after_undo() -> None:
    """A target added on a paused run's crossing step, removed, then put back after Start.

    Blind review of `PL-5GX4` found this sequence. The target reads as reached
    only through the step the paused run stands on (`PL-1ZQ4`). Start keeps
    that step's crossings only for the marks held at the time, and this one
    was removed then. The expected standing is the one a finder run halts on
    at the same step, which never removes the target.
    """

    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.3))
    finder = SimulationController()
    finder.add_mac_target(target)
    finder.start()
    _advance_until_halted(finder, limit_s=400)
    assert finder.snapshot().bookmark_standings.of_mac_target(target) is MarkStanding.REACHED

    paused = SimulationController()
    paused.start()

    for _ in range(finder._state.step_count):
        paused.advance()

    paused.pause()
    paused.add_mac_target(target)
    assert paused.snapshot().bookmark_standings.of_mac_target(target) is MarkStanding.REACHED

    removed = paused.remove_mac_target(target)
    paused.start()
    _advance_for(paused, duration_s=10)
    paused.restore_mark(removed)

    assert paused.snapshot().bookmark_standings.of_mac_target(target) is MarkStanding.REACHED


def test_a_time_mark_put_back_after_its_removal_returns_to_its_row() -> None:
    """The middle of three time marks returns between the other two, as the run held it."""

    controller = SimulationController()
    marks = [
        TimeBookmark(CaseInstant(instant_s), f"mark {instant_s}") for instant_s in (90, 30, 60)
    ]

    for mark in marks:
        controller.add_time_bookmark(mark)

    controller.start()
    _advance_until_halted(controller, limit_s=60)
    before = controller.snapshot()

    removed = controller.remove_time_bookmark(TimeBookmark(CaseInstant(30)))
    controller.restore_mark(removed)
    after = controller.snapshot()

    assert removed.position == 1
    assert after.bookmarks.time_bookmarks == tuple(marks)
    assert after.bookmark_halt == before.bookmark_halt


def test_a_removed_time_mark_records_whether_the_run_had_passed_it() -> None:
    """The record of a removed time mark says whether the run's clock was at or past it.

    The run halts on the mark at 30 s and then runs on to 40 s. Its clock is
    then past that mark and short of the one at 600 s, so `docs/INTERFACE.md`
    § "What a mark's row reports" calls the first passed and the second still
    running.
    """

    controller = SimulationController()
    behind = TimeBookmark(CaseInstant(30))
    ahead = TimeBookmark(CaseInstant(600))

    for mark in (behind, ahead):
        controller.add_time_bookmark(mark)

    controller.start()
    _advance_until_halted(controller, limit_s=60)
    controller.start()
    _advance_for(controller, duration_s=10)

    assert controller.snapshot().elapsed_s == 40
    assert controller.remove_time_bookmark(behind).reached
    assert not controller.remove_time_bookmark(ahead).reached


def test_a_target_put_back_after_a_reset_reads_as_the_new_run_has_it() -> None:
    """A reset begins a new run, so the old run's crossing is not put back into it.

    The expected standing is a fresh run's, built directly with the same
    target and never stepped.
    """

    controller = SimulationController()
    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.15))
    controller.add_mac_target(target)
    controller.start()
    _advance_until_halted(controller, limit_s=60)
    assert controller.snapshot().bookmark_standings.of_mac_target(target) is MarkStanding.REACHED

    removed = controller.remove_mac_target(target)
    controller.reset()
    controller.restore_mark(removed)
    fresh = SimulationController()
    fresh.add_mac_target(target)

    assert removed.reached
    assert (
        controller.snapshot().bookmark_standings.of_mac_target(target)
        is fresh.snapshot().bookmark_standings.of_mac_target(target)
        is MarkStanding.STILL_RUNNING
    )
