"""This module draws the Workspace tab strip in PySide6, with one tab for each Workspace.

`PL-QW1Z` decided its place and its look, and `PL-2KXB` builds it. The strip
sits directly above the Areas, under the unconditional region, and spans the
layout container's width. It sits there because a tab switches the Areas and
nothing above them (Q1). It holds the tabs and a "+" at its end, and nothing
else (Q2). The shipped Workspaces' tabs come first, then a separator line,
then the reader's own (Q4).

**The strip owns no Workspace.** It is drawn from the `WorkspaceSet` that the
dashboard holds. Every change a reader makes produces a new set, which the
strip hands to the `change` callback. The dashboard applies the new set and
draws the strip again with `show_set`. So the set has one owner, as
`.claude/rules/ui-areas.md` asks of any state that the rest of the dashboard
draws from.

**Each menu entry is worked out before it is shown.** `tab_operations` asks
the set what new set each entry would make, in the same way that
`AreaLayout.operations` asks the layout model. An entry that the set refuses
is shown disabled, with the reason as its tooltip. So when only one Workspace
is left, its Delete entry is shown as unavailable, rather than refused after
a click (`PL-WV9K` Q2).

Each tab's context menu holds these entries, in the order that `PL-QW1Z` Q3
set: Rename, Duplicate, Move left, Move right, one entry to pin or unpin each
open run, Reset this Workspace (only on a shipped tab), and Delete. The menu
opens on a right-click, the Menu key or Shift+F10. A double-click or F2
renames a tab in place. Delete and Reset ask for confirmation first, because
a session's Workspaces have no undo.

**The Layout menu, at the strip's right end, makes every Workspace operation
available without a pointer** (`PL-M352`). It is the "layout drop-down menu"
that `PL-WV9K` § "Answers 2026-09-27" names. It lists every Workspace, with
the current one checked, and choosing one switches to it. Next come Previous
Workspace and Next Workspace. Their shortcuts are Ctrl+PageUp and
Ctrl+PageDown, which Blender uses for the same thing (Blender Manual,
"Workspaces", "Controls", read 2026-10-19). As in Blender's
`SCREEN_OT_workspace_cycle`, they wrap around at either end. Last comes a
"This Workspace" submenu, which holds the current tab's own menu. The menu's
button is in the tab order after "+". Its place and its wording are
placeholders, chosen under the project owner's rule of 2026-10-18.

**The Layout menu ends with the three entries that keep or undo a session's
changes** (`PL-DWHG`). A separator sets them apart. `PL-WV9K` § "Answers
2026-09-27" decided them, modelled on Blender's Save Startup File and Load
Factory Settings. The three entries are these.

- "Save as default" writes every Workspace, their order and the current one
  to `workspaces.json` through `layout/store.py`. It first asks a question
  that names the file it will write. The next launch opens on what it saved.
  Nothing else writes the file, so a change that is not saved is lost at
  quit. The entry is shown as unavailable, with the reason as its tooltip,
  when there is no store or the store refuses to save in this session.
- "Restore shipped Workspaces" puts back each shipped Workspace that the
  reader deleted, as its shipped file holds it, and changes nothing else.
- "Reset all layouts" replaces every Workspace with the shipped set. It asks
  a question first, because a session's Workspaces have no undo. It writes
  no file, so the saved default stays until the reader saves again.

**What the store reports is shown, never kept quiet** (`PL-WV9K` Q5). Three
kinds of message are shown on a line under the tabs: a notice from the load,
a save that the operating system refused, and a save that worked. Each one
stays until the reader dismisses it or the next one replaces it. A notice is
conditional text, so the line is not shown when there is no notice.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import Final

from PySide6.QtCore import QEvent, QObject, QPoint, Qt
from PySide6.QtGui import QAction, QContextMenuEvent, QFont, QKeyEvent, QKeySequence, QMouseEvent
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QMenu,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from anesthesia_sim.app.dashboard_frame import run_label
from anesthesia_sim.app.qt_widgets import declare_interface_colours, style_label, styled_label
from anesthesia_sim.app.stylesheets import (
    filled_button_stylesheet,
    menu_stylesheet,
    outlined_button_stylesheet,
    view_chooser_stylesheet,
    workspace_separator_stylesheet,
    workspace_tab_stylesheet,
)
from anesthesia_sim.app.theme import (
    INK,
    METRIC_NAME_SIZE,
    METRIC_QUALIFIER_SIZE,
    NEW_CASE_DIALOG_SPACING,
    NEW_CASE_DIALOG_WIDTH,
    WARNING,
)
from anesthesia_sim.layout.exceptions import (
    InvalidLayout,
    LastWorkspace,
    LayoutRefused,
    ShippedWorkspaceError,
    WorkspaceFileError,
)
from anesthesia_sim.layout.run_identity import RunId
from anesthesia_sim.layout.shipped import shipped_workspace, shipped_workspaces
from anesthesia_sim.layout.store import WorkspaceStore
from anesthesia_sim.layout.workspace import (
    ShippedWorkspaceId,
    Workspace,
    WorkspaceName,
    WorkspaceSet,
)

__all__ = [
    "ADD_WORKSPACE_LABEL",
    "DELETE_LABEL",
    "DISMISS_LABEL",
    "DUPLICATE_LABEL",
    "LAYOUT_MENU_LABEL",
    "MOVE_LEFT_LABEL",
    "MOVE_RIGHT_LABEL",
    "NEXT_WORKSPACE_KEYS",
    "NEXT_WORKSPACE_LABEL",
    "PREVIOUS_WORKSPACE_KEYS",
    "PREVIOUS_WORKSPACE_LABEL",
    "RENAME_LABEL",
    "RESET_ALL_LABEL",
    "RESET_LABEL",
    "RESTORE_SHIPPED_LABEL",
    "SAVE_AS_DEFAULT_LABEL",
    "THIS_WORKSPACE_LABEL",
    "LayoutMenu",
    "SaveEntry",
    "TabOperation",
    "WorkspaceQuestion",
    "WorkspaceQuestionDialog",
    "WorkspaceTab",
    "WorkspaceTabs",
    "default_operations",
    "display_order",
    "restore_shipped",
    "save_entry",
    "tab_operations",
]

# The strip's words. Each is a placeholder, decided by `PL-2KXB` under the
# project owner's rule of 2026-10-18 that look, wording and placement are
# placeholders while the structure is built.
ADD_WORKSPACE_LABEL: Final = "+"
RENAME_LABEL: Final = "Rename"
DUPLICATE_LABEL: Final = "Duplicate"
MOVE_LEFT_LABEL: Final = "Move left"
MOVE_RIGHT_LABEL: Final = "Move right"
RESET_LABEL: Final = "Reset this Workspace"
DELETE_LABEL: Final = "Delete"
LAYOUT_MENU_LABEL: Final = "Layout"
PREVIOUS_WORKSPACE_LABEL: Final = "Previous Workspace"
NEXT_WORKSPACE_LABEL: Final = "Next Workspace"
THIS_WORKSPACE_LABEL: Final = "This Workspace"
SAVE_AS_DEFAULT_LABEL: Final = "Save as default"
RESTORE_SHIPPED_LABEL: Final = "Restore shipped Workspaces"
RESET_ALL_LABEL: Final = "Reset all layouts"
DISMISS_LABEL: Final = "Dismiss"
PREVIOUS_WORKSPACE_KEYS: Final = "Ctrl+PgUp"
NEXT_WORKSPACE_KEYS: Final = "Ctrl+PgDown"
_LAYOUT_DESCRIPTION: Final = "Switch, rename, duplicate or delete Workspaces"
_PIN_TEMPLATE: Final = "Pin {run}"
_UNPIN_TEMPLATE: Final = "Unpin {run}"
_ADD_DESCRIPTION: Final = "Duplicate the current Workspace"
_LAST_WORKSPACE_TEXT: Final = "Not available: there is always at least one Workspace."
_FIRST_TEXT: Final = "Not available: this tab is already first in its group."
_LAST_TEXT: Final = "Not available: this tab is already last in its group."
_NO_RUN_TEXT: Final = "Not available: no run is open."
_KEEP_LABEL: Final = "Keep"
_DELETE_TITLE: Final = "Delete this Workspace?"
_DELETE_SHIPPED_TEXT: Final = (
    'Delete the shipped Workspace "{name}"? "Restore shipped Workspaces" in the Layout menu '
    "brings back the shipped version."
)
_DELETE_MINE_TEXT: Final = 'Delete your Workspace "{name}"? This cannot be undone.'
_RESET_TITLE: Final = "Reset this Workspace?"
_RESET_TEXT: Final = (
    'Reset "{name}" to the Workspace shipped as "{shipped}"? Its layout and every '
    "View's settings return to the shipped ones. This cannot be undone."
)
_REFUSED_TEXT: Final = "Not available: {reason}"
_ALL_RESTORED_TEXT: Final = "Not available: every shipped Workspace is already here."
_RESET_ALL_TITLE: Final = "Reset all layouts?"
_RESET_ALL_TEXT: Final = (
    "Replace every Workspace with the shipped ones? Your own Workspaces and your changes to "
    "the shipped ones are removed. The saved default is not changed until you save again."
)
_RESET_ALL_PROCEED_LABEL: Final = "Reset all"
_SAVE_TITLE: Final = "Save as default?"
_SAVE_REPLACING_TEXT: Final = (
    "Save these {count} Workspaces as the default that opens at each launch? They replace the "
    "default saved in {path}."
)
_SAVE_FIRST_TEXT: Final = (
    "Save these {count} Workspaces as the default that opens at each launch? They are saved "
    "in {path}."
)
_SAVE_PROCEED_LABEL: Final = "Save"
_CANCEL_LABEL: Final = "Cancel"
_NO_STORE_TEXT: Final = "Not available: this session has no folder to save Workspaces in."
_SAVED_TEXT: Final = "Saved {count} Workspaces as the default, in {path}."
_SAVE_FAILED_TEXT: Final = "The Workspaces were not saved: {reason}"

#: The width of the rule between the shipped tabs and the reader's own.
_SEPARATOR_WIDTH: Final = 1


@dataclass(frozen=True, slots=True)
class WorkspaceQuestion:
    """What a reader is asked before an entry is applied: a title, one statement, two buttons."""

    title: str
    text: str
    proceed_label: str
    keep_label: str = _KEEP_LABEL


@dataclass(frozen=True, slots=True)
class TabOperation:
    """One entry in a tab's menu, with its label and the set it makes or why it cannot.

    Attributes:
        label: The entry's text.
        result: The set the entry makes, or `None` where it is unavailable.
        refusal: Why it is unavailable, shown as its tooltip, or `None`.
        question: What the reader is asked before `result` is applied, or
            `None` where the entry applies at once.
    """

    label: str
    result: WorkspaceSet | None
    refusal: str | None = None
    question: WorkspaceQuestion | None = None

    @property
    def available(self) -> bool:
        """Whether the entry can be chosen."""

        return self.result is not None


def display_order(workspaces: WorkspaceSet) -> tuple[int, ...]:
    """The set's positions in the order their tabs stand: shipped first, then the reader's own.

    Within each group the set's own order holds (`PL-QW1Z` Q4).
    """

    shipped = [i for i, ws in enumerate(workspaces.workspaces) if ws.origin.is_shipped]
    mine = [i for i, ws in enumerate(workspaces.workspaces) if not ws.origin.is_shipped]

    return (*shipped, *mine)


def tab_operations(
    workspaces: WorkspaceSet,
    index: int,
    open_runs: tuple[RunId, ...],
    shipped: Callable[[ShippedWorkspaceId], Workspace] = shipped_workspace,
) -> tuple[TabOperation, ...]:
    """Return the menu entries after Rename for the tab at `index`, in `PL-QW1Z` Q3's order.

    Args:
        workspaces: The set the strip is drawn from.
        index: The tab's position in the set.
        open_runs: The runs the session has open, in drawing order. A
            pinned run that is no longer open can still be unpinned.
        shipped: Returns the shipped Workspace with a given id. A shipped
            tab resets to that Workspace. A test passes its own.

    Raises:
        TypeError: `index` is not an `int`.
        NotInWorkspaceSet: `index` is not a position in the set.
    """

    workspace = workspaces.activate(index).current
    operations = [TabOperation(DUPLICATE_LABEL, workspaces.duplicate(index))]
    operations.extend(_moves(workspaces, index))
    operations.extend(_pins(workspaces, index, workspace, open_runs))

    if workspace.origin.shipped_id is not None:
        operations.append(
            _reset(workspaces, index, workspace, partial(shipped, workspace.origin.shipped_id))
        )

    operations.append(_delete(workspaces, index, workspace))

    return tuple(operations)


def _moves(workspaces: WorkspaceSet, index: int) -> tuple[TabOperation, TabOperation]:
    """Move left and Move right, each within the tab's own group."""

    shipped = workspaces.workspaces[index].origin.is_shipped
    group = [
        i
        for i in display_order(workspaces)
        if workspaces.workspaces[i].origin.is_shipped == shipped
    ]
    place = group.index(index)
    left = group[place - 1] if place > 0 else None
    right = group[place + 1] if place < len(group) - 1 else None

    return (
        TabOperation(MOVE_LEFT_LABEL, None, _FIRST_TEXT)
        if left is None
        else TabOperation(MOVE_LEFT_LABEL, workspaces.move(index, left)),
        TabOperation(MOVE_RIGHT_LABEL, None, _LAST_TEXT)
        if right is None
        else TabOperation(MOVE_RIGHT_LABEL, workspaces.move(index, right)),
    )


