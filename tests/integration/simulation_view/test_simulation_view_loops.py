"""The dashboard, driven headless against real runs.

These tests cover the stepping and drawing timer loops.

`simulation_view_support.py` describes the whole suite.
"""

from collections.abc import Sequence
from dataclasses import replace
from typing import NoReturn

import pytest
from PySide6.QtWidgets import QApplication

from anesthesia_sim.app import run_presentation as run_presentation_module
from anesthesia_sim.app import simulation_view as simulation_view_module
from anesthesia_sim.app.chart_frame import ChartFrame
from anesthesia_sim.app.compartment_schematic import SchematicShown
from anesthesia_sim.app.controller import RunRecord, SimulationController, SimulationSnapshot
from anesthesia_sim.app.dashboard_frame import (
    SIMULATION_STEP_S,
    SIMULATION_TICK_INTERVAL_S,
    STATUS_FAILED_TEXT,
    Readout,
    accounting,
    readouts,
    slider_position,
)
from anesthesia_sim.app.formatting import FLOW_DISPLAY_DECIMALS
from anesthesia_sim.app.playback import (
    DEFAULT_PLAYBACK_RATE,
    SUPPORTED_PLAYBACK_RATES,
    PlaybackRate,
    playback_rate_for,
)
from anesthesia_sim.app.run_presentation import RunPresentation
from anesthesia_sim.app.theme import WARNING
from anesthesia_sim.app.view_registry import AGENT_ACCOUNTING
from anesthesia_sim.app.views import (
    AccountingView,
    AgentCostView,
    CompartmentSchematicView,
    ConcentrationView,
)
from anesthesia_sim.core.supported_ranges import FreshGasFlow
from anesthesia_sim.layout.tree import AreaId
from tests.integration.simulation_view.simulation_view_support import (
    _RUN_PANEL_VIEWS,
    _accounting_of,
    _accounting_panel,
    _accounting_reading,
    _advance,
    _concentration,
    _dial_readings,
    _dials,
    _failing_assembly,
    _fresh_run,
    _real_step_failure,
    _select_playback_rate,
    _setting_row,
    _settle,
    _shown_view,
    _StepFailingController,
    _steps,
)

# -------------------------------------------------------------- the loops


def test_simulation_loop_advances_without_rendering(application: QApplication) -> None:
    """Stepping must not be gated on drawing."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()
    presented = view.presented_frames

    _steps(view.runs[0], 3)

    assert controller.snapshot().elapsed_s > 0.0
    assert view.presented_frames == presented


def test_render_loop_draws_without_advancing(application: QApplication) -> None:
    """Drawing must not move simulation time."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()
    presented = view.presented_frames

    view.render_tick()
    view.render_tick()

    assert controller.snapshot().elapsed_s == 0.0
    assert view.presented_frames >= presented + 1


def test_neither_loop_does_anything_while_paused(application: QApplication) -> None:
    controller = SimulationController()
    view = _shown_view(application, controller)
    presented = view.presented_frames

    _steps(view.runs[0], 2)
    view.render_tick()

    assert controller.snapshot().elapsed_s == 0.0
    assert view.presented_frames == presented


