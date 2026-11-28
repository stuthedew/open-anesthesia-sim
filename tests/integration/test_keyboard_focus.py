"""Headless tests that every control a reader can Tab to shows that it has the focus.

WCAG 2.2 Success Criterion 2.4.7, Focus Visible (Level AA), asks that "the
keyboard focus indicator is visible". Under Qt's Fusion style a slider, a combo
box drawn by a style sheet, a scroll area and a list drew no mark (`PL-63FQ`),
and Start, Pause and Reset looked the same pressed as at rest (`PL-CXYV`).

Qt's Fusion style draws a focus mark only when the window's last focus change
came from the keyboard, which Qt records as `WA_KeyboardFocusChange`.
`FocusRing` follows the same rule. A real Tab press sets it. A call to
`setFocus` with `TabFocusReason` outside a Tab key event clears it, so these
tests move the focus with `ShortcutFocusReason`, which keeps it set, as the
keyboard shortcut that it stands for would.
"""

import importlib
from collections import Counter
from collections.abc import Iterator
from typing import Final

import pytest
from pyqtgraph import PlotWidget
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QAccessible, QAccessibleInterface, QColor, QImage
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QGraphicsView,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QScrollArea,
    QSlider,
    QWidget,
)

from anesthesia_sim.app import qt_widgets
from anesthesia_sim.app.agent_cost import UNIT_CHOICE_LABEL
from anesthesia_sim.app.area_layout import SPLIT_SIDE_BY_SIDE_LABEL
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import AGENT_SELECTOR_LABEL, control_name, new_case_question
from anesthesia_sim.app.pinned_heading import HeadingScroll
from anesthesia_sim.app.qt_agent_price import (
    AGENT_FIELD_LABEL,
    APPLIES_ON_FIELD_LABEL,
    BOTTLE_PRICE_FIELD_LABEL,
    BOTTLE_VOLUME_FIELD_LABEL,
    CURRENCY_FIELD_LABEL,
    PRICE_FORM_KIND,
    SET_PRICE_LABEL,
    PriceEntry,
)
from anesthesia_sim.app.qt_widgets import (
    DescribedGraphic,
    FocusRing,
    NewCaseDialog,
    SelectorComboBox,
    label_control,
    name_control,
)
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.theme import (
    AGENT_COLOR_SCHEMES,
    CONTROL_BORDER_WIDTH,
    FOCUS_RING_WIDTH,
    INK,
    PANEL,
    PANEL_RADIUS,
)
from anesthesia_sim.app.view_contract import AreaName
from anesthesia_sim.app.view_registry import (
    AGENT_COST,
    COMPARTMENT_SCHEMATIC,
    CONCENTRATION_CHART,
    REGISTERED,
    WASH_IN,
)
from anesthesia_sim.layout.model import MAIN_WINDOW
from anesthesia_sim.layout.shipped import SHIPPED_WORKSPACE_IDS, shipped_workspaces
from anesthesia_sim.layout.tree import ViewKind, areas_in
from anesthesia_sim.layout.workspace import ShippedWorkspaceId
from tests.integration.simulation_view.simulation_view_support import (
    EVERY_REGISTERED_VIEW_SIZE_PX,
    _branched_case,
    _settle,
    _take_fork,
    built_view_kinds,
    every_registered_view,
)

_AGENT_ID = "sevoflurane"


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


@pytest.fixture
def dashboard(application: QApplication) -> Iterator[SimulationView]:
    """The dashboard as `main` builds it, drawing every registered kind of View."""

    case = BranchedCase(SimulationController(agent_id=_AGENT_ID))
    view = SimulationView((case.trunk,), case=case, workspaces=every_registered_view())
    view.resize(*EVERY_REGISTERED_VIEW_SIZE_PX)
    view.show()
    view.activateWindow()
    application.processEvents()
    view.present(False)
    application.processEvents()

    yield view

    view.close()


def _tab_stops(window: QWidget) -> list[QWidget]:
    """Return every widget in `window` that Tab can reach now: shown, enabled, taking Tab focus."""

    return [
        widget
        for widget in window.findChildren(QWidget)
        if widget.window() is window
        and widget.isVisible()
        and widget.isEnabled()
        and widget.focusPolicy() & Qt.FocusPolicy.TabFocus
    ]


def _related(first: QWidget, second: QWidget) -> bool:
    return first is second or first.isAncestorOf(second) or second.isAncestorOf(first)


def _focus(widget: QWidget, application: QApplication) -> None:
    widget.setFocus(Qt.FocusReason.ShortcutFocusReason)
    application.processEvents()


def _unmarked(window: QWidget, application: QApplication) -> list[str]:
    """Return each Tab stop in `window` that looks the same with the focus as without it.

    Each stop is grabbed while another stop holds the focus, then again while
    it holds the focus itself. The other stop is neither inside it nor round
    it, so only the focus differs between the two images.
    """

    window.activateWindow()
    QTest.keyClick(window, Qt.Key.Key_Tab)
    application.processEvents()
    assert window.testAttribute(Qt.WidgetAttribute.WA_KeyboardFocusChange)
    stops = _tab_stops(window)
    unmarked = []

    for stop in stops:
        elsewhere = next(other for other in stops if not _related(other, stop))
        _focus(elsewhere, application)
        unfocused = stop.grab().toImage()
        _focus(stop, application)
        assert stop.hasFocus(), type(stop).__name__

        if stop.grab().toImage() == unfocused:
            unmarked.append(type(stop).__name__)

    return unmarked


def test_every_tab_stop_on_the_dashboard_shows_the_focus(
    dashboard: SimulationView, application: QApplication
) -> None:
    """Every control Tab reaches, in every kind of View, looks different while it has the focus.

    The walk takes the controls from the built dashboard rather than from a
    list, so a control added later to any View is in it.
    """

    assert len(built_view_kinds(dashboard)) == len(REGISTERED), built_view_kinds(dashboard)
    stops = _tab_stops(dashboard)
    kinds = {type(stop).__name__ for stop in stops}

    # The controls that drew no mark before `PL-63FQ` are all in the walk.
    assert {"_SettingSlider", "SelectorComboBox", "TimeBaseSelector", "FocusedComboBox"} <= kinds
    assert {"HeadingScroll", "ViewScroll", "FittedScroll"} <= kinds
    assert _unmarked(dashboard, application) == []


