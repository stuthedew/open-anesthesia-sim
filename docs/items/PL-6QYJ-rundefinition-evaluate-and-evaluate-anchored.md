---
id: PL-6QYJ
title: RunDefinition.evaluate and evaluate_anchored chain one exact propagator over any positive sample spacing, with no floor, so at a 1e-12 s spacing the drawn change is about 9e-3 wrong (measured 2026-10-03), the regime MINIMUM_SIMULATION_STEP_S refuses for a run's step; whether the chart can reach such a spacing is unchecked
priority: P3
effort: S
status: dropped
classes: defect
feature: numerical-domain
touches: src/anesthesia_sim/core/run_definition.py
added: 2026-10-03
closed: 2026-10-03
reason: the premise overstated it: a grid chains its spacing at most once per column, so drawn values stay accurate at any spacing (a grid at a tenth of the 1 ms floor lands within 5e-14 of state_at, test_an_anchored_window_draws_a_spacing_finer_than_the_smallest_step_exactly); only the change across a sub-nanosecond window was wrong, which nothing draws. Flooring the spacing would refuse narrow axes the controller draws today (test_the_window_starts_at_the_time_asked_for_and_never_after_it draws 0.1 s at 150 columns)
---

**Problem.** RunDefinition.evaluate and evaluate_anchored chain one exact propagator over any positive sample spacing, with no floor, so at a 1e-12 s spacing the drawn change is about 9e-3 wrong (measured 2026-10-03), the regime MINIMUM_SIMULATION_STEP_S refuses for a run's step; whether the chart can reach such a spacing is unchecked

**Found 2026-10-03** by an adversarial review of `PL-YZ17` (#1306). The chart
evaluates a run by chaining one exact propagator over the sample spacing, so
the rounding `PL-YZ17` measured for a run's step applies to the spacing too:
at 1e-12 s the change drawn is about 9e-3 wrong, measured with the run's floor
in place. `MINIMUM_SIMULATION_STEP_S` binds only `AgentUptakeSystem.advance()`
and `SimulationState`, so nothing refuses such a spacing. First question, and
cheap: what is the smallest spacing the chart can actually ask for - the
narrowest window over the most columns, and the hover resolution
(`HOVER_INSTANT_RESOLUTION_S` is the ceiling, 0.1 s). If that is far above
1 ms, the answer may be a guard rather than a redesign. Sits with `PL-WP52`
and `PL-BPRK`: three entry points that take a positive interval with no floor.
