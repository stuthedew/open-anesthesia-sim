"""Headless tests that every layout operation is reachable without a drag.

`PL-M352` asks that split, join, resize, swap, close, Workspace switch,
rename, duplicate and delete each be reachable from a menu and from the
keyboard. Split, join, swap and close are in each Area's menu, which Shift+F10
on the Area's View chooser opens (`PL-R5G4`). Resize uses the "Resize"
submenu, which gives a border the keyboard focus. The arrow keys then move the
border. Switching Workspace uses Ctrl+PageUp and Ctrl+PageDown, or Previous
and Next Workspace in a tab's menu. Rename, duplicate and delete are in each
tab's menu, which Shift+F10 on the tab opens, and again in the Layout menu's
"This Workspace" submenu.

The first test drives the whole set with key presses. It gives each control
the focus in code, as the Tab key would. The tab-order tests check that each
control is in the tab order. No test here presses, moves or releases the
mouse, so none synthesises a drag. Each test works out its expected layout or
size from pixel measurements or from the operation itself. It never reads its
expected values back from `AreaLayout`, the code under test. The tests render
under the `offscreen` platform that `tests/conftest.py` selects. A desktop
makes the window active again when a popup menu closes, but that platform does
not. So the tests activate the window themselves.
"""

from collections.abc import Iterator
from functools import partial
from pathlib import Path

import pytest
from PySide6.QtCore import QEvent, QPoint, Qt, QTimer
from PySide6.QtGui import QContextMenuEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialog, QMenu, QSplitter, QToolButton, QWidget

from anesthesia_sim.app.area_layout import (
    CLOSE_AREA_LABEL,
    JOIN_WITH_LABEL,
    RESIZE_LABEL,
    SPLIT_SIDE_BY_SIDE_LABEL,
    SPLIT_STACKED_LABEL,
    SWAP_WITH_LABEL,
    AreaLayout,
    AreaMenu,
    _AreaHandle,
)
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.theme import AREA_HANDLE_WIDTH, AREA_KEYBOARD_STEP
from anesthesia_sim.app.view_contract import (
    STATE_VERSION_KEY,
    SavedState,
    ViewContext,
    ViewRequests,
    ViewTick,
)
from anesthesia_sim.app.view_registry import PARAMETER_CONTROLS, RegisteredView, registry
from anesthesia_sim.app.workspace_tabs import (
    DELETE_LABEL,
    DUPLICATE_LABEL,
    MOVE_LEFT_LABEL,
    MOVE_RIGHT_LABEL,
    NEXT_WORKSPACE_LABEL,
    PREVIOUS_WORKSPACE_LABEL,
    RENAME_LABEL,
    RESET_ALL_LABEL,
    RESTORE_SHIPPED_LABEL,
    SAVE_AS_DEFAULT_LABEL,
    THIS_WORKSPACE_LABEL,
    WorkspaceQuestionDialog,
    WorkspaceTabs,
    display_order,
)
from anesthesia_sim.layout.model import Handle, LayoutModel
from anesthesia_sim.layout.shipped import shipped_workspace, shipped_workspaces
from anesthesia_sim.layout.store import WORKSPACES_FILE_NAME, Source, WorkspaceStore
from anesthesia_sim.layout.tree import Area, AreaId, Node, Orientation, Split, ViewKind, Window
from anesthesia_sim.layout.workspace import ShippedWorkspaceId, WorkspaceName, WorkspaceSet

_VIEW = ViewKind("test_view")
_REQUESTS = ViewRequests(lambda _time_base: None, lambda _quantity, _shown: None)

# A container this size leaves 800 px for the children of a split of two once
# the handle is taken out, so a step reads straight off as pixels.
_SIDE_PX = 800 + AREA_HANDLE_WIDTH


class _BlankView(QWidget):
    """A View that draws nothing and is small enough never to stop a border."""

    def __init__(self, context: ViewContext) -> None:
        super().__init__()
        self.setMinimumSize(10, 10)

    def refresh(self, tick: ViewTick) -> None:
        pass

    @property
    def owes_a_frame(self) -> bool:
        return False

    def frame_width_px(self) -> float | None:
        return None

    def save_state(self) -> SavedState:
        return {STATE_VERSION_KEY: 1}

    def painted_strings(self) -> tuple[str, ...]:
        return ()


_REGISTERED = registry(RegisteredView(_VIEW, "Blank view", _BlankView))


def _area(number: int) -> Area:
    return Area(AreaId(number), _VIEW)


def _row(sizes: tuple[float, ...], *children: Node) -> Split:
    return Split(Orientation.ROW, sizes, children)


def _column(sizes: tuple[float, ...], *children: Node) -> Split:
    return Split(Orientation.COLUMN, sizes, children)


def _layout(tree: Node, next_id: int) -> LayoutModel:
    return LayoutModel((Window(tree),), AreaId(next_id))


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


