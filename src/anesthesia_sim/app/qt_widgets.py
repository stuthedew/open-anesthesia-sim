"""The dashboard's leaf widgets, which show what `dashboard_frame` gives them and decide nothing.

These are the Qt widgets for everything on the dashboard that is not a plot:
a readout panel and the row of panels, a setting slider, the notice banner,
the new-case confirmation and the window's opening geometry. Each widget is
written from a `dashboard_frame` value, such as a `Readout`, a
`SettingReadout` or a `NewCaseQuestion`. A widget reads nothing from the
simulation, formats no number and never chooses between two strings. So
every claim a reader sees stays where `tests/unit/test_dashboard_frame.py`
can test it without a display (`PL-25KS`, decision D2). What a widget does
own is layout arithmetic: how wide a panel must be, how many columns a row
gets at a given width, and where the window opens.

**A readout value never wraps away from its unit** (`PL-3355`). Each of a
panel's four lines is a `QLabel` without word wrap. The panel reserves its
width once, from the font-metric advance of the widest string its column
can show. So no window width can put "0.13" on one line and "%" on the
next. The reservation is measured rather than declared. The Flet build used
a fixed guess at the clock's width, `theme.ELAPSED_VALUE_WIDTH`, and that
guess was retired with the port (`PL-25KS`).

**A slider position is a printed value** (`PL-25KS`, decision D4). The four
sliders are integer `QSlider`s. One step of a slider is the control's
display resolution, and a position is decoded through
`dashboard_frame.slider_value`. So the number applied to the model is
exactly the number beside the thumb.

**A row that has to wrap wraps here.** Qt ships no wrapping row. The Flet
build wrapped its legend rows (`ft.Row(wrap=True)`). Laid out without
wrapping, each of those rows became one unbreakable line of six checkboxes.
Those lines held the chart column to 1220 px and pushed the sidebar off a
1400 px window.
`FlowLayout` follows the shape of Qt's documented Flow Layout example, and
`qt_chart` lays out every legend row in one.

**Every colour comes from `app/theme.py`** (decision D10, `PL-Y4YX`). A
colour reaches a widget through a stylesheet that `app/stylesheets.py`
composes from the theme name. So the palette that `tools/contrast_check.py`
checks is the palette drawn. A colour for a palette role that no stylesheet
can reach is declared on the palette instead, by
`declare_interface_colours`.
"""

from __future__ import annotations

from collections.abc import Sequence
from math import ceil
from typing import Final

from PySide6.QtCore import QPoint, QRect, QSignalBlocker, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPalette, QResizeEvent
from PySide6.QtWidgets import (
    QApplication,
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
    QStyle,
    QStyleOptionComboBox,
    QVBoxLayout,
    QWidget,
)

from anesthesia_sim.app.bookmarks import MacTarget, TimeBookmark
from anesthesia_sim.app.chart_frame import trace_style
from anesthesia_sim.app.dashboard_frame import (
    ADD_MARK_LABEL,
    BOOKMARK_DIALOG_TITLE,
    CLOSE_BOOKMARKS_LABEL,
    COMPARTMENT_FIELD_LABEL,
    DEFAULT_MAXIMUM_TARGET_MAC,
    EDIT_BOOKMARKS_LABEL,
    FORK_HEADING,
    FORK_POINT_LABEL,
    HEIGHT_FIELD_LABEL,
    INSTANT_ENTRY_DECIMALS,
    INSTANT_ENTRY_STEP_S,
    INSTANT_ENTRY_SUFFIX,
    INSTANT_FIELD_LABEL,
    MAC_TARGET_HEADING,
    MARK_NAME_FIELD_LABEL,
    MARK_NAME_PLACEHOLDER,
    REMOVE_MARK_LABEL,
    TAKE_FORK_LABEL,
    TIME_BOOKMARK_HEADING,
    BookmarkPanel,
    ForkOffer,
    ForkPoint,
    MarkListing,
    NewCaseQuestion,
    Readout,
    SettingReadout,
    readout_columns,
    readout_row_width,
    slider_position,
    slider_value,
    widest_fork_point_label,
)
from anesthesia_sim.app.formatting import (
    MAC_DISPLAY_DECIMALS,
    MAC_DISPLAY_RESOLUTION_MAC,
    MAC_UNIT_SUFFIX,
    format_elapsed,
)
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity
from anesthesia_sim.app.stylesheets import (
    filled_button_stylesheet,
    foreground_stylesheet,
    outlined_button_stylesheet,
    panel_stylesheet,
    selector_stylesheet,
    slider_stylesheet,
)
from anesthesia_sim.app.theme import (
    BOOKMARK_DIALOG_WIDTH,
    BOOKMARK_LIST_MAX_HEIGHT,
    BOOKMARK_ROW_SPACING,
    BOOKMARK_SECTION_SPACING,
    CONTROL_ROW_SPACING,
    INK,
    MARK_ROW_BULLET,
    MARK_ROW_BULLET_SPACING,
    MARK_ROW_SPACING,
    METRIC_NAME_SIZE,
    METRIC_QUALIFIER_SIZE,
    METRIC_SECONDARY_VALUE_SIZE,
    METRIC_VALUE_SIZE,
    MUTED,
    NEW_CASE_DIALOG_SPACING,
    NEW_CASE_DIALOG_WIDTH,
    PANEL,
    PANEL_PADDING,
    PARAMETER_QUALIFIER_SIZE,
    PRIMARY,
    WARNING,
)
from anesthesia_sim.core.concentration import MacMultiple
from anesthesia_sim.core.supported_ranges import MAXIMUM_ELAPSED_SIMULATION_TIME_S, CaseInstant

# The fraction of the screen's available area that the window's normal geometry
# takes (`PL-005`). The window opens maximized (`PL-Z4K6`), so the normal
# geometry is what a reader gets back on un-maximizing. It is a fraction rather
# than a size, so the same rule gives a window that is fully visible on every
# display. It is never full screen, because full screen hides the window
# controls on some platforms.
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
        color: The value of a `theme.py` colour name. It is applied to the
            label through `foreground_stylesheet`, never as a literal.
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
    style_label(label, color=color, size_px=size_px, bold=bold, italic=italic, wrap=wrap)

    return label


def style_label(
    label: QLabel,
    *,
    color: str,
    size_px: int | None = None,
    bold: bool = False,
    italic: bool = False,
    wrap: bool = False,
) -> None:
    """Give a label one of the theme's colours and sizes, as `styled_label` does.

    Use this for a class that is itself a label, which `styled_label` cannot
    build. The arguments are the same as `styled_label`'s.
    """

    label.setStyleSheet(foreground_stylesheet(color))
    label.setWordWrap(wrap)
    font = QFont(label.font())

    if size_px is not None:
        font.setPixelSize(size_px)

    font.setBold(bold)
    font.setItalic(italic)
    label.setFont(font)


def _advance_px(label: QLabel, text: str) -> int:
    """How wide `text` is in `label`'s font, in logical pixels."""

    return QFontMetrics(label.font()).horizontalAdvance(text)


