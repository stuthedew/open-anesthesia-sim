---
id: PL-S6CP
title: The concentration chart's least height of 280 px was measured with the offscreen font and no advisory, so in an Area held at that height (Induction at 1366 by 768) an off-scale, capped-trace or hidden-trace advisory, or a desktop font taller than the offscreen one, pushes the bottom of the plot and its time axis below the Area's edge until the learner scrolls; decide whether the chart's need follows the View's own layout, so the Areas move when an advisory appears, or stays a fixed number, so the plot scrolls
status: untriaged
feature: window-is-the-frame
added: 2026-11-14
---

**Problem.** The concentration chart's least height of 280 px was measured with the offscreen font and no advisory, so in an Area held at that height (Induction at 1366 by 768) an off-scale, capped-trace or hidden-trace advisory, or a desktop font taller than the offscreen one, pushes the bottom of the plot and its time axis below the Area's edge until the learner scrolls; decide whether the chart's need follows the View's own layout, so the Areas move when an advisory appears, or stays a fixed number, so the plot scrolls

**Found by** both blind review passes on `PL-CBYS`'s pull request `#2134`, on
2026-11-14. `_CHART_LEAST_HEIGHT_PX` in `app/view_registry.py` is 280 px: the
View's heading, the first two rows of its key box and the plot at its least
160 px, measured at 275 px with the offscreen font. The advisories sit outside
the key box, above the plot, so each one shown adds its height to what the
View needs. The View then scrolls inside its Area by that height, and the
bottom of the plot, with the time axis and the traces near zero, is below the
Area's edge. The constant is also a second copy of a fact the View's own layout
holds, and it is right only for the font it was measured with.

**Why it was not fixed on `#2134`.** Each fix is a choice between two
behaviours a learner sees. If the chart's need follows the View's own least
height, the plot always stays whole, but the Areas move each time an advisory
appears or clears, and the wash-in Area below gives up the room. If the need
stays a fixed number, the layout is stable, but the plot's bottom scrolls out
of view while an advisory is shown.

**A second case, from the adversarial review on 2026-11-14.** Taking a fork in
Induction at 1366 by 768 adds a second run, and the advisory that the chart
draws at most two compartments per run appears outside the key box (30 px).
The View's content becomes 311 px in the same 280 px Area, the plot sits at
y 137 to 297, and its bottom 17 px are scrolled out of view.
