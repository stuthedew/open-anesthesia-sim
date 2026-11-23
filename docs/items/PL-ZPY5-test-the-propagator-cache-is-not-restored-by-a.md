---
id: PL-ZPY5
title: test_the_propagator_cache_is_not_restored_by_a_rollback changes no setting between the capture, the restore and the second step, so the same propagator applies under any cache behaviour and the test cannot fail, though its docstring says it shows the cache exemption is safe
priority: P3
effort: S
status: done
classes: test
feature: replay-findings
touches: tests/unit/test_state_capture.py
added: 2026-10-25
closed: 2026-11-22
pr: 2258
payoff: the test that justifies keeping the propagator cache out of the captured state can fail when the cache is wrong
tests: tests/unit/test_state_capture.py::test_a_rollback_across_a_setting_change_rebuilds_the_propagator
---

**Problem.** The test (`tests/unit/test_state_capture.py`) captures a state, steps, restores and steps again, with no setting changed. A cache that never rebuilds, or one that capture or restore wrongly clears, gives the same result. So the test cannot tell correct code from wrong code.

**Why it matters.** It claims to justify keeping `_propagator` and `_propagator_key` out of `AgentUptakeSystemState`. To discriminate, it should change a setting after the capture, restore, step, and compare with a freshly built system stepped the same way. The nearby `test_a_step_after_a_setting_moved_propagates_with_the_new_matrix` covers a setting change but not a rollback.

**Done when.** `tests/unit/test_state_capture.py` has `test_a_rollback_across_a_setting_change_rebuilds_the_propagator`, which changes a setting after the capture, restores, steps, and compares with a freshly built system stepped the same way, so a cache that is never rebuilt fails it. The old test is removed or folded into it.

**Found by.** `PL-TBQS` reviewer replay on #376, finding r03 F2. Checked against main on 2026-10-25 by reading the test.

**Checked 2026-11-22** against `d4e8200`: still applies. `test_the_propagator_cache_is_not_restored_by_a_rollback` in `tests/unit/test_state_capture.py` still changes no setting between the capture, the restore and the second step. No test named `test_a_rollback_across_a_setting_change_rebuilds_the_propagator` exists.

**Done 2026-11-22.** `test_a_rollback_across_a_setting_change_rebuilds_the_propagator` replaces the old test. It changes the cardiac output after the capture, restores, steps, and compares the state with a system that has never stepped, given the new setting and the captured state, so it holds no cached propagator. It also checks that a restore with no setting changed keeps the cached propagator. Changing `_step_propagator` so that it never rebuilds a cached propagator makes the test fail. Documents checked for the old test's name or the cache exemption: `docs/MODEL.md`, `docs/VERIFICATION.md`, `docs/PARAMETERS.md`, `docs/INTERFACE.md`, `docs/ARCHITECTURE.md`; none names either.
