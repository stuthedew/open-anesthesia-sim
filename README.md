> [!WARNING]
> # PRE-RELEASE
> # Work in Progress

# Open Anesthesia Simulator

A deterministic simulator of inhaled-anesthetic uptake and distribution, built
for teaching.

> [!WARNING]
> **This is an educational simulator, not a medical device.** It is not a
> clinical prediction tool, a dosing tool, or a patient monitor, and nothing it
> displays should be used to guide the care of a real patient. Every value on
> screen is a model output, never a measurement.

## What it is for

Uptake and distribution is taught from curves, and the curves are hard to
watch. Six compartments move at once and none of them on a timescale that
suits a teaching session: the circuit turns over in minutes, muscle in hours,
fat over days, while the induction the learner is actually looking at is a few
minutes long. The shape of any one curve depends on four settings that
interact. A figure in a textbook shows one case and cannot answer the question
that always follows it — *what if the fresh gas flow were lower?*

This simulator answers that question by running the case. It is written for two
readers:

- **Educators and trainees** in anesthesiology and critical care, who want to
  drive a case, change something mid-run, and see where the agent goes.
- **Contributors** with a foot in both anesthesiology and code, who want to
  extend a model whose every equation, constant and assumption is written down.

What distinguishes it from a demonstration is that the whole chain is
inspectable and reproducible. The governing equations, units, numerical method
and known limitations are specified in
[`docs/MODEL.md`](docs/MODEL.md); every parameter names its source *and the
strength of that source*; and a run is deterministic — the same inputs give the
same run, sample for sample — so a curve can be reproduced, cited, and argued
with.

## What it simulates

One reference adult and one volatile agent at a time — sevoflurane, isoflurane
or desflurane — carried from the vaporizer through an explicit breathing
circuit into alveolar gas, blood, and three tissue groups, with mixed-venous
return to the lungs:

```text
delivered agent -> breathing circuit -> alveolar gas -> blood
                -> vessel-rich group / muscle / fat -> mixed venous return
```

Four settings change during a run without disturbing what is already in the
patient: **fresh gas flow, delivered concentration, alveolar ventilation and
cardiac output**. Each is supported over a stated interval, and a setting
outside it is *refused* rather than quietly clamped, because a clamped setting
would simulate and display a case nobody asked for. A change the model cannot
continue past halts the run and says why, instead of leaving the display
reading "Running" over numbers that have stopped advancing.

While a case runs, the interface shows:

- every compartment concentration, in percent **and** as a multiple of the
  running agent's 1 MAC, with that agent's 1 MAC stated on screen — the same
  percentage is a different MAC multiple for each agent, so neither unit is
  safe alone;
- the agent that is running, by name and by its ISO 5360 vaporizer color;
- agent delivered, exhausted and stored, with the mass-balance residual;
- every setting changed during the run, marked on the chart at the simulated
  time it took effect;
- the wash-in curve the literature is taught from, $`F_A/F_I`$, on a
  dimensionless axis of its own, drawn against the *modeled* inspired
  concentration rather than the vaporizer dial;
- the running agent's population MAC-awake as a labelled band, and its nominal
  1 MAC as a line.

Because muscle and fat cannot be watched in real time, a run can be played at
**1×, 5×, 20×, 60× or 300× real time**. The rate is a mode, so it is displayed
wherever simulated time is displayed and at every rate including real time.
Playing a run faster takes more of the same steps per tick rather than larger
steps: the same case at 1× and at 300× is the same arithmetic, sample for
sample. Separately, the **chart's time base** — how much of the case is in view,
from fifteen minutes to twelve hours, or the whole run so far — is chosen by the
reader and changes only what is drawn.

For what this models today and what is planned next, see
[`ROADMAP.md`](ROADMAP.md).

## What it does not simulate

Reading a value here as more than it is would be the likeliest way to be misled
by it, so the boundary is stated rather than left to be discovered:

- **Nitrous oxide, any second gas, and concentration or second-gas effects.**
- **Switching agents mid-run.** Choosing a different agent starts a new run;
  residual washout of the previous agent is not modeled.
- **Regional gas exchange** — no dead space, shunt, ventilation–perfusion
  mismatch, diffusion limitation, or airway sampling delay.
- **Metabolism, degradation, or reaction with circuit materials.**
- **Intravenous agents, effect-site compartments, and any measure of
  anesthetic depth** — no BIS, no age-dependent MAC, no summing of MAC across
  agents.
- **Alarms, thresholds, and recommendations of any kind.**

