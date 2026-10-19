"""Tests of the Workspace tab strip, run headless.

`app/workspace_tabs.py` draws one tab per Workspace from a `WorkspaceSet` it
does not own, and hands every change a reader makes back as a new set
(`PL-2KXB`). These tests check `PL-QW1Z`'s decisions: the shipped tabs come
first and a rule follows them, the current tab is the checked one, each menu
entry is worked out before it is shown, Delete and Reset ask first, and a tab
is renamed in place. The dashboard tests check what the strip does to the
page. A tab switches the Areas and never a run. A Workspace that the reader
leaves and comes back to is as it was left. A pinned Workspace draws its run
alone, or says that the run is not open (`PL-WV9K` Q6). The tests render under
the `offscreen` platform that `tests/conftest.py` selects.
"""

from collections.abc import Iterator

import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QContextMenuEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from anesthesia_sim.app.chart_time_base import time_base_for_span
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import SIMULATION_STEP_S
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.view_registry import WASH_IN
from anesthesia_sim.app.views import ConcentrationView
from anesthesia_sim.app.workspace_tabs import (
    DELETE_LABEL,
    DUPLICATE_LABEL,
    MOVE_LEFT_LABEL,
    MOVE_RIGHT_LABEL,
    RENAME_LABEL,
    RESET_LABEL,
    TabOperation,
    WorkspaceTabs,
    display_order,
    tab_operations,
)
from anesthesia_sim.layout.exceptions import ShippedWorkspaceError
from anesthesia_sim.layout.run_identity import RunId, RunIdentities, SessionToken
from anesthesia_sim.layout.shipped import shipped_workspace, shipped_workspaces
from anesthesia_sim.layout.tree import AreaId
from anesthesia_sim.layout.workspace import (
    ShippedWorkspaceId,
    Workspace,
    WorkspaceName,
    WorkspaceSet,
)

_SESSION = SessionToken("0" * 32)
_RUN_1 = RunId(_SESSION, 1)
_RUN_2 = RunId(_SESSION, 2)


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


class _Owner:
    """What a dashboard does with the strip: hold the set, and draw the strip again on a change."""

    def __init__(self, workspaces: WorkspaceSet, runs: tuple[RunId, ...] = (_RUN_1,)) -> None:
        self.changes: list[WorkspaceSet] = []
        self.runs = runs
        self.strip = WorkspaceTabs(workspaces, self.change, lambda: self.runs)
        self.strip.resize(900, 40)
        self.strip.show()

    def change(self, workspaces: WorkspaceSet) -> None:
        self.changes.append(workspaces)
        self.strip.show_set(workspaces)

    @property
    def names(self) -> list[str]:
        return [tab.text() for tab in self.strip.tabs]


@pytest.fixture
def owner(application: QApplication) -> Iterator[_Owner]:
    made = _Owner(_with_mine(shipped_workspaces()))
    yield made
    made.strip.close()
    made.strip.deleteLater()
    application.processEvents()


def _with_mine(workspaces: WorkspaceSet) -> WorkspaceSet:
    """The shipped set with a copy of the Default after it, and the Default active."""

    return workspaces.duplicate(0).activate(0)


def _entries(strip: WorkspaceTabs, index: int) -> list[tuple[str, bool]]:
    return [(action.text(), action.isEnabled()) for action in strip.menu_for(index).actions()]


def _named(operations: tuple[TabOperation, ...], label: str) -> TabOperation:
    return next(operation for operation in operations if operation.label == label)


def test_the_shipped_tabs_come_first_and_a_rule_follows_them(owner: _Owner) -> None:
    """`PL-QW1Z` Q4: order and a separator, the set's own order within each group."""

    workspaces = owner.strip.workspaces
    assert [ws.name for ws in workspaces.workspaces] == [
        "Default",
        "Default (copy)",
        "Induction",
        "Maintenance",
    ]
    assert display_order(workspaces) == (0, 2, 3, 1)
    assert owner.names == ["Default", "Induction", "Maintenance", "Default (copy)"]

    row = owner.strip.row
    items = [row.itemAt(i) for i in range(row.count())]
    widgets = [None if item is None else item.widget() for item in items]
    assert widgets.index(owner.strip.separator) == 3
    assert owner.strip.separator.isVisible()
    assert widgets[5] is owner.strip.add_button


def test_the_rule_is_hidden_while_one_group_has_every_tab(application: QApplication) -> None:
    made = _Owner(shipped_workspaces())

    assert not made.strip.separator.isVisible()
    made.strip.close()


