---
id: PL-2D9Z
title: Walking Qt's focus chain with nextInFocusChain on every dashboard draw makes a later keyboard test crash inside a pyqtgraph layout request, and the cause is unknown
priority: P3
effort: M
status: ready
classes: defect
feature: interface-design-review
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_layout_keyboard.py
deferred-from: v0.7.0 - captured after the freeze; the shipped code does not walk the focus chain, so no reader can reach the crash
added: 2026-11-22
payoff: a crash inside the Qt bindings is named and reported, or fixed here, before other code reaches it
---

**Problem.** While building the tab order in `PL-B45W`, the first version
listed the window's focusable widgets by walking Qt's focus chain with
`QWidget.nextInFocusChain`, once at the end of every dashboard draw. With that
walk in place, `test_every_layout_operation_is_reachable_from_the_keyboard` in
`tests/integration/test_layout_keyboard.py` crashed with a segmentation fault
several steps after a walk, not during one. The native stack ended inside a
pyqtgraph chart's layout request: `QGraphicsWidget.setGeometry`, then
`effectiveBoundingRect`, then `Shiboken::BindingManager::getOverride`, then
`func_dealloc`. That looks like a Python wrapper freed while Qt still calls
into it. The versions were PySide6 6.11.2, pyqtgraph 0.14.0 and Python 3.15.2,
offscreen.

**What was ruled out.** Bisection did not find one draw whose walk is enough
on its own. Allocating the same number of plain Python objects instead of
walking did not crash, and neither did calling `gc.collect()` at the same
points. Every wrapper the walk returned still had the Python type that matched
its Qt class name, so no wrapper had been swapped for a bare `QWidget`.
Keeping a reference to every widget the walk returned did not stop the crash.
Listing the same widgets with `QObject.findChildren(QWidget)` does not crash,
so `PL-B45W` ships that.

**A second sign of the same kind (2026-11-22).** A later version of
`_focusable_widgets` walked each widget's `children()` and ordered them by its
layout, through `QLayout.itemAt`, `QLayoutItem.widget` and
`QGridLayout.getItemPosition`. It failed every time while the dashboard was
being built, with `RuntimeError: libshiboken: Internal C++ object
(PySide6.QtWidgets.QScrollBar) already deleted`. The scroll bar sat under a plain
widget inside a `QScrollArea`, and the wrapper had passed `isWindow()` a
moment before. No event loop ran in between. Both signs look
like a Python wrapper outliving its C++ object, so they may share a cause.

**Why it matters.** The cause may be a defect in PySide6, Shiboken or
pyqtgraph that other code paths can reach. `tests/integration/test_qt_widgets.py`
already walks the focus chain of the bookmark editor once, and that test
passes. A crash that depends on how many wrappers a walk creates could appear
later in the running app, where it would close the window without a message.

**Generator check.** Unknown until the cause is found, which is this item's
question. No other item records a crash of this shape. The suite's one other
walk of a focus chain, in the bookmark editor's test, passes.

**How to reproduce it.** On the commit that closes `PL-B45W`, change
`_focusable_widgets` in `src/anesthesia_sim/app/simulation_view.py` to walk
the chain instead of calling `findChildren`:

```python
widgets = []
widget = window.nextInFocusChain()
while widget is not window:
    if widget.focusPolicy() & Qt.FocusPolicy.TabFocus:
        widgets.append(widget)
    widget = widget.nextInFocusChain()
return widgets
```

Then run
`QT_QPA_PLATFORM=offscreen uv run pytest -q tests/integration/test_layout_keyboard.py -k test_every_layout_operation_is_reachable_from_the_keyboard`.
It ended in a segmentation fault in both of two runs on 2026-11-22.

**What to do.** Cut the reproduction down until it no longer needs the
simulator: a window with a pyqtgraph `PlotWidget` and some focusable widgets,
a walk of the chain, and a layout change. Run it under `python -X dev` with
`faulthandler` and a debug build of PySide6 if one installs. If the smaller
case still crashes, report it upstream with the case, to PySide6's tracker
(https://bugreports.qt.io/browse/PYSIDE, linked from
https://wiki.qt.io/Qt_for_Python/Reporting_Bugs, read 2026-11-22) or to
pyqtgraph, as the stack points, and record the report here. If it stops crashing, say which part of this
project's code it needed.

**Done when.** The cause is named, with either an upstream report or a fix
here, and this item records which.
