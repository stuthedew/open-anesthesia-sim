"""Unit tests for the presentation logic in SimulationView.

These tests exercise formatting, unit conversion, and controller-wiring
without a live Flet client. Flet's individual controls (Text, Slider,
Event, chart series, ...) can be constructed and inspected as plain Python
objects; only a live Page/Session is needed to actually flush updates to a
browser. `_FakePage` stands in for exactly the two Page behaviors
SimulationView touches outside of `mount()` and `start_simulation_timer()`
(which this suite does not call and does not claim to cover): the
`padding` attribute and the `update()` call.
"""

import asyncio
import contextlib

import flet as ft
import flet_charts as fch
import pytest

from anesthesia_sim.app.controller import (
    SimulationController,
    SimulationHistorySample,
    SimulationSnapshot,
)
from anesthesia_sim.app.simulation_view import (
    MAX_CHART_POINTS_PER_SERIES,
    RENDER_INTERVAL_S,
    SIMULATION_STEP_S,
    SimulationView,
)
from anesthesia_sim.app.theme import ACCENT, MUTED, WARNING


class _FakePage:
    """Stand-in exposing only what SimulationView uses outside of mount()."""

    def __init__(self) -> None:
        self.padding: int | None = None
        self.update_calls = 0

    def update(self) -> None:
        self.update_calls += 1


class _FakeController:
    """Stand-in with a caller-controlled snapshot.

    Isolates view-formatting tests from the simulation engine so the
    accounting-failed branch can be exercised without needing to actually
    violate a physical invariant.
    """

    def __init__(self, snapshot: SimulationSnapshot) -> None:
        self.snapshot_value = snapshot
        self.is_running = snapshot.is_running

    def snapshot(self) -> SimulationSnapshot:
        return self.snapshot_value


def _sample(
    elapsed_s: float,
    circuit: float,
    alveolar: float,
    venous: float,
    vessel_rich: float,
    muscle: float,
    fat: float,
) -> SimulationHistorySample:
    return SimulationHistorySample(
        elapsed_s=elapsed_s,
        circuit_concentration_fraction=circuit,
        alveolar_concentration_fraction=alveolar,
        mixed_venous_concentration_fraction=venous,
        vessel_rich_partial_pressure_fraction=vessel_rich,
        muscle_partial_pressure_fraction=muscle,
        fat_partial_pressure_fraction=fat,
    )


def _snapshot(
    is_running: bool = False,
    circuit_time_constant_s: float = 90.0,
    passes_validation: bool = True,
    history: tuple[SimulationHistorySample, ...] | None = None,
    agent_id: str = "sevoflurane",
    agent_display_name: str = "Sevoflurane",
    max_delivered_concentration_percent: float = 8.0,
) -> SimulationSnapshot:
    if history is None:
        history = (_sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),)

    latest = history[-1]

    return SimulationSnapshot(
        is_running=is_running,
        elapsed_s=latest.elapsed_s,
        agent_id=agent_id,
        agent_display_name=agent_display_name,
        max_delivered_concentration_percent=max_delivered_concentration_percent,
        circuit_volume_l=6.0,
        fresh_gas_flow_l_min=4.0,
        delivered_concentration_fraction=0.08,
        alveolar_ventilation_l_min=4.0,
        cardiac_output_l_min=5.0,
        circuit_concentration_fraction=latest.circuit_concentration_fraction,
        alveolar_concentration_fraction=latest.alveolar_concentration_fraction,
        mixed_venous_concentration_fraction=latest.mixed_venous_concentration_fraction,
        vessel_rich_partial_pressure_fraction=latest.vessel_rich_partial_pressure_fraction,
        muscle_partial_pressure_fraction=latest.muscle_partial_pressure_fraction,
        fat_partial_pressure_fraction=latest.fat_partial_pressure_fraction,
        circuit_time_constant_s=circuit_time_constant_s,
        delivered_agent_l=0.012345,
        exhausted_agent_l=0.002345,
        stored_agent_l=0.01,
        unaccounted_agent_l=1.5e-13,
        agent_accounting_absolute_error_l=1.5e-13,
        agent_accounting_passes_validation=passes_validation,
        concentration_history=history,
    )


