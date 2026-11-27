"""The dashboard, driven headless against real runs.

These tests cover bookmarks.

`simulation_view_support.py` describes the whole suite.
"""

from typing import NoReturn

import pytest
from PySide6.QtCore import QEvent, QPoint
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel, QListWidget, QPushButton, QWidget

from anesthesia_sim.app import simulation_view as simulation_view_module
from anesthesia_sim.app.area_layout import ViewScroll
from anesthesia_sim.app.bookmarks import MacTarget, MarkStanding, TimeBookmark
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import (
    MARK_STANDING_COMPARED_TEXT,
    MARK_STANDING_TEXT,
    MARK_STILL_RUNNING_TEXT,
    NO_MAC_TARGETS_TEXT,
    NO_TIME_BOOKMARKS_TEXT,
    STATUS_FAILED_TEXT,
    MarkListing,
    run_label,
)
from anesthesia_sim.app.formatting import format_elapsed, mac_multiple
from anesthesia_sim.app.qt_widgets import BookmarksPanel, MarkEditor, MarkList
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.theme import MARK_ROW_BULLET
from anesthesia_sim.app.view_registry import AGENT_ACCOUNTING, BOOKMARKS
from anesthesia_sim.app.views import BookmarksView
from anesthesia_sim.core.concentration import MacMultiple, fraction_from_percent
from anesthesia_sim.core.supported_ranges import CaseInstant
from anesthesia_sim.layout.shipped import shipped_workspaces
from anesthesia_sim.layout.tree import AreaId
from tests.integration.announcement_support import ASSERTIVE, Announcement, record_announcements
from tests.integration.simulation_view.simulation_view_support import (
    FIRST_RUN,
    SECOND_RUN,
    _advance_to,
    _branched_case,
    _case_view,
    _failing_assembly,
    _halted_branch_view,
    _mark_editor,
    _marks_panel,
    _paused_run_with_history,
    _real_step_failure,
    _settle,
    _shown_view,
    _take_fork,
)


def test_a_dashboard_opens_with_both_collections_listed_as_empty(application: QApplication) -> None:
    view = _shown_view(application, SimulationController())

    assert _marks_panel(view).times.text() == NO_TIME_BOOKMARKS_TEXT
    assert _marks_panel(view).targets.text() == NO_MAC_TARGETS_TEXT


def test_an_instant_entered_in_the_editor_is_listed_with_the_marks(
    application: QApplication,
) -> None:
    view = _shown_view(application, SimulationController())
    editor = _mark_editor(view)
    editor.instant_spin.setValue(600)
    editor.time_label_edit.setText("intubation")
    editor.add_time_button.click()

    assert "intubation" in _marks_panel(view).times.text()
    assert len(_marks_panel(view).times.rows) == 1


def test_the_entered_instant_is_restated_in_the_form_the_clock_uses(
    application: QApplication,
) -> None:
    # The spin box states one unit and the clock states three, so the editor
    # carries the conversion rather than leaving it to the reader.
    view = _shown_view(application, SimulationController())
    editor = _mark_editor(view)
    editor.instant_spin.setValue(600)

    assert editor.instant_preview.text() == format_elapsed(600)


def test_a_target_entered_in_the_editor_names_its_compartment_and_height(
    application: QApplication,
) -> None:
    view = _shown_view(application, SimulationController())
    editor = _mark_editor(view)
    editor.compartment_combo.setCurrentIndex(
        editor.compartment_combo.findData(RecordedQuantity.VESSEL_RICH.value)
    )
    editor.height_spin.setValue(0.8)
    editor.add_target_button.click()

    listed = _marks_panel(view).targets.text()

    assert listed == "Vessel-rich 0.80 ×MAC"


def test_the_compartment_picker_offers_the_six_drawn_compartments_and_no_ratio(
    application: QApplication,
) -> None:
    # `WASH_IN_RATIO` is a quotient rather than a concentration, so a multiple
    # of MAC of it is not a quantity the model holds.
    view = _shown_view(application, SimulationController())
    editor = _mark_editor(view)
    offered = [
        editor.compartment_combo.itemData(row) for row in range(editor.compartment_combo.count())
    ]

    assert offered == [quantity.value for quantity in COMPARTMENT_QUANTITIES]
    assert RecordedQuantity.WASH_IN_RATIO.value not in offered


def test_the_height_control_stops_at_what_the_running_agent_can_reach(
    application: QApplication,
) -> None:
    # No compartment exceeds the delivered concentration, and the vaporizer
    # limits that. So no run of this agent could cross a target above it. The
    # control refuses such a target rather than reporting it afterwards.
    controller = SimulationController()
    view = _shown_view(application, controller)
    editor = _mark_editor(view)
    snapshot = controller.snapshot()
    reachable = mac_multiple(
        fraction_from_percent(snapshot.max_delivered_concentration_percent),
        snapshot.agent_mac_percent,
    )

    # Sevoflurane's 8% maximum over its 1.80% MAC is 4.444 MAC. The control
    # holds two decimals, so it stops at 4.44, which a run can still reach.
    assert reachable == pytest.approx(8.0 / 1.8)
    assert editor.height_spin.maximum() == pytest.approx(4.44)
    assert editor.height_spin.maximum() <= reachable

    editor.height_spin.setValue(reachable * 2.0)

    assert editor.height_spin.value() == pytest.approx(4.44)


