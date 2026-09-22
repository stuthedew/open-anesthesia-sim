"""What the dashboard claims about one run at one instant, with no toolkit loaded.

The counterpart of `chart_frame.py` for everything beside the plots: the
status word, the notice banner, the seven readouts, the four setting
controls, the transport enablement, the agent-accounting panel, the
control-change list, the two bookmark listings, the chart captions and the
new-case question. Each is a
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

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final

from anesthesia_sim.app.bookmarks import (
    BookmarkCrossing,
    BookmarkSet,
    BookmarkStandings,
    MacTarget,
    MarkStanding,
    TimeBookmark,
)
from anesthesia_sim.app.chart_frame import (
    COMPARED_COMPARTMENT_CAP,
    ChartFrame,
    TraceStyle,
    trace_style,
)
from anesthesia_sim.app.chart_time_base import TIME_BASE_LADDER
from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.control_timeline import ControlAdjustment, format_adjustment
from anesthesia_sim.app.controller import SimulationSnapshot
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
    render_mac_multiple,
)
from anesthesia_sim.app.playback import SUPPORTED_PLAYBACK_RATES, PlaybackRate
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.app.wash_in import WashInDomain, read_wash_in
from anesthesia_sim.core.concentration import (
    Fraction,
    Percent,
    fraction_from_percent,
    percent_from_fraction,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError, SimulationDomainLimitError
from anesthesia_sim.core.parameters import AGENT_DATA_FILENAMES, load_agent_parameters
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
# Where the two runs of a comparison are drawn, and so what `run_label` calls
# them. The trunk first and its branch second is an invariant of how
# `SimulationView` builds and adds runs rather than a fact about a case, and
# `comparing_fork_lock_text` is what depends on it: a sentence sending a
# learner to one run's Reset is only findable if it names the run that Reset
# belongs to.
TRUNK_RUN_INDEX: Final = 0
BRANCH_RUN_INDEX: Final = 1

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

# The bookmark panel. Two headings and two empty lines rather than one of
# each, because the two collections are listed apart (`PL-LPLD`) and a shared
# "nothing marked yet" would leave a reader working out which of the two it
# was about.
#
# Oldest first, which is the opposite of the control-change list above and is
# not an inconsistency: that list is a record of what has happened and the
# newest entry is the one a reader is chasing, while this is a set of standing
# questions a reader adds to and scans, so an entry that moves when another is
# added is one they have to find again.
#
# **The headings name the two kinds and say nothing else.** A caption here
# would be explaining the domain to a clinician, which
# `.claude/rules/ui-reader.md` rules out; what each row asserts is carried by
# its own units and words.
TIME_BOOKMARK_HEADING: Final = "Time bookmarks"
MAC_TARGET_HEADING: Final = "MAC targets"
NO_TIME_BOOKMARKS_TEXT: Final = "None marked"
NO_MAC_TARGETS_TEXT: Final = "None set"

# The separator between a mark's value and the name the learner gave it. An
# en dash, which `tools/glyph_check.py` records as rendered.
MARK_LABEL_JOINER: Final = " – "

# What a row says about how far the run has got with the mark it lists
# (`PL-CTD7`). Conditional text rather than standing text, which is the
# distinction `.claude/rules/ui-reader.md` draws: a mark the run can still
# reach says nothing at all, so the words appear on exactly the rows whose
# state a reader would otherwise have to infer from silence.
#
# **The three negative answers are worded apart deliberately.** "Not reached"
# alone would be true of all three and would tell a learner that a bookmark
# before this branch's fork might arrive if they kept running, which it cannot -
# `bookmarks.MarkStanding` carries the argument, and `CLAUDE.md`'s
# safety-critical standard is what rules out the plausible-looking answer.
# `NOT_REACHED_WITHIN_CAP` names the run length rather than a number of hours,
# so the figure lives once, in `core/supported_ranges.py` and
# `docs/MODEL.md` § "Supported run length".
#
# **The failed run's word names the failure for the same reason the cap's
# names the cap** (`PL-N3N5`). Each says what the mark went unreached
# *within* or *before*, so the row carries why nothing more will happen to
# the mark rather than leaving a reader to find it on the run's own panel -
# and it borrows that panel's phrase, so a screen read at one instant says
# "Stopped - simulation error" above and "not reached before the simulation
# error" beside the mark instead of two accounts of one stop. What it does
# not do is predicate the transport state of the mark: "not reached" is the
# claim, and the failure is when it stopped being open to revision, which is
# the distinction `MARK_STILL_RUNNING_TEXT` below was introduced for.
#
# **"passed" and "reached" are two words because they are two claims**
# (`PL-3K9B`). "Passed" is where the run's clock is relative to a marked
# instant, so it is re-read every time the row is drawn and stays true across
# anything that moves the clock. "Reached" is what the run did to a marked
# height, which no clock orders. Wording them alike would put one word on a
# row a rewind can revoke and a row it cannot, which is the plausible-looking
# answer again - and a learner reading two branches side by side is reading
# exactly that difference.
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

# The same answers, attributed, for a row whose displayed runs disagree
# (`PL-LHBY`, `PL-4KZD`). A mark's *set* is shared across the runs on screen -
# `SimulationView._apply_to_every_run` is the only thing that writes one - but
# its *standing* is computed from each run's own clock, its own opening
# instant and its own halts, so two managements of one case answer the same
# mark differently and both answers are the case's news.
#
# **`STILL_RUNNING` is the one entry that gains a word here, and only here.**
# On an unattributed row silence is unambiguous: nothing has happened to a
# mark on the one run whose answer the row states. Beside a named run that has
# something to say, silence would read as the second run having no answer
# rather than as its answer being not yet, so the row would leave a reader to
# infer from an absence exactly what `.claude/rules/ui-reader.md` keeps
# conditional text for. The word costs nothing on the rows that stay
# unattributed, because those rows never reach this table.
#
# **It is predicated of the mark, not of the run, and "still running" was the
# wrong word for it.** `MARK_ATTRIBUTION_TEMPLATE` puts the run's name first,
# which makes the run the grammatical subject: for `passed`, `reached` and the
# cap the predicate still reads as that run's relation to the mark, but "still
# running" reads as its transport state. This interface owns that vocabulary
# already - `STATUS_RUNNING_TEXT`, `STATUS_PAUSED_TEXT` and
# `STATUS_FAILED_TEXT` are a few lines above, and
# `REFUSED_SETTING_NOTICE_TEMPLATE` uses the phrase in exactly that sense - so
# `Run 2 still running` contradicted the word on Run 2's own panel whenever
# that run was paused, which is most of the time a learner reads this row, and
# said something `MarkStanding.STILL_RUNNING` is not licensed to claim: it
# says the run *can still reach* the mark and has not yet, which is a
# statement about the mark rather than about the clock. "Not yet" is that
# statement, and it holds of a paused run and a running one alike.
#
# Derived from `MARK_STANDING_TEXT` rather than written out again, so the four
# words the two tables share cannot come to disagree about what a standing is
# called on one row and on the row beside it.
MARK_STILL_RUNNING_TEXT: Final = "not yet"
MARK_STANDING_COMPARED_TEXT: Final[Mapping[MarkStanding, str]] = MappingProxyType(
    {**MARK_STANDING_TEXT, MarkStanding.STILL_RUNNING: MARK_STILL_RUNNING_TEXT}
)
# One run's answer, named by the run it belongs to. The run's own word comes
# first, because a row that disagrees is scanned down its run names.
MARK_ATTRIBUTION_TEMPLATE: Final = "{run} {said}"

# The editor's own words. Field labels rather than sentences, which is the
# form `.claude/rules/ui-reader.md` asks a specialist reader's screen to carry
# its meaning in: "Compartment" and "Height" say what the control sets, and
# what a height on a given compartment does and does not assert is
# `docs/MODEL.md` § "MAC multiples as a display unit" rather than a paragraph
# in a dialog.
# The branch control, beside the marks and for the same reason: both offer
# instants of the *case* rather than of either run, so both are panels of the
# dashboard rather than of a `RunView` (`docs/ARCHITECTURE.md` § "Where new
# code belongs"). "From" labels the instant the branch opens at; the heading
# names the mechanism and says nothing else, per the rule the mark headings
# are written under.
FORK_HEADING: Final = "Branch"
FORK_POINT_LABEL: Final = "From"
TAKE_FORK_LABEL: Final = "Branch here"
# Conditional text, so it earns a sentence where standing chrome would not
# (`.claude/rules/ui-reader.md`). It says the rule and the way out of it,
# because a refused control that does not say how to un-refuse itself is a
# dead end rather than a mode. The display is capped at two runs and there is
# no run selector yet - `ROADMAP.md` § "Explicitly out of scope for v0.5.0" -
# so a second branch would have to replace the shown one silently, with the
# first still live inside `BranchedCase`.
#
# **A template, because the way out is a button and a button is found by the
# words on it** (`PL-WG73`). It read "Reset the case" while the only Reset in
# `app/` is labelled `RESET_LABEL` and nothing on screen says "case", so the
# way out named a control this interface does not have. A comparison draws
# two of them, one per run, and they do opposite things: the trunk's rebuilds
# the case, the branch's returns that run to its own fork and leaves this
# lock standing - which is the one a learner reaches for, being the run they
# are trying to end. So the sentence names both, and
# `comparing_fork_lock_text` fills it from `run_label` and `RESET_LABEL`,
# which is what stops an instruction and the control it names drifting apart
# again.
#
# It states what the trunk's Reset costs as well as what it ends. Sending a
# learner to a control that discards every run without saying so would be
# this same defect with the consequence hidden rather than the label.
COMPARING_FORK_LOCK_TEMPLATE: Final = (
    "One comparison at a time. {trunk}'s {reset} ends it and starts the case over; "
    "{branch}'s {reset} only returns {branch} to where it branched."
)
FORK_NOTHING_SELECTED_TEXT: Final = "Select an instant to branch at"

# The fork at a bookmark halt, which is a second control rather than a row in
# the selector above (`PL-TYWQ`, project owner 2026-09-21, ratified, over the
# single list that grows a row while the run is halted). The two offers have
# different lifetimes: `fork_points_s` only grows and every instant in it stays
# forkable, while this one is valid only while the trunk stands on the halt, so
# a row that arrived and left would change the selector's membership under a
# reader who had looked away - the stale-state case
# `.claude/rules/expert-review.md` names, and detectable only against a
# remembered list. A control that is either there or not is detectable on
# sight.
#
# **The instant is the halt's, not the mark's, and the wording keeps them
# apart.** A mark lying inside a step halts the run at the step's end, so the
# instant a learner marked and the instant the branch opens at are not in
# general the same number (`SimulationController.resumed_at_halt`). The label
# therefore binds its instant to "Branch here" - what this control will do -
# and says "stopped on your mark" of the halt rather than of the number, so it
# never states a mark's position. Labelling it with the marked instant instead
# would be the wrong label on a correct value, which `CLAUDE.md`'s
# safety-critical standard counts as a failure of the value.
#
# One label for a crossing of either kind. A step can cross a marked instant
# and a marked height at once, and "your mark" is true of both; which marks
# were crossed is the bookmark panel's row to state, and repeating it here
# would put two accounts of one stop on screen.
#
# **These exact words** (project owner, 2026-09-21, ratified, over `PL-TYWQ`'s
# own illustrative "Branch at your mark - 0:45", which asserts where the mark
# *is* and so is wrong whenever a mark lies inside a step). Ratified rather
# than specified, so ordinary evidence reopens it - a learner who misreads it,
# a measurement - but the clause it was chosen over is the one thing a rewrite
# must not reintroduce.
HALT_FORK_LABEL_TEMPLATE: Final = "Branch here: {instant}, stopped on your mark"

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
# The entry unit for an instant, and the resolution it is entered at. Seconds
# rather than the compound form the clock reads, because a spin box states one
# unit and the compound form is three; the dialog restates the entered value in
# that form beside the control, so no reader converts between them. One decimal
# is the simulation step, which is the finest instant a run can stand on.
INSTANT_ENTRY_SUFFIX: Final = " s"
INSTANT_ENTRY_DECIMALS: Final = 1
INSTANT_ENTRY_STEP_S: Final = 1.0
# What the height control is bounded at before an agent has been named. Every
# shipped agent's vaporizer reaches at least this multiple of its own 1 MAC,
# so it is a floor on the real bound rather than a guess at it, and
# `BookmarkDialog.set_reachable_height` replaces it with the running agent's
# own the first time a frame is drawn.
DEFAULT_MAXIMUM_TARGET_MAC: Final = 3.0

REMOVE_NOTHING_SELECTED_TEXT: Final = "Select a mark to remove it."
"""Conditional text, which is where a sentence is appropriate: it fires on a
press that did nothing and costs nothing when it does not
(`.claude/rules/ui-reader.md`). The two empty lines above are standing text
and are labels for that reason."""
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
# The other two reasons the chip stands in the selector's place. A branch
# carries the agent of the case it continues - `SimulationController.set_agent`
# refuses one outright (`PL-TFX5`) - so its selector is not locked but absent,
# and the caption says what is true of it rather than what a Pause would undo.
# While two runs are compared the trunk's selector *would* be obeyed, and that
# is the worse case: the switch succeeds, `assemble_chart_frame` then refuses a
# frame whose runs are on two agents, and `_halt_every_run` fails both over an
# input to one of them (`PL-QRD1`). Refusing it before it reaches the controller
# is `.claude/rules/expert-review.md`'s preference for an interface that
# prevents the error over one that reports it afterwards.
BRANCH_AGENT_LOCK_TEXT: Final = "Locked to the case"
COMPARING_AGENT_LOCK_TEXT: Final = "Locked while comparing"

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
#: The MAC-awake band's legend words: a population value with its spread,
#: and the trace it is read against (`PL-90Y6`).
MAC_AWAKE_BAND_LEGEND_LABEL: Final = "MAC-awake (population, ±1 SD; read against vessel-rich trace)"
#: What assistive technology announces for a compartment's legend box: the
#: act it performs rather than the pattern words beside it, which describe
#: the line and not the control. Carried over from the Flet legend's
#: semantics label so the port loses nothing a screen reader had.
TRACE_TOGGLE_ACCESSIBLE_NAME_TEMPLATE: Final = "Draw the {label} compartment on the chart"
#: A compartment's legend words: its name and its line style, so the style is
#: legible without reference to the plot (`docs/MODEL.md` § "The six
#: compartment traces"). One template rather than an f-string at each legend
#: row, because the compare-mode row has to say the same words as the
#: checkbox above it or the two describe one curve differently.
TRACE_LEGEND_LABEL_TEMPLATE: Final = "{label} ({line_style})"
#: What a run is called in text. `docs/MODEL.md` § "Minimum displayed outputs"
#: requires the run to be named in text rather than carried by colour or by
#: position: colour is spent on the compartment, and position alone fails the
#: reader who has looked away and back.
#:
#: Numbered by drawing order, which is also the order the run panels are laid
#: out in, because the name has to be findable - a legend entry reading "Run 2"
#: is only an attribution if something else on screen also says "Run 2", and
#: that is the panel holding the settings that produced it.
RUN_LABEL_TEMPLATE: Final = "Run {number}"
#: One drawn trace's legend words while more than one run is shown: the
#: compartment's own words, then the run's. Both dimensions named on every
#: entry, which is what `PL-8PSW` asks of a legend once a curve carries two.
COMPARED_TRACE_LEGEND_TEMPLATE: Final = "{trace}, {run}"
#: The caption on the compare-mode legend row. "Drawn" rather than
#: "Compartments", because the row above it already names the compartments and
#: is the control; this row is the four curves actually on the plot.
COMPARED_TRACE_LEGEND_CAPTION: Final = "Drawn traces:"
#: One run's line in a column the runs share, while more than one is drawn:
#: the run's name, then the line. The run leads here where it trails in
#: `COMPARED_TRACE_LEGEND_TEMPLATE`, and the difference is what the reader is
#: scanning for. A legend is read by curve, so the compartment leads there and
#: the run tells two entries for one compartment apart. These columns stack one
#: line per run, each opening with the same words - "Above the top of the
#: plot", "Now: F_A/F_I" - so the run is the only thing distinguishing them,
#: and a differentiator at the end of a wrapped sentence is one the reader has
#: to go looking for.
COMPARED_RUN_LINE_TEMPLATE: Final = "{run} — {line}"
#: One run's banner in the notice column the runs share, while more than one is
#: drawn. A colon where `COMPARED_RUN_LINE_TEMPLATE` uses an em dash, because
#: every notice already opens `label — detail` - "Simulation stopped — ...",
#: "Setting refused — ..." - so a second em dash would sit at a different depth
#: than the first and read as the banner's own separator with the run's name as
#: the label. The colon scopes what follows to the run, which is the sense
#: `OFF_SCALE_NOTICE_TEMPLATE` and `COMPARED_TRACE_LEGEND_CAPTION` already use
#: it in. The run leads for `COMPARED_RUN_LINE_TEMPLATE`'s reason and not
#: `COMPARED_PANEL_HEADING_TEMPLATE`'s: these stack wrapped sentences opening
#: with identical words, not short headings whose both ends are read at once.
COMPARED_RUN_NOTICE_TEMPLATE: Final = "{run}: {notice}"
#: One run's panel heading in a column the runs share: the panel's own words,
#: then the run's. The run trails here where it leads in
#: `COMPARED_RUN_LINE_TEMPLATE`, and the two are not in tension - this is the
#: legend's case rather than the shared-line one. The sidebar stacks whole
#: panels, each found by the kind of record it holds, so the kind leads exactly
#: as the compartment does in `COMPARED_TRACE_LEGEND_TEMPLATE` and the run
#: tells two panels of one kind apart. The differentiator-first argument that
#: puts the run in front of a shared line turns on a wrapped sentence whose end
#: a reader has to go looking for; a heading is one short bold line, where both
#: ends are read at once.
#:
#: An em dash rather than the colon `COMPARTMENT_SUBSTANCE_TEMPLATE` uses:
#: "Agent accounting validation: Run 2" reads as the validation's *result*,
#: which is the word the line directly below it carries (`ACCOUNTING_VALID_TEXT`).
COMPARED_PANEL_HEADING_TEMPLATE: Final = "{heading} — {run}"
#: The fork's legend words. Vertical like a control mark and solid where that
#: is dashed, which is the pair of channels that separates them; the words say
#: both so the mark is identifiable without reference to the plot.
BRANCH_POINT_LEGEND_LABEL: Final = "Branch point (vertical, solid)"
#: Said while the two-compartment cap is holding traces off the chart. It
#: names the bound, what it removed, and where those values still are - the
#: last because `docs/MODEL.md` § "Minimum displayed outputs" makes the
#: readouts what keeps a capped compartment on the display, so a reader told
#: only that a trace is gone has been told half of it.
COMPARED_CAP_NOTICE_TEMPLATE: Final = (
    "Two runs are shown, so the chart draws at most {cap} compartments at once. "
    "Every compartment's value is in the readouts below, for both runs."
)
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
#: What each readout column reserves its width for, in `READOUT_PANELS`
#: order: the clock its widest elapsed form and its playback line, every
#: compartment the two strings above. Each column reserves its own widest
#: value rather than the clock's, which is what lets seven stand across a
#: laptop-wide row while no value can wrap from its unit (`PL-3355`,
#: `PL-8M05`).
READOUT_RESERVATIONS: Final[tuple[tuple[str, str], ...]] = tuple(
    (WIDEST_READOUT_VALUE, WIDEST_READOUT_SECONDARY)
    if panel.quantity is None
    else (WIDEST_COMPARTMENT_VALUE, WIDEST_COMPARTMENT_SECONDARY)
    for panel in READOUT_PANELS
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
            agent chip. True while running, because choosing an agent
            discards the case; true on a branch and while two runs are
            compared, for the reasons `selector_lock_reason` states.
        selector_lock_reason: What the chip says about why the selector is
            gone, or the empty string while the selector is shown. Carried
            here rather than chosen in the widget layer, so the three
            reasons are written in one place and a reader is never told
            "running" about a lock a Pause will not lift.
    """

    start_enabled: bool
    pause_enabled: bool
    reset_enabled: bool
    selector_locked: bool
    selector_lock_reason: str


