[![quality](https://github.com/stuthedew/open-anesthesia-sim/actions/workflows/quality.yml/badge.svg)](https://github.com/stuthedew/open-anesthesia-sim/actions/workflows/quality.yml)

> [!WARNING]
> **Pre-release: the simulator is unfinished.** Features, settings and displayed values
> may change before the first release.

# Open Anesthesia Simulator

A deterministic simulator of inhaled-anesthetic uptake and distribution, built
for teaching.

> [!WARNING]
> **This is an educational simulator, not a medical device.** It is not a
> clinical prediction tool, a dosing tool, or a patient monitor, and nothing it
> displays should be used to guide the care of a real patient. Every value on
> screen is a model output, never a measurement.

![The simulator's window after ten simulated minutes of sevoflurane delivered at 2.00% (1.00 times MAC) with a fresh gas flow of 4.0 L/min, played at 1× real time. A row of readouts gives the modelled concentrations, each also as a multiple of MAC: circuit 1.61%, alveolar 1.25%, mixed venous 0.83%, vessel-rich group 1.09%, muscle 0.06% and fat <0.01%. Below them, a chart traces each compartment over time against a dashed line at 1 MAC and a shaded MAC-awake band, beside the four setting controls.](assets/screenshots/dashboard.png)
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->
<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->

*The default case after ten simulated minutes, rendered on 2026-11-09 from the
code after release 0.6.16. Every value shown is a model output. The script
`tests/benchmarks/readme_screenshot.py` retakes the image.*

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

### The model

The model follows one volatile agent at a time (sevoflurane, isoflurane or
desflurane) in a built-in reference adult, who cannot be changed. The agent
passes from the vaporizer through an explicit breathing circuit into alveolar
gas, blood and three tissue groups, with mixed-venous return to the lungs:

```text
delivered agent -> breathing circuit -> alveolar gas -> blood
                -> vessel-rich group / muscle / fat -> mixed venous return
```

You can change four settings during a run without disturbing what is already in
the patient: **fresh gas flow, delivered concentration, alveolar ventilation and
cardiac output**. Each has a supported range, listed in
[`docs/INTERFACE.md`](docs/INTERFACE.md) § "Supported input ranges". The simulator
refuses a setting outside its range, rather than quietly using the nearest value
in range and showing a case nobody asked for. When the model cannot continue
after a change, the simulator stops the run and says why.

### The window

The window is divided into Areas, which you can split, join, resize, swap and
close. Each Area holds one View, and its View chooser offers all eight: the
concentration chart, the wash-in plot, the parameter controls, the bookmarks,
the branch control, the agent accounting, the compartment schematic and the
agent cost. An arrangement is kept as a Workspace, and you switch between
Workspaces by their tabs. Three come with the simulator: Default, Induction and
Maintenance. The Areas share the window's height below the region described
next. A View that needs more room than its Area scrolls inside the Area, so on
a 1366 by 768 laptop screen the window itself does not scroll.

A region outside the Areas shows the simulated time, the playback speed, whether
the simulation is running or halted and why, the agent and its 1 MAC, the
delivered concentration, each compartment's concentration, and the list of
settings changed during the run, with when each took effect and its value. You
need these values to read any other number, so no arrangement can remove them.

The agent appears by name and in its ISO 5360 vaporizer color. Every
concentration is given in percent **and** as a multiple of the agent's 1 MAC.
The same percentage is a different MAC multiple for each agent, so neither unit
is safe alone.

While a case runs, the window shows the following.

- The bookmarks View lists the instants and the MAC multiples you marked, and
  opens the editor that adds and removes them. All three Workspaces include
  this View.
- The branch View opens a second run from an earlier instant of the case. The
  second run is drawn beside the first, so you can change a setting and
  compare the two. All three Workspaces include this View.
- The agent accounting View shows the agent delivered, exhausted and stored,
  and any agent left unaccounted for. None of the three Workspaces includes
  this View.
- The compartment schematic View shows where the agent is. Each compartment is
  drawn as a container, filled to its tension on the concentration chart's
  scale and labelled with its tension and its amount in mL of vapour. One bar
  shows each compartment's share of all the agent in the run, so fat's share
  can be seen growing while its tension stays near zero. The Maintenance
  Workspace includes this View.
- The agent cost View shows the agent delivered, in mL of the liquid that the
  vaporizer turned into vapour. You can choose litres of vapour instead, and the
  unit is named on the value. Your choice is saved in your preferences file and
  still applies after a restart.
- The agent cost View also shows what the delivered agent cost. You set a price
  per bottle for each agent, with a currency code and the date the price
  applied. The simulator comes with no prices, so until you set one, the View
  says why it shows no cost. Beside each cost are the liquid volume and the
  price per millilitre that were multiplied to give it.
- Each setting changed during the run is marked on the concentration chart at
  the simulated time it took effect.
- The wash-in plot draws $`F_A/F_I`$ on a dimensionless axis of its own. Its
  $`F_I`$ is the *modeled* inspired concentration, not the vaporizer dial
  setting. The Induction Workspace includes this plot.
- The running agent's population MAC-awake is drawn as a labelled band, and its
  nominal 1 MAC as a line.
- Hovering over a drawn point of a trace opens a readout. Its first line says
  that the value is modeled, and names the agent and the simulated time. While
  more than one run is drawn, the first line also names the run that the point
  belongs to. Below that is the value: for a compartment, its name and value in
  both units at the readouts' own resolution, and for the wash-in curve, the
  ratio. Hovering shows nothing between drawn points, over a reference band or
  line, or over a mark for a changed setting.

### Playback speed and time base

A run can be played at **1×, 5×, 20×, 60× or 300× real time**, because changes
in muscle and fat are too slow to watch as they happen. The playback speed is
displayed wherever simulated time is, even at 1×. The same case gives identical
values, sample for sample, at 1× and at 300×, because the simulator plays faster
by computing more steps of the same size each second.

You choose each chart's **time base**: how much of the case is in view, from
fifteen minutes to twelve hours, or the whole run so far. The time base affects
only what is drawn.

## What it does not simulate

- **Nitrous oxide, any second gas, and concentration or second-gas effects.**
  Nitrous oxide is planned. The scope word differs between this page and the
  package for that reason: this page says *inhaled*, the subject the project
  teaches, and `pyproject.toml` says *volatile*, the three agents this release
  models (`PL-XF89`).
- **Switching agents mid-run.** Choosing a different agent starts a new run.
  Washout of the previous agent is not modeled.
- **Regional gas exchange.** There is no dead space, shunt,
  ventilation–perfusion mismatch, or diffusion limitation.
- **Airway sampling delay.**
- **Metabolism, degradation, or reaction with circuit materials.**
- **Intravenous agents, effect-site compartments, and any measure of
  anesthetic depth.** There is no BIS, no age-dependent MAC, and no summing of
  MAC across agents.
- **Alarms, thresholds, and recommendations of any kind.**

A MAC multiple here is therefore a **partial-pressure ratio, not a depth of
anesthesia**. A multiple of *N* means that a compartment's partial pressure
equals *N* times the alveolar concentration that would be 1 MAC in a population.

The full list is in `docs/MODEL.md` § "Known limitations" and
§ "Model boundary", with the simplifications behind each item. For what the
simulator models today and what is planned next, see [`ROADMAP.md`](ROADMAP.md).

## How the model is checked

The tests are organized around two questions. **Verification** asks whether the
code solves the intended equations correctly. **Validation** asks whether those
equations describe the real physiology. A model can solve its equations without
error and still be physiologically wrong, so verification tests alone cannot
answer the second question.

Verification uses these tests:

- a comparison with an independently written solution of the model's equations
- a comparison with an exact solution for the breathing circuit
- a check of mass balance, to within a documented tolerance
- checks at zero flow and at equilibrium
- checks that changing solubility or ventilation moves the results in the
  expected direction
- a check that replaying a case gives identical results

Validation is one test (`tests/reference/test_published_wash_in_and_elimination.py`).
It compares each agent's $`F_A/F_I`$ at 30 minutes with the volunteer
measurements of Yasuda et al. All three agents' simulated values fall inside the
measured spread. The volunteers, however, were breathing nitrous oxide, which
this model cannot reproduce. The model's partition coefficients also come from
the same line of research as the volunteer data. A pass shows that the model
reproduces what its parameter set is meant to give, not that the parameter set
is independently right.

The validation test also compares the first five minutes of elimination, as
$`F_A/F_{A0}`$: the alveolar fraction divided by its value when the agent was
turned off. Here the model disagrees with the volunteers. It keeps more agent in
the alveoli than every published cohort did. Most of the difference comes from
the breathing circuit: the model always rebreathes, and the volunteers breathed
through a fresh non-rebreathing circuit. When a test removes the circuit's
effect, three of the four cohorts agree, but desflurane then washes out faster
than the volunteers did, a disagreement about how agent returns from the
tissues. The model's documentation gives the numbers and the reasons
(`docs/MODEL.md` § "Published wash-in and elimination validation test").

The model's documentation (`docs/MODEL.md`) therefore grades the cited source of
every value as a primary measurement, a secondary synthesis, or the parameter set
of another simulator used as a reference. Moving the remaining values onto primary
sources is open work, tracked in [`ROADMAP.md`](ROADMAP.md).

A further test compares simulated elimination with the mean washout curves that
Yasuda et al. published (`tests/reference/test_late_washout_against_published_fits.py`).
It covers 24 hours, the most the simulator allows. It records where the model's
tail lies above and below those curves. It passes whether or not the two agree.
The model's documentation gives the result (`docs/MODEL.md` §
"The first 24 hours of elimination against the published mean curves").
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

## Running it

**There is no packaged application yet.** The only way to run the simulator is
to build it from source. Installers, code signing and distribution are planned
but out of scope for now, and [`ROADMAP.md`](ROADMAP.md) tracks that work.

Building from source needs:

- **[uv](https://docs.astral.sh/uv/) 0.12.5 or newer.** An older uv stops with a
  message, because the project's settings require this minimum
  (`required-version` in `pyproject.toml`).
- **Python 3.15**, which uv installs for you. The file `.python-version` names
  the exact patch release.
- **On Linux, `libegl1`** (`apt install libegl1`). The Qt interface requires it,
  and the PySide6 wheels do not carry it. An ordinary desktop needs nothing
  else, because it already has the four other system libraries that Qt links:
  `libgl1`, `libxkbcommon0`, `libdbus-1-3` and `libfontconfig1`. For a minimal
  container, which may lack them, `docs/ARCHITECTURE.md` § "Dependencies" has
  the measured list of what the wheels expect from the system.
- **On macOS and Windows, nothing extra.**

```bash
git clone https://github.com/stuthedew/open-anesthesia-sim.git
cd open-anesthesia-sim
uv sync --locked --dev
make run          # or: uv run anesthesia-sim
```

## Documentation

- [`docs/MODEL.md`](docs/MODEL.md) — the scientific specification: equations,
  units, conventions, parameter provenance, numerical method, properties the
  model must always keep, required tests, assumptions and known limitations.
- [`docs/INTERFACE.md`](docs/INTERFACE.md) — the interface requirements: what
  the display must show, and what each control does.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — how the folders `core/`,
  `app/` and `data/` fit together, and where new code belongs.
- [`ROADMAP.md`](ROADMAP.md) — the authoritative version and milestone map.
- [`docs/items/`](docs/items) — the development queue, one file per work item,
  each with a brief written for someone new to the item.
- [`CLAUDE.md`](CLAUDE.md) — the engineering and safety-critical standards this
  project is developed under.

## Contributing and getting help

Questions, bug reports and suggestions belong in
[GitHub issues](https://github.com/stuthedew/open-anesthesia-sim/issues). The
project is maintained by [Stuart Feichtinger](https://github.com/stuthedew).

Corrections to the science are especially welcome, and the more specific the
better. The model description in `docs/MODEL.md` cites its sources precisely, so
a disagreement can be about a measurement rather than a recollection.

The short guide in [`CONTRIBUTING.md`](CONTRIBUTING.md) sets out the
requirements for a change and how to add a source document. The map in
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) shows where new code belongs.

You can send a change without knowing anything about the development queue.
The `PL-XXXX` ids in the project's pull request titles are the maintainer's
bookkeeping, and nothing checks your title for one.

A change is complete only when `make check` passes. It runs CI's checks:
formatting, linting, strict type checking, and the full test suite with a 100%
statement and branch coverage gate on the simulation core. A few checks run in
only one of `make check` and CI, so a passing `make check` does not guarantee a
passing CI run. A list in [`tools/doc_check.py`](tools/doc_check.py)
(`GATE_ONLY`) names them.

Run `make test` for the test suite alone, without the coverage gate. Use
`make fix` to apply the formatter and the safe lint fixes.

## Citation

If you use this software, cite it. The **Cite this repository** button in
GitHub's sidebar formats the citation in [`CITATION.cff`](CITATION.cff) as APA
and BibTeX.

## Acknowledgements

The interface's layout follows Blender's model of workspaces, areas and
editors. Blender is developed by the Blender Foundation and its contributors.
Blender's design was studied from its published source code and design
documentation. This project uses no Blender code and reproduces none of
Blender's documentation. See
[`docs/interface-provenance.md`](docs/interface-provenance.md) for what was
adopted, changed and refused, and for Blender's licences.

## License

[Apache-2.0](LICENSE).