"""The dashboard, driven headless against real runs.

These tests cover the agent selector.

`simulation_view_support.py` describes the whole suite.
"""

import importlib
import re

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget

from anesthesia_sim.app import run_view as run_view_module
from anesthesia_sim.app import theme
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import RUNNING_AGENT_LOCK_TEXT
from anesthesia_sim.app.run_view import RunView
from anesthesia_sim.app.theme import AGENT_COLOR_SCHEMES, AGENT_SELECTOR_WIDTH
from anesthesia_sim.core.parameters import AGENT_DATA_FILENAMES, load_agent_parameters
from tests.integration.simulation_view.simulation_view_support import (
    FIRST_RUN,
    _colour_name,
    _dials,
    _identity_controls,
    _select_agent,
    _settle,
    _shown_view,
)

# ---------------------------------------------------- the agent selector


def test_agent_dropdown_options_pair_every_color_with_the_agent_name(
    application: QApplication,
) -> None:
    """Colour is a redundant cue: every option pairs the name with its ISO 5360 pair."""

    combo = _shown_view(application, SimulationController()).runs[0]._agent_dropdown
    keys = [combo.itemData(index) for index in range(combo.count())]

    assert keys == list(AGENT_DATA_FILENAMES)
    assert set(keys) == set(AGENT_COLOR_SCHEMES)

    for index, agent_id in enumerate(keys):
        scheme = AGENT_COLOR_SCHEMES[agent_id]

        assert combo.itemText(index) == load_agent_parameters(agent_id).display_name
        assert _colour_name(combo.itemData(index, Qt.ItemDataRole.BackgroundRole)) == (
            _colour_name(scheme.fill)
        )
        assert _colour_name(combo.itemData(index, Qt.ItemDataRole.ForegroundRole)) == (
            _colour_name(scheme.foreground)
        )


def test_refresh_view_shows_current_agent_in_subtitle_and_dropdown(
    application: QApplication,
) -> None:
    run = _shown_view(application, SimulationController(agent_id="isoflurane")).runs[0]
    scheme = AGENT_COLOR_SCHEMES["isoflurane"]

    assert "Isoflurane" in run._subtitle_text.text()
    assert run._agent_dropdown.currentData() == "isoflurane"
    assert scheme.fill in run._agent_header_badge.styleSheet()
    assert scheme.foreground in run._subtitle_text.styleSheet()
    assert scheme.fill in run._agent_dropdown.styleSheet()
    assert scheme.foreground in run._agent_dropdown.styleSheet()


@pytest.mark.parametrize("agent_id", list(AGENT_COLOR_SCHEMES))
def test_refresh_view_applies_current_agent_color_to_control_and_header(
    application: QApplication, agent_id: str
) -> None:
    run = _shown_view(application, SimulationController(agent_id=agent_id)).runs[0]
    scheme = AGENT_COLOR_SCHEMES[agent_id]

    assert run._agent_dropdown.currentData() == agent_id
    assert scheme.fill in run._agent_dropdown.styleSheet()
    assert scheme.foreground in run._agent_dropdown.styleSheet()
    assert scheme.fill in run._agent_header_badge.styleSheet()
    assert scheme.foreground in run._subtitle_text.styleSheet()
    assert load_agent_parameters(agent_id).display_name in run._subtitle_text.text()


@pytest.mark.parametrize("agent_id", list(AGENT_COLOR_SCHEMES))
def test_agent_header_badge_is_bordered_against_the_panel(
    application: QApplication, agent_id: str
) -> None:
    """Sevoflurane's fill is 1.37:1 on the panel, so the badge carries a border."""

    run = _shown_view(application, SimulationController(agent_id=agent_id)).runs[0]
    scheme = AGENT_COLOR_SCHEMES[agent_id]

    assert re.search(
        rf"border:\s*1px solid {re.escape(scheme.foreground)}", run._agent_header_badge.styleSheet()
    ), run._agent_header_badge.styleSheet()


@pytest.mark.parametrize("agent_id", list(AGENT_COLOR_SCHEMES))
def test_every_agent_has_render_objects_in_its_own_identification_color(
    application: QApplication, agent_id: str
) -> None:
    """The six identity controls carry the running agent's pair, and only its pair."""

    run = _shown_view(application, SimulationController(agent_id=agent_id)).runs[0]
    scheme = AGENT_COLOR_SCHEMES[agent_id]

    for control in _identity_controls(run):
        assert scheme.fill in control.styleSheet(), control
        assert scheme.foreground in control.styleSheet(), control

        for other_id, other in AGENT_COLOR_SCHEMES.items():
            if other_id != agent_id and other.fill != scheme.fill:
                assert other.fill not in control.styleSheet(), (control, other_id)


def test_switching_agent_repaints_the_header_badge_and_the_dropdown(
    application: QApplication,
) -> None:
    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    scheme = AGENT_COLOR_SCHEMES["desflurane"]

    _select_agent(run, "desflurane")

    assert controller.snapshot().agent_id == "desflurane"
    assert run._agent_dropdown.currentData() == "desflurane"
    assert "Desflurane" in run._subtitle_text.text()

    for control in _identity_controls(run):
        assert scheme.fill in control.styleSheet(), control
        assert scheme.foreground in control.styleSheet(), control


