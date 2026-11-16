"""The simulation controller, driven against real runs.

These tests cover edits made at a paused instant (`PL-ZR49`).

`controller_support.py` holds what several of these files share.
"""

import dataclasses

from anesthesia_sim.app.bookmarks import BookmarkCrossing, MacTarget, MarkStanding, TimeBookmark
from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.control_timeline import group_adjustments
from anesthesia_sim.app.controller import BranchedCase, HereForkPoint, SimulationController
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.core.concentration import MacMultiple, Percent
from anesthesia_sim.core.governing_equations import UptakeEquationSettings
from anesthesia_sim.core.simulation_step import MAXIMUM_SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import (
    AlveolarVentilation,
    CardiacOutput,
    CaseInstant,
    FreshGasFlow,
)
from tests.integration.controller.controller_support import (
    _advance_for,
    _advance_until_halted,
    _described,
    _states_agree_after_the_fork,
)


def _replayed_from_provenance(branch: SimulationController) -> UptakeEquationSettings:
    """Return the settings a branch runs under, as its provenance and control timeline state them.

    This helper applies each recorded change to the stretch the branch opened
    from, by hand, so the result does not come from the controller's own
    reading of either record.
    """

    fields_of_controls = {
        ControlInput.FRESH_GAS_FLOW: ("fresh_gas_flow_l_min", FreshGasFlow),
        ControlInput.DELIVERED: ("delivered_concentration_percent", Percent),
        ControlInput.ALVEOLAR_VENTILATION: ("alveolar_ventilation_l_min", AlveolarVentilation),
        ControlInput.CARDIAC_OUTPUT: ("cardiac_output_l_min", CardiacOutput),
    }
    assert branch.opened_from is not None
    settings = branch.opened_from.segment.settings

    for change in branch.snapshot().control_timeline:
        name, checked = fields_of_controls[change.control]
        settings = dataclasses.replace(settings, **{name: checked(change.new_value)})

    return settings


def test_every_door_at_a_paused_instant_agrees_after_an_edit_made_there() -> None:
    """Every way of branching at one instant uses the same two stretches (`PL-ZR49`).

    The trunk runs at 2% and a mark at 30 s halts it. While the trunk is
    halted there, the learner turns the vaporizer to 4%, removes the mark and
    adds it back under another label, and marks an instant inside the halting
    step. Before those edits, branches are taken where the trunk is halted and
    at the mark. Only those two ways are used, since no keyframe exists at
    30 s yet. After the edits, all three ways of branching are used. Once the
    trunk has run on past 30 s, branches are taken at the mark and at the
    keyframe again. Each branch is then reset.

    Each branch is checked against the rule that `docs/MODEL.md` states. All
    of them share one provenance, the stretch that the halting step ran
    under. Each runs under what the dial showed when it was taken. So a
    branch taken before the edits runs under 2%. Every branch taken after
    them runs under 4% and records the change at the fork in its own timeline
    (project owner, 2026-10-26). In its halt record, every branch taken after
    the edits names the marks as they now are, as the trunk does while it is
    halted there. A reset reopens each branch with the same provenance,
    timeline, settings and halt record. The expected settings are the literal
    values that the test dialled. The expected marks are the instants and
    labels that the test gave them. The run that each branch describes is
    checked against a run built directly. That run is either a 2% case that
    nobody changed or the trunk.
    """

    first = TimeBookmark(CaseInstant(30.0), "first")
    relabelled = TimeBookmark(CaseInstant(30.0), "relabelled")
    trunk = SimulationController(delivered_concentration_percent=Percent(2.0))
    trunk.add_time_bookmark(first)
    trunk.start()
    _advance_until_halted(trunk, limit_s=31.0)
    fork_s = trunk.snapshot().elapsed_s
    inside_s = fork_s - MAXIMUM_SIMULATION_STEP_S / 2
    inside = TimeBookmark(CaseInstant(inside_s), "inside the step")

    branches = {
        "here, before the edits": trunk.resumed_here(),
        "at the mark, before the edits": trunk.resumed_at_mark(first),
    }

    trunk.set_delivered_concentration_percent(Percent(4.0))
    trunk.remove_time_bookmark(first)
    trunk.add_time_bookmark(relabelled)
    trunk.add_time_bookmark(inside)

    branches |= {
        "here, after the edits": trunk.resumed_here(),
        "at the mark, after the edits": trunk.resumed_at_mark(relabelled),
        "at the keyframe, after the edits": trunk.resumed_at(fork_s),
    }
    halt_on_the_trunk = trunk.snapshot().bookmark_halt
    here_on_the_trunk = trunk.here_fork_point

    trunk.start()
    _advance_for(trunk, duration_s=10.0)
    trunk.pause()

    branches |= {
        "at the mark, after running on": trunk.resumed_at_mark(relabelled),
        "at the keyframe, after running on": trunk.resumed_at(fork_s),
    }

    def runs_under_the_change(name: str) -> bool:
        return not name.endswith("before the edits")

    def named(crossing: BookmarkCrossing | None) -> set[tuple[float, str | None]]:
        assert crossing is not None
        assert crossing.instant_s == fork_s

        return {(mark.instant_s, mark.label) for mark in crossing.time_bookmarks}

    # One provenance: the stretch the halting step ran under, which opens at 0 s.
    provenance = branches["here, before the edits"].opened_from
    assert provenance is not None
    assert provenance.segment == trunk.run_segments[0]
    assert provenance.fork.instant_s == fork_s

    for name, branch in branches.items():
        assert branch.opened_from == provenance, name

    # Settings: every door taken after the change runs under it, and its own record says so.
    for name, branch in branches.items():
        snapshot = branch.snapshot()

        if runs_under_the_change(name):
            assert snapshot.delivered_concentration_percent == 4.0, name
            assert _described(snapshot.control_timeline) == [
                (fork_s, ControlInput.DELIVERED, 2.0, 4.0)
            ], name
        else:
            assert snapshot.delivered_concentration_percent == 2.0, name
            assert snapshot.control_timeline == (), name

        assert _replayed_from_provenance(branch) == branch.run_segments[-1].settings, name

    # The trunk standing there, and every branch taken after the edits, name
    # the marks as they now are. A branch taken before the edits holds the
    # marks that the trunk held when the branch was taken.
    now_marked = {(30.0, "relabelled"), (inside_s, "inside the step")}
    assert named(halt_on_the_trunk) == now_marked
    assert here_on_the_trunk == HereForkPoint(fork_s, stopped_on_mark=True)

    for name, branch in branches.items():
        snapshot = branch.snapshot()

        if name.endswith("before the edits"):
            assert named(snapshot.bookmark_halt) == {(30.0, "first")}, name
            continue

        assert named(snapshot.bookmark_halt) == now_marked, name
        assert snapshot.bookmark_standings.of_time_bookmark(inside) is MarkStanding.PASSED, name

    # A branch's reset reopens it on the same record.
    for name, branch in branches.items():
        before_reset = branch.snapshot()
        branch.reset()
        after_reset = branch.snapshot()

        assert branch.opened_from == provenance, name
        assert after_reset.control_timeline == before_reset.control_timeline, name
        assert after_reset.delivered_concentration_percent == (
            before_reset.delivered_concentration_percent
        ), name
        assert after_reset.bookmark_halt == before_reset.bookmark_halt, name

    # And the record is the run: a 2% branch is the case nobody changed, and
    # the 4% branch is the trunk, element for element.
    never_changed = SimulationController(delivered_concentration_percent=Percent(2.0))
    never_changed.start()
    _advance_for(never_changed, duration_s=40.0)

    for name, branch in branches.items():
        branch.start()
        _advance_for(branch, duration_s=10.0)
        _states_agree_after_the_fork(
            branch, trunk if runs_under_the_change(name) else never_changed, fork_s, steps=100
        )


