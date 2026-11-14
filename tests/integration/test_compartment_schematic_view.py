"""The compartment schematic View in a real dashboard, from patient inputs to its drawn labels.

`docs/MODEL.md` § "The compartment schematic: what its heights, amounts and
share bar assert" is the specification (`PL-2881`), and `PL-RNYV` built the
View. These tests check two things. First, they check that a run's inputs reach
the drawn labels through the model. The expected labels come from a closed form
that is computed apart from the code under test. Second, they check the labels
after each action by a learner that changes which state a run is in. The
actions are a reset, an agent change, a branch, a branch taken at a mark behind
the clock, and opening and closing a comparison. After each one, every label
matches the run's state at that moment, and each schematic is named the same
way as the run's own panel. The tests render under the `offscreen` platform
that `tests/conftest.py` selects.
"""

from collections.abc import Iterator
from math import exp, floor, log10
from typing import NoReturn

import pytest
from PySide6.QtCore import QEvent
from PySide6.QtGui import QColor, QImage
from PySide6.QtWidgets import QApplication, QLabel

from anesthesia_sim.app import simulation_view as simulation_view_module
from anesthesia_sim.app.bookmarks import TimeBookmark
from anesthesia_sim.app.chart_frame import trace_style
from anesthesia_sim.app.compartment_schematic import NO_AGENT_SHARE_LINE, WITHHELD_AMOUNT_TEXT
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import (
    SIMULATION_STEP_S,
    TRUNK_RUN_INDEX,
    WITHHELD_CONCENTRATION_TEXT,
)
from anesthesia_sim.app.formatting import format_elapsed
from anesthesia_sim.app.qt_schematic import RunSchematic, SchematicCanvas
from anesthesia_sim.app.qt_widgets import ForkPanel
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES
from anesthesia_sim.app.run_view import RunView
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.theme import MUTED, PANEL, WARNING
from anesthesia_sim.app.view_registry import BRANCH, COMPARTMENT_SCHEMATIC, REGISTERED
from anesthesia_sim.app.views import BranchView, CompartmentSchematicView, ConcentrationView
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.parameters import load_agent_parameters
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CaseInstant, FreshGasFlow
from anesthesia_sim.layout.model import LayoutModel
from anesthesia_sim.layout.shipped import shipped_workspaces
from anesthesia_sim.layout.tree import Area, AreaId, Orientation, Split, Window
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

