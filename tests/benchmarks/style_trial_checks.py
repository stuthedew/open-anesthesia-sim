"""The parts of the style trial that a test can decide (`PL-BVC5`).

`style_trial.py` draws one push button as a style sheet and as a custom Qt
style. Its timings need judgment and are not asserted here. These tests cover
what does not: that the custom style takes nothing from the host appearance,
that each arm draws five states a reader can tell apart, that the two arms
draw the same button, and that the custom style draws a check box's tick
with no image file.

Run them with `uv run pytest tests/benchmarks/style_trial_checks.py --no-cov`.
The suite does not collect this file, because its name does not start with
`test_`. `tests/unit/test_bytecode_guard.py` relies on this directory holding
one collected module, and the trial is deleted once its decision is recorded.

`style_trial` imports as a bare module, as `test_frame_cost.py` explains for
`frame_cost`.
"""

from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
import style_trial
from PySide6.QtCore import QRect
from PySide6.QtGui import QColor, QImage, QPalette
from PySide6.QtWidgets import QApplication, QCheckBox, QPushButton, QStyle, QStyleOptionButton
from style_trial import (
    Arm,
    ButtonState,
    ComparisonWindow,
    TrialStyle,
    digest,
    dress,
    held_button,
    image_of,
    trial_button_stylesheet,
    trial_check_box_stylesheet,
)

from anesthesia_sim.app.qt_widgets import declare_application_colours
from anesthesia_sim.app.theme import PANEL

#: A dark host appearance: every role near-black or near-white, in every
#: colour group, as a platform set to Dark supplies them.
_DARK_SURFACE = "#1E1E1E"
_DARK_TEXT = "#F0F0F0"
_TEXT_ROLES = (
    QPalette.ColorRole.WindowText,
    QPalette.ColorRole.Text,
    QPalette.ColorRole.ButtonText,
    QPalette.ColorRole.BrightText,
    QPalette.ColorRole.HighlightedText,
    QPalette.ColorRole.PlaceholderText,
)


@pytest.fixture
def application() -> Iterator[QApplication]:
    """The shared application with the interface's colours declared, restored afterwards."""

    existing = QApplication.instance() or QApplication([])
    assert isinstance(existing, QApplication)
    supplied = QPalette(existing.palette())
    declare_application_colours(existing)

    yield existing

    existing.setPalette(supplied)


def _set_dark_host(application: QApplication) -> None:
    """Give the application a dark host's palette, then declare the interface's colours on it."""

    dark = QPalette()

    for group in (
        QPalette.ColorGroup.Active,
        QPalette.ColorGroup.Inactive,
        QPalette.ColorGroup.Disabled,
    ):
        for role in QPalette.ColorRole:
            if role is QPalette.ColorRole.NColorRoles:
                continue

            value = _DARK_TEXT if role in _TEXT_ROLES else _DARK_SURFACE
            dark.setColor(group, role, QColor(value))

    application.setPalette(dark)
    declare_application_colours(application)


def _states(arm: Arm, style: TrialStyle) -> dict[ButtonState, QImage]:
    """One arm's button rendered in each of the five states."""

    return {state: image_of(held_button(arm, state, style)) for state in ButtonState}


def _differing_pixels(first: QImage, second: QImage) -> int:
    """How many pixels differ between two images of one size."""

    assert first.size() == second.size()

    return sum(
        first.pixel(x, y) != second.pixel(x, y)
        for x in range(first.width())
        for y in range(first.height())
    )


def test_the_custom_style_draws_the_same_pixels_under_a_dark_host(
    application: QApplication,
) -> None:
    """The item's second test, against a simulated host: no state takes a colour from the host.

    The guard is a plain button, drawn by Fusion with no style sheet. When
    unavailable it takes its label from the `Disabled` group, which the
    project leaves to the host, so it must come out differently. Without that
    guard, a platform that ignored the palette would pass this test.
    """

    style = TrialStyle()
    plain = QPushButton("Start")
    plain.setEnabled(False)
    light = {state: digest(image) for state, image in _states(Arm.STYLE, style).items()}
    light_plain = digest(image_of(plain))

    _set_dark_host(application)

    plain_under_dark = QPushButton("Start")
    plain_under_dark.setEnabled(False)
    dark = {state: digest(image) for state, image in _states(Arm.STYLE, style).items()}

    assert digest(image_of(plain_under_dark)) != light_plain
    assert dark == light


@pytest.mark.parametrize("arm", list(Arm))
def test_each_arm_draws_five_states_that_differ(application: QApplication, arm: Arm) -> None:
    """A state that drew as another would make the comparison compare nothing."""

    style = TrialStyle()
    digests = {digest(image) for image in _states(arm, style).values()}

    assert len(digests) == len(ButtonState)


def test_the_two_arms_draw_the_same_button(application: QApplication) -> None:
    """Both arms draw one design: the same size, and the same pixels but for the edge's blending.

    The two arms round the corners with different code, so the pixels along
    the edge blend a little differently. The limit is a tenth of the button's
    pixels. A wrong colour, a wrong edge width or a moved label changes far
    more than that.
    """

    style = TrialStyle()
    sheet = _states(Arm.SHEET, style)
    custom = _states(Arm.STYLE, style)

    for state in ButtonState:
        assert custom[state].size() == sheet[state].size(), state
        pixels = sheet[state].width() * sheet[state].height()
        assert _differing_pixels(custom[state], sheet[state]) < pixels / 10, state