def test_a_change_made_on_the_halt_opens_every_branch_taken_after_it() -> None:
    """`PL-HSP8`: a branch taken on a halt runs under what the dial says when it is taken.

    The trunk runs at 2% and a mark at 60 s halts it. The vaporizer is turned
    off while the trunk stands there, and the trunk then runs on to 120 s.
    There the vaporizer is turned to 1%, a change made after the halt. The
    halt branch is taken both before and after the change made on the halt.
    Once the trunk has run on and made its later change, a branch is taken
    at the mark, and another with `resumed_at` at the keyframe that the
    change on the halt recorded.

    The halt branch taken before the change runs at 2%. The other three run
    at 0%, the setting the trunk left the halt under, and none takes the
    later 1%. Each of the three records the change at the fork in its own
    timeline. All four name the same provenance, the stretch that the
    halting step ran under (project owner, 2026-10-26). The expected
    settings are the literal values that the test dialled. The 2% branch is
    checked against a 2% run nobody changed. Each 0% branch is checked
    against the trunk, which is the case run directly with the change made
    on the halt.
    """

    mark = TimeBookmark(CaseInstant(60.0), "on your mark")
    trunk = SimulationController(delivered_concentration_percent=Percent(2.0))
    trunk.add_time_bookmark(mark)
    trunk.start()
    _advance_until_halted(trunk, limit_s=61.0)
    halt_s = trunk.snapshot().elapsed_s

    before_the_change = trunk.resumed_here()
    trunk.set_delivered_concentration_percent(Percent(0.0))
    after_the_change = {"here, after the change": trunk.resumed_here()}
    trunk.start()
    _advance_for(trunk, duration_s=60.0)
    trunk.pause()
    trunk.set_delivered_concentration_percent(Percent(1.0))
    after_the_change |= {
        "at the mark, later": trunk.resumed_at_mark(mark),
        "at the keyframe, later": trunk.resumed_at(halt_s),
    }

    assert before_the_change.snapshot().delivered_concentration_percent == 2.0
    assert before_the_change.snapshot().control_timeline == ()

    for name, branch in after_the_change.items():
        assert branch.opened_from == before_the_change.opened_from, name
        assert branch.snapshot().delivered_concentration_percent == 0.0, name
        assert _described(branch.snapshot().control_timeline) == [
            (halt_s, ControlInput.DELIVERED, 2.0, 0.0)
        ], name

    never_changed = SimulationController(delivered_concentration_percent=Percent(2.0))
    never_changed.start()
    _advance_for(never_changed, duration_s=70.0)
    before_the_change.start()
    _advance_for(before_the_change, duration_s=10.0)

    _states_agree_after_the_fork(before_the_change, never_changed, halt_s, steps=100)

    for branch in after_the_change.values():
        branch.start()
        _advance_for(branch, duration_s=10.0)

        _states_agree_after_the_fork(branch, trunk, halt_s, steps=100)


