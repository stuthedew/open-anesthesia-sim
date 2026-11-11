"""A Reset or an agent change that raises part-way still withholds the discarded run's values.

`PL-MVCF` found that `RunView` counted a start-over only after
`SimulationController.reset()` returned. `reset()` clears the run's state
before its last statements, so a Reset that raised after that point left a run
at 0 s while the panel still counted it as the run the last frame drew. When
frames then failed, the halt kept that frame's values: a clock of 10 min and a
circuit at 1.61 % under a run that stood at 0 s.

These tests inject the failure into `SimulationController._note_recorded_settings`,
which `reset()` and `set_agent` both call after the run's state is cleared or
rebuilt, and make every frame fail. The expected texts are typed from what a
reader sees on a withheld card: a dash in place of the value, with its unit.
The tests render under the `offscreen` platform that `tests/conftest.py`
selects.
"""

from collections.abc import Iterator
from typing import NoReturn

import pytest
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication

from anesthesia_sim.app import simulation_view as simulation_view_module
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import READOUT_PANELS, SIMULATION_STEP_S
from anesthesia_sim.app.run_view import RunView
from anesthesia_sim.app.simulation_view import SimulationView

_SECONDS_PER_MINUTE = 60.0
_WINDOW_WIDTH_PX = 1400
_WINDOW_HEIGHT_PX = 1000

#: The index of the clock among the readout cards, and of every card that shows
#: a compartment's concentration.
_CLOCK_INDEX = next(index for index, panel in enumerate(READOUT_PANELS) if panel.quantity is None)
_COMPARTMENT_INDICES = tuple(
    index for index, panel in enumerate(READOUT_PANELS) if panel.quantity is not None
)

_SHOWN_VIEWS: list[SimulationView] = []


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


@pytest.fixture(autouse=True)
def _torn_down_views(application: QApplication) -> Iterator[None]:
    yield

    for view in _SHOWN_VIEWS:
        view.stop_timers()
        view.close()
        view.deleteLater()

    _SHOWN_VIEWS.clear()
    application.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    application.processEvents()


def _shown_run(application: QApplication, controller: SimulationController) -> RunView:
    """The only run of a dashboard over `controller`, shown and presented once."""

    view = SimulationView((controller,))
    _SHOWN_VIEWS.append(view)
    view.resize(_WINDOW_WIDTH_PX, _WINDOW_HEIGHT_PX)
    view.show()
    application.processEvents()
    view.present(False)

    return view.runs[0]


def _failing_assembly(*args: object, **kwargs: object) -> NoReturn:
    """Stand in for `assemble_chart_frame`, so that every frame fails."""

    raise RuntimeError("this frame could not be assembled")


def _failing_note(self: SimulationController) -> NoReturn:
    """Stand in for `_note_recorded_settings`, which runs after the state is cleared."""

    raise RuntimeError("the reset failed after it cleared the run")


def _cards(run: RunView) -> list[tuple[str, str]]:
    return [
        (panel.value_label.text(), panel.secondary_label.text())
        for panel in run._readout_row.panels
    ]


def _a_paused_run_at_10_minutes() -> SimulationController:
    controller = SimulationController()
    controller.start()

    for _ in range(round(10 * _SECONDS_PER_MINUTE / SIMULATION_STEP_S)):
        controller.advance(SIMULATION_STEP_S)

    controller.pause()

    return controller


def test_a_reset_that_raises_after_clearing_the_run_withholds_every_value(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The halt shows dashes, not the 10 min frame of the run that Reset discarded."""

    controller = _a_paused_run_at_10_minutes()
    run = _shown_run(application, controller)
    assert run._readout_row.panels[_CLOCK_INDEX].value_label.text() == "10m"
    monkeypatch.setattr(SimulationController, "_note_recorded_settings", _failing_note)
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    run._reset_button.click()

    assert controller.has_failed is True
    assert controller.snapshot().elapsed_s == 0.0
    cards = _cards(run)
    assert cards[_CLOCK_INDEX][0] == "—"
    assert [cards[index] for index in _COMPARTMENT_INDICES] == [("—%", "— ×MAC")] * len(
        _COMPARTMENT_INDICES
    )
    assert [panel._agent_accounting_detail_text.text() for panel in run._accounting_panels] == [
        "No frame has been drawn since the run started over."
    ] * len(run._accounting_panels)


def test_a_reset_refused_before_it_clears_anything_keeps_the_last_frame(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A refusal that leaves the run as it was is not a start-over, so the halt keeps the frame.

    `reset()` reads the settings record before it clears anything, and that read
    is the one step the core refuses (`PL-M4M0`). The run then still stands at
    10 min, and the last frame drawn describes it.
    """

    controller = _a_paused_run_at_10_minutes()
    run = _shown_run(application, controller)
    drawn = _cards(run)
    # Scale each tissue's perfusion fraction, past its guard, so that the tissue
    # flows sum to 6 L/min against a cardiac output of 5 L/min. The settings
    # record that `reset()` reads first then refuses them (`PL-M4M0`).
    patient = controller._state.uptake_system.patient
    scale = 6.0 / patient.cardiac_output_l_min

    for tissue in patient.tissues:
        object.__setattr__(tissue, "perfusion_fraction", tissue.perfusion_fraction * scale)

    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    run._reset_button.click()

    assert controller.has_failed is True
    assert controller.snapshot().elapsed_s == pytest.approx(10 * _SECONDS_PER_MINUTE)
    assert _cards(run) == drawn
    assert drawn[_CLOCK_INDEX][0] == "10m"


def test_an_agent_change_that_raises_after_rebuilding_the_run_withholds_every_value(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A switch that raised after the run was rebuilt has still discarded the run on screen."""

    controller = SimulationController()
    run = _shown_run(application, controller)
    assert run._readout_row.panels[_CLOCK_INDEX].value_label.text() != "—"
    monkeypatch.setattr(SimulationController, "_note_recorded_settings", _failing_note)
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    combo = run._agent_dropdown

    combo.setCurrentIndex(combo.findData("desflurane"))

    assert controller.has_failed is True
    assert controller.agent_id == "desflurane"
    cards = _cards(run)
    assert cards[_CLOCK_INDEX][0] == "—"
    assert [cards[index] for index in _COMPARTMENT_INDICES] == [("—%", "— ×MAC")] * len(
        _COMPARTMENT_INDICES
    )
