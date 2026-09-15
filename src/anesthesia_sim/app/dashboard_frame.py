"""What the dashboard claims about one run at one instant, with no toolkit loaded.

The counterpart of `chart_frame.py` for everything beside the plots: the
status word, the notice banner, the seven readouts, the four setting
controls, the transport enablement, the agent-accounting panel, the
control-change list, the chart captions and the new-case question. Each is a
pure function of a `SimulationSnapshot` (or of the `ChartFrame` the same tick
assembled), so every string a reader sees and every precedence rule that
chooses between two of them is readable and testable without a display.
`tests/unit/test_dashboard_frame.py` holds it that way; the PySide6 widgets
in `qt_widgets.py`, `run_view.py` and `simulation_view.py` call these per
tick and decide nothing (`PL-25KS`, decision D2).

Every displayed number passes through `app/formatting.py`. This module
composes strings and settles enablement, precedence and layout arithmetic;
it formats nothing itself, so no resolution is spelled here and a change to
a displayed resolution reaches this module without an edit.

The strings are the Flet dashboard's, verbatim. Parity with that build is
the port's definition of done, and three of the strings are safety
requirements rather than wording: the "Alveolar" readout glossed
"end-tidal-equivalent" (`PL-NV9W`), the "Circuit" readout glossed "inspired"
(`PL-8M05`) and the "Fresh gas flow" control glossed "common gas outlet"
(`PL-71CF`), each stated in `docs/MODEL.md` and held by an exact-string test.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from anesthesia_sim.app.chart_frame import ChartFrame, trace_style
from anesthesia_sim.app.chart_time_base import TIME_BASE_LADDER
from anesthesia_sim.app.control_timeline import ControlAdjustment, format_adjustment
from anesthesia_sim.app.controller import ControlInput, RecordedQuantity, SimulationSnapshot
from anesthesia_sim.app.formatting import (
    CONCENTRATION_DISPLAY_DECIMALS,
    CONCENTRATION_DISPLAY_RESOLUTION_PERCENT,
    FLOW_DISPLAY_DECIMALS,
    format_agent_residual,
    format_agent_volume,
    format_case_discard_warning,
    format_delivered_label,
    format_elapsed,
    format_flow,
    format_mac_awake_reference,
    format_mac_multiple,
    format_mac_reference,
    format_percent,
    format_playback_rate,
    format_supported_run_length,
    format_time_base,
    format_wash_in_ratio,
)
from anesthesia_sim.app.playback import SUPPORTED_PLAYBACK_RATES, PlaybackRate
from anesthesia_sim.app.wash_in import WashInDomain, read_wash_in
from anesthesia_sim.core.concentration import (
    Fraction,
    Percent,
    fraction_from_percent,
    percent_from_fraction,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError, SimulationDomainLimitError
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MINIMUM_CARDIAC_OUTPUT_L_MIN,
    MINIMUM_FRESH_GAS_FLOW_L_MIN,
)

# The step each simulation tick advances by. What range of steps is
# *supported* is `core/`'s to declare: `core.uptake_system.MAXIMUM_SIMULATION_STEP_S`
# is that declaration, and a step above it is refused there rather than
# displayed here. This is a cadence choice inside that range, at its ceiling
# deliberately: running finer buys nothing a reader could see (halving the
# step moves a displayed fraction by around 1e-16), and running coarser
# costs control resolution. The two coinciding is a fact about this
# configuration rather than an identity, so they are named apart and
# `test_the_shipped_step_is_within_the_maximum_simulation_step` holds the
# relation; `docs/MODEL.md` § "Supported simulation step" and § "Displayed
# precision" carry the two derivations separately (`PL-X9KD`).
SIMULATION_STEP_S: Final = 0.1
# How often the simulation timer fires, in *real* seconds. Numerically equal
# to the step and conceptually unrelated to it: the playback multiplier is
# the ratio between them - a tick advances `rate.steps_per_tick(...)` steps of
# `SIMULATION_STEP_S`, which is `multiplier` times faster than real time only
# because a tick is one step long (`app/playback.py`,
# `test_a_tick_is_one_simulation_step_of_real_time`). It is also the
# interface's control resolution (`PL-NBWP`): a tick advances its whole burst
# uninterrupted, so a setting changed while the run plays first acts at a
# tick boundary, `multiplier` times this interval apart.
SIMULATION_TICK_INTERVAL_S: Final = SIMULATION_STEP_S
# Render cadence, independent of the simulation step. Twice the tick, so a
# frame is two control-grid steps at every playback rate - which is why
# `PL-NBWP` left the grid where it is. Written as its own number rather than
# derived, because a display cadence and a timer cadence are separate
# decisions; `test_a_frame_is_two_control_grid_steps_at_every_rate` holds the
# relation instead.
RENDER_INTERVAL_S: Final = 0.2
# How wide the chart is before the first frame runs: the narrowest rung,
# which is what "Fit run" answers with on a run that has recorded nothing.
INITIAL_CHART_TIME_BASE: Final = TIME_BASE_LADDER[0]

# How many runs the dashboard may draw at once. Two, because that is what
# `ROADMAP.md` § "v0.5.0 - the case you can branch" puts in its own
# out-of-scope list, and because the encoding that tells one run from another
# is two-level (`PL-HLD5`: the run on line width, under a cap of two
# compartments). A third run would have nothing left to be drawn with.
MAX_DISPLAYED_RUNS: Final = 2

# A readout with no gloss still draws the gloss line, so every reading in the
# row sits on one baseline (`PL-8M05`). A non-breaking space rather than an
# empty string: the Flet build needed it because a blank collapsed to zero
# height there, and it is kept because `tools/glyph_check.py` names these
# two constants as the evidence for U+00A0 and a test asserts the line holds
# a value.
EMPTY_METRIC_QUALIFIER: Final = " "
# The same spacer for the second-unit line, so the "Simulated time" panel -
# which has no MAC multiple - is the height of the six that do.
EMPTY_METRIC_SECONDARY_VALUE: Final = " "

# The delivered-concentration dial's floor, in percent. Its maximum is
# agent-specific (the real vaporizer's capability) and comes from
# `SimulationSnapshot.max_delivered_concentration_percent` rather than from a
# constant; the floor is here because it is a percent where the core's own
# guard is a fraction. The three flow ranges are `core/supported_ranges.py`'s
# and are imported, never restated (`PL-0MLQ`).
MIN_DELIVERED_CONCENTRATION_PERCENT: Final = 0.0

# The four status words. Four states, not two: a stopped run must never
# render as a pause, and the two stopped states are not each other. A
# failure says the model reached a state it could not step from; the
# supported run length says it reached the end of what it is claimed to
# represent, having done everything right.
STATUS_PAUSED_TEXT: Final = "Paused"
STATUS_RUNNING_TEXT: Final = "Running"
STATUS_FAILED_TEXT: Final = "Stopped — simulation error"
STATUS_SUPPORTED_LIMIT_TEXT: Final = "Stopped — supported run length reached"

# The three notice banners, in precedence order. The stopped-run wording says
# what the values *are* rather than warning about them, which is what rolling
# the failed step back bought (`PL-026`). The run-length wording does not
# borrow the failure's: nothing failed and nothing was rolled back, and
# describing a correct model as a broken one is the safety defect `CLAUDE.md`
# names (`PL-Y5WR`). It says why the limit exists, because a boundary with no
# reason reads as an arbitrary restriction.
FAILURE_NOTICE_TEMPLATE: Final = (
    "Simulation stopped — {failure_reason}. The values shown are the last completed "
    "step; the step that failed was rolled back and changed nothing. "
    "Reset to start a new run."
)
SUPPORTED_LIMIT_NOTICE_TEMPLATE: Final = (
    "Simulation stopped — this run reached the supported run length of {run_length}. "
    "Beyond it this model's omitted metabolism and its fat perfusion dominate the "
    "trace, so it is not claimed to represent a patient. The values shown are the "
    "last completed step, inside the supported span. Reset to start a new run."
)
REFUSED_SETTING_TEMPLATE: Final = "Setting refused — {error}"
REFUSED_SETTING_NOTICE_TEMPLATE: Final = (
    "{refused}. The simulation is unchanged and still running its previous setting."
)

# What the chart says when a reader has unchecked every compartment. A plot
# missing all six is a blank panel, and a blank panel reads as a display that
# has failed rather than as one showing what it was asked for.
NO_TRACES_SHOWN_TEXT: Final = (
    "No compartment traces are shown. Check a compartment above to draw it — "
    "the readouts and the run itself are unaffected."
)

# Said when a drawn trace goes above the top of the plot, naming which. The
# fixed axis (`CHART_AXIS_TOP_MAC`) is exceeded by a setting in common use -
# sevoflurane's 8% dial is 4.00 MAC - and a trace clipped at the ceiling draws
# as a horizontal line, which is what a plateau looks like. Growing the axis
# to fit was rejected: it redraws the curve at a smaller height partway
# through the induction it is being used to teach.
OFF_SCALE_NOTICE_TEMPLATE: Final = (
    "Above the top of the plot: {compartments}. The axis stops at {top} and these "
    "traces are cut off there — their values are in the readouts above, which are "
    "not clipped."
)

# The control-change panel. Newest first because it is a fixed panel beside
# a chart rather than a scrollback; bounded, and honest about the bound.
NO_CONTROL_CHANGES_TEXT: Final = "No settings changed yet in this run."
MAX_LISTED_ADJUSTMENTS: Final = 12
CONTROL_TIMELINE_HEADING: Final = "Control changes"
CONTROL_TIMELINE_CAPTION: Final = (
    "What was changed during this run, most recent first. Settings only — not a measurement."
)
UNLISTED_CHANGES_TEMPLATE: Final = "{count} earlier change(s) not listed"
UNMARKED_CHANGES_TEMPLATE: Final = "{count} not marked on the chart"
TIMELINE_OVERFLOW_JOINER: Final = "; "

# Names the substance the six readouts belong to (`PL-TCD1`). Label rather
# than sentence, and "Modelled" rather than a bare agent name, because the
# row's own hazard is a reader setting these beside a monitor.
COMPARTMENT_SUBSTANCE_TEMPLATE: Final = "Modelled concentrations: {agent}"

# What the confirmation says before a new case replaces a recorded one, in
# the order a reader meets it: why this is a new case at all, what is about
# to be lost (`formatting.format_case_discard_warning`, per case), and what
# survives. `NEW_CASE_CARRYOVER_TEMPLATE` is a claim about
# `SimulationController.set_agent` and has to stay true with it. It names
# three of the four settings that carry over, deliberately (`PL-0Q1T`): the
# circuit volume carries over too, but it is not a setting the reader chose,
# and listed among sliders it read as one mislaid somewhere.
NEW_CASE_TITLE_TEMPLATE: Final = "Start a new {agent} case?"
NEW_CASE_IS_NOT_A_VIEW_TEXT: Final = (
    "Changing agent starts a new case. This model does not simulate switching "
    "between volatile agents, so a run cannot be continued under a different one."
)
NEW_CASE_CARRYOVER_TEMPLATE: Final = (
    "Fresh gas flow, alveolar ventilation and cardiac output carry over. "
    "Delivered {agent} starts at that agent's own 1 MAC."
)
# Both buttons name their outcome rather than answering a question. The
# declining one is the *default* - filled, and last - so the press a reader
# makes without reading is the one that keeps their case.
KEEP_CURRENT_CASE_TEMPLATE: Final = "Keep the {agent} case"
START_NEW_CASE_TEMPLATE: Final = "Discard and start {agent}"

# While a run is going the agent selector is *replaced* by a chip rather than
# greyed, because a disabled control repaints the agent's identity colour in
# a theme grey at the one moment every number beside it is agent-specific
# (`PL-61WW`). The caption says "running" rather than "this case" because
# that is what is true: the selector returns on Pause.
RUNNING_AGENT_LOCK_TEXT: Final = "Locked while running"

# The agent-accounting panel. The amounts are litres of equivalent pure agent
# gas - not the unit anyone consumes agent in - so the caption says so
# (`PL-TG60`); the two residual lines keep the exponent form because their
# whole purpose is an order of magnitude.
ACCOUNTING_HEADING: Final = "Agent accounting validation"
ACCOUNTING_VALID_TEXT: Final = "Valid"
ACCOUNTING_FAILED_TEXT: Final = "Validation failed"
ACCOUNTING_INITIAL_DETAIL_TEXT: Final = "No unaccounted agent detected."
ACCOUNTING_VALID_DETAIL_TEXT: Final = "The simulation still accounts for all delivered agent."
ACCOUNTING_FAILED_DETAIL_TEXT: Final = "The simulation has detected unaccounted agent."
ACCOUNTING_UNIT_CAPTION: Final = "Litres of equivalent pure agent gas"

# The transport row's labels, and the two selector captions beside it.
START_LABEL: Final = "Start"
PAUSE_LABEL: Final = "Pause"
RESET_LABEL: Final = "Reset"
PLAYBACK_LABEL: Final = "Playback"
TIME_BASE_LABEL: Final = "Time base"
FIT_RUN_LABEL: Final = "Fit run"

# The chart panel's heading and its time-axis captions. The caption states
# the span actually drawn because the width is a mode (`PL-012`): the same
# plot showing fifteen minutes and twelve hours is two different claims
# about what a flat trace means. Under "Fit run" it says both that the
# whole run is drawn and how wide the plot had to be to draw it, because the
# selector then names the rule and only this line names what it came out as.
CHART_HEADING: Final = "Agent concentration and relative partial pressure over time"
FITTED_TIME_AXIS_CAPTION_TEMPLATE: Final = "whole run so far, {span} shown"
CHOSEN_TIME_AXIS_CAPTION_TEMPLATE: Final = "{span} shown"

# The wash-in section. "Modelled, not measured" is its own line rather than
# the tail of a paragraph: three words the safety standard requires, at the
# end of a long sentence, are three words nobody reads (`PL-F9TQ`).
WASH_IN_HEADING: Final = "Wash-in: F_A/F_I, alveolar as a fraction of the modelled circuit"
WASH_IN_DENOMINATOR_TEXT: Final = (
    "F_I = modelled circuit, not the vaporizer dial — a rise across a control mark "
    "can be the denominator moving, not uptake"
)
WASH_IN_MODELLED_TEXT: Final = "Modelled, not measured"
WASH_IN_TRACE_LEGEND_LABEL: Final = "F_A/F_I (solid)"
EQUILIBRIUM_LEGEND_LABEL: Final = "Equilibrium, F_A = F_I (wide dash)"
CONTROL_MARK_LEGEND_LABEL: Final = "Control change (vertical, fine dash)"
#: What assistive technology announces for a compartment's legend box: the
#: act it performs rather than the pattern words beside it, which describe
#: the line and not the control. Carried over from the Flet legend's
#: semantics label so the port loses nothing a screen reader had.
TRACE_TOGGLE_ACCESSIBLE_NAME_TEMPLATE: Final = "Draw the {label} compartment on the chart"
# What the wash-in plot is showing at this instant. A trace that stops has
# to say which of its two boundaries it stopped at: "nothing has reached the
# circuit yet" and "the patient is giving agent back" are opposite
# situations, and a reader shown only an empty plot would have neither.
WASH_IN_STATE_TEMPLATE: Final = "Now: F_A/F_I = {ratio}"
WASH_IN_NOT_DEFINED_TEXT: Final = "Not defined: no agent has reached the circuit yet."
WASH_IN_ELIMINATION_TEXT: Final = (
    "Past equilibrium: alveolar exceeds inspired — the patient is returning agent, "
    "which is elimination and not wash-in."
)
WASH_IN_UNDRAWN_SUFFIX_TEMPLATE: Final = " ({count} earlier stretch(es) not drawn)"

# The two standing statements. The first says what the tool is *for*; the
# second says how to read a number on it, beside the readouts themselves
# (`PL-2K1R`): the compartments this simulator exists to display are the ones
# no monitor shows, so a reader has no measured counterpart to check a
# trace against and the polish of the display argues the other way. Once,
# on the readout section's heading row, because a repeated disclaimer is one
# that stops being read.
USE_DISCLAIMER_TEXT: Final = (
    "Educational simulation only. This idealized model is not a clinical prediction, "
    "monitoring, or dosing tool."
)
INTERPRETATION_DISCLAIMER_TEXT: Final = "Model outputs — not measurements."

# The column counts the readout row may take, widest first: the row reflows
# to the largest of these whose panels fit its width instead of squeezing a
# label (`PL-8M05`), and the widest seats all seven. The rungs are the
# ladder; the widths at which the row steps down are not recorded here,
# because they are a property of the rendering font. `PL-8M05` recorded the
# Flet build's breakpoints as a rendered measurement at Flet's sizes; the
# port derives the same ladder from the font it actually renders with, so no
# pixel figure is asserted that a font or a HiDPI scale would falsify.
READOUT_ROW_LADDER: Final[tuple[int, ...]] = (7, 4, 2, 1)


class Emphasis(StrEnum):
    """How a status word is drawn: the colour role, named without a colour.

    The widget layer maps `MUTED` to `theme.MUTED`, `ACCENT` to
    `theme.ACCENT_TEXT` and `WARNING` to `theme.WARNING`; naming the role
    here keeps every colour token in `theme.py`. `WARNING` is the failure's
    and deliberately not shared with the supported-limit stop: colouring a
    correct model's declared boundary as a fault teaches a reader to
    distrust a sound number, and spends the one signal this interface has
    for a real one.
    """

    MUTED = "muted"
    ACCENT = "accent"
    WARNING = "warning"


@dataclass(frozen=True, slots=True)
class StatusWord:
    """One word stating the run's state, and the emphasis it is drawn with."""

    text: str
    emphasis: Emphasis