def test_a_dragged_slider_leaves_its_frame_to_the_render_tick(application: QApplication) -> None:
    """Moving a held thumb defers its frames, and the release draws one at once (`PL-R2YM`).

    The thumb's moves only redraw the preview, so they wait for the render
    tick like any dragged slider. The release is one discrete action, and it
    draws one frame at once, so the preview is gone the moment the thumb is
    let go (`PL-5B1N`). The view beside the dial agrees with the snapshot the
    moment the setting is applied (`PL-018`).
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()
    presented = view.presented_frames
    slider = _dials(run)._fresh_gas_flow_slider.slider

    slider.setSliderDown(True)

    for flow in (5.0, 6.0, 7.0):
        slider.setSliderPosition(slider_position(flow, FLOW_DISPLAY_DECIMALS))

    assert view.presented_frames == presented
    assert view._render_pending is True

    slider.setSliderDown(False)

    assert controller.snapshot().fresh_gas_flow_l_min == 7.0
    assert _dials(run)._fresh_gas_flow_slider.value_label.text() == "7.0 L/min"
    assert view.presented_frames == presented + 1
    assert view._render_pending is False
    assert run.preview is None


def test_a_refused_slider_change_draws_its_own_frame(application: QApplication) -> None:
    """A refused change is the one state whose frame the coalescing rule may not defer.

    A refused setting is the only case where the dial on screen and the
    simulation disagree. Waiting even one tick there leaves a control showing
    a setting that the run is not using.
    """

    controller = SimulationController(agent_id="isoflurane")
    view = _shown_view(application, controller)
    run = view.runs[0]
    presented = view.presented_frames

    run._handle_delivered_concentration_change(50.0)

    assert run._notice_text.isHidden() is False
    assert view.presented_frames == presented + 1
    assert view._render_pending is False


def test_the_frame_that_clears_a_refusal_is_drawn_too(application: QApplication) -> None:
    """The same fault in reverse: a notice left up after it stopped being true."""

    controller = SimulationController(agent_id="isoflurane")
    view = _shown_view(application, controller)
    run = view.runs[0]

    run._handle_delivered_concentration_change(50.0)
    presented = view.presented_frames

    run._handle_delivered_concentration_change(2.0)

    assert run._notice_text.isHidden() is True
    assert view.presented_frames == presented + 1


def test_a_discrete_action_still_draws_its_own_frame(application: QApplication) -> None:
    """Only a control that reports continuously coalesces."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    presented = view.presented_frames

    view.runs[0]._start_button.click()

    assert controller.is_running
    assert view.presented_frames == presented + 1
    assert view._render_pending is False


def test_the_render_tick_draws_a_pending_change_while_the_run_is_stopped(
    application: QApplication,
) -> None:
    """The limit on deferring a frame still applies when a reader pauses, changes and resumes.

    While the run is paused there is no run to draw, but a dial can still move.
    So the tick draws a frame for a change that is owed one, and stops drawing
    once that frame is drawn.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    slider = _dials(view.runs[0])._fresh_gas_flow_slider.slider

    # A key or wheel step applies with no press, and leaves its frame owed.
    # A released drag draws its own frame at once (`PL-5B1N`).
    slider.setValue(slider_position(7.0, FLOW_DISPLAY_DECIMALS))
    assert view._render_pending is True
    presented = view.presented_frames

    view.render_tick()

    assert view.presented_frames == presented + 1
    assert view._render_pending is False

    view.render_tick()

    assert view.presented_frames == presented + 1, (
        "the tick kept drawing a paused run with nothing owed"
    )


def test_simulation_time_does_not_depend_on_render_cadence(application: QApplication) -> None:
    """Identical step counts must give identical results, however drawing goes.

    `PL-VM40`: simulation time is a function of steps taken, never of the
    wall clock or of how many frames were drawn between them.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()

    for _ in range(5):
        view.runs[0].step_tick()
        view.render_tick()

    steps_taken = round(controller.snapshot().elapsed_s / SIMULATION_STEP_S)
    reference = SimulationController()
    reference.start()
    _advance(reference, steps_taken * SIMULATION_STEP_S)

    assert controller.snapshot().elapsed_s == reference.snapshot().elapsed_s
    assert (
        controller.snapshot().alveolar_partial_pressure_fraction
        == reference.snapshot().alveolar_partial_pressure_fraction
    )


