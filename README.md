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

- Python 3.14 — `.python-version` names the exact patch release, and
  `uv sync` installs it
- [uv](https://docs.astral.sh/uv/) 0.12.5 or newer for dependency management
  and running commands. `required-version` in `pyproject.toml` is the floor,
  so an older build stops with `Required uv version ">=0.12.5" does not match
  the running version` rather than quietly resolving `.python-version` against
  an interpreter list that predates the pin. `uv self update` is the fix;
  where that is rate-limited, `python3 -m pip install --user --upgrade uv`
  installs the same binary from PyPI.

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
make release VERSION=0.3.0   # cut a release: bump and relock, then name the
                 # ROADMAP.md edits it does not write
make doc-check   # validate the package map, provenance table, citations,
                 # release train, frozen-list counts, current-baseline
                 # version, and release tags
```

`mypy` runs in strict mode over `src/`, `tools/` and
`subprojects/docket/src/`. Those paths are named once, in `[tool.mypy] files`
in `pyproject.toml`, which also records why `tests/` sits outside the gate.

The last two are stdlib-only scripts in `tools/`, so they run in a bare
checkout. `tools/doc_check.py` also has a `candidates` mode that prints the
documentation lines mentioning anything a diff changed, for the sweep a
change needs before it is complete.

Running in a bare checkout means running under whatever `python3` is on PATH,
which is older than the 3.14 this project requires. `tools/ruff.toml` and
`subprojects/docket/ruff.toml` therefore pin the formatter to that floor, so
it cannot rewrite either tree into syntax the interpreter that actually runs
it cannot parse; `tests/unit/test_tools_portability.py` and
`subprojects/docket/tests/test_portability.py` hold them to it, and hold both
trees to importing nothing a bare checkout does not already carry.

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
  standards followed in this repository. The standards that apply only to part
  of the tree, and the shape a reply takes, live alongside it in
  [`.claude/rules/`](.claude/rules).
- [`docs/maintainer.md`](docs/maintainer.md) — the notes addressed to whoever
  runs the sessions rather than to the sessions themselves.

## License

Apache License 2.0 — see [`LICENSE`](LICENSE). Copyright Stuart Feichtinger.
