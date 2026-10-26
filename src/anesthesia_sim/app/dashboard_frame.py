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
"common gas outlet" (`PL-71CF`). Each is stated in `docs/MODEL.md` and
enforced by an exact-string test.
"""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final

from anesthesia_sim.app.bookmarks import (
    BookmarkSet,
    BookmarkStandings,
    MacTarget,
    MarkStanding,
    TimeBookmark,
)
from anesthesia_sim.app.chart_frame import (
    COMPARED_COMPARTMENT_CAP,
    ChartFrame,
    RunCount,
    RunIndex,
    TraceStyle,
    trace_style,
)
from anesthesia_sim.app.chart_time_base import TIME_BASE_LADDER
from anesthesia_sim.app.control_record import CONTROL_INPUT_DISPLAY_UNITS, ControlInput
from anesthesia_sim.app.control_timeline import ControlAdjustment, format_adjustment
from anesthesia_sim.app.controller import (
    HereForkPoint,
    MarkForkPoint,
    RunRecord,
    RunSettings,
    RunStatus,
    SimulationSnapshot,
)
from anesthesia_sim.app.formatting import (
    CONCENTRATION_DISPLAY_DECIMALS,
    CONCENTRATION_DISPLAY_RESOLUTION_PERCENT,
    DECIMAL_BASE,
    FLOW_DISPLAY_DECIMALS,
    MAC_UNIT_SUFFIX,
    format_agent_residual,
    format_agent_volume,
    format_branch_discard_warning,
    format_case_discard_warning,
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
    render_mac_multiple,
)
from anesthesia_sim.app.playback import SUPPORTED_PLAYBACK_RATES, PlaybackRate
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.app.wash_in import WashInDomain, read_wash_in
from anesthesia_sim.core.concentration import Fraction, fraction_from_percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError, SimulationDomainLimitError
from anesthesia_sim.core.parameters import AGENT_DATA_FILENAMES, load_agent_parameters
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MINIMUM_CARDIAC_OUTPUT_L_MIN,
    CaseInstant,
)
from anesthesia_sim.core.units import MINUTES_PER_HOUR, SECONDS_PER_HOUR, SECONDS_PER_MINUTE
from anesthesia_sim.layout.run_identity import RunId

# The step that each simulation tick advances by. `core/` declares which steps
# are *supported*: `core.simulation_step.MINIMUM_SIMULATION_STEP_S` and
# `MAXIMUM_SIMULATION_STEP_S` are that declaration. `SimulationStep` rejects a
# step outside them when it is built, which here happens at import, so no such
# step reaches a run that is displayed. The value below is a choice of cadence
# inside that range, and it sits at the ceiling deliberately. A finer step buys
# nothing a reader could see: halving the step moves a displayed fraction by
# around 1e-16. A coarser step costs control resolution. That the chosen step
# equals the ceiling is a fact about this configuration, not an identity. So
# the two are named separately, and
# `test_the_shipped_step_is_within_the_maximum_simulation_step` checks the
# relation. `docs/MODEL.md` § "Supported simulation step" and § "Displayed
# precision" give the two derivations separately (`PL-X9KD`).
SIMULATION_STEP_S: Final = SimulationStep(0.1)
# How often the simulation timer fires, in *real* seconds. It is numerically
# equal to the step but means something different. The playback multiplier is
# the ratio between the two. A tick advances `rate.steps_per_tick(...)` steps
# of `SIMULATION_STEP_S`. That is `multiplier` times faster than real time only
# because a tick is one step long (`app/playback.py`,
# `test_a_tick_is_one_simulation_step_of_real_time`). The interval is also the
# interface's control resolution (`PL-NBWP`). A tick advances its whole burst
# without interruption. So a setting changed while the run plays first takes
# effect at a tick boundary, and tick boundaries are `multiplier` times this
# interval apart in simulated time.
SIMULATION_TICK_INTERVAL_S: Final = float(SIMULATION_STEP_S)
# How often the display redraws, independent of the simulation step. It is
# twice the tick, so a frame spans two control-grid steps at every playback
# rate. That is why `PL-NBWP` left the grid where it is. The value is written
# as its own number rather than derived from the tick, because a display
# cadence and a timer cadence are separate decisions.
# `test_a_frame_is_two_control_grid_steps_at_every_rate` checks the relation
# instead.
RENDER_INTERVAL_S: Final = 0.2
# How wide the chart is before the first frame is drawn. It is the narrowest
# rung, which is the width "Fit run" chooses for a run that has recorded
# nothing.
INITIAL_CHART_TIME_BASE: Final = TIME_BASE_LADDER[0]

# How many runs the dashboard may draw at once. The limit is two for two
# reasons. Two is what `ROADMAP.md` § "v0.5.0 - the case you can branch" puts
# in its own out-of-scope list. And the encoding that tells one run from
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
# row sits on one baseline (`PL-8M05`). The line holds a non-breaking space
# rather than an empty string. The Flet build needed it because a blank line
# collapsed to zero height there. It is kept because `tools/glyph_check.py`
# names these two constants as the evidence for U+00A0, and a test asserts
# that the line holds a value.
EMPTY_METRIC_QUALIFIER: Final = " "
# The same spacer for the second-unit line. The "Simulated time" panel has no
# MAC multiple, and the spacer makes it the same height as the six panels that
# do.
EMPTY_METRIC_SECONDARY_VALUE: Final = " "

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

# The four status words. There are four states, not two. A stopped run must
# never be shown as paused, and the two stopped states must not be confused
# with each other. A failure says the model reached a state it could not step
# from. The supported run length says the model reached the end of what it is
# claimed to represent, having done everything right.
STATUS_PAUSED_TEXT: Final = "Paused"
STATUS_RUNNING_TEXT: Final = "Running"
STATUS_FAILED_TEXT: Final = "Stopped — simulation error"
STATUS_SUPPORTED_LIMIT_TEXT: Final = "Stopped — supported run length reached"

# The three notice banners, in precedence order. The stopped-run wording says
# what the values *are* rather than warning about them. Rolling the failed
# step back is what made that possible (`PL-026`). Whether a step was rolled
# back is for the failure itself to say, and `SimulationNumericalError`'s
# message does say it. The banner no longer says it of every failure, because
# a setting that raised (`PL-YK2V`) and a displayed value that the interface
# rejected (`PL-7DJK`) failed no step. The run-length wording does not reuse
# the failure's wording. Nothing failed and nothing was rolled back, and
# describing a correct model as a broken one is the safety defect that
# `CLAUDE.md` names (`PL-Y5WR`). The wording says why the limit exists, because
# a boundary given with no reason looks like an arbitrary restriction.
#
# Both failure wordings end with `{exit}`, which names the way out. Normally
# that is `RESET_EXIT_TEXT`, because Reset is the only way out of a stopped
# run. When Reset itself was refused, `refused_reset_exit` names the other way
# out instead. Sending a reader back to the control that was just refused
# would be an instruction that the screen already knows cannot be followed
# (`PL-M4M0`). The run-length wording keeps its own Reset line. A refused Reset
# halts the run as a failure, and a failure outranks the limit, so the
# run-length banner never needs another exit.
RESET_EXIT_TEXT: Final = "Reset to start a new run."
FAILURE_NOTICE_TEMPLATE: Final = (
    "Simulation stopped — {failure_reason}. The values shown are the last completed step. {exit}"
)
# The failure banner as `RunView.present_halt` writes it, before any frame of
# the stopped run has been drawn. At that point the chart and the readouts
# still show the frame drawn before the stop, which is not the step the run
# stopped at. So "the values shown are the last completed step" would be the
# stale-state misreading that the hazard table names. `refresh` replaces this
# banner with `FAILURE_NOTICE_TEMPLATE` on the first frame that draws. Which of
# the two banners is shown is therefore decided by whether a frame drew, not
# guessed from the reason (`PL-7DJK`).
UNDRAWN_FAILURE_NOTICE_TEMPLATE: Final = (
    "Simulation stopped — {failure_reason}. No frame of the stopped run could be drawn: "
    "the chart and the readouts show the last frame drawn before it stopped, and the "
    "run itself stands at its last completed step. {exit}"
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
# Which wording states the refusal depends on the banner's reason. On a run
# that had not failed, or whose recorded failure is this same refusal, the
# halt's reason is the refusal, so the exit refers to it. On a run that had
# failed for something else, the controller keeps that earlier reason
# (`SimulationController.fail`). The exit then states the refusal itself, in
# the form in which the failure line gives a reason (`PL-M4M0`).
REFUSED_RESET_EXIT_TEMPLATE: Final = "Reset was refused for this reason. {way_out}"
REFUSED_RESET_AFTER_FAILURE_EXIT_TEMPLATE: Final = "Reset was refused — {reason}. {way_out}"
REFUSED_RESET_WAY_OUT_TEXT: Final = (
    "No setting can repair this, because only a fault in the simulator causes it. "
    "Close and reopen the application to start a new run."
)

# What the chart says when a reader has unchecked every compartment. A plot
# with all six missing is a blank panel. A blank panel looks like a display
# that has failed, not like one showing what it was asked to show.
NO_TRACES_SHOWN_TEXT: Final = (
    "No compartment traces are shown. Check a compartment above to draw it — "
    "the readouts and the run itself are unaffected."
)

# Shown when a drawn trace goes above the top of the plot, naming the traces
# that do. A setting in common use exceeds the fixed axis
# (`CHART_AXIS_TOP_MAC`): sevoflurane's 8% dial setting is 4.00 MAC. A trace
# clipped at the ceiling draws as a horizontal line, which is what a plateau
# looks like. Growing the axis to fit was rejected, because it would redraw the
# curve at a smaller height partway through the induction it is being used to
# teach.
OFF_SCALE_NOTICE_TEMPLATE: Final = (
    "Above the top of the plot: {compartments}. The axis stops at {top} and these "
    "traces are cut off there — their values are in the readouts above, which are "
    "not clipped."
)

# The control-change panel. It lists the newest change first, because it is a
# fixed panel beside a chart rather than a scrolling history. It lists a
# limited number of changes and says how many it left out.
NO_CONTROL_CHANGES_TEXT: Final = "No settings changed yet in this run."
MAX_LISTED_ADJUSTMENTS: Final = 12
CONTROL_TIMELINE_HEADING: Final = "Control changes"
CONTROL_TIMELINE_CAPTION: Final = (
    "What was changed during this run, most recent first. Settings only — not a measurement."
)
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

# The separator between a mark's value and the name the learner gave it. An
# en dash, which `tools/glyph_check.py` records as rendered.
MARK_LABEL_JOINER: Final = " – "

# What a row says about how far the run has got with the mark it lists
# (`PL-CTD7`). This is conditional text rather than standing text, which is
# the distinction `.claude/rules/ui-reader.md` draws. A row for a mark that the
# run can still reach says nothing at all. So the words appear on exactly the
# rows whose state a reader would otherwise have to infer from silence.
#
# **The three negative answers are worded differently on purpose.** "Not
# reached" alone would be true of all three. It would tell a learner that a
# bookmark before this branch's fork might still arrive if they kept running,
# which it cannot. `bookmarks.MarkStanding` gives the argument, and
# `CLAUDE.md`'s safety-critical standard is what rules out that
# plausible-looking answer. `NOT_REACHED_WITHIN_CAP` names the run length
# rather than a number of hours, so the figure is written in one place only:
# `core/supported_ranges.py` and `docs/MODEL.md` § "Supported run length".
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
# That is the plausible-looking answer again, and a learner reading two
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
# that run was paused, which is most of the time a learner reads this row. It
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

# The bookmark editor's own words. They are field labels rather than
# sentences, which is the form in which `.claude/rules/ui-reader.md` asks a
# specialist reader's screen to carry its meaning. "Compartment" and "Height"
# say what the control sets. What a height on a given compartment does and
# does not assert is stated in `docs/MODEL.md` § "MAC multiples as a display
# unit", not in a paragraph in a dialog.
# The branch control's words follow, beside the marks and for the same reason.
# Both offer instants of the *case* rather than of either run, so both are
# panels of the dashboard rather than of a `RunView` (`docs/ARCHITECTURE.md`
# § "Where new code belongs"). "From" labels the instant at which the branch
# opens. The heading names the mechanism and says nothing else, under the same
# rule as the mark headings.
FORK_HEADING: Final = "Branch"
FORK_POINT_LABEL: Final = "From"
# The label is "Branch", not "Branch here" (`PL-Y2SL`). On the button below,
# "here" names where the paused trunk stands, while this button branches at
# the point that "From" names. Two adjacent buttons whose labels start with
# the same words but do different things invite the wrong press. A branch
# taken at the wrong instant can then be ended only with the trunk's Reset,
# because only one comparison is allowed at a time.
TAKE_FORK_LABEL: Final = "Branch"
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
# the one a learner reaches for, because the branch is the run they are trying
# to end. So the sentence names both. `comparing_fork_lock_text` fills it from
# the runs' names and `RESET_LABEL`, which stops an instruction and the
# control it names from drifting apart again.
#
# The text states what the trunk's Reset costs as well as what it ends.
# Sending a learner to a control that discards every run, without saying so,
# would be the same defect with the consequence hidden instead of the label.
COMPARING_FORK_LOCK_TEMPLATE: Final = (
    "One comparison at a time. {trunk}'s {reset} ends it and starts the case over; "
    "{branch}'s {reset} only returns {branch} to where it branched."
)
FORK_NOTHING_SELECTED_TEXT: Final = "Select an instant to branch at"

# The fork where the paused trunk stands. It is a second control rather than
# a row in the selector above. A learner who pauses can branch there, and that
# is the default action (project owner, 2026-10-12: "if I pause I should be
# able to branch from there too"), because it is the one control labelled with
# the instant the learner is looking at. The selector remains the way to
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
HERE_FORK_LABEL_TEMPLATE: Final = "Branch here: {instant}"
# The same control's words when a mark stopped the trunk where it stands.
#
# **The instant is the halt's, not the mark's, and the wording keeps the two
# apart.** A mark that lies inside a step halts the run at the end of that
# step. So the instant a learner marked and the instant at which the branch
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
# a learner who misreads it or a measurement. But a rewrite must not
# reintroduce the wording it was chosen over.
HALT_FORK_LABEL_TEMPLATE: Final = "Branch here: {instant}, stopped on your mark"
# This clause ends either label above, or a mark's entry in the selector below,
# when the trunk changed a setting at the instant where the branch opens.
# `HereForkPoint.setting_changed_here` and `MarkForkPoint.setting_changed_at_fork`
# record whether the trunk did. A branch taken where the trunk stands, or at a
# mark, opens under the settings from before that change. The selector's
# keyframe entry at the same instant opens under the change (`PL-ZR49`).
# Without the clause, two controls would show one instant and open under
# different settings. The wording is a placeholder chosen in `PL-ZR49`. The
# project owner's rule of 2026-10-18 lets the session doing the work decide
# wording while the interface is being built. The clause follows the ratified
# words of each label and does not change them.
BEFORE_CHANGE_FORK_LABEL_SUFFIX: Final = ", before your change"
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
# within the supported run. Hours are less than the run length in hours,
# minutes and whole seconds are less than 60, and the tenth is nonzero. Each
# range starts at 1, so that a reading built from them includes every part
# (`PL-NC0D`).
_CLOCK_HOURS: Final = range(1, int(MAXIMUM_ELAPSED_SIMULATION_TIME_S // SECONDS_PER_HOUR))
_CLOCK_MINUTES: Final = range(1, int(MINUTES_PER_HOUR))
_CLOCK_WHOLE_SECONDS: Final = range(1, int(SECONDS_PER_MINUTE))
_TENTHS_PER_SECOND: Final = 10
_CLOCK_TENTHS: Final = range(1, _TENTHS_PER_SECOND)


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
    run has passed is the widest kind of entry. It holds a clock reading, as
    a control event's entry does, followed by the words of
    `MARK_FORK_LABEL_TEMPLATE`. Where the trunk changed a setting at the
    mark's fork, `BEFORE_CHANGE_FORK_LABEL_SUFFIX` comes last. The widest
    clock reading is found by measuring, not by counting characters. A
    proportional font gives its digits different widths, so 23h59m59.9s, the
    reading at the last step, is not the widest. Hours, minutes and seconds
    vary independently. So the widest value of each, put together, is the
    widest reading that `format_elapsed` writes within the supported length
    of a run.

    Args:
        advance_px: How wide a string draws in the selector's font, in
            pixels.

    Returns:
        The entry for a mark passed at the instant with the widest reading,
        with the clause for a setting changed there.
    """

    # Each part is measured as `format_elapsed` writes it alone, so the
    # measured text follows the clock's own format (`PL-G84G`).
    hours = max(_CLOCK_HOURS, key=lambda hour: advance_px(format_elapsed(hour * SECONDS_PER_HOUR)))
    minutes = max(
        _CLOCK_MINUTES, key=lambda minute: advance_px(format_elapsed(minute * SECONDS_PER_MINUTE))
    )
    whole, tenth = max(
        ((whole, tenth) for whole in _CLOCK_WHOLE_SECONDS for tenth in _CLOCK_TENTHS),
        key=lambda second: advance_px(format_elapsed(second[0] + second[1] / _TENTHS_PER_SECOND)),
    )
    instant_s = (
        hours * SECONDS_PER_HOUR + minutes * SECONDS_PER_MINUTE + whole + tenth / _TENTHS_PER_SECOND
    )

    return (
        MARK_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(instant_s))
        + BEFORE_CHANGE_FORK_LABEL_SUFFIX
    )