def test_a_trunk_change_at_a_forked_instant_keeps_the_branch_provenance_in_the_trunk() -> None:
    """`PL-NRR6`: setting the dial back where a branch was taken keeps its provenance in the trunk.

    The trunk is paused at 30 s at 2% and set to 4%. A branch is taken at the
    keyframe that change recorded, and the trunk is then set back to 2%. That
    removes the trunk's keyframe at 30 s, because nothing about the trunk
    changed there. The branch's provenance is the stretch that the step
    reaching 30 s ran under, which is still the trunk's. The branch's own
    timeline records the 4% it runs under. The instant stays a place to
    branch for as long as the trunk stands there, and a branch taken there
    now names the same provenance.
    """

    trunk = SimulationController(delivered_concentration_percent=Percent(2.0))
    trunk.start()
    _advance_for(trunk, duration_s=30.0)
    trunk.pause()
    fork_s = trunk.snapshot().elapsed_s
    trunk.set_delivered_concentration_percent(Percent(4.0))
    branch = trunk.resumed_at(fork_s)
    trunk.set_delivered_concentration_percent(Percent(2.0))

    assert branch.opened_from is not None
    assert branch.opened_from.segment in trunk.run_segments
    assert [segment.opening.instant_s for segment in trunk.run_segments] == [0.0]
    assert branch.snapshot().delivered_concentration_percent == 4.0
    assert _described(branch.snapshot().control_timeline) == [
        (fork_s, ControlInput.DELIVERED, 2.0, 4.0)
    ]
    assert trunk.here_fork_point == HereForkPoint(fork_s, stopped_on_mark=False)
    assert trunk.resumed_here().opened_from == branch.opened_from


def test_a_branch_reset_after_a_setting_change_keeps_its_record_and_provenance_in_agreement() -> (
    None
):
    """`PL-K5BS`: a reset branch runs under settings that its record and its provenance both state.

    The trunk changes the fresh gas flow from 4 to 6 L/min at 30 s, and a
    branch is taken at that keyframe. The learner runs the branch for 10 s,
    sets 8 L/min and resets. The reset keeps 8 L/min, as a reset keeps
    settings. The timeline keeps the trunk's change that the branch opened
    with, and records the 8 L/min after it as a change at the fork.
    Replaying the branch's timeline over the stretch it opened from gives
    the settings it runs under. The reset branch is checked against a branch
    taken directly at the keyframe and set to 8 L/min there.
    """

    trunk = SimulationController(fresh_gas_flow_l_min=FreshGasFlow(4.0))
    trunk.start()
    _advance_for(trunk, duration_s=30.0)
    trunk.pause()
    fork_s = trunk.snapshot().elapsed_s
    trunk.set_fresh_gas_flow(FreshGasFlow(6.0))

    branch = trunk.resumed_at(fork_s)
    branch.start()
    _advance_for(branch, duration_s=10.0)
    branch.pause()
    branch.set_fresh_gas_flow(FreshGasFlow(8.0))
    branch.reset()

    built_directly = trunk.resumed_at(fork_s)
    built_directly.set_fresh_gas_flow(FreshGasFlow(8.0))

    snapshot = branch.snapshot()
    assert snapshot.elapsed_s == fork_s
    assert snapshot.fresh_gas_flow_l_min == 8.0
    assert _described(snapshot.control_timeline) == [
        (fork_s, ControlInput.FRESH_GAS_FLOW, 4.0, 6.0),
        (fork_s, ControlInput.FRESH_GAS_FLOW, 6.0, 8.0),
    ]
    assert _described(snapshot.control_timeline) == _described(
        built_directly.snapshot().control_timeline
    )
    assert _replayed_from_provenance(branch) == branch.run_segments[-1].settings
    assert _replayed_from_provenance(branch) == branch._state.uptake_system.equation_settings()

    branch.start()
    _advance_for(branch, duration_s=10.0)
    built_directly.start()
    _advance_for(built_directly, duration_s=10.0)

    _states_agree_after_the_fork(branch, built_directly, fork_s, steps=100)


