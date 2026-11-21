"""The simulation controller, driven against real runs.

These tests cover each branch refusal a learner can read, pinned whole (`PL-79PK`).

`controller_support.py` holds what several of these files share.
"""

import pytest

from anesthesia_sim.app.bookmarks import TimeBookmark
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.supported_ranges import CaseInstant
from tests.integration.controller.controller_support import (
    _trunk_paused_past_a_change,
    _trunk_with_two_changes,
)

# --- Each branch refusal a learner can read, pinned whole (PL-79PK) -----------
#
# `SimulationView` shows the message for a refused branch, and for a refused
# agent change, word for word in the "Setting refused" banner. The tests above
# match one phrase of each message, so they pass even when the instant, the
# reason or the advice is wrong. Each expected sentence below is typed by hand
# from the run the test builds. The two-change trunk changes a setting at 30 s
# and 60 s and stops at 120 s. The paused-past-a-change trunk changes one
# setting at 30 s and stops at 180 s.


def test_a_branch_s_agent_change_refusal_is_pinned_whole() -> None:
    trunk = _trunk_with_two_changes()
    branch = BranchedCase(trunk).fork_at(CaseInstant(60))

    with pytest.raises(SimulationConfigurationError) as refusal:
        branch.set_agent("desflurane")

    assert str(refusal.value) == (
        "this run is a branch opened at 60 s, and a branch carries the agent of the case "
        "it continues; changing agent begins a new case, so change it on the run this "
        "branch came from or start a new one"
    )


def test_a_branch_at_a_second_the_run_has_not_reached_refusal_is_pinned_whole() -> None:
    trunk = _trunk_with_two_changes()

    with pytest.raises(SimulationConfigurationError) as refusal:
        trunk.resumed_at(CaseInstant(121))

    assert str(refusal.value) == (
        "this run stores no state at 121 s: it stores one state for each second from 0 s, "
        "where it opened, to 120 s, the second it has reached"
    )


def test_each_refusal_to_branch_where_a_run_stands_is_pinned_whole() -> None:
    going = _trunk_with_two_changes()
    going.start()
    failed = _trunk_with_two_changes()
    failed.fail("a step raised")
    opening = SimulationController()
    refusals = {}

    for name, trunk in (("going", going), ("failed", failed), ("opening", opening)):
        with pytest.raises(SimulationConfigurationError) as refusal:
            trunk.resumed_here()

        refusals[name] = str(refusal.value)

    assert refusals == {
        "going": (
            "this run is going, so where it stands moves with every step and an instant read "
            "off it is gone before it can be branched at; pause it, and resumed_here branches "
            "where it then stands"
        ),
        "failed": (
            "this run stopped at 120 s on a failure, not a pause (a step raised), so where "
            "it stands is not a place to branch; a setting change or a mark it passed before "
            "is still branched at with resumed_at or resumed_at_mark"
        ),
        "opening": (
            "this run stands at its opening and has recorded nothing to branch from; "
            "resumed_at opens a branch at the opening"
        ),
    }


def test_each_refusal_to_branch_at_a_mark_is_pinned_whole() -> None:
    trunk = _trunk_paused_past_a_change()
    ahead = TimeBookmark(CaseInstant(600))
    trunk.add_time_bookmark(ahead)

    with pytest.raises(SimulationConfigurationError) as short_of_it:
        trunk.resumed_at_mark(ahead)

    with pytest.raises(SimulationConfigurationError) as unmarked:
        trunk.resumed_at_mark(TimeBookmark(CaseInstant(60)))

    assert str(short_of_it.value) == (
        "this run's clock stands at 180 s, short of the mark at 600 s, so the case "
        "holds no state there to branch from: a mark is branched at once the run has "
        "passed it, or, standing on the step that crosses it, with resumed_here"
    )
    assert str(unmarked.value) == "no time bookmark stands at 60 s, so there is no mark there"