A MAC multiple here is therefore a **partial-pressure ratio, not a depth of
anesthesia**: it says a compartment's partial pressure equals *N* times the
alveolar concentration that would be 1 MAC in a population, and nothing about
the simulated patient's state of consciousness. The full list, with the
simplifications each one rests on, is in `docs/MODEL.md` under "Known
limitations" and "Model boundary".

## Running it

**There is no packaged application yet.** Installers, code signing and
distribution are planned but deliberately out of scope for now, which means
that today the only way to run the simulator is to build it from source. If you
want to *use* it rather than work on it, that is the honest answer rather than a
shortcut being withheld, and [`ROADMAP.md`](ROADMAP.md) is where the packaging
work is tracked.

Building from source needs two things:

- **Python 3.14** — `.python-version` names the exact patch release, and `uv`
  installs it for you.
- **[uv](https://docs.astral.sh/uv/) 0.12.5 or newer.** `required-version` in
  `pyproject.toml` is a floor, so an older build stops with a clear message
  rather than quietly resolving the interpreter pin against a list that
  predates it.

```bash
git clone https://github.com/stuthedew/open-anesthesia-sim.git
cd open-anesthesia-sim
uv sync --locked --dev
make run          # or: uv run anesthesia-sim
```

For development, `make check` runs everything CI runs — formatting, linting,
strict type checking, and the full test suite under a 100% statement and branch
coverage gate on the simulation core — and must pass before a change is
complete. `make test` is the suite alone, without the coverage gate;
`make fix` applies the formatter and the safe lint fixes.
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) is the map of where new code
belongs.

## How the model is checked

The distinction the test suite is organized around is between **verification**
— the implementation solves the intended equations correctly — and
**validation** — those equations describe the phenomenon. A model can be
numerically flawless and physiologically wrong, and a suite made only of the
first would report that as though it had settled the second.

Verification is an independent from-scratch solution of the same system, an
analytic circuit solution preserved from before there was a patient, mass
balance closed to a documented tolerance, the zero-flow and equilibrium limits,
directional tests on solubility and ventilation, and a deterministic-replay
test.

Validation is one test, and it is deliberately not oversold:
`tests/reference/test_published_wash_in_and_elimination.py` compares each agent's $`F_A/F_I`$
at 30 minutes against the volunteer measurements of Yasuda et al., and all
three land inside the measured spread. That module states its own caveats at
length — the published subjects were breathing nitrous oxide, which this model
cannot reproduce, and the shipped partition coefficients descend from the same
lineage as the data being compared against. Passing it shows this implementation
reproduces its parameter set's intent, not that the parameter set is
independently right.

That last point generalizes, and it is why parameter provenance is graded
rather than merely cited. `docs/MODEL.md` distinguishes a primary measurement
from a secondary synthesis from a reference implementation's parameter set, and
says which tier each shipped number actually sits on. Moving the remaining
values onto primary sources is open work, tracked in
[`ROADMAP.md`](ROADMAP.md).

## Documentation

- [`docs/MODEL.md`](docs/MODEL.md) — the scientific specification: equations,
  units, conventions, parameter provenance, numerical method, required
  invariants and tests, interface requirements, assumptions and known
  limitations. If a statement's truth depends on the model version, it lives
  here rather than in this file.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — how `core/`, `app/` and
  `data/` fit together, and where new code belongs.
- [`ROADMAP.md`](ROADMAP.md) — the authoritative version and milestone map.
- [`docs/items/`](docs/items) — the development queue, one file per item, each
  carrying a brief written for someone who has never seen it.
- [`CLAUDE.md`](CLAUDE.md) — the engineering and safety-critical standards this
  repository is developed under.

## Contributing and getting help

Questions, bug reports and suggestions belong in
[GitHub issues](https://github.com/stuthedew/open-anesthesia-sim/issues). The
project is maintained by [Stuart Feichtinger](https://github.com/stuthedew).

[`CONTRIBUTING.md`](CONTRIBUTING.md) is the short version: what CI checks, what
a change is held to, and how to add a source document. You do not need to know
anything about the development queue to send one — the `PL-XXXX` pull request
titles are a maintainer's bookkeeping, and nothing checks yours for an id.

Corrections to the science are especially welcome, and the more specific the
better: `docs/MODEL.md` cites its sources precisely so that a disagreement can
be about a measurement rather than about a recollection.

## Citation

If you use this software, cite it through
[`CITATION.cff`](CITATION.cff) — GitHub renders it into APA and BibTeX from the
**Cite this repository** button in the sidebar.

## License

[Apache-2.0](LICENSE).
