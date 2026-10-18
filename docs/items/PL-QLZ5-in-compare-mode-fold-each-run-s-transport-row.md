---
id: PL-QLZ5
title: In compare mode, fold each run's transport row and readout heading line into one line, so the 1366 by 700 laptop reference gives the concentration chart back roughly 70 to 80 px (PL-JG82)
priority: P1
effort: M
status: done
classes: safety
feature: interface-areas
milestone: v0.5.30
touches: src/anesthesia_sim/app/, tests/integration, docs/MODEL.md
added: 2026-10-18
closed: 2026-10-18
pr: 1609
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

**Built 2026-10-18.** While two runs are compared, `RunView.set_comparing`
folds each run's two lines into one (`_fold_heading_into_transport`). The
run's delivered concentration moves onto its transport row, after the status
word. The agent chip lays its lock caption beside the agent's name instead of
under it, at one width for both runs, measured from the widest agent name and
the widest caption. The values both runs share are stated once, on the first
run's heading line above the paired readouts: the substance, the
interpretation line, the agent's 1 MAC and the version-and-model badge. The
second run's readout section is hidden, and its `unconditional_widgets` names
the first run's substance and 1 MAC labels. That is true because `add_run`
refuses a run on another agent and a branch's MAC is checked against its
trunk's when it is opened. A lone run is laid out exactly as before, and the
fold is undone when the branch is dropped.

The brief put 1 MAC on each run's line. It is on the shared heading line
instead, because both runs' 1 MAC is one value and a line holding it twice did
not fit 1073 px beside the transport controls. This is a placement choice, a
placeholder under the project owner's 2026-10-18 rule; the value is still on
screen and labelled with the agent. The chip's and the badge's inset above and
below the text drops from 8 px and 6 px to 2 px while folded, so a run's line
is one selector high. That is also a placeholder.

**Measured** with `QT_QPA_PLATFORM=offscreen` at 1366 by 700 on the offscreen
font. One run: region 175 px, unchanged, which leaves the chart 392 px by
`PL-JG82`'s budget formula. Two runs: region 366 px before and 303 px after,
63 px back, which leaves the chart about 264 px instead of 201 px. Each run's
line is 27 px, the selector's height, where it was 48 px. The shared heading
line is 21 px, the badge's height, where it was 15 px. The estimate of 70 to
80 px was not reached because the badge now sits on the heading line. The
other 24 px of slack in compare mode is the empty notice column's spacing,
filed separately as `PL-T91K`.

**Rule 6.** `test_two_compared_runs_take_one_line_each_above_one_shared_heading`
fails against the code before the fix (`git stash push src/` then
`QT_QPA_PLATFORM=offscreen uv run pytest -q tests/integration/test_simulation_view.py -k compared_runs_take_one_line`):
`assert False` where `False = line.isAncestorOf(run._delivered_text)`.
