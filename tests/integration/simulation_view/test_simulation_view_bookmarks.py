"""The dashboard, driven headless against real runs.

These tests cover bookmarks.

`simulation_view_support.py` describes the whole suite.
"""

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication

from anesthesia_sim.app.bookmarks import MarkStanding, TimeBookmark
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
from anesthesia_sim.app.qt_widgets import MarkListingLabel
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity
from anesthesia_sim.app.theme import MARK_ROW_BULLET
from anesthesia_sim.app.views import BookmarksView
from anesthesia_sim.core.concentration import fraction_from_percent
from anesthesia_sim.core.supported_ranges import CaseInstant
from tests.integration.simulation_view.simulation_view_support import (
    FIRST_RUN,
    SECOND_RUN,
    _advance_to,
    _branched_case,
    _case_view,
    _halted_branch_view,
    _marks_panel,
    _opened_bookmark_dialog,
    _real_step_failure,
    _shown_view,
    _take_fork,
)


def test_a_dashboard_opens_with_both_collections_listed_as_empty(application: QApplication) -> None:
    view = _shown_view(application, SimulationController())

    assert _marks_panel(view).times.text() == NO_TIME_BOOKMARKS_TEXT
    assert _marks_panel(view).targets.text() == NO_MAC_TARGETS_TEXT


def test_an_instant_entered_in_the_dialog_is_listed_beside_the_chart(
    application: QApplication,
) -> None:
    view = _shown_view(application, SimulationController())
    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(600.0)
    dialog.time_label_edit.setText("intubation")
    dialog.add_time_button.click()

    assert "intubation" in _marks_panel(view).times.text()
    assert dialog.time_list.count() == 1


def test_the_entered_instant_is_restated_in_the_form_the_clock_uses(
    application: QApplication,
) -> None:
    # The spin box states one unit and the clock states three, so the dialog
    # carries the conversion rather than leaving it to the reader.
    view = _shown_view(application, SimulationController())
    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(600.0)

    assert dialog.instant_preview.text() == format_elapsed(600.0)


def test_a_target_entered_in_the_dialog_names_its_compartment_and_height(
    application: QApplication,
) -> None:
    view = _shown_view(application, SimulationController())
    dialog = _opened_bookmark_dialog(view)
    dialog.compartment_combo.setCurrentIndex(
        dialog.compartment_combo.findData(RecordedQuantity.VESSEL_RICH.value)
    )
    dialog.height_spin.setValue(0.8)
    dialog.add_target_button.click()

    listed = _marks_panel(view).targets.text()

    assert listed == "Vessel-rich 0.80 ×MAC"


