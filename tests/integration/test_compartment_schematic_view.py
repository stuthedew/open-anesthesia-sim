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

import json
from collections.abc import Iterator
from math import exp, floor, log10
from pathlib import Path
from typing import NoReturn

import pytest
from PySide6.QtCore import QEvent, QPoint, QRect, QRectF, Qt
from PySide6.QtGui import QColor, QFontMetrics, QImage, QPainter
from PySide6.QtWidgets import QAbstractSlider, QApplication, QLabel, QScrollArea, QWidget

from anesthesia_sim.app import simulation_view as simulation_view_module
from anesthesia_sim.app.area_layout import AreaFrame, ViewScroll
from anesthesia_sim.app.bookmarks import TimeBookmark
from anesthesia_sim.app.chart_frame import trace_style
from anesthesia_sim.app.compartment_schematic import (
    CUT_CONTAINERS_TEXT,
    NO_AGENT_SHARE_CAPTION,
    NO_SHARE_TEXT,
    SHARE_TEMPLATE,
    WIDEST_LABELS,
    WITHHELD_AMOUNT_TEXT,
)
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import TRUNK_RUN_INDEX, WITHHELD_CONCENTRATION_TEXT
from anesthesia_sim.app.formatting import ChartCeiling, format_compartment_share, format_elapsed
from anesthesia_sim.app.preferences import (
    PREFERENCES_FILE_NAME,
    Preferences,
    PreferencesFileError,
    PreferencesStore,
)
from anesthesia_sim.app.qt_schematic import (
    CanvasParts,
    ContainerNames,
    RunSchematic,
    SchematicCanvas,
)
from anesthesia_sim.app.qt_widgets import ForkPanel
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES
from anesthesia_sim.app.run_view import RunView
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.theme import INK, MUTED, PANEL_PADDING, VIEW_ROW_SPACING, WARNING
from anesthesia_sim.app.view_registry import (
    BOOKMARKS,
    BRANCH,
    COMPARTMENT_SCHEMATIC,
    PARAMETER_CONTROLS,
    REGISTERED,
)
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


def _beside_the_controls(name: str, bookmarks_first: bool) -> WorkspaceSet:
    """Return one Workspace of the schematic beside the parameter controls, and the bookmarks.

    The bookmarks' Area stands under that row, or over it where
    `bookmarks_first`, so that a window shorter than the page scrolls the
    page. While the page scrolls, every Area is held at its need, the least
    height at which its View is shown. The parameter controls need their whole
    height, which with a branch open is more than the schematic needs to show
    a whole row of containers. Their row is as tall as they are, so the
    schematic beside them is shown, and its box is shorter than two runs'
    schematics, so it scrolls too (`PL-GWTR`).
    """

    row = Split(
        Orientation.ROW,
        (0.6, 0.4),
        (Area(AreaId(1), COMPARTMENT_SCHEMATIC), Area(AreaId(2), PARAMETER_CONTROLS)),
    )
    bookmarks = Area(AreaId(3), BOOKMARKS)
    children = (bookmarks, row) if bookmarks_first else (row, bookmarks)

    return WorkspaceSet(
        (
            Workspace(
                WorkspaceName(name),
                Origin.mine(),
                LayoutModel((Window(Split(Orientation.COLUMN, (0.5, 0.5), children)),), AreaId(4)),
            ),
        ),
        0,
    )


#: The schematic and the controls over the bookmarks, for a test that scrolls
#: the page and carries the schematic's top out of view.
_SCHEMATIC_OVER_BOOKMARKS = _beside_the_controls("Schematic over bookmarks", False)

#: The bookmarks over the schematic and the controls, for a test that scrolls
#: the page and carries the whole schematic out of view below the window.
_BOOKMARKS_OVER_SCHEMATIC = _beside_the_controls("Bookmarks over schematic", True)

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
_CONTAINER_HEIGHT_PX = 72
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
    preferences_store: PreferencesStore | None = None,
) -> SimulationView:
    """Return a dashboard at `size`, paused 10 minutes into a run, with a branch open if asked.

    The branch opens at the run's last second, so the two runs show the same
    values and differ only in their names. A `preferences_store` is the store
    the dashboard loads the reader's preferences from and saves them to, and by
    default it has none.
    """

    controller = SimulationController()

    if dial_percent is not None:
        controller.set_delivered_concentration_percent(Percent(dial_percent))

    controller.start()
    _advance_to(controller, 10 * SECONDS_PER_MINUTE)
    controller.pause()
    case = BranchedCase(controller)
    view = SimulationView(
        (controller,),
        case=case,
        workspaces=workspaces,
        preferences=None if preferences_store is None else preferences_store.load(),
        preferences_store=preferences_store,
    )
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
    """Return the part of the schematic's box in view on the page, in the page viewport's pixels.

    While the page carries the Area's top above the window's edge, the Area's
    header and pinned row stand over the box's top (`PL-DKQ5`), so the part
    they cover is not in view.
    """

    box = QRect(scroll.viewport().mapTo(page.viewport(), QPoint(0, 0)), scroll.viewport().size())
    shown = page.viewport().rect().intersected(box)
    chrome = _frame_of(scroll).chrome
    covered = QRect(chrome.mapTo(page.viewport(), QPoint(0, 0)), chrome.size())

    if covered.intersects(shown):
        shown.setTop(covered.bottom() + 1)

    return shown if shown.height() > 0 else QRect()


