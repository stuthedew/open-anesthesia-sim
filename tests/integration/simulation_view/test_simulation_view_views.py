"""The dashboard, driven headless against real runs.

These tests cover the Views a Workspace places in the dashboard.

`simulation_view_support.py` describes the whole suite.
"""

from collections.abc import Callable, Mapping
from typing import Final, NoReturn

import pytest
from PySide6.QtWidgets import QAbstractButton, QApplication, QComboBox, QLabel, QWidget

from anesthesia_sim.app import run_presentation as run_presentation_module
from anesthesia_sim.app import simulation_view as simulation_view_module
from anesthesia_sim.app.bookmarks import TimeBookmark
from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import (
    BRANCH_RUN_INDEX,
    FORK_NOTHING_SELECTED_TEXT,
    SIMULATION_STEP_S,
    STATUS_FAILED_TEXT,
    TRUNK_RUN_INDEX,
    run_label,
    slider_position,
)
from anesthesia_sim.app.formatting import (
    CONCENTRATION_DISPLAY_DECIMALS,
    FLOW_DISPLAY_DECIMALS,
    format_flow,
)
from anesthesia_sim.app.qt_widgets import BookmarksPanel, ForkPanel, ParameterSlider
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.app.run_surfaces import AccountingPanel, ParameterControls
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.view_contract import ViewTick
from anesthesia_sim.app.view_registry import (
    AGENT_ACCOUNTING,
    AGENT_COST,
    BOOKMARKS,
    BRANCH,
    COMPARTMENT_SCHEMATIC,
    CONCENTRATION_CHART,
    PARAMETER_CONTROLS,
    REGISTERED,
)
from anesthesia_sim.app.views import (
    AccountingView,
    AgentCostView,
    BookmarksView,
    BranchView,
    CompartmentSchematicView,
    ConcentrationView,
    ParameterControlsView,
)
from anesthesia_sim.core import supported_ranges as supported_ranges_module
from anesthesia_sim.core.supported_ranges import CaseInstant
from anesthesia_sim.layout.run_identity import RunId
from anesthesia_sim.layout.tree import AreaId, ViewKind
from tests.integration.simulation_view.simulation_view_support import (
    _CARDIAC_OUTPUT_REFUSED_ON_A_STOPPED_RUN,
    _RUN_PANEL_VIEWS,
    _accounting,
    _accounting_reading,
    _advance,
    _branched_case,
    _case_view,
    _concentration,
    _dial_readings,
    _dials,
    _drag,
    _failing_assembly,
    _fork_panel,
    _halted_trunk_case,
    _marks_panel,
    _no_setting,
    _paused_run_with_history,
    _setting_controls,
    _settle,
    _shown_view,
    _strings_of,
    _take_fork,
    _wash_in,
    _withheld_accounting,
)


def _run_named_on(line: str) -> str | None:
    """The run that a schematic's or a cost panel's first line names, or None if it names none."""

    name, named, _ = line.partition(", at ")

    return name if named else None


def _runs_named_in_the_views(view: SimulationView) -> dict[str, list[str | None]]:
    """What each of the three Views calls each run it shows, in drawing order."""

    views = view.layout_container.views()
    (accounting,) = (shown for shown in views if isinstance(shown, AccountingView))
    (schematic,) = (shown for shown in views if isinstance(shown, CompartmentSchematicView))
    (cost,) = (shown for shown in views if isinstance(shown, AgentCostView))

    return {
        "accounting": [panel._accounting_heading_text.text() for panel in accounting.panels],
        "schematic": [_run_named_on(drawn.name_text.text()) for drawn in schematic.schematics],
        "agent cost": [_run_named_on(panel.name_text.text()) for panel in cost.panels],
    }


@pytest.mark.parametrize("frames_fail", [False, True], ids=["frames draw", "every frame fails"])
def test_the_views_name_each_run_while_two_are_drawn_and_only_then(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, frames_fail: bool
) -> None:
    """Each View names both runs once a branch is drawn, and no run once Reset drops it.

    Renaming the runs draws nothing (`PL-B1R9`). A View names a run from the
    run's presentation, so it shows a new name on the tick that follows the
    change to the run set. That tick is a drawn frame. While every frame
    fails, it is the halt that the failed frame causes, which hands every
    View the runs with no frame (`PL-RF2S`). The branch is added with no
    frame asked for, so the render tick is what draws it. Then the trunk's
    Reset drops the branch. Each name is written out by hand.
    """

    case = _branched_case()
    view = _shown_view(application, case.trunk, case=case, workspaces=_RUN_PANEL_VIEWS)
    lone: dict[str, list[str | None]] = {
        "accounting": ["Agent accounting validation"],
        "schematic": [None],
        "agent cost": [None],
    }
    assert _runs_named_in_the_views(view) == lone
    branch = case.fork_here()

    if frames_fail:
        monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    view.add_run(branch)
    view.render_tick()
    _settle(application)

    assert case.trunk.has_failed is frames_fail
    assert _runs_named_in_the_views(view) == {
        "accounting": [
            "Agent accounting validation \u2014 Run 1",
            "Agent accounting validation \u2014 Run 2",
        ],
        "schematic": ["Run 1", "Run 2"],
        "agent cost": ["Run 1", "Run 2"],
    }

    trunk = view.runs[TRUNK_RUN_INDEX]
    trunk._reset_button.click()
    dialog = trunk._reset_dialog

    if dialog is not None:
        dialog.discard_button.click()

    _settle(application)

    assert len(view.runs) == 1
    assert case.trunk.has_failed is frames_fail
    assert _runs_named_in_the_views(view) == lone


