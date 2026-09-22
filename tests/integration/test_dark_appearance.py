"""What the interface draws when the host is set to a dark appearance.

Every colour this interface declares is a light-theme value, and Qt's palette
follows the host, so where the two disagree the interface wins only where
something declares the colour. `PL-DHBX` was three transport buttons taking
their labels from palette `ButtonText`; `PL-RKRY`, `PL-7W9N` and `PL-0NVN` are
the controls no stylesheet reaches at all - an entry's fill, a spin box's
stepper, a list's rows and its scrollbar, a check box's indicator, a selector's
popup. The project owner reported the first of those from his own screen on
2026-09-20: a white dialog carrying six near-black boxes.

**The host appearance is set on the `QApplication` here, deliberately, where
`tests/integration/test_qt_widgets.py` sets it on one widget.** That module
tests a control whose declaration is a *stylesheet*, which wins whatever the
palette says, so handing the widget a dark palette is a fair stand-in. It
cannot be the stand-in here, because the declaration under test *is* a
palette: setting one on the widget would overwrite the fix rather than
exercise it. A host appearance reaches a widget through the application
palette, so that is where it is set - and restored by the fixture, since every
test module in this tree shares one `QApplication`.

**Every test carries a vacuity guard**, in the shape `PL-DHBX`'s does: the
same kind of control, undeclared, is built under the same host and shown to
come out *differently*. Without it a platform plugin that ignored the palette
would leave every assertion here passing while measuring nothing. The chrome
tests take the one shape that has no undeclared counterpart to build - there
is only one application - so their guard is the same control measured *before*
the declaration and shown to come out differently after it.

**The chrome is asserted too, since `PL-KRZW`.** The project owner chose to
declare this interface's colours on the `QApplication` itself (2026-09-20,
ratified), so the page's scroll bars - which no stylesheet and no widget
palette reaches - resolve to the theme rather than to the host. Two things
still do not, both by the rule rather than by omission: a *disabled* widget
draws from the `Disabled` colour group this project leaves to the platform,
which is why the inert splitter handles stay the host's (`PL-05M4`), and a
tooltip draws from `ToolTipBase` and `ToolTipText`, which are outside the
declared role set and which this interface uses nowhere today.
"""

from collections.abc import Iterator

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPalette
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractSpinBox,
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QLabel,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
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
    inert_splitter,
)
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.theme import AGENT_COLOR_SCHEMES, INK, MUTED, PANEL, PRIMARY

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

#: The pages `_shown` builds, kept alive for the test that asked for one. A
#: page that falls out of scope is collected and takes its child widget with
#: it, and the child is what is under test - the failure arrives as
#: `Internal C++ object already deleted` from whichever line touches it next.
_PAGES: list[QWidget] = []


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


@pytest.fixture
def dark_host(application: QApplication) -> Iterator[QApplication]:
    """The application under a dark host appearance, restored afterwards.

    Restoring matters more than it looks: the modules in this tree share one
    `QApplication`, and this one sorts first, so a palette left behind would
    reach every test after it.
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
    """A widget laid out, shown and given the event loop, as `main.py` does.

    Laid out rather than merely shown, because that is what the defect turned
    on: a palette set on a combo box's popup reads back correctly until the
    selector is added to a layout, at which point the popup is reparented and
    re-resolves from the application's (`PL-0NVN`).
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
    """Every widget under `root` that paints from a palette and is not the theme's.

    A widget whose own stylesheet declares a `background-color` declares its
    own surface and is exempt: the agent selector is drawn in the running
    agent's ISO 5360 fill, which is not this interface's PANEL and which
    `tools/agent_identity_check.py` governs.
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


def _colours(widget: QWidget, application: QApplication) -> list[str]:
    """Every pixel of a rendered widget, as upper-case hex names."""

    application.processEvents()
    image: QImage = widget.grab().toImage()

    return [
        image.pixelColor(x, y).name().upper()
        for y in range(image.height())
        for x in range(image.width())
    ]


def _commonest(colours: list[str]) -> str:
    return max(set(colours), key=colours.count)


def _dark_share(widget: QWidget, application: QApplication) -> float:
    """The fraction of a rendered widget's pixels darker than mid-grey.

    The chrome is *shaded* from the palette rather than painted in it: Fusion
    derives a scroll bar's groove, handle and both its edges from `Button`, so
    no pixel of it is ever exactly PANEL and naming a colour to assert would
    be asserting one style's arithmetic. What separates a light host from a
    dark one survives that derivation, which is why it is what is measured
    here.

    Args:
        widget: The widget to render.
        application: The application, whose pending events are processed
            first so that a palette just assigned has reached the widget.

    Returns:
        A fraction in [0, 1]. HSL lightness is the measure, so the midpoint
        is 128 of 255.
    """

    application.processEvents()
    image: QImage = widget.grab().toImage()
    pixels = [image.pixelColor(x, y) for y in range(image.height()) for x in range(image.width())]

    return sum(pixel.lightness() < 128 for pixel in pixels) / len(pixels)


def _page_scroll_area() -> QScrollArea:
    """A scroll area built as `SimulationView` builds the page's, with a bar to draw.

    The content is made taller than any layout will give it so that the
    vertical bar is live: a scroll bar with nothing to scroll is hidden, and
    a hidden widget renders as nothing at all.
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
    """A declared widget takes no disabled colour off the platform style.

    This is the guarantee `tools/contrast_check.py` used to hold by refusing
    `setPalette` outright, moved to where it can be checked exactly rather
    than approximated. `.claude/rules/ui-color.md` keeps a disabled colour the
    platform's with one declared exception - the unavailable transport
    button's MUTED label, which is measured - and a palette assigned wholesale
    would quietly add a second for every role at once.

    So `declare_interface_colours` writes the `Active` and `Inactive` groups
    only, and this holds the `Disabled` group role by role against what the
    application supplies. It is checked on a widget that *is* disabled, since
    an enabled widget would resolve the same either way and the test would
    pass without the property holding.
    """

    entry = _shown(QLineEdit(), dark_host)
    entry.setEnabled(False)
    declare_interface_colours(entry)
    supplied = dark_host.palette()

    for role, _ in _DECLARED_ROLES:
        assert entry.palette().color(QPalette.ColorGroup.Disabled, role) == supplied.color(
            QPalette.ColorGroup.Disabled, role
        ), role