def _fix_width_to_entry(selector: QComboBox, entry: str) -> None:
    """Fix `selector`'s width so that `entry` fits whole in its text field.

    The width is the entry's advance, its drawn width in the selector's
    font, plus whatever the style draws around the text field: the frame,
    the padding and the arrow. The code asks the style for that margin
    around a field exactly as wide as the entry. So the width stays correct
    in whatever font face and size the selector is drawn in (`PL-NC0D`).

    Args:
        selector: The selector, with its stylesheet already set.
        entry: The widest entry it must show whole.
    """

    selector.ensurePolished()
    entry_px = selector.fontMetrics().horizontalAdvance(entry)
    option = QStyleOptionComboBox()
    selector.initStyleOption(option)
    option.rect = QRect(0, 0, entry_px, selector.sizeHint().height())
    field = selector.style().subControlRect(
        QStyle.ComplexControl.CC_ComboBox, option, QStyle.SubControl.SC_ComboBoxEditField, selector
    )
    selector.setFixedWidth(entry_px + entry_px - field.width())


#: The palette roles this interface declares, and the `app/theme.py` colour
#: declared for each. `Base` and `Text` paint an entry's fill and the text
#: typed into it, a list's rows, and a check box's indicator and its tick.
#: `Button` and `ButtonText` paint a spin box's steppers and their arrows.
#: `PlaceholderText` paints the word shown where no name has been typed yet.
#: `Highlight` and `HighlightedText` paint a selected row. `Window` and
#: `WindowText` paint the surface a dialog draws, and anything on it that
#: declares no colour of its own.
_DECLARED_ROLES: Final = (
    (QPalette.ColorRole.Window, PANEL),
    (QPalette.ColorRole.WindowText, INK),
    (QPalette.ColorRole.Base, PANEL),
    (QPalette.ColorRole.AlternateBase, PANEL),
    (QPalette.ColorRole.Text, INK),
    (QPalette.ColorRole.Button, PANEL),
    (QPalette.ColorRole.ButtonText, INK),
    (QPalette.ColorRole.PlaceholderText, MUTED),
    (QPalette.ColorRole.Highlight, PRIMARY),
    (QPalette.ColorRole.HighlightedText, PANEL),
)


def declare_interface_colours(widget: QWidget) -> None:
    """Draw one widget's palette-painted parts in this interface's colours.

    This interface declares the colours of every surface it draws, such as a
    panel, a badge, a button or a slider. A widget that declares nothing
    paints from Qt's palette instead, and that palette follows the *host
    appearance* rather than this interface. The transport buttons' labels had
    that defect (`PL-DHBX`). The controls this function covers are the ones
    that no stylesheet reaches. An entry's fill, a spin box's stepper, a
    list's rows and its scroll bar, a check box's indicator and a dialog's own
    surface are each painted from a palette role. So under a dark host
    appearance they were drawn near-black inside a light dialog (`PL-RKRY`,
    `PL-7W9N`).

    **A palette rather than a stylesheet, measured rather than assumed.**
    Styling `QAbstractSpinBox` with `setStyleSheet` moves the widget onto
    `QStyleSheetStyle`. That style rendered both spin boxes without their
    up/down steppers, and the stepper is the only way to change the value
    with a mouse. A styled `QCheckBox::indicator` loses its tick entirely
    unless an image is supplied for it, which would make the drawn state and
    the hidden state look identical. Declaring the roles keeps every native
    sub-control and only recolours it. `popup_stylesheet` is the one place
    where the opposite choice applies, and its docstring says why.

    **The `Disabled` colour group is left exactly as the platform supplied
    it.** That is what makes this function allowed at all.
    `.claude/rules/ui-color.md` requires a disabled colour to be the
    platform's, with one declared exception: `transport_button_stylesheet`'s
    MUTED label. `tools/contrast_check.py` refuses a second exception. This
    function writes only the `Active` and `Inactive` groups, starting from
    the widget's own palette. So nothing in this interface chooses a disabled
    colour that no contrast requirement measures. `test_dark_appearance.py`
    tests this. Nothing this function is applied to is disabled today. The
    controls that are disabled elsewhere are the agent selector, the three
    transport buttons, some menu entries, and the fork panel's point
    selector, take button and here button. The agent selector and the fork
    panel's three controls are each hidden by the same expression that
    disables them.

    The colours come from `app/theme.py`, and the contrast of every pair they
    make is already measured. `tools/contrast_check.py` checks INK on PANEL
    for the text a reader types and the rows of a list, MUTED on PANEL for
    the placeholder, and PANEL on PRIMARY for a selected row.

    Args:
        widget: The widget to declare colours for. Its own palette is the
            starting point. So a role this interface does not name keeps
            whatever colour it already resolved to, and the `Disabled` group
            keeps all of its colours.
    """

    widget.setPalette(_with_declared_roles(widget.palette()))


def declare_application_colours(application: QApplication) -> None:
    """Draw the chrome that no stylesheet or widget palette reaches in this interface's colours.

    `declare_interface_colours` declares the colours of one widget. This
    function declares the palette that every widget falls back to. Qt's
    application palette follows the *host appearance*. So on a machine set to
    Dark, the parts of the window that this interface never names were drawn
    dark around a light interface. Declaring the light palette here is the
    project owner's decision (`PL-KRZW`, 2026-09-20, ratified). It was chosen
    over leaving the host appearance alone, and over adding a second palette
    for dark support. A second palette would mean re-measuring all 24
    contrast requirements and re-picking the six trace colours against dark
    surfaces. The light theme is the one declared because of the contrast
    checks. Every requirement in `tools/contrast_check.py` is measured on
    PANEL and BACKGROUND. An interface that drew any other surface would be
    measured against surfaces that are not on screen.

    **A palette rather than `styleHints().setColorScheme`.** Qt 6.8 documents
    its colour scheme as a hint, and says that "overriding the color scheme is
    not supported on all platforms". On 2026-09-20 the hint was observed being
    ignored outright: `styleHints().colorScheme()` still reported `Unknown`
    after it was set. So nothing may depend on it. An application palette
    always takes effect, at any depth. It is also the only thing that reaches
    a widget below an ancestor that has a stylesheet. A stylesheet makes every
    widget beneath it take its colours from the *application* palette rather
    than from the styled widget. That is why a list's scroll bar and three
    selector popups could not be reached from the widget containing them
    (`PL-0NVN`).

    **What it covers, measured.** Under the dark host palette that
    `tests/integration/test_dark_appearance.py` supplies, the scroll bar of
    the page's scroll area went from 94.3% of its pixels darker than mid-grey
    to 0%.

    **What it does not cover, and why that follows the rule rather than
    leaving a gap.** The `Disabled` colour group is left exactly as the
    platform supplied it, for the reason `declare_interface_colours` gives.
    So a disabled control with no colour of its own keeps drawing the host's
    colours. Declaring a disabled colour is a decision under
    `.claude/rules/ui-color.md`, not a style choice. This interface declares
    exactly one, and it is measured.

    **The per-widget declarations stay.** This function does not make them
    redundant. Tests build a view without `main()` ever running, and a view
    could be embedded the same way. `test_dark_appearance.py` asserts that a
    widget's own declaration survives a *hostile* application palette. That
    test would fail if the only declaration were the global one.

    Args:
        application: The application to declare colours for. Call this
            immediately after the application is constructed and before any
            widget exists, so that nothing is built under the host's palette.
            The application's current palette is the starting point. So the
            `Disabled` group and every role not named here keep what the
            platform supplied.
    """

    application.setPalette(_with_declared_roles(application.palette()))


