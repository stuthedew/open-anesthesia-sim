---
id: PL-0T2H
title: Arrow-key, wheel and track-click steps on one dial are joined into one adjustment, so the chart marks only the first step and docs/INTERFACE.md says each step is an adjustment of its own: decide which a learner sees
priority: P2
effort: M
status: done
classes: defect
feature: interface-matches-its-spec
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/chart_frame.py, docs/INTERFACE.md, tests/integration/controller/test_controller_control_timeline.py
blocked-by: PL-Z6C8
deferred-from: v0.7.0 - filed on 2026-11-21, after the gate froze; it builds after the whole-second stepping work, which changes when a setting takes effect
added: 2026-11-21
closed: 2026-11-22
pr: 2228
payoff: A learner who steps a dial up and later back with the keys sees a mark on the chart at each change
tests: tests/integration/controller/test_controller_control_timeline.py::test_steps_of_one_control_at_three_instants_are_three_adjustments, tests/integration/simulation_view/test_simulation_view_controls.py::test_each_arrow_key_step_at_a_new_instant_is_marked_and_listed
---

**Problem.** Arrow-key, wheel and track-click steps on one dial are joined into one adjustment, so the chart marks only the first step and docs/INTERFACE.md says each step is an adjustment of its own: decide which a learner sees

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). `docs/INTERFACE.md` § "The control-input timeline" says "A key press, one notch of the scroll wheel or a click on the slider away from its handle is a single input, and is an adjustment of its own." The code joins them. The interface declares the start of an adjustment only when the handle is pressed (`ParameterSlider.__init__` in `app/qt_widgets.py` connects `sliderPressed` to `adjustment_started`). `SimulationController._record_in_timeline` in `app/controller.py` opens a new adjustment only when the changed control differs from the one already open, whatever simulated time has passed. A chart marks one instant for each adjustment, its start (`_run_frame` in `app/chart_frame.py`).

The script below starts a run and presses the Right arrow on the fresh gas flow slider at 10 s, 40 s and 100 s. Run it from the repository root with `QT_QPA_PLATFORM=offscreen PYTHONPATH=. uv run python keys.py`.

```python
import sys
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from anesthesia_sim.app.controller import SimulationController
from tests.integration.simulation_view.simulation_view_support import _shown_view, _dials, _advance

app = QApplication.instance() or QApplication(sys.argv)
controller = SimulationController()
view = _shown_view(app, controller)
run = view.runs[0]
controller.start()
_advance(controller, 10.0)
slider = _dials(run)._fresh_gas_flow_slider.slider
slider.setFocus()
QTest.keyClick(slider, Qt.Key.Key_Right)
_advance(controller, 30.0)
QTest.keyClick(slider, Qt.Key.Key_Right)
_advance(controller, 60.0)
QTest.keyClick(slider, Qt.Key.Key_Right)
view.present(False)
print(repr(run._control_timeline_text.text()))
for c in controller.snapshot().control_timeline:
    print(c.elapsed_s, c.adjustment, c.control.value, c.previous_value, c.new_value, c.unit)
from tests.integration.simulation_view.simulation_view_support import _concentration, _wash_in
print("concentration chart marks at:", _concentration(view).chart.control_mark_times(0))
print("F_A/F_I chart marks at:", _wash_in(view).chart.control_mark_times(0))
print("unmarked notes:", [w.text() for w in _concentration(view).unmarked_changes.holder.findChildren(type(run._control_timeline_text)) if w.text()])
print("run segments open at:", [float(s.opening.instant_s) for s in controller.run_segments])
```

Output:

```
'10s–1m40s · Fresh gas flow 4.0 L/min -> 4.3 L/min (3 settings)'
10.0 1 fresh_gas_flow 4.0 4.1 L/min
40.0 1 fresh_gas_flow 4.1 4.2 L/min
100.0 1 fresh_gas_flow 4.2 4.3 L/min
concentration chart marks at: (10.0,)
F_A/F_I chart marks at: (10.0,)
unmarked notes: []
run segments open at: [0.0, 10.0, 40.0, 100.0]
```

Three wheel notches and three clicks on the track gave the same single line under Qt's Fusion style. `test_consecutive_changes_to_one_control_are_one_adjustment` in `tests/integration/controller/test_controller_control_timeline.py` checks the joining at the controller, and no test presses a key on a slider. `PL-5B1N` (a drag applies once, at release) recorded that "the adjustment grouping stays for keyboard runs". The docstring of `SimulationController.begin_control_adjustment` repeats the document's sentence.

**Why it matters.** A learner who steps a dial up with the arrow keys at one minute and steps it back at ten sees one dashed line on the chart, at one minute. The curves bend at ten minutes with no mark, and the count of unmarked changes does not include the step. The section's own reason for marking changes is that "A learner who cannot see where they dialled back cannot read their own experiment."

