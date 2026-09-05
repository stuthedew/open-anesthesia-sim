---
id: PL-011
title: Bound the controller's concentration history
priority: P2
effort: S
status: dropped
classes: perf
feature: teachable-case
touches: src/anesthesia_sim/app/controller.py
added: 2026-08-23
closed: 2026-09-05
reason: Superseded by PL-T691 and PL-2FM6. This item asks how to bound a store the score architecture removes rather than shrinks: once state is a closed-form function of the run's control-input timeline (PL-T691), the controller holds a score plus one keyframe per control event - measured 2026-09-05 at about 140 KiB for a 30-day ICU case against the 3.16 GB this item was opened to bound - and PL-2FM6 deletes RunHistory outright. The open single-precision question is moot for the same reason: halving a store that is deleted spends a decision for nothing. Its measurements are preserved in PL-T691's brief. Work exists on origin/claude/next-item-75htc6 and is deliberately not carried forward.
---

**Problem.** `SimulationController._concentration_history` appends one
sample per `advance()` and nothing ever trims it. At the fixed 0.1 s step
that is 36 000 samples per hour of simulated time, held for the life of the
session.
**Why it matters.** ~~No longer a rendering problem — PL-001 made the render
payload independent of history length~~ — **corrected 2026-09-04 by PL-Q197's
measurements.** The *payload* is independent of history length; two costs in
the per-frame path are not:

- `snapshot()` builds `concentration_history=tuple(self._concentration_history)`,
  a full copy of the run, and `_refresh_view` calls it every frame. Measured
  0.09 ms at 10 000 samples, 1.15 ms at 100 000, 5.25 ms at 500 000 — linear,
  about 10.5 us per thousand. `PL-0VM7` is that defect and the windowed read
  interface that removes it.
- Decimation rescans the visible window every frame, so cost is O(window), not
  O(points drawn). Measured per frame: 8.9 ms at a 15 min window, 15.9 ms at
  1 h, 62.6 ms at 4 h, and **207.7 ms at 12 h — more than the whole 200 ms
  frame budget**. The 12 h scale the owner now wants (see `PL-SSBP`) is
  unreachable until per-bucket extremes are computed once and kept rather than
  rederived. PL-Q197 made that possible by anchoring buckets to absolute
  sample index: a completed bucket's extremes never change again, so they are
  now cacheable, which they were not when boundaries moved every frame.
  `PL-D9WD` is that cache, agreed with the project owner 2026-09-04, and this
  item's retention policy is downstream of it — raw samples become evictable
  once a tier fine enough to serve the narrowest scale has consolidated them.

Unbounded memory growth in a long teaching session remains the original
concern, and the original note that it is "lower priority than it looks"
holds only for the durations that were in view when it was written: an hour
costs single-digit MB. The project owner has since said the allowed
simulation duration is to be *extended* past Gas Man's (2026-09-04), which is
what changes the arithmetic — see the table below.
**Where.** `app/controller.py` (`RunHistory`, `advance`).
**First step.** Decide what the history is *for* now that the chart no longer
consumes all of it. If it is the record of a run (a future export or replay
feature), it should stay complete and the fix is a documented ceiling with an
explicit failure at the limit rather than silent trimming.
**Owner input (2026-08-25).** Scenario run time will be capped rather than
unlimited - 30 days as the working figure, revisable upward later. That
settles the ceiling but not this item: at the fixed 0.1 s step, 30 days is
25 920 000 samples, and a `SimulationHistorySample` measures 88 B as an
object plus its floats (~256 B worst case, ~88 B if the floats are shared),
so the cap bounds retention at roughly 2.3-6.6 GB. That is a bound in name
only. The retention policy still has to be decided on its own terms, and the
run-time cap should be enforced as an explicit halt with a stated reason
rather than left implicit.

**Now also feeds** the scenario-branching work (PL-WRKL, PL-RRWV): what the
history retains determines which past points a run can be branched from
exactly, so decide the retention policy before, not after, that design.

**Measured cost of the current policy (2026-09-04).** `advance()` runs at
19 us per step and a `SimulationHistorySample` is about 264 B including its
float objects. `core.uptake_system.MAXIMUM_SIMULATION_STEP_S` is 0.1 s and
`advance()` *raises* above it, so the step count is fixed by the operator
split's applicability domain and cannot be reduced by taking coarser steps.