def test_the_current_tab_is_the_checked_one_and_a_click_makes_another_current(
    owner: _Owner,
) -> None:
    assert [tab.isChecked() for tab in owner.strip.tabs] == [True, False, False, False]

    QTest.mouseClick(owner.strip.tab_at(2), Qt.MouseButton.LeftButton)

    assert owner.changes[-1].current.name == "Induction"
    assert [tab.isChecked() for tab in owner.strip.tabs] == [False, True, False, False]


def test_a_click_on_the_current_tab_changes_nothing_and_leaves_it_checked(owner: _Owner) -> None:
    QTest.mouseClick(owner.strip.tab_at(0), Qt.MouseButton.LeftButton)

    assert owner.changes == []
    assert owner.strip.tab_at(0).isChecked()


def test_the_menu_lists_q3s_entries_in_order(owner: _Owner) -> None:
    """Rename, Duplicate, Move left, Move right, pin, Reset on a shipped tab, then Delete."""

    assert _entries(owner.strip, 0) == [
        (RENAME_LABEL, True),
        (DUPLICATE_LABEL, True),
        (MOVE_LEFT_LABEL, False),
        (MOVE_RIGHT_LABEL, True),
        ("Pin Run 1", True),
        (RESET_LABEL, True),
        (DELETE_LABEL, True),
    ]
    # The reader's own Workspace has no shipped file to reset to.
    assert _entries(owner.strip, 1) == [
        (RENAME_LABEL, True),
        (DUPLICATE_LABEL, True),
        (MOVE_LEFT_LABEL, False),
        (MOVE_RIGHT_LABEL, False),
        ("Pin Run 1", True),
        (DELETE_LABEL, True),
    ]


def test_moves_stay_inside_the_tabs_group(owner: _Owner) -> None:
    """Maintenance is last of the shipped tabs, so it cannot move right onto the reader's own."""

    operations = tab_operations(owner.strip.workspaces, 3, (_RUN_1,))
    right = _named(operations, MOVE_RIGHT_LABEL)

    assert not right.available
    assert right.refusal == "Not available: this tab is already last in its group."

    left = _named(operations, MOVE_LEFT_LABEL).result
    assert left is not None
    assert [ws.name for ws in left.workspaces] == [
        "Default",
        "Default (copy)",
        "Maintenance",
        "Induction",
    ]
    # Default stays the current Workspace.
    assert left.current.name == "Default"


def test_a_move_across_a_tab_of_the_other_group_lands_beside_its_neighbour() -> None:
    """Induction's left neighbour in the strip is Default, two places along the set."""

    workspaces = _with_mine(shipped_workspaces())
    moved = _named(tab_operations(workspaces, 2, ()), MOVE_LEFT_LABEL).result

    assert moved is not None
    assert display_order(moved) == (0, 1, 3, 2)
    assert [moved.workspaces[i].name for i in display_order(moved)] == [
        "Induction",
        "Default",
        "Maintenance",
        "Default (copy)",
    ]


def test_each_open_run_can_be_pinned_and_a_pinned_run_unpinned(application: QApplication) -> None:
    """`PL-WV9K` Q6: a Workspace pins one run by its identity, and unpins it."""

    workspaces = shipped_workspaces()
    pins = [
        operation
        for operation in tab_operations(workspaces, 1, (_RUN_1, _RUN_2))
        if operation.label.startswith("Pin")
    ]

    assert [pin.label for pin in pins] == ["Pin Run 1", "Pin Run 2"]
    pinned = pins[1].result
    assert pinned is not None
    assert pinned.workspaces[1].pinned_run == _RUN_2
    assert pinned.workspaces[0].pinned_run is None

    # A pinned run that has closed can still be unpinned.
    unpin = _named(tab_operations(pinned, 1, (_RUN_1,)), "Unpin Run 2")
    assert unpin.result is not None
    assert unpin.result.workspaces[1].pinned_run is None


def test_no_run_to_pin_is_shown_unavailable() -> None:
    pin = _named(tab_operations(shipped_workspaces(), 0, ()), "Pin run")

    assert not pin.available
    assert pin.refusal == "Not available: no run is open."


def test_the_last_workspaces_delete_is_shown_unavailable_with_its_reason() -> None:
    """`PL-WV9K` Q2: the floor is shown, never met as an error after a click."""

    lone = WorkspaceSet((shipped_workspace(ShippedWorkspaceId("default")),), 0)
    delete = _named(tab_operations(lone, 0, ()), DELETE_LABEL)

    assert not delete.available
    assert delete.refusal == "Not available: there is always at least one Workspace."


