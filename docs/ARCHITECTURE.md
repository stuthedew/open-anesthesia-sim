# Architecture overview

This document describes how the code is organized and how data flows through
it. It is a map for contributors, not a scientific specification — for the
equations, units, parameter provenance, and numerical method, see
[`docs/MODEL.md`](MODEL.md). For version history and milestones, see
[`ROADMAP.md`](../ROADMAP.md). For where the interface's planned area and
workspace model comes from — what was studied of Blender, under what licence
rules, and what this project deliberately does differently — see
[`docs/interface-provenance.md`](interface-provenance.md).

## Layering

The codebase is split into three independent layers, enforced by import
direction (never edit around this — see `CLAUDE.md`):

```text
data/  --loaded by-->  core/  --read by-->  app/
```

- **`core/`** is the scientific simulation. It has no dependency on the UI
  toolkit, no wall-clock time, and no I/O beyond reading the packaged JSON files in
  `data/`. Every quantity it produces is deterministic for identical inputs.
- **`app/`** is the PySide6 user interface. It never performs a physiological or
  unit calculation itself — it only reads immutable snapshots from `core/`
  (through a thin controller) and renders them, and forwards user input back
  as setter calls.
- **`data/`** holds versioned, schema-validated parameter files (JSON) with
  citations, in three kinds — the agent, the patient, and the machine in front
  of them. Every scientific constant a shipped run uses comes from one of them:
  `AgentUptakeSystem.for_agent()` passes each value explicitly, so no
  compartment's field default is reached on a shipped path. The defaults are
  still written in `core/` for bare unit construction, and each is pinned by a
  test to the file that is its authority — `PL-4YY1` added the machine file and
  the first of those pins after finding that the circuit's volume and flow were
  reached from `core/circuit.py` and were therefore invisible to
  `tools/doc_check.py`'s provenance walk, which can only see a constant that
  entered a data file.

This mirrors the repository rules in `CLAUDE.md`: simulation code stays
independent of the toolkit, no simulation calculations belong in UI callbacks, and
model parameters live in validated, versioned data files rather than as
executable code.

## Package map

```text
src/anesthesia_sim/
├── app_metadata.py      # app name, bundle id, and the version the header shows: the installed distribution's version, plus the commit where the running code is not a clean checkout of the released tag, because between two releases every build otherwise displays the same string and a fix confirmed by eye cannot be told from the code it replaced
├── core/                # scientific simulation — no toolkit dependency
│   ├── validation.py              # shared input-validation guards (raise SimulationConfigurationError; a value that is not a number at all is a TypeError, as for every checked type)
│   ├── checked_number.py          # what a checked type, and the two sign-and-finiteness guards in validation.py, are built from: an int or a float and nothing else, never a value built as another checked quantity, with minus zero held as zero; the base every checked type shares; and how a refusal names a value
│   ├── concentration.py           # fraction vs percent: the two forms, and the only crossing
│   ├── units.py                   # seconds, minutes, hours, milliseconds: the factors between them, each written once
│   ├── supported_ranges.py        # the declared domain: FreshGasFlow, AlveolarVentilation and CardiacOutput, which cannot hold a flow outside it, CaseInstant, which cannot hold an instant outside the run length, StepCount, a whole nonnegative count, and the guards that refuse a run outside it
│   ├── simulation_step.py         # the run's step: its supported range, and SimulationStep, which cannot hold one outside it
│   ├── exceptions.py              # exception hierarchy; every core failure is inside it
│   ├── parameters.py              # load + validate agent/patient/machine JSON data
│   ├── circuit.py                 # breathing circuit compartment
│   ├── alveolar.py                # alveolar gas compartment
│   ├── blood.py                   # venous blood compartment
│   ├── tissue.py                  # one perfusion-limited tissue group
│   ├── patient.py                 # PatientCompartments: VRG + muscle + fat + venous blood
│   ├── governing_equations.py     # MODEL.md's balance equations as one system matrix
│   ├── matrix_exponential.py      # exp(A dt) for a compartment system; no physiology in it
│   ├── uptake_system.py      # couples circuit + alveoli + patient; advances one step
│   ├── run_definition.py               # a run as its settings over time; any state in closed form
│   ├── agent_simulation_validation.py  # mass-balance / agent-accounting tracker
│   └── simulation.py              # SimulationState: explicit elapsed time (bounded) + AgentUptakeSystem
├── app/                  # user interface - PySide6 and pyqtgraph since PL-25KS (ROADMAP.md § "Completed: v0.4.26 - the interface moves to Qt")
│   ├── controller.py               # SimulationController: run controls, read-only snapshots; ResumePoint and BranchedCase: where a branch opened, and the trunk it belongs to
│   ├── run_series.py               # the vocabulary a run's drawn values are addressed by, and the window one frame reads them from: RecordedQuantity, RecordedSeries, DrawnWindow; toolkit-independent
│   ├── control_record.py           # what a run's settings are addressed by and the change a run records: ControlInput, CONTROL_INPUT_UNITS, ControlChange; toolkit-independent
│   ├── bookmarks.py                # what a learner marks a case at, held in two collections: TimeBookmark (an instant), MacTarget (a height on one compartment), BookmarkSet; toolkit-independent, and it detects a crossing between two readings it is handed, which SimulationController.advance supplies each step
│   ├── simulation_view.py          # SimulationView on PySide6: what runs share - the charts, the legend, the time base, the captions, the wash-in section, the render tick, the splitter layout; no domain logic
│   ├── run_view.py                 # one run's widgets, controller, handlers, refresh and halt; RunView, instantiated once per run (the seam PL-B9PY drew)
│   ├── qt_widgets.py               # PySide6 leaf widgets that decide nothing: MetricPanel, ReadoutRow, ParameterSlider, NoticeLabel, NewCaseDialog, BookmarksPanel, ForkPanel, inert_splitter, initial_window_geometry
│   ├── formatting.py               # modeled value -> displayed string; toolkit-independent
│   ├── playback.py                 # playback rate -> whole simulation steps per tick; toolkit-independent
│   ├── dashboard_frame.py          # what the dashboard claims about one run at one instant, as plain values: the status word, the notice and its precedence, the readouts and their glosses, the setting controls, the transport enablement, the accounting panel, the control-change list, the captions and the new-case question; toolkit-independent
│   ├── chart_frame.py              # what one frame of both plots draws, as plain values: the trace table, the window, the axes' ticks, the references, the marks, the wash-in stretches and the hover text; toolkit-independent
│   ├── qt_chart.py                 # the concentration chart, the wash-in plot and the legend on pyqtgraph, moved per frame to match a chart_frame.ChartFrame; declares no colour and formats no value
│   ├── chart_time_base.py          # how wide the chart's window is and how it is ruled; toolkit-independent
│   ├── control_timeline.py         # recorded control changes -> the acts a reader sees; toolkit-independent
│   ├── wash_in.py                  # F_A/F_I and the domain it holds on; toolkit-independent
│   ├── theme.py                    # every display token: palette, cited ISO 5360 agent colors, type sizes, spacing, dash patterns; toolkit-independent
│   └── main.py                     # PySide6 entry point; builds the BranchedCase and opens the dashboard over its trunk; the window opens maximized (PL-Z4K6) over a sized, centred normal geometry (PL-005)
└── data/                 # versioned, cited parameter files
    ├── agents/{sevoflurane,isoflurane,desflurane}.json
    ├── machines/reference_circle_system.json
    └── patients/reference_adult.json
```

