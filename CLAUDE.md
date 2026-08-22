# Open Anesthesia Simulator — Project Context

Read this file before proposing or making changes.

## Project purpose

Open Anesthesia Simulator is an open-source, deterministic educational simulation of anesthesia-machine and anesthetic-agent behavior.

The long-term goal is a scientifically transparent, extensible simulator with explicit equations, units, assumptions, provenance, numerical validation, and a polished interface.

This is an educational model—not a clinical prediction, monitoring, decision-support, or dosing tool.

## Repository and current branch

Repository:

```text
~/Developer/open-anesthesia-sim
```

Current development branch:

```text
build/v0.1.0-sevo-patient
```

The working tree contains substantial intentional, uncommitted v0.1.0 work. Do not reset, discard, overwrite, switch branches, clean untracked files, or otherwise destroy changes unless the user explicitly requests it.

Generated files such as `__pycache__`, `.coverage`, and `.DS_Store` are present. Treat repository cleanup as a separate task and do not delete files without reviewing the exact targets.

## Authoritative versioning decision

`ROADMAP.md` is the authoritative milestone map.

| Version | Meaning |
| --- | --- |
| v0.0.1 | Initial runnable prototype |
| v0.0.2 | Analytically validated ideal breathing-circuit wash-in/washout |
| v0.1.0 | First patient sevoflurane uptake/distribution model—the “Sevo works” milestone |

There is no active v0.0.3 milestone. Older material describing this patient milestone as v0.0.3 is superseded.

The package version has already been changed to `0.1.0`, but v0.1.0 has not been released or tagged.

## Sources of truth

When answering project questions, reconcile these sources:

1. The user’s current request
2. `ROADMAP.md` for milestone identity and scope
3. `docs/MODEL.md` for scientific equations, units, assumptions, and limitations
4. The current working tree and tests for actual implementation state
5. Prior build guides and conversation artifacts

If sources disagree, explicitly identify the discrepancy. Do not silently choose one.

The `ROADMAP.md` baseline description refers to released `main` at v0.0.2. The current feature branch contains the in-progress v0.1.0 implementation.

## Current scientific architecture

The implemented pathway is:

```text
Delivered sevoflurane
    → breathing circuit
    → alveolar gas
    → venous blood and perfusion-limited tissues
    → vessel-rich group / muscle / fat
    → mixed-venous return
```

Important files:

```text
src/anesthesia_sim/core/circuit.py
    Exact ideal breathing-circuit fresh-gas update.
    Preserve v0.0.2 analytic behavior.

src/anesthesia_sim/core/alveolar.py
    Explicit alveolar gas volume and ventilation behavior.

src/anesthesia_sim/core/blood.py
    Mixed-venous blood compartment.

src/anesthesia_sim/core/tissue.py
    One perfusion-limited tissue group.

src/anesthesia_sim/core/patient.py
    Vessel-rich, muscle, fat, cardiac output, and mixed-venous return.

src/anesthesia_sim/core/respiratory_system.py
    Owns the conservative circuit/alveolar/patient coupling order.

src/anesthesia_sim/core/agent_simulation_validation.py
    Tracks delivered, exhausted, stored, and unaccounted agent.

src/anesthesia_sim/core/simulation.py
    Owns the complete respiratory system and explicit elapsed simulation time.

src/anesthesia_sim/core/parameters.py
    Loads and validates agent and patient data.

src/anesthesia_sim/core/exceptions.py
    Project-specific exception hierarchy.

src/anesthesia_sim/data/agents/sevoflurane.json
    Sevoflurane parameters and provenance.

src/anesthesia_sim/data/patients/reference_adult.json
    Reference adult parameters and provenance.

src/anesthesia_sim/app/controller.py
    Run state, immutable snapshots, named history samples, and live settings.

src/anesthesia_sim/app/simulation_view.py
    Responsive Flet dashboard. It must not perform physiological calculations.

src/anesthesia_sim/app/main.py
    Flet application construction and console launcher.
```

Keep Flet, display dimensions, wall-clock timing, and UI formatting out of the scientific core.

## Intentional nomenclature

Do not perform broad naming changes without explicit user approval.

The following distinction is intentional:

- The module is `agent_simulation_validation.py`.
- The broader types are `AgentSimulationValidator`, `AgentSimulationValidationResult`, and `AgentSimulationValidationError`.
- Within that broader validation system, `agent_accounting`, `check_agent_accounting()`, and `require_valid_agent_accounting()` are appropriate names for the specific conservation calculation.

The user deliberately reverted an earlier attempt to eliminate all “accounting” terminology.