def status_word(snapshot: SimulationSnapshot) -> StatusWord:
    """The run's status word: failure, then supported limit, then running, then paused.

    A failure outranks the supported run length on the reasoning
    `notice` gives: the two cannot both arise from one run, and where a
    failure is somehow recorded it is the more serious statement.

    Args:
        snapshot: The run's state this tick.

    Returns:
        The word and its emphasis.
    """

    if snapshot.failure_reason is not None:
        return StatusWord(STATUS_FAILED_TEXT, Emphasis.WARNING)

    if snapshot.supported_limit_reason is not None:
        return StatusWord(STATUS_SUPPORTED_LIMIT_TEXT, Emphasis.MUTED)

    if snapshot.is_running:
        return StatusWord(STATUS_RUNNING_TEXT, Emphasis.ACCENT)

    return StatusWord(STATUS_PAUSED_TEXT, Emphasis.MUTED)


@dataclass(frozen=True, slots=True)
class ReadoutPanel:
    """One readout panel's fixed half: its name, its gloss and what it reads.

    Attributes:
        name: The modeled quantity, in the model's own terms.
        qualifier: What a clinician would compare that quantity against, or
            None where nothing measured corresponds to it. Drawn smaller
            than the name because it is the weaker claim of the two: the
            compartment is what the model computes, the measurement is what
            a clinician would set beside it, and equal type would offer them
            as alternative names for one quantity (`PL-NV9W`, `PL-8M05`).
        quantity: The compartment the panel reads, or None for the clock.
    """

    name: str
    qualifier: str | None
    quantity: RecordedQuantity | None


