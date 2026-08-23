# Open Anesthesia Simulator

An open-source, deterministic anesthesia simulation for education. It models
volatile-agent delivery, uptake, and distribution through an explicit
breathing circuit, alveolar gas, blood, and tissue compartments.

**This is an educational tool, not a clinical prediction, dosing, or
monitoring device.** No output should be used to guide real-world patient
care.

## Current status: v0.1.0

The simulator currently models sevoflurane wash-in, uptake, tissue
distribution, mixed-venous return, and washout in a single reference adult
patient:

```text
delivered sevo -> breathing circuit -> alveoli -> blood
               -> vessel-rich group / muscle / fat -> mixed venous return
```

Fresh gas flow, delivered concentration, alveolar ventilation, and cardiac
output can all be changed live during a run. Agent mass delivered, exhausted,
and stored across every compartment is tracked and checked against a
documented numerical tolerance.

Not yet modeled: other volatile agents, IV anesthetics, metabolism,
effect-site/MAC/BIS predictions, or any decision support. See
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
make check   # ruff format --check, ruff check, mypy (strict), pytest
make fix     # ruff format, ruff check --fix
make test    # pytest only
```

`make check` mirrors the checks run in CI (`.github/workflows/quality.yml`)
and must pass before a change is considered complete.

## Documentation

- [`ROADMAP.md`](ROADMAP.md) — authoritative version and milestone map.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — how `core/`, `app/`, and
  `data/` fit together, and where new code belongs.
- [`docs/MODEL.md`](docs/MODEL.md) — scientific model specification:
  equations, units, assumptions, parameter provenance, numerical method, and
  known limitations.
- [`CLAUDE.md`](CLAUDE.md) — development and safety-critical engineering
  standards followed in this repository.