def test_every_tab_stop_in_the_new_case_question_shows_the_focus(
    dashboard: SimulationView, application: QApplication
) -> None:
    """The new-case question is a window of its own, so the dashboard's walk does not reach it.

    The marks editor was the other window until `PL-CHX0` moved it into the
    Bookmarks View, where the dashboard's walk covers it.
    """

    snapshot = SimulationController(agent_id=_AGENT_ID).snapshot()
    question = new_case_question(snapshot, "Isoflurane", 0)
    confirmation = NewCaseDialog(question, dashboard)
    confirmation.show()
    application.processEvents()
    assert _unmarked(confirmation, application) == []
    confirmation.close()


def _accessible_tree(root: QAccessibleInterface) -> list[QAccessibleInterface]:
    """Every node of the accessible tree under `root`, as Qt hands it to the platform."""

    nodes = [root]

    for node in nodes:
        nodes.extend(node.child(index) for index in range(node.childCount()))

    return nodes


def _labels(node: QAccessibleInterface) -> list[str]:
    """Return the text of each label tied to `node`, which every platform reports as its label."""

    return [
        label.text(QAccessible.Text.Name) for label, _ in node.relations(QAccessible.Relation.Label)
    ]


def _said_purpose(node: QAccessibleInterface) -> str:
    """Return what a screen reader is told a control is for, or "" where it is told nothing.

    A label tied to the control comes first, because every platform reports
    it. Otherwise the control's own name counts, unless the name only repeats
    the control's value. On Linux and macOS, Qt names a selector by the entry
    it shows (`QAccessibleComboBox::text` in Qt 6.12), so "Sevoflurane" alone
    says nothing about what the selector sets.
    """

    labels = _labels(node)

    if labels:
        return labels[0]

    name = node.text(QAccessible.Text.Name)

    return "" if name == node.text(QAccessible.Text.Value) else name


def _unnamed(window: QWidget) -> list[str]:
    """Return each control in `window` that a reader can reach and a screen reader cannot name.

    A control a reader can reach is a node on screen that takes the focus.
    """

    return [
        f"{node.role().name} {type(node.object()).__name__}"
        for node in _accessible_tree(QAccessible.queryAccessibleInterface(window))
        if node.state().focusable and not node.state().invisible and not _said_purpose(node)
    ]


def test_every_control_a_reader_can_reach_says_what_it_is_for(
    dashboard: SimulationView, application: QApplication
) -> None:
    """`PL-RK9Z`: no control reaches a screen reader without a name for its purpose.

    WCAG 2.2 SC 4.1.2 (Name, Role, Value) asks every user interface component
    for a name that a program can read. The walk reads the tree that Qt hands
    each platform's accessibility interface, in every kind of View and in the
    new-case question, so a control added later to any of them is in it.
    Before `PL-RK9Z`, the walk found 61 controls without one, among them the
    bookmark editor's fields, the price form's fields, the Area corners, the
    scroll boxes and every selector.
    """

    assert len(built_view_kinds(dashboard)) == len(REGISTERED), built_view_kinds(dashboard)
    assert _unnamed(dashboard) == []

    snapshot = SimulationController(agent_id=_AGENT_ID).snapshot()
    confirmation = NewCaseDialog(new_case_question(snapshot, "Isoflurane", 0), dashboard)
    confirmation.show()
    application.processEvents()
    assert _unnamed(confirmation) == []
    confirmation.close()


def test_each_selector_is_named_by_its_shown_label_on_every_platform(
    dashboard: SimulationView,
) -> None:
    """Each selector has a label tied to it, and its accessible name starts with the label's text.

    Linux and macOS take a selector's purpose from the tied label, and Windows
    from the accessible name (`qt_widgets.label_control`). The run's agent
    selector had no label shown beside it, so it gained one, "Agent". The name
    is compared with the text the label shows, not with the label's accessible
    name, because `label_control` gives a label the selector's own name where
    the label alone does not say which control it is (`PL-YSFX`).
    """

    selectors = [
        node
        for node in _accessible_tree(QAccessible.queryAccessibleInterface(dashboard))
        if node.role() is QAccessible.Role.ComboBox and not node.state().invisible
    ]
    labels = {_labels(node)[0] if _labels(node) else "" for node in selectors}

    # The agent selector, the playback rate, the branch point, both time
    # bases, the chart's top, the schematic's top, the cost unit, the price
    # form's agent and the bookmark editor's compartment.
    assert len(selectors) == 10
    assert AGENT_SELECTOR_LABEL in labels

    for node in selectors:
        tied = node.relations(QAccessible.Relation.Label)
        selector = node.object()
        assert isinstance(selector, QWidget)
        assert tied, selector.accessibleName()
        shown = tied[0][0].object()
        assert isinstance(shown, QLabel)
        assert selector.accessibleName().startswith(shown.text()), shown.text()


#: The controls a reader can reach that a screen reader is told are for the
#: same thing, each against its reason. The test below checks the table in both
#: directions: a shared name that no entry lists fails, and so does an entry
#: that no two controls share any more. It is empty since `PL-XV64` named each
#: Area's corners and borders with the Area.
SHARED_PURPOSES: Final[dict[tuple[str, str], str]] = {}

#: The kinds of View that draw against an axis, whose controls each name their
#: plot. A split Area of one of these shows two plots with the same controls.
#: A copy of any other kind shows the same shared state as the original, so its
#: controls are "actually identical", which the ARIA Authoring Practices Guide
#: lets share a name (`PL-XV64`).
PLOT_KINDS: Final = (CONCENTRATION_CHART, WASH_IN, COMPARTMENT_SCHEMATIC)


