---
id: PL-0T2H
title: Arrow-key, wheel and track-click steps on one dial are joined into one adjustment, so the chart marks only the first step and docs/INTERFACE.md says each step is an adjustment of its own: decide which a learner sees
status: untriaged
feature: interface-matches-its-spec
added: 2026-11-21
---

**Problem.** Arrow-key, wheel and track-click steps on one dial are joined into one adjustment, so the chart marks only the first step and docs/INTERFACE.md says each step is an adjustment of its own: decide which a learner sees

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). `docs/INTERFACE.md` § "Control changes on the chart" says "A key press, one notch of the scroll wheel or a click on the slider away from its handle is a single input, and is an adjustment of its own." The code joins them. The interface declares the start of an adjustment only when the handle is pressed (`ParameterSlider.__init__` in `app/qt_widgets.py` connects `sliderPressed` to `adjustment_started`). `SimulationController._record_in_timeline` in `app/controller.py` opens a new adjustment only when the changed control differs from the one already open, whatever simulated time has passed. A chart marks one instant for each adjustment, its start (`_run_frame` in `app/chart_frame.py`).

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

**Done when.** A key press, a wheel notch and a click on the track each give the result the owner chooses, a test presses a key on a slider at two simulated instants and checks the marks, and `docs/INTERFACE.md` § "Control changes on the chart" and the docstring of `begin_control_adjustment` say what the code does. Build this after the whole-second stepping work (`PL-SZ6G`, `PL-MH9J`, `PL-FST0`, `PL-Z6C8`), which changes when a setting takes effect.
