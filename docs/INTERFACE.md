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
a run first acts at the next tick, so the same slider moves made at two playback
rates produce different runs. `docs/MODEL.md` § "Supported simulation step" quantifies this.

**For developers.** § "Interface boundary" sets the constraints on the
interface's own settings. `docs/MODEL.md` § "The reproducibility guarantee" rules out treating
the playback rate as a model input.

### Halting on a marked crossing

A run may be **marked** in two ways. A *time bookmark* marks an instant of the
case. A *MAC target* marks a height on one named compartment, such as the
circuit. The height is stored as a multiple of 1 MAC of the agent in use.
Marking a height adds nothing to what that multiple asserts about each
compartment (§ "MAC multiples as a display unit"). A mark is a question asked
of the case, not an input to it. A run that halts at its marks computes exactly
the values that an unmarked run computes, element for element. The only thing a mark changes is when
the run stops.

**The run halts on the simulation step that crossed a mark, at every playback
rate.** Every step is tested for a crossing. In this one respect a halt is finer
than anything a learner can do while the run plays. A setting changed during
play first acts at the next point of a grid whose spacing is the playback rate
times 0.1 s (`docs/MODEL.md` § "Supported simulation step"): 0.1 s at 1x and 30 simulated
seconds at 300x. A halt is not on that grid. It lands on the crossing step
itself, at every playback rate. If the crossing were tested once per screen
update instead, the same bookmark would stop at a different concentration
depending on how fast the case was played, and nothing on screen would say so.
Two runs both branched off the case "at 0.8 ×MAC" would then start from two
different states.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**A halt leaves the run paused until the learner resumes it.** No step is taken
while the run is paused, and a setting changed then applies at once. So the
learner gets the safe order, pause, change, resume, without having to know it.
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
halts showing 0.11 ×MAC. The change can be larger on other compartments. Run
the same settings for 120 s with alveolar ventilation at 0 L/min, so that the
alveolar reading stays at zero while the circuit fills. Restoring ventilation
to 12 L/min then makes a 0.10 ×MAC alveolar target halt showing 0.12 ×MAC, two
display counts past its mark. A value one or more display counts past the mark
is therefore correct, and is not a fault in detecting the crossing.
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
trunk, the run that branches are taken from.** When the trunk halted at a
target's exact height on readings that it carries forward step by step, a branch
opened on the halting step could show that target as still running.

**The state of a mark is one of six outcomes.** Each of the last four has its
own wording, because a reader would otherwise mistake it for one of the others.

- **Still running**: nothing has happened yet, and the run can still reach the
  mark.
- **Passed**: a time bookmark at or behind the run's own clock. This outcome
  applies however the clock came to be there. A step may have taken the run
  past the mark, the run may be a branch that opened standing on the mark, or
  the learner may have marked an instant that the case had already run past.
  A passed mark on the trunk is one at which a branch may be taken
  (§ "What this requires of a branch").
- **Reached**: a MAC target crossed by a step that the run has stood on at least
  once. Either the run halted on that step, or it stands on that step or opened
  on it. This outcome belongs to the run rather than to the mark, so a reset or
  a change of agent clears it, because each begins a new run.

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
- **Before this branch opened**: a time bookmark earlier than the instant at
  which this branch opened. A branch inherits its trunk's marks, so such a
  bookmark comes across with the rest, and no step of the branch can reach it.
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
  reached within the supported run length. No step is taken after an error, so
  such a run ran out of supported time first, and a setting caused the error
  afterwards.

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

**For developers.** Nothing marked enters a governing equation, opens a segment
or moves a keyframe.

Crossings are decided from the canonical readings, each of which is one matrix
exponential. A running trunk also holds live readings, carried forward step by
step. These can lie about 1e-14 from the canonical readings, on the other side
of a height, which is why the trunk does not decide a crossing from them.

The height band (`bookmarks.HEIGHT_BAND`) is there because a steady
compartment's canonical reading moves in its last digit from step to step. When
crossings were tested at the exact height, a run with no ventilation and a
target on the circuit at 1.00 ×MAC of a 1 MAC dial halted 965 times in ten
minutes (2026-11-01).

A canonical reading costs about 2 ms, and a whole step about 60 µs, so the live
readings screen each step. A step is tested again from the canonical readings
when its live readings cross a mark, or when either live reading differs from
the height of a band edge by less than 1e-6 of that height
(`bookmarks.LIVE_READING_GAP`). Any other step is let through, because its
canonical readings lie on the same side of each band edge as its live readings.
So the run halts only on a crossing that its halt record names. The widest gap
between the live and canonical readings in a 2 h run at the 0.001 s step
(2026-11-01) was 1.2e-9 of the reading. Scaled linearly to 24 h, the supported
run length, it is 1.4e-8, about a seventieth of the 1e-6 allowance. A marked
instant needs no canonical reading, because whether a step crosses it depends
only on the step's two instants.
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

### The control-input record

The record lists each change to a control that the model runs under.
§ "The control-input timeline" below explains what the record is for, what it
shows and why it takes this form.

#### The control-input timeline

**The timeline records the settings that a run was given.** Each entry is one
change that the model ran under. It gives the simulated time at which the
change took effect, the control, the values before and after, the unit of both
values, and the user adjustment that the change belongs to, such as one drag of
a slider. The timeline is kept with the run and cleared with it. It is shown as
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
part a learner returns to.

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

The interface declares an adjustment when a drag starts, and each change
carries the number of its adjustment. A change that arrives with no declared
adjustment, such as a call from code, gets a number of its own. Code must never
group changes by the time between them. A playback multiplier changes how much
simulated time one drag spans, so any time threshold would group correctly at
one multiplier and wrongly at another.

The limit on a chart's marks is `MAX_CHART_CONTROL_MARKS` in
`app/chart_frame.py`, and the limit on the list's lines is
`MAX_LISTED_ADJUSTMENTS` in `app/dashboard_frame.py`. No record gives the
reason for either value (`PL-N8G4`).

Capping the timeline would not bound memory use, because the run itself holds
one stretch and one keyframe for each accepted change and has no limit either
(§ "The run is that record, and every state is derived from it").

The timeline can be unlimited because it grows with the number of settings
changed, not with the length of the run. Until a drag was recorded only on its
release (`PL-5B1N`), each drag added at most one entry per simulation step,
however fast the slider reported. The number of entries per real second then
depended on the tick rather than on simulated time, so it was the same at every
playback multiplier. On 2026-09-14, under `PL-1PSX`, continuous dragging gave
ten entries per real second at 1×, 5×, 20×, 60× and 300× alike, and a drag made
while the run was paused gave one entry. Grouping the entries for display costs
0.9 ms per frame at a thousand entries and 8.8 ms at ten thousand, against a
200 ms frame. The grouping is recomputed only when the timeline changes. At a
hundred thousand entries it would cost half a frame. Reaching that many took
about three hours of unbroken dragging under the old behaviour, and the
timeline would then be smaller than 9 MB.
<!-- provenance: app/dashboard_frame.py RENDER_INTERVAL_S = 0.2 -->

#### The run is that record, and every state is derived from it

**A run is stored as a record of the settings in force at each moment and the
state at each change.** The settings are the four controls above, together with
the patient and agent parameters that the equations use. Each change has one
*keyframe*, the state at the instant that change took effect. Flows are stored
as they were set, in liters per minute (§ "Time" explains why). Nothing else
about the run is stored. The chart is drawn from the stored settings and
keyframes, so there is no second record that could disagree with them.

**The program computes the state at a single instant in one calculation.** The
settings stay constant over a *stretch*, the time between two changes. The
calculation starts from the keyframe that opens the stretch containing the
instant, so no value need have been stored for the state to be recovered. Within
a stretch, the method in `docs/MODEL.md` § "Selected method (as implemented)" solves the
equations exactly over any length of time, not only over one simulation step.
Each keyframe is computed the same way from the keyframe before it, starting at
the beginning of the run.

**The chart's values are computed a second way, and agree with the state
calculated at a single instant well within the last displayed digit.** To draw
the chart, the program computes the state at evenly spaced instants, one per
column, each from the one before it while the settings stay the same. On
2026-09-07, both ways were compared with a step-by-step run of the simulation.
Their differences from it were about ten orders of magnitude below 0.01%, the
smallest difference that the two-decimal percent readout can show
(§ "Displayed precision"). A test checks the record against the step-by-step
simulation that advances the run. § "The canonical evaluation rule" below
states which of the two ways a stored, exported or branched value may be
taken from.

**For developers.** The record is defined in `core/run_definition.py`. The
method is exact because the equations are linear and time-invariant while every
setting is held constant.

The step-by-step run used for the 2026-09-07 comparison simulated 600 s of
sevoflurane with two setting changes and reached a fraction of 0.0316. The
state at a single instant stayed within 1.8e-14 of that run, and the drawn
chart within 3.7e-15, both as absolute differences in a fraction of one
atmosphere. The test of the record against the step-by-step simulation is the
"Closed-form agreement test".

Storing the run as a record keeps it small. At one sample per fixed 0.1 s
step, a 30-day case takes 3.16 GiB: 25 920 000 samples of 130.8 bytes each
(measured over 20 000 samples of a live run). Stored as its settings and their
changes, the same case takes 1.6 MiB, about two thousand times less. The
1.6 MiB assumes that every day is a busy ICU day with 50 setting changes, which
gives 1 501 stretches over the case.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

With the run stored as a record, the time to draw a chart window does not grow
with the run's length. A one-hour window at 600 columns costs 10.6 ms to draw on
a two-hour run and 13.0 ms on a thirty-day run. Drawing from per-step samples
cost 62.6 ms at four hours and 207.7 ms at twelve.

The number of changes in view does raise the cost of a frame, because each
stretch in view needs its own *propagator*: the matrix that carries the state
across one interval at fixed settings. When no propagators are kept from an
earlier frame, a window spanning the whole thirty-day run at 600 columns costs
14.2 ms with two changes in view, 231 ms with sixty and about 1.1 s with six
hundred. Once the changes outnumber the columns, sampling 600 instants is the
wrong way to draw the run. What to draw instead is a question for the interface.

The number of changes in view sets the cost of the first frame only. Drawing a
window keeps the propagators it used (`RunDefinition.evaluate_anchored`), and
the next window can reuse them. All but three of them cover an interval that
the grid fixes: either the column spacing, set by the time base, or a stretch's
offset to its first grid column, set by the anchoring. The three that change
are the two for the window's bounds and the one for the offset in the stretch
where the window opens. In that stretch, the first grid column is the first one
past the window's left edge. For a window that follows the run, the program
therefore forms two new propagators every frame, and the third only when the
window's left edge has passed a grid column since the frame before. It also
forms those of any stretch newly in view. When the column spacing changes, it
forms every propagator again.

Only the last window's propagators are kept. Each is about 3.1 KB, and six
hundred take 1.8 MiB, so their memory is bounded by one window and does not grow
with the run. A kept propagator is identical, bit for bit, to one formed again
from the same inputs, because it is looked up by all of them: the settings and
the interval. Which propagators are kept depends on the window drawn last, but
no drawn value can depend on that. The kept propagators are therefore not a
second record of the run, and the function that returns the state at an instant
(`state_at`) reads none of them.

The first-frame and later costs were measured on 2026-10-04 on a 24-hour run,
the longest that § "Supported run length" allows, with every setting distinct.
The window spanned the whole run at 600 columns, with its left edge fixed at the
run's opening. With two, sixty and six hundred changes in view, it cost 13.2 ms,
179 ms and 819 ms on its first frame, and 6.3 ms, 5.9 ms and 8.3 ms on each
frame after.

At the dashboard's settings, with kept propagators, the column count sets the
cost of a frame and the number of changes in view does not (measured
2026-10-04). The dashboard redraws every 200 ms (`RENDER_INTERVAL_S` in
`app/dashboard_frame.py`) and shows at most two runs (`MAX_DISPLAYED_RUNS`). It
draws each run with one call (`SimulationController.drawn_window`) at
`max(150, plot width in pixels + 1)` columns (`chart_columns` in
`app/chart_frame.py`). Each cell of the table gives one run's cost per frame
without kept propagators, then with them. The costs are medians of 40 frames,
with a 15-minute window following a 30-minute run at 1x:
<!-- provenance: app/dashboard_frame.py RENDER_INTERVAL_S = 0.2 -->

| Changes in view | 150 columns | 1 069 columns | 2 401 columns |
| --- | --- | --- | --- |
| None | 6.6 ms → 3.9 ms | 12.3 ms → 10.1 ms | 20.3 ms → 18.6 ms |
| Ten | 25.0 ms → 3.5 ms | 28.6 ms → 9.4 ms | 35.5 ms → 18.0 ms |
| Sixty | 135 ms → 3.7 ms | 119 ms → 9.1 ms | 129 ms → 18.8 ms |

With kept propagators, three costs are left. The propagators for the window's
two bounds cost about 1.4 ms each on every frame. Each column costs one chained
product, at about 7 µs. The third cost is forming the propagator for the offset
in the stretch where the window opens. At 1x, it is formed on about one frame in
forty at 150 columns, one in four at 1 069 and one in two at 2 401. From 5x up,
at 1 069 columns or more, it is formed on nearly every frame.

Even so, playing faster adds little. In a later measurement of one run with
sixty changes in view, a frame at 1 069 columns cost 13.0 ms at 20x against
12.0 ms at 1x. At 2 401 columns, it cost 23.9 ms against 22.8 ms. That
measurement's times ran about a quarter above the table's.

Two runs at 2 401 columns therefore take about 40-50 ms of the 200 ms between
redraws. Without kept propagators, two runs with sixty changes in view at
1 069 columns take about 240 ms, which is longer than the time between redraws.
<!-- provenance: app/dashboard_frame.py RENDER_INTERVAL_S = 0.2 -->

#### The canonical evaluation rule

**The state at an instant has one value, whatever route the program took to
it.** A run's states are calculated, and the same state can be reached by more
than one sequence of arithmetic. A fixed 0.1 s step allows only one sequence,
because every calculation must take that step. A calculation that is exact over
an interval of any length lifts that limit, and with it the guarantee of a
single sequence. The rule below restores that guarantee.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

The program computes a state on one of two paths:

- **The canonical path.** A run is divided into stretches, each under one set
  of settings, and the state at the opening of a stretch is its keyframe. The
  state at an instant is one calculation forward from the keyframe that opens
  the stretch containing the instant, over the interval between the two. Each
  keyframe is computed the same way: one calculation per stretch, in recording
  order from the start of the run. So working out one run's state at one instant
  twice does exactly the same arithmetic in the same order. Both results are
  identical to the last digit, not merely equal within a tolerance.
- **The display path.** To draw a chart's evenly spaced columns, the program
  reuses one calculation across the columns inside a stretch, chaining from the
  first column. This reuse makes the cost of each redraw depend on the window of
  columns drawn rather than on the length of the run. The path solves the same
  equations exactly, but does the arithmetic in a different order.

**What each path may be used for.** Every value that is stored, exported,
replayed, compared against another run, or used as the state a branch opens from
is taken from the canonical path. A value from the display path may be drawn,
and it may be used for nothing else. It may not be a keyframe, an exported
figure or a branch's opening state.

**The program enforces the limits on display values.** Anything that takes a
state rejects a value from the display path. A run also refuses one as its
opening state, with an error that says which path the value came from.

**The canonical and display paths differ by far less than the screen can show
for any amount, but by enough to change the agent-accounting panel's residual
lines, which is why the rule is enforced rather than trusted.** In a run of the
model on 2026-09-07, the difference grew with the time that the chart's 600
columns spanned, so it was largest over 24 h, the longest supported run
(§ "Supported run length"). A fraction is shown as a two-decimal percent, and
the paths differ by about a hundred-millionth of its 0.01% step. The
agent-accounting panel displays its three amounts to 0.1 L, and the paths'
running totals differ by less than a ten-millionth of that. But the panel's two
residual lines print the power of ten that a residual lies below, and a
residual is formed from those running totals. At 30 minutes and over 24 h, the
paths' running totals differ by as much as an ordinary passing residual. So a
display value that reached the mass-balance readout would change the power of
ten it prints, and the wrong one would look exactly like an ordinary passing
residual.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**What this requires of a branch.** The roadmap asks that a branched run
reproduce its parent exactly, not merely within a tolerance (`ROADMAP.md` item
12). A run's *definition* is the record its states are computed from: its
stretches and their keyframes. The rule above gives exact reproduction under
two conditions on how a branch is built:

- **A branch opens at a keyframe.** If a branch restarted from the canonical
  state at an instant where the parent has no keyframe, it would compute in two
  calculations what the parent computed in one, and round the same exact
  solution differently. Opening at the start of a stretch reproduces the parent
  to the last digit. A restart's differences depend on where the fork is and how
  far past it one looks, so any figure for them is an example, not a bound. The
  route the program actually takes is bounded, and that bound is zero.
- **The branch's definition opens *at* the fork instant, on the case's own time
  axis**, carrying the parent's keyframe. Parent and child then name the same
  instant of the case. Each computes its interval as that instant minus the
  opening of the stretch that holds it, from the same keyframe by the same
  subtraction. So the reproduction follows from how the branch is built, not
  from the code that asks for a state converting time correctly.

Each condition rules out a defect that a plausible way of building branches
would introduce. The first rules out a restart between keyframes. The second
rules out a definition that opens at a zero of its own. All code that asks for
the branch's state at an instant would then reach that instant by subtracting
the fork instant from the case's time, and that subtraction can change the last
digit. The branch would compute over a slightly different interval from its
parent, and give a result that differs in its last digit.

**A branch's simulated time is the case's time, measured from induction.** It
continues the parent's time rather than restarting at the fork. This one time
is what the clock displays and what stamps every recorded setting change. The
chart's axis, the supported run length and the times of the definition's
stretches and keyframes are measured in it too. Nothing anywhere converts
between two times, so there is no conversion to get wrong. Continuing the case's
time is also a matter of correctness, because uptake and distribution depend on
the time since induction. A branch that counted from zero would place the
patient at the wrong point on the uptake curve, on the clock, the control marks
and the axis at once. That is the correct value shown under the wrong patient
context, which the project's safety-critical standard (`CLAUDE.md`) counts as a
failure in its own right.

**A fork at a bookmark cannot open its definition both at a keyframe and at the
fork.** A control event, a change of a setting, is a keyframe, so a fork there
could meet both conditions. A bookmark is a mark the learner sets at an
instant, and the run halts when it reaches the mark. A bookmark's instant
usually is not a keyframe. On a 120 s run with two control changes, only 3 of
the 1 201 instants where a halt could land are keyframes. Meeting both
conditions there would mean *recording* a keyframe where the run halts. That
makes the branch exact against its parent, but it changes the parent's later
results: 48 of 54 values differ from the same case built without the mark.
Marking a run would then change the run, which the project's determinism
requirement (`CLAUDE.md`) forbids.

**So every fork opens its definition at the keyframe at or before the fork
instant.** This keeps the first condition and relaxes the second. The branch's
clock and its running simulation are still at the fork. Exact reproduction
still holds, because it never depended on the definition opening *at* the fork.
It depends on parent and child computing each interval from the same keyframe
by the same subtraction, and opening where the parent's own stretch opens gives
exactly that. The one time axis is not relaxed: the definition still opens at an
instant of the case's own time, and the clock still continues the parent's. So
code that asks for a state still never subtracts the fork instant, which is the
subtraction that can change the last digit. The only change is that the
definition now opens earlier than the fork instant, on the same axis. On
2026-09-14, exact reproduction held on a 3 600 s sevoflurane run of the model
with changes at 300 s and 600 s, forked at a bookmark at 655.3 s. Across nine
state values at six times out to an hour, 0 of 54 differed. The trunk, the
case's main run, stayed exactly identical to the same case built without the
bookmark.

**A branch taken where a run is paused or stopped runs under the settings the
dials show there, and records the settings the run had on its way there as
where it came from.** The two can differ, because the learner can turn a dial
while the run is paused. Take a sevoflurane run at 2% that is paused at
10 min, after which the learner turns the vaporizer to 3%. The run reached
10 min under a stretch of settings at 2%, and that stretch cannot change. The
3% starts a new stretch at 10 min that has not run yet. Any change made during
the pause goes into that new stretch, so turning the dial again before the
next step replaces the 3%. A change during the pause never adds a second
stretch at the same instant. Below, the *reaching stretch* is the stretch that
ran up to the instant, the 2% one here. The *stretch in force* is the stretch
that runs from the instant on, the 3% one here. Where nothing changed at the
instant, the two are the same stretch. The halt record lists the marks a run
stopped on. The three ways of branching (at a keyframe, where a paused run
stands, and at a mark), a branch's reset and the halt record all follow one
rule:
<!-- not-restated: 2 % -->

- **A branch's provenance, the record of where it came from, is the reaching
  stretch.** A fork at a control event is built the same way as a fork at a
  bookmark, so the construction above serves every fork. Except at the case's
  opening, which the paragraph after this list covers, nothing the parent later
  does at the fork can replace the stretch that the branch records as its
  provenance.
- **All three ways of branching run under the stretch in force at the fork,
  which is what the dial says.** So "Branch here" opens with the dials as they
  stand when it is taken. A branch at an instant that the trunk has already
  passed runs under the settings the trunk had as it left that instant,
  including a change made at that instant and no change made later. On a run
  that a mark has halted, a branch taken before the learner changes a setting
  there runs under the old setting. A branch taken after that change runs under
  the new one, as do the branches taken from that instant's mark and keyframe
  entries in the "From" selector. A branch opens at what the dial says and does
  not go back to the previous setting.
- **The branch's timeline opens with the parent's changes at the fork.** The
  branch's definition records, as a change at the fork, each setting it runs
  under that differs from its provenance. Its control timeline opens with a
  copy of each change the parent recorded at the fork. After the case's
  opening, those copies are the settings that differ between the reaching
  stretch and the stretch in force, so the definition and the control timeline
  agree. At the case's opening, the copies are the changes the parent made
  before Start, each shown from the value the parent's timeline starts at.
  Either way, the branch's timeline shows the settings it opened under,
  whatever the trunk later does at the fork instant. No later change merges
  into a copied entry or removes it, and a change the learner makes at the fork
  is recorded after the copies.
- **A reset branch keeps its settings and the entries it opened with.** Reset
  keeps the settings, restores the fork state and reopens the branch at the fork
  on the same provenance. An entry the branch opened with records where the
  branch began, not something done to it since. A branch reset after the learner
  has dialled something new stands at the fork state under settings its parent
  never used. Because the definition still opens at the parent's keyframe under
  the parent's settings, the new setting is recorded as a change at the fork, in
  the definition and in the branch's control timeline. The keyframe that change
  opens is the fork's own state. So the trace starts where the readouts say the
  branch is, and the parent's stretch stays the parent's. § "Reset behavior"
  describes the timeline of a reset branch, and
  § "Discarding a run, and the questions that guard it" says which entries
  count when the trunk's Reset asks before discarding it.
- **The halt record names the marks as they are.** A run's halt record lists
  the marks crossed by the step it stopped on: the step that halted a trunk, or
  the step that reached a branch's fork. The record is worked out again against
  the current marks whenever it is read, as the mark outcomes are. So a mark
  removed and added back under another label is named by its new label.

At the case's opening no step has run yet, so the opening stretch is both the
reaching stretch and the stretch in force. A change the trunk makes at the
opening still replaces the opening stretch, even after a branch was taken
there. The branch's provenance then names settings the trunk no longer opens
under. That provenance is still true, because the opening keyframe is a state
that no setting produced, and the branch did run under those settings from
there. Its own timeline still states them, as its copy of the trunk's changes
made before Start.

**Returning to a mark the run has already passed is a bookmark fork, taken
late.** Consider a learner paused at three hours who marks the one-hour point
and goes back to it. The run holds no keyframe at that instant and is not
standing on it, so neither branching at a keyframe nor branching where the run
stands applies. Building a bookmark fork needs neither a keyframe at the
instant nor a run standing on it. The state at any instant the run has reached
is the run's definition evaluated there, and standing on a halt only ever
served to name the fork instant. So returning to a mark builds a bookmark fork
at the step that reached the mark. Such a branch has six properties:

- **It reproduces the case's state at the mark in every value.** The branch
  opens from the canonical state there, inside the parent's own stretch. Every
  later instant is one calculation from the same keyframe that the parent
  calculates from, until the branch's own settings change. On a run marked at
  60 s after its clock reached 180 s, the branch agrees with its trunk at all
  601 instants from the mark to a minute past it.
- **It is the branch the halt would have given.** A mark set before the run
  passed it halts the run, and the run is forked at the halt. The same mark set
  after the clock went past it is forked here. The two branches' whole
  provenance is equal: stretch, fork state, step count and the step the fork
  ends. Taken at the same moment, both run under the same settings, including a
  change the trunk made while it stood on the halt. The branch also stays the
  halt's branch for a mark added later. Every run checks which marks were
  crossed by the step it opened on or stands on, against the marks as they are
  whenever its mark outcomes are read. So a mark added inside that step is
  treated the same on the trunk and on the branch, whether it was added before
  the branch or after. Every way of forking checks that step in the same way,
  including a fork at a control event. So a branch taken at a keyframe the
  trunk halted on opens on the marks that the halting step crossed, as a branch
  taken where the run stands does.
- **It leaves the trunk unchanged.** Nothing is recorded where the mark is.
  That is what kept the bookmark fork from changing the run it marks.
- **It does not open at the typed instant.** The fork is the end of the step
  that reaches the mark, at the mark or one step past it: the instant a halt
  would have stopped on. For a typed 45.3 s at the 0.1 s step the fork is at
  45.300000000000004 s, and for a typed 45.35 s it is at 45.400000000000006 s.
  The rule that decides which step crosses a mark finds the fork, and the
  typed value is not rounded. Rounding would put a mark that lies inside a step
  onto the step before it. The branch treats its mark as passed, not as "before
  this branch opened", even when the fork is one step past the mark, because
  the branch opens standing on the step that crossed the mark.