def _build_view(snapshot: SimulationSnapshot) -> tuple[SimulationView, _FakePage]:
    page = _FakePage()
    view = SimulationView(page=page, controller=_FakeController(snapshot))
    return view, page


def test_format_percent_uses_three_decimal_places() -> None:
    assert SimulationView._format_percent(0.0) == "0.000%"
    assert SimulationView._format_percent(1.0) == "100.000%"
    assert SimulationView._format_percent(0.0803456) == "8.035%"


def test_refresh_view_formats_every_concentration_metric() -> None:
    snapshot = _snapshot(
        history=(_sample(12.5, 0.02345, 0.01234, 0.00456, 0.00789, 0.00321, 0.00012),)
    )
    view, _ = _build_view(snapshot)

    assert view._elapsed_time_text.value == "12.5 s"
    assert view._circuit_concentration_text.value == "2.345%"
    assert view._alveolar_concentration_text.value == "1.234%"
    assert view._mixed_venous_concentration_text.value == "0.456%"
    assert view._vessel_rich_concentration_text.value == "0.789%"
    assert view._muscle_concentration_text.value == "0.321%"
    assert view._fat_concentration_text.value == "0.012%"
    assert view._fresh_gas_flow_text.value == "4.0 L/min"
    assert view._delivered_concentration_text.value == "8.000%"
    assert view._alveolar_ventilation_text.value == "4.0 L/min"
    assert view._cardiac_output_text.value == "5.0 L/min"


@pytest.mark.parametrize(
    ("is_running", "expected_status", "expected_start_disabled", "expected_pause_disabled"),
    [
        (True, "Running", True, False),
        (False, "Paused", False, True),
    ],
)
def test_refresh_view_reflects_running_state(
    is_running: bool,
    expected_status: str,
    expected_start_disabled: bool,
    expected_pause_disabled: bool,
) -> None:
    view, _ = _build_view(_snapshot(is_running=is_running))

    assert view._status_text.value == expected_status
    assert view._status_text.color == (ACCENT if is_running else MUTED)
    assert view._start_button.disabled is expected_start_disabled
    assert view._pause_button.disabled is expected_pause_disabled


def test_refresh_view_populates_chart_series_from_history() -> None:
    history = (
        _sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        _sample(0.1, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06),
        _sample(0.2, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12),
    )
    view, _ = _build_view(_snapshot(history=history))

    for series, attribute in (
        (view._circuit_series, "circuit_concentration_fraction"),
        (view._alveolar_series, "alveolar_concentration_fraction"),
        (view._mixed_venous_series, "mixed_venous_concentration_fraction"),
        (view._vessel_rich_series, "vessel_rich_partial_pressure_fraction"),
        (view._muscle_series, "muscle_partial_pressure_fraction"),
        (view._fat_series, "fat_partial_pressure_fraction"),
    ):
        assert len(series.points) == len(history)

        for point, sample in zip(series.points, history, strict=True):
            assert point.x == pytest.approx(sample.elapsed_s)
            assert point.y == pytest.approx(getattr(sample, attribute) * 100.0)


def test_refresh_view_reports_valid_agent_accounting() -> None:
    view, _ = _build_view(_snapshot(passes_validation=True))

    assert view._agent_accounting_status_text.value == "Valid"
    assert view._agent_accounting_status_text.color == ACCENT
    assert "still accounts for all delivered agent" in (view._agent_accounting_detail_text.value)
    assert view._agent_amounts_text.value == (
        "Delivered: 0.012345 L\n"
        "Exhausted: 0.002345 L\n"
        "Stored: 0.010000 L\n"
        "Unaccounted: 1.500e-13 L\n"
        "Absolute error: 1.500e-13 L"
    )


def test_refresh_view_reports_failed_agent_accounting() -> None:
    view, _ = _build_view(_snapshot(passes_validation=False))

    assert view._agent_accounting_status_text.value == "Validation failed"
    assert view._agent_accounting_status_text.color == WARNING
    assert "unaccounted agent" in view._agent_accounting_detail_text.value


