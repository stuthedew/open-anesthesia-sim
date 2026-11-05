# Architecture overview

This document describes how the code is organized and how data flows through
it. For the equations, units, parameter provenance, and numerical method, see
[`docs/MODEL.md`](MODEL.md). For version history and milestones, see
[`ROADMAP.md`](../ROADMAP.md). For the origin of the interface's area and
workspace model, see [`docs/interface-provenance.md`](interface-provenance.md).
That document says which parts of Blender were studied, under which licence
rules, and what this project deliberately does differently.

## Layering

The codebase is split into four layers, and imports between them run in one
direction only. An import check (`tools/import_boundary_check.py`) runs at every
`make check`. It rejects an import of the UI toolkit under `core/` or `layout/`,
and an import of `app/` from `core/`. Never edit code to get around that check.

```text
data/  --loaded by-->  core/  --read by-->  app/
                                             ^
                    layout/  --read by-------+
```

- **`core/`** is the scientific simulation. It does not use wall-clock time, and
  its only I/O is reading the packaged JSON files in `data/`. Identical inputs
  always give identical results.
- **`layout/`** holds the layout of each window as a value: which View occupies
  which part of the window. It also provides the operations a user performs on
  a layout (`PL-C842`, `PL-1FT6`). It imports no toolkit, so every operation is
  tested without a `QApplication`. The one `core/` module it imports is
  `core/checked_number.py`, for the way that module names a refused value. Only
  one module in `layout/` writes outside the source tree (`store.py`). It saves
  the user's Workspaces, which are layouts, as described under
  § "User state: the saved Workspaces" below.
- **`app/`** is the PySide6 user interface. It never performs a physiological
  or unit calculation itself. For every file under `app/`, a project rule
  forbids simulation calculations in UI callbacks
  (`.claude/rules/ui-calculations.md`). The user interface only reads immutable
  snapshots from `core/`, through a thin controller, and renders them. It
  forwards user input back as setter calls. It builds the widget tree from a
  layout (`app/area_layout.py`, `PL-W9P6`). It also holds the one list of View
  kinds that a layout may name (`app/view_registry.py`, `PL-R1WQ`).
- **`data/`** holds versioned, schema-validated JSON parameter files with
  citations. There are three kinds of parameter file: agent, patient and
  machine. Every scientific constant that a shipped run uses comes from one of
  these files. A project rule forbids writing a model parameter as executable
  code (`CLAUDE.md` § "Architecture and development discipline"), and the
  typed payloads in `core/parameters.py` reject a formula where a number is
  expected. The documentation check (`tools/doc_check.py`) traces a constant to
  its source only when the constant is in a data file (`PL-4YY1`).

  Each compartment in `core/` keeps field defaults so that it can be
  constructed with no arguments. No shipped code path uses those defaults,
  because the code that builds an agent's uptake system
  (`AgentUptakeSystem.for_agent()`) passes each value explicitly. A test pins
  each default to the data file that is its authority.

  The shipped Workspaces are in `data/workspaces/`. They are not parameters: a
  module in `layout/` reads them (`layout/shipped.py`), and nothing in `core/`
  does.

## Package map

