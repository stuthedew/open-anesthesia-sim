"""The dashboard, driven headless against real runs.

These tests cover comparing a trunk and its branch: the lock, resets that drop a branch, and adding
a run.

`simulation_view_support.py` describes the whole suite.
"""

import re

import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QAbstractSlider, QApplication, QScrollArea

from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import (
    BRANCH_AGENT_LOCK_TEXT,
    BRANCH_RUN_INDEX,
    COMPARING_AGENT_LOCK_TEXT,
    MAX_DISPLAYED_RUNS,
    RESET_LABEL,
    SIMULATION_STEP_S,
    TRUNK_RUN_INDEX,
    comparing_fork_lock_text,
    fork_offer,
    run_label,
)
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.app.run_view import RunView
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.core.supported_ranges import CaseInstant
from tests.integration.simulation_view.simulation_view_support import (
    COMPARED,
    RUN_IDS,
    _branched_case,
    _case_view,
    _concentration,
    _fork_panel,
    _marks_panel,
    _opened_bookmark_dialog,
    _paused_run_with_history,
    _select_agent,
    _set_fresh_gas_flow,
    _settle,
    _shown_view,
    _steps,
    _take_fork,
)


def test_a_branch_shows_the_agent_chip_in_place_of_the_selector(application: QApplication) -> None:
    """`PL-QRD1`, the branch half: a branch carries the agent of the case it continues.

    `SimulationController.set_agent` refuses a branch outright (`PL-TFX5`),
    so a selector on its row would refuse every input it accepted. The chip
    says which lock is in force, and it is not the one a Pause would lift.
    """

    view = _case_view(application, _branched_case())
    _take_fork(view, 60.0)
    branch = view.runs[1]

    assert branch._agent_dropdown.isHidden() is True
    assert branch._agent_dropdown.isEnabled() is False
    assert branch._running_agent_display.isHidden() is False
    assert branch._running_agent_lock_text.text() == BRANCH_AGENT_LOCK_TEXT


def test_the_trunks_selector_is_locked_while_two_runs_are_shown(application: QApplication) -> None:
    """`PL-QRD1`, the trunk half: `set_agent` succeeds on a trunk and destroys the case.

    With a branch displayed and the trunk paused, the trunk's selector was
    enabled. Choosing another agent restarted the trunk and left
    `BranchedCase` listing a branch of a run that no longer existed.
    `assemble_chart_frame` then refused the frame over the shared MAC axis.
    So `_halt_every_run` failed both runs over an input to one of them. The
    switch is now refused before it reaches the controller.
    """

    case = _branched_case()
    view = _case_view(application, case)
    trunk = view.runs[0]

    assert trunk._agent_dropdown.isHidden() is False

    _take_fork(view, 60.0)

    assert trunk._agent_dropdown.isHidden() is True
    assert trunk._agent_dropdown.isEnabled() is False
    assert trunk._running_agent_lock_text.text() == COMPARING_AGENT_LOCK_TEXT
    assert trunk.snapshot().agent_id == "sevoflurane"

    trunk._reset_button.click()
    _settle(application)

    assert trunk._agent_dropdown.isHidden() is False
    assert trunk._running_agent_display.isHidden() is True


def test_resetting_the_trunk_ends_the_comparison(application: QApplication) -> None:
    """Reset is the way back to one run, and the case it leaves has no branches.

    The trunk has started over, so it never passed through the instant at
    which the branch was taken. A branch left on the chart would show two
    curves claiming one patient under two managements, when they no longer
    describe one patient.
    """

    case = _branched_case()
    view = _case_view(application, case)
    _take_fork(view, 60.0)

    assert len(view.runs) == 2

    view.runs[0]._reset_button.click()
    _settle(application)

    assert len(view.runs) == 1
    assert view.case is not None
    assert view.case is not case
    assert view.case.trunk is view.runs[0].controller
    assert view.case.branches == ()
    assert _concentration(view).legend._run_count == 1
    assert view.runs[0]._run_name_text.isHidden() is True
    assert _fork_panel(view).take_button.isHidden() is False
    assert _fork_panel(view).lock_text.isHidden() is True
    assert _fork_panel(view).notice.notice() is None
    # A branch just taken holds nothing, so the Reset asked nothing (`PL-W5WX`).
    assert view.runs[0]._reset_dialog is None


