"""The heading that stays at the top of its section's part in view, built from plain widgets.

`app/pinned_heading.py` is the module under test. The compartment schematic's
own tests of its run headings are in
`tests/integration/test_compartment_schematic_view.py`. These build each
section from rows painted solid in `INK`, under a one-line heading, so each
test checks one promise of `PinnedHeadingSection` and nothing else on screen
can keep it. The tests render under the `offscreen` platform that
`tests/conftest.py` selects.
"""

from collections.abc import Iterator

import pytest
from PySide6.QtCore import QEvent, QPoint, QRect
from PySide6.QtGui import QColor, QImage, QPainter, QPaintEvent
from PySide6.QtWidgets import QApplication, QLabel, QScrollArea, QVBoxLayout, QWidget

from anesthesia_sim.app.pinned_heading import PinnedHeadingSection, pin_headings, pin_on_scroll
from anesthesia_sim.app.theme import INK

_ROW_HEIGHT_PX = 20
_BOX_WIDTH_PX = 300
_BOX_HEIGHT_PX = 150


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


@pytest.fixture
def boxes(application: QApplication) -> Iterator[list[QScrollArea]]:
    """The boxes a test shows, closed and deleted when it ends."""

    shown: list[QScrollArea] = []

    yield shown

    for box in shown:
        box.close()
        box.deleteLater()

    application.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    application.processEvents()


class _Row(QWidget):
    """A row painted solid in `INK`, so any part that shows through a heading changes its pixels."""

    def __init__(self) -> None:
        super().__init__()
        self.setFixedHeight(_ROW_HEIGHT_PX)

    def paintEvent(self, event: QPaintEvent) -> None:  # Qt spells this in camelCase.
        del event
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(INK))
        painter.end()


def _section(rows: int) -> PinnedHeadingSection:
    """Return a section of `rows` rows under the heading "Run 1".

    The rows are added after the section is built, as a View adds its rows, so
    each is a newer child than the heading and would be drawn over it unless
    the heading is raised.
    """

    section = PinnedHeadingSection(QLabel("Run 1"), "pinned_heading_test")
    section.column.setSpacing(0)

    for _ in range(rows):
        section.column.addWidget(_Row())

    return section


def _shown_box(
    application: QApplication,
    boxes: list[QScrollArea],
    *sections: PinnedHeadingSection,
    room_px: int = 0,
) -> tuple[QScrollArea, QWidget]:
    """Return a box that scrolls `sections`, stacked with no gap, and the widget it scrolls.

    The widget is at least `room_px` tall, and the space under the sections is
    empty. A section that grows into that space moves the sections under it
    without resizing them.
    """

    held = QWidget()
    held.setMinimumHeight(room_px)
    column = QVBoxLayout(held)
    column.setContentsMargins(0, 0, 0, 0)
    column.setSpacing(0)

    for section in sections:
        column.addWidget(section)

    column.addStretch(1)

    box = QScrollArea()
    box.setWidgetResizable(True)
    box.setWidget(held)
    box.resize(_BOX_WIDTH_PX, _BOX_HEIGHT_PX)
    boxes.append(box)
    box.show()
    application.processEvents()

    return box, held


def _heading_on_screen(box: QScrollArea, section: PinnedHeadingSection) -> QImage:
    """Return the pixels that the box shows where the section's heading stands."""

    heading = QRect(section.heading.mapTo(box.viewport(), QPoint(0, 0)), section.heading.size())

    return box.viewport().grab(heading).toImage()


def test_the_heading_hides_the_rows_scrolled_under_it(
    application: QApplication, boxes: list[QScrollArea]
) -> None:
    """`PL-Q740`: rows scrolled under the heading leave the heading's pixels as they were.

    The schematic's scroll tests count a value under a heading as hidden. That
    holds only while the heading is drawn over the rows and on an opaque
    surface. With the section's top in view, nothing lies under the heading.
    Scrolled five rows down, the heading stands over rows painted solid in
    `INK`. Its pixels must be the same in both places. A heading drawn under
    the rows, or on no surface of its own, lets the rows show through.
    """

    section = _section(rows=20)
    box, _ = _shown_box(application, boxes, section)
    pin_on_scroll(box)
    with_nothing_under_it = _heading_on_screen(box, section)

    box.verticalScrollBar().setValue(5 * _ROW_HEIGHT_PX)
    application.processEvents()

    # The premise: the heading has moved down over the fifth row.
    assert section.heading.y() == 5 * _ROW_HEIGHT_PX
    assert _heading_on_screen(box, section) == with_nothing_under_it


def test_a_section_moved_inside_its_box_moves_its_own_heading(
    application: QApplication, boxes: list[QScrollArea]
) -> None:
    """`PL-Q740`: a section that moves inside the widget its box scrolls moves its heading.

    Two sections are stacked, and the box is scrolled five rows into the
    second, whose heading is pinned there. Three rows then join the first
    section, as a line does when a schematic's container goes above the
    scale, so the second section moves 60 px down without any scroll. Its part
    in view now starts two rows into it, and its heading must stand there. The
    box here is not connected through `pin_on_scroll`, and the widget it
    scrolls has room under the sections, so the second section is moved and
    not resized. Only the section's own move can move the heading.
    """

    above = _section(rows=2)
    below = _section(rows=20)
    box, held = _shown_box(application, boxes, above, below, room_px=40 * _ROW_HEIGHT_PX)
    below_height = below.height()
    bar = box.verticalScrollBar()
    bar.setValue(below.y() + 5 * _ROW_HEIGHT_PX)
    application.processEvents()
    pin_headings(held)

    # The premise: the second section's heading is pinned five rows into it.
    assert below.heading.y() == 5 * _ROW_HEIGHT_PX

    for _ in range(3):
        above.column.addWidget(_Row())

    application.processEvents()

    # The premise: the first section grew by three rows, so the second moved
    # down by as much with no scroll and kept its height, and its part in view
    # now starts two rows into it.
    assert below.height() == below_height
    assert bar.value() - below.y() == 2 * _ROW_HEIGHT_PX
    assert below.heading.y() == 2 * _ROW_HEIGHT_PX
