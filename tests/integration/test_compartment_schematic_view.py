"""The compartment schematic View in a real dashboard, from patient inputs to its drawn labels.

`docs/INTERFACE.md` § "The compartment schematic: what its heights, amounts and
share bar assert" is the specification (`PL-2881`), and `PL-RNYV` built the
View. These tests check two things. First, they check that a run's inputs reach
the drawn labels through the model. The expected labels come from a closed form
that is computed apart from the code under test. Second, they check the labels
after each action by a user that changes which state a run is in. The
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
from PySide6.QtCore import QEvent, QPoint, QRect, QRectF
from PySide6.QtGui import QColor, QFontMetrics, QImage
from PySide6.QtWidgets import QApplication, QLabel, QScrollArea, QWidget

from anesthesia_sim.app import simulation_view as simulation_view_module
from anesthesia_sim.app.area_layout import ViewScroll
from anesthesia_sim.app.bookmarks import TimeBookmark
from anesthesia_sim.app.chart_frame import trace_style
from anesthesia_sim.app.compartment_schematic import (
    NO_AGENT_SHARE_CAPTION,
    NO_SHARE_TEXT,
    SHARE_TEMPLATE,
    WIDEST_LABELS,
    WITHHELD_AMOUNT_TEXT,
)
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import TRUNK_RUN_INDEX, WITHHELD_CONCENTRATION_TEXT
from anesthesia_sim.app.formatting import format_compartment_share, format_elapsed
from anesthesia_sim.app.qt_schematic import ContainerNames, RunSchematic, SchematicCanvas
from anesthesia_sim.app.qt_widgets import ForkPanel
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES
from anesthesia_sim.app.run_view import RunView
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.theme import INK, MUTED, WARNING
from anesthesia_sim.app.view_registry import BOOKMARKS, BRANCH, COMPARTMENT_SCHEMATIC, REGISTERED
from anesthesia_sim.app.views import BranchView, CompartmentSchematicView, ConcentrationView
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.parameters import load_agent_parameters
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
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

#: The schematic over the bookmarks, for a test that scrolls the page. The
#: bookmarks' Area below gives the page room to carry the schematic's top out
#: of a short window while the rest of it is in view.
_SCHEMATIC_OVER_BOOKMARKS = WorkspaceSet(
    (
        Workspace(
            WorkspaceName("Schematic over bookmarks"),
            Origin.mine(),
            LayoutModel(
                (
                    Window(
                        Split(
                            Orientation.COLUMN,
                            (0.5, 0.5),
                            (Area(AreaId(1), COMPARTMENT_SCHEMATIC), Area(AreaId(2), BOOKMARKS)),
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

SECONDS_PER_MINUTE = 60


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
    this moment, in millilitres to two significant figures. A share is checked
    against the same six amounts, summed here, and is None while they sum to
    zero. So the check fails for a schematic that still shows a state its run
    has left.
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

        total_l = sum(amounts.of(quantity) for quantity in COMPARTMENT_QUANTITIES)

        for reading in readings:
            millilitres = amounts.of(reading.quantity) * 1000.0
            assert reading.amount == _two_figures(millilitres), reading.name

            if total_l == 0.0:
                assert reading.share is None, reading.name
            else:
                assert reading.share == pytest.approx(amounts.of(reading.quantity) / total_l)


def _two_figures(millilitres: float) -> str:
    """An amount written to two significant figures, never finer than 0.01 mL.

    It is written here apart from the formatter, from the rule in
    `docs/INTERFACE.md` § "Displayed precision".
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


