"""The one module that builds splitters: the widget tree drawn from the layout model.

`PL-C842` made the layout's source of truth a pure-Python value,
`layout.model.LayoutModel`, because `QSplitter.saveState()` records no View
identity. This module is the other half of that decision. It builds one
`QSplitter` for each split in the model and puts each Area's View into it. It
is the only module that imports `QSplitter`, and
`tools/import_boundary_check.py` refuses the import anywhere else
(`PL-L8RN`). So no View can see a splitter, save a splitter's state or store
its own geometry.

**A drag changes the model, and the widgets follow the model.** When a reader
drags a handle, Qt reports the new place as a share of the one splitter that
was dragged. The adapter turns that share into a position in the window, asks
`LayoutModel.resize()` for the layout that results, and lays every splitter
out again from it. So the other handles on the dragged border's line move with
it, because `resize()` moves every handle `LayoutModel.borders()` joins to the
dragged one (`PL-5HSG`). A drag the model refuses puts the splitter back where
the model has it.

**A window resize keeps each split's fractions.** Each splitter lays its
children out from the model again whenever it is resized, so rounding to whole
pixels cannot carry the layout away from the model over many resizes.

**Every Area has a header, and the header holds the View chooser**
(`PL-TH35` Q11, `PL-MS34`, `PL-50PZ`). The container draws the header, not
the View, so every View gets the same one. It is one text row on the panel
surface with a 1px rule beneath it. Its first control is the chooser: a flat
menu button showing the Area's View by its registry title, whose menu lists
every registered kind in registry order with the current one checked
(`PL-RBXL`). Choosing an entry calls `LayoutModel.set_view` for that Area and
draws the result. The menu reads the registry and not the Workspace, so every
registered kind, the agent accounting among them, can be brought into any
Area of any layout. That is what `docs/MODEL.md` means by reachable.

**Each Area's View kind is looked up in the View registry.** An Area whose
kind `app/view_registry.py` registers draws the widget the caller's
`view_for` returns for it. An Area whose kind is not registered draws the
failure notice in its place, and `view_for` is never asked for it
(`PL-R1WQ`). The notice names the saved kind, says what became of it, and
tells the reader to choose a View from the chooser above it. Where the View
was renamed, the notice also offers a button that shows it under its new tag,
since a renamed tag is never mapped silently (`PL-R1WQ` Q3). It shows no value
from any run, and the model keeps the kind, so the Area's neighbours draw as
usual and a later save writes back what was read. The notice's look is
`PL-DB5G`'s: a bold title in `WARNING` over a body in `INK`, on the panel
surface, with no fill, border or icon.

**Until `PL-TH35` gives the registry a factory, the caller builds each View,
and may not have one to give.** `view_for` returns None for a registered kind
the caller cannot yet draw in an Area of its own, and that Area shows a notice
saying so. The caller may also hand back a widget another Area already
shows, where it draws only one of that View. A widget cannot sit in two
places, so the second Area shows a notice instead and the first keeps the
View. Both notices are `AreaNotice`s, so a reader meets one shape for every
state in which an Area shows no View (`PL-DB5G`).

**What is not here yet.** A minimum size for each View, and what an Area shows
when it cannot be given that size, are `PL-K285`'s. Until then Qt holds each
View to its own minimum size hint, so a split narrower than that in the model
is drawn at the minimum instead. Shift to move one handle alone, Escape to
cancel a drag and the warning line at a minimum are `PL-2KXB`'s, with the
corner drag and the swap a reader performs. Only the main window is drawn,
because v0.6.0 opens one (`ROADMAP.md` § "v0.6.0 - the layout is the
reader's", "Explicitly out of scope for v0.6.0").
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from functools import partial
from typing import Final

from PySide6.QtCore import QEvent, QRect, Qt, Signal
from PySide6.QtGui import QColor, QEnterEvent, QFont, QPainter, QPaintEvent, QResizeEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QMenu,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QSplitterHandle,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from anesthesia_sim.app.qt_widgets import styled_label
from anesthesia_sim.app.stylesheets import (
    foreground_stylesheet,
    menu_stylesheet,
    outlined_button_stylesheet,
    panel_stylesheet,
    view_chooser_stylesheet,
)
from anesthesia_sim.app.theme import (
    AREA_HANDLE_LINE_WIDTH,
    AREA_HANDLE_WIDTH,
    GRIDLINE,
    INK,
    METRIC_NAME_SIZE,
    PANEL_PADDING,
    PRIMARY,
    WARNING,
)
from anesthesia_sim.app.view_registry import (
    MISSING_VIEW_TITLE,
    REGISTERED,
    RETIRED_TAGS,
    SHOWN_ELSEWHERE_TITLE,
    UNPLACED_VIEW_TITLE,
    RegisteredView,
    RetiredTag,
    missing_view_text,
    rename_offer_text,
    shown_elsewhere_text,
    unplaced_view_text,
)
from anesthesia_sim.layout.exceptions import LayoutRefused
from anesthesia_sim.layout.model import MAIN_WINDOW, Handle, LayoutModel
from anesthesia_sim.layout.tree import Area, AreaId, Node, Orientation, Split, ViewKind

__all__ = ["AreaFrame", "AreaLayout", "AreaNotice", "ViewChooser", "ViewFor"]

type ViewFor = Callable[[Area], QWidget | None]
"""What gives the adapter each Area's View: the widget to draw in that Area.

