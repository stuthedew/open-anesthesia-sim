---
id: PL-YJ7N
title: At its least height the concentration plot's data area is about 120 px and its hover box up to 113 px, so where the box fits neither above nor below the hovered point it sits at the plot's top beside the point and covers most of the plot to one side (measured offscreen on 2026-11-14, vessel-rich at 330 s in Induction at 1366 by 768)
status: untriaged
feature: window-is-the-frame
added: 2026-11-14
---

**Problem.** At its least height the concentration plot's data area is about 120 px and its hover box up to 113 px, so where the box fits neither above nor below the hovered point it sits at the plot's top beside the point and covers most of the plot to one side (measured offscreen on 2026-11-14, vessel-rich at 330 s in Induction at 1366 by 768)

**Found by** the review of `PL-CBYS`'s pull request `#2134`, on 2026-11-14.
Before `PL-CBYS` the plot was never shorter than 360 px, so the box always
fitted above or below the point. `#2134` puts it at the plot's top, beside the
point, when neither side has room. The box states the value it reports, so no
reading is lost, but the curve beside the point is hidden while the box shows.
A placement outside the plot, or a smaller box, would remove the overlap.
