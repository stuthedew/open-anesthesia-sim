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
  citations. `core/` never contains hardcoded scientific constants for the
  agent or patient it loads by default.

This mirrors the repository rules in `CLAUDE.md`: simulation code stays
independent of Flet, no simulation calculations belong in UI callbacks, and
model parameters live in validated, versioned data files rather than as
executable code.

## Package map

```text
src/anesthesia_sim/
├── app_metadata.py      # app name, version (from package metadata), bundle id
├── core/                # scientific simulation — no Flet dependency
│   ├── validation.py              # shared input-validation guards (raise SimulationConfigurationError)
│   ├── exceptions.py              # exception hierarchy; every core failure is inside it
│   ├── parameters.py              # load + validate agent/patient JSON data
│   ├── circuit.py                 # breathing circuit compartment
│   ├── alveolar.py                # alveolar gas compartment
│   ├── blood.py                   # venous blood compartment
│   ├── tissue.py                  # one perfusion-limited tissue group
│   ├── patient.py                 # PatientCompartments: VRG + muscle + fat + venous blood
│   ├── respiratory_system.py      # couples circuit + alveoli + patient; advances one step
│   ├── agent_simulation_validation.py  # mass-balance / agent-accounting tracker
│   └── simulation.py              # SimulationState: explicit elapsed time + RespiratorySystem
├── app/                  # Flet user interface
│   ├── controller.py               # SimulationController: run controls, read-only snapshots
│   ├── simulation_view.py          # renders snapshots as the dashboard; no domain logic
│   ├── chart_downsampling.py       # chooses which samples a trace draws; Flet-independent
│   ├── theme.py                    # UI palette, cited ISO 5360 agent colors, layout constants
│   └── main.py                     # entry point; builds the Flet page
└── data/                 # versioned, cited parameter files
    ├── agents/{sevoflurane,isoflurane,desflurane}.json
    └── patients/reference_adult.json
```

## Data flow

**Startup / parameter loading:**