def _split_each_area_of(
    view: SimulationView, application: QApplication, kinds: tuple[ViewKind, ...]
) -> None:
    """Split each Area that shows one of `kinds` from its Area menu, as a reader does.

    Each half is checked to draw its View, because a View that its Area is too
    small for is hidden, and the walk would then not reach its controls.
    """

    layout = view.layout_container
    split = [
        area for area in areas_in(layout.model.windows[MAIN_WINDOW].tree) if area.view in kinds
    ]
    assert sorted(area.view for area in split) == sorted(kinds)

    for area in split:
        (operation,) = [
            entry for entry in layout.operations(area.id) if entry.label == SPLIT_SIDE_BY_SIDE_LABEL
        ]
        layout.perform(operation)
        _settle(application)

    view.present(False)
    _settle(application)
    shown = [area for area in areas_in(layout.model.windows[MAIN_WINDOW].tree)]

    assert len(shown) == len(REGISTERED) + len(kinds)
    for area in shown:
        frame = layout.frame(area.id)
        assert frame.content.isVisible(), f"{area.view} in Area {area.id} is not drawn"


def _compared_dashboard(
    application: QApplication, runs: int, shipped: ShippedWorkspaceId | None = None
) -> SimulationView:
    """The dashboard showing one run or a trunk and its branch, in one Workspace.

    With no `shipped` id, the one Workspace shows every kind of View. With an
    id, the window holds the shipped Workspaces and shows the one named. The
    branch is taken in the first shipped Workspace, which shows the branch
    control, and the window then switches tab, as a user would. The window is
    large enough that every View draws everything it can show.
    """

    case = _branched_case()
    workspaces = every_registered_view() if shipped is None else shipped_workspaces()
    view = SimulationView((case.trunk,), case=case, workspaces=workspaces)
    view.resize(*EVERY_REGISTERED_VIEW_SIZE_PX)
    view.show()
    application.processEvents()
    view.present(False)
    _settle(application)

    if runs == 2:
        _take_fork(view, 60.0)
        _settle(application)
        view.present(False)
        _settle(application)

    if shipped is not None and SHIPPED_WORKSPACE_IDS.index(shipped):
        index = SHIPPED_WORKSPACE_IDS.index(shipped)
        QTest.mouseClick(view.tab_strip.tab_at(index), Qt.MouseButton.LeftButton)
        _settle(application)
        assert view.workspaces.active == index

    assert len(view.runs) == runs

    return view


#: The Workspaces a screen-reader walk covers: one that shows every kind of
#: View, so a View registered later is in the walk, and each shipped
#: Workspace, as a user first meets it.
WALKED: Final[tuple[ShippedWorkspaceId | None, ...]] = (None, *SHIPPED_WORKSPACE_IDS)
WALKED_IDS: Final = ["every kind of View", *(str(shipped) for shipped in SHIPPED_WORKSPACE_IDS)]


def _reachable_purposes(window: QWidget) -> list[tuple[str, str]]:
    """Return the role and the said purpose of each control a reader can reach in `window`.

    An entry in a selector's list is left out. A screen reader reads it inside
    the selector it belongs to, so the same entry in two lists is told apart
    by its list.
    """

    return [
        (node.role().name, _said_purpose(node))
        for node in _accessible_tree(QAccessible.queryAccessibleInterface(window))
        if node.state().focusable
        and not node.state().invisible
        and node.role() is not QAccessible.Role.ListItem
    ]


def _told_names(window: QWidget) -> list[tuple[str, str]]:
    """Return the role and the name a screen reader is told for each control and picture shown.

    The controls are those `_reachable_purposes` returns. A picture that takes
    no focus is added, because a screen reader reaches it by moving through
    the window's objects. A picture that takes the focus is a control already,
    so it is not counted twice. Static text is left out: its name is the text the screen shows
    in that place, so the same words shown twice are told as the screen
    shows them.
    """

    pictures = [
        (node.role().name, node.text(QAccessible.Text.Name))
        for node in _accessible_tree(QAccessible.queryAccessibleInterface(window))
        if node.role() is QAccessible.Role.Graphic
        and not node.state().invisible
        and not node.state().focusable
    ]

    return [*_reachable_purposes(window), *pictures]


@pytest.mark.parametrize("runs", [1, 2], ids=["one run", "two runs compared"])
@pytest.mark.parametrize("shipped", WALKED, ids=WALKED_IDS)
def test_no_two_controls_a_reader_can_reach_are_said_to_be_for_the_same_thing(
    application: QApplication, shipped: ShippedWorkspaceId | None, runs: int
) -> None:
    """`PL-YSFX`: each control or picture a reader reaches has a name no other of its role has.

    The W3C's ARIA Authoring Practices Guide asks for "unique names for
    elements with the same role unless the elements are actually identical"
    (in its section "Composing Effective and User-friendly Accessible Names"). A sighted
    user sees which run's panel or which plot a control sits in, and a
    screen-reader user hears only its name. Before `PL-YSFX`, two compared
    runs gave two selectors called "Playback" and two Start buttons, and the
    two plots gave two selectors called "Time base". The walk covers every kind
    of View and every shipped Workspace, so a control or a picture added later
    that repeats another's name fails here (`PL-9XGQ`).

    Only the Workspace with every kind of View checks that each entry of
    `SHARED_PURPOSES` is still needed, because a shipped Workspace with one
    Area would have no border to share a name.
    """

    view = _compared_dashboard(application, runs, shipped)
    counts = Counter(_told_names(view))
    shared = {purpose for purpose, count in counts.items() if count > 1}
    view.close()

    assert sorted(shared - set(SHARED_PURPOSES)) == []

    if shipped is None:
        assert sorted(set(SHARED_PURPOSES) - shared) == [], (
            "these entries of SHARED_PURPOSES name controls that no longer share a name - "
            "remove each"
        )


