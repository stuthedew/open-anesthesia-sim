"""What the dashboard states about one run at one instant, computed without a GUI toolkit.

This module is the counterpart of `chart_frame.py` for everything beside the
plots: the status word, the notice banner, the seven readouts, the four
setting controls, the transport enablement, the agent-accounting panel, the
control-change list, the two bookmark listings, the chart captions and the
new-case question. Each is a pure function of a `SimulationSnapshot`, or of
the `ChartFrame` that the same tick assembled. So every string a reader sees,
and every precedence rule that chooses between two strings, can be read and
tested without a display. `tests/unit/test_dashboard_frame.py` tests them that
way. The PySide6 widgets in `qt_widgets.py`, `run_view.py` and
`simulation_view.py` call these functions on every tick and decide nothing
themselves (`PL-25KS`, decision D2).

Every displayed number passes through `app/formatting.py`. This module
composes strings and decides enablement, precedence and layout arithmetic.
It formats no number itself, so no display resolution is written here. So a
change to a displayed resolution takes effect here without an edit to this
module.

The strings are copied word for word from the Flet dashboard. Matching that
build is the port's definition of done. Three of the strings are safety
requirements rather than wording choices: the "Alveolar" readout with the
gloss "end-tidal-equivalent" (`PL-NV9W`), the "Circuit" readout with the gloss
"inspired" (`PL-8M05`), and the "Fresh gas flow" control with the gloss
"common gas outlet" (`PL-71CF`). `docs/INTERFACE.md` § "Minimum displayed
outputs" states all three and the reason for each, and an exact-string test
enforces each of them.
"""

import html
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from math import ceil, floor, isfinite
from pathlib import Path
from types import MappingProxyType
from typing import Final

from anesthesia_sim.app.bookmarks import (
    BookmarkSet,
    BookmarkStandings,
    MacTarget,
    MarkStanding,
    TimeBookmark,
)
from anesthesia_sim.app.branch_controls import HERE_FORK_NAME
from anesthesia_sim.app.chart_frame import (
    ALVEOLAR_FRACTION_NAME,
    COMPARED_COMPARTMENT_CAP,
    INSPIRED_FRACTION_NAME,
    WASH_IN_RATIO_NAME,
    ChartFrame,
    RunCount,
    RunIndex,
    TraceStyle,
    latest_values_lines,
    latest_wash_in_lines,
    plain_text,
    preview_label_lines,
    trace_style,
)
from anesthesia_sim.app.chart_time_base import TIME_BASE_LADDER
from anesthesia_sim.app.control_record import (
    CONTROL_INPUT_DISPLAY_UNITS,
    CONTROL_INPUT_FIELDS,
    ControlInput,
    control_value,
)
from anesthesia_sim.app.control_timeline import (
    CONTROL_INPUT_LABELS,
    ControlAdjustment,
    format_adjustment,
)
from anesthesia_sim.app.controller import (
    HereForkPoint,
    MarkForkPoint,
    PreviewOfAnotherCase,
    RunRecord,
    RunSettings,
    RunStatus,
    SimulationSnapshot,
)
from anesthesia_sim.app.display_units import (
    BODY_STORES_CONDITION_LINES,
    REFERENCE_CONDITION_LABEL,
    DisplayUnit,
)
from anesthesia_sim.app.failures import FailureKind, failure_kind
from anesthesia_sim.app.formatting import (
    CONCENTRATION_DISPLAY_DECIMALS,
    CONCENTRATION_DISPLAY_RESOLUTION_PERCENT,
    DECIMAL_BASE,
    FLOW_DISPLAY_DECIMALS,
    MAC_DISPLAY_DECIMALS,
    MAC_UNIT_SUFFIX,
    VAPORIZER_LABEL,
    format_agent_residual,
    format_agent_volume,
    format_branch_discard_warning,
    format_build_version,
    format_case_discard_warning,
    format_chart_time_label,
    format_delivered_label,
    format_delivered_playback_rate,
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
    mac_multiple,
    render_mac_multiple,
)
from anesthesia_sim.app.playback import SUPPORTED_PLAYBACK_RATES, PlaybackRate
from anesthesia_sim.app.run_series import COMPARTMENT_GLOSSES, COMPARTMENT_NAMES, RecordedQuantity
from anesthesia_sim.app.wash_in import WashInDomain, WashInReading
from anesthesia_sim.app_metadata import APP_DISPLAY_NAME
from anesthesia_sim.core.agent_simulation_validation import AgentSimulationValidationResult
from anesthesia_sim.core.checked_number import shown
from anesthesia_sim.core.concentration import Fraction, Percent, fraction_from_percent
from anesthesia_sim.core.exceptions import (
    SettingLimit,
    SettingOutsideRange,
    SimulationConfigurationError,
    SimulationDomainLimitError,
)
from anesthesia_sim.core.mac import mac_for_patient
from anesthesia_sim.core.parameters import (
    AGENT_DATA_FILENAMES,
    load_agent_parameters,
    load_reference_adult_parameters,
)
from anesthesia_sim.core.rounding import WHOLE_COUNT_TOLERANCE
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MINIMUM_CARDIAC_OUTPUT_L_MIN,
    CaseInstant,
)
from anesthesia_sim.core.units import MINUTES_PER_HOUR, SECONDS_PER_HOUR, SECONDS_PER_MINUTE
from anesthesia_sim.layout.run_identity import RunId, SessionToken

# How often the simulation timer fires, in milliseconds of real time. It is a
# whole number, so the simulated time that a tick owes a run is a whole number
# of milliseconds at every playback rate (`OwedSimulatedTime` in
# `app/playback.py`). A tick is a tenth of the one-second step
# (`core/simulation_step.py`). So at real time the run takes one step on every
# tenth tick, and a press of Pause or a change of rate is acted on within a
# tenth of a second. The interval also sets the interface's control resolution
# at the fast rates (`PL-NBWP`). A tick takes all of its steps without
# interruption, so a setting changed while the run plays first takes effect on
# the next step the loop takes (`PlaybackRate.control_grid_s`).
SIMULATION_TICK_INTERVAL_MS: Final = 100
# How often the display redraws, in seconds of real time. It is twice the
# tick, and it is written as its own number rather than derived from the tick,
# because a display cadence and a timer cadence are separate decisions. At 1x
# and 5x a step takes longer than a frame, so some frames redraw unchanged
# values. `test_a_frame_is_two_ticks` checks the relation with the tick.
RENDER_INTERVAL_S: Final = 0.2
# The shortest time, in milliseconds of real time, between the starts of two
# frames drawn for a dial that the reader is moving. Nielsen Norman Group gives
# 0.1 s as the limit for a user to feel that they are directly manipulating
# what is on screen ("Response Times: The 3 Important Limits", nngroup.com).
# The render tick stays slower, because a chart that follows a playing run
# with no hand on a dial is not being manipulated, and drawing every 0.1 s
# would double the drawing load for the whole run (`PL-NKFD`).
INPUT_FRAME_INTERVAL_MS: Final = 100
# How wide the chart is before the first frame is drawn. It is the narrowest
# rung, which is the width "Fit run" chooses for a run that has recorded
# nothing.
INITIAL_CHART_TIME_BASE: Final = TIME_BASE_LADDER[0]

# How many runs the dashboard may draw at once. The limit is two for two
# reasons. Two is what `ROADMAP.md` § "Completed: v0.5.0 - the case you can
# branch" puts in its own out-of-scope list. And the encoding that tells one run from
# another has two levels (`PL-HLD5`: the run is shown by line width, with a cap
# of two compartments). A third run would have no encoding left to be drawn
# with.
MAX_DISPLAYED_RUNS: Final = 2
# Where the two runs of a comparison are drawn. The trunk is drawn first and
# its branch second. That order is an invariant of how `SimulationView` builds
# and adds runs, not a fact about a case. The index decides where a run is
# drawn and never what it is called: `run_label` names a run from its identity
# (`PL-7Z84`).
TRUNK_RUN_INDEX: Final = 0
BRANCH_RUN_INDEX: Final = 1

# A readout with no gloss still draws the gloss line, so every reading in the
# row sits on one baseline (`PL-8M05`). The line holds a no-break space rather
# than an empty string. A Qt label holding an empty string is one pixel shorter
# than one holding text in most fonts. The container's Inter is an exception,
# which `PL-P55M` mistook for the rule. CI's font gave 15 px for an empty
# second-unit line and 16 px for a filled one. A no-break space gives the
# same height as text in every font measured (`PL-P55M`).
# `test_an_empty_gloss_line_is_as_tall_as_a_filled_one` pins the height.
EMPTY_METRIC_QUALIFIER: Final = "\u00a0"
# The same spacer for the second-unit line. No readout draws it today, because
# the clock panel's second line always shows the playback rate (`PL-SN2C`).
EMPTY_METRIC_SECONDARY_VALUE: Final = "\u00a0"

# The lowest setting of the delivered-concentration dial, in percent. Its
# maximum depends on the agent, because it is the real vaporizer's capability.
# The maximum comes from
# `SimulationSnapshot.max_delivered_concentration_percent` rather than from a
# constant. The minimum is defined here because it is a percent, while the
# core's own guard is a fraction. The flow ranges belong to `core/` and are
# never restated here. The ranges for ventilation and cardiac output are
# constants imported from `core/supported_ranges.py` (`PL-0MLQ`). The fresh gas
# flow's range belongs to the circuit. It is read from
# `SimulationSnapshot.accepted_fresh_gas_flow_range_l_min`, because a machine
# profile can narrow it (`PL-7CRY`).
MIN_DELIVERED_CONCENTRATION_PERCENT: Final = 0.0

# The five status words. A stopped run must never be shown as paused, and the
# two stopped states must not be confused with each other. A failure says the
# model reached a state it could not step from. The supported run length says
# the model reached the end of what it is claimed to represent, having done
# everything right.
STATUS_PAUSED_TEXT: Final = "Paused"
# The status word of a run that a mark paused, as opposed to the user's own
# Pause (`PL-QBQX`). The fork control's "stopped on your mark" was the only cue,
# and the fork control is withdrawn while two runs are compared. A MAC target's
# row reads "reached" from its first crossing, so it does not change on a later
# one either. Without this word, a run that a mark stopped during a comparison
# looked like a pause that nobody made. The word starts with "Paused", because
# the run is paused and Start resumes it (`docs/INTERFACE.md` § "Halting on a marked
# crossing"). It reuses the fork label's ratified "stopped on your mark", which
# names no mark and no instant. A mark inside a step halts the run at the step's
# end, so a named instant could be wrong, and one step can cross several marks
# (`HALT_FORK_LABEL_TEMPLATE`). The wording is a placeholder while the interface
# is built (project owner, 2026-10-18).
STATUS_MARK_HALT_TEXT: Final = "Paused — stopped on your mark"
STATUS_RUNNING_TEXT: Final = "Running"
STATUS_FAILED_TEXT: Final = "Stopped — simulation error"
STATUS_SUPPORTED_LIMIT_TEXT: Final = "Stopped — supported run length reached"

# The three notice banners, in precedence order. The stopped-run wording says
# what the values *are* rather than warning about them. Rolling the failed
# step back is what made that possible (`PL-026`). Whether a step was rolled
# back is for the failure's own message to say, which the details under the
# banner show (`failure_details`), and `SimulationNumericalError`'s message does
# say it. The banner does not say it of every failure, because
# a setting that raised an exception (`PL-YK2V`) and a displayed value that the
# interface rejected (`PL-7DJK`) failed no step. The run-length wording does not
# reuse the failure's wording, because nothing failed and nothing was rolled
# back. Describing a correct model as a broken one is the safety defect that
# `CLAUDE.md` names (`PL-Y5WR`). The wording says why the limit exists, because
# a boundary given with no reason looks like an arbitrary restriction.
#
# Both failure wordings end with `{exit}`, which names the way out. Normally
# that is `RESET_EXIT_TEXT`, because Reset is the only way out of a stopped
# run. When Reset itself was refused, `refused_reset_exit` names the other way
# out instead. Sending a reader back to the control that was just refused
# would give an instruction that the screen already knows cannot be followed
# (`PL-M4M0`). The run-length wording ends with `{exit}` too. A refused Reset
# halts the run as a failure, and a failure outranks the limit, so the
# run-length banner never names the refused-Reset exit. Its exit changes only
# when a dial was moved on the stopped run, as the comment above
# `STOPPED_RUN_SETTING_EXIT_TEMPLATE` says.
RESET_EXIT_TEXT: Final = "Reset to start a new run."
FAILURE_NOTICE_TEMPLATE: Final = (
    "Simulation stopped — {failure_reason}. The values shown are the last completed step. {exit}"
)
# The failure banner after a step whose agent accounting failed its check, for a
# frame that drew. The core rolled the step back, so the readouts and the chart
# show the last completed step. The accounting panel shows the rejected step's
# verdict and totals instead, because the restored step passed its check
# (`PL-HF4B`). So this banner names the panel as the one exception to "the last
# completed step". The wording is a placeholder.
REJECTED_ACCOUNTING_NOTICE_TEMPLATE: Final = (
    "Simulation stopped — {failure_reason}. The values shown are the last completed step, "
    "except the agent accounting panel, which shows the rejected step. {exit}"
)
# The reasons a failure banner gives, one for each kind of failure that the
# simulator can tell apart (`failures.FailureKind`). The reason a run records
# is written for a developer: it names the exception's class beside its
# message (`halt_disposition`), and the accounting check's message prints every
# total in e-notation under its code name, such as
# `absolute_error=1.000000e+00 L`. So that message goes to the failure
# log (`run_view.log_failure`) and to the details under the banner
# (`failure_details`), and the user gets plain words. Each says what
# happened, as far as the kind shows it, and that it is a fault in the
# simulator and not a change in the patient. The banner's own exit says what to
# do next. An unexpected error says plainly that its cause is not known, rather
# than guess at one (`PL-XWCH` quotes the guidance). The wording is a
# placeholder.
FAULT_NOT_PATIENT_TEXT: Final = "This is a fault in the simulator, not a change in the patient"
# The controls and lines under a failure's banner that hold the details for a
# report (`failure_details`, `report_fault_text`). The wording is a
# placeholder.
SHOW_FAILURE_DETAILS_LABEL: Final = "Show details"
HIDE_FAILURE_DETAILS_LABEL: Final = "Hide details"
COPY_FAILURE_DETAILS_LABEL: Final = "Copy details"
FAILURE_LOG_NOT_KEPT_TEXT: Final = (
    "Failure log: none is kept this session, because the data folder could not be used"
)
REPORT_FAULT_TEMPLATE: Final = (
    "To report this fault, copy the details and paste them into a new issue on the "
    '<a href="{url}" style="color: {link_colour};">project\'s issue page</a>.'
)
REPORT_FAULT_NO_PAGE_TEXT: Final = (
    "To report this fault, copy the details and send them to the project's maintainers."
)
# What each kind of failure is, in the words a user reads. The banner adds
# `FAULT_NOT_PATIENT_TEXT` after it (`shown_failure_reason`). A refused Reset on
# a run that had already failed names its own kind without that sentence,
# because its way out already says that only a fault causes it
# (`refused_reset_exit`). The accounting check fails when the amounts are out
# of balance by more than rounding allows, which can be less than the 0.1 L the
# panel's amounts are shown to. So its words say what a failed check means,
# that agent was created or lost, and do not claim that the amounts on the
# panel fail to add up (`PL-TWZY`).
FAILURE_CAUSE_TEXTS: Final[Mapping[FailureKind, str]] = MappingProxyType(
    {
        FailureKind.ACCOUNTING: (
            "the agent accounting check failed: the rejected step created or lost anesthetic agent"
        ),
        FailureKind.NUMERICAL: (
            "the model produced a value it cannot hold, such as a negative amount of agent"
        ),
        FailureKind.CONFIGURATION: (
            "one part of the simulator gave another a value that it does not accept"
        ),
        FailureKind.EXECUTION: "the simulator could not continue the run safely",
        FailureKind.UNEXPECTED: (
            "an unexpected error occurred in the simulator, and its cause is not known"
        ),
    }
)
# The failure banner that `run_presentation.halted_run` gives before any frame of the
# stopped run has been drawn. At that point the chart and the readouts still show
# the frame drawn before the stop, which is not the step the run stopped at. So
# "the values shown are the last completed step" would be the stale-state
# misreading that the hazard table in `docs/VERIFICATION.md` names. The first frame that
# draws replaces this banner with `FAILURE_NOTICE_TEMPLATE`. Which
# of the two banners is shown is therefore decided by whether a frame drew, not
# guessed from the reason (`PL-7DJK`). A chart can still be withheld while the
# readouts are kept, for example a chart chosen during the halt at a window that
# no frame was kept for (`views._withholds`). So the banner speaks only of each
# chart that still has a plot, and the withheld chart says why it is empty. When
# every chart is withheld, `CHARTS_WITHHELD_UNDRAWN_FAILURE_NOTICE_TEMPLATE` is
# given instead (blind review of `PL-RF2S`, pass 3). The wording is a
# placeholder.
UNDRAWN_FAILURE_NOTICE_TEMPLATE: Final = (
    "Simulation stopped — {failure_reason}. No frame of the stopped run could be drawn: "
    "the readouts and every chart that still has a plot show the last frame drawn "
    "before it stopped. The run itself stands at its last completed step. {exit}"
)
# The failure banner for a halt when no frame has been drawn since the run started
# over after a Reset or an agent change. The last frame then belongs to the run
# before the restart. So `run_presentation.halted_run` withholds the readouts and their
# clock, and the banner says so rather than calling them the last frame drawn
# (adversarial review of `PL-J5GC`). The charts' frame belongs to the run before
# the restart too, so each chart withholds it and shows an empty plot
# (`run_presentation.shown_without_a_frame`, `PL-RF2S`). The wording is a
# placeholder.
STARTED_OVER_UNDRAWN_FAILURE_NOTICE_TEMPLATE: Final = (
    "Simulation stopped — {failure_reason}. No frame has been drawn since the run "
    "started over: the readouts and the charts are withheld, and the run itself stands "
    "at its last completed step. {exit}"
)
# The failure banner for a halt when no frame has been drawn for the runs the
# charts show now, although the run itself has not started over. A branch was
# taken, the reader chose a Workspace that shows other runs, no frame has been
# drawn at all, or the last frame showed the preview of a dial held at the
# halt. The readouts are still the run's last frame, but
# each chart withholds its frame, because that frame drew another set of runs
# (`run_presentation.kept_frames_match`, blind review of `PL-RF2S`). So the
# banner says that the charts are withheld rather than that they show the last
# frame. The wording is a placeholder.
CHARTS_WITHHELD_UNDRAWN_FAILURE_NOTICE_TEMPLATE: Final = (
    "Simulation stopped — {failure_reason}. No frame of the stopped run could be drawn: "
    "the readouts show the last frame drawn before it stopped, the charts are withheld, "
    "and the run itself stands at its last completed step. {exit}"
)
SUPPORTED_LIMIT_NOTICE_TEMPLATE: Final = (
    "Simulation stopped — this run reached the supported run length of {run_length}. "
    "This model leaves out metabolism, and its fat flow is uncertain. How far the "
    "slow part of the trace can stray from a patient grows as a run goes on, so the "
    "model is not claimed to represent a patient past this span. The values shown "
    "are the last completed step, inside the supported span. {exit}"
)
#: The banner a run shows in the last stretch before the supported run length. It is
#: drawn in the muted colour, as the stop it announces is, because nothing is wrong
#: with the run (`PL-H2K2`, `PL-0889`).
APPROACHING_LIMIT_NOTICE_TEMPLATE: Final = (
    "This run stops in {remaining} of simulated time, at the supported run length of {run_length}."
)
#: The least real time, in seconds, for which the approaching-limit banner is on
#: screen before the stop, at the fastest playback rate. WCAG 2.2 SC 2.2.1 (Timing
#: Adjustable) asks that a user be warned before a time limit expires and given at
#: least 20 seconds to act. Read from W3C's Understanding document for that criterion
#: on 2026-11-22. The run's limit is in simulated time, so the banner opens this many
#: real seconds before the stop at the fastest rate, and earlier in real time at every
#: slower rate.
APPROACHING_LIMIT_WARNING_REAL_S: Final = 20
#: How much simulated time before the supported run length the banner opens: the
#: real-time warning above, at the fastest playback rate offered. At 300x that is
#: 6,000 s, 1 h 40 min of simulated time.
APPROACHING_LIMIT_NOTICE_S: Final = APPROACHING_LIMIT_WARNING_REAL_S * max(
    rate.multiplier for rate in SUPPORTED_PLAYBACK_RATES
)
REFUSED_SETTING_TEMPLATE: Final = "Setting refused — {error}"
# A refused branch changed no setting, so its notice does not say "Setting
# refused" (`PL-3JTH`).
REFUSED_BRANCH_TEMPLATE: Final = "Branch not opened — {error}"
# A refused preview changes no setting either, and the thumb is still held, so its
# notice opens by saying that the preview was not drawn. It takes the form of the
# two notices above, because NUREG-0700 Rev. 3 guideline 2.7.1-2 asks that "System
# messages should use consistent grammatical construction". The release still
# applies the held value, so the notice ends by saying so rather than that the run
# is unchanged. Guideline 2.7.3-1 asks that "an error message should state the
# error and possible subsequent operations" (`PL-412F`).
REFUSED_PREVIEW_TEMPLATE: Final = (
    "Preview not drawn — {error}. Releasing the dial still applies the new setting."
)
# A setting refused for lying outside a limit is named to the user by its control's
# label, with the value asked for and the limit, as the stopped run's refusal names
# its control (`SimulationController._refuse_a_setting_on_a_stopped_run`). The core's
# own message names the setting's field in the code, for a developer (`PL-8QFW`).
REFUSED_SETTING_OUTSIDE_RANGE_TEMPLATE: Final = (
    "the {setting} setting cannot be {requested}, because {reason}"
)
#: Why each limit refused the setting, in the user's words. `lowest` and `highest`
#: are the limit's two ends, written exactly (`_exact_setting`).
SETTING_LIMIT_REASONS: Final[Mapping[SettingLimit, str]] = MappingProxyType(
    {
        SettingLimit.SUPPORTED_INPUT_RANGE: "the model covers only {lowest} to {highest}",
        SettingLimit.PERCENT: "a concentration can only be from {lowest} to {highest}",
        SettingLimit.VAPORIZER_MAXIMUM: "this agent's vaporizer delivers at most {highest}",
        SettingLimit.MACHINE_RANGE: (
            "this anesthesia machine sets a flow only from {lowest} to {highest}"
        ),
    }
)
REFUSED_SETTING_NOTICE_TEMPLATE: Final = (
    "{refused}. The simulation is unchanged and still running its previous setting."
)

# The way out that a stopped run's banner names after a dial was moved on that run.
# The controller refuses every setting on a stopped run, so the dial springs back
# to the setting the run holds
# (`SimulationController._refuse_a_setting_on_a_stopped_run`, `PL-3B34`). Without a
# sentence to explain it, the refusal would look like a dial that moves and returns
# for no stated reason. A stopped run outranks a refused setting, so the refusal is
# stated inside the stopped run's banner, in place of its exit. That run's own way
# out to a new setting follows the refusal.
#
# The two stopped states have different ways out (project owner, 2026-10-26). The
# supported run length is the expected end of a long run, so its way out can be a
# branch opened at an earlier instant. Such a branch can take a different setting,
# and each of its dials starts at what it was set to at that instant
# (`_branch_from`). A failure is a fault, so Reset stays its way out. Reset keeps
# every setting (`SimulationController.reset`), and the banner says so, because a
# reader could expect Reset to restore the defaults. When Reset itself was refused,
# the banner already names closing the application, which is the only way out left.
# So the refusal follows that exit and adds no other. A refusal made while the run
# was still going is kept until a setting is accepted, as on a running run, so it
# can appear here too. The way out that it is given is still correct. The wording
# is a placeholder.
#
# The banner names a branch only while a branch can be taken from this run. No
# branch can be taken while two runs are compared, because the branch control is
# locked then (`fork_offer`). Nor can one be taken from a run whose `fork_refusal`
# gives a reason. Naming the branch there would send the reader to a control that
# the screen has replaced with its lock caption. So the run at the supported run
# length then names only Reset, as a failed run does (blind review of `PL-3B34`).
STOPPED_RUN_SETTING_EXIT_TEMPLATE: Final = "{refused}. {way_out}"
SUPPORTED_LIMIT_SETTING_WAY_OUT_TEXT: Final = (
    "To try a different setting, branch at an earlier instant, where each dial starts at "
    "what it was set to then, or Reset to start a new run, which keeps every setting."
)
RESET_SETTING_WAY_OUT_TEXT: Final = "Reset to start a new run, which keeps every setting."

