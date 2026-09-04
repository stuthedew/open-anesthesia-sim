"""Present the interactive volatile-agent simulation as a responsive dashboard.

This module is the visual boundary between the scientific simulation and the
user. It builds the controls, renders immutable controller snapshots, and
forwards user settings to the controller without implementing physiological
calculations or modifying model state directly.

Two concerns it used to hold are their own modules, because each is a
presentation-*correctness* question rather than a layout one and each needs
to be readable and testable without loading a Flet interface:
`formatting.py` turns a modeled fraction into the string a reader sees, at
the resolution `docs/MODEL.md` derives, and `chart_series.py` shapes the
chart's traces from the recorded run. What is left here is the interface
itself.

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
from dataclasses import dataclass
from typing import Final

import flet as ft
import flet_charts as fch

from anesthesia_sim.app import chart_series
from anesthesia_sim.app.control_timeline import (
    ControlAdjustment,
    format_adjustment,
    group_adjustments,
)
from anesthesia_sim.app.controller import (
    HistoryWindow,
    RecordedQuantity,
    SimulationController,
    SimulationSnapshot,
)
from anesthesia_sim.app.formatting import (
    CONCENTRATION_DISPLAY_DECIMALS,
    FLOW_DISPLAY_DECIMALS,
    format_delivered_label,
    format_elapsed,
    format_flow,
    format_mac_awake_reference,
    format_mac_multiple,
    format_mac_reference,
    format_percent,
    format_subtitle,
    format_wash_in_ratio,
    mac_awake_band_percent,
    mac_axis_ticks,
)
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
from anesthesia_sim.app.wash_in import WASH_IN_EQUILIBRIUM_RATIO, WashInDomain, read_wash_in
from anesthesia_sim.app_metadata import APP_DISPLAY_NAME
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
# applicability domain is `core.uptake_system.MAXIMUM_SIMULATION_STEP_S`,
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
CHART_HEIGHT = 360

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
# The MAC line under each reading, in the same relationship to the percent
# above it as the gloss is to the compartment name: smaller and MUTED, because
# it is the weaker of the two claims. Percent is what the model computes and
# what a monitor would show; a MAC multiple is that number divided by a
# population constant this model does not otherwise use, and on the four
# non-alveolar compartments it is a partial-pressure ratio rather than
# anything a clinician reads off a patient. Sized between the name and the
# gloss so the row reads value, then unit-conversion, then annotation.
METRIC_SECONDARY_VALUE_SIZE = 13
# A panel with no gloss still draws the line, so that every reading in the row
# sits on one baseline. A blank string collapses to zero height in Flutter,
# where a non-breaking space renders a full line of the qualifier's size -
# which keeps the spacer tied to that size rather than to a pixel constant
# somebody would have to re-measure after a font change.
EMPTY_METRIC_QUALIFIER = "\u00a0"
# The same spacer for the MAC line, so the "Simulated time" panel - which has
# no concentration and therefore no MAC multiple - is the height of the six
# that do, and every reading in the row keeps the shared baseline
# `_build_concentration_metrics` exists to preserve.
EMPTY_METRIC_SECONDARY_VALUE = "\u00a0"

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

# The colour swatch every legend entry draws, at one size across all three
# legend rows so that a reader scanning down them compares marks rather than
# shapes. `_build_band_legend_item` is the one deliberate exception: a band's
# extent is exactly what distinguishes it from a line.
LEGEND_SWATCH_WIDTH = 24
LEGEND_SWATCH_HEIGHT = 4
# What the chart says when a reader has unchecked every compartment. The
# checkboxes state which traces are drawn, so a plot missing one or two is
# already explained where the reader is looking; a plot missing all six is a
# blank panel, and a blank panel reads as a display that has failed rather
# than as one showing what it was asked for. `NO_CONTROL_CHANGES_TEXT` is the
# same call made for the empty control-input list.
NO_TRACES_SHOWN_TEXT = (
    "No compartment traces are shown. Check a compartment above to draw it — "
    "the readouts and the run itself are unaffected."
)

# The two chart references are furniture rather than data, and are drawn in
# the interface's own ink and label colour rather than in a seventh and
# eighth hue. A new hue would enter the trace palette's separation problem
# (`.claude/rules/ui-color.md`, judgment 3: six traces already cannot all
# clear 3:1 against each other on a bounded axis) while implying the mark is
# another compartment. What separates a reference from a trace here is
# instead its *kind* — constant, horizontal, spanning the window — and its
# mark type, which is also what separates the two references from each
# other: a band for a measured population value with real spread, a line for
# a definitional anchor. That distinction survives greyscale and every
# colour-vision deficiency, which `.claude/rules/ui-color.md`'s judgment 2
# requires of any encoding that carries meaning.
#
# The ranking between them is deliberate and is INK against MUTED. After a
# long case at a steady setpoint the alveolar and vessel-rich traces have
# converged, so the 1 MAC anchor is robust to which trace it is read
# against; at MAC-awake they have not, so the band is the trace-critical
# mark and carries the heavier weight. Giving the easier mark equal weight
# is the failure PL-F52R names.
MAC_AWAKE_BAND_COLOR = INK
ONE_MAC_LINE_COLOR = MUTED
# The band's fill is decoration: its boundaries are carried by a stroke on
# the upper edge and by the fill's own cut-off on the lower, both in
# `MAC_AWAKE_BAND_COLOR`, which is what `tools/contrast_check.py` measures.
# The fill is light enough for six traces to remain legible across it, which
# a fill at its own 3:1 would not be.
MAC_AWAKE_BAND_FILL_OPACITY = 0.14
# Wider than any trace's dashes ([10, 4], [4, 3], [2, 3], [12, 4, 2, 4]), so
# the 1 MAC line does not read as a seventh compartment at a glance.
ONE_MAC_LINE_DASH_PATTERN = [16, 8]

# A control-change mark is furniture like the two references, and takes the
# same MUTED ink for the same reason: it is not a compartment, and a hue of
# its own would enter the trace palette's separation problem while implying
# it were. It needs no second colour channel because it already has a
# stronger one - it is the only vertical thing on the chart, which no
# colour-vision deficiency and no greyscale rendering can take away.
# Reusing MUTED also declares no new pair for `tools/contrast_check.py`:
# MUTED on PANEL is already measured, as the 1 MAC line.
CONTROL_MARK_COLOR = MUTED
# Finer than either reference and than every trace, because a control mark
# annotates the run rather than showing any part of it: at the density of a
# case with a dozen adjustments, a mark as heavy as a trace would compete
# with the curves it exists to be read against. Heavier than the vertical
# grid lines, though, and dashed where they are solid: measured against a
# rendered frame, a mark at a hair's width beside a 60 s gridline is
# findable but not immediately separable from it, and a reader who cannot
# tell an annotation from an axis decoration reads the time off the wrong
# one.
CONTROL_MARK_STROKE_WIDTH = 1.5
CONTROL_MARK_DASH_PATTERN = [3, 5]
# How many control marks the chart can stand at once. The pool is built at
# construction and its members are moved from frame to frame, exactly as the
# traces are (PL-010), so this is a ceiling on control count rather than on
# how many adjustments a run may record - the list beside the chart shows
# them whether or not there is a mark left to draw one, and says so when
# there is not.
MAX_CHART_CONTROL_MARKS = 24
# What the list says before anything has been changed. It states the run's
# state rather than leaving an empty panel, which reads as a panel that has
# failed to load.
NO_CONTROL_CHANGES_TEXT = "No settings changed yet in this run."
# How many adjustments the list shows. A fixed panel beside a chart, not a
# scrollback: the count of what is not shown is displayed rather than the
# entries silently ending.
MAX_LISTED_ADJUSTMENTS = 12

# The wash-in trace takes the alveolar compartment's own colour, because it
# is that compartment expressed against the one filling it: the numerator is
# the alveolar fraction and nothing else on the second chart competes with
# it. Reusing it declares no new pair for `tools/contrast_check.py` - ACCENT
# on PANEL is already measured - and it is what lets a reader carry the
# alveolar curve from the chart above into the ratio below.
WASH_IN_COLOR = ALVEOLAR_COLOR
# Shorter than the compartment chart. The ratio is one trace on a fixed
# 0-to-1 axis, so it needs no room to separate six curves, and the two plots
# have to be readable together without scrolling between them.
WASH_IN_CHART_HEIGHT = 200
# Gridlines at quarter-fractions, which is the ruling every published wash-in
# figure carries and the spacing a reader compares against. The axis is
# labelled at exactly these values rather than at whatever interval the chart
# would choose for itself: a rule at 0.25 beside a label at 0.2 puts two
# different scales on one axis, and a reader taking a value off the nearest
# gridline would take it off the wrong one.
WASH_IN_GRID_INTERVAL = 0.25
# The axis stands above equilibrium rather than at it, which is a legibility
# requirement rather than a spare margin. The trace ends where it crosses
# `WASH_IN_EQUILIBRIUM_RATIO`, and with the axis topping out there that
# ending lands on the frame - where a line that stopped and a line the plot
# cut off look exactly alike. Lifting the axis puts clear space above the
# ending, so the stop is visibly the trace's own. 1.15 leaves that space
# without adding a fifth labelled interval: the ruling and the labels stop at
# 1.00, which is where the readable scale ends, and `show_max` keeps the
# chart from labelling the top of the frame.
WASH_IN_AXIS_MAXIMUM = 1.15
# How far past equilibrium the trace may be drawn so that its ending lands on
# the line rather than a step short of it. `chart_series.redraw_wash_in_segments`
# carries the whole reasoning, including why the bound is stated rather than
# taken from the measured 1.00235 a 0.1 s step actually produces. Set below
# `WASH_IN_AXIS_MAXIMUM` rather than at it, so even the widest crossing this
# admits still has clear space above it.
WASH_IN_TERMINUS_CEILING = 1.05
# The wash-in curve's asymptote, drawn as the reference it is. A trace that
# simply halts in open space reads as clipped; one that halts *on a labelled
# line* reads as having arrived somewhere. It is a definitional anchor rather
# than a measured value with spread - F_A = F_I is where net uptake stops, by
# definition - so it is a line and not a band, on the distinction
# `docs/MODEL.md` § "MAC-awake as a chart reference" draws between the two.
# MUTED and a wide dash, matching the 1 MAC line on the chart above: this is
# furniture rather than a second compartment, and it declares no new pair for
# `tools/contrast_check.py`.
EQUILIBRIUM_LINE_COLOR = MUTED
EQUILIBRIUM_LINE_DASH_PATTERN = [16, 8]
# Room for one axis label at `format_wash_in_ratio`'s two decimals. The chart's
# own default is sized for the single digits the percent axis carries, and
# wraps "0.25" onto two lines.
WASH_IN_AXIS_LABEL_SIZE = 34
# How many separated stretches of wash-in the chart can draw at once. The
# trace breaks wherever the ratio leaves the domain `app/wash_in.py` states -
# a vaporizer turned off and later reopened is two stretches, not one line
# drawn through the washout between them - and the pool is fixed at
# construction for the reason the control-mark pool is. Eight is more
# stretches than a taught case produces inside one chart window; what does
# not fit is counted and said, never dropped in silence.
MAX_CHART_WASH_IN_SEGMENTS = 8

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


def _build_wash_in_axis_labels() -> list[fch.ChartAxisLabel]:
    """Label the wash-in axis at its own gridlines, in its own resolution.

    Built once at import time rather than per frame: unlike the MAC axis,
    nothing about this axis depends on the agent or on the run - it is a
    dimensionless 0 to 1 under every setting, which is the property that
    makes the plot comparable across agents in the first place.

    The labels go through `format_wash_in_ratio`, so the axis a value is
    read against and the reading printed beside the plot cannot be at two
    different resolutions.

    Returns:
        One label per gridline, from 0 to the plotted maximum.
    """

    tick_count = round(WASH_IN_EQUILIBRIUM_RATIO / WASH_IN_GRID_INTERVAL)

    return [
        fch.ChartAxisLabel(
            value=index * WASH_IN_GRID_INTERVAL,
            label=ft.Text(
                format_wash_in_ratio(index * WASH_IN_GRID_INTERVAL),
                color=MUTED,
                size=METRIC_QUALIFIER_SIZE,
            ),
        )
        for index in range(tick_count + 1)
    ]


@dataclass(frozen=True)
class _AgentRenderStyle:
    """The Flet objects one agent's identification color renders as.

    `theme.py` holds the colors; this holds what Flet needs built out of
    them. They are separate because the colors are the provenanced value -
    an ISO 5360 sample, checked for contrast by `tools/contrast_check.py`,
    which parses `theme.py` without importing Flet - while these are render
    objects derived from it.

    Attributes:
        badge_border: Outline for the header badge, in the agent's own text
            color. `theme.py` records why the badge needs one at all.
        dropdown_text_style: Style for the selected agent's name in the
            dropdown.
    """

    badge_border: ft.Border
    dropdown_text_style: ft.TextStyle


# Built once per agent at import time rather than per frame. `ft.Border` and
# `ft.TextStyle` are Flet *value* types - no control identity, compared by
# value - so one instance can be assigned repeatedly and to more than one
# control without aliasing anything. `_apply_agent_color_scheme` still assigns
# them on every tick: which agent is displayed stays read from the snapshot,
# and Flet's own equality check makes the unchanged case free. Nothing may
# mutate these; assign a different one instead.
AGENT_RENDER_STYLES: Final[dict[str, _AgentRenderStyle]] = {
    agent_id: _AgentRenderStyle(
        badge_border=ft.Border.all(1, scheme.foreground),
        dropdown_text_style=ft.TextStyle(color=scheme.foreground, weight=ft.FontWeight.BOLD),
    )
    for agent_id, scheme in AGENT_COLOR_SCHEMES.items()
}


@dataclass
class _CompartmentTrace:
    """One compartment trace: what it draws, how it is drawn, and whether it is.

    Everything that has to agree about a single compartment, held together in
    one object. Before this the same trace was described in three places -
    the colour and dash pattern where the series was built, the compartment it
    draws in the `PlottedSeries` table, and the name and line-style words in a
    hand-written legend row six hundred lines away - and keeping the three in
    agreement was left to whoever remembered. A legend that names a line the
    chart is not drawing misstates the run as surely as a wrong number does,
    which is why this is one record rather than three lists.

    **The pairing travels as one object, which is what makes filtering safe.**
    `plotted` manufactures the `(series, quantity)` pair from this record's own
    fields, so a filter over these records - which is how a hidden trace is
    left out of a frame - cannot reorder or misalign the pairing the way a
    filter over two parallel sequences could. That is the specific hazard
    `test_chart_traces_stay_bound_to_their_own_compartment` guards, and it now
    covers the filtered table too.

    Attributes:
        quantity: The one recorded quantity this trace draws.
        label: The compartment's name, as the legend and its control say it.
        color: The trace's line colour, and its legend swatch's fill.
        line_style: The dash pattern in words, for the legend. Kept beside
            the pattern it describes rather than in the legend's own code,
            so "dotted" cannot come to describe a line that is not.
        series: The chart series this trace is drawn as.
        swatch: The legend's colour mark for it. Filled while the trace is
            drawn and empty while it is not.
        checkbox: The control that shows and hides it, whose label is this
            trace's legend text.
        visible: Whether the chart is currently drawing it. Presentation
            state only: it is never read by the simulation and changes
            nothing the model computes.
    """

    quantity: RecordedQuantity
    label: str
    color: str
    line_style: str
    series: fch.LineChartData
    swatch: ft.Container
    checkbox: ft.Checkbox
    visible: bool = True

    @property
    def plotted(self) -> chart_series.PlottedSeries:
        """This trace paired with the one quantity it draws."""

        return (self.series, self.quantity)


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
        # Adjustments inside the visible window that the fixed pool of chart
        # marks could not draw. Held so the panel can say so: a chart that
        # silently stops annotating asserts that nothing more happened.
        self._undrawn_control_marks = 0
        self._undrawn_wash_in_segments = 0
        self._notice_text = ft.Text("", color=WARNING, weight=ft.FontWeight.BOLD, visible=False)
        self._elapsed_time_text = self._build_metric_value("0.0 s")
        # Placeholders come from the formatter rather than from literals, so
        # a change to the displayed resolution cannot leave the pre-run
        # reading disagreeing with every reading after it.
        empty_compartment = format_percent(0.0)
        self._circuit_concentration_text = self._build_metric_value(empty_compartment)
        self._alveolar_concentration_text = self._build_metric_value(empty_compartment)
        self._mixed_venous_concentration_text = self._build_metric_value(empty_compartment)
        self._vessel_rich_concentration_text = self._build_metric_value(empty_compartment)
        self._muscle_concentration_text = self._build_metric_value(empty_compartment)
        self._fat_concentration_text = self._build_metric_value(empty_compartment)

        # The second display unit, one line under each percent. Both are shown
        # at once rather than behind a unit selector: a selector would make the
        # unit a mode, and a reader who missed the switch would read a
        # desflurane compartment at 6.0 as six times what it is. Two lines
        # cannot be misread that way, and the pair is also what makes the
        # conversion legible - the agent's own 1 MAC is the ratio between them,
        # and it is named under the chart.
        empty_mac = format_mac_multiple(0.0, initial_snapshot.agent_mac_percent)
        self._circuit_mac_text = self._build_metric_secondary_value(empty_mac)
        self._alveolar_mac_text = self._build_metric_secondary_value(empty_mac)
        self._mixed_venous_mac_text = self._build_metric_secondary_value(empty_mac)
        self._vessel_rich_mac_text = self._build_metric_secondary_value(empty_mac)
        self._muscle_mac_text = self._build_metric_secondary_value(empty_mac)
        self._fat_mac_text = self._build_metric_secondary_value(empty_mac)

        self._agent_accounting_status_text = ft.Text(
            "Valid", color=ACCENT_TEXT, size=20, weight=ft.FontWeight.BOLD
        )
        self._agent_accounting_detail_text = ft.Text("No unaccounted agent detected.", color=MUTED)
        self._agent_amounts_text = ft.Text(
            ("Delivered: 0.000000 L | Exhausted: 0.000000 L | Stored: 0.000000 L"), color=MUTED
        )

        self._fresh_gas_flow_text = ft.Text(
            format_flow(initial_snapshot.fresh_gas_flow_l_min), color=INK
        )
        self._delivered_concentration_text = ft.Text(
            format_percent(initial_snapshot.delivered_concentration_fraction), color=INK
        )
        # The dial in the same two units as the compartments it fills. Without
        # it the one control a reader sets would be the only value on screen
        # they could not compare with the traces it produces.
        self._delivered_concentration_mac_text = ft.Text(
            format_mac_multiple(
                initial_snapshot.delivered_concentration_fraction,
                initial_snapshot.agent_mac_percent,
            ),
            color=MUTED,
            size=METRIC_SECONDARY_VALUE_SIZE,
        )
        self._alveolar_ventilation_text = ft.Text(
            format_flow(initial_snapshot.alveolar_ventilation_l_min), color=INK
        )
        self._cardiac_output_text = ft.Text(
            format_flow(initial_snapshot.cardiac_output_l_min), color=INK
        )

        # Every compartment trace, in the order they are drawn and listed.
        # One table rather than three: `_CompartmentTrace` records why the
        # series, the compartment it draws, and the legend entry that names
        # it are declared together and never separately.
        self._compartment_traces: tuple[_CompartmentTrace, ...] = (
            self._build_compartment_trace(
                RecordedQuantity.CIRCUIT, "Circuit", CIRCUIT_COLOR, 3, "solid"
            ),
            self._build_compartment_trace(
                RecordedQuantity.ALVEOLAR, "Alveolar", ALVEOLAR_COLOR, 3, "long dash", [10, 4]
            ),
            self._build_compartment_trace(
                RecordedQuantity.MIXED_VENOUS,
                "Mixed venous",
                MIXED_VENOUS_COLOR,
                2,
                "short dash",
                [4, 3],
            ),
            self._build_compartment_trace(
                RecordedQuantity.VESSEL_RICH, "Vessel-rich", VESSEL_RICH_COLOR, 2, "solid"
            ),
            self._build_compartment_trace(
                RecordedQuantity.MUSCLE, "Muscle", MUSCLE_COLOR, 2, "dotted", [2, 3]
            ),
            self._build_compartment_trace(
                RecordedQuantity.FAT, "Fat", FAT_COLOR, 2, "dash-dot", [12, 4, 2, 4]
            ),
        )
        # One stable handle per trace, as the two references below have.
        # Looked up by the quantity each draws rather than by position, so
        # reordering the table cannot silently rebind a name onto another
        # compartment's line - which is the same pairing failure the table
        # itself exists to make impossible.
        self._circuit_series = self._trace(RecordedQuantity.CIRCUIT).series
        self._alveolar_series = self._trace(RecordedQuantity.ALVEOLAR).series
        self._mixed_venous_series = self._trace(RecordedQuantity.MIXED_VENOUS).series
        self._vessel_rich_series = self._trace(RecordedQuantity.VESSEL_RICH).series
        self._muscle_series = self._trace(RecordedQuantity.MUSCLE).series
        self._fat_series = self._trace(RecordedQuantity.FAT).series
        # Said only when every compartment has been unchecked. Held rather
        # than built inline because its visibility is written by
        # `_apply_trace_visibility`, which is the one writer of everything
        # that has to agree with what the chart is drawing.
        self._hidden_traces_text = ft.Text(
            NO_TRACES_SHOWN_TEXT,
            color=MUTED,
            size=METRIC_QUALIFIER_SIZE,
            italic=True,
            visible=False,
        )
        # The two clinical references. Deliberately not members of
        # `_plotted_series` below: nothing reads a sample to place them, and
        # the table they would join exists to bind a trace to the one
        # compartment it draws.
        self._mac_awake_band_series = chart_series.build_reference_line(
            color=MAC_AWAKE_BAND_COLOR, stroke_width=1.5
        )
        self._mac_awake_band_series.below_line_bgcolor = ft.Colors.with_opacity(
            MAC_AWAKE_BAND_FILL_OPACITY, MAC_AWAKE_BAND_COLOR
        )
        self._one_mac_line_series = chart_series.build_reference_line(
            color=ONE_MAC_LINE_COLOR, stroke_width=1.5, dash_pattern=ONE_MAC_LINE_DASH_PATTERN
        )
        # Two rulers against one set of traces. The plotted points stay in
        # percent - `chart_series.redraw_series` converts nothing else - and
        # the MAC axis is a relabelling of the same coordinate, so the two
        # axes cannot come to disagree about where a trace is. That is the
        # reason for a second axis rather than a unit toggle: a toggle would
        # make the axis unit a hidden mode, and a chart read under the wrong
        # assumed unit is a misreading no disclaimer catches.
        # What the MAC axis labels currently stand for, so a frame that
        # changes neither leaves them alone. They depend on the agent and the
        # plotted range and on nothing that moves during a run, where the
        # render loop runs several times a second: rebuilding them per frame
        # would allocate a label control per tick per frame and send the
        # client an add-and-remove of the whole axis each time - the same
        # per-frame churn PL-010 removed from the traces, arriving by
        # another door. `tests/integration/test_chart_patching.py` is what
        # measures that, and it fails if this guard is dropped.
        self._mac_axis_basis = (
            initial_snapshot.max_delivered_concentration_percent,
            initial_snapshot.agent_mac_percent,
        )
        self._mac_axis = fch.ChartAxis(
            title=ft.Text("multiples of 1 MAC", color=MUTED, size=METRIC_QUALIFIER_SIZE),
            labels=self._build_mac_axis_labels(*self._mac_axis_basis),
            # The MAC ticks are the whole point of the axis, so the ends of
            # the percent range must not add two more at whatever multiples
            # they happen to fall on: isoflurane's 5% dial maximum is
            # 4.17 MAC, and a label reading 4.17 beside labels reading 3.5
            # and 4.0 would be read as a tick rather than as an endpoint.
            show_min=False,
            show_max=False,
        )
        # One series per mark, built once. Marks come first in the drawing
        # order - behind the references and behind every trace - because a
        # vertical rule crossing the whole plot is the one annotation that
        # can obscure all six compartments at the moment a reader is trying
        # to see what the change did to them.
        self._control_mark_series = [
            chart_series.build_control_mark(
                CONTROL_MARK_COLOR, CONTROL_MARK_STROKE_WIDTH, CONTROL_MARK_DASH_PATTERN
            )
            for _ in range(MAX_CHART_CONTROL_MARKS)
        ]
        # A second pool of marks for the wash-in chart, rather than the same
        # objects drawn twice: a Flet control belongs to one chart, and the
        # dial change that invalidates a wash-in reading has to be visible on
        # the plot being misread, not only on the one above it.
        self._wash_in_control_mark_series = [
            chart_series.build_control_mark(
                CONTROL_MARK_COLOR, CONTROL_MARK_STROKE_WIDTH, CONTROL_MARK_DASH_PATTERN
            )
            for _ in range(MAX_CHART_CONTROL_MARKS)
        ]
        self._wash_in_segment_series = [
            chart_series.build_series(color=WASH_IN_COLOR, stroke_width=3)
            for _ in range(MAX_CHART_WASH_IN_SEGMENTS)
        ]
        self._equilibrium_line_series = chart_series.build_reference_line(
            color=EQUILIBRIUM_LINE_COLOR,
            stroke_width=1.5,
            dash_pattern=EQUILIBRIUM_LINE_DASH_PATTERN,
        )
        self._wash_in_state_text = ft.Text("", color=MUTED, size=METRIC_QUALIFIER_SIZE)
        self._control_timeline_text = ft.Text(
            NO_CONTROL_CHANGES_TEXT, color=MUTED, size=METRIC_QUALIFIER_SIZE
        )
        self._control_timeline_overflow_text = ft.Text(
            "", color=MUTED, size=METRIC_QUALIFIER_SIZE, italic=True, visible=False
        )
        self._concentration_chart = fch.LineChart(
            data_series=self._chart_data_series(),
            min_x=0,
            max_x=INITIAL_CHART_WINDOW_S,
            min_y=0,
            max_y=initial_snapshot.max_delivered_concentration_percent,
            left_axis=fch.ChartAxis(
                title=ft.Text("percent", color=MUTED, size=METRIC_QUALIFIER_SIZE)
            ),
            right_axis=self._mac_axis,
            horizontal_grid_lines=fch.ChartGridLines(interval=2, color="#D9E2EC"),
            vertical_grid_lines=fch.ChartGridLines(interval=60, color="#D9E2EC"),
            expand=True,
        )
        self._wash_in_chart = fch.LineChart(
            data_series=[
                *self._wash_in_control_mark_series,
                self._equilibrium_line_series,
                *self._wash_in_segment_series,
            ],
            min_x=0,
            max_x=INITIAL_CHART_WINDOW_S,
            min_y=0,
            # Fixed, and fixed just above the equilibrium value rather than
            # at whatever the run reaches. 0 to 1 is the scale every
            # published wash-in figure uses, which is the whole point of
            # drawing this curve at all; an axis that grew to fit an
            # excursion above 1 would redraw the wash-in curve at a smaller
            # height partway through a lesson, which is a shape change a
            # reader would read as the model's rather than the axis's.
            # `WASH_IN_AXIS_MAXIMUM` records why the top is not at 1 exactly,
            # and `app/wash_in.py` why nothing past the crossing sample is
            # drawn.
            max_y=WASH_IN_AXIS_MAXIMUM,
            left_axis=fch.ChartAxis(
                title=ft.Text("F_A / F_I", color=MUTED, size=METRIC_QUALIFIER_SIZE),
                labels=_build_wash_in_axis_labels(),
                # Both, and for different reasons: `labels` says what the
                # ticks read, `label_spacing` says which of them are drawn.
                # Left to choose for itself the chart samples the list at a
                # coarser interval than the gridlines, so the quarter marks
                # are ruled and unlabelled.
                label_spacing=WASH_IN_GRID_INTERVAL,
                label_size=WASH_IN_AXIS_LABEL_SIZE,
                # The scale ends at 1.00; the headroom above it is space, not
                # a tick. Labelling the top of the frame would put "1.15" on
                # an axis whose every other label is a quarter, and invite it
                # being read as the range the ratio can reach.
                show_max=False,
            ),
            horizontal_grid_lines=fch.ChartGridLines(
                interval=WASH_IN_GRID_INTERVAL, color="#D9E2EC"
            ),
            vertical_grid_lines=fch.ChartGridLines(interval=60, color="#D9E2EC"),
            expand=True,
        )
        # Names the divisor every MAC number on this page was produced with,
        # which is what makes those numbers traceable without opening a data
        # file (`CLAUDE.md`, safety-critical clinical-output standard). It
        # changes with the agent, so it is held rather than built inline.
        self._mac_reference_text = ft.Text(
            format_mac_reference(
                initial_snapshot.agent_display_name, initial_snapshot.agent_mac_percent
            ),
            color=MUTED,
        )
        # The same traceability the line above gives the MAC axis, for the
        # band: it has two free parameters rather than one - a published
        # fraction and the divisor it is applied to - and both are named, so
        # a reader who disagrees with either can see which.
        self._mac_awake_reference_text = ft.Text(
            self._format_mac_awake_reference(initial_snapshot), color=MUTED
        )

        self._start_button = ft.Button(content="Start", on_click=self._handle_start)
        self._pause_button = ft.Button(content="Pause", disabled=True, on_click=self._handle_pause)
        self._reset_button = ft.OutlinedButton(content="Reset", on_click=self._handle_reset)

        initial_agent_colors = AGENT_COLOR_SCHEMES[initial_snapshot.agent_id]
        initial_agent_style = AGENT_RENDER_STYLES[initial_snapshot.agent_id]
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
            text_style=initial_agent_style.dropdown_text_style,
            border_color=initial_agent_colors.foreground,
            focused_border_color=initial_agent_colors.foreground,
            on_select=self._handle_agent_change,
        )

        self._subtitle_text = ft.Text(
            format_subtitle(initial_snapshot.agent_display_name),
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
            border=initial_agent_style.badge_border,
            border_radius=COMPACT_PANEL_RADIUS,
            padding=6,
        )
        self._delivered_concentration_label = ft.Text(
            format_delivered_label(initial_snapshot.agent_display_name),
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
            on_change_start=self._handle_adjustment_start,
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
            on_change_start=self._handle_adjustment_start,
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
            on_change_start=self._handle_adjustment_start,
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
            on_change_start=self._handle_adjustment_start,
        )

        self._refresh_view()

    def _build_compartment_trace(
        self,
        quantity: RecordedQuantity,
        label: str,
        color: str,
        stroke_width: float,
        line_style: str,
        dash_pattern: list[int] | None = None,
    ) -> _CompartmentTrace:
        """Build one compartment's trace, its legend swatch, and its control.

        All three from one call, so the colour and the dash pattern a trace
        is drawn with and the ones its legend entry claims cannot be written
        twice and drift apart.

        The control is a checkbox carrying the legend's own text as its
        label, which is what makes it a labelled control to a screen reader
        and to a pointer rather than a bare box, and what stops the interface
        holding two lists of the same six compartments.

        Args:
            quantity: The recorded quantity this trace draws.
            label: The compartment's name, as the legend says it.
            color: Line colour, and the legend swatch's fill.
            stroke_width: Line width in display pixels.
            dash_pattern: Alternating dash and gap lengths in display
                pixels, or None for a solid line.
            line_style: The same pattern in words, for the legend.

        Returns:
            The trace, ready to be drawn and to be shown or hidden.
        """

        trace = _CompartmentTrace(
            quantity=quantity,
            label=label,
            color=color,
            line_style=line_style,
            series=chart_series.build_series(
                color=color, stroke_width=stroke_width, dash_pattern=dash_pattern
            ),
            swatch=ft.Container(
                width=LEGEND_SWATCH_WIDTH, height=LEGEND_SWATCH_HEIGHT, bgcolor=color
            ),
            checkbox=ft.Checkbox(
                value=True,
                label=f"{label} ({line_style})",
                label_style=ft.TextStyle(color=INK),
                # Deliberately not one of the six trace colours, and not the
                # slider accent either. This row has already spent its whole
                # colour budget on six compartments - `.claude/rules/ui-color.md`
                # judgment 3 - so a coloured box beside a coloured swatch
                # would compete for the one channel that carries compartment
                # identity. INK is the interface's own ink, reads as furniture,
                # and is the pair `tools/contrast_check.py` already measures
                # against PANEL at the text minimum, comfortably above SC
                # 1.4.11's 3:1 for a control.
                active_color=INK,
                check_color=PANEL,
                semantics_label=f"Draw the {label} compartment on the chart",
            ),
        )
        trace.checkbox.on_change = lambda event: self._handle_trace_visibility_change(trace, event)

        return trace

    def _trace(self, quantity: RecordedQuantity) -> _CompartmentTrace:
        """The one trace that draws this quantity.

        Args:
            quantity: The recorded quantity to find the trace for.

        Returns:
            Its trace.

        Raises:
            KeyError: If no trace draws it, which would mean the table has
                lost a compartment rather than that a caller asked wrongly.
        """

        for trace in self._compartment_traces:
            if trace.quantity is quantity:
                return trace

        raise KeyError(f"no compartment trace draws {quantity}")

    @property
    def _plotted_series(self) -> tuple[chart_series.PlottedSeries, ...]:
        """Every trace paired with the compartment it draws, hidden ones included.

        The whole trace-to-quantity pairing: an entry naming the wrong
        quantity would plot one compartment's values on another
        compartment's line, which misstates the run as surely as a wrong
        number would. Nothing in the type system can catch that -
        `flet_charts` ships no stubs, so a chart series is `Any` to the
        checker - so `test_chart_traces_stay_bound_to_their_own_compartment`
        is what holds it, by giving each compartment a distinct multiple and
        reading the drawn points back.

        Hidden traces are included because what a trace *draws* does not
        change with whether it is currently on the chart. `_visible_plotted_series`
        is the frame's subset.
        """

        return tuple(trace.plotted for trace in self._compartment_traces)

    @property
    def _visible_plotted_series(self) -> tuple[chart_series.PlottedSeries, ...]:
        """The pairing above, filtered to the traces the reader is looking at.

        The filter is over whole records, each carrying its own series and
        its own quantity, so it cannot misalign the pairing - see
        `_CompartmentTrace`.
        """

        return tuple(trace.plotted for trace in self._compartment_traces if trace.visible)

    def _chart_data_series(self) -> list[fch.LineChartData]:
        """Every series the compartment chart holds, in drawing order.

        Marks first - behind the references and behind every trace - because
        a vertical rule crossing the whole plot is the one annotation that
        can obscure all six compartments at the moment a reader is trying to
        see what the change did to them. References next, so every trace is
        drawn over them: a compartment obscured by a reference band would be
        the annotation hiding the run it annotates.

        A hidden trace is **absent** from this list rather than present and
        empty. That is what stops the client holding its points at all,
        which is the whole render-cost half of this control; leaving it in
        place with an empty point list would keep the series, keep diffing
        it, and leave a trace that is no longer redrawn one bug away from
        showing the frame it was last drawn in.

        Returns:
            The chart's series list.
        """

        return [
            *self._control_mark_series,
            self._mac_awake_band_series,
            self._one_mac_line_series,
            *(trace.series for trace in self._compartment_traces if trace.visible),
        ]

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
                            controls=[self._build_chart_panel(), self._build_chart_sidebar()],
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
                    self._delivered_concentration_mac_text,
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
        self,
        label: str | ft.Text,
        slider: ft.Slider,
        value_text: ft.Text,
        secondary_value_text: ft.Text | None = None,
    ) -> ft.Container:
        """Build one compact simulation-setting panel.

        Args:
            label: User-facing setting name, or a pre-built Text control
                for a label that changes later (e.g. names the agent).
            slider: Slider controlling the setting.
            value_text: Current value with its physical unit.
            secondary_value_text: The same setting in a second display
                unit, drawn under the slider, or None where the setting
                has only one. Only the delivered agent has two: the three
                flow settings are in L/min, which MAC does not convert.

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
                controls=[
                    label_control,
                    ft.Row(controls=[slider, value_text]),
                    *([] if secondary_value_text is None else [secondary_value_text]),
                ],
                spacing=4,
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
                self._build_metric_panel("Simulated time", None, self._elapsed_time_text, None),
                self._build_metric_panel(
                    "Circuit", "inspired", self._circuit_concentration_text, self._circuit_mac_text
                ),
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
                    "Alveolar",
                    "end-tidal-equivalent",
                    self._alveolar_concentration_text,
                    self._alveolar_mac_text,
                ),
                self._build_metric_panel(
                    "Mixed venous",
                    None,
                    self._mixed_venous_concentration_text,
                    self._mixed_venous_mac_text,
                ),
                self._build_metric_panel(
                    "Vessel-rich group",
                    None,
                    self._vessel_rich_concentration_text,
                    self._vessel_rich_mac_text,
                ),
                self._build_metric_panel(
                    "Muscle", None, self._muscle_concentration_text, self._muscle_mac_text
                ),
                self._build_metric_panel(
                    "Fat", None, self._fat_concentration_text, self._fat_mac_text
                ),
            ],
        )

    def _build_metric_panel(
        self,
        name: str,
        qualifier: str | None,
        value_text: ft.Text,
        secondary_value_text: ft.Text | None,
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
            secondary_value_text: The same quantity in the second display
                unit - a MAC multiple - or None for a panel that has no
                second unit. A spacer line is drawn in its place so the
                panel keeps the height of the six that do.

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
                    (
                        secondary_value_text
                        if secondary_value_text is not None
                        else self._build_metric_secondary_value(EMPTY_METRIC_SECONDARY_VALUE)
                    ),
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
                        (
                            "Left axis: percent of one atmosphere | "
                            "Right axis: multiples of 1 MAC | "
                            "Horizontal axis: simulated seconds"
                        ),
                        color=MUTED,
                    ),
                    # The convention, stated where the numbers that depend on
                    # it are read. A MAC multiple on the alveolar trace is the
                    # conventional reading; on the other five it is a
                    # partial-pressure ratio, and the two are indistinguishable
                    # on a label unless the label says which. `docs/MODEL.md`
                    # § "MAC multiples as a display unit" is the specification
                    # this sentence is the display-side half of, and PL-DHV7
                    # the item that required both.
                    ft.Row(
                        controls=[
                            self._mac_reference_text,
                            ft.Text(
                                (
                                    "A MAC multiple is a compartment's partial pressure "
                                    "relative to the alveolar concentration that would be "
                                    "1 MAC in a 40-year-old — not a depth of anesthesia, "
                                    "and not adjusted for age or any second agent."
                                ),
                                color=MUTED,
                                italic=True,
                            ),
                        ],
                        wrap=True,
                        spacing=8,
                        run_spacing=2,
                    ),
                    # The compartment legend, which is also the control that
                    # shows and hides each trace - `_build_trace_legend_item`
                    # records why those are one row and not two. Labelled
                    # like the two rows under it, so the three kinds of mark
                    # read as three kinds.
                    ft.Row(
                        controls=[
                            ft.Text("Compartments:", color=MUTED),
                            *(
                                self._build_trace_legend_item(trace)
                                for trace in self._compartment_traces
                            ),
                        ],
                        wrap=True,
                        spacing=16,
                        run_spacing=6,
                    ),
                    # What unchecking one does, and - the part that matters -
                    # what it does not. A reader looking at two curves has to
                    # know they are looking at a chosen view of six modelled
                    # compartments rather than at a model with two, and that
                    # the run is the same run either way.
                    ft.Text(
                        (
                            "Unchecking a compartment removes its trace from the plot "
                            "only. Its concentration stays in the readouts above, and "
                            "the simulation is unchanged — this chooses what is drawn, "
                            "not what is modelled."
                        ),
                        color=MUTED,
                        italic=True,
                    ),
                    self._hidden_traces_text,
                    # The references get their own legend row rather than
                    # joining the six above. They are not compartments, and a
                    # single row would invite reading them as a seventh and
                    # eighth trace - which is the misreading PL-F52R exists to
                    # prevent, arriving through the legend instead of the
                    # chart.
                    ft.Row(
                        controls=[
                            ft.Text("Clinical references:", color=MUTED),
                            self._build_band_legend_item(
                                "MAC-awake (population, ±1 SD)", MAC_AWAKE_BAND_COLOR
                            ),
                            self._build_legend_item(
                                "1 MAC, reference adult", ONE_MAC_LINE_COLOR, "wide dash"
                            ),
                        ],
                        wrap=True,
                        spacing=16,
                        run_spacing=6,
                    ),
                    # What the band asserts, what it does not, and which trace
                    # it is read against - the last being the whole reason the
                    # sentence is here rather than only in `docs/MODEL.md`.
                    # The model has no effect-site compartment and defines the
                    # arterial fraction as the alveolar one, so the alveolar
                    # trace is the fastest curve on the chart and the furthest
                    # from where responsiveness actually returns: measured on a
                    # 3-hour 1 MAC sevoflurane case with the vaporizer turned
                    # off at 10 L/min, it crosses 0.33 MAC 2.2x earlier than
                    # the vessel-rich trace. A band read against it therefore
                    # teaches an early wake-up, which is the direction with
                    # clinical consequence.
                    ft.Row(
                        controls=[
                            self._mac_awake_reference_text,
                            ft.Text(
                                (
                                    "MAC-awake is the population concentration at which half "
                                    "of patients respond to command — a different endpoint "
                                    "from MAC, which is immobility to incision. Read the band "
                                    "against the vessel-rich trace: it is a brain "
                                    "concentration, and during washout the alveolar trace "
                                    "falls first and reaches the band earlier than the patient "
                                    "would. Not a prediction for any individual patient, and "
                                    "not a time to wake-up."
                                ),
                                color=MUTED,
                                italic=True,
                            ),
                        ],
                        wrap=True,
                        spacing=8,
                        run_spacing=2,
                    ),
                    # A third legend row, because a control mark is neither
                    # of the two kinds above it. A compartment trace is a
                    # modelled quantity and a clinical reference is a
                    # published constant; this is a record of something the
                    # *user* did, which is a claim of a different type
                    # altogether, and a row of its own is what says so
                    # before a reader has to work it out from the shape.
                    ft.Row(
                        controls=[
                            ft.Text("Run record:", color=MUTED),
                            self._build_control_mark_legend_item(),
                            ft.Text(
                                (
                                    "A vertical mark is a setting you changed, at the "
                                    "simulated time it took effect — an input to the run, "
                                    "not anything measured from the patient. The panel "
                                    "beside the chart says which setting and to what."
                                ),
                                color=MUTED,
                                italic=True,
                            ),
                        ],
                        wrap=True,
                        spacing=8,
                        run_spacing=2,
                    ),
                    ft.Container(height=CHART_HEIGHT, content=self._concentration_chart),
                    ft.Divider(height=16, color="#D9E2EC"),
                    *self._build_wash_in_section(),
                ]
            ),
            bgcolor=PANEL,
            border_radius=COMPACT_PANEL_RADIUS,
            padding=COMPACT_PANEL_PADDING,
            col={"sm": 12, "lg": 9},
        )

    def _build_wash_in_section(self) -> list[ft.Control]:
        """Build the F_A/F_I plot and everything a reader needs to read it.

        Under the compartment chart rather than beside it, on the same
        time window, because it is that chart's alveolar and circuit
        traces expressed as one number: a reader who has just watched
        them separate is looking for how far apart they are, which is
        what this plots.

        The prose is not decoration. This is the graph the uptake
        literature is taught from, so it arrives carrying a reader's
        expectations about what it means, and three of those have to be
        corrected at the point of display rather than in a document:
        which concentration the denominator is, that the curve is the
        textbook one only while that concentration is held constant, and
        that the trace is bounded to the wash-in domain and stops
        outside it. `docs/MODEL.md` § "F_A/F_I as a displayed ratio" is
        the specification these three sentences are the display-side
        half of.

        Returns:
            The controls to append to the chart panel's column.
        """

        return [
            ft.Text(
                "Wash-in: F_A/F_I, alveolar as a fraction of inspired",
                weight=ft.FontWeight.BOLD,
                color=INK,
            ),
            ft.Text(
                (
                    "Vertical axis: dimensionless ratio, 0 to 1 | "
                    "Horizontal axis: simulated seconds, the same window as above"
                ),
                color=MUTED,
            ),
            ft.Text(
                (
                    "F_I is the modelled inspired concentration, not the vaporizer "
                    "dial — the dial is what the circuit is filled from, and the "
                    "circuit only approaches it over its own time constant. Inspired "
                    "and circuit are one quantity in this model because it has a "
                    "single perfectly mixed circuit, with no dead space and no "
                    "separate inspiratory and expiratory limbs."
                ),
                color=MUTED,
                italic=True,
            ),
            ft.Text(
                (
                    "This is the wash-in curve of the uptake literature only while "
                    "the inspired concentration is held constant. The vertical marks "
                    "are where a setting was changed: a rise across one is a dial "
                    "change, not uptake. The trace stops where no agent has yet "
                    "reached the circuit, and it ends on the equilibrium line "
                    "where alveolar reaches inspired — past that the patient is "
                    "returning agent, which is elimination and not wash-in. "
                    "Modelled, not measured."
                ),
                color=MUTED,
                italic=True,
            ),
            ft.Row(
                controls=[
                    self._build_legend_item("F_A/F_I", WASH_IN_COLOR, "solid"),
                    self._build_legend_item(
                        "Equilibrium, F_A = F_I", EQUILIBRIUM_LINE_COLOR, "wide dash"
                    ),
                    self._build_control_mark_legend_item(),
                    self._wash_in_state_text,
                ],
                wrap=True,
                spacing=16,
                run_spacing=6,
            ),
            ft.Container(height=WASH_IN_CHART_HEIGHT, content=self._wash_in_chart),
        ]

    def _build_chart_sidebar(self) -> ft.Container:
        """Build the column of panels that stands beside the chart.

        The control-input timeline sits under the accounting panel rather
        than beneath the chart, because it is read *against* the chart: a
        mark on the plot and the line that says what it was are one piece
        of information split across two places, and putting them side by
        side is what lets a reader pair them without scrolling.

        Returns:
            Responsive column holding the accounting and timeline panels.
        """

        return ft.Container(
            content=ft.Column(
                controls=[
                    self._build_agent_accounting_panel(),
                    self._build_control_timeline_panel(),
                ],
                spacing=12,
            ),
            col={"sm": 12, "lg": 3},
        )

    def _build_control_timeline_panel(self) -> ft.Container:
        """Build the list of settings changed during this run.

        The record half of the chart's vertical marks. It states what the
        marks cannot - which control moved, and from what to what - and it
        is deliberately a record of *inputs*: nothing in it is a measured
        or a modelled quantity, and nothing about it says what the patient
        did in response, which is what the traces beside it are for.

        Newest first. The panel is a fixed height beside a chart rather
        than a scrollback, so the entry a reader has just produced has to
        be the one they can see; oldest-first would push each new
        adjustment off the bottom at the moment it was made.

        Returns:
            Panel holding the run's adjustments, most recent first.
        """

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Control changes", weight=ft.FontWeight.BOLD, color=INK),
                    ft.Text(
                        "What was changed during this run, most recent first. "
                        "Settings only — not a measurement.",
                        color=MUTED,
                        size=METRIC_QUALIFIER_SIZE,
                        italic=True,
                    ),
                    self._control_timeline_text,
                    self._control_timeline_overflow_text,
                ],
                spacing=4,
            ),
            bgcolor=PANEL,
            border_radius=COMPACT_PANEL_RADIUS,
            padding=COMPACT_PANEL_PADDING,
        )

    def _build_agent_accounting_panel(self) -> ft.Container:
        """Build the agent-conservation diagnostic panel.

        Returns:
            Validation panel containing agent amounts in equivalent liters
            of agent gas.
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
                ft.Container(width=LEGEND_SWATCH_WIDTH, height=LEGEND_SWATCH_HEIGHT, bgcolor=color),
                ft.Text(f"{label} ({line_style})", color=INK),
            ],
            spacing=6,
            tight=True,
        )

    @staticmethod
    def _build_trace_legend_item(trace: _CompartmentTrace) -> ft.Row:
        """Build one compartment's legend entry, which is also its control.

        One row rather than a legend beside a separate row of checkboxes.
        Two lists of the same six compartments is exactly how a legend comes
        to name a line the chart is not drawing - they agree only while
        somebody keeps them agreeing. Here the entry *is* the state: the box,
        the swatch and the label are written in one place,
        `_apply_trace_visibility`, from the same flag the chart's own series
        list is built from, so there is no second copy to fall out of step.

        The swatch carries the trace's colour while it is drawn and nothing
        while it is not, so the legend never shows a line the plot does not
        have. Its size does not change with the state: this is a control a
        reader clicks repeatedly, and a row that reflowed under the cursor
        would move the next box out from under it.

        Args:
            trace: The compartment whose entry this is.

        Returns:
            Tightly sized legend entry and visibility control.
        """

        return ft.Row(controls=[trace.swatch, trace.checkbox], spacing=6, tight=True)

    @staticmethod
    def _build_control_mark_legend_item() -> ft.Row:
        """Build the legend entry for a recorded control change.

        Drawn as an upright swatch rather than the flat bar every other
        entry uses, so the legend carries the same non-colour channel the
        mark itself does: what makes a control mark unmistakable on the
        chart is that it is the only vertical thing there, and a legend
        that showed it as one more horizontal bar would give a reader no
        way to connect the two.

        Returns:
            Tightly sized chart legend entry.
        """

        return ft.Row(
            controls=[
                ft.Container(width=3, height=16, bgcolor=CONTROL_MARK_COLOR),
                ft.Text("Control change (vertical, fine dash)", color=INK),
            ],
            spacing=6,
            tight=True,
        )

    @staticmethod
    def _build_band_legend_item(label: str, color: str) -> ft.Row:
        """Build the legend entry for a reference band, drawn as a band.

        A filled swatch with a ruled upper edge rather than the 4px line
        every other entry uses. The mark type is what distinguishes a
        measured population value with real spread from a definitional
        anchor, so a legend that drew both as lines would lose the one
        channel carrying that distinction.

        Args:
            label: Reference name, including what its extent means.
            color: Hexadecimal edge color; the fill is this at
                `MAC_AWAKE_BAND_FILL_OPACITY`, as on the chart.

        Returns:
            Tightly sized chart legend entry.
        """

        return ft.Row(
            controls=[
                ft.Container(
                    width=24,
                    height=12,
                    bgcolor=ft.Colors.with_opacity(MAC_AWAKE_BAND_FILL_OPACITY, color),
                    border=ft.Border(top=ft.BorderSide(1.5, color)),
                ),
                ft.Text(label, color=INK),
            ],
            spacing=6,
            tight=True,
        )

    @staticmethod
    def _mac_awake_band_percent(snapshot: SimulationSnapshot) -> tuple[float, float]:
        """Place this snapshot's MAC-awake band on the percent axis.

        Both the fraction and the divisor it scales come out of one
        snapshot, so the band can never be drawn from one agent's MAC-awake
        at another agent's MAC — the correct number at the wrong height on a
        labelled axis.

        Args:
            snapshot: The frame being rendered.

        Returns:
            Lower and upper edges as a percent of one atmosphere.
        """

        mac_awake = snapshot.agent_mac_awake

        return mac_awake_band_percent(
            fraction_of_mac=mac_awake.fraction_of_mac,
            standard_deviation_fraction_of_mac=(mac_awake.standard_deviation_fraction_of_mac),
            mac_percent=snapshot.agent_mac_percent,
        )

    @staticmethod
    def _format_mac_awake_reference(snapshot: SimulationSnapshot) -> str:
        """State what this snapshot's MAC-awake band was drawn from.

        Args:
            snapshot: The frame being rendered.

        Returns:
            A one-line statement of the band's centre and its edges.
        """

        mac_awake = snapshot.agent_mac_awake

        return format_mac_awake_reference(
            snapshot.agent_display_name,
            fraction_of_mac=mac_awake.fraction_of_mac,
            standard_deviation_fraction_of_mac=(mac_awake.standard_deviation_fraction_of_mac),
            mac_percent=snapshot.agent_mac_percent,
        )

    def _refresh_view(self) -> None:
        """Refresh every visible value from one controller snapshot."""

        snapshot = self._controller.snapshot()

        self._subtitle_text.value = format_subtitle(snapshot.agent_display_name)
        self._apply_agent_color_scheme(snapshot.agent_id)
        self._delivered_concentration_label.value = format_delivered_label(
            snapshot.agent_display_name
        )
        self._agent_dropdown.value = snapshot.agent_id
        self._agent_dropdown.disabled = snapshot.is_running

        self._delivered_concentration_slider.max = snapshot.max_delivered_concentration_percent
        self._delivered_concentration_slider.value = (
            snapshot.delivered_concentration_fraction * 100.0
        )
        self._concentration_chart.max_y = snapshot.max_delivered_concentration_percent
        # The divisor and the plotted range both change with the agent, so a
        # MAC axis carried over from the previous agent would label the same
        # traces against the wrong scale. Rebuilt only when one of the two
        # actually moves, for the reason recorded at `_mac_axis_basis`.
        mac_axis_basis = (snapshot.max_delivered_concentration_percent, snapshot.agent_mac_percent)

        if mac_axis_basis != self._mac_axis_basis:
            self._mac_axis_basis = mac_axis_basis
            self._mac_axis.labels = self._build_mac_axis_labels(*mac_axis_basis)

        self._mac_reference_text.value = format_mac_reference(
            snapshot.agent_display_name, snapshot.agent_mac_percent
        )
        self._mac_awake_reference_text.value = self._format_mac_awake_reference(snapshot)

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
        self._elapsed_time_text.value = format_elapsed(snapshot.elapsed_s)
        self._circuit_concentration_text.value = format_percent(
            snapshot.circuit_concentration_fraction
        )
        self._alveolar_concentration_text.value = format_percent(
            snapshot.alveolar_concentration_fraction
        )
        self._mixed_venous_concentration_text.value = format_percent(
            snapshot.mixed_venous_concentration_fraction
        )
        self._vessel_rich_concentration_text.value = format_percent(
            snapshot.vessel_rich_partial_pressure_fraction
        )
        self._muscle_concentration_text.value = format_percent(
            snapshot.muscle_partial_pressure_fraction
        )
        self._fat_concentration_text.value = format_percent(snapshot.fat_partial_pressure_fraction)

        # Every MAC line is produced from this snapshot's own divisor, so a
        # frame can never pair one agent's concentration with another agent's
        # MAC. `_refresh_view` is the only writer of both.
        mac_percent = snapshot.agent_mac_percent
        self._circuit_mac_text.value = format_mac_multiple(
            snapshot.circuit_concentration_fraction, mac_percent
        )
        self._alveolar_mac_text.value = format_mac_multiple(
            snapshot.alveolar_concentration_fraction, mac_percent
        )
        self._mixed_venous_mac_text.value = format_mac_multiple(
            snapshot.mixed_venous_concentration_fraction, mac_percent
        )
        self._vessel_rich_mac_text.value = format_mac_multiple(
            snapshot.vessel_rich_partial_pressure_fraction, mac_percent
        )
        self._muscle_mac_text.value = format_mac_multiple(
            snapshot.muscle_partial_pressure_fraction, mac_percent
        )
        self._fat_mac_text.value = format_mac_multiple(
            snapshot.fat_partial_pressure_fraction, mac_percent
        )

        self._fresh_gas_flow_text.value = format_flow(snapshot.fresh_gas_flow_l_min)
        self._delivered_concentration_text.value = format_percent(
            snapshot.delivered_concentration_fraction
        )
        self._delivered_concentration_mac_text.value = format_mac_multiple(
            snapshot.delivered_concentration_fraction, mac_percent
        )
        self._alveolar_ventilation_text.value = format_flow(snapshot.alveolar_ventilation_l_min)
        self._cardiac_output_text.value = format_flow(snapshot.cardiac_output_l_min)

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

        # The references span the same window as the traces and are moved in
        # the same frame, so a scroll can never leave one ruled across part of
        # the chart or drawn at the previous agent's height.
        mac_awake_lower_percent, mac_awake_upper_percent = self._mac_awake_band_percent(snapshot)
        chart_series.redraw_reference_band(
            self._mac_awake_band_series,
            chart_min_x,
            chart_max_x,
            mac_awake_lower_percent,
            mac_awake_upper_percent,
        )
        chart_series.redraw_reference_line(
            self._one_mac_line_series, chart_min_x, chart_max_x, snapshot.agent_mac_percent
        )

        # Two reads of one controller, and they cannot disagree: this
        # method is synchronous, so no `await` can fall between them and the
        # simulation loop cannot advance a step in the gap. That is what
        # keeps the right-hand end of every trace the same sample the
        # readouts above were formatted from, which `chart_downsampling.py`
        # states as a property of the display rather than an accident of
        # ordering. The window asked for is the axis just set, so the samples
        # that arrive are exactly the ones this frame draws (`PL-0VM7`).
        #
        # Read once and drawn twice: both plots span the same window, so one
        # read is what makes them the same *samples* and not merely the same
        # axis numbers.
        # Only the traces the reader has left shown. A hidden trace costs
        # nothing here and holds nothing on the client, because
        # `_chart_data_series` has taken it off the chart as well - the two
        # go together, and `chart_series.redraw_visible_window` says why
        # doing one without the other would leave a stale curve drawn.
        window = self._controller.history_window(chart_min_x)
        chart_series.redraw_visible_window(self._visible_plotted_series, window)

        adjustments = group_adjustments(snapshot.control_timeline)
        self._redraw_control_marks(adjustments, chart_min_x, chart_max_x, snapshot)
        self._refresh_wash_in(snapshot, window, chart_min_x, chart_max_x)
        self._refresh_control_timeline(adjustments)

    def _redraw_control_marks(
        self,
        adjustments: tuple[ControlAdjustment, ...],
        chart_min_x: float,
        chart_max_x: float,
        snapshot: SimulationSnapshot,
    ) -> None:
        """Stand a mark at each adjustment the visible window contains.

        The pool is fixed, so the marks drawn are the *most recent* that
        fit rather than an arbitrary subset: a reader watching a run is
        reading the change they just made against the curve it moved. What
        the pool cannot show is not dropped in silence - the panel beside
        the chart says how many marks are missing, because a plot that
        quietly stops annotating is a plot that asserts nothing happened.

        Every mark spans the plotted range, which follows the running
        agent's dial maximum, so it is taken from the snapshot rather than
        from the chart control: the two are set in the same frame and this
        way they cannot be read from different ones.
        """

        visible = [
            adjustment
            for adjustment in adjustments
            if chart_min_x <= adjustment.started_at_s <= chart_max_x
        ]
        drawn = visible[-MAX_CHART_CONTROL_MARKS:]
        self._undrawn_control_marks = len(visible) - len(drawn)

        # Both charts, in one pass over one list. A Flet control belongs to
        # one chart, so the two pools are distinct objects - but which
        # adjustments they stand for must not be, and drawing them from
        # separate call sites is how one plot comes to be annotated and the
        # other not. Each pool spans its own chart's plotted range.
        for mark_series, top_y in (
            (self._control_mark_series, snapshot.max_delivered_concentration_percent),
            (self._wash_in_control_mark_series, WASH_IN_AXIS_MAXIMUM),
        ):
            for series, adjustment in zip(mark_series, drawn, strict=False):
                chart_series.redraw_control_mark(series, adjustment.started_at_s, top_y)

            for series in mark_series[len(drawn) :]:
                chart_series.park_control_mark(series)

    def _refresh_wash_in(
        self,
        snapshot: SimulationSnapshot,
        window: HistoryWindow,
        chart_min_x: float,
        chart_max_x: float,
    ) -> None:
        """Redraw the F_A/F_I plot and say what it is currently showing.

        The window is taken from the same two numbers the compartment
        chart above was just set to, in the same frame, so the two plots
        can never be showing different spans of the run while sitting one
        above the other. The samples are the very ones that chart drew,
        passed down rather than re-read, so the two cannot even differ by
        a step the run took in between.

        Args:
            snapshot: The frame being rendered.
            window: The samples the compartment chart was just drawn from.
            chart_min_x: Left edge of the visible window, in simulated
                seconds.
            chart_max_x: Right edge of the visible window, in simulated
                seconds.
        """

        self._wash_in_chart.min_x = chart_min_x
        self._wash_in_chart.max_x = chart_max_x
        # Moved in the same frame as the trace that ends on it, so a scroll
        # can never leave the line ruled across part of the plot while the
        # curve terminating on it spans the whole of it.
        chart_series.redraw_reference_line(
            self._equilibrium_line_series, chart_min_x, chart_max_x, WASH_IN_EQUILIBRIUM_RATIO
        )
        self._undrawn_wash_in_segments = chart_series.redraw_wash_in_segments(
            self._wash_in_segment_series, window, WASH_IN_TERMINUS_CEILING
        )
        self._wash_in_state_text.value = self._format_wash_in_state(snapshot)

    def _format_wash_in_state(self, snapshot: SimulationSnapshot) -> str:
        """State what the wash-in plot is showing at this instant, and why.

        A trace that stops has to say which of its two boundaries it
        stopped at: "nothing has reached the circuit yet" and "the patient
        is giving agent back" are opposite situations, and a reader shown
        only an empty plot would have neither. Where the trace *is*
        drawing, the number here is the same value its right-hand end
        stands at, so the plot and the sentence beside it cannot disagree.

        Args:
            snapshot: The frame being rendered.

        Returns:
            One line for the row above the plot.
        """

        reading = read_wash_in(
            snapshot.alveolar_concentration_fraction, snapshot.circuit_concentration_fraction
        )

        if reading.plotted_ratio is not None:
            state = f"Now: F_A/F_I = {format_wash_in_ratio(reading.plotted_ratio)}"
        elif reading.domain is WashInDomain.NO_INSPIRED_AGENT:
            state = "Not defined: no agent has reached the circuit yet."
        else:
            state = (
                "Past equilibrium: alveolar exceeds inspired — the patient is "
                "returning agent, which is elimination and not wash-in."
            )

        if self._undrawn_wash_in_segments:
            state = f"{state} ({self._undrawn_wash_in_segments} earlier stretch(es) not drawn)"

        return state

    def _refresh_control_timeline(self, adjustments: tuple[ControlAdjustment, ...]) -> None:
        """Write the run's adjustments into the panel beside the chart.

        Most recent first, bounded, and honest about the bound: what the
        panel cannot fit is counted rather than left off, and so is what
        the chart could not mark, since a reader comparing the two would
        otherwise conclude that a change they made was never recorded.
        """

        if not adjustments:
            self._control_timeline_text.value = NO_CONTROL_CHANGES_TEXT
            self._control_timeline_overflow_text.visible = False
            self._control_timeline_overflow_text.value = ""

            return

        listed = adjustments[-MAX_LISTED_ADJUSTMENTS:]
        self._control_timeline_text.value = "\n".join(
            format_adjustment(adjustment) for adjustment in reversed(listed)
        )

        unlisted = len(adjustments) - len(listed)
        notes = []

        if unlisted:
            notes.append(f"{unlisted} earlier change(s) not listed")

        if self._undrawn_control_marks:
            notes.append(f"{self._undrawn_control_marks} not marked on the chart")

        self._control_timeline_overflow_text.value = "; ".join(notes)
        self._control_timeline_overflow_text.visible = bool(notes)

    def _apply_trace_visibility(self) -> None:
        """Put exactly the shown traces on the chart, and say the legend's part.

        The one writer of everything that has to agree about which
        compartments are drawn: the chart's series list, each entry's
        checkbox, swatch and label, and the line said when none is drawn.
        They are written from one flag in one pass, which is what makes the
        legend's agreement with the plot a property of the code rather than
        of somebody's diligence.

        **Called when visibility changes and at no other time.** Reassigning
        the chart's series list is the whole-list churn `_mac_axis_basis`
        guards the axis against, and nothing about it belongs on a render
        tick: `visible` is only ever moved by a reader clicking a box.

        **A trace being shown again still holds the points of the frame it
        was last drawn in.** The caller must redraw before calling this, so
        that a stale curve is never on the chart even momentarily -
        `_handle_trace_visibility_change` is the caller and records the
        ordering.
        """

        self._concentration_chart.data_series = self._chart_data_series()

        for trace in self._compartment_traces:
            trace.checkbox.value = trace.visible
            trace.checkbox.label_style = ft.TextStyle(color=INK if trace.visible else MUTED)
            trace.swatch.bgcolor = trace.color if trace.visible else None

        self._hidden_traces_text.visible = not any(
            trace.visible for trace in self._compartment_traces
        )

    def _handle_trace_visibility_change(
        self, trace: _CompartmentTrace, event: ft.Event[ft.Checkbox]
    ) -> None:
        """Show or hide one compartment trace at the reader's request.

        The flag lives in the view rather than in the controller, for the
        reason `_rejected_setting_notice` does: which traces someone is
        looking at changes nothing about the simulation and must not.
        Identical inputs still produce identical results whatever is on
        screen, so nothing here reads or writes model state, and this is
        not routed through `_apply_setting` - there is no value for the core
        to refuse.

        Args:
            trace: The compartment whose box was clicked.
            event: The checkbox event carrying its new state.
        """

        trace.visible = bool(event.control.value)
        # Redrawn before it is put back on the chart, never after. A trace
        # hidden for a while still carries the points of the frame it was
        # last drawn in, and adding it to the chart first would put that
        # stale curve one raise away from reaching the client. Nothing is
        # sent until `update()`, so a reader sees only the finished frame.
        self._refresh_view()
        self._apply_trace_visibility()
        self._page.update()

    def _apply_agent_color_scheme(self, agent_id: str) -> None:
        """Apply the verified agent color to the header and selection control."""

        scheme = AGENT_COLOR_SCHEMES[agent_id]
        style = AGENT_RENDER_STYLES[agent_id]
        self._agent_header_badge.bgcolor = scheme.fill
        self._agent_header_badge.border = style.badge_border
        self._subtitle_text.color = scheme.foreground

        self._agent_dropdown.fill_color = scheme.fill
        self._agent_dropdown.bgcolor = scheme.fill
        self._agent_dropdown.color = scheme.foreground
        self._agent_dropdown.text_style = style.dropdown_text_style
        self._agent_dropdown.border_color = scheme.foreground
        self._agent_dropdown.focused_border_color = scheme.foreground

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

    def _handle_adjustment_start(self, event: ft.Event[ft.Slider]) -> None:
        """Tell the controller a new user adjustment is beginning.

        A slider reports its value continuously while it is dragged, so one
        turn of one dial reaches the controller as a run of changes - the
        same shape two separate turns of that dial arrive in. This is where
        the difference is known, and the only place it is: the drag has a
        beginning, and the interface is told about it.

        It changes no simulation state and records nothing on its own, so it
        does not go through `_apply_setting`: there is no value here for the
        core to refuse, and nothing on screen that could come to disagree
        with the snapshot.
        """

        del event
        self._controller.begin_control_adjustment()

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

        Stepping is deliberately separate from drawing, and how many steps a
        tick takes is a constant of this loop rather than a function of how
        long the tick actually took. A host that wakes the loop late leaves
        the run behind the wall clock, and it stays behind: no tick takes
        extra steps to make up the difference, and nothing here reads a
        clock. So a slow machine, a busy event loop or a skipped frame makes
        the run *slower* and never *different* - identical inputs still
        produce an identical trajectory, sample for sample. That is the
        reproducibility guarantee `docs/MODEL.md` states under "Time", and
        the property a run compared against another run rests on; the
        alternative, stepping until simulated time catches up to elapsed
        real time, would make the trajectory a property of the machine.

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
    def _build_metric_secondary_value(initial_value: str) -> ft.Text:
        """Build the second-unit line drawn under a dashboard metric.

        Args:
            initial_value: Initial formatted value including its unit, or
                `EMPTY_METRIC_SECONDARY_VALUE` for a panel with no second
                unit.

        Returns:
            Styled Flet text control, subordinate to the reading above it.
        """

        return ft.Text(initial_value, size=METRIC_SECONDARY_VALUE_SIZE, color=MUTED)

    @staticmethod
    def _build_mac_axis_labels(max_percent: float, mac_percent: float) -> list[fch.ChartAxisLabel]:
        """Build the chart's MAC axis labels for one agent and range.

        The placement is `formatting.mac_axis_ticks`, which is Flet-free
        and tested on its own; this only wraps each tick in the control
        the chart draws it with.

        Args:
            max_percent: Top of the chart's percent axis.
            mac_percent: Running agent's 1 MAC as a percent of one
                atmosphere.

        Returns:
            One label per tick, positioned in the chart's own percent
            coordinates.
        """

        return [
            fch.ChartAxisLabel(
                value=percent, label=ft.Text(label, color=MUTED, size=METRIC_QUALIFIER_SIZE)
            )
            for percent, label in mac_axis_ticks(max_percent, mac_percent)
        ]