def test_delete_asks_first_naming_the_workspace_and_its_origin(owner: _Owner) -> None:
    menu = owner.strip.menu_for(2)
    entry = next(action for action in menu.actions() if action.text() == DELETE_LABEL)
    entry.trigger()

    question = owner.strip.question
    assert question is not None
    assert owner.changes == []
    texts = [label.text() for label in question.findChildren(type(owner.strip.refusal_label))]
    assert (
        'Delete the shipped Workspace "Induction"? "Restore shipped Workspaces" in the Layout '
        "menu brings back the shipped version." in texts
    )

    question.keep_button.click()
    assert owner.changes == []

    delete = _named(owner.strip.operations(1), DELETE_LABEL)
    assert delete.question is not None
    assert delete.question.text == 'Delete your Workspace "Default (copy)"? This cannot be undone.'
    owner.strip.choose(delete)
    question = owner.strip.question
    assert question is not None
    question.proceed_button.click()

    assert owner.names == ["Default", "Induction", "Maintenance"]


def test_reset_asks_first_and_restores_the_shipped_layout_and_name(owner: _Owner) -> None:
    workspaces = owner.strip.workspaces
    induction = workspaces.workspaces[2]
    edited = induction.renamed(WorkspaceName("Mine now")).with_view_state(
        AreaId(1), induction.layout.areas()[0].view, {"version": 1}
    )
    owner.change(workspaces.replace(2, edited))

    reset = _named(owner.strip.operations(2), RESET_LABEL)
    assert reset.question is not None
    assert reset.question.text.startswith(
        'Reset "Mine now" to the Workspace shipped as "Induction"?'
    )
    owner.strip.choose(reset)
    question = owner.strip.question
    assert question is not None
    question.accept()

    assert owner.changes[-1].workspaces[2] == shipped_workspace(ShippedWorkspaceId("induction"))


def test_a_reset_the_set_refuses_is_shown_unavailable(application: QApplication) -> None:
    """A shipped file that does not read, or a name another tab holds, is the reason shown."""

    def broken(shipped_id: ShippedWorkspaceId) -> Workspace:
        raise ShippedWorkspaceError(f"{shipped_id}.json does not read")

    reset = _named(tab_operations(shipped_workspaces(), 0, (), broken), RESET_LABEL)

    assert not reset.available
    assert reset.refusal == "Not available: default.json does not read"


def test_a_double_click_renames_in_place_and_return_takes_the_name(owner: _Owner) -> None:
    QTest.mouseDClick(owner.strip.tab_at(1), Qt.MouseButton.LeftButton)
    editor = owner.strip.editor

    assert editor is not None
    assert editor.text() == "Default (copy)"
    editor.setText("Wash-in study")
    QTest.keyClick(editor, Qt.Key.Key_Return)

    assert owner.strip.editor is None
    assert owner.changes[-1].workspaces[1].name == "Wash-in study"
    assert owner.names[-1] == "Wash-in study"


def test_a_taken_name_is_refused_and_the_editor_stays_open(owner: _Owner) -> None:
    owner.strip.rename(1)
    editor = owner.strip.editor
    assert editor is not None
    editor.setText("Induction")
    QTest.keyClick(editor, Qt.Key.Key_Return)

    assert owner.strip.editor is editor
    assert owner.changes == []
    assert owner.strip.refusal_label.isVisible()
    assert "Induction" in owner.strip.refusal_label.text()

    QTest.keyClick(editor, Qt.Key.Key_Escape)
    assert owner.strip.editor is None
    assert not owner.strip.refusal_label.isVisible()
    assert owner.names[-1] == "Default (copy)"


def test_f2_renames_the_focused_tab(owner: _Owner) -> None:
    tab = owner.strip.tab_at(3)
    tab.setFocus()
    QTest.keyClick(tab, Qt.Key.Key_F2)

    editor = owner.strip.editor
    assert editor is not None
    assert editor.text() == "Maintenance"


def test_the_arrow_keys_move_the_focus_along_the_strip(
    owner: _Owner, application: QApplication
) -> None:
    owner.strip.activateWindow()
    application.processEvents()
    first = owner.strip.tabs[0]
    first.setFocus()
    assert application.focusWidget() is first
    QTest.keyClick(first, Qt.Key.Key_Right)

    assert application.focusWidget() is owner.strip.tabs[1]


def test_plus_duplicates_the_current_workspace_and_opens_it_for_renaming(owner: _Owner) -> None:
    QTest.mouseClick(owner.strip.tab_at(2), Qt.MouseButton.LeftButton)
    owner.strip.add_button.click()

    made = owner.changes[-1]
    assert made.current.name == "Induction (copy)"
    assert not made.current.origin.is_shipped
    editor = owner.strip.editor
    assert editor is not None
    assert editor.index == made.active
    assert editor.text() == "Induction (copy)"