# The way out when Reset itself was refused, in the two wordings that
# `refused_reset_exit` chooses between. Reset is refused only for a settings
# record whose tissue flows do not sum to the cardiac output. Every flow is
# computed from the output (`PL-HQF5`), so a new output scales them all by one
# factor and the sum still disagrees. Only a perfusion fraction written past
# its guard (`PL-Z0HN`) can build that record, and no shipped code writes one.
# So no setting can repair the refusal, and the banner says so rather than
# naming a dial. Until `PL-01GY` the banner said to change the setting that the
# refusal names, and that advice stopped being true with `PL-HQF5`.
#
# The way out that the banner names is to close and reopen the application,
# because that is available on every run. A new case is not. A new case is
# started from the agent selector, which a comparison replaces with
# `COMPARING_AGENT_LOCK_TEXT` and which a branch does not have (`PL-TFX5`). If
# a refusal that a setting can repair is ever added to that record, this text
# must change with it.
#
# Closing the application can clear what Copy details copied. On X11 an
# application serves the clipboard it owns (Qt 6, `QClipboard`, "Notes for X11
# Users"), and an owner that exits with no clipboard manager running "should
# simply exit" (freedesktop.org, Clipboard Manager Specification, section
# "Responsibilities of clipboard owners"; both read 2026-11-27). So the text
# says to paste the details before closing, as NUREG-0700 Rev. 3 guideline
# 2.7.5-2, p. 2-89, asks: "For conditions that may require special user
# attention to protect against information loss, an explicit alert or advisory
# message, or both, should prompt appropriate user action" (`PL-PYWF`).
#
# Which wording states the refusal depends on the banner's reason. On a run
# that had not failed, or whose recorded failure is this same refusal, the
# halt's reason is the refusal, so the exit refers to it. On a run that had
# failed for something else, the controller keeps that earlier reason
# (`SimulationController.fail`). The exit then states the refusal itself, in
# the form in which the failure line gives a reason (`PL-M4M0`).
REFUSED_RESET_EXIT_TEMPLATE: Final = "Reset was refused for this reason. {way_out}"
REFUSED_RESET_AFTER_FAILURE_EXIT_TEMPLATE: Final = "Reset was refused — {reason}. {way_out}"
# The way out names the two buttons in the order the user presses them,
# because the copy button stays hidden until the details are shown
# (`FailureDetails` in `app/qt_widgets.py`). It reads their labels, so a
# renamed button renames them here too.
REFUSED_RESET_WAY_OUT_TEXT: Final = (
    "No setting can repair this, because only a fault in the simulator causes it. "
    f"To keep the failure details, use {SHOW_FAILURE_DETAILS_LABEL}, then "
    f"{COPY_FAILURE_DETAILS_LABEL}, and paste them elsewhere before closing, "
    "because closing the application can clear the copy. "
    "Then close and reopen the application to start a new run."
)

# What the chart says when a reader has unchecked every compartment. A plot
# with all six missing is a blank panel. A blank panel looks like a display
# that has failed, not like one showing what it was asked to show.
NO_TRACES_SHOWN_TEXT: Final = (
    "No compartment traces are shown. Check a compartment above to draw it — "
    "the readouts and the run itself are unaffected."
)

#: Where a notice in a chart's Area sends the reader for a compartment's value.
#: This build draws one window, and the compartment readouts are in the region
#: above every Area of it, however the Areas are laid out. So both notices that
#: name the readouts use this one phrase (`PL-4246`). A second window would
#: carry no compartment readouts (`docs/INTERFACE.md` § "What this list
#: requires once the layout is the reader's"), so a chart in one could not use
#: this phrase.
READOUTS_PLACE_TEXT: Final = "the readouts above"

# Shown when a drawn trace goes above the top of the plot, naming the traces
# that do. A setting in common use exceeds the standard top
# (`CHART_AXIS_TOP_MAC`): sevoflurane's 8% dial setting is 4.44 MAC at age 40. A trace
# clipped at the ceiling draws as a horizontal line, which is what a plateau
# looks like. Growing the axis to fit was rejected, because it would redraw the
# curve at a smaller height partway through the induction it is being used to
# teach.
OFF_SCALE_NOTICE_TEMPLATE: Final = (
    "Above the top of the plot: {compartments}. The axis stops at {top} and these "
    "traces are cut off there — their values are in " + READOUTS_PLACE_TEXT + ", which are "
    "not clipped."
)

# Added to the off-scale notice when a preview goes above the top of the plot.
# The readouts give the run's values, not the preview's, and the hover never
# shows a preview's values. So this sentence states each clipped prediction's
# highest value in the window. Dragging sevoflurane's dial toward 8% is the
# commonest preview. Without this sentence, the clipped curve could be
# mistaken for a predicted plateau at the top of the axis (`PL-5B1N`).
PREVIEW_OFF_SCALE_NOTICE_TEMPLATE: Final = (
    "The preview goes above the top of the plot and is cut off at {top}. "
    "Highest predicted values in view: {peaks}."
)

# The control-change panel. It lists the newest change first, because it is a
# fixed panel beside a chart rather than a scrolling history. It lists a
# limited number of changes and says how many it left out.
NO_CONTROL_CHANGES_TEXT: Final = "No settings changed yet in this run."
# No record gives the reason for 12. The number first appears in the change
# that recorded the control-input timeline (`PL-DR1Z`, #301, 2026-09-04), in
# the Flet interface's `app/simulation_view.py`, and the PySide6 port (#588)
# kept it. That change's commit message, its item and its documents say what
# the limit does, but not why it is 12 (traced for `PL-N8G4`). The panel lists
# the newest changes and counts the rest. So raising the limit lists more
# changes for the reader to scroll through. The panel sits in the record
# column of the part of the page that is always on screen, outside the Areas.
# That column is held as tall as the run rows beside it, and each run's list
# scrolls inside its own panel (`PL-HF1B`). Lowering the limit moves more
# changes into the count.
MAX_LISTED_ADJUSTMENTS: Final = 12
CONTROL_TIMELINE_HEADING: Final = "Control changes"
CONTROL_TIMELINE_CAPTION: Final = (
    "What was changed during this run, most recent first. Settings only — not a measurement."
)
CHANGE_COUNT_TEMPLATE: Final = "{count} change(s)"
UNLISTED_CHANGES_TEMPLATE: Final = "{count} earlier change(s) not listed"
TIMELINE_OVERFLOW_JOINER: Final = "; "

# Shown on a chart whose limited pool of drawn marks could not mark every
# control change inside its window. Each chart has its own window (`PL-L59K`),
# so the count belongs to the chart. It used to appear in the run's
# control-change panel, when every chart drew the same window. The wording is
# a placeholder.
UNMARKED_CHANGES_TEMPLATE: Final = "{count} control change(s) in this window not marked"

# The bookmark panel. It has two headings and two empty-list lines rather than
# one of each, because the two collections are listed separately (`PL-LPLD`).
# A shared "nothing marked yet" would leave a reader working out which of the
# two collections it was about.
#
# The panel lists the oldest mark first. That is the opposite of the
# control-change list above, and it is not an inconsistency. The control-change
# list is a record of what has happened, and the newest entry is the one a
# reader is looking for. This panel is a set of open questions that a reader
# adds to and scans. An entry that moves when another is added is one the
# reader has to find again.
#
# **The headings name the two kinds and say nothing else.** A caption here
# would explain the domain to a clinician, which `.claude/rules/ui-reader.md`
# rules out. Each row's own units and words state what the row asserts.
TIME_BOOKMARK_HEADING: Final = "Time bookmarks"
MAC_TARGET_HEADING: Final = "MAC targets"
NO_TIME_BOOKMARKS_TEXT: Final = "None marked"
NO_MAC_TARGETS_TEXT: Final = "None set"

# The separator between a mark's value and the name the user gave it. An
# en dash, which `tools/glyph_check.py` records as rendered.
MARK_LABEL_JOINER: Final = " – "

# What a row says about how far the run has got with the mark it lists
# (`PL-CTD7`). This is conditional text rather than standing text, which is
# the distinction `.claude/rules/ui-reader.md` draws. A row for a mark that the
# run can still reach says nothing at all. So the words appear on exactly the
# rows whose state a reader would otherwise have to infer from silence.
#
# **The three negative answers are worded differently on purpose.** "Not
# reached" alone would be true of all three. It would tell a user that a
# bookmark before this branch's fork might still arrive if they kept running,
# which it cannot. `bookmarks.MarkStanding` gives the argument, and
# `CLAUDE.md`'s safety-critical standard is what rules out that
# plausible-looking answer. `NOT_REACHED_WITHIN_CAP` names the run length
# rather than a number of hours, so the figure is written in one place only:
# `core/supported_ranges.py` and `docs/INTERFACE.md` § "Supported run length".
#
# **The failed run's words name the failure, for the same reason that the
# cap's words name the cap** (`PL-N3N5`). Each says what the mark went
# unreached *within* or *before*. So the row says why nothing more will happen
# to the mark, rather than leaving a reader to find the reason on the run's
# own panel. The words also reuse that panel's phrase. So a screen read at one
# instant says "Stopped - simulation error" above and "not reached before the
# simulation error" beside the mark, instead of giving two accounts of one
# stop. The words do not attach the run's transport state to the mark. "Not
# reached" is the claim, and the failure is the moment it stopped being open
# to revision. `MARK_STILL_RUNNING_TEXT` below was introduced for that same
# distinction.
#
# **"passed" and "reached" are two words because they are two claims**
# (`PL-3K9B`). "Passed" says where the run's clock is relative to a marked
# instant. So it is worked out again every time the row is drawn, and it stays
# true across anything that moves the clock. "Reached" says what the run did
# at a marked height, which no clock orders. Wording them alike would put the
# same word on a row that a rewind can revoke and on a row that it cannot.
# That is the plausible-looking answer again, and a user reading two
# branches side by side is reading exactly that difference.
MARK_STANDING_JOINER: Final = " · "
MARK_STANDING_TEXT: Final[Mapping[MarkStanding, str]] = MappingProxyType(
    {
        MarkStanding.STILL_RUNNING: "",
        MarkStanding.PASSED: "passed",
        MarkStanding.REACHED: "reached",
        MarkStanding.NOT_REACHED_WITHIN_CAP: "not reached within the supported run length",
        MarkStanding.BEFORE_THIS_BRANCH: "before this branch opened",
        MarkStanding.NOT_REACHED_BEFORE_FAILURE: "not reached before the simulation error",
    }
)

# The same answers, each attributed to its run, for a row on which the
# displayed runs disagree (`PL-LHBY`, `PL-4KZD`). The *set* of marks is shared
# across the runs on screen. `SimulationView._apply_to_every_run` is the only
# code that writes one. But a mark's *standing* is computed from each run's
# own clock, its own opening instant and its own halts. So two managements of
# one case can give different answers for the same mark, and both answers are
# news about the case.
#
# **`STILL_RUNNING` is the one entry that gains a word here, and only here.**
# On an unattributed row, silence is unambiguous: nothing has happened to the
# mark on the one run whose answer the row states. Beside a named run that has
# something to say, silence would look as if the second run had no answer,
# rather than as if its answer were "not yet". The row would then leave a
# reader to infer from an absence exactly what `.claude/rules/ui-reader.md`
# reserves conditional text for. The word costs nothing on the rows that stay
# unattributed, because those rows never use this table.
#
# **The word describes the mark, not the run, and "still running" was the
# wrong word for it.** `MARK_ATTRIBUTION_TEMPLATE` puts the run's name first,
# which makes the run the grammatical subject. For `passed`, `reached` and the
# cap, the phrase still reads as that run's relation to the mark. But "still
# running" reads as the run's transport state. This interface already uses
# that vocabulary for transport state. `STATUS_RUNNING_TEXT`,
# `STATUS_PAUSED_TEXT` and `STATUS_FAILED_TEXT` are a few lines above, and
# `REFUSED_SETTING_NOTICE_TEMPLATE` uses the phrase in exactly that sense. So
# `Run 2 still running` contradicted the word on Run 2's own panel whenever
# that run was paused, which is most of the time a user reads this row. It
# also claimed something that `MarkStanding.STILL_RUNNING` does not support.
# That standing says the run *can still reach* the mark and has not yet, which
# is a statement about the mark rather than about the clock. "Not yet" is that
# statement, and it is true of a paused run and a running one alike.
#
# The table is derived from `MARK_STANDING_TEXT` rather than written out
# again. So the four words that the two tables share cannot come to disagree
# about what a standing is called on one row and on the row beside it.
MARK_STILL_RUNNING_TEXT: Final = "not yet"
MARK_STANDING_COMPARED_TEXT: Final[Mapping[MarkStanding, str]] = MappingProxyType(
    {**MARK_STANDING_TEXT, MarkStanding.STILL_RUNNING: MARK_STILL_RUNNING_TEXT}
)
# One run's answer, labelled with the run it belongs to. The run's name comes
# first, because a reader scans a row of disagreeing answers down its run
# names.
MARK_ATTRIBUTION_TEMPLATE: Final = "{run} {said}"

# The marks editor's own words. They are field labels rather than
# sentences, which is the form in which `.claude/rules/ui-reader.md` asks a
# specialist reader's screen to carry its meaning. "Compartment" and "Height"
# say what the control sets. What a height on a given compartment does and
# does not assert is stated in `docs/INTERFACE.md` § "MAC multiples as a display
# unit", not in a paragraph beside the form.
# The branch control's words follow the marks' words, for the same reason.
# Both offer instants of the *case* rather than of either run, so both are
# panels of the dashboard rather than of a `RunView` (`docs/ARCHITECTURE.md`
# § "Where new code belongs"). "From" labels the instant at which the branch
# opens. The heading names the mechanism and says nothing else, under the same
# rule as the mark headings.
FORK_HEADING: Final = "Branch"
#: What the branch View shows where the dashboard was handed loose runs and
#: holds no case. A control there could only refuse, so none is drawn, and the
#: View says why its rectangle is empty (`PL-9YPR`). The wording is a placeholder.
NO_CASE_TO_BRANCH_TEXT: Final = "These runs belong to no case, so no branch can be opened."
# This is conditional text, so it earns a sentence where standing interface
# text would not (`.claude/rules/ui-reader.md`). It states the rule and the
# way out of it, because a refused control that does not say how to lift the
# refusal is a dead end rather than a mode. The display is capped at two runs
# and there is no run selector yet (`ROADMAP.md` § "Explicitly out of scope for
# v0.5.0"). So a second branch would have to replace the shown one silently,
# while the first branch stayed live inside `BranchedCase`.
#
# **It is a template, because the way out is a button and a reader finds a
# button by the words on it** (`PL-WG73`). The text used to say "Reset the
# case", but the only Reset in `app/` is labelled `RESET_LABEL` and nothing on
# screen says "case". So the way out named a control that this interface does
# not have. A comparison draws two Reset buttons, one per run, and they do
# opposite things. The trunk's Reset rebuilds the case. The branch's Reset
# returns that run to its own fork and leaves this lock in place, and it is
# the one a user reaches for, because the branch is the run they are trying
# to end. So the sentence names both. `comparing_fork_lock_text` fills it from
# the runs' names and `RESET_LABEL`, which stops an instruction and the
# control it names from drifting apart again.
#
# The text states what the trunk's Reset costs as well as what it ends.
# Sending a user to a control that discards every run, without saying so,
# would be the same defect with the consequence hidden instead of the label.
COMPARING_FORK_LOCK_TEMPLATE: Final = (
    "One comparison at a time. {trunk}'s {reset} ends it and starts the case over; "
    "{branch}'s {reset} only returns {branch} to where it branched."
)
# A Workspace pinned to one run draws no comparison: its Views show the pinned
# run alone, or nothing while that run is not open (`PL-WV9K` Q6). A branch
# taken there opens in no Area of it, so the lock caption, which is the text
# the Branch View shows at once in place of the control that was pressed,
# also says why the comparison is not drawn and how to draw it (`PL-YQ5J`).
# It reports the result of the press without moving the user, which WCAG
# 2.2 Success Criterion 4.1.3 calls a status message. Nothing announces it to
# a screen reader yet: screen-reader support is planned and not yet built
# (`docs/INTERFACE.md`), so the caption meets the criterion's intent for a
# sighted reader only. The dashboard does not switch to another Workspace
# instead. Pressing "Branch" asks for a branch, not for a different
# Workspace, and the WCAG Understanding document for Success Criterion 3.2.2
# holds a change of context appropriate "only when it is clear that such a
# change will happen in response to the user's action". The sentence is
# worked out from the pin on every tick, so it goes as soon as the user
# unpins the Workspace or switches to another one.
COMPARISON_PINNED_AWAY_TEMPLATE: Final = (
    "This Workspace is pinned to {pinned}, so it does not draw this comparison. "
    "Unpin it from the Workspace's tab to compare {trunk} and {branch}."
)
# The same pin, said before a branch is taken (`PL-RXR8`). The template above
# reports the pin after the press, once the one comparison slot is filled. A
# branch cannot be undone short of the trunk's Reset, which starts the case
# over, so the Branch View also says it before the press, while only one run is
# open. Telling a reader what an action will do before they act is what
# Vermeulen et al. (CHI 2013, doi:10.1145/2470654.2466255) call feedforward,
# and the Nielsen Norman Group's "Preventing User Errors: Avoiding Conscious
# Mistakes" asks for a preview of the result "wherever possible". It is a
# state caption in `MUTED`, like the lock, and not a warning: nothing is wrong
# yet, and the press stays offered. The wording is a placeholder.
PINNED_FORK_NOTICE_TEMPLATE: Final = (
    "This Workspace is pinned to {pinned}, so it will not draw a branch taken here "
    "beside it. Unpin it from the Workspace's tab to compare the two runs here."
)
FORK_NOTHING_SELECTED_TEXT: Final = "Select an instant to branch at"

# The fork where the paused trunk stands. It is a second control rather than
# a row in the selector above. A user who pauses can branch there, and that
# is the default action (project owner, 2026-10-12: "if I pause I should be
# able to branch from there too"), because it is the one control labelled with
# the instant the user is looking at. The selector remains the way to
# branch anywhere else. The fork is a button rather than an entry selected by
# default (project owner, 2026-10-12, ratified, over a row at the top of the
# selector selected by default, `PL-Y2SL`; and `PL-TYWQ`, project owner
# 2026-09-21, ratified, over the single list that grows a row while the run is
# halted).
#
# The two offers last for different lengths of time. An entry in the selector
# stays available for a branch until the case itself changes. This button is
# valid only while the trunk stays where it stopped. A row that appeared and
# then disappeared would change the selector's contents under a reader who had
# looked away. That is the stale-state case that
# `.claude/rules/expert-review.md` names, and a reader could detect it only by
# comparing against a remembered list. A default selection that jumped to the
# row would also move a choice the reader had made. A control that is either
# there or not can be noticed on sight.
#
# The instant shown is the clock's, which is where the branch opens. The clock
# advances in whole steps, so the label and the fork are the same number
# (`HereForkPoint`).
HERE_FORK_LABEL_TEMPLATE: Final = f"{HERE_FORK_NAME}: {{instant}}"
# The same control's words when a mark stopped the trunk where it stands.
#
# **The instant is the halt's, not the mark's, and the wording keeps the two
# apart.** A mark that lies inside a step halts the run at the end of that
# step. So the instant a user marked and the instant at which the branch
# opens are, in general, not the same number
# (`SimulationController.resumed_here`). The label therefore attaches its
# instant to "Branch here", which is what this control will do. It applies
# "stopped on your mark" to the halt rather than to the number, so it never
# states where a mark is. Labelling the control with the marked instant
# instead would put the wrong label on a correct value, which `CLAUDE.md`'s
# safety-critical standard counts as a failure of the value.
#
# One label serves a crossing of either kind. A step can cross a marked
# instant and a marked height at once, and "your mark" is true of both. The
# bookmark panel's rows state which marks were crossed. Repeating that here
# would put two accounts of one stop on screen.
#
# **These exact words** (project owner, 2026-09-21, ratified, over `PL-TYWQ`'s
# own illustrative "Branch at your mark - 0:45", which asserts where the mark
# *is* and so is wrong whenever a mark lies inside a step). The decision was
# ratified rather than specified, so ordinary evidence can reopen it, such as
# a user who misreads it or a measurement. But a rewrite must not
# reintroduce the wording it was chosen over.
HALT_FORK_LABEL_TEMPLATE: Final = f"{HERE_FORK_NAME}: {{instant}}, stopped on your mark"
# A time bookmark that the trunk has passed, as an entry in the selector beside
# the control events (`PL-W4XQ`). **The instant is `MarkForkPoint.fork_s`, the
# instant at which the branch opens, never the value typed for the mark.** A
# mark that lies inside a step is reached at the end of the step, so the two
# instants differ. The entry names the instant the branch will use, for the
# same reason as the halt label above. "On your mark" follows that ratified
# label's wording, "stopped on your mark". Like that label, it refers to the
# mark without stating where the mark is. It does not carry the mark's name
# either, for the reason the halt label gives: the bookmark panel's rows state
# which marks are meant. These words are the project owner's (2026-10-12,
# ratified, over a label stating the mark's typed instant or its name). So a
# change to them is proposed to the project owner, not made directly.
MARK_FORK_LABEL_TEMPLATE: Final = "{instant}, on your mark"