## Data flow

**Startup / parameter loading:**

```text
data/agents/sevoflurane.json                ──┐
data/patients/reference_adult.json          ──┤
data/machines/reference_circle_system.json  ──┴─> core/parameters.py
                                        (parse + validate schema, units, ranges)
                                        │
                                        ▼
                          AgentUptakeSystem.default()
                          (circuit + alveoli + patient compartments)
                                        │
                                        ▼
                              SimulationState (adds elapsed_s)
                                        │
                                        ▼
                            app/controller.SimulationController
```

`core/parameters.py` is the only module that reads the JSON files (via
`importlib.resources`), and it validates schema version, required fields,
units, and ranges before constructing `AgentParameters` /
`ReferenceAdultParameters` / `BreathingCircuitParameters`. The schemas are
strict at every nesting level:
a key the schema does not declare fails the load rather than being silently
discarded, so a data file cannot document one model while the app runs
another. Nothing downstream re-reads or re-derives these values from disk.

**Each simulation step**, `AgentUptakeSystem.advance()` advances the whole
coupled system at once, by one exact propagation rather than by a sequence of
sub-exchanges or a generic numerical integrator:

1. `core/governing_equations.py` assembles the system matrix `A` — every entry
   one term of one balance equation in `docs/MODEL.md`, "Governing equations";
2. `core/matrix_exponential.py` computes `exp(A dt)`, which is the system's
   exact propagator because every setting is held constant across a step. It
   is cached against the settings it was built for and rebuilt when one moves;
3. one matrix-vector product advances the six fractions and, in the same
   solution, the cumulative delivered and exhausted amounts;
4. the agent-accounting validator records those amounts and checks mass
   balance (`AgentSimulationValidator`), raising
   `AgentSimulationValidationError` if it fails.

Steps 1 and 2 carry the split of concerns the package is arranged around: the
equations file holds the physiology and no arithmetic, the exponential file
holds the arithmetic and no physiology.

**UI direction:** `app/controller.py`'s `SimulationController` owns a
`SimulationState`, exposes `start()` / `pause()` / `reset()` / per-parameter
setters, and produces an immutable `SimulationSnapshot` on request. It holds
no default values and no bounds of its own: every unspecified setting comes
from what `AgentUptakeSystem.for_agent()` built from the data files, and a
setting the core rejects — a delivered concentration above the agent's
vaporizer maximum, say — raises out of the core rather than being clamped or
defaulted at this boundary. Conservation is core's on the same terms: until
PL-006 the controller read the circuit's stored agent out and put it back
around `set_circuit_volume`, which left `core/` exposing an unconserving
primitive publicly and the invariant holding only for the caller that knew
to compensate. The core setter conserves, and the controller calls it once,
from `_build_state()`, to apply the volume the session was built with.
There is no live setter above it: PL-GYH2 established the circuit volume as
a fixed model parameter rather than a control, so the per-parameter setters
named above are the four the interface offers and no fifth exists.
`docs/MODEL.md` § "What is not bounded this way" carries the argument. The
snapshot is the run's state at one instant: a fixed number of values,
however long the run has been going. The run itself is answered for
separately, by `drawn_window(start_s, stop_s, columns)`, which evaluates the
states at the instants a chart is about to plot across the axis the caller
names and returns them as a `DrawnWindow`. The two were one field until
PL-0VM7: the snapshot carried every sample the run had then recorded, so a
frame's cost grew with the length of the run while the chart discarded all
but the few hundred inside its axis; PL-2FM6 later removed the record itself.
The snapshot does carry the run's `ControlChange` timeline — one entry
per setting the model was actually stepped under, so re-applying the
timeline reproduces the run rather than approximating it, and a timeline is
bounded by how often a user touches a control rather than by how long they
watch.

**A run is its inputs, and its states are derived from them** (PL-T691).
The controller holds the run as a `core/run_definition.py`
`RunDefinition`: the settings in force at each moment, plus one keyframe — the
state at that instant — per change, and nothing else of the run. (The chart's
read keeps the propagators its last window used, for the next frame to reuse,
but each is a function of settings the definition already holds, so no drawn
value depends on whether it was kept: `RunDefinition.evaluate_anchored`,
PL-CNCF.) Because the equations
are linear and time-invariant while the settings hold, the propagator is exact
over any horizon and not only over a step, so every state the run passed
through is one propagation from the keyframe bracketing it and none of them
has to have been recorded. `RunDefinition.evaluate(start_s, stop_s, columns)`
and `evaluate_anchored(start_s, stop_s, spacing_s)` are that read — the second
is the chart's, reached through `SimulationController.drawn_window` — and
`run_segments` hands the record itself out as frozen segments — readable
without being advanceable, so nothing above the controller can move the
run definition's reach past where the run actually got to and have a prediction
come
back drawn on the run's own axis. `docs/MODEL.md` § "The run is that record,
and every state is derived from it" carries the measurements, and § "The
canonical evaluation rule" states which of the two evaluation paths a stored,
exported, replayed or branched value may be taken from.

