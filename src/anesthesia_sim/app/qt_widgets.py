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

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace
from enum import Enum
from functools import partial
from math import ceil
from typing import Final

from PySide6.QtCore import (
    QElapsedTimer,
    QEvent,
    QObject,
    QPoint,
    QRect,
    QRectF,
    QSignalBlocker,
    QSize,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import (
    QAccessible,
    QAccessibleAnnouncementEvent,
    QAccessibleEvent,
    QAccessibleValueInterface,
    QColor,
    QFont,
    QFontMetrics,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPalette,
    QPen,
    QPolygon,
    QResizeEvent,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QAccessibleWidget,
    QApplication,
    QComboBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLayoutItem,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QStyle,
    QStyleOptionComboBox,
    QStyleOptionSlider,
    QVBoxLayout,
    QWidget,
)
from shiboken6 import isValid

from anesthesia_sim.app.bookmarks import MacTarget, TimeBookmark
from anesthesia_sim.app.branch_controls import FORK_POINT_KIND, FORK_POINT_LABEL, TAKE_FORK_LABEL
from anesthesia_sim.app.chart_frame import trace_style
from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.dashboard_frame import (
    ADD_MARK_LABEL,
    COMPARTMENT_FIELD_LABEL,
    COPY_FAILURE_DETAILS_LABEL,
    DEFAULT_MAXIMUM_TARGET_MAC,
    HEIGHT_FIELD_LABEL,
    HIDE_FAILURE_DETAILS_LABEL,
    INSTANT_ENTRY_SUFFIX,
    INSTANT_FIELD_LABEL,
    MARK_NAME_FIELD_LABEL,
    MARK_NAME_PLACEHOLDER,
    REMOVE_MARK_LABEL,
    REMOVED_MARK_TEMPLATE,
    SHOW_FAILURE_DETAILS_LABEL,
    TARGET_FORM_HEADING,
    TARGET_MARK_KIND,
    TIME_FORM_HEADING,
    TIME_MARK_KIND,
    UNDO_REMOVAL_LABEL,
    UNDO_REMOVAL_NAME_TEMPLATE,
    BookmarkPanel,
    ForkOffer,
    ForkPoint,
    MarkListing,
    NewCaseQuestion,
    Readout,
    SettingReadout,
    control_name,
    height_entry_maximum_mac,
    readout_columns,
    readout_row_width,
    report_fault_text,
    setting_value_text,
    slider_position,
    slider_value,
    spoken_reading,
    widest_fork_point_label,
)
from anesthesia_sim.app.formatting import (
    MAC_DISPLAY_DECIMALS,
    MAC_DISPLAY_RESOLUTION_MAC,
    MAC_UNIT_SUFFIX,
    format_elapsed,
)
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES
from anesthesia_sim.app.stylesheets import (
    clear_scroll_area_stylesheet,
    filled_button_stylesheet,
    foreground_stylesheet,
    outlined_button_stylesheet,
    panel_stylesheet,
    selector_stylesheet,
    slider_stylesheet,
)
from anesthesia_sim.app.theme import (
    BOOKMARK_ROW_SPACING,
    BOOKMARK_SECTION_SPACING,
    CONTROL_BORDER_WIDTH,
    CONTROL_ROW_SPACING,
    FOCUS_RING_WIDTH,
    INK,
    MARK_ROW_BULLET,
    MARK_ROW_BULLET_SPACING,
    MARK_ROW_SPACING,
    MENU_ARROW_SIZE,
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
    PARAMETER_SLIDER_LEAST_LENGTH,
    PRIMARY,
    VIEW_ROW_SPACING,
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
    for dark support. A second palette would mean re-measuring all 27
    contrast requirements and re-picking the six trace colours against dark
    surfaces. The light theme is the one declared because of the contrast
    checks. Every requirement in `tools/contrast_check.py` is measured on the
    light theme's own surfaces: PANEL, BACKGROUND, the three agent fills and
    the one filled button. An interface that drew any other surface would be
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

    **The light colour scheme is requested as well** (`PL-YZ9L`). The palette
    does not reach how macOS draws each letter. Qt draws a glyph with a black
    fill unless the host's colour scheme is Dark, and with a white fill when
    it is, and macOS thickens the strokes by the fill colour
    (`QCoreTextFontEngine::imageForGlyph`, Qt 6.11). So under Dark, the
    interface's dark lettering on its light surfaces was drawn heavier than
    under Light. On macOS, `setColorScheme(Light)` sets the application's
    appearance to Aqua (`QCocoaTheme::requestColorScheme`, Qt 6.10), so Qt
    then draws the letters as it does under Light. The request is made
    before the palette is set, because Qt rereads the system palette when the
    scheme changes. On a platform that ignores the request, the palette still
    applies.

    **What it covers, measured.** Under the dark host palette that
    `tests/integration/test_dark_appearance.py` supplies, the scroll bar of
    the page's scroll area went from 94.3% of its pixels darker than mid-grey
    to 0%.

    **What it does not cover, and why that follows the rule rather than
    leaving a gap.** The `Disabled` colour group is left exactly as the
    platform supplied it, for the reason `declare_interface_colours` gives.
    So a disabled control with no colour of its own keeps drawing the
    platform's colours. On a platform that honours the light request above,
    those are its light palette's; on one that ignores it, they follow the
    host appearance. Declaring a disabled colour is a decision under
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

    application.styleHints().setColorScheme(Qt.ColorScheme.Light)
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


def _clauses(words: str) -> list[str]:
    """Return `words` cut after each word that ends in a comma or a semicolon."""

    clauses = [""]

    for word in words.split(" "):
        clauses[-1] = f"{clauses[-1]} {word}" if clauses[-1] else word

        if word.endswith((",", ";")):
            clauses.append("")

    return [clause for clause in clauses if clause]


def clause_lines(words: str, metrics: QFontMetrics, width: int) -> list[str]:
    """Return `words` as lines that each fit in `width` px, broken only after a clause.

    A clause ends at a word that ends in a comma or a semicolon. A clause
    wider than `width` on its own still takes one line, because a break
    inside it could part a value from its unit.

    Args:
        words: The words on one line.
        metrics: The metrics of the font that the words are drawn in.
        width: The width each line should fit in, in px.

    Returns:
        The lines, in order.
    """

    lines: list[str] = []

    for clause in _clauses(words):
        if lines and metrics.horizontalAdvance(f"{lines[-1]} {clause}") <= width:
            lines[-1] = f"{lines[-1]} {clause}"
        else:
            lines.append(clause)

    return lines


class ClauseWrappingLabel(QLabel):
    """Words that keep to one line where there is room, and break only after a clause.

    The words break only at a space after a comma or a semicolon. So a value
    keeps its unit, and a range keeps both its edges, on one line: the
    MAC-awake entry never ends a line on "0.58–" or between "±1" and "SD".
    Qt's own word wrap breaks at any space, and it also wraps at a width it
    guesses, even in a row wide enough for one line. This label asks for its
    one-line width instead. A `FlowLayout` row gives an entry narrower than
    that its own width and the height its lines need there, and the label
    breaks only as many clauses onto new lines as that width needs.

    `text()` returns the words as broken at the current width. `words()`
    returns them on one line, and the dashboard's walk over what is on
    screen reads that, so a narrow View states the same text as a wide one.

    Args:
        text: The words on one line.
        color: The value of a `theme.py` colour name, for the words.
    """

    def __init__(self, text: str, *, color: str) -> None:
        super().__init__(text)
        self._words = text
        self.setStyleSheet(foreground_stylesheet(color))

    def setText(self, text: str) -> None:  # Qt spells this in camelCase.
        # A chart View rewrites its legend on every frame. Unchanged words
        # leave the layout alone, as `QLabel.setText` does.
        if text == self._words:
            return

        self._words = text
        super().setText(self._lines_at(self.width() - self._extra_px()))
        self.updateGeometry()

    def words(self) -> str:
        """The words on one line, as the entry states them wherever it is laid out."""

        return self._words

    def _lines_at(self, width: int) -> str:
        """Return the words with a line break after each clause that does not fit in `width`."""

        return "\n".join(clause_lines(self._words, self.fontMetrics(), width))

    def _extra_px(self) -> int:
        margins = self.contentsMargins()

        return margins.left() + margins.right() + 2 * self.margin()

    def _height_of(self, text: str) -> int:
        margins = self.contentsMargins()
        rows = text.count("\n") + 1

        return (
            rows * self.fontMetrics().lineSpacing()
            + margins.top()
            + margins.bottom()
            + 2 * self.margin()
        )

    def hasHeightForWidth(self) -> bool:  # Qt spells this in camelCase.
        return True

    def heightForWidth(self, width: int) -> int:  # Qt spells this in camelCase.
        return self._height_of(self._lines_at(width - self._extra_px()))

    def sizeHint(self) -> QSize:  # Qt spells this in camelCase.
        # One pixel more than the text's advance, so the layout's rounding
        # cannot leave the words a fraction too narrow and break them.
        width = self.fontMetrics().horizontalAdvance(self._words) + 1 + self._extra_px()

        return QSize(width, self._height_of(self._words))

    def minimumSizeHint(self) -> QSize:  # Qt spells this in camelCase.
        # The height is one line's. A layout widens an item's size hint to its
        # minimum, so the height of the narrowest layout here would be
        # reserved at every width. The height at a given width is
        # `heightForWidth`'s.
        metrics = self.fontMetrics()
        widest = max(metrics.horizontalAdvance(clause) for clause in _clauses(self._words))

        return QSize(widest + 1 + self._extra_px(), self._height_of(self._words))

    def resizeEvent(self, event: QResizeEvent) -> None:  # Qt spells this in camelCase.
        super().resizeEvent(event)
        lines = self._lines_at(self.width() - self._extra_px())

        if lines != self.text():
            super().setText(lines)


class OneLineWhereRoomLabel(QLabel):
    """Words on one line where the row has room, wrapped between words where it has not.

    Qt's own word wrap guesses a width of its own for a label's size hint, so
    a label in a row asks for that width even where the row has room for the
    whole text. It then breaks onto two lines in a wide window too. This
    label asks for its one-line width instead, and keeps Qt's word wrap for a
    row that gives it less. Its least width is its longest word, so a long
    text cannot hold the row it sits in at the text's full length
    (`PL-92XM`).

    Args:
        text: The words on one line.
    """

    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.setWordWrap(True)

    def _extra_px(self) -> int:
        margins = self.contentsMargins()

        return margins.left() + margins.right() + 2 * self.margin()

    def sizeHint(self) -> QSize:  # Qt spells this in camelCase.
        # One pixel more than the text's advance, so the layout's rounding
        # cannot leave the words a fraction too narrow and break them.
        width = self.fontMetrics().horizontalAdvance(self.text()) + 1 + self._extra_px()

        return QSize(width, self.heightForWidth(width))

    def minimumSizeHint(self) -> QSize:  # Qt spells this in camelCase.
        metrics = self.fontMetrics()
        widest = max(metrics.horizontalAdvance(word) for word in self.text().split() or [""])
        width = widest + 1 + self._extra_px()

        return QSize(width, self.heightForWidth(self.sizeHint().width()))


class LinesHeldLabel(QLabel):
    """Words that wrap between words, and keep the height their lines need at their width.

    A word-wrapped `QLabel` reports its height for a width, and a layout that
    reads it gives the label that height where the room allows. Where the
    room runs short, the layout counts the label at one line, and squeezes
    its later lines out of sight. This label takes the height its lines need
    at the width it was last given as its least height instead. A column of
    such labels above a list that scrolls then asks for enough height to
    show every line of them, and the list gives up its height first
    (`PL-HF1B`).

    The label reports no height for a width of its own. Reporting one would
    make the layout above it count its minimum as its full height, which
    for a column holding a scrolling list is the whole list's height.

    Args:
        text: The words, which wrap between words.
    """

    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.setWordWrap(True)

    def hasHeightForWidth(self) -> bool:  # Qt spells this in camelCase.
        return False

    def _lines_height(self) -> int:
        """Return the height that the label's lines need at the width it has now."""

        return super().heightForWidth(self.width())

    def sizeHint(self) -> QSize:  # Qt spells this in camelCase.
        return QSize(super().sizeHint().width(), self._lines_height())

    def minimumSizeHint(self) -> QSize:  # Qt spells this in camelCase.
        return QSize(super().minimumSizeHint().width(), self._lines_height())

    def setText(self, text: str) -> None:  # Qt spells this in camelCase.
        super().setText(text)
        # The new words may need another number of lines at this width.
        self.updateGeometry()

    def resizeEvent(self, event: QResizeEvent) -> None:  # Qt spells this in camelCase.
        old_width = event.oldSize().width()
        super().resizeEvent(event)

        # The lines the words need change with the width, and only then.
        if event.size().width() != old_width:
            self.updateGeometry()


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
    An item wider than the row whose height depends on its width, such as
    words that wrap, is given the row's width and the height it needs at
    that width (`PL-K4CZ`).
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

            # An item wider than the row, whose height depends on its width,
            # takes the row's width and the height it needs there. A legend
            # entry whose words wrap is such an item, and it would otherwise
            # run past the right edge.
            if size.width() > inner.width() and item.hasHeightForWidth():
                size = QSize(inner.width(), item.heightForWidth(inner.width()))

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
    rather than by a second row (`docs/INTERFACE.md` § "Minimum displayed
    outputs", `PL-F2YS`). Each reading then names its run on a line above its
    value.

    **Each reading is named for assistive technology** (`PL-N5JB`). A screen
    reader can reach the value or the second line on its own, away from the
    name above it, so each carries an accessible name built by
    `spoken_reading`: the panel's name, whether it is modelled, the run while
    runs are compared, and the line itself. The names are rewritten whenever
    a line or the run name changes.

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
        self._readout = readout
        self._run_name: str | None = None
        self._name_readings()

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
        self._run_name = name
        self._name_readings()

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
        self._readout = readout
        self._name_readings()

    def _name_readings(self) -> None:
        """Write the value's and the second line's accessible names from the lines they show.

        Qt tells assistive technology of each name that changes
        (`QWidget::setAccessibleName`), so a screen reader reading a panel
        hears the new value. The readouts are rewritten on every frame, so a
        name is written only where it changed.
        """

        for label, reading in (
            (self.value_label, self._readout.value),
            (self.secondary_label, self._readout.secondary),
        ):
            spoken = spoken_reading(self._readout, reading, self._run_name)

            if label.accessibleName() != spoken:
                label.setAccessibleName(spoken)


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


class DialInput(Enum):
    """Whether a dial's value is followed at once by a frame of its own, or needs one.

    A value set by a key, the wheel or a click on the track needs a frame.
    The dashboard draws it at once unless it drew a frame for an input less
    than `INPUT_FRAME_INTERVAL_MS` ago, and draws it at the end of that
    interval otherwise (`SimulationView.present_input`, `PL-2WVC`). The value at which
    a previewed thumb is released needs none, because the end of the preview
    draws a frame at once right after it (`PL-5B1N`).

    Members:
        STEP: A value set by a key press, a wheel event or a click on the
            track, alone or as one of a burst.
        RELEASE: The value at which a previewed thumb was released.
    """

    STEP = "a key, the wheel or a click on the track"
    RELEASE = "a released thumb"


class _SettingSlider(QSlider):
    """A horizontal slider on which a press on the track is one input, and one on the handle a grab.

    Each platform's style says which mouse buttons move the handle straight
    to the pointer when pressed on the track (`SH_Slider_AbsoluteSetButtons`).
    On macOS that is the left button. Under Qt's Fusion style it is the middle
    button, and a left click on the track steps one page instead. The slider
    keeps each platform's own convention (project owner, 2026-11-22,
    ratified, `PL-57LD`).

    Qt's `QSlider.mousePressEvent` handles such a press in two parts. It
    applies the value at the pointer, and then it marks the handle as held,
    which emits `sliderPressed`. `ParameterSlider` starts a preview of an
    unapplied value on `sliderPressed`. So without this class, a click on the
    track applied a value and then drew it labelled "not applied". A press on
    the handle off its centre also moved the handle to the pointer, and so
    applied a value before any drag.

    This class handles the two cases apart. A press on the track applies the
    value at the pointer, as one input, and `jumping` is true while it does
    so, so that no preview starts. A press on the handle applies nothing. The
    handle stays where it was, and the press then reports `sliderPressed` as
    a grab of the handle does under any style.

    Qt measures the drag that follows from where the handle would have jumped
    to, and keeps that distance where this class cannot reach it. Left to
    Qt, the first movement of the drag, even one pixel, would bring the
    handle's centre under the pointer and change the setting by up to half
    the handle's width. So this class measures that drag itself, from where
    the pointer pressed the handle, and the handle moves only as far as the
    pointer does.

    **Each input on the slider is announced before it changes the value**
    (`PL-0T2H`, `PL-PXTT`). A mouse press, a key press and a wheel notch each
    emit `input_started` first, so that the run records each as an adjustment
    of its own (`docs/INTERFACE.md` § "The control-input timeline"). A held
    key repeats its press, and Qt marks each repeat as such
    (`QKeyEvent.isAutoRepeat`). A repeat announces nothing, so the whole hold
    is one adjustment, and the earlier marks on the chart are not pushed off
    by one held key. A trackpad swipe is announced only where it begins, for
    the same reason.

    **A key press, a wheel turn or a second mouse button while the handle is
    held does nothing** (`PL-M3H5`). Qt's slider applies a key step at once
    even while the handle is down, and the chart would still label the held
    value "not applied" until the release. So while a pointer holds the
    handle, the drag is the one input, as a drag-and-drop library keeps
    standard keys from acting during a mouse drag (react-beautiful-dnd,
    docs/sensors/mouse.md, read 2026-11-23). A key whose press was ignored
    stays ignored while it is held, and a trackpad swipe that began during the
    hold stays ignored until it ends. Otherwise a key held past the release
    would repeat into the run with no announcement, and its steps would be
    counted as part of the drag.

    **A hold on the handle can be cancelled** (`cancel_hold`, `PL-HPD0`). The
    handle goes back to the value the slider holds, the rest of the gesture
    moves nothing, and its release applies nothing.

    **Assistive technology is told the setting, not the position**
    (`PL-9QY5`). The slider's position is a count of display steps, such as
    180 for 1.80% sevoflurane, and Qt's own accessible slider reports that
    count. `_SettingSliderAccessible` reports the value the position stands
    for instead, in the setting's own unit.

    Attributes:
        jumping: True only while a press on the track moves the handle to
            the pointer.
        control: The setting this slider sets, which words its value for
            assistive technology.
        decimals: The setting's display resolution, as in
            `SettingReadout.decimals`.
        input_started: Emitted at the start of each input, before the value
            it applies arrives.
    """

    input_started = Signal()

    def __init__(self, control: ControlInput, decimals: int) -> None:
        """Build the slider for one setting.

        Args:
            control: The setting this slider sets.
            decimals: The setting's display resolution.
        """

        super().__init__(Qt.Orientation.Horizontal)
        _install_setting_slider_accessibility()
        self.jumping = False
        self.control = control
        self.decimals = decimals
        self._grab_offset: int | None = None
        self._ignored_keys: set[int] = set()
        self._ignoring_swipe = False
        # True from a cancelled hold until the release of the mouse button that
        # held the handle (`cancel_hold`).
        self._hold_cancelled = False

    def setting(self) -> float:
        """Return the setting that the slider's value stands for, in the setting's unit."""

        return slider_value(self.value(), self.decimals)

    def apply_from_assistive_technology(self, setting: float) -> None:
        """Apply a setting that assistive technology asks for, as one input, like a key press.

        A screen reader's own command to set a slider's value arrives here
        in the setting's unit. It is announced first, as each input is, and
        it is ignored while a pointer holds the handle, as a key press is
        (`PL-M3H5`). A setting outside the slider's range is taken as its
        nearest end. A value that is not a finite number is ignored, so no
        adjustment is announced that no value follows.

        Args:
            setting: The setting asked for, in the setting's unit.
        """

        if self.isSliderDown() or not math.isfinite(setting):
            return

        lowest = slider_value(self.minimum(), self.decimals)
        highest = slider_value(self.maximum(), self.decimals)
        position = slider_position(min(max(setting, lowest), highest), self.decimals)
        self.input_started.emit()
        self.setValue(position)

    def cancel_hold(self) -> None:
        """End a pointer's hold on the handle without applying the value under it.

        The handle goes back to the value the slider holds, and no signal is
        emitted, so nothing is applied and no preview is reported as ended.
        Until the mouse button that held the handle is released, a move of the
        pointer moves nothing, and the release applies nothing. A slider whose
        handle is not held is left as it is.

        Each platform ends a pointer gesture in this way when something takes
        it away. Android's `MotionEvent.ACTION_CANCEL` says "You should not
        perform any action that you normally would as a result of this
        gesture", and `PL-HPD0` lists the other sources.
        """

        if not self.isSliderDown():
            return

        self._hold_cancelled = True
        self._grab_offset = None

        with QSignalBlocker(self):
            self.setSliderPosition(self.value())
            self.setSliderDown(False)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # Qt spells this in camelCase.
        if self.isSliderDown():
            self._ignored_keys.add(event.key())
            event.accept()
            return

        if event.isAutoRepeat() and event.key() in self._ignored_keys:
            event.accept()
            return

        self._ignored_keys.discard(event.key())

        if not event.isAutoRepeat():
            self.input_started.emit()

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:  # Qt spells this in camelCase.
        if not event.isAutoRepeat():
            self._ignored_keys.discard(event.key())

        super().keyReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:  # Qt spells this in camelCase.
        # A mouse wheel sends each notch as an event with no scroll phase. A
        # trackpad swipe sends one event that begins the gesture and then many
        # small ones, its momentum included, so it is announced only where it
        # begins and is one adjustment however far it moves the value.
        starts = event.phase() in (Qt.ScrollPhase.NoScrollPhase, Qt.ScrollPhase.ScrollBegin)

        if starts:
            self._ignoring_swipe = False

        if self.isSliderDown() or self._ignoring_swipe:
            self._ignoring_swipe = event.phase() not in (
                Qt.ScrollPhase.NoScrollPhase,
                Qt.ScrollPhase.ScrollEnd,
            )
            event.accept()
            return

        if starts:
            self.input_started.emit()

        super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # Qt spells this in camelCase.
        if event.buttons() != event.button():
            # Another button is already down, so this press is ignored.
            event.accept()
            return

        # No button was down, so no cancelled hold is still going on.
        self._hold_cancelled = False
        self.input_started.emit()
        button = event.button().value
        moves_to_pointer = self.style().styleHint(
            QStyle.StyleHint.SH_Slider_AbsoluteSetButtons, None, self
        )

        if button & moves_to_pointer != button:
            super().mousePressEvent(event)
            return

        options = QStyleOptionSlider()
        self.initStyleOption(options)
        pressed = self.style().hitTestComplexControl(
            QStyle.ComplexControl.CC_Slider, options, event.position().toPoint(), self
        )

        if pressed != QStyle.SubControl.SC_SliderHandle:
            self.jumping = True

            try:
                super().mousePressEvent(event)
            finally:
                self.jumping = False

            return

        held = self.value()
        handle = self._handle_rect()

        with QSignalBlocker(self):
            super().mousePressEvent(event)
            self.setValue(held)

        if self.isSliderDown():
            self._grab_offset = event.position().toPoint().x() - handle.x()
            self.sliderPressed.emit()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # Qt spells this in camelCase.
        if self._hold_cancelled:
            event.accept()
            return

        if self._grab_offset is None or not self.isSliderDown():
            super().mouseMoveEvent(event)
            return

        options = QStyleOptionSlider()
        self.initStyleOption(options)
        groove = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider, options, QStyle.SubControl.SC_SliderGroove, self
        )
        handle_width = self._handle_rect().width()
        span = groove.width() - handle_width
        handle_left = event.position().toPoint().x() - self._grab_offset - groove.x()
        self.setSliderPosition(
            QStyle.sliderValueFromPosition(
                self.minimum(), self.maximum(), handle_left, span, options.upsideDown
            )
        )
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # Qt spells this in camelCase.
        if event.buttons():
            # A second button was let go while the first still holds the handle.
            event.accept()
            return

        self._grab_offset = None

        if self._hold_cancelled:
            self._hold_cancelled = False

            # Qt's own release still runs, so the slider no longer counts the
            # handle as pressed. Its signals are blocked, so it applies nothing.
            with QSignalBlocker(self):
                super().mouseReleaseEvent(event)

            return

        super().mouseReleaseEvent(event)

    def _handle_rect(self) -> QRect:
        """Return the handle's rectangle, in this slider's pixels, as the style draws it."""

        options = QStyleOptionSlider()
        self.initStyleOption(options)

        return self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider, options, QStyle.SubControl.SC_SliderHandle, self
        )


class _SettingSliderValue(QAccessibleValueInterface):
    """Tell assistive technology a setting slider's value in the setting's unit, never its position.

    Each platform's bridge reads a different part of a slider's accessible
    interface, as Qt 6.10's source shows (read 2026-11-23). On macOS,
    VoiceOver's value is `currentValue` turned into text, and a value it sets
    arrives as a number (`qcocoaaccessibility.mm`, `getValueAttribute`;
    `qcocoaaccessibilityelement.mm`, `accessibilitySetValue`). On Linux,
    AT-SPI reads and sets `currentValue`, its bounds and its step as numbers
    (`atspiadaptor.cpp`, `AtSpiAdaptor::valueInterface`). On Windows, UI
    Automation reads the value pattern's text from `text(QAccessible.Text.Value)`
    and the range from the numbers (`qwindowsuiavalueprovider.cpp`,
    `qwindowsuiarangevalueprovider.cpp`).

    So the numbers here are in the setting's unit, and
    `_SettingSliderAccessible` gives the readout's own text as the value
    text. The value text then carries the unit where a platform reads it, as
    the slider pattern's `aria-valuetext` does where a number alone is not
    understandable (W3C WAI-ARIA Authoring Practices, Slider Pattern, read
    2026-11-23). macOS reads only the number, so `ParameterSlider` puts the
    unit in the slider's accessible name as well.

    This is an object of its own, not a second base class of
    `_SettingSliderAccessible`. A Python class with two wrapped Qt bases holds
    two C++ objects, and Qt's `interface_cast` then received the widget
    interface's address where it asked for the value interface's. A platform
    bridge calling `currentValue` through that address would have called
    another method of the widget interface (measured 2026-11-23, PySide6 6.12).
    """

    def __init__(self, slider: _SettingSlider) -> None:
        """Describe one setting slider's value.

        Args:
            slider: The slider described.
        """

        super().__init__()
        self._slider = slider

    def currentValue(self) -> float:  # Qt spells this in camelCase.
        """Return the setting in force at the slider, in the setting's unit."""

        return self._slider.setting()

    def setCurrentValue(self, value: object) -> None:  # Qt spells this in camelCase.
        """Apply a setting that assistive technology asks for, in the setting's unit."""

        if isinstance(value, int | float):
            self._slider.apply_from_assistive_technology(float(value))

    def minimumValue(self) -> float:  # Qt spells this in camelCase.
        """Return the slider's lowest setting, in the setting's unit."""

        return slider_value(self._slider.minimum(), self._slider.decimals)

    def maximumValue(self) -> float:  # Qt spells this in camelCase.
        """Return the slider's highest setting, in the setting's unit."""

        return slider_value(self._slider.maximum(), self._slider.decimals)

    def minimumStepSize(self) -> float:  # Qt spells this in camelCase.
        """Return one step of the slider, in the setting's unit."""

        return slider_value(1, self._slider.decimals)


class _SettingSliderAccessible(QAccessibleWidget):
    """Describe a setting slider to assistive technology, with its value in the setting's unit.

    The value is `_SettingSliderValue`, and the value text is the text the
    readout beside the slider prints, from `setting_value_text`.
    """

    def __init__(self, slider: _SettingSlider) -> None:
        """Describe one setting slider.

        Args:
            slider: The slider described.
        """

        super().__init__(slider, QAccessible.Role.Slider)
        self._slider = slider
        self._value = _SettingSliderValue(slider)

    # PySide6's stub types the C++ `void *` result as `int`. The binding turns
    # a returned wrapper into its C++ object's address, which Qt then casts to
    # the value interface. A number returned here crashed the process.
    def interface_cast(self, interface: QAccessible.InterfaceType) -> object:  # type: ignore[override]
        """Return the value object's address for `ValueInterface`, and Qt's result otherwise."""

        if interface is QAccessible.InterfaceType.ValueInterface:
            return self._value

        return QAccessibleWidget.interface_cast(self, interface)

    def text(self, kind: QAccessible.Text) -> str:
        """Return the setting as its readout prints it, or Qt's own text for anything else."""

        if kind is QAccessible.Text.Value:
            return setting_value_text(self._slider.control, self._slider.setting())

        return QAccessibleWidget.text(self, kind)


def _setting_slider_accessible(key: str, widget: QObject) -> _SettingSliderAccessible | None:
    """Return the accessible interface for a setting slider, and nothing for any other object.

    Qt asks each installed factory for an object's interface, once per class
    name from the object's own class up to `QObject`, and keeps the first
    interface returned. Returning `None` leaves every other object to Qt.

    Args:
        key: The class name Qt is asking about.
        widget: The object Qt is describing.

    Returns:
        The setting slider's interface, or `None`.
    """

    if isinstance(widget, _SettingSlider):
        return _SettingSliderAccessible(widget)

    return None


# Whether `_setting_slider_accessible` is installed. Qt keeps one list of
# factories for the process, so one installation serves every slider.
_accessibility_installed = False


def _install_setting_slider_accessibility() -> None:
    """Install `_setting_slider_accessible` the first time a setting slider is built.

    PySide6 installs a factory only once a `QApplication` exists, and a
    widget cannot be built before one, so the first slider is the earliest
    point that is always late enough. A probe on 2026-11-23 under PySide6
    6.12 found a factory installed before the `QApplication` never called.
    """

    global _accessibility_installed

    if _accessibility_installed:
        return

    QAccessible.installFactory(_setting_slider_accessible)
    _accessibility_installed = True


class ParameterSlider(QWidget):
    """One setting: its name, its gloss, the value in force and an integer slider under it.

    The slider spans `slider_position(minimum)` to `slider_position(maximum)`
    in steps of one count. One count is the control's display resolution, so
    the value the slider emits and the value printed above it are the same
    number (`PL-25KS`, decision D4). The value label shows the settings in
    force. `set_setting` writes it from the snapshot that a frame was drawn
    from. On a halt that no frame follows, it writes the label from the
    controller's own settings instead (`PL-85LJ`). So after a refused
    setting, or a drag that halted the run, the control shows what the
    simulation is actually running at.

    The value has a row of its own above the slider, so the slider takes the
    card's whole width, and a printed value that gains or loses a digit
    never moves the slider under the pointer. The slider is never shorter than
    `PARAMETER_SLIDER_LEAST_LENGTH`, so the card's least width holds it
    (`PL-V4Q8`). The name and its gloss break between words when the card is
    narrow, so a long name such as "Sevoflurane vaporizer" does not set the
    card's least width. The value and its unit never break (`PL-D5J4`).

    **A pointer drag applies on release, and previews until then**
    (`PL-5B1N`, project owner, 2026-09-27, ratified). While the thumb is held,
    the run keeps its current setting. The slider reports where the thumb
    stands through `preview_moved`, so the chart can draw the trajectory that
    setting would give. Releasing the thumb applies the value once, through
    `value_changed`, and then ends the preview through `preview_ended`. In
    that order, the frame drawn at the release shows the run under its new
    setting and no preview. So the value applied at the release is marked
    `DialInput.RELEASE`, and its frame is the one that ends the preview. A
    release ends a preview only where one started. A left click on the track
    under macOS moves the handle to the pointer and marks it held, but starts
    no preview, so its release draws no second frame. Qt itself would apply the value only after
    `sliderReleased`, so `_on_thumb_released` applies it first. A key press,
    a wheel step or a click on the groove is one discrete input, so it
    applies at once and previews nothing. Qt's slider tracking is switched
    off to give exactly that split. With tracking off, `valueChanged` fires
    on release for a drag and at once for every other input.

    A click on the groove steps one count under Fusion and moves the handle
    to the pointer on macOS, as each platform's style says. Either way it
    applies at once and draws no preview. Under Fusion, holding the button
    there repeats the step, and each step applies. On macOS, where the
    handle has moved to the pointer, moving the pointer with the button
    still down is a drag, and it previews as one (`_SettingSlider`,
    `PL-57LD`).

    Attributes:
        slider: The integer slider.
        name_label: The setting's name.
        qualifier_label: The gloss under the name, hidden where the setting
            has none. No spacer keeps the line open, because the four
            controls have unequal heights by design (`SettingReadout`).
        value_label: The setting as the snapshot prints it.
        secondary_label: The setting in its second unit, beside the value
            and shown only where the setting has one, which is the delivered
            dial's MAC multiple.
        adjustment_started: Emitted at the start of each input on the
            slider, so the run can mark one adjustment before the values
            arrive: a press, a key press that is not a held key's repeat, or
            a wheel notch.
        value_changed: Emitted with the decoded value when the reader
            applies one, and whether a frame follows it (`DialInput`): on
            releasing a dragged thumb, or at once for a key, a wheel step or
            a click on the groove. `set_setting` never emits it.
        preview_moved: Emitted with the decoded value at the held thumb's
            position, when the thumb is pressed and each time it moves. A
            press on the groove emits it only once the held thumb moves.
        preview_ended: Emitted when a held thumb that started a preview is
            released, after `value_changed` has applied the value.
    """

    adjustment_started = Signal()
    value_changed = Signal(float, object)
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
        # Whether a preview is shown for this slider's held thumb, which
        # `preview_ended` ends.
        self._previewing = False
        # True only while `_on_thumb_released` applies the released value.
        self._releasing = False
        # The setting's name and unit, and the run's name while runs are
        # compared, which `_write_accessible_name` puts together.
        self._setting_name = (setting.name, setting.unit)
        self._run_name: str | None = None
        self.name_label = styled_label(setting.name, color=INK, bold=True, wrap=True)
        self.qualifier_label = styled_label(
            setting.qualifier, color=MUTED, size_px=PARAMETER_QUALIFIER_SIZE, italic=True, wrap=True
        )
        self.slider = _SettingSlider(setting.control, setting.decimals)
        self.slider.setSingleStep(1)
        self.slider.setPageStep(1)
        self.slider.setTracking(False)
        self.slider.setStyleSheet(slider_stylesheet())
        self.slider.setMinimumWidth(PARAMETER_SLIDER_LEAST_LENGTH)
        FocusRing(self.slider)
        self.value_label = styled_label(setting.value_text, color=INK)
        self.secondary_label = styled_label(
            setting.secondary, color=MUTED, size_px=METRIC_SECONDARY_VALUE_SIZE
        )

        column = QVBoxLayout(self)
        column.setContentsMargins(PANEL_PADDING, PANEL_PADDING, PANEL_PADDING, PANEL_PADDING)
        column.addWidget(self.name_label)
        column.addWidget(self.qualifier_label)
        row = QHBoxLayout()
        row.addWidget(self.value_label)
        row.addWidget(self.secondary_label)
        row.addStretch(1)
        column.addLayout(row)
        column.addWidget(self.slider)

        self.slider.input_started.connect(self.adjustment_started.emit)
        self.slider.sliderPressed.connect(self._on_thumb_pressed)
        self.slider.sliderMoved.connect(self._on_thumb_moved)
        self.slider.sliderReleased.connect(self._on_thumb_released)
        self.slider.valueChanged.connect(self._on_slider_moved)
        self.set_setting(setting)

    def name_run(self, run_name: str | None) -> None:
        """Name the run in the slider's accessible name while runs are compared.

        Each compared run has a row of the same four sliders. A screen reader
        that moves from one row to the next would otherwise hear two sliders
        with the same name, and could not tell which run a change goes to.

        Args:
            run_name: What the run is called while a second run is drawn, or
                None for a lone run, which is not named.
        """

        self._run_name = run_name
        self._write_accessible_name()

    def _write_accessible_name(self) -> None:
        # macOS reads a slider's value as a bare number, so the name carries
        # the unit (`_SettingSliderAccessible`).
        name, unit = self._setting_name
        subject = name if self._run_name is None else f"{name} for {self._run_name}"
        self.slider.setAccessibleName(f"{subject}, {unit}")

    def set_setting(self, setting: SettingReadout) -> None:
        """Write the range, position and text from this tick's setting.

        The slider's signals are blocked while it is written. So a value that
        came *from* the snapshot is never sent back to the run as a new
        setting, which would record a control change the reader did not make.

        The position is not written while the thumb is held. The run keeps its
        setting during a drag, so writing it would pull the thumb back from
        under the pointer on every frame. The value above the slider is still
        written, and it shows the setting in force.

        Args:
            setting: The control as drawn this tick.
        """

        self.slider.decimals = setting.decimals
        self.name_label.setText(setting.name)
        self._setting_name = (setting.name, setting.unit)
        self._write_accessible_name()
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
        self.secondary_label.setText(setting.secondary)
        self.secondary_label.setHidden(not setting.secondary)

    def value(self) -> float:
        """The value the slider's position stands for, in the setting's unit."""

        return self.slider.setting()

    def cancel_hold(self) -> None:
        """Let go of a held thumb without applying its value, and end its preview without a signal.

        The View calls this when the run starts over, by a Reset or an agent
        change, while the thumb is held (`PL-HPD0`). The run's view has already
        dropped the preview, so `preview_ended` is not emitted. Neither is
        `value_changed`, so the release applies nothing to the new run. A thumb
        that is not held is left as it is.
        """

        self._previewing = False
        self.slider.cancel_hold()

    def _on_slider_moved(self, position: int) -> None:
        dial_input = DialInput.RELEASE if self._releasing else DialInput.STEP
        self.value_changed.emit(slider_value(position, self.slider.decimals), dial_input)

    def _on_thumb_pressed(self) -> None:
        """Start a preview where the handle stands, unless the press was on the groove.

        A press on the groove has already applied its value, so a preview
        would label an applied value "not applied" (`PL-57LD`).
        """

        if self.slider.jumping:
            return

        self._previewing = True
        self.preview_moved.emit(slider_value(self.slider.sliderPosition(), self.slider.decimals))

    def _on_thumb_moved(self, position: int) -> None:
        self._previewing = True
        self.preview_moved.emit(slider_value(position, self.slider.decimals))

    def _on_thumb_released(self) -> None:
        """Apply where the thumb was released, then end the preview.

        `QAbstractSlider.setSliderDown` emits `sliderReleased` before it moves
        the value to the thumb's position. Setting the value here applies it
        first, and Qt then finds nothing left to move.
        """

        position = self.slider.sliderPosition()
        previewing, self._previewing = self._previewing, False

        if position != self.slider.value():
            self._releasing = previewing

            try:
                self.slider.setValue(position)
            finally:
                self._releasing = False

        if previewing:
            self.preview_ended.emit()


class NoticeLabel(QLabel):
    """The banner above a run's values: a stopped run or a refused setting, or nothing.

    The banner is word-wrapped and bold. It is drawn in `theme.WARNING`, the
    one warning colour this interface has, unless the caller names another
    colour for a banner that reports no fault. It is hidden rather than blank
    when there is nothing to say, so an empty line never takes up the space a
    warning would.

    A new banner is also announced to assistive technology, because a screen
    reader says nothing when a label's text changes. WCAG 2.2 SC 4.1.3
    (Status Messages) asks that such a message reach a screen reader without
    taking the focus (`PL-J7Z5`). A banner in the warning colour, a failure
    or a refused request, interrupts what is being read, because it asks the
    reader to act. Any other banner, such as the
    countdown to the supported run length or the stop there, waits until
    speech pauses. Qt asks that the interrupting kind be used only where the
    interruption is imperative (`QAccessible.AnnouncementPoliteness`).

    The banner is announced once control returns to the event loop, as it
    stands then. So a banner written twice in one action is read once. A halt
    writes its banner before its frame is drawn and again from the frame, and
    only the second is read. Banners that change in one action in the same
    window are read as one announcement (`announce`), so a halt of every run
    reads each run's banner rather than only the last (`PL-MP92`).

    A label in a View that the dashboard builds again on each Workspace
    switch, or holds in two Areas at once, is built with `announces` False.
    The notice it shows belongs to the dashboard, which announces it once,
    when it is made (`SimulationView`). A label that announced it would read
    a standing refusal again in each new copy (`PL-J7Z5`).

    Args:
        parent: The widget the label is drawn in.
        announces: Whether the label announces each new banner itself.
    """

    def __init__(self, parent: QWidget | None = None, *, announces: bool = True) -> None:
        super().__init__(parent)
        self._announces = announces
        self.setWordWrap(True)
        font = QFont(self.font())
        font.setBold(True)
        self.setFont(font)
        self._notice: str | None = None
        self._color: str | None = None
        # The topic of the banner on screen, and of the one last announced.
        # Each is None while the banner is hidden.
        self._topic: str | None = None
        self._announced_topic: str | None = None
        self.set_notice(None)

    def set_notice(
        self, text: str | None, color: str = WARNING, *, topic: str | None = None
    ) -> None:
        """Show `text` in `color`, or hide the banner when there is none, and announce a new one.

        Args:
            text: The banner this tick, such as `dashboard_frame.notice`'s
                result.
            color: A theme colour. `theme.WARNING` unless the banner reports
                no fault, such as a stop at the supported run length.
            topic: What the banner is about, where its text changes while its
                topic does not, as `dashboard_frame.Notice.topic` gives it.
                The banner is announced when its topic changes. It is the
                text itself by default.
        """

        # A stylesheet write restyles the label, so it is made only when the
        # colour changes rather than on every frame.
        if color != self._color:
            self.setStyleSheet(foreground_stylesheet(color))
            self._color = color

        self._notice = text
        self._topic = None if text is None else text if topic is None else topic
        self.setText(text if text is not None else "")
        self.setHidden(text is None)

        if self._announces and self._topic != self._announced_topic:
            _announcements_of(self).add(self, self, self._take_announcement)

    def notice(self) -> str | None:
        """The banner's text, or None while it is hidden."""

        return self._notice

    def _take_announcement(self) -> tuple[str, bool] | None:
        """Return the banner on screen and whether it interrupts, if its topic is new.

        It returns None while the banner is hidden, or while its topic is the
        one last announced. Either way the topic on screen becomes the one
        last announced.
        """

        announcement = (
            (self._notice, self._color == WARNING)
            if self._notice is not None and self._topic != self._announced_topic
            else None
        )
        self._announced_topic = self._topic

        return announcement


#: A request for one announcement: it returns the message and whether it
#: interrupts, or None when there is nothing to read by then.
_AnnouncementRequest = Callable[[], tuple[str, bool] | None]


class _WindowAnnouncements(QObject):
    """The announcements one window asks for before control returns to the event loop.

    They are sent as one announcement. WAI-ARIA 1.2's definition of `aria-live`
    says that a screen reader given an assertive update "could potentially clear
    the speech queue of previous updates", and that it "MAY choose to clear
    queued changes when an assertive change occurs". So two announcements sent
    in one action can leave a screen-reader user hearing only the second. When
    every run halts at once, that was each compared run's halt but the last
    (`PL-MP92`). The one announcement interrupts what is being read if any of
    the messages in it does, and it repeats no message. The messages that
    interrupt come first, so the ones that ask the reader to act are heard even
    if a later announcement cuts this one short. Within each group, the messages
    keep the order they were asked for. Each message but the last ends with a
    full stop, so a screen reader pauses between two messages.

    Each request is read when the announcement is sent, so a banner written twice
    in one action is read as the action leaves it. A request from a widget that
    has been deleted by then is dropped. The object is a child of its window, so
    a window that is closed and deleted takes its unsent requests with it, and two
    windows never share one.

    Args:
        window: The window whose announcements this sends.
    """

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self._requests: dict[object, tuple[QWidget, _AnnouncementRequest]] = {}
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(0)
        self._timer.timeout.connect(self._send)

    def add(self, key: object, source: QWidget, request: _AnnouncementRequest) -> None:
        """Ask for `request` to be read with the window's other announcements.

        Args:
            key: What the request is for. A second request under the same key
                before the announcement is sent keeps the first one's place.
            source: The widget that shows the message.
            request: Returns the message and whether it interrupts, or None.
        """

        self._requests.setdefault(key, (source, request))
        self._timer.start()

    def _send(self) -> None:
        """Send every request that still has a message, as one announcement."""

        requests, self._requests = self._requests, {}
        readings: dict[str, tuple[QWidget, bool]] = {}

        for source, request in requests.values():
            if not isValid(source):
                continue

            reading = request()

            if reading is None:
                continue

            message, interrupts = reading
            earlier = readings.get(message)

            if earlier is None:
                readings[message] = (source, interrupts)
            elif interrupts:
                readings[message] = (earlier[0], True)

        if not readings:
            return

        # sorted() keeps the order asked for among messages with the same key.
        ordered = sorted(readings.items(), key=lambda reading: not reading[1][1])
        messages = [_ended_as_sentence(message) for message, _ in ordered[:-1]]
        messages.append(ordered[-1][0])
        source, interrupt = ordered[0][1]
        _send_announcement(source, " ".join(messages), interrupt=interrupt)


#: The marks that end a sentence, after which a screen reader pauses.
_SENTENCE_ENDS: Final = (".", "!", "?")


def _ended_as_sentence(message: str) -> str:
    """Return `message` with a full stop added where it ends with no mark that ends a sentence.

    Some messages are shown without one, such as "Select an instant to branch
    at". Read before another message in one announcement, such a message would
    run into the next with no pause (`PL-MP92`).
    """

    return message if message.endswith(_SENTENCE_ENDS) else f"{message}."


def _announcements_of(widget: QWidget) -> _WindowAnnouncements:
    """Return the announcements of `widget`'s window, made the first time they are asked for."""

    window = widget.window()
    announcements = window.findChild(
        _WindowAnnouncements, "", Qt.FindChildOption.FindDirectChildrenOnly
    )

    return _WindowAnnouncements(window) if announcements is None else announcements


def announce(source: QWidget, message: str, *, interrupt: bool) -> None:
    """Ask assistive technology to read `message` once control returns to the event loop.

    The focus does not move. Every announcement that `source`'s window asks for
    in the same action is read as one (`_WindowAnnouncements`, `PL-MP92`).

    Args:
        source: The widget that shows the message.
        message: What to read, which is the text the widget shows.
        interrupt: True to interrupt what is being read, for a message that
            asks the reader to act. False to wait until speech pauses.
    """

    _announcements_of(source).add(object(), source, lambda: (message, interrupt))


def _send_announcement(source: QWidget, message: str, *, interrupt: bool) -> None:
    """Ask assistive technology to read `message` now, without moving the focus.

    Qt passes the request to each platform's screen reader interface: AT-SPI
    on Linux, UI Automation on Windows and the accessibility notifications on
    macOS. It does nothing where no screen reader is running.
    """

    announcement = QAccessibleAnnouncementEvent(source, message)
    announcement.setPoliteness(
        QAccessible.AnnouncementPoliteness.Assertive
        if interrupt
        else QAccessible.AnnouncementPoliteness.Polite
    )
    QAccessible.updateAccessibility(announcement)


class FailureDetails(QWidget):
    """The details under a failed run's banner, for a report of the fault, and nothing otherwise.

    The banner gives the user plain words. The details, the build, the
    exception's own message and the failure log's path, are written for a
    developer, so they stay behind "Show details" until asked for. "Copy
    details" puts them on the clipboard, and the line under them links the
    project's issue page (`dashboard_frame.failure_details`,
    `dashboard_frame.report_fault_text`, `PL-XWCH`). The widget is hidden while
    the run has not failed, and folds the details away again when a new
    failure's details replace them.

    Attributes:
        toggle: The button that shows or hides the details.
        details_text: The details, selectable so that part of them can be copied.
        copy_button: The button that copies the details to the clipboard.
        report_text: The line that says how to report the fault.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.toggle = QPushButton(SHOW_FAILURE_DETAILS_LABEL)
        self.toggle.setStyleSheet(outlined_button_stylesheet())
        self.toggle.setCheckable(True)
        self.details_text = styled_label("", color=INK, wrap=True)
        self.details_text.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        self.copy_button = QPushButton(COPY_FAILURE_DETAILS_LABEL)
        self.copy_button.setStyleSheet(outlined_button_stylesheet())
        self.report_text = styled_label("", color=INK, wrap=True)
        self.report_text.setTextFormat(Qt.TextFormat.RichText)
        self.report_text.setOpenExternalLinks(True)
        # A label lets only the mouse follow a link by default, so the link is
        # also put in the tab order and followed with Enter (WCAG 2.2 SC 2.1.1).
        self.report_text.setTextInteractionFlags(
            Qt.TextInteractionFlag.LinksAccessibleByMouse
            | Qt.TextInteractionFlag.LinksAccessibleByKeyboard
        )
        self.report_text.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self._details: str | None = None
        self._run_name: str | None = None

        buttons = QHBoxLayout()
        buttons.setContentsMargins(0, 0, 0, 0)
        buttons.addWidget(self.toggle)
        buttons.addWidget(self.copy_button)
        buttons.addStretch(1)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.addLayout(buttons)
        column.addWidget(self.details_text)
        column.addWidget(self.report_text)

        self.toggle.toggled.connect(self._show_details)
        self.copy_button.clicked.connect(self.copy_details)
        self.set_details(None, None, run_name=None)

    def set_details(
        self, details: str | None, issues_url: str | None, *, run_name: str | None
    ) -> None:
        """Show the details of a failure, or hide the widget when the run has not failed.

        The link to the issue page is drawn in the line's own `INK`, and Qt
        underlines it, so the host appearance does not choose its colour.

        Args:
            details: `dashboard_frame.failure_details`'s result this tick.
            issues_url: The project's issue page, or None where the build kept
                no metadata (`app_metadata.APP_ISSUES_URL`).
            run_name: What the run is called while a second run is drawn, or
                None. A screen reader then names the run in each button's
                name, because two runs' buttons read alike.
        """

        report = report_fault_text(issues_url, link_colour=INK)

        if details != self._details:
            # New details are folded away, so a reader who opened one failure's
            # details does not read them as the next failure's.
            self.toggle.setChecked(False)

        self._details = details
        self._run_name = run_name
        self.copy_button.setAccessibleName(self._named(COPY_FAILURE_DETAILS_LABEL))
        self.details_text.setText(details or "")
        self.report_text.setText(report)
        self.setHidden(details is None)
        self._show_details(self.toggle.isChecked())

    def details(self) -> str | None:
        """The details this widget holds, or None while the run has not failed."""

        return self._details

    def copy_details(self) -> None:
        """Put the details on the clipboard, as plain text."""

        if self._details is not None:
            QApplication.clipboard().setText(self._details)

    def _named(self, label: str) -> str:
        return label if self._run_name is None else f"{label} for {self._run_name}"

    def _show_details(self, shown: bool) -> None:
        label = HIDE_FAILURE_DETAILS_LABEL if shown else SHOW_FAILURE_DETAILS_LABEL
        self.toggle.setText(label)
        self.toggle.setAccessibleName(self._named(label))
        self.details_text.setHidden(not shown)
        self.copy_button.setHidden(not shown)
        self.report_text.setHidden(not shown)


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
        """Rewrite every line of the question from the runs as they stand now.

        The question names how much work starting over discards. The run
        view rewrites the question on each refresh, so the figure the reader
        decides on matches the work as it stands now (`PL-WM5P`). Every run holds
        while the dialog is open (`RunView.hold_while`, `PL-TPBH`), so the
        figure no longer changes. The rewrite is kept as a guard against a
        later path that moves a run under an open question.

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
    """One mark's row: a bullet, the row's text wrapping under itself, and a Remove button.

    The bullet has a column of its own because a row can wrap. A wrapped row's
    continuation can be a whole clause that names a run, such as
    `Run 2 reached`. If the continuation started at the same margin as every
    row, it would look like a row of its own (`PL-FPY2`). Here a continuation
    starts under the text, to the right of the column where the next row's
    bullet sits. A standing is the clause that says whether a run has reached
    a mark. So a reader can tell which mark a standing belongs to from its
    position rather than from its wording.

    The Remove button is on the row it removes, so a press removes the mark
    the reader is looking at and no other (`PL-G1JM`). Its accessible name
    adds the row's text, so a screen reader names the mark the button
    removes.

    Attributes:
        bullet_label: Where the row starts.
        text_label: The row itself.
        remove_button: Removes this row's mark from every run.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.bullet_label = styled_label(
            MARK_ROW_BULLET, color=MUTED, size_px=METRIC_QUALIFIER_SIZE
        )
        self.text_label = styled_label("", color=MUTED, size_px=METRIC_QUALIFIER_SIZE, wrap=True)
        self.remove_button = QPushButton(REMOVE_MARK_LABEL)
        self.remove_button.setStyleSheet(outlined_button_stylesheet())
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(MARK_ROW_BULLET_SPACING)
        row.addWidget(self.bullet_label, 0, Qt.AlignmentFlag.AlignTop)
        row.addWidget(self.text_label, 1)
        row.addWidget(self.remove_button, 0, Qt.AlignmentFlag.AlignTop)

    def set_text(self, text: str) -> None:
        """Write the row's text, and name the mark in its Remove button's accessible name."""

        self.text_label.setText(text)
        self.remove_button.setAccessibleName(f"{REMOVE_MARK_LABEL} {text}")


class MarkList(QWidget):
    """One bookmark collection: a heading, a row for each mark, and why a removal was refused.

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
    added or removed when the number of marks changes. Each row carries the
    button that removes it, so the list is shown once and no row has to be
    selected first (`PL-G1JM`).

    After a removal, the mark below moves up into the pressed row, under the
    pointer. So a press of any Remove button in this list within the
    platform's double-click interval of the last removal is ignored, and a
    double-click removes one mark rather than two. A press after that
    interval is a press of the mark the row then shows. The Undo button keeps
    the same interval, because after an undo the button can offer the
    removal before it, in the same place.

    Under the rows, a line names the mark last removed from this list, with
    an Undo button that puts it back (`PL-5GX4`). The line has no time
    limit. It stays until the marks change in some other way, so a reader
    who notices a mistake late can still undo it.

    Attributes:
        remove_requested: Emitted with a row's position in the list when its
            Remove button is pressed.
        undo_requested: Emitted when the Undo button is pressed.
        heading_label: The collection's name.
        empty_label: The line that stands in for the rows when the collection
            is empty.
        rows: One `MarkRow` per mark, in the order they were added.
        undo_label: Names the mark that the Undo button puts back.
        undo_button: Puts the mark back.
        remove_notice: Why the last removal from this list was refused,
            hidden when there is nothing to say.
    """

    remove_requested = Signal(int)
    undo_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.heading_label = styled_label("", color=INK, bold=True)
        self.empty_label = styled_label("", color=MUTED, size_px=METRIC_QUALIFIER_SIZE, wrap=True)
        self.rows: list[MarkRow] = []
        self.undo_label = styled_label("", color=MUTED, size_px=METRIC_QUALIFIER_SIZE, wrap=True)
        self.undo_button = QPushButton(UNDO_REMOVAL_LABEL)
        self.undo_button.setStyleSheet(outlined_button_stylesheet())
        self.undo_button.clicked.connect(self._ask_to_undo)
        self.remove_notice = NoticeLabel(announces=False)
        # When this list last asked for a removal or an undo, so that the
        # second press of a double-click is not taken for a press of the next
        # mark or of the next undo.
        self._last_press = QElapsedTimer()
        self._rows_column = QVBoxLayout()
        self._rows_column.setContentsMargins(0, 0, 0, 0)
        self._rows_column.setSpacing(MARK_ROW_SPACING)
        self._undo_row = QWidget()
        undo_row = QHBoxLayout(self._undo_row)
        undo_row.setContentsMargins(0, 0, 0, 0)
        undo_row.setSpacing(MARK_ROW_BULLET_SPACING)
        undo_row.addWidget(self.undo_label, 1)
        undo_row.addWidget(self.undo_button, 0, Qt.AlignmentFlag.AlignTop)
        self._undo_row.setHidden(True)
        self.undo_button.setDisabled(True)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(BOOKMARK_ROW_SPACING)
        column.addWidget(self.heading_label)
        column.addWidget(self.empty_label)
        column.addLayout(self._rows_column)
        column.addWidget(self._undo_row)
        column.addWidget(self.remove_notice)

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
            row.remove_button.clicked.connect(partial(self._ask_to_remove, len(self.rows)))
            self._rows_column.addWidget(row)
            self.rows.append(row)

        while len(self.rows) > len(listing.rows):
            row = self.rows.pop()
            self._rows_column.removeWidget(row)
            row.hide()
            row.deleteLater()

        for row, text in zip(self.rows, listing.rows, strict=True):
            row.set_text(text)

    def remove_buttons(self) -> list[QPushButton]:
        """Return each row's Remove button, from the first row to the last."""

        return [row.remove_button for row in self.rows]

    def set_undo(self, mark_text: str | None) -> None:
        """Offer to put back the mark that `mark_text` names, or offer nothing where it is None.

        The button is disabled by the same expression that hides it, as every
        control on this dashboard is (`tools/agent_identity_check.py`).
        """

        offered = mark_text is not None
        self.undo_label.setText(REMOVED_MARK_TEMPLATE.format(mark=mark_text) if offered else "")
        self.undo_button.setAccessibleName(
            UNDO_REMOVAL_NAME_TEMPLATE.format(mark=mark_text) if offered else UNDO_REMOVAL_LABEL
        )
        self.undo_button.setDisabled(not offered)
        self._undo_row.setHidden(not offered)

    def _ask_to_remove(self, row: int, *_: object) -> None:
        """Ask for the mark in `row` to be removed, unless this list just asked for something."""

        if self._pressed_just_now():
            return

        self.remove_requested.emit(row)

    def _ask_to_undo(self, *_: object) -> None:
        """Ask for the last removal to be undone, unless this list just asked for something."""

        if self._pressed_just_now():
            return

        self.undo_requested.emit()

    def _pressed_just_now(self) -> bool:
        """Whether this list took a press within the double-click interval, else note this one."""

        if (
            self._last_press.isValid()
            and self._last_press.elapsed() < QApplication.doubleClickInterval()
        ):
            return True

        self._last_press.start()

        return False

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
    """The case's two collections of marks, and below them the forms that add marks.

    Each Area that holds a `views.BookmarksView` shows its own copy of this
    panel (`PL-9YPR`). The two lists come first, so an Area too short for the
    whole panel shows what is marked before it shows the forms. Each mark is
    listed once, with its Remove button on its row (`PL-G1JM`). The forms are
    in the same View rather than in a window of their own, so no window opens
    over the readouts when a reader edits a mark (`PL-CHX0`).

    Attributes:
        times: The marked instants, with each run's standing on each.
        targets: The marked heights, with each run's standing on each.
        editor: The forms in which the reader adds marks. The view connects
            their buttons.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.times = MarkList()
        self.targets = MarkList()
        self.editor = MarkEditor()
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(BOOKMARK_SECTION_SPACING)
        column.addWidget(self.times)
        column.addWidget(self.targets)
        column.addWidget(self.editor)

    def set_panel(self, panel: BookmarkPanel) -> None:
        """Draw both collections from one tick's result.

        Each list that a halt withdrew is shown again.

        Args:
            panel: `dashboard_frame.bookmark_panel`'s result this tick.
        """

        self.times.set_listing(panel.times)
        self.targets.set_listing(panel.targets)
        self.times.show()
        self.targets.show()

    def withdraw(self) -> None:
        """Hide every list of marks, because the halt could not work out their standings.

        A mark's standing says whether the run has reached it. The halt path calls this
        method when restating the panel raised an exception
        (`SimulationView._restate_bookmark_panel`). The rows on screen come from the last
        frame. On a failed run, a row that still shows a mark as still to come is a stale
        claim. The halt restates the panel to remove that claim (`PL-YHR3`). Each row's
        Remove button is hidden with its row, so the reader cannot remove a mark through a
        row they cannot see (`PL-F5KT`). The forms stay on screen. The next call to
        `set_panel` shows every list again.
        """

        self.times.hide()
        self.targets.hide()

    def show_undo(self, undo: MarkUndo | None) -> None:
        """Offer to undo the last removal under the list it came from, and nothing under the other.

        Args:
            undo: The removal that an Undo would reverse, or None where there
                is none to offer.
        """

        for button, listed in (
            (MarkButton.REMOVE_TIME, self.times),
            (MarkButton.REMOVE_TARGET, self.targets),
        ):
            listed.set_undo(undo.mark_text if undo is not None and undo.button is button else None)

    def show_refusal(self, refusal: MarkRefusal | None) -> None:
        """Show why the last edit was refused under the list or form it came from. Clear the others.

        Args:
            refusal: The last refusal, or None where the last edit was accepted.
        """

        for button, notice in (
            (MarkButton.ADD_TIME, self.editor.add_time_notice),
            (MarkButton.REMOVE_TIME, self.times.remove_notice),
            (MarkButton.ADD_TARGET, self.editor.add_target_notice),
            (MarkButton.REMOVE_TARGET, self.targets.remove_notice),
        ):
            notice.set_notice(
                refusal.text if refusal is not None and refusal.button is button else None
            )


class ForkPanel(QWidget):
    """Where a user takes a branch: which point to open it at, and the two buttons.

    The dashboard builds the panel, as it builds the marks, and no `RunView`
    does. Each Area that holds a `views.BranchView` shows its own copy
    (`PL-9YPR`). The points the panel offers belong to the *case*: the
    trunk's keyframes and the marks the trunk has passed. A control copied
    into each displayed run would give a branch a control that can only
    refuse (`docs/ARCHITECTURE.md` § "Where new code belongs").

    The panel decides nothing. A function settles which points are offered,
    how they are rendered and whether the control is shown at all, so a test
    can check them without a display (`dashboard_frame.fork_offer`). This
    class writes that function's result into widgets.

    **The panel keeps the `ForkPoint`s it was given, in the selector's order,
    and returns one of them** (`selected_point`). So the caller acts on the
    point it was handed, either a keyframe's `CaseInstant` or a mark itself.
    It does not act on the string a reader sees, or on a value read back out
    of Qt. The selected point is found in the list by `ForkPoint` equality,
    never by `findData`, for two reasons.
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
        point_selector: The points a branch may be opened at: the recorded
            control events and the marks the trunk has passed.
        take_button: Takes the branch; `clicked` is connected by the view.
        here_button: Takes the branch where the trunk is paused, and is on
            screen only while `dashboard_frame.fork_offer` offers that.
            `clicked` is connected by the view.
        lock_text: Why the control is not offered, shown where the control
            was.
        pin_text: Shown above the controls while the Workspace is pinned to
            one run, saying that a branch taken here will not be drawn in it
            (`PL-RXR8`).
        notice: Why the last requested branch was refused.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.point_selector = SelectorComboBox()
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
        self.pin_text = styled_label("", color=MUTED, wrap=True)
        self.pin_text.setHidden(True)
        self.notice = NoticeLabel(self, announces=False)
        self._point_label = styled_label(FORK_POINT_LABEL, color=MUTED)
        label_control(
            self._point_label, self.point_selector, control_name(FORK_POINT_LABEL, FORK_POINT_KIND)
        )
        # The points behind the selector's entries, one per entry, in the
        # selector's order. `selected_point` returns one of them, and
        # `set_offer` rebuilds the entries when a new offer differs from them.
        self._offered: tuple[ForkPoint, ...] = ()

        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(BOOKMARK_ROW_SPACING)
        # The panel has no heading of its own: the Area header above it says
        # "Branch", and so does the button (`PL-8LMY`). The pin's notice comes
        # first, so it is read before either button is pressed (`PL-RXR8`).
        column.addWidget(self.pin_text)
        controls = QHBoxLayout()
        controls.setSpacing(CONTROL_ROW_SPACING)
        controls.addWidget(self._point_label)
        controls.addWidget(self.point_selector)
        controls.addWidget(self.take_button)
        controls.addWidget(self.lock_text)
        controls.addStretch(1)
        column.addLayout(controls)
        # The refusal sits directly under the selector's row and above the here
        # button. A review (`PL-9YPR`) found it below the fold of a short Area
        # when it was the panel's last row, so a refused press changed nothing
        # a user could see.
        column.addWidget(self.notice)
        here_row = QHBoxLayout()
        here_row.setSpacing(CONTROL_ROW_SPACING)
        here_row.addWidget(self.here_button)
        here_row.addStretch(1)
        column.addLayout(here_row)

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

    def set_offer(self, offer: ForkOffer, selected: ForkPoint | None) -> None:
        """Draw one tick's offer, with `selected` as the selected point.

        The dashboard owns the selection and passes it with every offer
        (`dashboard_frame.kept_fork_selection`). Every copy of the panel then
        shows the same point, and a copy that is built later shows the point
        the user chose (`PL-9YPR`). Where the offer does not hold
        `selected`, and where `selected` is None, nothing is selected. So
        `selected_point` returns None, and a press is refused with a notice
        that says so (`PL-J12Z`). Qt selects the first entry whenever an
        emptied selector is refilled, which is why the index is set on every
        call.

        The entries are rebuilt only when they have changed. A running trunk
        adds an entry at every setting change and at every mark its clock
        reaches, and a selector rebuilt every frame would close under a
        reader's click. Both the rebuild and the index are written under a
        `QSignalBlocker`, so that the dashboard writing the control is not
        mistaken for a reader operating it.

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
            selected: The point to show as selected, or None for no point.
        """

        with QSignalBlocker(self.point_selector):
            if offer.points != self._offered:
                self.point_selector.clear()

                for point in offer.points:
                    self.point_selector.addItem(point.label, userData=float(point.instant_s))

                self._offered = offer.points

            self.point_selector.setCurrentIndex(
                offer.points.index(selected) if selected in offer.points else -1
            )

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
        self.pin_text.setText(offer.pinned_notice)
        self.pin_text.setHidden(not offer.pinned_notice)
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


class MarkButton(Enum):
    """Which edit of the marks a button asks for, so its refusal is shown beside it.

    An Add button belongs to one of the two forms. A Remove button sits on
    each listed mark, and a refusal of a removal is shown under its list.
    """

    ADD_TIME = "add time"
    REMOVE_TIME = "remove time"
    ADD_TARGET = "add target"
    REMOVE_TARGET = "remove target"


@dataclass(frozen=True, slots=True)
class MarkRefusal:
    """Why an edit of the marks was refused, and the button that asked for it.

    Attributes:
        button: The button the reader pressed. The refusal is shown under it.
        text: What the refusal says.
    """

    button: MarkButton
    text: str


@dataclass(frozen=True, slots=True)
class MarkUndo:
    """The removal that the Undo button would reverse, and the list it was removed from.

    Attributes:
        button: The Remove button's kind, `REMOVE_TIME` or `REMOVE_TARGET`,
            which names the list the Undo is offered under.
        mark_text: The removed mark's own words (`dashboard_frame.stated_mark`).
    """

    button: MarkButton
    mark_text: str


@dataclass(frozen=True, slots=True)
class MarkEntry:
    """What the reader has entered in the marks editor's two forms.

    The dashboard keeps the last entry and writes it into every copy of the
    editor (`MarkEditor.set_entry`). So two Areas that show the Bookmarks View
    show the same entry. A copy built after a switch of Workspace shows the
    entry that the reader left there (`PL-CHX0`).

    Attributes:
        instant_s: The instant to mark, in whole seconds.
        time_name: The text of the time bookmark's name field.
        compartment_row: The selected row of the compartment selector.
        height_mac: The height, in multiples of the running agent's 1 MAC.
        target_name: The text of the target's name field.
    """

    instant_s: int
    time_name: str
    compartment_row: int
    height_mac: float
    target_name: str

    def time_bookmark(self) -> TimeBookmark:
        """The time bookmark that the instant and the name describe.

        Raises:
            SimulationConfigurationError: If `CaseInstant` refuses the
                instant, or `TimeBookmark` refuses the name. The editor's
                instant control has the same range, so an instant typed there
                is never refused.
        """

        return TimeBookmark(CaseInstant(self.instant_s), _entered_name(self.time_name))

    def mac_target(self) -> MacTarget:
        """The MAC target that the compartment, the height and the name describe.

        The compartment row counts in `COMPARTMENT_QUANTITIES`, the order in
        which the editor lists the compartments.

        Raises:
            ValueError: If the compartment row selects no compartment.
            SimulationConfigurationError: If `MacTarget` refuses the height
                or the name.
        """

        if not 0 <= self.compartment_row < len(COMPARTMENT_QUANTITIES):
            raise ValueError(
                f"the compartment row {self.compartment_row} selects none of the "
                f"{len(COMPARTMENT_QUANTITIES)} compartments that a target can mark"
            )

        return MacTarget(
            COMPARTMENT_QUANTITIES[self.compartment_row],
            MacMultiple(self.height_mac),
            _entered_name(self.target_name),
        )

    def without_names(self) -> MarkEntry:
        """This entry with both name fields emptied, as they are after a mark is added.

        The instant, the compartment and the height are kept. Adding a second
        mark near the first is the common case. A name is emptied because
        reusing it would give two marks the same name.
        """

        return replace(self, time_name="", target_name="")

    def held_within(self, reachable_height_mac: float) -> MarkEntry:
        """This entry as the editor holds it under the height bound.

        The height is held within the bound, as the height control holds it.
        So a copy built later shows what the copies on screen show
        (`PL-CHX0`).
        """

        return replace(
            self,
            height_mac=round(
                min(max(self.height_mac, MAC_DISPLAY_RESOLUTION_MAC), reachable_height_mac),
                MAC_DISPLAY_DECIMALS,
            ),
        )


def _entered_name(text: str) -> str | None:
    """What a name field says, or `None` where the reader left it empty.

    An empty field means "list it under its own value" rather than "name it
    nothing". `bookmarks.TimeBookmark` refuses a blank string in order to
    keep that distinction.
    """

    entered = text.strip()

    return entered or None


class MarkEditor(QWidget):
    """The two forms in which the reader adds both kinds of mark.

    The editor sits in the Bookmarks View, below the two lists of marks. Each
    row of those lists carries the button that removes its mark
    (`MarkList`), so the editor holds no list of its own and each mark is
    listed once (`PL-G1JM`). Each Area that shows that View holds its own copy
    (`BookmarksPanel`). The editor opens no window. A window could cover the
    readouts that `docs/INTERFACE.md` § "Minimum displayed outputs" requires
    while a run plays, and on Wayland the application can neither place a
    window nor find out where the reader has dragged it. An Area cannot cover
    those readouts, because the layout keeps them in a region outside every
    Area (`PL-CHX0`).

    One editor serves both kinds of mark. The reference simulator uses that
    shape, and `PL-LPLD` was scoped on it. Both forms are visible at once,
    and each has its own Add button, on the row of the last field it reads.
    A tab or a kind selector would turn the choice of which kind is being
    added into a mode. The two collections also have different fields, not
    the same fields under a different kind, so a shared form would have
    nothing in common to hold. Each Add button shows its own refusal directly
    under its form, so the refusal is in sight of the button that was
    pressed.

    **Each input control declares its own colours, as a palette**
    (`PL-RKRY`). Their fills and the spin boxes' steppers paint from palette
    roles. The View that holds the editor declares its surface with a
    stylesheet, and a stylesheet on a parent makes the controls under it take
    the application palette rather than the parent's. So each control
    declares the roles itself (`declare_interface_colours`).

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
        entry_edited: Emitted when a field changes, unless `set_entry` wrote
            the change. The dashboard connects it and writes the new entry
            into every other copy of the editor.
        instant_spin: The instant to mark, in seconds.
        instant_preview: That instant in the compound form the clock uses, so
            that no reader has to convert between the entry and the display.
        time_label_edit: The optional name for a time bookmark.
        add_time_button: Adds the time bookmark. The view connects its
            `clicked` signal.
        add_time_notice: Why the last press of `add_time_button` was
            refused, hidden when there is nothing to say.
        compartment_combo: The compartment whose value a target is compared
            against.
        height_spin: The height, in multiples of the running agent's 1 MAC.
        target_label_edit: The optional name for a target.
        add_target_button: Adds the target.
        add_target_notice: Why the last press of `add_target_button` was
            refused.
    """

    entry_edited = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.instant_spin = QSpinBox()
        self.instant_spin.setRange(0, MAXIMUM_ELAPSED_SIMULATION_TIME_S)
        self.instant_spin.setSuffix(INSTANT_ENTRY_SUFFIX)
        self.instant_preview = styled_label(
            format_elapsed(0), color=MUTED, size_px=METRIC_QUALIFIER_SIZE
        )
        self.instant_spin.valueChanged.connect(self._refresh_instant_preview)
        self.time_label_edit = QLineEdit()
        self.time_label_edit.setPlaceholderText(MARK_NAME_PLACEHOLDER)
        self.add_time_button = QPushButton(ADD_MARK_LABEL)
        self.add_time_notice = NoticeLabel(announces=False)

        self.compartment_combo = FocusedComboBox()
        self.compartment_combo.setStyleSheet(selector_stylesheet())

        for quantity in COMPARTMENT_QUANTITIES:
            self.compartment_combo.addItem(trace_style(quantity).label, userData=quantity.value)

        self.height_spin = QDoubleSpinBox()
        self.height_spin.setDecimals(MAC_DISPLAY_DECIMALS)
        self.height_spin.setSingleStep(MAC_DISPLAY_RESOLUTION_MAC)
        self.height_spin.setSuffix(MAC_UNIT_SUFFIX)
        self.target_label_edit = QLineEdit()
        self.target_label_edit.setPlaceholderText(MARK_NAME_PLACEHOLDER)
        self.add_target_button = QPushButton(ADD_MARK_LABEL)
        self.add_target_notice = NoticeLabel(announces=False)

        for field in (self.instant_spin, self.height_spin):
            wheel_only_with_focus(field)

        for control in (
            self.instant_spin,
            self.time_label_edit,
            self.height_spin,
            self.target_label_edit,
        ):
            declare_interface_colours(control)

        for button in (self.add_time_button, self.add_target_button):
            button.setStyleSheet(outlined_button_stylesheet())

        self.instant_spin.valueChanged.connect(self.entry_edited)
        self.time_label_edit.textChanged.connect(self.entry_edited)
        self.compartment_combo.currentIndexChanged.connect(self.entry_edited)
        self.height_spin.valueChanged.connect(self.entry_edited)
        self.target_label_edit.textChanged.connect(self.entry_edited)

        self._build_layout()
        self.set_reachable_height(DEFAULT_MAXIMUM_TARGET_MAC)

    def _build_layout(self) -> None:
        """Lay out the two forms one above the other, each Add button beside its name field."""

        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(BOOKMARK_SECTION_SPACING)

        times_heading = styled_label(TIME_FORM_HEADING, color=INK, bold=True)
        instant_name = styled_label(INSTANT_FIELD_LABEL, color=MUTED)
        time_label_name = styled_label(MARK_NAME_FIELD_LABEL, color=MUTED)
        times_form = _form_grid(
            (times_heading, times_heading, times_heading),
            (instant_name, self.instant_spin, self.instant_preview),
            (time_label_name, self.time_label_edit, self.add_time_button),
            (self.add_time_notice, self.add_time_notice, self.add_time_notice),
        )

        targets_heading = styled_label(TARGET_FORM_HEADING, color=INK, bold=True)
        compartment_name = styled_label(COMPARTMENT_FIELD_LABEL, color=MUTED)
        height_name = styled_label(HEIGHT_FIELD_LABEL, color=MUTED)
        target_label_name = styled_label(MARK_NAME_FIELD_LABEL, color=MUTED)
        targets_form = _form_grid(
            (targets_heading, targets_heading, targets_heading),
            (compartment_name, self.compartment_combo, self.compartment_combo),
            (height_name, self.height_spin, None),
            (target_label_name, self.target_label_edit, self.add_target_button),
            (self.add_target_notice, self.add_target_notice, self.add_target_notice),
        )

        # Both forms have a "Name" field and an "Add" button, so each is named
        # with its form's kind of mark as well (`control_name`).
        time_name = control_name(MARK_NAME_FIELD_LABEL, TIME_MARK_KIND)
        target_name = control_name(MARK_NAME_FIELD_LABEL, TARGET_MARK_KIND)

        for label, control, name in (
            (instant_name, self.instant_spin, None),
            (time_label_name, self.time_label_edit, time_name),
            (compartment_name, self.compartment_combo, None),
            (height_name, self.height_spin, None),
            (target_label_name, self.target_label_edit, target_name),
        ):
            label_control(label, control, name)

        self.add_time_button.setAccessibleName(control_name(ADD_MARK_LABEL, TIME_MARK_KIND))
        self.add_target_button.setAccessibleName(control_name(ADD_MARK_LABEL, TARGET_MARK_KIND))

        # Both forms give their field names the width of the widest name, so
        # the fields of the two forms start at one edge and read as one column.
        names_width = max(
            name.sizeHint().width()
            for name in (instant_name, time_label_name, compartment_name, height_name)
        )

        for form in (times_form, targets_form):
            # The field names keep the width they need, and the fields take
            # the rest. A wide Area then widens the fields rather than the gap
            # between a name and its field, or the Add button.
            form.setColumnMinimumWidth(0, names_width)
            form.setColumnStretch(1, 1)
            column.addLayout(form)

    def _refresh_instant_preview(self, seconds: int) -> None:
        """Restate the entered instant in the form the clock and the axis use."""

        self.instant_preview.setText(format_elapsed(seconds))

    def set_reachable_height(self, maximum_mac: float) -> None:
        """Bound the height control at what the running agent can actually reach.

        Args:
            maximum_mac: The agent's maximum delivered concentration as a
                multiple of its own 1 MAC. The upper bound is this value
                rounded down to the control's resolution, so the control
                never offers a height that the agent cannot reach. The lower
                bound is one count of the displayed resolution, because every
                run is already at a target of zero before it begins.
        """

        self.height_spin.setRange(MAC_DISPLAY_RESOLUTION_MAC, height_entry_maximum_mac(maximum_mac))

    def entry(self) -> MarkEntry:
        """Return what the two forms hold now."""

        return MarkEntry(
            instant_s=self.instant_spin.value(),
            time_name=self.time_label_edit.text(),
            compartment_row=self.compartment_combo.currentIndex(),
            height_mac=self.height_spin.value(),
            target_name=self.target_label_edit.text(),
        )

    def set_entry(self, entry: MarkEntry) -> None:
        """Write `entry` into the two forms without emitting `entry_edited`.

        The dashboard calls this method to copy what the reader entered in one
        copy of the editor into the others. Each field's signals are blocked,
        so that the copy is not mistaken for the reader editing this one. The
        height control keeps its own range, so a height above the running
        agent's reach is held at that reach, as a typed one is.

        Args:
            entry: The entry to show.
        """

        fields: tuple[QWidget, ...] = (
            self.instant_spin,
            self.time_label_edit,
            self.compartment_combo,
            self.height_spin,
            self.target_label_edit,
        )
        blockers = [QSignalBlocker(field) for field in fields]
        self.instant_spin.setValue(entry.instant_s)
        self.time_label_edit.setText(entry.time_name)
        self.compartment_combo.setCurrentIndex(entry.compartment_row)
        self.height_spin.setValue(entry.height_mac)
        self.target_label_edit.setText(entry.target_name)

        for blocker in blockers:
            blocker.unblock()

        self._refresh_instant_preview(self.instant_spin.value())

    def entered_time_bookmark(self) -> TimeBookmark:
        """The time bookmark the form currently describes (`MarkEntry.time_bookmark`).

        Raises:
            SimulationConfigurationError: As `MarkEntry.time_bookmark` raises it.
        """

        return self.entry().time_bookmark()

    def entered_mac_target(self) -> MacTarget:
        """The MAC target the form currently describes (`MarkEntry.mac_target`).

        Raises:
            SimulationConfigurationError: As `MarkEntry.mac_target` raises it.
        """

        return self.entry().mac_target()

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


class DescribedGraphic(QWidget):
    """A widget that draws a picture of values, and gives a screen reader a text alternative for it.

    Qt describes a plain widget as a client area, which VoiceOver on macOS
    passes over, and nothing a widget paints reaches assistive technology. So
    each such widget reports the role of a graphic, which AT-SPI, UI
    Automation and macOS each report as an image, with a short name and a long
    description. That pair is the text alternative that WCAG 2.2 SC 1.1.1 asks
    of a chart or a diagram (`PL-T9RB`, `PL-R1M6`). A subclass writes both from
    what it last drew, in `graphic_name` and `graphic_description`, and both
    are read when a screen reader asks for them.

    A screen reader that keeps the texts it has read, as the AT-SPI client
    library on Linux does, reads them again only when told that they changed.
    So a subclass calls `report_text_changes` once at the end of its own
    `__init__`, and again after each draw.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        _install_graphic_accessibility()
        # The name and description last reported, or None before the first.
        self._reported_texts: tuple[str, str] | None = None

    def graphic_name(self) -> str:
        """Return the short text alternative, which says what the picture shows.

        Raises:
            NotImplementedError: The subclass does not define its name.
        """

        raise NotImplementedError

    def graphic_description(self) -> str:
        """Return the long text alternative, which gives the values the picture shows.

        Raises:
            NotImplementedError: The subclass does not define its description.
        """

        raise NotImplementedError

    def report_text_changes(self) -> None:
        """Tell assistive technology that the name or the description changed, if either did.

        Qt sends these events for its own widgets when their text changes, as
        `QLabel.setText` does. The first call only records the texts, because
        it comes before any screen reader can have read them.
        """

        texts = (self.graphic_name(), self.graphic_description())
        events = (QAccessible.Event.NameChanged, QAccessible.Event.DescriptionChanged)

        if self._reported_texts is not None:
            for event, before, now in zip(events, self._reported_texts, texts, strict=True):
                if now != before:
                    QAccessible.updateAccessibility(QAccessibleEvent(self, event))

        self._reported_texts = texts


class _DescribedGraphicAccessible(QAccessibleWidget):
    """Describe a `DescribedGraphic` to a screen reader as an image with its text alternative."""

    def __init__(self, graphic: DescribedGraphic) -> None:
        super().__init__(graphic, QAccessible.Role.Graphic)
        self._graphic = graphic

    def text(self, kind: QAccessible.Text) -> str:
        """Return the graphic's name or long description, or Qt's own text for anything else."""

        if kind is QAccessible.Text.Name:
            return self._graphic.graphic_name()

        if kind is QAccessible.Text.Description:
            return self._graphic.graphic_description()

        return QAccessibleWidget.text(self, kind)


def _described_graphic_accessible(key: str, widget: QObject) -> _DescribedGraphicAccessible | None:
    """Return the accessible interface for a `DescribedGraphic`, and nothing for any other object.

    Qt asks each installed factory as `_setting_slider_accessible` describes,
    and keeps the first interface returned.
    """

    if isinstance(widget, DescribedGraphic):
        return _DescribedGraphicAccessible(widget)

    return None


# Whether `_described_graphic_accessible` is installed. Qt keeps one list of
# factories for the process, so one installation serves every graphic.
_graphic_accessibility_installed = False


def _install_graphic_accessibility() -> None:
    """Install `_described_graphic_accessible` the first time a graphic is built.

    PySide6 installs a factory only once a `QApplication` exists, as
    `_install_setting_slider_accessibility` records, and a widget cannot be
    built before one.
    """

    global _graphic_accessibility_installed

    if _graphic_accessibility_installed:
        return

    QAccessible.installFactory(_described_graphic_accessible)
    _graphic_accessibility_installed = True


class FocusRing(QWidget):
    """Draws a ring inside a control's edge while the control has the keyboard focus.

    Under Qt's Fusion style a slider, a combo box drawn by a style sheet, a
    scroll area and a list look the same with and without the focus. A
    `:focus` rule in a slider's or a selector's style sheet changed no pixel
    (`PL-63FQ`). So a keyboard user could not see which control the arrow keys
    would move, which WCAG 2.2 SC 2.4.7 (Focus Visible, Level AA) forbids.

    The ring is a child widget that covers the control, lets the pointer
    through and never takes the focus. So the control keeps its class, its
    style sheet and its size, and nothing moves when the ring appears. The
    ring is `FOCUS_RING_WIDTH` px wide.

    The ring shows only when the focus came from the keyboard, which is when
    Qt sets `WA_KeyboardFocusChange` on the window. Fusion applies the same
    rule to the mark it draws on a button or a check box. A click that moves
    the focus clears the attribute, so a click on a blank part of the page,
    which gives the page's scroll area the focus, draws no ring round the
    whole page. A click on the control that already has the focus leaves the
    ring, as Fusion leaves its own mark.

    Args:
        control: The control to mark. The ring becomes its child.
        colour: The ring's colour, a `theme.py` colour. None draws it in the
            text colour that the control's style sheet sets, which the agent
            selector needs because its text colour follows the running agent.
        radius: The corner radius of the control's edge, in px.
        inset: The width of the control's own edge, in px. The ring is drawn
            inside that edge. So every pixel of the ring changes from the
            control's fill to the ring's colour. WCAG 2.2 SC 2.4.13 (Level
            AAA) asks for that change to be at least 3:1 over an area as
            large as a 2 px perimeter.
    """

    def __init__(
        self, control: QWidget, colour: str | None = INK, radius: int = 0, inset: int = 0
    ) -> None:
        super().__init__(control)
        self._control = control
        self._colour = colour
        self._radius = radius
        self._inset = inset
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setGeometry(control.rect())
        control.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        kind = event.type()

        if kind == QEvent.Type.Resize:
            self.setGeometry(self._control.rect())
        elif kind in (QEvent.Type.FocusIn, QEvent.Type.FocusOut):
            # A scroll bar or a viewport that the control adds later is
            # stacked above the ring, so the ring is raised whenever it may
            # be drawn.
            self.raise_()
            self.update()

        return False

    def showing(self) -> bool:
        """Return whether the ring is drawn: the control has the focus, and the keyboard gave it."""

        window = self._control.window()

        return self._control.hasFocus() and window.testAttribute(
            Qt.WidgetAttribute.WA_KeyboardFocusChange
        )

    def colour(self) -> QColor:
        """Return the colour the ring is drawn in now."""

        if self._colour is None:
            return self._control.palette().color(QPalette.ColorRole.ButtonText)

        return QColor(self._colour)

    def paintEvent(self, event: QPaintEvent) -> None:
        if not self.showing():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, self._radius > 0)
        pen = QPen(self.colour())
        pen.setWidth(FOCUS_RING_WIDTH)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        # A pen is centred on its path, so the path runs half the pen's width
        # inside the control's edge, and the whole ring lies inside that edge.
        inset = self._inset + FOCUS_RING_WIDTH / 2
        radius = max(self._radius - self._inset, 0)
        ring = QRectF(self.rect()).adjusted(inset, inset, -inset, -inset)
        painter.drawRoundedRect(ring, radius, radius)
        painter.end()


class SelectorComboBox(QComboBox):
    """A combo box that draws the arrow marking its list in its own text colour.

    `selector_stylesheet` and `agent_selector_stylesheet` stop the platform
    style drawing the drop-down button, whose edge showed through the rounded
    frame (`PL-9389`). A style sheet cannot draw an arrow without an image
    file, so this class paints one into the space the sheet leaves for it. The
    arrow is a triangle `MENU_ARROW_SIZE` px wide, the size of the View
    chooser's, in the colour the style sheet gives the text. So it is
    the running agent's foreground on the agent selector. It is drawn without
    smoothing, so each of its pixels is the text colour.

    The selector also carries a `FocusRing`, in that same text colour, inside
    its edge.

    Attributes:
        focus_ring: The ring drawn while the selector has the keyboard focus.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.focus_ring = FocusRing(
            self, colour=None, radius=PANEL_RADIUS, inset=CONTROL_BORDER_WIDTH
        )

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        option = QStyleOptionComboBox()
        self.initStyleOption(option)
        button = self.style().subControlRect(
            QStyle.ComplexControl.CC_ComboBox, option, QStyle.SubControl.SC_ComboBoxArrow, self
        )
        half_width = MENU_ARROW_SIZE // 2
        left = button.center().x() - half_width + 1
        top = button.center().y() - half_width // 2
        painter = QPainter(self)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.palette().color(QPalette.ColorRole.ButtonText))
        painter.drawPolygon(
            QPolygon(
                [
                    QPoint(left, top),
                    QPoint(left + MENU_ARROW_SIZE, top),
                    QPoint(left + half_width, top + half_width),
                ]
            )
        )
        painter.end()


