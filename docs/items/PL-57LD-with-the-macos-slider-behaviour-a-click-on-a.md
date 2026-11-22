---
id: PL-57LD
title: With the macOS slider behaviour, a click on a slider's track applies the setting and then draws it as a preview labelled 'not applied', and a press on the handle away from its centre applies a change before any drag
priority: P1
effort: M
status: done
classes: defect, safety
feature: interface-matches-its-spec
milestone: v0.6.20
touches: src/anesthesia_sim/app/qt_widgets.py, tests/integration/simulation_view/test_simulation_view_controls.py, docs/INTERFACE.md
added: 2026-11-21
closed: 2026-11-22
pr: 2214
payoff: A learner on a Mac who clicks a setting slider sees either an applied change or a labelled preview, never an applied value marked not applied.
tests: tests/integration/simulation_view/test_simulation_view_controls.py::test_a_click_on_a_slider_s_track_applies_at_once_and_draws_no_preview, tests/integration/simulation_view/test_simulation_view_controls.py::test_a_press_on_the_handle_off_its_centre_released_unmoved_applies_nothing, tests/integration/simulation_view/test_simulation_view_controls.py::test_a_drag_from_off_the_handle_s_centre_moves_the_setting_only_as_far_as_the_pointer_moves
---

**Problem.** With the macOS slider behaviour, a click on a slider's track applies the setting and then draws it as a preview labelled 'not applied', and a press on the handle away from its centre applies a change before any drag

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). `docs/INTERFACE.md` § "A preview of an unapplied setting" says "**A drag applies its value only when the handle is released.**" and "A key press, one notch of the scroll wheel or a click on the slider away from its handle is a single input, so it applies at once and draws no preview." Both hold under Qt's Fusion style, which the test platform uses. They may not hold on macOS, where the style lets a left click on the track move the handle to the pointer.

Qt's source at tag v6.11.2 (the installed PySide6 is 6.11.2), read from `raw.githubusercontent.com/qt/qtbase`:

- `src/plugins/styles/mac/qmacstyle_mac.mm` returns `Qt::LeftButton|Qt::MiddleButton` for `SH_Slider_AbsoluteSetButtons` and `0` for `SH_Slider_PageSetButtons`. `qcommonstyle.cpp` returns `Qt::MiddleButton` and `Qt::LeftButton` for the same two hints.
- `QSlider::mousePressEvent` in `src/widgets/widgets/qslider.cpp`, for an absolute-set button, calls `setSliderPosition`, `triggerAction(SliderMove)` and `setSliderDown(true)`. `triggerAction` ends with `setValue`, which emits `valueChanged` even with tracking off, and `setSliderDown(true)` emits `sliderPressed`.
- The application sets no style (`git grep -n -E "\.setStyle\(|QStyleFactory|Fusion" -- src` finds nothing), and a stylesheet does not change either hint.

`ParameterSlider` in `app/qt_widgets.py` connects `sliderPressed` to the start of a preview and `valueChanged` to the applied value. The script below gives the slider the macOS hints through a proxy style on Linux, then presses the left button on the fresh gas flow slider's track on a run paused at 300 s. It was not run on macOS.

```python
import sys
from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QProxyStyle, QStyle, QStyleOptionSlider

from anesthesia_sim.app.controller import SimulationController
from tests.integration.simulation_view.simulation_view_support import (
    _advance, _concentration, _dials, _shown_view, _wash_in,
)


class MacHints(QProxyStyle):
    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint == QStyle.StyleHint.SH_Slider_AbsoluteSetButtons:
            return int(Qt.MouseButton.LeftButton.value | Qt.MouseButton.MiddleButton.value)
        if hint == QStyle.StyleHint.SH_Slider_PageSetButtons:
            return 0
        return super().styleHint(hint, option, widget, returnData)


app = QApplication.instance() or QApplication(sys.argv)
if "mac" in sys.argv:
    app.setStyle(MacHints())
controller = SimulationController()
controller.start()
_advance(controller, 300.0)
controller.pause()
view = _shown_view(app, controller)
run = view.runs[0]
control = _dials(run)._fresh_gas_flow_slider
chart = _concentration(view).chart
slider = control.slider
opt = QStyleOptionSlider()
slider.initStyleOption(opt)
handle = slider.style().subControlRect(QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderHandle, slider)
away = QPoint(slider.width() - 10, slider.height() // 2)
assert not handle.contains(away)
print("before: flow in force", controller.settings().fresh_gas_flow_l_min, "| changes recorded", len(controller.record().control_timeline))
QTest.mousePress(slider, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, away)
view.render_tick()
print("button held on the groove: flow in force", controller.settings().fresh_gas_flow_l_min,
      "| changes recorded", len(controller.record().control_timeline),
      "| label in the plot:", chart.preview_label(0), "| region:", chart.preview_region(0),
      "| value beside the slider:", control.value_label.text())
QTest.mouseRelease(slider, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, away)
view.render_tick()
print("released: flow in force", controller.settings().fresh_gas_flow_l_min, "| changes recorded", len(controller.record().control_timeline), "| label:", chart.preview_label(0))
```

