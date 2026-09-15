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
the next. The reservation is measured rather than declared: it supersedes
`theme.ELAPSED_VALUE_WIDTH`, which was the Flet build's fixed guess at the
clock's width and is no longer read.

**A slider position is a printed value** (`PL-25KS`, decision D4). The four
sliders are integer `QSlider`s whose one step is the control's display
resolution, decoded through `dashboard_frame.slider_value`, so the number
applied to the model is exactly the number beside the thumb.

**Every colour is `app/theme.py`'s**, reaching a stylesheet as an f-string
over the theme name (decision D10), so `tools/contrast_check.py`'s palette
is the palette drawn. The few bare pixel spacings inside stylesheets are the
interim decision D9 accepts; `PL-L9RD` names the spacing scale that replaces
them.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Final

from PySide6.QtCore import QRect, QSignalBlocker, QSize, Qt, Signal
from PySide6.QtGui import QFont, QFontMetrics, QResizeEvent
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QSlider,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from anesthesia_sim.app.dashboard_frame import (
    EMPTY_METRIC_QUALIFIER,
    NewCaseQuestion,
    Readout,
    SettingReadout,
    readout_columns,
    slider_position,
    slider_value,
)
from anesthesia_sim.app.theme import (
    ACCENT,
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
    and fall away. `theme.ELAPSED_VALUE_WIDTH` was the Flet build's fixed
    guess at the same reservation and is superseded by this measurement.

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
    resize `dashboard_frame.readout_columns` says how many panels stand
    side by side, and the grid is re-laid to that count with every column
    given equal stretch and the same minimum, so no panel is given more of
    the row than its neighbours. The layout imposes no minimum on the row
    itself, because a row held at its seven-column minimum could never
    receive the narrower resize that tells it to reflow.

    Attributes:
        panels: One `MetricPanel` per readout, in row order.
        panel_minimum_width_px: The minimum every column is held to - the
            widest of the panels' own reservations - so a column count's
            fit at a width can be checked against it.
    """

    def __init__(
        self,
        readouts: Sequence[Readout],
        *,
        widest_value: str,
        widest_secondary: str,
        parent: QWidget | None = None,
    ) -> None:
        """Build one panel per readout and lay them out for the current width.

        Args:
            readouts: The panels' lines as drawn this tick, in row order.
            widest_value: `dashboard_frame.WIDEST_READOUT_VALUE`.
            widest_secondary: `dashboard_frame.WIDEST_READOUT_SECONDARY`.
            parent: The Qt parent.
        """

        super().__init__(parent)
        self.panels = tuple(
            MetricPanel(readout, widest_value=widest_value, widest_secondary=widest_secondary)
            for readout in readouts
        )
        self.panel_minimum_width_px = max(panel.minimum_value_width_px for panel in self.panels)
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self._columns = 0
        self._lay_out(readout_columns(self.width()))

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

    def resizeEvent(self, event: QResizeEvent) -> None:  # Qt spells this in camelCase.
        super().resizeEvent(event)
        columns = readout_columns(event.size().width())

        if columns != self._columns:
            self._lay_out(columns)

    def _lay_out(self, columns: int) -> None:
        """Seat the panels `columns` across, every column equal."""

        while self._grid.takeAt(0) is not None:
            pass

        for index, panel in enumerate(self.panels):
            self._grid.addWidget(panel, index // columns, index % columns)

        for column in range(max(columns, self._columns)):
            in_use = column < columns
            self._grid.setColumnStretch(column, 1 if in_use else 0)
            self._grid.setColumnMinimumWidth(column, self.panel_minimum_width_px if in_use else 0)

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
        qualifier_label: The gloss under the name, or `EMPTY_METRIC_QUALIFIER`
            where the setting has none, so the four sliders sit level.
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
            EMPTY_METRIC_QUALIFIER, color=MUTED, size_px=PARAMETER_QUALIFIER_SIZE, italic=True
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
        self.qualifier_label.setText(
            setting.qualifier if setting.qualifier else EMPTY_METRIC_QUALIFIER
        )

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
