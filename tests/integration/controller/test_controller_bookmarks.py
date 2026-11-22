"""The simulation controller, driven against real runs.

These tests cover bookmarks, and branches taken at a bookmark.

`controller_support.py` holds what several of these files share.
"""

from collections.abc import Callable

import pytest

from anesthesia_sim.app.bookmarks import MacTarget, MarkStanding, TimeBookmark
from anesthesia_sim.app.controller import (
    BranchedCase,
    HereForkPoint,
    SimulationController,
    SimulationSnapshot,
)
from anesthesia_sim.app.formatting import MAC_UNIT_SUFFIX, format_mac_multiple
from anesthesia_sim.app.run_series import (
    COMPARTMENT_QUANTITIES,
    COMPARTMENT_STATE_INDEX,
    RecordedQuantity,
)
from anesthesia_sim.core.concentration import Fraction, MacMultiple, Percent, fraction_from_percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CaseInstant, FreshGasFlow
from anesthesia_sim.core.uptake_system import AgentUptakeSystem
from tests.integration.controller.controller_support import (
    _advance_for,
    _advance_until_halted,
    _run_with_two_changes,
    _trunk_halted_on_a_bookmark,
    _trunk_with_two_changes,
)

# --------------------------------------------------------------- bookmarks
#
# `tests/unit/test_bookmarks.py` covers what a mark rejects. This section
# covers the controller's half. It checks that the collections reach a reader
# through the snapshot. It also checks what happens to them at the three
# points where a run starts over: `reset`, `set_agent` and a fork. Each of
# those three is a decision rather than a consequence, so each has a test
# that says which way it went and why (`PL-LPLD`).


def test_a_fresh_run_is_marked_at_nothing() -> None:
    assert SimulationController().snapshot().bookmarks.is_empty


def test_a_mark_reaches_a_reader_through_the_snapshot() -> None:
    controller = SimulationController()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(600), "intubation"))
    controller.add_mac_target(MacTarget(RecordedQuantity.VESSEL_RICH, MacMultiple(0.8), "wash-in"))

    marks = controller.snapshot().bookmarks

    assert [bookmark.label for bookmark in marks.time_bookmarks] == ["intubation"]
    assert [target.label for target in marks.mac_targets] == ["wash-in"]


def test_the_two_collections_are_added_to_and_removed_from_independently() -> None:
    controller = SimulationController()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(600)))
    controller.add_mac_target(MacTarget(RecordedQuantity.FAT, MacMultiple(0.5)))
    controller.remove_time_bookmark(TimeBookmark(CaseInstant(600)))

    marks = controller.snapshot().bookmarks

    assert marks.time_bookmarks == ()
    assert len(marks.mac_targets) == 1


def test_a_snapshot_taken_before_a_mark_was_added_does_not_acquire_it() -> None:
    # The snapshot is a read-only view of one instant. A panel that keeps a
    # snapshot from an earlier tick must not come to describe a later run.
    controller = SimulationController()
    before = controller.snapshot()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(600)))

    assert before.bookmarks.is_empty
    assert not controller.snapshot().bookmarks.is_empty


def test_a_marked_instant_cannot_be_marked_twice_through_the_controller() -> None:
    controller = SimulationController()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(600)))

    with pytest.raises(SimulationConfigurationError, match="marked once"):
        controller.add_time_bookmark(TimeBookmark(CaseInstant(600), "and again"))

    assert len(controller.snapshot().bookmarks.time_bookmarks) == 1


def test_resetting_a_run_keeps_its_marks() -> None:
    # A reset is for running the same case again, and it is the same case the
    # learner was asking about. So the marks stay with the settings rather
    # than with the state.
    controller = SimulationController()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(600)))
    controller.start()
    _advance_for(controller, duration_s=30)
    controller.reset()

    assert controller.snapshot().bookmarks.time_bookmarks == (TimeBookmark(CaseInstant(600)),)