def _frame_of(widget: QWidget) -> AreaFrame:
    """Return the Area frame that holds `widget`."""

    ancestor = widget.parentWidget()

    while not isinstance(ancestor, AreaFrame):
        assert ancestor is not None, widget
        ancestor = ancestor.parentWidget()

    return ancestor


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


def _qualifiers(run: RunSchematic) -> tuple[QWidget, ...]:
    """Return the run's heading, and its run name, share caption and compartment names.

    Each line must stand in the heading, which is drawn over the rows. A line
    that left it would scroll with the rows and could be hidden under the
    heading while a value under it is seen.
    """

    lines = (run.name_text, run.share_text, run.names)

    for line in lines:
        assert run.heading.isAncestorOf(line), line

    return (run.heading, *lines)


def _heading_in_view(page: QScrollArea, run: RunSchematic, shown_part: QRect) -> bool:
    """Return whether the run's heading is wholly in `shown_part`, above each value seen there.

    Each line the heading holds must lie wholly in `shown_part`. A value seen
    above its own run's heading would stand under the rows of the run above,
    and read as that run's value.
    """

    heading_bottom = run.heading.mapTo(page.viewport(), QPoint(0, 0)).y() + run.heading.height()

    return all(
        shown_part.contains(QRect(line.mapTo(page.viewport(), QPoint(0, 0)), line.size()))
        for line in _qualifiers(run)
    ) and all(
        value.top() >= heading_bottom for value in _seen_without_heading(page, run, shown_part)
    )


def _in_run(run: RunSchematic, widget: QWidget, rectangle: QRectF) -> QRectF:
    """Return `rectangle`, in `widget`'s pixels, in the pixels of the run's schematic."""

    return rectangle.translated(widget.mapTo(run, QPoint(0, 0)).toPointF())


@pytest.mark.parametrize(
    ("dial_percent", "branched", "size"),
    [(None, True, (1920, 1080)), (8.0, False, (1366, 768)), (None, False, (1366, 768))],
    ids=["two runs", "one run off the scale", "one run"],
)
def test_no_value_is_in_view_without_its_run_and_compartment_at_any_scroll_position(
    application: QApplication,
    shown: list[SimulationView],
    dial_percent: float | None,
    branched: bool,
    size: tuple[int, int],
) -> None:
    """`PL-3NGZ`: wherever a value of a run is in view, that run's whole heading is in view too.

    The Maintenance Workspace at 1366 by 768 gives the schematic an Area
    shorter than one run's schematic. At that size, two compared runs leave the
    schematic's box too short to show a whole row of containers, so the Area
    shows a notice in place of the View (`PL-GWTR`). At 1920 by 1080 the two
    runs share a box that shows a whole row and is shorter than both runs'
    schematics. The test scrolls the Area through every position. Wherever a container, a share bar
    or a line of a label is wholly in view and not under the heading, the
    heading is wholly in view too, and above that value. It holds the line
    that names the run and the instant, the share caption and the
    compartments' names. Before the
    heading was pinned, a scroll of the two runs' schematic showed a tension
    with neither its run nor its compartment named. The disclaimer, the
    tensions' unit and the amounts' unit with its condition stand above the
    scroll box, so they are in view at every position. At 8% the circuit is
    off the scale, which adds the off-scale
    line to the schematic. At every position each heading stays inside its own
    run's schematic, so it never covers the other run's rows.
    """

    view = _paused_dashboard(
        application, shown, _maintenance(), size, branched=branched, dial_percent=dial_percent
    )
    schematic = _schematic(view)
    scroll = _view_scroll(schematic)
    bar = scroll.verticalScrollBar()
    viewport = scroll.viewport().rect()

    assert len(schematic.schematics) == (2 if branched else 1)
    # The premise: the Area shows the schematic, and cannot hold all of it,
    # so the test scrolls.
    assert schematic.isVisible()
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
            qualifiers = [
                _in_viewport(scroll, line, QRectF(line.rect())) for line in _qualifiers(run)
            ]
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
                for qualifier in qualifiers:
                    assert viewport.contains(qualifier), (position, run.name_text.text())

            # A value seen above its own run's heading would stand under the
            # rows of the run above, and read as that run's value.
            for value in seen:
                assert value.top() >= heading.top() + heading.height(), (
                    position,
                    run.name_text.text(),
                )


#: What the schematic says under its axis top control while the top in force
#: is one the next launch will not open at. Written out by hand (`PL-GWSY`).
_UNSAVED_TOP_LINE = (
    "The application could not save this axis top, so it lasts only until the "
    "application closes. The Agent cost View says why."
)


class _RefusingStore(PreferencesStore):
    """A preferences store whose every save fails, as one on a full disk would."""

    def save(self, preferences: Preferences) -> Path:
        raise PreferencesFileError(f"the preferences could not be saved to {self.path}")


