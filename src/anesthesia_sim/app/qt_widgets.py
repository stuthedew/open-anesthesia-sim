"""The dashboard's leaf widgets, which move to match `dashboard_frame` and decide nothing.

The toolkit half of everything on the dashboard that is not a plot: a
readout panel and the row of them, a setting slider, the notice banner, the
new-case confirmation, the inert splitter between sections, and the window's
opening geometry. Each is written from a `dashboard_frame` value - a
`Readout`, a `SettingReadout`, a `NewCaseQuestion` - and reads nothing from
the simulation, formats no number and chooses between no two strings, so
every claim a reader sees stays where `tests/unit/test_dashboard_frame.py`
can hold it without a display (`PL-25KS`, decision D2). What a widget does
own is layout arithmetic: how wide a panel must be, how many columns a row
gets at a width, where the window opens.

**A readout value never wraps away from its unit** (`PL-3355`). Each of a
panel's four lines is a `QLabel` without word wrap, and the panel reserves
its width once, from the font-metric advance of the widest string its
column can show, so no window width can put "0.13" on one line and "%" on
the next. The reservation is measured rather than declared; the Flet
build's fixed guess at the clock's width, `theme.ELAPSED_VALUE_WIDTH`, was
retired with the port (`PL-25KS`).

**A slider position is a printed value** (`PL-25KS`, decision D4). The four
sliders are integer `QSlider`s whose one step is the control's display
resolution, decoded through `dashboard_frame.slider_value`, so the number
applied to the model is exactly the number beside the thumb.

**A row that has to wrap wraps here.** Qt ships no wrapping row, and the
legend rows the Flet build wrapped (`ft.Row(wrap=True)`) held the chart
column to 1220 px on one unbreakable line of six checkboxes, pushing the
sidebar off a 1400 px window. `FlowLayout` is the shape of Qt's documented
Flow Layout example, and `qt_chart` lays every legend row in one.

**Every colour is `app/theme.py`'s**, reaching a stylesheet as an f-string
over the theme name (decision D10), so `tools/contrast_check.py`'s palette
is the palette drawn. The few bare pixel spacings inside stylesheets are the
interim decision D9 accepts; `PL-L9RD` names the spacing scale that replaces
them.
"""

from __future__ import annotations

from collections.abc import Sequence
from math import ceil
from typing import Final

from PySide6.QtCore import QPoint, QRect, QSignalBlocker, QSize, Qt, Signal
from PySide6.QtGui import QFont, QFontMetrics, QResizeEvent
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLayoutItem,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSlider,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from anesthesia_sim.app.bookmarks import CrossingDirection, MacTarget, TimeBookmark
from anesthesia_sim.app.chart_frame import trace_style
from anesthesia_sim.app.dashboard_frame import (
    ADD_MARK_LABEL,
    BOOKMARK_DIALOG_TITLE,
    CLOSE_BOOKMARKS_LABEL,
    COMPARTMENT_FIELD_LABEL,
    CROSSING_DIRECTION_WORDS,
    DEFAULT_MAXIMUM_TARGET_MAC,
    DIRECTION_FIELD_LABEL,
    EDIT_BOOKMARKS_LABEL,
    HEIGHT_FIELD_LABEL,
    INSTANT_ENTRY_DECIMALS,
    INSTANT_ENTRY_STEP_S,
    INSTANT_ENTRY_SUFFIX,
    INSTANT_FIELD_LABEL,
    MAC_TARGET_HEADING,
    MARK_NAME_FIELD_LABEL,
    MARK_NAME_PLACEHOLDER,
    REMOVE_MARK_LABEL,
    TIME_BOOKMARK_HEADING,
    BookmarkPanel,
    MarkListing,
    NewCaseQuestion,
    Readout,
    SettingReadout,
    readout_columns,
    readout_row_width,
    slider_position,
    slider_value,
)
from anesthesia_sim.app.formatting import (
    MAC_DISPLAY_DECIMALS,
    MAC_DISPLAY_RESOLUTION_MAC,
    MAC_UNIT_SUFFIX,
    format_elapsed,
)
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity
from anesthesia_sim.app.theme import (
    ACCENT,
    BOOKMARK_DIALOG_WIDTH,
    BOOKMARK_ROW_SPACING,
    BOOKMARK_SECTION_SPACING,
    GRIDLINE,
    INK,
    METRIC_NAME_SIZE,
    METRIC_QUALIFIER_SIZE,
    METRIC_SECONDARY_VALUE_SIZE,
    METRIC_VALUE_SIZE,
    MUTED,
    NEW_CASE_DIALOG_SPACING,
    NEW_CASE_DIALOG_WIDTH,
    PANEL,
    PANEL_PADDING,
    PANEL_RADIUS,
    PARAMETER_QUALIFIER_SIZE,
    PRIMARY,
    WARNING,
)
from anesthesia_sim.core.concentration import MacMultiple
from anesthesia_sim.core.supported_ranges import MAXIMUM_ELAPSED_SIMULATION_TIME_S

# How much of the screen's available area the window opens on (`PL-005`).
# A fraction rather than a size, so the same rule opens a window that is
# fully visible on every display, and never full-screen, which hides the
# window controls on some platforms.
WINDOW_SCREEN_FRACTION: Final = 0.8


def styled_label(
    text: str,
    *,
    color: str,
    size_px: int | None = None,
    bold: bool = False,
    italic: bool = False,
    wrap: bool = False,
) -> QLabel:
    """A label in one of the theme's colours, at one of its sizes.

    Args:
        text: What the label says.
        color: A `theme.py` colour name's value; it reaches the label as a
            stylesheet f-string, never as a literal.
        size_px: The theme's pixel size for this line, or None for the
            application default.
        bold: Whether the text is bold.
        italic: Whether the text is italic.
        wrap: Whether the text may break across lines. Off by default,
            because a value that wraps loses its unit (`PL-3355`).

    Returns:
        The label.
    """

    label = QLabel(text)
    label.setStyleSheet(f"color: {color};")
    label.setWordWrap(wrap)
    font = QFont(label.font())

    if size_px is not None:
        font.setPixelSize(size_px)

    font.setBold(bold)
    font.setItalic(italic)
    label.setFont(font)

    return label


