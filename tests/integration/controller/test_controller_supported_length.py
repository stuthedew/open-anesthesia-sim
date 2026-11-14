"""The simulation controller, driven against real runs.

These tests cover stopping at, and standing on, the supported run length.

`controller_support.py` holds what several of these files share.
"""

from collections.abc import Callable

import pytest

from anesthesia_sim.app.bookmarks import MacTarget, MarkStanding, TimeBookmark
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import (
    RESET_EXIT_TEXT,
    SUPPORTED_LIMIT_NOTICE_TEMPLATE,
    notice,
    transport,
)
from anesthesia_sim.app.formatting import format_supported_run_length
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.core.concentration import MacMultiple
from anesthesia_sim.core.exceptions import SimulationConfigurationError, SimulationDomainLimitError
from anesthesia_sim.core.simulation_step import MAXIMUM_SIMULATION_STEP_S, SimulationStep
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    CaseInstant,
    FreshGasFlow,
    maximum_step_count,
    require_supported_run_length,
)
from anesthesia_sim.core.units import SECONDS_PER_MINUTE

# --- Stopping at the supported run length (PL-Y5WR) --------------------------


def test_stopping_at_the_supported_run_length_is_not_a_failure() -> None:
    """Three stopped states, and the snapshot has to tell them apart.

    A pause, a failure and reaching the supported run length all leave
    `is_running` false. Only a failure means that something on screen cannot
    be trusted. The interface reads these two fields to decide what to say.
    So if a run that stopped correctly reported a `failure_reason`, the
    interface would show "simulation error" over a sound model
    (`docs/INTERFACE.md`, "Supported run length").
    """

    controller = SimulationController()
    controller.start()
    controller.advance(SimulationStep(0.1))
    controller.halt_at_supported_limit("reached 86400 s of simulated time")

    snapshot = controller.snapshot()

    assert snapshot.is_running is False
    assert controller.has_reached_supported_limit is True
    assert snapshot.supported_limit_reason == "reached 86400 s of simulated time"
    assert controller.has_failed is False
    assert snapshot.failure_reason is None


def test_a_session_at_the_supported_run_length_cannot_be_resumed() -> None:
    """The core would refuse Start on its first tick.

    The controller raises an error rather than quietly declining, for the
    same reason a failed session does. A Start that silently does nothing is
    a control that pretends to work. The message says which of the two
    stopped states the session is in, so a caller that reports the refusal
    does not have to guess.
    """

    controller = SimulationController()
    controller.start()
    controller.halt_at_supported_limit("reached 86400 s of simulated time")

    with pytest.raises(SimulationDomainLimitError, match="supported run length"):
        controller.start()

    assert controller.snapshot().is_running is False


def test_the_first_supported_limit_reason_is_the_one_kept() -> None:
    """A later tick that reaches the same boundary must not overwrite the first reason."""

    controller = SimulationController()
    controller.halt_at_supported_limit("reached 86400 s of simulated time")
    controller.halt_at_supported_limit("reached 86400 s again")

    assert controller.snapshot().supported_limit_reason == "reached 86400 s of simulated time"


def test_reset_clears_the_supported_limit_and_restores_a_startable_session() -> None:
    """Reset is the only way out of this state, so it must really work."""

    controller = SimulationController()
    controller.start()
    controller.advance(SimulationStep(0.1))
    controller.halt_at_supported_limit("reached 86400 s of simulated time")

    controller.reset()

    assert controller.has_reached_supported_limit is False
    assert controller.snapshot().supported_limit_reason is None

    controller.start()

    assert controller.snapshot().is_running is True


def test_switching_agent_clears_the_supported_limit() -> None:
    """A new agent is a new run, and a new run has no run length behind it."""

    controller = SimulationController()
    controller.start()
    controller.halt_at_supported_limit("reached 86400 s of simulated time")

    controller.set_agent("isoflurane")

    assert controller.has_reached_supported_limit is False
    assert controller.snapshot().supported_limit_reason is None