def test_the_line_under_the_axis_top_control_is_in_view_at_any_scroll_position(
    application: QApplication, shown: list[SimulationView], tmp_path: Path
) -> None:
    """`PL-B3M6`: a line that appears under the pinned axis top control is on screen with it.

    The Maintenance Workspace at 1920 by 1080 with two compared runs gives the
    schematic a box that scrolls. The test scrolls it to its end and then picks
    a top. Every save fails, so the top cannot be kept, and the line under the
    control says so. The line stands in the pinned row,
    outside the box, inside the window, and tall enough for every line of its
    text. The box keeps the place the reader scrolled to, and it is still tall
    enough to show a whole row of containers, so the View is still shown. The
    pinned row grows by the line's height while the line shows, and shrinks back
    when a top the next launch opens at clears it. Before the fix, the line
    stood at the top of the box's content, above the part in view.
    """

    view = _paused_dashboard(
        application,
        shown,
        _maintenance(),
        (1920, 1080),
        branched=True,
        preferences_store=_RefusingStore(tmp_path),
    )
    schematic = _schematic(view)
    scroll = _view_scroll(schematic)
    bar = scroll.verticalScrollBar()
    line = schematic.ceiling_notice
    row_height = schematic.pinned_row.height()

    # The premise: the box scrolls, and no line shows yet.
    assert bar.maximum() > 0
    assert line.isHidden()

    bar.setValue(bar.maximum())
    application.processEvents()
    scrolled_to = bar.value()
    high = schematic.ceiling_selector.findData(ChartCeiling.HIGH.name)
    schematic.ceiling_selector.setCurrentIndex(high)
    schematic.ceiling_selector.activated.emit(high)
    application.processEvents()

    assert line.text() == _UNSAVED_TOP_LINE
    assert line.isVisible()
    assert not scroll.isAncestorOf(line)
    assert view.rect().contains(QRect(line.mapTo(view, QPoint(0, 0)), line.size()))
    assert line.height() == line.heightForWidth(line.width())
    assert schematic.pinned_row.height() == row_height + VIEW_ROW_SPACING + line.height()
    assert bar.value() == scrolled_to
    assert view.layout_container.too_small() == ()
    assert schematic.isVisible()
    legible = schematic.legible_height()
    assert legible is not None and scroll.viewport().height() >= legible

    standard = schematic.ceiling_selector.findData(ChartCeiling.STANDARD.name)
    schematic.ceiling_selector.setCurrentIndex(standard)
    schematic.ceiling_selector.activated.emit(standard)
    application.processEvents()

    assert line.isHidden()
    assert schematic.pinned_row.height() == row_height


def test_an_area_too_short_for_the_line_under_the_axis_top_control_shows_the_too_small_notice(
    application: QApplication, shown: list[SimulationView], tmp_path: Path
) -> None:
    """`PL-B3M6`: the line under the axis top control counts in the height the schematic needs.

    The line stands in the row kept above the schematic's box, so while it
    shows, the box is shorter by the line and the gap above it. The test sizes
    a window that shows only the schematic so that its box is exactly tall
    enough for a run's heading and a whole row of containers without the line.
    A picked top that cannot be saved then shows the line, and the Area shows
    the too-small notice rather than containers that every scroll position
    would cut (`PL-GWTR`). The height the notice states grows by the gap above
    the line and the line's height at the width the row is drawn, measured here
    from the font. A top that the next launch opens at clears the line, and the
    schematic is shown again.
    """

    store = _RefusingStore(tmp_path)
    short = _paused_dashboard(
        application, shown, _SCHEMATIC_ONLY, (1366, 420), branched=False, preferences_store=store
    )
    (too_short,) = short.layout_container.too_small()
    window_height = 420 + too_short.needed.height_px - too_short.available.height_px
    view = _paused_dashboard(
        application,
        shown,
        _SCHEMATIC_ONLY,
        (1366, window_height),
        branched=False,
        preferences_store=store,
    )
    schematic = _schematic(view)
    line = schematic.ceiling_notice

    # The premise: without the line, the box is exactly tall enough.
    assert view.layout_container.too_small() == ()
    assert schematic.isVisible()

    high = schematic.ceiling_selector.findData(ChartCeiling.HIGH.name)
    schematic.ceiling_selector.setCurrentIndex(high)
    schematic.ceiling_selector.activated.emit(high)
    application.processEvents()

    text_width = schematic.pinned_row.width() - 2 * PANEL_PADDING
    line_height = (
        QFontMetrics(line.font())
        .boundingRect(QRect(0, 0, text_width, 1000), Qt.TextFlag.TextWordWrap, _UNSAVED_TOP_LINE)
        .height()
    )
    (too_small,) = view.layout_container.too_small()

    assert line.text() == _UNSAVED_TOP_LINE
    assert not schematic.isVisible()
    assert too_small.needed.height_px == (
        too_short.needed.height_px + VIEW_ROW_SPACING + line_height
    )

    standard = schematic.ceiling_selector.findData(ChartCeiling.STANDARD.name)
    schematic.ceiling_selector.setCurrentIndex(standard)
    schematic.ceiling_selector.activated.emit(standard)
    application.processEvents()

    assert view.layout_container.too_small() == ()
    assert schematic.isVisible()


