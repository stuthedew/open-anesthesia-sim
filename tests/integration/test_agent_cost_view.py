"""The agent cost View in a real dashboard, from patient inputs to its drawn amount.

`ROADMAP.md` § "v0.7.0 - the schematic", entry 8, specifies the View, and
`PL-B396` built it. These tests check four things. First, a run's inputs reach
the drawn amount through the model. The expected text is the dial times the
fresh gas flow times the time, divided by a vapour-to-liquid factor worked out
here from transcribed constants, not by the conversion under test. Second, the
reader's choice of unit reaches every agent cost View, is saved in the
preferences file, and survives a restart. Third, a failed save keeps the
choice for the session and says why it will not be kept. Fourth, the panel
follows its run through a Reset that no frame draws, an agent change and a
comparison, and never shows a state its run has left. The tests render under
the `offscreen` platform that `tests/conftest.py` selects, and every
preferences file is under `tmp_path`.
"""

import json
from collections.abc import Iterator
from datetime import date
from pathlib import Path
from typing import NoReturn

import pytest
from PySide6.QtCore import QDate, QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication

from anesthesia_sim.app import simulation_view as simulation_view_module
from anesthesia_sim.app.agent_cost import NO_PRICE_TEXT
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import (
    INTERPRETATION_DISCLAIMER_TEXT,
    SIMULATION_STEP_S,
    TRUNK_RUN_INDEX,
)
from anesthesia_sim.app.formatting import AgentAmountUnit
from anesthesia_sim.app.main import open_dashboard, open_preferences
from anesthesia_sim.app.preferences import PREFERENCES_FILE_NAME, AgentPrice, PreferencesStore
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.view_registry import AGENT_COST, REGISTERED
from anesthesia_sim.app.views import AgentCostView
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.supported_ranges import FreshGasFlow
from anesthesia_sim.layout.model import LayoutModel
from anesthesia_sim.layout.serialization import workspace_set_to_json
from anesthesia_sim.layout.store import USER_DIRECTORY_VARIABLE, WORKSPACES_FILE_NAME
from anesthesia_sim.layout.tree import Area, AreaId, Node, Orientation, Split, Window
from anesthesia_sim.layout.workspace import Origin, Workspace, WorkspaceName, WorkspaceSet

#: Each agent's liquid density at 20 °C in g/mL and molar mass in g/mol,
#: transcribed from `docs/MODEL.md` § "Agent amount", the table under "Why
#: 20 °C". The densities are Laster, Fang and Eger's.
_DENSITY_AND_MOLAR_MASS = {
    "sevoflurane": (1.5203, 200.05),
    "isoflurane": (1.5019, 184.49),
    "desflurane": (1.4651, 168.04),
}

#: The ideal-gas molar volume at 20 °C and one standard atmosphere, in mL/mol,
#: from R = 8.314462618 J/(mol K) (CODATA 2022).
_MOLAR_VOLUME_ML = 8.314462618 * 293.15 / 101_325.0 * 1.0e6

_SECONDS_PER_MINUTE = 60.0
_WINDOW_WIDTH_PX = 1400
_WINDOW_HEIGHT_PX = 1000


def _workspaces(*areas: Area) -> WorkspaceSet:
    """One Workspace whose Areas show `areas`, side by side when there are two."""

    root: Node = (
        areas[0]
        if len(areas) == 1
        else Split(Orientation.ROW, tuple(1.0 / len(areas) for _ in areas), areas)
    )

    return WorkspaceSet(
        (
            Workspace(
                WorkspaceName("Cost"),
                Origin.mine(),
                LayoutModel((Window(root),), AreaId(len(areas) + 1)),
            ),
        ),
        0,
    )


