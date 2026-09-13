---
id: PL-V6M0
title: _apply_setting reports a SimulationExecutionError as a refused setting and lets the run continue, which is the opposite of what that type means
priority: P1
effort: S
status: done
classes: safety, anticipated
touches: src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py
added: 2026-09-13
closed: 2026-09-13
verify: uv run pytest tests/unit/test_simulation_view.py -q && grep -q 'def test_a_settings_execution_error_halts_the_run_instead_of_reading_as_refused' tests/unit/test_simulation_view.py
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

## Decided 2026-09-13: catch `SimulationConfigurationError`, not the base class

**`docs/ARCHITECTURE.md` had already decided it, and the code was what
disagreed.** The "Failure direction" section splits the hierarchy into two
branches that "mean different things and get different treatment", and its
first bullet says in terms that `SimulationConfigurationError` is what "the
view's `_apply_setting` catches ... the run is untouched and keeps going",
against a second bullet whose branch means "the run must stop". So this was
never a choice between two defensible readings: the specification named the
narrow class, `PL-YK2V` widened the arm to the base class while fixing a
different problem, and nothing noticed because the widened arm and the
specified one behave identically until a route raises the execution branch.
That is what made the decision a session's rather than the owner's.

**What changed.** One word in `app/simulation_view.py` — the arm now reads
`except SimulationConfigurationError` — plus the import, the docstring
paragraph stating the policy, and the `Args:` note. Everything under
`SimulationExecutionError` now falls to the `except Exception` arm and
`_halt_run`, which already routes `SimulationDomainLimitError` to the
supported-limit channel rather than to `fail`, so the milder branch gets its
correct wording with no second branch added here. A bare
`AnesthesiaSimulationError` raised directly is unclassified and halts too,
which is the asymmetry `_halt_run`'s own docstring already states.

**Why not leave it.** The alternative the brief named — keep the base-class
catch and accept that the distinction only matters once a route exists — was
refused because the failure it protects against is silent. A
`SimulationExecutionError` reported as a refused setting leaves "Running"
over numbers the core has disowned, with nothing on screen and nothing in the
logs distinguishing it from an ordinary refusal, which is the
plausible-looking value `CLAUDE.md` prefers an obvious failure state to. The
fix costs one word and the tests that pin it; waiting costs a route nobody
has written yet plus the session that would have to diagnose it.

**Regression tests, run against the old arm first.** Both new tests fail with
the base-class catch restored and pass with the narrow one; the existing
`test_a_refused_setting_is_still_a_notice_and_not_a_halt` passes under both,
which is what shows the narrowing did not collapse the case it must keep.

**Docs swept:** `docs/ARCHITECTURE.md` (the Failure-direction bullets, which
this change makes true rather than aspirational), `docs/MODEL.md` (§ "A
refused setting is not recorded", unaffected — recording still happens after
the setter returns). No edit was needed to either.