def test_a_narrower_window_counts_the_rows_the_line_under_the_axis_top_control_takes_there(
    application: QApplication, shown: list[SimulationView], tmp_path: Path
) -> None:
    """`PL-B3M6`: after a resize, the Area counts the line at the width it is drawn.

    The preferences file holds a saved top that is long text, so the line under
    the axis top control, which quotes it, wraps onto a different number of
    rows at each width. The schematic's Area takes 70% of the window's width.
    The test sizes the window so that, at 1366 px wide, the box is exactly tall
    enough for a run's heading and a whole row of containers. Narrowing the
    window to 1136 px wraps the line onto more rows, so the box becomes too
    short, and the Area shows the too-small notice rather than containers
    that every scroll position would cut (`PL-GWTR`).
    """

    (tmp_path / PREFERENCES_FILE_NAME).write_text(
        json.dumps(
            {
                "schema_version": 2,
                "agent_cost_unit": "millilitres of liquid",
                "agent_prices": [],
                "chart_axis_top_mac": "a top typed by hand " * 8,
            }
        ),
        encoding="utf-8",
    )
    store = PreferencesStore(tmp_path)
    short = _paused_dashboard(
        application,
        shown,
        _SCHEMATIC_AND_BRANCH,
        (1366, 420),
        branched=False,
        preferences_store=store,
    )
    (too_short,) = short.layout_container.too_small()
    window_height = 420 + too_short.needed.height_px - too_short.available.height_px
    view = _paused_dashboard(
        application,
        shown,
        _SCHEMATIC_AND_BRANCH,
        (1366, window_height),
        branched=False,
        preferences_store=store,
    )
    schematic = _schematic(view)
    line = schematic.ceiling_notice
    wide_rows = line.height()

    # The premise: the line shows, and the box is exactly tall enough.
    assert line.text().startswith('The saved axis top, "a top typed by hand')
    assert view.layout_container.too_small() == ()
    assert schematic.isVisible()

    view.resize(1136, window_height)
    application.processEvents()

    # The premise: at the narrower width the line takes more rows.
    assert line.heightForWidth(schematic.pinned_row.width() - 2 * PANEL_PADDING) > wide_rows
    assert len(view.layout_container.too_small()) == 1
    assert not schematic.isVisible()


# How far the line that marks a container above the scale reaches past the
# container's top: half its 4 px width, restated from `app/qt_schematic.py`.
_OFF_SCALE_REACH_PX = 2
# An Area's header row and the 1 px rule under it, which the too-small notice
# leaves out of the size it gives, restated as `tests/integration/test_layout_adapter.py`
# measures them.
_AREA_CHROME_PX = 27