Output of `QT_QPA_PLATFORM=offscreen PYTHONPATH=. uv run python dash.py fusion`, then with `mac`:

```
before: flow in force 4.0 | changes recorded 0
button held on the groove: flow in force 4.1 | changes recorded 1 | label in the plot: None | region: None | value beside the slider: 4.1 L/min
released: flow in force 4.1 | changes recorded 1 | label: None

before: flow in force 4.0 | changes recorded 0
button held on the groove: flow in force 10.0 | changes recorded 1 | label in the plot: Preview: Fresh gas flow 10.0 L/min, not applied | region: (300.0, 450.0) | value beside the slider: 10.0 L/min
released: flow in force 10.0 | changes recorded 1 | label: None
```

With the macOS hints, a press on the handle 3 px to the right of its centre, released without moving, also applied a value: `[('value_changed', 4.1), ('preview_moved', 4.1), 'preview_ended']`. Under Fusion the same press gave `[('preview_moved', 4.0), 'preview_ended']`.

**Why it matters.** If the macOS style behaves as its source reads, a learner on a Mac who clicks the track sees the setting jump to the pointer and take effect, while the chart labels that value "not applied" for as long as the button is down. A drag that starts off the handle's centre applies a value at the press, and a second value at release.

**The owner can confirm it in a minute.** On a paused run on the Mac, click the fresh gas flow slider's track well away from the handle. If the value jumps to the pointer, and not by one step, the macOS style behaves as above.

**Done when.** A click on the track and a press on the handle give the same result under the macOS hints as under Fusion, in whichever form `docs/INTERFACE.md` § "A preview of an unapplied setting" then states, and a test runs both gestures under a proxy style that returns the macOS hints.

**Checked 2026-11-22**, at `d4e8200c`. The code is as it was. `git grep -n -E '\.setStyle\(|QStyleFactory|Fusion|SH_Slider' -- src` still finds nothing, so the application still takes the host platform's slider hints. `ParameterSlider` in `app/qt_widgets.py` still turns tracking off, connects `sliderPressed` to the start of a preview, and connects `valueChanged` to the applied value. The preview did not exist at the freeze; it came in with `PL-5B1N` (the preview a held control draws). It has still not been run on macOS.

**Generator check.** A one-off. The misread fact is which pointer gestures a slider turns into an applied value on each host platform's style: the tests run only under Fusion, and nothing models the macOS hints. `PL-KRZW` (closed: which palette roles a widget takes from the host platform) states a neighbouring fact about colour, not input, and `PL-YZ9L` (open: heavier lettering under macOS Dark) is a second item about a host-platform difference that the offscreen tests cannot see. Two items do not make a generator.

**Owner check asked 2026-11-22.** On a Mac, pause a run and click the fresh gas flow slider's track well away from the handle. If the value jumps to the pointer, the chart labels an applied setting "not applied" and the item stays on Gate 3's frozen list. If it moves one step, the hazard is not live on that Mac and the item can be deferred with that record.

**Answered 2026-11-22 (project owner, 2026-11-22, ratified, over a Mac test before deciding).** The owner asked that each item needing him be settled by standard practice. A slider follows the host platform's own track-click convention, which Qt's style for each platform encodes: on macOS a left click on the track moves the handle to the pointer, and under Fusion it steps one page. The source read on 2026-11-21 and quoted above shows this for `qmacstyle_mac.mm` and `qcommonstyle.cpp` at tag v6.11.2. Overriding the platform's hint would make the simulator behave unlike every other slider on a Mac. What is wrong is the preview label. A click on the track is a single input on either platform, so it applies at once and draws no preview, and a press on the handle applies nothing until the handle moves. The Mac check is no longer needed to decide the item: the fix and its test cover the macOS hints whether or not the owner's Mac shows the jump, so the item stays on Gate 3's frozen list.

**Done when, as answered.** Under a proxy style that returns the macOS hints, a click on the track applies the value at the pointer and draws no preview, and a press on the handle off its centre, released without moving, applies nothing. The same test under Fusion shows a one-page step with no preview. `docs/INTERFACE.md` § "A preview of an unapplied setting" states both platforms' track click.

**Done 2026-11-22.** A click on a slider's track is one input on every platform: it applies at once and draws no preview, and the platform's own convention for which button jumps and which steps is kept (`_SettingSlider` in `app/qt_widgets.py`). A press on the handle applies nothing until a drag, and the drag is measured from where the handle was pressed, so a 1 px movement after an off-centre press moves the setting no further than Fusion's own grab does. Docs checked: `docs/INTERFACE.md` § "A preview of an unapplied setting" (rewritten, with its developer note), `ParameterSlider`'s docstring (corrected for Fusion's repeating step), `docs/ARCHITECTURE.md` (one stale sentence said a drag records several settings; it now says a drag applies once, at the release) and `README.md` (no mention of a slider, by `grep -n -i "slider"`). Left for later: PL-M3H5 (a key press while the handle is held applies but stays labelled "not applied").
