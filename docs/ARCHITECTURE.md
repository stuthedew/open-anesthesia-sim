# Architecture overview

This document describes how the code is organized and how data flows through
it. It is a map for contributors, not a scientific specification. For the
equations, units, parameter provenance, and numerical method, see
[`docs/MODEL.md`](MODEL.md). For version history and milestones, see
[`ROADMAP.md`](../ROADMAP.md).
[`docs/interface-provenance.md`](interface-provenance.md) records where the
interface's area and workspace model comes from. It says which parts of
Blender were studied, under which licence rules, and what this project
deliberately does differently.

## Layering

The codebase is split into independent layers. The direction of imports
enforces the split, and `tools/import_boundary_check.py` checks it at every
`make check`. Never edit code to get around that check.

```text
data/  --loaded by-->  core/  --read by-->  app/
                                             ^
                    layout/  --read by-------+
```

- **`core/`** is the scientific simulation. It has no dependency on the UI
  toolkit, no wall-clock time, and no I/O beyond reading the packaged JSON
  files in `data/`. Every quantity it produces is deterministic for identical
  inputs.
- **`app/`** is the PySide6 user interface. It never performs a physiological
  or unit calculation itself. It only reads immutable snapshots from `core/`,
  through a thin controller, and renders them. It forwards user input back as
  setter calls.
- **`layout/`** is the area layout as a value. It records which View occupies
  which part of each window, and it provides the operations a reader performs
  on the layout (`PL-C842`, `PL-1FT6`). It imports no toolkit, which
  `tools/import_boundary_check.py` enforces, so every operation is tested
  without a `QApplication`. The only part of `core/` that it reads is
  `core/checked_number.py`, for the way that module names a refused value.
  Its `store.py` is the one module in the package, and the first under `src/`,
  that writes outside the tree. It writes the reader's saved Workspaces, as
  described under § "User state: the saved Workspaces" below.
  `app/area_layout.py` builds the widget tree from the layout (`PL-W9P6`).
  `app/view_registry.py` is the one list of the View kinds that a layout may
  name (`PL-R1WQ`), because the `layout/` package holds no such list.
- **`data/`** holds versioned, schema-validated parameter files (JSON) with
  citations. The files come in three kinds: the agent, the patient, and the
  machine in front of them. Every scientific constant that a shipped run uses
  comes from one of these files. `AgentUptakeSystem.for_agent()` passes each
  value explicitly, so no shipped path uses a compartment's field default.
  The defaults are still written in `core/`, so that a unit can be constructed
  bare. A test pins each default to the data file that is its authority.
  `PL-4YY1` added the machine file and the first of those pins. It did so
  after finding that the circuit's volume and flow were taken from
  `core/circuit.py`. That made them invisible to `tools/doc_check.py`'s
  provenance walk, which can only see a constant that has entered a data file.
  `data/workspaces/` holds the shipped Workspaces. These are layout rather
  than parameters: `layout/shipped.py` reads them, and nothing in `core/`
  does.

Three rules rest on this layering, and this section is where the first one is
stated. The first rule is that simulation code stays independent of the UI
toolkit. `tools/import_boundary_check.py` rejects a toolkit import under
`core/` and a `core/` import of `app/`. The rule was a `CLAUDE.md` bullet
until `PL-ZYHX` retired the bullet in favour of that check on 2026-10-17. The
second rule is that no simulation calculation belongs in a UI callback.
`.claude/rules/ui-calculations.md` states that rule, and it loads with every
file under `app/`. The third rule is that model parameters live in validated,
versioned data files and never as executable code. `CLAUDE.md`
§ "Architecture and development discipline" keeps that rule, and the typed
payloads in `core/parameters.py` reject a formula where a number is expected.

## Package map

