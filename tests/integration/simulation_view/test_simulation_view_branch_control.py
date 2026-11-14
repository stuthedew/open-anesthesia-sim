"""The dashboard, driven headless against real runs.

These tests cover where the branch control offers a fork, and what a failing frame withdraws from
it.

`simulation_view_support.py` describes the whole suite.
"""

from typing import NoReturn

import pytest
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QStyle, QStyleOptionComboBox

from anesthesia_sim.app import simulation_view as simulation_view_module
from anesthesia_sim.app.bookmarks import MarkStanding, TimeBookmark
from anesthesia_sim.app.controller import BranchedCase, MarkForkPoint, SimulationController
from anesthesia_sim.app.dashboard_frame import (
    FORK_NOTHING_SELECTED_TEXT,
    HALT_FORK_LABEL_TEMPLATE,
    HERE_FORK_LABEL_TEMPLATE,
    MARK_STANDING_COMPARED_TEXT,
    SIMULATION_STEP_S,
    STATUS_FAILED_TEXT,
    comparing_fork_lock_text,
    fork_offer,
    run_label,
)
from anesthesia_sim.app.formatting import format_elapsed
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    CaseInstant,
    FreshGasFlow,
)
from anesthesia_sim.core.units import SECONDS_PER_HOUR, SECONDS_PER_MINUTE
from tests.integration.simulation_view.simulation_view_support import (
    _BEHIND_MARK_FORK_S,
    _BEHIND_MARK_LABEL,
    _BEHIND_MARK_S,
    _HALT_MARK_S,
    _REWIND_PAUSE_S,
    COMPARED,
    FIRST_RUN,
    SECOND_RUN,
    _advance_to,
    _branched_case,
    _case_view,
    _failing_assembly,
    _fork_panel,
    _halted_branch_view,
    _halted_trunk_case,
    _marks_panel,
    _offered_fork_instants,
    _opened_bookmark_dialog,
    _paused_run_with_history,
    _real_step_failure,
    _rewind_case,
    _select_fork_entry,
    _shown_view,
    _steps,
    _take_fork,
)


def test_a_second_fork_is_refused_while_two_runs_are_shown(application: QApplication) -> None:
    """The display is capped at two and there is no run selector, so the way out is Reset.

    The fork is refused visibly rather than silently. The control is hidden
    in the same way that the transport hides the agent selector, and the
    reason stays where it was, even after a press. Replacing the shown branch while
    the first branch went on living inside `BranchedCase` would create state
    that the screen does not show.
    """

    case = _branched_case()
    view = _case_view(application, case)
    _take_fork(view, 60.0)

    panel = _fork_panel(view)

    assert panel.take_button.isHidden() is True
    assert panel.take_button.isEnabled() is False
    assert panel.point_selector.isHidden() is True
    assert panel.point_selector.isEnabled() is False
    assert panel.lock_text.text() == comparing_fork_lock_text(COMPARED)
    assert panel.lock_text.isHidden() is False
    # The mode is not a warning: this interface has one alarm colour and a
    # comparison in progress is the dashboard working as intended.
    assert panel.notice.notice() is None

    view._handle_fork()

    assert len(view.runs) == 2
    assert len(case.branches) == 1
    assert panel.lock_text.text() == comparing_fork_lock_text(COMPARED)


def test_a_branch_is_offered_at_the_mark_the_run_is_standing_on(application: QApplication) -> None:
    """`PL-TYWQ`, and `ROADMAP.md`'s v0.5.0 Definition of done end to end.

    This is the one sequence that the interface could not complete: mark the
    decision point, watch the run stop there, and branch there. The branch
    opens at the instant on which the trunk halted. It does not open at the
    nearest keyframe, which is what a learner used to have to settle for. It
    arrives through the same panel from which a control-event fork is taken.

    The trunk is left on its halt, which makes this a comparison rather than
    an undo.
    """

    case, view = _halted_trunk_case(application)
    halt = case.trunk.snapshot().bookmark_halt
    assert halt is not None
    halted_s = halt.instant_s

    assert _fork_panel(view).here_button.isHidden() is False
    assert halted_s not in case.fork_points_s

    _fork_panel(view).here_button.click()

    assert len(view.runs) == 2
    assert len(case.branches) == 1
    branch = case.branches[0]
    assert branch.snapshot().elapsed_s == pytest.approx(halted_s)
    assert view.runs[1].controller is branch
    # A mark adds no keyframe, so the trunk's keyframes are untouched by all
    # of this.
    assert case.fork_points_s == (0.0, 60.0)
    # And the trunk still stands where it stopped.
    assert case.trunk.snapshot().elapsed_s == pytest.approx(halted_s)
    assert _fork_panel(view).notice.notice() is None


