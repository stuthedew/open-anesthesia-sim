---
id: PL-8LZS
title: control_timeline.ControlAdjustment.unit is a second copy of CONTROL_INPUT_UNITS that nothing reads, since format_adjustment takes each value's unit from the control
status: untriaged
feature: one-source-of-truth
added: 2026-11-23
filed-pr: 2281
---

**Problem.** control_timeline.ControlAdjustment.unit is a second copy of CONTROL_INPUT_UNITS that nothing reads, since format_adjustment takes each value's unit from the control

**What happens.** `ControlAdjustment` in `src/anesthesia_sim/app/control_timeline.py` stores a `unit` for each adjustment, copied from `CONTROL_INPUT_UNITS[control]` when `group_adjustments` builds it. Nothing in `src/` reads the field: `format_adjustment` writes each value through `format_control_value`, which takes the unit from the control. Two mutants of `group_adjustments` that change the stored unit (15 and 34) survived the 2026-11-23 whole run (`PL-00Y5`), and no test can tell them apart from the original through any reader in `src/`.

**Why it matters.** A second copy of a fact the code already holds can disagree with the first, and a later reader could take the unit from the record instead of from the control.

**What to do.** Remove the field, and the `unit=` argument from each place that builds a `ControlAdjustment`: `group_adjustments` and its helper in `control_timeline.py`, `tests/integration/test_qt_chart.py`, `tests/unit/test_supported_range_edges.py`, `tests/unit/test_chart_frame.py` and `tests/unit/test_control_timeline.py`.
