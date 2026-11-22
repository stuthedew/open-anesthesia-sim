---
id: PL-571L
title: The chart's top tick labels, 6 on the percent axis and 3.0 on the MAC-multiple axis, are cut in half at the plot's top edge
priority: P2
effort: S
status: done
classes: defect, ux
touches: src/anesthesia_sim/app/qt_chart.py, tests/integration/test_qt_chart.py
deferred-from: v0.7.0 - captured after the freeze; the axis values are correct and the other tick labels are whole, and it belongs with the interface pass rather than the schematic
added: 2026-11-09
closed: 2026-11-22
pr: 2225
payoff: a learner reads the top of each chart axis as clearly as the rest of the scale
tests: tests/integration/test_qt_chart.py::test_every_tick_label_is_painted_whole_inside_the_chart
---

**Problem.** The chart's top tick labels, 6 on the percent axis and 3.0 on the MAC-multiple axis, are cut in half at the plot's top edge

**Reproduced 2026-11-11.** An offscreen grab of the concentration chart on `main`, built by the run-the-app skill's recipe at 1600 by 2400 px and run to 120 s, shows the top tick label of each axis, 6 on the percent axis and 3.0 on the MAC-multiple axis, cut in half by the plot's top edge.

**Why it matters.** The top tick is the one a reader uses to judge an axis's range at a glance. The lower half of a "6" can read as a "0", so a learner may misjudge the scale. The other tick labels are whole, so the scale can still be worked out from them, which is why this is classed as a display defect and not a safety one.

**Done when.** A test grabs the chart and finds every tick label on both axes drawn whole inside the plot widget, and the test fails on today's `main`.

**Generator check.** A one-off. The plot's top margin is set without room for half a label's height, and no head's `misread:` states a fact about how a chart's margins are laid out.

**Checked 2026-11-22** against `d4e8200`: still applies, as far as the code shows. No test named in `verify:` exists. Since the reproduction of 2026-11-11, the four commits that touched `src/anesthesia_sim/app/qt_chart.py` (#2109, #2134, #2200, #2180) changed no margin, padding or axis range. The chart was not grabbed again in this check.

**Done 2026-11-22.** `_plot` in `src/anesthesia_sim/app/qt_chart.py` now sets the plot item's top margin to half a line of the plot's font, rounded up, in place of pyqtgraph's 1 px. Each axis range ends at a labelled tick and a label is centred on its tick, so the top label's upper half had fallen outside the widget. The margin is read from the font, so it holds under the container's font and CI's alike. Both plots share `_plot`, so the wash-in plot's top label is fixed too. `test_every_tick_label_is_painted_whole_inside_the_chart` reads each axis's painted label boxes through the new `tick_label_rects` and fails on the code before the fix with "the left axis's labels ['6'] reach outside the chart". Files checked: `docs/INTERFACE.md` (no margin or tick-label placement is specified) and `docs/ARCHITECTURE.md`.
