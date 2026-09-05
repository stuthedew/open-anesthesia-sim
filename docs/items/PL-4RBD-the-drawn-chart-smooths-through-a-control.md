---
id: PL-4RBD
title: The drawn chart smooths through a control change that leaves the trace monotone, because M4 selects extremes and such a change is not one
priority: P2
effort: S
status: untriaged
added: 2026-09-05
classes: defect, ux
feature: teachable-case
touches: src/anesthesia_sim/app/chart_downsampling.py, src/anesthesia_sim/app/chart_series.py, docs/MODEL.md
---

**Problem.** `chart_downsampling` selects each bucket's minimum, maximum,
first and last sample, which is M4 as published (Jugel et al. 2014, held in
`docs/references/`). A vaporizer change makes the derivative of the circuit
fraction discontinuous, and whether that kink is drawn depends entirely on
which way the dial moved:

- **Turned down** — the circuit fraction stops rising and starts falling, so
  the kink *is* a local maximum, M4's `max` tuple lands exactly on it, and the
  drawn line is faithful.
- **Turned up mid-rise** — the trace keeps rising, only faster. The kink is
  interior to a monotone bucket, none of the four tuples lands on it, and the
  polyline is drawn straight through it.

Meanwhile the chart draws a vertical control-change mark at that exact
x-position (`PL-DR1Z`, record the control-input timeline, landed v0.3.7). So
the interface asserts "the dial moved here" over a trace that visibly does not
change there. Under `CLAUDE.md`'s safety-critical standard that is a
presentation failure rather than a cosmetic one: the annotation and the data
it annotates disagree, and the reader has no way to tell which to believe.

**Measured 2026-09-05.** Sevoflurane at the envelope corner (FGF 10,
V_A 12, Q 10), dial changed at t = 300 s of a 900 s run. Worst error of the
M4-drawn polyline against the full 0.1 s trace, over every bucket phase, in
the percentage points the readout is in (display resolution 0.01 pp):

| Bucket | 2% -> 4% (monotone) | 4% -> 0% (an extreme) |
| --- | ---: | ---: |
| 4 samples (0.4 s) | 0.0037 pp, at the change | 0.0001 pp, at the change |
| 16 samples (1.6 s) | 0.0202 pp, at the change | 0.0017 pp, away from it |
| 64 samples (6.4 s) | 0.0796 pp, at the change | 0.0246 pp, away from it |

In the turned-down column the worst error moves *away* from the change as
buckets widen — the kink is drawn exactly and the residual is ordinary
curvature elsewhere. In the turned-up column the worst error stays pinned to
the change and grows with the bucket.

**What it costs today, and what it will cost.** At the widest current chart
window (`MAX_CHART_WINDOW_S` 300 s, `CHART_COLUMN_BUDGET_PER_SERIES` 150) the
bucket is 32 samples, so this sits at roughly 0.04 pp — four counts of the last
displayed digit. `PL-SSBP` (add the chart time-base selector with 15, 30 and 60
minute scales) widens the bucket to 64 samples and beyond, taking it to 0.08 pp
and up.

**Fix.** Force the drawn set to include every recorded control-change index.
`ControlChange.sample_index` already stores exactly those indices, and stores
them precisely because "a mark placed on the chart from a recomputed index
would drift from the sample the model actually changed at" — so the indices the
selection needs are already computed, already correct, and already read by the
same render path that draws the marks. Adding them to the selected set is a
union, not a new scan, and it strictly improves the drawn line: M4's own §4.3
error classes are about *missing* tuples, so adding tuples cannot introduce one.

Two details for whoever takes it. The count is bounded by the marks the chart
already draws, so the per-series column budget needs a stated allowance rather
than an unbounded union. And `docs/MODEL.md`'s statement of what the chart
draws has to say that the drawn set is M4 plus the control-change indices,
since it currently cites M4 alone.

**Why this is worth doing rather than accepting.** The project owner decided on
2026-09-05, under `PL-C4PH` (record the history sampling cadence as a decision
of its own), that the *chart* must reproduce a control change faithfully while
the stored record may coarsen behind it. That decision is what makes the drawn
line the guarantee, and this is the one case where the drawn line does not
currently provide it.

**Done when.** The drawn set includes every control-change index inside the
window; a test asserts that a dial change which leaves the trace monotone is
still a drawn point at every bucket width the time-base selector can produce;
and `docs/MODEL.md` states the drawn set as M4 plus those indices.

**Sequencing.** Before `PL-011` (bound the controller's concentration history),
whose retention horizon may only coarsen what the chart is guaranteed to draw
correctly. Independent of `PL-SSBP` (the chart time-base selector), which makes
it worse but does not cause it.