def _run_widgets_by_view(view: SimulationView) -> dict[str, tuple[QWidget, tuple[QWidget, ...]]]:
    """Each View that shows something for each run, with the View and its widget for each run."""

    accounting = _accounting(view)
    controls = _setting_controls(view)
    concentration = _concentration(view)
    wash_in = _wash_in(view)

    return {
        "accounting": (accounting, accounting.panels),
        "setting controls": (controls, controls.rows),
        "off-scale": (concentration, concentration.off_scale.lines),
        "unmarked changes": (concentration, concentration.unmarked_changes.lines),
        "wash-in state": (wash_in, wash_in.states.lines),
        "wash-in unmarked changes": (wash_in, wash_in.unmarked_changes.lines),
    }


def test_each_view_places_one_widget_per_run_inside_itself(application: QApplication) -> None:
    """A View shows its widget for each run in its own rectangle (`PL-TH35`).

    Each run's panel names the run (`PL-C3GS`). A widget built for a run and
    never placed would not be seen, so this test checks that each one is
    inside its View.
    """

    view = _case_view(application, _branched_case())
    _take_fork(view, 60.0)
    _settle(application)

    assert len(view.runs) == 2

    for name, (shown_in, widgets) in _run_widgets_by_view(view).items():
        assert len(widgets) == 2, f"{name}: {len(widgets)} widgets for 2 runs"

        for widget in widgets:
            assert shown_in.isAncestorOf(widget), f"{name}: a run's widget is outside its View"

    for panel in _accounting(view).panels:
        assert panel.isVisible(), "an accounting panel is not shown"


