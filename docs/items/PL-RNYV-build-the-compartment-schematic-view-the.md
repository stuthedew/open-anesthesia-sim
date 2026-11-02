---
id: PL-RNYV
title: Build the compartment schematic View: the circuit, the alveoli, venous blood and the three tissue groups as containers filled to tension, each labelled with its tension and its amount of agent vapour
priority: P1
effort: L
status: done
classes: safety, anticipated
feature: schematic
touches: src/anesthesia_sim/app, tests/integration, tests/unit, tools/contrast_check.py, docs/MODEL.md, docs/ARCHITECTURE.md
blocked-by: PL-2881, PL-KFTM
added: 2026-10-25
closed: 2026-11-01
pr: 1921
payoff: a learner can place the compartment schematic in any Area and see each compartment's tension and amount for every displayed run, never a state the run has left
verify: grep -q 'ViewKind("compartment_schematic")' src/anesthesia_sim/app/view_registry.py
---

**Where this came from.** `PL-LF0P` scoped v0.7.0, the schematic, on 2026-10-25. The project owner chose containers that fill to tension, labelled with their amounts, plus a bar showing each compartment's share of the agent (project owner, 2026-10-25, ratified, over containers drawn to scale and over Gas Man's Picture as it is). `ROADMAP.md` § "v0.7.0 - the schematic" has the reasoning and the measurements behind it.

**Problem.** No View draws how the compartments connect, or where the agent
is. The chart puts six tension traces on one axis.

**What to build.** One registered View kind, built against the View contract
(`src/anesthesia_sim/app/view_contract.py`) like every other View, so any Area
can hold it and compare mode draws one schematic per displayed run. It draws
the circuit, the alveoli, venous blood, the vessel-rich group, muscle and fat
as containers in the order agent reaches them, joined as the circulation
joins them. Each container fills to its tension on the run's shared scale and
is labelled with its name, its tension and its amount, as `PL-2881` specifies.
It shows the run's current instant and redraws on every frame the readouts
redraw on. It declares the least size it can be read at. Its colours are the
compartment trace colours `app/theme.py` already holds.

**Tests.** An end-to-end test runs patient inputs through the model to the
drawn labels. A test drives a reset, an agent change, a branch, a return to a
mark and compare mode on and off, and checks after each that every label
matches the snapshot. `tools/contrast_check.py` covers every colour drawn.

**Why it matters.** This is the milestone's main View, and the one that
teaches what the chart cannot.

**Done when.** The View is in the registry, reachable from every Workspace's
View chooser, and the tests above pass.

**Generator check.** None: the only workflow path touched is
`tools/contrast_check.py`, which gains this View's colours as every new View's
colours are added, and that produces no findings of its own.

**Checked 2026-10-25 (`PL-F2NX`, Gate 3's staleness sweep): still true.** `app/view_registry.py` registers no schematic View, the six compartment colours are in `app/theme.py`, and both blockers, `PL-2881` and `PL-KFTM`, are open.

**What `PL-2881` settled for this build, 2026-11-01.** `docs/MODEL.md` § "The compartment schematic: what its heights, amounts and share bar assert" is the specification. Three parts of it need code here. First, each container fills against `chart_axis_top_percent`, the chart's own axis top, and a tension above it fills the container and is marked off the scale while its label keeps the value. Second, an amount is shown to two significant figures and never finer than 0.01 mL, with `<0.01 mL vapour` below that and `0 mL vapour` at zero (§ "Displayed precision"). `AgentAmountPrecision` holds a count of decimals, so it needs a significant-figure form for `AgentAmount.COMPARTMENT`, and `test_a_unit_with_no_derived_precision_is_refused` changes with it. Third, the unit is written "mL vapour", and that spelling goes into `DisplayUnit` so no View writes its own. The schematic's heading carries "Model outputs — not measurements." The two hazard rows that name this item need their tests.

**Closed 2026-11-01, by `#1921`.** `CompartmentSchematicView` is registered as `compartment_schematic` and offered in every Workspace's View chooser. Each schematic is a run surface, `RunSchematic` in `app/qt_schematic.py`, which `RunView` writes, withholds and names beside its readouts. So a Reset or an agent change that no frame draws withholds it as it withholds the readouts. The containers stand in the readout row's order, and the three tissue groups are drawn in parallel between an arterial and a venous line, because the model perfuses them in parallel. Each schematic says the simulated instant it shows, because two compared runs can stand at different times. Its off-scale mark reads the chart's own test, `above_the_axis_top`. Three decisions were placeholders and are recorded here as such: the container sizes and colours, the wording of the heading, captions and instant line, and naming each run on the instant line while runs are compared. The two blind passes, one adversarial pass and the prose review are recorded in the commit trailers and the pull request body.