def test_the_height_control_rounds_its_maximum_down_for_desflurane(
    application: QApplication,
) -> None:
    """The control offers no height above what desflurane's vaporizer can reach (`PL-LBVN`).

    Desflurane's 18% maximum over its 6.6% MAC is 2.727 MAC, worked here by
    hand. A spin box rounds its maximum to the nearest value it can show, which
    is 2.73, so the control used to offer a target that no desflurane run can
    cross. It now stops at 2.72.
    """

    controller = SimulationController(agent_id="desflurane")
    view = _shown_view(application, controller)
    editor = _mark_editor(view)
    snapshot = controller.snapshot()
    reachable = mac_multiple(
        fraction_from_percent(snapshot.max_delivered_concentration_percent),
        snapshot.agent_mac_percent,
    )

    assert reachable == pytest.approx(18.0 / 6.6)
    assert editor.height_spin.maximum() == pytest.approx(2.72)
    assert editor.height_spin.maximum() <= reachable

    editor.height_spin.setValue(reachable)

    assert editor.height_spin.value() == pytest.approx(2.72)


def test_a_mark_added_from_the_dashboard_reaches_every_displayed_run(
    application: QApplication,
) -> None:
    # The marks belong to the case. Writing to every run makes it impossible
    # to compare two runs at two different heights because a user typed
    # one of them twice.
    first = SimulationController()
    second = SimulationController()
    view = _shown_view(application, first, second)
    editor = _mark_editor(view)
    editor.instant_spin.setValue(600)
    editor.add_time_button.click()

    assert first.snapshot().bookmarks == second.snapshot().bookmarks
    assert len(first.snapshot().bookmarks.time_bookmarks) == 1


def test_every_displayed_run_carries_the_same_marks_after_an_add_and_a_removal(
    application: QApplication,
) -> None:
    first = SimulationController()
    second = SimulationController()
    view = _shown_view(application, first, second)
    editor = _mark_editor(view)

    for instant_s in (120, 600):
        editor.instant_spin.setValue(instant_s)
        editor.add_time_button.click()

    _marks_panel(view).times.rows[0].remove_button.click()

    assert first.snapshot().bookmarks == second.snapshot().bookmarks
    assert [mark.instant_s for mark in first.snapshot().bookmarks.time_bookmarks] == [600.0]


def test_a_row_s_remove_button_removes_that_row_s_mark_and_no_other(
    application: QApplication,
) -> None:
    """Each listed mark's own Remove button removes that mark, from every run (`PL-G1JM`).

    Three instants and three heights are marked, and the middle row of each
    list is removed. A removal that took the wrong row, or every row after
    it, would leave a different pair of marks.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    editor = _mark_editor(view)
    panel = _marks_panel(view)

    for instant_s in (300, 600, 900):
        editor.instant_spin.setValue(instant_s)
        editor.add_time_button.click()

    for height_mac in (0.5, 1.0, 1.5):
        editor.height_spin.setValue(height_mac)
        editor.add_target_button.click()

    panel.times.rows[1].remove_button.click()
    panel.targets.rows[1].remove_button.click()
    bookmarks = controller.snapshot().bookmarks

    assert [mark.instant_s for mark in bookmarks.time_bookmarks] == [300.0, 900.0]
    assert [float(mark.mac_multiple) for mark in bookmarks.mac_targets] == [0.5, 1.5]
    assert len(panel.times.rows) == len(panel.targets.rows) == 2
    assert editor.add_time_notice.notice() is None
    assert panel.times.remove_notice.notice() is None


def test_a_double_click_on_a_remove_button_removes_one_mark(application: QApplication) -> None:
    """The second press of a double-click lands on the mark that moved up, and removes nothing.

    After a removal the mark below moves up into the pressed row, under the
    pointer. A blind review of `PL-G1JM` found that a double-click then took
    two marks from every run. A press within the platform's double-click
    interval of the last removal from that list is ignored, and a press after
    it removes the mark the row then shows.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    editor = _mark_editor(view)

    for instant_s in (300, 600, 900):
        editor.instant_spin.setValue(instant_s)
        editor.add_time_button.click()

    times = _marks_panel(view).times
    times.rows[0].remove_button.click()
    times.rows[0].remove_button.click()

    assert [mark.instant_s for mark in controller.bookmarks.time_bookmarks] == [600.0, 900.0]

    QTest.qWait(QApplication.doubleClickInterval() + 50)
    times.rows[0].remove_button.click()

    assert [mark.instant_s for mark in controller.bookmarks.time_bookmarks] == [900.0]


def test_the_tab_key_visits_the_remove_buttons_before_the_forms_below_them(
    application: QApplication,
) -> None:
    """Tab goes down the View: each time mark's Remove, each target's Remove, then the forms.

    The Remove buttons are built after the forms, when marks are added, so
    an order taken from when each widget was built would put them after the
    forms. A target is added before a time mark here, so that order would
    also put the target's button first. A blind review of `PL-G1JM` expected
    both. Qt placed each new button with the other widgets of its own list
    instead, and this test holds that order.
    """

    view = _shown_view(application, SimulationController())
    editor = _mark_editor(view)
    editor.height_spin.setValue(0.8)
    editor.add_target_button.click()
    editor.instant_spin.setValue(600)
    editor.add_time_button.click()
    panel = _marks_panel(view)
    expected = [
        panel.times.rows[0].remove_button,
        panel.targets.rows[0].remove_button,
        editor.instant_spin,
        editor.time_label_edit,
        editor.add_time_button,
        editor.compartment_combo,
    ]
    wanted = {id(widget) for widget in expected}
    visited: list[QWidget] = []
    widget = expected[0]

    # The chain also holds widgets inside these controls, such as a spin
    # box's own text field, so the walk keeps only the controls listed. The
    # limit makes a chain that never reaches them all fail instead of hang.
    for _ in range(len(view.findChildren(QWidget))):
        if id(widget) in wanted:
            visited.append(widget)

        if len(visited) == len(expected):
            break

        widget = widget.nextInFocusChain()

    assert visited == expected


