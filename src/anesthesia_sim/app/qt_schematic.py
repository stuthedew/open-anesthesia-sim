"""The drawing of one run's compartment schematic, in PySide6.

`SchematicCanvas` paints six containers and the lines that join them, from
the readings that `app/compartment_schematic.py` computes. The canvas computes
no value of its own. Each container fills from its bottom to the reading's
`fill`, in the colour of its compartment's chart trace. So a learner who moves
between the schematic and the chart finds each compartment in one colour. The
compartment's name, tension and amount are painted under its container, in
text, so no value is carried by colour or height alone (`docs/MODEL.md`
§ "The compartment schematic: what its heights, amounts and share bar assert").

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
gives.

**The share bar** (`PL-S79P`). Under the containers, `ShareBar` draws one bar.
The bar is divided into each compartment's share of all the agent the run
holds, in the containers' order and colours. The lines under the bar name each
share in text. The containers' heights are tensions, so fat's container stays
nearly empty even while fat comes to hold a fifth of the agent. The bar is
where the learner sees that growing share.

Every size and colour choice here is a placeholder while the interface is being
built (project owner, 2026-10-18). The parallel drawing of the tissues is not a
placeholder, because it is what the model asserts.
"""

from __future__ import annotations

from typing import Final

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QBrush, QColor, QFontMetrics, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

from anesthesia_sim.app.chart_frame import trace_style
from anesthesia_sim.app.compartment_schematic import (
    CONTAINER_ORDER,
    WIDEST_LABELS,
    ContainerReading,
    SchematicShown,
    ShareSegment,
    instant_line,
)
from anesthesia_sim.app.qt_widgets import styled_label
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.app.theme import (
    INK,
    METRIC_QUALIFIER_SIZE,
    MUTED,
    PANEL,
    VIEW_ROW_SPACING,
    WARNING,
)

__all__ = ["RunSchematic", "SchematicCanvas", "ShareBar"]

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
_LABEL_LINES: Final = 3
# Where in its column a container stands: at the column's centre, half of the
# column's width from its left edge.
_COLUMN_CENTRE: Final = 0.5
# Half a pixel, by which the share bar's 1 px outline is inset so that it is
# drawn on whole pixels, inside the bar.
_HALF_PIXEL: Final = 0.5


class SchematicCanvas(QWidget):
    """One run's six containers, joined as the circulation joins them, each labelled in text.

    `show_readings` gives the canvas the readings of one snapshot, and the
    canvas paints exactly those. It keeps no reading of an earlier snapshot.
    """

    def __init__(self) -> None:
        super().__init__()
        self._readings: tuple[ContainerReading, ...] = ()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    @property
    def readings(self) -> tuple[ContainerReading, ...]:
        """The readings painted now, one per container."""

        return self._readings

    def show_readings(self, readings: tuple[ContainerReading, ...]) -> None:
        """Paint `readings`, one per container, in `CONTAINER_ORDER`.

        Raises:
            ValueError: If the readings are not one per container in
                `CONTAINER_ORDER`. A container drawn from the wrong
                compartment's reading would show a plausible tension under
                the wrong name.
        """

        if tuple(reading.quantity for reading in readings) != CONTAINER_ORDER:
            raise ValueError(
                "the schematic draws one reading per container in "
                f"{[quantity.name for quantity in CONTAINER_ORDER]}, not "
                f"{[reading.quantity.name for reading in readings]}"
            )

        self._readings = readings
        self.updateGeometry()
        self.update()

    def painted_strings(self) -> tuple[str, ...]:
        """Every label painted now: each container's name, tension and amount, in order."""

        return tuple(
            text
            for reading in self._readings
            for text in (reading.name, reading.tension, reading.amount)
        )

    def sizeHint(self) -> QSize:  # Qt spells this in camelCase.
        return self.minimumSizeHint()

    def minimumSizeHint(self) -> QSize:  # Qt spells this in camelCase.
        metrics = QFontMetrics(self.font())

        return QSize(
            self._column_width(metrics) * len(CONTAINER_ORDER),
            self._labels_top() + _LABEL_LINES * metrics.height(),
        )

    def paintEvent(self, event: QPaintEvent) -> None:  # Qt spells this in camelCase.
        del event

        if not self._readings:
            return

        metrics = QFontMetrics(self.font())
        column = self.width() / len(CONTAINER_ORDER)
        rectangles = [self._container(index, column) for index in range(len(CONTAINER_ORDER))]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._paint_connections(painter, rectangles)

        for reading, rectangle in zip(self._readings, rectangles, strict=True):
            self._paint_container(painter, reading, rectangle)
            self._paint_labels(painter, metrics, reading, rectangle.center().x(), column)

        painter.end()

    def _column_width(self, metrics: QFontMetrics) -> int:
        """The width of one container's column: its widest label, reserved or shown, and a gap."""

        texts = (*WIDEST_LABELS, *self.painted_strings())
        widest = max(metrics.horizontalAdvance(text) for text in texts)

        return max(widest, _CONTAINER_WIDTH) + _COLUMN_GAP

    @staticmethod
    def _containers_top() -> float:
        return float(_BUS_GAP)

    def _labels_top(self) -> int:
        return int(self._containers_top()) + _CONTAINER_HEIGHT + _BUS_GAP + _LABEL_GAP

    def _container(self, index: int, column: float) -> QRectF:
        centre = column * (index + _COLUMN_CENTRE)

        return QRectF(
            centre - _CONTAINER_WIDTH / 2.0,
            self._containers_top(),
            float(_CONTAINER_WIDTH),
            float(_CONTAINER_HEIGHT),
        )

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

    def _paint_labels(
        self,
        painter: QPainter,
        metrics: QFontMetrics,
        reading: ContainerReading,
        centre: float,
        column: float,
    ) -> None:
        """Paint the container's name, tension and amount under it, one line each."""

        painter.setPen(QColor(INK))
        top = float(self._labels_top())

        for line, text in enumerate((reading.name, reading.tension, reading.amount)):
            painter.drawText(
                QRectF(
                    centre - column / 2.0, top + line * metrics.height(), column, metrics.height()
                ),
                int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop),
                text,
            )