def test_the_run_loop_takes_one_step_per_tick_at_real_time_and_never_catches_up(
    application: QApplication,
) -> None:
    """A late tick must cost the run real time, never change its trajectory.

    The number of steps a tick takes is set by the reader's playback setting,
    not by how long the tick took. So when a host wakes the tick late, the run
    falls behind the wall clock and stays behind.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()

    ticks = 7
    _steps(view.runs[0], ticks)

    assert controller.snapshot().elapsed_s == ticks * SIMULATION_STEP_S
    assert round(controller.snapshot().elapsed_s / SIMULATION_STEP_S) == ticks


@pytest.mark.parametrize(
    "rate",
    SUPPORTED_PLAYBACK_RATES,
    ids=[f"{rate.multiplier}x" for rate in SUPPORTED_PLAYBACK_RATES],
)
def test_the_run_loop_takes_the_playback_rates_steps_per_tick(
    application: QApplication, rate: PlaybackRate, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The multiplier is steps per tick, and the step never moves (`PL-SN2C`)."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    view.runs[0]._playback_rate = rate
    controller.start()

    steps_requested: list[float] = []
    advance = controller.advance

    def recording_advance(simulation_step_s: float) -> None:
        steps_requested.append(simulation_step_s)
        advance(simulation_step_s)

    monkeypatch.setattr(controller, "advance", recording_advance)

    ticks = 3
    _steps(view.runs[0], ticks)

    steps_per_tick = rate.steps_per_tick(
        tick_interval_s=SIMULATION_TICK_INTERVAL_S, simulation_step_s=SIMULATION_STEP_S
    )
    expected_steps = ticks * steps_per_tick

    assert steps_per_tick == rate.multiplier
    assert len(steps_requested) == expected_steps
    assert set(steps_requested) == {SIMULATION_STEP_S}
    assert controller.snapshot().elapsed_s == expected_steps * SIMULATION_STEP_S
    assert round(controller.snapshot().elapsed_s / SIMULATION_STEP_S) == expected_steps


def test_a_failed_step_abandons_the_rest_of_its_tick(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A burst is not a licence to step past a step the core could not take.

    The run must stop on the last completed step, exactly as it does at real
    time. Nothing after the exception runs, in this tick or the next.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    view.runs[0]._playback_rate = playback_rate_for(60)
    controller.start()

    calls = 0
    advance = controller.advance

    def failing_advance(simulation_step_s: float) -> None:
        nonlocal calls
        calls += 1

        if calls == 5:
            raise _real_step_failure()

        advance(simulation_step_s)

    monkeypatch.setattr(controller, "advance", failing_advance)

    _steps(view.runs[0], 2)

    assert calls == 5
    assert controller.snapshot().elapsed_s == 4 * SIMULATION_STEP_S
    assert controller.is_running is False


def test_a_failed_step_stops_the_run_instead_of_killing_the_loop(application: QApplication) -> None:
    """`PL-018`: a core failure must never leave a stale "Running" display."""

    controller = _StepFailingController(_real_step_failure())
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()
    presented = view.presented_frames

    _steps(run, 3)

    assert controller.is_running is False
    assert controller.has_failed is True
    assert run._status_text.text() == "Stopped — simulation error"
    assert WARNING in run._status_text.styleSheet()
    assert run._notice_text.isHidden() is False
    notice = run._notice_text.notice()
    assert notice is not None
    assert "SimulationNumericalError" in notice
    # The failure was drawn, not just recorded.
    assert view.presented_frames >= presented + 1


def test_the_simulation_loop_survives_a_failure_so_reset_can_restart_it(
    application: QApplication,
) -> None:
    """The tick slot must keep working after a halt, or Reset restarts nothing."""

    controller = _StepFailingController(_real_step_failure())
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()

    _steps(run, 3)
    assert controller.has_failed is True

    run._reset_button.click()
    run._start_button.click()
    _steps(run, 3)

    assert controller.has_failed is False
    assert controller.snapshot().elapsed_s > 0.0
    assert run._status_text.text() == "Running"
    assert run._notice_text.isHidden() is True


def test_a_failed_render_stops_the_run_rather_than_freezing_the_display(
    application: QApplication,
) -> None:
    """A dead render loop over a live simulation is the mirror failure."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()

    real_refresh_view = view._refresh_view
    failures_left = [1]

    def failing_refresh_view() -> None:
        if failures_left[0]:
            failures_left[0] -= 1
            raise RuntimeError("chart series could not be updated")

        real_refresh_view()

    view._refresh_view = failing_refresh_view  # type: ignore[method-assign]

    view.render_tick()
    view.render_tick()

    assert controller.is_running is False
    assert controller.has_failed is True
    assert run._status_text.text() == "Stopped — simulation error"
    notice = run._notice_text.notice()
    assert notice is not None
    assert "RuntimeError" in notice


