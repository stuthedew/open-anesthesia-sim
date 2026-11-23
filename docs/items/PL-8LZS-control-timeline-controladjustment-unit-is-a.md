---
id: PL-8LZS
title: control_timeline.ControlAdjustment.unit is a second copy of CONTROL_INPUT_UNITS that nothing reads, since format_adjustment takes each value's unit from the control
priority: P3
effort: S
status: done
classes: defect
feature: one-source-of-truth
touches: src/anesthesia_sim/app/control_record.py, src/anesthesia_sim/app/control_timeline.py, tests/integration/test_qt_chart.py, tests/unit/test_chart_frame.py, tests/unit/test_control_timeline.py, tests/unit/test_supported_range_edges.py
added: 2026-11-23
closed: 2026-11-23
pr: 2302
filed-pr: 2281
payoff: each control's unit has one home, so the control-change list, the slider label and the recorded change cannot name different units
tests: tests/unit/test_control_timeline.py::test_each_line_states_the_unit_the_control_table_gives_it, tests/unit/test_control_timeline.py::test_a_control_given_a_unit_no_formatter_writes_is_refused
---

**Problem.** control_timeline.ControlAdjustment.unit is a second copy of CONTROL_INPUT_UNITS that nothing reads, since format_adjustment takes each value's unit from the control

**What happens.** `ControlAdjustment` in `src/anesthesia_sim/app/control_timeline.py` stores a `unit` for each adjustment, copied from `CONTROL_INPUT_UNITS[control]` when `group_adjustments` builds it. Nothing in `src/` reads the field: `format_adjustment` writes each value through `format_control_value`, which takes the unit from the control. Two mutants of `group_adjustments` that change the stored unit (15 and 34) survived the 2026-11-23 whole run (`PL-00Y5`), and no test can tell them apart from the original through any reader in `src/`.

**Why it matters.** A second copy of a fact the code already holds can disagree with the first, and a later reader could take the unit from the record instead of from the control.

**What to do.** Remove the field, and the `unit=` argument from each place that builds a `ControlAdjustment`: `group_adjustments` and its helper in `control_timeline.py`, `tests/integration/test_qt_chart.py`, `tests/unit/test_supported_range_edges.py`, `tests/unit/test_chart_frame.py` and `tests/unit/test_control_timeline.py`.


**Done when.** `ControlAdjustment` has no `unit` field, nothing in `src/` or `tests/` passes one, and every value in an adjustment is still written with the unit `format_control_value` takes from its control.

**Generator check.** A one-off. The fact misread is each control's unit, whose home is `CONTROL_INPUT_UNITS`. The adjustment record held a copy that nothing read, since `format_adjustment` takes the unit from the control. No head's `misread:` names a value copied into a record that the display builds.

**Done 2026-11-23.** The field, its three writes in `app/control_timeline.py` and the import it needed are gone, and the tests that built adjustments, in `tests/unit/test_control_timeline.py`, `tests/unit/test_chart_frame.py`, `tests/unit/test_supported_range_edges.py` and `tests/integration/test_qt_chart.py`, no longer pass a unit. Those tests and `tests/unit/test_dashboard_frame.py` pass, so every adjustment still prints its unit. `ControlChange.unit` in `app/control_record.py` stays. It is the recorded timeline's own field, which `tests/integration/controller/test_controller_control_timeline.py` describes as the record a stored run would carry, so it is part of what a run records rather than a copy made for display. Documents checked: `docs/INTERFACE.md` and `docs/ARCHITECTURE.md` (neither names the field).

**Blind review, 2026-11-23.** One pass. It found that the unit a learner reads on each line of the control-change list still did not come from `CONTROL_INPUT_DISPLAY_UNITS`. `format_control_value` chose its formatter by testing for the delivered dial and printed every other control as a flow, so a change to one control's unit in that table would have moved the slider's label and the recorded change and left the line in L/min. It also found that the comment above the table still said a displayed line reads its unit from the change that produced it, which this item made false. `format_control_value` now takes the control's unit from the table, formats a concentration or a flow from it, and refuses any other unit with a `ValueError` that names the control and the unit. `tests/unit/test_control_timeline.py::test_each_line_states_the_unit_the_control_table_gives_it` checks every control's line against the table's label, and `test_a_control_given_a_unit_no_formatter_writes_is_refused` checks the refusal. The comment now says that a displayed line takes its unit from the table through `format_control_value`.