# The seven panels in row order. "end-tidal-equivalent", never "end-tidal":
# `docs/MODEL.md` § "Minimum displayed outputs" requires the hedge because
# dead space, airway sampling delay, shunt and V/Q mismatch are all in its
# "Known limitations", so this value is not end-tidal in any patient, and
# end-tidal is the name of a *measurement* a clinician would most readily set
# this readout beside. Do not shorten either gloss to fit a layout;
# `test_the_alveolar_readout_is_labelled_end_tidal_equivalent` holds the pair.
READOUT_PANELS: Final[tuple[ReadoutPanel, ...]] = (
    ReadoutPanel("Simulated time", None, None),
    ReadoutPanel("Circuit", "inspired", RecordedQuantity.CIRCUIT),
    ReadoutPanel("Alveolar", "end-tidal-equivalent", RecordedQuantity.ALVEOLAR),
    ReadoutPanel("Mixed venous", None, RecordedQuantity.MIXED_VENOUS),
    ReadoutPanel("Vessel-rich group", None, RecordedQuantity.VESSEL_RICH),
    ReadoutPanel("Muscle", None, RecordedQuantity.MUSCLE),
    ReadoutPanel("Fat", None, RecordedQuantity.FAT),
)


@dataclass(frozen=True, slots=True)
class Readout:
    """One readout panel's four lines, as drawn this tick.

    Attributes:
        name: The panel's name line.
        qualifier: Its gloss line, or `EMPTY_METRIC_QUALIFIER` where the
            panel has none, so the line is held open.
        value: The reading with its unit: the clock in compound form, or a
            compartment as a percent of one atmosphere.
        secondary: The second line under the value: the compartment as a
            multiple of the running agent's 1 MAC, or on the clock panel
            the playback rate. Both units are shown at once rather than
            behind a selector, because a selector would make the unit a
            mode. The rate is drawn at every rate including 1x, so a blank
            line never has to be read as real time (`PL-SN2C`).
    """

    name: str
    qualifier: str
    value: str
    secondary: str


