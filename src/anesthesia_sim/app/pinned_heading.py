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

The heading is drawn over the section's rows, on the panel's colour. So a row
is either below the heading, and seen, or under it, and hidden. No row can be
seen without the heading.

Every box that scrolls a section moves the heading again after each scroll
(`pin_on_scroll`). That includes the dashboard's page, which scrolls every
Area in a window too small for them.
"""

from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QMoveEvent, QResizeEvent, QShowEvent
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from anesthesia_sim.app.stylesheets import heading_surface_stylesheet

__all__ = ["PinnedHeadingSection", "in_view", "pin_headings", "pin_on_scroll"]


def in_view(widget: QWidget) -> QRect:
    """Return the part of `widget` that its ancestors leave in view, in the widget's own pixels.

    Each ancestor clips what it holds to its own rectangle, so a widget inside
    a box that scrolls is in view only where it lies within the box's
    viewport. The result is empty for a widget that is not visible. Only the
    ancestors' geometry is read, which is what Qt reads to clip a widget's
    painting.
    """

    if not widget.isVisible():
        return QRect()

    shown = widget.rect()
    ancestor = widget.parentWidget()

    while ancestor is not None and not shown.isEmpty():
        shown = shown.intersected(QRect(widget.mapFrom(ancestor, QPoint(0, 0)), ancestor.size()))
        ancestor = ancestor.parentWidget()

    return shown


def pin_headings(root: QWidget) -> None:
    """Move the heading of every `PinnedHeadingSection` under `root` to the top of its part in view.

    A box that scrolls its widget calls this after each scroll and each
    resize, because a scroll moves the widget it holds and leaves each section
    where it is inside that widget. So no section learns of a scroll by
    itself. `ViewScroll` calls it on a resize, and `pin_on_scroll` on a
    scroll.
    """

    for section in root.findChildren(PinnedHeadingSection):
        section.pin_heading()


def pin_on_scroll(box: QScrollArea) -> None:
    """Move the headings in the widget that `box` scrolls each time `box` scrolls, on either axis.

    A box moves the widget it holds when its scroll bar moves. Qt connects
    the bar to that move when the box is built, so the move has happened by
    the time this connection runs. `ViewScroll` and the dashboard's page call
    this, so a heading follows a scroll of its Area and of the page alike.
    """

    def pin(_: int) -> None:
        held = box.widget()

        if held is not None:
            pin_headings(held)

    box.verticalScrollBar().valueChanged.connect(pin)
    box.horizontalScrollBar().valueChanged.connect(pin)


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

    Attributes:
        heading: The heading.
        column: The layout that the section's rows go in, under the
            heading's space. A subclass sets its spacing.
    """

    def __init__(self, heading: QWidget, object_name: str) -> None:
        super().__init__()
        self.heading = heading
        heading.setParent(self)
        heading.setObjectName(object_name)
        heading.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        heading.setStyleSheet(heading_surface_stylesheet(object_name))
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

    def pin_heading(self) -> None:
        """Place the heading at the top of the section's part in view, over the rows there."""

        height = self.heading.sizeHint().height()
        least_width = self.heading.minimumSizeHint().width()

        # The space under the heading holds the section to the heading's
        # height and least width, so the section's layout makes room for a
        # heading that it does not hold.
        if self._room.height() != height:
            self._room.setFixedHeight(height)

        if self._room.minimumWidth() != least_width:
            self._room.setMinimumWidth(least_width)

        shown = in_view(self)
        top = 0 if shown.isEmpty() else min(max(shown.top(), 0), max(self.height() - height, 0))
        self.heading.setGeometry(0, top, self.width(), height)
        self.heading.raise_()

    def resizeEvent(self, event: QResizeEvent) -> None:  # Qt spells this in camelCase.
        super().resizeEvent(event)
        self.pin_heading()

    def moveEvent(self, event: QMoveEvent) -> None:  # Qt spells this in camelCase.
        super().moveEvent(event)
        self.pin_heading()

    def showEvent(self, event: QShowEvent) -> None:  # Qt spells this in camelCase.
        super().showEvent(event)
        self.pin_heading()