def test_a_refused_branch_does_not_survive_a_one_run_reset(application: QApplication) -> None:
    """`PL-75P5`: a refusal names an instant of the run the trunk's Reset has just ended.

    The one-run case is every case before a learner branches. The guard that
    spares a one-run dashboard its layout work once returned before the
    refusal was cleared. So the banner went on reporting an instant that the
    restarted run does not hold, since that run is back at induction.
    """

    case = _branched_case()
    view = _case_view(application, case)
    panel = _fork_panel(view)
    panel.set_offer(
        fork_offer(
            (CaseInstant(0.0), CaseInstant(30.0), CaseInstant(60.0)),
            marks=(),
            comparing=None,
            here=None,
        ),
        None,
    )
    panel.point_selector.setCurrentIndex(panel.point_selector.findData(30.0))
    panel.take_button.click()

    assert len(view.runs) == 1
    refusal = panel.notice.notice()
    assert refusal is not None
    assert "30" in refusal

    view.runs[TRUNK_RUN_INDEX]._reset_button.click()
    _settle(application)

    assert view.runs[TRUNK_RUN_INDEX].snapshot().elapsed_s == 0.0
    assert view._fork_refusal is None
    assert panel.notice.notice() is None


def test_a_one_run_reset_leaves_a_case_with_no_branches(application: QApplication) -> None:
    """The case is a record of the trunk's run, so its Reset rebuilds it whatever is drawn.

    A fork whose drawing raised leaves a branch that the case keeps but the
    dashboard does not draw (`PL-08SS`). The test builds such a branch by
    forking the case directly. It must not outlive the trunk's Reset as a
    branch of a run that no longer exists, merely because one run was on
    screen.
    """

    case = _branched_case()
    view = _case_view(application, case)
    case.fork_at(CaseInstant(60.0))

    assert len(view.runs) == 1
    assert len(case.branches) == 1

    view.runs[TRUNK_RUN_INDEX]._reset_button.click()
    _settle(application)

    assert view.case is not None
    assert view.case is not case
    assert view.case.trunk is view.runs[TRUNK_RUN_INDEX].controller
    assert view.case.branches == ()


def test_resetting_a_branch_leaves_the_comparison_standing(application: QApplication) -> None:
    """A branch's Reset returns it to its fork, and only the trunk's Reset starts a new case.

    The test checks that the lock is still there, because that is the part
    that surprises a learner (`PL-WG73`). The run they were trying to end has
    lost four steps of simulated case, and the control they were sent to
    press is still refused, under the same sentence.
    """

    case = _branched_case()
    view = _case_view(application, case)
    _take_fork(view, 60.0)
    branch = view.runs[BRANCH_RUN_INDEX]
    branch._start_button.click()
    _steps(branch, 4)
    branch._reset_button.click()
    _settle(application)

    assert len(view.runs) == 2
    assert view.case is case
    assert len(case.branches) == 1
    assert branch.snapshot().elapsed_s == pytest.approx(60.0)
    assert _fork_panel(view).lock_text.isHidden() is False
    assert _fork_panel(view).take_button.isHidden() is True


def _branch_holding_work(view: SimulationView, application: QApplication, work: str) -> RunView:
    """Take a branch at 60 s and give it one of the two kinds of work `has_recorded_run` checks.

    `elapsed` runs it four steps past its fork with nothing touched, and
    `change` records one fresh gas flow change at the fork with no time run.
    Either alone is work the trunk's Reset would discard.
    """

    _take_fork(view, 60.0)
    branch = view.runs[BRANCH_RUN_INDEX]

    if work == "elapsed":
        branch._start_button.click()
        _steps(branch, 4)
        branch._pause_button.click()
    else:
        _set_fresh_gas_flow(branch, 3.0)

    _settle(application)

    return branch