def test_changing_agent_keeps_the_marks_although_it_destroys_the_run() -> None:
    # A MAC target is a multiple of whichever agent is running, so 0.8 x MAC
    # stays 0.8 x MAC of the new agent rather than becoming the old agent's
    # absolute concentration under a new divisor. A learner who changes agent
    # wants to see the same multiple reached at a different time.
    controller = SimulationController()
    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.8))
    controller.add_mac_target(target)
    controller.start()
    _advance_for(controller, duration_s=30)
    controller.set_agent("desflurane")

    after = controller.snapshot()

    assert after.agent_id == "desflurane"
    assert after.control_timeline == ()
    assert after.bookmarks.mac_targets == (target,)


def _run_to_halt(
    controller: SimulationController, reading_of: Callable[[SimulationSnapshot], Fraction]
) -> tuple[float, SimulationSnapshot]:
    """Advance one step at a time until a mark halts the run.

    Returns the reading on the step before the halt, in multiples of MAC, and
    the halted snapshot.
    """

    mac_fraction = float(fraction_from_percent(controller.snapshot().agent_mac_percent))
    before = float(reading_of(controller.snapshot())) / mac_fraction
    for _ in range(60 // SIMULATION_STEP_S):
        controller.advance()
        snapshot = controller.snapshot()
        if snapshot.bookmark_halt is not None:
            return before, snapshot
        before = float(reading_of(snapshot)) / mac_fraction
    raise AssertionError("no mark halted the run within 60 s")


def _sevoflurane_at_8_percent_and_10_l_min() -> SimulationController:
    controller = SimulationController()
    controller.set_agent("sevoflurane")
    controller.set_fresh_gas_flow(FreshGasFlow(10.0))
    controller.set_delivered_concentration_percent(Percent(8.0))
    return controller


def test_a_circuit_target_halts_within_one_step_of_its_mark_and_can_show_counts_past() -> None:
    """The simulation halts within one simulation step of the mark, as `docs/INTERFACE.md` now says.

    A mark is the target value that the learner sets for a reading. The simulation halts when
    the reading crosses it. § "Halting on a marked crossing" used to say that the value
    displayed beside a halt is the value the learner marked (`PL-M8F6`). The specification
    now gives this case as its first example. With 8% sevoflurane at 10 L/min, a 0.10 ×MAC
    circuit target halts showing 0.12 ×MAC, two display counts past its mark. A bare uptake
    system with the same settings reads 0.1211 ×MAC of sevoflurane's 1.80% at 1 s
    (measured 2026-11-22). When the stored MAC was 2.0%, the same reading was 0.11 ×MAC.
    """

    controller = _sevoflurane_at_8_percent_and_10_l_min()
    mark = MacMultiple(0.10)
    controller.add_mac_target(MacTarget(RecordedQuantity.CIRCUIT, mark))
    controller.start()

    before, halted = _run_to_halt(
        controller, lambda snapshot: snapshot.inspired_partial_pressure_fraction
    )

    # The halting step is the one that crossed: the reading before it was
    # below the mark, and its own reading is at or past it.
    mac_fraction = float(fraction_from_percent(halted.agent_mac_percent))
    assert before < mark <= float(halted.inspired_partial_pressure_fraction) / mac_fraction
    assert format_mac_multiple(
        halted.inspired_partial_pressure_fraction, halted.agent_mac_percent
    ) == (f"0.12{MAC_UNIT_SUFFIX}")


def test_an_alveolar_target_can_halt_many_counts_past_its_mark_when_ventilation_resumes() -> None:
    """In one simulation step, a reading can move many display counts past its mark.

    A display count is one unit of the last digit shown. This test is the second case that
    `docs/INTERFACE.md` § "Halting on a marked crossing" describes. After 120 s with no
    alveolar ventilation, the circuit has filled but the alveolar reading is still zero. When
    ventilation is restored to 12 L/min, the alveolar reading rises in the next one-second
    step from zero to 0.32 ×MAC. So a 0.10 ×MAC alveolar target halts showing 0.32 ×MAC,
    twenty-two display counts past its mark.

    The expected reading comes from an uptake system built directly from the core, with no
    controller and no mark. It is given the same settings and takes the same 121 steps.
    """

    controller = _sevoflurane_at_8_percent_and_10_l_min()
    controller.set_alveolar_ventilation(AlveolarVentilation(0.0))
    controller.start()
    for _ in range(120 // SIMULATION_STEP_S):
        controller.advance()
    assert controller.snapshot().alveolar_partial_pressure_fraction == 0.0
    mark = MacMultiple(0.10)
    controller.add_mac_target(MacTarget(RecordedQuantity.ALVEOLAR, mark))
    controller.set_alveolar_ventilation(AlveolarVentilation(12.0))

    before, halted = _run_to_halt(
        controller, lambda snapshot: snapshot.alveolar_partial_pressure_fraction
    )

    never_marked = AgentUptakeSystem.for_agent("sevoflurane")
    never_marked.set_fresh_gas_flow(FreshGasFlow(10.0))
    never_marked.set_delivered_concentration_percent(Percent(8.0))
    never_marked.set_alveolar_ventilation(AlveolarVentilation(0.0))
    for _ in range(120 // SIMULATION_STEP_S):
        never_marked.advance()
    never_marked.set_alveolar_ventilation(AlveolarVentilation(12.0))
    never_marked.advance()

    mac_fraction = float(fraction_from_percent(halted.agent_mac_percent))
    assert halted.elapsed_s == 121
    assert before < mark <= float(halted.alveolar_partial_pressure_fraction) / mac_fraction
    # The arithmetic is the same on both sides, so the comparison is exact.
    unmarked_reading = never_marked.alveoli.partial_pressure_fraction
    assert halted.alveolar_partial_pressure_fraction == unmarked_reading
    # The unmarked system reads 0.3209 ×MAC of sevoflurane's 1.80% at 121 s,
    # which a two-decimal readout shows as 0.32 (measured 2026-11-22).
    assert round(unmarked_reading / mac_fraction, 2) == 0.32
    assert format_mac_multiple(
        halted.alveolar_partial_pressure_fraction, halted.agent_mac_percent
    ) == (f"0.32{MAC_UNIT_SUFFIX}")


def test_a_branch_opens_carrying_the_marks_of_the_case_it_continues() -> None:
    # Marks behave the opposite way to the control timeline, for the opposite
    # reason. The timeline records what was done to a run, and a mark is a
    # question about what is still to come. A comparison is two managements
    # answering one question. A learner made to re-enter the marks could
    # compare two branches at two different heights, with nothing to show it.
    trunk = _trunk_with_two_changes()
    target = MacTarget(RecordedQuantity.MUSCLE, MacMultiple(0.3))
    trunk.add_time_bookmark(TimeBookmark(CaseInstant(45), "the decision point"))
    trunk.add_mac_target(target)

    branch = trunk.resumed_at(trunk.run_segments[-1].opened_at_s)
    marks = branch.snapshot().bookmarks

    assert marks.time_bookmarks == (TimeBookmark(CaseInstant(45), "the decision point"),)
    assert marks.mac_targets == (target,)
    # The trunk's earlier changes do not carry over, because a branch inherits
    # the marks but not the timeline. The branch's timeline holds only the
    # change at the fork that the branch runs under (`PL-ZR49`).
    fork_s = trunk.run_segments[-1].opened_at_s
    timeline = branch.snapshot().control_timeline
    assert [change.elapsed_s for change in timeline] == [fork_s]


def test_marking_a_branch_does_not_mark_the_trunk_it_came_from() -> None:
    # Marks are inherited at the fork and not shared afterwards. The two runs
    # are two managements, and a mark added to one is a question asked of that
    # one.
    trunk = _trunk_with_two_changes()
    branch = trunk.resumed_at(trunk.run_segments[-1].opened_at_s)
    branch.add_time_bookmark(TimeBookmark(CaseInstant(600)))

    assert trunk.snapshot().bookmarks.is_empty
    assert len(branch.snapshot().bookmarks.time_bookmarks) == 1


def test_a_mark_changes_nothing_the_run_computes() -> None:
    # This property is what lets a mark be carried across a fork at all.
    # `PL-B8MK` measured the alternative against it. Recording a keyframe where
    # a run halts changes the trunk's own later results. Keeping a mark in a
    # collection beside the run changes nothing. The comparison is element-wise
    # rather than within a tolerance, because that is the claim.
    #
    # The test still applies unchanged after `PL-CTD7`, and the claim is now
    # stronger. The marked run below is *stopped twice* on the way: at 45 s,
    # and where the alveolar compartment crosses 0.8 ×MAC. It still computes
    # the same trajectory element-wise. A halt costs the run no simulated time
    # and changes no state. It only declines to take the next step until asked.
    marked = SimulationController()
    marked.add_time_bookmark(TimeBookmark(CaseInstant(45)))
    marked.add_mac_target(MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.8)))
    unmarked = SimulationController()

    for controller in (marked, unmarked):
        _run_with_two_changes(controller)
        controller.pause()

    assert marked.snapshot().elapsed_s == unmarked.snapshot().elapsed_s

    for quantity in COMPARTMENT_QUANTITIES:
        position = COMPARTMENT_STATE_INDEX[quantity]
        window = marked.drawn_window(0.0, marked.snapshot().elapsed_s, 50)
        same = unmarked.drawn_window(0.0, unmarked.snapshot().elapsed_s, 50)

        assert [state[position] for state in window.states] == [
            state[position] for state in same.states
        ]


def _the_same_case_never_marked(steps: int) -> SimulationController:
    """`_trunk_halted_on_a_bookmark`'s case without the mark, run the same distance.

    The run takes the number of steps that the marked run has completed, so
    both runs stand at the same instant.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=30)
    controller.set_delivered_concentration_percent(Percent(4.0))

    for _ in range(steps - controller._state.step_count):
        controller.advance()

    return controller


def test_a_branch_taken_at_a_bookmark_reproduces_its_parent_without_changing_it() -> None:
    """`PL-B8MK`'s deliverable, and both halves of it.

    A design this project refused could satisfy either half alone. Recording a
    keyframe where the run halts makes the branch exact against the trunk it
    forked from. But it also changes that trunk's own later results: 48 of 54
    elements differed from the same case built unmarked, so marking a run
    would change it. Doing nothing at all leaves the trunk untouched but
    refuses the fork. So the two halves are asserted together. The branch
    reproduces its parent element-wise from the fork onwards, *and* the trunk
    is, element for element, the case it would have been if nobody had marked
    it.
    """

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    fork_steps = marked._state.step_count

    # The premise: the trunk has no keyframe at the fork instant, so the
    # refused route would have had to record one there.
    assert fork_s not in [segment.opened_at_s for segment in marked.run_segments]

    branch = marked.resumed_here()

    marked.start()
    _advance_for(marked, duration_s=30)
    marked.pause()

    branch.start()
    _advance_for(branch, duration_s=30)
    branch.pause()

    unmarked = _the_same_case_never_marked(steps=marked._state.step_count)
    unmarked.pause()

    # The trunk is the case it would have been without the mark: the same
    # keyframes, at the same instants, with the same states. A keyframe
    # recorded where the run halted would show up here as a third opening
    # that the unmarked run does not have.
    assert marked._state.step_count == unmarked._state.step_count
    assert marked.snapshot().elapsed_s == unmarked.snapshot().elapsed_s
    assert [segment.opened_at_s for segment in marked.run_segments] == [
        segment.opened_at_s for segment in unmarked.run_segments
    ]
    assert [
        marked._state.stored_states.state_at(segment.opened_at_s) for segment in marked.run_segments
    ] == [
        unmarked._state.stored_states.state_at(segment.opened_at_s)
        for segment in unmarked.run_segments
    ]

    for steps in range(0, marked._state.step_count + 1):
        case_s = steps * SIMULATION_STEP_S

        assert marked._state.stored_states.state_at(
            CaseInstant(case_s)
        ) == unmarked._state.stored_states.state_at(CaseInstant(case_s)), (
            f"marking the run moved what it says at {case_s} s"
        )

    # And the branch reproduces the parent it forked from, element for element,
    # at every instant the two share.
    for steps_past_fork in range(0, 31):
        case_s = (fork_steps + steps_past_fork) * SIMULATION_STEP_S

        assert branch._state.stored_states.state_at(
            CaseInstant(case_s)
        ) == marked._state.stored_states.state_at(CaseInstant(case_s)), (
            f"the branch and its parent differ at {case_s} s"
        )


def test_a_bookmark_fork_opens_its_definition_at_the_keyframe_before_it() -> None:
    """The route this project chose, stated as the structure it produces.

    The branch's clock and live system are at the bookmark. Its run definition
    opens at the keyframe *at or before* that instant, with that keyframe's
    own state. Every instant after the fork is then one propagation from the
    same keyframe that the trunk propagates from. `docs/INTERFACE.md` § "What this
    requires of a branch" states the rule: a branch's settings record opens
    with the stretch that its parent ran up to the fork.
    """

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s

    branch = marked.resumed_here()

    assert branch.snapshot().elapsed_s == fork_s
    assert branch.opened_from is not None
    assert branch.opened_from.fork.instant_s == fork_s

    # The definition opens earlier, at the trunk's own keyframe rather than at
    # the fork, and nothing was recorded on the trunk to make one there.
    assert branch.run_segments[0].opened_at_s == 30.0
    assert branch.run_segments[0].opened_at_s < fork_s
    assert branch._state.stored_states.state_at(
        branch.run_segments[0].opened_at_s
    ) == marked._state.stored_states.state_at(marked.run_segments[-1].opened_at_s)
    assert [segment.opened_at_s for segment in marked.run_segments] == [0.0, 30.0]


def test_a_branch_taken_at_a_bookmark_is_not_drawn_before_its_fork() -> None:
    """The window is clipped at the fork, not at the definition's opening.

    The definition can return values for the stretch between the keyframe it
    opens at and the fork, because that stretch belongs to the parent. The
    branch did not live through it. Drawing it would show the trunk's
    trajectory under the branch's identity. Those are the right numbers in the
    wrong patient context, and `CLAUDE.md`'s safety-critical standard counts
    that as a failure in its own right.
    """

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    branch = marked.resumed_here()

    # An axis that ends inside the interval that the definition covers, and
    # that the branch never lived through, draws nothing at all.
    assert 30.0 < fork_s - 5.0 < fork_s
    window = branch.drawn_window(0.0, fork_s - 5.0, 150)

    assert window.times_s == ()
    assert window.states == ()

    # An axis reaching the fork draws from the fork, not from the keyframe.
    spanning = branch.drawn_window(0.0, fork_s, 150)

    assert spanning.times_s == (fork_s,)

    # On the same axis, the trunk draws the stretch that the branch does not.
    # The two differ because the branch did not exist yet.
    assert marked.drawn_window(0.0, fork_s - 5.0, 150).times_s != ()


def test_a_bookmark_branch_and_its_parent_agree_at_every_column_they_share() -> None:
    """`PL-Z3W6`: a branch agrees with its parent at every sampled point a learner sees.

    "Every sampled point" has a second meaning, and it is the one the release is
    for: the columns that the chart draws. A learner does not compare two runs at
    whole steps of the solver. They compare them at the vertices of two overlaid
    traces. A divergence before the fork would make it impossible to attribute a
    difference after the fork to the one setting that was changed.

    Two things are asserted:

    - **The branch draws no column that the trunk does not draw.** This axis has a
      column at every whole second, and the mark is a whole second. So the fork is a
      column on both runs, and it is the left end of the branch's clipped range. On
      an axis whose columns are further apart, the fork can be the one column that
      the branch adds, which
      `test_a_bookmark_branch_draws_one_column_its_parent_does_not_and_it_is_the_fork`
      covers.
    - **The drawn compartment values agree bit for bit at every column they share.**
      Each run draws the states it stored. The branch's first stored state is the
      one its parent stored for the fork, and with no setting changed each later
      step repeats its parent's (`PL-MH9J`). So a reader who subtracts one drawn
      trace from the other sees zero. Before `PL-MH9J` the chart computed each
      column by formula, and 183 of the 279 drawn elements at these columns
      differed in their last bits (measured 2026-11-21).
    """

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    branch = marked.resumed_here()

    marked.start()
    _advance_for(marked, duration_s=30)
    marked.pause()

    branch.start()
    _advance_for(branch, duration_s=30)
    branch.pause()

    span_s = marked.snapshot().elapsed_s
    trunk_window = marked.drawn_window(0.0, span_s, 601)
    branch_window = branch.drawn_window(0.0, span_s, 601)
    shared = sorted(set(trunk_window.times_s) & set(branch_window.times_s))

    assert set(branch_window.times_s) <= set(trunk_window.times_s)
    assert branch_window.times_s[0] == fork_s
    # The fork is at 45 s and both runs reach 75 s. The columns are one second
    # apart, so the two runs share the 31 columns from 45 s to 75 s.
    assert len(shared) == 31

    trunk_drawn = dict(zip(trunk_window.times_s, trunk_window.states, strict=True))
    branch_drawn = dict(zip(branch_window.times_s, branch_window.states, strict=True))

    elements = 0

    for elapsed_s in shared:
        for position in COMPARTMENT_STATE_INDEX.values():
            elements += 1

            assert trunk_drawn[elapsed_s][position] == branch_drawn[elapsed_s][position], (
                f"the two drawn columns at {elapsed_s} s differ"
            )

    assert elements == 31 * len(COMPARTMENT_QUANTITIES)


def test_a_paused_trunk_branches_where_it_stands() -> None:
    """`PL-Y2SL`'s deliverable: paused anywhere, the learner can branch right there.

    The trunk is paused at 120 s, which is neither a keyframe nor a mark.
    Before this item, no fork method reached such an instant, so a learner had
    to mark it first. The branch uses the bookmark fork's construction, with
    the clock giving the fork instant. The branch starts at the clock, and its
    definition opens at the keyframe where the trunk's current stretch opens.
    It reproduces the trunk element-wise from the fork on, and the trunk stays
    the case it was. The method takes no instant, so there is no instant to
    get wrong.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.snapshot().elapsed_s
    fork_steps = trunk._state.step_count
    keyframes = [
        (segment.opened_at_s, trunk._state.stored_states.state_at(segment.opened_at_s))
        for segment in trunk.run_segments
    ]

    # The premise: nothing is recorded where the trunk is paused.
    assert fork_s not in [instant_s for instant_s, _ in keyframes]
    assert trunk.snapshot().bookmark_halt is None
    assert trunk.here_fork_point == HereForkPoint(fork_s, stopped_on_mark=False)

    branch = trunk.resumed_here()

    assert branch.began_at_s == branch.snapshot().elapsed_s == fork_s
    assert branch._state.step_count == fork_steps
    assert branch.opened_from is not None
    assert branch.opened_from.fork.state == trunk._state.stored_states.state_at(fork_s)
    assert branch.snapshot().bookmark_halt is None
    assert branch.run_segments[0].opened_at_s == trunk.run_segments[-1].opened_at_s
    assert [
        (segment.opened_at_s, trunk._state.stored_states.state_at(segment.opened_at_s))
        for segment in trunk.run_segments
    ] == keyframes

    trunk.start()
    _advance_for(trunk, duration_s=30)
    trunk.pause()

    branch.start()
    _advance_for(branch, duration_s=30)
    branch.pause()

    for steps_past_fork in range(0, 31):
        case_s = (fork_steps + steps_past_fork) * SIMULATION_STEP_S

        assert branch._state.stored_states.state_at(
            CaseInstant(case_s)
        ) == trunk._state.stored_states.state_at(CaseInstant(case_s)), (
            f"the branch and the trunk it was paused at differ at {case_s} s"
        )


def test_resuming_past_a_bookmark_turns_its_fork_into_the_paused_point() -> None:
    """A step uses up the halt, nothing is offered while the run goes, and a pause offers again.

    A running run's position moves with each step, so an instant read from it
    is gone before it can be taken. The fork method refuses it rather than
    fork a step or a tick later than the label said. Once paused again, the
    run offers the place where it then is, which is no longer on the mark.
    """

    marked = _trunk_halted_on_a_bookmark()
    halted_s = marked.snapshot().elapsed_s

    assert marked.here_fork_point == HereForkPoint(halted_s, stopped_on_mark=True)

    marked.start()
    marked.advance()

    assert marked.here_fork_point is None

    with pytest.raises(SimulationConfigurationError, match="is going"):
        marked.resumed_here()

    marked.pause()
    paused_s = marked.snapshot().elapsed_s

    assert paused_s > halted_s
    assert marked.here_fork_point == HereForkPoint(paused_s, stopped_on_mark=False)
    assert marked.resumed_here().began_at_s == paused_s


def test_a_failed_run_offers_no_place_to_branch_where_it_stands() -> None:
    """A failure is not a pause, so a failed run's position is neither offered nor taken.

    `RunStatus.failure_reason` keeps a failure from being presented as a
    pause. A branch there would resume a run that `fail` says is not resumed.
    The run can still be branched at the keyframes it passed before the
    failure, as the refusal says.
    """

    trunk = _trunk_with_two_changes()
    trunk.fail("a step raised")

    assert trunk.here_fork_point is None

    with pytest.raises(SimulationConfigurationError, match="not a pause") as refusal:
        trunk.resumed_here()

    assert "a step raised" in str(refusal.value)
    assert "resumed_at" in str(refusal.value)
    assert trunk.resumed_at(trunk.run_segments[-1].opened_at_s).began_at_s == (
        trunk.run_segments[-1].opened_at_s
    )


def test_a_run_at_its_opening_offers_no_place_to_branch_where_it_stands() -> None:
    """Nothing is recorded at the opening, and `resumed_at` already opens a branch there."""

    trunk = SimulationController()

    assert trunk.here_fork_point is None

    with pytest.raises(SimulationConfigurationError, match="opening"):
        trunk.resumed_here()

    assert trunk.resumed_at(CaseInstant(0)).began_at_s == 0.0


def test_a_mark_added_on_the_halting_step_reads_passed_on_the_branch() -> None:
    """A mark the halting step crossed shows as passed on the branch, however late (`PL-2N43`).

    A 0.3 ×MAC alveolar target halts the run at the end of the step that
    crosses it. A time mark added at that instant while the run is stopped
    there was crossed by that same step. The halt's record names only what
    was marked when the run stopped. So a branch started from that record
    would open with no record of the time mark. When the step's crossing is
    computed from the current marks, it names both, and the trunk, the branch
    and `resumed_at_mark` agree.
    """

    trunk = SimulationController()
    trunk.add_mac_target(MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.3)))
    trunk.start()
    _advance_until_halted(trunk, limit_s=400)
    halted_s = trunk.snapshot().elapsed_s
    added = TimeBookmark(CaseInstant(halted_s), "added while standing")
    trunk.add_time_bookmark(added)

    branch = trunk.resumed_here()

    assert branch.began_at_s == halted_s
    assert branch.snapshot().bookmark_standings.of_time_bookmark(added) is MarkStanding.PASSED
    assert trunk.snapshot().bookmark_standings.of_time_bookmark(added) is MarkStanding.PASSED
    assert trunk.resumed_at_mark(added).opened_from == branch.opened_from