def _pins(
    workspaces: WorkspaceSet, index: int, workspace: Workspace, open_runs: tuple[RunId, ...]
) -> tuple[TabOperation, ...]:
    """Unpin the pinned run, or one entry to pin each open run."""

    if workspace.pinned_run is not None:
        label = _UNPIN_TEMPLATE.format(run=run_label(workspace.pinned_run))

        return (TabOperation(label, workspaces.replace(index, workspace.pinned_to(None))),)

    if not open_runs:
        return (TabOperation(_PIN_TEMPLATE.format(run="run"), None, _NO_RUN_TEXT),)

    return tuple(
        TabOperation(
            _PIN_TEMPLATE.format(run=run_label(run)),
            workspaces.replace(index, workspace.pinned_to(run)),
        )
        for run in open_runs
    )


def _reset(
    workspaces: WorkspaceSet, index: int, workspace: Workspace, read: Callable[[], Workspace]
) -> TabOperation:
    """Reset this Workspace from its shipped file, or why it cannot be."""

    try:
        restored = read()
        result = workspaces.replace(index, restored)
    except (ShippedWorkspaceError, LayoutRefused) as refusal:
        return TabOperation(RESET_LABEL, None, _REFUSED_TEXT.format(reason=refusal))

    question = WorkspaceQuestion(
        _RESET_TITLE, _RESET_TEXT.format(name=workspace.name, shipped=restored.name), RESET_LABEL
    )

    return TabOperation(RESET_LABEL, result, question=question)


