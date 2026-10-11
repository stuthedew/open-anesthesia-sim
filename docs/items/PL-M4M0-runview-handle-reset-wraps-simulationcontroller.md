---
id: PL-M4M0
title: RunView._handle_reset wraps SimulationController.reset() in nothing, so the SimulationConfigurationError that equation_settings() raises at Reset when the tissue flows are stale (a CardiacOutput written onto patient.cardiac_output_l_min past set_cardiac_output, the type-only write guard PL-LBQY chose) escapes the slot after pause() and _state.reset(), leaving a half-reset run paused with no failure recorded, the readout showing a cardiac output the model never ran at and case_restarted never emitted; at step time the same stale record is presented as a SimulationNumericalError in L/s where every readout shows L/min (found reviewing PL-LBQY)
priority: P1
effort: M
status: done
classes: safety, defect
feature: parse-dont-validate
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/core/governing_equations.py, src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/core/patient.py, tests/integration/test_simulation_view.py, tests/integration/test_controller.py, tests/unit/test_governing_equations.py, tests/unit/test_dashboard_frame.py, tests/unit/test_uptake_system_failure.py, docs/MODEL.md, docs/ARCHITECTURE.md
added: 2026-10-05
closed: 2026-10-11
pr: 1414
payoff: a Reset the simulator refuses stops the run visibly with its reason, rather than leaving a half-reset run showing a cardiac output the model never ran at
verify: grep -q 'def test_a_reset_the_core_refuses_halts_the_run_visibly' tests/integration/test_simulation_view.py && grep -q 'def test_a_tissue_flow_mismatch_is_stated_in_litres_per_minute' tests/unit/test_governing_equations.py
---

**Problem.** `RunView._handle_reset` calls `SimulationController.reset()` with
no `try` (`app/run_view.py`), and `reset()` can raise: on a trunk it rebuilds
the run definition from `uptake_system.equation_settings()`, and
`UptakeEquationSettings` refuses tissue flows that do not sum to cardiac output
(`core/governing_equations.py`). They stop summing when a `CardiacOutput` is
written straight onto `patient.cardiac_output_l_min` rather than through
`set_cardiac_output`, which rescales the tissue flows with it - the type-only
write guard `PL-LBQY` chose checks the value's type, not that the flows follow.
`reset()` has already run `pause()` and `_state.reset()` by then, so the raise
leaves a run half-reset: state cleared to zero, the old run definition and
control timeline kept, no failure recorded, and the slot gone before
`case_restarted` and `presentation_requested` are emitted. At step time the
same record is refused inside `advance()`, which restates it as a
`SimulationNumericalError` - a step that could not be completed - in L/s, where
every readout and control shows L/min.

**Reproduced 2026-10-05.** One `uv run python -c` under
`QT_QPA_PLATFORM=offscreen`: a `SimulationView` over one `SimulationController`,
Start clicked, `patient.cardiac_output_l_min = CardiacOutput(6.0)` written
directly, then Reset clicked. The slot printed `SimulationConfigurationError:
the tissue groups are perfused at 0.08333333333333333 L/s in total but cardiac
output is 0.1 L/s ...` and the run read `is_running False | failure_reason None
| snapshot CO 6.0 L/min | status 'Running' | Pause enabled True |
case_restarted emitted 0`. `start()` then `advance(SIMULATION_STEP_S)` raised
`SimulationNumericalError: the simulation step of 0.1 s could not be completed
and was rolled back ...: the tissue groups are perfused at 0.0833... L/s in
total but cardiac output is 0.1 L/s ...`.

**Why it matters.** A screen reading "Running" with Pause enabled over a
stopped controller, a readout at a cardiac output the tissues were never
perfused at, and no banner, is the stale, wrong-context display `CLAUDE.md`'s
safety standard names - the shape `PL-25KS` fixed for the render path,
reached here through Reset, the one control a learner uses to get out of a
failure. The step-time message blames a step that never ran and states the
disagreement in a unit nothing on screen uses. Not reachable from a supported
setting today: every interface path sets cardiac output through
`set_cardiac_output`, so the stale record needs a direct write.

