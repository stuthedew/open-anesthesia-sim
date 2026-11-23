---
id: PL-M3H5
title: A key press while a slider's handle is held applies the value at once, while the chart still says 'Preview: ... not applied' until release; ignore keys while the handle is held, or end the preview when a key applies (found by the PL-57LD review, flow slider at 4.0 L/min, Right while holding)
priority: P1
effort: S
status: ready
classes: defect, safety
feature: interface-matches-its-spec
touches: src/anesthesia_sim/app/qt_widgets.py
added: 2026-11-22
payoff: the chart never labels as not applied a setting the run has already applied
---

**Problem.** A key press while a slider's handle is held applies the value at once, while the chart still says 'Preview: ... not applied' until release; ignore keys while the handle is held, or end the preview when a key applies (found by the PL-57LD review, flow slider at 4.0 L/min, Right while holding)

**Why it matters.** The chart says "Preview: ... not applied" for a value that is already applied. A learner who reads the label believes the run is still on the old setting, which is a wrong state shown beside a clinical value, so the safety-critical standard applies.

**Done when.** A test holds a slider's handle, presses an arrow key, and shows that the chart never labels as not applied a value that the run has applied. Which of the two fixes is taken, and the platform convention it follows, is recorded here.

**Generator check.** A one-off: the slider's key path and its drag path each decide whether a value is applied, and only the drag path ends the preview.

**Reproduced 2026-11-23.** `_SettingSlider.keyPressEvent` in `src/anesthesia_sim/app/qt_widgets.py` passes every key to `QSlider.keyPressEvent` whether or not the handle is down.
