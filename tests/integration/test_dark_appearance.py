"""What the interface draws when the host is set to a dark appearance.

Every colour this interface declares is a light-theme value. Qt's palette
follows the host, so where the two disagree, the interface's colour is used
only where something declares it. `PL-DHBX` was three transport buttons that
took their labels from the palette's `ButtonText`. `PL-RKRY`, `PL-7W9N` and
`PL-0NVN` are the controls that no stylesheet applies to at all: an entry's
fill, a spin box's stepper, a list's rows and its scrollbar, a check box's
indicator, and a selector's popup. The project owner reported the first of
those from his own screen on 2026-09-20: a white dialog that held six
near-black boxes.

**This module sets the host appearance on the `QApplication`, deliberately,
while `tests/integration/test_qt_widgets.py` sets it on one widget.** That
module tests a control that declares its colours in a *stylesheet*. A
stylesheet wins whatever the palette says, so giving that widget a dark palette
is a fair stand-in for a dark host. It cannot be the stand-in here, because the
declaration under test *is* a palette: setting a palette on the widget would
overwrite the fix rather than exercise it. A host appearance reaches a widget
through the application palette, so this module sets it there. The fixture
restores it afterwards, because every test module in this tree shares one
`QApplication`.

**Every test carries a vacuity guard**, in the same shape as `PL-DHBX`'s test.
The guard builds the same kind of control, with no colours declared, under the
same host, and shows that it comes out *differently*. Without the guard, a
platform plugin that ignored the palette would leave every assertion here
passing while measuring nothing. The chrome tests have no undeclared
counterpart to build, because there is only one application. Their guard
instead measures the same control *before* the declaration and shows that it
comes out differently after it.

**The chrome is asserted too, since `PL-KRZW`.** The project owner chose to
declare this interface's colours on the `QApplication` itself (2026-09-20,
ratified). As a result, the page's scroll bars, which no stylesheet and no
widget palette applies to, resolve to the theme rather than to the host. Two
things still resolve to the host, both by rule rather than by omission. A
*disabled* widget that declares no colour of its own draws from the `Disabled`
colour group, which this project leaves to the platform. A tooltip draws from
`ToolTipBase` and `ToolTipText`, which are outside the declared role set and
which this interface does not use anywhere today.
"""

from collections.abc import Iterator

import pytest
from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QColor, QImage, QPalette
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractSpinBox,
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QLineEdit,
    QScrollArea,
    QSplitter,
    QStyle,
    QStyleOptionButton,
    QVBoxLayout,
    QWidget,
)

from anesthesia_sim.app.compartment_selection import (
    INITIAL_COMPARTMENT_SELECTION,
    CompartmentSelection,
)
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import new_case_question
from anesthesia_sim.app.qt_chart import TraceLegend
from anesthesia_sim.app.qt_widgets import (
    _DECLARED_ROLES,
    BookmarkDialog,
    NewCaseDialog,
    declare_application_colours,
    declare_interface_colours,
)
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.theme import AGENT_COLOR_SCHEMES, BACKGROUND, INK, MUTED, PANEL, PRIMARY

#: The palette Qt reports on a host set to a dark appearance: a dark window, a
#: near-black entry `Base` under a near-white `Text`, and a mid-grey
#: `PlaceholderText`. The values stand in for what macOS supplies in Dark
#: appearance, where every instance of this defect has been reported. The
#: bevel roles are given too, because a host supplies them and leaving them
#: light would make the test kinder than the host is.
_HOST_DARK: dict[QPalette.ColorRole, str] = {
    QPalette.ColorRole.Window: "#323232",
    QPalette.ColorRole.WindowText: "#FFFFFF",
    QPalette.ColorRole.Base: "#1E1E1E",
    QPalette.ColorRole.AlternateBase: "#2A2A2A",
    QPalette.ColorRole.Text: "#FFFFFF",
    QPalette.ColorRole.Button: "#323232",
    QPalette.ColorRole.ButtonText: "#FFFFFF",
    QPalette.ColorRole.PlaceholderText: "#6E6E6E",
    QPalette.ColorRole.Highlight: "#0058D0",
    QPalette.ColorRole.HighlightedText: "#FFFFFF",
    QPalette.ColorRole.Light: "#3C3C3C",
    QPalette.ColorRole.Midlight: "#2F2F2F",
    QPalette.ColorRole.Mid: "#282828",
    QPalette.ColorRole.Dark: "#1A1A1A",
    QPalette.ColorRole.Shadow: "#000000",
}

