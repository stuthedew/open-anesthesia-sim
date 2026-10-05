---
id: PL-M4M0
title: RunView._handle_reset wraps SimulationController.reset() in nothing, so the SimulationConfigurationError that equation_settings() raises at Reset when the tissue flows are stale (a CardiacOutput written onto patient.cardiac_output_l_min past set_cardiac_output, the type-only write guard PL-LBQY chose) escapes the slot after pause() and _state.reset(), leaving a half-reset run paused with no failure recorded, the readout showing a cardiac output the model never ran at and case_restarted never emitted; at step time the same stale record is presented as a SimulationNumericalError in L/s where every readout shows L/min (found reviewing PL-LBQY)
status: untriaged
added: 2026-10-05
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
