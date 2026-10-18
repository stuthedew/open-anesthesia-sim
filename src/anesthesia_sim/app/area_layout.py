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

**What is not here yet.** A minimum size for each View, and what an Area shows
when it cannot be given that size, are `PL-K285`'s. Until then Qt holds each
View to its own minimum size hint, so a split narrower than that in the model
is drawn at the minimum instead. Shift to move one handle alone, Escape to
cancel a drag and the warning line at a minimum are `PL-2KXB`'s, with the
corner drag and the swap a reader performs. Looking a View kind up in a
registry, and the failure an unknown kind shows in its Area, are `PL-R1WQ`'s.
Until then the caller passes a function that returns each Area's View. Only
the main window is drawn, because v0.6.0 opens one (`ROADMAP.md` § "v0.6.0 -
the layout is the reader's", "Explicitly out of scope for v0.6.0").
"""

from __future__ import annotations

import math
from collections.abc import Callable
from functools import partial
from typing import Final

from PySide6.QtCore import QEvent, QRect, Qt, Signal
from PySide6.QtGui import QColor, QEnterEvent, QPainter, QPaintEvent, QResizeEvent
from PySide6.QtWidgets import QSplitter, QSplitterHandle, QVBoxLayout, QWidget

from anesthesia_sim.app.theme import AREA_HANDLE_LINE_WIDTH, AREA_HANDLE_WIDTH, PRIMARY
from anesthesia_sim.layout.exceptions import LayoutRefused
from anesthesia_sim.layout.model import Handle, LayoutModel
from anesthesia_sim.layout.tree import Area, Node, Orientation, Split

__all__ = ["AreaLayout", "ViewFor"]

type ViewFor = Callable[[Area], QWidget]
"""What gives the adapter each Area's View: the widget to draw in that Area."""

# A row lays its children out left to right, which Qt calls horizontal, and a
# column stacks them, which Qt calls vertical (`layout/tree.py` says why the
# model does not use Qt's words).
_QT_ORIENTATION: Final = {
    Orientation.ROW: Qt.Orientation.Horizontal,
    Orientation.COLUMN: Qt.Orientation.Vertical,
}

# The main window's index in `LayoutModel.windows`, the only window drawn.
_MAIN_WINDOW: Final = 0


class AreaLayout(QWidget):
    """The main window's Areas, laid out in splitters built from a `LayoutModel`.

    Attributes:
        layout_changed: Emitted with the new `LayoutModel` after a reader's
            drag has changed it. `set_model` does not emit it, because the
            caller already holds the layout it passed.

    Raises:
        TypeError: `model` is not a `LayoutModel`.
        ValueError: `model` holds more than one window.
    """

    layout_changed = Signal(object)

    def __init__(
        self, model: LayoutModel, view_for: ViewFor, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._view_for = view_for
        self._column = QVBoxLayout(self)
        self._column.setContentsMargins(0, 0, 0, 0)
        self._model = _drawable(model)
        self._root: QWidget | None = None
        self._views: list[QWidget] = []
        self._splitters: dict[tuple[int, ...], _AreaSplitter] = {}
        self._hovered: _AreaHandle | None = None
        self._build()

    @property
    def model(self) -> LayoutModel:
        """The layout drawn now, after every drag the reader has made."""

        return self._model

    def set_model(self, model: LayoutModel) -> None:
        """Draw `model` in place of the layout drawn now.

        Where `model` holds the same splits and the same Areas in the same
        places, only the sizes change, and every View stays where it is.
        Otherwise the splitters are built again and each Area's View is asked
        for again. A View the new layout still draws is moved into the new
        splitters. A View it no longer draws is taken out of this widget and
        left to whatever made it.

        Raises:
            TypeError: `model` is not a `LayoutModel`.
            ValueError: `model` holds more than one window.
        """

        model = _drawable(model)
        same_shape = _shape(model.windows[_MAIN_WINDOW].tree) == _shape(
            self._model.windows[_MAIN_WINDOW].tree
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
        self._views = []
        self._splitters = {}
        self._hovered = None
        root = self._widget_for(self._model.windows[_MAIN_WINDOW].tree, ())

        for view in previous_views:
            if not any(view is kept for kept in self._views):
                view.setParent(None)

        if previous_root is not None:
            self._column.removeWidget(previous_root)

            if not any(previous_root is kept for kept in self._views):
                previous_root.setParent(None)
                previous_root.deleteLater()

        self._column.addWidget(root)
        self._root = root
        self._lay_out_all()

    def _widget_for(self, node: Node, path: tuple[int, ...]) -> QWidget:
        """The widget drawing `node`: its View for an Area, a splitter for a split."""

        if isinstance(node, Area):
            view = self._view_for(node)
            self._views.append(view)

            return view

        splitter = _AreaSplitter(self, path, _QT_ORIENTATION[node.orientation])
        self._splitters[path] = splitter

        for index, child in enumerate(node.children):
            splitter.addWidget(self._widget_for(child, path + (index,)))

        splitter.splitterMoved.connect(partial(self._dragged, splitter))

        return splitter

    def _lay_out_all(self) -> None:
        for splitter in self._splitters.values():
            self._lay_out(splitter)

    def _lay_out(self, splitter: _AreaSplitter) -> None:
        """Give `splitter`'s children the sizes the model holds for its split."""

        if self._splitters.get(splitter.path) is not splitter:
            # A splitter the last rebuild replaced, resized while it waits to
            # be deleted.
            return

        split = _split_at(self._model.windows[_MAIN_WINDOW].tree, splitter.path)
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

        handle = Handle(_MAIN_WINDOW, splitter.path, index - 1)
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

            for member in self._model.borders(Handle(_MAIN_WINDOW, splitter.path, index - 1)):
                lit.append(self._splitters[member.path].handle(member.index + 1))

        for splitter in self._splitters.values():
            for index in range(1, splitter.count()):
                handle = splitter.handle(index)

                if isinstance(handle, _AreaHandle):
                    handle.set_lit(any(handle is member for member in lit))


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