It returns None for a registered kind the caller cannot yet draw in an Area of
its own, and the Area then shows a notice that says so.
"""

# The height of the rule under an Area's header.
_HEADER_RULE_PX: Final = 1

# A row lays its children out left to right, which Qt calls horizontal, and a
# column stacks them, which Qt calls vertical (`layout/tree.py` says why the
# model does not use Qt's words).
_QT_ORIENTATION: Final = {
    Orientation.ROW: Qt.Orientation.Horizontal,
    Orientation.COLUMN: Qt.Orientation.Vertical,
}


class AreaLayout(QWidget):
    """The main window's Areas, laid out in splitters built from a `LayoutModel`.

    Attributes:
        layout_changed: Emitted with the new `LayoutModel` after a reader's
            drag has changed it. `set_model` does not emit it, because the
            caller already holds the layout it passed.

    Args:
        model: The layout to draw.
        view_for: Gives the widget for each Area whose View kind is
            registered, or None where it has none to give.
        parent: The Qt parent.
        registered: The View kinds this build can draw, in the order each
            Area's chooser lists them. A test passes a registry of its own.
        retired: The tags no View has any more, which the failure notice
            reads. A test passes a table of its own.

    Raises:
        TypeError: `model` is not a `LayoutModel`.
        ValueError: `model` holds more than one window.
    """

    layout_changed = Signal(object)

    def __init__(
        self,
        model: LayoutModel,
        view_for: ViewFor,
        parent: QWidget | None = None,
        *,
        registered: Mapping[str, RegisteredView] = REGISTERED,
        retired: Mapping[str, RetiredTag] = RETIRED_TAGS,
    ) -> None:
        super().__init__(parent)
        self._view_for = view_for
        self._registered = registered
        self._retired = retired
        self._column = QVBoxLayout(self)
        self._column.setContentsMargins(0, 0, 0, 0)
        self._model = _drawable(model)
        self._root: QWidget | None = None
        self._views: list[QWidget] = []
        self._notices: list[AreaNotice] = []
        self._frames: dict[AreaId, AreaFrame] = {}
        self._splitters: dict[tuple[int, ...], _AreaSplitter] = {}
        self._hovered: _AreaHandle | None = None
        self._build()

    @property
    def model(self) -> LayoutModel:
        """The layout drawn now, after every drag the reader has made."""

        return self._model

    def frame(self, area_id: AreaId) -> AreaFrame:
        """The widget drawing the Area `area_id`: its header, and its View or notice under it.

        Raises:
            KeyError: the layout drawn now holds no Area `area_id`.
        """

        return self._frames[area_id]

    def choose_view(self, area_id: AreaId, view: ViewKind) -> None:
        """Show `view` in the Area `area_id`, as its chooser does when the reader picks it.

        Choosing the kind the Area already shows changes nothing. Otherwise
        the model's `set_view` gives the new layout, the widgets are built
        from it, and `layout_changed` is emitted with it.

        Raises:
            TypeError: `area_id` is not an `AreaId`, or `view` not a `ViewKind`.
            NotInLayout: the layout drawn now holds no Area `area_id`.
        """

        moved = self._model.set_view(area_id, view)

        if moved == self._model:
            return

        self._model = moved
        self._build()
        self.layout_changed.emit(moved)

    def set_model(self, model: LayoutModel) -> None:
        """Draw `model` in place of the layout drawn now.

        Where `model` holds the same splits and the same Areas in the same
        places, only the sizes change, and every View stays where it is.
        Otherwise the splitters are built again and each Area's View is asked
        for again. A View the new layout still draws is moved into the new
        splitters. A View it no longer draws is taken out of this widget and
        left to whatever made it. Each failure notice is built again with the
        splitters.

        Raises:
            TypeError: `model` is not a `LayoutModel`.
            ValueError: `model` holds more than one window.
        """

        model = _drawable(model)
        same_shape = _shape(model.windows[MAIN_WINDOW].tree) == _shape(
            self._model.windows[MAIN_WINDOW].tree
        )
        self._model = model

        if same_shape:
            self._lay_out_all()
            self._relight()
        else:
            self._build()

    def _build(self) -> None:
        """Build the splitters for the model and put each Area's View in its place."""

        previous_root = self._root
        previous_views = self._views
        previous_notices = self._notices
        self._views = []
        self._notices = []
        self._frames = {}
        self._splitters = {}
        self._hovered = None
        root = self._widget_for(self._model.windows[MAIN_WINDOW].tree, ())

        for view in previous_views:
            if not any(view is kept for kept in self._views):
                view.setParent(None)

        for notice in previous_notices:
            notice.setParent(None)
            notice.deleteLater()

        if previous_root is not None:
            # The root is an Area's frame or a splitter, never a View, so it
            # always goes; every View it held that is kept has moved already.
            self._column.removeWidget(previous_root)
            previous_root.setParent(None)
            previous_root.deleteLater()

        self._column.addWidget(root)
        self._root = root
        self._lay_out_all()

    def _widget_for(self, node: Node, path: tuple[int, ...]) -> QWidget:
        """The widget drawing `node`: its frame for an Area, a splitter for a split."""

        if isinstance(node, Area):
            chooser = ViewChooser(node, self._registered, self.choose_view)
            frame = AreaFrame(node.id, chooser, self._content_for(node))
            self._frames[node.id] = frame

            return frame

        splitter = _AreaSplitter(self, path, _QT_ORIENTATION[node.orientation])
        self._splitters[path] = splitter

        for index, child in enumerate(node.children):
            splitter.addWidget(self._widget_for(child, path + (index,)))

        splitter.splitterMoved.connect(partial(self._dragged, splitter))

        return splitter

    def _content_for(self, area: Area) -> QWidget:
        """What `area` shows under its header: its View, or the notice saying why not."""

        if area.view not in self._registered:
            offer = rename_offer_text(area.view, self._registered, self._retired)
            notice = AreaNotice(
                MISSING_VIEW_TITLE,
                missing_view_text(area.view, self._registered, self._retired),
                offer_label=offer,
            )

            if notice.offer_button is not None:
                successor = self._retired[area.view].successor
                assert successor is not None, "an offer is made only for a renamed tag"
                notice.offer_button.clicked.connect(partial(self.choose_view, area.id, successor))

            return self._notice(notice)

        view = self._view_for(area)

        if view is None:
            return self._notice(
                AreaNotice(UNPLACED_VIEW_TITLE, unplaced_view_text(area.view, self._registered))
            )

        if any(view is placed for placed in self._views):
            return self._notice(
                AreaNotice(SHOWN_ELSEWHERE_TITLE, shown_elsewhere_text(area.view, self._registered))
            )

        self._views.append(view)

        return view

    def _notice(self, notice: AreaNotice) -> AreaNotice:
        self._notices.append(notice)

        return notice

    def _lay_out_all(self) -> None:
        for splitter in self._splitters.values():
            self._lay_out(splitter)

    def _lay_out(self, splitter: _AreaSplitter) -> None:
        """Give `splitter`'s children the sizes the model holds for its split."""

        if self._splitters.get(splitter.path) is not splitter:
            # A splitter the last rebuild replaced, resized while it waits to
            # be deleted.
            return

        split = _split_at(self._model.windows[MAIN_WINDOW].tree, splitter.path)
        extent = (
            splitter.width()
            if splitter.orientation() == Qt.Orientation.Horizontal
            else splitter.height()
        )
        available = extent - splitter.handleWidth() * (splitter.count() - 1)
        splitter.setSizes(_pixel_sizes(split.sizes, max(available, len(split.sizes))))

    def _dragged(self, splitter: _AreaSplitter, _position_px: int, index: int) -> None:
        """Take a reader's drag of `splitter`'s handle `index` into the model.

        Qt numbers a splitter's handles from 1, each before the child of the
        same index, and `Handle.index` counts the gaps from 0.
        """

        handle = Handle(MAIN_WINDOW, splitter.path, index - 1)
        sizes = splitter.sizes()
        total = sum(sizes)

        if total <= 0:
            return

        low, high = self._model.span(handle)
        position = low + (high - low) * (sum(sizes[:index]) / total)

        try:
            moved = self._model.resize(handle, position)
        except LayoutRefused:
            # Nothing changed in the model, so nothing changes on screen.
            self._lay_out_all()
            return

        changed = moved != self._model
        self._model = moved
        self._lay_out_all()
        self._relight()

        if changed:
            self.layout_changed.emit(moved)

    def _hover(self, handle: _AreaHandle | None) -> None:
        """Mark the handles a drag of `handle` would move, or none when the pointer left."""

        self._hovered = handle
        self._relight()

    def _relight(self) -> None:
        """Light every handle on the hovered handle's line, and only those."""

        lit: list[QSplitterHandle] = []
        hovered = self._hovered

        if hovered is not None and self._splitters.get(hovered.owner.path) is hovered.owner:
            splitter = hovered.owner
            index = next(
                index for index in range(1, splitter.count()) if splitter.handle(index) is hovered
            )

            for member in self._model.borders(Handle(MAIN_WINDOW, splitter.path, index - 1)):
                lit.append(self._splitters[member.path].handle(member.index + 1))

        for splitter in self._splitters.values():
            for index in range(1, splitter.count()):
                handle = splitter.handle(index)

                if isinstance(handle, _AreaHandle):
                    handle.set_lit(any(handle is member for member in lit))


