"""The simulation controller, driven against real runs.

These tests cover each branch refusal a learner can read, pinned whole (`PL-79PK`).

`controller_support.py` holds what several of these files share.
"""

import pytest

from anesthesia_sim.app.bookmarks import TimeBookmark
from anesthesia_sim.app.branch_controls import FORK_POINT_LABEL, HERE_FORK_NAME, TAKE_FORK_LABEL
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.failures import FailureKind
from anesthesia_sim.app.formatting import format_elapsed
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.supported_ranges import CaseInstant
from tests.integration.controller.controller_support import (
    _trunk_paused_past_a_change,
    _trunk_with_two_changes,
)

# --- Each branch refusal a learner can read, pinned whole (PL-79PK) -----------
#
# `SimulationView` shows the message for a refused branch word for word after
# "Branch not opened", and for a refused agent change in the "Setting refused"
# banner. The tests above
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
        "this run is a branch opened at 1m, and a branch carries the agent of the case "
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
    failed.fail("a step raised", kind=FailureKind.UNEXPECTED)
    opening = SimulationController()
    refusals = {}

    for name, trunk in (("going", going), ("failed", failed), ("opening", opening)):
        with pytest.raises(SimulationConfigurationError) as refusal:
            trunk.resumed_here()

        refusals[name] = str(refusal.value)

    assert refusals == {
        "going": (
            "this run is still going, so where it stands moves on with every step; pause it, "
            'then press "Branch here" to branch where it stops'
        ),
        "failed": (
            "this run stopped at 2m on a failure, not a pause (a step raised), so where it "
            "stands is not a place to branch; an earlier setting change or mark can still be "
            'chosen under "From" and branched at with "Branch"'
        ),
        "opening": (
            "this run stands at its opening and has recorded nothing to branch from; to "
            'branch at the opening, choose it under "From" and press "Branch"'
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
        "this run's clock stands at 3m, short of the mark at 10m, so the case holds no "
        "state there to branch from; a mark can be branched at once the run has passed it, "
        'or with "Branch here" while the run is stopped on the step that crosses it'
    )
    assert str(unmarked.value) == "no time bookmark stands at 1m, so there is no mark there"


def test_a_refused_branch_names_the_on_screen_control_and_a_formatted_instant() -> None:
    """Each branch refusal names controls by their words on screen and instants as the panel does.

    The branch panel labels its instants with `format_elapsed`, such as "2m",
    and its controls "From", "Branch" and "Branch here". A refusal that named
    the controller's methods or printed seconds as "120 s" gave a learner
    nothing on screen to act on (`PL-3JTH`).
    """

    going = _trunk_with_two_changes()
    going.start()
    failed = _trunk_with_two_changes()
    failed.fail("a step raised", kind=FailureKind.UNEXPECTED)
    short = _trunk_paused_past_a_change()
    ahead = TimeBookmark(CaseInstant(600))
    short.add_time_bookmark(ahead)
    refusals: list[str] = []

    for call in (going.resumed_here, failed.resumed_here, lambda: short.resumed_at_mark(ahead)):
        with pytest.raises(SimulationConfigurationError) as refusal:
            call()

        refusals.append(str(refusal.value))

    going_text, failed_text, short_text = refusals

    assert f'"{HERE_FORK_NAME}"' in going_text
    assert f'"{FORK_POINT_LABEL}"' in failed_text
    assert f'"{TAKE_FORK_LABEL}"' in failed_text
    assert format_elapsed(CaseInstant(120)) in failed_text
    assert format_elapsed(CaseInstant(180)) in short_text
    assert format_elapsed(CaseInstant(600)) in short_text
    assert f'"{HERE_FORK_NAME}"' in short_text

    for text in refusals:
        assert "resumed_" not in text
        assert "s" not in text.replace(",", " ").replace(";", " ").split()
