---
id: PL-562Z
title: Taking a branch pushes the concentration chart mostly below the fold: in a 1600 x 1000 window the second run's readouts move it from y 520-880 to 848-1208 of the 1000 px page, so a learner who branched to compare two curves sees 152 of its 360 px without scrolling
status: untriaged
added: 2026-10-01
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