@pytest.mark.parametrize("runs", [1, 2], ids=["one run", "two runs compared"])
def test_no_two_controls_or_pictures_share_a_name_after_each_plot_area_is_split(
    application: QApplication, runs: int
) -> None:
    """`PL-XV64`: two copies of each plot, side by side, give no two controls or pictures one name.

    Each Area that draws a plot is split from its Area menu, as a reader
    splits it. Before `PL-XV64`, every corner was "Area corner", every border
    "Area border", and the two halves of a split Area gave two "Time base,
    Concentrations" selectors.
    """

    view = _compared_dashboard(application, runs)
    _split_each_area_of(view, application, PLOT_KINDS)
    counts = Counter(_told_names(view))
    shared = {purpose for purpose, count in counts.items() if count > 1}
    view.close()

    assert sorted(shared) == []


def _as_said(text: str) -> str:
    """Return `text` as a speech-input user says it: no mnemonic mark, case or punctuation.

    The Understanding document for WCAG 2.2 SC 2.5.3 (Label in Name) says that
    capitalization and most punctuation "are generally ignored when a user
    speaks a label", so a difference in either does not count. Qt draws a
    single "&" in a button's text as an underline under the next letter, and
    "&&" as one "&".
    """

    shown = text.replace("&&", "\0").replace("&", "").replace("\0", "&")
    words = "".join(character if character.isalnum() else " " for character in shown.casefold())

    return " ".join(words.split())


def _names_without_their_shown_words(window: QWidget) -> list[str]:
    """Return each button or box shown in `window` whose name does not start with its own words.

    The name is compared word by word, so "Settings" does not start with
    "Set". A button or a box with no letter or digit in its text is left out,
    such as "▶". The Understanding document for SC 2.5.3 does not count text
    used as a symbol as a label.
    """

    found = []

    for node in _accessible_tree(QAccessible.queryAccessibleInterface(window)):
        widget = node.object()

        if not isinstance(widget, QAbstractButton) or node.state().invisible:
            continue

        shown = _as_said(widget.text()).split()
        name = node.text(QAccessible.Text.Name)

        if shown and _as_said(name).split()[: len(shown)] != shown:
            found.append(f"{type(widget).__name__} shows {widget.text()!r} but is named {name!r}")

    return found


@pytest.mark.parametrize("runs", [1, 2], ids=["one run", "two runs compared"])
@pytest.mark.parametrize("shipped", WALKED, ids=WALKED_IDS)
def test_each_button_and_box_is_named_starting_with_the_words_it_shows(
    application: QApplication, shipped: ShippedWorkspaceId | None, runs: int
) -> None:
    """`PL-PN2C`: a speech-input user can say the words on a button or a box to click it.

    WCAG 2.2 SC 2.5.3 (Label in Name) asks that a control's name contain the
    words that label it on screen, and its Understanding document calls it
    best practice for the name to start with them. `qt_widgets.label_control`
    refuses such a name for a control labelled by a separate label. A button
    or a box shows its own words, and nothing refused a name for it that left
    them out. So the concentration chart's legend boxes showed "Circuit
    (solid)" and were named "Draw the Circuit compartment on the chart"
    until `PL-PN2C`.
    """

    view = _compared_dashboard(application, runs, shipped)
    found = _names_without_their_shown_words(view)
    view.close()

    assert found == []


#: The widget classes that paint themselves but draw no picture, each against
#: what it draws. A screen reader is told about each in another way, or what it
#: draws is told beside it. A class of this program that paints itself and is
#: not listed is taken for a picture, so the walk below fails on it until it is
#: described, as a `DescribedGraphic`, or listed here with its reason. A
#: subclass is covered by the class whose painting it keeps.
PAINTED_NOT_PICTURES: Final[dict[str, str]] = {
    "anesthesia_sim.app.area_layout._AreaHandle": (
        "a border between Areas, drawn as a line only while a drag of it is one move away; "
        "a screen reader is told it as a grip with a name"
    ),
    "anesthesia_sim.app.area_layout._CornerZone": (
        "an Area corner's grip; a screen reader is told it as a control with a name"
    ),
    "anesthesia_sim.app.area_layout._LayoutOverlay": (
        "a corner drag's preview, drawn only while a pointer drags; the Area menu offers the "
        "same splits, joins and swaps in words"
    ),
    "anesthesia_sim.app.qt_chart._LineSwatch": (
        "a legend's sample of a line, beside the check box that names the line"
    ),
    "anesthesia_sim.app.qt_chart._BandSwatch": (
        "the legend's sample of the MAC-awake band, beside the text that names the band"
    ),
    "anesthesia_sim.app.qt_schematic.ContainerNames": (
        "the six compartment names over their containers, which the schematic's description "
        "names one line each"
    ),
    "anesthesia_sim.app.qt_widgets.FocusRing": (
        "the ring round the control that has the keyboard focus, which a screen reader "
        "follows itself"
    ),
    "anesthesia_sim.app.qt_widgets.SelectorComboBox": (
        "a selector's arrow; a screen reader is told the selector as a combo box with a name "
        "and a value"
    ),
}


def _painter(widget: QWidget) -> str | None:
    """Return the class of this program that paints `widget`, or None where Qt or a library does."""

    painter = next(kind for kind in type(widget).__mro__ if "paintEvent" in vars(kind))

    if not painter.__module__.startswith("anesthesia_sim."):
        return None

    return f"{painter.__module__}.{painter.__qualname__}"


def _is_picture(widget: QWidget) -> bool:
    """Return whether `widget` draws a picture.

    A picture is a graphics view, which every plot is drawn in, an SVG
    widget, a label that shows an image, a recorded picture or a movie and no
    text, or a widget that a class of this program paints and
    `PAINTED_NOT_PICTURES` does not list. A picture drawn some
    other way, such as from an event filter, is not found here, which is why
    each `DescribedGraphic` and each node that reports itself as an image is
    checked as well.
    """

    if isinstance(widget, (QGraphicsView, QSvgWidget)):
        return True

    if isinstance(widget, QLabel):
        shows = not widget.pixmap().isNull() or not widget.picture().isNull()

        return not widget.text() and (shows or widget.movie() is not None)

    painter = _painter(widget)

    return painter is not None and painter not in PAINTED_NOT_PICTURES