def test_each_remove_button_names_its_mark_to_a_screen_reader(application: QApplication) -> None:
    """Every Remove button reads as one word, so its accessible name says which mark it removes.

    The names are built from the marks the test adds, not read from the rows.
    """

    view = _shown_view(application, SimulationController())
    editor = _mark_editor(view)

    for instant_s, name in ((300, "induction"), (600, "incision")):
        editor.instant_spin.setValue(instant_s)
        editor.time_label_edit.setText(name)
        editor.add_time_button.click()

    names = [row.remove_button.accessibleName() for row in _marks_panel(view).times.rows]

    assert [row.remove_button.text() for row in _marks_panel(view).times.rows] == ["Remove"] * 2
    assert names[0].startswith("Remove 5m – induction")
    assert names[1].startswith("Remove 10m – incision")


def test_marking_one_instant_twice_is_refused_and_says_why(application: QApplication) -> None:
    controller = SimulationController()
    view = _shown_view(application, controller)
    editor = _mark_editor(view)
    editor.instant_spin.setValue(600)
    editor.add_time_button.click()
    editor.add_time_button.click()

    notice = editor.add_time_notice.notice()

    assert notice is not None
    assert "marked once" in notice
    assert len(controller.snapshot().bookmarks.time_bookmarks) == 1


def test_a_refused_target_says_why_under_the_target_s_own_add_button(
    application: QApplication,
) -> None:
    """A target that every run refuses is explained under the Add button of the target form.

    The refusal comes from the runs, not from the form, so it reaches the
    editor through the code that writes a mark to every run. That code shows
    it under the button that asked (`PL-CHX0`). Shown under the time form, it
    would be out of sight of the button the reader pressed.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    editor = _mark_editor(view)
    editor.height_spin.setValue(1.0)
    editor.add_target_button.click()
    editor.add_target_button.click()

    notice = editor.add_target_notice.notice()

    assert notice is not None
    assert "marked once" in notice
    assert editor.add_time_notice.notice() is None
    assert len(controller.snapshot().bookmarks.mac_targets) == 1


def test_an_accepted_mark_clears_the_refusal_before_it(application: QApplication) -> None:
    """Once an edit is accepted, the refusal of the edit before it is no longer shown.

    A refusal left on screen after the next mark was added would tell the
    reader that the mark they just added was refused.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    editor = _mark_editor(view)
    editor.instant_spin.setValue(600)
    editor.add_time_button.click()
    editor.add_time_button.click()

    assert editor.add_time_notice.notice() is not None

    editor.instant_spin.setValue(900)
    editor.add_time_button.click()

    assert editor.add_time_notice.notice() is None
    assert [mark.instant_s for mark in controller.bookmarks.time_bookmarks] == [600.0, 900.0]


def test_a_mark_edited_after_a_fork_reaches_the_branch_too(application: QApplication) -> None:
    """The invariant the marks panel now rests on, in the one shape `main` produces.

    `bookmark_panel` reads the reference run's mark *set*, and every run's
    standings against that set. So a branch whose set had drifted from the
    trunk's no longer quietly draws the trunk's answer. Instead
    `BookmarkStandings` refuses the lookup, `present` catches the refusal, and
    the whole dashboard halts. That is the right direction under `CLAUDE.md`'s
    safety-critical standard, and it makes the invariant matter in a way it
    did not before.

    The three tests that check the invariant build two separate trunks. That
    is a configuration `main()` cannot produce, because it opens one trunk and
    a `BranchedCase`. This test walks through the real configuration: a fork,
    then an add and a removal from the dashboard. `_branch_from` copies the
    set at the fork, and `_apply_to_every_run` has to keep the two sets in
    step afterwards.
    """

    case = _branched_case()
    view = _case_view(application, case)
    _take_fork(view, 60.0)
    trunk, branch = (run.controller for run in view.runs)

    editor = _mark_editor(view)
    editor.instant_spin.setValue(600)
    editor.add_time_button.click()

    assert trunk.snapshot().bookmarks == branch.snapshot().bookmarks
    assert len(branch.snapshot().bookmarks.time_bookmarks) == 1

    editor.compartment_combo.setCurrentIndex(
        editor.compartment_combo.findData(RecordedQuantity.VESSEL_RICH.value)
    )
    editor.height_spin.setValue(0.8)
    editor.add_target_button.click()

    assert trunk.snapshot().bookmarks == branch.snapshot().bookmarks

    _marks_panel(view).times.rows[0].remove_button.click()

    assert trunk.snapshot().bookmarks == branch.snapshot().bookmarks
    assert branch.snapshot().bookmarks.time_bookmarks == ()

    # And the panel still draws, which is what the refusal above would stop.
    view.present(False)

    assert _marks_panel(view).targets.text().startswith("Vessel-rich")


def test_a_refusal_leaves_every_run_carrying_the_same_marks(application: QApplication) -> None:
    # The refusal fires on the second run rather than the first only if the
    # two runs have drifted apart. This checks that they have not, which is
    # the invariant that the write-to-every-run path exists for.
    first = SimulationController()
    second = SimulationController()
    view = _shown_view(application, first, second)
    editor = _mark_editor(view)
    editor.instant_spin.setValue(600)
    editor.add_time_button.click()
    editor.add_time_button.click()

    assert first.snapshot().bookmarks == second.snapshot().bookmarks


def test_a_name_field_is_cleared_after_a_mark_is_added_and_the_value_is_not(
    application: QApplication,
) -> None:
    # Adding a second mark near the first is the common case, so the instant
    # stays. A reused name would give two marks the same name, so the name is
    # cleared.
    view = _shown_view(application, SimulationController())
    editor = _mark_editor(view)
    editor.instant_spin.setValue(600)
    editor.time_label_edit.setText("intubation")
    editor.add_time_button.click()

    assert editor.time_label_edit.text() == ""
    assert editor.instant_spin.value() == 600


