"""Draw one push button as a style sheet and as a custom Qt style, and measure both (`PL-BVC5`).

The interface pass will give about six controls five states each. The
controls can be drawn by style sheets, as the interface draws them now, or by
a custom `QStyle`. This harness is the trial that decides between the two. It
draws one push button in its five states both ways, from the same design, and
measures what the choice costs.

To open the comparison on a desktop, run `uv run python
tests/benchmarks/style_trial.py`. The other commands are `dashboard`,
`frame-cost`, `compare-frame-cost` and `paint-cost`; `--help` lists them.

**The design is a placeholder.** The trial needs one design drawn twice, and
the interface pass has not chosen its colours or its states yet. At rest and
when unavailable, the button is the run controls' shipped button
(`stylesheets.transport_button_stylesheet`). The pointer, pressed and focus
states are this file's own, and nothing ships them.

**What each arm is.**

- The style sheet arm is `trial_button_stylesheet`, set on a `QPushButton`.
- The custom style arm is `TrialStyle`, a `QProxyStyle` over Qt's Fusion
  style. It draws the button's surface and edge with `QPainter`, and it takes
  every colour from a role of the palette that
  `qt_widgets.declare_application_colours` declares.

**The three tests the item sets, and where each is answered.**

1. No measurable slowdown in the frame-cost benchmark: `compare-frame-cost`
   runs `frame_cost.measure` in fresh processes, rotating through its arms.
2. The same look under the light and the dark host appearance:
   `style_trial_checks.py` checks it against a simulated dark host, and the
   comparison window's "Record this appearance" button checks it on a real
   one. Where the pixels differ, the window says whether the difference is
   in the lettering alone, because on macOS Qt draws lettering by the host
   appearance whatever draws the button (see `Recording`).
3. No image files: neither arm of the button needs one. The check box row
   shows the control that does. A style sheet that styles a check box's
   indicator draws no tick unless it names an image, and `TrialStyle` draws
   the tick with `QPainter`.

**Kept only until the decision is recorded.** If the custom style is chosen,
`TrialStyle` moves to `src/anesthesia_sim/app/` with the first control built
in it. If it is not, this file is deleted and the item records which test
failed.
"""

import argparse
import hashlib
import json
import os
import statistics
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from time import perf_counter
from typing import Final

from PySide6.QtCore import QPoint, QPointF, QRect, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPaintEvent, QPalette, QPen, QRegion
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProxyStyle,
    QPushButton,
    QStyle,
    QStyleHintReturn,
    QStyleOption,
    QStyleOptionButton,
    QStyleOptionComplex,
    QStylePainter,
    QVBoxLayout,
    QWidget,
)

from anesthesia_sim.app.theme import INK, MUTED, PANEL, PANEL_RADIUS, PRIMARY

# ----------------------------------------------------------- the one design

#: The width of the button's edge, and of the edge that marks keyboard focus.
EDGE_PX: Final = 1
FOCUS_EDGE_PX: Final = 2

#: The space between the edge and the label, as the shipped run controls have it.
PADDING_VERTICAL_PX: Final = 4
PADDING_HORIZONTAL_PX: Final = 12

#: How far the surface moves from PANEL toward PRIMARY under the pointer and
#: while pressed. Both are placeholders.
POINTER_TINT: Final = 0.08
PRESSED_TINT: Final = 0.20

#: The side of the check box indicator, in pixels.
INDICATOR_PX: Final = 16

#: Where the comparison window saves its pictures: the repository's `out/`,
#: which `.gitignore` covers.
SCREENSHOT_DIRECTORY: Final = Path(__file__).resolve().parents[2] / "out"


class ButtonState(Enum):
    """The five states the interface pass will draw each control in."""

    REST = "At rest"
    POINTER = "Under the pointer"
    PRESSED = "Pressed"
    FOCUS = "Keyboard focus"
    UNAVAILABLE = "Unavailable"


def tinted(surface: QColor, toward: QColor, share: float) -> QColor:
    """Mix `share` of `toward` into `surface`, channel by channel.

    Args:
        surface: The colour to start from.
        toward: The colour to move toward.
        share: The fraction of `toward` in the result, from 0 to 1.

    Returns:
        The mixed colour, opaque.
    """

    return QColor(
        round(surface.red() + (toward.red() - surface.red()) * share),
        round(surface.green() + (toward.green() - surface.green()) * share),
        round(surface.blue() + (toward.blue() - surface.blue()) * share),
    )


# ------------------------------------------------------ the style sheet arm


def trial_button_stylesheet() -> str:
    """Return the five-state button as a style sheet, composed from the theme's values.

    The focus rule widens the edge by one pixel and narrows the padding by
    one, so the label does not move when the button takes focus.
    """

    pointer = tinted(QColor(PANEL), QColor(PRIMARY), POINTER_TINT).name()
    pressed = tinted(QColor(PANEL), QColor(PRIMARY), PRESSED_TINT).name()
    widened = FOCUS_EDGE_PX - EDGE_PX

    return (
        f"QPushButton {{ color: {INK}; background-color: {PANEL}; "
        f"border: {EDGE_PX}px solid {MUTED}; border-radius: {PANEL_RADIUS}px; "
        f"padding: {PADDING_VERTICAL_PX}px {PADDING_HORIZONTAL_PX}px; }} "
        f"QPushButton:hover {{ background-color: {pointer}; border-color: {PRIMARY}; }} "
        f"QPushButton:pressed {{ background-color: {pressed}; border-color: {PRIMARY}; }} "
        f"QPushButton:focus {{ border: {FOCUS_EDGE_PX}px solid {PRIMARY}; "
        f"padding: {PADDING_VERTICAL_PX - widened}px {PADDING_HORIZONTAL_PX - widened}px; }} "
        f"QPushButton:disabled {{ color: {MUTED}; }}"
    )


