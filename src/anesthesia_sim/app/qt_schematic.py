"""The drawing of one run's compartment schematic, in PySide6.

`SchematicCanvas` paints six containers and the lines that join them, from
the readings that `app/compartment_schematic.py` computes. The canvas computes
no value of its own. Each container fills from its bottom to the reading's
`fill`, in the colour of its compartment's chart trace. So a user who moves
between the schematic and the chart finds each compartment in one colour. The
compartment's tension, amount and share of all the agent are painted under its
container, in text, so no value is carried by colour or height alone
(`docs/INTERFACE.md` § "The compartment schematic: what its heights, amounts
and share bar assert"). Its name is painted over its column in the run's
heading (`ContainerNames`), which stays in view while any of the run's
schematic is in view (`PL-3NGZ`).
Short marks inside each container's two sides stand at the concentration
chart's gridlines. A container is much shorter than the chart's plot, so a
user reads a fill level against these marks, never across to the chart
(`PL-8W1B`).

**Nothing is drawn in part** (`PL-GWTR`). A container shows its tension as the
height of its fill, so one shown in part could look full, or empty, at a
tension it does not hold. A label line shown in part could be read as other
digits. So the canvas draws its containers only while all of them are whole in
view and clear of the run's heading, and each label line and share bar only
while it is. In place of the containers it paints `CUT_CONTAINERS_TEXT`.

**How the containers are joined** (`PL-RNYV`). The containers stand in one row
in the order the readout row lists them: the circuit, the alveoli, venous
blood, the vessel-rich group, muscle and fat. A line joins the circuit to the
alveoli, and stands for ventilation. A line above the row carries arterial
blood from the alveoli to each tissue group. A line below the row carries each
tissue group's venous blood to the venous container. A line joins the venous
container to the alveoli, and stands for the blood's return to the lungs. So
the three tissue groups are drawn in parallel, as the model perfuses them. They
are never drawn as a chain through which agent passes from one tissue to the
next. No container stands for arterial blood, for the reason `docs/MODEL.md`
§ "What the model represents" gives.

**The share bars** (`PL-S79P`, `PL-8PL4`). Under each container's label, a
short bar is filled from its left end to the compartment's share of all the
agent that the six compartments hold. The six bars are one length, so they
compare the shares on one scale, and each sits in its own container's column
under the label that names it. The containers' heights are tensions, so fat's
container stays nearly empty even while fat comes to hold a fifth of the agent.
Fat's bar is where the user sees that growing share.

Every size and colour choice here is a placeholder while the interface is being
built (project owner, 2026-10-18). The parallel drawing of the tissues is not a
placeholder, because it is what the model asserts.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from PySide6.QtCore import QPointF, QRect, QRectF, QSize, Qt
from PySide6.QtGui import QBrush, QColor, QFontMetrics, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget

from anesthesia_sim.app.chart_frame import trace_style
from anesthesia_sim.app.compartment_schematic import (
    CONTAINER_ORDER,
    CUT_CONTAINERS_TEXT,
    WIDEST_LABELS,
    WITHHELD_SCHEMATIC,
    ContainerReading,
    SchematicShown,
    instant_line,
)
from anesthesia_sim.app.pinned_heading import PinnedHeadingSection
from anesthesia_sim.app.qt_widgets import styled_label
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.app.theme import (
    INK,
    METRIC_QUALIFIER_SIZE,
    MUTED,
    VIEW_HEADING_SPACING,
    VIEW_ROW_SPACING,
    WARNING,
)

__all__ = ["CanvasParts", "ContainerNames", "RunSchematic", "SchematicCanvas"]

_TISSUES: Final = frozenset(
    {RecordedQuantity.VESSEL_RICH, RecordedQuantity.MUSCLE, RecordedQuantity.FAT}
)

# Sizes in logical pixels. Each is a placeholder.
_CONTAINER_WIDTH: Final = 44
_CONTAINER_HEIGHT: Final = 96
# The gap between a container and the arterial line above it, or the venous
# line below it.
_BUS_GAP: Final = 14
_COLUMN_GAP: Final = 12
_LABEL_GAP: Final = 8
_LINE_WIDTH: Final = 2.0
_OUTLINE_WIDTH: Final = 1.0
_OFF_SCALE_WIDTH: Final = 4.0
# The height of the share bar under each label, and the gap between the bar and
# the label's last line.
_SHARE_BAR_HEIGHT: Final = 8
_SHARE_BAR_GAP: Final = 4
# How far inside a share bar's edge its fill starts: past the 1 px outline and
# one pixel of the canvas's ground. Fat's and venous blood's colours are dark,
# so a small share drawn against the outline looked like a thicker outline.
_SHARE_FILL_INSET: Final = 2.0
# How far each mark reaches in from a container's side. It leaves the middle of
# the container clear, so the fill is seen whole between the marks.
_MARK_LENGTH: Final = 8.0
# Where in its column a container stands: at the column's centre, half of the
# column's width from its left edge.
_COLUMN_CENTRE: Final = 0.5
# Half a pixel, by which a share bar's 1 px outline is inset so that it is drawn
# on whole pixels, inside the bar.
_HALF_PIXEL: Final = 0.5
# How the cut-containers line is placed: at the top left of its space, wrapped
# where the canvas is narrower than the line.
_CUT_NOTICE_FLAGS: Final = int(
    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap
)


@dataclass(frozen=True)
class CanvasParts:
    """The parts of a run's schematic that its canvas paints now.

    Attributes:
        containers: Whether the containers are painted, with the lines that
            join them and the marks inside them. They are painted only while
            every container is whole in the canvas's clear part.
        lines: Each label line painted, as a pair of the container's index
            and the line's index under it (`SchematicCanvas.label_line`).
        bars: The index of each container whose share bar is painted.
        cut_notice: Where `CUT_CONTAINERS_TEXT` is painted in place of the
            containers, or None where it is not painted.
    """

    containers: bool
    lines: frozenset[tuple[int, int]]
    bars: frozenset[int]
    cut_notice: QRectF | None


class SchematicCanvas(QWidget):
    """One run's six containers, joined as the circulation joins them, each labelled in text.

    `show_readings` gives the canvas the readings of one snapshot, and the
    canvas paints exactly those. It keeps no reading of an earlier snapshot.

    The canvas paints only the parts that are whole in its clear part
    (`shown_parts`). The run that holds the canvas says where that part is,
    through `measure_clear_part`. A canvas that nobody measures paints every
    part.
    """

    def __init__(self) -> None:
        super().__init__()
        self._readings: tuple[ContainerReading, ...] = ()
        self._marks: tuple[float, ...] = ()
        self._clear_part: Callable[[], QRect] | None = None
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def measure_clear_part(self, clear_part: Callable[[], QRect]) -> None:
        """Read the canvas's clear part from `clear_part` each time the canvas paints.

        `clear_part` returns the part of the canvas that is in view and that
        nothing is drawn over, in the canvas's pixels. It is read at each
        paint rather than kept, so a scroll can never leave the canvas
        painting from where the clear part was before it.
        """

        self._clear_part = clear_part
        self.update()

    def shown_parts(self) -> CanvasParts:
        """Return the parts that `paintEvent` paints now, from the clear part as it is now.

        The containers are painted while every container, with the line that
        marks one above the scale, is whole in the clear part. Each label line
        and each share bar is painted while it is whole there. Only the
        vertical extent of each part is compared, because a cut at a side
        leaves a fill's height and a line's digits as they are. Where the
        containers are not painted, `CUT_CONTAINERS_TEXT` is painted at the top
        of the clear part, above the labels, where that space holds all of
        it.
        """

        if not self._readings:
            return CanvasParts(False, frozenset(), frozenset(), None)

        clear = None if self._clear_part is None else self._clear_part()

        def whole(top: float, bottom: float) -> bool:
            if clear is None:
                return True

            return (
                not clear.isEmpty() and clear.top() <= top and bottom <= clear.y() + clear.height()
            )

        reach = _container_reach()
        top = self._containers_top() - reach
        containers = whole(top, top + _CONTAINER_HEIGHT + 2.0 * reach)
        lines = frozenset(
            (index, line)
            for index in range(len(CONTAINER_ORDER))
            for line in range(_LABEL_LINES)
            if whole(self.label_line(index, line).top(), self.label_line(index, line).bottom())
        )
        bars = frozenset(
            index
            for index in range(len(CONTAINER_ORDER))
            if whole(self.share_bar(index).top(), self.share_bar(index).bottom())
        )

        return CanvasParts(
            containers,
            lines,
            bars,
            None if containers or clear is None else self._cut_notice(clear),
        )

    def _cut_notice(self, clear: QRect) -> QRectF | None:
        """Return where the cut-containers line goes in `clear`, or None where it does not fit."""

        top = max(clear.top(), 0)
        height = min(clear.y() + clear.height(), self._labels_top()) - top

        if clear.isEmpty() or height <= 0:
            return None

        space = QRect(0, top, self.width(), height)
        needed = QFontMetrics(self.font()).boundingRect(
            space, _CUT_NOTICE_FLAGS, CUT_CONTAINERS_TEXT
        )

        if needed.height() > height:
            return None

        return QRectF(0.0, float(top), float(self.width()), float(needed.height()))

    @property
    def readings(self) -> tuple[ContainerReading, ...]:
        """The readings painted now, one per container."""

        return self._readings

    @property
    def marks(self) -> tuple[float, ...]:
        """The height of each mark painted now, as a share of a container's height."""

        return self._marks

    def show_readings(
        self, readings: tuple[ContainerReading, ...], marks: tuple[float, ...]
    ) -> None:
        """Paint `readings`, one per container, in `CONTAINER_ORDER`, each marked at `marks`.

        Raises:
            ValueError: If the readings are not one per container in
                `CONTAINER_ORDER`. A container drawn from the wrong
                compartment's reading would show a plausible tension under
                the wrong name.
        """

        _check_order(readings)
        self._readings = readings
        self._marks = marks
        self.updateGeometry()
        self.update()

    def painted_strings(self) -> tuple[str, ...]:
        """Every label painted now: each container's tension, amount and share, in order.

        `paintEvent` paints exactly these strings, read through `_labels`, so a
        test that reads them reads what the reader sees (`PL-0G2P`). The
        containers' names are painted in the run's heading
        (`ContainerNames`).
        """

        return tuple(text for reading in self._readings for text in _labels(reading))

    def sizeHint(self) -> QSize:  # Qt spells this in camelCase.
        return self.minimumSizeHint()

    def minimumSizeHint(self) -> QSize:  # Qt spells this in camelCase.
        metrics = QFontMetrics(self.font())

        return QSize(
            self._column_width(metrics) * len(CONTAINER_ORDER),
            self._share_bars_top(metrics) + _SHARE_BAR_HEIGHT,
        )

    def share_bar(self, index: int) -> QRectF:
        """Return the outline of the share bar under container `index`, in the canvas's pixels.

        Every bar has one length: the width of the widest label that a column
        reserves room for. So the six bars compare the shares on one scale, and
        each share is read as the length of its fill from the bar's left end.
        The bar is centred in its container's column, under the label that
        names it. Its edges fall on whole pixels. `paintEvent` paints each bar
        here, so a test that measures a bar measures what the reader sees.

        Raises:
            IndexError: If `index` does not name one of the containers.
        """

        _check_index(index)
        metrics = QFontMetrics(self.font())
        length = self._column_width(metrics) - _COLUMN_GAP
        centre = self.width() / len(CONTAINER_ORDER) * (index + _COLUMN_CENTRE)

        return QRectF(
            float(round(centre - length / 2.0)),
            float(self._share_bars_top(metrics)),
            float(length),
            float(_SHARE_BAR_HEIGHT),
        )

    def container(self, index: int) -> QRectF:
        """Return the outline of container `index`, in the canvas's pixels.

        `paintEvent` fills and outlines each container here, so a test that
        finds a container finds what the reader sees.

        Raises:
            IndexError: If `index` does not name one of the containers.
        """

        _check_index(index)
        centre = self.width() / len(CONTAINER_ORDER) * (index + _COLUMN_CENTRE)

        return QRectF(
            centre - _CONTAINER_WIDTH / 2.0,
            self._containers_top(),
            float(_CONTAINER_WIDTH),
            float(_CONTAINER_HEIGHT),
        )

    def label_line(self, index: int, line: int) -> QRectF:
        """Return where line `line` of container `index`'s label is painted, in the canvas's pixels.

        The lines are counted from 0 at the top, in the order `_labels` gives
        them: the tension, the amount and the share. Each line is as
        wide as its container's column. `paintEvent` paints each line here, so
        a test that finds a line finds what the reader sees.

        Raises:
            IndexError: If `index` does not name one of the containers, or
                `line` is not one of the label's lines.
        """

        _check_index(index)

        if not 0 <= line < _LABEL_LINES:
            raise IndexError(f"a label has {_LABEL_LINES} lines, so it has no line {line}")

        height = QFontMetrics(self.font()).height()
        column = self.width() / len(CONTAINER_ORDER)

        return QRectF(
            column * index, float(self._labels_top() + line * height), column, float(height)
        )

    def paintEvent(self, event: QPaintEvent) -> None:  # Qt spells this in camelCase.
        del event

        if not self._readings:
            return

        parts = self.shown_parts()
        rectangles = [self.container(index) for index in range(len(CONTAINER_ORDER))]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if parts.containers:
            self._paint_connections(painter, rectangles)

        for index, (reading, rectangle) in enumerate(zip(self._readings, rectangles, strict=True)):
            if parts.containers:
                self._paint_container(painter, reading, rectangle)
                self._paint_marks(painter, rectangle)

            self._paint_labels(painter, index, reading, parts.lines)

            if index in parts.bars:
                self._paint_share_bar(painter, reading, self.share_bar(index))

        if parts.cut_notice is not None:
            painter.setPen(QColor(WARNING))
            painter.drawText(parts.cut_notice, _CUT_NOTICE_FLAGS, CUT_CONTAINERS_TEXT)

        painter.end()

    def containers_bottom(self) -> int:
        """Return how far below the canvas's top the containers end, in pixels.

        It counts the half of each outline drawn outside a container. A box
        that scrolls the canvas must be this tall below the run's heading
        before any scroll position shows the containers whole
        (`RunSchematic.legible_height`).
        """

        return math.ceil(self._containers_top() + _CONTAINER_HEIGHT + _container_reach())

    def _column_width(self, metrics: QFontMetrics) -> int:
        """The width of one container's column: its widest label, reserved or shown, and a gap."""

        return _column_width(metrics, self.painted_strings())

    @staticmethod
    def _containers_top() -> float:
        return float(_BUS_GAP)

    def _labels_top(self) -> int:
        return int(self._containers_top()) + _CONTAINER_HEIGHT + _BUS_GAP + _LABEL_GAP

    def _share_bars_top(self, metrics: QFontMetrics) -> int:
        return self._labels_top() + _LABEL_LINES * metrics.height() + _SHARE_BAR_GAP

    def _paint_connections(self, painter: QPainter, rectangles: list[QRectF]) -> None:
        """Join the containers as the model's circulation joins the compartments."""

        placed = dict(zip(CONTAINER_ORDER, rectangles, strict=True))
        circuit = placed[RecordedQuantity.CIRCUIT]
        alveoli = placed[RecordedQuantity.ALVEOLAR]
        venous = placed[RecordedQuantity.MIXED_VENOUS]
        tissues = [placed[quantity] for quantity in CONTAINER_ORDER if quantity in _TISSUES]
        middle = alveoli.center().y()
        arterial = alveoli.top() - _BUS_GAP / 2.0
        venous_line = alveoli.bottom() + _BUS_GAP / 2.0
        painter.setPen(QPen(QColor(MUTED), _LINE_WIDTH))

        # Ventilation, and the venous blood's return to the lungs.
        painter.drawLine(QPointF(circuit.right(), middle), QPointF(alveoli.left(), middle))
        painter.drawLine(QPointF(alveoli.right(), middle), QPointF(venous.left(), middle))

        # Arterial blood, from the alveoli to each tissue group.
        painter.drawLine(
            QPointF(alveoli.center().x(), alveoli.top()), QPointF(alveoli.center().x(), arterial)
        )
        painter.drawLine(
            QPointF(alveoli.center().x(), arterial), QPointF(tissues[-1].center().x(), arterial)
        )

        # Each tissue group's venous blood, to the venous container.
        painter.drawLine(
            QPointF(venous.center().x(), venous.bottom()), QPointF(venous.center().x(), venous_line)
        )
        painter.drawLine(
            QPointF(venous.center().x(), venous_line),
            QPointF(tissues[-1].center().x(), venous_line),
        )

        for tissue in tissues:
            x = tissue.center().x()
            painter.drawLine(QPointF(x, arterial), QPointF(x, tissue.top()))
            painter.drawLine(QPointF(x, tissue.bottom()), QPointF(x, venous_line))

    @staticmethod
    def _paint_container(painter: QPainter, reading: ContainerReading, rectangle: QRectF) -> None:
        """Fill a container to its tension from the bottom, outline it, and mark it if off scale."""

        filled = rectangle.height() * reading.fill
        painter.fillRect(
            QRectF(rectangle.left(), rectangle.bottom() - filled, rectangle.width(), filled),
            QBrush(QColor(trace_style(reading.quantity).color)),
        )
        painter.setPen(QPen(QColor(INK), _OUTLINE_WIDTH))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(rectangle)

        if reading.off_scale:
            painter.setPen(QPen(QColor(WARNING), _OFF_SCALE_WIDTH))
            painter.drawLine(rectangle.topLeft(), rectangle.topRight())

    def _paint_marks(self, painter: QPainter, rectangle: QRectF) -> None:
        """Draw a short mark inside both sides of a container at each of the chart's gridlines.

        The marks are drawn without antialiasing, so each is one whole row of
        pixels in `MUTED`, over the fill and over the empty part alike.
        """

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setPen(QPen(QColor(MUTED), _OUTLINE_WIDTH))

        for mark in self._marks:
            y = rectangle.bottom() - rectangle.height() * mark
            painter.drawLine(
                QPointF(rectangle.left(), y), QPointF(rectangle.left() + _MARK_LENGTH, y)
            )
            painter.drawLine(
                QPointF(rectangle.right() - _MARK_LENGTH, y), QPointF(rectangle.right(), y)
            )

        painter.restore()

    def _paint_labels(
        self,
        painter: QPainter,
        index: int,
        reading: ContainerReading,
        shown: frozenset[tuple[int, int]],
    ) -> None:
        """Paint the container's tension, amount and share under it, one line each, where shown."""

        painter.setPen(QColor(INK))

        for line, text in enumerate(_labels(reading)):
            if (index, line) not in shown:
                continue

            painter.drawText(
                self.label_line(index, line),
                int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop),
                text,
            )

    @staticmethod
    def _paint_share_bar(painter: QPainter, reading: ContainerReading, bar: QRectF) -> None:
        """Outline the bar in INK, and fill the inside from its left end to the reading's share.

        The fill starts one pixel inside the outline, so the outline never
        covers a small share, and a dark fill is not mistaken for a thicker
        outline. A reading with no share leaves the bar empty, and
        the outline still shows where the bar is and how long the whole would
        be. The bar is drawn without antialiasing, so that its fill and outline
        fall on whole pixels and a fill's length can be counted in pixels.
        """

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        if reading.share is not None:
            inset = _SHARE_FILL_INSET
            inside = bar.adjusted(inset, inset, -inset, -inset)
            painter.fillRect(
                QRectF(
                    inside.left(), inside.top(), inside.width() * reading.share, inside.height()
                ),
                QBrush(QColor(trace_style(reading.quantity).color)),
            )

        painter.setPen(QPen(QColor(INK), _OUTLINE_WIDTH))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(bar.adjusted(_HALF_PIXEL, _HALF_PIXEL, -_HALF_PIXEL, -_HALF_PIXEL))
        painter.restore()


