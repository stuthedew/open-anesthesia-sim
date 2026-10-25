---
id: PL-06LS
title: RunDefinition.evaluate_anchored loops once per sample with only stop_s / spacing_s being finite to bound it, so a spacing of 1e-300 s hangs rather than refusing, and evaluate accepts a columns count with no type check or upper bound
priority: P2
effort: S
status: ready
classes: defect
feature: floating-point-domain
touches: src/anesthesia_sim/core/run_definition.py, tests/unit
deferred-from: v0.7.0 - split from the generator head PL-58D7 on 2026-10-25, which this gate defers for the same reason; the generator tier ranks it, not the gate
added: 2026-10-25
payoff: a request for more samples than a chart can draw is refused instead of hanging
verify: grep -rq 'def test_evaluate_anchored_refuses_more_samples_than_its_bound' tests/unit
---

**Problem.** RunDefinition.evaluate_anchored loops once per sample with only stop_s / spacing_s being finite to bound it, so a spacing of 1e-300 s hangs rather than refusing, and evaluate accepts a columns count with no type check or upper bound

**Where it is.** `RunDefinition.evaluate_anchored` accepts any positive finite spacing for which `stop_s / spacing_s` is finite (`PL-BPRK`), and `_anchored_columns` then loops once per anchored sample. At a spacing of 1e-300 s and a one-second window that is about 1e300 iterations, so the call never returns rather than refusing. `PL-6QYJ` was dropped on 2026-10-25 because the values drawn at a fine spacing stay accurate. That decision is about accuracy and does not cover this hang. `RunDefinition.evaluate` tests only `columns < 1`, so it accepts a float or an arbitrarily large int. Found by the `PL-58D7` inventory on 2026-10-25 by reading the code; not yet reproduced. No shipped caller is known to pass such a spacing or count. `app/playback.py` `PlaybackRate.steps_per_tick` holds a similar quotient.

**What to do.** Bound the number of samples one call may produce, for example by the most columns a chart can draw, and refuse anything past it with an error from `core/exceptions.py`. Check that `columns` is an int.

**Why it matters.** A call that never returns is a hang with no error, so the caller never learns why.

**Done when.** `evaluate_anchored` and `evaluate` refuse a request for more samples than the stated bound with a `core/exceptions.py` error, and a test drives each one past it.

**Generator check.** A member of the `floating-point-domain` feature, split from `PL-58D7`, the generator head.
