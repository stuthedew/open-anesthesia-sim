---
id: PL-011
title: Bound the controller's concentration history
priority: P2
effort: S
status: ready
classes: perf
feature: chart-readout
touches: src/anesthesia_sim/app/controller.py
added: 2026-08-23
---

**Problem.** `SimulationController._concentration_history` appends one
sample per `advance()` and nothing ever trims it. At the fixed 0.1 s step
that is 36 000 samples per hour of simulated time, held for the life of the
session.
**Why it matters.** No longer a rendering problem — PL-001 made the render
payload independent of history length — but still unbounded memory growth in
a long teaching session. Lower priority than it looks: a slotted dataclass of
seven floats is on the order of a few hundred bytes, so an hour costs single-
digit MB.
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

**Done when.** Memory growth over a long run is bounded, or the retention
policy is documented and deliberate rather than accidental.