```text
data/agents/sevoflurane.json  ──┐
data/patients/reference_adult.json ─┴─> core/parameters.py
                                        (parse + validate schema, units, ranges)
                                        │
                                        ▼
                          RespiratorySystem.default()
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
`ReferenceAdultParameters`. The schemas are strict at every nesting level:
a key the schema does not declare fails the load rather than being silently
discarded, so a data file cannot document one model while the app runs
another. Nothing downstream re-reads or re-derives these values from disk.

**Each simulation step**, `RespiratorySystem.advance()` runs a fixed sequence
of exact analytic solutions (operator splitting — see `docs/MODEL.md` for the
equations) rather than a generic numerical integrator:

1. circuit ⇄ fresh gas exchange (`BreathingCircuit.advance_fresh_gas`);
2. circuit ⇄ alveolar gas exchange (`RespiratorySystem._exchange_circuit_and_alveoli`);
3. patient uptake/return (`PatientCompartments.advance`), driven by the
   current alveolar fraction;
4. alveolar gas absorbs the resulting blood uptake
   (`AlveolarCompartment.apply_blood_uptake`);
5. the agent-accounting validator records delivered/exhausted amounts and
   checks mass balance (`AgentSimulationValidator`), raising
   `AgentSimulationValidationError` if it fails.

**UI direction:** `app/controller.py`'s `SimulationController` owns a
`SimulationState`, exposes `start()` / `pause()` / `reset()` / per-parameter
setters, and produces an immutable `SimulationSnapshot` on request. It holds
no default values and no bounds of its own: every unspecified setting comes
from what `RespiratorySystem.for_agent()` built from the data files, and a
setting the core rejects — a delivered concentration above the agent's
vaporizer maximum, say — raises out of the core rather than being clamped or
defaulted at this boundary. The
snapshot carries the complete `SimulationHistorySample` record of the run:
one sample per simulation step, not trimmed (see `docs/items/`).
`app/simulation_view.py` reads only from that snapshot — it formats
fractions as percentages, builds the chart, and wires slider/button
callbacks through `_apply_setting` to controller setters. It performs no
physiological or unit calculation of its own.

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
  not be completed, so compartment state may sit partway through it.
  `RespiratorySystem.advance()` is what makes this distinction: it checks
  its own arguments first, then restates any guard reached during the step
  as a `SimulationNumericalError`, keeping the original as `__cause__`.

Both view loops are guarded, and both call `SimulationController.fail()`
on any exception — a `TypeError` from a refactor kills an asyncio task
exactly as silently as a modelling failure does. `fail()` is a third run
state, carried on the snapshot as `failure_reason` and rendered as
"Stopped — simulation error" with a banner over the values: a halted run
must never present as a pause, because the numbers beside it may come from
a step that never finished. It cannot be resumed, only cleared by `reset()`
or by starting a fresh run with `set_agent()`. Neither loop returns on
failure — they are started once, at mount, so a loop that exited could
never be restarted.

Drawing that full record every frame is what made the render payload grow
with run length, so the view draws a bounded subset instead: which samples a
trace draws is decided by `app/chart_downsampling.py`, a Flet-independent
module kept separate because choosing a subset is a
presentation-correctness concern (a subset that drops a transient shows a
curve the simulation never produced) and therefore needs to be tested on its
own. Stepping and drawing also run as separate loops on separate intervals,
so simulation time stays a function of steps taken rather than of how long a
frame took.

## Data files (`data/`)

Each JSON file carries a `schema_version`, an `id`, the parameter values, and
a `sources` array of citations (`citation`, `url`, `note` per entry — see
`core.parameters.SourceReference`). `core/parameters.py` rejects a file that
is missing required fields, uses an unsupported schema version, contains a
value outside its validated range (e.g. non-positive volumes, tissue
perfusion fractions that don't sum to 1), or carries a key the schema does
not declare — including inside a nested object such as
`tissue_gas_partition_coefficients` or one `sources` entry. Adding a new agent or patient
profile means adding a new validated, cited JSON file plus any new parsing
support in `parameters.py` — not adding constants directly to `core/`.

## Developer tooling (`tools/`)

Outside the packaged application, and not imported by it:

```text
tools/
├── doc_check.py          # validates this map, MODEL.md's provenance table, doc citations, ROADMAP.md's release train and current baseline
└── review-verification/  # read-only harness reproducing the v0.2.0 architecture-review findings
```

`tools/review-verification/` is evidence, not tests: each script re-runs a
reviewed claim against the current tree and reports whether it still
reproduces. See its own `README.md` for what each check means and why it
exits `1` on a healthy tree.

`tools/doc_check.py` holds this document to the code. The package-map trees
above are checked against the tree on disk in both directions, so a module
added here without a line in the map, or a line left behind after a deletion,
fails `make check`. That is why the trees list every module individually: a
directory drawn with no children beneath it (`tools/review-verification/`)
stands for its whole subtree and is not expanded, and `__init__.py` is
excluded throughout. The same tool checks `docs/MODEL.md`'s provenance table against
the data files and resolves every path and section heading the documentation
cites.

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

The same module reads `ROADMAP.md`'s *version* table, and `doc_check` holds
the three statements of the current version to each other: one row per
released version, exactly one marked the current baseline, a "Current
baseline:" heading naming that same version, and that version matching
`pyproject.toml`. A release bumps the version file and leaves the plan naming
its predecessor, which happened on two consecutive releases. Tags are
deliberately not compared — a shallow clone is a normal checkout, and a check
that fails on how somebody fetched the repository gets switched off. `docket
release` enforces the tag instead, when tags are certainly to hand.

## Tests (`tests/`)

- **`tests/unit/`** — one module's behavior in isolation (a compartment, a
  validator, a parameter loader, the controller, the view's formatting).
- **`tests/integration/`** — components wired together as the app assembles
  them (e.g. controller driving a full `RespiratorySystem`).
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
- A new agent or patient profile → a new validated, cited file under
  `data/`, not hardcoded values in `core/`.
- A new display panel, control, or chart series → `app/simulation_view.py`,
  reading only fields already on `SimulationSnapshot`/`SimulationHistorySample`;
  if the UI needs a value that doesn't exist yet, add it to those dataclasses
  in `app/controller.py`, computed in `core/`, never computed in the view.
