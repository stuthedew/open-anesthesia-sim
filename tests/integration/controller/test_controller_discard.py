"""The simulation controller, driven against real runs.

These tests cover whether a run holds anything a reset would discard.

`controller_support.py` holds what several of these files share.
"""

from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.core.simulation_step import MAXIMUM_SIMULATION_STEP_S, SimulationStep
from anesthesia_sim.core.supported_ranges import FreshGasFlow
from tests.integration.controller.controller_support import (
    _advance_for,
    _trunk_halted_on_a_bookmark,
    _trunk_with_two_changes,
)


def test_a_run_nobody_has_touched_holds_nothing_to_discard() -> None:
    """Check the state of a new session, which is also the state `reset()` returns to.

    `SimulationSnapshot.has_recorded_run` lets the interface tell an agent
    change that would destroy a run from a harmless one. So the tests pin both
    of its values rather than leaving them to a caller's interpretation.
    """

    controller = SimulationController()

    assert controller.snapshot().has_recorded_run is False


def test_an_advanced_run_holds_something_to_discard() -> None:
    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=10.0)

    assert controller.snapshot().has_recorded_run is True


def test_a_setting_changed_before_the_run_starts_is_something_to_discard() -> None:
    """Elapsed time alone would miss this one.

    A vaporizer turned before Start is a recorded input at zero simulated
    time, and it is part of the case that a reader set up. A check that read
    only the clock would call this run empty and discard it without asking.
    """

    controller = SimulationController()
    controller.set_fresh_gas_flow(FreshGasFlow(2.0))

    snapshot = controller.snapshot()
    assert snapshot.elapsed_s == 0.0
    assert snapshot.control_timeline != ()
    assert snapshot.has_recorded_run is True


def test_reset_returns_a_run_to_holding_nothing_to_discard() -> None:
    """Reset is the way to make an agent change cost nothing.

    This matters. A reader who wants a different agent and does not want to
    keep their case is told to use Reset. So Reset must really clear both
    halves of the predicate.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=10.0)
    controller.set_fresh_gas_flow(FreshGasFlow(2.0))
    controller.reset()

    assert controller.snapshot().has_recorded_run is False


def test_set_agent_leaves_a_new_run_holding_nothing_to_discard() -> None:
    """Right after a confirmed switch, the new run must not count as something to discard.

    Otherwise a learner who confirmed a new case and then opened the selector
    again would be asked about a case with nothing in it.
    """

    controller = SimulationController()
    controller.start()
    _advance_for(controller, duration_s=10.0)
    controller.set_agent("desflurane")

    assert controller.snapshot().has_recorded_run is False


def test_a_fresh_branch_holds_nothing_to_destroy() -> None:
    """`PL-7TBQ`: a new branch is built at its fork, and being built there is not a learner's act.

    The branch uses the case's clock, so its elapsed time is past zero as soon
    as it exists. Counted from zero, it held a run to lose before the learner
    had done anything to it. Counted from where it began, it holds nothing.

    A branch taken at a keyframe also opens with the trunk's change there in
    its own timeline (`PL-ZR49`). That entry is where the branch began, not
    something the learner did to it, so it does not count either.
    """

    trunk = _trunk_with_two_changes()
    fork_s = trunk.run_segments[-1].opening.instant_s
    branch = BranchedCase(trunk).fork_at(fork_s)

    snapshot = branch.snapshot()

    # The premise: the clock is past zero, and the only entry is the one the
    # branch opened with.
    assert snapshot.elapsed_s == snapshot.began_at_s == branch.began_at_s == fork_s
    assert snapshot.elapsed_s > 0.0
    assert [change.elapsed_s for change in snapshot.control_timeline] == [fork_s]
    assert snapshot.opened_with == snapshot.control_timeline
    assert trunk.snapshot().began_at_s == 0.0

    assert snapshot.has_recorded_run is False


def test_a_fresh_branch_taken_at_a_bookmark_holds_nothing_to_destroy() -> None:
    """Check the other way to fork, at the step on which the trunk halted."""

    marked = _trunk_halted_on_a_bookmark()
    branch = BranchedCase(marked).fork_here()

    snapshot = branch.snapshot()

    assert snapshot.elapsed_s == snapshot.began_at_s == marked.snapshot().elapsed_s
    assert snapshot.has_recorded_run is False


def test_a_branch_advanced_one_step_past_its_fork_holds_something_to_destroy() -> None:
    trunk = _trunk_with_two_changes()
    branch = trunk.resumed_at(trunk.run_segments[-1].opening.instant_s)
    branch.start()
    branch.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert branch.snapshot().has_recorded_run is True


def test_a_setting_changed_on_a_fresh_branch_is_something_to_destroy() -> None:
    """Check the timeline half on a branch: a change made at the fork is the learner's act."""

    trunk = _trunk_with_two_changes()
    branch = trunk.resumed_at(trunk.run_segments[-1].opening.instant_s)
    branch.set_fresh_gas_flow(FreshGasFlow(1.0))

    snapshot = branch.snapshot()

    assert snapshot.elapsed_s == snapshot.began_at_s
    assert snapshot.has_recorded_run is True


def test_resetting_a_branch_returns_it_to_holding_nothing_to_destroy() -> None:
    """A branch that was advanced and then reset still had a run to lose, as `PL-7TBQ` measured.

    A branch's reset returns it to its fork rather than to zero. So a branch
    that was only advanced is a fresh branch after its reset, and it must
    count as one. A setting that the learner changed and kept through the
    reset is different. `PL-7TBQ`'s Done-when, the condition for closing that
    item, counts "a setting change of its own" as something to lose. Until
    `PL-K5BS`, a reset dropped the record of such a change while the branch
    kept running under it. So this test once expected nothing to lose in that
    case too (`PL-ZR49`).
    """

    trunk = _trunk_with_two_changes()
    branch = trunk.resumed_at(trunk.run_segments[-1].opening.instant_s)
    branch.start()
    _advance_for(branch, duration_s=5.0)
    branch.reset()

    assert branch.snapshot().has_recorded_run is False

    branch.start()
    _advance_for(branch, duration_s=5.0)
    branch.set_fresh_gas_flow(FreshGasFlow(1.0))
    branch.reset()

    assert branch.snapshot().fresh_gas_flow_l_min == 1.0
    assert branch.snapshot().has_recorded_run is True
