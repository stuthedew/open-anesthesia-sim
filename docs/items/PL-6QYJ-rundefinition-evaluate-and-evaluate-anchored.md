---
id: PL-6QYJ
title: RunDefinition.evaluate and evaluate_anchored chain one exact propagator over any positive sample spacing, with no floor, so at a 1e-12 s spacing the drawn change is about 9e-3 wrong (measured 2026-10-03), the regime MINIMUM_SIMULATION_STEP_S refuses for a run's step; whether the chart can reach such a spacing is unchecked
status: untriaged
feature: numerical-domain
added: 2026-10-03
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