def test_a_branch_dropped_while_frames_fail_leaves_no_widget_in_any_view(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A Reset that drops the branch takes its widgets away even when no frame can be drawn.

    A View drops a run's widget on the first tick that no longer names the
    run. When only a drawn frame brought a tick, and every frame failed, the
    branch's accounting panel stayed on screen with the status "Valid",
    beside the halted trunk, after the branch was gone. The halt now hands
    every View the runs that are left (`PL-RF2S`). The dashboard is searched
    for dials and accounting panels too, so a widget that a View no longer
    lists but still holds fails here.
    """

    view = _case_view(application, _branched_case())
    _take_fork(view, 60.0)
    _settle(application)
    assert len(view.findChildren(ParameterControls)) == 2
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    view.runs[0]._reset_button.click()
    _settle(application)

    assert len(view.runs) == 1
    assert view.runs[0].controller.has_failed is True

    for name, (_, widgets) in _run_widgets_by_view(view).items():
        assert len(widgets) == 1, f"{name}: the dropped branch's widget is still shown"

    assert len(view.findChildren(ParameterControls)) == 1
    assert len(view.findChildren(AccountingPanel)) == 1


def _no_tick_without_a_frame(tick: ViewTick) -> NoReturn:
    """Stand in for a View's `refresh` in a test where the View raises on a halt's tick.

    The tests that use it make every frame fail, so the only tick that
    reaches a View is the one a halt hands it, which has no frame.
    """

    assert tick.frame is None, "a frame was drawn in a test where every frame must fail"

    raise RuntimeError("this View could not show the tick")


def test_a_view_that_raises_on_a_halt_leaves_no_dropped_branch_in_the_views_after_it(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One View that raises on a halt's tick does not stop the Views after it learning of the halt.

    Every frame fails, so the halt's tick is the only thing that tells a
    View which runs are left. The concentration chart raises on that tick.
    One setting controls View sits before the chart in reading order. A
    second one, the accounting View, the schematic View and the agent cost
    View sit after it. The trunk's Reset then drops the branch. When the
    Views after the chart were handed nothing, they went on showing Run 2's
    dials and panels, and the name "Run 1", beside a dashboard that held one
    unnamed run at 0 s (blind review of `PL-RF2S`).

    Each View after the chart must show what the View before it shows: one
    run, not named, with its values withheld, because the run has started
    over and no frame has drawn since. Each expected text is written out by
    hand, or is the withheld form that `dashboard_frame` gives.
    """

    case = _branched_case()
    view = _case_view(application, case)

    for area, kind in ((3, PARAMETER_CONTROLS), (5, COMPARTMENT_SCHEMATIC), (6, AGENT_COST)):
        view.layout_container.choose_view(AreaId(area), kind)
        _settle(application)

    view.add_run(case.fork_here())
    view.render_tick()
    _settle(application)
    views = view.layout_container.views()
    kinds = [type(shown) for shown in views]
    assert kinds == [
        ParameterControlsView,
        ConcentrationView,
        ParameterControlsView,
        AccountingView,
        CompartmentSchematicView,
        AgentCostView,
    ]
    before_the_chart, chart, after_the_chart, accounting_view, schematic, cost = views
    assert isinstance(before_the_chart, ParameterControlsView)
    assert isinstance(after_the_chart, ParameterControlsView)
    assert isinstance(accounting_view, AccountingView)
    assert isinstance(schematic, CompartmentSchematicView)
    assert isinstance(cost, AgentCostView)
    assert len(after_the_chart.rows) == len(accounting_view.panels) == 2
    assert len(schematic.schematics) == len(cost.panels) == 2
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    monkeypatch.setattr(chart, "refresh", _no_tick_without_a_frame)

    trunk = view.runs[TRUNK_RUN_INDEX]
    trunk._reset_button.click()
    dialog = trunk._reset_dialog

    if dialog is not None:
        dialog.discard_button.click()

    _settle(application)

    assert len(view.runs) == 1
    assert trunk.controller.has_failed is True
    assert trunk.snapshot().elapsed_s == 0.0
    assert len(before_the_chart.rows) == 1
    assert len(after_the_chart.rows) == 1, "the dropped branch's dials are still shown"
    assert _dial_readings(after_the_chart.rows[0]) == _dial_readings(before_the_chart.rows[0])
    assert [panel._accounting_heading_text.text() for panel in accounting_view.panels] == [
        "Agent accounting validation"
    ]
    assert _accounting_reading(accounting_view.panels[0]) == _withheld_accounting()
    assert [_run_named_on(drawn.name_text.text()) for drawn in schematic.schematics] == [None]
    assert [_run_named_on(panel.name_text.text()) for panel in cost.panels] == [None]
    assert len(view.findChildren(ParameterControls)) == 2, "one row of dials for each of two Views"
    assert len(view.findChildren(AccountingPanel)) == 1


def test_a_view_that_raises_on_a_halt_hides_neither_a_run_s_halt_nor_the_first_exception(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A View that raises on a halt's tick hides neither a run's halt nor the first exception.

    Every frame fails, and neither of two runs can build its dials. Each
    run shows its halt and then raises, because its dials could not be
    built. The concentration chart then raises on the halt's tick. Each run
    must still show its halt. The exception that reaches the caller must be
    the first one, the first run's, so that the console names the earliest
    cause (`PL-TLH4`). The View after the chart is still handed the tick, so
    it shows the line that stands in place of each run's dials.
    """

    first, second = SimulationController(), SimulationController()
    view = _shown_view(application, first, second)
    view.layout_container.choose_view(AreaId(3), PARAMETER_CONTROLS)
    _settle(application)
    _, after_the_chart = (
        shown for shown in view.layout_container.views() if isinstance(shown, ParameterControlsView)
    )
    assert [row.controls is None for row in after_the_chart.rows] == [False, False]
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    monkeypatch.setattr(run_presentation_module, "setting_readouts", _no_setting)
    monkeypatch.setattr(_concentration(view), "refresh", _no_tick_without_a_frame)

    with pytest.raises(ValueError, match="this control can offer no setting"):
        view.present(False)

    for run, controller in zip(view.runs, (first, second), strict=True):
        assert controller.has_failed is True
        assert run._status_text.text() == STATUS_FAILED_TEXT
        notice = run._notice_text.notice()
        assert notice is not None
        assert "RuntimeError: this frame could not be assembled" in notice

    assert [row.controls is None for row in after_the_chart.rows] == [True, True]
    assert [row.not_shown_text.isHidden() for row in after_the_chart.rows] == [False, False]


def test_a_view_that_raises_on_a_halt_leaves_no_dial_on_a_setting_the_run_refused(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A dial moved on a halted run goes back to the run's setting in every View.

    The run holds a fresh gas flow of 2.0 L/min, and a halted run refuses a
    dial. Every frame fails, and the concentration chart raises on the
    halt's tick. One setting controls View sits before the chart in reading
    order and one after it. A learner drags the fresh gas flow dial to
    7.0 L/min in the second View. The halt that follows the refusal is the
    only thing that writes the dial back. When the Views after the chart
    were handed nothing, the dial's thumb stayed on 7.0 L/min beside a first
    View that showed 2.0 L/min (blind review of `PL-RF2S`).
    """

    controller = _paused_run_with_history(60.0)
    view = _shown_view(application, controller)
    view.layout_container.choose_view(AreaId(3), PARAMETER_CONTROLS)
    _settle(application)
    before_the_chart, after_the_chart = (
        shown for shown in view.layout_container.views() if isinstance(shown, ParameterControlsView)
    )
    in_force = _dial_readings(before_the_chart.rows[0])
    assert _dial_readings(after_the_chart.rows[0]) == in_force
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    monkeypatch.setattr(_concentration(view), "refresh", _no_tick_without_a_frame)

    with pytest.raises(RuntimeError, match="this View could not show the tick"):
        view.present(False)

    assert controller.has_failed is True
    moved = after_the_chart.rows[0].controls
    assert moved is not None

    _drag(moved._fresh_gas_flow_slider, 7.0, FLOW_DISPLAY_DECIMALS)
    _settle(application)

    assert controller.settings().fresh_gas_flow_l_min == 2.0
    assert moved._fresh_gas_flow_slider.value_label.text() == "2.0 L/min"
    assert _dial_readings(after_the_chart.rows[0]) == in_force
    assert _dial_readings(before_the_chart.rows[0]) == in_force


#: Each request with which a View names a run, as a call on the dashboard
#: for the run it is given.
_REQUESTS_THAT_NAME_A_RUN: Final[Mapping[str, Callable[[SimulationView, RunId], None]]] = {
    "a dial pressed": lambda view, run_id: view._handle_adjustment_start_request(run_id),
    "a setting": lambda view, run_id: view._handle_setting_request(
        run_id, ControlInput.FRESH_GAS_FLOW, 7.0
    ),
    "a preview": lambda view, run_id: view._handle_preview_request(
        run_id, ControlInput.FRESH_GAS_FLOW, 7.0
    ),
    "a preview ended": lambda view, run_id: view._handle_preview_end_request(run_id),
}


@pytest.mark.parametrize("request_made", list(_REQUESTS_THAT_NAME_A_RUN))
def test_a_request_that_names_a_run_the_dashboard_does_not_hold_halts_every_run(
    application: QApplication, request_made: str
) -> None:
    """A View that asks to change a run that is gone is refused by name, and nothing is changed.

    A View names the run that it asks about, in each of its four requests:
    a dial pressed, a setting, a preview and a preview ended. The dashboard
    holds Run 1 alone here, and the request names Run 2. No run takes a
    setting or a preview. The refusal halts every run, as any exception in
    one of the dashboard's own slots does, and the banner names the run that
    was asked for and the runs that are held.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    absent = view._run_identities.mint()
    refusal = (
        "a View asked for a change to Run 2, which this dashboard does not hold; it holds Run 1"
    )

    with pytest.raises(ValueError, match=refusal):
        view._run_with(absent)

    _REQUESTS_THAT_NAME_A_RUN[request_made](view, absent)

    assert controller.settings().fresh_gas_flow_l_min == 4.0
    assert controller.record().control_timeline == ()
    assert view.runs[0].preview is None
    assert controller.has_failed is True
    notice = view.runs[0]._notice_text.notice()
    assert notice is not None
    assert f"ValueError: {refusal}" in notice


def _refusing(*args: object, **kwargs: object) -> NoReturn:
    """Stand in for a controller method in a test where the controller raises inside a request."""

    raise RuntimeError("the controller could not do this")


def _a_setting_the_controller_raises_on(view: SimulationView, patch: pytest.MonkeyPatch) -> None:
    second = view.runs[1]
    patch.setattr(second.controller, "set_fresh_gas_flow", _refusing)
    _drag(_dials(second)._fresh_gas_flow_slider, 7.0, FLOW_DISPLAY_DECIMALS)


def _a_preview_the_controller_raises_on(view: SimulationView, patch: pytest.MonkeyPatch) -> None:
    second = view.runs[1]
    patch.setattr(second.controller, "preview_settings", _refusing)
    _hold_thumb(_dials(second)._fresh_gas_flow_slider, 7.0, FLOW_DISPLAY_DECIMALS)


def _a_setting_for_a_control_the_run_does_not_have(
    view: SimulationView, patch: pytest.MonkeyPatch
) -> None:
    view._handle_setting_request(
        view.runs[1].run_id,
        "tidal volume",  # type: ignore[arg-type]
        7.0,
    )


@pytest.mark.parametrize(
    ("request_made", "error"),
    [
        (_a_setting_the_controller_raises_on, "RuntimeError: the controller could not do this"),
        (_a_preview_the_controller_raises_on, "RuntimeError: the controller could not do this"),
        (_a_setting_for_a_control_the_run_does_not_have, "KeyError: 'tidal volume'"),
    ],
    ids=["a setting", "a preview", "a setting for no control"],
)
def test_a_request_that_one_run_cannot_carry_out_halts_that_run_alone_and_shows_its_halt(
    application: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    request_made: Callable[[SimulationView, pytest.MonkeyPatch], None],
    error: str,
) -> None:
    """A View's request that fails inside one run stops that run, and the other run goes on.

    A dial in a View asks the dashboard, and the dashboard passes the
    request to the run that the dial names (`RunView.request_setting`,
    `RunView.request_preview`). The second of two runs fails to carry the
    request out: its controller raises, or the request names a control that
    the run does not have. That run shows its halt, with the error in its
    banner. The first run has not failed and shows no halt. If the run's
    method let the exception out, the dashboard would halt every run.
    """

    first, second = SimulationController(), SimulationController()
    view = _shown_view(application, first, second)

    request_made(view, monkeypatch)
    _settle(application)

    halted, untouched = view.runs[1], view.runs[0]
    assert second.has_failed is True
    assert halted._status_text.text() == STATUS_FAILED_TEXT
    notice = halted._notice_text.notice()
    assert notice is not None
    assert error in notice
    assert first.has_failed is False, "the run that was not asked was halted too"
    assert untouched._status_text.text() != STATUS_FAILED_TEXT
    assert second.settings().fresh_gas_flow_l_min == 4.0
    assert halted.preview is None


def test_a_view_chosen_while_frames_fail_does_not_ask_again_every_tick(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A failed frame is not retried on every render tick, for a View chosen after it either.

    A new View owed its first frame until one drew, so with every frame
    failing, each idle render tick assembled the frame again and halted every
    run again. The dashboard now records that the frame failed for these
    Views, and a View owes one again only once the Views change.
    """

    controller = _paused_run_with_history(60.0)
    view = _shown_view(application, controller)
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    halts: list[Exception] = []
    halt = view._halt_every_run
    monkeypatch.setattr(view, "_halt_every_run", lambda error: (halts.append(error), halt(error)))

    view.layout_container.choose_view(AreaId(3), CONCENTRATION_CHART)
    chosen = len(halts)

    for _ in range(5):
        view.render_tick()

    assert chosen == 1, "the chosen View was not offered a frame at once"
    assert len(halts) == chosen, f"{len(halts) - chosen} idle ticks retried the failed frame"


# ------------------------------------------------------ the preview of a dragged setting


def _hold_thumb(control: ParameterSlider, value: float, decimals: int) -> None:
    """Press a slider's thumb and drag it to `value`, without releasing it."""

    control.slider.setSliderDown(True)
    control.slider.setSliderPosition(slider_position(value, decimals))


def test_a_held_thumb_previews_the_setting_without_applying_it(application: QApplication) -> None:
    """While the thumb is held the run keeps its setting and both plots draw the preview.

    The preview appears at the press, is labelled in the plot, and is gone on
    the frame drawn at the release, which is when the value is applied and
    recorded once (`PL-5B1N`).
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    controller.pause()
    held_flow = controller.settings().fresh_gas_flow_l_min
    view = _shown_view(application, controller)
    run = view.runs[0]
    control = _dials(run)._fresh_gas_flow_slider
    concentration, wash_in = _concentration(view).chart, _wash_in(view).chart

    _hold_thumb(control, 6.0, FLOW_DISPLAY_DECIMALS)
    view.render_tick()

    assert held_flow != 6.0
    assert controller.settings().fresh_gas_flow_l_min == held_flow
    assert controller.record().control_timeline == ()
    assert control.value_label.text() == format_flow(held_flow)
    for plot in (concentration, wash_in):
        assert plot.preview_label(0) == "Preview: Fresh gas flow 6.0 L/min, not applied"
        region = plot.preview_region(0)
        assert region is not None
        assert region[0] == pytest.approx(300.0)
    assert concentration.preview_points(0, RecordedQuantity.ALVEOLAR)[0]

    control.slider.setSliderDown(False)

    assert controller.settings().fresh_gas_flow_l_min == 6.0
    assert len(controller.record().control_timeline) == 1
    for plot in (concentration, wash_in):
        assert plot.preview_region(0) is None
        assert plot.preview_label(0) is None
    assert concentration.preview_points(0, RecordedQuantity.ALVEOLAR) == ((), ())


def test_a_preview_is_drawn_only_inside_its_region_with_its_label(
    application: QApplication,
) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    controller.pause()
    view = _shown_view(application, controller)
    control = _dials(view.runs[0])._cardiac_output_slider
    chart = _concentration(view).chart

    _hold_thumb(control, 8.0, FLOW_DISPLAY_DECIMALS)
    view.render_tick()
    region = chart.preview_region(0)
    assert region is not None
    start_s, stop_s = region
    frame = chart.frame
    assert frame is not None

    # The window keeps its width and puts the reach at mid-plot.
    assert (frame.start_s + frame.stop_s) / 2.0 == pytest.approx(300.0) or frame.start_s == 0.0
    assert chart.preview_label(0) == "Preview: Cardiac output 8.0 L/min, not applied"

    for quantity in frame.visible:
        predicted, _ = chart.preview_points(0, quantity)
        drawn, _ = chart.drawn_points(0, quantity)

        assert predicted
        assert all(start_s <= time_s <= stop_s for time_s in predicted)
        assert all(time_s <= start_s for time_s in drawn)
        assert chart.preview_pen(0, quantity).widthF() >= 2


def test_the_hover_never_answers_from_a_preview(application: QApplication) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    controller.pause()
    view = _shown_view(application, controller)
    control = _dials(view.runs[0])._delivered_concentration_slider
    chart = _concentration(view).chart

    _hold_thumb(control, 8.0, CONCENTRATION_DISPLAY_DECIMALS)
    view.render_tick()
    times, percents = chart.preview_points(0, RecordedQuantity.CIRCUIT)
    index = len(times) * 3 // 4

    # The point is well past the run's reach, on a curve the run never drew.
    assert times[index] > 300.0 + 60.0
    assert chart.readout_at(times[index], percents[index]) is None


def test_a_stopped_run_draws_no_preview_while_its_thumb_is_held(application: QApplication) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 60.0)
    controller.fail("a failure the test injects")
    view = _shown_view(application, controller)
    control = _dials(view.runs[0])._fresh_gas_flow_slider

    _hold_thumb(control, 6.0, FLOW_DISPLAY_DECIMALS)
    view.render_tick()

    assert _concentration(view).chart.preview_region(0) is None
    assert _wash_in(view).chart.preview_region(0) is None


def test_only_the_compared_run_whose_thumb_is_held_previews_and_its_label_names_it(
    application: QApplication,
) -> None:
    case = _branched_case()
    view = _case_view(application, case)
    view.add_run(case.fork_at(CaseInstant(60.0)))
    view.present(False)
    branch = view.runs[BRANCH_RUN_INDEX]
    control = _dials(branch)._fresh_gas_flow_slider
    chart = _concentration(view).chart

    _hold_thumb(control, 6.0, FLOW_DISPLAY_DECIMALS)
    view.render_tick()

    assert chart.preview_region(0) is None
    assert chart.preview_label(BRANCH_RUN_INDEX) == (
        f"{run_label(branch.run_id)} preview: Fresh gas flow 6.0 L/min, not applied"
    )


# ------------------------------------- the case's panels, in more than one Area


def _show_in_three_areas(application: QApplication, view: SimulationView, kind: ViewKind) -> None:
    """Show `kind` in the accounting Area and the wash-in Area, as well as in its own.

    `_EVERY_VIEW` shows each kind once, so three Areas then show this one.
    """

    for area_id in (AreaId(2), AreaId(3)):
        view.layout_container.choose_view(area_id, kind)
        _settle(application)


def _marks_panels(view: SimulationView) -> list[BookmarksPanel]:
    """Every Area's copy of the lists of marks."""

    panels = [v.panel for v in view.layout_container.views() if isinstance(v, BookmarksView)]

    return [panel for panel in panels if panel is not None]


def _fork_panels(view: SimulationView) -> list[ForkPanel]:
    """Every Area's copy of the branch control."""

    panels = [v.panel for v in view.layout_container.views() if isinstance(v, BranchView)]

    return [panel for panel in panels if panel is not None]


def test_every_bookmarks_view_lists_the_case_s_marks_and_follows_a_new_one(
    application: QApplication,
) -> None:
    """Three Areas showing the bookmarks each list the same marks (`PL-9YPR`).

    The marks belong to the case, so a mark added after the Areas were made
    appears in all three on the next frame.
    """

    case = _branched_case()
    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(30.0), "first look"))
    view = _case_view(application, case)
    _show_in_three_areas(application, view, BOOKMARKS)
    panels = _marks_panels(view)

    assert len(panels) == 3
    assert len({id(panel) for panel in panels}) == 3, "the Areas share one panel"

    for panel in panels:
        assert any("first look" in text for text in _strings_of(panel.times, ()))

    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(45.0), "second look"))
    view.present(False)

    for panel in panels:
        assert any("first look" in text for text in _strings_of(panel.times, ()))
        assert any("second look" in text for text in _strings_of(panel.times, ()))


