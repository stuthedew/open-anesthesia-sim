import asyncio
from math import isinf

import flet as ft
import flet_charts as fch

from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.theme import (
    ACCENT,
    INK,
    MUTED,
    PANEL,
    PANEL_PADDING,
    PANEL_RADIUS,
    PRIMARY,
    WARNING,
)
from anesthesia_sim.app_metadata import APP_DISPLAY_NAME, APP_VERSION

SIMULATION_STEP_S = 0.1
INITIAL_CHART_WINDOW_S = 300.0
CHART_WIDTH_TO_HEIGHT_RATIO = 3.0
MAX_FRESH_GAS_FLOW_L_MIN = 10.0
MIN_CIRCUIT_VOLUME_L = 1.0
MAX_CIRCUIT_VOLUME_L = 10.0
MAX_DELIVERED_CONCENTRATION_PERCENT = 10.0


class SimulationView:
    """Build and update the Flet interface for circuit wash-in."""

    def __init__(
        self,
        page: ft.Page,
        controller: SimulationController,
    ) -> None:
        self._page = page
        self._controller = controller
        initial_snapshot = controller.snapshot()

        self._status_text = ft.Text(
            "Paused",
            color=MUTED,
            weight=ft.FontWeight.BOLD,
        )
        self._elapsed_time_text = self._build_metric_value("0.0 s")
        self._circuit_concentration_text = self._build_metric_value("0.000%")
        self._time_constant_text = self._build_metric_value("--")

        self._fresh_gas_flow_text = ft.Text(
            f"{initial_snapshot.fresh_gas_flow_l_min:.1f} L/min",
            color=INK,
        )
        self._circuit_volume_text = ft.Text(
            f"{initial_snapshot.circuit_volume_l:.1f} L",
            color=INK,
        )
        self._delivered_concentration_text = ft.Text(
            self._format_percent(initial_snapshot.delivered_concentration_fraction),
            color=INK,
        )

        self._concentration_series = fch.LineChartData(
            points=[fch.LineChartDataPoint(0.0, 0.0)],
            color=PRIMARY,
            stroke_width=3,
            curved=False,
            point=False,
        )
        self._concentration_chart = fch.LineChart(
            data_series=[self._concentration_series],
            min_x=0,
            max_x=INITIAL_CHART_WINDOW_S,
            min_y=0,
            max_y=MAX_DELIVERED_CONCENTRATION_PERCENT,
            horizontal_grid_lines=fch.ChartGridLines(
                interval=2,
                color="#D9E2EC",
            ),
            vertical_grid_lines=fch.ChartGridLines(
                interval=60,
                color="#D9E2EC",
            ),
            expand=True,
        )

        self._start_button = ft.Button(
            content="Start",
            on_click=self._handle_start,
        )
        self._pause_button = ft.Button(
            content="Pause",
            disabled=True,
            on_click=self._handle_pause,
        )
        self._reset_button = ft.OutlinedButton(
            content="Reset",
            on_click=self._handle_reset,
        )

        self._fresh_gas_flow_slider = ft.Slider(
            min=0,
            max=MAX_FRESH_GAS_FLOW_L_MIN,
            value=initial_snapshot.fresh_gas_flow_l_min,
            label="{value} L/min",
            active_color=ACCENT,
            expand=True,
            on_change=self._handle_fresh_gas_flow_change,
        )
        self._circuit_volume_slider = ft.Slider(
            min=MIN_CIRCUIT_VOLUME_L,
            max=MAX_CIRCUIT_VOLUME_L,
            value=initial_snapshot.circuit_volume_l,
            label="{value} L",
            active_color=ACCENT,
            expand=True,
            on_change=self._handle_circuit_volume_change,
        )
        self._delivered_concentration_slider = ft.Slider(
            min=0,
            max=MAX_DELIVERED_CONCENTRATION_PERCENT,
            value=(initial_snapshot.delivered_concentration_fraction * 100.0),
            label="{value}%",
            active_color=ACCENT,
            expand=True,
            on_change=(self._handle_delivered_concentration_change),
        )

        self._refresh_view()

    def mount(self) -> None:
        """Add the complete circuit interface to the page."""

        self._page.add(
            ft.SafeArea(
                expand=True,
                content=ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Text(
                            APP_DISPLAY_NAME,
                            size=30,
                            weight=ft.FontWeight.BOLD,
                            color=INK,
                        ),
                        ft.Text(
                            f"Version {APP_VERSION}",
                            color=MUTED,
                        ),
                        self._build_parameter_controls(),
                        ft.Row(
                            controls=[
                                self._start_button,
                                self._pause_button,
                                self._reset_button,
                                self._status_text,
                            ],
                            wrap=True,
                        ),
                        ft.ResponsiveRow(
                            controls=[
                                self._build_metric_panel(
                                    "Simulated time",
                                    self._elapsed_time_text,
                                ),
                                self._build_metric_panel(
                                    "Circuit concentration",
                                    self._circuit_concentration_text,
                                ),
                                self._build_metric_panel(
                                    "Circuit time constant",
                                    self._time_constant_text,
                                ),
                            ]
                        ),
                        self._build_chart_panel(),
                        ft.Text(
                            (
                                "Idealized breathing-circuit model "
                                "only - no patient uptake or "
                                "clinical predictions."
                            ),
                            color=WARNING,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                ),
            )
        )

    def start_simulation_timer(self) -> None:
        """Start the task that advances a running simulation."""

        self._page.run_task(self._run_simulation_timer)

    def _build_parameter_controls(self) -> ft.ResponsiveRow:
        return ft.ResponsiveRow(
            controls=[
                self._build_parameter_panel(
                    "Fresh gas flow",
                    self._fresh_gas_flow_slider,
                    self._fresh_gas_flow_text,
                ),
                self._build_parameter_panel(
                    "Circuit volume",
                    self._circuit_volume_slider,
                    self._circuit_volume_text,
                ),
                self._build_parameter_panel(
                    "Delivered concentration",
                    self._delivered_concentration_slider,
                    self._delivered_concentration_text,
                ),
            ]
        )

    def _build_parameter_panel(
        self,
        label: str,
        slider: ft.Slider,
        value_text: ft.Text,
    ) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        label,
                        weight=ft.FontWeight.BOLD,
                        color=INK,
                    ),
                    ft.Row(controls=[slider, value_text]),
                ]
            ),
            col={"sm": 12, "md": 4},
        )

    def _build_metric_panel(
        self,
        label: str,
        value_text: ft.Text,
    ) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(label, color=MUTED),
                    value_text,
                ]
            ),
            bgcolor=PANEL,
            border_radius=PANEL_RADIUS,
            padding=PANEL_PADDING,
            col={"sm": 12, "md": 4},
        )

    def _build_chart_panel(self) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        ("Circuit concentration over simulated time"),
                        weight=ft.FontWeight.BOLD,
                        color=INK,
                    ),
                    ft.Container(
                        aspect_ratio=(CHART_WIDTH_TO_HEIGHT_RATIO),
                        content=self._concentration_chart,
                    ),
                ]
            ),
            bgcolor=PANEL,
            border_radius=PANEL_RADIUS,
            padding=PANEL_PADDING,
        )

    def _refresh_view(self) -> None:
        snapshot = self._controller.snapshot()

        self._status_text.value = "Running" if snapshot.is_running else "Paused"
        self._status_text.color = ACCENT if snapshot.is_running else MUTED
        self._elapsed_time_text.value = f"{snapshot.elapsed_s:.1f} s"
        self._circuit_concentration_text.value = self._format_percent(
            snapshot.circuit_concentration_fraction
        )
        self._time_constant_text.value = (
            "Infinite (zero flow)"
            if isinf(snapshot.circuit_time_constant_s)
            else f"{snapshot.circuit_time_constant_s:.1f} s"
        )
        self._fresh_gas_flow_text.value = f"{snapshot.fresh_gas_flow_l_min:.1f} L/min"
        self._circuit_volume_text.value = f"{snapshot.circuit_volume_l:.1f} L"
        self._delivered_concentration_text.value = self._format_percent(
            snapshot.delivered_concentration_fraction
        )
        self._start_button.disabled = snapshot.is_running
        self._pause_button.disabled = not snapshot.is_running

        self._concentration_series.points = [
            fch.LineChartDataPoint(
                elapsed_s,
                concentration_fraction * 100.0,
            )
            for (
                elapsed_s,
                concentration_fraction,
            ) in snapshot.concentration_history
        ]
        self._concentration_chart.max_x = max(
            INITIAL_CHART_WINDOW_S,
            snapshot.elapsed_s + 60.0,
        )

    def _refresh_and_render(self) -> None:
        self._refresh_view()
        self._page.update()

    def _handle_start(
        self,
        event: ft.Event[ft.Button],
    ) -> None:
        del event
        self._controller.start()
        self._refresh_and_render()

    def _handle_pause(
        self,
        event: ft.Event[ft.Button],
    ) -> None:
        del event
        self._controller.pause()
        self._refresh_and_render()

    def _handle_reset(
        self,
        event: ft.Event[ft.OutlinedButton],
    ) -> None:
        del event
        self._controller.reset()
        self._refresh_and_render()

    def _handle_fresh_gas_flow_change(
        self,
        event: ft.Event[ft.Slider],
    ) -> None:
        if event.control.value is None:
            return

        self._controller.set_fresh_gas_flow(float(event.control.value))
        self._refresh_and_render()

    def _handle_circuit_volume_change(
        self,
        event: ft.Event[ft.Slider],
    ) -> None:
        if event.control.value is None:
            return

        self._controller.set_circuit_volume(float(event.control.value))
        self._refresh_and_render()

    def _handle_delivered_concentration_change(
        self,
        event: ft.Event[ft.Slider],
    ) -> None:
        if event.control.value is None:
            return

        delivered_concentration_fraction = float(event.control.value) / 100.0
        self._controller.set_delivered_concentration(delivered_concentration_fraction)
        self._refresh_and_render()

    async def _run_simulation_timer(self) -> None:
        while True:
            await asyncio.sleep(SIMULATION_STEP_S)

            if self._controller.is_running:
                # The timer schedules rendering. Model time advances
                # explicitly through the controller and core.
                self._controller.advance(SIMULATION_STEP_S)
                self._refresh_and_render()

    @staticmethod
    def _build_metric_value(
        initial_value: str,
    ) -> ft.Text:
        return ft.Text(
            initial_value,
            size=26,
            weight=ft.FontWeight.BOLD,
            color=INK,
        )

    @staticmethod
    def _format_percent(
        concentration_fraction: float,
    ) -> str:
        return f"{concentration_fraction * 100.0:.3f}%"
