"""The Workspace tab strip, with one tab per Workspace, directly above the Areas, in PySide6.

`PL-QW1Z` decided its place and its look, and `PL-2KXB` builds it. The strip
spans the layout container's width under the unconditional region, because a
tab switches the Areas and nothing above them (Q1). It holds the tabs and a
"+" at its end, and nothing else (Q2). The shipped Workspaces' tabs come
first, then a rule, then the reader's own (Q4).

**The strip owns no Workspace.** It is drawn from the `WorkspaceSet` that the
dashboard holds. Every change a reader makes produces a new set, which the
strip hands to the `change` callback. The dashboard applies it and draws the
strip again with `show_set`. So the set has one owner, as
`.claude/rules/ui-areas.md` asks of any state that the rest of the dashboard
draws from.

**Each menu entry is worked out before it is shown.** `tab_operations` asks
the set what new set each entry would make, in the same way that
`AreaLayout.operations` asks the layout model. An entry the set refuses is
shown disabled, with the reason as its tooltip. So the last Workspace's Delete
is shown as unavailable rather than refused after a click (`PL-WV9K` Q2).

The tab's context menu holds, in `PL-QW1Z` Q3's order: Rename, Duplicate,
Move left, Move right, one entry to pin or unpin each open run, Reset this
Workspace (only on a shipped tab), and Delete. It opens on a right-click, the
Menu key or Shift+F10. A double-click or F2 renames a tab in place. Delete and
Reset ask first, because a session's Workspaces have no undo.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import Final

from PySide6.QtCore import QEvent, QObject, QPoint, Qt
from PySide6.QtGui import QContextMenuEvent, QFont, QKeyEvent, QMouseEvent
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
from anesthesia_sim.app.qt_widgets import declare_interface_colours, styled_label
from anesthesia_sim.app.stylesheets import (
    filled_button_stylesheet,
    menu_stylesheet,
    outlined_button_stylesheet,
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
)
from anesthesia_sim.layout.run_identity import RunId
from anesthesia_sim.layout.shipped import shipped_workspace
from anesthesia_sim.layout.workspace import (
    ShippedWorkspaceId,
    Workspace,
    WorkspaceName,
    WorkspaceSet,
)

__all__ = [
    "ADD_WORKSPACE_LABEL",
    "DELETE_LABEL",
    "DUPLICATE_LABEL",
    "MOVE_LEFT_LABEL",
    "MOVE_RIGHT_LABEL",
    "RENAME_LABEL",
    "RESET_LABEL",
    "TabOperation",
    "WorkspaceQuestion",
    "WorkspaceQuestionDialog",
    "WorkspaceTab",
    "WorkspaceTabs",
    "display_order",
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
_PIN_TEMPLATE: Final = "Pin {run}"
_UNPIN_TEMPLATE: Final = "Unpin {run}"
_ADD_DESCRIPTION: Final = "Duplicate the current Workspace"
_LAST_WORKSPACE_TEXT: Final = "Not available: there is always at least one Workspace."
_FIRST_TEXT: Final = "Not available: this tab is already first in its group."
_LAST_TEXT: Final = "Not available: this tab is already last in its group."
_NO_RUN_TEXT: Final = "Not available: no run is open."
_KEEP_LABEL: Final = "Keep"
_DELETE_TITLE: Final = "Delete this Workspace?"
_DELETE_SHIPPED_TEXT: Final = 'Delete the shipped Workspace "{name}"? This cannot be undone.'
_DELETE_MINE_TEXT: Final = 'Delete your Workspace "{name}"? This cannot be undone.'
_RESET_TITLE: Final = "Reset this Workspace?"
_RESET_TEXT: Final = (
    'Reset "{name}" to the Workspace shipped as "{shipped}"? Its layout and every '
    "View's settings return to the shipped ones. This cannot be undone."
)
_RESET_REFUSED_TEXT: Final = "Not available: {reason}"

#: The width of the rule between the shipped tabs and the reader's own.
_SEPARATOR_WIDTH: Final = 1


@dataclass(frozen=True, slots=True)
class WorkspaceQuestion:
    """What a reader is asked before an entry is applied: a title, one statement, two buttons."""

    title: str
    text: str
    proceed_label: str


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
        return TabOperation(RESET_LABEL, None, _RESET_REFUSED_TEXT.format(reason=refusal))

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


class WorkspaceQuestionDialog(QDialog):
    """The question asked before a Workspace is deleted or reset.

    The dialog is laid out like `NewCaseDialog`, with the destructive button
    first and the safe one last. The entry's own button is outlined. The keep
    button is filled and is the default, so Return and Escape both keep the
    Workspace. `accept()` means "go ahead". The dialog is shown with `open()`,
    so a test can call `accept()` itself.

    Attributes:
        proceed_button: Applies the entry. Its `clicked` signal runs
            `accept()`.
        keep_button: Keeps the Workspace and is the default.
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
        self.keep_button = QPushButton(_KEEP_LABEL)
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
            a duplicate copies what the reader sees. By default, the set that
            was drawn.

    Attributes:
        question: The question dialog open now, or `None`.
    """

    def __init__(
        self,
        workspaces: WorkspaceSet,
        change: Callable[[WorkspaceSet], None],
        open_runs: Callable[[], tuple[RunId, ...]],
        parent: QWidget | None = None,
        *,
        live: Callable[[], WorkspaceSet] | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("workspaceTabs")
        self._change = change
        self._open_runs = open_runs
        self._live = live
        self._workspaces = workspaces
        self._tabs: list[WorkspaceTab] = []
        self._editor: _NameEditor | None = None
        self.question: WorkspaceQuestionDialog | None = None
        self._row = QHBoxLayout(self)
        self._row.setContentsMargins(0, 0, 0, 0)
        self._row.setSpacing(0)
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
        # Conditional text: why the name a reader typed was not taken.
        self.refusal_label = styled_label("", color=WARNING, size_px=METRIC_QUALIFIER_SIZE)
        self.refusal_label.hide()
        self.show_set(workspaces)

    @property
    def workspaces(self) -> WorkspaceSet:
        """The set the strip is drawn from now."""

        return self._workspaces

    def _now(self) -> WorkspaceSet:
        """The set every entry is worked out from: the owner's live one, or the one drawn."""

        return self._workspaces if self._live is None else self._live()

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

        # The keyboard reaches the tabs in the order they stand, then "+".
        for before, after in zip(self._tabs, [*self._tabs[1:], self.add_button], strict=True):
            QWidget.setTabOrder(before, after)
        self._row.addWidget(self.add_button)
        self._row.addWidget(self.refusal_label)
        self._row.addStretch(1)

    def activate(self, index: int) -> None:
        """Make the Workspace at `index` current."""

        self.tab_at(index).setChecked(index == self._workspaces.active)

        if index != self._workspaces.active:
            self._change(self._now().activate(index))

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
        menu.addAction(RENAME_LABEL).triggered.connect(partial(self.rename, index))

        for operation in self.operations(index):
            action = menu.addAction(operation.label)
            action.setEnabled(operation.available)
            action.setToolTip(operation.refusal or "")
            action.triggered.connect(partial(self.choose, operation))

        return menu

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

        dialog = WorkspaceQuestionDialog(operation.question, self)
        dialog.accepted.connect(partial(self._change, operation.result))
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