def test_the_fork_here_says_which_instant_it_will_open_the_branch_at(
    application: QApplication,
) -> None:
    """The label carries the halted instant, so a press is readable before it is made.

    A bare "Branch here" beside the permanent button would leave two
    identical buttons doing different things. The instant is the one at which
    the branch opens, not the one the learner marked. Those differ whenever a
    mark lies inside a step, and naming the wrong one would put a correct
    control under a wrong label.
    """

    case, view = _halted_trunk_case(application)
    halt = case.trunk.snapshot().bookmark_halt
    assert halt is not None

    label = _fork_panel(view).here_button.text()

    assert label == HALT_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(halt.instant_s))

    _fork_panel(view).here_button.click()

    assert case.branches[0].snapshot().elapsed_s == pytest.approx(halt.instant_s)


def test_a_mark_inside_a_step_branches_where_the_run_stopped_not_where_it_was_marked(
    application: QApplication,
) -> None:
    """The safety-relevant half of the label, end to end (`PL-TYWQ`).

    A mark that does not land on the step grid halts the run at the step's
    end. So the instant a learner marked and the instant at which a branch
    can open are two different numbers. The branch opens at the second one,
    because it is the only one for which the run holds state. So the button
    has to show the second one. Showing the first would put a correct control
    under a label naming a time at which nothing happens.
    `CLAUDE.md`'s safety-critical standard counts that as a failure of the
    value rather than of its presentation.
    """

    marked_s = 80.05
    halted_s = 80.1
    case = _branched_case()
    view = _case_view(application, case)
    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(marked_s), "mid-step"))
    case.trunk.start()
    _advance_to(case.trunk, halted_s)
    view.present(False)

    halt = case.trunk.snapshot().bookmark_halt
    assert halt is not None
    assert halt.instant_s == pytest.approx(halted_s)
    assert halt.instant_s != pytest.approx(marked_s)

    label = _fork_panel(view).here_button.text()

    assert format_elapsed(halted_s) in label
    assert format_elapsed(marked_s) not in label

    _fork_panel(view).here_button.click()

    assert case.branches[0].snapshot().elapsed_s == pytest.approx(halted_s)


def test_the_fork_here_is_on_the_panel_whenever_the_trunk_stops_and_off_it_while_it_goes(
    application: QApplication,
) -> None:
    """`PL-Y2SL`: the control is shown on any pause, and while running it is absent, not inert.

    The control is there on the paused trunk and gone once the trunk starts.
    It comes back with the halt's own words when a mark stops the trunk, goes
    again on the next step, and comes back with the plain words when the
    learner pauses. The selector does not follow it, which is the point of
    making this a second control. A list that gained and lost a row would
    change its entries under a reader who had looked away. A control that is
    either there or not can be noticed on sight. The mark the run stopped on
    joins the selector when the clock reaches it, as a mark the trunk has
    passed (`PL-W4XQ`). The end of the halt does not take it away again.
    """

    case = _branched_case()
    view = _case_view(application, case)
    button = _fork_panel(view).here_button
    offered_before = list(_offered_fork_instants(view))
    paused_s = case.trunk.snapshot().elapsed_s

    assert button.isHidden() is False
    assert button.isEnabled() is True
    assert button.text() == HERE_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(paused_s))

    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(_HALT_MARK_S)))
    case.trunk.start()
    view.present(False)

    assert button.isHidden() is True
    assert button.isEnabled() is False
    assert button.text() == ""

    _advance_to(case.trunk, _HALT_MARK_S)
    view.present(False)

    halt = case.trunk.snapshot().bookmark_halt
    assert halt is not None
    assert button.isHidden() is False
    assert button.isEnabled() is True
    assert button.text() == HALT_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(halt.instant_s))
    offered_on_the_halt = list(_offered_fork_instants(view))
    assert offered_on_the_halt == [*offered_before, halt.instant_s]

    case.trunk.start()
    case.trunk.advance(SIMULATION_STEP_S)
    view.present(False)

    assert case.trunk.snapshot().bookmark_halt is None
    assert button.isHidden() is True
    assert button.isEnabled() is False
    assert list(_offered_fork_instants(view)) == offered_on_the_halt

    case.trunk.pause()
    view.present(False)
    paused_again_s = case.trunk.snapshot().elapsed_s

    assert button.isHidden() is False
    assert button.text() == HERE_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(paused_again_s))
    assert list(_offered_fork_instants(view)) == offered_on_the_halt


