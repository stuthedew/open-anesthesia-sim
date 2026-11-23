# Interface requirements

This document states what the simulator's interface must show and do: its
controls, what a reset and a change of agent do, the questions asked before a
run is discarded, what a comparison of two runs of one case shows, the boundary
between the interface and the model, and the outputs that must be displayed.
It also gives the ranges of the settings, and the length of a run, over which
the model is claimed to represent a patient (§ "Supported input ranges" and
§ "Supported run length"). A separate document, `docs/MODEL.md`, specifies the
model that computes the displayed values.

## Runtime controls

This section names the four controls and says when a change to one acts. Its
subsections then say how a run halts on a mark, what a run records, how a
branch is taken from a run, and the range over which each control is
supported.

Four settings are the model's only inputs. Each can be changed during a run
without resetting the model's state:

- fresh gas flow;
- delivered agent concentration;
- alveolar ventilation; and
- cardiac output.

From the next simulation step on, a change affects transfers. Changing delivered
concentration does not alter the existing circuit concentration. Changing
ventilation does not alter existing circuit or alveolar stores. Changing cardiac
output does not alter existing blood or tissue stores, but it recalculates
tissue flows:

$$
Q_i=f_iQ
$$

**The model's state does not depend on the playback rate, the chart's time
base or which compartment traces are drawn.** These are settings of the interface
itself, and each can be changed during a run. Identical inputs still produce
identical results, so a case played at sixty times real time is the same run
watched faster.

**The playback rate does decide when an input acts.** A control changed *during*
a run first acts on the next step that the run takes. The faster rates take
several steps at a time, so the same slider moves made at two playback rates can
produce different runs. `docs/VERIFICATION.md` § "Supported simulation step" quantifies this.

**For developers.** § "Interface boundary" sets the constraints on the
interface's own settings. `docs/VERIFICATION.md` § "The reproducibility guarantee" rules out treating
the playback rate as a model input.

The tests check that a run reaches the same definition at every playback rate
(`test_a_run_reaches_the_same_definition_at_every_playback_rate` in
`tests/integration/test_sevo_controller.py`). They also check that a change of
ventilation or of cardiac output leaves the stored agent where it was
(`test_changing_ventilation_preserves_alveolar_agent` in
`tests/unit/test_alveolar.py` and `test_changing_output_preserves_stored_agent`
in `tests/unit/test_patient.py`).

### Halting on a marked crossing

A run may be **marked** in two ways. A *time bookmark* marks an instant of the
case. A *MAC target* marks a height on one named compartment, such as the
circuit. The height is stored as a multiple of 1 MAC of the agent in use.
Marking a height adds nothing to what that multiple asserts about each
compartment (§ "MAC multiples as a display unit"). A mark is a question asked
of the case, not an input to it. A run that halts at its marks computes exactly
the values that an unmarked run computes, element for element. The only thing a mark changes is when
the run stops.

**The marks are added and removed in the Bookmarks View**, below the lists of
marks and each run's standing on them. No window opens to edit a mark
(§ "What this list requires once the layout is the reader's"). After a mark is
removed, no mark in that list is selected, so a second press of its Remove
button removes nothing.

**The run halts on the simulation step that crossed a mark, at every playback
rate.** Every step is tested for a crossing. At the faster rates, a halt is
finer than anything a learner can do while the run plays. A setting changed
during play first acts on the next step that the run takes. At 1x and 5x that
step begins at the next whole second. At 20x, 60x and 300x the run takes 2, 6
and 30 steps at a time, so a change can act only at instants 2, 6 and 30
simulated seconds apart (`docs/VERIFICATION.md` § "Supported simulation step"). A halt
is not on that grid. It lands on the crossing step
itself, at every playback rate. If the crossing were tested once per screen
update instead, the same bookmark would stop at a different concentration
depending on how fast the case was played, and nothing on screen would say so.
Two runs both branched off the case "at 0.8 ×MAC" would then start from two
different states.

**A halt leaves the run paused until the learner resumes it.** No step is taken
while the run is paused, and a setting changed then applies at once. So the
learner gets the safe order, pause, change, resume, without having to know it.
The one exception is a mark on the supported run length. The run stops there as
§ "Supported run length" says, so it can be neither resumed nor given a new
setting, and its status reads "Stopped — supported run length reached".
Without the pause, the run would play on, and a change made after the halt would
wait for the next point of the grid above, so turning the vaporizer off at a
0.8 ×MAC mark could take effect up to 30 simulated seconds after the value the
learner was looking at. The displayed value would be right, and the action
taken from it would be wrong. The run's status reads "Paused — stopped on your
mark", so the halt is not mistaken for the learner's own Pause while two runs
are compared and the branch control is withdrawn.

**The value shown at a halt can lie one or more display counts past the mark,
and is still correct.** It is the reading on the first step at or past the
marked height, so it lies within one simulation step of that height: above the
mark on a rising crossing and below it on a falling one. One step's change can
still show on screen. That change grows with the gap between a compartment and
the gas reaching it, and with the flow that carries that gas in. With 8%
sevoflurane and a fresh gas flow of 10 L/min, a 0.10 ×MAC target on the circuit
halts showing 0.12 ×MAC. The change can be larger on other compartments. Run
the same settings for 120 s with alveolar ventilation at 0 L/min, so that the
alveolar reading stays at zero while the circuit fills. Restoring ventilation
to 12 L/min then raises the alveolar reading from zero to 0.32 ×MAC in the next
one-second step. So a 0.10 ×MAC alveolar target halts showing 0.32 ×MAC,
twenty-two display counts past its mark. A value one or more display counts past
the mark is therefore correct, and is not a fault in detecting the crossing.
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->

**A crossing is a transition between two steps, never a comparison at one
step.** The test asks whether the reading was on one side of the height at the
previous step and is on the other side at this step. A test of "the reading is
at or above the height" would fail in two ways. A run that settled exactly on a
marked height would pass that test on every later step and could never be
advanced past it. Nor could a test of one reading say *which* step crossed, and
saying that is the whole purpose of the halt. The height counts as reached on
arrival, not on departure, in both directions. This rule also lets a halted run
resume. The run is left standing on the crossing step, so the previous reading
for the next step is the crossing step's own, and the crossing just halted on
is not crossed again.

**A MAC target halts on every crossing, in either direction.** A target names a
compartment and a height, and no direction. A case taken up through 0.8 ×MAC
and back down through it has reached what the learner marked both times, so it
stops both times. A target that halted once and then had to be set again would
make two identical-looking targets in the list behave differently, according to
which one had already halted. Nothing on screen would tell them apart, and this
interface is built to avoid such hidden modes. Resuming a paused run takes one
control, which the learner is already looking at.

**A target's height is a narrow band, so that a run settled on a target does
not cross it again and again.** The band extends one part in a hundred thousand
of the height on either side, about five hundred times finer than a two-decimal
readout near 1 MAC of sevoflurane. A reading inside the band is at the height,
and the transition rule above applies to the band.

**A crossing is decided from the same readings on every branch and on the
trunk, the run that branches are taken from.** If the trunk and a branch
decided a crossing from two calculations of the same step, a trunk that halted
at a target's exact height could leave a branch opened on the halting step
showing that target as still running.

**For developers.** A crossing is decided from the two states that the run
stored for the ends of the step: the second before and the second the step
reached (`SimulationController._step_ending_here`, § "Each second has one
stored state"). Each end has one reading, so the run, a branch and a later
review of the halt all decide from the same two numbers.

The height band (`HEIGHT_BAND` in `core/rounding.py`) is there because a steady
compartment's reading moves in its last digit from step to step. Its docstring
gives the measurement that showed this. A marked instant needs no reading,
because whether a step crosses it depends only on the step's two seconds.

The tests are in `tests/unit/test_bookmarks.py` unless another file is named. A
halt lands on the same step at 1x and at 300x
(`test_a_halt_lands_on_the_same_step_at_1x_and_at_300x`) and leaves the run
paused on the crossing step
(`test_a_halt_leaves_the_run_paused_on_the_crossing_step`). An unmarked run
takes the same trajectory as one that halted
(`test_an_unmarked_run_takes_the_same_trajectory_as_one_that_halted`). The
status does not read as the learner's own pause
(`test_a_run_a_mark_stopped_is_not_worded_as_the_learner_s_own_pause` in
`tests/unit/test_dashboard_frame.py`). A halt can show a few display counts past
a circuit target and many past an alveolar one
(`test_a_circuit_target_halts_within_one_step_of_its_mark_and_can_show_counts_past`
and
`test_an_alveolar_target_can_halt_many_counts_past_its_mark_when_ventilation_resumes`
in `tests/integration/controller/test_controller_bookmarks.py`). A target is
crossed in either direction
(`test_a_target_halts_on_every_crossing_in_either_direction`), once by a run
that settles on it
(`test_a_run_that_settles_exactly_on_a_target_halts_once_and_then_advances`),
and never by leaving its height
(`test_a_target_is_not_crossed_by_leaving_its_height_in_either_direction`). A
reading on either edge of the band is inside it
(`test_a_reading_exactly_on_the_lower_edge_of_the_band_is_inside_it` and
`test_a_reading_exactly_on_the_upper_edge_of_the_band_is_inside_it`). A branch
opened on a halting step agrees with the trunk
(`test_a_branch_opened_on_a_halting_step_agrees_with_the_trunk`).

#### What a mark's row reports

**The state of a mark is one of six outcomes.** Each of the last four has its
own wording, because a reader would otherwise mistake it for one of the others.

- **Still running**: nothing has happened yet, and the run can still reach the
  mark. A row in this state shows no words. Where two compared runs differ on a
  mark, the row reads "not yet" beside the name of the run in this state.
- **Passed**: a time bookmark at or behind the run's own clock. This outcome
  applies however the clock came to be there. A step may have taken the run
  past the mark, the run may be a branch that opened standing on the mark, or
  the learner may have marked an instant that the case had already run past.
  A passed mark on the trunk is one at which a branch may be taken
  (§ "What this requires of a branch"), unless the mark is on the supported run
  length, where a branch would have no step left to take.
- **Reached**: a MAC target crossed by a step that the run has stood on at least
  once. Either the run halted on that step, or it stands on that step or opened
  on it. This outcome belongs to the run rather than to the mark, so a reset or
  a change of agent clears it, because each begins a new run. A branch's reset
  returns it to the step it opened on, so a target that this step crossed still
  shows as reached.

  Every time the outcomes are read, two steps are checked again against the
  current marks. The first is the last step of a stopped run, whether it
  paused, halted or reached the supported run length, on a trunk or on a
  branch. A run stopped by an error is not checked, because an error is not a
  pause. The second is the step on which a branch opened. A branch starts out
  standing on that step, so the step counts as the branch's own however far the
  branch has run since. A target added after the step that crossed it therefore
  shows as reached on a trunk standing on that step, and on every branch opened
  there, whether the target or the branch came first. The run keeps that
  outcome after it moves on. A run that went past that step before the target
  was added never stood on it with the target marked. That run shows the target
  as still running, as it shows any height it did not stop on.
- **Not reached within the supported run length**: the run has stopped at the
  limit that § "Supported run length" declares, and this mark is still
  outstanding. A height above a compartment's asymptote is never reached, so
  this outcome is a result, not an interruption. A row that kept showing "still
  running" would invite a learner to wait for something that cannot arrive.
- **Before this branch opened**: a time bookmark earlier than the step on
  which this branch opened. A bookmark inside that step reads as passed,
  because the branch opened standing on the step that crossed it. A branch
  inherits its trunk's marks, so an earlier bookmark comes across with the
  rest, and no step of the branch can reach it.
  It is inherited rather than dropped so that a trunk's list and a branch's list
  do not disagree about what the case is marked at (`docs/ARCHITECTURE.md`
  § "What a branch is"). This outcome can be decided without running anything.
  Reporting it as "Not reached within the supported run length" would tell a
  learner that a longer run might reach the mark, which is false. A MAC target
  has no equivalent outcome. A height can be reached from either side, so a
  branch may cross a height that its trunk never crossed.
- **Not reached before the simulation error**: the run stopped on an error that
  the model could not step past, and this mark is still outstanding. Resuming
  is not offered, because the next step would fail with the same error as the
  last one. So only a reset could reach the mark, and a reset is a different
  run. This outcome is worded differently from "Not reached within the supported
  run length", because that is the outcome a reader would mistake it for. The
  two stop a run for opposite reasons. At the supported run length, the model
  has answered the question and says that a longer run would not change the
  result. When a run stops on an error, the model could not answer at all.
  Reporting an error as a stop at the supported run length would turn what
  this run did into a claim about what the model supports. A run that has both
  reached the supported run length and met an error is reported as not
  reached within the supported run length. No step is taken after an error, and
  a run stopped at the supported run length refuses every setting. So such a
  run ran out of supported time first, and the error came afterwards from
  something other than a step or a setting, such as a frame that the dashboard
  could not draw. The run's status word and banner report the error, because
  it is the run's last event. So such a run shows the error in its status, and
  the supported run length on the row of each mark that it did not reach
  (`test_a_run_at_the_supported_run_length_that_then_fails_gives_each_reason_in_its_place` in `tests/integration/controller/test_controller_supported_length.py`).

**Time bookmarks and MAC targets are reported in different words.** A run's
clock only moves forward, and it never goes below the instant the run began. So
a time bookmark is either ahead of the clock, or at or behind it, and no history
is needed to decide which. A compartment may arrive at a height, leave it and
arrive again, so the only thing that can be said of a target is what the run
did. "Passed" and "before this branch opened" therefore apply only to time
bookmarks, and "Reached" applies only to targets. The other three outcomes
apply to both.

**A bookmark is reported as "passed", never as "reached".** Suppose a
bookmark's outcome were decided only from where the run halted. Then every
instant that the run is at or behind, but never *stopped on*, would show "still
running", which says the run can still reach the mark. Seven cases were found
(2026-09-20) in which no step could make that true. "Reached" would also go
wrong whenever the clock moves backwards. In the reference simulator, Gas Man,
a bookmark is a pause point that fires on the original pass and on every replay
alike (Philip JH, *Workbook for Gas Man®*, Med Man Simulations, chapter 2,
"Using Bookmarks"). So a rewind, or cutting a run back to a mark and running
on, leaves a mark that will stop the learner again, and any earlier claim that
it was reached is no longer true. "Passed" is worked out again from the clock
every time the row is drawn, so it survives a rewind. "Reached" would have to
be withdrawn, and failing to withdraw it would leave a displayed value quietly
wrong.

### The control-input record

A run keeps three records. The control-input timeline lists each change to a
control that the model ran under, and is what the learner sees. The stored
states hold the state of every second the run has reached. The settings record
holds the settings in force at each second. The subsections below say what
each record holds and what it is for.

#### The control-input timeline

**The timeline records the settings that a run was given.** Each entry is one
change that the model ran under. It gives the simulated time at which the
change took effect, the control, the values before and after, the unit of both
values, and the user adjustment that the change belongs to, such as one drag of
a slider. The timeline is kept with the run and cleared with it, except that
Reset on a branch keeps the entries that the branch opened with
(§ "Reset behavior"). The timeline is shown as
marks on the charts and as a list beside them. Settings of the delivered
concentration appear in the same format as every other concentration on the
page.

**A curve can be checked only against the settings that produced it.** The
exercises that this simulator exists to support all take the form "change one
thing and look at what happened". Examples are overpressuring and then dialling
back, dropping the flow, and halving the cardiac output. A learner who cannot
see where they dialled back cannot read their own experiment. Given the
recorded settings at the recorded times, a fresh run must reproduce the run
that the timeline describes.

**Each recorded value is the one that took effect.** The model refuses a
setting outside its allowed range rather than replacing it with the nearest
allowed value, so the value that took effect never differs silently from the
value asked for. A refused setting is not recorded.

**Only what the model saw is recorded.** A setting equal to the one already in
place is not a change. Nor is a setting that is replaced before the next
simulation step, because the model uses only the value in place when a step
runs. A control moved twice between two steps is therefore one change, from the
first value to the last. A control moved and moved back within one step is no
change at all. Recording the values in between would describe a run that did
not happen.

**One drag of a control is one adjustment, and it applies once.** While the
slider's handle is held, the run keeps its setting and the chart draws a preview
(§ "A preview of an unapplied setting"). Releasing the handle applies the value
once, so a drag records one setting change. A key press, one notch of the scroll
wheel or a click on the slider away from its handle is a single input, and is an
adjustment of its own.

A displayed adjustment states the interval it spans and how many settings the
model ran under during it. The count is shown because an adjustment made over
eight settings is a different run from one made in a single step, even when
the two start and end at the same values.

**A timeline entry records an input, and says nothing about the patient.** The
marks on the charts are labelled as inputs, and the list says so, because a
vertical line on a chart of patient concentrations would otherwise invite the
reader to see an event in the curves.

**Bounds are displayed, not silent.** The charts and the list show when they
leave adjustments out. A chart shows
at most a fixed number of marks, and the list of setting changes at most a fixed
number of lines, so a run may record more adjustments than either can show. A
chart or a list that ended without a count would tell the reader that nothing
else happened. Each chart shows the count of adjustments it leaves unmarked,
because each chart has its own time window (§ "The chart's time base").

**The timeline itself has no limit.** The limits above apply only to what is
shown. Capping the timeline would lose the settings needed to reproduce the run.
Dropping the oldest entries would remove the start of the case, which is the
part a learner returns to. The timeline can be unlimited because it grows with
the number of settings changed, not with the length of the run.

**For developers.** Each control is recorded under a fixed name from the
clinical vocabulary: `fresh_gas_flow`, `delivered`, `alveolar_ventilation` and
`cardiac_output`. A name taken from the accessor that applies the setting would
change whenever the code was renamed, and those accessors have been renamed
three times (`PL-3TLK`, `PL-9SH6`, `PL-NJPB`). The circuit volume was recorded
as a fifth control, `circuit_volume`, until it became a fixed model parameter
(§ "What is not bounded this way"). Removing that name broke no recorded
timeline, because a timeline is held in memory and is never saved.

Every value is stored in the unit the model is set with, which for the
delivered concentration is the percent of one atmosphere (`PL-NJPB`). The
formatter for concentrations (`format_percent`) takes a fraction, so the stored
percent is converted to a fraction on its way in and back to a percent for
display.

The timeline reads each value from the compartment that holds it, after the
model's setter for that control returns. A setter returns only when the model
accepts the value, so no separate check is needed to keep a refused setting out.

The interface declares an adjustment at the start of each input on a slider:
a press on it, a key press and a wheel notch. Each change carries the number of
its adjustment. A held key sends its press again and again, and Qt marks each
repeat as such. A repeat declares nothing, so a held key is one adjustment, and
it cannot fill the chart's marks and push the earlier ones off. A trackpad
swipe declares an adjustment only where it begins, for the same reason. A change that
arrives with no declared adjustment, such as a call from code, joins the
adjustment open on the same control, or opens one. Code must never group
changes by the time between them. A playback multiplier changes how much
simulated time one input spans, so any time threshold would group correctly at
one multiplier and wrongly at another.

The limit on a chart's marks is `MAX_CHART_CONTROL_MARKS` in
`app/chart_frame.py`, and the limit on the list's lines is
`MAX_LISTED_ADJUSTMENTS` in `app/dashboard_frame.py`. No record gives the
reason for either value. Both first appear, at 24 and 12, in the change that
first recorded the control-input timeline, and its commit message, its item
and its documents say what each limit does but not why it is that number
(`PL-DR1Z`, `PL-N8G4`). The comment beside each limit says what changing it
would do.

Grouping the entries for display is recomputed only when the timeline changes
(`AdjustmentGrouping` in `app/control_timeline.py`). `PL-1PSX` holds the
measurements of how fast the timeline grew and what grouping it cost.

The tests are in
`tests/integration/controller/test_controller_control_timeline.py` unless
another file is named. A change is stamped with the instant it took effect
(`test_a_recorded_change_is_stamped_with_the_instant_it_took_effect`), and the
dial is recorded as the percent dialled
(`test_the_control_timeline_records_the_vaporizer_percent_as_dialled`). A value
equal to the one in place, or a refused one, records nothing
(`test_a_setting_equal_to_the_one_in_place_records_nothing` and
`test_a_refused_setting_records_nothing`), and changes within one step collapse
to what the model integrated
(`test_changes_within_one_step_collapse_to_what_the_model_integrated`).
Each input the interface declares on one control is an adjustment of its own
(`test_declared_steps_of_one_control_at_three_instants_are_three_adjustments`),
changes with no input declared between them are one adjustment
(`test_unannounced_steps_of_one_control_at_three_instants_are_one_adjustment`),
and a drag reads as one act (`test_a_drag_reads_as_one_act_spanning_the_settings_the_model_saw`
in `tests/unit/test_control_timeline.py`). The recorded timeline reproduces the
run step for step (`test_the_recorded_timeline_reproduces_the_run_step_for_step`
in `tests/integration/test_control_timeline_replay.py`). The screen says that a
control mark is an input and not a measurement
(`test_the_screen_says_a_control_mark_is_an_input_not_a_measurement` in
`tests/integration/simulation_view/test_simulation_view_whole_interface.py`). A
chart leaves its oldest marks unmarked when it has more than it can show
(`test_marks_beyond_the_pool_are_the_oldest_left_unmarked` in
`tests/integration/test_qt_chart.py`).

#### A run stores the state of every second it reaches

**A run takes one step for each second of simulated time, and stores the state
that the step wrote.** A state is the six fractions (inspired, alveolar, mixed
venous and the three tissue groups), the agent delivered and the agent
exhausted since induction, and the constant one that the equations read their
inputs against. The method in `docs/VERIFICATION.md` § "Selected method (as
implemented)" computes each step. The run's record of stored states holds one
state for every second from the run's opening to the second it has reached.

**A run also records its settings, and computes no state from them.** The
settings are the four controls that § "Runtime controls" names, together with
the patient and agent
parameters that the equations use. They are kept as *stretches*: a stretch
holds one set of settings and the second at which it took effect. Flows are
stored as they were set, in liters per minute (`docs/VERIFICATION.md` § "Time"
explains why). The settings record says which settings were in force at a
second, which is what a branch records as where it came from. The control-input timeline (§ "The
control-input timeline") is a third record, kept to show and group the
changes.

**A run of the supported length fits in memory.** A run of 24 h, the longest
that § "Supported run length" allows, holds 86 401 states in about 6.2 MB. The
compensation terms of its two running totals take 1.4 MB more (measured
2026-11-21).
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**For developers.** The stored states are `StoredStates` in
`core/stored_states.py`, and the settings record is `RunDefinition` in
`core/run_definition.py`. The memory figures are measured in the docstring of
`core/stored_states.py`.

Each second returns the state stored for it bit for bit
(`test_each_second_returns_the_state_stored_for_it_bit_for_bit` in
`tests/unit/test_stored_states.py`), and a recorded setting gives back what was
set (`test_a_recorded_setting_round_trips_to_what_was_set` in
`tests/unit/test_run_definition.py`).

#### Each second has one stored state

**Every value that is shown, compared, exported or branched from is read from
the state stored for its second.** The readouts show the state stored for the
second the run has reached. The chart draws the stored states of the seconds it
draws (§ "What the chart draws"). A mark is tested against the states stored
for the two ends of a step (§ "Halting on a marked crossing"). A branch opens
from the state stored for its fork. Nothing computes the state of a reached
second again, so two readers of one second always get the same numbers.

**No value between two seconds is shown.** The record holds no state between
two seconds, and nothing interpolates one. A chart point, a readout and a mark
each fall on a whole second.

**A preview is the one computed state, and it is only drawn.** A preview shows
seconds the run has not reached yet (§ "A preview of an unapplied setting"). It
starts from the state stored for the second the run has reached. For its first
hour it takes one-second steps as the run does, under the previewed settings.
After the first hour it predicts only the seconds the chart draws (§ "What the
chart draws"). A predicted
state can differ in its last digits from the state that the run later stores
for the same second. A run's step reads each fraction back from the amount of
agent in its compartment, and a prediction carries the fractions directly.
Over 24 h of one-second steps, the two routes differed by at most 9.7e-11
of the fraction (measured 2026-11-21). A sevoflurane fraction of 0.02 then
differs by 2e-12, which is fifty million times smaller than the 0.01% that the
percent readout resolves. A predicted state is never stored, compared or
branched from.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**For developers.** The readouts and the chart show the state stored for each
second
(`test_the_readouts_and_the_chart_show_the_state_stored_for_each_second`), a run
halts on the second whose stored state first reaches a marked height
(`test_a_run_halts_on_the_second_whose_stored_state_first_reaches_a_marked_height`),
and a branch steps on from its parent's state at the fork
(`test_a_branch_stores_its_parents_state_at_the_fork_and_steps_on_from_it`).
These three are in
`tests/integration/controller/test_controller_stored_states.py`. A run cannot
open between two seconds
(`test_an_opening_that_is_not_a_whole_second_cannot_be_built` in
`tests/unit/test_run_definition.py`). Each predicted second matches the second
the run stepped (`test_each_predicted_second_matches_the_second_the_run_stepped`
and `test_a_prediction_at_chosen_seconds_matches_the_seconds_the_run_stepped` in
`tests/unit/test_prediction.py`).

### What this requires of a branch

The first run of a case is the **trunk**. A **branch** continues it in another
way from an instant that the trunk passed through, and that instant is the
**fork**. This document also calls the trunk the branch's parent. A branch is
never taken from another branch.

The roadmap asks that a branched run reproduce its parent exactly, not merely within a tolerance (`ROADMAP.md` item
12). A branch holds a copy of its parent's stored states up to the fork. It
steps on from the state stored for the fork, together with the compensation
terms of the running totals stored beside it. So while no setting differs,
every state the branch stores equals its parent's in every digit, the
delivered and exhausted totals included. A branch can be taken at any whole
second its parent has reached: at a control change, at a mark, or wherever a
paused run stands. Taking a branch records nothing on the parent, so marking a
run or branching from it never changes the parent's later states.

**So no divergence is left over to bound, and there is nothing to show a
learner.** The roadmap's definition of done for v0.5.0 asks this document for
"the bound on any divergence that could not be eliminated" (`ROADMAP.md`). A
branch and its parent hold the same stored state at every second they share,
until a setting differs. The one computed value is the preview, and it is only
drawn. A bound of zero drawn on screen would tell a learner there is something
to watch where there is nothing. § "What a branch comparison asserts, and what
it does not" says what a comparison of the two drawn runs may claim, and the
zero bound is one of those claims.

**A branch's simulated time is the case's time, measured from induction.** It
continues the parent's time rather than restarting at the fork. This one time
is what the clock displays and what stamps every recorded setting change. The
chart's axis, the supported run length, the seconds of the stored states and
the stretches of the settings record are measured in it too. Nothing anywhere
converts between two times, so there is no conversion to get wrong. Continuing
the case's time is also a matter of correctness, because uptake and
distribution depend on the time since induction. A branch that counted from
zero would place the patient at the wrong point on the uptake curve, on the
clock, the control marks and the axis at once. That is the correct value shown
under the wrong patient context, which the project's safety-critical standard
(`CLAUDE.md`) counts as a failure in its own right.

#### The settings a branch runs under

**A branch taken where a run is paused or stopped runs under the settings the
dials show there, and records the settings the run had on its way there as
where it came from.** The two can differ, because the learner can turn a dial
while the run is paused. Take a sevoflurane run at 2% that is paused at
10 min, after which the learner turns the vaporizer to 3%. The run reached
10 min under a stretch of settings at 2%, and that stretch cannot change. The
3% starts a new stretch at 10 min that has not run yet. Any change made during
the pause goes into that new stretch, so turning the dial again before the
next step replaces the 3%. A change during the pause never adds a second
stretch at the same second. Below, the *reaching stretch* is the stretch that
ran up to the second, the 2% one here. The *stretch in force* is the stretch
that runs from the second on, the 3% one here. Where nothing changed at the
second, the two are the same stretch. The halt record lists the marks a run
stopped on. The three ways of branching (at a control change, where a paused
run stands, and at a mark), a branch's reset and the halt record all follow
one rule:

- **A branch's provenance, the record of where it came from, is the reaching
  stretch.** Except at the case's opening, which the paragraph after this list
  covers, nothing the parent later does at the fork can replace the stretch
  that the branch records as its provenance.
- **All three ways of branching run under the stretch in force at the fork,
  which is what the dial says.** So "Branch here" opens with the dials as they
  stand when it is taken. A branch at a second that the trunk has already
  passed runs under the settings the trunk had as it left that second,
  including a change made at that second and no change made later. On a run
  that a mark has halted, a branch taken before the learner changes a setting
  there runs under the old setting. A branch taken after that change runs under
  the new one, as do the branches taken from that second's mark and control
  change entries in the "From" selector. A branch opens at what the dial says
  and does not go back to the previous setting.
- **The branch's timeline opens with the parent's changes at the fork.** The
  branch's settings record opens with its parent's reaching stretch, and
  records as a change at the fork each setting it runs under that differs from
  that stretch. Its control timeline opens with a copy of each change the
  parent recorded at the fork. After the case's opening, those copies are the
  settings that differ between the reaching stretch and the stretch in force,
  so the settings record and the control timeline agree. At the case's
  opening, the copies are the changes the parent made before Start, each shown
  from the value the parent's timeline starts at. Either way, the branch's
  timeline shows the settings it opened under, whatever the trunk later does at
  the fork. No later change merges into a copied entry or removes it, and a
  change the learner makes at the fork is recorded after the copies.
- **A reset branch keeps its settings and the entries it opened with.** Reset
  keeps the settings, restores the stored states up to the fork and reopens the
  branch at the fork on the same provenance. An entry the branch opened with
  records where the branch began, not something done to it since. A setting
  dialled since then is recorded as a change at the fork, in the settings
  record and in the branch's control timeline, so the trace starts where the
  readouts say the branch is. § "Reset behavior" describes the timeline of a
  reset branch, and § "Discarding a run, and the questions that guard it" says
  which entries count when the trunk's Reset asks before discarding it.
- **The halt record names the marks as they are.** A run's halt record lists
  the marks crossed by the step it stopped on: the step that halted a trunk, or
  the step that reached a branch's fork. The record is worked out again against
  the current marks whenever it is read, as the mark outcomes are. So a mark
  removed and added back under another label is named by its new label.

At the case's opening no step has run yet, so the opening stretch is both the
reaching stretch and the stretch in force. A change the trunk makes at the
opening still replaces the opening stretch, even after a branch was taken
there. The branch's provenance then names settings the trunk no longer opens
under. That provenance is still true, because no setting produced the opening
state, and the branch did run under those settings from there. Its own
timeline still states them, as its copy of the trunk's changes made before
Start.

#### Returning to a mark, and branching where a run is paused

**Returning to a mark the run has already passed is a branch taken at the
mark's second.** Consider a learner paused at three hours who marks the
one-hour point and goes back to it. The run stored a state for that second, so
a branch can open there although the run is not standing on it. Such a branch
has six properties:

- **It reproduces the case at the mark in every value.** It holds the trunk's
  stored states up to the mark, and steps on from the state stored there. On a
  run marked at 60 s after its clock reached 180 s, the branch agrees with its
  trunk at all 61 whole seconds from the mark to a minute past it.
- **It is the branch the halt would have given.** A mark set before the run
  passed it halts the run, and the run is forked at the halt. The same mark set
  after the clock went past it is forked here. The two branches' whole
  provenance is equal: stretch, fork state, step count and the step that ends
  at the fork. Taken at the same moment, both run under the same settings,
  including a change the trunk made while it stood on the halt. Every run
  checks which marks were crossed by the step it opened on or stands on,
  against the marks as they are whenever its mark outcomes are read. So a mark
  that this step crossed is treated the same on the trunk and on the branch,
  whether it was added before the branch or after. Every way of branching
  checks that step in the same way.
- **It leaves the trunk unchanged.** Nothing is recorded on the trunk.
- **It opens at the marked second.** A mark is a whole number of seconds, and
  a step ends on every whole second. So the fork is the end of the step that
  reaches the mark, which is the second a halt would have stopped on. The
  branch treats its mark as passed, not as "before this branch opened",
  because the branch opens standing on the step that crossed the mark.
- **It does not replay what the trunk did afterwards.** The branch continues
  under the settings the trunk had as it left the mark's second, until the
  learner changes something. Its own control record holds only a change the
  trunk made at that second, if there was one. The trunk's later changes stay
  the trunk's. The reference simulator's rewind works differently. It returns
  to time zero, keeps the recorded settings and plays them back as it runs
  (Philip JH, *Workbook for Gas Man®*, Med Man Simulations, appendix E,
  "Replaying Simulations", printed pages 186-87). So it takes the trunk back and
  truncates it at the mark. Returning to a mark here forks instead, so the run
  that happened stays on the axis beside the alternative.
- **It opens with the readouts the trunk showed at that second**, because
  both read the one state stored for it.

A mark still ahead of the clock is refused rather than reached. The case holds
no state there yet, and a fork there would be a prediction drawn as if it were
a run. The learner reaches such a mark by running on, and the halt there is
then the fork.

**A branch can be taken wherever a paused run stands.** The clock always
stands on a whole second, and the run stored a state for it. So a branch can
be taken wherever the trunk is paused, on a halt or anywhere else. It opens
from the state stored there and records nothing on the trunk. The branch opens
standing on the marks crossed by the step that ends there. Those are checked
again against the marks as they are now, as for a return to a mark. The halt
record is worked out from the current marks in the same way, whenever it is
read. Four kinds of run are refused. A running run is refused, because where it
stands moves with every step. A failed run is refused, because a failure is
not a pause. A run at the supported run length is refused, because it has no
step left for a branch to take. A run that stands at its opening is refused,
because it has recorded nothing to branch from. A branch at the opening is
taken from the "From" selector's opening entry instead.

#### How a branch is drawn

**A branch's chart starts at the fork.** The branch holds its parent's states
before the fork, but it did not live through them. Every fork therefore
carries the fork second explicitly, and the chart clips the branch's drawn
range there. Drawing the earlier seconds would show the trunk's course under
the branch's name. That would put the right numbers in the wrong patient
context, a presentation failure that the safety-critical standard names. The
fork second also decides that a mark is out of the branch's reach.

**One time axis puts a trunk and its branch on the same columns.** Drawn
columns sit on multiples of the column spacing in the case's own time
(§ "What the chart draws"). So a trunk and a branch are drawn at the same
seconds. Take a 120 s sevoflurane run and a branch of it, drawn on a 13-column
axis spanning 120 s, with the fork deliberately off the grid at a control
change at 55 s. All 8 of the branch's columns are seconds that the trunk also
draws. With the branch anchored to its own zero, it would draw 55, 65, 75 …
and share 2 of 8, so the two traces could not be read against each other at
matched points.

**A branch taken at a mark draws at most one column that its trunk does not,
the fork itself.** The 55 s fork above lands on the trunk's own columns,
because a control change is drawn on every run that has one. A mark's second
is not a control change, so the trunk draws it only if it falls on the grid.
Where the columns are one second apart it always does, because a mark is a
whole number of seconds. On a 120 s axis at 13 columns, which are 10 s apart,
the trunk does not draw a mark at 45 s. The branch always draws its fork,
because it is the left end of the branch's drawn range. Everywhere else, the
two traces can still be read against each other. The value at that one column
is the case's own state there, which both runs hold. So the extra column marks
the second at which the two stop being the same run, not a disagreement about
that second.

**At the columns they share, a branch and its parent draw the same values in
every digit** while no setting differs, because each draws the states it
stored.

#### The code and tests behind branching

**For developers.** The three ways of branching are
`SimulationController.resumed_at()` at a stored second,
`resumed_here()` where a paused run stands, and `resumed_at_mark()` at a mark.
Each records the reaching stretch as `ResumePoint.segment` (from
`RunDefinition.reaching_segment_at`), and the fork second and the state stored
there as `ResumePoint.fork`. The stretch in force comes from
`RunDefinition.segment_at`. The branch's stored states are its parent's,
copied up to the fork by `StoredStates.through`, and its live system is placed
at the fork state with the stored compensation terms
(`AgentUptakeSystem.resume_at`). The copies of the parent's changes at the
fork are `RunRecord.opened_with`. The rule that decides which step crosses a
mark is `TimeBookmark.steps_to_reach`. A mark's second is a `CaseInstant`,
which is a whole number of seconds, so a mark at N seconds is reached by
step N.

The controller reads the fork second as `SimulationController.began_at_s`:
zero on a trunk, the fork second on a branch. Drawing (`drawn_window()`) clips
the window's lower bound there, with
`first_s = max(ceil(start_s), self.began_at_s)` in `app/controller.py`. The
bookmark code (`app/bookmarks.py`) is also given the fork second, to decide
that a mark is unreachable. The fork second is kept apart from the settings
record, so that no code infers it from where that record opens
(`run_segments[0].opened_at_s`), which is the opening of the reaching stretch.

A setting dialled before a reset is recorded as a change at the fork, and a
dial moved and moved back before a step ran cancels out
(`RunDefinition.record_change`). So the sequences *dial, dial back, reset* and
*dial, reset, dial back* leave the same branch: the same settings record, live
state and displayed values.

The tests are in `tests/integration/controller/test_controller_stored_states.py`,
`tests/integration/controller/test_controller_bookmarks.py` and
`tests/integration/controller/test_controller_marks.py`. A branch with no
setting moved repeats its trunk's later states in every number
(`test_a_branch_with_no_setting_moved_repeats_its_trunks_later_states_in_every_number`),
and its delivered and exhausted totals for nine minutes
(`test_a_branch_repeats_its_trunks_delivered_and_exhausted_totals_for_nine_minutes`).
A branch taken at a mark agrees with its trunk at every drawn column they share
(`test_a_bookmark_branch_and_its_parent_agree_at_every_column_they_share`), and
draws one column its trunk does not, the fork
(`test_a_bookmark_branch_draws_one_column_its_parent_does_not_and_it_is_the_fork`).

### Supported input ranges

The model supports each control over its range below, both ends included:

| Control | Range |
| --- | --- |
| Fresh gas flow | 0 to 10 L/min |
| Delivered concentration | 0 to the maximum of the agent's vaporizer |
| Alveolar ventilation | 0 to 12 L/min |
| Cardiac output | 0 to 10 L/min |

<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->

**A setting outside its range is refused, not replaced by the nearest limit**, for the same reason
as the vaporizer maximum. The limit would then be simulated, displayed and charted as a value that the user did not ask for. The refusal
comes before anything changes, so the run in progress stays trustworthy, and the interface reports
the refusal in that run's notice banner. The ranges belong to the model, so the model
refuses such a setting however it is run, not only from the interface.

**Fresh gas flow has a second limit: the flow that the attached anesthesia machine can
deliver.** This limit is the machine's, not the model's, and the table does not show it. The
fresh gas flow control offers only the part of the model's range that lies within that limit
(§ "The model's envelope and a machine's deliverable range are two claims", below).

**A run is refused if it opens with a flow between two steps of its slider.** The ventilation,
cardiac output and fresh gas flow sliders move in steps of 0.1 L/min. A run opens at the
ventilation and cardiac output that its patient profile states. Without the refusal, the slider
would sit on a neighbouring step beside a rounded readout, and both would show a flow that the
run does not have. The patient supplied with the simulator, the reference adult, opens at 4.0
and 5.0 L/min, both on a step, so the refusal changes nothing that the simulator displays.
One test checks the refusal and the steps it names
(`test_an_opening_ventilation_or_cardiac_output_off_the_slider_grid_is_refused`), and another
checks the reference adult's two opening flows (`test_loads_reference_adult_parameters`).
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->
<!-- provenance: data/patients/reference_adult.json default_cardiac_output_l_min = 5 -->

**The maxima for fresh gas flow, ventilation and cardiac output come from no source.** Each was
chosen as the edge of the settings that the interface offers and that two tests cover
(§ "Why a setting outside the ranges is refused").

**Zero is a supported setting on every control, deliberately.** There are three reasons, and
the third decides it:

- The equations stay well posed. A zero flow removes a transfer term rather than dividing by zero.
  At $`Q=0`$ the tissue and venous compartments stop changing, and the alveolar equation loses
  its uptake term.
- Zero is the endpoint of a continuous axis. A slider whose lowest value sat just above zero
  would place an arbitrary boundary inside the range where the model is valid. A reader would
  have no way to tell that boundary from a limit of the model.
- The low end of each flow axis is where the teaching is, and zero is its limit. Reducing
  cardiac output *accelerates* alveolar wash-in, because less agent is carried away from the
  lungs per unit time. This is one of the central results in uptake and distribution, and this
  model reproduces it. With sevoflurane at 1 MAC and the reference adult's other defaults,
  $`F_A/F_I`$ at five minutes is 0.60 at 10 L/min, 0.68 at 5 L/min, 0.75 at 2.5 L/min, 0.85 at
  1 L/min, and 0.96 at zero
  (`test_alveolar_wash_in_at_five_minutes_quickens_as_cardiac_output_falls`). Refusing zero
  would cut the demonstration off one step before its clearest case. The same argument applies
  to alveolar ventilation at zero, which is apnoea.

<!-- not-restated: 10 L/min, 5 L/min -->

**A run at zero cardiac output shows where the agent goes when perfusion stops, and nothing
else.** With no uptake, alveolar gas approaches the inspired gas, and the tissues keep the agent
they already hold. The run does not model circulatory arrest, cardiopulmonary bypass or ECMO.
`docs/MODEL.md` § "Known limitations" lists cardiopulmonary bypass and ECMO among what the model
does not represent. Nothing about the patient's condition follows from such
a run.

**No compartment stores a blood flow, so none can disagree with the cardiac output.** A tissue
group's blood flow is its perfusion fraction times the patient's cardiac output,
$`Q_i = f_iQ`$, and the venous pool's flow is the cardiac output itself.

**A tissue's perfusion fraction is fixed once its group is built.** The patient's three
fractions are checked to sum to 1 when the patient is built and when one of its tissue groups is
replaced. A later change to one fraction of a built group would run neither check, and would
leave tissue flows that no longer sum to the cardiac output. A change to a
fraction is therefore refused.

**For developers.** The checks behind these requirements are in `core/`, and each module's
docstrings explain them. Each flow is a checked type, a subclass of `float` declared with its
range in `core/supported_ranges.py` (`FreshGasFlow`, `AlveolarVentilation`, `CardiacOutput`).
Only its constructor checks the range, and a flow outside it raises
`SimulationConfigurationError`, so a script, a notebook and a test meet the same refusal as the
interface. The module's docstring says where each flow is stored and checked again by type.
`core/checked_number.py` says what every checked type may be built from, and
`core/blood_flow.py` holds the perfusion fraction and the blood flow. A record restored from a
pickle or a copy runs its constructor's checks (`core/checked_record.py`). Each compartment
checks a field as it is written, in its `__setattr__`, and its `restore_state` says why a
rollback bypasses that check. A new cardiac output written onto a built patient is refused, and
the refusal names `set_cardiac_output`, so that cardiac output has one way in. The dial is checked against the vaporizer maximum by
`require_within_vaporizer_maximum` in `core/validation.py`, from both the circuit and the
settings record (`UptakeEquationSettings` in `core/governing_equations.py`). The docstrings of
`SimulationController.reset` and `SimulationController._record_control_change` say how the
controller refuses or undoes a setting that the settings record refuses.

The control timeline's fields are declared as plain `float` and are not checked, so a setting
read back from it is rebuilt as its type. Nothing in `src/` loads a pickle yet. Every record in
`core/`, the parameter payloads that the data files load into among them, saves its values by
field name and checks them again when a pickle or a copy rebuilds it. If a halt comes before the screen
is redrawn, every withheld value is hidden before the dials are written, because writing a dial
can raise an exception.

The dashboard refuses a run that opens between two slider steps when it sets up its controls.
One test checks this for an opening ventilation or cardiac output
(`test_an_opening_ventilation_or_cardiac_output_off_the_slider_grid_is_refused` in
`tests/unit/test_dashboard_frame.py`). Three tests in the same file check the three cases of the
fresh gas flow control that § "The model's envelope and a machine's deliverable range are two
claims" describes:
`test_the_fresh_gas_flow_control_narrows_to_a_declared_machine_range`,
`test_a_declared_range_off_the_display_grid_offers_only_settings_inside_it` and
`test_an_opening_fresh_gas_flow_off_the_slider_grid_is_refused`.

The zero-ventilation, zero-cardiac-output and zero-tissue-flow tests in `docs/VERIFICATION.md` § "Required tests"
specify how the equations behave at zero flow.

**The supported ranges are the verification domain: the settings over which the model is checked
against an independent solution.** The test in `docs/VERIFICATION.md` § "Independent-solution test" runs its
trajectories across everything these ranges allow. Two of its trajectories hold a flow at zero.
One holds alveolar ventilation at zero, and the other holds cardiac output at zero. Narrowing a
range would take a trajectory that the test runs out of reach, and widening one would admit
trajectories that were never checked.
Either way, that test must be re-run. Widening a limit is a legitimate change, and a
safety-critical one. First extend the verification domain. Then re-run the test over the wider
range, and revise this section with the results.

**To change a flow range, edit its constant in `core/supported_ranges.py`.** The flow types,
their checks, and the ventilation and cardiac output sliders all read the constant from there,
and the fresh gas flow slider follows through the range that the circuit accepts. A test then
fails on purpose (`test_envelope_limits_match_the_supported_input_ranges` in
`tests/reference/test_coupled_dynamics.py`). Re-run that file's envelope and trajectory sweeps at
the new limits. Update its limit constants, and the most that the exact step may differ from the
independent solution (`EXACT_STEP_ORACLE_TOLERANCE`). Then re-derive every figure computed at the
flow maxima: the fastest time constant in `docs/MODEL.md` § "Time constants" and `docs/VERIFICATION.md` § "Supported simulation step",
the corner sweeps in `docs/VERIFICATION.md` § "The numerical envelope" and
`tests/unit/test_numerical_envelope.py`, and every figure in this document that a
`provenance:` marker ties to one of the three flow maxima.

Three tests stop a range from changing unnoticed. The first is the test above, which restates
all six flow limits and fails if the model moves one. The second does the same for the displayed
resolution and the step at which every figure is quoted
(`test_displayed_resolution_and_shipped_step_match_the_interface`). The third fails if the
interface stops short of the declared ranges or goes past them
(`test_the_sliders_span_the_supported_input_ranges`). It reads the shipped machine profile,
which declares no deliverable range. A profile that declares one narrows the fresh gas flow
slider to the overlap on purpose (§ "The model's envelope and a machine's deliverable range are
two claims").

**The simulation step is fixed, and is separate from the supported input ranges.** Neither a
user nor a caller sets the step. Every call that advances a run (`advance()`) takes one step of
1 s (`SIMULATION_STEP_S` in `core/simulation_step.py`), and `docs/VERIFICATION.md` § "Supported
simulation step" gives the reasons for that length. The step is a
declared limit, in seconds, on how long a change to a control may go unseen by the model. The
input ranges are a claim about where the compartment structure represents a patient. Neither is
calculated from the other. Widening a range means re-running the reference tests at the new
extreme setting, without revisiting the step. A compartment advanced alone is calculated
exactly at any step, so it still takes a step of any length from 1 ms to the supported run
length (`require_compartment_step` in `core/supported_ranges.py`).
<!-- provenance: core/simulation_step.py SIMULATION_STEP_S = 1 -->
<!-- provenance: core/supported_ranges.py MINIMUM_COMPARTMENT_STEP_S = 0.001 -->

#### Why a setting outside the ranges is refused

**The simulator refuses a setting outside the ranges, because neither its code nor its model has
been checked there.** The ranges are the model's **verification domain**. Across them, its results
have been compared with an independent calculation (`docs/VERIFICATION.md` § "Independent-solution test") and with
measured human data (`docs/VERIFICATION.md` § "Published wash-in and elimination validation test"). Every model result in
this document comes from settings within the ranges.

Outside the ranges, the simulator must refuse rather than show a plausible-looking number. Solved
exactly for a cardiac output of 1000 L/min, the model's equations would give a precise answer to a
question that physiology does not ask, and nothing on the display would invite doubt. Such a
cardiac output is not a patient, and the equations were never proposed to describe one.

**For developers.** The smallest value above each maximum is refused
(`test_rejects_the_smallest_value_above_the_maximum` in
`tests/unit/test_supported_ranges.py`).

#### The model's envelope and a machine's deliverable range are two claims

A run accepts a fresh gas flow only when the flow lies inside two separate ranges. The model's
envelope is the range of fresh gas flows over which the model is claimed to represent a patient.
The model is built on lumped compartments, the reference adult's fixed volumes and constant
partition coefficients. A machine's deliverable range is what its flowmeters, minimum flow and
fresh gas delivery can physically set. A machine can therefore narrow the flows a run accepts, but
never widen them beyond the envelope.

**The machine that ships with the simulator declares no deliverable range, so the model's
envelope is the only limit on the flow.** With this machine, nothing displayed depends on a
machine's range. No declared range means **no claim, not a machine known to be unlimited**. The
shipped machine declares none because, for all eight machines surveyed, no operator's manual or
manufacturer specification giving a deliverable range could be obtained (`docs/machine-survey.md`
§ "(b8) Flow bounds, minimum oxygen flow, and the hypoxic guard"). The survey names
ISO 80601-2-13:2022 as the governing standard. That standard could not be obtained either, so the
survey does not say what it requires.

**The fresh gas flow slider offers only flows that both the model and the machine accept.** It
moves in steps of 0.1 L/min, the flow's displayed resolution. Where an end of the offered range
falls between two steps, the slider offers the step just inside it. For a machine with a minimum
flow of 0.25 L/min, the slider's lowest setting is 0.3 L/min, never the 0.2 L/min that the machine
would refuse (`test_a_declared_range_off_the_display_grid_offers_only_settings_inside_it`). An
offered range that contains no step is an error, because otherwise the slider could offer only a
flow that the run refuses.

**A machine whose starting flow is not one of the slider's steps is refused when the dashboard
sets up its controls.** A user reads the slider's position like a displayed value. If a run
started between two steps, the slider would sit on a neighbouring step beside a rounded readout,
and both would show a flow that the run does not have.

**Each refusal of a fresh gas flow says which range the flow is outside: the model's envelope or
the machine's deliverable range.** The model's refusal names its envelope. The machine's refusal
names the machine and says, in the same sentence, that the model did not refuse the flow.

**A machine whose range does not overlap the model's envelope at all is refused when the
simulated breathing circuit is built.** If such a machine were accepted, every setting would be
refused, each time correctly, but no refusal would say that the pairing itself cannot be simulated.

**A machine's minimum oxygen flow is not stored.** It would affect nothing the model calculates,
because the model carries one volatile agent in one gas phase and no oxygen.

**For developers.** The two ranges are declared and enforced here:

| Claim | Declared in | Refused by |
| --- | --- | --- |
| The model's envelope | `MINIMUM_FRESH_GAS_FLOW_L_MIN` and `MAXIMUM_FRESH_GAS_FLOW_L_MIN` in `core/supported_ranges.py` | `FreshGasFlow`, which runs `require_supported_fresh_gas_flow` when it is built |
| A machine's deliverable range | `deliverable_fresh_gas_flow_range` in that machine's `data/machines/*.json` profile | `BreathingCircuit`, which runs `_require_deliverable_flow` in `core/circuit.py` whenever its flow or its machine range is written |

The two ranges are kept apart because one merged pair of limits fails in two ways. A profile whose
flowmeter reaches 15 L/min would extend the range that every reference test was run over,
without any change to `core/supported_ranges.py`. A run in the extended range would give an exact
number, computed outside everything that was checked and shown just like one inside it. Take a
machine with no true off position at its common gas outlet and a minimum flow of 0.5 L/min. The
merged pair would either fail to represent it or move the model's lower limit for every other
machine. A test checks both refusals with one machine that has both features, a range from 0.5
to 15 L/min (`test_machine_deliverable_flow_range_is_separate_from_model_envelope` in
`tests/unit/test_supported_ranges.py`).

A machine range that does not overlap the envelope is refused when it is reassigned on a built circuit, as well as when the circuit is built
(`test_a_direct_write_is_held_to_the_constructors_checks` and
`test_a_machine_that_overlaps_the_envelope_nowhere_is_refused_when_built` in
`tests/unit/test_circuit.py`).

The circuit gives, in one place, the range of flows that both the model and the machine accept
(`BreathingCircuit.accepted_fresh_gas_flow_range_l_min`), and the slider reads it from there. The
slider is limited to that range because offering a flow the attached machine cannot set would
invite a refusal instead of preventing one.

The shipped profile (`data/machines/reference_circle_system.json`) records its deliverable range
(`deliverable_fresh_gas_flow_range`) as `null` and gives the reason in its `provenance_gap` field.
A test checks that the file still declares no range and says why
(`test_the_shipped_machine_declares_no_deliverable_flow_range_and_says_why` in
`tests/unit/test_parameters.py`).

`docs/machine-abstraction.md` says that two quantities in the machine survey's section (b8) are
not fields. They are a minimum total flow and a minimum oxygen flow. Neither is stored in a
machine profile, because that document allows a field only
where something uses it. A minimum total flow *is* the lower end of the deliverable range, so a
field of its own would store one number under two names in a safety-critical data file. A minimum
oxygen flow can be added when a hypoxic guard needs it, as an extension of the model rather than a
change to the data.

#### Supported run length

A run is supported up to **24 hours of elapsed simulated time**. This is the same kind of limit
as the four ranges in § "Supported input ranges". Outside the supported span, the equations
still solve exactly,
as § "Why a setting outside the ranges is refused" says of the flows. What stops at the boundary is
the claim that the solution represents a patient.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The run length differs from the flow ranges only in that it is reached rather than set. A flow
is a setting, and a value outside its range is refused. Because the run length is how far a
run has gone, it is checked as each step is taken, and otherwise only where a run opens with
time already elapsed. The supported span includes its end, so a run may complete the step that
lands on 24 hours. A step is 1 s, so the last step ends exactly there. A run that has
stopped at the limit rests on a point that the model accepts as the state of a run, and the
model refuses only the step from that point. The interface opens no branch there, because
such a branch could never step. A point past 24 hours can also be given directly rather than
reached, as the opening of a branch or a point to which a run is moved. It is refused before
any run is placed there. A time bookmark past 24 hours cannot be made at all, because a
bookmark accepts only a time that has already been checked against the limit.
<!-- provenance: core/simulation_step.py SIMULATION_STEP_S = 1 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

| Quantity | Limit | Declared and refused by |
| --- | --- | --- |
| Elapsed simulated time | 0 to 24 h (86 400 s) | `core/supported_ranges.py` declares it. `CaseInstant` there and `SimulationState` in `core/simulation.py` refuse a value past it. |

<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**The 24 hours belong to the case, not to each run.** The limit is argued from what the
model leaves out, which depends on how long the *patient* has been anesthetized. So a branch
shares the 24 hours its parent was using, and its elapsed time carries on from the point where
the branch was taken. A branch taken at 23 h has one hour left. A test checks that a branch
carries on the case's count of steps
(`test_a_branch_continues_the_case_s_step_count_so_the_envelope_is_the_case_s` in
`tests/integration/controller/test_controller_branching.py`).
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

##### What happens when a run reaches the limit

**Reaching the limit is not a failure, and the interface may not present it as one.** The
step past the limit is refused before it begins, so a run that stops there ends on a
completed step inside the supported span. Every displayed value is therefore a real solution
of the model. The run stops, and the interface says which limit was reached and why it is set
there. Reset starts a new run. Describing a correct model as a broken one misleads a reader as
surely as the reverse. It spends the interface's one signal for a real fault, and it teaches
a reader to discount that signal. The interface must not present the stop as a pause either.
Start is refused, because a resumed run's first step would be refused again.

**The banner that reports the stop is drawn in the muted color, as the status word above it
is** (`PL-0889`). The alert color stays with a run that failed and with a refused setting,
including a dial moved on the stopped run, whose refusal the stop's banner then states.

**A run says that the stop is coming before it arrives** (`PL-H2K2`). From 1 h 40 min of
simulated time before the limit, the banner reads, for example, "This run stops in 1h40m of
simulated time, at the supported run length of 24 hours", in the muted color, and counts down
with the clock. A stopped run or a failure takes the banner in its place. A refused setting
stays on screen until a setting is accepted, so a refusal made hours earlier can still hold
the banner. The countdown then follows the refusal in the same banner, in the alert color,
so the stop is never left unannounced.
The span is set so that the banner is on screen for at least 20 s of real time at the fastest
playback rate, 300 times real time, and for longer at every slower rate. Twenty seconds is the
least time that WCAG 2.2 SC 2.2.1 (Timing Adjustable) asks a page to give a user between
warning of a time limit and its end. W3C's Understanding document for that criterion was read
on 2026-11-22. A reader who knows the stop is coming can mark the run, branch it or pause it
before it stops, and does not take the stop for a fault. A branch taken within the last
1 h 40 min shows the banner from its first frame.
<!-- provenance: app/dashboard_frame.py APPROACHING_LIMIT_WARNING_REAL_S = 20 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

##### Why the limit is set where it is

**What bounds the run length is what this model omits.** The first omission is metabolism,
which this model does not have (`docs/MODEL.md` § "Known limitations"). The second is the fat group's flow.
The two human sources that `docs/MODEL.md` § "Known limitations" weighs do not agree about which way the
stored flow errs, but either way the flow acts directly on the slow tail of washout. The
published wash-in and elimination test compares the model with five minutes of elimination.
It explicitly refuses the two Yasuda papers' own multi-day curves, because *over days the
missing metabolism is no longer negligible, and neither is the fat group's flow*
(`docs/VERIFICATION.md` § "Published wash-in and elimination validation test"). A run beyond the limit therefore
displays a trace whose slow component is increasingly the two omissions rather than the
model.

Sevoflurane is the agent for which the missing metabolism matters most, so it is the agent
that constrains this limit. For sevoflurane, 2% to 5% of the absorbed dose is metabolized,
against far less for isoflurane and desflurane. Its metabolism begins immediately, and
fluoride and HFIP appear in plasma within minutes of the start of administration. Kharasch's
review, cited below (PMID 7486145), reports these figures. It also finds that metabolism
"does not contribute to the termination of clinical drug effect". That finding is what makes omitting
metabolism safe over a case. It holds while ventilation and perfusion dominate the trace,
and becomes progressively false once the only thing still moving is the slow tail, to which
this model gives no sink.
<!-- not-restated: 5 % -->

- Kharasch ED. *Biotransformation of sevoflurane.* Anesth Analg
  1995;81(6 Suppl):S27-38. PMID 7486145,
  doi:10.1097/00000539-199512001-00005.

**No stored value comes from Kharasch's review** (PMID 7486145). As a review, it is tier 2
under `docs/PARAMETERS.md` § "Source hierarchy", and a tier-2 source is the authority for a stored value only on a
recorded decision. No such decision has been taken for this review, and there would be
nothing for one to authorize. The 24 hours is not computed from 2% to 5%, and no parameter in
this model descends from that paper. What the review supplies is the magnitude and the
timing of the omission on which this limit rests, and tier 2 is legitimate for exactly that.
A limit computed from a metabolic rate would need the primary measurements instead. It would
be a different and better limit than this one.
<!-- not-restated: 5 % -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**The 24 hours are not inside the exposure range over which sevoflurane's metabolism was
measured.** The studies of plasma fluoride that Kharasch's review summarizes gave
sevoflurane doses from 0.35 to 9.5 MAC-hours (PMID 7486145). The limit bounds elapsed time, not exposure. A MAC-hour is
usually counted at the end-tidal concentration, which in this model is the alveolar fraction. A run
whose alveolar fraction is held near 1 MAC gains about one MAC-hour per hour. So it leaves the
measured range at about 9.5 hours, and reaches about 24 MAC-hours at the limit. Every agent's
dial opens at that agent's 1 MAC. The alveolar fraction stays below the dial during uptake,
so a run left at the dial gains somewhat less. Sevoflurane's vaporizer delivers at most 8%,
4.4 times its 1.80% MAC. Counted at the dial, a run held there reaches at most about 107
MAC-hours. A long run at or above 1 MAC end-tidal therefore leaves the measured range well
before 24 hours, and past that range even the size of the omission is unmeasured. The 24
hours rest not on the measured range but on the argument above, that the omission grows
steadily once only the slow tail is still moving, with no sudden break. Because isoflurane
and desflurane are metabolized far less, the same span omits less for them. A test recomputes
the hours and MAC-hours in this paragraph
(`test_a_long_sevoflurane_run_leaves_the_measured_exposure_range_as_printed`).
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: data/agents/sevoflurane.json mac_at_age_40_percent = 1.8 -->
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->
<!-- derived: 107 MAC-hours from data/agents/sevoflurane.json max_delivered_concentration_percent = 8, mac_at_age_40_percent = 1.8 -->

**Why 24 hours, and not a multiple of the slowest time constant.** At the shipped reference
settings, sevoflurane's fat group has an isolated time constant of about 42 h, which
`docs/MODEL.md` § "Tissue groups" defines. A limit set at several multiples of it would
favour exactly the long tail described above, the part of the trace that is most nearly all
omission. The fat time constant sets a minimum for the limit instead, and that minimum is a
fraction of one time constant. The run must last long enough that the fat compartment is
still visibly filling when it stops. 24 hours is about 0.6 of the isolated time constant.
By then a single compartment filling exponentially has gone a little over two fifths of the
way to equilibrium, so the fat trace still shows what it exists to show. The model's
slowest term is somewhat longer than the isolated time constant, so 24 hours is a smaller
fraction of it. `docs/MODEL.md` § "Time constants" gives that term and says why it is
longer. A run of a few hours would stop that trace near its start. The minimum says
nothing about how far above it a run may go. The span is also far longer than any
anesthetic this simulator is built to teach. A test recomputes the time constant and the
fractions in this paragraph
(`test_the_run_length_is_the_fraction_of_the_fat_time_constant_printed`).
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**Volatile sedation in intensive care is out of scope, deliberately.** It runs for days
through an anesthetic-conserving device, which is exactly the regime in which this model is
wrong. Supporting it needs a model extension, metabolism first. Raising this limit without
that extension would produce the plausible-looking wrong values that this document exists to
prevent.

##### The washout tail inside the limit

**Inside the limit, the washout tail already lacks its largest measured term, and the
displayed number does not say so.** Every washout that the two Yasuda papers fitted needed
five compartments. Their authors took the fourth to be fat filled by diffusion from the
well-perfused tissue beside it. This model has no such route. The fourth compartment
carries the largest term in the measured curve over most of the supported span: from about
1.8 to 3.1 hours after a 30-minute administration until about 20.7 to 29.4 hours. The
intertissue-diffusion note under `docs/MODEL.md` § "Known limitations" has the coefficients and the
arithmetic. All else equal, a tail without that store falls faster than the measured one
from about the third hour of elimination. Measured against the published mean curves over
the whole supported run, the shipped tail does so (`docs/VERIFICATION.md` § "The first 24 hours of elimination
against the published mean curves"). Two tests compute these hours and ratios from the
model and hold them to the values recorded there
(`test_the_fourth_compartment_is_the_largest_term_over_the_recorded_hours` and
`test_the_first_24_hours_of_elimination_against_the_published_mean_curves`). It runs about a
third below the curves from about the seventh hour until about the twenty-first. For desflurane it runs below them by half, from
3.4 to 15.3 hours. In the hours before that, it runs above them by 12 to 52% at the widest, while
the rebreathing circuit and the muscle group's slow return hold it up. At 23.5 hours of
elimination it runs above them again, by 12 to 24%, or by a factor of 2.1 for desflurane.
That is because this model's fat group returns more agent than the fitted fat term.
<!-- not-restated: 2.1 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**The tail's departures from the published curves do not move the 24 hours.** The limit rests on
the two omissions, metabolism and the fat group's flow
(§ "Why the limit is set where it is"), growing past negligible over the span, and the departures
come from neither of them. In `docs/VERIFICATION.md` § "The first 24 hours of elimination against the published mean
curves", the metabolism bound accounts for about an eighth of the excess where the tail runs
above the curves, and widens the gap where it runs below. The shortfall comes from the missing
fourth compartment, which is as present in the first hour as in the last, so shortening the
span would not remove it. Extending the span would add the late excess, which is still growing
at 24 hours. The limit therefore certifies how closely the late tail follows a measured washout
inside the span only as far as the comparison with the published mean curves goes.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

##### The code and tests behind the run length

**For developers.** The limit is declared as `MAXIMUM_ELAPSED_SIMULATION_TIME_S` in
`core/supported_ranges.py`. Widening it is a safety-critical change on the same terms as
widening a flow range. Argue the longer span against what the model omits, extend the
validation that covers it, and revise this section with the result.

The banner that announces the stop is built by `run_notice` in `app/dashboard_frame.py`. It
reads the limit from `MAXIMUM_ELAPSED_SIMULATION_TIME_S`, so it cannot announce a limit the
model does not enforce, and it opens `APPROACHING_LIMIT_NOTICE_S` before it. Tests in
`tests/unit/test_dashboard_frame.py` check its wording, when it opens and what outranks it,
from `test_the_interface_says_the_run_is_approaching_its_supported_length` on.
`test_a_refusal_made_before_the_warning_does_not_hide_the_countdown` checks that a refusal
still on screen keeps the countdown, and
`test_a_refusal_on_a_run_stopped_at_the_limit_is_drawn_as_a_warning` checks that a refusal
on the stopped run takes the alert color.
`test_the_supported_limit_banner_is_not_drawn_in_the_failure_colour` in
`tests/integration/simulation_view/test_simulation_view_run_stops_itself.py` checks the
colours of the stop's banner and a failure's.

Reaching the limit and handing in a value past it raise different errors. The step that would
carry a run past the limit is refused in `SimulationState.advance()` with a
`SimulationDomainLimitError`. That error is separate because reaching the limit is not a
failure, and the interface (`app/`) checks for it to choose its wording. A value past the
limit that is handed in is itself what is wrong, so it is refused with a
`SimulationConfigurationError` before any run holds it. A step count past the limit is refused
where the simulation state (`SimulationState`) stores it, and an instant past the
limit where it is built as a `CaseInstant`.

No separate check makes a branch share the case's 24 hours. Every check on the limit reads
the case's clock, as a step count or a case instant, and a branch continues that clock from
its parent. So the arithmetic that limits the original run also limits every branch of it.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**Each instant and each step count is a type, checked once where it is built**, as
§ "Supported input ranges" describes for the flows. Every instant at which a run is opened,
moved, keyframed, marked or branched is a `CaseInstant`, a subclass of `int` that holds a
whole number of seconds. Only its
constructor runs the check (`require_supported_case_instant`). The constructor accepts only
an `int`. It refuses a `float` whatever its value, because a run moves only by the one-second
step, and it refuses a `bool`. The places that keep an instant, or move a
run to one, require the type and refuse anything else with a `TypeError`, whatever its
value. These places are the opening of a run and every point it is advanced to
(`RunDefinition`), each `Keyframe`, a `TimeBookmark` and the `BookmarkCrossing` that a run
halts on, and the instant at which the controller branches a run
(`SimulationController.resumed_at`). The chart requires the type as well, where it fits or
places its time window from the newest run's instant (`assemble_chart_frame`, `fit_to_run`
and `preview_window`). The control record's instants are `CaseInstant` too:
`ControlChange.elapsed_s` and an adjustment's start and end. A value built as another checked
quantity is refused as a swapped argument, with no advice to rebuild it, both where the
instant is kept and by `CaseInstant` itself. One example is a step count (`StepCount`) passed
as an instant. Code that only passes an instant on is annotated with the type and checks
nothing again, such as a snapshot and the instants at which a branch is offered.

A count of completed steps is a `StepCount`, a subclass of `int`. It is checked only for what
a count can be checked for alone: it must be whole and not negative, and a `bool` is refused.
How many steps a run may complete is the run's limit and not the count's. So the simulation
state checks the count against the last supported count (`MAXIMUM_STEP_COUNT`, through
`require_supported_step_count`). The state makes that check at
every write to the field, in `__setattr__`. The constructor's checks and messages therefore
also apply to a count assigned straight onto a built state, and a refused value
leaves the field unchanged. The type checker (`mypy`) refuses such an assignment in `src/`. A
plain `int` count is refused with a `TypeError`. A count past the run length is refused with a
`SimulationConfigurationError`.
A flow written onto its compartment is treated the same way (§ "Supported input ranges"). The
state's uptake system is written once, when the state is built, because the count says how
far that one system has been advanced. A later write is refused with a
`SimulationConfigurationError`.

The step's check and the state's own check read the last supported count from one constant,
`MAXIMUM_STEP_COUNT`. A step is one second, so that count is the 24 hours in seconds, and it
is exact. The simulated time, `elapsed_s`, is the count times the step, which the state
builds as a `CaseInstant`. Both are whole numbers, so nothing is rounded, and a count is
accepted exactly when the instant it stands at is accepted. So the simulated time is never
refused as a `CaseInstant`, and a
branch is built or refused alike, whether it is taken from its parent's count or from its
parent's instant.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

An instant that a run is only *asked* about stays a plain `float`, such as the instant passed
to `RunDefinition.segment_at` and the ends of a drawn window. The run's own opening and end
bound such an instant, and the run checks that relation. Arithmetic on either type returns a
plain `int`, so a calculated instant or count is never taken as checked.

**Whether a run is at the limit is decided from the run, never from a refused step alone.** A
run comes to rest on 24 hours only by stepping onto the last supported count, and that step
is not refused. No branch can be opened there. A dial moved on a run stopped at the limit is
refused, and so is a fork on the limit, so a branch's Reset never returns it to the limit. If
the limit were recorded only from a refused step, a run standing on the last count would look
like an ordinary pause: Start offered, no limit notice, and a mark that the run never reached
reported as still ahead of a run that cannot step. So the
controller asks the core's own check (`require_supported_run_length`) whether the run's next
step would be refused. It asks every time the run's state is read and after every step, and
reports the limit with the reason that the refusal would give. A run stepping onto the last
count halts on the step that arrives there, not on the refused step after it. So no run
appears to be running, or paused, while it is at a point where no step is left. The interface
may catch a `SimulationDomainLimitError` on some other path, such as a setting. That error is
recorded as the reason, and it takes precedence over the reason derived from the run.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The limit is 24 hours (`test_the_supported_run_length_is_twenty_four_hours` in
`tests/unit/test_supported_ranges.py`), and the step that would cross it is
refused (`test_the_step_that_would_cross_the_boundary_is_refused`, in the same
file). Stopping there is not a failure
(`test_stopping_at_the_supported_run_length_is_not_a_failure` in
`tests/integration/controller/test_controller_supported_length.py`), and the
notice does not describe one
(`test_the_supported_run_length_notice_does_not_describe_a_failure` in
`tests/unit/test_dashboard_frame.py`). A run standing on the limit reads as
stopped from the step that arrives there
(`test_a_run_standing_on_the_supported_run_length_reads_as_stopped_from_the_arriving_step`),
and no branch can be taken where it stands
(`test_a_run_at_the_supported_run_length_offers_no_place_to_branch_where_it_stands`),
both in `tests/integration/controller/test_controller_supported_length.py`. The
step count and the case instant bound the same span
(`test_the_step_count_and_the_case_instant_bound_the_same_span`), and a `float`
is refused as a case instant whatever it holds
(`test_a_float_is_refused_as_a_case_instant_whatever_it_holds`), both in
`tests/unit/test_supported_ranges.py`.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

#### What is not bounded this way

The two gas volumes, of the breathing circuit and of the alveolar compartment, are **fixed
model parameters rather than controls**, and have no supported range. Each is set when the
run is built, and nothing changes it during the run. The interface has no control for
either. Both have a numerical envelope, 0.01 to 10 000 L, which is a separate claim,
stated in `docs/VERIFICATION.md` § "The numerical envelope". It says only where the arithmetic has been checked
against a high-precision calculation. It says nothing about which volumes describe a
patient, so it does not contradict the physiological argument below.
<!-- provenance: core/numerical_envelope.py MAXIMUM_VOLUME_L = 10000 -->

The two volumes have different sources. The alveolar gas volume is a patient parameter of
2.5 L, read from `data/patients/reference_adult.json`. The provenance table in `docs/PARAMETERS.md` lists it,
and § "The reference patient's parameters" there gives the FRC measurement it is compared with. The circuit volume is a *machine*
parameter of 6.0 L, read from `data/machines/reference_circle_system.json`. That is a third
kind of parameter file, beside the agent and patient files, because the breathing system
belongs to neither. The same table lists the circuit volume, and the note after the table
gives what is known of its origin, which is that no source has been adopted for it.
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6 -->

**Why neither gets a supported range.** A supported range describes an
envelope that a run can be steered *within*. The four controls in § "Supported input ranges"
each name an interval because a user can put the model anywhere in it. The verification
gates are what establish that the model represents a patient across that
interval. Neither volume moves. The single shipped value is the whole of each
volume's domain, and every reference measurement in `docs/MODEL.md` is made at
that value. An interval declared around it would assert verification across a
span that nothing has measured. That would be the same overstatement as
widening one of the four intervals without re-running the gates. Fixing the
value and saying so is the stronger claim, not the weaker one.

**What a wrong volume would be wrong for.** The argument is about physiology, as it is for
the four controls, not about numerical error. On 2026-09-06, with sevoflurane at the
0.1 s simulation step then shipped, a 0.005 L alveolar compartment and a 10 000 L circuit both
ran without incident. The agent balance held. So each gave an
arithmetically correct answer to a question that physiology does not ask. The model has
since been given a numerical envelope, and it now refuses the 0.005 L volume
(`docs/VERIFICATION.md` § "The numerical envelope"). A 5 mL alveolus
is not a lung. This model's few compartments, its fixed tissue volumes and its constant
partition coefficients are claimed to represent a patient only near the shipped values.
<!-- not-restated: 10000 L -->

**For developers.** `AgentUptakeSystem.for_agent()` reads both volumes from the
files, and the controller then writes the circuit volume it was built with, if it was
given one. `SimulationController` has no setter for either.

**What is left open, stated plainly.** Python code written against `core/` can still build
either volume anywhere in the numerical envelope, 0.01 to 10 000 L, by passing a
`CompartmentVolume`. So a 10 000 L circuit or a 0.01 L alveolar compartment is accepted.
`SimulationController` still takes a `circuit_volume_l` argument when it is built. Such
values are outside the verified domain, and only the numerical envelope limits them. They
cannot be changed during a run, and the interface cannot reach them at all. A run refuses
its next step when a change to either volume has moved the fractions it stopped at
(`SimulationState.advance`). The controller refuses its next step when the settings on the
core differ from the ones it last recorded (`PL-XRN8`). It also refuses its next control
change, before the change is applied, so a written volume is never recorded as one of the
run's settings (`PL-S8FM`).
They are chosen once, by someone who has gone to the trouble of building the model directly.
`BreathingCircuit.set_circuit_volume` remains for the same reason. It is how the value
reaches the circuit, and it holds the checks for agent conservation and capacity.
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->
<!-- provenance: core/numerical_envelope.py MAXIMUM_VOLUME_L = 10000 -->

**Each parameter file is the only source of its own values, and `core/` keeps no copy of
them.** `AlveolarCompartment` has no default for its gas volume or its ventilation, and
`BreathingCircuit` has none for its volume or its vaporizer maximum. Every shipped run is
built by `AgentUptakeSystem.for_agent()`, which reads the values from the agent, patient
and machine files and passes them on. The fresh gas flow keeps a default for a machine
profile that states no startup flow (`docs/PARAMETERS.md` § "The circuit volume and the default fresh gas flow" gives its
reason, its constant and its tests).
`test_for_agent_builds_the_circuit_at_the_machine_file_s_values` in `tests/unit/test_circuit.py`
and `test_for_agent_builds_the_alveoli_at_the_patient_file_s_values` in
`tests/unit/test_alveolar.py` check that a shipped run gets the file's values. The serious failure would be a change that stopped `for_agent()`
reading a file. Every row of the provenance table in `docs/PARAMETERS.md` for those values would
then silently describe a file that the model no longer uses. So each of the four values is also checked with a file that
states a different value, and that run fails if `for_agent()` stops passing the value on.
For the machine file the tests are
`test_for_agent_builds_the_circuit_at_a_changed_machine_file_volume` (3.3 L) and
`test_a_profile_stating_its_startup_flow_opens_the_run_at_that_flow` (2.0 L/min), both in
`tests/unit/test_circuit.py`. For the patient file the test is
`test_for_agent_builds_the_alveoli_at_changed_patient_file_values`, in the same file as the
other alveolar test (3.0 L and 5.0 L/min).
<!-- not-restated: 5.0 L/min -->

## Reset behavior

Reset pauses the simulation and keeps the user's selected settings. It also:

- sets simulation time to zero;
- clears the agent amounts in the circuit, alveoli, blood and tissues;
- discards the run, so that none of its states can be read or drawn;
- clears the recorded timeline of control inputs;
- sets the cumulative amounts delivered and exhausted, and the mass-balance
  residual, back to zero; and
- clears any recorded failure, so that a session halted by a failed step can
  start again from a clean state.

**Reset on a branch returns it to the point where it was taken from its parent
run, rather than to zero.** The branch's simulation time, state and
accounting go back to the fork, because that is where the branch began. The
states it holds before the fork are a copy of its parent's (§ "What this
requires of a branch"). Its timeline of control inputs then holds
the entries that the branch first opened with, followed by each setting that
Reset kept and that differs from the one the branch opened under.

**The simulator refuses Reset when the tissue flows no longer sum to the cardiac
output.** This mismatch can happen only when a perfusion fraction is changed in
a way that bypasses its range check (`PL-HQF5`, `PL-Z0HN`). A refused Reset
leaves the run exactly as it was. The refusal message, shown in the failure's
details under the banner, gives the two flows as they were set, in L/min, the
unit every readout shows.

After a refused Reset, the interface halts the run, as it does when a step
fails (`PL-M4M0`). The status word, the run controls and the banner show the
halt. The interface records the refusal as the run's failure. For other
failures, the banner names Reset as the way to recover. For a refused Reset, it
says instead that Reset was refused, and that no setting can repair the run,
because only a fault in the simulator causes the refusal. A new cardiac output
cannot repair it, because it scales every flow by one factor. The banner also
says that closing and reopening the application starts a new run (`PL-01GY`).
It names neither Reset nor a dial as the way to recover. If the run had already
failed from another cause, the interface
keeps that earlier failure as the reason, and the banner's advice on recovery
mentions the refusal.

**For developers.** Reset sets simulation time to zero by clearing the count of
steps taken. It discards the run's stored states, which then hold only the
cleared state at second 0, and opens a fresh run definition under the user's
settings. A run definition is the run's settings record: the settings in force
in each stretch, and the second at which each stretch opened
(§ "A run stores the state of every second it reaches"). The timeline
of control inputs is cleared because it belongs to the run that recorded it.

On a branch, the stored states are cut back to the fork, and the fresh run
definition opens instead on the stretch of the parent run that the branch was
taken from. The user's settings are recorded in it as a change at the fork. The branch's timeline and provenance then agree on its
settings (`PL-K5BS`, `PL-ZR49`).

Reset is refused when it cannot build the settings record that the fresh run
definition opens on. It builds that record from the compartments before it
changes anything (`SimulationController.reset()`). The build fails when the
tissue flows do not sum to the cardiac output, which can happen only when a
perfusion fraction is written in a way that bypasses its guard (`PL-HQF5`,
`PL-Z0HN`). The next simulation step (`AgentUptakeSystem.advance()`) refuses
the same record. It reports a failed step rather than a refused setting, because
a run whose record cannot be built is not worth continuing.

The tests check that Reset keeps every user setting
(`test_reset_preserves_all_user_settings` in
`tests/integration/test_sevo_controller.py`), pauses the run
(`test_reset_pauses_and_clears_concentration_history`), clears a failure
(`test_reset_clears_a_failure_and_restores_a_startable_session`), both in
`tests/integration/controller/test_controller_running.py`, and clears the
control-input timeline (`test_reset_clears_the_control_timeline_with_the_run` in
`tests/integration/controller/test_controller_control_timeline.py`). A branch's
Reset returns it to its fork
(`test_resetting_a_branch_returns_it_to_its_fork_rather_than_to_zero` in
`tests/integration/controller/test_controller_branching.py`). A refused Reset
leaves the run exactly as it was
(`test_a_reset_the_core_refuses_leaves_the_run_exactly_as_it_was` in
`tests/integration/controller/test_controller_run_definition.py`), halts it
visibly (`test_a_reset_the_core_refuses_halts_the_run_visibly`), and names no
setting as the way out
(`test_a_refused_reset_names_no_setting_and_sends_the_reader_to_restart`), both
in `tests/integration/simulation_view/test_simulation_view_run_stops_itself.py`.

## Agent-change behavior

Changing the running agent must begin a new run. Switching between volatile
agents is not modeled (see `docs/MODEL.md` § "Known limitations"), so there is no residual
washout to carry over. The model's values for the old agent would mean nothing
under the new agent's partition coefficients. A change of agent must therefore
do everything Reset does, and rebuild every compartment with the new agent's
parameters. It must also set the delivered concentration to 1 MAC of the new
agent rather than keep the old agent's percentage, because the same percentage
is a different clinical depth for each agent.

**For developers.** An agent change starts the run definition over
(`test_changing_agent_starts_the_run_definition_over` in
`tests/integration/controller/test_controller_run_definition.py`) and sets the
dial to the new agent's 1 MAC
(`test_set_agent_resets_delivered_concentration_to_the_new_agent_one_mac` in
`tests/integration/controller/test_controller_setup.py`).

## Discarding a run, and the questions that guard it

Beginning a new run **discards the current one**. All a user can look back at
is the run's stored states, its timeline of control changes and the simulated
time it reached. Nothing in the simulator saves them and there is no undo, so the
interface must follow these rules:

- Before the interface discards a run that has any elapsed simulated time or
  any recorded control change, it must say so and ask the user to confirm.
- The question must name what will be lost in the terms that the display
  already uses, so that the user can check it against the readouts.
- Declining must leave the run, its definition, its timeline and the control
  that offered the change exactly as they were.
- Choosing the agent that is already running is not a change of agent, so it
  must do nothing.

A run with no elapsed simulated time and no recorded control change is
discarded without a question, so a user who presses Reset first can then
change agent without one.

**Pressing a run's Reset confirms discarding that run, and no other run**
(project owner, 2026-10-18, ratified, over extending it to every run the press
takes with it, `PL-W5WX`). The display draws each branch beside its trunk
(§ "What this requires of a branch" defines the trunk, a branch and its fork).
Pressing the trunk's Reset also discards every branch, because a branch cannot
outlive its trunk. When a branch has run past its fork, or has had a control
change since then, the trunk's Reset says what that branch holds and asks before
it discards any run. The trunk's Reset also asks about a branch when the
simulator cannot tell what that branch holds. Any other branch is discarded
without a question.

In deciding whether the trunk's Reset asks before discarding a branch, an opened
entry does not count as work the branch would lose (`RunRecord.opened_with`).
Every later entry does, including a setting that the user changed and kept
through a reset. When the question is asked, the number of control changes it
states includes the opened entries, so that it matches the branch's "Control
changes" panel.
Turning a dial back to a value the trunk had before the fork is still a control
change, because the branch started from what the dial said at the fork.

**Every run waits while a question is open, and carries on as it was when the
question closes** (project owner, 2026-10-31, ratified, over letting the runs
go on stepping, `PL-TPBH`). Each of these questions blocks the rest of the
window: the trunk's Reset question, the question asked before a change of
agent starts a new case, and the questions from the Workspace strip. While one
is open, the user cannot press Pause on any run. A run that was running
resumes at the same playback rate, and a paused run stays paused. The wait
changes nothing in a run, so each run follows the same course as if the user
had answered at once, as `docs/VERIFICATION.md` § "The reproducibility guarantee" requires.

**For developers.** Runs with nothing to lose get no question because a
question asked when nothing is at stake teaches the user to answer it without
reading it. By the time something is at stake, the question would go unread.

In the code, the entry that a branch was opened with is `RunRecord.opened_with`.
Four tests in `tests/integration/simulation_view/test_simulation_view_comparison.py` enforce the rule for
branches: `test_resetting_the_trunk_asks_before_dropping_a_branch_that_holds_work`,
`test_resetting_the_trunk_asks_before_dropping_a_branch_set_back_to_the_earlier_flow`,
`test_declining_the_trunks_reset_leaves_every_run_as_it_was` and
`test_confirming_the_trunks_reset_starts_the_case_over_without_the_branch`.

Runs wait during a question because otherwise a user who spent ten seconds on
it at 300× playback would come back to a case 50 simulated minutes further on.
The wait works by skipping ticks of the step timer. One test enforces the wait
during the trunk's Reset question
(`test_the_run_does_not_advance_while_a_reset_question_is_open`), and two tests
beside that one do the same for the question asked before a change of agent
and the Workspace strip's questions.

## What a branch comparison asserts, and what it does not

**A difference between two runs is real, but a comparison does not say what it
means for a patient.** The difference does not come from rounding, from the
order of the program's arithmetic, from the playback rate or from the computer
(`docs/VERIFICATION.md` § "The reproducibility guarantee", `docs/INTERFACE.md` § "Each second has one stored state"). A
comparison can teach only the mechanism: which way a curve moves when one thing
changes, why it moves that way, and roughly how fast, in a model whose
structure makes the reason easy to see.

### What is compared, and what the two runs share

**A comparison shows two managements of one case:** the trunk, and a branch
taken from it at its fork (§ "What this requires of a branch").

**The display shows at most two runs.** While two are shown, another branch is
refused rather than replacing the one on screen. No branch is compared with
another branch, only with the trunk it was taken from. Nothing on screen
surveys a range of managements or ranks them, because only two were run.

**After the fork, a difference between the two runs is caused by the settings
that differ between them, and by nothing else in the model.** The program
guarantees that both runs share the following:

- **The patient.** Both runs use the same reference adult, which the branch
  takes from the trunk at the fork.
- **The agent.** The branch takes the trunk's agent at the fork, and neither
  run's agent can be changed while the comparison is shown.
- **The equations, the parameter set and the model version.** Both runs come
  from the same program.
- **The circuit volume.** The branch takes the trunk's circuit volume, which
  cannot be changed during a run.
- **The simulation step.** Every run takes the same step of one second, and a
  fork is a whole second, so no fork lies between two steps.
- **Every setting up to the fork.** The branch's settings are replayed from the
  trunk's record of setting changes, then checked against the trunk's own
  settings at the fork.
- **The bookmarks.** A bookmark marks an instant or a height on a curve, and a
  run halts when it reaches one. The branch opens with the trunk's bookmarks.
  While the comparison is shown, each bookmark that is added or removed in the
  Bookmarks View is written to both runs, so the two runs always hold the same
  bookmarks. Each run has its own standing on each bookmark.
- **The time frame.** Both runs count time from induction. The chart anchors
  both to induction rather than to either run's own start, so the two traces
  are compared at the same instants.

**For developers.** The architecture document describes a branch's structure
(`docs/ARCHITECTURE.md` § "What a branch is, and what it shares with its
parent").

The roadmap leaves a third run and a comparison of two branches out of scope
for v0.5.0 (`ROADMAP.md` § "Explicitly out of scope for v0.5.0"). A test checks
that another branch is refused while two runs are shown
(`test_a_second_fork_is_refused_while_two_runs_are_shown` in `tests/integration/simulation_view/test_simulation_view_branch_control.py`).

The code enforces what the two runs share as follows:

- The reference adult is stored in
  `src/anesthesia_sim/data/patients/reference_adult.json`. Two tests check that
  a branch carries the trunk's patient and agent
  (`test_a_branch_is_the_agent_and_patient_its_parent_was`,
  `test_a_case_s_branches_carry_the_trunk_s_agent_and_patient_at_the_fork` in `tests/integration/controller/test_controller_branching.py`).
- A branch refuses an agent change outright (`set_agent`,
  `test_a_branch_cannot_change_its_agent_out_from_under_the_case` in `tests/integration/controller/test_controller_branching.py`). On the
  trunk, the agent selector is locked
  (`test_the_trunks_selector_is_locked_while_two_runs_are_shown` in `tests/integration/simulation_view/test_simulation_view_comparison.py`). Changing
  the agent begins a new run (§ "Agent-change behavior"), so an agent change
  during a comparison would end one of the two runs rather than vary it.
- Exact reproducibility is not guaranteed across model versions or platforms
  (`docs/VERIFICATION.md` § "The reproducibility guarantee"), and the two runs of a comparison always
  share one model version and one platform.
- The circuit volume is a build-time parameter with no live setter
  (`test_the_circuit_volume_is_a_build_time_parameter_with_no_live_setter` in `tests/integration/controller/test_controller_running.py`).
  It is applied to a branch before any state is.
- Every run takes the one step that the core defines (`SIMULATION_STEP_S`), so
  a branch cannot step differently from its trunk. A test checks that a branch
  steps to where its trunk stepped
  (`test_a_branch_steps_to_where_its_parent_stepped` in `tests/integration/controller/test_controller_branching.py`). A fork instant is a
  `CaseInstant`, which is built only from a whole number of seconds, and a
  fork instant that was not built as one is refused
  (`test_a_fork_instant_not_built_as_a_case_instant_is_refused` in `tests/integration/controller/test_controller_branching.py`).
- A test checks the replayed settings
  (`test_a_branch_inherits_its_parent_s_settings_at_the_fork` in `tests/integration/controller/test_controller_branching.py`).
- A test checks that a branch carries the trunk's bookmarks
  (`test_a_branch_opens_carrying_the_marks_of_the_case_it_continues` in `tests/integration/controller/test_controller_bookmarks.py`).
- Each column of the chart stands for an instant at which it draws a value. A
  test checks that a branch uses the trunk's columns
  (`test_a_branch_is_drawn_on_the_same_columns_as_the_run_it_forked_from` in `tests/integration/controller/test_controller_branching.py`). A
  fork at a bookmark adds at most one column, the fork itself
  (`test_a_bookmark_branch_draws_one_column_its_parent_does_not_and_it_is_the_fork` in `tests/integration/controller/test_controller_marks.py`).

#### What differs between the two runs

**Everything that either run records after the fork is what its learner did to
it**, for three reasons. Taking a branch leaves the trunk unchanged. The
branch's record of setting changes opens with copies of the trunk's changes at
the fork, and holds none of the trunk's earlier changes. A reset branch keeps
those copies and can record the learner's settings after them
(§ "Reset behavior").

**For developers.** In the code, a run's record of setting changes is its
control timeline. Two tests check what a branch's control timeline opens with and that forking leaves
the trunk untouched
(`test_a_branch_opens_with_only_the_change_it_runs_under_in_its_timeline`,
`test_forking_leaves_the_trunk_untouched` in `tests/integration/controller/test_controller_branching.py`).

Each entry that a reset branch keeps states a setting in force from the fork
on, so a reset does not change what can cause a difference after the fork.

Building the case twice instead of forking would leave the two runs differing
by everything that was not reproduced identically, and a learner could not see
which differences they had caused.

### The shared history is identical by construction, not by measurement

**Before the fork, a branch and its trunk are exactly equal.** The branch holds
a copy of the trunk's stored states up to the fork, and from the fork on it
repeats the trunk's steps until a setting differs. This holds for every branch
the program builds (§ "What this requires of a branch"). There is no error to
allow for, and none is shown. The chart draws stored states, so the two drawn
traces agree in every digit at every point they share, wherever the branch was
taken (§ "Each second has one stored state").

**A branch's equality with its trunk before the fork sets no bound on anything
after it.** Only the settings and the model decide how far the two runs
diverge, in which direction, how quickly, and whether they converge again.

**For developers.** The tests check equality through the controller, at each
stored second and at the drawn columns
(`test_a_branch_reproduces_its_parent_at_every_instant_they_share` in `tests/integration/controller/test_controller_branching.py`,
`test_a_bookmark_branch_and_its_parent_agree_at_every_column_they_share` in `tests/integration/controller/test_controller_bookmarks.py`), and
for a branch taken at any whole second
(`test_a_branch_at_any_whole_second_holds_its_trunks_states_up_to_that_second` in `tests/integration/controller/test_controller_stored_states.py`).

### Neither run is a prediction for a patient

**This model has one patient, and no variability around it.** No equation takes
a covariate that distinguishes one patient from another, such as weight, age,
sex or body composition. Nothing scales a volume, a flow or a coefficient from
such a covariate (`docs/MODEL.md` § "Known limitations"). The two runs are two trajectories of
*one* modelled patient under two managements. They are not two patients, not
two samples from a population, and not a range.

**So a difference between the runs is a property of the model, not an expected
clinical difference.** It carries no interval, spread or distribution, because
the model contains nothing that could supply one. It does not say how much two
patients managed those two ways would differ, how far a real patient would
depart from either curve, or how likely either management is to reach a given
state by a given time. It says what these equations do under these two
managements, within the limits that § "Supported input ranges" and
§ "Supported run length" declare, and with the fidelity that `docs/VERIFICATION.md` § "Published
wash-in and elimination validation test" establishes.

**A branch that differs in cardiac output is still not a second patient.** This
is the case most likely to be misread, because cardiac output is both a setting
the learner can adjust during a run and the quantity by which a clinician most
readily tells one patient from another. Dialling it changes this patient's
circulation. Its effect on uptake is a real property of these equations, and
setting it differently in the two runs is legitimate. But a patient who differs
in cardiac output differs in compartment volumes too, and this model keeps
those volumes fixed. So changing cardiac output alone shifts every tissue time
constant $`V_i \lambda_{i:b} / Q_i`$ in a direction that flow and volume
changing together need not take. `docs/PARAMETERS.md` § "The evidence behind the known limitations" gives the size of this
artifact for a cardiac output scaled to body weight with the volumes kept fixed,
and the same arithmetic applies here.

**Do not read a comparison as "low flow woke this patient twelve minutes
sooner."** Three separate things are wrong with that reading, and only the
first is about variability.

- **"this patient"**: there is one modelled patient and no population around
  it, so nothing on screen is about a patient at all.
- **"woke"**: this model has no effect-site compartment and defines
  $`F_a \equiv F_A`$ (`docs/MODEL.md` § "What the model represents"), so it has no measure of
  responsiveness in which two runs could differ. The nearest thing the chart
  shows is the vessel-rich trace read against the MAC-awake band. That band is
  one standard deviation either side of a published population mean, and it is
  not a prediction for the patient on the screen (§ "MAC-awake as a chart
  reference").
- **"twelve minutes"**: a duration read between two curves inherits every
  limitation of the model that drew them, and this model does not claim to get
  a difference in emergence time right to the minute (`docs/MODEL.md` § "Comparing two runs").

**For developers.** The dashboard carries the educational disclaimer
(`test_the_dashboard_carries_the_educational_disclaimer` in
`tests/integration/simulation_view/test_simulation_view_two_runs.py`), and the
disclaimer says what the tool is not
(`test_the_educational_disclaimer_says_what_the_tool_is_not` in
`tests/unit/test_dashboard_frame.py`).

### What the interface may assert about a comparison

The interface may mark the fork, where the two runs split. It may name the run
that each displayed value and each record of setting changes belongs to
(`docs/VERIFICATION.md` § "Reasonably foreseeable misuse, and the hazards the presentation carries",
the row on reading one run's value as the other's). And it may show the two
standing disclaimers: the one on interpretation beside the readouts, and the one
on use across the foot of the window.

**The interface must not draw the conclusion for the reader.** That rules out a
difference trace between the two runs, a score or ranking of one management
against the other, a time-to-wake-up figure, and a sentence stating what the
comparison shows. As checked on 2026-09-21, the interface draws none of them.
Each would state a conclusion that the model does not support. A qualifier
beside any of them would not repair that, because the reader would act on the
conclusion and not on the qualifier. § "MAC-awake as a chart reference" makes
the same argument about a wake-up readout.

**Two features of the interface come close to drawing a conclusion, and neither
does: the clock after a run halts on crossing a bookmark, and each run's record
of setting changes.**

- A run halts on the step that crosses a bookmark, and the clock then shows
  where that run actually stopped (§ "Halting on a marked crossing"). Two runs
  halted at one marked height therefore show two instants. Each is an instant
  that its run *reached*, not a predicted time for an endpoint that the run has
  not reached.
- Each run's record of setting changes states what that run's learner did, not
  a difference between the two runs. That is why the record's heading names its
  run rather than the comparison.

**For developers.** The fork's mark is `BRANCH_POINT_LEGEND_LABEL` in
`src/anesthesia_sim/app/dashboard_frame.py`, and the two disclaimers are
`INTERPRETATION_DISCLAIMER_TEXT` and `USE_DISCLAIMER_TEXT`. The check on
2026-09-21 covered `src/anesthesia_sim/app/dashboard_frame.py`,
`src/anesthesia_sim/app/chart_frame.py` and
`src/anesthesia_sim/app/qt_chart.py`.

Before the fork a difference trace would read exactly zero, because the two
runs hold the same stored states there (§ "The shared history is identical by
construction, not by measurement"). Its fault is after the fork, where it
would state the conclusion that the paragraph above rules out.

## Interface boundary

The interface shows the model's results and controls the run, but it does none
of the model's calculations. It may:

- display values;
- convert fractions to percent;
- show a modelled value in another unit that this document names: a multiple
  of 1 MAC, an amount in millilitres, a cost at a price that the reader sets,
  or a compartment's share of the agent;
- collect user settings;
- issue Start, Pause, and Reset commands;
- take a branch of a run, which continues the case in another way from an
  instant that the run passed through;
- halt a run on the simulation step that crossed a mark, or when the run
  reaches the supported run length;
- halt a run, and record why, when the model stops with an error;
- report a value that the model refused; and
- display mass-balance status.

Under the conditions set out below, it may also:

- draw the states that the run stored, at the seconds of a window of time
  that the interface chooses;
- choose how wide a window of the run the chart shows, and how its time axis
  is ruled;
- draw only some of the compartment traces, when the user asks;
- draw, while the user holds a slider's handle, the trajectory that the run
  would take if the value under the handle were applied, computed by the model
  and marked as a prediction (§ "A preview of an unapplied setting");
- draw a published clinical constant as a chart reference, at a height that
  the chart's own axis gives meaning to;
- form the ratio of two modelled fractions where this document names it as a
  displayed quantity;
- declare where one adjustment of a control begins, so that the run's record
  of its inputs can be read as the user's actions that produced it; and
- choose how many simulation steps to take at a time, so that a run can be
  played faster than real time.

It must not:

- calculate uptake, partitioning, tissue flow, mixed-venous return or mass
  balance;
- integrate the model's equations;
- correct negative stores;
- change the model's state directly;
- continue a run past a step that the model could not complete;
- take extra simulation steps to catch up when it falls behind real time, or
  otherwise let elapsed real time decide how many steps a run takes;
- change the simulation step size in response to a playback control, or
  advance a run at a rate other than the one it displays;
- let a display choice, such as the chart's window width, change what a run
  recorded, or present a chart window narrower than the run as though it
  showed the whole run;
- present a run halted by a failure as though it were paused;
- discard a run that holds recorded state without stating what will be lost
  and asking the user to confirm, unless the user pressed that run's own
  Reset, as § "Discarding a run, and the questions that guard it" requires;
- display a concentration at a finer resolution than § "Displayed precision"
  justifies, or show a value that the model does not resolve as though the
  model asserted it; or
- predict when the simulated patient would wake, or display a
  time-to-awakening figure of any kind (§ "MAC-awake as a chart reference").

**Every trace and every readout names the substance it shows.** A chart trace
shows one compartment of one substance, because a compartment fraction means
nothing without the substance it is a fraction of. Today a run contains one
substance, its agent, and changing the agent starts a new run rather than
adding to this one. A trace draws only the substance it names. The readout row
names the substance itself, so the user need not carry it over from the agent
selector. A compartment value and the trace beside it always name the same
substance.

**For developers.** The readout row names the substance its numbers belong to
(`test_the_readout_row_names_the_substance_its_numbers_belong_to` in
`tests/unit/test_dashboard_frame.py`), and a drawn window refuses another
substance (`test_a_drawn_window_refuses_another_substance` in
`tests/integration/controller/test_controller_run_definition.py`).

### What the chart draws

Every point that a chart trace draws is a state the
run reached, at the instant where it is drawn. The interface never interpolates, smooths,
averages or otherwise makes up a plotted value. Each point is the state that
the run stored for that second, which is the state the readouts showed at that
second. The values that a chart draws are for display only, and the program
prevents their use for anything else (§ "Each second has one stored state" above).

**The chart draws the run's state at one instant for each pixel boundary of
its widest plot, and never at fewer than 150 instants, unless that would put
two drawn instants less than one second apart.** A run stands only on whole
seconds, so the chart draws no instant between two of them. On an axis that
shows more seconds than the plot has pixels, a trace need not draw every
second, because a second is narrower than a pixel there. The instant that the
numeric readouts show
is always drawn, so the end of a trace always agrees with the readouts beside
it. When a plot becomes wider, after the user resizes the application window or
drags an area's border, it is redrawn at its new width on the next screen
update, whether the run is running or paused. Two rules set where the drawn
instants fall:

- **The drawn instants lie on a grid that starts at the case's time zero.**
  A run branched from another therefore draws at the same instants as the run
  it branched from, and the two can be compared point for point. Each drawn
  instant falls on a whole second, so the hover readout can give
  the exact time of the state it shows.
- **Every control change inside the window is a drawn instant.** Between
  control changes each compartment's value is a sum of exponentials, with
  bounded curvature and no hidden transients, so every sharp feature of a run
  is at a control change. A grid that stepped over one would draw a straight
  line through the very instant that the user is looking for. The point drawn
  there is the state that the run stored for that second. The
  chart therefore shows every control change exactly, to the last digit the
  readouts display.

**Between control changes, the drawn line is never further from the run than the
time that one pixel of the plot spans, except at a peak or a trough.** It passes
through the run's exact state at every drawn instant, and drawn instants are no
more than a pixel apart. The exception to that spacing is an axis that shows
fewer seconds than the plot has pixels across it: a one-minute axis on a plot
wider than 60 px, and a fifteen-minute axis on one wider than 900 px. There the
chart draws every second, and the line segment between two drawn instants spans
more than a pixel. Where the run only rises or only falls between two drawn
instants, the run and the straight segment drawn between them cross every level
inside the same pixel. This one-pixel guarantee is in time, not in percentage
points. Where a trace is steep, the run can change by many percentage points
within one pixel of time. No display shows a value between drawn instants, the
hover readout included (§ "The chart's hover readout").

The straight segment between two drawn instants starts and ends on the run's
curve, but can lie above or below the curve in between. The table gives that
vertical gap where it is largest, in percentage points (pp), computed on
a plot 1 000 px wide. A time base is a window width that the chart offers, and
the spacing between drawn instants is that width divided by 1 000, rounded down
to a whole second and never less than one second.

| Time base | Spacing | Sevoflurane 2% to 4%, worst trace | Desflurane 0% to 12% to 6%, worst trace | Desflurane, alveolar |
| --- | ---: | ---: | ---: | ---: |
| 15 min | 1 s | 0.0005 pp | 0.0031 pp | 0.0031 pp |
| 1 h | 3 s | 0.0038 pp | 0.023 pp | 0.023 pp |
| 4 h | 14 s | 0.046 pp (circuit) | 0.27 pp (circuit) | 0.21 pp |
| 12 h | 43 s | 0.21 pp (circuit) | 1.20 pp (circuit) | 0.26 pp |

<!-- provenance: app/chart_time_base.py SELECTABLE_TIME_BASE_FLOOR_S = 900 -->

<!-- provenance: core/simulation_step.py SIMULATION_STEP_S = 1 -->

The gaps grow with the spacing, so a narrower plot has larger gaps and a wider
plot smaller ones. They bound the error in a trace's *shape* inside one pixel
column, never in a displayed value.

**A compartment can peak or dip between two columns, and the chart draws that
peak or trough too.** Because the alveoli and the venous blood keep filling
for a moment after the vaporizer is turned down, a trace can peak between two
columns, above its value at both. For each compartment, the chart also draws
the second at which the compartment is highest between two columns and the
second at which it is lowest, where that value lies outside its values at
both columns. So each trace reaches the highest and the lowest value that the
run stored between any two columns.

A chart that drew only its columns fell short of such a peak. Over five
simulated runs that each change the dial at 600 s, the largest gap on any time
base was 0.0094 pp, on the mixed venous trace at the desflurane dial-down on the
eight-hour time base. The gap depends on where the change falls between two
columns: the same dial-down at the reference adult's flows, made at 629 s, left
a gap of 0.036 pp on the vessel-rich trace on the twelve-hour time base, against
a readout resolution of 0.01 pp. Both gaps are for a plot 1 000 px wide,
measured on 2026-11-21.

A preview is drawn by the same rule for its first hour, with the second of
each predicted peak and trough between two columns. After its first hour it
draws one value for each column and its right edge. Turning a setting causes
the sharp peaks, and they come within the first hour. Measured for each
shipped agent under eight setting changes, with columns from 43 s to 579 s
apart, a preview drawn one value per column fell short of a peak by up to
0.17 pp in the first hour, and by at most 0.000002 pp after it (`PL-Z6C8`,
measured 2026-11-21). Predicting every
second to the right edge of a 12-hour axis took 0.26 s, so a drag on a dial
stuttered. The preview now takes about 0.03 s on any axis.

**The F_A/F_I plot draws the ratio's own peaks and troughs between two columns
too** (`PL-DN13`). The ratio can turn at a second where neither fraction does.
After the dial is raised, the inspired fraction rises faster than the alveolar
one, so the ratio falls for some seconds and then recovers. So the chart also
draws the second at which the ratio is highest and the second at which it is
lowest between two columns, by the rule it uses for a compartment. A second
whose inspired fraction is too small to divide by has no ratio. That second is
left out of the search, and a column with no ratio is not compared with.

A plot that drew the ratio only at its columns and at the fractions' turns
could draw it above its trough. With the default sevoflurane patient on the
twelve-hour time base, the dial was raised to 8% at each second from 30 s to
102 s in turn. The largest gap between the drawn line and the trough was 0.090
of the ratio on a plot 1 000 px wide, 0.12 at 600 px and 0.065 at 1 500 px. The
axis spans 0 to 1.15, so a gap of 0.090 is about 8% of the plot's height. The
same dial raised later in the run left smaller gaps: up to 0.022 at 1 000 px
when raised to 8% between 600 s and 672 s. Measured on 2026-11-22.

<!-- not-restated: 8 % -->

**The F_A/F_I plot also draws the second at which the ratio crosses
equilibrium between two columns** (`PL-CJJ1`). A wash-in stretch ends on the
first drawn point past equilibrium, so that the curve meets the equilibrium line
and ends there with a dot. After the dial is closed, one step carries the ratio
at most 3% past equilibrium, but the next column can be minutes later, and the
ratio there is far above the plot's top. Before this rule the curve
then stopped below the line with no dot, which looks like a cut-off trace rather
than a finished wash-in. With the run of 60 minutes at the default dial
followed by 20 minutes with the dial closed, this happened at 17 of 66 pairs
of time base and plot width tried, from 300 px to 1 600 px, and it happens at
none of them now. The crossing second is a stored state, as every drawn point
is. Where the first second outside the domain has no ratio, because the
inspired fraction is too small to divide by, the stretch ends without a
crossing, as before. A stretch that starts after the dial is raised starts on
the line only when the ratio's last second outside the domain is drawn. A large
step of the dial can carry the ratio in one second from above the plot's top to
well below the line, and the stretch then starts below the line, because the
ratio never took a value in between.

**For developers.** `chart_time_base.wash_in_crossing_seconds` chooses the
crossing seconds. `controller._with_extremes` adds them to every drawn window
and to a preview's first hour, and `controller._with_later_crossings` to the
rest of a preview. `test_a_wash_in_stretch_at_a_wide_time_base_ends_at_equilibrium`
in `tests/unit/test_chart_frame.py` reproduces the run above.

### What the reader chooses: traces, window and playback rate

**The user chooses which compartment traces are drawn and how wide a window
of the run the chart shows, and neither choice changes the run.** The two
choices change no model state and nothing in the run's definition, and
identical inputs still produce identical results. The window width therefore
sits outside "Runtime controls", with the other interface settings.

A user cannot compare two compartments while four other lines cross them, so
the interface may draw only some of the six traces. When it does:

1. The numeric readouts still show every compartment's concentration
   (§ "Minimum displayed outputs"). A chart with two curves is a chosen view of
   six modelled compartments, not a model with two.
2. The display states, for every compartment, whether its trace is drawn. A
   legend entry for a line missing from the plot claims something about the
   run that the run does not support.

A case runs for hours, but the moment a learner is most likely to be watching
lasts minutes, and no single window width serves both. Two conditions apply to
the width that the user chooses:

1. The width is fixed by the selection, never by how long the run has been
   going. A window that grew with the run would change the slope of every trace
   while the underlying rates stayed the same.
2. A setting that claims to show the whole run shows all of it, at every
   length. A narrower window labelled as the whole run misstates what the user
   is looking at.

See § "The chart's time base" for the widths, the ruling and the labels that
meet these conditions.

A **chart reference** is not a trace. It draws a published constant, not a
state of the run, so the rule that every drawn point is a state the run reached
does not apply to it. Instead, it must be labelled. Its label states the value
and the divisor it was drawn from, and names the compartment it is to be read
against. The reference differs in kind from a compartment trace by its type of
mark, not by colour alone. A user with no reason to think otherwise takes an
unlabelled horizontal line for a modelled quantity, and so mistakes a measured
value for a modelled one.
See § "MAC-awake as a chart reference".

A **displayed ratio** of two modelled fractions is a trace, so the rule that
every drawn point is a state the run reached applies to it. Each point is formed
from one substance's two fractions in one state of the run, at the instant
where it is drawn. A ratio also needs a stated **domain**: the states of the run
for which it is drawn. A ratio of two modelled values can be undefined, when its
denominator is zero, or can fall outside what the plot claims to show. In
neither case may the interface substitute a number. Four rules follow:

1. A drawn instant outside the domain gives no point, rather than a point moved
   to the nearest limit, extrapolated or set to a default value. The one
   exception is the first drawn instant past each end of a stretch of the
   trace. It is drawn at its own value where it has a ratio no higher than a
   fixed ceiling, so that the trace meets the boundary it crossed.
2. The trace breaks where the domain does, and does not join across the
   instants it skipped, because a join would draw values the run never
   produced.
3. The display states which two quantities the ratio is of, in the terms this
   document uses for them.
4. Where the trace is absent, the display says at which boundary it stopped,
   because otherwise an absent trace looks like a run that stopped.

See § "F_A/F_I as a displayed ratio", the only such quantity today.

A **control mark** shows the instant on the time axis at which the user moved
a control. It draws no value and says nothing about the vertical axis, so the
rule that every drawn point is a state the run reached does not apply to it.
Instead, it must be labelled. It differs in kind from both a trace and a
reference, by something other than colour. The display identifies it as a
record of a user input, not of anything measured or modelled, and states which
control moved and to what setting. A bare mark says only that something
happened, and invites the user to supply their own explanation for the change
in the curves beside it.
See § "The control-input timeline".

Declaring where one adjustment of a control begins concerns the input device,
not the model. The run receives only the value that a drag applies when its
handle is released, so only the interface can tell one turn of a control from
two. The declaration records no
value. It must not change the simulation state, what the run records or what
the model computes.

**A playback rate is a number of steps, never a step size, and it must be on
screen.** Real time is too slow to watch the two compartments that make uptake
and distribution worth teaching. At the reference settings, sevoflurane's
isolated time constant is about 135 min for the muscle group and about 42 h for
fat (`docs/MODEL.md` § "Tissue groups").
The interface advances the run in ticks, one every 100 ms of real time. Each
tick adds the playback rate times 100 ms to the simulated time that the run is
owed, and the run takes one step for each whole second owed. At real time the
run therefore takes one step on every tenth tick, so the clock and the readouts
change once a second. At 5× it takes one step on every second tick. At 20×,
60× and 300× it takes 2, 6 and 30 steps on every tick. Faster playback is
allowed under three conditions of different kinds.
<!-- provenance: app/dashboard_frame.py SIMULATION_TICK_INTERVAL_MS = 100 -->

The first condition is arithmetic. A rate is a whole number of simulated
seconds for each real second, and the simulated time owed is counted in whole
milliseconds. So nothing is rounded: the part of a second left over after a
tick is carried to the next tick, and the run advances at the displayed rate to
within one step. The step itself is the same at every rate. So faster playback
stays within "The reproducibility guarantee":
identical inputs still produce identical run definitions, and two learners
comparing the same case at different speeds are comparing the same arithmetic.

The second condition is control resolution, and it limits that last claim. The
two learners are comparing the same *case* only if neither of them touches a
control. The same slider moves made at two rates land at two different
simulated instants and produce two different runs. The runs differ because the
inputs differed, not because the arithmetic did. A change made during play can
act only at instants 1, 1, 2, 6 and 30 simulated seconds apart at 1×, 5×, 20×,
60× and 300×. `docs/VERIFICATION.md` § "Supported simulation step" gives that grid
and how far a delay of one grid step can shift a displayed compartment. It also
gives the route that places a change on a chosen whole second at every rate:
pause, change the setting, then resume. No route places a change between two
whole seconds.

The third condition is human factors, and it is why the rate is a required
display rather than a preference. A rate is a mode. A clock is easy to misread
at a glance when it advances at sixty times real time beside numbers that look
like a live case. So the rate is shown wherever simulated time is shown, at
every rate, including real time. If the label were absent at 1×, its presence
would become the signal, and a user would have to be taught that convention
instead of reading the rate off the screen. The rate states only how fast the
interface is playing the run. It implies nothing about the model or the
patient, and it is not a second reading of the clock beside it.

**The rate label shows the rate that was set: the multiple of real time chosen
with the playback control.** The interface computes the simulated time that
each tick owes the run from that setting, so the label always agrees with the
steps the run takes. The simulated clock is exact at every rate, because simulated time is a
count of the steps taken. Whether the run keeps pace with real time depends on
the computer. When the computer cannot run a tick in time, the tick is lost,
and no extra steps make it up. The **delivered rate** is the set rate times the
fraction of ticks that ran. In a measurement on 2026-09-27, every rate from 1×
to 300× delivered 98.9 to 99.9% of its setting over 8 to 30 s. On a computer
that loses ticks, the run plays slower than the label says, and nothing on
screen shows the delivered rate.

### The code and tests behind the interface boundary

**For developers.** A chart draws from a window of states (`DrawnWindow` in
`app/run_series.py`), one for each instant that a frame plots. The controller
reads each of them from the run's stored states (`SimulationController.drawn_window`,
`SimulationState.stored_states`), so a point on a trace is the value that the
readout showed at that second (`PL-MH9J`). Whole-second steps brought in the
stored states, which replaced the earlier design of keeping no stored samples
and computing each point from the run's definition (project owner, 2026-09-05).

Each state carries its substance's six compartment values, as fractions of one
atmosphere, under stable identifiers (`RecordedQuantity`). A trace addresses one
of them as a substance-and-quantity pair (`RecordedSeries`). When a frame asks
for a substance that the run does not contain, it fails rather than drawing
whichever substance is in the run. The window is read by substance and quantity
rather than by six named fields, because six flat names can describe only one
substance. A
second substance would then need six more names, or values pooled with the
first substance's, and pooled values show a correct number under the wrong
label.

A frame is rendered from the running agent's state at one instant
(`SimulationSnapshot` in `app/controller.py`), which carries the six compartment
values as flat named fields. This difference from the window is a decision, not
unfinished work (`PL-TCD1`, 2026-09-13). Unlike the run's definition, a snapshot
is never stored, never compared with a later run and never read back, so giving
it a second substance later adds a field and invalidates nothing already
written. The roadmap's test for a change like this is "whether retrofitting a
feature invalidates recorded runs or merely adds a field"
(`ROADMAP.md` § "Designed for forking"). By that test, the roadmap left
per-compartment agent amounts out of the snapshot until their milestone
arrived. That milestone was the compartment schematic, and the snapshot now
carries each compartment's amount as one record keyed by compartment
(`compartment_agent_amounts`). The snapshot gains the
per-substance mapping with `ROADMAP.md` Phase 1, which generalizes the patient
to N simultaneously present substances. The snapshot carries the six fields
beside the identifier and display name of the agent they belong to
(`agent_id`, `agent_display_name`), as it carries the agent's MAC
(`agent_mac_percent`), and the age that MAC is stated for
(`agent_mac_age_years`), beside the concentrations that MAC scales. The controller
exposes immutable snapshots, and immutable windows onto the recorded run, rather
than mutable compartment objects.

A function sets the number of grid columns that the time axis is divided into
(`chart_columns` in `app/chart_frame.py`, `PL-GS3R`). The spacing is the time
base divided by one less than that number. It is rounded down onto whole seconds, and a spacing of less than 1 s
is raised to 1 s (`grid_spacing_s` in `app/chart_time_base.py`). Rounding down
is what keeps drawn instants no more than a pixel apart, wherever the axis
shows at least as many seconds as the plot has pixels. Each drawn instant is a
time that the clock also shows. A plot is redrawn when it
grows wider than the width its frame was sampled for (`resample_owed`,
`PL-9LNF`).
<!-- provenance: core/simulation_step.py SIMULATION_STEP_S = 1 -->

The two rules for where drawn instants fall are requirements of this document,
not optimisations. The grid sits at absolute multiples of the spacing, so a
window that follows the run keeps every drawn instant it had and gains at most
one, and a steady trace is not redrawn on every frame. A grid anchored to the
viewport would move on every scroll and resize, and rewrite the whole chart on
every frame. A grid anchored to each run's own start would put a branch forked
at 55 s on 55, 65, 75 … while the run it branched from draws 0, 10, 20 ….

Each control change is a drawn instant because the run has a kink there: the
derivative of the circuit fraction is discontinuous. Without a drawn instant
there, the interpolation error at that instant would scale as O(h), in
proportion to the spacing h between drawn instants, rather than as O(h²), in
proportion to its square. The state drawn at a control change is the one that
the run stored for that second, like every other drawn state.

The pixel in the one-pixel guarantee is a logical pixel of the plot, the
resolution at which the axis is ruled and labelled.

The one-pixel guarantee works in pixel columns, as Jugel, Jerzak, Hackenbroich
and Markl do for recorded data. They prove that a line chart is fixed by at most
four values per pixel column (M4: A Visualization-Oriented Time Series Data
Aggregation, *Proceedings of the VLDB Endowment* 2014;7(10):797-808). Their
method of selecting values from a store is not used on its own, because a selection of
recorded extremes could not guarantee that every control change is a drawn
instant whatever the pixel width (`PL-4RBD`). The chart reads the run's stored
state at each grid column and each control change instead. It then adds the
second of each compartment's highest and lowest stored value between two drawn
seconds, which are two of the four values that M4 keeps
(`extreme_seconds` in `app/chart_time_base.py`, `PL-BLZJ`).

The one-pixel guarantee (`PL-GS3R`, decided 2026-09-14) replaced a fixed budget
of 150 drawn instants at every width. That count stays as the minimum, because
no smaller count has been measured. Across the twelve-hour time base, the fixed
budget spaced drawn instants 290 s apart, and it drew the steep early wash-in
below the run. For sevoflurane 2% to 4% at the fastest supported settings
(FGF 10 L/min, V_A 12 L/min, Q 10 L/min), the line fell below the run by
0.53 pp on the alveolar trace (0.26 MAC) and 0.89 pp on the circuit trace. For
a desflurane overpressure induction, 0% to 12% then 6% at 600 s, it fell below
by 3.8 pp on the alveolar trace (0.64 MAC) and 5.5 pp on the circuit. Keeping
every trace within the readout's resolution everywhere would instead need a 2 s
spacing on the desflurane case: 21 601 drawn instants across twelve hours. No
hardware this project has measured can draw that many in the time one frame
allows. All of the fixed budget's error lies within 1 800 s of a dial change,
and beyond that the 290 s spacing itself is within 0.0024 pp. These values were
computed on 2026-09-14 against the model's exact solution every 0.1 s, over
five twelve-hour runs built by formula.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->

The five simulated runs for the gap at a peak or a trough were sevoflurane
2% to 4% and 4% to 0% at the fastest settings, the desflurane case at the
fastest settings and at slow settings (FGF 0.5 L/min, V_A 2 L/min, Q 2 L/min),
and the reference adult at 1 to 2 MAC. The run at the reference adult's flows
moved the desflurane dial-down one second at a time from 600 s to 642 s. Two
tests check that the chart draws a peak between two columns at its stored
value, and that each compartment's highest and lowest values between two
columns are drawn
(`test_a_peak_between_two_chart_columns_is_drawn_at_its_stored_value` and
`test_every_compartments_highest_and_lowest_value_in_each_column_is_drawn` in
`tests/integration/controller/test_controller_stored_states.py`). A third
checks that a trough of the F_A/F_I ratio between two columns is drawn at its
stored value
(`test_a_trough_of_the_ratio_between_two_chart_columns_is_drawn_at_its_stored_value`
in the same file). A preview
is drawn by the same rule, so its peaks and troughs are drawn too. With
sevoflurane at 2% for five minutes and the dial then turned off, a preview
draws the alveolar peak 2 s later, the vessel-rich peak 63 s later and the
venous peak 79 s later, each between two columns 30 s apart
(`test_a_preview_after_turning_the_dial_off_draws_each_peak_the_run_would_reach`
in `tests/unit/test_chart_frame.py`).

Bounding the gap at a peak or a trough by the readout's resolution is
deliberate. The bound is about the chart, in the units that the readout shows,
so it does not break the rule that the readout's number of decimals must not
feed back into the model (§ "Why the readouts show two decimals", note for
developers). That rule is why the step tolerance and the supported ranges are
stated in absolute percentage points. The two-decimal readout itself follows
from the model's fidelity, which § "Why the readouts show two decimals"
measures as the shift that one published SD of a partition coefficient causes
in a displayed compartment.

The code enforces a displayed ratio's domain in one place.

The steps that each tick takes are derived in `app/playback.py`
(`OwedSimulatedTime`), and a precise timer starts
each tick (`PreciseTimer`, `RunView.step_tick`). A count of more than 1 000
steps per tick is refused (`PL-T6P0`). A tick takes all of its steps before the
interface can respond, so a count with no bound would freeze the application
with no error. The bound is set by time: one step took about 53 microseconds
when measured on 2026-10-26, so 1 000 steps take about half of the 100 ms tick.
The fastest offered rate, 300×, takes 30 steps per tick. A test checks the grid
of instants that a change can reach at each rate
(`test_the_control_grid_at_each_rate_is_the_one_two_documents_publish` in `tests/unit/test_playback.py`).
<!-- provenance: app/playback.py MAXIMUM_STEPS_PER_TICK = 1000 -->
<!-- provenance: app/dashboard_frame.py SIMULATION_TICK_INTERVAL_MS = 100 -->

The 2026-09-27 measurement used the real dashboard on the offscreen platform,
with both timers running, and the tick period stayed at 100 ms to within 4 ms.
<!-- provenance: app/dashboard_frame.py SIMULATION_TICK_INTERVAL_MS = 100 -->

Showing only the set rate is a decision (project owner, 2026-09-27, ratified,
over qualifying the label as "up to 300×", which trades a precise claim that is
true for a vague one, and over building the disclosure now). A proposed change
would show the delivered rate beside the set one when fewer than 95% of ticks
run over a 50-tick window (`PL-2NYN`). If a delivered rate below 99% is
measured on the owner's own machine, the decision is reopened (`PL-SQJ1`).

## Minimum displayed outputs

The interface must show the following outputs. The names in brackets after each
entry are the tests that check whether the output is drawn on the display.

- simulated time (`test_refresh_view_formats_every_concentration_metric`,
  `test_the_clock_panel_reads_in_the_chart_axis_form_past_an_hour`);
- the playback rate that is set, as a multiple of real time. It is drawn
  wherever simulated time is drawn, and at every rate, including real time
  (`test_the_playback_rate_is_drawn_under_the_clock_it_governs`). A paused,
  reset or halted run still shows the rate it would play at. The status word in
  the row of playback controls says whether the clock is moving. See
  § "Interface boundary" for what the rate does and does not assert;
- how much simulated time the chart is showing, and whether that span was the
  reader's choice or fits the whole run so far
  (`test_the_axis_caption_states_the_span_the_chart_is_showing`,
  `test_the_caption_says_when_the_span_was_chosen_by_the_run_rather_than_the_reader`).
  See § "The chart's time base";
- run state, with running, paused, and halted-by-failure distinguishable from
  one another (`test_refresh_view_reflects_running_state`,
  `test_the_transport_is_enabled_by_state_in_all_four_states`);
- why a run halted, whenever one has
  (`test_refresh_view_reports_a_failed_run_as_stopped_not_paused`,
  `test_refresh_view_reports_the_supported_run_length_as_stopped_not_failed`);
- which agent is running
  (`test_the_readout_row_names_the_substance_its_numbers_belong_to`);
- the delivered concentration of that agent
  (`test_refresh_view_formats_every_concentration_metric`,
  `test_refresh_view_updates_delivered_concentration_label_for_current_agent`);
- circuit or inspired concentration
  (`test_refresh_view_formats_every_concentration_metric`,
  `test_the_alveolar_readout_is_labelled_end_tidal_equivalent`);
- alveolar or end-tidal-equivalent concentration
  (`test_the_alveolar_readout_is_labelled_end_tidal_equivalent`);
- mixed-venous concentration
  (`test_refresh_view_formats_every_concentration_metric`);
- vessel-rich concentration
  (`test_refresh_view_formats_every_concentration_metric`);
- muscle concentration
  (`test_refresh_view_formats_every_concentration_metric`);
- fat concentration (`test_refresh_view_formats_every_concentration_metric`,
  `test_a_real_run_displays_a_filling_compartment_as_below_resolution`);
- cumulative delivered amount
  (`test_the_accounting_panel_prints_amounts_at_one_decimal_of_a_litre`);
- cumulative exhausted amount
  (`test_the_accounting_panel_prints_amounts_at_one_decimal_of_a_litre`);
- total stored amount
  (`test_the_accounting_panel_prints_amounts_at_one_decimal_of_a_litre`);
- mass-balance residual or status
  (`test_refresh_view_reports_valid_agent_accounting`,
  `test_refresh_view_reports_failed_agent_accounting`);
- every concentration above, including the delivered concentration, also shown
  as a multiple of the running agent's 1 MAC, with that agent's 1 MAC in percent
  stated on the display (`test_every_compartment_is_readable_in_mac_multiples`,
  `test_the_dial_is_readable_in_the_unit_its_compartments_are`,
  `test_the_display_names_the_mac_the_readouts_were_divided_by`). See
  § "MAC multiples as a display unit" for what the multiple asserts and why both
  units are shown;
- the running agent's population MAC-awake, drawn on the chart as a band. The
  band was derived from two numbers. The band's legend entry gives the first,
  MAC-awake as a fraction of the agent's 1 MAC, with the percent that the
  fraction comes to and the band's two edges in percent. The 1 MAC line's
  legend entry, just before it, gives the second, that 1 MAC in percent. The
  band's legend entry also names the trace to read the band against. A
  visually distinct line on the chart
  marks the agent's nominal 1 MAC
  (`test_the_band_states_the_fraction_and_the_divisor_it_was_drawn_from`,
  `test_the_interface_says_which_trace_the_band_is_read_against`,
  `test_no_trace_dash_is_as_wide_as_the_one_mac_reference_line`). See
  § "MAC-awake as a chart reference" for what the band does and does not assert,
  and why no time-to-wake-up figure is displayed anywhere in the interface;
- every setting changed during the current run. The list gives each of the
  most recent adjustments with the simulated time at which it started, or the
  interval that it spans, and the control and its values before and after. It
  counts the earlier adjustments that it leaves out. The chart marks each
  adjustment at the time it started, and counts those that it could not mark.
  One adjustment can hold several changes of one control
  (`test_the_list_states_what_was_changed_and_to_what`,
  `test_a_recorded_change_is_marked_on_the_chart_at_its_own_time`). See
  § "The control-input timeline"; and
- $`F_A/F_I`$ over the run, on a dimensionless axis of its own. The plot is
  labelled as a ratio against the modelled inspired concentration, not against
  the vaporizer dial. It carries the marks for setting changes, has a line at
  the equilibrium that the curve approaches, and states where the ratio is not
  defined
  (`test_the_wash_in_axis_is_ruled_at_quarters_and_the_window_is_the_chart_s`,
  `test_the_wash_in_plot_says_what_its_denominator_is`,
  `test_the_wash_in_trace_draws_nothing_before_agent_reaches_the_circuit`). See
  § "F_A/F_I as a displayed ratio" for the part of the run over which the curve
  is drawn, and for what it does and does not assert.

The six compartment concentrations above are requirements on the **numeric
readouts**, not on the chart. The reader may show and hide the chart's
compartment traces (see § "Interface boundary"), but a required value must stay
on the display when its trace is hidden. The MAC-awake band, the 1 MAC line and
the marks for setting changes are requirements on a concentration chart that is
shown. The equilibrium line and the statement of where the ratio is not defined
are requirements on an $`F_A/F_I`$ plot that is shown. The reader cannot hide
any of them on a chart or plot, but can remove the chart or the plot itself
(§ "What this list requires once the layout is the reader's"). Of the chart
entries, only the span of
simulated time is the reader's choice, and no particular span is required.

Telling a halted run from a paused one is a required output. Both stop the
numbers advancing, and under `docs/VERIFICATION.md` § "Step atomicity" both leave the simulation in a
state that the reader can trust. A paused run continues when the reader asks,
but a halted run cannot. A halted run shown as "Paused" would offer a Start
control that fails at the first simulation step, and would present a stopped
trajectory as one still in progress. That is the mode confusion that this
document's interface rules exist to prevent. A display that merely freezes, with
no change of state at all, is worse still.

Showing which agent is running is also a required output. A correct
concentration attributed to the wrong agent is a display failure, and the same
number means a different clinical depth for each agent (§ "MAC multiples as a
display unit").

The alveolar readout is labelled "Alveolar", with "end-tidal-equivalent" on the
line below. It shows the concentration in the model's one well-mixed alveolar
compartment, which is the value a monitor's end-tidal reading estimates in a
real patient. The model has no dead space, airway sampling delay or shunt, so
this readout is not a simulated end-tidal measurement.

The circuit readout is labelled "Circuit", with "inspired" on the line below.
The model's circuit is one well-mixed volume with no separate inspiratory limb,
so the gas the patient breathes in is the circuit gas (`docs/MODEL.md`
§ "What the model represents"). The gloss names the circuit concentration as
the one a monitor's inspired reading estimates. Without it, "Circuit" can be
read as the vaporizer dial or the fresh gas. At a steady dial, while the patient
takes up agent, rebreathing holds the inspired concentration below both.

The fresh gas flow control is labelled "Fresh gas flow", with "common gas
outlet" on the line below. The flow it sets is the whole stream leaving the
common gas outlet, carrier gas plus vapour, which is up to 22% above the
flowmeter setting (`docs/MODEL.md` § "Breathing circuit"). "Fresh gas flow"
alone is the name on a real machine's flowmeter bank. None of these three
labels is shortened to its first line to fit a layout.
<!-- derived: 22 percent from data/agents/desflurane.json max_delivered_concentration_percent = 18 -->

Arterial concentration is **not** in the list above. In this model the arterial
fraction is defined as the alveolar one, $`F_a \equiv F_A`$ (see
`docs/MODEL.md` § "What the model represents"). A separate arterial readout would show the alveolar number
a second time under another name, as though the model computed an arterial
value of its own.

**No difference readout is required, and none may be added without a stated
sign convention.** The arithmetic difference of two alveolar fractions has no
conventional clinical reading, because clinicians reason about depth in MAC
multiples and time to target. Displaying it would imply a standard meaning that
it does not have, which § "Displayed precision" rules out on grounds of
interpretability. The chart already shows the comparison continuously, on the
axis the reader is looking at.

**For developers.** Testing the display matters because a required output can
stay in the simulation snapshot (`SimulationSnapshot`) long after the widget
that draws it has gone. Three entries have no field in the snapshot at all. The
playback rate and the chart's span are view settings, and $`F_A/F_I`$ is
computed when the plot is drawn.

The documentation check reads the list of required outputs (`docs/VERIFICATION.md` § "How this document is held to the tree"), and fails when an entry names nothing that backs
it, or names a test that does not exist.

The tests that the list names are in `tests/unit/test_dashboard_frame.py`, with
five exceptions.
`test_the_interface_says_which_trace_the_band_is_read_against` and
`test_the_wash_in_plot_says_what_its_denominator_is` are in
`tests/integration/simulation_view/test_simulation_view_whole_interface.py`.
`test_a_recorded_change_is_marked_on_the_chart_at_its_own_time` is in
`tests/integration/simulation_view/test_simulation_view_charts.py`.
`test_no_trace_dash_is_as_wide_as_the_one_mac_reference_line` is in
`tests/unit/test_chart_frame.py`, and
`test_the_wash_in_axis_is_ruled_at_quarters_and_the_window_is_the_chart_s` is in
`tests/integration/test_qt_chart.py`.

Most of those tests read the formatted value from the toolkit-free frame, not
from a drawn widget. `test_every_minimum_displayed_output_reads_its_value_from_its_widget`,
in `tests/integration/simulation_view/test_simulation_view_readouts.py`, closes
that gap for the unconditional part of the list. It walks the set that
`app/unconditional_set.py` declares, finds each value's widget through
`RunView.unconditional_widgets`, and checks that the widget is shown and reads
the run's value. For a compartment it reads the multiple of 1 MAC beside the
percent.

### Every value and what qualifies it come from one step

Where the screen shows a value with what qualifies it, both come from a single
simulation step. A test checks each of these groups:

- the readout cards, with their heading and 1 MAC line;
- the dials, with the delivered line;
- the accounting verdict, with the totals it judges.

A run stops when it fails or reaches the supported run length, the longest run
the model allows.

**If an agent change or a Reset starts a new run, and the new run stops before
the screen is redrawn**, the last values drawn belong to the discarded run. Each
card therefore withholds its percent and ×MAC number ("—%", "— ×MAC") under the
new run's heading and 1 MAC line. The clock reads "—", and the accounting panel
shows no verdict or amounts. Each chart shows an empty plot, with no trace, no
1 MAC line and no MAC-awake band, and a line above the plot says that nothing
is plotted because no frame could be drawn for that chart. The
legend's 1 MAC and MAC-awake entries read "—", and the axes lose their labels.
The banner says that the readouts and the charts are withheld.
Removing a value that no longer describes the run, and saying where it was,
follows FAA Advisory Circular 25-11B, *Electronic Flight Displays* (2014). Its
paragraph 4.6.4 asks that lost or erroneous information be removed from the
display or crossed out, so that it is not used, and its paragraph 6.2.1.7 puts
a failure flag where the information it replaces would be.

**If the runs the charts show change, and the runs stop before the screen is
redrawn**, the charts withhold their frame in the same way, because it was
drawn for other runs. A branch taken while frames fail does this, and so does
a Workspace that shows other runs, or a halt before any frame was drawn. So
does a halt while a dial is held, because the last frame shows the held
setting's preview, which the stopped run will refuse. A run that has not
started over keeps its readouts, and its banner says that the readouts show the
last frame drawn and that the charts are withheld.

After any other halt, each chart keeps the last frame it drew, which is the
frame that the readouts show, and the banner says that the readouts and every
chart that still has a plot show the last frame. A chart chosen during such a
halt draws that frame too. It is withheld instead when no frame was kept for
its window, or when the kept frame was sampled for a narrower plot, so that
its lines between drawn instants could be wider than a pixel.

**After a step fails its accounting check**, the accounting panel shows
"Validation failed" with that step's totals. If the screen is not redrawn after
the failure, the panel shows the same result from the run's record. The run
stops, and the model undoes the failed step, so the run's own accounting passes
again. The banner names the panel as the one exception to "the values shown are
the last completed step". It says in words that the check failed because the
rejected step created or lost agent, and that this is a fault in the simulator
and not a change in the patient. It does not print the totals. The panel shows
the rejected step's amounts, and the exact totals go to the details under the
banner and to the failure log, the file `failures.log` in the reader's data
directory, beside the saved Workspaces. Where that directory cannot be written,
the log goes to standard error only, and the application still opens.

**Every failure banner names the kind of failure in plain words**, and never
the error's own message, which is written for a developer. The kind is found
from the type of error that stopped the run, and each kind has its own words:

1. A failed accounting check: the words above.
2. A value the model cannot hold, such as a negative amount of agent.
3. A value that one part of the simulator gave another and that it does not
   accept. A setting the learner chose is refused before it is applied, so the
   learner's own dial never causes this kind.
4. A run that could not continue safely for another reason the model names.
5. Any other error. The banner says that an unexpected error occurred and that
   its cause is not known, rather than guess at one.

Each banner adds that this is a fault in the simulator and not a change in the
patient. Microsoft's guidance on error messages asks for a different message
for each cause that can be detected, and for an unknown cause to be stated as
unknown (Microsoft, "Error messages", Windows app development design
guidelines, learn.microsoft.com/en-us/windows/win32/uxguide/mess-error).

**A "Show details" button sits under every failure banner.** It shows these
lines:

1. The application's name and version.
2. The run's name, while two runs are drawn.
3. The type and message of the error that stopped the run.
4. The message of a Reset refused after that, if any. A run keeps its first
   failure, so this line is the only place on screen that names the refusal.
5. The path of the failure log, written from the home folder as `~`, because
   the full path usually holds the learner's login name.

A run stopped at the supported run length did not fail and has no details.
"Copy details" puts the lines on the clipboard, and a line under them links the
project's issue page and asks the reader to paste the details into a new issue.
The link is in the tab order and opens with Enter. The details fold away again
whenever a new failure replaces them, so one failure's details
are not read as the next one's. The same guidance hides detailed information
in an error message behind a "Show/Hide details" button, so that the message is
simpler for typical use.

**A dial moved on a stopped run is refused** before anything is applied, and
springs back to the run's setting. The model computes no step after a stop, so
the new setting would sit beside values it never produced, and the run's record
would claim a change that never acted on the patient. When a run fails on the
first step after a setting was accepted, none of the run's values was computed
under that setting either.

The banner states the refusal and the way out: Reset, which keeps every setting.
At the supported run length, a branch is a second way out: a new run from an
earlier instant, with each dial at its setting from that instant. The banner
names a branch only when one can be taken. It names Reset alone while no Area
shows the branch View, and while the run is compared with another, because
comparison locks the branch control.

**For developers.** For each scenario, a test requires every screen element in a
group to describe the step that the scenario names. It also requires every other
screen element to be listed with the reason it belongs to no group. On a
dashboard that holds no case to branch, the banner names Reset alone.

Every value on screen and its qualifiers come from one state
(`test_every_value_and_its_qualifiers_on_screen_come_from_one_state` in
`tests/integration/simulation_view/test_simulation_view_run_stops_itself.py`). A
Reset or an agent change that fails after it has cleared the run withholds every
value (`test_a_reset_that_raises_after_clearing_the_run_withholds_every_value`
and
`test_an_agent_change_that_raises_after_rebuilding_the_run_withholds_every_value`
in `tests/integration/test_failed_start_over.py`). A failed step leaves every
displayed value unchanged
(`test_a_failed_step_leaves_every_displayed_value_bit_identical`), and a stopped
run refuses every setting
(`test_a_stopped_run_refuses_every_setting_and_records_nothing`), both in
`tests/integration/controller/test_controller_running.py`. The banner after a
failed accounting check shows no e-notation and no code name, and the log keeps
the totals
(`test_an_accounting_halt_tells_the_learner_in_words_and_logs_the_totals`, in
the same file as the first test). The failure log is written to the data
directory (`test_a_failure_logged_by_a_run_reaches_the_file_in_the_data_directory`
in `tests/integration/test_failure_log.py`), and a directory that cannot be made
does not stop the launch
(`test_a_data_directory_that_cannot_be_made_keeps_no_file_and_lets_the_launch_go_on`,
in the same file).

Each kind of failure has its own words and no developer message
(`test_each_kind_of_failure_has_its_own_plain_words_and_no_developer_message`
in `tests/unit/test_failure_words.py`), and the details name the build, the
error and the log (`test_the_details_name_the_build_the_message_and_the_log`,
in the same file). A real failed step is worded for the learner and keeps its
message in the details
(`test_a_failed_step_is_worded_for_the_learner_and_its_message_kept_in_the_details`
in `tests/integration/simulation_view/test_simulation_view_failure_details.py`).
The same file tests the toggle, the copy button, the folding of new details,
each kind's words on a real halt, the refused Reset's line and the run's name.

### Naming the run in a comparison

While two or more runs are drawn, each of these places names its run in text:

1. The readout panels, which the runs share. Each value in a panel is under its
   run's name, and each run's row of controls opens with its name
   (§ "Minimum displayed outputs").
2. The chart's hover readout. With one run under the pointer, its name is on
   the readout's first line (§ "The hover and the run it belongs to"). With
   several, each value line gives its run's name. The readout reports every run
   inside the hover radius, so a small pointer movement cannot swap which run is
   read (§ "When more than one trace is within reach").
3. The three advisory lines inside a chart: the wash-in state, the off-scale
   notice, and the count of control changes the chart could not mark. They
   stack one line per run.
4. The headings of the two record panels: the agent-accounting validation, in
   each area that shows the accounting view, and the control-change record
   ("What was changed during this run") in the right column of the always-shown
   region of the window. Each
   record stacks one whole panel per run, so a run's name is in its panel's
   heading and moves with that panel.
5. The notice banner, between the runs' control rows and their readouts. Both
   runs use this one place, and an empty banner is hidden and takes no room. A
   banner's position therefore does not show which run it belongs to.
6. The heading over each run's compartment schematic, taken from the name on
   the run's own panel.
7. The heading over each run's agent cost panel, in the same way.
8. The line above each run's row of dials in the setting controls view, in the
   same way (`PL-CPF2`).

With only one run drawn, the hover readout, the chart's advisory lines, the
two record panels' headings and the banner show no run name.

Without the run names, a learner could misread a comparison in three ways:

- One run's F_A/F_I could be read as the other's, or its off-scale notice could
  be attributed to a run whose traces are all inside the axis.
- If read as the other run's, the control-change record says that run received
  an intervention it never got.
- If read as covering the whole dashboard, a halt banner says both runs are
  frozen. "The values shown are the last completed step" then claims both runs
  stopped at a failed step when one is still going. "The simulation is
  unchanged and still running its previous setting" is false of the run that
  accepted the setting.

**The run is named in text, not by colour or position.** Colour already
identifies the compartment in both modes, so it cannot also identify the run.
The worst contrast between two compartment traces is 1.05:1, against the 3:1
required (§ "The six compartment traces"). The chart therefore shows the run by
line width instead (`PL-HLD5`), but text has no equivalent of line width.
Position alone fails a reader who looks away and back, and naming the run exists
to protect that reader.

**A run's name gives its identity, not its place** (`PL-7Z84`). Each run placed
in a session gets a number, counting from 1, and its name is "Run" followed by
that number. A run keeps its number for as long as it holds its place on screen.
Branches fork from a run called the trunk, which holds its place from when the
dashboard opens. A branch holds its place from its fork until it is dropped.
Resetting a run and changing its agent both keep the number, because each starts
the run afresh in the same place. The restart comes after any confirmation the
reader is asked for (§ "Discarding a run, and the questions that guard it").
No number is given out twice in a session, so a branch taken after a dropped one
is "Run 3", never a second "Run 2". A Workspace can be pinned to a run, so that
it shows that run. If a name were reused, a Workspace pinned to the dropped run
would find a new run of that name and show its values as the dropped run's.

**A Workspace pins a run by its identity, and says when that run is absent**
(`PL-WV9K` Q6). The pin is saved with the Workspace as two values: the run's
number, and a random code for the session that placed the run. A run with the
same number in a later session is therefore a different run. When the pinned
run is not open, each of the Workspace's areas that show a run's values says
so in place of its view ("Run 2 is not open."), with the run's name in the
area's header. The areas never show another run in its place, and the
simulation is left untouched. The Bookmarks View and the Branch View show the
case rather than one run, so they still show the case's marks and the branch
control, and their headers name no run
(`test_a_workspace_pinned_to_a_run_that_is_not_open_still_shows_the_case_s_marks_and_branch` in
`tests/integration/test_workspace_tabs.py`, `PL-1D3Z`).
Where an earlier session placed the pinned run, the areas and the menu of the
Workspace's tab call it "a run from an earlier session" and give no number,
because a run that is open now can carry the same number
(`test_a_pinned_run_that_is_not_open_is_stated_in_every_area_of_the_runs` in `tests/integration/test_workspace_tabs.py`).
The reader sets and removes a pin from the menu of the Workspace's tab
(`PL-2KXB`).

**A branch taken in a pinned Workspace says where the comparison is**
(`PL-YQ5J`). A pinned Workspace draws one run at most, so a branch taken from
its Branch View opens in none of its areas. The caption that replaces the
branch control while two runs are open then adds a sentence naming the pin and
the way to compare the runs ("This Workspace is pinned to Run 1, so it does not
draw this comparison. Unpin it from the Workspace's tab to compare Run 1 and
Run 2."). The learner stays in the Workspace they chose. The sentence goes as
soon as the Workspace is unpinned or the reader switches to another Workspace.
The interface does not switch the Workspace itself, because the press asked
for a branch and not for another Workspace. WCAG 2.2 Success Criterion 4.1.3
treats a result shown without moving the reader as a status message. Nothing
announces this one to a screen reader yet, because screen-reader support is
planned and not yet a commitment (§ "Color contrast, and the standard this
interface is held to"). The Understanding document for Success Criterion 3.2.2 holds a change of context
appropriate "only when it is clear that such a change will happen in response
to the user's action"
(`test_a_branch_taken_in_a_workspace_pinned_to_a_run_that_is_not_open_says_where_it_went`
and `test_a_branch_taken_in_a_workspace_pinned_to_the_trunk_says_so_until_it_is_unpinned`
in `tests/integration/test_workspace_tabs.py`).

**A pinned Workspace says so before a branch is taken, too** (`PL-RXR8`). A
branch cannot be undone short of the trunk's Reset, which starts the case over,
so the learner is told before pressing rather than only after. While one run is
open and a branch is offered, the Branch View says above its control that the
Workspace will not draw a branch taken there ("This Workspace is pinned to Run
1, so it will not draw a branch taken here beside it. Unpin it from the
Workspace's tab to compare the two runs here."). Both buttons stay offered. The
sentence reads the pin where the caption after a branch reads it, so the two
name the same run
(`test_a_pinned_workspace_says_before_a_branch_that_it_will_not_draw_it` and
`test_a_workspace_pinned_to_a_run_that_is_not_open_says_so_before_a_branch` in
`tests/integration/test_workspace_tabs.py`).

A view shows its run's name whenever a reader could mistake its values for
another run's: while another run is drawn anywhere in the application, while the
view is pinned to a run, and always in a window broken out of the main one.
Break-out windows are not built yet, so the dashboard is the only window that
draws a run. In this version, therefore, the names appear when two runs are
compared, and a pinned Workspace shows its run's name in the header of every
area that shows a run's values (`PL-2KXB`). The header of the Bookmarks View and
of the Branch View never names a run, because both show the whole case
(`test_a_case_view_s_header_never_names_the_open_run_a_workspace_is_pinned_to` in
`tests/integration/test_workspace_tabs.py`, `PL-1D3Z`).

**For developers.** Colour cannot name the run for a second reason: the hover
readout is separate from the legend. Drawing order cannot name it either,
because nothing shows which run is drawn on top. The run names sit in the
always-shown region above the charts.

A run's identity is defined in `src/anesthesia_sim/layout/run_identity.py`, and
one function renders a run's name everywhere it appears
(`dashboard_frame.run_label`). A Workspace's views show the runs that a method
returns (`Workspace.shown_runs`). An earlier rule showed run names only when more
than one run was on the dashboard. That rule fails for a run shown alone in a
pinned area or in a window of its own (`PL-2KXB`).

### The statement that the readouts are model outputs

The heading row of the readout section shows **"Model outputs — not
measurements."** beside "Modelled concentrations:" and the agent's name. The
chart's hover text labels every value as modelled. No monitor displays the
compartments that this simulator exists to show, so a user cannot check these
readouts against a measured value. A polished display makes them easy to
mistake for measurements.

**For developers.** The statement is required by the hazard row for reading a
modelled compartment value as a measured one. It sits beside the values it
qualifies, as the timeline's "Settings only — not a measurement." does for
control marks. The statement is not on the chart because people stop reading a
repeated disclaimer.

The statement is checked by
`test_the_interface_says_the_readouts_are_model_outputs_not_measurements` in
`tests/unit/test_dashboard_frame.py` and by
`test_the_readouts_say_they_are_model_outputs_beside_the_values` in
`tests/integration/simulation_view/test_simulation_view_readouts.py`.

### What this list requires once the layout is the reader's

Since v0.6.0, the reader can add, resize and remove the interface's areas, the
parts of the window that each show one view, such as a chart (`ROADMAP.md`
planned-milestone item 34). This list was written for one fixed layout. It now
divides its values into three parts, by what a reader could misread without
them. Unconditional values stay on screen in every layout. From any layout, the
reader can bring on screen the agent accounting, which tracks how much agent the
model has delivered, exhausted and stored. Conditional values appear only with
the chart they belong to.

The division stops a rearranged layout from breaking this list unnoticed.
Hiding a compartment trace is safe because its value stays in the numeric
readouts. A layout that could remove the readouts would make every show/hide
control that this document permits unsafe at once, while the chart still
behaved exactly as documented.

#### The unconditional values

**A value is unconditional when a reader could misread the run's other
displayed numbers without it.** Nothing may cover such a value. The set is
defined by this criterion, not by a fixed list, and the criterion gives two
tiers.

**The invariant tier of unconditional values is the same whatever is
simulated.** It consists of simulated time, the rate at which it is advancing,
the run state, why the run halted (when it has), and what is being administered.
A concentration shown with no time, no run state and no named drug is the
correct number under the wrong patient, which is a display failure.

**The per-substance tier of unconditional values depends on what the run
models** (project owner, 2026-09-16). For the inhaled-agent model that this
document specifies, the criterion selects the delivered concentration and the
six compartment concentrations, each in both units, with the agent's 1 MAC in
percent. A run that gives no volatile agent need not show them, because it has
no vaporizer dial, circuit concentration or MAC multiple to misread. That
applies to a run of the planned intravenous models (`ROADMAP.md`
planned-milestone item 13) or of any later substance. The same criterion selects
such a run's own values, which are named where its substance's model is
specified.

**The control-input record is unconditional, and its chart marks are
conditional.** The record holds every change to a setting during the run, with
the simulated time it took effect, the control it changed and the values it
moved between. The region lists the most recent adjustments, up to a fixed
number of lines, and states how many earlier ones it leaves out
(§ "The control-input timeline"). The record gives the facts, and the marks
place them against the curve.

#### Where the unconditional values sit on screen

**The unconditional values sit outside the areas.** Each run's unconditional
values are in one band across the top of the dashboard, the unconditional
region. The setting controls are a view that an area holds like any other view,
so a Workspace can leave them out (`PL-2KXB`). The region is not affected by a
change to the areas or a switch of Workspace (a saved layout, chosen by its
tab), so no saved layout has to be checked against this list. The dashboard
will not place a run whose region lacks a required value (`PL-NWTM`, laid out
to `PL-J8K2`).

**The educational-use disclaimer is a line across the foot of the window,
outside the layout** (`PL-JSY5`, `PL-J8K2` Q1). Like the unconditional region,
it is unaffected by any change to the areas, so it is present in every Workspace
a reader builds. Once a run can be shown in a separate window, each window will
carry the line in its own frame, beside its invariant tier. A window read alone
needs the statement of what the tool is for as much as it needs the run's time
and agent.

**The disclaimer line and the unconditional region are always in view**
(`PL-NNML`). The line sits below the part of the dashboard that scrolls, and
the region sits above it. Only the Workspace tabs and the areas scroll between
them. The interpretation statement on the region's
readout heading row stays in view with the line and the region, at any window
height and through any scrolling. This is what "always" means in the paragraphs
on the alert colour in § "Color contrast, and the standard this interface is
held to".

#### Values that must stay reachable

**The agent accounting must stay reachable, though not always visible.** It
consists of cumulative agent delivered, cumulative agent exhausted, total agent
stored, and the mass-balance residual. These four
amounts show whether the model is conserving mass, and a reader does not
titrate against them. A Workspace may leave the amounts out, because their
absence makes no clinical reading wrong, but nothing may remove them from the
application.

**"Reachable" means the reader can bring a view on screen through the interface
alone** (`PL-50PZ`). They must be able to do it from the Workspace they are in,
in a bounded number of steps, without dragging anything or editing a file.
Every area's header has a view chooser, whose menu lists every kind of view the
application has, whatever the Workspace. Choosing a view shows it in that area.
The exception is a Workspace pinned to a run that is not open. Each of its
areas that shows a run's values then says that the run is not open, in place of
its view, until the reader removes the pin from the menu of the Workspace's tab.
The Bookmarks View and the Branch View are still shown there.
A view that needs more room than its area scrolls inside the area. Three views
never scroll: the concentration chart, the Parameters view and the Branch view.
Their areas grow to hold all of the view, so the chart's plot, a run's dials or
the branch control's caption cannot sit out of sight below the area's edge
(`PL-D5J4`). The page
grows past the window only where the window is too small for every view's least
height or least width. So the reader sees the view itself, never only a notice
that the area is
too small (`PL-K285`, `PL-CBYS`). The
application will not start if the accounting view is missing from the chooser's
menu. Every layout has at least one area, so a chooser always offers the
accounting view. None of the Workspaces supplied with the simulator includes the
accounting view, so the chooser is how a reader reaches it.

#### Values required only with their chart

**Conditional values are required only on a chart or plot that is shown.** A
concentration chart shows the MAC-awake band, the 1 MAC line and the marks of
control changes. It also states how much simulated time it shows, and whether
that span was chosen or fits the run. An $`F_A/F_I`$ plot shows its equilibrium
line and states where the ratio is not defined. These references exist so that a
trace is never read without its clinical anchor. Where no trace is drawn there
is nothing to anchor, so leaving the chart out loses nothing.

#### No required value may be covered

**No value this list requires may be covered while the application treats it
as shown.** This occlusion rule applies to a panel drawn over the dashboard, a
separate window dragged over another window's invariant tier or over the main
window's per-substance readouts, and any floating element added later. It is a
property of the display, so it is the same for every kind of window.

**The occlusion rule applies only to the application's own windows and panels**
(2026-09-16). The application creates and places these, and can check their
state. A window of another program or of the operating system can still cover a
value, and no application can prevent that. The application can tell when one of
its windows is minimized or hidden, but it has no reliable signal that a window
is covered. It must never go on treating a value as shown once it can see that
the value's window is minimized or hidden.

**The marks are edited in a view, not in a window of their own** (project
owner, 2026-11-21, ratified, over a window kept off the readouts, an exemption
from this rule, and an editor during which every run waits). A learner edits
marks while a run plays. The Bookmarks View sits in an area, and the
unconditional region is outside every area, so editing a mark cannot cover a
value this list requires on any platform. A separate window could cover the readouts, and on Linux the
application cannot reliably keep it off them. Under Wayland's usual desktop
shell, Qt ignores a request to place a top-level window and reports every
window's position as (0, 0), so the application could neither place the
window nor learn where the reader had moved it (Qt 6.12 documentation,
"Window and Dialog Widgets", section "Wayland Peculiarities",
https://doc.qt.io/qt-6/application-windows.html).

#### What a separate window shows

**A separate window shows the invariant tier, not the whole set**
(project owner, 2026-09-16, ratified - a recommendation put to them and agreed,
chosen over the two live readings `PL-W54S` had written, and reopenable on
ordinary evidence per `CLAUDE.md`; the occlusion rule (§ "No required value may be covered") is not, being the
safety requirement rather than the arrangement). Breaking an area out into a
window of its own is the second half of `ROADMAP.md` planned-milestone item 34,
and it is wanted but not yet scheduled (project owner, 2026-09-26). Such a
window is a full window, with areas of its own. The two tiers are unconditional
for different reasons, so each goes where its reason applies:

- **Every window of the application carries the invariant tier and the name of
  the run it shows**, in a region outside that window's areas. Any view that
  shows a concentration needs its time, run state and drug, so the tier goes
  with the concentration into whatever window shows it. Five values and a name
  fit, without squeezing, in a window that holds one chart.
- **The per-substance tier appears once, in the main window**, and must be in
  view whenever any window of the application is open. Closing the main window
  closes the others, so no other window is left open without it. That rule does
  not by itself keep the tier in view: a minimized main window, or a break-out
  window placed over it, still hides the tier. The break-out design must also
  cover those cases. The closing rule is a placeholder until break-out windows
  are built (`PL-DPY1`). A reader could misread the run's other displayed numbers without this
  tier, so it concerns the display as a whole rather than any one view.
- **The agent accounting is unchanged**, because its requirement already applies
  to the application rather than to any layout or window.

**The invariant tier guards against a documented failure: correct data read in
the wrong context.** This is an established class of clinical-information-system
error. Ash, Berg and Coiera describe the "silent errors" that such systems
foster rather than prevent (*J Am Med Inform Assoc* 2004;11(2):104-112,
doi:10.1197/jamia.M1471). Magrabi and colleagues classified 42,616 reported
incidents, and their classification makes information *output* a category of
its own, at 20% of computer-related problems (*J Am Med Inform Assoc*
2010;17(6):663-670, doi:10.1136/jamia.2009.002444). The closest measured
analogue is the wrong-patient order. Restoring one piece of patient context, a
photograph, to the display banner was associated with fewer wrong-patient
orders across 2,558,746 orders (adjusted OR 0.57, 95% CI 0.52-0.61; Salmasian
et al., *JAMA Netw Open* 2020;3(11):e2019652,
doi:10.1001/jamanetworkopen.2020.19652). That is the invariant tier's argument
in another clinical setting: context carried in the frame of the view, not
assumed from elsewhere on the screen.

#### When two runs are shown

**While two runs are shown, every readout names its run, and all six
compartments keep their readouts for both runs** (`PL-1XPX`). A required value
must not leave the display with the curve that draws it. That applies to the
chart's limit of two compartments in compare mode (`ROADMAP.md` v0.5.0,
`PL-HLD5`) just as it does when a reader hides a trace. The limit comes from how
many colours the chart can use, and it does not reduce what the display must
show.

**Both runs' values are shown, not only the selected run's.** Showing only the
selected run would make the readout block a mode. The block would look the same
whichever run was selected, so a stale selection would have no visual sign. A
reader who had forgotten the selection would take one management's number for
the other's. Stating the selection would only warn after the fact, whereas
showing both runs prevents the error.

Each compartment's panel holds both runs' values. The second run's value and its
second unit sit under the first run's, and each value has its run's name on the
line above it. The block therefore stays one row of seven panels and grows only
by those name lines (`PL-F2YS`). The single row keeps the comparison for which
this document requires uniform resolution: a reader sees the circuit lead the
alveoli, and the alveoli lead the tissues. Each readout panel reserves the width
of the widest value it can show, so a value is never wrapped away from its unit
at any width at which the row is laid out (`PL-3355`).

Each run's delivered concentration sits on that run's own line, beside its name
and its controls, such as Start. The values the two runs share appear once, on
the heading line above the block: the substance, the agent's 1 MAC, and the
version and model. They are the same for both runs because a second run must use
the first run's agent, and a branch's MAC is checked against its trunk's when
the branch is opened (`PL-QLZ5`).

#### The code and tests behind the layout requirements

**For developers.** The unconditional tiers and the control-input record are
stated as data in `app/unconditional_set.py`, with the inhaled-agent tier as
`INHALED_AGENT`. The educational-use disclaimer is a standing statement
(`USE_DISCLAIMER_TEXT`) rather than one of this list's values, so that file
does not declare it. The interpretation statement is
`INTERPRETATION_DISCLAIMER_TEXT`.

The marks editor is `MarkEditor`, in `app/qt_widgets.py`, and each copy of the
Bookmarks View holds one. A test adds and removes marks with a run playing and
checks that no window opens
(`test_editing_a_mark_while_a_run_plays_opens_no_window`, in
`tests/integration/simulation_view/test_simulation_view_comparison.py`).

The division of this list into three parts is a first version (project owner,
2026-09-15). The fixed unconditional region and the conditional remainder were
chosen to be correct while the tools for arranging the layout are built, and the
division is expected to change as those tools mature. Any change must keep the
occlusion rule, because that rule is the safety requirement and the division is
only the arrangement.

A code change that moves a required value into an area fails at once, because
the dashboard then refuses to place the run. Otherwise the reader could close
the value along with its area. Checking each saved Workspace and rejecting the
ones that fail is the fallback for anything that cannot sit outside the areas.
It is the weaker guarantee, because a check warns after the fact, while the
structure prevents the failure.

Blender is the model for the region's structure, a region outside the areas,
and not for its persistence. Blender's Topbar and Status Bar sit outside its
areas as this region does. Focus Mode hides both, together with the editor's
secondary regions, for maximum screen space (View -> Area -> Focus Mode,
Ctrl-Alt-Spacebar; Blender Manual, "Interface -> Window System -> Areas", read
at the source 2026-09-16). That is the right trade for a 3D application and the
wrong one here. Blender has no value whose absence is a safety failure, and
this application does. Take the structure, and leave out any way to hide the
region, such as Focus Mode. Say so wherever a reader would otherwise assume
that the whole precedent was copied.

A test checks that the unconditional region and the disclaimer line stay in view
in windows 700, 900 and 1100 px tall, in each supplied Workspace
(`test_the_region_and_the_use_disclaimer_stay_in_the_viewport` in `tests/integration/simulation_view/test_simulation_view_two_runs.py`). The region and
the line must also stay in view through the scroll to the concentration chart
that happens when a branch is taken (`PL-562Z`). Another test checks that the
dashboard shows the line
(`test_the_dashboard_carries_the_educational_disclaimer` in `tests/integration/simulation_view/test_simulation_view_two_runs.py`).

The view chooser is built in `app/area_layout.py`. The view registry marks the
accounting view as required to be reachable (`required_reachable`, in
`app/view_registry.py`), and a build that does not register that view fails
when the module is imported. Each area that shows the accounting view builds a
copy of its own, so two such areas both show the four amounts (`PL-TH35`). A
test checks the chooser's route to the accounting view from every area of each
Workspace supplied with the simulator
(`tests/integration/test_view_chooser.py`).

The toolkit can report less about a covered window than first appears (measured
on PySide6 6.11.2 / Qt 6.11.2, 2026-09-16). A widget's visibility flag
(`QWidget.isVisible()`) is documented to stay true for a widget "obscured by
other windows on the screen", so it reports the application's own show/hide
bookkeeping and never occlusion. A window's visibility state
(`QWindow.visibility()`) says which of Hidden, Windowed, Minimized, Maximized or
FullScreen the window is in, so it catches a minimized or hidden window and
nothing else. The one signal close to occlusion (`QWindow.isExposed()`) is
documented only as something that *might* change when a window is "made totally
obscured by another window", and the platform plugins disagree about it. The
macOS plugin drives it from `NSWindow.occlusionState`, while the Windows plugin
deliberately keeps it true under occlusion for compatibility. No safety rule may
rest on that signal, which is why the occlusion rule relies only on what the
application can see.

The region built in v0.6.0 must already have the right shape for separate
windows, because its protection from changes to the areas stops at the frame of
its own window.

Two other readings of what a separate window must show were refused, and should
not be proposed again. Giving every window the whole unconditional region fails
because a broken-out window is typically small, such as one chart on a second
screen. Seven concentrations in two units would either dominate it, which
defeats breaking it out, or be squeezed, which
§ "Diverged, and each divergence has a specific cause" of
`docs/interface-provenance.md` rules out. Giving the main window everything, and
a broken-out window only its run's name, leaves a window drawing compartment
traces with no time, no rate, no run state and no agent. That reading also rests
the guarantee on a window that the reader may not be able to see. In a third
reading, the requirement applies to the application rather than to each window.
It was ruled out on the same ground (`PL-WLWY`), because it too rests the
guarantee on where the window manager has put things.

The evidence checked does not name duplicating a live readout across windows
as a hazard in itself. The one randomised trial of concurrently open records
found no difference in wrong-patient errors (Adelman et al., *JAMA*
2019;321(18):1780-1787, doi:10.1001/jama.2019.3698). Nor does the evidence show
a published preference for non-overlapping areas over overlapping windows, and
the only controlled comparison does not support one. The case for
non-overlapping areas rests on this project's own reasoning about covered
values, as `ROADMAP.md` planned-milestone item 34 records.

Stacking the two runs' values leaves each panel at its one-run width, so the row
stays seven panels across at 1366 px. Placed side by side, the values would make
each panel roughly twice as wide (`PL-F2YS`).

### MAC multiples as a display unit

Every compartment is shown in two units at once: a percent of one atmosphere,
and a multiple of 1 MAC of the agent in use. Both units appear on the readouts,
on the delivered-agent control and on the chart. The chart has a percent axis
on the left, titled `% of 1 atm`, and a MAC axis on the right, titled `×MAC`. It
plots each trace once, in percent, and the MAC axis relabels that scale, so the
two axes always agree about where a trace is.

The percent unit is `% of 1 atm`, not `vol %`, because `vol %` is a gas-phase
volume fraction and only the circuit and alveolar compartments have one. The
mixed-venous, vessel-rich, muscle and fat compartments hold a partial pressure,
which convention quotes as a percent of one atmosphere.

The MAC multiple of a concentration is its percent divided by 1 MAC of the
agent that produced it:

$$
\text{MAC multiple} = \frac{100F}{\mathrm{MAC}_\%}
$$

The MAC multiple is a unit of the interface, not of the model. The display
shows it, and a MAC target is set in it (§ "Halting on a marked crossing"). The
model neither stores a compartment's MAC multiple nor computes one.

**MAC multiples keep their meaning when the agent changes, and clinicians reason
in them.** A percent changes meaning with the agent: 1.8% is 1 MAC of sevoflurane
and about a quarter of a MAC of desflurane. A desflurane wash-in and a sevoflurane
wash-in drawn at the same height in percent therefore show two different
clinical situations.
<!-- provenance: data/agents/sevoflurane.json mac_at_age_40_percent = 1.8 -->
<!-- derived: a quarter of a MAC of desflurane from data/agents/desflurane.json mac_at_age_40_percent = 6.6 -->

#### What a MAC multiple means

**What a MAC multiple means depends on the compartment.** MAC is defined for the
*alveolar* (end-tidal) concentration at one atmosphere in a nominal
40-year-old. It is the population ED50 for immobility in response to a
standardized surgical stimulus. So:

- On the **alveolar** compartment, a MAC multiple has its conventional
  meaning, subject to the limitations listed below.
- On the **circuit, mixed-venous, vessel-rich, muscle and fat** compartments,
  it means only *this compartment's partial pressure equals N times the
  alveolar partial pressure that would be 1 MAC*. It is a ratio of partial
  pressures, **not** a statement that the patient is at N MAC of anesthetic
  depth.

Three limitations apply to every compartment, including the alveolar one:

1. MAC falls about 6% per decade of age (Mapleson 1996). The model's
   reference adult has no age parameter, so every run divides by the MAC at
   age 40.
2. The MAC multiples of co-administered agents are additive, and the model runs
   one agent at a time.
3. Opioids, temperature and patient factors modify MAC, and the model
   represents none of them.

**The MAC multiple is written `×MAC`, not `MAC`.** A clinician reads "0.80 MAC"
as a depth of anesthesia, and "0.80 ×MAC" as a multiple of 1 MAC, which is what
the number is. Every readout carries the multiplication sign, and so does the
MAC axis title. The axis ticks show bare numbers, such as `0.5` and `1.0`, so
only the title says what they are. That title labels six traces at once, and
five of them are not the alveolar compartment. No text on the display explains
the difference between a ratio and a depth, so the sign is the only thing that
marks it.

**The agent's 1 MAC is shown beside the chart with the age it is stated
for**, for example as "1 MAC sevoflurane (age 40) = 1.8%". A reader can
compare this 1 MAC with the value they use for their own patient, and can
convert a MAC multiple back to the percent that the model computes. The 1 MAC
is also the vaporizer's starting position. In each agent's data file, the
authority for the stored 1 MAC is Mapleson's 1996 meta-analysis, which gives
each agent's MAC at age 40. `docs/PARAMETERS.md` § \"Delivery-limit and MAC
parameters" gives the source of each agent's 1 MAC and its confidence limits.
<!-- provenance: data/agents/sevoflurane.json mac_at_age_40_percent = 1.8 -->

**The 1 MAC prints with at most two decimals and no trailing zero**: 1.8%
sevoflurane, 1.17% isoflurane and 6.6% desflurane. Two decimals show
isoflurane's 1.17% in full. A trailing zero would claim a digit that the MAC's
uncertainty does not support, because Mapleson's 95% limits are about ±7% of
the MAC (±10% for desflurane). The GUM rounds an estimate to be consistent with
its uncertainty (JCGM 100:2008, *Evaluation of measurement data: Guide to the
expression of uncertainty in measurement*, § 7.2.6). The Joint Commission's
"Do Not Use" list allows a trailing zero only where it shows the precision of
the value reported. The line then reads as the 1 MAC gridline's axis label
does. The dial and the percent readouts keep two decimals, because they show a
setting and a computed concentration at the dial's step.
<!-- provenance: data/agents/sevoflurane.json mac_at_age_40_percent = 1.8 -->
<!-- provenance: data/agents/isoflurane.json mac_at_age_40_percent = 1.17 -->
<!-- provenance: data/agents/desflurane.json mac_at_age_40_percent = 6.6 -->

**For developers.** The display code converts percent to MAC multiples in
`app/formatting.py`, outside the model's code in `core/`. It takes the agent's
1 MAC as an argument. Each snapshot of the simulation's state carries that 1 MAC
beside the concentrations it scales and the agent it belongs to
(`SimulationSnapshot.agent_mac_percent`), with the age it is stated for
(`SimulationSnapshot.agent_mac_age_years`). Both come from one `PatientMac`,
which `mac_for_patient()` in `core/mac.py` builds from the agent and the
patient. The display code therefore cannot pair
one agent's concentrations with another agent's 1 MAC.

Both units are shown because a unit selector would make the axis unit a mode,
and a chart read under the wrong assumed unit is a misreading that no
disclaimer catches. The agent's 1 MAC is shown because the project's rules
(`CLAUDE.md`) require a clinically meaningful displayed value to be traceable to
the transformation that produced it. The display carries no text explaining MAC
because its reader, an anesthesia provider, knows what MAC is defined against,
and a dozen lines of text between the reader and the plot cost more than they
gave (`PL-6580`).

The stored 1 MAC (`mac_at_age_40_percent`) is a tier-2 value under
`docs/PARAMETERS.md` § \"Source hierarchy: what may be cited as the authority for a value".
Its adopted source in each agent's data file is Mapleson 1996, which is also
the source for the fall in MAC with age.

The multiple carries the multiplication sign
(`test_format_mac_multiple_carries_the_multiplication_sign` in
`tests/unit/test_formatting.py`), every compartment can be read in MAC multiples
(`test_every_compartment_is_readable_in_mac_multiples` in
`tests/unit/test_dashboard_frame.py`), and the 1 MAC value stays on screen
(`test_the_1_mac_value_stays_on_screen_where_the_rows_above_the_plot_scroll` in
`tests/integration/simulation_view/test_simulation_view_page.py`). The MAC axis
and the references follow the agent
(`test_the_mac_axis_and_references_follow_the_agent` in
`tests/integration/simulation_view/test_simulation_view_charts.py`).

#### The chart's fixed MAC axis

**The chart's vertical range is set in MAC, and fixed until the reader changes
it.** For every agent, the axis runs from 0 to a top that the reader chooses
from three: **1.5, 3 or 4.5 ×MAC** of the agent in use. The chart opens at
3 ×MAC. A given MAC multiple is therefore drawn at the same height under any
agent. The "Axis top" control sits beside the time base, under the chart's
heading, and names the top in force in words. The axis never grows or shrinks to fit a trace. The top stays where the
reader put it across runs and across both runs of a comparison, so runs drawn
one after another are comparable too. Each chart View keeps its own top and
saves it with its layout.
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

**Every gridline stands at a MAC multiple that the right axis labels.** The
right axis is labelled every half MAC at a top of 3 or 4.5 ×MAC, and every
quarter MAC at 1.5 ×MAC, so it never has more than ten intervals.

**The left axis is labelled at round percentages, each at its own tick mark.**
A MAC multiple is rarely a round percentage. At isoflurane's MAC of 1.17%, half
a MAC is 0.585%, so labels at the gridlines would read 0.585, 1.755 and 2.925,
with three decimals where the readouts show two, and no mark at 1% or 2%. So
the left axis takes its own steps, of 1, 2 or 5 times a power of ten, and never
more labels than the right axis has. At 3 ×MAC isoflurane is labelled 0, 1, 2
and 3%, sevoflurane 0 to 5%, and desflurane 0, 5, 10 and 15%. The gridlines
stay on the MAC multiples, so a percent label and a gridline near it can be
different values: desflurane's 1.5 ×MAC gridline is 9.9%, beside the 10%
label.
<!-- provenance: data/agents/isoflurane.json mac_at_age_40_percent = 1.17 -->
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->
<!-- not-restated: 5 % -->

**The chart names each compartment whose trace is above the top of the axis.**
Such a trace is cut off at the top of the frame, where it runs flat as a
plateau would. Without the name, a reader would conclude that the
concentration stopped rising at the top, when in the model it did not. The
chart names the top in percent and in MAC, the two units its axes are
labelled in, and says that the readouts are not cut off and keep showing their
values. Inhalational induction commonly uses sevoflurane's 8% dial setting,
which is 4.44 ×MAC, above the standard top. At the 4.5 ×MAC top, no agent's
vaporizer can take a trace off the plot at the MAC for age 40. At a lower MAC,
such as an older patient's, the off-scale notice can still appear at that top.
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->
<!-- derived: 4.44 from data/agents/sevoflurane.json max_delivered_concentration_percent = 8, mac_at_age_40_percent = 1.8 -->

**The chart's percent axis is linear, which crowds the slow compartments
together** (project owner, 2026-09-23, ratified, over a reader-selected logarithmic scale,
`PL-QYBW`). Only fat stays crowded for long. At a 1 MAC dial, across
the simulator's three agents, muscle spans about 22–43 px at one hour and fat
about 1.3–3.3 px. That is with the chart at its preferred height of 360 px,
where the percent axis is about 320 px tall and the time axis and its labels
take the rest. In a small area the chart can be as short as 160 px, with a
percent axis about 120 px tall: muscle about 8–16 px and fat 0.5–1.2 px. Fat's
trace near zero is its true partial
pressure, and partial pressure drives effect, so one linear axis serves all six
compartments. Because the hover readout reports every trace in reach, the
crowding needs no change of scale. The fat trace cannot show how much agent fat
holds. The compartment schematic shows that amount (§ "The compartment schematic: what its
heights, amounts and share bar assert").
<!-- not-restated: 1.3 -->

**For developers.** The vertical range is fixed because an axis that grew to fit a trace would
redraw a rising curve smaller partway through a lesson, and a reader would take
that change of shape for something the model did.

A top that the chart chose for itself is refused, not merely left off. Height
on a chart is read as size, and an axis fitted to the data changes how large
the same difference looks. In crowd-sourced experiments the effect of a
truncated axis on judged effect size persisted even when the design marked the
truncation explicitly (Correll, Bertini and Franconeri, CHI 2020,
doi:10.1145/3313831.3376222, abstract read on arXiv 1907.02035). The same paper
advises choosing an axis for the size of difference the chart is meant to show.
A reader-chosen top does that for the lesson in hand, a low top for a lesson
held near 1 MAC and a high one for an overpressure induction, and it changes
only when the reader changes it (`PL-V67Q`'s design round, project owner,
2026-10-03, ratified, `PL-K1VH`).

The three tops are `ChartCeiling` in `app/formatting.py`. The low top puts
1 MAC at two thirds of the plot's height. The high top is above every agent's
vaporizer maximum, the highest being sevoflurane's 8%, at 4.44 ×MAC.
<!-- derived: 4.44 from data/agents/sevoflurane.json max_delivered_concentration_percent = 8, mac_at_age_40_percent = 1.8 -->

A second axis that shows the same quantity in another unit, as Celsius beside
Fahrenheit does, is the accepted use of a dual-axis chart, and such charts
give each axis its own tick interval by default (Datawrapper, "Dual-axis
charts: a guide" and "Dual-axis charts", both read 2026-11-22). Round labels
make a value easier to read off an axis: Talbot, Lin and Hanrahan
(IEEE InfoVis 2010, section 2) cite evidence that round numbers are much easier
to work with in mental estimation. So each axis is labelled at round values of
its own unit (`PL-BNMZ`). The percent steps are `PERCENT_AXIS_STEP_LADDER` in
`app/chart_frame.py`, the 1-2-5 steps of Heckbert's labelling algorithm that
the same paper describes.

The standard 3 ×MAC top (`CHART_AXIS_TOP_MAC` in `app/formatting.py`) puts the
1 MAC line at a third of the plot height, inside the plot rather than on its
frame. Unlike a ceiling of 2, it also keeps on the plot the 2-3 ×MAC range that
overpressure induction works in. Desflurane's vaporizer is the most limited. Its
18% maximum is 2.73 ×MAC, so desflurane's plot has an empty band from 18% to its
19.8% top, which no dial setting can reach. A ceiling at each agent's own dial
maximum could never be exceeded, but the chart would then draw the same MAC
multiple at different heights for different agents, because the dial maxima run
from 2.73 ×MAC for desflurane to 4.44 ×MAC for sevoflurane (`PL-CC23`).
<!-- derived: 2.73 from data/agents/desflurane.json max_delivered_concentration_percent = 18, mac_at_age_40_percent = 6.6 -->
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->
<!-- derived: 4.44 from data/agents/sevoflurane.json max_delivered_concentration_percent = 8, mac_at_age_40_percent = 1.8 -->

The gridlines stand at the positions of the MAC axis's labels, which
`mac_axis_ticks` places, so the axis names every gridline on the plot.

The chart compares a trace's excess over the ceiling with the displayed
resolution rather than with zero, so it does not name a compartment whose trace
sits exactly at the ceiling. This matters for desflurane, whose ceiling,
3 × 6.6, is 19.799999999999997 in binary floating point.
<!-- provenance: data/agents/desflurane.json mac_at_age_40_percent = 6.6 -->
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

Each top is scaled by the agent's MAC, the standard top leaves room above
1 MAC, and the high top is above every vaporizer maximum
(`test_the_chart_ceiling_is_the_chosen_top_times_the_agent_s_mac`,
`test_the_chart_ceiling_leaves_one_mac_inside_the_plot_with_room_to_overpressure`
and `test_the_high_ceiling_is_above_every_agent_s_vaporizer_maximum` in
`tests/unit/test_formatting.py`). Both axes' labels at every top and agent are
in `test_each_axis_is_labelled_at_round_values_of_its_own_unit`
(`tests/unit/test_chart_frame.py`), and the drawn gridlines in
`test_the_mac_axis_labels_every_gridline_and_the_percent_axis_is_round`
(`tests/integration/test_qt_chart.py`). A trace above the axis is reported on the
run that drew it
(`test_a_trace_above_the_axis_is_reported_on_the_run_that_drew_it` in
`tests/integration/simulation_view/test_simulation_view_readouts.py`), and a
trace exactly at the ceiling is not
(`test_a_trace_exactly_at_the_ceiling_is_not_reported_off_scale` in
`tests/unit/test_dashboard_frame.py`).

### The chart's time base

**The time base is how much simulated time a chart shows at once.** The reader
either picks from a fixed ladder of widths, from fifteen minutes to twelve
hours, or leaves the default, which fits the whole run so far. Either way, the
horizontal axis is simulated time. A separate control, the playback rate, sets
how fast the run advances, so that a long case can be watched in one sitting.

**A time base changes the view and never the run.** No simulation step is
resized or taken again. Nothing that defines the run is added, discarded or
altered. A case watched at a width of fifteen minutes or of twelve hours is the
same run, so `docs/VERIFICATION.md` § "The reproducibility guarantee" still applies. Every point drawn
at any width is a state that the run reached at the simulated instant where the
point sits. In a wider window, these states lie further apart in simulated time.
No drawn value is estimated from its neighbours, and no stored image is
enlarged.

**No one width suits a whole case.** The compartments this model exists to teach
are slow, but the moment a learner is most likely to be watching is not. At the
reference settings, sevoflurane's isolated time constant is about 135 min for
muscle and about 42 h for fat (`docs/MODEL.md` § "Tissue groups"), while
induction lasts minutes. A five-minute window hides everything slower than the
vessel-rich group. A twelve-hour window puts a five-minute induction in the
leftmost 0.7% of the plot.

**A chosen width keeps slopes comparable within a run and between runs.** It
stays the same at every moment of every run. Seconds per pixel then depend on
the reader's choice alone, not on how long the run has gone on. A trace's slope
on the plot is therefore a fixed multiple of its rate of change. A window that
widened continuously with the run would rescale every slope while the rates
stayed the same. That would misrepresent rate of rise, the one quantity by which
uptake and distribution are taught. The vertical axis has a fixed range for the
same reason (§ "The chart's fixed MAC axis").

**The gridlines follow from the width.** Each width on the ladder sets the
interval at which gridlines and labels fall, so that the axis holds four to six
intervals. Gridlines fall at multiples of that interval counted from the start
of the case, not from the window's left edge, so a gridline stays at the same
simulated time as the window slides under it. The gridlines are the same for
every run drawn on the axis, because a run branched from another keeps the clock
of the run it came from.

**The default time base shows the whole run, except while a setting is
previewed** (§ "A preview of an unapplied setting"). It uses the narrowest
width that holds the run, so the width steps up as the run grows, and slopes on
the plot change scale at each step. Past the widest width on the ladder, it
keeps doubling the width. Early in a run, it can also use widths narrower than
any the reader can choose.

**Every axis label carries its own unit, and each chart states its width.** A
label reads `0`, `45s`, `3m`, `1m30s` or `1h30m`. The time axis's title names
the width in words, after "simulated time". It says whether the reader chose the width, or it is
the whole run so far, or the window is centred on the current time for a
preview.

**Each chart has its own time base** (project owner, 2026-10-19, ratified, over
one shared window saved per Workspace; `PL-L59K`). The concentration chart and
the F_A/F_I plot each have a time-base control, and a choice in one sets that
chart alone. One chart can show the newest fifteen minutes of a case while
another fits the whole run. Two charts with the same time-base setting show the
same instants.
Each notice that depends on a chart's window describes that window and appears
on that chart. These are the notice that names traces above the top of the axis,
the count of control changes the chart could not mark, and the count of F_A/F_I
stretches it could not draw.

**A chart saves its width in its Workspace.** The Induction Workspace
that comes with the simulator saves its concentration chart at the 15-minute
width. The window follows the run, so the current values stay on the plot after
the first fifteen minutes. Switching to the Induction tab opens the chart at that
width (`PL-2KXB`).

**For developers.** The time base's code is in `app/chart_time_base.py`. The
module does arithmetic on simulated time. It reads no simulation state and
imports no interface toolkit, so the widths and gridline intervals can be read,
cited and tested without loading the interface.

Each width on the ladder is at least half again as wide as the one below it, so
one step up or down visibly changes the view.

Four to six intervals look like a grid rather than a bare axis or a hatch
pattern. No single fixed interval does that across the whole ladder. The 60 s
interval used before would draw 720 gridlines across a twelve-hour axis, enough
to look like a solid block.

The doubling is there because a mode named for showing the whole run would
misstate what is on screen if it showed only the last twelve hours of a
fourteen-hour run. Widths narrower than any on the ladder let the default work
ten seconds into a run as well as at ten hours. The reader cannot pick them,
because a span with nothing in it gives a view nobody wants.

Each label carries its unit because the axis spans anything from a minute to
half a day. A bare `12` would mean twelve minutes at one width and twelve hours
at another. Like the playback rate, the width is displayed because a reader who
cannot see the span supplies their own assumption for it. The chart also says
how the width was set, because a chosen width and the whole run so far mean
different things about what is on screen.

The roadmap for v0.6.0 asks for a time base per chart (`ROADMAP.md`
§ "Completed: v0.6.0 - the layout is the reader's", Required scope entry 11).
Each chart's notices describe its own window, because a notice naming a clipped
trace that the chart does not draw would be false for that chart. Charts with
the same time-base setting are drawn from one frame.

The tests in `tests/integration/simulation_view/test_simulation_view_charts.py`
check that a time base changes nothing the run recorded
(`test_choosing_a_time_base_changes_nothing_the_run_recorded`) and makes the
window exactly as wide as chosen
(`test_selecting_a_time_base_makes_the_window_exactly_that_wide`). Those in
`tests/unit/test_chart_time_base.py` check that each width is ruled into four to
six intervals (`test_every_rung_is_ruled_into_between_four_and_six_intervals`),
that fitting always contains the run (`test_fitting_a_run_always_contains_it`),
and that a chosen width is held at every point of a run
(`test_a_chosen_width_is_held_exactly_at_every_point_of_a_run`). Each chart
names only the clipped traces its own window shows
(`test_each_chart_names_only_the_clipped_traces_its_own_window_shows` in
`tests/integration/test_run_surfaces.py`).

### MAC-awake as a chart reference

The compartment chart carries two horizontal clinical references for the agent
in use. A **band** marks the agent's MAC-awake, the concentration at which half
of a population responds to verbal command. The band's label says
"MAC-awake". A **line** marks the agent's nominal 1 MAC, whose endpoint is
immobility in response to a standardized surgical incision. Neither is
modelled. Both are published constants, drawn at their values on the chart's
percent axis.

**With the MAC-awake band and the 1 MAC line both drawn, the chart shows the
*decrement required for arousal*, not only the endpoint.** Chortkoff et al.
state that "along with pharmacokinetics, the ratio of the awakening
concentration to the anesthetizing concentration (MAC-awake/MAC) determines
time to awakening". That ratio becomes the visible gap between the two
references, so a reader can compare a twenty-minute case with a three-hour case
side by side and see the lesson of context-sensitive emergence.

**Shape, not colour, tells the two references apart.** MAC-awake is a measured
population value with real spread, so it is drawn as a band. 1 MAC is a
definitional anchor, not a distribution of the same kind, so it is drawn as a
line. The difference between a band and a line survives greyscale and every
colour-vision deficiency. Both references are drawn in the interface's own ink
and label colours, so neither is mistaken for a compartment.

**The band spans one standard deviation either side of the published mean
MAC-awake.** It covers roughly the middle two thirds of a population, not its
full range. A rule marks each edge, on its published value, with a light fill
between the two. Nothing pads the band outward, even where it is thin, so the
space between the rules is exactly the published spread. The fill is light
enough that every trace keeps 3:1 against it in all four vision models, because
the band is where a reader compares the crossings (`PL-GT8W`).

**The fat trace is told apart from both references by lightness.** Grey marks
the chart's furniture: the 1 MAC line, the control marks and the gridlines.
After a long case the fat trace is nearly flat and lies near the band, so it
could be taken for the 1 MAC line or for a band edge. The fat trace is a dark
olive, darker than the grey line and lighter than the ink edges. The contrast
check holds it at least 1.5:1 from each, in all four vision models. Six traces
cannot all be held more than 1.48:1 apart from each other, so each reference is
further from fat than the traces can be from each other (`PL-6W49`).

**The 1 MAC line marks the nominal value, not the dialled one.** A fixed line
sits at the same height in every run, so runs stay comparable. A line that
tracked the dialled concentration would only restate where the trace already
starts. The line sits at the stored MAC, the MAC at age 40, and is labelled as
a reference adult value, not as this patient's MAC, because this model has no
age parameter.

**The band is not a prediction for the patient on the screen.** It is the
strongest claim that the evidence supports. The interface shows no
time-to-wake-up figure of any kind, because this model does not support a
per-patient prediction.

**Read the band against the vessel-rich trace.** This model has no effect-site
compartment and defines $`F_a \equiv F_A`$ (see `docs/MODEL.md` § "What the model represents"), so the
alveolar trace is the fastest patient trace on the chart and the furthest from
where responsiveness returns. One simulation shows the size of the gap. It ran
sevoflurane for 3 hours at the opening dial of 1.80%, which is the stored 1 MAC,
and the default fresh gas flow of 4 L/min. That brought the alveolar fraction
only to 1.52%, or 0.84 MAC. The vaporizer was then turned off and the fresh gas
flow raised to 10 L/min. The alveolar trace crosses the band's centre at
2.86 min, and the vessel-rich trace crosses it at 6.55 min, 2.29 times later.
These figures are from a run on 2026-11-22 (`PL-39KH`, `PL-PTDZ`). An
automated test reruns this protocol and checks each figure to the decimal
places printed here.
<!-- not-restated: 10 L/min -->
<!-- provenance: data/agents/sevoflurane.json mac_at_age_40_percent = 1.8 -->
<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->

<!-- derived: 2.86 min from data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34, mac_at_age_40_percent = 1.8 -->

At a 1 MAC dial, no patient trace reaches the 1 MAC line, however long the case
runs. This is expected and is not a display fault. Muscle and fat keep taking
up agent for many hours, so the blood returning to the lungs stays below the
alveolar gas. That keeps the alveolar fraction below the inspired fraction, and
rebreathing keeps the inspired fraction below the dial (`PL-39KH`). In the
3-hour run above, the vessel-rich trace reached only 0.84 MAC, as the alveolar
trace did. This shortfall happens in real patients too, and it is worth
teaching.

**All three stored MAC-awake fractions belong against the vessel-rich
trace**, because each was determined at equilibrium, not by fast washout.
`docs/PARAMETERS.md` § "The MAC-awake fractions" records how the sources were
read, and why each agent keeps its own fraction.

**The band is drawn at a fraction of the stored MAC.** MAC-awake is stored as
that fraction, never as a percent of one atmosphere. The chart's MAC axis is
also scaled by the stored MAC, so the band sits at its published fraction on
that axis. `docs/PARAMETERS.md` § "The MAC-awake fractions" says why a
published percent would draw the band too high.

**The *absolute height* of the MAC-awake band and the 1 MAC line inherits every
limitation of the stored MAC.** The MAC-awake fractions come from primary
measurements in humans (tier 1). The stored MAC is Mapleson's meta-analytic
MAC at age 40, not a measurement, so the source hierarchy grades it tier 2
(`docs/PARAMETERS.md` § \"Source hierarchy: what may be cited as the authority for a value").
`docs/PARAMETERS.md` § \"Delivery-limit and MAC parameters" records its limitations. The interface
shows that MAC, so a reader can compare it with the value they would use.

**Three misreadings of the band all make emergence look faster than this model
says.** Concentration falls during emergence, so a trace crosses a higher
reference sooner, and a faster-falling trace crosses any reference sooner. The
three are:

1. reading the band against the alveolar trace instead of the vessel-rich one;
2. drawing the slow-washout value against a fast-washout alveolar trace, where
   0.22 would be the matching figure;
3. dividing a published MAC-awake percent by a MAC other than the one its
   population was measured against, as in the desflurane example in
   `docs/PARAMETERS.md` § "The MAC-awake fractions".

A learner who takes away any of these errors carries into practice the belief
that a patient is more awake than they are.

**The stored MAC is a fourth source of error in the band's height**
(`PL-GCGX`). The band is drawn at a fraction of the stored MAC, Mapleson's MAC
at age 40, and `docs/PARAMETERS.md` § "The stored MAC" gives its 95% confidence
limits of about ±7%, and ±10% for desflurane. A dial set in percent fixes the
traces, so an error in the stored MAC moves the band against them by the same
proportion. In a run left at its opening 1 MAC dial, the error does not move
the band against the traces. The dial opens at the stored MAC and the model is
linear in the dial, so the traces move with the band, and the error is in the
percent that the dial delivers instead. In the washout run described earlier in
this section, the vessel-rich trace crosses sevoflurane's drawn band centre of
0.612% at 6.55 min. A patient older than 40 has a lower MAC, so the band drawn
at the MAC at age 40 sits above that patient's own and teaches an earlier
wake-up.
<!-- derived: 0.612 percent from data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34, mac_at_age_40_percent = 1.8 -->

The comparison with Katoh's own MAC at age 40 points the other way: the band
sits slightly low, so it teaches a slightly late wake-up. `docs/PARAMETERS.md`
§ "The MAC-awake fractions" gives the comparison.

**For developers.** No governing equation in the model's code (`core/`) uses
MAC-awake or the stored MAC (`mac_at_age_40_percent`). `core/parameters.py` gives the
band's two edges as fractions of MAC (`mac_awake_band_fractions`), and
`app/formatting.py` multiplies them by the stored MAC to place the band on the
percent axis (`mac_awake_band_percent`). Each
agent's data file records the MAC that its MAC-awake fraction was derived
against (`mac_awake.mac_reference_basis`). Storing the fraction is a safety
decision, and it also keeps the band correct if the stored MAC is ever changed
or made age-aware.

Telling the references apart by shape meets the requirement in
§ "Color contrast" below for any encoding that carries meaning, and it
separates them more strongly than any pair of colours would. Drawing them in
the ink and label colours avoids adding a seventh and eighth hue to the chart.

The band is left unpadded, even though a minimum drawn height would help
legibility, because a padded band would claim a wider population spread than
the sources support.

The band is ruled on both edges because no axis range that the chart can use
gives it enough height to look like a band on its own. On the fixed axis, whose
top is 3 ×MAC (`CHART_AXIS_TOP_MAC`), the band spans 3.33% of the plot height
for sevoflurane and 4.20% for desflurane. A 2 MAC ceiling would make the band
unambiguous, but would put the 1 MAC line at mid-plot and leave no room above it
for the overpressure induction that the chart must be able to show
(§ "MAC multiples as a display unit"). A 4 MAC ceiling would shrink the band to
2.50%, as on the earlier axis, whose top was the vaporizer dial's maximum. A
band ruled on its upper edge only, over an unruled fill, looks like a line with
a shadow beneath it, whatever the fill's height, so the two references would no
longer differ in shape. Two rules with a gap between them look like an interval
at any height the axis leaves.

<!-- derived: 3.33 percent from data/agents/sevoflurane.json mac_awake.standard_deviation_fraction_of_mac = 0.05 -->
<!-- derived: 4.20 percent from data/agents/desflurane.json mac_awake.standard_deviation_fraction_of_mac = 0.063 -->
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

The time-to-wake-up readout is left out because a figure such as "time to
wake-up: 14 min" would be taken as a per-patient prediction. No disclaimer
beside it would undo that, because readers act on the number and not on the
disclaimer.

The washout figures come from simulating sevoflurane uptake
(`AgentUptakeSystem.for_agent("sevoflurane")`) in steps of 1 s. Since the
2026-10-31 run, each crossing time is interpolated between the two steps on
either side of it. The automated test reads the protocol and its figures from
this section (`tests/reference/test_mac_awake_washout_figures.py`), so a
parameter change that moves a figure fails it, and so does an edit to the
protocol or to a figure on its own.
<!-- provenance: core/simulation_step.py SIMULATION_STEP_S = 1 -->

### F_A/F_I as a displayed ratio

**A second plot draws $`F_A/F_I`$.** The plot is a view of its own. Of the
Workspaces supplied with the simulator, only Induction includes it, beside the
compartment chart. In the others the reader shows it from an area's view
chooser. The plot shows the modelled alveolar fraction divided by the modelled
inspired fraction, on a fixed, dimensionless axis labelled from 0 to 1. It has
its own time window (§ "The chart's time base"). The
uptake literature is taught from this curve, and the wash-in figures a reader
has seen show it. The plot can therefore be laid beside a published figure. The
six compartment concentrations on the concentration chart cannot. A validation test
compares the plotted ratio with human measurements at 30 minutes, for all three
agents in the simulator (`docs/VERIFICATION.md` § "Published wash-in and elimination validation test").
The ratio is computed only for display, and no equation of the model uses it.

**The ratio is a modelled value, not a measurement.** It has the alveolar
compartment's limitation: this model has no airway sampling delay and no dead
space. It is not a depth of anesthesia, a time to any endpoint, or a
prediction for an individual patient.

**The denominator is the modelled inspired concentration, not the vaporizer
dial.** This model assumes that the inspired fraction is the concentration in
the breathing circuit (`docs/MODEL.md` § "What the model represents"). The circuit approaches the
delivered concentration only over its own time constant, so early in a run the
two differ substantially. Dividing by the dial would understate the ratio for
as long as they differed. The interface says beside the plot which denominator
the ratio uses.

**The curve is the textbook wash-in curve only while the inspired
concentration is held constant.** If the vaporizer setting or the fresh gas
flow changes mid-run, the ratio is no longer the wash-in fraction of anything a
reader can name. A rise across such a change shows the setting moving, not
uptake slowing. This plot therefore carries the compartment chart's control
marks, which show where each setting changed (§ "The control-input timeline").

**A point is drawn only inside two boundaries, one on the inspired fraction and
one on the ratio.** The plot samples the run at a series of instants, called
columns. A column is inside the boundaries when both of these conditions are
true:

1. $`F_I \geq 10^{-4}`$ (0.01%), the smallest step of the concentration
   display. $`F_I`$ is exactly zero until agent reaches the circuit: at the
   start of every run, and throughout a run whose vaporizer is never opened.
   There the ratio is $`0/0`$. With this limit, the ratio is never formed
   from an inspired concentration that the display shows as `0.00%`.
2. $`F_A/F_I \leq 1`$, which is the uptake regime. Alveolar gas gives up agent
   to blood, so the alveolar fraction stays below the inspired one and reaches
   it only at equilibrium. Above 1, the tissues are returning agent faster
   than it is delivered, which is elimination, not wash-in. The chart draws
   equilibrium as a labelled reference line.

   This boundary allows the ratio up to 1.000001. At zero cardiac output the
   exact ratio rises to 1 and stops, but the simulation's rounding can leave
   it a hair above 1. If the ratio stayed at 1.000001 for a whole run of the
   longest supported length, the run would lose less than 1% of the agent in
   alveolar gas, venous blood and the vessel-rich group.

Outside either boundary nothing is drawn, so the trace breaks into separate
stretches. No value is pinned to the edge of the axis or replaced by a
default, and no line bridges a gap. A ratio held at 1.0 would show a completed
wash-in that the run never reached. A line joining the wash-in on either side
of a washout would show values that the run never produced.

**Each stretch of the trace is extended by one column at each end, so a reader
can see where it stops.** That extra column is the stretch's *crossing column*:
the neighbouring column that has a ratio but lies outside the boundaries.
Without it, the trace would stop at its last column inside the boundaries,
still climbing steeply. That last column can lie below the equilibrium line by
as much as the trace rises between two columns. A trace that stops in clear
space short of the line looks exactly like one cut off by the edge of the plot.
With the crossing column drawn, the trace meets the equilibrium line and ends on
it, with a point marker that shows the trace ended rather than ran out of view.

A crossing column whose ratio is above a fixed ceiling is not drawn at all. Its
stretch then ends at its last column inside the boundaries, with no point moved
onto the ceiling and no line drawn toward it.

**The extra column at each end of a stretch is drawn, but its value is not
shown as wash-in.** Its ratio is above 1. Hovering over it shows "Past
equilibrium: not a wash-in fraction" under the wash-in label, in place of the
ratio. A value such as 1.03 shown there would teach a wash-in past completion,
at the point marker, where a reader is most likely to look.

**The caption beside the plot states the ratio, or says why the trace is
blank.** While the trace is drawn, the caption gives the value at its
right-hand end. "No agent has reached the circuit yet" and "the patient is
returning agent" are opposite situations, and an absent trace alone cannot show
which applies. The caption and the trace are computed separately, from the same
stored state. The caption reads the state that the run stored for the second it
has reached, and the trace's right-hand end is drawn from that same state by the
same division, so the two show the same ratio.

**The gridlines and labels run from 0 to 1, with a little space above them.**
Every published wash-in figure uses a scale of 0 to 1, and matching those
figures is the point of this plot. The space above keeps a trace that ends at
equilibrium off the top edge, where it would look cut off. Because that space
is unlabelled, a reader does not take it for a range the ratio can reach.

**The axis is fixed rather than fitted.** An axis that grew to fit the ratio
during elimination would redraw the wash-in curve at a smaller height partway
through a lesson, and a reader would attribute that change of shape to the
model. Such an axis would also have no stable height. During elimination the
circuit is fed by agent-free fresh gas and by rebreathed alveolar gas, so the
ratio settles near $`1 + \dot V_{\mathrm{FGF}} / \dot V_A`$, which the
supported input ranges do not bound.

**The ratio is shown to two decimals, to match the spread of its published
values.** Yasuda et al. report 0.850, 0.733 and 0.90, with standard deviations
of 0.018, 0.027 and 0.01, so a third decimal would be finer than that spread.
See `docs/VERIFICATION.md` § "Published wash-in and elimination validation test".

**For developers.** The ratio and its two boundaries are computed only in
`app/wash_in.py`, a module that contains nothing else. Unit tests cover both
(`tests/unit/test_wash_in.py`). The ratio is no part of a run's definition. A
test checks that the plotted ratio is the quantity that the validation compares
(`test_the_displayed_ratio_is_the_quantity_this_file_validates` in `tests/reference/test_published_wash_in_and_elimination.py`).

Both plots take their control marks from the run's one record of setting
changes. The marks are computed once for each time window
(`assemble_chart_frame` in `app/chart_frame.py`), so plots that show the same
window draw the same marks. A plot with a window of its own marks the changes
inside that window.

The 0.01% limit on $`F_I`$ is derived from the concentration display's
resolution (`CONCENTRATION_DISPLAY_RESOLUTION_PERCENT`), so it follows that
resolution if the display changes.

The rounding allowance of 1e-6 (`WASH_IN_ROUNDING_ALLOWANCE`, `PL-N559`) is
there because, at zero cardiac output, the stepped run settles on a
floating-point fixed point within about 1e-13 of the exact solution. A fixed
point is a state that every later step returns unchanged. In some runs that
state has $`F_A`$ above $`F_I`$. At the 0.1 s step that a run took until
2026-11-21, an isoflurane run at a fresh gas flow of 10 L/min settled at a ratio
of 1 + 2.2e-14, which the plot once captioned as the patient returning agent.
Which side of 1 a run settles on changes with the step. At the one-second step,
isoflurane at 6 L/min settles at 1 + 4.7e-15, and every shipped agent at the
fastest fresh gas flow settles below 1 (measured 2026-11-21). Because later
steps return the same state, the overshoot does not grow with run length. On
2026-10-26 it was the same at 96 h as at 1 h. A test checks the fixed point against the exact solution for each
shipped agent
(`test_a_zero_cardiac_output_steady_state_is_not_read_as_elimination`).
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->

The allowance is sized from the 1% limit in condition 2 under § "A point is
drawn only inside two boundaries", a clinical requirement, rather
than from the rounding (project owner, 2026-10-26, ratified, over 1e-9 sized
from the rounding and over deriving the value in code). At a ratio of
1 + 1e-6, agent leaves at a rate of alveolar ventilation times $`F_I`$ times
1e-6. The agent held in alveolar gas, venous blood and the vessel-rich group
also scales with $`F_I`$, so the fraction lost is the same at any $`F_I`$. The
worst case is desflurane at an alveolar ventilation of 12 L/min, where a run
loses about 0.3% in 24 h. A test checks the loss for every shipped agent from
the run-length limit, the ventilation limit and the data files, so extending
any of them fails it
(`test_the_rounding_allowance_hides_no_clinical_change_over_a_whole_run`). The
allowance is also about 10 million times the largest overshoot seen in a run,
9.6e-14, which was measured on 2026-10-26, before a run stepped in whole
seconds.
<!-- provenance: core/supported_ranges.py MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The chart code recomputes the stretches in each frame, from the columns that
frame draws, rather than keeping them as the run goes. A stretch can therefore
start or end only at an instant that the chart plots (`app/chart_frame.py`,
PL-2FM6).

The column at which the $`F_A/F_I`$ curve crosses equilibrium has a ceiling,
because the ratio can jump. In runs stepped at 1 s, the first value above
equilibrium is at most 1.0281, across every shipped agent and the supported
alveolar ventilations and cardiac outputs, at the maximum fresh gas flow
(2 646 runs, measured 2026-11-21). The largest case has no cardiac output and
little ventilation. There the inspired fraction falls for one second while the
alveolar fraction barely moves.
A change to the circuit volume would move the ratio further, because the
circuit keeps its agent and divides it by the new volume, so a doubled volume
halves $`F_I`$. A run refuses its next step after such a change while the
circuit holds agent (`SimulationState.advance`), so no stored state shows that
jump. A drawn column can still land on a state later than the one measured, so
the ceiling keeps a margin above 1.0281. The ceiling is 1.05 (`WASH_IN_TERMINUS_CEILING` in
`app/chart_frame.py`), below the axis top of 1.15 (`WASH_IN_AXIS_MAXIMUM`), so
even the highest crossing column it allows still has clear space above it.
<!-- provenance: core/simulation_step.py SIMULATION_STEP_S = 1 -->
<!-- provenance: app/chart_frame.py WASH_IN_TERMINUS_CEILING = 1.05 -->
<!-- provenance: app/chart_frame.py WASH_IN_AXIS_MAXIMUM = 1.15 -->

The hover text past equilibrium is set in the chart code
(`WASH_IN_HOVER_PAST_EQUILIBRIUM_TEXT` in `app/chart_frame.py`, `PL-YH6Z`).

The formula for the ratio during elimination was checked on sevoflurane by
closing the vaporizer at a fresh gas flow of 10 L/min after a 30-minute wash-in.
The ratio was 3.47 at the reference adult's 4.0 L/min of alveolar ventilation,
1.83 at 12.0, 5.93 at 2.0 and 20.11 at 0.5, against predictions of 3.50, 1.83,
6.00 and 21.00.
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4.0 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->

The two decimals are not derived from the concentration display's resolution,
because the ratio's resolution depends on its denominator. It is far coarser
early in wash-in than at equilibrium, so any single derived figure would
over-claim at one end.

### Color contrast, and the standard this interface is held to

**The interface is held to WCAG 2.2 Level AA.** WCAG 2.2 is the current W3C
Recommendation (published 2023-10-05). Meeting its Level AA also satisfies the
2.1 AA that EN 301 549 and the 2024 ADA Title II rule reference, and the 2.0 AA
that Section 508 references. None of those applies to this project. AA was
chosen as the right engineering bar for a teaching tool. The interface does not
target WCAG 3.0, a Working Draft whose scoring model replaces pass and fail.
<!-- not-restated: 2.1 -->

The project defers four criteria until the interface is settled enough to
assess them: SC 2.4.11 (Focus Not Obscured), 2.5.8 (Target Size), 1.4.10
(Reflow) and 1.4.12 (Text Spacing). Every layout operation can be done from
the keyboard. Keyboard operation of the rest of the interface and
screen-reader support are planned (`ROADMAP.md`, planned-milestone item 20)
and are not yet commitments.

**Every control that Tab reaches shows when it has the keyboard focus**, as
SC 2.4.7 (Focus Visible) requires. The platform style draws no mark on a
slider, a selector, a scroll area or a list. Each of those draws a 2 px ring
inside its edge, in INK, or in the agent's foreground on the agent selector.
Start, Pause and Reset carry the same ring, and they also look different while
held down. The ring shows only when the keyboard moved the focus, as the
platform's own focus marks do. A plot takes no key, so Tab does not stop on it.
<!-- provenance: app/theme.py FOCUS_RING_WIDTH = 2 -->

#### Minimum contrast for text and graphics

Two criteria carry most of the weight:

- **SC 1.4.3, Contrast (Minimum)**, requires 4.5:1 for text. Every readout,
  every label naming a readout, and every agent name over its identification
  color must meet it. The project never uses the large-text exception (18pt, or
  14pt bold), so the larger readout values must meet 4.5:1 too, and so must the
  bold status text, set at the application's default size, which the platform
  chooses.

  **Text is measured against the surface it is drawn on: the page background
  or a panel.** The run-status word, the halted-run notice and the
  educational-use disclaimer sit directly on the page background. The
  readouts, their labels, the axis description and the accounting lines sit
  inside panels, which are lighter than the page. Where a color appears on
  both, the page background is the stricter test, and it is the one that
  counts.
- **SC 1.4.11, Non-text Contrast**, requires 3:1 for graphical objects. Here
  that means each chart trace against what it is drawn on: the panel, the
  MAC-awake band's fill where the trace crosses the band, and the fill of the
  region in which a drag's preview is drawn, alone and where it overlaps the
  band. It also means each agent swatch treated as a shape, and the active
  track of each parameter slider, which shows where the slider's value sits in
  its range. It also means the two chart references, which are the MAC-awake
  band and the 1 MAC line, and the lines that the layout draws on an Area
  border, under the current Workspace tab and during a corner drag.

<!-- not-restated: 4.5 -->

**No control that carries the agent's identity is ever drawn disabled.** SC
1.4.3 sets no contrast requirement for text in an inactive control, and W3C's
Understanding document for that criterion gives a disabled button with grey
text as its example. Qt draws a disabled control's text in the platform's grey,
over whatever color the interface set. A disabled agent selector would
therefore conform to AA and still lose the agent's name against its
identification color. The interface does not use this exemption for those
controls. While a run holds the agent fixed, the selector is hidden rather than
disabled, and the running-agent label takes its place. The label has no
disabled state.

#### Where the chart goes beyond AA

The interface goes beyond AA in two places:

- **Chart traces can be told apart from each other, which WCAG does not
  cover.** SC 1.4.11 asks only for 3:1 against the *background*, yet reading
  one compartment against another is the whole lesson of this chart. W3C's
  Understanding document for that criterion excuses lines from contrasting
  with each other only where they overlap little. This chart's six traces
  start together, converge toward equilibrium and cross during wash-in and
  washout. No choice of colors can give every pair of six traces 3:1 against
  each other, so each trace also has a line style or marker, which the next
  section describes.
- **Each chart trace clears 3:1 against the panel, both as displayed and under
  simulated dichromacy.** SC 1.4.11 is defined on the color the display emits,
  so this bar is the project's own. Its reason is the criterion's purpose: a
  graphical object must be findable against its background, and a check that
  models only normal color vision cannot show that for a reader with
  dichromacy.

The excuse for lines that overlap little comes from the Understanding document
for SC 1.4.11, read on 2026-09-07 in a copy the project owner supplied
(`PL-JX0Z`). Its line-graph example (Figure 38) says: *"The lines should have
3:1 contrast against their background, but as there is little overlap with
other lines they do not need to contrast with each other or the graduated
lines."* Its "Graphical Objects" section makes each line in a graph a graphical
object in its own right. Citing the Gestalt "law of continuity", it lets
**minor** overlaps between lines be ignored.

#### The exempt gridline grey

**The gridline grey is exempt from SC 1.4.11** (project owner, 2026-09-27,
ratified, over darkening the grey to 3:1; `PL-HKTB`). It colors the plot's
gridlines, the axis lines, the line under each Area's header and the sliders'
unfilled groove, at 1.31:1 against the panel. The criterion
applies only to a graphical object *required to understand the content*. The
values that the gridlines mark are shown in three other ways: each gridline
stands at an axis tick labeled in text at 5.00:1, the readouts state every
compartment's current value, and hovering over any drawn point shows its exact
value. The line under an Area's header sits between the header's menu and the
View's own heading, which already mark the boundary. The groove is the edge of
a slider whose handle and filled track identify it.

The gridline grey's exemption (`GRIDLINE`) rests on the Understanding document
for SC 1.4.11. The document's line-graph example does ask 3:1 of a chart's
"background lines for the values", but in that example the gridlines are how a
value is perceived at all. Under the heading "Required for understanding", the
document says the criterion does not apply when "a graphic with text embedded
or overlaid conveys the same information, such as labels and values on a
chart". This chart passes the criterion's own test: imagine the gridlines
invisible, and ask whether the chart is still understood. The criterion's
paragraph on boundaries is what excuses the groove.

Darkening the grey was refused because of the chart's visual order, in which a
gridline sits below a reference line and a reference line below a trace. A
gridline at 3:1 would be 87% as dark as the lightest trace (3.43:1), and that
order would collapse. Line widths of 1 / 1.5 / 2-3 px also carry that order.

#### How the ratios are measured, and why the window is always light

**The contrast ratios are computed from the interface's own colors**, with
WCAG 2.2's definitions of relative luminance and contrast ratio, each time the
project's checks run. Each requirement is a minimum ratio that named colors
must reach, such as 4.5:1 for a readout's text on its panel. A requirement
whose colors miss its minimum today is a shortfall. Each shortfall is recorded
with the work item that will fix it.
<!-- not-restated: 4.5 -->

**The window is always light, even on a computer set to dark appearance**
(project owner, 2026-09-20, ratified - chosen over leaving the host appearance
alone, and over growing a second palette for dark appearance). All 27
requirements are measured on the light theme's surfaces. Four are measured on
a fill that the theme declares: the three agent fills, and the primary color
behind a filled button's label and a selected row. The other 23 are measured
on the panel or the page background. The
six compartment trace colors were chosen to meet their minimums under simulated
dichromacy on those same surfaces. A window drawn on other surfaces would show
color pairs that nothing has measured. A disabled control still takes its
colors from the computer's setting, apart from two disabled states that the
interface declares in the muted color: the label of an unavailable transport
button, and an unavailable menu entry. That color's contrast is checked too.

Supporting dark appearance would mean measuring every requirement again on a
second pair of surfaces, and choosing all six trace colors again under four
vision models.

#### Color as a cue: agent colors and the alert color

**Color is never the only cue.** SC 1.4.1 (Level A) requires this. Telling a
running simulation from a halted one is safety-critical. The status words
"Running" and "Valid" differ from the words for the other states, so a reader
who cannot tell the colors apart still reads the state. "Paused" and the
words for a run that halted on a mark or at the supported run length appear in
the muted color, as do the banner that reports a stop at the supported run length
and the banner that announces it. "Stopped — simulation
error" and "Validation failed" appear in the alert color.

The agent selector, the header and the running-agent label back the written
name with the agent-identification color of ISO 5360:2016 Table 2 ("Dimensions and colours
of agent-specific bottle collars and connectors"): yellow for sevoflurane,
purple for isoflurane, and blue for desflurane. Footnote b of that table is why
the color appears at all: "if a colour is used on a vaporizer, bottle, or
package label to facilitate correct identification, it is important that only
the colour for the appropriate anaesthetic agent be used". The footnote makes
displaying a color an obligation to display the correct one, which is a
stronger reason than SC 1.4.1 for never using color as the only cue. A second
cue keeps a mis-seen color from becoming a mis-identified agent, so the agent
name always accompanies the color.

The running-agent label stands in the selector's place while a run holds the
agent fixed, which is most of the time a reader is looking at the screen. It
names the agent on the same fill and in the same text color as the selector.

The displayed fills are two approximations away from the standard's own color.
Table 2 footnote c states that "Munsell colour is the original" and that the
other color systems it lists "show the nearest available colour sample". The
Pantone reference is therefore already ISO's approximation, and each displayed
fill is a screen color (sRGB) that approximates the Pantone in turn. The
sevoflurane and desflurane originals lie outside the range of sRGB colors, so
no display can reproduce them exactly. Converting each Munsell original to sRGB
directly gives each displayed fill's difference from the standard's original
(ΔE00):

| Agent | ISO Munsell original | Munsell as sRGB | Displayed fill | ΔE00 |
| --- | --- | --- | --- | --- |
| Sevoflurane | 6.25Y 8.5/12 | `#F2D600` | `#FEDB00` | 2.1 |
| Isoflurane | 7.5P 4/12 | `#8D4192` | `#981D97` | 5.7 |
| Desflurane | 10B 4/10 | `#0069A0` | `#00629B` | 2.6 |

<!-- not-restated: 2.1 -->

Table 2 specifies a *color* for desflurane, and this application uses it,
even though the Scope of ISO 5360 excludes desflurane's *dimensions* and its
row in that table records "N.S." for the collar angle.

This application keeps a known limitation of the standard. A reader with a
color vision deficiency cannot tell isoflurane's purple from desflurane's blue.
With normal color vision the two differ by only 1.09 in luminance, so hue alone
separates them. Simulating the three dichromacies removes the hue without
supplying the luminance difference needed to tell them apart: 1.48 for
protanopia, 1.06 for deuteranopia, and 1.11 for tritanopia. More separable
colors would break the match with real vaporizers, so they are the worse
option. For a reader with a color vision deficiency, the agent name beside each
color identifies the agent instead.

**The alert color deliberately does not follow the medical alarm-color
convention** (project owner, 2026-09-14). This interface uses the alert color
for text and for three kinds of drawn line. The text is the run-status word of
a failed run, a transient notice line, the agent-accounting status word when
validation fails, the permanent educational disclaimer, the discard statement
of the case-discard dialog, the title of the notice that an Area shows in
place of a View it cannot draw, and the text that states a refusal, a failure
or a value above the scale. The drawn lines are an Area border whose drag has
stopped at a least size, the preview of a split, join or swap that the layout
refuses, and the bar that marks a schematic container above its scale.
The agent colors above follow a standard because it requires them, and nothing
requires the alert color.

IEC 60601-1-8 governs *visual alarm signals*, which are indicators that encode
priority by color together with a flash rate. This interface has no indicator
lamp, filled banner, flashing element or priority tier, so the convention has
nothing to apply to.

The alert-color decision applies to every element added to the interface. An
indicator-shaped element could still appear, and it must not arrive with a
monitor's priority palette.

IEC 60601-1-8's mapping of priority to color could not be established from a
primary source, and the secondary sources disagree. Three independent reports
give the low-priority color as cyan, as blue, and as "green or blue". The
alert-color decision does not depend on the mapping.

The disclaimer settles the question against the convention. The alert color
marks a line that is on screen *always*, while a monitor's alarm colors carry
meaning because they are absent until something is wrong. A permanent element
painted in a high- or medium-priority alarm color would teach the opposite of
the convention it borrowed. Departing from the convention is also wanted for its
own sake. A teaching tool that looks unmistakably unlike a monitor cannot be
mistaken for one, which is the view this project's disclaimers already take.

*The disclaimer line has been in view at every window height since it was
fixed outside the scrolling part of the page* (`PL-NNML`).
The paragraph that opens "The disclaimer line and the unconditional region are
always in view", in § "What this list requires once the layout is the
reader's", says where the line is placed. The argument above needs only that
the line is a permanent statement, not a conditional one.

The boundary of the supported run length is shown in the muted color, not the
alert color. Coloring a correct model's declared boundary as a fault would
teach a reader to distrust a sound number. § "Supported run length" gives the
rest of the argument.

#### The code and tests behind the color requirements

**For developers.** The contrast check (`tools/contrast_check.py`) runs in
`make check`. It reads the color constants from `app/theme.py`, which contains
every one of them. A second check (`check_colors_live_in_the_theme`) keeps them
there.

A third check (`tools/agent_identity_check.py`) keeps every control that
carries the agent's color from being drawn disabled. It allows a control to be
disabled only where the same condition also hides it. The running-agent label
is `_running_agent_display` in `app/run_view.py`, and
`_apply_agent_color_scheme` there is the one method that writes the agent's
colors.

Each entry in the contrast check's requirement table names the colors, the
criterion and the reason for the minimum. The table records which colors
matter, and the check only evaluates it. Most entries are one foreground against
one background. Some elements show their edge in either of two colors, such as
an agent badge, which is a fill outlined in the agent's own text color. The
entry for such an element declares both colors. The element passes when the
better of the two meets the minimum, because a reader finds the edge by
whichever color contrasts more. Shortfalls are listed in a second table
(`KNOWN_SHORTFALLS`), keyed by the requirement that each one excuses. The
check reports an error when a listed shortfall starts passing, so a fix cannot
leave its listing behind.

A color needs two constants when its use as a graphic wants a shade too light
for text, because text needs 4.5:1 and a graphic 3:1. The accent color is the
only such case. The sliders' active track uses `ACCENT`, and "Running" and
"Valid" use `ACCENT_TEXT`, the same hue darkened until it is legible as text.
The muted, ink and alert colors each serve both roles with one constant,
because each meets 4.5:1.
<!-- not-restated: 4.5 -->

Because SC 1.4.11 does not require pairwise separation, the contrast check
reports the contrast between every pair of traces without failing on it. It
enforces the 3:1 minimum against the panel, which the criterion does require.

A color that a criterion does not apply to goes in the contrast check's
exemption table (`EXEMPT`), with one entry per use. Each entry gives the
criterion's grounds and cites the drawing code by symbol. An entry must rest on
an exemption that the criterion itself grants, never on a failing ratio. A
color that fails its minimum is listed as a shortfall. The checks that
`make check` runs count the exempt uses into the contrast report line.
They refuse an exempt name that `app/theme.py` does not define, and a color
that is both required and exempt on one surface.

A declared color reaches the screen by one of three mechanisms. Most of the
interface is drawn by stylesheets, all composed in one module
(`app/stylesheets.py`) from the theme's color constants (`PL-Y4YX`). Some
widgets are painted from Qt palette roles instead: an entry's fill, a spin
box's stepper, a list's rows and its scroll bar, a check box's indicator and a
dialog's own surface. A stylesheet would cost them the native stepper and the
check box's tick. For those widgets, a function
(`qt_widgets.declare_interface_colours`) declares the same theme colors as
palette roles. It maps PANEL to `Window`, `Base`, `AlternateBase` and
`Button`, and INK to `WindowText`, `Text` and `ButtonText`. It maps MUTED to
`PlaceholderText`, and PRIMARY and PANEL to `Highlight` and `HighlightedText`.
The pairs on screen are therefore pairs that the requirement table already
measures.
It writes only the `Active` and `Inactive` color groups.

The third mechanism is the fallback that keeps the window light under a dark
host. A function (`qt_widgets.declare_application_colours`) writes the same
roles on the `QApplication` itself. Without this fallback, Qt's application
palette follows the host appearance. On a machine set to Dark, everything this
interface did not name would then take a dark theme's surfaces, around a light
window. No per-widget declaration can cover all of that, because every widget
beneath a styled widget resolves its colors from the application palette
rather than from the styled ancestor.

The interface sets a palette, which is authoritative at any depth, and does not
rely on a color-scheme hint. Qt 6.8 documents its color-scheme setting
(`styleHints().setColorScheme`) as a hint: "overriding the color scheme is not
supported on all platforms". On 2026-09-20 the setting was seen to be ignored
outright: it still reported `Unknown` after being set.

Disabled controls follow the host because both palette mechanisms leave the
`Disabled` color group to the platform, and the stylesheets declare a disabled
color only for the transport buttons and the menu entries. The project's rule
for interface colors (`.claude/rules/ui-color.md`) governs any decision to
declare a disabled color.
The splitter handles are enabled (`PL-W9P6`), so the border between two areas
shows the page's `BACKGROUND` under a dark host too, rather than the host's dark
surface. A test
(`test_the_border_between_two_areas_shows_the_page_rather_than_the_host`)
checks this (`PL-05M4`).

Tooltips also follow the host, because they draw from `ToolTipBase` and
`ToolTipText`, which are outside the declared roles. This interface shows a
tooltip in two places: the reason that a menu entry is unavailable, and the
description of the "+" button at the end of the Workspace tabs. No contrast
requirement measures a tooltip's colors.

The dark-appearance test (`tests/integration/test_dark_appearance.py`) renders
the dashboard, whose Bookmarks View holds the marks editor, and the new-case
confirmation under the
palette a dark host supplies. The dashboard it renders draws every registered
kind of View. It
fails on any content widget that resolves to that palette, and it checks the
chrome and the untouched `Disabled` group against the same host. Under that
host palette, 94.3% of the page scroll bar's pixels are darker than mid-grey
without the interface's own palette, and none are with it.

A second test (`tests/integration/simulation_view/test_simulation_view_foreground.py`) catches any control
that declares no color, including one added later. It builds the dashboard
with every registered kind of View drawn, under a foreground color that this
interface never uses, and fails
on any control that paints its own content and resolves to that color. It
exempts kinds of control that draw no text, and the plots and the compartment
schematic, whose text takes its color from a pen that the test cannot read. It names each kind with
its reason. A requirement exists only where somebody wrote a color down, so the
contrast check counts those kinds into its report line. Without that count, a
control that declares no color would appear on neither side of the report
line, and the line would show it as covered (`PL-4L49`).

The cited standard references, the screen-color approximations and the
accessible foregrounds are kept together in `app/theme.py`, so that the
agent-color mapping can be audited as one unit. Every foreground and background
pair must meet WCAG 2.2 AA contrast. Tests in
`tests/integration/simulation_view/test_simulation_view_agent_selector.py`
check that the agent name is shown beside its color in the selector's options
and in the header badge.

Each Munsell original was converted to sRGB via Illuminant C, chromatically
adapted to D65. The dichromacy figures were computed by the contrast check with
the Brettel 1997 projection recorded under § "The six compartment traces: what
separates them". A
test pins them, so a color change cannot leave them out of date
(`tests/unit/test_contrast_check.py`).

The alert color is `WARNING` in `app/theme.py`, and the muted color is
`MUTED`. Whatever alert color is chosen, two constraints apply. It must still
meet the interface's contrast target, which the contrast check enforces. The
ISO 5360 agent colors stay as they are, because they identify an agent and
carry no urgency.

`FocusRing` in `app/qt_widgets.py` draws the keyboard
focus ring. `tests/integration/test_keyboard_focus.py` grabs every control
that Tab reaches, in every kind of View and in the new-case question, with
and without the focus, and fails where the two images match.

### The six compartment traces: what separates them

Each compartment's trace has its own line style, and color is only a second
cue. Six traces share one plot, and a trace mistaken for another gives a wrong
clinical value.

| Compartment | Line style | Dash pattern (px) | Width (px) |
| --- | --- | --- | --- |
| Circuit | solid | — | 3 |
| Alveolar | long dash | 10 on, 4 off | 3 |
| Mixed venous | short dash | 4 on, 3 off | 2 |
| Vessel-rich | even dash | 6 on, 6 off | 2 |
| Muscle | dotted | 2 on, 3 off | 2 |
| Fat | dash-dot | 12 on, 4 off, 2 on, 4 off | 2 |

The legend entry beside each checkbox names its trace's style in words, so a
reader can learn every style from the legend alone.

**Color cannot be the first cue, because some pairs of trace colors are almost
equally bright.** The closest pairs are alveolar and muscle, circuit and
mixed venous, and, under protanopia, vessel-rich and fat. No other choice of colors fixes this. Each color has at least the 3:1
contrast against the panel that WCAG success criterion 1.4.11 requires, both as
displayed and as simulated for protanopia, deuteranopia and tritanopia. The
colors are chosen to label their compartment and to clear that minimum.

**The colors decide which line style goes on which compartment.** The two traces
whose colors are hardest to separate get styles that are easy to separate by
shape: alveolar's long dash against muscle's dots, and circuit's solid line
against mixed venous's short dash. Fat's dash-dot differs in dash length, gap
length and rhythm from both the vessel-rich even dash and the mixed venous short
dash, which is what tells fat from vessel-rich for a reader with protanopia. The one pair of styles that a reader could confuse is dotted, with 2 px
dots, and short dash, with 4 px dashes. That pair goes to muscle and mixed
venous, whose colors are 1.45 apart at worst, more than eleven of the fifteen
pairs in the table below.

**With two runs on the plot, at most two compartments are drawn** (`PL-HLD5`,
`PL-8PSW`). The cap applies to the plot only. All six readouts stay on screen for
both runs (§ "Minimum displayed outputs").

**Line width shows the run.** Each compartment keeps its line style and color.
The first run's traces are wider, and the second run's keep the width in the
table above. A reader compares the two widths only between the two traces of one
compartment, which are always adjacent. A branched run repeats its parent exactly
up to the branch point, where the two runs diverge (planned-milestone item 12).
Before that point the two traces of a compartment coincide, so the narrower one
is drawn on top, where the wider one cannot hide it.

**A solid vertical line marks a branch point, and a finely dashed one marks a
control change.** Both lines are the same color, so only their dash pattern and
the legend's words tell them apart. A reader must not confuse the two, because
reading a branch point as a control change would attribute the runs' divergence
to the wrong cause.

**For developers.** A script computes the pairwise ratios and the two ceilings
in this section, and checks each trace against the panel in all four vision
models (`tools/contrast_check.py`). A unit test checks the closest pair, the two
ceilings and the 3:1 minimum against these figures
(`tests/unit/test_contrast_check.py`). The script's `contrast_ratio` and
`as_seen` functions give the per-trace table and the figures for the two colors
before they were darkened, and no test checks those. The search over lightness
is not part of the script. The script runs as part of `make check`, and its
`--matrix` option prints the pairwise ratios in the table below.

Each trace has this contrast against the panel, as displayed (Normal) and as
simulated for each dichromacy:

| Trace | sRGB | Normal | Protanopia | Deuteranopia | Tritanopia |
| --- | --- | --- | --- | --- | --- |
| Circuit | `#176B87` | 6.02 | 5.67 | 6.21 | 6.02 |
| Alveolar | `#159789` | 3.61 | 3.23 | 3.84 | 3.63 |
| Mixed venous | `#7C3AED` | 5.70 | 5.96 | 4.68 | 5.55 |
| Vessel-rich | `#DC2626` | 4.83 | 7.18 | 4.14 | 4.84 |
| Muscle | `#D17206` | 3.43 | 3.96 | 3.22 | 3.46 |
| Fat | `#5D5510` | 7.57 | 7.51 | 7.63 | 7.62 |

The contrast between each pair of traces is far lower, and the design in this
section rests on it:

| Pair | Normal | Protanopia | Deuteranopia | Tritanopia | Worst |
| --- | --- | --- | --- | --- | --- |
| Vessel-rich / Fat | 1.57 | 1.05 | 1.84 | 1.57 | **1.05** |
| Alveolar / Muscle | 1.05 | 1.23 | 1.19 | 1.05 | **1.05** |
| Circuit / Mixed venous | 1.06 | 1.05 | 1.33 | 1.08 | **1.05** |
| Alveolar / Vessel-rich | 1.34 | 2.22 | 1.08 | 1.33 | **1.08** |
| Mixed venous / Vessel-rich | 1.18 | 1.20 | 1.13 | 1.15 | **1.13** |
| Alveolar / Mixed venous | 1.58 | 1.84 | 1.22 | 1.53 | **1.22** |
| Circuit / Fat | 1.26 | 1.33 | 1.23 | 1.27 | **1.23** |
| Circuit / Vessel-rich | 1.25 | 1.27 | 1.50 | 1.24 | **1.24** |
| Mixed venous / Fat | 1.33 | 1.26 | 1.63 | 1.37 | **1.26** |
| Vessel-rich / Muscle | 1.41 | 1.81 | 1.28 | 1.40 | **1.28** |
| Circuit / Muscle | 1.75 | 1.43 | 1.93 | 1.74 | **1.43** |
| Mixed venous / Muscle | 1.66 | 1.50 | 1.45 | 1.61 | **1.45** |
| Circuit / Alveolar | 1.67 | 1.75 | 1.62 | 1.66 | **1.62** |
| Muscle / Fat | 2.21 | 1.90 | 2.36 | 2.20 | **1.90** |
| Alveolar / Fat | 2.10 | 2.32 | 1.99 | 2.10 | **1.99** |

<!-- not-restated: 2.10 -->

Other colors would not help, because the closest pair among any six colors has a
contrast ceiling of $`21^{1/5}\approx1.84`$. Contrast ratios multiply along a
bounded scale: black to white is 21:1. With $`n`$ traces sorted by luminance, the
smallest gap between adjacent traces is largest when the gaps are equal. Requiring 3:1 against the white panel
caps each trace's luminance at 0.30, which lowers that ceiling to **1.48**. A
search over lightness, with each hue and saturation held fixed, reaches **1.28**
at best for the worst pair across the four vision models. It gets there only by
making four of the six traces nearly black, which loses the hue that lets a
reader name a trace. Even then, 1.28 is less than half of 3:1. A project rule
(`.claude/rules/ui-color.md`) records this result, so that the search is not
re-run each time a color changes.

Two colors were darkened to meet the 3:1 minimum against the panel, not to
improve separation. The alveolar trace was `#18A999`, at 2.93:1 as displayed
and 2.61:1 simulated for protanopia. The muscle trace was `#D97706`, at 3.19:1
as displayed and 2.98:1 simulated for deuteranopia. Each new color keeps the
old hue and saturation exactly, and is darkened to the lightest shade that
clears 3.2:1 in all four vision models. The extra 0.2 keeps the shipped color
off the 3:1 boundary. The $`F_A/F_I`$ wash-in plot takes its single line's
color from the alveolar trace's constant, so it had the same shortfall, and
darkening the alveolar color fixed it.

The dichromacy figures use Brettel, Viénot and Mollon's projection onto the
reduced stimulus surface that each dichromacy leaves. That surface is defined by
the neutral axis and by the monochromatic stimuli that a dichromat and a normal
trichromat see as the same hue.[^brettel1997] The simulation uses the
two-half-plane form, because the single-matrix simplification of Viénot,
Brettel and Mollon (1999) is not accurate for tritanopia.[^vienot1999] The
coefficients are the precomputed sRGB-space forms published by libDaltonLens,
which derives them from Brettel's construction over the Smith and Pokorny (1975)
cone fundamentals.[^daltonlens]

The figures support one comparative claim: no arrangement of these six colors
separates the traces, whichever observer is assumed. The figures have three
limits:

1. The simulation renders, for a normal observer, an approximation of a
   dichromat's *appearance*. It does not measure dichromatic perception. It
   models the three dichromacies, not the far commoner anomalous trichromacies,
   so it does not represent their milder losses.
2. The script applies WCAG's relative-luminance formula to the simulated output.
   The formula was not defined for that use, because success criterion 1.4.11 is
   written for the color the display emits.
3. The calculation concerns luminance only, so it says nothing about the
   difference in hue that a reader with normal color vision uses.

Color stays with the compartment when a second run is added, because a cue
whose meaning changed between one run and two would invite misreading a clinical
value.

Because the colors cannot separate the traces, width can show the run only under
a cap on the compartments drawn. The six compartments already use two widths,
2 px and 3 px, which sets the cap at two.

The first run is widened, rather than the second narrowed, so that no trace is
drawn narrower than 2 px. A 1 px antialiased line renders lighter than its color
and would fall below the 3:1 minimum against the panel that every trace must
meet.

[^brettel1997]: Brettel H, Viénot F, Mollon JD. Computerized simulation of
    color appearance for dichromats. J Opt Soc Am A. 1997;14(10):2647-2655.
    doi:10.1364/JOSAA.14.002647

[^vienot1999]: Viénot F, Brettel H, Mollon JD. Digital video colourmaps for
    checking the legibility of displays by dichromats. Color Res Appl.
    1999;24(4):243-252.
    doi:10.1002/(SICI)1520-6378(199908)24:4<243::AID-COL5>3.0.CO;2-3

[^daltonlens]: libDaltonLens, public domain, https://github.com/DaltonLens/libDaltonLens
    — coefficients and derivation, the latter written out at
    https://daltonlens.org/understanding-cvd-simulation/

### Displayed precision

#### What the concentration readouts show

In all six compartments, every modeled concentration and relative partial
pressure is displayed to **0.01 percentage points**. The delivered-agent
setting uses the same resolution, in the readout above its slider and in the
label shown while the slider is dragged, so the setting and the values it
produces are read at one scale. A positive value that would round to `0.00%`
is displayed as `<0.01%`, so `0.00%` means only that no agent has arrived, as
before a run starts.

Each digit shown is accurate for this model with its parameters. No displayed
value can be trusted to its last digit as a prediction about a patient
(`docs/MODEL.md` § "Known limitations").

**For developers.** One test enforces the display resolution
(`test_format_percent_uses_the_documented_display_resolution` in `tests/unit/test_formatting.py`), and another
enforces the `<0.01%` form
(`test_format_percent_marks_a_value_below_the_resolution` in `tests/unit/test_formatting.py`).

#### Why the readouts show two decimals

**The equation solver does not limit how many decimals a readout can show.** The
test that `docs/VERIFICATION.md` § "Independent-solution test" describes holds the
simulator's results to within $`4\times10^{-11}`$ percentage points of an
independently computed solution, in the runs that it covers. It holds them to within $`10^{-10}`$ percentage
points at one reference point held for an hour: 5% delivered, 4 L/min of fresh gas, and
the reference adult's default ventilation and cardiac output, checked at 60 s, 600 s and
3600 s. Those limits are $`4\times10^{-13}`$ and $`10^{-12}`$ as a
fraction. The larger is one hundred-millionth of the last displayed digit, so **a
third decimal would not be numerical noise.** Legibility sets the
number of decimals instead: the readouts show the coarsest resolution that keeps
every compartment's wash-in visible (below). How far the model's parameters vary
between patients does not set it (project owner, 2026-11-14, `PL-W51N`). That
spread is stated below as a limitation on reading a value as a patient's.
<!-- not-restated: 5 %, 4 L/min -->

**Two questions about resolution must be kept apart: how finely two moments
within one run can be told apart, and how finely this model resolves a
concentration in a patient.** Within a run the parameters are fixed and the
simulation is deterministic, so the answer to the first is about nine decimal
places finer than the readout shows. The second is the question that a clinician
reading a percent sign is asking, and its answer is much coarser.

**Between patients, one measured standard deviation of a partition coefficient
moves a readout by anything from a third of one count to ninety-nine counts of
the last displayed digit.** One count is 0.01 percentage points. When one stored coefficient is
changed by one published SD and the run is repeated at 1 MAC with the reference
adult's flows, the largest shift of any displayed reading in the first hour and
over the whole 24 h run is as follows
(`test_one_sd_of_each_coefficient_displaces_the_readouts_as_the_table_states`):
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

| Coefficient changed by one SD | The SD as a share of the mean | Largest shift in the first hour | Largest shift over 24 h |
| --- | --- | --- | --- |
| Blood:gas | 5.7% to 8.3% | 2.0×10⁻² to 9.0×10⁻² pp | 2.4×10⁻² to 1.3×10⁻¹ pp |
| Vessel-rich tissue:gas | 3.7% to 6.1% | 1.0×10⁻² to 5.4×10⁻² pp | 1.0×10⁻² to 5.4×10⁻² pp |
| Muscle tissue:gas | 37% to 45% | 1.5×10⁻¹ to 9.9×10⁻¹ pp | 2.1×10⁻¹ to 1.0 pp |
| Fat tissue:gas | 17% to 19% | 3.4×10⁻³ to 4.0×10⁻² pp | 7.4×10⁻² to 4.4×10⁻¹ pp |

<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- not-restated: 2.4, 2.1, 1.3 -->

Each range covers the three agents that the simulator offers, and desflurane
always gives the largest shift. A run of 24 h is the longest the simulator
supports.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

Each SD is the SD of the coefficient that the model stores. The tissue SDs are
from Yasuda, Targ and Eger's Table 1 of human tissue:gas coefficients at 37 °C
(Anesth Analg 1989;69:370-373, p. 371). The stored vessel-rich coefficient is
that table's brain value, so it takes the brain SD. The blood:gas SDs are
Eger's for desflurane ($`0.424 \pm 0.024`$), Strum and Eger's for sevoflurane
($`0.686 \pm 0.047`$), and Esper and colleagues' for isoflurane
($`1.45 \pm 0.12`$), the only adult SD for isoflurane that has been read. Each
run changes the coefficient by its SD as a share of the mean, upward and
downward, and keeps the larger shift.

So a reading can differ between two patients by many times its last digit. In
the first hour the muscle coefficient alone moves a reading by up to 99 counts.
Over a whole run the slow compartments fill further, and the blood:gas and fat
coefficients move a reading by up to 13 and 44 counts.

**The last digit separates two moments of one run, not two patients.** An SD
changes where the whole curve sits, not how finely two points on it can be told
apart. So the SD does not limit a reader who compares 09:14 with 09:16 of one
run, and it does not set the number of decimals. No displayed value is a
prediction for a patient (`docs/MODEL.md` § "Known limitations"), and the table
above measures how far a patient's value could lie from the one shown.

**Legibility sets the lower limit on decimals: one decimal hides the slow
compartments' wash-in, which is the reason for displaying them.** At one decimal
the sevoflurane and isoflurane fat fractions read `0.0%` for the whole hour
(0.029% and 0.014% at 3600 s). Desflurane's fat fraction stays at `0.0%` for its
first 17.9 minutes and reaches 0.2%. Muscle reads `0.0%` for its first 2.7
minutes with desflurane, 9.2 minutes with sevoflurane and 15.1 minutes with
isoflurane. At two decimals, at 1 MAC with default flows, muscle first shows a
nonzero value at 55, 133 and 194 seconds and fat at 224, 845 and 1507 seconds,
for desflurane, sevoflurane and isoflurane in that order. Three tests check
these figures against the model, all in
`tests/reference/test_displayed_precision_figures.py`:
`test_the_fat_fractions_at_one_hour_match_the_model`,
`test_the_one_decimal_erasure_times_match_the_model` and
`test_the_first_nonzero_two_decimal_readings_match_the_model`.

This lower limit is the project owner's teaching judgment, not a property of the
model: the solver supports one decimal comfortably. One
decimal is ruled out because a simulator built to show uptake and distribution
would then show a flat zero where the uptake is happening.

**Two decimals is the chosen count**, because it is the coarsest that keeps
every compartment legible. The readouts show no finer resolution than that
needs. Moving the readout to one decimal would change what a reader sees and
which settings a slider can reach, but nothing in the model's equations.

**Why not the 0.1 percentage points that agent monitors show.** Agent monitors
display end-tidal and inspired concentrations to a tenth of a percentage point,
which would suit the circuit and alveolar readouts. This simulator also displays
compartments that no monitor shows, and at one decimal fat and muscle read `0.0%`
for the times given under the lower limit above, which
`test_the_one_decimal_erasure_times_match_the_model` checks. A resolution of
0.01 percentage points is the coarsest that keeps every displayed compartment
legible.

**Why not significant figures.** A significant-figures rule would give the six
readouts different numbers of decimal places, and the row is read by comparing
them (§ "One resolution for all six readouts"). It would also give the smallest
values the most digits: three figures on a fat fraction of a thousandth of a
percent would print five decimals. The equation solver is not the limit here.
In a sevoflurane run at the default settings, the venous blood and the three
tissue groups read `<0.01%` for the whole of the first ten seconds. The
simulator's values for these compartments differ from the same equations solved
to 50 significant digits by less than $`10^{-13}`$ of each value. That
difference is the rounding of double-precision arithmetic, which builds up over
the steps. `tests/reference/test_solver_error_figures.py` checks the bound.

**Why a value below the resolution is shown as `<0.01%` rather than as zero.**
Even at two decimals, muscle and fat start below the last digit, for the times
given under the lower limit above. Showing `0.00%` then would state that the compartment
holds no agent, which the model does not say. The model says that the
compartment is filling, below what the display resolves, and `<0.01%` states
exactly that. The display marks what it cannot show, rather than adding a decimal
that the model cannot support.

A negative value is never shown as `<0.01%`, where it would pass for a plausible
small positive reading. The model cannot hold a negative concentration
(`docs/VERIFICATION.md` § "Concentrations"), so a negative value that reaches the display means that
something upstream is wrong, and the display refuses it.

**For developers.** The readout's decimal count must not feed back into the
model, and nothing in the `core/` directory reads it. The simulation
step (`SIMULATION_STEP_S`) is a tolerance in seconds. Three of the four supported
input ranges are intervals in L/min, and the fourth, the delivered concentration,
is an interval in percent. Both are derived without reference to the
readout, in `docs/VERIFICATION.md` § "Supported simulation step" and `docs/INTERFACE.md` § "Supported input ranges". A
future change to one decimal has to answer the objection to it given under the
lower limit above. The negative concentrations that the model cannot hold
include minus zero (`docs/VERIFICATION.md` § "Concentrations"). No value of the `Fraction` type can be
negative, and the formatter is the code that refuses a negative value.

One test module holds every figure in this section that
comes from changing a coefficient by one SD
(`tests/integration/test_parameter_uncertainty.py`). The table and its ordering
are held by
`test_one_sd_of_each_coefficient_displaces_the_readouts_as_the_table_states`,
the SDs by `test_the_relative_sds_are_those_the_section_states`, and the range
of a third of a count to ninety-nine counts by
`test_one_sd_is_a_third_of_a_count_to_ninety_nine_counts_of_the_last_digit`. The
whole-run counts of 13 and 44 are the table's last column in counts.
`test_each_tissue_coefficient_s_sd_is_the_sd_of_the_coefficient_the_model_stores`
fails if an SD is taken from a row whose mean the stored coefficient does not
match, as the brain:blood SDs were.

#### The MAC multiple's resolution

**The MAC readout shows the MAC multiple in steps of 0.01 MAC.** One step is 0.018
percentage points of sevoflurane, 0.0117 of isoflurane and 0.066 of desflurane. Each is
at least the percent readout's 0.01 percentage points, because the MAC multiple is
calculated from the percent concentration and can be no more precise than it. The two
readouts round separately, so the MAC readout can occasionally change while the percent
readout stays the same.
`test_the_mac_step_in_percentage_points_matches_each_stored_mac` in `tests/reference/test_displayed_precision_figures.py` checks the three
per-agent figures against each agent's stored MAC.

A MAC multiple above zero that rounds to `0.00 ×MAC` shows as `<0.01 ×MAC`. The `<` sign
matters more on the MAC readout than on the percent readout, because a filling
compartment reaches 0.01 percentage points before it reaches 0.01 MAC. In between,
`0.00 ×MAC` would contradict the percent readout above it, which already shows the
compartment filling.

**For developers.**
The MAC resolution is derived from the percent resolution rather than stored beside
it, so that re-measuring the percent resolution never leaves a second number to
update. Divided by the agent's MAC in percent (`mac_at_age_40_percent`), 0.01
percentage points is 0.0056 MAC for sevoflurane, 0.0085 for isoflurane and 0.0015 for
desflurane. The MAC resolution is the finest power of ten at or above the coarsest of
these, isoflurane's 0.0085. A test repeats this arithmetic for every shipped agent
(`test_the_mac_resolution_is_derived_from_the_percent_resolution` in `tests/unit/test_formatting.py`) and fails if
adding an agent or changing the percent resolution would make the MAC readout finer
than the percent readout supports. Another test checks the `<0.01 ×MAC` form
(`test_format_mac_multiple_marks_a_value_below_the_resolution` in `tests/unit/test_formatting.py`).

#### What the model keeps that the display rounds

**Only the display rounds a value, and only once.** The model computes and keeps
every value at full precision, including the values the chart is drawn from. A
slider's value reaches the model without rounding. The readout is the only place
between a slider and a pixel where resolution is lost. The model keeps about
nine orders of magnitude more precision than the display shows.

**For developers.** Everything upstream of the formatter carries full binary64
precision: the compartment states, every integration step, the mixed-venous and
tissue transfers, and the states the chart is drawn from (`DrawnWindow`). Nothing
in the model's code (`core/`) rounds. The snapshot fields that the interface
reads are raw fractions. The figure of nine orders of magnitude applies to the
exact method that the simulator uses. A test runs the model twice, with delivered
concentrations that differ by an amount four orders of magnitude smaller than
the display resolution (`test_the_model_keeps_precision_the_display_throws_away` in `tests/unit/test_formatting.py`).
The two runs must reach different states and must still look identical on the
display.

#### Comparing two readouts

**A reader can rely on which of two compartments the readout row shows as higher,
except possibly while the two are almost equal, as when they cross.** The interface therefore adds no warning or
marker when readouts are compared. Where seven panels fit, the six compartment readouts
and the clock sit in one row, so that the readouts can be read *in order*: the circuit
leads the alveoli, and the alveoli lead the tissues.
§ "How the readout row fits the window's width" below says what happens when seven panels do not
fit.

When a reader compares two readouts, the simulator's calculation error could mislead them
only by reversing which of the two is shown as higher. Rounding to a fixed number of
decimals never reverses the order of two values, so the display can show two compartments
in the wrong order only where the simulator and the exact solution put them in
opposite order. Such a reversal needs a true gap smaller than the two compartments'
calculation errors added together. How large each error can be depends on the run:

1. In the runs that the test in `docs/VERIFICATION.md` § "Independent-solution test"
   covers, each compartment's calculation error is at most $`4\times10^{-13}`$ as a
   fraction, not a percent. Those runs are five scripted runs of 600 s to 900 s and nine
   random runs of 600 s. A reversal in them needs a true gap below $`8\times10^{-13}`$.
2. In the reference run held for an hour, the same section allows $`10^{-12}`$.
3. **No test bounds the calculation error in a learner's own session.** The derived
   bound for the longest session the simulator allows, 24 h of one-second steps, is
   $`1.5\times10^{-9}`$ of the largest fraction in the run (`run_rounding` in
   `src/anesthesia_sim/core/rounding.py`). At desflurane's vaporizer maximum of 18%,
   that is less than $`3\times10^{-8}`$ percentage points.
<!-- not-restated: 900 s -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->

All three are more than five orders of magnitude below the readout's resolution of 0.01
percentage points. A true gap that small occurs only where two compartments are almost
equal. That happens in the moment when two compartments cross. It also happens where two
compartments converge on the same value, such as the circuit and the alveoli approaching
the delivered fraction when cardiac output is zero. A reversal is arithmetically possible
there and nowhere else. The first two limits hold on any computer on which that
section's test passes.

**A gap that a reader works out from two readings can differ from the true gap by
up to one count of the last displayed digit.** Each reading is rounded to that
digit. The gap carries the rounding of both readings and the simulator's calculation
error, up to the limits listed above. That calculation error does not make the
gap less accurate than either reading. The interface shows no gap between two readouts.

**For developers.** Two tests enforce the claim about which compartment is shown
as higher. Each covers one half of the path from the model to the readout and can
fail on its own. The first bounds the simulator's calculation error against the
independent solution
(`test_exact_step_matches_the_independent_solution_everywhere` in `tests/reference/test_coupled_dynamics.py`). The second checks
that the interface's formatter, `format_percent`, never shows a higher fraction as
a lower percent (`test_format_percent_preserves_order` in
`tests/unit/test_formatting.py`). It covers the "<0.01%" reading below the display
resolution and both sides of every value at which the last displayed digit changes.
Together the two tests mean that, in the runs that the first test covers, no reversal
can occur at a true gap above twice the first test's tolerance: $`8.0\times10^{-9}`$ counts of the last displayed digit. A
third test compares every pair of the six readouts at every time step, for all three
agents, in every run of the first test, reading each value through the
interface's formatter (`test_displayed_ordering_reverses_only_at_a_crossing` in `tests/reference/test_coupled_dynamics.py`). It
allows a reversal where the true gap is below the first two tests' threshold of
$`8.0\times10^{-9}`$ counts, because one is possible where two compartments are almost
equal. It fails only when
one of those tests fails, so it adds no evidence of its own.

The claim about a gap's calculation error rests on one property of the model: within one
time step, it updates every compartment from the values at the start of that step.

#### One resolution for all six readouts

**All six compartment readouts show the same number of decimal places, because
they are compared with one another.** If they showed different numbers of
decimal places, digits of different place value would sit in the same position,
and someone scanning the row would misjudge a value by a factor of ten. This
reason comes from how the row is read, so it applies however the simulator
computes the values.

**For developers.** The six readouts share one formatter, whose resolution is
checked by `test_format_percent_uses_the_documented_display_resolution` in
`tests/unit/test_formatting.py`.

#### How the readout row fits the window's width

**The readout row's width decides how many panels share a line.** Every panel
takes exactly one column. The panels sit seven across wherever all seven columns
fit the row, four per line where they do not, two where four do not fit, and one
below that. Each column is at least as wide as the widest line its panel can
show. Those lines are the panel's name, the gloss under its name, and its
widest value, which is the clock's longest elapsed time or a compartment's
widest percent and MAC multiple. The clock therefore widens no other column.
In every arrangement each
panel keeps that width, so no value is wrapped away from its unit. The widths at
which the row steps down depend on the font and the display scale. With the font
that the project's tests use, for example, the row is seven across from 985 px,
four across from 571 px and two across from 290 px (measured 2026-11-22). Those
figures illustrate the rule and do not specify it.

When fewer panels share a line, both reasons given above for the row still
apply, but not equally.

- **Reading the row in order becomes harder.** The six readouts other than the
  clock then sit on two or more lines, so comparing them takes a scan across the
  lines instead of a single glance. The readouts' ordering is still faithful,
  because it depends on the displayed values, not on where they sit.
- **The uniform resolution still applies at every width.** The grid aligns the
  values within each column, so a reader compares two panels against a common
  position, whether they sit side by side or stacked.

**The row's width follows the window, never the layout below it.** The readouts
sit in a region above the part of the window that the reader divides into Areas
(§ "Minimum displayed outputs" -> "What this list requires once the layout is
the reader's"). The row's width therefore stays the same when the reader splits
or joins an Area, drags a border or switches Workspace. Only two things change
it: the window's width, and how the region divides that width between the
readouts and the control-change record.

**The window opens maximized, so the row starts in the widest arrangement that
the screen allows.** Maximized is not full screen: the title bar and window
controls stay, and on macOS the window is zoomed. A maximized window gives the
region the screen's available width less the window's frame. A reader who
un-maximizes the window returns it to its normal size: a fixed fraction of the
screen's available area, centred. At that size the row steps down wherever its
width requires. On a screen too narrow for seven across even when maximized,
the row opens in a narrower arrangement, because maximizing changes the row's
width, never the rule that picks the arrangement.

**On a 1366 px laptop screen, one of the commonest widths, the row opens seven
across, with one run or two** (measured 2026-10-18). In compare mode the two
runs share one readout row. On that screen the longest control-change lines do
not fit the record's column, so the record wraps them. It breaks them only after
the time or after the arrow, so every value stays beside its unit.

**In a window 1280 px wide the row opens seven across with some fonts and four
across with others, with one run or two** (measured 2026-11-14). At that width
the row is within a few pixels of what seven across needs, so the font decides.
With four across, the readouts take two lines. A window frame or a dock at the
side of the screen narrows the row further. The record wraps its lines at this
width too. It narrows further when the row of run controls above the readouts
needs more room, for example for a long version label, and it can then cut off
the end of its longest lines (`PL-6XPZ`).

**For developers.** A function sets the row's column count from its width
(`readout_columns` in `src/anesthesia_sim/app/dashboard_frame.py`). A constant
lists the four arrangements (`READOUT_ROW_LADDER`). Column widths come from the
font that the interface draws with, so the code fixes no pixel width that
another font or display scale would make wrong. The step-down widths above are
in logical pixels, for the tests' offscreen font. One test reads those widths
from the row instead of asserting them
(`test_the_readout_row_reflows_where_its_panels_stop_fitting` in `tests/integration/test_qt_widgets.py`). Another enforces
the column count and each panel's one-column span
(`test_every_readout_reserves_a_qualifier_line_and_an_equal_column` in `tests/integration/test_qt_widgets.py`).

A test checks that the readouts' region stays outside the Areas
(`test_no_unconditional_value_sits_inside_the_layout_container` in `tests/integration/simulation_view/test_simulation_view_branch_display.py`). The region
(`SimulationView.unconditional_region`) gives 0.82 of its width to a left column
for the readouts and 0.18 to a right column for the control-change record. These
are the shares that the chart panel's Area and the sidebar's Area had in the
layout that the dashboard first opened on. In that layout the record was as wide
as the sidebar beneath it. The Workspaces that ship now divide the width
differently, and the region keeps its own shares. The left column never narrows
below its minimum width.
<!-- not-restated: 0.18 -->

The window is opened maximized (`showMaximized()` in
`src/anesthesia_sim/app/main.py`). A constant in
`src/anesthesia_sim/app/qt_widgets.py` gives the
window's normal size as a fraction of the screen's available area
(`WINDOW_SCREEN_FRACTION`). Opening maximized matches the default window state of
the reference design that the interface follows (`docs/interface-provenance.md`
§ "Adopted").

With the tests' font, a 1366 px window gives the region 1334 px (measured
2026-11-14). The right column takes 238 px and the left column 1084 px, which is
99 px more than the 985 px that seven across needs (measured 2026-11-22). Two tests check that a
1366 px window opens the row seven across, with one run and in compare mode
(`test_a_1366_px_window_opens_one_run_s_readout_row_on_seven_columns` and
`test_two_runs_share_one_readout_block_whose_values_name_their_runs` in `tests/integration/simulation_view/test_simulation_view_readouts.py`). A 1280 px
window gives the region 1248 px. The left column takes at least its share,
1014 px. With the font in the container where the tests were written, that is
29 px more than seven across needs (measured 2026-11-22). With the font on the
CI runner, seven across needed 1068 px on 2026-11-14 and the row got 1060 px, so
it opened on four. The clock's widest reading was then `23h59m59.9s`. It is now
`23h59m59s`, which narrows the clock's column by 20 px with the tests' font, so
the row on the CI runner may now open seven across. Two tests check that a 1280 px window opens the row seven across
where seven fit and four across otherwise, with one run and with two
(`test_a_1280_px_window_opens_one_run_s_readout_row_on_seven_or_four_columns`
and
`test_a_1280_px_window_opens_two_compared_runs_readout_row_on_seven_or_four_columns` in `tests/integration/simulation_view/test_simulation_view_readouts.py`).
The left
column cannot narrow below the transport row's minimum width, which includes
the version label. So below about 1366 px a longer version string widens the
left column and narrows the record (`PL-6XPZ`). A function wraps the
control-change record (`wrapping_between_parts`).

#### Time, flows and the chart

**Simulated time is displayed in whole seconds, and one simulation step is
exactly 1 s.**
Every recorded control change is stamped at that same resolution, so the
timeline and the clock never show one time in two different forms.
<!-- provenance: core/simulation_step.py SIMULATION_STEP_S = 1 -->

The screen shows time in one form. The displayed clock, the time stamp on each
recorded control change and the chart's axis ticks are all durations. Each part
of a duration carries its own unit: `45s`, `1m30s`, `1h23m45s`, `24h`. A part
that is zero is left out. No part carries a fraction of a second, because a run
stands only on whole seconds and every tick that the time axis can place falls
on one.

There are two exceptions, and both are written out in words. One is the time
span that the chart draws, such as `15 minutes` above an axis whose last tick
reads `15m`. The reader picks that phrase from a selector and sees it again in
a caption. The other is the supported run length in the notice that stops a
run at it, `24 hours`.
§ "Displayed precision" sets the precision at which each form is shown.
§ "The chart's time base" explains the time-axis label form, why it differs
from the clock's, and why the span is written in words.

The clock and the stamps use the time axis's form
because all three are on screen together. A control mark stamped `5400 s` on
an axis reading `1h30m` would leave the reader to convert between the two by
hand. At the supported 24-hour run length, a clock in seconds would read
`86400 s`, a count of seconds for a limit that this document states
in hours. A stamp names a whole second, so it identifies the
simulation step (`SIMULATION_STEP_S`) at which it was taken. The span's wording does not have to
fit in a tick's width, because neither the selector nor the caption is a tick
label.

**Fresh gas flow, alveolar ventilation and cardiac output are displayed to
0.1 L/min**, the resolution of the controls that set them. A slider and the
readout above it show one quantity, so each slider moves in steps of its
display resolution: 0.1 L/min for the three flows and 0.01 percentage points
for the delivered dial. The value applied to the model is exactly the value
printed above the control. If a control could apply a value that its own label
rounds away, a reader could not tell which value is the setting in force.

**The chart is read for shape, so its resolution is coarser than the
readouts'.** It plots the same percentages on a shared linear axis that runs
from 0 to the top the reader chose, 3 ×MAC of the agent in use unless the
reader changes it, and a second axis on the right shows the
same position in MAC multiples. Its resolution is set by pixels rather than by
decimals. Every number that the chart offers is shown at the resolutions that § "Why the readouts show two decimals" and
§ "The MAC multiple's resolution" set,
in the readout row and in the hover readout
(§ "The chart's hover readout: what the tooltip may show", below). Because
the range is set in MAC, the MAC axis has the same round labels for every agent
at a given top, so a gridline that a reader learns under one agent means the
same thing under the next. § "The chart's fixed MAC axis" above explains the
range. The reader selects the time span that the chart's width
covers, and so chooses the seconds per pixel (§ "The chart's time base").
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

**For developers.** The sliders are integer-valued. Three tests read each flow's resolution from
its control's label (`test_fresh_gas_flow_slider_forwards_value_to_controller`,
`test_alveolar_ventilation_slider_forwards_value_to_controller` and
`test_cardiac_output_slider_forwards_value_to_controller` in `tests/integration/simulation_view/test_simulation_view_controls.py`), and a fourth
enforces the slider steps (`test_the_slider_steps_at_the_display_resolution` in `tests/integration/test_qt_widgets.py`).
Those steps come from the number of decimals displayed for concentration and
for flow (`CONCENTRATION_DISPLAY_DECIMALS` and `FLOW_DISPLAY_DECIMALS`), so
those two counts decide which settings can reach the model. A change to either
decimal count is therefore derived in this section first. The code in
`app/wash_in.py` computes a limit from the concentration resolution: the
smallest inspired fraction from which an F_A/F_I ratio may be formed
(`WASH_IN_DENOMINATOR_FLOOR_FRACTION`, § "F_A/F_I as a displayed ratio").
Because the limit follows from that resolution, each extra decimal of
concentration moves it down tenfold.

#### The agent-accounting panel

**The panel's three amounts are displayed to 0.1 L, and its residual line shows
only the power of ten that the residual lies below, because they answer different
questions** (decided 2026-09-15). The amounts are read against each other, delivered
against exhausted plus stored, and against a reader's sense of scale. The residual
line is a numerical check. They have to make a residual of order 10⁻¹² L visible
against amounts of order 1 to 100 L, which no fixed decimal count can do.

The panel labels the unit as litres of equivalent pure agent gas, the unit this
document uses, because a bare "L" beside an anaesthetic agent invites a reader
to take it as litres of liquid. The label also names the reference condition of
`docs/MODEL.md` § "Agent amount", and says that the amounts held in the body
read high at it (`docs/MODEL.md` § "Units and symbols").

**A run total is shown in steps of 0.1 L, and can differ between patients by
many steps.** As with the readouts, the spread between patients does not set the
step (project owner, 2026-11-14, `PL-W51N`). Changing one of the coefficients
by its published SD (§ "Why the readouts show two decimals") shifts the
exhausted total. At 1 MAC with the reference adult's flows, after 1 h and at
24 h, the longest run the simulator supports, the largest shifts are 0.030 and
0.55 L for sevoflurane, 0.025 and 0.61 L for isoflurane, and 0.097 and 0.74 L
for desflurane. At each agent's dial maximum with 10 L/min they are 0.17 and
2.5 L, 0.16 and 2.8 L, and 0.32 and 2.1 L. The muscle coefficient gives the
largest shift in every case. So after 24 h at a dial maximum an exhausted or
stored total could differ between patients by 21 to 28 steps. Delivered agent
carries no parameter uncertainty,
because it is the dial setting times the flow times the time. It is still
displayed to 0.1 L, so that the three amounts read at one scale.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- not-restated: 2.5 L -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**A residual line shows the power of ten that the residual is less than, such
as `<10⁻¹³ L`.** The exponent is written in superscript digits rather than in
e-notation. The `<` means the same as it does on the amounts. A residual of exactly
zero reads `0 L`. A residual that passes its check is the rounding left over from
summing the initial, delivered, exhausted and stored amounts. Its digits and its
sign are set by the order in which the arithmetic ran, not by anything modelled.
They change even when a correct edit to the code alters only the last binary digits of that
arithmetic, so the line shows neither. The panel shows the residual once, as
"Unaccounted". An absolute-error line would read the same string without a sign,
so the panel has none (project owner, 2026-10-03, ratified, over keeping both
lines and over keeping "Absolute error" instead). The sign means something only
in a check that fails. The run then halts, and the
failure log records the signed unaccounted amount with six decimal places, such
as `1.000000e+00 L`, for a developer. The banner does not show it.

**For developers.** At 1 MAC with the reference adult's flows, one 0.1 L step is
worth between about four SDs, for isoflurane at 1 h, and a seventh of an SD, for
desflurane at 24 h. At each agent's dial maximum with 10 L/min it falls to a
twenty-first to a twenty-eighth of an SD at 24 h.
`test_the_run_totals_litre_step_at_each_agent_s_dial_maximum` in `tests/integration/test_parameter_uncertainty.py` computes every
shift in this subsection. A constant stores the amounts' decimal count (`AGENT_AMOUNT_DISPLAY_PRECISION`),
a function formats them (`format_agent_volume`), and a test checks both
(`test_agent_amounts_precision` in `tests/unit/test_formatting.py`).
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The residual line's form rests on simulated runs compared on 2026-10-03. The 81
runs covered three agents, three pairs of dial settings, three cardiac outputs and
three fresh gas flows. Each was forked at minute 30 with the dial set back, and its
branch was played for 30 minutes. All 81 were replayed on the v0.5.21 tag and on
v0.5.22, before and after a change to the propagator's arithmetic that left each
run's own path bit-identical. Between the two versions, a branch's residual changed
by a factor of up to 5.9. Of 2,511 branch samples, the two versions' residuals read
differently at four significant digits on 1,975, at two on 634, at one on 154, and
at the power of ten on 22. Those 22 are the samples where the two residuals fell on
either side of a power of ten. The largest residual was 2.13 × 10⁻¹¹ L in both
versions, every check passed in both, and each run's own path read identically in
every form.

The residual line's power of ten is computed from the residual's exact
floating-point value. A function formats the line (`format_agent_residual`), and
four tests in `tests/unit/test_formatting.py` check it:
`test_format_agent_residual_prints_the_power_of_ten_it_lies_below`,
`test_format_agent_residual_drops_the_sign_the_rounding_chose`,
`test_format_agent_residual_bound_is_strict_and_tight_at_every_power_of_ten` and
`test_format_agent_residual_reads_zero_as_zero`. A fifth test uses the pair
`5.601e-14 L` and `5.609e-14 L`, which the two versions printed for one sample
(`test_format_agent_residual_prints_no_digit_a_last_bit_change_redraws`, in the same file).

#### Agent amounts in millilitres, and the cost

**An agent amount's precision is derived for the amount in one unit, and does
not carry over to another unit.** The derivation in § "The agent-accounting panel" is for litres of vapour.
The agent cost display shows the delivered total in millilitres of liquid, and
the compartment schematic shows each compartment's amount in millilitres of
vapour, so each of those needs its own precision. An amount in a unit that has
no derivation is refused, rather than shown at a default.

The bound is one-sided. It limits only how fine an amount may be shown. A coarser
precision loses detail but claims nothing false. A finer one claims a resolution
that the measured density or the conversion does not support, so it is refused rather
than quietly reduced to the derived precision.

| Amount | Unit | Decimals | Resolution | Derived from |
| --- | --- | --- | --- | --- |
| A run total: delivered, exhausted or stored | Litres of vapour | 1 | 0.1 L | Kept as shipped, `PL-W51N`, above |
| The delivered total | Millilitres of liquid | 0 | 1 mL | One SD of the measured liquid density |
| The exhausted total | Millilitres of liquid | 0 | 1 mL | The litre's resolution, converted |
| The stored total | Millilitres of liquid | Refused | - | The conversion reads a store 5.8% high |
| One compartment's amount | Millilitres of vapour | Two significant figures, none finer than 0.01 mL | 1% to 10% of the amount | The amounts' range, below |
| One compartment's share of the agent held | Percent of the stored total | 0 | 1 percentage point | Kept as shipped, `PL-W51N`, below |
<!-- derived: 5.8% from core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->

**The delivered total in millilitres of liquid is shown in whole millilitres.**
The delivered agent is the dial times the flow times the time, and its
conversion to liquid at the 20 °C reference is exact. Its only uncertainty in
liquid is the measured density's, which grows in proportion to the total. At
sevoflurane's largest supported total, 8% at 10 L/min for 24 h, one SD is about
3.3 mL. So a step of 1 mL is about 0.3 SD. No supported setting makes it finer
than a seventh of the density's SD, the finest step that the choice of whole
millilitres accepted (`PL-SP6H`). A step of 0.1 mL would be about a
thirtieth.
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->

**A cost is shown as money, to its currency's minor unit.** USD 12.34 reads
`USD 12.34` and USD 123.454 reads `USD 123.45`. The count of decimals is the
one that the Unicode CLDR's currency data gives each currency, which it bases
on the minor unit that ISO 4217 lists: two for USD and EUR, none for JPY and
three for KWD. A code that CLDR does not list gets CLDR's default of two
(Unicode Technical Standard #35, Part 3, Numbers, section "Currency Fraction
Digits and Rounding", https://www.unicode.org/reports/tr35/tr35-numbers.html). A cost
is not a value that patient care depends on, and a price is read to the cent,
so the liquid density's uncertainty does not set its precision. A positive
cost that would round to zero reads `USD <0.01` or `JPY <1`, and a run that has
delivered nothing reads `USD 0.00`. The digits are not grouped in thousands,
because the separator differs between regions, and in many a comma is the
decimal point.

**A price per millilitre is shown to four significant figures**, such as
`USD 0.2047 per mL of liquid`. Most prices per millilitre are less than one
unit of the currency, so a price rounded to the cent would lose most of its
figures. At four figures, rounding moves the price by at most 0.05 %. The
liquid volume is shown in whole millilitres, so a reader who multiplies the
volume by the price will not always get the cost, and the readout says that
the figures are rounded (§ "A cost at the reader's price").

**The exhausted total in millilitres of liquid has a precision of whole
millilitres, and no View shows it in that unit yet.**
It carries the partition coefficients' uncertainty, so it must not claim a finer
resolution in liquid than in litres of vapour. Otherwise a reader who could switch
the unit would see the model resolve a difference in one unit that it does not
resolve in the other. One step of the litre display, 0.1 L of vapour, is
0.55 mL of sevoflurane liquid, 0.51 mL of isoflurane and 0.48 mL of desflurane
at the 20 °C reference of `docs/MODEL.md` § "Agent amount". The smallest power of ten at or
above all three is 1 mL. For scale, at 1 MAC with the reference adult's flows, the one-SD shifts
at 24 h given in § "The agent-accounting panel", 0.55 L of sevoflurane vapour, 0.61 L of
isoflurane and 0.74 L of
desflurane, are 3.0, 3.1 and 3.5 mL of liquid. So at those settings one step of
1 mL is about a third of an SD, and a step of 0.1 mL would be about a thirtieth.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->

**The stored total has no precision in millilitres of liquid, and is refused in
that unit.** A store converted to liquid reads 5.8% high (`docs/MODEL.md` § "Units and symbols").
That error grows with the amount. At 17 mL of liquid it is already a whole step
of 1 mL, and in a long run it is several steps. No number of decimals can make a
figure with a known bias of several steps read correctly, so the stored total
keeps litres of vapour, as the accounting panel shows it.
<!-- derived: 5.8% from core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->
<!-- derived: 17 mL from core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->

The agent cost display is the only part of the simulator that converts an amount
to liquid. It converts only the delivered agent, so no figure it shows carries
the 5.8 % error. It reads the delivered amount and the vapour-to-liquid ratio of
the agent in use from the same moment of the run, so it cannot pair one agent's
vapour with another agent's ratio. Using desflurane's ratio would misstate
sevoflurane by about 13 %.
<!-- derived: 5.8 % from core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->

**The simulator derives each agent's vapour-to-liquid ratio, as the first table
in `docs/PARAMETERS.md` § "Agent amount" does.** It stores the liquid density and the molar mass,
each with its source, and the temperature at which the density was measured. It
refuses to load a density measured at any temperature other than 20 °C, because
it has no temperature correction. It computes the molar volume from the gas
constant, 20 °C and one standard atmosphere. Neither the molar volume nor the
published constants are stored.
<!-- provenance: core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->

A test checks the derived ratios against Biro's within 1 % and against Gas
Man's within 0.5 %. It also computes the cost of the isoflurane delivered in
the Gas Man Workbook's Exercises 14-1 and 14-2 with the derived ratio. Those
costs must match the book's, allowing for rounding to the cent and for Gas
Man's constant, which is rounded to a whole millilitre.

**For developers.** Four tests in `tests/unit/test_formatting.py` check the
liquid amounts. One repeats the litre-to-millilitre conversion for every
shipped agent from the stored molar mass and density
(`test_the_exhausted_total_in_millilitres_of_liquid_claims_no_more_than_in_litres`).
Another computes each agent's largest supported total and its SD from the stored
densities
(`test_the_delivered_total_in_millilitres_of_liquid_is_shown_in_whole_millilitres`).
A third holds the price per millilitre's four figures to the 0.05 % bound
above
(`test_four_figures_keep_the_price_per_millilitre_within_a_twentieth_of_a_percent`),
and `test_a_cost_is_shown_to_its_currency_s_minor_unit` checks a cost's decimals
in USD, JPY, KWD and a code CLDR does not list.
A fourth checks that the stored total is refused in liquid
(`test_a_unit_with_no_derived_precision_is_refused`). Whole millilitres replaced a tenth on
2026-11-04 (project owner, ratified, over keeping the tenth and over four
significant figures, `PL-SP6H`).
Each agent's file in `data/agents/` stores the density, with its SD and
measurement temperature, as `liquid_density`, and the molar mass as
`molar_mass_g_mol`. The density's source entry (`sources`) is a tier-1
measurement. The molar mass's entry says why no tier-1 source
(`docs/PARAMETERS.md` § "Source hierarchy") exists. The vapor-to-liquid ratio is derived in
`core/liquid_agent.py` and checked against Biro's and Gas Man's constants in
`tests/reference/test_published_vapour_to_liquid.py`
(`test_the_derived_ratio_is_within_one_percent_of_biros_published_constant` and
`test_the_derived_ratio_is_within_half_a_percent_of_gas_mans_20_celsius_constant`).
The agent cost display reads the amount and the ratio from one snapshot of the
run (`SimulationSnapshot.agent_vapour_per_liquid`). A unit test fails if any
other code under `src/` calls the conversion to liquid (`liquid_volume_ml`).

One table in `app/formatting.py` gives the precision for each run total in each
unit where the precision is a number of decimals
(`AGENT_AMOUNT_DISPLAY_PRECISION`). A compartment's amount, its share and the
price per millilitre have precisions that are not a number of decimals of one
unit. Each is held in constants of its own beside its formatter
(`COMPARTMENT_AMOUNT_SIGNIFICANT_FIGURES`, `COMPARTMENT_AMOUNT_FINEST_DECIMALS`,
`COMPARTMENT_SHARE_DECIMALS`, `PRICE_PER_LIQUID_ML_SIGNIFICANT_FIGURES`). A
cost's count of decimals comes from its currency, through `minor_unit_decimals`
in `app/currency_code.py`, and
`test_a_cost_is_shown_to_its_currency_s_minor_unit` checks it. The table
refuses a compartment's amount in every unit. Each entry of the table
(`AgentAmountPrecision`) holds the amount, the unit and the precision shown. It
reads the finest precision from the derivation for that amount and unit, so no
caller can pass a looser limit. It refuses a finer precision when it is built.
A precision that a reader could set would be built the same way. Concentration,
flow, MAC multiples and the F_A/F_I ratio are each shown in one unit, so each
keeps one precision. If a reader is ever given a choice of unit for one of
them, its precision moves into a table like the one for agent amounts.

#### A compartment's amount and share on the schematic

**A compartment's amount is shown to two significant figures, in millilitres of
vapour, because the amounts span from a fraction of a millilitre to several
litres.** Two figures give every label of 0.10 mL or more the same relative
step, 1% to 10% of the amount
(`test_a_compartment_s_amount_is_shown_to_two_figures_and_no_finer_than_0_01_ml`).
A smaller amount is shown in steps of 0.01 mL, which is coarser. A positive
amount that would round to 0.00 mL reads `<0.01 mL vapour`,
and exactly zero reads `0 mL vapour`.

**Between patients, one SD of a partition coefficient shifts a compartment's
amount by a share of it, not by a fixed volume.** Runs that change each of the four
stored coefficients in turn by one published SD (§ "Why the readouts show two
decimals"), at 1 MAC with the reference adult's flows, were read every second
for the first 20 minutes and then every minute to 24 h. The largest shift, as a
share of the amount, is 3.4% in the circuit, 8.3% in the alveoli, 17% in venous
blood, 8.3% in the vessel-rich group, 44% in muscle and 8.2% in fat. The circuit
and the alveoli move least, because the dial sets them. With two significant
figures, one step of the last digit is 1% to 10% of the amount, so an amount
can differ between patients by many steps of its label. At most, in
sevoflurane's muscle at 4 h 13 min, which holds 995 mL, one SD is 31 steps of
10 mL. Two tests hold these figures
(`test_one_sd_shifts_each_compartment_s_amount_by_the_share_the_section_states`
and `test_a_two_figure_amount_s_finest_step_is_a_thirty_first_of_an_sd` in `tests/integration/test_parameter_uncertainty.py`).
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- not-restated: 10 mL -->

**A compartment's share of the agent is shown in whole percent.** A positive
share below 0.5% reads `<1%`, so a compartment that holds agent never reads as
holding none. A share of 99.5% or more that is not the whole reads `>99%`, so no
compartment reads as holding all of the agent while another holds some. A run
holds no agent when it opens, and its next stored state is one second later.
At the settings that a run opens with, the circuit then holds 99.45% of the agent with each agent
the simulator offers, and its share reads `99%` (measured 2026-11-22). At a
lower alveolar ventilation, set before the run starts, the circuit holds more
than 99.5% in the first stored seconds, and its share then reads `>99%`. With
each agent, that lasts 1 s at 2 L/min and 7 s at 0.5 L/min (measured
2026-11-22). One SD of a coefficient moves a compartment's share by at most 13
percentage points, in isoflurane's muscle at 8 h 43 min
(`test_one_sd_moves_a_compartment_s_share_by_at_most_thirteen_percentage_points` in `tests/integration/test_parameter_uncertainty.py`). So
a share can differ between patients by up to 13 steps of 1 percentage point.
<!-- not-restated: 1 s -->

**For developers.** A compartment's amount needs a precision of its own. At the
run totals' 0.1 L, venous blood reads below resolution for a whole hour at 1 MAC
with every agent the simulator offers, and so do the alveoli with sevoflurane
and isoflurane. Desflurane's alveoli read 0.1 L from about two minutes. These
figures are checked by
`test_the_amounts_below_the_run_totals_step_match_the_model` in `tests/reference/test_displayed_precision_figures.py`.

The readouts' uniform resolution does not carry over to the amounts either,
because neither of its two reasons applies to them. The uncertainty that the
parameters cause in an amount is relative, not absolute. And the amounts are not
a row read as one set. They are labels on separate containers, each followed by
its unit, and the schematic compares them on one scale, in the share bar.

No single number of decimals suits every amount. The shift from one SD in the
runs above ran from almost nothing, in the circuit in the first seconds, to
770 mL, in desflurane's muscle at 24 h, because the amounts themselves span that
many orders of magnitude
(`test_one_sd_shifts_each_compartment_s_amount_by_the_share_the_section_states`).
A step of 10 mL would print sevoflurane's and isoflurane's venous blood as
"<10 mL" for the first seven or eight minutes and as "10 mL" for the rest of
the first hour, the flat reading that the readouts' lower limit rules out. That blood holds about 0.18 mL
at 1 min, 6.6 mL of sevoflurane at 10 min, and 9.7 to 10.0 mL at 60 min.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- not-restated: 10 mL, 10.0 mL -->

Two significant figures are kept as shipped (`PL-W51N`). Three would print a
muscle amount of about a litre to the millilitre. One significant figure would
print fat's amount in steps of 1000 mL by 24 h. A test checks the two-figure rule
(`test_a_compartment_s_amount_is_shown_to_two_figures_and_no_finer_than_0_01_ml`).
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The 0.01 mL limit is a provisional choice made for legibility. A finer limit
would print four or more decimals for a moment's worth of agent. The limit can
only make an amount coarser than the two-figure rule would show it, which the
one-sided bound allows. A test checks the forms `<0.01 mL vapour` and `0 mL vapour`
(`test_a_compartment_s_amount_is_shown_to_two_figures_and_no_finer_than_0_01_ml`).

The formatting module (`app/formatting.py`) puts this section into code. It holds
the concentration resolution as one constant (`CONCENTRATION_DISPLAY_DECIMALS`),
and the formatter and the below-resolution marker read it. The MAC decimal count
is a second constant (`MAC_DISPLAY_DECIMALS`), and a test fails if it differs
from the count that the concentration resolution supports
(`test_the_mac_resolution_is_derived_from_the_percent_resolution`). The MAC
axis placement depends on neither. The module
imports no toolkit, so the functions that this section reasons about can be read,
cited and tested without loading the interface. Its tests
(`tests/unit/test_formatting.py`) check the constant's value and every string
the formatter produces. The dashboard's tests (`tests/unit/test_dashboard_frame.py`)
follow the whole path: a real controller, a real step, and the string on the
panel. The dashboard (`app/dashboard_frame.py`) reads the constant to set the
delivered dial's slider position, so the value that the slider applies and the
readout above it cannot drift apart. Another test
(`tests/reference/test_coupled_dynamics.py`) restates the constant and checks it
against the formatting module, because the ordering claim in § "Comparing two readouts" is a property of
the rounded values. Adding a decimal would change what that claim proves without
changing anything the test reads, so changing the resolution means revising this
section.

### The chart's hover readout: what the tooltip may show

When the pointer rests over a trace, a small box appears with the value under the
pointer. This box, the hover readout, supplies for itself every qualifier that the
readout panel takes from its surroundings. The panel's six values sit under a
heading that names the agent and calls them modelled, beside a legend that names
each compartment. The panel's alveolar entry also carries the gloss
`end-tidal-equivalent`. The box floats over the plot and can cover the heading under
which it would otherwise be read. It is the one place in the interface where a
number appears with nothing around it.

The box is also the display that a reader consults most deliberately, so it is the
one most likely to be written down, and the one where a value mistaken for a
measurement costs most. A value in the readout panel is glanced at while a run
plays, but a value under the pointer is one that somebody went looking for.

#### What it shows

The box has three lines: the run context, what the value is, and the value.

```
Modelled sevoflurane · 20m8s
Alveolar (end-tidal-equivalent)
1.43%   0.71 ×MAC
```

The lines that qualify the value come first, so a reader reaches `1.43%` only after
passing "Modelled" and the compartment. A qualifier below the number would come too
late, because the number has already been read.

1. **Run context: "Modelled", the agent, the run when more than one is drawn, and
   the instant.** "Modelled" appears in every box, not only for the compartments
   that a monitor also measures. The agent is there because one percentage means
   different things under different agents: 1.43% is 0.71 MAC of sevoflurane and
   0.24 MAC of desflurane. The instant is printed in whole seconds, in
   the form that the clock, the time axis and the time stamp of each control change
   also use, such as `20m8s`. It is the exact instant of the value in the box, not a
   rounded one.
2. **What the value is: the compartment, with its gloss where the readout panel
   has one.** Two compartments carry a gloss, `Alveolar (end-tidal-equivalent)`
   and `Circuit (inspired)`, because a clinician would most readily set those two
   beside a monitor reading (§ "Minimum displayed outputs"). The other four carry
   none, as in the readout panel.
3. **The value, in percent and as a MAC multiple.** The readout panel shows the
   same pair. The chart has an axis for each, and a single number could be read
   against either.

Every number in the box takes the readout panel's format, never the charting
software's default (§ "What a chart library prints instead, measured"). The MAC
multiple is computed with the same MAC as the MAC axis and the readout panel.

**For developers.** Two functions in `app/chart_frame.py` produce the three-line
form (`format_trace_hover` and `format_wash_in_hover`). Every number in it comes
from one of four functions in `app/formatting.py`: `format_percent`,
`format_mac_multiple`, `format_elapsed` and, for the wash-in ratio,
`format_wash_in_ratio`. The multiple divides by the run's own MAC
(`RunFrame.mac_percent`), which is copied from the snapshot's
`agent_mac_percent`. Any other divisor would bring the traceability failure that
`CLAUDE.md` forbids into the display that looks least like a calculation.

The qualifiers come first because of the general rule in
`.claude/rules/expert-review.md`: prefer an interface that prevents an error to one
that warns after it.

The instant that the box prints is exact, because every drawn instant is a whole
number of seconds (`SimulationController.drawn_window`, `PL-T5NJ`). The box rounds
nothing (`_hover_instant` in `app/chart_frame.py`).

The box reads as this section shows
(`test_the_hover_reads_as_the_specification_shows`), every number in it is the
formatter's at the snapshot's own divisor
(`test_every_hover_number_is_the_formatter_s_at_the_snapshot_s_own_divisor`),
and its instant is at the clock's resolution
(`test_the_hover_states_the_instant_at_the_clock_s_own_resolution`). These are
in `tests/unit/test_chart_frame.py`. On screen, the box states the agent, the
compartment and both units
(`test_the_hover_readout_states_the_agent_compartment_and_both_units` in
`tests/integration/simulation_view/test_simulation_view_readouts.py`).

#### The hover and the run it belongs to

**While more than one run is drawn, the first line of the hover box names the run.
While only one run is drawn, it does not** (project owner, 2026-09-17, ratified,
over giving the run a fourth line of its own and over holding the curve's line
width and the legend to be sufficient).

```
Modelled sevoflurane · Run 2 · 20m8s
Alveolar (end-tidal-equivalent)
1.43%   0.71 ×MAC
```

The box follows the rule for naming the run (§ "Naming the run in a comparison"),
because a concentration that does not say which management produced it is the
correct number under the wrong patient context. The rule matters more for the box
than for the panel, which sits in a labelled block.

Pointing at one trace does not pick out one run. The box can report a trace that
lies within 12 pixels (px) of the pointer, a distance called the hover radius.
Where two runs' traces for one compartment lie close together, the pointer is
within that radius of both. The percent axis tops out at 3 MAC for every agent,
so the slow compartments lie close to zero (§ "MAC multiples as a display unit").
Through the first hour of the cases that `PL-JVHL` measured, the two runs' fat traces lie
so close together that a pointer within the radius of one is within the radius of
the other over most of the area from which either can be reached.
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

The two runs' fat values can still differ. Take a sevoflurane case held at 1 MAC,
and call it the trunk. The branch is a second run forked from it at 10 min with
the vaporizer turned off. At 3492 s the fat value reads either `0.03%   0.02 ×MAC`
or `0.01%   <0.01 ×MAC`, depending on the run. The modelled values are 0.031% and
0.006%, about a fivefold difference in stored agent that the box shows as
threefold, between a run still carrying agent and a run 48 minutes into
emergence. The slow compartments are the ones this chart exists to teach.

A single run goes unnamed because there is nothing to tell it apart from, and a
name would suggest a comparison that is not on screen. A reader always sees when
a second run is drawn, because it brings a second legend entry, a second named
reading in each readout panel and a second set of traces.

**For developers.** Line 1 already gives the run's context, so naming the run
there keeps the box at three lines. While two runs are compared, the run name is
the only part of that line that tells them apart. The agent is always the same:
the code that assembles the chart (`assemble_chart_frame`) refuses runs that
differ in agent, because they share one MAC axis and one set of clinical
references. The one argument for a fourth line is that a reader scans a separate
line but may miss a word in the middle of one. A missed word matters because the
run under a resting pointer can change. But when the run changes, the value on
line 3 changes at the same moment, so the reader gets two cues.

The run name appears on the same condition as the difference in line width
between runs: the code that styles each run's trace (`run_trace_style`) widens
none until a second run exists.

Naming the run showed which run the box reported, but did not make it report
the trace the reader aimed at. § "When more than one trace is within reach" gives the
rule that replaced reporting the single nearest point, and `PL-JVHL` holds the
measurements behind the change.

The box names the run only while more than one is drawn
(`test_the_hover_names_the_run_only_while_more_than_one_is_drawn`), and a
compared box refuses to name one agent over another run's value
(`test_a_compared_hover_refuses_to_name_one_agent_over_another_run_s_value`),
both in `tests/unit/test_chart_frame.py`.

#### When more than one trace is within reach

**The hover readout's box reports every run whose drawn point is inside the hover
radius, with one value line per run** (project owner, 2026-09-19, ratified, over
breaking near-ties toward the trunk and over leaving the targeting alone until
the axis compression is fixed).

```
Modelled sevoflurane
Alveolar (end-tidal-equivalent)
Run 1 · 20m8s   1.43%   0.71 ×MAC
Run 2 · 20m8s   1.45%   0.73 ×MAC
```

**Every compartment whose drawn point is inside the hover radius is also reported**
(project owner, 2026-09-20, ratified, over recording the measurement and leaving
the flip to the axis fix). When every reading in reach belongs to one
compartment, as on most hovers, the box keeps the form above: the agent, the
compartment, then one value line per run. When the readings span several
compartments, the box drops the compartment line. Each value line then opens
with its compartment, and its gloss where it has one, such as "Alveolar
(end-tidal-equivalent)". The run follows when the chart draws more than one run:

```
Modelled sevoflurane
Muscle · Run 1 · 20m   0.19%   0.10 ×MAC
Muscle · Run 2 · 20m   0.09%   0.04 ×MAC
Fat · Run 1 · 20m   0.01%   0.01 ×MAC
Fat · Run 2 · 20m   0.01%   <0.01 ×MAC
```

The box reports every trace in reach because, where traces crowd together, no
hand can aim at one rather than another. Two runs' fat traces lie 0.2–1.4 px
apart, and at that separation no rule for picking one trace can follow the
reader's aim (`PL-QYBW`). The earlier rule reported only the nearest point, so a
2 px movement could switch the box to another run or compartment, and to a
different number. The box itself stayed put. Only the name and the numbers
changed, and the reader had already read past the name. Now no movement too
small to aim with decides what the box shows.

The percent axis stays linear, which crowds the slow compartments together.
Because the box reports every trace in reach, the crowding needs no change of
scale (§ "MAC multiples as a display unit").

Value lines are ordered by compartment and then by run, both in the chart's
drawing order, so the box follows the legend and the readout panels beside it.
Distance from the pointer never sets the order, because lines ordered by distance
would swap places under movements too small to aim with.

The box is placed at the first reported run's point. A dot marks every reported
point, because a single dot would mark one run's trace while the text reported
several.

Once the reader has aimed the pointer, usually only one run is in reach. With
one run in reach, the hover readout's box uses the three-line form, and names
that run if two are drawn. The box gains a line when a run
comes into reach and loses it when the reader moves away, so the reader sees each
run arrive and leave. The box holds at most four value lines on a two-run chart,
which draws at most two compartments. On a single-run chart it can hold six, as
it does at the run's opening, where all six traces start together.

**For developers.** Two functions produce the forms above that list several runs or compartments
(`chart_frame.format_compared_trace_hover` and
`chart_frame.format_compared_wash_in_hover`), and their numbers come from
`app/formatting.py` like every other number in the box. The unit tests in
`tests/unit/test_chart_frame.py` contain both worked examples above verbatim.
They also contain the fat and muscle cases behind the decisions to report every
run and every compartment in reach.

The rules weighed before this one, and the scans behind reporting every run in
reach (`PL-JVHL`) and every compartment in reach (`PL-0RZ0`), are in those
items. `PL-QYBW` holds the measured case for a logarithmic axis, which was not
built.

#### The instant each value is reported at

**The pointer's position along the time axis sets the instant reported, and the
hover radius decides only which traces are in reach** (`PL-1K9G`, 2026-09-22). The
chart draws each run as columns of points. The spacing between columns follows the
plot's width: on a plot 900 px wide, it is 4 s on a 60-minute axis and 48 s on a
12-hour axis. Each run also draws a point at each of its control changes and at
each peak or trough between two columns (§ "What the chart draws"). A branch
draws no columns before its fork. Each run is reported at its
drawn instant nearest the pointer in time, and a tie goes to the earlier instant.
Each of that run's compartments is reported if its point at that instant is
inside the radius, so every compartment of one run is reported at one instant.
Moving the pointer up or down can change what is in reach, but never the instant
printed. The wash-in plot follows the same rule.

Each value line prints its own instant, because two runs' nearest instants can
differ, and the printed form shows the difference. They differ by up to one
column where one run draws an instant that the other does not, such as a
control change. Beside a branch's fork, or past the end of the shorter run, they
can differ by up to the hover radius of 12 px plus half a column along the time
axis. One
instant above several values would claim that they are simultaneous when they may
not be.

**For developers.** Two functions collect the traces within reach at the instant
that the pointer's time sets (`nearest_trace_point` and `nearest_wash_in_point`),
and the first of them skips hidden compartments. The unit tests in
`tests/unit/test_chart_frame.py` also contain the geometry behind the decision
that the pointer's time alone sets the instant
(`test_every_compartment_of_one_run_answers_at_one_instant`). The rules weighed
before this one, and the scan behind letting the pointer's time alone set the
instant, are in `PL-1K9G`.

#### Resolution: the readouts' derivation applies unchanged

The box prints a percent and a MAC multiple to two decimals each, or `<0.01%` and
`<0.01 ×MAC` below 0.01. § "Displayed precision" derives both forms for the
readout panel, and nothing in that derivation depends on where the number appears.
Legibility sets the number of decimals. Two is the coarsest count that keeps
every compartment's wash-in visible, and the readouts show nothing finer. That
lower limit is a teaching judgment about what a reader can learn from the slow
compartments. How far a partition coefficient varies between patients does not
set the count. That section states the spread as a limitation on reading a
value as a patient's.

**The box gets no third decimal.** A printed digit could answer either of two
questions. One is how finely two moments within one run can be told apart, which
is about nine decimal places finer than the readout panel shows. The other is how
finely this model resolves a concentration in a patient, which is much coarser.
The box suits the first question better than the readout panel does, because it
reports one trace at one instant, the form a within-run comparison takes. That
question alone would justify a third decimal. But a reader cannot tell which
question a digit answers, and the box makes the confusion worse. It is the
display most likely to be written down, it floats over a chart whose whole
subject is a patient, and it is read without the readout panel's five other
compartments, which show that a within-run comparison is on offer.

**The box must keep `<0.01%` and `<0.01 ×MAC`.** Fat and muscle stay below 0.01%
for the first minutes of a run, and § "Why the readouts show two decimals" states
how long, where it explains its lower limit. Those minutes are the slow-compartment
wash-in that the chart exists to show. `<0.01%` says what is known. A number there
would claim a resolution the model does not have, on the compartment where a reader
is least able to notice.

**For developers.** The box keeps the readout row's below-resolution forms and
glosses
(`test_the_hover_keeps_the_below_resolution_forms_and_the_readout_row_s_glosses`
in `tests/unit/test_chart_frame.py`).

#### What a chart library prints instead, measured

Left to its default, the charting software's own pop-up label prints the plotted
coordinate instead of a clinical value. It has no unit, so a value such as `1.54` could
belong to either axis, and for sevoflurane the axes differ by a factor of about two.
Where the box prints `<0.01%`, the label gives a number. It adds decimals as the value
shrinks. A display whose precision changes with the size of the value claims that the
model resolves small values more finely than large ones, the opposite of the truth. This
fault is the one that would go unnoticed.

**For developers.** The default matters because it is what ships if nothing
overrides it, and both toolkits that this project has used format the coordinate. In
Flet, a chart's data point (`flet_charts.LineChartDataPoint`) has a pop-up label
(`LineChartDataPointTooltip`) by default, and this application never set that label's
`text` while its chart was drawn with Flet. In pyqtgraph, a scatter plot
(`pyqtgraph.ScatterPlotItem`) formats the label
of a hoverable point with a function (`tip`) whose default is
`'x: {x:.3g}\ny: {y:.3g}\ndata={data}'.format`. The table shows the drawn y at four
instants of the first hour in two ways: with `.3g`, as that scatter plot would apply it,
and with this application's percent formatter (`format_percent`). The values come from
a run on 2026-09-14 on the reference adult, with sevoflurane delivered at 0.02 (1 MAC)
and the columns that the chart then drew over a one-hour axis, which fell between whole
seconds.

| Instant | Compartment | `.3g` on the drawn y | This readout |
| --- | --- | ---: | ---: |
| 48.3 s | Alveolar | `0.262` | `0.26%` |
| 48.3 s | Muscle | `0.000656` | `<0.01%` |
| 48.3 s | Fat | `3.52e-05` | `<0.01%` |
| 289.9 s | Fat | `0.00116` | `<0.01%` |
| 1208.1 s | Fat | `0.00888` | `0.01%` |
| 3600.0 s | Alveolar | `1.54` | `1.54%` |

- Without a unit, `3.52e-05` is worse than `1.54`, because the smaller number reads
  equally well as a fraction of an atmosphere, a hundredfold out.
- `3.52e-05` carries five decimal places beyond the resolution that § "Displayed
  precision" sets, on the compartment where the readout panel prints no number at
  all. A reader comparing that number with the panel would find them disagreeing
  about whether the value is known.
- Three significant figures give two decimals at `1.54`, three at `0.262` and six at
  `0.000656`.

The rendered box reports the drawn state through this project's formatters, not
the library's default
(`test_the_hover_reports_the_drawn_state_through_the_formatters` in
`tests/integration/test_qt_chart.py`).

#### Which lines on the chart show a hover readout

The six compartment traces respond to a hover in the form that § "What it shows" gives, unless the
reader has hidden the compartment. The wash-in trace responds with a plain ratio,
because $`F_A/F_I`$ is dimensionless and has neither a percent nor a MAC reading:

```
Modelled sevoflurane · 20m8s
Wash-in FA/FI (alveolar / modelled circuit)
0.71
```

The caption in parentheses says that $`F_I`$ is the modelled circuit, not the
vaporizer dial. At the one column that a stretch draws past equilibrium, the
third line reads `Past equilibrium: not a wash-in fraction` instead of a number
(§ "F_A/F_I as a displayed ratio").

The 1 MAC line, the MAC-awake band and the control marks do not respond. What
the three would report is already on screen. The MAC value used to compute the
MAC multiples is stated beside the chart, and the input timeline lists each
control change with its old and new value.

**For developers.** The line, the band and the marks do not respond because all
three cross every trace: the line and the band run across the plot, and the marks
are vertical and full height. If they responded, an annotation would appear under
the pointer wherever a reader aims at a trace that passes behind one of them. That
is exactly where a reading is most wanted: a trace crossing 1 MAC is the event the
line is drawn for.

The wash-in ratio has its own formatter (`format_wash_in_ratio`), and its caption
is a constant in the chart-frame module (`WASH_IN_HOVER_LABEL` in
`app/chart_frame.py`). The caption uses a slash rather
than a division sign because every non-ASCII character that reaches a reader must
first have been rendered and seen (`tools/glyph_check.py`), and the division sign
has not been.

The references answer no hover, and clear space answers none
(`test_the_references_answer_no_hover_and_clear_space_answers_none` in
`tests/integration/test_qt_chart.py`). A hidden trace and a preview answer no
hover either (`test_a_hidden_trace_answers_no_hover` and
`test_the_hover_never_answers_from_a_preview` in
`tests/unit/test_chart_frame.py`).

#### When the hover readout appears

The box appears whenever the pointer is over a trace, whether the run is playing
or paused. At high playback speed its value moves with the run, as every other
readout does. To study a value, pause the run. Moving the pointer off the plot
removes the box at once, so a value that moves with the run is always one that
the reader is pointing at.

**For developers.** The box is built on pyqtgraph and reports the drawn points
within the hover radius (`PL-G59B`, 2026-09-14). The code that shows it is in
`app/qt_chart.py`, and an integration test checks the rendered box against a real
run (`tests/integration/test_qt_chart.py`).

The Qt build had to provide the hover, under the parity rule "Every capability the
Flet build has, the Qt build has". The hover does not come by default. A pyqtgraph
scatter plot (`ScatterPlotItem`) ships with `hoverable` set to `False`, and a
plotted line has no hover of its own, so a port that says nothing about the hover
loses it.

The box appears while a run plays because a hover that responds only while paused
is a hidden mode. A reader who tries it during a run gets nothing, concludes that
the chart is not interactive, and never finds the hover again. An earlier change
had withdrawn the hover while a run plays (`PL-KP7H`), because Flet's control-tree
diff visits every point's tooltip object on every frame, and the tooltips were
half the cost of a saturated frame.

Qt has no such cost. The box reads the pointer's moves from the plot's own
viewport through an event filter (`_PointerMoves` in `app/qt_chart.py`). It
handles the first move at once, and then at most sixty moves a second
(`PL-TCR5`). Two other routes were available. One drives a crosshair from the
scene's own mouse-move signal (`sigMouseMoved`), rate-limited through a signal
proxy (`SignalProxy`). The other gives each hoverable point a callable (`tip`)
that runs when the pointer arrives, with no tooltip object stored for each
point. All three cost work per pointer event, whatever the number of points
drawn.

Besides removing the box, leaving the plot discards any pointer move still waiting
to be handled. A box left at the last point the pointer crossed would recompute
its value every frame. While a run played, that value would climb with the run
like a live readout, for an instant that nobody is looking at (`PL-LTKL`).

The box answers while the run is playing
(`test_the_hover_answers_while_the_run_is_playing`), and hides when the pointer
leaves
(`test_the_hover_hides_when_the_pointer_leaves_and_a_later_frame_does_not_bring_it_back`),
both in `tests/integration/test_qt_chart.py`.

### A preview of an unapplied setting

While a learner holds a slider's handle, the chart draws the trajectory that the
run would take if the value under the handle were applied at the run's current
time (`PL-5B1N`). Both plots draw it, so they never show two different futures.
On the F_A/F_I plot the preview is the predicted ratio. A dot marks where a
stretch of it stops, as on the run's curve.

**A preview is a prediction.** The run has not passed through it, so it is not a
modelled state of the run. It is not a measurement either. It depends on a
setting that the learner has not applied and may never apply. Drawn with the
run's line width and no label, it would look like a run that happened.

**Four cues mark a preview: its position, a label, its line width and its timing.**
None of them is colour. A preview's curves keep each compartment's colour and dash
pattern, because those tell the six compartments apart.

1. **Position.** The preview lies wholly to the right of the run's current time,
   inside a tinted region. A line at the run's current time is the region's left
   edge. The preview ends at the right edge of the time axis, or at the end of the
   longest run the simulator supports if that comes first. The run that the
   preview belongs to never enters the region, but when runs are compared, a run
   that has gone further may be drawn inside it.
2. **Label.** A label in the plot names the control and the value tried, in the
   slider's own words, such as "Preview: Fresh gas flow 6.0 L/min, not applied".
   It is drawn inside the region, so a screenshot taken during a drag includes
   it. Each compared run has its own controls, so only the run whose slider
   handle is held shows a preview. The label names that run.
3. **Width.** Each preview curve is one pixel thinner than the same compartment's
   curve in a run shown alone, but never thinner than 2 px. The two compartments
   drawn at 3 px therefore have 2 px preview curves, and so do the four drawn at
   2 px. For those four, the other three cues mark the preview. When runs are
   compared, the first run's curves are drawn one step wider, but its preview
   curves keep the width they have when the run is shown alone. The preview is
   then no wider than the other run's curve of the same compartment.
4. **Timing.** The preview exists only while the handle is held. It appears at
   the press and is gone from the frame drawn at release. It also ends while the
   handle is still held when the run starts over, on a Reset or an agent change,
   and when a branch is opened or dropped, because its label would otherwise
   name an agent or a run that is no longer shown (`PL-1WFW`). If the held
   handle then moves, a new preview is drawn from the run on screen.

**The preview comes from the same model and version as the run.** It starts from
the run's state at its current time, as § "Each second has one stored state"
defines that state. The value goes through the same checks as when it is
applied. A new cardiac output moves every tissue flow exactly as applying it
would. The same inputs always give the same preview. Computing a preview changes
nothing in the run. When the value under the handle is the setting already in
force, the preview matches what the run then draws, to within the computer's
rounding error. While the run plays, the preview is computed again on every
frame from the run's new current time.

**A drag applies its value only when the handle is released.** The run records
one setting change at that moment. Until then the run keeps the setting in force,
and the value printed above the slider is that setting. The value is applied
before the preview ends, so the frame drawn at release already shows the run
under its new setting. A key press, one notch of the scroll wheel or a click on
the slider away from its handle is a single input, so it applies at once and
draws no preview. Such an input also draws the whole screen at once, so the
readouts, the compartment schematic and both charts show the same instant
after it (`PL-2WVC`). An input that comes soon after another input's frame
waits, and the wait's end draws the latest state. The next frame starts
100 ms after the last one started, or twice that frame's drawing time after
it, whichever is later. So while a key or button is held, a wheel spins, a
trackpad swipes or a handle is dragged, the charts follow the dial at
Nielsen Norman Group's 0.1-second limit for a user to feel that they are
directly moving what is on screen, on every platform, as long as a frame
takes less than 50 ms to draw (`PL-NKFD`). A slower frame, such as one that
draws a preview over an hour-long run, is followed by a pause as long as
itself, so drawing never takes more than half of the time in which the run
steps and the reader's inputs are handled. A render tick during a burst
counts as one of its frames. Until that frame, the readouts can show
a later step than the charts. A click that moves the handle to the pointer
draws one frame, and its release draws no second one. A handle released at
the setting already in force applies nothing, and the run records no setting
change.
<!-- provenance: app/dashboard_frame.py INPUT_FRAME_INTERVAL_MS = 100 -->

**A click on the slider away from its handle follows the platform's own
convention** (`PL-57LD`). The simulator sets no style of its own, so Qt's style
for the platform decides it. On macOS, and under Qt's Windows 11 style, a left
click moves the handle to the pointer. Under Qt's Fusion style a left click
moves the handle one step towards the pointer, and a middle click moves it to
the pointer. Holding the left button down there repeats the step while it stays
down. Each step and each jump is one input, so it is applied at once and
draws no preview. Where the click moved the handle to the pointer, moving the
pointer with the button still down is a drag, which previews until the release.
A press on the handle itself applies nothing until the handle is dragged, on
every platform, even where the press is off the handle's centre. The drag then
moves the handle only as far as the pointer moves.

**A stopped run accepts no new setting and draws no preview.** A run stops when
it fails or reaches the end of the longest run the simulator supports.

**The time window keeps its width during a preview.** It slides so that the
run's current time sits at mid-plot: half the window shows the run that
happened, and half shows the prediction. Early in a run the window stops at
zero, and the current time sits left of the middle. Widening the window to make
room would rescale every slope, which § "The chart's time base" rules out. When
runs are compared, the window centres on the current time of the run whose
slider handle is held. At release, the window goes back to following the run.

**No value on a preview curve is printed as a reading.** A value shown when the
pointer hovers over the chart never comes from a preview. A preview that goes
above the top of the concentration axis is cut off there, as a run's curve is.
The off-scale notice then names each preview curve that is cut off, with its
highest value in view, because the readouts give only the run's values.

**For developers.** The preview's states come from `core/prediction.py`
(`SimulationController.preview_window`). For `PREVIEW_EXACT_S` seconds past the
reach, `predicted_states` takes one-second steps from the state stored for the
second the run has reached, and the window is drawn on the run's time grid with
the second of each peak and trough between two columns. After that,
`predicted_states_at` predicts each grid second and the right edge from the one
before. Where F_A/F_I is inside the wash-in domain at one of two such columns
and outside it at the other, the seconds between them are predicted too, and the
crossing second is drawn (`controller._with_later_crossings`,
`test_a_preview_past_its_first_hour_draws_the_second_its_ratio_crosses_equilibrium`). The controller keeps the last predicted window and draws it again while
none of its inputs change. `test_a_preview_past_its_first_hour_draws_the_grid_seconds_and_its_right_edge_only`
in `tests/unit/test_chart_frame.py` checks the split. The preview's settings are
built the way a branch's are (`SimulationController.preview_settings`). A trial
run is rebuilt from the settings in force and checked to match the run in every
value. The trial run then takes the new value through the same setter that
applies a value to the run. The centred time window comes from
`chart_time_base.preview_window`, and the wording of the off-scale notice from
`dashboard_frame.PREVIEW_OFF_SCALE_NOTICE_TEMPLATE`.

The platform's convention is the style hint `SH_Slider_AbsoluteSetButtons`.
Qt's source at tag v6.11.2 sets it to the left and middle buttons in
`qmacstyle_mac.mm`, to the left button in `qwindows11style.cpp`, and to the
middle button in `qcommonstyle.cpp`, which Fusion inherits. For such a press,
`QSlider.mousePressEvent` applies the value at the pointer and then marks the
handle as held, which is the signal that starts a preview. `_SettingSlider` in
`app/qt_widgets.py` therefore starts no preview for a press on the track, and
puts the handle back where it was for a press on the handle. Qt then
measures the drag from where the handle would have jumped to, so
`_SettingSlider` measures that drag itself, from where the pointer pressed the
handle. The tests in
`tests/integration/simulation_view/test_simulation_view_controls.py` run both
presses under Fusion and under a style that returns the macOS hints
(`test_a_click_on_a_slider_s_track_applies_at_once_and_draws_no_preview`,
`test_a_press_on_the_handle_off_its_centre_released_unmoved_applies_nothing`,
`test_a_drag_from_off_the_handle_s_centre_moves_the_setting_only_as_far_as_the_pointer_moves`).

The 2 px minimum width for a preview curve is there because an antialiased line
thinner than 2 px has less than 3:1 contrast against the panel
(§ "The six compartment traces: what separates them").

Neither dash pattern nor reduced opacity can mark a curve as predicted. The
muscle curve is already dotted, and drawing the run solid with a dotted preview
would flatten the five dashed curves into one style. At 0.85 opacity, the
alveolar and muscle curves fall to contrasts of 2.93 and 2.83 against the panel,
less than the 3:1 that WCAG success criterion 1.4.11 sets. At 0.75 they fall
further, to 2.57 and 2.49.

The region has no fill, because its edge and its label carry the information.
A fill light enough to keep every trace at 3:1 where the region overlaps the
MAC-awake band could not be seen: the muscle trace already measures 3.03:1
against the band's fill under deuteranopia (`PL-GT8W`). The contrast check
measures every trace against the region's fill, alone and over the band's, in
all four vision models, so a fill added at `theme.PREVIEW_REGION_FILL_OPACITY`
fails the check unless every trace still clears 3:1.

### A cost at the reader's price

The agent cost View shows what the delivered agent costs, at a price that the
reader sets in its form. The readout shows which part of the cost is the model's
and which part is the reader's (`PL-VJZK`). A price is neither modelled nor
measured, because the reader supplies it. Every other value the interface shows
today is modelled. A cost is a modelled amount times that price, so a wrong
price makes a correct amount lead to a wrong conclusion.

#### What the cost readout shows

**A cost is never shown alone.** Beside it, the readout shows six things:

1. the delivered agent in millilitres of liquid equivalent, labelled as
   delivered and as liquid. This is the modelled figure that the cost is
   computed from. It stays on screen even where the reader has chosen to show
   the View's amounts in litres of vapour (`ROADMAP.md`, v0.7.0 entry 8), so
   that the modelled amount never appears only inside a figure that includes
   the reader's price;
2. the price per millilitre of liquid that the cost uses, so that the reader
   can check the product by eye;
3. the bottle price and the bottle volume that the price per millilitre came
   from;
4. the currency's code, on the cost and on each price;
5. the date on which the price applied; and
6. words saying that the cost is at the reader's price, not only a colour or a
   style, so that no reader misses the statement.

**A bare "mL" does not say whether it means liquid or vapour.** The schematic
labels its amounts in millilitres of vapour (`ROADMAP.md`, v0.7.0 entry 1).
Gas Man quotes its price as "Cost/mL vapor" (printed p. 174). One millilitre
of liquid isoflurane gives about 196 mL of vapour, so a volume or a price read
as vapour is wrong by that factor.

**The displayed cost reproduces the four costs printed in Gas Man's two
isoflurane exercises.** The simulator runs each exercise from its patient
inputs, at the price that the book prints beside the costs of Exercise 14-1,
"a bottle cost of US$20.47 per 100 ml" (printed p. 134). For Exercise 14-1 at
60 min, the readout could show "39 mL of liquid x USD 0.2047 per mL of liquid =
USD 8.07, at your price of USD 20.47 per 100 mL bottle, as of 2008-03-05". The
wording and the layout are placeholders. The book prints $8.06, because Gas Man
rounds isoflurane's vapour-to-liquid ratio to 196 (`docs/PARAMETERS.md` § "Agent amount").

**The figures beside a cost are rounded, and the readout says so.** It says
that the figures may therefore not multiply exactly. The cost is computed from
the unrounded liquid volume and price per millilitre (`PL-1P15`).
§ "Agent amounts in millilitres, and the cost" sets the
precision of each figure. The liquid volume is shown in whole millilitres, so
the product of the figures shown can differ from the cost by more than one unit
of the cost's last digit. In the example above, 39 mL times USD 0.2047 is
USD 7.98. The cost is USD 8.07 because it uses the unrounded 39.42 mL. At
USD 115.13 per 240 mL bottle, 60 min of desflurane at 6 % and 1 L/min costs
USD 8.23. Shown as 17 mL and USD 0.4797 per mL, the two figures multiply to
USD 8.15.


**The cost is the delivered agent's liquid equivalent times the price per
millilitre.** It uses the delivered agent because that is what left the bottle
(`ROADMAP.md`, planned-milestone item 28, and `PL-H4N8`). The conversion to
liquid is exact (`docs/MODEL.md` § "Agent amount"). The cost depends only on the delivered
amount, the agent's vapour-to-liquid ratio and the price stored for that agent.
That same stored price supplies the bottle price and volume, the price per
millilitre, the currency and the date shown beside the cost. The date is never
used to compute the cost, and neither is today's date. When two runs are
compared, each run's cost uses the price of its own agent. A cost is never added
to, or subtracted from, a cost in another currency.

**When no cost is shown.** The readout shows no cost, and says why, in each of
these four cases:

- no price is set for the agent;
- the stored price was refused when the simulator read its preferences file.
  No default replaces it, and the readout says that no valid price is set for
  the agent. The View names each refused entry, and under that notice it offers
  to discard them all. The reader confirms the discard first, because it cannot
  be undone
  (`test_the_reader_can_discard_refused_entries_and_the_next_launch_names_none`
  in `tests/integration/test_agent_cost_view.py`);
- the price per millilitre is not a positive finite number, or the cost is not
  finite, which extreme entries can cause, such as a bottle price of 10 to the
  power 308 for a 0.5 mL bottle. The same applies to a cost too large to be held
  to its minor unit, above about USD 3.5 × 10^13, where the cents shown would
  come from the computer's rounding rather than from the price; or
- the delivered amount cannot be converted to liquid (`docs/PARAMETERS.md` § "Agent amount").

The readout never shows a cost of zero in place of one of these cases. Nor does
it show a cost left over from an earlier instant, another agent or an earlier
price. When the price changes, the readout redraws the cost at once, whether or
not the run is advancing.

#### Setting a price

**The project ships no price.** Until the reader sets a price, the readout says
that no price is set, and it shows no cost. A shipped price goes stale, and it
differs from one institution to the next. Gas Man shows both problems. Its
default price for isoflurane is $20.47 for a 100 mL bottle (Philip JH,
*Workbook for Gas Man*, Appendix C, printed p. 171). The book calls its
defaults "USA bottle volume and bottle cost as of March 5, 2008" (printed
p. 105). Chapter 14 gives $78.00 per 100 mL bottle "on March 5, 2008" (printed
p. 141).

**The simulator keeps at most one price for each agent, and the price records
five things:**

- the agent it prices;
- the price of one bottle, in the price's currency;
- the volume of that bottle, in millilitres of liquid agent;
- the currency, as its three-letter ISO 4217 code, such as `USD` or `EUR`;
  and
- the date on which the price applied, as an ISO 8601 calendar date, such as
  `2008-03-05`.

The form's date field writes dates this way. For an agent with no stored price
it fills in the day of entry, and for an agent with a stored price it shows
that price's date. The
reader should change it to the day the price was quoted, because a price goes
stale from that day, not from the day it was typed in.

When the reader types another bottle price, bottle volume or currency over a
stored price, the form moves the date to the day of entry and says that it did,
because a new price saved under the stored date would be shown as older than it
is. Typing the stored price again moves the date back. A date that the reader
edits is kept, whatever they type afterwards. The date field therefore always
shows the date that the form saves
(`test_a_price_typed_over_a_stored_one_is_dated_at_the_day_of_entry` and
`test_a_date_the_reader_edits_is_kept_for_a_price_typed_over_a_stored_one`, both
in `tests/integration/test_agent_cost_view.py`).

**The form takes the price per bottle, and the simulator derives the price per
millilitre** (decided by `PL-VJZK` on 2026-10-26, over asking for a price per
millilitre). An institution buys agent by the bottle, and its pharmacy quotes a
price per bottle. The price per millilitre is never stored, so it cannot
disagree with the bottle price and volume. The form still allows three mistakes:

- a price per millilitre typed as the bottle price. The cost is then 100 to
  250 times too low, because the bottles in Gas Man's defaults hold 100 to
  250 mL of the volatile agents (printed pp. 171-172);
- a bottle volume typed in litres, such as 0.25, or as 1 for one bottle. The
  cost is then 100 to 1000 times too high; and
- the price and the volume swapped. The price per millilitre is then inverted.

The field for the bottle volume therefore names its unit, millilitres of liquid.
The first two mistakes make the price per millilitre on the readout wrong by the
same factor as the cost. A swap stands out only where the bottle price and
volume differ widely. At Gas Man's sevoflurane default of 240.34 for a 250 mL
bottle (printed p. 172), a swap changes the cost by 8 %, and nothing on screen
would show it.

<!-- not-restated: 8 % -->

**What is refused.** The simulator checks every price, at entry and again when
it reads its preferences file. A bottle price or a bottle volume must be a positive finite
number. A price of zero is refused because it is far more likely to be an empty
field than an agent given away. The currency must be three capital letters, and
the date a real calendar date. The three letters are not checked against the
codes that ISO 4217 assigns, but a mistyped code shows beside every cost and
price, where the reader sees it.

The reader types the bottle price and the bottle volume as digits with at most
one decimal point. A sign, an exponent, a thousands separator or a decimal comma
is refused rather than guessed at, because "1,250" could mean 1250 or 1.25.

**A refused entry changes nothing.** The form says why it refused the entry,
and the readout goes on showing the cost at the price already stored, with
that price beside it.

#### The code and tests behind the cost readout

**For developers.** `app/agent_cost.py` computes every line of the cost readout
and reads the price that the reader typed (`PL-1P15`). The agent cost View is
`AgentCostView` in `app/views.py`. Each run's panel is in
`app/qt_agent_cost.py`, and the form is in `app/qt_agent_price.py`. The
preferences module in `app/preferences.py`
stores each price (`PL-93B3`). The safety standard in `CLAUDE.md` applies to a
cost, although money is not a clinical quantity.

A stored price has no field that says who set it, because the project ships
none. If a release ever ships a default price, each stored price gains that
field, and the readout must then mark a default price as one the project
supplied, with its date.

The form asks for a bottle price because a field for a price per millilitre
would make the reader divide first, and a bottle price typed into it would
multiply every cost by the bottle's volume in millilitres (`PL-VJZK`).
Gas Man's Set Cost command likewise takes "the bottle volume and bottle cost"
(printed p. 15). One function derives the price per millilitre from the bottle
price and volume. The preferences module accepts any positive finite bottle
volume, because no source gives the sizes in which the agents are sold
(`PL-93B3`, 2026-11-01).

The readout names a currency by its code because the sign "$" names the United
States, Canadian and Australian dollars, among others. Gas Man shows the
problem. Its defaults label each bottle cost "Bottle cost in $US" (printed
p. 171). Its menu says the cost is typed "in the local currency" (printed
p. 15). A code from ISO 4217:2015 names exactly one currency.

The currency check stops at three capital letters (`PL-93B3`, 2026-11-01)
because ISO 4217's list of codes changes several times a year. Checking against
the list would need a dated copy of it with a record of its source, and a copy
that fell out of date would refuse a real currency. Any three letters still
remove the ambiguity of "$".

The price's date follows ISO 8601-1:2019 because 03/05/2008 means March or May
depending on the reader's country. Neither this standard nor ISO 4217:2015 was
read for this section.

The shown liquid volume times the shown price per millilitre differs from the
cost by at most half a unit of the volume's last shown digit times the price per
millilitre, plus the volume times half a unit of the price's last shown digit.
The cost is shown to its currency's minor unit (§ "Agent amounts in millilitres,
and the cost").

The two rows in the hazard table (`docs/VERIFICATION.md` § "Reasonably foreseeable misuse, and the
hazards the presentation carries") name the tests for this section. The cost is
checked against the four costs printed in Gas Man's two isoflurane exercises, in
`tests/integration/test_agent_cost_view.py`
(`test_the_displayed_cost_reproduces_gas_man_s_printed_costs`). The conversion
to liquid alone is checked against the same exercises in
`tests/reference/test_published_vapour_to_liquid.py`.

### The compartment schematic: what its heights, amounts and share bar assert

The compartment schematic draws six compartments as containers: the circuit,
the alveoli, venous blood, the vessel-rich group, muscle and fat, in the
readout row's order (`PL-RNYV`). Like Gas Man's Picture, it shows where the
tension is. It also shows where the agent is, which neither the readouts nor
the concentration chart does. It prints the amount of agent each container
holds, and its share bar gives each compartment's part of all the agent.

**Every height, amount and share on the schematic is a model output.** The
schematic therefore prints "Model outputs — not measurements." once, in its
own heading, as the readout section does. No amount is a prediction about a
patient to its last digit, for the reason § "Displayed precision" gives for
the readouts.

**A container's fill height is the compartment's modelled tension, not an
amount.** All containers of one run fill against one scale: the concentration
chart's standard scale, from zero at the bottom to 3 MAC of the running agent
at the top. The schematic keeps that scale when a reader gives the chart
another top. So a container filled to some share of its height shows the same
tension as a trace standing at that share of the chart's axis at its standard
top. A container is much shorter than the chart's plot, so its fill level does
not line up with the chart's gridlines on screen. Each container therefore
carries short marks every 0.5 MAC, and the caption names the top in percent
and in MAC, and the spacing in MAC (`PL-8W1B`). A container that holds more agent can stand lower than one that
holds less. At 60 min in a run with sevoflurane at a 1 MAC dial, fat holds a fifth of
all the agent in the run, but its tension of 0.03% atm fills less than 1% of
its container's height (`ROADMAP.md` § "v0.7.0 - the schematic"). At a 1 MAC
dial, across the simulator's three agents, fat holds a fifth of the stored agent
at one hour and a third at three hours, which the chart's fat trace cannot show.
Every container is drawn at one width, so its filled area is not an amount
either.
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

A tension above the top of the scale fills its container to the top. The
schematic marks the container as off the scale when the tension is above the
top by more than the smallest step that the readouts show
(§ "What the concentration readouts show"). The concentration chart uses the
same test for a trace above its axis, in its off-scale notice. The container's
label still prints the tension. The circuit rises above the top, towards 4 MAC,
when a sevoflurane dial is at its 8% maximum.
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->

**A container's amount is the agent that the model holds in that compartment,
counted as vapour.** It is the equivalent volume of pure agent vapour at a
reference condition of 20 °C and 760 mmHg, dry, shown in millilitres ($`M_x`$ in
`docs/MODEL.md` § "Agent amount"). The agent in blood and fat is dissolved, so the volume
expresses an amount of agent, not gas present in the body. This subsection's
rules for an agent amount also apply to every other View that shows one,
including the share bar (`PL-S79P`) and the agent cost View (`PL-B396`).
§ "Displayed precision" derives the precision at which amounts are shown.
<!-- provenance: core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->

**An agent amount's unit always names vapour or liquid, and is never a bare
"mL".** Millilitres of vapour and millilitres of liquid differ by a factor of
about 180 to 210, depending on the agent. At the reference condition, 1 mL of
liquid gives about 183 mL of sevoflurane vapour or about 210 mL of desflurane
vapour (`docs/PARAMETERS.md` § "Agent amount"). A vapour amount is written "mL vapour", as in
"38 mL vapour". A liquid amount is written "mL of liquid", as in
"4 mL of liquid". The model holds no liquid, so a liquid amount is worked
out from a vapour amount, as the volume of liquid agent that would give that
much vapour. That volume is what a vaporizer uses up. A caption under a liquid
amount says that the vaporizer used this liquid. The accounting View shows
amounts in litres, under a caption that begins "Litres of equivalent pure
agent gas", which marks them as vapour, and names their condition. The agent cost panel writes its delivered amount
as "mL of liquid" or "L vapour", whichever unit the reader chose, and its
caption says what that unit measures. These spellings may change while the
interface is being built.

**The share bar shows each compartment's share of all the agent the run holds,
circuit included.** The bar is divided into six segments, in the containers'
order. Each segment's length is that compartment's amount divided by the sum of
the six amounts:

```math
s_x = \frac{M_x}{\sum_y M_y}
```

The six segments therefore fill the whole bar. Each segment is named in text,
never by colour alone. A share printed in text is shown in whole percent
(§ "Displayed precision"). A run holds no agent when it starts, so the bar is
then drawn empty and prints no share.

**Lines between the containers show ventilation and blood flow.** The
containers stand in one row. A line joins the circuit to the alveoli for
ventilation. A line above the row carries arterial blood from the alveoli to
each tissue group. A line below the row carries each tissue group's venous
blood to the venous blood container, and a line joins that container back to
the alveoli. So the three tissue groups are drawn in parallel, as the model
perfuses them (`docs/MODEL.md` § "Assumptions"). The containers are not joined one to the next,
because that would draw agent passing from the vessel-rich group through muscle
into fat, a route between tissues that this model omits (`PL-RNYV`).

**No container is drawn for arterial blood.** The model sets arterial tension
equal to alveolar tension at every instant ($`F_a \equiv F_A`$,
`docs/MODEL.md` § "What the model represents"), so it gives arterial blood no volume, capacity or
amount of its own. The alveolar container therefore shows arterial tension as
well. Gas Man's Picture draws an arterial container. Here such a container
would show agent that the model does not hold.

**Each schematic shows its run at the same instant as the readouts.** A line
of text above the schematic gives that instant as the readouts' clock prints
it. While runs are compared, that line also names the run, so that a reader
does not take one run's value for the other's. Two compared runs can be at
different times, as when one is a branch taken at an earlier point. A
difference between their schematics may then come from elapsed time rather
than from the change the branch made. The schematic withholds its values
whenever the readouts withhold theirs: after a Reset or an agent change, until
the screen is next redrawn. A run's schematic also shows no values until a
frame of that run has been drawn. If the run's first frame fails, the readouts
show the state in which the run was opened, and the schematic shows no values.

**For developers.** The schematic takes the top of its scale from the function
that sets the concentration chart's top (`chart_axis_top_percent`), at the
standard top (`ChartCeiling.STANDARD`), and sets no top of its own. Its marks
are the chart's MAC labels at that top (`mac_axis_ticks`). The top's MAC
multiple is a constant (`CHART_AXIS_TOP_MAC`), and § "MAC multiples as a
display unit" gives the reason for 3 MAC.
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

The containers' common width is there because, for sevoflurane, fat's container
drawn to scale would take about 500 px of a View 600 px wide, and four of the
others would take between 1 and 7 px each. The roadmap records the designs that
the schematic was chosen over (`ROADMAP.md` § "v0.7.0 - the schematic").

The run writes the schematic where it writes its readouts, from the same
snapshot of its state. Each amount comes from the snapshot's record for its
compartment (`PL-KFTM`), and that record is read from the amount of agent that
the model holds in the compartment (`agent_amount_l` in `core/`). The schematic
computes no amount of its own. The sum in the share formula is the snapshot's
total of stored agent (`stored_agent_l`).

Each spelling of an amount's unit is defined once, in `app/display_units.py`
(`DisplayUnit`). Whoever writes the first View to print a spelling adds it
there. Every View reads its spellings from that file and defines none of
its own (`test_no_agent_amount_unit_is_spelled_outside_the_units_module` in `tests/unit/test_display_units.py`). The
agent-accounting panel's caption and the "L" beside each of its amounts are
one member of that file.

The empty bar at a run's start is there because computing a share would then
divide by zero, and six zeros would look like real shares.

Shares are shown on a bar rather than by the containers' areas because a
position along a common scale is judged more accurately than an area
(Cleveland WS, McGill R, "Graphical perception: theory, experimentation, and
application to the development of graphical methods", *J Am Stat Assoc*
1984;79(387):531-554, https://doi.org/10.1080/01621459.1984.10478080). Only the
first segment starts at the bar's baseline, but each of the others is judged by
its length, which Cleveland and McGill's ranking still places above area.

The hazard table requires the run's name in the line above the schematic, in
its row on taking one run's value for the other's.