@pytest.mark.parametrize(
    ("work", "warning", "listed"),
    [
        (
            "elapsed",
            "Run 2 — branched at 1m and run to 1m0.4s, 1 recorded control change — will be "
            "discarded along with its chart history. This cannot be undone.",
            1,
        ),
        (
            "change",
            "Run 2 — branched at 1m, 2 recorded control changes — will be discarded along with "
            "its chart history. This cannot be undone.",
            2,
        ),
    ],
)
def test_resetting_the_trunk_asks_before_dropping_a_branch_that_holds_work(
    application: QApplication, work: str, warning: str, listed: int
) -> None:
    """Reset on Run 1 does not discard Run 2's work until the learner agrees (`PL-W5WX`).

    The `work` parameter takes the values `elapsed` and `change`, one for each
    condition that `has_recorded_run` checks. A question that checked only one
    of them would miss the other. The expected warning is a literal string.
    Four steps of 0.1 s from the fork at 60 s reach 1m0.4s on the case clock.
    In both cases the branch's "Control changes" panel lists the trunk's
    change at 1m, which the branch opened with. For `change`, it also lists
    the learner's change, recorded after the opened entry. The question
    counts what the panel lists (`PL-ZR49`).
    """

    case = _branched_case()
    view = _case_view(application, case)
    branch = _branch_holding_work(view, application, work)
    before = (branch.snapshot().elapsed_s, branch.controller.run_segments)

    view.runs[TRUNK_RUN_INDEX]._reset_button.click()
    _settle(application)

    dialog = view.runs[TRUNK_RUN_INDEX]._reset_dialog
    assert dialog is not None
    assert dialog.isVisible() is True
    assert dialog.title_label.text() == "Reset Run 1 and discard Run 2?"
    assert dialog.body_labels[1].text() == warning
    assert len(branch._control_timeline_text.text().splitlines()) == listed
    assert len(view.runs) == 2
    assert view.case is case
    assert (branch.snapshot().elapsed_s, branch.controller.run_segments) == before
    assert view.runs[TRUNK_RUN_INDEX].snapshot().elapsed_s == pytest.approx(60.0)


def test_resetting_the_trunk_asks_before_dropping_a_branch_set_back_to_the_earlier_flow(
    application: QApplication,
) -> None:
    """A branch that the learner set back to the trunk's earlier flow holds work (`PL-ZR49`).

    The trunk's fresh gas flow went from 4 to 2 L/min at 1m, and a branch is
    taken there. The branch opens at 2 L/min, which is what the dial said.
    The learner sets it back to 4 L/min at the fork. The branch's "Control
    changes" panel lists the trunk's change and then the learner's, and the
    trunk's Reset asks before it discards the branch. Both blind review
    passes of the rework found that the learner's change deleted the opened
    entry instead. The panel was then empty, and the trunk's Reset discarded
    the branch without asking.
    """

    case = _branched_case()
    view = _case_view(application, case)
    _take_fork(view, 60.0)
    branch = view.runs[BRANCH_RUN_INDEX]
    _set_fresh_gas_flow(branch, 4.0)
    _settle(application)

    assert branch.snapshot().fresh_gas_flow_l_min == 4.0
    assert len(branch._control_timeline_text.text().splitlines()) == 2

    view.runs[TRUNK_RUN_INDEX]._reset_button.click()
    _settle(application)

    dialog = view.runs[TRUNK_RUN_INDEX]._reset_dialog
    assert dialog is not None
    assert dialog.isVisible() is True
    assert dialog.body_labels[1].text() == (
        "Run 2 — branched at 1m, 2 recorded control changes — will be discarded along with "
        "its chart history. This cannot be undone."
    )
    assert len(view.runs) == 2
    assert view.case is case


def test_an_open_trunk_reset_question_follows_a_running_branch(application: QApplication) -> None:
    """The Reset question reports the branch's work as it is now (`PL-WM5P`).

    The question does not report the work as it was when it was asked.
    Before `PL-TPBH` a branch went on running while the trunk's question was
    open. The runs' ticks now hold while it is open, so the test moves the
    branch's controller directly, and the rewrite is kept as a guard. The
    test compares the warning with a literal string. Four steps of 0.1 s
    from the fork at 60 s reach 1m0.4s, and four more reach 1m0.8s. The one
    recorded change is the trunk's change at 1m. The branch opened with that
    change, and its "Control changes" panel lists it (`PL-ZR49`).
    """

    case = _branched_case()
    view = _case_view(application, case)
    branch = _branch_holding_work(view, application, "elapsed")
    trunk = view.runs[TRUNK_RUN_INDEX]
    branch._start_button.click()

    trunk._reset_button.click()
    dialog = trunk._reset_dialog
    assert dialog is not None
    assert "run to 1m0.4s" in dialog.body_labels[1].text()

    for _ in range(4):
        branch.controller.advance(SIMULATION_STEP_S)

    view.present(False)

    assert dialog.body_labels[1].text() == (
        "Run 2 — branched at 1m and run to 1m0.8s, 1 recorded control change — will be "
        "discarded along with its chart history. This cannot be undone."
    )
    assert dialog.title_label.text() == "Reset Run 1 and discard Run 2?"


