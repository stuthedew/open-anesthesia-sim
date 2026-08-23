"""Present the interactive volatile-agent simulation as a responsive dashboard.

This module is the visual boundary between the scientific simulation and the
user. It renders immutable controller snapshots, translates concentration
fractions to display percentages, and forwards user settings to the controller
without implementing physiological calculations or modifying model state
directly.
"""

import asyncio
from collections.abc import Callable

import flet as ft
import flet_charts as fch

from anesthesia_sim.app.controller import (
    SimulationController,
    SimulationHistorySample,
)
from anesthesia_sim.app.theme import (
    ACCENT,
    INK,
    MUTED,
    PANEL,
    PRIMARY,
    WARNING,
)
from anesthesia_sim.app_metadata import APP_DISPLAY_NAME, APP_VERSION
from anesthesia_sim.core.parameters import AGENT_DATA_FILENAMES, load_agent_parameters

SIMULATION_STEP_S = 0.1
INITIAL_CHART_WINDOW_S = 60.0
MAX_CHART_WINDOW_S = 300.0
CHART_HEIGHT = 360
COMPACT_PAGE_PADDING = 16
COMPACT_PANEL_PADDING = 14
COMPACT_PANEL_RADIUS = 10

MAX_FRESH_GAS_FLOW_L_MIN = 10.0
MAX_ALVEOLAR_VENTILATION_L_MIN = 12.0
MAX_CARDIAC_OUTPUT_L_MIN = 10.0
# Delivered-concentration max is agent-specific (real vaporizer dial
# capability), sourced from SimulationSnapshot.max_delivered_concentration_percent
# rather than a fixed constant here.

CIRCUIT_COLOR = PRIMARY
ALVEOLAR_COLOR = ACCENT
MIXED_VENOUS_COLOR = "#7C3AED"
VESSEL_RICH_COLOR = "#DC2626"
MUSCLE_COLOR = "#D97706"
FAT_COLOR = "#64748B"

# (agent_id, display_name) for every built-in agent, in AGENT_DATA_FILENAMES
# order. Loaded once at import time; each file is tiny and this avoids
# hardcoding display names that already live in the data files.
AVAILABLE_AGENTS: tuple[tuple[str, str], ...] = tuple(
    (agent_id, load_agent_parameters(agent_id).display_name) for agent_id in AGENT_DATA_FILENAMES
)