#: The schematic beside the branch control, for a test that opens a branch.
_SCHEMATIC_AND_BRANCH = WorkspaceSet(
    (
        Workspace(
            WorkspaceName("Schematic and branch"),
            Origin.mine(),
            LayoutModel(
                (
                    Window(
                        Split(
                            Orientation.ROW,
                            (0.7, 0.3),
                            (Area(AreaId(1), COMPARTMENT_SCHEMATIC), Area(AreaId(2), BRANCH)),
                        )
                    ),
                ),
                AreaId(3),
            ),
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
    workspaces: WorkspaceSet = _SCHEMATIC_ONLY,
) -> SimulationView:
    """A dashboard showing only the schematic, presented once, as `main()` opens one."""

    view = SimulationView((controller,), case=case, workspaces=workspaces)
    shown.append(view)
    view.resize(_WINDOW_WIDTH_PX, _WINDOW_HEIGHT_PX)
    view.show()
    application.processEvents()
    view.present(False)

    return view


def _settle(application: QApplication) -> None:
    application.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    application.processEvents()


def _branch_control(view: SimulationView) -> ForkPanel:
    """The branch control in the one Area that shows it."""

    (branch,) = (v for v in view.layout_container.views() if isinstance(v, BranchView))
    assert branch.panel is not None

    return branch.panel


def _schematic(view: SimulationView) -> CompartmentSchematicView:
    return next(v for v in view.layout_container.views() if isinstance(v, CompartmentSchematicView))


def _readout_values(run: RunView) -> tuple[str, ...]:
    """The tension each compartment's readout prints now, in the readout row's order."""

    return tuple(panel.value_label.text() for panel in run._readout_row.panels[1:])


def _assert_every_label_matches_its_run(view: SimulationView) -> None:
    """Check that each run has one schematic, and that its name and labels match the run now.

    Each schematic is named as its run's panel is named. A tension is checked
    against the run's own readout, which is written from the same snapshot by a
    different path. An amount is checked against the run's controller, read at
    this moment, in millilitres to two significant figures. So the check fails
    for a schematic that still shows a state its run has left.
    """

    schematics = _schematic(view).schematics

    assert len(schematics) == len(view.runs)

    for schematic, run in zip(schematics, view.runs, strict=True):
        panel_name = None if run._run_name_text.isHidden() else run._run_name_text.text()
        clock = run._readout_row.panels[0].value_label.text()
        instant = f"{clock} of simulated time"

        assert schematic.name_text.text() == (
            f"At {instant}" if panel_name is None else f"{panel_name}, at {instant}"
        )

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
    """With no ventilation, the circuit's agent fraction follows F_D(1 - exp(-t FGF / V)).

    The circuit's amount is V times that fraction. The closed form is computed
    here, from the inputs and the circuit volume alone. The expected labels are
    written in this test's own format, so the View's formatter is not used to
    check itself.
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
    view = _dashboard(application, shown, trunk, case, _SCHEMATIC_AND_BRANCH)

    _assert_every_label_matches_its_run(view)
    assert _schematic(view).schematics[0].name_text.text().startswith("At ")

    # Every frame redraws the instant the run stands at.
    trunk.start()
    _advance(trunk, 30.0)
    trunk.pause()
    view.present(False)
    _assert_every_label_matches_its_run(view)

    # A branch opens a comparison: two schematics, each named.
    panel = _branch_control(view)
    panel.point_selector.setCurrentIndex(panel.point_selector.findData(60.0))
    panel.take_button.click()
    _settle(application)
    view.present(False)

    assert len(view.runs) == 2
    _assert_every_label_matches_its_run(view)
    names = [schematic.name_text.text() for schematic in _schematic(view).schematics]
    assert [name.split(",")[0] for name in names] == ["Run 1", "Run 2"]

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
    assert _schematic(view).schematics[0].name_text.text() == "At 0s of simulated time"
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
    schematic = _schematic(view).schematics[0]
    assert f"0 to {isoflurane_top:g}% of 1 atm" in schematic.scale_text.text()

    # Each fill must be measured against isoflurane's scale, not sevoflurane's.
    # The expected tensions come from the snapshot's own fields, in the readout
    # row's order, rather than through the lookup that the schematic uses.
    snapshot = run.controller.snapshot()
    fractions = (
        snapshot.inspired_partial_pressure_fraction,
        snapshot.alveolar_partial_pressure_fraction,
        snapshot.mixed_venous_partial_pressure_fraction,
        snapshot.vessel_rich_partial_pressure_fraction,
        snapshot.muscle_partial_pressure_fraction,
        snapshot.fat_partial_pressure_fraction,
    )
    for reading, fraction in zip(schematic.canvas.readings, fractions, strict=True):
        percent = float(fraction) * 100.0
        assert reading.fill == pytest.approx(percent / isoflurane_top, rel=1e-9), reading.name


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
    view = _dashboard(application, shown, trunk, case, _SCHEMATIC_AND_BRANCH)
    trunk.add_time_bookmark(TimeBookmark(CaseInstant(75.05), "what if"))
    view.present(False)
    selector = _branch_control(view).point_selector
    selector.setCurrentIndex(selector.findText(f"{format_elapsed(751 * 0.1)}, on your mark"))
    _branch_control(view).take_button.click()
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


def _failing_assembly(*args: object, **kwargs: object) -> NoReturn:
    """Stand in for `assemble_chart_frame` where every frame must fail."""

    del args, kwargs
    raise RuntimeError("this frame could not be assembled")


def test_a_reset_that_no_frame_draws_withholds_the_schematic_with_the_readouts(
    application: QApplication, shown: list[SimulationView], monkeypatch: pytest.MonkeyPatch
) -> None:
    """After a Reset that no frame has drawn, the schematic shows no value of the discarded run.

    The adversarial review of `PL-RNYV` found this defect. At the time, the
    schematic's View wrote the schematic on each tick. After a Reset, while
    every frame failed, the schematic kept the run's last values, although the
    readouts beside it were withheld. The run now writes and withholds its
    schematic at the same moments as its readouts. The workspace in this test
    also shows a chart, so that a frame is assembled and fails.
    """

    controller = SimulationController()
    controller.start()
    _advance_to(controller, 90.0)
    controller.pause()
    view = _dashboard(application, shown, controller, workspaces=shipped_workspaces())
    view.layout_container.choose_view(AreaId(2), COMPARTMENT_SCHEMATIC)
    _settle(application)
    view.present(False)
    _assert_every_label_matches_its_run(view)

    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    run = view.runs[0]
    run._reset_button.click()
    dialog = run._reset_dialog
    if dialog is not None:
        dialog.discard_button.click()
    _settle(application)
    view.present(False)

    assert run.controller.has_failed is True
    assert _readout_values(run) == (WITHHELD_CONCENTRATION_TEXT,) * 6
    schematic = _schematic(view).schematics[0]
    assert [reading.tension for reading in schematic.canvas.readings] == [
        WITHHELD_CONCENTRATION_TEXT
    ] * 6
    assert [reading.amount for reading in schematic.canvas.readings] == [WITHHELD_AMOUNT_TEXT] * 6
    assert [reading.fill for reading in schematic.canvas.readings] == [0.0] * 6
    assert schematic.scale_text.isHidden()
    assert schematic.off_scale_text.isHidden()
    assert schematic.share_bar.segments is None
    assert schematic.share_text.isHidden()


def _everything_drawn(schematic: RunSchematic) -> tuple[object, ...]:
    """Every text, reading and share that one run's schematic draws, in a fixed order.

    Nothing here names a value. The labels are found by walking the widget,
    so a label added to it later is compared too.
    """

    return (
        [label.text() for label in schematic.findChildren(QLabel) if not label.isHidden()],
        schematic.canvas.painted_strings(),
        schematic.canvas.readings,
        schematic.share_bar.segments,
    )


def test_a_schematic_reset_with_no_frame_is_drawn_like_one_that_never_showed_a_run(
    application: QApplication, shown: list[SimulationView], monkeypatch: pytest.MonkeyPatch
) -> None:
    """After a Reset that no frame draws, the schematic keeps nothing of the discarded run.

    Two dashboards hold the same state: a run at its opening, halted, with no
    frame drawn of it. One showed a run at 90 s first and was then Reset, and
    the other never drew a frame. Everything the schematic of each draws is
    read back, and the two must be equal. So a value left from the
    discarded run fails this test whether a label holds it or the canvas
    paints it, and no assertion has to name the value (`PL-RF2S`, replaying
    `PL-B8DL` and `PL-0G2P`).

    The two are compared by what they draw and not by their pixels. A
    dashboard whose first frame failed lays its Areas out at other widths
    than one that drew a frame, so the two images differ in size.

    The test above names each value it checks, and it does not name the
    instant in the schematic's heading. With that instant kept from the
    discarded run, the test above passes and this one fails.
    """

    controller = SimulationController()
    controller.start()
    _advance_to(controller, 90.0)
    controller.pause()
    used = _dashboard(application, shown, controller, workspaces=shipped_workspaces())
    used.layout_container.choose_view(AreaId(2), COMPARTMENT_SCHEMATIC)
    _settle(application)
    used.present(False)
    _assert_every_label_matches_its_run(used)

    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    run = used.runs[0]
    run._reset_button.click()
    dialog = run._reset_dialog
    if dialog is not None:
        dialog.discard_button.click()
    _settle(application)
    used.present(False)

    fresh = _dashboard(application, shown, SimulationController(), workspaces=shipped_workspaces())
    fresh.layout_container.choose_view(AreaId(2), COMPARTMENT_SCHEMATIC)
    _settle(application)
    fresh.present(False)
    _settle(application)

    assert run.controller.has_failed is True
    assert fresh.runs[0].controller.has_failed is True
    # The fresh dashboard's View holds no copy of the schematic. A View is given
    # its runs by a tick, and a dashboard whose first frame fails gives none
    # (`PL-RF2S`, second pull request). So the fresh run builds its copy here.
    on_screen = _schematic(used).schematics[0]
    never_used = fresh.runs[0].build_compartment_schematic()
    assert _everything_drawn(on_screen) == _everything_drawn(never_used)


def _painted(canvas: SchematicCanvas) -> QImage:
    image = canvas.grab().toImage()
    assert image.devicePixelRatio() == 1.0

    return image


def _column_centre(canvas: SchematicCanvas, index: int) -> int:
    return int(canvas.width() / 6 * (index + 0.5))


# Where the canvas stands its containers, restated from `app/qt_schematic.py`'s
# placeholder sizes: their top, their height and their width, in pixels.
_CONTAINER_TOP_PX = 14
_CONTAINER_HEIGHT_PX = 96
_CONTAINER_WIDTH_PX = 44


def test_a_container_cannot_be_read_against_the_chart(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """`PL-8W1B`: beside the chart, the caption says a fill level is not on its gridlines.

    The Maintenance Workspace shows the concentration chart and the schematic
    side by side. A container is much shorter than the chart's plot, so one
    tension stands at different screen heights in the two. A learner who read a
    fill level across to the chart's gridlines would read the wrong tension. The
    caption therefore names the chart's range without calling it the chart's
    scale, and says the heights do not line up with its gridlines.
    """

    workspaces = shipped_workspaces()
    maintenance = next(
        index
        for index, workspace in enumerate(workspaces.workspaces)
        if workspace.name == WorkspaceName("Maintenance")
    )
    controller = SimulationController()
    controller.start()
    _advance(controller, 600.0)
    view = _dashboard(
        application, shown, controller, workspaces=WorkspaceSet(workspaces.workspaces, maintenance)
    )
    (chart,) = (v for v in view.layout_container.views() if isinstance(v, ConcentrationView))
    (schematic,) = _schematic(view).schematics
    caption = schematic.scale_text.text()

    assert chart.chart.plot_area().height() > 2 * _CONTAINER_HEIGHT_PX
    assert "do not line up with the chart's gridlines" in caption
    assert "Read each tension from its label." in caption
    assert "on the concentration chart's scale" not in caption
    assert not schematic.scale_text.isHidden()


def test_each_container_is_painted_to_its_tension_and_an_off_scale_one_is_marked(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """The painted fill, not only the reading, is the tension's share of the scale.

    The test measures the fill by counting pixels of the compartment's own colour
    down the container's centre. The outline and the off-scale bar cover up to
    three pixels of the fill. So the count must be within three pixels of the
    reading's share of the container's height.
    """

    off_scale = SimulationController(agent_id="sevoflurane")
    off_scale.set_alveolar_ventilation(AlveolarVentilation(0.0))
    off_scale.set_fresh_gas_flow(FreshGasFlow(8.0))
    off_scale.set_delivered_concentration_percent(Percent(8.0))
    off_scale.start()
    _advance(off_scale, 10 * SECONDS_PER_MINUTE)
    off_scale.pause()
    ordinary = SimulationController()
    ordinary.start()
    _advance(ordinary, 20 * SECONDS_PER_MINUTE)
    ordinary.pause()
    warning = QColor(WARNING).rgb()

    for controller in (off_scale, ordinary):
        canvas = _schematic(_dashboard(application, shown, controller)).schematics[0].canvas
        image = _painted(canvas)

        for index, reading in enumerate(canvas.readings):
            x = _column_centre(canvas, index)
            colour = QColor(trace_style(reading.quantity).color).rgb()
            painted = sum(image.pixelColor(x, y).rgb() == colour for y in range(image.height()))
            assert abs(painted - reading.fill * _CONTAINER_HEIGHT_PX) <= 3, reading.name
            marked = any(
                image.pixelColor(x, y).rgb() == warning
                for y in range(_CONTAINER_TOP_PX - 2, _CONTAINER_TOP_PX + 3)
            )
            assert marked is reading.off_scale, reading.name

        assert any(reading.off_scale for reading in canvas.readings) is (controller is off_scale)


def test_the_tissues_are_drawn_in_parallel_and_never_joined_to_each_other(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """No line joins one tissue's container to the next, as no flow joins them.

    A line joins the circuit to the alveoli and the alveoli to venous blood,
    at the containers' mid-height. Between venous blood and each tissue, and
    between tissues, the gap at that height is empty. The arterial line above
    the row and the venous line below it run the length of the tissues.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 20 * SECONDS_PER_MINUTE)
    controller.pause()
    canvas = _schematic(_dashboard(application, shown, controller)).schematics[0].canvas
    image = _painted(canvas)
    muted = QColor(MUTED).rgb()
    middle = _CONTAINER_TOP_PX + _CONTAINER_HEIGHT_PX // 2

    def lined(left: int, right: int, rows: range) -> list[bool]:
        """Whether each row has a MUTED pixel in the gap between two containers."""

        xs = range(
            _column_centre(canvas, left) + _CONTAINER_WIDTH_PX // 2 + 1,
            _column_centre(canvas, right) - _CONTAINER_WIDTH_PX // 2 - 1,
        )
        return [any(image.pixelColor(x, y).rgb() == muted for x in xs) for y in rows]

    across = range(middle - 4, middle + 5)
    assert any(lined(0, 1, across)), "the circuit is joined to the alveoli"
    assert any(lined(1, 2, across)), "the alveoli are joined to venous blood"
    assert not any(lined(2, 3, across)), "venous blood is not joined sideways to a tissue"
    assert not any(lined(3, 4, across)), "the vessel-rich group is not joined to muscle"
    assert not any(lined(4, 5, across)), "muscle is not joined to fat"

    bus_rows = range(0, _CONTAINER_TOP_PX)
    below_rows = range(
        _CONTAINER_TOP_PX + _CONTAINER_HEIGHT_PX + 1,
        _CONTAINER_TOP_PX + _CONTAINER_HEIGHT_PX + _CONTAINER_TOP_PX,
    )
    for left in range(1, 5):
        assert any(lined(left, left + 1, bus_rows)), f"arterial line spans gap {left}"
    for left in range(2, 5):
        assert any(lined(left, left + 1, below_rows)), f"venous line spans gap {left}"


def test_the_share_bar_is_painted_to_each_share_and_named_in_text(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """Each segment's painted length is its share of the bar, and the lines under it name each.

    The segment of each compartment is measured in pixels of its own colour
    along the bar's middle row. Antialiasing and the divider before a segment
    can take one pixel at each end of it. So each count must be within two
    pixels of the share multiplied by the bar's width. At ten seconds, venous
    blood, muscle and fat each hold far less than 1%. The blind review of
    `PL-S79P` found that their dividers then covered them and merged into one
    another. So the test checks the bar at that instant as well as at one hour.
    """

    for seconds in (10.0, 60 * SECONDS_PER_MINUTE):
        _check_the_share_bar(application, shown, seconds)


def _check_the_share_bar(
    application: QApplication, shown: list[SimulationView], seconds: float
) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, seconds)
    controller.pause()
    schematic = _schematic(_dashboard(application, shown, controller)).schematics[0]
    bar = schematic.share_bar
    segments = bar.segments
    assert segments is not None
    image = bar.grab().toImage()
    assert image.devicePixelRatio() == 1.0
    middle = image.height() // 2
    amounts = controller.snapshot().compartment_agent_amounts
    total = sum(amounts.of(segment.quantity) for segment in segments)

    for segment in segments:
        colour = QColor(trace_style(segment.quantity).color).rgb()
        painted = sum(image.pixelColor(x, middle).rgb() == colour for x in range(image.width()))
        expected = amounts.of(segment.quantity) / total * image.width()
        assert abs(painted - expected) <= 2, segment.name
        assert f"{segment.name} {segment.text}" in schematic.share_text.text()

    assert not schematic.share_text.isHidden()

    # Inside the outline, the row is coloured segments with one panel-coloured
    # divider between each pair of neighbours, and no divider that stands
    # beside another or covers a segment.
    trace_colours = {QColor(trace_style(segment.quantity).color).rgb() for segment in segments}
    panel = QColor(PANEL).rgb()
    runs: list[int] = []
    for x in range(1, image.width() - 1):
        colour = image.pixelColor(x, middle).rgb()
        if not runs or runs[-1] != colour:
            runs.append(colour)
    assert set(runs) <= trace_colours | {panel}, "every pixel is a segment or a divider"
    assert runs[0] != panel
    assert runs[-1] != panel
    assert runs.count(panel) == len(runs) - runs.count(panel) - 1, seconds


def test_a_run_that_holds_no_agent_shows_an_empty_share_bar_and_says_why(
    application: QApplication, shown: list[SimulationView]
) -> None:
    schematic = _schematic(_dashboard(application, shown, SimulationController())).schematics[0]
    image = schematic.share_bar.grab().toImage()
    middle = image.height() // 2
    colours = {QColor(trace_style(quantity).color).rgb() for quantity in COMPARTMENT_QUANTITIES}

    assert schematic.share_bar.segments is None
    assert schematic.share_text.text() == NO_AGENT_SHARE_LINE
    assert not any(image.pixelColor(x, middle).rgb() in colours for x in range(image.width()))