def _compartment_fraction(snapshot: SimulationSnapshot, quantity: RecordedQuantity) -> Fraction:
    """The snapshot field one readout panel reads.

    Raises:
        KeyError: If `quantity` is not one of the six compartments the
            readout row shows - `RecordedQuantity.WASH_IN_RATIO` has its own
            plot and no panel.
    """

    return {
        RecordedQuantity.CIRCUIT: snapshot.inspired_partial_pressure_fraction,
        RecordedQuantity.ALVEOLAR: snapshot.alveolar_partial_pressure_fraction,
        RecordedQuantity.MIXED_VENOUS: snapshot.mixed_venous_partial_pressure_fraction,
        RecordedQuantity.VESSEL_RICH: snapshot.vessel_rich_partial_pressure_fraction,
        RecordedQuantity.MUSCLE: snapshot.muscle_partial_pressure_fraction,
        RecordedQuantity.FAT: snapshot.fat_partial_pressure_fraction,
    }[quantity]


def readouts(snapshot: SimulationSnapshot, playback_rate: PlaybackRate) -> tuple[Readout, ...]:
    """The seven readouts, in `READOUT_PANELS` order, from one snapshot.

    Every MAC line is produced from this snapshot's own divisor, read once,
    so a frame can never pair one agent's concentration with another agent's
    MAC.

    Args:
        snapshot: The run's state this tick.
        playback_rate: The rate the run is being played at - a view
            setting, drawn on the clock panel because a rate is a mode and
            the clock is where it would be misread.

    Returns:
        One `Readout` per panel.

    Raises:
        ValueError: If the snapshot's elapsed time is negative or not finite
            (`format_elapsed`), or its `agent_mac_percent` is not strictly
            positive (`format_mac_multiple`).
    """

    mac_percent = snapshot.agent_mac_percent
    panels: list[Readout] = []

    for panel in READOUT_PANELS:
        qualifier = panel.qualifier if panel.qualifier is not None else EMPTY_METRIC_QUALIFIER

        if panel.quantity is None:
            value = format_elapsed(snapshot.elapsed_s)
            secondary = format_playback_rate(playback_rate.multiplier)
        else:
            fraction = _compartment_fraction(snapshot, panel.quantity)
            value = format_percent(fraction)
            secondary = format_mac_multiple(fraction, mac_percent)

        panels.append(Readout(panel.name, qualifier, value, secondary))

    return tuple(panels)