**That boundary is a type rather than a convention.** `evaluate` and
`evaluate_anchored` hand back `DisplayState` values, which are not state
vectors, so a drawn column cannot become a keyframe, an exported figure or a
branch's opening state by being the same nine numbers in the same order;
`RunDefinition` refuses one as an
opening state by name. A layer above the controller therefore cannot cross
that boundary by forgetting it is there, which is the only way a boundary
stated in prose is ever crossed.

There is one record. Until PL-2FM6 landed in v0.4.12 the controller kept a
per-step sample history beside the definition and the chart drew from it,
with `docs/MODEL.md` § "Closed-form agreement test" holding the two to each
other; that change deleted the history, because the run definition is the run
and the samples were a second copy of it. What the chart draws now is what
`drawn_window` evaluates, and nothing exists behind those states to disagree
with them.
`app/run_view.py` and `app/simulation_view.py` read only those two — a
`RunView` builds one run's controls and wires slider/button callbacks through
`_apply_setting` to controller setters, and the `SimulationView` drives the
charts every run shares. Neither performs a physiological or unit calculation
of its own. The transformations they do apply are each their own module,
because each is a presentation-*correctness* question rather than a layout
one and each must be readable and testable with no toolkit loaded:
`app/formatting.py` turns a fraction into the strings a reader sees — a
percent and a multiple of the running agent's 1 MAC — at the resolutions
`docs/MODEL.md` § "Displayed precision" derives, `app/chart_frame.py` settles
what one frame of the chart claims - which compartment a curve carries, which
instants are drawn, where the references stand, what a hover says - as plain
values, and `app/qt_chart.py` moves pyqtgraph items to match it;
`app/dashboard_frame.py` does the same for everything beside the plots - the
status word, the notice and its precedence, the readouts, the setting
controls, the captions, the two bookmark listings - and `app/qt_widgets.py`
moves the leaf widgets to match it, deciding nothing; `app/control_timeline.py` turns the recorded
control changes into the adjustments a reader sees, `app/playback.py` turns the playback rate a
reader selects into the number of whole simulation steps a tick takes, and
`app/wash_in.py` divides the alveolar fraction by the inspired one. The last
three are correctness questions for reasons worth stating. The control record is faithful to the run and a drag
of one slider is several settings in it, so the collapse into one displayed
act is a claim about what the user did rather than a tidier rendering of
what the model saw. And the wash-in quotient has a domain: it is undefined
before any agent reaches the circuit and stops being a wash-in fraction
above 1, so the module returns the value and the reason together and the
chart draws the trace in segments that break where the domain does —
`docs/MODEL.md` § "F_A/F_I as a displayed ratio" is the specification. And a
playback rate is realised only as a step *count*, never as a larger step, so
the module derives the count from the rate and refuses a rate that does not
land on a whole number of steps: the alternative is a run advancing at a rate
other than the one it displays, which is a presentation failure that looks
like a working feature. The MAC divisor reaches the formatter as an argument, from
`SimulationSnapshot.agent_mac_percent`, rather than being looked up: it is
what makes a displayed multiple agent-specific, so it travels with the value
it divides. The agent's MAC-awake travels the same way and for the same
reason, as `SimulationSnapshot.agent_mac_awake` beside that divisor, because
the chart's MAC-awake band is the one multiplied by the other and pairing
two agents' values would place a correct number at the wrong height. A
reference is placed by `app/chart_frame.py` and drawn by `app/qt_chart.py`
but is deliberately not a member of `chart_frame.COMPARTMENT_TRACES`, the
trace-to-compartment table: it reads no state of the run.
A control mark is a third kind of series on the same terms and for a
stronger version of the reason — it draws no value at all, only a simulated
time — and it is likewise outside that table.

**Failure direction:** every failure `core/` reports is a subclass of
`AnesthesiaSimulationError` (`core/exceptions.py`), never a bare
`ValueError`, so the interface can recognise a simulation failure and act
on it. The hierarchy's two branches mean different things and get
different treatment:

- `SimulationConfigurationError` — a value was rejected before it changed
  anything. Raised by the guards in `core/validation.py`, by the checked
  types' constructors (`Fraction` and `Percent` in `core/concentration.py`,
  and those in `core/supported_ranges.py` and `core/simulation_step.py`), by
  compartment constructors and setters, and by the parameter-file loaders.
  The view's `_apply_setting` catches it, restores the control from the
  snapshot, and says the setting was refused; the run is untouched and keeps
  going. A setter, or a compartment's flow field written directly, handed a
  value not built as its type raises `TypeError` instead, a programming error
  rather than a refused setting; so does a checked type built from what it is
  not built from - a `bool`, a `Decimal` or a string for any of them, a
  `float` for `StepCount`, which is built from an `int` alone, or a value
  already built as another checked quantity, for all of them - before its
  range is read (`core/checked_number.py`), and so do the two
  sign-and-finiteness guards in `core/validation.py`, which also refuse an
  `int` past the float range by name rather than letting `math.isfinite`
  raise `OverflowError` converting it (`PL-3800`). A
  concentration the display builds is not a setting, and one refused there
  halts the run; no supported setting makes one refuse (`PL-7DJK`).
- `SimulationExecutionError` (and its `SimulationNumericalError` /
  `AgentSimulationValidationError` subclasses) — a step began and could
  not be completed, so the run must stop.
  `AgentUptakeSystem.advance()` is what makes this distinction: it checks
  its own arguments first, then restates any guard reached during the step
  as a `SimulationNumericalError`, keeping the original as `__cause__`.
  It is also what makes the step atomic — it captures every dynamic value
  before the step and restores it on any failure, so what is left behind is
  the last completed step rather than a state vector written into some
  compartments and not others.
  Each compartment captures its own state (`capture_state()` /
  `restore_state()`), so a dynamic field added without a matching capture
  is a local omission; `docs/MODEL.md`, "Step atomicity", is the contract.