def _shown_texts(panel: BookmarksPanel) -> list[str]:
    """Every line of text the panel shows: each label, each button and each row of a list widget.

    A list widget is read as well as the labels, because the marks were once
    listed a second time in one (`PL-G1JM`).
    """

    texts: list[str] = []

    for child in panel.findChildren(QWidget):
        if not isinstance(child, QLabel | QPushButton | QListWidget):
            continue

        if not child.isVisibleTo(panel):
            continue

        if isinstance(child, QListWidget):
            texts.extend(child.item(row).text() for row in range(child.count()))
        else:
            texts.append(child.text())

    return texts


def test_the_bookmarks_view_lists_each_mark_once(application: QApplication) -> None:
    """A mark's name appears once in the Bookmarks View, on its row with its Remove button.

    The forms used to hold a second, selectable copy of each list, so every
    mark was shown twice in a View that is short at 1366 by 768 (`PL-G1JM`).
    """

    view = _shown_view(application, SimulationController())
    editor = _mark_editor(view)
    editor.instant_spin.setValue(600)
    editor.time_label_edit.setText("intubation")
    editor.add_time_button.click()
    editor.height_spin.setValue(0.8)
    editor.target_label_edit.setText("awake")
    editor.add_target_button.click()
    # Qt shows a row added to a shown list on the next pass of the event loop.
    _settle(application)
    texts = _shown_texts(_marks_panel(view))

    assert sum("intubation" in text for text in texts) == 1
    assert sum("awake" in text for text in texts) == 1


def test_a_wrapped_mark_row_is_told_apart_from_the_row_below_it(application: QApplication) -> None:
    # `PL-FPY2`: the two rows `PL-LHBY`'s review measured wrapping at 350 px.
    # When the rows were joined into one label, the first row's continuation
    # began at the same margin as every row. So `Run 2 reached` looked like a
    # mark of its own, and attached one run's answer to the wrong mark.
    listing = MarkList()
    listing.set_listing(
        MarkListing(
            heading="MAC targets",
            rows=(
                "Fat 1.25 ×MAC – saturation probe · Run 1 not yet · Run 2 reached",
                "Alveolar 0.50 ×MAC · Run 1 reached · Run 2 not yet",
            ),
            empty_text=NO_MAC_TARGETS_TEXT,
        )
    )
    wrapped, below = listing.rows

    # Both dimensions are taken from the row, not from a sidebar width in
    # pixels. A fixed width was a bet on the font that the host resolves for
    # sans-serif (`PL-VCF0`). The width is half the row's own one-line advance,
    # so the row wraps under any font. The height is the listing's height at
    # that width, as the sidebar's layout gives it. A bare window opens at the
    # height its size hint works out for a width of its own choosing. Under
    # Inter at the sidebar's narrow end, 300 px, that was 66 px, against the
    # 81 px that the wrap needs.
    width = wrapped.text_label.fontMetrics().horizontalAdvance(wrapped.text_label.text()) // 2
    listing.resize(width, listing.heightForWidth(width))
    listing.show()

    # The list is a window of its own. Left shown, it outlived this test and
    # failed a later test that counts the shown windows.
    try:
        application.processEvents()
        continuation_x = wrapped.text_label.mapTo(listing, QPoint(0, 0)).x()
        next_row_x = below.bullet_label.mapTo(listing, QPoint(0, 0)).x()

        # The case is exercised only if the first row really does wrap here.
        assert wrapped.text_label.height() >= 2 * wrapped.text_label.fontMetrics().lineSpacing()
        assert below.bullet_label.text() == MARK_ROW_BULLET
        assert continuation_x > next_row_x
        assert wrapped.geometry().bottom() < below.geometry().top()
    finally:
        listing.close()
        listing.deleteLater()
        application.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def test_a_branch_halted_on_a_mark_says_so(application: QApplication) -> None:
    """`PL-LHBY`, the silent negative, end to end from the marks to the drawn row.

    The branch stops itself on a height the user marked. When the row was
    drawn from the reference run, it said nothing at all, because the trunk
    was still running for that target. So the one on-screen sign that a run
    stopped where it was asked to existed for a lone run. It vanished as soon
    as a second run was drawn, and the halt then looked the same as a Pause.

    The test checks the run that halted *and* the run that did not. If only
    the branch were named, the trunk's silence could be read as the trunk
    having no answer, rather than as its answer being "not yet".
    """

    view = _halted_branch_view(application)

    # The crossing lies between 109 s and 110 s (`_halted_branch_view`), and
    # the run stops on the first whole second after it.
    assert view.runs[1].snapshot().elapsed_s == 110
    assert view.runs[1].is_running is False

    listed = _marks_panel(view).targets.text()

    assert f"{run_label(SECOND_RUN)} {MARK_STANDING_COMPARED_TEXT[MarkStanding.REACHED]}" in listed
    assert f"{run_label(FIRST_RUN)} {MARK_STILL_RUNNING_TEXT}" in listed


def test_a_mark_the_branch_cannot_reach_is_not_drawn_as_the_trunk_left_it(
    application: QApplication,
) -> None:
    """`PL-LHBY`, the false positive, and the worse half of the pair.

    The branch inherits an instant but opens after it. That instant used to
    show the trunk's `passed`. So the screen claimed something about the
    displayed branch that the model shows to be false from
    `ResumePoint.fork.instant_s` alone. `MarkStanding.BEFORE_THIS_BRANCH`
    exists so that this is not said, but no screen could show it. The
    reference run is the trunk, and no instant comes before a trunk.
    """

    view = _halted_branch_view(application)

    listed = _marks_panel(view).times.text()

    assert listed.endswith(
        f"{run_label(SECOND_RUN)} {MARK_STANDING_COMPARED_TEXT[MarkStanding.BEFORE_THIS_BRANCH]}"
    )
    assert f"{run_label(FIRST_RUN)} {MARK_STANDING_COMPARED_TEXT[MarkStanding.PASSED]}" in listed


