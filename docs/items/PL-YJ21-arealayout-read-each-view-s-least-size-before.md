---
id: PL-YJ21
title: AreaLayout read each View's least size before Qt had handled the layout requests that drawing a frame posts, so the Areas, and the page around them, were sized from what the Views needed before their first frame
priority: P3
effort: S
status: done
classes: defect, ux
feature: interface-areas
touches: src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/simulation_view.py, tests/integration/test_qt_rendering.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-10-19
closed: 2026-10-19
pr: 1686
payoff: the Areas and the page stand at their final sizes as soon as a frame is drawn, so no border move or pixel test meets a late relayout
verify: grep -q 'def _handle_layout_requests' src/anesthesia_sim/app/area_layout.py
root-cause-of: PL-4L8B, PL-PHPZ, PL-MXMG
generator: spent - AreaLayout.follow_needs reads every View's need only after Qt has handed out the posted layout requests
misread: a View's least size is read before Qt has applied the layout requests its last frame posted
---

**Problem.** `AreaLayout` read each View's least size before Qt had handled the layout requests that drawing a frame posts, so the Areas, and the page around them, were sized from what the Views needed before their first frame.

**Cause, traced 2026-10-19 on `main` at `2aab62b3`.** A View that builds,
shows or hides widgets while it draws changes its least size only once Qt
hands out the layout requests those changes post. Qt does that on the next
passes of the event loop, one level of widgets per pass. `AreaLayout._settle`
ran from `resizeEvent`, `showEvent` and a layout change, so it read each
View's `minimumSizeHint` either before the first frame or while requests from
it were still waiting. Two Views show it:

- The setting controls build their per-run copies on their first frame. Their
  Area's least width went from 0 to 590 px after the splitter had already
  given it 336 px (`PL-4L8B`).
- `_RunCopies.follow` shows each per-run line, and `_RunLines.show` hides the
  ones with no text, in the same frame. Until the requests were handed out,
  the concentration chart still counted two 15 px lines. Its least height read
  594 px instead of 564 px. That is the 30 px that `PL-4L8B`'s first fix
  attempt could not explain.

The page then laid the Areas out from a hint read at one of those moments
(`PL-PHPZ`), and changed height a pass or two later (`PL-MXMG`). In
`_EVERY_VIEW` at 1400 by 1000, the Areas stood at 1179 px for a hint of
1241 px straight after the first frame, and at 1241 px for a hint of 1196 px
once the event loop had run.

**Why it matters.** A reader saw the chart Area change width once at launch,
and the first border move after it jumped by about 250 px. A pixel measured in
a test depended on when it was read, which made a hover-box test fail in about
3 runs of 10. Every View that fills in on its first frame would have met the
same late relayout.

**Done when.** The Areas and the page stand at their final sizes straight
after a frame is drawn. A test shows the dashboard page keeping its height
from its first paint (`test_the_dashboard_page_keeps_its_height_from_its_first_paint`),
and each member's own test passes.

**Fixed 2026-10-19.** `AreaLayout.follow_needs` hands out every posted layout
request, and the ones those post, until a round hands out none
(`_handle_layout_requests`). It then reads the needs again, and where one
changed it settles the Areas, calls `updateGeometry` and hands out the
requests that follow. `refresh` calls it after the Views draw, and
`SimulationView` calls it again after each run's own surfaces are written,
because an `AccountingView` shows a run's accounting panel and the run writes
that panel after the Areas draw. Up to nine rounds were measured in the
dashboard, so the cap of 64 rounds is not reached.

**Generator check.** One fact misread by three readers of it: a View's least
size, read at a moment when Qt had not yet applied the View's last changes.
No head's `misread:` states it. It is spent, because the one place that reads
the needs now reads them after the requests are handed out.
