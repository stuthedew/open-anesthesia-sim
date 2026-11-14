---
id: PL-571L
title: The chart's top tick labels, 6 on the percent axis and 3.0 on the MAC-multiple axis, are cut in half at the plot's top edge
priority: P2
effort: S
status: ready
classes: defect, ux
touches: src/anesthesia_sim/app/qt_chart.py, tests/integration/test_qt_chart.py
deferred-from: v0.7.0 - captured after the freeze; the axis values are correct and the other tick labels are whole, and it belongs with the interface pass rather than the schematic
added: 2026-11-09
payoff: a learner reads the top of each chart axis as clearly as the rest of the scale
verify: grep -q 'def test_every_tick_label_is_drawn_whole_inside_the_plot' tests/integration/test_qt_chart.py
---

**Problem.** The chart's top tick labels, 6 on the percent axis and 3.0 on the MAC-multiple axis, are cut in half at the plot's top edge

**Reproduced 2026-11-11.** An offscreen grab of the concentration chart on `main`, built by the run-the-app skill's recipe at 1600 by 2400 px and run to 120 s, shows the top tick label of each axis, 6 on the percent axis and 3.0 on the MAC-multiple axis, cut in half by the plot's top edge.

**Why it matters.** The top tick is the one a reader uses to judge an axis's range at a glance. The lower half of a "6" can read as a "0", so a learner may misjudge the scale. The other tick labels are whole, so the scale can still be worked out from them, which is why this is classed as a display defect and not a safety one.

**Done when.** A test grabs the chart and finds every tick label on both axes drawn whole inside the plot widget, and the test fails on today's `main`.

**Generator check.** A one-off. The plot's top margin is set without room for half a label's height, and no head's `misread:` states a fact about how a chart's margins are laid out.
