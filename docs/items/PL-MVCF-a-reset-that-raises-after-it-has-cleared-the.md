---
id: PL-MVCF
title: A Reset that raises after it has cleared the run is not counted as a start-over, so a halt keeps the discarded run's cards under a clock of 10 min for a run at 0 s
priority: P1
effort: S
status: done
classes: safety, defect
feature: every-view-in-run-state-tests
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/controller.py, tests/integration/test_failed_start_over.py
added: 2026-11-11
closed: 2026-11-11
pr: 2138
payoff: after a failed Reset the screen withholds the discarded run's values instead of showing them as the current run's
verify: grep -rq 'def test_a_reset_that_raises_after_clearing_the_run_withholds_every_value' tests/
---

**Problem.** A Reset that raises after it has cleared the run is not counted as a start-over, so a halt keeps the discarded run's cards under a clock of 10 min for a run at 0 s

**Found by** the lifecycle review of `PL-RF2S`'s first pull request, on 2026-11-11. The fault is on `main` as well.

**Scenario, reproduced.** A run at 10 minutes, paused. `SimulationController.reset()` raises after it has cleared the state (injected at `_note_recorded_settings`), and frames fail. The learner presses Reset. The run now stands at 0.0 s, failed. The panel shows:

```
cards: ('Simulated time', '10m', ...), ('Circuit', '1.61%', '0.80 ×MAC'), ...
accounting: ('Valid', ..., 'Delivered: 0.8 L ...')
banner: ... the chart and the readouts show the last frame drawn before it stopped, and the run itself stands at its last completed step. Reset was refused ...
```

With frames working, the panel recovers: the next frame draws 0 s and 0.00%.

**Cause.** `RunView._reset_now` and `_announce_the_start_over` advance the panel's count of start-overs (`_case`) only after `SimulationController.reset()` returns. `reset()` calls `self._state.reset()` before its last statements, so a raise after that point leaves a cleared run that the panel still counts as the run the last frame drew. `halted_run` then keeps that frame's values.

**Reach.** It needs two faults at once: a Reset that raises part-way, and frames that fail.

**Suggested fix.** Count the start-over before the controller is asked to reset, or in a `finally`, so that a Reset that raises is treated as a start-over and the values are withheld.

**Done when** a Reset that raises after clearing the run leaves every compartment value withheld on a halt, and the scenario above is a test that fails first.

**Why it matters.** The halted screen shows the discarded run's values, a clock of 10 min and 1.61% in the circuit, under a run that stands at 0 s. A learner reads them as the state of the run on screen. The safety-critical standard counts a stale value shown as current as a safety failure, however unlikely the two faults together are.

**Generator check.** An instance of the fact that `PL-RF2S` states, and `PL-RF2S` is still open: which widgets state a run's current state, and that each is restated on every path that changes it. Here the path is a Reset that raises part-way. `PL-RF2S` is in flight on another branch, so adding this item to its `root-cause-of:` is left to that branch.

**Built 2026-11-11.** `SimulationController` now counts each time it begins to discard its run's state, in `runs_discarded`. `reset()` raises the count just before it clears anything past the settings read that the core can refuse, and `set_agent` just before it rebuilds the run. `RunView._reset_now` compares the count before and after `reset()`, and records the start-over when the count moved, even when `reset()` raised. The agent switch in `_start_new_case` does the same in a `finally`, because `set_agent` has the same shape. A refusal raised before anything is cleared leaves the count unchanged, so that halt still shows the last frame, which describes the run that still stands. The count is recorded at the moment the controller knows it, instead of being inferred from where an exception came from.

`tests/integration/test_failed_start_over.py` holds three tests: the item's scenario (`test_a_reset_that_raises_after_clearing_the_run_withholds_every_value`), its agent-change twin, and a refused Reset that must keep the 10 min frame. They are in a file of their own because `PL-RF2S`'s branch is rewriting `tests/integration/test_simulation_view.py`. On the code before the fix, the first fails with `assert '10m' == '—'` and the agent-change test with `assert '0s' == '—'` (run with `git stash -- src`).

**Blind review, one pass, two should-fix findings, both fixed.** First, `set_agent` raised the count before `_build_state`, which reads the new agent's parameters and applies the carried-over settings before it writes anything to the controller. A refusal there left the run intact with the count moved, so the switch was announced as a start-over and dropped every branch. The count now goes up inside `_build_state`, after the new system is built and before the first assignment, and `test_an_agent_change_refused_before_it_replaces_the_run_keeps_the_last_frame` holds it (on the code before this fix it fails with the cards withheld, `('—', ...) == ('0s', ...)`). Second, a Reset that raised after clearing kept the refused-Reset way out, so the banner said Reset was refused, over a run that had started over. That path now halts as a failure: the banner names the failure and Reset as the way out, and a refused-setting sentence about the discarded run is cleared. The item's own test now asserts that the banner names the failure and does not carry the refused-Reset text. A `SimulationConfigurationError` raised after an agent change began to replace the run would still reach the reader as a refused setting. With a freshly built system nothing after that point raises one, so it is noted here and not coded.