@pytest.fixture
def shown(application: QApplication) -> Iterator[list[QWidget]]:
    """Every window a test shows, closed after it."""

    windows: list[QWidget] = []
    yield windows

    for window in windows:
        if isinstance(window, SimulationView):
            window.stop_timers()

        window.close()
        window.deleteLater()

    application.processEvents()


def _activate(application: QApplication, window: QWidget) -> None:
    """Make `window` the active window, as a desktop does when a popup menu closes."""

    window.activateWindow()
    assert QTest.qWaitForWindowActive(window, 2000)
    application.processEvents()


def _container(application: QApplication, shown: list[QWidget], model: LayoutModel) -> AreaLayout:
    container = AreaLayout(model, _REQUESTS, registered=_REGISTERED)
    container.resize(_SIDE_PX, _SIDE_PX)
    container.show()
    shown.append(container)
    _activate(application, container)

    return container


def _dashboard(
    application: QApplication, shown: list[QWidget], store: WorkspaceStore | None = None
) -> SimulationView:
    workspaces = None if store is None else store.load(shipped_workspaces()).workspaces
    view = SimulationView((SimulationController(),), workspaces=workspaces, store=store)
    view.resize(1400, 1000)
    view.show()
    shown.append(view)
    _activate(application, view)
    view.present(False)

    return view


def _handle(container: AreaLayout, handle: Handle) -> _AreaHandle:
    """The widget drawing `handle`, found through the splitters rather than the adapter."""

    splitters = [
        splitter
        for splitter in container.findChildren(QSplitter)
        if getattr(splitter, "path", None) == handle.path
    ]
    assert len(splitters) == 1
    widget = splitters[0].handle(handle.index + 1)
    assert isinstance(widget, _AreaHandle)

    return widget


def _choose_by_keys(
    application: QApplication,
    window: QWidget,
    control: QWidget,
    path: tuple[str, ...],
    *,
    context: bool = False,
) -> None:
    """Open a menu from `control` by key, and walk `path` with Down, Right and Return.

    Space opens a button's own menu. With `context`, Shift+F10 opens the
    control's context menu instead, as for an Area's chooser or a tab. A
    button's menu runs its own event loop, so the walk is queued before the
    key is pressed. The queued walk then waits until the menu is open. At the
    end of the walk, every popup is closed, whatever the walk found. So a
    missing entry fails the test instead of leaving the test waiting on a menu.
    """

    reached: list[str] = []
    finished = False

    def walk(tries: int) -> None:
        popup = QApplication.activePopupWidget()

        if finished:
            return

        if popup is None and tries > 0:
            QTimer.singleShot(10, partial(walk, tries - 1))
            return

        try:
            for depth, label in enumerate(path):
                if not isinstance(popup, QMenu):
                    return

                for _ in range(len(popup.actions()) + 1):
                    active = popup.activeAction()

                    if active is not None and active.text() == label:
                        break

                    QTest.keyClick(popup, Qt.Key.Key_Down)
                else:
                    return

                reached.append(label)

                if depth < len(path) - 1:
                    QTest.keyClick(popup, Qt.Key.Key_Right)
                    popup = QApplication.activePopupWidget()
                else:
                    QTest.keyClick(popup, Qt.Key.Key_Return)
        finally:
            while (left_open := QApplication.activePopupWidget()) is not None:
                left_open.close()

    assert control.focusPolicy() & Qt.FocusPolicy.TabFocus
    control.setFocus(Qt.FocusReason.TabFocusReason)
    application.processEvents()
    QTimer.singleShot(0, partial(walk, 100))

    if context:
        QTest.keyClick(control, Qt.Key.Key_F10, Qt.KeyboardModifier.ShiftModifier)
    else:
        QTest.keyClick(control, Qt.Key.Key_Space)

    application.processEvents()
    finished = True
    _activate(application, window)

    assert reached == list(path)


def _proceed_by_keys(application: QApplication, dialog: QDialog) -> None:
    """Tab to the open question's proceed button, then press Space on it."""

    assert isinstance(dialog, WorkspaceQuestionDialog)
    _activate(application, dialog)

    for _ in range(4):
        if dialog.focusWidget() is dialog.proceed_button:
            break

        QTest.keyClick(dialog, Qt.Key.Key_Tab)

    assert dialog.focusWidget() is dialog.proceed_button
    QTest.keyClick(dialog.proceed_button, Qt.Key.Key_Space)
    application.processEvents()


def _menu(view: SimulationView, area_id: AreaId) -> AreaMenu:
    menu = view.layout_container.frame(area_id).menu
    assert menu is not None

    return menu


def _choose_in_area_menu(
    application: QApplication, view: SimulationView, area_id: AreaId, path: tuple[str, ...]
) -> None:
    """Walk `path` in the Area's menu, opened with Shift+F10 on its View chooser."""

    chooser = view.layout_container.frame(area_id).chooser
    _choose_by_keys(application, view, chooser, path, context=True)


def _choose_in_tab_menu(
    application: QApplication, view: SimulationView, path: tuple[str, ...]
) -> None:
    """Walk `path` in the current tab's menu, opened with Shift+F10 on the tab."""

    tab = view.tab_strip.tab_at(view.workspaces.active)
    _choose_by_keys(application, view, tab, path, context=True)