def test_a_branch_taken_at_a_keyframe_keeps_a_record_of_the_setting_it_opened_under() -> None:
    """`PL-TNYP`: a keyframe branch's own record states its setting, whatever the trunk does next.

    The trunk is paused at 60 s and set from 4 to 6 L/min, a branch is taken
    at that keyframe, and the trunk is set back to 4 L/min. The branch runs at
    6 L/min, and its own control timeline, which its panel lists, says so.
    """

    trunk = SimulationController(fresh_gas_flow_l_min=FreshGasFlow(4.0))
    trunk.start()
    _advance_for(trunk, duration_s=60.0)
    trunk.pause()
    fork_s = trunk.snapshot().elapsed_s
    trunk.set_fresh_gas_flow(FreshGasFlow(6.0))
    branch = BranchedCase(trunk).fork_at(fork_s)
    trunk.set_fresh_gas_flow(FreshGasFlow(4.0))

    snapshot = branch.snapshot()
    assert trunk.snapshot().control_timeline == ()
    assert snapshot.fresh_gas_flow_l_min == 6.0
    assert _described(snapshot.control_timeline) == [
        (fork_s, ControlInput.FRESH_GAS_FLOW, 4.0, 6.0)
    ]
    assert _replayed_from_provenance(branch) == branch._state.uptake_system.equation_settings()


def test_the_halt_record_follows_the_current_marks_after_a_mark_is_removed_and_added_back() -> None:
    """`PL-XV0D`: the halt record names the marks as they are, on the trunk and after a reset.

    A mark labelled "original" halts the trunk at 30 s, and a branch is taken
    there. On both runs the mark is removed, which leaves no halt to report,
    and a mark at the same instant labelled "again" is added. The branch is
    then reset. Both runs report the halt on "again", and the trunk still
    offers a branch on its mark.
    """

    original = TimeBookmark(CaseInstant(30.0), "original")
    again = TimeBookmark(CaseInstant(30.0), "again")
    trunk = SimulationController()
    trunk.add_time_bookmark(original)
    trunk.start()
    _advance_until_halted(trunk, limit_s=31.0)
    halt_s = trunk.snapshot().elapsed_s
    branch = trunk.resumed_here()

    for run in (trunk, branch):
        run.remove_time_bookmark(original)

        assert run.snapshot().bookmark_halt is None

        run.add_time_bookmark(again)

    branch.reset()

    for run in (trunk, branch):
        assert run.snapshot().bookmark_halt == BookmarkCrossing(halt_s, (again,))

    assert trunk.here_fork_point == HereForkPoint(halt_s, stopped_on_mark=True)


def test_a_branch_at_the_case_s_opening_keeps_the_settings_it_opened_under() -> None:
    """A branch at the case's opening has the opening stretch as provenance and runs under it.

    No step has run yet at the case's opening. A trunk edit at the opening
    still replaces the opening stretch, even after a branch was taken there,
    as it did before `PL-ZR49`. The branch's provenance is the opening
    keyframe together with the settings that the branch ran under from there.
    No setting produced the opening keyframe's state. Both parts of the
    provenance still describe the branch after the trunk's edit, so the
    provenance still states what the branch runs under. The branch's timeline
    keeps the change that the trunk made before Start, so the branch's own
    panel shows the setting too.
    """

    trunk = SimulationController(delivered_concentration_percent=Percent(2.0))
    trunk.set_delivered_concentration_percent(Percent(4.0))
    branch = trunk.resumed_at(CaseInstant(0.0))
    trunk.set_delivered_concentration_percent(Percent(2.0))

    assert branch.opened_from is not None
    assert branch.opened_from.fork == trunk.run_segments[0].opening
    assert branch.opened_from.segment.settings.delivered_concentration_percent == 4.0
    assert branch.snapshot().delivered_concentration_percent == 4.0
    assert _described(branch.snapshot().control_timeline) == [
        (0.0, ControlInput.DELIVERED, 2.0, 4.0)
    ]
    assert trunk.snapshot().control_timeline == ()


def test_a_branch_at_the_case_s_opening_states_the_trunk_s_changes_made_before_start() -> None:
    """A branch taken at 0 s opens with the trunk's changes made before Start.

    The trunk is created at 2% delivered, set to 3% before Start, and a
    branch is taken at 0 s. The trunk is then set to 4%. The branch runs at
    3%, exactly as a case created at 3% does. Its timeline holds the change
    from 2% to 3% at 0 s, while the trunk's holds the change from 2% to 4%.
    The second blind review pass of the rework found the branch's timeline
    empty. A learner who read the trunk's "0s: 2% → 4%" beside an empty
    panel would take the branch to be at 2%.

    The copied entry is where the branch began. So the new branch holds
    nothing that a trunk Reset would lose, and the learner's first change on
    it is an adjustment of its own.
    """

    trunk = SimulationController(delivered_concentration_percent=Percent(2.0))
    trunk.set_delivered_concentration_percent(Percent(3.0))
    branch = trunk.resumed_at(CaseInstant(0.0))
    trunk.set_delivered_concentration_percent(Percent(4.0))
    created_at_three = SimulationController(delivered_concentration_percent=Percent(3.0))

    assert branch.snapshot().delivered_concentration_percent == 3.0
    assert branch.run_segments == created_at_three.run_segments
    assert _described(branch.snapshot().control_timeline) == [
        (0.0, ControlInput.DELIVERED, 2.0, 3.0)
    ]
    assert _described(trunk.snapshot().control_timeline) == [
        (0.0, ControlInput.DELIVERED, 2.0, 4.0)
    ]
    assert branch.snapshot().changes_since_opening == ()
    assert not branch.snapshot().has_recorded_run

    branch.set_delivered_concentration_percent(Percent(2.0))

    assert [
        (adjustment.from_value, adjustment.to_value)
        for adjustment in group_adjustments(branch.snapshot().control_timeline)
    ] == [(2.0, 3.0), (3.0, 2.0)]
    assert branch.snapshot().has_recorded_run


