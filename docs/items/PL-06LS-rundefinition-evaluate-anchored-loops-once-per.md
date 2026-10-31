---
id: PL-06LS
title: RunDefinition.evaluate_anchored loops once per sample with only stop_s / spacing_s being finite to bound it, so a spacing of 1e-300 s hangs rather than refusing, and evaluate accepts a columns count with no type check or upper bound
priority: P2
effort: S
status: done
classes: defect
feature: floating-point-domain
milestone: v0.6.9
touches: src/anesthesia_sim/core/run_definition.py, tests/unit
deferred-from: v0.7.0 - split from the generator head PL-58D7 on 2026-10-25, which this gate defers for the same reason; the generator tier ranks it, not the gate
added: 2026-10-25
closed: 2026-10-25
pr: 1836
payoff: a request for more samples than a chart can draw is refused instead of hanging
verify: grep -rq 'def test_evaluate_anchored_refuses_more_samples_than_its_bound' tests/unit
---

**Problem.** RunDefinition.evaluate_anchored loops once per sample with only stop_s / spacing_s being finite to bound it, so a spacing of 1e-300 s hangs rather than refusing, and evaluate accepts a columns count with no type check or upper bound

**Where it is.** `RunDefinition.evaluate_anchored` accepts any positive finite spacing for which `stop_s / spacing_s` is finite (`PL-BPRK`), and `_anchored_columns` then loops once per anchored sample. At a spacing of 1e-300 s and a one-second window that is about 1e300 iterations, so the call never returns rather than refusing. `PL-6QYJ` was dropped on 2026-10-25 because the values drawn at a fine spacing stay accurate. That decision is about accuracy and does not cover this hang. `RunDefinition.evaluate` tests only `columns < 1`, so it accepts a float or an arbitrarily large int. Found by the `PL-58D7` inventory on 2026-10-25 by reading the code; not yet reproduced. No shipped caller is known to pass such a spacing or count. `app/playback.py` `PlaybackRate.steps_per_tick` holds a similar quotient.

**What to do.** Bound the number of samples one call may produce, for example by the most columns a chart can draw, and refuse anything past it with an error from `core/exceptions.py`. Check that `columns` is an int.

**Why it matters.** A call that never returns is a hang with no error, so the caller never learns why.

**Done when.** `evaluate_anchored` and `evaluate` refuse a request for more samples than the stated bound with a `core/exceptions.py` error, and a test drives each one past it.

**Generator check.** A member of the `floating-point-domain` feature, split from `PL-58D7`, the generator head.

**Outcome (2026-10-25).** `core/run_definition.py` now holds `MAXIMUM_WINDOW_COLUMNS = 100_000`. `evaluate` refuses more columns than that, and refuses a `columns` that is not an `int` or is a `bool`, with a `TypeError` that names `columns`. `evaluate_anchored` counts the grid multiples it would loop over, exactly, before it loops, and refuses a count past the bound. A full-width 8K plot asks for 7 681 columns, so the bound rejects nothing a chart draws. `chart_columns` is read in the test so that a change there fails the suite rather than a wide screen. A blind review found that the count can be one more than the grid columns drawn, because a multiple on `stop_s` is drawn as the stop. The constant's docstring and the refusal now call the count "grid multiples" and say so. It also found that a 1e-300 s spacing printed a 300-digit count whose later digits were rounding error, so the refusal now gives six significant figures.

**Reproduced before the fix**, against `origin/main` at `af627f045` with this branch's `run_definition.py` swapped back. `evaluate_anchored(6.0, 7.0, 1e-300)` on a 30 s sevoflurane run did not return within 30 s (`timeout 30` exited 124). `evaluate(0.0, 0.0, 5.0)` raised `TypeError: 'float' object cannot be interpreted as an integer`, which does not name `columns`. `evaluate(0.0, 0.0, True)` returned one column, and `evaluate(0.0, 30.0, 100_001)` returned 100 001 columns. The new tests import `MAXIMUM_WINDOW_COLUMNS`, so they cannot be collected against the old code; the script at `/mnt/project-files/v0.7.0/pl-06ls/pre_fix.py` is the variant that does not need it.

**Filed alongside.** `PL-T6P0`: `PlaybackRate.steps_per_tick` has the same shape. It returns 3.000e+305 steps at 300x with a 1e300 s tick and a 1 ms step, measured on 2026-10-25.