BOOKMARK_DIALOG_TITLE: Final = "Bookmarks"
EDIT_BOOKMARKS_LABEL: Final = "Edit bookmarks"
CLOSE_BOOKMARKS_LABEL: Final = "Close"
ADD_MARK_LABEL: Final = "Add"
REMOVE_MARK_LABEL: Final = "Remove selected"
INSTANT_FIELD_LABEL: Final = "Instant"
COMPARTMENT_FIELD_LABEL: Final = "Compartment"
HEIGHT_FIELD_LABEL: Final = "Height"
MARK_NAME_FIELD_LABEL: Final = "Name"
MARK_NAME_PLACEHOLDER: Final = "Optional"
# The unit in which an instant is entered, and the resolution of the entry.
# The unit is seconds rather than the compound form the clock shows, because a
# spin box states one unit and the compound form has three. The dialog
# restates the entered value in the compound form beside the control, so no
# reader has to convert between them. One decimal place matches the
# simulation step, which is the finest instant a run can stop at.
INSTANT_ENTRY_SUFFIX: Final = " s"
INSTANT_ENTRY_DECIMALS: Final = 1
INSTANT_ENTRY_STEP_S: Final = 1.0
# The upper bound of the height control before an agent has been named. Every
# shipped agent's vaporizer reaches at least this multiple of its own 1 MAC.
# So this value is a lower bound on the real limit rather than a guess at it.
# `BookmarkDialog.set_reachable_height` replaces it with the running agent's
# own limit the first time a frame is drawn.
DEFAULT_MAXIMUM_TARGET_MAC: Final = 3.0