Use the current repository names as authoritative. Do not rename APIs merely to make naming internally uniform.

## Validation and exceptions

Agent accounting verifies:

```text
initial stored agent + delivered agent
=
exhausted agent + currently stored agent
```

The validator reports:

- delivered agent
- exhausted agent
- currently stored agent
- unaccounted agent
- absolute error
- relative error
- whether validation passes

Use project-specific exceptions by default for project-level failures:

```text
AnesthesiaSimulationError
├── SimulationConfigurationError
└── SimulationExecutionError
    └── SimulationNumericalError
        └── AgentSimulationValidationError
```

Do not replace a meaningful project exception with a generic exception without a concrete reason.

## Current application entry point

The console entry point is:

```toml
[project.scripts]
anesthesia-sim = "anesthesia_sim.app.main:main"
```

`src/anesthesia_sim/app/main.py` contains:

- asynchronous `build_app(page)`
- no-argument `main()`
- `main()` calls `ft.run(build_app)`

This fixed an earlier failure where the console script incorrectly attempted to import `main` from `anesthesia_sim/__init__.py`.

## Current interface state

The application runs.

The current `simulation_view.py` is a compact, self-contained dashboard with:

- title, version, run controls, and status in a compact header
- fresh gas flow control
- delivered sevoflurane control
- alveolar ventilation control
- cardiac output control
- circuit/inspired concentration
- alveolar/end-tidal concentration
- mixed-venous concentration
- vessel-rich, muscle, and fat values
- six named chart traces with color and line-pattern distinctions
- agent-accounting status and amounts
- educational/non-clinical warning
- fixed 360-pixel chart height
- 60-second initial chart window
- rolling maximum 300-second display window
- responsive stacking on smaller windows

The UI has received an interim polish pass, not a final visual-design pass.

Do not move simulation math into the view.

## Current test status

As of 2026-08-22:

```text
92 tests passed
Ruff formatting passed
Ruff lint passed
Strict mypy passed
```

The complete quality command is:

```bash
make check
```

Core scientific modules generally have approximately 94–100% coverage.

Overall coverage was approximately 73% because `simulation_view.py` and most Flet application assembly currently have no automated coverage. A green test suite does not prove that the new UI is wired correctly.

The circuit-only tests are not automatically outdated. They intentionally preserve v0.0.2 analytic behavior and are required regression tests.

Known testing gap:

- Flet slider handlers
- Start/Pause/Reset view wiring
- chart-series wiring
- agent-accounting display
- responsive view construction

Manual UI smoke testing remains required until focused view tests are added.

## Makefile workflow

Use the project’s established Make commands.

Synchronize dependencies:

```bash
make sync
```

Run pytest:

```bash
make test
```

Format and apply safe Ruff fixes:

```bash
make fix
```

Run dependency sync, formatting check, lint, strict mypy, and all tests:

```bash
make check
```

Show Git status and run the complete gate:

```bash
make prebuild
```

Launch the application:

```bash
make run
```

Coverage diagnostic:

```bash
uv run pytest \
  --cov=anesthesia_sim \
  --cov-report=term-missing
```

## User collaboration preferences

These are strict defaults.

### Do not implement by default

Unless the user explicitly asks to implement changes, provide code for the user to copy and paste.

Read-only inspection and diagnostic test runs are acceptable when relevant.

### Whole-file replacements are the default

If a file needs changes in multiple locations, provide the complete file in one code block.

Do not make the user hunt through a file for several separate replacements.

An isolated one-line change may be provided as a partial edit.

Every code block must clearly identify its destination file.

### Step-by-step workflow

The user prefers one clearly bounded step at a time and will say:

```text
next
```

when ready to continue.

Every step response should have:

- a large, clear header at the top
- exact destination filenames
- complete copy/paste code
- generous visual separation between different files
- terminal commands to verify the step
- expected results

### Communication

Use plain language and intuitive explanations.

The user often asks what a scientific or architectural component does before deciding on naming. Explain the responsibility and domain meaning, not merely the Python mechanics.

Do not silently change naming conventions, APIs, equations, units, scope, or architecture.

Inspect the current repository before giving code that depends on repository state.

## Code-quality standard

Approach the project as an expert Python software architect specializing in scientific simulations and open-source tools, with professional, industry-leading UX, UI and graphic-design judgment.

The expected code should be:

- elegant
- intuitive
- deterministic
- explicit about units and ownership
- scientifically defensible
- conservative in scope
- easy for another developer to skim
- minimally surprising
- thoroughly validated
- polished without unnecessary abstraction

Do not introduce architecture merely to appear sophisticated.

## Documentation standard

