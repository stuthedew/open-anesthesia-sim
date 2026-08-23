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

import flet as ft
import pytest

from anesthesia_sim.app.controller import (
    SimulationController,
    SimulationHistorySample,
    SimulationSnapshot,
)
from anesthesia_sim.app.simulation_view import SimulationView
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
) -> SimulationSnapshot:
    if history is None:
        history = (_sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),)

    latest = history[-1]

    return SimulationSnapshot(
        is_running=is_running,
        elapsed_s=latest.elapsed_s,
        agent_id=agent_id,
        agent_display_name=agent_display_name,
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
