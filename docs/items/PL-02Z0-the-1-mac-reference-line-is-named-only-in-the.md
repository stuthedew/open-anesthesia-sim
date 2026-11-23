---
id: PL-02Z0
title: The 1 MAC reference line is named only in the chart's legend and heading, so a reader has to look away from the plot to tell it from a trace; label it directly at its right end
status: untriaged
feature: presentation-safety
added: 2026-11-23
filed-pr: 2271
---

**Problem.** The concentration chart draws 1 MAC as a dashed `MUTED` line and names it only in the legend and the heading's reference text. A reader has to look from the line to the legend to tell it from a compartment trace. `PL-6W49` (tell the fat trace from the 1 MAC line) moved the fat trace off grey, so the two no longer look alike, but the line is still identified only at a distance from it.

**Recommendation.** Label the line at its right end, inside the plot, as "1 MAC". Wilke, *Fundamentals of Data Visualization* (O'Reilly, 2019), chapter 20 § 20.2 "Redundant coding", recommends labelling lines directly in place of a legend where the lines can be labelled; read it at source again before building, and check the label against the traces that pass under it at equilibrium.

**Done when.** The 1 MAC line carries its own label in the plot, the label never covers a trace's end value, and the label stays legible at the chart's minimum size.
