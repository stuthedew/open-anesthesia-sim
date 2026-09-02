---
id: PL-VM40
title: Derive simulated time from a step count and never catch up to the wall clock
priority: P1
effort: M
status: blocked
classes: safety, science
feature: teachable-case
touches: src/anesthesia_sim/core/simulation.py, src/anesthesia_sim/app/simulation_view.py, docs/MODEL.md, tests/unit/test_simulation.py
added: 2026-08-25
blocked-by: PL-WB0X
---
**Problem.** Two separate things make a run irreproducible. `SimulationState.advance`
accumulates `self.elapsed_s += simulation_step_s` per step, so the clock depends on
the order and count of the additions that reached it rather than on how far the
simulation has gone. And the run loop in `app/simulation_view.py` sleeps
`SIMULATION_STEP_S` and takes one step, so the number of steps a run takes is set by
how promptly the event loop wakes - which is a property of the machine, not of the
model.

**Why it matters.** Neither is visible today: the accumulated float error over a
four-hour run is on the order of nanoseconds, far below anything displayed, and at
1x the loop is close enough to real time that nobody notices a dropped tick. Both
become load-bearing the moment a run is compared to another run. Planned-milestone
item 12 (forking) requires that a branch taken at time t reproduce its parent
element-wise at every recorded sample up to t, and names exactly these two causes -
accumulation order for `elapsed_s`, and a different number of steps per frame - as
the divergences that would destroy it. The playback multiplier (PL-SN2C) makes the
second one worse in proportion to the rate. Retrofitting this after runs have been
recorded and compared is expensive; doing it before is small.

**Where.** `core/simulation.py` (`elapsed_s`, `advance`, `reset`),
`app/simulation_view.py` (`SIMULATION_STEP_S` and the run loop around line 943),
`docs/MODEL.md` § "Time" and § "Interface boundary".

**Approach.** Hold an integer `step_count` and derive `elapsed_s` as
`step_count * simulation_step_s`. Keep the step fixed at 0.1 s. The run loop
advances a fixed number of steps per tick and never takes extra steps to make up
lost wall-clock time: a slow machine runs slower, it does not run differently. Say
this in `docs/MODEL.md` as a guarantee rather than leaving it as an implementation
detail, since it is what a later forking claim rests on.

**Done when.** Simulated time is an exact function of the number of steps taken;
two runs given identical inputs produce element-wise identical recorded history
regardless of machine speed or how the ticks fell, asserted by test; and
`docs/MODEL.md` states the reproducibility guarantee and what it does and does not
cover.

**Blocked on `PL-WB0X` (2026-09-02, project owner).** Not a stated
prerequisite in this brief - it is file contention that `bin/docket concurrent
PL-WB0X` reports and nothing else would have surfaced. `PL-WB0X` moves the
formatters and the chart-series assembly out of `simulation_view.py` into
`app/formatting.py`, and this item edits both in their current location. Doing
it first means doing that part of it twice, and the second time inside a file
that has since moved.

The block is sequencing only: nothing here is wrong today, and the band stands
on this item's own classes rather than on the blocker's.