def test_every_branch_view_shows_the_one_selected_point_and_a_press_branches_at_it(
    application: QApplication,
) -> None:
    """Three Areas showing the branch control show one selection, the case's (`PL-9YPR`).

    The trunk offers induction, a mark at 30 s and its setting change at
    60 s, and every copy starts on induction. The mark is chosen in the
    second copy. All three then show it, a frame leaves it there, and the
    button of the third copy opens the branch at 30 s.
    """

    case = _branched_case()
    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(30.0), "check"))
    view = _case_view(application, case)
    _show_in_three_areas(application, view, BRANCH)
    panels = _fork_panels(view)

    assert len(panels) == 3
    assert len({id(panel) for panel in panels}) == 3, "the Areas share one control"
    assert [float(panel.point_selector.currentData()) for panel in panels] == [0.0, 0.0, 0.0]

    index = panels[1].point_selector.findData(30.0)
    assert index >= 0, "the control does not offer the mark at 30 s"
    panels[1].point_selector.setCurrentIndex(index)

    assert [float(panel.point_selector.currentData()) for panel in panels] == [30.0, 30.0, 30.0]

    view.present(False)

    assert [float(panel.point_selector.currentData()) for panel in panels] == [30.0, 30.0, 30.0]

    panels[2].take_button.click()
    _settle(application)

    assert len(case.branches) == 1
    assert case.branches[0].snapshot().elapsed_s == pytest.approx(30.0)