def test_a_failed_run_s_marks_do_not_stand_as_reachable(application: QApplication) -> None:
    """`PL-N3N5`, read as the adversarial review of `PL-LHBY` found it.

    One of two displayed runs is failed the way a step that raised fails it.
    `RunView.halt` records the disposition, and the tick handler calls that
    method. The whole screen is then read at one instant. The trunk's own
    panel said `Stopped - simulation error`, while its clause on a mark it had
    not reached said `not yet`. That is `MarkStanding.STILL_RUNNING`, which
    claims the run can still reach the mark. But `SimulationController.start`
    refuses to resume that run without a reset.

    The failed run is the trunk rather than the branch, so that the test
    reproduces the *drawn* defect and not only the standing behind it. The
    branch has something to say about both new marks, so the rows are
    attributed, and the trunk's answer reaches the screen in words. Where the
    two runs agreed, the row was drawn as silence instead, which made the same
    false claim quietly.

    Both kinds of mark are checked, because a failure ends a clock and a
    height alike. The trunk's inherited `passed` is checked beside them. A
    failure stops a clock without taking it back, so the answers about what
    did happen still apply.
    """

    view = _halted_branch_view(application)
    trunk = view.runs[0]
    # The marks are added after the fork and through the editor, so both runs
    # hold them. The set belongs to the case, and `_apply_to_every_run` is
    # what writes a mark. The instant is ahead of the trunk's clock and behind
    # the branch's. Fat at 0.8 xMAC is out of reach of either run here. So
    # each mark is left outstanding on the trunk, while the branch has an
    # answer for it.
    editor = _mark_editor(view)
    editor.instant_spin.setValue(90)
    editor.add_time_button.click()
    editor.compartment_combo.setCurrentIndex(
        editor.compartment_combo.findData(RecordedQuantity.FAT.value)
    )
    editor.height_spin.setValue(0.8)
    editor.add_target_button.click()

    trunk.halt(_real_step_failure())
    view.present(False)

    assert trunk.controller.has_failed is True
    assert trunk._status_text.text() == STATUS_FAILED_TEXT

    said = MARK_STANDING_COMPARED_TEXT[MarkStanding.NOT_REACHED_BEFORE_FAILURE]
    still_reachable = f"{run_label(FIRST_RUN)} {MARK_STILL_RUNNING_TEXT}"
    times = _marks_panel(view).times.text()
    targets = _marks_panel(view).targets.text()

    assert f"{run_label(FIRST_RUN)} {said}" in times
    assert f"{run_label(FIRST_RUN)} {said}" in targets
    assert still_reachable not in times
    assert still_reachable not in targets
    # The branch still answers for itself, and the trunk still reports what
    # it did reach before the failure.
    assert f"{run_label(SECOND_RUN)} {MARK_STANDING_COMPARED_TEXT[MarkStanding.PASSED]}" in times
    assert f"{run_label(FIRST_RUN)} {MARK_STANDING_COMPARED_TEXT[MarkStanding.PASSED]}" in times
    assert f"{run_label(SECOND_RUN)} {MARK_STANDING_COMPARED_TEXT[MarkStanding.REACHED]}" in targets


def test_a_lone_run_states_a_mark_s_standing_without_naming_a_run(
    application: QApplication,
) -> None:
    # The other side of the same rule: a clause that names no run is a claim
    # about the case, and with one run that claim is true. A run name on every
    # row of a single-run panel would be the standing chrome that
    # `.claude/rules/ui-reader.md` rules out. The dashboard already refuses
    # such names for the legend and the run headings.
    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()
    _advance_to(controller, 60)
    # Marked behind the clock, so the run passes it without halting on it:
    # this test is about how the standing is attributed, not about the halt.
    controller.add_time_bookmark(TimeBookmark(CaseInstant(30), "check"))
    view.present(False)

    listed = _marks_panel(view).times.text()

    assert listed.endswith(MARK_STANDING_TEXT[MarkStanding.PASSED])
    assert run_label(FIRST_RUN) not in listed


def test_the_bookmark_panel_is_placed_inside_its_bookmarks_view(application: QApplication) -> None:
    # The marks belong to the case, so they have a View of their own
    # (`PL-9YPR`). A View builds its copy of the panel on its first frame, and
    # a copy that was built and never placed would be drawn nowhere.
    view = _shown_view(application, SimulationController())
    bookmarks = next(v for v in view.layout_container.views() if isinstance(v, BookmarksView))
    marks = _marks_panel(view)

    assert bookmarks.isAncestorOf(marks)
    assert marks.isVisibleTo(view)


# ------------------------------------------- the editor, in more than one Area


def _panels(view: SimulationView) -> list[BookmarksPanel]:
    """Every Area's copy of the bookmarks panel, in the order the layout lists the Views."""

    panels = [v.panel for v in view.layout_container.views() if isinstance(v, BookmarksView)]

    return [panel for panel in panels if panel is not None]


def _editors(view: SimulationView) -> list[MarkEditor]:
    """Every Area's copy of the marks editor, in the order the layout lists the Views."""

    return [panel.editor for panel in _panels(view)]


def _show_bookmarks_in_two_areas(application: QApplication, view: SimulationView) -> None:
    """Show the bookmarks View in the accounting Area as well as in its own Area."""

    view.layout_container.choose_view(AreaId(2), BOOKMARKS)
    _settle(application)
    view.present(False)


