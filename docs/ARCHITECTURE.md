# Architecture overview

This document describes how the code under `src/anesthesia_sim/` is organized
and how data flows through it. It is a map for contributors, not a scientific
specification. To find where a change belongs, start at § "Where new code
belongs", the last chapter.
§ "Layering" says what an Area, a View and a Workspace are.
For the equations, units, parameter provenance, and numerical method, see
[`docs/MODEL.md`](MODEL.md). For version history and milestones, see
[`ROADMAP.md`](../ROADMAP.md). For the origin of the interface's area and
workspace model, see [`docs/interface-provenance.md`](interface-provenance.md).
That document says which parts of Blender were studied, under which licence
rules, and what this project deliberately does differently.

## Layering

The codebase is split into four independent layers. The direction of imports
enforces the split, and the import check (`tools/import_boundary_check.py`)
verifies it at every `make check`. Never edit code to get around that check.

```text
data/  --loaded by-->  core/  --read by-->  app/
                                             ^
                    layout/  --read by-------+
```

- **`core/`** is the scientific simulation. It has no dependency on the UI
  toolkit, no wall-clock time, and no I/O beyond reading the packaged JSON
  files in `data/`. Every quantity it produces is deterministic for identical
  inputs.
- **`app/`** is the PySide6 user interface. It advances no part of the model.
  It reads immutable snapshots from `core/` through the controller
  (`app/controller.py`), and the chart also reads the states it plots through
  `SimulationController.drawn_window`. It derives a value only for display: a
  fraction as a percent or a MAC multiple, a drawn value in its axis unit, the
  F_A/F_I ratio, and the liquid agent used as a cost at the reader's price.
  Each of these sits in a module that loads no toolkit and has its own tests:
  `app/formatting.py`, `app/chart_frame.py`, `app/wash_in.py` and
  `app/agent_cost.py`. `app/compartment_schematic.py` computes each
  container's fill and each compartment's share of the agent held, and
  `tests/unit/test_compartment_schematic.py` tests it. `app/` forwards user
  input back as setter calls.
- **`layout/`** is the area layout as a value. A window is divided into
  **Areas**, and each Area holds one **View**: a widget such as a chart or the
  setting controls. Any View can occupy any Area. A **Workspace** is a named
  layout, holding each View's saved state and the run it is pinned to. A
  pinned Workspace's Views draw that run alone, and the tabs above the Areas
  switch between Workspaces. `layout/` records which View occupies which part
  of each window, and it provides the operations a reader performs on the
  layout (`PL-C842`, `PL-1FT6`).

  `layout/` imports no toolkit, so every operation is tested without a
  `QApplication`. The only part of `core/` that it reads is
  `core/checked_number.py`, for the way that module names a refused value. In
  `layout/`, only the store (`store.py`) writes outside the tree. It writes the
  reader's saved Workspaces, as § "User state: the saved Workspaces" describes.
  The one list of the View kinds that a layout may name is
  `app/view_registry.py` (`PL-R1WQ`), because the `layout/` package holds no
  such list.
- **`data/`** holds the cited parameter files that `core/` reads, and the
  shipped Workspaces, which `layout/` reads. § "Data files (`data/`)" describes
  both.

Three rules rest on this layering. The first is that simulation code stays
independent of the UI toolkit. This section states that rule, and the import
check enforces it (`PL-ZYHX`). The second is that no simulation calculation
belongs in a UI callback. `.claude/rules/ui-calculations.md` states that rule,
and it loads with every file under `app/`. The third is that model parameters
live in validated, versioned data files and never as executable code.
`CLAUDE.md` § "Architecture and development discipline" states that rule, and
the parameter loader rejects a formula where a number is expected
(§ "Data files (`data/`)").

**What the import check rejects.** Under `core/`, it rejects `PySide6`,
`pyqtgraph`, `numpy` and any import of `app/`. Under `layout/`, it rejects
`PySide6`, `pyqtgraph` and any import of `app/`. Anywhere under `src/`, it
rejects the former dependencies `flet` and `flet-charts`. § "Dependencies" says
why each declared package is present. The check also enforces other
boundaries, such as keeping the wall clock out of `core/`. The full list, each
boundary with its reason, is `BOUNDARIES` in `tools/import_boundary_check.py`.

## Package map

A script (`tools/doc_check.py`) checks this map against the tree on disk. A
module added without a line in the map fails `make check`, and so does a line
left behind after its module is deleted.