Both timer slots are guarded — `RunView.step_tick` steps the run and
`SimulationView.render_tick` presents it — and both halt the run on any
exception, because a `TypeError` from a refactor is exactly as silent inside a
Qt slot as a modelling failure is. Which halt is `dashboard_frame.halt_disposition`'s
call, and `RunView.halt` routes by it: through `SimulationController.fail()`
for a failure, through `halt_at_supported_limit()` for a
`SimulationDomainLimitError` raised on a path the controller does not step
itself, such as a setting. A run stepping onto the supported run length meets
no raise: `SimulationController.advance()` halts it on the arriving step, and
the snapshot reads the limit from the run's own state, so a run forked or
reset onto that step reads as stopped there too (`PL-5291`). `fail()` is a
third run state, carried
on the snapshot as `failure_reason` and rendered as "Stopped — simulation
error" with a banner over the values: a halted run must never present as a
pause, because a pause is a run that continues when asked and a halt is one
that cannot. Both halts are read off `SimulationController.status()` as a
`RunStatus`, which the snapshot extends, so `RunView.present_halt` states a
halt without building any compartment value - the snapshot's own `Fraction`s
being among the values a halt can be for - and the banner it writes,
`dashboard_frame.halt_notice`, says no frame of the stopped run has been drawn
until `refresh` replaces it on the first frame that draws (`PL-7DJK`). The
supported-limit halt is a fourth, distinct from the failure —
`supported_limit_reason` on the snapshot, "Stopped — supported run length reached"
in place of the failure word — because there nothing went wrong: the run
stands on a completed step at a time the model claims to represent, and the
next step would be refused identically. Neither can be resumed, only cleared
by `reset()` or by starting a fresh run with `set_agent()` - and `reset()`
can itself refuse, for a settings record the definition cannot open on, which
it does before it clears anything; `RunView._handle_reset` halts the run on
that refusal through the same path, the banner naming a new case as the way
out, since Reset is the door it names otherwise (`PL-M4M0`). Neither timer
stops on either halt — both are started once, when the window opens, and a
halted run leaves them firing and finding nothing to do — so a run reset and
started again is stepped without anything having to be restarted.

Drawing that full record every frame is what made the render payload grow
with run length. The run no longer keeps a record to draw: `core/run_definition.py`
answers the state at any instant in closed form, so the view asks the
controller for the states at the instants it is about to plot
(`SimulationController.drawn_window`) and there is nothing to subset. Which
instants those are is a presentation-correctness concern — a chart that
stepped over a control change would show a curve the simulation never
produced — so the rules that place them are stated in `docs/MODEL.md` § "What
the chart draws" and tested on their own. The evaluated instants are anchored
to an absolute grid measured from the case's zero rather than to position
within the window, so a window following the run keeps every column it had
and gains at most one (`RunDefinition.evaluate_anchored`; PL-Q197 established
the rule over recorded samples, when the Flet client was patched per point
and every shifted column was a changed point, and PL-2FM6 carried it over to
evaluated columns). `app/chart_frame.py` is the layer above it — it holds the
column-per-pixel rule and its floor (`chart_columns`), reads the window once
per run for every trace, and converts each drawn value into its own axis's
unit — and it is separate for the same reason: which quantity a line carries
is a correctness claim, declared once in `chart_frame.COMPARTMENT_TRACES`
beside the traces themselves. The unit conversion belongs to the layer that
knows the axis: the six compartment traces are drawn in percent and the
wash-in ratio in its own dimensionless unit. Stepping and drawing also run on
separate timers on separate intervals, so simulation time stays a function of
steps taken rather than of how long a frame took.

## What a branch is, and what it shares with its parent

A **branch** is a second live run of the same case, opened at a state the
first run passed through. The run it was taken from is the **trunk**. One
trunk with N branches is the whole of the structure — sub-forks of forks are
excluded rather than unimplemented (project owner, 2026-08-25): they multiply
without bound and buy little over branching from the trunk again.

This is the object map. What a branch *guarantees* — that its run definition
opens at a keyframe of the case and why, that it opens at that keyframe's own
case instant so no clock is re-based and no conversion is performed, and what
both are worth in floating point — is `docs/MODEL.md` § "The canonical
evaluation rule", which is the one place those are stated and measured. Which
keyframe, and how it relates to the instant the branch itself began at, is the
same section's "What this requires of a branch".

Four things in `app/controller.py` carry it:

- `SimulationController.resumed_at(elapsed_s)` makes one. It builds a second
  controller through the ordinary constructor, replays the trunk's settings
  from the recorded control timeline into it, seeds its system with the
  trunk's canonical state at `elapsed_s`, and hands it back paused. The trunk
  is read and never written, so the two runs share no compartment, no
  accounting and no clock — which is what lets both be advanced.
- `SimulationController.resumed_at_halt()` makes one at the bookmark crossing
  the trunk is standing on. What a branch *is* is the bullet above — the two
  share `_branch_from` — and what differs is only where the fork may be
  taken. It takes no instant, deliberately: the fork is the halt, so there is
  no float for a caller to name a mark the run has not reached with, and no
  way to confuse the instant a learner *marked* with the step instant the run
  actually stopped on.
- `ResumePoint` is where the branch came from: the trunk stretch it opened
  inside, the fork — the instant it was taken at and the canonical state
  there — the case's step count at the fork, the step it was taken at, the
  agent its accounting period started from, and the marked crossing it was
  forked at, which is `None` for a fork at a control event. `opened_from` is
  `None` on a trunk and this on a branch, so every run knows which it is. The
  stretch's opening and the fork are one instant for a fork at a control event
  and two for a fork at a bookmark, which is the whole of what `PL-B8MK`
  changed. The crossing is carried here rather than read from the trunk so
  that a reset seeds from the same value a fork did — `reset()` goes back
  through the same `_open_at`, and a branch that lost its crossing there would
  stand on its own fork reporting that it had crossed nothing (`PL-3K9B`).
- `BranchedCase` holds a trunk and the branches taken from it. It is what
  makes two controllers one case rather than two unrelated sessions, and it
  is where the flat shape stops being a refusal: the trunk is the only run it
  will fork, so a sub-fork is not an operation it can express. `resumed_at`
  keeps its own refusal for the caller that holds a branch directly.

