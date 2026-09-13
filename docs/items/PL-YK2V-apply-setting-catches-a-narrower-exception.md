---
id: PL-YK2V
title: _apply_setting catches a narrower exception class than the timer paths, so an unexpected raise escapes into Flet's dispatch
status: done
priority: P2
effort: S
classes: defect, ux
touches: src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py
added: 2026-09-02
closed: 2026-09-13
verify: uv run pytest tests/unit/test_simulation_view.py && grep -q 'def test_a_settings_raise_outside_the_project_hierarchy_halts_the_run' tests/unit/test_simulation_view.py
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

**Measured 2026-09-02.** Confirmed as written, through the real
`_apply_setting` on a view built from `tests/unit/test_simulation_view.py`'s
own doubles. A `SimulationConfigurationError` is handled and leaves
`_rejected_setting_notice` set to `'Setting refused - a value the core
refused'`. A `TypeError` raised from the same call site **escapes**
`_apply_setting` and propagates to the caller - which in the running
application is Flet's event dispatch - so the `_refresh_and_render()` on the
last line never runs and the interface is not put back in step with the
controller.

The contrast is the point: `_halt_run(TypeError(...))`, which is where the
two timer loops send exactly this exception, stops the run and puts the
failure on screen. Same error, same process, two policies.

**Decided 2026-09-13: widen, as the audit recommended.**
The settings path now applies the timer loops' policy - an
`AnesthesiaSimulationError` stays a refused-setting notice, anything else
routes to `_halt_run()`. The alternative the brief offers, closing the routes
in one at a time, loses on the standard rather than on effort: it requires
every future raise to be enumerated in advance, and the failure when one is
missed is silent and clinical. `_refresh_and_render()` never runs, so the
dropdown shows the agent the reader picked while the badge and all six
readouts still show the previous one, the run is silently paused, and nothing
on screen says any of it. That is a displayed value under the wrong patient
model, which `CLAUDE.md` names as a safety failure in its own right - not a
missing log line, and not something the reader can be expected to notice.

Two tests rather than one, because widening a catch can overshoot: the second
pins the narrow case - same method, same doubles, opposite outcome - so a
`SimulationConfigurationError` is still a notice over an untouched run rather
than being collapsed into a halt.

**Not folded in, and filed separately as `PL-V6M0`.** The catch is on the
base class, so a `SimulationExecutionError` raised inside a setting handler
is still reported as a refused setting and the run continues - which is the
opposite of what that type means. No route into `_apply_setting` raises it
today, so this is anticipated rather than live, and it is a different
question from the asymmetry this item was about.