def test_a_frame_that_cannot_be_drawn_on_a_discrete_action_halts_every_run(
    application: QApplication,
) -> None:
    """A discrete action presents through a signal, and Qt prints and drops a slot's exception.

    So the immediate presentation guards itself, as the render tick does.
    Without that guard, a frame that could not be drawn for a playback change
    would leave every run advancing behind a display that had stopped.
    """

    first = SimulationController()
    second = SimulationController()
    first.start()
    second.start()
    view = _shown_view(application, first, second)

    real_refresh_view = view._refresh_view
    failures_left = [1]

    def failing_refresh_view() -> None:
        if failures_left[0]:
            failures_left[0] -= 1
            raise RuntimeError("the frame could not be built")

        real_refresh_view()

    view._refresh_view = failing_refresh_view  # type: ignore[method-assign]

    _select_playback_rate(view.runs[0], SUPPORTED_PLAYBACK_RATES[-1].multiplier)

    assert failures_left == [0], "the playback change did not present at once"

    for controller in (first, second):
        assert controller.is_running is False
        assert controller.has_failed is True
        assert controller.snapshot().failure_reason == "RuntimeError: the frame could not be built"

    for run in view.runs:
        assert run._status_text.text() == "Stopped — simulation error"
        notice = run._notice_text.notice()
        assert notice is not None
        assert "RuntimeError" in notice


def test_a_halt_whose_frame_cannot_be_drawn_is_still_shown_on_every_run(
    application: QApplication,
) -> None:
    """The shared render path draws the frame, so a halt from its exception cannot wait for one.

    Every controller is failed. A reader has to see the status word and the
    banner that say so, and neither needs a frame. Here one run's frame cannot
    be built on any attempt. The halt is still written, from each run's record,
    and the frame that the halt path tries afterwards fails again and is
    swallowed. Before a halt was written from the record alone, both status
    words went on showing the state from before the exception, with no banner
    under either.
    """

    first = SimulationController()
    second = SimulationController()
    first.start()
    second.start()
    view = _shown_view(application, first, second)

    build = view.runs[0].presentation

    def failing_frame(drawn: SimulationSnapshot | None = None) -> RunPresentation:
        if drawn is not None:
            raise RuntimeError("this run's frame could not be built")

        return build()

    view.runs[0].presentation = failing_frame  # type: ignore[method-assign]

    view.render_tick()

    for controller in (first, second):
        assert controller.is_running is False
        assert controller.has_failed is True

    for run in view.runs:
        assert run._status_text.text() == "Stopped — simulation error"
        notice = run._notice_text.notice()
        assert notice is not None
        assert "RuntimeError: this run's frame could not be built" in notice
        assert run._pause_button.isEnabled() is False
        assert run._start_button.isEnabled() is False


@pytest.mark.parametrize("refuses_every_write", [False, True], ids=["one frame", "every write"])
def test_a_halt_after_a_frame_whose_value_could_not_be_written_is_still_stated(
    application: QApplication, refuses_every_write: bool
) -> None:
    """A frame whose readouts cannot be written stops the run, and the panel says so.

    The readout row refuses the second frame's values, and in one case every
    value after them. The halt writes the last frame's values again. When it
    wrote them before the status word and the banner, the same refusal left
    the panel showing "Running" with Pause enabled over a failed run (blind
    review of `PL-RF2S`). The status word, the transport and the banner are
    now written first.
    """

    controller = SimulationController()
    controller.start()
    view = _shown_view(application, controller)
    run = view.runs[0]
    first_frame = readouts(controller.snapshot(), DEFAULT_PLAYBACK_RATE)
    write = run._readout_row.set_readouts

    def refusing(shown: Sequence[Readout]) -> None:
        if refuses_every_write or tuple(shown) != first_frame:
            raise ValueError("the readouts could not show these values")

        write(shown)

    run._readout_row.set_readouts = refusing  # type: ignore[method-assign]
    controller.advance(SIMULATION_STEP_S)

    if refuses_every_write:
        with pytest.raises(ValueError, match="the readouts could not show these values"):
            view.present(False)
    else:
        view.present(False)

    assert controller.has_failed is True
    assert run._status_text.text() == STATUS_FAILED_TEXT
    notice = run._notice_text.notice()
    assert notice is not None
    assert "ValueError: the readouts could not show these values" in notice
    assert run._pause_button.isEnabled() is False
    assert run._start_button.isEnabled() is False


