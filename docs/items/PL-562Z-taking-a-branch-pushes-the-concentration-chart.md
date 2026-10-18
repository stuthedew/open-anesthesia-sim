---
id: PL-562Z
title: Taking a branch pushes the concentration chart mostly below the fold: in a 1600 x 1000 window the second run's readouts move it from y 520-880 to 848-1208 of the 1000 px page, so a learner who branched to compare two curves sees 152 of its 360 px without scrolling
priority: P2
effort: S
status: done
classes: ux
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_simulation_view.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
closed: 2026-10-18
pr: 1578
payoff: taking a branch leaves the concentration chart in view, so the comparison the learner asked for is on screen
verify: grep -q "def test_taking_a_branch_leaves_the_concentration_chart_in_view" tests/integration/test_simulation_view.py
---

**Problem.** Taking a branch pushes the concentration chart mostly below the fold: in a 1600 x 1000 window the second run's readouts move it from y 520-880 to 848-1208 of the 1000 px page, so a learner who branched to compare two curves sees 152 of its 360 px without scrolling

**Measured 2026-10-01** while working `PL-WPDB`, with a scratch probe under the
offscreen platform: the dashboard opened as `main.py` opens it, sized to
`tests/benchmarks/frame_cost.py`'s 1600 x 1000 window, one run against a trunk
and a branch taken at induction. The page's scroll viewport is 1586 x 1000 in
both. With one run the content is 1582 px tall and the concentration chart
spans y 520-880, wholly in view; with two it is 1986 px and the chart spans
848-1208. The wash-in chart is below the fold in both (1010-1308, then
1358-1684). `app/simulation_view.py` makes no call that scrolls the page (no
`ensureWidgetVisible` or scroll-bar write), so taking a branch leaves the
scroll where it was.

**Why it matters.** Taking a branch is the act of asking for a comparison, and
the comparison is drawn on the chart; the frame that answers it shows the
second run's readouts and a sliver of the chart. A maximized window on a
shorter screen loses more: the main window opens maximized (`PL-Z4K6`), and on
the 1366 x 768 laptop `main.py`'s docstring names, the one-run chart's lower
edge at 880 px would already sit below a viewport of roughly 700 px (inferred
from the measured positions, not measured at that size).

**Not decided here.** Whether the answer is a scroll on fork, a different
order of the page, or `ROADMAP.md`'s v0.6.0 layout work ("the layout is the
reader's") is the triage's call. `frame_cost.py` now scrolls the chart into
view before measuring (`_bring_chart_into_view`), so the harness's paint figure
no longer depends on this.

**Done when.** The answer below is recorded, and either taking a branch leaves the concentration chart in view at 1600 x 1000, held by a test, or the item closes into the v0.6.0 `Required scope` entry that owns the page's arrangement.

**Decision needed.** Whether to fix this before v0.6.0 replaces the single scrolling page, and how: (a) scroll the chart into view when a branch is taken - one `ensureWidgetVisible` call from the fork handler and a test; (b) re-order the page so the readouts do not sit above the chart; or (c) leave it to v0.6.0, whose tiled layout gives the chart its own view. **Recommended: (a).** It answers the click that asked for the comparison, v0.6.0 deletes it along with the page, and v0.6.0 is 4 L, 16 M and 3 S away. Its cost is a page that moves on a click; (b) is layout work v0.6.0 owns and would be redone, and (c) leaves every branch until then showing 152 of the chart's 360 px. It is the owner's because it is behaviour a learner sees.

**Re-read 2026-10-18 at `21174fd3`, in the product decision batch's design
round.** `app/simulation_view.py` still makes no call that scrolls the page
when a branch is taken. The pixel figures above were measured on 2026-10-01
and were not re-measured here. A build under (a) re-measures them in its
test. v0.6.0's build has not started: its gate has 20 entries open, and the
layout adapter (`PL-W9P6`) is blocked behind it. So under (c) the chart stays
mostly below the fold until that build ships. The recommendation stays (a),
and the question is put to the project owner, because the answer decides
what a learner sees after pressing Branch.

**Answered 2026-10-18: (a), scroll the chart into view when a branch is
taken** (project owner, 2026-10-18, ratified, over (c), leaving it to
v0.6.0's tiled layout, and over (b), re-ordering the page). Stuart tapped
"Scroll now" on the product decision batch's card at 03:55Z. The build
makes the fork handlers bring the concentration chart into view once the
branch's readouts are laid out. A test at 1600 x 1000 asserts that the chart
lies wholly inside the page's viewport after a branch is taken. The scroll
goes when v0.6.0 replaces the scrolling page.

**Built 2026-10-18 under (a).** `SimulationView._show_branch` ends both branch
controls. It calls `_keep_chart_in_view`, which scrolls the page with Qt's
`ensureWidgetVisible` so that the concentration chart is wholly in view. The
branch's readouts reach their final size over several passes of layout after
the press returns. A single scroll at the press, or one on a zero timer,
landed while the page was 1,568 px or 1,830 px tall and left the chart's lower
edge below the fold (measured with a scratch probe at 1600 x 1000). So the
view scrolls again each time the page's height changes, which the scroll bar
reports through `rangeChanged`. An event filter on the chart and its parents
did the same, but it ran on views being garbage-collected in
`tests/integration/test_dark_appearance.py` after their attributes had gone,
and printed 96 `AttributeError` tracebacks in `make check`. It stops when the reader
scrolls the page themselves, through the scroll bar's `actionTriggered`
signal, or when the trunk's Reset ends the comparison.

Re-measured at 1600 x 1000 before the fix: one run puts the chart at y 512-872
of the 1000 px viewport, and two runs at 869-1229. With the fix, two runs put
it at 640-1000.

`test_taking_a_branch_leaves_the_concentration_chart_in_view` (both branch
controls) and `test_the_page_stops_holding_the_chart_once_the_reader_scrolls`
hold it. Against the code before the fix, the first fails with
`assert 1229 <= 1000` for both controls, and the second with `assert 0 > 0`.