REMOVE_NOTHING_SELECTED_TEXT: Final = "Select a mark to remove it."
"""Conditional text, which is where a sentence is appropriate.

It appears only after a press that did nothing, and costs nothing when it
does not appear (`.claude/rules/ui-reader.md`). The two empty-list lines above
are standing text, and are labels for that reason."""
# Names the substance that the six readouts belong to (`PL-TCD1`). It is a
# label rather than a sentence. It says "Modelled" rather than giving a bare
# agent name, because the hazard on this row is a reader comparing these
# values with a monitor.
COMPARTMENT_SUBSTANCE_TEMPLATE: Final = "Modelled concentrations: {agent}"

# The dial's setting on the readout heading line, in the two units that the
# dial prints it in. This labels a setting, not a modelled value, so the word
# is the dial's own: what the vaporizer is set to deliver (`PL-NWTM`).
DELIVERED_LINE_TEMPLATE: Final = "Delivered {value} ({secondary})"

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
    "Delivered {agent} starts at that agent's own 1 MAC."
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
# says so (`PL-TG60`). The two residual lines print only the power of ten that
# each value is less than. An order of magnitude is the whole purpose of those
# lines, and it is the only meaningful digit a rounding residual has
# (`PL-3PJZ`).
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
# the span actually drawn, because the width is a mode (`PL-012`). The same
# plot showing fifteen minutes and showing twelve hours makes two different
# claims about what a flat trace means. Under "Fit run" the caption says both
# that the whole run is drawn and how wide the plot had to be to draw it. The
# selector then names only the rule, and this line is the only one that names
# the resulting width.
CHART_HEADING: Final = "Agent concentration and relative partial pressure over time"
FITTED_TIME_AXIS_CAPTION_TEMPLATE: Final = "whole run so far, {span} shown"
CHOSEN_TIME_AXIS_CAPTION_TEMPLATE: Final = "{span} shown"

