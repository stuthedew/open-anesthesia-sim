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
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Final

import flet as ft
import flet_charts as fch

from anesthesia_sim.app import chart_series
from anesthesia_sim.app.chart_time_base import (
    FIT_RUN_KEY,
    SELECTABLE_TIME_BASES,
    TIME_BASE_LADDER,
    ChartTimeBase,
    fit_to_run,
    fitted_window,
    following_window,
    tick_times,
    time_base_for_span,
)
from anesthesia_sim.app.control_timeline import (
    ControlAdjustment,
    format_adjustment,
    group_adjustments,
)
from anesthesia_sim.app.controller import (
    DrawnWindow,
    RecordedQuantity,
    RecordedSeries,
    SimulationController,
    SimulationSnapshot,
)
from anesthesia_sim.app.formatting import (
    CONCENTRATION_DISPLAY_DECIMALS,
    CONCENTRATION_DISPLAY_RESOLUTION_PERCENT,
    FLOW_DISPLAY_DECIMALS,
    chart_axis_top_percent,
    chart_grid_interval_percent,
    format_case_discard_warning,
    format_chart_time_label,
    format_delivered_label,
    format_elapsed,
    format_flow,
    format_mac_awake_reference,
    format_mac_multiple,
    format_mac_reference,
    format_percent,
    format_playback_rate,
    format_subtitle,
    format_supported_run_length,
    format_time_base,
    format_wash_in_ratio,
    mac_awake_band_percent,
    mac_axis_ticks,
)
from anesthesia_sim.app.playback import (
    DEFAULT_PLAYBACK_RATE,
    SUPPORTED_PLAYBACK_RATES,
    PlaybackRate,
    playback_rate_for,
)
from anesthesia_sim.app.theme import (
    ACCENT,
    ACCENT_TEXT,
    ACCOUNTING_STATUS_SIZE,
    AGENT_COLOR_SCHEMES,
    AGENT_SELECTOR_WIDTH,
    ALVEOLAR_COLOR,
    APP_TITLE_SIZE,
    BAND_SWATCH_HEIGHT,
    BAND_SWATCH_WIDTH,
    CHART_HEIGHT,
    CIRCUIT_COLOR,
    CONTROL_MARK_COLOR,
    CONTROL_MARK_DASH_PATTERN,
    CONTROL_MARK_STROKE_WIDTH,
    CONTROL_MARK_SWATCH_HEIGHT,
    CONTROL_MARK_SWATCH_WIDTH,
    EQUILIBRIUM_LINE_COLOR,
    EQUILIBRIUM_LINE_DASH_PATTERN,
    EQUILIBRIUM_LINE_STROKE_WIDTH,
    FAT_COLOR,
    GRIDLINE,
    INK,
    LEGEND_SWATCH_HEIGHT,
    LEGEND_SWATCH_WIDTH,
    MAC_AWAKE_BAND_COLOR,
    MAC_AWAKE_BAND_EDGE_STROKE_WIDTH,
    MAC_AWAKE_BAND_FILL_OPACITY,
    METRIC_NAME_SIZE,
    METRIC_QUALIFIER_SIZE,
    METRIC_SECONDARY_VALUE_SIZE,
    METRIC_VALUE_SIZE,
    MIXED_VENOUS_COLOR,
    MUSCLE_COLOR,
    MUTED,
    NEW_CASE_DIALOG_SPACING,
    NEW_CASE_DIALOG_WIDTH,
    ONE_MAC_LINE_COLOR,
    ONE_MAC_LINE_DASH_PATTERN,
    ONE_MAC_LINE_STROKE_WIDTH,
    PAGE_PADDING,
    PANEL,
    PANEL_PADDING,
    PANEL_RADIUS,
    PARAMETER_QUALIFIER_SIZE,
    PLAYBACK_RATE_SELECTOR_WIDTH,
    RUNNING_AGENT_DISPLAY_PADDING,
    SECTION_DIVIDER_HEIGHT,
    TIME_BASE_SELECTOR_WIDTH,
    VESSEL_RICH_COLOR,
    WARNING,
    WASH_IN_AXIS_LABEL_SIZE,
    WASH_IN_CHART_HEIGHT,
    WASH_IN_COLOR,
    WASH_IN_STROKE_WIDTH,
)
from anesthesia_sim.app.wash_in import WASH_IN_EQUILIBRIUM_RATIO, WashInDomain, read_wash_in
from anesthesia_sim.app_metadata import APP_DISPLAY_NAME
from anesthesia_sim.core.exceptions import AnesthesiaSimulationError, SimulationDomainLimitError
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
# is `core/`'s to declare and no longer this module's:
# `core.uptake_system.MAXIMUM_SIMULATION_STEP_S` is that declaration, and a step
# above it is refused there rather than displayed here.
#
# This is a cadence choice inside that range, and it sits at the ceiling
# deliberately. Running finer would buy nothing a reader could see: with
# settings held, halving the step moves a displayed fraction by around 1e-16,
# which is nine orders below anything the readout resolves. Running coarser
# would cost control resolution, which is what `core/`'s constant is a
# tolerance on. `test_the_shipped_step_is_within_the_maximum_simulation_step`
# holds the relationship, so a cadence and a limit cannot drift apart
# unnoticed.
#
# The two coinciding is a fact about this configuration rather than an
# identity, which is why they are named apart. Neither is derived from the
# other, and neither is derived from how many decimals the readout shows -
# docs/MODEL.md § "Supported simulation step" and § "Displayed precision"
# carry the two derivations separately (`PL-X9KD`).
SIMULATION_STEP_S = 0.1
# How often the simulation loop wakes, in *real* seconds. Numerically equal to
# the step above and conceptually unrelated to it: one is a property of the
# model's numerics and the other of this host's event loop. They are named
# apart because the playback multiplier is the ratio between them - a tick
# advances `rate.steps_per_tick(...)` steps of `SIMULATION_STEP_S`, which is
# `multiplier` times faster than real time only because a tick is one step
# long. Spelling the equality out is what lets that derivation be checked
# (`app/playback.py`, and
# `test_a_tick_is_one_simulation_step_of_real_time`) rather than assumed;
# re-tuning the wakeup for the host would otherwise silently falsify every
# rate the interface displays.
#
# It is also the interface's control resolution, which is the second thing
# this constant decides and the one that is easy to miss (`PL-NBWP`). A tick
# advances its whole burst uninterrupted, so a setting changed while the run
# plays first acts at a tick boundary: the reachable simulated instants are
# `multiplier` times this interval apart, which is 30 s at 300x. Shortening
# it would tighten that grid at the cost of waking the loop more often.
SIMULATION_TICK_INTERVAL_S = SIMULATION_STEP_S
# Render cadence, deliberately independent of the simulation step. The two
# were previously the same 10 Hz tick, which made every redraw a gate on the
# next simulation step and on servicing the next button press.
#
# Twice the tick interval, so a frame is two control-grid steps at every
# playback rate - 0.2 s of simulated time apart at 1x and 60 s at 300x. That
# ordering is why `PL-NBWP` left the grid where it is: a finer grid would
# resolve control timing the display cannot show, so tightening one without
# the other buys a reader nothing.
#
# Written as its own number rather than derived from the tick, for the same
# reason the step and the tick are named apart above: a display cadence and
# an event-loop cadence are separate decisions that happen to be in this
# ratio today. `test_a_frame_is_two_control_grid_steps_at_every_rate` holds
# the relation instead, because it is the premise of a published argument
# rather than an incidental ratio, and a test is what makes it fail here
# rather than silently in `docs/MODEL.md`.
RENDER_INTERVAL_S = 0.2
# How wide the chart is before the first frame runs. Every frame after it
# derives the width from the selected time base, so this is only what the
# control is constructed holding - the narrowest rung, which is what "Fit
# run" answers with on a run that has recorded nothing yet.
INITIAL_CHART_TIME_BASE = TIME_BASE_LADDER[0]


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

# Said when a drawn trace goes above the top of the plot, naming which.
#
# A fixed axis can be exceeded, and `CHART_AXIS_TOP_MAC` is exceeded by a
# setting in common use rather than by an edge case: sevoflurane's 8% dial is
# 4.00 MAC and is a common inhalational-induction setting, so the circuit trace
# leaving the frame is a thing a lesson will do on purpose. What must not happen is
# that it leave *quietly* — a trace clipped at the ceiling draws as a
# horizontal line, and a horizontal line is what a plateau looks like. A
# reader would conclude the concentration had stopped rising at 3 MAC, which
# is a wrong clinical reading of a correct model.
#
# So the plot says so, and says where the true value is. The alternative
# considered and rejected was growing the axis to fit: that redraws the
# curve at a smaller height partway through the induction it is being used
# to teach, which trades a visible cut-off for an invisible rescale.
OFF_SCALE_NOTICE_TEMPLATE = (
    "Above the top of the plot: {compartments}. The axis stops at {top} and these "
    "traces are cut off there — their values are in the readouts above, which are "
    "not clipped."
)


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

# What the confirmation says before a new case replaces a recorded one, in
# the order a reader meets it. Three statements rather than one paragraph,
# because they answer three different questions and a reader stops at the
# first that satisfies them: why this is a new case at all, what is about to
# be lost, and what survives. The middle one is built per case by
# `formatting.format_case_discard_warning`, which quotes the run's own
# elapsed time and control-change count.
#
# `NEW_CASE_CARRYOVER_TEMPLATE` is a claim about `SimulationController.set_agent`
# and has to stay true with it: that method preserves the circuit and patient
# settings and takes the delivered concentration from the new agent's own
# `mac_percent`.
NEW_CASE_TITLE_TEMPLATE = "Start a new {agent} case?"
NEW_CASE_IS_NOT_A_VIEW_TEXT = (
    "Changing agent starts a new case. This model does not simulate switching "
    "between volatile agents, so a run cannot be continued under a different one."
)
NEW_CASE_CARRYOVER_TEMPLATE = (
    "Circuit volume, fresh gas flow, alveolar ventilation and cardiac output "
    "carry over. Delivered {agent} starts at that agent's own 1 MAC."
)
# Both buttons name their outcome rather than answering a question, so
# neither can be pressed on the reading that "OK" confirms whatever was on
# screen. The declining one is also the *default*: it is the filled button
# and it sits where a dialog's primary action sits, so the press a reader
# makes without reading is the one that keeps their case. Placing the
# destructive action there instead would put an unrecoverable loss under
# exactly the reflex this dialog exists to interrupt.
KEEP_CURRENT_CASE_TEMPLATE = "Keep the {agent} case"
START_NEW_CASE_TEMPLATE = "Discard and start {agent}"