# Each range below holds every value that one part of a clock reading can take
# within the supported run. Hours are less than the run length in hours, and
# minutes and seconds are less than 60. Each range starts at 1, so that a
# reading built from them includes every part (`PL-NC0D`).
_CLOCK_HOURS: Final = range(1, int(MAXIMUM_ELAPSED_SIMULATION_TIME_S // SECONDS_PER_HOUR))
_CLOCK_MINUTES: Final = range(1, int(MINUTES_PER_HOUR))
_CLOCK_SECONDS: Final = range(1, int(SECONDS_PER_MINUTE))


def displayed_run_count(run_count: int) -> RunCount:
    """Build `run_count` as a `RunCount`, checking that the dashboard can display that many runs.

    `RunCount` refuses anything that is not a count of at least one run. The
    upper bound, `MAX_DISPLAYED_RUNS`, is a limit of the dashboard rather than
    of counts in general, so this function checks it. It is the one place that
    states the range. The dashboard calls it for the runs it is built with and
    for each run it adds. A compartment selection calls it for the runs it is
    drawn across (`PL-F9TC`).

    Raises:
        TypeError: If `run_count` is a `bool` or not an `int` (`RunCount`).
        ValueError: If `run_count` is not between 1 and `MAX_DISPLAYED_RUNS`.
            The message gives that range and the count refused.
    """

    out_of_range = ValueError(
        f"the dashboard displays 1 to {MAX_DISPLAYED_RUNS} runs at once, not {run_count}"
    )

    try:
        count = RunCount(run_count)
    except ValueError as error:
        raise out_of_range from error

    if count > MAX_DISPLAYED_RUNS:
        raise out_of_range

    return count


def widest_fork_point_label(advance_px: Callable[[str], int]) -> str:
    """Return the branch selector's widest possible entry, as `advance_px` measures it.

    The selector has a fixed width, so it reserves the width of its widest
    entry once, when it is built (`PL-NC0D`). The entry for a mark that the
    run has passed is the widest kind of entry. It is the clock reading of a
    control event, followed by the words of `MARK_FORK_LABEL_TEMPLATE`. The
    widest clock reading is found by measuring, not by counting characters.
    A proportional font gives its digits different widths, so 23h59m59s,
    the reading at the last step, is not the widest. Hours, minutes and
    seconds vary independently. So the widest value of each, put together,
    is the widest reading that `format_elapsed` writes within the supported
    run.

    Args:
        advance_px: How wide a string draws in the selector's font, in
            pixels.

    Returns:
        The entry for a mark passed at the instant with the widest reading.
    """

    # Each part is measured as `format_elapsed` writes it alone, so the
    # measured text follows the clock's own format (`PL-G84G`).
    hours = max(_CLOCK_HOURS, key=lambda hour: advance_px(format_elapsed(hour * SECONDS_PER_HOUR)))
    minutes = max(
        _CLOCK_MINUTES, key=lambda minute: advance_px(format_elapsed(minute * SECONDS_PER_MINUTE))
    )
    seconds = max(_CLOCK_SECONDS, key=lambda second: advance_px(format_elapsed(second)))
    instant_s = hours * SECONDS_PER_HOUR + minutes * SECONDS_PER_MINUTE + seconds

    return MARK_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(instant_s))


# The headings of the marks editor's two forms. Each names the one action
# its form does, so a reader does not take a form for a second copy of the
# list above it (`PL-G1JM`). The wording is a placeholder (`PL-CHX0`).
TIME_MARK_KIND: Final = "time bookmark"
TARGET_MARK_KIND: Final = "MAC target"
TIME_FORM_HEADING: Final = f"Add a {TIME_MARK_KIND}"
TARGET_FORM_HEADING: Final = f"Add a {TARGET_MARK_KIND}"
ADD_MARK_LABEL: Final = "Add"
# The label of the button on each listed mark. The button's accessible name
# adds the mark's own text, so a screen reader says which mark it removes.
REMOVE_MARK_LABEL: Final = "Remove"
# The line under a list after a mark is removed from it, and the button that
# puts the mark back (`PL-5GX4`). The button's accessible name names the mark,
# as the Remove button's does.
REMOVED_MARK_TEMPLATE: Final = "Removed: {mark}"
UNDO_REMOVAL_LABEL: Final = "Undo"
UNDO_REMOVAL_NAME_TEMPLATE: Final = "Undo removing {mark}"
INSTANT_FIELD_LABEL: Final = "Instant"
COMPARTMENT_FIELD_LABEL: Final = "Compartment"
HEIGHT_FIELD_LABEL: Final = "Height"
MARK_NAME_FIELD_LABEL: Final = "Name"


def control_name(label: str, which: str | None) -> str:
    """Return what a screen reader calls a control whose label is shown on another control too.

    The name is the label, then which control it is, such as "Name, MAC target"
    for one of the marks editor's two "Name" fields (`PL-RK9Z`), or "Playback,
    Run 2" while two runs are compared (`PL-YSFX`). The W3C's ARIA Authoring
    Practices Guide asks for "unique names for elements with the same role
    unless the elements are actually identical", and for names that are concise
    (in its section "Composing Effective and User-friendly Accessible Names"). The name
    starts with the label, which the Understanding document for WCAG 2.2 SC
    2.5.3 (Label in Name) calls best practice.

    Args:
        label: The label shown beside or on the control.
        which: What tells this control from the others that show the same
            label, such as a run's name or a View's title, or None where no
            other control shows it.

    Returns:
        The label alone when `which` is None.
    """

    return label if which is None else f"{label}, {which}"


MARK_NAME_PLACEHOLDER: Final = "Optional"
# The unit in which an instant is entered, and the resolution of the entry.
# The unit is seconds rather than the compound form the clock shows, because a
# spin box states one unit and the compound form has three. The editor
# restates the entered value in the compound form beside the control, so no
# reader has to convert between them. The entry is a whole number of seconds,
# because a run stands only on whole seconds (`core/simulation_step.py`).
INSTANT_ENTRY_SUFFIX: Final = " s"
# The upper bound of the height control before an agent has been named. Every
# shipped agent's vaporizer reaches at least this multiple of its own 1 MAC
# for the reference adult. The least is desflurane's, 18% / 6.6% = 2.73 MAC.
# So this value is a lower bound on the real limit rather than a guess at it,
# and `test_every_agent_reaches_the_default_target_ceiling` holds it there.
# It was 3.0 while desflurane's MAC was 6.0% (`PL-LBVN`).
# `MarkEditor.set_reachable_height` replaces it with the running agent's
# own limit the first time a frame is drawn.
DEFAULT_MAXIMUM_TARGET_MAC: Final = 2.5


def height_entry_maximum_mac(reachable_mac: float) -> float:
    """Return the highest height that the height control may offer, in multiples of MAC.

    The control holds `MAC_DISPLAY_DECIMALS` decimals, and a spin box rounds
    its maximum to the nearest value it can show. Rounding to nearest can
    round up. Desflurane's 18% dial over its 6.6% MAC is 2.727 MAC, and the
    control would then offer 2.73, a target that no desflurane run can cross
    (`PL-LBVN`). This function rounds down instead, so every height the
    control offers is one that the running agent can reach.

    Rounding can leave a quotient just below the hundredth that it equals, so
    the count of hundredths allows `WHOLE_COUNT_TOLERANCE` before it is
    rounded down. Without the allowance, a reachable height of exactly
    4.17 MAC that arrived as 4.169999999999999 would lose a hundredth.

    Args:
        reachable_mac: The agent's maximum delivered concentration as a
            multiple of its own 1 MAC.

    Returns:
        `reachable_mac` rounded down to the control's resolution.
    """

    scale = DECIMAL_BASE**MAC_DISPLAY_DECIMALS
    return floor(reachable_mac * scale + WHOLE_COUNT_TOLERANCE) / scale


# Names the substance that the six readouts belong to (`PL-TCD1`). It is a
# label rather than a sentence. It says "Modelled" rather than giving a bare
# agent name, because the hazard on this row is a reader comparing these
# values with a monitor.
COMPARTMENT_SUBSTANCE_TEMPLATE: Final = "Modelled concentrations: {agent}"

# The delivered dial's setting on the transport row, in the two units that the
# dial prints it in. It says that the value is the vaporizer's setting, so a
# user cannot read it as a modelled concentration, or as the inspired one
# at low fresh gas flow (`PL-NWTM`, `PL-M4WT`).
DELIVERED_LINE_TEMPLATE: Final = f"{VAPORIZER_LABEL} {{value}} ({{secondary}})"

# What the confirmation says before a new case replaces a recorded one, in
# the order a reader meets it: why this is a new case at all, what is about
# to be lost (`formatting.format_case_discard_warning`, per case), and what
# survives. `NEW_CASE_CARRYOVER_TEMPLATE` is a claim about
# `SimulationController.set_agent`, and it has to stay true as that method
# changes. It deliberately names only three of the four settings that carry
# over (`PL-0Q1T`). The circuit volume carries over too, but it is not a
# setting the reader chose. Listed among the sliders, it looked like a slider
# that had gone missing.
NEW_CASE_TITLE_TEMPLATE: Final = "Start a new {agent} case?"
NEW_CASE_IS_NOT_A_VIEW_TEXT: Final = (
    "Changing agent starts a new case. This model does not simulate switching "
    "between volatile agents, so a run cannot be continued under a different one."
)
NEW_CASE_CARRYOVER_TEMPLATE: Final = (
    "Fresh gas flow, alveolar ventilation and cardiac output carry over. "
    f"The {{agent}} {VAPORIZER_LABEL.lower()} starts at that agent's own 1 MAC."
)
# Both buttons name their outcome rather than answering yes or no. The button
# that declines is the *default*: it is filled, and it comes last. So the
# press a reader makes without reading is the one that keeps their case.
KEEP_CURRENT_CASE_TEMPLATE: Final = "Keep the {agent} case"
START_NEW_CASE_TEMPLATE: Final = "Discard and start {agent}"

# What the confirmation says before the trunk's Reset discards a branch
# holding work (`PL-W5WX`). It is built the way the new-case question is:
# why the branch goes too, what is lost (`formatting.format_branch_discard_warning`,
# per branch), and what the trunk keeps. `TRUNK_RESET_KEEPS_TEMPLATE` is a
# claim about `SimulationController.reset`, which keeps the settings and the
# bookmarks, and the text has to stay true as that method changes. The
# buttons name their outcomes, and the button that keeps the branches is the
# default, as on the new-case question.
TRUNK_RESET_TITLE_TEMPLATE: Final = "{reset} {trunk} and discard {branches}?"
TRUNK_RESET_ENDS_BRANCHES_TEMPLATE: Final = (
    "{trunk}'s {reset} starts the case over, and a branch cannot outlive the run it was taken from."
)
TRUNK_RESET_KEEPS_TEMPLATE: Final = (
    "{trunk} goes back to induction with its settings and bookmarks kept."
)
TRUNK_RESET_DISCARD_TEMPLATE: Final = "{reset} and discard {branches}"
KEEP_BRANCHES_TEMPLATE: Final = "Keep {branches}"

# While a run is going, the agent selector is *replaced* by a chip rather than
# greyed out. A disabled control would repaint the agent's identity colour in
# a theme grey, at the one moment when every number beside it depends on the
# agent (`PL-61WW`). The caption says "running" rather than "this case",
# because that is what is true: the selector returns on Pause.
RUNNING_AGENT_LOCK_TEXT: Final = "Locked while running"
# The other two reasons why the chip replaces the selector. A branch carries
# the agent of the case it continues, and `SimulationController.set_agent`
# refuses a branch outright (`PL-TFX5`). So a branch's selector is not locked
# but absent, and the caption says what is true of it rather than what a Pause
# would undo. While two runs are compared, the trunk's selector *would* be
# obeyed, and that is the worse case. The switch succeeds, then
# `assemble_chart_frame` rejects a frame whose runs use two agents, and
# `_halt_every_run` fails both runs over an input to one of them (`PL-QRD1`).
# Refusing the switch before it reaches the controller follows
# `.claude/rules/expert-review.md`'s preference for an interface that prevents
# the error over one that reports it afterwards.
BRANCH_AGENT_LOCK_TEXT: Final = "Locked to the case"
COMPARING_AGENT_LOCK_TEXT: Final = "Locked while comparing"

# The agent-accounting panel. The amounts are litres of equivalent pure agent
# gas, which is not the unit in which anyone consumes agent, so the caption
# says so (`PL-TG60`). The residual line prints only the power of ten that the
# value is less than. An order of magnitude is the whole purpose of that line,
# and it is the only meaningful digit a rounding residual has (`PL-3PJZ`).
ACCOUNTING_HEADING: Final = "Agent accounting validation"
ACCOUNTING_VALID_TEXT: Final = "Valid"
ACCOUNTING_FAILED_TEXT: Final = "Validation failed"
ACCOUNTING_INITIAL_DETAIL_TEXT: Final = "No unaccounted agent detected."
ACCOUNTING_VALID_DETAIL_TEXT: Final = "The simulation still accounts for all delivered agent."
ACCOUNTING_FAILED_DETAIL_TEXT: Final = "The simulation has detected unaccounted agent."
# The detail line after a step whose accounting failed its check. That step was
# rolled back, and the panel shows its totals, the ones the check judged
# (`PL-HF4B`). The wording is a placeholder.
ACCOUNTING_REJECTED_DETAIL_TEXT: Final = (
    "A step failed this check and was rolled back. The amounts below are that step's."
)
# The detail line while the panel withholds what it last showed. The panel does so
# during a halt when no frame has been drawn since the run started over
# (`WITHHELD_ACCOUNTING`). The wording is a placeholder.
ACCOUNTING_WITHHELD_DETAIL_TEXT: Final = "No frame has been drawn since the run started over."
# The unit of every amount on the accounting panel, with the temperature and
# pressure the amounts are stated at (`PL-HQPF`). The amounts held in the body
# are at body temperature, and are stated at this condition so that the panel's
# amounts add up (`docs/MODEL.md` § "Units and symbols"). So the last two lines
# say that the stored amount reads high. The caption is four short lines rather
# than wrapped text, because Qt leaves a wrapped label's extra lines out of the
# panel's minimum size. Each line fits in the width the panel had before the
# condition was added, so the panel's column, and the plot beside it, keep
# their width. The wording is a placeholder, but the condition
# and its effect on the stored amount must be on screen. The unit's name is
# read from its `DisplayUnit` member (`PL-2TWX`).
_ACCOUNTED_UNIT_IN_FULL: Final = DisplayUnit.ACCOUNTED_AGENT_LITRES.recorded
ACCOUNTING_UNIT_CAPTION: Final = (
    f"{_ACCOUNTED_UNIT_IN_FULL[:1].upper()}{_ACCOUNTED_UNIT_IN_FULL[1:]},\n"
    f"at {REFERENCE_CONDITION_LABEL}.\n"
    f"{BODY_STORES_CONDITION_LINES}"
)
#: The names of the panel's four amount lines, in the order the panel shows them. The
#: residual is shown once, as "Unaccounted": the panel prints a residual only as the
#: power of ten it lies below, without its sign, so an absolute-error line would read
#: the same string (project owner, 2026-10-03, ratified, `PL-XFWG`).
ACCOUNTING_AMOUNT_NAMES: Final = ("Delivered", "Exhausted", "Stored", "Unaccounted")

# The transport row's labels, and the two selector captions beside it.
# The agent selector's caption is shown rather than given to a screen reader
# alone. On Linux and macOS, Qt takes what a selector is for only from a
# label shown beside it (`qt_widgets.label_control`, `PL-RK9Z`).
AGENT_SELECTOR_LABEL: Final = "Agent"
START_LABEL: Final = "Start"
PAUSE_LABEL: Final = "Pause"
RESET_LABEL: Final = "Reset"
PLAYBACK_LABEL: Final = "Playback"
TIME_BASE_LABEL: Final = "Time base"
# The label beside the control that sets the top of the compartment chart's
# axis. The control names the top in MAC, so the label says what it sets.
CHART_CEILING_LABEL: Final = "Axis top"
FIT_RUN_LABEL: Final = "Fit run"

# The chart panel's heading and its time-axis captions. The caption states
# the span actually drawn, because the width is a mode (`PL-012`). The same
# plot showing fifteen minutes and showing twelve hours makes two different
# claims about what a flat trace means. Under "Fit run" the caption says both
# that the whole run is drawn and how wide the plot had to be to draw it. The
# selector then names only the rule, and the caption is the only text that
# names the resulting width. The caption is written into the time axis's
# title.
CHART_HEADING: Final = "Agent concentration and relative partial pressure over time"
# The names the View chooser gives the three Views that draw against an axis
# (`view_registry.REGISTERED`). Each one's axis controls are named with its
# View's name too, because the others have controls with the same labels
# (`control_name`, `PL-YSFX`).
CONCENTRATION_VIEW_TITLE: Final = "Concentrations"
WASH_IN_VIEW_TITLE: Final = "Wash-in"
SCHEMATIC_VIEW_TITLE: Final = "Compartment schematic"
# What the chart's long description opens with. The W3C example of a chart's
# text alternative "identifies the type of chart" first (Understanding WCAG
# 2.2 SC 1.1.1, `PL-T9RB`).
CHART_TYPE_TEXT: Final = "Line chart."
# What a screen reader calls the box that holds each chart View's legend,
# which takes the focus so the keyboard can scroll it (`PL-RK9Z`).
CONCENTRATION_LEGEND_NAME: Final = "Concentration chart legend"
WASH_IN_LEGEND_NAME: Final = "Wash-in plot legend"
# What a screen reader calls the page that scrolls the Workspace tabs and their
# Areas, which takes the focus for the same reason (`PL-RK9Z`).
WORKSPACE_PAGE_NAME: Final = "Workspace"
# The time axis's title states the window after the axis's name, so the
# window takes no line of its own above the plot (`PL-K4CZ`). A narrow plot
# breaks the title after a comma, and so never between a span and its unit.
TIME_AXIS_TITLE: Final = "simulated time"
TIME_AXIS_TITLE_TEMPLATE: Final = f"{TIME_AXIS_TITLE}, {{window}}"
FITTED_TIME_AXIS_CAPTION_TEMPLATE: Final = "whole run so far, {span} shown"
CHOSEN_TIME_AXIS_CAPTION_TEMPLATE: Final = "{span} shown"
# While a setting is previewed, the window keeps its width and slides so that
# the run's reach sits at mid-plot (`chart_time_base.preview_window`). It then
# shows neither the whole run nor the newest stretch, so the caption says what
# it does show (`PL-5B1N`).
PREVIEW_TIME_AXIS_CAPTION_TEMPLATE: Final = "{span} shown, centred on now during the preview"
# A window the reader moved back holds still while the run goes on
# (`chart_time_base.held_window`). It then shows the past while every readout
# shows the present, so the axis title says it is not following the run, and
# a line above the plot says how far the run has gone past it (`PL-Z7LY`).
HELD_TIME_AXIS_CAPTION_TEMPLATE: Final = "{span} shown, held: not following the run"
# With one run on the chart, the line gives that run's time. With more, it
# names each run's time, because the runs stand at different instants and
# one time would be read as the run the reader is watching.
HELD_WINDOW_NOTICE_TEMPLATE: Final = "Showing {start} to {stop}. {now}"
HELD_ONE_RUN_NOW_TEMPLATE: Final = "The run is now at {now}."
HELD_RUNS_NOW_TEMPLATE: Final = "Now: {runs}."
HELD_RUN_NOW_TEMPLATE: Final = "{label} at {now}"
# The controls that move a chart's window. The arrows sit either side of the
# time-base selector, as a date picker's do, so a step reads as a step through
# time. Each also carries a name that a screen reader speaks and a tooltip
# says, because an arrow alone names no action. The button that ends a hold
# uses the axis title's own words for the state it returns to.
EARLIER_WINDOW_TEXT: Final = "\u25c0"
LATER_WINDOW_TEXT: Final = "\u25b6"
EARLIER_WINDOW_NAME: Final = "Show an earlier part of the run"
LATER_WINDOW_NAME: Final = "Show a later part of the run"
FOLLOW_RUN_TEXT: Final = "Follow the run"

# The wash-in section. It says that its values are modelled with
# `INTERPRETATION_DISCLAIMER_TEXT`, on a line of its own rather than at the end
# of a paragraph, where nobody reads it (`PL-F9TQ`, `PL-T8DF`).
WASH_IN_HEADING: Final = (
    f"Wash-in: {WASH_IN_RATIO_NAME}, alveolar as a fraction of the modelled circuit"
)
WASH_IN_DENOMINATOR_TEXT: Final = (
    f"{INSPIRED_FRACTION_NAME} = modelled circuit, not the vaporizer dial — a rise across a "
    "control mark can be the denominator moving, not uptake"
)
WASH_IN_TRACE_LEGEND_LABEL: Final = f"{WASH_IN_RATIO_NAME} (solid)"
# The reference line at which the ratio is 1. The legend adds how the line is
# drawn, and the plot's text alternative gives the reference alone.
EQUILIBRIUM_REFERENCE_TEXT: Final = (
    f"Equilibrium, {ALVEOLAR_FRACTION_NAME} = {INSPIRED_FRACTION_NAME}"
)
EQUILIBRIUM_LEGEND_LABEL: Final = f"{EQUILIBRIUM_REFERENCE_TEXT} (wide dash)"
CONTROL_MARK_LEGEND_LABEL: Final = "Control change (vertical, fine dash)"
#: The 1 MAC line's words, which its legend entry and the concentration
#: chart's text alternative both start with. `{reference}` is the line's value,
#: as `mac_reference_caption` writes it. The compartment the line is read
#: against is named from `run_series.COMPARTMENT_NAMES`, in lower case because
#: it sits inside a phrase (`PL-GRC6`).
_ONE_MAC_LINE_WORDS: Final = (
    "{reference}, reference adult (" + COMPARTMENT_NAMES[RecordedQuantity.ALVEOLAR].lower()
)
#: The 1 MAC line's legend words, so the value and the line's style are stated
#: once, in one entry (`PL-K4CZ`). Before the first frame `{reference}` is the
#: bare name, `ONE_MAC_LINE_LEGEND_NAME`.
ONE_MAC_LINE_LEGEND_TEMPLATE: Final = _ONE_MAC_LINE_WORDS + ", wide dash)"
ONE_MAC_LINE_LEGEND_NAME: Final = "1 MAC"
#: The 1 MAC line's words in the concentration chart's text alternative: the
#: legend's words without how the line is drawn, as the wash-in plot's text
#: alternative gives its equilibrium line (`PL-596J`).
ONE_MAC_LINE_SPOKEN_TEMPLATE: Final = _ONE_MAC_LINE_WORDS + ")"
#: The MAC-awake band's legend words: the band's values, as
#: `mac_awake_caption` writes them, that they are a population's, and the
#: trace that the band is read against (`PL-90Y6`, `PL-K4CZ`). Before the
#: first frame `{reference}` is the bare name, `MAC_AWAKE_BAND_LEGEND_NAME`.
#: The trace is named from `run_series.COMPARTMENT_NAMES`, so the band names
#: the compartment as its legend line does (`PL-GRC6`).
MAC_AWAKE_BAND_LEGEND_TEMPLATE: Final = (
    "{reference}; population, read against "
    + COMPARTMENT_NAMES[RecordedQuantity.VESSEL_RICH].lower()
    + " trace"
)
MAC_AWAKE_BAND_LEGEND_NAME: Final = "MAC-awake"
#: A compartment's legend words: its name and its line style, so the style can
#: be read without looking at the plot (`docs/INTERFACE.md` § "The six
#: compartment traces"). It is one template rather than an f-string at each
#: legend row. The compare-mode row has to say the same words as the checkbox
#: above it, or the two would describe one curve differently.
TRACE_LEGEND_LABEL_TEMPLATE: Final = "{label} ({line_style})"
#: What a run is called in text. `docs/INTERFACE.md` § "Minimum displayed outputs"
#: requires the run to be named in text, not shown only by colour or by
#: position. Colour is already used for the compartment, and position alone
#: fails a reader who has looked away and back.
#:
#: Runs are numbered by their identity rather than by where they are drawn
#: (`PL-7Z84`). A session numbers its runs in the order it places them and
#: never gives out a number twice. So a branch taken after an earlier branch
#: was dropped is "Run 3", never a second "Run 2". The reader must also be able
#: to find what the name refers to. A legend entry reading "Run 2" is only an
#: attribution if something else on screen also says "Run 2". That something
#: is the panel holding the settings that produced the run.
RUN_LABEL_TEMPLATE: Final = "Run {number}"
#: What a Workspace's pinned run is called when an earlier session of the
#: application placed it. Its number is left out, because a run that is open
#: now can carry the same number and is a different run (`PL-7H9X`).
EARLIER_SESSION_RUN_TEXT: Final = "a run from an earlier session"
#: One drawn trace's legend words while more than one run is shown: the
#: compartment's own words, then the run's. Every entry names both dimensions,
#: which is what `PL-8PSW` asks of a legend once a curve carries two.
COMPARED_TRACE_LEGEND_TEMPLATE: Final = "{trace}, {run}"
#: The caption on the compare-mode legend row. It says "Drawn" rather than
#: "Compartments", because the row above it already names the compartments and
#: is the control. This row lists the four curves actually on the plot.
COMPARED_TRACE_LEGEND_CAPTION: Final = "Drawn traces:"
#: One run's line in a column that the runs share, while more than one run is
#: drawn: the run's name, then the line. The run comes first here but last in
#: `COMPARED_TRACE_LEGEND_TEMPLATE`, and the difference matches what the reader
#: is scanning for. A legend is read by curve, so the compartment comes first
#: there and the run tells two entries for one compartment apart. These
#: columns stack one line per run, and each line opens with the same words,
#: such as "Above the top of the plot" or "Now: F_A/F_I". So the run is the
#: only thing that distinguishes the lines. A distinguishing word at the end of
#: a wrapped sentence is one the reader has to go looking for.
COMPARED_RUN_LINE_TEMPLATE: Final = "{run} — {line}"
#: One run's banner in the notice column that the runs share, while more than
#: one run is drawn. It uses a colon where `COMPARED_RUN_LINE_TEMPLATE` uses an
#: em dash. Every notice already opens with `label — detail`, as in
#: "Simulation stopped — ..." and "Setting refused — ...". A second em dash
#: would sit at a different level from the first. It would look like the
#: banner's own separator, with the run's name as the label. The colon limits
#: what follows to the run, which is the sense in which
#: `OFF_SCALE_NOTICE_TEMPLATE` and `COMPARED_TRACE_LEGEND_CAPTION` already use
#: it. The run comes first for the reason given at `COMPARED_RUN_LINE_TEMPLATE`,
#: not the reason given at `COMPARED_PANEL_HEADING_TEMPLATE`. These banners
#: stack wrapped sentences that open with identical words. They are not short
#: headings whose two ends are both read at once.
COMPARED_RUN_NOTICE_TEMPLATE: Final = "{run}: {notice}"
#: One run's panel heading in a column that the runs share: the panel's own
#: words, then the run's. The run comes last here but first in
#: `COMPARED_RUN_LINE_TEMPLATE`, and the two choices do not conflict. This is
#: the legend's case, not the shared-line case. The sidebar stacks whole
#: panels, and a reader finds each one by the kind of record it holds. So the
#: kind comes first, exactly as the compartment does in
#: `COMPARED_TRACE_LEGEND_TEMPLATE`, and the run tells two panels of one kind
#: apart. The argument for putting the run first on a shared line depends on a
#: wrapped sentence whose end a reader has to go looking for. A heading is one
#: short bold line, and both its ends are read at once.
#:
#: It uses an em dash rather than the colon that
#: `COMPARTMENT_SUBSTANCE_TEMPLATE` uses. "Agent accounting validation: Run 2"
#: reads as if "Run 2" were the validation's *result*. The result is the word
#: on the line directly below (`ACCOUNTING_VALID_TEXT`).
COMPARED_PANEL_HEADING_TEMPLATE: Final = "{heading} — {run}"
#: The fork's legend words. The fork mark is vertical like a control mark, but
#: solid where a control mark is dashed. That pair of visual channels tells
#: them apart, and the words state both, so the mark can be identified without
#: looking at the plot.
BRANCH_POINT_LEGEND_LABEL: Final = "Branch point (vertical, solid)"
#: The word that opens a preview's label in the plot (`preview_label`). It
#: names the kind of value first, so a reader who sees only the start of the
#: label still knows the curves beside it did not happen (`PL-5B1N`).
PREVIEW_LABEL_SUBJECT: Final = "Preview"
#: Shown while the two-compartment cap is keeping traces off the chart. It
#: names the limit, what the limit removed, and where those values can still
#: be read. The last part matters because
#: `docs/INTERFACE.md` § "Minimum displayed outputs" makes the readouts what keeps
#: a capped compartment on the display.
#: A reader told only that a trace is gone has been told half of the story.
COMPARED_CAP_NOTICE_TEMPLATE: Final = (
    "Two runs are shown, so the chart draws at most {cap} compartments at once. "
    "Every compartment's value is in " + READOUTS_PLACE_TEXT + ", for both runs."
)
# What the wash-in plot is showing at this instant. A trace that stops has
# to say which condition stopped it: an inspired concentration too low to
# divide by, alveolar ventilation at zero, or an alveolar concentration above
# the inspired. A reader shown only an empty plot could not tell them apart.
# Each sentence names the condition and not a cause, and all three use one
# construction, the condition and then "so" and the verdict (NUREG-0700 Rev. 3,
# guideline 2.7.1-2, p. 2-85, `PL-8R2Y`). The inspired
# concentration also falls that low during a washout, while the patient still
# holds agent (`PL-P3ZL`). The sentence for a ratio above 1 does not say that
# the patient returns agent or that the run is past equilibrium, for the same
# reason (`PL-7PBB`). At zero ventilation no agent moves between the circuit
# and the lungs, so the ratio is not a wash-in fraction on either side of 1,
# and the plot draws nothing (rule 3 of `app/wash_in.py`, `PL-49D5`). The
# sentence for zero ventilation speaks of the state shown, not of the setting.
# A paused run can stand on a state reached during apnoea while its control
# already shows ventilation restored, and both stay true until the next step.
WASH_IN_STATE_TEMPLATE: Final = "Now: " + WASH_IN_RATIO_NAME + " = {ratio}"
WASH_IN_NOT_DEFINED_TEXT: Final = (
    "The inspired concentration is too low to divide by, so the ratio is not defined."
)
WASH_IN_ELIMINATION_TEXT: Final = (
    "Alveolar exceeds inspired, so the ratio is not a wash-in fraction."
)
WASH_IN_VENTILATION_STOPPED_TEXT: Final = (
    "Alveolar ventilation was zero over the last simulated second, "
    "so the ratio is not a wash-in fraction."
)
WASH_IN_UNDRAWN_SUFFIX_TEMPLATE: Final = " ({count} earlier stretch(es) not drawn)"

# The two standing statements. The first says what the tool is *for*. The
# second, placed beside the readouts themselves, says how to read a number on
# it (`PL-2K1R`). The compartments this simulator exists to display are the
# ones no monitor shows. So a reader has no measured value to check a trace
# against, and the polish of the display suggests more accuracy than there
# is. The first is drawn once, as a line across the foot of the window,
# because a repeated disclaimer stops being read. The second is drawn on the
# readout section's heading row, and in the headings of the compartment
# schematic View and the agent cost View.
USE_DISCLAIMER_TEXT: Final = (
    "Educational simulation only. This idealized model is not a clinical prediction, "
    "monitoring, or dosing tool."
)
INTERPRETATION_DISCLAIMER_TEXT: Final = "Model outputs — not measurements."

# The column counts that the readout row may use, widest first. The row
# reflows to the largest count whose panels fit its width, instead of
# squeezing a label (`PL-8M05`). The widest count fits all seven panels. These
# counts are the steps of the ladder. The widths at which the row steps down
# are not recorded here, because they depend on the rendering font. `PL-8M05`
# recorded the Flet build's breakpoints as a measurement rendered at Flet's
# sizes. The port derives the breakpoints for the same ladder from the font
# it actually renders with. So no pixel figure is asserted here that a
# different font or a HiDPI scale would make wrong.
READOUT_ROW_LADDER: Final[tuple[int, ...]] = (7, 4, 2, 1)


class Emphasis(StrEnum):
    """How a status word is drawn: its colour role, named without naming a colour.

    The widget layer maps `MUTED` to `theme.MUTED`, `ACCENT` to
    `theme.ACCENT_TEXT` and `WARNING` to `theme.WARNING`. Naming only the role
    here keeps every colour token in `theme.py`. `WARNING` is used for a
    failure, and deliberately not for the stop at the supported limit.
    Colouring a correct model's declared boundary as a fault teaches a reader
    to distrust a sound number. It also uses up the one signal this interface
    has for a real fault.
    """

    MUTED = "muted"
    ACCENT = "accent"
    WARNING = "warning"


@dataclass(frozen=True, slots=True)
class StatusWord:
    """One word stating the run's state, and the emphasis it is drawn with."""

    text: str
    emphasis: Emphasis


def status_word(status: RunStatus, *, stopped_on_mark: bool) -> StatusWord:
    """Return the run's status word: failure, then supported limit, then running, then paused.

    A failure outranks the supported run length. One run can carry both: it
    stops at the supported run length, and an error then arrives from
    something other than a step or a setting, such as a frame that the
    dashboard could not draw. The error is then the run's last event and the
    more serious statement, so the word reports it. The row of a mark that
    such a run did not reach reports the run length, which is why the mark was
    not reached (`bookmarks._mac_target_standing`, `PL-3DHK`). The word for a
    paused run that a mark stopped says that a mark stopped it, so that the
    stop is not mistaken for the user's own Pause
    (`STATUS_MARK_HALT_TEXT`, `PL-QBQX`).

    Args:
        status: The run's status this tick, either a `RunStatus` or the
            snapshot carrying one. `run_presentation.halted_run` passes a
            `RunStatus`, which is read without building any compartment
            value. So a halt is worded from facts that cannot fail
            (`PL-7DJK`).
        stopped_on_mark: Whether a step of the run halted it on a mark
            (`SimulationSnapshot.stopped_on_mark`). A branch at its fork
            carries the parent step's halt record and is not stopped on a
            mark. It is a separate argument because a `RunStatus` does not
            carry the halt record, which is worked out from the run's stored
            states (`SimulationController._halt_crossing`).

    Returns:
        The word and its emphasis.
    """

    if status.failure_reason is not None:
        return StatusWord(STATUS_FAILED_TEXT, Emphasis.WARNING)

    if status.supported_limit_reason is not None:
        return StatusWord(STATUS_SUPPORTED_LIMIT_TEXT, Emphasis.MUTED)

    if status.is_running:
        return StatusWord(STATUS_RUNNING_TEXT, Emphasis.ACCENT)

    if stopped_on_mark:
        return StatusWord(STATUS_MARK_HALT_TEXT, Emphasis.MUTED)

    return StatusWord(STATUS_PAUSED_TEXT, Emphasis.MUTED)


@dataclass(frozen=True, slots=True)
class ReadoutPanel:
    """The fixed part of one readout panel: what it shows, and so its name and gloss.

    A compartment's panel reads its name and gloss from `run_series`'s records
    by its compartment, so the readout names a compartment as the chart's
    legend, the schematic and the mark editor do (`PL-GRC6`).

    Attributes:
        quantity: The compartment the panel shows, or None for the clock.
    """

    quantity: RecordedQuantity | None

    @property
    def name(self) -> str:
        """The modelled quantity, in the model's own terms, or the clock's name."""

        quantity = self.quantity
        return CLOCK_PANEL_NAME if quantity is None else COMPARTMENT_NAMES[quantity]

    @property
    def qualifier(self) -> str | None:
        """What a clinician would compare the quantity against, or None.

        It is None for the clock and for a compartment that nothing measured
        corresponds to. It is drawn smaller than the name because it is the
        weaker claim of the two. The compartment is what the model computes,
        and the measurement is what a clinician would compare it with. Type
        of equal size would present them as two names for one quantity
        (`PL-NV9W`, `PL-8M05`).
        """

        quantity = self.quantity
        return None if quantity is None else COMPARTMENT_GLOSSES[quantity]

    @property
    def is_clock(self) -> bool:
        """Whether this is the clock's panel.

        This is the one place that asks which panel is the clock. A second
        panel with no compartment, or a clock given one, then changes the
        answer everywhere at once (`PL-J791`).
        """

        return self.quantity is None

    def compartment(self) -> RecordedQuantity:
        """Return the compartment this panel shows.

        Raises:
            ValueError: This is the clock's panel, which shows no compartment.
        """

        quantity = self.quantity
        if quantity is None:
            raise ValueError(f"the {self.name!r} panel is the clock and shows no compartment")
        return quantity


#: The clock panel's name.
CLOCK_PANEL_NAME: Final = "Simulated time"

# The seven panels in row order. Each compartment's name and gloss are read
# from `run_series.COMPARTMENT_NAMES` and `COMPARTMENT_GLOSSES`, which say why
# the alveolar gloss is "end-tidal-equivalent" and never "end-tidal".
READOUT_PANELS: Final[tuple[ReadoutPanel, ...]] = (
    ReadoutPanel(None),
    ReadoutPanel(RecordedQuantity.CIRCUIT),
    ReadoutPanel(RecordedQuantity.ALVEOLAR),
    ReadoutPanel(RecordedQuantity.MIXED_VENOUS),
    ReadoutPanel(RecordedQuantity.VESSEL_RICH),
    ReadoutPanel(RecordedQuantity.MUSCLE),
    ReadoutPanel(RecordedQuantity.FAT),
)

#: Each panel that shows a compartment, in row order (`PL-J791`).
COMPARTMENT_PANELS: Final[tuple[ReadoutPanel, ...]] = tuple(
    panel for panel in READOUT_PANELS if not panel.is_clock
)


def clock_playback_line(
    playback_rate: PlaybackRate, delivered_fraction: float | None = None
) -> str:
    """Return the clock panel's second line, the rate at which the run is played.

    Every readout row builds the line here, live or withheld, so the two cannot
    word it differently (`PL-J791`). The line states the set rate. While the
    computer delivers less of it than `playback.PACE_DISCLOSED_BELOW`,
    the line also names the rate delivered (`PL-2NYN`).

    Args:
        playback_rate: The set rate.
        delivered_fraction: The fraction of the set rate that the run is
            delivering, as `playback.TickPace.disclosed_fraction` returns it,
            or None when the line states only the set rate.

    Raises:
        ValueError: As `formatting.format_delivered_playback_rate` raises it.
    """

    if delivered_fraction is None:
        return format_playback_rate(playback_rate.multiplier)

    return format_delivered_playback_rate(playback_rate.multiplier, delivered_fraction)


@dataclass(frozen=True, slots=True)
class Readout:
    """One readout panel's four lines, as drawn this tick.

    Attributes:
        name: The panel's name line.
        qualifier: Its gloss line, or `EMPTY_METRIC_QUALIFIER` where the
            panel has none, so the line keeps its height.
        value: The reading with its unit: the clock in compound form, or a
            compartment as a percent of one atmosphere.
        secondary: The second line under the value. On a compartment panel
            it is the compartment as a multiple of the running agent's 1 MAC.
            On the clock panel it is the playback rate. Both units are shown
            at once rather than behind a selector, because a selector would
            make the unit a mode. The rate is drawn at every rate, including
            1x, so a reader never has to take a blank line to mean real time
            (`PL-SN2C`).
        panel: The panel these lines are drawn on, which says whether they
            are modelled.
    """

    name: str
    qualifier: str
    value: str
    secondary: str
    panel: ReadoutPanel

    @property
    def modelled(self) -> bool:
        """Whether the readings are model outputs: true for a compartment, false for the clock."""

        return not self.panel.is_clock


#: How a compartment's reading is named for assistive technology. A screen
#: reader that reads one line of a panel on its own then still says which
#: compartment it belongs to and that it is modelled (`PL-N5JB`). A panel's
#: gloss, such as "inspired" for the circuit, follows its name, because it says
#: which measured value the reading corresponds to.
SPOKEN_MODELLED_READING_TEMPLATE: Final = "{name}, modelled: {reading}"
#: How the clock's reading is named for assistive technology.
SPOKEN_READING_TEMPLATE: Final = "{name}: {reading}"
#: How a reading is named while runs are compared, so it says which run it is.
SPOKEN_RUN_READING_TEMPLATE: Final = "{run}, {spoken}"


def spoken_reading(readout: Readout, reading: str, run_name: str | None) -> str:
    """Return the name that assistive technology is given for one line of a readout panel.

    A screen reader can reach a panel's value or its second line on its own,
    away from the panel's name above it. So each line is named with the
    panel's name and gloss, whether it is modelled and, while runs are
    compared, the run, all taken from the strings the panel shows
    (`PL-N5JB`). A withheld reading, which the screen shows as a dash, is
    said in words (`SPOKEN_WITHHELD_READINGS`).

    Args:
        readout: The panel's four lines as drawn this tick.
        reading: The line being named, `readout.value` or `readout.secondary`.
        run_name: The run's name while runs are compared, or `None` for a lone
            run (`dashboard_frame.run_label`).

    Returns:
        The name, such as "Alveolar, end-tidal-equivalent, modelled: 1.20%".
    """

    template = SPOKEN_MODELLED_READING_TEMPLATE if readout.modelled else SPOKEN_READING_TEMPLATE
    gloss = readout.panel.qualifier
    name = readout.name if gloss is None else f"{readout.name}, {gloss}"
    spoken = template.format(name=name, reading=SPOKEN_WITHHELD_READINGS.get(reading, reading))

    if run_name is None:
        return spoken

    return SPOKEN_RUN_READING_TEMPLATE.format(run=run_name, spoken=spoken)


def compartment_fraction(snapshot: SimulationSnapshot, quantity: RecordedQuantity) -> Fraction:
    """Return the snapshot field that one readout panel shows.

    Raises:
        KeyError: If `quantity` is not one of the six compartments that the
            readout row shows. `RecordedQuantity.WASH_IN_RATIO` has its own
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
    """Build the seven readouts from one snapshot, in `READOUT_PANELS` order.

    Every MAC line divides by this snapshot's own MAC, which is read once.
    So a frame can never pair one agent's concentration with another agent's
    MAC.

    Args:
        snapshot: The run's state this tick.
        playback_rate: The rate at which the run is played. It is a view
            setting. It is drawn on the clock panel, because a rate is a mode
            and the clock is where it would be misread.

    Returns:
        One `Readout` per panel.

    Raises:
        ValueError: If the snapshot's elapsed time is negative or not finite
            (`format_elapsed`).
        TypeError: If its `agent_mac_percent` was not built as a
            `MacPercent` (`format_mac_multiple`).
    """

    mac_percent = snapshot.agent_mac_percent
    panels: list[Readout] = []

    for panel in READOUT_PANELS:
        qualifier = panel.qualifier if panel.qualifier is not None else EMPTY_METRIC_QUALIFIER

        if panel.is_clock:
            value = format_elapsed(snapshot.elapsed_s)
            secondary = clock_playback_line(playback_rate)
        else:
            fraction = compartment_fraction(snapshot, panel.compartment())
            value = format_percent(fraction)
            secondary = format_mac_multiple(fraction, mac_percent)

        panels.append(Readout(panel.name, qualifier, value, secondary, panel))

    return tuple(panels)


# The widest string that each readout column can show, so a panel can reserve
# its width once instead of moving as a value changes length (`PL-3355`).
# The value line is the clock's reading just before the supported run length,
# which has every part of the compound form. The second line is the longest
# clock line at any set rate, counting the form that names a delivered rate at
# every whole percent from 1 to 96 and the form for a rate below 1%
# (`PL-2NYN`). A percent readout and a MAC multiple are both shorter than these
# at every value the dial can reach. The strings are chosen by character count
# from the formatters' own extremes, and the widget measures the chosen string
# in its font.
WIDEST_READOUT_VALUE: Final = format_elapsed(MAXIMUM_ELAPSED_SIMULATION_TIME_S - 1)
WIDEST_READOUT_SECONDARY: Final = max(
    (
        clock_playback_line(rate, delivered_fraction)
        for rate in SUPPORTED_PLAYBACK_RATES
        for delivered_fraction in (None, *(percent / 100 for percent in range(1, 97)), 0.001)
    ),
    key=len,
)
#: The widest strings a compartment column can show: the percent at a whole
#: atmosphere, and that fraction as a multiple of the smallest 1 MAC any
#: shipped agent has for the reference adult, since the smallest divisor
#: prints the most digits.
WIDEST_COMPARTMENT_VALUE: Final = format_percent(Fraction(1.0))
WIDEST_COMPARTMENT_SECONDARY: Final = max(
    (
        format_mac_multiple(
            Fraction(1.0),
            mac_for_patient(
                load_agent_parameters(agent_id), load_reference_adult_parameters()
            ).percent,
        )
        for agent_id in AGENT_DATA_FILENAMES
    ),
    key=len,
)
#: The two lines that a readout card shows instead of its values during a halt when no
#: frame has been drawn since the run started over. The card was last written for the
#: run before the Reset or the agent change. After an agent change, its percent is the
#: old agent's concentration, and its ×MAC multiple was divided by that agent's MAC.
#: The heading and the 1 MAC line above the cards already name the new agent
#: (`PL-6RJ0`, `PL-J5GC`). Each text keeps its unit, so the card still says which
#: value is missing. Each text is shorter than the widest string that its line
#: reserves, so the card does not resize.
WITHHELD_CONCENTRATION_TEXT: Final = f"\u2014{DisplayUnit.CONCENTRATION.label}"
WITHHELD_MAC_MULTIPLE_TEXT: Final = f"\u2014{MAC_UNIT_SUFFIX}"
#: The clock's value line during the same halt. The clock states the instant of
#: the cards beside it, so it is withheld with them. Until the adversarial review
#: of `PL-J5GC`, the clock showed the discarded run's instant beside a run standing
#: at its opening.
WITHHELD_ELAPSED_TIME_TEXT: Final = "\u2014"
#: The delivered line while a run's setting controls cannot be built. Without it,
#: the line would keep the setting of the run before a Reset or an agent change,
#: beside a 1 MAC line that already names the new agent (`PL-SV2Q`). Each value
#: keeps its unit, so the line still says which values are missing.
WITHHELD_DELIVERED_LINE_TEXT: Final = DELIVERED_LINE_TEMPLATE.format(
    value=WITHHELD_CONCENTRATION_TEXT, secondary=WITHHELD_MAC_MULTIPLE_TEXT
)
#: What the setting controls View shows for a run whose setting controls cannot
#: be built, in place of that run's four dials (`PL-SV2Q`). The wording is a
#: placeholder.
SETTING_CONTROLS_NOT_SHOWN_TEXT: Final = "This run's setting controls cannot be shown."
#: What a chart shows in place of its plot when its frame is withheld: the runs
#: it shows changed or started over, no frame was kept for its window or its
#: width, or the kept frame held a preview, and no frame can be drawn now
#: (`run_presentation.shown_without_a_frame`, `views._withholds`, `PL-RF2S`). The plot is empty, so
#: no trace of the discarded run and no line of another agent stays on it. The
#: wording is a placeholder.
WITHHELD_FRAME_TEXT: Final = "Nothing is plotted, because no frame could be drawn for this chart."
#: What the legend's 1 MAC and MAC-awake entries show while the chart's frame is
#: withheld. Both values are the agent's, and after an agent change the last
#: frame's are the old agent's.
WITHHELD_REFERENCE_TEXT: Final = WITHHELD_ELAPSED_TIME_TEXT
#: What assistive technology is told in place of each withheld readout line
#: (`spoken_reading`). On screen the dash says that the value is withheld by
#: how it looks, so a screen reader is told in words. The wording is a
#: placeholder.
SPOKEN_WITHHELD_READINGS: Final[Mapping[str, str]] = MappingProxyType(
    {
        WITHHELD_CONCENTRATION_TEXT: "percent not shown",
        WITHHELD_MAC_MULTIPLE_TEXT: "multiple of MAC not shown",
        WITHHELD_ELAPSED_TIME_TEXT: "not shown",
    }
)
#: The strings whose width each readout column reserves, in `READOUT_PANELS`
#: order. The clock column reserves its widest elapsed form and its playback
#: line. Every compartment column reserves the two strings above. Each column
#: reserves its own widest value rather than the clock's. That is what lets
#: seven panels fit across a laptop-wide row while no value can wrap away from
#: its unit (`PL-3355`, `PL-8M05`).
READOUT_RESERVATIONS: Final[tuple[tuple[str, str], ...]] = tuple(
    (WIDEST_READOUT_VALUE, WIDEST_READOUT_SECONDARY)
    if panel.is_clock
    else (WIDEST_COMPARTMENT_VALUE, WIDEST_COMPARTMENT_SECONDARY)
    for panel in READOUT_PANELS
)


def withheld_readouts(playback_rate: PlaybackRate) -> tuple[Readout, ...]:
    """Build the seven readouts with every value withheld, in `READOUT_PANELS` order.

    A halt shows these when the run has started over and no frame has been
    drawn since. `WITHHELD_CONCENTRATION_TEXT` says why. Each panel keeps its
    name and its gloss, so the row still says which values are missing. The
    clock keeps its playback line, because the rate is a setting of the view
    and does not belong to the run that was discarded.

    Args:
        playback_rate: The rate at which the run is played, as `readouts`
            takes it.

    Returns:
        One `Readout` per panel.
    """

    return tuple(
        Readout(
            panel.name,
            panel.qualifier if panel.qualifier is not None else EMPTY_METRIC_QUALIFIER,
            WITHHELD_ELAPSED_TIME_TEXT if panel.is_clock else WITHHELD_CONCENTRATION_TEXT,
            clock_playback_line(playback_rate) if panel.is_clock else WITHHELD_MAC_MULTIPLE_TEXT,
            panel,
        )
        for panel in READOUT_PANELS
    )


@dataclass(frozen=True, slots=True)
class ParameterControl:
    """The fixed part of one setting control, saying what it sets and how it is offered.

    Attributes:
        control: The setting that the control forwards to the controller.
        name: The setting's name. It is None where the name includes the agent;
            `format_delivered_label` then supplies the name on each tick.
        qualifier: Words that tell the setting apart from a different quantity
            that the name alone would suggest, or None where the name is
            unambiguous. Fresh gas flow has the qualifier "common gas outlet".
            "Fresh gas flow" alone is how a flowmeter bank is labelled, and a
            flowmeter reads only the carrier gas. In the model's mass balance,
            this setting is the whole stream leaving the vaporizer. The two
            differ by 22% at desflurane's 18% dial setting. That difference
            carries into the circuit time constant, which is what the wash-in
            curve shows (`PL-71CF`).
        decimals: The display resolution at which the slider steps, taken from
            `formatting.py`. So the value applied to the model is exactly the
            value printed above the slider (`PL-25KS`, decision D4).

    The range is not stored here. For two of the four controls, the range is
    instance state rather than a constant. The delivered dial's ceiling is the
    running agent's vaporizer maximum. The fresh gas flow's range is the model's
    envelope, narrowed by the mounted machine. So `setting_readouts` states every
    control's range in one table, and it reads those two ranges from the snapshot.
    """

    control: ControlInput
    name: str | None
    qualifier: str | None
    decimals: int

    @property
    def unit(self) -> str:
        """The label of the unit the slider's value is in.

        The label comes from the `DisplayUnit` member that
        `control_record.CONTROL_INPUT_DISPLAY_UNITS` gives this control. Each
        recorded change carries the recorded spelling of that same member. So the
        slider's label and the recorded unit cannot name different units
        (`PL-Q3G9`).
        """

        return CONTROL_INPUT_DISPLAY_UNITS[self.control].label


# The four controls in panel order.
PARAMETER_CONTROLS: Final[tuple[ParameterControl, ...]] = (
    ParameterControl(
        ControlInput.FRESH_GAS_FLOW, "Fresh gas flow", "common gas outlet", FLOW_DISPLAY_DECIMALS
    ),
    ParameterControl(ControlInput.DELIVERED, None, None, CONCENTRATION_DISPLAY_DECIMALS),
    ParameterControl(
        ControlInput.ALVEOLAR_VENTILATION, "Alveolar ventilation", None, FLOW_DISPLAY_DECIMALS
    ),
    ParameterControl(ControlInput.CARDIAC_OUTPUT, "Cardiac output", None, FLOW_DISPLAY_DECIMALS),
)


def _setting_words(
    control: ParameterControl, value: float, agent_display_name: str
) -> tuple[str, str]:
    """Return a control's name and a value's text, as the slider prints them.

    `setting_readouts` writes the slider from these words, and
    `preview_label` names a previewed value with them. So the label in the
    plot and the readout above the slider cannot word one setting two ways.

    Args:
        control: The control.
        value: The setting, in the control's own unit: litres per minute for
            a flow, and percent of one atmosphere for the dial.
        agent_display_name: The running agent, which names the dial.

    Returns:
        The control's name and the value's text.

    Raises:
        SimulationConfigurationError: If the dial's value is not a percent
            from 0 to 100 (`fraction_from_percent`).
    """

    name = control.name if control.name is not None else format_delivered_label(agent_display_name)

    return name, setting_value_text(control.control, value)


def setting_value_text(control: ControlInput, value: float) -> str:
    """Return a setting's value as the readout above its slider prints it, with its unit.

    The readout, the preview's label in the plot and the value a screen
    reader hears from the slider all take their text from here, so the three
    cannot word one setting two ways (`PL-9QY5`).

    Args:
        control: The setting.
        value: The setting, in the control's own unit: litres per minute for
            a flow, and percent of one atmosphere for the dial.

    Returns:
        The value and its unit, such as "1.80%" or "4.0 L/min".

    Raises:
        SimulationConfigurationError: If the dial's value is not a percent
            from 0 to 100 (`fraction_from_percent`).
    """

    if control is ControlInput.DELIVERED:
        return format_percent(
            fraction_from_percent(Percent(value, name="delivered_concentration_percent"))
        )

    return format_flow(value)


def preview_label(
    control: ControlInput, value: float, agent_display_name: str, run_name: str | None
) -> str:
    """Return the label a preview's region carries in the plot.

    A preview is a trajectory the run would take under a setting the user
    is dragging and has not applied (`PL-5B1N`). A screenshot taken during the
    drag must not be mistaken for a run that happened. So the plot says in
    words that it is a preview, as well as through the region and the thinner
    curves. The label names the control and the value tried, in the slider's
    own words (`_setting_words`), and says that the value is not applied.
    Where more than one run is drawn, it names the run too, because each run
    has its own controls.

    Args:
        control: The control being dragged.
        value: The value tried, in the control's own unit.
        agent_display_name: The running agent, which names the dial.
        run_name: The run's name while runs are compared, or `None` for a lone
            run (`RunPresentation.name`).

    Returns:
        The label, on one line.
    """

    entry = next(entry for entry in PARAMETER_CONTROLS if entry.control is control)
    name, value_text = _setting_words(entry, value, agent_display_name)
    subject = (
        PREVIEW_LABEL_SUBJECT if run_name is None else f"{run_name} {PREVIEW_LABEL_SUBJECT.lower()}"
    )

    return f"{subject}: {name} {value_text}, not applied"


@dataclass(frozen=True, slots=True)
class SettingReadout:
    """One setting control as drawn this tick: its range, its value and its text.

    Every slider is set from the snapshot on every tick, not left where the
    reader dragged it. A refused setting must not leave a control showing one
    value while the simulation runs at another, because the control displays
    model state as much as it accepts input. On a halt, the slider is set from
    `SimulationController.record()` first, for the same reason, because no
    frame may follow (`PL-85LJ`).

    Attributes:
        control: The setting that the control forwards.
        name: The name line.
        qualifier: The gloss line, or the empty string where there is none.
            No spacer is drawn for a setting with no gloss, so the four
            panels have unequal heights by design.
        unit: The unit of `value`.
        decimals: The display resolution at which the slider steps.
        minimum: The slider's lowest position, in `unit`: the lowest setting
            at the slider's resolution that the run accepts (`offered_range`).
        maximum: The slider's highest position, in `unit`: the highest such
            setting.
        value: The setting in force, in `unit`.
        value_text: The setting as the readout above the slider prints it.
        secondary: The same setting in the second display unit, or the empty
            string for a setting with one unit. For the delivered dial it is
            the setting as a multiple of the agent's 1 MAC. That lets a reader
            compare the one control they set with the traces it produces.
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


# The three flows whose opening value a profile states. Each entry gives the
# profile that states it and the `docs/INTERFACE.md` section that gives its range.
# Every flow that a slider sets is one of the slider's steps. So only an
# opening value can fall off the slider's grid, and `setting_readouts` rejects
# one that does (`PL-1KQ9`, `PL-96SQ`). The delivered dial is not listed here.
# Its setting is a fraction that is converted to percent, so comparing it
# exactly with a step would first need a rule for rounding that conversion.
_OPENING_SOURCES: Final[Mapping[ControlInput, tuple[str, str]]] = MappingProxyType(
    {
        ControlInput.FRESH_GAS_FLOW: (
            "machine profile",
            "The model's envelope and a machine's deliverable range are two claims",
        ),
        ControlInput.ALVEOLAR_VENTILATION: ("patient profile", "Supported input ranges"),
        ControlInput.CARDIAC_OUTPUT: ("patient profile", "Supported input ranges"),
    }
)


def setting_readouts(settings: RunSettings) -> tuple[SettingReadout, ...]:
    """Build the four setting controls from the settings in force, in `PARAMETER_CONTROLS` order.

    Args:
        settings: The agent and the four settings in force. This is either
            the snapshot that a frame drew from, or
            `SimulationController.record()` for a run whose snapshot is
            refused, so that no frame is drawn (`PL-85LJ`).

    Returns:
        One `SettingReadout` per control.

    Raises:
        TypeError: If `agent_mac_percent` was not built as a `MacPercent`
            (`format_mac_multiple`, on the delivered dial's MAC line).
        ValueError: If no step of a control's display resolution lies inside
            the range the run accepts for it (`offered_range`). A control
            that can offer no accepted setting then fails visibly, rather
            than offering a refused one. No shipped range causes this. A
            machine profile that declares a fresh gas flow range narrower
            than one step could cause it. Also raised if the fresh gas flow,
            alveolar ventilation or cardiac output in force is not one of the
            steps its slider offers.
            Every flow that a slider sets is a step, so only an opening flow
            stated by a machine or patient profile can cause this. The run
            is then rejected, rather than opened with the slider and its
            readout each showing a flow that the run does not have
            (`PL-1KQ9`, `PL-96SQ`, `PL-25KS` decision D4). No shipped
            profile causes it.
    """

    delivered = settings.delivered_partial_pressure_fraction
    # The range of values that the run accepts for each control, read on this tick.
    # The model's supported ranges come from `core/supported_ranges.py`. So the
    # interface offers only the values that the verification gates cover, and
    # nothing wider (`PL-0MLQ`). The fresh gas flow range is the model's range,
    # narrowed to the limits of the mounted machine. The circuit states that
    # narrower range (`PL-7CRY`). The vaporizer dial's maximum is the maximum of
    # the vaporizer for the agent that is running.
    accepted_ranges: dict[ControlInput, tuple[float, float]] = {
        ControlInput.FRESH_GAS_FLOW: settings.accepted_fresh_gas_flow_range_l_min,
        ControlInput.DELIVERED: (
            MIN_DELIVERED_CONCENTRATION_PERCENT,
            settings.max_delivered_concentration_percent,
        ),
        ControlInput.ALVEOLAR_VENTILATION: (
            MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
            MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
        ),
        ControlInput.CARDIAC_OUTPUT: (MINIMUM_CARDIAC_OUTPUT_L_MIN, MAXIMUM_CARDIAC_OUTPUT_L_MIN),
    }
    readouts: list[SettingReadout] = []

    for control in PARAMETER_CONTROLS:
        # Which settings field holds the value is `control_value`'s to say,
        # so this readout and the control's recorded changes read one field.
        value = control_value(settings, control.control)

        if control.control is ControlInput.DELIVERED:
            secondary = format_mac_multiple(delivered, settings.agent_mac_percent)
        else:
            secondary = ""

        name, value_text = _setting_words(control, value, settings.agent_display_name)

        accepted_minimum, accepted_maximum = accepted_ranges[control.control]
        offered = offered_range(accepted_minimum, accepted_maximum, control.decimals)

        if offered is None:
            raise ValueError(
                f"{name} can offer no setting: no {slider_value(1, control.decimals)} "
                f"{control.unit} step lies inside {accepted_minimum} to {accepted_maximum} "
                f'{control.unit}, the range the run accepts (docs/INTERFACE.md, "Supported '
                'input ranges")'
            )

        minimum, maximum = offered

        if control.control in _OPENING_SOURCES and not _is_offered_step(
            value, offered, control.decimals
        ):
            profile, section = _OPENING_SOURCES[control.control]
            raise ValueError(
                f"{name} is {value} {control.unit}, which the slider cannot show: it offers "
                f"{slider_value(1, control.decimals)} {control.unit} steps from {minimum} to "
                f"{maximum} {control.unit}, so a {profile} must open the run on one of "
                f'those steps (docs/INTERFACE.md, "{section}")'
            )

        readouts.append(
            SettingReadout(
                control=control.control,
                name=name,
                qualifier=control.qualifier if control.qualifier is not None else "",
                unit=control.unit,
                decimals=control.decimals,
                minimum=minimum,
                maximum=maximum,
                value=value,
                value_text=value_text,
                secondary=secondary,
            )
        )

    return tuple(readouts)


def _is_offered_step(value: float, offered: tuple[float, float], decimals: int) -> bool:
    """Whether a setting is one of the steps a slider offers, so the slider can show it.

    A step is compared as the value the slider emits for it, `slider_value`,
    so a setting that the slider wrote is always an offered step. The only
    setting that no slider wrote is an opening flow stated by a machine or
    patient profile
    (`PL-1KQ9`, `PL-96SQ`).

    Args:
        value: The setting in force, in the control's unit.
        offered: The slider's floor and ceiling, from `offered_range`.
        decimals: The control's `SettingReadout.decimals`.

    Returns:
        True where `value` is a step of the slider's resolution between its
        floor and its ceiling.
    """

    minimum, maximum = offered

    return (
        minimum <= value <= maximum
        and slider_value(slider_position(value, decimals), decimals) == value
    )


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

    return round(value * DECIMAL_BASE**decimals)


def slider_value(position: int, decimals: int) -> float:
    """Return the value that an integer slider position represents, inverting `slider_position`.

    Args:
        position: The slider's integer position.
        decimals: The control's `SettingReadout.decimals`.

    Returns:
        The setting, in the control's unit.
    """

    return position / DECIMAL_BASE**decimals


def offered_range(minimum: float, maximum: float, decimals: int) -> tuple[float, float] | None:
    """Return the lowest and highest steps that a slider stepping at `decimals` offers in a range.

    The range is closed. A slider steps at its display resolution
    (`slider_position`), so its lowest and highest positions are the steps
    nearest the range's ends, from inside the range. Rounding an end to the
    nearest step instead can land outside the range, on a setting that the run
    refuses. For example, a machine whose minimum is 0.25 L/min would be
    offered 0.2 L/min at one decimal (`PL-7CRY`). An end that is already a step
    is offered as that step. So a range declared in whole steps, as every
    shipped range is, is offered exactly. Each step is compared as the value
    that the slider emits for it, `slider_value`. So the comparison is the same
    one that the run's own guard makes on that value.

    Args:
        minimum: The lowest setting the run accepts, in the control's unit.
        maximum: The highest, in the same unit.
        decimals: The control's `SettingReadout.decimals`.

    Returns:
        The lowest and highest step inside the range, in the control's unit,
        or None where no step lies inside it at all.
    """

    lowest = slider_position(minimum, decimals)

    if slider_value(lowest, decimals) < minimum:
        lowest += 1

    highest = slider_position(maximum, decimals)

    if slider_value(highest, decimals) > maximum:
        highest -= 1

    if lowest > highest:
        return None

    return (slider_value(lowest, decimals), slider_value(highest, decimals))


@dataclass(frozen=True, slots=True)
class Transport:
    """Which transport controls a reader may use this tick.

    Attributes:
        start_enabled: False while running. Also false for a run that has
            failed or has reached the supported run length. Neither run can
            be resumed, only reset. A Start button that the controller would
            refuse is a control pretending to work.
        pause_enabled: True only while running.
        reset_enabled: Always true, because Reset is how every stopped state
            ends.
        selector_locked: Whether the agent chip replaces the agent selector.
            True while running, because choosing an agent discards the case.
            Also true on a branch and while two runs are compared, for the
            reasons that `selector_lock_reason` states.
        selector_lock_reason: What the chip says about why the selector is
            gone, or the empty string while the selector is shown. The reason
            is chosen here rather than in the widget layer. So the three
            reasons are written in one place, and a reader is never told
            "running" about a lock that a Pause will not lift.
    """

    start_enabled: bool
    pause_enabled: bool
    reset_enabled: bool
    selector_locked: bool
    selector_lock_reason: str


def transport(status: RunStatus, *, is_branch: bool = False, comparing: bool = False) -> Transport:
    """Return the transport enablement for one snapshot, and why its selector is locked.

    The three locks are ranked by how long they last, longest first. The chip
    has room for one reason, and a reader acts on that reason. A branch's
    selector never returns. A comparison's selector returns on Reset. A
    running run's selector returns on Pause. Naming the shortest-lasting lock
    that happens to apply would send a reader to Pause for a lock that Pause
    cannot lift.

    Args:
        status: The run's status this tick, either a `RunStatus` or the
            snapshot carrying one, as `status_word` takes it.
        is_branch: Whether this run was opened from another run
            (`SimulationController.opened_from`). A branch carries the agent
            of the case it continues, so `set_agent` refuses it outright. The
            selector would then be a control pretending to work.
        comparing: Whether more than one run is on the chart. The runs share
            one MAC axis and one set of clinical references. So a switch
            accepted here would be rejected a moment later by
            `chart_frame.assemble_chart_frame`, after the controller had
            already changed agent (`PL-QRD1`).

    Returns:
        Which controls are usable, and what the chip says when the selector
        is not one of them.
    """

    stopped = status.failure_reason is not None or status.supported_limit_reason is not None
    lock_reason = ""

    if is_branch:
        lock_reason = BRANCH_AGENT_LOCK_TEXT
    elif comparing:
        lock_reason = COMPARING_AGENT_LOCK_TEXT
    elif status.is_running:
        lock_reason = RUNNING_AGENT_LOCK_TEXT

    return Transport(
        start_enabled=not status.is_running and not stopped,
        pause_enabled=status.is_running,
        reset_enabled=True,
        selector_locked=bool(lock_reason),
        selector_lock_reason=lock_reason,
    )


def shown_failure_reason(status: RunStatus) -> str | None:
    """Return the reason that a failure banner shows the user, or None if the run has not failed.

    The banner gives the plain words for the kind of failure that the run
    recorded (`FAILURE_CAUSE_TEXTS`), never the exception's own message,
    which is written for a developer. The details under the banner give that
    message (`failure_details`). A controller keeps its first failure
    (`SimulationController.fail`), so a run shows the kind of the failure that
    stopped it.

    Args:
        status: The run's status, either a `RunStatus` or the snapshot
            carrying one.
    """

    if status.failure_kind is None:
        return None

    return f"{FAILURE_CAUSE_TEXTS[status.failure_kind]}. {FAULT_NOT_PATIENT_TEXT}"


def failure_details(
    status: RunStatus,
    failure_log: Path | None,
    *,
    run_name: str | None,
    refused_reset_reason: str | None,
) -> str | None:
    """Return the details that a failed run shows under its banner, or None if it has not failed.

    The banner gives the user plain words (`shown_failure_reason`). These
    details are for a report of the fault: the build, the run while two are
    drawn, the exception's type and message as the run recorded it, a refused
    Reset's own message, and the file that holds the traceback. Microsoft's
    guidance on error messages puts such detail behind a "Show details"
    control, and the Nielsen Norman Group shows error codes for diagnosis only
    (`PL-XWCH` quotes both). A run stopped at its supported run length did not
    fail, and has no details.

    The log's path is given from the home folder, as `~/...`. The report line
    asks the user to paste the details into a public issue, and the full
    path usually holds their login name.

    Args:
        status: The run's status, either a `RunStatus` or the snapshot
            carrying one.
        failure_log: The file the failure was logged to
            (`failures.failure_log_path`), or None where no file is kept.
        run_name: What the run is called while a second run is drawn, or None.
        refused_reset_reason: The message of the error with which a Reset was
            refused on this run, or None. A controller keeps its first failure,
            so a refusal after an earlier failure is otherwise named nowhere.
    """

    if status.failure_reason is None:
        return None

    lines = [f"{APP_DISPLAY_NAME} — {format_build_version()}"]

    if run_name is not None:
        lines.append(f"Stopped run: {run_name}")

    lines.append(f"What stopped the run: {status.failure_reason}")

    if refused_reset_reason is not None and refused_reset_reason != status.failure_reason:
        lines.append(f"Reset was then refused: {refused_reset_reason}")

    lines.append(
        f"Failure log: {_from_home(failure_log)}"
        if failure_log is not None
        else FAILURE_LOG_NOT_KEPT_TEXT
    )

    return "\n".join(lines)


def _from_home(path: Path) -> str:
    """Return `path` written from the home folder as `~`, where it lies under it."""

    try:
        return str(Path("~") / path.relative_to(Path.home()))
    except ValueError:
        return str(path)


def report_fault_text(issues_url: str | None, *, link_colour: str) -> str:
    """Return the line under a failure's details that says how to report the fault, as rich text.

    A user cannot repair a fault in the simulator, so the useful next step
    is to report it (`PL-XWCH`). The line links the project's issue page where
    the installed metadata names one (`app_metadata.APP_ISSUES_URL`).

    Args:
        issues_url: The issue page, or None where the build kept no metadata.
        link_colour: The colour the link is drawn in. Qt otherwise draws a
            link in the palette's link colour, which the host appearance
            chooses, so the widget that shows the line passes its own.
    """

    if issues_url is None:
        return REPORT_FAULT_NO_PAGE_TEXT

    # `html.escape` escapes both quote characters by default, so neither value
    # can close the attribute it is written into.
    return REPORT_FAULT_TEMPLATE.format(
        url=html.escape(issues_url), link_colour=html.escape(link_colour)
    )


def refused_setting_notice(error: SimulationConfigurationError) -> str:
    """Return what the banner says about a setting that the core refused.

    A `SimulationConfigurationError` means the core rejected the value and
    changed nothing. The run is untouched and must not be marked as failed.
    So this text names the setting, and `notice` adds that the run continues
    unchanged.

    Args:
        error: The refusal, whose message names the value and why.

    Returns:
        The first half of the refused-setting banner.
    """

    return REFUSED_SETTING_TEMPLATE.format(error=error)


def setting_refusal_for_a_user(
    control: ControlInput, error: SimulationConfigurationError
) -> SimulationConfigurationError:
    """Return a refused setting's error, worded for the user who moved the control.

    A `SettingOutsideRange` is written for a developer, so it names the value
    by its field name in the code, such as `delivered_concentration_percent`.
    The error returned names the control by its label on screen, gives the value
    asked for and the limit, and says which limit refused it
    (`SETTING_LIMIT_REASONS`). Each value is written exactly
    (`_exact_setting`). The developer's message is kept whole,
    as the returned error's note (Python's `add_note`, PEP 678) and as its
    cause. The branch refusals keep a developer's detail the same way
    (`SimulationController._branch_from`, `PL-72X2`).

    Any other refusal is returned as it is. The controller words those for the
    user itself, as it does a setting on a stopped run. So is a range
    refusal of another control's field, which the settings record can raise
    while it checks every field after one control moves. Reworded for this
    control, it would name the wrong control and the wrong unit.

    Args:
        control: The control that asked for the setting.
        error: The refusal that the core or the controller raised.

    Returns:
        The refusal to show in the banner.
    """

    if (
        not isinstance(error, SettingOutsideRange)
        or error.quantity != CONTROL_INPUT_FIELDS[control]
    ):
        return error

    refusal = SimulationConfigurationError(
        REFUSED_SETTING_OUTSIDE_RANGE_TEMPLATE.format(
            setting=CONTROL_INPUT_LABELS[control].lower(),
            requested=_exact_setting(control, error.requested),
            reason=SETTING_LIMIT_REASONS[error.limit].format(
                lowest=_exact_setting(control, error.lowest),
                highest=_exact_setting(control, error.highest),
            ),
        )
    )
    refusal.add_note(str(error))
    refusal.__cause__ = error

    return refusal


def _exact_setting(control: ControlInput, value: float) -> str:
    """Return a refused value or a limit exactly, followed by the unit the control's slider shows.

    The value is written as the core's own message writes it (`shown`), which
    is the shortest text that reads back as the same number. The readout's
    format rounds, to 0.1 L/min or 0.01%, so a value just past a limit would be
    written equal to the limit or inside it: 10.04 L/min as "10.0 L/min"
    beside a highest flow of "10.0 L/min". A refusal reaches the banner only
    when a slider and a limit disagree, which is most likely at such a
    boundary. A percent sign follows with no space, as the readout writes one.
    """

    unit = CONTROL_INPUT_DISPLAY_UNITS[control].label

    return f"{shown(value)}{'' if unit == '%' else ' '}{unit}"


def refused_branch_notice(error: SimulationConfigurationError) -> str:
    """Return what the branch control says when the case refused to open a branch.

    The case opens no branch and changes nothing, so the notice says only that
    the branch was not opened and why. The reason names the controls by their
    words on screen (`controller.SimulationController.resumed_at`).

    Args:
        error: The refusal, whose message names the instant and why.

    Returns:
        The notice shown in place of the branch control's caption.
    """

    return REFUSED_BRANCH_TEMPLATE.format(error=error)


def refused_preview_notice(error: PreviewOfAnotherCase) -> str:
    """Return what the banner says while a held dial's preview is refused.

    The preview is refused because the run it was rebuilt as differs from the
    run on screen. The banner says that the release still applies the held
    value, because applying a value rebuilds nothing. So the notice is not
    worded as a refused setting, whose run keeps its previous setting.

    Args:
        error: The refusal, whose message names the dial and what to do.

    Returns:
        The whole banner, which `notice` shows in place of a refused setting's.
    """

    return REFUSED_PREVIEW_TEMPLATE.format(error=error)


def refused_reset_exit(error: BaseException, *, recorded_failure_reason: str | None) -> str:
    """Return the way out that a stopped-run banner names when the core refused Reset.

    Every failure wording ends by naming Reset, the only way out of a stopped
    run. When Reset is the control that was just refused, that line would
    send the reader back to it. So this exit says that Reset was refused, that
    no setting can repair the refusal, and that closing and reopening the
    application starts a new run. `REFUSED_RESET_WAY_OUT_TEXT` holds those
    words, and its comment says why no setting can repair the refusal.
    How the exit says Reset was refused depends on the banner's existing
    reason. A controller keeps the first failure it was given
    (`SimulationController.fail`). On a run that had not failed, or that this
    same refusal already stopped, the recorded reason is the refusal, so the
    exit refers to it. On a run that had failed for something else, the
    reason remains that earlier failure, so the exit states the refusal itself
    (`PL-M4M0`).

    Args:
        error: The refusal that `SimulationController.reset()` raised.
        recorded_failure_reason: The run's failure reason as it was when
            Reset was refused, or None if the run had not failed. It is
            compared with the reason this refusal records
            (`halt_disposition`), because pressing Reset twice for one
            refusal gives one reason, not two.

    Returns:
        The banner's closing sentence, for `notice` and `halt_notice`.
    """

    _, reason = halt_disposition(error)

    if recorded_failure_reason is None or recorded_failure_reason == reason:
        return REFUSED_RESET_EXIT_TEMPLATE.format(way_out=REFUSED_RESET_WAY_OUT_TEXT)

    return REFUSED_RESET_AFTER_FAILURE_EXIT_TEMPLATE.format(
        reason=FAILURE_CAUSE_TEXTS[failure_kind(error)], way_out=REFUSED_RESET_WAY_OUT_TEXT
    )


def notice(
    status: RunStatus,
    rejected_setting_notice: str | None,
    *,
    refused_reset: str | None = None,
    branch_offered: bool = False,
    refused_preview: str | None = None,
) -> str | None:
    """Return the banner for a frame that drew: a stopped run, a refusal, or nothing.

    A stopped run outranks a refusal, because it describes the state of
    everything else on screen, while a refusal describes only one control.
    A failure in turn outranks the supported run length. A setting refused on
    a stopped run is stated inside the stopped run's banner, in place of its
    way out (`_stopped_run_exit`, `PL-3B34`). A refused preview outranks a
    refused setting, because it is about the dial the user holds now, and an
    earlier refusal returns once the drag ends (`PL-412F`).

    `RunView.show_presentation` writes this banner while the frame for which the status
    was read is on screen. That is what lets the failure wording say that the
    values shown are the last completed step. `halt_notice` gives the banner
    for a halt for which no frame has been drawn.

    Args:
        status: The run's status this tick: the snapshot the frame drew
            from, or a bare `RunStatus`, as `status_word` takes it.
        rejected_setting_notice: The text from `refused_setting_notice` for
            the last refused setting, or None if the last setting was
            accepted. The run's view keeps it rather than the controller,
            because a refused setting changes nothing about the simulation.
        refused_reset: The sentence from `refused_reset_exit` while Reset
            itself was refused. It takes the place where the failure wording
            otherwise names Reset as the way out. It is None while Reset is
            the way out. The run's view keeps it, for the same reason as the
            refused setting.
        branch_offered: Whether a branch can be taken from this run now, as
            `RunView` reads it. A setting refused at the supported run length
            names a branch as its way out only while this is True. It is False
            by default, so when a caller leaves it out, the banner names only
            Reset, which is always offered.
        refused_preview: The banner from `refused_preview_notice` while a
            held dial's preview is refused, or None. The run's view keeps it,
            and drops it when the drag ends.

    Returns:
        The banner text, or None when there is nothing to say.
    """

    if status.failure_reason is not None:
        template = (
            FAILURE_NOTICE_TEMPLATE
            if status.rejected_accounting is None
            else REJECTED_ACCOUNTING_NOTICE_TEMPLATE
        )
        return template.format(
            failure_reason=shown_failure_reason(status),
            exit=_stopped_run_exit(
                rejected_setting_notice, refused_reset, setting_way_out=RESET_SETTING_WAY_OUT_TEXT
            ),
        )

    if status.supported_limit_reason is not None:
        return SUPPORTED_LIMIT_NOTICE_TEMPLATE.format(
            run_length=format_supported_run_length(),
            exit=_stopped_run_exit(
                rejected_setting_notice,
                refused_reset,
                setting_way_out=_supported_limit_setting_way_out(branch_offered),
            ),
        )

    if refused_preview is not None:
        return refused_preview

    if rejected_setting_notice is not None:
        return REFUSED_SETTING_NOTICE_TEMPLATE.format(refused=rejected_setting_notice)

    return None


def halt_notice(
    status: RunStatus,
    rejected_setting_notice: str | None = None,
    *,
    refused_reset: str | None = None,
    branch_offered: bool = False,
    started_over: bool = False,
    charts_withheld: bool = False,
) -> str | None:
    """Return the banner for a halt with no frame drawn yet: a stopped run, or nothing.

    `RunView.show_presentation` writes this banner from the run's status alone,
    before any frame is attempted. A failure uses
    `UNDRAWN_FAILURE_NOTICE_TEMPLATE` rather than `notice`'s wording, because
    with no frame drawn the values on screen are not the step the run stopped
    at. The first frame that draws writes `notice`'s banner in its place.
    After a step failure, the rollback leaves the run drawable, so its frame
    replaces this banner in the same turn. After a refused displayed value,
    the frame is refused again, so this banner stays. Which banner is shown is
    therefore decided by whether a frame drew, never guessed from the reason
    (`PL-7DJK`). The supported run length keeps its single wording, because
    nothing is wrong with the state it stops on, and the frame that follows
    draws. A refused setting is not a halt, so it has a banner here only
    inside a stopped run's, as in `notice`.

    Args:
        status: The run's status, as `SimulationController.status()` gives
            it. It is read without building any compartment value, which is
            the whole reason this function takes a status rather than a
            snapshot.
        rejected_setting_notice: As `notice` takes it. A dial moved on a run
            whose frame is refused springs back and is stated here.
        refused_reset: As `notice` takes it: the way out while Reset itself
            was refused, or None while Reset is the way out.
        branch_offered: As `notice` takes it: whether a branch can be taken
            from this run now.
        started_over: Whether the run has started over, by a Reset or an
            agent change, since its last frame was drawn. A failure then uses
            `STARTED_OVER_UNDRAWN_FAILURE_NOTICE_TEMPLATE`, because the
            readouts are withheld rather than showing the last frame. A run
            that has started over has not reached the supported run length,
            so that wording does not change.
        charts_withheld: Whether each chart withholds its frame, because the
            runs it shows are not the runs its last frame was drawn from. A
            failure of a run that has not started over then uses
            `CHARTS_WITHHELD_UNDRAWN_FAILURE_NOTICE_TEMPLATE`, so that the
            banner does not say that the charts show the last frame.

    Returns:
        The banner text, or None when the run is not halted.
    """

    if status.failure_reason is not None:
        if started_over:
            template = STARTED_OVER_UNDRAWN_FAILURE_NOTICE_TEMPLATE
        elif charts_withheld:
            template = CHARTS_WITHHELD_UNDRAWN_FAILURE_NOTICE_TEMPLATE
        else:
            template = UNDRAWN_FAILURE_NOTICE_TEMPLATE

        return template.format(
            failure_reason=shown_failure_reason(status),
            exit=_stopped_run_exit(
                rejected_setting_notice, refused_reset, setting_way_out=RESET_SETTING_WAY_OUT_TEXT
            ),
        )

    if status.supported_limit_reason is not None:
        return SUPPORTED_LIMIT_NOTICE_TEMPLATE.format(
            run_length=format_supported_run_length(),
            exit=_stopped_run_exit(
                rejected_setting_notice,
                refused_reset,
                setting_way_out=_supported_limit_setting_way_out(branch_offered),
            ),
        )

    return None


@dataclass(frozen=True, slots=True)
class Notice:
    """The banner above a run's values, and the emphasis it is drawn with.

    A run failing, or a setting being refused, is drawn as a warning. A stop
    at the supported run length, and the banner that announces it, are drawn
    muted, as the status word for that stop is. Nothing is wrong with a run
    that reaches its declared span, and drawing it in the warning colour
    would spend the interface's one signal for a real fault (`PL-0889`).

    Attributes:
        text: The banner's words.
        emphasis: How the banner is drawn.
        topic: What the banner is about, where its text changes while its
            topic does not. A countdown's time left changes every second, so
            a countdown's topic is its wording without that time. It is None
            where the text is the topic. A screen reader is told the banner
            when its topic changes, and not on each second of a countdown
            (`qt_widgets.NoticeLabel`, `PL-J7Z5`). Two banners with the same
            text are equal whatever their topics, because the topic is read
            from the text.
    """

    text: str
    emphasis: Emphasis
    topic: str | None = field(default=None, compare=False)


def run_notice(
    status: RunStatus,
    rejected_setting_notice: str | None,
    *,
    elapsed_s: int,
    refused_reset: str | None = None,
    branch_offered: bool = False,
    refused_preview: str | None = None,
) -> Notice | None:
    """Return the banner for a frame that drew, with its emphasis.

    The text is `notice`'s, and it outranks everything else. Below it, a run
    within `APPROACHING_LIMIT_NOTICE_S` of the supported run length says how
    much simulated time it has left before it stops (`PL-H2K2`). So a reader
    learns of the stop before it arrives, and the stop does not read as a
    fault when it comes. A refused setting stays on screen until the next
    accepted setting, so a refusal made hours earlier can still hold the
    banner when the run enters that span. The countdown then follows the
    refusal in the same banner, so the warning is never hidden behind it.

    Args:
        status: As `notice` takes it.
        rejected_setting_notice: As `notice` takes it.
        elapsed_s: The run's elapsed simulated time at this frame, in whole
            seconds.
        refused_reset: As `notice` takes it.
        branch_offered: As `notice` takes it.
        refused_preview: As `notice` takes it.

    Returns:
        The banner, or None when there is nothing to say.
    """

    text = notice(
        status,
        rejected_setting_notice,
        refused_reset=refused_reset,
        branch_offered=branch_offered,
        refused_preview=refused_preview,
    )
    remaining_s = MAXIMUM_ELAPSED_SIMULATION_TIME_S - elapsed_s
    countdown = (
        APPROACHING_LIMIT_NOTICE_TEMPLATE.format(
            remaining=format_elapsed(remaining_s), run_length=format_supported_run_length()
        )
        if remaining_s <= APPROACHING_LIMIT_NOTICE_S
        else None
    )

    # The countdown's topic is its wording with the time left still a
    # placeholder, so the topic stays the same while the time counts down.
    if text is None:
        return (
            None
            if countdown is None
            else Notice(countdown, Emphasis.MUTED, topic=APPROACHING_LIMIT_NOTICE_TEMPLATE)
        )

    stopped = status.failure_reason is not None or status.supported_limit_reason is not None
    emphasis = _stopped_emphasis(status, rejected_setting_notice, refused_reset)

    if countdown is not None and not stopped:
        return Notice(
            f"{text} {countdown}", emphasis, topic=f"{text} {APPROACHING_LIMIT_NOTICE_TEMPLATE}"
        )

    return Notice(text, emphasis)


def halt_run_notice(
    status: RunStatus,
    rejected_setting_notice: str | None = None,
    *,
    refused_reset: str | None = None,
    branch_offered: bool = False,
    started_over: bool = False,
    charts_withheld: bool = False,
) -> Notice | None:
    """Return `halt_notice`'s banner with its emphasis, for a halt with no frame drawn yet.

    Args:
        status: As `halt_notice` takes it.
        rejected_setting_notice: As `halt_notice` takes it.
        refused_reset: As `halt_notice` takes it.
        branch_offered: As `halt_notice` takes it.
        started_over: As `halt_notice` takes it.
        charts_withheld: As `halt_notice` takes it.

    Returns:
        The banner, or None when the run is not halted.
    """

    text = halt_notice(
        status,
        rejected_setting_notice,
        refused_reset=refused_reset,
        branch_offered=branch_offered,
        started_over=started_over,
        charts_withheld=charts_withheld,
    )

    return (
        None
        if text is None
        else Notice(text, _stopped_emphasis(status, rejected_setting_notice, refused_reset))
    )


def _stopped_emphasis(
    status: RunStatus, rejected_setting_notice: str | None, refused_reset: str | None
) -> Emphasis:
    """Return the emphasis of `notice`'s and `halt_notice`'s banners, by the same precedence.

    A failure outranks the supported run length, as in `status_word`. A
    banner that states a refused setting or a refused Reset is drawn as a
    warning, because what the reader asked for was not done. That holds on a
    run stopped at the supported run length too, whose banner then states
    the refusal. Only the stop itself, with nothing refused, is muted.
    """

    if (
        status.failure_reason is None
        and status.supported_limit_reason is not None
        and rejected_setting_notice is None
        and refused_reset is None
    ):
        return Emphasis.MUTED

    return Emphasis.WARNING


def _supported_limit_setting_way_out(branch_offered: bool) -> str:
    """Return the sentence that names the way out to a new setting from a stopped run.

    The run stopped because it reached the supported run length. The sentence
    names a branch at an earlier instant only while one can be taken, and Reset
    otherwise. A failed run's way out is always Reset.
    """

    return SUPPORTED_LIMIT_SETTING_WAY_OUT_TEXT if branch_offered else RESET_SETTING_WAY_OUT_TEXT


def _stopped_run_exit(
    rejected_setting_notice: str | None, refused_reset: str | None, *, setting_way_out: str
) -> str:
    """Return the closing sentences of a stopped run's banner, for `notice` and `halt_notice`.

    The exit is the sentence that names the way out. It is `RESET_EXIT_TEXT`
    unless something on the stopped run was refused. When Reset was refused,
    `refused_reset` replaces it. When a setting was refused on the stopped run,
    the closing sentences state the refused setting in place of the exit. They
    follow it with `setting_way_out`, the run's own way out to a new setting.
    When Reset was refused as well, the refused setting comes after the
    `refused_reset` exit instead, because closing the application is then the
    only way out. The comment above `STOPPED_RUN_SETTING_EXIT_TEMPLATE` gives
    the reasons for these choices.

    Args:
        rejected_setting_notice: The text from `refused_setting_notice`, or
            None while no setting is refused.
        refused_reset: The sentence from `refused_reset_exit`, or None while
            Reset is the way out.
        setting_way_out: The sentence that names the way out to a new
            setting. The caller chooses it, because the caller knows which of
            the two kinds of stop ended the run: reaching the supported run
            length, or a failure.

    Returns:
        The banner's closing sentences.
    """

    if rejected_setting_notice is None:
        return refused_reset or RESET_EXIT_TEXT

    if refused_reset is not None:
        return f"{refused_reset} {rejected_setting_notice}."

    return STOPPED_RUN_SETTING_EXIT_TEMPLATE.format(
        refused=rejected_setting_notice, way_out=setting_way_out
    )


class HaltDisposition(StrEnum):
    """Which of the two stopped states a raise puts the run in."""

    SUPPORTED_LIMIT = "supported_limit"
    FAILURE = "failure"


def halt_disposition(error: BaseException) -> tuple[HaltDisposition, str]:
    """Return how a raised exception stops the run, and the reason recorded for it.

    Every exception stops the run. A `TypeError` from a future refactor
    kills a timer slot exactly as silently as a modelling failure does. The
    exception's type decides only what the reader is told, and only one type
    is treated differently. `SimulationDomainLimitError` means the run reached
    the end of the supported domain. The core refused the next step before
    taking it, and nothing was miscalculated. Reporting it as a failure would
    put "simulation error" over a correct model that stopped where
    `docs/INTERFACE.md` § "What happens when a run reaches the limit" says it must
    (`PL-Y5WR`, `PL-V6M0`). Every other exception, known or not, is a failure.
    Only the narrow case is named, so
    an unrecognised exception falls through to the more cautious branch.

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
        amounts: Four lines. The first three give delivered, exhausted and
            stored agent at the resolution that `format_agent_volume`
            derives. The last gives the unaccounted amount as the power of
            ten that it is less than, because an order of magnitude is what
            that line is for (`PL-TG60`, `PL-3PJZ`, `PL-XFWG`).
    """

    status: StatusWord
    detail: str
    amounts: str


def accounting(snapshot: SimulationSnapshot) -> Accounting:
    """The agent-accounting panel for one snapshot.

    The verdict and the amounts always come from one step. After a step whose
    accounting failed its check, the core rolls that step back, and the
    snapshot's own accounting describes the restored step, which passed. The
    panel then shows the rejected step's check, which the snapshot carries as
    `rejected_accounting`. Showing "Validation failed" beside the restored
    totals would pair a verdict with totals it never judged (`PL-HF4B`,
    `PL-J5GC`).

    Args:
        snapshot: The run's state this tick.

    Returns:
        The panel's three parts.
    """

    if snapshot.rejected_accounting is not None:
        return rejected_step_accounting(snapshot.rejected_accounting)

    if snapshot.agent_accounting_passes_validation:
        status = StatusWord(ACCOUNTING_VALID_TEXT, Emphasis.ACCENT)
        detail = ACCOUNTING_VALID_DETAIL_TEXT
    else:
        status = StatusWord(ACCOUNTING_FAILED_TEXT, Emphasis.WARNING)
        detail = ACCOUNTING_FAILED_DETAIL_TEXT

    amounts = _accounting_amounts(
        delivered_l=snapshot.delivered_agent_l,
        exhausted_l=snapshot.exhausted_agent_l,
        stored_l=snapshot.stored_agent_l,
        unaccounted_l=snapshot.unaccounted_agent_l,
    )

    return Accounting(status, detail, amounts)


def rejected_step_accounting(rejected: AgentSimulationValidationResult) -> Accounting:
    """The agent-accounting panel for a step whose accounting check failed and was rolled back.

    `accounting` returns it for a frame that drew after the failure.
    `RunView.show_presentation` writes it when no frame can be drawn, from the
    `rejected_accounting` that the run's record carries. Until the adversarial
    review of `PL-J5GC`, the panel kept the last frame's "Valid" in that case,
    under a banner reporting the failed check.

    Args:
        rejected: The rejected step's check, with the totals it judged.

    Returns:
        The panel's three parts: "Validation failed", `ACCOUNTING_REJECTED_DETAIL_TEXT`
        and the rejected step's totals.
    """

    return Accounting(
        StatusWord(ACCOUNTING_FAILED_TEXT, Emphasis.WARNING),
        ACCOUNTING_REJECTED_DETAIL_TEXT,
        _accounting_amounts(
            delivered_l=rejected.delivered_agent_l,
            exhausted_l=rejected.exhausted_agent_l,
            stored_l=rejected.currently_stored_agent_l,
            unaccounted_l=rejected.unaccounted_agent_l,
        ),
    )


def _accounting_amounts(
    *, delivered_l: float, exhausted_l: float, stored_l: float, unaccounted_l: float
) -> str:
    """The accounting panel's four amount lines, from one step's totals, in litres."""

    amounts = (
        format_agent_volume(delivered_l),
        format_agent_volume(exhausted_l),
        format_agent_volume(stored_l),
        format_agent_residual(unaccounted_l),
    )

    return "\n".join(
        f"{name}: {amount}" for name, amount in zip(ACCOUNTING_AMOUNT_NAMES, amounts, strict=True)
    )


#: The accounting panel shown during a halt when no frame has been drawn since the run
#: started over. It replaces what the last frame wrote, for the same reason that the
#: readout cards withhold their values (`WITHHELD_CONCENTRATION_TEXT`). The panel was
#: last written for the run before the Reset or the agent change. So its verdict and
#: amounts describe a run that was discarded, while the heading above it names the
#: run that replaced it. Each amount line keeps its name, so the panel still says
#: which values are missing. The next frame writes the panel again (blind and
#: adversarial reviews of `PL-J5GC`).
WITHHELD_ACCOUNTING: Final = Accounting(
    StatusWord("\u2014", Emphasis.MUTED),
    ACCOUNTING_WITHHELD_DETAIL_TEXT,
    "\n".join(f"{name}: \u2014" for name in ACCOUNTING_AMOUNT_NAMES),
)


@dataclass(frozen=True, slots=True)
class TimelinePanel:
    """The control-change panel as drawn this tick.

    Attributes:
        entries: The listed adjustments, newest first, one per line, or
            `NO_CONTROL_CHANGES_TEXT` for a run nobody has touched.
        summary: How many changes the run has, and how many earlier ones the
            panel did not list, or the empty string for a run with no
            changes. It sits under the panel's heading, where it stays in
            view while the list scrolls (`PL-HF1B`). The count of changes
            that a chart left unmarked appears on that chart instead. The
            changes are counted rather than silently dropped, because a list
            that quietly stops, or that scrolls without saying so, asserts
            that nothing earlier happened.
    """

    entries: str
    summary: str


def timeline_panel(adjustments: Sequence[ControlAdjustment]) -> TimelinePanel:
    """The control-change panel for one run's adjustments.

    The panel lists changes, and says how many there are and how many it
    left out. The count of
    changes that a chart left unmarked appears on that chart instead, from
    `unmarked_changes_lines`, because each chart has its own window
    (`PL-L59K`).

    Args:
        adjustments: The run's adjustments, oldest first, as
            `control_timeline.AdjustmentGrouping` groups them.

    Returns:
        The panel's two parts.
    """

    if not adjustments:
        return TimelinePanel(NO_CONTROL_CHANGES_TEXT, "")

    listed = adjustments[-MAX_LISTED_ADJUSTMENTS:]
    entries = "\n".join(format_adjustment(adjustment) for adjustment in reversed(listed))

    unlisted = len(adjustments) - len(listed)
    notes = [CHANGE_COUNT_TEMPLATE.format(count=len(adjustments))]

    if unlisted:
        notes.append(UNLISTED_CHANGES_TEMPLATE.format(count=unlisted))

    return TimelinePanel(entries, TIMELINE_OVERFLOW_JOINER.join(notes))


@dataclass(frozen=True, slots=True)
class MarkListing:
    """One of the two bookmark collections as drawn this tick.

    Attributes:
        heading: What the collection is called.
        rows: One line per mark, in the order they were added, or empty.
        empty_text: The line shown in place of the rows when there are none.
            It is stored on the listing rather than chosen by the widget, so
            the two collections cannot come to disagree about what "nothing
            marked" looks like.
    """

    heading: str
    rows: tuple[str, ...]
    empty_text: str

    @property
    def empty_line(self) -> str | None:
        """The line shown in place of the rows, or None while there are rows.

        The choice between the rows and the empty line is made here, where a
        test can check it, so the widget decides nothing. The widget draws
        each entry of `rows` on its own row (`PL-FPY2`), and draws this line
        only when it is not None.
        """

        return None if self.rows else self.empty_text


@dataclass(frozen=True, slots=True)
class BookmarkPanel:
    """Both bookmark collections, listed separately.

    There are two listings, not one, which is the design that `PL-LPLD` was
    scoped on. A single list with a column for the kind of mark would make a
    reader sort the rows before reading either collection.

    Attributes:
        times: The marked instants.
        targets: The marked heights.
    """

    times: MarkListing
    targets: MarkListing


@dataclass(frozen=True, slots=True)
class RunMarks:
    """One displayed run's standing on each of the marks that the case carries.

    The panel is drawn from one of these per run, rather than from a single
    run's snapshot (`PL-LHBY`, `PL-4KZD`). A standing is computed from the
    run's own clock, its own opening instant and its own set of halts. So
    using one run's standings for every run's rows stated one management's
    answer as the case's answer while two runs were on screen. A user
    comparing two managements is reading exactly the quantity that differs.

    Attributes:
        label: What this run is called in text, from `run_label`. The caller
            supplies it, for the reason `chart_frame.RunInput.label` gives.
            The same word has to appear on the run's own panel beside the
            settings that produced the run, and a name invented by this
            module would appear nowhere else. It is drawn only on a row whose
            runs disagree, so a lone run's panel never shows it.
        standings: This run's standing on each of the case's marks, from
            `SimulationSnapshot.bookmark_standings`. That is the same
            snapshot that the run's readouts and traces were drawn from, so a
            row and the trace it is read against show one instant of one run.
    """

    label: str
    standings: BookmarkStandings


def _with_standings(stated: str, said: Sequence[str]) -> str:
    """Return one row: the mark's own value, then what the displayed runs say about it.

    Args:
        stated: The mark's own value and name, which every row carries. It is
            stated once however many runs are shown, because the runs share
            the marks by design. Only the runs' answers differ.
        said: The text of each clause of the row, in drawing order, from
            `_standing_clauses`. An empty clause is dropped rather than drawn
            as an empty tail.

    Returns:
        The row, with each clause that has something to say joined onto it.
    """

    return stated + "".join(f"{MARK_STANDING_JOINER}{clause}" for clause in said if clause)


def _standing_clauses(answers: Sequence[tuple[str, MarkStanding]]) -> tuple[str, ...]:
    """Return what one mark's row says about it, attributed to each run where the runs disagree.

    **Agreement decides attribution, not the number of runs** (`PL-LHBY`,
    `PL-4KZD`). An unattributed clause is a claim about the case. So it may be
    drawn only where it is true of every run on screen. That is always so for
    a lone run, and it is so for two runs that give the same answer. This
    makes the single-run row the simplest case of this rule rather than a
    second code path, which keeps the two from drifting apart. While the panel
    used one run's standings for every run's marks, it had no way to draw a
    branch's own answer at all. `MarkStanding`'s `BEFORE_THIS_BRANCH` could
    then never appear on screen, because the reference run was the trunk, and
    a trunk has no branch point for a mark to lie before.

    Where the runs disagree, the clause is no longer a claim about the case,
    so every run is named. That includes a run whose answer is "not yet",
    which unattributed silence would hide behind the run that did have
    something to say.

    **Each run and its answer arrive already paired, rather than as two
    sequences read in step.** Pairing them here would let a shorter standings
    sequence draw the agreement clause from only some of the runs. One run's
    answer would then be stated as the case's answer, which is the defect this
    function exists to remove, coming back as an off-by-one error. The caller
    builds each pair in one comprehension over the runs. So there is no length
    to check and no guard that could be dropped. `CLAUDE.md` asks for the
    interface that prevents the error over the one that rejects it afterwards.

    Args:
        answers: One `(run label, that run's standing on this mark)` pair per
            displayed run, in drawing order.

    Returns:
        One clause where the runs agree, or one clause per run where they do
        not. The result is empty when no run is given, but `bookmark_panel`
        rejects that case before calling this function.
    """

    standings = tuple(standing for _, standing in answers)

    if len(set(standings)) == 1:
        return (MARK_STANDING_TEXT[standings[0]],)

    return tuple(
        MARK_ATTRIBUTION_TEMPLATE.format(run=label, said=MARK_STANDING_COMPARED_TEXT[standing])
        for label, standing in answers
    )


def stated_mark(mark: TimeBookmark | MacTarget) -> str:
    """Return a mark's own words, as its row in the Bookmarks View begins.

    The row adds each run's standing after these words (`bookmark_panel`).
    The line that offers to undo a removal names the mark in the same words,
    without a standing, because the removed mark has none on screen.
    """

    if isinstance(mark, TimeBookmark):
        return _stated_time_bookmark(mark)

    return _stated_mac_target(mark)


def _stated_time_bookmark(bookmark: TimeBookmark) -> str:
    """Return a marked instant's own words: the time, and the name if it was given one.

    Every drawn row puts the time first and the name after it. The time is
    what the row asserts, and the name is what the user chose to call it.
    A reader comparing two rows reads down their first column. The time is
    rendered by `format_elapsed`, so a bookmark and the run clock beside it
    state one quantity in one way.
    """

    rendered = format_elapsed(bookmark.instant_s)

    if bookmark.label is None:
        return rendered

    return f"{rendered}{MARK_LABEL_JOINER}{bookmark.label}"


def _stated_mac_target(target: MacTarget) -> str:
    """Return a marked height's own words: the compartment, the height, and any name.

    Every drawn row gives the compartment, then the height, then the name,
    because `bookmark_panel` builds every row from this function. The
    compartment is on the row rather than in a heading above it, because a
    target means something different on each compartment. `docs/INTERFACE.md`
    § "MAC multiples as a display unit" states that a multiple of 1 MAC has its
    conventional meaning only on the alveolar compartment, and is a
    partial-pressure ratio everywhere else. So a row naming the height alone
    would be one number standing for six claims. The compartment's name comes
    from `chart_frame.trace_style`, so one table names both the row and the
    trace it is read against.
    """

    compartment = trace_style(target.quantity).label
    height = render_mac_multiple(target.mac_multiple)
    stated = f"{compartment} {height}"

    if target.label is None:
        return stated

    return f"{stated}{MARK_LABEL_JOINER}{target.label}"


def bookmark_panel(bookmarks: BookmarkSet, runs: Sequence[RunMarks]) -> BookmarkPanel:
    """Return the case's two collections of marks, as two listings.

    The panel states what is marked *and* how far each displayed run has got
    with each mark (`PL-CTD7`). Even so, nothing here reads a compartment. The
    standings are computed in the advance loop, once per completed simulation
    step, and arrive through `SimulationSnapshot.bookmark_standings`. That
    keeps a drawn row from implying that this module detected anything.

    **The rows use every displayed run, not only the reference run**
    (`PL-LHBY`, `PL-4KZD`). The marks belong to the case and the runs share
    them by design, so one row per mark is right. But each run has its own
    standings. So a row states the answer unattributed only where the runs
    agree, and names each run where they do not. Using `snapshots[0]` for
    every row instead put one management's answer on the other's mark, in
    both directions. A branch that halted on a user's mark reported
    nothing, because the trunk had not yet reached that mark. And an
    inherited bookmark that the branch could never reach was shown with the
    trunk's standing for it.

    Args:
        bookmarks: The case's marks, from `SimulationSnapshot.bookmarks`.
        runs: Every run on screen, in drawing order. Each carries the
            standings read from the same snapshot that its traces were drawn
            from. Marks and standings arrive as separate arguments, rather
            than one being derived from the other. So a panel cannot be drawn
            from one run's marks and another run's answers.

    Returns:
        Both listings, each with its heading, its rows and its empty line.

    Raises:
        ValueError: If no run is given. A panel drawn for no run would list
            the case's marks with standings that no run had given. That is
            the plausible-looking row for which `CLAUDE.md`'s safety-critical
            standard prefers an obvious failure.
        SimulationConfigurationError: If a run's standings were computed for a
            set of marks that does not hold one of these marks.
            `BookmarkStandings` rejects that case rather than using a default.
    """

    if not runs:
        raise ValueError("a marks panel states at least one run's standings; none was given")

    return BookmarkPanel(
        times=MarkListing(
            TIME_BOOKMARK_HEADING,
            tuple(
                _with_standings(
                    _stated_time_bookmark(bookmark),
                    _standing_clauses(
                        tuple((run.label, run.standings.of_time_bookmark(bookmark)) for run in runs)
                    ),
                )
                for bookmark in bookmarks.time_bookmarks
            ),
            NO_TIME_BOOKMARKS_TEXT,
        ),
        targets=MarkListing(
            MAC_TARGET_HEADING,
            tuple(
                _with_standings(
                    _stated_mac_target(target),
                    _standing_clauses(
                        tuple((run.label, run.standings.of_mac_target(target)) for run in runs)
                    ),
                )
                for target in bookmarks.mac_targets
            ),
            NO_MAC_TARGETS_TEXT,
        ),
    )


@dataclass(frozen=True, slots=True)
class CaseMarks:
    """The case's marks as the bookmarks panel lists them, and the highest mark it accepts.

    Attributes:
        panel: Both listings, with every displayed run's standing on each mark.
        reachable_height_mac: The highest marked height the editor accepts,
            in multiples of the agent's 1 MAC: the agent's highest delivered
            concentration divided by its 1 MAC.
    """

    panel: BookmarkPanel
    reachable_height_mac: float


def reachable_mark_height_mac(settings: RunSettings) -> float:
    """Return the highest height a run can be asked to reach, in multiples of its agent's 1 MAC.

    The bound is the agent's published highest delivered concentration divided
    by the agent's MAC. A run's own delivered setting changes what the run
    will reach, not what it may be asked to reach (`PL-GHMB`).
    """

    return mac_multiple(
        fraction_from_percent(settings.max_delivered_concentration_percent),
        settings.agent_mac_percent,
    )


def case_marks(
    labels: Sequence[str],
    bookmarks: Sequence[BookmarkSet],
    standings: Sequence[BookmarkStandings],
    settings: Sequence[RunSettings],
) -> CaseMarks:
    """Return the case's marks from every displayed run, refusing runs that disagree on them.

    The set of marks and the editor's bound belong to the case, so each is
    stated once. Each is read from every run and exists only when every run
    agrees on it (`PL-RF2S`). Before, both were read from the first run alone.
    The dashboard writes a mark to every run at once and a branch copies its
    trunk's marks, and two compared runs are on one agent, so the runs agree
    by construction. Where they do not, the panel would list one run's marks
    beside another run's standings, so this function refuses instead. A
    run's standing on each mark is its own, and `bookmark_panel` names each
    run where the standings differ.

    Args:
        labels: What each displayed run is called, from `run_label`, in
            drawing order.
        bookmarks: Each run's marks, in the same order.
        standings: Each run's standings on its marks, in the same order.
        settings: Each run's agent and settings, in the same order.

    Raises:
        ValueError: If the four sequences differ in length, if no run is
            given, if two runs hold different marks, or if two runs' agents
            give different bounds. The message names the runs.
        SimulationConfigurationError: As `bookmark_panel` raises it.
    """

    counts = {len(labels), len(bookmarks), len(standings), len(settings)}

    if len(counts) != 1:
        raise ValueError(
            f"the case's marks need one entry per run in each of four lists, given {sorted(counts)}"
        )

    if not labels:
        raise ValueError("the case's marks are read from at least one run; none was given")

    marks = bookmarks[0]
    heights = tuple(reachable_mark_height_mac(run) for run in settings)

    # The lengths were checked above, so `strict` can change nothing here.
    each_run = zip(labels, bookmarks, heights, strict=True)  # pragma: no mutate

    for label, run_marks, height in each_run:
        if run_marks != marks:
            raise ValueError(
                f"{label} holds different marks from {labels[0]}, and the marks belong to the case"
            )

        if height != heights[0]:
            raise ValueError(
                f"{label} accepts marks up to {height} x MAC and {labels[0]} up to "
                f"{heights[0]} x MAC, and the bound belongs to the case's one agent"
            )

    runs = zip(labels, standings, strict=True)  # pragma: no mutate

    return CaseMarks(
        bookmark_panel(marks, tuple(RunMarks(label, run) for label, run in runs)), heights[0]
    )


@dataclass(frozen=True, slots=True)
class ForkPoint:
    """One entry in the branch selector.

    The entry says where a branch would open and which method opens it. A
    recorded control event and a time bookmark that the trunk has passed are
    listed together, because both stay on offer until the case itself
    changes. `fork_offer` explains why that puts them in one list. The two
    kinds are taken through different methods, and `mark` says which.

    **A mark's entry carries the mark, not an instant to branch at.** A branch
    at a mark opens at the end of the step that reaches the mark. In general,
    that is not the instant the user typed (`MarkForkPoint`). A caller
    taking the entry passes `mark` back to `BranchedCase.fork_at_mark`, which
    finds that step itself. So there is no float here for a caller to get
    wrong. The entry is labelled and ordered by `instant_s`, but a mark's
    branch is never requested at that instant.

    Attributes:
        instant_s: Where a branch taken here opens, in seconds of the case.
            It is either a keyframe of the trunk or a passed mark's
            `MarkForkPoint.fork_s`.
        label: What the selector shows for the entry: `format_elapsed` of
            `instant_s`, placed inside `MARK_FORK_LABEL_TEMPLATE` for a mark.
        mark: None for a recorded control event, which is taken through
            `BranchedCase.fork_at` at `instant_s`. For a passed mark, it is
            the time bookmark itself, as the trunk holds it, and the entry is
            taken through `BranchedCase.fork_at_mark`.
    """

    instant_s: CaseInstant
    label: str
    mark: TimeBookmark | None


@dataclass(frozen=True, slots=True)
class ForkOffer:
    """What the branch control offers this tick, and why it may offer nothing.

    Attributes:
        points: What the selector offers, earliest first. It holds every
            keyframe of the trunk, from `BranchedCase.fork_points_s`: its
            opening at induction and every setting change that the model was
            actually stepped under. It also holds every time bookmark that
            the trunk has passed, from `BranchedCase.mark_fork_points`. The
            case rejects a branch anywhere else rather than approximating it.
            So the control offers this list and never a free choice of
            instant. Each instant is rendered by `format_elapsed`, the form
            that the run clock and every bookmark row use, so a user reads
            one quantity in one way wherever it appears. The list is empty
            once the trunk's frame has failed, and the panel then withdraws
            the selector (`PL-T2Q2`).
        locked: Whether the control is replaced by its reason. True while a
            comparison is already on the chart.
        lock_reason: The text shown in place of the control, or the empty
            string while the control is offered. It is a state caption rather
            than a warning. A mode that a reader can leave by pressing Reset
            is not the same kind of thing as a refusal. This interface has one
            alarm colour (`.claude/rules/ui-reader.md`), and it keeps its
            value only if it is used sparingly.
        here_offered: Whether the second control, the fork where the paused
            trunk stands, is on screen this tick. It appears when the trunk
            stops and disappears when the trunk starts. An entry in `points`
            instead stays until the case itself changes. That is why the fork
            here is a control of its own rather than an entry in that list
            (`PL-TYWQ`, `PL-Y2SL`).
        here_label: What that control says, or the empty string while it is
            not offered. It names the instant at which the branch will open,
            using `HERE_FORK_LABEL_TEMPLATE`. When a mark stopped the trunk
            there, it adds that fact, using `HALT_FORK_LABEL_TEMPLATE`. The
            comment on that template explains why those are two clauses
            rather than one.
        refusal: Why the most recently requested branch was not taken, for
            the notice banner, or None. It is never set while `locked`. The
            control that produced the refusal is gone, so the message would
            be about something the reader can no longer see.
        pinned_notice: What the panel says above its controls while the
            current Workspace is pinned to one run and a branch is still
            offered, or the empty string. A branch taken there would not be
            drawn in the Workspace (`PINNED_FORK_NOTICE_TEMPLATE`). It is
            empty while `locked`, because the lock caption then names the pin
            itself (`comparing_fork_lock_text`), and while nothing is offered.
    """

    points: tuple[ForkPoint, ...]
    locked: bool
    lock_reason: str
    here_offered: bool
    here_label: str
    refusal: str | None
    pinned_notice: str = ""


@dataclass(frozen=True, slots=True)
class ComparedRuns:
    """What the two runs of a comparison are called, and whether this Workspace draws them.

    Attributes:
        trunk: The trunk's name, from `run_label`.
        branch: The branch's name, from `run_label`.
        pinned_away: The name of the run that the current Workspace is pinned
            to, where that pin keeps the comparison off its Views, or None
            where the Workspace draws both runs. The name comes from
            `run_label` for an open run, and from `pinned_run_label` for one
            that is not open.
    """

    trunk: str
    branch: str
    pinned_away: str | None = None


def comparing_fork_lock_text(runs: ComparedRuns) -> str:
    """Return the caption shown in place of the branch control, naming the way out of the lock.

    The caption is filled from the runs' names and `RESET_LABEL` rather than
    written out. The way out is a button, and a reader finds a button by the
    words on it. A comparison draws two Reset buttons, one per run, each in a
    transport row that starts with that run's name. So a sentence that names
    neither leaves the reader to guess which one to press (`PL-WG73`, and
    `COMPARING_FORK_LOCK_TEMPLATE` for what that guess cost).

    The lock applies only while a second run is drawn, which is `fork_offer`'s
    `comparing`. So whenever this text is on screen, both names belong to
    runs on screen. One is the trunk, whose Reset ends the comparison. The
    other is the branch, whose Reset returns that run to its fork and leaves
    the lock exactly where it was. The text uses the names the runs carry,
    not their positions, because a branch taken after an earlier branch was
    dropped is not "Run 2" (`PL-7Z84`).

    Where the current Workspace is pinned to one run, its Views draw no
    comparison, so the caption goes on to say so and how to draw it
    (`COMPARISON_PINNED_AWAY_TEMPLATE`, `PL-YQ5J`).

    Args:
        runs: What the trunk and the branch are called on screen, and the
            run the current Workspace is pinned to where that keeps the
            comparison off its Views.

    Returns:
        The caption, naming both Resets as the screen names them.
    """

    lock = COMPARING_FORK_LOCK_TEMPLATE.format(
        trunk=runs.trunk, branch=runs.branch, reset=RESET_LABEL
    )

    if runs.pinned_away is None:
        return lock

    pinned_away = COMPARISON_PINNED_AWAY_TEMPLATE.format(
        pinned=runs.pinned_away, trunk=runs.trunk, branch=runs.branch
    )

    return f"{lock} {pinned_away}"


def fork_offer(
    fork_points_s: Sequence[CaseInstant],
    *,
    marks: Sequence[MarkForkPoint],
    comparing: ComparedRuns | None,
    here: HereForkPoint | None,
    refusal: str | None = None,
    pinned_to: str | None = None,
) -> ForkOffer:
    """Return what the branch control shows for one tick of the trunk.

    All three ways of taking a branch are decided here, in two fields.
    `points` is one list, ordered by instant. It holds every keyframe of the
    trunk, taken through `fork_at`, and every time bookmark that the trunk
    has passed, taken through `fork_at_mark`. `here_offered` says whether a
    branch is offered at the point where the paused trunk stands right now.
    That branch is taken through `fork_here`.

    **The passed marks last as long as the keyframes, and the paused point
    does not.** A mark joins the list when the trunk's clock reaches it, or
    when a mark is set behind the clock. It leaves only when the user
    removes it or the trunk starts over, just as a keyframe stays until the
    case changes. So the marks belong in the selector. The paused point ends
    when the trunk starts, so it stays a control of its own. A row that
    appeared and disappeared as the run moved would change the selector's
    contents under a reader who had looked away. The comment on
    `HERE_FORK_LABEL_TEMPLATE` records both decisions. `docs/ARCHITECTURE.md`
    § "Where a branch may be taken" explains why the model keeps the paused
    point apart from the keyframes. Pausing records no keyframe, so the paused
    point adds nothing to `fork_points_s`.

    The list is earliest first, and a control event comes before a mark at
    the same instant. That is the order in which the two lists are given,
    kept by a stable sort, so one case is always listed in the same way.

    Induction is offered rather than filtered out. A branch at zero is a
    second management of the whole case, which is a comparison a user may
    legitimately want. Filtering it out would leave a case that has recorded
    nothing with no instant to offer at all. That would be a control with an
    empty list and a live button, which is worse than an odd-looking entry.

    Args:
        fork_points_s: The trunk's keyframes, from
            `BranchedCase.fork_points_s`.
        marks: The time bookmarks that the trunk has passed, each with the
            instant at which a branch taken there opens, from
            `BranchedCase.mark_fork_points`. The argument is required rather
            than defaulted. So a caller must state that the trunk has passed
            no marks, instead of silently leaving out the third way to branch.
        comparing: The two runs on the chart while a second run is already
            there, or None while only one run is. The display is capped at
            `MAX_DISPLAYED_RUNS`, and no run selector exists yet (`ROADMAP.md`
            § "Explicitly out of scope for v0.5.0"). So a second branch taken
            now would have to replace the shown one, while the first branch
            went on living inside `BranchedCase`. The screen would not show
            that state, which is why the control is refused. The refusal
            applies to every way of branching, because a branch is a branch
            whichever way it was taken. This interface prevents a control
            that the cap would reject on press, rather than reporting the
            rejection afterwards (`.claude/rules/expert-review.md`).
        here: Where the **trunk** is paused, from
            `BranchedCase.here_fork_point`, or None while `fork_here` would
            refuse. It refuses while the trunk is running, has failed, or has
            reached the supported run length, where a branch would have no
            step to take. It also refuses while the trunk is at its opening,
            which the selector's induction entry already offers. This argument
            is the model's answer, not an instant read off the clock here. So
            the offer comes from the same check that `fork_here` raises from,
            and it says whether a mark stopped the trunk there, which a float
            could not say.
        refusal: Why the most recently requested branch was not taken, or
            None. It is dropped while the control is locked, because it
            describes a press of a control that the reader can no longer see.
        pinned_to: The name of the run that the current Workspace is pinned
            to, or None while it is not pinned. The dashboard reads it as it
            reads `ComparedRuns.pinned_away`, so the sentence before a branch
            and the sentence after it name the same run (`PL-RXR8`). It is
            ignored while `comparing` is set, because the lock caption then
            says it, and while nothing is offered.

    Returns:
        The points to offer, each labelled and carrying the method through
        which it is taken. Also whether the branch at the paused point is
        offered and what its control says, or the reason that none of it is
        offered.
    """

    control_events = tuple(
        ForkPoint(instant_s, format_elapsed(instant_s), None) for instant_s in fork_points_s
    )
    passed_marks = tuple(
        ForkPoint(
            point.fork_s,
            MARK_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(point.fork_s)),
            point.bookmark,
        )
        for point in marks
    )
    # The comparison cap refuses every way of branching. So it is applied
    # once, here, rather than checked separately for each field.
    offered_here = None if comparing is not None else here
    points = tuple(sorted((*control_events, *passed_marks), key=lambda point: point.instant_s))
    # The pin is said only beside a branch that can be taken. While two runs
    # are open the lock caption names it, and with nothing offered there is no
    # press for it to come before.
    branch_offered = comparing is None and (bool(points) or offered_here is not None)

    return ForkOffer(
        points=points,
        locked=comparing is not None,
        lock_reason="" if comparing is None else comparing_fork_lock_text(comparing),
        here_offered=offered_here is not None,
        here_label="" if offered_here is None else _here_fork_label(offered_here),
        refusal=None if comparing is not None else refusal,
        pinned_notice=(
            PINNED_FORK_NOTICE_TEMPLATE.format(pinned=pinned_to)
            if branch_offered and pinned_to is not None
            else ""
        ),
    )