def test_a_halt_shows_the_last_frame_whose_readouts_were_written_on_every_panel(
    application: QApplication,
) -> None:
    """A frame whose readouts could not be written is not the frame a halt shows.

    The first frame draws the run at 60 s. On the frame at 120 s the
    accounting View writes its panel, and then the readout row refuses its
    values. The halt that follows writes the readouts and hands every View
    the values from one frame: the one at 60 s, the last whose readouts
    were written. So the cards and the accounting panel again show one
    state of the run (`PL-RNYV`, `PL-RF2S`). The expected cards and amounts
    are those of a second run built directly and stepped to 60 s.

    The readout row is where a frame fails after every View has drawn it.
    A frame can also fail in a View, after the Views before it have drawn
    it. The test of a schematic that refuses a frame covers that case
    (`test_a_schematic_that_refuses_a_frame_leaves_every_view_on_the_frame_the_readouts_show`).
    """

    controller = _fresh_run(60.0)
    view = _shown_view(application, controller)
    run = view.runs[0]
    first_frame = readouts(controller.snapshot(), DEFAULT_PLAYBACK_RATE)
    write = run._readout_row.set_readouts
    refused: list[str] = []

    def refusing_a_later_frame(shown: Sequence[Readout]) -> None:
        if tuple(shown) != first_frame:
            refused.append(_accounting_panel(run)._agent_amounts_text.text())
            raise ValueError("the readouts could not show these values")

        write(shown)

    run._readout_row.set_readouts = refusing_a_later_frame  # type: ignore[method-assign]
    controller.start()
    _advance(controller, 60.0)
    later = accounting(controller.snapshot()).amounts
    at_60_s = _fresh_run(60.0).snapshot()

    view.present(False)

    assert later != accounting(at_60_s).amounts
    assert refused[0] == later, "the accounting View did not write the frame at 120 s first"
    assert controller.has_failed is True
    assert run._status_text.text() == STATUS_FAILED_TEXT
    assert [
        (panel.value_label.text(), panel.secondary_label.text())
        for panel in run._readout_row.panels
    ] == [
        (readout.value, readout.secondary) for readout in readouts(at_60_s, DEFAULT_PLAYBACK_RATE)
    ]
    assert _accounting_reading(_accounting_panel(run)) == _accounting_of(at_60_s)


def test_a_schematic_that_refuses_a_frame_leaves_every_view_on_the_frame_the_readouts_show(
    application: QApplication,
) -> None:
    """A View that cannot write a frame does not leave the View before it on that frame.

    The accounting View sits before the schematic View in reading order, and
    the agent cost View after it. The first frame draws the run at 60 s. The
    schematic then refuses the value of any later frame. On the frame at
    120 s the accounting View writes its panel, and then the schematic
    refuses. The halt tries the frame again, and the same happens. Before
    the fix, the accounting panel was left showing the amounts at 120 s,
    beside readouts and a clock at 1m (blind review of `PL-RF2S`).

    After the halt, the readouts, the accounting panel, the schematic and
    the cost panel must show the frame at 60 s, the last whose readouts
    were written. The expected cards and amounts are those of a second run
    built directly and stepped to 60 s, and the instant on the schematic and
    on the cost panel is written out by hand.
    """

    controller = _fresh_run(60.0)
    view = _shown_view(application, controller, workspaces=_RUN_PANEL_VIEWS)
    run = view.runs[0]
    accounting_view, schematic_view, cost_view = view.layout_container.views()
    assert isinstance(accounting_view, AccountingView)
    assert isinstance(schematic_view, CompartmentSchematicView)
    assert isinstance(cost_view, AgentCostView)
    panel = accounting_view.panels[0]
    schematic = schematic_view.schematics[0]
    first_frame = run.presentation(controller.snapshot()).values.schematic
    show = schematic.show_schematic
    written_before_the_schematic: list[str] = []

    def refusing_a_later_frame(shown: SchematicShown) -> None:
        if shown != first_frame:
            written_before_the_schematic.append(panel._agent_amounts_text.text())
            raise ValueError("the schematic could not show this value")

        show(shown)

    schematic.show_schematic = refusing_a_later_frame  # type: ignore[method-assign]
    controller.start()
    _advance(controller, 60.0)
    later = accounting(controller.snapshot()).amounts
    at_60_s = _fresh_run(60.0).snapshot()

    view.present(False)

    assert later != accounting(at_60_s).amounts
    assert written_before_the_schematic == [later, later], (
        "the accounting View did not write the frame at 120 s before the schematic refused it, "
        "on the frame and on the halt's second attempt"
    )
    assert controller.has_failed is True
    assert run._status_text.text() == STATUS_FAILED_TEXT
    assert [
        (card.value_label.text(), card.secondary_label.text()) for card in run._readout_row.panels
    ] == [
        (readout.value, readout.secondary) for readout in readouts(at_60_s, DEFAULT_PLAYBACK_RATE)
    ]
    assert _accounting_reading(panel) == _accounting_of(at_60_s)
    assert schematic.name_text.text() == "At 1m of simulated time"
    assert cost_view.panels[0].name_text.text() == "At 1m of simulated time"