```text
src/anesthesia_sim/
├── user_files.py        # the atomic write of a user's file, shared by the Workspaces and the preferences stores (§ "User state: the saved Workspaces", PL-93B3)
├── app_metadata.py      # app name, bundle id, and the version the header shows: the installed distribution's version, plus the commit where the running code is not a clean checkout of the released tag, because between two releases every build otherwise displays the same string and a fix confirmed by eye cannot be told from the code it replaced
├── core/                # scientific simulation — no toolkit dependency
│   ├── validation.py              # shared input-validation guards (raise SimulationConfigurationError; a value that is not a number at all is a TypeError, as for every checked type)
│   ├── checked_number.py          # what a checked type, and the two sign-and-finiteness guards in validation.py, are built from: an int or a float and nothing else, never a value built as another checked quantity, with minus zero held as zero; the base every checked type shares; and how a refusal names a value
│   ├── concentration.py           # fraction vs percent: the two forms, and the only crossing
│   ├── units.py                   # seconds, minutes, hours, milliseconds, and litres to millilitres and cubic metres: the factors between them, each written once
│   ├── supported_ranges.py        # the declared domain: FreshGasFlow, AlveolarVentilation and CardiacOutput, which cannot hold a flow outside it, CaseInstant, which cannot hold an instant outside the run length, StepCount, a whole nonnegative count, and the guards that refuse a run outside it
│   ├── simulation_step.py         # the run's step: its supported range, and SimulationStep, which cannot hold one outside it
│   ├── numerical_envelope.py      # where core's arithmetic is shown correct: CompartmentVolume and PartitionCoefficient, which cannot hold a volume or a coefficient outside it, and the one place the tissue:blood quotient is formed
│   ├── blood_flow.py              # a tissue group's perfusion fraction and its blood flow: PerfusionFraction, which cannot hold a fraction of 0 or less or a fraction above 1, and BloodFlow, which is built only as a PerfusionFraction of a CardiacOutput
│   ├── exceptions.py              # exception hierarchy; every core failure is inside it
│   ├── parameters.py              # load + validate agent/patient/machine JSON data
│   ├── liquid_agent.py            # the 20 °C reference condition's molar volume, LiquidDensity, and the conversion of an amount of vapour into the millilitres of liquid agent it came from (PL-KZ99)
│   ├── circuit.py                 # breathing circuit compartment
│   ├── alveolar.py                # alveolar gas compartment
│   ├── blood.py                   # venous blood compartment
│   ├── tissue.py                  # one perfusion-limited tissue group
│   ├── exponential_approach.py    # the first-order approach to a held input, each compartment's own closed-form step in the advance methods of blood.py, tissue.py and circuit.py; not how a run advances, which is AgentUptakeSystem.advance alone: formed from the value held for a step closing up to half the gap and from the equilibrium beyond, exact at zero flow and at a full approach
│   ├── patient.py                 # PatientCompartments: VRG + muscle + fat + venous blood
│   ├── governing_equations.py     # MODEL.md's balance equations as one system matrix
│   ├── matrix_exponential.py      # exp(A dt) for a compartment system; no physiology in it
│   ├── uptake_system.py      # couples circuit + alveoli + patient; AgentUptakeSystem.advance is a run's step, one exact propagation of the whole system
│   ├── run_definition.py               # a run as its settings over time; any state in closed form
│   ├── agent_simulation_validation.py  # mass-balance / agent-accounting tracker
│   └── simulation.py              # SimulationState: explicit elapsed time (bounded) + AgentUptakeSystem
├── app/                  # user interface - PySide6 and pyqtgraph since PL-25KS (ROADMAP.md § "Completed: v0.4.26 - the interface moves to Qt")
│   ├── controller.py               # SimulationController: run controls, read-only snapshots; ResumePoint and BranchedCase: where a branch opened, and the trunk it belongs to
│   ├── run_series.py               # the vocabulary a run's drawn values are addressed by, and the window one frame reads them from: RecordedQuantity, RecordedSeries, DrawnWindow; toolkit-independent
│   ├── unconditional_set.py        # docs/MODEL.md's unconditional set as data: UnconditionalValue, its tiers, SubstanceInstance and INHALED_AGENT, read by the region that holds it (PL-NWTM); window_region, what each top-level window's region owes (PL-W54S); toolkit-independent
│   ├── control_record.py           # what a run's settings are addressed by and the change a run records: ControlInput, CONTROL_INPUT_DISPLAY_UNITS and CONTROL_INPUT_UNITS, control_value (which settings field holds each control's value, PL-000W), ControlChange; toolkit-independent
│   ├── display_units.py            # DisplayUnit: each unit the interface states, with its recorded spelling, the label beside a value and its chart axis title, so the record, the panel, the formatters and the chart read one member (PL-G84G); toolkit-independent
│   ├── bookmarks.py                # what a learner marks a case at, held in two collections: TimeBookmark (an instant), MacTarget (a height on one compartment), BookmarkSet; toolkit-independent, and it detects a crossing between two readings it is handed (§ "What a branch is, and what it shares with its parent")
│   ├── simulation_view.py          # SimulationView on PySide6: what runs share - the unconditional region above the layout container, which refuses a run lacking a declared value, the compartment selection every View is shown, the chart frame a tick assembles for each window a chart View asks for (PL-L59K), the case section of bookmarks and branching under the Areas, the render tick, and the Workspaces: the tab strip over the Areas switches among them, and a pinned Workspace's Views draw its run alone (PL-2KXB); no domain logic
│   ├── area_layout.py              # AreaLayout: the one module that builds QSplitters, every one from a layout.LayoutModel; a drag on a border becomes LayoutModel.resize and every splitter follows the new model (PL-W9P6), stopping in WARNING at an Area's least size, moving one border alone with Shift and undone by Escape; a border in the tab order moves one step per arrow key, and the Area menu's Resize entry gives one the focus (PL-M352); a right-click on each Area's header opens an AreaMenu that splits, joins, swaps or closes it, and a corner drag splits or joins it, or with Ctrl swaps it, with a preview drawn over the Areas (PL-2KXB, PL-R5G4); each Area is an AreaFrame whose header holds a ViewChooser listing every registered kind, and a choice is LayoutModel.set_view (PL-50PZ); each Area's View is built by its registry entry's factory, saved when replaced, and drawn from each ViewTick (PL-TH35); an Area whose View kind is not registered, or whose factory fails, shows an AreaNotice instead (PL-R1WQ); no View is drawn below its need, and an Area that cannot be given it shows the size it needs (PL-K285); load draws another Workspace from its layout and View state, and a pinned Workspace's run is named in every Area's header, or stated absent in place of each View (PL-2KXB)
│   ├── workspace_tabs.py           # WorkspaceTabs: the Workspace tab strip above the Areas, drawn from a WorkspaceSet it does not own; shipped tabs first, a rule, then the reader's own; each tab's menu entry worked out before it is shown, Delete and Reset asking first, and rename in place (PL-QW1Z, PL-2KXB); a Layout menu, opened by a right-click on the strip outside a tab, lists every Workspace and holds the current one's entries, and Ctrl+PgUp and Ctrl+PgDn step through them (PL-M352, PL-R5G4); the entries that save and restore Workspaces are in § "User state: the saved Workspaces" (PL-DWHG)
│   ├── view_contract.py            # the View contract every View implements: the View protocol, the ViewContext it is built from, the FrameRequest naming the window and width it draws, the ViewTick it is drawn from, the RunSurfaces a View may show, ViewRequests for a change to shared state or a frame, including the agent cost View's unit and the reader's price for an agent (PL-B396, PL-1P15), PreferencesInForce, the reader's preferences each tick shows every View (PL-B396), and the saved-state version check (PL-TH35)
│   ├── views.py                    # the shipped Views, each a QWidget satisfying view_contract.View: ConcentrationView, WashInView, ParameterControlsView, AccountingView (PL-TH35) and CompartmentSchematicView, which shows one RunSchematic per displayed run, each a run surface its run writes, withholds and names (PL-RNYV), and AgentCostView, which shows one RunAgentCost per displayed run in the unit the reader's preferences hold, with a selector that asks the dashboard to change it (PL-B396), the cost at the reader's price, and the form that sets that price (PL-1P15); each chart View holds and saves its own time window and writes the lines that depend on it from its own frame (PL-L59K)
│   ├── view_registry.py            # the View registry: each View kind's tag, written once as a literal, its RegisteredView entry with the factory that builds it, and RETIRED_TAGS for a tag renamed or removed; REQUIRED_REACHABLE, the kinds a build fails on import without (PL-50PZ); the text of the missing-kind and failed-build notices (PL-R1WQ)
│   ├── run_view.py                 # one run's widgets, controller, handlers, refresh and halt; RunView, instantiated once per run (the seam PL-B9PY drew)
│   ├── halt_gate.py                # halt_gate: every slot of RunView and SimulationView is called through it (§ "Failures and halts", PL-HJKN); toolkit-independent
│   ├── run_surfaces.py             # the parts of a run that may sit in an Area, each built any number of times from the values it draws: ParameterControls, AccountingPanel, and keep_until_destroyed, which keeps the list of live copies RunView writes (PL-9LNF); the third such part, RunSchematic, is in qt_schematic.py, and the fourth, RunAgentCost, in qt_agent_cost.py
│   ├── qt_widgets.py               # PySide6 leaf widgets that decide nothing: MetricPanel, ReadoutRow, ParameterSlider, NoticeLabel, NewCaseDialog, BookmarksPanel, ForkPanel, initial_window_geometry
│   ├── formatting.py               # modeled value -> displayed string: a percent, and a multiple of the running agent's 1 MAC; toolkit-independent
│   ├── currency_code.py            # the one rule for a currency code, three capital letters, which the preferences store and the cost formatters both read (PL-1P15); toolkit-independent
│   ├── preferences.py              # the reader's preferences.json: an AgentPrice per agent and the agent cost View's unit (§ "User state: the reader's preferences", PL-93B3); toolkit-independent
│   ├── playback.py                 # playback rate -> whole simulation steps per tick; toolkit-independent
│   ├── dashboard_frame.py          # what the dashboard claims about one run at one instant, as plain values: the status word, the notice and its precedence, the readouts and their glosses, the setting controls, the transport enablement, the accounting panel, the control-change list, the two bookmark listings, the captions and the new-case question; toolkit-independent
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
│   └── main.py                     # PySide6 entry point (§ "What a branch is, and what it shares with its parent" and the two User state chapters); the window opens maximized (PL-Z4K6) over a sized, centred normal geometry (PL-005)
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

## Data files (`data/`)

`data/` holds versioned, schema-validated parameter files (JSON) with
citations. Every scientific constant that a shipped run uses comes from one of
these files. § "Where new code belongs" says how to add an agent, patient or
machine profile.

Each value belongs in exactly one of three directories of `data/`, by what it
describes:

- `data/agents/` for what the drug does.
- `data/patients/` for who is being anesthetized.
- `data/machines/` for the apparatus that delivers the drug, namely the
  breathing system's volume and the default fresh gas flow.

Filing a machine parameter in a file under `data/patients/` would misstate where
it comes from (`PL-4YY1`).

When the code builds the compartments for an agent from the data files
(`AgentUptakeSystem.for_agent()`), it passes each value explicitly. Each value
that a data file states is a required argument of its compartment, with no
default, so `core/` holds no second copy of it (`PL-M85T`). One default is left.
When a machine file states no fresh gas flow, a run opens at the flow that
`core/circuit.py` defines (`TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN`). A test keeps
that default equal to the flow in the shipped machine file
(`test_the_flow_default_matches_the_shipped_machine_file`). A value written only
in `core/` would be invisible to the check of where each value comes from
(`tools/doc_check.py`), which sees only constants in data files.

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

- lacks a required field, or uses an unsupported schema version
  (`_validate_schema_version`).
- gives a `tier` outside the three tiers, or an `adopted` that is not a JSON
  boolean.
- gives an `authority_for` that is empty when `adopted` is true, or not empty
  when it is false.
- names in `authority_for` something that is not one of the file's stored
  values, or names a stored value twice.
- holds a value outside its validated range, such as a non-positive volume, or
  tissue perfusion fractions that do not sum to 1
  (`require_perfusion_fractions_sum_to_one`).
- gives a formula where a number is expected, which the typed payloads in
  `core/parameters.py` reject.
- carries a key that the schema does not declare, such as a field whose name
  gives another unit. This includes a key inside a nested object, such as
  `tissue_gas_partition_coefficients` or a `sources` entry.

Every payload model inherits `_StrictPayload`, which forbids an undeclared key
rather than silently discarding it, so the schemas are strict at every nesting
level. As a result, a data file cannot document one model while the app runs
another.

A script reads every `authority_for` and prints the source and tier behind each
stored value, file by file and in total (`python3 tools/source_tier_counts.py`).
Its output gives the counts that `docs/MODEL.md` states, but the script does not
check them. It never blocks a change, by the project owner's decision
recorded on `PL-9LXK`.

`data/workspaces/` holds the shipped Workspaces. These are layout rather than
parameters: `layout/shipped.py` reads them, and nothing in `core/` does, so
nothing above in this chapter applies to them. § "User state: the saved
Workspaces" describes the shipped set.

## Data flow

**Startup / parameter loading**, in `SimulationController._build_state()`:

```text
data/agents/<agent_id>.json                 ──┐
data/patients/reference_adult.json          ──┤
data/machines/reference_circle_system.json  ──┴─> core/parameters.py
                                        (parse + validate schema, units, ranges)
                                        │
                                        ▼
                      AgentUptakeSystem.for_agent(agent_id)
                          (circuit + alveoli + patient compartments)
                                        │
                                        ▼
                              SimulationState (adds elapsed_s)
                                        │
                                        ▼
                            app/controller.SimulationController
