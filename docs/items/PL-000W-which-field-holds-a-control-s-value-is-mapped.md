---
id: PL-000W
title: Which field holds a control's value is mapped twice: controller._control_value maps each ControlInput to an UptakeEquationSettings field, and dashboard_frame's flows dict maps three of them to the run's displayed settings, so a fifth control has to be added to both
priority: P1
effort: S
status: ready
classes: defect, safety
feature: one-source-of-truth
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/dashboard_frame.py, tests/unit/test_dashboard_frame.py
added: 2026-10-26
payoff: a new control reaches the settings readouts and the control-change record from one map, so a readout cannot silently miss or misread it
verify: grep -q 'def test_every_control_input_reads_one_settings_field' tests/unit/test_dashboard_frame.py
---

**Problem.** Which field holds a control's value is mapped twice: controller._control_value maps each ControlInput to an UptakeEquationSettings field, and dashboard_frame's flows dict maps three of them to the run's displayed settings, so a fifth control has to be added to both

**Evidence.** Found on 2026-10-26 by the test-strength review of `PL-ZR49`'s change. `_control_value` in `src/anesthesia_sim/app/controller.py` was added by `PL-ZR49` and covers all four `ControlInput` members, over `UptakeEquationSettings`. The `flows` dict in `dashboard_frame`'s readout builder dates from the PySide6 port (`ae8fc7bc`, 2026-09-15). It covers the three flows over the run's displayed settings, and the delivered concentration is read beside it as a fraction. The two records hold the same values under the same field names, apart from the delivered concentration's unit, but nothing makes a new control appear in both.

**Reproduced 2026-10-31.** `_control_value` in `app/controller.py` matches all
four `ControlInput` members to `UptakeEquationSettings` fields, and the `flows`
dict in `app/dashboard_frame.py` lists three of the same members against the
settings record again. Nothing ties the two together.

**Why it matters.** The settings readouts show the flows a run is running
under, which a learner reads as the run's settings. A fifth control added to
one map and not the other would show a missing or wrong readout beside correct
concentrations. `CLAUDE.md`'s rule that a shared fact has one source of truth
is the rule each copy breaks, even while the copies agree.

**Done when.** One function or table states, for each `ControlInput`, which settings field holds its value, and both readers use it. Or the item records why the two records need different maps.

**Generator check.** One-off. The fact is which settings field holds each
control's value, and no head's `misread:` states it. `PL-40SJ`'s fact is a
named constant's value, which is narrower (`PL-R4Y2`'s triage, 2026-10-31).