def test_a_view_that_cannot_draw_the_frame_a_halt_tries_again_leaves_every_view_on_one_frame(
    application: QApplication,
) -> None:
    """A View placed before one that raises is not left on a frame the readouts never showed.

    An accounting View sits before the concentration chart in reading order,
    and a second one sits after it. The first frame draws the run at 60 s.
    From then on the chart raises on every frame it is handed. On the frame
    at 120 s the first accounting View writes its panel, and then the chart
    raises. The halt tries the frame again, and the same happens. Before the
    fix, the first accounting View was left showing the amounts at 120 s,
    beside readouts and a second accounting View that showed 60 s (blind
    review of `PL-RF2S`).

    After the halt, the readouts and both accounting Views must show the
    frame at 60 s, the last whose readouts were written. The expected cards
    and amounts are those of a second run built directly and stepped to 60 s.
    """

    controller = _fresh_run(60.0)
    view = _shown_view(application, controller)
    run = view.runs[0]
    view.layout_container.choose_view(AreaId(4), AGENT_ACCOUNTING)
    _settle(application)
    kinds = [type(shown) for shown in view.layout_container.views()]
    before_the_chart, after_the_chart = (
        shown.panels[0]
        for shown in view.layout_container.views()
        if isinstance(shown, AccountingView)
    )
    assert kinds.index(AccountingView) < kinds.index(ConcentrationView)
    written_before_the_chart: list[str] = []

    def refusing(frame: ChartFrame) -> None:
        written_before_the_chart.append(before_the_chart._agent_amounts_text.text())
        raise ValueError("the chart could not draw this frame")

    _concentration(view).chart.draw = refusing  # type: ignore[method-assign]
    controller.start()
    _advance(controller, 60.0)
    later = accounting(controller.snapshot()).amounts
    at_60_s = _fresh_run(60.0).snapshot()

    view.present(False)

    assert later != accounting(at_60_s).amounts
    assert written_before_the_chart == [later, later], (
        "the first accounting View did not write the frame at 120 s before the chart raised, "
        "on the frame and on the halt's second attempt"
    )
    assert controller.has_failed is True
    assert run._status_text.text() == STATUS_FAILED_TEXT
    assert [
        (panel.value_label.text(), panel.secondary_label.text())
        for panel in run._readout_row.panels
    ] == [
        (readout.value, readout.secondary) for readout in readouts(at_60_s, DEFAULT_PLAYBACK_RATE)
    ]
    assert _accounting_reading(after_the_chart) == _accounting_of(at_60_s)
    assert _accounting_reading(before_the_chart) == _accounting_of(at_60_s)


