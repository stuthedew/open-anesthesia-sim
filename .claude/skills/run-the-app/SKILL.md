---
name: run-the-app
description: Launch, drive and screenshot this repository's Qt interface in a session with no display. Use when asked to run, start, see or screenshot the app, or to check how a change looks in the real interface.
---

# run-the-app

A container session has no display and needs none. Under Qt's `offscreen`
platform the real widgets are built, laid out and painted into memory,
`QWidget.grab()` writes the result to a PNG, and the `Read` tool opens the PNG
as an image. Everything below is that one route, and every command in it was
run as written on 2026-10-01 (`PL-CQRL`).

## See the dashboard in a given state

```bash
mkdir -p out && QT_QPA_PLATFORM=offscreen uv run python - <<'EOF'
from PySide6.QtWidgets import QApplication, QPushButton
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import SIMULATION_STEP_S
from anesthesia_sim.app.qt_widgets import declare_application_colours
from anesthesia_sim.app.simulation_view import SimulationView

SIMULATED_S = 120.0
WIDTH_PX, HEIGHT_PX = 1600, 2400

app = QApplication([])
declare_application_colours(app)
case = BranchedCase(SimulationController())
view = SimulationView((case.trunk,), case=case)
view.resize(WIDTH_PX, HEIGHT_PX)
view.show()
app.processEvents()
view.present(False)

next(b for b in view.findChildren(QPushButton) if b.text() == "Start").click()
controller = case.trunk
for _ in range(round(SIMULATED_S / SIMULATION_STEP_S)):
    controller.advance(SIMULATION_STEP_S)

view.present(False)
app.processEvents()
print(view.grab().save("out/dashboard.png"))
EOF
```

It prints `True` and writes `out/dashboard.png`, the whole page from the title
to the disclaimer; open it with `Read`. A fresh container takes about ten
seconds, most of it `uv` building the environment. At a height of 1000 the
grab is the top of the scroll area only.

What each step is for, so the command can be changed without breaking it:

- **`declare_application_colours` and `BranchedCase` are what `main()` does**,
  in `src/anesthesia_sim/app/main.py`. Leave them out and the picture is not
  what ships: built without `case=`, the view hides its Branch section.
- **The first `processEvents()` lets the layout settle**, because the first
  frame reads the plot's laid-out width.
- **Start is pressed through its button**, so the view's own slot runs, as it
  does for a user.
- **`advance` moves the model and nothing else. The view draws only when
  `present(False)` is called** - in the running app a render timer calls it,
  and no timer runs here. Grab without the second `present(False)` and the PNG
  is the frame drawn before Start: `0s`, `Paused`, flat traces, and no error.
  That is what the instruction this skill replaced produced, on 2026-10-01.
- **The last `processEvents()` paints what `present` assembled**;
  `tests/benchmarks/frame_cost.py` says why that is a stage of its own.

**Before reading anything off the image, check it is the frame you asked
for**: the Simulated time readout must show the time you advanced to.

## Driving it further

- **A control change mid-run** is what the `dashboard` fixture in
  `tests/integration/test_qt_rendering.py` does: advance, call
  `controller.begin_control_adjustment()`, set the control through the
  controller, advance again. Copy it rather than reconstructing it; it is the
  tested form.
- **A state you only need to look at** goes through the controller, which has
  no widget to find.
- **An interaction you are checking** goes through the widget, found with
  `view.findChildren(<type>)` and driven by its own API, so the signal the view
  connects is the one that fires. A setter fires only the programmatic signals:
  `QComboBox.setCurrentIndex` fires `currentIndexChanged`, which the view
  connects, but `QSlider.setValue` fires `valueChanged` and not
  `sliderPressed`, which a setting panel in `qt_widgets.py` connects to mark an
  adjustment's start - emit `sliderPressed` yourself first when that start is
  part of what you are checking. Then `present(False)` and `processEvents()`
  before the grab, as above.

## What an offscreen frame cannot settle

- **Type metrics.** The container draws with its fallback sans-serif font, not
  the font the project owner's machine draws with, so wrapping, clipping and
  widths measured here are indicative rather than final; `PL-Z4K6` measured on
  the offscreen font and said so.
- **Timing.** No event loop runs, so neither playback cadence nor the render
  timer is exercised. `tests/benchmarks/frame_cost.py` measures frame cost,
  and on this container's software rasteriser only relatively.
- **The window.** `main()`'s maximised window and its initial geometry are not
  exercised; the view is grabbed at the size you set.
- **The real entry point.** `xvfb-run` is installed, but `uv run
  anesthesia-sim` under it aborts at startup: Qt's `xcb` plugin needs
  `libxcb-cursor0` and other xcb libraries this container lacks (measured
  2026-10-01). Installing them would open that route; nothing here needs it.

## Keep the look as a test where it matters

A screenshot is a look, not a guarantee. A presentation change that has to
stay right lands with an assertion in `tests/integration/test_qt_rendering.py`,
which renders the real dashboard headless and asserts over pixels and laid-out
geometry. Images go in `out/`, which `.gitignore` covers, so a grab cannot
reach a commit (`PL-CNJ1`); delete it whenever.