def kept_fork_selection(
    previous: Sequence[ForkPoint] | None, selected: ForkPoint | None, points: Sequence[ForkPoint]
) -> ForkPoint | None:
    """Return the point the branch selector shows as selected once `points` is the offer.

    The dashboard keeps one selection for the case, and every copy of the
    branch control shows it. So a copy that is built later, such as after a
    switch of Workspace, shows the point the user chose (`PL-9YPR`).

    **A selection whose point is no longer offered is cleared, and a cleared
    selection stays clear** (`PL-J12Z`). Falling back to the first entry would
    put induction under a user who had chosen a later decision point, and
    the next press would branch there. A point can leave the offer without a
    reset: a keyframe collapses when a dial is returned to its previous value
    at the same instant, and a mark leaves when it is unmarked.

    An offer shown first, or shown after an offer that held no point, is the
    one exception. Nobody has chosen yet, so the first entry is selected, as a
    selector normally does.

    Args:
        previous: The points of the offer shown before this one, or None
            where no offer has been shown.
        selected: The point selected under `previous`, or None for no point.
        points: The points of the offer about to be shown.

    Returns:
        The first of `points` where `previous` is None or held no point, or
        None where `points` is empty too. Otherwise `selected` where `points`
        still holds it, and None where it does not.
    """

    if not previous:
        return points[0] if points else None

    return selected if selected in points else None