def _with_declared_roles(existing: QPalette) -> QPalette:
    """Return a copy of `existing` with this interface's colours in its live groups.

    This function is the one place that enforces the rule that only the
    `Active` and `Inactive` groups are written. So the widget declaration and
    the application declaration cannot drift apart on that rule. Both of
    their docstrings say why the `Disabled` group keeps the platform's colours.

    Args:
        existing: The palette to start from. Every role that `_DECLARED_ROLES`
            does not name keeps the colour it already resolved to.

    Returns:
        The copy. `existing` is not modified.
    """

    palette = QPalette(existing)

    for role, color in _DECLARED_ROLES:
        for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive):
            palette.setColor(group, role, QColor(color))

    return palette


class FlowLayout(QLayout):
    """A row of items that wraps onto further lines when the width runs out.

    It follows the shape of Qt's documented Flow Layout example. Items are
    laid out left to right in the order they were added. Each line is as tall
    as its tallest item, and an item that would overrun the right edge starts
    the next line. The layout reports its height for a given width, so the
    column above it makes the row taller as the row narrows. The layout
    expands in neither direction. Its minimum size is just large enough to
    hold any one of its items, so no item is ever laid out outside it. The
    legend rows use this layout so that six compartment entries on one line
    cannot hold the whole chart column to their combined width (`PL-25KS`).
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
        """Return the items this row actually places: every item except a hidden widget.

        A hidden widget is not on screen. Reserving its width would leave a
        gap in the row, and could push the entries after it onto another line
        for no reason. Qt's own layouts skip a hidden widget. This row is
        hand-written, so it has to skip one explicitly. Rows whose entries
        appear and disappear depend on this. An example is the chart legend's
        per-run entries, which are hidden while only one run is drawn.
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

    The panel always has four lines, so every panel in the row has the same
    shape. A panel with no gloss (the short qualifier line under the name)
    draws `EMPTY_METRIC_QUALIFIER`, and one with no second unit draws
    `EMPTY_METRIC_SECONDARY_VALUE`. So every reading sits on one baseline
    (`PL-8M05`). The gloss is smaller than the name, and the second unit is
    smaller than the value, because each is the weaker claim of its pair
    (`theme.METRIC_QUALIFIER_SIZE`, `theme.METRIC_SECONDARY_VALUE_SIZE`).

    The panel reserves its minimum width when it is built. The width is the
    widest string each line can show, measured in that line's font, plus the
    panel's padding (`PL-3355`). No line wraps. So a layout that offers less
    than the reservation clips the panel's edge rather than moving a unit
    onto its own line. The clock is the one value whose string changes length
    every tick. The reservation also stops the clock from shifting its panel
    as parts of the time, such as the hours, appear and fall away.

    The value and the second unit form the panel's *reading*, which is one
    widget under the name and the gloss. While two runs are compared, the
    second run's reading joins the first run's panel instead of appearing in
    a second panel of its own. So the readout block grows by a few lines
    rather than by a second row (`docs/MODEL.md` § "Minimum displayed
    outputs", `PL-F2YS`). Each reading then names its run on a line above its
    value.

    Attributes:
        name_label: The modeled quantity, in the model's own terms.
        qualifier_label: What a clinician would compare it against.
        reading: The run name, the value and the second unit, in one widget
            that `add_reading` can give to another run's panel.
        run_name_label: The run the reading belongs to, hidden while no
            name is set.
        value_label: The reading with its unit. It never wraps.
        secondary_label: The reading in its second unit. It never wraps.
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
        self.setStyleSheet(panel_stylesheet(self.objectName()))
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
        self.run_name_label = styled_label("", color=INK, size_px=METRIC_QUALIFIER_SIZE, bold=True)
        self.run_name_label.setHidden(True)

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

        self.reading = QWidget()
        reading_column = QVBoxLayout(self.reading)
        reading_column.setContentsMargins(0, 0, 0, 0)
        reading_column.setSpacing(0)

        for label in (self.run_name_label, self.value_label, self.secondary_label):
            reading_column.addWidget(label)

        self._column = QVBoxLayout(self)
        self._column.setContentsMargins(PANEL_PADDING, PANEL_PADDING, PANEL_PADDING, PANEL_PADDING)
        self._column.setSpacing(0)

        for widget in (self.name_label, self.qualifier_label, self.reading):
            self._column.addWidget(widget)

    def set_run_name(self, name: str | None) -> None:
        """Name the run this panel's own reading belongs to, or show no name.

        Args:
            name: The run's name from `dashboard_frame.run_label`, or `None`
                for a lone run. A lone run needs no name, because there is no
                other run to tell it apart from.
        """

        self.run_name_label.setText(name or "")
        self.run_name_label.setHidden(name is None)

    def add_reading(self, reading: QWidget) -> None:
        """Show another run's reading of the same quantity under this one's.

        The reading is still the other run's widget, and that run's view
        writes it. The reading leaves this panel when it is deleted.

        Args:
            reading: The other panel's `reading`.
        """

        self._column.addWidget(reading)

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

    The row reflows rather than squeezing a panel (`PL-8M05`). At each
    resize, `dashboard_frame.readout_columns` returns how many panels fit the
    new width, given the row's own measured reservations and the grid's own
    spacing between them. The grid is then laid out again with that many
    columns. Every column gets equal stretch and a minimum width, so no panel
    gets more of the row than its neighbours and none is laid out outside the
    row. Each column's minimum width is the widest reservation among the
    panels in it. So the clock's wide elapsed form does not cost the six
    compartment columns its width, and seven columns fit across a
    laptop-wide row. The widths at which the count steps down therefore come
    from the rendering font rather than from a recorded table of pixel
    widths.

    The row's own minimum width is one column's width, which is the widest
    panel's reservation, rather than the grid's minimum. A row held at its
    seven-column minimum by a scroll area or a splitter could never receive
    the narrower resize that tells it to reflow. Each panel keeps its own
    reservation, so no value wraps at any column count (`PL-3355`).

    Attributes:
        panels: One `MetricPanel` per readout, in row order.
        panel_minimum_widths_px: Each panel's own reservation, in row
            order, so that whether a column count fits a given width can be
            checked against them.
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
            reservations: For each panel, the widest value and the widest
                second line its column can show, from
                `dashboard_frame.READOUT_RESERVATIONS`.
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
            ValueError: If `readouts` does not hold one readout per panel.
                A row written from the wrong count would leave a panel
                showing the previous tick beside six panels showing this one.
        """

        if len(readouts) != len(self.panels):
            raise ValueError(
                f"the readout row holds {len(self.panels)} panels and was given "
                f"{len(readouts)} readouts"
            )

        for panel, readout in zip(self.panels, readouts, strict=True):
            panel.set_readout(readout)

    def set_run_name(self, name: str | None) -> None:
        """Name the run every panel's own reading belongs to, or show no name.

        Args:
            name: The run's name from `dashboard_frame.run_label`, or `None`
                for a lone run.
        """

        for panel in self.panels:
            panel.set_run_name(name)

    def add_readings(self, other: ReadoutRow) -> tuple[QWidget, ...]:
        """Show another run's readings in this row's panels, and hide its row.

        This is how two runs share one readout block. Each panel shows both
        runs' values under one name, and each value names its run. So a
        second run adds three lines to the block rather than a second row of
        seven panels (`PL-F2YS`).

        Args:
            other: The second run's row. It is hidden, because its panels no
                longer contain their readings.

        Returns:
            The readings that were moved, in row order. Deleting them takes
            them out of this row's panels again.

        Raises:
            ValueError: If the rows do not name the same quantities in the
                same order, which would put a value under another quantity's
                name.
        """

        names = tuple(panel.name_label.text() for panel in self.panels)
        compared_names = tuple(panel.name_label.text() for panel in other.panels)

        if compared_names != names:
            raise ValueError(
                f"a row naming {', '.join(names)} cannot show the readings of a row "
                f"naming {', '.join(compared_names)}"
            )

        for panel, compared in zip(self.panels, other.panels, strict=True):
            panel.add_reading(compared.reading)

        other.setHidden(True)

        return tuple(compared.reading for compared in other.panels)

    def minimumSizeHint(self) -> QSize:  # Qt spells this in camelCase.
        """Return a size one column wide, and as tall as the grid at its current column count."""

        return QSize(self.panel_minimum_width_px, super().minimumSizeHint().height())

    def resizeEvent(self, event: QResizeEvent) -> None:  # Qt spells this in camelCase.
        super().resizeEvent(event)
        columns = self._columns_for(event.size().width())

        if columns != self._columns:
            self._lay_out(columns)

    def width_for(self, columns: int) -> int:
        """The narrowest row width that fits the panels `columns` across, at their reservations."""

        return ceil(
            readout_row_width(columns, self.panel_minimum_widths_px, self._grid.horizontalSpacing())
        )

    def _columns_for(self, width_px: int) -> int:
        """The largest allowed column count whose panels fit `width_px` at their reservations."""

        return readout_columns(
            width_px, self.panel_minimum_widths_px, self._grid.horizontalSpacing()
        )

    def _lay_out(self, columns: int) -> None:
        """Seat the panels `columns` across, every column with equal stretch.

        A column's minimum width is the widest reservation among the panels
        in it. The stretch is equal, so any width beyond the minimums is
        shared equally, and the columns are equal in width wherever there is
        room.
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
    in steps of one count. One count is the control's display resolution, so
    the value the slider emits and the value printed beside it are the same
    number (`PL-25KS`, decision D4). The value label shows the settings in
    force. `set_setting` writes it from the snapshot that a frame was drawn
    from. On a halt that no frame follows, it writes the label from the
    controller's own settings instead (`PL-85LJ`). So after a refused
    setting, or a drag that halted the run, the control shows what the
    simulation is actually running at.

    The value label's width only grows. It is reserved from the first text
    the label is given, and widened when a longer text arrives, but never
    narrowed. So the slider beside it does not shorten under the pointer
    mid-drag when the printed value loses a digit.

    **A pointer drag applies on release, and previews until then**
    (`PL-5B1N`, project owner, 2026-09-27, ratified). While the thumb is held,
    the run keeps the setting in force, and the slider reports where the
    thumb stands through `preview_moved`, so the chart can draw the
    trajectory that setting would give. Releasing the thumb applies the value
    through `value_changed`, once, and then ends the preview through
    `preview_ended`. That order lets the frame drawn at the release show the
    run under its new setting and no preview. Qt itself would apply the value
    only after `sliderReleased`, so `_on_thumb_released` applies it first. A
    key press, a wheel step or a click on the groove is one discrete input,
    so it applies at once and previews nothing. Qt's
    tracking is switched off to give exactly that split: `valueChanged`
    fires on release for a drag and at once for every other input.

    Attributes:
        slider: The integer slider.
        name_label: The setting's name.
        qualifier_label: The gloss under the name, hidden where the setting
            has none. No spacer keeps the line open, because the four
            controls have unequal heights by design (`SettingReadout`).
            Only the delivered dial carries a second line, for its MAC
            multiple.
        value_label: The setting as the snapshot prints it.
        secondary_label: The setting in its second unit, shown only where
            the setting has one, which is the delivered dial's MAC line.
        adjustment_started: Emitted when the reader presses the thumb, so
            the run can mark one adjustment before the values arrive.
        value_changed: Emitted with the decoded value when the reader
            applies one: on releasing a dragged thumb, or at once for a key,
            a wheel step or a click on the groove. `set_setting` never emits
            it.
        preview_moved: Emitted with the decoded value where the held thumb
            stands, when it is pressed and each time it moves.
        preview_ended: Emitted when the held thumb is released, after
            `value_changed` has applied the value.
    """

    adjustment_started = Signal()
    value_changed = Signal(float)
    preview_moved = Signal(float)
    preview_ended = Signal()

    def __init__(self, setting: SettingReadout, parent: QWidget | None = None) -> None:
        """Build the control and write it from `setting`.

        Args:
            setting: The control as drawn this tick.
            parent: The Qt parent.
        """

        super().__init__(parent)
        self.setObjectName("parameterPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(panel_stylesheet(self.objectName()))
        self._decimals = setting.decimals
        self.name_label = styled_label(setting.name, color=INK, bold=True)
        self.qualifier_label = styled_label(
            setting.qualifier, color=MUTED, size_px=PARAMETER_QUALIFIER_SIZE, italic=True
        )
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setSingleStep(1)
        self.slider.setPageStep(1)
        self.slider.setTracking(False)
        self.slider.setStyleSheet(slider_stylesheet())
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
        self.slider.sliderPressed.connect(self._on_thumb_pressed)
        self.slider.sliderMoved.connect(self._on_thumb_moved)
        self.slider.sliderReleased.connect(self._on_thumb_released)
        self.slider.valueChanged.connect(self._on_slider_moved)
        self.set_setting(setting)

    def set_setting(self, setting: SettingReadout) -> None:
        """Write the range, position and text from this tick's setting.

        The slider's signals are blocked while it is written, so a value
        that came *from* the snapshot is never applied back to it: that
        would record a control change the reader did not make.

        The position is not written while the thumb is held. The run keeps its
        setting during a drag, so writing it would pull the thumb back from
        under the pointer on every frame. The label beside the slider is still
        written, and it shows the setting in force.

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
            if not self.slider.isSliderDown():
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

    def _on_thumb_pressed(self) -> None:
        self.preview_moved.emit(slider_value(self.slider.sliderPosition(), self._decimals))

    def _on_thumb_moved(self, position: int) -> None:
        self.preview_moved.emit(slider_value(position, self._decimals))

    def _on_thumb_released(self) -> None:
        """Apply where the thumb was released, then end the preview.

        `QAbstractSlider.setSliderDown` emits `sliderReleased` before it moves
        the value to the thumb's position. Setting the value here applies it
        first, and Qt then finds nothing left to move.
        """

        position = self.slider.sliderPosition()

        if position != self.slider.value():
            self.slider.setValue(position)

        self.preview_ended.emit()


class NoticeLabel(QLabel):
    """The banner above a run's values: a stopped run or a refused setting, or nothing.

    The banner is word-wrapped, bold and drawn in `theme.WARNING`, which is
    the one warning colour this interface has. It is hidden rather than blank
    when there is nothing to say, so an empty line never takes up the space a
    warning would.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(foreground_stylesheet(WARNING))
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


def lay_out_question(
    dialog: QDialog, title: str, body: Sequence[QLabel], action_label: str, keep_label: str
) -> tuple[QLabel, QPushButton, QPushButton]:
    """Build a modal question that asks before something is discarded or changed.

    `NewCaseDialog` and `WorkspaceQuestionDialog` are both laid out this way.
    The title comes first. The `body` labels follow it, each at the dialog's fixed width.
    The two buttons come last, with the destructive button first and the safe button last.
    The action button is outlined and is never the default. The keep button is filled
    and is the default. So pressing Return keeps everything as it was. Pressing Escape
    or closing the dialog does the same. The action button's `clicked` signal runs
    `accept()`, and the keep button's `clicked` signal runs `reject()`.

    Args:
        dialog: The dialog to build. This function calls `declare_interface_colours`
            on it, which declares the dialog's surface.
        title: The question, shown as the window title and as the first label.
        body: The statements under the title, in reading order.
        action_label: The destructive action's text.
        keep_label: The safe action's text.

    Returns:
        The title label, the action button and the keep button.
    """

    dialog.setModal(True)
    dialog.setWindowTitle(title)
    declare_interface_colours(dialog)
    title_label = styled_label(title, color=INK, bold=True, wrap=True)
    action_button = QPushButton(action_label)
    action_button.setAutoDefault(False)
    action_button.setDefault(False)
    action_button.setStyleSheet(outlined_button_stylesheet())
    keep_button = QPushButton(keep_label)
    keep_button.setDefault(True)
    keep_button.setStyleSheet(filled_button_stylesheet())

    column = QVBoxLayout(dialog)
    column.setSpacing(NEW_CASE_DIALOG_SPACING)
    column.addWidget(title_label)

    for label in body:
        label.setFixedWidth(NEW_CASE_DIALOG_WIDTH)
        column.addWidget(label)

    actions = QHBoxLayout()
    actions.addStretch(1)
    actions.addWidget(action_button)
    actions.addWidget(keep_button)
    column.addLayout(actions)

    action_button.clicked.connect(dialog.accept)
    keep_button.clicked.connect(dialog.reject)
    return title_label, action_button, keep_button


class NewCaseDialog(QDialog):
    """The confirmation asked before a recorded run is discarded for a new agent.

    The destructive button comes first and the safe button last. The discard
    button is drawn first and outlined, and the keep button is drawn last and
    filled. Only the keep button is the default. So the press a reader makes
    without reading, either Return or the trailing action, keeps their case.
    Escape or closing the dialog does the same. `accept()` therefore means
    "discard and start the new case", and `reject()` means "keep". The run
    connects to `finished` and checks which result arrived. The dialog is
    modal, so the reader cannot reach the run's controls while a question
    about that run is open. It is shown with `open()` and never with
    `exec()`, so a test can call `accept()` and `reject()` itself.

    The surface is `theme.PANEL`, set explicitly rather than left to the
    platform. So the title's INK, the discard line's WARNING and the
    carry-over line's MUTED are drawn on the surface that
    `tools/contrast_check.py` measures them against (`PL-R3KB`). Since
    `PL-RKRY`, the surface is declared as a palette rather than as a
    one-rule stylesheet. A stylesheet on a dialog stops everything inside it
    from inheriting the dialog's own colours. So a control added here later
    would paint in the host appearance's colours, however this surface was
    set.

    Attributes:
        title_label: Names the agent the reader would start.
        body_labels: The three statements, in the order a reader meets
            them: the opening line in INK, then the discard warning in bold
            WARNING, then the carry-over line in MUTED.
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
        opening, discard_warning, carry_over = question.body
        self.body_labels = (
            styled_label(opening, color=INK, wrap=True),
            styled_label(discard_warning, color=WARNING, bold=True, wrap=True),
            styled_label(carry_over, color=MUTED, wrap=True),
        )
        self.title_label, self.discard_button, self.keep_button = lay_out_question(
            self, question.title, self.body_labels, question.discard_label, question.keep_label
        )

    def show_question(self, question: NewCaseQuestion) -> None:
        """Rewrite every line of the question, because the runs may have moved on while it is open.

        The question names how much work starting over discards. A running
        run goes on stepping while the dialog is open, so the run view
        rewrites the question on each refresh. The reader therefore decides
        on a figure for the work as it stands now (`PL-WM5P`).

        Args:
            question: The text of `dashboard_frame.new_case_question` or
                `dashboard_frame.trunk_reset_question`, for the runs as they
                stand now.
        """

        self.title_label.setText(question.title)

        for label, line in zip(self.body_labels, question.body, strict=True):
            label.setText(line)

        self.discard_button.setText(question.discard_label)
        self.keep_button.setText(question.keep_label)


class MarkRow(QWidget):
    """One mark's row: a bullet, and beside it the row's text, wrapping under itself.

    The bullet has a column of its own because a row can wrap. A wrapped row's
    continuation can be a whole clause that names a run, such as
    `Run 2 reached`. If the continuation started at the same margin as every
    row, it would look like a row of its own (`PL-FPY2`). Here a continuation
    starts under the text, to the right of the column where the next row's
    bullet sits. A standing is the clause that says whether a run has reached
    a mark. So a reader can tell which mark a standing belongs to from its
    position rather than from its wording.

    Attributes:
        bullet_label: Where the row starts.
        text_label: The row itself.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.bullet_label = styled_label(
            MARK_ROW_BULLET, color=MUTED, size_px=METRIC_QUALIFIER_SIZE
        )
        self.text_label = styled_label("", color=MUTED, size_px=METRIC_QUALIFIER_SIZE, wrap=True)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(MARK_ROW_BULLET_SPACING)
        row.addWidget(self.bullet_label, 0, Qt.AlignmentFlag.AlignTop)
        row.addWidget(self.text_label, 1)


class MarkListingLabel(QWidget):
    """One bookmark collection, drawn read-only: a heading and its rows.

    The bookmarks panel uses two of these rather than one widget holding both
    collections. The two collections are listed apart (`PL-LPLD`), and a
    widget that knew there were exactly two could not be placed anywhere a
    third kind was wanted. This widget is given a `MarkListing` and decides
    nothing. Whether it draws the rows or the empty line is settled in
    `dashboard_frame.MarkListing.empty_line`, where a test can check it
    without a display.

    Each mark is a `MarkRow` of its own rather than a line in one label, so a
    reader can tell a row that wraps apart from the row below it
    (`PL-FPY2`). The rows are rewritten in place each tick, and are only
    added or removed when the number of marks changes.

    Attributes:
        heading_label: The collection's name.
        empty_label: The line that stands in for the rows when the collection
            is empty.
        rows: One `MarkRow` per mark, in the order they were added.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.heading_label = styled_label("", color=INK, bold=True)
        self.empty_label = styled_label("", color=MUTED, size_px=METRIC_QUALIFIER_SIZE, wrap=True)
        self.rows: list[MarkRow] = []
        self._rows_column = QVBoxLayout()
        self._rows_column.setContentsMargins(0, 0, 0, 0)
        self._rows_column.setSpacing(MARK_ROW_SPACING)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(BOOKMARK_ROW_SPACING)
        column.addWidget(self.heading_label)
        column.addWidget(self.empty_label)
        column.addLayout(self._rows_column)

    def set_listing(self, listing: MarkListing) -> None:
        """Draw `listing`, both its heading and its rows.

        Args:
            listing: One of `dashboard_frame.bookmark_panel`'s two listings.
        """

        self.heading_label.setText(listing.heading)
        self.empty_label.setText(listing.empty_line or "")
        self.empty_label.setHidden(listing.empty_line is None)

        while len(self.rows) < len(listing.rows):
            row = MarkRow(self)
            self._rows_column.addWidget(row)
            self.rows.append(row)

        while len(self.rows) > len(listing.rows):
            row = self.rows.pop()
            self._rows_column.removeWidget(row)
            row.hide()
            row.deleteLater()

        for row, text in zip(self.rows, listing.rows, strict=True):
            row.text_label.setText(text)

    def text(self) -> str:
        """What the collection draws under its heading, one row to a line.

        Returns:
            The rows' text joined by newlines, or the empty line when there
            are no rows.
        """

        if self.rows:
            return "\n".join(row.text_label.text() for row in self.rows)

        return self.empty_label.text()


class BookmarksPanel(QWidget):
    """The two collections beside the chart, with the control that opens the editor.

    The panel is read-only. Marks are created and removed in
    `BookmarkDialog`. So the panel in front of the reader while a case runs
    shows what is marked, and offers nothing that a mis-click could use to
    change a run.

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
        self.edit_button.setStyleSheet(outlined_button_stylesheet())
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
        """Draw both collections from one tick's result, and show them again if withdrawn.

        Args:
            panel: `dashboard_frame.bookmark_panel`'s result this tick.
        """

        self.times.set_listing(panel.times)
        self.targets.set_listing(panel.targets)
        self.times.show()
        self.targets.show()

    def withdraw(self) -> None:
        """Hide both lists of marks, because the halt could not work out their standings.

        A mark's standing says whether the run has reached it. The halt path calls this
        method when restating the panel raised an exception
        (`SimulationView._restate_bookmark_panel`). The rows on screen come from the
        last frame. On a failed run, a row that still shows a mark as still to come is
        a stale claim. The halt restates the panel to remove that claim (`PL-YHR3`). The
        button that opens the editor stays on screen. The editor hides its own lists at
        the same moment (`BookmarkDialog.withdraw`). The next call to `set_panel` shows
        both lists again.
        """

        self.times.hide()
        self.targets.hide()


class ForkPanel(QWidget):
    """Where a learner takes a branch: which point to open it at, and the button.

    The panel sits beside the marks rather than inside a `RunView`, for the
    same reason the marks sit there. The points it offers belong to the
    *case*: the trunk's keyframes and the marks the trunk has passed. A
    control copied into each displayed run would give a branch a control that
    can only refuse (`docs/ARCHITECTURE.md` § "Where new code belongs").

    The panel decides nothing. Which points are offered, how they are
    rendered and whether the control is shown at all are settled in
    `dashboard_frame.fork_offer`, where a test can check them without a
    display. This class writes that result into widgets.

    **The panel keeps the `ForkPoint`s it was given, in the selector's order,
    and returns one of them** (`selected_point`). So the caller acts on the
    point it was handed, either a keyframe's `CaseInstant` or a mark itself.
    It does not act on the string a reader sees, or on a value read back out
    of Qt. When the list is rebuilt, a kept selection is found in the new
    list by `ForkPoint` equality, never by `findData`, for two reasons.
    First, Qt holds a `float` subclass as an opaque Python object, and
    `findData` matches that object only by identity. So an equal
    `CaseInstant` built anew is not found (measured 2026-10-04, PySide6,
    `PL-CN5S`). Second, a control event and a mark can stand at the same
    instant, and no lookup by number could tell them apart. Each entry still
    carries its instant as a plain-`float` `userData`. That is how code
    outside the panel reads the selector, as when a test finds an entry by
    its instant. Nothing in this class acts on it.

    **The panel refuses in the same way the transport refuses** (`PL-61WW`).
    It calls `setDisabled` beside `setHidden` with the same operand, and
    shows the reason where the control was. So a control that cannot be used
    is not drawn at all, and a reader is never left guessing what a
    greyed-out button needed.

    **A lock and a refusal get two different lines, because they are two
    different things.** A lock is a mode the reader can leave, and it is
    written as an ordinary caption where the control was. A refusal is the
    case rejecting what was asked for, and it is a `NoticeLabel` like every
    other refusal on this dashboard. Writing the lock in the notice's colour
    would spend this interface's one alarm colour on a state that is working
    as intended.

    **Two controls offer three kinds of branch point, because the points
    have two lifetimes** (`PL-TYWQ`, `PL-Y2SL`). The selector's entries are
    the recorded control events and the marks the trunk has passed. They
    stay until the case itself changes. The here button's instant is the one
    the paused trunk is standing on, and it is gone once the trunk starts.
    So the here button has a row of its own below the selector. It takes no
    instant from this panel at all. `BranchedCase.fork_here` forks where the
    trunk stands, so a press has no instant that it could name wrongly.

    Attributes:
        heading_label: What the section is called.
        point_selector: The points a branch may be opened at: the recorded
            control events and the marks the trunk has passed.
        take_button: Takes the branch; `clicked` is connected by the view.
        here_button: Takes the branch where the trunk is paused, and is on
            screen only while `dashboard_frame.fork_offer` offers that.
            `clicked` is connected by the view.
        lock_text: Why the control is not offered, shown where the control
            was.
        notice: Why the last requested branch was refused.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.heading_label = styled_label(FORK_HEADING, color=INK, bold=True)
        self.point_selector = QComboBox()
        self.point_selector.setStyleSheet(selector_stylesheet())
        # The selector has a fixed width because its entries grow as the trunk runs. A
        # selector that widened as it filled would move the button beside it under the
        # reader's pointer. The width is measured from the widest entry in the selector's
        # own font, because an entry cut short would lose the words that say it is a mark
        # (`PL-NC0D`).
        _fix_width_to_entry(
            self.point_selector,
            widest_fork_point_label(self.point_selector.fontMetrics().horizontalAdvance),
        )
        self.take_button = QPushButton(TAKE_FORK_LABEL)
        self.take_button.setStyleSheet(outlined_button_stylesheet())
        # This button has the same outline as the button above, because it is
        # the same kind of act on the same case. It differs in two ways: it
        # carries its instant in its own label, and it is only sometimes on
        # screen.
        self.here_button = QPushButton("")
        self.here_button.setStyleSheet(outlined_button_stylesheet())
        self.here_button.setDisabled(True)
        self.here_button.setHidden(True)
        self.lock_text = styled_label("", color=MUTED, wrap=True)
        self.lock_text.setHidden(True)
        self.notice = NoticeLabel(self)
        self._point_label = styled_label(FORK_POINT_LABEL, color=MUTED)
        # The points behind the selector's entries, one per entry, in the
        # selector's order. `selected_point` returns one of them, and
        # `set_offer` compares a new offer against them.
        self._offered: tuple[ForkPoint, ...] = ()

        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(BOOKMARK_ROW_SPACING)
        column.addWidget(self.heading_label)
        controls = QHBoxLayout()
        controls.setSpacing(CONTROL_ROW_SPACING)
        controls.addWidget(self._point_label)
        controls.addWidget(self.point_selector)
        controls.addWidget(self.take_button)
        controls.addWidget(self.lock_text)
        controls.addStretch(1)
        column.addLayout(controls)
        here_row = QHBoxLayout()
        here_row.setSpacing(CONTROL_ROW_SPACING)
        here_row.addWidget(self.here_button)
        here_row.addStretch(1)
        column.addLayout(here_row)
        column.addWidget(self.notice)

    def selected_point(self) -> ForkPoint | None:
        """Return the point currently selected, or None while nothing is selected.

        The result is the `ForkPoint` the panel was given. It is looked up by
        the selector's index in the points the panel keeps, rather than
        rebuilt from what Qt holds. So a mark comes back as the mark, and a
        keyframe comes back as the `CaseInstant` it was offered as (see this
        class's docstring).
        """

        index = self.point_selector.currentIndex()

        return None if index < 0 else self._offered[index]

    def set_offer(self, offer: ForkOffer) -> None:
        """Draw one tick's offer, keeping the reader's selection where it still exists.

        The entries are rebuilt only when they have changed. A running trunk
        adds an entry at every setting change and at every mark its clock
        reaches. A selector rebuilt every frame would drop a reader's choice
        mid-click. The rebuild runs under a `QSignalBlocker`, so that
        refilling the control cannot be mistaken for a reader operating it.

        **A selection whose point is no longer offered is cleared rather than
        moved, and a cleared selection stays clear** (`PL-J12Z`). The point
        is looked up by equality in the new list. When it is not there,
        `setCurrentIndex(-1)` leaves nothing selected, so `selected_point`
        returns None and the button says so. Falling back to the first entry
        would put *induction* under a reader who had chosen a later decision
        point, and the next press would branch there. That would be a
        silently substituted default, of exactly the kind `CLAUDE.md`'s
        safety-critical standard refuses. It can happen without a reset. A
        keyframe collapses when a dial is returned to its previous value at
        the same instant, which is a learner changing their mind. A mark
        leaves the list when it is unmarked. Qt itself selects the first
        entry whenever an emptied selector is refilled. That is why the index
        is set on every rebuild, not only when a selection survives. The
        first fill is the one exception, and it selects the first entry as a
        selector normally does. Nobody has chosen yet, so no choice is being
        replaced.

        **The here button is shown or hidden as a whole, never emptied in
        place.** The button carries its instant in its own label, so there is
        no selection for a reader to lose, as there is with the selector. In
        a frame in which the trunk is running, the button is taken off the
        panel. A live button is never left labelled with an instant that has
        passed. The button is disabled by the same expression that hides it,
        which is the pairing `tools/agent_identity_check.py` requires of
        every control on this dashboard.

        Args:
            offer: `dashboard_frame.fork_offer`'s result this tick.
        """

        if offer.points != self._offered:
            selected = self.selected_point()
            first_fill = not self._offered

            with QSignalBlocker(self.point_selector):
                self.point_selector.clear()

                for point in offer.points:
                    self.point_selector.addItem(point.label, userData=float(point.instant_s))

                if first_fill:
                    self.point_selector.setCurrentIndex(0)
                elif selected in offer.points:
                    self.point_selector.setCurrentIndex(offer.points.index(selected))
                else:
                    self.point_selector.setCurrentIndex(-1)

            self._offered = offer.points

        # An offer of no points is withdrawn like a locked one. It comes only
        # from a trunk whose frame failed, and a live button over an empty
        # selector could only fail (`PL-T2Q2`).
        withdrawn = offer.locked or not offer.points
        self.point_selector.setDisabled(withdrawn)
        self.point_selector.setHidden(withdrawn)
        self.take_button.setDisabled(withdrawn)
        self.take_button.setHidden(withdrawn)
        self._point_label.setHidden(withdrawn)
        # The label is written before the button is shown, so the button is
        # never on screen for a frame with an instant the trunk has already left.
        self.here_button.setText(offer.here_label)
        self.here_button.setDisabled(not offer.here_offered)
        self.here_button.setHidden(not offer.here_offered)
        self.lock_text.setText(offer.lock_reason)
        self.lock_text.setHidden(not offer.locked)
        self.notice.set_notice(offer.refusal)


def _form_grid(*rows: tuple[QWidget | None, ...]) -> QGridLayout:
    """Lay out a form on a grid, with its rows in the order they are given.

    Each row lists the widget in each of its columns, from left to right, with
    None for an empty cell. The same widget listed in neighbouring columns of
    one row spans those columns. So each widget's row and column come from its
    position in the arguments, and the code that builds a form writes no row or
    column number.

    Args:
        rows: The form's rows, from top to bottom.

    Returns:
        The grid, with every widget placed.
    """

    grid = QGridLayout()

    for row, cells in enumerate(rows):
        column = 0

        while column < len(cells):
            widget = cells[column]
            span = 1

            while column + span < len(cells) and cells[column + span] is widget:
                span += 1

            if widget is not None:
                grid.addWidget(widget, row, column, 1, span)

            column += span

    return grid


class BookmarkDialog(QDialog):
    """Where the two kinds of mark are created, listed and removed.

    One dialog serves both kinds of mark. The reference simulator uses that
    shape, and `PL-LPLD` was scoped on it. Both forms are visible at once,
    and each has its own add button. A tab or a kind selector would turn the
    choice of which kind is being added into a mode. The two collections also
    have different fields, not the same fields under a different kind, so a
    shared form would have nothing in common to hold.

    The dialog is non-modal, and it is shown with `open()` rather than
    `exec()` so that a test can drive it. It is non-modal deliberately. A run
    may be playing, and a modal window over a moving chart would lock the
    reader out of the transport controls with a window about something else.

    **The surface is declared as a palette**, and the six input controls are
    drawn from the same palette (`PL-RKRY`). Their fills, the spin boxes'
    steppers, the lists' rows and scrollbars and the compartment popup all
    paint from palette roles. Under a dark host appearance they were drawn
    near-black inside this light dialog. A one-rule stylesheet on the dialog
    was what stopped them inheriting the dialog's colours.
    `declare_interface_colours` gives the reasoning and the roles.

    **The height a target may be set to is bounded by the running agent.**
    The bound is here rather than on `MacTarget`, because it belongs to the
    agent rather than to the mark. No compartment can exceed the delivered
    concentration, and the vaporizer's own maximum bounds the delivered
    concentration. So no run of this agent could ever cross a target above
    `max_delivered_concentration_percent / agent_mac_percent`. Refusing such
    a target in the control follows `.claude/rules/expert-review.md`'s
    preference for an interface that prevents an error over one that reports
    it afterwards. The bound moves with the agent, because the two values it
    is computed from do.

    Attributes:
        instant_spin: The instant to mark, in seconds.
        instant_preview: That instant in the compound form the clock uses, so
            that no reader has to convert between the entry and the display.
        time_label_edit: The optional name for a time bookmark.
        add_time_button: Adds the time bookmark. The view connects its
            `clicked` signal.
        time_list: The marked instants, selectable for removal.
        remove_time_button: Removes the selected instant.
        compartment_combo: The compartment whose value a target is compared
            against.
        height_spin: The height, in multiples of the running agent's 1 MAC.
        target_label_edit: The optional name for a target.
        add_target_button: Adds the target.
        target_list: The marked heights, selectable for removal.
        remove_target_button: Removes the selected target.
        notice: Why an add was refused, hidden when there is nothing to say.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(BOOKMARK_DIALOG_TITLE)
        declare_interface_colours(self)
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
        self.target_label_edit = QLineEdit()
        self.target_label_edit.setPlaceholderText(MARK_NAME_PLACEHOLDER)
        self.add_target_button = QPushButton(ADD_MARK_LABEL)
        self.target_list = QListWidget()
        self.remove_target_button = QPushButton(REMOVE_MARK_LABEL)

        for listing in (self.time_list, self.target_list):
            listing.setMaximumHeight(BOOKMARK_LIST_MAX_HEIGHT)

        self.notice = NoticeLabel()
        self.close_button = QPushButton(CLOSE_BOOKMARKS_LABEL)
        self.close_button.setDefault(True)
        self.close_button.setStyleSheet(filled_button_stylesheet())
        self.close_button.clicked.connect(self.accept)

        for button in (
            self.add_time_button,
            self.remove_time_button,
            self.add_target_button,
            self.remove_target_button,
        ):
            button.setAutoDefault(False)
            button.setStyleSheet(outlined_button_stylesheet())

        self._build_layout()
        self.set_reachable_height(DEFAULT_MAXIMUM_TARGET_MAC)

    def _build_layout(self) -> None:
        """Lay the two forms out one above the other, each over its own list."""

        column = QVBoxLayout(self)
        column.setSpacing(BOOKMARK_SECTION_SPACING)

        times_heading = styled_label(TIME_BOOKMARK_HEADING, color=INK, bold=True)
        instant_name = styled_label(INSTANT_FIELD_LABEL, color=MUTED)
        time_label_name = styled_label(MARK_NAME_FIELD_LABEL, color=MUTED)
        column.addLayout(
            _form_grid(
                (times_heading, times_heading, times_heading),
                (instant_name, self.instant_spin, self.instant_preview),
                (time_label_name, self.time_label_edit, self.time_label_edit),
                (None, self.add_time_button, None),
                (self.time_list, self.time_list, self.time_list),
                (None, self.remove_time_button, None),
            )
        )

        targets_heading = styled_label(MAC_TARGET_HEADING, color=INK, bold=True)
        compartment_name = styled_label(COMPARTMENT_FIELD_LABEL, color=MUTED)
        height_name = styled_label(HEIGHT_FIELD_LABEL, color=MUTED)
        target_label_name = styled_label(MARK_NAME_FIELD_LABEL, color=MUTED)
        column.addLayout(
            _form_grid(
                (targets_heading, targets_heading, targets_heading),
                (compartment_name, self.compartment_combo, self.compartment_combo),
                (height_name, self.height_spin, None),
                (target_label_name, self.target_label_edit, self.target_label_edit),
                (None, self.add_target_button, None),
                (self.target_list, self.target_list, self.target_list),
                (None, self.remove_target_button, None),
            )
        )

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
                multiple of its own 1 MAC. The lower bound is one count of
                the displayed resolution, because every run is already at a
                target of zero before it begins.
        """

        self.height_spin.setRange(MAC_DISPLAY_RESOLUTION_MAC, maximum_mac)

    def set_panel(self, panel: BookmarkPanel) -> None:
        """Redraw both lists from one tick's result, keeping each selection.

        The rows are the same strings the panel beside the chart draws, from
        the same `dashboard_frame` call, so a reader moving between the two
        is reading one listing in two places rather than two listings.

        Args:
            panel: `dashboard_frame.bookmark_panel`'s result this tick.
        """

        _refill(self.time_list, panel.times.rows)
        _refill(self.target_list, panel.targets.rows)

        for widget in self._withdrawable():
            widget.show()

    def withdraw(self) -> None:
        """Hide both lists and their Remove buttons, because the standings could not be worked out.

        A mark's standing says whether the run has reached it. The halt path calls this
        method together with `BookmarksPanel.withdraw`, when restating the marks raised an
        exception (`SimulationView._restate_bookmark_panel`). The rows come from the last
        frame. On a failed run, a row that still lists a mark as still to come is a stale
        claim. The panel beside the chart has already hidden the same rows (`PL-F5KT`).
        The rows are hidden rather than cleared, because Remove selects a mark by its row.
        Each Remove button is hidden with its list, so the reader cannot remove a mark
        through a row they cannot see. The two forms stay on screen. The next call to
        `set_panel` shows the lists and buttons again.
        """

        for widget in self._withdrawable():
            widget.hide()

    def _withdrawable(self) -> tuple[QWidget, ...]:
        """The widgets `withdraw` hides and `set_panel` shows again."""

        return (
            self.time_list,
            self.remove_time_button,
            self.target_list,
            self.remove_target_button,
        )

    def selected_time_index(self) -> int:
        """Which marked instant is selected, or -1 for none."""

        return self.time_list.currentRow()

    def selected_target_index(self) -> int:
        """Which marked height is selected, or -1 for none."""

        return self.target_list.currentRow()

    def entered_time_bookmark(self) -> TimeBookmark:
        """The time bookmark the form currently describes.

        Raises:
            SimulationConfigurationError: If `CaseInstant` refuses the
                entered instant, or `TimeBookmark` refuses the name. The spin
                box's own range keeps the instant from being refused.
        """

        return TimeBookmark(
            CaseInstant(self.instant_spin.value()), _entered_label(self.time_label_edit)
        )

    def entered_mac_target(self) -> MacTarget:
        """The MAC target the form currently describes.

        Raises:
            SimulationConfigurationError: If `MacTarget` refuses the entered
                height or name.
        """

        return MacTarget(
            RecordedQuantity(self.compartment_combo.currentData()),
            MacMultiple(self.height_spin.value()),
            _entered_label(self.target_label_edit),
        )

    def clear_entry(self) -> None:
        """Empty the two name fields, for a mark that has just been added.

        The instant, compartment and height are left as they are. Adding a
        second mark near the first is the common case, and a control that
        reset itself would make the second entry take longer than the first.
        A name is cleared because reusing it would give two marks the same
        name.
        """

        self.time_label_edit.clear()
        self.target_label_edit.clear()


def _entered_label(field: QLineEdit) -> str | None:
    """What a name field says, or `None` where the reader left it empty.

    An empty field means "list it under its own value" rather than "name it
    nothing". `bookmarks.TimeBookmark` refuses a blank string in order to
    keep that distinction.
    """

    entered = field.text().strip()

    return entered or None


def _refill(widget: QListWidget, rows: Sequence[str]) -> None:
    """Rewrite `widget`'s rows, leaving the selected position where it was.

    Qt clears the current row when the model empties, so the index is saved
    before the rewrite and set again afterwards, rather than trusted to
    survive it. When the list no longer has a row at the selected position,
    such as after a reader removes the last row, nothing is selected. That is
    what a reader expects of a list they have just shortened.
    """

    selected = widget.currentRow()

    with QSignalBlocker(widget):
        widget.clear()
        widget.addItems(list(rows))

        if 0 <= selected < widget.count():
            widget.setCurrentRow(selected)


def initial_window_geometry(available: QRect, minimum: QSize, fraction: float) -> QRect:
    """The normal geometry: a fraction of the available screen, centred, never below its minimum.

    The geometry is sized from the screen rather than from a pixel count, so
    the window is fully visible on every display and never full screen
    (`PL-005`). The window opens maximized over this geometry (`PL-Z4K6`). So
    this geometry is what a reader gets back on un-maximizing, not the size
    first drawn. A minimum wider or taller than the fraction wins, because a
    window that cannot show its own content is worse than one that overhangs
    the screen. The window is still centred on the available area.

    Args:
        available: The screen's available geometry, which is what is left
            after the platform's own bars.
        minimum: The window's minimum size, from its own size hint.
        fraction: How much of `available`'s width and height to take,
            above zero and at most one.

    Returns:
        The window's normal frame geometry.

    Raises:
        ValueError: If `fraction` is not above zero and at most one. A
            window cannot open at zero size or at a size larger than the
            screen.
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
