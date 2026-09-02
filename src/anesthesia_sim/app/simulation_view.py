"""Present the interactive volatile-agent simulation as a responsive dashboard.

This module is the visual boundary between the scientific simulation and the
user. It renders immutable controller snapshots, translates concentration
fractions to display percentages, and forwards user settings to the controller
without implementing physiological calculations or modifying model state
directly.

It is also the only layer that can tell a user what a raise out of `core/`
means for what they are looking at, so both timer loops and every setting
callback are guarded. The two outcomes are deliberately different: a
refused setting leaves a trustworthy run alone and says the setting did
not take, while a raise from a step halts the run and says so, because the
alternative — an asyncio task dying behind a display that still reads
"Running" — leaves the reader no cue that the numbers stopped advancing.
"""

import asyncio
from collections.abc import Callable

import flet as ft
import flet_charts as fch

from anesthesia_sim.app.chart_downsampling import first_index_at_or_after, select_envelope_indices
from anesthesia_sim.app.controller import SimulationController, SimulationHistorySample
from anesthesia_sim.app.theme import (
    ACCENT,
    ACCENT_TEXT,
    AGENT_COLOR_SCHEMES,
    INK,
    MUTED,
    PANEL,
    PRIMARY,
    WARNING,
)
from anesthesia_sim.app_metadata import APP_DISPLAY_NAME, APP_VERSION
from anesthesia_sim.core.exceptions import AnesthesiaSimulationError
from anesthesia_sim.core.parameters import AGENT_DATA_FILENAMES, load_agent_parameters
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MINIMUM_CARDIAC_OUTPUT_L_MIN,
    MINIMUM_FRESH_GAS_FLOW_L_MIN,
)

# The step each simulation tick advances by. What range of steps is *supported*
# is `core/`'s to declare and no longer this module's: the operator split's
# applicability domain is `core.respiratory_system.MAXIMUM_SIMULATION_STEP_S`,
# and a step above it is refused there rather than displayed here. This is a
# cadence choice inside that domain, and it sits at the domain's ceiling
# deliberately - docs/MODEL.md § "Displayed precision" derives the two-decimal
# readout from the split's error at exactly this step, so a coarser step would
# make that derivation false while a finer one would cost frames without
# moving a displayed digit.
# `test_the_shipped_step_is_within_the_maximum_simulation_step` holds the
# relationship, so a cadence and a limit cannot drift apart unnoticed.
SIMULATION_STEP_S = 0.1
# Render cadence, deliberately independent of the simulation step. The two
# were previously the same 10 Hz tick, which made every redraw a gate on the
# next simulation step and on servicing the next button press.
RENDER_INTERVAL_S = 0.2
INITIAL_CHART_WINDOW_S = 60.0
MAX_CHART_WINDOW_S = 300.0
# Per-trace ceiling on points handed to the chart. Each point is a Flet
# control costing roughly 8 us to build, so this ceiling — not the length of
# the run — sets the cost of a frame. 300 points across a chart a few hundred
# pixels wide is already finer than the display can resolve.
MAX_CHART_POINTS_PER_SERIES = 300
CHART_HEIGHT = 360

# Displayed resolution for every modeled concentration and relative partial
# pressure, and for the delivered-agent setting shown beside its slider. Two
# decimals of a percent — 0.01 percentage points — is a recorded decision
# (PL-040), justified in `docs/MODEL.md` § "Displayed precision" against the
# measured error of the shipped operator split. The short version: the
# split disagrees with the independent solution by up to 5e-3 percentage
# points at the default flows and 1.2e-2 at the extreme corner of the
# settings envelope, so the second decimal is the uncertain digit — as the
# last displayed digit should be — and the third and beyond were noise.
# Changing this is a safety-critical change to how a clinical value reads,
# not a formatting preference: revise the documented basis with it.
CONCENTRATION_DISPLAY_DECIMALS = 2
# Smallest percentage-point difference the concentration readouts resolve.
CONCENTRATION_DISPLAY_RESOLUTION_PERCENT = 10.0**-CONCENTRATION_DISPLAY_DECIMALS

# Decimals shown on the flow sliders' drag labels, matching the ".1f L/min"
# readouts beside them. Flet's default is 0, which would make a slider's own
# label disagree with the text next to it mid-drag.
FLOW_DISPLAY_DECIMALS = 1

COMPACT_PAGE_PADDING = 16
COMPACT_PANEL_PADDING = 14
COMPACT_PANEL_RADIUS = 10