def _entry(view: SimulationView, area_id: AreaId, group: str) -> str:
    """The label of the first available entry of `group` in the Area's menu."""

    return next(
        operation.label
        for operation in view.layout_container.operations(area_id)
        if operation.group == group and operation.available
    )


def test_every_layout_operation_is_reachable_from_the_keyboard(
    application: QApplication, shown: list[QWidget]
) -> None:
    """Resize, split, swap, join, close, switch, rename, duplicate and delete, by key alone."""

    view = _dashboard(application, shown)
    areas = view.layout_container
    strip = view.tab_strip
    first = areas.model.areas()[0].id
    kinds = {area.id: area.view for area in areas.model.areas()}

    # Resize. The Resize submenu gives the first Area's right border the focus.
    # Left then moves the border one step from where it is drawn, so the
    # first Area is drawn AREA_KEYBOARD_STEP px narrower (`PL-4L8B`).
    before_px = areas.frame(first).width()
    _choose_in_area_menu(application, view, first, (RESIZE_LABEL, "Right border"))
    border = QApplication.focusWidget()
    assert isinstance(border, _AreaHandle)
    QTest.keyClick(border, Qt.Key.Key_Left)
    application.processEvents()
    assert areas.frame(first).width() == before_px - AREA_KEYBOARD_STEP

    # Split: the first Area becomes two side by side, both showing its View.
    _choose_in_area_menu(application, view, first, (SPLIT_SIDE_BY_SIDE_LABEL,))
    assert len(areas.model.areas()) == 3
    made = next(area.id for area in areas.model.areas() if area.id not in kinds)
    assert areas.model.area(made).view == kinds[first]

    # Swap: the first Area and another exchange their places.
    label = _entry(view, first, SWAP_WITH_LABEL)
    place = areas.model.rectangle(first)
    _choose_in_area_menu(application, view, first, (SWAP_WITH_LABEL, label))
    assert areas.model.rectangle(first) != place
    assert len(areas.model.areas()) == 3

    # Join: the first Area takes a neighbour's place, so one Area fewer.
    label = _entry(view, first, JOIN_WITH_LABEL)
    _choose_in_area_menu(application, view, first, (JOIN_WITH_LABEL, label))
    assert len(areas.model.areas()) == 2

    # Close: a neighbour takes the closed Area's place, leaving one.
    survivor = next(area.id for area in areas.model.areas() if area.id != first)
    _choose_in_area_menu(application, view, survivor, (CLOSE_AREA_LABEL,))
    assert len(areas.model.areas()) == 1

    # Switch Workspace: Ctrl+PageDown and Ctrl+PageUp, then a tab's menu.
    order = display_order(view.workspaces)
    QTest.keyClick(strip.add_button, Qt.Key.Key_PageDown, Qt.KeyboardModifier.ControlModifier)
    assert view.workspaces.active == order[1]
    QTest.keyClick(strip.add_button, Qt.Key.Key_PageUp, Qt.KeyboardModifier.ControlModifier)
    assert view.workspaces.active == order[0]
    # A shortcut consumes its key press, and QTest then leaves Ctrl held in
    # the application's modifier state, so Ctrl is let go here by hand.
    QTest.keyClick(strip.add_button, Qt.Key.Key_Control)
    _choose_in_tab_menu(application, view, (NEXT_WORKSPACE_LABEL,))
    _choose_in_tab_menu(application, view, (NEXT_WORKSPACE_LABEL,))
    assert view.workspaces.active == order[2]

    # Rename: F2 on the focused tab, a new name, Return.
    tab = strip.tab_at(view.workspaces.active)
    tab.setFocus(Qt.FocusReason.TabFocusReason)
    QTest.keyClick(tab, Qt.Key.Key_F2)
    editor = strip.editor
    assert editor is not None
    QTest.keyClicks(editor, "Mine")
    QTest.keyClick(editor, Qt.Key.Key_Return)
    assert view.workspaces.current.name == "Mine"

    # Duplicate, from the tab's menu.
    count = len(view.workspaces.workspaces)
    _choose_in_tab_menu(application, view, (DUPLICATE_LABEL,))
    assert len(view.workspaces.workspaces) == count + 1

    # Delete, which asks first: Tab to the dialog's Delete button, then Space.
    if strip.editor is not None:
        QTest.keyClick(strip.editor, Qt.Key.Key_Escape)
    _choose_in_tab_menu(application, view, (DELETE_LABEL,))
    dialog = strip.question
    assert dialog is not None
    _activate(application, dialog)

    for _ in range(4):
        if dialog.focusWidget() is dialog.proceed_button:
            break

        QTest.keyClick(dialog, Qt.Key.Key_Tab)

    assert dialog.focusWidget() is dialog.proceed_button
    QTest.keyClick(dialog.proceed_button, Qt.Key.Key_Space)
    application.processEvents()
    assert len(view.workspaces.workspaces) == count