def _here_fork_label(here: HereForkPoint) -> str:
    """Return the label of the fork where the trunk stands: its instant, and any stopping mark.

    Args:
        here: Where the trunk stands, from `BranchedCase.here_fork_point`.
    """

    template = HALT_FORK_LABEL_TEMPLATE if here.stopped_on_mark else HERE_FORK_LABEL_TEMPLATE

    return template.format(instant=format_elapsed(here.fork_s))


def delivered_line(delivered: SettingReadout) -> str:
    """Return the vaporizer setting in both units, for the run's transport row.

    The line is written from the same readout as the dial itself, so the line
    and the dial print one setting in one form (`PL-NWTM`).

    Args:
        delivered: The delivered dial's readout from `setting_readouts`.

    Returns:
        The line.

    Raises:
        ValueError: If `delivered` is not the delivered dial's readout. A
            flow's readout has no second unit. Printed here, it would present
            a flow as the concentration that the vaporizer is set to.
    """

    if delivered.control is not ControlInput.DELIVERED:
        raise ValueError(
            f"the delivered line is written from the delivered dial's readout, "
            f"not from {delivered.control.value}'s"
        )

    return DELIVERED_LINE_TEMPLATE.format(value=delivered.value_text, secondary=delivered.secondary)


def substance_heading(settings: RunSettings) -> str:
    """Return the heading that names the substance the six readouts belong to (`PL-TCD1`).

    Args:
        settings: The run's agent and settings. This is the snapshot that a
            frame drew from, or the controller's record when no frame draws.
            That is why the function takes the type that both of them
            provide (`PL-1YDD`).

    Returns:
        The heading line.
    """

    return COMPARTMENT_SUBSTANCE_TEMPLATE.format(agent=settings.agent_display_name)