#: The widget kinds that paint a surface from a palette role rather than from
#: anything a stylesheet in this interface sets. Everything else on the
#: dashboard - a label, a panel, a transport button - declares its own colours.
_PALETTE_PAINTED = (QLineEdit, QAbstractSpinBox, QAbstractItemView, QCheckBox, QComboBox)

_AGENT_ID = "sevoflurane"

#: The pages that `_shown` builds, kept alive for the test that asked for each
#: one. A page that goes out of scope is garbage-collected and takes its child
#: widget with it. The child is the widget under test, so the failure appears
#: as `Internal C++ object already deleted` from whichever line touches it next.
_PAGES: list[QWidget] = []


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


@pytest.fixture
def dark_host(application: QApplication) -> Iterator[QApplication]:
    """Yield the application under a dark host appearance, then restore its palette.

    Restoring the palette matters more than it seems. The modules in this tree
    share one `QApplication`, and this module sorts first, so a palette left
    behind would apply to every test that runs after it.
    """

    original = QPalette(application.palette())
    dark = QPalette(original)

    for role, value in _HOST_DARK.items():
        dark.setColor(QPalette.ColorGroup.All, role, QColor(value))

    application.setPalette(dark)

    yield application

    application.setPalette(original)

    for page in _PAGES:
        page.close()

    _PAGES.clear()


def _shown(widget: QWidget, application: QApplication) -> QWidget:
    """Lay out and show a widget, then run the event loop, as `main.py` does.

    The widget is laid out rather than merely shown, because the defect
    depended on the layout. A palette set on a combo box's popup reads back
    correctly until the selector is added to a layout. At that point the popup
    is reparented and resolves its palette again from the application's
    (`PL-0NVN`).
    """

    page = QWidget()
    layout = QVBoxLayout(page)
    layout.addWidget(widget)
    page.resize(560, 320)
    page.show()
    application.processEvents()
    _PAGES.append(page)

    return widget


def _undeclared(root: QWidget) -> list[str]:
    """List each widget under `root` that paints from a palette that is not the theme's.

    A widget whose own stylesheet declares a `background-color` declares its
    own surface and is exempt. The agent selector is one: it is drawn in the
    running agent's ISO 5360 fill, which is not this interface's PANEL and
    which `tools/agent_identity_check.py` governs.
    """

    widgets: list[QWidget] = [root, *root.findChildren(QWidget)]

    for widget in list(widgets):
        if isinstance(widget, QComboBox):
            widgets.append(widget.view())

    reported = []

    for widget in widgets:
        if not isinstance(widget, _PALETTE_PAINTED):
            continue

        if "background-color" in widget.styleSheet():
            continue

        palette = widget.palette()
        base = palette.color(QPalette.ColorRole.Base).name().upper()
        text = palette.color(QPalette.ColorRole.Text).name().upper()

        if base != PANEL.upper() or text != INK.upper():
            reported.append(f"{type(widget).__name__} Base={base} Text={text}")

    return reported


def _colours(widget: QWidget, application: QApplication, area: QRect | None = None) -> list[str]:
    """Return each pixel of a rendered widget, or of `area` within it, as an upper-case hex name."""

    application.processEvents()
    image: QImage = (widget.grab() if area is None else widget.grab(area)).toImage()

    return [
        image.pixelColor(x, y).name().upper()
        for y in range(image.height())
        for x in range(image.width())
    ]


def _indicator(box: QCheckBox) -> QRect:
    """Return the area where `box`'s style draws its indicator, in the box's own coordinates."""

    option = QStyleOptionButton()
    box.initStyleOption(option)
    indicator = box.style().subElementRect(QStyle.SubElement.SE_CheckBoxIndicator, option, box)

    assert not indicator.isEmpty()

    return indicator


def _commonest(colours: list[str]) -> str:
    return max(set(colours), key=colours.count)


