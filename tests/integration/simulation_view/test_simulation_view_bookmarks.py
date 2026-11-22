"""The dashboard, driven headless against real runs.

These tests cover bookmarks.

`simulation_view_support.py` describes the whole suite.
"""

from typing import NoReturn

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication

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
    REMOVE_NOTHING_SELECTED_TEXT,
    STATUS_FAILED_TEXT,
    MarkListing,
    run_label,
)
from anesthesia_sim.app.formatting import format_elapsed, mac_multiple
from anesthesia_sim.app.qt_widgets import MarkEditor, MarkListingLabel
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.theme import MARK_ROW_BULLET
from anesthesia_sim.app.view_registry import AGENT_ACCOUNTING, BOOKMARKS
from anesthesia_sim.app.views import BookmarksView
from anesthesia_sim.core.concentration import MacMultiple, fraction_from_percent
from anesthesia_sim.core.supported_ranges import CaseInstant
from anesthesia_sim.layout.shipped import shipped_workspaces
from anesthesia_sim.layout.tree import AreaId
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
    assert editor.time_list.count() == 1


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


def test_a_mark_added_from_the_dashboard_reaches_every_displayed_run(
    application: QApplication,
) -> None:
    # The marks belong to the case. Writing to every run makes it impossible
    # to compare two runs at two different heights because a learner typed
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

    editor.time_list.setCurrentRow(0)
    editor.remove_time_button.click()

    assert first.snapshot().bookmarks == second.snapshot().bookmarks
    assert [mark.instant_s for mark in first.snapshot().bookmarks.time_bookmarks] == [600.0]


def test_removing_with_nothing_selected_says_so_and_removes_nothing(
    application: QApplication,
) -> None:
    controller = SimulationController()
    view = _shown_view(application, controller)
    editor = _mark_editor(view)
    editor.instant_spin.setValue(600)
    editor.add_time_button.click()
    editor.time_list.setCurrentRow(-1)
    editor.remove_time_button.click()

    assert editor.remove_time_notice.notice() == REMOVE_NOTHING_SELECTED_TEXT
    assert editor.add_time_notice.notice() is None
    assert len(controller.snapshot().bookmarks.time_bookmarks) == 1


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

    editor.time_list.setCurrentRow(0)
    editor.remove_time_button.click()

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


def test_the_editor_and_the_lists_above_it_show_one_set_of_rows(application: QApplication) -> None:
    # Both read `dashboard_frame.bookmark_panel`, so a reader moving between
    # them is reading one listing in two places.
    view = _shown_view(application, SimulationController())
    editor = _mark_editor(view)
    editor.instant_spin.setValue(600)
    editor.time_label_edit.setText("intubation")
    editor.add_time_button.click()

    listed = [editor.time_list.item(row).text() for row in range(editor.time_list.count())]

    assert _marks_panel(view).times.text() == "\n".join(listed)


def test_a_wrapped_mark_row_is_told_apart_from_the_row_below_it(application: QApplication) -> None:
    # `PL-FPY2`: the two rows `PL-LHBY`'s review measured wrapping at 350 px.
    # When the rows were joined into one label, the first row's continuation
    # began at the same margin as every row. So `Run 2 reached` looked like a
    # mark of its own, and attached one run's answer to the wrong mark.
    listing = MarkListingLabel()
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
    application.processEvents()

    continuation_x = wrapped.text_label.mapTo(listing, QPoint(0, 0)).x()
    next_row_x = below.bullet_label.mapTo(listing, QPoint(0, 0)).x()

    # The case is exercised only if the first row really does wrap here.
    assert wrapped.text_label.height() >= 2 * wrapped.text_label.fontMetrics().lineSpacing()
    assert below.bullet_label.text() == MARK_ROW_BULLET
    assert continuation_x > next_row_x
    assert wrapped.geometry().bottom() < below.geometry().top()


def test_a_branch_halted_on_a_mark_says_so(application: QApplication) -> None:
    """`PL-LHBY`, the silent negative, end to end from the marks to the drawn row.

    The branch stops itself on a height the learner marked. When the row was
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


def _editors(view: SimulationView) -> list[MarkEditor]:
    """Every Area's copy of the marks editor, in the order the layout lists the Views."""

    panels = [v.panel for v in view.layout_container.views() if isinstance(v, BookmarksView)]

    return [panel.editor for panel in panels if panel is not None]


def _show_bookmarks_in_two_areas(application: QApplication, view: SimulationView) -> None:
    """Show the bookmarks View in the accounting Area as well as in its own Area."""

    view.layout_container.choose_view(AreaId(2), BOOKMARKS)
    _settle(application)
    view.present(False)


