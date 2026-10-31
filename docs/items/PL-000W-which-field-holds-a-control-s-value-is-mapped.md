---
id: PL-000W
title: Which field holds a control's value is mapped twice: controller._control_value maps each ControlInput to an UptakeEquationSettings field, and dashboard_frame's flows dict maps three of them to the run's displayed settings, so a fifth control has to be added to both
priority: P1
effort: S
status: done
classes: defect, safety
feature: one-source-of-truth
touches: src/anesthesia_sim/app/control_record.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/dashboard_frame.py, tests/unit/test_control_record.py, tests/unit/test_dashboard_frame.py
added: 2026-10-26
closed: 2026-10-31
pr: 1898
payoff: a new control reaches the settings readouts and the control-change record from one map, so a readout cannot silently miss or misread it
verify: grep -q 'def control_value' src/anesthesia_sim/app/control_record.py && ! grep -q 'def _control_value' src/anesthesia_sim/app/controller.py && ! grep -q 'flows = {' src/anesthesia_sim/app/dashboard_frame.py && grep -q 'def test_each_control_reads_the_value_it_was_set_to' tests/unit/test_control_record.py
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

**Resolved 2026-10-31.** `control_value` in `app/control_record.py` is now the
one map from each `ControlInput` to the settings field that holds its value.
`control_record.py` already defines which controls exist and the unit of each,
and both the controller and `dashboard_frame` import it, so it was the one home
that keeps every import pointing one way. The function takes a
`ControlSettings` protocol, which both `UptakeEquationSettings` and
`RunSettings` satisfy, because they store the four values under the same field
names and in the same units. The delivered concentration is the percent
dialled in both. The controller's `_control_value` is deleted, and
`setting_readouts` reads all four values through `control_value`, so its
`flows` dict is gone.

The match in `control_value` has no default case. A fifth `ControlInput`
member without a case makes `mypy` fail with "Missing return statement".
That was checked by adding a member temporarily and running `uv run mypy` on
the module. So a fifth control cannot reach a readout or a recorded change
without naming its field.

`tests/unit/test_control_record.py` checks each control against a literal
value on both records, with four distinct values. Making `control_value` read
the alveolar ventilation for the fresh gas flow fails that test, and also
`test_refresh_view_formats_every_concentration_metric` in
`tests/unit/test_dashboard_frame.py`, which shows that the readouts read
through the one map.

The commissioned `verify:` grepped `tests/unit/test_dashboard_frame.py` for a
test name chosen before the work. The test the work needed checks the map on
both records, so it belongs with `control_record.py`, in a module of its own.
The `verify:` now greps for what the work added and removed.