def test_the_compartment_picker_offers_the_six_drawn_compartments_and_no_ratio(
    application: QApplication,
) -> None:
    # `WASH_IN_RATIO` is a quotient rather than a concentration, so a multiple
    # of MAC of it is not a quantity the model holds.
    view = _shown_view(application, SimulationController())
    dialog = _opened_bookmark_dialog(view)
    offered = [
        dialog.compartment_combo.itemData(row) for row in range(dialog.compartment_combo.count())
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
    dialog = _opened_bookmark_dialog(view)
    snapshot = controller.snapshot()
    reachable = mac_multiple(
        fraction_from_percent(snapshot.max_delivered_concentration_percent),
        snapshot.agent_mac_percent,
    )

    assert dialog.height_spin.maximum() == pytest.approx(reachable)

    dialog.height_spin.setValue(reachable * 2.0)

    assert dialog.height_spin.value() == pytest.approx(reachable)


def test_a_mark_added_from_the_dashboard_reaches_every_displayed_run(
    application: QApplication,
) -> None:
    # The marks belong to the case. Writing to every run makes it impossible
    # to compare two runs at two different heights because a learner typed
    # one of them twice.
    first = SimulationController()
    second = SimulationController()
    view = _shown_view(application, first, second)
    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(600.0)
    dialog.add_time_button.click()

    assert first.snapshot().bookmarks == second.snapshot().bookmarks
    assert len(first.snapshot().bookmarks.time_bookmarks) == 1


def test_every_displayed_run_carries_the_same_marks_after_an_add_and_a_removal(
    application: QApplication,
) -> None:
    first = SimulationController()
    second = SimulationController()
    view = _shown_view(application, first, second)
    dialog = _opened_bookmark_dialog(view)

    for instant_s in (120.0, 600.0):
        dialog.instant_spin.setValue(instant_s)
        dialog.add_time_button.click()

    dialog.time_list.setCurrentRow(0)
    dialog.remove_time_button.click()

    assert first.snapshot().bookmarks == second.snapshot().bookmarks
    assert [mark.instant_s for mark in first.snapshot().bookmarks.time_bookmarks] == [600.0]


def test_removing_with_nothing_selected_says_so_and_removes_nothing(
    application: QApplication,
) -> None:
    controller = SimulationController()
    view = _shown_view(application, controller)
    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(600.0)
    dialog.add_time_button.click()
    dialog.time_list.setCurrentRow(-1)
    dialog.remove_time_button.click()

    assert dialog.notice.notice() == REMOVE_NOTHING_SELECTED_TEXT
    assert len(controller.snapshot().bookmarks.time_bookmarks) == 1


def test_marking_one_instant_twice_is_refused_and_says_why(application: QApplication) -> None:
    controller = SimulationController()
    view = _shown_view(application, controller)
    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(600.0)
    dialog.add_time_button.click()
    dialog.add_time_button.click()

    notice = dialog.notice.notice()

    assert notice is not None
    assert "marked once" in notice
    assert len(controller.snapshot().bookmarks.time_bookmarks) == 1


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

    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(600.0)
    dialog.add_time_button.click()

    assert trunk.snapshot().bookmarks == branch.snapshot().bookmarks
    assert len(branch.snapshot().bookmarks.time_bookmarks) == 1

    dialog.compartment_combo.setCurrentIndex(
        dialog.compartment_combo.findData(RecordedQuantity.VESSEL_RICH.value)
    )
    dialog.height_spin.setValue(0.8)
    dialog.add_target_button.click()

    assert trunk.snapshot().bookmarks == branch.snapshot().bookmarks

    dialog.time_list.setCurrentRow(0)
    dialog.remove_time_button.click()

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
    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(600.0)
    dialog.add_time_button.click()
    dialog.add_time_button.click()

    assert first.snapshot().bookmarks == second.snapshot().bookmarks


def test_a_name_field_is_cleared_after_a_mark_is_added_and_the_value_is_not(
    application: QApplication,
) -> None:
    # Adding a second mark near the first is the common case, so the instant
    # stays. A reused name would give two marks the same name, so the name is
    # cleared.
    view = _shown_view(application, SimulationController())
    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(600.0)
    dialog.time_label_edit.setText("intubation")
    dialog.add_time_button.click()

    assert dialog.time_label_edit.text() == ""
    assert dialog.instant_spin.value() == 600.0


def test_the_dialog_and_the_panel_list_one_set_of_rows(application: QApplication) -> None:
    # Both read `dashboard_frame.bookmark_panel`, so a reader moving between
    # them is reading one listing in two places.
    view = _shown_view(application, SimulationController())
    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(600.0)
    dialog.time_label_edit.setText("intubation")
    dialog.add_time_button.click()

    listed = [dialog.time_list.item(row).text() for row in range(dialog.time_list.count())]

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

    assert view.runs[1].snapshot().elapsed_s == pytest.approx(114.7)
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
    dialog = _opened_bookmark_dialog(view)
    dialog.instant_spin.setValue(90.0)
    dialog.add_time_button.click()
    dialog.compartment_combo.setCurrentIndex(
        dialog.compartment_combo.findData(RecordedQuantity.FAT.value)
    )
    dialog.height_spin.setValue(0.8)
    dialog.add_target_button.click()

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
    _advance_to(controller, 60.0)
    # Marked behind the clock, so the run passes it without halting on it:
    # this test is about how the standing is attributed, not about the halt.
    controller.add_time_bookmark(TimeBookmark(CaseInstant(30.0), "check"))
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