def _rebuild_the_branch_view(application: QApplication, view: SimulationView) -> ForkPanel:
    """Show another View in the branch control's Area and then the branch View again.

    `_EVERY_VIEW` shows the branch View in Area 6 alone, so no copy of the
    control exists between the two choices.

    Returns:
        The new copy of the branch control.
    """

    before = _fork_panel(view)
    view.layout_container.choose_view(AreaId(6), AGENT_ACCOUNTING)
    _settle(application)

    assert _fork_panels(view) == []

    view.layout_container.choose_view(AreaId(6), BRANCH)
    _settle(application)
    view.present(False)
    after = _fork_panel(view)

    assert after is not before

    return after


def test_the_selected_branch_point_survives_the_branch_view_being_rebuilt(
    application: QApplication,
) -> None:
    """A copy of the branch control built later shows the point the learner chose (`PL-9YPR`).

    A blind review found that a new copy started on induction, as a control
    nobody had used does. A switch of Workspace rebuilds every View, so the
    learner's choice of the setting change at 60 s became 0 s, and the next
    press opened the branch at induction.
    """

    case = _branched_case()
    view = _case_view(application, case)
    selector = _fork_panel(view).point_selector
    selector.setCurrentIndex(selector.findData(60.0))

    rebuilt = _rebuild_the_branch_view(application, view)

    assert float(rebuilt.point_selector.currentData()) == 60.0

    rebuilt.take_button.click()
    _settle(application)

    assert len(case.branches) == 1
    assert case.branches[0].snapshot().elapsed_s == pytest.approx(60.0)