def _dark_share(widget: QWidget, application: QApplication) -> float:
    """Return the fraction of a rendered widget's pixels that are darker than mid-grey.

    The chrome is *shaded* from the palette rather than painted in it. Fusion
    derives a scroll bar's groove, its handle and both its edges from
    `Button`, so no pixel of the bar is ever exactly PANEL. Asserting a named
    colour would therefore assert one style's arithmetic. The difference
    between a light host and a dark one survives that derivation, so that
    difference is what this function measures.

    Args:
        widget: The widget to render.
        application: The application, whose pending events are processed
            first so that a palette just assigned has reached the widget.

    Returns:
        A fraction in [0, 1]. The measure is HSL lightness, so the midpoint
        is 128 of 255.
    """

    application.processEvents()
    image: QImage = widget.grab().toImage()
    pixels = [image.pixelColor(x, y) for y in range(image.height()) for x in range(image.width())]

    return sum(pixel.lightness() < 128 for pixel in pixels) / len(pixels)


def _page_scroll_area() -> QScrollArea:
    """Build a scroll area the way `SimulationView` builds the page's, with a bar to draw.

    The content is made taller than any layout will allow, so that the
    vertical scroll bar is live. A scroll bar with nothing to scroll is
    hidden, and a hidden widget renders as nothing at all.
    """

    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setFrameShape(QFrame.Shape.NoFrame)
    inner = QWidget()
    inner.setMinimumHeight(4000)
    area.setWidget(inner)

    return area


def test_declaring_a_widget_leaves_its_disabled_colours_to_the_platform(
    dark_host: QApplication,
) -> None:
    """Declaring a widget's colours leaves its disabled colours to the platform style.

    `tools/contrast_check.py` used to enforce this guarantee by refusing
    `setPalette` outright. The guarantee has moved here, where it can be
    checked exactly rather than approximated. `.claude/rules/ui-color.md`
    keeps every disabled colour the platform's, with one declared exception:
    the unavailable transport button's MUTED label, which is measured. A
    palette assigned wholesale would quietly add a second exception for every
    role at once.

    So `declare_interface_colours` writes only the `Active` and `Inactive`
    groups, and this test checks the `Disabled` group, role by role, against
    what the application supplies. It checks a widget that *is* disabled,
    because an enabled widget would resolve the same either way, and the test
    would then pass even if the property did not hold.
    """

    entry = _shown(QLineEdit(), dark_host)
    entry.setEnabled(False)
    declare_interface_colours(entry)
    supplied = dark_host.palette()

    for role, _ in _DECLARED_ROLES:
        assert entry.palette().color(QPalette.ColorGroup.Disabled, role) == supplied.color(
            QPalette.ColorGroup.Disabled, role
        ), role


# --------------------------- the application palette, and the chrome it applies to


def test_the_chrome_draws_the_theme_rather_than_the_host_palette(dark_host: QApplication) -> None:
    """The page's scroll bars, which no stylesheet or widget palette applies to, draw the theme.

    This is `PL-KRZW`'s regression test. A scroll bar inside an ancestor that
    has a stylesheet resolves its colours from the *application* palette,
    however the ancestor was declared. Under a dark host, the page's bars were
    therefore dark rails down a light window, and no per-widget declaration
    could have changed them. The fix is the application palette, which is
    authoritative at any depth. The alternative, `styleHints().setColorScheme`, is
    only a hint: Qt documents it as unsupported on some platforms, and it was
    observed reporting `Unknown` after being set.

    The test builds the bar *before* the declaration, deliberately. A widget
    already laid out is the case that would fail if the application palette
    did not propagate. The same ordering is also the vacuity guard, since
    there is no second, undeclared application to build. That ordering is why
    the test calls `processEvents` below. Qt updates an existing widget by
    posting `ApplicationPaletteChange`, not by resolving its palette again
    inside the call, so without that call the test would read the palette the
    bar still had. `main()` declares the colours before the first widget
    exists, so it never depends on the posted event.

    The measure is the share of pixels darker than mid-grey rather than a
    named colour, for the reason that `_dark_share` gives.
    """

    bar = _shown(_page_scroll_area(), dark_host).verticalScrollBar()

    assert bar.palette().color(QPalette.ColorRole.Button).name().upper() != PANEL.upper()
    assert _dark_share(bar, dark_host) > 0.5

    declare_application_colours(dark_host)
    dark_host.processEvents()

    assert bar.palette().color(QPalette.ColorRole.Button).name().upper() == PANEL.upper()
    assert _dark_share(bar, dark_host) == 0.0