def test_a_branch_at_the_second_a_halted_run_stands_on_is_the_branch_taken_there() -> None:
    """`resumed_at` and `resumed_here` open one branch where the run is halted (`PL-FST0`).

    Until `PL-FST0`, `resumed_at` opened only at the run's start or at a
    setting change, and it refused the second of a halt. The run stores a
    state for every second, so naming the second now gives the branch that
    `resumed_here` gives: the same provenance and the same snapshot.
    """

    marked = _trunk_halted_on_a_bookmark()
    halted_s = marked.snapshot().elapsed_s

    assert halted_s not in [segment.opened_at_s for segment in marked.run_segments]

    named = marked.resumed_at(halted_s)
    here = marked.resumed_here()

    assert named.opened_from == here.opened_from
    assert named.began_at_s == halted_s
    assert named.snapshot() == here.snapshot()


def test_resetting_a_branch_taken_at_a_bookmark_returns_it_to_the_bookmark() -> None:
    """A branch's beginning is its fork, and a bookmark fork is no exception."""

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    fork_state = marked._state.stored_states.state_at(CaseInstant(fork_s))
    branch = marked.resumed_here()

    branch.start()
    _advance_for(branch, duration_s=10)
    branch.reset()

    assert branch.snapshot().elapsed_s == fork_s
    assert branch._state.stored_states.state_at(CaseInstant(fork_s)) == fork_state