class _WheelOnlyWithFocus(QObject):
    """An event filter that hands a wheel event to the widget's parent while the widget lacks focus.

    `wheel_only_with_focus` installs one on each widget it is given.
    """

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if (
            event.type() is QEvent.Type.Wheel
            and isinstance(watched, QWidget)
            and not watched.hasFocus()
        ):
            # Ignoring the event makes Qt offer it to each parent in turn, so
            # the scroll area that holds the widget scrolls instead.
            event.ignore()
            return True

        return False


def wheel_only_with_focus(widget: QWidget) -> None:
    """Make `widget` change its value on a mouse wheel only once it has focus.

    Qt's combo box, spin boxes and date field change their value on a wheel
    event even without focus. The Areas sit in a page that scrolls, and a View
    taller than its Area scrolls inside it. So a reader scrolling past such a
    control would change its value without meaning to, and often without seeing
    the change (`PL-B396`, `PL-8FSN`, `PL-CHX0`). Once the control has this
    filter, a wheel over it scrolls whatever holds it. A click or the keyboard
    gives the control focus, and the wheel then works as usual.

    The focus policy becomes `StrongFocus`. A spin box's default policy,
    `WheelFocus`, would give the control focus on the first wheel event and
    so let that event change it.
    """

    widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    widget.installEventFilter(_WheelOnlyWithFocus(widget))