def test_declaring_the_application_leaves_its_disabled_colours_to_the_platform(
    dark_host: QApplication,
) -> None:
    """Declaring the application's colours leaves its disabled colours to the platform style.

    `test_declaring_a_widget_leaves_its_disabled_colours_to_the_platform`
    checks this guarantee for one widget. This test checks it for the palette
    that every widget falls back to, where it matters more. A `Disabled` group
    written into the application palette would be a second authored disabled
    colour for every role in the interface at once. `.claude/rules/ui-color.md` makes that a
    decision rather than a style choice, and `tools/contrast_check.py`
    refuses it.

    The test asserts the visible consequence rather than leaving it as a
    claim. A disabled surface that declares no colour of its own draws from
    the group left to the platform, so it keeps the host's surface after the
    declaration. That result is the rule working, not the declaration
    failing. Until `PL-W9P6`, the splitter handles were such a surface. They
    are live now, and the test below checks what they draw (`PL-05M4`).
    """

    surface = QWidget()
    surface.setAutoFillBackground(True)
    surface.setMinimumSize(40, 40)
    surface.setEnabled(False)
    _shown(surface, dark_host)
    supplied = QPalette(dark_host.palette())

    declare_application_colours(dark_host)

    for role, _ in _DECLARED_ROLES:
        assert dark_host.palette().color(QPalette.ColorGroup.Disabled, role) == supplied.color(
            QPalette.ColorGroup.Disabled, role
        ), role

    assert not surface.isEnabled()
    assert _commonest(_colours(surface, dark_host)) == _HOST_DARK[QPalette.ColorRole.Window].upper()


def test_the_border_between_two_areas_shows_the_page_rather_than_the_host(
    dark_host: QApplication,
) -> None:
    """`PL-05M4`: under a dark host, the gap between the chart panel and the sidebar stays light.

    The inert handle was disabled, so it drew the host's dark surface between
    two light panels. The live handle is enabled and draws nothing at rest
    (`PL-RQT1` Q1), so the page's BACKGROUND shows through it, as it does on
    a light host.
    """

    declare_application_colours(dark_host)
    view = SimulationView((SimulationController(agent_id=_AGENT_ID),))
    view.resize(1600, 1000)
    view.show()
    dark_host.processEvents()
    splitter = view.layout_container.findChild(QSplitter)
    assert splitter is not None, "the dashboard's Areas are not in a splitter"
    handle = splitter.handle(1)
    gap = QRect(handle.mapTo(view, QPoint(0, 0)), handle.size())

    assert handle.isEnabled()
    assert _commonest(_colours(view, dark_host, gap)) == BACKGROUND.upper()

    view.close()


# ------------------------------------------------------- the bookmark editor


def test_the_bookmark_dialog_draws_the_theme_rather_than_the_host_palette(
    dark_host: QApplication,
) -> None:
    """The editor's entries, spin boxes and lists keep this interface's surface.

    This is `PL-RKRY`'s regression test, and it turns the project owner's
    screenshot into assertions. Eleven widgets in this dialog paint from a
    palette and declared nothing, so each one showed the host's near-black
    `Base` inside a dialog whose own surface was declared PANEL.

    The placeholder is checked separately because it is the role that a
    half-fix makes *worse*. Declaring a light fill without declaring
    `PlaceholderText` leaves the host's light-grey hint on white, which takes
    "Optional" from poorly legible to invisible.
    """

    dialog = BookmarkDialog()
    dialog.show()
    dark_host.processEvents()

    assert _undeclared(dialog) == []

    placeholder = dialog.time_label_edit.palette().color(QPalette.ColorRole.PlaceholderText)

    assert placeholder.name().upper() == MUTED.upper()
    assert _commonest(_colours(dialog, dark_host)) == PANEL.upper()

    # The vacuity guard: an entry that declares nothing, under the same host.
    bare = _shown(QLineEdit(), dark_host)

    assert _commonest(_colours(bare, dark_host)) != PANEL.upper()

    dialog.close()


