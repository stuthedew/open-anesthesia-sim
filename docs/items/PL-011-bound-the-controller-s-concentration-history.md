---
id: PL-011
title: Bound the controller's concentration history
priority: P2
effort: S
status: ready
classes: perf
feature: teachable-case
touches: src/anesthesia_sim/app/controller.py
added: 2026-08-23
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
**Where.** `app/controller.py` (`_concentration_history`, `advance`).
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
rather than a summary. Note that `chart_downsampling.py` currently implements
the paper's *MinMax*, not M4 — it keeps min and max per bucket but not each
bucket's first and last.

Sizing it here: tiers of bucket width 2^t samples from t=5 upward, each bucket
holding per-quantity min and max with the sample index each occurred at, total
about n/16 buckets at ~144 B — roughly 54 MB for a week against 1.60 GB raw.

Two constraints that are correctness rather than capacity:

- `chart_downsampling.py` guarantees a drawn point is always a *recorded
  sample*, never synthesized. Min/max consolidation keeps that true only if
  each extreme carries the timestamp it actually occurred at, rather than
  being placed at a bucket boundary. Storing means instead would break the
  guarantee outright.
- `PL-Z7LY` lets the user pan back across the whole record (project owner,
  2026-09-04: scroll back through the whole run, as Gas Man does). Nothing the
  pan can reach may be discarded, so eviction applies to raw samples only once
  a tier fine enough to serve the narrowest scale has consolidated them.

**Done when.** Memory growth over a long run is bounded, or the retention
policy is documented and deliberate rather than accidental.
