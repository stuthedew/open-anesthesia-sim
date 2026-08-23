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
│   ├── validation.py              # shared input-validation helpers
│   ├── exceptions.py              # exception hierarchy
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
│   ├── theme.py                    # colors and layout constants
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
`ReferenceAdultParameters`. Nothing downstream re-reads or re-derives these
values from disk.

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
setters, and produces an immutable `SimulationSnapshot` on request. The
snapshot carries the complete `SimulationHistorySample` record of the run:
one sample per simulation step, not trimmed (see `docs/PUNCH_LIST.md`).
`app/simulation_view.py` reads only from that snapshot — it formats
fractions as percentages, builds the chart, and wires slider/button
callbacks straight to controller setters. It performs no physiological or
unit calculation of its own.

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
is missing required fields, uses an unsupported schema version, or contains
a value outside its validated range (e.g. non-positive volumes, tissue
perfusion fractions that don't sum to 1). Adding a new agent or patient
profile means adding a new validated, cited JSON file plus any new parsing
support in `parameters.py` — not adding constants directly to `core/`.

## Tests (`tests/`)

- **`tests/unit/`** — one module's behavior in isolation (a compartment, a
  validator, a parameter loader, the controller, the view's formatting).
- **`tests/integration/`** — components wired together as the app assembles
  them (e.g. controller driving a full `RespiratorySystem`).
- **`tests/reference/`** — analytic/independent reference cases the
  implementation must reproduce (e.g. the closed-form circuit wash-in
  solution, the sevoflurane patient reference scenario). These are the
  regression tests referenced throughout `docs/MODEL.md`'s release gate.

## Where new code belongs

- A new physiological compartment or coupling → `core/`, with its equations
  and reference cases documented in `docs/MODEL.md` first (per `CLAUDE.md`).
- A new agent or patient profile → a new validated, cited file under
  `data/`, not hardcoded values in `core/`.
- A new display panel, control, or chart series → `app/simulation_view.py`,
  reading only fields already on `SimulationSnapshot`/`SimulationHistorySample`;
  if the UI needs a value that doesn't exist yet, add it to those dataclasses
  in `app/controller.py`, computed in `core/`, never computed in the view.