class SimulationView:
    """Render and update the volatile-agent patient interface.

    The view displays controller snapshots and forwards user interactions to
    the controller. It does not perform compartment calculations, agent
    accounting, or physiological state updates.

    Attributes:
        _page: Flet page hosting the interface.
        _controller: Controller that owns the simulation and read-only history.
    """

    def __init__(
        self,
        page: ft.Page,
        controller: SimulationController,
    ) -> None:
        """Initialize the interface and its visual controls.

        Args:
            page: Flet page that will host the dashboard.
            controller: Simulation controller supplying immutable snapshots.
        """

        self._page = page
        self._page.padding = COMPACT_PAGE_PADDING
        self._controller = controller
        initial_snapshot = controller.snapshot()

        self._status_text = ft.Text(
            "Paused",
            color=MUTED,
            weight=ft.FontWeight.BOLD,
        )
        self._elapsed_time_text = self._build_metric_value("0.0 s")
        self._circuit_concentration_text = self._build_metric_value("0.000%")
        self._alveolar_concentration_text = self._build_metric_value("0.000%")
        self._mixed_venous_concentration_text = self._build_metric_value("0.000%")
        self._vessel_rich_concentration_text = self._build_metric_value("0.000%")
        self._muscle_concentration_text = self._build_metric_value("0.000%")
        self._fat_concentration_text = self._build_metric_value("0.000%")

        self._agent_accounting_status_text = ft.Text(
            "Valid",
            color=ACCENT,
            size=20,
            weight=ft.FontWeight.BOLD,
        )
        self._agent_accounting_detail_text = ft.Text(
            "No unaccounted agent detected.",
            color=MUTED,
        )
        self._agent_amounts_text = ft.Text(
            ("Delivered: 0.000000 L | Exhausted: 0.000000 L | Stored: 0.000000 L"),
            color=MUTED,
        )

        self._fresh_gas_flow_text = ft.Text(
            (f"{initial_snapshot.fresh_gas_flow_l_min:.1f} L/min"),
            color=INK,
        )
        self._delivered_concentration_text = ft.Text(
            self._format_percent(initial_snapshot.delivered_concentration_fraction),
            color=INK,
        )
        self._alveolar_ventilation_text = ft.Text(
            (f"{initial_snapshot.alveolar_ventilation_l_min:.1f} L/min"),
            color=INK,
        )
        self._cardiac_output_text = ft.Text(
            (f"{initial_snapshot.cardiac_output_l_min:.1f} L/min"),
            color=INK,
        )

        self._circuit_series = self._build_chart_series(
            color=CIRCUIT_COLOR,
            stroke_width=3,
        )
        self._alveolar_series = self._build_chart_series(
            color=ALVEOLAR_COLOR,
            stroke_width=3,
            dash_pattern=[10, 4],
        )
        self._mixed_venous_series = self._build_chart_series(
            color=MIXED_VENOUS_COLOR,
            stroke_width=2,
            dash_pattern=[4, 3],
        )
        self._vessel_rich_series = self._build_chart_series(
            color=VESSEL_RICH_COLOR,
            stroke_width=2,
        )
        self._muscle_series = self._build_chart_series(
            color=MUSCLE_COLOR,
            stroke_width=2,
            dash_pattern=[2, 3],
        )
        self._fat_series = self._build_chart_series(
            color=FAT_COLOR,
            stroke_width=2,
            dash_pattern=[12, 4, 2, 4],
        )

        self._concentration_chart = fch.LineChart(
            data_series=[
                self._circuit_series,
                self._alveolar_series,
                self._mixed_venous_series,
                self._vessel_rich_series,
                self._muscle_series,
                self._fat_series,
            ],
            min_x=0,
            max_x=INITIAL_CHART_WINDOW_S,
            min_y=0,
            max_y=initial_snapshot.max_delivered_concentration_percent,
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

        self._agent_dropdown = ft.Dropdown(
            value=initial_snapshot.agent_id,
            options=[
                ft.dropdown.Option(key=agent_id, text=display_name)
                for agent_id, display_name in AVAILABLE_AGENTS
            ],
            width=180,
            on_select=self._handle_agent_change,
        )

        self._subtitle_text = ft.Text(
            self._format_subtitle(initial_snapshot.agent_display_name),
            color=MUTED,
        )
        self._delivered_concentration_label = ft.Text(
            self._format_delivered_label(initial_snapshot.agent_display_name),
            weight=ft.FontWeight.BOLD,
            color=INK,
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
        self._delivered_concentration_slider = ft.Slider(
            min=0,
            max=initial_snapshot.max_delivered_concentration_percent,
            value=(initial_snapshot.delivered_concentration_fraction * 100.0),
            label="{value}%",
            active_color=ACCENT,
            expand=True,
            on_change=(self._handle_delivered_concentration_change),
        )
        self._alveolar_ventilation_slider = ft.Slider(
            min=0,
            max=MAX_ALVEOLAR_VENTILATION_L_MIN,
            value=(initial_snapshot.alveolar_ventilation_l_min),
            label="{value} L/min",
            active_color=ACCENT,
            expand=True,
            on_change=(self._handle_alveolar_ventilation_change),
        )
        self._cardiac_output_slider = ft.Slider(
            min=0,
            max=MAX_CARDIAC_OUTPUT_L_MIN,
            value=initial_snapshot.cardiac_output_l_min,
            label="{value} L/min",
            active_color=ACCENT,
            expand=True,
            on_change=self._handle_cardiac_output_change,
        )

        self._refresh_view()

    def mount(self) -> None:
        """Mount the complete patient simulation dashboard."""

        self._page.add(
            ft.SafeArea(
                expand=True,
                content=ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    spacing=12,
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            APP_DISPLAY_NAME,
                                            size=26,
                                            weight=(ft.FontWeight.BOLD),
                                            color=INK,
                                        ),
                                        self._subtitle_text,
                                    ],
                                    spacing=2,
                                    tight=True,
                                ),
                                ft.Row(
                                    controls=[
                                        self._agent_dropdown,
                                        self._start_button,
                                        self._pause_button,
                                        self._reset_button,
                                        self._status_text,
                                    ],
                                    spacing=8,
                                    tight=True,
                                ),
                            ],
                            alignment=(ft.MainAxisAlignment.SPACE_BETWEEN),
                            wrap=True,
                        ),
                        self._build_parameter_controls(),
                        self._build_concentration_metrics(),
                        ft.ResponsiveRow(
                            controls=[
                                self._build_chart_panel(),
                                (self._build_agent_accounting_panel()),
                            ],
                            spacing=12,
                            run_spacing=12,
                        ),
                        ft.Text(
                            (
                                "Educational simulation only. "
                                "This idealized model is not a "
                                "clinical prediction, monitoring, "
                                "or dosing tool."
                            ),
                            color=WARNING,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                ),
            )
        )

    def start_simulation_timer(self) -> None:
        """Start the asynchronous simulation display timer."""

        self._page.run_task(self._run_simulation_timer)

    def _build_parameter_controls(
        self,
    ) -> ft.ResponsiveRow:
        """Build the simulation-setting controls.

        Returns:
            Responsive controls for fresh gas flow in L/min, delivered
            agent concentration in percent, alveolar ventilation in
            L/min, and cardiac output in L/min.
        """

        return ft.ResponsiveRow(
            controls=[
                self._build_parameter_panel(
                    "Fresh gas flow",
                    self._fresh_gas_flow_slider,
                    self._fresh_gas_flow_text,
                ),
                self._build_parameter_panel(
                    self._delivered_concentration_label,
                    self._delivered_concentration_slider,
                    self._delivered_concentration_text,
                ),
                self._build_parameter_panel(
                    "Alveolar ventilation",
                    self._alveolar_ventilation_slider,
                    self._alveolar_ventilation_text,
                ),
                self._build_parameter_panel(
                    "Cardiac output",
                    self._cardiac_output_slider,
                    self._cardiac_output_text,
                ),
            ]
        )

    def _build_parameter_panel(
        self,
        label: str | ft.Text,
        slider: ft.Slider,
        value_text: ft.Text,
    ) -> ft.Container:
        """Build one compact simulation-setting panel.

        Args:
            label: User-facing setting name, or a pre-built Text control
                for a label that changes later (e.g. names the agent).
            slider: Slider controlling the setting.
            value_text: Current value with its physical unit.

        Returns:
            Responsive setting panel.
        """

        label_control = (
            label
            if isinstance(label, ft.Text)
            else ft.Text(
                label,
                weight=ft.FontWeight.BOLD,
                color=INK,
            )
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    label_control,
                    ft.Row(
                        controls=[
                            slider,
                            value_text,
                        ]
                    ),
                ],
                spacing=4,
            ),
            bgcolor=PANEL,
            border_radius=COMPACT_PANEL_RADIUS,
            padding=12,
            col={
                "sm": 12,
                "md": 6,
                "lg": 3,
            },
        )

    def _build_concentration_metrics(
        self,
    ) -> ft.ResponsiveRow:
        """Build the compact concentration summary grid.

        Returns:
            Seven responsive panels containing simulated time in
            seconds and compartment values in percent.
        """

        return ft.ResponsiveRow(
            columns=14,
            controls=[
                self._build_metric_panel(
                    "Simulated time",
                    self._elapsed_time_text,
                ),
                self._build_metric_panel(
                    "Circuit / inspired",
                    self._circuit_concentration_text,
                ),
                self._build_metric_panel(
                    "Alveolar / end-tidal",
                    self._alveolar_concentration_text,
                ),
                self._build_metric_panel(
                    "Mixed venous",
                    self._mixed_venous_concentration_text,
                ),
                self._build_metric_panel(
                    "Vessel-rich group",
                    self._vessel_rich_concentration_text,
                ),
                self._build_metric_panel(
                    "Muscle",
                    self._muscle_concentration_text,
                ),
                self._build_metric_panel(
                    "Fat",
                    self._fat_concentration_text,
                ),
            ],
        )

    def _build_metric_panel(
        self,
        label: str,
        value_text: ft.Text,
    ) -> ft.Container:
        """Build one compact read-only metric panel.

        Args:
            label: User-facing metric name.
            value_text: Formatted value with its physical unit.

        Returns:
            Responsive metric panel.
        """

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        label,
                        color=MUTED,
                    ),
                    value_text,
                ],
                spacing=2,
            ),
            bgcolor=PANEL,
            border_radius=COMPACT_PANEL_RADIUS,
            padding=COMPACT_PANEL_PADDING,
            col={
                "sm": 14,
                "md": 7,
                "lg": 2,
            },
        )

    def _build_chart_panel(self) -> ft.Container:
        """Build the multitrace compartment chart.

        Returns:
            Responsive chart panel with time in seconds and
            concentration or relative partial pressure in percent.
        """

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        ("Agent concentration and relative partial pressure over time"),
                        weight=ft.FontWeight.BOLD,
                        color=INK,
                    ),
                    ft.Text(
                        ("Vertical axis: percent | Horizontal axis: simulated seconds"),
                        color=MUTED,
                    ),
                    ft.Row(
                        controls=[
                            self._build_legend_item(
                                "Circuit",
                                CIRCUIT_COLOR,
                                "solid",
                            ),
                            self._build_legend_item(
                                "Alveolar",
                                ALVEOLAR_COLOR,
                                "long dash",
                            ),
                            self._build_legend_item(
                                "Mixed venous",
                                MIXED_VENOUS_COLOR,
                                "short dash",
                            ),
                            self._build_legend_item(
                                "Vessel-rich",
                                VESSEL_RICH_COLOR,
                                "solid",
                            ),
                            self._build_legend_item(
                                "Muscle",
                                MUSCLE_COLOR,
                                "dotted",
                            ),
                            self._build_legend_item(
                                "Fat",
                                FAT_COLOR,
                                "dash-dot",
                            ),
                        ],
                        wrap=True,
                        spacing=16,
                        run_spacing=6,
                    ),
                    ft.Container(
                        height=CHART_HEIGHT,
                        content=self._concentration_chart,
                    ),
                ]
            ),
            bgcolor=PANEL,
            border_radius=COMPACT_PANEL_RADIUS,
            padding=COMPACT_PANEL_PADDING,
            col={
                "sm": 12,
                "lg": 9,
            },
        )

    def _build_agent_accounting_panel(
        self,
    ) -> ft.Container:
        """Build the agent-conservation diagnostic panel.

        Returns:
            Responsive validation panel containing agent amounts in
            equivalent liters of agent gas.
        """

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Agent accounting validation",
                        weight=ft.FontWeight.BOLD,
                        color=INK,
                    ),
                    self._agent_accounting_status_text,
                    self._agent_accounting_detail_text,
                    self._agent_amounts_text,
                ]
            ),
            bgcolor=PANEL,
            border_radius=COMPACT_PANEL_RADIUS,
            padding=COMPACT_PANEL_PADDING,
            col={
                "sm": 12,
                "lg": 3,
            },
        )

    @staticmethod
    def _build_chart_series(
        color: str,
        stroke_width: float,
        dash_pattern: list[int] | None = None,
    ) -> fch.LineChartData:
        """Build one visual series for the compartment chart.

        Args:
            color: Hexadecimal line color.
            stroke_width: Line width in display pixels.
            dash_pattern: Optional alternating dash and gap lengths
                in display pixels.

        Returns:
            Configured Flet line-chart series.
        """

        return fch.LineChartData(
            points=[
                fch.LineChartDataPoint(
                    0.0,
                    0.0,
                )
            ],
            color=color,
            stroke_width=stroke_width,
            dash_pattern=dash_pattern,
            curved=False,
            point=False,
        )

    @staticmethod
    def _build_legend_item(
        label: str,
        color: str,
        line_style: str,
    ) -> ft.Row:
        """Build one compact chart legend entry.

        Args:
            label: Modeled compartment name.
            color: Hexadecimal chart-line color.
            line_style: Text description of the line pattern.

        Returns:
            Tightly sized chart legend entry.
        """

        return ft.Row(
            controls=[
                ft.Container(
                    width=24,
                    height=4,
                    bgcolor=color,
                ),
                ft.Text(
                    f"{label} ({line_style})",
                    color=INK,
                ),
            ],
            spacing=6,
            tight=True,
        )

    def _refresh_view(self) -> None:
        """Refresh every visible value from one controller snapshot."""

        snapshot = self._controller.snapshot()

        self._subtitle_text.value = self._format_subtitle(snapshot.agent_display_name)
        self._delivered_concentration_label.value = self._format_delivered_label(
            snapshot.agent_display_name
        )
        self._agent_dropdown.value = snapshot.agent_id
        self._agent_dropdown.disabled = snapshot.is_running

        self._delivered_concentration_slider.max = snapshot.max_delivered_concentration_percent
        self._delivered_concentration_slider.value = (
            snapshot.delivered_concentration_fraction * 100.0
        )
        self._concentration_chart.max_y = snapshot.max_delivered_concentration_percent

        self._status_text.value = "Running" if snapshot.is_running else "Paused"
        self._status_text.color = ACCENT if snapshot.is_running else MUTED
        self._elapsed_time_text.value = f"{snapshot.elapsed_s:.1f} s"
        self._circuit_concentration_text.value = self._format_percent(
            snapshot.circuit_concentration_fraction
        )
        self._alveolar_concentration_text.value = self._format_percent(
            snapshot.alveolar_concentration_fraction
        )
        self._mixed_venous_concentration_text.value = self._format_percent(
            snapshot.mixed_venous_concentration_fraction
        )
        self._vessel_rich_concentration_text.value = self._format_percent(
            snapshot.vessel_rich_partial_pressure_fraction
        )
        self._muscle_concentration_text.value = self._format_percent(
            snapshot.muscle_partial_pressure_fraction
        )
        self._fat_concentration_text.value = self._format_percent(
            snapshot.fat_partial_pressure_fraction
        )

        self._fresh_gas_flow_text.value = f"{snapshot.fresh_gas_flow_l_min:.1f} L/min"
        self._delivered_concentration_text.value = self._format_percent(
            snapshot.delivered_concentration_fraction
        )
        self._alveolar_ventilation_text.value = f"{snapshot.alveolar_ventilation_l_min:.1f} L/min"
        self._cardiac_output_text.value = f"{snapshot.cardiac_output_l_min:.1f} L/min"

        self._start_button.disabled = snapshot.is_running
        self._pause_button.disabled = not snapshot.is_running

        if snapshot.agent_accounting_passes_validation:
            self._agent_accounting_status_text.value = "Valid"
            self._agent_accounting_status_text.color = ACCENT
            self._agent_accounting_detail_text.value = (
                "The simulation still accounts for all delivered agent."
            )
        else:
            self._agent_accounting_status_text.value = "Validation failed"
            self._agent_accounting_status_text.color = WARNING
            self._agent_accounting_detail_text.value = (
                "The simulation has detected unaccounted agent."
            )

        self._agent_amounts_text.value = (
            f"Delivered: "
            f"{snapshot.delivered_agent_l:.6f} L\n"
            f"Exhausted: "
            f"{snapshot.exhausted_agent_l:.6f} L\n"
            f"Stored: "
            f"{snapshot.stored_agent_l:.6f} L\n"
            f"Unaccounted: "
            f"{snapshot.unaccounted_agent_l:.3e} L\n"
            f"Absolute error: "
            f"{snapshot.agent_accounting_absolute_error_l:.3e} L"
        )

        history = snapshot.concentration_history

        self._circuit_series.points = self._history_points(
            history,
            lambda sample: sample.circuit_concentration_fraction,
        )
        self._alveolar_series.points = self._history_points(
            history,
            lambda sample: sample.alveolar_concentration_fraction,
        )
        self._mixed_venous_series.points = self._history_points(
            history,
            lambda sample: sample.mixed_venous_concentration_fraction,
        )
        self._vessel_rich_series.points = self._history_points(
            history,
            lambda sample: sample.vessel_rich_partial_pressure_fraction,
        )
        self._muscle_series.points = self._history_points(
            history,
            lambda sample: sample.muscle_partial_pressure_fraction,
        )
        self._fat_series.points = self._history_points(
            history,
            lambda sample: sample.fat_partial_pressure_fraction,
        )

        chart_max_x = max(
            INITIAL_CHART_WINDOW_S,
            snapshot.elapsed_s + 10.0,
        )
        self._concentration_chart.max_x = chart_max_x
        self._concentration_chart.min_x = max(
            0.0,
            chart_max_x - MAX_CHART_WINDOW_S,
        )

    @staticmethod
    def _history_points(
        history: tuple[SimulationHistorySample, ...],
        value_for: Callable[
            [SimulationHistorySample],
            float,
        ],
    ) -> list[fch.LineChartDataPoint]:
        """Convert recorded fractions to chart percentages.

        Args:
            history: Immutable simulation samples with elapsed time
                in seconds and compartment values as fractions.
            value_for: Function selecting one fraction from a sample.

        Returns:
            Chart points with time in seconds and the selected value
            converted from a fraction to percent.
        """

        return [
            fch.LineChartDataPoint(
                sample.elapsed_s,
                value_for(sample) * 100.0,
            )
            for sample in history
        ]

    def _refresh_and_render(self) -> None:
        """Refresh the dashboard and submit it to the Flet page."""

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

    def _handle_agent_change(
        self,
        event: ft.Event[ft.Dropdown],
    ) -> None:
        if event.control.value is None:
            return

        self._controller.set_agent(event.control.value)
        self._refresh_and_render()

    def _handle_fresh_gas_flow_change(
        self,
        event: ft.Event[ft.Slider],
    ) -> None:
        if event.control.value is None:
            return

        self._controller.set_fresh_gas_flow(float(event.control.value))
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

    def _handle_alveolar_ventilation_change(
        self,
        event: ft.Event[ft.Slider],
    ) -> None:
        if event.control.value is None:
            return

        self._controller.set_alveolar_ventilation(float(event.control.value))
        self._refresh_and_render()

    def _handle_cardiac_output_change(
        self,
        event: ft.Event[ft.Slider],
    ) -> None:
        if event.control.value is None:
            return

        self._controller.set_cardiac_output(float(event.control.value))
        self._refresh_and_render()

    async def _run_simulation_timer(self) -> None:
        """Advance and redraw the running simulation every 0.1 seconds."""

        while True:
            await asyncio.sleep(SIMULATION_STEP_S)

            if self._controller.is_running:
                self._controller.advance(SIMULATION_STEP_S)
                self._refresh_and_render()

    @staticmethod
    def _build_metric_value(
        initial_value: str,
    ) -> ft.Text:
        """Build a formatted dashboard metric.

        Args:
            initial_value: Initial formatted value including its
                physical unit.

        Returns:
            Styled Flet text control.
        """

        return ft.Text(
            initial_value,
            size=22,
            weight=ft.FontWeight.BOLD,
            color=INK,
        )

    @staticmethod
    def _format_percent(
        concentration_fraction: float,
    ) -> str:
        """Convert a concentration fraction to display percent.

        Args:
            concentration_fraction: Dimensionless concentration
                fraction from zero through one.

        Returns:
            Concentration formatted as percent with three decimal
            places.
        """

        return f"{concentration_fraction * 100.0:.3f}%"

    @staticmethod
    def _format_subtitle(agent_display_name: str) -> str:
        """Build the header subtitle naming the current app version and agent."""

        return f"Version {APP_VERSION} — {agent_display_name} patient model"

    @staticmethod
    def _format_delivered_label(agent_display_name: str) -> str:
        """Build the delivered-concentration panel label naming the agent."""

        return f"Delivered {agent_display_name.lower()}"
