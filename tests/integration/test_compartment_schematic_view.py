"""The compartment schematic View in a real dashboard, from patient inputs to its drawn labels.

`docs/MODEL.md` § "The compartment schematic: what its heights, amounts and
share bar assert" is the specification (`PL-2881`), and `PL-RNYV` built the
View. These tests check two things. First, a run's inputs reach the drawn
labels through the model, against a closed form computed apart from the code
under test. Second, after each action a learner takes that changes which
state a run is in (a reset, an agent change, a branch, a branch taken at a
mark behind the clock, and a comparison opened and closed), every label
matches the run's state at that moment, and each schematic is named as the
run's own panel is named. They render under the `offscreen` platform that
`tests/conftest.py` selects.
"""

from collections.abc import Iterator
from math import exp, floor, log10

import pytest
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication

from anesthesia_sim.app.bookmarks import TimeBookmark
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import SIMULATION_STEP_S, TRUNK_RUN_INDEX
from anesthesia_sim.app.formatting import format_elapsed
from anesthesia_sim.app.run_view import RunView
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.view_registry import COMPARTMENT_SCHEMATIC, REGISTERED
from anesthesia_sim.app.views import CompartmentSchematicView
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.parameters import load_agent_parameters
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CaseInstant, FreshGasFlow
from anesthesia_sim.layout.model import LayoutModel
from anesthesia_sim.layout.tree import Area, AreaId, Window
from anesthesia_sim.layout.workspace import Origin, Workspace, WorkspaceName, WorkspaceSet

#: One Workspace that shows only the schematic, so every run it draws is the
#: schematic's.
_SCHEMATIC_ONLY = WorkspaceSet(
    (
        Workspace(
            WorkspaceName("Schematic"),
            Origin.mine(),
            LayoutModel((Window(Area(AreaId(1), COMPARTMENT_SCHEMATIC)),), AreaId(2)),
        ),
    ),
    0,
)

_WINDOW_WIDTH_PX = 1400
_WINDOW_HEIGHT_PX = 1000

# The compartments' names, restated rather than read from the readout panels,
# so an edit there cannot move both sides of an assertion at once.
_NAMES = ("Circuit", "Alveolar", "Mixed venous", "Vessel-rich group", "Muscle", "Fat")

SECONDS_PER_MINUTE = 60.0


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


@pytest.fixture
def shown(application: QApplication) -> Iterator[list[SimulationView]]:
    """The dashboards a test shows, closed and deleted when it ends."""

    views: list[SimulationView] = []

    yield views

    for view in views:
        view.stop_timers()
        view.close()
        view.deleteLater()

    application.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    application.processEvents()


def _dashboard(
    application: QApplication,
    shown: list[SimulationView],
    controller: SimulationController,
    case: BranchedCase | None = None,
) -> SimulationView:
    """A dashboard showing only the schematic, presented once, as `main()` opens one."""

    view = SimulationView((controller,), case=case, workspaces=_SCHEMATIC_ONLY)
    shown.append(view)
    view.resize(_WINDOW_WIDTH_PX, _WINDOW_HEIGHT_PX)
    view.show()
    application.processEvents()
    view.present(False)

    return view


def _settle(application: QApplication) -> None:
    application.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    application.processEvents()


def _schematic(view: SimulationView) -> CompartmentSchematicView:
    return next(v for v in view.layout_container.views() if isinstance(v, CompartmentSchematicView))


def _readout_values(run: RunView) -> tuple[str, ...]:
    """The tension each compartment's readout prints now, in the readout row's order."""

    return tuple(panel.value_label.text() for panel in run._readout_row.panels[1:])


def _assert_every_label_matches_its_run(view: SimulationView) -> None:
    """Each run has one schematic, named as its panel is named, labelled from its state now.

    A tension is checked against the run's own readout, which is written from
    the same snapshot by a different path. An amount is checked against the
    run's controller, read at this moment, in millilitres to two significant
    figures. So a schematic left at a state its run has left fails here.
    """

    schematics = _schematic(view).schematics

    assert len(schematics) == len(view.runs)

    for schematic, run in zip(schematics, view.runs, strict=True):
        panel_name = None if run._run_name_text.isHidden() else run._run_name_text.text()

        assert schematic.name_text.isHidden() is (panel_name is None)
        assert schematic.name_text.text() == (panel_name or "")

        readings = schematic.canvas.readings
        amounts = run.controller.snapshot().compartment_agent_amounts

        assert tuple(reading.name for reading in readings) == _NAMES
        assert tuple(reading.tension for reading in readings) == _readout_values(run)

        for reading in readings:
            millilitres = amounts.of(reading.quantity) * 1000.0
            assert reading.amount == _two_figures(millilitres), reading.name


