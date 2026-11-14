---
id: PL-F4T4
title: The test that a refused layout leaves no widget behind counts every widget in the application, so a widget from another test that is destroyed while it runs fails it (CI on #2140, 2026-11-14: 1650 against 1666)
status: untriaged
added: 2026-11-14
---

**Problem.** The test that a refused layout leaves no widget behind counts every widget in the application, so a widget from another test that is destroyed while it runs fails it (CI on #2140, 2026-11-14: 1650 against 1666)

**Seen 2026-11-14.** `tests/integration/test_layout_adapter.py::test_a_refused_layout_leaves_no_widget_behind` failed in CI part 1 on #2140 (run 43542118295, job 132284813814): `assert 1650 == 1666`. The count fell rather than rose, so no widget was left behind. Sixteen widgets from an earlier test on the same xdist worker were destroyed between the two `QApplication.allWidgets()` reads. #2140 changes only test wording files, so the failure is not its own. A fix could count only widgets whose parent chain reaches the layout under test, or compare the sets of widgets before and after and look only for new ones.