def _delete(workspaces: WorkspaceSet, index: int, workspace: Workspace) -> TabOperation:
    """Delete, which asks first, or why the last Workspace cannot be deleted."""

    try:
        result = workspaces.remove(index)
    except LastWorkspace:
        return TabOperation(DELETE_LABEL, None, _LAST_WORKSPACE_TEXT)

    template = _DELETE_SHIPPED_TEXT if workspace.origin.is_shipped else _DELETE_MINE_TEXT
    question = WorkspaceQuestion(_DELETE_TITLE, template.format(name=workspace.name), DELETE_LABEL)

    return TabOperation(DELETE_LABEL, result, question=question)


@dataclass(frozen=True, slots=True)
class SaveEntry:
    """The "Save as default" entry: the question asked before saving, or why it is unavailable.

    Exactly one of the two is set.
    """

    question: WorkspaceQuestion | None
    refusal: str | None

    @property
    def available(self) -> bool:
        """Whether the entry can be chosen."""

        return self.question is not None


def save_entry(
    store: WorkspaceStore | None, workspaces: WorkspaceSet, missing_store: str | None = None
) -> SaveEntry:
    """Return the "Save as default" entry for saving `workspaces` to `store`.

    The entry is unavailable where there is no store, where the store has
    loaded nothing yet, and where its load turned saving off for the session.
    In the last case the reason is the store's own notice, which names the
    file.

    Args:
        store: The store the session loaded from, or `None` where there is
            none.
        workspaces: The set the entry would save.
        missing_store: Why there is no store, shown as the reason where
            `store` is `None`. Where both are `None`, a generic reason is
            shown instead.
    """

    if store is None:
        reason = (
            _NO_STORE_TEXT if missing_store is None else _REFUSED_TEXT.format(reason=missing_store)
        )

        return SaveEntry(None, reason)

    loaded = store.loaded

    if loaded is None:
        return SaveEntry(
            None, _REFUSED_TEXT.format(reason=f"nothing has been loaded from {store.directory} yet")
        )

    if not loaded.writable:
        reason = loaded.notice or "saving is off for this session"

        return SaveEntry(None, _REFUSED_TEXT.format(reason=reason))

    template = _SAVE_REPLACING_TEXT if store.path.exists() else _SAVE_FIRST_TEXT
    text = template.format(count=len(workspaces.workspaces), path=store.path)

    return SaveEntry(WorkspaceQuestion(_SAVE_TITLE, text, _SAVE_PROCEED_LABEL, _CANCEL_LABEL), None)


