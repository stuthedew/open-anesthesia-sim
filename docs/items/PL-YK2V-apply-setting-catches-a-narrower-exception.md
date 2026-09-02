---
id: PL-YK2V
title: _apply_setting catches a narrower exception class than the timer paths, so an unexpected raise escapes into Flet's dispatch
status: needs-decision
priority: P2
effort: S
classes: defect, ux
touches: src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py
added: 2026-09-02
---

**Problem.** `_apply_setting()` catches `AnesthesiaSimulationError` only.
The two timer loops catch bare `Exception` and route to `_halt_run()`,
deliberately - `_halt_run`'s docstring says a `TypeError` from a future
refactor "kills the loop exactly as silently as a modelling failure does".
The settings path applies the opposite policy to the same class of error.

**Why it matters.** An unexpected raise inside a setting handler escapes
into Flet's event dispatch, so `_refresh_and_render()` at the end of
`_apply_setting` never runs. The dropdown then shows the agent the user
picked while the header badge and all six readouts still show the previous
one, the run is silently paused, and no notice explains any of it.
`_apply_setting`'s own docstring names that outcome as the thing it exists to
prevent: "the control would keep the refused value while the simulation kept
running at the old one".

`PL-B32L` is the concrete way to reach it today - a data-file load error
during an agent switch - but the asymmetry is the finding, not that one
route.

**Where.** `src/anesthesia_sim/app/simulation_view.py`, `_apply_setting()`
against `_run_simulation_timer()` and `_run_render_timer()`.

**Decision needed.** Whether the settings path should adopt the timer paths'
policy: an `AnesthesiaSimulationError` stays a refused-setting notice, and
anything else routes to `_halt_run()` so the failure is on screen rather
than in a log nobody reads. The alternative is to leave the narrow catch and
close the routes into it one at a time, `PL-B32L` being the first.

Widening is what the audit recommended, since it makes the two paths agree
rather than requiring every future raise to be enumerated. Not agreed.

**Done when.** The decision is recorded, and if the catch widens, a test
makes a setting call raise a non-project exception and asserts the interface
reaches a halted state rather than an inconsistent one.