# The wash-in section. "Modelled, not measured" is its own line rather than
# the end of a paragraph. The safety standard requires those three words, and
# at the end of a long sentence nobody reads them (`PL-F9TQ`).
WASH_IN_HEADING: Final = "Wash-in: F_A/F_I, alveolar as a fraction of the modelled circuit"
WASH_IN_DENOMINATOR_TEXT: Final = (
    "F_I = modelled circuit, not the vaporizer dial — a rise across a control mark "
    "can be the denominator moving, not uptake"
)
WASH_IN_MODELLED_TEXT: Final = "Modelled, not measured"
WASH_IN_TRACE_LEGEND_LABEL: Final = "F_A/F_I (solid)"
EQUILIBRIUM_LEGEND_LABEL: Final = "Equilibrium, F_A = F_I (wide dash)"
CONTROL_MARK_LEGEND_LABEL: Final = "Control change (vertical, fine dash)"
#: The MAC-awake band's legend words: a population value with its spread,
#: and the trace that the band is read against (`PL-90Y6`).
MAC_AWAKE_BAND_LEGEND_LABEL: Final = "MAC-awake (population, ±1 SD; read against vessel-rich trace)"
#: What assistive technology announces for a compartment's legend box. It
#: names the action the box performs, not the pattern words beside it, which
#: describe the line rather than the control. It is carried over from the Flet
#: legend's semantics label, so the port loses nothing a screen reader had.
TRACE_TOGGLE_ACCESSIBLE_NAME_TEMPLATE: Final = "Draw the {label} compartment on the chart"
#: A compartment's legend words: its name and its line style, so the style can
#: be read without looking at the plot (`docs/MODEL.md` § "The six
#: compartment traces"). It is one template rather than an f-string at each
#: legend row. The compare-mode row has to say the same words as the checkbox
#: above it, or the two would describe one curve differently.
TRACE_LEGEND_LABEL_TEMPLATE: Final = "{label} ({line_style})"
#: What a run is called in text. `docs/MODEL.md` § "Minimum displayed outputs"
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
#: Shown while the two-compartment cap is keeping traces off the chart. It
#: names the limit, what the limit removed, and where those values can still
#: be read. The last part matters because
#: `docs/MODEL.md` § "Minimum displayed outputs" makes the readouts what keeps
#: a capped compartment on the display.
#: A reader told only that a trace is gone has been told half of the story.
COMPARED_CAP_NOTICE_TEMPLATE: Final = (
    "Two runs are shown, so the chart draws at most {cap} compartments at once. "
    "Every compartment's value is in the readouts below, for both runs."
)
# What the wash-in plot is showing at this instant. A trace that stops has
# to say at which of its two boundaries it stopped. "Nothing has reached the
# circuit yet" and "the patient is giving agent back" are opposite
# situations, and a reader shown only an empty plot could tell neither.
WASH_IN_STATE_TEMPLATE: Final = "Now: F_A/F_I = {ratio}"
WASH_IN_NOT_DEFINED_TEXT: Final = "Not defined: no agent has reached the circuit yet."
WASH_IN_ELIMINATION_TEXT: Final = (
    "Past equilibrium: alveolar exceeds inspired — the patient is returning agent, "
    "which is elimination and not wash-in."
)
WASH_IN_UNDRAWN_SUFFIX_TEMPLATE: Final = " ({count} earlier stretch(es) not drawn)"