def _one_tick_advance_s(run: RunView) -> float:
    """Step `run` by one tick and return how far its clock moved."""

    before = run.snapshot().elapsed_s
    run.step_tick()

    return run.snapshot().elapsed_s - before


@pytest.mark.parametrize("trunk_running", [True, False], ids=["running", "paused"])
def test_the_run_does_not_advance_while_a_reset_question_is_open(
    application: QApplication, trunk_running: bool
) -> None:
    """Every run holds while the trunk's Reset question is open, and resumes as it was (`PL-TPBH`).

    The question is window-modal, so the reader cannot press Pause while it
    is open. The project owner decided on 2026-10-31 that the runs hold and
    then carry on as they were. The branch is running throughout. The trunk
    is running in one case and paused in the other. After Keep, each run is
    in the state it was in before the question, at the same playback rate.
    """

    case = _branched_case()
    view = _case_view(application, case)
    branch = _branch_holding_work(view, application, "elapsed")
    trunk = view.runs[TRUNK_RUN_INDEX]
    branch._start_button.click()

    if trunk_running:
        trunk._start_button.click()

    tick_s = {run.run_id: _one_tick_advance_s(run) for run in view.runs}
    assert tick_s[branch.run_id] > 0.0
    assert (tick_s[trunk.run_id] > 0.0) is trunk_running

    trunk._reset_button.click()
    dialog = trunk._reset_dialog
    assert dialog is not None
    held_at = [run.snapshot().elapsed_s for run in view.runs]

    for run in view.runs:
        _steps(run, 10)

    assert [run.snapshot().elapsed_s for run in view.runs] == held_at
    assert [run.is_running for run in view.runs] == [trunk_running, True]

    dialog.keep_button.click()
    _settle(application)

    assert trunk._reset_dialog is None
    assert {run.run_id: _one_tick_advance_s(run) for run in view.runs} == pytest.approx(tick_s)
    assert [run.is_running for run in view.runs] == [trunk_running, True]


def test_a_running_run_holds_while_its_new_case_question_is_open(application: QApplication) -> None:
    """The question asked before a new agent discards the run holds it too (`PL-TPBH`)."""

    controller = _paused_run_with_history(60.0)
    controller.start()
    view = _shown_view(application, controller)
    run = view.runs[0]
    tick_s = _one_tick_advance_s(run)

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    held_at = run.snapshot().elapsed_s
    _steps(run, 10)

    assert run.snapshot().elapsed_s == held_at

    dialog.keep_button.click()
    _settle(application)

    assert run._new_case_dialog is None
    assert run.is_running
    assert _one_tick_advance_s(run) == pytest.approx(tick_s) != 0.0


def test_a_running_run_holds_while_a_workspace_question_is_open(application: QApplication) -> None:
    """A Workspace question blocks Pause as a Reset question does, so it holds the run too."""

    controller = _paused_run_with_history(60.0)
    controller.start()
    view = _shown_view(application, controller)
    run = view.runs[0]
    tick_s = _one_tick_advance_s(run)
    strip = view.tab_strip
    _restore, reset_all = strip.default_operations()
    assert reset_all.question is not None

    strip.choose(reset_all)
    question = strip.question
    assert question is not None
    held_at = run.snapshot().elapsed_s
    _steps(run, 10)

    assert run.snapshot().elapsed_s == held_at

    question.keep_button.click()
    _settle(application)

    assert strip.question is None
    assert _one_tick_advance_s(run) == pytest.approx(tick_s) != 0.0


