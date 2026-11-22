---
id: PL-G2WC
title: No test checks that a value shown in compare mode sits under its own run: the readout test checks the 'Run 1' and 'Run 2' labels and never a value against the run it names
priority: P1
effort: M
status: done
classes: defect, safety
feature: every-view-in-run-state-tests
milestone: v0.6.20
touches: tests/integration
deferred-from: v0.7.0 - found by the 2026-11-10 audit after the freeze; not live: checked 2026-11-10, the audit found no value shown under the wrong run, and the gap is that no test would catch one
added: 2026-11-10
closed: 2026-11-22
pr: 2229
filed-pr: 2090
payoff: in compare mode a value shown under the wrong run's name fails a test, for every View that shows two runs
tests: tests/integration/simulation_view/test_simulation_view_run_values.py::test_each_compared_value_is_shown_under_its_own_run
reenters: PL-GTH6
---

**Problem.** No test checks that a value shown in compare mode sits under its own run: the readout test checks the 'Run 1' and 'Run 2' labels and never a value against the run it names

**Checked 2026-11-10:** `PL-GTH6` (which run a displayed value belongs to once two runs are shown) closed on 2026-10-25 with `generator: spent - no member filed since 2026-09-21 across 34 days of compare-mode changes (inferred from the store)`. It names no check. `tests/integration/test_compartment_schematic_view.py` and `tests/integration/test_agent_cost_view.py` assert the run names "Run 1" and "Run 2". The audit's reviewer reported that no test compares a displayed value with the run it sits under, for any View. The filing session confirmed the two name assertions and did not read every compare-mode test, so confirm that first.

**Why it matters.** In compare mode a learner reads two runs side by side, and a value shown under the wrong run's name is a correct number in the wrong context. The record that this cannot happen is an absence of filings.

**Done when.** A test loads two runs that differ in agent and in settings, and for every View that shows two runs checks each displayed value against the value of the run it is shown under. The Views come from the registry, as in `PL-B8DL` (the test layout built from the registry), so a new View is included without being listed.

**Generator check.** An instance of `PL-GTH6`'s fact, filed after that head closed on 2026-10-25. The head's verdict rests on no filing having arrived, not on a check.

**Checked 2026-11-22** against `d4e8200`: still applies. `test_two_runs_share_one_readout_block_whose_values_name_their_runs` in `tests/integration/simulation_view/test_simulation_view_readouts.py` still checks only that the labels read "Run 1" and "Run 2". No test in `test_simulation_view_comparison.py`, `test_simulation_view_readouts.py`, `test_compartment_schematic_view.py` or `test_agent_cost_view.py` compares a shown value with the run it sits under. `PL-RF2S` (one value for the whole screen) still has its third pull request to build, the one that makes each run's name travel with its values.

**Done 2026-11-22, in #2229 with the third pull request of `PL-RF2S`.** `test_each_compared_value_is_shown_under_its_own_run` in `tests/integration/simulation_view/test_simulation_view_run_values.py` compares a trunk and a branch that runs at a higher fresh gas flow. It shows every registered View kind in turn, and for each View that shows a block per run it checks each block's numbers against the same View on a fresh single run built with that run's settings, and that each block names its run. The two runs share one agent rather than differing in agent, as "Done when" asked, because a dashboard refuses two runs on different agents (`test_a_dashboard_refuses_two_runs_on_different_agents`). Docs checked: none describe this test.
