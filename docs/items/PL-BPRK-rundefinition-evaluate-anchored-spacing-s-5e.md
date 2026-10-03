---
id: PL-BPRK
title: RunDefinition.evaluate_anchored(..., spacing_s=5e-324) and PlaybackRate.steps_per_tick(simulation_step_s=5e-324) raise a bare OverflowError (an int or round of infinity), outside the simulator's own exceptions, the same defect PL-YZ17 closed for SimulationState; no shipped caller reaches either
priority: P2
effort: S
status: done
classes: defect
feature: numerical-domain
touches: src/anesthesia_sim/core/run_definition.py, src/anesthesia_sim/app/playback.py, tests/unit/test_run_definition.py, tests/unit/test_playback.py, docs/MODEL.md
added: 2026-10-03
closed: 2026-10-03
pr: 1306
verify: grep -q 'def test_an_anchored_window_refuses_a_spacing_too_fine_to_count' tests/unit/test_run_definition.py && uv run pytest tests/unit/test_run_definition.py tests/unit/test_playback.py
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

**Done 2026-10-03, in #1306 at the project owner's request.**
`PlaybackRate.steps_per_tick` now checks its step with
`core.uptake_system.require_supported_simulation_step`, since the step a tick
counts in is the run's own, and refuses a step count too large to count, which
an enormous tick still produced with a supported step.
`RunDefinition.evaluate_anchored` refuses a spacing whose grid multiples up to
`stop_s` cannot be counted. It is deliberately not floored at
`MINIMUM_SIMULATION_STEP_S`: a grid chains its spacing at most once per column,
so its rounding does not accumulate, and a floor would refuse the narrow axes
the controller draws today (`PL-6QYJ`, dropped on that evidence).
`RunDefinition.evaluate` needed nothing, since it never divides by its spacing.