def test_the_new_case_dialog_declares_its_surface_as_a_palette(dark_host: QApplication) -> None:
    """The discard confirmation keeps PANEL under a dark host, as a palette.

    The dialog kept its surface before `PL-RKRY` too, through a one-rule
    stylesheet. That rule is what cut off palette inheritance for everything
    inside the dialog. A control added to the dialog later would therefore
    have painted the host's colours, however the dialog's own surface was set.
    Nothing inside the dialog paints from a palette today, which is exactly
    why this test checks the mechanism rather than a symptom.
    """

    controller = SimulationController(agent_id=_AGENT_ID)
    dialog = NewCaseDialog(new_case_question(controller.snapshot(), "Isoflurane", 0))
    dialog.show()

    assert _commonest(_colours(dialog, dark_host)) == PANEL.upper()
    assert dialog.palette().color(QPalette.ColorRole.Window).name().upper() == PANEL.upper()
    assert "background-color" not in dialog.styleSheet()

    dialog.close()


# --------------------------------------------------------- the chart legend


@pytest.mark.parametrize("drawn", [True, False], ids=["drawn", "hidden"])
def test_a_legend_checkbox_draws_its_indicator_in_the_theme(
    dark_host: QApplication, drawn: bool
) -> None:
    """The box that says whether a compartment is on the chart is legible in either state.

    This is `PL-7W9N`'s regression test. `TraceLegend` declares the *label*:
    INK while the trace is drawn, and MUTED while it is hidden. It declared
    nothing for the indicator, which is painted from `Base`, with its tick in
    `Text`. Under a dark host, that made the tick INK on near-black, a
    contrast of 1.35:1. It also made an unchecked box a solid dark square.
    That is the shape a filled box has elsewhere, which is the opposite of
    what it means here.

    The test covers both states, because `PL-DHBX` shipped a fix for one state
    and left the other broken, and the project owner found the broken state on
    his own screen.

    The test reaches the hidden state through the widget rather than at
    construction, on purpose. `_on_toggled` rewrites the box's stylesheet when
    the box is unchecked, and a stylesheet write is one of the things that can
    reset a palette the widget was given. The hidden state arrives as a
    selection handed to the legend, which is how its boxes change
    (`PL-VN6M`). A box set directly, with nothing to handle the request, goes
    back to the state it was shown in, and the hidden case would then quietly
    test the drawn one.
    """

    legend = _shown(TraceLegend(), dark_host)
    box = legend.findChildren(QCheckBox)[0]
    legend.show_selection(INITIAL_COMPARTMENT_SELECTION if drawn else CompartmentSelection((), 1))
    dark_host.processEvents()

    assert box.isChecked() is drawn

    # Check the indicator's pixels alone. A bare box draws its label in the
    # host's `WindowText`, which is the same white as PANEL. Wherever a glyph
    # covers a whole pixel, the label supplies the colour that this assertion
    # looks for: 29 pixels of `bare` under Inter, 1 under DejaVu Sans, and none
    # of them inside the indicator (`PL-K9Z5`).
    assert box.palette().color(QPalette.ColorRole.Base).name().upper() == PANEL.upper()
    assert PANEL.upper() in _colours(box, dark_host, _indicator(box))

    # The vacuity guard: a box that declares nothing, in the same state.
    bare = _shown(QCheckBox("bare"), dark_host)
    bare.setChecked(drawn)

    assert bare.palette().color(QPalette.ColorRole.Base).name().upper() != PANEL.upper()
    assert PANEL.upper() not in _colours(bare, dark_host, _indicator(bare))


# ------------------------------------------------------------- the selectors