def trial_check_box_stylesheet() -> str:
    """Return a check box whose indicator the style sheet draws, with no image named.

    A style sheet that styles `QCheckBox::indicator` takes over the whole
    indicator, tick included, and it can draw a tick only from an image file.
    This sheet names none, so the row shows what that costs.
    """

    return (
        f"QCheckBox {{ color: {INK}; }} "
        f"QCheckBox::indicator {{ width: {INDICATOR_PX - 2 * EDGE_PX}px; "
        f"height: {INDICATOR_PX - 2 * EDGE_PX}px; background-color: {PANEL}; "
        f"border: {EDGE_PX}px solid {MUTED}; border-radius: 3px; }} "
        f"QCheckBox::indicator:checked {{ background-color: {PRIMARY}; "
        f"border-color: {PRIMARY}; }}"
    )


# ------------------------------------------------------ the custom style arm


class TrialStyle(QProxyStyle):
    """Fusion, with the push button and the check box indicator drawn by this class.

    Every colour is read from the `Active` group of the option's palette. A
    disabled widget's palette resolves to its `Disabled` group, which this
    project leaves to the platform, so reading the current group would draw
    the host appearance's grey.
    """

    def __init__(self) -> None:
        """Build the style over Qt's Fusion style."""

        super().__init__("Fusion")

    # Qt spells its virtual functions in camelCase.
    def drawControl(
        self,
        element: QStyle.ControlElement,
        option: QStyleOption,
        painter: QPainter,
        widget: QWidget | None = None,
    ) -> None:
        """Draw a push button here, and hand every other element to Fusion."""

        if element == QStyle.ControlElement.CE_PushButton and isinstance(
            option, QStyleOptionButton
        ):
            self._draw_push_button(option, painter, widget)
            return

        super().drawControl(element, option, painter, widget)

    def drawPrimitive(
        self,
        element: QStyle.PrimitiveElement,
        option: QStyleOption,
        painter: QPainter,
        widget: QWidget | None = None,
    ) -> None:
        """Draw a check box's indicator here, and hand every other element to Fusion."""

        if element == QStyle.PrimitiveElement.PE_IndicatorCheckBox:
            self._draw_check_box_indicator(option, painter)
            return

        super().drawPrimitive(element, option, painter, widget)

    def sizeFromContents(
        self,
        contents_type: QStyle.ContentsType,
        option: QStyleOption,
        size: QSize,
        widget: QWidget | None = None,
    ) -> QSize:
        """Size a push button as its label plus the padding and the edge."""

        if contents_type == QStyle.ContentsType.CT_PushButton:
            return QSize(
                size.width() + 2 * (PADDING_HORIZONTAL_PX + EDGE_PX),
                size.height() + 2 * (PADDING_VERTICAL_PX + EDGE_PX),
            )

        return super().sizeFromContents(contents_type, option, size, widget)

    def _draw_push_button(
        self, option: QStyleOptionButton, painter: QPainter, widget: QWidget | None
    ) -> None:
        """Draw the surface and the edge, then have Fusion draw the label in the declared colour."""

        active = QPalette.ColorGroup.Active
        palette = option.palette
        panel = palette.color(active, QPalette.ColorRole.Button)
        primary = palette.color(active, QPalette.ColorRole.Highlight)
        muted = palette.color(active, QPalette.ColorRole.PlaceholderText)
        ink = palette.color(active, QPalette.ColorRole.ButtonText)
        state = option.state
        enabled = bool(state & QStyle.StateFlag.State_Enabled)
        pressed = enabled and bool(state & QStyle.StateFlag.State_Sunken)
        pointer = enabled and bool(state & QStyle.StateFlag.State_MouseOver)
        focused = enabled and bool(state & QStyle.StateFlag.State_HasFocus)

        surface = panel
        edge = muted

        if pointer:
            surface = tinted(panel, primary, POINTER_TINT)
            edge = primary

        if pressed:
            surface = tinted(panel, primary, PRESSED_TINT)
            edge = primary

        edge_px = EDGE_PX

        if focused:
            edge = primary
            edge_px = FOCUS_EDGE_PX

        inset = edge_px / 2
        outline = QRectF(option.rect).adjusted(inset, inset, -inset, -inset)
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(edge, edge_px))
        painter.setBrush(surface)
        painter.drawRoundedRect(outline, PANEL_RADIUS - inset, PANEL_RADIUS - inset)
        painter.restore()

        label = QStyleOptionButton(option)
        declared = QPalette(palette)
        declared.setColor(QPalette.ColorRole.ButtonText, ink if enabled else muted)
        label.palette = declared
        label.rect = option.rect.adjusted(
            PADDING_HORIZONTAL_PX + EDGE_PX,
            PADDING_VERTICAL_PX + EDGE_PX,
            -(PADDING_HORIZONTAL_PX + EDGE_PX),
            -(PADDING_VERTICAL_PX + EDGE_PX),
        )
        super().drawControl(QStyle.ControlElement.CE_PushButtonLabel, label, painter, widget)

    def _draw_check_box_indicator(self, option: QStyleOption, painter: QPainter) -> None:
        """Draw the box, and a tick inside it when the box is checked."""

        active = QPalette.ColorGroup.Active
        palette = option.palette
        panel = palette.color(active, QPalette.ColorRole.Button)
        primary = palette.color(active, QPalette.ColorRole.Highlight)
        muted = palette.color(active, QPalette.ColorRole.PlaceholderText)
        checked = bool(option.state & QStyle.StateFlag.State_On)
        box = QRectF(option.rect).adjusted(0.5, 0.5, -0.5, -0.5)
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(primary if checked else muted, EDGE_PX))
        painter.setBrush(primary if checked else panel)
        painter.drawRoundedRect(box, 3, 3)

        if checked:
            tick = QPen(panel, 2)
            tick.setCapStyle(Qt.PenCapStyle.RoundCap)
            tick.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(tick)
            left, top, side = box.left(), box.top(), box.width()
            painter.drawPolyline(
                [
                    QPointF(left + 0.22 * side, top + 0.52 * side),
                    QPointF(left + 0.43 * side, top + 0.73 * side),
                    QPointF(left + 0.78 * side, top + 0.30 * side),
                ]
            )

        painter.restore()