def _described(node: QAccessibleInterface) -> bool:
    """Return whether `node` reports itself as an image with a name and a description."""

    return (
        node.role() is QAccessible.Role.Graphic
        and bool(node.text(QAccessible.Text.Name))
        and bool(node.text(QAccessible.Text.Description))
    )


def _undescribed_pictures(window: QWidget) -> list[str]:
    """Return each picture shown in `window` that a screen reader is not told about on its own.

    Each picture must sit in a `DescribedGraphic` that reports itself as an
    image with a name and a description, and no two pictures may share one,
    because one text alternative would then be read for two pictures. Each
    `DescribedGraphic` must be shown, since the window is large enough for
    every View to draw all it can. Each other node that reports itself as an
    image needs a name and a description too.
    """

    undescribed = []
    covered: Counter[int] = Counter()
    graphics = window.findChildren(DescribedGraphic)

    for widget in window.findChildren(QWidget):
        if not widget.isVisible() or not _is_picture(widget):
            continue

        graphic: QWidget | None = widget

        while graphic is not None and not isinstance(graphic, DescribedGraphic):
            graphic = graphic.parentWidget()

        if graphic is None or not _described(QAccessible.queryAccessibleInterface(graphic)):
            undescribed.append(type(widget).__name__)
        else:
            covered[id(graphic)] += 1

    undescribed.extend(
        f"{type(graphic).__name__} that holds {covered[id(graphic)]} pictures"
        for graphic in graphics
        if covered[id(graphic)] > 1
    )
    undescribed.extend(
        f"hidden {type(graphic).__name__}" for graphic in graphics if not graphic.isVisible()
    )
    undescribed.extend(
        f"{node.role().name} {type(node.object()).__name__}"
        for node in _accessible_tree(QAccessible.queryAccessibleInterface(window))
        if node.role() is QAccessible.Role.Graphic
        and not node.state().invisible
        and not _described(node)
    )

    return undescribed


@pytest.mark.parametrize("runs", [1, 2], ids=["one run", "two runs compared"])
@pytest.mark.parametrize("shipped", WALKED, ids=WALKED_IDS)
def test_every_control_and_picture_in_every_workspace_reaches_a_screen_reader_named(
    application: QApplication, shipped: ShippedWorkspaceId | None, runs: int
) -> None:
    """`PL-9XGQ`: no control a reader can reach goes unnamed, and no picture undescribed.

    WCAG 2.2 SC 4.1.2 (Name, Role, Value) asks every control for a name, and
    SC 1.1.1 (Non-text Content) asks every picture for a text alternative. A
    plot takes no focus, so the walk of the controls passed the wash-in plot
    and the schematic while they gave a screen reader nothing (`PL-R1M6`).
    This walk finds each picture from the widgets shown, so a plot, a
    schematic or a painted widget added later to any View is in it.
    """

    view = _compared_dashboard(application, runs, shipped)
    areas = len(view.layout_container.model.areas())
    built = len(view.layout_container.views())
    pictures = [widget for widget in view.findChildren(DescribedGraphic) if widget.isVisible()]
    unnamed = _unnamed(view)
    undescribed = _undescribed_pictures(view)
    view.close()

    # An Area whose View failed to build shows a notice instead, and would
    # hide that View's pictures from the walk.
    assert built == areas
    assert pictures
    assert unnamed == []
    assert undescribed == []


def test_each_painted_widget_that_draws_no_picture_still_paints() -> None:
    """Each entry of `PAINTED_NOT_PICTURES` names a class that still paints itself.

    An entry for a class that is gone or no longer paints would hide the next
    class given that name.
    """

    stale = []

    for name in PAINTED_NOT_PICTURES:
        module, _, qualname = name.rpartition(".")
        kind = getattr(importlib.import_module(module), qualname, None)

        if kind is None or "paintEvent" not in vars(kind):
            stale.append(name)

    assert stale == []


def test_each_run_s_and_each_plot_s_controls_are_named_with_their_run_or_plot(
    application: QApplication,
) -> None:
    """While two runs are compared, each run's controls name the run, and each plot's name the plot.

    The names start with the label shown beside or on the control, which the
    Understanding document for WCAG 2.2 SC 2.5.3 (Label in Name) calls best
    practice. A selector's purpose is what the label tied to it reports, which
    is what Linux and macOS read (`qt_widgets.label_control`), so each name
    below is the one every platform hears.
    """

    view = _compared_dashboard(application, 2)
    purposes = [purpose for _, purpose in _reachable_purposes(view)]
    view.close()

    def starting(label: str) -> list[str]:
        return sorted(purpose for purpose in purposes if purpose.startswith(label))

    assert starting("Playback") == ["Playback, Run 1", "Playback, Run 2"]
    assert starting("Start") == ["Start, Run 1", "Start, Run 2"]
    assert starting("Time base") == ["Time base, Concentrations", "Time base, Wash-in"]
    assert starting("Show an earlier part of the run") == [
        "Show an earlier part of the run, Concentrations",
        "Show an earlier part of the run, Wash-in",
    ]