# How many readout panels stand side by side, by window width. Each panel
# spans one column, so this is the row's own column count rather than a span:
# the seven panels always divide the row evenly, and the row reflows instead
# of squeezing labels. The steps are set by the widest label a panel has to
# hold on one line, not by taste - `_build_concentration_metrics` carries the
# measurement and PL-8M05 the defect it fixes. Flet's breakpoint minima are
# xs 0, sm 576, md 768, lg 992, xl 1200, xxl 1400 CSS pixels; a width takes
# the largest step at or below it.
METRIC_GRID_COLUMNS: dict[ft.ResponsiveRowBreakpoint | str, int | float] = {
    ft.ResponsiveRowBreakpoint.XS: 1,
    ft.ResponsiveRowBreakpoint.MD: 2,
    ft.ResponsiveRowBreakpoint.LG: 4,
    ft.ResponsiveRowBreakpoint.XL: 7,
}

# The clinical gloss under a compartment name is deliberately smaller than the
# name above it. Which quantity the model computes is the primary claim; what
# a clinician would compare it against is a secondary one, and the type sizes
# say so. Same MUTED colour as the name, so this adds no pair to
# `tools/contrast_check.py`, and it stays normal text at WCAG's 4.5:1.
METRIC_NAME_SIZE = 14
METRIC_QUALIFIER_SIZE = 12
# A panel with no gloss still draws the line, so that every reading in the row
# sits on one baseline. A blank string collapses to zero height in Flutter,
# where a non-breaking space renders a full line of the qualifier's size -
# which keeps the spacer tied to that size rather than to a pixel constant
# somebody would have to re-measure after a font change.
EMPTY_METRIC_QUALIFIER = "\u00a0"

# The three flow sliders span the model's own supported input ranges, imported
# from `core/supported_ranges.py` rather than restated here. Until PL-0MLQ this
# module declared them, which made a presentation constant the only thing
# keeping a run inside the domain the verification gates cover: any other
# caller of `core/` could set a cardiac output of 1000 L/min and be given a
# number. They are the model's declaration now, this module offers exactly
# them, and `test_the_sliders_span_the_supported_input_ranges` holds the two
# together.
#
# Delivered-concentration max is agent-specific (real vaporizer dial
# capability), sourced from SimulationSnapshot.max_delivered_concentration_percent
# rather than a fixed constant here; its floor is below, because it is a
# percent where the core's own guard is a fraction.
MIN_DELIVERED_CONCENTRATION_PERCENT = 0.0

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

# Adding a built-in agent without a verified identification color would make
# the selector silently lose a safety cue. Fail at startup instead. This check
# concerns presentation metadata only; agent/scientific parameters remain in
# their validated data files.
if set(AGENT_COLOR_SCHEMES) != set(AGENT_DATA_FILENAMES):
    raise RuntimeError("AGENT_COLOR_SCHEMES must define exactly the built-in volatile agents")


# One named reader per plotted quantity. Named rather than inline so that the
# trace-to-quantity pairing in `_refresh_chart_series` reads as an explicit
# table: plotting a compartment's values on another compartment's line would
# be a presentation-correctness failure, and a table is auditable at a glance.
def _sample_elapsed_s(sample: SimulationHistorySample) -> float:
    return sample.elapsed_s


def _circuit_value(sample: SimulationHistorySample) -> float:
    return sample.circuit_concentration_fraction


def _alveolar_value(sample: SimulationHistorySample) -> float:
    return sample.alveolar_concentration_fraction


def _mixed_venous_value(sample: SimulationHistorySample) -> float:
    return sample.mixed_venous_concentration_fraction


def _vessel_rich_value(sample: SimulationHistorySample) -> float:
    return sample.vessel_rich_partial_pressure_fraction


def _muscle_value(sample: SimulationHistorySample) -> float:
    return sample.muscle_partial_pressure_fraction


def _fat_value(sample: SimulationHistorySample) -> float:
    return sample.fat_partial_pressure_fraction