def test_a_branch_reset_under_new_settings_is_drawn_from_where_it_stands() -> None:
    """`reset()` preserves settings, and the definition has to follow.

    A branch reset after its learner has dialled something new is at the fork
    state under the new settings. A definition still opening at the parent's
    earlier keyframe would propagate that keyframe forward under settings the
    parent never used. It would draw the branch from a state the branch is not
    in. The readouts would then say one thing and the trace another, about one
    run.
    """

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    fork_state = marked._state.stored_states.state_at(CaseInstant(fork_s))
    branch = marked.resumed_here()

    branch.set_delivered_concentration_percent(Percent(6.0))
    branch.reset()

    assert branch.snapshot().elapsed_s == fork_s
    assert branch._state.stored_states.state_at(CaseInstant(fork_s)) == fork_state


def test_a_branch_of_a_bookmark_fork_is_refused_rather_than_silently_flattened() -> None:
    """The flat shape applies to every branch, whichever fork method made it."""

    marked = _trunk_halted_on_a_bookmark()
    branch = marked.resumed_here()
    branch.add_time_bookmark(TimeBookmark(CaseInstant(600)))

    with pytest.raises(SimulationConfigurationError, match="branch of a branch"):
        branch.resumed_at(branch.run_segments[0].opened_at_s)


