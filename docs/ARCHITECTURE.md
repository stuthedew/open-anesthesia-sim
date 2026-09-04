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
│   ├── supported_ranges.py        # the declared input domain; refuses a setting outside it
│   ├── exceptions.py              # exception hierarchy; every core failure is inside it
│   ├── parameters.py              # load + validate agent/patient JSON data
│   ├── circuit.py                 # breathing circuit compartment
│   ├── alveolar.py                # alveolar gas compartment
│   ├── blood.py                   # venous blood compartment
│   ├── tissue.py                  # one perfusion-limited tissue group
│   ├── patient.py                 # PatientCompartments: VRG + muscle + fat + venous blood
│   ├── uptake_system.py      # couples circuit + alveoli + patient; advances one step
│   ├── agent_simulation_validation.py  # mass-balance / agent-accounting tracker
│   └── simulation.py              # SimulationState: explicit elapsed time + AgentUptakeSystem
├── app/                  # Flet user interface
│   ├── controller.py               # SimulationController: run controls, read-only snapshots
│   ├── simulation_view.py          # renders snapshots as the dashboard; no domain logic
│   ├── formatting.py               # modeled value -> displayed string; Flet-independent
│   ├── chart_series.py             # builds and redraws the chart's traces, references and control marks
│   ├── chart_downsampling.py       # chooses which samples a trace draws; Flet-independent
│   ├── control_timeline.py         # recorded control changes -> the acts a reader sees; Flet-independent
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
`ReferenceAdultParameters`. The schemas are strict at every nesting level:
a key the schema does not declare fails the load rather than being silently
discarded, so a data file cannot document one model while the app runs
another. Nothing downstream re-reads or re-derives these values from disk.

**Each simulation step**, `AgentUptakeSystem.advance()` runs a fixed sequence
of exact analytic solutions (operator splitting — see `docs/MODEL.md` for the
equations) rather than a generic numerical integrator:

1. circuit ⇄ fresh gas exchange (`BreathingCircuit.advance_fresh_gas`);
2. circuit ⇄ alveolar gas exchange (`AgentUptakeSystem._exchange_circuit_and_alveoli`);
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
from what `AgentUptakeSystem.for_agent()` built from the data files, and a
setting the core rejects — a delivered concentration above the agent's
vaporizer maximum, say — raises out of the core rather than being clamped or
defaulted at this boundary. Conservation is core's on the same terms: until
PL-006 the controller read the circuit's stored agent out and put it back
around `set_circuit_volume`, which left `core/` exposing an unconserving
primitive publicly and the invariant holding only for the caller that knew
to compensate. The setter conserves, and the controller forwards. The
snapshot carries the complete `SimulationHistorySample` record of the run:
one sample per simulation step, not trimmed (see `docs/items/`). It carries
the run's `ControlChange` timeline beside it — one entry per setting the
model was actually stepped under, so re-applying the timeline reproduces
the run rather than approximating it.
`app/simulation_view.py` reads only from that snapshot — it builds the
controls, drives the chart, and wires slider/button callbacks through
`_apply_setting` to controller setters. It performs no physiological or
unit calculation of its own. The transformations it does apply are each
their own module, because each is a presentation-*correctness* question
rather than a layout one and each must be readable and testable without a
Flet interface: `app/formatting.py` turns a fraction into the strings a
reader sees — a percent and a multiple of the running agent's 1 MAC — at the
resolutions `docs/MODEL.md` § "Displayed precision" derives,
`app/chart_series.py` builds the traces and redraws them from the recorded
run, and `app/control_timeline.py` turns the recorded control changes into
the adjustments a reader sees. That last one is a correctness question for a
reason worth stating: the record is faithful to the run and a drag of one
slider is several settings in it, so the collapse into one displayed act is
a claim about what the user did rather than a tidier rendering of what the
model saw. The MAC divisor reaches the formatter as an argument, from
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
  before the step and restores it on any failure, so what is left behind
  is the last completed step rather than four of the five sub-exchanges.
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
with run length, so the view draws a bounded subset instead: which samples a
trace draws is decided by `app/chart_downsampling.py`, a Flet-independent
module kept separate because choosing a subset is a
presentation-correctness concern (a subset that drops a transient shows a
curve the simulation never produced) and therefore needs to be tested on its
own. `app/chart_series.py` is the layer above it — it holds the per-trace
point budget, converts fraction to percent, and moves the points a trace
already holds — and it is separate for the same reason: which quantity a
line carries is a correctness claim, and the view passes it in as one
`PlottedSeries` table declared beside the traces themselves. Stepping and drawing also run as separate loops on separate intervals,
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
├── branch_id_check.py    # refuses a branch ahead of the default base that carries no item id in its name and leads no commit subject with one, because every in-flight guard matches an id and work carrying none is invisible to all of them
├── contrast_check.py     # computes every declared color pair's WCAG 2.2 contrast ratio from the constants in `app/`, and holds each to its declared minimum
├── doc_check.py          # validates this map, MODEL.md's provenance table and its marked prose values, doc citations, markdown math syntax, ROADMAP.md's release train, frozen-list counts and current baseline; reports resident instruction size
├── import_boundary_check.py  # fails the build on a `pydantic` import anywhere under `src/anesthesia_sim/` other than `core/parameters.py`, so the payload/dataclass boundary is measured rather than asserted
├── ignore_check.py       # evaluates warn_unused_ignores over the two test trees `[tool.mypy] files` excludes, so an inert `type: ignore` fails the build
├── pr_title_check.py     # refuses a pull request whose title does not lead with the ids its branch closes, because the squash-merge subject is taken from that title and is what `docket check` reads to recover which pull request closed an item
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