# While a run is going the agent selector is *replaced* rather than greyed.
# Disabling it is what the run needs - choosing an agent discards the case -
# but a disabled control is not a neutral rendering of the same information:
# Flet/Material paints its label in the theme's disabled-content grey, which
# overrides the `color=` and `text_style=` the agent scheme sets while leaving
# the saturated ISO 5360 fill behind it. Grey on purple, at the one moment
# every number beside it - percent, MAC multiple, alveolar and mixed-venous
# partial pressures - is agent-specific, which is the wrong-context failure
# `CLAUDE.md`'s presentation clause names rather than a styling complaint
# (PL-61WW).
#
# Two things follow from replacing it rather than restyling it. The colour on
# screen during a run is `AgentColorScheme.foreground` on `.fill` - a declared
# pair `tools/contrast_check.py` measures - instead of a Material default that
# appears in no source file and so cannot be measured at all. And the display
# gets to say what the greyed control could not: a disabled dropdown reads as
# "unavailable", where what a reader needs while a run is going is "this is
# what is running", with why it cannot be changed second.
#
# The caption says "running" rather than "this case" because that is what is
# true: the selector returns on Pause, and a label claiming the agent is fixed
# for the case would be a mode statement contradicted by the next click.
RUNNING_AGENT_LOCK_TEXT = "Locked while running"

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