def test_a_dial_set_back_at_the_fork_is_work_a_trunk_reset_would_lose() -> None:
    """A branch that the learner sets back to the trunk's earlier value holds the learner's change.

    The trunk is paused at 60 s, its fresh gas flow is set from 4 to 6 L/min,
    and a branch is taken at that keyframe. The branch opens at 6 L/min,
    because every branch opens at what the dial says (project owner,
    2026-10-26). Setting the branch to 8 L/min at the fork adds the change
    from 6 to 8 L/min after the opened entry. Setting it to 4 L/min then
    turns that entry into a change from 6 to 4 L/min. The opened entry stays,
    so the "Control changes" panel shows both the trunk's change and the
    learner's. No branch taken at 60 s opens at 4 L/min, so the learner's
    change is work that a trunk Reset would lose. Both blind review passes of
    the rework found that the opened entry was deleted instead. The branch
    then held nothing to lose, and the trunk's Reset discarded it without
    asking.

    The branch's run is exactly the run of a second branch, taken where the
    trunk stands after the trunk is set back to 4 L/min. The second branch
    records nothing, because it opened at 4 L/min.
    """

    trunk = SimulationController(fresh_gas_flow_l_min=FreshGasFlow(4.0))
    trunk.start()
    _advance_for(trunk, duration_s=60.0)
    trunk.pause()
    fork_s = trunk.snapshot().elapsed_s
    trunk.set_fresh_gas_flow(FreshGasFlow(6.0))
    branch = trunk.resumed_at(fork_s)

    assert _described(branch.snapshot().control_timeline) == [
        (fork_s, ControlInput.FRESH_GAS_FLOW, 4.0, 6.0)
    ]
    assert branch.snapshot().changes_since_opening == ()
    assert not branch.snapshot().has_recorded_run

    branch.set_fresh_gas_flow(FreshGasFlow(8.0))

    assert _described(branch.snapshot().control_timeline) == [
        (fork_s, ControlInput.FRESH_GAS_FLOW, 4.0, 6.0),
        (fork_s, ControlInput.FRESH_GAS_FLOW, 6.0, 8.0),
    ]
    assert _described(branch.snapshot().changes_since_opening) == [
        (fork_s, ControlInput.FRESH_GAS_FLOW, 6.0, 8.0)
    ]

    branch.set_fresh_gas_flow(FreshGasFlow(4.0))
    trunk.set_fresh_gas_flow(FreshGasFlow(4.0))
    taken_here = trunk.resumed_here()

    assert branch.snapshot().fresh_gas_flow_l_min == 4.0
    assert _described(branch.snapshot().control_timeline) == [
        (fork_s, ControlInput.FRESH_GAS_FLOW, 4.0, 6.0),
        (fork_s, ControlInput.FRESH_GAS_FLOW, 6.0, 4.0),
    ]
    assert _described(branch.snapshot().changes_since_opening) == [
        (fork_s, ControlInput.FRESH_GAS_FLOW, 6.0, 4.0)
    ]
    assert branch.snapshot().has_recorded_run
    assert len(group_adjustments(branch.snapshot().control_timeline)) == 2
    assert branch.run_segments == taken_here.run_segments
    assert taken_here.snapshot().control_timeline == ()


def test_a_branch_reset_at_the_trunk_s_earlier_value_is_work_a_trunk_reset_would_lose() -> None:
    """A setting kept through a branch reset is compared with the value the branch opened at.

    The trunk is paused at 60 s, its fresh gas flow is set from 4 to 6 L/min,
    and a branch is taken at that keyframe. The learner runs the branch for
    10 s, sets 4 L/min and resets it. The reset keeps 4 L/min. It records the
    setting after the opened entry, as a change from 6 L/min, which is the
    value the branch opened at. Both blind review passes of the rework found
    that the reset recorded the difference from the trunk's earlier value
    instead. That difference was empty, so the trunk's Reset discarded the
    branch without asking.
    """

    trunk = SimulationController(fresh_gas_flow_l_min=FreshGasFlow(4.0))
    trunk.start()
    _advance_for(trunk, duration_s=60.0)
    trunk.pause()
    fork_s = trunk.snapshot().elapsed_s
    trunk.set_fresh_gas_flow(FreshGasFlow(6.0))
    branch = trunk.resumed_at(fork_s)
    branch.start()
    _advance_for(branch, duration_s=10.0)
    branch.pause()
    branch.set_fresh_gas_flow(FreshGasFlow(4.0))
    branch.reset()

    assert branch.snapshot().elapsed_s == fork_s
    assert branch.snapshot().fresh_gas_flow_l_min == 4.0
    assert _described(branch.snapshot().control_timeline) == [
        (fork_s, ControlInput.FRESH_GAS_FLOW, 4.0, 6.0),
        (fork_s, ControlInput.FRESH_GAS_FLOW, 6.0, 4.0),
    ]
    assert _described(branch.snapshot().changes_since_opening) == [
        (fork_s, ControlInput.FRESH_GAS_FLOW, 6.0, 4.0)
    ]
    assert branch.snapshot().has_recorded_run
    assert _replayed_from_provenance(branch) == branch._state.uptake_system.equation_settings()