class EveryCallThroughPythonStyle(TrialStyle):
    """`TrialStyle`, with the rest of a style's frequently called functions passed through Python.

    `TrialStyle` reimplements three functions, so only calls to those three
    enter Python. A style that draws six controls will reimplement more:
    sliders and selectors are complex controls, and spacing comes from pixel
    metrics. This class reimplements those functions too and hands every call
    straight to Fusion. It draws nothing differently. It exists to measure
    what an application-wide style costs once those calls also enter Python.
    """

    def drawComplexControl(
        self,
        control: QStyle.ComplexControl,
        option: QStyleOptionComplex,
        painter: QPainter,
        widget: QWidget | None = None,
    ) -> None:
        """Hand the call to Fusion."""

        super().drawComplexControl(control, option, painter, widget)

    def subElementRect(
        self, element: QStyle.SubElement, option: QStyleOption, widget: QWidget | None = None
    ) -> QRect:
        """Hand the call to Fusion."""

        return super().subElementRect(element, option, widget)

    def subControlRect(
        self,
        control: QStyle.ComplexControl,
        option: QStyleOptionComplex,
        sub_control: QStyle.SubControl,
        widget: QWidget | None = None,
    ) -> QRect:
        """Hand the call to Fusion."""

        return super().subControlRect(control, option, sub_control, widget)

    def pixelMetric(
        self,
        metric: QStyle.PixelMetric,
        option: QStyleOption | None = None,
        widget: QWidget | None = None,
    ) -> int:
        """Hand the call to Fusion."""

        return super().pixelMetric(metric, option, widget)

    def styleHint(
        self,
        hint: QStyle.StyleHint,
        option: QStyleOption | None = None,
        widget: QWidget | None = None,
        return_data: QStyleHintReturn | None = None,
    ) -> int:
        """Hand the call to Fusion."""

        return super().styleHint(hint, option, widget, return_data)


# --------------------------------------------- one button held in one state


class HeldButton(QPushButton):
    """A push button painted in one named state, whatever the pointer and the keyboard do.

    It paints as `QPushButton` does, through its own style and its own style
    option. Only the option's state flags are replaced. So a held button under
    a style sheet takes the sheet's `:hover`, `:pressed` and `:focus` rules,
    and one under `TrialStyle` takes that style's branches.
    """

    def __init__(self, text: str, held: ButtonState) -> None:
        """Build the button.

        Args:
            text: The label.
            held: The state to paint. `UNAVAILABLE` also disables the button.
        """

        super().__init__(text)
        self._held = held
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setEnabled(held is not ButtonState.UNAVAILABLE)

    # Qt spells its event handlers in camelCase.
    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the button with the held state's flags in place of the live ones."""

        option = QStyleOptionButton()
        self.initStyleOption(option)
        live = (
            QStyle.StateFlag.State_MouseOver
            | QStyle.StateFlag.State_Sunken
            | QStyle.StateFlag.State_HasFocus
        )
        option.state &= ~live
        option.state |= QStyle.StateFlag.State_Raised

        if self._held is ButtonState.POINTER:
            option.state |= QStyle.StateFlag.State_MouseOver
        elif self._held is ButtonState.PRESSED:
            option.state |= QStyle.StateFlag.State_MouseOver | QStyle.StateFlag.State_Sunken
            option.state &= ~QStyle.StateFlag.State_Raised
        elif self._held is ButtonState.FOCUS:
            option.state |= QStyle.StateFlag.State_HasFocus

        QStylePainter(self).drawControl(QStyle.ControlElement.CE_PushButton, option)