# The two standing statements. The first says what the tool is *for*. The
# second, placed beside the readouts themselves, says how to read a number on
# it (`PL-2K1R`). The compartments this simulator exists to display are the
# ones no monitor shows. So a reader has no measured value to check a trace
# against, and the polish of the display suggests more accuracy than there
# is. Each statement appears once, on the readout section's heading row,
# because a repeated disclaimer stops being read.
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


def status_word(status: RunStatus) -> StatusWord:
    """Return the run's status word: failure, then supported limit, then running, then paused.

    A failure outranks the supported run length for the reason `notice`
    gives. The two cannot both arise from one run, and if a failure is
    somehow recorded, it is the more serious statement.

    Args:
        status: The run's status this tick, either a `RunStatus` or the
            snapshot carrying one. `RunView.present_halt` passes a
            `RunStatus`, which is read without building any compartment
            value. So a halt is worded from facts that cannot fail
            (`PL-7DJK`).

    Returns:
        The word and its emphasis.
    """

    if status.failure_reason is not None:
        return StatusWord(STATUS_FAILED_TEXT, Emphasis.WARNING)

    if status.supported_limit_reason is not None:
        return StatusWord(STATUS_SUPPORTED_LIMIT_TEXT, Emphasis.MUTED)

    if status.is_running:
        return StatusWord(STATUS_RUNNING_TEXT, Emphasis.ACCENT)

    return StatusWord(STATUS_PAUSED_TEXT, Emphasis.MUTED)


@dataclass(frozen=True, slots=True)
class ReadoutPanel:
    """The fixed part of one readout panel: its name, its gloss and what it shows.

    Attributes:
        name: The modeled quantity, in the model's own terms.
        qualifier: What a clinician would compare that quantity against, or
            None where nothing measured corresponds to it. It is drawn
            smaller than the name because it is the weaker claim of the two.
            The compartment is what the model computes, and the measurement
            is what a clinician would compare it with. Type of equal size
            would present them as two names for one quantity (`PL-NV9W`,
            `PL-8M05`).
        quantity: The compartment the panel shows, or None for the clock.
    """

    name: str
    qualifier: str | None
    quantity: RecordedQuantity | None