def test_each_copy_of_the_view_removes_the_mark_on_the_row_pressed(
    application: QApplication,
) -> None:
    """Two Areas list the same marks, and a row's Remove button in either copy removes that mark.

    Three instants are marked. The middle row is removed in the first copy,
    and then the last row in the second. The mark below a removed one moves
    up into its row, and no press removes a mark that the reader did not
    press. Before `PL-G1JM`, a selected row stayed selected after a removal,
    so a second press could take a mark that the reader never chose
    (`PL-CHX0`).
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    _show_bookmarks_in_two_areas(application, view)
    first, second = _panels(view)
    editor = first.editor

    for instant_s in (300, 600, 900):
        editor.instant_spin.setValue(instant_s)
        editor.add_time_button.click()

    first.times.rows[1].remove_button.click()

    assert [mark.instant_s for mark in controller.bookmarks.time_bookmarks] == [300.0, 900.0]
    assert [len(panel.times.rows) for panel in (first, second)] == [2, 2]

    second.times.rows[1].remove_button.click()

    assert [mark.instant_s for mark in controller.bookmarks.time_bookmarks] == [300.0]


def test_every_copy_of_the_marks_editor_shows_one_entry_and_acts_on_it(
    application: QApplication,
) -> None:
    """Two Areas show the marks editor, and what the reader enters in one shows in both.

    The marks are edited in the Bookmarks View since `PL-CHX0`, and each Area
    that shows that View holds its own copy of the editor. The dashboard keeps
    the entry, as it keeps the branch control's selected point (`PL-9YPR`). So
    the two copies never show two different entries, and the Add button of
    either copy adds what both of them show.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    _show_bookmarks_in_two_areas(application, view)
    first, second = _editors(view)

    first.instant_spin.setValue(900)
    first.time_label_edit.setText("incision")

    assert (second.instant_spin.value(), second.time_label_edit.text()) == (900, "incision")
    assert second.instant_preview.text() == "15m"

    second.add_time_button.click()

    assert controller.bookmarks.time_bookmarks == (TimeBookmark(CaseInstant(900), "incision"),)
    assert [editor.time_label_edit.text() for editor in (first, second)] == ["", ""]

    for instant_s in (300, 1200):
        first.instant_spin.setValue(instant_s)
        first.add_time_button.click()

    first.instant_spin.setValue(1500)
    _panels(view)[1].times.rows[2].remove_button.click()

    assert [mark.instant_s for mark in controller.bookmarks.time_bookmarks] == [900.0, 300.0]
    assert [editor.instant_spin.value() for editor in (first, second)] == [1500, 1500]


def test_a_refusal_shows_in_every_copy_under_the_button_that_was_pressed(
    application: QApplication,
) -> None:
    """A refused edit is explained under its own button, in every Area that shows the editor.

    The Bookmarks Area of the Default Workspace is about 150 pixels tall at
    1366 by 768, so the View scrolls. A refusal is shown directly under the
    button that was pressed, so that it is in view of that button
    (`PL-CHX0`). The next edit replaces it, under whichever button asked.
    """

    view = _shown_view(application, SimulationController())
    _show_bookmarks_in_two_areas(application, view)
    first, second = _editors(view)
    first.instant_spin.setValue(600)
    first.add_time_button.click()
    second.add_time_button.click()

    for editor in (first, second):
        notice = editor.add_time_notice.notice()
        assert notice is not None
        assert "marked once" in notice
        assert editor.add_target_notice.notice() is None

    for panel in _panels(view):
        assert panel.times.remove_notice.notice() is None
        assert panel.targets.remove_notice.notice() is None

    second.instant_spin.setValue(900)
    second.add_time_button.click()

    for editor in (first, second):
        assert editor.add_time_notice.notice() is None


def test_a_rebuilt_bookmarks_view_shows_the_entry_and_the_refusal_the_reader_left(
    application: QApplication,
) -> None:
    """A copy of the editor built after its Area showed another View shows what the reader left.

    A switch of Workspace, or of an Area's View, deletes the View's copy and
    builds a new one. The editor was a window that lasted for the life of the
    dashboard, so a reader who closed it found their entry where they had left
    it. The dashboard keeps the entry and the refusal for the same reason
    (`PL-CHX0`).

    The height is 3.7 times the agent's MAC, which sevoflurane can reach and
    which is above the bound a new height control starts with. A new copy
    must take the running agent's bound before it shows the kept entry, or
    the control would cut the height down to its starting bound.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    (editor,) = _editors(view)
    editor.instant_spin.setValue(600)
    editor.add_time_button.click()
    editor.add_time_button.click()
    editor.instant_spin.setValue(1500)
    editor.time_label_edit.setText("emergence")
    editor.compartment_combo.setCurrentIndex(
        editor.compartment_combo.findData(RecordedQuantity.FAT.value)
    )
    editor.height_spin.setValue(3.7)
    refusal = editor.add_time_notice.notice()
    assert refusal is not None
    assert editor.height_spin.value() == 3.7

    view.layout_container.choose_view(AreaId(5), AGENT_ACCOUNTING)
    _settle(application)
    assert _editors(view) == []

    view.layout_container.choose_view(AreaId(5), BOOKMARKS)
    _settle(application)
    view.present(False)
    (rebuilt,) = _editors(view)

    assert rebuilt is not editor
    assert rebuilt.instant_spin.value() == 1500
    assert rebuilt.instant_preview.text() == "25m"
    assert rebuilt.time_label_edit.text() == "emergence"
    assert rebuilt.compartment_combo.currentData() == RecordedQuantity.FAT.value
    assert rebuilt.height_spin.value() == 3.7
    assert rebuilt.add_time_notice.notice() == refusal


def test_a_refused_mark_is_read_out_once_however_many_copies_show_it(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A screen reader is interrupted once for each refused press, by the dashboard (`PL-J7Z5`).

    Two Areas show the editor, and both show the refusal under the button
    that was pressed. When each copy read out its own refusal, a reader heard
    it twice. A copy built again later shows the refusal the reader left, which
    is not news, so it is not read out again.
    """

    view = _shown_view(application, SimulationController())
    _show_bookmarks_in_two_areas(application, view)
    first, _ = _editors(view)
    first.instant_spin.setValue(600)
    first.add_time_button.click()
    _settle(application)
    recorded = record_announcements(monkeypatch)

    first.add_time_button.click()
    _settle(application)

    refusal = first.add_time_notice.notice()
    assert refusal is not None
    assert "marked once" in refusal
    assert recorded == [Announcement(refusal, ASSERTIVE)]

    recorded.clear()
    view.layout_container.choose_view(AreaId(5), AGENT_ACCOUNTING)
    _settle(application)
    view.layout_container.choose_view(AreaId(5), BOOKMARKS)
    _settle(application)
    view.present(False)
    _settle(application)

    assert [editor.add_time_notice.notice() for editor in _editors(view)] == [refusal, refusal]
    assert recorded == []