# --- Standing on the supported run length with no step refused (PL-5291) ------
#
# The core refuses a step that starts *from* the last supported step count. So
# if a run stopped only when a step was refused, it would look like an ordinary
# pause on every route that brings it to 24:00:00 without a refused step. Those
# routes are a trunk halted there on a mark, a branch forked there, and a branch
# reset onto such a fork. Each of these offered Start, showed no limit notice,
# and told a learner that an unreached mark was still ahead of a run that could
# not step. Every assertion below is checked end to end, from the controller's
# snapshot through the pure dashboard functions that a frame is built from. The
# tests use the shipped 0.1 s step, because that is the step whose last
# supported count lands exactly on 24 hours (`PL-8H2R`).
#
# Stepping a run to 24 hours takes about 30 s. So the two runs that do it are
# built once per pytest run and shared between xdist workers. No test below
# changes what another test reads from them. A fork leaves its parent
# untouched, and the one dial moved on a stopped run is refused (`PL-3B34`).

#: A height the fat group cannot reach at 1 MAC delivered. The mark stays
#: unreached on every run below, so its standing is what the tests check.
_UNREACHABLE_TARGET = MacTarget(RecordedQuantity.FAT, MacMultiple(3.0), "never")


def _step_onto_the_supported_run_length(controller: SimulationController) -> None:
    """Take exactly the supported number of 0.1 s steps, and no refused one.

    `maximum_step_count` is the largest step count the run may reach. The core
    refuses the step after it, and this helper never takes that step.
    """

    controller.start()
    step = SimulationStep(MAXIMUM_SIMULATION_STEP_S)

    for _ in range(maximum_step_count(step)):
        controller.advance(step)


def _stepped_onto_the_limit() -> SimulationController:
    """An unmarked trunk that took the last supported step and was never refused one."""

    controller = SimulationController()
    _step_onto_the_supported_run_length(controller)

    return controller


def _halted_on_a_mark_at_the_limit() -> SimulationController:
    """A trunk halted by a time mark on 24:00:00, carrying a mark it never reached."""

    controller = SimulationController()
    controller.add_time_bookmark(
        TimeBookmark(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S), "the end")
    )
    controller.add_mac_target(_UNREACHABLE_TARGET)
    _step_onto_the_supported_run_length(controller)

    return controller


@pytest.fixture(scope="module")
def trunk_stepped_onto_the_limit(
    computed_once: Callable[[str, Callable[[], SimulationController]], SimulationController],
) -> SimulationController:
    """An unmarked trunk that took the last supported step and was never refused one."""

    return computed_once("controller trunk stepped onto the limit", _stepped_onto_the_limit)


@pytest.fixture(scope="module")
def trunk_halted_on_a_mark_at_the_limit(
    computed_once: Callable[[str, Callable[[], SimulationController]], SimulationController],
) -> SimulationController:
    """A trunk halted by a time mark on 24:00:00, carrying a mark it never reached."""

    return computed_once(
        "controller trunk halted on a mark at the limit", _halted_on_a_mark_at_the_limit
    )


#: The two runs above, each with the number of simulated minutes it steps
#: through. `tests/conftest.py` schedules every test that reads one of them
#: back to back, at the start of one xdist worker's first slice (`PL-K5VM`).
#: Each run is built once per pytest run. A worker that `worksteal` gives one
#: of these tests reads the run through `computed_once` rather than building
#: it again (`PL-ZWQS`).
MODULE_FIXTURE_MINUTES = {
    fixture.name: MAXIMUM_ELAPSED_SIMULATION_TIME_S / SECONDS_PER_MINUTE
    for fixture in (trunk_stepped_onto_the_limit, trunk_halted_on_a_mark_at_the_limit)
}