def test_an_area_alone_of_its_kind_adds_no_name_to_its_legends_pictures_or_price_form(
    application: QApplication,
) -> None:
    """`PL-XV64`: a legend, a picture or the price form adds its Area's name only among copies.

    The Workspace shows each kind of View once, so no legend box, plot or
    schematic picture, or price form field ends with its Area's name.
    The controls beside a plot are the exception, because their names carry
    the Area's name in place of the View's title whether or not it repeats.
    """

    view = _compared_dashboard(application, 1)
    _settle(application)
    purposes = [purpose for _, purpose in _reachable_purposes(view)]
    pictures = [
        QAccessible.queryAccessibleInterface(picture).text(QAccessible.Text.Name)
        for picture in view.findChildren(DescribedGraphic)
        if picture.isVisible()
    ]
    removes = [form.remove_button.accessibleName() for form in view.findChildren(PriceEntry)]
    view.close()

    assert "Concentration chart legend" in purposes
    assert "Alveolar (long dash)" in purposes
    assert "Bottle price" in purposes
    assert removes == ["Remove price"]
    assert len(pictures) == 3
    for name in pictures:
        assert not name.endswith((", Concentrations", ", Wash-in", ", Compartment schematic"))


def test_the_schematic_view_renames_the_schematics_it_has_drawn_as_soon_as_it_is_told_its_area(
    application: QApplication,
) -> None:
    """`PL-XV64`: a schematic already drawn takes its Area's new name at once, not a frame later.

    The layout tells a View its Area's name each time it builds the Areas
    again, and the View draws a new frame only when the dashboard next
    presents one.
    """

    view = _compared_dashboard(application, 1)
    layout = view.layout_container
    (area,) = [
        area
        for area in areas_in(layout.model.windows[MAIN_WINDOW].tree)
        if area.view == COMPARTMENT_SCHEMATIC
    ]
    schematics = layout.frame(area.id).content

    def names() -> list[str]:
        return [
            QAccessible.queryAccessibleInterface(picture).text(QAccessible.Text.Name)
            for picture in schematics.findChildren(DescribedGraphic)
        ]

    assert len(names()) == 1
    alone = names()[0]
    assert alone.startswith("Compartment schematic, at ")

    schematics.name_controls(AreaName("Compartment schematic", 2))
    copied = names()
    schematics.name_controls(AreaName("Compartment schematic"))
    restored = names()
    view.close()

    assert copied == [f"{alone}, Compartment schematic 2"]
    assert restored == [alone]


def test_each_half_of_a_split_area_names_its_controls_with_the_half_s_number(
    application: QApplication,
) -> None:
    """`PL-XV64`: a split Area's halves name themselves, their corners and plot controls by number.

    The Areas showing one kind are numbered through the layout's splits, the
    left or upper part first, as VS Code numbers its editor groups. Each name
    still starts with the label shown. The legend's boxes, and each plot and
    schematic picture, add the number only while two Areas of their kind are
    on screen.
    """

    view = _compared_dashboard(application, 1)
    _split_each_area_of(view, application, PLOT_KINDS)
    purposes = [purpose for _, purpose in _reachable_purposes(view)]
    pictures = [
        QAccessible.queryAccessibleInterface(picture).text(QAccessible.Text.Name)
        for picture in view.findChildren(DescribedGraphic)
        if picture.isVisible()
    ]
    view.close()

    # Each half's plot, or its one run's schematic, ends its name with the
    # half's Area, so no two pictures share a name.
    halves = ("Concentrations", "Wash-in", "Compartment schematic")
    assert sorted(name.rsplit(", ", 1)[1] for name in pictures) == sorted(
        f"{title} {number}" for title in halves for number in (1, 2)
    )
    assert len(set(pictures)) == len(pictures)

    def starting(label: str) -> list[str]:
        return sorted(purpose for purpose in purposes if purpose.startswith(label))

    assert starting("Time base") == [
        "Time base, Concentrations 1",
        "Time base, Concentrations 2",
        "Time base, Wash-in 1",
        "Time base, Wash-in 2",
    ]
    assert starting("Axis top") == [
        "Axis top, Compartment schematic 1",
        "Axis top, Compartment schematic 2",
        "Axis top, Concentrations 1",
        "Axis top, Concentrations 2",
    ]
    assert starting("Alveolar (long dash)") == [
        "Alveolar (long dash), Concentrations 1",
        "Alveolar (long dash), Concentrations 2",
    ]
    assert starting("Concentration chart legend") == [
        "Concentration chart legend, Concentrations 1",
        "Concentration chart legend, Concentrations 2",
    ]
    assert starting("Area corner, Wash-in 2") == [
        "Area corner, Wash-in 2, bottom left",
        "Area corner, Wash-in 2, bottom right",
        "Area corner, Wash-in 2, top left",
        "Area corner, Wash-in 2, top right",
    ]
    assert "Area border, right of Concentrations 1" in purposes
    assert {"Concentrations 1", "Concentrations 2", "Parameters"} <= set(purposes)


def test_each_half_of_a_split_agent_cost_area_names_its_own_price_form(
    application: QApplication,
) -> None:
    """`PL-XV64`: each copy of the price form holds what was typed in it, so each is named apart.

    The unit selector acts on the reader's one set of preferences, so its two
    copies are the same control twice and keep one name. Before this, both
    forms' fields and buttons had the same names, such as two "Bottle price"
    fields and two "Set price" buttons. Each form's Remove button is
    unavailable until a price is stored, so a keyboard walk passes over it, and
    its name is read from the button itself.
    """

    view = _compared_dashboard(application, 1)
    _split_each_area_of(view, application, (AGENT_COST,))
    purposes = [purpose for _, purpose in _reachable_purposes(view)]
    removes = [form.remove_button.accessibleName() for form in view.findChildren(PriceEntry)]
    view.close()

    assert sorted(removes) == ["Remove price, Agent cost 1", "Remove price, Agent cost 2"]

    for label in (
        f"{AGENT_FIELD_LABEL}, {PRICE_FORM_KIND}",
        BOTTLE_PRICE_FIELD_LABEL,
        BOTTLE_VOLUME_FIELD_LABEL,
        CURRENCY_FIELD_LABEL,
        APPLIES_ON_FIELD_LABEL,
        SET_PRICE_LABEL,
    ):
        assert sorted(purpose for purpose in purposes if purpose.startswith(label)) == [
            f"{label}, Agent cost 1",
            f"{label}, Agent cost 2",
        ]

    assert purposes.count(UNIT_CHOICE_LABEL) == 2


