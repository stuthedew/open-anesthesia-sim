---
id: PL-9SL5
title: RunDefinition.evaluate spaces its columns as start_s plus a multiple of the spacing and never pins the last one, so about one window in forty returns a final instant one rounding unit past stop_s, and past the run's reach when stop_s is the reach, which the method says it refuses
priority: P1
effort: S
status: done
classes: defect, safety
feature: replay-findings
milestone: v0.6.9
touches: src/anesthesia_sim/core/run_definition.py, tests/unit/test_run_definition.py
added: 2026-10-25
closed: 2026-10-26
pr: 1864
payoff: no display path can propagate a column past the instant the run has reached
verify: grep -q 'def test_evaluate_ends_its_last_column_exactly_at_stop' tests/unit/test_run_definition.py
---

**Problem.** `RunDefinition.evaluate` builds its column times as `start_s + column * spacing_s` (`src/anesthesia_sim/core/run_definition.py`). It never sets the last column to `stop_s`. So the last time often lands one rounding unit past `stop_s`. On an 11 s run, `evaluate(0.3, 11.0, 42)` returns a last time of 11.000000000000002. When `stop_s` is the time the run has reached, that column is propagated past the run. `_require_within_run` refuses exactly that instant when a caller names it.

**Why it matters.** The chart no longer uses this method. It uses `evaluate_anchored`, which pins both bounds (`run_definition.py`). But `evaluate` is still a public display path, and the tests use it as the display-path reference. A caller that matches the last column to the readout or to a change instant by equality will miss it. Setting the last column to exactly `stop_s` removes the fault. Deleting `evaluate` would remove it too, if the tests can compare against `evaluate_anchored` instead.

**Done when.** `RunDefinition.evaluate` returns `stop_s` exactly as its last column time, as `evaluate_anchored` does. `tests/unit/test_run_definition.py` has `test_evaluate_ends_its_last_column_exactly_at_stop`, which checks `evaluate(0.3, 11.0, 42)` on an 11 s run. Deleting `evaluate` and moving its tests to `evaluate_anchored` also satisfies the item, with the test written against the replacement.

**Found by.** `PL-TBQS` reviewer replay on #430, findings 430 r02 F1 and 430 r06 F1, checked against main on 2026-10-25. Reproduced with `scratchpad/r/scripts/d_430_core.py`: `evaluate` returned 11.000000000000002 and `evaluate_anchored` returned 11.0 for the same window.