@dataclass(frozen=True, slots=True)
class RunStatement:
    """What a run's screen states without a compartment value: every run-state widget but the dials.

    `RunView.show_presentation` is the only code that writes these widgets.
    `run_presentation.drawn_run` builds the statement from the snapshot that
    a frame drew from. `run_presentation.halted_run` builds it from
    `SimulationController.record()` when no frame can draw. So a widget
    listed here shows the same thing on a drawn run and on a halted run in
    the same state. Before this class existed, the halt wrote only to a list
    of widgets chosen by hand, and each widget the list missed went on
    showing the last frame's run (`PL-X7D5`, `PL-1YDD`, `PL-DTJQ`).

    The four dials are built next to this statement from the same record,
    rather than carried in it. `setting_readouts` can raise for a control that
    can offer no setting, and everything here has to be on screen before that
    refusal is raised (`PL-85LJ`, `run_presentation.NotBuilt`).

    Attributes:
        agent_id: The running agent. `RunView._apply_agent_color_scheme`
            writes its ISO 5360 colour pair, and the selector shows its
            entry.
        agent_name: The running agent's name, on the chip that replaces the
            selector.
        subtitle: The header badge's line naming the build and the agent.
        substance_heading: The heading saying which agent's concentrations
            the readouts show.
        status: The status word.
        transport: Which transport controls are usable, and why the
            selector is locked.
        timeline: The control-change panel.
        banner: The notice banner before it is attributed to a run, or None
            for no banner.
    """

    agent_id: str
    agent_name: str
    subtitle: str
    substance_heading: str
    status: StatusWord
    transport: Transport
    timeline: TimelinePanel
    banner: Notice | None