class Arm(Enum):
    """The two ways the trial draws a control."""

    SHEET = "Style sheet"
    STYLE = "Custom style"


def dress(widget: QPushButton | QCheckBox, arm: Arm, style: TrialStyle) -> None:
    """Give one control its arm's drawing: the trial's style sheet, or the trial's style.

    Args:
        widget: The control.
        arm: Which way to draw it.
        style: The custom style, used by the `STYLE` arm. Setting a style on a
            widget does not transfer ownership, so the caller keeps it alive.
    """

    if arm is Arm.STYLE:
        widget.setStyle(style)
    elif isinstance(widget, QCheckBox):
        widget.setStyleSheet(trial_check_box_stylesheet())
    else:
        widget.setStyleSheet(trial_button_stylesheet())


def held_button(arm: Arm, held: ButtonState, style: TrialStyle, text: str = "Start") -> HeldButton:
    """Build one arm's button, held in one state."""

    button = HeldButton(text, held)
    dress(button, arm, style)

    return button


def image_of(widget: QWidget) -> QImage:
    """Render a widget over PANEL, at one device pixel per pixel, in a fixed format.

    The widget's own window background is not drawn. A control sits on a
    panel, and its rounded corners show that panel. Rendered alone, an
    unavailable control would fill its corners from the `Disabled` group's
    window colour, which is the host's, and the image would then show a
    colour that no reader of the interface sees.
    """

    widget.ensurePolished()
    widget.resize(widget.sizeHint())
    image = QImage(widget.size(), QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(QColor(PANEL))
    widget.render(image, QPoint(), QRegion(), QWidget.RenderFlag.DrawChildren)

    return image


def digest(image: QImage) -> str:
    """A short fingerprint of an image's pixels, to compare two renderings."""

    fixed = image.convertToFormat(QImage.Format.Format_ARGB32)

    return hashlib.sha256(bytes(fixed.constBits())).hexdigest()[:12]


@dataclass(frozen=True)
class PixelDifference:
    """How far two renderings of one control are apart.

    Attributes:
        pixels: The number of pixels whose colour differs.
        largest_step: The largest difference in any one colour channel of any
            pixel, on the 0 to 255 scale. A step of a few units is invisible,
            and a step near 255 is one colour replaced by another.
    """

    pixels: int
    largest_step: int


def difference_between(first: QImage, second: QImage) -> PixelDifference:
    """Compare two images pixel by pixel.

    Images of different sizes count as differing in every pixel of the larger
    one, by the full step. The window that calls this function runs on the
    owner's desktop, where a report is more use than an exception.
    """

    if first.size() != second.size():
        larger = max(first.width() * first.height(), second.width() * second.height())

        return PixelDifference(pixels=larger, largest_step=255)

    # Each converted image is held in a name until its bytes are copied. The
    # buffer that `constBits` returns does not keep its image alive, and a
    # copy made after the image is freed held 40 wrong bytes of 5,400 here.
    first_fixed = first.convertToFormat(QImage.Format.Format_ARGB32)
    second_fixed = second.convertToFormat(QImage.Format.Format_ARGB32)
    one = bytes(first_fixed.constBits())
    two = bytes(second_fixed.constBits())
    pixels = 0
    largest_step = 0

    for offset in range(0, len(one), 4):
        step = max(
            abs(left - right)
            for left, right in zip(one[offset : offset + 4], two[offset : offset + 4], strict=True)
        )

        if step:
            pixels += 1
            largest_step = max(largest_step, step)

    return PixelDifference(pixels=pixels, largest_step=largest_step)


def differing_pixel_mask(first: QImage, second: QImage) -> QImage:
    """An image of the first one's size: INK where the two differ, PANEL elsewhere."""

    mask = QImage(first.size(), QImage.Format.Format_ARGB32)
    mask.fill(QColor(PANEL))

    if first.size() != second.size():
        mask.fill(QColor(INK))

        return mask

    for x in range(first.width()):
        for y in range(first.height()):
            if first.pixel(x, y) != second.pixel(x, y):
                mask.setPixelColor(x, y, QColor(INK))

    return mask


@dataclass(frozen=True)
class Recording:
    """One arm's five held buttons, as drawn under one host appearance.

    The buttons are recorded twice because lettering and the button around it
    are drawn by different code. On macOS, Qt draws each letter with a black
    or a white fill according to the host appearance, and macOS thickens a
    letter's strokes by an amount that depends on that fill
    (`QCoreTextFontEngine::imageForGlyph`, `qfontengine_coretext.mm`, Qt
    6.11.0). So the same dark lettering on the same light surface can come out
    a little heavier or lighter under Dark than under Light, whichever arm
    drew the button. The recording without lettering shows whether anything
    else changed.

    Attributes:
        lettered: The five buttons as the window shows them.
        bare: The same five buttons, at the same size, with no lettering.
    """

    lettered: tuple[QImage, ...]
    bare: tuple[QImage, ...]


#: How many times larger than life the difference picture draws each button.
DIFFERENCE_PICTURE_SCALE: Final = 4


# ------------------------------------------------- the comparison window


def colour_scheme_name(application: QApplication) -> str:
    """The host appearance as Qt reports it: `Light`, `Dark` or `Unknown`."""

    return application.styleHints().colorScheme().name


class ComparisonWindow(QWidget):
    """Both arms side by side: five held states each, a live row, and the check box row."""

    def __init__(self, application: QApplication) -> None:
        """Build the window over an application whose palette is already declared."""

        super().__init__()
        self._application = application
        self._style = TrialStyle()
        self._recorded: dict[Arm, dict[str, Recording]] = {arm: {} for arm in Arm}
        self.setWindowTitle("PL-BVC5 trial: one button, drawn two ways")
        self.setAutoFillBackground(True)
        column = QVBoxLayout(self)
        column.setSpacing(16)
        column.setContentsMargins(24, 24, 24, 24)

        column.addWidget(self._caption("Each button below is held in the state its column names."))
        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(10)

        for index, state in enumerate(ButtonState, start=1):
            grid.addWidget(self._caption(state.value), 0, index)

        self._rows: dict[Arm, list[HeldButton]] = {arm: [] for arm in Arm}
        # The same buttons with no lettering. They are never shown, and
        # `record_appearance` renders them to tell lettering from the rest.
        self._bare_rows: dict[Arm, list[HeldButton]] = {arm: [] for arm in Arm}

        for row, arm in enumerate(Arm, start=1):
            grid.addWidget(self._caption(arm.value), row, 0)

            for index, state in enumerate(ButtonState, start=1):
                button = held_button(arm, state, self._style)
                self._rows[arm].append(button)
                grid.addWidget(button, row, index, Qt.AlignmentFlag.AlignLeft)
                bare = held_button(arm, state, self._style, text="")
                bare.setFixedSize(button.sizeHint())
                self._bare_rows[arm].append(bare)

        grid.setColumnStretch(len(ButtonState) + 1, 1)
        column.addLayout(grid)

        column.addWidget(
            self._caption(
                "These are live. Move the pointer over them, press them, and press Tab to move "
                "keyboard focus."
            )
        )
        live = QHBoxLayout()
        live.setSpacing(16)

        for arm in Arm:
            live.addWidget(self._caption(arm.value))

            for text in ("Start", "Pause"):
                button = QPushButton(text)
                dress(button, arm, self._style)
                live.addWidget(button)

            box = QCheckBox("Halt at the mark")
            box.setChecked(True)
            dress(box, arm, self._style)
            live.addWidget(box)

        live.addStretch(1)
        column.addLayout(live)

        record = QPushButton("Record this appearance")
        record.clicked.connect(self.record_appearance)
        self._verdict = self._caption("")
        self._verdict.setWordWrap(True)
        self._verdict.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        column.addWidget(record, 0, Qt.AlignmentFlag.AlignLeft)
        column.addWidget(self._verdict)
        record.setFocus()
        self._write_verdict()

    def _caption(self, text: str) -> QLabel:
        """A line of plain text in the declared ink."""

        label = QLabel(text)
        label.setStyleSheet(f"color: {INK};")

        return label

    def held_buttons(self, arm: Arm) -> tuple[HeldButton, ...]:
        """One arm's row of five held buttons, in the order of `ButtonState`."""

        return tuple(self._rows[arm])

    def record_appearance(self) -> None:
        """Record both rows under the host appearance in force, and say what has matched.

        It also saves a picture of the window, named for the appearance, in
        `SCREENSHOT_DIRECTORY`. Once two appearances are recorded it saves
        `style-trial-difference.png` there too: each row under each
        appearance, and the pixels that differ.
        """

        scheme = colour_scheme_name(self._application)

        for arm in Arm:
            self._recorded[arm][scheme] = Recording(
                lettered=tuple(image_of(button) for button in self._rows[arm]),
                bare=tuple(image_of(button) for button in self._bare_rows[arm]),
            )

        self._write_verdict()
        # The lines lengthen with each recording, so the window grows to show
        # them whole. On the owner's Mac the last line was cut off.
        self.adjustSize()
        print(self._verdict.text(), flush=True)
        SCREENSHOT_DIRECTORY.mkdir(parents=True, exist_ok=True)
        saved = SCREENSHOT_DIRECTORY / f"style-trial-{scheme}.png"

        if self.grab().save(str(saved)):
            print(f"Saved {saved}", flush=True)

        picture = self.difference_picture()
        difference = SCREENSHOT_DIRECTORY / "style-trial-difference.png"

        if picture is not None and picture.save(str(difference)):
            print(f"Saved {difference}", flush=True)

    def verdict_text(self) -> str:
        """The lines the window shows beside the record button."""

        return self._verdict.text()

    def _compared(self, arm: Arm) -> tuple[str, str] | None:
        """The two recorded appearances to compare for one arm, or None with fewer than two.

        They are the first by name, and the first after it whose lettered row
        differs from it. Where every recording matches, they are the first two.
        """

        recorded = self._recorded[arm]
        names = sorted(recorded)

        if len(names) < 2:
            return None

        first = names[0]

        for other in names[1:]:
            if _row_difference(recorded[first].lettered, recorded[other].lettered).pixels:
                return first, other

        return first, names[1]

    def _write_verdict(self) -> None:
        """Write, for each arm, the appearances recorded and whether their pixels are the same."""

        lines = [f"Host appearance now: {colour_scheme_name(self._application)}."]

        for arm in Arm:
            recorded = self._recorded[arm]
            pair = self._compared(arm)

            if not recorded:
                lines.append(f"{arm.value}: nothing recorded yet.")
            elif pair is None:
                (scheme,) = recorded
                lines.append(
                    f"{arm.value}: recorded under {scheme}. Switch the appearance and record again."
                )
            else:
                names = " and ".join(sorted(recorded))
                first, second = (recorded[name] for name in pair)
                lettered = _row_difference(first.lettered, second.lettered)
                bare = _row_difference(first.bare, second.bare)
                buttons = sum(
                    difference_between(one, two).pixels > 0
                    for one, two in zip(first.lettered, second.lettered, strict=True)
                )

                if not lettered.pixels:
                    lines.append(f"{arm.value}: THE SAME PIXELS under {names}.")
                    continue

                counted = (
                    f"{arm.value}: DIFFERENT PIXELS under {names}: {lettered.pixels} pixels in "
                    f"{buttons} of {len(first.lettered)} buttons, largest colour step "
                    f"{lettered.largest_step} of 255."
                )

                if bare.pixels:
                    lines.append(
                        f"{counted} Drawn without lettering, {bare.pixels} pixels STILL DIFFER "
                        f"(largest step {bare.largest_step}), so the edge or the fill differs."
                    )
                else:
                    lines.append(
                        f"{counted} Drawn without lettering the buttons are THE SAME, so ONLY "
                        "THE LETTERING differs."
                    )

        self._verdict.setText("\n".join(lines))

    def difference_picture(self) -> QImage | None:
        """Each arm's row under the two compared appearances, and the pixels that differ.

        Returns:
            The picture, drawn `DIFFERENCE_PICTURE_SCALE` times larger than
            life so that single pixels can be seen, or None until some arm has
            two appearances recorded.
        """

        strips: list[tuple[str, tuple[QImage, ...]]] = []

        for arm in Arm:
            pair = self._compared(arm)

            if pair is None:
                continue

            first, second = (self._recorded[arm][name] for name in pair)
            strips.append((f"{arm.value}, {pair[0]}", first.lettered))
            strips.append((f"{arm.value}, {pair[1]}", second.lettered))
            strips.append(
                (
                    f"{arm.value}, pixels that differ",
                    tuple(
                        differing_pixel_mask(one, two)
                        for one, two in zip(first.lettered, second.lettered, strict=True)
                    ),
                )
            )

        if not strips:
            return None

        scale = DIFFERENCE_PICTURE_SCALE
        gap = 12
        caption_width = 260
        cell_width = max(image.width() for _, images in strips for image in images) * scale
        cell_height = max(image.height() for _, images in strips for image in images) * scale
        columns = max(len(images) for _, images in strips)
        picture = QImage(
            caption_width + columns * (cell_width + gap) + gap,
            len(strips) * (cell_height + gap) + gap,
            QImage.Format.Format_ARGB32,
        )
        picture.fill(QColor(PANEL))
        painter = QPainter(picture)
        painter.setPen(QColor(INK))

        for row, (caption, images) in enumerate(strips):
            top = gap + row * (cell_height + gap)
            painter.drawText(
                QRect(gap, top, caption_width - gap, cell_height),
                int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
                caption,
            )

            for column, image in enumerate(images):
                enlarged = image.scaled(
                    image.width() * scale,
                    image.height() * scale,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.FastTransformation,
                )
                painter.drawImage(caption_width + column * (cell_width + gap), top, enlarged)

        painter.end()

        return picture


def _row_difference(first: Sequence[QImage], second: Sequence[QImage]) -> PixelDifference:
    """The difference between two renderings of one row of buttons, summed over the row."""

    each = [difference_between(one, two) for one, two in zip(first, second, strict=True)]

    return PixelDifference(
        pixels=sum(difference.pixels for difference in each),
        largest_step=max(difference.largest_step for difference in each),
    )


# ----------------------------------------------------------- measurements


class FrameArm(Enum):
    """The five dashboards whose frame cost the trial compares.

    Attributes:
        SHEETS: The dashboard as it ships: Fusion, and every control a style sheet.
        STYLE_INSTALLED: `TrialStyle` is the application's style, and every
            control keeps its style sheet. It isolates what routing every
            widget's drawing through a Python style costs.
        STYLE_DRAWN: As `STYLE_INSTALLED`, and the three run controls have no
            style sheet, so `TrialStyle` draws them.
        STYLE_ON_CONTROLS: The application keeps Fusion. `TrialStyle` is set
            on each run control alone, and draws it. No other widget's
            drawing passes through Python.
        EVERY_CALL: As `STYLE_DRAWN`, with `EveryCallThroughPythonStyle` as
            the application's style.
    """

    SHEETS = "sheets"
    STYLE_INSTALLED = "style-installed"
    STYLE_DRAWN = "style-drawn"
    STYLE_ON_CONTROLS = "style-on-controls"
    EVERY_CALL = "every-call"


def prepare_application(arm: FrameArm) -> tuple[QApplication, TrialStyle | None]:
    """Build the offscreen application for one frame-cost arm.

    Returns:
        The application, and the style it was given, which the caller keeps
        alive for as long as the application is used.
    """

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    existing = QApplication.instance()
    application = existing if isinstance(existing, QApplication) else QApplication(sys.argv[:1])

    if arm is FrameArm.SHEETS:
        return application, None

    style = EveryCallThroughPythonStyle() if arm is FrameArm.EVERY_CALL else TrialStyle()

    if arm is FrameArm.STYLE_ON_CONTROLS:
        clear_run_control_sheets(style)
        return application, style

    application.setStyle(style)

    if arm in (FrameArm.STYLE_DRAWN, FrameArm.EVERY_CALL):
        clear_run_control_sheets()

    return application, style


def clear_run_control_sheets(style: TrialStyle | None = None) -> None:
    """Make `RunView` build its three run controls with no style sheet.

    The trial does not edit `src/`. It replaces the one function `RunView`
    takes the run controls' style sheet from, for this process only.

    Args:
        style: When given, each push button `RunView` builds is also given
            this style as its own, so the style draws the run controls while
            the application keeps its style.
    """

    from anesthesia_sim.app import run_view

    run_view.transport_button_stylesheet = lambda: ""

    if style is None:
        return

    class OwnStyleButton(QPushButton):
        def __init__(self, text: str) -> None:
            super().__init__(text)
            self.setStyle(style)

    run_view.QPushButton = OwnStyleButton


def frame_cost(arm: FrameArm) -> dict[str, float]:
    """Run the frame-cost benchmark once under one arm, at its defaults.

    Returns:
        The median of each stage across the measured frames, in milliseconds.
    """

    from frame_cost import measure

    _application, _style = prepare_application(arm)
    measurement = measure()

    return {
        stage: measurement.median_s(stage) * 1000.0
        for stage in ("advance_s", "present_s", "paint_s", "settled_s", "interface_s", "total_s")
    }


def rotation_order(arms: Sequence[FrameArm], rotation: int) -> tuple[FrameArm, ...]:
    """The order the arms run in during one rotation, counted from zero.

    Rotation 0 runs the arms as given, and each later rotation starts one arm
    later and wraps around. Over a number of rotations that is a multiple of
    the number of arms, every arm runs equally often in every place.
    """

    start = rotation % len(arms)

    return (*arms[start:], *arms[:start])


@dataclass(frozen=True, slots=True)
class PairedDifference:
    """How one arm's timings differ from the first arm's, rotation by rotation.

    Attributes:
        mean_ms: The mean of the differences, in milliseconds per frame.
        standard_error_ms: The standard error of that mean.
    """

    mean_ms: float
    standard_error_ms: float


def paired_difference(arm: Sequence[float], baseline: Sequence[float]) -> PairedDifference:
    """Compare one arm with the baseline arm, pairing the two timings of each rotation."""

    differences = [value - base for value, base in zip(arm, baseline, strict=True)]
    spread = statistics.stdev(differences) if len(differences) > 1 else 0.0

    return PairedDifference(
        mean_ms=statistics.fmean(differences), standard_error_ms=spread / len(differences) ** 0.5
    )


def compare_frame_cost(
    invocations: int, arms: Sequence[FrameArm] = tuple(FrameArm)
) -> dict[str, dict[str, list[float]]]:
    """Run each arm `invocations` times, each in a fresh process, in rotation.

    The arms alternate so that drift in the machine's speed falls on all of
    them alike. Each rotation also starts one arm later than the one before
    (`rotation_order`), because an arm's place in a rotation changes its
    timing: with the shipped dashboard always first, the simulation stage,
    which a style cannot change, read 0.79 ms faster in the second arm.

    Returns:
        For each arm, each stage's median from every invocation, in order.
    """

    collected: dict[str, dict[str, list[float]]] = {arm.value: {} for arm in arms}

    for rotation in range(invocations):
        for arm in rotation_order(arms, rotation):
            finished = subprocess.run(
                [sys.executable, __file__, "frame-cost", "--arm", arm.value],
                check=True,
                capture_output=True,
                text=True,
            )
            medians = json.loads(finished.stdout.strip().splitlines()[-1])

            for stage, value in medians.items():
                collected[arm.value].setdefault(stage, []).append(value)

    return collected


@dataclass(frozen=True, slots=True)
class PaintCost:
    """What one repaint of one control costs under one arm.

    Attributes:
        arm: The arm measured.
        paints: How many repaints were timed.
        median_us: The median time of one repaint, in microseconds.
    """

    arm: Arm
    paints: int
    median_us: float


def paint_cost(paints: int) -> tuple[PaintCost, ...]:
    """Time `paints` repaints of one live button under each arm."""

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    application = QApplication.instance() or QApplication(sys.argv[:1])
    assert isinstance(application, QApplication)
    declare_colours(application)
    style = TrialStyle()
    results = []

    for arm in Arm:
        button = QPushButton("Start")
        dress(button, arm, style)
        button.ensurePolished()
        button.resize(button.sizeHint())
        image = QImage(button.size(), QImage.Format.Format_ARGB32_Premultiplied)
        timings = []

        for _ in range(paints):
            started = perf_counter()
            button.render(image)
            timings.append(perf_counter() - started)

        results.append(PaintCost(arm, paints, statistics.median(timings) * 1e6))

    return tuple(results)


def declare_colours(application: QApplication) -> None:
    """Declare the interface's palette on the application, as `main()` does."""

    from anesthesia_sim.app.qt_widgets import declare_application_colours

    declare_application_colours(application)


# ------------------------------------------------------------ the commands


def _show_comparison(save: Path | None) -> int:
    application = QApplication(sys.argv[:1])
    declare_colours(application)
    window = ComparisonWindow(application)
    window.show()

    if save is not None:
        application.processEvents()
        save.parent.mkdir(parents=True, exist_ok=True)
        print(window.grab().save(str(save)))
        return 0

    return application.exec()


def _show_dashboard(save: Path | None) -> int:
    """Open the dashboard with `TrialStyle` as the application's style.

    It saves nothing: the view is built with no Workspace or preference
    store, so the reader's own files are neither read nor written.
    """

    from anesthesia_sim.app.controller import BranchedCase, SimulationController
    from anesthesia_sim.app.simulation_view import SimulationView

    application = QApplication(sys.argv[:1])
    declare_colours(application)
    style = TrialStyle()
    application.setStyle(style)
    # Declared again in case a platform replaces the palette when the style
    # changes. Under the offscreen platform it did not (2026-11-11).
    declare_colours(application)
    clear_run_control_sheets()
    case = BranchedCase(SimulationController())
    view = SimulationView((case.trunk,), case=case)
    window = QMainWindow()
    window.setWindowTitle("PL-BVC5 trial: the dashboard under the custom style")
    window.setCentralWidget(view)
    window.resize(1600, 1000)
    window.show()
    view.present(False)

    if save is not None:
        application.processEvents()
        save.parent.mkdir(parents=True, exist_ok=True)
        print(window.grab().save(str(save)))
        return 0

    view.start_simulation_timer()

    return application.exec()


def _print_frame_comparison(invocations: int, arms: Sequence[FrameArm]) -> int:
    collected = compare_frame_cost(invocations, arms)
    stages = ("advance_s", "present_s", "paint_s", "interface_s", "total_s")
    print(f"Median of {invocations} invocations (lowest to highest), in ms per frame")
    print(f"{'arm':<18}" + "".join(f"{stage:>26}" for stage in stages))

    for arm, by_stage in collected.items():
        cells = []

        for stage in stages:
            values = by_stage[stage]
            cells.append(
                f"{statistics.median(values):7.2f} ({min(values):5.2f}-{max(values):5.2f})"
            )

        print(f"{arm:<18}" + "".join(f"{cell:>26}" for cell in cells))

    baseline, *others = collected
    print(f"Mean difference from {baseline}, paired by rotation (plus or minus 2 standard errors)")

    for arm in others:
        cells = []

        for stage in stages:
            paired = paired_difference(collected[arm][stage], collected[baseline][stage])
            cells.append(f"{paired.mean_ms:+6.2f} (+-{2 * paired.standard_error_ms:4.2f})")

        print(f"{arm:<18}" + "".join(f"{cell:>26}" for cell in cells))

    print(json.dumps(collected))

    return 0


def main(arguments: Sequence[str] | None = None) -> int:
    """Run one of the trial's commands. With no command, open the comparison window."""

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command")
    window = commands.add_parser("window", help="open the side-by-side comparison (the default)")
    window.add_argument("--save", type=Path, help="write the window to this PNG and exit")
    dashboard = commands.add_parser(
        "dashboard", help="open the dashboard with the custom style as the application's style"
    )
    dashboard.add_argument("--save", type=Path, help="write the window to this PNG and exit")
    frame = commands.add_parser("frame-cost", help="run the frame-cost benchmark under one arm")
    frame.add_argument("--arm", choices=[arm.value for arm in FrameArm], required=True)
    compare = commands.add_parser(
        "compare-frame-cost", help="run every frame-cost arm in fresh processes, in rotation"
    )
    compare.add_argument("--invocations", type=int, default=5)
    compare.add_argument(
        "--arms",
        nargs="+",
        choices=[arm.value for arm in FrameArm],
        default=[arm.value for arm in FrameArm],
    )
    paint = commands.add_parser("paint-cost", help="time one button's repaint under each arm")
    paint.add_argument("--paints", type=int, default=2000)
    chosen = parser.parse_args(arguments)
    handlers: dict[str | None, Callable[[], int]] = {
        None: lambda: _show_comparison(None),
        "window": lambda: _show_comparison(chosen.save),
        "dashboard": lambda: _show_dashboard(chosen.save),
        "frame-cost": lambda: _print(json.dumps(frame_cost(FrameArm(chosen.arm)))),
        "compare-frame-cost": lambda: _print_frame_comparison(
            chosen.invocations, [FrameArm(arm) for arm in chosen.arms]
        ),
        "paint-cost": lambda: _print(
            "\n".join(
                f"{cost.arm.value}: {cost.median_us:.1f} microseconds per repaint, "
                f"median of {cost.paints}"
                for cost in paint_cost(chosen.paints)
            )
        ),
    }

    return handlers[chosen.command]()


def _print(text: str) -> int:
    print(text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