# The seven panels in row order. The gloss is "end-tidal-equivalent", never
# "end-tidal". `docs/MODEL.md` § "Minimum displayed outputs" requires the
# hedge, because dead space, airway sampling delay, shunt and V/Q mismatch are
# all listed in its "Known limitations". So this value is not end-tidal in any
# patient. End-tidal is the name of a *measurement*, and it is the one a
# clinician would most readily compare this readout with. Do not shorten
# either gloss to fit a layout.
# `test_the_alveolar_readout_is_labelled_end_tidal_equivalent` checks the pair.
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
    """

    name: str
    qualifier: str
    value: str
    secondary: str


def _compartment_fraction(snapshot: SimulationSnapshot, quantity: RecordedQuantity) -> Fraction:
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

        if panel.quantity is None:
            value = format_elapsed(snapshot.elapsed_s)
            secondary = format_playback_rate(playback_rate.multiplier)
        else:
            fraction = _compartment_fraction(snapshot, panel.quantity)
            value = format_percent(fraction)
            secondary = format_mac_multiple(fraction, mac_percent)

        panels.append(Readout(panel.name, qualifier, value, secondary))

    return tuple(panels)


# The widest string that each readout column can show, so a panel can reserve
# its width once instead of moving as a value changes length (`PL-3355`).
# The value line is the clock's reading just before the supported run length,
# which has every part of the compound form, including tenths. The second
# line is the longest playback rate. A percent readout and a MAC multiple are
# both shorter than these at every value the dial can reach. The strings are
# chosen by character count from the formatters' own extremes, and the widget
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
#: The widest strings a compartment column can show: the percent at a whole
#: atmosphere, and that fraction as a multiple of the smallest 1 MAC any
#: shipped agent has, since the smallest divisor prints the most digits.
WIDEST_COMPARTMENT_VALUE: Final = format_percent(Fraction(1.0))
WIDEST_COMPARTMENT_SECONDARY: Final = max(
    (
        format_mac_multiple(Fraction(1.0), load_agent_parameters(agent_id).mac_percent)
        for agent_id in AGENT_DATA_FILENAMES
    ),
    key=len,
)
#: The text that a readout card shows instead of its ×MAC number during a halt that
#: follows an agent change. The card still holds the last frame's value, divided by
#: the old agent's MAC, while the 1 MAC line already states the new agent's 1 MAC
#: (`PL-6RJ0`). The text keeps the ×MAC unit, so the card's line still says which
#: value is missing. It is shorter than `WIDEST_COMPARTMENT_SECONDARY`, so the card
#: does not resize.
WITHHELD_MAC_MULTIPLE_TEXT: Final = f"\u2014{MAC_UNIT_SUFFIX}"
#: The strings whose width each readout column reserves, in `READOUT_PANELS`
#: order. The clock column reserves its widest elapsed form and its playback
#: line. Every compartment column reserves the two strings above. Each column
#: reserves its own widest value rather than the clock's. That is what lets
#: seven panels fit across a laptop-wide row while no value can wrap away from
#: its unit (`PL-3355`, `PL-8M05`).
READOUT_RESERVATIONS: Final[tuple[tuple[str, str], ...]] = tuple(
    (WIDEST_READOUT_VALUE, WIDEST_READOUT_SECONDARY)
    if panel.quantity is None
    else (WIDEST_COMPARTMENT_VALUE, WIDEST_COMPARTMENT_SECONDARY)
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
            value printed beside the slider (`PL-25KS`, decision D4).

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
            No spacer is drawn for a setting. These four panels have unequal
            heights by design, because the delivered dial carries a MAC line
            and the flow settings have no such conversion.
        unit: The unit of `value`.
        decimals: The display resolution at which the slider steps.
        minimum: The slider's lowest position, in `unit`: the lowest setting
            at the slider's resolution that the run accepts (`offered_range`).
        maximum: The slider's highest position, in `unit`: the highest such
            setting.
        value: The setting in force, in `unit`.
        value_text: The setting as the readout beside the slider prints it.
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
# profile that states it and the `docs/MODEL.md` section that gives its range.
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
    flows = {
        ControlInput.FRESH_GAS_FLOW: settings.fresh_gas_flow_l_min,
        ControlInput.ALVEOLAR_VENTILATION: settings.alveolar_ventilation_l_min,
        ControlInput.CARDIAC_OUTPUT: settings.cardiac_output_l_min,
    }
    # The range that the run accepts for each control, read this tick. The
    # model's envelopes come from `core/supported_ranges.py`, so the interface
    # offers the domain that the verification gates cover and nothing wider
    # (`PL-0MLQ`). The fresh gas flow's range is that envelope narrowed by the
    # mounted machine, as the circuit states it (`PL-7CRY`). The dial's
    # maximum is the running agent's vaporizer maximum.
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
        name = (
            control.name
            if control.name is not None
            else format_delivered_label(settings.agent_display_name)
        )

        if control.control is ControlInput.DELIVERED:
            value: float = settings.delivered_concentration_percent
            value_text = format_percent(delivered)
            secondary = format_mac_multiple(delivered, settings.agent_mac_percent)
        else:
            value = flows[control.control]
            value_text = format_flow(value)
            secondary = ""

        accepted_minimum, accepted_maximum = accepted_ranges[control.control]
        offered = offered_range(accepted_minimum, accepted_maximum, control.decimals)

        if offered is None:
            raise ValueError(
                f"{name} can offer no setting: no {slider_value(1, control.decimals)} "
                f"{control.unit} step lies inside {accepted_minimum} to {accepted_maximum} "
                f'{control.unit}, the range the run accepts (docs/MODEL.md, "Supported '
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
                f'those steps (docs/MODEL.md, "{section}")'
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
        reason=reason, way_out=REFUSED_RESET_WAY_OUT_TEXT
    )


def notice(
    status: RunStatus, rejected_setting_notice: str | None, *, refused_reset: str | None = None
) -> str | None:
    """Return the banner for a frame that drew: a stopped run, a refused setting, or nothing.

    A stopped run outranks a refused setting, because it describes the state
    of everything else on screen, while a refusal describes only one control.
    A failure in turn outranks the supported run length.

    `RunView.refresh` writes this banner while the frame for which the status
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

    Returns:
        The banner text, or None when there is nothing to say.
    """

    if status.failure_reason is not None:
        return FAILURE_NOTICE_TEMPLATE.format(
            failure_reason=status.failure_reason, exit=refused_reset or RESET_EXIT_TEXT
        )

    if status.supported_limit_reason is not None:
        return SUPPORTED_LIMIT_NOTICE_TEMPLATE.format(run_length=format_supported_run_length())

    if rejected_setting_notice is not None:
        return REFUSED_SETTING_NOTICE_TEMPLATE.format(refused=rejected_setting_notice)

    return None


def halt_notice(status: RunStatus, *, refused_reset: str | None = None) -> str | None:
    """Return the banner for a halt with no frame drawn yet: a stopped run, or nothing.

    `RunView.present_halt` writes this banner from the run's status alone,
    before it attempts any frame. A failure uses
    `UNDRAWN_FAILURE_NOTICE_TEMPLATE` rather than `notice`'s wording, because
    with no frame drawn the values on screen are not the step the run stopped
    at. `refresh` writes `notice`'s banner on the first frame that draws.
    After a step failure, the rollback leaves the run drawable, so its frame
    replaces this banner in the same turn. After a refused displayed value,
    the frame is refused again, so this banner stays. Which banner is shown is
    therefore decided by whether a frame drew, never guessed from the reason
    (`PL-7DJK`). The supported run length keeps its single wording, because
    nothing is wrong with the state it stops on, and the frame that follows
    draws. A refused setting is not a halt and has no banner here.

    Args:
        status: The run's status, as `SimulationController.status()` gives
            it. It is read without building any compartment value, which is
            the whole reason this function takes a status rather than a
            snapshot.
        refused_reset: As `notice` takes it: the way out while Reset itself
            was refused, or None while Reset is the way out.

    Returns:
        The banner text, or None when the run is not halted.
    """

    if status.failure_reason is not None:
        return UNDRAWN_FAILURE_NOTICE_TEMPLATE.format(
            failure_reason=status.failure_reason, exit=refused_reset or RESET_EXIT_TEXT
        )

    if status.supported_limit_reason is not None:
        return SUPPORTED_LIMIT_NOTICE_TEMPLATE.format(run_length=format_supported_run_length())

    return None


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
    `docs/MODEL.md` says it must (`PL-Y5WR`, `PL-V6M0`). Every other
    exception, known or not, is a failure. Only the narrow case is named, so
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
        amounts: Five lines. The first three give delivered, exhausted and
            stored agent at the resolution that `format_agent_volume`
            derives. The last two give the unaccounted amount and the
            absolute error, each as the power of ten that it is less than,
            because an order of magnitude is what those two lines are for
            (`PL-TG60`, `PL-3PJZ`).
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
        overflow: The count of earlier changes that the panel did not list,
            or the empty string when nothing was left out. The count of
            changes that a chart left unmarked appears on that chart instead.
            The changes are counted rather than silently dropped, because a
            list that quietly stops asserts that nothing earlier happened.
    """

    entries: str
    overflow: str


