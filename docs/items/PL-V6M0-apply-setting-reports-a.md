---
id: PL-V6M0
title: _apply_setting reports a SimulationExecutionError as a refused setting and lets the run continue, which is the opposite of what that type means
priority: P1
effort: S
status: needs-decision
classes: safety, anticipated
touches: src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py
added: 2026-09-13
---

**Problem.** _apply_setting reports a SimulationExecutionError as a refused setting and lets the run continue, which is the opposite of what that type means

**Why it matters.** `PL-YK2V` widened `_apply_setting`'s catch so that
anything outside the project hierarchy halts the run. The narrow arm it kept
catches `AnesthesiaSimulationError`, the *base* class, and reports every
subclass of it as a refused setting over a run that keeps going. That is
right for `SimulationConfigurationError` - a value was rejected and nothing
was miscalculated - and wrong for `SimulationExecutionError`, whose whole
meaning per `core/exceptions.py` is that "the run must stop rather than
continue". A `SimulationDomainLimitError` is the same shape again: it would
read as a refused setting rather than as the run reaching the end of the
supported domain, which `_halt_run` routes to its own channel precisely so
that it is not mislabelled.

**Anticipated rather than live.** No route into `_apply_setting` raises
either type today: the setting handlers call controller setters, and
`SimulationExecutionError` is raised from `advance()`. It becomes reachable
if a setting is ever applied by re-stepping, or if a setter grows a guard
that raises the execution branch.

**Where.** `src/anesthesia_sim/app/simulation_view.py`, `_apply_setting()`.

**Decision needed.** Whether the narrow arm should catch
`SimulationConfigurationError` specifically rather than the base class,
routing the other two branches to `_halt_run()` alongside everything else.
That is the reading which makes the arm mean what the exception hierarchy
says it means. The alternative is to leave the base-class catch and accept
that the distinction only matters once a route exists.

**Done when.** `_apply_setting`'s narrow arm catches only what a refused
setting can be, with the execution branches routed to `_halt_run()` alongside
everything else - or the base-class catch is kept deliberately and the reason
is recorded at the `except` itself, where the next reader of
`core/exceptions.py` will meet it. Either way a test drives a setting handler
raising each of `SimulationConfigurationError`, `SimulationExecutionError` and
`SimulationDomainLimitError`, and asserts which channel the run ends up in.

**On the band.** Seated at P1 because `classes` carries `safety` and the pin
in `checks.py` holds safety-critical work at P0 or P1. `anticipated` is carried
for what it says to a reader - no route raises either type today - and not for
the exemption, which `checks.py` grants only at `status: blocked` and which
this item cannot claim: nothing blocks it, and the trigger is a future route
rather than a named item or milestone.