def test_the_bookmark_editor_is_not_modal_and_holds_no_run(application: QApplication) -> None:
    """The bookmark editor leaves Pause reachable, so the runs go on (`PL-TPBH` blind review).

    `QDialog.open()` makes a dialog window-modal. The editor was shown that
    way, so it blocked every Pause button while the runs went on stepping,
    which is the defect `PL-TPBH` removes for the questions. The editor is
    meant to be non-modal, so it is now shown with `show()`.
    """

    controller = _paused_run_with_history(60.0)
    controller.start()
    view = _shown_view(application, controller)
    run = view.runs[0]

    _marks_panel(view).edit_button.click()
    _settle(application)
    dialog = view._bookmark_dialog
    assert dialog is not None
    assert dialog.isVisible()
    assert not dialog.isModal()
    assert dialog.windowModality() is Qt.WindowModality.NonModal
    assert _one_tick_advance_s(run) > 0.0

    run._pause_button.click()

    assert not run.is_running


def test_declining_the_trunks_reset_leaves_every_run_as_it_was(application: QApplication) -> None:
    """Keeping the branch keeps the trunk too: nothing is reset, and the comparison stays open."""

    case = _branched_case()
    view = _case_view(application, case)
    branch = _branch_holding_work(view, application, "elapsed")
    trunk = view.runs[TRUNK_RUN_INDEX]
    branch_before = (branch.snapshot().elapsed_s, branch.controller.run_segments)
    trunk_before = (trunk.snapshot().elapsed_s, trunk.controller.run_segments)

    trunk._reset_button.click()
    dialog = trunk._reset_dialog
    assert dialog is not None
    assert dialog.keep_button.text() == "Keep Run 2"
    dialog.keep_button.click()
    _settle(application)

    assert trunk._reset_dialog is None
    assert len(view.runs) == 2
    assert view.case is case
    assert (branch.snapshot().elapsed_s, branch.controller.run_segments) == branch_before
    assert (trunk.snapshot().elapsed_s, trunk.controller.run_segments) == trunk_before


def test_confirming_the_trunks_reset_starts_the_case_over_without_the_branch(
    application: QApplication,
) -> None:
    """Confirming does what the trunk's Reset did unasked before `PL-W5WX`."""

    case = _branched_case()
    view = _case_view(application, case)
    _branch_holding_work(view, application, "elapsed")
    trunk = view.runs[TRUNK_RUN_INDEX]

    trunk._reset_button.click()
    dialog = trunk._reset_dialog
    assert dialog is not None
    assert dialog.discard_button.text() == "Reset and discard Run 2"
    dialog.discard_button.click()
    _settle(application)

    assert trunk._reset_dialog is None
    assert len(view.runs) == 1
    assert view.case is not None
    assert view.case is not case
    assert view.case.branches == ()
    assert trunk.snapshot().elapsed_s == 0.0


def _chart_span_in_viewport(view: SimulationView) -> tuple[int, int, int]:
    """The chart's top and bottom edges in the page's viewport, and the viewport's height."""

    scroll = view.findChild(QScrollArea)
    assert scroll is not None, "the dashboard has no scroll area"
    viewport = scroll.viewport()
    chart = _concentration(view).chart
    top = chart.mapTo(viewport, QPoint(0, 0)).y()

    return top, top + chart.height(), viewport.height()


@pytest.mark.parametrize("door", ["selector", "here"])
def test_taking_a_branch_leaves_the_concentration_chart_in_view(
    application: QApplication, door: str
) -> None:
    """`PL-562Z`: the chart the learner branched to compare on is wholly on screen afterwards.

    At 1600 x 1000 the branch's readouts push the chart down to about
    y 869-1229 of a 1000 px viewport, measured with this scroll removed on
    2026-10-18. Both branch controls are pressed, because both are ways to
    ask for the comparison.
    """

    view = _case_view(application, _branched_case(), width_px=1600)

    if door == "selector":
        _take_fork(view, 60.0)
    else:
        _fork_panel(view).here_button.click()

    _settle(application)
    _settle(application)

    assert len(view.runs) == 2
    top, bottom, viewport_height = _chart_span_in_viewport(view)
    assert top >= 0
    assert bottom <= viewport_height


def test_the_page_stops_holding_the_chart_once_the_reader_scrolls(
    application: QApplication,
) -> None:
    """The scroll a branch makes is the dashboard's until the reader scrolls the page themselves.

    After that the reader owns the page. So a later change of layout does not
    scroll the page back. Here that change is a shorter window, which moves
    the chart. Since `PL-CBYS` the page scrolls only where the window is too
    small for the Areas' least heights, so the test opens a 700 px window.
    """

    view = _case_view(application, _branched_case(), width_px=1600, height_px=700)
    _take_fork(view, 60.0)
    _settle(application)
    scroll = view.findChild(QScrollArea)
    assert scroll is not None
    bar = scroll.verticalScrollBar()
    assert bar.value() > 0

    bar.triggerAction(QAbstractSlider.SliderAction.SliderToMinimum)
    view.resize(1600, 600)
    _settle(application)

    assert bar.value() == 0