High-quality professional documentation is the default for new code and for any complete existing file that must be replaced during a future step.

Follow these rules strictly:

1. Do not alter, optimize, or change execution logic, mathematics, formulas, or established variable names merely while adding documentation.
2. Every complete module should begin with a triple-quoted module docstring explaining its responsibility and domain context—why it exists, not merely what it contains.
3. Add Google-style docstrings to all classes and major methods.
4. State physical units explicitly for arguments, attributes, state, and return values where applicable.
5. Every function signature must have explicit type hints.
6. Use `typing.NewType` when unit safety materially improves the API without unnecessarily disrupting established interfaces.
7. Use inline comments only for non-obvious domain physics, scientific formulas, numerical methods, or safety guardrails.
8. Do not add comments that merely narrate obvious Python operations.
9. Do not begin a separate retroactive documentation rewrite unless requested.
10. If a file must already be replaced for a functional change, return the complete file with documentation upgraded throughout while preserving unrelated logic exactly.

## Scientific-development rules

- Preserve deterministic results for identical inputs and time steps.
- Use explicit physical units in names and documentation.
- Keep one canonical equivalent-agent amount basis for accounting.
- Do not sum unlike concentration or amount representations.
- Use conservative transfers: an amount removed from one compartment must be the amount added to another.
- Do not hide lost mass with post-hoc clipping.
- Maintain safe behavior at zero fresh gas flow, zero ventilation, and zero cardiac output.
- Keep parameters separate from mutable state.
- Keep built-in profiles read-only.
- Require schema version and provenance for scientific data.
- Preserve the existing circuit analytic regression behavior.
- Define equations, units, assumptions, and numerical ownership before adding new scientific scope.
- Do not add deferred features to v0.1.0.

## Explicit v0.1.0 exclusions

Do not add these during v0.1.0 cleanup:

- additional volatile anesthetics
- nitrous oxide
- simultaneous gases
- vaporizer interlocks or agent switching
- V/Q mismatch, dead space, shunt, or multiple alveolar units
- metabolism
- MAC, BIS, hypnosis, or nociception models
- IV anesthetics
- ECMO or cardiopulmonary bypass
- scenario save/load, replay, comparison, or forking
- clinical prediction or dosing guidance

## Build-guide and PDF preferences

Future build guides and PDFs should:

- use the authoritative milestone version from `ROADMAP.md`
- include exact filenames for every code block
- provide complete files when multiple parts of a file change
- be command-heavy and copy/paste-friendly
- retain the Makefile workflow
- include concrete terminal commands where useful
- use large step headers and whitespace between code blocks
- include or accompany the relevant `docs/MODEL.md` text
- render equations using clean Markdown equation formatting when supported
- never leave placeholders such as “Agent data shape” without saying which file to edit
- never depend on conversational memory for versioning or architecture

Older v0.0.3 patient-build guides are superseded.

## Current next steps

The v0.1.0 feature branch is functionally advanced but not release-ready.

Recommended continuation:

1. Launch the compact interface with `make run`.
2. Repeat the manual smoke sequence:
   - Start and confirm the circuit rises first.
   - Confirm alveolar concentration follows.
   - Confirm vessel-rich tissue rises before muscle and fat.
   - Change ventilation without resetting state.
   - Change cardiac output without resetting state.
   - Set delivered sevoflurane to zero and observe washout.
   - Pause and confirm state freezes.
   - Reset and confirm dynamic state clears while settings persist.
   - Confirm agent-accounting status remains valid.
3. Add focused tests for important UI/controller wiring where practical.
4. Run the complete scientific and release test matrix.
5. Review `docs/MODEL.md` against the actual implementation.
6. Update `README.md` to describe the v0.1.0 capability and limitations.
7. Review parameter provenance, equations, units, numerical tolerances, and limitations.
8. Inspect the complete diff before staging anything.
9. Clean generated artifacts deliberately and safely.
10. Do not mark `ROADMAP.md` complete or create the v0.1.0 tag until the merged release gate passes.

## Git safety

The branch has a dirty working tree with many intentional new files.

Before any Git operation:

```bash
git status --short
```

Do not run destructive commands such as:

```text
git reset --hard
git checkout --
git clean -fd
```

Do not stage generated caches or `.DS_Store` files.

Do not commit, push, merge, or tag unless the user explicitly requests that action.

## First response in a new session

Before proposing work:

1. Read this file.
2. Read `ROADMAP.md`.
3. Inspect `git status --short`.
4. Inspect the relevant current files.
5. Run or review `make check` when appropriate.
6. State the exact current step and whether the response will provide snippets or perform implementation.