- **It does not replay what the trunk did afterwards.** The branch continues
  under the settings the trunk had as it left the mark's instant, until the
  learner changes something. Its own control record holds only a change the
  trunk made at that instant, if there was one. The trunk's later changes stay
  the trunk's. The reference simulator's rewind works differently. It returns
  to time zero, keeps the recorded settings and plays them back as it runs
  (Philip JH, *Workbook for Gas Man®*, Med Man Simulations, appendix E,
  "Replaying Simulations", printed pages 186-87). So it takes the trunk back and
  truncates it at the mark. Returning to a mark here forks instead, so the run
  that happened stays on the axis beside the alternative.
- **It opens with the canonical state's readouts, not the ones the trunk showed
  when it stood there.** A running case displays its live state, calculated one
  step at a time from the opening. Every branch opens from the canonical state.
  Over three hours of a run of the model on 2026-10-12, the two agreed to less
  than a billionth of the 0.01% that a two-decimal percent can show, so no
  reader can see the difference. The same holds for a fork at a control event
  or at a halt.

<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

A mark still ahead of the clock is refused rather than reached. The case holds
no state there yet, and a fork there would be a prediction drawn as if it were
a run. The learner reaches such a mark by running on, and the halt there is
then the fork.

**A branch taken where a paused run stands is built as a bookmark fork, with
the clock naming the instant.** The clock always stands on a whole number of
steps, and the construction above reproduces the case at any instant the run
has reached. So a branch can be taken wherever the trunk is paused, on a halt
or anywhere else. It forks from the canonical state there, inside the parent's
own stretch, and records nothing on the trunk. The branch opens standing on the
marks crossed by the step that ends there. Those are checked again against the
marks as they are now, as for a return to a mark, and are not read from a
halt's record, which names only what was marked when the run stopped. Three
kinds of run are refused. A running run is refused, because where it stands
moves with every step. A failed run is refused, because a failure is not a
pause. A run at the supported run length is refused, because it has no step
left for a branch to take.

**So no divergence is left over to bound, and there is nothing to show a
learner.** The roadmap's definition of done for v0.5.0 asks this document for
"the bound on any divergence that could not be eliminated" (`ROADMAP.md`). On
the canonical path, no such divergence survives. A branch and its parent agree
exactly at every instant they share, for a fork on a keyframe and for a fork
between two keyframes. Two divergences do exist. One is the display path's,
and the program refuses that path's values for anything but drawing. The other
is a restart between keyframes, and no branch this program builds restarts
that way. A bound of zero drawn on screen would tell a learner there is
something to watch where there is nothing. § "What a branch comparison
asserts, and what it does not" says what a comparison of the two drawn runs
may claim, and the zero bound is one of those claims.

**A branch's chart starts at the fork, not at the earlier keyframe where its
definition opens.** Every fork therefore carries the fork instant explicitly,
and the chart clips the branch's drawn range there. Clipping at the
definition's opening would draw the branch back across time it never lived
through, showing the trunk's course under the branch's name. That would put
the right numbers in the wrong patient context, a presentation failure that the
safety-critical standard names. The fork instant also decides that a mark is
out of the branch's reach.

**One time axis puts a trunk and its branch on the same columns.** Drawn
columns sit on multiples of the column spacing in the case's own time
(§ "What the chart draws"). So a trunk and a branch are drawn at the same
instants without the display path being told anything. On 2026-09-14, the
program drew a 120 s sevoflurane run and a branch of it on a 13-column axis
spanning 120 s, with the fork deliberately off the grid at 55.3 s. All 8 of the
branch's columns were instants that the trunk also draws. With the branch
anchored to its own zero, it drew 55.3, 65.3, 75.3 … and shared 2 of 8, so the
two traces could not be read against each other at matched points.

**A bookmark branch draws exactly one column that its trunk does not, the fork
itself** (run of the model on 2026-09-20, on a 120 s axis at 150 columns). The
55.3 s fork above lands on the trunk's own columns, because a control event is
drawn on every run that has one. A bookmark's instant is not a control event,
so the trunk draws it only if it happens to fall on the grid. The branch always
draws it, because it is the left end of the branch's drawn range. Everywhere
else, the two traces can still be read against each other. The value at that
one column is the case's own state there, which both runs contain. So the extra
column marks the instant at which the two stop being the same run, not a
disagreement about that instant.

**At the columns they share, a bookmark branch's drawn values can differ from
the trunk's in the last digits, while a control-event branch's are exact.** The
display path chains one calculation across consecutive columns. It restarts at
the edge of the drawn range or at an event column, so a branch restarts from
its keyframe at its own left edge. For a fork at a control event, that instant
also opens a stretch on the trunk, and both restart there. A bookmark's instant
does not open a stretch on the trunk. So the trunk chains straight through it
while the branch restarts, and the same exact solution comes out of arithmetic
in a different order. On 2026-09-20, the program forked the 3 600 s case above
at the 655.3 s bookmark, advanced both runs 1 200 s, and drew both on a
601-column axis from zero to 1 800 s. Of the 3 438 values at the 382 columns
the two runs share, 2 977 differed. The worst difference in a fraction was
eleven orders of magnitude below the 0.01% to which § "Displayed precision"
resolves a fraction. The worst difference in a running total was twelve orders
below the 0.1 L to which the agent-accounting panel displays an amount. A
branch forked at the 600 s control event instead differs at none of the
columns it shares.

**Branches still reproduce their parent exactly, because that guarantee rests
on the canonical path and not on the display path.** Calculated on the
canonical path at those 382 instants, the two runs agree exactly, with 0 values
differing. On the 45.3 s case above, across the 240 columns that the two runs
share, 0 of 2 160 canonical values differ, while 1 909 of the same 2 160 drawn
values do, and the fork is the one extra column. § "What a branch comparison
asserts, and what it does not" says what this means for a trace of the
difference between two runs.

**For developers.** The canonical path is `RunDefinition.state_at` in
`core/run_definition.py`. The display path is `RunDefinition.evaluate`, and
the chart's version of it is `RunDefinition.evaluate_anchored`. Each
calculation over an interval uses a matrix for that interval, its propagator.
The chart's version also keeps the propagators it used, for the next frame. A
kept propagator is the matrix that forming it again would give. So keeping
them changes no drawn value, and the canonical path reads none of them.

Code that takes a state rejects a display value because the display path
returns its states wrapped in a type that is not a state vector
(`DisplayState`). The run definition's check of an opening state looks for that
type by name, so its error names the path instead of reporting a length
mismatch. The wrapper is not a subclass of the state tuple, because some code
that will take a state has not been written yet. Code without a check of its
own rejects only a value whose shape is not a state's, and a subclass would
pass it.

The table gives the worst absolute difference between the canonical and the
display result at the same instant, over the 600-column window a chart draws.
The run is the sevoflurane run with four setting changes in
`tests/reference/test_canonical_evaluation.py`, simulated on 2026-09-07. That
test checks both quantities against bounds an order of magnitude above these
values:

| Span | Six compartment fractions | Two cumulative accumulators |
| --- | --- | --- |
| 1800 s | 1.0e-14, of 0.0301 | 3.1e-12 L, of 2.06 L |
| 24 h | 8.0e-13, of 0.0300 | 3.1e-09 L, of 30.26 L |

<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

A wider span is worse because its columns are further apart, so each chained
calculation covers a longer interval. The second row is therefore the worst
that a supported run reaches at this column count.

The three ways of branching are `SimulationController.resumed_at()` at a
keyframe, `resumed_here()` where a paused run stands, and `resumed_at_mark()`
at a mark. Each opens the branch's definition at the keyframe of the reaching
stretch, which it records as `ResumePoint.segment` (from
`RunDefinition.reaching_segment_at`). The stretch in force comes from
`RunDefinition.segment_at`. The copies of the parent's changes at the fork are
`RunRecord.opened_with`. The rule that decides which step crosses a mark is
`TimeBookmark.steps_to_reach`. In the first hour, 12 767 of the 36 001
one-decimal instants are not a whole number of steps in binary, as 45.3 s is
not. Stepping (`advance()`) and drawing (`drawn_window()`) pass case time
straight through to the definition.

Continuing the case's time keeps simulated time to the single multiplication
that `docs/MODEL.md` § "Simulated time is a count of steps, not a running total" describes. A
branch's instants, in its run definition and on its clock, are the case's step
count times the step, not the fork instant plus a second total.

The fork instant is stored with the branch's provenance (`ResumePoint.fork`),
and the controller reads it as `SimulationController.began_at_s`: zero on a
trunk, the fork instant on a branch. Drawing (`drawn_window()`) clips the
window's lower bound there, with `first_s = max(start_s, self.began_at_s)` in
`app/controller.py`. The bookmark code (`app/bookmarks.py`) is also given the
fork instant, to decide that a mark is unreachable. The fork instant is kept
apart from the definition so that no code infers it from where the definition
opens (`opened_at_s`, `run_segments[0].opening.instant_s`), the keyframe at or
before the fork.

A setting dialled before a reset is recorded as a change because choosing the
definition's opening from the settings at the reset would depend on the order
of two reversible acts. The sequences *dial, dial back, reset* and *dial,
reset, dial back* leave the same branch: the same settings, live state and
displayed values. If the opening were chosen at the reset, the second sequence
would open the definition at the fork rather than at the keyframe. That branch
would then compute in two calculations where the parent took one, and silently
stop reproducing the parent. On 2026-09-20, 40 of 45 values differed across
five probes, the worst by 1.21e-15. When the dial is recorded as a change, the
dial-back is collapsed by a rule the run definition already has: a dial moved
and moved back before a step ran cancels out. The branch is then where it
started. After a reset that *kept* the new setting, the remaining difference is
0.000249 on the same probes. That is a different management of the case, not
rounding, and recording the dial as a change keeps the two apart.

These are the figures behind the statements above:

- **Headroom against the screen and the residual lines.** A two-decimal percent
  resolves 1e-4 (§ "Displayed precision"). That section records passing
  residuals below 2.1e-11 L, from branches simulated for 30 minutes. The
  display path's accumulator difference at 1800 s is 3.1e-12 L. Over 24 h the
  worst simulated relative residual was 3.08e-12, which on amounts of tens of
  litres is of the order of 1e-10 L. The accumulator difference at 24 h is
  3.1e-9 L.
- **A restart off a keyframe.** On the run in
  `tests/reference/test_canonical_evaluation.py`, a restart at 1 234.5 s
  changed 1 109 of the 1 269 state values in their last digits. At the 141
  instants at or past the fork (2026-09-21), the worst difference was 7.8e-15
  as a fraction and 1.9e-12 L on an accumulator. An earlier restart on the same
  run differed by up to 5.3e-13 in an accumulator (2026-09-07).
- **The subtraction.** With a fork at 900 s, `(900.0 + 1e-6) - 900.0` is
  9.999999974752427e-07 and not 1e-6. So a child asked for its own `1e-6`
  would land one unit in the last place away.
- **One time axis (2026-09-14).** A branch of a 120 s sevoflurane run, forked
  at the 60 s keyframe and advanced 60 s further, agrees with its parent at all
  601 case instants that the two share. Both are given the same number, the
  case's own `steps × step`, and neither does arithmetic on it. A definition
  opened at a zero of its own, and asked for its own `steps × step`, differs
  from the parent at 354 of those 601. Both are exact solutions of the same
  equations, but only the first is the same sequence of floating-point
  operations, which is the sameness `ROADMAP.md` item 12 asks for. A
  definition opened at its own zero could match too, but only if every caller
  subtracted the fork instant itself, and nothing enforced that. With one time
  axis, the 354 mismatches cannot arise.
- **Drawn values at a bookmark fork (2026-09-20).** The worst differences were
  7.70e-16 as a fraction and 8.17e-14 L on an accumulator.
- **Drawn values of two identical runs.** The worst of the differing drawn
  elements was 2.7e-15.
- **A branch's opening readouts.** Over three hours (2026-10-12), they agreed
  with the trunk's to 4.9e-14 as a fraction.
- **Tests.** The test of the canonical path
  (`tests/reference/test_canonical_evaluation.py`) checks that a fork at a
  stretch boundary reproduces the parent bit for bit. It checks forks on and
  between keyframes over 207 instants, against a restart at the fork, which
  does not agree. The controller's test (`tests/integration/test_controller.py`)
  checks the same over 201, 301 and 601 case instants, and over the 240 drawn
  columns that a trunk and a bookmark branch share. Its run marked at 60 s after
  the clock reached 180 s is the return-to-a-mark example. The controller's test
  also checks the 45.3 s case, where the canonical values agree and the drawn
  values differ. Both files test the two results of 2026-09-14: the reproduction
  at 601 instants and the 8 shared columns.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- not-restated: 900 s -->

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
the refusal beside the control that caused it. The ranges belong to the model, so the model
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
<!-- provenance: data/patients/reference_adult.json default_cardiac_output_l_min = 5 -->

**The maxima for fresh gas flow, ventilation and cardiac output come from no source.** Each was
chosen as the edge of the settings that the interface offers and that two tests cover
(§ "What a setting outside the range costs").

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
  $`F_A/F_I`$ at five minutes is 0.41 at 10 L/min, 0.49 at 5 L/min, 0.58 at 2.5 L/min, 0.70 at
  1 L/min, and 0.86 at zero. Refusing zero would cut the demonstration off one step before its
  clearest case. The same argument applies to alveolar ventilation at zero, which is apnoea.

<!-- not-restated: 10 L/min, 5 L/min -->

**A run at zero cardiac output shows where the agent goes when perfusion stops, and nothing
else.** With no uptake, alveolar gas approaches the inspired gas, and the tissues keep the agent
they already hold. The run does not model circulatory arrest, cardiopulmonary bypass or ECMO, and
`docs/MODEL.md` § "Known limitations" excludes all three. Nothing about the patient's condition follows from such
a run.

**No compartment stores a blood flow, so none can disagree with the cardiac output.** A tissue
group's blood flow is its perfusion fraction times the patient's cardiac output,
$`Q_i = f_iQ`$, and the venous pool's flow is the cardiac output itself.

**A tissue's perfusion fraction is fixed once its group is built.** The patient's three
fractions are checked to sum to 1 only when the patient is built, so a later change to one
fraction would leave tissue flows that no longer sum to the cardiac output. A change to a
fraction is therefore refused.

**For developers.** Each flow is its own subclass of `float`, declared with its range in
`core/supported_ranges.py`: `FreshGasFlow`, `AlveolarVentilation` and `CardiacOutput`. Only a
type's constructor runs the range check, and nothing else produces a value of the type. A flow
is therefore checked once, when its value is made, not where it is stored or used. A flow
outside its range raises a `SimulationConfigurationError`, so a script, a notebook and a test
meet the same error as the interface. The error marks a refused argument, which
`docs/MODEL.md` § "Supported simulation step" distinguishes from a step that broke down.

A flow is kept from one step to the next, and it can enter the simulation five ways: through a
setter of the agent uptake system (`AgentUptakeSystem`), through the setter of the compartment
that holds it, through that compartment's constructor, through the settings record
(`UptakeEquationSettings`), or by assignment straight onto the compartment's field. The run's
definition (`RunDefinition`) is built from the settings record, and keeps each change as a new
record. Every field and argument that holds a flow requires the type, in the compartments, the
settings record, the application's snapshot and the setters that feed them. A plain `float`
passed to any of the five ways in is refused, whatever its value, with a `TypeError` that names
the type to build. So no way in has to remember the check. The control timeline stores plain
`float` values, and a setting read back from it is rebuilt as its type. Arithmetic on a flow
returns a plain `float`, so a value calculated from a flow is never taken as checked. The
simulation step is a checked type in the same way (`SimulationStep`).

A tissue group's perfusion fraction and its blood flow have checked types too, in
`core/blood_flow.py`. The perfusion fraction (`PerfusionFraction`) is checked as above 0 and at
most 1 when it is created. The blood flow (`BloodFlow`) is created only by multiplying a
`CardiacOutput` by a `PerfusionFraction`, and it has no check of its own. Until these types
existed, three places each checked a blood flow by hand as finite and not negative, and each
accepted a flow that no supported cardiac output can give.

**A settings record loaded from a saved file runs its constructor's checks.** Python restores a
pickled or copied frozen dataclass through `__setstate__`, which by default writes each saved
value straight into its field without running `__post_init__`. Instead, the settings records for
the uptake equations and for a tissue group's equations rebuild themselves from the saved values
(`UptakeEquationSettings`, `TissueGroupEquationSettings`). A saved value that the constructor
would refuse is therefore refused on load, at every pickle protocol, with the constructor's own
exception. The rebuild catches a wrong saved value. It does not protect against a pickle made to
attack, because a pickle can call any importable function. Nothing in `src/` loads a pickle yet.
The other records that a saved run holds, such as `RunDefinition` and `Keyframe`, do not yet
check their values on load.

**A value assigned straight onto a flow field is refused at the assignment.** In `src/`, the
type checker (`mypy`) refuses `circuit.fresh_gas_flow_l_min = 1000.0`, and the compartments' own
methods write the field only from a checked flow. A plain `float` can still arrive from code
that the type checker does not cover, such as a notebook, a test or a value typed `Any`. If the
check came any later, the snapshot that the display reads would already have copied the value,
and the readouts would have shown it. So the flow's check (`require_*`) runs in the `__setattr__`
of the circuit, the alveolar compartment and the patient's compartments (`BreathingCircuit`,
`AlveolarCompartment`, `PatientCompartments`). The write is refused with the same `TypeError` and
message as the other ways in, and the field keeps its previous value. For a flow, the write checks
the type. The fresh gas flow's write also checks the flow against the machine's range
(§ "The model's envelope and a machine's deliverable range are two claims"). The dataclass
constructor, `dataclasses.replace`, a copy and a pickle all write through `__setattr__`, so the
compartments' constructors run no check of their own. A copy and a pickle write through it
because each compartment is a `slots=True` dataclass, which they restore one field at a time. A
`__dict__` would be updated without calling `__setattr__`.

**Every checked type but `BloodFlow` is built from an `int` or a `float` and nothing else, with
no sign at zero.** `BloodFlow` is built from a `CardiacOutput` and a `PerfusionFraction`, and it
refuses a number. One file states what every other checked type is built from
(`core/checked_number.py`), and `FreshGasFlow`, `AlveolarVentilation`, `CardiacOutput`,
`PerfusionFraction`, `Fraction`, `Percent` and `CaseInstant` all build through it. They accept
an `int` or a `float`, subclasses included, so a NumPy double passes. A `bool`, a `Decimal` or a
string is refused with a `TypeError` that names the value and
its type, before any comparison reads it. So is a value already built as another checked type,
such as a `StepCount` or a `CaseInstant` passed to a flow's constructor, because such a value is
a swapped argument. Minus zero is stored as zero, so a readout never shows `-0.0 L/min`. The
range check is one chained comparison against both ends, ends included. A NaN fails both
halves, and an infinity fails one. An `int` too large for a `float` is compared exactly and
refused as outside the range, in the setting's own words. The step count (`StepCount`) refuses
anything that is not an `int` in the same way, with a `TypeError`.

Two more checks refuse a `bool`, a `Decimal` or a string, for each amount, flow and step that
they check: the checks for a positive and for a non-negative finite number
(`require_positive_finite`, `require_nonnegative_finite` in `core/validation.py`). The
simulation step is built through the first of them. These two checks do not refuse a value
built as another checked type, and they leave minus zero as it is. They refuse an `int` too
large for a `float` by name, as outside what a `float` can hold, before `isfinite` reads it,
because they have no supported range to compare it against.

**The circuit and the settings record compare the vaporizer dial with its maximum through one
shared check.** The delivered concentration has the same five ways in as a flow. Its bound is
the maximum of the agent's vaporizer, not a constant of the model, so no type can carry it.
Only a record that holds both the dial and the maximum can check one against the other. The
circuit (`BreathingCircuit`) holds both. The settings record (`UptakeEquationSettings`) carries
the maximum (`max_delivered_concentration_percent`) beside the dial, as a required field with no
default. Each record's constructor refuses a dial above the maximum through
`require_within_vaporizer_maximum` in `core/validation.py`. So both records refuse in the same
words, and the rule is written once. Both accept zero, which is the vaporizer off, and the maximum
itself. The uptake system's settings method reads the maximum off the circuit
(`AgentUptakeSystem.equation_settings()`), so each stretch of a run records the limit that its
dial was set under. The propagator cache key carries the maximum with the rest of the record,
although the matrix never reads the maximum.

A tissue group's blood flow is computed in one place (`TissueGroup.blood_flow_l_min_at`). Each
compartment is given its blood flow, rather than storing it, when it computes its time constant
or takes a step (`time_constant_s`, `advance()`), as $`Q_i`$ is given to
$`\tau_i = V_i\lambda_{i:b}/Q_i`$. So every flow follows the cardiac output through
`set_cardiac_output`, a copy, `dataclasses.replace` and a pickle, and a copy made at another
output leaves the original's flows unchanged. A tissue group is given a `BloodFlow`, and the
venous pool is given the cardiac output. Each refuses a plain `float`, whatever its value, with
a `TypeError` that names the type to build. A tissue group is given the blood:gas coefficient as
well as its flow, so that it keeps no copy that could disagree with the coefficient
(`docs/MODEL.md` § "Blood compartments"). A new cardiac output written onto the field of a built patient is
refused, and the refusal names `set_cardiac_output`, so that cardiac output has one way in.
Writing the value that the field already holds is accepted.

A tissue group refuses a second write of its perfusion fraction (`TissueGroup`), and the refusal
says to build a new patient with the new fractions. A tissue group written onto a built patient
is refused unless the fractions, with the replacement in place, still sum to 1. A copy or a
pickle writes the fraction once, onto a new object, so it is accepted. Neither a tissue group nor
the patient lets a field be deleted, because a write after the deletion would bypass both checks.

The settings record also refuses tissue flows that do not sum to the cardiac output. Only a
fraction forced past its check, with `object.__setattr__`, can reach that refusal. At the next
step, the method that advances the simulation (`advance()`) raises the refusal as a
`SimulationNumericalError`, as it does for every check that fails inside a step. Through the
simulation controller (`SimulationController`), the same refusal comes before that step begins,
as a `SimulationConfigurationError`. The controller finds that the simulation's settings no longer
match the run's definition, and builds the settings record to report why before it takes the step.
At Reset, the controller refuses before it clears anything (`SimulationController.reset()`), and
the interface halts the run. A setting change that the record refuses is undone, so the
compartment, the run's definition and the timeline keep the previous setting. No setting change
repairs such a fraction (§ "Reset behavior"). Putting the fractions back, or building a new
patient, is the only repair.

Code in `app/` changes settings only through the simulation controller, which saves the whole
settings record at each change. Before each step, in the method that advances the run
(`SimulationController.advance()`), the controller compares the current settings key
(`AgentUptakeSystem.settings_key()`) with the key saved with the last settings record.

The agent selector and the sliders read the snapshot only inside handlers guarded by the halt
gate (`halt_gate` in `app/halt_gate.py`). A halt resets the selector from the run's settings
record, because the selector would otherwise read the agent from the refused snapshot. If a halt
comes before the screen is redrawn, every withheld value is hidden before the dials are written,
because writing a dial can raise an exception.

**The alveolar and tissue agent amounts are checked against the compartment's capacity when
they are written.** The check runs in `__setattr__`, as a flow's check does. The partial
pressure setter (`set_partial_pressure_fraction`) takes a checked `Fraction`, so no setter can
store an amount greater than the capacity. An assignment onto the field could, and the resulting
partial pressure above one atmosphere would be refused only two layers later, when the
controller's snapshot built the `Fraction` (`SimulationController.snapshot()`). Whether an
amount fits the volume that holds it is for the compartment to check, not for either value alone
(`.claude/rules/core-domain.md`). So the alveolar compartment and each tissue group check it
where the amount is stored. They check the constructor, the setter and a direct assignment
alike, in the constructor's own words, and the field keeps its previous value.