**Decision needed.** When a learner changes one dial several times with the arrow keys, the scroll wheel or clicks on the track, without touching another control in between, what does the chart mark? The choice is the owner's because it changes which of a learner's own changes the chart shows.

- **A. Each step that takes effect at a different simulated instant is its own adjustment.** The chart draws a dashed line at each, and the list of control changes shows one line for each. Steps made while the run is paused, or inside one simulation step, take effect at one instant and stay one adjustment with one line. In the example above the learner sees three marks, at 10 s, 40 s and 1 min 40 s.
- **B. Keep the joining, and correct the document.** The learner sees one mark at the first step and one line that covers the whole interval, "10s–1m40s · Fresh gas flow 4.0 L/min -> 4.3 L/min (3 settings)". Later steps change the curves with no mark.

**Recommendation: A.** It is what the document already requires, and it marks the dial-back that the section exists to show. It costs more dashed lines when a learner holds an arrow key down while the run plays. The chart's existing rule for crowded marks covers that case.

**Decided 2026-11-21: A, as an obvious call in the round.** `docs/INTERFACE.md` § "The control-input timeline" already requires it: "A key press, one notch of the scroll wheel or a click on the slider away from its handle is a single input, and is an adjustment of its own." So the code is the defect, and the document is not changed. B would lower a requirement of the document to match the code. The coordinator of the v0.7.0 project asked for the call to be taken on this ground on 2026-11-21. The project owner was told in the thread the same day and can overrule it. The session took the call, so it is not recorded as the owner's.

[superseded 2026-11-21] **Waits on the whole-second stepping build.** `PL-SZ6G`, `PL-MH9J`, `PL-FST0` and `PL-Z6C8` change when a setting takes effect, and they were in flight on `origin/claude/project-thread-er38tc` on 2026-11-21. This item is blocked on the last of them, `PL-Z6C8`, and it is deferred from v0.7.0's gate because it was filed after that gate froze.

**Generator check.** One-off. The fact is what one adjustment is. The document states it per input, and `SimulationController._record_in_timeline` opens an adjustment per control. `test_consecutive_changes_to_one_control_are_one_adjustment` checks the controller's reading, and no test pressed a key on a slider at two simulated instants. `PL-41YP` (assert every required displayed output reaches the rendered view) describes the wider gap. Found by `PL-5FMC`, the check of the interface documents that the project owner asked for.

**Done when.** A key press, a wheel notch and a click on the track each open an adjustment of their own when they take effect at a different simulated instant, a test presses a key on a slider at two simulated instants and checks the marks, and `docs/INTERFACE.md` § "The control-input timeline" and the docstring of `begin_control_adjustment` say what the code does. Build this after the whole-second stepping work (`PL-SZ6G`, `PL-MH9J`, `PL-FST0`, `PL-Z6C8`), which changes when a setting takes effect.

**Checked 2026-11-22** against `d4e8200`: still applies, and its blocker `PL-Z6C8` closed with #2180. `SimulationController._record_in_timeline` in `app/controller.py` still opens a new adjustment only when `control is not self._open_adjustment_control`. `ParameterSlider` in `app/qt_widgets.py` still emits `adjustment_started` only on `sliderPressed`. `docs/INTERFACE.md` § "The control-input timeline" still says each key press, wheel notch or track click "is an adjustment of its own". No test presses a key on a slider.

**Done 2026-11-22.** `SimulationController._record_in_timeline` opens a new adjustment when the control differs from the open one or when the change takes effect at a later simulated instant (`self._open_adjustment_instant`). Changes to one control at one instant, as on a paused run, stay one adjustment. A drag applies once, at release (`PL-5B1N`), so no drag spans instants. On the code before the fix, `test_steps_of_one_control_at_three_instants_are_three_adjustments` failed with "assert [1, 1, 1] == [1, 2, 3]" and `test_each_arrow_key_step_at_a_new_instant_is_marked_and_listed` failed with "AssertionError: assert 1 == 3". The second presses the Right arrow on the fresh gas flow slider at 10 s, 40 s and 100 s and checks three timeline entries, three list lines and marks at 10, 40 and 100 s on both charts. `test_changes_to_one_control_at_one_instant_are_one_adjustment` replaces `test_consecutive_changes_to_one_control_are_one_adjustment`. The interface wording test's setting-change point now shows two separate Delivered agent lines where it showed one line with "(2 settings)", and its approved list was re-approved.

**Docs checked.** `docs/INTERFACE.md` § "The control-input timeline": the paragraph on how the interface declares an adjustment now says that a change to another control or at a later instant starts one. The per-input sentence already said so. The dashboard's list of what it shows still holds ("One adjustment can hold several changes of one control" is true at a branch's fork instant), and `PL-MQD3` asks whether that form is still worth keeping. The docstring of `begin_control_adjustment`. `docs/ARCHITECTURE.md`, `docs/VERIFICATION.md` and `README.md` say nothing about adjustments.