```text
src/anesthesia_sim/
├── user_files.py        # the steps that write a reader's file atomically - write and fsync a temporary file, os.replace, fsync the directory - shared by the Workspaces and the preferences stores (PL-93B3)
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
│   ├── control_record.py           # what a run's settings are addressed by and the change a run records: ControlInput, CONTROL_INPUT_DISPLAY_UNITS and CONTROL_INPUT_UNITS, control_value (which settings field holds each control's value, PL-000W), ControlChange; toolkit-independent
│   ├── display_units.py            # DisplayUnit: each unit the interface states, with its recorded spelling, the label beside a value and its chart axis title, so the record, the panel, the formatters and the chart read one member (PL-G84G); toolkit-independent
│   ├── bookmarks.py                # what a learner marks a case at, held in two collections: TimeBookmark (an instant), MacTarget (a height on one compartment), BookmarkSet; toolkit-independent, and it detects a crossing between two readings it is handed, which SimulationController.advance supplies each step
│   ├── simulation_view.py          # SimulationView on PySide6: what runs share - the unconditional region above the layout container, which refuses a run lacking a declared value, the compartment selection every View is shown, the chart frame a tick assembles for each window a chart View asks for (PL-L59K), the case section of bookmarks and branching under the Areas, the render tick, and the Workspaces: the tab strip over the Areas switches among them, and a pinned Workspace's Views draw its run alone (PL-2KXB); no domain logic
│   ├── area_layout.py              # AreaLayout: the one module that builds QSplitters, every one from a layout.LayoutModel; a drag on a border becomes LayoutModel.resize and every splitter follows the new model (PL-W9P6), stopping in WARNING at an Area's least size, moving one border alone with Shift and undone by Escape; a border in the tab order moves one step per arrow key, and the Area menu's Resize entry gives one the focus (PL-M352); a right-click on each Area's header opens an AreaMenu that splits, joins, swaps or closes it, and a corner drag splits or joins it, or with Ctrl swaps it, with a preview drawn over the Areas (PL-2KXB, PL-R5G4); each Area is an AreaFrame whose header holds a ViewChooser listing every registered kind, and a choice is LayoutModel.set_view (PL-50PZ); each Area's View is built by its registry entry's factory, saved when replaced, and drawn from each ViewTick (PL-TH35); an Area whose View kind is not registered, or whose factory fails, shows an AreaNotice instead (PL-R1WQ); no View is drawn below its need, and an Area that cannot be given it shows the size it needs (PL-K285); load draws another Workspace from its layout and View state, and a pinned Workspace's run is named in every Area's header, or stated absent in place of each View (PL-2KXB)
│   ├── workspace_tabs.py           # WorkspaceTabs: the Workspace tab strip above the Areas, drawn from a WorkspaceSet it does not own; shipped tabs first, a rule, then the reader's own; each tab's menu entry worked out before it is shown, Delete and Reset asking first, and rename in place (PL-QW1Z, PL-2KXB); a Layout menu, opened by a right-click on the strip outside a tab, lists every Workspace and holds the current one's entries, and Ctrl+PgUp and Ctrl+PgDn step through them (PL-M352, PL-R5G4); it and each tab's menu end with Save as default, Restore shipped Workspaces and Reset all layouts, and a line under the tabs shows what the store reported (PL-DWHG)
│   ├── view_contract.py            # the View contract every View implements: the View protocol, the ViewContext it is built from, the FrameRequest naming the window and width it draws, the ViewTick it is drawn from, the RunSurfaces a View may show, ViewRequests for a change to shared state or a frame, including the agent cost View's unit and the reader's price for an agent (PL-B396, PL-1P15), PreferencesInForce, the reader's preferences each tick shows every View (PL-B396), and the saved-state version check (PL-TH35)
│   ├── views.py                    # the shipped Views, each a QWidget satisfying view_contract.View: ConcentrationView, WashInView, ParameterControlsView, AccountingView (PL-TH35) and CompartmentSchematicView, which shows one RunSchematic per displayed run, each a run surface its run writes, withholds and names (PL-RNYV), and AgentCostView, which shows one RunAgentCost per displayed run in the unit the reader's preferences hold, with a selector that asks the dashboard to change it (PL-B396), the cost at the reader's price, and the form that sets that price (PL-1P15); each chart View holds and saves its own time window and writes the lines that depend on it from its own frame (PL-L59K)
│   ├── view_registry.py            # the View registry: each View kind's tag, written once as a literal, its RegisteredView entry with the factory that builds it, and RETIRED_TAGS for a tag renamed or removed; REQUIRED_REACHABLE, the kinds a build fails on import without (PL-50PZ); the text of the missing-kind and failed-build notices (PL-R1WQ)
│   ├── run_view.py                 # one run's widgets, controller, handlers, refresh and halt; RunView, instantiated once per run (the seam PL-B9PY drew)
│   ├── halt_gate.py                # halt_gate: every slot of RunView and SimulationView is called through it, so a raise inside one halts its run, or every run for SimulationView, rather than escaping to Qt (PL-HJKN); toolkit-independent
│   ├── run_surfaces.py             # the parts of a run that may sit in an Area, each built any number of times from the values it draws: ParameterControls, AccountingPanel, and keep_until_destroyed, which keeps the list of live copies RunView writes (PL-9LNF); the third such part, RunSchematic, is in qt_schematic.py, and the fourth, RunAgentCost, in qt_agent_cost.py
│   ├── qt_widgets.py               # PySide6 leaf widgets that decide nothing: MetricPanel, ReadoutRow, ParameterSlider, NoticeLabel, NewCaseDialog, BookmarksPanel, ForkPanel, initial_window_geometry
│   ├── formatting.py               # modeled value -> displayed string; toolkit-independent
│   ├── currency_code.py            # the one rule for a currency code, three capital letters, which the preferences store and the cost formatters both read (PL-1P15); toolkit-independent
│   ├── preferences.py              # the reader's preferences.json: an AgentPrice per agent and the agent cost View's unit, each refused alone when invalid and kept for the next save; a newer or unreadable file turns saving off (PL-93B3); toolkit-independent
│   ├── playback.py                 # playback rate -> whole simulation steps per tick; toolkit-independent
│   ├── dashboard_frame.py          # what the dashboard claims about one run at one instant, as plain values: the status word, the notice and its precedence, the readouts and their glosses, the setting controls, the transport enablement, the accounting panel, the control-change list, the captions and the new-case question; toolkit-independent
│   ├── chart_frame.py              # what one frame of the plots at one time window draws, as plain values: the trace table, the window, the axes' ticks, the references, the marks, the wash-in stretches and the hover text; toolkit-independent
│   ├── compartment_schematic.py    # what each container of the compartment schematic is filled to and labelled with, from one snapshot: its fill on the chart's own scale, whether it is off that scale, its tension and its amount (PL-RNYV); toolkit-independent
│   ├── compartment_selection.py    # CompartmentSelection: which compartments the chart draws, as a value the dashboard owns and the legend shows (PL-VN6M); held inside the compared cap, and a reader's click over it drops the longest-standing; toolkit-independent
│   ├── agent_cost.py               # what the agent cost View shows for one run, from one snapshot: the delivered agent in millilitres of liquid equivalent and in litres of vapour, each with its unit named and a caption saying what it measures; converts only the delivered agent, reading the amount and the agent's ratio from one snapshot (PL-B396); the cost at the reader's price, with the figures it multiplied and where the price came from, or why no cost is shown, all from one price record, and the price form's reading of what the reader typed (PL-1P15); toolkit-independent
│   ├── qt_agent_cost.py            # RunAgentCost on Qt: one run's instant line, delivered amount and caption, in the unit its View sets (PL-B396), and its cost readout at the reader's price (PL-1P15); computes no value
│   ├── qt_agent_price.py           # PriceEntry on Qt: the agent cost View's form for the reader's price per agent, which asks the dashboard through ViewRequests.agent_price and shows why an entry was refused (PL-1P15)
│   ├── qt_schematic.py             # SchematicCanvas on Qt: one run's six containers in the readout row's order, the tissue groups drawn in parallel between an arterial and a venous line, each filled in its trace colour to the reading's fill and labelled in text; ShareBar, each compartment's share of the agent the run holds as one bar (PL-S79P); and RunSchematic, the run surface that adds the instant line, the run's name while compared and the scale and off-scale captions (PL-RNYV); computes no value
│   ├── qt_chart.py                 # the concentration chart, the wash-in plot, the legend and the time base selector on pyqtgraph and Qt, moved per frame to match a chart_frame.ChartFrame, the legend showing a CompartmentSelection and the selector a time base it is handed; each chart says when it owes a frame at a wider width (PL-9LNF); declares no colour and formats no value
│   ├── chart_time_base.py          # how wide the chart's window is and how it is ruled; toolkit-independent
│   ├── control_timeline.py         # recorded control changes -> the acts a reader sees; toolkit-independent
│   ├── wash_in.py                  # F_A/F_I and the domain it holds on; toolkit-independent
│   ├── theme.py                    # every display token: palette, cited ISO 5360 agent colors, type sizes, spacing, dash patterns; toolkit-independent
│   ├── stylesheets.py              # every stylesheet a widget is given, composed from theme.py's tokens, so each visual decision is written once; toolkit-independent
│   └── main.py                     # PySide6 entry point; loads the reader's saved Workspaces from their data directory (PL-DWHG) and their preferences from the same directory (PL-B396), builds the BranchedCase and opens the dashboard over its trunk; the window opens maximized (PL-Z4K6) over a sized, centred normal geometry (PL-005)
├── layout/               # the area layout as a value: which View occupies which part of each window - no toolkit dependency (PL-C842, PL-1FT6)
│   ├── tree.py                     # the values a layout is built from - AreaId, ViewKind, Area, Split, Window - each refusing what could not be one, and the one form a tree takes
│   ├── sizing.py                   # how a layout is drawn in whole pixels: each Area held at its View's need, its siblings giving way, and which Areas are too small and held at their floor instead, a size that fits the header and the too-small notice at the width the Area is drawn at (PL-K285, PL-Y65Q, PL-16BG); pure functions of a tree and an extent
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

**At startup, parameters flow from the data files to the controller:**

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

Only one module, `core/parameters.py`, reads the JSON files, which it does
through `importlib.resources`. It validates the schema version, the required
fields, the units, and the ranges before it builds the agent, patient and
circuit parameters (`AgentParameters`, `ReferenceAdultParameters` and
`BreathingCircuitParameters`). The schemas are strict at every nesting level, so
a key that the schema does not declare fails the load. A data file therefore
cannot document one model while the app runs another. Nothing downstream
re-reads these values from disk or derives them again.

**Each simulation step advances the whole coupled system at once**, in
`AgentUptakeSystem.advance()`. It uses one exact propagation, rather than a
generic numerical integrator or a sequence of separate exchanges between
compartments:

1. The equations file, `core/governing_equations.py`, assembles the system
   matrix `A`. Each entry is one term of one balance equation in
   `docs/MODEL.md` § "Governing equations".
2. The exponential file, `core/matrix_exponential.py`, computes `exp(A dt)`.
   This is the system's exact propagator, because every setting is held
   constant across a step. The result is cached against the settings it was
   built for, and it is rebuilt when one of those settings changes.
3. One matrix-vector product advances the agent fraction in each of the six
   compartments. The same solution advances the cumulative delivered and
   exhausted amounts.
4. The agent-accounting validator (`AgentSimulationValidator`) records those
   amounts and checks mass balance. If the check fails, it raises
   `AgentSimulationValidationError`. The error carries the failing check,
   because the step is then rolled back and the run's own accounting no longer
   holds the rejected step's totals (`PL-HF4B`).

The package is arranged around the split between steps 1 and 2. The equations
file contains the physiology and no arithmetic, and the exponential file
contains the arithmetic and no physiology.

**Settings pass from the interface through the controller, which adds no
defaults or bounds of its own.** The controller (`SimulationController`, in
`app/controller.py`) owns the simulation state (`SimulationState`). It exposes
`start()`, `pause()`, `reset()` and four per-parameter setters, and it produces
an immutable snapshot (`SimulationSnapshot`) on request. Every setting that a
caller leaves unspecified comes from the system that the core built from the
data files (`AgentUptakeSystem.for_agent()`). When the core rejects a setting,
such as a delivered concentration above the agent's vaporizer maximum, the error
is raised out of the core, and the controller does not clamp the setting or
replace it with a default.

Conservation of agent belongs to the core, as bounds and defaults do. The
core's circuit-volume setter, `set_circuit_volume`, conserves agent itself.
A public setter in `core/` that did not would leave conservation to whichever
caller knew to compensate (PL-006). The controller calls the setter only once,
from `_build_state()`, to apply the volume the session was built with. The
circuit volume is a fixed model parameter, not a control (PL-GYH2), so none of
the four setters changes it. `docs/MODEL.md` § "What is not bounded this way"
gives the argument.

The snapshot is the run's state at one instant. It holds a fixed number of
values, however long the run has been going. The run as a whole comes
separately, from another method of the controller,
`drawn_window(start_s, stop_s, columns)`. That method evaluates the states at
the instants that a chart is about to plot, across the axis the caller names,
and returns them as a drawn window (`DrawnWindow`). The snapshot and the run are
kept apart because a snapshot that carried the whole run would make each frame's
cost grow with the run's length (PL-0VM7). The chart draws only the few hundred
samples inside its axis.

The snapshot does carry the run's timeline of control changes
(`ControlChange`), with one entry per setting that the model was stepped
under. Re-applying the timeline therefore reproduces the run rather than
approximating it. The timeline grows only when a user touches a control,
however long they watch.

The snapshot carries each compartment's agent amount in one record
(`CompartmentAgentAmounts`), keyed by compartment (`RecordedQuantity`,
`PL-KFTM`). The compartment schematic (`app/compartment_schematic.py`) labels
each of its containers from this record (`PL-RNYV`) and draws its share bar from
it (`PL-S79P`). The controller reads each amount from the compartment in `core/`
(`agent_amount_l`) when it builds the snapshot (`snapshot()`), so the interface
computes no amount of its own.

The record is keyed rather than ordered, so a container looks its amount up by
the compartment it draws and cannot be handed a neighbour's. Because the amounts
are not in the state vector, the controller pairs each key by hand with the
`core/` object it is read from. This is a second pairing, beside the one the
traces use (`run_series.COMPARTMENT_STATE_INDEX`). The reference test against
the coupled oracle catches a wrong pair. A later model that holds several
substances keys the same record by substance as well, rather than adding fields.

The record holds the six amounts and not their total. The snapshot carries the
total separately (`stored_agent_l`). It is the one sum of the six amounts that
the core computes (`AgentUptakeSystem.total_stored_agent_l`), and the accounting
check reads it. Adding up the record again in the interface would compute the
same total a second time. Instead, a unit test requires the six amounts, added
in the core's order, to equal the snapshot's total to the last bit. A reference
test compares each amount with oracles that do not read `core/`.

**A run is its inputs, and its states are derived from them** (PL-T691). The
controller keeps the run as a run definition (`RunDefinition`, in
`core/run_definition.py`). The definition holds the settings in force at each
moment, plus one keyframe per change, and nothing else of the run. A keyframe is
the state at the instant of its change. While the settings stay the same, the
equations are linear and time-invariant, so the propagator is exact over any
horizon, not only over a step. Every state that the run passed through is
therefore one propagation from the latest keyframe before it, and none of those
states has to have been recorded. No per-step sample history is kept beside the
definition, because such a history would be a second copy of the run that could
disagree with it (PL-2FM6). `docs/MODEL.md`
§ "The run is that record, and every state is derived from it" gives the
measurements.

Two methods of the run definition evaluate those states:
`RunDefinition.evaluate(start_s, stop_s, columns)` and
`evaluate_anchored(start_s, stop_s, spacing_s)`. The chart uses the second,
through the controller (`SimulationController.drawn_window`). The chart's
evaluation keeps the propagators that its last window used, so that the next
frame can reuse them. Each propagator is a function of settings that the
definition already holds, so no drawn value depends on whether it was kept
(`RunDefinition.evaluate_anchored`, PL-CNCF).

The definition itself is handed out as frozen segments (`run_segments`), which
can be read but not advanced. So no code above the controller can extend the
definition past the point the run has reached, and then have a prediction
drawn on the run's own axis.

**Drawn values have a type of their own.** Both evaluation methods return
display states (`DisplayState`), which are not state vectors. So a drawn column
cannot become a keyframe, an exported figure or a branch's opening state just
because it holds the same nine numbers in the same order. The run definition
rejects a display state by name as an opening state. A layer above the
controller therefore cannot turn a drawn value into a state by forgetting the
difference. `docs/MODEL.md` § "The canonical evaluation rule" states which of
the two evaluation paths a stored, exported, replayed or branched value may be
taken from.

**The views read only the snapshot and the drawn window.** A run view
(`RunView`, in `app/run_view.py`) builds one run's controls, and it wires the
slider and button callbacks through `_apply_setting` to the controller's
setters. The simulation view (`SimulationView`, in `app/simulation_view.py`)
drives the charts that every run shares. Neither performs a physiological or
unit calculation of its own. Each transformation that they do apply is in a
separate module, because each is a question of presentation *correctness*
rather than of layout, and must be readable and testable with no toolkit loaded.

The presentation is split into these modules:

- The formatter (`app/formatting.py`) turns a fraction into the strings a
  reader sees: a percent, and a multiple of the running agent's 1 MAC. It uses
  the resolutions that `docs/MODEL.md` § "Displayed precision" derives.
- The chart layer (`app/chart_frame.py`) decides, as plain values, what one
  frame of the chart shows: which compartment a trace carries, which instants
  are drawn, where the references are placed, and what a hover says. The
  plotting code (`app/qt_chart.py`) updates the pyqtgraph items to match that
  frame.
- The dashboard layer (`app/dashboard_frame.py`) does the same for everything
  beside the plots: the status word, the notice and its precedence, the
  readouts, the setting controls, the captions, and the two bookmark listings.
  The widget code (`app/qt_widgets.py`) updates the leaf widgets to match, and
  decides nothing.
- The control timeline (`app/control_timeline.py`) turns the recorded control
  changes into the adjustments a reader sees. Those changes are faithful to the
  run, so one slider drag appears among them as several settings. Showing that
  drag as one adjustment is a claim about what the user did, not a tidier
  rendering of what the model saw.
- The playback module (`app/playback.py`) turns the playback rate that a
  reader selects into the number of whole simulation steps that a tick takes.
  A rate is realised only as a step count, never as a larger step, so the
  module rejects a rate that does not land on a whole number of steps.
  Otherwise the run would advance at a rate other than the one it displays: a
  presentation failure that looks like a working feature.
- The wash-in module (`app/wash_in.py`) divides the alveolar fraction by the
  inspired one. The ratio has a domain: it is undefined before any agent
  reaches the circuit, and above 1 it stops being a wash-in fraction. So the
  module returns the value and the reason together, and the chart draws the
  trace in segments that break where the domain does. `docs/MODEL.md`
  § "F_A/F_I as a displayed ratio" is the specification.

The formatter takes the agent's MAC as an argument, from the snapshot
(`SimulationSnapshot.agent_mac_percent`), rather than looking it up. The MAC is
the divisor that makes a displayed multiple specific to the agent, so it travels
with the value it divides. The agent's MAC-awake travels the same way, beside
the MAC in the snapshot (`SimulationSnapshot.agent_mac_awake`). The chart's
MAC-awake band is one of these values multiplied by the other, so pairing two
different agents' values would place a correct number at the wrong height.

Which instants the chart evaluates is a question of presentation correctness: a
chart that stepped over a control change would show a curve the simulation never
produced. The rules that place the instants are therefore stated in
`docs/MODEL.md` § "What the chart draws" and tested on their own.
The instants are anchored to an absolute grid measured from the case's zero,
rather than to their position within the window. So a window that follows the
run keeps every column it had and gains at most one
(`RunDefinition.evaluate_anchored`, PL-Q197, PL-2FM6).

The chart layer sits above that anchored evaluation. It applies the rule of
one column per pixel, with that rule's minimum column count (`chart_columns`).
It reads the window once per run for every trace, and converts each drawn
value into the unit of its own axis, because it is the layer that knows the
axis. The six compartment traces are drawn in percent, and the wash-in ratio
is dimensionless. Which quantity a trace carries is declared once, beside the
traces, in the table that maps traces to compartments
(`chart_frame.COMPARTMENT_TRACES`). A reference reads no state of the run, so
it is deliberately not in that table. A control mark draws no value at all,
only a simulated time, so it is outside the table as well.

**Every failure that the core reports is a simulation error.** Each is a
subclass of `AnesthesiaSimulationError` (`core/exceptions.py`), never a bare
`ValueError`, so the interface can recognise a simulation failure and act on it.
The hierarchy has two branches, which the interface treats differently:

- A configuration error (`SimulationConfigurationError`) means that a value was
  rejected before it changed anything. The run view catches it
  (`_apply_setting`), restores the control from the snapshot, and says that the
  setting was refused. The run is untouched and keeps going. If a concentration
  that the display builds is refused, the run halts instead, because that
  concentration is not a setting. No supported setting causes such a refusal
  (`PL-7DJK`).
- An execution error (`SimulationExecutionError`, with its subclasses
  `SimulationNumericalError` and `AgentSimulationValidationError`) means that a
  step began and could not be completed, so the run must stop.

The following raise a configuration error:

- the guards in `core/validation.py`
- the constructors of the checked types: `Fraction`, `Percent` and
  `MacPercent` in `core/concentration.py`, and those in
  `core/supported_ranges.py`, `core/simulation_step.py` and
  `core/numerical_envelope.py`
- compartment constructors and setters
- a compartment field written directly, because its record checks every write
  in `__setattr__` (`PL-19Y0`)
- the parameter-file loaders

`TypeError` is raised instead in three cases, as a programming error rather than
a refused setting:

1. A setter, or a compartment field written directly, is handed a value not
   built as its type.
2. A checked type is built from something it does not accept. No checked type
   accepts a `bool`, a `Decimal`, a string, or a value already built as another
   checked type. The step count (`StepCount`) accepts only an `int`, so it also
   refuses a `float`. The checked type raises before it reads the range
   (`core/checked_number.py`).
3. The two sign-and-finiteness guards in `core/validation.py` raise it. They
   also reject an `int` beyond the float range by name, rather than let
   `math.isfinite` raise `OverflowError` while converting it (`PL-3800`).

The step method, `AgentUptakeSystem.advance()`, decides which branch a failure
belongs to. It checks its own arguments first. Then it re-raises any guard
failure during the step as a numerical error (`SimulationNumericalError`),
keeping the original as `__cause__`.

The step method also makes the step atomic: it captures every dynamic value
before the step and restores them all on any failure. So what is left behind is
the last completed step, rather than a state vector written into some
compartments and not others. Each compartment captures its own state
(`capture_state()` / `restore_state()`), so a dynamic field added without a
matching capture is an omission local to that compartment. `docs/MODEL.md`
§ "Step atomicity" is the contract.

**Every slot of a run view or of the simulation view passes the halt gate**
(`halt_gate`, in `app/halt_gate.py`), which turns any exception raised inside
the slot into a halt (`PL-HJKN`). So a control used on a run whose snapshot
fails meets a halt, rather than an exception that the toolkit prints. A slot of
a run view halts its own run, through `_halt_run`. A slot of the simulation view
halts every run, because it acts on the case. The two timer slots pass the gate
too: the run view's step tick steps the run (`RunView.step_tick`), and the
simulation view's render tick presents it (`SimulationView.render_tick`). The
gate catches every exception, not only a simulation error, because a `TypeError`
from a refactor is exactly as silent inside a Qt slot as a modelling failure is.
A `try` written by hand in each slot was not enough: six slots were found
without one, one review at a time. A test fails on any connected slot that does
not pass the gate (`test_every_slot_that_touches_a_run_passes_the_halt_gate`).

The dashboard layer decides whether a halt is a failure or a stop at the limit
of what the model supports (`dashboard_frame.halt_disposition`), and the run
view routes the halt by that decision (`RunView.halt`). A failure halts the run
through the controller (`SimulationController.fail()`). When a setting, or
another path that the controller does not step itself, raises a domain-limit
error (`SimulationDomainLimitError`), the run takes the supported-limit halt
(`halt_at_supported_limit()`). A run that steps onto the supported run length
meets no exception: the controller halts it on the step that arrives there
(`SimulationController.advance()`). The snapshot reads the limit from the run's
own state, so a run that is forked or reset onto that step is also treated as
stopped there (`PL-5291`).

A failure sets a third run state, through `fail()`. The snapshot carries this
state (`failure_reason`), and the dashboard renders it as
"Stopped — simulation error" with a banner over the values. A halted run must
never look like a paused one, because a paused run continues when asked and a
halted run cannot.

The supported-limit halt is a fourth run state, kept apart from the failure
because nothing went wrong. The run is at a completed step, at a time the model
claims to represent, and the next step would be refused every time it was tried.
The snapshot carries this state (`supported_limit_reason`), and the status reads
"Stopped — supported run length reached" in place of the failure wording.

Neither halt can be resumed. Only two actions clear a halt: a reset (`reset()`),
and an agent change, which starts a fresh run (`set_agent()`). A reset can
itself refuse, when the run definition cannot start from the settings record.
It does so before it clears anything. The run view then halts the run on that
refusal through the same path as other halts (`RunView._handle_reset`,
`PL-M4M0`). Every other halt's banner names reset as the way out, so the banner
for this halt says instead that no setting can repair the refusal, and that
closing and reopening the application starts a new run (`PL-01GY`).

A halt is presented from the run's record (`RunRecord`), which the controller
returns (`SimulationController.record()`). Both the snapshot and the record
extend one status type that carries both halts (`RunStatus`). The run view
presents a halt (`RunView.present_halt`) without building any compartment value,
because the snapshot's own `Fraction` values are among those that can cause a
halt. Halting a run through `_halt_run` also works from the record, so on a run
whose snapshot failed, the agent selector goes back to the agent that the record
names. The snapshot cannot name it, because the snapshot is what failed
(`PL-V2HC`). When the run view presents a halt, it writes a banner
(`dashboard_frame.halt_notice`) saying that no frame of the stopped run has been
drawn. The first frame that draws replaces it (`refresh`, `PL-7DJK`).

Every widget that states what the run holds is written by one method of the run
view (`RunView._write_statement`), from the dashboard layer
(`dashboard_frame.run_statement`). It writes the status word, the transport, the
agent identity, the four dials, the control-change panel and the banner. It is
called both when a frame draws (`refresh`) and when a halt is presented
(`present_halt`), so on each of these widgets a halted run shows what a frame
would show. A dial dragged into the halt shows the value the run holds, not the
value from before the drag (`PL-85LJ`). An agent changed just before the halt is
named on every identity widget (`PL-1YDD`). The control-change panel lists the
control changes that the run holds (`PL-DTJQ`).

Some things only a frame can state: the readouts and the clock read with them,
the accounting panel, the off-scale and wash-in lines, and both legends. These
stay as the last frame drew them, and values shown together still describe one
step. The legends are told what a frame drew only once both plots have drawn it,
so when the frame that a click asked for fails, the legend boxes still name the
traces on the plot (`PL-G3K7`). If a run halts after a reset or an agent change
and before any frame has been drawn, each readout card and the clock withhold
their values, and the accounting panel withholds its verdict and amounts. After
an accounting halt, the accounting panel shows the rejected step's check,
whether or not a frame draws. A stopped run refuses a dial, so the dials keep
the settings the run holds (`PL-3B34`).

Two tests check these rules. One checks each value on screen, and what
qualifies it, against one step
(`test_every_value_and_its_qualifiers_on_screen_come_from_one_state`,
`PL-J5GC`). The second requires every other widget that shows the run's state
to read the same on a halted run as on a drawn one. It applies to a widget by
default, so a widget added later is checked without anyone listing it
(`test_every_run_state_widget_reads_alike_on_a_drawn_run_and_a_halted_one`,
`PL-X7D5`).

When the simulation view halts every run (`SimulationView._halt_every_run`), it
updates the branch controls from the case, so a failed trunk offers no branch
from the point where it stopped (`PL-MMNX`). It also updates the bookmark
listings from each run's controller, so a mark that the failed run will never
reach is not listed as still to come (`PL-YHR3`). A halt updates these two
panels, and the marks editor with the bookmark panel, from one list of panels
(`SimulationView.halt_restatements`). A test fails on any dashboard control that
is not covered by a run, a listed panel or a named exemption, so a panel added
later is checked without anyone having to remember it
(`test_every_dashboard_control_is_restated_on_a_halt`, `PL-5JTH`).

When a frame fails, the trunk records that its dashboard failed. It then offers
no keyframe and no passed mark either, because a branch opened at one of them
would be drawn by the same dashboard, which could fail the same way. An
exception raised in one of the dashboard's own slots is recorded in the same way
as a frame that fails, because it too belongs to no single run
(`SimulationController.record_failed_frame`, `PL-T2Q2`, `PL-HJKN`).

Stepping and drawing run on separate timers, at separate intervals, so
simulation time depends on the steps taken, not on how long a frame took. Both
timers are started once, when the window opens, and neither stops on a halt. A
halted run leaves them firing and finding nothing to do, so a run that is reset
and started again is stepped without anything having to be restarted.

The render tick draws whenever a displayed run's record differs from the one its
view last wrote (`RunView.owes_a_frame`), and whenever the set of runs differs
from the set it last drew over. So when a run stops itself inside its own step
tick, on a mark or on reaching the supported run length, it is drawn without
anything asking for a frame. Each view stores the record when it writes it,
including when it presents a halt, so a frame that keeps failing is attempted
once rather than on every tick (`PL-X7D5`, `PL-T995`).

## What a branch is, and what it shares with its parent

A **branch** is a second live run of the same case, opened at a state that the
first run passed through. The run it was taken from is the **trunk**, and the
instant at which it was taken is its **fork**. A case is one trunk with any
number of branches. Branches of a branch are excluded by design, not merely
unbuilt (project owner, 2026-08-25). They multiply without bound and offer
little over branching from the trunk again.

`docs/MODEL.md` § "The canonical evaluation rule" states a branch's guarantees,
and how exact each is in floating point.

**Where a branch may be taken.** There are three places, each reached by its own
method rather than through one list. A fork at the supported run length is
rejected for every method (`_resume_point`, `PL-VHQX`), because the branch would
have no step to take and a reset would return it to the same stop.

The first is any **keyframe** that the trunk holds. A keyframe is the trunk's
opening at induction, or a setting change that the model was actually stepped
under. Each keyframe opens a **stretch** of the trunk's run, and a stretch holds
each setting as it was set. A caller lists the keyframes with
`BranchedCase.fork_points_s` and branches at one with `fork_at`. The branch's
run definition then opens at the fork itself. Any other instant passed to
`fork_at` is refused as belonging to another method, not as one that a branch
could not reproduce (`PL-54V0`). The other two methods both fork between
keyframes and reproduce the trunk exactly.

The second is the trunk's **paused point**, where the paused trunk stands. A
caller branches there with `fork_here` (`PL-Y2SL`). A learner who pauses to
think can then try something else from that instant in one action, without
marking it first (project owner, 2026-10-12).

A halt at a mark also leaves the trunk at a paused point. A learner may mark,
for example, an instant (a **time bookmark**) or a MAC target. What may be
marked is defined in `app/bookmarks.py` (`PL-LPLD`). The controller halts a run
on the step that crosses a mark (`SimulationController.advance`, `PL-CTD7`). It
reads every compartment before and after each step, and by the **crossing
rule** a step crosses a mark when the mark lies between the two readings.

A branch at the paused point opens its run definition at the keyframe at or
before the fork, because a paused trunk usually does not stand on a keyframe. On
a 120 s run with two setting changes, 3 of the 1 201 instants it can stand at
are keyframes, and none is recorded at a pause. The branch's clock and its live
system stand at the fork. This route costs the trunk nothing. Recording a
keyframe where the run halts was rejected. The branch would be exact against its
trunk either way, but a recorded keyframe would move the trunk's own later
results away from what the unmarked case gives, so marking a run would change
it. The results of both routes are in `PL-B8MK`.
`docs/MODEL.md` § "What this requires of a branch" says which of its two
conditions the route used here relaxes, and what that costs.

A paused point ends when the trunk starts again, because the point where a
running trunk stands moves with every step. For that reason it is kept out of
the keyframe list (`fork_points_s`). That list would otherwise change its
members as the run moved, and a caller holding an instant from it could ask for
a fork at an instant the run no longer stands on.

A failed trunk has no paused point, because a failure is not a pause. A trunk at
the supported run length has none either, because that is a stop. Nor does a
trunk standing at its opening, where `fork_at` already opens a branch.

The third is any **time bookmark that the trunk has passed**. The run may have
halted there, or the learner may have marked the instant after the clock went
past it. A caller lists these marks with `BranchedCase.mark_fork_points`, each
with the instant at which its branch would open, and branches at one with
`fork_at_mark` (`PL-W4XQ`). For example, a learner paused at three hours can
mark the one-hour point and branch from it. The trunk need hold no keyframe at
the mark, nor stand on it. The branch opens at the end of the step that reached
the mark, where a halt would have stopped the run. Its state is the trunk's run
definition evaluated there, so it is the branch that the halt would have given.
Its own run definition opens at the keyframe at or before the fork.

Unlike the paused point, a passed mark stays on its list from step to step. It
joins the list when the clock reaches it, or when it is set behind the clock. It
leaves only when the learner unmarks it or the trunk starts over. Keyframes have
the same lifetime. A mark at the supported run length is not listed. Nor is a
MAC target, because it has no instant. A branch at a MAC target is taken with
`fork_here`, once the target's halt has stopped the run.

Five things in `app/controller.py` implement a branch:

- A branch at a keyframe is made by `SimulationController.resumed_at(instant_s)`.
  The method builds a second controller through the ordinary constructor, with
  the settings of the trunk's stretch that opens at `instant_s`, so the branch
  runs under the change recorded there. It then seeds the new controller's
  system with the trunk's **canonical state** at `instant_s`, and returns the
  controller paused. The canonical state is the trunk's run definition evaluated
  at that instant. Because the trunk is read and never written, the two runs
  share no compartment, no accounting and no clock, and both can be advanced.
- A branch at the paused point is made by `SimulationController.resumed_here()`,
  whether or not the trunk halted at a mark (`PL-Y2SL`). The method uses the
  same helper that builds a branch at a keyframe (`_branch_from`), so the two
  branches differ only in where the fork is. A setting that the learner changed
  on the trunk while it stood there is therefore on the branch (`PL-HSP8`,
  `PL-ZR49`). The method takes no instant, because the fork is wherever the
  clock stands. A caller then has no float with which to name an instant the
  run has not reached, and cannot confuse the instant a learner marked with the
  step instant at which the run stopped. The method refuses a trunk with no
  paused point. An offer to branch at the paused point is built from the same
  check (`here_fork_point`), so the offer cannot disagree with the method.
- A branch at a passed time bookmark is made by
  `SimulationController.resumed_at_mark(bookmark)`. The method finds the step
  that reached the mark by the crossing rule itself
  (`TimeBookmark.steps_to_reach`), and forks at that step's end. It takes the
  mark rather than an instant, so that a caller cannot name an instant the run
  has not reached, or confuse the marked instant with the step instant at which
  the branch opens.
- The record of where a branch came from is a `ResumePoint`. It holds the fork
  and the trunk's canonical state there, the case's step count at the fork, the
  step that ends at the fork, and the agent that the branch's accounting period
  started from. It also holds the stretch that this step ran under, chosen by
  the same rule for every way of branching. After the case's opening, no later
  change on the trunk can replace that stretch. The stretch's opening and the
  fork are different instants, except for a fork at the case's opening
  (`PL-B8MK`, `PL-ZR49`). Each run records where it was opened from
  (`opened_from`), as `None` on a trunk and as this record on a branch, so every
  run knows which kind it is. A branch's run definition may open at a keyframe
  before the fork (`PL-B8MK`), so read the fork instant from the time at which
  the run began (`began_at_s`). That time is zero on a trunk and the fork on a
  branch.

  Each time the branch is read, it works out again which of the current marks
  the step ending at the fork crossed, in the same way for every branch. A mark
  added at an instant inside that step therefore counts as passed on the branch,
  as it does on the trunk (`PL-2N43`, `PL-XV0D`). The record stores no list of
  those marks, because a stored list would go on naming a mark that was removed
  and added back.
- A trunk and the branches taken from it are held by a `BranchedCase`, which
  makes two controllers one case rather than two unrelated sessions. The case
  forks only the trunk, so it has no way to make a branch of a branch, and needs
  no refusal to prevent one. Still, the method that branches at a keyframe
  (`resumed_at`) refuses to branch from a branch, for a caller that holds a
  branch directly.

**A branch inherits these from its trunk, and none of them is chosen again:**

- The agent and the patient. Changing either would make the branch a second
  case rather than a second management of this one. Choosing another agent
  (`set_agent`) already starts a new run for that reason, and is refused
  outright on a branch.
- The circuit volume, applied before any state is. Setting the volume
  (`BreathingCircuit.set_circuit_volume`) conserves agent by rewriting the
  inspired fraction, so a volume set afterwards would move the branch off the
  state it opened at.
- The four live controls, read from the trunk's stretch still open at the fork.
  That stretch holds the settings that the controls show there
  (`docs/MODEL.md` § "The canonical evaluation rule", `PL-ZR49`). The rebuilt
  branch is then checked against those settings rather than trusted. The check
  covers every setting the stretch carries, and the agent's displayed
  references, because the agent and the patient are read again from their data
  files. A refusal names each setting or reference that differs, and gives both
  of its values (`PL-NC62`).
- The marks. A mark is a question about what is still to come, and a comparison
  is two managements answering one question. If a learner had to re-enter the
  marks, two branches could be compared at different marks with nothing saying
  so.

A branch does not inherit the trunk's control timeline, because the branch's
record is of what the learner does to *it*. Its timeline opens only with copies
of the trunk's changes at the fork (`RunRecord.opened_with`). A reset
(`reset()`) reopens the branch through the code that opened it (`_open_at`),
with the settings the branch runs under. The reset keeps the record of where
the branch came from and the entries its timeline opened with. After those
entries, it records each setting that differs from the one the branch opened
under (`PL-K5BS`, `PL-ZR49`).

**A branch keeps the case's clock.** A branch continues the case's step count,
so every instant it gives is in case time. These include the elapsed time in a
snapshot (`snapshot().elapsed_s`), the time stamp of every control change, and
the instants of the drawn window (`drawn_window`) *and* of the run's segments
(`run_segments`). A branch's run definition (`RunDefinition`) opens at a
keyframe of the case rather than at a zero of its own, so a keyframe read from a
branch needs no conversion to be placed on the case's axis, and no code that
reads a run's instants has to know whether the run is a trunk or a branch.
`docs/MODEL.md` § "The canonical evaluation rule" explains why the definition
opens at a keyframe. A second time frame for branches once anchored a branch's
drawn columns to its own zero, so they landed at case instants the trunk never
draws (`PL-2R2C`). That frame has since been removed (`PL-ZMRT`).

No method restarts a branch's run definition at its fork, and none may be
relaxed into a restart on the grounds that the difference is small. A unit test
(`tests/unit/test_run_definition.py`) checks that a restart stops reproducing
the run it claims to continue, and `docs/MODEL.md` shows what a restart does.

### How a learner takes one, and how a comparison ends

A case (`BranchedCase`) holds a trunk run and every branch forked from it. At
start-up, the application builds a case and opens the dashboard over its trunk
(`app/main.py`). The application is therefore a case from its first frame,
never a single run that is later made into one (`PL-VKJW`). Three things follow
from this. Each is a property of the display, not of the model:

- **The branch control belongs to the case**, so it sits beside the bookmark
  panel in the dashboard (`SimulationView`), not in either run's view
  (`RunView`). One function decides what the control shows
  (`dashboard_frame.fork_offer`), and a widget draws it
  (`qt_widgets.ForkPanel`). A learner pauses at the decision point, or sets a
  mark there, a bookmark at which the run stops. The learner then forks at that
  point, so they read the bookmark panel before the branch control.

  When a learner returns to a mark, the trunk is kept, and their change is made
  on a branch drawn beside it. A learner who wants to try something else from
  the same point uses the branch's own Reset (project owner, 2026-10-12,
  ratified, over truncating the run at the mark after a confirmation as Gas Man
  does, `PL-ZW0J`).

  **The branch control has a selector and a button, because a learner can fork
  from points that last for different lengths of time** (`PL-TYWQ`, `PL-Y2SL`).
  The selector lists two kinds of row together, earliest first. The first kind
  is each instant in the case's list of fork points
  (`BranchedCase.fork_points_s`), and a branch from one opens at that instant
  (`fork_at`). The second kind is each mark that the trunk has passed
  (`BranchedCase.mark_fork_points`, `PL-W4XQ`), and a branch from one is taken
  through a separate method (`fork_at_mark`). A mark's row gives the instant at
  which its branch opens, and never the instant of the mark itself. The row
  adds "on your mark", the wording of the label shown when the run halts. The
  selector gains a row as the clock passes a mark, and loses one only when the
  learner removes that mark or the trunk starts over.

  Below the selector, a button takes a branch where the paused trunk stands
  (`BranchedCase.here_fork_point`). Pausing records no keyframe, so the paused
  point adds no fork point. Unlike a row in the selector, it lasts only until
  the run resumes. The button appears whenever the case offers that point and
  only one run is shown. Its label gives the instant at which the branch will
  open, as in "Branch here: 1h23m". When a mark stopped the trunk there, the
  label reads "..., stopped on your mark". A row and the button labelled with
  the same instant open their branches under the same settings, because each
  opens under what the dial says at its instant (`PL-ZR49`).

  The project owner chose these two controls (2026-09-21, ratified, over one
  list that grows a row while the run is halted). With one list, that row would
  vanish when the run resumed. A learner could notice that only by comparing the
  list with a remembered one, the stale-state case that
  `.claude/rules/expert-review.md` names. A control that vanishes can be noticed
  on sight. The owner chose them again (2026-10-12, ratified, over a row at the
  top of the selector selected by default), because a default selection that
  jumped to the paused point would move a choice the learner had made.

  The button takes its branch through a method that accepts no instant
  (`fork_here`). The method exists to prevent one hazard: a fork at the
  instant a learner *marked*, rather than at the step on which the run
  stopped. Because the button passes no instant, the interface cannot ask for
  that fork.

  The branch control takes the paused point from the **trunk**, not from the
  displayed runs (`fork_offer`), because the button's method forks the trunk
  and refuses to fork a branch. A control drawn from a branch's paused point
  would offer a fork that the case cannot take.
- **The dashboard can add a run after it opens** (`SimulationView.add_run`),
  so a branch taken during a session can be drawn. Whenever the set of runs
  changes, the dashboard rewrites both legends' run counts, the names the runs
  carry, the setting sections and the agent locks from the new set. At most two
  runs are shown (`MAX_DISPLAYED_RUNS`).
- **One comparison at a time, and Reset is the way out.** A comparison is two
  runs shown together, the trunk and one branch. There is no control for
  choosing which runs to show, because the roadmap defers it (`ROADMAP.md`
  § "Explicitly out of scope for v0.5.0"). Without such a control, a second
  branch could only replace the branch on screen while the first stayed in the
  case. The branch control is therefore locked while two runs are shown, and
  the lock gives its reason on screen.

  Resetting the *trunk* takes every branch off the dashboard and rebuilds the
  case on the restarted run, because a restarted trunk never passed through
  the instant at which a branch was taken. The trunk's Reset asks first when a
  branch has run past its fork or holds a control change made since it opened
  (`PL-W5WX`, `SimulationSnapshot.has_recorded_run`). The dashboard writes the
  question (`SimulationView._trunk_reset_question`) and hands it to the
  trunk's view through `RunView.ask_before_reset`. Resetting a *branch*
  returns it to its own fork and leaves the comparison in place.

  **The lock says which Reset to press, in the words on the screen**
  (`PL-WG73`). Its sentence (`comparing_fork_lock_text`) takes those words from
  the run's label and the Reset button's label, `run_label` and `RESET_LABEL`,
  so it cannot name a control that is not there. An instruction to "Reset the
  case" fails, because the Reset a learner reaches for is the branch's, on the
  run they are trying to end. That press leaves the comparison and its lock in
  place.

**No agent may be chosen while two runs are shown** (`PL-QRD1`). A branch
refuses an agent change outright (`set_agent`), so its view shows the agent as
a chip in place of the agent selector. On the trunk, an agent change
*succeeds*, which is worse. Without a lock, the switch would restart the trunk
while the case went on listing a branch of a run that no longer existed. The
shared MAC axis would then make the chart refuse the frame
(`assemble_chart_frame`), so both runs would fail because of an input to one of
them (`_halt_every_run`).

The trunk's agent selector is therefore locked while a comparison is shown
(project owner, 2026-09-20, ratified, over keeping the selector live and adding
to the confirmation dialog in `RunView._confirm_new_case` a clause about the
branches that an agent change would orphan). This follows the preference in
`.claude/rules/expert-review.md` for an interface that prevents an error over
one that reports it afterwards. Ordinary evidence is enough to reopen the
decision with the owner: a learner who wants to change agent during a
comparison, a measurement, or a cost that the reasons above leave out.

The chip names the longest-lasting lock that applies, so it never sends a
learner to Pause for a lock that Pause cannot lift. One function computes all
three locks and makes that choice (`dashboard_frame.transport`).

### What a branch comparison asserts, and which part of it is structural

**The code structure described above guarantees three parts of what a branch
comparison asserts.** A branch comparison shows one case managed two ways.
`docs/MODEL.md` § "What a branch comparison asserts, and what it does not" gives
the full claim.

**The comparison is always between a trunk and one branch of it, and the
structure enforces this.** A branched case (`BranchedCase`) forks only its trunk,
so it cannot represent a branch of a branch. The screen shows at most two runs
(`MAX_DISPLAYED_RUNS`), and there is no run selector.

**After the fork, a difference between the two runs can come only from their
control timelines.** A branch inherits the trunk's agent, patient, circuit
volume and bookmarks, and the four live controls up to the fork. It keeps these
fixed, so that a difference between the runs cannot come from any of them. For
example, the agent cannot be changed on a branch (`set_agent` refuses), and on
the trunk it is locked while two runs are shown. The control timeline is the
one thing a branch does not inherit. The branch's timeline opens with only the
trunk's changes at the fork, if there are any.

**Before the fork, the two runs use the same history object, not a reproduction
of it.** A branch's definition holds the trunk's own keyframe, and both runs sit
in the case's single time frame. So the runs agree by construction, not within a
tolerance. `docs/MODEL.md` § "What this requires of a branch" states this and
reports a difference of zero between the runs.

After the fork, the structure sets no limit on how far the runs may diverge. A
difference between them is a property of the model, not an expected clinical
difference. Neither run is a prediction for a patient at any point, because the
model describes one reference adult and no variability around it.

## Data files (`data/`)

Each agent, patient and machine profile is a validated, cited JSON file under
`data/`. To add a profile, write its file, and put any parsing support the file
needs in `core/parameters.py`. Never put its values in `core/` as constants.

Each value belongs in exactly one of three directories, by what it describes:

- `data/agents/` for what the drug does.
- `data/patients/` for who is being anesthetized.
- `data/machines/` for the apparatus that delivers the drug, namely the
  breathing system's volume and the default fresh gas flow.

Filing a machine parameter in a patient file would misstate where it comes from
(`PL-4YY1`).

Each file holds a `schema_version`, an `id`, the parameter values, and a
`sources` array of citations. Each entry in `sources` has the fields `citation`,
`url`, `note` and the three below (`core.parameters.SourceReference`):

- `tier` is one of the three tiers that `docs/MODEL.md` § "Source hierarchy"
  defines (`core.parameters.SOURCE_TIERS`).
- `adopted` says whether the file names the source as the authority for a value
  it stores, whatever the source's tier.
- `authority_for` lists the stored values for which the source is the
  authority, each named by the dotted key path that the provenance table uses.

A file that adopts no primary source carries a top-level `provenance_gap` that
says so.

The code that reads the files (`core/parameters.py`) rejects a file that:

- lacks a required field, or uses an unsupported schema version.
- gives a `tier` outside the three tiers, or an `adopted` that is not a JSON
  boolean.
- gives an `authority_for` that is empty when `adopted` is true, or not empty
  when it is false.
- names in `authority_for` something that is not one of the file's stored
  values, or names a stored value twice.
- holds a value outside its validated range, such as a non-positive volume, or
  tissue perfusion fractions that do not sum to 1.
- carries a key that the schema does not declare, including a key inside a
  nested object such as `tissue_gas_partition_coefficients` or a `sources`
  entry.

A script reads every `authority_for` and prints the source and tier behind each
stored value, file by file and in total (`python3 tools/source_tier_counts.py`).
Its output gives the counts that `docs/MODEL.md` states, but the script does not
check them. It never blocks a change (`PL-9LXK`).

## User state: the saved Workspaces

The application writes two things outside its own tree: the reader's saved
Workspaces, and the reader's preferences, which § "User state: the reader's
preferences" below describes. The store in `layout/store.py` keeps the whole
set of Workspaces (`WorkspaceSet`) in a single JSON file, under one
`schema_version`. For each Workspace, the set holds its layout and each View's
saved state, including which run the View is pinned to. It also holds the
order of the Workspaces and which one is active. No run's data is saved. A
pin names a run only by its identity, so in a later session the pinned run
is absent (`PL-7Z84`). The design follows `PL-SSQW` (project owner, 2026-09-27,
ratified) and question Q4 of `PL-WV9K` (project owner, 2026-09-27, specified).

- **Where.** The file is saved in the directory that Qt reports for
  `QStandardPaths.AppDataLocation`. On macOS the directory is
  `~/Library/Application Support/<App>`. On Windows it is
  `%APPDATA%\<Org>\<App>`, in the Roaming folder, because the file holds no
  window geometry and its sizes are fractions. On Linux it is
  `~/.local/share/<App>`. In these paths, `<Org>` is the organization name
  and `<App>` the application's display name, both defined in `app_metadata`
  (`APP_ORGANIZATION_NAME` and `APP_DISPLAY_NAME`). If a platform reports no
  directory, the session saves nothing and tells the reader so.

  The store is given its directory and does not work one out itself. Qt
  reports the directory once the organization and application names are set,
  so the entry point (`app/main.py`) sets them before it asks (`PL-DWHG`). A
  test passes the store `tmp_path`. For a headless or portable run, the
  environment variable `ANESTHESIA_SIM_USER_DIR` overrides the directory. It
  is the only override, and it is applied in `store.user_data_directory`.
- **When.** The store writes only when the reader chooses "Save as default"
  in the Layout menu, never when something changes. A first run leaves no
  trace. "Save as default" first asks a question that names the file it will
  write. The two entries next to it write nothing: "Restore shipped Workspaces"
  and "Reset all layouts" (`PL-DWHG`).

  The save writes a temporary file beside the target and `fsync`s it. It then
  copies the current file to `workspaces.json.previous`, so that one prior
  generation survives. Finally it `os.replace`s the target. As a result, only
  a crash in the middle of the replace can leave the current file torn. A
  failed save raises `WorkspaceFileError`, which names the path and the
  reason. The error is reported where the action was invoked, on the line
  under the Workspace tabs.
- **The shipped set** that the store falls back to is three Workspaces in
  `data/workspaces/`, one JSON file each, in the saved file's format
  (`PL-KXTL`). In `layout/shipped.py`, they are read by the same code that
  reads the saved file. That module requires them to be at the current
  `schema_version`, because a shipped file is never migrated. "Reset this
  Workspace" reads one shipped file again, by its id.
- **What a launch does with the saved file** depends on the file's
  `schema_version` and on whether the file can be read. The entry point loads
  the set (`open_workspaces` in `app/main.py`). The store returns the whole
  outcome in `store.Loaded`, so that the interface can show it on the line
  under the Workspace tabs. There are five cases.
  - *none*: the launch shows the shipped set and says nothing.
  - *older*: the launch migrates the file in memory with
    `layout/migrations.py`, one step per version. The reader is told only
    where a step lost information. At the next save, the file as it was
    before migration is kept once as `workspaces.v<N>.json`.
  - *newer*: the launch refuses the file and leaves it untouched. It shows
    the shipped set and turns saving off for the session. A notice names the
    file and both versions.
  - *unreadable*: the launch handles the file as it handles a newer one.
  - *invalid at a version this build reads*: the launch sets the file aside
    unchanged as `workspaces.invalid-<UTC time>.json`. It loads
    `workspaces.json.previous` if that file validates, and the shipped set
    otherwise. A notice says which one it loaded, and saving stays on.

  A saved View of a kind that this build has not registered is not a file
  error. The file loads, and the Area that holds the View shows a failure
  state (`PL-R1WQ`).

  The one-version rule in `core/parameters.py` is right for files that ship
  with the code but wrong for a file that the reader wrote, so the store does
  not use it.

## User state: the reader's preferences

A preference belongs to the reader, not to a layout, so the preferences are
kept in their own file, `preferences.json`. It sits beside the layouts file,
`workspaces.json`, in the reader's data directory, outside this repository
(`PL-MQHN`, `PL-93B3`). Only the preferences module (`app/preferences.py`)
reads and writes the file. That module imports no Qt.
<!-- absent: preferences.json workspaces.json -->

The file holds at most one price for each shipped agent (`AgentPrice`), and the
unit in which the agent cost View shows the delivered agent: millilitres of
liquid or litres of vapour. `docs/MODEL.md` § "A cost at the reader's price"
specifies what a price carries and what is refused. The project ships no price.

- **What a launch does with the file.** Startup code in `app/main.py` opens the
  preferences store (`open_preferences`) in the directory it finds for the
  layouts file. The store's load method (`PreferencesStore.load`) returns the
  preferences to use, whether saving is on, and any notice, in one
  `LoadedPreferences` result. With no file, there is no price or notice, and
  the unit is millilitres of liquid. If a newer build wrote the file, or the
  file cannot be read or checked entry by entry, saving is turned off for the
  session, so the file is left as it is. The notice says why. Otherwise, each
  entry is checked. A refused price is not used, and no default takes its
  place. A refused unit falls back to millilitres of liquid. Either way, the
  notice says what was refused and why. Until the reader replaces a refused
  entry, each save writes it back unchanged, and the agent cost View shows the
  notice about it.
- **Who uses the preferences.** The dashboard holds the preferences, as it
  holds the compartment selection. It passes them to every View in each tick
  (`ViewTick`). Only the agent cost View uses them (`PL-B396`). It asks the
  dashboard to change the unit (`ViewRequests.agent_cost_unit`), so two agent
  cost Views always show the same unit.
- **When the file is written.** The preferences store writes the whole file when
  asked (`PreferencesStore.save`). The dashboard saves as soon as the reader
  picks the agent cost View's unit (`PL-B396`) or sets or removes a price
  (`PL-1P15`), the way Blender saves its preferences. Nothing is written before
  the first save.
- **How a save works.** A save writes a temporary file, calls `fsync` on it and
  replaces the old file with it (`os.replace`). The store takes these steps
  through the module that also saves the layouts file (`user_files.py`). No
  backup is kept, because the file is small and the reader can set a price
  again. When a save fails, the change lasts only for the session, and the agent
  cost View says so.

## Dependencies

**`pyproject.toml` declares four runtime dependencies:** `PySide6-Essentials`,
`pyqtgraph`, `numpy` and `pydantic`. pyqtgraph already depends on numpy, but
the project declares numpy too, as it does every package that it imports. The
import check forbids the former dependencies `flet` and `flet-charts` in every
module under `src/` (`tools/import_boundary_check.py`, `PL-3SQT`).

**In `src/`, numpy is used only for the chart's arrays.** The Qt chart module
(`app/qt_chart.py`) hands pyqtgraph every curve's points as `numpy.ndarray`s,
the form that pyqtgraph's performance guidance asks for (`PL-TCNT`). The import
check forbids numpy in every module under `core/`, so the model's propagator
stays in pure Python, as `docs/MODEL.md` § "The reproducibility guarantee"
describes. The chart-frame module (`app/chart_frame.py`) does not import numpy
either, because a frame holds plain values and only the toolkit layer converts
them to arrays. The tests also use numpy: one decomposes the model's
open-circuit system with `numpy.linalg.eig`
(`tests/reference/test_late_washout_against_published_fits.py`, `PL-921Y`).

**On Linux, the Qt wheels need shared objects from five OS packages.** Running
`ldd` on 2026-09-16 showed that the wheels' `Qt/lib/libQt6Gui.so.6` and
`Qt/plugins/platforms/libqoffscreen.so` link to the shared objects below, which
resolve outside the wheels.

| shared object | Debian/Ubuntu package |
| --- | --- |
| `libEGL.so.1` | `libegl1` |
| `libGL.so.1`, `libGLX.so.0`, `libGLdispatch.so.0` | `libgl1` |
| `libxkbcommon.so.0` | `libxkbcommon0` |
| `libdbus-1.so.3` | `libdbus-1-3` |
| `libfontconfig.so.1` | `libfontconfig1` |

Only `libegl1` is normally missing, because an ordinary desktop already has the
other four. `README.md` § "Running it" therefore names only that package. The
CI workflow (`.github/workflows/quality.yml`) also installs only `libegl1`,
because the `ubuntu-latest` image has the other four (`PL-VHLZ`). A minimal
container is neither an ordinary desktop nor that image, so check it for all
five packages. macOS and Windows need nothing extra.

**A bundled build will bring licence obligations, and nothing is violated today
(`PL-3SQT`).** `pyside6_essentials` 6.11.2 and `shiboken6` 6.11.2 both declare
`LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`. Neither wheel ships the licence
text: when checked on 2026-09-16, their `dist-info` metadata held no `licenses`
directory and no `License-File:` entry. This repository is Apache-2.0 and has no
`NOTICE` file. The LGPL obligations are dynamic linking, a recipient's ability
to relink, and conveying the licence text. They attach when a binary is
*conveyed*. This project conveys none, because building from source is the only
way to run it (`README.md` § "Running it") and `uv` installs each wheel from PyPI
for each user. A bundled build is part of the packaging work in `ROADMAP.md`.

pyqtgraph is MIT, and numpy is
`BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0`. Both wheels ship their
licence text.

## The workflow apparatus

A separate document, [`docs/apparatus.md`](apparatus.md), maps the scripts
under `tools/`, the hooks under `.claude/hooks/` and the third-party text that
their tests read. All three exist so that agent sessions can build the
simulator, and nothing under `src/` imports them. That document is held to the
apparatus standard in `.claude/rules/apparatus-standard.md`, not to the
specialist standard in `CLAUDE.md` that applies to this document (`PL-KRGY`).

A script (`tools/doc_check.py`) checks the package map above against the tree
on disk. A module added without a line in the map fails `make check`, and so
does a line left behind after its module is deleted.

## Tests (`tests/`)

- **`tests/unit/`** — tests of one module's behavior in isolation, such as a
  compartment, a validator, a parameter loader, the controller and the
  displayed-value formatters. One test checks what the dashboard would show on
  each tick, with no toolkit loaded (`test_dashboard_frame.py`). Every
  operation and refusal of the area layout is tested in `test_layout_model.py`,
  `test_layout_serialization.py`, `test_layout_workspace.py`,
  `test_layout_migrations.py` and `test_layout_store.py`, which runs against
  `tmp_path`.
- **`tests/integration/`** — components wired together as the app assembles
  them, such as the controller driving a full agent-uptake system
  (`AgentUptakeSystem`). The directory's tests of the Qt interface include
  these:
  - A test draws the Qt chart headless against a real run, and reads back the
    plotted items and the painted pixels (`test_qt_chart.py`).
  - A test covers the dashboard's leaf widgets (`test_qt_widgets.py`).
  - A test drives the whole dashboard against real controllers, and reads back
    every widget's text, enablement and visibility (`test_simulation_view.py`).
  - A test renders the whole dashboard headless at one fixed size, and reads
    back the painted pixels and the laid-out geometry (`test_qt_rendering.py`).
    It also writes the kind of screenshot that the instructions for running
    the app explain how to take (`.claude/skills/run-the-app/SKILL.md`,
    `PL-YCWZ`, `PL-CQRL`).
  - A test checks what the interface draws when the *host* is set to a dark
    appearance (`test_dark_appearance.py`). It sets a dark host's palette on
    the `QApplication`, whereas the other tests set a palette on one widget.
    It does so because the code under test declares palettes (`PL-RKRY`).
- **`tests/reference/`** — analytic or independent reference cases that the
  implementation must reproduce. Examples are the closed-form circuit wash-in
  solution, the sevoflurane patient reference scenario, and the from-scratch
  RK4 integration of the coupled system in `test_coupled_dynamics.py`.
  These are the regression tests referred to throughout the release gate in
  `docs/MODEL.md`. A reference case may import the parameter loaders but must
  not use a solver in `core/`, because its value is that it was derived
  independently of the code it checks.
- **`tests/benchmarks/`** — measurement harnesses, which the test runner does
  not collect. A harness that imports PySide6 and the simulator's package
  belongs here rather than in `tools/`, because it runs only inside the project
  virtualenv. `make check`, CI and the hooks run `tools/` scripts with a bare
  `python3` outside the virtualenv, so those scripts may use only the
  standard library.

  One harness drives a real dashboard frame by frame under Qt's `offscreen`
  platform (`frame_cost.py`). For each frame it times the simulation
  (`controller.advance`), the assembly (`SimulationView.present`) and the
  paint (`QApplication.processEvents`). Running
  `uv run python tests/benchmarks/frame_cost.py` therefore shows how the time
  splits between the simulation and the interface (`PL-ZG5J`). It takes about
  three seconds and prints the timings for a person to judge. A collected test
  in the same directory checks that the harness still runs and still reports
  the stages it names (`test_frame_cost.py`). That test asserts nothing about
  a duration, because a threshold would measure the runner rather than the
  code.

The test suite renders on a runner with no display, because the test
configuration in `tests/conftest.py` selects Qt's `offscreen` platform plugin
before any `PySide6` import. On Linux that plugin needs `libegl1` from the OS.
The PySide6 wheels do not carry it, so the CI workflow in
`.github/workflows/quality.yml` installs it (`PL-VHLZ`).

## Where new code belongs

- A new physiological compartment or coupling → `core/`. Document its
  equations and reference cases in `docs/MODEL.md` first, as `CLAUDE.md`
  requires.
- A new agent, patient or machine profile → a new validated, cited file under
  the matching subdirectory of `data/`. A compartment in `core/` takes a value
  from such a file as a required argument, with no default that restates it.
  The breathing circuit takes its volume this way (`BreathingCircuit`,
  `PL-M85T`).
- A number the code needs → one place, and every use refers to it by its name.
  A scientific value lives in a cited data file under `data/`. A unit
  conversion factor lives in `core/units.py`. Any other number is a
  module-level constant in the module that owns the quantity. Other modules
  import that constant and never declare it a second time. A check
  (`tools/literal_home_check.py`) rejects a copy in either of two forms: a bare
  numeric literal other than 0, 1 and 2 anywhere under `src/anesthesia_sim/`,
  or a numeric constant defined in more than one module. The check's baseline
  lists the literals that existed before the check, and the baseline only
  shrinks. Each finding names any constant with the same value, and the
  contributor decides whether that constant is the same quantity (`PL-40SJ`).
- A new View → a class in `app/views.py`. A View is a widget shown in an Area.
  An Area is a part of the layout that holds one View, and any View can occupy
  any Area. A View never shows a value from the unconditional set, the values
  that `docs/MODEL.md` § "Minimum displayed outputs" requires on screen at all
  times.

  The class is a `QWidget` and satisfies the `View` protocol in
  `app/view_contract.py`, whose module docstring states the contract. It is
  built from its context (`ViewContext`) alone. It draws what each update
  (`ViewTick`) gives it. It does not assume its size, its neighbours, or that
  it is alone (`.claude/rules/ui-areas.md`). It asks for a change to shared
  state through the context's requests, and it never holds that state itself.
  The concentration View (`ConcentrationView`) is the example to read from end
  to end.

  Then register the View in `app/view_registry.py`. Give it a tag, written as
  a literal. Beside the tag, add a registry entry (`RegisteredView`) that names
  the class as its factory. Every Area's chooser lists the new View at once
  (`PL-50PZ`). Saved layouts name a View by its tag, so a tag never changes.
  When a View is renamed or removed, its tag goes into the list of retired
  tags (`RETIRED_TAGS`) with the release that retired it. A retired tag is
  never registered again (`PL-R1WQ`). A test
  (`tests/integration/test_view_contract.py`) builds the View, checks it
  against the protocol, and checks that it reads back the state it saves.
- A new display panel or control outside the Areas → three places. Two parts
  of the layout are outside the Areas: the region that shows the unconditional
  set, and the case section below the Areas. Anything an Area holds is a View,
  built as the entry above describes (`PL-TH35`). The setting controls are a
  View (`PL-2KXB`).

  What the panel shows goes in `app/dashboard_frame.py`, as a plain value with
  a test in `tests/unit/test_dashboard_frame.py`. The widget that draws it goes
  in `app/qt_widgets.py`, and that widget decides nothing. The code that places
  the panel goes in `app/run_view.py` or `app/simulation_view.py`.

  To choose between those two files, ask whose panel it is. A panel that
  states one run's numbers belongs to the per-run container (`RunView`).
  Examples are readouts, settings, transport controls, and the record of what
  was changed during the run. The dashboard places such a panel by looping
  over its runs. A panel about the chart that both runs are drawn on belongs
  to the simulation's container (`SimulationView`) or to the chart View that
  draws it. Examples are an axis, a legend, a reference, and the compartment
  selection. A chart's time window belongs to that chart View alone
  (`PL-L59K`).

  A control that applies to the whole case, rather than to one run, also
  belongs to the simulation's container. The bookmark editor is the worked
  example (`PL-LPLD`). It writes each mark to every displayed run, so that the
  runs' controllers all hold the same marks. The branch control is the second
  example (`PL-VKJW`). The instants it offers are the trunk's keyframes, so a
  copy of it in each run would give a branch a control that could only
  refuse.

  Putting a panel in the wrong container misleads the user. If a run's panel
  were placed once on the dashboard, it would show one run's numbers as though
  they applied to both. Copying a shared control into each run would let the
  user interpret a comparison made under two different settings. A View must
  avoid both mistakes as well.

  Moving a panel or View into a second top-level window has been wanted but
  unscheduled since 2026-09-26 (the second half of item 34). Once that is
  built, `docs/MODEL.md` § "Minimum displayed outputs" decides which window
  each panel or View is created in.
- A value that the display needs and does not yet have → add it to
  `app/controller.py`, and compute it in `core/`, never in the code that
  displays it. A panel reads only what the run's snapshot already carries
  (`SimulationSnapshot`) and the states that the controller returns for a span
  of the run (`DrawnWindow`). Those states are held per substance. A trace
  addresses one value in them by a recorded series (`RecordedSeries`), not by
  a named field. A recorded series pairs a substance with a recorded quantity
  (`RecordedQuantity`).

  When a panel shows a span of the run rather than one instant, it asks the
  controller for the span it draws
  (`SimulationController.drawn_window(start_s, stop_s, columns)`), never for
  the whole run. The states come back evaluated at the instants that the panel
  plots, so the amount of data the panel receives is limited by the display,
  not by the length of the run.
- A new way of *rendering* a value that the user interprets →
  `app/formatting.py`. Examples are a unit, a decimal count, or a marker for
  what the display cannot resolve. Write it as a pure function with its own
  test, and record the reason for it in `docs/MODEL.md` § "Displayed precision".
- A new stylesheet, or a change to how a widget is styled → a function in
  `app/stylesheets.py` that builds the stylesheet string from the values in
  `app/theme.py` and returns it. Neither module imports the Qt toolkit. A new
  colour is first added as a token in `app/theme.py`. Every `setStyleSheet`
  call under `app/` passes a call to a function in `app/stylesheets.py`
  (`PL-Y4YX`). A test (`tests/unit/test_stylesheets.py`) fails any call that
  does not. A widget may paint a colour from a palette role, such as an
  entry's fill or a check box's indicator. Declare that colour with the
  function for interface colours (`qt_widgets.declare_interface_colours`),
  never with a stylesheet (`.claude/rules/ui-color.md`).
- A new chart series, or a change to how one is drawn → two modules. What the
  series shows goes in `app/chart_frame.py`. How pyqtgraph paints it goes in
  `app/qt_chart.py`.

  A new *compartment* trace is one record in the table of compartment traces
  (`chart_frame.COMPARTMENT_TRACES`). The record gives four things together:
  the quantity the trace draws, how it is drawn, the legend words that name
  it, and the explanation in its hover text. The table belongs to the chart,
  not to any one run. The function that assembles the chart
  (`assemble_chart_frame`) reads the table once per run, for the substance
  that the run's snapshot names. The run is recorded under that substance's
  identifier.

  The chart draws the compartments that the user has selected on the dashboard
  (`ChartFrame.visible` is the dashboard's `CompartmentSelection`). The legend
  shows that selection and asks to change it, but does not hold it
  (`PL-VN6M`). Once the chart shows more than one run, it draws at most a fixed
  number of the selected compartments (`compared_compartments`,
  `COMPARED_COMPARTMENT_CAP`). So the painting code in `app/qt_chart.py` keeps
  one curve per run per trace and moves each curve to match. Nothing is edited
  directly.

  A curve's width comes from the run's trace style
  (`chart_frame.run_trace_style`), not from the table, because the width tells
  two runs apart while both are drawn. A new trace in the table therefore
  declares no width.

  Two kinds of series stay out of the table, because the table binds each
  trace to one recorded series. One is a series that draws no state of the
  run, such as a clinical reference or a control mark. It must meet the
  labelling requirement that `docs/MODEL.md` § "Interface boundary" sets in
  place of the drawn-point rule. The other is a trace of a derived quantity
  with a domain, such as the wash-in ratio. Its value is sometimes absent, so
  it has no recorded series to bind to. State such a trace's domain in
  `docs/MODEL.md` and at the point of display.