def test_moving_a_tab_and_stacking_a_split_are_reachable_from_the_keyboard(
    application: QApplication, shown: list[QWidget]
) -> None:
    """Move right, Move left and a stacked split, by key alone (`PL-DZL0`).

    The test above drives every other layout operation by key. The tab order
    expected here is written out from the shipped order, Default, Induction
    and Maintenance, rather than read from the strip.
    """

    view = _dashboard(application, shown)
    areas = view.layout_container
    first = areas.model.areas()[0].id
    kinds = {area.id: area.view for area in areas.model.areas()}
    place = areas.model.rectangle(first)

    # Split stacked: the first Area becomes two, one above the other, across
    # the width it had.
    _choose_in_area_menu(application, view, first, (SPLIT_STACKED_LABEL,))
    assert len(areas.model.areas()) == len(kinds) + 1
    made = next(area.id for area in areas.model.areas() if area.id not in kinds)
    upper, lower = sorted((first, made), key=lambda area_id: areas.model.rectangle(area_id).top)

    for area_id in (upper, lower):
        rectangle = areas.model.rectangle(area_id)
        assert (rectangle.left, rectangle.right) == (place.left, place.right)

    assert areas.model.rectangle(upper).top == place.top
    assert areas.model.rectangle(upper).bottom == areas.model.rectangle(lower).top
    assert areas.model.rectangle(lower).bottom == place.bottom

    def tab_names() -> list[str]:
        return [str(view.workspaces.workspaces[i].name) for i in display_order(view.workspaces)]

    assert tab_names() == ["Default", "Induction", "Maintenance"]
    assert view.workspaces.current.name == "Default"

    # Move right, then Move left, from the current tab's menu.
    _choose_in_tab_menu(application, view, (MOVE_RIGHT_LABEL,))
    assert tab_names() == ["Induction", "Default", "Maintenance"]
    assert view.workspaces.current.name == "Default"

    _choose_in_tab_menu(application, view, (MOVE_LEFT_LABEL,))
    assert tab_names() == ["Default", "Induction", "Maintenance"]
    assert view.workspaces.current.name == "Default"


def test_every_layout_operation_is_reachable_from_a_menu(
    application: QApplication, shown: list[QWidget]
) -> None:
    """Each operation is an entry in the Area menu, the Layout menu or a tab's menu."""

    view = _dashboard(application, shown)
    first = view.layout_container.model.areas()[0].id
    area_menu = _menu(view, first)
    area_menu.fill()
    area_entries = [action.text() for action in area_menu.actions()]

    for label in (
        SPLIT_SIDE_BY_SIDE_LABEL,
        SPLIT_STACKED_LABEL,
        JOIN_WITH_LABEL,
        SWAP_WITH_LABEL,
        RESIZE_LABEL,
        CLOSE_AREA_LABEL,
    ):
        assert label in area_entries

    strip = view.tab_strip
    strip.layout_menu.fill()
    layout_actions = {action.text(): action for action in strip.layout_menu.actions()}
    names = [strip.workspaces.workspaces[index].name for index in display_order(strip.workspaces)]

    for label in (*names, PREVIOUS_WORKSPACE_LABEL, NEXT_WORKSPACE_LABEL, THIS_WORKSPACE_LABEL):
        assert label in layout_actions

    this_workspace = layout_actions[THIS_WORKSPACE_LABEL].menu()
    assert isinstance(this_workspace, QMenu)
    entries = [action.text() for action in this_workspace.actions()]

    for label in (RENAME_LABEL, DUPLICATE_LABEL, DELETE_LABEL):
        assert label in entries

    tab_entries = [action.text() for action in strip.menu_for(strip.workspaces.active).actions()]
    assert tab_entries[: len(entries)] == entries

    for label in (
        PREVIOUS_WORKSPACE_LABEL,
        NEXT_WORKSPACE_LABEL,
        SAVE_AS_DEFAULT_LABEL,
        RESTORE_SHIPPED_LABEL,
        RESET_ALL_LABEL,
    ):
        assert label in tab_entries
        assert label in layout_actions

    layout_actions[names[1]].trigger()
    assert view.workspaces.active == display_order(view.workspaces)[1]


def test_the_layout_menu_lists_every_workspace_in_tab_order_with_the_current_checked(
    application: QApplication,
) -> None:
    workspaces = shipped_workspaces().duplicate(0).activate(2)
    strip = WorkspaceTabs(workspaces, lambda _set: None, lambda: ())
    strip.layout_menu.fill()
    actions = strip.layout_menu.actions()
    names = [workspaces.workspaces[index].name for index in display_order(workspaces)]

    assert [action.text() for action in actions[: len(names)]] == names
    assert [action.isChecked() for action in actions[: len(names)]] == [
        index == 2 for index in display_order(workspaces)
    ]
    assert strip.previous_action.shortcut().toString() == "Ctrl+PgUp"
    assert strip.next_action.shortcut().toString() == "Ctrl+PgDown"


