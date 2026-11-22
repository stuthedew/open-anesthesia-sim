---
id: PL-F4T4
title: The test that a refused layout leaves no widget behind counts every widget in the application, so a widget from another test that is destroyed while it runs fails it (CI on #2140, 2026-11-14: 1650 against 1666)
priority: P3
effort: S
status: done
classes: defect
touches: tests/integration/test_layout_adapter.py
deferred-from: v0.7.0 - present at the freeze, but a test that fails only by chance on a shared CI worker, with no connection to anything on the frozen list or in v0.7.0 Required scope; no learner sees it
added: 2026-11-14
closed: 2026-11-22
pr: 2224
payoff: a pull request is not failed by a widget another test destroyed, and a widget that a refused layout leaves behind is still caught
tests: tests/integration/test_layout_adapter.py::test_a_refused_layout_leaves_no_widget_behind
---

**Problem.** The test that a refused layout leaves no widget behind counts every widget in the application, so a widget from another test that is destroyed while it runs fails it (CI on #2140, 2026-11-14: 1650 against 1666)

**Seen 2026-11-14.** `tests/integration/test_layout_adapter.py::test_a_refused_layout_leaves_no_widget_behind` failed in CI part 1 on #2140 (run 43542118295, job 132284813814): `assert 1650 == 1666`. The count fell rather than rose, so no widget was left behind. Sixteen widgets from an earlier test on the same xdist worker were destroyed between the two `QApplication.allWidgets()` reads. #2140 changes only test wording files, so the failure is not its own. A fix could count only widgets whose parent chain reaches the layout under test, or compare the sets of widgets before and after and look only for new ones.

**Checked 2026-11-22.** `test_a_refused_layout_leaves_no_widget_behind` in `tests/integration/test_layout_adapter.py` still compares `len(QApplication.allWidgets())` before and after the refused layout. So a widget that other code destroys in between changes the count. The test was the same at the freeze.

**Why it matters.** The test can fail a pull request that did not cause the failure, as it did on #2140, and a session then spends a run and a diagnosis on it. It also checks less than its name says: a refused layout that left one widget behind would pass while another test's widget was destroyed.

**Done when.** The test fails only for a widget that the refused layout created and left behind, and a widget destroyed by other code while it runs does not change its result.

**Generator check.** The fact misread is which widgets belong to the layout under test, as against every widget in the process. No head states it, and no other test counts `allWidgets()`. This is a one-off.

**Done 2026-11-22.** `test_a_refused_layout_leaves_no_widget_behind` now records the set of widgets before the refusal and fails only on a widget that was not in it, so another test's widget destroyed meanwhile no longer changes its result. Files checked: `docs/INTERFACE.md` and `docs/ARCHITECTURE.md` say nothing about this test.