| Simulated | Steps | History RAM | Compute to reach it |
| ---: | ---: | ---: | ---: |
| 1 hour | 36 000 | 0.01 GB | 1 s |
| 12 hours | 432 000 | 0.11 GB | 8 s |
| 1 day | 864 000 | 0.23 GB | 16 s |
| 1 week | 6 048 000 | 1.60 GB | 115 s |

So compute is not the obstacle and memory is — and the owner's stated 30-day
cap bounds it at roughly 6.6 GB, which is a bound in name only, as the note
above already says.

**The established answer, for when this is worked.** Multi-resolution
retention: recent data at full resolution, older data progressively
consolidated, with consolidation preserving *extremes* rather than averaging
them away. RRDtool has done this since 1999 (round-robin archives with
min/max/average/last consolidation, fixed total storage regardless of run
length) — *cited from general knowledge; verify against its documentation
before relying on the detail*. OM3 (Proc. ACM Management of Data, SIGMOD 2023)
is the current academic form. M4 (Jugel et al., PVLDB 7(10):797-808, 2014) is
the matching read rule; `PL-D9WD` carries it, read from the paper itself
rather than a summary.

**The consolidation half of that answer has landed, and it moved these
numbers the other way (`PL-D9WD`, 2026-09-04).** The predicted sizing above
was tiers of bucket width 2^t from t=5 upward at about n/16 buckets, kept
*alongside* the raw record. What shipped keeps those tiers - four M4 tuples
per bucket rather than two extremes - but stores the run itself by quantity
as arrays of doubles rather than as a list of frozen dataclasses, and the
second change is much the larger of the two. Measured over 200 000 samples:
**127 B per sample including the ladders, against 264 B for the list of rows
it replaced**. So halve every figure in the table above, and the owner's
30-day cap now bounds retention at roughly 3.3 GB rather than 6.6.

That is still a bound in name only and this item is still open: the store
grows without limit, and what remains is the *eviction* rule - which raw
samples may be dropped once a tier fine enough to serve the narrowest scale
has consolidated them, and what the interface says when it happens.

Two constraints that are correctness rather than capacity:

- `chart_downsampling.py` guarantees a drawn point is always a *recorded
  sample*, never synthesized. Consolidation keeps that true only if each
  extreme carries the timestamp it actually occurred at, rather than being
  placed at a bucket boundary — which is why `M4Aggregate` stores four sample
  *indices*. Storing means instead would break the guarantee outright.
- `PL-Z7LY` lets the user pan back across the whole record (project owner,
  2026-09-04: scroll back through the whole run, as Gas Man does). Nothing the
  pan can reach may be discarded, so eviction applies to raw samples only once
  a tier fine enough to serve the narrowest scale has consolidated them.

**Done when.** Memory growth over a long run is bounded, or the retention
policy is documented and deliberate rather than accidental.

**Blocked on `PL-W3DD` (2026-09-04, project owner, deciding `PL-5WFS`).**
Sequencing only: nothing here is wrong today, and this item's own band and
class are unchanged. `PL-W3DD` re-keys `SimulationHistorySample` by substance,
and the cap above is sized against the record it replaces — "a slotted
dataclass of seven floats", and the 2.3-6.6 GB that number bounds. A
per-substance mapping carries a dict or a nested structure per sample, so both
figures stop describing the record they are about. Land `PL-W3DD` first and
measure the cap against the shape that ships.

`PL-THVN` carries the diagnosis. The dependency was invisible to the ranking
before this edit: `bin/docket next` offered this item 3rd and `PL-W3DD` 9th,
both `P2`, because the ranking reads front matter and the dependency was
stated only in a third item's prose.

**Decision needed.** What is the recorded run *for*, now that the chart reads
aggregates rather than samples? If it is the record of a run - the thing a
future export, replay or fork reproduces - it stays complete and the answer is
a documented ceiling with an explicit failure at it, never silent truncation.
If it exists only to be drawn, raw samples become evictable once an aggregate
tier fine enough for the narrowest time base has consolidated them, and the
answer is that eviction policy. The two give different code and different
guarantees, and `PL-SSBP`'s upper time bases wait on whichever it is.