def transport(
    snapshot: SimulationSnapshot, *, is_branch: bool = False, comparing: bool = False
) -> Transport:
    """The transport enablement for one snapshot, and why its selector is locked.

    The three locks are ranked by how long they last, longest first, because
    the chip has room for one reason and a reader acts on it: a branch's
    selector never returns, a comparison's returns on Reset, and a running
    run's returns on Pause. Naming the shortest of the three that happens to
    hold would send a reader to Pause for a lock Pause cannot lift.

    Args:
        snapshot: The run's state this tick.
        is_branch: Whether this run was opened from another
            (`SimulationController.opened_from`). A branch carries the agent
            of the case it continues, so `set_agent` refuses it outright and
            the selector would be a control presenting itself as working.
        comparing: Whether more than one run is on the chart. The runs share
            one MAC axis and one set of clinical references, so a switch
            accepted here is refused a moment later by
            `chart_frame.assemble_chart_frame` - after the controller has
            already changed agent (`PL-QRD1`).

    Returns:
        Which controls are usable, and what the chip says when the selector
        is not one of them.
    """

    stopped = snapshot.failure_reason is not None or snapshot.supported_limit_reason is not None
    lock_reason = ""

    if is_branch:
        lock_reason = BRANCH_AGENT_LOCK_TEXT
    elif comparing:
        lock_reason = COMPARING_AGENT_LOCK_TEXT
    elif snapshot.is_running:
        lock_reason = RUNNING_AGENT_LOCK_TEXT

    return Transport(
        start_enabled=not snapshot.is_running and not stopped,
        pause_enabled=snapshot.is_running,
        reset_enabled=True,
        selector_locked=bool(lock_reason),
        selector_lock_reason=lock_reason,
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


@dataclass(frozen=True, slots=True)
class MarkListing:
    """One of the two bookmark collections as drawn this tick.

    Attributes:
        heading: What the collection is called.
        rows: One line per mark, in the order they were added, or empty.
        empty_text: What stands where the rows would be when there are none.
            Carried on the listing rather than chosen by the widget, so the
            two collections cannot come to disagree about what "nothing
            marked" looks like.
    """

    heading: str
    rows: tuple[str, ...]
    empty_text: str

    @property
    def empty_line(self) -> str | None:
        """The line that stands where the rows would be, or None while there are rows.

        The choice between the rows and the empty line is made here, where a
        test can read it, so the widget decides nothing: it draws `rows` one
        to a row (`PL-FPY2`) and this line only when it is not None.
        """

        return None if self.rows else self.empty_text


@dataclass(frozen=True, slots=True)
class BookmarkPanel:
    """Both collections, listed apart.

    Two listings and not one, which is the shape `PL-LPLD` was scoped on: a
    single list with a kind column would make a reader sort the rows before
    reading either.

    Attributes:
        times: The marked instants.
        targets: The marked heights.
    """

    times: MarkListing
    targets: MarkListing


@dataclass(frozen=True, slots=True)
class RunMarks:
    """One displayed run's answers about the marks the case carries.

    The panel is drawn from one of these per run rather than from a single
    run's snapshot (`PL-LHBY`, `PL-4KZD`). A standing is computed from the
    run's own clock, its own opening instant and its own halt set, so reading
    one run's standings for every run's rows stated one management's answer
    as the case's while two were on screen - and a learner comparing two
    managements is reading exactly the quantity that differs.

    Attributes:
        label: What this run is called in text, from `run_label`. The
            caller's, for the reason `chart_frame.RunInput.label` gives: the
            same word has to appear on the run's own panel beside the
            settings that produced it, and a name this module invented would
            be this module's alone. It is drawn only on a row whose runs
            disagree, so a lone run's panel never states it.
        standings: This run's standing on each of the case's marks, from
            `SimulationSnapshot.bookmark_standings` - the same snapshot the
            run's readouts and traces were drawn from, so a row and the
            trace it is read against are one instant of one run.
    """

    label: str
    standings: BookmarkStandings


def _with_standings(stated: str, said: Sequence[str]) -> str:
    """One row: the mark's own value, then what the displayed runs say about it.

    Args:
        stated: The mark's own value and name, which every row carries. It is
            stated once however many runs are shown, because the marks are
            shared across them by construction; it is the answers that differ.
        said: What each clause of the row says, in drawing order, from
            `_standing_clauses`. A clause that says nothing is dropped rather
            than drawn as an empty tail.

    Returns:
        The row, with each clause that has something to say joined onto it.
    """

    return stated + "".join(f"{MARK_STANDING_JOINER}{clause}" for clause in said if clause)


def _standing_clauses(answers: Sequence[tuple[str, MarkStanding]]) -> tuple[str, ...]:
    """What one mark's row says about it, attributed where the runs disagree.

    **Agreement is what decides attribution, not the number of runs**
    (`PL-LHBY`, `PL-4KZD`). An unattributed clause is a claim about the case,
    so it may be drawn only where it is true of every run on screen - which is
    always so for a lone run, and so for two runs that answer alike. That
    makes the single-run row the degenerate case of this rule rather than a
    second path through it, which is what keeps the two from drifting apart:
    the panel had no way to draw a branch's own answer at all while it read
    one run's standings for every run's marks, and `MarkStanding`'s
    `BEFORE_THIS_BRANCH` could not reach the screen, the reference run being
    the trunk and no mark standing before a trunk.

    Where they disagree the clause is no longer the case's, so every run is
    named - including a run whose answer is "not yet", which unattributed
    silence would hide behind the run that did have something to say.

    **One run and its answer arrive already paired, rather than as two
    sequences read in step.** Pairing them here would make a shorter standings
    sequence draw the agreement clause from a subset of the runs — one run's
    answer stated as the case's, which is the defect this function exists to
    remove, reappearing as an off-by-one. The caller builds each pair in one
    comprehension over the runs, so there is no length to check and no guard
    that could be dropped: `CLAUDE.md` asks for the interface that prevents
    the error over the one that refuses it afterwards.

    Args:
        answers: One `(run label, that run's standing on this mark)` pair per
            displayed run, in drawing order.

    Returns:
        One clause for the case where the runs agree, and one clause per run
        where they do not. Empty where no run is given, which
        `bookmark_panel` refuses before reaching here.
    """

    standings = tuple(standing for _, standing in answers)

    if len(set(standings)) == 1:
        return (MARK_STANDING_TEXT[standings[0]],)

    return tuple(
        MARK_ATTRIBUTION_TEMPLATE.format(run=label, said=MARK_STANDING_COMPARED_TEXT[standing])
        for label, standing in answers
    )


def format_time_bookmark(bookmark: TimeBookmark, standing: MarkStanding) -> str:
    """One marked instant, as a reader meets it.

    The time first and the name after it, because the time is what the row
    asserts and the name is what the learner chose to call it — and because
    two rows read against each other are read down their first column.
    `format_elapsed` renders it, so a bookmark and the run clock beside it
    state one quantity one way. Where the run has something to say about the
    mark, it comes last, after both.

    **The unattributed form, which is the row every displayed run agrees
    on.** `bookmark_panel` builds a drawn row from `_stated_time_bookmark`
    and `_standing_clauses` instead, because a row whose runs *disagree*
    carries a clause per run and there is then no single standing to pass
    here. So this renders the row a lone run draws, and the row two runs
    draw when they answer alike — and it is where the unattributed wording
    is pinned.

    Args:
        bookmark: The marked instant.
        standing: Its standing, from `SimulationSnapshot.bookmark_standings`.
            Required rather than defaulted, so no row can be rendered that
            quietly asserts a mark is still reachable without anybody having
            asked the run.
    """

    return _with_standings(_stated_time_bookmark(bookmark), (MARK_STANDING_TEXT[standing],))


def _stated_time_bookmark(bookmark: TimeBookmark) -> str:
    """A marked instant's own words: the time, and the name if it was given one.

    The time first and the name after it, on every drawn row: the time is
    what the row asserts and the name is what the learner chose to call it,
    and two rows read against each other are read down their first column.
    `format_elapsed` renders it, so a bookmark and the run clock beside it
    state one quantity one way.
    """

    rendered = format_elapsed(bookmark.instant_s)

    if bookmark.label is None:
        return rendered

    return f"{rendered}{MARK_LABEL_JOINER}{bookmark.label}"


def format_mac_target(target: MacTarget, standing: MarkStanding) -> str:
    """One marked height, as a reader meets it.

    Compartment, then height, then the name. The compartment is on the row
    rather than in a heading above it because a target means a different thing
    on each one: `docs/MODEL.md` § "MAC multiples as a display unit" states
    that a multiple of 1 MAC is the conventional reading only on the alveolar
    compartment and is a partial-pressure ratio everywhere else, so a row
    naming the height alone would be one number standing for six claims.

    The compartment's name comes from `chart_frame.trace_style`, so the row
    and the trace it is read against are named by one table.

    The unattributed form, for the reason `format_time_bookmark` gives: a
    drawn row whose runs disagree carries a clause per run, and
    `bookmark_panel` assembles that from `_stated_mac_target` and
    `_standing_clauses`.

    Args:
        target: The marked height.
        standing: Its standing, required for the reason
            `format_time_bookmark` gives.
    """

    return _with_standings(_stated_mac_target(target), (MARK_STANDING_TEXT[standing],))


def _stated_mac_target(target: MacTarget) -> str:
    """A marked height's own words: the compartment, the height, and any name.

    Compartment, then height, then the name — on every drawn row, this being
    what `bookmark_panel` builds them from. The compartment is on the row
    rather than in a heading above it because a target means a different
    thing on each one: `docs/MODEL.md` § "MAC multiples as a display unit"
    states that a multiple of 1 MAC is the conventional reading only on the
    alveolar compartment and is a partial-pressure ratio everywhere else, so
    a row naming the height alone would be one number standing for six
    claims. The compartment's name comes from `chart_frame.trace_style`, so
    the row and the trace it is read against are named by one table.
    """

    compartment = trace_style(target.quantity).label
    height = render_mac_multiple(target.mac_multiple)
    stated = f"{compartment} {height}"

    if target.label is None:
        return stated

    return f"{stated}{MARK_LABEL_JOINER}{target.label}"


def bookmark_panel(bookmarks: BookmarkSet, runs: Sequence[RunMarks]) -> BookmarkPanel:
    """The two collections the case is marked at, as two listings.

    It states what is marked *and* where each displayed run has got with it
    (`PL-CTD7`). Still nothing here reads a compartment: the standings are
    computed in the advance loop, one per completed simulation step, and
    arrive through `SimulationSnapshot.bookmark_standings` — which is what
    keeps a drawn row from implying a detection this module performed.

    **Every displayed run, not the reference run** (`PL-LHBY`, `PL-4KZD`). The
    marks are the case's and are shared across the runs by construction, so
    one row per mark is right; their standings are each run's own, so a row
    states the answer unattributed only where the runs agree and names them
    where they do not. Reading `snapshots[0]` for every row instead put one
    management's answer on the other's mark in both directions: a branch that
    halted on a learner's mark reported nothing, because the trunk was still
    running for it, and an inherited bookmark the branch could never reach
    read as the trunk had left it.

    Args:
        bookmarks: The case's marks, from `SimulationSnapshot.bookmarks`.
        runs: Every run on screen, in drawing order, each with the standings
            read from the same snapshot its traces were drawn from. Marks and
            standings arrive as separate arguments rather than one derived
            from the other, so a panel cannot be drawn from one run's marks
            and another run's answers.

    Returns:
        Both listings, each with its heading, its rows and its empty line.

    Raises:
        ValueError: If no run is given. A panel drawn for no run would list
            the case's marks under standings nobody had answered, which is
            the plausible-looking row `CLAUDE.md`'s safety-critical standard
            prefers an obvious failure to.
        SimulationConfigurationError: If a run's standings were computed for a
            set that does not hold one of these marks, which
            `BookmarkStandings` refuses rather than defaulting.
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
class ForkOffer:
    """What the branch control offers this tick, and why it may offer nothing.

    Attributes:
        points_s: The case instants a branch may be taken at, earliest
            first, from `BranchedCase.fork_points_s`. They are the trunk's
            keyframes: its opening at induction and every setting change the
            model was actually stepped under. Anywhere else is refused by
            `SimulationController.resumed_at` rather than approximated, so
            the control offers this list and never a free instant.
        labels: One label per instant, in the same order, rendered by
            `format_elapsed` - the form the run clock and every bookmark row
            use, so a learner reads one quantity one way wherever it appears.
        locked: Whether the control is replaced by its reason. True while a
            comparison is already on the chart.
        lock_reason: What stands where the control stood, or the empty
            string while it is offered. A state caption rather than a
            warning: a mode a reader can leave by pressing Reset is not the
            same kind of thing as a refusal, and this interface has one
            alarm colour (`.claude/rules/ui-reader.md`) which is worth
            exactly as much as it is spent on.
        halt_offered: Whether the second control - the fork at the bookmark
            halt the trunk is standing on - is on screen this tick. It
            appears and disappears with the trunk's halt, where `points_s`
            only grows, which is why it is a control of its own rather than
            an entry in that list (`PL-TYWQ`).
        halt_label: What that control says, or the empty string while it is
            not offered. It names the instant the branch will open at and
            that the trunk stopped there on a mark; `HALT_FORK_LABEL_TEMPLATE`
            carries why those are two clauses rather than one.
        refusal: Why the branch last asked for was not taken, for the
            notice banner, or None. Never set while `locked`: the control
            that produced it is gone, so the message is about something the
            reader can no longer see.
    """

    points_s: tuple[float, ...]
    labels: tuple[str, ...]
    locked: bool
    lock_reason: str
    halt_offered: bool
    halt_label: str
    refusal: str | None


def comparing_fork_lock_text() -> str:
    """The caption standing where the branch control stood, naming the way out of the lock.

    Filled from `run_label` and `RESET_LABEL` rather than written out. The way
    out is a button, a button is found by the words on it, and a comparison
    draws two Resets - one per run, each in a transport row led by that run's
    name - so a sentence that names neither leaves the reader to guess which
    (`PL-WG73`, and `COMPARING_FORK_LOCK_TEMPLATE` for what that guess cost).

    The lock stands only while a second run is drawn - `fork_offer`'s
    `comparing` - so the first two positions both name a run on screen
    whenever this text is on screen: the trunk, whose Reset ends the
    comparison, and the branch, whose Reset returns that run to its fork and
    leaves the lock exactly where it was.

    Returns:
        The sentence, naming both Resets as the screen names them.
    """

    return COMPARING_FORK_LOCK_TEMPLATE.format(
        trunk=run_label(TRUNK_RUN_INDEX), branch=run_label(BRANCH_RUN_INDEX), reset=RESET_LABEL
    )


def fork_offer(
    fork_points_s: Sequence[float],
    *,
    comparing: bool,
    halt: BookmarkCrossing | None,
    refusal: str | None = None,
) -> ForkOffer:
    """What the branch control shows for one tick of the trunk.

    Both doors to a fork are decided here, and they are two fields rather than
    one list: `points_s` is every keyframe the trunk holds, and `halt_offered`
    is the crossing it is standing on right now. `docs/ARCHITECTURE.md`
    § "Where a branch may be taken" is why the model keeps them apart - a
    bookmark records no keyframe, so a halt adds nothing to `fork_points_s` -
    and `HALT_FORK_LABEL_TEMPLATE` is why the interface does too.

    Induction is offered rather than filtered out. A fork at zero is a second
    management of the whole case, which is a comparison a learner may
    legitimately want, and filtering it would leave a case that has recorded
    nothing offering no instant at all - a control with an empty list and a
    live button, which is worse than a strange entry.

    Args:
        fork_points_s: The trunk's keyframes, from
            `BranchedCase.fork_points_s`.
        comparing: Whether a second run is already on the chart. The display
            is capped at `MAX_DISPLAYED_RUNS` and no run selector exists yet
            (`ROADMAP.md` § "Explicitly out of scope for v0.5.0"), so a
            second branch taken now would have to replace the shown one while
            the first went on living inside `BranchedCase` - state the screen
            does not carry, which is what the control is refused for. It
            refuses both doors: a branch is a branch whichever one it came
            through, and a transient control the cap would reject on press is
            one this interface prevents rather than reports
            (`.claude/rules/expert-review.md`).
        halt: The bookmark crossing the **trunk** is standing on, from
            `SimulationSnapshot.bookmark_halt`, or None when it is standing
            on none. The crossing rather than its instant deliberately:
            `fork_at_halt` opens the branch at the step the run halted on,
            and a float parameter here would let a caller hand over the
            instant a learner *marked* instead - a different number whenever
            a mark lies inside a step. A crossing carries the halted instant
            by construction, so there is none to get wrong.
        refusal: Why the branch last asked for was not taken, or None. It
            is dropped while the control is locked, because it describes a
            press of a control the reader can no longer see.

    Returns:
        The instants to offer and their labels, whether the halt fork is on
        offer and what it says, or the reason none of it is.
    """

    points = tuple(fork_points_s)
    # The comparison cap refuses both doors, so it is applied once, here,
    # rather than by each field asking about it separately.
    offered_halt = None if comparing else halt

    return ForkOffer(
        points_s=points,
        labels=tuple(format_elapsed(instant_s) for instant_s in points),
        locked=comparing,
        lock_reason=comparing_fork_lock_text() if comparing else "",
        halt_offered=offered_halt is not None,
        halt_label=(
            ""
            if offered_halt is None
            else HALT_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(offered_halt.instant_s))
        ),
        refusal=None if comparing else refusal,
    )


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


def run_label(run_index: int) -> str:
    """What the run at this position on the chart is called, in text.

    The one place a run is named, so the legend entry, the run's own panel
    heading and any later view say the same word. A name is only an
    attribution if the reader can find what it refers to, and what it
    refers to is the panel carrying that run's settings.

    Args:
        run_index: Which run, as a position in the frame's runs.

    Returns:
        The run's name.

    Raises:
        ValueError: If `run_index` is negative, which addresses no run.
    """

    if run_index < 0:
        raise ValueError(f"a run is at a nonnegative position on the chart, not {run_index}")

    return RUN_LABEL_TEMPLATE.format(number=run_index + 1)


def trace_legend_label(style: TraceStyle) -> str:
    """One compartment's legend words: its name and its line style."""

    return TRACE_LEGEND_LABEL_TEMPLATE.format(label=style.label, line_style=style.line_style)


def compared_trace_legend_label(trace: str, run: str) -> str:
    """One drawn curve's legend words while more than one run is shown.

    Args:
        trace: The trace's own words - a compartment's from
            `trace_legend_label`, or the wash-in plot's single trace label.
        run: The run's name, from `run_label`.

    Returns:
        Both dimensions in one entry, in that order.
    """

    return COMPARED_TRACE_LEGEND_TEMPLATE.format(trace=trace, run=run)


def compared_run_line(line: str, frame: ChartFrame, run_index: int) -> str:
    """One run's line in a column the runs share, named while more than one is drawn.

    The wash-in state line and the off-scale notice both sit in the chart
    column rather than on the run's own panel, one line per run, and both
    carry a clinical value: an F_A/F_I the reader compares against the other
    run's, and a statement that a compartment's trace is clipped. Neither
    said whose it was, and stacking order is not an attribution - it is
    declared nowhere on screen, and the run names live in a different
    splitter section. Read as the other run's, the first inverts the
    comparison a branch exists to teach and the second reports a clipped
    trace on a run that has none (`PL-25DD`).

    Composed here rather than built into either line, following
    `compared_trace_legend_label`: what the line says is a property of the
    run's state, and which run it belongs to is a property of how many runs
    the chart is drawing, so the run's name is a separate fact joined at the
    one place that holds both.

    A lone run is given no name, having nothing to be told apart from - the
    rule `SimulationView._rename_runs` applies to the run panels and to both
    legends, so a single-run display is unchanged. The frame's run is read
    before that count is consulted, so an index addressing no run raises on
    a one-run frame too rather than returning a line that looks right.

    Args:
        line: This run's line, already formatted.
        frame: The frame drawn this tick, which is what says how many runs
            are on the chart and what each is called.
        run_index: Which of the frame's runs the line belongs to.

    Returns:
        The line unchanged while one run is drawn; the run's name and then
        the line while more than one is.

    Raises:
        IndexError: If `run_index` is not one of the frame's runs.
    """

    run = frame.runs[run_index]

    if len(frame.runs) <= 1:
        return line

    return COMPARED_RUN_LINE_TEMPLATE.format(run=run.label, line=line)


def compared_run_notice(notice_text: str | None, run_name: str | None) -> str | None:
    """One run's banner in the notice column the runs share, named while two are drawn.

    The banner sits in a column both runs write into, and all three of the
    notices `notice` can return assert something about *a* run while naming
    none: a halt says "Simulation stopped", and a refusal says "The
    simulation is unchanged and still running its previous setting" - which
    is false of the run it is not about. Read as the dashboard's rather than
    one run's, a halt on the branch says the case has stopped when the trunk
    is still going, and a refusal says a setting was not applied to a run
    that took it (`PL-TSZM`).

    Stacking order separates these less than it separates the chart column's
    lines, because a banner with nothing to say is hidden rather than blank:
    with one run halted the column holds a single block whose position moves
    by the column's spacing alone - 12 px measured on 2026-09-21, against
    nothing on screen to measure it from - while the words are identical.

    A colon rather than `COMPARED_RUN_LINE_TEMPLATE`'s em dash, which is why
    this is a second function and not that one with the run read from a
    different place. Every notice already opens `label — detail`
    ("Simulation stopped — ...", "Setting refused — ..."), so an em dash
    prefix would put two in one sentence at different depths, and the first
    would read as the banner's own label separator with "Run 2" as the
    label. The colon is the same one `OFF_SCALE_NOTICE_TEMPLATE` and the
    compare-mode legend caption already use to scope what follows.

    Takes the run's name rather than the frame and an index, where
    `compared_run_line` takes the frame: the banner is also written by
    `RunView.present_halt`, which states a halt from the snapshot alone
    because the frame is what may have failed (`PL-25KS`). Reading the count
    off the frame there would drop the attribution in exactly the case this
    is for, and the name the dashboard has already given the run through
    `set_run_name` is the same word `run_label` put on the run's own panel
    and in both legends.

    Args:
        notice_text: `notice`'s result for this run this tick, or None when
            there is nothing to say.
        run_name: What the dashboard calls this run, from `run_label`, or
            None while one run is drawn and there is nothing to tell it
            apart from.

    Returns:
        The notice unchanged while one run is drawn or there is no notice;
        the run's name and then the notice while two are.

    Raises:
        ValueError: If `run_name` is empty, which names no run. An empty
            name would render a banner opening with a bare colon rather
            than fail, and a notice that looks addressed to a run called
            nothing is the plausible-looking output `CLAUDE.md` asks to be
            failed instead.
    """

    if run_name is not None and not run_name:
        raise ValueError("a run's name says which run the banner is about, so it cannot be empty")

    if notice_text is None or run_name is None:
        return notice_text

    return COMPARED_RUN_NOTICE_TEMPLATE.format(run=run_name, notice=notice_text)


def compared_panel_heading(heading: str, run: str | None) -> str:
    """One run's panel heading in a column the runs share, named while more than one is drawn.

    The sidebar holds two panels per run - the agent-accounting validation
    and the control-change record - in a column the runs share, so a branch
    stacks four: accounting, control changes, accounting, control changes,
    with nothing on any of them saying whose. Both carry a claim about one
    run: the accounting panel a mass-balance status and litres of equivalent
    pure agent gas, the control-change panel a list of settings under the
    words "What was changed during this run". Read as the other run's, the
    second says the trunk received an intervention it never got, which is the
    comparison a branch exists to teach inverted rather than merely blurred
    (`PL-C3GS`).

    The name goes in the heading rather than on each line beneath it, which
    is what separates this from `compared_run_line`: those columns hold one
    bare line per run and have no heading to carry it, while a panel has a
    heading whose whole job is to say what the panel holds. Prefixing five
    lines with the same run name would say it five times and read as part of
    each value.

    Kept general over the heading, and given no knowledge of which panel it
    is naming, because every main view will owe an area a heading of its own
    (`.claude/rules/ui-areas.md`) - and because a heading that travels with
    its own panel survives a reader rearranging the column, where one group
    heading above both panels would not.

    Args:
        heading: The panel's own heading words.
        run: The run's name, from `run_label`, or `None` while one run is
            drawn - which is the rule `SimulationView._rename_runs` already
            applies to the run panels and both legends, so a single-run
            display gains no standing text.

    Returns:
        The heading unchanged while one run is drawn; the heading and then
        the run's name while more than one is.
    """

    if run is None:
        return heading

    return COMPARED_PANEL_HEADING_TEMPLATE.format(heading=heading, run=run)


def compartment_cap_notice(frame: ChartFrame) -> str | None:
    """What the chart says while the two-compartment cap is holding traces off it.

    Conditional text, fired by the state it explains and costing nothing
    otherwise (`.claude/rules/ui-reader.md`). It earns a sentence because it
    accounts for two things a reader would otherwise have to guess at: why
    four traces left the chart when the second run arrived, and why a fifth
    box will not stay checked. Neither is a label, a unit or an axis title.

    It fires on the cap being *in force* rather than on a count of traces
    removed, because the legend holds the selection inside the cap from the
    moment the second run appears - so by the time a frame is assembled the
    count is zero and the reader has still lost four curves.

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


def readout_row_width(columns: int, panel_widths_px: Sequence[float], spacing_px: float) -> float:
    """The narrowest row that seats the panels `columns` across.

    Panels fill the grid row by row, so column `j` holds every panel whose
    index is `j` modulo `columns` and is as wide as the widest of them; the
    row is those column widths plus `columns - 1` gaps of `spacing_px`.

    Args:
        columns: How many panels stand side by side; at least one.
        panel_widths_px: Each panel's own reservation, in row order.
        spacing_px: The gap between neighbouring columns, in logical pixels.

    Raises:
        ValueError: If `columns` is below one, since no row seats its
            panels in no columns.
    """

    if columns < 1:
        raise ValueError(f"a readout row seats its panels in at least one column, not {columns}")

    occupied = min(columns, len(panel_widths_px))
    column_widths = (max(panel_widths_px[first::columns]) for first in range(occupied))
    return sum(column_widths) + (columns - 1) * spacing_px


def readout_columns(width_px: float, panel_widths_px: Sequence[float], spacing_px: float) -> int:
    """How many readout panels stand side by side at this width.

    The largest rung of `READOUT_ROW_LADDER` whose panels fit: the row
    `readout_row_width` gives for that count takes no more than `width_px`.
    One column is the floor, however narrow the row, because a row must
    hold its panels somewhere. Each panel's width is the widget's measured
    reservation - the widest value its column can show, in the rendering
    font (`PL-3355`) - so the row steps down exactly where a panel would
    otherwise be clipped, at whatever width that is on the reader's display
    (`PL-8M05`).

    Args:
        width_px: The readout row's width, in logical pixels.
        panel_widths_px: Each panel's reservation, in row order, in logical
            pixels.
        spacing_px: The gap between neighbouring columns, in logical pixels.

    Returns:
        The column count: 7, 4, 2 or 1.
    """

    for columns in READOUT_ROW_LADDER:
        if readout_row_width(columns, panel_widths_px, spacing_px) <= width_px:
            return columns

    return READOUT_ROW_LADDER[-1]