# ------------------------------------ the application, and the chrome it reaches


def test_the_chrome_draws_the_theme_rather_than_the_host_palette(dark_host: QApplication) -> None:
    """The page's scroll bars, which no stylesheet and no widget palette reaches.

    `PL-KRZW`'s regression test. A scroll bar inside a stylesheet ancestor
    resolves from the *application* palette however the ancestor was declared,
    so under a dark host the page's bars were dark rails down a light window -
    and no per-widget declaration could have reached them. The fix is the
    application palette, which is authoritative at any depth where
    `styleHints().setColorScheme` is a hint Qt documents as unsupported on
    some platforms and which was observed reporting `Unknown` after being set.

    The bar is built *before* the declaration deliberately: a widget already
    laid out is the case that would fail if the application palette did not
    propagate, and it is also the vacuity guard, since there is no second,
    undeclared application to build. That ordering is the reason for the
    `processEvents` below - Qt reaches an existing widget by posting
    `ApplicationPaletteChange` rather than by re-resolving in the call, so
    without it this reads the palette the bar still had. `main()` declares
    before the first widget exists and so never depends on it.

    The measure is the share of pixels darker than mid-grey rather than a
    named colour, for the reason `_dark_share` gives.
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
    """The application declaration takes no disabled colour off the platform style.

    The same guarantee
    `test_declaring_a_widget_leaves_its_disabled_colours_to_the_platform`
    holds for one widget, held for the palette every widget falls back to -
    where it binds harder, because a `Disabled` group written here would be a
    second authored disabled colour for every role in the interface at once,
    which `.claude/rules/ui-color.md` makes a decision rather than a style
    choice and `tools/contrast_check.py` refuses.

    Its visible consequence is asserted rather than left as a claim: a
    splitter handle is disabled by `freeze_splitter_handles`, so it draws from
    the group left to the platform and keeps the host's surface after the
    declaration. That is the rule working rather than the declaration
    failing - `PL-05M4` is where whether the handles should be declared too
    is decided.
    """

    handle = _shown(
        inert_splitter(Qt.Orientation.Horizontal, (QLabel("left"), QLabel("right"))), dark_host
    ).handle(1)
    supplied = QPalette(dark_host.palette())

    declare_application_colours(dark_host)

    for role, _ in _DECLARED_ROLES:
        assert dark_host.palette().color(QPalette.ColorGroup.Disabled, role) == supplied.color(
            QPalette.ColorGroup.Disabled, role
        ), role

    assert not handle.isEnabled()
    assert _commonest(_colours(handle, dark_host)) == _HOST_DARK[QPalette.ColorRole.Window].upper()


# ------------------------------------------------------- the bookmark editor


def test_the_bookmark_dialog_draws_the_theme_rather_than_the_host_palette(
    dark_host: QApplication,
) -> None:
    """The editor's entries, spin boxes and lists keep this interface's surface.

    `PL-RKRY`'s regression test, and the project owner's screenshot in
    assertions: eleven widgets in this dialog paint from a palette and declared
    nothing, so each arrived at the host's near-black `Base` inside a dialog
    whose own surface was declared PANEL.

    The placeholder is checked separately because it is the role a half-fix
    makes *worse*: declaring a light fill without declaring `PlaceholderText`
    leaves the host's light-grey hint on white, which takes "Optional" from
    poor to invisible.
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

    It held its surface before `PL-RKRY` too, as a one-rule stylesheet - and
    that rule is what severed palette inheritance to everything inside it, so
    a control added to this dialog later would have painted the host's
    colours however the dialog's own surface was set. Nothing inside it paints
    from a palette today, which is exactly why this test is about the
    mechanism rather than about a symptom.
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
    """The box saying whether a compartment is on the chart is legible either way.

    `PL-7W9N`'s regression test. `TraceLegend` declares the *label* - INK while
    the trace is drawn, MUTED while it is hidden - and declared nothing for the
    indicator, which is painted from `Base` with its tick in `Text`. Under a
    dark host that made the tick INK on near-black, 1.35:1, and an unchecked
    box a solid dark square: the shape a filled box has elsewhere, which is the
    opposite of what it means here.

    Both states, because `PL-DHBX` shipped a fix for one state and left the
    other broken, and the project owner found it on his own screen.

    The toggled state is set through the widget rather than at construction on
    purpose: `_on_toggled` rewrites the box's stylesheet, and a stylesheet
    write is one of the things that can reset a palette a widget was given.
    """

    legend = _shown(TraceLegend(), dark_host)
    box = legend.findChildren(QCheckBox)[0]
    box.setChecked(drawn)
    dark_host.processEvents()

    assert box.palette().color(QPalette.ColorRole.Base).name().upper() == PANEL.upper()
    assert PANEL.upper() in _colours(box, dark_host)

    # The vacuity guard: a box that declares nothing, in the same state.
    bare = _shown(QCheckBox("bare"), dark_host)
    bare.setChecked(drawn)

    assert bare.palette().color(QPalette.ColorRole.Base).name().upper() != PANEL.upper()
    assert PANEL.upper() not in _colours(bare, dark_host)


