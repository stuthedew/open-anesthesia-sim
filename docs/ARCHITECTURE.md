# Architecture overview

This document describes how the code is organized and how data flows through
it. It is a map for contributors, not a scientific specification — for the
equations, units, parameter provenance, and numerical method, see
[`docs/MODEL.md`](MODEL.md). For version history and milestones, see
[`ROADMAP.md`](../ROADMAP.md).

## Layering

The codebase is split into three independent layers, enforced by import
direction (never edit around this — see `CLAUDE.md`):

```text
data/  --loaded by-->  core/  --read by-->  app/
```

- **`core/`** is the scientific simulation. It has no dependency on Flet, no
  wall-clock time, and no I/O beyond reading the packaged JSON files in
  `data/`. Every quantity it produces is deterministic for identical inputs.
- **`app/`** is the Flet user interface. It never performs a physiological or
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
independent of Flet, no simulation calculations belong in UI callbacks, and
model parameters live in validated, versioned data files rather than as
executable code.

## Package map

```text
src/anesthesia_sim/
├── app_metadata.py      # app name, bundle id, and the version the header shows: the installed distribution's version, plus the commit where the running code is not a clean checkout of the released tag, because between two releases every build otherwise displays the same string and a fix confirmed by eye cannot be told from the code it replaced
├── core/                # scientific simulation — no Flet dependency
│   ├── validation.py              # shared input-validation guards (raise SimulationConfigurationError)
│   ├── concentration.py           # fraction vs percent: the two forms, and the only crossing
│   ├── supported_ranges.py        # the declared domain; refuses a setting, or a run, outside it
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
├── app/                  # user interface - Flet, with the chart already on pyqtgraph while the port lands (ROADMAP.md § "v0.4.26 - the interface moves to Qt")
│   ├── controller.py               # SimulationController: run controls, read-only snapshots; ResumePoint and BranchedCase: where a branch opened, and the trunk it belongs to
│   ├── simulation_view.py          # renders snapshots as the dashboard; no domain logic. Two classes since PL-B9PY: `RunView` is one run - its controller, readouts, settings, transport and the lines it draws - and `SimulationView` is what two runs share, the charts, their axes, the window, the time base and the compartment selection
│   ├── formatting.py               # modeled value -> displayed string; Flet-independent
│   ├── playback.py                 # playback rate -> whole simulation steps per tick; Flet-independent
│   ├── chart_frame.py              # what one frame of both plots draws, as plain values: the trace table, the window, the axes' ticks, the references, the marks, the wash-in stretches and the hover text; toolkit-independent
│   ├── chart_series.py             # builds and redraws the Flet chart's traces, references and control marks; leaves with PL-7SVX
│   ├── qt_chart.py                 # the concentration chart, the wash-in plot and the legend on pyqtgraph, moved per frame to match a chart_frame.ChartFrame; declares no colour and formats no value
│   ├── chart_time_base.py          # how wide the chart's window is and how it is ruled; Flet-independent
│   ├── control_timeline.py         # recorded control changes -> the acts a reader sees; Flet-independent
│   ├── wash_in.py                  # F_A/F_I and the domain it holds on; Flet-independent
│   ├── theme.py                    # every display token: palette, cited ISO 5360 agent colors, type sizes, spacing, dash patterns; Flet-independent
│   └── main.py                     # entry point; builds the Flet page
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
however long the run has been going. The recorded run itself — one
`SimulationHistorySample` per simulation step, not trimmed — is answered for
separately, by `history_window()`, which returns the samples at or after a
time the caller names. The two were one field until PL-0VM7: the snapshot
carried every sample ever recorded, so a frame's cost grew with the length
of the run while the chart discarded all but the few hundred inside its
axis. The snapshot does carry the run's `ControlChange` timeline — one entry
per setting the model was actually stepped under, so re-applying the
timeline reproduces the run rather than approximating it, and a timeline is
bounded by how often a user touches a control rather than by how long they
watch.

**A run is its inputs, and its states are derived from them** (PL-T691).
Beside the recorded history the controller holds a `core/run_definition.py`
`RunDefinition`: the settings in force at each moment, plus one keyframe — the
state at that instant — per change. Because the equations are linear and
time-invariant while the settings hold, the propagator is exact over any
horizon and not only over a step, so every state the run passed through is
one propagation from the keyframe bracketing it and none of them has to have
been recorded. `evaluate_window(start_s, stop_s, columns)` is that read, and
`run_segments` hands the record itself out as frozen segments — readable
without being advanceable, so nothing above the controller can move the
run definition's reach past where the run actually got to and have a prediction
come
back drawn on the run's own axis. `docs/MODEL.md` § "The run is that record,
and every state is derived from it" carries the measurements, and § "The
canonical evaluation rule" states which of the two evaluation paths a stored,
exported, replayed or branched value may be taken from.

**That boundary is a type rather than a convention.** `evaluate_window` hands
back `DisplayState` values, which are not state vectors, so a drawn column
cannot become a keyframe, an exported figure or a branch's opening state by
being the same nine numbers in the same order; `RunDefinition` refuses one as an
opening state by name. A layer above the controller therefore cannot cross
that boundary by forgetting it is there, which is the only way a boundary
stated in prose is ever crossed.

Both records are live in this release and the chart still draws from the
recorded one; § "Closed-form agreement test" is what holds them to each
other while that is true. Which representation the interface reads is not a
question the layering leaves open — the run definition is the run and the samples are
a second copy of it — so this is a transition rather than a choice, and
PL-2FM6 is what finishes it.
`app/simulation_view.py` reads only those two — it builds the
controls, drives the chart, and wires slider/button callbacks through
`_apply_setting` to controller setters. It performs no physiological or
unit calculation of its own. The transformations it does apply are each
their own module, because each is a presentation-*correctness* question
rather than a layout one and each must be readable and testable without a
Flet interface: `app/formatting.py` turns a fraction into the strings a
reader sees — a percent and a multiple of the running agent's 1 MAC — at the
resolutions `docs/MODEL.md` § "Displayed precision" derives,
`app/chart_frame.py` settles what one frame of the chart claims - which
compartment a curve carries, which instants are drawn, where the references
stand, what a hover says - as plain values with no toolkit loaded, and
`app/qt_chart.py` moves pyqtgraph items to match it while `app/chart_series.py`
still does the same for the Flet chart, `app/control_timeline.py` turns the recorded control changes into
the adjustments a reader sees, `app/playback.py` turns the playback rate a
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
reference is built and moved by `app/chart_series.py` but is deliberately
not a member of the view's trace-to-compartment table: it reads no sample.
A control mark is a third kind of series on the same terms and for a
stronger version of the reason — it draws no value at all, only a simulated
time — and it is likewise outside that table.

**Failure direction:** every failure `core/` reports is a subclass of
`AnesthesiaSimulationError` (`core/exceptions.py`), never a bare
`ValueError`, so the interface can recognise a simulation failure and act
on it. The hierarchy's two branches mean different things and get
different treatment:

- `SimulationConfigurationError` — a value was rejected before it changed
  anything. Raised by the guards in `core/validation.py`, by compartment
  constructors and setters, and by the parameter-file loaders. The view's
  `_apply_setting` catches it, restores the control from the snapshot, and
  says the setting was refused; the run is untouched and keeps going.
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

Both view loops are guarded, and both call `SimulationController.fail()`
on any exception — a `TypeError` from a refactor kills an asyncio task
exactly as silently as a modelling failure does. `fail()` is a third run
state, carried on the snapshot as `failure_reason` and rendered as
"Stopped — simulation error" with a banner over the values: a halted run
must never present as a pause, because a pause is a run that continues when
asked and a halt is one that cannot. It cannot be resumed, only cleared by
`reset()` or by starting a fresh run with `set_agent()`. Neither loop returns on
failure — they are started once, at mount, so a loop that exited could
never be restarted.

Drawing that full record every frame is what made the render payload grow
with run length. The run no longer keeps a record to draw: `core/run_definition.py`
answers the state at any instant in closed form, so the view asks the
controller for the states at the instants it is about to plot
(`SimulationController.drawn_window`) and there is nothing to subset. Which
instants those are is a presentation-correctness concern — a chart that
stepped over a control change would show a curve the simulation never
produced — so the rules that place them are stated in `docs/MODEL.md` § "What
the chart draws" and tested on their own. Bounding how many points are drawn
is only half of it: the client is
patched per point, so what a frame costs is how many drawn points *changed*
which sample they show. The selection is therefore anchored to absolute
sample index rather than to position within the window, so appending a
sample leaves every completed bucket choosing what it already chose
(PL-Q197). `app/chart_frame.py` is the layer above it — it holds the
per-trace column floor and reads the window once per run for every trace,
and `app/chart_series.py`, for the Flet chart, converts each drawn value into its own axis's unit,
and moves the points a trace already holds — and it is separate for the same
reason: which quantity a line carries is a correctness claim, and the view
passes it in as one `PlottedSeries` table declared beside the traces
themselves. The unit conversion belongs to the caller that knows the axis:
the six compartment traces are drawn in percent and the wash-in ratio in its
own dimensionless unit, through one shared point-writing primitive. Stepping and drawing also run as separate loops on separate intervals,
so simulation time stays a function of steps taken rather than of how long a
frame took.

## What a branch is, and what it shares with its parent

A **branch** is a second live run of the same case, opened at a state the
first run passed through. The run it was taken from is the **trunk**. One
trunk with N branches is the whole of the structure — sub-forks of forks are
excluded rather than unimplemented (project owner, 2026-08-25): they multiply
without bound and buy little over branching from the trunk again.

This is the object map. What a branch *guarantees* — that it opens at a
keyframe and why, that its run definition opens at that keyframe's own case
instant so no clock is re-based and no conversion is performed, and what both
are worth in floating point — is `docs/MODEL.md` § "The canonical evaluation
rule", which is the one place those are stated and measured.

Three objects in `app/controller.py` carry it:

- `SimulationController.resumed_at(elapsed_s)` makes one. It builds a second
  controller through the ordinary constructor, replays the trunk's settings
  from the recorded control timeline into it, seeds its system with the
  trunk's canonical state at `elapsed_s`, and hands it back paused. The trunk
  is read and never written, so the two runs share no compartment, no
  accounting and no clock — which is what lets both be advanced.
- `ResumePoint` is where the branch came from: the trunk stretch it opened
  inside, the case's step count there, the step it was taken at, and the
  agent its accounting period started from. `opened_from` is `None` on a
  trunk and this on a branch, so every run knows which it is.
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
in the units the compartments hold, and then checked against the settings the
trunk's own stretch carries rather than trusted. What it does not inherit is
the trunk's control timeline, which starts empty: the branch's record is of
what the learner does to *it*, and `opened_from` is what records where the
fork was taken — the definition's own first segment stands at the same instant,
so `opened_from` carries the provenance rather than being the only copy of the
number.

**One time frame, and every reader is in it.** A branch continues the case's
step count, so `snapshot().elapsed_s`, every control-change stamp,
`drawn_window`'s instants *and* the instants `run_segments` hands out are all
case time. Its `RunDefinition` opens at the fork rather than at a zero of its
own, so a keyframe read from a branch needs no conversion to be placed on the
case's axis and no reader has to know which kind of run it is holding.

Until 2026-09-14 there were two frames and a `SimulationController.origin_s`
holding the difference, which `advance` and `drawn_window` subtracted and
`run_segments` warned about. `PL-ZMRT` (project owner, 2026-09-14) removed the
second frame: `origin_s` and both subtractions are gone, and `PL-2R2C` — a
branch's drawn columns anchored to its own zero, landing at case instants the
trunk never draws — was dissolved by it rather than fixed separately.
`docs/MODEL.md` § "The canonical evaluation rule" measures what that is worth.

**Where a branch may be taken.** At any keyframe the trunk holds —
`BranchedCase.fork_points_s` — which is its opening at induction and every
setting change the model was actually stepped under. Anywhere else is refused
rather than approximated, for the arithmetic reason `docs/MODEL.md` measures.
`tests/unit/test_run_definition.py` holds the other side of that refusal: that
a branch opened off a keyframe really does stop reproducing the run it claims
to continue, rather than the refusal guarding against nothing.

A **bookmark is not yet one of those instants**, and how it becomes one is
open. Bookmarks are `PL-LPLD` and the halt that stops a run on the step
crossing one is `PL-CTD7`; neither is built. A bookmark's instant is not in
general a setting change, so the trunk holds no keyframe there and `resumed_at`
refuses it like any other — on a 120 s run with two control changes, 3 of the
1 201 instants a halt could land on are keyframes. Two routes to a forkable
bookmark are measured in `PL-B8MK`, and the obvious one is the worse of them:
recording a keyframe where the run halts makes the branch exact against the
trunk it forked from, but it moves that trunk's own later answers away from
what the case would have said unmarked, so marking a run changes it. Opening
the branch's *definition* at the keyframe before the bookmark, while its clock
and its live system stand at the bookmark, costs the trunk nothing and is exact
too. Neither is built or chosen here.

What a comparison between two branches *asserts* — what a difference between
them may be attributed to, and that neither is a prediction for a patient — is
not here and is not yet written anywhere. It is `PL-W7H9`, which places it in
`docs/MODEL.md` and in this document.

## Data files (`data/`)

Each JSON file carries a `schema_version`, an `id`, the parameter values, and
a `sources` array of citations (`citation`, `url`, `tier`, `adopted`, `note`
per entry — see `core.parameters.SourceReference`). `tier` is drawn from the
closed vocabulary `core.parameters.SOURCE_TIERS`, which is the three tiers
`docs/MODEL.md` § "Source hierarchy" defines; `adopted` says whether the file
names that source as the authority for a value it stores, which is a separate
question from what tier the source is. A file that adopts no primary source at
all carries a top-level `provenance_gap` saying so. `core/parameters.py`
rejects a file that
is missing required fields, uses an unsupported schema version, declares a
tier outside the vocabulary or an `adopted` flag that is not a JSON boolean,
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

## Developer tooling (`tools/`)

Outside the packaged application, and not imported by it:

```text
tools/
├── agent_identity_check.py  # refuses a control that carries the agent colour and can be rendered disabled, because Flet/Material then paints its label in a disabled-content grey that is declared in no source file and so is unreachable by `contrast_check.py`; a control may be `disabled` only where it is also `visible = not <the same expression>`, and one given an agent colour where it is constructed must be written by the single writer `RunView._apply_agent_color_scheme`
├── branch_id_check.py    # refuses a branch ahead of the default base that carries no item id in its name and leads no commit subject with one, because every in-flight guard matches an id and work carrying none is invisible to all of them; scoped to the `claude/*` namespace, since a contributor has no queue to be visible in
├── dead_ends.py          # emits `docs/dead-ends.md`'s entry lines into session context at start, and holds that emitted half - never the file's preamble, which is instructions for adding an entry rather than for reading one - to 30 entries and 4,000 bytes, because a `SessionStart` hook's output is resent on every turn and an unbounded always-loaded store measurably degrades an agent rather than merely costing tokens; refuses an entry citing an id that resolves to nothing, since `bin/docket show <id>` is the entry's whole retrieval path
├── contrast_check.py     # computes every declared color requirement's WCAG 2.2 contrast ratio from the constants in `app/`, and holds each to its declared minimum, taking the better channel where an element's edge can be carried by either its fill or its border
├── core_vocabulary_check.py  # holds `core/`'s identifiers to the vocabulary `docs/MODEL.md` establishes, in the three ways that are decidable: every `ClassName.accessor` in the Symbols table's Code column resolves to a real attribute, property or field - an em dash being accepted only where the cell says what the code reads instead; none of the accessor names `PL-9SH6` retired comes back, matched whole rather than as substrings, so that an identifier merely containing a retired name is not accused of reviving it - a rule with no live counterexample in `core/` since `PL-6KNM` renamed `require_concentration_fraction` to `require_fraction`, and `PL-JW9J` is where tightening it is decided; and every `*partition_coefficient` identifier names both of its phases in the declared outward order, gas then blood then tissue, so a coefficient cannot be written as its own reciprocal in a literature that calls one quantity tissue-gas, tissue-blood and blood tissue in a single chapter. It runs under `uv run python`, not at the 3.11 floor, because it parses `core/` with `ast`; whether a name is the one a reader who knows the domain would guess stays a judgment and is deliberately not scripted
├── doc_check.py          # validates this map, MODEL.md's provenance table and its marked prose values, the data files' declared source tiers, citations - in the documentation, in every `docs/items/` brief and in every source docstring, since those last two are where this project writes most of them - markdown math syntax, ROADMAP.md's release train, frozen-list counts and current baseline, and the current gate's membership against the queue - unconditionally for the queue's `safety`- and `science`-classed items, and as a recorded disposition, placed or deferred, for every other open debt item; that no milestone names one id under both its `Required scope` and its `Explicitly out of scope`, advising where a scope bullet carries exclusion language; that every test `MODEL.md` names resolves to one that exists; reports resident instruction size
├── glyph_check.py        # refuses a non-ASCII character that nobody has confirmed the client can draw, from any string that can reach a reader - every string literal outside a docstring under `app/` and `core/`, and every string in the `data/` JSON - because `→` (U+2192) has no glyph in the Flutter client, drew as a replacement box in the control-change list, and no test in this repository could see it: every string assertion here compares text the same font-less Python process produced; the allowlist is per character rather than per Unicode block, and each entry records what was rendered and looked at
├── import_boundary_check.py  # fails the build on any import its `BOUNDARIES` table confines elsewhere: `pydantic` anywhere under `src/anesthesia_sim/` other than `core/parameters.py`, and `time`, `datetime`, `random`, `secrets` or `uuid` in any module under `core/`, so the payload/dataclass boundary and the never-wall-clock rule are measured rather than asserted
├── ignore_check.py       # evaluates warn_unused_ignores over the two test trees `[tool.mypy] files` excludes, so an inert `type: ignore` fails the build
├── item_reads.py         # reports, from the local untracked `.docket-reads.log` that `.claude/hooks/item_read_log.py` writes, how many distinct items sessions actually open, what share of those are closed, and how many citation edges are traversed within a session - the read-side measurements every argument about the store's shape had been assuming; states the sample size first and chooses between none of the readings a low count admits
├── main_ci_status.py     # reports the default branch's last quality verdict, and nothing at all when it was a success, because the whole-store `verify:` replay runs only on push to `main` and its failures therefore land on a run no pull request shows; the session-start hook calls it, it gates nothing, and it is the one tool here that reads the network
├── pr_title_check.py     # refuses a pull request whose title does not lead with the ids its branch closes, because the squash-merge subject is taken from that title and is what `docket check` reads to recover which pull request closed an item
├── rules_paths_check.py  # refuses a `.claude/rules/*.md` `paths:` entry that does not begin with `/`, or whose literal prefix resolves to nothing, because an unanchored glob also matches its name at any depth while `./` and a typo'd prefix match nothing at all — so a rule's real scope can differ silently from the one it declares, in either direction
├── workflow_paths_check.py  # holds `docket.toml`'s two hand-maintained lists to the tree: `workflow_paths` to what each file under `tests/` imports — apparatus when it does not import `anesthesia_sim`, the simulator's when it does — because the apparatus tests living in the simulator's test tree were listed by hand and drifted, and an item declaring one alongside the script it tests is set aside from both lanes and offered to nobody; and `gate_paths` to every `ruff.toml` in the tree, because an uncovered linter config is one `docket verify`'s "the checks themselves are unedited" audit will not defend
└── ruff.toml             # pins the formatter to the oldest interpreter these tools have to parse under
```

`tools/doc_check.py` holds this document to the code. The package-map trees
above are checked against the tree on disk in both directions, so a module
added here without a line in the map, or a line left behind after a deletion,
fails `make check`. That is why the trees list every module individually: a
directory drawn with no children beneath it stands for its whole subtree and
is not expanded — no tree draws one today — and `__init__.py` is excluded
throughout. The same tool checks `docs/MODEL.md`'s provenance table against
the data files and resolves every path and section heading the documentation
cites.

Its `check_source_tiers` holds the same data files to `docs/MODEL.md`
§ "Source hierarchy": every `sources` entry declares a `tier` from the closed
vocabulary and an `adopted` flag, and a file with no entry that is both
`primary` and `adopted` records a `provenance_gap`. It decides only what a
file *declares*. Whether a citation labelled `primary` really is a primary
measurement of the quantity needs somebody who has read the paper, and a tool
guessing at that — by author, by journal, by a denylist on a product name —
would be authoritative and wrong. That is the same split the provenance table
check already runs on: it decides that a documented key exists and holds the
stated value, never that the value is right.

`tools/pr_title_check.py` is the prevention half of `PL-2XTF`. A squash merge
takes its subject from the pull request title, so a title naming none of the
items it closes lands a subject that `docket check` cannot trace a closure back
to. That happened once: a UI-generated title closed three items, `main` went
red with errors no recovery could clear, and the numbers had to be read off
GitHub by hand. The recovery half now falls back to each item's own file
history, and this half stops the bad subject reaching `main` while the title
can still be edited. Both are wanted — recovery alone leaves the wrong subject
on `main` for good, and the check alone leaks when a merger retypes the subject
in the squash dialog.

It runs in `.github/workflows/pr-title.yml`, which takes the title from
`PR_TITLE`, and in `make check` and `make pr-title`, which pass `--discover`
and read it from the branch's own open pull request instead (`PL-J3BB`). It
was CI-only until then, which made it the one gate a session could not run
before pushing: the check compares the title against *what the branch closes*,
and a branch closes more items as it goes, so a correct title goes stale the
moment the next item closes on it. Every way the lookup can fail — no token, no
network, no pull request open yet — is a silent skip, so `make check` stays
green offline.

`tools/branch_id_check.py` is the same shape of guard aimed at the other end of
the same problem, and the two do not overlap: the title check asks whether a
pull request names the items it *closes*, and answers "no id is owed" for a
branch that closes none — which is exactly the unfiled repository housekeeping
`PL-CP74` found colliding. `docket flight`, `show`, `next`, `concurrent` and
the session-start digest all answer "is anybody already on this?" by matching a
`PL-` id in a branch name or at the front of a commit subject, so a branch
carrying none reads as nobody's work to every one of them, and goes on doing so
after both sessions have pushed.

That argument is about agent sessions, so the check binds only their branch
namespace — `claude/*` — and passes anything outside it. A contributor has no
queue and no id, and requiring one refused `#394`, the project owner's own
web-UI edit to the README, in the required job (`PL-8P6D`).
[`CONTRIBUTING.md`](../CONTRIBUTING.md) is the route that leaves open.

It imports `BRANCH_ID_RE` and `leading_ids` from `docket.vcs` rather than
matching ids its own way, because a check looser than the guard it protects
would certify a branch as visible that `docket flight` still cannot see — the
gate green while the guarantee is void. One commit carrying an id is enough,
which is what keeps the tool out of the judgment it must not make: how small a
piece of work is too small to file is decided in `.claude/skills/docket/SKILL.md`
under "Mode: housekeeping nobody filed", and a fix riding inside a commit an id
already leads needs no item of its own. A release commit is exempt, exactly:
`make release` writes that subject, and it closes no item.

`tools/contrast_check.py` holds the interface to the accessibility target
`docs/MODEL.md` states — WCAG 2.2 Level AA. It reads the color constants with `ast`
rather than importing them, because `app/simulation_view.py` imports Flet and
these tools run under a bare `python3`. Since `PL-2CS8` every color is declared
in `app/theme.py`, and `check_colors_live_in_the_theme` fails the build on one
declared anywhere else; it still parses `app/simulation_view.py` as well, so a
color put back there is measured rather than lost, which is the failure that
item was filed for. Its `REQUIREMENTS` table is the specification: each entry names
the colors that appear on screen together, the success criterion, the minimum,
and the reason, which cites the code they are drawn in by symbol. Most entries
are one foreground against one background; an element whose edge either of two
channels can carry — the agent badges, each a fill with a border in the agent's
own text color — declares both and is held to the better, because measuring
such an element one channel at a time reports a false shortfall whichever
channel is picked (`PL-GNN1`). The tool
evaluates that table and decides nothing else — which colors matter, which
channels an element really has, and whether
a non-color channel is genuinely redundant, are judgments, and
`.claude/rules/ui-color.md` carries them. The one thing it does decide about
the prose is the half a script can: a description may cite no line number, and
every symbol it names must exist in the two modules read above. Those citations
were line numbers until `PL-GJDW`, and all fourteen had rotted into unrelated
code, which made the tool's own coverage unauditable while looking audited. Requirements that fall short
today are listed against the item that closes each, and a listed shortfall that
starts passing is an error, so a fix cannot leave its excuse behind.

It measures one thing beyond the `REQUIREMENTS` table, and that one is a hard
error rather than a listable shortfall. `TRACE_FLOOR` holds each of the six
chart traces to 3:1 against the panel under **four** vision models — as
displayed, and simulated for protanopia, deuteranopia and tritanopia by the
Brettel 1997 projection in `DICHROMACY_TRANSFORMS`. The fourth model is the
project's own bar rather than the criterion's, since SC 1.4.11 is defined on
the color a display emits; the reason it is worth the extra arithmetic is that
`MUSCLE_COLOR` measured 3.19:1 on screen and 2.98:1 for a deuteranope, which no
normal-vision check could see (`PL-GVXP`). `--matrix` prints the pairwise
separation across all four, which is the evidence that these six traces cannot
be separated by color at all and that the line style is doing the work;
`docs/MODEL.md` § "The six compartment traces" carries the tables and the
limits on how far a simulated ratio may be read.

`tools/agent_identity_check.py` closes the one gap that table structurally
cannot cover: a colour the project never declares. Flet/Material paints a
disabled control's label in the theme's disabled-content grey, which appears in
neither module `contrast_check.py` reads, so a requirement went on measuring
the enabled pair and reporting a pass while the agent's name sat grey on its
own ISO 5360 fill for the whole of every run (`PL-61WW`). The rule it enforces
is the project owner's, 2026-09-08: no control carrying agent identity may be
*rendered* disabled, so SC 1.4.3's exemption for an inactive component — which
settles a conformance claim, not whether a reader can identify the running
agent — is never claimed here. Rendered is the load-bearing word: a control may
be `disabled` where it is also `visible = not <the same expression>`, since it
then draws nothing. The identity set is not a second list to keep in step but
whatever `RunView._apply_agent_color_scheme` writes, that method already
being the single writer of agent colour; a control given an agent colour where
it is constructed and never written there is the check's other error, and is
what keeps that coverage claim true rather than asserted. Like the two tools
above it decides nothing else — whether a control's identity is legible, and
whether a pairing is the right one for it, stay judgments.

**What a Qt port costs these two, measured rather than estimated (`PL-JRS3`).**
The dependency is split, and not the way the question assumed: one reads
*values* and survives, the other reads Flet's *control objects* and goes
silent. Measured 2026-09-14 by rewriting `app/theme.py` and
`app/simulation_view.py` on the AST — every Flet property assignment replaced
by the PySide6 setter call that supplants it — and running both against the
result.

`contrast_check.py` survives. Its whole input is module-level
`NAME = "#RRGGBB"` constants, which no toolkit owns, and every way of removing
a declared one is loud: renaming `FAT_COLOR` failed with the constant named,
and moving `SimulationView` to its own module — which `PL-B9PY` records the
port doing from the start — failed with 68 unresolved citations, from the
symbol rule `PL-J7C5` added for an unrelated reason. Its one hole is
**additive**, and the port is what opens it: a colour declared in a module that
is neither of the two read here is measured by nothing and missed by nothing,
and a new chart-panel module holding a selection colour at 1.07:1 on the panel
passed with `0 errors`. Nothing exploits it today — no hex constant sits outside those
two files.

`agent_identity_check.py` does not survive, and its failure is worse than
silence. Rule 1 reads `self.X.disabled = EXPR` paired with
`self.X.visible = not EXPR`; PySide6 spells both as calls, so `property_writes`
returns nothing and the pairing loop runs zero times. On a tree where all six
identity controls are driven by `setEnabled()` with no paired hide it printed
"6 control(s) carry the agent colour, none of them rendered disabled" and
exited 0 — an affirmative claim about a tree it had not measured, which a
reader cannot tell from the same sentence earned. Whether it goes quiet turns
on a choice the port makes incidentally: porting the colour writes as well
trips rule 2 and moving the class trips the empty-set guard, so both of those
are loud, but rule 2 then misdiagnoses, reporting that the writer "never
writes" controls it writes through `setStyleSheet`.

So the port's cost side gains one entry rather than two, and it is specific:
rule 1 of `agent_identity_check.py` is inside the port's scope, and
`contrast_check.py`'s two read paths widen to whatever modules the decomposed
view declares colours in.

`tools/glyph_check.py` covers the half of presentation correctness that no
string assertion here can reach. Every such assertion compares text the same
font-less Python process produced, so the suite is blind to whether the client
can *draw* what it is given: `→` (U+2192) has no glyph in the Flutter client
and drew as a replacement box in the control-change list on 2026-09-04, in the
arrow of `5.60% -> 0.95%` — the direction of a setting change, which is the one
thing that line exists to state (`PL-8XPQ`). The rule is default-deny: every
non-ASCII character in a string that can reach a reader must appear in
`CONFIRMED`, whose entries each record what somebody rendered and saw. Per
character rather than per Unicode block, because Latin-1 Supplement admits `¤`,
`þ` and `ð` beside the `·`, `±` and `×` this interface has actually shown — a
block set would admit thousands on the evidence of three. It reads three trees,
not the one the item first named: `app/` draws the strings, `core/` raises the
text the view prints verbatim — `_apply_setting` renders `f"Setting refused —
{error}"` from a `SimulationConfigurationError` — and `data/` holds
`display_name`, which reaches the readouts and is the one place an edit lands
without touching Python. Documentation is exempt by a structural test, a string
that is a bare expression statement, which is what keeps `§` out of a list
meant to record what was rendered. Like the tools above it decides nothing
else: whether an unlisted character *would* render needs a real client, so it
refuses and never approves.

`tools/import_boundary_check.py` measures two claims the source makes about
itself. `_StrictPayload`'s docstring says that the `_...Payload`/public-
dataclass pairs exist so the rest of `core/` never imports Pydantic, and
`docs/MODEL.md` "The reproducibility guarantee" says that a run is a function of
its inputs and of the number of steps taken and of nothing else — so the run
loop reads no clock. Nothing checked either, so a leak into a compartment would
have left both paragraphs reading as verified while being false — worse than the
coupling itself. Its `BOUNDARIES` table is the specification, and the tool
decides nothing beyond it: which packages ought to be confined, and where the
exception belongs, are judgments written there with the reason beside them.
Three further states are errors, each closing a way the check could pass while
meaning nothing — an allowance naming a file that no longer exists, an allowance
no longer used, and a declared tree matching no source files at all.

The two boundaries cover different trees, and the asymmetry is deliberate. The
Pydantic boundary covers `app/` as well as `core/`, so the rule reads *exactly
one module in this package imports Pydantic*. The `time`, `datetime`,
`random`, `secrets` and `uuid` boundaries stop at `core/` and permit no module
at all, because the
guarantee they defend explicitly allows the interface its wall clock — what it
forbids is a tick's real duration reaching the run. A test pins that asymmetry
end-to-end, so widening the tree to the whole package would fail on an import
the design permits rather than passing quietly (`PL-J833`).

`tools/main_ci_status.py` is the one tool here that gates nothing, and the only
one that reads the network. `.github/workflows/quality.yml` runs the whole-store
`verify:` replay only on push to `main` — `PL-SDHR`'s decision, because a pull
request cannot have changed whether some *other* item's work merged, and
replaying the store on every branch costs more than it buys. The consequence is
that when that replay fails it fails on a run no pull request shows, and `main`
was red across three consecutive merges with every session believing the tree
was clean (`PL-0ZGK`). So the loop is closed from the reading end rather than by
making every branch pay to prevent it: `.claude/hooks/docket-digest.sh` calls
this at session start, and it prints one line when `main`'s last verdict was not
a success.

Two properties are what make it safe to run unconditionally, and both are held
by tests. **It is silent unless there is something to act on** — a green `main`,
no network, a non-GitHub remote and a malformed response all print nothing and
exit 0, because a line that appears every session trains a reader to skim the
region a real advisory occupies. And **a `cancelled` run is not a verdict**: the
workflow cancels superseded runs, so the newest completed run on `main` is
routinely one that judged nothing, and the tool reports the newest run that
actually reached a conclusion. It is unauthenticated — the repository is public,
so no token is read and none is needed, which keeps a credential off a
session-start path. The GitHub read deliberately does not live in `docket`,
whose rule is that a read must work from a bare offline tree.

`tools/ignore_check.py` covers what the type-check gate cannot. `[tool.mypy]
files` names `src`, `tools`, `.claude/hooks` and `subprojects/docket/src`, and every
`type: ignore` in the repository sits outside that set, so `strict = true`'s
`warn_unused_ignores` never read one. It runs mypy over `tests/` and
`subprojects/docket/tests/` separately and takes two things from the output: an
inert directive, and an unresolved import — which makes live directives look
inert, so it invalidates the answer rather than adding to it. The several dozen
type errors those trees report, which are why the gate excludes them, pass
unread. It is the guarantee `RUF100` gives for `noqa`, arriving through the
other tool.

It holds every markdown file in the checkout — not only the documentation
proper — to the math syntax GitHub renders. Two failures, both silent:
LaTeX's `\(...\)` and `\[...\]`, which CommonMark strips to bare
parentheses before any math parser sees them, and an expression split across a
source line break, which renders as literal text on both sides because inline
math is parsed within a line. `docs/MODEL.md` carried 97 of the first and
three of the second, its whole symbol table among them. Fences, code spans and
well-formed expressions are blanked before either rule runs, so writing
*about* the broken syntax is not writing it. Every markdown file is read
because rendering is not a claim held to the tree: a queue item renders on
GitHub like anything else, and seven of them had copied the broken form out of
`docs/MODEL.md`.

It also holds `ROADMAP.md`'s release-train table to a row grammar: each step
is a milestone carrying a version, a patch track, a numbered gate, or an
unnumbered marker, and the versions, gates and step numbers must run in order.
That table is the project's only statement of which milestone is current and
which is next, so it has to be readable by a tool rather than only by a
person — a hyphen typed for its em dash would otherwise reclassify a release
as a marker, silently. What the rows *mean* is not checked and is not
checkable: whether the prose beside a step is still true stays with the
reader.

The grammar itself lives in `subprojects/docket/src/docket/roadmap.py` and is
imported here. `docket wave` reads the same table to report which beat of the
planning cadence is due, and a second copy of the rules would drift from the
first silently — in the one document that says which milestone is current.

One thing it reports rather than checks: how many lines of instruction every
session loads before it has read anything — `CLAUDE.md` plus the
`.claude/rules/*.md` files carrying no `paths:` frontmatter — and whether that
total has grown against the default branch. Growth is an advisory, never an
error. A threshold would be met by deleting a rule to reach a number, and no
number the tool could hold would know which rules a session must see before it
reads anything; where each rule belongs stays with the reader, the way
`docket stranded` leaves its own judgment.

It also holds every count a frozen list states about itself to the entries in
it. `ROADMAP.md` states a release's list size in its group headings and in the
two table rows naming the release, and the same number reached six places
once; admitting four entries on 2026-09-01 meant correcting nine numbers by
hand, then eight of them again an hour later. Counts written in prose are
deliberately not read, because a checker cannot tell a claim about today's
list from a dated fact about the day it was frozen — so the prose states no
count, and the number lives only where its meaning is fixed by where it sits.

A frozen list can be internally consistent and still be missing entries, so
membership is read too, against the queue rather than against the file. The
gate rule makes one class of finding unconditional: an item classed `safety`
or `science`, or one at `P0`, re-enters the *current* gate however long after
the freeze it was noticed. Every other class turns on whether its problem
predates the freeze, which is a judgment. Only the unconditional half is
checked, and only in the direction that is decidable — an open item of that
class whose id the current milestone's section does not place, either on its
frozen list or under `Required scope`. What such an item should *become* is
left alone, so this reports as an advisory and names the three dispositions
rather than choosing one. It exists because the rule ran only when a session
thought of it: eleven qualifying items were filed in the two days after Gate
1 froze and none reached the list, while every count in the file agreed and
`docket wave` reported the written list correctly the whole time — 84 open of
121, holding no `P1` at all, since both classes are pinned to the top band
(`PL-KTKP`).

The same module reads `ROADMAP.md`'s *version* table, and `doc_check` holds
the three statements of the current version to each other: one row per
released version, exactly one marked the current baseline, a "Current
baseline:" heading naming that same version, and that version matching
`pyproject.toml`. A release bumps the version file and leaves the plan naming
its predecessor, which happened on two consecutive releases.

Tags *are* compared, in three directions: a completed release git holds no tag
for is an error, a release tag no version-table row names is an error, and the
roadmap's own count of deliberately untagged versions is held to git. What the
check will not do is speak when it cannot tell a missing tag from an unfetched
one — a check that fails on how somebody fetched the repository gets switched
off. So it says nothing when the checkout holds no tags at all, withholds the
findings a truncated clone could have invented, and says nothing about the
release being cut right now, whose tag goes on a merge commit that does not
exist yet (`PL-J295`, `PL-R7C0`). That last silence is safe because the version
stops being the baseline as soon as a newer one lands, and is an error from
then on — which is when an untagged release first costs anything. `docket
release` is the other half, refusing to cut a release while the previous one is
untagged, at the moment tags are certainly to hand.

Everything here depends on nothing outside the standard library and parses
under whatever bare `python3` is on PATH: `make check` invokes `python3
tools/doc_check.py check` directly, CI does the same, and both have to work in
a checkout with no virtualenv. That is why the floor these tools are held to is
**Python 3.11** — not the version `pyproject.toml` requires. The floor is not a
number chosen here: `doc_check.py` imports `docket.roadmap` for the release
train and `docket.config`, `docket.model` and `docket.store` for the queue, so
it is whatever `subprojects/docket/pyproject.toml` declares in
`requires-python`.

`.claude/hooks/` is held to the same floor for the same reason, and its
`ruff.toml` inherits the pin from `tools/ruff.toml` rather than restating it.
Claude Code invokes a hook as bare `python3` too, so a hook moved out of
`tools/` would otherwise be formatted at the repository's 3.14 target and
become unparseable by the interpreter that runs it.
`tests/unit/test_tools_portability.py` covers both directories by path rather
than by filename, so the guard follows the next hook without being extended.

Seven of them are nonetheless *invoked* under `uv run python`, and the
distinction is worth keeping straight, because it is about what a tool reads
rather than what it needs. `ignore_check.py` is the odd one and the only one
of the seven with a reason of its own: it shells out to mypy, so it wants the
virtualenv that gate runs in.

The other six are one reason repeated. `import_boundary_check.py`,
`contrast_check.py`, `agent_identity_check.py`, `workflow_paths_check.py`,
`core_vocabulary_check.py` and `glyph_check.py` each parse repository source
with `ast`, and that
source targets 3.14: `app/chart_series.py` declares `type PlottedSeries = ...`,
a PEP 695 statement added in 3.12 and so a `SyntaxError` to the 3.11 parser,
and `ast.parse`'s `feature_version` only narrows the syntax it accepts rather
than extending it. A tool that parses repository source can only run under an
interpreter that understands that source. All of them still meet the promise
above — standard library only, parseable at the floor — which is what the
portability suite holds them to, and it is why they stay in scope for it while
being absent from the CI floor section.

`contrast_check.py` is why the group is worth naming rather than left to each
tool's own docstring. It ran bare until `PL-L17Q`, green only because the two
files it reads happened to carry no 3.12+ syntax, so one PEP 695 generic added
to either would have failed the floor section on a tool nobody had touched. The
rule the six are an instance of is stated in
`tests/unit/test_tools_portability.py`'s module docstring, and a tool joining
them belongs on the `uv run python` lines in both `Makefile` and
`.github/workflows/quality.yml`, never in that workflow's floor section.

`tools/ruff.toml` is what keeps that true. The repository targets 3.14, where
PEP 758 makes the parentheses in `except (OSError, TimeoutError):` redundant,
so a 3.14-targeted `ruff format` removes them and 3.11 can no longer parse the
file — a break the test suite cannot see, because it runs under the project
virtualenv and only the bare-`python3` invocation fails. The file extends the
repository's rules and overrides `target-version` alone;
`tests/unit/test_tools_portability.py` holds it to the declared floor, holds
every file here to parsing at it, and holds every import here to the standard
library plus in-tree `docket` — the same failure one step earlier, since a
package resolvable only inside the project virtualenv is a `ModuleNotFoundError`
under bare `python3`. A tool added later inherits all three.
`subprojects/docket/` carries the same guards for the same reason.

All of those are approximations run under the project virtualenv — a syntax
gate rather than an older parser, and the wrong interpreter's
`sys.stdlib_module_names`. The floor section of
`.github/workflows/quality.yml`'s `checks` job performs the run they stand in
for: `actions/setup-python` at the declared floor, then
`python3 tools/doc_check.py check`, `python3 tools/branch_id_check.py`,
`python3 tools/rules_paths_check.py` and `bin/docket check` under it. It runs ahead of the uv install rather than in a
job of its own (`PL-D551`), which is what keeps the no-virtualenv claim true:
at that point none exists. `contrast_check.py` was there too until `PL-L17Q`
and is deliberately not now, for the input-versus-dependency reason above.
That decides syntax, imports and runtime behavior at once, with no list to keep
current. A fourth test holds that section's pinned version to `requires-python`, so
raising the floor cannot leave CI exercising an interpreter the project no
longer supports. The approximations stay because they name the offending file
and import, run before a push, and reach what those five commands never do.

## Wired hooks (`.claude/hooks/`)

The four scripts `.claude/settings.json` wires as hooks live in
`.claude/hooks/`, not in `tools/`, and the reason is a guard rather than tidiness.
`.claude` is a *protected directory* in Claude Code's own list, so a write to
anything under it is never auto-approved: it prompts, or in auto mode routes to
the classifier ([protected
paths](https://code.claude.com/docs/en/permission-modes#protected-paths), read
2026-09-05). A `permissions.allow` entry cannot lift that — the safety check
runs before allow rules are evaluated — so the directory is the guard, and
putting a hook anywhere else silently leaves it out. `stop_hook_patch.py` sat
in `tools/` until `PL-W4H9`, which is exactly the gap that item names: a script
that rewrites another hook, editable without review. `docket-digest.sh`,
`docket-branch-guard.sh` and `no-prune-guard.sh` are documented where their
behavior is, in their own headers.

`.claude/hooks/stop_hook_patch.py` is the one hook here that is not a check and
does not run under `make check`. It is wired as a SessionStart hook, and it
edits a file this repository does not own:
`~/.claude/stop-hook-git-check.sh`, which a cloud container writes at start and
runs at every `Stop`. That hook counts unpushed commits against
`origin/<branch>` whenever that ref *resolves locally*, so a merged branch's
surviving tracking ref makes it demand a push that would recreate a dead branch
identical to `main`. The correction counts commits held by no remote ref
instead. It is a hook rather than a patch the project owner applies because the
file is not theirs to change: a container rewrites it at every start,
user-level settings never reach a cloud session, and an environment setup
script runs before Claude Code launches and is skipped once the environment
cache exists. The script matches one whole line and rewrites nothing if it is
absent or doubled, so an upstream change is a clean miss that reports itself
rather than a partial edit to a script every stop executes. `PL-WW08` carries
the diagnosis and the measurements.

It does a second thing for the same reason, and the two are one job: counting
commits held by no remote ref only works if this checkout *has* such refs. The
harness clones with `git clone --depth 1`, which implies `--single-branch`, so
`remote.origin.fetch` names the default branch alone and `git push` never
writes `refs/remotes/origin/<branch>` — every commit on a pushed branch then
reads as unpushed however many times it has been pushed. The hook widens that
refspec, which repairs the clone rather than the test and keeps the stop check
offline instead of trading it for a network call at every `Stop`. It only ever
widens, and it neither fetches nor prunes, so it cannot destroy a ref
`bin/docket stranded` needs. `PL-3SGR` and `PL-483K` are the two reproductions.

## Tests (`tests/`)

- **`tests/unit/`** — one module's behavior in isolation (a compartment, a
  validator, a parameter loader, the controller, the displayed-value
  formatters, the view).
- **`tests/integration/`** — components wired together as the app assembles
  them (e.g. controller driving a full `AgentUptakeSystem`), and the Qt chart
  drawn headless against a real run (`test_qt_chart.py`), which reads the
  plotted items and the painted pixels back. `tests/conftest.py` selects Qt's
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

## Where new code belongs

- A new physiological compartment or coupling → `core/`, with its equations
  and reference cases documented in `docs/MODEL.md` first (per `CLAUDE.md`).
- A new agent, patient or machine profile → a new validated, cited file under
  the matching subdirectory of `data/`, not hardcoded values in `core/`. Where
  a compartment keeps a field default restating one of those values for bare
  unit construction, the default is pinned to the file by a test, as
  `test_the_bare_circuit_defaults_match_the_shipped_machine_file` pins
  `BreathingCircuit`'s.
- A new display panel or control → `app/simulation_view.py`, and the first
  question is *whose* it is. A panel stating a particular run's numbers -
  readouts, settings, transport, the record of what was changed during it -
  belongs to `RunView`, which is instantiated once per run, and the dashboard
  places it by looping over its runs. A panel about the chart both runs are
  drawn on - an axis, a legend, a reference, the time base, the compartment
  selection - belongs to `SimulationView`. Getting this the wrong way round
  is not a tidiness matter: a run's panel put on the dashboard would state one
  branch's numbers over both, and a shared control duplicated into each run
  would let a comparison be read under two different settings. Either way,
  read only what `SimulationSnapshot` already carries and what a recorded
  sample already records — a `SimulationHistorySample` holds its values per
  substance, under `RecordedQuantity`'s identifiers, rather than as named
  fields; if the UI needs a value that doesn't exist yet, add it in
  `app/controller.py`, computed in `core/`, never computed in the view. A
  panel wanting the run rather than the instant asks `history_window()` for
  the span it draws, and never for the whole run: what crosses that boundary
  has to stay bounded by the display rather than by the run's length.
- A new way of *rendering* a value a reader interprets — a unit, a decimal
  count, a marker for what the display cannot resolve → `app/formatting.py`,
  as a pure function with its own test, and with the reason recorded in
  `docs/MODEL.md` § "Displayed precision".
- A new chart series, or a change to how one is drawn → what it *claims* in
  `app/chart_frame.py` and how pyqtgraph paints it in `app/qt_chart.py`, with
  a new *compartment* trace declared in `chart_frame.COMPARTMENT_TRACES`,
  which is where the quantity it draws, how it is drawn, the legend words that
  name it and the gloss its hover carries are written as one record; the Flet
  dashboard's `_traces` table is built from that one and leaves with
  `PL-7SVX`. The table is the chart's rather than any one run's: each run builds
  its own line from it (`_CompartmentTrace.build_line`), because a line holds
  points and the points are a run's. `RunView._plotted_series` pairs that
  table with the substance the frame is drawing — the agent its own snapshot
  names, since the run is recorded under that identifier — and
  `RunView._visible_plotted_series` is the subset a frame draws; neither is
  edited directly. A series that draws no recorded sample — a
  clinical reference, a control mark — stays out of that table by
  construction, and owes the labelling requirement `docs/MODEL.md`
  § "Interface boundary" puts in place of the sample rule instead. So does a
  trace of a *derived* quantity with a domain, such as the wash-in ratio: the
  table binds a line to one recorded field, and a value that is sometimes
  absent has no such field to be bound to. It owes its domain in
  `docs/MODEL.md` and at the point of display instead.