def test_a_branch_reset_between_a_change_and_its_undoing_holds_what_the_other_order_holds() -> None:
    """ "Change, reset, change back" and "change, change back, reset" give the same result.

    Each branch is taken from the trunk, which is paused at 30 s. On both
    branches, the fresh gas flow goes from 4 to 8 L/min and back, with a reset
    before or after the change back. A reset keeps the settings and records
    them at the fork (`PL-K5BS`). It does not replace the entries that each
    branch first opened with. The two branches end with the same run, the
    same control timeline and the same opened entries. Neither holds anything
    that a trunk Reset would lose.
    """

    trunk = SimulationController(fresh_gas_flow_l_min=FreshGasFlow(4.0))
    trunk.start()
    _advance_for(trunk, duration_s=30.0)
    trunk.pause()

    reset_between = trunk.resumed_here()
    reset_between.set_fresh_gas_flow(FreshGasFlow(8.0))
    reset_between.reset()
    reset_between.set_fresh_gas_flow(FreshGasFlow(4.0))

    reset_last = trunk.resumed_here()
    reset_last.set_fresh_gas_flow(FreshGasFlow(8.0))
    reset_last.set_fresh_gas_flow(FreshGasFlow(4.0))
    reset_last.reset()

    for branch in (reset_between, reset_last):
        assert branch.snapshot().control_timeline == ()
        assert branch.snapshot().opened_with == ()
        assert branch.snapshot().fresh_gas_flow_l_min == 4.0
        assert not branch.snapshot().has_recorded_run

    assert reset_between.run_segments == reset_last.run_segments


def test_a_dial_set_back_and_forward_again_at_the_fork_leaves_nothing_to_lose() -> None:
    """A branch that ends where it opened holds nothing to lose, whatever path its dial took.

    The trunk is paused at 60 s, its fresh gas flow is set from 4 to 6 L/min,
    and two branches are taken at that keyframe. Each opens with the trunk's
    change at the fork. One branch is set to 4 L/min and then to 6 L/min. The
    other is set to 8 L/min and then to 6 L/min. Each detour adds a change
    after the opened entry, and setting 6 L/min removes that change again.
    Both branches then run as a branch freshly taken at that keyframe would.
    An adversarial review of `PL-ZR49`'s change found that an earlier
    version counted the first branch as holding a change.
    """

    trunk = SimulationController(fresh_gas_flow_l_min=FreshGasFlow(4.0))
    trunk.start()
    _advance_for(trunk, duration_s=60.0)
    trunk.pause()
    fork_s = trunk.snapshot().elapsed_s
    trunk.set_fresh_gas_flow(FreshGasFlow(6.0))
    fresh = trunk.resumed_at(fork_s)

    for detour in (4.0, 8.0):
        branch = trunk.resumed_at(fork_s)
        branch.set_fresh_gas_flow(FreshGasFlow(detour))
        branch.set_fresh_gas_flow(FreshGasFlow(6.0))

        assert _described(branch.snapshot().control_timeline) == [
            (fork_s, ControlInput.FRESH_GAS_FLOW, 4.0, 6.0)
        ]
        assert branch.snapshot().changes_since_opening == ()
        assert not branch.snapshot().has_recorded_run
        assert branch.run_segments == fresh.run_segments


def test_a_learner_s_first_change_on_a_branch_is_an_adjustment_of_its_own() -> None:
    """The "Control changes" panel never merges the trunk's change with the learner's.

    The trunk is paused at 60 s and its fresh gas flow set from 4 to 6 L/min,
    and a branch is taken at that keyframe. The branch opens with the trunk's
    change. It runs 10 s, and then its flow is set to 8 L/min through the
    setter alone. The interface marks no adjustment boundary for that change,
    because it marks one only when a drag starts. A change from any other
    input path would arrive in this way. The panel must still show two acts:
    the trunk's at the fork and the learner's. The test-strength review of
    `PL-ZR49`'s change found that no test noticed if a branch's opening did
    not start a new adjustment.
    """

    trunk = SimulationController(fresh_gas_flow_l_min=FreshGasFlow(4.0))
    trunk.start()
    _advance_for(trunk, duration_s=60.0)
    trunk.pause()
    fork_s = trunk.snapshot().elapsed_s
    trunk.set_fresh_gas_flow(FreshGasFlow(6.0))
    branch = trunk.resumed_at(fork_s)
    branch.start()
    _advance_for(branch, duration_s=10.0)
    branch.pause()
    branch.set_fresh_gas_flow(FreshGasFlow(8.0))

    adjustments = group_adjustments(branch.snapshot().control_timeline)

    assert [
        (adjustment.from_value, adjustment.to_value, adjustment.change_count)
        for adjustment in adjustments
    ] == [(4.0, 6.0, 1), (6.0, 8.0, 1)]
    assert adjustments[0].started_at_s == fork_s
    assert adjustments[1].started_at_s > fork_s