# The widest string each readout column can show, so a panel can reserve
# the width once instead of moving as a value changes length (`PL-3355`).
# The value line is the clock's just before the supported run length -
# every component of the compound form present, with tenths - and the
# second line is the longest playback rate; a percent readout and a MAC
# multiple are both shorter than these at every value the dial can reach.
# Chosen by character count from the formatters' own extremes; the widget
# measures the chosen string in its font.
WIDEST_READOUT_VALUE: Final = max(
    (
        format_elapsed(MAXIMUM_ELAPSED_SIMULATION_TIME_S - tenth * SIMULATION_STEP_S)
        for tenth in range(1, 11)
    ),
    key=len,
)
WIDEST_READOUT_SECONDARY: Final = max(
    (format_playback_rate(rate.multiplier) for rate in SUPPORTED_PLAYBACK_RATES), key=len
)


@dataclass(frozen=True, slots=True)
class ParameterControl:
    """One setting control's fixed half: what it sets and how it is offered.

    Attributes:
        control: The setting it forwards to the controller.
        name: The setting's name, or None where the name carries the
            agent and comes from `format_delivered_label` per tick.
        qualifier: Where the name alone would be read as a different
            quantity than the model uses, the words that separate the two,
            or None where the name is unambiguous. "common gas outlet"
            because "Fresh gas flow" alone is what a flowmeter bank is
            labelled, and a flowmeter reads the carrier gas only, while
            the model's mass balance makes this the whole post-vaporizer
            stream - 22% apart at desflurane's 18% dial, landing on the
            circuit time constant the wash-in curve is about (`PL-71CF`).
        unit: The unit the slider's value is in.
        decimals: The display resolution the slider steps at, from
            `formatting.py`, so the value applied to the model is exactly
            the value printed beside the slider (`PL-25KS`, decision D4).
        minimum: The slider's floor.
        maximum: The slider's ceiling, or None where it is the running
            agent's own vaporizer maximum and comes from the snapshot.
    """

    control: ControlInput
    name: str | None
    qualifier: str | None
    unit: str
    decimals: int
    minimum: float
    maximum: float | None


# The four controls in panel order. The three flow ranges are the model's
# own declaration (`core/supported_ranges.py`) so the interface offers
# exactly the domain the verification gates cover (`PL-0MLQ`).
PARAMETER_CONTROLS: Final[tuple[ParameterControl, ...]] = (
    ParameterControl(
        ControlInput.FRESH_GAS_FLOW,
        "Fresh gas flow",
        "common gas outlet",
        "L/min",
        FLOW_DISPLAY_DECIMALS,
        MINIMUM_FRESH_GAS_FLOW_L_MIN,
        MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    ),
    ParameterControl(
        ControlInput.DELIVERED,
        None,
        None,
        "%",
        CONCENTRATION_DISPLAY_DECIMALS,
        MIN_DELIVERED_CONCENTRATION_PERCENT,
        None,
    ),
    ParameterControl(
        ControlInput.ALVEOLAR_VENTILATION,
        "Alveolar ventilation",
        None,
        "L/min",
        FLOW_DISPLAY_DECIMALS,
        MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
        MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    ),
    ParameterControl(
        ControlInput.CARDIAC_OUTPUT,
        "Cardiac output",
        None,
        "L/min",
        FLOW_DISPLAY_DECIMALS,
        MINIMUM_CARDIAC_OUTPUT_L_MIN,
        MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    ),
)


@dataclass(frozen=True, slots=True)
class SettingReadout:
    """One setting control as drawn this tick: its range, its value and its text.

    Every slider is written from the snapshot on every tick, not left where
    the reader dragged it: a refused setting must not leave a control
    reading one value while the simulation runs at another, because the
    control is a display of model state as much as an input to it.

    Attributes:
        control: The setting it forwards.
        name: The name line.
        qualifier: The gloss line, or the empty string where there is none.
            No spacer is drawn for a setting: these four panels are of
            unequal height by design, the delivered dial carrying a MAC
            line the flow settings have no conversion for.
        unit: The unit of `value`.
        decimals: The display resolution the slider steps at.
        minimum: The slider's floor, in `unit`.
        maximum: The slider's ceiling, in `unit`.
        value: The setting in force, in `unit`.
        value_text: The setting as the readout beside the slider prints it.
        secondary: The same setting in the second display unit - the
            delivered dial as a multiple of the agent's 1 MAC, so the one
            control a reader sets can be compared with the traces it
            produces - or the empty string for a setting with one unit.
    """

    control: ControlInput
    name: str
    qualifier: str
    unit: str
    decimals: int
    minimum: float
    maximum: float
    value: float
    value_text: str
    secondary: str


def setting_readouts(snapshot: SimulationSnapshot) -> tuple[SettingReadout, ...]:
    """The four setting controls, in `PARAMETER_CONTROLS` order, from one snapshot.

    Args:
        snapshot: The run's state this tick.

    Returns:
        One `SettingReadout` per control.

    Raises:
        ValueError: If `agent_mac_percent` is not strictly positive
            (`format_mac_multiple`, on the delivered dial's MAC line).
    """

    delivered = snapshot.delivered_partial_pressure_fraction
    flows = {
        ControlInput.FRESH_GAS_FLOW: snapshot.fresh_gas_flow_l_min,
        ControlInput.ALVEOLAR_VENTILATION: snapshot.alveolar_ventilation_l_min,
        ControlInput.CARDIAC_OUTPUT: snapshot.cardiac_output_l_min,
    }
    settings: list[SettingReadout] = []

    for control in PARAMETER_CONTROLS:
        if control.control is ControlInput.DELIVERED:
            value: float = percent_from_fraction(delivered)
            value_text = format_percent(delivered)
            secondary = format_mac_multiple(delivered, snapshot.agent_mac_percent)
        else:
            value = flows[control.control]
            value_text = format_flow(value)
            secondary = ""

        settings.append(
            SettingReadout(
                control=control.control,
                name=(
                    control.name
                    if control.name is not None
                    else format_delivered_label(snapshot.agent_display_name)
                ),
                qualifier=control.qualifier if control.qualifier is not None else "",
                unit=control.unit,
                decimals=control.decimals,
                minimum=control.minimum,
                maximum=(
                    control.maximum
                    if control.maximum is not None
                    else snapshot.max_delivered_concentration_percent
                ),
                value=value,
                value_text=value_text,
                secondary=secondary,
            )
        )

    return tuple(settings)


