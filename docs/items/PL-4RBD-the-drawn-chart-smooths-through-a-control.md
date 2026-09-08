---
id: PL-4RBD
title: The drawn chart smooths through a control change that leaves the trace monotone, because M4 selects extremes and such a change is not one
priority: P1
effort: S
status: done
classes: defect, ux, safety
feature: teachable-case
milestone: v0.4.12
touches: src/anesthesia_sim/app/chart_downsampling.py, src/anesthesia_sim/app/chart_series.py, docs/MODEL.md
added: 2026-09-05
closed: 2026-09-08
pr: 488
verify: uv run pytest tests/integration/test_controller.py && grep -q 'def test_a_control_change_is_drawn_at_every_time_base_the_reader_can_select' tests/integration/test_controller.py
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

**Why it matters: what it costs today, and what it will cost.** At the chart
window this item was written against (`MAX_CHART_WINDOW_S` 300 s,
`CHART_COLUMN_BUDGET_PER_SERIES` 150) the bucket is 32 samples, so this sits at
roughly 0.04 pp — four counts of the last displayed digit. `PL-SSBP` (add the
chart time-base selector) was named here as what would widen the bucket to 64
samples and beyond, taking it to 0.08 pp and up.

**That premise is already stale (triage, 2026-09-05).** `PL-SSBP` is `done`, and
`MAX_CHART_WINDOW_S` is no longer in the tree at all — no `.py` or `.md` outside
this item mentions it. `chart_time_base.TIME_BASE_LADDER` tops out at
`span_s=43200.0`, so a reader can select a **12-hour** base, and "Fit run" is
explicitly not capped there. At `CHART_COLUMN_BUDGET_PER_SERIES` 150 and the
shipped 10 Hz recording, a 12-hour base is a **2 880-sample bucket** — forty-five
times the widest row the table above measures, and "Fit run" on a long case is
wider still. So the "what it will cost" column is what ships today, and the
0.04 pp this item is banded on was taken at a window the interface no longer
has.

**Re-measure before sizing, and re-band if the measurement says so.** Extend the
measured table to the shipped bases (900 s through 43 200 s, and a fitted
multi-hour run) as the first step of the work. The `P2`/`defect, ux` triage below
rests on the 0.04 pp figure: an error of four counts of the last displayed digit,
in one bucket, is a fidelity defect and not a clinician being misled, which is
what this store's top band means. If the error at a 12-hour base or at "Fit run"
is instead a readable fraction of a MAC, that reasoning does not survive and the
item wants `safety` and `P1`. That is a measurement rather than a judgement, so
it belongs to whoever starts this and not to a triage pass.

**Re-measured 2026-09-08, and the banding does not survive it.** The table
above was taken at `MAX_CHART_WINDOW_S` 300 s, a constant no longer in the
tree. Re-run against the shipped `chart_time_base.TIME_BASE_LADDER`, through
`M4AggregateCache.select_indices` itself rather than a model of it, on a real
12 h run at the envelope corner (FGF 10, V_A 12, Q 10), sevoflurane 2% -> 4%
at t = 600 s, `CHART_COLUMN_BUDGET_PER_SERIES` 150:

| Time base | Bucket | Alveolar | as MAC | Circuit |
| --- | ---: | ---: | ---: | ---: |
| 15 min | 64 | 0.0124 pp | 0.006 | 0.0607 pp |
| 1 h | 256 | 0.1005 pp | 0.049 | 0.2467 pp |
| 4 h | 1024 | 0.2145 pp | 0.105 | 0.4925 pp |
| 8 h | 2048 | 0.4216 pp | 0.206 | 0.7627 pp |
| 12 h | 4096 | 0.6467 pp | **0.315** | 1.0027 pp |

MAC taken as 2.05% for a 40-year-old (Nickalls RWD, Mapleson WW, "Age-related
iso-MAC charts for isoflurane, sevoflurane and desflurane in man", Br J
Anaesth 2003;91(2):170-4).

