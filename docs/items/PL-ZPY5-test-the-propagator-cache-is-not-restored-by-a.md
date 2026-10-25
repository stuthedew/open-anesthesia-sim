---
id: PL-ZPY5
title: test_the_propagator_cache_is_not_restored_by_a_rollback changes no setting between the capture, the restore and the second step, so the same propagator applies under any cache behaviour and the test cannot fail, though its docstring says it shows the cache exemption is safe
priority: P3
effort: S
status: ready
classes: test
feature: replay-findings
touches: tests/unit/test_state_capture.py
added: 2026-10-25
payoff: the test that justifies keeping the propagator cache out of the captured state can fail when the cache is wrong
verify: grep -q 'def test_a_rollback_across_a_setting_change_rebuilds_the_propagator' tests/unit/test_state_capture.py
---

**Problem.** The test (`tests/unit/test_state_capture.py`) captures a state, steps, restores and steps again, with no setting changed. A cache that never rebuilds, or one that capture or restore wrongly clears, gives the same result. So the test cannot tell correct code from wrong code.

**Why it matters.** It claims to justify keeping `_propagator` and `_propagator_key` out of `AgentUptakeSystemState`. To discriminate, it should change a setting after the capture, restore, step, and compare with a freshly built system stepped the same way. The nearby `test_a_step_after_a_setting_moved_propagates_with_the_new_matrix` covers a setting change but not a rollback.

**Done when.** `tests/unit/test_state_capture.py` has `test_a_rollback_across_a_setting_change_rebuilds_the_propagator`, which changes a setting after the capture, restores, steps, and compares with a freshly built system stepped the same way, so a cache that is never rebuilt fails it. The old test is removed or folded into it.

**Found by.** `PL-TBQS` reviewer replay on #376, finding r03 F2. Checked against main on 2026-10-25 by reading the test.