def test_shift_f10_and_the_menu_key_open_the_tabs_menu(
    owner: _Owner, monkeypatch: pytest.MonkeyPatch
) -> None:
    opened: list[int] = []
    monkeypatch.setattr(owner.strip, "open_menu", lambda index, at: opened.append(index))

    tab = owner.strip.tab_at(2)
    QTest.keyClick(tab, Qt.Key.Key_F10, Qt.KeyboardModifier.ShiftModifier)
    at = QPoint(2, 2)
    keyboard = QContextMenuEvent.Reason.Keyboard
    QApplication.sendEvent(tab, QContextMenuEvent(keyboard, at, tab.mapToGlobal(at)))

    assert opened == [2, 2]


# --------------------------------------------------------------- the dashboard


@pytest.fixture
def shown(application: QApplication) -> Iterator[list[SimulationView]]:
    """Every dashboard a test shows, closed after it."""

    views: list[SimulationView] = []
    yield views

    for view in views:
        view.stop_timers()
        view.close()
        view.deleteLater()

    application.processEvents()


def _dashboard(
    application: QApplication,
    shown: list[SimulationView],
    *controllers: SimulationController,
    workspaces: WorkspaceSet | None = None,
) -> SimulationView:
    """A dashboard over these runs, numbered from 1 in session `_SESSION`, shown and drawn once."""

    view = SimulationView(
        controllers, run_identities=RunIdentities(_SESSION), workspaces=workspaces
    )
    shown.append(view)
    view.resize(1400, 1000)
    view.show()
    application.processEvents()
    view.present(False)

    return view


def _ran(seconds: float) -> SimulationController:
    controller = SimulationController()

    for _ in range(round(seconds / SIMULATION_STEP_S)):
        controller.advance(SIMULATION_STEP_S)

    return controller


def _concentration(view: SimulationView) -> ConcentrationView:
    return next(v for v in view.layout_container.views() if isinstance(v, ConcentrationView))