def test_a_control_named_for_one_of_two_runs_takes_its_label_s_name_back_when_one_is_drawn(
    application: QApplication,
) -> None:
    """A name written for a compared run goes once the run is the only one drawn again.

    The label keeps the name it was given only while it has one, so a screen
    reader on Linux or macOS is not left saying "Playback, Run 1" for the only
    run on screen.
    """

    window = QWidget()
    label = QLabel("Playback", window)
    selector = SelectorComboBox(window)
    selector.addItem("1× real time")

    label_control(label, selector, control_name("Playback", "Run 1"))
    node = QAccessible.queryAccessibleInterface(selector)
    assert (_labels(node), selector.accessibleName()) == (["Playback, Run 1"], "Playback, Run 1")

    label_control(label, selector, control_name("Playback", None))
    assert (_labels(node), selector.accessibleName()) == (["Playback"], "Playback")


def test_a_name_that_does_not_start_with_the_shown_label_is_refused(
    application: QApplication,
) -> None:
    """A name that drops the label shown is refused, and the control keeps the name it had.

    A screen reader user would hear one name and a speech-input user would
    have to say a word that is not on screen. "Rate of playback" beside a
    label that shows "Playback" is such a name.
    """

    window = QWidget()
    label = QLabel("Playback", window)
    selector = SelectorComboBox(window)
    selector.addItem("1× real time")
    label_control(label, selector)

    with pytest.raises(ValueError, match="'Rate of playback'.*'Playback'"):
        label_control(label, selector, "Rate of playback")

    assert (selector.accessibleName(), label.accessibleName()) == ("Playback", "")


def _texts(widget: QWidget) -> tuple[str, str, str]:
    """The name, description and help text that Qt hands a screen reader for `widget`."""

    node = QAccessible.queryAccessibleInterface(widget)

    return (
        node.text(QAccessible.Text.Name),
        node.text(QAccessible.Text.Description),
        node.text(QAccessible.Text.Help),
    )


@pytest.mark.parametrize("on_macos", [False, True], ids=["Windows and Linux", "macOS"])
def test_a_control_s_hint_is_its_description_except_on_macos_where_it_is_its_help(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, on_macos: bool
) -> None:
    """`PL-26K2`: on macOS a control is described by its name, and its hint is its help text.

    VoiceOver reads a widget's description in place of its name
    (`qt_widgets.description_is_read_as_the_name`). Three controls are
    written out: a corner with a hint, a button whose tool tip Qt would read
    as its description, and an entry field whose placeholder Qt would read
    as its description. A selector with none of the three keeps no
    description on either platform.
    """

    monkeypatch.setattr(qt_widgets, "description_is_read_as_the_name", lambda: on_macos)
    window = QWidget()
    corner = QWidget(window)
    name_control(corner, "Area corner, Wash-in, top left", "Drag it to split or join the Area.")
    button = QPushButton("‹", window)
    button.setToolTip("Show an earlier part of the run")
    name_control(button, "Show an earlier part of the run, Wash-in")
    label = QLabel("Name", window)
    entry = QLineEdit(window)
    entry.setPlaceholderText("Optional")
    label_control(label, entry, "Name, MAC target")
    agent = QLabel("Agent", window)
    selector = SelectorComboBox(window)
    selector.addItem("Sevoflurane")
    label_control(agent, selector)

    if on_macos:
        assert _texts(corner) == (
            "Area corner, Wash-in, top left",
            "Area corner, Wash-in, top left",
            "Drag it to split or join the Area.",
        )
        assert _texts(button) == (
            "Show an earlier part of the run, Wash-in",
            "Show an earlier part of the run, Wash-in",
            "",
        )
        assert _texts(entry) == ("Name, MAC target", "Name, MAC target", "Optional")
    else:
        assert _texts(corner) == (
            "Area corner, Wash-in, top left",
            "Drag it to split or join the Area.",
            "",
        )
        assert _texts(button) == (
            "Show an earlier part of the run, Wash-in",
            "Show an earlier part of the run",
            "",
        )
        assert _texts(entry) == ("Name, MAC target", "Optional", "")
        # Qt reads the placeholder itself, so a placeholder changed later is
        # the one a screen reader hears.
        entry.setPlaceholderText("Required")
        assert _texts(entry)[1] == "Required"

    assert _texts(selector)[1:] == ("", "")


def _described_in_place_of_their_names(window: QWidget) -> list[str]:
    """Each widget whose description a Mac user would hear without what its name says.

    A control passes with no description, or with its name as its
    description. A picture passes when its description opens with its name
    and a full stop. A menu has no name on any platform, so its description is
    all a screen reader says of it there as everywhere, and it is skipped.
    """

    found = []

    for widget in [window, *window.findChildren(QWidget)]:
        node = QAccessible.queryAccessibleInterface(widget)

        if node is None or isinstance(widget, QMenu):
            continue

        name = node.text(QAccessible.Text.Name)
        description = node.text(QAccessible.Text.Description)

        if isinstance(widget, DescribedGraphic):
            if not description.startswith(f"{name}.\n"):
                found.append(f"{type(widget).__name__} {name!r} opens with {description[:40]!r}")
        elif description not in ("", name):
            found.append(f"{type(widget).__name__} {name!r} is described as {description!r}")

    return found