def label_control(label: QLabel, control: QWidget, name: str | None = None) -> None:
    """Make `label` the label that assistive technology gives `control`, and name the control.

    The label becomes the control's buddy. Qt reports a buddy to each
    platform's accessibility interface as the control's label. On Linux and
    macOS, Qt names a selector by the entry it shows and takes what the
    selector is for from that label alone (`QAccessibleComboBox::text` in Qt
    6.12). So a selector with no buddy reaches a screen reader there as, for
    example, "Sevoflurane" and never as "Agent" (`PL-RK9Z`). Windows names a
    selector by its accessible name, so the control is given one as well. A
    spin box or an entry field takes the name on every platform.

    A `name` is given to the label as well as to the control, while the label
    still shows its own text. Qt reports a label by its accessible name where
    it has one. So on Linux and macOS a selector is said to be for "Playback,
    Run 2" and not for "Playback" alone (`PL-YSFX`). A caller whose name
    changes calls this again with the new name. Only a name that differs is
    written, so a name written again on each frame sends a screen reader no
    change.

    Args:
        label: The label shown beside the control.
        control: The control the label names.
        name: The name for a screen reader, where the label's text alone does
            not say which control it is, such as one of two fields called
            "Name" (`dashboard_frame.control_name`). It is the label's text by
            default.

    Raises:
        ValueError: `name` does not start with the label's text. A name that
            starts with the label shown is what WCAG 2.2's Understanding
            document for SC 2.5.3 (Label in Name) calls best practice, and it
            lets a user of speech input say the label they see.
    """

    if name is not None and not name.startswith(label.text()):
        raise ValueError(
            f"The name {name!r} for a screen reader does not start with the label "
            f"shown beside its control, {label.text()!r}. Start the name with the "
            "label, as dashboard_frame.control_name does."
        )

    label.setBuddy(control)
    spoken = label.text() if name is None else name

    if control.accessibleName() != spoken:
        control.setAccessibleName(spoken)

    if label.accessibleName() != ("" if name is None else name):
        label.setAccessibleName("" if name is None else name)