def run_statement(
    record: RunRecord,
    adjustments: Sequence[ControlAdjustment],
    *,
    is_branch: bool,
    comparing: bool,
    banner: Notice | None,
    stopped_on_mark: bool,
) -> RunStatement:
    """Return what a run's screen shows from its record alone, for `RunView.show_presentation`.

    This function builds no compartment value. So when a run halts because of
    a compartment value, stating that halt cannot raise the same error again
    (`PL-7DJK`).

    Args:
        record: The run's record. This is the snapshot that a frame drew
            from, or `SimulationController.record()` when no frame draws.
        adjustments: `record.control_timeline` grouped into acts, as
            `RunView.adjustments` groups it.
        is_branch: As `transport` takes it.
        comparing: As `transport` takes it.
        banner: The banner from `run_notice` when a frame drew, or from
            `halt_run_notice` when none has. The caller chooses, because only the
            caller knows whether a frame drew.
        stopped_on_mark: As `status_word` takes it.

    Returns:
        The statement.
    """

    return RunStatement(
        agent_id=record.agent_id,
        agent_name=record.agent_display_name,
        subtitle=format_subtitle(record.agent_display_name),
        substance_heading=substance_heading(record),
        status=status_word(record, stopped_on_mark=stopped_on_mark),
        transport=transport(record, is_branch=is_branch, comparing=comparing),
        timeline=timeline_panel(adjustments),
        banner=banner,
    )


def time_axis_caption(frame: ChartFrame) -> str:
    """Return the span of the run that the chart shows, and what set it: reader, hold or run.

    Args:
        frame: The frame drawn this tick.

    Returns:
        The caption line.
    """

    span = format_time_base(frame.time_base.span_s)

    if any(run.preview is not None for run in frame.runs):
        return PREVIEW_TIME_AXIS_CAPTION_TEMPLATE.format(span=span)

    if frame.fitted:
        return FITTED_TIME_AXIS_CAPTION_TEMPLATE.format(span=span)

    if frame.held:
        return HELD_TIME_AXIS_CAPTION_TEMPLATE.format(span=span)

    return CHOSEN_TIME_AXIS_CAPTION_TEMPLATE.format(span=span)


def held_window_notice(frame: ChartFrame) -> str | None:
    """Return the line that says what a held window shows and where the run is now, or None.

    The line appears only while the reader holds the window back from the
    run (`ChartFrame.held`). It names the window's edges as the axis labels
    them, and each run's instant as the clock states it, so a reader can see
    how far the readouts have moved past the plot. With two runs on the
    chart it names each run, because a branch and its trunk stand at
    different instants. It is left out
    during a preview, whose window is centred on the run's reach rather than
    the held one.

    Args:
        frame: The frame drawn this tick.

    Returns:
        The line, or None where the window follows the run or a preview
        replaces it.
    """

    if not frame.held or any(run.preview is not None for run in frame.runs):
        return None

    if len(frame.runs) == 1:
        now = HELD_ONE_RUN_NOW_TEMPLATE.format(now=format_elapsed(frame.runs[0].elapsed_s))
    else:
        now = HELD_RUNS_NOW_TEMPLATE.format(
            runs=", ".join(
                HELD_RUN_NOW_TEMPLATE.format(label=run.label, now=format_elapsed(run.elapsed_s))
                for run in frame.runs
            )
        )

    return HELD_WINDOW_NOTICE_TEMPLATE.format(
        start=format_chart_time_label(frame.start_s),
        stop=format_chart_time_label(frame.stop_s),
        now=now,
    )


def mac_reference_caption(frame: ChartFrame) -> str:
    """Return a caption naming the divisor that every MAC number on the page uses.

    The caption names the reference run's agent and its 1 MAC. That is what
    makes the MAC readouts traceable without opening a data file (`CLAUDE.md`,
    safety-critical clinical-output standard).

    Args:
        frame: The frame drawn this tick. All of its runs use one agent.

    Returns:
        The reference line.
    """

    return format_mac_reference(
        frame.runs[0].agent_display_name, frame.mac_percent, age_years=frame.mac_age_years
    )


def mac_awake_caption(frame: ChartFrame) -> str:
    """Return what the MAC-awake band was drawn from: its published fraction and the divisor.

    This text names the published fraction, and the band's legend entry
    shows it. The divisor, the agent's 1 MAC in percent, is in the 1 MAC
    line's entry beside it (`mac_reference_caption`, `PL-K4CZ`).
    So both free parameters are on screen, and a reader who disagrees with
    either one can see which one it is (`PL-F52R`).

    The values are read from the frame that drew the band, as the 1 MAC line's
    are. Every run of a frame is on one agent, so the caption is true of every
    run on the plot (`PL-RF2S`).

    Args:
        frame: The frame drawn this tick.

    Returns:
        The reference line.
    """

    mac_awake = frame.mac_awake

    return format_mac_awake_reference(
        frame.runs[0].agent_display_name,
        fraction_of_mac=mac_awake.fraction_of_mac,
        standard_deviation_fraction_of_mac=mac_awake.standard_deviation_fraction_of_mac,
        mac_percent=frame.mac_percent,
    )


def concentration_chart_name(frame: ChartFrame | None) -> str:
    """Return what a screen reader calls the concentration chart: what it plots, and its window.

    This is the chart's short text alternative, which WCAG 2.2 SC 1.1.1 asks
    of non-text content (`PL-T9RB`). It is the chart's heading followed by the
    time axis's caption, so it says the same as the screen. A withheld frame
    has no window, so the name is the heading alone.

    Args:
        frame: The frame the chart drew, or None while it draws none.

    Returns:
        The name.
    """

    return CHART_HEADING if frame is None else f"{CHART_HEADING}, {time_axis_caption(frame)}"


def concentration_chart_description(frame: ChartFrame | None) -> str:
    """Return the concentration chart's long description, for a screen reader.

    The W3C example of a chart's text alternative pairs a short name with a
    longer description that names the type of chart and summarises its data
    (Understanding WCAG 2.2 SC 1.1.1, `PL-T9RB`). This one names the type,
    then gives the latest drawn value of each trace shown
    (`chart_frame.latest_values_lines`). While a drag draws a preview, the
    preview's label follows (`chart_frame.preview_label_lines`, `PL-MP1X`).
    Then come the 1 MAC and MAC-awake references the chart draws. Each
    reference is worded as its legend entry words it, less how the line is
    drawn. So the band says that it is a
    population's and is read against the vessel-rich group trace, and the 1 MAC
    line names the reference adult and the alveolar trace (`PL-596J`). Each
    reference ends with a full stop, as each sentence before it does. A screen
    reader that reads the description as one passage then pauses between them,
    because JAWS, NVDA and VoiceOver pause at a full stop, while NVDA reads
    through a parenthesis without a pause (Bohman, "Why Don't Screen Readers
    Always Read What's on the Screen? Part 1", Deque, 2014). Where the reader
    has unchecked every compartment, or no frame could be drawn, it says what
    the screen says instead. A window in which no run has a drawn point gives
    no values.

    Args:
        frame: The frame the chart drew, or None while it draws none.

    Returns:
        The description, one sentence or reference per line.
    """

    if frame is None:
        return WITHHELD_FRAME_TEXT

    values = (NO_TRACES_SHOWN_TEXT,) if no_traces_shown(frame) else latest_values_lines(frame)
    # The plot draws a preview's region and label even with every compartment
    # unchecked, so the label is read in that case too.
    values = (*values, *preview_label_lines(frame))

    references = (
        ONE_MAC_LINE_SPOKEN_TEMPLATE.format(reference=mac_reference_caption(frame)) + ".",
        MAC_AWAKE_BAND_LEGEND_TEMPLATE.format(reference=mac_awake_caption(frame)) + ".",
    )

    return "\n".join((CHART_TYPE_TEXT, *values, *references))


def wash_in_state(reading: WashInReading, undrawn_wash_in_stretches: int) -> str:
    """Return what the wash-in plot is showing at this instant, and why.

    The reading comes from `read_wash_in_with_ventilation` on the snapshot's
    own alveolar and inspired fractions and the ventilation of the step that
    reached them (`chart_frame.RunFrame.wash_in_now`). The trace's right-hand
    end comes from the states that the chart evaluates
    (`DrawnWindow.wash_in_quotients`). Both read the state that the run stored
    for the second (`PL-MH9J`), and both apply the three rules of
    `app/wash_in.py`, so the caption names the value the trace ends at.

    Args:
        reading: The run's F_A/F_I reading this tick.
        undrawn_wash_in_stretches: How many stretches inside the window the
            plot's limited pool of lines could not draw, from
            `RunFrame.undrawn_wash_in_stretches` of the same tick. The count
            is appended, so the pool's limit is shown rather than hidden.

    Returns:
        One line for the row above the plot.
    """

    if reading.plotted_ratio is not None:
        state = WASH_IN_STATE_TEMPLATE.format(ratio=format_wash_in_ratio(reading.plotted_ratio))
    elif reading.domain is WashInDomain.NO_INSPIRED_AGENT:
        state = WASH_IN_NOT_DEFINED_TEXT
    elif reading.domain is WashInDomain.VENTILATION_STOPPED:
        state = WASH_IN_VENTILATION_STOPPED_TEXT
    else:
        state = WASH_IN_ELIMINATION_TEXT

    if undrawn_wash_in_stretches:
        state += WASH_IN_UNDRAWN_SUFFIX_TEMPLATE.format(count=undrawn_wash_in_stretches)

    return state