def test_a_paused_trunk_is_branched_where_it_stands_from_the_panel(
    application: QApplication,
) -> None:
    """`PL-Y2SL` end to end: paused between keyframes, one press branches right there.

    The trunk is at 120 s, which is neither a keyframe nor a mark, so no
    entry in the selector names it. The button names it. The branch that the
    button takes opens at that instant and is drawn beside the trunk. The
    trunk stays where it was.
    """

    case, view, _ = _rewind_case(application)
    paused_s = case.trunk.snapshot().elapsed_s
    button = _fork_panel(view).here_button

    assert paused_s not in _offered_fork_instants(view)
    assert button.isHidden() is False
    assert button.text() == HERE_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(paused_s))

    button.click()

    assert len(view.runs) == 2
    assert len(case.branches) == 1
    assert case.branches[0].began_at_s == paused_s
    assert view.runs[1].controller is case.branches[0]
    assert case.trunk.snapshot().elapsed_s == paused_s
    assert _fork_panel(view).notice.notice() is None


def test_the_fork_here_is_refused_with_the_rest_while_two_runs_are_shown(
    application: QApplication,
) -> None:
    """The cap applies to branches, whichever control a branch is taken through.

    A second fork taken through the transient control has to be refused
    exactly as one through the permanent control is. The display is capped at
    two runs, and there is no run selector. So the control goes off the panel
    rather than staying enabled only to apologise when pressed. The guard
    behind it still applies, for a press that reaches it anyway.
    """

    case, view = _halted_trunk_case(application)
    _take_fork(view, 60.0)

    assert len(view.runs) == 2
    assert case.trunk.snapshot().bookmark_halt is not None
    assert _fork_panel(view).here_button.isHidden() is True
    assert _fork_panel(view).here_button.isEnabled() is False
    assert _fork_panel(view).here_button.text() == ""

    view._handle_here_fork()

    assert len(view.runs) == 2
    assert len(case.branches) == 1
    assert _fork_panel(view).lock_text.text() == comparing_fork_lock_text(COMPARED)


def test_a_fork_here_the_case_refuses_is_reported_and_adds_no_run(
    application: QApplication,
) -> None:
    """The trunk can be started after the frame that drew the button, so the press re-asks.

    The position of a running trunk moves with every step. So the case
    refuses a fork there, rather than taking one a step or a tick away from
    the instant the button named. The reason reaches the notice instead of
    being swallowed. The panel's own frame does not prove that the fork is
    still available.
    """

    case, view = _halted_trunk_case(application)
    case.trunk.start()

    _fork_panel(view).here_button.click()

    assert len(view.runs) == 1
    assert case.branches == ()
    notice = _fork_panel(view).notice.notice()
    assert notice is not None
    # It names what is wrong rather than reporting a generic failure, so a
    # reader who pressed a button that was there a moment ago learns why.
    assert "is going" in notice


