---
id: PL-CNCF
title: controller.drawn_window costs 6.2 ms a frame at the shipped 150-column budget - 99% of the frame's read and about eighty times the simulation at 1x
priority: P2
effort: M
status: ready
classes: perf
feature: chart-readout
touches: src/anesthesia_sim/core/run_score.py, src/anesthesia_sim/app/controller.py, docs/MODEL.md
added: 2026-09-08
verify: python3 tools/doc_check.py check && grep -qF 'drawn_window costs' docs/MODEL.md
---

**Problem.** controller.drawn_window costs 6.2 ms a frame at the shipped 150-column budget - 99% of the frame's read and about eighty times the simulation at 1x

**Measured 2026-09-08**, on the 4-vCPU container `PL-YSZN` and `PL-QXSB` used,
against a 1 800 s run at the fitted 15-minute base, median of 40 calls:

| Call | Median |
| --- | ---: |
| `SimulationController.drawn_window`, 150 columns | 6.15 ms |
| ...at 600 columns | 9.69 ms |
| ...at 2 400 columns | 25.81 ms |
| fraction-to-percent conversion, six traces | 0.06 ms |
| `SimulationController.snapshot` | 0.02 ms |

So the whole of a frame's read is the score evaluation: 6.18 ms of 6.24 ms.
About 4.9 ms of it is fixed and about 8.7 us per column marginal.

**Why it matters, and it is two separate things.** The measurement lands on
a cost nobody had attributed, and it has one consequence for what the chart
may draw and a second for what the frame budget actually pays for.

**The column budget is now bounded here rather than by the toolkit.**
`CHART_COLUMN_BUDGET_PER_SERIES` is 150 because Flet charged ~24.5 us per
point control per frame whether or not the point moved (`PL-YSZN`). `PL-QXSB`
measured Qt drawing 648 000 points in 1.96 ms, which was read as "the budget
stops mattering". It does not: it stops being a *drawing* constraint and
becomes an evaluation one. Raising the budget fourfold costs 3.5 ms a frame,
and sixteenfold costs 20 ms - which at the 200 ms render budget is affordable
and at a 60 Hz ambition is not.

**At 1x the chart read is about eighty times the simulation.** A frame
advances two steps - 0.08 ms - and then spends 6.2 ms evaluating 150 columns
of a run it has already advanced. Inside Flet that is invisible under 26-45 ms
of `page.update()`, which is why nothing has reported it; on any toolkit
without a diff it is the whole frame.

**What it is not.** Not a defect in `PL-2FM6`, which bought exactness at
control changes that no selection over recorded samples could give
(`PL-4RBD` measured the old path at 0.32 MAC of departure at the 12-hour
base). This is the price of that, stated.

**Worth checking before sizing any fix**: whether `RunScore.evaluate_anchored`
re-propagates columns whose values cannot have changed. `PL-2FM6`'s brief
records that anchoring keeps the columns in fixed *positions* so that a steady
frame moves only the newest one; if the evaluation nonetheless recomputes all
150 every frame, the anchoring is buying stability without buying work, and
memoizing completed segments is the obvious lever.

**Done when** the per-frame evaluation cost is either reduced or recorded as
accepted with a number beside it, and `docs/MODEL.md`'s statement of what a
drawn window costs agrees with the measurement.

**Why it matters, and it survives the port.** This is the one frame cost in the
2026-09-08 measurements that is not Flet's. `controller.drawn_window` is the
score evaluation - `core/run_score.py` and the controller, no toolkit in it - so
the PySide6 port removes the 26-45 ms `page.update()` term and leaves this one
standing at 6.2 ms. Inside Flet it was invisible under the diff; on Qt it is
about 99% of the frame's read and roughly eighty times the simulation at 1x.

That inverts what the column budget means. `CHART_COLUMN_BUDGET_PER_SERIES` is
150 because Flet charged per point control; `PL-QXSB` measured Qt drawing 648 000
points in 1.96 ms, which was read as the budget ceasing to matter. It does not -
it stops being a *drawing* constraint and becomes an *evaluation* one, at about
8.7 us per column. Raising the budget fourfold costs 3.5 ms a frame and
sixteenfold costs 20 ms, which is affordable against a 200 ms render budget and
is not against a 60 Hz ambition. `PL-GS3R`'s chord-width rule, which makes the
column count a function of the selected span, is sized directly by this number.

**Not a defect in `PL-2FM6`.** That change bought exactness at control changes
that no selection over recorded samples could give; this is the price of it,
stated rather than discovered later.