def timeline_panel(adjustments: Sequence[ControlAdjustment]) -> TimelinePanel:
    """The control-change panel for one run's adjustments.

    The panel lists changes and says how many it left out. The count of
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
    notes: list[str] = []

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
    answer as the case's answer while two runs were on screen. A learner
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


def _stated_time_bookmark(bookmark: TimeBookmark) -> str:
    """Return a marked instant's own words: the time, and the name if it was given one.

    Every drawn row puts the time first and the name after it. The time is
    what the row asserts, and the name is what the learner chose to call it.
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
    target means something different on each compartment. `docs/MODEL.md`
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
    both directions. A branch that halted on a learner's mark reported
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
class ForkPoint:
    """One entry in the branch selector.

    The entry says where a branch would open and which method opens it. A
    recorded control event and a time bookmark that the trunk has passed are
    listed together, because both stay on offer until the case itself
    changes. `fork_offer` explains why that puts them in one list. The two
    kinds are taken through different methods, and `mark` says which.

    **A mark's entry carries the mark, not an instant to branch at.** A branch
    at a mark opens at the end of the step that reaches the mark. In general,
    that is not the instant the learner typed (`MarkForkPoint`). A caller
    taking the entry passes `mark` back to `BranchedCase.fork_at_mark`, which
    finds that step itself. So there is no float here for a caller to get
    wrong. The entry is labelled and ordered by `instant_s`, but a mark's
    branch is never requested at that instant.

    Attributes:
        instant_s: Where a branch taken here opens, in seconds of the case.
            It is either a keyframe of the trunk or a passed mark's
            `MarkForkPoint.fork_s`.
        label: What the selector shows for the entry. It is `instant_s` as
            `format_elapsed` writes it. For a mark, that reading is placed
            inside `MARK_FORK_LABEL_TEMPLATE`, followed by
            `BEFORE_CHANGE_FORK_LABEL_SUFFIX` where the trunk changed a
            setting at `instant_s`.
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
            that the run clock and every bookmark row use, so a learner reads
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
            rather than one. When a setting was changed there, it ends with
            `BEFORE_CHANGE_FORK_LABEL_SUFFIX`.
        refusal: Why the most recently requested branch was not taken, for
            the notice banner, or None. It is never set while `locked`. The
            control that produced the refusal is gone, so the message would
            be about something the reader can no longer see.
    """

    points: tuple[ForkPoint, ...]
    locked: bool
    lock_reason: str
    here_offered: bool
    here_label: str
    refusal: str | None


@dataclass(frozen=True, slots=True)
class ComparedRuns:
    """What the two runs of a comparison are called, the trunk's first, from `run_label`."""

    trunk: str
    branch: str


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

    Args:
        runs: What the trunk and the branch are called on screen.

    Returns:
        The sentence, naming both Resets as the screen names them.
    """

    return COMPARING_FORK_LOCK_TEMPLATE.format(
        trunk=runs.trunk, branch=runs.branch, reset=RESET_LABEL
    )


def fork_offer(
    fork_points_s: Sequence[CaseInstant],
    *,
    marks: Sequence[MarkForkPoint],
    comparing: ComparedRuns | None,
    here: HereForkPoint | None,
    refusal: str | None = None,
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
    when a mark is set behind the clock. It leaves only when the learner
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
    second management of the whole case, which is a comparison a learner may
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
        ForkPoint(point.fork_s, _mark_fork_label(point), point.bookmark) for point in marks
    )
    # The comparison cap refuses every way of branching. So it is applied
    # once, here, rather than checked separately for each field.
    offered_here = None if comparing is not None else here

    return ForkOffer(
        points=tuple(sorted((*control_events, *passed_marks), key=lambda point: point.instant_s)),
        locked=comparing is not None,
        lock_reason="" if comparing is None else comparing_fork_lock_text(comparing),
        here_offered=offered_here is not None,
        here_label="" if offered_here is None else _here_fork_label(offered_here),
        refusal=None if comparing is not None else refusal,
    )


def _mark_fork_label(point: MarkForkPoint) -> str:
    """Return the selector's label for a mark the trunk has passed.

    The label gives the instant where the branch opens, and whether the
    branch opens before a setting change made there.

    Args:
        point: The mark and where its branch opens, from
            `BranchedCase.mark_fork_points`.
    """

    suffix = BEFORE_CHANGE_FORK_LABEL_SUFFIX if point.setting_changed_at_fork else ""

    return MARK_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(point.fork_s)) + suffix


def _here_fork_label(here: HereForkPoint) -> str:
    """Return the label of the fork where the trunk stands.

    The label gives the instant, any mark that stopped the trunk there, and
    whether the branch opens before a setting change made there.

    Args:
        here: Where the trunk stands, from `BranchedCase.here_fork_point`.
    """

    template = HALT_FORK_LABEL_TEMPLATE if here.stopped_on_mark else HERE_FORK_LABEL_TEMPLATE
    suffix = BEFORE_CHANGE_FORK_LABEL_SUFFIX if here.setting_changed_here else ""

    return template.format(instant=format_elapsed(here.fork_s)) + suffix


def delivered_line(delivered: SettingReadout) -> str:
    """Return the delivered concentration in both units, for the readout heading line.

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

    `RunView._write_statement` is the only code that writes these widgets.
    `refresh` calls it with the snapshot that a frame drew from. `present_halt`
    calls it with `SimulationController.record()` when no frame can draw. So a
    widget listed here shows the same thing on a drawn run and on a halted run
    in the same state. Before this class existed, the halt wrote a list of
    widgets chosen by hand, and each widget the list missed went on showing
    the last frame's run (`PL-X7D5`, `PL-1YDD`, `PL-DTJQ`).

    The four dials are written next to this statement from the same record,
    rather than carried in it. `setting_readouts` can raise for a control that
    can offer no setting, and everything here has to be on screen before that
    happens (`PL-85LJ`).

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
        banner: The notice banner's text before it is attributed to a run,
            or None for no banner.
    """

    agent_id: str
    agent_name: str
    subtitle: str
    substance_heading: str
    status: StatusWord
    transport: Transport
    timeline: TimelinePanel
    banner: str | None


def run_statement(
    record: RunRecord,
    adjustments: Sequence[ControlAdjustment],
    *,
    is_branch: bool,
    comparing: bool,
    banner: str | None,
) -> RunStatement:
    """Return what a run's screen shows from its record alone, for `RunView._write_statement`.

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
        banner: The text from `notice` when a frame drew, or from
            `halt_notice` when none has. The caller chooses, because only the
            caller knows whether a frame drew.

    Returns:
        The statement.
    """

    return RunStatement(
        agent_id=record.agent_id,
        agent_name=record.agent_display_name,
        subtitle=format_subtitle(record.agent_display_name),
        substance_heading=substance_heading(record),
        status=status_word(record),
        transport=transport(record, is_branch=is_branch, comparing=comparing),
        timeline=timeline_panel(adjustments),
        banner=banner,
    )


def time_axis_caption(frame: ChartFrame) -> str:
    """Return the span of the run that the chart shows, and whether the reader or the run chose it.

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
    """Return a caption naming the divisor that every MAC number on the page uses.

    The caption names the reference run's agent and its 1 MAC. That is what
    makes the MAC readouts traceable without opening a data file (`CLAUDE.md`,
    safety-critical clinical-output standard).

    Args:
        frame: The frame drawn this tick. All of its runs use one agent.

    Returns:
        The reference line.
    """

    return format_mac_reference(frame.runs[0].agent_display_name, frame.mac_percent)