def test_a_halt_whose_dials_and_1_mac_line_cannot_be_built_is_still_stated(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A record whose MAC is a bare number still shows its halt, with no 1 MAC line.

    The dials and the 1 MAC line both refuse a MAC that was not built as
    `MacPercent`, with a `TypeError`. When that exception left the builder,
    nothing of the halt was written, and the panel went on showing the run
    as it was before it failed (blind review of `PL-RF2S`). The halt is now
    written without the two parts, and the 1 MAC line is cleared.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    assert run._one_mac_text.text() == "1 MAC sevoflurane = 2.0%"
    record = controller.record

    def record_with_an_unchecked_mac() -> RunRecord:
        return replace(record(), agent_mac_percent=2.0)  # type: ignore[arg-type]

    controller.record = record_with_an_unchecked_mac  # type: ignore[method-assign]
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    with pytest.raises(TypeError, match="mac_percent of 2.0 was not built as MacPercent"):
        view.present(False)

    assert controller.has_failed is True
    assert run._status_text.text() == STATUS_FAILED_TEXT
    notice = run._notice_text.notice()
    assert notice is not None
    assert "RuntimeError: this frame could not be assembled" in notice
    assert run._pause_button.isEnabled() is False
    assert run._start_button.isEnabled() is False
    assert run._one_mac_text.text() == ""
    assert run.owes_a_frame is False


def test_a_halt_that_cannot_be_stated_is_not_tried_again_on_every_tick(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A halt whose statement cannot be built is attempted once, not on every render tick.

    Here the run's statement cannot be built. That is the part of its
    presentation that shows the agent, the status word, the transport and
    the control-change panel. A frame builds each run's statement before it
    assembles anything, so every frame fails there, and so does the
    statement of the halt that follows. Before the halt is built, the run's
    record is stored as the one last written. So the render ticks that
    follow find the run's record unchanged, build nothing and raise nothing.
    When the record was stored only by a halt that could be built, each tick
    tried the frame again and printed the same exception (adversarial review
    of `PL-RF2S`). The attempts are counted where the statement is built.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    statements: list[None] = []

    def no_statement(*args: object, **kwargs: object) -> NoReturn:
        statements.append(None)
        raise ValueError("this run could not be stated")

    monkeypatch.setattr(run_presentation_module, "run_statement", no_statement)

    with pytest.raises(ValueError, match="this run could not be stated"):
        view.present(False)

    assert controller.has_failed is True
    attempted = len(statements)
    assert attempted > 0

    for _ in range(5):
        view.render_tick()

    assert len(statements) == attempted
    assert run.owes_a_frame is False


def test_a_run_s_panel_refuses_a_presentation_built_for_another_run(
    application: QApplication,
) -> None:
    """One run's values cannot be written into the other run's panel.

    The second run is running and the first is not. The second run's
    presentation is refused by the first run's panel before anything is
    written, so the first panel still shows its own status word.
    """

    first = SimulationController()
    second = SimulationController()
    second.start()
    view = _shown_view(application, first, second)
    trunk, branch = view.runs
    own_status = trunk._status_text.text()
    assert branch._status_text.text() != own_status

    with pytest.raises(
        ValueError, match="a presentation built for Run 2 was given to the panel of Run 1"
    ):
        trunk.show_presentation(branch.presentation(second.snapshot()))

    assert trunk._status_text.text() == own_status
    assert trunk._start_button.isEnabled() is True


def test_a_run_s_dials_refuse_a_presentation_built_for_another_run(
    application: QApplication,
) -> None:
    """One run's settings cannot be written into the dials that change the other run.

    A row of dials asks for a change to the run it was built for. The second
    run's fresh gas flow is 2.0 L/min and the first run's is 4.0 L/min. The
    second run's presentation is refused by the first run's row before
    anything is written, so the first run's dials still show its own
    settings. Dials that showed 2.0 L/min here would change the run that
    holds 4.0 L/min.
    """

    first = SimulationController()
    second = SimulationController()
    second.set_fresh_gas_flow(FreshGasFlow(2.0))
    view = _shown_view(application, first, second)
    trunk, branch = view.runs
    row = _setting_row(trunk)
    own = _dial_readings(row)
    assert own[0][0] == "4.0 L/min"
    assert _dial_readings(_setting_row(branch))[0][0] == "2.0 L/min"

    with pytest.raises(
        ValueError, match="a presentation built for Run 2 was given to the dials of Run 1"
    ):
        row.show_dials(branch.presentation(second.snapshot()))

    assert _dial_readings(row) == own
    assert row.not_shown_text.isHidden() is True
