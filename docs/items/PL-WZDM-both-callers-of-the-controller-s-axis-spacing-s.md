---
id: PL-WZDM
title: Both callers of the controller's _axis_spacing_s raise its result to one second, where the function could return that minimum itself
priority: P3
effort: S
status: ready
classes: defect
feature: tests-detect-wrong-values
touches: src/anesthesia_sim/app/controller.py, tests/integration/controller/test_controller_preview.py
deferred-from: v0.7.0 - its problem is new since the freeze and no release schedules it, so it is deferred on the terms of § "Deferring to the next gate"; not safety or science (triage 2026-11-27)
added: 2026-11-23
filed-pr: 2306
payoff: the chart time grid states its one-second minimum once, so a change to it cannot leave a caller behind
---

**Problem.** `_axis_spacing_s` in `src/anesthesia_sim/app/controller.py` returns 0 for an axis of zero width, and both of its callers, `drawn_window` and `preview_window`, then raise the spacing to one second with `max(spacing_s, 1)`. The one-second minimum is stated in three places, and mutants 21 and 22 of the 2026-11-23 mutation run, which change those `max` calls, survive because the chart never asks for a zero-width axis.

`PL-PZSF` found it on 2026-11-23, and recorded the reason in the function's docstring.

**What to do.** Have `_axis_spacing_s` return at least one second, remove the two `max` calls, and update its docstring. Check that `drawn_window` and `preview_window` return the same instants as before for a zero-width axis, with a test for each.

**Why it matters.** The one-second minimum is written in three places, so a change to it in one leaves the others behind, and two mutants of the 2026-11-23 run survive because no test asks for a zero-width axis.

**Reproduced 2026-11-27.** On `main` at `f653c1eb`, `src/anesthesia_sim/app/controller.py` still applies `max(spacing_s, 1)` in both callers of `_axis_spacing_s`. The function was added on 2026-10-31 (#1896), after the freeze.

**Done when.** `_axis_spacing_s` returns at least one second, neither caller applies its own minimum, and a test for each of `drawn_window` and `preview_window` shows that a zero-width axis returns the same instants as before.

**Generator check.** A minimum stated by each caller instead of by the function that owns it, so `defect` under the one-source-of-truth rule. Found by `PL-PZSF` among mutation survivors. A one-off.