def test_the_comparison_lock_names_the_run_whose_reset_ends_it(application: QApplication) -> None:
    """`PL-WG73` end to end: the words in the lock are on screen, on the button that works.

    `test_the_comparison_lock_names_a_control_the_learner_can_press` checks
    the sentence against what `run_label` and `RESET_LABEL` say. This test
    checks that the runs those names refer to are the ones drawn, and that
    each carries its name where a reader meets its Reset. It also checks that
    the Reset the sentence sends the reader to is the one that lifts the
    lock. Neither half is worth anything alone, because a name attributes a
    control only if the reader can find what it refers to.
    """

    view = _case_view(application, _branched_case())
    _take_fork(view, 60.0)

    lock = _fork_panel(view).lock_text.text()

    assert lock == comparing_fork_lock_text(COMPARED)

    for index, run in enumerate(view.runs):
        assert run._run_name_text.text() == run_label(RUN_IDS[index])
        assert run._run_name_text.isHidden() is False
        assert run._run_name_text.text() in lock
        assert run._reset_button.text() == RESET_LABEL
        assert run._reset_button.isHidden() is False

    # Find the run that the way out is about by reading the sentence as a
    # learner reads it, not by looking it up by position. A lock that named
    # both runs correctly but paired each with the other's outcome would pass
    # every assertion above. It would still send the reader to the button
    # that keeps the mode.
    way_out, _, _ = lock.partition(";")
    named = [run for run in view.runs if run._run_name_text.text() in way_out]

    assert len(named) == 1
    assert named[0] is view.runs[TRUNK_RUN_INDEX]

    named[0]._reset_button.click()
    _settle(application)

    assert len(view.runs) == 1
    assert _fork_panel(view).lock_text.isHidden() is True
    assert _fork_panel(view).take_button.isHidden() is False


def test_a_branch_added_while_the_dashboard_runs_gets_its_own_step_timer(
    application: QApplication,
) -> None:
    """`start_simulation_timer` started the runs that existed then, and this one did not exist.

    Without its own timer a branch would sit at its fork however often the
    learner pressed Start.
    """

    view = _case_view(application, _branched_case())

    _take_fork(view, 60.0)
    assert view.runs[1]._step_timer.isActive() is False

    view.runs[0]._reset_button.click()
    _settle(application)
    view.start_simulation_timer()

    try:
        _take_fork(view, 0.0)

        assert view.runs[1]._step_timer.isActive() is True
    finally:
        view.stop_timers()


def test_a_run_added_to_a_paused_dashboard_is_drawn_on_the_next_tick(
    application: QApplication,
) -> None:
    """`add_run` draws nothing, and the next render tick draws the run it added.

    A caller of the public method that did not present afterwards left the
    plot on the old run set while both legends already named the new one,
    because the tick drew only while a run was running or a frame was owed
    (`PL-0LG6`). The tick now reads the run set and the new run's unwritten
    record itself (`PL-X7D5`). A branch taken through the control still
    draws exactly once: its press draws the frame, and the tick after it
    finds nothing owed.
    """

    case = _branched_case()
    view = _case_view(application, case)
    presented = view.presented_frames

    view.add_run(case.fork_at(CaseInstant(60.0)))

    assert view.presented_frames == presented, "add_run drew a frame of its own"

    view.render_tick()

    assert view.presented_frames == presented + 1
    assert _concentration(view).chart.frame is not None
    assert len(_concentration(view).chart.frame.runs) == 2
    assert _concentration(view).chart.drawn_points(BRANCH_RUN_INDEX, RecordedQuantity.ALVEOLAR)[0]

    view.render_tick()

    assert view.presented_frames == presented + 1, "a frame drawn for nothing owed"

    taken = _case_view(application, _branched_case())
    presented = taken.presented_frames

    _take_fork(taken, 60.0)
    taken.render_tick()

    assert taken.presented_frames == presented + 1


