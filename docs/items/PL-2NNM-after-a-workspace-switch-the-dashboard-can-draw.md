---
id: PL-2NNM
title: After a Workspace switch the dashboard can draw a View narrower than its least width for several passes of the event loop before the Areas settle (measured offscreen on 2026-11-14: Parameters 350 px wide against a 590 px least width in Induction at 1366 by 768, reaching 604 px after about ten passes and a frame), and the page-scroll test checks only the scroll bar, which cannot see the squeeze
priority: P2
effort: M
status: ready
classes: defect
feature: window-is-the-frame
touches: src/anesthesia_sim/app/area_layout.py, tests/integration/simulation_view/test_simulation_view_page.py
deferred-from: v0.7.0 - present-or-not unmeasured, deferred on a stated reason: the squeeze lasts a few passes of the event loop after a Workspace switch and then settles, no value is misread in it, and the area-sizing work it follows is finished
added: 2026-11-14
payoff: A Workspace switch never draws a View cut short of its least width, and the fit test would catch a change that made it do so.
reenters: PL-YJ21
---

**Problem.** After a Workspace switch the dashboard can draw a View narrower than its least width for several passes of the event loop before the Areas settle (measured offscreen on 2026-11-14: Parameters 350 px wide against a 590 px least width in Induction at 1366 by 768, reaching 604 px after about ten passes and a frame), and the page-scroll test checks only the scroll bar, which cannot see the squeeze

**Found by** the review of `PL-CBYS`'s pull request `#2134`, on 2026-11-14.
The reviewer added `assert frame.content.width() >=
frame.content.minimumSizeHint().width()` to a copy of
`test_no_shipped_workspace_scrolls_the_page`, and it failed for Induction at
1366 by 768 and 1920 by 1080 and Maintenance at 1366 by 768. Whether the same
lag exists on `main`, where an Area's need also followed its View's least
width, is not measured. A View's least width can grow when its first frame is
drawn, which would make the Areas settle again.

**A second case, 2026-11-14, after `#2134` brought `main` in.** In the test
Workspace with every View, the concentration plot sits at its least height,
and the first frame is drawn at a plot width of 979 px. Every later frame is
drawn at 990 px, so the first frame's curves have 1,092 points and the next
frame's 1,001. `test_hiding_a_trace_changes_only_what_is_drawn` now compares
from the second frame.

**Checked 2026-11-22**, at `d4e8200c`. The test gap is still there. `test_no_shipped_workspace_scrolls_the_page` in `tests/integration/simulation_view/test_simulation_view_page.py` still asserts only that each Area's horizontal scroll bar has a maximum of 0, and nothing compares a View's drawn width with its least width. The lag itself was not measured again. Whether it existed at the freeze is not measured either, so the presumption of presence applies.

**Why it matters.** A View drawn narrower than its least width cuts off or overlaps what it shows, which can include readouts and their units. Here it lasts several passes of the event loop after a Workspace switch, about a frame. The test meant to show that every shipped Workspace fits cannot see it, so a change that made the squeeze last would still pass.

**Done when.** After a Workspace switch, no View is drawn narrower than its least width on any frame, and a test of every shipped Workspace at the reference window sizes checks each View's drawn width against its least width as well as the scroll bar.

**Generator check.** An instance of the fact that `PL-YJ21` states, "a View's least size is read before Qt has applied the layout requests its last frame posted": the Areas settle, a View's first frame raises its least width, and the Areas settle again. `PL-YJ21` closed on 2026-10-19, before this was filed, so it is recorded as re-entering that head.
