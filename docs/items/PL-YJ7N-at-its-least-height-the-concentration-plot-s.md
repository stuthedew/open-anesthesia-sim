---
id: PL-YJ7N
title: At its least height the concentration plot's data area is about 120 px and its hover box up to 113 px, so where the box fits neither above nor below the hovered point it sits at the plot's top beside the point and covers most of the plot to one side (measured offscreen on 2026-11-14, vessel-rich at 330 s in Induction at 1366 by 768)
priority: P3
effort: S
status: ready
classes: ux, defect
feature: window-is-the-frame
touches: src/anesthesia_sim/app/qt_chart.py, tests/integration/test_qt_chart.py
deferred-from: v0.7.0 - a new problem: #2134 (PL-CBYS, 2026-11-13) let the plot shrink to 160 px after the freeze; at 0947408 it was never shorter than 360 px, so the hover box always fitted above or below the point
added: 2026-11-14
payoff: A learner reading one value on a short concentration plot can still see the curve the value belongs to.
---

**Problem.** At its least height the concentration plot's data area is about 120 px and its hover box up to 113 px, so where the box fits neither above nor below the hovered point it sits at the plot's top beside the point and covers most of the plot to one side (measured offscreen on 2026-11-14, vessel-rich at 330 s in Induction at 1366 by 768)

**Found by** the review of `PL-CBYS`'s pull request `#2134`, on 2026-11-14.
Before `PL-CBYS` the plot was never shorter than 360 px, so the box always
fitted above or below the point. `#2134` puts it at the plot's top, beside the
point, when neither side has room. The box states the value it reports, so no
reading is lost, but the curve beside the point is hidden while the box shows.
A placement outside the plot, or a smaller box, would remove the overlap.

**Checked 2026-11-22**, at `d4e8200c`. `_HoverReadout.show` in `src/anesthesia_sim/app/qt_chart.py` still places the box at `self._top_value()` beside the point when the room both above and below is less than the box's height, and `CHART_LEAST_HEIGHT` in `src/anesthesia_sim/app/theme.py` is still 160 px. Before `#2134` the plot was never shorter than 360 px, so this problem arrived after the freeze.

**Why it matters.** A learner who hovers on a short plot to read one value loses sight of the curve beside it, which is the context the value is read in. The box gives the value it reports, so no reading is lost, and the curve returns when the pointer moves away.

**Done when.** On the concentration plot at its least height, the hover box no longer covers the curve beside the hovered point when it fits neither above nor below it, and a test shows where the box sits in that case. Where the box goes, outside the plot or as a smaller box, is this item's choice, recorded in the brief.

**Generator check.** A one-off. It is a consequence of `#2134` letting the plot shrink below the height the hover placement was written for. No head's `misread:` states where a hover box may sit.