def test_a_box_too_short_for_a_row_of_containers_shows_a_notice_in_place_of_the_schematic(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """`PL-GWTR`: where every scroll position would cut each container, no container is drawn.

    In the Maintenance Workspace at 1366 by 768, a branch adds the second run's
    row to the parameter controls, and the page then scrolls. Each Area is then
    held at its need, which leaves the schematic's box shorter than a run's
    heading and its row of containers. So the Area shows the too-small notice
    in place of the View. The height it states is worked out here: the row kept
    above the box, the run's heading, and the canvas down to the containers'
    lower edge, past which the line over a container above the scale reaches
    2 px. No border can give the Area that height while the page scrolls, so
    the notice says to make the window taller. At 1920 by 1080 the box is tall
    enough, and the schematic is shown.
    """

    view = _paused_dashboard(application, shown, _maintenance(), (1366, 768), branched=True)
    schematic = _schematic(view)
    run = schematic.schematics[0]
    (too_small,) = view.layout_container.too_small()
    frame = view.layout_container.frame(too_small.area_id)
    notice = frame.too_small_notice
    needed = (
        schematic.pinned_row.sizeHint().height()
        + run.heading.sizeHint().height()
        + _CONTAINER_TOP_PX
        + _CONTAINER_HEIGHT_PX
        + _OFF_SCALE_REACH_PX
    )
    has = frame.height() - _AREA_CHROME_PX

    # The premise: the page scrolls, so every Area is held at its need.
    assert view._page_scroll.verticalScrollBar().maximum() > 0
    assert too_small.needed.height_px == needed + _AREA_CHROME_PX
    assert not schematic.isVisible()
    assert notice is not None and notice.isVisible()
    assert [notice.title_label.text(), notice.body_label.text()] == [
        "Too small for Compartment schematic.",
        f"It needs at least {too_small.needed.width_px} by {needed} px; this Area is "
        f"{frame.width()} by {has}. Make the window taller, or choose a smaller View from "
        "the menu above.",
    ]

    wide = _paused_dashboard(application, shown, _maintenance(), (1920, 1080), branched=True)

    assert wide.layout_container.too_small() == ()
    assert _schematic(wide).isVisible()


def _clear_part(scroll: ViewScroll, run: RunSchematic) -> QRect:
    """Return the part of the run's canvas in the box's view and below the heading, in its pixels.

    It is worked out here from where the box, the heading and the canvas stand,
    apart from the code under test.
    """

    viewport = scroll.viewport()
    corner = run.canvas.mapTo(viewport, QPoint(0, 0))
    shown_part = QRect(corner, run.canvas.size()).intersected(viewport.rect())
    shown_part.setTop(
        max(shown_part.top(), run.heading.mapTo(viewport, QPoint(0, 0)).y() + run.heading.height())
    )

    if shown_part.height() <= 0:
        return QRect()

    return shown_part.translated(-corner)


def _whole_in(clear: QRect, part: QRectF, reach: float = 0.0, *, across: bool = False) -> bool:
    """Return whether `part`, widened by `reach` px above and below, lies within `clear`'s rows.

    With `across`, `part` must lie within `clear`'s columns too.
    """

    return (
        not clear.isEmpty()
        and clear.top() <= part.top() - reach
        and part.bottom() + reach <= clear.top() + clear.height()
        and (
            not across
            or (clear.left() <= part.left() and part.right() <= clear.x() + clear.width())
        )
    )


def _middle_row(image: QImage, part: QRectF) -> set[int]:
    """Return the colours along the middle row of `part` in `image`."""

    row = int(part.center().y())

    return {
        image.pixel(x, row)
        for x in range(max(int(part.left()), 0), min(int(part.right()), image.width()))
    }


def test_no_container_label_line_or_share_bar_is_painted_cut_at_any_scroll_position(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """`PL-GWTR`: each part of the schematic is painted only while it is whole in view.

    A container shows its tension as the height of its fill, so a container
    cut by a run's heading or by the box's edge could look full, or empty, at a
    tension it does not hold. A cut line of a label could be read as other
    digits. In the Maintenance Workspace at 1920 by 1080, two compared runs
    share a box shorter than both. The test scrolls the box through every
    position and works out, for each run, the part of the canvas in view and
    not under the heading. The six containers must be painted only while all of
    them are whole there, with the 2 px by which the line over a container
    above the scale reaches past its top. Each label line and share bar must be
    painted only while it is whole there. The test then reads the painted
    pixels. A container that is not painted shows none of its compartment's
    colour down its middle. A label line or a share bar that is not painted is
    one colour along its middle row. Where the containers are not painted, the
    line that says why may be painted, in the clear part and above the labels.
    """

    view = _paused_dashboard(application, shown, _maintenance(), (1920, 1080), branched=True)
    schematic = _schematic(view)
    scroll = _view_scroll(schematic)
    bar = scroll.verticalScrollBar()
    columns = range(len(_NAMES))
    states = {"containers painted": 0, "containers hidden, line painted": 0, "a line hidden": 0}

    # The premise: the schematic is shown, the whole box is in the page's
    # view, and the box scrolls.
    assert schematic.isVisible()
    assert _shown_part(view._page_scroll, scroll).size() == scroll.viewport().size()
    assert bar.maximum() > 0

    for position in range(bar.maximum() + 1):
        bar.setValue(position)
        application.processEvents()

        for run in schematic.schematics:
            canvas = run.canvas
            clear = _clear_part(scroll, run)
            parts = canvas.shown_parts()
            image = canvas.grab().toImage()
            containers = all(
                _whole_in(clear, canvas.container(index), _OFF_SCALE_REACH_PX) for index in columns
            )
            where = (position, run.name_text.text())

            assert parts.containers is containers, where
            assert parts.lines == {
                (index, line)
                for index in columns
                for line in range(3)
                if _whole_in(clear, canvas.label_line(index, line), across=True)
            }, where
            assert parts.bars == {
                index for index in columns if _whole_in(clear, canvas.share_bar(index), across=True)
            }, where

            for index, reading in enumerate(canvas.readings):
                colour = QColor(trace_style(reading.quantity).color).rgb()
                fill = range(_CONTAINER_TOP_PX, _CONTAINER_TOP_PX + _CONTAINER_HEIGHT_PX + 1)
                filled = any(image.pixel(_column_centre(canvas, index), y) == colour for y in fill)
                assert containers or not filled, (*where, reading.name)

                for line in range(3):
                    if (index, line) not in parts.lines:
                        assert len(_middle_row(image, canvas.label_line(index, line))) == 1, where

                if index not in parts.bars:
                    assert len(_middle_row(image, canvas.share_bar(index))) == 1, where

            if parts.cut_notice is not None:
                assert not containers, where
                assert clear.contains(parts.cut_notice.toAlignedRect()), where
                assert parts.cut_notice.bottom() <= canvas.label_line(0, 0).top(), where
                assert len(_middle_row(image, parts.cut_notice)) > 1, where

            states["containers painted"] += containers
            states["containers hidden, line painted"] += parts.cut_notice is not None
            states["a line hidden"] += len(parts.lines) < 3 * len(_NAMES)

    # The premise: the scroll reached each state at least once.
    assert all(states.values()), states


def test_a_canvas_paints_each_part_only_while_its_clear_part_holds_it_whole(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """`PL-GWTR`: the canvas paints the parts that the clear part it is given holds whole.

    Each canvas here is given one run's readings, at the size the run's own
    canvas has, and a fixed clear part. A canvas that nobody measures, or one
    whose clear part is all of it, paints every part. The containers stand from
    14 px down, and the line over a container above the scale reaches 2 px
    above them, so a clear part from 12 px down shows them and one from 13 px
    hides them. A clear part from 20 px puts the line that says why they are
    hidden at its top, above the labels. An edge across a label line hides
    that line in every column. A space too short for the line paints neither
    the containers nor the line. An edge at a side hides each label line and
    share bar that it crosses, because a line cut there loses digits, but not
    the containers, whose fills keep their heights.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 10 * SECONDS_PER_MINUTE)
    controller.pause()
    source = _schematic(_dashboard(application, shown, controller)).schematics[0].canvas
    width, height = source.width(), source.height()
    every_line = frozenset((index, line) for index in range(6) for line in range(3))
    every_bar = frozenset(range(6))

    source_shown = source.shown
    assert source_shown is not None

    def measured(clear: QRect | None) -> CanvasParts:
        canvas = SchematicCanvas()
        canvas.show_schematic(source_shown, None)
        canvas.resize(source.size())

        if clear is not None:
            canvas.measure_clear_part(lambda: clear)

        return canvas.shown_parts()

    assert SchematicCanvas().shown_parts() == CanvasParts(False, frozenset(), frozenset(), None)

    for clear in (None, QRect(0, 0, width, height)):
        assert measured(clear) == CanvasParts(True, every_line, every_bar, None)

    assert measured(QRect(0, 12, width, height - 12)).containers
    assert not measured(QRect(0, 13, width, height - 13)).containers

    hidden = measured(QRect(0, 20, width, height - 20))

    assert (hidden.containers, hidden.lines, hidden.bars) == (False, every_line, every_bar)
    assert hidden.cut_notice is not None
    assert hidden.cut_notice.top() == 20
    assert hidden.cut_notice.bottom() <= source.label_line(0, 0).top()

    top = int(source.label_line(0, 0).top()) + 3
    first_cut = measured(QRect(0, top, width, height - top))

    assert first_cut.lines == every_line - {(index, 0) for index in range(6)}
    assert first_cut.cut_notice is None

    bottom = int(source.label_line(0, 1).bottom()) - 2

    assert measured(QRect(0, 0, width, bottom)) == CanvasParts(
        True, frozenset((index, 0) for index in range(6)), frozenset(), None
    )

    # A cut at a side hides the lines and the bar it crosses, and leaves the
    # containers, whose fills keep their heights.
    last_column = frozenset((5, line) for line in range(3))
    first_column = frozenset((0, line) for line in range(3))

    assert measured(QRect(0, 0, width - 1, height)) == CanvasParts(
        True, every_line - last_column, every_bar, None
    )
    assert measured(QRect(0, 0, int(source.share_bar(5).right()) - 1, height)) == CanvasParts(
        True, every_line - last_column, every_bar - {5}, None
    )
    assert measured(QRect(1, 0, width - 1, height)) == CanvasParts(
        True, every_line - first_column, every_bar, None
    )

    too_short = measured(QRect(0, 100, width, 10))

    assert not too_short.containers
    assert too_short.cut_notice is None
    assert measured(QRect()) == CanvasParts(False, frozenset(), frozenset(), None)


@pytest.mark.parametrize(
    ("workspaces", "size", "branched"),
    [
        (_maintenance(), (1920, 1080), True),
        (_SCHEMATIC_ONLY, (_WINDOW_WIDTH_PX, _WINDOW_HEIGHT_PX), False),
    ],
    ids=["two runs at 1920 by 1080", "one run, wide"],
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
    # The premise: the Area shows the schematic, not the notice that stands in
    # its place in a box too short for a row of containers (`PL-GWTR`).
    assert _schematic(view).isVisible()

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


def _with_text_alone(widget: QWidget, painted: QImage, cell: QRectF, text: str) -> QImage:
    """Return `painted` with `cell` cleared to its background and `text` painted alone in it.

    The text is centred at the top of the cell, in `widget`'s font and in
    `INK`, as `widget` paints each string. So the result is what `widget` would
    show if `cell` held `text`. The cell's corner is clear of its text, so its
    pixel is the background.
    """

    image = painted.copy()
    area = cell.toAlignedRect().intersected(image.rect())
    painter = QPainter(image)
    painter.fillRect(area, image.pixelColor(area.topLeft()))
    painter.setFont(widget.font())
    painter.setPen(QColor(INK))
    painter.drawText(cell, int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop), text)
    painter.end()

    return image


def _distance(first: QImage, second: QImage, area: QRect) -> int:
    """Return the sum, over `area`, of the absolute differences of the two images' colour bytes."""

    one = first.copy(area).convertToFormat(QImage.Format.Format_RGB32)
    two = second.copy(area).convertToFormat(QImage.Format.Format_RGB32)

    return sum(
        abs(a - b) for a, b in zip(bytes(one.constBits()), bytes(two.constBits()), strict=True)
    )


def test_each_name_and_label_line_is_painted_in_its_own_container_s_column(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """`PL-Q740`: the pixels of each name and each label line are that string, in its own cell.

    `test_each_compartment_name_stands_over_its_own_container` compares the
    cells that `name_cell` and `container` return, and nothing there reads
    where the strings are painted. So a name or a tension painted in another
    container's cell would put "Fat", or another compartment's tension, over
    the circuit with every rectangle still right. This test reads the painted
    pixels of each cell. It clears the cell and paints in it, alone, each
    string of the cell's row in turn, and also nothing. The painted cell must
    be nearest to the one painted with the string that belongs there. Every
    string shown here differs from the others in its row, so a string painted
    in another container's cell is nearer to that string, and an empty cell is
    nearer to nothing. The cell is held to the nearest string, not to an exact
    copy, because an exact copy failed on CI's ARM runners. There the widget's
    own painting and the test's differ, which they do not in the x86
    development container.
    """

    view = _paused_dashboard(
        application, shown, _SCHEMATIC_ONLY, (_WINDOW_WIDTH_PX, _WINDOW_HEIGHT_PX), branched=False
    )
    run = _schematic(view).schematics[0]
    labels = run.canvas.painted_strings()
    placed: list[tuple[QWidget, QRectF, str]] = [
        (run.names, run.names.name_cell(index), name) for index, name in enumerate(_NAMES)
    ]
    placed += [
        (run.canvas, run.canvas.label_line(index, line), labels[index * 3 + line])
        for index in range(len(_NAMES))
        for line in range(3)
    ]
    painted: dict[QWidget, QImage] = {
        widget: widget.grab().toImage() for widget in (run.names, run.canvas)
    }

    rows = [_NAMES] + [
        tuple(labels[index * 3 + line] for index in range(len(_NAMES))) for line in range(3)
    ]

    # The premise: no two strings in a row are the same, so each cell's pixels
    # tell its string from every other in the row.
    for row in rows:
        assert len(set(row)) == len(row), row

    for position, (widget, cell, text) in enumerate(placed):
        image = painted[widget]
        area = cell.toAlignedRect().intersected(image.rect())
        # The names come first, one row of six, then each container's three lines.
        row = rows[0] if position < len(_NAMES) else rows[1 + (position - len(_NAMES)) % 3]
        distances = {
            candidate: _distance(image, _with_text_alone(widget, image, cell, candidate), area)
            for candidate in (*row, "")
        }

        assert min(distances, key=lambda candidate: distances[candidate]) == text, (text, distances)


def test_a_run_heading_follows_a_scroll_of_the_page(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """`PL-3NGZ`: wherever the page's scroll leaves a run's value in view, its heading is in view.

    A window shorter than the dashboard scrolls the whole page, Areas and
    all. The schematic's Area is here at the top of a window 500 px tall,
    beside the parameter controls and over the bookmarks' Area, so a page
    scroll carries the top of its box, and the heading pinned there, above
    the page's edge. For each run, the test scrolls the
    box until a container, a share bar or a line of a label stands just
    under the heading pinned at the box's top. It then scrolls the page
    through every position. Wherever a value is wholly in view and not under
    the heading, the heading is wholly in view too, and above that value.
    Before the page's scroll
    moved the headings, the heading stayed where the box's last scroll put
    it, and went above the page's edge while the value under it stayed in
    view.
    """

    view = _paused_dashboard(
        application, shown, _SCHEMATIC_OVER_BOOKMARKS, (_WINDOW_WIDTH_PX, 500), branched=True
    )
    page = view._page_scroll
    schematic = _schematic(view)
    scroll = _view_scroll(schematic)
    page_bar = page.verticalScrollBar()
    box_bar = scroll.verticalScrollBar()

    # The premise: the page scrolls far enough to take the top of the
    # schematic's box out of view, and the box shows the schematic and scrolls.
    page_bar.setValue(0)
    application.processEvents()
    assert page_bar.maximum() > scroll.viewport().mapTo(page.viewport(), QPoint(0, 0)).y()
    assert schematic.isVisible()
    assert box_bar.maximum() > 0

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

    With the bookmarks over the schematic and the parameter controls, in a
    window 1400 by 500 px with a branch open, the page scrolls. The page is
    scrolled to its end, as a reader scrolls it. In a Workspace that shows the
    concentration chart, that ends the hold on the chart that a branch begins,
    so no later change of the page's range scrolls the page to the chart. The
    schematic's box is scrolled until the first run's tension line stands
    just under the heading, and the page is scrolled back to its top, which
    takes the schematic's Area below the window's lower edge. No part of
    either section is then in view, so each heading stands at its section's
    top. The window is then made as tall as it can be while the page still
    scrolls, which brings the box back into view. While the page scrolls, its
    Areas keep their least heights, so the box keeps its size. The test checks
    that the resize scrolls neither the page nor the box and leaves the box's
    size as it was, and the run is paused, so no drawn frame moves a heading
    either. Wherever a value is then seen, its run's heading is wholly
    in view, and above that value. Before a change of the page's scroll
    range moved the headings, the first run's six tensions were in view with
    its heading above the box's top edge.
    """

    view = _paused_dashboard(
        application, shown, _BOOKMARKS_OVER_SCHEMATIC, (_WINDOW_WIDTH_PX, 500), branched=True
    )
    page = view._page_scroll
    schematic = _schematic(view)
    scroll = _view_scroll(schematic)
    first = schematic.schematics[0]
    page_bar = page.verticalScrollBar()
    box_bar = scroll.verticalScrollBar()

    # `triggerAction` reports the scroll through `actionTriggered`, as the
    # wheel, the keys and the bar do, so it ends the hold on the chart.
    page_bar.triggerAction(QAbstractSlider.SliderAction.SliderToMaximum)
    application.processEvents()
    box_bar.setValue(
        first.mapTo(schematic, QPoint(0, 0)).y()
        + first.canvas.mapTo(first, first.canvas.label_line(0, 0).topLeft().toPoint()).y()
        - first.heading.height()
    )
    application.processEvents()
    page_bar.triggerAction(QAbstractSlider.SliderAction.SliderToMinimum)
    application.processEvents()

    # The premise: the Area shows the schematic, and the page's scroll has
    # taken the whole box out of view.
    assert not schematic.isHidden()
    assert _shown_part(page, scroll).isEmpty()
    before = (page_bar.value(), box_bar.value(), scroll.viewport().size())

    # The page's viewport grows with the window, so this leaves the page one
    # pixel to scroll.
    view.resize(_WINDOW_WIDTH_PX, 500 + page_bar.maximum() - 1)
    application.processEvents()
    shown_part = _shown_part(page, scroll)

    # The premise: the taller window scrolled neither the page nor the box and
    # left the box's size as it was. A scroll or a resize would move the
    # headings by itself, so only the change of the page's range can have.
    assert page_bar.maximum() == 1
    assert (page_bar.value(), box_bar.value(), scroll.viewport().size()) == before

    # The premise: the taller window shows the schematic and the first run's
    # values again.
    assert schematic.isVisible()
    assert _seen_without_heading(page, first, shown_part)

    for run in schematic.schematics:
        if _seen_without_heading(page, run, shown_part):
            assert _heading_in_view(page, run, shown_part), run.name_text.text()


def test_a_page_scrolled_sideways_hides_each_label_line_and_share_bar_it_cuts(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """`PL-GWTR`: a column cut at the window's side shows no part of its label or share bar.

    In the Maintenance Workspace at 1280 by 1080 with one run, the page is
    wider than the window and scrolls sideways, and the schematic is in the
    right-hand column. With the page at its left end, the window's right edge
    runs through the last containers' columns. A tension cut there could read
    as a smaller number, and a share bar cut at its right end could read as a
    larger share. The part of each label line and share bar in view is worked
    out here from where the page, the box and the canvas stand. Each must be
    painted only while it is whole in view, at both ends of the page's scroll.
    """

    view = _paused_dashboard(application, shown, _maintenance(), (1280, 1080), branched=False)
    schematic = _schematic(view)
    (run,) = schematic.schematics
    canvas = run.canvas
    scroll = _view_scroll(schematic)
    page = view._page_scroll
    sideways = page.horizontalScrollBar()
    columns = range(len(_NAMES))

    # The premise: the schematic is shown and the page scrolls sideways.
    assert schematic.isVisible()
    assert sideways.maximum() > 0

    hidden_at_left = None

    for position in (0, sideways.maximum()):
        sideways.setValue(position)
        application.processEvents()
        corner = canvas.mapTo(page.viewport(), QPoint(0, 0))
        on_page = QRect(corner, canvas.size()).intersected(page.viewport().rect())
        clear = _clear_part(scroll, run).intersected(on_page.translated(-corner))
        parts = canvas.shown_parts()
        lines = {
            (index, line)
            for index in columns
            for line in range(3)
            if _whole_in(clear, canvas.label_line(index, line), across=True)
        }
        bars = {
            index for index in columns if _whole_in(clear, canvas.share_bar(index), across=True)
        }

        assert parts.lines == lines, position
        assert parts.bars == bars, position

        if position == 0:
            hidden_at_left = len(columns) * 3 - len(lines)

    # The premise: at the page's left end the window's edge cuts a column.
    assert hidden_at_left is not None and hidden_at_left > 0


def test_the_hidden_containers_line_is_listed_with_each_run_s_strings(
    application: QApplication, shown: list[SimulationView]
) -> None:
    """`PL-GWTR`: the interface's wording test can read the line that replaces cut containers.

    The canvas paints the line itself, so no label holds it. Each run's
    schematic lists it once, after its names and labels, at every scroll
    position, as it lists the labels. So the dashboard's strings hold it, and
    a change to its words fails the wording test until it is approved.
    """

    view = _paused_dashboard(application, shown, _maintenance(), (1920, 1080), branched=True)
    schematic = _schematic(view)

    for run in schematic.schematics:
        assert run.painted_strings()[-1] == CUT_CONTAINERS_TEXT
        assert run.painted_strings().count(CUT_CONTAINERS_TEXT) == 1

    assert view.interface_strings().count(CUT_CONTAINERS_TEXT) == len(schematic.schematics)


def test_each_move_of_a_run_heading_asks_its_canvas_to_repaint(
    application: QApplication, shown: list[SimulationView], monkeypatch: pytest.MonkeyPatch
) -> None:
    """`PL-GWTR`: a scroll that moves a run's heading asks that run's canvas to paint again.

    On a platform that scrolls by copying the pixels already painted, a
    container painted whole before a scroll would stay painted after the
    scroll had slid the heading over its top, until something else repainted
    it. So each move of a heading asks its canvas to paint again, and the
    canvas then paints from its clear part as it is. The offscreen platform
    the tests run on repaints the whole widget after a scroll, measured on
    2026-11-28, so no pixel there can show the stale case. The test therefore
    counts the canvas's requests to paint while the box scrolls by 3 px in the
    Maintenance Workspace at 1920 by 1080 with two runs.
    """

    view = _paused_dashboard(application, shown, _maintenance(), (1920, 1080), branched=True)
    schematic = _schematic(view)
    bar = _view_scroll(schematic).verticalScrollBar()
    bar.setValue(bar.maximum() // 2)
    application.processEvents()
    requests = {id(run.canvas): 0 for run in schematic.schematics}

    for run in schematic.schematics:

        def count(canvas_id: int = id(run.canvas)) -> None:
            requests[canvas_id] += 1

        monkeypatch.setattr(run.canvas, "update", count)

    bar.setValue(bar.value() + 3)
    application.processEvents()

    assert all(requests.values()), requests
