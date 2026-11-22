---
id: PL-2D9Z
title: Walking Qt's focus chain with nextInFocusChain on every dashboard draw makes a later keyboard test crash inside a pyqtgraph layout request, and the cause is unknown
priority: P3
effort: M
status: done
classes: defect
feature: interface-design-review
milestone: v0.6.21
touches: pyproject.toml, README.md, uv.lock, src/anesthesia_sim/app/simulation_view.py, tests/integration/test_layout_keyboard.py, docs/ARCHITECTURE.md
deferred-from: v0.7.0 - captured after the freeze; the shipped code does not walk the focus chain, so no reader can reach the crash
added: 2026-11-22
closed: 2026-11-22
pr: 2239
payoff: a crash inside the Qt bindings is named and reported, or fixed here, before other code reaches it
tests: tests/integration/test_layout_keyboard.py::test_layout_operations_survive_a_walk_of_the_focus_chain_on_every_draw
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

**Generator check.** Not a generator here. The cause is one fault in the Qt
bindings, which a version floor removes for every code path at once. No other
item records a crash of this shape, and no other test failed on 6.12.0.

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

**Cause (2026-11-22).** A use-after-free inside the Qt bindings. Under
valgrind (run with `PYTHONMALLOC=malloc`), the reproduction above on PySide6
6.11.2 showed Shiboken's `Sbk_GetPyOverride` freeing a Python function object,
made by a class body, and `BindingManager::getOverride` then reading it through
`PyObject_GetAttr`. That is the frame the native stack ended in. The same run
crashed on 6.11.3, and on Python 3.14 as well as 3.15, so neither the patch
release nor the interpreter is the cause. On 6.12.0 the reproduction passed on
both interpreters, and valgrind reported no read of freed memory during the
run. Adding a `findChildren` call after the walk hid the crash, and turning
the garbage collector off did not, which fits memory reuse rather than a
collected wrapper. Each version was tried with
`uv run --with "pyside6-essentials==X" --with "shiboken6==X"`.

**Sources read on 2026-11-22.** The PySide6 release notes
(https://doc.qt.io/qtforpython-6/release_notes/pyside6_release_notes.html,
full page) list for 6.12.0 the first support for Python 3.15 and PYSIDE-3469.
The Jira record of PYSIDE-3469
(https://bugreports.qt.io/rest/api/2/issue/PYSIDE-3469, read through the
REST API) is titled "Segfault from stale Shiboken QLayoutItem wrappers" and is
fixed in 6.12.0. It matches this item's second sign, the "already deleted"
scroll bar met through `QLayout.itemAt`. PyPI's JSON record for
`pyside6-essentials` gives 6.12.0's upload date as 2026-10-08 and its Python
range as `>=3.10, <3.16`. No upstream report is filed, because the fault is
already fixed upstream.

**Fix.** `pyproject.toml` raises the floor to `PySide6-Essentials>=6.12`, with
the reason beside it, and `uv.lock` moves `pyside6-essentials` and `shiboken6`
from 6.11.2 to 6.12.0. The full suite passed on 6.12.0 (12,429 tests; the one
failure in that run was a test reading a source file that this session was
editing at the time, and it passed on its own afterwards). The dashboard keeps
`findChildren`, which already returns the tree's order, and the docstring of
`_focusable_widgets` no longer says the cause is unknown.

**The cost: macOS 13 is dropped.** The blind review found that 6.12.0's macOS
wheels for both packages are tagged `macosx_14_0`, where 6.11.2's were
`macosx_13_0`, and neither package ships a source distribution. Qt's page for
macOS (https://doc.qt.io/qt-6/macos.html, read 2026-11-22) says Qt 6.12
supports macOS 14.4 or later. The floor is kept, because the alternative is a
binding with a known memory fault. `README.md` § "Running it" now names macOS
14.4, and `pyproject.toml` says why beside the floor.

**Regression test.**
`tests/integration/test_layout_keyboard.py::test_layout_operations_survive_a_walk_of_the_focus_chain_on_every_draw`
swaps the dashboard's widget list for the walk of the focus chain and runs every
layout operation from the keyboard. On 6.11.2,
`QT_QPA_PLATFORM=offscreen uv run --with "pyside6-essentials==6.11.2" --with "shiboken6==6.11.2" pytest -q tests/integration/test_layout_keyboard.py -k survive_a_walk`
ended with "Fatal Python error: Segmentation fault" and exit status 139. On
6.12.0 it passes.

**Documents checked.** `docs/ARCHITECTURE.md` names 6.11.2 in two dated
measurements. Both were checked again on 6.12.0: `readelf -d` lists the same
shared objects for `libQt6Gui.so.6`, and both wheels declare the same licence
with no licence file. Each sentence now gives both dates. `README.md` now names
the macOS version that Qt 6.12 needs. `docs/INTERFACE.md`
names 6.11.2 twice, as the version that a measurement of window visibility and
a reading of Qt's slider source were made on. Both are dated statements about
that version, and neither depends on the upgrade. `docs/VERIFICATION.md`, `docs/MODEL.md`, `docs/PARAMETERS.md` and
`CONTRIBUTING.md` name no PySide6 version.
