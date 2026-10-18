---
id: PL-4H4T
title: No test changes the step size within one uptake system, so a propagator cache key that loses the step survives the whole suite, and SimulationState.reset() followed by a different step would reuse the old exp(A*dt) with accounting still passing
priority: P2
effort: S
status: done
classes: test
feature: tests-detect-wrong-values
milestone: v0.5.26
touches: tests/unit/test_matrix_exponential.py, tests/unit/test_simulation.py
added: 2026-10-17
closed: 2026-10-17
pr: 1513
payoff: a propagator cache that reuses the old step's exp(A dt) after a step change fails a test, so a reset followed by a new step size cannot advance the run by the wrong time
verify: grep -q 'def test_a_step_size_change_within_one_system_obeys_the_semigroup_property' tests/unit/test_matrix_exponential.py
---

**Problem.** No test changes the step size within one uptake system, so a propagator cache key that loses the step survives the whole suite, and SimulationState.reset() followed by a different step would reuse the old exp(A*dt) with accounting still passing

**Severity: medium, latent.** The shipped interface cannot reach this today,
but the core API can. Audit finding `_propagator_for__mutmut_2`, a real-gap
mutant confirmed against the whole suite.

**Evidence.** The mutant changes
`key = self._propagator_cache_key(simulation_step_s)` to
`self._propagator_cache_key(None)` in `AgentUptakeSystem._propagator_for`
(`src/anesthesia_sim/core/uptake_system.py`), so the cache key no longer
includes the step. It survived the whole simulator suite at `25ef454b`
(5734 passed, 530 s).

Probe one: `AgentUptakeSystem.for_agent("sevoflurane")`, then 10 calls of
`advance(SimulationStep(0.1))` and 20 calls of `advance(SimulationStep(0.05))`.
The shipped code gives F_A 1.1310605640318983e-05. The mutant gives
2.4866450975939883e-05, because it advances 3 s of physics in 2 s of reported
time. The accounting check still passes, since delivered and exhausted agent
come from the same wrong propagator.

Probe two, through `SimulationState`'s public API and by the route its own
refusal message recommends ("reset it to run at a different step"): 10 steps
at 0.1 s, `reset()`, then 20 steps at 0.05 s. The mutant gives F_A
1.1310605640318981e-05, against 2.8943041009819916e-06 for a fresh
`SimulationState` taking the same 20 steps. That is 3.9 times too high, while
`elapsed_s` reads 1.0 s for 2.0 s of physics. `SimulationState.reset()` calls
`uptake_system.reset()`, which keeps the cached propagator.

Why no test sees it: every reference and integration test builds a fresh
system for each step size (for example `_run_shipped` in
`tests/reference/test_coupled_dynamics.py`), the controller tests always step
at `MAXIMUM_SIMULATION_STEP_S`, and `SimulationState` refuses a step change in
the middle of a run. The cache is tested for settings changes
(`test_the_propagator_cache_key_covers_every_equation_setting`) but never for a
step change.

**Why it matters.** The interface steps at a fixed `SIMULATION_STEP_S` of
0.1 s, so a learner cannot reach this. Any future caller that varies the step
could: an adaptive step, a final partial step to land exactly on a mark, or a
notebook. Every compartment value it reported for an instant would belong to a
later instant, and no guard or accounting check would fire.

**Where.** `src/anesthesia_sim/core/uptake_system.py` (`_propagator_for`,
`_propagator_cache_key`); `src/anesthesia_sim/core/simulation.py`
(`SimulationState.reset`); the uptake-system unit tests.

**Recommended test.** Use the semigroup property of the exact solution,
exp(A x 0.1) = exp(A x 0.05)^2, which does not depend on the cache. Build
`halves` and `whole` with `AgentUptakeSystem.for_agent("sevoflurane")`. Step
both 600 times with `SimulationStep(0.1)`. Then advance `halves` twice with
`SimulationStep(0.05)` and `whole` once with `SimulationStep(0.1)`. Assert each
entry of `halves.state_vector()` equals the matching entry of
`whole.state_vector()` with `pytest.approx(rel=1e-12, abs=1e-18)`. The worst
relative difference on the shipped code was 5.4e-16. Also add a
`SimulationState` test: reset, then run at a new step, and compare with a
fresh run.

**Done when.** A test fails under the cache-key mutant and passes on the
shipped code.

**Related.** `PL-5BD7` (ready) is about the numeric types inside the same
cache key, not about the step.

**Provenance.** A read-only test-effectiveness audit on 2026-10-17 found this.
The audit ran mutation testing with mutmut 3.8.0 over `core/` and four
presentation modules against the 33 simulator unit-test files (at
`b9b3c812`). It ran each real-gap survivor against the whole 5734-test
simulator suite (at `25ef454b`). It also used fault injection, stored-value
perturbation, oracle classification and regression-test replay, and an
adversarial second agent verified each finding. Its scratch files are not
durable, so the evidence is written out above. Symbols re-checked against
`9ea87a3c`.

**Fail-before, 2026-10-17.** Two tests. In
`tests/unit/test_matrix_exponential.py`,
`test_a_step_size_change_within_one_system_obeys_the_semigroup_property`
steps two sevoflurane systems 600 times at 0.1 s, then steps one of them
twice at 0.05 s and the other once at 0.1 s, and compares their state
vectors at `rel=1e-12`. In `tests/unit/test_simulation.py`,
`test_a_run_reset_to_a_new_step_matches_a_fresh_run_at_that_step` takes ten
0.1 s steps, resets, takes twenty 0.05 s steps, and compares the elapsed time
and `capture_state()` with a fresh run that took only the twenty. Both pass
on the shipped code, where the worst relative difference in the first is
5.4e-16. With the audit's mutant applied by
`sed -i 's/key = self._propagator_cache_key(simulation_step_s)/key = self._propagator_cache_key(None)/' src/anesthesia_sim/core/uptake_system.py`,
the command `uv run pytest -q -p no:randomly tests/unit/test_matrix_exponential.py::test_a_step_size_change_within_one_system_obeys_the_semigroup_property tests/unit/test_simulation.py::test_a_run_reset_to_a_new_step_matches_a_fresh_run_at_that_step`
exits 1 with both failed. The first fails with
`comparison failed. Mismatched elements: 6 / 9` and
`Max relative difference: 0.0044518725238513746`; its alveolar fraction is
0.003342337705568135 against 0.0033364819833999622. The second fails with
`Differing attributes: ['circuit', 'alveoli', 'patient', 'agent_simulation_validator']`;
under the mutant the reset run's alveolar fraction is 1.1310605640318981e-05
against the fresh run's 2.8943041009819916e-06, 3.9 times too high, while both
report 1.0 s. The mutant was then reverted with `git checkout`.