**What a branch inherits, and why each is not re-chosen.** The agent and the
patient, because changing either makes it a second case rather than a second
management of this one — `set_agent` already starts a new run for that reason,
and refuses outright on a branch. The circuit volume, applied before any state
is, because `BreathingCircuit.set_circuit_volume` conserves agent by rewriting
the inspired fraction and a volume set afterwards would move the branch off the
state it opened at. The four live controls, replayed from the recorded timeline
in the units the compartments hold. The rebuilt branch is then checked against
the trunk rather than trusted — the settings the trunk's own stretch carries,
and the agent's displayed references, since the agent and patient are re-read
from their data files — and a refusal names each value that differs, with both
of its values (`PL-NC62`). And the bookmarks, which is
the opposite case to the timeline below and settles by the same test: a mark is
a question about what is still to come, and a comparison is two managements
answering one question, so a learner made to re-enter the marks could compare
two branches at two different heights with nothing saying so. What it does not
inherit is the trunk's control timeline, which starts empty: the branch's
record is of what the learner does to *it*, and `opened_from` is what records
where the fork was taken. `began_at_s` is the one number to read for it — zero
on a trunk, the fork instant on a branch. The definition's own first segment
used to stand at the same instant and no longer always does, which is why that
property exists rather than the inference (`PL-B8MK`).

**One time frame, and every reader is in it.** A branch continues the case's
step count, so `snapshot().elapsed_s`, every control-change stamp,
`drawn_window`'s instants *and* the instants `run_segments` hands out are all
case time. Its `RunDefinition` opens at a keyframe of the case rather than at
a zero of its own, so a keyframe read from a branch needs no conversion to be
placed on the case's axis and no reader has to know which kind of run it is
holding. *Which* keyframe is the fork's own question: the fork itself for a
branch taken at a control event, and the keyframe at or before it for one
taken at a bookmark.

Until 2026-09-14 there were two frames and a `SimulationController.origin_s`
holding the difference, which `advance` and `drawn_window` subtracted and
`run_segments` warned about. `PL-ZMRT` (project owner, 2026-09-14) removed the
second frame: `origin_s` and both subtractions are gone, and `PL-2R2C` — a
branch's drawn columns anchored to its own zero, landing at case instants the
trunk never draws — was dissolved by it rather than fixed separately.
`docs/MODEL.md` § "The canonical evaluation rule" measures what that is worth.

**Where a branch may be taken.** Two places, reached by two methods rather
than by one list.

At any keyframe the trunk holds — `BranchedCase.fork_points_s`, taken with
`fork_at` — which is its opening at induction and every setting change the
model was actually stepped under. Any *other* instant a caller names is
refused rather than approximated, for the arithmetic reason `docs/MODEL.md`
measures. `tests/unit/test_run_definition.py` holds the other side of that
refusal: that a branch opened off a keyframe really does stop reproducing the
run it claims to continue, rather than the refusal guarding against nothing.

And at the **bookmark crossing the trunk is standing on**, taken with
`fork_at_halt`. `app/bookmarks.py` is what a learner may mark (`PL-LPLD`), and
`SimulationController.advance` is what halts a run on the step crossing one
(`PL-CTD7`): it reads every compartment either side of each step and pauses
the run where a mark lies between the two readings. A bookmark's instant is
not in general a setting change — on a 120 s run with two control changes, 3
of the 1 201 instants a halt could land on are keyframes — so the trunk holds
no keyframe there, and nothing records one. The branch's *definition* opens at
the keyframe at or before the bookmark while its clock and its live system
stand at the bookmark, which costs the trunk nothing and reproduces it
element-wise. The obvious route was measured and refused: recording a keyframe
where the run halts makes the branch exact against the trunk it forked from,
and it moves that trunk's own later answers away from what the case would have
said unmarked, so marking a run would change it. `PL-B8MK` carries both
measurements, and `docs/MODEL.md` § "What this requires of a branch" records
which of that section's two conditions the chosen route relaxes and what the
relaxation costs.

The halt is a permission rather than a standing offer: taking a step clears
it, so a run that has resumed has no bookmark fork until the next crossing.
That is why it is not a widened `fork_points_s` — such a list would change
membership as the run moved, and a caller holding an instant from it could ask
for a fork at a mark the run is no longer standing on.

### How a learner takes one, and how a comparison ends

`app/main.py` builds the `BranchedCase` and opens the dashboard over its
trunk, so the application is a *case* from its first frame rather than a run
that might later be made into one (`PL-VKJW`). Three things follow, and each
is a property of the display rather than of the model:

- **The branch control is the case's**, so it stands beside the bookmark
  panel in `SimulationView` rather than in either `RunView`. It offers
  `BranchedCase.fork_points_s` and takes the branch through `fork_at`;
  `dashboard_frame.fork_offer` decides what it shows and
  `qt_widgets.ForkPanel` draws it. A learner marks the decision point and
  then forks there, which is the order the two panels are read in.
- **Two controls, because the two doors to a fork have different lifetimes**
  (`PL-TYWQ`). The selector offers `BranchedCase.fork_points_s` and takes the
  branch through `fork_at`. Below it, a second button takes the branch at the
  bookmark crossing the trunk is standing on, through `fork_at_halt`, and is
  on the panel only while it is standing on one — labelled with the instant
  the branch will open at and that the trunk stopped there on a mark. A
  bookmark records no keyframe, so the halt adds nothing to `fork_points_s`
  and the selector's membership never changes as the run moves. Shape chosen
  by the project owner (2026-09-21, ratified, over one list that grows a row
  while the run is halted): a vanishing list row is detectable only against a
  remembered list, which is the stale-state case
  `.claude/rules/expert-review.md` names, where a vanishing control is
  detectable on sight. The button names no instant to `fork_at_halt`, which
  takes none — so the hazard that method exists to prevent, a fork asked for
  at the instant a learner *marked* rather than the step the run stopped on,
  is not expressible through the interface either. `fork_offer` reads the
  halt from the **trunk** rather than from the displayed runs, because
  `fork_at_halt` forks the trunk and refuses a branch: a panel drawn from a
  branch's halt would offer a fork the case cannot take.
- **`SimulationView.add_run` is how a run reaches the dashboard after
  construction.** Its run set was fixed at construction until `PL-VKJW` —
  "the count cannot change while a dashboard is alive" — so a branch taken
  during a session had nowhere to be drawn. Both legends' run counts, the
  names the runs carry, the splitter sections and the agent locks are now
  written from the run set on every change to it. The cap is still
  `MAX_DISPLAYED_RUNS`, which is two.