def test_next_and_previous_workspace_follow_the_tabs_and_wrap_round(
    application: QApplication,
) -> None:
    """Shipped tabs first, then the reader's own; past either end comes the other, as in Blender."""

    workspaces = shipped_workspaces().duplicate(0).activate(0)
    order = display_order(workspaces)
    assert len(order) >= 3

    def change(made: WorkspaceSet) -> None:
        strip.show_set(made)

    strip = WorkspaceTabs(workspaces, change, lambda: ())

    strip.next_action.trigger()
    assert strip.workspaces.active == order[1]
    strip.previous_action.trigger()
    strip.previous_action.trigger()
    assert strip.workspaces.active == order[-1]
    strip.next_action.trigger()
    assert strip.workspaces.active == order[0]


def test_next_workspace_during_a_rename_takes_the_typed_name_before_it_switches(
    application: QApplication,
) -> None:
    """Ctrl+PgDown reaches the window while a name is being typed, and kept the name from it."""

    workspaces = shipped_workspaces().duplicate(0).activate(0)
    order = display_order(workspaces)

    def change(made: WorkspaceSet) -> None:
        strip.show_set(made)

    strip = WorkspaceTabs(workspaces, change, lambda: ())
    strip.rename(order[0])
    editor = strip.editor
    assert editor is not None
    editor.setText("Mine")

    strip.next_action.trigger()

    assert strip.editor is None
    assert strip.workspaces.workspaces[order[0]].name == "Mine"
    assert strip.workspaces.active == order[1]


def test_a_menu_written_at_each_opening_keeps_only_the_submenus_of_the_last_one(
    application: QApplication, shown: list[QWidget]
) -> None:
    """Three openings leave the submenus of one, not three, in each menu written on opening."""

    strip = WorkspaceTabs(shipped_workspaces(), lambda _set: None, lambda: ())
    container = _container(
        application, shown, _layout(_row((1 / 3, 1 / 3, 1 / 3), _area(1), _area(2), _area(3)), 4)
    )
    area_menu = container.frame(AreaId(2)).menu
    assert area_menu is not None

    for _ in range(3):
        strip.layout_menu.fill()
        area_menu.fill()
        QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)

    direct = Qt.FindChildOption.FindDirectChildrenOnly
    layout_submenus = strip.layout_menu.findChildren(QMenu, options=direct)
    area_submenus = area_menu.findChildren(QMenu, options=direct)
    # The Layout menu has one submenu, "This Workspace". The Area menu has
    # three: "Join with", "Swap with" and "Resize".
    assert [submenu.title() for submenu in layout_submenus] == [THIS_WORKSPACE_LABEL]
    assert sorted(submenu.title() for submenu in area_submenus) == sorted(
        (JOIN_WITH_LABEL, SWAP_WITH_LABEL, RESIZE_LABEL)
    )