def _the_reason_the_refused_step_would_give(run: SimulationController) -> str:
    """The message with which the core refuses this run's next step, taken from the core."""

    with pytest.raises(SimulationDomainLimitError) as refusal:
        require_supported_run_length(
            run._state.step_count, SimulationStep(MAXIMUM_SIMULATION_STEP_S)
        )

    return str(refusal.value)


def _assert_reads_as_stopped_at_the_supported_run_length(run: SimulationController) -> None:
    """Check `PL-5291`'s completion condition: every reader says the run is at the limit.

    The snapshot carries the reason the refused step would give. Start is
    refused and not offered. The banner names the limit. A mark the run never
    reached shows as "not reached within the supported run length", not as
    still ahead. None of them shows a failure.
    """

    snapshot = run.snapshot()

    assert snapshot.elapsed_s == MAXIMUM_ELAPSED_SIMULATION_TIME_S
    assert snapshot.is_running is False
    assert run.has_reached_supported_limit is True
    assert snapshot.supported_limit_reason == _the_reason_the_refused_step_would_give(run)
    assert run.has_failed is False
    assert snapshot.failure_reason is None

    with pytest.raises(SimulationDomainLimitError, match="supported run length"):
        run.start()

    assert run.snapshot().is_running is False
    assert transport(snapshot).start_enabled is False
    assert notice(snapshot, None) == SUPPORTED_LIMIT_NOTICE_TEMPLATE.format(
        run_length=format_supported_run_length(), exit=RESET_EXIT_TEXT
    )

    if _UNREACHABLE_TARGET in snapshot.bookmarks.mac_targets:
        standing = snapshot.bookmark_standings.of_mac_target(_UNREACHABLE_TARGET)

        assert standing is MarkStanding.NOT_REACHED_WITHIN_CAP


def test_a_run_standing_on_the_supported_run_length_reads_as_stopped_from_the_arriving_step(
    trunk_stepped_onto_the_limit: SimulationController,
) -> None:
    """The run halts on the step that arrives at the limit, not one refused tick later.

    No step was refused: the run took exactly the supported count of steps and
    stopped there. Because the limit is read from the state, this stop is the
    same stop that the refusal used to produce. Halting on arrival keeps the
    snapshot's contract, which is that `is_running` is false wherever a limit
    reason is set. It does so without a flag that only a refusal could set.
    """

    trunk = trunk_stepped_onto_the_limit

    assert trunk._state.step_count == maximum_step_count(SimulationStep(MAXIMUM_SIMULATION_STEP_S))
    _assert_reads_as_stopped_at_the_supported_run_length(trunk)

    # A further tick does nothing, as it does on a paused run. Nothing is
    # raised, and the clock stays exactly where the last supported step left it.
    trunk.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert trunk.snapshot().elapsed_s == MAXIMUM_ELAPSED_SIMULATION_TIME_S


def test_a_trunk_halted_on_a_mark_at_the_supported_run_length_reads_as_stopped_there(
    trunk_halted_on_a_mark_at_the_limit: SimulationController,
) -> None:
    """The first row of `PL-5291`'s table: a trunk halted on a mark at 24:00:00.

    That trunk showed "Paused" and offered Start.
    """

    trunk = trunk_halted_on_a_mark_at_the_limit
    snapshot = trunk.snapshot()

    assert snapshot.bookmark_halt is not None
    assert snapshot.bookmark_standings.of_time_bookmark(
        TimeBookmark(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S), "the end")
    ) is (MarkStanding.PASSED)
    _assert_reads_as_stopped_at_the_supported_run_length(trunk)


