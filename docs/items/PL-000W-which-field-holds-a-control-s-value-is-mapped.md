---
id: PL-000W
title: Which field holds a control's value is mapped twice: controller._control_value maps each ControlInput to an UptakeEquationSettings field, and dashboard_frame's flows dict maps three of them to the run's displayed settings, so a fifth control has to be added to both
status: untriaged
feature: one-source-of-truth
added: 2026-10-26
---

**Problem.** Which field holds a control's value is mapped twice: controller._control_value maps each ControlInput to an UptakeEquationSettings field, and dashboard_frame's flows dict maps three of them to the run's displayed settings, so a fifth control has to be added to both

**Evidence.** Found on 2026-10-26 by the test-strength review of `PL-ZR49`'s change. `_control_value` in `src/anesthesia_sim/app/controller.py` was added by `PL-ZR49` and covers all four `ControlInput` members, over `UptakeEquationSettings`. The `flows` dict in `dashboard_frame`'s readout builder dates from the PySide6 port (`ae8fc7bc`, 2026-09-15). It covers the three flows over the run's displayed settings, and the delivered concentration is read beside it as a fraction. The two records hold the same values under the same field names, apart from the delivered concentration's unit, but nothing makes a new control appear in both.

**Done when.** One function or table states, for each `ControlInput`, which settings field holds its value, and both readers use it. Or the item records why the two records need different maps.
