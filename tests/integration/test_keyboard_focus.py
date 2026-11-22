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
from PySide6.QtGui import QColor, QImage
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QPushButton, QScrollArea, QSlider, QWidget

from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import new_case_question
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
    assert {"QScrollArea", "ViewScroll", "_KeyScroll"} <= kinds
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