def test_refresh_view_shows_current_agent_in_subtitle_and_dropdown() -> None:
    view, _ = _build_view(_snapshot(agent_id="isoflurane", agent_display_name="Isoflurane"))

    assert view._subtitle_text.value is not None
    assert "Isoflurane" in view._subtitle_text.value
    assert view._agent_dropdown.value == "isoflurane"


def test_refresh_view_scales_slider_and_chart_to_agent_max() -> None:
    """Real vaporizer caps differ per agent (e.g. desflurane 18% vs isoflurane 5%);
    the delivered-concentration slider and the chart's y-axis must track it."""

    view, _ = _build_view(
        _snapshot(
            agent_id="desflurane",
            agent_display_name="Desflurane",
            max_delivered_concentration_percent=18.0,
        )
    )

    assert view._delivered_concentration_slider.max == 18.0
    assert view._concentration_chart.max_y == 18.0


def test_refresh_view_disables_agent_dropdown_while_running() -> None:
    view, _ = _build_view(_snapshot(is_running=True))

    assert view._agent_dropdown.disabled is True


def test_refresh_view_updates_delivered_concentration_label_for_current_agent() -> None:
    """Regression test: this label was found hardcoded to "Delivered
    sevoflurane" during manual browser verification of agent switching,
    left stale even after selecting a different agent."""

    view, _ = _build_view(_snapshot(agent_id="desflurane", agent_display_name="Desflurane"))

    assert view._delivered_concentration_label.value == "Delivered desflurane"


def test_start_pause_reset_handlers_drive_the_real_controller() -> None:
    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)

    view._handle_start(ft.Event(name="click", control=view._start_button))

    assert controller.is_running is True
    assert view._status_text.value == "Running"
    assert view._start_button.disabled is True
    assert view._pause_button.disabled is False
    assert page.update_calls == 1

    controller.advance(1.0)
    view._handle_pause(ft.Event(name="click", control=view._pause_button))

    assert controller.is_running is False
    assert view._status_text.value == "Paused"
    assert page.update_calls == 2

    view._handle_reset(ft.Event(name="click", control=view._reset_button))

    assert controller.snapshot().elapsed_s == 0.0
    assert view._elapsed_time_text.value == "0.0 s"
    assert page.update_calls == 3


def test_agent_dropdown_handler_switches_the_real_controller() -> None:
    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    view._agent_dropdown.value = "desflurane"

    view._handle_agent_change(ft.Event(name="select", control=view._agent_dropdown))

    assert controller.snapshot().agent_id == "desflurane"
    assert view._agent_dropdown.value == "desflurane"
    assert view._subtitle_text.value is not None
    assert "Desflurane" in view._subtitle_text.value


def test_fresh_gas_flow_slider_forwards_value_to_controller() -> None:
    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    view._fresh_gas_flow_slider.value = 7.0

    view._handle_fresh_gas_flow_change(ft.Event(name="change", control=view._fresh_gas_flow_slider))

    assert controller.snapshot().fresh_gas_flow_l_min == 7.0
    assert view._fresh_gas_flow_text.value == "7.0 L/min"


def test_delivered_concentration_slider_converts_percent_to_fraction() -> None:
    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    view._delivered_concentration_slider.value = 6.5

    view._handle_delivered_concentration_change(
        ft.Event(name="change", control=view._delivered_concentration_slider)
    )

    assert controller.snapshot().delivered_concentration_fraction == pytest.approx(0.065)
    assert view._delivered_concentration_text.value == "6.500%"


def test_alveolar_ventilation_slider_forwards_value_to_controller() -> None:
    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    view._alveolar_ventilation_slider.value = 8.0

    view._handle_alveolar_ventilation_change(
        ft.Event(name="change", control=view._alveolar_ventilation_slider)
    )

    assert controller.snapshot().alveolar_ventilation_l_min == 8.0
    assert view._alveolar_ventilation_text.value == "8.0 L/min"


