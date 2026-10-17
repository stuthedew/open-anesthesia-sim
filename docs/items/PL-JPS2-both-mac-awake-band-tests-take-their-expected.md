---
id: PL-JPS2
title: Both MAC-awake band tests take their expected band from the snapshot under test, so a band left at the previous agent's values after an agent switch passes the whole suite and the chart would draw sevoflurane's 0.34 x MAC band under desflurane's name
priority: P1
effort: S
status: done
classes: safety, test
feature: tests-detect-wrong-values
touches: tests/integration/test_simulation_view.py, tests/integration/test_qt_chart.py
added: 2026-10-17
closed: 2026-10-17
pr: 1506
payoff: the MAC-awake band a learner reads emergence against is checked against each agent's own published values after a switch, not against the snapshot it came from
verify: grep -q 'def test_the_mac_awake_band_after_a_switch_is_the_new_agents_own' tests/integration/test_simulation_view.py
---

**Problem.** Both MAC-awake band tests take their expected band from the snapshot under test, so a band left at the previous agent's values after an agent switch passes the whole suite and the chart would draw sevoflurane's 0.34 x MAC band under desflurane's name

**Severity: safety.** A wrong population reference under the correct agent's
name, on the line a learner reads emergence against. Audit finding CMP-2,
confirmed by the adversarial verifier.

**Evidence.** Fault injection I2: in `SimulationController._build_state`,
replace `self._agent_mac_awake = agent_parameters.mac_awake` with
`self._agent_mac_awake = getattr(self, "_agent_mac_awake", agent_parameters.mac_awake)`,
so an agent switch keeps the old agent's fraction and SD. The whole simulator
suite passed (2969 tests then, 444 s). The verifier re-ran the 701 tests that
can reach the switch path: 701 passed. After a switch from sevoflurane to
desflurane the snapshot holds 0.34 / 0.05, where desflurane's own values are
0.36 / 0.063.

Both band tests read their expected value from the field under test:

- `test_the_mac_axis_and_references_follow_the_agent`
  (`tests/integration/test_simulation_view.py`) builds its expected MAC-awake
  text from `snapshot.agent_mac_awake` after `_select_agent(..., "desflurane")`.
  Only the 1 MAC divisor is a literal, `format_mac_reference("Desflurane", 6.0)`.
  That is why the matching divisor injection (I1) was caught and this one was
  not.
- `test_the_references_stand_at_the_running_agent_s_own_values_and_follow_it`
  (`tests/integration/test_qt_chart.py`) builds its band from
  `snapshot.agent_mac_awake`, and it builds a fresh controller per agent with
  `_run_with_a_dial_change(agent_id)`, so it never takes the switch path.

`test_the_screen_states_the_band_fraction_and_the_divisor_for_every_agent`
and the dashboard-frame band tests do load the data file independently, but
they also build a fresh controller for each agent.

**Why it matters.** After a sevoflurane-to-desflurane switch the chart would
state "MAC-awake desflurane = 0.34 ×MAC (2.04%)" with a band of 1.74-2.34%,
instead of 0.36 ×MAC (2.16%) and 1.78-2.54%. After a switch to isoflurane it
would draw 0.35-0.47% instead of 0.31-0.43%. The verifier checked these
against the loaded data: desflurane's true band is 1.782-2.538% and
isoflurane's 0.312-0.432%.

**Where.** `src/anesthesia_sim/app/controller.py` (`_build_state`);
`tests/integration/test_simulation_view.py`; `tests/integration/test_qt_chart.py`.

**Recommended test.** In `test_the_mac_axis_and_references_follow_the_agent`,
take the expected values from an independent
`load_agent_parameters("desflurane").mac_awake`, or the literals 0.36 and
0.063, and assert `chart.mac_awake_band()` numerically after the switch. Add
the reverse direction (desflurane to sevoflurane) and a switch to isoflurane.
In the `test_qt_chart.py` references test, use a switched controller rather
than a fresh one per agent.

**Done when.** Injection I2 fails a test, and each agent's band after a switch
into that agent is asserted against values not read from the snapshot.

**Related.** `PL-QJXS` (the same switch path, for the compartments).

**Provenance.** A read-only test-effectiveness audit on 2026-10-17 found this.
The audit ran mutation testing with mutmut 3.8.0 over `core/` and four
presentation modules against the 33 simulator unit-test files (at
`b9b3c812`). It ran each real-gap survivor against the whole 5734-test
simulator suite (at `25ef454b`). It also used fault injection, stored-value
perturbation, oracle classification and regression-test replay, and an
adversarial second agent verified each finding. Its scratch files are not
durable, so the evidence is written out above. Symbols re-checked against
`9ea87a3c`.

**Fail-before, 2026-10-17.** The expected values now come from
`load_agent_parameters` for the agent switched to, never from the snapshot
under test. `test_the_mac_axis_and_references_follow_the_agent` reads
desflurane's own file. The new
`test_the_mac_awake_band_after_a_switch_is_the_new_agents_own` in
`tests/integration/test_simulation_view.py` covers all six switches between
the three agents, and asserts the drawn band and its line of text. The
`tests/integration/test_qt_chart.py` references test now runs three switched
runs instead of a fresh controller per agent. All eight pass on the shipped
code. With injection I2 applied by
`sed -i 's/self\._agent_mac_awake = agent_parameters\.mac_awake/self._agent_mac_awake = getattr(self, "_agent_mac_awake", agent_parameters.mac_awake)/' src/anesthesia_sim/app/controller.py`,
the command
`uv run pytest -q -p no:cacheprovider tests/integration/test_simulation_view.py tests/integration/test_qt_chart.py -k "mac_awake_band_after_a_switch or mac_axis_and_references_follow or references_stand_at_the_running"`
exits 1 with all eight failed. The sevoflurane-to-desflurane line reads
`MAC-awake desflurane = 0.34 ×MAC (2.04%), band ±1 SD 1.74–2.34%` where
`MAC-awake desflurane = 0.36 ×MAC (2.16%), band ±1 SD 1.78–2.54%` was
expected. After the switch from sevoflurane to isoflurane the band is
`(0.348, 0.468)` where `(0.312, 0.432)` was expected. The injection was then
reverted with `git checkout`.