def test_a_failing_frame_on_a_paused_trunk_withdraws_branch_here(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A paused trunk whose frame fails stops offering a branch where it stands.

    "Branch here" is offered at every pause (`PL-Y2SL`), and the panel was
    redrawn only at the end of a frame. So with every frame failing, the
    trunk showed "Stopped - simulation error" beside an enabled "Branch
    here: 1m". A press was refused by the case, and the next failing frame
    lost the refusal (`PL-MMNX`). The halt now redraws the panel from the
    case, which offers no fork on a failed trunk.
    """

    case = _branched_case()
    view = _case_view(application, case)
    here = _fork_panel(view).here_button
    assert here.isHidden() is False, "the paused trunk offers no branch here to withdraw"
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    view.present(False)

    assert case.trunk.has_failed is True
    assert case.here_fork_point is None
    assert view.runs[0]._status_text.text() == STATUS_FAILED_TEXT
    assert here.isHidden() is True
    assert here.isEnabled() is False


def test_a_trunk_halted_by_a_failing_frame_offers_no_branch_at_all(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A trunk halted by the shared frame offers no keyframe, no mark and no "Branch here".

    A branch opened there would be drawn by the same failing frame and halt
    on the next one, so each of the three could only fail (`PL-T2Q2`). Before
    this, the keyframe selector's Branch button stayed enabled and `fork_at`
    opened the branch. The case now refuses every way of opening a branch,
    as well as withdrawing the offer.
    """

    case = _branched_case()
    mark = TimeBookmark(CaseInstant(30.0), "check")
    case.trunk.add_time_bookmark(mark)
    view = _case_view(application, case)
    panel = _fork_panel(view)
    # Induction, the mark the trunk passed and its one setting change.
    assert panel.point_selector.count() == 3, "the trunk offers no keyframe or mark to withdraw"
    assert panel.here_button.isHidden() is False, "the paused trunk offers no branch here"
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    view.present(False)

    assert case.trunk.has_failed is True
    assert view.runs[0]._status_text.text() == STATUS_FAILED_TEXT
    assert panel.point_selector.count() == 0
    assert panel.point_selector.isHidden() is True
    assert panel.take_button.isHidden() is True
    assert panel.take_button.isEnabled() is False
    assert panel.here_button.isHidden() is True
    assert case.fork_points_s == ()
    assert case.mark_fork_points == ()

    with pytest.raises(
        SimulationConfigurationError, match="the dashboard this run is drawn in failed"
    ):
        case.fork_at(CaseInstant(60.0))

    with pytest.raises(
        SimulationConfigurationError, match="the dashboard this run is drawn in failed"
    ):
        case.fork_at_mark(mark)

    assert case.branches == ()


def test_a_trunk_failed_on_its_own_step_keeps_its_earlier_keyframes_branchable(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A trunk whose own step failed keeps the keyframes it recorded, and a branch opens at one.

    Each keyframe is a state the run computed before the failure, and the
    frame still draws, so "go back and try something else" stays on offer
    (`PL-T2Q2`). Only the frame's failure withdraws it. The instants are the
    fixture's own: induction, and the setting change it made at 60 s.
    """

    case = _branched_case()
    view = _case_view(application, case)
    trunk = case.trunk

    def failing_advance(simulation_step_s: float) -> NoReturn:
        raise _real_step_failure()

    trunk.start()
    monkeypatch.setattr(trunk, "advance", failing_advance)

    _steps(view.runs[0], 1)

    assert trunk.has_failed is True
    assert view.runs[0]._status_text.text() == STATUS_FAILED_TEXT
    assert _offered_fork_instants(view) == (0.0, 60.0)
    assert _fork_panel(view).take_button.isHidden() is False

    _take_fork(view, 60.0)

    assert len(case.branches) == 1
    assert len(view.runs) == 2
    opened_from = case.branches[0].opened_from
    assert opened_from is not None
    assert opened_from.fork.instant_s == 60.0


def test_a_fork_panel_the_case_cannot_restate_on_a_halt_offers_nothing(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    """A halt whose fork panel raises when restated withdraws the panel and still stands.

    The restatement runs inside the halt path. There, an exception would
    escape the render path's guard into the toolkit and leave the halt's
    retry undone. So the restatement is guarded. A panel that it cannot
    restate offers nothing, rather than the last frame's offer (`PL-MMNX`).
    """

    case = _branched_case()
    view = _case_view(application, case)
    assert _fork_panel(view).point_selector.count() > 0

    def unanswerable(case: BranchedCase) -> NoReturn:
        raise RuntimeError("the case could not say where its trunk stands")

    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    monkeypatch.setattr(BranchedCase, "here_fork_point", property(unanswerable))
    capfd.readouterr()

    view.present(False)

    assert "Traceback" not in capfd.readouterr().err
    assert case.trunk.has_failed is True
    assert view.runs[0]._status_text.text() == STATUS_FAILED_TEXT
    assert _fork_panel(view).here_button.isHidden() is True
    assert _fork_panel(view).point_selector.count() == 0


def test_a_failing_frame_withdraws_the_last_frames_bookmark_standings(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If every frame fails, the bookmark panel stops listing an unreachable mark as still to come.

    The bookmark panel used to be redrawn only from the snapshots in a
    frame that drew. When every frame failed, the panel kept the standings from the last
    frame that drew. So a mark ahead of the clock was still listed as to come, beside
    "Stopped - simulation error". That row tells a learner to wait for a mark that the
    failed run will never reach (`PL-YHR3`). Now, when the run halts, the panel is redrawn
    from each run's own record of its marks. That redraw does not need a frame.

    The test writes the expected row as a literal string. It copies the panel's wording for
    a mark that a failed run can no longer reach. The test then lets frames draw again and
    checks that a frame of the same failed run shows the same row. That shows the redraw at
    the halt and the redraw from a frame agree.
    """

    controller = _paused_run_with_history()
    # Ahead of the paused clock, so the run has not reached it yet.
    controller.add_time_bookmark(TimeBookmark(CaseInstant(600.0), "check"))
    view = _shown_view(application, controller)
    ahead = _marks_panel(view).times.text()
    assert ahead == "10m – check", "the mark is not listed as still to come"
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    view.present(False)

    assert controller.has_failed is True
    assert view.runs[0]._status_text.text() == STATUS_FAILED_TEXT
    halted = _marks_panel(view).times.text()
    assert halted == "10m – check · not reached before the simulation error"

    monkeypatch.undo()
    view.present(False)

    assert _marks_panel(view).times.text() == halted


def test_a_failing_frame_restates_each_displayed_run_s_own_bookmark_standings(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When a trunk and its branch halt, the panel gives each run its own standing, not the trunk's.

    The branch ran up through a marked height of 0.50 xMAC alveolar that the
    trunk never reached. When every frame fails, both runs stop. The branch has
    still reached the mark, but the trunk now cannot reach it. So the mark's row
    names both runs. Suppose the halt gave every run the standings of the
    reference run, which here is the trunk. The two runs would then agree, so the
    panel would draw the row without naming either run (`PL-YHR3`).
    """

    view = _halted_branch_view(application)
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    view.present(False)

    assert all(run.controller.has_failed for run in view.runs)
    targets = _marks_panel(view).targets.text()
    failed = MARK_STANDING_COMPARED_TEXT[MarkStanding.NOT_REACHED_BEFORE_FAILURE]
    reached = MARK_STANDING_COMPARED_TEXT[MarkStanding.REACHED]

    assert f"{run_label(FIRST_RUN)} {failed}" in targets
    assert f"{run_label(SECOND_RUN)} {reached}" in targets


def test_a_bookmark_panel_that_cannot_be_restated_on_a_halt_lists_no_standing(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    """If restating the bookmark panel raises, the halt hides both listings and still takes effect.

    The restatement runs inside the halt path, where an exception would escape
    the render path's guard and reach the toolkit. So the restatement is guarded, as
    the fork panel's restatement is (`PL-MMNX`). A panel that cannot be restated
    shows no standing at all, rather than the last frame's standings (`PL-YHR3`).
    The next frame that draws shows both listings again.
    """

    controller = _paused_run_with_history()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(600.0), "check"))
    view = _shown_view(application, controller)
    panel = _marks_panel(view)
    assert panel.times.isHidden() is False

    def unanswerable(self: SimulationController) -> NoReturn:
        raise RuntimeError("the run could not say where it stands on its marks")

    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    monkeypatch.setattr(SimulationController, "bookmark_standings", unanswerable)
    capfd.readouterr()

    view.present(False)

    assert "Traceback" not in capfd.readouterr().err
    assert controller.has_failed is True
    assert view.runs[0]._status_text.text() == STATUS_FAILED_TEXT
    assert panel.times.isHidden() is True
    assert panel.targets.isHidden() is True

    monkeypatch.undo()
    view.present(False)

    assert panel.times.isHidden() is False
    assert panel.targets.isHidden() is False


def test_a_vanished_fork_instant_leaves_nothing_selected(application: QApplication) -> None:
    """`PL-J12Z`: a chosen instant that stops being a keyframe clears the control.

    This state is reachable without a reset. A keyframe collapses when a setting is
    returned to its previous value at the same instant, which is a learner
    changing their mind about a dial while paused. Falling back to the first
    entry would leave induction selected under a reader who had chosen a
    later decision point, and branch there on the next press.
    """

    trunk = SimulationController()
    trunk.start()
    _advance_to(trunk, 60.0)
    trunk.pause()
    original_flow = trunk.snapshot().fresh_gas_flow_l_min
    trunk.set_fresh_gas_flow(FreshGasFlow(original_flow + 2.0))
    case = BranchedCase(trunk)
    view = _case_view(application, case)
    panel = _fork_panel(view)

    assert case.fork_points_s == (0.0, 60.0)

    panel.point_selector.setCurrentIndex(panel.point_selector.findData(60.0))

    selected = panel.selected_point()
    assert selected is not None
    assert selected.instant_s == pytest.approx(60.0)

    trunk.set_fresh_gas_flow(FreshGasFlow(original_flow))
    view.present(False)

    assert case.fork_points_s == (0.0,)
    assert panel.selected_point() is None

    panel.take_button.click()

    assert len(view.runs) == 1
    assert case.branches == ()
    assert panel.notice.notice() == FORK_NOTHING_SELECTED_TEXT


def test_a_fork_instant_still_offered_stays_selected_when_the_offer_grows(
    application: QApplication,
) -> None:
    """The other half of `PL-J12Z`: a rebuilt list keeps a choice it still offers.

    A running trunk adds a keyframe at each setting change, and the selector
    is rebuilt when one appears. `set_offer` finds the reader's choice by
    `ForkPoint` equality in the new list rather than with `findData`, which
    matches a `CaseInstant` only by identity, so an equal one built anew is
    found nowhere and the choice would be dropped (`PL-CN5S`).
    """

    trunk = SimulationController()
    trunk.start()
    _advance_to(trunk, 60.0)
    trunk.pause()
    original_flow = trunk.snapshot().fresh_gas_flow_l_min
    trunk.set_fresh_gas_flow(FreshGasFlow(original_flow + 2.0))
    case = BranchedCase(trunk)
    view = _case_view(application, case)
    panel = _fork_panel(view)
    panel.point_selector.setCurrentIndex(panel.point_selector.findData(60.0))

    trunk.start()
    _advance_to(trunk, 120.0)
    trunk.pause()
    trunk.set_fresh_gas_flow(FreshGasFlow(original_flow))
    view.present(False)

    assert case.fork_points_s == (0.0, 60.0, 120.0)
    selected = panel.selected_point()
    assert selected is not None
    assert selected.instant_s == 60.0
    assert selected.mark is None


def test_a_cleared_fork_selection_stays_cleared_when_the_list_next_changes(
    application: QApplication,
) -> None:
    """`PL-J12Z`'s cleared selection lasts past the next rebuild, not for only one frame.

    Qt selects the first entry of an emptied selector as soon as it is
    refilled. So a rebuild that set no index put *induction* under a reader
    whose choice had just been cleared. That is the substitution the clear
    exists to refuse, arriving one setting change later. Since `PL-W4XQ`,
    each mark the trunk's clock reaches also causes a rebuild. That makes the
    later change the common case rather than a rare one.
    """

    trunk = SimulationController()
    trunk.start()
    _advance_to(trunk, 60.0)
    trunk.pause()
    original_flow = trunk.snapshot().fresh_gas_flow_l_min
    trunk.set_fresh_gas_flow(FreshGasFlow(original_flow + 2.0))
    case = BranchedCase(trunk)
    view = _case_view(application, case)
    panel = _fork_panel(view)
    panel.point_selector.setCurrentIndex(panel.point_selector.findData(60.0))
    trunk.set_fresh_gas_flow(FreshGasFlow(original_flow))
    view.present(False)

    assert panel.selected_point() is None

    trunk.start()
    _advance_to(trunk, 90.0)
    trunk.pause()
    trunk.set_fresh_gas_flow(FreshGasFlow(original_flow + 2.0))
    view.present(False)

    assert case.fork_points_s == (0.0, 90.0)
    assert panel.point_selector.count() == len(case.fork_points_s)
    assert panel.point_selector.currentIndex() == -1
    assert panel.selected_point() is None

    panel.take_button.click()

    assert case.branches == ()
    assert panel.notice.notice() == FORK_NOTHING_SELECTED_TEXT


def test_a_mark_set_behind_the_trunk_s_clock_is_offered_and_branched_at(
    application: QApplication,
) -> None:
    """`PL-W4XQ` end to end: paused past a mark, a learner branches there from the selector.

    The mark was set after the clock had passed it. So no step crossed it,
    the trunk holds no keyframe there, and the trunk is not on a halt. The
    other two ways of taking a branch refuse this case. The mark is offered
    beside the control events. It is labelled with the instant at which the
    branch will open, not the instant typed. The branch opens there, and the
    trunk stays as it was.
    """

    case, view, mark = _rewind_case(application)
    panel = _fork_panel(view)
    labels = [panel.point_selector.itemText(row) for row in range(panel.point_selector.count())]
    keyframes = case.fork_points_s

    assert case.trunk.snapshot().bookmark_halt is None
    assert _BEHIND_MARK_FORK_S not in keyframes
    assert labels == [
        format_elapsed(keyframes[0]),
        format_elapsed(keyframes[1]),
        _BEHIND_MARK_LABEL,
    ]
    assert format_elapsed(_BEHIND_MARK_S) not in _BEHIND_MARK_LABEL

    _select_fork_entry(view, _BEHIND_MARK_LABEL)

    selected = panel.selected_point()
    assert selected is not None
    assert selected.mark == mark
    assert selected.instant_s == _BEHIND_MARK_FORK_S

    panel.take_button.click()

    assert len(view.runs) == 2
    assert len(case.branches) == 1
    branch = case.branches[0]
    assert view.runs[1].controller is branch
    assert branch.began_at_s == _BEHIND_MARK_FORK_S
    assert branch.snapshot().elapsed_s == _BEHIND_MARK_FORK_S
    assert panel.notice.notice() is None
    # The trunk is read and not written: no keyframe is recorded where it was
    # branched, and its clock stays where it was paused.
    assert case.fork_points_s == keyframes
    assert case.trunk.snapshot().elapsed_s == pytest.approx(_REWIND_PAUSE_S)


def test_a_mark_still_ahead_of_the_trunk_s_clock_is_not_offered(application: QApplication) -> None:
    """The case holds no state at a mark the clock has not reached, so nothing branches there.

    A branch there would be a prediction drawn as a run. The mark stops the
    running case when it is reached, and then joins the selector. Until then
    the selector offers the control events and nothing else.
    """

    case, view, behind = _rewind_case(application)
    ahead = TimeBookmark(CaseInstant(600.0), "later")
    case.trunk.add_time_bookmark(ahead)
    view.present(False)

    selector = _fork_panel(view).point_selector
    offered = [selector.itemData(row) for row in range(selector.count())]
    labels = [selector.itemText(row) for row in range(selector.count())]

    assert ahead in case.trunk.snapshot().bookmarks.time_bookmarks
    assert ahead.instant_s not in offered
    assert labels == [
        *(format_elapsed(instant_s) for instant_s in case.fork_points_s),
        _BEHIND_MARK_LABEL,
    ]
    assert [point.bookmark for point in case.mark_fork_points] == [behind]


def test_a_selected_mark_is_cleared_not_moved_when_the_learner_unmarks_it(
    application: QApplication,
) -> None:
    """`PL-J12Z` for marks: an entry the learner removes takes the selection with it.

    Unmarking is how a mark leaves the list, as a collapsed keyframe is how a
    control event leaves it. Moving the choice to a neighbour, such as
    induction or the other mark beside it, would make the next press branch
    somewhere the learner did not choose. So the selector is left on nothing,
    and the press says so.
    """

    case, view, mark = _rewind_case(application)
    later = TimeBookmark(CaseInstant(100.0))
    case.trunk.add_time_bookmark(later)
    view.present(False)
    panel = _fork_panel(view)
    _select_fork_entry(view, _BEHIND_MARK_LABEL)

    dialog = _opened_bookmark_dialog(view)
    dialog.time_list.setCurrentRow(case.trunk.snapshot().bookmarks.time_bookmarks.index(mark))
    dialog.remove_time_button.click()

    labels = [panel.point_selector.itemText(row) for row in range(panel.point_selector.count())]

    assert case.trunk.snapshot().bookmarks.time_bookmarks == (later,)
    assert _BEHIND_MARK_LABEL not in labels
    assert f"{format_elapsed(100.0)}, on your mark" in labels
    assert panel.point_selector.currentIndex() == -1
    assert panel.selected_point() is None

    panel.take_button.click()

    assert case.branches == ()
    assert panel.notice.notice() == FORK_NOTHING_SELECTED_TEXT


def _widest_mark_entry_fits(application: QApplication) -> tuple[int, int]:
    """Give a dashboard's selector its widest mark entry and measure that entry against the field.

    The widest entry is found here rather than taken from
    `widest_fork_point_label`, so the test does not check that function
    against its own result. The font spaces its digits proportionally, so
    23h59m59.9s, the reading at the last step, is not the widest reading.
    Hours, minutes and seconds vary independently, so the widest value of
    each, put together, is the widest clock reading that `format_elapsed`
    can write. The test passes the entry through `fork_offer` and reads it
    back from the selector, rather than measuring it as a bare string.

    Returns:
        The entry's advance, which is its drawn width, and the width of the
        selector's text field. Both are in pixels, in the font that the
        selector is drawn in.
    """

    view = _case_view(application, _branched_case())
    panel = _fork_panel(view)
    metrics = panel.point_selector.fontMetrics()
    hours = max((f"{hour}h" for hour in range(10, 24)), key=metrics.horizontalAdvance)
    minutes = max((f"{minute}m" for minute in range(10, 60)), key=metrics.horizontalAdvance)
    seconds = max(
        (f"{whole}.{tenth}s" for whole in range(10, 60) for tenth in range(1, 10)),
        key=metrics.horizontalAdvance,
    )
    instant = CaseInstant(
        int(hours[:-1]) * SECONDS_PER_HOUR
        + int(minutes[:-1]) * SECONDS_PER_MINUTE
        + float(seconds[:-1])
    )

    assert format_elapsed(instant) == hours + minutes + seconds
    assert instant < MAXIMUM_ELAPSED_SIMULATION_TIME_S

    panel.set_offer(
        fork_offer(
            (CaseInstant(0.0),),
            marks=(MarkForkPoint(TimeBookmark(instant), instant),),
            comparing=None,
            here=None,
        ),
        None,
    )
    _select_fork_entry(view, f"{hours}{minutes}{seconds}, on your mark")
    option = QStyleOptionComboBox()
    panel.point_selector.initStyleOption(option)
    field = panel.point_selector.style().subControlRect(
        QStyle.ComplexControl.CC_ComboBox,
        option,
        QStyle.SubControl.SC_ComboBoxEditField,
        panel.point_selector,
    )

    return metrics.horizontalAdvance(panel.point_selector.currentText()), field.width()


def test_the_branch_selector_draws_its_widest_entry_whole(application: QApplication) -> None:
    """A mark's entry cut short would lose the words that say it is a mark.

    The selector has a fixed width. Its widest entry is the entry for a mark
    late in the supported run. So the test checks that the width fits that
    entry, in the font the selector is drawn in.
    """

    entry_px, field_px = _widest_mark_entry_fits(application)

    assert entry_px <= field_px


def test_the_branch_selector_fits_its_widest_entry_in_a_wider_face(
    application: QApplication,
) -> None:
    """The width still fits in a face and size that the container does not draw in (`PL-NC0D`).

    The application sets no font of its own, so the selector draws in the
    platform's default face and size. In DejaVu Sans at 16 px, the widest
    entry needs 228 px. The fixed 230 px width that this replaced left a
    text field of only 196 px, so the words "on your mark" were cut. The
    width is now measured from the selector's own font when it is built.
    """

    previous = application.font()
    wider = QFont("DejaVu Sans")
    wider.setPixelSize(16)
    application.setFont(wider)

    try:
        entry_px, field_px = _widest_mark_entry_fits(application)
    finally:
        application.setFont(previous)

    assert entry_px <= field_px
