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

Sevoflurane, isoflurane, and desflurane are each modeled from the Gas Man
reference simulator's published partition data, not from primary
measurements — the primary human studies are cited beside every value, with
how far the shipped number sits from each (`docs/MODEL.md`, "Source
hierarchy"). Each agent's 30-minute wash-in lands inside the standard
deviation of the ratio Yasuda et al. measured in volunteers
(`tests/reference/test_published_wash_in.py`, which carries the citations and
states what that comparison does and does not establish). All three can be
picked in the interface, which identifies the selected agent by name and by
its ISO 5360 vaporizer color. Selecting an agent starts a new run at that
agent's own 1 MAC: switching agents does **not** model washout of the
previous agent, because carrying residual agent across a switch is a
distinct, harder problem left to the anesthesia-machine milestone. Because
the switch begins a new run it discards the current one, so the interface
says what will be lost and asks first wherever there is a run to lose — and
does not ask where there is not. The delivered-concentration control is
limited to each agent's real vaporizer maximum.

Fresh gas flow, delivered concentration, alveolar ventilation, and cardiac
output can all be changed live during a run. Agent mass delivered,
exhausted, and stored across every compartment is tracked and checked
against a documented numerical tolerance.

A setting the model refuses is reported as refused and leaves the run
alone. A failure the model cannot continue past halts the run and says so,
rather than leaving the display reading "Running" over numbers that have
stopped advancing. A step is all-or-nothing: one that cannot be completed
is rolled back, so a halted run shows the last completed step rather than
a step abandoned partway through. A halted run is cleared by Reset.

Concentrations are displayed to 0.01 percentage points, which is the
resolution the numerical method supports rather than the resolution the
floating-point values carry: the shipped operator split disagrees with an
independent solution by up to 1.2e-2 percentage points across the settings
the interface exposes, so a finer readout would present solver noise as model
output. A positive value too small to show reads `<0.01%`, so an empty
compartment stays distinguishable from an unresolved one.

Every compartment is also displayed as a multiple of the running agent's
1 MAC, written `×MAC`, and the chart carries both units as two axes on one
set of traces. That is the unit that survives an agent change — 2% is 1 MAC
of sevoflurane and about a third of a MAC of desflurane — so a percent axis
alone silently changes meaning when the agent does. Both units are always
shown rather than selected, because a unit toggle would make the axis a mode.
The MAC resolution is derived from the percent resolution rather than chosen
beside it, and works out to 0.01 MAC.

The chart's vertical range carries the same argument. It is fixed at 0 to
3 ×MAC for every agent rather than running to the agent's vaporizer dial,
which was 3 MAC of desflurane and 4.17 of isoflurane — so the same case drawn
under two agents used to be drawn at two scales, and comparing the wash-in
shapes was comparing a rescaling. It does not grow to fit a run, because an
axis that grew would redraw a rising curve at a smaller height partway
through a lesson. A trace that goes above the ceiling is named under the
chart rather than left to draw as a flat line at the top, which is what a
plateau looks like.

Any compartment's trace can be turned off, because the legend under the
chart is also its control: a checkbox per compartment, as Gas Man has. "Why
does fat lag muscle" is a two-trace question, and it is unreadable against
four other lines crossing it. Turning one off changes what is drawn and
nothing else — every compartment's concentration stays in the readouts above
the chart, and the run itself is untouched — so a chart showing two curves is
a chosen view of six modelled compartments rather than a smaller model.

Under that chart is the graph the uptake literature is taught from:
`F_A/F_I`, the alveolar concentration as a fraction of the inspired one, on a
dimensionless axis fixed from 0 to 1. It is the same quantity the Yasuda
comparison above is made on, so the trace can be laid beside a published
figure. The denominator is the **modelled inspired concentration and not the
vaporizer dial** — the circuit only approaches the dial over its own time
constant — and the curve is the textbook one only while that concentration is
held constant, which is why every setting change is marked on this plot as
well as on the chart above it. The trace stops rather than inventing a value
where the ratio is undefined (nothing has reached the circuit yet) or above 1
(alveolar exceeds inspired, so the patient is returning agent and this is
elimination), ending on a ruled equilibrium line so the stop reads as an
arrival rather than a clipped edge, and the line beside the plot says which
boundary it stopped at.

A MAC multiple here is a **partial-pressure ratio, not a depth of
anesthesia**, and on the five non-alveolar compartments that distinction is
the whole point: it says that compartment's partial pressure equals N times
the alveolar concentration that would be 1 MAC. The simulator models no
anesthetic depth — no effect-site compartment, no BIS, no age adjustment, no
summing of MAC across agents — and the divisor is a tier-3 value the display
names on screen so it can be converted back. Also not modeled: agents beyond
these three, IV anesthetics, metabolism, or any decision support. See
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
make check       # ruff format --check, ruff check, mypy (strict), the
                 # type: ignore checker, pytest across every core under a
                 # 100% statement and branch coverage gate on
                 # src/anesthesia_sim/core/, then the docket,
                 # documentation, contrast and import-boundary checkers
make fix         # ruff format, ruff check --fix, and write any pull
                 # request number a landed closure is owed
make test        # pytest across every core, without the coverage gate
make docket      # validate docs/items/ and list anything untriaged
make release VERSION=<next>  # cut a release: bump and relock, then name the
                 # ROADMAP.md edits it does not write
make doc-check   # validate the package map, provenance table, citations,
                 # release train, frozen-list counts, current-baseline
                 # version, and release tags
```

`mypy` runs in strict mode over `src/`, `tools/` and
`subprojects/docket/src/`. Those paths are named once, in `[tool.mypy] files`
in `pyproject.toml`, which also records why `tests/` sits outside the gate.

Sitting outside the gate does not leave the test trees' suppressions unread.
`tools/ignore_check.py`, which `make check` runs immediately after, evaluates
`warn_unused_ignores` over `tests/` and `subprojects/docket/tests/` and fails on
a `type: ignore` that suppresses nothing — the guarantee `RUF100` gives for
`noqa`, arriving through the other tool. It reports an unresolved import as
"not checked" rather than as a clean run, because an unresolved module makes
live directives look inert. It shells out to mypy, so unlike the two scripts
below it needs the project virtualenv.

`tools/import_boundary_check.py` is the same shape for a set of invariants
declared in one table. `core/parameters.py` is the one module allowed to import
Pydantic, so that the compartments, the controller and the interface hold plain
frozen dataclasses rather than validation models; and no module under `core/`
may import `time`, `datetime`, `random`, `secrets` or `uuid`, so that a run
stays a function of its inputs and of its step count rather than of what the
machine was doing. Both were prose — a docstring and a guarantee in
`docs/MODEL.md` — and nothing measured either. Like `ignore_check.py` it needs the project interpreter, though
for an unrelated reason — it parses `src/`, and `src/` targets 3.14.

`tools/doc_check.py`, `tools/contrast_check.py` and `tools/branch_id_check.py`
are stdlib-only scripts that run in a bare checkout. `doc_check.py` also has a
`candidates` mode that prints the documentation lines mentioning anything a diff
changed, for the sweep a change needs before it is complete.

Running in a bare checkout means running under whatever `python3` is on PATH,
which is older than the 3.14 this project requires. `tools/ruff.toml` and
`subprojects/docket/ruff.toml` therefore pin the formatter to that floor, so
it cannot rewrite either tree into syntax the interpreter that actually runs
it cannot parse; `tests/unit/test_tools_portability.py` and
`subprojects/docket/tests/test_portability.py` hold them to it, and hold both
trees to importing nothing a bare checkout does not already carry.

Those tests approximate the older interpreter; the floor section of
`.github/workflows/quality.yml`'s `checks` job is the run itself. It runs
before the uv install, so no virtualenv exists yet to fall back on. It installs
the declared floor and executes
`python3 tools/doc_check.py check`, `python3 tools/branch_id_check.py`,
`bin/docket check` and `python3 tools/contrast_check.py` under it, which settles
syntax, imports and runtime behavior together rather than one at a time.

`make check` mirrors the checks run in CI (`.github/workflows/quality.yml`)
and must pass before a change is considered complete. It runs those
stdlib-only commands under whatever `python3` is on your PATH rather than under
a pinned interpreter, so on a machine already at 3.14 CI's floor section is the
only place they meet the older one.

CI checks out the full history (`fetch-depth: 0`), which a local
clone usually does not have. Three checks need it and say so rather than
guessing when they lack it — the release-tag read in `tools/doc_check.py`,
and the recorded- and missing-pull-request reads in `bin/docket check`. So a
shallow checkout that reports them as not checked is working correctly, and
CI is where they actually run.

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
- [`docs/references/`](docs/references/README.md) — source documents held on
  hand so a session can read them rather than recall them, with the full
  citation for each. Publisher-copyright works under the owner's personal
  access, not covered by this repository's license, and they have to be
  removed from the history before the repository could be made public.
- [`CLAUDE.md`](CLAUDE.md) — development and safety-critical engineering
  standards followed in this repository. The standards that apply only to part
  of the tree, and the shape a reply takes, live alongside it in
  [`.claude/rules/`](.claude/rules).
- [`docs/maintainer.md`](docs/maintainer.md) — the notes addressed to whoever
  runs the sessions rather than to the sessions themselves.

## License

Apache License 2.0 — see [`LICENSE`](LICENSE). Copyright Stuart Feichtinger.