class ContainerNames(QWidget):
    """The compartments' names, each centred over its own container's column.

    The run's heading holds this row, so the names stay in view with the
    heading while the Area scrolls. A tension, an amount or a share in view
    then always has its compartment's name over it (`PL-3NGZ`). The row is as
    wide as the canvas under it, and both divide their width into one equal
    column per container, so each name stands over its own container.
    """

    def __init__(self) -> None:
        super().__init__()
        self._names: tuple[str, ...] = ()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def show_names(self, readings: tuple[ContainerReading, ...]) -> None:
        """Paint the name of each of `readings`, one per container, in `CONTAINER_ORDER`.

        Raises:
            ValueError: If the readings are not one per container in
                `CONTAINER_ORDER`, as `SchematicCanvas.show_readings` says.
        """

        _check_order(readings)
        self._names = tuple(reading.name for reading in readings)
        self.updateGeometry()
        self.update()

    def painted_strings(self) -> tuple[str, ...]:
        """Every name painted now, in the containers' order.

        `paintEvent` paints exactly these strings, so a test that reads them
        reads what the reader sees (`PL-0G2P`).
        """

        return self._names

    def name_cell(self, index: int) -> QRectF:
        """Return where container `index`'s name is painted, in the row's pixels.

        The cell is as wide as the container's column. `paintEvent` paints each
        name here, so a test that finds a name finds what the reader sees.

        Raises:
            IndexError: If `index` does not name one of the containers.
        """

        _check_index(index)
        column = self.width() / len(CONTAINER_ORDER)

        return QRectF(column * index, 0.0, column, float(self.height()))

    def sizeHint(self) -> QSize:  # Qt spells this in camelCase.
        return self.minimumSizeHint()

    def minimumSizeHint(self) -> QSize:  # Qt spells this in camelCase.
        metrics = QFontMetrics(self.font())

        return QSize(_column_width(metrics, self._names) * len(CONTAINER_ORDER), metrics.height())

    def paintEvent(self, event: QPaintEvent) -> None:  # Qt spells this in camelCase.
        del event
        painter = QPainter(self)
        painter.setPen(QColor(INK))

        for index, name in enumerate(self._names):
            painter.drawText(
                self.name_cell(index),
                int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop),
                name,
            )

        painter.end()