- **One comparison at a time, and Reset is the way out.** There is no run
  selector — `ROADMAP.md` § "Explicitly out of scope for v0.5.0" defers it —
  so a second branch could only replace the displayed one while the first
  went on living inside `BranchedCase`. The control is refused while two runs
  are shown, visibly and with the reason readable. Resetting the *trunk*
  takes every branch off the dashboard and rebuilds the case on the restarted
  run, because a trunk that has started over never passed through the instant
  a branch was taken at; resetting a *branch* returns it to its own fork and
  leaves the comparison standing. **The lock says which of those two Resets
  it means, in the words the screen carries** (`PL-WG73`).
  `comparing_fork_lock_text` fills its sentence from `run_label` and
  `RESET_LABEL`, so an instruction cannot name a control that is not there:
  the sentence it replaced sent a learner to "Reset the case", and the Reset
  they reach for is the branch's - the run they are trying to end, which that
  press returns to its fork while the lock stays exactly where it was.

**No agent may be chosen while two runs are shown** (`PL-QRD1`). A branch's
`set_agent` refuses outright, so its `RunView` shows the agent chip in place
of the selector. The trunk's `set_agent` *succeeds*, which is the worse case:
the switch restarted the trunk, `BranchedCase` went on listing a branch of a
run that no longer existed, and `assemble_chart_frame` then refused the frame
over the shared MAC axis — so `_halt_every_run` failed both runs over an
input to one of them. The trunk's selector is therefore locked while a
comparison is shown too (project owner, 2026-09-20, ratified, over keeping the
selector live and growing `RunView._confirm_new_case`'s dialog a clause about
the branches it would orphan), which is `.claude/rules/expert-review.md`'s
preference for an interface that prevents the error over one that reports it
afterwards. Ratified rather than specified: the case put to the owner was a
session's own recommendation, so ordinary evidence — a learner who wants to
change agent mid-comparison, a measurement, a cost the case did not carry —
is enough to put it back to them. `dashboard_frame.transport` carries all three locks and names the
longest-lasting one that holds, so the chip never sends a reader to Pause for
a lock Pause cannot lift.

### What a branch comparison asserts, and which part of it is structural

**The full statement is `docs/MODEL.md` § "What a branch comparison asserts,
and what it does not", and it is stated there because it is a claim about the
model rather than about the object map.** What belongs here is the part the
structure above decides, which is three things.

**The comparison is a trunk and one branch of it, and the shape is what says
so.** `BranchedCase` forks only its trunk, so a branch of a branch is not an
operation it can express, and `MAX_DISPLAYED_RUNS` is two with no run
selector — so what is on screen is always one case managed two ways, never a
survey of N managements and never one branch read against another. A reader
generalising the drawing into a wider facility is generalising past what the
structure can build.

**What may be attributed to the settings that differ is exactly the
complement of what a branch inherits.** The agent, the patient, the circuit
volume, the four live controls up to the fork and the bookmarks are carried
across and then held — `set_agent` refuses on a branch and is locked on the
trunk while two runs are shown — and the control timeline is the one thing
that starts empty. So the difference between two runs past the fork is the
difference between two control timelines, and the inheritance list above is
the audit of that claim rather than a convenience.

**The shared history is the same object, not a reproduction of one.** A
branch's definition carries the trunk's own keyframe and both runs stand in
the case's one time frame, so agreement before the fork follows from
construction rather than from a tolerance being met; `docs/MODEL.md` § "What
this requires of a branch" is where that is stated and measured, and the
residual it leaves is zero. What the structure does *not* supply is any bound
on what happens after the fork, and neither run is a prediction for a patient
at any point: the model holds one reference adult and no variability around
it, so a difference between two branches is a property of the model rather
than an expected clinical difference. That last clause is the one a reader of
a drawn comparison is likeliest to need, and `docs/MODEL.md` § "What a branch
comparison asserts, and what it does not" is where it is argued.

## Data files (`data/`)

