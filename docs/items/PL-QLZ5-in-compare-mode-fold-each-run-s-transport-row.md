---
id: PL-QLZ5
title: In compare mode, fold each run's transport row and readout heading line into one line, so the 1366 by 700 laptop reference gives the concentration chart back roughly 70 to 80 px (PL-JG82)
priority: P1
effort: M
status: ready
classes: safety
feature: interface-areas
touches: src/anesthesia_sim/app/, tests/integration, docs/MODEL.md
added: 2026-10-18
payoff: compare mode on the 1366 by 700 laptop gives the chart back what folding the per-run lines saves, with every required value still named
verify: grep -q 'PL-QLZ5' tests/integration/test_simulation_view.py
---

**Problem.** With two runs compared, each run has a transport row and a
readout heading line of its own in the unconditional region. At a 1366 px
window each transport row wraps onto a second line (48 px instead of 29 px),
because compare mode adds the run name and a lock sentence to it. The heading
line under it adds another 15 px and spacing per run. `PL-JG82` measured the
region at 366 px with two runs, which leaves the concentration chart about
201 px on the 1366 by 700 laptop reference.

**Why it matters.** The project owner accepted a chart under 360 px in compare
mode on that reference, on the condition that layout wins back what it can
(`PL-JG82`, 2026-10-18). Folding each run's transport row and heading line
into one line is worth roughly 70 to 80 px by `PL-JG82`'s rows. That figure is
inferred from the row heights, not measured.

**Done when.** In compare mode each run's transport controls and its heading
values (run name, agent, delivered concentration, 1 MAC) share one line at a
1366 px window, every value `docs/MODEL.md` § "Minimum displayed outputs"
requires for each run is still on screen and named, and the chart height left
on the 1366 by 700 reference is measured and recorded in `PL-JG82`'s place in
`ROADMAP.md` Required scope entry 20.
