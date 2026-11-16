---
id: PL-2NNM
title: After a Workspace switch the dashboard can draw a View narrower than its least width for several passes of the event loop before the Areas settle (measured offscreen on 2026-11-14: Parameters 350 px wide against a 590 px least width in Induction at 1366 by 768, reaching 604 px after about ten passes and a frame), and the page-scroll test checks only the scroll bar, which cannot see the squeeze
status: untriaged
feature: window-is-the-frame
added: 2026-11-14
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
