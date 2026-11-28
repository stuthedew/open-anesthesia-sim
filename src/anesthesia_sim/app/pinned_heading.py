"""A heading that stays in view while any part of its section is, as a View scrolls in its Area.

An Area scrolls a View that is taller than it (`ViewScroll` in
`app/area_layout.py`). A heading that says whose values the rows under it
show, such as the run that a schematic's tensions belong to, could then scroll
out of view while those rows stay in view. A reader would see values with
nothing to say whose they are (`PL-3NGZ`). A `PinnedHeadingSection` keeps its
heading at the top of the part of the section that is in view. This is how a
list's section headers stay pinned while the list scrolls (Apple, SwiftUI
documentation, "Grouping data with lazy stack views", section "Keep important
information visible", read 2026-11-27).

The heading is drawn over the section's rows, on the panel's colour, so the
part of a row under it is hidden. No row can be seen without the heading,
though a row that stands across the heading's lower edge shows in part. A row
whose cut part could be misread, such as a filled container or a line of
digits, reads `clear_of_heading` and draws only what that part holds whole
(`PL-GWTR`).

Every box that scrolls a section moves the heading again after each scroll,
and after each change of what it can scroll (`pin_on_scroll`). That includes
the dashboard's page, which scrolls every Area in a window too small for
them.

Sections nest. Each Area's header and the row its View keeps above its scroll
box are the heading of a section that holds the View (`AreaFrame` in
`app/area_layout.py`). So while the page carries an Area's top above the
window's edge, the header and the row stand at the top of the Area's part in
view, over the View's top (`PL-DKQ5`). A heading inside the View then stands
under them, because the part of a widget in view leaves out what any heading
around it covers (`in_view`). NUREG-0700 Rev. 3 (U.S. Nuclear Regulatory
Commission, 2020), guideline 1.5-15, p. 1-59, asks for this: "General labels
and row and column labels should remain along the top (or bottom) and left (or
right) edges of the display." So a heading's general label, such as a run's
name, also starts at the left edge of the part in view while the page is
scrolled sideways (`follows_left`, `slides_left`). Its column labels stay over
their columns.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, Qt
from PySide6.QtGui import QMoveEvent, QResizeEvent, QShowEvent
from PySide6.QtWidgets import QAbstractScrollArea, QBoxLayout, QScrollArea, QVBoxLayout, QWidget

from anesthesia_sim.app.stylesheets import heading_surface_stylesheet

__all__ = [
    "HeadingScroll",
    "PinnedHeadingSection",
    "in_view",
    "pin_headings",
    "pin_on_scroll",
    "scroll_clear_into_view",
]

# How far inside a box's edge, below any heading, a widget that takes the
# keyboard focus is scrolled to. It is the margin Qt's own scroll box keeps
# (`QScrollArea.ensureWidgetVisible`, whose margins default to 50 px).
_FOCUS_MARGIN_PX = 50


def in_view(widget: QWidget) -> QRect:
    """Return the part of `widget` that its ancestors leave in view, in the widget's own pixels.

    Each ancestor clips what it holds to its own rectangle, so a widget inside
    a box that scrolls is in view only where it lies within the box's
    viewport. A `PinnedHeadingSection` around the widget also covers the
    widget's part above its heading's lower edge, unless the widget is in
    that heading. The result leaves that part out, so it is the part a reader
    can see. The result is empty for a widget that is not visible. Only the
    ancestors' geometry is read, which is what Qt reads to clip a widget's
    painting. Each heading's place is worked out from that geometry too, so
    the result does not depend on which heading was moved last.
    """

    if not widget.isVisible():
        return QRect()

    shown = widget.rect()
    ancestor = widget.parentWidget()

    while ancestor is not None and not shown.isEmpty():
        shown = shown.intersected(QRect(widget.mapFrom(ancestor, QPoint(0, 0)), ancestor.size()))

        if isinstance(ancestor, PinnedHeadingSection) and not ancestor.heading.isAncestorOf(widget):
            covered_bottom = ancestor.heading_place().bottom() + 1
            shown.setTop(max(shown.top(), widget.mapFrom(ancestor, QPoint(0, covered_bottom)).y()))

        ancestor = ancestor.parentWidget()

    return shown if shown.height() > 0 and shown.width() > 0 else QRect()


def pin_headings(root: QWidget) -> None:
    """Move the heading of every `PinnedHeadingSection` under `root` to the top of its part in view.

    A box that scrolls its widget calls this after each scroll and each
    resize, because a scroll moves the widget it holds and leaves each section
    where it is inside that widget. So no section learns of a scroll by
    itself. `ViewScroll` calls it on a resize, and `pin_on_scroll` on a
    scroll or a change of what a box can scroll.
    """

    for section in root.findChildren(PinnedHeadingSection):
        section.pin_heading()


def pin_on_scroll(box: QScrollArea) -> None:
    """Move the headings in the widget `box` scrolls after each scroll and each change of range.

    A box moves the widget it holds when its scroll bar moves. Qt connects
    the bar to that move when the box is built, so the move has happened by
    the time this connection runs. A box's range changes when its viewport
    grows or shrinks, which brings part of the widget into view, or takes it
    out, with no scroll at all. A taller window does this to the dashboard's
    page, so a section out of view can come back into view with its heading
    still where it was put while the section was out of view. `ViewScroll`
    and the dashboard's page call this, so a heading follows its Area and the
    page alike.
    """

    def pin() -> None:
        held = box.widget()

        if held is not None:
            pin_headings(held)

    def after_scroll(_: int) -> None:
        pin()

    def after_range(_minimum: int, _maximum: int) -> None:
        pin()

    for bar in (box.verticalScrollBar(), box.horizontalScrollBar()):
        bar.valueChanged.connect(after_scroll)
        bar.rangeChanged.connect(after_range)


def scroll_clear_into_view(box: QScrollArea, widget: QWidget, margin: int = 0) -> None:
    """Scroll `box` as little as it takes to show `widget` whole and clear of every heading.

    `widget` is in the widget that `box` scrolls. A heading around `widget`
    stands over the top of the part in view once its section's top has
    scrolled out of view (`PinnedHeadingSection`). So `widget` is scrolled to
    stand at least that heading's height below the box's top, where no
    heading covers it. Qt's `ensureWidgetVisible` would put `widget` at the
    box's top edge, under the headings. Up to `margin` pixels more are kept
    clear on each side, as Qt keeps 50 for a widget that takes the keyboard
    focus, where the box has room for them.
    Where `widget` is already in view and clear, nothing moves. Where it is
    taller than the box can show, its top is shown.
    """

    held = box.widget()

    if held is None or not held.isAncestorOf(widget):
        return

    corner = widget.mapTo(held, QPoint(0, 0))
    covered = 0
    ancestor = widget.parentWidget()

    while ancestor is not None and ancestor is not held:
        if isinstance(ancestor, PinnedHeadingSection) and not ancestor.heading.isAncestorOf(widget):
            covered += ancestor.heading.sizeHint().height()

        ancestor = ancestor.parentWidget()

    viewport = box.viewport().size()

    for bar, start, length, room, lead in (
        (box.horizontalScrollBar(), corner.x(), widget.width(), viewport.width(), 0),
        (box.verticalScrollBar(), corner.y(), widget.height(), viewport.height(), covered),
    ):
        position = bar.value()
        # A box too short for the margins keeps only what room it has left
        # on each side, so the widget is never scrolled out of view for them.
        kept = min(margin, max((room - lead - length) // 2, 0))

        if start + length + kept > position + room:
            position = start + length + kept - room

        if start - lead - kept < position:
            position = start - lead - kept

        bar.setValue(position)


class HeadingScroll(QScrollArea):
    """A scroll box that brings a widget taking the keyboard focus into view clear of the headings.

    Qt's own box scrolls a widget that Tab or Shift+Tab gives the focus to
    until it stands 50 px inside the box's edge. A heading pinned over the top
    of the part in view can be taller than that, so the widget could take the
    focus under it, with its focus ring hidden (`PL-DKQ5`). This box keeps
    the same 50 px below the headings instead (`scroll_clear_into_view`).

    One box can hold another, as the page holds each Area's View. Qt asks the
    box nearest the focused widget first, and that box asks the box around it
    before it scrolls. So the outer box would scroll first, to where the
    widget stood before the inner box moved it. The outermost box therefore
    scrolls every box around the widget, from the innermost out, and the
    boxes inside it leave the scroll to it.
    """

    def focusNextPrevChild(self, next: bool) -> bool:  # Qt spells this in camelCase.
        # The scroll area's base class moves the focus without scrolling, so
        # the scrolls below are the only ones.
        moved = QAbstractScrollArea.focusNextPrevChild(self, next)
        focused = self.focusWidget()

        if moved and focused is not None and _boxes_around(self) == []:
            for box in _boxes_around(focused):
                scroll_clear_into_view(box, focused, _FOCUS_MARGIN_PX)

        return moved


def _boxes_around(widget: QWidget) -> list[HeadingScroll]:
    """Return each `HeadingScroll` that holds `widget`, from the innermost out."""

    boxes: list[HeadingScroll] = []
    holder = widget.parentWidget()

    while holder is not None:
        if isinstance(holder, HeadingScroll):
            boxes.append(holder)

        holder = holder.parentWidget()

    return boxes


class PinnedHeadingSection(QWidget):
    """A column of rows under a heading that stays at the top of the column's part in view.

    The heading is laid over the column, not in it. Above the column is an
    empty space as tall as the heading, with no spacing between the two. So
    with the whole section in view, the heading stands where a heading laid
    above the column would, and the heading's own lower margin is the gap
    between it and the first row. Once the
    section's top has scrolled out of view, the heading stands at the top of
    the part still in view. When that part is shorter than the heading, the
    heading moves up with the section's lower edge. It then never covers the
    section below.

    Args:
        heading: The heading. The section takes it as its child.
        object_name: The heading's object name, which scopes its surface's
            stylesheet to it.
        follows_left: A layout in the heading that holds the heading's general
            label, or None. While the section's left part is out of view, this
            layout's left margin grows by that part's width, so the label
            starts at the left edge of the part in view. The heading's other
            rows, such as column labels, stay over their columns.
        slides_left: Whether the whole heading moves right by the width of
            the section's part out of view on the left, so every line of it
            starts at the left edge of the part in view. A heading whose
            every line is a general label, such as an Area's header and
            pinned row, slides.
        surface_at_home: Whether the heading is drawn on the panel's colour
            while it stands in its own space, above the column and at its left
            end. A heading whose own rows draw their surfaces passes False, so
            it looks the same as a heading laid out above the column until it
            moves over the rows.

    Attributes:
        heading: The heading.
        column: The layout that the section's rows go in, under the
            heading's space. A subclass sets its spacing.
    """

    def __init__(
        self,
        heading: QWidget,
        object_name: str,
        *,
        follows_left: QBoxLayout | None = None,
        slides_left: bool = False,
        surface_at_home: bool = True,
    ) -> None:
        super().__init__()
        self.heading = heading
        heading.setParent(self)
        heading.setObjectName(object_name)
        heading.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._surface_at_home = surface_at_home
        self._surface_drawn = surface_at_home
        heading.setStyleSheet(heading_surface_stylesheet(object_name, drawn=surface_at_home))
        self._follows_left = follows_left
        self._slides_left = slides_left
        self._left_margin = 0 if follows_left is None else follows_left.contentsMargins().left()
        self._inset = 0
        self._room = QWidget()
        self._room.setFixedHeight(heading.sizeHint().height())
        self._room.setMinimumWidth(heading.minimumSizeHint().width())
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self._room)
        self.column = QVBoxLayout()
        self.column.setContentsMargins(0, 0, 0, 0)
        outer.addLayout(self.column)
        # A row of the heading shown, hidden or changed in size changes the
        # heading's height, and only the heading learns of it.
        heading.installEventFilter(self)

    def clear_of_heading(self, row: QWidget) -> QRect:
        """Return the part of `row` that is in view and not under the heading, in `row`'s pixels.

        `row` is a widget in this section's column. The result is empty where
        none of `row` is in view or all of it is under the heading. It is
        `in_view(row)`, which leaves out the part under this heading and
        under every heading around this section.
        """

        return in_view(row)

    def heading_place(self) -> QRect:
        """Return where the heading stands for the part in view, in the section's pixels.

        The heading stands at the top of the part in view, and never lower
        than the section's lower edge allows. Where none of the section is in
        view, it stands in its own space.
        """

        height = self.heading.sizeHint().height()
        shown = in_view(self)
        top = 0 if shown.isEmpty() else min(max(shown.top(), 0), max(self.height() - height, 0))
        # A heading that slides ends at the section's right edge, so a
        # control at its right end stays in view with the part in view. It is
        # never narrower than its least width, so no line is squeezed. Where
        # the part in view is narrower than that, the section's right edge
        # cuts the heading's end (`PL-BQB6`).
        left = self._inset if self._slides_left else 0
        width = max(self.width() - left, self._least_line_width()) if left else self.width()

        return QRect(left, top, width, height)

    def _least_line_width(self) -> int:
        """Return the least width that the widest of the heading's lines needs, in pixels.

        A line can ask for no width of its own, as an Area's header does so
        that a narrow Area clips its title rather than growing. The heading's
        own least width then leaves that line out, so each line is asked.
        """

        margins = self.heading.contentsMargins()
        lines = self.heading.findChildren(
            QWidget, options=Qt.FindChildOption.FindDirectChildrenOnly
        )
        widest = max(
            (line.minimumSizeHint().width() for line in lines if not line.isHidden()), default=0
        )

        return max(
            widest + margins.left() + margins.right(), self.heading.minimumSizeHint().width()
        )

    def _left_inset(self) -> int:
        """Return how far the heading's start moves right, to the left edge of the part in view.

        Where the part in view is narrower than a line of the heading, the
        line's end is cut at the section's right edge rather than its start.
        A line read from its start names what it labels, and one cut at its
        start may not.
        """

        if self._follows_left is None and not self._slides_left:
            return 0

        shown = in_view(self)

        return 0 if shown.isEmpty() else max(shown.left(), 0)

    def pin_heading(self) -> None:
        """Place the heading at the top of the section's part in view, over the rows there."""

        inset = self._left_inset()

        if self._follows_left is not None and inset != self._inset:
            margins = self._follows_left.contentsMargins()
            margins.setLeft(self._left_margin + inset)
            self._follows_left.setContentsMargins(margins)

        self._inset = inset

        height = self.heading.sizeHint().height()
        least_width = self.heading.minimumSizeHint().width() - (
            0 if self._follows_left is None else self._inset
        )

        # The space under the heading holds the section to the heading's
        # height and least width, so the section's layout makes room for a
        # heading that it does not hold.
        if self._room.height() != height:
            self._room.setFixedHeight(height)

        if self._room.minimumWidth() != least_width:
            self._room.setMinimumWidth(least_width)

        place = self.heading_place()
        self.heading.setGeometry(place)

        drawn = self._surface_at_home or place.top() > 0 or self._inset > 0

        if drawn != self._surface_drawn:
            self._surface_drawn = drawn
            self.heading.setStyleSheet(
                heading_surface_stylesheet(self.heading.objectName(), drawn=drawn)
            )

        self.heading.raise_()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # Qt spells this in camelCase.
        if watched is self.heading and event.type() == QEvent.Type.LayoutRequest:
            self.pin_heading()

        return super().eventFilter(watched, event)

    def resizeEvent(self, event: QResizeEvent) -> None:  # Qt spells this in camelCase.
        super().resizeEvent(event)
        self.pin_heading()

    def moveEvent(self, event: QMoveEvent) -> None:  # Qt spells this in camelCase.
        super().moveEvent(event)
        self.pin_heading()

    def showEvent(self, event: QShowEvent) -> None:  # Qt spells this in camelCase.
        super().showEvent(event)
        self.pin_heading()