class FocusedComboBox(SelectorComboBox):
    """A combo box that a mouse wheel changes only once it has focus (`wheel_only_with_focus`).

    Without it, a wheel over the agent cost View's selectors would change the
    unit, or the agent whose price is shown, and emit `activated` as if the
    reader had picked (`PL-B396`).
    """

    def __init__(self) -> None:
        super().__init__()
        wheel_only_with_focus(self)


class FocusedDateEdit(QDateEdit):
    """A date field that a mouse wheel changes only once it has focus (`wheel_only_with_focus`).

    Without it, a wheel over the price form would step the date of a price,
    and the form would then keep that date as one the reader chose
    (`PL-8FSN`).
    """

    def __init__(self) -> None:
        super().__init__()
        wheel_only_with_focus(self)


class FittedScroll(QScrollArea):
    """Holds rows that a reader reads in order, and scrolls them where its space is too short.

    The box asks for the height that the rows need at the width the box has,
    and takes no more. Where its space is shorter than the rows, it is
    squeezed to `least_height_px`, and the reader scrolls the rows inside
    the box. A chart View's key, which holds the lines that qualify its plot
    and its legend, is one such box (`PL-CBYS`). Each run's list of control
    changes is another (`PL-HF1B`).

    The box takes the keyboard focus so that the keyboard can scroll it, so
    it carries a name for a screen reader to say when it has the focus
    (`PL-RK9Z`).

    Args:
        rows: The rows, in the order they are read.
        least_height_px: The height the box keeps however short its space is.
        name: What a screen reader calls the box, such as the heading shown
            above it.
    """

    def __init__(self, rows: Sequence[QWidget], least_height_px: int, name: str) -> None:
        super().__init__()
        self.setAccessibleName(name)
        self._body = QWidget()
        column = QVBoxLayout(self._body)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(VIEW_ROW_SPACING)

        for row in rows:
            column.addWidget(row)

        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMinimumHeight(least_height_px)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        # The box paints nothing of its own, so the panel it sits on shows
        # behind the rows. `setWidget` would otherwise fill the rows'
        # background from the palette.
        self.setStyleSheet(clear_scroll_area_stylesheet())
        self.viewport().setAutoFillBackground(False)
        self.setWidget(self._body)
        self._body.setAutoFillBackground(False)
        FocusRing(self)

    def minimumSizeHint(self) -> QSize:  # Qt spells this in camelCase.
        """The widest row's least width with the scroll bar beside it, and the box's least height.

        The box never scrolls sideways, so a box narrower than its widest row
        would cut that row off at the right. A `QScrollArea`'s own least width
        counts only its scroll bar, so the layout around the box would
        otherwise leave out every row in it (`PL-CBYS`).
        """

        least = super().minimumSizeHint()
        width = self._body.minimumSizeHint().width() + self.verticalScrollBar().sizeHint().width()

        return QSize(max(least.width(), width), least.height())

    def sizeHint(self) -> QSize:  # Qt spells this in camelCase.
        """The rows' width, and the height the rows need at the width the box has."""

        hint = self._body.sizeHint()
        height = self._body.heightForWidth(self.viewport().width())

        return QSize(hint.width(), hint.height() if height < 0 else height)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        # The height that the rows need depends on the box's width.
        self.updateGeometry()