**Unblocked 2026-09-05 by `PL-W3DD` closing**, and moved to `needs-decision`
rather than to `ready`: its "First step" above is a question - what the
history is *for* now that the chart no longer consumes all of it - and
answering that is the work, not a field to fill in. `PL-8GLL` is the
measurement it needs first: the per-sample figure the table below is read off
describes a per-step history `PL-D9WD` replaced, so the arithmetic that
decides whether a ceiling is needed at all rests on a superseded number.

**Measured 2026-09-05, against the shape that shipped, and it moves the
decision.** `PL-8GLL`'s measurement, run before answering this item because
every figure above was read off a per-sample cost that `PL-D9WD` superseded.
`tracemalloc` over a recorded run, marginal between 100 000 and 200 000 samples
so the fixed overhead is out of it; one substance, seven series:

| What is retained | Bytes per sample |
| --- | ---: |
| Elapsed array + 7 series' `array("d")` of values | 64.0 |
| The dyadic M4 aggregate ladder over them | 63.9 |
| **Total** | **127.9** |

This confirms `PL-D9WD`'s 127 B and retires the 88 B and 264 B figures. The
table above is therefore right as corrected, and the 30-day cap bounds
retention at 3.3 GB.

**The half that changes the answer: eviction is a factor of two, not a bound.**
This item's framing - "raw samples become evictable once an aggregate tier fine
enough to serve the narrowest scale has consolidated them" - was written when
the raw record was assumed to be the whole cost. It is half of it. The ladder
holds about `n/16` `M4Aggregate` objects per series and grows linearly in the
run exactly as the samples do, so evicting every raw sample takes 30 days from
3.3 GB to 1.66 GB and leaves the growth linear. Whichever way this item is
decided, "evict the raw samples" does not on its own satisfy **Done when**'s
first disjunct.

**What the narrowest scale actually needs, checked rather than assumed.**
`chart_time_base.py`'s `SELECTABLE_TIME_BASE_FLOOR_S` is 900 s and
`chart_series.py`'s `CHART_COLUMN_BUDGET_PER_SERIES` is 150, so the narrowest
selectable window is 9 000 samples across 150 columns - **60 samples per
column, against a `FINEST_CACHED_BUCKET_SAMPLES` of 32**. The finest tier
already spans less than a column at the narrowest window the selector offers,
so eviction would not break that window; it would cost the ragged ends of each
column's range, which `M4AggregateCache.aggregate` reads raw. The rungs below
900 s are reachable only by "Fit run", and a fitted window is at least as wide
as the run, so no *long* run is ever drawn at them. Eviction is therefore
feasible - it is simply not where the memory is.

**What the recorded run is for, answered from the code.** The trajectory-
determining state is not in the history and does not need to be:
`AgentUptakeSystem.capture_state()` already returns an `AgentUptakeSystemState`
- the six concentrations plus the validator's three accounting totals - and
`restore_state()` puts it back, so a fork is served by one ~88 B snapshot at the
fork point rather than by retaining every sample. `docs/WORKING_NOTES.md`'s
branching thread measured both axes and reached the same place: a snapshot is
nearly free, and resimulation is nearly free (re-measured 2026-09-05 at 18.4 us
per step - 2.0 s to rebuild a 3-hour run from t=0, 15.9 s for a day). What
neither a fork nor a replay can be built from today is the *control timeline*,
which nothing records; that is `PL-WRKL`, `ROADMAP.md` item 8. So the record of
a run is its initial conditions plus its control timeline, and the sample
history is a rendering cache over a computation that is cheap and deterministic
to redo.

**Recommended answer, put to the project owner 2026-09-05.** Cap the run and
halt explicitly, and do not build eviction at this milestone. A cap satisfies
both disjuncts of **Done when** at `S`: growth is bounded and the policy is
deliberate. Eviction buys 2x and does not bound; a real bound needs the ladder
coarsened as well, which is `M`/`L` and should follow `PL-Z7LY` (pan back
across the whole run) and `PL-SSBP` (the upper time bases), since those decide
what resolution old data has to serve. The 30-day working figure does not
survive the measurement - 3.3 GB is not a bound a teaching machine can honour -
and the rate that makes this reachable by accident is **1.38 GB per wall-clock
hour at the 300x maximum playback rate**, not the 30-day run nobody sits
through. 48 h costs 221 MB, 24 h costs 110 MB, 7 days costs 774 MB.