def test_adding_a_third_run_is_refused(application: QApplication) -> None:
    """The cap belongs to the display, so it applies to the public method as well as the control."""

    view = _case_view(application, _branched_case())
    _take_fork(view, 60.0)

    with pytest.raises(
        ValueError,
        match=re.escape(f"the dashboard displays 1 to {MAX_DISPLAYED_RUNS} runs at once, not 3"),
    ):
        view.add_run(SimulationController())


def test_adding_a_run_on_another_agent_is_refused(application: QApplication) -> None:
    """One ×MAC ruler cannot describe two agents, whenever the second run arrives."""

    view = _case_view(application, _branched_case())

    with pytest.raises(
        ValueError,
        match=re.escape(
            "every displayed run must be on the same agent, because they share one MAC axis "
            "and one set of clinical references; the dashboard is showing sevoflurane and "
            "this run is on desflurane"
        ),
    ):
        view.add_run(SimulationController(agent_id="desflurane"))


def test_a_mark_added_after_a_fork_reaches_both_runs(application: QApplication) -> None:
    """The marks belong to the case, so the run added after construction is written too."""

    view = _case_view(application, _branched_case())
    _take_fork(view, 60.0)
    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(300.0)
    dialog.add_time_button.click()

    marked = [run.snapshot().bookmarks.time_bookmarks for run in view.runs]

    assert len(marked) == 2
    assert marked[0] == marked[1]
    assert [bookmark.instant_s for bookmark in marked[0]][-1] == pytest.approx(300.0)


def test_resetting_a_case_less_dashboards_first_run_keeps_the_others(
    application: QApplication,
) -> None:
    """`PL-LQ19`: a dashboard with no case has no branches, so Reset drops nothing.

    The runs of a case-less dashboard are independent trunks. The constructor
    accepts them, and the two-trunk tests build them. So the first run
    starting over says nothing about the second. Dropping the second would
    destroy a recorded run over an input to another one, through the action
    a reader uses to start a single run again.
    """

    other = _paused_run_with_history()
    view = _shown_view(application, SimulationController(), other)

    assert view.case is None
    assert len(view.runs) == 2

    view.runs[0]._reset_button.click()
    _settle(application)

    assert len(view.runs) == 2
    assert view.runs[1].controller is other
    assert view.runs[1].snapshot().elapsed_s == pytest.approx(60.0)
    assert view.runs[1].snapshot().has_recorded_run is True


def test_add_run_refuses_a_run_the_case_never_sanctioned(application: QApplication) -> None:
    """`PL-K5NY`: two curves on one axis claim one patient, so a stranger is refused.

    Every guard but this one passed a fresh controller on the displayed
    agent: it was placed as "Run 2", drawn in the same frame against the same
    ×MAC ruler and named by `run_label` exactly as a branch is, while the
    case went on holding one run. `CLAUDE.md` names the correct number under
    the wrong patient context as a failure of the value.
    """

    case = _branched_case()
    view = _case_view(application, case)
    stranger = SimulationController()

    with pytest.raises(
        ValueError,
        match=re.escape(
            "a displayed run must be a branch of the case on the dashboard, because two "
            "curves on one axis assert one patient under two managements; this run is a "
            "trunk of its own and was never branched from this case"
        ),
    ):
        view.add_run(stranger)

    assert len(view.runs) == 1
    assert stranger not in case.runs


def test_add_run_refuses_a_branch_of_another_case(application: QApplication) -> None:
    """A run that is somebody else's branch is refused, and the message says which."""

    view = _case_view(application, _branched_case())
    elsewhere = BranchedCase(_paused_run_with_history())
    foreign = elsewhere.fork_at(CaseInstant(60.0))

    with pytest.raises(ValueError, match=re.escape("opened at 60.0 s but belongs to another case")):
        view.add_run(foreign)

    assert len(view.runs) == 1


def test_a_dashboard_with_no_case_cannot_gain_a_run(application: QApplication) -> None:
    """A second run is a branch of the first, and loose runs have no case to branch."""

    view = _shown_view(application, SimulationController())

    with pytest.raises(
        ValueError,
        match=re.escape("this dashboard holds no case, so it has no branches to display"),
    ):
        view.add_run(SimulationController())

    assert len(view.runs) == 1