_COST_ONLY = _workspaces(Area(AreaId(1), AGENT_COST))
_TWO_COST_VIEWS = _workspaces(Area(AreaId(1), AGENT_COST), Area(AreaId(2), AGENT_COST))


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
    *,
    case: BranchedCase | None = None,
    workspaces: WorkspaceSet = _COST_ONLY,
    directory: Path | None = None,
) -> SimulationView:
    """A dashboard presented once, as `main()` opens one, with preferences from `directory`."""

    if directory is None:
        view = SimulationView((controller,), case=case, workspaces=workspaces)
    else:
        # The launch path `main()` takes, over a data directory that already
        # holds these Workspaces, so the wiring that saves a choice is tested.
        directory.mkdir(parents=True, exist_ok=True)
        (directory / WORKSPACES_FILE_NAME).write_text(
            workspace_set_to_json(workspaces), encoding="utf-8"
        )
        view = open_dashboard(
            BranchedCase(controller) if case is None else case,
            "",
            {USER_DIRECTORY_VARIABLE: str(directory)},
        )

    shown.append(view)
    view.resize(_WINDOW_WIDTH_PX, _WINDOW_HEIGHT_PX)
    view.show()
    application.processEvents()
    view.present(False)

    return view


def _settle(application: QApplication) -> None:
    application.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    application.processEvents()


def _cost_views(view: SimulationView) -> tuple[AgentCostView, ...]:
    return tuple(v for v in view.layout_container.views() if isinstance(v, AgentCostView))


def _advance(controller: SimulationController, seconds: float) -> None:
    for _ in range(round(seconds / SIMULATION_STEP_S)):
        controller.advance(SIMULATION_STEP_S)


def _liquid_ml(agent_id: str, vapour_l: float) -> float:
    density_g_ml, molar_mass_g_mol = _DENSITY_AND_MOLAR_MASS[agent_id]

    return vapour_l * 1000.0 / (density_g_ml / molar_mass_g_mol * _MOLAR_VOLUME_ML)


def _pick(cost_view: AgentCostView, unit: AgentAmountUnit) -> None:
    """Pick `unit` in the selector, as a reader does."""

    index = cost_view.unit_selector.findData(unit)
    cost_view.unit_selector.setCurrentIndex(index)
    cost_view.unit_selector.activated.emit(index)


def test_the_view_is_registered_under_its_kind() -> None:
    """The View chooser lists every registered kind, so registration is reachability."""

    entry = REGISTERED[AGENT_COST]

    assert AGENT_COST == "agent_cost"
    assert entry.factory is AgentCostView
    assert entry.title == "Agent cost"


def test_patient_inputs_reach_the_drawn_liquid_figure_through_the_model(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """Isoflurane at 1.5 % and 2 L/min for 40 min delivers 1.2 L of vapour, or 6 mL of liquid.

    The expected text is worked out here, from the inputs and the transcribed
    constants, and written in this test's own format.
    """

    dial_percent, flow_l_min, minutes = 1.5, 2.0, 40.0
    controller = SimulationController(agent_id="isoflurane")
    controller.set_fresh_gas_flow(FreshGasFlow(flow_l_min))
    controller.set_delivered_concentration_percent(Percent(dial_percent))
    controller.start()
    _advance(controller, minutes * _SECONDS_PER_MINUTE)
    controller.pause()
    view = _dashboard(application, shown, controller)
    vapour_l = dial_percent / 100.0 * flow_l_min * minutes
    (cost_view,) = _cost_views(view)
    (panel,) = cost_view.panels

    assert vapour_l == pytest.approx(1.2)
    assert panel.amount_text.text() == f"{_liquid_ml('isoflurane', vapour_l):.0f} mL of liquid"
    assert panel.amount_text.text() == "6 mL of liquid"
    assert panel.label_text.text() == "Isoflurane delivered"
    assert panel.caption_text.text().startswith("Liquid used by the vaporizer")
    assert panel.name_text.text() == "At 40m of simulated time"
    assert cost_view.unit_selector.currentData() is AgentAmountUnit.MILLILITRES_OF_LIQUID
    assert INTERPRETATION_DISCLAIMER_TEXT in {
        label.text() for label in cost_view.findChildren(type(panel.amount_text))
    }
    assert cost_view.preferences_notice.isHidden()


def test_a_unit_picked_in_one_view_reaches_every_view_and_survives_a_restart(
    application: QApplication, shown: list[SimulationView], tmp_path: Path
) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 10 * _SECONDS_PER_MINUTE)
    controller.pause()
    view = _dashboard(
        application, shown, controller, workspaces=_TWO_COST_VIEWS, directory=tmp_path
    )
    first, second = _cost_views(view)

    assert not (tmp_path / PREFERENCES_FILE_NAME).exists()

    _pick(first, AgentAmountUnit.LITRES_OF_VAPOUR)

    vapour_l = 2.0 / 100.0 * 4.0 * 10.0
    for cost_view in (first, second):
        assert cost_view.unit_selector.currentData() is AgentAmountUnit.LITRES_OF_VAPOUR
        assert cost_view.panels[0].amount_text.text() == f"{vapour_l:.1f} L vapour"
        assert cost_view.panels[0].caption_text.text().startswith("Vapour put out by the vaporizer")

    saved = json.loads((tmp_path / PREFERENCES_FILE_NAME).read_text(encoding="utf-8"))
    assert saved["agent_cost_unit"] == AgentAmountUnit.LITRES_OF_VAPOUR.value

    # A restart: a new dashboard loads the file the first one saved.
    restarted = _dashboard(application, shown, SimulationController(), directory=tmp_path)
    (cost_view,) = _cost_views(restarted)

    assert cost_view.unit_selector.currentData() is AgentAmountUnit.LITRES_OF_VAPOUR
    assert cost_view.panels[0].amount_text.text() == "0.0 L vapour"


