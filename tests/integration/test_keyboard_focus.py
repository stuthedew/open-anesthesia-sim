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

from collections.abc import Iterator

import pytest
from pyqtgraph import PlotWidget
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QAccessible, QAccessibleInterface, QColor, QImage
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QPushButton, QScrollArea, QSlider, QWidget

from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import AGENT_SELECTOR_LABEL, new_case_question
from anesthesia_sim.app.qt_widgets import FocusRing, NewCaseDialog, SelectorComboBox
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.theme import (
    AGENT_COLOR_SCHEMES,
    CONTROL_BORDER_WIDTH,
    FOCUS_RING_WIDTH,
    INK,
    PANEL,
    PANEL_RADIUS,
)
from anesthesia_sim.app.view_registry import REGISTERED
from tests.integration.simulation_view.simulation_view_support import (
    EVERY_REGISTERED_VIEW_SIZE_PX,
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
    """Each selector has a label tied to it, and its accessible name starts with that label.

    Linux and macOS take a selector's purpose from the tied label, and Windows
    from the accessible name (`qt_widgets.label_control`). The run's agent
    selector had no label shown beside it, so it gained one, "Agent".
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
        label = _labels(node)
        selector = node.object()
        assert isinstance(selector, QWidget)
        assert label, selector.accessibleName()
        assert selector.accessibleName().startswith(label[0]), label[0]


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