```

`core/parameters.py` is the only module that reads the JSON files, which it
does through `importlib.resources`. It checks each file before it constructs
`AgentParameters` / `ReferenceAdultParameters` /
`BreathingCircuitParameters`, and § "Data files (`data/`)" lists what the check
rejects. Nothing downstream re-reads these values from disk or derives them
again.

**Each simulation step**, `AgentUptakeSystem.advance()` advances the whole
coupled system at once. It does so by one exact propagation, rather than by
a sequence of separate exchanges between compartments or a generic numerical
integrator:

1. `core/governing_equations.py` assembles the system matrix `A`. Each entry
   is one term of one balance equation in `docs/MODEL.md`,
   "Governing equations".
2. `core/matrix_exponential.py` computes `exp(A dt)`. This is the system's
   exact propagator, because every setting is held constant across a step.
   The result is cached against the settings it was built for, and it is
   rebuilt when one of those settings changes.
3. One matrix-vector product, `matrix_exponential.propagate()`, advances the
   agent fraction in each of the six compartments. The same solution also
   advances the cumulative delivered and exhausted amounts.
4. The agent-accounting validator (`AgentSimulationValidator`) records those
   amounts and checks mass balance. It raises
   `AgentSimulationValidationError` if the check fails. The error carries the
   failing check, because the step is then rolled back and the run's own
   accounting no longer holds the rejected step's totals (`PL-HF4B`).

The package is arranged around the split of concerns between steps 1 and 2. The
equations file, `core/governing_equations.py`, contains the physiology and no
arithmetic. The exponential file, `core/matrix_exponential.py`, contains the
arithmetic and no physiology.

**The controller (`SimulationController`, in `app/controller.py`) stands
between the interface and the core.** It owns a `SimulationState`. It exposes
`start()` / `pause()` / `reset()` / per-parameter setters, and it produces an
immutable `SimulationSnapshot` on request. It has no default values and no
bounds of its own. Every unspecified setting comes from what
`AgentUptakeSystem.for_agent()` built from the data files. When the core
rejects a setting, such as a delivered concentration above the agent's
vaporizer maximum, the error is raised out of the core. At this boundary, the
controller neither clamps the setting nor replaces it with a default.

Conservation of agent also belongs to the core. The core's circuit-volume
setter (`set_circuit_volume`) conserves agent itself (`PL-006`). Before
`PL-006`, the controller read the circuit's stored agent out and put it back
around `set_circuit_volume`. That left `core/` exposing a public primitive
that did not conserve agent, and only the one caller that knew to compensate
kept the invariant. The controller calls the setter once, from `_build_state()`,
to apply the volume the session was built with, and no live setter exists
above it. The circuit volume is a fixed model parameter rather than a control
(`PL-GYH2`). So the per-parameter setters named above are the four that the
interface offers, and no fifth one exists. `docs/MODEL.md` § "What is not
bounded this way" gives the argument.

The snapshot is the run's state at one instant. It holds a fixed number of
values, however long the run has been going. Values across the run are
returned separately, by `drawn_window(start_s, stop_s, columns)`. That method
evaluates the states at the instants that a chart is about to plot, across the
axis the caller names, and returns them as a `DrawnWindow`. So the amount of
data that passes from the controller to the view is limited by the display, not
by the length of the run. The snapshot once carried every sample that the run
had recorded. A frame's cost therefore grew with the length of the run, while
the chart discarded all but the few hundred samples inside its axis (`PL-0VM7`).

The snapshot does carry the run's control-change timeline (`ControlChange`),
with one entry per setting that the model was actually stepped under.
Re-applying the timeline therefore reproduces the run rather than approximating
it. A timeline's length is bounded by how often a user touches a control, not
by how long they watch.

The snapshot carries each compartment's agent amount as one record,
`CompartmentAgentAmounts`, keyed by the compartment's `RecordedQuantity`
(`PL-KFTM`). `app/compartment_schematic.py` labels each container of the
compartment schematic from it (`PL-RNYV`), and the schematic's share bar is
drawn from it (`PL-S79P`). `snapshot()` reads each amount from that
compartment's `agent_amount_l` in `core/`, so the interface computes no amount
of its own. The record is keyed rather than ordered, so a container looks its
amount up by the compartment it draws and cannot be handed a neighbour's.
Because amounts are not in the state vector, `snapshot()` pairs each key with
its `core/` object by hand, beside the traces' pairing in
`run_series.COMPARTMENT_STATE_INDEX`. The reference test against the coupled
oracle is what catches a wrong pair. A later model that holds several
substances keys the same record by substance too, rather than adding fields.

The record holds the parts and not their total. The snapshot's
`stored_agent_l` is still the accounting check's reading, `core/`'s one sum of
the six amounts (`AgentUptakeSystem.total_stored_agent_l`), because summing the
record again in `app/` would be a second sum of the same fact. Instead, a unit
test checks that the six amounts, added in `core/`'s order, equal
`stored_agent_l` to the last bit, and a reference test compares each amount
with oracles that do not read `core/`.

**A run is its inputs, and its states are derived from them** (PL-T691).
The controller holds the run as a `RunDefinition` (`core/run_definition.py`).
The definition holds the settings in force at each moment, plus one keyframe
per change, and nothing else of the run. A keyframe is the state at the instant
of its change. The equations are linear and time-invariant while the settings
stay the same, so the propagator is exact over any horizon, not only over a
step. Every state that the run passed through is therefore one propagation from
the latest keyframe at or before it, and none of those states has to have been
recorded. `RunDefinition.evaluate(start_s, stop_s, columns)` and
`evaluate_anchored(start_s, stop_s, spacing_s)` perform that evaluation. The
chart uses the second, through `SimulationController.drawn_window`. The
chart's evaluation keeps the propagators that its last window used, so that the
next frame can reuse them. Each propagator is a function of settings that the
definition already holds, so no drawn value depends on whether it was kept
(`RunDefinition.evaluate_anchored`, PL-CNCF).

`run_segments` hands out the record itself as frozen segments, which can be
read but not advanced. So nothing above the controller can move the run
definition's reach past where the run actually got to, and then have a
prediction drawn back on the run's own axis. `docs/MODEL.md` § "The run is that
record, and every state is derived from it" gives the measurements, and
`docs/MODEL.md` § "The canonical evaluation rule" states which of the two
evaluation paths a stored, exported, replayed or branched value may be taken
from.

**The boundary between drawn values and the run's states is a type rather than
a convention.** `evaluate` and `evaluate_anchored` return `DisplayState`
values, which are not state vectors. So a drawn column cannot become a
keyframe, an exported figure or a branch's opening state just because it holds
the same nine numbers in the same order. `RunDefinition` rejects such a value
as an opening state by name. A layer above the controller therefore cannot
cross that boundary by forgetting that it is there.
Forgetting is the only way that a boundary stated in prose is ever crossed.

**The run definition is the only record of the run.** What the chart draws is
what `drawn_window` evaluates, so nothing exists behind those states that could
disagree with them. `PL-2FM6` deleted the per-step sample history that the
controller once kept beside the definition, because the samples were a second
copy of the run. Until then, `docs/MODEL.md` § "Closed-form agreement test"
held the two in agreement with each other.

Which instants `drawn_window` evaluates is a presentation-correctness concern,
because a chart that stepped over a control change would show a curve the
simulation never produced. So the rules that place the instants are stated in
`docs/MODEL.md` § "What the chart draws" and are tested on their own. The
evaluated instants are anchored to an absolute grid measured from the case's
zero, rather than to their position within the window. So a window that
follows the run keeps every column it had and gains at most one
(`RunDefinition.evaluate_anchored`). `PL-Q197` set this rule for recorded
samples, and `PL-2FM6` carried it over to evaluated columns.

The chart-frame module (`app/chart_frame.py`) is the layer above that anchored
evaluation. It holds the rule of one column per pixel, with that rule's
minimum column count (`chart_columns`). It reads the window once per run for
every trace, and converts each drawn value into the unit of its own axis. It is
a layer of its own because which quantity a line carries is a correctness
claim, as the placing of the instants is. That claim is declared once, beside
the traces themselves, in `chart_frame.COMPARTMENT_TRACES`. The unit conversion
belongs to the layer that knows the axis. The six compartment traces are drawn
in percent, and the wash-in ratio in its own dimensionless unit.

`app/run_view.py` and `app/simulation_view.py` read only the snapshot and
`drawn_window`. A `RunView` builds one run's controls, and it wires the slider
and button callbacks through `_apply_setting` to the controller's setters. The
`SimulationView` drives the charts that every run shares. Each transformation
that they apply is a module of its own: `app/formatting.py`,
`app/chart_frame.py` with `app/qt_chart.py`, `app/dashboard_frame.py` with
`app/qt_widgets.py`, `app/control_timeline.py`, `app/playback.py` and
`app/wash_in.py`. Each is separate because it decides presentation
*correctness* rather than layout, and must be readable and testable with no
toolkit loaded. § "Package map" gives each one's role. `app/formatting.py`
uses the resolutions that `docs/MODEL.md` § "Displayed precision" derives.

`app/control_timeline.py` reads a control record that is faithful to the run,
in which a drag of one slider appears as several settings. So collapsing that
drag into one displayed act is a claim about what the user did, not a tidier
rendering of what the model saw.

In `app/wash_in.py`, the wash-in quotient has a domain. It is undefined before
any agent reaches the circuit, and above 1 it stops being a wash-in fraction.
So the module returns the value and the reason together, and the chart draws
the trace in segments that break where the domain does. `docs/MODEL.md`
§ "F_A/F_I as a displayed ratio" is the specification.

In `app/playback.py`, a playback rate is realised only as a step *count*, never
as a larger step. So the module derives the count from the rate, and it rejects
a rate that does not land on a whole number of steps. Otherwise the run would
advance at a rate other than the one it displays, a presentation failure that
looks like a working feature.

The MAC divisor is passed to the formatter as an argument, from
`SimulationSnapshot.agent_mac_percent`, rather than being looked up. The
divisor is what makes a displayed multiple specific to the agent, so it
travels with the value it divides. The agent's MAC-awake travels the same
way and for the same reason, as `SimulationSnapshot.agent_mac_awake` beside
that divisor. The chart's MAC-awake band is one of these values multiplied by
the other, so pairing two different agents' values would place a correct
number at the wrong height.

Stepping and drawing run on separate timers with separate intervals
(`SIMULATION_TICK_INTERVAL_S` and `RENDER_INTERVAL_S`), so simulation time stays
a function of the steps taken rather than of how long a frame took.
§ "Failures and halts" says what the timers do on a halt.

## What a branch is, and what it shares with its parent

A **branch** is a second live run of the same case, opened at a state the first
run passed through. The run it was taken from is the **trunk**, and the instant
at which it was taken is its **fork**. The whole structure, `BranchedCase`, is
one trunk with N branches. Sub-forks, meaning branches of a branch, are
excluded, not merely unimplemented (project owner, 2026-08-25). They multiply
without bound and offer little over branching from the trunk again.

This section is the object map of `BranchedCase`, its runs and the
`RunDefinition` each run carries. What a branch *guarantees* is stated and
measured in one place only:
`docs/MODEL.md` § "The canonical evaluation rule". That section says that a
branch's run definition opens at a keyframe of the case, and why. It says that
the definition opens at that keyframe's own case instant, so no clock is
re-based and no conversion is performed. It also says what both of these are
worth in floating point. The same section's "What this requires of a branch"
says which keyframe is used, and how it relates to the instant at which the
branch itself began.

Five things in `app/controller.py` implement a branch:

- `SimulationController.resumed_at(instant_s)` makes a branch at one of the
  trunk's keyframes. It builds a second controller through the ordinary
  constructor, with the settings of the trunk's stretch that opens at
  `instant_s`, so the branch runs under the change recorded there. It then
  seeds the new controller's system with the trunk's canonical state at
  `instant_s`, which is the trunk's run definition evaluated at that instant,
  and returns the controller paused. The trunk is read and never written. So
  the two runs share no compartment, no accounting and no clock, and that is
  what lets both be advanced.
- `SimulationController.resumed_here()` makes a branch where the paused trunk
  stands, whether or not it stopped on a bookmark halt (`PL-Y2SL`). The two
  methods share `_branch_from`, so this method makes the branch that the bullet
  above describes, and only the place where the fork may be taken differs. So a
  setting that the learner changed on the trunk while it stood there is on the
  branch (`PL-HSP8`, `PL-ZR49`). The method deliberately takes no instant,
  because the fork is wherever the clock stands. So a caller has no float with
  which to name an instant the run has not reached. Nor can anyone confuse the
  instant a learner *marked* with the step instant the run actually stopped on.
  The method refuses a running trunk, a failed one, and one standing at its
  opening (§ "Failures and halts" says what a failed run and a halt are). It
  also refuses one at the supported run length, where a branch would have no
  step to take. `here_fork_point` returns its result from the same check, so an
  offer built from it cannot disagree with `resumed_here`. By the **crossing
  rule**, a step crosses a mark when the mark lies between the readings on
  either side of it. The branch opens on the crossing of the step it stands on,
  meaning the marks that step crossed. That crossing is computed again from the
  marks as they are at each read, in the same way for every branch. So a mark
  added inside the halting step counts as passed on the branch, just as it does
  on the trunk (`PL-2N43`, `PL-XV0D`).
- `SimulationController.resumed_at_mark(bookmark)` makes a branch at a time
  bookmark that the trunk has passed. The run may have halted there, or the
  learner may have marked the instant after the clock went past it (`PL-W4XQ`).
  It gives the branch that a halt on that mark would have given, taken late.
  The fork is the end of the step that reached the mark, and
  `TimeBookmark.steps_to_reach` finds that step from the crossing rule itself.
  The branch opens from the trunk's canonical state there, exactly as a fork
  after a halt does. The method takes the mark rather than an instant, for the
  same reason that `resumed_here` takes nothing. `mark_fork_points` lists the
  marks it accepts, each with the instant at which its branch would open. A
  mark on the supported run length is not listed, and `_resume_point` rejects a
  fork there for every method, because the branch would have no step to take
  and its Reset would return it to the same stop (`PL-VHQX`).
- `ResumePoint` records where the branch came from. It holds the trunk stretch
  that the step reaching the fork ran under, the fork's instant and the
  canonical state there, the case's step count at the fork, the step that ends
  at the fork, and the agent that the branch's accounting period started from.
  It holds no crossing, because a crossing stored with the marks it named would
  go on naming a mark that was removed and added back (`PL-XV0D`). So at each
  read, the branch asks again what the step ending at its fork crossed.
  `opened_from` is `None` on a trunk and a `ResumePoint` on a branch, so every
  run knows which kind it is. The stretch's opening and the fork are two
  instants for every fork except one at the case's opening (`PL-B8MK`,
  `PL-ZR49`). `reset()` goes back through the same `_open_at`, with the
  settings the branch runs under. So a reset opens the branch on the same
  provenance and keeps the entries it opened with. After them, it records each
  setting that differs from the one the branch opened under (`PL-K5BS`,
  `PL-ZR49`).
- `BranchedCase` holds a trunk and the branches taken from it. It is what makes
  two controllers one case rather than two unrelated sessions. It also makes the
  one-trunk shape a matter of structure rather than of a refusal: the trunk is
  the only run that `BranchedCase` will fork, so a sub-fork is not an operation
  it can express. `resumed_at` keeps its own refusal for a caller that holds a
  branch directly.

**What a branch inherits, and why each is not re-chosen.** A branch inherits the
agent and the patient, because changing either would make it a second case
rather than a second management of this one. `set_agent` already starts a new
run for that reason, and it refuses outright on a branch. A branch inherits the
circuit volume, applied before any state is, because
`BreathingCircuit.set_circuit_volume` conserves agent by rewriting the inspired
fraction. A volume set afterwards would move the branch off the state it opened
at.

When `SimulationController.resumed_at` opens a branch, the branch inherits the
four live controls, read from the settings of the trunk's stretch, which hold
each value as it was set. The rebuilt branch is then checked against those
settings rather than trusted. The check covers every setting the stretch carries,
and the agent's displayed references, since the agent and patient are read again
from their data files. A refusal names each setting or displayed reference that
differs, with both of its values (`PL-NC62`). For every way of branching, one
rule decides which stretch the branch names as its provenance: the stretch that
the step reaching the fork ran under. After the case's opening, no later change
on the trunk can replace that stretch. The branch runs under the stretch still
open at the fork, which is what the dial says there
(`docs/MODEL.md` § "The canonical evaluation rule", `PL-ZR49`).

A branch inherits the bookmarks but not the trunk's control timeline, and one
test settles both. A mark is a question about what is still to come, and a
comparison is two managements answering one question. If a learner had to
re-enter the marks, two branches could be compared at two different heights
with nothing saying so. The timeline is not inherited, because the branch's
record is of what the learner does to *it*. The only entries that the branch's
timeline opens with are copies of the trunk's changes at the instant the
branch was taken (`RunRecord.opened_with`). A reset keeps them, and records
after them each setting that the learner changed and the reset kept.

`opened_from` records where the fork was taken. Read the fork instant only
from `began_at_s`, which is zero on a trunk and the fork instant on a branch.
The property exists because the definition's own first segment no longer
always starts at the fork, so the instant cannot be inferred from it
(`PL-B8MK`).

**One time frame, and every reader is in it.** A branch continues the case's
step count. So `snapshot().elapsed_s`, every control-change stamp,
`drawn_window`'s instants *and* the instants `run_segments` hands out are all
in case time. A branch's `RunDefinition` opens at a keyframe of the case rather
than at a zero of its own. So a keyframe read from a branch needs no conversion
to be placed on the case's axis, and no reader has to know which kind of run it
holds. *Which* keyframe depends on the fork. For a branch taken at a control
event, it is the fork itself. For a branch taken at a bookmark, it is the
keyframe at or before the fork.

A branch once had a second time frame, offset from the case's by
`SimulationController.origin_s`. `advance` and `drawn_window` subtracted that
offset, and `run_segments` warned about it. The branch's drawn columns were
anchored to its own zero, so they landed at case instants the trunk never draws
(`PL-2R2C`). The frame was removed, with `origin_s` and both subtractions
(`PL-ZMRT`), and that solved the problem without a separate fix.
`docs/MODEL.md` § "The canonical evaluation rule" measures what the removal is
worth.

**Where a branch may be taken.** There are three places: at a keyframe, where
the paused trunk stands, and at a time bookmark the trunk has passed. Each is
reached by its own method of `BranchedCase` rather than through one list:
`fork_at`, `fork_here` and `fork_at_mark`.

The first is at any keyframe the trunk holds. These are listed by
`BranchedCase.fork_points_s` and taken with `fork_at`. The keyframes are the
trunk's opening at induction and every setting change the model was actually
stepped under. Any *other* instant that a caller names to `fork_at` is refused
as belonging to another method, not as an instant a branch could not reproduce
(`PL-54V0`). The two methods below both fork between keyframes and reproduce
the trunk exactly. No method *restarts* a branch's definition at its fork.
`docs/MODEL.md` measures what a restart does, and
`tests/unit/test_run_definition.py` checks that a restart really does stop
reproducing the run it claims to continue. So the construction every method
uses is never relaxed into a restart on the grounds that the difference is
small.

The second is **where the paused trunk stands**, with `fork_here` (`PL-Y2SL`).
A learner who pauses to think tries something else from that instant in one
action, without marking it first (project owner, 2026-10-12). A bookmark halt is
one such pause. `app/bookmarks.py` defines what a learner may mark (`PL-LPLD`).
`SimulationController.advance` halts a run on the step that crosses a mark
(`PL-CTD7`). It reads every compartment on either side of each step, and pauses
the run where a mark lies between the two readings.

Where a run stands is not, in general, a setting change. On a 120 s run with
two control changes, 3 of the 1 201 instants it can stand at are keyframes. So
the trunk holds no keyframe there, and nothing records one. The branch's
*definition* opens at the keyframe at or before the fork
(`SimulationController._keyframe_before`), while its clock and
its live system stand at the fork. This costs the trunk nothing and reproduces
it element-wise. The obvious route was measured and refused. Recording a
keyframe where the run halts makes the branch exact against the trunk it forked
from, but it also moves that trunk's own later results away from what the case
would have given unmarked, so marking a run would change it. Both measurements
are in `PL-B8MK`. `docs/MODEL.md` § "What this requires of a branch" records
which of that section's two conditions the chosen route relaxes, and what the
relaxation costs.

The paused point is a permission rather than a standing offer. It ends when the
trunk starts again, because the point where a running trunk stands moves with
every step. A failed trunk offers no paused point either, because a failure is
not a pause. Nor does a trunk at the supported run length, which is a stop
rather than a pause and leaves a branch no step to take. Nor does a trunk
standing at its opening, where `fork_at` already opens a branch. The paused
point is not part of a widened `fork_points_s`, because such a list would
change its members as the run moved. A caller holding an instant from it could
then ask for a fork at an instant the run no longer stands on.

The third is at any **time bookmark the trunk has passed**. These are listed by
`BranchedCase.mark_fork_points` and taken with `fork_at_mark` (`PL-W4XQ`). This
is what a learner paused at three hours does after marking the one-hour point.
The instant is behind the clock. The trunk holds no keyframe there and is not
standing on it, and nothing in the bookmark fork's construction needed either.
The branch opens on the step on which the mark is reached, which is the instant
a halt would have stopped the run on. The branch's state is the trunk's
definition evaluated there, so the branch is the one the halt would have given.
Unlike the paused point, this list does not end at the next step. A mark joins
the list when the clock reaches it, or when a mark is set behind the clock. It
leaves the list only when the learner unmarks it or the trunk starts over,
which is the same lifetime that the keyframes have. A MAC target is not on the
list, because it has no instant. A fork at a height is taken through
`fork_here`, where the height's halt stops the run.

### How a learner takes one, and how a comparison ends

`app/main.py` builds the `BranchedCase` and opens the dashboard over its
trunk. So the application is a *case* from its first frame, not a run that
might later be made into one (`PL-VKJW`). Three things follow from this. Each
is a property of the display, not of the model:

- **The branch control belongs to the case**, so it sits beside the bookmark
  panel in `SimulationView` rather than in either `RunView`. It offers
  `BranchedCase.fork_points_s`, `BranchedCase.mark_fork_points` and
  `BranchedCase.here_fork_point`, and it takes the branch through `fork_at`,
  `fork_at_mark` or `fork_here`. `dashboard_frame.fork_offer` decides what the
  control shows, and `qt_widgets.ForkPanel` draws it. A learner pauses at the
  decision point, or marks it and is stopped there, and then forks at that
  point, which is the order in which the two panels are read. Returning to a
  mark forks the run rather than truncating it. The trunk is kept, and the
  change is made on a branch drawn beside it. A learner who wants to try
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
  opens and with "on your mark", in the halt label's wording, so the row never
  states where the mark itself lies. Below the selector, a second button takes
  the branch at the point where the paused trunk is, through `fork_here`. The
  button is on the panel whenever `BranchedCase.here_fork_point` offers that
  point and no comparison is shown. It is labelled "Branch here: 1h23m", with
  the instant at which the branch will open. When a mark stopped the trunk
  there, the label is "..., stopped on your mark". Every entry and the button
  open under what the dial says at their instant, so two controls labelled
  with one instant open under the same settings (`PL-ZR49`).

  Pausing records no keyframe, so the paused point adds nothing to
  `fork_points_s`. The selector therefore never loses a row as the run moves.
  It gains a row as the clock passes a mark, and it loses a row only when the
  learner unmarks that mark or the trunk starts over. The project owner chose
  this shape (2026-09-21, ratified, over one list that grows a row while the
  run is halted; and 2026-10-12, ratified, over a row at the top of the
  selector selected by default). The reasons are these. A row that vanishes
  from a list can be noticed only by comparing the list with a remembered one,
  which is the stale-state case that `.claude/rules/expert-review.md` names. A
  control that vanishes, by contrast, can be noticed on sight. And a default
  selection that jumped to the paused point would move a choice the reader had
  made.

  The button passes no instant to `fork_here`, which takes none. That method
  exists to prevent one hazard: a fork asked for at the instant a learner
  *marked*, rather than at the step on which the run stopped. Because the
  button names no instant, that hazard cannot be expressed through the
  interface either. `fork_offer` takes the paused point from the **trunk**,
  not from the displayed runs, because `fork_here` forks the trunk and refuses
  a branch. A panel drawn from a branch's paused point would offer a fork that
  the case cannot take.
- **`SimulationView.add_run` is how a run reaches the dashboard after
  construction** (`PL-VKJW`), so a branch taken during a session has
  somewhere to be drawn. Both legends' run counts, the names the runs carry,
  the setting sections and the agent locks are rewritten from the run set
  whenever it changes. The cap is `MAX_DISPLAYED_RUNS`, which is two.
- **One comparison at a time, and Reset is the way out.** There is no run
  selector, because `ROADMAP.md` § "Explicitly out of scope for v0.5.0" defers
  it. So a second branch could only replace the displayed one, while the first
  went on living inside `BranchedCase`. The branch control is refused while two
  runs are shown. The refusal is visible, and its reason can be read. Resetting
  the *trunk* takes every branch off the dashboard and rebuilds the case on the
  restarted run, because a trunk that has started over never passed through
  the instant at which a branch was taken. Where a branch has run past its
  fork, or holds a control change made since it opened, the trunk's Reset asks
  first (`PL-W5WX`, `SimulationSnapshot.has_recorded_run`). The question comes
  from `SimulationView._trunk_reset_question`, which `RunView.ask_before_reset`
  hands to the trunk's view. Resetting a *branch* returns it to its own fork
  and leaves the comparison in place. **The lock says which of those two
  Resets it means, in the words shown on the screen** (`PL-WG73`).
  `comparing_fork_lock_text` fills its sentence from the run's label and the
  Reset button's label, `run_label` and `RESET_LABEL`, so an instruction cannot
  name a control that is not there. An earlier lock that said "Reset the case"
  failed because the Reset a learner reaches for is the branch's, on the run
  they are trying to end. That press returns the branch to its fork, while the
  lock stays exactly where it was.

**No agent may be chosen while two runs are shown** (`PL-QRD1`). A branch's
`set_agent` refuses outright, so its `RunView` shows the agent chip in place of
the selector. The trunk's `set_agent` *succeeds*, which is the worse case. The
switch restarted the trunk, but `BranchedCase` went on listing a branch of a
run that no longer existed. `assemble_chart_frame` then refused the frame over
the shared MAC axis. So the method that halts every run
(`SimulationView._halt_every_run`, § "Failures and halts") failed both runs
because of an input to one of them. The trunk's selector is therefore locked
while a comparison is shown too (project owner, 2026-09-20, ratified, over
keeping the selector live and growing `RunView._confirm_new_case`'s dialog a
clause about the branches it would orphan). This follows the preference in
`.claude/rules/expert-review.md` for an interface that prevents the error over
one that reports it afterwards. The decision was ratified rather than
specified, because the case put to the owner was a session's own
recommendation. So ordinary evidence is enough to put it back to them: a
learner who wants to change agent mid-comparison, a measurement, or a cost the
case did not carry. `dashboard_frame.transport` carries all three locks and
names the longest-lasting one that applies, so the chip never sends a reader
to Pause for a lock that Pause cannot lift.

### What a branch comparison asserts, and which part of it is structural

**The full statement is in `docs/MODEL.md` § "What a branch comparison asserts,
and what it does not".** It is stated there because it is a claim about the
model, not about how the code is arranged. This section covers only the part of
that claim that the structure of `BranchedCase` decides, which is three things.

**The comparison is a trunk and one branch of it, and the structure enforces
this.** `BranchedCase` forks only its trunk, so it cannot express a branch of
a branch. The display shows at most two runs (`MAX_DISPLAYED_RUNS`), and there
is no run selector. So what is on screen is always one case managed two ways.
It is never a survey of N managements, and never one branch compared with
another. A reader who generalises the drawing into a wider facility goes past
what the structure can build.

**What may be attributed to the settings that differ is exactly the
complement of what a branch inherits.** A branch carries across the agent,
the patient, the circuit volume, the four live controls up to the fork, and
the bookmarks. It then keeps them fixed: `set_agent` refuses on a branch and
is locked on the trunk while two runs are shown. The control timeline is the
one thing not carried across. It opens with only the trunk's changes at the
fork, if any. So the difference between two runs after the fork is the
difference between two control timelines. The inheritance list above is the
audit of that claim, not a convenience.

**The shared history is the same object, not a reproduction of one.** A branch's
`RunDefinition` carries the trunk's own `Keyframe`, and both runs sit in the case's
single time frame. So the runs agree before the fork by construction, not
because they meet a tolerance. `docs/MODEL.md` § "What this requires of a
branch" is where that is stated and measured, and the residual it leaves is
zero. The structure does *not* supply any bound on what happens after the fork.
Neither run is a prediction for a patient at any point, because the model
contains one reference adult and no variability around it. So a difference
between the two runs is a property of the model, not an expected clinical
difference. That last point is the one that a reader of a drawn comparison is
most likely to need. `docs/MODEL.md` § "What a branch comparison asserts, and
what it does not" is where it is argued.

## Failures and halts

Every failure that `core/` reports is a subclass of
`AnesthesiaSimulationError` (`core/exceptions.py`), never a bare
`ValueError`. That lets the interface recognise a simulation failure and act
on it. The hierarchy has two kinds, which mean different things and get
different treatment:

- `SimulationConfigurationError` means that a value was rejected before it
  changed anything. The guards in `core/validation.py` raise it. So do the
  checked types' constructors (`Fraction`, `Percent` and `MacPercent` in
  `core/concentration.py`, and those in `core/supported_ranges.py`,
  `core/simulation_step.py`, `core/numerical_envelope.py` and
  `core/blood_flow.py`). Compartment
  constructors and setters raise it too. So does a compartment field written
  directly, because its record checks every write in `__setattr__` (`PL-19Y0`).
  The parameter-file loaders raise it as well. The view's `_apply_setting`
  catches it, restores the control from the snapshot, and says that the setting
  was refused. The run is untouched and keeps going. Three cases raise
  `TypeError` instead, as a programming error rather than a refused setting. The
  first is a setter, or a compartment field written directly, that is handed a
  value not built as its type. The second is a checked type built from something
  it does not accept. That means a `bool`, a `Decimal` or a string for any
  checked type, and a `float` for `StepCount`, which is built from an `int`
  alone. For all of them, it also means a value already built as another checked
  quantity. The checked type raises before it reads the range
  (`core/checked_number.py`). The third is the two sign-and-finiteness guards in
  `core/validation.py`. They also reject an `int` past the float range by name.
  They do not let `math.isfinite` raise `OverflowError` while converting it
  (`PL-3800`). A concentration that the display builds is not a setting. If one
  is refused there, the run halts. No supported setting causes such a refusal
  (`PL-7DJK`).
- `SimulationExecutionError` means that a step began and could not be
  completed, so the run must stop. The same holds for its subclasses,
  `SimulationNumericalError` and `AgentSimulationValidationError`.
  `AgentUptakeSystem.advance()` is what makes the distinction between the two
  kinds. It checks its own arguments first. Then it restates any guard failure
  raised during the step as a `SimulationNumericalError`, and it keeps the
  original as `__cause__`. It is also what makes the step atomic. It captures
  every dynamic value before the step and restores them all on any failure. So
  what is left behind is the last completed step, rather than a state vector
  written into some compartments and not others.
  Each compartment captures its own state (`capture_state()` /
  `restore_state()`). So a dynamic field added without a matching capture is
  an omission local to that compartment. `docs/MODEL.md`, "Step atomicity",
  is the contract.

Both timer slots pass the halt gate, as every other slot does (`halt_gate`, in
`app/halt_gate.py`, `PL-HJKN`). The gate turns any exception raised inside a
slot into a halt. `RunView.step_tick` steps the run and
`SimulationView.render_tick` presents it. On any exception, the first halts its
run and the second halts every run. They do so because a `TypeError` from a
refactor is exactly as silent inside a Qt slot as a modelling failure is.

`dashboard_frame.halt_disposition` decides which halt applies, and
`RunView.halt` routes by its decision. A failure goes through
`SimulationController.fail()`. When a `SimulationDomainLimitError` is raised on
a path that the controller does not step itself, such as a setting, it goes
through `halt_at_supported_limit()`. A run that steps onto the supported run
length meets no exception. `SimulationController.advance()` halts it on the
step that arrives there, and the snapshot reads the limit from the run's own
state (`PL-5291`). No branch or Reset lands on the limit, because
`_resume_point` rejects a fork there, as § "What a branch is, and what it
shares with its parent" says (`PL-VHQX`).

`fail()` sets a third run state. The snapshot carries it as `failure_reason`,
and the dashboard renders it as "Stopped — simulation error" with a banner over
the values. A halted run must never look like a pause, because a pause is a run
that continues when asked and a halt is a run that cannot continue. `RunStatus`
carries both halts, and the snapshot extends `RunStatus`.
`RunView.present_halt` states a halt from the `RunRecord` that
`SimulationController.record()` returns, and `RunRecord` also extends
`RunStatus`. `present_halt` does this without building any compartment value,
because the snapshot's own `Fraction`s are among the values that can cause a
halt. The banner it writes (`dashboard_frame.halt_notice`) says that no frame of
the stopped run has been drawn. `refresh` replaces that banner on the first
frame that draws (`PL-7DJK`).

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
an exception that the toolkit prints, because every slot of `RunView` and
`SimulationView` passes the halt gate. A `RunView` slot halts its own run
through `_halt_run`, and a `SimulationView` slot halts every run, because it
acts on the case. `_halt_run` restates the halt from `record()`. So on a run
whose snapshot refused, the agent selector goes back to the agent that the
record names. The snapshot cannot name it, because the snapshot is what
refused (`PL-V2HC`). When each slot was given its own `try` by hand, six slots
were left without one, each found by a separate review (`PL-HJKN`). So
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
no single run (`SimulationController.record_failed_frame`, `PL-T2Q2`,
`PL-HJKN`).

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

- **Where.** The file is saved in the directory that Qt reports for `QStandardPaths.AppDataLocation`. On macOS the directory is
  `~/Library/Application Support/<App>`. On Windows it is
  `%APPDATA%\<Org>\<App>`, in the Roaming folder, because the file holds no
  window geometry and its sizes are fractions. On Linux it is
  `~/.local/share/<App>`. In these paths, `<Org>` is the organization name
  and `<App>` the application's display name, both defined in `app_metadata`
  (`APP_ORGANIZATION_NAME` and `APP_DISPLAY_NAME`). If a platform reports no
  directory, the session saves nothing and tells the reader so.

  The store is given its directory and does not work one out itself. Qt reports
  the directory once the organization and application names are set, so the
  entry point (`app/main.py`) sets them before it asks (`PL-DWHG`). For a
  headless or portable run, the environment variable `ANESTHESIA_SIM_USER_DIR`
  overrides the directory. It is the only override, and it is applied in
  `store.user_data_directory`.
- **When.** As with Blender's startup file, the store writes only when the
  reader chooses "Save as default" in the Layout menu or a tab's menu, never
  when something changes (`WorkspaceStore.save`). A first run leaves no trace.
  "Save as default" first asks a question that names the file it will write.
  The two entries next to it write nothing: "Restore shipped Workspaces" and
  "Reset all layouts" (`PL-DWHG`). These three entries come last in both menus.

  The save writes a temporary file beside the target and `fsync`s it. It then
  copies the current file to `workspaces.json.previous`, so that one prior
  generation survives. Finally it `os.replace`s the target, and makes a best
  effort to `fsync` the directory. As a result, only a crash in the middle of
  the replace can leave the current file torn. Both stores take the temporary
  file's write and `fsync`, and the directory's `fsync`, from the module that
  writes a user's file (`user_files.py`). Each store calls `os.replace` itself,
  and only the Workspaces store makes the copy. A failed save raises
  `WorkspaceFileError`, which names the path and the reason. The error is shown
  where the action was invoked, on the line under the Workspace tabs that shows
  what the store reported (`app/workspace_tabs.py`).
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
  - *none*: the launch shows the shipped set and says nothing, unless
    `workspaces.json.previous` exists (`_without_current_file`). If that file
    validates, the launch shows its set and says so. If it cannot be used, the
    launch shows the shipped set and says why. If a newer build wrote it, the
    launch also turns saving off for the session and says so.
  - *older*: the launch migrates the file in memory with
    `layout/migrations.py`, one step per version. The reader is told only
    where a step lost information. At the next save, the file as it was
    before migration is kept once as `workspaces.v<N>.json`.
  - *newer*: the launch refuses the file (`UnsupportedSchemaVersion`) and
    leaves it untouched. It shows the shipped set and turns saving off for the
    session. A notice names the file and both versions.
  - *unreadable*: the launch handles a file it cannot read (`OSError`) as it
    handles a newer one (`WorkspaceStore._load`). It sets aside a file that is
    not UTF-8 text (`UnicodeDecodeError`), as it does an invalid one.
  - *invalid at a version this build reads*: the launch sets the file aside
    unchanged as `workspaces.invalid-<UTC time>.json` (`_set_aside`). It loads
    `workspaces.json.previous` if that file validates, and the shipped set
    otherwise. A notice says which one it loaded, and saving stays on.

  A saved View of a kind that this build has not registered is not a file
  error. The file loads, and `app/area_layout.py` draws a notice in the Area
  that holds the View (`PL-R1WQ`).

  The parameter loader (`core/parameters.py`) accepts a file at one schema
  version only. That rule is right for files that ship with the code but wrong
  for a file that the reader wrote, so the store does not use it.

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
  layouts file (`PL-B396`). The store's load method (`PreferencesStore.load`)
  returns the preferences to use, whether saving is on, and any notice, in one
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
  (`PL-1P15`), as Blender saves its preferences on change. Nothing is
  written until the reader does one of these.
- **How a save works.** A save takes the same atomic write as the saved
  Workspaces, through `user_files.py`. No previous version is kept,
  because the file is small and the reader can set a price
  again. When a save fails, the change lasts only for the session, and the agent
  cost View says so.

## Dependencies

**`pyproject.toml` declares four runtime dependencies:** `PySide6-Essentials`,
`pyqtgraph`, `numpy` and `pydantic`. pyqtgraph already depends on numpy, but
the project declares numpy too, as it does every package that it imports. `flet`
and `flet-charts` are former dependencies (`PL-3SQT`). The import check, not
the list of declared dependencies, is what keeps them out of `src/`
(§ "Layering").

**In `src/`, numpy is used only for the chart's arrays.** The Qt chart module
(`app/qt_chart.py`) hands pyqtgraph every curve's points as `numpy.ndarray`s,
the form that pyqtgraph's performance guidance asks for (`PL-TCNT`). The import
check keeps numpy out of `core/` (§ "Layering"), so the model's propagator
stays in pure Python, as `docs/MODEL.md` § "The reproducibility guarantee"
describes. The chart-frame module (`app/chart_frame.py`) does not import numpy
either, because a frame holds plain values and only the toolkit layer converts
them to arrays. The tests also use numpy: one decomposes the model's
open-circuit system with `numpy.linalg.eig`
(`tests/reference/test_late_washout_against_published_fits.py`, `PL-921Y`).

**On Linux, the Qt wheels need shared objects from five OS packages.** Running
`ldd` on 2026-09-16 showed that the wheels' `Qt/lib/libQt6Gui.so.6` and
`Qt/plugins/platforms/libqoffscreen.so` link to the shared objects below, which
resolve outside the wheels that `pyproject.toml` installs.

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
because its own comment records that the `ubuntu-latest` image has the other
four (`PL-VHLZ`). A minimal container is neither an ordinary desktop nor that
image, so check it for all five packages. macOS and Windows need nothing extra.

**A bundled build will bring licence obligations, and nothing is violated today
(`PL-3SQT`).** `pyside6_essentials` 6.11.2 and `shiboken6` 6.11.2 both declare
`LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`. Neither wheel ships the licence
text: when checked on 2026-09-16, their `dist-info` metadata held no `licenses`
directory and no `License-File:` entry. This repository is Apache-2.0 and has no
`NOTICE` file. The LGPL obligations are dynamic linking, a recipient's ability
to relink, and conveying the licence text. They attach when a binary is
*conveyed*. This project conveys none, because building from source is the only
way to run it (`README.md` § "Running it") and `uv` installs each wheel from
PyPI for each user. A bundled build is part of the packaging work in
`ROADMAP.md`.

pyqtgraph is MIT, and numpy is `BSD-3-Clause AND 0BSD AND MIT AND Zlib AND
CC0-1.0`. Both are dependencies in `pyproject.toml`, and both wheels ship their licence
text.

## Development scripts and hooks

A separate document, [`docs/apparatus.md`](apparatus.md), maps the scripts
under `tools/`, the hooks under `.claude/hooks/` and the third-party text that
their tests read. All three exist so that agent sessions can build the
simulator, and nothing under `src/` imports them. That document is held to the
apparatus standard in `.claude/rules/apparatus-standard.md`, not to the
specialist standard in `CLAUDE.md` that applies to this document (`PL-KRGY`).

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
  (`controller.advance`), the assembly (`SimulationView.present`) and the paint
  (`QApplication.processEvents`). Running `uv run python
  tests/benchmarks/frame_cost.py` therefore shows how the time splits between
  the simulation and the interface with one command, rather than on a throwaway
  harness written for a fifth time (`PL-ZG5J`). It takes about three seconds and
  prints the timings for a person to judge. A collected test in the same
  directory checks that the harness still runs and still reports the stages it
  names (`test_frame_cost.py`). That test asserts nothing about a duration,
  because a threshold would measure the runner rather than the code.

The test suite renders on a runner with no display, because the test
configuration in `tests/conftest.py` selects Qt's `offscreen` platform plugin
before any `PySide6` import. On Linux that plugin needs the OS libraries that
§ "Dependencies" lists.

## Where new code belongs

- A new physiological compartment or coupling → `core/`. Document its
  equations and reference cases in `docs/MODEL.md` first, as `CLAUDE.md`
  requires.
- A new agent, patient or machine profile → a new validated, cited file under
  the matching subdirectory of `data/`, and any parsing support the file needs
  in `core/parameters.py`. Do not hardcode its values in `core/`.
  A compartment takes such a value as a required argument, with no default
  that restates it. `BreathingCircuit` takes its volume this way (`PL-M85T`).
- A number the code needs → one home, and every use reads the number through
  its name. A scientific value lives in a cited data file under `data/`. A
  factor between units lives in `core/units.py`. Any other number is a
  module-level constant in the module that owns the quantity. Other modules
  import that constant and never declare it a second time. The literal check
  (`tools/literal_home_check.py`) rejects the two forms that a copy takes. The
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
  saves. A View never shows a value from the unconditional set, the values
  that `docs/MODEL.md` § "Minimum displayed outputs" requires on screen at all
  times.
- A new display panel or control → three places. What the panel *claims* goes
  in `app/dashboard_frame.py`, as a plain value with a test in
  `tests/unit/test_dashboard_frame.py`. The widget that draws it goes in
  `app/qt_widgets.py`, and that widget decides nothing. The code that places
  it goes in `app/run_view.py` or `app/simulation_view.py`.

  To choose between those two, first ask *whose* panel it is. A panel that
  states a particular run's numbers belongs to `RunView`. Such panels include
  readouts, settings, transport, and the record of what was changed during the
  run. `RunView` is instantiated once per run, and the dashboard places the
  panel by looping over its runs. A panel about the chart that both runs are
  drawn on belongs to `SimulationView` or to the chart View that draws it. Such
  panels include an axis, a legend, a reference, and the compartment
  selection. A chart's time window belongs to that chart View alone
  (`PL-L59K`). A control that asks one question of the whole case, rather than
  of either run, also belongs to `SimulationView`. The bookmark editor is the
  worked example (`PL-LPLD`). It writes each mark to every displayed run, so
  that the copies the controllers hold stay equal. The branch control is the
  second example (`PL-VKJW`). The instants it offers are the trunk's
  keyframes. A copy of it in each run would give a branch a control that could
  only refuse. Getting this the wrong way round is not a matter of tidiness. A
  run's panel put on the dashboard would state one branch's numbers over both
  runs. A shared control duplicated into each run would let a reader interpret
  a comparison under two different settings.

  In either place, read only what `SimulationSnapshot` already carries and
  what a `DrawnWindow` already returns. A window holds its states per
  substance. A trace addresses one value in those states as a
  `RecordedSeries`, not as a named field. A `RecordedSeries` is a pair of a
  substance and a `RecordedQuantity`. If the UI needs a value that does not
  exist yet, add it in `app/controller.py`, and compute it in `core/`, never
  in the view. A panel that needs the run, rather than the instant, asks
  `SimulationController.drawn_window(start_s, stop_s, columns)` for the span
  it draws. It never asks for the whole run. § "Data flow" says why.

  **For anything an Area holds, the View contract replaces the routing question
  of *whose* panel it is.** That question belongs to the fixed layout, where it
  routes a surface by which of two containers holds it. An Area holds one View,
  and any View can occupy any Area, so inside an Area the question has no
  answer. For a View, follow the new-View entry above (`PL-TH35`). This entry
  still decides **where the code goes** for what stays outside the Areas: the
  unconditional region and the case section below the Areas. The setting
  controls were a third such surface until `PL-2KXB` made them a View. Inside an
  Area, this entry's *reason* still applies, though its routing does not. A
  run's panel must not state one branch's numbers over both runs. A control
  shared between runs must not be duplicated into each run. Both are properties
  of the value rather than of the container, so they apply to a View exactly as
  they apply to a panel today. The project's rule file for interface areas
  (`.claude/rules/ui-areas.md`) decides **what shape a View is in**, and it
  loads with any file under `app/`, `layout/` or `data/workspaces/`. A View is
  a widget that is given what it draws. It does not assume its size, its
  neighbours, or that it is alone.

  Breaking a surface out into a second top-level window is wanted but not
  scheduled. `ROADMAP.md` § "Explicitly out of scope for v0.6.0" says where it
  stands. Once it is built, the routing question gains a second half: *which
  window* a surface is instantiated in. Until then, `app/area_layout.py` builds
  every Area in the main window. `docs/MODEL.md` § "Minimum displayed
  outputs" answers the *which window* half, not this entry.
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
  series *claims* goes in `app/chart_frame.py`. How pyqtgraph paints it goes in
  `app/qt_chart.py`. A new *compartment* trace is declared in
  `chart_frame.COMPARTMENT_TRACES`. Its entry there gives four things as one
  record: the quantity the trace draws, how it is drawn, the legend words that
  name it, and the gloss its hover text carries. The table belongs to the
  chart, not to any one run. `assemble_chart_frame` reads it once per run, for
  the substance that the run's snapshot names. The run is recorded under that
  substance's identifier. `ChartFrame.visible` is the dashboard's
  `CompartmentSelection`. The legend shows that selection and asks to change
  it, but does not hold it (`PL-VN6M`). Once more than one run is on the chart,
  `ChartFrame.visible` is that selection narrowed by `compared_compartments` to
  `COMPARED_COMPARTMENT_CAP`. So `app/qt_chart.py` keeps one curve per run per
  trace and moves each curve to match. Nothing is edited directly. The *width*
  of a curve comes from `chart_frame.run_trace_style`, not from the table.
  While two runs are drawn, that width is the run's own channel. The table
  records what a compartment looks like, so a new trace declares no width for a
  run.

  A series that draws no state of the run stays out of that table by
  construction. Examples are a clinical reference and a control mark. A
  reference is placed by `app/chart_frame.py` and drawn by `app/qt_chart.py`,
  and it reads no state of the run. A control mark is a third kind of series,
  for a stronger version of the same reason: it draws no value at all, only a
  simulated time.
  A series outside the table must meet a labelling requirement instead.
  `docs/MODEL.md` § "Interface boundary" sets that requirement in place of the
  drawn-point rule. A trace of a *derived* quantity with a domain, such as the
  wash-in ratio, also stays out of the table. The table binds a line to one
  `RecordedSeries`, and a value that is sometimes absent has no such series to
  bind to. Such a trace must state its domain instead, in `docs/MODEL.md` and
  at the point of display.