# ------------------------------------------------------------- the selectors


def test_a_selector_popup_draws_the_theme_rather_than_the_host_palette(
    dark_host: QApplication,
) -> None:
    """The lists an agent, a time base, a playback rate and a branch point come from.

    `PL-0NVN`'s regression test. A stylesheet on a combo box makes everything
    inside it resolve from the application palette, so every one of these
    popups drew the host's surface however its selector was styled. The count
    is asserted rather than the walk left open, so a selector added without a
    popup declaration fails here rather than reaching a reader - which is what
    the branch point's selector was checked by when `PL-VKJW` added it.

    The declaration is a rule inside each selector's own stylesheet rather
    than a palette on the view, and this test is laid out for the reason that
    matters: a palette set on `QComboBox.view()` at construction reads back
    correctly and is then lost when the selector is added to a layout. The
    guard below is an undeclared selector put through the same layout.
    """

    controller = SimulationController(agent_id=_AGENT_ID)
    view = SimulationView((controller,))
    view.resize(1600, 1000)
    view.show()
    dark_host.processEvents()
    view.present(False)
    dark_host.processEvents()

    popups = [box.view() for box in view.findChildren(QComboBox)]

    assert len(popups) == 4

    for popup in popups:
        palette = popup.palette()

        assert palette.color(QPalette.ColorRole.Base).name().upper() == PANEL.upper()
        assert palette.color(QPalette.ColorRole.Text).name().upper() == INK.upper()
        assert palette.color(QPalette.ColorRole.Highlight).name().upper() == PRIMARY.upper()

    # The vacuity guard: a selector carrying the same closed-surface rule
    # without the popup rule, laid out the same way.
    bare = QComboBox()
    bare.addItem("one")
    bare.setStyleSheet(f"QComboBox {{ background-color: {PANEL}; }}")
    _shown(bare, dark_host)

    assert bare.view().palette().color(QPalette.ColorRole.Base).name().upper() != PANEL.upper()

    view.close()


def test_the_agent_popup_keeps_its_iso_5360_row_colours(dark_host: QApplication) -> None:
    """Declaring the popup's surface does not take the agent colours off its rows.

    The agent selector's three rows carry their ISO 5360 fill and foreground as
    item data, and `PL-0NVN` gave the *view* a PANEL background. An item's own
    background is painted by the delegate from the model, over whatever the
    view's is, so the identification colours survive - and this holds it,
    because a popup rule that flattened them would be an agent-identity defect
    rather than a styling one (`app/theme.py`, ISO 5360 Table 2 footnote b).
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
    """The sweep, which is what catches the *next* control rather than these three.

    Each of the three items above fixed the instance in front of it, and the
    instance is not what keeps costing: this defect has now arrived four times
    in controls added months apart, because nothing failed when a new widget
    declared nothing. This walks the whole rendered tree - the dashboard and
    both dialogs - and fails on any widget that paints a surface from a
    palette role and does not resolve to this interface's.

    A control that declares its own `background-color` is exempt, which is how
    the agent selector's ISO 5360 fill passes. Chrome is out of scope here by
    construction - a scroll bar and a splitter handle are neither in
    `_PALETTE_PAINTED` nor content - and is held by
    `test_the_chrome_draws_the_theme_rather_than_the_host_palette` instead,
    against the application palette `PL-KRZW` added, which is the only thing
    that reaches it.
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
