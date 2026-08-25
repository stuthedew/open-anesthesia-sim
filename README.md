# Open Anesthesia Simulator

An open-source, deterministic anesthesia simulation for education. It models
volatile-agent delivery, uptake, and distribution through an explicit
breathing circuit, alveolar gas, blood, and tissue compartments.

**This is an educational tool, not a clinical prediction, dosing, or
monitoring device.** No output should be used to guide real-world patient
care.

## Current status

The simulator models volatile-agent wash-in, uptake, tissue distribution,
mixed-venous return, and washout in a single reference adult patient:

```text
delivered agent -> breathing circuit -> alveoli -> blood
                -> vessel-rich group / muscle / fat -> mixed venous return
```

Sevoflurane, isoflurane, and desflurane are each modeled from validated,
cited partition data and can be picked in the interface, which identifies the
selected agent by name and by its ISO 5360 vaporizer color. Selecting an agent
starts a new run at that agent's own 1 MAC: switching agents does **not**
model washout of the previous agent, because carrying residual agent across
a switch is a distinct, harder problem left to the anesthesia-machine
milestone. The delivered-concentration control is limited to each agent's
real vaporizer maximum.

Fresh gas flow, delivered concentration, alveolar ventilation, and cardiac
output can all be changed live during a run. Agent mass delivered,
exhausted, and stored across every compartment is tracked and checked
against a documented numerical tolerance.

A setting the model refuses is reported as refused and leaves the run
alone. A failure the model cannot continue past halts the run and says so,
rather than leaving the display reading "Running" over numbers that have
stopped advancing; a halted run is cleared by Reset.

Concentrations are displayed to 0.01 percentage points, which is the
resolution the numerical method supports rather than the resolution the
floating-point values carry: the shipped operator split disagrees with an
independent solution by up to 1.2e-2 percentage points across the settings
the interface exposes, so a finer readout would present solver noise as model
output. A positive value too small to show reads `<0.01%`, so an empty
compartment stays distinguishable from an unresolved one.

Each agent's MAC is used only to pick a clinically sensible starting dial
position. The simulator does not model anesthetic depth: there is no
effect-site compartment, and no MAC-fraction, BIS, or other depth readout is
predicted or displayed. Also not modeled: agents beyond these three, IV
anesthetics, metabolism, or any decision support. See
[`docs/MODEL.md`](docs/MODEL.md) for the full model specification, including
equations, units, parameter provenance, and known limitations, and
[`ROADMAP.md`](ROADMAP.md) for version history and planned milestones.

## Requirements

- Python 3.14 (see `.python-version`)
- [uv](https://docs.astral.sh/uv/) for dependency management and running
  commands

## Setup

```bash
uv sync --locked --dev
```

## Running the simulator

```bash
make run
# or: uv run anesthesia-sim
```

## Development

```bash
make check       # ruff format --check, ruff check, mypy (strict), pytest,
                 # then the docket and documentation checkers
make fix         # ruff format, ruff check --fix
make test        # pytest only
make docket      # validate docs/items/ and list anything untriaged
make doc-check   # validate the package map, provenance table, and doc citations
```

The last two are stdlib-only scripts in `tools/`, so they run in a bare
checkout. `tools/doc_check.py` also has a `candidates` mode that prints the
documentation lines mentioning anything a diff changed, for the sweep a
change needs before it is complete.

`make check` mirrors the checks run in CI (`.github/workflows/quality.yml`)
and must pass before a change is considered complete.

## Documentation

- [`ROADMAP.md`](ROADMAP.md) — authoritative version and milestone map.
- [`docs/items/`](docs/items) — the development queue: one file per item,
  covering defects, cleanups, optimizations, and small features. Read and
  written with `docket` (see below).
- [`subprojects/docket/`](subprojects/docket/README.md) — the queue tool
  itself, a standalone package with no dependency on this simulator.
- [`docs/WORKING_NOTES.md`](docs/WORKING_NOTES.md) — cross-session log of
  open threads, diagnoses, and the rationale behind decisions.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — how `core/`, `app/`, and
  `data/` fit together, and where new code belongs.
- [`docs/MODEL.md`](docs/MODEL.md) — scientific model specification:
  equations, units, assumptions, parameter provenance, numerical method, and
  known limitations.
- [`CLAUDE.md`](CLAUDE.md) — development and safety-critical engineering
  standards followed in this repository.

## License

Apache License 2.0 — see [`LICENSE`](LICENSE). Copyright Stuart Feichtinger.
