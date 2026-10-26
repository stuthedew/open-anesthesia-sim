---
id: PL-T6P0
title: PlaybackRate.steps_per_tick refuses only a step count that cannot be counted, so an enormous finite tick interval returns a step count of about 1e305 and the run loop would step for ever instead of refusing
status: untriaged
classes: defect
feature: floating-point-domain
touches: src/anesthesia_sim/app/playback.py, tests/unit
deferred-from: v0.7.0 - filed 2026-10-25 while fixing PL-06LS, after this gate froze; the gate defers its sibling PL-06LS for the same reason, so the generator tier ranks it, not the gate
added: 2026-10-25
---

**Problem.** `PlaybackRate.steps_per_tick` refuses a step count only when it cannot be counted at all. A large but finite count is returned as it is. The run loop then takes that many steps in one tick, so it would step for ever instead of refusing.

**Where it is.** `src/anesthesia_sim/app/playback.py`, `PlaybackRate.steps_per_tick`. It checks `math.isfinite(exact)` (`PL-YZ17`) and that `exact` is close to a whole number, and nothing else. Measured on 2026-10-25: the 300x rate with a tick interval of 1e300 s and a 1 ms step returns 3.000e+305 steps. No shipped caller is known to pass such a tick interval. The run loop's own tick is a fixed constant. This was found while fixing `PL-06LS`, which bounded the same shape in `RunDefinition.evaluate_anchored`.

**What to do.** State the most steps one tick may take, as a named constant, and refuse a count past it with a `SimulationConfigurationError`. `PL-06LS`'s `MAXIMUM_WINDOW_COLUMNS` in `core/run_definition.py` is the pattern. Choose the bound from the fastest supported rate, the slowest tick the app uses and the smallest supported step, with margin.

**Why it matters.** A call that never returns is a hang with no error, so the caller never learns why.

**Done when.** `steps_per_tick` refuses a count past the stated bound, and a test drives it one past the bound and at the bound.