def _advance(controller: SimulationController, seconds: int) -> None:
    for _ in range(seconds // SIMULATION_STEP_S):
        controller.advance()


def _advance_to(controller: SimulationController, elapsed_s: int) -> None:
    while controller.snapshot().elapsed_s < elapsed_s:
        controller.advance()


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

    dial_percent, flow_l_min, seconds = 4.0, 8.0, 30
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
    axis_top_percent = 3 * load_agent_parameters("sevoflurane").mac_at_age_40_percent

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
    _advance_to(trunk, 60)
    trunk.set_fresh_gas_flow(FreshGasFlow(2.0))
    trunk.pause()
    case = BranchedCase(trunk)
    view = _dashboard(application, shown, trunk, case, _SCHEMATIC_AND_BRANCH)

    _assert_every_label_matches_its_run(view)
    assert _schematic(view).schematics[0].name_text.text().startswith("At ")

    # Every frame redraws the instant the run stands at.
    trunk.start()
    _advance(trunk, 30)
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
    _advance(branch, 45)
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
    _advance(run.controller, 120)
    run.controller.pause()
    view.present(False)

    _assert_every_label_matches_its_run(view)
    isoflurane_top = 3 * load_agent_parameters("isoflurane").mac_at_age_40_percent
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
    _advance_to(trunk, 30)
    trunk.set_fresh_gas_flow(FreshGasFlow(2.0))
    _advance_to(trunk, 120)
    trunk.pause()
    case = BranchedCase(trunk)
    view = _dashboard(application, shown, trunk, case, _SCHEMATIC_AND_BRANCH)
    trunk.add_time_bookmark(TimeBookmark(CaseInstant(75), "what if"))
    view.present(False)
    selector = _branch_control(view).point_selector
    selector.setCurrentIndex(selector.findText(f"{format_elapsed(75)}, on your mark"))
    _branch_control(view).take_button.click()
    _settle(application)
    view.present(False)

    assert len(view.runs) == 2
    assert view.runs[1].controller.snapshot().elapsed_s == 75
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
    _advance_to(controller, 90)
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
    assert [reading.share for reading in schematic.canvas.readings] == [None] * 6
    assert [reading.share_text for reading in schematic.canvas.readings] == [NO_SHARE_TEXT] * 6
    assert schematic.share_text.isHidden()


def _everything_drawn(schematic: RunSchematic) -> tuple[object, ...]:
    """Every text, reading and share that one run's schematic draws, in a fixed order.

    Nothing here names a value. The labels are found by walking the widget,
    so a label added to it later is compared too.
    """

    return (
        [label.text() for label in schematic.findChildren(QLabel) if not label.isHidden()],
        schematic.painted_strings(),
        schematic.canvas.readings,
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
    _advance_to(controller, 90)
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
    # Both schematics are read from the View. A halt hands every View the runs
    # with no frame, so the fresh dashboard's View holds a schematic although
    # its first frame failed (`PL-RF2S`).
    on_screen = _schematic(used).schematics[0]
    never_used = _schematic(fresh).schematics[0]
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
# How far inside a share bar's edge its fill starts, past the outline and one
# pixel of ground, restated the same way.
_FILL_INSET_PX = 2


def test_a_container_cannot_be_read_against_the_chart(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """`PL-8W1B`: beside the chart, each container carries the chart's gridlines as marks.

    The Maintenance Workspace shows the concentration chart and the schematic
    side by side. A container is much shorter than the chart's plot, so one
    tension stands at different screen heights in the two. A user who read a
    fill level across to the chart's gridlines would read the wrong tension. So
    each container is marked inside both sides at the chart's gridlines, and the
    caption says what the marks stand for.

    The chart rules its axis every 0.5 MAC up to 3 MAC, so the expected marks
    stand at sixths of the container's height. The test finds each painted mark
    as a row of `MUTED` pixels just inside the container's left side.
    """

    workspaces = shipped_workspaces()
    maintenance = next(
        index
        for index, workspace in enumerate(workspaces.workspaces)
        if workspace.name == WorkspaceName("Maintenance")
    )
    controller = SimulationController()
    controller.start()
    _advance(controller, 600)
    view = _dashboard(
        application, shown, controller, workspaces=WorkspaceSet(workspaces.workspaces, maintenance)
    )
    (chart,) = (v for v in view.layout_container.views() if isinstance(v, ConcentrationView))
    (schematic,) = _schematic(view).schematics
    caption = schematic.scale_text.text()
    canvas = schematic.canvas
    image = _painted(canvas)
    muted = QColor(MUTED).rgb()
    sixths = [sixth / 6 for sixth in range(1, 6)]

    assert chart.chart.plot_area().height() > 2 * _CONTAINER_HEIGHT_PX
    assert canvas.marks == pytest.approx(sixths)
    assert "Marks stand every 0.5 ×MAC." in caption
    assert not schematic.scale_text.isHidden()

    for index in range(len(canvas.readings)):
        x = _column_centre(canvas, index) - _CONTAINER_WIDTH_PX // 2 + 3
        inside = range(_CONTAINER_TOP_PX + 1, _CONTAINER_TOP_PX + _CONTAINER_HEIGHT_PX)
        rows = [y for y in inside if image.pixelColor(x, y).rgb() == muted]
        expected = [_CONTAINER_TOP_PX + _CONTAINER_HEIGHT_PX * (1 - sixth) for sixth in sixths]
        assert len(rows) == len(expected), canvas.readings[index].name
        assert all(
            abs(row - mark) <= 1
            for row, mark in zip(sorted(rows, reverse=True), expected, strict=True)
        ), canvas.readings[index].name


def test_each_container_is_painted_to_its_tension_and_an_off_scale_one_is_marked(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """The painted fill, not only the reading, is the tension's share of the scale.

    The test measures the fill by counting pixels of the compartment's own colour
    down the container's centre, from the container's top to its bottom, so a
    share bar under the label is not counted. The outline and the off-scale bar
    cover up to three pixels of the fill. So the count must be within three
    pixels of the reading's share of the container's height.
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
            container_rows = range(_CONTAINER_TOP_PX, _CONTAINER_TOP_PX + _CONTAINER_HEIGHT_PX + 1)
            painted = sum(image.pixelColor(x, y).rgb() == colour for y in container_rows)
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


def test_each_share_bar_is_painted_to_its_share_on_one_scale_under_its_own_label(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """`PL-8PL4`: each bar is filled to its compartment's share, all six on one scale.

    The fill of each bar is counted in pixels of its compartment's colour along
    the bar's middle row. The fill starts 2 px inside the bar's edge, and its
    last pixel can round either way, so each count must be within one pixel of
    the share multiplied by the length left inside. The share is worked out
    here from the six amounts. The six bars must be one length, so that equal
    lengths of fill are equal shares, and each must be at least as long as
    every label line above it. Each bar must stand inside its own container's
    column, under the label that names it, and that label's last line must be
    the share worked out here. At ten seconds, venous blood, muscle and fat
    each hold far less than 1%, and at one hour venous blood holds about 1%, so
    the test checks the bars at both.
    """

    for seconds in (10, 60 * SECONDS_PER_MINUTE):
        _check_the_share_bars(application, shown, seconds)


def _check_the_share_bars(
    application: QApplication, shown: list[SimulationView], seconds: int
) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, seconds)
    controller.pause()
    canvas = _schematic(_dashboard(application, shown, controller)).schematics[0].canvas
    image = _painted(canvas)
    amounts = controller.snapshot().compartment_agent_amounts
    total = sum(amounts.of(quantity) for quantity in COMPARTMENT_QUANTITIES)
    bars = [canvas.share_bar(index) for index in range(6)]
    column = canvas.width() / 6
    painted_strings = canvas.painted_strings()
    lines = len(painted_strings) // 6
    metrics = QFontMetrics(canvas.font())
    widest_line = max(metrics.horizontalAdvance(text) for text in painted_strings)

    assert len({bar.width() for bar in bars}) == 1, "the six bars are not one length"
    assert bars[0].width() >= widest_line, "a bar is shorter than a label line"

    for index, (reading, bar) in enumerate(zip(canvas.readings, bars, strict=True)):
        assert column * index <= bar.left(), reading.name
        assert bar.right() <= column * (index + 1), reading.name
        share = format_compartment_share(amounts.of(reading.quantity) / total)
        assert painted_strings[lines * index + lines - 1] == SHARE_TEMPLATE.format(share=share)
        middle = int(bar.center().y())
        colour = QColor(trace_style(reading.quantity).color).rgb()
        painted = sum(
            image.pixelColor(x, middle).rgb() == colour
            for x in range(int(bar.left()), int(bar.right()))
        )
        expected = amounts.of(reading.quantity) / total * (bar.width() - 2 * _FILL_INSET_PX)
        assert abs(painted - expected) <= 1, (reading.name, painted, expected)


def test_a_run_that_holds_no_agent_shows_empty_share_bars_and_says_why(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """Before any agent, each bar is an outline, each share a dash, and the caption says why.

    Inside each empty outline every pixel must be the canvas's ground, so no
    line of the label above runs into the bar, and the bar must lie wholly
    inside the canvas.
    """

    schematic = _schematic(_dashboard(application, shown, SimulationController())).schematics[0]
    canvas = schematic.canvas
    image = _painted(canvas)
    colours = {QColor(trace_style(quantity).color).rgb() for quantity in COMPARTMENT_QUANTITIES}
    ink = QColor(INK).rgb()

    assert [reading.share_text for reading in canvas.readings] == [NO_SHARE_TEXT] * 6
    assert schematic.share_text.text() == NO_AGENT_SHARE_CAPTION
    assert not schematic.share_text.isHidden()

    for index in range(6):
        bar = canvas.share_bar(index)
        middle = int(bar.center().y())
        row = [image.pixelColor(x, middle).rgb() for x in range(int(bar.left()), int(bar.right()))]
        assert not any(colour in colours for colour in row), index
        assert row[0] == ink, index
        assert row[-1] == ink, index
        inside = {
            image.pixelColor(x, y).rgb()
            for x in range(int(bar.left()) + 1, int(bar.right()) - 1)
            for y in range(int(bar.top()) + 1, int(bar.bottom()) - 1)
        }
        assert len(inside) == 1, index
        assert bar.bottom() <= canvas.height(), index


def test_a_share_bar_is_refused_for_an_index_outside_the_six_containers(
    application: QApplication,
) -> None:
    """Asking for a seventh container's bar, outline, label or name, or index -1's, raises.

    Python would read index -1 as the last container, and a test that found a
    drawn item there would check the wrong compartment's.
    """

    canvas = SchematicCanvas()
    names = ContainerNames()

    for index in (-1, 6):
        for find in (
            canvas.share_bar,
            canvas.container,
            lambda index: canvas.label_line(index, 0),
            names.name_cell,
        ):
            with pytest.raises(
                IndexError, match=f"has 6 containers, so it has none at index {index}"
            ):
                find(index)

    for line in (-1, 3):
        with pytest.raises(IndexError, match=f"a label has 3 lines, so it has no line {line}"):
            canvas.label_line(0, line)


def test_the_share_line_adds_no_width_to_a_column(application: QApplication) -> None:
    """`PL-8PL4`: no share line is wider than the widest name or amount that a column holds.

    A column is as wide as its widest label, and the schematic is at least six
    columns wide. A share line wider than every name and amount would therefore
    widen the schematic, and with it the Maintenance Workspace's column that
    holds it. Worded "of the agent", the share line at ">99%" was the widest
    label. Under the font that CI draws in, the Maintenance Workspace then
    scrolled sideways at 1366 by 768, and the parameter controls moved at 1920
    by 1080. The share lines are worked out here, at a share that prints as
    "<1%", two digits, ">99%" and "100%", and with no share.
    """

    metrics = QFontMetrics(SchematicCanvas().font())
    share_lines = [
        SHARE_TEMPLATE.format(share=format_compartment_share(share))
        for share in (1e-9, 0.55, 1.0 - 1e-9, 1.0)
    ] + [NO_SHARE_TEXT]
    names_and_amounts = [text for text in WIDEST_LABELS if text not in share_lines]

    widest_share = max(metrics.horizontalAdvance(text) for text in share_lines)
    widest_other = max(metrics.horizontalAdvance(text) for text in names_and_amounts)

    assert widest_share <= widest_other, (share_lines, widest_share, widest_other)


def _view_scroll(widget: QWidget) -> ViewScroll:
    """Return the box that scrolls the View holding `widget`."""

    ancestor = widget.parentWidget()

    while not isinstance(ancestor, ViewScroll):
        assert ancestor is not None, "the widget is in no View's scroll box"
        ancestor = ancestor.parentWidget()

    return ancestor


def _in_viewport(scroll: ViewScroll, widget: QWidget, rectangle: QRectF) -> QRect:
    """Return `rectangle`, in `widget`'s pixels, in the pixels of the box's viewport."""

    return QRect(
        widget.mapTo(scroll.viewport(), rectangle.topLeft().toPoint()), rectangle.size().toSize()
    )


def _maintenance() -> WorkspaceSet:
    """Return the shipped Workspaces with the Maintenance Workspace active."""

    workspaces = shipped_workspaces()
    maintenance = next(
        index
        for index, workspace in enumerate(workspaces.workspaces)
        if workspace.name == WorkspaceName("Maintenance")
    )

    return WorkspaceSet(workspaces.workspaces, maintenance)


def _paused_dashboard(
    application: QApplication,
    shown: list[SimulationView],
    workspaces: WorkspaceSet,
    size: tuple[int, int],
    *,
    branched: bool,
    dial_percent: float | None = None,
) -> SimulationView:
    """Return a dashboard at `size`, paused 10 minutes into a run, with a branch open if asked.

    The branch opens at the run's last second, so the two runs show the same
    values and differ only in their names.
    """

    controller = SimulationController()

    if dial_percent is not None:
        controller.set_delivered_concentration_percent(Percent(dial_percent))

    controller.start()
    _advance_to(controller, 10 * SECONDS_PER_MINUTE)
    controller.pause()
    case = BranchedCase(controller)
    view = SimulationView((controller,), case=case, workspaces=workspaces)
    shown.append(view)
    view.resize(*size)
    view.show()
    application.processEvents()
    view.present(False)

    if branched:
        view._show_branch(case.fork_here())
        application.processEvents()
        view.present(False)

    application.processEvents()

    return view


def _shown_part(page: QScrollArea, scroll: ViewScroll) -> QRect:
    """Return the part of the schematic's box in view on the page, in the page viewport's pixels."""

    box = QRect(scroll.viewport().mapTo(page.viewport(), QPoint(0, 0)), scroll.viewport().size())

    return page.viewport().rect().intersected(box)


def _seen_without_heading(page: QScrollArea, run: RunSchematic, shown_part: QRect) -> list[QRect]:
    """Return each container, share bar and label line of the run that is seen in `shown_part`.

    A value is seen when it lies wholly in `shown_part` and clear of the
    run's heading. Each is in the page viewport's pixels. A value under the heading is
    hidden by it, so only a value clear of the heading is seen.
    """

    heading = QRect(run.heading.mapTo(page.viewport(), QPoint(0, 0)), run.heading.size())
    values = [
        QRect(run.canvas.mapTo(page.viewport(), drawn.topLeft().toPoint()), drawn.size().toSize())
        for index in range(len(_NAMES))
        for drawn in (
            run.canvas.container(index),
            run.canvas.share_bar(index),
            *(run.canvas.label_line(index, line) for line in range(3)),
        )
    ]

    return [
        value for value in values if shown_part.contains(value) and not value.intersects(heading)
    ]


def _heading_in_view(page: QScrollArea, run: RunSchematic, shown_part: QRect) -> bool:
    """Return whether the run's heading lies wholly in `shown_part`."""

    return shown_part.contains(
        QRect(run.heading.mapTo(page.viewport(), QPoint(0, 0)), run.heading.size())
    )


def _in_run(run: RunSchematic, widget: QWidget, rectangle: QRectF) -> QRectF:
    """Return `rectangle`, in `widget`'s pixels, in the pixels of the run's schematic."""

    return rectangle.translated(widget.mapTo(run, QPoint(0, 0)).toPointF())


@pytest.mark.parametrize(
    ("dial_percent", "branched"),
    [(None, True), (8.0, False), (None, False)],
    ids=["two runs", "one run off the scale", "one run"],
)
def test_no_value_is_in_view_without_its_run_and_compartment_at_any_scroll_position(
    application: QApplication,
    shown: list[SimulationView],
    dial_percent: float | None,
    branched: bool,
) -> None:
    """`PL-3NGZ`: wherever a value of a run is in view, that run's whole heading is in view too.

    The Maintenance Workspace at 1366 by 768 gives the schematic an Area
    shorter than one run's schematic, and two compared runs share it. The test
    scrolls the Area through every position. Wherever a container, a share bar
    or a line of a label is wholly in view and not under the heading, the
    heading is wholly in view too. It holds the line that names the run and
    the instant, the share caption and the compartments' names. Before the
    heading was pinned, a scroll of the two runs' schematic showed a tension
    with neither its run nor its compartment named. The disclaimer, the
    tensions' unit and the amounts' unit with its condition stand above the
    scroll box, so they are in view at every position. At 8% the circuit is
    off the scale, which adds the off-scale
    line to the schematic. At every position each heading stays inside its own
    run's schematic, so it never covers the other run's rows.
    """

    view = _paused_dashboard(
        application,
        shown,
        _maintenance(),
        (1366, 768),
        branched=branched,
        dial_percent=dial_percent,
    )
    schematic = _schematic(view)
    scroll = _view_scroll(schematic)
    bar = scroll.verticalScrollBar()
    viewport = scroll.viewport().rect()

    assert len(schematic.schematics) == (2 if branched else 1)
    # The premise: the Area cannot hold the schematic, so the test scrolls.
    assert bar.maximum() > 0
    assert schematic.pinned_row.isVisible()
    assert not scroll.isAncestorOf(schematic.pinned_row)
    assert schematic.qualifier_label.text().splitlines() == [
        "Model outputs — not measurements. Tensions are in % of 1 atm.",
        "Amounts are millilitres of vapour at 20 °C and 1 atm.",
    ]

    for position in range(bar.maximum() + 1):
        bar.setValue(position)
        application.processEvents()

        for run in schematic.schematics:
            assert run.names.painted_strings() == _NAMES
            # The heading stays inside its own run's schematic, so it never
            # covers the other run's rows.
            assert run.rect().contains(run.heading.geometry()), position
            heading = _in_viewport(scroll, run.heading, QRectF(run.heading.rect()))
            canvas = run.canvas
            values = [
                _in_viewport(scroll, canvas, drawn)
                for index in range(len(_NAMES))
                for drawn in (
                    canvas.container(index),
                    canvas.share_bar(index),
                    *(canvas.label_line(index, line) for line in range(3)),
                )
            ]
            seen = [
                value
                for value in values
                if viewport.contains(value) and not value.intersects(heading)
            ]

            if seen:
                assert viewport.contains(heading), (position, run.name_text.text())


@pytest.mark.parametrize(
    ("workspaces", "size", "branched"),
    [
        (_maintenance(), (1366, 768), True),
        (_SCHEMATIC_ONLY, (_WINDOW_WIDTH_PX, _WINDOW_HEIGHT_PX), False),
    ],
    ids=["two runs at 1366 by 768", "one run, wide"],
)
def test_each_compartment_name_stands_over_its_own_container(
    application: QApplication,
    shown: list[SimulationView],
    workspaces: WorkspaceSet,
    size: tuple[int, int],
    branched: bool,
) -> None:
    """`PL-3NGZ`: each name in a run's heading is centred over the container it names.

    The names are painted in the heading, and the containers in the canvas
    under it. Each widget divides its own width into six columns, so a name
    stands over its container only while the two widgets are as wide as each
    other and start at one edge. A container that slid under its neighbour's
    name would show its tension under the wrong compartment's name. The test
    checks each column at two widths of the schematic.
    """

    view = _paused_dashboard(application, shown, workspaces, size, branched=branched)

    for run in _schematic(view).schematics:
        for index, name in enumerate(_NAMES):
            cell = _in_run(run, run.names, run.names.name_cell(index))
            container = _in_run(run, run.canvas, run.canvas.container(index))

            assert run.names.painted_strings()[index] == name
            assert cell.left() <= container.left(), name
            assert container.right() <= cell.right(), name
            # Both centres are computed from one width divided by six, so they
            # agree to the half pixel by which a rectangle's centre is rounded.
            assert abs(cell.center().x() - container.center().x()) <= 0.5, name


def test_a_run_heading_follows_a_scroll_of_the_page(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """`PL-3NGZ`: wherever the page's scroll leaves a run's value in view, its heading is in view.

    A window shorter than the dashboard scrolls the whole page, Areas and
    all. The schematic's Area is here at the top of a window 400 px tall,
    over the bookmarks' Area, so a page scroll carries the top of its box,
    and the heading pinned there, above the page's edge. For each run, the test scrolls the
    box until a container, a share bar or a line of a label stands just
    under the heading pinned at the box's top. It then scrolls the page
    through every position. Wherever a value is wholly in view and not under
    the heading, the heading is wholly in view too. Before the page's scroll
    moved the headings, the heading stayed where the box's last scroll put
    it, and went above the page's edge while the value under it stayed in
    view.
    """

    view = _paused_dashboard(
        application, shown, _SCHEMATIC_OVER_BOOKMARKS, (_WINDOW_WIDTH_PX, 400), branched=True
    )
    page = view._page_scroll
    schematic = _schematic(view)
    scroll = _view_scroll(schematic)
    page_bar = page.verticalScrollBar()
    box_bar = scroll.verticalScrollBar()

    # The premise: the page scrolls far enough to take the top of the
    # schematic's box out of view.
    page_bar.setValue(0)
    application.processEvents()
    assert page_bar.maximum() > scroll.viewport().mapTo(page.viewport(), QPoint(0, 0)).y()

    for pinned in schematic.schematics:
        for placed in (
            pinned.canvas.container(0),
            pinned.canvas.share_bar(0),
            *(pinned.canvas.label_line(0, line) for line in range(3)),
        ):
            page_bar.setValue(0)
            box_bar.setValue(
                pinned.mapTo(schematic, QPoint(0, 0)).y()
                + pinned.canvas.mapTo(pinned, placed.topLeft().toPoint()).y()
                - pinned.heading.height()
            )
            box_position = box_bar.value()

            for page_position in range(page_bar.maximum() + 1):
                page_bar.setValue(page_position)
                application.processEvents()
                shown_part = _shown_part(page, scroll)

                for run in schematic.schematics:
                    if _seen_without_heading(page, run, shown_part):
                        assert _heading_in_view(page, run, shown_part), (
                            box_position,
                            page_position,
                            run.name_text.text(),
                        )


def test_a_run_heading_follows_a_taller_window_that_brings_its_run_into_view(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """`PL-H55Q`: a taller window moves each heading over the part of its run it brings into view.

    In the Maintenance Workspace at 1366 by 600 with a branch open, the page
    scrolls. The schematic's box is scrolled until the first run's tension
    line stands just under the heading, and the page is scrolled back to its
    top, which takes the schematic's Area below the window's lower edge. No
    part of either section is then in view, so each heading stands at its
    section's top. Making the window 810 px tall brings the box back into
    view with no scroll of the page or of the box, and the run is paused, so
    no drawn frame moves a heading either. Wherever a value is then seen, its
    run's heading is wholly in view. Before a change of the page's scroll
    range moved the headings, the first run's six tensions were in view with
    its heading above the box's top edge.
    """

    view = _paused_dashboard(application, shown, _maintenance(), (1366, 600), branched=True)
    page = view._page_scroll
    schematic = _schematic(view)
    scroll = _view_scroll(schematic)
    first = schematic.schematics[0]

    page.verticalScrollBar().setValue(page.verticalScrollBar().maximum())
    application.processEvents()
    scroll.verticalScrollBar().setValue(
        first.mapTo(schematic, QPoint(0, 0)).y()
        + first.canvas.mapTo(first, first.canvas.label_line(0, 0).topLeft().toPoint()).y()
        - first.heading.height()
    )
    application.processEvents()
    page.verticalScrollBar().setValue(0)
    application.processEvents()

    # The premise: the page's scroll has taken the whole box out of view.
    assert _shown_part(page, scroll).isEmpty()

    view.resize(1366, 810)
    application.processEvents()
    shown_part = _shown_part(page, scroll)

    # The premise: the taller window shows the first run's values again.
    assert _seen_without_heading(page, first, shown_part)

    for run in schematic.schematics:
        if _seen_without_heading(page, run, shown_part):
            assert _heading_in_view(page, run, shown_part), run.name_text.text()