Each JSON file carries a `schema_version`, an `id`, the parameter values, and
a `sources` array of citations (`citation`, `url`, `tier`, `adopted`,
`authority_for`, `note` per entry — see `core.parameters.SourceReference`).
`tier` is drawn from the closed vocabulary `core.parameters.SOURCE_TIERS`,
which is the three tiers `docs/MODEL.md` § "Source hierarchy" defines. `adopted`
says whether the file names that source as the authority for a value it
stores, which is a separate question from what tier the source is.
`authority_for` names which stored values, by the dotted key path the
provenance table uses, and is empty exactly when `adopted` is false. A file
that adopts no primary source at all carries a top-level `provenance_gap`
saying so. `python3 tools/source_tier_counts.py` reads `authority_for` and
prints the source and tier behind every stored value, file by file and in
total. It gates nothing, by the project owner's decision recorded on
`PL-9LXK`: it prints the counts `docs/MODEL.md` states and never checks them.
`core/parameters.py` rejects a file that
is missing required fields, uses an unsupported schema version, declares a
tier outside the vocabulary or an `adopted` flag that is not a JSON boolean,
declares an `authority_for` that disagrees with `adopted`, names something
that is not one of the file's stored values or names a stored value twice,
contains a
value outside its validated range (e.g. non-positive volumes, tissue
perfusion fractions that don't sum to 1), or carries a key the schema does
not declare — including inside a nested object such as
`tissue_gas_partition_coefficients` or one `sources` entry. Adding a new agent, patient
or machine profile means adding a new validated, cited JSON file plus any new
parsing support in `parameters.py` — not adding constants directly to `core/`.

The three kinds answer three different questions and a value belongs to
exactly one of them: `data/agents/` is what the drug does, `data/patients/` is
who is being anesthetized, and `data/machines/` is the apparatus delivering
it — the
breathing system's volume and the default fresh gas flow. Filing a machine
parameter under the patient would say something false about where it came
from, which is why `PL-4YY1` added a third directory rather than a field to
`reference_adult.json`.

## Dependencies

**Three declared runtime dependencies**, in `pyproject.toml`:
`PySide6-Essentials`, `pyqtgraph` and `pydantic`. `flet` and `flet-charts`
went out with `PL-3SQT`, once `PL-25KS` had deleted the last module importing
either. Removing them from that list is not what keeps Flet out, though -
`tools/import_boundary_check.py` permits both in no module under `src/` at
all, and that is the rule.

**numpy arrives underneath pyqtgraph**, whose metadata requires
`numpy>=1.25.0` outright, so it is installed in every environment and
`uv.lock` names the version - but no module under `src/` imports it, and
`import_boundary_check.py` permits it in none under `core/`. The tests declare
it for themselves, in the `dev` group, since
`tests/reference/test_late_washout_against_published_fits.py` decomposes the
model's open-circuit system with `numpy.linalg.eig` (`PL-921Y`). Nothing here
takes a position on declaring it for the application; `docs/WORKING_NOTES.md`
§ "Decided: no numpy" says why that stays open until a module under `src/`
wants it.

**What Linux has to supply, which the Qt wheels do not carry.** Measured
2026-09-16 with `ldd` over the wheel's own `Qt/lib/libQt6Gui.so.6` and
`Qt/plugins/platforms/libqoffscreen.so`: both link shared objects that resolve
outside the wheel, and five OS packages provide them.

| shared object | Debian/Ubuntu package |
| --- | --- |
| `libEGL.so.1` | `libegl1` |
| `libGL.so.1`, `libGLX.so.0`, `libGLdispatch.so.0` | `libgl1` |
| `libxkbcommon.so.0` | `libxkbcommon0` |
| `libdbus-1.so.3` | `libdbus-1-3` |
| `libfontconfig.so.1` | `libfontconfig1` |

Only the first is normally absent. `README.md` § "Running it" names `libegl1`
alone because the other four are on an ordinary desktop already, and
`.github/workflows/quality.yml` installs `libegl1` alone because its own
comment records the other four as present on the `ubuntu-latest` image
(`PL-VHLZ`). The full list is here so that a minimal container - which is
neither of those - has something to read. macOS and Windows need nothing
extra.

**Licensing, written down before a packaged build needs it (`PL-3SQT`).**
`pyside6_essentials` 6.11.2 and `shiboken6` 6.11.2 both declare
`LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`, and neither wheel ships the
licence text: measured 2026-09-16, neither `dist-info` carries a `licenses`
directory or a `License-File:` entry. This repository is Apache-2.0 and has no
`NOTICE`. **Nothing is violated today.** The LGPL obligations - dynamic
linking, a recipient's ability to relink, conveying the licence text - attach
when a binary is *conveyed*, and this project conveys none: `README.md`
§ "Running it" says building from source is the only route, and `uv` installs
each wheel from PyPI per user. They arrive the day a bundled build does, which
is `ROADMAP.md`'s packaging work, and this paragraph exists so that is not
discovered then. pyqtgraph is MIT and numpy is
`BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0`; both ship their licence
text in the wheel.

## The workflow apparatus

The scripts under `tools/`, the hooks under `.claude/hooks/` and the
third-party text their tests read are mapped in
[`docs/apparatus.md`](apparatus.md). They exist so that agent sessions can
build the simulator, nothing under `src/` imports them, and that document is
held to `.claude/rules/apparatus-standard.md` rather than to the specialist
standard `CLAUDE.md` holds this one to (`PL-KRGY`). One of them holds this
document to the code: `tools/doc_check.py` checks the package map above
against the tree on disk in both directions, so a module added without a line
in it, or a line left behind after a deletion, fails `make check`.

## Tests (`tests/`)

- **`tests/unit/`** — one module's behavior in isolation (a compartment, a
  validator, a parameter loader, the controller, the displayed-value
  formatters, and what the dashboard claims per tick with no toolkit loaded,
  in `test_dashboard_frame.py`).
- **`tests/integration/`** — components wired together as the app assembles
  them (e.g. controller driving a full `AgentUptakeSystem`), the Qt chart
  drawn headless against a real run (`test_qt_chart.py`), which reads the
  plotted items and the painted pixels back, the dashboard's leaf widgets
  (`test_qt_widgets.py`), the whole dashboard driven against real
  controllers (`test_simulation_view.py`), which reads every widget's text,
  enablement and visibility back, and the whole dashboard rendered headless
  at one fixed size (`test_qt_rendering.py`), which reads the painted pixels
  and the laid-out geometry back and writes the kind of screenshot
  `.claude/skills/run-the-app/SKILL.md` shows a session how to take
  (`PL-YCWZ`, `PL-CQRL`), and what the interface draws when
  the *host* is set to a dark appearance (`test_dark_appearance.py`), which
  sets the palette such a host supplies on the `QApplication` - where the
  others set it on one widget - because the declarations it tests are
  themselves palettes (`PL-RKRY`). `tests/conftest.py` selects Qt's
  `offscreen` platform plugin before any `PySide6` import, so the suite renders
  on a runner with no display; on Linux that plugin needs `libegl1` from the
  OS, which `.github/workflows/quality.yml` installs and the PySide6 wheels
  do not carry (`PL-VHLZ`).
- **`tests/reference/`** — analytic/independent reference cases the
  implementation must reproduce (e.g. the closed-form circuit wash-in
  solution, the sevoflurane patient reference scenario, and the from-scratch
  RK4 integration of the coupled system in `test_coupled_dynamics.py`).
  These are the regression tests referenced throughout `docs/MODEL.md`'s
  release gate. A reference case here may import the parameter loaders but
  must not reach a solver in `core/`: the value of the case is that it was
  derived independently of the code it checks.
- **`tests/benchmarks/`** — measurement harnesses, which are not tests and
  are not collected as any: `frame_cost.py` drives a real dashboard frame by
  frame under the `offscreen` platform and times each frame's simulation
  (`controller.advance`), assembly (`SimulationView.present`) and paint
  (`QApplication.processEvents`), so "is this the simulation or the
  interface" is re-measured with one command rather than re-derived on a
  throwaway harness for a fifth time (`PL-ZG5J`). Run it with `uv run python
  tests/benchmarks/frame_cost.py`; it takes about three seconds and prints
  timings, which are a judgment rather than a verdict. This is why such a
  harness is not a `tools/` script: those are invoked by `make check`, CI and
  the hooks under a bare `python3` outside the project virtualenv, which is
  what makes them standard-library-only, and a harness that imports PySide6
  and the package itself can only ever run inside it. What *is* decidable
  about one — that it still runs, and still reports the stages it names — is
  a collected test beside it, `test_frame_cost.py`, which asserts nothing
  about a duration: a threshold here would measure the runner rather than the
  code.