def slider_position(value: float, decimals: int) -> int:
    """The integer slider position for a value, at the control's display resolution.

    The sliders are integer-valued and step at the display resolution, so
    a position and a printed value are the same number (`PL-25KS`, D4).

    Args:
        value: The setting, in the control's unit.
        decimals: The control's `SettingReadout.decimals`.

    Returns:
        `value` in counts of `10**-decimals`, rounded to the nearest.
    """

    return round(value * 10.0**decimals)


def slider_value(position: int, decimals: int) -> float:
    """The value an integer slider position stands for; the inverse of `slider_position`.

    Args:
        position: The slider's integer position.
        decimals: The control's `SettingReadout.decimals`.

    Returns:
        The setting, in the control's unit.
    """

    return position / 10.0**decimals


def delivered_fraction(percent: float) -> Fraction:
    """The fraction the core is set with, from the delivered dial's percent.

    Through `core.concentration.fraction_from_percent` and never a division
    by hand, so the one unit conversion between the dial and the model is
    made in the one place that owns it.

    Args:
        percent: The dial's position, in percent of one atmosphere.

    Returns:
        The same partial pressure as a fraction of one atmosphere.
    """

    return fraction_from_percent(Percent(percent))


@dataclass(frozen=True, slots=True)
class Transport:
    """Which transport controls a reader may use this tick.

    Attributes:
        start_enabled: False while running, and false for a run that has
            failed or stands at the supported run length: neither can be
            resumed - only reset - and a Start the controller would refuse
            is a control presenting itself as working.
        pause_enabled: True only while running.
        reset_enabled: Always true; Reset is how every stopped state ends.
        selector_locked: Whether the agent selector is replaced by the
            running-agent chip. True while running, because choosing an
            agent discards the case.
    """

    start_enabled: bool
    pause_enabled: bool
    reset_enabled: bool
    selector_locked: bool


def transport(snapshot: SimulationSnapshot) -> Transport:
    """The transport enablement for one snapshot.

    Args:
        snapshot: The run's state this tick.

    Returns:
        Which controls are usable.
    """

    stopped = snapshot.failure_reason is not None or snapshot.supported_limit_reason is not None

    return Transport(
        start_enabled=not snapshot.is_running and not stopped,
        pause_enabled=snapshot.is_running,
        reset_enabled=True,
        selector_locked=snapshot.is_running,
    )


def refused_setting_notice(error: SimulationConfigurationError) -> str:
    """What the banner says about a setting the core refused.

    A `SimulationConfigurationError` means the core rejected the value and
    changed nothing: the run is untouched and must not be marked failed,
    so the notice names the setting and `notice` appends that the run goes
    on unchanged.

    Args:
        error: The refusal, whose message names the value and why.

    Returns:
        The first half of the refused-setting banner.
    """

    return REFUSED_SETTING_TEMPLATE.format(error=error)


def notice(snapshot: SimulationSnapshot, rejected_setting_notice: str | None) -> str | None:
    """The banner: a stopped run, or a refused setting, or nothing.

    A stopped run outranks a refused setting because it describes the state
    of everything else on screen, where a refusal describes only one
    control. A failure outranks the supported run length in turn.

    Args:
        snapshot: The run's state this tick.
        rejected_setting_notice: `refused_setting_notice`'s text for the
            last refused setting, or None if the last setting took. Held by
            the run's view rather than the controller because a refused
            setting changes nothing about the simulation.

    Returns:
        The banner text, or None when there is nothing to say.
    """

    if snapshot.failure_reason is not None:
        return FAILURE_NOTICE_TEMPLATE.format(failure_reason=snapshot.failure_reason)

    if snapshot.supported_limit_reason is not None:
        return SUPPORTED_LIMIT_NOTICE_TEMPLATE.format(run_length=format_supported_run_length())

    if rejected_setting_notice is not None:
        return REFUSED_SETTING_NOTICE_TEMPLATE.format(refused=rejected_setting_notice)

    return None


class HaltDisposition(StrEnum):
    """Which of the two stopped states a raise puts the run in."""

    SUPPORTED_LIMIT = "supported_limit"
    FAILURE = "failure"


def halt_disposition(error: BaseException) -> tuple[HaltDisposition, str]:
    """How a raise stops the run, and the reason recorded for it.

    Every exception stops the run - a `TypeError` from a future refactor
    kills a timer slot exactly as silently as a modelling failure does.
    What the type decides is what the reader is told, for exactly one type:
    `SimulationDomainLimitError` is the run reaching the end of the
    supported domain, where the core refused the next step before taking
    it and nothing was miscalculated, so reporting it as a failure would put
    "simulation error" over a correct model that stopped where
    `docs/MODEL.md` says it must (`PL-Y5WR`, `PL-V6M0`). Everything else,
    known or not, is a failure: the narrow case is the named one, so an
    unrecognised exception falls through to the more cautious branch.

    Args:
        error: What was raised.

    Returns:
        The disposition, and the reason to record with it: the limit's own
        message, or `"{TypeName}: {message}"` for a failure.
    """

    if isinstance(error, SimulationDomainLimitError):
        return HaltDisposition.SUPPORTED_LIMIT, str(error)

    return HaltDisposition.FAILURE, f"{type(error).__name__}: {error}"


