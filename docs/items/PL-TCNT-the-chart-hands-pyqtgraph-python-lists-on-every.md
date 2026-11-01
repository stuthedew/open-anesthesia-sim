---
id: PL-TCNT
title: The chart hands pyqtgraph Python lists on every frame and checks every value for NaN, where pyqtgraph's own performance guidance asks for numpy arrays and allows skipFiniteCheck once the values are known finite; take both, behind a frame-side guarantee that every drawn value is finite, so the chart's per-frame cost follows the library's recommended path
priority: P3
effort: S
status: done
feature: chart-readout
touches: src/anesthesia_sim/app/qt_chart.py, src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/run_series.py, pyproject.toml, uv.lock, docs/ARCHITECTURE.md, docs/WORKING_NOTES.md, tests/integration/test_qt_chart.py, tests/integration/test_simulation_view.py, tests/unit/test_chart_frame.py, tests/unit/test_run_series.py
added: 2026-11-01
closed: 2026-11-01
pr: 1924
verify: .venv/bin/python -m pytest -q tests/integration/test_qt_chart.py::test_every_curve_is_handed_the_frame_s_own_values_as_float64_arrays tests/integration/test_simulation_view.py::test_a_non_finite_drawn_value_halts_the_run_naming_its_compartment tests/unit/test_chart_frame.py::test_a_non_finite_drawn_value_is_refused_naming_its_compartment tests/unit/test_chart_frame.py::test_a_wash_in_stretch_refuses_a_non_finite_ratio tests/unit/test_run_series.py::test_a_window_refuses_an_instant_that_is_not_finite
---

**Problem.** The chart hands pyqtgraph Python lists on every frame and checks every value for NaN, where pyqtgraph's own performance guidance asks for numpy arrays and allows skipFiniteCheck once the values are known finite; take both, behind a frame-side guarantee that every drawn value is finite, so the chart's per-frame cost follows the library's recommended path

**Context (2026-11-01).** The project owner asked for the chart's redraw to follow best practice rather than be measured for whether it is good enough (`PL-0KPD`, dropped the same day). The comparison against pyqtgraph's documentation:

- **Already the standard design.** The frame evaluates one column per pixel of plot width (`chart_frame.py`, `CHART_COLUMN_BUDGET_PER_SERIES`), which is the outcome pyqtgraph's `autoDownsample` aims for: "avoid plotting multiple line segments per pixel". The render tick draws only when a frame is owed or a run is running (`SimulationView.render_tick`), and simulation time is explicit state, so a late frame delays the picture and never the run.
- **Off the recommended path, and cheap to fix.** `qt_chart.py` calls `curve.setData(list(...), list(...))`. The `PlotDataItem` page says: "use `numpy.ndarray` instead of python's built-in lists." The `PlotCurveItem` page says `skipFiniteCheck` "can speed up plotting by not checking and compensating for NaN values", and that non-finite data then behaves unpredictably. So the flag is safe only behind a guarantee, made where the frame is assembled, that every drawn value is finite. A non-finite value must still halt the run with a named compartment rather than draw nothing.
- **Off the recommended path on purpose.** The traces use antialiased pens at least 2 px wide (`theme.MINIMUM_TRACE_STROKE_WIDTH`) with dash patterns. The `PlotDataItem` page says "Use a `QPen` with `width=1`. All wider pens cause a loss in performance", and its fast `drawLines` path needs a solid, opaque, non-antialiased pen. The width and dashes carry compartment identity and colour-vision accessibility (`PL-4LS8`), so they stay. OpenGL is not the answer either: `enableExperimental` is documented as single precision that "may cause drawing artifacts".

Sources: https://pyqtgraph.readthedocs.io/en/latest/api_reference/graphicsItems/plotdataitem.html and https://pyqtgraph.readthedocs.io/en/latest/api_reference/graphicsItems/plotcurveitem.html (read 2026-11-01).

**Done when.** Every `setData` on the concentration and wash-in charts receives numpy arrays. `skipFiniteCheck=True` is set only where the frame guarantees finite values, and a test shows a non-finite value still halts the run with its compartment named. The drawn points are unchanged, shown by comparing the arrays handed to pyqtgraph before and after.

**Generator check.** Not a generator. It is one change to one adapter, and nothing else was filed from it. It touches `docs/WORKING_NOTES.md` only to record the numpy decision that note left open until a module under `src/` wanted numpy.

**Outcome (2026-11-01).** `app/qt_chart.py` hands every curve and dot `float64` arrays through `_plot_coordinates`, and draws every curve through `_draw_curve`, which passes `skipFiniteCheck=True`. Those two functions are the one place where each happens. The finite-value guarantee is stated in `app/chart_frame.py`'s module docstring and enforced where each coordinate is built. A compartment value is a `Fraction`, which already rejected NaN and infinity under the compartment's name. `DrawnWindow` now rejects a non-finite instant, and `WashInStretch` now rejects a non-finite ratio. numpy became a declared runtime dependency, since a package the project imports is one it declares, and the `dev` group's copy went in the same commit. `app/chart_frame.py` and `core/` still do not import numpy.

A checked `CaseInstant` type for every drawn instant was considered instead of the finiteness check in `DrawnWindow`. It would also check the supported run length, but it reaches into `core/run_definition.py`, which produces the instants, and finiteness is all that `skipFiniteCheck` needs. The pens stay as they are: the item's context records why the wider, dashed, antialiased pens are kept.