# The same names, keyed for the one lookup that has an agent id and no
# snapshot to read the name off: the agent a reader has just selected, which
# is not the one the controller is answering for until they confirm it.
AGENT_DISPLAY_NAMES: Final[Mapping[str, str]] = dict(AVAILABLE_AGENTS)

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

    def plotted(self, substance_id: str) -> chart_series.PlottedSeries:
        """This trace paired with the one recorded series it draws.

        The substance is the caller's because it is a property of the run
        rather than of the trace: the six traces draw whichever agent the
        controller is running, and `set_agent` starts a new run under a new
        identifier. Holding a copy of it on the trace would be a second
        place for the running agent to be recorded, free to disagree with
        the snapshot the same frame formats its readouts from.

        Args:
            substance_id: The substance whose run is being drawn, from the
                snapshot of the frame drawing it.

        Returns:
            This trace bound to that substance's values for its compartment.
        """

        return (self.series, RecordedSeries(substance_id, self.quantity))


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
        self._page.padding = PAGE_PADDING
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
        # Whether the charts are currently answering a hover. Held so that
        # `_apply_trace_visibility` can put a trace back on the chart in the
        # mode the last frame set, rather than reading the run again and
        # possibly disagreeing with the frame it was called from. Starts
        # false so that the first frame's write is the one that decides it,
        # whatever state the run is in when the dashboard is mounted.
        self._chart_tooltips_enabled = False
        # Whether a frame is owed to a setting change that chose not to draw
        # its own. Set by a coalesced `_apply_setting` and cleared by the
        # render tick that pays it, which is what lets that tick run while
        # the simulation is stopped - a paused reader moving a dial still
        # needs the readouts beside it to move.
        self._render_pending = False
        # The agent a reader has asked for and not yet confirmed, and the
        # dialog asking them. Held here rather than passed through the
        # button callbacks because Flet hands a callback its own control and
        # nothing else, and because this pair *is* the state "a destructive
        # confirmation is open": `_resolve_new_case` clears the first, which
        # is what makes answering the dialog idempotent when Flet reports
        # the dismissal that follows a button press.
        self._pending_agent_id: str | None = None
        self._new_case_dialog: ft.AlertDialog | None = None
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
            "Valid", color=ACCENT_TEXT, size=ACCOUNTING_STATUS_SIZE, weight=ft.FontWeight.BOLD
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
        #
        # **Six patterns, all different, because the line style is what
        # actually separates these curves.** The colours above cannot: the
        # closest pair sits at 1.01 for normal colour vision and no palette
        # reaches 3:1. Circuit and vessel-rich were both solid until PL-GVXP,
        # which made the second channel redundant in name only for the one
        # pair - and a reader who takes a value off the wrong curve has
        # misread a clinical quantity, not a decoration.
        #
        # **Which style goes on which trace is decided by the colours, not
        # chosen freely.** The two traces a reader can least separate by
        # colour get the two marks they can most separate by shape, and so on
        # outward. So the closest pairs - vessel-rich against fat at 1.01, and
        # mixed venous against fat at 1.02 under simulated deuteranopia - are
        # an even dash against an alternating dash-dot, and a short uniform
        # dash against that same dash-dot: each differs from its partner in
        # mark length, in gap length and in rhythm at once. The one genuinely
        # confusable pair in the set, the 2 px dots against the 4 px short
        # dash, is spent on mixed venous against muscle, which is the *widest*
        # separation any pair of these six has (1.45). `docs/MODEL.md` carries
        # the matrix this was read off.
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
            # Equal mark and gap, which is the one rhythm no other trace here
            # has: the other four dashed traces all draw more ink than gap.
            # Deliberately not a second long dash - at [8, 8] it read as the
            # alveolar trace's [10, 4] with wider gaps, and those two sit at
            # 1.08 under simulated deuteranopia, which is no place to put a
            # pair that has to be told apart by mark length alone.
            self._build_compartment_trace(
                RecordedQuantity.VESSEL_RICH,
                "Vessel-rich",
                VESSEL_RICH_COLOR,
                2,
                "even dash",
                [6, 6],
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
        # The companion to the notice above, and held for the same reason:
        # both report something the plot is not showing, and both are written
        # by exactly one method so the words and the picture cannot part.
        # This one is written per frame, by `_refresh_off_scale_notice`,
        # because whether a trace is off scale is a property of the samples
        # rather than of the checkboxes.
        self._off_scale_text = ft.Text(
            "", color=WARNING, size=METRIC_QUALIFIER_SIZE, italic=True, visible=False
        )
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
        # Two series for one mark: the upper edge carries the fill, cut off
        # at the lower edge by `redraw_reference_band`, and the lower edge
        # strokes the boundary that cut-off makes. Neither is a reference of
        # its own and the legend shows one entry, because they are the two
        # ends of a single published interval.
        self._mac_awake_band_upper_edge = chart_series.build_reference_line(
            color=MAC_AWAKE_BAND_COLOR, stroke_width=MAC_AWAKE_BAND_EDGE_STROKE_WIDTH
        )
        self._mac_awake_band_upper_edge.below_line_bgcolor = ft.Colors.with_opacity(
            MAC_AWAKE_BAND_FILL_OPACITY, MAC_AWAKE_BAND_COLOR
        )
        self._mac_awake_band_lower_edge = chart_series.build_reference_line(
            color=MAC_AWAKE_BAND_COLOR, stroke_width=MAC_AWAKE_BAND_EDGE_STROKE_WIDTH
        )
        self._one_mac_line_series = chart_series.build_reference_line(
            color=ONE_MAC_LINE_COLOR,
            stroke_width=ONE_MAC_LINE_STROKE_WIDTH,
            dash_pattern=ONE_MAC_LINE_DASH_PATTERN,
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
        # One number, where this used to be two. The plotted range is now
        # `CHART_AXIS_TOP_MAC` times this very quantity, so the agent's 1 MAC
        # is the only thing either the ticks or the ceiling depend on, and
        # the two cannot come to disagree about the scale they describe.
        self._mac_axis_basis = initial_snapshot.agent_mac_percent
        self._mac_axis = fch.ChartAxis(
            # `×MAC`, the same token every numeric MAC readout on the page
            # carries (`formatting.MAC_UNIT_SUFFIX`), rather than a second
            # wording for one unit. The ticks read bare numbers - "0.5",
            # "1.0" - so this title is the only thing that says what they
            # are, which is exactly the position `docs/MODEL.md` § "MAC
            # multiples as a display unit" writes the notation rule for:
            # "0.80 MAC" is read as a depth of anesthesia and "0.80 ×MAC" as
            # the partial-pressure ratio it is. The divisor is not repeated
            # here because `_mac_reference_text` names it in full - "1 MAC
            # sevoflurane = 2.0%" - a few lines above the plot (PL-6580).
            title=ft.Text("×MAC", color=MUTED, size=METRIC_QUALIFIER_SIZE),
            labels=self._build_mac_axis_labels(self._mac_axis_basis),
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
            chart_series.build_series(color=WASH_IN_COLOR, stroke_width=WASH_IN_STROKE_WIDTH)
            for _ in range(MAX_CHART_WASH_IN_SEGMENTS)
        ]
        self._equilibrium_line_series = chart_series.build_reference_line(
            color=EQUILIBRIUM_LINE_COLOR,
            stroke_width=EQUILIBRIUM_LINE_STROKE_WIDTH,
            dash_pattern=EQUILIBRIUM_LINE_DASH_PATTERN,
        )
        self._wash_in_state_text = ft.Text("", color=MUTED, size=METRIC_QUALIFIER_SIZE)
        self._control_timeline_text = ft.Text(
            NO_CONTROL_CHANGES_TEXT, color=MUTED, size=METRIC_QUALIFIER_SIZE
        )
        self._control_timeline_overflow_text = ft.Text(
            "", color=MUTED, size=METRIC_QUALIFIER_SIZE, italic=True, visible=False
        )
        # The chart's time base: how wide the visible window is. `None` is
        # "Fit run", the default, which is a rule for choosing the width each
        # frame rather than one of the widths - the whole run, on the
        # narrowest rung of `TIME_BASE_LADDER` that contains it. A rung here
        # instead means the reader has chosen a width and the window follows
        # the run at it.
        #
        # Like the compartment checkboxes and unlike the agent dropdown, this
        # is a *view* control and reaches no model state: it changes which
        # part of the recorded run is drawn and never what was recorded, so
        # identical inputs still produce an identical run. It is therefore
        # never disabled - the reason to reach for it is usually to widen the
        # window on a run already going - and Reset leaves it alone, like
        # every other reader setting.
        self._time_base: ChartTimeBase | None = None
        # What the last frame actually drew, which is not the line above:
        # under "Fit run" the width is derived from the run's length, so it
        # moves without anybody touching the control. Held so the axis labels
        # and the caption can be rebuilt when it moves and left alone when it
        # does not - the same guard, and for the same reason, as
        # `_mac_axis_basis`.
        self._drawn_time_base = INITIAL_CHART_TIME_BASE
        self._drawn_tick_times: tuple[float, ...] = ()
        self._time_base_dropdown = ft.Dropdown(
            value=FIT_RUN_KEY,
            options=[
                ft.dropdown.Option(key=FIT_RUN_KEY, text="Fit run"),
                *(
                    ft.dropdown.Option(
                        key=str(time_base.span_s), text=format_time_base(time_base.span_s)
                    )
                    for time_base in SELECTABLE_TIME_BASES
                ),
            ],
            width=TIME_BASE_SELECTOR_WIDTH,
            filled=True,
            fill_color=PANEL,
            bgcolor=PANEL,
            color=INK,
            border_color=MUTED,
            focused_border_color=INK,
            label="Time base",
            on_select=self._handle_time_base_change,
        )
        # One axis object per chart rather than one shared between them: a
        # Flet control belongs to a single chart, the same constraint the two
        # pools of control marks are built around. `show_min` and `show_max`
        # are off because the window's own edges are not ticks - while the
        # window follows the run they fall wherever the newest sample puts
        # them, and a label there would read as a gridline that is not ruled.
        self._time_axis = self._build_time_axis()
        self._wash_in_time_axis = self._build_time_axis()
        # The two axis captions, held rather than built inline because both
        # state the span the chart is currently showing, which moves. Saying
        # it is not decoration: under "Fit run" the width is chosen by the
        # run's length rather than by the reader, so the caption is the only
        # place the plot says how much time it is showing.
        self._time_axis_caption = ft.Text(self._time_axis_caption_text(), color=MUTED)
        self._wash_in_time_axis_caption = ft.Text(
            "Vertical axis: dimensionless ratio, 0 to 1 | "
            "Horizontal axis: simulated time, the same window as above",
            color=MUTED,
        )
        self._concentration_chart = fch.LineChart(
            data_series=self._chart_data_series(),
            min_x=0,
            max_x=INITIAL_CHART_TIME_BASE.span_s,
            min_y=0,
            # Denominated in MAC rather than in the agent's dial maximum, so
            # every agent is drawn against one ruler; `CHART_AXIS_TOP_MAC`
            # carries why, and why it does not move during a run.
            max_y=chart_axis_top_percent(initial_snapshot.agent_mac_percent),
            left_axis=fch.ChartAxis(
                # "percent of what" has to be on the axis, because after
                # PL-6580 stripped the caption's axis key this is the only
                # place the left scale is named. Not "vol %": that is a
                # gas-phase volume fraction, true of the circuit and
                # alveolar traces and a category error on the muscle, fat
                # and vessel-rich ones, which hold a partial pressure that
                # convention quotes as a percentage of an atmosphere.
                # `docs/MODEL.md` § "MAC multiples as a display unit" states
                # the compartments are displayed "as a percent of one
                # atmosphere", and this is that phrase at axis length.
                title=ft.Text("% of 1 atm", color=MUTED, size=METRIC_QUALIFIER_SIZE)
            ),
            right_axis=self._mac_axis,
            bottom_axis=self._time_axis,
            horizontal_grid_lines=fch.ChartGridLines(
                interval=chart_grid_interval_percent(initial_snapshot.agent_mac_percent),
                color=GRIDLINE,
            ),
            vertical_grid_lines=fch.ChartGridLines(
                interval=INITIAL_CHART_TIME_BASE.tick_interval_s, color=GRIDLINE
            ),
            expand=True,
        )
        self._wash_in_chart = fch.LineChart(
            data_series=[
                *self._wash_in_control_mark_series,
                self._equilibrium_line_series,
                *self._wash_in_segment_series,
            ],
            min_x=0,
            max_x=INITIAL_CHART_TIME_BASE.span_s,
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
            bottom_axis=self._wash_in_time_axis,
            horizontal_grid_lines=fch.ChartGridLines(
                interval=WASH_IN_GRID_INTERVAL, color=GRIDLINE
            ),
            vertical_grid_lines=fch.ChartGridLines(
                interval=INITIAL_CHART_TIME_BASE.tick_interval_s, color=GRIDLINE
            ),
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

        # How fast the run is played. This is a *view* control and nothing
        # else: it decides how many steps a tick takes and never how large a
        # step is, so it reaches no model state and leaves identical inputs
        # producing an identical run (`app/playback.py`, and docs/MODEL.md
        # § "Interface boundary"). Two consequences follow from that and are
        # deliberate. It is never disabled - unlike the agent dropdown, which
        # is, because choosing an agent discards the case - since the reason
        # to reach for it is usually to slow a running case down and watch
        # something. And Reset leaves it alone, like every other user
        # setting: `SimulationController.reset` clears dynamic state and
        # preserves settings, and a rate silently snapping back to 1x would
        # be a mode change nobody asked for.
        self._playback_rate: PlaybackRate = DEFAULT_PLAYBACK_RATE
        # Rendered by the same function as the dropdown's own options, so the
        # rate the control reports and the rate the clock reports cannot
        # differ. It is drawn on the "Simulated time" panel rather than only
        # here beside the transport controls because a rate is a mode, and
        # the hazard is a clock read without it: `docs/MODEL.md` requires
        # the rate wherever simulated time is shown.
        self._playback_rate_text = self._build_metric_secondary_value(
            format_playback_rate(self._playback_rate.multiplier)
        )
        self._playback_rate_dropdown = ft.Dropdown(
            value=str(self._playback_rate.multiplier),
            options=[
                ft.dropdown.Option(
                    key=str(rate.multiplier), text=format_playback_rate(rate.multiplier)
                )
                for rate in SUPPORTED_PLAYBACK_RATES
            ],
            width=PLAYBACK_RATE_SELECTOR_WIDTH,
            filled=True,
            fill_color=PANEL,
            bgcolor=PANEL,
            color=INK,
            border_color=MUTED,
            focused_border_color=INK,
            label="Playback",
            on_select=self._handle_playback_rate_change,
        )

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
            width=AGENT_SELECTOR_WIDTH,
            filled=True,
            fill_color=initial_agent_colors.fill,
            bgcolor=initial_agent_colors.fill,
            color=initial_agent_colors.foreground,
            text_style=initial_agent_style.dropdown_text_style,
            border_color=initial_agent_colors.foreground,
            focused_border_color=initial_agent_colors.foreground,
            visible=not initial_snapshot.is_running,
            on_select=self._handle_agent_change,
        )

        # The running agent's identity, carried by a control that is never
        # disabled and so never recoloured by the theme. `RUNNING_AGENT_LOCK_TEXT`
        # records why this exists rather than a restyled dropdown.
        #
        # Bordered in the agent's own foreground for the reason
        # `_agent_header_badge` is: this row sits on BACKGROUND, and the
        # sevoflurane fill is 1.27:1 against it, so without an edge the
        # coloured region a reader is meant to recognise loses its shape.
        # Both strings take the agent's foreground, so the chip adds no pair
        # to `tools/contrast_check.py` that the selector did not already
        # declare - it is the same fill and the same text colour, now
        # actually rendered.
        self._running_agent_text = ft.Text(
            initial_snapshot.agent_display_name,
            color=initial_agent_colors.foreground,
            weight=ft.FontWeight.BOLD,
        )
        self._running_agent_lock_text = ft.Text(
            RUNNING_AGENT_LOCK_TEXT,
            color=initial_agent_colors.foreground,
            size=METRIC_QUALIFIER_SIZE,
        )
        self._running_agent_display = ft.Container(
            content=ft.Column(
                controls=[self._running_agent_text, self._running_agent_lock_text],
                spacing=0,
                tight=True,
            ),
            bgcolor=initial_agent_colors.fill,
            border=initial_agent_style.badge_border,
            border_radius=PANEL_RADIUS,
            padding=RUNNING_AGENT_DISPLAY_PADDING,
            width=AGENT_SELECTOR_WIDTH,
            visible=initial_snapshot.is_running,
        )

        self._subtitle_text = ft.Text(
            format_subtitle(initial_snapshot.agent_display_name),
            color=initial_agent_colors.foreground,
            weight=ft.FontWeight.BOLD,
        )
        # The badge is bordered in its own foreground color because the
        # sevoflurane fill is only 1.27:1 against the page it is drawn on:
        # without a border its edge effectively disappears, and the colored
        # region a reader is meant to recognize loses its shape. That border
        # is a channel `tools/contrast_check.py` measures rather than assumes -
        # the badge is declared there as fill *or* border and held to the
        # better of the two, which is what makes this one pass (PL-GNN1).
        self._agent_header_badge = ft.Container(
            content=self._subtitle_text,
            bgcolor=initial_agent_colors.fill,
            border=initial_agent_style.badge_border,
            border_radius=PANEL_RADIUS,
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

    def _plotted_series(self, substance_id: str) -> tuple[chart_series.PlottedSeries, ...]:
        """Every trace paired with the series it draws, hidden ones included.

        The whole trace-to-series pairing: an entry naming the wrong
        compartment - or, once a run records more than one substance, the
        wrong substance - would plot one set of values on another's line,
        which misstates the run as surely as a wrong number would. Nothing
        in the type system can catch that - `flet_charts` ships no stubs,
        so a chart series is `Any` to the checker - so
        `test_chart_traces_stay_bound_to_their_own_compartment` is what
        holds it, by giving each compartment a distinct multiple and
        reading the drawn points back.

        Hidden traces are included because what a trace *draws* does not
        change with whether it is currently on the chart.
        `_visible_plotted_series` is the frame's subset.

        Args:
            substance_id: The substance whose run this frame is drawing.
        """

        return tuple(trace.plotted(substance_id) for trace in self._compartment_traces)

    def _visible_plotted_series(self, substance_id: str) -> tuple[chart_series.PlottedSeries, ...]:
        """The pairing above, filtered to the traces the reader is looking at.

        The filter is over whole records, each carrying its own series and
        its own quantity, so it cannot misalign the pairing - see
        `_CompartmentTrace`.

        Args:
            substance_id: The substance whose run this frame is drawing.
        """

        return tuple(
            trace.plotted(substance_id) for trace in self._compartment_traces if trace.visible
        )

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
            self._mac_awake_band_upper_edge,
            self._mac_awake_band_lower_edge,
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
                                            size=APP_TITLE_SIZE,
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
                                        # Exactly one of these two is visible;
                                        # `_refresh_view` is the one writer of
                                        # which, from `is_running`.
                                        self._agent_dropdown,
                                        self._running_agent_display,
                                        self._start_button,
                                        self._pause_button,
                                        self._reset_button,
                                        self._playback_rate_dropdown,
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
                # "common gas outlet", never "Fresh gas flow" alone. The
                # phrase on its own is what an anesthesia machine's flowmeter
                # bank is labelled, and a flowmeter reads the carrier gas
                # only; the model's own mass balance forces this setting to
                # be the whole post-vaporizer stream, carrier plus the vapour
                # the vaporizer added, which `docs/MODEL.md` § "Breathing
                # circuit" states and derives. The two differ by
                # 1/(1 - F_D) - under a percent at ordinary dial settings,
                # 22% at desflurane's 18% Tec 6 maximum, where flowmeters at
                # 2 L/min leave the common gas outlet at about 2.44 L/min -
                # and the error lands on the circuit time constant
                # `V_C/V̇_F`, which is the quantity the wash-in curve is
                # about. Reading the slider as a flowmeter is therefore a
                # wrong clinical inference from a correct number, which
                # `CLAUDE.md` counts as a presentation-safety defect rather
                # than a wording preference (PL-71CF, after PL-CXYT). Do not
                # shorten it to fit a layout;
                # `test_the_fresh_gas_flow_control_names_the_common_gas_outlet`
                # holds the exact pair of strings.
                self._build_parameter_panel(
                    "Fresh gas flow",
                    self._fresh_gas_flow_slider,
                    self._fresh_gas_flow_text,
                    qualifier="common gas outlet",
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
        qualifier: str | None = None,
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
            qualifier: Where a setting's name alone would be read as a
                different quantity than the model uses, the words that
                separate the two, drawn smaller under the name as the
                clinical gloss is on a readout (`_build_metric_panel`), or
                None where the name is unambiguous. Unlike that gloss no
                spacer is drawn in its place, because these four panels
                are already of unequal height - the delivered agent
                carries a MAC line the three flow settings have no
                conversion for - so there is no shared baseline for a
                blank line to keep.

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
                    *(
                        []
                        if qualifier is None
                        else [
                            ft.Text(
                                qualifier, color=MUTED, size=PARAMETER_QUALIFIER_SIZE, italic=True
                            )
                        ]
                    ),
                    ft.Row(controls=[slider, value_text]),
                    *([] if secondary_value_text is None else [secondary_value_text]),
                ],
                spacing=4,
            ),
            bgcolor=PANEL,
            border_radius=PANEL_RADIUS,
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
                self._build_metric_panel(
                    "Simulated time",
                    None,
                    self._elapsed_time_text,
                    # The playback rate, in the slot the other six panels give
                    # to a MAC multiple. It is not a second unit for the value
                    # above it - simulated time has one unit and this is not
                    # another reading of it - but it is the one thing a reader
                    # needs in order to know what the clock beside it means,
                    # and this is where a reader of this row is already
                    # looking. Drawn at every rate including 1x, so that a
                    # blank line never has to be read as "real time".
                    self._playback_rate_text,
                ),
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
            border_radius=PANEL_RADIUS,
            padding=PANEL_PADDING,
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
                    # The panel's own heading row, with the time base beside
                    # it. The control sits at the top of the panel rather
                    # than under the four legend rows because it governs the
                    # axis the caption directly below it describes, and a
                    # reader looking for "how much of the run am I seeing"
                    # reads the caption first.
                    ft.Row(
                        controls=[
                            ft.Text(
                                ("Agent concentration and relative partial pressure over time"),
                                weight=ft.FontWeight.BOLD,
                                color=INK,
                            ),
                            self._time_base_dropdown,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        wrap=True,
                        spacing=8,
                        run_spacing=6,
                    ),
                    self._time_axis_caption,
                    # The divisor every MAC number on this page was produced
                    # with - "1 MAC sevoflurane = 2.0%" - which is the
                    # traceability `CLAUDE.md`'s clinical-output standard
                    # asks for, in the form it asks for it: a named value
                    # rather than an explanation of one.
                    #
                    # PL-DHV7 also required the convention in prose here -
                    # that a multiple on a non-alveolar compartment is a
                    # partial-pressure ratio and not a depth of anesthesia.
                    # PL-6580 removed that paragraph as tutorial for this
                    # audience and left the notation to carry it, which is
                    # what the axis title and the readouts' unit suffix are
                    # for. `docs/MODEL.md` "MAC multiples as a display unit"
                    # holds the full statement.
                    self._mac_reference_text,
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
                    # `_hidden_traces_text` names the compartments currently
                    # unchecked, which is what stops a hidden trace reading
                    # as a compartment the model does not have. It is state,
                    # and it stays.
                    #
                    # The paragraph above it until PL-6580 said that
                    # unchecking removes a trace from the plot only and
                    # leaves the run unchanged. Nothing was lost with it.
                    # The readouts above the chart go on showing that
                    # compartment's concentration while its curve is gone,
                    # which shows the reader the claim rather than asserting
                    # it - and `NO_TRACES_SHOWN_TEXT` states it in words at
                    # the one moment it is not self-evident, when every
                    # trace is off and the panel is blank. A standing
                    # paragraph was the same sentence charged to every
                    # reader on every frame.
                    self._hidden_traces_text,
                    self._off_scale_text,
                    # The references get their own legend row rather than
                    # joining the six above. They are not compartments, and a
                    # single row would invite reading them as a seventh and
                    # eighth trace - which is the misreading PL-F52R exists to
                    # prevent, arriving through the legend instead of the
                    # chart.
                    #
                    # Each entry names the compartment it is read against,
                    # which `docs/MODEL.md` "Interface boundary" requires of
                    # a reference in the same breath as it exempts one from
                    # the drawn-trace rule: a published constant may be
                    # drawn without a sample behind it, and it owes a reader
                    # the value, the divisor, and the curve to read it
                    # against in exchange. Both were in the prose PL-6580
                    # removed, so the labels carry them now. Not a
                    # restatement of the deleted paragraphs but the part of
                    # them that was a label all along - and the part with
                    # clinical consequence, since every way of pairing a
                    # reference with the wrong trace here shortens the
                    # apparent time to awakening.
                    ft.Row(
                        controls=[
                            ft.Text("Clinical references:", color=MUTED),
                            # Vessel-rich, not alveolar. The model has no
                            # effect-site compartment and defines the
                            # arterial fraction as the alveolar one, so the
                            # alveolar trace is the fastest curve on the
                            # chart and the furthest from where
                            # responsiveness returns; the stored fractions
                            # are slow-washout values, which Katoh measured
                            # against cerebral concentration.
                            self._build_band_legend_item(
                                "MAC-awake (population, ±1 SD; read against vessel-rich trace)",
                                MAC_AWAKE_BAND_COLOR,
                            ),
                            # Alveolar, because that is what MAC is defined
                            # for - the end-tidal concentration in a nominal
                            # 40-year-old - and the other five traces cross
                            # this line at a partial-pressure ratio rather
                            # than at a depth of anesthesia.
                            self._build_legend_item(
                                "1 MAC, reference adult (alveolar)", ONE_MAC_LINE_COLOR, "wide dash"
                            ),
                        ],
                        wrap=True,
                        spacing=16,
                        run_spacing=6,
                    ),
                    # The band's two free parameters, named: the published
                    # fraction and the divisor it was applied to, so a
                    # reader who disagrees with either can see which.
                    #
                    # The paragraph that stood beside it until PL-6580 gave
                    # the endpoint difference from MAC and the reason the
                    # band belongs against the vessel-rich trace. Both are
                    # in `docs/MODEL.md` "MAC-awake as a chart reference",
                    # and the endpoint is fundamental knowledge for this
                    # display's reader. The trace it is read against is not
                    # tutorial and did not go with it: `docs/MODEL.md`
                    # "Interface boundary" requires a reference to name the
                    # compartment it is read against, so that moved into the
                    # legend entry above, where a reader learns what a mark
                    # is. It is load-bearing rather than a caution - the
                    # alveolar trace crosses the band about 2.3x earlier
                    # than the vessel-rich one, so a band read against the
                    # wrong curve teaches an early wake-up.
                    self._mac_awake_reference_text,
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
                        ],
                        wrap=True,
                        spacing=8,
                        run_spacing=2,
                    ),
                    ft.Container(height=CHART_HEIGHT, content=self._concentration_chart),
                    ft.Divider(height=SECTION_DIVIDER_HEIGHT, color=GRIDLINE),
                    *self._build_wash_in_section(),
                ]
            ),
            bgcolor=PANEL,
            border_radius=PANEL_RADIUS,
            padding=PANEL_PADDING,
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
            self._wash_in_time_axis_caption,
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
            border_radius=PANEL_RADIUS,
            padding=PANEL_PADDING,
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
            border_radius=PANEL_RADIUS,
            padding=PANEL_PADDING,
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
                ft.Container(
                    width=CONTROL_MARK_SWATCH_WIDTH,
                    height=CONTROL_MARK_SWATCH_HEIGHT,
                    bgcolor=CONTROL_MARK_COLOR,
                ),
                ft.Text("Control change (vertical, fine dash)", color=INK),
            ],
            spacing=6,
            tight=True,
        )

    @staticmethod
    def _build_band_legend_item(label: str, color: str) -> ft.Row:
        """Build the legend entry for a reference band, drawn as a band.

        A filled swatch ruled on both edges rather than the 4px line every
        other entry uses. The mark type is what distinguishes a measured
        population value with real spread from a definitional anchor, so a
        legend that drew both as lines would lose the one channel carrying
        that distinction - and a swatch ruled on one edge only would teach
        the reader the wrong mark for the one on the chart, which is the
        same defect `PL-90Y6` fixed there.

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
                    width=BAND_SWATCH_WIDTH,
                    height=BAND_SWATCH_HEIGHT,
                    bgcolor=ft.Colors.with_opacity(MAC_AWAKE_BAND_FILL_OPACITY, color),
                    border=ft.Border(
                        top=ft.BorderSide(MAC_AWAKE_BAND_EDGE_STROKE_WIDTH, color),
                        bottom=ft.BorderSide(MAC_AWAKE_BAND_EDGE_STROKE_WIDTH, color),
                    ),
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
        # Disabled *and* hidden while the run is going, with
        # `_running_agent_display` in its place. `disabled` alone used to be
        # the whole of this and is what produced the grey-on-fill the chip
        # exists to prevent; it stays because a control that is off screen
        # must not be operable either, and because it is what a keyboard
        # user reaches the same way.
        self._agent_dropdown.disabled = snapshot.is_running
        self._agent_dropdown.visible = not snapshot.is_running
        self._running_agent_display.visible = snapshot.is_running
        self._running_agent_text.value = snapshot.agent_display_name

        self._delivered_concentration_slider.max = snapshot.max_delivered_concentration_percent
        self._delivered_concentration_slider.value = (
            snapshot.delivered_concentration_fraction * 100.0
        )
        # The ceiling and the rules move with the agent because both are
        # multiples of its 1 MAC - which is exactly what keeps the *scale*
        # still: 0 to 3 MAC, ruled every half MAC, whichever agent is
        # running. Set every frame like the slider above, because they are
        # cheap scalars; the axis labels below are not, and are guarded.
        self._concentration_chart.max_y = chart_axis_top_percent(snapshot.agent_mac_percent)
        self._concentration_chart.horizontal_grid_lines.interval = chart_grid_interval_percent(
            snapshot.agent_mac_percent
        )
        # The divisor is what every tick is placed against, so a MAC axis
        # carried over from the previous agent would label the same traces
        # against the wrong scale. Rebuilt only when it actually moves, for
        # the reason recorded at `_mac_axis_basis`.
        mac_axis_basis = snapshot.agent_mac_percent

        if mac_axis_basis != self._mac_axis_basis:
            self._mac_axis_basis = mac_axis_basis
            self._mac_axis.labels = self._build_mac_axis_labels(mac_axis_basis)

        self._mac_reference_text.value = format_mac_reference(
            snapshot.agent_display_name, snapshot.agent_mac_percent
        )
        self._mac_awake_reference_text.value = self._format_mac_awake_reference(snapshot)

        has_failed = snapshot.failure_reason is not None

        # Four states, not two. A stopped run must never render as a pause:
        # the numbers beside this word are a completed step's, but the run
        # cannot go on from them, and a reader who sees "Paused" expects
        # Start to resume it and reads a stopped trajectory as one still in
        # progress.
        #
        # The two stopped states are also not each other, which is why this
        # is four and not three. A failure says the model reached a state it
        # could not step from; the supported run length says it reached the
        # end of what it is claimed to represent, having done everything
        # right. WARNING is the failure's, deliberately not shared: colouring
        # a correct model's declared boundary as a fault teaches a reader to
        # distrust a number that is sound, and would spend the one signal
        # this interface has for a real one.
        if has_failed:
            self._status_text.value = "Stopped — simulation error"
            self._status_text.color = WARNING
        elif snapshot.supported_limit_reason is not None:
            self._status_text.value = "Stopped — supported run length reached"
            self._status_text.color = MUTED
        elif snapshot.is_running:
            self._status_text.value = "Running"
            self._status_text.color = ACCENT_TEXT
        else:
            self._status_text.value = "Paused"
            self._status_text.color = MUTED

        self._refresh_notice(snapshot.failure_reason, snapshot.supported_limit_reason)
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

        # Neither a failed run nor one standing at the supported run length
        # can be resumed — only reset — so Start must not invite it.
        # `is_running` alone would leave Start enabled for both, since each
        # is a stopped session; and a Start the controller would refuse is a
        # control presenting itself as working.
        self._start_button.disabled = (
            snapshot.is_running or has_failed or snapshot.supported_limit_reason is not None
        )
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

        # The visible window, and the two modes it can be in. "Fit run"
        # derives the width from the run so the whole of it is drawn, pinned
        # at zero; a chosen width is held exactly and follows the newest
        # sample, so a trace's slope on the plot means the same thing at
        # every moment of the run. `app/chart_time_base.py` carries both
        # rules and why they are not one.
        if self._time_base is None:
            time_base = fit_to_run(snapshot.elapsed_s)
            chart_min_x, chart_max_x = fitted_window(time_base)
        else:
            time_base = self._time_base
            chart_min_x, chart_max_x = following_window(time_base, snapshot.elapsed_s)

        self._concentration_chart.max_x = chart_max_x
        self._concentration_chart.min_x = chart_min_x
        self._apply_time_base(time_base, chart_min_x, chart_max_x)

        # The references span the same window as the traces and are moved in
        # the same frame, so a scroll can never leave one ruled across part of
        # the chart or drawn at the previous agent's height.
        mac_awake_lower_percent, mac_awake_upper_percent = self._mac_awake_band_percent(snapshot)
        chart_series.redraw_reference_band(
            self._mac_awake_band_upper_edge,
            self._mac_awake_band_lower_edge,
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
        # keeps the right-hand end of every trace the instant the readouts
        # above were formatted from - `RunScore.evaluate_anchored` always
        # draws the end of the range, so the two agree by construction
        # rather than by ordering. The window asked for is the axis just
        # set, clipped to the part of it the run covers (`PL-0VM7`).
        #
        # Read once and drawn twice: both plots span the same window, so one
        # read is what makes them the same *instants* and not merely the
        # same axis numbers.
        # Only the traces the reader has left shown. A hidden trace costs
        # nothing here and holds nothing on the client, because
        # `_chart_data_series` has taken it off the chart as well - the two
        # go together, and `chart_series.redraw_visible_window` says why
        # doing one without the other would leave a stale curve drawn.
        window = self._controller.drawn_window(
            chart_min_x, chart_max_x, chart_series.CHART_COLUMN_BUDGET_PER_SERIES
        )
        # Drawn under the agent this frame's readouts were formatted from,
        # so a run and the traces of it cannot come from different agents.
        # A snapshot naming an agent the window does not describe raises in
        # `DrawnWindow.compartment_fractions` rather than drawing whatever
        # the run does hold - see `RecordedSeries`.
        chart_series.redraw_visible_window(self._visible_plotted_series(snapshot.agent_id), window)

        # After the traces are drawn and before anything else reads them:
        # the notice is about the points this frame actually put on the
        # chart, so it is written from those rather than re-derived from
        # the snapshot, which would let the words and the picture disagree.
        self._refresh_off_scale_notice(snapshot)

        adjustments = group_adjustments(snapshot.control_timeline)
        self._redraw_control_marks(adjustments, chart_min_x, chart_max_x, snapshot)
        self._refresh_wash_in(snapshot, window, chart_min_x, chart_max_x)
        # Last, after every call above that can have appended a point: a
        # point built this frame carries no tooltip (`chart_series.build_point`),
        # so a run paused with a trace still growing would otherwise show a
        # hover that answered over part of a curve and not the rest.
        self._apply_chart_tooltips(enabled=not snapshot.is_running)
        self._refresh_control_timeline(adjustments)

    def _refresh_off_scale_notice(self, snapshot: SimulationSnapshot) -> None:
        """Say which drawn traces are above the top of the plot, if any.

        The axis is fixed at `CHART_AXIS_TOP_MAC`, so unlike the old
        dial-maximum ceiling it can be exceeded — and the setting that
        exceeds it, sevoflurane at 8%, is in common use rather than an
        accident. A clipped trace draws as a horizontal line at the
        ceiling, which is indistinguishable from a plateau, so leaving
        this unsaid would let a reader conclude the concentration stopped
        rising when the model says it did not.

        Read from the series' own points rather than from the snapshot.
        The snapshot carries only the newest sample, and a trace that rose
        above the axis earlier in the visible window is still drawn
        clipped now; the points are what the frame put on the chart.
        Hidden traces are skipped because a hidden series keeps the points
        of the frame it was last drawn in, which would otherwise report a
        compartment the reader is not looking at.

        Args:
            snapshot: The frame's state, for the agent's 1 MAC — the only
                thing the ceiling depends on.
        """

        top_percent = chart_axis_top_percent(snapshot.agent_mac_percent)
        # A trace is off scale only once it clears the ceiling by more than
        # the readouts can resolve. Below that the excursion is invisible in
        # every number on the display, and the comparison would instead be
        # reporting floating-point noise: isoflurane's ceiling is 3 x 1.2,
        # which is 3.5999999999999996 rather than 3.6.
        off_scale = [
            trace.label
            for trace in self._compartment_traces
            if trace.visible
            and any(
                point.y - top_percent > CONCENTRATION_DISPLAY_RESOLUTION_PERCENT
                for point in trace.series.points
            )
        ]

        self._off_scale_text.visible = bool(off_scale)
        self._off_scale_text.value = (
            OFF_SCALE_NOTICE_TEMPLATE.format(
                compartments=", ".join(off_scale),
                top=format_mac_multiple(top_percent / 100.0, snapshot.agent_mac_percent),
            )
            if off_scale
            else ""
        )

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

        Every mark spans the plotted range, which is `CHART_AXIS_TOP_MAC`
        multiples of the running agent's 1 MAC, so it is derived from the
        snapshot rather than read off the chart control: the two are set
        in the same frame and this way they cannot be read from different
        ones. A mark drawn to the old dial-maximum ceiling would now stand
        a third of a plot-height above the top of the frame.
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
            (self._control_mark_series, chart_axis_top_percent(snapshot.agent_mac_percent)),
            (self._wash_in_control_mark_series, WASH_IN_AXIS_MAXIMUM),
        ):
            for series, adjustment in zip(mark_series, drawn, strict=False):
                chart_series.redraw_control_mark(series, adjustment.started_at_s, top_y)

            for series in mark_series[len(drawn) :]:
                chart_series.park_control_mark(series)

    def _refresh_wash_in(
        self,
        snapshot: SimulationSnapshot,
        window: DrawnWindow,
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
            self._wash_in_segment_series, window, snapshot.agent_id, WASH_IN_TERMINUS_CEILING
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
        # A trace being shown again joins the chart *after* the redraw that
        # `_handle_trace_visibility_change` runs first, so the frame's own
        # tooltip pass never saw it. Re-applied here in the mode that frame
        # set, which is what stops a trace restored while paused being the
        # one curve on the chart that answers no hover.
        self._apply_chart_tooltips(enabled=self._chart_tooltips_enabled)

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

    def _apply_chart_tooltips(self, *, enabled: bool) -> None:
        """The one writer of whether either chart answers a hover.

        **The hover is offered while the run is paused and withdrawn while
        it plays**, which is a performance decision and a reading decision
        that happen to agree.

        The performance half. A tooltip is an object per point, and Flet's
        diff descends into it on every point on every frame - about half the
        cost of a frame, measured at 42.8 ms against 22.5 ms on a saturated
        chart at 300x (`PL-KP7H`, and `PL-YSZN` for where the rest of the
        frame goes). That bill is only presented while frames are being
        pushed: `_run_render_timer` takes no frame while the run is stopped,
        so a paused chart carrying tooltips costs nothing per second. The
        feature is therefore restored exactly where it is free.

        The reading half, which is why this is not merely an optimization
        dressed as a feature. A trace at 300x advances a simulated minute
        between frames, so a value read under a moving cursor is stale
        before it is read; and a drawn point is the run's state at that
        instant, which is a thing to study rather than to glance at.
        Pausing is what a reader does to inspect, and it is
        the state in which the number under the cursor still means what it
        said.

        What the tooltip *says* is `flet_charts`' default and was designed
        by nobody - `PL-YLKR` is the item for that, and it matters more now
        than it did, because this makes the tooltip a readout a reader
        deliberately stops to consult rather than one they brush past.

        `interactive` is the documented switch ("enables automatic tooltips
        and points highlighting when hovering over the chart") and is what
        makes the behaviour change in contract; the per-point write is what
        makes it cheap. Both are done here so the two cannot come to
        disagree - a chart left interactive over tooltipless points, or
        tooltips carried by points no hover can reach, are each half of this
        applied without the other.

        Args:
            enabled: Whether a hover should answer. Read from the frame's
                snapshot by `_refresh_view`, which is the only place the run
                state is consulted.
        """

        for chart in (self._concentration_chart, self._wash_in_chart):
            chart.interactive = enabled
            chart_series.apply_point_tooltips(chart.data_series, enabled=enabled)

        self._chart_tooltips_enabled = enabled

    def _apply_agent_color_scheme(self, agent_id: str) -> None:
        """Apply the verified agent color to every control that carries identity.

        Three of them: the header badge, the selector, and the chip that
        stands in the selector's place while a run is going. All three are
        written on every tick whether or not they are visible, so the one
        that becomes visible on the next state change is already correct -
        a chip revealed in the previous agent's colour would be the wrong
        label over the right numbers for as long as one frame.
        """

        scheme = AGENT_COLOR_SCHEMES[agent_id]
        style = AGENT_RENDER_STYLES[agent_id]
        self._agent_header_badge.bgcolor = scheme.fill
        self._agent_header_badge.border = style.badge_border
        self._subtitle_text.color = scheme.foreground

        self._running_agent_display.bgcolor = scheme.fill
        self._running_agent_display.border = style.badge_border
        self._running_agent_text.color = scheme.foreground
        self._running_agent_lock_text.color = scheme.foreground

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

    def _apply_setting(self, apply_setting: Callable[[], None], *, coalesce: bool = False) -> None:
        """Apply one user setting, reporting a refusal instead of losing it.

        A `SimulationConfigurationError` here means the core rejected the
        value and changed nothing, so the run is untouched and must not be
        marked failed. What must not happen is the raise escaping into
        Flet's event dispatch: the control would keep the refused value
        while the simulation kept running at the old one, which is the
        correct number under the wrong label that `CLAUDE.md` treats as a
        safety failure. `_refresh_view` restores the control from the
        snapshot, on the frame this draws or on the next tick.

        **`_refresh_view` is never what waits.** It runs on every call,
        coalesced or not, so the control objects always agree with the
        snapshot the moment a setting has been applied - which is the
        property `PL-018` established and the one a reader's dial position
        rests on. What waits is only `page.update()`, the submission of
        those objects to the client, and it is that which costs 23-59 ms on
        a saturated chart against this method's 3-4 ms (`PL-R2YM`,
        `PL-YSZN`). Deferring the cheap half as well would buy a further
        tenth of the drag and give up a stated invariant for it.

        **A refusal draws its own frame, whatever `coalesce` says**, and so
        does the call that clears one. A refusal is the one case where the
        control on screen and the simulation disagree - the reader dragged
        the dial somewhere the core would not go - so waiting even a tick
        would leave a dial stating a setting the run is not using, and
        leaving the notice up a tick after it stopped being true is the
        same fault backwards. An accepted setting with no notice on either
        side of it has nothing on screen to correct: the snapshot already
        says what the dial says.

        Args:
            apply_setting: The setter to run. Called once, and any
                `AnesthesiaSimulationError` it raises is reported rather
                than propagated.
            coalesce: Whether this call may leave its frame to the next
                render tick. True for the parameter sliders, which report
                continuously while dragged; false for every discrete
                action, where one action is one frame and a tick of delay
                would read as lag.
        """

        settled_notice = self._rejected_setting_notice

        try:
            apply_setting()
        except AnesthesiaSimulationError as error:
            self._rejected_setting_notice = f"Setting refused — {error}"
        else:
            self._rejected_setting_notice = None

        self._refresh_view()

        if coalesce and settled_notice is None and self._rejected_setting_notice is None:
            self._render_pending = True
            return

        self._page.update()

    def _refresh_notice(
        self, failure_reason: str | None, supported_limit_reason: str | None
    ) -> None:
        """Show a stopped-run banner, or a refused setting, or nothing.

        A stopped run outranks a refused setting: it describes the state of
        everything else on screen, where a refusal describes only one
        control. A failure outranks the supported run length in turn, on the
        same reasoning - the two cannot both arise from one run, and where a
        failure is somehow recorded it is the more serious statement.

        The stopped-run wording says what the values *are* rather than
        warning about them, which is what rolling the failed step back
        bought. The core leaves the last completed step, so the numbers are
        a real solution of the model at a real simulation time; what the
        reader needs to know is that they have stopped advancing and that
        the run cannot be resumed, not that they are untrustworthy.

        **The run-length wording does not borrow the failure's**, and the
        difference is required rather than stylistic. Nothing failed and
        nothing was rolled back: the step was refused before it began, and
        the values on screen are the model's last supported state. Saying
        "the step that failed was rolled back" there would describe an event
        that did not happen, and describe a correct model as a broken one -
        which `CLAUDE.md`'s standard treats as a safety defect, since a
        reader who distrusts a sound number is misled exactly as a reader who
        trusts an unsound one is. It says why the limit exists, because a
        boundary with no reason reads as an arbitrary restriction rather than
        as the edge of what the model represents.
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

        if supported_limit_reason is not None:
            self._notice_text.value = (
                "Simulation stopped — this run reached the supported run "
                f"length of {format_supported_run_length()}. Beyond it this "
                "model's omitted metabolism and its fat perfusion dominate "
                "the trace, so it is not claimed to represent a patient. "
                "The values shown are the last completed step, inside the "
                "supported span. Reset to start a new run."
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

    def _handle_playback_rate_change(self, event: ft.Event[ft.Dropdown]) -> None:
        """Play the run at the selected multiple of real time.

        Nothing here touches the simulation. The rate is read on the next
        tick as a number of steps, so a change takes effect without the loop
        being restarted, without a step being resized, and without a step in
        progress being interrupted - the run continues from exactly the step
        it had reached, at exactly the step size it has been taking.

        Changing it mid-run is the expected use rather than an edge case: a
        reader plays the uptake phase fast and drops back to real time to
        watch a control change take effect. Because the rate never reaches
        the model, a run played at three rates is the same run as one played
        at one, sample for sample.
        """

        if event.control.value is None:
            return

        # `playback_rate_for` raises on a multiplier the interface does not
        # offer rather than defaulting to one, and the raise is deliberately
        # not caught here: a value arriving from this dropdown that is not in
        # `SUPPORTED_PLAYBACK_RATES` means the control and that list have
        # diverged, which is a defect to surface. It cannot be a user error -
        # the options are the list.
        self._playback_rate = playback_rate_for(int(event.control.value))
        self._playback_rate_text.value = format_playback_rate(self._playback_rate.multiplier)
        self._refresh_and_render()

    def _handle_agent_change(self, event: ft.Event[ft.Dropdown]) -> None:
        """Treat a new selection as a request to start a new case.

        Nothing here rebuilds simulation state. Choosing an agent used to
        call `SimulationController.set_agent` straight from the dropdown,
        which always begins a new run: a control that reads as "show me this
        agent" discarded the case, its chart history and its recorded inputs,
        with no statement that it had happened and nothing to undo it with.
        What a selection does now depends on what there is to lose, and the
        three outcomes are deliberately different:

        - the agent already running, which a dropdown opened and closed on
          the same option reports as a selection: nothing at all, and no
          dialog either, since there is no new case to offer;
        - a run holding nothing recorded, which both a fresh session and
          Reset leave: the new case starts at once, because a confirmation
          that fires when nothing is at stake is the one nobody reads when
          something is;
        - anything else: `_confirm_new_case`, and no state rebuilt until it
          is answered.
        """

        if event.control.value is None:
            return

        agent_id = event.control.value
        snapshot = self._controller.snapshot()

        if agent_id == snapshot.agent_id:
            return

        if not snapshot.has_recorded_run:
            self._start_new_case(agent_id)
            return

        self._confirm_new_case(snapshot, agent_id)

    def _start_new_case(self, agent_id: str) -> None:
        """Rebuild the simulation around a different agent.

        Through `_apply_setting` like every other forwarded setting: the core
        can refuse the agent - a data file that will not load is the case that
        matters - and a raise escaping into Flet's event dispatch would leave
        the dropdown reading one agent while the run continued under another.
        """

        self._apply_setting(lambda: self._controller.set_agent(agent_id))

    def _confirm_new_case(self, snapshot: SimulationSnapshot, agent_id: str) -> None:
        """Ask, before a recorded run and its history are discarded.

        The selection is put back to the running agent *as the dialog opens*
        rather than when it is answered. A dropdown reading "Desflurane" over
        a header badge, a delivered-agent label, a MAC divisor and six
        readouts that are all still sevoflurane is the correct number under
        the wrong label `CLAUDE.md` treats as a safety failure, and it would
        stand for as long as the reader takes to decide. Nothing is lost by
        reverting it: the agent being offered is named in the dialog's title
        and in the button that accepts it, which is where a reader deciding
        this will be looking.
        """

        self._pending_agent_id = agent_id
        self._agent_dropdown.value = snapshot.agent_id
        self._new_case_dialog = self._build_new_case_dialog(snapshot, agent_id)
        self._page.show_dialog(self._new_case_dialog)
        self._page.update()

    def _build_new_case_dialog(self, snapshot: SimulationSnapshot, agent_id: str) -> ft.AlertDialog:
        """Build the confirmation for one proposed new case.

        Built per request rather than held and re-shown. `Page.show_dialog`
        raises on a dialog still in its stack, and a dialog leaves that stack
        only when the client reports its dismissal, so a held instance would
        make a destructive confirmation depend on a callback that may not have
        arrived - and the failure mode is a raise out of the dropdown's own
        event handler. One control tree per user gesture is the cost.

        `bgcolor` is set rather than left to the Flet theme so that the three
        text colours stand on the surface `tools/contrast_check.py` measures
        them against. A dialog painted in a theme surface would put INK,
        WARNING and MUTED on a background no declared requirement covers.

        `modal=True` so the run's controls cannot be reached around it: a
        reader who starts the run while being asked whether to discard it
        would answer the question about a different run from the one it
        describes.
        """

        current_agent = snapshot.agent_display_name
        new_agent = AGENT_DISPLAY_NAMES[agent_id]

        return ft.AlertDialog(
            modal=True,
            bgcolor=PANEL,
            title=ft.Text(
                NEW_CASE_TITLE_TEMPLATE.format(agent=new_agent.lower()),
                color=INK,
                weight=ft.FontWeight.BOLD,
            ),
            content=ft.Column(
                [
                    ft.Text(NEW_CASE_IS_NOT_A_VIEW_TEXT, color=INK),
                    ft.Text(
                        format_case_discard_warning(
                            current_agent,
                            snapshot.elapsed_s,
                            len(group_adjustments(snapshot.control_timeline)),
                        ),
                        color=WARNING,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        NEW_CASE_CARRYOVER_TEMPLATE.format(agent=new_agent.lower()), color=MUTED
                    ),
                ],
                tight=True,
                spacing=NEW_CASE_DIALOG_SPACING,
                width=NEW_CASE_DIALOG_WIDTH,
            ),
            # Destructive first, safe last: the trailing action is the one a
            # dialog's default press lands on, and it is the one that keeps
            # the case. It is also the only filled button on screen -
            # `ft.FilledButton` rather than the `ft.Button` the transport
            # controls use, which this theme draws as a pale tonal fill that
            # reads *quieter* than an outline. A safe default that looks like
            # the secondary choice is the arrangement's whole point undone.
            # See the button templates for the rest of the judgment.
            actions=[
                ft.OutlinedButton(
                    content=START_NEW_CASE_TEMPLATE.format(agent=new_agent.lower()),
                    on_click=self._handle_new_case_confirmed,
                ),
                ft.FilledButton(
                    content=KEEP_CURRENT_CASE_TEMPLATE.format(agent=current_agent.lower()),
                    on_click=self._handle_new_case_declined,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=self._handle_new_case_dismissed,
        )

    def _handle_new_case_confirmed(self, event: ft.Event[ft.OutlinedButton]) -> None:
        del event
        self._resolve_new_case(confirmed=True)

    def _handle_new_case_declined(self, event: ft.Event[ft.Button]) -> None:
        del event
        self._resolve_new_case(confirmed=False)

    def _handle_new_case_dismissed(self, event: ft.Event[ft.DialogControl]) -> None:
        """Treat any other way out of the dialog as declining.

        A dialog closed by anything but its two buttons - the escape key, the
        client tearing it down - has been answered by someone who chose
        nothing, and the only reading of that which cannot destroy a run is
        that the case stands.
        """

        del event
        self._resolve_new_case(confirmed=False)

    def _resolve_new_case(self, confirmed: bool) -> None:
        """Answer the open confirmation once, whichever way it was answered.

        Every route out of the dialog arrives here - either button, and the
        dismissal Flet reports afterwards - so the pending selection is
        cleared before anything acts on it and a second arrival finds nothing
        to do. Without that, the dismissal following a confirmed switch would
        run the declining branch over the case that had just started and put
        the dropdown back to the agent it had just replaced.
        """

        agent_id = self._pending_agent_id
        self._pending_agent_id = None

        if agent_id is None:
            return

        self._new_case_dialog = None
        self._page.pop_dialog()

        if confirmed:
            self._start_new_case(agent_id)
            return

        # Declining rebuilds nothing. The dropdown was put back when the
        # dialog opened; this is the frame that shows it, and the run, the
        # history and the timeline are as they were.
        self._refresh_and_render()

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
        self._apply_setting(
            lambda: self._controller.set_fresh_gas_flow(fresh_gas_flow_l_min), coalesce=True
        )

    def _handle_delivered_concentration_change(self, event: ft.Event[ft.Slider]) -> None:
        if event.control.value is None:
            return

        delivered_concentration_fraction = float(event.control.value) / 100.0
        self._apply_setting(
            lambda: self._controller.set_delivered_concentration(delivered_concentration_fraction),
            coalesce=True,
        )

    def _handle_alveolar_ventilation_change(self, event: ft.Event[ft.Slider]) -> None:
        if event.control.value is None:
            return

        alveolar_ventilation_l_min = float(event.control.value)
        self._apply_setting(
            lambda: self._controller.set_alveolar_ventilation(alveolar_ventilation_l_min),
            coalesce=True,
        )

    def _handle_cardiac_output_change(self, event: ft.Event[ft.Slider]) -> None:
        if event.control.value is None:
            return

        cardiac_output_l_min = float(event.control.value)
        self._apply_setting(
            lambda: self._controller.set_cardiac_output(cardiac_output_l_min), coalesce=True
        )

    def _halt_run(self, error: Exception) -> None:
        """Stop the run and say on screen why it stopped.

        The type still does not decide **whether** to stop - every exception
        stops the run, because a `TypeError` from a future refactor kills the
        loop exactly as silently as a modelling failure does, and both leave
        a display that would otherwise keep reading "Running" over numbers
        that stopped advancing.

        It decides **what the reader is told**, for exactly one type.
        `SimulationDomainLimitError` is the run reaching the end of the
        supported domain: the core refused the next step before taking it,
        nothing was miscalculated, and nothing was rolled back. Reporting it
        through `fail` would put "simulation error" over a correct model that
        stopped where `docs/MODEL.md` says it must, which is a misreading in
        the direction this interface can least afford - it spends the signal
        reserved for a real fault and teaches a reader to discount it.

        Everything else, known or not, is a failure. That asymmetry is
        deliberate: the narrow case is the one named, so an unrecognised
        exception falls through to the more cautious of the two.
        """

        if isinstance(error, SimulationDomainLimitError):
            self._controller.halt_at_supported_limit(str(error))
        else:
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
        """Advance the running simulation by the playback rate's steps per tick.

        Stepping is deliberately separate from drawing, and how many steps a
        tick takes is *the reader's setting* rather than a function of how
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

        The playback rate does not weaken that guarantee, because it changes
        only how many steps a tick takes. Every step is
        `SIMULATION_STEP_S`, at every rate: a rate that resized the step
        would make the same case read differently depending on how fast it
        was watched, which is a determinism failure regardless of the solver
        (`PL-SN2C`). So a run played at 60x that nobody touches records the
        history a run played at 1x records, element for element, and reaches
        it sixty times sooner in real time.

        **The qualification in that sentence is load-bearing and was absent
        until `PL-NBWP`.** The burst below has no `await` in it and Flet
        dispatches a sync handler inline on this loop, so no control event
        can land between two steps of a tick: simulated time stands still
        for one tick interval and then jumps by the whole burst. A setting
        changed while the run plays therefore first acts at a tick boundary,
        and the same case run at two rates with the same slider moves does
        *not* record the same history, because the moves land on grids
        `multiplier x SIMULATION_TICK_INTERVAL_S` apart. `app/playback.py`
        states the grid and the pause-change-resume route that is exact at
        every rate; `docs/MODEL.md` § "Supported simulation step" measures
        what one grid step costs a displayed compartment.

        Servicing events inside the burst was considered and rejected there
        rather than deferred: a step costs about 33 us, so even 300 of them
        occupy under a tenth of the tick and most control events already
        arrive while simulated time is standing still. Yielding would move
        no bound and would make *which* step a change lands on a function of
        the host's scheduler, which is the one thing the paragraph above
        promises it is not.

        The rate is read once per tick rather than held, so a change takes
        effect on the next wakeup and never part-way through a burst: a tick
        is all-or-nothing at one rate, which keeps the number of steps a
        tick took a fact about that tick rather than about when the dropdown
        happened to be opened.

        The loop survives a failed step rather than returning: the task is
        started once, at mount, so a loop that exits could never be
        restarted and Reset would leave the interface permanently dead.
        Halting clears `is_running`, so the loop idles until the user
        starts a fresh run. A step that raises part-way through a burst
        abandons the rest of it, which is the same rule one step per tick
        already followed - `AgentUptakeSystem.advance` rolls the failed step
        back, so the run stops on the last completed step and the steps that
        would have followed it in this tick are never taken.
        """

        while True:
            await asyncio.sleep(SIMULATION_TICK_INTERVAL_S)

            if not self._controller.is_running:
                continue

            steps = self._playback_rate.steps_per_tick(
                tick_interval_s=SIMULATION_TICK_INTERVAL_S, simulation_step_s=SIMULATION_STEP_S
            )

            try:
                for _ in range(steps):
                    self._controller.advance(SIMULATION_STEP_S)
            except Exception as error:  # broad by design - see _halt_run
                self._halt_run(error)

    async def _run_render_timer(self) -> None:
        """Redraw the running simulation on its own, slower cadence.

        Drawing no longer gates stepping, and the interval can be tuned for
        the display without changing the simulation. A discrete user action
        still redraws immediately rather than waiting for this tick, so a
        button or a dropdown never appears unresponsive.

        **A dragged slider is the exception, and it buys responsiveness
        rather than spending it** (`PL-R2YM`). A slider reports continuously
        while it is dragged, and each report used to draw a whole frame:
        Flet's diff walks the entire control tree whether or not anything in
        it moved, so one `on_change` cost 23-59 ms on a saturated chart and
        a drag emitting thirty a second asked for more event-loop time than
        a second contains. The loop could not deliver that, so the readouts
        arrived *later* than a tick, not sooner - the immediacy was claimed
        rather than achieved. Coalescing them onto this tick bounds the
        delay at `RENDER_INTERVAL_S` instead, which is the cadence every
        other readout on the dashboard already moves at.

        So this tick fires while the run is stopped as well, whenever a
        setting change is owed a frame. That is what makes the bound hold
        for a reader using the pause-change-resume route `app/playback.py`
        documents: paused, there is no run to draw, but there is still a
        dial moving and readouts that have to follow it.

        `_render_pending` is cleared before the frame rather than after, so
        a frame that raises does not also swallow the change that asked for
        it - `_halt_run` stops the run and draws what it can, and the next
        tick has no stale claim to act on.

        Guarded for the mirror-image reason the simulation loop is: a dead
        render loop leaves a frozen display over a simulation that is still
        advancing, so the values on screen silently stop being current.
        """

        while True:
            await asyncio.sleep(RENDER_INTERVAL_S)

            if not self._controller.is_running and not self._render_pending:
                continue

            self._render_pending = False

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

        return ft.Text(initial_value, size=METRIC_VALUE_SIZE, weight=ft.FontWeight.BOLD, color=INK)

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
    def _build_time_axis() -> fch.ChartAxis:
        """Build one chart's simulated-time axis.

        Labels, and whether the window's own ends are labelled, are filled
        in per frame by `_apply_time_base` - unlike the MAC axis, which can
        settle `show_min` and `show_max` once because the ends of its range
        are never ticks. Here it depends on the mode, so it is decided per
        frame rather than here.

        Returns:
            An axis with no labels yet.
        """

        return fch.ChartAxis(
            title=ft.Text("simulated time", color=MUTED, size=METRIC_QUALIFIER_SIZE)
        )

    def _time_axis_caption_text(self) -> str:
        """State the span of run the compartment chart is showing.

        The span, not only the unit. `PL-012` required the caption to name
        the span actually drawn because the width is a mode: the same plot
        showing fifteen minutes and twelve hours is two very different
        claims about what a flat trace means, and a reader who does not know
        which cannot tell a compartment at equilibrium from one that has not
        started moving yet.

        Under "Fit run" it says both - that the whole run is drawn, and how
        wide the plot had to be to draw it - because the width is then
        derived from the run rather than chosen, and the reader has nothing
        else on the display that says what it came out as. The selector
        beside it names the *rule*; this names what the rule came out as,
        which is why the caption is not redundant with it and does not
        appear only under one of the two modes.

        The span is all that is left of it. Until PL-6580 the line opened
        with a key naming all three axes and their units, each of which the
        axis's own title already carried, so the key restated on every frame
        what the chart states permanently. What no axis title can carry is
        which slice of the run is under it, because that changes with the
        mode and with the run's own length; that is this line's whole job
        now. `docs/MODEL.md` § "The chart's time base" is the requirement it
        answers.

        Returns:
            The caption line: the width in force, and whether the reader
            chose it or the run did.
        """

        span = format_time_base(self._drawn_time_base.span_s)

        return f"whole run so far, {span} shown" if self._time_base is None else f"{span} shown"

    @staticmethod
    def _build_time_axis_labels(ticks: tuple[float, ...]) -> list[fch.ChartAxisLabel]:
        """Build the simulated-time axis labels for one window.

        The placement is `chart_time_base.tick_times` and the wording is
        `formatting.format_chart_time_label`, both Flet-free and tested on
        their own; this only wraps each tick in the control the chart draws
        it with.

        Args:
            ticks: Tick positions, in simulated seconds.

        Returns:
            One axis label per tick.
        """

        return [
            fch.ChartAxisLabel(
                value=tick,
                label=ft.Text(
                    format_chart_time_label(tick), color=MUTED, size=METRIC_QUALIFIER_SIZE
                ),
            )
            for tick in ticks
        ]

    def _apply_time_base(
        self, time_base: ChartTimeBase, chart_min_x: float, chart_max_x: float
    ) -> None:
        """Rule and label both charts for the window this frame draws.

        The gridline interval is derived from the width and never fixed
        (`PL-012`): the 60 s interval this replaced would rule a twelve-hour
        axis into 720 lines and a solid block. Set every frame like the
        other cheap scalars.

        The labels are not cheap, and are guarded the way the MAC axis's
        are. Ticks stand at absolute multiples of the interval, so while the
        window follows the run the set only changes as an edge crosses one -
        every `tick_interval_s` of simulated time rather than every frame.
        Rebuilding them unguarded would allocate a control per tick per
        frame and send the client an add-and-remove of both axes each time,
        which is the per-frame churn `tests/integration/test_chart_patching.py`
        measures.

        Args:
            time_base: The width this frame is drawing at.
            chart_min_x: Left edge of the window, in simulated seconds.
            chart_max_x: Right edge of the window, in simulated seconds.
        """

        self._concentration_chart.vertical_grid_lines.interval = time_base.tick_interval_s
        self._wash_in_chart.vertical_grid_lines.interval = time_base.tick_interval_s

        ticks = tick_times(chart_min_x, chart_max_x, time_base.tick_interval_s)

        # Whether the window's own ends carry a label, which depends on the
        # mode. "Fit run" pins the window to zero and to a whole number of
        # intervals, so both ends are ruled and both deserve one - the
        # origin most of all, since it is where the run starts and the only
        # label that says so. A following window's ends fall wherever the
        # newest sample puts them, and a label there would read as a
        # gridline standing at a time nothing is ruled at. Set every frame,
        # because one selection changes it.
        starts_on_a_tick = bool(ticks) and ticks[0] == chart_min_x
        ends_on_a_tick = bool(ticks) and ticks[-1] == chart_max_x

        for axis in (self._time_axis, self._wash_in_time_axis):
            axis.show_min = starts_on_a_tick
            axis.show_max = ends_on_a_tick

        if ticks != self._drawn_tick_times:
            self._drawn_tick_times = ticks
            # Two label lists, not one shared between the axes: a Flet
            # control belongs to one chart, so the wash-in axis needs its
            # own copies of the same ticks.
            self._time_axis.labels = self._build_time_axis_labels(ticks)
            self._time_axis.label_spacing = time_base.tick_interval_s
            self._wash_in_time_axis.labels = self._build_time_axis_labels(ticks)
            self._wash_in_time_axis.label_spacing = time_base.tick_interval_s

        if time_base != self._drawn_time_base:
            self._drawn_time_base = time_base
            self._time_axis_caption.value = self._time_axis_caption_text()

    def _handle_time_base_change(self, event: ft.Event[ft.Dropdown]) -> None:
        """Draw the run against the width the reader selected.

        Nothing here touches the simulation. The time base decides which
        part of the recorded history the next frame draws and how wide the
        axis is; no sample is discarded, no step is resized, and the run
        continues from exactly the step it had reached. A case watched at
        fifteen minutes and the same case watched at twelve hours are the
        same run, sample for sample.

        Args:
            event: The dropdown selection, keyed by span in seconds or by
                `FIT_RUN_KEY`.
        """

        if event.control.value is None:
            return

        # `time_base_for_span` raises on a width the ladder does not carry
        # rather than falling back to a nearby one, and the raise is
        # deliberately not caught: a value arriving from this dropdown that
        # is not on `TIME_BASE_LADDER` means the control and that ladder have
        # diverged, which is a defect to surface. It cannot be a user error -
        # the options are the ladder.
        self._time_base = (
            None
            if event.control.value == FIT_RUN_KEY
            else time_base_for_span(float(event.control.value))
        )
        # The caption states the mode as well as the span, so it is rewritten
        # here as well as in `_apply_time_base`: switching between "Fit run"
        # and a width of the same span changes what the caption claims
        # without changing the width it names.
        self._time_axis_caption.value = self._time_axis_caption_text()
        self._refresh_and_render()

    @staticmethod
    def _build_mac_axis_labels(mac_percent: float) -> list[fch.ChartAxisLabel]:
        """Build the chart's MAC axis labels for one agent.

        The placement is `formatting.mac_axis_ticks`, which is Flet-free
        and tested on its own; this only wraps each tick in the control
        the chart draws it with.

        The range is derived here rather than passed in, from the same
        `chart_axis_top_percent` the chart's own ceiling is set from, so
        the ticks cannot be placed against a range the plot is not drawn
        at. Before PL-CC23 the two arrived as separate arguments and the
        top was the agent's dial maximum, which is what made the ruler
        agent-specific.

        Args:
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
            for percent, label in mac_axis_ticks(chart_axis_top_percent(mac_percent), mac_percent)
        ]