def _indicator_colours(box: QCheckBox) -> set[str]:
    """The colours inside a check box's indicator, as rendered."""

    box.ensurePolished()
    box.resize(box.sizeHint())
    option = QStyleOptionButton()
    box.initStyleOption(option)
    indicator: QRect = box.style().subElementRect(
        QStyle.SubElement.SE_CheckBoxIndicator, option, box
    )
    image = image_of(box)

    return {
        QColor(image.pixel(x, y)).name().upper()
        for x in range(indicator.left() + 3, indicator.right() - 2)
        for y in range(indicator.top() + 3, indicator.bottom() - 2)
    }


def test_the_custom_style_draws_a_tick_and_names_no_image(application: QApplication) -> None:
    """The item's third test, on the control it matters for.

    A style sheet that styles a check box's indicator can draw a tick only
    from an image file. The trial's sheets name no file, so the checked
    indicator is a filled square with no PANEL-coloured tick in it. The
    custom style paints the tick itself.
    """

    assert "url(" not in trial_button_stylesheet()
    assert "url(" not in trial_check_box_stylesheet()

    style = TrialStyle()
    boxes = {}

    for arm in Arm:
        box = QCheckBox("Halt at the mark")
        box.setChecked(True)
        dress(box, arm, style)
        boxes[arm] = _indicator_colours(box)

    assert PANEL.upper() not in boxes[Arm.SHEET]
    assert PANEL.upper() in boxes[Arm.STYLE]


def test_the_window_reports_the_same_pixels_across_a_change_of_host(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The line the owner reads on a real host is right on a simulated one.

    The offscreen platform reports no appearance, so the test names the two
    it records under. Between them the host palette turns dark.
    """

    monkeypatch.setattr(style_trial, "SCREENSHOT_DIRECTORY", tmp_path)
    window = ComparisonWindow(application)
    window.show()
    application.processEvents()

    monkeypatch.setattr(style_trial, "colour_scheme_name", lambda _application: "Light")
    window.record_appearance()
    _set_dark_host(application)
    application.processEvents()
    monkeypatch.setattr(style_trial, "colour_scheme_name", lambda _application: "Dark")
    window.record_appearance()

    verdict = window.verdict_text()

    assert "Custom style: THE SAME PIXELS under Dark and Light." in verdict
    assert "Style sheet: THE SAME PIXELS under Dark and Light." in verdict
    assert (tmp_path / "style-trial-Light.png").exists()
    assert (tmp_path / "style-trial-Dark.png").exists()
    assert (tmp_path / "style-trial-difference.png").exists()


def _record_twice(
    window: ComparisonWindow, monkeypatch: pytest.MonkeyPatch, between: Callable[[], None]
) -> str:
    """Record the window as Light, make a change, record it as Dark, and return its lines."""

    monkeypatch.setattr(style_trial, "colour_scheme_name", lambda _application: "Light")
    window.record_appearance()
    between()
    monkeypatch.setattr(style_trial, "colour_scheme_name", lambda _application: "Dark")
    window.record_appearance()

    return window.verdict_text()


def test_the_window_says_when_only_the_lettering_differs(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A change to the lettering alone is reported as that, for both arms.

    On macOS Qt draws lettering by the host appearance, so this is the case
    the owner's Mac is expected to show. Here the lettering is changed by
    hand between the two recordings.
    """

    monkeypatch.setattr(style_trial, "SCREENSHOT_DIRECTORY", tmp_path)
    window = ComparisonWindow(application)

    def reletter() -> None:
        for arm in Arm:
            for button in window.held_buttons(arm):
                button.setText("Stari")

    verdict = _record_twice(window, monkeypatch, reletter)

    for arm in Arm:
        (line,) = [line for line in verdict.splitlines() if line.startswith(arm.value)]
        assert "DIFFERENT PIXELS under Dark and Light" in line
        assert "5 of 5 buttons" in line
        assert line.endswith("so ONLY THE LETTERING differs.")


def test_the_window_says_when_the_fill_differs(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A fill that follows the host is reported as more than lettering.

    The custom style reads its fill from the palette, so a palette whose
    button colour changes between the recordings changes its buttons. The
    style sheet names its colours and is unchanged.
    """

    monkeypatch.setattr(style_trial, "SCREENSHOT_DIRECTORY", tmp_path)
    window = ComparisonWindow(application)

    def darken_the_button_role() -> None:
        palette = QPalette(application.palette())
        palette.setColor(
            QPalette.ColorGroup.Active, QPalette.ColorRole.Button, QColor(_DARK_SURFACE)
        )
        application.setPalette(palette)
        # Widgets take a changed application palette when its event is delivered.
        application.processEvents()

    verdict = _record_twice(window, monkeypatch, darken_the_button_role)

    assert "Style sheet: THE SAME PIXELS under Dark and Light." in verdict
    (line,) = [line for line in verdict.splitlines() if line.startswith(Arm.STYLE.value)]
    assert "pixels STILL DIFFER" in line
    assert line.endswith("so the edge or the fill differs.")