# The share bar's height, in logical pixels, and the least width of a segment
# that a divider is drawn before. Both are placeholders.
_SHARE_BAR_HEIGHT: Final = 18
_SHARE_DIVIDED_PX: Final = 3.0


class ShareBar(QWidget):
    """One bar, divided into each compartment's share of the agent the run holds (`PL-S79P`).

    The segments stand left to right in the containers' order. Each is filled
    in its compartment's trace colour, and each segment's length is its share
    of the bar's length. The bar is outlined in INK, so an empty bar still
    shows where the bar is. `RunSchematic` shows lines under the bar that name
    the segments in text, so no segment is told apart by colour alone. Readers
    judge a position along one common scale more accurately than an area
    (`docs/MODEL.md` § "The compartment schematic: what its heights, amounts
    and share bar assert"). So the bar carries the comparison of amounts that
    the containers' heights cannot.
    """

    def __init__(self) -> None:
        super().__init__()
        self._segments: tuple[ShareSegment, ...] | None = None
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    @property
    def segments(self) -> tuple[ShareSegment, ...] | None:
        """The segments painted now, or None while the bar is drawn empty."""

        return self._segments

    def show_segments(self, segments: tuple[ShareSegment, ...] | None) -> None:
        """Paint `segments`, one per container in `CONTAINER_ORDER`, or an empty bar for None.

        Raises:
            ValueError: If the segments are not one per container in
                `CONTAINER_ORDER`, which would paint one compartment's share
                in another's colour.
        """

        if segments is not None and (
            tuple(segment.quantity for segment in segments) != CONTAINER_ORDER
        ):
            raise ValueError(
                "the share bar draws one segment per container in "
                f"{[quantity.name for quantity in CONTAINER_ORDER]}, not "
                f"{[segment.quantity.name for segment in segments]}"
            )

        self._segments = segments
        self.update()

    def sizeHint(self) -> QSize:  # Qt spells this in camelCase.
        return self.minimumSizeHint()

    def minimumSizeHint(self) -> QSize:  # Qt spells this in camelCase.
        return QSize(_CONTAINER_WIDTH * len(CONTAINER_ORDER), _SHARE_BAR_HEIGHT)

    def paintEvent(self, event: QPaintEvent) -> None:  # Qt spells this in camelCase.
        del event

        bar = QRectF(0.0, 0.0, float(self.width()), float(_SHARE_BAR_HEIGHT))
        painter = QPainter(self)

        # Each segment starts where the shares before it end, so the segments
        # tile the bar without gaps or overlaps however the lengths round.
        if self._segments is not None:
            start = 0.0

            for segment in self._segments:
                end = start + segment.share
                painter.fillRect(
                    QRectF(
                        bar.left() + bar.width() * start,
                        bar.top(),
                        bar.width() * (end - start),
                        bar.height(),
                    ),
                    QBrush(QColor(trace_style(segment.quantity).color)),
                )
                start = end

            # A line in the panel's colour divides each pair of neighbouring visible
            # segments. So the ends of each segment are seen against the panel, and
            # the panel's contrast with every compartment colour is checked. They
            # are never seen only against a neighbour's colour, whose contrast is
            # not checked. A segment narrower than `_SHARE_DIVIDED_PX` gets no
            # divider. So a divider never covers a segment, and the visible segments
            # stay in the order in which the lines under the bar name them.
            painter.setPen(QPen(QColor(PANEL), _OUTLINE_WIDTH))
            start = 0.0
            visible_before = False

            for segment in self._segments:
                width = bar.width() * segment.share
                visible = width >= _SHARE_DIVIDED_PX

                if visible and visible_before:
                    x = bar.left() + bar.width() * start
                    painter.drawLine(QPointF(x, bar.top()), QPointF(x, bar.bottom()))

                visible_before = visible_before or visible
                start += segment.share

        painter.setPen(QPen(QColor(INK), _OUTLINE_WIDTH))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(bar.adjusted(_HALF_PIXEL, _HALF_PIXEL, -_HALF_PIXEL, -_HALF_PIXEL))
        painter.end()