The one write that bypasses this check is a rollback, which puts back what the compartment held
when the step began (`restore_state`). A rollback that could raise would replace the step's own
error. It would also leave later compartments still holding the failed step (`docs/MODEL.md` § "Step
atomicity"). Only a write that bypasses the capacity's own check can shrink a capacity below a
held amount, because each value is checked first by its own write. The rollback leaves that case
to the snapshot, whose amount-over-capacity fraction refuses it visibly. No supported setting
makes such a write. The tests reach a refusing snapshot by replacing the fraction that the
snapshot reads.

**Every checked field of the five run records goes through its constructor's checks when it
is written.** The five are the circuit, the alveolar compartment, each tissue group, the venous
pool and the validator (`BreathingCircuit`, `AlveolarCompartment`, `TissueGroup`,
`VenousBloodCompartment`, `AgentSimulationValidator`). Each checks every field in `__setattr__`,
the constructor's own writes included. So no constructor runs a check of its own, and nothing is
written when a value is refused. A relation between two fields is checked by whichever field is
written second. There are four such relations: the dial against the vaporizer's maximum, the
fresh gas flow against the machine's range, the machine's range against the model's supported
range, and each compartment's agent amount against its capacity. A volume or a partition
coefficient too small for the agent that the compartment holds is therefore refused, as the
circuit's volume setter (`set_circuit_volume`) refuses a circuit volume too small for its agent
(`require_room_for_the_agent_held` in `core/validation.py`).

The circuit stores its agent as a fraction of its volume. So a circuit volume assigned directly,
bypassing the volume setter, cannot overfill the circuit, and is not refused. Instead the agent
amount changes with the volume, and the circuit gains or loses agent that no flow carried. The
next step then halts on the mismatch that the mass-balance check finds (`docs/MODEL.md` § "Mass-balance
identity"), and the step is rolled back.

The venous pool's rollback bypasses its check, for the same reason as the alveolar and tissue
rollback. The circuit and the validator roll back through their checks. Those checks cannot
refuse a saved state (`capture_state()`), because nothing that the saved values are checked
against can have changed since.

The dashboard refuses a run that opens between two slider steps when it sets up its controls.
One test checks this for an opening ventilation or cardiac output
(`test_an_opening_ventilation_or_cardiac_output_off_the_slider_grid_is_refused` in
`tests/unit/test_dashboard_frame.py`). Three tests in the same file check the three cases of the
fresh gas flow control described below:
`test_the_fresh_gas_flow_control_narrows_to_a_declared_machine_range`,
`test_a_declared_range_off_the_display_grid_offers_only_settings_inside_it` and
`test_an_opening_fresh_gas_flow_off_the_slider_grid_is_refused`.

The zero-ventilation, zero-cardiac-output and zero-tissue-flow tests in `docs/MODEL.md` § "Required tests"
specify how the equations behave at zero flow.

The flow maxima began as the interface sliders' maxima, before the model declared any range.
Nothing in the equations breaks at 10.01 L/min, because the calculation is exact at any flow.

**The supported ranges are the verification domain: the settings over which the model is checked
against an independent solution.** The test in `docs/MODEL.md` § "Independent-solution test" runs its
trajectories across everything these ranges allow. Its worst disagreement with the independent
solution comes on a trajectory that holds cardiac output at zero. Narrowing a range would take
that worst case out of reach, and widening one would admit trajectories that were never checked.
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
flow maxima: the fastest time constant in `docs/MODEL.md` § "Alveolar gas" and `docs/MODEL.md` § "Supported simulation step",
the corner sweeps in `docs/MODEL.md` § "The numerical envelope" and `tests/unit/test_numerical_envelope.py`, and
the figures below.

Three tests stop a range from changing unnoticed. The first is the test above, which restates
all six flow limits and fails if the model moves one. The second does the same for the displayed
resolution and the step at which every figure is quoted
(`test_displayed_resolution_and_shipped_step_match_the_interface`). The third fails if the
interface stops short of the declared ranges or goes past them
(`test_the_sliders_span_the_supported_input_ranges`). It reads the shipped machine profile,
which declares no deliverable range. A profile that declares one narrows the fresh gas flow
slider to the overlap on purpose (§ "The model's envelope and a machine's deliverable range are
two claims").

**The simulation step has limits of its own, separate from the supported input ranges.** A user
does not set the step, but every call that advances the model takes it (`advance()`). Two
constants set its minimum and maximum (`MINIMUM_SIMULATION_STEP_S`, `MAXIMUM_SIMULATION_STEP_S`),
and `docs/MODEL.md` § "Supported simulation step" gives the reasons for both. The step's maximum is a
declared limit, in seconds, on how long a change to a control may go unseen by the model. The
input ranges are a claim about where the compartment structure represents a patient. Neither is
calculated from the other. Widening a range means re-running the reference tests at the new
extreme setting, without revisiting the step. The step's limits are checked at the run, not at
the compartment, because a step is an argument to one call. A compartment advanced alone is
calculated exactly at any step, so checking it against the maximum step would refuse an exact
calculation (`docs/MODEL.md` § "Supported simulation step").

#### What a setting outside the range costs

**The simulator refuses a setting outside the ranges, because neither its code nor its model has
been checked there.** The ranges are the model's **verification domain**. Across them, its results
have been compared with an independent calculation (`docs/MODEL.md` § "Independent-solution test") and with
measured human data (`docs/MODEL.md` § "Published wash-in and elimination validation test"). Every model result in
this document comes from settings within the ranges.

Outside the ranges, the simulator must refuse rather than show a plausible-looking number. Solved
exactly for a cardiac output of 1000 L/min, the model's equations would give a precise answer to a
question that physiology does not ask, and nothing on the display would invite doubt. Such a
cardiac output is not a patient, and the equations were never proposed to describe one.

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
would refuse. An offered range that contains no step is an error, because otherwise the slider
could offer only a flow that the run refuses.

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
| A machine's deliverable range | `deliverable_fresh_gas_flow_range` in that machine's `data/machines/*.json` profile | `BreathingCircuit._require_deliverable_flow` |

The two ranges are kept apart because one merged pair of limits fails in two ways. A profile whose
flowmeter reaches 15 L/min would extend the range that every reference test was run over,
without any change to `core/supported_ranges.py`. A run in the extended range would give an exact
number, computed outside everything that was checked and shown just like one inside it. Take a
machine with no true off position at its common gas outlet and a minimum flow of 0.5 L/min. The
merged pair would either fail to represent it or move the model's lower limit for every other
machine.

A test checks both refusals
(`test_machine_deliverable_flow_range_is_separate_from_model_envelope` in
`tests/unit/test_supported_ranges.py`). A machine range that does not overlap the envelope is
refused when it is reassigned on a built circuit, as well as when the circuit is built
(`test_a_machine_that_overlaps_the_envelope_nowhere_is_refused_when_built` in
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

The field table in `docs/machine-abstraction.md` lists a minimum total flow and a minimum oxygen
flow (`minimum_total_flow_l_min` and `minimum_oxygen_flow_l_min`) under the machine survey's
section (b8). Neither is stored in a machine profile, because that document allows a field only
where something uses it. A minimum total flow *is* the lower end of the deliverable range, so a
field of its own would store one number under two names in a safety-critical data file. A minimum
oxygen flow can be added when a hypoxic guard needs it, as an extension of the model rather than a
change to the data.

#### Supported run length

A run is supported up to **24 hours of elapsed simulated time**. This is the same kind of
limit as the four ranges above. Outside the supported span, the equations still solve exactly,
as "What a setting outside the range costs" says of the flows. What stops at the boundary is
the claim that the solution represents a patient.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The run length differs from the flow ranges only in that it is reached rather than set. A flow
is a setting, and a value outside its range is refused. Because the run length is how far a
run has gone, it is checked as each step is taken, and otherwise only where a run opens with
time already elapsed. The supported span includes its end, so a run may complete the step that
lands on 24 hours. At the shipped 0.1 s step, the last step ends exactly there. A run that has
stopped at the limit rests on a point at which a run may also be opened, and only the step
from that point is refused. A point past 24 hours can also be given directly rather than
reached, as the opening of a branch or a point to which a run is moved. It is refused before
any run is placed there. A time bookmark past 24 hours cannot be made at all, because a
bookmark accepts only a time that has already been checked against the limit.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

| Quantity | Limit | Declared and refused by |
| --- | --- | --- |
| Elapsed simulated time | 0 to 24 h (86 400 s) | `core/supported_ranges.py`: `CaseInstant` and `SimulationState` |

<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**The 24 hours belong to the case, not to each run.** The limit is argued from what the
model leaves out, which depends on how long the *patient* has been anesthetized. So a branch
shares the 24 hours its parent was using, and its elapsed time carries on from the point where
the branch was taken. A branch taken at 23 h has one hour left.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**Reaching the limit is not a failure, and the interface may not present it as one.** The
step past the limit is refused before it begins, so a run that stops there ends on a
completed step inside the supported span. Every displayed value is therefore a real solution
of the model. The run stops, and the interface says which limit was reached and why it is set
there. Reset starts a new run. Describing a correct model as a broken one misleads a reader as
surely as the reverse. It spends the interface's one signal for a real fault, and it teaches
a reader to discount that signal. The interface must not present the stop as a pause either.
Start is refused, because a resumed run's first step would be refused again.

**What bounds the run length is what this model omits.** The first omission is metabolism,
which this model does not have (`docs/MODEL.md` § "Known limitations"). The second is the fat group's flow.
The two human sources that `docs/MODEL.md` § "Known limitations" weighs do not agree about which way the
stored flow errs, but either way the flow acts directly on the slow tail of washout. The
published wash-in and elimination test compares the model with five minutes of elimination.
It explicitly refuses the two Yasuda papers' own multi-day curves, because *over days the
missing metabolism is no longer negligible, and neither is the fat group's flow*
(`docs/MODEL.md` § "Published wash-in and elimination validation test"). A run beyond the limit therefore
displays a trace whose slow component is increasingly the two omissions rather than the
model.

**Inside the limit, the washout tail already lacks its largest measured term, and the
displayed number does not say so.** Every washout that the two Yasuda papers fitted needed
five compartments. Their authors took the fourth to be fat filled by diffusion from the
well-perfused tissue beside it. This model has no such route. The fourth compartment
carries the largest term in the measured curve over most of the supported span: from about
1.8 to 3.1 hours after a 30-minute administration until about 20.7 to 29.4 hours. The
intertissue-diffusion note under `docs/MODEL.md` § "Known limitations" has the coefficients and the
arithmetic. All else equal, a tail without that store falls faster than the measured one
from about the third hour of elimination. Measured against the published mean curves over
the whole supported run, the shipped tail does so (`docs/MODEL.md` § "The first 24 hours of elimination
against the published mean curves"). It runs about a third below the curves from about the
seventh hour until about the twenty-first. For desflurane it runs below them by half, from
3.4 to 15.3 hours. In the hours before that, it runs a fifth to a half above them, while
the rebreathing circuit and the muscle group's slow return hold it up. At 23.5 hours of
elimination it runs above them again, by 12 to 24%, or by a factor of 2.1 for desflurane.
That is because this model's fat group returns more agent than the fitted fat term. In
that subsection's open-circuit run, which has no rebreathing, the tissue return alone is a
third to a half of the mean curve between hours 8 and 13.
<!-- not-restated: 2.1 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**The tail's departures from the published curves do not move the 24 hours.** The limit
rests on the two omissions above growing past negligible over the span, and the departures
come from neither of them. In `docs/MODEL.md` § "The first 24 hours of elimination against the published mean
curves", the metabolism bound accounts for about an eighth of the excess where the tail runs
above the curves, and widens the gap where it runs below. The shortfall comes from the missing
fourth compartment, which is as present in the first hour as in the last, so shortening the
span would not remove it. Extending the span would add the late excess, which is still growing
at 24 hours. The limit therefore certifies how closely the late tail follows a measured washout
inside the span only as far as the comparison with the published mean curves goes.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

Sevoflurane is the agent for which the missing metabolism matters most, so it is the agent
that constrains this limit. For sevoflurane, 2% to 5% of the absorbed dose is metabolized,
against far less for isoflurane and desflurane. Its metabolism begins immediately, and
fluoride and HFIP appear in plasma within minutes of the start of administration. Kharasch's
review, cited below, reports these figures. It also finds that metabolism "does not
contribute to the termination of clinical drug effect". That finding is what makes omitting
metabolism safe over a case. It holds while ventilation and perfusion dominate the trace,
and becomes progressively false once the only thing still moving is the slow tail, to which
this model gives no sink.
<!-- not-restated: 2 %, 5 % -->

- Kharasch ED. *Biotransformation of sevoflurane.* Anesth Analg
  1995;81(6 Suppl):S27-38. PMID 7486145,
  doi:10.1097/00000539-199512001-00005.

**No stored value comes from Kharasch's review.** As a review, it is tier 2 under
`docs/MODEL.md` § "Source hierarchy", and a tier-2 source is the authority for a stored value only on a
recorded decision. No such decision has been taken for this review, and there would be
nothing for one to authorize. The 24 hours is not computed from 2% to 5%, and no parameter in
this model descends from that paper. What the review supplies is the magnitude and the
timing of the omission on which this limit rests, and tier 2 is legitimate for exactly that.
A limit computed from a metabolic rate would need the primary measurements instead. It would
be a different and better limit than this one.
<!-- not-restated: 2 %, 5 % -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**The 24 hours are not inside the exposure range over which sevoflurane's metabolism was
measured.** Kharasch's review measured how sevoflurane's metabolism scales with dose only from
0.35 to 9.5 MAC-hours. The limit bounds elapsed time, not exposure. A MAC-hour is usually
counted at the end-tidal concentration, which in this model is the alveolar fraction. A run
whose alveolar fraction is held near 1 MAC gains about one MAC-hour per hour. So it leaves the
measured range at about 9.5 hours, and reaches about 24 MAC-hours at the limit. Every agent's
dial opens at that agent's 1 MAC. The alveolar fraction stays below the dial during uptake,
so a run left at the dial gains somewhat less. Sevoflurane's vaporizer delivers at most 8%,
four times its 2% MAC. Counted at the dial, a run held there reaches at most about 96
MAC-hours. A long run at or above 1 MAC end-tidal therefore leaves the measured range well
before 24 hours, and past that range even the size of the omission is unmeasured. The 24
hours rest not on the measured range but on the argument above, that the omission grows
steadily once only the slow tail is still moving, with no sudden break. Because isoflurane
and desflurane are metabolized far less, the same span omits less for them.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->
<!-- derived: 96 MAC-hours from data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->

**Why 24 hours, and not a multiple of the slowest time constant.** At the shipped reference
settings, sevoflurane's fat group has a time constant of about 42 h. A limit set at several
multiples of it would favour exactly the long tail described above, the part of the trace
that is most nearly all omission. The fat time constant sets a minimum for the limit
instead, and that minimum is a fraction of one time constant. The run must last long
enough that the fat compartment is still visibly filling when it stops. 24 hours is about
0.6 of the time constant. By then a single compartment filling exponentially has gone a
little over two fifths of the way to equilibrium, so the fat trace still shows what it
exists to show. A run of a few hours would stop that trace near its start. The minimum
says nothing about how far above it a run may go. The span is also far longer than any
anesthetic this simulator is built to teach.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**Volatile sedation in intensive care is out of scope, deliberately.** It runs for days
through an anesthetic-conserving device, which is exactly the regime in which this model is
wrong. Supporting it needs a model extension, metabolism first. Raising this limit without
that extension would produce the plausible-looking wrong values that this document exists to
prevent.

**For developers.** The limit is declared as `MAXIMUM_ELAPSED_SIMULATION_TIME_S` in
`core/supported_ranges.py`. Widening it is a safety-critical change on the same terms as
widening a flow range. Argue the longer span against what the model omits, extend the
validation that covers it, and revise this section with the result.

Reaching the limit and handing in a value past it raise different errors. The step that would
carry a run past the limit is refused in `SimulationState.advance()` with a
`SimulationDomainLimitError`. That error is separate because reaching the limit is not a
failure, and the interface (`app/`) checks for it to choose its wording. A value past the
limit that is handed in is itself what is wrong, so it is refused with a
`SimulationConfigurationError` before any run holds it. A step count past the limit is refused
where the simulation state (`SimulationState`) pairs it with its step, and an instant past the
limit where it is built as a `CaseInstant`.

No separate check makes a branch share the case's 24 hours. Every check on the limit reads
the case's clock, as a step count or a case instant, and a branch continues that clock from
its parent. So the arithmetic that limits the original run also limits every branch of it.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**Each instant and each step count is a type, checked once where it is built**, as
§ "Supported input ranges" describes for the flows. Every instant at which a run is opened,
moved, keyframed, marked or branched is a `CaseInstant`, a subclass of `float`. Only its
constructor runs the check (`require_supported_case_instant`). The constructor accepts only
an `int` or a `float`, and stores minus zero as zero, as the flows do. It refuses an `int`
too large for a `float` as past the run length. The places that keep an instant, or move a
run to one, require the type and refuse anything else with a `TypeError`, whatever its
value. These places are the opening of a run and every point it is advanced to
(`RunDefinition`), each `Keyframe`, a `TimeBookmark` and the `BookmarkCrossing` that a run
halts on, and the instant at which the controller branches a run
(`SimulationController.resumed_at`). The control record's instants are `CaseInstant` too:
`ControlChange.elapsed_s` and an adjustment's start and end. A value built as another checked
quantity is refused as a swapped argument, with no advice to rebuild it, both where the
instant is kept and by `CaseInstant` itself. One example is a step count (`StepCount`) passed
as an instant. Code that only passes an instant on is annotated with the type and checks
nothing again, such as a snapshot, a chart frame and the instants at which a branch is
offered.

A count of completed steps is a `StepCount`, a subclass of `int`. It is checked only for what
a count can be checked for alone: it must be whole and not negative, and a `bool` is refused.
How many steps fit in 24 hours depends on the step. So the simulation state checks the count
and the step together against the last supported count (`maximum_step_count`, through
`require_supported_step_count`). That check relates two fields, so the state makes it at
every write to either field, in `__setattr__`. The constructor's checks and messages therefore
also apply to a count or a step assigned straight onto a built state, and a refused value
leaves the field unchanged. The type checker (`mypy`) refuses such an assignment in `src/`. A
plain `int` count or a plain `float` step is refused with a `TypeError`. A count above zero
with no step, or a pair past the run length, is refused with a `SimulationConfigurationError`.
A flow written onto its compartment is treated the same way (§ "Supported input ranges"). The
state's uptake system is written once, when the state is built, because the count says how
far that one system has been advanced. A later write is refused with a
`SimulationConfigurationError`.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The step's check and the state's own check take the last supported count from one function,
`maximum_step_count`. It returns the largest count whose simulated time, `elapsed_s`, is no
later than 24 hours. That time is the count times the step, rounded once, and the state
builds it as a `CaseInstant`. The count is decided on that product, not on 24 hours divided
by the step. At some computed steps, that quotient rounds a whole step either way. It then
gives a last step that lands a rounding error past 24 hours, or one that stops a step short
of 24 hours. Deciding on the product means that a count is accepted exactly when the instant
it stands at is accepted. So the simulated time is never refused as a `CaseInstant`, and a
branch is built or refused alike, whether it is taken from its parent's count or from its
parent's instant.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

An instant that a run is only *asked* about stays a plain `float`, such as the instant passed
to `RunDefinition.state_at` and the ends of a drawn window. The run's own opening and end
bound such an instant, and the run checks that relation. Arithmetic on either type returns a
plain `float` or `int`, so a calculated instant or count is never taken as checked.

**Whether a run is at the limit is decided from the run, never from a refused step alone.** A
run can come to rest on 24 hours by three routes, and only one of them refuses a step. The
first is a trunk stepping onto the last supported count. The second is a branch forked on
that count, either at a mark that halted the trunk there or at a dial moved there. The third
is a branch reset onto such a fork. If the limit were recorded only from a refused step, the
other two routes would look like an ordinary pause: Start offered, no limit notice, and a
mark that the run never reached reported as still ahead of a run that cannot step. So the
controller asks the core's own check (`require_supported_run_length`) whether the run's next
step would be refused. It asks every time the run's state is read and after every step, and
reports the limit with the reason that the refusal would give. A run stepping onto the last
count halts on the step that arrives there, not on the refused step after it. So no run
appears to be running, or paused, while it is at a point where no step is left. The interface
may catch a `SimulationDomainLimitError` on some other path, such as a setting. That error is
recorded as the reason, and it takes precedence over the reason derived from the run.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

#### What is not bounded this way

The two gas volumes, of the breathing circuit and of the alveolar compartment, are **fixed
model parameters rather than controls**, and have no supported range. Each is set once,
when `AgentUptakeSystem.for_agent()` builds the system, and nothing changes it afterwards.
The interface has no control for either, and `SimulationController` has no setter for
either. Both have a numerical envelope, 0.01 to 10 000 L, which is a separate claim,
stated in `docs/MODEL.md` § "The numerical envelope". It says only where the arithmetic has been checked
against a high-precision calculation. It says nothing about which volumes describe a
patient, so it does not contradict the physiological argument below.
<!-- provenance: core/numerical_envelope.py MAXIMUM_VOLUME_L = 10000 -->

The two volumes have different sources. The alveolar gas volume is a patient parameter of
2.5 L, read from `data/patients/reference_adult.json`. The provenance table in `docs/MODEL.md` lists it
with the FRC measurement it is reconciled against. The circuit volume is a *machine*
parameter of 6.0 L, read from `data/machines/reference_circle_system.json`. That is a third
kind of parameter file, beside the agent and patient files, because the breathing system
belongs to neither. The same table lists the circuit volume with what is known of its
origin, which is that no source has been adopted for it.
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6 -->

**Each parameter file is the only source of its own values, and `core/` keeps no copy of
them.** `AlveolarCompartment` has no default for its gas volume or its ventilation, and
`BreathingCircuit` has none for its volume or its vaporizer maximum. Every shipped run is
built by `AgentUptakeSystem.for_agent()`, which reads the values from the agent, patient
and machine files and passes them on. The fresh gas flow keeps a default for a machine
profile that states no startup flow (`docs/MODEL.md` § "Source hierarchy: what may be cited as the
authority for a value" gives its reason, its constant and its tests).
`test_for_agent_builds_the_circuit_at_the_machine_file_s_values` and
`test_for_agent_builds_the_alveoli_at_the_patient_file_s_values` check that a shipped run
gets the file's values. The serious failure would be a change that stopped `for_agent()`
reading a file. Every provenance row in this table would then silently describe a file
that the model no longer uses. So each of the four values is also checked with a file that
states a different value, and that run fails if `for_agent()` stops passing the value on.
For the machine file the tests are
`test_for_agent_builds_the_circuit_at_a_changed_machine_file_volume` (3.3 L) and
`test_a_profile_stating_its_startup_flow_opens_the_run_at_that_flow` (2.0 L/min). For the
patient file the test is `test_for_agent_builds_the_alveoli_at_changed_patient_file_values`
(3.0 L and 5.0 L/min).
<!-- not-restated: 5.0 L/min -->

**Why neither gets a supported range.** A supported range describes an
envelope that a run can be steered *within*. The four controls above each name
an interval because a user can put the model anywhere in it. The verification
gates are what establish that the model represents a patient across that
interval. Neither volume moves. The single shipped value is the whole of each
volume's domain, and every reference measurement in `docs/MODEL.md` is made at
that value. An interval declared around it would assert verification across a
span that nothing has measured. That would be the same overstatement as
widening one of the four intervals without re-running the gates. Fixing the
value and saying so is the stronger claim, not the weaker one.

**What a wrong volume would be wrong for.** The argument is about physiology, as it is for
the four controls, not about numerical error. On 2026-09-06, with sevoflurane at the
shipped 0.1 s simulation step, a 0.005 L alveolar compartment and a 10 000 L circuit both
ran without incident. The agent balance held. So each gives an
arithmetically correct answer to a question that physiology does not ask. A 5 mL alveolus
is not a lung. This model's few compartments, its fixed tissue volumes and its constant
partition coefficients are claimed to represent a patient only near the shipped values.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
<!-- not-restated: 10000 L -->

**What is left open, stated plainly.** Python code written against `core/` can still build
either volume anywhere in the numerical envelope, 0.01 to 10 000 L, by passing a
`CompartmentVolume`. So a 10 000 L circuit or a 0.01 L alveolar compartment is accepted.
`SimulationController` still takes a `circuit_volume_l` argument when it is built. Such
values are outside the verified domain, and only the numerical envelope limits them. They
cannot be changed during a run, and the interface cannot reach them at all. They are
chosen once, by someone who has gone to the trouble of building the model directly.
`BreathingCircuit.set_circuit_volume` remains for the same reason. It is how the value
reaches the circuit, and it holds the checks for agent conservation and capacity.
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->
<!-- provenance: core/numerical_envelope.py MAXIMUM_VOLUME_L = 10000 -->

## Reset behavior

Reset pauses the simulation and keeps the user's selected settings. It also:

- sets simulation time to zero;
- clears the agent amounts in the circuit, alveoli, blood and tissues;
- discards the run, so that none of its states can be computed or drawn;
- clears the recorded timeline of control inputs;
- sets the cumulative amounts delivered and exhausted, and the mass-balance
  residual, back to zero; and
- clears any recorded failure, so that a session halted by a failed step can
  start again from a clean state.

**Reset on a branch returns it to the point where it was taken from its parent
run, rather than to zero.** A branch is a run taken from a point in a parent
run, and that point is called the fork. The branch's simulation time, state and
accounting go back to the fork, because a branch never held the case's induction
(§ "The canonical evaluation rule"). Its timeline of control inputs then holds
the entries that the branch first opened with, followed by each setting that
Reset kept and that differs from the one the branch opened under.

**The simulator refuses Reset when the tissue flows no longer sum to the cardiac
output.** This mismatch can happen only when a perfusion fraction is changed in
a way that bypasses its range check (`PL-HQF5`, `PL-Z0HN`). A refused Reset
leaves the run exactly as it was. The refusal message gives the two flows as
they were set, in L/min, the unit every readout shows.

After a refused Reset, the interface halts the run, as it does when a step
fails (`PL-M4M0`). The status word, the run controls and the banner show the
halt. The interface records the refusal as the run's failure. For other
failures, the banner names Reset as the way to recover. For a refused Reset, it
says instead that no setting can repair the run, because a new cardiac output
scales every flow by one factor. It also says that closing and reopening the
application starts a new run (`PL-01GY`). It names neither the refused Reset
nor a dial. If the run had already failed from another cause, the interface
keeps that earlier failure as the reason, and the banner's advice on recovery
mentions the refusal.

**For developers.** Reset sets simulation time to zero by clearing the count of
steps taken. It releases the step length that the run was using, so that a fresh
run may use a different one. It discards the run by opening a fresh run
definition at the cleared state, under the user's settings. A run definition is
the stored record of a run: the settings in force at each moment, and the state
at each change of setting, from which every other state is computed
(§ "The run is that record, and every state is derived from it"). The timeline
of control inputs is cleared because it belongs to the run that recorded it.

On a branch, the fresh run definition opens instead on the stretch of the parent
run that the branch was taken from, and the user's settings are recorded in it as
a change at the fork. The branch's timeline and provenance then agree on its
settings (`PL-K5BS`, `PL-ZR49`).

Reset is refused when it cannot build the settings record that the fresh run
definition opens on. It builds that record from the compartments before it
changes anything (`SimulationController.reset()`). The build fails when the
tissue flows do not sum to the cardiac output, which can happen only when a
perfusion fraction is written in a way that bypasses its guard (`PL-HQF5`,
`PL-Z0HN`). The next simulation step (`AgentUptakeSystem.advance()`) refuses
the same record. It reports a failed step rather than a refused setting, because
a run whose record cannot be built is not worth continuing.

## Agent-change behavior

Changing the running agent must begin a new run. Switching between volatile
agents is not modeled (see `docs/MODEL.md` § "Known limitations"), so there is no residual
washout to carry over. The model's values for the old agent would mean nothing
under the new agent's partition coefficients. A change of agent must therefore
do everything Reset does, and rebuild every compartment with the new agent's
parameters. It must also set the delivered concentration to 1 MAC of the new
agent rather than keep the old agent's percentage, because the same percentage
is a different clinical depth for each agent.

## Discarding a run, and the questions that guard it

Beginning a new run **discards the current one**. All a user can look back at
is the run's definition, its timeline of control changes and the simulated time
it reached. Nothing in the simulator saves them and there is no undo, so the
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
takes with it, `PL-W5WX`). A branch is a run taken from another run, the trunk,
at a moment called its fork. The display draws each branch beside its trunk.
Pressing the trunk's Reset also discards every branch, because a branch cannot
outlive its trunk. When a branch has run past its fork, or has had a control
change since then, the trunk's Reset says what that branch holds and asks before
it discards any run. The trunk's Reset also asks about a branch when the
simulator cannot tell what that branch holds. Any other branch is discarded
without a question.

When the trunk's Reset asks before discarding a branch, an opened entry does not
count as work the branch would lose (`RunRecord.opened_with`). Every later
entry does, including a setting that the user changed and kept through a reset.
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
had answered at once, as `docs/MODEL.md` § "The reproducibility guarantee" requires. The
bookmark editor does not block the window, so runs go on as usual while it is
open.

**For developers.** Runs with nothing to lose get no question because a
question asked when nothing is at stake teaches the user to answer it without
reading it. By the time something is at stake, the question would go unread.

In the code, the entry that a branch was opened with is `RunRecord.opened_with`.
Four tests in `tests/integration/test_simulation_view.py` enforce the rule for
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
(`docs/MODEL.md` § "The reproducibility guarantee", `docs/INTERFACE.md` § "The canonical evaluation rule"). A
comparison can teach only the mechanism: which way a curve moves when one thing
changes, why it moves that way, and roughly how fast, in a model whose
structure makes the reason easy to see.

### What is compared, and what the two runs share

**A comparison shows two managements of one case.** The first run is the
**trunk**. A **branch** continues it in another way from an instant that the
trunk passed through, and that instant is the **fork**.

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
- **The simulation step.** The branch uses the trunk's step, and a fork between
  two steps is refused rather than approximated.
- **Every setting up to the fork.** The branch's settings are replayed from the
  trunk's record of setting changes, then checked against the trunk's own
  settings at the fork.
- **The bookmarks set before the fork.** A bookmark marks an instant or a height
  on a curve, and a run halts when it reaches one. The branch opens with the
  trunk's bookmarks. A bookmark added after the fork belongs only to the run it
  was added to.
- **The time frame.** Both runs count time from induction. The chart anchors
  both to induction rather than to either run's own start, so the two traces
  are compared at the same instants.

**Everything that either run records after the fork is what its learner did to
it**, for three reasons. Taking a branch leaves the trunk unchanged. The
branch's record of setting changes opens with copies of the trunk's changes at
the fork, and holds none of the trunk's earlier changes. A reset branch keeps
those copies and can record the learner's settings after them
(§ "Reset behavior").

**For developers.** The architecture document describes a branch's structure
(`docs/ARCHITECTURE.md` § "What a branch is, and what it shares with its
parent").

The roadmap leaves a third run and a comparison of two branches out of scope
for v0.5.0 (`ROADMAP.md` § "Explicitly out of scope for v0.5.0"). A test checks
that another branch is refused while two runs are shown
(`test_a_second_fork_is_refused_while_two_runs_are_shown`).

The code enforces what the two runs share as follows:

- The reference adult is stored in
  `src/anesthesia_sim/data/patients/reference_adult.json`. Two tests check that
  a branch carries the trunk's patient and agent
  (`test_a_branch_is_the_agent_and_patient_its_parent_was`,
  `test_a_case_s_branches_carry_the_trunk_s_agent_and_patient_at_the_fork`).
- A branch refuses an agent change outright (`set_agent`,
  `test_a_branch_cannot_change_its_agent_out_from_under_the_case`). On the
  trunk, the agent selector is locked
  (`test_the_trunks_selector_is_locked_while_two_runs_are_shown`). Changing
  the agent begins a new run (§ "Agent-change behavior"), so an agent change
  during a comparison would end one of the two runs rather than vary it.
- Exact reproducibility is not guaranteed across model versions or platforms
  (`docs/MODEL.md` § "The reproducibility guarantee"), and the two runs of a comparison always
  share one model version and one platform.
- The circuit volume is a build-time parameter with no live setter
  (`test_the_circuit_volume_is_a_build_time_parameter_with_no_live_setter`).
  It is applied to a branch before any state is.
- A branch carries the trunk's step in its resume point (`ResumePoint`). A test
  checks this and the refusal of a fork between two steps
  (`test_a_branch_steps_to_where_its_parent_stepped`). Exact reproducibility is
  not guaranteed between runs at different steps (`docs/MODEL.md` § "The reproducibility
  guarantee"), so carrying the step keeps a comparison within the guarantee.
- A test checks the replayed settings
  (`test_a_branch_inherits_its_parent_s_settings_at_the_fork`).
- A test checks that a branch carries the trunk's bookmarks
  (`test_a_branch_opens_carrying_the_marks_of_the_case_it_continues`).
- Each column of the chart stands for an instant at which it draws a value. A
  test checks that a branch uses the trunk's columns
  (`test_a_branch_is_drawn_on_the_same_columns_as_the_run_it_forked_from`). A
  fork at a bookmark adds exactly one column, the fork itself
  (`test_a_bookmark_branch_draws_one_column_its_parent_does_not_and_it_is_the_fork`).

In the code, a run's record of setting changes is its control timeline. Two
tests check what a branch's control timeline opens with and that forking leaves
the trunk untouched
(`test_a_branch_opens_with_only_the_change_it_runs_under_in_its_timeline`,
`test_forking_leaves_the_trunk_untouched`).

Each entry that a reset branch keeps states a setting in force from the fork
on, so a reset does not change what can cause a difference after the fork.

Building the case twice instead of forking would leave the two runs differing
by everything that was not reproduced identically, and a learner could not see
which differences they had caused.

### The shared history is identical by construction, not by measurement

**Before the fork, a branch and its trunk are exactly equal.** The branch
repeats the trunk's arithmetic, operation for operation, at every instant they
share. This holds for every branch the program builds
(§ "What this requires of a branch"). There is no error to allow for, and none
is shown.

**A branch's exact equality with its trunk applies to the values the model
computes, and not always to the values the chart draws.** Where the fork was at
a setting change, the two drawn traces agree exactly at every point they share.
Where it was at a bookmark, they can differ by a rounding error that is orders
of magnitude too small to move any displayed digit
(§ "The canonical evaluation rule", § "Displayed precision").

**A branch's equality with its trunk before the fork sets no bound on anything
after it.** Only the settings and the model decide how far the two runs
diverge, in which direction, how quickly, and whether they converge again.

**For developers.** A keyframe is the state at the instant a setting change
took effect, and a segment is the stretch of a run between two changes
(§ "The run is that record, and every state is derived from it"). A branch's
run definition carries the trunk's own keyframe. It forms each propagation
interval as the instant minus the start of that instant's segment.
The branch repeats the trunk's arithmetic because both use the same keyframe
and the same subtraction. § "What this requires of a branch" sets out this
construction as a rule with two conditions, and says which condition a fork
at a bookmark relaxes. A branch that restarts at the fork would not reproduce
its trunk
(`test_a_fork_opening_at_the_instant_it_was_taken_does_not_reproduce_its_parent`).
No branch that this program builds takes that route.

Exact equality rests on the shared keyframe and subtraction, and the tests only
detect when it breaks. Two cover a fork on a keyframe and a fork between two
keyframes (`test_a_fork_opening_from_a_keyframe_reproduces_its_parent`,
`test_a_fork_opening_between_two_keyframes_reproduces_its_parent`). Two more
test both through the controller, at case instants and at drawn columns
(`test_a_branch_reproduces_its_parent_at_every_instant_they_share`,
`test_a_bookmark_branch_and_its_parent_agree_at_every_column_they_share`).
The last of these tests compares the 251 columns that a branch forked at a
bookmark shares with its trunk. On 2026-10-26, the worst difference over those
columns was 5.3e-16, a rounding error from the order of the floating-point
operations. Before the columns were put on whole hundredths of a second
(`PL-T5NJ`), it was 2.7e-15 over 240 columns, the figure
§ "The canonical evaluation rule" tabulates.

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
§ "Supported run length" declare, and with the fidelity that `docs/MODEL.md` § "Published
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
changing together need not take. `docs/MODEL.md` § "Known limitations" gives the size of this
artifact for a cardiac output scaled to body weight with the volumes kept fixed,
and the same arithmetic applies here.

**Do not read a comparison as "low flow woke this patient twelve minutes
sooner."** Three separate things are wrong with that reading, and only the
first is about variability.

- **"this patient"**: there is one modelled patient and no population around
  it, so nothing on screen is about a patient at all.
- **"woke"**: this model has no effect-site compartment and defines
  $`F_a \equiv F_A`$ (`docs/MODEL.md` § "Model boundary"), so it has no measure of
  responsiveness in which two runs could differ. The nearest thing the chart
  shows is the vessel-rich trace read against the MAC-awake band. That band is
  one standard deviation either side of a published population mean, and it is
  not a prediction for the patient on the screen (§ "MAC-awake as a chart
  reference").
- **"twelve minutes"**: a duration read between two curves inherits every
  limitation of the model that drew them, and this model does not claim to get
  a difference in emergence time right to the minute (`docs/MODEL.md` § "Known limitations").

### What the interface may assert about a comparison

The interface may mark the fork, where the two runs split. It may name the run
that each displayed value and each record of setting changes belongs to
(`docs/MODEL.md` § "Reasonably foreseeable misuse, and the hazards the presentation carries",
the row on reading one run's value as the other's). And it may show the two
standing disclaimers beside the readouts, one on interpretation and one on use.

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

A difference trace would mislead even before the fork, where the two runs are
identical. If the fork was at a bookmark, the trace would show a tiny nonzero
difference there instead of zero, and a reader would take that for a
disagreement about the case.

## Interface boundary

The interface shows the model's results and controls the run, but it does none
of the model's calculations. It may:

- display values;
- convert fractions to percent;
- collect user settings;
- issue Start, Pause, and Reset commands;
- halt a run, and record why, when the model stops with an error;
- report a value that the model refused; and
- display mass-balance status.

Under the conditions set out below, it may also:

- draw the run's states over a window of time, computed by the model at
  instants that the interface chooses;
- choose how wide a window of the run the chart shows, and how its time axis
  is ruled;
- draw only some of the compartment traces, when the user asks;
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
  and asking the user to confirm, as "Discarding a run, and the questions that guard it" requires;
- display a concentration at a finer resolution than "Displayed precision"
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

**What the chart draws.** Every point that a chart trace draws is a state the
run reached, at the instant where it is drawn. The interface never interpolates, smooths,
averages or otherwise makes up a plotted value. The model computes each point
from the run's definition, which gives the run's state at any instant directly,
by formula. No stored series of values lies behind a trace, so none can disagree
with it. The values that a chart draws are for display only, and the program
prevents their use for anything else (§ "The canonical evaluation rule" above).

**The chart draws the run's state at one instant for each pixel boundary of
its widest plot, and never at fewer than 150 instants.** A trace need not draw
every instant, because the run advances one step every 0.1 s of simulated time,
more often than a chart can resolve. The instant that the numeric readouts show
is always drawn, so the end of a trace always agrees with the readouts beside
it. When a plot becomes wider, after the user resizes the application window or
drags an area's border, it is redrawn at its new width on the next screen
update, whether the run is running or paused. Two rules set where the drawn
instants fall:
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

- **The drawn instants lie on a grid that starts at the case's time zero.**
  A run branched from another therefore draws at the same instants as the run
  it branched from, and the two can be compared point for point. Each drawn
  instant falls on a whole hundredth of a second, so the hover readout can give
  the exact time of the state it shows.
- **Every control change inside the window is a drawn instant.** Between
  control changes each compartment's value is a sum of exponentials, with
  bounded curvature and no hidden transients, so every sharp feature of a run
  is at a control change. A grid that stepped over one would draw a straight
  line through the very instant that the user is looking for. The point drawn
  there is the state that the run's definition stores for that instant. The
  chart therefore shows every control change exactly, to the last digit the
  readouts display.

**Between control changes, the drawn line is never further from the run than the
time that one pixel of the plot spans, except at a peak or a trough.** It passes
through the run's exact state at every drawn instant, and drawn instants are no
more than a pixel apart. The only exception to that spacing is a one-minute axis
more than 6000 px wide, where drawn instants a hundredth of a second apart span
more than a pixel. Where the run only rises or only falls between two drawn
instants, the run and the straight segment drawn between them cross every level
inside the same pixel. This one-pixel guarantee is in time, not in percentage
points. Where a trace is steep, the run can change by many percentage points
within one pixel of time. No display shows a value between drawn instants, the
hover readout included (§ "The chart's hover readout").

The straight segment between two drawn instants starts and ends on the run's
curve, but can lie above or below the curve in between. The table gives that
vertical gap at the middle of a segment, in percentage points (pp), computed on
a plot 1 000 px wide. A time base is a window width that the chart offers, and
the spacing between drawn instants is that width divided by 1 000.

| Time base | Spacing | Sevoflurane 2% to 4%, worst trace | Desflurane 0% to 12% to 6%, worst trace | Desflurane, alveolar |
| --- | ---: | ---: | ---: | ---: |
| 15 min | 0.9 s | 0.0004 pp | 0.0025 pp | 0.0025 pp |
| 1 h | 3.6 s | 0.0052 pp | 0.032 pp | 0.032 pp |
| 4 h | 14.4 s | 0.048 pp (circuit) | 0.28 pp (circuit) | 0.21 pp |
| 12 h | 43.2 s | 0.21 pp (circuit) | 1.21 pp (circuit) | 0.26 pp |

<!-- provenance: app/chart_time_base.py SELECTABLE_TIME_BASE_FLOOR_S = 900 -->

<!-- not-restated: 2 %, 6 % -->

The gaps grow with the spacing, so a narrower plot has larger gaps and a wider
plot smaller ones. They bound the error in a trace's *shape* inside one pixel
column, never in a displayed value.

**Between two control changes, the drawn line can miss the top of a peak or
the bottom of a trough.** Because the alveoli and the venous blood keep filling
for a moment after the vaporizer is turned down, the run can peak between two
drawn instants, above both drawn values. Over five simulated runs, the largest
gap at a peak or a trough on any time base is 0.0028 pp, on the mixed venous
trace at the desflurane dial-down on the twelve-hour time base. That is less
than a third of the readout's resolution of 0.01 pp.

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
   to the nearest limit, extrapolated or set to a default value.
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
not the model. A slider reports continuously while it is dragged, so only the
interface can tell one turn of a control from two. The declaration records no
value. It must not change the simulation state, what the run records or what
the model computes.

**A playback rate is a number of steps, never a step size, and it must be on
screen.** Real time is too slow to watch the two compartments that make uptake
and distribution worth teaching. At the reference settings, sevoflurane's
muscle group has a time constant of about 135 min, and fat one of about 42 h.
The interface advances the run in ticks, one every 0.1 s, and at real time each
tick takes one step. To play a run faster, it takes more steps per tick, under
three conditions of different kinds.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

The first condition is arithmetic. The interface refuses a rate that does not
come to a whole number of steps per tick, because rounding it would give either
a step of a different size or a run advancing at a rate other than the one
displayed. So faster playback stays within "The reproducibility guarantee":
identical inputs still produce identical run definitions, and two learners
comparing the same case at different speeds are comparing the same arithmetic.

The second condition is control resolution, and it limits that last claim. The
two learners are comparing the same *case* only if neither of them touches a
control. The same slider moves made at two rates land at two different
simulated instants and produce two different runs. The runs differ because the
inputs differed, not because the arithmetic did. `docs/MODEL.md` § "Supported simulation step"
gives the grid of tick boundaries for each rate, and how far a delay of one tick
can shift a displayed compartment. It also gives the route that is exact at
every rate: pause, change the setting, then resume.

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
with the playback control.** The interface computes the steps per tick from
that setting, so the label always agrees with the number of steps each tick
takes. The simulated clock is exact at every rate, because simulated time is a
count of the steps taken. Whether the run keeps pace with real time depends on
the computer. When the computer cannot run a tick in time, the tick is lost,
and no extra steps make it up. The **delivered rate** is the set rate times the
fraction of ticks that ran. In a measurement on 2026-09-27, every rate from 1×
to 300× delivered 99.0 to 99.9% of its setting over 8 to 30 s. On a computer
that loses ticks, the run plays slower than the label says, and nothing on
screen shows the delivered rate.

**For developers.** A chart draws from a window of states (`DrawnWindow` in
`app/run_series.py`), one for each instant that a frame plots. The controller
evaluates them from the run's definition (`SimulationController.drawn_window`,
`core/run_definition.py`). Keeping no stored samples of the run is a decision
(project owner, 2026-09-05, recorded here when the sample store was deleted).

Each state carries its substance's six compartment values, as fractions of one
atmosphere, under stable identifiers (`RecordedQuantity`). A trace addresses one
of them as a substance-and-quantity pair (`RecordedSeries`). When a frame asks
for a substance that the run does not contain, it fails rather than drawing
whichever substance is in the run. The window is keyed by substance rather than
by six named fields, because six flat names can describe only one substance. A
second substance would then need six more names, or values pooled with the
first substance's, and pooled values show a correct number under the wrong
label.

A frame is rendered from the running agent's state at one instant
(`SimulationSnapshot` in `app/controller.py`), which carries the six compartment
values as flat named fields. This difference from the window is a decision, not
unfinished work (`PL-TCD1`, 2026-09-13). Unlike the run's definition, a snapshot
is never stored, never compared with a later run and never read back, so giving
it a second substance later adds a field and invalidates nothing already
written. The roadmap's test for a change like this is "whether retrofitting
invalidates recorded runs or merely adds a field"
(`ROADMAP.md` § "Designed for forking"). By that test, the roadmap declines
per-compartment agent amounts in the snapshot. The snapshot gains the
per-substance mapping with `ROADMAP.md` Phase 1, which generalizes the patient
to N simultaneously present substances. The snapshot carries the six fields
beside the identifier and display name of the agent they belong to
(`agent_id`, `agent_display_name`), as it carries the agent's MAC
(`agent_mac_percent`) beside the concentrations that MAC scales. The controller
exposes immutable snapshots, and immutable windows onto the recorded run, rather
than mutable compartment objects.

A function sets the number of drawn instants (`chart_columns` in
`app/chart_frame.py`, `PL-GS3R`). The spacing is the time base divided by that
number. It is rounded down onto whole hundredths of a second, and onto whole
tenths of a second where that adds at most 10% more instants (`grid_spacing_s`
in `app/chart_time_base.py`, `PL-T5NJ`). Rounding down is what keeps drawn
instants no more than a pixel apart, except on a one-minute axis more than
6000 px wide. Where the spacing is 1 s or more, rounding onto tenths puts each
drawn instant on a time that the clock also shows. A plot is redrawn when it
grows wider than the width its frame was sampled for (`resample_owed`,
`PL-9LNF`).
<!-- not-restated: 1 s -->

The two rules for where drawn instants fall are requirements of this document,
not optimisations. The grid sits at absolute multiples of the spacing, so a
window that follows the run keeps every drawn instant it had and gains at most
one, and a steady trace is not redrawn on every frame. A grid anchored to the
viewport would move on every scroll and resize, and rewrite the whole chart on
every frame. A grid anchored to each run's own start put a branch forked at
55.3 s on 55.3, 65.3, 75.3 … while the run it branched from drew 0, 10, 20 ….

Each control change is a drawn instant because the run has a kink there: the
derivative of the circuit fraction is discontinuous. Without a drawn instant
there, the interpolation error at that instant would scale as O(h), in
proportion to the spacing h between drawn instants, rather than as O(h²), in
proportion to its square. The stored state drawn at a control change is a
keyframe, not one propagated from an earlier instant.

The pixel in the one-pixel guarantee is a logical pixel of the plot, the
resolution at which the axis is ruled and labelled.

The one-pixel guarantee works in pixel columns, as Jugel, Jerzak, Hackenbroich
and Markl do for recorded data. They prove that a line chart is fixed by at most
four values per pixel column (M4: A Visualization-Oriented Time Series Data
Aggregation, *Proceedings of the VLDB Endowment* 2014;7(10):797-808). Their
method of selecting values from a store is not used, because a selection of
recorded extremes could not guarantee that every control change is a drawn
instant whatever the pixel width (`PL-4RBD`). The run is evaluated at the drawn
instants instead.

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
computed on 2026-09-14 against the run's exact state every 0.1 s, the step the
run advances by, over five twelve-hour runs built by formula.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
<!-- not-restated: 2 %, 6 % -->

The five simulated runs for the gap at a peak or a trough were sevoflurane
2% to 4% and 4% to 0% at the fastest settings, the desflurane case at the
fastest settings and at slow settings (FGF 0.5 L/min, V_A 2 L/min, Q 2 L/min),
and the reference adult at 1 to 2 MAC. A test checks that the gap at the peak
in the desflurane dial-down case stays below half the readout's resolution
(`tests/unit/test_run_definition.py`).
<!-- not-restated: 2 % -->

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

The steps per tick are derived in `app/playback.py`, and a precise timer starts
each tick (`PreciseTimer`, `RunView.step_tick`). A count of more than 1 000
steps per tick is refused (`PL-T6P0`). A tick takes all of its steps before the
interface can respond, so a count with no bound would freeze the application
with no error. The bound is set by time: one step took about 53 microseconds
when measured on 2026-10-26, so 1 000 steps take about half of the 0.1 s tick.
A tick lasts as long in real time as one step does in simulated time, so the
fastest offered rate, 300×, takes 300 steps per tick whatever the step size.
<!-- provenance: app/playback.py MAXIMUM_STEPS_PER_TICK = 1000 -->
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

The 2026-09-27 measurement used the real dashboard on the offscreen platform,
with both timers running, and the tick period stayed at 100 ms to within 4 ms.
<!-- not-restated: 100 ms -->

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
  band was derived from two numbers, and its label gives both: MAC-awake as a
  fraction of the agent's 1 MAC, and that 1 MAC in percent. The label also names
  the trace to read the band against. A visually distinct line on the chart
  marks the agent's nominal 1 MAC
  (`test_the_band_states_the_fraction_and_the_divisor_it_was_drawn_from`,
  `test_the_interface_says_which_trace_the_band_is_read_against`,
  `test_no_trace_dash_is_as_wide_as_the_one_mac_reference_line`). See
  § "MAC-awake as a chart reference" for what the band does and does not assert,
  and why no time-to-wake-up figure is displayed anywhere in the interface;
- every setting changed during the current run. Each change is listed with the
  simulated time at which it took effect, the control and its old and new
  values. The chart marks each change at that time
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
on the display when its trace is hidden. The MAC-awake band, the 1 MAC line, the
marks for setting changes and the $`F_A/F_I`$ plot are requirements on the chart
itself, and the reader cannot hide them. Of the chart entries, only the span of
simulated time is the reader's choice, and no particular span is required.

Telling a halted run from a paused one is a required output. Both stop the
numbers advancing, and under `docs/MODEL.md` § "Step atomicity" both leave the simulation in a
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

Arterial concentration is **not** in the list above. In this model the arterial
fraction is defined as the alveolar one, $`F_a \equiv F_A`$ (see
`docs/MODEL.md` § "Model boundary"). A separate arterial readout would show the alveolar number
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

The documentation check reads the list of required outputs (`docs/MODEL.md` § "How this
document is held to the tree"), and fails when an entry names nothing that backs
it, or names a test that does not exist.

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
shows no verdict or amounts. The banner says that the readouts are withheld and
that the chart still shows the discarded run.

**After a step fails its accounting check**, the accounting panel shows
"Validation failed" with that step's totals. If the screen is not redrawn after
the failure, the panel shows the same result from the run's record. The run
stops, and the model undoes the failed step, so the run's own accounting passes
again. The banner names the panel as the one exception to "the values shown are
the last completed step".

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

### Naming the run in a comparison

While two or more runs are drawn, each of these places names its run in text:

1. Each run's own readout panel (§ "Minimum displayed outputs").
2. The chart's hover readout. With one run under the pointer, its name is on
   the readout's first line (§ "The hover and the run it belongs to"). With
   several, each value line gives its run's name. The readout reports every run
   inside the hover radius, so a small pointer movement cannot swap which run is
   read (§ "Where more than one trace answers").
3. The three advisory lines inside a chart: the wash-in state, the off-scale
   notice, and the count of control changes the chart could not mark. They
   stack one line per run.
4. The headings of the two record panels: the agent-accounting validation in
   the sidebar, and the control-change record ("What was changed during this
   run") in the right column of the always-shown region of the window. Each
   record stacks one whole panel per run, so a run's name is in its panel's
   heading and moves with that panel.
5. The notice banner, between the runs' control rows and their readouts. Both
   runs use this one place, and an empty banner is hidden and takes no room. A
   banner's position therefore does not show which run it belongs to.
6. The heading over each run's compartment schematic, taken from the name on
   the run's own panel.
7. The heading over each run's agent cost panel, in the same way.

With only one run drawn, the hover readout, the chart's advisory lines, the
sidebar panel headings and the banner show no run name.

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
The worst contrast between two compartment traces is 1.01:1, against the 3:1
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
run is not open, the Workspace's areas show a named "run not present" state.
They never show another run in its place, and the simulation is left untouched.
The reader sets a pin on the row of Workspace tabs, and sees there when the
pinned run is absent (`PL-2KXB`).

A view shows its run's name whenever a reader could mistake its values for
another run's: while another run is drawn anywhere in the application, while the
view is pinned to a run, and always in a window broken out of the main one.
Break-out windows are not built yet, so the dashboard is the only window that
draws a run. In this version, therefore, the names appear when two runs are
compared, and a pinned Workspace shows its run's name in the header of every
area (`PL-2KXB`).

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
conditional.** The record lists every change to a setting during the run, with
the simulated time it took effect, the control it changed and the values it
moved between. It gives the facts, and the marks place them against the curve.

**The unconditional values sit outside the areas.** Each run's unconditional
values are in one band across the top of the dashboard, the unconditional
region. The setting sections are in a plain column between that region and the
areas, so they are outside the areas too (`PL-W9P6`). Neither is affected by a
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
the region sits above it. Only the Workspace tabs, the areas and the case's
controls scroll between them. The interpretation statement on the region's
readout heading row stays in view with the line and the region, at any window
height and through any scrolling. This is what "always" means in the paragraphs
on the alert colour in § "Color contrast, and the standard this interface is
held to".

**The agent accounting must stay reachable, though not always visible.** It
consists of cumulative agent delivered, cumulative agent exhausted, total agent
stored, and the mass-balance residual with its absolute error. These five
amounts show whether the model is conserving mass, and a reader does not
titrate against them. A Workspace may leave the amounts out, because their
absence makes no clinical reading wrong, but nothing may remove them from the
application.

**"Reachable" means the reader can bring a view on screen through the interface
alone** (`PL-50PZ`). They must be able to do it from the Workspace they are in,
in a bounded number of steps, without dragging anything or editing a file.
Every area's header has a view chooser, whose menu lists every kind of view the
application has, whatever the Workspace. Choosing a view shows it in that area.
The page grows to give the view the space it needs, so the reader sees the view
itself, never only a notice that the area is too small (`PL-K285`). The
application will not start if the accounting view is missing from the chooser's
menu. Every layout has at least one area, so a chooser always offers the
accounting view. None of the Workspaces supplied with the simulator includes the
accounting view, so the chooser is how a reader reaches it.

**Conditional values are required only on a chart or plot that is shown.** A
concentration chart shows the MAC-awake band, the 1 MAC line and the marks of
control changes. It also states how much simulated time it shows, and whether
that span was chosen or fits the run. An $`F_A/F_I`$ plot shows its equilibrium
line and states where the ratio is not defined. These references exist so that a
trace is never read without its clinical anchor. Where no trace is drawn there
is nothing to anchor, so leaving the chart out loses nothing.

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

**A separate window shows the invariant tier, not the whole set**
(project owner, 2026-09-16, ratified - a recommendation put to them and agreed,
chosen over the two live readings `PL-W54S` had written, and reopenable on
ordinary evidence per `CLAUDE.md`; the occlusion rule above is not, being the
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
- **The per-substance tier appears once, in the main window**, which cannot be
  closed while any other window is open. Closing the main window closes the
  others. A reader could misread the run's other displayed numbers without this
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

**For developers.** The unconditional tiers and the control-input record are
stated as data in `app/unconditional_set.py`, with the inhaled-agent tier as
`INHALED_AGENT`. The educational-use disclaimer is a standing statement
(`USE_DISCLAIMER_TEXT`) rather than one of this list's values, so that file
does not declare it. The interpretation statement is
`INTERPRETATION_DISCLAIMER_TEXT`.

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

Before the region and the line were fixed outside the scrolling part
(`PL-NNML`), the whole page scrolled. At 1366 px wide, the page was 1087 px tall
in the Default Workspace and 1505 px in Induction and Maintenance (measured
offscreen, 2026-10-20). In a 700 or 900 px window, the disclaimer line was
therefore below the visible part, and scrolling down to it moved the region off
the top.

A test checks that the unconditional region and the disclaimer line stay in view
in windows 700, 900 and 1100 px tall, in each supplied Workspace
(`test_the_region_and_the_use_disclaimer_stay_in_the_viewport`). The region and
the line must also stay in view through the scroll to the concentration chart
that happens when a branch is taken (`PL-562Z`). Another test checks that the
line is present in every Workspace
(`test_the_dashboard_carries_the_educational_disclaimer`).

The view chooser is built in `app/area_layout.py`. The view registry marks the
accounting view as required to be reachable (`required_reachable`, in
`app/view_registry.py`), and a build that does not register that view fails
when the module is imported. Each area that shows the accounting view builds a
copy of its own, so two such areas both show the five amounts (`PL-TH35`). A
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

The MAC multiple is only a display unit. The model neither stores it nor
computes it.

**MAC multiples keep their meaning when the agent changes, and clinicians reason
in them.** A percent changes meaning with the agent: 2% is 1 MAC of sevoflurane
and about a third of a MAC of desflurane. A desflurane wash-in and a sevoflurane
wash-in drawn at the same height in percent therefore show two different
clinical situations.
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->
<!-- derived: a third of a MAC of desflurane from data/agents/desflurane.json mac_percent = 6 -->

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

1. MAC falls about 6% per decade of age (Mapleson 1996), and the model's
   reference adult has no age parameter.
2. The MAC multiples of co-administered agents are additive, and the model runs
   one agent at a time.
3. Opioids, temperature and patient factors modify MAC, and the model
   represents none of them.
<!-- not-restated: 6 % -->

**The MAC multiple is written `×MAC`, not `MAC`.** A clinician reads "0.80 MAC"
as a depth of anesthesia, and "0.80 ×MAC" as a multiple of 1 MAC, which is what
the number is. Every readout carries the multiplication sign, and so does the
MAC axis title. The axis ticks show bare numbers, such as `0.5` and `1.0`, so
only the title says what they are. That title labels six traces at once, and
five of them are not the alveolar compartment. No text on the display explains
the difference between a ratio and a depth, so the sign is the only thing that
marks it.

**The agent's 1 MAC is shown beside the chart**, for example as "1 MAC
sevoflurane = 2.0%". A reader can compare this 1 MAC with the value they use,
and can convert a MAC multiple back to the percent that the model computes. The
1 MAC is also the vaporizer's starting position. In each agent's data file, the
authority for the stored 1 MAC is De Wolf et al. 2012, which reports the flat
adult MAC that Gas Man uses. `docs/MODEL.md` § "Delivery-limit and MAC parameters" gives the
source of each agent's 1 MAC, how far it is from the primary literature, and
what that gap means for comparing agents.
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->

**The chart's vertical range is set in MAC, and fixed.** For every agent, the
axis runs from 0 to a ceiling of **3 ×MAC** of the agent in use, with a gridline
every half MAC. A given MAC multiple is therefore drawn at the same height under
any agent. The axis never grows to fit a trace. It stays the same for the whole
session, not only within a run, so two consecutive runs are comparable too.
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

**The chart names each compartment whose trace is above 3 ×MAC.** Such a trace
is cut off at the top of the frame, where it runs flat as a plateau would.
Without the name, a reader would conclude that the concentration stopped rising
at 3 ×MAC, when in the model it did not. The chart also says that the readouts
are not cut off and keep showing their values. Inhalational induction commonly
uses sevoflurane's 8% dial setting, which is 4.00 ×MAC, above the ceiling.
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->
<!-- derived: 4.00 from data/agents/sevoflurane.json max_delivered_concentration_percent = 8, mac_percent = 2 -->
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

**The chart's percent axis is linear, which crowds the slow compartments
together** (project owner, 2026-09-23, ratified, over a reader-selected logarithmic scale,
`PL-QYBW`). Only fat stays crowded for long. At a 1 MAC dial, across
the simulator's three agents, muscle spans 25–48 px of the 360 px plot at one
hour, and fat spans 1.5–3.7 px. Fat's trace near zero is its true partial
pressure, and partial pressure drives effect, so one linear axis serves all six
compartments. Because the hover readout reports every trace in reach, the
crowding needs no change of scale. The fat trace cannot show how much agent fat
holds. The compartment schematic shows that amount (§ "The compartment schematic: what its
heights, amounts and share bar assert").

**For developers.** The display code converts percent to MAC multiples in
`app/formatting.py`, outside the model's code in `core/`. It takes the agent's
1 MAC as an argument. Each snapshot of the simulation's state carries that 1 MAC
beside the concentrations it scales and the agent it belongs to
(`SimulationSnapshot.agent_mac_percent`). The display code therefore cannot pair
one agent's concentrations with another agent's 1 MAC.

Both units are shown because a unit selector would make the axis unit a mode,
and a chart read under the wrong assumed unit is a misreading that no
disclaimer catches. The agent's 1 MAC is shown because the project's rules
(`CLAUDE.md`) require a clinically meaningful displayed value to be traceable to
the transformation that produced it. The display carries no text explaining MAC
because its reader, an anesthesia provider, knows what MAC is defined against,
and a dozen lines of text between the reader and the plot cost more than they
gave (`PL-6580`).

The stored 1 MAC (`mac_percent`) is a tier-3 value under
`docs/MODEL.md` § "Source hierarchy: what may be cited as the authority for a value".
Mapleson 1996 is in the `sources` list of each agent's data file as the source
for the fall in MAC with age.

The vertical range is fixed because an axis that grew to fit a trace would
redraw a rising curve smaller partway through a lesson, and a reader would take
that change of shape for something the model did.

The 3 ×MAC ceiling (`CHART_AXIS_TOP_MAC` in `app/formatting.py`) is exactly
desflurane's dial maximum divided by its 1 MAC, so it rests on a real device
limit. Desflurane's vaporizer is the most limited, and the ceiling leaves no
empty band above the range that vaporizer can reach. The ceiling puts the 1 MAC
line at a third of the plot height, inside the plot rather than on its frame,
which a ceiling of 2 could not do. It also keeps on the plot the 2-3 ×MAC range
that overpressure induction works in. A ceiling at each agent's own dial maximum
could never be exceeded, but the chart would then draw the same MAC multiple at
different heights for different agents, because the dial maxima run from
3.00 ×MAC for desflurane to 4.17 ×MAC for isoflurane (`PL-CC23`).
<!-- derived: 3.00 from data/agents/desflurane.json max_delivered_concentration_percent = 18, mac_percent = 6 -->
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->
<!-- derived: 4.17 from data/agents/isoflurane.json max_delivered_concentration_percent = 5, mac_percent = 1.2 -->

A gridline every half MAC (`CHART_GRID_INTERVAL_MAC`) falls on the values that
the MAC axis labels, so the axis names every gridline on the plot.

The chart compares a trace's excess over the ceiling with the displayed
resolution rather than with zero, so it does not name a compartment whose trace
sits exactly at the ceiling. This matters for isoflurane, whose ceiling,
3 × 1.2, is 3.5999999999999996 in binary floating point.
<!-- provenance: data/agents/isoflurane.json mac_percent = 1.2 -->
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

### The chart's time base

**The time base is how much simulated time a chart shows at once.** The reader
either picks from a fixed ladder of widths, from fifteen minutes to twelve
hours, or leaves the default, which fits the whole run so far. Either way, the
horizontal axis is simulated time. A separate control, the playback rate, sets
how fast the run advances, so that a long case can be watched in one sitting.

**A time base changes the view and never the run.** No simulation step is
resized or taken again. Nothing that defines the run is added, discarded or
altered. A case watched at a width of fifteen minutes or of twelve hours is the
same run, so `docs/MODEL.md` § "The reproducibility guarantee" still applies. Every point drawn
at any width is a state that the run reached at the simulated instant where the
point sits. In a wider window, these states lie further apart in simulated time.
No drawn value is estimated from its neighbours, and no stored image is
enlarged.

**No one width suits a whole case.** The compartments this model exists to teach
are slow, but the moment a learner is most likely to be watching is not. At the
reference settings, muscle's time constant for sevoflurane is about 135 min and
fat's is about 42 h, while induction lasts minutes. A five-minute window hides
everything slower than the vessel-rich group. A twelve-hour window puts a
five-minute induction in the leftmost 0.7% of the plot.

**A chosen width keeps slopes comparable within a run and between runs.** It
stays the same at every moment of every run. Seconds per pixel then depend on
the reader's choice alone, not on how long the run has gone on. A trace's slope
on the plot is therefore a fixed multiple of its rate of change. A window that
widened continuously with the run would rescale every slope while the rates
stayed the same. That would misrepresent rate of rise, the one quantity by which
uptake and distribution are taught. The vertical axis has a fixed range for the
same reason (see the section above).

**The gridlines follow from the width.** Each width on the ladder sets the
interval at which gridlines and labels fall, so that the axis holds four to six
intervals. Gridlines fall at multiples of that interval counted from the start
of the case, not from the window's left edge, so a gridline stays at the same
simulated time as the window slides under it. The gridlines are the same for
every run drawn on the axis, because a run branched from another keeps the clock
of the run it came from.

**The default time base always shows the whole run.** It uses the narrowest
width that holds the run, so the width steps up as the run grows, and slopes on
the plot change scale at each step. Past the widest width on the ladder, it
keeps doubling the width. Early in a run, it can also use widths narrower than
any the reader can choose.

**Every axis label carries its own unit, and each chart states its width.** A
label reads `0`, `45s`, `3m`, `1m30s` or `1h30m`. Beside the plot, the chart
names the width in words and says whether the reader chose it or it is the whole
run so far.

**Each chart has its own time base** (project owner, 2026-10-19, ratified, over
one shared window saved per Workspace; `PL-L59K`). The concentration chart and
the F_A/F_I plot each have a time-base control, and a choice in one sets that
chart alone. One chart can show the first fifteen minutes of a case while
another fits the whole run. Two charts at the same width show the same instants.
Each notice that depends on a chart's window describes that window and appears
on that chart. These are the notice that names traces above the top of the axis,
the count of control changes the chart could not mark, and the count of F_A/F_I
stretches it could not draw.

**A chart saves its width with its other settings.** The Induction Workspace
that comes with the simulator saves its concentration chart at the 15-minute
width. The window follows the run, so the current values stay on the plot after
the first fifteen minutes. Switching to the Induction tab opens the chart at that
width (`PL-2KXB`).

**For developers.** The time base's code is in `app/chart_time_base.py`. The
module does arithmetic on simulated time. It reads no simulation state and
imports no interface toolkit, so the widths and gridline intervals can be read,
cited and tested without loading the interface.

Each drawn point is evaluated from the run's definition, under the constraint
that § "Interface boundary" places on a plotted trace.

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
§ "v0.6.0 - the layout is the reader's", Required scope entry 11). Each chart's
notices describe its own window, because a notice naming a clipped trace that
the chart does not draw would be false for that chart. Charts at the same width
are drawn from one frame.

### MAC-awake as a chart reference

The compartment chart carries two horizontal clinical references for the agent
in use. A **band** marks the agent's MAC-awake, the concentration at which half
of a population responds to verbal command. The band's label names that
endpoint. A **line** marks the agent's nominal 1 MAC, whose endpoint is
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
space between the rules is exactly the published spread.

**The 1 MAC line marks the nominal value, not the dialled one.** A fixed line
sits at the same height in every run, so runs stay comparable. A line that
tracked the dialled concentration would only restate where the trace already
starts. The line sits at the stored MAC and is labelled as a reference adult
value, not as this patient's MAC, because this model has no age parameter.

**The band is not a prediction for the patient on the screen.** It is the
strongest claim that the evidence supports. The interface shows no
time-to-wake-up figure of any kind, because this model does not support a
per-patient prediction.

**Read the band against the vessel-rich trace.** This model has no effect-site
compartment and defines $`F_a \equiv F_A`$ (see `docs/MODEL.md` § "Model boundary"), so the
alveolar trace is the fastest curve on the chart and the furthest from where
responsiveness returns. One simulation shows the size of the gap. It ran
sevoflurane for 3 hours at the opening dial of 2.0%, which is the stored 1 MAC,
and the default fresh gas flow of 4 L/min. That brought the alveolar fraction
only to 1.69%, or 0.84 MAC. The vaporizer was then turned off and the fresh gas
flow raised to 10 L/min. The alveolar trace crosses the band's centre at
2.86 min, and the vessel-rich trace crosses it at 6.55 min, 2.29 times later.
These figures are from a run on 2026-10-26, repeated on 2026-10-31 (`PL-39KH`,
`PL-PTDZ`). An automated test reruns this protocol and checks each figure to
the decimal places printed here.
<!-- not-restated: 10 L/min -->
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->
<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->

<!-- derived: 2.86 min from data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34, mac_percent = 2 -->

At a 1 MAC dial, no patient trace reaches the 1 MAC line, however long the case
runs. This is expected and is not a display fault. Muscle and fat keep taking
up agent for many hours, so the blood returning to the lungs stays below the
alveolar gas. That keeps the alveolar fraction below the inspired fraction, and
rebreathing keeps the inspired fraction below the dial (`PL-39KH`). In the
3-hour run above, the vessel-rich trace reached only 0.84 MAC, as the alveolar
trace did. This shortfall happens in real patients too, and it is worth
teaching.

**The trace that the band is read against decides which published MAC-awake
value is correct.** Katoh et al. determined sevoflurane and isoflurane MAC-awake
by a slow, equilibrated washout and by a fast one, and the two methods disagree.
Slow washout gave 0.34 of MAC for sevoflurane and 0.31 for isoflurane, against
0.22 for both by fast washout. Katoh attributes the disagreement to
end-tidal-to-arterial and arterial-to-cerebral anesthetic differences. This
model represents those differences as the gap between the alveolar and
vessel-rich traces. The stored values are the slow-washout ones, and they belong
against the vessel-rich trace.
<!-- provenance: data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34 -->
<!-- provenance: data/agents/isoflurane.json mac_awake.fraction_of_mac = 0.31 -->

Katoh also estimated the brain concentration at awakening. That estimate is not
a measurement, because cerebral concentration cannot be sampled in these
patients. The abstract says the brain concentrations were "calculated with
end-tidal anesthetic concentrations", and the title calls them "predicted".
So they come from Katoh's own model of brain uptake (`PL-YDRT`), which treats
the brain as one well-mixed compartment perfused by arterial blood. Katoh's
equation 1 (p. 1013) is:

$$
\frac{dP_{Brain}}{dt} = \frac{CBF \cdot \lambda_{B/G} \cdot (P_{Art} - P_{Brain})}{V_{Brain} \cdot \lambda_{T/G}}
$$

This is the perfusion-limited form that `docs/MODEL.md` § "Tissue uptake and return" uses for
each tissue group. Katoh's compartment is the brain alone, though, while this
model's vessel-rich group pools the brain with the heart, liver, kidney and
viscera.

Katoh computed every patient's flow and volume from the same formulas. Cerebral
blood flow $`CBF`$ is 14.3% of a cardiac output set by a cardiac index of
3.5 L/min/m², so it scales with body surface area. Brain volume $`V_{Brain}`$
is 21 mL/kg, so it scales with body weight. The brain's time constant therefore
varied a little from patient to patient. The coefficients were the same for
everyone. The blood:gas coefficient $`\lambda_{B/G}`$ is 0.63 for sevoflurane
and 1.36 for isoflurane, and the brain:gas coefficient $`\lambda_{T/G}`$ is
1.15 and 2.09.

During fast washout, Katoh's calculated brain concentration at first eye opening
does not differ significantly from the slow-washout values, under either of two
estimates of the arterial partial pressure. Katoh did not measure that pressure.
Equation 2 sets it equal to the end-tidal value. Equation 3 (p. 1016) corrects
the end-tidal value for 20% dead-space gas, as
$`P_{Art} = (P_{ET} - 0.2\,P_I)/0.8`$. During fast washout, the calculated
brain concentration at first eye opening was 0.30 of MAC for sevoflurane and
0.26 for isoflurane under equation 2 (Table 1, p. 1014).
Under equation 3 it was 0.34 and 0.30 (Table 3, p. 1016). The abstract quotes
the equation 3 figures and calls them
"nearly equal to MAC-Awake obtained by slow alveolar washout". So the stored
values and the choice of the vessel-rich trace rest on a modelled estimate that
agrees with an equilibrated measurement. That is weaker evidence than a direct
measurement of the brain would be.

<!-- not-restated: 0.34 -->

**The MAC-awake fractions for isoflurane, sevoflurane and desflurane were not
determined by one method.** Katoh's slow-washout arm is *descending*. Chortkoff
and Song et al. both determined desflurane MAC-awake by *ascending* stepwise
equilibration. All of these are equilibrated determinations, not fast-washout
ones, so all three fractions belong against the vessel-rich trace. But ascending
and descending determinations are not interchangeable, and no descending-washout
MAC-awake for desflurane was found. The three fractions (0.31 isoflurane, 0.34
sevoflurane, 0.36 desflurane) sit in a narrow range, so each agent carries its
own value rather than one fraction covering all three.
<!-- provenance: data/agents/isoflurane.json mac_awake.fraction_of_mac = 0.31 -->
<!-- provenance: data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34 -->

<!-- provenance: data/agents/desflurane.json mac_awake.fraction_of_mac = 0.36 -->

**The band is drawn at a fraction of the stored MAC.** MAC-awake is stored as
that fraction, never as a percent of one atmosphere. Each source expresses
MAC-awake as a ratio to MAC, and Katoh does so explicitly, "as a ratio to
age-adjusted MAC". A published *percent*, by contrast, is tied to whichever MAC
its own population was measured against. Desflurane shows the risk. Chortkoff's
MAC-awake of 2.60% is 36% of a MAC of about 7.25%, Rampil's figure for ages
18-30. The stored MAC is Rampil's figure for ages 31-65, 6.0%. Dividing 2.60% by
6.0% would give 0.433 instead of the published 0.36, so the band would be drawn
20% too high and crossed too soon. Storing the fraction avoids that error. The
chart's MAC axis is also scaled by the stored MAC, so the band sits at its
published fraction on that axis. For desflurane, storing the fraction allows an
independent check. The band's centre is 0.36 of the stored 6.0%, or 2.16%, and
Song et al. measured 2.17% in the non-jaundiced control arm of a population that
Rampil's 31-65 year MAC describes.

<!-- derived: 0.433 from data/agents/desflurane.json mac_percent = 6, mac_awake.fraction_of_mac = 0.36 -->
<!-- derived: 2.16 percent from data/agents/desflurane.json mac_awake.fraction_of_mac = 0.36, mac_percent = 6 -->

**The *absolute height* of the MAC-awake band and the 1 MAC line inherits every
limitation of the stored MAC.** The MAC-awake fractions come from primary
measurements in humans (tier 1). The stored MAC is Gas Man's parameter, not a
measurement, so the source hierarchy grades it tier 3
(`docs/MODEL.md` § "Source hierarchy: what may be cited as the authority for a value").
`docs/MODEL.md` § "Delivery-limit and MAC parameters" records its limitations. The interface
shows that MAC, so a reader can compare it with the value they would use.

**Three misreadings of the band all make emergence look faster than this model
says.** Concentration falls during emergence, so a trace crosses a higher
reference sooner, and a faster-falling trace crosses any reference sooner. The
three are:

1. reading the band against the alveolar trace instead of the vessel-rich one;
2. drawing the slow-washout value against a fast-washout alveolar trace, where
   0.22 would be the matching figure;
3. dividing a published MAC-awake percent by a MAC other than the one its
   population was measured against, as in the desflurane example above.

A learner who takes away any of these errors carries into practice the belief
that a patient is more awake than they are.

**The stored MAC is a fourth source of error in the band's height, and the
error's direction differs by agent** (`PL-GCGX`). That MAC is a flat adult
value. The traces are absolute partial pressures and do not depend on MAC, so
wherever the stored MAC departs from the literature, the band moves against the
traces by the same proportion. `docs/MODEL.md` § "Delivery-limit and MAC parameters" compares
the stored MAC with Mapleson's age-40 values. Against them, the stored MAC is
11.1% high for sevoflurane, 2.6% high for isoflurane and 9.1% low for
desflurane. All three are gaps from Mapleson's MAC, not from the MAC that each
source used. Mapleson's 95% confidence limits are about ±7%, and ±10% for
desflurane. Only sevoflurane's gap is larger than its limits, so the
sevoflurane band probably sits too high, by about 11% if Mapleson is right. A
band drawn too high teaches an earlier wake-up. In the washout run above, the
vessel-rich trace crosses sevoflurane's drawn band centre of 0.68% at 6.55 min.
It crosses 0.612%, the same fraction of Mapleson's 1.80%, at 7.30 min. The
isoflurane and desflurane gaps are inside the limits, so Mapleson does not show
either band to be off. Song et al.'s measurement also agrees with the drawn
desflurane band.
<!-- derived: 0.68 percent from data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34, mac_percent = 2 -->

The comparison with Katoh's own MAC at age 40 points the same way as the
Mapleson one: the band sits slightly high, so it teaches a slightly early
wake-up (`PL-P319`). Katoh's fractions are ratios to each patient's
age-adjusted MAC, which comes from two linear equations on p. 1013. For
isoflurane it is 1.43 − 0.0061 × age (yr) percent, and for sevoflurane
2.56 − 0.0156 × age (yr) percent. The paper cites four MAC studies for the
equations but does not say how the equations were derived from those studies.
At age 40 the equations give 1.94% for sevoflurane and 1.19% for isoflurane.
The stored MAC is 3.3% above Katoh's for sevoflurane and 1.2% above it for
isoflurane, so the band sits above Katoh's own age-40 awakening concentration
by the same proportions. The drawn centres are 0.68% sevoflurane and 0.372%
isoflurane, against 0.658% and 0.368% from Katoh's fractions times Katoh's
age-40 MAC. Both differences are much less than the standard deviation of
Katoh's fractions, 0.05 of MAC. Katoh's slow-washout patients themselves woke
at a mean end-tidal 0.63 ± 0.11% sevoflurane and 0.36 ± 0.08% isoflurane
(Table 1, p. 1014). Those figures are lower than the band mostly because the
patients were older, with mean ages of 45.9 and 45.1 years, so they are not a
like-for-like check of a band drawn for age 40.
<!-- not-restated: 0.36 -->
<!-- provenance: data/agents/sevoflurane.json mac_awake.standard_deviation_fraction_of_mac = 0.05 -->
<!-- provenance: data/agents/isoflurane.json mac_awake.standard_deviation_fraction_of_mac = 0.05 -->
<!-- derived: 3.3% from data/agents/sevoflurane.json mac_percent = 2 -->
<!-- derived: 1.2% from data/agents/isoflurane.json mac_percent = 1.2 -->
<!-- derived: 0.68 percent from data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34, mac_percent = 2 -->
<!-- derived: 0.372 percent from data/agents/isoflurane.json mac_awake.fraction_of_mac = 0.31, mac_percent = 1.2 -->

**For developers.** The model's code (`core/`) computes neither reference, and
no governing equation uses MAC-awake or the stored MAC (`mac_percent`). Each
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
(`AgentUptakeSystem.for_agent("sevoflurane")`) at 0.1 s steps. Since the
2026-10-31 run, each crossing time is interpolated between the two steps on
either side of it. The automated test reads the protocol and its figures from
this section (`tests/reference/test_mac_awake_washout_figures.py`), so a
parameter change that moves a figure fails it, and so does an edit to the
protocol or to a figure on its own.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

### F_A/F_I as a displayed ratio

**A second plot, under the compartment chart, draws $`F_A/F_I`$.** It shows the
modelled alveolar fraction divided by the modelled inspired fraction, over the
same time window, on a fixed, dimensionless axis labelled from 0 to 1. The
uptake literature is taught from this curve, and the wash-in figures a reader
has seen show it. The plot can therefore be laid beside a published figure. The
six compartment concentrations on the chart above cannot. A validation test
compares the plotted ratio with human measurements at 30 minutes, for all three
agents in the simulator (`docs/MODEL.md` § "Published wash-in and elimination validation test").
The ratio is computed only for display, and no equation of the model uses it.

**The ratio is a modelled value, not a measurement.** It has the alveolar
compartment's limitation: this model has no airway sampling delay and no dead
space. It is not a depth of anesthesia, a time to any endpoint, or a
prediction for an individual patient.

**The denominator is the modelled inspired concentration, not the vaporizer
dial.** This model assumes that the inspired fraction is the concentration in
the breathing circuit (`docs/MODEL.md` § "Model boundary"). The circuit approaches the
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
which applies. One calculation produces both the caption and the trace, so they
cannot disagree.

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
See `docs/MODEL.md` § "Published wash-in and elimination validation test".

**For developers.** The ratio and its two boundaries are computed only in
`app/wash_in.py`, a module that contains nothing else. Unit tests cover both
(`tests/unit/test_wash_in.py`). The ratio is no part of a run's definition. A
test checks that the plotted ratio is the quantity that the validation compares
(`test_the_displayed_ratio_is_the_quantity_this_file_validates`).

The control marks on both plots are drawn in one pass over the same setting
changes.

The 0.01% limit on $`F_I`$ is derived from the concentration display's
resolution (`CONCENTRATION_DISPLAY_RESOLUTION_PERCENT`), so it follows that
resolution if the display changes.

The rounding allowance of 1e-6 (`WASH_IN_ROUNDING_ALLOWANCE`, `PL-N559`) is
there because, at zero cardiac output, the stepped run settles on a
floating-point fixed point within about 1e-13 of the exact solution. A fixed
point is a state that every later step returns unchanged. In some runs that
state has $`F_A`$ above $`F_I`$. An isoflurane run at a fresh gas flow of
10 L/min settles at a ratio of 1 + 2.2e-14, which the plot once captioned as
the patient returning agent. Because later steps return the same state, the
overshoot does not grow with run length. On 2026-10-26 it was the same at 96 h
as at 1 h. A test checks the fixed point against the exact solution for each
shipped agent
(`test_a_zero_cardiac_output_steady_state_is_not_read_as_elimination`).
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->

The allowance is sized from the 1% limit above, a clinical requirement, rather
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
9.6e-14.
<!-- provenance: core/supported_ranges.py MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The chart code recomputes the stretches in each frame, from the columns that
frame draws, rather than keeping them as the run goes. A stretch can therefore
start or end only at an instant that the chart plots (`app/chart_frame.py`,
PL-2FM6).

The column at which the $`F_A/F_I`$ curve crosses equilibrium has a ceiling,
because the ratio can jump. In runs stepped at 0.1 s, the first value above
equilibrium is at most 1.00235, across every shipped agent and every supported
alveolar ventilation and cardiac output, at the maximum fresh gas flow.
Changing the circuit volume (`BreathingCircuit.set_circuit_volume`), however,
keeps the agent in the circuit and changes the volume it is divided by.
Doubling the volume between two steps therefore halves $`F_I`$ and doubles the
ratio. No interface control changes the circuit volume today, but the plot
should not rely on that. The ceiling is 1.05 (`WASH_IN_TERMINUS_CEILING` in
`app/chart_frame.py`), below the axis top of 1.15 (`WASH_IN_AXIS_MAXIMUM`), so
even the highest crossing column it allows still has clear space above it.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
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
(Reflow) and 1.4.12 (Text Spacing). Keyboard and screen-reader support is an
open question, not a commitment, because it depends on what the software that
draws the window can deliver.

Two criteria carry most of the weight:

- **SC 1.4.3, Contrast (Minimum)**, requires 4.5:1 for text. Every readout,
  every label naming a readout, and every agent name over its identification
  color must meet it. The project never uses the large-text exception (18pt, or
  14pt bold), so the larger readout values must meet 4.5:1 too, and so must the
  bold status text, set at the default size of 14px.

  **Text is measured against the surface it is drawn on: the page background
  or a panel.** The run-status word, the halted-run notice and the
  educational-use disclaimer sit directly on the page background. The
  readouts, their labels, the axis description and the accounting lines sit
  inside panels, which are lighter than the page. Where a color appears on
  both, the page background is the stricter test, and it is the one that
  counts.
- **SC 1.4.11, Non-text Contrast**, requires 3:1 for graphical objects. Here
  that means each chart trace against the panel it is drawn on, each agent
  swatch treated as a shape, and the active track of each parameter slider,
  which shows where the slider's value sits in its range.

<!-- not-restated: 4.5 -->

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

**The contrast ratios are computed from the interface's own colors**, with
WCAG 2.2's definitions of relative luminance and contrast ratio, each time the
project's checks run. Each requirement is a minimum ratio that named colors
must reach, such as 4.5:1 for a readout's text on its panel. A requirement
whose colors miss its minimum today is a shortfall. Each shortfall is recorded
with the work item that will fix it.
<!-- not-restated: 4.5 -->

**The window is always light, even on a computer set to dark appearance**
(project owner, 2026-09-20, ratified - chosen over leaving the host appearance
alone, and over growing a second palette for dark appearance). All 24
requirements are measured on the light theme's panel and page background. The
six compartment trace colors were chosen to meet their minimums under simulated
dichromacy on those same surfaces. A window drawn on other surfaces would show
color pairs that nothing has measured. A disabled control still takes its
colors from the computer's setting, apart from one disabled color that the
interface declares. That color's contrast is checked too.

**Color is never the only cue.** SC 1.4.1 (Level A) requires this. Telling a
running simulation from a halted one is safety-critical. The status words
"Running" and "Valid" differ from the words for the opposite states, which
appear in the alert color, so a reader who cannot tell the colors apart still
reads the state.

The agent selector and the header back the written name with the
agent-identification color of ISO 5360:2016 Table 2 ("Dimensions and colours
of agent-specific bottle collars and connectors"): yellow for sevoflurane,
purple for isoflurane, and blue for desflurane. Footnote b of that table is why
the color appears at all: "if a colour is used on a vaporizer, bottle, or
package label to facilitate correct identification, it is important that only
the colour for the appropriate anaesthetic agent be used". The footnote makes
displaying a color an obligation to display the correct one, which is a
stronger reason than SC 1.4.1 for never using color as the only cue. A second
cue keeps a mis-seen color from becoming a mis-identified agent, so the agent
name always accompanies the color.

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
only for bold colored text: the run-status word, a transient notice line, the
agent-accounting status word, the permanent educational disclaimer, and the
case-discard dialog. The agent colors above follow a standard because it
requires them, and nothing requires the alert color.

IEC 60601-1-8 governs *visual alarm signals*, which are indicators that encode
priority by color together with a flash rate. This interface has no indicator
lamp, filled banner, flashing element or priority tier, so the convention has
nothing to apply to.

The disclaimer settles the question against the convention. The alert color
marks a line that is on screen *always*, while a monitor's alarm colors carry
meaning because they are absent until something is wrong. A permanent element
painted in a high- or medium-priority alarm color would teach the opposite of
the convention it borrowed. Departing from the convention is also wanted for its
own sake. A teaching tool that looks unmistakably unlike a monitor cannot be
mistaken for one, which is the view this project's disclaimers already take.

*The disclaimer line is always placed in the layout, but it is not in view on
every screen today* (`PL-JSY5`, 2026-10-18). The argument above needs only that
the line is a permanent statement, not a conditional one, and that is true at
every window size. The paragraphs on the disclaimer line in
§ "What this list requires once the layout is the reader's" describe where the
line is placed and the one gap in that placement.

The boundary of the supported run length is shown in the muted color, not the
alert color. Coloring a correct model's declared boundary as a fault would
teach a reader to distrust a sound number. § "Supported run length" gives the
rest of the argument.

**For developers.** The contrast check (`tools/contrast_check.py`) runs in
`make check`. It reads the color constants from `app/theme.py`, which contains
every one of them. A second check (`check_colors_live_in_the_theme`) keeps them
there.

Each entry in the contrast check's requirement table names the colors, the
criterion and the reason for the minimum. The table records which colors
matter, and the check only evaluates it. Most entries are one foreground against
one background. Some elements show their edge in either of two colors, such as
an agent badge, which is a fill outlined in the agent's own text color. The
entry for such an element declares both colors. The element passes when the
better of the two meets the minimum, because a reader finds the edge by
whichever color contrasts more. Shortfalls are listed in the same table. The
check reports an error when a listed shortfall starts passing, so a fix cannot
leave its listing behind.

Measuring text on the panel alone once hid a shortfall, fixed in `PL-X0RG`.
The label color gave 4.28:1 on the panel and 3.98:1 on the page, where the
run-status word is drawn.

A color that carries meaning both as text and as a graphic needs two
constants, because text needs 4.5:1 and a graphic 3:1, and one constant serving
both roles fails one of them. The accent color is the only such case. The
sliders' active track uses `ACCENT`, and "Running" and "Valid" use
`ACCENT_TEXT`, the same hue darkened until it is legible as text.
<!-- not-restated: 4.5 -->

The excuse for lines that overlap little comes from the Understanding document
for SC 1.4.11, read on 2026-09-07 in a copy the project owner supplied
(`PL-JX0Z`). Its line-graph example (Figure 38) says: *"The lines should have
3:1 contrast against their background, but as there is little overlap with
other lines they do not need to contrast with each other or the graduated
lines."* Its "Graphical Objects" section makes each line in a graph a graphical
object in its own right. Citing the Gestalt "law of continuity", it lets
**minor** overlaps between lines be ignored.

Because the criterion does not require pairwise separation, the contrast check
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

The gridline grey's exemption (`GRIDLINE`) rests on the Understanding document
for SC 1.4.11. The document's line-graph example does ask 3:1 of a chart's
"background lines for the values", but in that example the gridlines are how a
value is perceived at all. Under the heading "Required for understanding", the
document says the criterion does not apply when "a graphic with text embedded
or overlaid conveys the same information, such as labels and values on a
chart". This chart passes the criterion's own test: imagine the gridlines
invisible, and ask whether the chart is still understood. The criterion's
paragraph on boundaries expressly excuses cases such as the line between
sections and the groove.

Darkening the grey was refused because of the chart's visual order, in which a
gridline sits below a reference line and a reference line below a trace. A
gridline at 3:1 would be 87% as dark as the lightest trace (3.43:1), and that
order would collapse. Line widths of 1 / 1.5 / 2-3 px also carry that order.

Supporting dark appearance would mean measuring every requirement again on a
second pair of surfaces, and choosing all six trace colors again under four
vision models.

A declared color reaches the screen by one of three mechanisms. Most of the
interface is drawn by stylesheets, all composed in one module
(`app/stylesheets.py`) from the theme's color constants (`PL-Y4YX`). Some
widgets are painted from Qt palette roles instead: an entry's fill, a spin
box's stepper, a list's rows and its scroll bar, a check box's indicator and a
dialog's own surface. A stylesheet would cost them the native stepper and the
check box's tick. For those widgets, a function
(`qt_widgets.declare_interface_colours`) declares the same theme colors as
palette roles. It maps PANEL and INK to `Base` and `Text`, MUTED to
`PlaceholderText`, and PRIMARY and PANEL to `Highlight` and `HighlightedText`,
so the pairs on screen are pairs that the requirement table already measures.
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

Disabled controls follow the host because all three mechanisms leave the
`Disabled` color group to the platform. The project's rule for interface colors
(`.claude/rules/ui-color.md`) governs any decision to declare a disabled color.
The splitter handles are enabled (`PL-W9P6`), so the border between two areas
shows the page's `BACKGROUND` under a dark host too, rather than the host's dark
surface. A test
(`test_the_border_between_two_areas_shows_the_page_rather_than_the_host`)
checks this (`PL-05M4`).

Tooltips also follow the host, because they draw from `ToolTipBase` and
`ToolTipText`, which are outside the declared roles. This interface uses no
tooltip today.

The dark-appearance test (`tests/integration/test_dark_appearance.py`) renders
the dashboard and both dialogs under the palette a dark host supplies. It
fails on any content widget that resolves to that palette, and it checks the
chrome and the untouched `Disabled` group against the same host. Under that
host palette, 94.3% of the page scroll bar's pixels are darker than mid-grey
without the interface's own palette, and none are with it.

A second test (`tests/integration/test_simulation_view.py`) catches any control
that declares no color, including one added later. It builds the whole
dashboard under a foreground color that this interface never uses, and fails
on any control that paints its own content and resolves to that color. It
exempts only kinds of control that draw no text, and names each kind with its
reason. A requirement exists only where somebody wrote a color down, so the
contrast check counts those kinds into its report line. Without that count, a
control that declares no color would appear on neither side of the report
line, and the line would show it as covered (`PL-4L49`).

The cited standard references, the screen-color approximations and the
accessible foregrounds are kept together in `app/theme.py`, so that the
agent-color mapping can be audited as one unit. Every foreground and background
pair must meet WCAG 2.2 AA contrast. Tests in `tests/unit/` check that the
agent name is shown beside its color in the selector's options and in the header
badge.

Each Munsell original was converted to sRGB via Illuminant C, chromatically
adapted to D65. The dichromacy figures were computed by the contrast check with
the Brettel 1997 projection recorded under § "The six compartment traces". A
test pins them, so a color change cannot leave them out of date
(`tests/unit/test_contrast_check.py`).

The alert color is `WARNING` in `app/theme.py`, and the muted color is
`MUTED`. Whatever alert color is chosen, two constraints apply. It must still
meet the interface's contrast target, which the contrast check enforces. The
ISO 5360 agent colors stay as they are, because they identify an agent and
carry no urgency.

The alert-color decision applies to the Qt port as much as to the current
interface. The port chooses its palette afresh, and an indicator-shaped element
could first appear in it, so the port must not arrive with a monitor's priority
palette.

IEC 60601-1-8's mapping of priority to color could not be established from a
primary source, and the secondary sources disagree. Three independent reports
give the low-priority color as cyan, as blue, and as "green or blue". The
alert-color decision does not depend on the mapping.

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
equally bright.** The closest pairs are vessel-rich and fat, and mixed venous and
fat. No other choice of colors fixes this. Each color has at least the 3:1
contrast against the panel that WCAG success criterion 1.4.11 requires, both as
displayed and as simulated for protanopia, deuteranopia and tritanopia. The
colors are chosen to label their compartment and to clear that minimum.

**The colors decide which line style goes on which compartment.** The two traces
whose colors are hardest to separate get the two styles that are easiest to
separate by shape. The next pair gets the next easiest, and so on. Fat's
dash-dot therefore differs in dash length, gap length and rhythm from both the
vessel-rich even dash and the mixed venous short dash. The one pair of styles
that a reader could confuse is dotted, with 2 px dots, and short dash, with 4 px
dashes. That pair goes to muscle and mixed venous, whose colors are the second
most widely separated pair among these six (1.45 in the table below, after
circuit and alveolar at 1.62).

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

**For developers.** A script computes every figure in this section
(`tools/contrast_check.py`), and a unit test checks the script's results against
these figures (`tests/unit/test_contrast_check.py`). The script runs as part of
`make check`, and its `--matrix` option prints the pairwise table below.

Each trace has this contrast against the panel, as displayed (Normal) and as
simulated for each dichromacy:

| Trace | sRGB | Normal | Protanopia | Deuteranopia | Tritanopia |
| --- | --- | --- | --- | --- | --- |
| Circuit | `#176B87` | 6.02 | 5.67 | 6.21 | 6.02 |
| Alveolar | `#159789` | 3.61 | 3.23 | 3.84 | 3.63 |
| Mixed venous | `#7C3AED` | 5.70 | 5.96 | 4.68 | 5.55 |
| Vessel-rich | `#DC2626` | 4.83 | 7.18 | 4.14 | 4.84 |
| Muscle | `#D17206` | 3.43 | 3.96 | 3.22 | 3.46 |
| Fat | `#64748B` | 4.76 | 4.74 | 4.76 | 4.77 |

The contrast between each pair of traces is far lower, and the design in this
section rests on it:

| Pair | Normal | Protanopia | Deuteranopia | Tritanopia | Worst |
| --- | --- | --- | --- | --- | --- |
| Vessel-rich / Fat | 1.01 | 1.51 | 1.15 | 1.02 | **1.01** |
| Mixed venous / Fat | 1.20 | 1.26 | 1.02 | 1.16 | **1.02** |
| Alveolar / Muscle | 1.05 | 1.23 | 1.19 | 1.05 | **1.05** |
| Circuit / Mixed venous | 1.06 | 1.05 | 1.33 | 1.08 | **1.05** |
| Alveolar / Vessel-rich | 1.34 | 2.22 | 1.08 | 1.33 | **1.08** |
| Mixed venous / Vessel-rich | 1.18 | 1.20 | 1.13 | 1.15 | **1.13** |
| Circuit / Fat | 1.26 | 1.19 | 1.31 | 1.26 | **1.19** |
| Muscle / Fat | 1.39 | 1.20 | 1.48 | 1.38 | **1.20** |
| Alveolar / Mixed venous | 1.58 | 1.84 | 1.22 | 1.53 | **1.22** |
| Alveolar / Fat | 1.32 | 1.47 | 1.24 | 1.31 | **1.24** |
| Circuit / Vessel-rich | 1.25 | 1.27 | 1.50 | 1.24 | **1.24** |
| Vessel-rich / Muscle | 1.41 | 1.81 | 1.28 | 1.40 | **1.28** |
| Circuit / Muscle | 1.75 | 1.43 | 1.93 | 1.74 | **1.43** |
| Mixed venous / Muscle | 1.66 | 1.50 | 1.45 | 1.61 | **1.45** |
| Circuit / Alveolar | 1.67 | 1.75 | 1.62 | 1.66 | **1.62** |

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
setting uses the same resolution, in the readout beside its slider and in the
label shown while the slider is dragged, so the setting and the values it
produces are read at one scale. A positive value that would round to `0.00%`
is displayed as `<0.01%`, so `0.00%` means only that no agent has arrived, as
before a run starts.

Each digit shown is accurate for this model with its parameters. No displayed
value can be trusted to its last digit as a prediction about a patient
(`docs/MODEL.md` § "Known limitations").

**For developers.** One test enforces the display resolution
(`test_format_percent_uses_the_documented_display_resolution`), and another
enforces the `<0.01%` form
(`test_format_percent_marks_a_value_below_the_resolution`).

#### Why the readouts show two decimals

**The equation solver does not limit how many decimals a readout can show.** On
2026-09-06, the simulator's results differed from an independently computed
solution by at most $`1.6\times10^{-12}`$ percentage points anywhere in the
reference test's runs, and by $`5.2\times10^{-12}`$ over an hour with the
settings held constant. That is about one two-billionth of the last displayed
digit, so **a third decimal would not be numerical noise.** Instead, what the
model's parameters can support sets the upper limit on the number of decimals,
and legibility sets the lower limit.

**Two questions about resolution must be kept apart: how finely two moments
within one run can be told apart, and how finely this model resolves a
concentration in a patient.** Within a run the parameters are fixed and the
simulation is deterministic, so the answer to the first is about nine decimal
places finer than the readout shows. The second is the question that a clinician
reading a percent sign is asking, and its answer is much coarser.

**The model's parameters set the upper limit on decimals: one measured standard
deviation of a partition coefficient is worth about one to seven counts of the
last displayed digit.** One count is 0.01 percentage points. When a single
stored coefficient is perturbed by one published SD and the run is repeated at
1 MAC with the reference adult's flows, a displayed compartment's reading shifts
by these amounts, which have no test yet (`PL-19W8`):

| Coefficient perturbed by one SD | Displacement, worst over 3600 s |
| --- | --- |
| Fat tissue:gas | 8.7×10⁻⁴ to 6.7×10⁻³ pp |
| Blood:gas | 1.5×10⁻² to 5.4×10⁻² pp |
| Vessel-rich tissue:gas | 1.3×10⁻² to 5.0×10⁻² pp |
| Muscle tissue:gas | 1.3×10⁻² to 6.8×10⁻² pp |

<!-- not-restated: 1.3 -->

Each range covers the three agents that the simulator offers, and desflurane
always gives the largest displacement, an ordering that has no test yet
(`PL-19W8`).

The SDs are the measured ones that `docs/MODEL.md` § "Parameter provenance" records. For
desflurane's blood:gas coefficient the SD is Eger's $`0.424 \pm 0.024`$, which is
5.7%. The tissue SDs are those of Yasuda, Targ and Eger's human tissue
coefficients, 3.9% of the mean for desflurane, 5.3% for sevoflurane and 6.4% for
isoflurane. These three are the source's brain:blood SDs, and the SDs for fat are
larger. Which SD was perturbed for each row is being checked, with no test yet
(`PL-TDX0`).

So the last digit of a two-decimal readout lies between about a seventh of one
parameter SD and seven times it. A third decimal would put the last digit at one
seventieth to seven tenths of one SD. It would claim a resolution one to two
orders of magnitude finer than the spread that the measured SDs produce, in the
readouts where a reader is least able to notice. Such false precision is why the
display stops at two decimals.

A digit finer than one SD is still honest, because an SD changes where the whole
curve sits, not how finely two points on it can be told apart. So the SD does not
limit a reader who compares 09:14 with 09:16 of one run. A digit *far* finer than
one SD is ruled out, because a reader cannot tell whether a printed digit
separates two moments of one run or resolves a concentration in a patient.

**Legibility sets the lower limit on decimals: one decimal hides the slow
compartments' wash-in, which is the reason for displaying them.** At one decimal
the sevoflurane and isoflurane fat fractions read `0.0%` for the whole hour
(0.032% and 0.015% at 3600 s). Desflurane's fat fraction stays at `0.0%` for its
first 19.3 minutes and reaches 0.2%. Muscle reads `0.0%` for its first 2.9
minutes with desflurane, 8.5 minutes with sevoflurane and 14.8 minutes with
isoflurane. At two decimals, at 1 MAC with default flows, muscle first shows a
nonzero value at 57, 125 and 190 seconds and fat at 237, 781 and 1477 seconds,
for desflurane, sevoflurane and isoflurane in that order. These times have no
test yet (`PL-19W8`).

This lower limit is the project owner's teaching judgment, not a property of the
model: the solver and the parameters both support one decimal comfortably. One
decimal is ruled out because a simulator built to show uptake and distribution
would then show a flat zero where the uptake is happening.

**So the number of decimals lies in a band of one to two, and two is the chosen
count.** The choice inside the band is a presentation decision, which the owner
may revise without re-deriving anything in the model. Moving the readout to one
decimal would change what a reader sees and which settings a slider can reach,
but nothing in the model's equations.

**Why not the 0.1 percentage points that agent monitors show.** Agent monitors
display end-tidal and inspired concentrations to a tenth of a percentage point,
which would suit the circuit and alveolar readouts. This simulator also displays
compartments that no monitor shows, and at one decimal fat and muscle read `0.0%`
for the times given under the lower limit above, which have no test yet
(`PL-19W8`). A resolution of 0.01 percentage points is the coarsest that keeps
every displayed compartment legible. It is a coincidence that this is also close
to what the parameters support, because the two were measured independently.

**Why not significant figures.** A significant-figures rule gives the smallest
values the most decimal places, and the small values are where this model
supports the least. The parameters' measured SDs are *relative*, 3.9% to 6.4% of
the mean, so they apply undiminished to a compartment holding a thousandth of a
percent. Three significant figures on the fat fraction would imply a relative
resolution of 0.1% on a number whose parameters are known to about 5%, which
over-claims by a factor of fifty. The equation solver is not the limit here. With
the exact method that the simulator uses, compartments that hold little agent
have a relative error of at most $`2\times10^{-4}`$ anywhere in the first ten
seconds of a run, and $`8\times10^{-11}`$ at ten seconds itself. The SDs here are
the brain:blood ones noted above, so this paragraph is being corrected, and its
figures have no test yet (`PL-TDX0`).
<!-- not-restated: 5 % -->

**Why a value below the resolution is shown as `<0.01%` rather than as zero.**
Even at two decimals, muscle and fat start below the last digit, for the times
given under the lower limit above. Showing `0.00%` then would state that the compartment
holds no agent, which the model does not say. The model says that the
compartment is filling, below what the display resolves, and `<0.01%` states
exactly that. The display marks what it cannot show, rather than adding a decimal
that the model cannot support.

A negative value is never shown as `<0.01%`, where it would pass for a plausible
small positive reading. The model cannot hold a negative concentration
(`docs/MODEL.md` § "Concentrations"), so a negative value that reaches the display means that
something upstream is wrong, and the display refuses it.

**For developers.** The readout's decimal count must not feed back into the
model, and nothing in the `core/` directory reads it. The maximum simulation
step (`MAXIMUM_SIMULATION_STEP_S`) is a tolerance in seconds, and the supported
input ranges are intervals in L/min. Both are derived without reference to the
readout, in `docs/MODEL.md` § "Supported simulation step" and `docs/INTERFACE.md` § "Supported input ranges". A
future change to one decimal has to answer the objection to it given under the
lower limit above. The negative concentrations that the model cannot hold
include minus zero (`docs/MODEL.md` § "Concentrations"). No value of the `Fraction` type can be
negative, and the formatter is the code that refuses a negative value.

#### The MAC multiple's resolution

**The MAC readout shows the MAC multiple in steps of 0.01 MAC.** One step is 0.02
percentage points of sevoflurane, 0.012 of isoflurane and 0.06 of desflurane. Each is
at least the percent readout's 0.01 percentage points, because the MAC multiple is
calculated from the percent concentration and can be no more precise than it. The two
readouts round separately, so the MAC readout can occasionally change while the percent
readout stays the same. The three per-agent figures have no test yet (`PL-19W8`).
<!-- not-restated: 0.06 -->

A MAC multiple above zero but below 0.01 MAC shows as `<0.01 ×MAC`. The `<` sign
matters more on the MAC readout than on the percent readout, because a filling
compartment reaches 0.01 percentage points before it reaches 0.01 MAC. In between,
`0.00 ×MAC` would contradict the percent readout above it, which already shows the
compartment filling.

**For developers.**
The MAC resolution is derived from the percent resolution rather than stored beside
it, so that re-measuring the percent resolution never leaves a second number to
update. Divided by the agent's MAC in percent (`mac_percent`), 0.01 percentage
points is 0.005 MAC for sevoflurane, 0.0083 for isoflurane and 0.0017 for desflurane.
The MAC resolution is the finest power of ten at or above the coarsest of these,
isoflurane's 0.0083. A test repeats this arithmetic for every shipped agent
(`test_the_mac_resolution_is_derived_from_the_percent_resolution`) and fails if
adding an agent or changing the percent resolution would make the MAC readout finer
than the percent readout supports. Another test checks the `<0.01 ×MAC` form
(`test_format_mac_multiple_marks_a_value_below_the_resolution`).

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
the display resolution (`test_the_model_keeps_precision_the_display_throws_away`).
The two runs must reach different states and must still look identical on the
display.

#### Comparing two readouts

**A reader can rely on which of two compartments the readout row shows as higher,
except possibly while the two cross.** The interface therefore adds no warning or
marker when readouts are compared. Where seven panels fit, the six compartment readouts
and the clock sit in one row, so that the readouts can be read *in order*: the circuit
leads the alveoli, and the alveoli lead the tissues.
§ "The readout row's width condition" below says what happens when seven panels do not
fit.

When a reader compares two readouts, the simulator's calculation error could mislead them
only by reversing which of the two is shown as higher. A test compared every pair of the
six readouts at every time step, for all three agents, in every run that
`docs/MODEL.md` § "Independent-solution test" describes: 1 485 000 pairs of readings in all. The
simulator's readings **never** disagreed with those of the independent solution about
which compartment is higher, even where the gap was tiny (checked 2026-10-17).

This result comes from runs on one computer platform and is not a guarantee.
Because rounding to a fixed number of decimals never reverses the order of two
values, the display can show two compartments in the wrong order only where the
simulator and the independent solution put them in opposite order. Such a reversal needs
a true gap smaller than the two compartments' calculation errors added together. In
every run, the simulator's gap between any two compartments differed from the
independent solution's by at most $`1.1\times10^{-12}`$ as a fraction, not a
percent. True gaps that small do occur while two compartments cross, so a reversal
is arithmetically possible there.

**A gap that a reader works out from two readings can differ from the true gap by
up to one count of the last displayed digit.** Each reading is rounded to that
digit. The gap carries the rounding of both readings and the simulator's calculation
error, up to the limit in the paragraph above. That calculation error does not make the
gap less accurate than either reading. The interface shows no gap between two readouts.

**For developers.** Two tests enforce the claim about which compartment is shown
as higher. Each covers one half of the path from the model to the readout and can
fail on its own. The first bounds the simulator's calculation error against the
independent solution
(`test_exact_step_matches_the_independent_solution_everywhere`). The second checks
that the interface's formatter, `format_percent`, never shows a higher fraction as
a lower percent (`test_format_percent_preserves_order` in
`tests/unit/test_formatting.py`). It covers the "<0.01%" reading below the display
resolution and both sides of every value at which the last displayed digit changes.
Together the two tests mean that no reversal can occur at a true gap above twice the
first test's tolerance: $`1.0\times10^{-7}`$ counts of the last displayed digit. A
third test makes the comparisons described above, reading each value through the
interface's formatter (`test_displayed_ordering_reverses_only_at_a_crossing`). It
allows a reversal where the true gap is below the first two tests' threshold of
$`1.0\times10^{-7}`$ counts, because one is possible at a crossing. It fails only when
one of those tests fails, so it records the result and adds no evidence of its own.

The claim about a gap's calculation error rests on one property of the model: within one
time step, it updates every compartment from the values at the start of that step.

#### One resolution for all six readouts

**All six compartment readouts show the same number of decimal places, for two
reasons.**

- **The six readouts are compared with one another.** If they showed different
  numbers of decimal places, digits of different place value would sit in the
  same position, and someone scanning the row would misjudge a value by a factor
  of ten. This reason comes from how the row is read, so it applies however the
  simulator computes the values.
- **The effect of parameter uncertainty varies much less across the six readouts
  than their values do.** § "Why the readouts show two decimals" tabulates the
  one-SD displacements. Across all six compartments and all four coefficients,
  they spread over less than two orders of magnitude, while the readouts'
  *values* span four. One number of decimal places therefore fits all six
  readouts. It is set by the compartments where the displacement is largest, so
  it is conservative where the displacement is smaller.

#### The readout row's width condition

**The readout row's width decides how many panels share a line.** Every panel
takes exactly one column. The panels sit seven across wherever all seven columns
fit the row, four per line where they do not, two where four do not fit, and one
below that. Each column is as wide as the widest value its panel can show: the
clock's longest elapsed time, or a compartment's widest percent and MAC
multiple. The clock therefore widens no other column. In every arrangement each
panel keeps that width, so no value is wrapped away from its unit. The widths at
which the row steps down depend on the font and the display scale. With the font
that the project's tests use, for example, the row is seven across from 1005 px,
four across from 591 px and two across from 310 px (measured 2026-10-18). Those
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

On a 1280 px screen, whether the row still opens seven across beside the
control-change record has no test yet (`PL-LKX7`).

**For developers.** A function sets the row's column count from its width
(`readout_columns` in `src/anesthesia_sim/app/dashboard_frame.py`). A constant
lists the four arrangements (`READOUT_ROW_LADDER`). Column widths come from the
font that the interface draws with, so the code fixes no pixel width that
another font or display scale would make wrong. The step-down widths above are
in logical pixels, for the tests' offscreen font. One test reads those widths
from the row instead of asserting them
(`test_the_readout_row_reflows_where_its_panels_stop_fitting`). Another enforces
the column count and each panel's one-column span
(`test_every_readout_reserves_a_qualifier_line_and_an_equal_column`).

A test checks that the readouts' region stays outside the Areas
(`test_no_unconditional_value_sits_inside_the_layout_container`). The region
(`SimulationView.unconditional_region`) gives 0.82 of its width to a left column
for the readouts and 0.18 to a right column for the control-change record. These
are the shares that the chart panel's Area and the sidebar's Area had in the
layout that the dashboard first opened on. In that layout the record was as wide
as the sidebar beneath it. The Workspaces that ship now divide the width
differently, and the region keeps its own shares. The left column never narrows
below its minimum width.
<!-- not-restated: 0.18 -->

The window is opened maximized (`showMaximized()` in
`src/anesthesia_sim/app/main.py`). A constant in the same file gives the
window's normal size as a fraction of the screen's available area
(`WINDOW_SCREEN_FRACTION`). Opening maximized matches the default window state of
the reference design that the interface follows (`docs/interface-provenance.md`
§ "Adopted").

With the tests' font, a 1366 px window gives the region 1320 px (measured
2026-10-18). The right column takes 235 px and the left column 1073 px, which is
68 px more than the 1005 px that seven across needs. Two tests check that a
1366 px window opens the row seven across in compare mode
(`test_two_runs_share_one_readout_block_whose_values_name_their_runs` and
`test_a_1366_px_window_opens_one_run_s_readout_row_on_seven_columns`). A function
wraps the control-change record (`wrapping_between_parts`). A 1280 px screen
gives the region about 1234 px (measured 2026-09-27, with the tests' font).

#### Time, flows and the chart

**Simulated time is displayed to 0.1 s, which is exactly one simulation step.**
Every recorded control change is stamped at that same resolution, so the
timeline and the clock never show one time in two different forms.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

The screen shows time in one form. The displayed clock, the time stamp on each
recorded control change and the chart's axis ticks are all durations. Each part
of a duration carries its own unit: `45s`, `1m30s`, `1h23m45.6s`, `24h`. A part
that is zero is left out. Tenths of a second appear only where there are some.
The time axis never shows them, because every tick it can place falls on a
whole second.

The one exception is the time span that the chart draws. It is written out in
words, such as `15 minutes` above an axis whose last tick reads `15m`. The
reader picks that phrase from a selector and sees it again in a caption.
§ "Displayed precision" sets the precision at which each form is shown.
§ "The chart's time base" explains the time-axis label form, why it differs
from the clock's, and why the span is written in words.

**For developers.** The clock and the stamps use the time axis's form
because all three are on screen together. A control mark stamped `5400.0 s` on
an axis reading `1h30m` would leave the reader to convert between the two by
hand. At the supported 24-hour run length, a clock in seconds would read
`86400.0 s`, which shows false precision for a limit that this document states
in hours. The tenths of a second are there so that a stamp identifies the
simulation step (`SIMULATION_STEP_S`) at which it was taken. The time axis needs
no tenths because it marks a span that a reader scans, not an instant that they
read off. Tenths on every label would also spend width on a digit that is zero
at every tick spacing that the axis offers. The span's wording does not have to
fit in a tick's width, because neither the selector nor the caption is a tick
label.

**The chart is read for shape, so its resolution is coarser than the
readouts'.** It plots the same percentages on a shared linear axis that runs
from 0 to 3 ×MAC of the agent in use, and a second axis on the right shows the
same position in MAC multiples. Its resolution is set by pixels rather than by
decimals. Every number that the chart offers is shown at the resolutions above,
in the readout row and in the hover readout
(§ "The chart's hover readout: what the tooltip may show", below). The fixed
3 ×MAC range gives the MAC axis round labels in half-MAC steps for every agent,
so a gridline that a reader learns under one agent means the same thing under
the next. § "The chart's vertical range is set in MAC, and fixed" above
explains the range. The reader selects the time span that the chart's width
covers, and so chooses the seconds per pixel (§ "The chart's time base").
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

**Fresh gas flow, alveolar ventilation and cardiac output are displayed to
0.1 L/min**, the resolution of the controls that set them. A slider and the
readout beside it show one quantity, so each slider moves in steps of its
display resolution: 0.1 L/min for the three flows and 0.01 percentage points
for the delivered dial. The value applied to the model is exactly the value
printed beside the control. If a control could apply a value that its own label
rounds away, a reader could not tell which value is the setting in force.

**For developers.** The sliders are integer-valued. Three tests read each flow's resolution from
its control's label (`test_fresh_gas_flow_slider_forwards_value_to_controller`,
`test_alveolar_ventilation_slider_forwards_value_to_controller` and
`test_cardiac_output_slider_forwards_value_to_controller`), and a fourth
enforces the slider steps (`test_the_slider_steps_at_the_display_resolution`).
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

**The panel's three amounts are displayed to 0.1 L, and its two residual lines show
only the power of ten that each residual lies below, because they answer different
questions** (decided 2026-09-15). The amounts are read against each other, delivered
against exhausted plus stored, and against a reader's sense of scale. The residual
lines are a numerical check. They have to make a residual of order 10⁻¹² L visible
against amounts of order 1 to 100 L, which no fixed decimal count can do.

The panel labels the unit as litres of equivalent pure agent gas, the unit this
document uses, because a bare "L" beside an anaesthetic agent invites a reader
to take it as litres of liquid. The label also names the reference condition of
`docs/MODEL.md` § "Agent amount", and says that the amounts held in the body
read high at it (`docs/MODEL.md` § "Known limitations").

**The amounts' 0.1 L step is set by the uncertainty in the simulator's coefficients,
as the readouts' steps are.** Changing one of those coefficients by its published SD
shifts the exhausted total. After 1 h and at 24 h, the longest run the simulator
supports, the shifts are 0.024 and 0.19 L for sevoflurane, 0.016 and 0.18 L for
isoflurane, and 0.042 and 0.23 L for desflurane. The blood:gas coefficient
dominates throughout. These shifts were simulated at 1 MAC with the reference
adult's flows, and have no test yet (`PL-19W8`). At a higher dial setting the
shifts are larger, and no test yet derives the step there (`PL-0P3F`). Delivered
agent carries no parameter uncertainty, because it is the dial setting times the
flow times the time. It is still displayed to 0.1 L, so that the three amounts
read at one scale.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**A residual line such as `<1e-13 L` means that the residual is less than
10⁻¹³ L.** The `<` means the same as it does on the amounts. A residual of exactly
zero reads `0 L`. A residual that passes its check is the rounding left over from
summing the initial, delivered, exhausted and stored amounts. Its digits and its
sign are set by the order in which the arithmetic ran, not by anything modelled.
They change even when a correct edit to the code alters only the last binary digits of that
arithmetic, so neither line shows them. Without a sign, the two lines read alike.
The sign means something only in a check that fails. The run then halts, and the
failure notice prints the signed values to six figures.

**For developers.** At 1 MAC with the reference adult's flows, the shifts in the
exhausted total make one 0.1 L step worth between about two-fifths of an SD and
six SDs from 1 h to 24 h. That range is inside the band that the readouts'
derivation allows. A step of 0.01 L would fall to about a twentieth of an SD by
24 h. A constant stores the amounts' decimal count (`AGENT_AMOUNT_DISPLAY_PRECISION`),
a function formats them (`format_agent_volume`), and a test checks both
(`test_agent_amounts_precision`).
<!-- not-restated: 0.01 L -->
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
either side of a power of ten. Every residual was below 2.1 × 10⁻¹¹ L, every check
passed in both versions, and each run's own path read identically in every form.
<!-- not-restated: 2.1 -->

The residual line's power of ten is computed from the residual's exact
floating-point value. A function formats the line (`format_agent_residual`), and
four tests check it: `test_format_agent_residual_prints_the_power_of_ten_it_lies_below`,
`test_format_agent_residual_drops_the_sign_the_rounding_chose`,
`test_format_agent_residual_bound_is_strict_and_tight_at_every_power_of_ten` and
`test_format_agent_residual_reads_zero_as_zero`. A fifth test uses the pair
`5.601e-14 L` and `5.609e-14 L`, which the two versions printed for one sample
(`test_format_agent_residual_prints_no_digit_a_last_bit_change_redraws`).

#### Agent amounts in millilitres, and the cost

**An agent amount's precision is derived for the amount in one unit, and does
not carry over to another unit.** The derivation above is for litres of vapour.
The agent cost display shows the delivered total in millilitres of liquid, and
the compartment schematic shows each compartment's amount in millilitres of
vapour, so each of those needs its own precision. An amount in a unit that has
no derivation is refused, rather than shown at a default.

The bound is one-sided. It limits only how fine an amount may be shown. A coarser
precision loses detail but claims nothing false. A finer one claims a resolution
that the parameters or the conversion do not support, so it is refused rather
than quietly reduced to the derived precision.

| Amount | Unit | Decimals | Resolution | Derived from |
| --- | --- | --- | --- | --- |
| A run total: delivered, exhausted or stored | Litres of vapour | 1 | 0.1 L | One SD of a partition coefficient, above |
| The delivered total | Millilitres of liquid | 0 | 1 mL | One SD of the measured liquid density |
| The exhausted total | Millilitres of liquid | 0 | 1 mL | The litre's resolution, converted |
| The stored total | Millilitres of liquid | Refused | - | The conversion reads a store 5.8% high |
| One compartment's amount | Millilitres of vapour | Two significant figures, none finer than 0.01 mL | 1% to 10% of the amount | One SD of a partition coefficient, as a share of the amount, below |
| One compartment's share of the agent held | Percent of the stored total | 0 | 1 percentage point | One SD of a partition coefficient, below |

**The exhausted total in millilitres of liquid is shown in whole millilitres.**
It carries the partition coefficients' uncertainty, so it must not claim a finer
resolution in liquid than in litres of vapour. Otherwise a reader who switches
the unit would see the model resolve a difference in one unit that it does not
resolve in the other. One step of the litre display, 0.1 L of vapour, is
0.55 mL of sevoflurane liquid, 0.51 mL of isoflurane and 0.48 mL of desflurane
at the 20 °C reference of `docs/MODEL.md` § "Agent amount". The smallest power of ten at or
above all three is 1 mL. The partition coefficients give the same result. In the
simulations above at 1 MAC with the reference adult's flows, the one-SD shifts
at 24 h are 0.19 L of sevoflurane vapour, 0.18 L of isoflurane and 0.23 L of
desflurane, which are 1.04, 0.92 and 1.10 mL of liquid. So at those settings one
step of 1 mL is about one SD, and a step of 0.1 mL would be a tenth of one.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->

**The delivered total in millilitres of liquid is shown in whole millilitres.**
The delivered agent is the dial times the flow times the time, and its
conversion to liquid at the 20 °C reference is exact. Its only uncertainty in
liquid is the measured density's, which grows in proportion to the total. At
sevoflurane's largest supported total, 8% at 10 L/min for 24 h, one SD is about
3.3 mL. So a step of 1 mL is about 0.3 SD, and no supported setting makes it
finer than the readouts' seventh of an SD. A step of 0.1 mL would be about a
thirtieth.
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->

**A cost is shown to three significant figures.** The agent cost display gives
the cost as the delivered agent in liquid times the reader's price per
millilitre (§ "A cost at the reader's price"). The price is the reader's own
figure, so it carries no modelled uncertainty. The cost's only modelled
uncertainty is therefore the liquid figure's. The largest relative SD of a
stored density is sevoflurane's, 0.0008 g/mL against 1.5203 g/mL, or 0.053 %.
That SD is relative, so the cost's precision is set in significant figures, not
in decimals. With n significant figures, the smallest relative step is 1 in
(10^n - 1), at a value such as 999. At three figures that is 0.10 %, coarser
than one SD of the density, which is allowed because the derived precision
limits only how fine a figure is shown. At four it would be 0.010 %, finer than
one SD.
<!-- provenance: data/agents/sevoflurane.json liquid_density.standard_deviation_g_ml = 0.0008 -->
<!-- provenance: data/agents/sevoflurane.json liquid_density.g_ml = 1.5203 -->

**A cost is never shown finer than a hundredth of its currency**, which is the
smallest unit of most currencies. For example, 0.68 reads `USD 0.68`, not
`USD 0.680`. A positive cost below a hundredth reads `USD <0.01`, and a run that
has delivered nothing reads `USD 0`.

**A price per millilitre is shown to four significant figures.** A reader can
multiply the liquid volume shown by the price shown. Four is the fewest figures
at which the price's rounding moves that product by at most half of the cost's
smallest step. At four figures that rounding is at most 0.5 in 1000 of the
price, and half of the cost's smallest step is 0.5 in 999 of the cost. The
liquid volume, in whole millilitres, is then the only figure in the reader's
multiplication rounded coarsely enough to matter. Its rounding can make the
product miss the cost by up to about half a millilitre's price, and the readout
says that the figures are rounded (§ "A cost at the reader's price").

**The stored total has no precision in millilitres of liquid, and is refused in
that unit.** A store converted to liquid reads 5.8% high (`docs/MODEL.md` § "Known limitations").
That error grows with the amount. At 17 mL of liquid it is already a whole step
of 1 mL, and in a long run it is several steps. No number of decimals can make a
figure with a known bias of several steps read correctly, so the stored total
keeps litres of vapour, as the accounting panel shows it.

The agent cost display is the only part of the simulator that converts an amount
to liquid. It converts only the delivered agent, so no figure it shows carries
the 5.8 % error. It reads the delivered amount and the vapour-to-liquid ratio of
the agent in use from the same moment of the run, so it cannot pair one agent's
vapour with another agent's ratio. Using desflurane's ratio would misstate
sevoflurane by about 13 %.

**The simulator derives each agent's vapour-to-liquid ratio, as the first table
in `docs/MODEL.md` § "Agent amount" does.** It stores the liquid density and the molar mass,
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

**For developers.** One test repeats the litre-to-millilitre conversion for every shipped agent from
the stored molar mass and density
(`test_the_exhausted_total_in_millilitres_of_liquid_claims_no_more_than_in_litres`).
Another computes each agent's largest supported total and its SD from the stored
densities
(`test_the_delivered_total_in_millilitres_of_liquid_is_shown_in_whole_millilitres`).
A third computes the cost's and the price's precisions from the stored densities
(`test_the_cost_s_and_the_price_s_precisions_follow_from_the_density_and_the_cost`).
A fourth checks that the stored total is refused in liquid
(`test_a_unit_with_no_derived_precision_is_refused`). Whole millilitres replaced a tenth on
2026-11-04 (project owner, ratified, over keeping the tenth and over four
significant figures, `PL-SP6H`).
Each agent's file in `data/agents/` stores the density, with its SD and
measurement temperature, as `liquid_density`, and the molar mass as
`molar_mass_g_mol`. Each has a source entry (`sources`) that says why no tier-1
source (`docs/MODEL.md` § "Source hierarchy") exists. The vapour-to-liquid ratio is derived in
`core/liquid_agent.py` and checked against Biro's and Gas Man's constants in
`tests/reference/test_published_vapour_to_liquid.py`
(`test_the_derived_ratio_is_within_one_percent_of_biros_published_constant` and
`test_the_derived_ratio_is_within_half_a_percent_of_gas_mans_20_celsius_constant`).
The agent cost display reads the amount and the ratio from one snapshot of the
run (`SimulationSnapshot.agent_vapour_per_liquid`). A unit test fails if any
other code under `src/` calls the conversion to liquid (`liquid_volume_ml`).

One table in `app/formatting.py` gives the precision for
each amount and unit (`AGENT_AMOUNT_DISPLAY_PRECISION`). Each entry
(`AgentAmountPrecision`) holds the amount, the unit and the precision shown. It
reads the finest precision from the derivation for that amount and unit, so no
caller can pass a looser limit. It refuses a finer precision when it is built.
A precision that a reader could set would be built the same way. Concentration,
flow, MAC multiples and the F_A/F_I ratio are each shown in one unit, so each
keeps one precision. If a reader is ever given a choice of unit for one of
them, its precision moves into a table like the one for agent amounts.

#### A compartment's amount and share on the schematic

**A compartment's amount is shown to two significant figures, in millilitres of
vapour, because its uncertainty is a fraction of the amount rather than a fixed
volume** (runs of 2026-11-01). A positive amount that would round to 0.00 mL reads `<0.01 mL vapour`,
and exactly zero reads `0 mL vapour`.

**Relative to a compartment's amount, the shift from one SD of a partition
coefficient falls in a narrow range.** Runs of the simulator on 2026-11-01
changed each of the four stored partition coefficients in turn by one published
SD, at 1 MAC with the reference adult's flows. In venous blood and the three
tissue groups, one SD shifted the amount by 1.4% to 12%. In the circuit and the
alveoli the shift was less than 3%, because the dial sets them and a coefficient
barely moves them. With two significant figures, one step of the last digit is
1% to 10% of the amount. In the runs, that step lay between a tenth of one SD,
in desflurane's venous blood at 79 s when it held 0.99 mL, and many SDs in the
circuit. These figures have no test yet (`PL-19W8`).

**A compartment's share of the agent is shown in whole percent.** A positive
share below 0.5% reads `<1%`, so a compartment that holds agent never reads as
holding none. A share of 99.5% or more that is not the whole reads `>99%`, so no
compartment reads as holding all of the agent while another holds some. In a
desflurane run, the circuit holds more than 99.5% of the agent for about the
first second. One SD of a coefficient moves a compartment's share by at most 1.2
percentage points, in isoflurane's muscle at 24 h. This figure has no test yet
(`PL-19W8`). So one step of 1 percentage point lies between 0.8 SD and more than
a hundred SDs, and a step of 0.1 percentage point would be as fine as a twelfth
of one SD.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**For developers.** A compartment's amount needs a precision of its own. At the
run totals' 0.1 L, venous blood reads below resolution for a whole hour at 1 MAC
with every agent the simulator offers, and so do the alveoli with sevoflurane
and isoflurane. Desflurane's alveoli read 0.1 L from about two minutes. These
figures have no test yet (`PL-19W8`).

The readouts' uniform resolution does not carry over to the amounts either,
because neither of its two reasons applies to them. The uncertainty that the
parameters cause in an amount is relative, not absolute. And the amounts are not
a row read as one set. They are labels on separate containers, each followed by
its unit, and the schematic compares them on one scale, in the share bar.

No single number of decimals keeps every amount's step inside the band that the
readouts' derivation admits. The 2026-11-01 runs repeated the run totals'
derivation on each compartment's amount, reading it every second for the first
20 minutes, and at 60 min, 180 min and 24 h. The shift from one SD ran from
almost nothing, in the circuit in the first seconds, to 216 mL, in desflurane's
fat at 24 h, because the amounts themselves span that many orders of magnitude.
A step of 1 mL is a two-hundredth of one SD in desflurane's fat at 24 h, the
kind of false precision that stopped the run totals at 0.1 L. A step of 10 mL is
still a twenty-second of an SD there. It would also print sevoflurane's and
isoflurane's venous blood as "<10 mL" for almost the whole first hour, the flat
reading that the readouts' lower limit rules out. That blood holds about 0.18 mL
at 1 min, 6.6 mL of sevoflurane at 10 min, and 9.7 to 10.0 mL at 60 min.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- not-restated: 10 mL, 10.0 mL -->

Two significant figures were chosen because they are the finest precision that
the parameters support. Three would put one step at a hundredth of an SD. That
is finer than the readouts' third decimal, rejected at a seventieth of an SD,
and the run totals' second decimal, rejected at about a twentieth. One
significant figure would print fat's amount in steps of 1000 mL by 24 h. The
one-sided bound allows the coarse end of a two-figure step's range, many SDs in
the circuit. The fine end is finer than the readouts' seventh of an SD, but only
in the first two minutes, while venous blood fills. A test checks the two-figure rule
(`test_a_compartment_s_amount_is_shown_to_two_figures_and_no_finer_than_0_01_ml`).
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The 0.01 mL limit is a provisional choice made for legibility. A finer limit
would print four or more decimals for a moment's worth of agent. The limit can
only make an amount coarser than the two-figure rule would show it, which the
one-sided bound allows. A test checks the forms `<0.01 mL vapour` and `0 mL vapour`
(`test_a_compartment_s_amount_is_shown_to_two_figures_and_no_finer_than_0_01_ml`).

The formatting module (`app/formatting.py`) puts this section into code. It holds
the resolution as one constant, and derives from it the formatter, the
below-resolution marker, the MAC decimal count and the MAC axis placement. It
imports no toolkit, so the functions that this section reasons about can be read,
cited and tested without loading the interface. Its tests
(`tests/unit/test_formatting.py`) check the constant's value and every string
the formatter produces. The dashboard's tests (`tests/unit/test_dashboard_frame.py`)
follow the whole path: a real controller, a real step, and the string on the
panel. The dashboard (`app/dashboard_frame.py`) reads the constant to set the
delivered dial's slider position, so the value that the slider applies and the
readout beside it cannot drift apart. Another test
(`tests/reference/test_coupled_dynamics.py`) restates the constant and checks it
against the formatting module, because the ordering claim above is a property of
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
   0.24 MAC of desflurane. The instant is printed to the hundredth of a second, in
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
from one of three functions in `app/formatting.py`: `format_percent`,
`format_mac_multiple` and `format_elapsed`. The multiple divides by the snapshot's
own MAC (`mac_percent`). Any other divisor would bring the traceability failure that
`CLAUDE.md` forbids into the display that looks least like a calculation.

The qualifiers come first because of the general rule in
`.claude/rules/expert-review.md`: prefer an interface that prevents an error to one
that warns after it.

The instant that the box prints is exact, because the chart's columns fall on whole
hundredths of a second (`PL-T5NJ`) and every other drawn instant falls on a
simulation step. The box rounds each instant to a hundredth of a second
(`HOVER_INSTANT_RESOLUTION_S`), which removes only floating-point noise.

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
All along the time axis, a pointer within the radius of one run's fat trace is
within the radius of the other's too, even under the widest difference in
management that the interface permits.
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

The two runs' fat values can still differ. Take a sevoflurane case held at 1 MAC,
and call it the trunk. The branch is a second run forked from it at 10 min with
the vaporizer turned off. At 3492 s the fat value reads either `0.03%   0.02 ×MAC`
or `0.01%   <0.01 ×MAC`, depending on the run. That is a threefold difference in
stored agent, between a run still carrying agent and a run 48 minutes into
emergence. The slow compartments are the ones this chart exists to teach.

A single run goes unnamed because there is nothing to tell it apart from, and a
name would suggest a comparison that is not on screen. A reader always sees when
a second run is drawn, because it brings a second legend entry, a second readout
panel and a second set of traces.

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

The table gives the share of the axis on which both runs' points for one
compartment lie inside the hover radius. The figures come from simulating the
branched case on the reference adult on 2026-09-17, with the branch's management
at the fork varied. The 60-minute axis was 900 px wide and 360 px tall, a scale of
4.00 s and 0.0167% per pixel. The percent axis had its shipped top
(`CHART_AXIS_TOP_MAC`). At the time, the hover followed the nearest-point rule:
it reported the single drawn point nearest the pointer across every run
(`nearest_trace_point`).

| Branch's management at the fork | Alveolar | Fat |
| --- | ---: | ---: |
| doubled to 2 MAC | 1.6% | 100% |
| raised to 1.25 MAC | 8.5% | 100% |
| vaporizer turned off | 1.6% | 100% |

Of the hovers that could report either run, 83.3–95.3% would print different text
for the alveolar compartment and 43.8–81.4% for fat. Naming the run showed which
run the nearest-point rule chose, but did not make the box report the trace the
reader aimed at. Moving the pointer 2 px changed which run the box reported on
75.4–99.9% of the fat axis. § "Where more than one trace answers" gives the rule
that replaced the nearest-point rule (`PL-JVHL`).

#### Where more than one trace answers

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
Fat · Run 2 · 20m   0.01%  <0.01 ×MAC
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
run arrive and leave. In the cases examined below, the box held at most four
value lines on a two-run chart, and at most three on a single-run chart.

**The pointer's position along the time axis sets the instant reported, and the
hover radius decides only which traces are in reach** (`PL-1K9G`, 2026-09-22). The
chart draws each run as columns of points: one column every 4 s on a 60-minute
axis and every 48 s on a 12-hour axis, plus a column at each of that run's control
changes. A branch draws no columns before its fork. Each run is reported at its
drawn instant nearest the pointer in time, and a tie goes to the earlier instant.
Each of that run's compartments is reported if its point at that instant is
inside the radius, so every compartment of one run is reported at one instant.
Moving the pointer up or down can change what is in reach, but never the instant
printed. The wash-in plot follows the same rule.

Each value line prints its own instant, because two runs' nearest instants can
differ by up to one column, and the printed form shows the difference. One
instant above several values would claim that they are simultaneous when they may
not be.

**For developers.** Five targeting rules were scored on the branched case, with
alveolar and fat displayed, a pair that the limit on a two-run chart's
compartments allows (`COMPARED_COMPARTMENT_CAP`). The score is the share of hovers
whose reported run changed after a 2 px move, among hovers with both runs inside
the radius before and after the move. It counts hovers that could go either way,
so it cannot be compared with the 75.4–99.9% figure under
§ "The hover and the run it belongs to", which is a share of axis columns.

| Targeting rule | fat, 2 MAC | fat, 1.25 MAC | fat, vaporizer off |
| --- | ---: | ---: | ---: |
| the single globally nearest drawn point | 9.2% | 9.0% | 9.2% |
| nearest trace measured along its length | 9.2% | 9.0% | 9.2% |
| the pointer inside a run's own band, 2 px or 4 px | 9.2% | 9.0% | 9.2% |
| distance, near-ties broken toward the trunk | 0.0% | 0.0% | 0.0% |
| every run inside the radius is reported | 0.0% | 0.0% | 0.0% |

The first three rules score the same to the digit, for two reasons in this
chart's geometry. First, the trace is drawn at about one sample per 4 s against
a 12 px radius, so the pointer's distance to the polyline and to the nearest
vertex differ by a fraction of a pixel. Nearest along the length would differ
from nearest drawn point only on a sparse, steep trace. Second, both runs' fat
points lie inside the radius over 94.5–98.0% of the hoverable area, so a band
rule must break its tie by the nearest-point rule it was meant to replace,
exactly where the reported run flips.

Breaking near-ties toward the trunk scores 0.0%, as reporting every run does, but
was refused for its costs. A tie window keeps the boundary between the runs and
adds a second one, where the pointer leaves the window. Among axis columns with
both runs in reach on the alveolar trace of the 1.25 MAC case, it raises the share
on which the reported run flips from 58.5% to 98.4%. It also makes the branch's
value unreachable wherever the two runs' traces lie inside the window, which is
most of the fat trace. A value that a reader cannot reach is worse than one that
is hard to aim at.

Before every compartment in reach was reported (`PL-0RZ0`), the nearest drawn point
picked the compartment, on the reasoning that a reader aims at a trace. The
crowding near zero defeats that reasoning. Two or more compartments lie inside the
radius over 15.2–45.7% of the two-run chart's hoverable area, and over 37.0% of
the single-run chart's. Across pairs of pointer positions 2 px apart with more
than one compartment in reach, the compartment reported changed on 6.6–13.6% of
pairs. On 99.9% of those, the box printed a different number, by a median of
17.1–17.9× for muscle against fat. At a change, the two nearest points were a
median 0.9 px apart, and all were within 2 px.

| Chart | Compartments | Two or more in reach | 2 px flips the compartment |
| --- | --- | ---: | ---: |
| one run | all six | 37.0% | 12.7% |
| two runs, vaporizer off | muscle + fat | 45.7% | 7.5% |
| two runs, 1.25 MAC | muscle + fat | 19.1% | 9.2% |
| two runs, 1.25 MAC | mixed venous + vessel rich | 29.4% | 6.6% |
| two runs, 2 MAC | alveolar + fat | 0.5% | 13.6% |

The nearest-point rule never made a value unreachable, which matters because the
tie-break above was refused partly for doing so. Across the same cases, every
compartment was reported on 98% or more of the axis columns where it is drawn.
The worst was muscle on the single-run chart, unreported on 2.0% of its columns.
<!-- not-restated: 2.0 % -->

Reporting every trace in reach was affordable because the box stays short. One
compartment alone is in reach on 54.3–99.5% of hovers across these cases, and
63.0% on the single-run chart. The box carries one value line on 21–93% of hovers.

A logarithmic axis fixed from 0.001 to 3 MAC would put two runs' fat traces
23–75 px apart, but it has three costs. It draws below the 0.01-point resolution
of § "Displayed precision". It is a display mode on a chart of clinical values.
It would also arrive ahead of the v0.6.0 View contract, which decides where a
View's own settings live. Its strongest use, the washout tail, is a candidate for
the catalogue of views (planned-milestone item 36) rather than a mode on this
chart.
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

Before the pointer's time alone set the instant (`PL-1K9G`), each trace reported
its own drawn point nearest the pointer in both dimensions, so on a sloped trace
the pointer's height chose the column. The scan behind that change covered the
branched case, and a two-hour single run on its fitted 2-hour axis and on the
12-hour axis, where a dial change draws a near-vertical step. It tried every pixel
of height at four sub-pixel phases per column, and its selection was checked
against the shipped function before any number was kept. The whole scan is in
`PL-1K9G`.

| Chart | Boxes holding 2+ of one run's readings that mixed instants | Spread, median / max | A vertical 2 px move changed the instant / the printed value |
| --- | ---: | ---: | ---: |
| one run, 60 min | 70.1% | 16 s / 72 s | 44.9% / 35.1% |
| two runs, mixed venous + vessel-rich | 88.3–94.7% | 12–16 s / 32–52 s | 50.6–62.8% / 36.9–52.8% |
| two runs, muscle + fat | 13.0–16.8% | 4 s / 4 s | 3.0–5.4% / 0.3–0.8% |
| one run, 12 h axis | 84.5% | 288 s / 912 s | 37.3% / 33.3% |

<!-- not-restated: 13.0 -->

Mixed instants matter because adjacent columns often print different values. On
the 60-minute axis, the share of adjacent columns that differ is 44.0–93.3% on the
circuit, alveolar, mixed venous and vessel-rich traces, against 3.3–16.0% on
muscle and 0.7–1.3% on fat. Under the old rule, a sloped trace's nearest point
could lie as far to the side as the radius reaches, which is fifteen minutes on
the 12-hour axis.

The alternative to testing reach at the instant the pointer sets was to keep the
old reach and report the point at that instant. Like the chosen rule, that would
have made the instant depend on time alone, and it would have kept every value
that the old rule reported. But where the chosen rule reports nothing, the
alternative would have reported a point a median 13.5 px and up to 42.5 px from
the pointer on the 60-minute axis, and up to 146 px on the 12-hour axis. The dot
and the box would then hang on a value the reader is nowhere near.

The chosen rule's cost comes beside a steep segment, where a pointer level with a
point several columns along no longer reports that point. Even so, the chosen
rule keeps 84–100% of the area over which the old rule reported each trace on the
60-minute and 2-hour axes, and 45–54% for the four fast compartments on the
12-hour axis. It reports nothing the old rule did not, and leaves no drawn
instant unreachable.

On the wash-in plot, the old rule let 23.9–44.4% of vertical 2 px moves change a
box's instant. No box there mixed instants, because the plot draws one trace per
run. The plot treats a run's stretches as one set of drawn instants.

Two functions produce the forms above that list several runs or compartments
(`chart_frame.format_compared_trace_hover` and
`chart_frame.format_compared_wash_in_hover`), and their numbers come from
`app/formatting.py` like every other number in the box. Two more collect the
traces within reach at the instant that the pointer's time sets
(`nearest_trace_point` and `nearest_wash_in_point`), and the first of them skips
hidden compartments. The unit tests in `tests/unit/test_chart_frame.py` contain
both worked examples above verbatim. They also contain the fat and muscle cases
behind the decisions to report every run and every compartment in reach, and the
geometry behind the decision that the pointer's time alone sets the instant
(`test_every_compartment_of_one_run_answers_at_one_instant`).

#### Resolution: the readouts' derivation applies unchanged

The box prints a percent and a MAC multiple to two decimals each, or `<0.01%` and
`<0.01 ×MAC` below 0.01. § "Displayed precision" derives both forms for the
readout panel, and nothing in that derivation depends on where the number appears.
The derivation's upper limit on precision is one measured standard deviation of a
partition coefficient. A change that large shifts the modelled trajectory itself,
whatever display shows it. The lower limit is a teaching judgment about what a
reader can learn from the slow compartments.

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
(`LineChartDataPointTooltip`) by default, and this application never sets that label's
`text`. In pyqtgraph, a scatter plot (`pyqtgraph.ScatterPlotItem`) formats the label
of a hoverable point with a function (`tip`) whose default is
`'x: {x:.3g}\ny: {y:.3g}\ndata={data}'.format`. The table shows the drawn y at four
instants of the first hour in two ways: with `.3g`, as that scatter plot would apply it,
and with this application's percent formatter (`format_percent`). The values come from
a run on 2026-09-14 on the reference adult, with sevoflurane delivered at 0.02 (1 MAC)
and the shipped number of columns over a one-hour axis.

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

#### Which series answer a hover, and which do not

The six compartment traces respond to a hover in the form above, unless the
reader has hidden the compartment. The wash-in trace responds with a plain ratio,
because $`F_A/F_I`$ is dimensionless and has neither a percent nor a MAC reading:

```
Modelled sevoflurane · 20m8s
Wash-in F_A/F_I (alveolar / modelled circuit)
0.71
```

The caption in parentheses says that $`F_I`$ is the modelled circuit, not the
vaporizer dial.

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
comes from the wash-in module (`app/wash_in.py`). The caption uses a slash rather
than a division sign because every non-ASCII character that reaches a reader must
first have been rendered and seen (`tools/glyph_check.py`), and the division sign
has not been.

#### When it answers

The box appears whenever the pointer is over a trace, whether the run is playing
or paused. At high playback speed its value moves with the run, as every other
readout does. To study a value, pause the run. Moving the pointer off the plot
removes the box at once, so a value that moves with the run is always one that
the reader is pointing at.

**For developers.** The box is built on pyqtgraph and reports the drawn points
within the hover radius (`PL-G59B`, 2026-09-14). The code that shows it is in
`app/qt_chart.py`, and an integration test checks the rendered box against a real
run (`tests/integration/test_qt_chart.py`).

The Qt build must provide the hover, under the parity rule "Every capability the
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

Qt has no such cost by either route the box could be built on. One route drives a
crosshair from the scene's own mouse-move signal (`sigMouseMoved`), rate-limited
through a signal proxy (`SignalProxy`). The other gives each hoverable point a
callable (`tip`) that runs when the pointer arrives, with no tooltip object stored
for each point. Both cost work per pointer event, whatever the number of points
drawn.

Besides removing the box, leaving the plot discards any pointer move still waiting
to be handled. A box left at the last point the pointer crossed would recompute
its value every frame. While a run played, that value would climb with the run
like a live readout, for an instant that nobody is looking at (`PL-LTKL`).

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
   the press and is gone from the frame drawn at release.

**The preview comes from the same model and version as the run.** It starts from
the run's state at its current time, as § "The canonical evaluation rule"
defines that state. The value goes through the same checks as when it is
applied. A new cardiac output moves every tissue flow exactly as applying it
would. The same inputs always give the same preview. Computing a preview changes
nothing in the run. When the value under the handle is the setting already in
force, the preview matches what the run then draws, to within the computer's
rounding error. While the run plays, the preview is computed again on every
frame from the run's new current time.

**A drag applies its value only when the handle is released.** The run records
one setting change at that moment. Until then the run keeps the setting in force,
and the value printed beside the slider is that setting. The value is applied
before the preview ends, so the frame drawn at release already shows the run
under its new setting. A key press, one notch of the scroll wheel or a click on
the slider away from its handle is a single input, so it applies at once and
draws no preview.

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

**For developers.** The preview has a run definition of its own
(`SimulationController.preview_window`) and is evaluated on the same time grid as
the run. A branch is a run taken from another run. The preview's settings are
built the way a branch's are (`SimulationController.preview_settings`). A trial
run is rebuilt from the settings in force and checked to match the run in every
value. The trial run then takes the new value through the same setter that
applies a value to the run. The centred time window comes from
`chart_time_base.preview_window`, and the wording of the off-scale notice from
`dashboard_frame.PREVIEW_OFF_SCALE_NOTICE_TEMPLATE`.

The 2 px minimum width for a preview curve is there because an antialiased line
thinner than 2 px has less than 3:1 contrast against the panel
(§ "The six compartment traces: what separates them").

Neither dash pattern nor reduced opacity can mark a curve as predicted. The
muscle curve is already dotted, and drawing the run solid with a dotted preview
would flatten the five dashed curves into one style. At 0.85 opacity, the
alveolar and muscle curves fall to contrasts of 2.93 and 2.83 against the panel,
less than the 3:1 that WCAG success criterion 1.4.11 sets. At 0.75, four of the
six fall below 3:1.

The region's tint is decoration, as the MAC-awake band's is, because the
region's edge and the label carry the information. Its opacity is
`theme.PREVIEW_REGION_FILL_OPACITY`.

### A cost at the reader's price

The agent cost View shows what the delivered agent costs, at a price that the
reader sets in its form. The readout shows which part of the cost is the model's
and which part is the reader's (`PL-VJZK`). A price is neither modelled nor
measured, because the reader supplies it. Every other value the interface shows
today is modelled. A cost is a modelled amount times that price, so a wrong
price makes a correct amount lead to a wrong conclusion.

**The project ships no price.** Until the reader sets a price, the readout says
that no price is set, and it shows no cost. A shipped price goes stale, and it
differs from one institution to the next. Gas Man shows both problems. Its
default price for isoflurane is $20.47 for a 100 mL bottle (Philip JH,
*Workbook for Gas Man*, Appendix C, printed p. 171). The book calls its
defaults "USA bottle volume and bottle cost as of March 5, 2008" (printed
p. 105). Chapter 14 gives $78.00 per 100 mL bottle "on March 5, 2008" (printed
p. 141).

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
rounds isoflurane's vapour-to-liquid ratio to 196 (`docs/MODEL.md` § "Agent amount").

**The figures beside a cost are rounded, and the readout says so.** It also
says that the cost is computed from the unrounded liquid volume and price per
millilitre (`PL-1P15`). § "Agent amounts in millilitres, and the cost" sets the
precision of each figure. The liquid volume is shown in whole millilitres, so
the product of the figures shown can differ from the cost by more than one unit
of the cost's last digit. In the example above, 39 mL times USD 0.2047 is
USD 7.98. The cost is USD 8.07 because it uses the unrounded 39.42 mL. At
USD 115.13 per 240 mL bottle, 60 min of desflurane at 6 % and 1 L/min costs
USD 8.23. Shown as 17 mL and USD 0.4797 per mL, the two figures multiply to
USD 8.15.

<!-- not-restated: 6 % -->

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

**The simulator keeps at most one price for each agent, and the price records
five things:**

- the agent it prices;
- the price of one bottle, in the price's currency;
- the volume of that bottle, in millilitres of liquid agent;
- the currency, as its three-letter ISO 4217 code, such as `USD` or `EUR`;
  and
- the date on which the price applied, as an ISO 8601 calendar date, such as
  `2008-03-05`.

The form's date field writes dates this way and fills in the day of entry. The
reader should change it to the day the price was quoted, because a price goes
stale from that day, not from the day it was typed in.

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

**When no cost is shown.** The readout shows no cost, and says why, in each of
these four cases:

- no price is set for the agent;
- the stored price was refused when the simulator read its preferences file.
  No default replaces it, and the readout says that no valid price is set for
  the agent;
- the price per millilitre is not a positive finite number, or the cost is not
  finite, which extreme entries can cause, such as a bottle price of 10 to the
  power 308 for a 0.5 mL bottle; or
- the delivered amount cannot be converted to liquid (`docs/MODEL.md` § "Agent amount").

The readout never shows a cost of zero in place of one of these cases. Nor does
it show a cost left over from an earlier instant, another agent or an earlier
price. When the price changes, the readout redraws the cost at once, whether or
not the run is advancing.

**For developers.** The agent cost View and its form live in
`app/agent_cost.py` (`PL-1P15`). The preferences module in `app/preferences.py`
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
The cost's precision is not a fixed count of decimals, because how many decimals
a cost can justify depends on the price (§ "Displayed precision", `PL-0S0V`).

The two rows in the hazard table (`docs/MODEL.md` § "Reasonably foreseeable misuse, and the
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

**A container's fill height is the compartment's modelled tension, not an
amount.** All containers of one run fill against one scale: the concentration
chart's percent axis, from zero at the bottom to 3 MAC of the running agent at
the top. So a container filled to some share of its height shows the same
tension as a trace standing at that share of the chart's axis. A container is
much shorter than the chart's plot, so its fill level does not line up with the
chart's gridlines on screen. Each container therefore carries short marks at the
chart's gridlines, every 0.5 MAC, and the caption names that spacing
(`PL-8W1B`). A container that holds more agent can stand lower than one that
holds less. At 60 min in a run with sevoflurane at a 1 MAC dial, fat holds a fifth of
all the agent in the run, but its tension of 0.03% atm fills less than 1% of
its container's height (`ROADMAP.md` § "v0.7.0 - the schematic"). At a 1 MAC
dial, across the simulator's three agents, fat holds a fifth of the stored agent
at one hour and a third at three hours, which the chart's fat trace cannot show.
Every container is drawn at one width, so its filled area is not an amount
either.
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->
<!-- provenance: app/formatting.py CHART_GRID_INTERVAL_MAC = 0.5 -->

A tension above the top of the scale fills its container to the top, and the
schematic marks the container as off the scale. The concentration chart does
the same for a trace above its axis, in its off-scale notice. The container's
label still prints the tension. The circuit reaches 4 MAC, above the top, when
a sevoflurane dial is at its 8% maximum.
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
vapour (`docs/MODEL.md` § "Agent amount"). A vapour amount is written "mL vapour", as in
"38 mL vapour". A liquid amount is written "mL of liquid", as in
"4.2 mL of liquid". The model holds no liquid, so a liquid amount is worked
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
`docs/MODEL.md` § "Blood compartments"), so it gives arterial blood no volume, capacity or
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
the screen is next redrawn.

**Every height, amount and share on the schematic is a model output.** The
schematic therefore prints "Model outputs — not measurements." once, in its
own heading, as the readout section does. No amount is a prediction about a
patient to its last digit, for the reason § "Displayed precision" gives for
the readouts.

**For developers.** The schematic takes the top of its scale from the function
that sets the concentration chart's top (`chart_axis_top_percent`) and sets no
top of its own. The top's MAC multiple is a constant (`CHART_AXIS_TOP_MAC`), and
§ "MAC multiples as a display unit" gives the reason for 3 MAC.
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

The containers' common width is there because fat's container, drawn to scale,
would take about 500 px of a View 600 px wide, and four of the others would
take between 1 and 7 px each. The roadmap records the designs that the
schematic was chosen over (`ROADMAP.md` § "v0.7.0 - the schematic").

The run writes the schematic where it writes its readouts, from the same
snapshot of its state. Each amount comes from the snapshot's record for its
compartment (`PL-KFTM`), and that record is read from the amount of agent that
the model holds in the compartment (`agent_amount_l` in `core/`). The schematic
computes no amount of its own. The sum in the share formula is the snapshot's
total of stored agent (`stored_agent_l`).

Each spelling of an amount's unit is defined once, in `app/display_units.py`
(`DisplayUnit`). Whoever writes the first View to print a spelling adds it
there. Every View reads its spellings from that file and defines none of
its own.

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

