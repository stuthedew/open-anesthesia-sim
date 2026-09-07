---
id: PL-2FM6
title: Delete RunHistory and draw the chart from the closed-form sampler instead of from recorded samples
priority: P2
effort: M
status: ready
classes: refactor, perf
feature: numerical-domain
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/chart_series.py, src/anesthesia_sim/app/simulation_view.py, tests/unit, tests/integration
added: 2026-09-05
verify: uv run pytest -q tests/unit tests/integration && ! grep -rq 'history_window\|RunHistory' src/anesthesia_sim/
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

**Done when.** `RunHistory` and `history_window` are gone; the chart is drawn
from evaluated columns; a control event inside the visible window always gets
its own column; and `tests/unit/test_run_history.py` is deleted rather than
adapted.