def test_a_remove_leaves_no_mark_selected_so_a_second_press_removes_nothing(
    application: QApplication,
) -> None:
    """After a Remove, no row is selected in any copy, so pressing Remove again takes nothing.

    Three instants are marked and the middle one is removed. The mark below
    it moves up into its row. Before the fix, that row stayed selected in
    every copy of the editor, and a second press of Remove took the 900 s
    mark from every run although the reader never chose it.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    _show_bookmarks_in_two_areas(application, view)
    first, second = _editors(view)

    for instant_s in (300, 600, 900):
        first.instant_spin.setValue(instant_s)
        first.add_time_button.click()

    first.time_list.setCurrentRow(1)
    first.remove_time_button.click()
    rows_after_remove = [first.time_list.currentRow(), second.time_list.currentRow()]
    second.remove_time_button.click()

    assert rows_after_remove == [-1, -1]
    assert [mark.instant_s for mark in controller.snapshot().bookmarks.time_bookmarks] == [300, 900]
    assert second.remove_time_notice.notice() == REMOVE_NOTHING_SELECTED_TEXT


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

    second.time_list.setCurrentRow(2)

    assert first.time_list.currentRow() == 2

    first.remove_time_button.click()

    assert [mark.instant_s for mark in controller.bookmarks.time_bookmarks] == [900.0, 300.0]


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
        assert editor.remove_target_notice.notice() is None

    second.target_list.setCurrentRow(-1)
    second.remove_target_button.click()

    for editor in (first, second):
        assert editor.add_time_notice.notice() is None
        assert editor.remove_target_notice.notice() == REMOVE_NOTHING_SELECTED_TEXT


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
    editor.time_list.setCurrentRow(0)
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
    assert rebuilt.time_list.currentRow() == 0
    assert rebuilt.add_time_notice.notice() == refusal


def test_a_rebuilt_bookmarks_view_does_not_select_a_row_the_reader_lost(
    application: QApplication,
) -> None:
    """A row that a removal deselected stays deselected in a copy of the editor built later.

    Removing the last of three rows leaves nothing selected, because that row
    is gone. If the dashboard still kept the old selection, a copy built after
    a third mark was added would select the new third row, and its Remove
    button would remove a mark the reader never chose (`PL-CHX0`).
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    (editor,) = _editors(view)

    for instant_s in (300, 600, 900):
        editor.instant_spin.setValue(instant_s)
        editor.add_time_button.click()

    editor.time_list.setCurrentRow(2)
    editor.remove_time_button.click()

    assert editor.time_list.currentRow() == -1

    # The third mark is added through the controller, so that no field of the
    # editor changes and nothing but a frame can update the kept entry.
    controller.add_time_bookmark(TimeBookmark(CaseInstant(1200)))
    view.present(False)
    view.layout_container.choose_view(AreaId(5), AGENT_ACCOUNTING)
    _settle(application)
    view.layout_container.choose_view(AreaId(5), BOOKMARKS)
    _settle(application)
    view.present(False)
    (rebuilt,) = _editors(view)

    assert rebuilt.time_list.count() == 3
    assert rebuilt.time_list.currentRow() == -1


def test_a_copy_built_while_a_halt_hides_the_lists_selects_the_kept_row_once_they_return(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A copy of the editor built while the lists are hidden selects the reader's row once shown.

    A halt that cannot work out the marks' standings hides the lists in every
    copy (`PL-F5KT`). A copy built then has no rows, so it cannot select the
    row the reader chose. Once a frame lists the marks again, both copies must
    select that row. Otherwise the two Areas show different selections, and
    Remove acts in one copy and is refused in the other (`PL-CHX0`).
    """

    controller = _paused_run_with_history()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(600), "check"))
    controller.add_time_bookmark(TimeBookmark(CaseInstant(900), "later"))
    view = _shown_view(application, controller)
    (first,) = _editors(view)
    first.time_list.setCurrentRow(1)

    def unanswerable(self: SimulationController) -> NoReturn:
        raise RuntimeError("the run could not say where it stands on its marks")

    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    monkeypatch.setattr(SimulationController, "bookmark_standings", unanswerable)
    view.present(False)
    view.layout_container.choose_view(AreaId(2), BOOKMARKS)
    _settle(application)
    (second,) = [editor for editor in _editors(view) if editor is not first]

    assert second.time_list.isHidden() is True

    monkeypatch.undo()
    view.present(False)

    assert second.time_list.isHidden() is False
    assert [editor.time_list.currentRow() for editor in (first, second)] == [1, 1]

    second.remove_time_button.click()

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
        editor.time_list,
        editor.compartment_combo,
        editor.height_spin,
        editor.target_label_edit,
        editor.add_target_button,
        editor.remove_target_button,
        editor.target_list,
    )

    assert box.viewport().height() < bookmarks.height()
    assert box.verticalScrollBar().maximum() >= bookmarks.height() - box.viewport().height()
    assert bookmarks.height() >= bookmarks.minimumSizeHint().height()

    for control in controls:
        bottom = control.mapTo(bookmarks, QPoint(0, control.height())).y()
        assert control.height() >= control.minimumSizeHint().height(), control
        assert bottom <= bookmarks.height(), control


def test_a_frame_that_lists_the_same_marks_keeps_where_the_reader_scrolled_each_list(
    application: QApplication,
) -> None:
    """A list longer than its box keeps its scroll position from one frame to the next.

    Every frame redraws the lists while a run plays. A list that was emptied
    and filled again on every frame, and then had its selected row set again,
    scrolled back to that row each time. A reader with a row selected could
    then not scroll the list while a run played (`PL-CHX0`). The test marks
    more instants and heights than either box shows, selects the first row of
    each list, scrolls both lists to the bottom, and draws another frame with
    the same marks.
    """

    controller = SimulationController()

    for minute in range(1, 13):
        controller.add_time_bookmark(TimeBookmark(CaseInstant(60 * minute)))
        controller.add_mac_target(MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.1 * minute)))

    view = _shown_view(application, controller)
    editor = _mark_editor(view)
    view.present(False)
    _settle(application)
    bars = [listing.verticalScrollBar() for listing in (editor.time_list, editor.target_list)]

    assert all(bar.maximum() > 0 for bar in bars)

    editor.time_list.setCurrentRow(0)
    editor.target_list.setCurrentRow(0)

    for bar in bars:
        bar.setValue(bar.maximum())

    scrolled = [bar.value() for bar in bars]
    view.present(False)
    _settle(application)

    assert [bar.value() for bar in bars] == scrolled
    assert [editor.time_list.currentRow(), editor.target_list.currentRow()] == [0, 0]