def test_refresh_view_disables_agent_dropdown_while_running(application: QApplication) -> None:
    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()
    view.present(False)

    assert view.runs[0]._agent_dropdown.isEnabled() is False
    assert view.runs[0]._agent_dropdown.isHidden() is True


@pytest.mark.parametrize("agent_id", list(AGENT_COLOR_SCHEMES))
def test_the_agent_name_stays_legible_while_the_run_disables_the_selector(
    application: QApplication, agent_id: str
) -> None:
    """`PL-61WW`: a disabled selector repaints the identity colour in a theme grey.

    So while the run locks the selector, the agent is named by a chip that
    is neither disabled nor greyed, in the agent's own pair, where the
    selector stood.
    """

    controller = SimulationController(agent_id=agent_id)
    view = _shown_view(application, controller)
    run = view.runs[0]
    scheme = AGENT_COLOR_SCHEMES[agent_id]
    controller.start()
    view.present(False)

    assert run._running_agent_display.isHidden() is False
    assert run._running_agent_display.isEnabled() is True
    assert scheme.fill in run._running_agent_display.styleSheet()
    assert run._running_agent_text.text() == load_agent_parameters(agent_id).display_name
    assert scheme.foreground in run._running_agent_text.styleSheet()
    assert scheme.foreground in run._running_agent_lock_text.styleSheet()
    assert run._agent_dropdown.isHidden() is True


@pytest.mark.parametrize("running", [False, True])
def test_exactly_one_of_the_selector_and_the_running_agent_display_is_shown(
    application: QApplication, running: bool
) -> None:
    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]

    if running:
        controller.start()
        view.present(False)

    assert run._agent_dropdown.isHidden() is not run._running_agent_display.isHidden()
    assert run._running_agent_display.isHidden() is not running


def test_the_running_agent_display_says_why_the_selector_is_gone(application: QApplication) -> None:
    controller = SimulationController(agent_id="desflurane")
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()
    view.present(False)

    assert run._running_agent_text.text() == "Desflurane"
    assert run._running_agent_lock_text.text() == RUNNING_AGENT_LOCK_TEXT
    assert run._running_agent_display.minimumWidth() == AGENT_SELECTOR_WIDTH
    assert run._running_agent_display.maximumWidth() == AGENT_SELECTOR_WIDTH
    assert run._agent_dropdown.minimumWidth() == AGENT_SELECTOR_WIDTH
    assert run._agent_dropdown.maximumWidth() == AGENT_SELECTOR_WIDTH


def test_the_running_agent_display_is_already_correct_before_it_is_shown(
    application: QApplication,
) -> None:
    """The chip is written every tick, so the frame that shows it has nothing to fix."""

    run = _shown_view(application, SimulationController(agent_id="isoflurane")).runs[0]
    scheme = AGENT_COLOR_SCHEMES["isoflurane"]

    assert run._running_agent_display.isHidden() is True
    assert scheme.fill in run._running_agent_display.styleSheet()
    assert run._running_agent_text.text() == "Isoflurane"
    assert scheme.foreground in run._running_agent_text.styleSheet()


def test_building_a_run_view_opens_no_window_of_its_own(application: QApplication) -> None:
    """A widget shown before a layout adopts it is a top-level window.

    The selector and the chip have their visibility written as the view is
    built, before any layout places them. So each is built with the view as
    its parent. A parentless one shown at that point opened a window of its
    own beside the dashboard (`PL-25KS`).
    """

    host = QWidget()
    windows_before = len(application.topLevelWindows())

    run = RunView(SimulationController(), host, run_id=FIRST_RUN, branch_control=False)
    application.processEvents()

    assert len(application.topLevelWindows()) == windows_before
    assert run.parent() is host

    host.deleteLater()
    _settle(application)


def test_the_delivered_label_on_screen_names_the_current_agent(application: QApplication) -> None:
    """Regression for a label hardcoded to "Delivered sevoflurane"."""

    run = _shown_view(application, SimulationController(agent_id="desflurane")).runs[0]

    assert _dials(run)._delivered_concentration_slider.name_label.text() == "Delivered desflurane"


def test_a_built_in_agent_without_an_identification_colour_fails_at_import() -> None:
    """Adding an agent without its ISO 5360 colour must stop the app starting.

    The guard runs at module scope, so covering it means re-executing the
    module body with the colour table short one entry, and reloading again
    afterwards so the genuine table is what every later test sees.
    """

    original = dict(theme.AGENT_COLOR_SCHEMES)
    theme.AGENT_COLOR_SCHEMES.pop(next(iter(original)))
    try:
        with pytest.raises(
            RuntimeError,
            match="^AGENT_COLOR_SCHEMES must define exactly the built-in volatile agents$",
        ):
            importlib.reload(run_view_module)
    finally:
        theme.AGENT_COLOR_SCHEMES.clear()
        theme.AGENT_COLOR_SCHEMES.update(original)
        importlib.reload(run_view_module)