def _container_reach() -> float:
    """Return how far a container's painting reaches past its outline: half its widest line."""

    return max(_OFF_SCALE_WIDTH, _OUTLINE_WIDTH) / 2.0


def _check_order(readings: tuple[ContainerReading, ...]) -> None:
    """Refuse readings that are not one per container, in `CONTAINER_ORDER`.

    Raises:
        ValueError: If the readings' compartments are not `CONTAINER_ORDER`.
    """

    if tuple(reading.quantity for reading in readings) != CONTAINER_ORDER:
        raise ValueError(
            "the schematic draws one reading per container in "
            f"{[quantity.name for quantity in CONTAINER_ORDER]}, not "
            f"{[reading.quantity.name for reading in readings]}"
        )


def _check_index(index: int) -> None:
    """Refuse an index that names none of the containers.

    Raises:
        IndexError: If `index` is not from 0 to one less than the number of
            containers.
    """

    if not 0 <= index < len(CONTAINER_ORDER):
        raise IndexError(
            f"the schematic has {len(CONTAINER_ORDER)} containers, so it has none at index {index}"
        )


def _column_width(metrics: QFontMetrics, shown: tuple[str, ...]) -> int:
    """The width of one container's column: its widest label, reserved or `shown`, and a gap.

    The canvas and the heading's row of names both read it, so a name stands
    over its own container at every width.
    """

    widest = max(metrics.horizontalAdvance(text) for text in (*WIDEST_LABELS, *shown))

    return max(widest, _CONTAINER_WIDTH) + _COLUMN_GAP