def mac_awake_caption(snapshot: SimulationSnapshot) -> str:
    """Return what the MAC-awake band was drawn from: its published fraction and the divisor.

    Both free parameters are named, so a reader who disagrees with either one
    can see which one it is (`PL-F52R`).

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
    """Return what the wash-in plot is showing at this instant, and why.

    While the trace is being drawn, the number here is the same value as the
    trace's right-hand end. Both come from `read_wash_in` on the snapshot's
    own alveolar and inspired fractions, so the plot and the sentence beside
    it cannot disagree.

    Args:
        snapshot: The run's state this tick.
        undrawn_wash_in_stretches: How many stretches inside the window the
            plot's limited pool of lines could not draw, from
            `RunFrame.undrawn_wash_in_stretches` of the same tick. The count
            is appended, so the pool's limit is shown rather than hidden.

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
    """Return a notice naming which of one run's drawn traces are above the plot, if any.

    The traces are read from the points the frame drew, not from the snapshot.
    The snapshot carries only the newest state, and a trace that rose above
    the axis earlier in the window is still drawn clipped now. Hidden traces
    are skipped, so the notice never points at a trace that is not there. A
    trace counts as off scale only once it exceeds the ceiling by more than
    the readouts resolve. Isoflurane's ceiling is 3 x 1.2, which in binary
    floating point is 3.5999999999999996. A comparison with zero tolerance
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
        The notice, or None when every drawn trace is inside the axis.

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
        if any(
            percent - frame.axis_top_percent > CONCENTRATION_DISPLAY_RESOLUTION_PERCENT
            for percent in run.percents(quantity)
        )
    ]

    if not off_scale:
        return None

    return OFF_SCALE_NOTICE_TEMPLATE.format(
        compartments=", ".join(off_scale),
        top=format_mac_multiple(fraction_from_percent(frame.axis_top_percent), frame.mac_percent),
    )


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


def wash_in_state_lines(
    frame: ChartFrame, snapshots: Sequence[SimulationSnapshot]
) -> tuple[str, ...]:
    """Each drawn run's wash-in state line, for the F_A/F_I plot that drew `frame`.

    The result has one entry for each run, in order. Each entry is the run's
    `wash_in_state`, with the count of stretches that this plot's window left
    undrawn. While more than one run is drawn, `compared_run_line` labels each
    entry with its run.

    Args:
        frame: The frame the plot drew.
        snapshots: The snapshot each of the frame's runs was read from, in
            the same order.

    Raises:
        ValueError: If there is not one snapshot for each of the frame's runs.
    """

    if len(snapshots) != len(frame.runs):
        raise ValueError(
            f"{len(snapshots)} snapshot(s) were given for a frame of {len(frame.runs)} run(s)"
        )

    return tuple(
        compared_run_line(wash_in_state(snapshot, run.undrawn_wash_in_stretches), frame, index)
        for index, (run, snapshot) in enumerate(zip(frame.runs, snapshots, strict=True))
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
    which tells two sessions' runs apart for a Workspace's pin. A reader never
    sees two sessions' runs at once (`PL-7Z84`).

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
    first line inverts the comparison that a branch exists to teach. The
    second reports a clipped trace on a run that has none (`PL-25DD`).

    The name is added here rather than built into either line, following
    `compared_trace_legend_label`. What the line says depends on the run's
    state. Whether the line needs its run's name depends on how many runs the
    chart is drawing. So the run's name is a separate fact, joined at the one
    place that knows both.

    A lone run is given no name, because there is nothing to tell it apart
    from. `SimulationView._rename_runs` applies the same rule to the run
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


def compared_run_notice(notice_text: str | None, run_name: str | None) -> str | None:
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
    `compared_run_line`, which takes the frame. `RunView.present_halt` also
    writes the banner, and it states a halt from the snapshot alone, because
    the frame is what may have failed (`PL-25KS`). Reading the run count from
    the frame there would drop the attribution in exactly the case it exists
    for. The name that the dashboard has already given the run through
    `set_run_name` is the same word that `run_label` put on the run's own
    panel and in both legends.

    Args:
        notice_text: The result of `notice` for this run this tick, or None
            when there is nothing to say.
        run_name: What the dashboard calls this run, from `run_label`, or
            None while only one run is drawn and there is nothing to tell it
            apart from.

    Returns:
        The notice unchanged while one run is drawn or there is no notice, or
        the run's name followed by the notice while two runs are drawn.

    Raises:
        ValueError: If `run_name` is empty, because an empty name names no
            run. An empty name would not fail on its own. It would render a
            banner that opens with a bare colon. A notice that looks
            addressed to a run called nothing is the plausible-looking output
            that `CLAUDE.md` asks to fail instead.
    """

    if run_name is not None and not run_name:
        raise ValueError("a run's name says which run the banner is about, so it cannot be empty")

    if notice_text is None or run_name is None:
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
    a branch exists to teach, rather than merely blurring it (`PL-C3GS`).

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
            drawn. `SimulationView._rename_runs` already applies that rule to
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
    began_at_s: float
    elapsed_s: float | None
    adjustment_count: int


def branch_at_stake(
    name: str, began_at_s: float, snapshot: SimulationSnapshot | None, adjustment_count: int
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

    `docs/MODEL.md` § "Agent-change behavior" requires it. That section exempts
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