def test_a_choice_that_cannot_be_saved_lasts_the_session_and_says_so(
    application: QApplication, shown: list[SimulationView], tmp_path: Path
) -> None:
    """A preferences file from a newer build turns saving off, and the View says so."""

    path = tmp_path / PREFERENCES_FILE_NAME
    newer = json.dumps({"schema_version": 99})
    path.write_text(newer, encoding="utf-8")
    view = _dashboard(application, shown, SimulationController(), directory=tmp_path)
    (cost_view,) = _cost_views(view)

    assert not cost_view.preferences_notice.isHidden()
    assert "newer build" in cost_view.preferences_notice.text()

    _pick(cost_view, AgentAmountUnit.LITRES_OF_VAPOUR)

    assert cost_view.panels[0].amount_text.text() == "0.0 L vapour"
    assert cost_view.preferences_notice.text().startswith(
        "This change lasts only until the application closes"
    )
    assert path.read_text(encoding="utf-8") == newer


def test_a_saved_unit_the_build_refuses_falls_back_to_liquid_with_a_notice(
    application: QApplication, shown: list[SimulationView], tmp_path: Path
) -> None:
    """The refused unit's notice goes once the reader picks a unit and it is saved."""

    path = tmp_path / PREFERENCES_FILE_NAME
    path.write_text(
        json.dumps({"schema_version": 1, "agent_cost_unit": "furlongs", "agent_prices": []}),
        encoding="utf-8",
    )
    view = _dashboard(application, shown, SimulationController(), directory=tmp_path)
    (cost_view,) = _cost_views(view)

    assert cost_view.unit_selector.currentData() is AgentAmountUnit.MILLILITRES_OF_LIQUID
    assert "furlongs" in cost_view.preferences_notice.text()

    _pick(cost_view, AgentAmountUnit.MILLILITRES_OF_LIQUID)

    assert cost_view.preferences_notice.isHidden()
    assert PreferencesStore(tmp_path).load().preferences.refused_unit is None


_REFUSED_PRICE = {
    "agent": "sevoflurane",
    "bottle_price": 0,
    "bottle_volume_ml": 250,
    "currency": "USD",
    "applies_on": "2008-03-05",
}