def test_the_dashboard_opens_on_the_shipped_default_with_the_strip_over_the_areas(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """`PL-QW1Z` Q1: the strip sits under the region and directly above the Areas."""

    view = _dashboard(application, shown, SimulationController())

    assert view.workspaces.current.name == "Default"
    assert view.layout_container.model == shipped_workspace(ShippedWorkspaceId("default")).layout
    strip, areas = view.tab_strip, view.layout_container
    assert strip.parentWidget() is areas.parentWidget()
    assert strip.mapTo(view, QPoint(0, strip.height())).y() <= areas.mapTo(view, QPoint()).y()
    region = view.unconditional_region
    assert region.mapTo(view, QPoint(0, region.height())).y() <= strip.mapTo(view, QPoint()).y()
    assert [tab.text() for tab in strip.tabs] == ["Default", "Induction", "Maintenance"]


def test_a_tab_switches_the_layout_and_leaves_the_run(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """`PL-WV9K` Q6: a switch changes which Views are drawn, and the run is not touched."""

    controller = _ran(30.0)
    before = controller.snapshot()
    view = _dashboard(application, shown, controller)
    run = view.runs[0]
    readouts = run.unconditional_widgets()
    # The notice banner is hidden while it has nothing to say, so what is
    # held is that each widget is shown as it was before the switch.
    visible = {value: widget.isVisibleTo(view) for value, widget in readouts.items()}

    QTest.mouseClick(view.tab_strip.tab_at(1), Qt.MouseButton.LeftButton)

    induction = shipped_workspace(ShippedWorkspaceId("induction"))
    assert view.workspaces.current.name == "Induction"
    assert view.layout_container.model == induction.layout
    assert [type(v).__name__ for v in view.layout_container.views()] == [
        "ConcentrationView",
        "WashInView",
        "ParameterControlsView",
    ]
    # The same run, at the same instant, with the same readouts in the region.
    assert view.runs == (run,)
    assert run.controller is controller
    assert controller.snapshot().elapsed_s == before.elapsed_s
    assert run.unconditional_widgets() == readouts

    for widget in readouts.values():
        assert widget is not None
        assert not view.layout_container.isAncestorOf(widget)

    assert {value: widget.isVisibleTo(view) for value, widget in readouts.items()} == visible


def test_the_induction_tab_opens_its_chart_on_the_15_minute_window(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """`PL-L59K`: switching to Induction draws its concentration chart from its saved window.

    The shipped file saves the chart at 15 minutes. The chart must draw a
    15-minute frame, not "Fit run", once the tab loads that state.
    """

    view = _dashboard(application, shown, _ran(30.0))

    QTest.mouseClick(view.tab_strip.tab_at(1), Qt.MouseButton.LeftButton)

    chart = _concentration(view)
    frame = chart.chart.frame
    assert view.workspaces.current.name == "Induction"
    assert chart.time_base_selector.currentData() == "900.0"
    assert frame is not None and not frame.fitted
    assert frame.time_base == time_base_for_span(900.0)
    assert (frame.start_s, frame.stop_s) == (0.0, 900.0)


def test_a_workspace_left_and_come_back_to_is_as_it_was_left(
    application: QApplication, shown: list[SimulationView]
) -> None:
    view = _dashboard(application, shown, SimulationController())
    view.layout_container.choose_view(AreaId(2), WASH_IN)
    left = view.layout_container.model

    QTest.mouseClick(view.tab_strip.tab_at(2), Qt.MouseButton.LeftButton)
    assert view.workspaces.current.name == "Maintenance"
    QTest.mouseClick(view.tab_strip.tab_at(0), Qt.MouseButton.LeftButton)

    assert view.layout_container.model == left
    assert view.workspaces.workspaces[0].layout == left


def test_plus_copies_the_layout_the_reader_sees(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """The copy is of the Workspace as drawn, after the reader's change, not as it was opened."""

    view = _dashboard(application, shown, SimulationController())
    view.layout_container.choose_view(AreaId(2), WASH_IN)
    seen = view.layout_container.model
    view.tab_strip.add_button.click()

    assert view.workspaces.current.name == "Default (copy)"
    assert view.workspaces.current.layout == seen
    assert view.layout_container.model == seen
    assert view.tab_strip.editor is not None


def test_a_pinned_workspace_draws_its_run_alone_and_names_it_on_every_area(
    application: QApplication, shown: list[SimulationView]
) -> None:
    view = _dashboard(application, shown, SimulationController(), SimulationController())
    assert _concentration(view).legend._run_names == ("Run 1", "Run 2")

    pin = _named(view.tab_strip.operations(0), "Pin Run 2")
    view.tab_strip.choose(pin)

    assert view.workspaces.current.pinned_run == _RUN_2
    assert _concentration(view).legend._run_names == ("Run 2",)

    for area in view.layout_container.model.areas():
        frame = view.layout_container.frame(area.id)
        assert frame.pin_label.isVisible()
        assert frame.pin_label.text() == "Run 2"
        assert frame.content.isVisible()

    # Both runs are still open, and the region still reads both.
    assert len(view.runs) == 2

    view.tab_strip.choose(_named(view.tab_strip.operations(0), "Unpin Run 2"))

    assert _concentration(view).legend._run_names == ("Run 1", "Run 2")
    assert not view.layout_container.frame(AreaId(1)).pin_label.isVisible()


def test_a_pinned_run_that_is_not_open_is_stated_in_every_area_and_no_other_run_is_shown(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """A run of an earlier session, numbered alike, is a different run (`PL-7Z84`)."""

    earlier = RunId(SessionToken("f" * 32), 1)
    shipped = shipped_workspaces()
    pinned = shipped.replace(0, shipped.current.pinned_to(earlier))
    view = _dashboard(application, shown, SimulationController(), workspaces=pinned)

    for area in view.layout_container.model.areas():
        frame = view.layout_container.frame(area.id)
        notice = frame.absent_notice
        assert notice is not None
        assert notice.isVisible()
        assert notice.title_label.text() == "Run 1 is not open."
        assert not frame.content.isVisible()

    # The region still shows the open run, which the pin never touches.
    assert view.runs[0].run_id == _RUN_1
    unpinned = _dashboard(application, shown, SimulationController())
    assert {
        value: widget.isVisibleTo(view)
        for value, widget in view.runs[0].unconditional_widgets().items()
    } == {
        value: widget.isVisibleTo(unpinned)
        for value, widget in unpinned.runs[0].unconditional_widgets().items()
    }

    QTest.mouseClick(view.tab_strip.tab_at(1), Qt.MouseButton.LeftButton)
    # A widget added to a shown layout is shown on the next pass of the loop.
    application.processEvents()

    for area in view.layout_container.model.areas():
        frame = view.layout_container.frame(area.id)
        assert frame.absent_notice is None or not frame.absent_notice.isVisible()
        assert frame.content.isVisible()