def off_scale_notice(frame: ChartFrame, run_index: int) -> str | None:
    """Return a notice naming which of one run's drawn traces are above the plot, if any.

    A preview's traces are checked too. A clipped preview is named in a second
    sentence that gives its highest predicted value in the window, because
    nothing else on screen shows a preview's values (`PL-5B1N`).

    The traces are read from the points the frame drew, not from the snapshot.
    The snapshot carries only the newest state, and a trace that rose above
    the axis earlier in the window is still drawn clipped now. Hidden traces
    are skipped, so the notice never points at a trace that is not there. A
    trace counts as off scale only once it exceeds the ceiling by more than
    the readouts resolve. Desflurane's ceiling is 3 x 6.6, which in binary
    floating point is 19.799999999999997. A comparison with zero tolerance
    would report that rounding noise as an excursion. This function builds no
    checked concentration. The percents and the axis top were built when the
    frame was assembled, so this function cannot reject a value after the
    chart has drawn it (`PL-7DJK`). The run index is built as a `RunIndex`
    before it is used, so a negative index is rejected rather than treated
    as the last run.

    Args:
        frame: The frame drawn this tick.
        run_index: Which of the frame's runs.

    Returns:
        The notice, or None when every drawn trace and preview is inside the axis.

    Raises:
        TypeError: If `run_index` is not an `int` (`RunIndex`).
        ValueError: If `run_index` is negative (`RunIndex`). Python would
            treat `-1` as the last run, and report on that run under the name
            of the run the caller meant (`PL-7694`).
        IndexError: If `run_index` is not one of the frame's runs.
    """

    run = frame.runs[RunIndex(run_index)]
    off_scale = [
        trace_style(quantity).label
        for quantity in frame.visible
        if _above_the_axis(frame, run.percents(quantity))
    ]
    preview_peaks = (
        []
        if run.preview is None
        else [
            f"{trace_style(quantity).label} "
            f"{format_mac_multiple(max(run.preview.fractions[quantity]), frame.mac_percent)}"
            for quantity in frame.visible
            if _above_the_axis(frame, run.preview.percents(quantity))
        ]
    )
    # The top is named in both of the axis's units, so a reader working from
    # either axis learns where the plot stops without converting (`PL-DVDY`).
    top_fraction = fraction_from_percent(frame.axis_top_percent)
    top = f"{format_percent(top_fraction)} ({format_mac_multiple(top_fraction, frame.mac_percent)})"
    sentences = []

    if off_scale:
        sentences.append(
            OFF_SCALE_NOTICE_TEMPLATE.format(compartments=", ".join(off_scale), top=top)
        )

    if preview_peaks:
        sentences.append(
            PREVIEW_OFF_SCALE_NOTICE_TEMPLATE.format(top=top, peaks=", ".join(preview_peaks))
        )

    return " ".join(sentences) or None


def above_the_axis_top(percent: float, axis_top_percent: float) -> bool:
    """Return whether a value exceeds the concentration axis's top by more than a display step.

    A display step is the smallest change that the readouts print. This is the
    one test of "off the scale", and both the chart's off-scale notice and the
    compartment schematic's off-scale mark use it (`PL-RNYV`). Both pass the
    top that the reader chose for every chart and schematic (`PL-7LZ7`), so
    the two agree about every tension. The margin of one display step is
    needed because of binary rounding. For example, desflurane's top of 3 x 6.6
    is 19.799999999999997 in binary. A value that the readouts print as the top
    is not above it.
    """

    return percent - axis_top_percent > CONCENTRATION_DISPLAY_RESOLUTION_PERCENT


def _above_the_axis(frame: ChartFrame, percents: Sequence[float]) -> bool:
    """Whether any drawn point exceeds the axis top by more than the readouts resolve."""

    return any(above_the_axis_top(percent, frame.axis_top_percent) for percent in percents)


def off_scale_lines(frame: ChartFrame) -> tuple[str | None, ...]:
    """Each drawn run's off-scale notice, for the concentration chart that drew `frame`.

    The result has one entry for each run in `frame.runs`, in the same order.
    An entry is the run's `off_scale_notice`. While more than one run is drawn,
    `compared_run_line` labels it with its run. An entry is None when every
    trace of that run is inside the axis. Each chart writes these lines from
    its own frame, because which points are off scale depends on the window
    that the chart shows (`PL-L59K`).
    """

    lines: list[str | None] = []

    for index in range(len(frame.runs)):
        notice = off_scale_notice(frame, index)
        lines.append(None if notice is None else compared_run_line(notice, frame, index))

    return tuple(lines)


def wash_in_state_lines(frame: ChartFrame) -> tuple[str, ...]:
    """Each drawn run's wash-in state line, for the F_A/F_I plot that drew `frame`.

    The result has one entry for each run, in order. Each entry is the run's
    `wash_in_state`, from the reading the frame holds for that run, with the
    count of stretches that this plot's window left undrawn. While more than
    one run is drawn, `compared_run_line` labels each entry with its run. The
    reading, the count and the name all come from one `RunFrame`, so no line
    can pair one run's name with another run's reading (`PL-RF2S`).

    Args:
        frame: The frame the plot drew.
    """

    return tuple(
        compared_run_line(
            wash_in_state(run.wash_in_now, run.undrawn_wash_in_stretches), frame, index
        )
        for index, run in enumerate(frame.runs)
    )


def wash_in_plot_name(frame: ChartFrame | None) -> str:
    """Return what a screen reader calls the wash-in plot: what it plots, and its window.

    This is the plot's short text alternative, built as
    `concentration_chart_name` builds the concentration chart's (`PL-R1M6`):
    the plot's heading, then the time axis's caption. The heading is given
    without its subscript markup, as Qt reads the heading's label to a
    screen reader. A withheld frame has no window, so the name is the
    heading alone.

    Args:
        frame: The frame the plot drew, or None while it draws none.

    Returns:
        The name.
    """

    heading = plain_text(WASH_IN_HEADING)

    return heading if frame is None else f"{heading}, {time_axis_caption(frame)}"


def wash_in_plot_description(frame: ChartFrame | None) -> str:
    """Return the wash-in plot's long description, for a screen reader.

    It follows `concentration_chart_description` (`PL-R1M6`). It names the
    type of chart and says that the values are modelled. Then it gives the
    last point each run's trace draws, with its instant
    (`chart_frame.latest_wash_in_lines`), and the label of a preview that a
    drag draws (`chart_frame.preview_label_lines`, `PL-MP1X`). Last comes the
    equilibrium line that the plot draws. It leaves out the row above the plot, which is text a
    screen reader already reads, and whose "Now" reading lies outside a
    held window. The lines are given without subscript markup. A window in
    which no run has a drawn point gives no values. A withheld frame gives
    what the concentration chart gives while it draws none.

    Args:
        frame: The frame the plot drew, or None while it draws none.

    Returns:
        The description, one sentence or reference per line.
    """

    if frame is None:
        return WITHHELD_FRAME_TEXT

    return "\n".join(
        plain_text(line)
        for line in (
            CHART_TYPE_TEXT,
            INTERPRETATION_DISCLAIMER_TEXT,
            *latest_wash_in_lines(frame),
            *preview_label_lines(frame),
            EQUILIBRIUM_REFERENCE_TEXT,
        )
    )


def unmarked_changes_lines(frame: ChartFrame) -> tuple[str | None, ...]:
    """Return, for each drawn run, how many of its control changes in the window went unmarked.

    The result has one entry for each run in `frame.runs`, in order. While more
    than one run is drawn, `compared_run_line` labels each entry with its run.
    An entry is None when every change inside the window is marked. Both plots
    draw the frame's marks, so each plot reports this count for its own window
    (`PL-L59K`).
    """

    return tuple(
        None
        if not run.undrawn_control_marks
        else compared_run_line(
            UNMARKED_CHANGES_TEMPLATE.format(count=run.undrawn_control_marks), frame, index
        )
        for index, run in enumerate(frame.runs)
    )


def run_label(run: RunId) -> str:
    """Return what this run is called in text, from its identity and never from where it is drawn.

    This is the only place where a run is named, so the legend entry, the
    run's own panel heading and any later view all use the same word. A name
    is only an attribution if the reader can find what it refers to. What it
    refers to is the panel carrying that run's settings.

    The name is the run's number alone. The identity also holds the session,
    which tells two sessions' runs apart for a Workspace's pin (`PL-7Z84`).
    Only a pin can name a run of an earlier session, and `pinned_run_label`
    names it without its number.

    Args:
        run: The run's identity (`layout/run_identity.py`).

    Returns:
        The run's name.

    Raises:
        TypeError: If `run` is not a `RunId`. A position in a tuple of runs
            names whichever run happens to be there, and naming by position
            is what this function replaced.
    """

    if not isinstance(run, RunId):
        raise TypeError(f"a run is named from its RunId, not from {type(run).__name__}")

    return RUN_LABEL_TEMPLATE.format(number=run.number)


def pinned_run_label(pinned: RunId, session: SessionToken) -> str:
    """Return what a Workspace's pinned run is called in the session `session`.

    A saved Workspace keeps its pin, so the pinned run can be one that an
    earlier session of the application placed. That run is never open, and a
    run that is open can carry its number. So it is called
    `EARLIER_SESSION_RUN_TEXT`, without its number (`PL-7H9X`). A run that
    this session placed is called by `run_label`, whether or not it is still
    open.

    Args:
        pinned: The pinned run's identity.
        session: The token of the session that is running now
            (`RunIdentities.session`).

    Raises:
        TypeError: If `pinned` is not a `RunId`, or `session` is not a
            `SessionToken`.
    """

    if not isinstance(session, SessionToken):
        raise TypeError(f"a session is a SessionToken, not {type(session).__name__}")

    name = run_label(pinned)

    if pinned.session != session:
        return EARLIER_SESSION_RUN_TEXT

    return name


def trace_legend_label(style: TraceStyle) -> str:
    """One compartment's legend words: its name and its line style."""

    return TRACE_LEGEND_LABEL_TEMPLATE.format(label=style.label, line_style=style.line_style)


def compared_trace_legend_label(trace: str, run: str) -> str:
    """Return one drawn curve's legend words while more than one run is shown.

    Args:
        trace: The trace's own words: a compartment's words from
            `trace_legend_label`, or the wash-in plot's single trace label.
        run: The run's name, from `run_label`.

    Returns:
        Both dimensions in one entry, in that order.
    """

    return COMPARED_TRACE_LEGEND_TEMPLATE.format(trace=trace, run=run)


def compared_run_line(line: str, frame: ChartFrame, run_index: int) -> str:
    """Return one run's line in a column that the runs share, named while more than one is drawn.

    The wash-in state line and the off-scale notice both sit in the chart
    column rather than on the run's own panel, one line per run. Both carry a
    clinical value. The first is an F_A/F_I that the reader compares with the
    other run's. The second states that a compartment's trace is clipped.
    Neither line used to say which run it belonged to, and stacking order is
    not an attribution. The order is explained nowhere on screen, and the run
    names are in a different splitter section. Read as the other run's, the
    first line inverts the comparison that a branch exists to show. The
    second reports a clipped trace on a run that has none (`PL-25DD`).

    The name is added here rather than built into either line, following
    `compared_trace_legend_label`. What the line says depends on the run's
    state. Whether the line needs its run's name depends on how many runs the
    chart is drawing. So the run's name is a separate fact, joined at the one
    place that knows both.

    A lone run is given no name, because there is nothing to tell it apart
    from. `SimulationView._run_name` applies the same rule to the run
    panels, and both legends apply it to the frame they are given, so a
    single-run display is unchanged. The frame's run is looked up before the
    run count is checked. So an index that matches no run raises on a one-run
    frame too, rather than returning a line that looks right.

    Args:
        line: This run's line, already formatted.
        frame: The frame drawn this tick, which is what says how many runs
            are on the chart and what each is called.
        run_index: Which of the frame's runs the line belongs to.

    Returns:
        The line unchanged while one run is drawn, or the run's name followed
        by the line while more than one run is drawn.

    Raises:
        TypeError: If `run_index` is not an `int` (`RunIndex`).
        ValueError: If `run_index` is negative (`RunIndex`), for the same
            reason that `off_scale_notice` rejects one.
        IndexError: If `run_index` is not one of the frame's runs.
    """

    run = frame.runs[RunIndex(run_index)]

    if len(frame.runs) <= 1:
        return line

    return COMPARED_RUN_LINE_TEMPLATE.format(run=run.label, line=line)


def compared_run_notice(notice_text: str, run_name: str | None) -> str:
    """Return one run's banner in the notice column that the runs share, named while two are drawn.

    The banner sits in a column that both runs write into. All three of the
    notices that `notice` can return assert something about *a* run without
    naming it. A halt says "Simulation stopped". A refusal says "The
    simulation is unchanged and still running its previous setting", which is
    false of the other run. Read as a statement about the whole dashboard
    rather than one run, a halt on the branch says the case has stopped while
    the trunk is still going. A refusal says a setting was not applied to a
    run that did accept it (`PL-TSZM`).

    Stacking order separates these banners even less than it separates the
    chart column's lines, because a banner with nothing to say is hidden
    rather than left blank. With one run halted, the column holds a single
    block whose position moves only by the column's spacing, while the words
    are identical. That spacing was 12 px, measured on 2026-09-21, with
    nothing on screen to measure it against.

    It uses a colon rather than the em dash of `COMPARED_RUN_LINE_TEMPLATE`.
    That is why this is a second function, not the same function with the
    run read from a different place. Every notice already opens with
    `label — detail` ("Simulation stopped — ...", "Setting refused — ..."). So
    an em dash prefix would put two dashes in one sentence at different
    levels. The first would look like the banner's own label separator, with
    "Run 2" as the label. The colon is the same one that
    `OFF_SCALE_NOTICE_TEMPLATE` and the compare-mode legend caption already
    use to limit what follows to one subject.

    It takes the run's name rather than the frame and an index, unlike
    `compared_run_line`, which takes the frame. `run_presentation.halted_run`
    also words the banner, and it states a halt from the run's record alone, because
    the frame is what may have failed (`PL-25KS`). Reading the run count from
    the frame there would drop the attribution in exactly the case it exists
    for. The name that the dashboard gives the run (`SimulationView._run_name`)
    is the same word that `run_label` put on the run's own
    panel and in both legends.

    Args:
        notice_text: The banner's text for this run this tick. A run with
            nothing to say has no banner to name, and
            `run_presentation` does not call this for it.
        run_name: What the dashboard calls this run, from `run_label`, or
            None while only one run is drawn and there is nothing to tell it
            apart from.

    Returns:
        The notice unchanged while one run is drawn, or the run's name
        followed by the notice while two runs are drawn.

    Raises:
        ValueError: If `run_name` is empty, because an empty name names no
            run. An empty name would not fail on its own. It would render a
            banner that opens with a bare colon. A notice that looks
            addressed to a run called nothing is the plausible-looking output
            that `CLAUDE.md` asks to fail instead.
    """

    if run_name is not None and not run_name:
        raise ValueError("a run's name says which run the banner is about, so it cannot be empty")

    if run_name is None:
        return notice_text

    return COMPARED_RUN_NOTICE_TEMPLATE.format(run=run_name, notice=notice_text)


def compared_panel_heading(heading: str, run: str | None) -> str:
    """Return one run's panel heading in a shared column, named while more than one run is drawn.

    The sidebar holds two panels per run, the agent-accounting validation and
    the control-change record, in a column that the runs share. So a branch
    stacks four panels: accounting, control changes, accounting, control
    changes. Nothing on any of them used to say which run it belonged to.
    Both panels make a claim about one run. The accounting panel gives a
    mass-balance status and litres of equivalent pure agent gas. The
    control-change panel gives a list of settings under the words "What was
    changed during this run". Read as the other run's, that list says the
    trunk received an intervention it never got. That inverts the comparison
    a branch exists to show, rather than merely blurring it (`PL-C3GS`).

    The name goes in the heading rather than on each line beneath it, which is
    what makes this different from `compared_run_line`. The chart column holds
    one bare line per run and has no heading to carry the name. A panel has a
    heading whose whole job is to say what the panel holds. Prefixing five
    lines with the same run name would say it five times, and it would look
    like part of each value.

    The function works for any heading and does not know which panel it is
    naming, for two reasons. Every main view will need a heading for each of
    its areas (`.claude/rules/ui-areas.md`). And a heading that moves with its
    own panel still works when a reader rearranges the column, where one group
    heading above both panels would not.

    Args:
        heading: The panel's own heading words.
        run: The run's name, from `run_label`, or `None` while one run is
            drawn. `SimulationView._run_name` already applies that rule to
            the run panels, and both legends apply it to the frame they are
            given. So a single-run display gains no standing text.

    Returns:
        The heading unchanged while one run is drawn, or the heading followed
        by the run's name while more than one run is drawn.
    """

    if run is None:
        return heading

    return COMPARED_PANEL_HEADING_TEMPLATE.format(heading=heading, run=run)


def compartment_cap_notice(frame: ChartFrame) -> str | None:
    """Return what the chart says while the two-compartment cap keeps traces off it.

    This is conditional text. It appears only in the state it explains, and
    costs nothing otherwise (`.claude/rules/ui-reader.md`). It earns a
    sentence because it explains two things that a reader would otherwise
    have to guess. One is why four traces left the chart when the second run
    arrived. The other is why checking a third box unchecks the box that has
    been checked longest (`CompartmentSelection.with_compartment`). Neither
    can be explained by a label, a unit or an axis title.

    It appears whenever the cap is *in force*, not according to a count of
    removed traces. The dashboard keeps its compartment selection within the
    cap from the moment the second run appears
    (`CompartmentSelection.with_run_count`). So by the time a frame is
    assembled, the count of removed traces is zero, yet the reader has still
    lost four curves.

    Args:
        frame: The frame drawn this tick.

    Returns:
        The notice, or None while one run is drawn and nothing is capped.
    """

    if len(frame.runs) <= 1:
        return None

    return COMPARED_CAP_NOTICE_TEMPLATE.format(cap=COMPARED_COMPARTMENT_CAP)


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
    """The confirmation asked before recorded work is discarded for a new case.

    Two questions take this shape: a new agent discarding the run
    (`new_case_question`), and the trunk's Reset discarding a branch
    (`trunk_reset_question`). Both start the case over.

    Attributes:
        title: Names what the reader would start, or the runs a Reset ends.
        body: Three statements in the order a reader meets them: why this
            is a new case at all, what is about to be lost, and what
            survives. They are three statements rather than one paragraph,
            because they answer three different questions, and a reader stops
            at the first one that satisfies them.
        discard_label: The destructive action, drawn first and outlined.
        keep_label: The safe action, drawn last and filled. It is the
            default, so the press a reader makes without reading keeps their
            case.
    """

    title: str
    body: tuple[str, str, str]
    discard_label: str
    keep_label: str


def new_case_question(
    snapshot: SimulationSnapshot, new_agent_display_name: str, adjustment_count: int
) -> NewCaseQuestion:
    """Return the confirmation for one proposed new case.

    Args:
        snapshot: The run that would be discarded.
        new_agent_display_name: The agent the reader selected, named as the
            reader sees it.
        adjustment_count: How many control changes the run holds. They are
            counted through the same grouping that the panel beside the chart
            uses to list them. So the count of what is about to be lost and
            the list of it cannot come from two different readings of one
            record.

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


@dataclass(frozen=True, slots=True)
class BranchAtStake:
    """One drawn branch that the trunk's Reset would discard, as the question states it.

    Attributes:
        name: What the branch is called on screen (`run_label`).
        began_at_s: The case instant it branched at.
        elapsed_s: The case instant it has run to, or None where its
            snapshot refuses a value and the instant could not be read.
        adjustment_count: How many control changes it holds, counted as its
            "Control changes" panel lists them.
    """

    name: str
    began_at_s: CaseInstant
    elapsed_s: CaseInstant | None
    adjustment_count: int


def branch_at_stake(
    name: str, began_at_s: CaseInstant, snapshot: SimulationSnapshot | None, adjustment_count: int
) -> BranchAtStake | None:
    """Return whether a trunk's Reset would discard work in this branch, and what work.

    A branch holding nothing is not at stake, as judged by
    `has_recorded_run`. The same test spares the reader the new-case
    question. If the question were asked when nothing would be lost, the
    reader would be answering it without reading by the time something
    would be. A branch
    whose snapshot raises on a value is at stake, because what it holds cannot
    be read. Discarding unread work without asking is the outcome this
    question exists to prevent.

    Args:
        name: What the branch is called on screen.
        began_at_s: The case instant at which it branched, from its
            controller.
        snapshot: Its snapshot, or None when reading one raised.
        adjustment_count: How many control changes it holds, grouped as its
            panel lists them.

    Returns:
        What the question states about the branch, or None where the branch
        holds nothing.
    """

    if snapshot is not None and not snapshot.has_recorded_run:
        return None

    return BranchAtStake(
        name=name,
        began_at_s=began_at_s,
        elapsed_s=None if snapshot is None else snapshot.elapsed_s,
        adjustment_count=adjustment_count,
    )


def trunk_reset_question(trunk_name: str, branches: Sequence[BranchAtStake]) -> NewCaseQuestion:
    """Return the confirmation asked before the trunk's Reset discards branches holding work.

    `docs/INTERFACE.md` § "Discarding a run, and the questions that guard it"
    requires it. That section exempts
    Reset from its confirmation only for the run whose button was pressed, and
    a branch is another run (`PL-W5WX`).

    Args:
        trunk_name: What the trunk is called on screen.
        branches: The drawn branches holding work, in drawing order.

    Returns:
        The question's text.

    Raises:
        ValueError: If no branch is given, because a Reset that discards
            nothing asks nothing. Also if an instant is negative or not finite
            (`format_branch_discard_warning`, through `format_elapsed`).
    """

    if not branches:
        raise ValueError("a trunk's Reset asks only before it discards a branch; none was given")

    # While `MAX_DISPLAYED_RUNS` is 2, only one branch can be drawn, so each
    # join below holds one branch. The joins stay so that a higher limit cannot
    # leave a branch that the Reset discards out of the question.
    names = " and ".join(branch.name for branch in branches)

    return NewCaseQuestion(
        title=TRUNK_RESET_TITLE_TEMPLATE.format(
            reset=RESET_LABEL, trunk=trunk_name, branches=names
        ),
        body=(
            TRUNK_RESET_ENDS_BRANCHES_TEMPLATE.format(trunk=trunk_name, reset=RESET_LABEL),
            " ".join(
                format_branch_discard_warning(
                    branch.name, branch.began_at_s, branch.elapsed_s, branch.adjustment_count
                )
                for branch in branches
            ),
            TRUNK_RESET_KEEPS_TEMPLATE.format(trunk=trunk_name),
        ),
        discard_label=TRUNK_RESET_DISCARD_TEMPLATE.format(reset=RESET_LABEL, branches=names),
        keep_label=KEEP_BRANCHES_TEMPLATE.format(branches=names),
    )


def readout_row_width(columns: int, panel_widths_px: Sequence[float], spacing_px: float) -> float:
    """Return the width of the narrowest row that fits the panels `columns` across.

    Panels fill the grid row by row. So column `j` holds every panel whose
    index is `j` modulo `columns`, and the column is as wide as the widest of
    those panels. The row's width is the sum of those column widths plus
    `columns - 1` gaps of `spacing_px`.

    Args:
        columns: How many panels stand side by side. At least one.
        panel_widths_px: The width each panel reserves, in row order.
        spacing_px: The gap between neighbouring columns, in logical pixels.

    Raises:
        ValueError: If `columns` is less than one, because a row cannot fit
            its panels into no columns.
    """

    if columns < 1:
        raise ValueError(f"a readout row seats its panels in at least one column, not {columns}")

    occupied = min(columns, len(panel_widths_px))
    column_widths = (max(panel_widths_px[first::columns]) for first in range(occupied))
    return sum(column_widths) + (columns - 1) * spacing_px


def readout_columns(width_px: float, panel_widths_px: Sequence[float], spacing_px: float) -> int:
    """Return how many readout panels stand side by side at this width.

    The result is the largest count in `READOUT_ROW_LADDER` whose panels fit.
    The panels fit when the row width that `readout_row_width` gives for that
    count is no more than `width_px`. The result is never less than one
    column, however narrow the row, because a row must hold its panels
    somewhere. Each panel's width is the width that the widget measured and
    reserved: the widest value its column can show, in the rendering font
    (`PL-3355`). So the row steps down exactly where a panel would otherwise
    be clipped, at whatever width that is on the reader's display
    (`PL-8M05`).

    Args:
        width_px: The readout row's width, in logical pixels.
        panel_widths_px: The width each panel reserves, in row order, in
            logical pixels.
        spacing_px: The gap between neighbouring columns, in logical pixels.

    Returns:
        The column count: 7, 4, 2 or 1.
    """

    for columns in READOUT_ROW_LADDER:
        if readout_row_width(columns, panel_widths_px, spacing_px) <= width_px:
            return columns

    return READOUT_ROW_LADDER[-1]


def input_frame_wait_ms(frame_cost_ms: float) -> int:
    """Return how long to wait after a dial input's frame before the next one may draw, in ms.

    The next frame starts `INPUT_FRAME_INTERVAL_MS` after this one started,
    or twice this frame's cost after it started, whichever is later. A cheap
    frame therefore lets the charts follow a moving dial at Nielsen Norman
    Group's 0.1 s limit. A frame that takes longer than half the interval,
    such as one that draws a preview over a long run, leaves the thread free
    for at least as long as it drew, so a moving dial never takes more than
    half of the time in which the run's steps and the reader's inputs are
    handled (`PL-NKFD`). The result is rounded up to a whole millisecond,
    because that is what a timer takes.

    Raises:
        ValueError: `frame_cost_ms` is negative or not finite. A wall-clock
            difference can be neither, so either means the caller measured
            the wrong thing.
    """

    if not isfinite(frame_cost_ms) or frame_cost_ms < 0.0:
        raise ValueError(
            f"a frame's cost must be a finite number of ms >= 0, got {frame_cost_ms!r}"
        )

    return ceil(max(INPUT_FRAME_INTERVAL_MS - frame_cost_ms, frame_cost_ms))