def test_cardiac_output_slider_forwards_value_to_controller() -> None:
    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    view._cardiac_output_slider.value = 6.5

    view._handle_cardiac_output_change(ft.Event(name="change", control=view._cardiac_output_slider))

    assert controller.snapshot().cardiac_output_l_min == 6.5
    assert view._cardiac_output_text.value == "6.5 L/min"


@pytest.mark.parametrize(
    "handler_name",
    [
        "_handle_fresh_gas_flow_change",
        "_handle_delivered_concentration_change",
        "_handle_alveolar_ventilation_change",
        "_handle_cardiac_output_change",
        "_handle_agent_change",
    ],
)
def test_change_handlers_ignore_a_none_value(handler_name: str) -> None:
    """Flet may report a control value of None mid-drag; handlers must be a no-op then."""

    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    before = controller.snapshot()

    unset_slider = ft.Slider(min=0, max=10)
    handler = getattr(view, handler_name)
    handler(ft.Event(name="change", control=unset_slider))

    assert controller.snapshot() == before
    assert page.update_calls == 0


def _run_history(sample_count: int) -> tuple[SimulationHistorySample, ...]:
    """A run of `sample_count` samples at the real 0.1 s simulation step."""

    return tuple(
        _sample(
            index * SIMULATION_STEP_S,
            0.08 * (1.0 - 0.5**index),
            0.07 * (1.0 - 0.5**index),
            0.06 * (1.0 - 0.5**index),
            0.05 * (1.0 - 0.5**index),
            0.04 * (1.0 - 0.5**index),
            0.03 * (1.0 - 0.5**index),
        )
        for index in range(sample_count)
    )


def _all_series(view: SimulationView) -> tuple[fch.LineChartData, ...]:
    return (
        view._circuit_series,
        view._alveolar_series,
        view._mixed_venous_series,
        view._vessel_rich_series,
        view._muscle_series,
        view._fat_series,
    )


@pytest.mark.parametrize("sample_count", [3_000, 6_000, 18_000])
def test_chart_payload_is_bounded_however_long_the_run(sample_count: int) -> None:
    """The render payload must not grow with the length of the run."""

    view, _ = _build_view(_snapshot(history=_run_history(sample_count)))

    for series in _all_series(view):
        assert len(series.points) <= MAX_CHART_POINTS_PER_SERIES


def test_chart_sends_only_samples_inside_the_visible_window() -> None:
    """Sending samples the axis clips is payload the client cannot show."""

    history = _run_history(6_000)
    view, _ = _build_view(_snapshot(history=history))

    window_start_s = view._concentration_chart.min_x
    assert window_start_s > 0.0

    for series in _all_series(view):
        assert all(point.x >= window_start_s for point in series.points)


def test_chart_right_edge_matches_the_numeric_readout() -> None:
    """A trace ending before the newest sample would contradict the metrics."""

    history = _run_history(6_000)
    latest = history[-1]
    view, _ = _build_view(_snapshot(history=history))

    for series, value in (
        (view._circuit_series, latest.circuit_concentration_fraction),
        (view._alveolar_series, latest.alveolar_concentration_fraction),
        (view._mixed_venous_series, latest.mixed_venous_concentration_fraction),
        (view._vessel_rich_series, latest.vessel_rich_partial_pressure_fraction),
        (view._muscle_series, latest.muscle_partial_pressure_fraction),
        (view._fat_series, latest.fat_partial_pressure_fraction),
    ):
        assert series.points[-1].x == pytest.approx(latest.elapsed_s)
        assert series.points[-1].y == pytest.approx(value * 100.0)

    assert view._circuit_concentration_text.value == SimulationView._format_percent(
        latest.circuit_concentration_fraction
    )


