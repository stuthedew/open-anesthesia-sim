---
id: PL-GS3R
title: The drawn chart's worst error moved from the control change to the steep early wash-in, and PL-4RBD's 0.32 MAC only fell to 0.26 MAC: uniform columns chord across the same width M4's buckets did
priority: P1
effort: M
status: needs-decision
classes: defect, safety
feature: teachable-case
touches: src/anesthesia_sim/core/run_score.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/chart_series.py, docs/MODEL.md
added: 2026-09-08
---

**Problem.** The drawn chart's worst error moved from the control change to the steep early wash-in, and PL-4RBD's 0.32 MAC only fell to 0.26 MAC: uniform columns chord across the same width M4's buckets did

**Why it matters.** `PL-4RBD` was re-banded `P1` `safety` on 0.32 MAC of
departure between the drawn trace and the run, and closed on the
understanding that evaluating columns removed it. Most of it is still there -
0.26 MAC at the 12 h base - and it has moved to the steep early wash-in,
which is the part of a case a learner is most likely to be studying. A trace
drawn below the run during induction, with nothing on screen saying the shape
between plotted points was inferred, is the presentation failure
`CLAUDE.md`'s clinical-output standard names rather than a fidelity
preference.

**Measured 2026-09-08, after `PL-2FM6` landed.** Same method as `PL-4RBD`'s
re-measurement - a real 12 h run at the envelope corner (FGF 10, V_A 12,
Q 10), sevoflurane 2% to 4% at t = 600 s, worst error of the drawn polyline
against the 0.1 s trace - but against the shipped evaluated columns rather
than against M4:

| Base | M4 alveolar | Evaluated alveolar | as MAC | worst at |
| --- | ---: | ---: | ---: | ---: |
| 15 min | 0.0124 pp | 0.0117 pp | 0.006 | t = 2.7 s |
| 1 h | 0.1005 pp | 0.0401 pp | 0.020 | t = 6.3 s |
| 4 h | 0.2145 pp | 0.1988 pp | 0.097 | t = 44.5 s |
| 12 h | 0.6467 pp | **0.5322 pp** | **0.260** | t = 85.8 s |

**What actually improved, and what did not.** `PL-2FM6` removed the *kink*
component: the worst error is no longer at the control change at t = 600 s,
which is `PL-4RBD`'s defect and is genuinely gone. It did **not** remove the
*curvature* component. Columns sit at the spacing the time base and the
column budget imply, and the chart rules a straight line between adjacent
columns - so at a 12 h base the chord spans about 290 s of a curve, which is
the same width M4's 4 096-sample bucket spanned. The error therefore fell
from 0.315 MAC to 0.260 MAC rather than to nothing.

**This corrects a claim made in `#488` and in `PL-4RBD`'s and `PL-2FM6`'s
close-out notes**, which said that most of the 0.65 pp was curvature "which
no selection of recorded extremes can reach" and that an evaluated column
therefore fixed both halves. The first half of that is true; the conclusion
does not follow, and the measurement above is what settles it. `docs/MODEL.md`
does not carry the error claim and needs no correction - it states the two
rules that place a column, both of which are accurate.

**Why the worst error moved to the start of the run.** The steep early
wash-in is where curvature is highest: the circuit fills on its own time
constant (V/FGF = 36 s at FGF 10 with a 6 L circuit) while the alveolar
trace lags it. A uniform grid spends the same column width there as it does
across an hour of near-equilibrium, so it is least resolved exactly where the
trace is most interesting - which is also where a learner watching an
induction is looking.

**Decision needed.** Whether to buy resolution with more columns, with a
curvature-adaptive grid, or to accept 0.26 MAC and state the bound in
`docs/MODEL.md`. Three routes, and they are not equivalent:

1. **More columns at wide time bases.** Cheapest to state, and it trades
   directly against the frame: `CHART_COLUMN_BUDGET_PER_SERIES` times traces
   drawn times about 24.5 us is the chart's share of a frame (`PL-YSZN`,
   `PL-YDKJ`), so doubling columns roughly doubles that share. At 150 columns
   a saturated frame was 42.8 ms against a 200 ms budget, so there is room -
   but it buys a factor of four in the error for a factor of two in cost, and
   it helps everywhere rather than where the curvature is.
2. **Non-uniform columns, denser where the second derivative is large.** The
   right answer numerically, and the expensive one: the chained-propagator
   optimisation `evaluate_anchored` depends on requires uniform spacing
   within a segment, and a propagator is about 1.29 ms against 6.2 us for a
   chained product. A curvature-adaptive grid would need its own scheme -
   perhaps a fixed dyadic refinement near each segment opening, which keeps
   the spacing uniform *within* each refinement level.
3. **Accept it and say so.** 0.26 MAC at a 12 h base, in the steep early
   wash-in, on a trace whose whole purpose is showing the shape of an
   induction. `CLAUDE.md`'s standard asks that uncertainty be visible rather
   than that it be zero, so an accepted bound stated in `docs/MODEL.md` is a
   legitimate answer - but it is the project owner's to give, which is why
   this is `needs-decision` rather than `ready`.

**Done when.** The project owner has chosen a route; if 1 or 2, the drawn
polyline's worst departure is measured again at every rung of
`TIME_BASE_LADDER` and recorded in `docs/MODEL.md`; if 3, `docs/MODEL.md`
states the bound and where it sits.