def _two_figures(millilitres: float) -> str:
    """An amount written to two significant figures, never finer than 0.01 mL.

    It is written here apart from the formatter, from the rule in
    `docs/MODEL.md` § "Displayed precision".
    """

    if millilitres == 0.0:
        return "0 mL vapour"

    exponent = floor(log10(millilitres))
    decimals = min(2, 1 - exponent)
    rounded = round(millilitres, decimals)

    # Rounding can carry into the next decade, as 9.96 does to 10.
    if rounded >= 10.0 ** (exponent + 1):
        decimals = min(2, 1 - (exponent + 1))
        rounded = round(millilitres, decimals)

    if rounded == 0.0:
        return "<0.01 mL vapour"

    return f"{rounded:.{max(decimals, 0)}f} mL vapour"


def _advance(controller: SimulationController, seconds: float) -> None:
    for _ in range(round(seconds / SIMULATION_STEP_S)):
        controller.advance(SIMULATION_STEP_S)


def _advance_to(controller: SimulationController, elapsed_s: float) -> None:
    while controller.snapshot().elapsed_s < elapsed_s - SIMULATION_STEP_S / 2.0:
        controller.advance(SIMULATION_STEP_S)


def test_the_two_figure_helper_writes_what_the_specification_writes() -> None:
    """The test's own helper, checked against values written out by hand."""

    values = (0.0, 0.001, 0.0096, 0.034, 0.25, 1.0, 6.62, 9.96, 38.4, 104.0, 8750.0)

    assert [_two_figures(value) for value in values] == [
        "0 mL vapour",
        "<0.01 mL vapour",
        "0.01 mL vapour",
        "0.03 mL vapour",
        "0.25 mL vapour",
        "1.0 mL vapour",
        "6.6 mL vapour",
        "10 mL vapour",
        "38 mL vapour",
        "100 mL vapour",
        "8800 mL vapour",
    ]


def test_the_schematic_is_registered_and_offered_in_every_workspace() -> None:
    """The View chooser lists every registered kind, so registration is reachability."""

    entry = REGISTERED[COMPARTMENT_SCHEMATIC]

    assert COMPARTMENT_SCHEMATIC == "compartment_schematic"
    assert entry.factory is CompartmentSchematicView
    assert entry.title == "Compartment schematic"