def test_chart_traces_stay_bound_to_their_own_compartment() -> None:
    """Each trace must plot its own quantity, decimation notwithstanding."""

    history = _run_history(6_000)
    view, _ = _build_view(_snapshot(history=history))

    # Distinct constant multiples in _run_history make a swapped pairing show
    # up as a trace whose values belong to another compartment.
    for series, attribute in (
        (view._circuit_series, "circuit_concentration_fraction"),
        (view._alveolar_series, "alveolar_concentration_fraction"),
        (view._mixed_venous_series, "mixed_venous_concentration_fraction"),
        (view._vessel_rich_series, "vessel_rich_partial_pressure_fraction"),
        (view._muscle_series, "muscle_partial_pressure_fraction"),
        (view._fat_series, "fat_partial_pressure_fraction"),
    ):
        by_time = {sample.elapsed_s: getattr(sample, attribute) for sample in history}

        for point in series.points:
            assert point.y == pytest.approx(by_time[point.x] * 100.0)


def test_chart_keeps_every_sample_of_a_short_run() -> None:
    """Decimation must not kick in before the budget is actually exceeded."""

    history = _run_history(50)
    view, _ = _build_view(_snapshot(history=history))

    for series in _all_series(view):
        assert len(series.points) == len(history)


def test_chart_points_are_recorded_samples_not_interpolations() -> None:
    history = _run_history(6_000)
    recorded_times = {sample.elapsed_s for sample in history}
    view, _ = _build_view(_snapshot(history=history))

    for series in _all_series(view):
        assert all(point.x in recorded_times for point in series.points)
        assert [point.x for point in series.points] == sorted(point.x for point in series.points)


def _run_briefly(coroutine_function, ticks: int, interval_s: float) -> None:
    """Run a never-ending view loop for roughly `ticks` of its own interval.

    The loops run forever by design, so each is started as a task, given a
    bounded amount of real time to tick, and then cancelled.
    """

    async def drive() -> None:
        task = asyncio.create_task(coroutine_function())
        await asyncio.sleep(interval_s * ticks + interval_s / 2.0)
        task.cancel()

        with contextlib.suppress(asyncio.CancelledError):
            await task

    asyncio.run(drive())


def test_simulation_loop_advances_without_rendering() -> None:
    """Stepping must not be gated on drawing."""

    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    controller.start()
    page.update_calls = 0

    _run_briefly(view._run_simulation_timer, ticks=3, interval_s=SIMULATION_STEP_S)

    # How many ticks land in a fixed slice of real time is up to the host, so
    # the claim under test is that stepping happened and drawing did not.
    assert controller.snapshot().elapsed_s > 0.0
    assert page.update_calls == 0


def test_render_loop_draws_without_advancing() -> None:
    """Drawing must not move simulation time."""

    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    controller.start()
    page.update_calls = 0

    _run_briefly(view._run_render_timer, ticks=2, interval_s=RENDER_INTERVAL_S)

    assert controller.snapshot().elapsed_s == 0.0
    assert page.update_calls >= 1


def test_neither_loop_does_anything_while_paused() -> None:
    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    page.update_calls = 0

    _run_briefly(view._run_simulation_timer, ticks=2, interval_s=SIMULATION_STEP_S)
    _run_briefly(view._run_render_timer, ticks=1, interval_s=RENDER_INTERVAL_S)

    assert controller.snapshot().elapsed_s == 0.0
    assert page.update_calls == 0


def test_simulation_time_does_not_depend_on_render_cadence() -> None:
    """Identical step counts must give identical results, however drawing goes.

    Simulation time is a function of steps taken, never of wall-clock time or
    of how long a frame took, so a slow or skipped redraw cannot perturb the
    trajectory.
    """

    page = _FakePage()
    controller = SimulationController()
    view = SimulationView(page=page, controller=controller)
    controller.start()

    _run_briefly(view._run_simulation_timer, ticks=5, interval_s=SIMULATION_STEP_S)
    stepped_by_the_loop = controller.snapshot()

    reference = SimulationController()
    reference.start()
    steps_taken = len(stepped_by_the_loop.concentration_history) - 1
    assert steps_taken > 0

    for _ in range(steps_taken):
        reference.advance(SIMULATION_STEP_S)

    assert stepped_by_the_loop.elapsed_s == pytest.approx(reference.snapshot().elapsed_s)
    assert stepped_by_the_loop.alveolar_concentration_fraction == pytest.approx(
        reference.snapshot().alveolar_concentration_fraction
    )