@dataclass(frozen=True, slots=True)
class Accounting:
    """The agent-accounting panel as drawn this tick.

    Attributes:
        status: "Valid" in accent or "Validation failed" in warning.
        detail: One sentence under it saying what the status means.
        amounts: Five lines: delivered, exhausted and stored agent at the
            resolution `format_agent_volume` derives, then the unaccounted
            amount and the absolute error in exponent form, since an order
            of magnitude is what those two are for (`PL-TG60`).
    """

    status: StatusWord
    detail: str
    amounts: str


def accounting(snapshot: SimulationSnapshot) -> Accounting:
    """The agent-accounting panel for one snapshot.

    Args:
        snapshot: The run's state this tick.

    Returns:
        The panel's three parts.
    """

    if snapshot.agent_accounting_passes_validation:
        status = StatusWord(ACCOUNTING_VALID_TEXT, Emphasis.ACCENT)
        detail = ACCOUNTING_VALID_DETAIL_TEXT
    else:
        status = StatusWord(ACCOUNTING_FAILED_TEXT, Emphasis.WARNING)
        detail = ACCOUNTING_FAILED_DETAIL_TEXT

    amounts = "\n".join(
        (
            f"Delivered: {format_agent_volume(snapshot.delivered_agent_l)}",
            f"Exhausted: {format_agent_volume(snapshot.exhausted_agent_l)}",
            f"Stored: {format_agent_volume(snapshot.stored_agent_l)}",
            f"Unaccounted: {format_agent_residual(snapshot.unaccounted_agent_l)}",
            f"Absolute error: {format_agent_residual(snapshot.agent_accounting_absolute_error_l)}",
        )
    )

    return Accounting(status, detail, amounts)


@dataclass(frozen=True, slots=True)
class TimelinePanel:
    """The control-change panel as drawn this tick.

    Attributes:
        entries: The listed adjustments, newest first, one per line, or
            `NO_CONTROL_CHANGES_TEXT` for a run nobody has touched.
        overflow: What the panel and the chart could not show - the count
            of earlier changes not listed and of changes not marked on the
            chart, joined - or the empty string when nothing was left out.
            Counted rather than dropped, because a list that quietly stops
            asserts that nothing earlier happened.
    """

    entries: str
    overflow: str


def timeline_panel(
    adjustments: Sequence[ControlAdjustment], undrawn_control_marks: int
) -> TimelinePanel:
    """The control-change panel for one run's adjustments.

    Args:
        adjustments: The run's adjustments, oldest first, as
            `control_timeline.AdjustmentGrouping` groups them.
        undrawn_control_marks: How many adjustments inside the chart's
            window its mark pool could not draw, from
            `RunFrame.undrawn_control_marks` of the same tick.

    Returns:
        The panel's two parts.
    """

    if not adjustments:
        return TimelinePanel(NO_CONTROL_CHANGES_TEXT, "")

    listed = adjustments[-MAX_LISTED_ADJUSTMENTS:]
    entries = "\n".join(format_adjustment(adjustment) for adjustment in reversed(listed))

    unlisted = len(adjustments) - len(listed)
    notes: list[str] = []

    if unlisted:
        notes.append(UNLISTED_CHANGES_TEMPLATE.format(count=unlisted))

    if undrawn_control_marks:
        notes.append(UNMARKED_CHANGES_TEMPLATE.format(count=undrawn_control_marks))

    return TimelinePanel(entries, TIMELINE_OVERFLOW_JOINER.join(notes))


def substance_heading(snapshot: SimulationSnapshot) -> str:
    """The heading naming the substance the six readouts belong to (`PL-TCD1`).

    Args:
        snapshot: The run's state this tick.

    Returns:
        The heading line.
    """

    return COMPARTMENT_SUBSTANCE_TEMPLATE.format(agent=snapshot.agent_display_name)


def time_axis_caption(frame: ChartFrame) -> str:
    """The span of run the chart is showing, and whether the reader or the run chose it.

    Args:
        frame: The frame drawn this tick.

    Returns:
        The caption line.
    """

    span = format_time_base(frame.time_base.span_s)

    if frame.fitted:
        return FITTED_TIME_AXIS_CAPTION_TEMPLATE.format(span=span)

    return CHOSEN_TIME_AXIS_CAPTION_TEMPLATE.format(span=span)


def mac_reference_caption(frame: ChartFrame) -> str:
    """The divisor every MAC number on the page was produced with.

    Names the reference run's agent and its 1 MAC, which is what makes the
    MAC readouts traceable without opening a data file (`CLAUDE.md`,
    safety-critical clinical-output standard).

    Args:
        frame: The frame drawn this tick; its runs are all on one agent.

    Returns:
        The reference line.
    """

    return format_mac_reference(frame.runs[0].agent_display_name, frame.mac_percent)


def mac_awake_caption(snapshot: SimulationSnapshot) -> str:
    """What the MAC-awake band was drawn from: its published fraction and the divisor.

    Both free parameters are named, so a reader who disagrees with either
    can see which (`PL-F52R`).

    Args:
        snapshot: The reference run's state this tick.

    Returns:
        The reference line.
    """

    mac_awake = snapshot.agent_mac_awake

    return format_mac_awake_reference(
        snapshot.agent_display_name,
        fraction_of_mac=mac_awake.fraction_of_mac,
        standard_deviation_fraction_of_mac=mac_awake.standard_deviation_fraction_of_mac,
        mac_percent=snapshot.agent_mac_percent,
    )


