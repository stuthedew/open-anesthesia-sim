"""Build the splitter widget tree from the layout model.

This is the only module that builds splitters. `PL-C842` made the layout's
source of truth a pure-Python value, `layout.model.LayoutModel`, because
`QSplitter.saveState()` records no View identity. This module is the other
half of that decision. It builds one `QSplitter` for each split in the model
and puts each Area's View into it. It is the only module that imports
`QSplitter`, and `tools/import_boundary_check.py` rejects that import anywhere
else (`PL-L8RN`). So no View can see a splitter, save a splitter's state or
store its own geometry.

**A drag changes the model, and the widgets follow the model.** When a reader
drags a handle, Qt reports the new position as a fraction of the one splitter
that was dragged. The adapter turns that fraction into a position in the
window and asks `LayoutModel.resize()` for the layout that results. It then
lays every splitter out again from that layout. `LayoutModel.borders()` gives
the handles that are joined to the dragged one, and `resize()` moves all of
them (`PL-5HSG`). So the other handles on the dragged border's line move with
the dragged handle. When the model rejects a drag, the splitter goes back to
the position that the model holds.

**A window resize keeps each split's fractions.** Each splitter lays its
children out from the model again whenever it is resized, so rounding to whole
pixels cannot carry the layout away from the model over many resizes.

**Every Area has a header, and the header holds the View chooser**
(`PL-TH35` Q11, `PL-MS34`, `PL-50PZ`). The container draws the header, not
the View, so every View gets the same header. The header is one row of text
on the panel surface, with a 1px rule beneath it. Its first control is the
chooser. The chooser is a flat menu button that shows the Area's View by its
registry title. Its menu lists every registered kind in registry order, with
the current kind checked (`PL-RBXL`). Choosing an entry calls
`LayoutModel.set_view` for that Area and draws the result. The menu takes its
list from the registry and not from the Workspace. So any registered kind,
including the agent accounting, can be brought into any Area of any layout.
That is what `docs/MODEL.md` means by reachable.

**Each Area's View kind is looked up in the View registry, and its View is
built by the entry's factory** (`PL-R1WQ`, `PL-TH35`). The factory is called
with a `ViewContext`. The context holds two things: how the View asks for a
change to shared state, and the state that this layout kept for that Area and
kind. So every registered kind can be drawn in any Area, and two Areas that
name one kind each get their own View. This module is the only caller of the
View contract's members (`app/view_contract.py`). It hands every View each
frame's `ViewTick`. It asks each View for the plot width that its frame must
be sampled for. It saves a View's state when the reader replaces that View
through the chooser. When that kind returns to that Area, its View is built
from the saved state. A View that the layout still draws in the same Area
keeps its instance across a rebuild. An Area whose kind is not registered
draws the failure notice instead of a View, and no factory is called for it.
An Area whose factory raises, or returns something that is not a View, draws a
notice that names the error, and the other Areas are built as usual.
The missing-kind notice names the saved kind, says what became of it, and tells the reader
to choose a View from the chooser above it. Where the View was renamed, the
notice also offers a button that shows the View under its new tag. The button
is there because a renamed tag is never mapped silently (`PL-R1WQ` Q3). The
notice shows no value from any run. The model keeps the kind, so the Area's
neighbours draw as usual and a later save writes back the kind that was read.
The notice uses the look that `PL-DB5G` set: a bold title in `WARNING` over a
body in `INK`, on the panel surface, with no fill, border or icon.

**Every Area has a menu at the end of its header** (`PL-MS34` Q2,
`PL-2KXB`). It holds the operations on the Area's place: a split left and
right or top and bottom, a join with each neighbour, a swap with every other
Area, and Close Area, which gives the place to a neighbour. Each entry is
worked out by asking the model for the layout it makes, and an entry the model
or the Area's size refuses is shown disabled with the reason beside it. So a
join the layout cannot make is visibly unavailable, and never approximated.

**A reader also splits and joins by dragging** (`PL-30L5`, `PL-RQT1`). Each
corner of an Area is a 16 px zone with a cross cursor. A drag inside the Area
previews a split through the pointer, and a drag into a neighbour previews a
join. The preview is drawn over the Areas, and nothing changes until release.
A border drag re-lays out the Areas live and stops, in WARNING, where an Area
beside the moved line reaches its least size. Shift moves one border alone,
and Escape undoes either drag.

**No View is drawn below the size it needs** (`PL-K285`). Each Area's need is
its View's, the larger of the minimum its registry entry declares and the
least size Qt would hold the View widget to, with the header above it.
`layout/sizing.py`'s `settle` works out the sizes at this widget's size, and
each frame is held at the size it was given, so a border drag stops at a
neighbour's need. This widget's minimum size hint is every need added up, so a
host that can grow, as the dashboard's scrolling page does, always gives every
View its size. Where the host cannot, an Area that the latest change did not
leave in place gives way first. It is held at its header and shows the size
its View needs against the size it has, until a later change can give it
that.

**What is not here yet.** The Workspace tab strip is left to `PL-2KXB`. Only
the main window is drawn, because v0.6.0 opens only one window (`ROADMAP.md`
§ "v0.6.0 - the layout is the reader's", "Explicitly out of scope for
v0.6.0").
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from collections.abc import Set as AbstractSet
from dataclasses import dataclass
from enum import Enum
from functools import partial
from typing import Final, cast

from PySide6.QtCore import QEvent, QPoint, QRect, QSize, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QEnterEvent,
    QFont,
    QFontMetrics,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPen,
    QResizeEvent,
    QShowEvent,
)
from PySide6.QtWidgets import (
    QApplication,
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
    AREA_CLOSING_TINT_ALPHA,
    AREA_CORNER_ZONE,
    AREA_GRIP_STROKE_LENGTH,
    AREA_GRIP_STROKE_WIDTH,
    AREA_GRIP_STROKES,
    AREA_HANDLE_LINE_WIDTH,
    AREA_HANDLE_WIDTH,
    AREA_PREVIEW_LINE_WIDTH,
    GRIDLINE,
    INK,
    METRIC_NAME_SIZE,
    MUTED,
    PANEL_PADDING,
    PRIMARY,
    WARNING,
)
from anesthesia_sim.app.view_contract import SavedState, View, ViewContext, ViewRequests, ViewTick
from anesthesia_sim.app.view_registry import (
    MISSING_VIEW_TITLE,
    REGISTERED,
    RETIRED_TAGS,
    UNBUILT_VIEW_TITLE,
    RegisteredView,
    RetiredTag,
    missing_view_text,
    pinned_run_absent_text,
    pinned_run_absent_title,
    rename_offer_text,
    too_small_text,
    too_small_title,
    unbuilt_view_text,
)
from anesthesia_sim.layout.exceptions import LayoutRefused
from anesthesia_sim.layout.model import (
    BORDER_ALIGNMENT_TOLERANCE,
    MAIN_WINDOW,
    Handle,
    LayoutModel,
    Neighbour,
    Rectangle,
    Side,
)
from anesthesia_sim.layout.sizing import (
    Fit,
    PixelSize,
    TooSmall,
    apportion,
    minimum_extent,
    pixel_sizes,
    settle,
)
from anesthesia_sim.layout.tree import Area, AreaId, Node, Orientation, Split, ViewKind

__all__ = [
    "AREA_MENU_LABEL",
    "CLOSE_AREA_LABEL",
    "JOIN_WITH_LABEL",
    "SPLIT_SIDE_BY_SIDE_LABEL",
    "SPLIT_STACKED_LABEL",
    "SWAP_WITH_LABEL",
    "AreaFrame",
    "AreaLayout",
    "AreaMenu",
    "AreaNotice",
    "AreaOperation",
    "JoinPreview",
    "SplitPreview",
    "ViewChooser",
]

# The height of the rule under an Area's header.
_HEADER_RULE_PX: Final = 1

# The space at each end of an Area's header row, before the chooser and after
# the Area menu. It is as wide as a corner's drag zone, so the zone never takes
# the first click meant for a header control (`PL-30L5` Q1).
_HEADER_MARGIN_PX: Final = AREA_CORNER_ZONE

# The Area menu and its entries (`PL-MS34` Q2, `PL-2KXB`). The wording is a
# placeholder until the visual pass, planned-milestone item 33. A split names
# where the two halves lie, since "horizontal" and "vertical" are read both
# ways.
AREA_MENU_LABEL: Final = "Area"
SPLIT_SIDE_BY_SIDE_LABEL: Final = "Split left and right"
SPLIT_STACKED_LABEL: Final = "Split top and bottom"
JOIN_WITH_LABEL: Final = "Join with"
SWAP_WITH_LABEL: Final = "Swap with"
CLOSE_AREA_LABEL: Final = "Close Area"

# Where a split made from the menu falls: halfway across the Area.
_MENU_SPLIT_AT: Final = 0.5

# How a neighbour's side is said in a menu entry.
_SIDE_WORDS: Final = {
    Side.LEFT: "on the left",
    Side.ABOVE: "above",
    Side.RIGHT: "on the right",
    Side.BELOW: "below",
}

# Why an operation is unavailable, shown beside its entry. A refusal names no
# Area id, since a reader never sees one.
_ONLY_AREA_TEXT: Final = "Not available: this is the only Area."
_NO_WHOLE_EDGE_TEXT: Final = (
    "Not available: the two Areas do not share a whole edge, so together they would not "
    "make a rectangle."
)
_NOT_EXPRESSIBLE_TEXT: Final = "Not available: the layout cannot be divided that way."
_NOTHING_TAKES_ITS_PLACE_TEXT: Final = (
    "Not available: no Area beside this one shares a whole edge with it, so none can take "
    "its place."
)
_TOO_SMALL_TO_SPLIT_TEXT: Final = (
    "Not available: each half would be too small to hold its header and one line of text."
)


@dataclass(frozen=True, slots=True)
class AreaOperation:
    """One entry of an Area's menu: what it is called, and the layout it would make.

    The layout is worked out by asking the model for it, which is how the
    model says whether an operation is available (`layout/model.py`). Where
    the model or the Area's size refuses it, `result` is None and `refusal`
    says why in the reader's words.

    Attributes:
        label: The entry's text.
        group: The submenu holding the entry, `JOIN_WITH_LABEL` or
            `SWAP_WITH_LABEL`, or None for the menu itself.
        result: The layout choosing the entry makes, or None where it is
            unavailable.
        refusal: Why it is unavailable, or "" where it is available.
    """

    label: str
    group: str | None
    result: LayoutModel | None
    refusal: str = ""

    @property
    def available(self) -> bool:
        return self.result is not None


@dataclass(frozen=True, slots=True)
class SplitPreview:
    """A corner drag inside its own Area: where the cut would fall, and the layout it makes.

    Attributes:
        area_id: The Area being split.
        orientation: `ROW` for a cut into left and right, `COLUMN` for top
            and bottom.
        at: Where the cut falls, as a fraction of the Area across the cut.
        result: The layout releasing the drag makes, or None where a part
            would be too small to hold its header, in which case the line is
            drawn in WARNING and releasing changes nothing.
    """

    area_id: AreaId
    orientation: Orientation
    at: float
    result: LayoutModel | None


@dataclass(frozen=True, slots=True)
class JoinPreview:
    """A corner drag into a neighbour: the Area that keeps its View, the one that closes.

    Attributes:
        keep: The Area the drag started in, which takes the other's place.
        remove: The Area under the pointer, which closes.
        result: The layout releasing the drag makes, or None where the two
            cannot be joined, in which case releasing changes nothing.
    """

    keep: AreaId
    remove: AreaId
    result: LayoutModel | None


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
        views_changed: Emitted once the Areas are built again, after a View
            is chosen or a layout of another shape is set. A View built then
            has drawn nothing yet, so the caller draws a frame at once rather
            than leave its Area blank until the next tick.

    Args:
        model: The layout to draw.
        requests: How every View asks the dashboard to change shared state,
            handed to each in its `ViewContext`.
        parent: The Qt parent.
        registered: The View kinds this build can draw, in the order each
            Area's chooser lists them. A test passes a registry of its own.
        retired: The tags no View has any more, which the failure notice
            reads. A test passes a table of its own.
        states: The state each View is built from, by its Area and kind, as
            a Workspace keeps it. By default, none.

    A factory that raises, or that returns something other than a
    `QWidget` satisfying `View`, leaves its Area showing a notice that names
    the error, and every other Area is built as usual.

    Raises:
        TypeError: `model` is not a `LayoutModel`.
        ValueError: `model` holds more than one window.
    """

    layout_changed = Signal(object)
    views_changed = Signal()

    def __init__(
        self,
        model: LayoutModel,
        requests: ViewRequests,
        parent: QWidget | None = None,
        *,
        registered: Mapping[str, RegisteredView] = REGISTERED,
        retired: Mapping[str, RetiredTag] = RETIRED_TAGS,
        states: Mapping[AreaId, Mapping[ViewKind, SavedState]] | None = None,
    ) -> None:
        # Refuse an undrawable layout before any widget exists, so the refusal
        # needs no QApplication and leaves nothing half-built behind it.
        drawable = _drawable(model)
        super().__init__(parent)
        self._requests = requests
        self._registered = registered
        self._retired = retired
        self._column = QVBoxLayout(self)
        self._column.setContentsMargins(0, 0, 0, 0)
        self._model = drawable
        self._previous_views: dict[AreaId, tuple[ViewKind, View]] = {}
        self._root: QWidget | None = None
        # Each Area's View, with the kind it was built for, in reading order.
        self._views: dict[AreaId, tuple[ViewKind, View]] = {}
        # The state of each View the reader replaced, by its Area and kind.
        self._saved: dict[tuple[AreaId, ViewKind], SavedState] = _flattened(states or {})
        self._notices: list[AreaNotice] = []
        self._frames: dict[AreaId, AreaFrame] = {}
        self._splitters: dict[tuple[int, ...], _AreaSplitter] = {}
        self._hovered: _AreaHandle | None = None
        self._border_drag: _BorderDrag | None = None
        self._at_minimum = False
        self._corner_drag: tuple[AreaId, QPoint] | None = None
        self.preview: SplitPreview | JoinPreview | None = None
        self._overlay = _LayoutOverlay(self)
        # What the last settle decided: each Area's size, and which Areas are
        # too small for their View (`layout/sizing.py`).
        self._fit: Fit | None = None
        self._drawn: frozenset[AreaId] = frozenset()
        # The pinned run's name, and whether it is absent (`show_pin`).
        self._pin: tuple[str | None, bool] = (None, False)
        self._settling = False
        self._least: PixelSize | None = None
        self._build(frozenset())

    @property
    def model(self) -> LayoutModel:
        """The layout drawn now, after every drag the reader has made."""

        return self._model

    def views(self) -> tuple[QWidget, ...]:
        """Every View drawn now, in the reading order of the Areas that show them."""

        return tuple(_widget(view) for _, view in self._views.values())

    def refresh(self, tick: ViewTick) -> None:
        """Draw `tick` in every View, in the reading order of their Areas.

        Raises:
            Exception: whatever a View raises while drawing. The Views after
                it are not drawn, and the caller halts every run.
        """

        for _, view in tuple(self._views.values()):
            view.refresh(tick)

    @property
    def owes_a_frame(self) -> bool:
        """Whether any View needs a frame although nothing in the runs changed."""

        return any(view.owes_a_frame for _, view in self._views.values())

    def frame_width_px(self) -> float:
        """The widest plot any View needs its frame sampled for, or 0 where none draws one.

        At 0, `chart_frame.chart_columns` samples the frame at its floor.
        """

        widths = [
            width
            for _, view in self._views.values()
            if (width := view.frame_width_px()) is not None
        ]

        return max(widths, default=0.0)

    def painted_strings(self) -> tuple[tuple[QWidget, str], ...]:
        """The text every View paints without a label or a button, in reading order.

        Each string comes with the View that paints it, so that a caller can
        ask whether the reader can see that View now.
        """

        return tuple(
            (_widget(view), text)
            for _, view in self._views.values()
            for text in view.painted_strings()
        )

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

        self._apply(self._model.set_view(area_id, view))

    def operations(self, area_id: AreaId) -> tuple[AreaOperation, ...]:
        """The entries of the Area `area_id`'s menu, each with the layout it would make.

        In order: the two splits, a join with each neighbour, a swap with
        every other Area, and Close Area. A split falls halfway across the
        Area, and the new half shows the same kind of View, built from a copy of
        the source View's state. "Join with" lists every
        Area whose edge meets this one, and the Area keeps its View and takes
        the other's place. A neighbour that does not share a whole edge with
        it is listed and unavailable, so a join the layout cannot make is
        shown as unavailable rather than left out. "Close Area" gives the
        Area's place to the first neighbour, in the order `neighbours` gives,
        that shares a whole edge with it. Each refused entry says why.

        Raises:
            TypeError: `area_id` is not an `AreaId`.
            NotInLayout: the layout drawn now holds no Area `area_id`.
        """

        model = self._model
        model.area(area_id)
        entries = [
            self._split_operation(area_id, Orientation.ROW, SPLIT_SIDE_BY_SIDE_LABEL),
            self._split_operation(area_id, Orientation.COLUMN, SPLIT_STACKED_LABEL),
        ]
        neighbours = model.neighbours(area_id)

        for neighbour in neighbours:
            label = f"{self._title(neighbour.area_id)}, {_SIDE_WORDS[neighbour.side]}"
            entries.append(
                _attempt(label, JOIN_WITH_LABEL, partial(model.join, area_id, neighbour.area_id))
                if neighbour.whole_edge
                else AreaOperation(label, JOIN_WITH_LABEL, None, _NO_WHOLE_EDGE_TEXT)
            )

        own = model.rectangle(area_id)

        for area in model.areas():
            if area.id == area_id:
                continue

            label = f"{self._title(area.id)}, {_relative_place(own, model.rectangle(area.id))}"
            entries.append(_attempt(label, SWAP_WITH_LABEL, partial(model.swap, area_id, area.id)))

        entries.append(self._close_operation(area_id, neighbours))

        return tuple(entries)

    def perform(self, operation: AreaOperation) -> None:
        """Draw the layout an available menu entry makes, as choosing it does.

        Raises:
            ValueError: `operation` is unavailable.
        """

        if operation.result is None:
            raise ValueError(f"{operation.label!r} is unavailable: {operation.refusal}")

        self._apply(operation.result)

    def _apply(self, moved: LayoutModel) -> None:
        """Draw `moved` and say so, unless it is the layout drawn now."""

        if moved == self._model:
            return

        self._copy_split_state(moved)
        kept = self._unmoved(moved)
        self._model = moved
        self._build(kept)
        self.layout_changed.emit(moved)

    def _unmoved(self, moved: LayoutModel) -> frozenset[AreaId]:
        """The Areas drawn now that `moved` leaves with the same View in the same place.

        `settle` lets these go to their floors last, so an Area the reader did
        not touch keeps its View when the change cannot fit (`PL-K285`).
        """

        held = {area.id: area.view for area in moved.areas()}

        return frozenset(
            area_id
            for area_id in self._drawn
            if held.get(area_id) == self._model.area(area_id).view
            and _same_place(self._model.rectangle(area_id), moved.rectangle(area_id))
        )

    def _copy_split_state(self, moved: LayoutModel) -> None:
        """Give each Area that a split makes in `moved` a copy of its source View's state.

        `PL-TH35` Q10 has the new half of a split start from the settings of
        the View it was cut from, so a reader who splits a chart gets two
        identical charts. `LayoutModel.split` gives the new Area the part
        after the cut and the same kind of View, so in reading order it comes
        straight after the Area it was cut from.
        """

        held = {area.id for area in self._model.areas()}
        areas = moved.areas()

        for source, area in zip(areas, areas[1:], strict=False):
            if area.id in held or source.id not in held or source.view != area.view:
                continue

            shown = self._views.get(source.id)

            if shown is not None and shown[0] == area.view:
                self._saved[(area.id, area.view)] = shown[1].save_state()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._overlay.setGeometry(self.rect())
        self._settle(self._drawn)

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        # Until it is shown, this widget's size is not the one it is drawn
        # at, so which Areas are too small is first decided here.
        self._settle(self._drawn)

    def minimum_extent(self) -> PixelSize:
        """The least size at which every Area draws its View: their needs, added up.

        It is this widget's minimum size hint, so a host that can grow never
        gives it less (`PL-K285` Q2). A host that cannot is given what it
        can, and the Areas it cannot hold show that they are too small.
        """

        least = self._least
        assert least is not None, "every build settles the Areas"

        return least

    def minimumSizeHint(self) -> QSize:
        least = self.minimum_extent()

        return QSize(least.width_px, least.height_px)

    def too_small(self) -> tuple[TooSmall, ...]:
        """The Areas too small for their View now, in reading order, with the size each needs."""

        fit = self._fit
        assert fit is not None, "every build settles the Areas"

        return fit.too_small

    def corner_pressed(self, area_id: AreaId, at: QPoint) -> None:
        """Start a corner drag of the Area `area_id`, pressed at `at` on the screen."""

        self._corner_drag = (area_id, at)
        self._show_preview(None)

    def corner_moved(self, at: QPoint) -> None:
        """Preview what releasing the corner drag at `at`, on the screen, would do."""

        if self._corner_drag is not None:
            self._show_preview(self._preview_at(*self._corner_drag, at))

    def corner_released(self, at: QPoint) -> None:
        """Make the split or join the drag previews at `at`, where it can be made."""

        if self._corner_drag is None:
            return

        preview = self._preview_at(*self._corner_drag, at)
        self.corner_cancelled()

        if isinstance(preview, SplitPreview) and preview.result is not None:
            self._apply(preview.result)
        elif isinstance(preview, JoinPreview) and preview.result is not None:
            self._apply(preview.result)

    def corner_cancelled(self) -> None:
        """End a corner drag with nothing changed, as Escape does."""

        self._corner_drag = None
        self._show_preview(None)

    def _show_preview(self, preview: SplitPreview | JoinPreview | None) -> None:
        self.preview = preview
        self._overlay.update()

    def frame_rect(self, area_id: AreaId) -> QRect:
        """Where the Area `area_id` is drawn, in this widget's coordinates."""

        frame = self._frames[area_id]

        return QRect(frame.mapTo(self, QPoint(0, 0)), frame.size())

    def _preview_at(
        self, area_id: AreaId, pressed: QPoint, at: QPoint
    ) -> SplitPreview | JoinPreview | None:
        """What a corner drag of `area_id` from `pressed` would do if released at `at`.

        Inside its own Area, the drag splits it. The cut runs across the
        direction the pointer has moved further in, through the pointer, so a
        drag sideways cuts the Area into left and right. Nothing is previewed
        until the pointer has moved the platform's drag distance. In another
        Area, the drag joins that Area into this one, which keeps its View.
        Anywhere else, nothing is previewed.
        """

        local = self.mapFromGlobal(at)
        own = self.frame_rect(area_id)

        if own.contains(local):
            moved = at - pressed

            if max(abs(moved.x()), abs(moved.y())) < QApplication.startDragDistance():
                return None

            if abs(moved.x()) >= abs(moved.y()):
                return self._split_preview(
                    area_id, Orientation.ROW, local.x() - own.left(), own.width()
                )

            return self._split_preview(
                area_id, Orientation.COLUMN, local.y() - own.top(), own.height()
            )

        for other in self._frames:
            if other != area_id and self.frame_rect(other).contains(local):
                result = _attempt("", None, partial(self._model.join, area_id, other)).result

                return JoinPreview(area_id, other, result)

        return None

    def _split_preview(
        self, area_id: AreaId, orientation: Orientation, offset_px: int, extent_px: int
    ) -> SplitPreview:
        """A cut `offset_px` into an Area `extent_px` long, refused where a part is too small."""

        minimum = _structural_minimum(self._frames[area_id])
        needed = minimum[0] if orientation is Orientation.ROW else minimum[1]
        at = offset_px / extent_px if extent_px > 0 else 0.0
        result: LayoutModel | None = None

        if needed <= offset_px and needed <= extent_px - offset_px - AREA_HANDLE_WIDTH:
            try:
                result = self._model.split(area_id, orientation, at)[0]
            except LayoutRefused:
                result = None

        return SplitPreview(area_id, orientation, at, result)

    def _title(self, area_id: AreaId) -> str:
        """The View an Area shows, by its registry title, or by its tag where none is held."""

        view = self._model.area(area_id).view
        entry = self._registered.get(view)

        return view if entry is None else entry.title

    def _split_operation(
        self, area_id: AreaId, orientation: Orientation, label: str
    ) -> AreaOperation:
        """A split of the Area halfway across, refused where a half could not hold its header."""

        frame = self._frames[area_id]
        minimum = _structural_minimum(frame)

        if orientation is Orientation.ROW:
            half, needed = (frame.width() - AREA_HANDLE_WIDTH) / 2, minimum[0]
        else:
            half, needed = (frame.height() - AREA_HANDLE_WIDTH) / 2, minimum[1]

        if half < needed:
            return AreaOperation(label, None, None, _TOO_SMALL_TO_SPLIT_TEXT)

        return _attempt(label, None, partial(_split_layout, self._model, area_id, orientation))

    def _close_operation(self, area_id: AreaId, neighbours: tuple[Neighbour, ...]) -> AreaOperation:
        """Give the Area's place to the first neighbour sharing a whole edge with it."""

        if len(self._model.areas()) == 1:
            return AreaOperation(CLOSE_AREA_LABEL, None, None, _ONLY_AREA_TEXT)

        for neighbour in neighbours:
            if neighbour.whole_edge:
                taken = _attempt(
                    CLOSE_AREA_LABEL, None, partial(self._model.join, neighbour.area_id, area_id)
                )

                if taken.available:
                    return taken

        return AreaOperation(CLOSE_AREA_LABEL, None, None, _NOTHING_TAKES_ITS_PLACE_TEXT)

    def set_model(self, model: LayoutModel) -> None:
        """Draw `model` in place of the layout drawn now.

        Where `model` holds the same splits and the same Areas in the same
        places, only the sizes change, and every View stays where it is.
        Otherwise the splitters are built again. An Area that still shows the
        same kind keeps its View, moved into the new splitters. Any other
        View's state is saved under its Area and kind, and the View is
        deleted. Each failure notice is built again with the splitters.

        Raises:
            TypeError: `model` is not a `LayoutModel`.
            ValueError: `model` holds more than one window.
        """

        model = _drawable(model)
        same_shape = _shape(model.windows[MAIN_WINDOW].tree) == _shape(
            self._model.windows[MAIN_WINDOW].tree
        )
        kept = self._unmoved(model)
        self._model = model

        if same_shape:
            self._settle(kept)
            self._relight()
        else:
            self._build(kept)

    def show_pin(self, run_name: str | None, *, absent: bool) -> None:
        """Name the Workspace's pinned run on every Area, and state on each whether it is absent.

        Held across rebuilds, so an Area made by a split shows it too. See
        `AreaFrame.show_pin`.
        """

        if self._pin == (run_name, absent):
            return

        self._pin = (run_name, absent)

        for frame in self._frames.values():
            frame.show_pin(run_name, absent=absent)

    def view_states(self) -> dict[AreaId, dict[ViewKind, SavedState]]:
        """Each View's state by its Area and kind, as a Workspace keeps it.

        That is the state of every View drawn now, and the state kept for
        each View the reader replaced in an Area the layout still holds. So a
        Workspace left and come back to shows each View as it was left
        (`PL-2KXB`).
        """

        held = {area.id for area in self._model.areas()}
        states: dict[AreaId, dict[ViewKind, SavedState]] = {}

        for (area_id, kind), state in self._saved.items():
            if area_id in held:
                states.setdefault(area_id, {})[kind] = state

        for area_id, (kind, view) in self._views.items():
            states.setdefault(area_id, {})[kind] = view.save_state()

        return states

    def load(
        self, model: LayoutModel, states: Mapping[AreaId, Mapping[ViewKind, SavedState]]
    ) -> None:
        """Draw another Workspace: `model`, with every View built again from `states`.

        No View drawn now is carried over, even in an Area of the same id and
        kind, because each Workspace holds its Views' state apart. A switch
        to a Workspace and back therefore shows what that Workspace held.

        Raises:
            TypeError: `model` is not a `LayoutModel`.
            ValueError: `model` holds more than one window.
        """

        self._model = _drawable(model)
        self._saved = _flattened(states)
        # The Views go with the splitters `_build` replaces, unsaved.
        self._views = {}
        self._build(frozenset())

    def _build(self, kept: AbstractSet[AreaId]) -> None:
        """Build the splitters for the model and put each Area's View in its place.

        `kept` names the Areas `settle` lets go last where the new layout
        cannot give every Area its View's size.
        """

        previous_root = self._root
        self._previous_views = self._views
        previous_notices = self._notices
        self._views = {}
        self._notices = []
        self._frames = {}
        self._splitters = {}
        self._hovered = None
        # A drag addresses a handle of the splitters being replaced.
        self._border_drag = None
        self._at_minimum = False
        root = self._widget_for(self._model.windows[MAIN_WINDOW].tree, ())

        for area_id, (kind, view) in self._previous_views.items():
            if not any(view is kept for _, kept in self._views.values()):
                self._saved[(area_id, kind)] = view.save_state()
                widget = _widget(view)
                widget.setParent(None)
                widget.deleteLater()

        self._previous_views = {}

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

        for frame in self._frames.values():
            frame.show_pin(self._pin[0], absent=self._pin[1])

        self._settle(kept)
        self._overlay.raise_()
        self.views_changed.emit()

    def _widget_for(self, node: Node, path: tuple[int, ...]) -> QWidget:
        """The widget drawing `node`: its frame for an Area, a splitter for a split."""

        if isinstance(node, Area):
            chooser = ViewChooser(node, self._registered, self.choose_view)
            menu = AreaMenu(node.id, self.operations, self.perform)
            frame = AreaFrame(node.id, chooser, self._content_for(node), menu=menu, drags=self)
            self._frames[node.id] = frame

            return frame

        splitter = _AreaSplitter(self, path, _QT_ORIENTATION[node.orientation])
        self._splitters[path] = splitter

        for index, child in enumerate(node.children):
            splitter.addWidget(self._widget_for(child, path + (index,)))

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

        kept = self._previous_views.get(area.id)

        if kept is not None and kept[0] == area.view:
            view = kept[1]
        else:
            context = ViewContext(self._requests, self._saved.get((area.id, area.view)))

            try:
                view = _checked_view(area.view, self._registered[area.view].factory(context))
            except Exception as error:
                # The failure stays in this Area, and the other Areas are still
                # built. Raised out of the chooser's menu, it would be lost and
                # leave the layout half built.
                return self._notice(
                    AreaNotice(
                        UNBUILT_VIEW_TITLE, unbuilt_view_text(area.view, error, self._registered)
                    )
                )

        self._views[area.id] = (area.view, view)

        return _widget(view)

    def _notice(self, notice: AreaNotice) -> AreaNotice:
        self._notices.append(notice)

        return notice

    def _settle(self, kept: AbstractSet[AreaId]) -> None:
        """Decide which Areas can be given their View's size, and lay every splitter out.

        `layout/sizing.py`'s `settle` decides it at this widget's size, so the
        sizes drawn are the ones it worked out (`PL-K285`). Each Area's frame
        is held at the bound it was given: its need where it draws its View,
        and its floor where it is too small, which then shows the statement
        of the size its View needs instead of the View. Before this widget is
        shown its size is not the one it is drawn at, so every Area keeps its
        View and is held at its need until then.

        Where the Views' needs add up to a new least size, the host is told,
        so a host that can grow, such as the dashboard's scrolling page, gives
        this widget room for every View (`minimumSizeHint`).
        """

        if self._settling:
            return

        self._settling = True

        try:
            tree = self._model.windows[MAIN_WINDOW].tree
            needs = {area_id: self._need(area_id) for area_id in self._frames}
            floors = {area_id: _floor(frame) for area_id, frame in self._frames.items()}
            extent = PixelSize(max(self.width(), 0), max(self.height(), 0))

            least = minimum_extent(tree, AREA_HANDLE_WIDTH, needs)

            if self.isVisible():
                fit = settle(tree, extent, AREA_HANDLE_WIDTH, needs, floors, kept)
            else:
                laid_out = apportion(tree, extent, AREA_HANDLE_WIDTH, needs)
                fit = Fit(laid_out, needs, frozenset(needs), ())

            self._fit = fit
            self._drawn = fit.drawn

            for area_id, frame in self._frames.items():
                bound = fit.bounds[area_id]
                frame.setMinimumSize(bound.width_px, bound.height_px)
                shown = self._views.get(area_id)

                if shown is None or area_id in fit.drawn:
                    frame.show_view()
                else:
                    frame.show_too_small(self._registered[shown[0]].title, self._view_need(area_id))

            for splitter in self._splitters.values():
                self._lay_out(splitter)

            if least != self._least:
                self._least = least
                self.updateGeometry()
        finally:
            self._settling = False

    def _need(self, area_id: AreaId) -> PixelSize:
        """The least size the Area `area_id` draws its View at: the View's need and the header.

        An Area that shows a notice in place of a View needs its floor alone.
        """

        frame = self._frames[area_id]

        if area_id not in self._views:
            return _floor(frame)

        view = self._view_need(area_id)

        return PixelSize(view.width_px, view.height_px + _chrome_height(frame))

    def _view_need(self, area_id: AreaId) -> PixelSize:
        """The least size the View in `area_id` is drawn at, below the Area's header.

        It is the larger, on each axis, of the minimum the View's registry
        entry declares and the least size Qt would hold the View widget to,
        which grows with what the View holds (`app/view_registry.py`).
        """

        kind, view = self._views[area_id]
        declared = self._registered[kind].minimum
        width, height = _least_size(_widget(view))

        return PixelSize(max(declared.width_px, width), max(declared.height_px, height))

    def _lay_out(self, splitter: _AreaSplitter) -> None:
        """Give `splitter`'s children the sizes the last settle worked out for its split."""

        if self._splitters.get(splitter.path) is not splitter:
            # A splitter the last rebuild replaced, resized while it waits to
            # be deleted.
            return

        sizes = None if self._fit is None else self._fit.apportionment.splits.get(splitter.path)

        if sizes is None:
            # The splitters are being built and nothing is settled yet.
            split = _split_at(self._model.windows[MAIN_WINDOW].tree, splitter.path)
            extent = (
                splitter.width()
                if splitter.orientation() == Qt.Orientation.Horizontal
                else splitter.height()
            )
            available = extent - splitter.handleWidth() * (splitter.count() - 1)
            sizes = pixel_sizes(split.sizes, max(available, len(split.sizes)))

        splitter.setSizes(list(sizes))

    def border_pressed(self, handle: _AreaHandle, offset_px: int, *, alone: bool) -> None:
        """Start a drag of the border `handle` draws, pressed `offset_px` into its width.

        The drag keeps the layout it started from, so every move is worked
        out from that layout and Escape can return to it. With `alone`, the
        reader held Shift and only this border moves, not the rest of its
        line (`LayoutModel.resize`).
        """

        self._border_drag = _BorderDrag(self._handle_of(handle), alone, self._model, offset_px)
        self._at_minimum = False
        self._relight()

    def border_moved(self, handle: _AreaHandle, at: QPoint) -> None:
        """Move the dragged border toward `at`, on the screen, and re-lay out the Areas now.

        `PL-RQT1` Q3 decided it. The Areas follow the pointer live. The
        border goes no further than the place where an Area beside a moved
        line reaches the least size it can be drawn at. Past that place the
        border stops and its line turns WARNING. A move the model refuses
        stops the same way.
        """

        drag = self._border_drag

        if drag is None:
            return

        position = self._position_at(handle, drag, at)

        if position is None:
            return

        moved, self._at_minimum = self._farthest(drag, position)
        self._resized(moved)

    def border_released(self) -> None:
        """End the border drag where it is."""

        self._border_drag = None
        self._at_minimum = False
        self._relight()

    def border_cancelled(self) -> None:
        """End the border drag and return to the layout it started from, as Escape does."""

        drag = self._border_drag

        if drag is None:
            return

        self._border_drag = None
        self._at_minimum = False
        self._resized(drag.start)

    def _resized(self, moved: LayoutModel) -> None:
        """Give the splitters `moved`'s sizes, and say so if it is a new layout.

        A drag changes only sizes, so the splitters are kept and set again
        rather than rebuilt.
        """

        changed = moved != self._model
        self._model = moved
        self._settle(self._drawn)
        self._relight()

        if changed:
            self.layout_changed.emit(moved)

    def _handle_of(self, handle: _AreaHandle) -> Handle:
        """The model's address of the border `handle` draws.

        Qt numbers a splitter's handles from 1, each before the child of the
        same index, and `Handle.index` counts the gaps from 0.
        """

        splitter = handle.owner
        index = next(
            index for index in range(1, splitter.count()) if splitter.handle(index) is handle
        )

        return Handle(MAIN_WINDOW, splitter.path, index - 1)

    def _position_at(self, handle: _AreaHandle, drag: _BorderDrag, at: QPoint) -> float | None:
        """Where in the window the dragged border lies with the pointer at `at`, on the screen.

        The splitter places a handle's leading edge after the children before
        it and the handles between them. So the share of the split before the
        border is that edge, less those handles, over the splitter's width
        less all its handles. The model's span of the split turns the share
        into a fraction of the window. None when the splitter has no width.
        """

        splitter = handle.owner
        index = drag.handle.index + 1
        local = splitter.mapFromGlobal(at)
        horizontal = splitter.orientation() == Qt.Orientation.Horizontal
        edge = (local.x() if horizontal else local.y()) - drag.offset_px
        extent = splitter.width() if horizontal else splitter.height()
        total = extent - splitter.handleWidth() * (splitter.count() - 1)

        if total <= 0:
            return None

        low, high = drag.start.span(drag.handle)
        share = (edge - splitter.handleWidth() * (index - 1)) / total

        return low + (high - low) * share

    def _farthest(self, drag: _BorderDrag, position: float) -> tuple[LayoutModel, bool]:
        """The layout with the border as near `position` as it can go, and whether it stopped.

        The border moves to `position` when the model allows it and every
        Area still fits (`_fits`). Otherwise the place where it stops lies
        between where the drag started and `position`, and is found by
        halving that interval `_BORDER_BISECTIONS` times. Every candidate is
        worked out from the layout the drag started from, so a drag's result
        depends only on where the pointer is, not on the path it took.
        """

        def attempt(at: float) -> LayoutModel | None:
            try:
                moved = drag.start.resize(drag.handle, at, alone=drag.alone)
            except LayoutRefused:
                return None

            return moved if self._fits(drag.start, moved) else None

        reached = attempt(position)

        if reached is not None:
            return reached, False

        near, far = drag.start.position(drag.handle), position
        best = drag.start

        for _ in range(_BORDER_BISECTIONS):
            middle = (near + far) / 2
            candidate = attempt(middle)

            if candidate is None:
                far = middle
            else:
                near, best = middle, candidate

        return best, True

    def _fits(self, start: LayoutModel, moved: LayoutModel) -> bool:
        """Whether every Area of `moved` is drawn at least at the least size it can take.

        An Area's least size is what Qt would hold it to anyway: its frame's
        minimum size, or its minimum size hint where none is set. Its drawn
        size is its share of this widget less one handle's width, which
        never overstates it. An Area that was already smaller than its least
        size when the drag started, because the window is small, may stay as
        it was but may not shrink further.
        """

        width, height = self.width(), self.height()

        def drawn(model: LayoutModel, area_id: AreaId) -> tuple[float, float]:
            place = model.rectangle(area_id)

            return (
                (place.right - place.left) * width - AREA_HANDLE_WIDTH,
                (place.bottom - place.top) * height - AREA_HANDLE_WIDTH,
            )

        for area in moved.areas():
            least = _least_size(self._frames[area.id])
            now, then = drawn(moved, area.id), drawn(start, area.id)

            if any(now[axis] < min(least[axis], then[axis]) for axis in (0, 1)):
                return False

        return True

    def _hover(self, handle: _AreaHandle | None) -> None:
        """Mark the handles a drag of `handle` would move, or none when the pointer left."""

        self._hovered = handle
        self._relight()

    def _relight(self) -> None:
        """Light every handle a drag moves, or would move, and only those.

        During a drag these are the handles it moves: the dragged one alone
        with Shift, and its whole line otherwise, read from the layout the
        drag started from. They are lit in WARNING while the drag is stopped
        at a minimum. With no drag, they are the handles on the hovered
        handle's line.
        """

        members: tuple[Handle, ...] = ()
        drag = self._border_drag
        hovered = self._hovered

        if drag is not None:
            members = (drag.handle,) if drag.alone else drag.start.borders(drag.handle)
        elif hovered is not None and self._splitters.get(hovered.owner.path) is hovered.owner:
            members = self._model.borders(self._handle_of(hovered))

        lit = [self._splitters[member.path].handle(member.index + 1) for member in members]
        warning = drag is not None and self._at_minimum

        for splitter in self._splitters.values():
            for index in range(1, splitter.count()):
                handle = splitter.handle(index)

                if isinstance(handle, _AreaHandle):
                    shown = any(handle is member for member in lit)
                    handle.set_lit(shown, warning=shown and warning)


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


