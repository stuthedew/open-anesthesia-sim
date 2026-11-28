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

from collections import Counter
from collections.abc import Iterator
from typing import Final

import pytest
from pyqtgraph import PlotWidget
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QAccessible, QAccessibleInterface, QColor, QImage
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QScrollArea, QSlider, QWidget

from anesthesia_sim.app.agent_cost import UNIT_CHOICE_LABEL
from anesthesia_sim.app.area_layout import SPLIT_SIDE_BY_SIDE_LABEL
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import AGENT_SELECTOR_LABEL, control_name, new_case_question
from anesthesia_sim.app.qt_agent_price import (
    AGENT_FIELD_LABEL,
    APPLIES_ON_FIELD_LABEL,
    BOTTLE_PRICE_FIELD_LABEL,
    BOTTLE_VOLUME_FIELD_LABEL,
    CURRENCY_FIELD_LABEL,
    PRICE_FORM_KIND,
    SET_PRICE_LABEL,
)
from anesthesia_sim.app.qt_widgets import (
    DescribedGraphic,
    FocusRing,
    NewCaseDialog,
    SelectorComboBox,
    label_control,
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
from anesthesia_sim.app.view_registry import (
    AGENT_COST,
    COMPARTMENT_SCHEMATIC,
    CONCENTRATION_CHART,
    REGISTERED,
    WASH_IN,
)
from anesthesia_sim.layout.model import MAIN_WINDOW
from anesthesia_sim.layout.tree import ViewKind, areas_in
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
    assert {"QScrollArea", "ViewScroll", "FittedScroll"} <= kinds
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


def _compared_dashboard(application: QApplication, runs: int) -> SimulationView:
    """The dashboard with every kind of View, showing one run or a trunk and its branch."""

    case = _branched_case()
    view = SimulationView((case.trunk,), case=case, workspaces=every_registered_view())
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

    assert len(view.runs) == runs

    return view


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


@pytest.mark.parametrize("split", [False, True], ids=["each View once", "each plot split"])
@pytest.mark.parametrize("runs", [1, 2], ids=["one run", "two runs compared"])
def test_no_two_controls_a_reader_can_reach_are_said_to_be_for_the_same_thing(
    application: QApplication, runs: int, split: bool
) -> None:
    """`PL-YSFX`: each control a screen reader reaches has a name no other control of its role has.

    The W3C's ARIA Authoring Practices Guide asks for "unique names for
    elements with the same role unless the elements are actually identical"
    (in its section "Composing Effective and User-friendly Accessible Names"). A sighted
    user sees which run's panel or which plot a control sits in, and a
    screen-reader user hears only its name. Before `PL-YSFX`, two compared
    runs gave two selectors called "Playback" and two Start buttons, and the
    two plots gave two selectors called "Time base". The walk covers every kind
    of View, so a control added later that repeats another's name fails here.

    The walk is taken again after each Area that draws a plot is split, so
    that two copies of each plot are on screen. Before `PL-XV64`, the 32
    corners were each "Area corner", the 7 borders each "Area border", and a
    split Area's two halves gave two "Time base, Concentrations" selectors.
    """

    view = _compared_dashboard(application, runs)

    if split:
        _split_each_area_of(view, application, PLOT_KINDS)

    counts = Counter(_reachable_purposes(view))
    shared = {purpose for purpose, count in counts.items() if count > 1}
    view.close()

    assert sorted(shared - set(SHARED_PURPOSES)) == []
    assert sorted(set(SHARED_PURPOSES) - shared) == [], (
        "these entries of SHARED_PURPOSES name controls that no longer share a name - remove each"
    )


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


def test_each_half_of_a_split_area_names_its_controls_with_the_half_s_number(
    application: QApplication,
) -> None:
    """`PL-XV64`: a split Area's halves name themselves, their corners and plot controls by number.

    The Areas showing one kind are numbered in reading order, as VS Code
    numbers its editor groups. Each name still starts with the label shown.
    The legend's boxes, and each plot and schematic picture, add the number
    only while two Areas of their kind are on screen.
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
    assert starting("Draw the Alveolar compartment") == [
        "Draw the Alveolar compartment on the chart, Concentrations 1",
        "Draw the Alveolar compartment on the chart, Concentrations 2",
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
    assert "Area border, Concentrations 1" in purposes
    assert {"Concentrations 1", "Concentrations 2", "Parameters"} <= set(purposes)


def test_each_half_of_a_split_agent_cost_area_names_its_own_price_form(
    application: QApplication,
) -> None:
    """`PL-XV64`: each copy of the price form holds what was typed in it, so each is named apart.

    The unit selector acts on the reader's one set of preferences, so its two
    copies are the same control twice and keep one name. Before this, both
    forms' fields and buttons had the same names, such as two "Bottle price"
    fields and two "Set price" buttons.
    """

    view = _compared_dashboard(application, 1)
    _split_each_area_of(view, application, (AGENT_COST,))
    purposes = [purpose for _, purpose in _reachable_purposes(view)]
    view.close()

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
        if type(area) is QScrollArea and area.widget().findChild(QSlider)
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
