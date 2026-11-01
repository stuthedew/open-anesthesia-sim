---
id: PL-TCNT
title: The chart hands pyqtgraph Python lists on every frame and checks every value for NaN, where pyqtgraph's own performance guidance asks for numpy arrays and allows skipFiniteCheck once the values are known finite; take both, behind a frame-side guarantee that every drawn value is finite, so the chart's per-frame cost follows the library's recommended path
status: untriaged
feature: chart-readout
added: 2026-11-01
---

**Problem.** The chart hands pyqtgraph Python lists on every frame and checks every value for NaN, where pyqtgraph's own performance guidance asks for numpy arrays and allows skipFiniteCheck once the values are known finite; take both, behind a frame-side guarantee that every drawn value is finite, so the chart's per-frame cost follows the library's recommended path

**Context (2026-11-01).** The project owner asked for the chart's redraw to follow best practice rather than be measured for whether it is good enough (`PL-0KPD`, dropped the same day). The comparison against pyqtgraph's documentation:

- **Already the standard design.** The frame evaluates one column per pixel of plot width (`chart_frame.py`, `CHART_COLUMN_BUDGET_PER_SERIES`), which is the outcome pyqtgraph's `autoDownsample` aims for: "avoid plotting multiple line segments per pixel". The render tick draws only when a frame is owed or a run is running (`SimulationView.render_tick`), and simulation time is explicit state, so a late frame delays the picture and never the run.
- **Off the recommended path, and cheap to fix.** `qt_chart.py` calls `curve.setData(list(...), list(...))`. The `PlotDataItem` page says: "use `numpy.ndarray` instead of python's built-in lists." The `PlotCurveItem` page says `skipFiniteCheck` "can speed up plotting by not checking and compensating for NaN values", and that non-finite data then behaves unpredictably. So the flag is safe only behind a guarantee, made where the frame is assembled, that every drawn value is finite. A non-finite value must still halt the run with a named compartment rather than draw nothing.
- **Off the recommended path on purpose.** The traces use antialiased pens at least 2 px wide (`theme.MINIMUM_TRACE_STROKE_WIDTH`) with dash patterns. The `PlotDataItem` page says "Use a `QPen` with `width=1`. All wider pens cause a loss in performance", and its fast `drawLines` path needs a solid, opaque, non-antialiased pen. The width and dashes carry compartment identity and colour-vision accessibility (`PL-4LS8`), so they stay. OpenGL is not the answer either: `enableExperimental` is documented as single precision that "may cause drawing artifacts".

Sources: https://pyqtgraph.readthedocs.io/en/latest/api_reference/graphicsItems/plotdataitem.html and https://pyqtgraph.readthedocs.io/en/latest/api_reference/graphicsItems/plotcurveitem.html (read 2026-11-01).

**Done when.** Every `setData` on the concentration and wash-in charts receives numpy arrays. `skipFiniteCheck=True` is set only where the frame guarantees finite values, and a test shows a non-finite value still halts the run with its compartment named. The drawn points are unchanged, shown by comparing the arrays handed to pyqtgraph before and after.
