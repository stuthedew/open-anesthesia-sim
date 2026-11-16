"""The dashboard, driven headless against real runs.

These tests cover a branch the case refuses, and how the refusal is shown.

`simulation_view_support.py` describes the whole suite.
"""

from typing import NoReturn

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication, QWidget

from anesthesia_sim.app import run_presentation as run_presentation_module
from anesthesia_sim.app.bookmarks import MacTarget, TimeBookmark
from anesthesia_sim.app.controller import MarkForkPoint
from anesthesia_sim.app.dashboard_frame import (
    FORK_NOTHING_SELECTED_TEXT,
    HERE_FORK_LABEL_TEMPLATE,
    STATUS_FAILED_TEXT,
    ForkPoint,
    fork_offer,
)
from anesthesia_sim.app.formatting import format_elapsed
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.core.concentration import MacMultiple
from anesthesia_sim.core.supported_ranges import CaseInstant
from tests.integration.simulation_view.simulation_view_support import (
    _branched_case,
    _case_view,
    _fork_panel,
    _halted_trunk_case,
    _opened_bookmark_dialog,
    _paused_run_with_history,
    _read_the_alveolar_quotient_as,
    _select_agent,
    _select_fork_entry,
    _set_fresh_gas_flow,
    _settle,
    _shown_view,
    _take_fork,
)


@pytest.mark.parametrize("door", ["take", "here"])
def test_a_fork_on_a_run_whose_snapshot_refuses_keeps_no_branch(
    application: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
    door: str,
) -> None:
    """A fork on a trunk whose snapshot raises ends in the halt, and the case keeps no branch.

    The case used to keep the branch before `add_run` read its snapshot to draw it. On a
    run whose snapshot rejects a value (`PL-7DJK`), that read raised out of the slot. The
    press showed nothing and left a branch that was kept but never drawn. A second press
    kept a second one (`PL-08SS`). Both fork handlers now read the trunk's snapshot first,
    through the halt.
    """

    case = _branched_case()
    view = _case_view(application, case)
    _read_the_alveolar_quotient_as(monkeypatch, 1.0000001)
    capfd.readouterr()

    if door == "take":
        _take_fork(view, 60.0)
    else:
        _fork_panel(view).here_button.click()

    assert "Traceback" not in capfd.readouterr().err
    assert case.branches == ()
    assert len(view.runs) == 1
    assert case.trunk.has_failed is True
    assert view.runs[0]._status_text.text() == STATUS_FAILED_TEXT


@pytest.mark.parametrize("kind", ["time", "target"])
def test_removing_a_mark_on_a_run_whose_snapshot_refuses_restates_the_halt(
    application: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
    kind: str,
) -> None:
    """Pressing Remove in the marks editor on a run whose snapshot raises shows the halt.

    Both remove handlers read the reference run's snapshot to find the selected mark.
    They used to read it outside the code that halts the run on an error. So on a run
    whose snapshot rejects a value, the press raised out of the slot. The button did
    nothing, and nothing on screen said why (`PL-F2T2`). The read now goes through the
    halt, so the run shows as stopped and the mark stays where it was.
    """

    controller = _paused_run_with_history()
    time_mark = TimeBookmark(CaseInstant(30.0), "check")
    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.5))
    controller.add_time_bookmark(time_mark)
    controller.add_mac_target(target)
    view = _shown_view(application, controller)
    dialog = _opened_bookmark_dialog(view)
    listing, remove = (
        (dialog.time_list, dialog.remove_time_button)
        if kind == "time"
        else (dialog.target_list, dialog.remove_target_button)
    )
    listing.setCurrentRow(0)
    _read_the_alveolar_quotient_as(monkeypatch, 1.0000001)
    capfd.readouterr()

    remove.click()

    assert "Traceback" not in capfd.readouterr().err
    assert controller.has_failed is True
    assert view.runs[0]._status_text.text() == STATUS_FAILED_TEXT
    assert controller.bookmarks.time_bookmarks == (time_mark,)
    assert controller.bookmarks.mac_targets == (target,)