def wash_in_state(snapshot: SimulationSnapshot, undrawn_wash_in_stretches: int) -> str:
    """What the wash-in plot is showing at this instant, and why.

    Where the trace is drawing, the number here is the same value its
    right-hand end stands at - `read_wash_in` on the snapshot's own
    alveolar and inspired fractions - so the plot and the sentence beside it
    cannot disagree.

    Args:
        snapshot: The run's state this tick.
        undrawn_wash_in_stretches: How many stretches inside the window the
            plot's pool could not draw, from `RunFrame.undrawn_wash_in_stretches`
            of the same tick; appended so the pool's bound is displayed
            rather than silent.

    Returns:
        One line for the row above the plot.
    """

    reading = read_wash_in(
        snapshot.alveolar_partial_pressure_fraction, snapshot.inspired_partial_pressure_fraction
    )

    if reading.plotted_ratio is not None:
        state = WASH_IN_STATE_TEMPLATE.format(ratio=format_wash_in_ratio(reading.plotted_ratio))
    elif reading.domain is WashInDomain.NO_INSPIRED_AGENT:
        state = WASH_IN_NOT_DEFINED_TEXT
    else:
        state = WASH_IN_ELIMINATION_TEXT

    if undrawn_wash_in_stretches:
        state += WASH_IN_UNDRAWN_SUFFIX_TEMPLATE.format(count=undrawn_wash_in_stretches)

    return state


def off_scale_notice(frame: ChartFrame, run_index: int) -> str | None:
    """Which of one run's drawn traces are above the top of the plot, if any.

    Read from the points the frame drew rather than from the snapshot: the
    snapshot carries only the newest sample, and a trace that rose above
    the axis earlier in the window is still drawn clipped now. Hidden
    traces are skipped, so the notice never points at a trace that is not
    there. A trace is off scale only once it clears the ceiling by more
    than the readouts resolve: isoflurane's ceiling is 3 x 1.2, which in
    binary floating point is 3.5999999999999996, and a comparison against
    zero would report that noise as an excursion.

    Args:
        frame: The frame drawn this tick.
        run_index: Which of the frame's runs.

    Returns:
        The notice, or None when every drawn trace is inside the axis.

    Raises:
        IndexError: If `run_index` is not one of the frame's runs.
    """

    run = frame.runs[run_index]
    off_scale = [
        trace_style(quantity).label
        for quantity in frame.visible
        if any(
            percent - frame.axis_top_percent > CONCENTRATION_DISPLAY_RESOLUTION_PERCENT
            for percent in run.percents(quantity)
        )
    ]

    if not off_scale:
        return None

    return OFF_SCALE_NOTICE_TEMPLATE.format(
        compartments=", ".join(off_scale),
        top=format_mac_multiple(
            fraction_from_percent(Percent(frame.axis_top_percent)), Percent(frame.mac_percent)
        ),
    )


def no_traces_shown(frame: ChartFrame) -> bool:
    """Whether the reader has unchecked every compartment, so the chart must say so.

    Args:
        frame: The frame drawn this tick.

    Returns:
        True when no trace is drawn.
    """

    return not frame.visible


@dataclass(frozen=True, slots=True)
class NewCaseQuestion:
    """The confirmation asked before a recorded run is discarded for a new agent.

    Attributes:
        title: Names the agent the reader would start.
        body: Three statements in the order a reader meets them: why this
            is a new case at all, what is about to be lost, and what
            survives. Three rather than one paragraph because they answer
            three different questions and a reader stops at the first that
            satisfies them.
        discard_label: The destructive action, drawn first and outlined.
        keep_label: The safe action, drawn last and filled - the default
            press, so the press a reader makes without reading keeps their
            case.
    """

    title: str
    body: tuple[str, str, str]
    discard_label: str
    keep_label: str


def new_case_question(
    snapshot: SimulationSnapshot, new_agent_display_name: str, adjustment_count: int
) -> NewCaseQuestion:
    """The confirmation for one proposed new case.

    Args:
        snapshot: The run that would be discarded.
        new_agent_display_name: The agent the reader selected, as it is
            named to them.
        adjustment_count: How many control changes the run holds, counted
            as the panel beside the chart lists them - through the same
            grouping - so the count of what is about to be lost and the
            list of it cannot come from two readings of one record.

    Returns:
        The question's text.

    Raises:
        ValueError: If the snapshot's elapsed time is negative or not finite
            (`format_case_discard_warning`, through `format_elapsed`).
    """

    current = snapshot.agent_display_name.lower()
    new = new_agent_display_name.lower()

    return NewCaseQuestion(
        title=NEW_CASE_TITLE_TEMPLATE.format(agent=new),
        body=(
            NEW_CASE_IS_NOT_A_VIEW_TEXT,
            format_case_discard_warning(
                snapshot.agent_display_name, snapshot.elapsed_s, adjustment_count
            ),
            NEW_CASE_CARRYOVER_TEMPLATE.format(agent=new),
        ),
        discard_label=START_NEW_CASE_TEMPLATE.format(agent=new),
        keep_label=KEEP_CURRENT_CASE_TEMPLATE.format(agent=current),
    )


def readout_columns(width_px: float, panel_width_px: float, spacing_px: float) -> int:
    """How many readout panels stand side by side at this width.

    The largest rung of `READOUT_ROW_LADDER` whose panels fit: `count`
    panels of `panel_width_px` with `count - 1` gaps of `spacing_px`
    between them take no more than `width_px`. One column is the floor,
    however narrow the row, because a row must hold its panels somewhere.
    The panel width is the widget's measured reservation - the widest value
    each column can show, in the rendering font (`PL-3355`) - so the row
    steps down exactly where a panel would otherwise be clipped, at
    whatever width that is on the reader's display (`PL-8M05`).

    Args:
        width_px: The readout row's width, in logical pixels.
        panel_width_px: The width every column is held to, in logical pixels.
        spacing_px: The gap between neighbouring columns, in logical pixels.

    Returns:
        The column count: 7, 4, 2 or 1.
    """

    for columns in READOUT_ROW_LADDER:
        if columns * panel_width_px + (columns - 1) * spacing_px <= width_px:
            return columns

    return READOUT_ROW_LADDER[-1]
