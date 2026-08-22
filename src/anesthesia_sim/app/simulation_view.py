import asyncio

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
INITIAL_CHART_WINDOW_S = 30.0


class SimulationView:
    """Build and update the Flet interface for one simulation session."""

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
        self._simulated_time_text = ft.Text(
            "0.0 s",
            size=26,
            weight=ft.FontWeight.BOLD,
            color=INK,
        )
        self._response_text = ft.Text(
            "0.000",
            size=26,
            weight=ft.FontWeight.BOLD,
            color=INK,
        )
        self._time_constant_text = ft.Text(
            f"{initial_snapshot.time_constant_s:.0f} s",
            color=INK,
        )

        # The chart renders controller history. It never calculates model values.
        self._response_series = fch.LineChartData(
            points=[fch.LineChartDataPoint(0.0, 0.0)],
            color=PRIMARY,
            stroke_width=3,
            curved=False,
            point=False,
        )
        self._response_chart = fch.LineChart(
            data_series=[self._response_series],
            min_x=0,
            max_x=INITIAL_CHART_WINDOW_S,
            min_y=0,
            max_y=1.0,
            horizontal_grid_lines=fch.ChartGridLines(
                interval=0.2,
                color="#D9E2EC",
            ),
            vertical_grid_lines=fch.ChartGridLines(
                interval=5,
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
        self._time_constant_slider = ft.Slider(
            min=2,
            max=30,
            divisions=28,
            value=initial_snapshot.time_constant_s,
            label="{value} s",
            active_color=ACCENT,
            on_change=self._handle_time_constant_change,
        )

        self._refresh_view()

    def mount(self) -> None:
        """Add the complete simulation interface to the page."""

        self._page.add(
            ft.SafeArea(
                expand=True,
                content=ft.Column(
                    expand=True,
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
                        ft.Text(
                            "Time constant",
                            weight=ft.FontWeight.BOLD,
                            color=INK,
                        ),
                        ft.Row(
                            controls=[
                                self._time_constant_slider,
                                self._time_constant_text,
                            ]
                        ),
                        ft.Row(
                            controls=[
                                self._start_button,
                                self._pause_button,
                                self._reset_button,
                            ],
                            wrap=True,
                        ),
                        self._status_text,
                        ft.ResponsiveRow(
                            controls=[
                                self._build_metric_panel(
                                    "Simulated time",
                                    self._simulated_time_text,
                                ),
                                self._build_metric_panel(
                                    "Dimensionless response",
                                    self._response_text,
                                ),
                            ]
                        ),
                        self._build_chart_panel(),
                        ft.Text(
                            (
                                "Demonstration model only — not a physiological "
                                "or clinical simulation."
                            ),
                            color=WARNING,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                ),
            )
        )

    def start_simulation_timer(self) -> None:
        """Start the background task that advances a running simulation."""

        self._page.run_task(self._run_simulation_timer)

    def _build_chart_panel(self) -> ft.Container:
        """Build a chart panel that fills the remaining vertical space."""

        return ft.Container(
            expand=True,
            bgcolor=PANEL,
            border_radius=PANEL_RADIUS,
            padding=PANEL_PADDING,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Text(
                        "Dimensionless response over simulated time",
                        weight=ft.FontWeight.BOLD,
                        color=INK,
                    ),
                    self._response_chart,
                ],
            ),
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
            col={"sm": 12, "md": 6},
        )

    def _refresh_view(self) -> None:
        """Update every displayed control from one controller snapshot."""

        snapshot = self._controller.snapshot()

        self._status_text.value = "Running" if snapshot.is_running else "Paused"
        self._status_text.color = ACCENT if snapshot.is_running else MUTED

        self._simulated_time_text.value = f"{snapshot.elapsed_s:.1f} s"
        self._response_text.value = f"{snapshot.response_fraction:.3f}"
        self._time_constant_text.value = f"{snapshot.time_constant_s:.0f} s"

        self._start_button.disabled = snapshot.is_running
        self._pause_button.disabled = not snapshot.is_running

        self._response_series.points = [
            fch.LineChartDataPoint(elapsed_s, response_fraction)
            for elapsed_s, response_fraction in snapshot.response_history
        ]
        self._response_chart.max_x = max(
            INITIAL_CHART_WINDOW_S,
            snapshot.elapsed_s + 5.0,
        )

    def _refresh_and_render(self) -> None:
        """Read current state and redraw the visible page."""

        self._refresh_view()
        self._page.update()

    def _handle_start(self, event: ft.Event[ft.Button]) -> None:
        del event
        self._controller.start()
        self._refresh_and_render()

    def _handle_pause(self, event: ft.Event[ft.Button]) -> None:
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

    def _handle_time_constant_change(
        self,
        event: ft.Event[ft.Slider],
    ) -> None:
        if event.control.value is None:
            return

        self._controller.set_time_constant(float(event.control.value))
        self._refresh_and_render()

    async def _run_simulation_timer(self) -> None:
        while True:
            await asyncio.sleep(SIMULATION_STEP_S)

            if self._controller.is_running:
                # Wall-clock sleep schedules updates. Simulation time advances
                # only through this explicit, deterministic step.
                self._controller.advance(SIMULATION_STEP_S)
                self._refresh_and_render()
