---
id: PL-CW51
title: A drift.yml interpreter job on CPython 3.15.0 printed 'pure virtual method called' and 'terminate called without an active exception' just before 100% while every test passed, so a C++ object is destroyed under a live Qt call somewhere in the suite (run 39167787757, job 117794282666, found timing PL-QT2J)
priority: P3
effort: M
status: done
classes: defect, test
feature: qt-teardown-crashes
milestone: v0.6.0
touches: tests/conftest.py, tests/integration/test_session_end.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 triage pass
added: 2026-10-18
closed: 2026-10-19
pr: 1686
payoff: The suite stops destroying a Qt object under a live call, so the next interpreter upgrade does not arrive with a worker crash already in it
verify: grep -q 'def windows_built' tests/conftest.py
not-delegable: Reproducing it needs the drift job's CPython 3.15.0 with the newest PySide6, and the message is printed by a run that still passes, so no command run on the base interpreter can fail before the work and pass after it
---

**Problem.** A drift.yml interpreter job on CPython 3.15.0 printed 'pure virtual method called' and 'terminate called without an active exception' just before 100% while every test passed, so a C++ object is destroyed under a live Qt call somewhere in the suite (run 39167787757, job 117794282666, found timing PL-QT2J)

The two lines appeared at 21:40:35Z on 2026-10-18, in job 117794282666 of run
39167787757, which ran `-n auto` on CPython 3.15.0 with the newest PySide6
that `uv sync --upgrade` resolved. The summary line still read 9,423 passed and 2 skipped, and the job concluded
`success`. The other three jobs on 3.15.0 in that run did not print it. Which
test was running is not known: `-n auto` prints dots, not names. That a Qt
object outlived its C++ side is the usual cause of this message, but here it is
inferred, not shown.

**Why it matters.** The message means native code called a method on a C++
object that had already been destroyed. Here the process survived, but the same
fault can kill an xdist worker, as `PL-Q18P` (a worker crash on `main`'s quality
run) shows. On the CPython that `drift.yml` tests ahead of time, it is a
warning that the suite may fail once the project moves to it.

**Done when.** The test that prints the message is found, for example by
running the drift job's interpreter with `-p no:xdist -v`. Then either its Qt
object lifetime is fixed, with a test that would have caught it, or the item
records that the fault is in PySide6 on CPython 3.15, with the upstream
report. If `PL-Q18P`'s fix removes the message, close this item with that
evidence.

**Fixed 2026-10-19.** No test prints the message. It is printed as a worker
exits, after the last test, while the exit destroys the windows the tests left
open: up to 213 top-level windows and 3,514 widgets in one worker. A core dump
of a worker that died silently on CPython 3.15.0 with PySide6 6.12.0 showed the
crash inside `PySide::destroyQCoreApplication`, which `atexit` runs. In this
container the message appeared in about 1 of 11 runs of `tests/integration`
on 3.15.0. `PL-Q18P`'s fix (#1651) did not remove it, since those runs were on
a tree that already had it.

The cause is a widget that Qt builds for its own use. Each
`QGraphicsLayoutStyleInfo` holds a parentless `QWidget` in a `unique_ptr`
("pixelMetric might need a widget ptr") and deletes it with the layout
(https://github.com/qt/qtbase/blob/6.11/src/widgets/graphicsview/qgraphicslayoutstyleinfo.cpp,
line 18). A pyqtgraph plot's layout builds one when the plot first takes its
size, so a dashboard has one per chart. Deleting that widget before its plot
makes the layout delete it a second time. This reproduces with one bare
`pg.PlotWidget()` on CPython 3.14.7 with PySide6 6.11.2: deleting the stray
widget and then the plot exits with a segmentation fault (139). Deleting the
plot first takes the widget with it and exits cleanly.

So `tests/conftest.py`'s `pytest_sessionfinish` now deletes, while the
application still runs, only the parentless windows that Python built
(`shiboken6.createdByPython`), and leaves Qt's own widgets to their owners. A
first attempt that deleted every parentless window crashed 2 of 4 workers on
both interpreters, which is the regression it guards against. With the fix,
three runs on 3.15.0 and one on 3.14.7 left no widget alive in any worker, and
three more runs (two on 3.15.0, one on 3.14.7) printed no "pure virtual", no
segmentation fault and no "node down". `tests/integration/test_session_end.py`
checks that the cleanup chooses a dashboard and not Qt's widget, and that
deleting the dashboard leaves none of its widgets alive. The variant without
the new `windows_built`, deleting every new parentless window, is the crash
above. The application itself never lists its windows, so its exit can reach
Qt's widget only through the plot that owns it; that is inferred, not tested.
The fault is not PySide6's or pyqtgraph's, so no upstream report is needed.