def test_the_strip_holds_no_layout_button_and_a_right_click_beside_the_tabs_opens_the_menu(
    application: QApplication, shown: list[QWidget]
) -> None:
    """`PL-R5G4`: as in Blender, the Workspace operations open from the strip, not a button.

    A right-click on "+" or on the strip's empty space opens the Layout menu.
    A right-click on a tab opens that tab's own menu instead.
    """

    strip = WorkspaceTabs(shipped_workspaces(), lambda _set: None, lambda: ())
    strip.resize(900, 40)
    strip.show()
    shown.append(strip)
    application.processEvents()

    visible = [button.text() for button in strip.findChildren(QToolButton) if button.isVisible()]
    assert sorted(visible) == sorted([*(tab.text() for tab in strip.tabs), "+"])

    mouse = QContextMenuEvent.Reason.Mouse
    empty = QPoint(strip.width() - 20, strip.height() // 2)
    assert strip.childAt(empty) is None

    for target, at in ((strip, empty), (strip.add_button, QPoint(2, 2))):
        assert not strip.layout_menu.isVisible()
        QApplication.sendEvent(target, QContextMenuEvent(mouse, at, target.mapToGlobal(at)))
        application.processEvents()
        assert strip.layout_menu.isVisible()
        strip.layout_menu.close()
        application.processEvents()

    tab = strip.tabs[0]
    QApplication.sendEvent(
        tab, QContextMenuEvent(mouse, QPoint(2, 2), tab.mapToGlobal(QPoint(2, 2)))
    )
    application.processEvents()
    popup = QApplication.activePopupWidget()
    assert isinstance(popup, QMenu) and popup is not strip.layout_menu
    popup.close()


def test_an_arrow_key_moves_a_focused_border_one_step_and_escape_puts_it_back(
    application: QApplication, shown: list[QWidget]
) -> None:
    """In a row of two at 400 px each, Right makes it 420 and 380, and Left goes back."""

    model = _layout(_row((0.5, 0.5), _area(1), _area(2)), 3)
    container = _container(application, shown, model)
    changed: list[LayoutModel] = []
    container.layout_changed.connect(changed.append)
    border = _handle(container, Handle(0, (), 0))

    container.focus_border(Handle(0, (), 0))
    application.processEvents()
    assert border.hasFocus() and border.lit and not border.warning

    QTest.keyClick(border, Qt.Key.Key_Right)
    QTest.keyClick(border, Qt.Key.Key_Right)
    assert border.owner.sizes() == [400 + 2 * AREA_KEYBOARD_STEP, 400 - 2 * AREA_KEYBOARD_STEP]

    QTest.keyClick(border, Qt.Key.Key_Left)
    assert border.owner.sizes() == [400 + AREA_KEYBOARD_STEP, 400 - AREA_KEYBOARD_STEP]

    # Up and Down move a border between Areas stacked, not this one.
    QTest.keyClick(border, Qt.Key.Key_Down)
    assert border.owner.sizes() == [400 + AREA_KEYBOARD_STEP, 400 - AREA_KEYBOARD_STEP]

    QTest.keyClick(border, Qt.Key.Key_Escape)
    assert container.model == model
    assert border.owner.sizes() == [400, 400]
    assert changed[-1] == model and len(changed) == 4


def test_shift_moves_a_focused_border_alone_and_without_it_its_whole_line_moves(
    application: QApplication, shown: list[QWidget]
) -> None:
    """Two columns side by side, each cut at half its height, have one horizontal line."""

    model = _layout(
        _row(
            (0.5, 0.5),
            _column((0.5, 0.5), _area(1), _area(2)),
            _column((0.5, 0.5), _area(3), _area(4)),
        ),
        5,
    )
    container = _container(application, shown, model)
    left, right = _handle(container, Handle(0, (0,), 0)), _handle(container, Handle(0, (1,), 0))
    container.focus_border(Handle(0, (0,), 0))
    application.processEvents()
    assert left.lit and right.lit

    QTest.keyClick(left, Qt.Key.Key_Down)
    step = [400 + AREA_KEYBOARD_STEP, 400 - AREA_KEYBOARD_STEP]
    assert left.owner.sizes() == step
    assert right.owner.sizes() == step

    QTest.keyClick(left, Qt.Key.Key_Down, Qt.KeyboardModifier.ShiftModifier)
    assert left.owner.sizes() == [400 + 2 * AREA_KEYBOARD_STEP, 400 - 2 * AREA_KEYBOARD_STEP]
    assert right.owner.sizes() == step
    assert left.lit and not right.lit


def test_a_focused_border_stops_where_an_area_reaches_its_least_size_and_turns_warning(
    application: QApplication, shown: list[QWidget]
) -> None:
    """Forty steps to the right would be 800 px, and the right Area keeps at least its header."""

    container = _container(application, shown, _layout(_row((0.5, 0.5), _area(1), _area(2)), 3))
    border = _handle(container, Handle(0, (), 0))
    container.focus_border(Handle(0, (), 0))
    application.processEvents()

    for _ in range(40):
        QTest.keyClick(border, Qt.Key.Key_Right)

    least = container.frame(AreaId(2)).minimumSizeHint().width()
    assert border.warning
    assert border.owner.sizes()[1] >= min(least, 400)
    assert container.model.rectangle(AreaId(2)).left < 1.0

    QTest.keyClick(border, Qt.Key.Key_Left)
    assert not border.warning


def test_a_focused_border_goes_past_its_last_whole_step_to_the_least_size(
    application: QApplication, shown: list[QWidget]
) -> None:
    """The last step stops at the minimum size, as a drag does, not one step short of it.

    The right Area starts 400 px wide, many steps above the minimum width that
    its frame declares. Pressing Right until the border can go no further
    leaves the Area at least as wide as that minimum, and less than one step wider.
    A border that stopped at its last whole step would be up to a whole step
    wider.
    """

    container = _container(application, shown, _layout(_row((0.5, 0.5), _area(1), _area(2)), 3))
    border = _handle(container, Handle(0, (), 0))
    container.focus_border(Handle(0, (), 0))
    application.processEvents()
    least = container.frame(AreaId(2)).minimumWidth()
    steps = (400 - least) // AREA_KEYBOARD_STEP
    assert steps >= 3

    for _ in range(steps + 2):
        QTest.keyClick(border, Qt.Key.Key_Right)

    assert border.warning
    assert least <= border.owner.sizes()[1] < least + AREA_KEYBOARD_STEP


def test_the_controls_area_has_its_least_width_from_the_first_frame(
    application: QApplication, shown: list[QWidget]
) -> None:
    """`PL-4L8B`: the first frame settles the Areas, so a border's first keyboard step is one step.

    The setting controls build their per-run copies on their first frame,
    which raises the minimum width of the Area that holds them. Before the fix,
    the root splitter kept the widths it had before that frame until the next
    pass of the event loop. At this size those widths were 1010 and 336 px, and
    that pass gave the controls their 590 px. A border moved between the frame
    and that pass moved by about 250 px. The test reads the width that the Area
    needs from Qt's own size hint for the Area's frame, not from the sizes that
    the adapter worked out.
    """

    view = _dashboard(application, shown)
    areas = view.layout_container
    controls = next(area.id for area in areas.model.areas() if area.view == PARAMETER_CONTROLS)
    frame = areas.frame(controls)
    border = _handle(areas, Handle(0, (), 0))
    root = border.owner
    first_frame = root.sizes()
    controls_px = frame.width()

    assert controls_px >= frame.minimumSizeHint().width() > 336
    application.processEvents()
    assert root.sizes() == first_frame

    areas.focus_border(Handle(0, (), 0))
    application.processEvents()
    QTest.keyClick(border, Qt.Key.Key_Left)

    assert frame.width() == controls_px + AREA_KEYBOARD_STEP
    assert root.sizes() == [
        first_frame[0] - AREA_KEYBOARD_STEP,
        first_frame[1] + AREA_KEYBOARD_STEP,
    ]


def test_a_focused_border_keeps_its_starting_layout_while_another_window_is_active(
    application: QApplication, shown: list[QWidget]
) -> None:
    """The window losing and regaining the focus does not move where Escape returns to."""

    model = _layout(_row((0.5, 0.5), _area(1), _area(2)), 3)
    container = _container(application, shown, model)
    border = _handle(container, Handle(0, (), 0))
    container.focus_border(Handle(0, (), 0))
    application.processEvents()
    QTest.keyClick(border, Qt.Key.Key_Right)
    assert border.owner.sizes() == [400 + AREA_KEYBOARD_STEP, 400 - AREA_KEYBOARD_STEP]

    other = QWidget()
    shown.append(other)
    other.show()
    _activate(application, other)
    _activate(application, container)
    assert border.hasFocus()

    QTest.keyClick(border, Qt.Key.Key_Escape)
    assert container.model == model
    assert border.owner.sizes() == [400, 400]


def test_a_border_is_in_the_tab_order_and_loses_its_line_with_the_focus(
    application: QApplication, shown: list[QWidget]
) -> None:
    container = _container(application, shown, _layout(_row((0.5, 0.5), _area(1), _area(2)), 3))
    border = _handle(container, Handle(0, (), 0))

    assert border.focusPolicy() == Qt.FocusPolicy.StrongFocus
    assert border.accessibleName()

    container.focus_border(Handle(0, (), 0))
    application.processEvents()
    assert border.lit

    container.frame(AreaId(1)).chooser.setFocus(Qt.FocusReason.TabFocusReason)
    application.processEvents()
    assert not border.lit


def test_the_resize_submenu_names_each_border_and_its_entry_gives_that_border_the_focus(
    application: QApplication, shown: list[QWidget]
) -> None:
    """In row[1, column[2, 3]], Area 2 has a left and a bottom border, and Area 1 a right one."""

    model = _layout(_row((0.5, 0.5), _area(1), _column((0.5, 0.5), _area(2), _area(3))), 4)
    container = _container(application, shown, model)

    assert [(border.label, border.handle) for border in container.borders(AreaId(1))] == [
        ("Right border", Handle(0, (), 0))
    ]
    assert [(border.label, border.handle) for border in container.borders(AreaId(2))] == [
        ("Left border", Handle(0, (), 0)),
        ("Bottom border", Handle(0, (1,), 0)),
    ]

    menu = container.frame(AreaId(2)).menu
    assert menu is not None
    menu.fill()
    top = {action.text(): action for action in menu.actions()}
    assert list(top)[-2:] == [RESIZE_LABEL, CLOSE_AREA_LABEL]
    resize = top[RESIZE_LABEL].menu()
    assert isinstance(resize, QMenu)
    entries = {action.text(): action for action in resize.actions()}
    assert list(entries) == ["Left border", "Bottom border"]

    entries["Bottom border"].trigger()
    application.processEvents()
    assert _handle(container, Handle(0, (1,), 0)).hasFocus()


def test_an_area_bordered_on_four_sides_lists_four_resize_entries_each_moving_its_own_side(
    application: QApplication, shown: list[QWidget]
) -> None:
    """In row[1, column[2, 3, 4], 5], Area 3 has a border on each side, named for that side."""

    model = _layout(
        _row(
            (0.25, 0.5, 0.25),
            _area(1),
            _column((1 / 3, 1 / 3, 1 / 3), _area(2), _area(3), _area(4)),
            _area(5),
        ),
        6,
    )
    container = _container(application, shown, model)
    entries = container.borders(AreaId(3))

    assert [entry.label for entry in entries] == [
        "Left border",
        "Top border",
        "Right border",
        "Bottom border",
    ]
    # The column's two borders are its own handles 0 and 1, and the row's
    # are the root's handles 0 and 1.
    assert [entry.handle for entry in entries] == [
        Handle(0, (), 0),
        Handle(0, (1,), 0),
        Handle(0, (), 1),
        Handle(0, (1,), 1),
    ]

    # Each entry's border, moved one step down or right, moves that side of
    # Area 3 and leaves the opposite side where it was.
    before = model.rectangle(AreaId(3))

    for entry, side in zip(entries, ("left", "top", "right", "bottom"), strict=True):
        container.focus_border(entry.handle)
        application.processEvents()
        border = QApplication.focusWidget()
        assert isinstance(border, _AreaHandle)
        assert border.lit and border.accessibleDescription()
        key = Qt.Key.Key_Right if side in ("left", "right") else Qt.Key.Key_Down
        QTest.keyClick(border, key)
        after = container.model.rectangle(AreaId(3))
        opposite = {"left": "right", "right": "left", "top": "bottom", "bottom": "top"}[side]
        assert getattr(after, side) > getattr(before, side)
        assert getattr(after, opposite) == getattr(before, opposite)

        # Escape puts the layout back and keeps the border's focus and its
        # line, so a second step and a second Escape behave the same way.
        QTest.keyClick(border, Qt.Key.Key_Escape)
        assert container.model == model and border.hasFocus() and border.lit
        QTest.keyClick(border, key)
        QTest.keyClick(border, Qt.Key.Key_Escape)
        assert container.model == model


def test_the_this_workspace_submenu_acts_on_the_current_workspace(
    application: QApplication,
) -> None:
    """With the third tab current, the submenu's Duplicate copies that Workspace."""

    workspaces = shipped_workspaces().activate(2)
    made: list[WorkspaceSet] = []
    strip = WorkspaceTabs(workspaces, made.append, lambda: ())
    strip.layout_menu.fill()
    entry = next(
        action for action in strip.layout_menu.actions() if action.text() == THIS_WORKSPACE_LABEL
    )
    submenu = entry.menu()
    assert isinstance(submenu, QMenu)
    duplicate = next(action for action in submenu.actions() if action.text() == DUPLICATE_LABEL)

    duplicate.trigger()

    assert made == [workspaces.duplicate(2)]


def test_the_only_areas_resize_submenu_is_shown_unavailable_with_its_reason(
    application: QApplication, shown: list[QWidget]
) -> None:
    container = _container(application, shown, LayoutModel.single_area(_VIEW))
    menu = container.frame(AreaId(1)).menu
    assert menu is not None
    menu.fill()
    resize = next(action for action in menu.actions() if action.text() == RESIZE_LABEL)

    assert not resize.isEnabled()
    assert "only Area" in resize.toolTip()


def test_save_restore_and_reset_all_are_reachable_from_the_keyboard(
    application: QApplication, shown: list[QWidget], tmp_path: Path
) -> None:
    """Restore shipped Workspaces, Save as default and Reset all layouts, by key alone.

    The store's directory is `tmp_path`, so the save writes there and nowhere
    else (`PL-DWHG`).
    """

    view = _dashboard(application, shown, WorkspaceStore(tmp_path))
    strip = view.tab_strip

    def names() -> list[str]:
        return [workspace.name for workspace in view.workspaces.workspaces]

    # Delete the shipped Induction Workspace, which asks first.
    strip.activate(view.workspaces.position_of(WorkspaceName("Induction")))
    _choose_in_tab_menu(application, view, (DELETE_LABEL,))
    dialog = strip.question
    assert dialog is not None
    _proceed_by_keys(application, dialog)
    assert names() == ["Default", "Maintenance"]
    assert view.workspaces.current.name == "Maintenance"

    # Restore puts it back where it was shipped, and keeps the current tab.
    _choose_in_tab_menu(application, view, (RESTORE_SHIPPED_LABEL,))
    assert names() == ["Default", "Induction", "Maintenance"]
    assert view.workspaces.current.name == "Maintenance"
    assert view.workspaces.workspaces[1] == shipped_workspace(ShippedWorkspaceId("induction"))

    # Duplicate the current Workspace, then save the four as the default.
    _choose_in_tab_menu(application, view, (DUPLICATE_LABEL,))
    if strip.editor is not None:
        QTest.keyClick(strip.editor, Qt.Key.Key_Escape)
    assert names() == ["Default", "Induction", "Maintenance", "Maintenance (copy)"]
    saved = view.workspaces
    _choose_in_tab_menu(application, view, (SAVE_AS_DEFAULT_LABEL,))
    dialog = strip.question
    assert dialog is not None
    _proceed_by_keys(application, dialog)
    reloaded = WorkspaceStore(tmp_path).load(shipped_workspaces())
    assert reloaded.source is Source.FILE
    assert reloaded.workspaces == saved
    written = (tmp_path / WORKSPACES_FILE_NAME).read_bytes()

    # Reset all layouts asks first. Escape keeps the set, and the button resets it.
    _choose_in_tab_menu(application, view, (RESET_ALL_LABEL,))
    dialog = strip.question
    assert dialog is not None
    _activate(application, dialog)
    QTest.keyClick(dialog, Qt.Key.Key_Escape)
    application.processEvents()
    assert names() == ["Default", "Induction", "Maintenance", "Maintenance (copy)"]
    _choose_in_tab_menu(application, view, (RESET_ALL_LABEL,))
    dialog = strip.question
    assert dialog is not None
    _proceed_by_keys(application, dialog)
    assert strip.workspaces == shipped_workspaces()
    assert (tmp_path / WORKSPACES_FILE_NAME).read_bytes() == written