```text
src/anesthesia_sim/
├── app_metadata.py      # app name, bundle id, and the version the header shows: the installed distribution's version, plus the commit where the running code is not a clean checkout of the released tag, because between two releases every build otherwise displays the same string and a fix confirmed by eye cannot be told from the code it replaced
├── core/                # scientific simulation — no toolkit dependency
│   ├── validation.py              # shared input-validation guards (raise SimulationConfigurationError; a value that is not a number at all is a TypeError, as for every checked type)
│   ├── checked_number.py          # what a checked type, and the two sign-and-finiteness guards in validation.py, are built from: an int or a float and nothing else, never a value built as another checked quantity, with minus zero held as zero; the base every checked type shares; and how a refusal names a value
│   ├── concentration.py           # fraction vs percent: the two forms, and the only crossing
│   ├── units.py                   # seconds, minutes, hours, milliseconds, and litres to millilitres and cubic metres: the factors between them, each written once
│   ├── supported_ranges.py        # the declared domain: FreshGasFlow, AlveolarVentilation and CardiacOutput, which cannot hold a flow outside it, CaseInstant, which cannot hold an instant outside the run length, StepCount, a whole nonnegative count, and the guards that refuse a run outside it
│   ├── simulation_step.py         # the run's step: its supported range, and SimulationStep, which cannot hold one outside it
│   ├── numerical_envelope.py      # where core's arithmetic is shown correct: CompartmentVolume and PartitionCoefficient, which cannot hold a volume or a coefficient outside it, and the one place the tissue:blood quotient is formed
│   ├── exceptions.py              # exception hierarchy; every core failure is inside it
│   ├── parameters.py              # load + validate agent/patient/machine JSON data
│   ├── liquid_agent.py            # the 20 °C reference condition's molar volume, LiquidDensity, and the conversion of an amount of vapour into the millilitres of liquid agent it came from (PL-KZ99)
│   ├── circuit.py                 # breathing circuit compartment
│   ├── alveolar.py                # alveolar gas compartment
│   ├── blood.py                   # venous blood compartment
│   ├── tissue.py                  # one perfusion-limited tissue group
│   ├── exponential_approach.py    # the first-order approach to a held input that blood.py and tissue.py advance their amount by, and circuit.py its fraction, which is what the circuit stores: formed from the value held for a step closing up to half the gap and from the equilibrium beyond, exact at zero flow and at a full approach
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
│   ├── unconditional_set.py        # docs/MODEL.md's unconditional set as data: UnconditionalValue, its tiers, SubstanceInstance and INHALED_AGENT, read by the region that holds it (PL-NWTM); window_region, what each top-level window's region owes (PL-W54S); toolkit-independent
│   ├── control_record.py           # what a run's settings are addressed by and the change a run records: ControlInput, CONTROL_INPUT_DISPLAY_UNITS and CONTROL_INPUT_UNITS, ControlChange; toolkit-independent
│   ├── display_units.py            # DisplayUnit: each unit the interface states, with its recorded spelling, the label beside a value and its chart axis title, so the record, the panel, the formatters and the chart read one member (PL-G84G); toolkit-independent
│   ├── bookmarks.py                # what a learner marks a case at, held in two collections: TimeBookmark (an instant), MacTarget (a height on one compartment), BookmarkSet; toolkit-independent, and it detects a crossing between two readings it is handed, which SimulationController.advance supplies each step
│   ├── simulation_view.py          # SimulationView on PySide6: what runs share - the unconditional region above the layout container, which refuses a run lacking a declared value, the compartment selection every View is shown, the chart frame a tick assembles for each window a chart View asks for (PL-L59K), the case section of bookmarks and branching under the Areas, the render tick, and the Workspaces: the tab strip over the Areas switches among them, and a pinned Workspace's Views draw its run alone (PL-2KXB); no domain logic
│   ├── area_layout.py              # AreaLayout: the one module that builds QSplitters, every one from a layout.LayoutModel; a drag on a border becomes LayoutModel.resize and every splitter follows the new model (PL-W9P6), stopping in WARNING at an Area's least size, moving one border alone with Shift and undone by Escape; a border in the tab order moves one step per arrow key, and the Area menu's Resize entry gives one the focus (PL-M352); a right-click on each Area's header opens an AreaMenu that splits, joins, swaps or closes it, and a corner drag splits or joins it, or with Ctrl swaps it, with a preview drawn over the Areas (PL-2KXB, PL-R5G4); each Area is an AreaFrame whose header holds a ViewChooser listing every registered kind, and a choice is LayoutModel.set_view (PL-50PZ); each Area's View is built by its registry entry's factory, saved when replaced, and drawn from each ViewTick (PL-TH35); an Area whose View kind is not registered, or whose factory fails, shows an AreaNotice instead (PL-R1WQ); no View is drawn below its need, and an Area that cannot be given it shows the size it needs (PL-K285); load draws another Workspace from its layout and View state, and a pinned Workspace's run is named in every Area's header, or stated absent in place of each View (PL-2KXB)
│   ├── workspace_tabs.py           # WorkspaceTabs: the Workspace tab strip above the Areas, drawn from a WorkspaceSet it does not own; shipped tabs first, a rule, then the reader's own; each tab's menu entry worked out before it is shown, Delete and Reset asking first, and rename in place (PL-QW1Z, PL-2KXB); a Layout menu, opened by a right-click on the strip outside a tab, lists every Workspace and holds the current one's entries, and Ctrl+PgUp and Ctrl+PgDn step through them (PL-M352, PL-R5G4); it and each tab's menu end with Save as default, Restore shipped Workspaces and Reset all layouts, and a line under the tabs shows what the store reported (PL-DWHG)
│   ├── view_contract.py            # the View contract every View implements: the View protocol, the ViewContext it is built from, the FrameRequest naming the window and width it draws, the ViewTick it is drawn from, ViewRequests for a change to shared state or a frame, and the saved-state version check (PL-TH35)
│   ├── views.py                    # the shipped Views, each a QWidget satisfying view_contract.View: ConcentrationView, WashInView, ParameterControlsView and AccountingView (PL-TH35); each chart View holds and saves its own time window and writes the lines that depend on it from its own frame (PL-L59K)
│   ├── view_registry.py            # the View registry: each View kind's tag, written once as a literal, its RegisteredView entry with the factory that builds it, and RETIRED_TAGS for a tag renamed or removed; REQUIRED_REACHABLE, the kinds a build fails on import without (PL-50PZ); the text of the missing-kind and failed-build notices (PL-R1WQ)
│   ├── run_view.py                 # one run's widgets, controller, handlers, refresh and halt; RunView, instantiated once per run (the seam PL-B9PY drew)
│   ├── halt_gate.py                # halt_gate: every slot of RunView and SimulationView is called through it, so a raise inside one halts its run, or every run for SimulationView, rather than escaping to Qt (PL-HJKN); toolkit-independent
│   ├── run_surfaces.py             # the two parts of a run that may sit in an Area, each built any number of times from the values it draws: ParameterControls, AccountingPanel, and keep_until_destroyed, which keeps the list of live copies RunView writes (PL-9LNF)
│   ├── qt_widgets.py               # PySide6 leaf widgets that decide nothing: MetricPanel, ReadoutRow, ParameterSlider, NoticeLabel, NewCaseDialog, BookmarksPanel, ForkPanel, initial_window_geometry
│   ├── formatting.py               # modeled value -> displayed string; toolkit-independent
│   ├── playback.py                 # playback rate -> whole simulation steps per tick; toolkit-independent
│   ├── dashboard_frame.py          # what the dashboard claims about one run at one instant, as plain values: the status word, the notice and its precedence, the readouts and their glosses, the setting controls, the transport enablement, the accounting panel, the control-change list, the captions and the new-case question; toolkit-independent
│   ├── chart_frame.py              # what one frame of the plots at one time window draws, as plain values: the trace table, the window, the axes' ticks, the references, the marks, the wash-in stretches and the hover text; toolkit-independent
│   ├── compartment_selection.py    # CompartmentSelection: which compartments the chart draws, as a value the dashboard owns and the legend shows (PL-VN6M); held inside the compared cap, and a reader's click over it drops the longest-standing; toolkit-independent
│   ├── qt_chart.py                 # the concentration chart, the wash-in plot, the legend and the time base selector on pyqtgraph and Qt, moved per frame to match a chart_frame.ChartFrame, the legend showing a CompartmentSelection and the selector a time base it is handed; each chart says when it owes a frame at a wider width (PL-9LNF); declares no colour and formats no value
│   ├── chart_time_base.py          # how wide the chart's window is and how it is ruled; toolkit-independent
│   ├── control_timeline.py         # recorded control changes -> the acts a reader sees; toolkit-independent
│   ├── wash_in.py                  # F_A/F_I and the domain it holds on; toolkit-independent
│   ├── theme.py                    # every display token: palette, cited ISO 5360 agent colors, type sizes, spacing, dash patterns; toolkit-independent
│   ├── stylesheets.py              # every stylesheet a widget is given, composed from theme.py's tokens, so each visual decision is written once; toolkit-independent
│   └── main.py                     # PySide6 entry point; loads the reader's saved Workspaces from their data directory (PL-DWHG), builds the BranchedCase and opens the dashboard over its trunk; the window opens maximized (PL-Z4K6) over a sized, centred normal geometry (PL-005)
├── layout/               # the area layout as a value: which View occupies which part of each window - no toolkit dependency (PL-C842, PL-1FT6)
│   ├── tree.py                     # the values a layout is built from - AreaId, ViewKind, Area, Split, Window - each refusing what could not be one, and the one form a tree takes
│   ├── sizing.py                   # how a layout is drawn in whole pixels: each Area held at its View's need, its siblings giving way, and which Areas are too small and held at their header instead (PL-K285); pure functions of a tree and an extent
│   ├── model.py                    # LayoutModel: every window's tree; split, join, resize, swap and set_view, each returning a new layout; the borders() line a drag moves
│   ├── serialization.py            # the layout, a Workspace and the set of them as JSON: each body, and the versioned documents - the set's is the file the application writes
│   ├── workspace.py                # Workspace and WorkspaceSet: a named layout with each View's saved state per Area and kind and the run it is pinned to, and the ordered set a reader works in; removing the last Workspace is refused by the type (PL-WV9K)
│   ├── run_identity.py             # RunId, a run's identity as the session that placed it and its number there, and RunIdentities, the session's counter; what a run is called and what a Workspace pins (PL-7Z84)
│   ├── migrations.py               # SchemaVersion, a version checked once when it is read (PL-8JV2); LAYOUT_SCHEMA_VERSION, and the steps that read a set document an older build wrote, each one version; version 2 added each Workspace's pinned run, and the chain is checked at import (PL-SSQW Q5, PL-7Z84)
│   ├── store.py                    # WorkspaceStore: the reader's workspaces.json - the atomic save on "Save as default", and what a launch does with a file that is missing, older, newer, invalid or unreadable, none of it silent (PL-SSQW)
│   ├── shipped.py                  # the shipped Workspaces read from data/workspaces/ by the reader the learner's file goes through, one file per Workspace, held to the current schema_version (PL-KXTL)
│   └── exceptions.py               # what the package refuses, and what each refusal means to a caller
└── data/                 # versioned, cited parameter files, and the shipped Workspaces
    ├── agents/{sevoflurane,isoflurane,desflurane}.json
    ├── machines/reference_circle_system.json
    ├── patients/reference_adult.json
    └── workspaces/{default,induction,maintenance}.json
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

`core/parameters.py` is the only module that reads the JSON files, which it
does through `importlib.resources`. Before it constructs `AgentParameters` /
`ReferenceAdultParameters` / `BreathingCircuitParameters`, it validates the
schema version, the required fields, the units, and the ranges. The schemas
are strict at every nesting level. A key that the schema does not declare
fails the load rather than being silently discarded. As a result, a data file
cannot document one model while the app runs another. Nothing downstream
re-reads these values from disk or derives them again.

**Each simulation step**, `AgentUptakeSystem.advance()` advances the whole
coupled system at once. It does so by one exact propagation, rather than by a
sequence of sub-exchanges or a generic numerical integrator:

1. `core/governing_equations.py` assembles the system matrix `A`. Each entry
   is one term of one balance equation in `docs/MODEL.md`,
   "Governing equations".
2. `core/matrix_exponential.py` computes `exp(A dt)`. This is the system's
   exact propagator, because every setting is held constant across a step.
   The result is cached against the settings it was built for, and it is
   rebuilt when one of those settings changes.
3. One matrix-vector product advances the six fractions. The same solution
   also advances the cumulative delivered and exhausted amounts.
4. The agent-accounting validator (`AgentSimulationValidator`) records those
   amounts and checks mass balance. It raises
   `AgentSimulationValidationError` if the check fails. The error carries the
   failing check, because the step is then rolled back and the run's own
   accounting no longer holds the rejected step's totals (`PL-HF4B`).

Steps 1 and 2 carry the split of concerns that the package is arranged
around. The equations file contains the physiology and no arithmetic. The
exponential file contains the arithmetic and no physiology.

**UI direction:** `app/controller.py`'s `SimulationController` owns a
`SimulationState`. It exposes `start()` / `pause()` / `reset()` /
per-parameter setters, and it produces an immutable `SimulationSnapshot` on
request. It has no default values and no bounds of its own. Every unspecified
setting comes from what `AgentUptakeSystem.for_agent()` built from the data
files. Suppose the core rejects a setting, such as a delivered concentration
above the agent's vaporizer maximum. Then the error is raised out of the
core, and the controller does not clamp the setting or replace it with a
default at this boundary.

Conservation of agent belongs to the core on the same terms. Until PL-006,
the controller read the circuit's stored agent out and put it back around
`set_circuit_volume`. That left `core/` exposing a public primitive that did
not conserve agent. The invariant was kept only by the one caller that knew
to compensate. Now the core setter conserves agent. The controller calls it
once, from `_build_state()`, to apply the volume the session was built with.
No live setter exists above it. PL-GYH2 established the circuit volume as a
fixed model parameter rather than a control. So the per-parameter setters
named above are the four that the interface offers, and no fifth one exists.
`docs/MODEL.md` § "What is not bounded this way" gives the argument.

The snapshot is the run's state at one instant. It holds a fixed number of
values, however long the run has been going. The run as a whole is returned
separately, by `drawn_window(start_s, stop_s, columns)`. That method
evaluates the states at the instants that a chart is about to plot, across
the axis the caller names, and returns them as a `DrawnWindow`. The snapshot
and the run were one field until PL-0VM7. Before then, the snapshot carried
every sample that the run had recorded so far. A frame's cost therefore grew
with the length of the run, while the chart discarded all but the few hundred
samples inside its axis. PL-2FM6 later removed the record itself. The
snapshot does carry the run's `ControlChange` timeline. The timeline has one
entry per setting that the model was actually stepped under. Re-applying the
timeline therefore reproduces the run rather than approximating it. The
length of a timeline is bounded by how often a user touches a control, not by
how long they watch.

**A run is its inputs, and its states are derived from them** (PL-T691).
The controller holds the run as a `core/run_definition.py`
`RunDefinition`. The definition holds the settings in force at each moment,
plus one keyframe per change, and nothing else of the run. A keyframe is the
state at the instant of its change. (The chart's evaluation keeps the
propagators that its last window used, so that the next frame can reuse
them. Each propagator is a function of settings that the definition already
holds, so no drawn value depends on whether it was kept:
`RunDefinition.evaluate_anchored`, PL-CNCF.) The equations are linear and
time-invariant while the settings stay the same. So the propagator is exact
over any horizon, not only over a step. Every state that the run passed
through is therefore one propagation from the keyframe that brackets it, and
none of those states has to have been recorded.
`RunDefinition.evaluate(start_s, stop_s, columns)` and
`evaluate_anchored(start_s, stop_s, spacing_s)` perform that evaluation. The
second is the one the chart uses, reached through
`SimulationController.drawn_window`. `run_segments` hands out the record
itself as frozen segments, which can be read but not advanced. So nothing
above the controller can move the run definition's reach past where the run
actually got to, and then have a prediction drawn back on the run's own axis.
`docs/MODEL.md` § "The run is that record, and every state is derived from it"
gives the measurements. § "The canonical evaluation rule" states which of the
two evaluation paths a stored, exported, replayed or branched value may be
taken from.

**That boundary is a type rather than a convention.** `evaluate` and
`evaluate_anchored` return `DisplayState` values, which are not state
vectors. So a drawn column cannot become a keyframe, an exported figure or a
branch's opening state just because it holds the same nine numbers in the
same order. `RunDefinition` rejects such a value as an opening state by name.
A layer above the controller therefore cannot cross that boundary by
forgetting that it is there. Forgetting is the only way that a boundary
stated in prose is ever crossed.

There is one record. Until PL-2FM6 landed in v0.4.12, the controller kept a
per-step sample history beside the definition, and the chart drew from that
history. `docs/MODEL.md` § "Closed-form agreement test" held the two in
agreement with each other. That change deleted the history, because the run
definition is the run and the samples were a second copy of it. What the
chart draws now is what `drawn_window` evaluates. Nothing exists behind those
states that could disagree with them.

`app/run_view.py` and `app/simulation_view.py` read only the snapshot and
`drawn_window`. A `RunView` builds one run's controls, and it wires the
slider and button callbacks through `_apply_setting` to the controller's
setters. The `SimulationView` drives the charts that every run shares.
Neither performs a physiological or unit calculation of its own. Each
transformation that they do apply is a module of its own. That is because
each one is a question of presentation *correctness* rather than of layout,
and each must be readable and testable with no toolkit loaded.

`app/formatting.py` turns a fraction into the strings a reader sees: a
percent, and a multiple of the running agent's 1 MAC. It uses the
resolutions that `docs/MODEL.md` § "Displayed precision" derives.
`app/chart_frame.py` settles, as plain values, what one frame of the chart
claims. That covers which compartment a curve carries, which instants are
drawn, where the references are placed, and what a hover says.
`app/qt_chart.py` moves pyqtgraph items to match that frame.
`app/dashboard_frame.py` does the same for everything beside the plots: the
status word, the notice and its precedence, the readouts, the setting
controls, the captions, and the two bookmark listings. `app/qt_widgets.py`
moves the leaf widgets to match it, and decides nothing.
`app/control_timeline.py` turns the recorded control changes into the
adjustments a reader sees. `app/playback.py` turns the playback rate that a
reader selects into the number of whole simulation steps that a tick takes.
`app/wash_in.py` divides the alveolar fraction by the inspired one.

The last three are correctness questions, for reasons worth stating. The
control record is faithful to the run, and a drag of one slider appears in it
as several settings. So collapsing that drag into one displayed act is a
claim about what the user did. It is not a tidier rendering of what the
model saw. The wash-in quotient has a domain. It is undefined before any
agent reaches the circuit, and above 1 it stops being a wash-in fraction. So
the module returns the value and the reason together, and the chart draws
the trace in segments that break where the domain does. `docs/MODEL.md`
§ "F_A/F_I as a displayed ratio" is the specification. A playback rate is
realised only as a step *count*, never as a larger step. So the module
derives the count from the rate, and it rejects a rate that does not land on
a whole number of steps. The alternative is a run that advances at a rate
other than the one it displays. That would be a presentation failure that
looks like a working feature.

The MAC divisor is passed to the formatter as an argument, from
`SimulationSnapshot.agent_mac_percent`, rather than being looked up. The
divisor is what makes a displayed multiple specific to the agent, so it
travels with the value it divides. The agent's MAC-awake travels the same
way and for the same reason, as `SimulationSnapshot.agent_mac_awake` beside
that divisor. The chart's MAC-awake band is one of these values multiplied by
the other, so pairing two different agents' values would place a correct
number at the wrong height. A reference is placed by `app/chart_frame.py` and
drawn by `app/qt_chart.py`. It is deliberately not a member of
`chart_frame.COMPARTMENT_TRACES`, the table that maps traces to compartments,
because a reference reads no state of the run. A control mark is a third kind
of series on the same terms, for a stronger version of the same reason. It
draws no value at all, only a simulated time, and it is likewise outside that
table.

**Failure direction:** every failure that `core/` reports is a subclass of
`AnesthesiaSimulationError` (`core/exceptions.py`), never a bare
`ValueError`. That lets the interface recognise a simulation failure and act
on it. The hierarchy has two branches, which mean different things and get
different treatment:

- `SimulationConfigurationError` means that a value was rejected before it
  changed anything. The guards in `core/validation.py` raise it. So do the
  checked types' constructors (`Fraction`, `Percent` and `MacPercent` in
  `core/concentration.py`, and those in `core/supported_ranges.py`,
  `core/simulation_step.py` and `core/numerical_envelope.py`). Compartment constructors and setters raise it
  too. So does a compartment field written directly, because its record
  checks every write in `__setattr__` (`PL-19Y0`). The parameter-file loaders
  raise it as well.
  The view's `_apply_setting` catches it, restores the control from the
  snapshot, and says that the setting was refused. The run is untouched and
  keeps going.
  Three cases raise `TypeError` instead, as a programming error rather than a
  refused setting. The first is a setter, or a compartment field written
  directly, that is handed a value not built as its type. The second is a
  checked type built from something it does not accept. That means a `bool`,
  a `Decimal` or a string for any checked type, and a `float` for
  `StepCount`, which is built from an `int` alone. For all of them, it also
  means a value already built as another checked quantity. The checked type
  raises before it reads the range (`core/checked_number.py`). The third is
  the two sign-and-finiteness guards in `core/validation.py`. They also
  reject an `int` past the float range by name. They do not let
  `math.isfinite` raise `OverflowError` while converting it (`PL-3800`).
  A concentration that the display builds is not a setting. If one is
  refused there, the run halts. No supported setting causes such a refusal
  (`PL-7DJK`).
- `SimulationExecutionError`, with its `SimulationNumericalError` /
  `AgentSimulationValidationError` subclasses, means that a step began and
  could not be completed, so the run must stop.
  `AgentUptakeSystem.advance()` is what makes this distinction. It checks its
  own arguments first. Then it restates any guard failure raised during the
  step as a `SimulationNumericalError`, and it keeps the original as
  `__cause__`. It is also what makes the step atomic. It captures every
  dynamic value before the step and restores them all on any failure. So
  what is left behind is the last completed step, rather than a state vector
  written into some compartments and not others.
  Each compartment captures its own state (`capture_state()` /
  `restore_state()`). So a dynamic field added without a matching capture is
  an omission local to that compartment. `docs/MODEL.md`, "Step atomicity",
  is the contract.

Both timer slots pass the halt gate, as every other slot does (`PL-HJKN`).
`RunView.step_tick` steps the run and `SimulationView.render_tick` presents
it, and both halt on any exception: the first halts its run, and the second
halts every run. They do so because a `TypeError` from a refactor is exactly
as silent inside a Qt slot as a modelling failure is.
`dashboard_frame.halt_disposition` decides which halt applies, and
`RunView.halt` routes by its decision. A failure goes through
`SimulationController.fail()`. A `SimulationDomainLimitError` raised on a path
that the controller does not step itself, such as a setting, goes through
`halt_at_supported_limit()`. A run that steps onto the supported run length
meets no exception. `SimulationController.advance()` halts it on the step that
arrives there, and the snapshot reads the limit from the run's own state. So a
run that is forked or reset onto that step is also treated as stopped there
(`PL-5291`).

`fail()` sets a third run state. The snapshot carries it as `failure_reason`,
and the dashboard renders it as "Stopped — simulation error" with a banner over
the values. A halted run must never look like a pause, because a pause is a run
that continues when asked and a halt is a run that cannot continue. `RunStatus`
carries both halts, and the snapshot extends `RunStatus`.
`RunView.present_halt` states a halt from `SimulationController.record()`,
which returns a `RunRecord`, and `RunRecord` extends `RunStatus` in turn.
`present_halt` does this without building any compartment value, because the
snapshot's own `Fraction`s are among the values that can cause a halt. The
banner it writes, `dashboard_frame.halt_notice`, says that no frame of the
stopped run has been drawn. `refresh` replaces that banner on the first frame
that draws (`PL-7DJK`).

The supported-limit halt is a fourth run state, distinct from the failure. The
snapshot carries it as `supported_limit_reason`, and the status reads
"Stopped — supported run length reached" in place of the failure wording. It is
kept separate because nothing went wrong. The run stands on a completed step,
at a time the model claims to represent, and the next step would be refused in
exactly the same way. Neither halt can be resumed. A halt is cleared only by
`reset()` or by starting a fresh run with `set_agent()`. But `reset()` can
itself refuse, when the settings record is one the definition cannot open on.
It refuses before it clears anything. `RunView._handle_reset` halts the run on
that refusal through the same path (`PL-M4M0`). In every other halt, the banner
names reset as the way out. So this banner says instead that no setting can
repair the refusal, and that closing and reopening the application starts a new
run (`PL-01GY`).

A control used on a run whose snapshot refuses meets the same halt, rather than
an exception that the toolkit prints. Every slot of `RunView` and
`SimulationView` passes `app/halt_gate.py`'s `halt_gate`, which turns any
exception raised inside the slot into a halt (`PL-HJKN`). A `RunView` slot halts
its own run through `_halt_run`, and a `SimulationView` slot halts every run,
because it acts on the case. `_halt_run` restates the halt from `record()`. So
on a run whose snapshot refused, the agent selector goes back to the agent that
the record names. The snapshot cannot name it, because the snapshot is what
refused (`PL-V2HC`). Before `PL-HJKN`, each slot was put behind a `try` by
hand, and six were found outside it, one review at a time.
`test_every_slot_that_touches_a_run_passes_the_halt_gate` now fails on a
connected slot that does not pass the gate.

Every widget that states what the run holds is written by one writer.
`RunView._write_statement` writes the status word, the transport, the agent
identity, the four dials, the control-change panel and the banner from
`dashboard_frame.run_statement`. Both `refresh` and `present_halt` call it, so
on each of these widgets a halted run shows what a frame would show. A dial
dragged into the halt shows the value the run holds, rather than the value from
before the drag (`PL-85LJ`). An agent changed just before the halt is named on
every identity widget (`PL-1YDD`). The control-change panel lists the record
that the run holds (`PL-DTJQ`). Some things only a frame can state: the
readouts and the clock read with them, the accounting panel, the off-scale and
wash-in lines, and both legends. These stay as the last frame drew them.
Values shown together still describe one step. After a halt that no frame
has drawn since the run started over, by a Reset or an agent change, each
readout card and the clock withhold their values, and the accounting panel
withholds its verdict and amounts. After an accounting halt, the accounting
panel shows the rejected step's check, whether or not a frame draws. A stopped
run refuses a dial, so the dials keep the settings the run holds (`PL-3B34`).
`test_every_value_and_its_qualifiers_on_screen_come_from_one_state`
checks each value and what qualifies it against one step (`PL-J5GC`).
`test_every_run_state_widget_reads_alike_on_a_drawn_run_and_a_halted_one`
requires every other widget to follow the halt by default. So a widget added
later is checked without anyone listing it (`PL-X7D5`).

The legends are told what a frame drew only once both plots have drawn it. So
when the frame that a click asked for fails, the legend boxes still name the
curves on the plot (`PL-G3K7`). `SimulationView._halt_every_run` restates the
branch controls from the case, so a failed trunk offers no branch from where it
stands (`PL-MMNX`). It also restates the bookmark standings from each run's
controller. So a mark that the failed run will never reach is not listed as
still to come (`PL-YHR3`). Both of these panels, and the marks editor with the
bookmark panel, are restated from one list, `SimulationView.halt_restatements`.
`test_every_dashboard_control_is_restated_on_a_halt` fails on any dashboard
control that is not covered by a run, a listed panel or a named exemption. So a
panel added later is checked without anyone having to remember it (`PL-5JTH`).
The trunk records that its dashboard failed, so it then also offers no keyframe
and no passed mark. A branch opened at one of them would be drawn by the same
dashboard, which could fail the same way. A raise in one of the dashboard's own
slots is recorded the same way as a frame that fails, because it too belongs to
no single run (`SimulationController.record_failed_frame`, `PL-T2Q2`, `PL-HJKN`).

A run can stop itself inside its own step tick, on a mark or on arriving at the
supported run length. Such a run asks for no frame, and nothing else needs to
ask for one. The render tick draws whenever a displayed run's `record()`
differs from the one its view last wrote (`RunView.owes_a_frame`). It also
draws when the set of runs differs from the set it last drew over. Each view
stores the record at the moment it writes it, `present_halt` included. So a
frame that keeps failing is attempted once rather than on every tick
(`PL-X7D5`, `PL-T995`). Neither timer stops on either halt. Both timers are
started once, when the window opens. A halted run leaves them firing and
finding nothing to do. So a run that is reset and started again is stepped
without anything having to be restarted.

Drawing that full record on every frame is what made the render payload grow
with the run's length. The run no longer keeps a record to draw.
`core/run_definition.py` returns the state at any instant in closed form. So
the view asks the controller for the states at the instants it is about to plot
(`SimulationController.drawn_window`), and there is nothing to subset. Which
instants those are is a presentation-correctness concern. A chart that stepped
over a control change would show a curve the simulation never produced. So the
rules that place the instants are stated in `docs/MODEL.md` §
"What the chart draws" and are tested on their own. The evaluated instants are
anchored to an absolute grid measured from the case's zero, rather than to
their position within the window. So a window that follows the run keeps every
column it had and gains at most one (`RunDefinition.evaluate_anchored`).
PL-Q197 established this rule for recorded samples. At that time the Flet
client was patched per point, so every shifted column was a changed point.
PL-2FM6 carried the rule over to evaluated columns.

`app/chart_frame.py` is the layer above that anchored evaluation. It holds the
rule of one column per pixel and that rule's minimum column count
(`chart_columns`). It reads the window once per run for every trace, and
converts each drawn value into the unit of its own axis. It is a separate layer
for the same reason that the rules placing the instants are tested on their
own: which quantity a line carries is a correctness claim. That claim is
declared once, in `chart_frame.COMPARTMENT_TRACES`, beside the traces
themselves. The unit conversion belongs to the layer that knows the axis. The
six compartment traces are drawn in percent, and the wash-in ratio in its own
dimensionless unit. Stepping and drawing also run on separate timers at
separate intervals. So simulation time stays a function of the steps taken
rather than of how long a frame took.

## What a branch is, and what it shares with its parent

A **branch** is a second live run of the same case, opened at a state the first
run passed through. The run it was taken from is the **trunk**. The whole
structure is one trunk with N branches. Sub-forks of forks are excluded, not
merely unimplemented (project owner, 2026-08-25). They multiply without bound
and offer little over branching from the trunk again.

This section is the object map. What a branch *guarantees* is stated and
measured in one place only: `docs/MODEL.md` § "The canonical evaluation rule".
That section says that a branch's run definition opens at a keyframe of the
case, and why. It says that the definition opens at that keyframe's own case
instant, so no clock is re-based and no conversion is performed. It also says
what both of these are worth in floating point. The same section's
"What this requires of a branch" says which keyframe is used, and how it
relates to the instant at which the branch itself began.

Five things in `app/controller.py` implement a branch:

- `SimulationController.resumed_at(instant_s)` makes a branch at one of the
  trunk's keyframes. It builds a second controller through the ordinary
  constructor, with the settings of the trunk's stretch that opens at
  `instant_s`. So the branch runs under the change recorded there. It then
  seeds the new controller's system with the trunk's canonical state at
  `instant_s`, and returns the controller paused. The trunk is read and never
  written. So the two runs share no compartment, no accounting and no clock,
  and that is what lets both be advanced.
- `SimulationController.resumed_here()` makes a branch where the paused trunk
  stands, whether or not it stopped on a bookmark halt (`PL-Y2SL`). It makes
  the branch that the bullet above describes, because the two methods share
  `_branch_from`. Only the place where the fork may be taken differs. So a
  setting that the learner changed on the trunk while it stood there is on the
  branch (`PL-HSP8`, `PL-ZR49`). The method deliberately takes no instant,
  because the fork is the clock. So a caller has no float with which to name
  an instant the run has not reached. Nor can anyone confuse the instant a
  learner *marked* with the step instant the run actually stopped on. The
  method refuses a running trunk, a failed one, and one standing at its
  opening. It also refuses one at the supported run length, where a branch
  would have no step to take. `here_fork_point` returns its result from the
  same check, so an offer built from it cannot disagree with `resumed_here`.
  The crossing that the branch opens on is the crossing of the step it stands
  on. That crossing is computed again from the marks as they are at each read,
  in the same way for every branch. So a mark added inside the halting step
  counts as passed on the branch, just as it does on the trunk (`PL-2N43`,
  `PL-XV0D`).
- `SimulationController.resumed_at_mark(bookmark)` makes a branch at a time
  bookmark that the trunk has passed. The run may have halted there, or the
  learner may have marked the instant after the clock went past it (`PL-W4XQ`).
  It is the halt fork, taken late. The fork is the end of the step that reached
  the mark, and `TimeBookmark.steps_to_reach` finds that step from the crossing
  rule itself. The branch opens from the trunk's canonical state there, exactly
  as a halt fork does. The method takes the mark rather than an instant, for
  the same reason that `resumed_here` takes nothing. `mark_fork_points` lists
  the marks it accepts, each with the instant at which its branch would open.
  A mark on the supported run length is not listed, and `_resume_point`
  rejects a fork there for every method, because the branch would have no step
  to take and its Reset would return it to the same stop (`PL-VHQX`).
- `ResumePoint` records where the branch came from. It holds the trunk stretch
  that the step reaching the fork ran under. It holds the fork, which is the
  instant at which the fork was taken and the canonical state there. It holds
  the case's step count at the fork, the step that ends at the fork, and the
  agent that the branch's accounting period started from. It holds no
  crossing. A crossing stored with the marks it named would go on naming a mark
  that was removed and added back (`PL-XV0D`). So at each read, the branch asks
  again what the step ending at its fork crossed. `opened_from` is `None` on a
  trunk and a `ResumePoint` on a branch, so every run knows which kind it is.
  The stretch's opening and the fork are two instants for every fork except one
  at the case's opening (`PL-B8MK`, `PL-ZR49`). `reset()` goes back through the
  same `_open_at`, with the settings the branch runs under. So a reset opens
  the branch on the same provenance and keeps the entries it opened with.
  After them, it records each setting that differs from the one the branch
  opened under (`PL-K5BS`, `PL-ZR49`).
- `BranchedCase` holds a trunk and the branches taken from it. It is what makes
  two controllers one case rather than two unrelated sessions. It is also where
  the flat shape stops depending on a refusal. The trunk is the only run that
  `BranchedCase` will fork, so a sub-fork is not an operation it can express.
  `resumed_at` keeps its own refusal for a caller that holds a branch directly.

**What a branch inherits, and why each is not re-chosen.** A branch inherits
the agent and the patient, because changing either would make it a second case
rather than a second management of this one. `set_agent` already starts a new
run for that reason, and it refuses outright on a branch. A branch inherits the
circuit volume, applied before any state is. This is because
`BreathingCircuit.set_circuit_volume` conserves agent by rewriting the inspired
fraction, so a volume set afterwards would move the branch off the state it
opened at. A branch inherits the four live controls, read from the settings of
the trunk's stretch, which hold each value as it was set. The rebuilt branch is
then checked against those settings rather than trusted. The check covers
every setting the stretch carries, and the agent's displayed references, since
the agent and patient are read again from their data files. A refusal names
each value that differs, with both of its values (`PL-NC62`). One rule, the
same for every way of branching, decides which stretch. The branch names as
its provenance the stretch that the step reaching the fork ran under. After the
case's opening, no later change on the trunk can replace that stretch. The
branch runs under the stretch still open at the fork, which is what the dial
says there. Its timeline opens with copies of the changes the trunk made there
(`docs/MODEL.md` § "The canonical evaluation rule", `PL-ZR49`). And a branch inherits the bookmarks. That is the
opposite case to the timeline below, and it is settled by the same test. A
mark is a question about what is still to come, and a comparison is two
managements answering one question. If a learner had to re-enter the marks,
two branches could be compared at two different heights with nothing saying
so. What a branch does not inherit is the trunk's control timeline. The
branch's record is of what the learner does to *it*. The only entries that the
branch's timeline opens with are copies of the trunk's changes at the instant
the branch was taken (`RunRecord.opened_with`). A reset keeps them, and records
after them each setting that the learner changed and the reset kept.
`opened_from` is what records
where the fork was taken, and `began_at_s` is the one number to read for the
fork instant. It is zero on a trunk and the fork instant on a branch. The
definition's own first segment used to start at the same instant, and it no
longer always does. That is why the property exists, rather than leaving
readers to infer the instant (`PL-B8MK`).

**One time frame, and every reader is in it.** A branch continues the case's
step count. So `snapshot().elapsed_s`, every control-change stamp,
`drawn_window`'s instants *and* the instants `run_segments` hands out are all
in case time. A branch's `RunDefinition` opens at a keyframe of the case rather
than at a zero of its own. So a keyframe read from a branch needs no conversion
to be placed on the case's axis, and no reader has to know which kind of run it
holds. *Which* keyframe depends on the fork. For a branch taken at a control
event, it is the fork itself. For a branch taken at a bookmark, it is the
keyframe at or before the fork.

Until 2026-09-14 there were two time frames, and
`SimulationController.origin_s` held the difference between them. `advance` and
`drawn_window` subtracted it, and `run_segments` warned about it. `PL-ZMRT`
(project owner, 2026-09-14) removed the second frame, so `origin_s` and both
subtractions are gone. `PL-2R2C` was the problem of a branch's drawn columns
being anchored to its own zero, so that they landed at case instants the trunk
never draws. Removing the second frame dissolved that problem rather than
fixing it separately. `docs/MODEL.md` § "The canonical evaluation rule"
measures what that is worth.

**Where a branch may be taken.** There are three places, each reached by its
own method rather than through one list.

The first is at any keyframe the trunk holds. These are listed by
`BranchedCase.fork_points_s` and taken with `fork_at`. The keyframes are the
trunk's opening at induction and every setting change the model was actually
stepped under. Any *other* instant that a caller names to `fork_at` is refused
as belonging to another method, not as an instant a branch could not reproduce
(`PL-54V0`). The two methods below both fork between keyframes and reproduce
the trunk exactly. What no method does is *restart* a branch's definition at
its fork, and `docs/MODEL.md` measures what a restart does.
`tests/unit/test_run_definition.py` checks that a restart really does stop
reproducing the run it claims to continue. So the construction every method
uses is never relaxed into a restart on the grounds that the difference is
small.

And a branch may be taken **where the paused trunk stands**, with `fork_here`
(`PL-Y2SL`). A learner who pauses to think tries something else from that
instant in one action, without marking it first (project owner, 2026-10-12). A
bookmark halt is one such pause. `app/bookmarks.py` defines what a learner may
mark (`PL-LPLD`). `SimulationController.advance` is what halts a run on the
step that crosses a mark (`PL-CTD7`). It reads every compartment on either side
of each step, and pauses the run where a mark lies between the two readings.
Where a run stands is not, in general, a setting change. On a 120 s run with
two control changes, 3 of the 1 201 instants it can stand at are keyframes. So
the trunk holds no keyframe there, and nothing records one. The branch's
*definition* opens at the keyframe at or before the fork, while its clock and
its live system stand at the fork. This costs the trunk nothing and reproduces
it element-wise. The obvious route was measured and refused. Recording a
keyframe where the run halts makes the branch exact against the trunk it forked
from. But it also moves that trunk's own later results away from what the case
would have given unmarked, so marking a run would change it. `PL-B8MK` carries
both measurements. `docs/MODEL.md` § "What this requires of a branch" records
which of that section's two conditions the chosen route relaxes, and what the
relaxation costs.

The paused point is a permission rather than a standing offer. It ends when the
trunk starts again, because the point where a running trunk stands moves with
every step. A failed trunk offers no paused point either, because a failure is
not a pause. Nor does a trunk at the supported run length. That is a stop
rather than a pause, and it leaves a branch no step to take. Nor does a trunk
standing at its opening, where `fork_at` already opens a branch. This is why
the paused point is not part of a widened `fork_points_s`. Such a list would
change its members as the run moved. A caller holding an instant from it could
then ask for a fork at an instant the run no longer stands on.

And a branch may be taken at any **time bookmark the trunk has passed**. These
are listed by `BranchedCase.mark_fork_points` and taken with `fork_at_mark`
(`PL-W4XQ`). This is what a learner paused at three hours does after marking
the one-hour point. The instant is behind the clock. The trunk holds no
keyframe there and is not standing on it, and nothing in the bookmark fork's
construction needed either. The branch opens on the step on which the mark is
reached, which is the instant a halt would have stopped the run on. The
branch's state is the trunk's definition evaluated there, so the branch is the
one the halt would have given. Unlike the paused point, this list does not end
at the next step. A mark joins the list when the clock reaches it, or when a
mark is set behind the clock. It leaves the list only when the learner unmarks
it or the trunk starts over. That is the same lifetime that the keyframes have.
A MAC target is not on the list, because it has no instant. A fork at a height
is taken through `fork_here`, where the height's halt stops the run.

### How a learner takes one, and how a comparison ends

`app/main.py` builds the `BranchedCase` and opens the dashboard over its
trunk. So the application is a *case* from its first frame, not a run that
might later be made into one (`PL-VKJW`). Three things follow from this. Each
is a property of the display, not of the model:

- **The branch control belongs to the case**, so it sits beside the bookmark
  panel in `SimulationView` rather than in either `RunView`. It offers
  `BranchedCase.fork_points_s`, `BranchedCase.mark_fork_points` and
  `BranchedCase.here_fork_point`. It takes the branch through `fork_at`,
  `fork_at_mark` or `fork_here`. `dashboard_frame.fork_offer` decides what the
  control shows, and `qt_widgets.ForkPanel` draws it. A learner pauses at the
  decision point, or marks it and is stopped there. The learner then forks at
  that point, which is the order in which the two panels are read. Returning
  to a mark forks the run rather than truncating it. The trunk is kept, and
  the change is made on a branch drawn beside it. A learner who wants to try
  something else from the same point uses the branch's own Reset (project
  owner, 2026-10-12, ratified, over truncating the run at the mark after a
  confirm as Gas Man does, `PL-ZW0J`).
- **Two controls, because the ways into a fork last for different lengths of
  time** (`PL-TYWQ`, `PL-Y2SL`). The selector offers two kinds of row in one
  list, earliest first. The first kind is each instant in
  `BranchedCase.fork_points_s`, taken through `fork_at`. The second kind is
  every time bookmark that the trunk has passed, from
  `BranchedCase.mark_fork_points` and taken through `fork_at_mark`
  (`PL-W4XQ`). A mark's row is labelled with the instant at which its branch
  opens and with "on your mark", in the halt label's wording. So the row never
  states where the mark itself lies. Below the selector, a second button takes
  the branch at the point where the paused trunk is, through `fork_here`. The
  button is on the panel whenever `BranchedCase.here_fork_point` offers that
  point and no comparison is shown. It is labelled "Branch here: 1h23m", with
  the instant at which the branch will open. When a mark stopped the trunk
  there, the label is "..., stopped on your mark". Every entry and the button
  open under what the dial says at their instant. So two controls labelled
  with one instant open under the same settings (`PL-ZR49`). Pausing records
  no keyframe, so the paused point adds nothing to `fork_points_s`. The
  selector therefore never loses a row as the run moves. It gains a row as the
  clock passes a mark. It loses a row only when the learner unmarks that mark
  or the trunk starts over. The project owner chose this shape (2026-09-21,
  ratified, over one list that grows a row while the run is halted; and
  2026-10-12, ratified, over a row at the top of the selector selected by
  default). The reasons are these. A row that vanishes from a list can be
  noticed only by comparing the list with a remembered one, which is the
  stale-state case that `.claude/rules/expert-review.md` names. A control
  that vanishes, by contrast, can be noticed on sight. And a default
  selection that jumped to the paused point would move a choice the reader
  had made. The button passes no instant to `fork_here`, which takes none.
  That method exists to prevent one hazard: a fork asked for at the instant a
  learner *marked*, rather than at the step on which the run stopped.
  Because the button names no instant, that hazard cannot be expressed
  through the interface either. `fork_offer` takes the paused point from the
  **trunk**, not from the displayed runs, because `fork_here` forks the trunk
  and refuses a branch. A panel drawn from a branch's paused point would
  offer a fork that the case cannot take.
- **`SimulationView.add_run` is how a run reaches the dashboard after
  construction.** Until `PL-VKJW`, the dashboard's run set was fixed at
  construction ("the count cannot change while a dashboard is alive"). So a
  branch taken during a session had nowhere to be drawn. Now both legends'
  run counts, the names the runs carry, the setting sections and the agent
  locks are rewritten from the run set whenever it changes. The cap is still
  `MAX_DISPLAYED_RUNS`, which is two.
- **One comparison at a time, and Reset is the way out.** There is no run
  selector, because `ROADMAP.md` § "Explicitly out of scope for v0.5.0" defers
  it. So a second branch could only replace the displayed one, while the first
  went on living inside `BranchedCase`. The control is refused while two runs
  are shown. The refusal is visible, and its reason can be read. Resetting the
  *trunk* takes every branch off the dashboard and rebuilds the case on the
  restarted run. This is because a trunk that has started over never passed
  through the instant at which a branch was taken. Where a branch has run
  past its fork, or holds a control change made since it opened, the trunk's
  Reset asks first (`PL-W5WX`, `SimulationSnapshot.has_recorded_run`). The
  question comes from
  `SimulationView._trunk_reset_question`, which `RunView.ask_before_reset`
  hands to the trunk's view. Resetting a *branch* returns it to its own fork
  and leaves the comparison in place. **The lock says which of those two
  Resets it means, in the words shown on the screen** (`PL-WG73`).
  `comparing_fork_lock_text` fills its sentence from `run_label` and
  `RESET_LABEL`, so an instruction cannot name a control that is not there.
  The sentence it replaced sent a learner to "Reset the case". But the Reset a
  learner reaches for is the branch's, on the run they are trying to end. That
  press returns the branch to its fork, while the lock stays exactly where it
  was.

**No agent may be chosen while two runs are shown** (`PL-QRD1`). A branch's
`set_agent` refuses outright, so its `RunView` shows the agent chip in place
of the selector. The trunk's `set_agent` *succeeds*, which is the worse case.
The switch restarted the trunk, but `BranchedCase` went on listing a branch of
a run that no longer existed. `assemble_chart_frame` then refused the frame
over the shared MAC axis. So `_halt_every_run` failed both runs because of an
input to one of them. The trunk's selector is therefore locked while a
comparison is shown too (project owner, 2026-09-20, ratified, over keeping the
selector live and growing `RunView._confirm_new_case`'s dialog a clause about
the branches it would orphan). This follows the preference in
`.claude/rules/expert-review.md` for an interface that prevents the error over
one that reports it afterwards. The decision was ratified rather than
specified, because the case put to the owner was a session's own
recommendation. So ordinary evidence is enough to put it back to them: a
learner who wants to change agent mid-comparison, a measurement, or a cost
the case did not carry. `dashboard_frame.transport` carries all three locks
and names the longest-lasting one that applies. So the chip never sends a
reader to Pause for a lock that Pause cannot lift.

### What a branch comparison asserts, and which part of it is structural

**The full statement is in `docs/MODEL.md` § "What a branch comparison asserts,
and what it does not".** It is stated there because it is a claim about the
model, not about the object map. This section covers only the part that the
structure above decides, and that part is three things.

**The comparison is a trunk and one branch of it, and the structure enforces
this.** `BranchedCase` forks only its trunk, so it cannot express a branch of
a branch. `MAX_DISPLAYED_RUNS` is two, and there is no run selector. So what
is on screen is always one case managed two ways. It is never a survey of N
managements, and never one branch compared with another. A reader who
generalises the drawing into a wider facility is generalising past what the
structure can build.

**What may be attributed to the settings that differ is exactly the
complement of what a branch inherits.** A branch carries across the agent,
the patient, the circuit volume, the four live controls up to the fork, and
the bookmarks. It then keeps them fixed: `set_agent` refuses on a branch and
is locked on the trunk while two runs are shown. The control timeline is the
one thing not carried across. It opens with only the trunk's changes at the
fork, if any. So the difference between two runs after the fork is the
difference between two control timelines. The inheritance list
above is the audit of that claim, not a convenience.

**The shared history is the same object, not a reproduction of one.** A
branch's definition carries the trunk's own keyframe, and both runs sit in
the case's single time frame. So the runs agree before the fork by
construction, not because they meet a tolerance. `docs/MODEL.md` § "What
this requires of a branch" is where that is stated and measured, and the
residual it leaves is zero. The structure does *not* supply any bound on what
happens after the fork. Neither run is a prediction for a patient at any
point, because the model contains one reference adult and no variability
around it. So a difference between two branches is a property of the model, not an
expected clinical difference. That last point is the one that a reader of a
drawn comparison is most likely to need. `docs/MODEL.md` § "What a branch
comparison asserts, and what it does not" is where it is argued.

## Data files (`data/`)

Each JSON file carries a `schema_version`, an `id`, the parameter values, and
a `sources` array of citations. Each entry in `sources` has `citation`,
`url`, `tier`, `adopted`, `authority_for` and `note` (see
`core.parameters.SourceReference`). `tier` comes from the closed vocabulary
`core.parameters.SOURCE_TIERS`, which contains the three tiers that
`docs/MODEL.md` § "Source hierarchy" defines. `adopted` says whether the file
names that source as the authority for a value it stores. That is a separate
question from the source's tier. `authority_for` names the stored values for
which the source is the authority, using the dotted key path that the
provenance table uses. It is empty exactly when `adopted` is false. A file
that adopts no primary source at all carries a top-level `provenance_gap`
that says so. `python3 tools/source_tier_counts.py` reads `authority_for` and
prints the source and tier behind every stored value, file by file and in
total. The script gates nothing, by the project owner's decision recorded on
`PL-9LXK`. It prints the counts that `docs/MODEL.md` states and never checks
them. `core/parameters.py` rejects a file in any of the following cases. The
file is missing required fields, or it uses an unsupported schema version.
It declares a tier outside the vocabulary, or an `adopted` flag that is not a
JSON boolean. It declares an `authority_for` that disagrees with `adopted`.
Its `authority_for` names something that is not one of the file's stored
values, or names a stored value twice. It contains a value outside its validated range (e.g.
non-positive volumes, tissue perfusion fractions that don't sum to 1). Or it
carries a key that the schema does not declare, including a key inside a
nested object such as `tissue_gas_partition_coefficients` or one `sources`
entry. Adding a new agent, patient or machine profile means adding a new
validated, cited JSON file, plus any new parsing support in `parameters.py`.
It does not mean adding constants directly to `core/`.

The three kinds of file answer three different questions, and a value belongs
to exactly one of them. `data/agents/` is what the drug does.
`data/patients/` is who is being anesthetized. `data/machines/` is the
apparatus delivering the drug: the breathing system's volume and the default
fresh gas flow. Filing a machine parameter under the patient would say
something false about where it came from. That is why `PL-4YY1` added a third
directory rather than a field to `reference_adult.json`.

## User state: the saved Workspaces

The application writes only one thing outside its own tree: the reader's saved
Workspaces. They are saved as a single JSON document that holds the whole
`WorkspaceSet` under one `schema_version`. The set includes every Workspace
with its layout, each View's saved state and the run that the View is pinned
to, the order of the Workspaces, and which Workspace is active. No run's data
is saved. A pin names a run only by its identity, so in a later session the
pinned run is absent (`PL-7Z84`). `layout/store.py` owns the document. The
decisions behind it come from `PL-SSQW` (project owner, 2026-09-27,
ratified) and from question Q4 of `PL-WV9K` (project owner, 2026-09-27,
specified). This entry replaces a measurement that `PL-CNJ1` took on
2026-09-15, which found that nothing under `src/` wrote to disk. That finding
was true until this store landed.

- **Where.** The store uses the directory that Qt reports for
  `QStandardPaths.AppDataLocation`. Qt reports it once the entry point has set
  the organization and application names, and `app/main.py` sets them before
  it asks (`PL-DWHG`). On macOS the directory is
  `~/Library/Application Support/<App>`. On Windows it is
  `%APPDATA%\<Org>\<App>`, in the Roaming folder, because the file holds no
  window geometry and its sizes are fractions. On Linux it is
  `~/.local/share/<App>`. In these paths, `<Org>` is the
  `APP_ORGANIZATION_NAME` in `app_metadata`, and `<App>` is its
  `APP_DISPLAY_NAME`. The store is given a directory and does not work one out
  itself. `store.user_data_directory` applies the one override, the
  `ANESTHESIA_SIM_USER_DIR` environment variable, for a headless or portable
  run. A test passes `tmp_path` instead. The function `open_workspaces` in
  `app/main.py` loads the set at launch. If a platform reports no directory,
  the session saves nothing and tells the reader so.
- **When.** The store writes only when the reader chooses "Save as default",
  like Blender's startup file. Nothing is written when something changes,
  nothing is written before the first save, and a first run leaves no trace.
  The save writes a temporary file beside the target and `fsync`s it. It then
  copies the current file to `workspaces.json.previous`, so that one prior
  generation survives. Finally it `os.replace`s the target. As a result, only
  a crash in the middle of the replace can leave the current file torn. A
  failed save raises `WorkspaceFileError`, which names the path and the
  reason. The error is reported where the action was invoked, on the line
  under the Workspace tabs. "Save as default" is an entry in the Layout menu.
  Before it writes, it asks a question that names the file it will write. It
  sits beside "Restore shipped Workspaces" and "Reset all layouts", and
  neither of those writes anything (`PL-DWHG`).
- **What a launch does with the file** depends on the file's
  `schema_version` and on whether the file can be read. The store returns the
  whole outcome in `store.Loaded`, so that the interface can show it on the
  line under the Workspace tabs. There are five cases.
  - *none*: the launch shows the shipped set and says nothing.
  - *older*: `layout/migrations.py` migrates the file in memory, one step per
    version. The reader is told only where a step lost information. At the
    next save, the file as it was before migration is kept once as
    `workspaces.v<N>.json`.
  - *newer*: the launch refuses the file and leaves it untouched. It shows
    the shipped set and turns saving off for the session. A notice names the
    file and both versions.
  - *unreadable*: the launch handles the file as it handles a newer one.
  - *invalid at a version this build reads*: the launch sets the file aside
    unchanged as `workspaces.invalid-<UTC time>.json`. It loads the previous
    generation if that generation validates, and the shipped set otherwise.
    The notice says which one it loaded, and saving stays on.

  A View kind under which no View is registered is not a file error. The file
  loads, and that Area shows the failure state that `PL-R1WQ` defines. The
  one-version rule in `core/parameters.py` is right for files that ship with
  the code. It is wrong for a file that the reader wrote. That is why this
  policy was decided rather than inherited.
- **The shipped set** that the store falls back to is the one `PL-KXTL`
  defines. It is three Workspaces under `data/workspaces/`, one JSON file
  each. Every file is a set document that holds one Workspace.
  `layout/shipped.py` reads them with the same reader that the learner's file
  goes through. It requires them to be at the current `schema_version`,
  because a shipped file is never migrated. "Reset this Workspace" reads one
  file again, by its id.

## Dependencies

**Three declared runtime dependencies** are listed in `pyproject.toml`:
`PySide6-Essentials`, `pyqtgraph` and `pydantic`. `flet` and `flet-charts`
were removed by `PL-3SQT`, after `PL-25KS` had deleted the last module that
imported either of them. Removing them from that list is not what keeps Flet
out, though. `tools/import_boundary_check.py` permits neither of them in any
module under `src/`, and that check is the rule.

**numpy arrives underneath pyqtgraph.** The metadata of pyqtgraph requires
`numpy>=1.25.0` outright, so numpy is installed in every environment and
`uv.lock` names its version. But no module under `src/` imports numpy, and
`import_boundary_check.py` permits it in no module under `core/`. The tests
declare numpy for themselves, in the `dev` group. They need it because
`tests/reference/test_late_washout_against_published_fits.py` decomposes the
model's open-circuit system with `numpy.linalg.eig` (`PL-921Y`). This
document takes no position on declaring numpy for the application.
`docs/WORKING_NOTES.md` § "Decided: no numpy" says why that question stays
open until a module under `src/` wants numpy.

**What Linux has to supply, which the Qt wheels do not carry.** This was
measured on 2026-09-16 by running `ldd` over two files in the wheel itself,
`Qt/lib/libQt6Gui.so.6` and `Qt/plugins/platforms/libqoffscreen.so`. Both
files link to shared objects that resolve outside the wheel. Five OS packages
provide those objects.

| shared object | Debian/Ubuntu package |
| --- | --- |
| `libEGL.so.1` | `libegl1` |
| `libGL.so.1`, `libGLX.so.0`, `libGLdispatch.so.0` | `libgl1` |
| `libxkbcommon.so.0` | `libxkbcommon0` |
| `libdbus-1.so.3` | `libdbus-1-3` |
| `libfontconfig.so.1` | `libfontconfig1` |

Only the first package is normally absent. `README.md` § "Running it" names
only `libegl1`, because the other four are already present on an ordinary
desktop. `.github/workflows/quality.yml` also installs only `libegl1`,
because its own comment records that the other four are present on the
`ubuntu-latest` image (`PL-VHLZ`). The full list is here so that a minimal
container, which is neither of those, has something to read. macOS and
Windows need nothing extra.

**Licensing, written down before a packaged build needs it (`PL-3SQT`).**
`pyside6_essentials` 6.11.2 and `shiboken6` 6.11.2 both declare
`LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`. Neither wheel ships the
licence text. A measurement on 2026-09-16 found that neither `dist-info`
carries a `licenses` directory or a `License-File:` entry. This repository is
Apache-2.0 and has no `NOTICE` file. **Nothing is violated today.** The LGPL
obligations are dynamic linking, a recipient's ability to relink, and
conveying the licence text. They attach when a binary is *conveyed*, and this
project conveys none. `README.md` § "Running it" says that building from
source is the only route, and `uv` installs each wheel from PyPI for each
user. The obligations will arrive on the day a bundled build does, as part of
the packaging work in `ROADMAP.md`. This paragraph exists so that they are not
first discovered then. pyqtgraph is MIT, and numpy is
`BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0`. Both ship their licence
text in the wheel.

## The workflow apparatus

The scripts under `tools/`, the hooks under `.claude/hooks/` and the
third-party text that their tests read are mapped in
[`docs/apparatus.md`](apparatus.md). They exist so that agent sessions can
build the simulator, and nothing under `src/` imports them. That document is
held to `.claude/rules/apparatus-standard.md`, not to the specialist standard
that `CLAUDE.md` sets for this document (`PL-KRGY`). One of those tools keeps
this document in step with the code. `tools/doc_check.py` checks the package
map above against the tree on disk in both directions. So a module added
without a line in the map, or a line left behind after a module is deleted,
fails `make check`.

## Tests (`tests/`)

- **`tests/unit/`** — tests of one module's behavior in isolation. Examples
  are a compartment, a validator, a parameter loader, the controller and the
  displayed-value formatters. `test_dashboard_frame.py` tests what the
  dashboard claims on each tick, with no toolkit loaded. Every operation and
  refusal of the area layout is tested in `test_layout_model.py`,
  `test_layout_serialization.py`, `test_layout_workspace.py`,
  `test_layout_migrations.py` and `test_layout_store.py`. The last of these
  runs against `tmp_path`.
- **`tests/integration/`** — components wired together as the app assembles
  them. One example is the controller driving a full `AgentUptakeSystem`.
  `test_qt_chart.py` draws the Qt chart headless against a real run, and
  reads the plotted items and the painted pixels back. `test_qt_widgets.py`
  tests the dashboard's leaf widgets. `test_simulation_view.py` drives the
  whole dashboard against real controllers, and reads back every widget's
  text, enablement and visibility. `test_qt_rendering.py` renders the whole
  dashboard headless at one fixed size. It reads back the painted pixels and
  the laid-out geometry. It also writes the kind of screenshot that
  `.claude/skills/run-the-app/SKILL.md` shows a session how to take
  (`PL-YCWZ`, `PL-CQRL`). `test_dark_appearance.py` tests what the interface
  draws when the *host* is set to a dark appearance. It sets the palette that
  such a host supplies on the `QApplication`, where the other tests set it on
  one widget. It does so because the declarations it tests are themselves
  palettes (`PL-RKRY`). `tests/conftest.py` selects Qt's `offscreen` platform
  plugin before any `PySide6` import, so the suite renders on a runner with no
  display. On Linux that plugin needs `libegl1` from the OS.
  `.github/workflows/quality.yml` installs it, and the PySide6 wheels do not
  carry it (`PL-VHLZ`).
- **`tests/reference/`** — analytic or independent reference cases that the
  implementation must reproduce. Examples are the closed-form circuit wash-in
  solution, the sevoflurane patient reference scenario, and the from-scratch
  RK4 integration of the coupled system in `test_coupled_dynamics.py`.
  These are the regression tests referred to throughout the release gate in
  `docs/MODEL.md`. A reference case here may import the parameter loaders,
  but it must not use a solver in `core/`. The value of the case is that it
  was derived independently of the code it checks.
- **`tests/benchmarks/`** — measurement harnesses. They are not tests, and
  the test runner does not collect them as tests. `frame_cost.py` drives a
  real dashboard frame by frame under the `offscreen` platform. For each frame
  it times the simulation (`controller.advance`), the assembly
  (`SimulationView.present`) and the paint (`QApplication.processEvents`).
  So the question "is this the simulation or the interface" is re-measured
  with one command, rather than re-derived on a throwaway harness for a fifth
  time (`PL-ZG5J`). Run it with `uv run python
  tests/benchmarks/frame_cost.py`. It takes about three seconds and prints
  timings. The timings call for a judgment and are not a verdict. A harness
  like this is not a `tools/` script, because of where each can run.
  `make check`, CI and the hooks invoke `tools/` scripts with a bare
  `python3` outside the project virtualenv, which is what makes those scripts
  standard-library-only. A harness that imports PySide6 and the package
  itself can only ever run inside the virtualenv. What *is* decidable about a
  harness is that it still runs and still reports the stages it names. A
  collected test beside it, `test_frame_cost.py`, checks that. The test
  asserts nothing about a duration, because a threshold here would measure
  the runner rather than the code.

## Where new code belongs

- A new physiological compartment or coupling → `core/`. Document its
  equations and reference cases in `docs/MODEL.md` first, as `CLAUDE.md`
  requires.
- A new agent, patient or machine profile → a new validated, cited file under
  the matching subdirectory of `data/`. Do not hardcode its values in `core/`.
  A compartment takes such a value as a required argument, with no default
  that restates it. `BreathingCircuit` takes its volume this way (`PL-M85T`).
- A number the code needs → one home, and every use reads the number through
  its name. A scientific value lives in a cited data file under `data/`. A
  factor between units lives in `core/units.py`. Any other number is a
  module-level constant in the module that owns the quantity. Other modules
  import that constant and never declare it a second time.
  `tools/literal_home_check.py` rejects the two shapes that a copy takes. The
  first is a bare numeric literal other than 0, 1 and 2, anywhere under
  `src/anesthesia_sim/`. The second is a numeric constant defined in more than
  one module. The check's baseline lists the literals that existed before the
  check, and the baseline only shrinks. A finding names any constant with the
  same value. It does not decide whether that constant is the same quantity,
  which stays the reader's call (`PL-40SJ`).
- A new View → a class in `app/views.py`. The class is a `QWidget`, satisfies
  the `View` protocol in `app/view_contract.py`, and is built from a
  `ViewContext` alone. It is drawn from each `ViewTick`. It asks for a
  change to shared state through the context's requests, and it never holds
  that state itself. The module docstring of `app/view_contract.py` states the
  contract, and `ConcentrationView` is the example to read from end to end.
  Then give the View a tag, written as a literal in `app/view_registry.py`.
  Beside the tag, add a `RegisteredView` entry that names the class as its
  factory. Saved layouts name a View by its tag, so the tag never changes.
  When a View is renamed or removed, its tag goes into `RETIRED_TAGS` with the
  release that retired it. That old tag is never registered again
  (`PL-R1WQ`). Every Area's chooser lists the new kind of View at once
  (`PL-50PZ`). `tests/integration/test_view_contract.py` builds the View,
  checks it against the protocol, and checks that it reads back the state it
  saves. A value that `docs/MODEL.md` § "Minimum displayed outputs" puts in
  the unconditional set never goes in a View.
- A new display panel or control → three places. What the panel *claims* goes
  in `app/dashboard_frame.py`, as a plain value with a test in
  `tests/unit/test_dashboard_frame.py`. The widget that draws it goes in
  `app/qt_widgets.py`, and that widget decides nothing. The code that places
  it goes in `app/run_view.py` or `app/simulation_view.py`. To choose between
  those two, first ask *whose* panel it is. A panel that states a particular
  run's numbers belongs to `RunView`. Such panels include readouts, settings,
  transport, and the record of what was changed during the run. `RunView` is
  instantiated once per run, and the dashboard places the panel by looping
  over its runs. A panel about the chart that both runs are drawn on belongs
  to `SimulationView` or to the chart View that draws it. Such panels include
  an axis, a legend, a reference, and the compartment selection. A chart's
  time window belongs to that chart View alone (`PL-L59K`). A control that
  asks one question of the whole case, rather than of either run, also
  belongs to `SimulationView`. The bookmark editor is the worked example
  (`PL-LPLD`). It writes each mark to every displayed run, so that the copies
  the controllers hold stay equal. The branch control is the second example
  (`PL-VKJW`). The instants it offers are the trunk's keyframes. A copy of it
  in each run would give a branch a control that could only refuse. Getting
  this the wrong way round is not a matter of tidiness. A run's panel put on
  the dashboard would state one branch's numbers over both runs. A shared
  control duplicated into each run would let a reader interpret a comparison
  under two different settings. In either place, read only what
  `SimulationSnapshot` already carries and what a `DrawnWindow` already
  returns. A window holds its states per substance. A trace addresses one
  value in those states as a `RecordedSeries`, not as a named field. A
  `RecordedSeries` is a pair of a substance and a `RecordedQuantity`. If the
  UI needs a value that does not exist yet, add it in `app/controller.py`.
  Compute that value in `core/`, never in the view. A panel that needs the
  run, rather than the instant, asks
  `SimulationController.drawn_window(start_s, stop_s, columns)` for the span
  it draws. It never asks for the whole run. The states come back evaluated
  at the instants that the span plots. So the amount of data that crosses
  that boundary is limited by the display, not by the length of the run.

  **The *whose is it* question describes the fixed layout. The View contract
  supersedes it for anything an Area holds.** The question routes a surface
  by which of two containers holds it. An Area holds one View, and any View
  can occupy any Area, so inside an Area the question has no answer. For a
  View, the route is the bullet above (`PL-TH35`). This bullet still decides
  **where the code goes** for what stays outside the Areas. That means the
  unconditional region and the case section below the Areas. The setting
  controls were a third such surface until `PL-2KXB` made them a View.
  `.claude/rules/ui-areas.md` decides **what shape a View is in**. A View is a
  widget that is given what it draws. It does not assume its size, its
  neighbours, or that it is alone. That rule loads with any file under
  `app/`, `layout/` or `data/workspaces/`. What outlives the fixed layout is
  this bullet's *reason*, not its routing. A run's panel must not state one
  branch's numbers over both runs. A control shared between runs must not be
  duplicated into each run. Both are properties of the value rather than of
  the container. They apply to a View exactly as they apply to a panel today.

  *The supersession has a release, as of 2026-09-16*. The release is v0.6.0,
  "the layout is the reader's", which builds the Areas, the View contract,
  the Workspaces and the persistence. Breaking a surface out into a second
  top-level window is the second half of item 34. It has been wanted but
  unscheduled since 2026-09-26. Once it is built, the routing question gains
  a second half: *which window* a surface is instantiated in.
  `docs/MODEL.md` § "Minimum displayed outputs" answers that half, not this
  bullet.
- A new way of *rendering* a value that a reader interprets →
  `app/formatting.py`. Examples are a unit, a decimal count, or a marker for
  what the display cannot resolve. Write it as a pure function with its own
  test, and record the reason in `docs/MODEL.md` § "Displayed precision".
- A new stylesheet, or a change to how a widget is styled → a function in
  `app/stylesheets.py` that returns the stylesheet string. The function
  composes the string from the values in `app/theme.py`, and it is called
  where `setStyleSheet` is called. A new colour is first added as a token in
  `app/theme.py`. Neither module imports the toolkit.
  `tests/unit/test_stylesheets.py` requires every `setStyleSheet` call under
  `app/` to pass a composer (`PL-Y4YX`). A widget may paint a colour from a
  palette role, such as an entry's fill or a check box's indicator. That
  colour is declared with `qt_widgets.declare_interface_colours` instead,
  never with a stylesheet (`.claude/rules/ui-color.md`).
- A new chart series, or a change to how one is drawn → two modules. What the
  series *claims* goes in `app/chart_frame.py`. How pyqtgraph paints it goes
  in `app/qt_chart.py`. A new *compartment* trace is declared in
  `chart_frame.COMPARTMENT_TRACES`. That table writes four things as one
  record: the quantity the trace draws, how it is drawn, the legend words
  that name it, and the gloss its hover text carries. The table belongs to
  the chart, not to any one run. `assemble_chart_frame` reads it once per
  run, for the substance that the run's snapshot names. The run is recorded
  under that substance's identifier. `ChartFrame.visible` is the dashboard's
  `CompartmentSelection`. The legend shows that selection and asks to change
  it, but does not hold it (`PL-VN6M`). Once more than one run is on the
  chart, `ChartFrame.visible` is that selection narrowed by
  `compared_compartments` to `COMPARED_COMPARTMENT_CAP`. So
  `app/qt_chart.py` keeps one curve per run per trace and moves each curve to
  match. Nothing is edited directly. The *width* of a curve comes from
  `chart_frame.run_trace_style`, not from the table. While two runs are
  drawn, that width is the run's own channel. The table records what a
  compartment looks like, so a new trace declares no width for a run. A
  series that draws no state of the run stays out of that table by
  construction. Examples are a clinical reference and a control mark. Such a
  series must meet a labelling requirement instead. `docs/MODEL.md`
  § "Interface boundary" sets that requirement in place of the drawn-point
  rule. A trace of a *derived* quantity with a domain, such as the wash-in
  ratio, also stays out of the table. The table binds a line to one
  `RecordedSeries`. A value that is sometimes absent has no such series to
  bind to. Such a trace must state its domain instead, in `docs/MODEL.md` and
  at the point of display.
