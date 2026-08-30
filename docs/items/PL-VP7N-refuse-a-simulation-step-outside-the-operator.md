---
id: PL-VP7N
title: Refuse a simulation step outside the operator split's applicability domain
priority: P1
effort: M
status: ready
classes: safety
feature: numerical-domain
touches: src/anesthesia_sim/core/respiratory_system.py, src/anesthesia_sim/core/simulation.py, src/anesthesia_sim/app/simulation_view.py, docs/MODEL.md, tests/reference/test_coupled_dynamics.py, tests/reference/test_sevo_patient.py, tests/integration/test_controller.py, tests/unit/test_simulation.py, tests/unit/test_simulation_view.py
added: 2026-08-30
verify: uv run pytest -k maximum_simulation_step
---

**Problem.** `core/` accepts any simulation step and returns a plausible wrong
number. `docs/MODEL.md:560-561` states the operator split "has an applicability
domain, and stepping outside it must fail rather than produce a number", but the
only check on the step is `require_positive_finite("simulation_step_s", ...)` at
`core/respiratory_system.py:138`, which has no upper bound. Measured over 600 s
of sevoflurane wash-in, against the same run at the shipped 0.1 s step:

| Step | Alveolar error at 600 s |
| --- | --- |
| 1 s | 0.005 percentage points |
| 10 s | 0.060 percentage points |
| 30 s | 0.205 percentage points |

No error is raised at any of them. The 30 s figure is twenty times the 0.01
percentage-point resolution the interface displays, so the readout is wrong in
its *first* decimal while presenting itself as a settled value.
`SimulationNumericalError` first fires at dt=60 s, and it is a capacity guard —
a compartment driven negative — not a domain check: it happens to catch the
grossest case and says nothing about the range between.

**Why it matters.** The supported step is currently declared in the
presentation layer, `SIMULATION_STEP_S = 0.1` at `app/simulation_view.py:39`,
and restated a second time at `tests/reference/test_coupled_dynamics.py:131`
*without* the cross-check that `test_envelope_limits_match_the_interface`
(`:550`) gives the slider limits. So the one number that bounds the split's
validity is held in two places that cannot disagree loudly, and in neither of
them is it enforced. Any caller of `core/` — a future headless runner, a
notebook, a test — gets a number instead of a refusal. `CLAUDE.md`'s standard
is explicit that an obvious failure is preferred to a plausible-looking number
when correctness cannot be established; this is the path where that is not
true.

**Where.** `core/respiratory_system.py:138` (`advance`),
`core/simulation.py` (`SimulationState.advance`), `app/simulation_view.py:39`,
`docs/MODEL.md:560-566`.

**Decided approach.** A documented `MAXIMUM_SIMULATION_STEP_S` in core,
validated in `RespiratorySystem.advance` and `SimulationState.advance`, raising
`SimulationConfigurationError` — the caller's argument is refused and nothing
has been miscalculated yet, which is the distinction
`respiratory_system.py:141-152` already draws between a refused setting and an
untrustworthy run. `app/` imports the constant rather than declaring its own,
with a test pinning the two together the way
`test_envelope_limits_match_the_interface` pins the sliders.

**Not on the compartments.** The guard belongs on the coupled system, not on
`BreathingCircuit` or the individual compartments. A bare circuit stepped 60 s
is a single exponential with no splitting error at all, and
`tests/unit/test_circuit.py:35` and `:58` exercise exactly that; they must keep
passing unaltered.

**Blast radius.** Five existing call sites advance the coupled system outside
the domain and assert on the results. They are reworked to run inside it, never
exempted from the guard:

- `tests/integration/test_controller.py:178` and `:248`
- `tests/unit/test_simulation.py:11` and `:29`
- `tests/unit/test_simulation_view.py:815`

Also in scope: `test_step_refinement_converges`
(`tests/reference/test_sevo_patient.py:122`) compares two step sizes where
`docs/MODEL.md:856-862` specifies three (0.1, 0.05, 0.025).

**Relation to other items.** PL-SN2C (add the playback multiplier as steps per
tick) states this invariant as prose in its Safety notes — the multiplier "must
never change the step size… would also invalidate the error bound
`docs/MODEL.md` § 'Displayed precision' derives the two-decimal readout from".
That is the hazard written down; this item is what makes it true in code. Order
of work: this item, then PL-VM40 (derive simulated time from a step count),
then PL-SN2C, which depends on PL-VM40.

This is also finding P2-1 of `tools/review-verification/`, which has reproduced
since the v0.2.0 architecture review and was never captured — see PL-STNV
(retire the review-verification harness and capture its last live finding).

**Done when.** `core/` names a maximum simulation step with its derivation
recorded in `docs/MODEL.md`, both `RespiratorySystem.advance` and
`SimulationState.advance` refuse a larger one with
`SimulationConfigurationError`, `app/` imports that constant and a test pins the
two together, the five call sites above run inside the domain, the bare-circuit
tests pass unaltered, and the step-refinement test compares the three steps
`docs/MODEL.md` specifies.