def test_a_refused_price_s_notice_stays_after_a_unit_is_picked_and_saved(
    application: QApplication, shown: list[SimulationView], tmp_path: Path
) -> None:
    """Picking a unit replaces no price, so the notice of the refused price still applies."""

    (tmp_path / PREFERENCES_FILE_NAME).write_text(
        json.dumps(
            {
                "schema_version": 1,
                "agent_cost_unit": "millilitres of liquid",
                "agent_prices": [_REFUSED_PRICE],
            }
        ),
        encoding="utf-8",
    )
    view = _dashboard(application, shown, SimulationController(), directory=tmp_path)
    (cost_view,) = _cost_views(view)
    before = cost_view.preferences_notice.text()

    _pick(cost_view, AgentAmountUnit.LITRES_OF_VAPOUR)

    assert "agent_prices[0]" in before
    assert cost_view.preferences_notice.text() == before
    assert not cost_view.preferences_notice.isHidden()


def test_a_failed_save_says_so_and_still_names_the_refused_price(
    application: QApplication, shown: list[SimulationView], tmp_path: Path
) -> None:
    """A directory where the save's temporary file belongs makes the save fail."""

    (tmp_path / PREFERENCES_FILE_NAME).write_text(
        json.dumps(
            {
                "schema_version": 1,
                "agent_cost_unit": "millilitres of liquid",
                "agent_prices": [_REFUSED_PRICE],
            }
        ),
        encoding="utf-8",
    )
    blocker = tmp_path / f"{PREFERENCES_FILE_NAME}.tmp"
    blocker.mkdir()
    (blocker / "keep").write_text("", encoding="utf-8")
    view = _dashboard(application, shown, SimulationController(), directory=tmp_path)
    (cost_view,) = _cost_views(view)

    _pick(cost_view, AgentAmountUnit.LITRES_OF_VAPOUR)

    notice = cost_view.preferences_notice.text()
    assert cost_view.panels[0].amount_text.text() == "0.0 L vapour"
    assert notice.startswith("This change lasts only until the application closes")
    assert "agent_prices[0]" in notice