class AreaMenu(QToolButton):
    """The last control of an Area's header: the operations on the Area's place.

    `PL-MS34` Q2 placed it, a flat button labelled "Area" with a chevron, and
    `PL-2KXB` fills it. Its menu holds the two splits, a "Join with" submenu,
    a "Swap with" submenu and Close Area. The entries are worked out each
    time the menu opens, from the layout drawn then. An unavailable entry is
    shown, disabled, with the reason as its tooltip, so the reader sees an
    operation the layout cannot make rather than not finding it. The button
    has the chooser's look and keyboard reach.

    Args:
        area_id: The Area whose header holds this menu.
        operations: Gives the Area's entries, as `AreaLayout.operations` does.
        perform: Draws the layout an available entry makes.
    """

    def __init__(
        self,
        area_id: AreaId,
        operations: Callable[[AreaId], tuple[AreaOperation, ...]],
        perform: Callable[[AreaOperation], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("areaMenu")
        self.area_id = area_id
        self._operations = operations
        self._perform = perform
        self.setText(AREA_MENU_LABEL)
        self.setAccessibleDescription("Split, join, swap or close this Area")
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
        """Write the menu's entries from the layout drawn now."""

        menu = self.menu()
        menu.clear()
        submenus: dict[str, QMenu] = {}

        for operation in self._operations(self.area_id):
            holder = menu

            if operation.group is not None:
                if operation.group not in submenus:
                    submenu = menu.addMenu(operation.group)
                    submenu.setStyleSheet(menu_stylesheet())
                    submenu.setToolTipsVisible(True)
                    submenus[operation.group] = submenu

                holder = submenus[operation.group]

            action = holder.addAction(operation.label)
            action.setEnabled(operation.available)
            action.setToolTip(operation.refusal)
            action.triggered.connect(partial(self._perform, operation))

        for group in (JOIN_WITH_LABEL, SWAP_WITH_LABEL):
            if group not in submenus:
                # No Area to join with or to swap with: the submenu is shown,
                # unavailable, rather than left out.
                empty = menu.addMenu(group)
                empty.setEnabled(False)
                empty.menuAction().setToolTip(_ONLY_AREA_TEXT)


class AreaFrame(QFrame):
    """One Area as drawn: its header, a rule, and its View or notice filling the rest.

    `PL-MS34` decided the header. It is one text row, as tall as the chooser
    in it, on the panel surface, with a 1px `GRIDLINE` rule under it. The
    chooser is its first control, a stretch follows it, and the Area menu
    ends it (`PL-2KXB`). While the Workspace is pinned to a run, the run's
    name follows the chooser, because `docs/MODEL.md` asks a View to name its
    run while it is pinned to one (`PL-7Z84`). The header never gets shorter
    than its row.

    **An Area of a Workspace whose pinned run is not open shows a notice in
    place of its View** (`PL-WV9K` Q6). The View is hidden, not deleted, and
    no other run is shown in its place. That notice takes precedence over the
    too-small one.

    **An Area too small for its View shows a notice in its place** (`PL-K285`,
    `PL-DB5G` Q3). The View is hidden, not deleted, so it keeps its state and
    is shown again once the Area can be given its size. The notice states the
    size the View needs and the size the Area has under its header, and it is
    restated whenever the Area is resized, so the reader dragging a border
    sees it clear the moment the size is enough. It shows no value from any
    run.

    Attributes:
        area_id: The Area this frame draws.
        header: The header row.
        chooser: The View chooser in the header.
        menu: The Area menu at the end of the header, or None where the
            caller gave none.
        content: The View or the notice under the header.
        too_small_notice: The notice shown in place of the View while the
            Area is too small for it, or None where it has never been.
        pin_label: The pinned run's name in the header, hidden while the
            Workspace pins no run.
        absent_notice: The notice shown in place of the View while the
            pinned run is not open, or None where it has never been.
    """

    def __init__(
        self,
        area_id: AreaId,
        chooser: ViewChooser,
        content: QWidget,
        parent: QWidget | None = None,
        *,
        menu: AreaMenu | None = None,
        drags: AreaLayout | None = None,
    ) -> None:
        super().__init__(parent)
        self.area_id = area_id
        self.chooser = chooser
        self.menu = menu
        self.content = content

        self.header = QWidget()
        self.header.setObjectName("areaHeader")
        self.header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.header.setStyleSheet(panel_stylesheet(self.header.objectName()))
        # The header asks for no width: what an Area needs is its View's
        # minimum, so a narrow Area clips the title rather than being held
        # wider than its View needs.
        self.header.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        row = QHBoxLayout(self.header)
        row.setContentsMargins(_HEADER_MARGIN_PX, 0, _HEADER_MARGIN_PX, 0)
        row.addWidget(chooser)
        self.pin_label = styled_label("", color=INK, size_px=METRIC_NAME_SIZE)
        self.pin_label.hide()
        row.addWidget(self.pin_label)
        row.addStretch(1)

        if menu is not None:
            row.addWidget(menu)

        rule = QFrame()
        rule.setFrameShape(QFrame.Shape.HLine)
        rule.setFixedHeight(_HEADER_RULE_PX)
        rule.setStyleSheet(foreground_stylesheet(GRIDLINE))

        self._column = QVBoxLayout(self)
        self._column.setContentsMargins(0, 0, 0, 0)
        self._column.setSpacing(0)
        self._column.addWidget(self.header)
        self._column.addWidget(rule)
        self._column.addWidget(content, 1)
        # A View handed back unparented by an earlier layout was hidden when
        # it lost its parent, and a layout does not show it again by itself.
        content.show()
        self.too_small_notice: AreaNotice | None = None
        self._needed: PixelSize | None = None
        self.absent_notice: AreaNotice | None = None
        self._absent = False

        self.corners: tuple[_CornerZone, ...] = ()

        if drags is not None:
            self.corners = tuple(_CornerZone(self, drags, corner) for corner in _Corner)

    def show_view(self) -> None:
        """Show the View or notice under the header, in place of the too-small notice."""

        self._needed = None

        if self.too_small_notice is not None:
            self.too_small_notice.hide()

        self.content.setHidden(self._absent)

    def show_too_small(self, title: str, needed: PixelSize) -> None:
        """Hide the View, and state that it needs `needed` under the header, which it lacks.

        Args:
            title: The View's title, as the chooser names it.
            needed: The least size the View is drawn at, below the header.
        """

        notice = self.too_small_notice

        if notice is None:
            notice = AreaNotice(too_small_title(title), "")
            self.too_small_notice = notice
            self._column.addWidget(notice, 1)
        else:
            notice.title_label.setText(too_small_title(title))

        self._needed = needed
        self.content.hide()
        notice.setHidden(self._absent)
        self._restate()

    def show_pin(self, run_name: str | None, *, absent: bool) -> None:
        """Name the pinned run in the header, and state in place of the View whether it is absent.

        Args:
            run_name: The pinned run's name, or None where the Workspace pins
                no run.
            absent: Whether the pinned run is not open. Only a pinned run can
                be absent.
        """

        self.pin_label.setText(run_name or "")
        self.pin_label.setVisible(run_name is not None)
        self._absent = absent and run_name is not None
        notice = self.absent_notice

        if self._absent and run_name is not None:
            if notice is None:
                notice = AreaNotice("", "")
                self.absent_notice = notice
                self._column.addWidget(notice, 1)

            notice.title_label.setText(pinned_run_absent_title(run_name))
            notice.body_label.setText(pinned_run_absent_text(run_name))
            notice.show()
        elif notice is not None:
            notice.hide()

        self.content.setHidden(self._absent or self._needed is not None)

        if self.too_small_notice is not None:
            self.too_small_notice.setHidden(self._absent or self._needed is None)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._restate()

        for zone in self.corners:
            zone.place()

    def _restate(self) -> None:
        """Write the too-small notice's body from the size the Area has now under its header."""

        notice, needed = self.too_small_notice, self._needed

        if notice is None or needed is None:
            return

        has = PixelSize(max(self.width(), 0), max(self.height() - _chrome_height(self), 0))
        notice.body_label.setText(too_small_text(needed, has))

    def enterEvent(self, event: QEnterEvent) -> None:
        super().enterEvent(event)
        self._show_grips(True)

    def leaveEvent(self, event: QEvent) -> None:
        super().leaveEvent(event)
        self._show_grips(False)

    def _show_grips(self, shown: bool) -> None:
        """Draw the corners' grips while the pointer is in this Area, and only then.

        `PL-30L5` Q1 decided it: an Area being handled shows its corners
        work, and an Area being read shows nothing.
        """

        for zone in self.corners:
            zone.set_grip_shown(shown)


class AreaNotice(QFrame):
    """What an Area shows in place of a View it cannot draw: a title and a body, and nothing else.

    `PL-DB5G` decided one notice for every state in which an Area shows no
    View, so a reader learns its shape once (project owner, 2026-10-11,
    ratified). The title is bold, in `WARNING`, and the body is regular, in
    `INK`, both at `METRIC_NAME_SIZE` and wrapped to the Area's width. They sit
    at the top left of the panel surface, inset by `PANEL_PADDING`. The notice
    has no fill colour of its own, no border and no icon, and it never shows a
    value from a run, since a plausible number in a failure state could be read
    as a View's. Three states are built so far: an unknown View kind, a View
    whose factory failed, and an Area too small for its View (`PL-K285`).

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


# How many times a stopped border drag halves the interval where it stops.
# Twenty halvings place the border to a millionth of its split's span, finer
# than a pixel on any screen.
_BORDER_BISECTIONS: Final = 20


@dataclass(frozen=True)
class _BorderDrag:
    """A border drag in progress: the border, whether it moves alone, and where it began."""

    handle: Handle
    alone: bool
    start: LayoutModel
    offset_px: int


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

    A press starts a drag that `AreaLayout` works out (`border_moved`), with
    Shift held to move this handle alone. The line turns `WARNING` while the
    drag is stopped at a minimum, and Escape returns the layout to where the
    drag started (`PL-RQT1` Q3).
    """

    def __init__(self, splitter: _AreaSplitter) -> None:
        super().__init__(splitter.orientation(), splitter)
        self.owner = splitter
        self._lit = False
        self._warning = False
        self._pressed = False
        # Escape reaches the handle only while it has the keyboard focus,
        # which a press gives it. It is not in the tab order.
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    @property
    def lit(self) -> bool:
        """Whether the line is drawn: the pointer is over this handle or one on its line."""

        return self._lit

    @property
    def warning(self) -> bool:
        """Whether the line is drawn in WARNING: a drag of it has stopped at a minimum."""

        return self._warning

    def set_lit(self, lit: bool, *, warning: bool = False) -> None:
        if (lit, warning) != (self._lit, self._warning):
            self._lit, self._warning = lit, warning
            self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Start a drag. Qt's own drag is not used, so the model decides where the border stops."""

        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        pressed = event.position().toPoint()
        horizontal = self.orientation() == Qt.Orientation.Horizontal
        self._pressed = True
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        self.owner.layout_owner.border_pressed(
            self,
            pressed.x() if horizontal else pressed.y(),
            alone=bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier),
        )
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not self._pressed:
            super().mouseMoveEvent(event)
            return

        self.owner.layout_owner.border_moved(self, event.globalPosition().toPoint())
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if not self._pressed or event.button() != Qt.MouseButton.LeftButton:
            super().mouseReleaseEvent(event)
            return

        self._pressed = False
        self.owner.layout_owner.border_released()
        event.accept()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if self._pressed and event.key() == Qt.Key.Key_Escape:
            self._pressed = False
            self.owner.layout_owner.border_cancelled()
            event.accept()
            return

        super().keyPressEvent(event)

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
        painter.fillRect(line, QColor(WARNING if self._warning else PRIMARY))
        painter.end()


class _Corner(Enum):
    """One of an Area's four corners, by which sides of the Area it lies on."""

    TOP_LEFT = (False, False)
    TOP_RIGHT = (True, False)
    BOTTOM_LEFT = (False, True)
    BOTTOM_RIGHT = (True, True)

    @property
    def right(self) -> bool:
        return self.value[0]

    @property
    def bottom(self) -> bool:
        return self.value[1]


class _CornerZone(QWidget):
    """A corner of an Area that a reader drags to split or join it (`PL-30L5` Q1).

    It is an `AREA_CORNER_ZONE` square inside the corner, above the View, with
    the platform's cross cursor. It draws a grip of three short strokes in
    MUTED while the pointer is in its Area, and nothing otherwise. A press
    starts a drag that `AreaLayout` previews and makes on release, and Escape
    during the drag cancels it.
    """

    def __init__(self, frame: AreaFrame, drags: AreaLayout, corner: _Corner) -> None:
        super().__init__(frame)
        self.frame = frame
        self.corner = corner
        self._drags = drags
        self._grip_shown = False
        self.setFixedSize(AREA_CORNER_ZONE, AREA_CORNER_ZONE)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.place()
        self.raise_()

    @property
    def grip_shown(self) -> bool:
        return self._grip_shown

    def set_grip_shown(self, shown: bool) -> None:
        if shown != self._grip_shown:
            self._grip_shown = shown
            self.update()

    def place(self) -> None:
        """Move to this zone's corner of the frame."""

        x = self.frame.width() - AREA_CORNER_ZONE if self.corner.right else 0
        y = self.frame.height() - AREA_CORNER_ZONE if self.corner.bottom else 0
        self.move(x, y)
        self.raise_()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.setFocus()
            self._drags.corner_pressed(self.frame.area_id, event.globalPosition().toPoint())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self._drags.corner_moved(event.globalPosition().toPoint())

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drags.corner_released(event.globalPosition().toPoint())

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self._drags.corner_cancelled()
        else:
            super().keyPressEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        if not self._grip_shown:
            return

        painter = QPainter(self)
        painter.setPen(QPen(QColor(MUTED), AREA_GRIP_STROKE_WIDTH))
        # Diagonal strokes across the corner, the nearest the shortest.
        for step in range(1, AREA_GRIP_STROKES + 1):
            reach = step * AREA_GRIP_STROKE_LENGTH // 2
            start = QPoint(reach, 0)
            end = QPoint(0, reach)

            if self.corner.right:
                start.setX(AREA_CORNER_ZONE - 1 - start.x())
                end.setX(AREA_CORNER_ZONE - 1 - end.x())

            if self.corner.bottom:
                start.setY(AREA_CORNER_ZONE - 1 - start.y())
                end.setY(AREA_CORNER_ZONE - 1 - end.y())

            painter.drawLine(start, end)

        painter.end()


class _LayoutOverlay(QWidget):
    """What a corner drag shows before it is released, drawn over the Areas (`PL-30L5` Q2).

    A split draws a line across the Area where the cut will fall, in PRIMARY,
    or in WARNING where a part would be too small to hold its header. A join
    tints the Area that will close in MUTED and outlines the Area the two
    will make in PRIMARY. A join the layout cannot make outlines the Area
    under the pointer in WARNING, with no tint. The overlay takes no mouse
    events, so the Areas under it work as usual.
    """

    def __init__(self, layout: AreaLayout) -> None:
        super().__init__(layout)
        self._layout = layout
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setGeometry(layout.rect())

    def paintEvent(self, event: QPaintEvent) -> None:
        preview = self._layout.preview

        if preview is None:
            return

        painter = QPainter(self)

        if isinstance(preview, SplitPreview):
            own = self._layout.frame_rect(preview.area_id)
            colour = QColor(PRIMARY if preview.result is not None else WARNING)

            if preview.orientation is Orientation.ROW:
                x = own.left() + round(preview.at * own.width()) - AREA_PREVIEW_LINE_WIDTH // 2
                line = QRect(x, own.top(), AREA_PREVIEW_LINE_WIDTH, own.height())
            else:
                y = own.top() + round(preview.at * own.height()) - AREA_PREVIEW_LINE_WIDTH // 2
                line = QRect(own.left(), y, own.width(), AREA_PREVIEW_LINE_WIDTH)

            painter.fillRect(line, colour)
        else:
            closing = self._layout.frame_rect(preview.remove)

            if preview.result is None:
                _outline(painter, closing, WARNING)
            else:
                tint = QColor(MUTED)
                tint.setAlphaF(AREA_CLOSING_TINT_ALPHA)
                painter.fillRect(closing, tint)
                _outline(painter, closing.united(self._layout.frame_rect(preview.keep)), PRIMARY)

        painter.end()


def _outline(painter: QPainter, rect: QRect, colour: str) -> None:
    """Draw `rect`'s edge, `AREA_PREVIEW_LINE_WIDTH` thick and inside it, in `colour`."""

    width = AREA_PREVIEW_LINE_WIDTH
    fill = QColor(colour)
    painter.fillRect(QRect(rect.left(), rect.top(), rect.width(), width), fill)
    painter.fillRect(QRect(rect.left(), rect.bottom() - width + 1, rect.width(), width), fill)
    painter.fillRect(QRect(rect.left(), rect.top(), width, rect.height()), fill)
    painter.fillRect(QRect(rect.right() - width + 1, rect.top(), width, rect.height()), fill)


def _checked_view(kind: ViewKind, view: object) -> View:
    """Return `view` once it is checked to be a `QWidget` that satisfies the View contract.

    Raises:
        TypeError: The factory for `kind` returned something else. A View
            that could not be drawn or refreshed would leave its Area showing
            whatever it drew last, or nothing, as if that were current.
    """

    if not isinstance(view, QWidget) or not isinstance(view, View):
        raise TypeError(
            f"the factory for the View kind {kind!r} returned a {type(view).__name__}, which "
            "is not a QWidget that satisfies the View contract"
        )

    return view


def _widget(view: View) -> QWidget:
    """`view` as the widget it is: `_checked_view` admitted only a `QWidget`."""

    return cast(QWidget, view)


def _flattened(
    states: Mapping[AreaId, Mapping[ViewKind, SavedState]],
) -> dict[tuple[AreaId, ViewKind], SavedState]:
    """A Workspace's View states, keyed by Area and kind as the adapter keeps them."""

    return {
        (area_id, kind): state for area_id, kinds in states.items() for kind, state in kinds.items()
    }


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


def _attempt(label: str, group: str | None, operation: Callable[[], LayoutModel]) -> AreaOperation:
    """The entry for an operation the model may refuse, with the layout it makes if it does not."""

    try:
        return AreaOperation(label, group, operation())
    except LayoutRefused:
        return AreaOperation(label, group, None, _NOT_EXPRESSIBLE_TEXT)


def _relative_place(own: Rectangle, other: Rectangle) -> str:
    """Where `other` lies from `own`, in the words a menu entry uses, from their centres."""

    across = (other.left + other.right) / 2 - (own.left + own.right) / 2
    down = (other.top + other.bottom) / 2 - (own.top + own.bottom) / 2
    words = []

    if down < 0:
        words.append(_SIDE_WORDS[Side.ABOVE])
    elif down > 0:
        words.append(_SIDE_WORDS[Side.BELOW])

    if across < 0:
        words.append(_SIDE_WORDS[Side.LEFT])
    elif across > 0:
        words.append(_SIDE_WORDS[Side.RIGHT])

    return ", ".join(words)


def _least_size(widget: QWidget) -> tuple[int, int]:
    """The width and height Qt holds `widget` to in a splitter that does not collapse its children.

    That is the widget's minimum size where one is set, and its minimum size
    hint otherwise, on each axis.
    """

    hint = widget.minimumSizeHint()

    return (widget.minimumWidth() or hint.width(), widget.minimumHeight() or hint.height())


def _structural_minimum(frame: AreaFrame) -> tuple[int, int]:
    """The least width and height an Area can be drawn at: its header, and one line of a notice.

    `PL-30L5` Q2 set it. Below it a half could not hold its own header row
    and the first line of `PL-DB5G`'s notice, so a split is refused there. A
    half too small for the View it shows is allowed, and that is `PL-K285`'s
    statement to make.
    """

    title_font = QFont(frame.font())
    title_font.setPixelSize(METRIC_NAME_SIZE)
    title_font.setBold(True)
    line = QFontMetrics(title_font).lineSpacing()
    header = frame.header.sizeHint()
    controls = frame.chooser.sizeHint().width() + (
        0 if frame.menu is None else frame.menu.sizeHint().width()
    )

    return (
        controls + 2 * _HEADER_MARGIN_PX,
        header.height() + _HEADER_RULE_PX + PANEL_PADDING + line,
    )


def _floor(frame: AreaFrame) -> PixelSize:
    """The least size an Area too small for its View is held at: `_structural_minimum`."""

    return PixelSize(*_structural_minimum(frame))


def _chrome_height(frame: AreaFrame) -> int:
    """How much of an Area's height its header and the rule under it take."""

    return frame.header.sizeHint().height() + _HEADER_RULE_PX


def _same_place(first: Rectangle, second: Rectangle) -> bool:
    """Whether two rectangles of an Area are one place, to within the model's rounding."""

    return first.window == second.window and all(
        math.isclose(one, other, abs_tol=BORDER_ALIGNMENT_TOLERANCE)
        for one, other in (
            (first.left, second.left),
            (first.top, second.top),
            (first.right, second.right),
            (first.bottom, second.bottom),
        )
    )


def _split_layout(model: LayoutModel, area_id: AreaId, orientation: Orientation) -> LayoutModel:
    """The layout a split from the menu makes: the Area cut halfway across."""

    return model.split(area_id, orientation, _MENU_SPLIT_AT)[0]