def test_a_drag_whose_readouts_refuse_halts_the_run(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    """A dial whose readouts cannot be built after a drag halts the run, and says so on screen.

    After a dragged dial is applied, the run's own labels are rewritten at once from a
    snapshot. `setting_readouts` raises there for a control that can offer no setting.
    Only the apply step was inside the guard. So the exception escaped the slot, and the
    run still showed "Paused" with no banner (`PL-M3M2`). The exception now halts the run
    first. The dial write in the halt raises again, and that second exception still
    reaches the console.
    """

    controller = _paused_run_with_history()
    view = _shown_view(application, controller)
    run = view.runs[0]

    def no_setting(settings: object) -> NoReturn:
        raise ValueError("this control can offer no setting")

    monkeypatch.setattr(run_presentation_module, "setting_readouts", no_setting)
    capfd.readouterr()

    _set_fresh_gas_flow(run, 4.0)

    assert controller.has_failed is True
    assert run._status_text.text() == STATUS_FAILED_TEXT
    assert run._start_button.isEnabled() is False
    notice = run._notice_text.notice()
    assert notice is not None
    assert "can offer no setting" in notice


def test_unmarking_the_mark_the_trunk_stopped_on_leaves_the_fork_here(
    application: QApplication,
) -> None:
    """Unmarking ends the halt and not the pause, so the control stays and drops the mark.

    The run stays where it stopped either way, and a learner who unmarks the
    instant they stopped on can still branch at it. What changes is that no
    mark stopped the run there any more, so the label stops saying one did.
    """

    case, view = _halted_trunk_case(application)
    halted_s = case.trunk.snapshot().elapsed_s
    mark = case.trunk.snapshot().bookmarks.time_bookmarks[0]
    case.trunk.remove_time_bookmark(mark)
    view.present(False)

    assert case.trunk.snapshot().bookmark_halt is None
    assert _fork_panel(view).here_button.text() == HERE_FORK_LABEL_TEMPLATE.format(
        instant=format_elapsed(halted_s)
    )

    _fork_panel(view).here_button.click()

    assert len(case.branches) == 1
    assert case.branches[0].began_at_s == halted_s


def test_a_branch_the_case_refuses_is_reported_and_adds_no_run(application: QApplication) -> None:
    """`resumed_at` refuses an instant that is not a keyframe rather than approximating.

    The control cannot offer such an instant, because `fork_offer` builds the
    offer from `fork_points_s`. So the test hands the panel an offer that
    lists one, the way a frame hands it the real offer, to reach the guard
    behind it. A refusal leaves the case and the display untouched and says
    which instant was refused.
    """

    case = _branched_case()
    view = _case_view(application, case)
    panel = _fork_panel(view)
    unkeyframed = ForkPoint(CaseInstant(30.0), format_elapsed(30.0), None)
    panel.set_offer(
        fork_offer(
            (CaseInstant(0.0), unkeyframed.instant_s, CaseInstant(60.0)),
            marks=(),
            comparing=None,
            here=None,
        ),
        None,
    )
    panel.point_selector.setCurrentIndex(panel.point_selector.findData(30.0))

    assert panel.selected_point() == unkeyframed
    assert unkeyframed.instant_s not in case.fork_points_s

    panel.take_button.click()

    assert len(view.runs) == 1
    assert case.branches == ()
    notice = panel.notice.notice()
    assert notice is not None
    assert "30" in notice


def test_a_mark_branch_the_case_refuses_is_reported_and_adds_no_run(
    application: QApplication,
) -> None:
    """A branch taken at a mark asks the case again on the press, and a refusal reaches the notice.

    An entry can outlive what it offers, by the gap between a frame and a
    press. So `_handle_fork` hands the mark back to the case rather than
    trusting the entry. Here the panel holds an entry for a mark that the
    trunk does not hold. An unmark that lands in that gap leaves such an
    entry behind. `fork_at_mark` refuses it and names the instant, rather
    than branching anywhere near it.
    """

    case = _branched_case()
    view = _case_view(application, case)
    panel = _fork_panel(view)
    unmarked = TimeBookmark(CaseInstant(30.0), "since removed")
    panel.set_offer(
        fork_offer(
            case.fork_points_s,
            marks=(MarkForkPoint(unmarked, CaseInstant(300 * 0.1)),),
            comparing=None,
            here=None,
        ),
        None,
    )
    _select_fork_entry(view, f"{format_elapsed(30.0)}, on your mark")

    selected = panel.selected_point()
    assert selected is not None
    assert selected.mark == unmarked
    assert case.trunk.snapshot().bookmarks.time_bookmarks == ()

    panel.take_button.click()

    assert len(view.runs) == 1
    assert case.branches == ()
    notice = panel.notice.notice()
    assert notice is not None
    assert "no time bookmark stands at 30.0 s" in notice


def test_a_branch_control_with_nothing_selected_says_so(application: QApplication) -> None:
    """A press that cannot name an instant is reported rather than ignored."""

    view = _case_view(application, _branched_case())
    _fork_panel(view).point_selector.clear()
    _fork_panel(view).take_button.click()

    assert len(view.runs) == 1
    assert _fork_panel(view).notice.notice() == FORK_NOTHING_SELECTED_TEXT


def test_a_refused_branch_shows_its_reason_between_the_selector_and_the_here_button(
    application: QApplication,
) -> None:
    """The reason for a refused press is the row under the button that was pressed (`PL-9YPR`).

    As the panel's last row, the reason fell below the fold of a short Area,
    under the "Branch here" row. A refused press then changed nothing that a
    learner could see.
    """

    view = _case_view(application, _branched_case())
    panel = _fork_panel(view)
    panel.point_selector.setCurrentIndex(-1)
    panel.take_button.click()
    _settle(application)

    assert panel.notice.notice() == FORK_NOTHING_SELECTED_TEXT
    assert panel.here_button.isHidden() is False

    def top(widget: QWidget) -> int:
        return widget.mapTo(panel, QPoint(0, 0)).y()

    assert top(panel.take_button) < top(panel.notice) < top(panel.here_button)


def test_an_agent_change_clears_the_fork_refusal_notice(application: QApplication) -> None:
    """`PL-BM6X`: an agent change clears a branch-panel notice about the case it ended.

    An agent change on the trunk starts a new case, as Reset does. Until
    `PL-BM6X`, only Reset told the dashboard so, and the branch panel went on
    saying "Select an instant to branch at" about a case no longer on screen.
    Both ways of changing the agent are checked: a run that has recorded
    something asks first, and one that has recorded nothing switches at once.
    """

    view = _case_view(application, _branched_case())
    trunk = view.runs[0]
    _fork_panel(view).point_selector.clear()
    _fork_panel(view).take_button.click()

    assert _fork_panel(view).notice.notice() == FORK_NOTHING_SELECTED_TEXT

    _select_agent(trunk, "desflurane")
    dialog = trunk._new_case_dialog
    assert dialog is not None
    dialog.discard_button.click()

    assert trunk.controller.agent_id == "desflurane"
    assert _fork_panel(view).notice.notice() is None

    _fork_panel(view).point_selector.clear()
    _fork_panel(view).take_button.click()

    assert _fork_panel(view).notice.notice() == FORK_NOTHING_SELECTED_TEXT
    assert trunk.controller.snapshot().has_recorded_run is False

    _select_agent(trunk, "isoflurane")

    assert trunk._new_case_dialog is None
    assert trunk.controller.agent_id == "isoflurane"
    assert _fork_panel(view).notice.notice() is None