def test_patient_inputs_reach_the_drawn_circuit_label_through_the_model(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """With no ventilation, the circuit follows F_D(1 - exp(-t FGF / V)) and holds V times that.

    The closed form is computed here, from the inputs and the circuit volume
    alone. The expected labels are written in this test's own format, so the
    View's formatter is not used to check itself.
    """

    dial_percent, flow_l_min, seconds = 4.0, 8.0, 30.0
    controller = SimulationController(agent_id="sevoflurane")
    controller.set_alveolar_ventilation(AlveolarVentilation(0.0))
    controller.set_fresh_gas_flow(FreshGasFlow(flow_l_min))
    controller.set_delivered_concentration_percent(Percent(dial_percent))
    controller.start()
    _advance(controller, seconds)
    controller.pause()
    view = _dashboard(application, shown, controller)
    volume_l = float(controller.snapshot().circuit_volume_l)
    percent = dial_percent * (1.0 - exp(-seconds * flow_l_min / SECONDS_PER_MINUTE / volume_l))
    millilitres = volume_l * percent / 100.0 * 1000.0
    circuit = _schematic(view).schematics[0].canvas.readings[0]
    axis_top_percent = 3 * load_agent_parameters("sevoflurane").mac_percent

    assert 100.0 <= millilitres < 1000.0
    assert circuit.name == "Circuit"
    assert circuit.tension == f"{percent:.2f}%"
    assert circuit.amount == f"{round(millilitres, -1):.0f} mL vapour"
    assert circuit.fill == pytest.approx(percent / axis_top_percent, rel=1e-6)
    assert ("Circuit", f"{percent:.2f}%") == _schematic(view).painted_strings()[:2]


def test_the_schematic_follows_its_run_through_a_reset_an_agent_change_and_a_comparison(
    application: QApplication, shown: list[SimulationView]
) -> None:
    trunk = SimulationController()
    trunk.start()
    _advance_to(trunk, 60.0)
    trunk.set_fresh_gas_flow(FreshGasFlow(2.0))
    trunk.pause()
    case = BranchedCase(trunk)
    view = _dashboard(application, shown, trunk, case)

    _assert_every_label_matches_its_run(view)
    assert _schematic(view).schematics[0].name_text.isHidden()

    # Every frame redraws the instant the run stands at.
    trunk.start()
    _advance(trunk, 30.0)
    trunk.pause()
    view.present(False)
    _assert_every_label_matches_its_run(view)

    # A branch opens a comparison: two schematics, each named.
    panel = view._fork_panel
    panel.point_selector.setCurrentIndex(panel.point_selector.findData(60.0))
    panel.take_button.click()
    _settle(application)
    view.present(False)

    assert len(view.runs) == 2
    _assert_every_label_matches_its_run(view)
    names = [schematic.name_text.text() for schematic in _schematic(view).schematics]
    assert names == ["Run 1", "Run 2"]

    # The branch moves on its own; each schematic shows its own run.
    branch = view.runs[1].controller
    branch.start()
    _advance(branch, 45.0)
    branch.pause()
    view.present(False)
    _assert_every_label_matches_its_run(view)
    first, second = (schematic.canvas.readings for schematic in _schematic(view).schematics)
    assert [reading.tension for reading in first] != [reading.tension for reading in second]

    # The trunk's Reset, once confirmed, ends the comparison: one schematic,
    # unnamed and empty.
    trunk_view = view.runs[TRUNK_RUN_INDEX]
    trunk_view._reset_button.click()
    dialog = trunk_view._reset_dialog
    assert dialog is not None
    dialog.discard_button.click()
    _settle(application)
    view.present(False)

    assert len(view.runs) == 1
    _assert_every_label_matches_its_run(view)
    assert _schematic(view).schematics[0].name_text.isHidden()
    assert {reading.amount for reading in _schematic(view).schematics[0].canvas.readings} == {
        "0 mL vapour"
    }

    # An agent change redraws against the new agent's scale.
    run = view.runs[TRUNK_RUN_INDEX]
    combo = run._agent_dropdown
    combo.setCurrentIndex(combo.findData("isoflurane"))
    _settle(application)
    run.controller.start()
    _advance(run.controller, 120.0)
    run.controller.pause()
    view.present(False)

    _assert_every_label_matches_its_run(view)
    isoflurane_top = 3 * load_agent_parameters("isoflurane").mac_percent
    assert f"0 to {isoflurane_top:g}% of 1 atm" in _schematic(view).schematics[0].scale_text.text()


def test_a_branch_taken_at_a_mark_behind_the_clock_draws_that_instant(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """A branch opened at a mark the trunk has passed shows its own earlier state, named."""

    trunk = SimulationController()
    trunk.start()
    _advance_to(trunk, 30.0)
    trunk.set_fresh_gas_flow(FreshGasFlow(2.0))
    _advance_to(trunk, 120.0)
    trunk.pause()
    case = BranchedCase(trunk)
    view = _dashboard(application, shown, trunk, case)
    trunk.add_time_bookmark(TimeBookmark(CaseInstant(75.05), "what if"))
    view.present(False)
    selector = view._fork_panel.point_selector
    selector.setCurrentIndex(selector.findText(f"{format_elapsed(751 * 0.1)}, on your mark"))
    view._fork_panel.take_button.click()
    _settle(application)
    view.present(False)

    assert len(view.runs) == 2
    assert view.runs[1].controller.snapshot().elapsed_s == pytest.approx(75.1)
    _assert_every_label_matches_its_run(view)
    trunk_readings, branch_readings = (
        schematic.canvas.readings for schematic in _schematic(view).schematics
    )
    assert trunk_readings[0].tension != branch_readings[0].tension or (
        trunk_readings[-1].amount != branch_readings[-1].amount
    )


def test_a_tension_above_the_scale_is_marked_and_named_in_words(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """An 8% sevoflurane dial puts the circuit at 4 MAC, above the 3 MAC top of the scale."""

    controller = SimulationController(agent_id="sevoflurane")
    controller.set_alveolar_ventilation(AlveolarVentilation(0.0))
    controller.set_fresh_gas_flow(FreshGasFlow(8.0))
    controller.set_delivered_concentration_percent(Percent(8.0))
    controller.start()
    _advance(controller, 10 * SECONDS_PER_MINUTE)
    controller.pause()
    view = _dashboard(application, shown, controller)
    schematic = _schematic(view).schematics[0]

    assert schematic.canvas.readings[0].off_scale
    assert not schematic.off_scale_text.isHidden()
    assert schematic.off_scale_text.text().startswith("Above the top of the scale: Circuit.")