**Two corrections to the brief above.** The bucket at a 12 h base is **4 096
samples**, not the 2 880 estimated: `_stable_bucket_width` climbs a
power-of-two ladder rather than fitting the window exactly. And "Fit run" is
uncapped — `chart_time_base` doubles past the ladder's last rung — so a case
longer than 12 h is drawn at a wider bucket than any row here.

**So the `P2`/`defect, ux` triage is withdrawn.** The item's own instruction
was that "if the error at a 12-hour base or at 'Fit run' is instead a readable
fraction of a MAC, that reasoning does not survive and the item wants `safety`
and `P1`". At the 12 h base the alveolar trace — the MAC-bearing one — departs
from the recorded trajectory by **0.32 MAC**, drawn with no indication that
anything between the plotted points was inferred. Re-banded `P1`, `safety`.

**And the fix in this brief is now the smaller half of the problem.** Unioning
the control-change indices into the selection pins the kink, which is the
component this item was written about. It does not touch the rest: most of the
0.65 pp above is ordinary curvature drawn as a chord across a 4 096-sample
bucket, and no selection of *recorded extremes* can fix that, because the
samples that would carry the shape are the ones the budget excludes.
`PL-2FM6` does fix it, structurally — an evaluated column is a point on the
trajectory rather than a selected extreme — which is why the sequencing note
below now decides this item rather than merely dating it.

**The shelf-life argument below is stale, for the second time.** It rests on
"two `L` items and an `M` stand between here and there". `PL-GS5X` and
`PL-T691` are both `done`; only `PL-2FM6` (`M`, `ready`) remains.

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

**Sequencing.** As captured this read "before `PL-011` (bound the controller's
concentration history)"; `PL-011` is now `dropped`, superseded by the score
architecture, so that edge is gone. `PL-SSBP` (the chart time-base selector) is
`done` and made this worse without causing it.

**This has a shelf life, and it is not short (triage, 2026-09-05).** The chain
that removes the defect structurally is `PL-GS5X` (replace the operator split
with the exact matrix exponential, `L`) -> `PL-T691` (the run is its
control-input timeline, `L`) -> `PL-2FM6` (delete `RunHistory` and draw the chart
from the closed-form sampler, `M`), whose own **Done when** already requires that
"a control event inside the visible window always gets its own column" — this
item's guarantee, delivered by evaluating columns instead of by unioning indices
into an M4 selection. `PL-8LXM` then deletes `chart_downsampling.py` outright.
Two `L` items and an `M` stand between here and there, and the drawn line is the
whole fidelity guarantee in the meantime (see `PL-C4PH`), so the `S` fix is worth
taking now. The **test** is the part that survives: write it against the drawn
set rather than against `chart_downsampling`'s internals, so `PL-2FM6` inherits
it as a behavioural requirement instead of deleting it with the module.

**Closed 2026-09-08 by `PL-2FM6`, structurally rather than by the fix above.**
The brief's own sequencing note anticipated this: `PL-2FM6`'s **Done when**
already required that "a control event inside the visible window always gets
its own column", which is this item's guarantee delivered by evaluating
columns instead of by unioning indices into a selection.

Taking the structural route rather than the `S` fix was the project owner's
call, on the re-measurement recorded above. The `S` fix pins the kink and
nothing else, and most of the 0.65 pp measured at the 12 h base is ordinary
curvature drawn as a chord across a 4 096-sample bucket - which no selection
of *recorded extremes* can reach, because the samples carrying the shape are
the ones the column budget excludes. An evaluated column is a point on the
trajectory, so both halves go together.

**The `verify:` command was re-pointed while this item was open**, from
`tests/unit/test_chart_downsampling.py` - a file `PL-8LXM` deletes - to
`test_a_control_change_is_drawn_at_every_time_base_the_reader_can_select` in
`tests/integration/test_controller.py`. That test walks the whole
`TIME_BASE_LADDER` rather than the three bucket widths the original table
measured, which is what the brief asked for: the event is a column because it
is an event, not because a spacing happened to land on it.