def test_a_case_forks_at_the_bookmark_its_trunk_is_standing_on() -> None:
    """The case-level fork method keeps the branch rather than returning it detached."""

    marked = _trunk_halted_on_a_bookmark()
    fork_s = marked.snapshot().elapsed_s
    case = BranchedCase(marked)

    branch = case.fork_here()

    assert case.branches == (branch,)
    assert case.runs == (marked, branch)
    assert branch.opened_from is not None
    assert branch.opened_from.fork.instant_s == fork_s
    # The trunk stays where it was, still stopped at its halt.
    assert marked.snapshot().elapsed_s == fork_s
    assert marked.snapshot().bookmark_halt is not None


def test_a_mark_between_a_bookmark_branch_s_definition_and_its_fork_is_unreachable() -> None:
    """The standings are taken from where the branch *began*, not where its definition opens.

    A bookmark branch's definition opens at the keyframe at or before the
    fork, and the stretch between them belongs to the parent. A mark in that
    stretch can never be reached going forward, so the row must say so. Until
    `PL-B8MK`, the definition's own opening was the same number as the fork
    for every branch. Using it here instead would tell a learner to wait for
    something that no step can reach.
    """

    marked = SimulationController()
    marked.add_time_bookmark(TimeBookmark(CaseInstant(40), "passed on the way"))
    marked.add_time_bookmark(TimeBookmark(CaseInstant(45), "the decision point"))
    marked.start()
    _advance_until_halted(marked, limit_s=60)
    marked.start()
    _advance_until_halted(marked, limit_s=60)

    fork_s = marked.snapshot().elapsed_s
    branch = marked.resumed_here()

    # The premise: the definition reaches back past the mark, and the branch
    # does not.
    assert branch.run_segments[0].opened_at_s < 40.0 < fork_s
    assert branch.began_at_s == fork_s

    standings = branch.snapshot().bookmark_standings

    assert standings.of_time_bookmark(TimeBookmark(CaseInstant(40), "passed on the way")) is (
        MarkStanding.BEFORE_THIS_BRANCH
    )
