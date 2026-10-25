---
id: PL-RNYV
title: Build the compartment schematic View: the circuit, the alveoli, venous blood and the three tissue groups as containers filled to tension, each labelled with its tension and its amount of agent vapour
priority: P1
effort: L
status: blocked
classes: safety, anticipated
feature: schematic
touches: src/anesthesia_sim/app, tests/integration, tests/unit, tools/contrast_check.py, docs/MODEL.md, docs/ARCHITECTURE.md
blocked-by: PL-2881, PL-KFTM
added: 2026-10-25
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