def test_a_branch_on_the_supported_run_length_is_not_sent_to_a_reset_that_returns_it_there(
    trunk_halted_on_a_mark_at_the_limit: SimulationController,
) -> None:
    """No branch opens on 24:00:00, so none is left where Reset only returns it to the limit.

    A branch taken at a mark on the limit could never step. Its banner named
    Reset as the way out. A branch's Reset returns it to its fork, so the way
    out led back to the same stop (`PL-VHQX`). Now the fork is rejected, and
    the branch control does not offer the mark. The trunk is still shown as
    stopped at the limit. The expected message is typed by hand.
    """

    trunk = trunk_halted_on_a_mark_at_the_limit
    on_the_limit = TimeBookmark(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S), "the end")

    assert on_the_limit in trunk.snapshot().bookmarks.time_bookmarks
    assert trunk.mark_fork_points == ()
    assert BranchedCase(trunk).mark_fork_points == ()

    with pytest.raises(SimulationConfigurationError) as refusal:
        trunk.resumed_at_mark(on_the_limit)

    assert str(refusal.value) == (
        "a branch at 86400.0 s would open on the supported run length, where no step is left "
        "to take, so it could never be run; a setting change or a mark before it is still "
        "branched at with resumed_at or resumed_at_mark"
    )
    _assert_reads_as_stopped_at_the_supported_run_length(trunk)


def test_no_dial_makes_a_keyframe_on_the_supported_run_length_to_branch_at(
    trunk_stepped_onto_the_limit: SimulationController,
) -> None:
    """A dial moved on the stopped trunk is refused, so no branch opens at a keyframe on 24:00:00.

    Until `PL-3B34`, a dial moved after the run stopped was recorded at
    24:00:00. That made a keyframe there, and `resumed_at` opened a branch on
    it that could never step. The stopped run now refuses the dial, so the
    trunk keeps its one stretch from 0 s. `resumed_at` therefore rejects the
    limit as an instant with no keyframe. A mark on the limit is rejected too, as
    `test_a_branch_on_the_supported_run_length_is_not_sent_to_a_reset_that_returns_it_there`
    checks.
    """

    trunk = trunk_stepped_onto_the_limit

    with pytest.raises(
        SimulationConfigurationError,
        match="^the fresh gas flow setting cannot be changed on a stopped run",
    ):
        trunk.set_fresh_gas_flow(FreshGasFlow(6.0))

    assert [segment.opening.instant_s for segment in trunk.run_segments] == [0.0]

    with pytest.raises(SimulationConfigurationError, match="keyframe"):
        trunk.resumed_at(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S))

    _assert_reads_as_stopped_at_the_supported_run_length(trunk)


def test_a_run_at_the_supported_run_length_offers_no_place_to_branch_where_it_stands(
    trunk_stepped_onto_the_limit: SimulationController,
    trunk_halted_on_a_mark_at_the_limit: SimulationController,
) -> None:
    """A stop at the limit is not a pause, so the run's position is neither offered nor taken.

    No step is left to take there, so a branch opened where the run is stopped
    could never be run. While the case allows only one comparison, only the trunk's
    Reset, which discards the case, would take that branch off the chart
    (`PL-Y2SL`). Both ways of arriving there are refused alike: stepping onto
    the limit, and halting on a mark at it. The refusal names the fork methods
    that still work there.
    """

    for trunk in (trunk_stepped_onto_the_limit, trunk_halted_on_a_mark_at_the_limit):
        assert trunk.here_fork_point is None
        assert BranchedCase(trunk).here_fork_point is None

        with pytest.raises(SimulationConfigurationError, match="supported run length") as refusal:
            trunk.resumed_here()

        assert "resumed_at_mark" in str(refusal.value)


def test_the_refusal_to_branch_at_the_supported_run_length_is_pinned_whole(
    trunk_stepped_onto_the_limit: SimulationController,
) -> None:
    """86,400 s is the supported run length `docs/INTERFACE.md` § "Supported run length" states."""

    with pytest.raises(SimulationConfigurationError) as refusal:
        trunk_stepped_onto_the_limit.resumed_here()

    assert str(refusal.value) == (
        "this run stands at 86400.0 s, the supported run length, where no step is left to "
        "take, so a branch opened where it stands could not be run; a setting change or a "
        "mark it passed before is still branched at with resumed_at or resumed_at_mark"
    )