@pytest.mark.parametrize("runs", [1, 2], ids=["one run", "two runs compared"])
@pytest.mark.parametrize("shipped", WALKED, ids=WALKED_IDS)
def test_on_macos_no_widget_is_described_by_less_than_its_name(
    application: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    shipped: ShippedWorkspaceId | None,
    runs: int,
) -> None:
    """`PL-26K2`: VoiceOver never reads a description that leaves out what a widget's name says.

    On macOS, VoiceOver reads a widget's description in place of its name
    (`qt_widgets.description_is_read_as_the_name`). Before `PL-26K2`, a Mac
    user heard an Area border as "The arrow keys move it.", each plot's
    earlier and later buttons without the plot's name, a mark's name field as
    "Optional", and each plot without its window or whether it is held. The
    walk covers what each shipped Workspace shows, with one run and with two
    compared, with the platform rule set as it is on macOS.
    """

    monkeypatch.setattr(qt_widgets, "description_is_read_as_the_name", lambda: True)
    view = _compared_dashboard(application, runs, shipped)
    found = _described_in_place_of_their_names(view)
    view.close()

    assert found == []


def test_a_plot_is_not_a_tab_stop(dashboard: SimulationView) -> None:
    """A plot takes no key, so Tab passes over it rather than landing where nothing happens."""

    plots = dashboard.findChildren(PlotWidget)

    assert plots
    for plot in plots:
        assert plot.focusPolicy() == Qt.FocusPolicy.NoFocus
        assert plot.viewport().focusPolicy() == Qt.FocusPolicy.NoFocus


def _left_edge(control: QWidget) -> list[QColor]:
    """Return the colours of the ring's columns at the middle of the control's left edge."""

    image: QImage = control.grab().toImage()

    return [image.pixelColor(column, image.height() // 2) for column in range(FOCUS_RING_WIDTH)]


def test_the_ring_shows_after_a_tab_press_and_not_after_a_click(application: QApplication) -> None:
    """The keyboard gives the focus with the ring in INK, and a later click gives it without.

    The click comes after a Tab press, so the window has already recorded a
    keyboard focus change, and the ring must still stay off. A click on a
    blank part of the page gives the page's scroll area the focus, and must
    not draw a ring round the whole page.
    """

    case = BranchedCase(SimulationController(agent_id=_AGENT_ID))
    view = SimulationView((case.trunk,), case=case)
    view.resize(1366, 768)
    view.show()
    view.activateWindow()
    application.processEvents()
    view.present(False)
    application.processEvents()
    first, second = [slider for slider in view.findChildren(QSlider) if slider.isVisible()][:2]
    ring = first.findChild(FocusRing)
    assert ring is not None

    QTest.keyClick(view, Qt.Key.Key_Tab)
    _focus(first, application)
    assert ring.showing()
    assert ring.colour() == QColor(INK)
    assert _left_edge(first) == [QColor(INK)] * FOCUS_RING_WIDTH

    QTest.mouseClick(second, Qt.MouseButton.LeftButton, pos=QPoint(second.width() - 3, 3))
    application.processEvents()
    second_ring = second.findChild(FocusRing)
    assert second_ring is not None
    assert second.hasFocus()
    assert not second_ring.showing()
    assert not ring.showing()

    QTest.keyClick(view, Qt.Key.Key_Tab)
    page = next(
        area
        for area in view.findChildren(QScrollArea)
        if type(area) is HeadingScroll and area.widget().findChild(QSlider)
    )
    blank = page.widget()
    QTest.mouseClick(
        blank, Qt.MouseButton.LeftButton, pos=QPoint(blank.width() - 5, blank.height() - 5)
    )
    application.processEvents()
    page_ring = page.findChild(FocusRing)
    assert page_ring is not None
    assert page.hasFocus()
    assert not page_ring.showing()
    view.close()


def test_the_agent_selector_draws_its_ring_in_the_agent_foreground(
    application: QApplication,
) -> None:
    """The agent selector's ring is the running agent's foreground, so it shows on the ISO fill."""

    case = BranchedCase(SimulationController(agent_id=_AGENT_ID))
    view = SimulationView((case.trunk,), case=case)
    view.resize(1366, 768)
    view.show()
    view.activateWindow()
    application.processEvents()
    selector = next(
        box
        for box in view.findChildren(SelectorComboBox)
        if box.isVisible() and "bold" in box.styleSheet()
    )
    foreground = QColor(AGENT_COLOR_SCHEMES[_AGENT_ID].foreground)

    QTest.keyClick(view, Qt.Key.Key_Tab)
    _focus(selector, application)
    assert selector.focus_ring.showing()
    assert selector.focus_ring.colour() == foreground
    view.close()


def test_each_run_button_draws_a_pressed_and_a_focused_state(application: QApplication) -> None:
    """Each run button draws three different images: at rest, held down and keyboard-focused."""

    case = BranchedCase(SimulationController(agent_id=_AGENT_ID))
    view = SimulationView((case.trunk,), case=case)
    view.resize(1366, 768)
    view.show()
    view.activateWindow()
    application.processEvents()
    view.present(False)
    application.processEvents()
    QTest.keyClick(view, Qt.Key.Key_Tab)
    buttons = {button.text(): button for button in view.findChildren(QPushButton)}

    # Pause is unavailable until the run starts, and Start is unavailable
    # once it has, so each is checked while it can be pressed.
    for label in ("Start", "Reset"):
        _assert_three_looks(buttons[label], buttons["Branch"], application)

    buttons["Start"].click()
    view.present(False)
    application.processEvents()
    _assert_three_looks(buttons["Pause"], buttons["Branch"], application)
    view.close()


def _assert_three_looks(button: QPushButton, elsewhere: QWidget, application: QApplication) -> None:
    assert button.isEnabled(), button.text()
    _focus(elsewhere, application)
    rest = button.grab().toImage()
    button.setDown(True)
    application.processEvents()
    pressed = button.grab().toImage()
    button.setDown(False)
    _focus(button, application)
    focused = button.grab().toImage()

    # A pressed button is filled in INK, so the whole fill changes from
    # PANEL to INK while it is held down.
    fill = QPoint(CONTROL_BORDER_WIDTH + PANEL_RADIUS, pressed.height() // 2)
    assert rest.pixelColor(fill) == QColor(PANEL), button.text()
    assert pressed.pixelColor(fill) == QColor(INK), button.text()
    assert rest != focused, button.text()
    assert pressed != focused, button.text()