def test_a_cleared_branch_selection_stays_clear_when_the_branch_view_is_rebuilt(
    application: QApplication,
) -> None:
    """A selection cleared because its mark was removed is still clear in a new copy (`PL-J12Z`).

    The learner chooses the mark at 30 s and then removes the mark. Nothing
    is selected, and a copy built afterwards must not put induction in its
    place. A press there is refused and opens no branch.
    """

    case = _branched_case()
    mark = TimeBookmark(CaseInstant(30.0), "check")
    case.trunk.add_time_bookmark(mark)
    view = _case_view(application, case)
    selector = _fork_panel(view).point_selector
    selector.setCurrentIndex(selector.findData(30.0))
    case.trunk.remove_time_bookmark(mark)
    view.present(False)

    assert selector.currentIndex() == -1

    rebuilt = _rebuild_the_branch_view(application, view)

    assert [rebuilt.point_selector.itemData(row) for row in range(2)] == [0.0, 60.0]
    assert rebuilt.point_selector.currentIndex() == -1

    rebuilt.take_button.click()
    _settle(application)

    assert case.branches == ()
    assert rebuilt.notice.notice() == FORK_NOTHING_SELECTED_TEXT


def test_a_stopped_run_names_a_branch_only_while_an_area_shows_the_branch_control(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The banner sends a learner to the branch control only while it is on screen (`PL-9YPR`).

    A blind review found that the banner named a branch whenever the
    dashboard held a case. Since the branch control became a View, a
    Workspace may show it in no Area, and the banner then sent the learner to
    a control that was not there. The supported run length here ends at
    300 s, for the reason that `_a_dial_moved_at_the_supported_run_length`
    gives.
    """

    last_step = round(300.0 / SIMULATION_STEP_S)
    monkeypatch.setattr(
        supported_ranges_module, "maximum_step_count", lambda simulation_step_s: last_step
    )
    refused = f"{_CARDIAC_OUTPUT_REFUSED_ON_A_STOPPED_RUN}. "
    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    view = _case_view(application, BranchedCase(controller))
    trunk = view.runs[0]
    view.layout_container.choose_view(AreaId(6), AGENT_ACCOUNTING)
    _settle(application)

    assert _fork_panels(view) == []

    _drag(_dials(trunk)._cardiac_output_slider, 10.0, FLOW_DISPLAY_DECIMALS)

    hidden = trunk._notice_text.notice()
    assert hidden is not None
    assert hidden.endswith(refused + "Reset to start a new run, which keeps every setting.")

    view.layout_container.choose_view(AreaId(6), BRANCH)
    _settle(application)
    view.present(False)

    shown = trunk._notice_text.notice()
    assert shown is not None
    assert shown.endswith(
        refused + "To try a different setting, branch at an earlier instant, where each dial "
        "starts at what it was set to then, or Reset to start a new run, which keeps every "
        "setting."
    )

    # An Area can hold a branch control that it does not draw, as when a pin's
    # notice covers the View (`PL-1D3Z`). Hiding the View produces that state.
    next(v for v in view.layout_container.views() if isinstance(v, BranchView)).hide()
    view.present(False)

    covered = trunk._notice_text.notice()
    assert _fork_panels(view) != []
    assert covered is not None
    assert covered.endswith(refused + "Reset to start a new run, which keeps every setting.")


def test_a_failing_frame_withdraws_the_branch_offer_from_every_copy(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A halt restates every Area's copy of the branch control, not just one (`PL-9YPR`)."""

    case = _branched_case()
    view = _case_view(application, case)
    _show_in_three_areas(application, view, BRANCH)
    panels = _fork_panels(view)

    assert len(panels) == 3
    assert all(panel.point_selector.count() == 2 for panel in panels)
    assert all(panel.here_button.isHidden() is False for panel in panels)

    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    view.present(False)

    assert case.trunk.has_failed is True
    restated = {
        id(panel) for restatement in view.halt_restatements() for panel in restatement.panels
    }

    for panel in panels:
        assert id(panel) in restated
        assert panel.point_selector.count() == 0
        assert panel.take_button.isHidden() is True
        assert panel.here_button.isHidden() is True


def test_a_halt_that_cannot_restate_the_marks_hides_them_in_every_copy_and_in_a_new_one(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """After a halt that cannot restate the marks, every copy, old or new, shows no standing.

    A copy built while the marks are withdrawn must not show a new panel's
    empty lists, which would read as "no marks set" (`PL-9YPR`, `PL-YHR3`).
    The next frame that draws shows the lists in every copy again.
    """

    controller = _paused_run_with_history()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(600.0), "check"))
    view = _shown_view(application, controller)
    _show_in_three_areas(application, view, BOOKMARKS)
    panels = _marks_panels(view)

    assert len(panels) == 3
    assert all(panel.times.isHidden() is False for panel in panels)

    def unanswerable(self: SimulationController) -> NoReturn:
        raise RuntimeError("the run could not say where it stands on its marks")

    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    monkeypatch.setattr(SimulationController, "bookmark_standings", unanswerable)
    view.present(False)
    built = view.build_bookmarks_panel()
    # The dashboard owns the copy, so the copy is deleted with it.
    built.setParent(view)

    assert controller.has_failed is True
    restated = {
        id(panel) for restatement in view.halt_restatements() for panel in restatement.panels
    }

    for panel in (*panels, built):
        assert id(panel) in restated
        assert panel.times.isHidden() is True
        assert panel.targets.isHidden() is True

    monkeypatch.undo()
    view.present(False)

    for panel in (*panels, built):
        assert panel.times.isHidden() is False
        assert panel.targets.isHidden() is False