def test_a_copy_built_while_a_halt_hides_the_lists_lists_the_marks_once_they_return(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A copy of the View built while the lists are hidden lists every mark once a frame shows them.

    A halt that cannot work out the marks' standings hides the lists in every
    copy, with their Remove buttons (`PL-F5KT`). A copy built then has no
    rows. Once a frame lists the marks again, its rows and their Remove
    buttons must act on the marks the first copy lists.
    """

    controller = _paused_run_with_history()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(600), "check"))
    controller.add_time_bookmark(TimeBookmark(CaseInstant(900), "later"))
    view = _shown_view(application, controller)
    (first,) = _panels(view)

    def unanswerable(self: SimulationController) -> NoReturn:
        raise RuntimeError("the run could not say where it stands on its marks")

    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    monkeypatch.setattr(SimulationController, "bookmark_standings", unanswerable)
    view.present(False)
    view.layout_container.choose_view(AreaId(2), BOOKMARKS)
    _settle(application)
    (second,) = [panel for panel in _panels(view) if panel is not first]

    assert second.times.isHidden() is True

    monkeypatch.undo()
    view.present(False)

    assert second.times.isHidden() is False
    assert second.times.text() == first.times.text()

    second.times.rows[1].remove_button.click()

    assert [mark.instant_s for mark in controller.bookmarks.time_bookmarks] == [600.0]


def test_the_marks_editor_scrolls_inside_the_default_bookmarks_area_rather_than_clipping(
    application: QApplication,
) -> None:
    """At 1366 by 768 the Default Workspace's Bookmarks Area scrolls the forms, and clips none.

    The Area is about 150 pixels tall there, and the two forms need several
    times that (`PL-CHX0`). Every View in an Area too short for it scrolls in
    the Area's box (`area_layout.ViewScroll`, `PL-CBYS`). So the View is drawn
    at least as tall as its content needs, each control of the editor is given
    at least the height it asks for, and the box can scroll to the last of
    them.
    """

    view = _shown_view(
        application,
        SimulationController(),
        width_px=1366,
        height_px=768,
        workspaces=shipped_workspaces(),
    )
    _settle(application)
    view.present(False)
    bookmarks = next(v for v in view.layout_container.views() if isinstance(v, BookmarksView))
    box = bookmarks.parentWidget()
    box = None if box is None else box.parentWidget()
    assert isinstance(box, ViewScroll)
    editor = _mark_editor(view)
    controls = (
        editor.instant_spin,
        editor.time_label_edit,
        editor.add_time_button,
        editor.compartment_combo,
        editor.height_spin,
        editor.target_label_edit,
        editor.add_target_button,
    )

    assert box.viewport().height() < bookmarks.height()
    assert box.verticalScrollBar().maximum() >= bookmarks.height() - box.viewport().height()
    assert bookmarks.height() >= bookmarks.minimumSizeHint().height()

    for control in controls:
        bottom = control.mapTo(bookmarks, QPoint(0, control.height())).y()
        assert control.height() >= control.minimumSizeHint().height(), control
        assert bottom <= bookmarks.height(), control


def test_a_frame_that_lists_the_same_marks_keeps_where_the_reader_scrolled_the_view(
    application: QApplication,
) -> None:
    """A Bookmarks View longer than its Area keeps its scroll position from one frame to the next.

    Every frame redraws the lists while a run plays. The rows are rewritten in
    place, so a reader who scrolled down to a mark's Remove button can still
    reach it while a run plays (`PL-CHX0`). The test marks more instants and
    heights than the Area shows, scrolls the Area to the bottom, and draws
    another frame with the same marks.
    """

    controller = SimulationController()

    for minute in range(1, 13):
        controller.add_time_bookmark(TimeBookmark(CaseInstant(60 * minute)))
        controller.add_mac_target(MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.1 * minute)))

    view = _shown_view(application, controller)
    view.present(False)
    _settle(application)
    bookmarks = next(v for v in view.layout_container.views() if isinstance(v, BookmarksView))
    box = bookmarks.parentWidget()
    box = None if box is None else box.parentWidget()
    assert isinstance(box, ViewScroll)
    bar = box.verticalScrollBar()

    assert bar.maximum() > 0

    bar.setValue(bar.maximum())
    scrolled = bar.value()
    view.present(False)
    _settle(application)

    assert bar.value() == scrolled


# --- Undo after a removal (PL-5GX4) ---------------------------------------------


def _wait_past_a_double_click() -> None:
    """Wait until a list takes a press again (`MarkList`'s double-click guard)."""

    QTest.qWait(QApplication.doubleClickInterval() + 50)


def test_undo_puts_a_removed_mark_back_in_its_row_in_every_run(application: QApplication) -> None:
    """The middle of three marks, removed and undone, is back between the other two in both runs.

    The expected marks are the ones the runs held before the removal. The
    offer is shown under the list the mark was removed from and not under the
    other, and it is gone once used.
    """

    first = SimulationController()
    second = SimulationController()
    view = _shown_view(application, first, second)
    editor = _mark_editor(view)
    panel = _marks_panel(view)

    for instant_s in (300, 600, 900):
        editor.instant_spin.setValue(instant_s)
        editor.add_time_button.click()

    before = first.bookmarks
    panel.times.rows[1].remove_button.click()
    _settle(application)

    assert panel.times.undo_button.isVisibleTo(panel)
    assert not panel.targets.undo_button.isVisibleTo(panel)
    assert panel.times.undo_label.text() == "Removed: 10m"

    _wait_past_a_double_click()
    panel.times.undo_button.click()
    _settle(application)

    assert first.bookmarks == second.bookmarks == before
    assert len(panel.times.rows) == 3
    assert not panel.times.undo_button.isVisibleTo(panel)


def test_undo_goes_back_through_several_removals_the_latest_first(
    application: QApplication,
) -> None:
    """Three removals from both lists are undone one at a time, each under its own list."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    editor = _mark_editor(view)
    panel = _marks_panel(view)

    for instant_s in (300, 600, 900):
        editor.instant_spin.setValue(instant_s)
        editor.add_time_button.click()

    editor.height_spin.setValue(1.0)
    editor.add_target_button.click()
    start = controller.bookmarks

    panel.times.rows[0].remove_button.click()
    panel.targets.rows[0].remove_button.click()
    _wait_past_a_double_click()
    panel.times.rows[1].remove_button.click()
    _settle(application)
    after_two = [mark.instant_s for mark in controller.bookmarks.time_bookmarks]

    assert after_two == [600.0]
    assert panel.times.undo_label.text() == "Removed: 15m"

    _wait_past_a_double_click()
    panel.times.undo_button.click()
    _settle(application)

    assert panel.targets.undo_button.isVisibleTo(panel)
    assert not panel.times.undo_button.isVisibleTo(panel)

    panel.targets.undo_button.click()
    _wait_past_a_double_click()
    panel.times.undo_button.click()
    _settle(application)

    assert controller.bookmarks == start
    assert not panel.times.undo_button.isVisibleTo(panel)
    assert not panel.targets.undo_button.isVisibleTo(panel)


def test_a_mark_added_after_a_removal_ends_the_offer_to_undo_it(application: QApplication) -> None:
    """Undo never reverses one edit on top of a later one, so an add withdraws the offer."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    editor = _mark_editor(view)
    panel = _marks_panel(view)

    for instant_s in (300, 600):
        editor.instant_spin.setValue(instant_s)
        editor.add_time_button.click()

    panel.times.rows[0].remove_button.click()
    editor.instant_spin.setValue(900)
    editor.add_time_button.click()
    _settle(application)

    assert not panel.times.undo_button.isVisibleTo(panel)
    assert panel.times.undo_button.isEnabled() is False
    assert [mark.instant_s for mark in controller.bookmarks.time_bookmarks] == [600.0, 900.0]


def test_a_reset_ends_the_offer_to_undo_a_removal_from_the_case_before_it(
    application: QApplication,
) -> None:
    """A Reset keeps the controller and the marks, but the removal belonged to the run before.

    Blind review of `PL-5GX4` found the offer still shown after a Reset with
    one run on screen, where neither the runs nor the marks had changed.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    editor = _mark_editor(view)
    times = _marks_panel(view).times

    for instant_s in (300, 600):
        editor.instant_spin.setValue(instant_s)
        editor.add_time_button.click()

    times.rows[0].remove_button.click()
    _settle(application)

    assert times.undo_button.isVisibleTo(times)

    view.runs[0]._reset_button.click()
    _settle(application)

    assert not times.undo_button.isVisibleTo(times)
    assert times.undo_button.isEnabled() is False
    assert [mark.instant_s for mark in controller.bookmarks.time_bookmarks] == [600.0]


def test_a_double_click_on_undo_puts_back_one_mark(application: QApplication) -> None:
    """The next removal back is offered where the last Undo was, so a double-click undoes one."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    editor = _mark_editor(view)
    times = _marks_panel(view).times

    for instant_s in (300, 600, 900):
        editor.instant_spin.setValue(instant_s)
        editor.add_time_button.click()

    times.rows[0].remove_button.click()
    _wait_past_a_double_click()
    times.rows[0].remove_button.click()
    _wait_past_a_double_click()
    times.undo_button.click()
    _settle(application)
    times.undo_button.click()

    assert [mark.instant_s for mark in controller.bookmarks.time_bookmarks] == [600.0, 900.0]


def test_the_undo_button_names_the_removed_mark_to_a_screen_reader(
    application: QApplication,
) -> None:
    """The name is built from the mark the test adds, not read from the row."""

    view = _shown_view(application, SimulationController())
    editor = _mark_editor(view)
    editor.instant_spin.setValue(300)
    editor.time_label_edit.setText("induction")
    editor.add_time_button.click()
    times = _marks_panel(view).times

    times.rows[0].remove_button.click()

    assert times.undo_button.text() == "Undo"
    assert times.undo_button.accessibleName() == "Undo removing 5m – induction"


def test_an_undone_removal_of_a_target_a_branch_reached_still_says_it_was_reached(
    application: QApplication,
) -> None:
    """Each run gets its own standing back: the branch reached the target, the trunk has not yet.

    The branch halts on the target and then runs on past it, so the halt no
    longer shows the target as reached on its own. The expected listing is
    the one drawn before the removal. A target added back as new would read
    as still to come on the branch.
    """

    view = _halted_branch_view(application)
    branch = view.runs[1].controller
    branch.start()

    for _ in range(10):
        branch.advance()

    view.present(False)
    _settle(application)
    targets = _marks_panel(view).targets
    before = targets.text()

    targets.rows[0].remove_button.click()
    _wait_past_a_double_click()
    targets.undo_button.click()
    _settle(application)

    assert targets.text() == before
    assert f"{run_label(SECOND_RUN)} {MARK_STANDING_COMPARED_TEXT[MarkStanding.REACHED]}" in before
