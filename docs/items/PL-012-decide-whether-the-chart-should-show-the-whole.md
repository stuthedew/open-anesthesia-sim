---
id: PL-012
title: Decide whether the chart should show the whole run
priority: P2
effort: S
status: needs-decision
classes: ux
touches: src/anesthesia_sim/app/simulation_view.py
added: 2026-08-23
---

**Problem.** The chart shows a scrolling 300 s window
(`MAX_CHART_WINDOW_S`), so on a run longer than five minutes the wash-in
curve scrolls off the left edge and cannot be seen again.
**Why it matters.** Wash-in and washout shape is the thing a learner is
there to see; a window that hides it works against the educational purpose.
The window was also the only thing bounding the drawn span, and PL-001
removed that constraint: with decimation to a fixed per-trace budget,
showing the entire run from t=0 now costs exactly the same as showing five
minutes of it.
**Where.** `app/simulation_view.py` (`MAX_CHART_WINDOW_S`, `_refresh_view`).
**Decision needed.** Show the whole run, keep the scrolling window, or offer
both. Showing the whole run means the x-axis rescales continuously, which
trades a stable time axis for a complete curve; a fixed window keeps the
recent detail legible. This is a teaching-design call, not a technical one.
**Done when.** The displayed time span is a deliberate, documented choice
rather than an artifact of an earlier payload limit.