def restore_shipped(workspaces: WorkspaceSet, shipped: WorkspaceSet) -> WorkspaceSet:
    """Return `workspaces` with each shipped Workspace it no longer holds put back.

    A shipped Workspace counts as still in the set while some Workspace in
    the set has it as its origin, whatever that Workspace has been renamed to
    or changed into. So only a deleted one comes back, and it comes back as
    its shipped file holds it. Each one goes back after the nearest Workspace
    that comes before it in the shipped order and is still in the set. Where
    no such Workspace exists, it goes back before the first shipped Workspace
    in the set. The current Workspace stays current, so the Areas do not
    change.

    Args:
        workspaces: The reader's set.
        shipped: The shipped set, in its shipped order.

    Raises:
        LayoutRefused: A Workspace in `workspaces` already has the name of
            a shipped Workspace that would be put back. The message names
            that Workspace.
    """

    order = [workspace.origin.shipped_id for workspace in shipped.workspaces]
    current = workspaces.current.name
    result = workspaces

    for place, workspace in enumerate(shipped.workspaces):
        held = [ws.origin.shipped_id for ws in result.workspaces]

        if order[place] in held:
            continue

        before = set(order[:place])
        earlier = [i for i, shipped_id in enumerate(held) if shipped_id in before]
        shipped_places = [i for i, shipped_id in enumerate(held) if shipped_id is not None]

        if earlier:
            at = max(earlier) + 1
        elif shipped_places:
            at = min(shipped_places)
        else:
            at = 0

        result = result.add(workspace, at=at)

    return result.activate(result.position_of(current))


def default_operations(
    workspaces: WorkspaceSet, shipped: Callable[[], WorkspaceSet] = shipped_workspaces
) -> tuple[TabOperation, TabOperation]:
    """Return the Restore shipped Workspaces and Reset all layouts entries for `workspaces`.

    Where the shipped set cannot be read, both entries are unavailable, and
    the reason names the file.

    Args:
        workspaces: The set the strip is drawn from.
        shipped: Returns the shipped set. A test passes its own.
    """

    try:
        factory = shipped()
    except ShippedWorkspaceError as refusal:
        reason = _REFUSED_TEXT.format(reason=refusal)

        return (
            TabOperation(RESTORE_SHIPPED_LABEL, None, reason),
            TabOperation(RESET_ALL_LABEL, None, reason),
        )

    try:
        restored = restore_shipped(workspaces, factory)
    except LayoutRefused as refusal:
        restore = TabOperation(RESTORE_SHIPPED_LABEL, None, _REFUSED_TEXT.format(reason=refusal))
    else:
        restore = (
            TabOperation(RESTORE_SHIPPED_LABEL, None, _ALL_RESTORED_TEXT)
            if len(restored.workspaces) == len(workspaces.workspaces)
            else TabOperation(RESTORE_SHIPPED_LABEL, restored)
        )

    question = WorkspaceQuestion(_RESET_ALL_TITLE, _RESET_ALL_TEXT, _RESET_ALL_PROCEED_LABEL)

    return restore, TabOperation(RESET_ALL_LABEL, factory, question=question)


