---
id: PL-02Z0
title: The 1 MAC reference line is named only in the chart's legend and heading, so a reader has to look away from the plot to tell it from a trace; label it directly at its right end
priority: P2
effort: S
status: ready
classes: feature
feature: presentation-safety
touches: src/anesthesia_sim/app/qt_chart.py, tests/integration/test_qt_chart.py
added: 2026-11-23
filed-pr: 2271
payoff: a learner can tell the 1 MAC reference line from a trace without looking away from the plot
---

**Problem.** The concentration chart draws 1 MAC as a dashed `MUTED` line and names it only in the legend and the heading's reference text. A reader has to look from the line to the legend to tell it from a compartment trace. `PL-6W49` (tell the fat trace from the 1 MAC line) moved the fat trace off grey, so the two no longer look alike, but the line is still identified only at a distance from it.

**Recommendation.** Label the line at its right end, inside the plot, as "1 MAC". Wilke, *Fundamentals of Data Visualization* (O'Reilly, 2019), chapter 20 § 20.2 "Redundant coding", recommends labelling lines directly in place of a legend where the lines can be labelled; read it at source again before building, and check the label against the traces that pass under it at equilibrium.

**Done when.** The 1 MAC line carries its own label in the plot, the label never covers a trace's end value, and the label stays legible at the chart's minimum size.

**Why it matters.** The 1 MAC line is the reference a learner reads every trace against. While it is named only in the legend and the heading, a learner whose eye is on the plot has to look away to confirm which line is the reference, and that look is repeated at every glance.

**Generator check.** Not owed: the item is new work, classed `feature`.

**Reproduced 2026-11-23.** `src/anesthesia_sim/app/qt_chart.py` draws the line with `ONE_MAC_LINE_COLOR` and `ONE_MAC_LINE_DASH_PATTERN` and names it through `ONE_MAC_LINE_LEGEND_NAME` only, with no label in the plot.