class ViewChooser(QToolButton):
    """The first control of an Area's header: its View's title, and a menu of every View.

    `PL-RBXL` decided it. It is a flat menu button rather than a combo box,
    because this interface uses combo boxes for settings, and choosing a View
    changes no run. It shows the Area's View by its registry title, or by the
    saved tag where the registry does not hold it. Its menu lists every kind
    in `registered`, in registry order, by title, with the current kind
    checked, and nothing marks the kinds that must stay reachable: the
    registry keeps them, so the menu needs no warning. Choosing an entry
    calls `choose`. The menu opens on a click, or on Space with the keyboard
    focus, and the button is in the tab order.

    Args:
        area: The Area whose header holds this chooser.
        registered: The View kinds the menu lists.
        choose: Called with the Area's id and the kind the reader chose.
    """

    def __init__(
        self,
        area: Area,
        registered: Mapping[str, RegisteredView],
        choose: Callable[[AreaId, ViewKind], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("viewChooser")
        current = registered.get(area.view)
        self.setText(area.view if current is None else current.title)
        self.setAccessibleDescription("Choose the View this Area shows")
        self.setStyleSheet(view_chooser_stylesheet())
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        font = QFont(self.font())
        font.setPixelSize(METRIC_NAME_SIZE)
        self.setFont(font)

        menu = QMenu(self)
        menu.setStyleSheet(menu_stylesheet())

        for kind, entry in registered.items():
            action = menu.addAction(entry.title)
            action.setCheckable(True)
            action.setChecked(kind == area.view)
            action.triggered.connect(partial(choose, area.id, ViewKind(kind)))

        self.setMenu(menu)


class AreaFrame(QFrame):
    """One Area as drawn: its header, a rule, and its View or notice filling the rest.

    `PL-MS34` decided the header. It is one text row, as tall as the chooser
    in it, on the panel surface, with a 1px `GRIDLINE` rule under it. The
    chooser is its first control and a stretch follows it. The run's name and
    the Area menu are later items' (`PL-7Z84`, `PL-M352`). The header never
    gets shorter than its row: an Area too short for it is a refused size,
    which is `PL-K285`'s.

    Attributes:
        area_id: The Area this frame draws.
        header: The header row.
        chooser: The View chooser in the header.
        content: The View or the notice under the header.
    """

    def __init__(
        self, area_id: AreaId, chooser: ViewChooser, content: QWidget, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.area_id = area_id
        self.chooser = chooser
        self.content = content

        self.header = QWidget()
        self.header.setObjectName("areaHeader")
        self.header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.header.setStyleSheet(panel_stylesheet(self.header.objectName()))
        # The header asks for no width: what an Area needs is its View's
        # minimum, which is `PL-K285`'s, so a narrow Area clips the title
        # rather than being held wider than its View needs.
        self.header.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        row = QHBoxLayout(self.header)
        row.setContentsMargins(PANEL_PADDING // 2, 0, PANEL_PADDING // 2, 0)
        row.addWidget(chooser)
        row.addStretch(1)

        rule = QFrame()
        rule.setFrameShape(QFrame.Shape.HLine)
        rule.setFixedHeight(_HEADER_RULE_PX)
        rule.setStyleSheet(foreground_stylesheet(GRIDLINE))

        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(0)
        column.addWidget(self.header)
        column.addWidget(rule)
        column.addWidget(content, 1)
        # A View handed back unparented by an earlier layout was hidden when
        # it lost its parent, and a layout does not show it again by itself.
        content.show()


class AreaNotice(QFrame):
    """What an Area shows in place of a View it cannot draw: a title and a body, and nothing else.

    `PL-DB5G` decided one notice for every state in which an Area shows no
    View, so a reader learns its shape once (project owner, 2026-10-11,
    ratified). The title is bold, in `WARNING`, and the body is regular, in
    `INK`, both at `METRIC_NAME_SIZE` and wrapped to the Area's width. They sit
    at the top left of the panel surface, inset by `PANEL_PADDING`. The notice
    has no fill colour of its own, no border and no icon, and it never shows a
    value from a run, since a plausible number in a failure state could be read
    as a View's. Three states are built so far: an unknown View kind, a
    registered View the caller cannot yet put in an Area, and a View another
    Area already shows.

    Args:
        title: The first line.
        body: What happened and what to do.
        parent: The Qt parent.
        offer_label: The label of a button under the body that puts it right,
            such as showing a renamed View under its new tag, or None for no
            button.

    Attributes:
        title_label: The title.
        body_label: The body.
        offer_button: The button `offer_label` names, or None.
    """

    def __init__(
        self,
        title: str,
        body: str,
        parent: QWidget | None = None,
        *,
        offer_label: str | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("areaNotice")
        self.setStyleSheet(panel_stylesheet(self.objectName()))
        self.title_label = styled_label(
            title, color=WARNING, size_px=METRIC_NAME_SIZE, bold=True, wrap=True
        )
        self.body_label = styled_label(body, color=INK, size_px=METRIC_NAME_SIZE, wrap=True)
        column = QVBoxLayout(self)
        column.setContentsMargins(PANEL_PADDING, PANEL_PADDING, PANEL_PADDING, PANEL_PADDING)
        column.addWidget(self.title_label)
        column.addWidget(self.body_label)
        self.offer_button: QPushButton | None = None

        if offer_label is not None:
            self.offer_button = QPushButton(offer_label)
            self.offer_button.setStyleSheet(outlined_button_stylesheet())
            column.addWidget(self.offer_button, 0, Qt.AlignmentFlag.AlignLeft)

        column.addStretch(1)


class _AreaSplitter(QSplitter):
    """One split of the model, drawn: it knows where in the tree it sits, and nothing else."""

    def __init__(self, layout: AreaLayout, path: tuple[int, ...], orientation: Qt.Orientation):
        super().__init__(orientation)
        self.layout_owner = layout
        self.path = path
        # A child dragged to nothing would be an Area that seems to have
        # vanished, and the model holds no Area of zero size.
        self.setChildrenCollapsible(False)
        self.setHandleWidth(AREA_HANDLE_WIDTH)

    def createHandle(self) -> QSplitterHandle:
        return _AreaHandle(self)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.layout_owner._lay_out(self)


class _AreaHandle(QSplitterHandle):
    """A border a reader drags: nothing at rest, a line when a drag of it is one move away.

    `PL-RQT1` decided the look. At rest the handle is a gap that draws
    nothing, so the page shows through between two Areas. With the pointer
    over it, it and every handle on its line show a `PRIMARY` line down the
    middle, because a drag moves all of them. The cursor is the platform's
    double-headed split arrow, which Qt gives a handle by its orientation.
    """

    def __init__(self, splitter: _AreaSplitter) -> None:
        super().__init__(splitter.orientation(), splitter)
        self.owner = splitter
        self._lit = False

    @property
    def lit(self) -> bool:
        """Whether the line is drawn: the pointer is over this handle or one on its line."""

        return self._lit

    def set_lit(self, lit: bool) -> None:
        if lit != self._lit:
            self._lit = lit
            self.update()

    def enterEvent(self, event: QEnterEvent) -> None:
        super().enterEvent(event)
        self.owner.layout_owner._hover(self)

    def leaveEvent(self, event: QEvent) -> None:
        super().leaveEvent(event)
        self.owner.layout_owner._hover(None)

    def paintEvent(self, event: QPaintEvent) -> None:
        if not self._lit:
            return

        rect = self.rect()

        if self.orientation() == Qt.Orientation.Horizontal:
            line = QRect(
                (rect.width() - AREA_HANDLE_LINE_WIDTH) // 2,
                0,
                AREA_HANDLE_LINE_WIDTH,
                rect.height(),
            )
        else:
            line = QRect(
                0,
                (rect.height() - AREA_HANDLE_LINE_WIDTH) // 2,
                rect.width(),
                AREA_HANDLE_LINE_WIDTH,
            )

        painter = QPainter(self)
        painter.fillRect(line, QColor(PRIMARY))
        painter.end()


def _drawable(model: LayoutModel) -> LayoutModel:
    """`model`, once it is a layout this build can draw.

    Raises:
        TypeError: `model` is not a `LayoutModel`.
        ValueError: `model` holds more than one window. An Area in a second
            window would not be drawn at all, so its View would be off the
            screen while the layout says it is shown.
    """

    if not isinstance(model, LayoutModel):
        raise TypeError(f"a layout is a LayoutModel, not {type(model).__name__}")

    if len(model.windows) != 1:
        raise ValueError(
            f"this build draws one window, and the layout holds {len(model.windows)}: taking "
            "an Area into a window of its own is not built yet"
        )

    return model


def _shape(node: Node) -> tuple[object, ...]:
    """What has to match for one tree to be drawn by another's splitters: all but the sizes."""

    if isinstance(node, Area):
        return (node.id, node.view)

    return (node.orientation, tuple(_shape(child) for child in node.children))


def _split_at(tree: Node, path: tuple[int, ...]) -> Split:
    """The split at `path`, which the adapter built a splitter for from this same tree."""

    node = tree

    for step in path:
        if not isinstance(node, Split):
            break

        node = node.children[step]

    if not isinstance(node, Split):
        raise LookupError(f"the layout has no split at {path}")

    return node


def _pixel_sizes(fractions: tuple[float, ...], available: int) -> list[int]:
    """Whole-pixel sizes in the proportion of `fractions`, summing to `available`.

    Each size is rounded down, and the pixels that leaves over go one each to
    the sizes that lost the most, so the sizes sum to `available` exactly and
    no size is more than a pixel from its share.
    """

    exact = [fraction * available for fraction in fractions]
    sizes = [math.floor(share) for share in exact]
    left_over = max(0, min(len(sizes), available - sum(sizes)))
    by_loss = sorted(range(len(sizes)), key=lambda index: (sizes[index] - exact[index], index))

    for index in by_loss[:left_over]:
        sizes[index] += 1

    return sizes