def test_a_selector_popup_draws_the_theme_rather_than_the_host_palette(
    dark_host: QApplication,
) -> None:
    """The popups for choosing an agent, time base, playback rate and branch point draw the theme.

    This is `PL-0NVN`'s regression test. A stylesheet on a combo box makes
    everything inside it resolve from the application palette, so every one
    of these popups drew the host's surface, however its selector was styled.
    The test asserts the number of popups rather than leaving the walk
    open-ended. A selector added without a popup declaration therefore fails
    here before it reaches a reader. That assertion is what checked the
    branch point's selector when `PL-VKJW` added it.

    The declaration is a rule inside each selector's own stylesheet rather
    than a palette on the view. This test lays the selectors out, because the
    layout is what loses a palette: a palette set on `QComboBox.view()` at
    construction reads back correctly and is then lost when the selector is
    added to a layout. The guard below puts an undeclared selector through the
    same layout.
    """

    controller = SimulationController(agent_id=_AGENT_ID)
    view = SimulationView((controller,))
    view.resize(1600, 1000)
    view.show()
    dark_host.processEvents()
    view.present(False)
    dark_host.processEvents()

    popups = [box.view() for box in view.findChildren(QComboBox)]

    # The shipped Default Workspace draws one chart, so it contains one
    # time-base selector (`PL-L59K`).
    assert len(popups) == 4

    for popup in popups:
        palette = popup.palette()

        assert palette.color(QPalette.ColorRole.Base).name().upper() == PANEL.upper()
        assert palette.color(QPalette.ColorRole.Text).name().upper() == INK.upper()
        assert palette.color(QPalette.ColorRole.Highlight).name().upper() == PRIMARY.upper()

    # The vacuity guard: a selector that carries the same rule for its closed
    # surface but no popup rule, laid out the same way.
    bare = QComboBox()
    bare.addItem("one")
    bare.setStyleSheet(f"QComboBox {{ background-color: {PANEL}; }}")
    _shown(bare, dark_host)

    assert bare.view().palette().color(QPalette.ColorRole.Base).name().upper() != PANEL.upper()

    view.close()


def test_the_agent_popup_keeps_its_iso_5360_row_colours(dark_host: QApplication) -> None:
    """Declaring the popup's surface does not take the agent colours off its rows.

    The agent selector's three rows carry their ISO 5360 fill and foreground as
    item data, and `PL-0NVN` gave the *view* a PANEL background. The delegate
    paints an item's own background from the model, over whatever background
    the view has, so the identification colours survive. This test checks
    that, because a popup rule that flattened them would be an agent-identity
    defect rather than a styling one (`app/theme.py`, ISO 5360 Table 2
    footnote b).
    """

    controller = SimulationController(agent_id=_AGENT_ID)
    view = SimulationView((controller,))
    view.show()
    dark_host.processEvents()
    view.present(False)

    agent_selector = next(
        box
        for box in view.findChildren(QComboBox)
        if any(
            box.itemData(index, Qt.ItemDataRole.BackgroundRole) is not None
            for index in range(box.count())
        )
    )
    declared = {scheme.fill.upper() for scheme in AGENT_COLOR_SCHEMES.values()}
    painted = {
        agent_selector.itemData(index, Qt.ItemDataRole.BackgroundRole).name().upper()
        for index in range(agent_selector.count())
    }

    assert painted == declared

    view.close()


# ------------------------------------------------- nothing left undeclared


def test_no_content_widget_in_the_interface_paints_from_the_host_palette(
    dark_host: QApplication,
) -> None:
    """Sweep the whole interface, to catch the *next* undeclared control, not only these three.

    Each of the three items above fixed the instance in front of it, but the
    single instance is not what keeps costing. This defect has now arrived
    four times, in controls added months apart, because nothing failed when a
    new widget declared nothing. This test walks the whole rendered tree: the
    dashboard and both dialogs. It fails on any widget that paints a surface
    from a palette role and does not resolve to this interface's colours.

    A control that declares its own `background-color` is exempt, which is how
    the agent selector's ISO 5360 fill passes. Chrome is out of scope here by
    construction, because a scroll bar and a splitter handle are neither in
    `_PALETTE_PAINTED` nor content.
    `test_the_chrome_draws_the_theme_rather_than_the_host_palette` checks the
    chrome instead, against the application palette that `PL-KRZW` added,
    which is the only thing that applies to it.
    """

    controller = SimulationController(agent_id=_AGENT_ID)
    view = SimulationView((controller,))
    view.resize(1600, 1000)
    view.show()
    dark_host.processEvents()
    view.present(False)
    dark_host.processEvents()

    editor = BookmarkDialog(view)
    editor.show()
    confirmation = NewCaseDialog(new_case_question(controller.snapshot(), "Isoflurane", 0), view)
    confirmation.show()
    dark_host.processEvents()

    for surface in (view, editor, confirmation):
        assert _undeclared(surface) == [], f"{type(surface).__name__} left a surface undeclared"

    confirmation.close()
    editor.close()
    view.close()
