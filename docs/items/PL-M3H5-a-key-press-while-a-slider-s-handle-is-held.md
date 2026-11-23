---
id: PL-M3H5
title: A key press while a slider's handle is held applies the value at once, while the chart still says 'Preview: ... not applied' until release; ignore keys while the handle is held, or end the preview when a key applies (found by the PL-57LD review, flow slider at 4.0 L/min, Right while holding)
priority: P1
effort: S
status: done
classes: defect, safety
feature: interface-matches-its-spec
touches: src/anesthesia_sim/app/qt_widgets.py
added: 2026-11-22
closed: 2026-11-23
pr: 2309
payoff: the chart never labels as not applied a setting the run has already applied
tests: tests/integration/test_qt_widgets.py::test_a_key_or_wheel_while_the_thumb_is_held_applies_nothing
---

**Problem.** A key press while a slider's handle is held applies the value at once, while the chart still says 'Preview: ... not applied' until release; ignore keys while the handle is held, or end the preview when a key applies (found by the PL-57LD review, flow slider at 4.0 L/min, Right while holding)

**Why it matters.** The chart says "Preview: ... not applied" for a value that is already applied. A learner who reads the label believes the run is still on the old setting, which is a wrong state shown beside a clinical value, so the safety-critical standard applies.

**Done when.** A test holds a slider's handle, presses an arrow key, and shows that the chart never labels as not applied a value that the run has applied. Which of the two fixes is taken, and the platform convention it follows, is recorded here.

**Generator check.** A one-off: the slider's key path and its drag path each decide whether a value is applied, and only the drag path ends the preview.

**Reproduced 2026-11-23.** `_SettingSlider.keyPressEvent` in `src/anesthesia_sim/app/qt_widgets.py` passes every key to `QSlider.keyPressEvent` whether or not the handle is down.

**Done 2026-11-23.** The first of the two fixes: while a pointer holds a
setting slider's handle, a key press or a wheel notch on that slider does
nothing, so the drag stays the one input and its release applies the value
once. The second fix, ending the preview when a key applies, was not taken,
because it would split one held drag into a key adjustment and a drag that
resumes from a value the pointer is not at. The convention followed is the one
a drag-and-drop library documents for a mouse drag, that standard keys do not
act while the drag is under way (react-beautiful-dnd, `docs/sensors/mouse.md`,
read 2026-11-23). The test holds the handle at 4.0 L/min, presses Right and
turns the wheel, and checks that nothing is applied until the release.

Run against the code before the fix, with
`QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/integration/test_qt_widgets.py::test_a_key_or_wheel_while_the_thumb_is_held_applies_nothing`,
it fails with `assert [('preview', ... track', 4.2)] == [('preview', ...review', 4.5)]`
and "Left contains 3 more items, first extra item: ('preview', 4.1)".

Docs checked: `docs/INTERFACE.md` § on setting sliders and the preview now
states the rule; § "A preview of an unapplied setting" needed no change.
