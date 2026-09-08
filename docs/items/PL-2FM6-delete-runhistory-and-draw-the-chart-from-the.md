---
id: PL-2FM6
title: Delete RunHistory and draw the chart from the closed-form sampler instead of from recorded samples
priority: P2
effort: M
status: done
classes: refactor, perf
feature: numerical-domain
touches: src/anesthesia_sim/core/run_score.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/chart_series.py, src/anesthesia_sim/app/simulation_view.py, tests/unit, tests/integration, docs/MODEL.md
added: 2026-09-05
closed: 2026-09-08
pr: 488
verify: uv run pytest -q tests/unit tests/integration && ! grep -rq 'history_window\|RunHistory' src/anesthesia_sim/ && grep -qF 'the drawn chart reproduces every control change' docs/MODEL.md
---

**Problem.** With `PL-T691` landed, `RunHistory`, `history_window`,
`RecordedSeries` and the windowing machinery in `app/controller.py` answer a
question nothing asks any more: which recorded samples does this window draw.
Left in place they are a second, divergent source of truth for the same
trace — the failure mode `CLAUDE.md`'s stale-state rule treats as a safety
issue, not tidiness.

**The change.** `chart_series.redraw_visible_window` asks the sampler for
`(t0, t1, n_columns)` and receives exact values, rather than asking the
controller for a window over recorded samples and decimating it. Column count
stays what `CHART_COLUMN_BUDGET_PER_SERIES` already sets; the point-reuse
optimisation in `redraw_points` (`PL-010`, 6 us to build against 0.8 us to
move) is unaffected and should be kept.

Two things the sampler must do that a recorded window did not:

1. **Place a column at every control event inside the window.** Between events
   the trajectory is a sum of exponentials with bounded curvature and no hidden
   transients; every sharp feature is at an event boundary. Sampling the event
   times explicitly is what makes the drawn curve exact rather than merely
   dense — and it is where the reference implementation fails: the Gas Man
   manual (p.192) records that flush spikes "occur between interpolation points
   on the graph … especially with relatively large-duration views".
2. **Keep the wash-in ratio's undefined stretches.** `app/wash_in.py`'s domain
   rules currently run once per recorded sample; they become a property of the
   evaluated column instead. `PL-4RBD` (the drawn chart smooths through a
   control change) is closely related and may close with this.

**A property the current design buys that this one must not lose (found
2026-09-05, reviewing which decisions the change makes moot).** `PL-Q197`
anchored decimation to the *run* rather than to the viewport, and the payoff it
bought was that a steady frame moves only the newest bucket and the final
sample — 2 700 discrete control mutations a frame was what saturated the
Flutter client, and that anchoring is what fixed it.

Evaluating the closed form at pixel columns throws that away by default: while
the window follows the run, every column is a new instant every frame, so
*every* point moves and the mutation count goes back up. The fix is the same
trick applied one level over — anchor the **evaluation times** to an absolute
grid measured from `t = 0`, at the column spacing the time base implies, so a
following window reuses all but its newest column times. Event columns are
added on top of that grid rather than replacing it.

This is a requirement of this item, not a later optimisation: without it the
architecture regresses a defect that was already measured and fixed, and it
would regress it in the one place the reader is looking. `PL-YDKJ` (decide
whether the chart should keep patching one control per plotted point) is the
open decision this interacts with, and it should be decided after this lands
rather than before — the point-movement rate is its main input, and this item
changes it.

**Why it matters.** This is where the memory actually comes back and where the
frame cost actually drops — `PL-T691` makes it possible, this makes it real.
It also removes the last consumer of `chart_downsampling`, which is `PL-8LXM`.

