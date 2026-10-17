---
id: PL-QJXS
title: No test compares an agent-switched run with a fresh run of the new agent, so a set_agent that keeps the previous agent's patient compartments passes the whole suite while a run labelled Desflurane computes with sevoflurane's blood:gas 0.65 and shows alveolar 2.95% (0.49 xMAC) at 5 min against 3.59% (0.60 xMAC)
priority: P1
effort: S
status: done
classes: safety, test
feature: tests-detect-wrong-values
touches: tests/integration/test_controller.py, tests/integration/test_simulation_view.py, tests/unit/test_dashboard_frame.py
added: 2026-10-17
closed: 2026-10-17
pr: 1499
payoff: a run switched to another agent is proved to compute with that agent alone, so a value shown under a correct agent name but computed from the previous agent fails the suite
verify: grep -q 'def test_an_agent_switch_runs_exactly_as_a_fresh_run_of_that_agent' tests/integration/test_controller.py
---

**Problem.** No test compares an agent-switched run with a fresh run of the new agent, so a set_agent that keeps the previous agent's patient compartments passes the whole suite while a run labelled Desflurane computes with sevoflurane's blood:gas 0.65 and shows alveolar 2.95% (0.49 xMAC) at 5 min against 3.59% (0.60 xMAC)

**Severity: safety.** A wrong clinical value under a correct agent label, with
nothing on screen to say so. Audit finding CMP-1, confirmed by the adversarial
verifier.

**Evidence.** Fault injection I9: in `SimulationController._build_state`
(`src/anesthesia_sim/app/controller.py`), right after
`uptake_system = AgentUptakeSystem.for_agent(agent_id)`, add
`if hasattr(self, "_state"): uptake_system.patient = self._state.uptake_system.patient; uptake_system.patient.reset()`.
The whole simulator suite passed (2969 tests then, 402 s). The verifier re-ran
the 701 tests that can reach `set_agent`, `_select_agent` or the presentation
wiring (`tests/integration`, `tests/unit/test_dashboard_frame.py`,
`tests/unit/test_chart_frame.py`): 701 passed, with a sentinel test confirming
pytest imported the injected source.

Measured effect, sevoflurane switched to desflurane, then 5 min at
desflurane's 1 MAC dial, labelled "Desflurane": alveolar 2.95% (0.49 xMAC),
F_A/F_I 0.676, blood:gas 0.65. A fresh desflurane run gives 3.59%
(0.60 xMAC), 0.771, blood:gas 0.42. The wrong value is 18% below the right
one (the audit's first "22%" was the right value measured against the wrong
one).

Why nothing catches it. Only `tests/integration/test_controller.py` (13
calls) and `tests/integration/test_simulation_view.py` (1) call
`set_agent(`. Every assertion after a switch checks the agent id, name, dial,
vaporizer maximum, zeroed stores, timeline, failure or limit state, or marks.
None compares compartment parameters or values with a fresh run.
`test_the_end_to_end_mac_path_reaches_the_panel_from_a_real_run` in
`tests/unit/test_dashboard_frame.py` builds a fresh desflurane controller (no
switch), takes its expected value from `format_mac_multiple(snapshot...)`, and
then asserts only 0 < MAC < 1. The readouts, the chart and the run definition
all derive from the same system, so every consistency test passes on a system
that is wrong but consistent.

One existing guard would see it, and no test uses it.
`SimulationController._disagreements_with`, called from `_branch_from`,
re-reads the agent's data file and refuses a branch whose settings differ.
Under I9, `resumed_at(...)` on a switched run raises
`SimulationConfigurationError` ("blood_gas_partition_coefficient is 0.65 in
this run ..."). No test branches after a switch, and a run nobody branches
shows the wrong values with no sign.

**Why it matters.** A refactor of `set_agent` that reuses or partly rebuilds
the compartments ("the flows are kept, so keep the patient") would show one
agent's uptake kinetics under another agent's name and MAC: 18% low for
desflurane at 5 min, and no test would fail.

**Where.** `src/anesthesia_sim/app/controller.py` (`_build_state`,
`set_agent`); `tests/integration/test_controller.py`;
`tests/integration/test_simulation_view.py`; `tests/unit/test_dashboard_frame.py`.

**Recommended test.** In `tests/integration/test_controller.py`, something
like `test_an_agent_switch_runs_exactly_as_a_fresh_run_of_that_agent`,
parametrized over every ordered agent pair. Build a controller on agent A
with a non-default circuit and flows, advance 60 s, `set_agent(B)`, start and
advance 300 s. Do the same with `SimulationController(agent_id=B)` and the
same settings. Assert `equation_settings()` equal before stepping, then all
six fractions and both accumulators equal with `==` (not approx) afterwards.
Add:

- the UI-path variant in `test_simulation_view.py`, through `_select_agent`
  and the confirmation;
- a "switch, run, branch" test, which the existing branch refusal would catch;
- one literal displayed string per agent, so the end-to-end test stops
  comparing the formatter with itself. For desflurane at 300 s on the
  protocol above the audit measured '3.59%' and '0.60 ×MAC'; re-measure them
  when the test is written.

**Done when.** Injection I9 fails at least one test, and every ordered agent
pair is compared element by element with a fresh run of the new agent.

**Related.** `PL-JPS2` (the same switch path, for the MAC-awake band rather
than the compartments). `PL-1YDD` (a halt right after `set_agent` showing two
agents) is a different defect on the same path.

**Provenance.** A read-only test-effectiveness audit on 2026-10-17 found this.
The audit ran mutation testing with mutmut 3.8.0 over `core/` and four
presentation modules against the 33 simulator unit-test files (at
`b9b3c812`). It ran each real-gap survivor against the whole 5734-test
simulator suite (at `25ef454b`). It also used fault injection, stored-value
perturbation, oracle classification and regression-test replay, and an
adversarial second agent verified each finding. Its scratch files are not
durable, so the evidence is written out above. Symbols re-checked against
`9ea87a3c`.

**Done, 2026-10-17.** Three tests compare a switched run with a run built
directly with the new agent and the same settings, using `==` on the whole
snapshot:

- `test_an_agent_switch_runs_exactly_as_a_fresh_run_of_that_agent` and
  `test_a_switched_run_branches_as_a_fresh_run_of_that_agent_does` in
  `tests/integration/test_controller.py`, over all six ordered agent pairs.
  The previous agent's run has non-default circuit, flows and cardiac output,
  all different from each other, 90 s of uptake and a dial change before the
  switch.
- `test_an_agent_chosen_in_the_selector_runs_as_a_fresh_run_of_that_agent` in
  `tests/integration/test_simulation_view.py`, through the selector and the
  new-case dialog.

`test_each_agents_alveolar_readout_at_five_minutes_is_pinned_as_displayed` in
`tests/unit/test_dashboard_frame.py` pins each agent's alveolar readout after
5 minutes on a fresh default run: sevoflurane '0.98%' and '0.49 ×MAC',
isoflurane '0.42%' and '0.35 ×MAC', desflurane '3.59%' and '0.60 ×MAC'. The
desflurane values match the audit's measurement. They pin the model's own
output and are not a comparison with measured data.

With injection I9 applied to `_build_state`, `uv run pytest -q
tests/integration/test_controller.py -k 'agent_switch_runs_exactly or
switched_run_branches'` failed all 12 cases. The first test failed on the
opening segment, with `blood_gas_partition_coefficient=0.65` against 0.42 for
sevoflurane to desflurane. The branch test failed with
`SimulationConfigurationError: a branch at 0.0 s would be rebuilt from values
this run did not hold there`. The selector test failed on the snapshot
comparison.