def _advance_px(label: QLabel, text: str) -> int:
    """How wide `text` is in `label`'s font, in logical pixels."""

    return QFontMetrics(label.font()).horizontalAdvance(text)


def _panel_stylesheet(object_name: str) -> str:
    """The panel surface: PANEL, rounded, scoped to one widget so its children keep their own."""

    return (
        f"QWidget#{object_name} {{ background-color: {PANEL}; border-radius: {PANEL_RADIUS}px; }}"
    )


def _slider_stylesheet() -> str:
    """The slider's track and thumb in the theme's colours.

    The active track is `ACCENT`, the colour `PL-W8DQ` measures for it. Qt
    paints a styled sub-page only inside a groove that is itself styled,
    and a styled groove draws no thumb of its own, so all three parts are
    given here: the unfilled track in `GRIDLINE`, the ruling colour, and
    the thumb as a `PANEL` disc edged in `MUTED`.
    """

    return (
        f"QSlider::groove:horizontal {{ background: {GRIDLINE}; height: 4px; "
        f"border-radius: 2px; }} "
        f"QSlider::sub-page:horizontal {{ background: {ACCENT}; border-radius: 2px; }} "
        f"QSlider::handle:horizontal {{ background: {PANEL}; border: 1px solid {MUTED}; "
        f"width: 14px; margin: -6px 0; border-radius: 8px; }}"
    )


def selector_stylesheet() -> str:
    """A combo box a reader reads rather than merely operates: PANEL fill, MUTED edge, INK text.

    The playback-rate and time-base selectors name the rate the clock is
    advancing at and how much of the run is on screen, which
    `docs/MODEL.md` requires displayed (`PL-SN2C`), so their surface is set
    here rather than left to the platform style: `tools/contrast_check.py`
    measures INK on PANEL for the text and MUTED against each selector's own
    surroundings for the border, and both claims hold only because the
    colours are these.
    """

    return (
        f"QComboBox {{ background-color: {PANEL}; color: {INK}; border: 1px solid {MUTED}; "
        f"border-radius: {PANEL_RADIUS}px; padding: 4px 8px; }}"
    )


def transport_button_stylesheet() -> str:
    """Start, Pause and Reset in both states: PANEL fill, MUTED edge, INK or MUTED label.

    Declared rather than left to the platform style, which is what `PL-DHBX`
    was: a button that sets no foreground takes one from Qt's palette
    `ButtonText` role, and that role is the *host appearance's* value rather
    than this interface's. Under macOS Dark it is near-white, while every
    surface this interface draws around it stays the light theme's - so the
    labels went to white-on-white and the run controls could not be read.

    **Both states, because the project owner's screenshots showed the second
    half failing the same way.** The first fix declared `:enabled` only and
    left the disabled button whole to the platform, on `PL-NGF7`'s decision of
    2026-09-16 and on WCAG 2.2 SC 1.4.3's exemption for text in an inactive
    component. On `0.4.26+g22bc6d82` the disabled button was then the invisible
    one - Start while running, Pause while paused - which is the cost that
    decision's case did not carry: the platform's disabled grey is not merely
    low-contrast under a dark host appearance, it is absent. An exemption from
    a contrast *minimum* is not a licence for a control to disappear.

    So the disabled label is `MUTED`, which is **5.00:1 on PANEL** and clears
    SC 1.4.3's 4.5:1 for normal text outright. No exemption is claimed for it,
    which matters here: SC 1.4.11's own inactive-component wording has never
    been read at the source from this container (`PL-JX0Z`, `w3.org` is
    `EGRESS_BLOCKED`), so nothing in this interface may rest on it.

    **The two states are not separated by colour alone.** `.claude/rules/ui-color.md`
    judgment 2 asks for a second channel, and the row already carries one in
    text: `_status_text` beside these three says "Running" or "Paused", which
    is what decides which button is unavailable - `dashboard_frame.transport`
    derives both from the same flag. A reader who cannot resolve INK from MUTED
    reads the state from the word, not from the buttons.

    The edge stays `MUTED` in both states. It is what identifies the control's
    boundary - `PANEL` on `BACKGROUND` is 1.07:1, so the fill does not - and a
    user-interface component needs SC 1.4.11's 3:1, which `MUTED` meets at
    4.65:1 against the row behind it. Softening it for the disabled state would
    have bought a second visual channel at the price of the boundary.

    `tools/contrast_check.py` measures all three pairs, and
    `check_disabled_states_are_the_style_s` is what requires that: a
    `:disabled` rule is admitted only from a function a requirement cites.
    """

    return (
        f"QPushButton {{ background-color: {PANEL}; border: 1px solid {MUTED}; "
        f"border-radius: {PANEL_RADIUS}px; padding: 4px 12px; }} "
        f"QPushButton:enabled {{ color: {INK}; }} "
        f"QPushButton:disabled {{ color: {MUTED}; }}"
    )


