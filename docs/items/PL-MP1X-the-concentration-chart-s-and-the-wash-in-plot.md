---
id: PL-MP1X
title: The concentration chart's and the wash-in plot's text alternatives leave out the predicted curve a held drag draws, so a screen reader is not told what the preview shows
priority: P3
status: untriaged
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/dashboard_frame.py
deferred-from: v0.7.0 - found after the freeze, not safety or science, and no user sees a wrong value from it; a preview needs a pointer drag, so the release waits only on the owner test drive (filed 2026-11-28)
added: 2026-11-28
---

**Problem.** While a reader holds a drag on a setting, the concentration chart and the wash-in plot draw the run's predicted curve under the new setting as a preview (`chart_frame.RunFrame.preview`). Neither chart's text alternative mentions it. `chart_frame.latest_values_lines` and `chart_frame.latest_wash_in_lines` read only the drawn run, so a screen-reader user hears the same description during a drag as before it.

**Why it matters.** WCAG 2.2 SC 1.1.1 asks that a text alternative serve the same purpose as the graphic (Understanding SC 1.1.1, https://www.w3.org/WAI/WCAG22/Understanding/non-text-content, read 2026-11-27). The preview is how the interface shows what a change would do before it is made. The chart's off-scale notice already names a clipped preview's peak, because nothing else on screen states a preview's values (`dashboard_frame.off_scale_notice`, `PL-5B1N`). A drag needs a pointer, so a keyboard or screen-reader user may rarely see a preview at all, which is the reason to check first whether the preview can be reached without one. I suggest P3.

**Approach.** First find out whether a keyboard adjustment of a dial shows a preview. If it does not, record that the preview is reachable only by pointer, and that the text alternative therefore has nothing to add, as a dated paragraph here. If it does, add one sentence per previewed run to each description, worded as the hover words a preview point, with the instant at the preview's end.

**Done when.** Either the dated paragraph above, or a test that holds a preview on each chart and reads its sentence in the description.

**How it was found.** The second blind review of `PL-R1M6`, 2026-11-28, noted that the wash-in description says nothing during a preview. The concentration chart's description, which `PL-T9RB` built, leaves it out in the same way.

**Generator check.** No head states the fact misread here, which is what a chart's text alternative has to cover: every curve the chart draws, a preview among them. `PL-T9RB` and `PL-R1M6` built the two descriptions from the drawn run alone, and this is the first item to name the gap.