def _words_read_in(panel: QWidget) -> list[str]:
    """The text of each label, button and selector entry that a panel shows, in the panel's order.

    A widget that the panel hides is left out, so two panels give the same
    list only when a learner reads the same words in both.
    """

    words: list[str] = []

    for child in panel.findChildren(QWidget):
        if not child.isVisibleTo(panel):
            continue

        if isinstance(child, QLabel | QAbstractButton):
            words.append(child.text())
        elif isinstance(child, QComboBox):
            words.extend(child.itemText(index) for index in range(child.count()))

    return words


def test_a_case_view_chosen_after_a_failing_halt_shows_the_halted_words(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A bookmarks or branch View whose first tick has no frame still takes its copy (`PL-RF2S`).

    Each View takes its copy of the case's panel on its first tick. While
    every frame fails, a View chosen then is handed only the halt's tick,
    which has no frame. Before every View was handed that tick, a View
    chosen then stayed an empty rectangle (`PL-G3N1`).

    The copies in Areas 5 and 6 were on screen when the frames began to
    fail, and the halt restated them: the mark is listed, and the failed
    trunk offers no point to branch at. Each View chosen afterwards for
    Area 2 must read the same.
    """

    case = _branched_case()
    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(30.0), "first look"))
    view = _case_view(application, case)
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    view.present(False)

    assert case.trunk.has_failed is True

    on_screen = _marks_panel(view)
    view.layout_container.choose_view(AreaId(2), BOOKMARKS)
    _settle(application)
    (chosen,) = (panel for panel in _marks_panels(view) if panel is not on_screen)

    assert any("first look" in words for words in _words_read_in(chosen))
    assert _words_read_in(chosen) == _words_read_in(on_screen)

    offered = _fork_panel(view)
    view.layout_container.choose_view(AreaId(2), BRANCH)
    _settle(application)
    (taken,) = (panel for panel in _fork_panels(view) if panel is not offered)

    assert taken.point_selector.count() == 0
    assert taken.take_button.isHidden() is True
    assert taken.here_button.isHidden() is True
    assert _words_read_in(taken) == _words_read_in(offered)


def test_the_case_views_of_a_dashboard_whose_first_frame_fails_show_the_halted_case(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The first tick of every View can be a halt's, with no frame (`PL-RF2S`).

    The dashboard is built while every frame fails. Its first frame halts the
    trunk, and the halt hands every View its first tick. The bookmarks View
    lists the trunk's mark, and the branch View holds a control that offers
    no point, because a failed trunk offers none.
    """

    case = _branched_case()
    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(30.0), "first look"))
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    view = _case_view(application, case)

    assert case.trunk.has_failed is True

    marks = _marks_panel(view)
    control = _fork_panel(view)

    assert marks.isVisibleTo(view)
    assert marks.times.isHidden() is False
    assert any("first look" in words for words in _words_read_in(marks))
    assert control.isVisibleTo(view)
    assert control.point_selector.count() == 0
    assert control.take_button.isHidden() is True
    assert control.here_button.isHidden() is True


