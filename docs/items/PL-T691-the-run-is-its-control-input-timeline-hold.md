---
id: PL-T691
title: The run is its control-input timeline: hold keyframes at every event and answer any window in closed form
priority: P1
effort: L
status: done
classes: refactor, perf
feature: numerical-domain
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/core, docs/MODEL.md, docs/ARCHITECTURE.md
added: 2026-09-05
closed: 2026-09-07
verify: uv run pytest -q tests/unit tests/integration && grep -q 'def test_evaluate_matches_a_stepped_run' tests/unit/test_run_score.py
---

**Problem.** The controller records one sample per solver step, so what a run
*is* has become a growing array of measurements of itself. At the fixed 0.1 s
step that is 122 B per sample across seven series plus the elapsed-time array
— measured 2026-09-05 at 16.3 B per sample per series on the live
`M4AggregateCache`. A week is 738 MB; the owner's 30-day cap is 3.16 GB, which
`PL-011` already calls a bound in name only.

**The change.** Once `PL-GS5X` lands, the state is a closed-form function of
`(patient, agents, ordered control events, t)`. Hold that triple — the *score*
— as the run, plus one *keyframe* per control event: the six states at that
event's simulated time, computed canonically. Any value at any time is then one
propagator application from the bracketing keyframe. Nothing is recorded.

Sizing, same measurement session: a busy 30-day ICU case at 50 changes per day
is ~1 500 events, so ~70 KiB of score and ~70 KiB of keyframes against 3.16 GB
today. A 2 h teaching case is ~4 KiB.

**Re-measured on the shipped implementation, 2026-09-07**, with `tracemalloc`
rather than by counting floats: the recorded history costs 130.8 B per sample
(over 20 000 samples of a live run), so 30 days at the 0.1 s step is 25 920 000
samples and 3.16 GiB — the estimate above holds. The score of the same case,
1 501 stretches, is **1.6 MiB rather than ~140 KiB**: a stretch carries a whole
`UptakeEquationSettings`, which is a frozen dataclass holding a tuple of three
more, and Python object overhead is about 1.1 kB per stretch against the ~240 B
its floats occupy. The ratio is still about 2 000x, so the change is worth
making for exactly the reason stated; the absolute figure was an order of
magnitude optimistic and is corrected here rather than left to be discovered.

**The frame-cost figures are also worth restating**, because the prototype's
were measured on a different arrangement. On the shipped implementation a
600-column window costs 10.6 ms over 1 h of a 2 h run and 13.0 ms over 1 h of a
30-day run, which is the run-length independence the item is for. What the
prototype's 3.6 ms for a 30-day *span* does not capture is that each stretch in
view needs its own propagator: a full 30-day span at 600 columns costs 14.2 ms
with two changes in view, 231 ms with sixty, and about 1.1 s with six hundred.
That regime — more setting changes than columns — is one where sampling 600
instants aliases the run in any case, so what to draw there is a question for
`PL-2FM6` rather than a defect here.

**The control-input timeline already exists** (v0.3.7, `PL-DR1Z`), in
`app/control_timeline.py` and the controller's `ControlChange` record. It is
currently *descriptive* — an annotation drawn on the chart. This item makes it
*authoritative*: the thing the state is derived from rather than a commentary
beside it. `ROADMAP.md` planned item 8 anticipated exactly this ("held
alongside the state it describes rather than in the view") as the prerequisite
under items 9 to 12.

**Why it matters beyond memory.** Frame cost stops depending on run length.
Measured in a standard-library prototype on 2026-09-05, rendering 600 columns
from the closed form costs **3.3 ms over a 1 h window and 3.6 ms over 30 days**
— O(columns + events in view), against the 62.6 ms at 4 h and 207.7 ms at 12 h
that `PL-011` records for the rescan the M4 cache was built to replace. The
uniform spacing of chart columns is what makes it cheap: one matrix exponential
serves a whole inter-event segment, and each column is a matrix-vector apply
(4.7 us measured).

It is also what `ROADMAP.md` items 9 to 12 need. Save is serialising the score;
replay is re-evaluating it; a fork shares its parent's event prefix, which
makes item 12's "reproduce its parent's state exactly at every recorded sample"
a structural property rather than something a test has to chase.

**Out of scope.** Deleting `RunHistory` and re-pointing the chart is `PL-2FM6`.
The canonical evaluation rule and its invariant test are `PL-P1Z3`. Save/load
and export are `ROADMAP.md` items 9 and 10, which this unblocks but does not
deliver.

**Done when.** The controller holds a score and its keyframes; a public
`evaluate`-shaped entry point answers a window of `(t0, t1, n)` with exact
states; and `docs/MODEL.md` and `docs/ARCHITECTURE.md` state that a run is its
inputs and what is derived from them.

Two clauses stood here and contradicted **Out of scope** above directly: that
the entry point is *the only thing the view calls* for trace data, and that
*no test asserts on a recorded sample series*. Both describe deleting
`RunHistory` and re-pointing the chart, which **Out of scope** assigns to
`PL-2FM6`, and the `verify:` command written against them could not pass while
this item's own scope held (`PL-LLDB`). They are struck rather than reconciled:
`PL-2FM6` already carries them, and it is unblocked the moment this lands.
