---
id: PL-BPRK
title: RunDefinition.evaluate_anchored(..., spacing_s=5e-324) and PlaybackRate.steps_per_tick(simulation_step_s=5e-324) raise a bare OverflowError (an int or round of infinity), outside the simulator's own exceptions, the same defect PL-YZ17 closed for SimulationState; no shipped caller reaches either
status: untriaged
feature: numerical-domain
added: 2026-10-03
---

**Problem.** RunDefinition.evaluate_anchored(..., spacing_s=5e-324) and PlaybackRate.steps_per_tick(simulation_step_s=5e-324) raise a bare OverflowError (an int or round of infinity), outside the simulator's own exceptions, the same defect PL-YZ17 closed for SimulationState; no shipped caller reaches either

**Found 2026-10-03** by an adversarial review of `PL-YZ17` (#1306), which gave
the run's step a floor and so closed this defect for `SimulationState`. Both
calls were reproduced in a scratch script with the floor in place: each turns a
quotient by a vanishing step or spacing into an integer and raises
`OverflowError` rather than a `SimulationConfigurationError` naming the value.
Neither has a shipped caller passing such a value - the interface samples and
steps at fixed spacings well above a millisecond - so this is the hierarchy
promise, not a reachable crash. The narrow fix is a guard that refuses a
non-finite quotient by name; whether these spacings should share
`MINIMUM_SIMULATION_STEP_S` is `PL-6QYJ`'s question.