def test_the_bookmarks_and_the_branch_control_are_registered_under_their_kinds() -> None:
    """Each Area's chooser lists the two Views by these titles (`PL-9YPR`).

    An Area never gives a View less room than its declared minimum. Both
    minimums are placeholders, set by `PL-CBYS` from the room each Area has.
    """

    bookmarks, branch = REGISTERED[BOOKMARKS], REGISTERED[BRANCH]

    assert BOOKMARKS == "bookmarks"
    assert bookmarks.factory is BookmarksView
    assert bookmarks.title == "Bookmarks"
    assert (bookmarks.minimum.width_px, bookmarks.minimum.height_px) == (220, 110)
    assert BRANCH == "branch"
    assert branch.factory is BranchView
    assert branch.title == "Branch"
    assert (branch.minimum.width_px, branch.minimum.height_px) == (220, 110)


def test_a_bookmarks_panel_built_between_frames_lists_the_marks_on_screen(
    application: QApplication,
) -> None:
    """A copy built after the last frame lists the marks that the frame's copy lists.

    The trunk is standing on the mark that halted it, so the frame listed
    one time bookmark. A new panel's own lists are empty (`PL-9YPR`).
    """

    _, view = _halted_trunk_case(application)
    drawn = _marks_panel(view)
    built = view.build_bookmarks_panel()
    # The dashboard owns the copy, so the copy is deleted with it.
    built.setParent(view)

    assert any("the decision point" in text for text in _strings_of(drawn.times, ()))
    assert _strings_of(built.times, ()) == _strings_of(drawn.times, ())
    assert built.times.isHidden() is False


def test_a_branch_control_built_between_frames_shows_the_offer_on_screen(
    application: QApplication,
) -> None:
    """A copy built after the last frame offers what the copy drawn by that frame offers.

    The trunk is standing on a mark that halted it, so the offer on screen
    has "Branch here" named for the halt. A new control's own defaults have
    no points and an unnamed button (`PL-9YPR`).
    """

    _, view = _halted_trunk_case(application)
    drawn = _fork_panel(view)
    built = view.build_branch_control()
    assert built is not None
    # The dashboard owns the copy, so the copy is deleted with it.
    built.setParent(view)

    def entries(panel: ForkPanel) -> list[str]:
        selector = panel.point_selector

        return [selector.itemText(index) for index in range(selector.count())]

    assert len(entries(drawn)) == 3, "the frame's offer is not the one this test describes"
    assert entries(built) == entries(drawn)
    assert built.here_button.text() == drawn.here_button.text() != ""
    assert built.here_button.isHidden() is drawn.here_button.isHidden() is False
    assert built.take_button.isEnabled() is drawn.take_button.isEnabled() is True
