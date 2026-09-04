---
id: PL-VM40
title: Derive simulated time from a step count and never catch up to the wall clock
priority: P1
effort: M
status: done
classes: safety, science
feature: teachable-case
touches: src/anesthesia_sim/core/simulation.py, src/anesthesia_sim/app/simulation_view.py, docs/MODEL.md, ROADMAP.md, tests/unit/test_simulation.py, tests/unit/test_simulation_view.py, tests/integration/test_sevo_controller.py
added: 2026-08-25
closed: 2026-09-04
verify: uv run pytest tests/unit/test_simulation.py && grep -q 'def test_elapsed_time_is_the_step_count_times_the_step' tests/unit/test_simulation.py
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

**Block cleared 2026-09-03.** `PL-WB0X` merged as `#263`, so the formatters
and the chart-series assembly are already in `app/formatting.py` and
`app/chart_series.py`. The paragraph above is kept as the record of why this
waited; it no longer holds. Recovered from `origin/claude/what-next-rsmqeu`,
which was abandoned without a pull request.

**Landed 2026-09-04.** `SimulationState` holds `step_count` and the
`simulation_step_s` the run is being taken at, and reports `elapsed_s` as
their product; `reset()` clears both.

Two decisions inside the approach, neither of which the brief settles:

- **The step is fixed per run rather than hard-coded at 0.1 s.** `advance()`
  records the step the run's first step was taken at and refuses a different
  one thereafter, as a `SimulationConfigurationError` raised before anything
  moves. That gives the product a single step to multiply by without moving
  the cadence decision out of `app/simulation_view.py`, where a comment
  derives it from the operator split's applicability domain, and without
  rewriting the ~50 `controller.advance(0.1)` call sites in the test suite. A
  step-refinement study can still take a whole run at a smaller step.
- **The run loop is unchanged, and gains no `STEPS_PER_TICK` constant.** One
  step per tick already *is* a fixed number of steps per tick, and nothing
  consumes a constant today; the guarantee is stated in the loop's docstring
  and locked by a test that drives it through a tick returning at once, so
  the assertion is "one step per wakeup" with no real time in it. `PL-SN2C`,
  the playback multiplier, is where a steps-per-tick constant belongs -
  v0.4.0's Required scope already says that item is implemented as steps per
  tick and never as a larger step.

`docs/MODEL.md` gained "Simulated time is a count of steps, not a running
total" and "The reproducibility guarantee" under § "Time", the second stating
the four things the guarantee does *not* cover: a different step size, a
different model version, a different platform (the compartments' analytic
solutions call `exp`, whose last bit is a library's), and elapsed real time.
"Deterministic replay test" now requires the comparison to be element-wise
and the two runs to be driven differently in real time; `ROADMAP.md`'s
forking entry no longer names the two divergence causes this closes.