## Where new code belongs

- A new physiological compartment or coupling → `core/`, with its equations
  and reference cases documented in `docs/MODEL.md` first (per `CLAUDE.md`).
- A new agent, patient or machine profile → a new validated, cited file under
  the matching subdirectory of `data/`, not hardcoded values in `core/`. Where
  a compartment keeps a field default restating one of those values for bare
  unit construction, the default is pinned to the file by a test, as
  `test_the_bare_circuit_defaults_match_the_shipped_machine_file` pins
  `BreathingCircuit`'s.
- A number the code needs → one home, read through its name at every use: a
  cited data file under `data/` for a scientific value, `core/units.py` for a
  factor between units, and otherwise a module-level constant in the module
  that owns the quantity - imported elsewhere, never declared a second time.
  `tools/literal_home_check.py` refuses the two shapes a copy takes: a bare
  numeric literal anywhere under `src/anesthesia_sim/` other than 0, 1 and 2,
  and a numeric constant defined in more than one module. Its baseline holds
  the literals that predate it and only shrinks, and a finding names any
  constant of the same value without deciding that it is the same quantity,
  which stays the reader's call (`PL-40SJ`).
- A new display panel or control → what it *claims*, as a plain value with a
  test in `tests/unit/test_dashboard_frame.py`, in `app/dashboard_frame.py`;
  the widget that draws it, deciding nothing, in `app/qt_widgets.py`; and its
  place in `app/run_view.py` or `app/simulation_view.py`, where the first
  question is *whose* it is. A panel stating a particular run's numbers -
  readouts, settings, transport, the record of what was changed during it -
  belongs to `RunView`, which is instantiated once per run, and the dashboard
  places it by looping over its runs. A panel about the chart both runs are
  drawn on - an axis, a legend, a reference, the time base, the compartment
  selection - belongs to `SimulationView`, and so does a control asking one
  question of the whole case rather than of either run: the bookmark editor
  is the worked example (`PL-LPLD`), and it writes each mark to every
  displayed run so the copies the controllers hold stay equal. The branch
  control is the second (`PL-VKJW`): the instants it offers are the trunk's
  keyframes, so duplicating it into each run would give a branch a control
  that could only refuse. Getting this the wrong way round
  is not a tidiness matter: a run's panel put on the dashboard would state one
  branch's numbers over both, and a shared control duplicated into each run
  would let a comparison be read under two different settings. Either way,
  read only what `SimulationSnapshot` already carries and what a
  `DrawnWindow` already answers — a window holds its states per substance,
  and a trace addresses one value in them as a `RecordedSeries`, a
  substance-and-`RecordedQuantity` pair, rather than as a named field; if the
  UI needs a value that doesn't exist yet, add it in `app/controller.py`,
  computed in `core/`, never computed in the view. A panel wanting the run
  rather than the instant asks
  `SimulationController.drawn_window(start_s, stop_s, columns)` for the span
  it draws, and never for the whole run: the states come back evaluated for
  the instants that span plots, so what crosses that boundary is bounded by
  the display rather than by the run's length.

  **The *whose is it* question describes the fixed layout shipped today, and
  is superseded when `ROADMAP.md` item 34's area system lands.** It routes by
  which of two containers holds a surface, and an area holds one View with
  any View able to occupy any area, so the question stops having an answer:
  `PL-TH35` is where the View contract that replaces it is written, and
  adding that route is its work rather than this bullet's. Until then this
  bullet still decides **where the code goes**, and
  `.claude/rules/ui-areas.md` — which loads on the same `src/` read as this
  file — decides **what shape it is in**: a widget that does not assume its
  size, its neighbours, or that it is alone. The two are not in conflict once
  read that way, and neither licenses building splitting, joining, workspace
  tabs or layout persistence early. What outlives the fixed layout is this
  bullet's *reason* rather than its routing: a run's panel must not state one
  branch's numbers over both, and a control shared between runs must not be
  duplicated into each. Both are properties of the value rather than of the
  container, and they bind a View exactly as they bind a panel today.

  *The supersession has a release, as of 2026-09-16*: v0.6.0, "the layout is the
  reader's", which builds the Areas, the View contract, the Workspaces and the
  persistence. Break-out into a second top-level window is item 34's second
  half, wanted but unscheduled since 2026-09-26; once it is built, the
  routing question gains a second half - *which window* a surface is
  instantiated in - answered by `docs/MODEL.md` § "Minimum displayed outputs"
  rather than by this bullet.
- A new way of *rendering* a value a reader interprets — a unit, a decimal
  count, a marker for what the display cannot resolve → `app/formatting.py`,
  as a pure function with its own test, and with the reason recorded in
  `docs/MODEL.md` § "Displayed precision".
- A new chart series, or a change to how one is drawn → what it *claims* in
  `app/chart_frame.py` and how pyqtgraph paints it in `app/qt_chart.py`, with
  a new *compartment* trace declared in `chart_frame.COMPARTMENT_TRACES`,
  which is where the quantity it draws, how it is drawn, the legend words that
  name it and the gloss its hover carries are written as one record. The
  table is the chart's rather than any one run's: `assemble_chart_frame`
  reads it once per run, for the substance that run's snapshot names — the
  run is recorded under that identifier — and `ChartFrame.visible` is the
  subset the legend leaves drawn, narrowed by `compared_compartments` to
  `COMPARED_COMPARTMENT_CAP` once more than one run is on the chart, so
  `app/qt_chart.py` holds one curve per run per trace and moves it to match;
  nothing is edited directly. The *width* of that curve is the run's own
  channel while two are drawn and is `chart_frame.run_trace_style`'s, not the
  table's: the table is what a compartment looks like, and a new trace
  declares no width for a run. A series
  that draws no state of the run — a
  clinical reference, a control mark — stays out of that table by
  construction, and owes the labelling requirement `docs/MODEL.md`
  § "Interface boundary" puts in place of the drawn-point rule instead. So
  does a trace of a *derived* quantity with a domain, such as the wash-in
  ratio: the table binds a line to one `RecordedSeries`, and a value that is
  sometimes absent has no such series to be bound to. It owes its domain in
  `docs/MODEL.md` and at the point of display instead.