def _labels(reading: ContainerReading) -> tuple[str, str, str]:
    """The lines painted under one container, from the top: its tension, amount and share.

    The painting and `SchematicCanvas.painted_strings` both read this one
    function, so no painted line can be left out of what a test reads.
    """

    return (reading.tension, reading.amount, reading.share_text)


#: How many lines `_labels` paints under each container. It is counted from
#: `_labels` itself, so a line added there moves the share bars down with it.
_LABEL_LINES: Final = len(_labels(WITHHELD_SCHEMATIC.readings[0]))


#: The object name of each run's heading, which scopes its surface's stylesheet.
_RUN_HEADING_NAME: Final = "runSchematicHeading"


class RunSchematic(PinnedHeadingSection):
    """One run's compartment schematic: its heading, its containers and share bars, and its lines.

    The compartment schematic View builds one for each displayed run, and
    writes it on every tick from that run's `RunPresentation`
    (`app/views.py`, `app/run_presentation.py`). The presentation holds the
    schematic, the run's name and the run's readouts together. So a
    schematic never shows a state that its run has left while the readouts
    show another, and it is withheld whenever the readouts are (`PL-RNYV`,
    `PL-RF2S`). A lone run is not named. While runs are compared, each
    schematic is named, because the order in which the schematics are
    stacked cannot say which run a tension belongs to. The hazard table in
    `docs/VERIFICATION.md` § "Reasonably foreseeable misuse, and the hazards the
    presentation carries" has a row on reading one run's value as the other's.

    The heading holds the line that names the run and the instant, the line
    that says what the shares are of, and the containers' names. It stays at
    the top of the part of the schematic in view while the Area scrolls
    (`PinnedHeadingSection`). So on a laptop screen no label or share bar is
    in view without the run's name, its compartment's name or what its share
    is of (`PL-3NGZ`).

    Args:
        shown: The schematic to draw first.
        name: The run's name while runs are compared, or None.

    Attributes:
        name_text: The line that names the instant shown, and the run while
            runs are compared.
        share_text: The line that says what every share is a part of, or why
            no share is shown.
        names: The containers' names, each over its own container.
        canvas: The containers, their labels and their share bars.
        off_scale_text: The lines that name each container above the scale.
        scale_text: The caption that names the scale the containers fill
            against, and says that the amounts held in the body read high.
    """

    def __init__(self, shown: SchematicShown, name: str | None) -> None:
        name_text = styled_label("", color=INK, bold=True)
        share_text = styled_label("", color=MUTED, size_px=METRIC_QUALIFIER_SIZE)
        names = ContainerNames()
        heading = QWidget()
        rows = QVBoxLayout(heading)
        # The lower margin keeps a row that scrolls under the heading clear
        # of its words, and is the gap above the canvas while nothing has
        # scrolled.
        rows.setContentsMargins(0, 0, 0, VIEW_ROW_SPACING)
        rows.setSpacing(VIEW_ROW_SPACING)
        line = QHBoxLayout()
        line.setContentsMargins(0, 0, 0, 0)
        line.setSpacing(VIEW_HEADING_SPACING)
        line.addWidget(name_text, 0, Qt.AlignmentFlag.AlignBaseline)
        line.addWidget(share_text, 0, Qt.AlignmentFlag.AlignBaseline)
        line.addStretch(1)
        rows.addLayout(line)
        rows.addWidget(names)
        super().__init__(heading, _RUN_HEADING_NAME)
        self.name_text = name_text
        self.share_text = share_text
        self.names = names
        self.canvas = SchematicCanvas()
        self.canvas.measure_clear_part(lambda: self.clear_of_heading(self.canvas))
        self.scale_text = styled_label("", color=MUTED, size_px=METRIC_QUALIFIER_SIZE)
        self.off_scale_text = styled_label("", color=WARNING, size_px=METRIC_QUALIFIER_SIZE)
        self.column.setSpacing(VIEW_ROW_SPACING)
        self.column.addWidget(self.canvas)
        # The off-scale line comes first under the containers, because it
        # warns that a fill is cut off.
        self.column.addWidget(self.off_scale_text)
        self.column.addWidget(self.scale_text)
        self._name = name
        self._shown = shown
        self.show_schematic(shown)

    def painted_strings(self) -> tuple[str, ...]:
        """Every string painted without a label: each container's name, tension, amount and share.

        They come in the containers' order, the name first, which is the
        order a reader takes them in down each column.
        """

        labels = self.canvas.painted_strings()

        return tuple(
            text
            for index, name in enumerate(self.names.painted_strings())
            for text in (name, *labels[index * _LABEL_LINES : (index + 1) * _LABEL_LINES])
        )

    def pin_heading(self) -> None:
        """Place the heading over the part in view, and repaint the canvas for what it leaves clear.

        A scroll moves the canvas's pixels without asking the canvas to paint
        them again, so a container that the scroll has cut would stay painted
        whole. The canvas is therefore repainted after every move of the
        heading, and paints only what is whole in its clear part now
        (`SchematicCanvas.shown_parts`).
        """

        super().pin_heading()
        self.canvas.update()

    def legible_height(self) -> int:
        """Return the least height of a box in which a scroll can show every container whole.

        It is the heading's height and the canvas's height down to the
        containers' lower edge. In a shorter box, every scroll position cuts
        the containers, by the heading or by the box's lower edge
        (`CompartmentSchematicView.legible_height`, `PL-GWTR`).
        """

        return self.heading.sizeHint().height() + self.canvas.containers_bottom()

    def show_name(self, name: str | None) -> None:
        """Name the schematic while runs are compared, or leave it unnamed when `name` is None."""

        self._name = name
        self.name_text.setText(instant_line(self._shown.instant, name))
        self.pin_heading()

    def show_schematic(self, shown: SchematicShown) -> None:
        """Draw `shown`: the instant it is read at, its containers, and each of its other lines."""

        self.canvas.show_readings(shown.readings, shown.marks)
        self.names.show_names(shown.readings)
        self._shown = shown
        self.name_text.setText(instant_line(shown.instant, self._name))

        for label, text in (
            (self.scale_text, shown.scale_caption),
            (self.off_scale_text, shown.off_scale_line),
            (self.share_text, shown.share_caption),
        ):
            label.setText(text or "")
            label.setHidden(text is None)

        self.pin_heading()