def test_while_every_frame_fails_a_pick_leaves_the_selector_on_the_unit_drawn(
    application: QApplication, shown: list[SimulationView], monkeypatch: pytest.MonkeyPatch
) -> None:
    """The selector never names a unit that no value on screen is shown in.

    The blind and adversarial reviews of `PL-B396` both found the selector
    showing litres of vapour while the panels still showed millilitres of
    liquid, after a pick made while frames were failing. Once a frame draws
    again, every View shows the pick.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 5 * _SECONDS_PER_MINUTE)
    controller.pause()
    view = _dashboard(application, shown, controller, workspaces=_TWO_COST_VIEWS)
    first, second = _cost_views(view)
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    _pick(first, AgentAmountUnit.LITRES_OF_VAPOUR)

    for cost_view in (first, second):
        assert cost_view.unit_selector.currentData() is AgentAmountUnit.MILLILITRES_OF_LIQUID
        assert cost_view.panels[0].amount_text.text() == "2 mL of liquid"

    monkeypatch.undo()
    view.present(False)

    for cost_view in (first, second):
        assert cost_view.unit_selector.currentData() is AgentAmountUnit.LITRES_OF_VAPOUR
        assert cost_view.panels[0].amount_text.text() == "0.4 L vapour"


def test_a_mouse_wheel_over_the_selector_changes_nothing_until_it_has_focus(
    application: QApplication, shown: list[SimulationView]
) -> None:
    view = _dashboard(application, shown, SimulationController())
    (cost_view,) = _cost_views(view)
    selector = cost_view.unit_selector
    centre = QPointF(selector.rect().center())
    wheel = QWheelEvent(
        centre,
        selector.mapToGlobal(centre),
        QPoint(0, -120),
        QPoint(0, -120),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.NoScrollPhase,
        False,
    )

    QApplication.sendEvent(selector, wheel)

    assert selector.focusPolicy() == Qt.FocusPolicy.StrongFocus
    assert selector.currentData() is AgentAmountUnit.MILLILITRES_OF_LIQUID
    assert cost_view.panels[0].amount_text.text() == "0 mL of liquid"


def test_a_session_with_no_data_directory_keeps_no_choice_and_says_so() -> None:
    launch = open_preferences("", {})

    assert launch.store is None
    assert launch.loaded.writable is False
    assert launch.loaded.notice is not None
    assert launch.loaded.notice.endswith("No change of preference will be kept after this session")


def _failing_assembly(*args: object, **kwargs: object) -> NoReturn:
    """Stand in for `assemble_chart_frame` where every frame must fail."""

    del args, kwargs
    raise RuntimeError("this frame could not be assembled")


def test_a_reset_that_no_frame_draws_withholds_the_delivered_agent_with_the_readouts(
    application: QApplication, shown: list[SimulationView], monkeypatch: pytest.MonkeyPatch
) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 5 * _SECONDS_PER_MINUTE)
    controller.pause()
    view = _dashboard(application, shown, controller)
    (cost_view,) = _cost_views(view)

    _enter_price(cost_view, "sevoflurane", "240.34", "250", "USD", date(2008, 3, 5))

    assert cost_view.panels[0].amount_text.text() == "2 mL of liquid"
    assert cost_view.panels[0].cost_text.text().startswith("USD ")

    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    run = view.runs[0]
    run._reset_button.click()
    dialog = run._reset_dialog

    if dialog is not None:
        dialog.discard_button.click()

    _settle(application)
    view.present(False)

    panel = cost_view.panels[0]
    assert run.controller.has_failed is True
    assert panel.amount_text.text() == "— mL of liquid"
    assert panel.label_text.text() == "Agent delivered"
    assert panel.name_text.text() == "At — of simulated time"
    assert panel.cost_text.text() == "—"
    assert panel.working_text.isHidden()
    assert "sevoflurane" not in panel.cost_label_text.text()


def test_the_panel_follows_its_run_through_an_agent_change_and_a_comparison(
    application: QApplication, shown: list[SimulationView]
) -> None:
    # The flow change at 1 min is the instant the branch is taken at.
    trunk = SimulationController()
    trunk.start()
    _advance(trunk, _SECONDS_PER_MINUTE)
    trunk.set_fresh_gas_flow(FreshGasFlow(2.0))
    _advance(trunk, _SECONDS_PER_MINUTE)
    trunk.pause()
    case = BranchedCase(trunk)
    view = _dashboard(application, shown, trunk, case=case)
    (cost_view,) = _cost_views(view)

    # A branch at 1 min opens a comparison: two panels, each named and each
    # showing its own run's delivered agent.
    panel = view._fork_panel
    panel.point_selector.setCurrentIndex(panel.point_selector.findData(60.0))
    panel.take_button.click()
    _settle(application)
    branch = view.runs[1].controller
    branch.set_fresh_gas_flow(FreshGasFlow(4.0))
    branch.set_delivered_concentration_percent(Percent(8.0))
    branch.start()
    _advance(branch, 3 * _SECONDS_PER_MINUTE)
    branch.pause()
    view.present(False)

    assert len(view.runs) == 2
    first, second = cost_view.panels
    trunk_ml = _liquid_ml("sevoflurane", 0.02 * 4.0 * 1.0 + 0.02 * 2.0 * 1.0)
    branch_ml = _liquid_ml("sevoflurane", 0.02 * 4.0 * 1.0 + 0.08 * 4.0 * 3.0)
    assert first.name_text.text().startswith("Run 1, at ")
    assert second.name_text.text().startswith("Run 2, at ")
    assert first.amount_text.text() == f"{trunk_ml:.0f} mL of liquid"
    assert second.amount_text.text() == f"{branch_ml:.0f} mL of liquid"

    # The trunk's Reset ends the comparison, then an agent change and a run of
    # 5 min convert with desflurane's own factor.
    trunk_view = view.runs[TRUNK_RUN_INDEX]
    trunk_view._reset_button.click()
    dialog = trunk_view._reset_dialog
    assert dialog is not None
    dialog.discard_button.click()
    _settle(application)
    run = view.runs[TRUNK_RUN_INDEX]
    combo = run._agent_dropdown
    combo.setCurrentIndex(combo.findData("desflurane"))
    _settle(application)
    dial_percent = float(run.controller.snapshot().delivered_concentration_percent)
    run.controller.start()
    _advance(run.controller, 5 * _SECONDS_PER_MINUTE)
    run.controller.pause()
    view.present(False)

    (alone,) = cost_view.panels
    flow_l_min = float(run.controller.snapshot().fresh_gas_flow_l_min)
    desflurane_ml = _liquid_ml("desflurane", dial_percent / 100.0 * flow_l_min * 5.0)
    assert alone.label_text.text() == "Desflurane delivered"
    assert alone.amount_text.text() == f"{desflurane_ml:.0f} mL of liquid"
    assert alone.name_text.text() == "At 5m of simulated time"


def _enter_price(
    cost_view: AgentCostView,
    agent_id: str,
    bottle_price: str,
    bottle_volume_ml: str,
    currency: str,
    applies_on: date,
) -> None:
    """Fill the price form for `agent_id` and press Set price, as a reader does."""

    entry = cost_view.price_entry
    index = entry.agent_selector.findData(agent_id)
    entry.agent_selector.setCurrentIndex(index)
    entry.agent_selector.activated.emit(index)
    entry.bottle_price_edit.setText(bottle_price)
    entry.bottle_volume_edit.setText(bottle_volume_ml)
    entry.currency_edit.setText(currency)
    entry.applies_on_edit.setDate(QDate(applies_on.year, applies_on.month, applies_on.day))
    entry.set_button.click()


def _cost_line(cost_view: AgentCostView) -> str:
    (panel,) = cost_view.panels

    return panel.cost_text.text()


def test_no_cost_is_shown_before_the_reader_sets_a_price(
    application: QApplication, shown: list[SimulationView]
) -> None:
    controller = SimulationController(agent_id="isoflurane")
    controller.start()
    _advance(controller, 5 * _SECONDS_PER_MINUTE)
    controller.pause()
    view = _dashboard(application, shown, controller)
    (cost_view,) = _cost_views(view)
    (panel,) = cost_view.panels

    assert panel.cost_text.text() == NO_PRICE_TEXT.format(agent="isoflurane")
    assert panel.working_text.isHidden()
    assert panel.price_text.isHidden()
    assert cost_view.price_entry.agent_id == "isoflurane"
    assert cost_view.price_entry.bottle_price_edit.text() == ""
    assert not cost_view.price_entry.remove_button.isEnabled()


@pytest.mark.parametrize(
    ("flow_l_min", "first_percent", "second_percent", "printed_at_13_min", "printed_at_60_min"),
    [
        # Exercise 14-1, printed pp. 133-134: 2 % at 8 L/min to 13 min, then 1.5 %.
        pytest.param(8.0, 2.0, 1.5, 2.17, 8.06, id="exercise 14-1"),
        # Exercise 14-2, printed pp. 135-136: 5 % at 1 L/min to 13 min, then 2.7 %.
        pytest.param(1.0, 5.0, 2.7, 0.68, 2.00, id="exercise 14-2"),
    ],
)
def test_the_displayed_cost_reproduces_gas_man_s_printed_costs(
    application: QApplication,
    shown: list[SimulationView],
    tmp_path: Path,
    flow_l_min: float,
    first_percent: float,
    second_percent: float,
    printed_at_13_min: float,
    printed_at_60_min: float,
) -> None:
    """The project owner's sanity check on a calculated price, end to end (`PL-1P15`).

    The project owner asked on 2026-10-26 for "a sanity check for calculated
    agent price". The reader enters Gas Man's isoflurane price, US$20.47 for a
    100 mL bottle (Philip JH, *Workbook for Gas Man*, Appendix C, printed
    p. 171), in the View's form. The run uses the exercise's flow and dial
    settings, and the test follows it from the patient inputs through the
    model to the drawn text.
    Gas Man rounds isoflurane's vapour-to-liquid ratio to 196, which can move
    a cost by 0.26 %. Both the book and the readout also round to the cent.
    So the drawn cost may differ from the printed one by a cent's rounding on
    each side plus 0.26 %. The test also works out the liquid volume itself,
    multiplies it by the price per millilitre, and checks the drawn cost
    against that product.
    """

    controller = SimulationController(agent_id="isoflurane")
    controller.set_fresh_gas_flow(FreshGasFlow(flow_l_min))
    controller.set_delivered_concentration_percent(Percent(first_percent))
    view = _dashboard(application, shown, controller, directory=tmp_path)
    (cost_view,) = _cost_views(view)
    _enter_price(cost_view, "isoflurane", "20.47", "100", "USD", date(2008, 3, 5))
    usd_per_ml = 20.47 / 100.0

    def drawn_usd() -> float:
        text = _cost_line(cost_view)
        assert text.startswith("USD ")
        return float(text.removeprefix("USD "))

    def allowed(printed: float) -> float:
        return 0.005 + 0.005 + printed * 0.5 / 196.0

    controller.start()
    _advance(controller, 13 * _SECONDS_PER_MINUTE)
    view.present(False)
    liquid_at_13_ml = _liquid_ml("isoflurane", first_percent / 100.0 * flow_l_min * 13.0)

    assert abs(drawn_usd() - printed_at_13_min) <= allowed(printed_at_13_min)
    assert _cost_line(cost_view) == f"USD {liquid_at_13_ml * usd_per_ml:.2f}"

    controller.set_delivered_concentration_percent(Percent(second_percent))
    _advance(controller, 47 * _SECONDS_PER_MINUTE)
    controller.pause()
    view.present(False)
    vapour_l = (first_percent * 13.0 + second_percent * 47.0) / 100.0 * flow_l_min
    liquid_ml = _liquid_ml("isoflurane", vapour_l)
    (panel,) = cost_view.panels

    assert abs(drawn_usd() - printed_at_60_min) <= allowed(printed_at_60_min)
    assert _cost_line(cost_view) == f"USD {liquid_ml * usd_per_ml:.2f}"
    assert panel.working_text.text() == (
        f"{liquid_ml:.0f} mL of liquid x USD 0.2047 per mL of liquid"
    )
    assert (
        panel.price_text.text() == "Your price: USD 20.47 for 100 mL of liquid, as of 2008-03-05."
    )
    assert not panel.rounded_text.isHidden()


def test_a_price_change_redraws_the_cost_at_once_while_paused_and_survives_a_restart(
    application: QApplication, shown: list[SimulationView], tmp_path: Path
) -> None:
    controller = SimulationController(agent_id="isoflurane")
    controller.set_fresh_gas_flow(FreshGasFlow(8.0))
    controller.set_delivered_concentration_percent(Percent(2.0))
    controller.start()
    _advance(controller, 13 * _SECONDS_PER_MINUTE)
    controller.pause()
    view = _dashboard(application, shown, controller, directory=tmp_path)
    (cost_view,) = _cost_views(view)
    liquid_ml = _liquid_ml("isoflurane", 0.02 * 8.0 * 13.0)

    _enter_price(cost_view, "isoflurane", "20.47", "100", "USD", date(2008, 3, 5))

    assert _cost_line(cost_view) == f"USD {liquid_ml * 0.2047:.2f}"

    _enter_price(cost_view, "isoflurane", "78", "100", "USD", date(2008, 3, 5))

    assert _cost_line(cost_view) == f"USD {liquid_ml * 0.78:.2f}"
    assert PreferencesStore(tmp_path).load().preferences.price_for("isoflurane") == AgentPrice(
        "isoflurane", 78.0, 100.0, "USD", date(2008, 3, 5)
    )

    restarted = _dashboard(application, shown, controller, directory=tmp_path)
    (cost_view,) = _cost_views(restarted)

    assert _cost_line(cost_view) == f"USD {liquid_ml * 0.78:.2f}"
    assert cost_view.price_entry.bottle_price_edit.text() == "78"
    assert cost_view.price_entry.bottle_volume_edit.text() == "100"
    assert cost_view.price_entry.currency_edit.text() == "USD"
    assert cost_view.price_entry.applies_on_edit.date() == QDate(2008, 3, 5)


def test_a_refused_entry_changes_nothing_and_says_why(
    application: QApplication, shown: list[SimulationView], tmp_path: Path
) -> None:
    """A bottle price typed with a decimal comma is refused, and the earlier price stays."""

    controller = SimulationController(agent_id="isoflurane")
    controller.start()
    _advance(controller, 5 * _SECONDS_PER_MINUTE)
    controller.pause()
    view = _dashboard(application, shown, controller, directory=tmp_path)
    (cost_view,) = _cost_views(view)
    _enter_price(cost_view, "isoflurane", "20.47", "100", "USD", date(2008, 3, 5))
    before = _cost_line(cost_view)

    _enter_price(cost_view, "isoflurane", "20,47", "100", "USD", date(2008, 3, 5))

    assert _cost_line(cost_view) == before
    assert before.startswith("USD ")
    assert not cost_view.price_entry.refusal.isHidden()
    assert cost_view.price_entry.refusal.text().startswith("Price not set: ")
    assert "20,47" in cost_view.price_entry.refusal.text()
    assert PreferencesStore(tmp_path).load().preferences.price_for("isoflurane") == AgentPrice(
        "isoflurane", 20.47, 100.0, "USD", date(2008, 3, 5)
    )


def test_removing_the_price_shows_no_cost_again(
    application: QApplication, shown: list[SimulationView], tmp_path: Path
) -> None:
    controller = SimulationController(agent_id="isoflurane")
    view = _dashboard(application, shown, controller, directory=tmp_path)
    (cost_view,) = _cost_views(view)
    _enter_price(cost_view, "isoflurane", "20.47", "100", "USD", date(2008, 3, 5))

    assert cost_view.price_entry.remove_button.isEnabled()

    cost_view.price_entry.remove_button.click()

    assert _cost_line(cost_view) == NO_PRICE_TEXT.format(agent="isoflurane")
    assert cost_view.price_entry.bottle_price_edit.text() == ""
    assert PreferencesStore(tmp_path).load().preferences.price_for("isoflurane") is None


def test_the_cost_s_working_stays_in_liquid_when_the_amounts_are_shown_in_vapour(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """The liquid figure the cost multiplies stays on screen in either unit (item 1)."""

    controller = SimulationController(agent_id="isoflurane")
    controller.set_fresh_gas_flow(FreshGasFlow(8.0))
    controller.set_delivered_concentration_percent(Percent(2.0))
    controller.start()
    _advance(controller, 13 * _SECONDS_PER_MINUTE)
    controller.pause()
    view = _dashboard(application, shown, controller)
    (cost_view,) = _cost_views(view)
    _enter_price(cost_view, "isoflurane", "20.47", "100", "USD", date(2008, 3, 5))

    _pick(cost_view, AgentAmountUnit.LITRES_OF_VAPOUR)

    (panel,) = cost_view.panels
    assert panel.amount_text.text() == "2.1 L vapour"
    assert panel.working_text.text().startswith(
        f"{_liquid_ml('isoflurane', 2.08):.0f} mL of liquid x"
    )


def test_a_refused_price_for_the_first_run_s_agent_can_be_removed_from_the_first_frame(
    application: QApplication, shown: list[SimulationView], tmp_path: Path
) -> None:
    """Remove is offered for a refused entry at launch, and withdrawn once it is gone.

    Blind review pass 2 of `PL-1P15` found that Remove was not offered at
    launch. The form refilled only when the stored price changed, and there is
    no stored price whether or not a refused entry is in the file.
    """

    (tmp_path / PREFERENCES_FILE_NAME).write_text(
        json.dumps(
            {
                "schema_version": 1,
                "agent_cost_unit": "millilitres of liquid",
                "agent_prices": [_REFUSED_PRICE],
            }
        ),
        encoding="utf-8",
    )
    view = _dashboard(application, shown, SimulationController(), directory=tmp_path)
    (cost_view,) = _cost_views(view)
    entry = cost_view.price_entry

    assert entry.agent_id == "sevoflurane"
    assert entry.remove_button.isEnabled()

    entry.remove_button.click()

    assert not entry.remove_button.isEnabled()
    assert cost_view.preferences_notice.isHidden()
    assert _cost_line(cost_view) == NO_PRICE_TEXT.format(agent="sevoflurane")
    assert PreferencesStore(tmp_path).load().preferences.refused_prices == ()