class WorkspaceQuestionDialog(QDialog):
    """The question asked before a Workspace is deleted or reset, or the set saved or reset.

    The dialog is laid out like `NewCaseDialog`, with the destructive button
    first and the safe one last. The entry's own button is outlined. The keep
    button is filled and is the default, so Return and Escape both leave
    everything as it was. `accept()` means "go ahead". The dialog is shown
    with `open()`, so a test can call `accept()` itself.

    Attributes:
        proceed_button: Applies the entry. Its `clicked` signal runs
            `accept()`.
        keep_button: Leaves everything as it was, and is the default. It is
            labelled with the question's `keep_label`.
    """

    def __init__(self, question: WorkspaceQuestion, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle(question.title)
        declare_interface_colours(self)
        title = styled_label(question.title, color=INK, bold=True, wrap=True)
        text = styled_label(question.text, color=INK, wrap=True)
        text.setFixedWidth(NEW_CASE_DIALOG_WIDTH)
        self.proceed_button = QPushButton(question.proceed_label)
        self.proceed_button.setAutoDefault(False)
        self.proceed_button.setStyleSheet(outlined_button_stylesheet())
        self.keep_button = QPushButton(question.keep_label)
        self.keep_button.setDefault(True)
        self.keep_button.setStyleSheet(filled_button_stylesheet())

        column = QVBoxLayout(self)
        column.setSpacing(NEW_CASE_DIALOG_SPACING)
        column.addWidget(title)
        column.addWidget(text)
        actions = QHBoxLayout()
        actions.addStretch(1)
        actions.addWidget(self.proceed_button)
        actions.addWidget(self.keep_button)
        column.addLayout(actions)

        self.proceed_button.clicked.connect(self.accept)
        self.keep_button.clicked.connect(self.reject)


class LayoutMenu(QToolButton):
    """The Layout menu at the strip's right end, which lists the Workspaces and their operations.

    The menu writes its entries each time it opens. It works them out from the
    same set that the strip uses for its own entries. The module docstring
    lists the menu's entries. The button looks like the Area menu and is
    reached from the keyboard in the same way. It is in the tab order, and
    Space or Enter opens it.

    Args:
        strip: The strip that carries out each entry.
    """

    def __init__(self, strip: WorkspaceTabs) -> None:
        super().__init__(strip)
        self.setObjectName("layoutMenu")
        self._strip = strip
        self.setText(LAYOUT_MENU_LABEL)
        self.setAccessibleDescription(_LAYOUT_DESCRIPTION)
        self.setStyleSheet(view_chooser_stylesheet())
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        font = QFont(self.font())
        font.setPixelSize(METRIC_NAME_SIZE)
        self.setFont(font)
        menu = QMenu(self)
        menu.setStyleSheet(menu_stylesheet())
        menu.setToolTipsVisible(True)
        menu.aboutToShow.connect(self.fill)
        self.setMenu(menu)

    def fill(self) -> None:
        """Write the menu's entries from the set the strip works its entries out from."""

        strip = self._strip
        now = strip.current_set()
        menu = self.menu()
        _clear(menu)

        for index in display_order(now):
            action = menu.addAction(now.workspaces[index].name)
            action.setCheckable(True)
            action.setChecked(index == now.active)
            action.triggered.connect(partial(strip.activate, index))

        menu.addSeparator()
        menu.addAction(strip.previous_action)
        menu.addAction(strip.next_action)
        menu.addSeparator()
        current = menu.addMenu(THIS_WORKSPACE_LABEL)
        current.setStyleSheet(menu_stylesheet())
        current.setToolTipsVisible(True)
        strip.fill_tab_menu(current, now.active)
        menu.addSeparator()
        save = strip.save_entry()
        action = menu.addAction(SAVE_AS_DEFAULT_LABEL)
        action.setEnabled(save.available)
        action.setToolTip(save.refusal or "")
        action.triggered.connect(partial(strip.save_as_default, save))

        for operation in strip.default_operations():
            action = menu.addAction(operation.label)
            action.setEnabled(operation.available)
            action.setToolTip(operation.refusal or "")
            action.triggered.connect(partial(strip.choose, operation))


def _clear(menu: QMenu) -> None:
    """Remove every entry from `menu`, and delete the submenus created for those entries.

    `QMenu.clear` removes the entries but keeps each submenu as a child of `menu`. So a
    menu that is rebuilt each time it opens would gain one submenu per opening.
    """

    for submenu in menu.findChildren(QMenu, options=Qt.FindChildOption.FindDirectChildrenOnly):
        submenu.deleteLater()

    menu.clear()


class WorkspaceTab(QToolButton):
    """One Workspace's tab, showing its name and checked while it is the current Workspace.

    A click makes it current. A double-click or F2 renames it. The Menu key,
    Shift+F10 or a right-click opens its menu. Left and Right move the keyboard
    focus to the neighbouring tab. The strip carries out each of these actions.

    Attributes:
        index: The Workspace's position in the set the strip was drawn from.
    """

    def __init__(self, strip: WorkspaceTabs, index: int, workspace: Workspace, active: bool):
        super().__init__(strip)
        self.setObjectName("workspaceTab")
        self.index = index
        self._strip = strip
        self.setText(workspace.name)
        self.setCheckable(True)
        self.setChecked(active)
        self.setAutoRaise(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet(workspace_tab_stylesheet())
        font = QFont(self.font())
        font.setPixelSize(METRIC_NAME_SIZE)
        self.setFont(font)
        # A click on the current tab must leave it checked, so the strip
        # rather than the button decides the checked state.
        self.clicked.connect(partial(strip.activate, index))

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        self._strip.rename(self.index)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        self._strip.open_menu(self.index, event.globalPos())

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        shift = event.modifiers() & Qt.KeyboardModifier.ShiftModifier

        if key == Qt.Key.Key_F2:
            self._strip.rename(self.index)
        elif key == Qt.Key.Key_F10 and shift:
            self._strip.open_menu(self.index, self.mapToGlobal(self.rect().bottomLeft()))
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_Right):
            self._strip.focus_beside(self.index, -1 if key == Qt.Key.Key_Left else 1)
        else:
            super().keyPressEvent(event)


class _NameEditor(QLineEdit):
    """The in-place editor a tab is replaced by while it is renamed. Escape cancels."""

    def __init__(self, strip: WorkspaceTabs, index: int, name: str) -> None:
        super().__init__(name, strip)
        self.setObjectName("workspaceNameEditor")
        self.index = index
        self._strip = strip
        declare_interface_colours(self)
        font = QFont(self.font())
        font.setPixelSize(METRIC_NAME_SIZE)
        self.setFont(font)
        self.selectAll()
        self.returnPressed.connect(partial(strip.finish_rename, keep_open=True))
        self.installEventFilter(self)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self._strip.cancel_rename()
        else:
            super().keyPressEvent(event)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self and event.type() == QEvent.Type.FocusOut:
            self._strip.finish_rename(keep_open=False)

        return False


class WorkspaceTabs(QWidget):
    """The strip of Workspace tabs, drawn from a `WorkspaceSet` it does not own.

    Args:
        workspaces: The set to draw first.
        change: Called with each set a reader's action makes. The owner
            applies it and calls `show_set` with it.
        open_runs: Returns the runs open now, for the pin entries.
        live: Returns the set as it stands now. The owner's current Workspace
            can change after the strip draws it, through a dragged border or
            a View's own settings. Every entry is worked out from this set, so
            a duplicate copies what the reader sees, and "Save as default"
            saves it. By default, the set that was drawn.
        store: The store that "Save as default" writes to, or `None`. With
            `None`, that entry is shown as unavailable.
        notice: What the reader is told about the load, shown under the tabs
            from the start, or `None`. Where `store` is `None` it is also the
            reason "Save as default" is unavailable.
        shipped: Returns the shipped set, for Restore shipped Workspaces and
            Reset all layouts. A test passes its own.

    Attributes:
        question: The question dialog open now, or `None`.
        notice_label: The line under the tabs that shows the last notice.
        dismiss_button: Hides the notice line.
    """

    def __init__(
        self,
        workspaces: WorkspaceSet,
        change: Callable[[WorkspaceSet], None],
        open_runs: Callable[[], tuple[RunId, ...]],
        parent: QWidget | None = None,
        *,
        live: Callable[[], WorkspaceSet] | None = None,
        store: WorkspaceStore | None = None,
        notice: str | None = None,
        shipped: Callable[[], WorkspaceSet] = shipped_workspaces,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("workspaceTabs")
        self._change = change
        self._open_runs = open_runs
        self._live = live
        self._store = store
        # Why there is no store, which is the load's notice when there is one.
        self._missing_store = notice if store is None else None
        self._shipped = shipped
        self._workspaces = workspaces
        self._tabs: list[WorkspaceTab] = []
        self._editor: _NameEditor | None = None
        self.question: WorkspaceQuestionDialog | None = None
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(0)
        self._row = QHBoxLayout()
        self._row.setContentsMargins(0, 0, 0, 0)
        self._row.setSpacing(0)
        column.addLayout(self._row)
        self._separator = QFrame(self)
        self._separator.setObjectName("workspaceSeparator")
        self._separator.setFixedWidth(_SEPARATOR_WIDTH)
        self._separator.setStyleSheet(workspace_separator_stylesheet())
        self.add_button = QToolButton(self)
        self.add_button.setObjectName("addWorkspace")
        self.add_button.setText(ADD_WORKSPACE_LABEL)
        self.add_button.setToolTip(_ADD_DESCRIPTION)
        self.add_button.setAccessibleName(_ADD_DESCRIPTION)
        self.add_button.setAutoRaise(True)
        self.add_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.add_button.setStyleSheet(workspace_tab_stylesheet())
        self.add_button.clicked.connect(self.add)
        self.previous_action = self._cycle_action(
            PREVIOUS_WORKSPACE_LABEL, PREVIOUS_WORKSPACE_KEYS, -1
        )
        self.next_action = self._cycle_action(NEXT_WORKSPACE_LABEL, NEXT_WORKSPACE_KEYS, 1)
        self.layout_menu = LayoutMenu(self)
        # Conditional text: why the name a reader typed was not taken.
        self.refusal_label = styled_label("", color=WARNING, size_px=METRIC_QUALIFIER_SIZE)
        self.refusal_label.hide()
        # Conditional text: what the store reported, or what a save did.
        self.notice_label = styled_label("", color=WARNING, size_px=METRIC_QUALIFIER_SIZE)
        self.notice_label.setObjectName("workspaceNotice")
        self.notice_label.setWordWrap(True)
        self.notice_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.dismiss_button = QToolButton(self)
        self.dismiss_button.setObjectName("dismissWorkspaceNotice")
        self.dismiss_button.setText(DISMISS_LABEL)
        self.dismiss_button.setAutoRaise(True)
        self.dismiss_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.dismiss_button.setStyleSheet(workspace_tab_stylesheet())
        self.dismiss_button.clicked.connect(self.dismiss_notice)
        notice_row = QHBoxLayout()
        notice_row.setContentsMargins(0, 0, 0, 0)
        notice_row.addWidget(self.notice_label, 1)
        notice_row.addWidget(self.dismiss_button)
        column.addLayout(notice_row)
        self.dismiss_notice()
        self.show_set(workspaces)

        if notice:
            self.show_notice(notice, warning=True)

    @property
    def workspaces(self) -> WorkspaceSet:
        """The set the strip is drawn from now."""

        return self._workspaces

    def _now(self) -> WorkspaceSet:
        """The set every entry is worked out from: the owner's live one, or the one drawn."""

        return self._workspaces if self._live is None else self._live()

    def current_set(self) -> WorkspaceSet:
        """The set every menu entry is worked out from, as the Layout menu reads it."""

        return self._now()

    @property
    def row(self) -> QHBoxLayout:
        """The row holding the tabs, "+", the rename refusal and the Layout menu."""

        return self._row

    @property
    def tabs(self) -> tuple[WorkspaceTab, ...]:
        """The tabs, in the order they stand."""

        return tuple(self._tabs)

    @property
    def separator(self) -> QFrame:
        """The rule after the shipped tabs, shown only where both groups have a tab."""

        return self._separator

    @property
    def editor(self) -> _NameEditor | None:
        """The in-place name editor while a tab is renamed, or `None`."""

        return self._editor

    def tab_at(self, index: int) -> WorkspaceTab:
        """The tab of the Workspace at position `index` in the set."""

        return next(tab for tab in self._tabs if tab.index == index)

    def show_set(self, workspaces: WorkspaceSet) -> None:
        """Draw the strip from `workspaces`, closing any rename in progress."""

        self._workspaces = workspaces
        self._close_editor()

        while self._row.count():
            self._row.takeAt(0)

        for tab in self._tabs:
            tab.hide()
            tab.deleteLater()

        order = display_order(workspaces)
        self._tabs = [
            WorkspaceTab(self, index, workspaces.workspaces[index], index == workspaces.active)
            for index in order
        ]
        shipped = sum(1 for index in order if workspaces.workspaces[index].origin.is_shipped)

        for place, tab in enumerate(self._tabs):
            if place == shipped and place > 0:
                self._row.addWidget(self._separator)

            self._row.addWidget(tab)

        self._separator.setVisible(0 < shipped < len(self._tabs))

        # The keyboard reaches the tabs in the order they stand, then "+",
        # then the Layout menu, then Dismiss while a notice is shown.
        chain = [*self._tabs, self.add_button, self.layout_menu, self.dismiss_button]

        for before, after in zip(chain, chain[1:], strict=False):
            QWidget.setTabOrder(before, after)
        self._row.addWidget(self.add_button)
        self._row.addWidget(self.refusal_label)
        self._row.addStretch(1)
        self._row.addWidget(self.layout_menu)

    def activate(self, index: int) -> None:
        """Make the Workspace at `index` current."""

        self.tab_at(index).setChecked(index == self._workspaces.active)

        if index != self._workspaces.active:
            self._change(self._now().activate(index))

    def _cycle_action(self, label: str, keys: str, step: int) -> QAction:
        """An action that makes current the Workspace `step` tabs along, on `keys` in the window."""

        action = QAction(label, self)
        action.setShortcut(QKeySequence(keys))
        action.setShortcutContext(Qt.ShortcutContext.WindowShortcut)
        action.triggered.connect(partial(self.cycle, step))
        self.addAction(action)

        return action

    def cycle(self, step: int) -> None:
        """Switch to the Workspace `step` tabs along from the current one, wrapping round.

        The tabs are counted in their display order, with the shipped tabs
        first. After the last tab comes the first, as in Blender's
        `SCREEN_OT_workspace_cycle`. If a tab is being renamed, the name typed so
        far is accepted first, just as it is when the focus moves away. This is
        needed because the shortcut keys reach the window even while the name
        editor has the focus.
        """

        self.finish_rename(keep_open=False)
        now = self._now()
        order = display_order(now)
        place = order.index(now.active)
        self.activate(order[(place + step) % len(order)])

    def add(self) -> None:
        """Duplicate the current Workspace, make the copy current, and rename it in place."""

        now = self._now()
        made = now.duplicate(now.active)
        self._change(made)
        self.rename(made.active)

    def operations(self, index: int) -> tuple[TabOperation, ...]:
        """The menu entries after Rename for the tab at `index`, from the set drawn now."""

        return tab_operations(self._now(), index, self._open_runs())

    def menu_for(self, index: int) -> QMenu:
        """The context menu of the tab at `index`, built from the set drawn now."""

        menu = QMenu(self)
        menu.setStyleSheet(menu_stylesheet())
        menu.setToolTipsVisible(True)
        self.fill_tab_menu(menu, index)

        return menu

    def fill_tab_menu(self, menu: QMenu, index: int) -> None:
        """Add the entries of the tab at `index`'s menu to `menu`: Rename, then `operations`."""

        menu.addAction(RENAME_LABEL).triggered.connect(partial(self.rename, index))

        for operation in self.operations(index):
            action = menu.addAction(operation.label)
            action.setEnabled(operation.available)
            action.setToolTip(operation.refusal or "")
            action.triggered.connect(partial(self.choose, operation))

    def open_menu(self, index: int, at: QPoint) -> None:
        """Open the tab's context menu at `at`, in global coordinates."""

        self.menu_for(index).popup(at)

    def choose(self, operation: TabOperation) -> None:
        """Apply an entry, asking first where it asks."""

        if operation.result is None:
            return

        if operation.question is None:
            self._change(operation.result)
            return

        self._ask(operation.question, partial(self._change, operation.result))

    def save_entry(self) -> SaveEntry:
        """The "Save as default" entry for the set as it stands now."""

        return save_entry(self._store, self._now(), self._missing_store)

    def default_operations(self) -> tuple[TabOperation, TabOperation]:
        """The Restore shipped Workspaces and Reset all layouts entries for the set now."""

        return default_operations(self._now(), self._shipped)

    def save_as_default(self, entry: SaveEntry) -> None:
        """Ask the entry's question, and save the set as it then stands if the reader agrees."""

        if entry.question is None:
            return

        self._ask(entry.question, self._save)

    def _save(self) -> None:
        """Save the set as it stands now, and say what happened under the tabs.

        When the store refuses a save, or the operating system makes it fail,
        the failure is reported here, at the action the reader chose, and the
        session carries on (`PL-SSQW` Q6).
        """

        store = self._store

        if store is None:
            return

        workspaces = self._now()

        try:
            path = store.save(workspaces)
        except (LayoutRefused, WorkspaceFileError) as refusal:
            self.show_notice(_SAVE_FAILED_TEXT.format(reason=refusal), warning=True)
            return

        self.show_notice(
            _SAVED_TEXT.format(count=len(workspaces.workspaces), path=path), warning=False
        )

    def show_notice(self, text: str, *, warning: bool) -> None:
        """Show `text` on the line under the tabs, in the warning colour where `warning`."""

        style_label(
            self.notice_label,
            color=WARNING if warning else INK,
            size_px=METRIC_QUALIFIER_SIZE,
            wrap=True,
        )
        self.notice_label.setText(text[:1].upper() + text[1:])
        self.notice_label.show()
        self.dismiss_button.show()

    def dismiss_notice(self) -> None:
        """Hide the line under the tabs."""

        self.notice_label.hide()
        self.notice_label.clear()
        self.dismiss_button.hide()

    def _ask(self, question: WorkspaceQuestion, then: Callable[[], None]) -> None:
        """Open `question`, and run `then` if the reader goes ahead."""

        dialog = WorkspaceQuestionDialog(question, self)
        dialog.accepted.connect(then)
        dialog.finished.connect(partial(self._question_closed, dialog))
        self.question = dialog
        dialog.open()

    def _question_closed(self, dialog: WorkspaceQuestionDialog, *_result: object) -> None:
        if self.question is dialog:
            self.question = None

        dialog.deleteLater()

    def rename(self, index: int) -> None:
        """Replace the tab at `index` with an editor holding its name."""

        self._close_editor()
        tab = self.tab_at(index)
        editor = _NameEditor(self, index, tab.text())
        self._row.replaceWidget(tab, editor)
        tab.hide()
        self._editor = editor
        editor.show()
        editor.setFocus(Qt.FocusReason.OtherFocusReason)

    def finish_rename(self, *, keep_open: bool) -> None:
        """Take the edited name, or show why it was not taken.

        Args:
            keep_open: If the name is refused, whether the editor stays open
                for another try (after Return) or closes (after the focus moves
                away).
        """

        editor = self._editor

        if editor is None:
            return

        now = self._now()

        try:
            renamed = now.rename(editor.index, WorkspaceName(editor.text()))
        except (InvalidLayout, LayoutRefused) as refusal:
            self.refusal_label.setText(str(refusal))
            self.refusal_label.show()

            if not keep_open:
                self.cancel_rename(keep_refusal=True)

            return

        self.refusal_label.hide()
        self._close_editor()

        if renamed.workspaces[editor.index].name != now.workspaces[editor.index].name:
            self._change(renamed)

    def cancel_rename(self, *, keep_refusal: bool = False) -> None:
        """Close the editor and leave the name as it was."""

        if not keep_refusal:
            self.refusal_label.hide()

        self._close_editor()

    def _close_editor(self) -> None:
        editor = self._editor

        if editor is None:
            return

        self._editor = None
        editor.removeEventFilter(editor)
        tab = next((tab for tab in self._tabs if tab.index == editor.index), None)

        if tab is not None:
            self._row.replaceWidget(editor, tab)
            tab.show()
        else:
            self._row.removeWidget(editor)

        editor.hide()
        editor.deleteLater()

    def focus_beside(self, index: int, step: int) -> None:
        """Move the keyboard focus from the tab at `index` to the one `step` places along."""

        place = self._tabs.index(self.tab_at(index)) + step

        if 0 <= place < len(self._tabs):
            self._tabs[place].setFocus(Qt.FocusReason.TabFocusReason)