class FlowLayout(QLayout):
    """A row of items that wraps onto further lines when the width runs out.

    The shape of Qt's documented Flow Layout example: items are laid left to
    right in the order added, each line as tall as its tallest item, and an
    item that would overrun the right edge starts the next line. The layout
    reports its height for a width, so the column above it grows the row as
    it narrows; it expands in neither direction; and its minimum is its
    widest single item, so nothing is ever laid outside it. The legend rows
    use it so that six compartment entries on one line cannot hold the whole
    chart column to their summed width (`PL-25KS`).
    """

    def __init__(
        self, *, horizontal_spacing: int, vertical_spacing: int, parent: QWidget | None = None
    ) -> None:
        """Build an empty row.

        Args:
            horizontal_spacing: The gap between neighbours on one line.
            vertical_spacing: The gap between lines.
            parent: The widget this layout manages, if it is the top layout.
        """

        super().__init__(parent)
        self._items: list[QLayoutItem] = []
        self._horizontal_spacing = horizontal_spacing
        self._vertical_spacing = vertical_spacing
        self.setContentsMargins(0, 0, 0, 0)

    def addItem(self, item: QLayoutItem) -> None:  # Qt spells this in camelCase.
        self._items.append(item)

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, index: int) -> QLayoutItem | None:  # Qt spells this in camelCase.
        if 0 <= index < len(self._items):
            return self._items[index]

        return None

    def takeAt(self, index: int) -> QLayoutItem | None:  # Qt spells this in camelCase.
        if 0 <= index < len(self._items):
            return self._items.pop(index)

        return None

    def expandingDirections(self) -> Qt.Orientation:  # Qt spells this in camelCase.
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:  # Qt spells this in camelCase.
        return True

    def heightForWidth(self, width: int) -> int:  # Qt spells this in camelCase.
        return self._lay_out(QRect(0, 0, width, 0), apply=False)

    def setGeometry(self, rect: QRect) -> None:  # Qt spells this in camelCase.
        super().setGeometry(rect)
        self._lay_out(rect, apply=True)

    def sizeHint(self) -> QSize:  # Qt spells this in camelCase.
        return self.minimumSize()

    def minimumSize(self) -> QSize:  # Qt spells this in camelCase.
        size = QSize()

        for item in self._laid_items():
            size = size.expandedTo(item.minimumSize())

        margins = self.contentsMargins()

        return size + QSize(margins.left() + margins.right(), margins.top() + margins.bottom())

    def _laid_items(self) -> list[QLayoutItem]:
        """The items this row actually places: everything but a hidden widget.

        A hidden widget is not on screen, so reserving its width would leave
        a gap in the row and push the entries after it onto a further line
        for nothing. Qt's own layouts skip one; this row is hand-written and
        has to do it explicitly. Rows whose entries appear and disappear -
        the chart legend's per-run entries, which stand down while one run is
        drawn - depend on it.
        """

        return [
            item
            for item in self._items
            if (widget := item.widget()) is None or not widget.isHidden()
        ]

    def _lay_out(self, rect: QRect, *, apply: bool) -> int:
        """Place the items inside `rect`, or only measure, and return the height used."""

        margins = self.contentsMargins()
        inner = rect.adjusted(margins.left(), margins.top(), -margins.right(), -margins.bottom())
        x = inner.x()
        y = inner.y()
        line_height = 0

        for item in self._laid_items():
            size = item.sizeHint()
            next_x = x + size.width() + self._horizontal_spacing

            if next_x - self._horizontal_spacing > inner.right() and line_height > 0:
                x = inner.x()
                y = y + line_height + self._vertical_spacing
                next_x = x + size.width() + self._horizontal_spacing
                line_height = 0

            if apply:
                item.setGeometry(QRect(QPoint(x, y), size))

            x = next_x
            line_height = max(line_height, size.height())

        return y + line_height - rect.y() + margins.bottom()


class MetricPanel(QFrame):
    """One readout: its name, its gloss, its value and its second unit.

    Four lines, always present, so every panel in the row is the same
    shape: a panel with no gloss draws `EMPTY_METRIC_QUALIFIER` and one
    with no second unit draws `EMPTY_METRIC_SECONDARY_VALUE`, and every
    reading sits on one baseline (`PL-8M05`). The gloss is smaller than the
    name and the second unit smaller than the value, because each is the
    weaker claim of its pair (`theme.METRIC_QUALIFIER_SIZE`,
    `theme.METRIC_SECONDARY_VALUE_SIZE`).

    The panel's minimum width is reserved at construction from the widest
    string each line can show, measured in that line's font, plus the
    panel's padding (`PL-3355`). No line wraps, so a layout that offers
    less than the reservation clips the panel's edge rather than moving a
    unit onto its own line; and the clock, the one value whose string
    changes length every tick, cannot shift its panel as components appear
    and fall away.

    Attributes:
        name_label: The modeled quantity, in the model's own terms.
        qualifier_label: What a clinician would compare it against.
        value_label: The reading with its unit; never wraps.
        secondary_label: The reading in its second unit; never wraps.
        minimum_value_width_px: The width reserved for the panel: the
            widest of the four lines' advances plus the padding on both
            sides.
    """

    def __init__(
        self,
        readout: Readout,
        *,
        widest_value: str,
        widest_secondary: str,
        parent: QWidget | None = None,
    ) -> None:
        """Build the panel and reserve its width.

        Args:
            readout: The four lines as drawn this tick.
            widest_value: The widest string the value line can show, from
                `dashboard_frame.WIDEST_READOUT_VALUE`.
            widest_secondary: The widest string the second-unit line can
                show, from `dashboard_frame.WIDEST_READOUT_SECONDARY`.
            parent: The Qt parent.
        """

        super().__init__(parent)
        self.setObjectName("metricPanel")
        self.setStyleSheet(_panel_stylesheet(self.objectName()))
        self.name_label = styled_label(readout.name, color=MUTED, size_px=METRIC_NAME_SIZE)
        self.qualifier_label = styled_label(
            readout.qualifier, color=MUTED, size_px=METRIC_QUALIFIER_SIZE, italic=True
        )
        self.value_label = styled_label(
            readout.value, color=INK, size_px=METRIC_VALUE_SIZE, bold=True
        )
        self.secondary_label = styled_label(
            readout.secondary, color=MUTED, size_px=METRIC_SECONDARY_VALUE_SIZE
        )

        value_advance = _advance_px(self.value_label, widest_value)
        secondary_advance = _advance_px(self.secondary_label, widest_secondary)
        self.value_label.setMinimumWidth(value_advance)
        self.secondary_label.setMinimumWidth(secondary_advance)
        self.minimum_value_width_px = (
            max(
                value_advance,
                secondary_advance,
                _advance_px(self.name_label, readout.name),
                _advance_px(self.qualifier_label, readout.qualifier),
            )
            + 2 * PANEL_PADDING
        )
        self.setMinimumWidth(self.minimum_value_width_px)

        column = QVBoxLayout(self)
        column.setContentsMargins(PANEL_PADDING, PANEL_PADDING, PANEL_PADDING, PANEL_PADDING)
        column.setSpacing(0)

        for label in (
            self.name_label,
            self.qualifier_label,
            self.value_label,
            self.secondary_label,
        ):
            column.addWidget(label)

    def set_readout(self, readout: Readout) -> None:
        """Write the four lines from this tick's readout.

        Args:
            readout: The four lines as drawn this tick.
        """

        self.name_label.setText(readout.name)
        self.qualifier_label.setText(readout.qualifier)
        self.value_label.setText(readout.value)
        self.secondary_label.setText(readout.secondary)