`tools/pr_title_check.py` runs only on pull requests, and is the prevention
half of `PL-2XTF`. A squash merge takes its subject from the pull request
title, so a title naming none of the items it closes lands a subject that
`docket check` cannot trace a closure back to. That happened once: a
UI-generated title closed three items, `main` went red with errors no recovery
could clear, and the numbers had to be read off GitHub by hand. The recovery
half now falls back to each item's own file history, and this half stops the
bad subject reaching `main` while the title can still be edited. Both are
wanted — recovery alone leaves the wrong subject on `main` for good, and the
check alone leaks when a merger retypes the subject in the squash dialog.

`tools/branch_id_check.py` is the same shape of guard aimed at the other end of
the same problem, and the two do not overlap: the title check asks whether a
pull request names the items it *closes*, and answers "no id is owed" for a
branch that closes none — which is exactly the unfiled repository housekeeping
`PL-CP74` found colliding. `docket flight`, `show`, `next`, `concurrent` and
the session-start digest all answer "is anybody already on this?" by matching a
`PL-` id in a branch name or at the front of a commit subject, so a branch
carrying none reads as nobody's work to every one of them, and goes on doing so
after both sessions have pushed.

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
`docs/MODEL.md` states — WCAG 2.2 Level AA. It reads the color constants out of
`app/theme.py` and `app/simulation_view.py` with `ast` rather than importing
them, because `app/simulation_view.py` imports Flet and these tools run under a
bare `python3`. Its `REQUIREMENTS` table is the specification: each entry names
a pair that appears on screen together, the success criterion, the minimum, and
the reason. The tool evaluates that table and decides nothing else — which
pairs matter, and whether a non-color channel is genuinely redundant, are
judgments, and `.claude/rules/ui-color.md` carries them. Pairs that fall short
today are listed against the item that closes each, and a listed shortfall that
starts passing is an error, so a fix cannot leave its excuse behind.

`tools/import_boundary_check.py` measures the claim `core/parameters.py` makes
about itself. `_StrictPayload`'s docstring says that the `_...Payload`/public-
dataclass pairs exist so the rest of `core/` never imports Pydantic; nothing
checked it, so a leak into a compartment would have left that paragraph reading
as verified while being false — worse than the coupling itself. Its `BOUNDARIES`
table is the specification, and the tool decides nothing beyond it: which
packages ought to be confined, and where the exception belongs, are judgments
written there with the reason beside them. Three further states are errors, each
closing a way the check could pass while meaning nothing — an allowance naming a
file that no longer exists, an allowance no longer used, and a declared tree
matching no source files at all. The boundary covers `app/` as well as `core/`,
so the rule reads *exactly one module in this package imports Pydantic*.

`tools/ignore_check.py` covers what the type-check gate cannot. `[tool.mypy]
files` names `src`, `tools` and `subprojects/docket/src`, and every
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
number chosen here: `doc_check.py` imports `docket.roadmap`, so it is whatever
`subprojects/docket/pyproject.toml` declares in `requires-python`.

Two of them are nonetheless *invoked* under `uv run python`, and the
distinction is worth keeping straight, because it is about what a tool reads
rather than what it needs. `ignore_check.py` shells out to mypy, so it wants
the virtualenv that gate runs in. `import_boundary_check.py` parses
`src/anesthesia_sim/`, and that source targets 3.14: `app/chart_downsampling.py`
opens `def first_index_at_or_after[SampleT](`, PEP 695 syntax that is a
`SyntaxError` to the 3.11 parser, and `ast.parse`'s `feature_version` only
narrows the syntax it accepts rather than extending it. A tool that parses
repository source can only run under an interpreter that understands that
source. Both still meet the promise above, which is what the portability suite
holds them to — `contrast_check.py` reads `app/` too and runs bare, and
`PL-L17Q` is the item saying that it does so only because the two files it
happens to read carry no 3.12+ syntax yet.

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
`sys.stdlib_module_names`. `.github/workflows/quality.yml`'s `floor` job
performs the run they stand in for: `actions/setup-python` at the declared
floor, then `python3 tools/doc_check.py check`, `python3 tools/branch_id_check.py`,
`bin/docket check` and `python3 tools/contrast_check.py` under it.
That decides syntax, imports and runtime behavior at once, with no list to keep
current. A fourth test holds the job's pinned version to `requires-python`, so
raising the floor cannot leave CI exercising an interpreter the project no
longer supports. The approximations stay because they name the offending file
and import, run before a push, and reach what those two commands never do.

## Tests (`tests/`)

- **`tests/unit/`** — one module's behavior in isolation (a compartment, a
  validator, a parameter loader, the controller, the displayed-value
  formatters, the view).
- **`tests/integration/`** — components wired together as the app assembles
  them (e.g. controller driving a full `AgentUptakeSystem`).
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
- A new display panel or control → `app/simulation_view.py`, reading only
  fields already on `SimulationSnapshot`/`SimulationHistorySample`; if the UI
  needs a value that doesn't exist yet, add it to those dataclasses in
  `app/controller.py`, computed in `core/`, never computed in the view.
- A new way of *rendering* a value a reader interprets — a unit, a decimal
  count, a marker for what the display cannot resolve → `app/formatting.py`,
  as a pure function with its own test, and with the reason recorded in
  `docs/MODEL.md` § "Displayed precision".
- A new chart series, or a change to how one is drawn → `app/chart_series.py`,
  with the trace paired to its quantity in `SimulationView`'s
  `_plotted_series` table. A series that draws no recorded sample — a
  clinical reference, a control mark — stays out of that table by
  construction, and owes the labelling requirement `docs/MODEL.md`
  § "Interface boundary" puts in place of the sample rule instead.