class RunSchematic(QWidget):
    """One run's compartment schematic: its name, containers, lines and share bar.

    The compartment schematic View builds one for each displayed run, and
    writes it on every tick from that run's `RunPresentation`
    (`app/views.py`, `app/run_presentation.py`). The presentation holds the
    schematic, the run's name and the run's readouts together. So a
    schematic never shows a state that its run has left while the readouts
    show another, and it is withheld whenever the readouts are (`PL-RNYV`,
    `PL-RF2S`). A lone run is not named. While runs are compared, each
    schematic is named, because the order in which the schematics are
    stacked cannot say which run a tension belongs to (`docs/MODEL.md`, the
    hazard table's row on reading one run's value as the other's).

    Args:
        shown: The schematic to draw first.
        name: The run's name while runs are compared, or None.
        parent: The Qt parent.
    """

    def __init__(
        self, shown: SchematicShown, name: str | None, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.name_text = styled_label("", color=INK, bold=True)
        self.canvas = SchematicCanvas()
        self.scale_text = styled_label("", color=MUTED, size_px=METRIC_QUALIFIER_SIZE)
        self.off_scale_text = styled_label("", color=WARNING, size_px=METRIC_QUALIFIER_SIZE)
        self.share_bar = ShareBar()
        self.share_text = styled_label("", color=INK, size_px=METRIC_QUALIFIER_SIZE)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(VIEW_ROW_SPACING)
        column.addWidget(self.name_text)
        column.addWidget(self.canvas)
        column.addWidget(self.off_scale_text)
        column.addWidget(self.scale_text)
        column.addWidget(self.share_bar)
        column.addWidget(self.share_text)
        self._name = name
        self._shown = shown
        self.show_schematic(shown)

    def show_name(self, name: str | None) -> None:
        """Name the schematic while runs are compared, or leave it unnamed when `name` is None."""

        self._name = name
        self.name_text.setText(instant_line(self._shown.instant, name))

    def show_schematic(self, shown: SchematicShown) -> None:
        """Draw `shown`: the instant it is read at, its containers, and each of its other lines."""

        self._shown = shown
        self.name_text.setText(instant_line(shown.instant, self._name))
        self.canvas.show_readings(shown.readings)
        self.share_bar.show_segments(shown.shares)

        for label, text in (
            (self.scale_text, shown.scale_caption),
            (self.off_scale_text, shown.off_scale_line),
            (self.share_text, shown.share_line),
        ):
            label.setText(text or "")
            label.setHidden(text is None)