def test_a_reset_branch_stands_on_no_halt_it_made_after_its_fork() -> None:
    """A branch that halted on a mark after its fork, and was then reset, reports no halt.

    The trunk is paused at 20 s, and a branch is taken at that instant. The
    branch gets a MAC target at 0.4 MAC alveolar and runs until the target
    halts it. Its reset returns it to its fork at 20 s. The step that reached
    the fork crossed no mark, so the branch's halt record must be empty. The
    test-strength review of `PL-ZR49`'s change found a gap in the tests. At
    the time, a trunk's halt still kept the heights that its stepped readings
    crossed, and no test noticed if a reset left a halt's crossings behind.
    Since `PL-QVBR`, every halt is derived from the step that ends at the run's
    instant, so no halt keeps anything. This test still guards against a halt
    record that names the target at the fork.
    """

    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.4), "later")
    trunk = SimulationController()
    trunk.start()
    _advance_for(trunk, duration_s=20.0)
    trunk.pause()
    fork_s = trunk.snapshot().elapsed_s
    branch = trunk.resumed_here()
    branch.add_mac_target(target)
    branch.start()
    _advance_until_halted(branch, limit_s=400.0)
    halt = branch.snapshot().bookmark_halt

    assert halt is not None
    assert halt.mac_targets == (target,)
    assert halt.instant_s > fork_s

    branch.reset()

    assert branch.snapshot().elapsed_s == fork_s
    assert branch.snapshot().bookmark_halt is None


def test_a_setting_kept_through_a_branch_reset_is_work_a_trunk_reset_would_lose() -> None:
    """A branch reset keeps the learner's settings, and they still count as the learner's work.

    The trunk runs with a fresh gas flow of 4 L/min, a delivered
    concentration of 2% and 4 L/min of ventilation. It is paused at 60 s, and
    its fresh gas flow is set to 6 L/min. A branch taken at that keyframe
    opens with the trunk's change. On the branch, the learner sets the
    delivered concentration to 3% and runs the branch for 5 s. The learner
    then resets the branch. The reset keeps 3% and records it at the fork
    (`PL-K5BS`). The learner then sets 5 L/min of ventilation. The timeline
    holds three entries. The branch opened with only the trunk's change. So
    the other two entries are work that the trunk's Reset would discard, and
    the Reset must ask first (`PL-W5WX`). The adversarial review of
    `PL-ZR49`'s change found that the 3% was treated as an opened entry
    after the reset. So a branch whose only work was the 3% was discarded
    without asking.
    """

    trunk = SimulationController(
        fresh_gas_flow_l_min=FreshGasFlow(4.0),
        delivered_concentration_percent=Percent(2.0),
        alveolar_ventilation_l_min=AlveolarVentilation(4.0),
    )
    trunk.start()
    _advance_for(trunk, duration_s=60.0)
    trunk.pause()
    fork_s = trunk.snapshot().elapsed_s
    trunk.set_fresh_gas_flow(FreshGasFlow(6.0))
    branch = trunk.resumed_at(fork_s)
    branch.set_delivered_concentration_percent(Percent(3.0))
    branch.start()
    _advance_for(branch, duration_s=5.0)
    branch.pause()
    branch.reset()

    assert branch.snapshot().elapsed_s == fork_s
    assert _described(branch.snapshot().changes_since_opening) == [
        (fork_s, ControlInput.DELIVERED, 2.0, 3.0)
    ]
    assert branch.snapshot().has_recorded_run

    branch.set_alveolar_ventilation(AlveolarVentilation(5.0))

    timeline = _described(branch.snapshot().control_timeline)
    since_opening = _described(branch.snapshot().changes_since_opening)

    assert len(timeline) == 3
    assert set(timeline) == {
        (fork_s, ControlInput.FRESH_GAS_FLOW, 4.0, 6.0),
        (fork_s, ControlInput.DELIVERED, 2.0, 3.0),
        (fork_s, ControlInput.ALVEOLAR_VENTILATION, 4.0, 5.0),
    }
    assert len(since_opening) == 2
    assert set(since_opening) == {
        (fork_s, ControlInput.DELIVERED, 2.0, 3.0),
        (fork_s, ControlInput.ALVEOLAR_VENTILATION, 4.0, 5.0),
    }