**Supersedes.** `PL-011` (bound the controller's concentration history) and
`PL-XNHJ` (`RunHistory` stores an elapsed time per sample that is an affine
function of the sample index) both become moot: there is no history to bound
and no per-sample time to store. Close them against this item rather than
working them. `PL-1PSX` (the control-input timeline is unbounded and regrouped
in full on every frame) survives but changes character — the timeline is now
the run, so its bound is a bound on the score itself.

**The chart-fidelity requirement, transplanted from `PL-C4PH` (project owner,
2026-09-05; moved here 2026-09-08 when that item was dropped).** The decision
is **chart-faithful only**: *the drawn chart* must reproduce a control change to
the last displayed digit; *the stored record* need not. It was recorded nowhere
but in `PL-C4PH`'s brief, and `PL-C4PH` was opened to describe a recorded-sample
cadence this item deletes - so the requirement is restated here, as a property of
the drawn chart rather than of a store, and it outlives both mechanisms.

Why it binds *this* item specifically: the measurements under `PL-C4PH` (dropped,
file retained, table preserved there) found the worst interpolation error at every
cadence sits at `t` = the instant the dial moves, scaling as O(h) rather than
O(h^2) - the signature of a kink, since the derivative of the circuit fraction is
discontinuous at a control change. Away from one the trajectory is faithful to
about 1e-3 pp even at a 2 s cadence, a tenth of the display resolution. So the
fidelity question is entirely a question about control events, which is exactly
what this item's "a control event inside the visible window always gets its own
column" answers - and after this lands the drawn line is the *whole* guarantee,
because there is no stored record behind it to appeal to.

`PL-4RBD` (the drawn chart smooths through a control change that leaves the trace
monotone) is the live defect against this requirement in the M4 path, and is
deliberately kept rather than dropped with `PL-C4PH`: it ships today, and its test
is written against the drawn set so this item inherits it.

**"To the last displayed digit" is deliberately coupled to display resolution
(project owner, 2026-09-08), and that does not cross the line `docs/MODEL.md`
draws.** The question raised was whether pinning the guarantee to the readout
means a later precision change moves it. It does, and that is correct here.
`docs/MODEL.md` § "Supported simulation step" forbids the traffic in the *other*
direction - "the readout's decimal count is a presentation decision (§ 'Displayed
precision') and must not reach back into the model" - which is why the step
tolerance and the supported ranges are stated in absolute percentage points
rather than in counts of the readout. This requirement is a statement about the
*chart*, expressed in the units a reader actually reads it in, so it is the
permitted direction rather than the forbidden one. Nor is the peg arbitrary: the
two-decimal readout is itself derived from model fidelity (§ "Displayed
precision"), one published SD of a partition coefficient displacing a compartment
by 8.7e-4 to 6.8e-2 pp. An absolute tolerance was considered and refused: it
would invent a number nobody measured, where this one inherits a derivation.

**Done when.** `RunHistory` and `history_window` are gone; the chart is drawn
from evaluated columns; a control event inside the visible window always gets
its own column; `docs/MODEL.md` states, in those words, that **the drawn chart
reproduces every control change** to the last displayed digit while the stored
record need not; and `tests/unit/test_run_history.py` is deleted rather than
adapted.

**Closed 2026-09-08.** `RunHistory`, `HistoryWindow`, `SimulationHistorySample`,
`history_window` and `evaluate_window` are gone; the chart evaluates
`RunScore.evaluate_anchored` over the axis it has just set. Both requirements
the brief singled out are met and tested: a control event inside the window
always gets its own column, at every rung of the time-base ladder, and it is
read from the keyframe the score already holds rather than propagated, so it
is exact rather than merely placed; and the evaluation times are anchored to
multiples of the spacing measured from `t = 0`, so a following window keeps
every interior column and moves only its right-hand edge - `PL-Q197`'s
property, preserved by test rather than by intention.

**One deliberate departure from the brief.** It listed `RecordedSeries` among
the machinery to delete. It is kept: it is what binds a trace to one
substance-and-quantity pair, which is the pairing `PlottedSeries` exists to
make auditable, and deleting it would remove a presentation-safety guard
rather than a storage concern. `RecordedQuantity` is kept with it, and both
now address a drawn window rather than a store.

**Two things the brief did not anticipate.** The sampler needed an evaluation
shape of its own - `evaluate` spaces columns across whichever bounds it is
given, which moves every drawn point on every frame - so `core/run_score.py`
is in `touches` and `evaluate_anchored` is where most of the design went. And
`ControlChange.sample_index` indexed a store that no longer exists; its only
job was folding two changes to one control inside a single step into one act,
which `elapsed_s` does directly, so the field and
`ControlAdjustment.sample_index` are gone.

**Measured.** A propagator costs about 1.29 ms against 6.2 us for a chained
product, so taking each column from its own keyframe would be 193 ms for 150
columns against a 200 ms frame; the grid therefore stays uniform within a
segment. A 12 h window at 150 columns over four segments evaluates in 15.4 ms,
and the worst departure from the canonical path is 3.3e-10 pp - seven orders
below the 0.01 pp the readout resolves. Cost still scales with segments in
view, which is `PL-1PSX` rather than anything new here.