class SimulationView:
    """Render and update the volatile-agent patient interface.

    The view displays controller snapshots and forwards user interactions to
    the controller. It does not perform compartment calculations, agent
    accounting, or physiological state updates.

    Attributes:
        _page: Flet page hosting the interface.
        _controller: Controller that owns the simulation and read-only history.
    """

    def __init__(self, page: ft.Page, controller: SimulationController) -> None:
        """Initialize the interface and its visual controls.

        Args:
            page: Flet page that will host the dashboard.
            controller: Simulation controller supplying immutable snapshots.
        """

        self._page = page
        self._page.padding = COMPACT_PAGE_PADDING
        self._controller = controller
        initial_snapshot = controller.snapshot()

        self._status_text = ft.Text("Paused", color=MUTED, weight=ft.FontWeight.BOLD)
        # Why the last setting change did not take, or None if it did. Held
        # in the view rather than the controller because a refused setting
        # changes nothing about the simulation — there is no core state for
        # it to belong to.
        self._rejected_setting_notice: str | None = None
        self._notice_text = ft.Text("", color=WARNING, weight=ft.FontWeight.BOLD, visible=False)
        self._elapsed_time_text = self._build_metric_value("0.0 s")
        # Placeholders come from the formatter rather than from literals, so
        # a change to the displayed resolution cannot leave the pre-run
        # reading disagreeing with every reading after it.
        empty_compartment = self._format_percent(0.0)
        self._circuit_concentration_text = self._build_metric_value(empty_compartment)
        self._alveolar_concentration_text = self._build_metric_value(empty_compartment)
        self._mixed_venous_concentration_text = self._build_metric_value(empty_compartment)
        self._vessel_rich_concentration_text = self._build_metric_value(empty_compartment)
        self._muscle_concentration_text = self._build_metric_value(empty_compartment)
        self._fat_concentration_text = self._build_metric_value(empty_compartment)

        self._agent_accounting_status_text = ft.Text(
            "Valid", color=ACCENT_TEXT, size=20, weight=ft.FontWeight.BOLD
        )
        self._agent_accounting_detail_text = ft.Text("No unaccounted agent detected.", color=MUTED)
        self._agent_amounts_text = ft.Text(
            ("Delivered: 0.000000 L | Exhausted: 0.000000 L | Stored: 0.000000 L"), color=MUTED
        )

        self._fresh_gas_flow_text = ft.Text(
            (f"{initial_snapshot.fresh_gas_flow_l_min:.1f} L/min"), color=INK
        )
        self._delivered_concentration_text = ft.Text(
            self._format_percent(initial_snapshot.delivered_concentration_fraction), color=INK
        )
        self._alveolar_ventilation_text = ft.Text(
            (f"{initial_snapshot.alveolar_ventilation_l_min:.1f} L/min"), color=INK
        )
        self._cardiac_output_text = ft.Text(
            (f"{initial_snapshot.cardiac_output_l_min:.1f} L/min"), color=INK
        )

        self._circuit_series = self._build_chart_series(color=CIRCUIT_COLOR, stroke_width=3)
        self._alveolar_series = self._build_chart_series(
            color=ALVEOLAR_COLOR, stroke_width=3, dash_pattern=[10, 4]
        )
        self._mixed_venous_series = self._build_chart_series(
            color=MIXED_VENOUS_COLOR, stroke_width=2, dash_pattern=[4, 3]
        )
        self._vessel_rich_series = self._build_chart_series(color=VESSEL_RICH_COLOR, stroke_width=2)
        self._muscle_series = self._build_chart_series(
            color=MUSCLE_COLOR, stroke_width=2, dash_pattern=[2, 3]
        )
        self._fat_series = self._build_chart_series(
            color=FAT_COLOR, stroke_width=2, dash_pattern=[12, 4, 2, 4]
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
            horizontal_grid_lines=fch.ChartGridLines(interval=2, color="#D9E2EC"),
            vertical_grid_lines=fch.ChartGridLines(interval=60, color="#D9E2EC"),
            expand=True,
        )

        self._start_button = ft.Button(content="Start", on_click=self._handle_start)
        self._pause_button = ft.Button(content="Pause", disabled=True, on_click=self._handle_pause)
        self._reset_button = ft.OutlinedButton(content="Reset", on_click=self._handle_reset)

        initial_agent_colors = AGENT_COLOR_SCHEMES[initial_snapshot.agent_id]
        self._agent_dropdown = ft.Dropdown(
            value=initial_snapshot.agent_id,
            options=[
                ft.dropdown.Option(
                    key=agent_id,
                    text=display_name,
                    style=ft.ButtonStyle(
                        bgcolor=AGENT_COLOR_SCHEMES[agent_id].fill,
                        color=AGENT_COLOR_SCHEMES[agent_id].foreground,
                    ),
                )
                for agent_id, display_name in AVAILABLE_AGENTS
            ],
            width=180,
            filled=True,
            fill_color=initial_agent_colors.fill,
            bgcolor=initial_agent_colors.fill,
            color=initial_agent_colors.foreground,
            text_style=ft.TextStyle(
                color=initial_agent_colors.foreground, weight=ft.FontWeight.BOLD
            ),
            border_color=initial_agent_colors.foreground,
            focused_border_color=initial_agent_colors.foreground,
            on_select=self._handle_agent_change,
        )

        self._subtitle_text = ft.Text(
            self._format_subtitle(initial_snapshot.agent_display_name),
            color=initial_agent_colors.foreground,
            weight=ft.FontWeight.BOLD,
        )
        # The badge is bordered in its own foreground color because the
        # sevoflurane fill is only 1.37:1 against the white panel: without a
        # border its edge effectively disappears, and the colored region a
        # reader is meant to recognize loses its shape.
        self._agent_header_badge = ft.Container(
            content=self._subtitle_text,
            bgcolor=initial_agent_colors.fill,
            border=ft.Border.all(1, initial_agent_colors.foreground),
            border_radius=COMPACT_PANEL_RADIUS,
            padding=6,
        )
        self._delivered_concentration_label = ft.Text(
            self._format_delivered_label(initial_snapshot.agent_display_name),
            weight=ft.FontWeight.BOLD,
            color=INK,
        )

        self._fresh_gas_flow_slider = ft.Slider(
            min=MINIMUM_FRESH_GAS_FLOW_L_MIN,
            max=MAXIMUM_FRESH_GAS_FLOW_L_MIN,
            value=initial_snapshot.fresh_gas_flow_l_min,
            label="{value} L/min",
            round=FLOW_DISPLAY_DECIMALS,
            active_color=ACCENT,
            expand=True,
            on_change=self._handle_fresh_gas_flow_change,
        )
        self._delivered_concentration_slider = ft.Slider(
            min=MIN_DELIVERED_CONCENTRATION_PERCENT,
            max=initial_snapshot.max_delivered_concentration_percent,
            value=(initial_snapshot.delivered_concentration_fraction * 100.0),
            label="{value}%",
            # The drag label is the same clinical value as the readout beside
            # it and must be read at the same resolution. Flet rounds this
            # label to whole numbers unless told otherwise, which would show
            # "2%" on a dial the readout reports as "2.40%" — two displayed
            # values of one quantity, disagreeing by up to half a percentage
            # point.
            round=CONCENTRATION_DISPLAY_DECIMALS,
            active_color=ACCENT,
            expand=True,
            on_change=(self._handle_delivered_concentration_change),
        )
        self._alveolar_ventilation_slider = ft.Slider(
            min=MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
            max=MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
            value=(initial_snapshot.alveolar_ventilation_l_min),
            label="{value} L/min",
            round=FLOW_DISPLAY_DECIMALS,
            active_color=ACCENT,
            expand=True,
            on_change=(self._handle_alveolar_ventilation_change),
        )
        self._cardiac_output_slider = ft.Slider(
            min=MINIMUM_CARDIAC_OUTPUT_L_MIN,
            max=MAXIMUM_CARDIAC_OUTPUT_L_MIN,
            value=initial_snapshot.cardiac_output_l_min,
            label="{value} L/min",
            round=FLOW_DISPLAY_DECIMALS,
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
                                        self._agent_header_badge,
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
                        # Directly under the run controls and above every
                        # displayed value, so a halted run is read before the
                        # values it explains: a completed step, but not a
                        # continuing one.
                        self._notice_text,
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
        """Start the simulation and render loops as independent tasks."""

        self._page.run_task(self._run_simulation_timer)
        self._page.run_task(self._run_render_timer)

    def _build_parameter_controls(self) -> ft.ResponsiveRow:
        """Build the simulation-setting controls.

        Returns:
            Responsive controls for fresh gas flow in L/min, delivered
            agent concentration in percent, alveolar ventilation in
            L/min, and cardiac output in L/min.
        """

        return ft.ResponsiveRow(
            controls=[
                self._build_parameter_panel(
                    "Fresh gas flow", self._fresh_gas_flow_slider, self._fresh_gas_flow_text
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
                    "Cardiac output", self._cardiac_output_slider, self._cardiac_output_text
                ),
            ]
        )

    def _build_parameter_panel(
        self, label: str | ft.Text, slider: ft.Slider, value_text: ft.Text
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
            else ft.Text(label, weight=ft.FontWeight.BOLD, color=INK)
        )

        return ft.Container(
            content=ft.Column(
                controls=[label_control, ft.Row(controls=[slider, value_text])], spacing=4
            ),
            bgcolor=PANEL,
            border_radius=COMPACT_PANEL_RADIUS,
            padding=12,
            col={"sm": 12, "md": 6, "lg": 3},
        )

    def _build_concentration_metrics(self) -> ft.ResponsiveRow:
        """Build the compact concentration summary grid.

        Each panel names a compartment on one line and, where one applies,
        glosses it on a smaller line beneath: "Alveolar" over
        "end-tidal-equivalent", "Circuit" over "inspired". The split is a
        safety decision before it is a typographic one. What the model
        computes is a compartment - the gas fraction of one perfectly-mixed
        alveolus, the mixed contents of the circuit - and what a clinician
        would set beside it on a monitor is a different, measured thing. Two
        lines at two sizes say which is which; one line joined by a slash
        offered them as alternative names for the same quantity, which is the
        modeled-versus-measured confusion `CLAUDE.md` forbids (PL-NV9W, then
        PL-8M05).

        It also lets every reading in the row share a baseline. `docs/MODEL.md`
        § "Displayed precision" says the six readouts "sit in one row and are
        read comparatively" - the reason for showing them together is that a
        reader can see "the circuit lead the alveoli lead the tissues" - and a
        label that wrapped where its neighbours did not pushed one reading out
        of that line. Splitting the two longest labels leaves no name long
        enough to wrap, and a panel with no gloss still draws the gloss line,
        so the seven blocks are the same height whatever they contain.

        The row then reflows rather than squeezing: seven across at 1200 CSS
        pixels and wider, four at 992, two at 768, one below that. Measured by
        rendering the running app at each step.

        Returns:
            Seven responsive panels containing simulated time in
            seconds and compartment values in percent.
        """

        return ft.ResponsiveRow(
            columns=METRIC_GRID_COLUMNS,
            controls=[
                self._build_metric_panel("Simulated time", None, self._elapsed_time_text),
                self._build_metric_panel("Circuit", "inspired", self._circuit_concentration_text),
                # "end-tidal-equivalent", never "end-tidal": the hedge is
                # required by docs/MODEL.md § "Minimum displayed outputs", and
                # the reason is stated there in terms - the phrase "must not
                # imply that airway sampling dynamics, dead space, or
                # capnography are modeled", none of which they are. Dead space,
                # airway sampling delay, shunt and V/Q mismatch are all in
                # MODEL.md's "Known limitations", so this value is not
                # end-tidal in any patient. End-tidal is the name of a
                # *measurement*, and this is the readout a clinician would most
                # readily set beside a real agent monitor, which is what makes
                # an unhedged label a presentation-safety defect rather than a
                # wording preference (PL-NV9W). Do not shorten it to fit a
                # layout; `test_the_alveolar_readout_is_labelled_end_tidal_equivalent`
                # holds the exact pair of strings.
                self._build_metric_panel(
                    "Alveolar", "end-tidal-equivalent", self._alveolar_concentration_text
                ),
                self._build_metric_panel(
                    "Mixed venous", None, self._mixed_venous_concentration_text
                ),
                self._build_metric_panel(
                    "Vessel-rich group", None, self._vessel_rich_concentration_text
                ),
                self._build_metric_panel("Muscle", None, self._muscle_concentration_text),
                self._build_metric_panel("Fat", None, self._fat_concentration_text),
            ],
        )

    def _build_metric_panel(
        self, name: str, qualifier: str | None, value_text: ft.Text
    ) -> ft.Container:
        """Build one compact read-only metric panel.

        Args:
            name: The modeled quantity this panel displays, in the model's own
                terms.
            qualifier: What a clinician would compare that quantity against,
                or None where nothing measured corresponds to it. Drawn
                smaller than the name, because it is the weaker claim of the
                two - see `_build_concentration_metrics`.
            value_text: Formatted value with its physical unit.

        Returns:
            Responsive metric panel.
        """

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(name, color=MUTED, size=METRIC_NAME_SIZE),
                    ft.Text(
                        qualifier if qualifier is not None else EMPTY_METRIC_QUALIFIER,
                        color=MUTED,
                        size=METRIC_QUALIFIER_SIZE,
                        italic=True,
                    ),
                    value_text,
                ],
                spacing=0,
            ),
            bgcolor=PANEL,
            border_radius=COMPACT_PANEL_RADIUS,
            padding=COMPACT_PANEL_PADDING,
            col=1,
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
                        ("Vertical axis: percent | Horizontal axis: simulated seconds"), color=MUTED
                    ),
                    ft.Row(
                        controls=[
                            self._build_legend_item("Circuit", CIRCUIT_COLOR, "solid"),
                            self._build_legend_item("Alveolar", ALVEOLAR_COLOR, "long dash"),
                            self._build_legend_item(
                                "Mixed venous", MIXED_VENOUS_COLOR, "short dash"
                            ),
                            self._build_legend_item("Vessel-rich", VESSEL_RICH_COLOR, "solid"),
                            self._build_legend_item("Muscle", MUSCLE_COLOR, "dotted"),
                            self._build_legend_item("Fat", FAT_COLOR, "dash-dot"),
                        ],
                        wrap=True,
                        spacing=16,
                        run_spacing=6,
                    ),
                    ft.Container(height=CHART_HEIGHT, content=self._concentration_chart),
                ]
            ),
            bgcolor=PANEL,
            border_radius=COMPACT_PANEL_RADIUS,
            padding=COMPACT_PANEL_PADDING,
            col={"sm": 12, "lg": 9},
        )

    def _build_agent_accounting_panel(self) -> ft.Container:
        """Build the agent-conservation diagnostic panel.

        Returns:
            Responsive validation panel containing agent amounts in
            equivalent liters of agent gas.
        """

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Agent accounting validation", weight=ft.FontWeight.BOLD, color=INK),
                    self._agent_accounting_status_text,
                    self._agent_accounting_detail_text,
                    self._agent_amounts_text,
                ]
            ),
            bgcolor=PANEL,
            border_radius=COMPACT_PANEL_RADIUS,
            padding=COMPACT_PANEL_PADDING,
            col={"sm": 12, "lg": 3},
        )

    @staticmethod
    def _build_chart_series(
        color: str, stroke_width: float, dash_pattern: list[int] | None = None
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
            points=[fch.LineChartDataPoint(0.0, 0.0)],
            color=color,
            stroke_width=stroke_width,
            dash_pattern=dash_pattern,
            curved=False,
            point=False,
        )

    @staticmethod
    def _build_legend_item(label: str, color: str, line_style: str) -> ft.Row:
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
                ft.Container(width=24, height=4, bgcolor=color),
                ft.Text(f"{label} ({line_style})", color=INK),
            ],
            spacing=6,
            tight=True,
        )

    def _refresh_view(self) -> None:
        """Refresh every visible value from one controller snapshot."""

        snapshot = self._controller.snapshot()

        self._subtitle_text.value = self._format_subtitle(snapshot.agent_display_name)
        self._apply_agent_color_scheme(snapshot.agent_id)
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

        has_failed = snapshot.failure_reason is not None

        # Three states, not two. A halted run must never render as a pause.
        # The core rolls a failed step back, so the numbers beside this word
        # are a completed step's - but the run cannot go on from them, and a
        # reader who sees "Paused" expects Start to resume it and reads a
        # stopped trajectory as one still in progress.
        if has_failed:
            self._status_text.value = "Stopped — simulation error"
            self._status_text.color = WARNING
        elif snapshot.is_running:
            self._status_text.value = "Running"
            self._status_text.color = ACCENT_TEXT
        else:
            self._status_text.value = "Paused"
            self._status_text.color = MUTED

        self._refresh_notice(snapshot.failure_reason)
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

        # Every slider is driven from the snapshot, not left wherever the
        # user dragged it. A refused setting must not leave a control
        # reading one value while the simulation runs at another: the
        # control is a display of model state as much as an input to it.
        self._fresh_gas_flow_slider.value = snapshot.fresh_gas_flow_l_min
        self._alveolar_ventilation_slider.value = snapshot.alveolar_ventilation_l_min
        self._cardiac_output_slider.value = snapshot.cardiac_output_l_min

        # A failed run cannot be resumed — only reset — so Start must not
        # invite it. `is_running` alone would leave Start enabled here,
        # since a failed session is stopped.
        self._start_button.disabled = snapshot.is_running or has_failed
        self._pause_button.disabled = not snapshot.is_running

        if snapshot.agent_accounting_passes_validation:
            self._agent_accounting_status_text.value = "Valid"
            self._agent_accounting_status_text.color = ACCENT_TEXT
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

        chart_max_x = max(INITIAL_CHART_WINDOW_S, snapshot.elapsed_s + 10.0)
        chart_min_x = max(0.0, chart_max_x - MAX_CHART_WINDOW_S)
        self._concentration_chart.max_x = chart_max_x
        self._concentration_chart.min_x = chart_min_x

        self._refresh_chart_series(snapshot.concentration_history, chart_min_x)

    def _apply_agent_color_scheme(self, agent_id: str) -> None:
        """Apply the verified agent color to the header and selection control."""

        scheme = AGENT_COLOR_SCHEMES[agent_id]
        self._agent_header_badge.bgcolor = scheme.fill
        self._agent_header_badge.border = ft.Border.all(1, scheme.foreground)
        self._subtitle_text.color = scheme.foreground

        self._agent_dropdown.fill_color = scheme.fill
        self._agent_dropdown.bgcolor = scheme.fill
        self._agent_dropdown.color = scheme.foreground
        self._agent_dropdown.text_style = ft.TextStyle(
            color=scheme.foreground, weight=ft.FontWeight.BOLD
        )
        self._agent_dropdown.border_color = scheme.foreground
        self._agent_dropdown.focused_border_color = scheme.foreground

    def _refresh_chart_series(
        self, history: tuple[SimulationHistorySample, ...], window_start_s: float
    ) -> None:
        """Redraw every trace from the samples inside the visible window.

        Only samples the chart can actually show are sent, and that window is
        decimated to a fixed per-trace budget, so the render payload is
        bounded by the window and the budget rather than by how long the
        simulation has been running. The controller's own history is read but
        never modified.

        Args:
            history: Immutable simulation samples, oldest first, with elapsed
                time in seconds and compartment values as fractions.
            window_start_s: Earliest simulated time the chart displays, in
                seconds. Samples older than this are outside the plotted axis
                range and are not sent.
        """

        visible = history[first_index_at_or_after(history, window_start_s, _sample_elapsed_s) :]

        for series, value_for in (
            (self._circuit_series, _circuit_value),
            (self._alveolar_series, _alveolar_value),
            (self._mixed_venous_series, _mixed_venous_value),
            (self._vessel_rich_series, _vessel_rich_value),
            (self._muscle_series, _muscle_value),
            (self._fat_series, _fat_value),
        ):
            series.points = self._decimated_points(visible, value_for)

    @staticmethod
    def _decimated_points(
        visible: tuple[SimulationHistorySample, ...],
        value_for: Callable[[SimulationHistorySample], float],
    ) -> list[fch.LineChartDataPoint]:
        """Convert one trace's visible samples to bounded chart percentages.

        Args:
            visible: Simulation samples inside the plotted time range.
            value_for: Function selecting one fraction from a sample.

        Returns:
            At most `MAX_CHART_POINTS_PER_SERIES` chart points with time in
            seconds and the selected value converted from a fraction to
            percent. Every point is a recorded sample: values are converted
            but never interpolated or synthesized.
        """

        values = [value_for(sample) for sample in visible]

        return [
            fch.LineChartDataPoint(visible[index].elapsed_s, values[index] * 100.0)
            for index in select_envelope_indices(values, MAX_CHART_POINTS_PER_SERIES)
        ]

    def _refresh_and_render(self) -> None:
        """Refresh the dashboard and submit it to the Flet page."""

        self._refresh_view()
        self._page.update()

    def _apply_setting(self, apply_setting: Callable[[], None]) -> None:
        """Apply one user setting, reporting a refusal instead of losing it.

        A `SimulationConfigurationError` here means the core rejected the
        value and changed nothing, so the run is untouched and must not be
        marked failed. What must not happen is the raise escaping into
        Flet's event dispatch: the control would keep the refused value
        while the simulation kept running at the old one, which is the
        correct number under the wrong label that `CLAUDE.md` treats as a
        safety failure. `_refresh_view` restores the control from the
        snapshot on the way out.
        """

        try:
            apply_setting()
        except AnesthesiaSimulationError as error:
            self._rejected_setting_notice = f"Setting refused — {error}"
        else:
            self._rejected_setting_notice = None

        self._refresh_and_render()

    def _refresh_notice(self, failure_reason: str | None) -> None:
        """Show the halted-run banner, or a refused setting, or nothing.

        A halted run outranks a refused setting: it describes the state of
        everything else on screen, where a refusal describes only one
        control.

        The halted-run wording says what the values *are* rather than
        warning about them, which is what rolling the failed step back
        bought. The core leaves the last completed step, so the numbers are
        a real solution of the model at a real simulation time; what the
        reader needs to know is that they have stopped advancing and that
        the run cannot be resumed, not that they are untrustworthy.
        """

        if failure_reason is not None:
            self._notice_text.value = (
                f"Simulation stopped — {failure_reason}. "
                "The values shown are the last completed step; the step that "
                "failed was rolled back and changed nothing. "
                "Reset to start a new run."
            )
            self._notice_text.visible = True
            return

        if self._rejected_setting_notice is not None:
            self._notice_text.value = (
                f"{self._rejected_setting_notice}. "
                "The simulation is unchanged and still running its previous setting."
            )
            self._notice_text.visible = True
            return

        self._notice_text.value = ""
        self._notice_text.visible = False

    def _handle_start(self, event: ft.Event[ft.Button]) -> None:
        del event
        self._apply_setting(self._controller.start)

    def _handle_pause(self, event: ft.Event[ft.Button]) -> None:
        del event
        self._controller.pause()
        self._refresh_and_render()

    def _handle_reset(self, event: ft.Event[ft.OutlinedButton]) -> None:
        del event
        self._controller.reset()
        self._rejected_setting_notice = None
        self._refresh_and_render()

    def _handle_agent_change(self, event: ft.Event[ft.Dropdown]) -> None:
        if event.control.value is None:
            return

        agent_id = event.control.value
        self._apply_setting(lambda: self._controller.set_agent(agent_id))

    def _handle_fresh_gas_flow_change(self, event: ft.Event[ft.Slider]) -> None:
        if event.control.value is None:
            return

        fresh_gas_flow_l_min = float(event.control.value)
        self._apply_setting(lambda: self._controller.set_fresh_gas_flow(fresh_gas_flow_l_min))

    def _handle_delivered_concentration_change(self, event: ft.Event[ft.Slider]) -> None:
        if event.control.value is None:
            return

        delivered_concentration_fraction = float(event.control.value) / 100.0
        self._apply_setting(
            lambda: self._controller.set_delivered_concentration(delivered_concentration_fraction)
        )

    def _handle_alveolar_ventilation_change(self, event: ft.Event[ft.Slider]) -> None:
        if event.control.value is None:
            return

        alveolar_ventilation_l_min = float(event.control.value)
        self._apply_setting(
            lambda: self._controller.set_alveolar_ventilation(alveolar_ventilation_l_min)
        )

    def _handle_cardiac_output_change(self, event: ft.Event[ft.Slider]) -> None:
        if event.control.value is None:
            return

        cardiac_output_l_min = float(event.control.value)
        self._apply_setting(lambda: self._controller.set_cardiac_output(cardiac_output_l_min))

    def _halt_run(self, error: Exception) -> None:
        """Stop the run and put the failure on screen.

        The exception type is recorded alongside its message rather than
        being used to decide whether to stop: a `TypeError` from a future
        refactor kills the loop exactly as silently as a modelling failure
        does, and both leave a display that would otherwise keep reading
        "Running" over numbers that stopped advancing.
        """

        self._controller.fail(f"{type(error).__name__}: {error}")

        try:
            self._refresh_and_render()
        except Exception:  # broad by design - see the comment below
            # The interface could not be updated to show the failure. The
            # run is stopped regardless, which is the part that matters: a
            # frozen display over a stopped simulation is at worst
            # uninformative, while one over a running simulation is
            # actively misleading.
            pass

    async def _run_simulation_timer(self) -> None:
        """Advance the running simulation one fixed step per tick.

        Stepping is deliberately separate from drawing. Simulation time stays
        a function of how many steps have been taken, never of wall-clock
        time or of how long a redraw took, so a slow or skipped frame cannot
        change the trajectory: identical inputs still produce identical
        results.

        The loop survives a failed step rather than returning: the task is
        started once, at mount, so a loop that exits could never be
        restarted and Reset would leave the interface permanently dead.
        Halting clears `is_running`, so the loop idles until the user
        starts a fresh run.
        """

        while True:
            await asyncio.sleep(SIMULATION_STEP_S)

            if not self._controller.is_running:
                continue

            try:
                self._controller.advance(SIMULATION_STEP_S)
            except Exception as error:  # broad by design - see _halt_run
                self._halt_run(error)

    async def _run_render_timer(self) -> None:
        """Redraw the running simulation on its own, slower cadence.

        Drawing no longer gates stepping, and the interval can be tuned for
        the display without changing the simulation. Explicit user actions
        redraw immediately rather than waiting for this tick, so a control
        never appears unresponsive and the view is never left showing state
        the user has already changed.

        Guarded for the mirror-image reason the simulation loop is: a dead
        render loop leaves a frozen display over a simulation that is still
        advancing, so the values on screen silently stop being current.
        """

        while True:
            await asyncio.sleep(RENDER_INTERVAL_S)

            if not self._controller.is_running:
                continue

            try:
                self._refresh_and_render()
            except Exception as error:  # broad by design - see _halt_run
                self._halt_run(error)

    @staticmethod
    def _build_metric_value(initial_value: str) -> ft.Text:
        """Build a formatted dashboard metric.

        Args:
            initial_value: Initial formatted value including its
                physical unit.

        Returns:
            Styled Flet text control.
        """

        return ft.Text(initial_value, size=22, weight=ft.FontWeight.BOLD, color=INK)

    @staticmethod
    def _format_percent(concentration_fraction: float) -> str:
        """Convert a concentration fraction to display percent.

        Renders at `CONCENTRATION_DISPLAY_RESOLUTION_PERCENT`, the
        resolution `docs/MODEL.md` § "Displayed precision" justifies against
        the measured error of the shipped operator split.

        A value that is positive but rounds to zero is rendered as below the
        resolution rather than as zero. The distinction is the point: muscle
        and fat sit under 0.01% for the first minutes of a run — fat for
        thirteen of them at 1 MAC sevoflurane — and `0.00%` there would
        assert a compartment is empty when the model says it is filling.
        `<0.01%` says only what is known, and leaves `0.00%` meaning what it
        should, that nothing has arrived yet.

        A negative fraction is deliberately not given the below-resolution
        form. The compartment guards make one impossible, so if one ever
        reaches here it must stay visible as the anomaly it is rather than
        be absorbed into a plausible-looking reading.

        Args:
            concentration_fraction: Dimensionless concentration
                fraction from zero through one.

        Returns:
            Concentration as percent at the displayed resolution, or the
            below-resolution form for a positive value that rounds to zero.
        """

        percent = concentration_fraction * 100.0
        rendered = f"{percent:.{CONCENTRATION_DISPLAY_DECIMALS}f}"

        if percent > 0.0 and float(rendered) == 0.0:
            resolution = CONCENTRATION_DISPLAY_RESOLUTION_PERCENT

            return f"<{resolution:.{CONCENTRATION_DISPLAY_DECIMALS}f}%"

        return f"{rendered}%"

    @staticmethod
    def _format_subtitle(agent_display_name: str) -> str:
        """Build the header subtitle naming the current app version and agent."""

        return f"Version {APP_VERSION} — {agent_display_name} patient model"

    @staticmethod
    def _format_delivered_label(agent_display_name: str) -> str:
        """Build the delivered-concentration panel label naming the agent."""

        return f"Delivered {agent_display_name.lower()}"