**Done when.** A Reset the core refuses halts the run through the path a
failed step takes - failure recorded, status word, transport and banner
written - and leaves no half-reset state: whatever `reset()` can refuse is
refused before it clears anything, or the halt says the run is cleared.
`test_a_reset_the_core_refuses_halts_the_run_visibly` in
`tests/integration/test_simulation_view.py` writes the stale cardiac output as
above, clicks Reset, and asserts the failure is recorded and shown and that
Start is not offered; it fails on today's tree. And the tissue-flow refusal
states both flows in L/min, as the settings record holds them:
`test_a_tissue_flow_mismatch_is_stated_in_litres_per_minute` in
`tests/unit/test_governing_equations.py`, beside
`test_rejects_tissue_flows_that_do_not_sum_to_cardiac_output`. Whether a stale
record met at step time keeps `advance()`'s restatement as a step that could
not be completed - the settings are built inside the step, by
`_propagator_for` - or is refused as a settings disagreement before the step
begins is the implementing session's call; the brief only asks that the
choice be stated in `advance()`'s docstring.

**Decided 2026-10-11, in the implementing session.** Refused before anything
is cleared, not announced after: `SimulationController.reset()` now builds the
settings record first - `self._state.uptake_system.equation_settings()` ahead
of `pause()`, `_state.reset()` and the rest - and hands it to `RunDefinition`
on a trunk and to `_open_at(resume_point, settings)` on a branch, whose
`record_change` used to read the record itself after the branch had been
stood back at its fork. The record holds no dynamic value, so the one read
before the clear is the one the cleared system would give after; and a
refused Reset leaves the run exactly as it was, still running if it was, on
its own state, definition, timeline and any recorded failure
(`test_a_reset_the_core_refuses_leaves_the_run_exactly_as_it_was`,
`test_a_branch_reset_the_core_refuses_leaves_the_branch_exactly_as_it_was`).
The view halts on it: `RunView._handle_reset` wraps the call and routes every
raise through `_halt_run`, the path a failed step takes, so the refusal is
recorded as the failure and the status word, the transport and the banner
state it; `case_restarted` is not emitted, since no case restarted. A
`SimulationConfigurationError` here is deliberately not treated as a refused
setting, because the run it leaves cannot be cleared.

The banner's way out is the one new piece. Every failure wording ended by
naming Reset, which for this halt is the control just refused, so
`FAILURE_NOTICE_TEMPLATE` and `UNDRAWN_FAILURE_NOTICE_TEMPLATE` take an
`{exit}` - `RESET_EXIT_TEXT` normally, `refused_reset_exit`'s sentence while
Reset is what was refused - in three wordings: on a run that had not failed,
"Reset was refused for this reason. Start a new case to continue.", since the
recorded reason *is* the refusal; on a run that had, the controller keeps the
first failure as the reason (`fail`), so the exit carries the refusal itself,
"Reset was refused — {error}. Start a new case to continue."; and on a branch,
which cannot start a case of its own (`PL-TFX5`), the trunk's Reset, which
ends the comparison, in `COMPARING_FORK_LOCK_TEMPLATE`'s words. The view holds
it beside the refused-setting notice, and an accepted setting clears it, since
`set_cardiac_output` is the repair that makes the next Reset take
(`test_a_refused_reset_takes_once_the_cardiac_output_is_set_again`).
`SUPPORTED_LIMIT_NOTICE_TEMPLATE` keeps its own Reset line: a refused Reset
halts as a failure, which outranks the limit everywhere, so that banner never
carries another exit.

Step time keeps `advance()`'s restatement, stated in its docstring. The record
is met inside the step, where `_propagator_for` rebuilds it only when a
setting has moved (`PL-R460`), and a `SimulationConfigurationError` out of
`advance()` would promise a run still worth continuing (`core/exceptions.py`),
which a run refused on every step after, and at Reset, is not. Refusing it
before the step would also have to rebuild the record on every step, undoing
`PL-R460`, to decide nothing the restatement does not already say.
`test_a_stale_record_met_at_step_time_is_a_failed_step_stated_in_litres_per_minute`
pins it, with the rollback.

The refusal now states both flows in L/min, summed from the record's own
`blood_flow_l_min` fields with the comparison left in L/s. Beyond the unit, it
removes a float artefact the L/s form carried: the required test's run on the
unfixed tree printed `perfused at 0.12999999999999998 L/s in total but cardiac
output is 0.156 L/s`, where the L/min form reads `7.8 L/min` against
`9.36 L/min`, the values that were set.

Both required tests were run against the unfixed source before the fix was
restored: the view test failed on `controller.has_failed` being False, the
half-reset run, and the settings test on the L/s message above.
`test_a_wrapped_mark_row_is_told_apart_from_the_row_below_it` failed in this
container on the same run - a font-metrics assertion, `23 >= 2 * 15`, which is
the container's Qt font rendering (`PL-K9Z5`) and not this item's.