class ReadoutRow(QWidget):
    """The readout panels in a grid whose column count follows the row's width.

    The row reflows rather than squeezing a panel (`PL-8M05`): at each
    resize `dashboard_frame.readout_columns` says how many panels of the
    row's own measured reservation, with the grid's own spacing between
    them, fit the new width, and the grid is re-laid to that count with
    every column given equal stretch and the same minimum, so no panel is
    given more of the row than its neighbours and none is laid outside the
    row. Each column is held to the widest reservation of the panels it
    holds, so the clock's wide elapsed form does not cost the six
    compartment columns its width and seven stand across a laptop-wide
    row. The widths at which the count steps down are therefore the
    rendering font's rather than a recorded pixel ladder. The row's own
    minimum is one column's - the widest panel's reservation - rather than
    the grid's, because a row held at its seven-column minimum by a scroll
    area or a splitter could never receive the narrower resize that tells
    it to reflow; each panel keeps its own reservation, so no value wraps
    at any count (`PL-3355`).

    Attributes:
        panels: One `MetricPanel` per readout, in row order.
        panel_minimum_widths_px: Each panel's own reservation, in row
            order, so a column count's fit at a width can be checked
            against them.
        panel_minimum_width_px: The widest of those, which is the row's own
            minimum width.
    """

    def __init__(
        self,
        readouts: Sequence[Readout],
        *,
        reservations: Sequence[tuple[str, str]],
        parent: QWidget | None = None,
    ) -> None:
        """Build one panel per readout and lay them out for the current width.

        Args:
            readouts: The panels' lines as drawn this tick, in row order.
            reservations: Per panel, the widest value and the widest second
                line its column can show - `dashboard_frame.READOUT_RESERVATIONS`.
            parent: The Qt parent.

        Raises:
            ValueError: If there is not one reservation per readout, since a
                panel with no reservation could wrap its value.
        """

        super().__init__(parent)

        if len(reservations) != len(readouts):
            raise ValueError(
                f"{len(readouts)} readouts were given {len(reservations)} width reservations"
            )

        self.panels = tuple(
            MetricPanel(readout, widest_value=value, widest_secondary=secondary)
            for readout, (value, secondary) in zip(readouts, reservations, strict=True)
        )
        self.panel_minimum_widths_px = tuple(panel.minimum_value_width_px for panel in self.panels)
        self.panel_minimum_width_px = max(self.panel_minimum_widths_px)
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.setMinimumWidth(self.panel_minimum_width_px)
        self._columns = 0
        self._lay_out(self._columns_for(self.width()))

    def columns(self) -> int:
        """How many panels stand side by side at the row's current width."""

        return self._columns

    def set_readouts(self, readouts: Sequence[Readout]) -> None:
        """Write every panel from this tick's readouts.

        Args:
            readouts: One `Readout` per panel, in row order.

        Raises:
            ValueError: If `readouts` is not one per panel; a row written
                from the wrong count would leave a panel showing the
                previous tick beside six showing this one.
        """

        if len(readouts) != len(self.panels):
            raise ValueError(
                f"the readout row holds {len(self.panels)} panels and was given "
                f"{len(readouts)} readouts"
            )

        for panel, readout in zip(self.panels, readouts, strict=True):
            panel.set_readout(readout)

    def minimumSizeHint(self) -> QSize:  # Qt spells this in camelCase.
        """One column wide, and as tall as the grid is at its current count."""

        return QSize(self.panel_minimum_width_px, super().minimumSizeHint().height())

    def resizeEvent(self, event: QResizeEvent) -> None:  # Qt spells this in camelCase.
        super().resizeEvent(event)
        columns = self._columns_for(event.size().width())

        if columns != self._columns:
            self._lay_out(columns)

    def width_for(self, columns: int) -> int:
        """The narrowest row that seats the panels `columns` across, at their reservations."""

        return ceil(
            readout_row_width(columns, self.panel_minimum_widths_px, self._grid.horizontalSpacing())
        )

    def _columns_for(self, width_px: int) -> int:
        """The rung of the ladder whose panels fit `width_px` at their reservations."""

        return readout_columns(
            width_px, self.panel_minimum_widths_px, self._grid.horizontalSpacing()
        )

    def _lay_out(self, columns: int) -> None:
        """Seat the panels `columns` across, every column with equal stretch.

        A column's minimum is the widest reservation among the panels it
        holds; the stretch is equal, so any width beyond the minimums is
        shared equally and the columns are equal wherever there is room.
        """

        while self._grid.takeAt(0) is not None:
            pass

        for index, panel in enumerate(self.panels):
            self._grid.addWidget(panel, index // columns, index % columns)

        for column in range(max(columns, self._columns)):
            in_use = column < columns
            self._grid.setColumnStretch(column, 1 if in_use else 0)
            self._grid.setColumnMinimumWidth(
                column, max(self.panel_minimum_widths_px[column::columns]) if in_use else 0
            )

        self._columns = columns


class ParameterSlider(QWidget):
    """One setting: its name, its gloss, an integer slider and the value beside it.

    The slider spans `slider_position(minimum)` to `slider_position(maximum)`
    in steps of one count, and a count is the control's display resolution,
    so the value it emits and the value printed beside it are one number
    (`PL-25KS`, decision D4). The value label is the snapshot's own text,
    written by `set_setting`, so a refused setting leaves the control
    reading what the simulation is actually running at.

    The value label's width only grows: reserved from the text it is first
    given and widened when a longer one arrives, never narrowed, so the
    slider beside it does not shorten under a pointer mid-drag as the
    printed value loses a digit.

    Attributes:
        slider: The integer slider.
        name_label: The setting's name.
        qualifier_label: The gloss under the name, hidden where the setting
            has none: no spacer holds the line open, because the four
            controls are of unequal height by design (`SettingReadout`),
            the delivered dial alone carrying a second line for its MAC
            multiple.
        value_label: The setting as the snapshot prints it.
        secondary_label: The setting in its second unit, shown only where
            the setting has one - the delivered dial's MAC line.
        adjustment_started: Emitted when the reader presses the thumb, so
            the run can mark one adjustment before the values arrive.
        value_changed: Emitted with the decoded value each time the slider
            moves under the reader; never by `set_setting`.
    """

    adjustment_started = Signal()
    value_changed = Signal(float)

    def __init__(self, setting: SettingReadout, parent: QWidget | None = None) -> None:
        """Build the control and write it from `setting`.

        Args:
            setting: The control as drawn this tick.
            parent: The Qt parent.
        """

        super().__init__(parent)
        self.setObjectName("parameterPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(_panel_stylesheet(self.objectName()))
        self._decimals = setting.decimals
        self.name_label = styled_label(setting.name, color=INK, bold=True)
        self.qualifier_label = styled_label(
            setting.qualifier, color=MUTED, size_px=PARAMETER_QUALIFIER_SIZE, italic=True
        )
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setSingleStep(1)
        self.slider.setPageStep(1)
        self.slider.setStyleSheet(_slider_stylesheet())
        self.value_label = styled_label(setting.value_text, color=INK)
        self.secondary_label = styled_label(
            setting.secondary, color=MUTED, size_px=METRIC_SECONDARY_VALUE_SIZE
        )

        column = QVBoxLayout(self)
        column.setContentsMargins(PANEL_PADDING, PANEL_PADDING, PANEL_PADDING, PANEL_PADDING)
        column.addWidget(self.name_label)
        column.addWidget(self.qualifier_label)
        row = QHBoxLayout()
        row.addWidget(self.slider, 1)
        row.addWidget(self.value_label)
        column.addLayout(row)
        column.addWidget(self.secondary_label)

        self.slider.sliderPressed.connect(self.adjustment_started.emit)
        self.slider.valueChanged.connect(self._on_slider_moved)
        self.set_setting(setting)

    def set_setting(self, setting: SettingReadout) -> None:
        """Write the range, position and text from this tick's setting.

        The slider's signals are blocked while it is written, so a value
        that came *from* the snapshot is never applied back to it: that
        would record a control change the reader did not make.

        Args:
            setting: The control as drawn this tick.
        """

        self._decimals = setting.decimals
        self.name_label.setText(setting.name)
        self.qualifier_label.setText(setting.qualifier)
        self.qualifier_label.setHidden(not setting.qualifier)

        with QSignalBlocker(self.slider):
            self.slider.setRange(
                slider_position(setting.minimum, setting.decimals),
                slider_position(setting.maximum, setting.decimals),
            )
            self.slider.setValue(slider_position(setting.value, setting.decimals))

        self.value_label.setText(setting.value_text)
        self.value_label.setMinimumWidth(
            max(self.value_label.minimumWidth(), _advance_px(self.value_label, setting.value_text))
        )
        self.secondary_label.setText(setting.secondary)
        self.secondary_label.setHidden(not setting.secondary)

    def value(self) -> float:
        """The value the slider's position stands for, in the setting's unit."""

        return slider_value(self.slider.value(), self._decimals)

    def _on_slider_moved(self, position: int) -> None:
        self.value_changed.emit(slider_value(position, self._decimals))


class NoticeLabel(QLabel):
    """The banner above a run's values: a stopped run or a refused setting, or nothing.

    Word-wrapped, bold and in `theme.WARNING`, the one signal this interface
    has. Hidden rather than blank when there is nothing to say, so an empty
    line never holds the space a warning would.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"color: {WARNING};")
        self.setWordWrap(True)
        font = QFont(self.font())
        font.setBold(True)
        self.setFont(font)
        self._notice: str | None = None
        self.set_notice(None)

    def set_notice(self, text: str | None) -> None:
        """Show `text`, or hide the banner when there is none.

        Args:
            text: `dashboard_frame.notice`'s result this tick.
        """

        self._notice = text
        self.setText(text if text is not None else "")
        self.setHidden(text is None)

    def notice(self) -> str | None:
        """The banner's text, or None while it is hidden."""

        return self._notice


class NewCaseDialog(QDialog):
    """The confirmation asked before a recorded run is discarded for a new agent.

    Destructive first, safe last: the discard button is drawn first and
    outlined, and the keep button last and filled, and only the keep button
    is the default, so the press a reader makes without reading - Return,
    or the trailing action - keeps their case, and Escape or closing the
    dialog does the same. `accept()` therefore means "discard and start
    the new case" and `reject()` means "keep"; the run connects to
    `finished` and reads which. Modal, so the run's controls cannot be
    reached around a question about that run. Shown with `open()` and
    never `exec()`, so a test can drive `accept()` and `reject()` itself.

    The surface is `theme.PANEL`, set rather than left to the platform, so
    the title's INK, the discard line's WARNING and the carry-over line's
    MUTED stand on the surface `tools/contrast_check.py` measures them
    against (`PL-R3KB`).

    Attributes:
        title_label: Names the agent the reader would start.
        body_labels: The three statements, in the order a reader meets
            them: INK, then the discard warning in bold WARNING, then the
            carry-over line in MUTED.
        discard_button: The destructive action; `clicked` runs `accept()`.
        keep_button: The safe action and the default; `clicked` runs
            `reject()`.
    """

    def __init__(self, question: NewCaseQuestion, parent: QWidget | None = None) -> None:
        """Build the dialog from one question.

        Args:
            question: `dashboard_frame.new_case_question`'s text.
            parent: The window the dialog is modal to.
        """

        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle(question.title)
        self.setStyleSheet(f"QDialog {{ background-color: {PANEL}; }}")
        self.title_label = styled_label(question.title, color=INK, bold=True, wrap=True)
        opening, discard_warning, carry_over = question.body
        self.body_labels = (
            styled_label(opening, color=INK, wrap=True),
            styled_label(discard_warning, color=WARNING, bold=True, wrap=True),
            styled_label(carry_over, color=MUTED, wrap=True),
        )
        self.discard_button = QPushButton(question.discard_label)
        self.discard_button.setAutoDefault(False)
        self.discard_button.setDefault(False)
        self.discard_button.setStyleSheet(
            f"QPushButton {{ color: {INK}; background-color: {PANEL}; "
            f"border: 1px solid {INK}; border-radius: {PANEL_RADIUS}px; padding: 6px 12px; }}"
        )
        self.keep_button = QPushButton(question.keep_label)
        self.keep_button.setDefault(True)
        self.keep_button.setStyleSheet(
            f"QPushButton {{ color: {PANEL}; background-color: {PRIMARY}; "
            f"border: 1px solid {PRIMARY}; border-radius: {PANEL_RADIUS}px; padding: 6px 12px; }}"
        )

        column = QVBoxLayout(self)
        column.setSpacing(NEW_CASE_DIALOG_SPACING)
        column.addWidget(self.title_label)

        for label in self.body_labels:
            label.setFixedWidth(NEW_CASE_DIALOG_WIDTH)
            column.addWidget(label)

        actions = QHBoxLayout()
        actions.addStretch(1)
        actions.addWidget(self.discard_button)
        actions.addWidget(self.keep_button)
        column.addLayout(actions)

        self.discard_button.clicked.connect(self.accept)
        self.keep_button.clicked.connect(self.reject)


class MarkListingLabel(QWidget):
    """One bookmark collection, drawn read-only: a heading and its rows.

    Two of these rather than one widget holding both collections, because the
    two are listed apart (`PL-LPLD`) and a widget that knew there were exactly
    two of them could not be placed anywhere a third kind was wanted. It is
    given a `MarkListing` and decides nothing: which of the rows and the empty
    line is drawn is settled in `dashboard_frame.MarkListing.text`, where a
    test can read it without a display.

    Attributes:
        heading_label: The collection's name.
        rows_label: The rows, or the line that stands in for them when the
            collection is empty.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.heading_label = styled_label("", color=INK, bold=True)
        self.rows_label = styled_label("", color=MUTED, size_px=METRIC_QUALIFIER_SIZE, wrap=True)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(BOOKMARK_ROW_SPACING)
        column.addWidget(self.heading_label)
        column.addWidget(self.rows_label)

    def set_listing(self, listing: MarkListing) -> None:
        """Draw `listing`, heading and rows both.

        Args:
            listing: One of `dashboard_frame.bookmark_panel`'s two listings.
        """

        self.heading_label.setText(listing.heading)
        self.rows_label.setText(listing.text)


class BookmarksPanel(QWidget):
    """The two collections beside the chart, with the control that opens the editor.

    Read-only. Marks are created and removed in `BookmarkDialog`, so the
    panel a reader has in front of them while a case runs states what is
    marked and offers nothing that could change a run by a mis-click.

    Attributes:
        times: The marked instants.
        targets: The marked heights.
        edit_button: Opens the dialog; `clicked` is connected by the view.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.times = MarkListingLabel()
        self.targets = MarkListingLabel()
        self.edit_button = QPushButton(EDIT_BOOKMARKS_LABEL)
        self.edit_button.setStyleSheet(_outlined_button_stylesheet())
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(BOOKMARK_SECTION_SPACING)
        column.addWidget(self.times)
        column.addWidget(self.targets)
        actions = QHBoxLayout()
        actions.addWidget(self.edit_button)
        actions.addStretch(1)
        column.addLayout(actions)

    def set_panel(self, panel: BookmarkPanel) -> None:
        """Draw both collections from one tick's answer.

        Args:
            panel: `dashboard_frame.bookmark_panel`'s result this tick.
        """

        self.times.set_listing(panel.times)
        self.targets.set_listing(panel.targets)


class BookmarkDialog(QDialog):
    """Where the two kinds of mark are created, listed and removed.

    One dialog over two mechanisms, which is the shape the reference
    simulator uses and what `PL-LPLD` was scoped on. Both forms are visible
    at once and each has its own add button: a tab or a kind selector would
    make which mechanism is armed a mode, and the two collections differ in
    their fields rather than in a flavour, so there is nothing for a shared
    form to hold.

    Non-modal, and shown with `open()` rather than `exec()` so a test can
    drive it. Non-modal deliberately: a run may be playing, and a modal
    window over a moving chart is a reader locked out of the transport
    controls by a window about something else.

    **The height a target may be set to is bounded by the running agent**,
    and the bound is here rather than on `MacTarget` because it is the
    agent's rather than the mark's. No compartment can exceed the delivered
    concentration, and the vaporizer's own maximum bounds that, so a target
    above `max_delivered_concentration_percent / agent_mac_percent` is one no
    run of this agent could ever cross. Refusing it in the control is
    `.claude/rules/expert-review.md`'s preference for an interface that
    prevents the error over one that reports it afterwards - and it moves
    with the agent, because the two values it is computed from do.

    Attributes:
        instant_spin: The instant to mark, in seconds.
        instant_preview: That instant in the compound form the clock uses, so
            no reader converts between the entry and the display.
        time_label_edit: The optional name for a time bookmark.
        add_time_button: Adds the time bookmark; `clicked` is the view's.
        time_list: The marked instants, selectable for removal.
        remove_time_button: Removes the selected instant.
        compartment_combo: Which compartment a target is read against.
        height_spin: The height, in multiples of the running agent's 1 MAC.
        direction_combo: Which crossing counts.
        target_label_edit: The optional name for a target.
        add_target_button: Adds the target.
        target_list: The marked heights, selectable for removal.
        remove_target_button: Removes the selected target.
        notice: What a refused add says, or hidden when there is nothing.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(BOOKMARK_DIALOG_TITLE)
        self.setStyleSheet(f"QDialog {{ background-color: {PANEL}; }}")
        self.setMinimumWidth(BOOKMARK_DIALOG_WIDTH)

        self.instant_spin = QDoubleSpinBox()
        self.instant_spin.setDecimals(INSTANT_ENTRY_DECIMALS)
        self.instant_spin.setSingleStep(INSTANT_ENTRY_STEP_S)
        self.instant_spin.setRange(0.0, MAXIMUM_ELAPSED_SIMULATION_TIME_S)
        self.instant_spin.setSuffix(INSTANT_ENTRY_SUFFIX)
        self.instant_preview = styled_label(
            format_elapsed(0.0), color=MUTED, size_px=METRIC_QUALIFIER_SIZE
        )
        self.instant_spin.valueChanged.connect(self._refresh_instant_preview)
        self.time_label_edit = QLineEdit()
        self.time_label_edit.setPlaceholderText(MARK_NAME_PLACEHOLDER)
        self.add_time_button = QPushButton(ADD_MARK_LABEL)
        self.time_list = QListWidget()
        self.remove_time_button = QPushButton(REMOVE_MARK_LABEL)

        self.compartment_combo = QComboBox()

        for quantity in COMPARTMENT_QUANTITIES:
            self.compartment_combo.addItem(trace_style(quantity).label, userData=quantity.value)

        self.height_spin = QDoubleSpinBox()
        self.height_spin.setDecimals(MAC_DISPLAY_DECIMALS)
        self.height_spin.setSingleStep(MAC_DISPLAY_RESOLUTION_MAC)
        self.height_spin.setSuffix(MAC_UNIT_SUFFIX)
        self.direction_combo = QComboBox()

        for direction, word in CROSSING_DIRECTION_WORDS.items():
            self.direction_combo.addItem(word, userData=direction.value)

        self.target_label_edit = QLineEdit()
        self.target_label_edit.setPlaceholderText(MARK_NAME_PLACEHOLDER)
        self.add_target_button = QPushButton(ADD_MARK_LABEL)
        self.target_list = QListWidget()
        self.remove_target_button = QPushButton(REMOVE_MARK_LABEL)

        self.notice = NoticeLabel()
        self.close_button = QPushButton(CLOSE_BOOKMARKS_LABEL)
        self.close_button.setDefault(True)
        self.close_button.setStyleSheet(_filled_button_stylesheet())
        self.close_button.clicked.connect(self.accept)

        for button in (
            self.add_time_button,
            self.remove_time_button,
            self.add_target_button,
            self.remove_target_button,
        ):
            button.setAutoDefault(False)
            button.setStyleSheet(_outlined_button_stylesheet())

        self._build_layout()
        self.set_reachable_height(DEFAULT_MAXIMUM_TARGET_MAC)

    def _build_layout(self) -> None:
        """Lay the two forms out one above the other, each over its own list."""

        column = QVBoxLayout(self)
        column.setSpacing(BOOKMARK_SECTION_SPACING)

        times = QGridLayout()
        times.addWidget(styled_label(TIME_BOOKMARK_HEADING, color=INK, bold=True), 0, 0, 1, 3)
        times.addWidget(styled_label(INSTANT_FIELD_LABEL, color=MUTED), 1, 0)
        times.addWidget(self.instant_spin, 1, 1)
        times.addWidget(self.instant_preview, 1, 2)
        times.addWidget(styled_label(MARK_NAME_FIELD_LABEL, color=MUTED), 2, 0)
        times.addWidget(self.time_label_edit, 2, 1, 1, 2)
        times.addWidget(self.add_time_button, 3, 1)
        times.addWidget(self.time_list, 4, 0, 1, 3)
        times.addWidget(self.remove_time_button, 5, 1)
        column.addLayout(times)

        targets = QGridLayout()
        targets.addWidget(styled_label(MAC_TARGET_HEADING, color=INK, bold=True), 0, 0, 1, 3)
        targets.addWidget(styled_label(COMPARTMENT_FIELD_LABEL, color=MUTED), 1, 0)
        targets.addWidget(self.compartment_combo, 1, 1, 1, 2)
        targets.addWidget(styled_label(HEIGHT_FIELD_LABEL, color=MUTED), 2, 0)
        targets.addWidget(self.height_spin, 2, 1)
        targets.addWidget(styled_label(DIRECTION_FIELD_LABEL, color=MUTED), 3, 0)
        targets.addWidget(self.direction_combo, 3, 1, 1, 2)
        targets.addWidget(styled_label(MARK_NAME_FIELD_LABEL, color=MUTED), 4, 0)
        targets.addWidget(self.target_label_edit, 4, 1, 1, 2)
        targets.addWidget(self.add_target_button, 5, 1)
        targets.addWidget(self.target_list, 6, 0, 1, 3)
        targets.addWidget(self.remove_target_button, 7, 1)
        column.addLayout(targets)

        column.addWidget(self.notice)
        actions = QHBoxLayout()
        actions.addStretch(1)
        actions.addWidget(self.close_button)
        column.addLayout(actions)

    def _refresh_instant_preview(self, seconds: float) -> None:
        """Restate the entered instant in the form the clock and the axis use."""

        self.instant_preview.setText(format_elapsed(seconds))

    def set_reachable_height(self, maximum_mac: float) -> None:
        """Bound the height control at what the running agent can actually reach.

        Args:
            maximum_mac: The agent's maximum delivered concentration as a
                multiple of its own 1 MAC. The floor is one count of the
                displayed resolution, because a target at zero is one every
                run stands on before it begins.
        """

        self.height_spin.setRange(MAC_DISPLAY_RESOLUTION_MAC, maximum_mac)

    def set_panel(self, panel: BookmarkPanel) -> None:
        """Redraw both lists from one tick's answer, keeping each selection.

        The rows are the same strings the panel beside the chart draws, from
        the same `dashboard_frame` call, so a reader moving between the two
        is reading one listing in two places rather than two listings.

        Args:
            panel: `dashboard_frame.bookmark_panel`'s result this tick.
        """

        _refill(self.time_list, panel.times.rows)
        _refill(self.target_list, panel.targets.rows)

    def selected_time_index(self) -> int:
        """Which marked instant is selected, or -1 for none."""

        return self.time_list.currentRow()

    def selected_target_index(self) -> int:
        """Which marked height is selected, or -1 for none."""

        return self.target_list.currentRow()

    def entered_time_bookmark(self) -> TimeBookmark:
        """The time bookmark the form currently describes.

        Raises:
            SimulationConfigurationError: If the entered instant or name is
                one `TimeBookmark` refuses.
        """

        return TimeBookmark(self.instant_spin.value(), _entered_label(self.time_label_edit))

    def entered_mac_target(self) -> MacTarget:
        """The MAC target the form currently describes.

        Raises:
            SimulationConfigurationError: If the entered height or name is one
                `MacTarget` refuses.
        """

        return MacTarget(
            RecordedQuantity(self.compartment_combo.currentData()),
            MacMultiple(self.height_spin.value()),
            CrossingDirection(self.direction_combo.currentData()),
            _entered_label(self.target_label_edit),
        )

    def clear_entry(self) -> None:
        """Empty the two name fields, for a mark that has just been added.

        The instant, compartment, height and direction are left where they
        are: adding a second mark near the first is the common case, and a
        control that reset itself would make the second entry the longer one.
        A name is cleared because reusing one would name two marks alike.
        """

        self.time_label_edit.clear()
        self.target_label_edit.clear()


def _entered_label(field: QLineEdit) -> str | None:
    """What a name field says, or `None` where the reader left it empty.

    An empty field means "list it under its own value" rather than "name it
    nothing", which is the distinction `bookmarks.TimeBookmark` refuses a
    blank string in order to keep.
    """

    entered = field.text().strip()

    return entered or None


def _refill(widget: QListWidget, rows: Sequence[str]) -> None:
    """Rewrite `widget`'s rows, leaving the selected position where it was.

    Qt clears the current row when the model empties, so the index is read
    back afterwards rather than trusted across the rewrite. A selection that
    no longer exists - the row a reader has just removed - lands on nothing,
    which is what a reader expects of a list they have just shortened.
    """

    selected = widget.currentRow()

    with QSignalBlocker(widget):
        widget.clear()
        widget.addItems(list(rows))

        if 0 <= selected < widget.count():
            widget.setCurrentRow(selected)


def _outlined_button_stylesheet() -> str:
    """The secondary action: INK on PANEL inside an INK border.

    The same pair `NewCaseDialog`'s discard button draws, which
    `tools/contrast_check.py` already measures, so these buttons declare no
    colour of their own.
    """

    return (
        f"QPushButton {{ color: {INK}; background-color: {PANEL}; "
        f"border: 1px solid {INK}; border-radius: {PANEL_RADIUS}px; padding: 6px 12px; }}"
    )


def _filled_button_stylesheet() -> str:
    """The primary action: PANEL on PRIMARY, as `NewCaseDialog`'s keep button draws."""

    return (
        f"QPushButton {{ color: {PANEL}; background-color: {PRIMARY}; "
        f"border: 1px solid {PRIMARY}; border-radius: {PANEL_RADIUS}px; padding: 6px 12px; }}"
    )


def inert_splitter(orientation: Qt.Orientation, widgets: Sequence[QWidget]) -> QSplitter:
    """A splitter whose sections a reader cannot yet drag.

    Every surface of the dashboard is an independent widget inside nested
    splitters (`PL-25KS`), so that a later item can let a reader resize
    them by enabling the handles. Until then the handles are disabled and
    show the arrow cursor, and no section can be collapsed: a readout row
    dragged to nothing would be a display that appears to have failed.
    The handles stay visible so the sections read as sections.

    Args:
        orientation: Which way the sections stack.
        widgets: The sections, in order.

    Returns:
        The splitter, with `widgets` added.
    """

    splitter = QSplitter(orientation)
    splitter.setChildrenCollapsible(False)

    for widget in widgets:
        splitter.addWidget(widget)

    for index in range(1, splitter.count()):
        handle = splitter.handle(index)
        handle.setEnabled(False)
        handle.setCursor(Qt.CursorShape.ArrowCursor)

    return splitter


def initial_window_geometry(available: QRect, minimum: QSize, fraction: float) -> QRect:
    """Where the window opens: a fraction of the available screen, centred, never below its minimum.

    Sized from the screen rather than from a pixel count, so the window is
    fully visible on every display and never full-screen (`PL-005`). A
    minimum wider or taller than the fraction wins, because a window that
    cannot show its own content is worse than one that overhangs the
    screen; it is still centred on the available area.

    Args:
        available: The screen's available geometry - what is left after
            the platform's own bars.
        minimum: The window's minimum size, from its own size hint.
        fraction: How much of `available`'s width and height to take,
            above zero and at most one.

    Returns:
        The window's frame geometry.

    Raises:
        ValueError: If `fraction` is not above zero and at most one: a
            zero-sized or larger-than-the-screen window is not a size to
            open at.
    """

    if not 0.0 < fraction <= 1.0:
        raise ValueError(
            f"a window opens on a fraction of the screen above zero and at most one, "
            f"not {fraction!r}"
        )

    width = max(round(available.width() * fraction), minimum.width())
    height = max(round(available.height() * fraction), minimum.height())
    left = available.x() + (available.width() - width) // 2
    top = available.y() + (available.height() - height) // 2

    return QRect(left, top, width, height)