def test_branch_here_opens_with_the_dials_as_they_stand() -> None:
    """ "Branch here" runs under the settings the dials show when it is taken.

    The trunk is paused at 60 s and its fresh gas flow is set from 4 to
    6 L/min. A branch taken where the trunk stands then runs at 6 L/min, as
    the keyframe branch at that instant does, and both record the change at
    the fork. Setting the flow back to 4 L/min removes the change. A branch
    taken where the trunk stands then runs at 4 L/min and records nothing
    (project owner, 2026-10-26). The expected flows are the literal values
    that the test dialled. Each branch is checked against a run built
    directly, which is either a 4 L/min case nobody changed or one set to
    6 L/min at the same instant.
    """

    trunk = SimulationController(fresh_gas_flow_l_min=FreshGasFlow(4.0))
    trunk.start()
    _advance_for(trunk, duration_s=60.0)
    trunk.pause()
    fork_s = trunk.snapshot().elapsed_s
    trunk.set_fresh_gas_flow(FreshGasFlow(6.0))
    under_the_change = {"here": trunk.resumed_here(), "at the keyframe": trunk.resumed_at(fork_s)}
    trunk.set_fresh_gas_flow(FreshGasFlow(4.0))
    set_back = trunk.resumed_here()

    for name, branch in under_the_change.items():
        assert branch.opened_from == set_back.opened_from, name
        assert branch.snapshot().fresh_gas_flow_l_min == 6.0, name
        assert _described(branch.snapshot().control_timeline) == [
            (fork_s, ControlInput.FRESH_GAS_FLOW, 4.0, 6.0)
        ], name

    assert set_back.snapshot().fresh_gas_flow_l_min == 4.0
    assert set_back.snapshot().control_timeline == ()

    never_changed = SimulationController(fresh_gas_flow_l_min=FreshGasFlow(4.0))
    never_changed.start()
    _advance_for(never_changed, duration_s=70.0)
    changed_at_the_fork = SimulationController(fresh_gas_flow_l_min=FreshGasFlow(4.0))
    changed_at_the_fork.start()
    _advance_for(changed_at_the_fork, duration_s=60.0)
    changed_at_the_fork.pause()
    changed_at_the_fork.set_fresh_gas_flow(FreshGasFlow(6.0))
    changed_at_the_fork.start()
    _advance_for(changed_at_the_fork, duration_s=10.0)

    for branch, expected in (
        (under_the_change["here"], changed_at_the_fork),
        (under_the_change["at the keyframe"], changed_at_the_fork),
        (set_back, never_changed),
    ):
        branch.start()
        _advance_for(branch, duration_s=10.0)

        _states_agree_after_the_fork(branch, expected, fork_s, steps=100)


def test_a_passed_mark_opens_under_the_settings_the_trunk_left_its_instant_under() -> None:
    """A mark's branch runs under the settings the trunk had as it left the mark's instant.

    The trunk is paused at 30 s, its fresh gas flow is set from 4 to 6 L/min,
    and it then runs on to 60 s. Three marks are then set at instants that
    the trunk has already passed: at the opening, on the change and at 45 s.
    The branch at the opening runs at 4 L/min, because the change came
    later. The branch on the change runs at 6 L/min and records the change
    at its fork, as the keyframe branch there does. The branch at 45 s runs
    at 6 L/min and records nothing, because the step reaching 45 s already
    ran at 6 L/min (project owner, 2026-10-26). The expected flows are the
    literal values that the test dialled. Each branch is checked against a
    run built directly, which is either a 4 L/min case nobody changed or the
    trunk.
    """

    trunk = SimulationController(fresh_gas_flow_l_min=FreshGasFlow(4.0))
    trunk.start()
    _advance_for(trunk, duration_s=30.0)
    trunk.pause()
    change_s = trunk.snapshot().elapsed_s
    trunk.set_fresh_gas_flow(FreshGasFlow(6.0))
    trunk.start()
    _advance_for(trunk, duration_s=30.0)
    trunk.pause()
    at_opening = TimeBookmark(CaseInstant(0.0))
    on_the_change = TimeBookmark(CaseInstant(30.0), "the change")
    after_it = TimeBookmark(CaseInstant(45.0))

    for mark in (after_it, on_the_change, at_opening):
        trunk.add_time_bookmark(mark)

    points = {point.bookmark: point.fork_s for point in trunk.mark_fork_points}
    branches = {mark: trunk.resumed_at_mark(mark) for mark in points}

    assert points[on_the_change] == change_s
    assert {mark: branch.snapshot().fresh_gas_flow_l_min for mark, branch in branches.items()} == {
        at_opening: 4.0,
        on_the_change: 6.0,
        after_it: 6.0,
    }
    assert {
        mark: _described(branch.snapshot().control_timeline) for mark, branch in branches.items()
    } == {
        at_opening: [],
        on_the_change: [(change_s, ControlInput.FRESH_GAS_FLOW, 4.0, 6.0)],
        after_it: [],
    }
    assert branches[on_the_change].opened_from == trunk.resumed_at(change_s).opened_from

    never_changed = SimulationController(fresh_gas_flow_l_min=FreshGasFlow(4.0))
    never_changed.start()
    _advance_for(never_changed, duration_s=10.0)

    for mark, branch in branches.items():
        branch.start()
        _advance_for(branch, duration_s=10.0)
        expected = never_changed if mark is at_opening else trunk

        _states_agree_after_the_fork(branch, expected, points[mark], steps=100)
