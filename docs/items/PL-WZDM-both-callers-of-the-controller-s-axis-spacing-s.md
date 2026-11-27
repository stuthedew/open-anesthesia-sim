---
id: PL-WZDM
title: Both callers of the controller's _axis_spacing_s raise its result to one second, where the function could return that minimum itself
priority: P3
effort: S
status: done
classes: defect
feature: tests-detect-wrong-values
touches: src/anesthesia_sim/app/controller.py, tests/integration/controller/test_controller_preview.py, tests/unit/test_controller_drawn_seconds.py
deferred-from: v0.7.0 - its problem is new since the freeze and no release schedules it, so it is deferred on the terms of § "Deferring to the next gate"; not safety or science (triage 2026-11-27)
added: 2026-11-23
closed: 2026-11-27
pr: 2334
filed-pr: 2306
payoff: the chart time grid states its one-second minimum once, so a change to it cannot leave a caller behind
tests: tests/unit/test_controller_drawn_seconds.py::test_an_axis_of_zero_width_is_spaced_one_second_and_a_wider_one_by_its_columns, tests/integration/controller/test_controller_preview.py::test_a_run_on_an_axis_of_zero_width_is_drawn_at_that_one_second, tests/integration/controller/test_controller_preview.py::test_a_preview_toward_an_axis_of_zero_width_is_drawn_at_every_second_up_to_it
---

**Problem.** `_axis_spacing_s` in `src/anesthesia_sim/app/controller.py` returns 0 for an axis of zero width, and both of its callers, `drawn_window` and `preview_window`, then raise the spacing to one second with `max(spacing_s, 1)`. The one-second minimum is stated in three places, and mutants 21 and 22 of the 2026-11-23 mutation run, which change those `max` calls, survive because the chart never asks for a zero-width axis.

`PL-PZSF` found it on 2026-11-23, and recorded the reason in the function's docstring.

**What to do.** Have `_axis_spacing_s` return at least one second, remove the two `max` calls, and update its docstring. Check that `drawn_window` and `preview_window` return the same instants as before for a zero-width axis, with a test for each.

**Why it matters.** The one-second minimum is written in three places, so a change to it in one leaves the others behind, and two mutants of the 2026-11-23 run survive because no test asks for a zero-width axis.

**Reproduced 2026-11-27.** On `main` at `f653c1eb`, `src/anesthesia_sim/app/controller.py` still applies `max(spacing_s, 1)` in both callers of `_axis_spacing_s`. The function was added on 2026-10-31 (#1896), after the freeze.

**Done when.** `_axis_spacing_s` returns at least one second, neither caller applies its own minimum, and a test for each of `drawn_window` and `preview_window` shows that a zero-width axis returns the same instants as before.

**Generator check.** A minimum stated by each caller instead of by the function that owns it, so `defect` under the one-source-of-truth rule. Found by `PL-PZSF` among mutation survivors. A one-off.

**Fixed 2026-11-27.** `_axis_spacing_s` returns `SIMULATION_STEP_S`, one second, for an axis of zero width, and the two `max(spacing_s, 1)` calls are gone. The zero case is an explicit `if span_s == 0.0` branch rather than the old conditional expression on `span_s > 0.0`, because once the function returns the minimum itself, that comparison gives the same spacing for every axis whether it is made against 0.0 or 1.0, which would leave a mutant no test can catch. `test_an_axis_of_zero_width_is_spaced_one_second_and_a_wider_one_by_its_columns` checks the spacing at zero, two minutes, fifteen minutes and an hour, and the two window tests check that a zero-width axis draws the same instants as on `main` at `9c475dc7`: `(30,)` for the run at 30 s, nothing at 30.5 s, and every second from 60 s to 70 s for a preview toward 70 s.

**Mutation check, 2026-11-27.** The unit tests did not catch a mutant that divides the span by `columns - 2` in place of `columns - 1`, because every axis the test used was 150 columns wide, where both round down to the same second. The test now also checks three columns over ten seconds, which stand 5 s apart.
