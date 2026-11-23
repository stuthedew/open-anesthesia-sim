---
id: PL-9RZJ
title: Deleting a View that is its own window makes the time axis title raise 'AxisItem already deleted' tracebacks after the window closes; they fail no test, but a later Qt or pyqtgraph change could turn them into a crash or hide a real error in the log
status: done
milestone: v0.6.22
added: 2026-11-22
closed: 2026-11-22
pr: 2257
filed-pr: 2249
tests: tests/integration/test_qt_chart.py::test_deleting_a_chart_s_window_leaves_its_time_axis_title_writing_nothing
---

**Problem.** Deleting a View that is its own window makes the time axis title raise 'AxisItem already deleted' tracebacks after the window closes; they fail no test, but a later Qt or pyqtgraph change could turn them into a crash or hide a real error in the log

**Done 2026-11-22.** What was wrong: `_TimeAxisTitle` in `app/qt_chart.py` connected its `_refit` to the time axis's `geometryChanged` signal. `_TimeAxisTitle` is a plain Python object, so Qt never ended that connection on its own. When a chart had drawn a frame and then withheld one, deleting its window made Qt report a geometry change on the axis while the axis itself was being deleted, after its Python side was gone. `_refit` then read the axis's size and raised `RuntimeError: libshiboken: Internal C++ object (AxisItem) already deleted.` PySide printed the traceback and went on, so no test failed. The test that showed it is `tests/integration/test_view_contract.py::test_every_registered_view_draws_a_state_alike_whatever_it_drew_before`, for the concentration chart and the wash-in plot, whose `_drawn_alone` shows each View in a window of its own and deletes the window. It printed 20 tracebacks, each for a pair of states that ends with a frame withheld after one drawn.

The fix ends the connection before the axis is deleted. `_TimeAxisTitle` now takes the plot widget that draws the axis, and disconnects `_refit` when that widget's `destroyed` signal fires. A probe with `shiboken6.isValid` showed the order: the plot widget's `destroyed` arrives while the axis is still valid, and the report on the dying axis comes after it. A check of `shiboken6.isValid` inside `_refit` would also have silenced the traceback, but it would leave the slot connected to a dead object and hide the cause.

Test: `tests/integration/test_qt_chart.py::test_deleting_a_chart_s_window_leaves_its_time_axis_title_writing_nothing`, for both charts. It draws a frame, withholds one, deletes the window, and asserts that the error stream holds no traceback. Before the fix, `uv run pytest -q tests/integration/test_qt_chart.py -k deleting_a_chart` failed both cases with `assert 'Traceback' not in 'Traceback (...y deleted.\n'`, the captured text ending `RuntimeError: libshiboken: Internal C++ object (AxisItem) already deleted.` After the fix, `uv run pytest -q -s tests/integration/test_view_contract.py tests/integration/test_qt_chart.py` prints no traceback.

Files checked: `docs/INTERFACE.md` and `docs/ARCHITECTURE.md`, with `grep -n -i "time axis title\|axis title\|AxisItem\|geometryChanged\|already deleted"`. Neither describes how the title is refitted, so neither is stale.

**Generator check.** One instance, not a generator. `grep -rn "geometryChanged\|\.sig[A-Z][A-Za-z]*\.connect" src/anesthesia_sim/app/` finds two other connections to a pyqtgraph item's signal, `sigResized` to each chart's `_refresh_hover`. Their receiver is the chart, a `QWidget`, and the full `-s` run of both test files above prints nothing from them.
