---
id: PL-YDKJ
title: Decide whether the chart should keep patching one control per plotted point
priority: P3
effort: S
status: done
classes: perf
feature: teachable-case
touches: src/anesthesia_sim/app/chart_series.py, src/anesthesia_sim/app/chart_downsampling.py, src/anesthesia_sim/app/simulation_view.py, ROADMAP.md
added: 2026-09-04
closed: 2026-09-08
pr: 481
verify: python3 tools/doc_check.py check && grep -q 'the ceiling this budget sizes against' src/anesthesia_sim/app/chart_series.py
---

**Problem.** `flet_charts.LineChartData.points` is a `list[LineChartDataPoint]`
where each point is a Flet *control* in the page's control tree, so a frame
reaches the client as one patch operation per changed coordinate. PL-Q197
measured what that costs: ~3 500 operations a frame saturated the Flutter
client on ~50 kB of actual data, and the fix for it — anchoring decimation to
absolute sample index — is a workaround for the transport rather than a
treatment of it.

No mature charting stack transfers a series that way. They take arrays and
re-render from them: rendering 1 800 points is trivial for a GPU, and the
expense here is entirely per-object tree diffing. That mismatch is why a
scrolling window still costs one full rebuild per bucket width (PL-Q197's
documented residual), and why any further tuning of the *selection* buys
progressively less.

**Why it matters.** Not urgent — after PL-Q197 the sustained rate is 98 ops/s
growing and ~1 350 ops/s scrolling, against the ~17 900 that saturated the
client, so the app works. It matters because it caps how far the chart can go:
more traces, a faster render cadence, a longer visible window or a second
chart all multiply a per-point cost that should not exist, and each would be
diagnosed from scratch as a new performance bug.

**Decision needed.** Accept that the chart is patched one control per plotted
point — sizing the drawn point count around it — or move the traces onto a
different rendering path. Answer it only when a scale, a trace count or a
render cadence is actually blocked by the ceiling; as of 2026-09-04 nothing
is, and `PL-Q197` plus `PL-CG7J` between them leave enough headroom.

**Options.**

1. Accept it. Document the ceiling and stop tuning the selection. Costs
   nothing now.
2. ~~Draw the traces on `flet.Canvas` as a path rather than as chart
   points.~~ **Measured 2026-09-04 and ruled out.** `Path.PathElement` is
   declared `@value` rather than `@control`, which suggested a path's whole
   vertex list would cross as one field. It does not: Flet's diff descends
   into value lists element by element, so a canvas polyline costs the same
   ~2 operations per vertex as a `LineChartDataPoint` does - 1 206 operations
   for 100 vertices across six traces, 36 006 for 3 000. There is no
   array-shaped transport inside Flet to move to.
3. Render server-side. `flet_charts` also ships `matplotlib_chart.py` and
   `plotly_chart.py`; one image per frame is one patch. Almost certainly too
   slow to redraw at 5 Hz in Python, and would lose live interaction — worth a
   measurement before dismissing.
4. A sweep display rather than a scrolling one, which is what physiologic
   monitors do and for this exact reason: a fixed set of columns overwritten
   in place by a moving cursor changes one column per frame instead of
   shifting every point. Domain-native and O(1), but a visible change to how
   the chart reads, so it is a design decision rather than an optimization.

**Where.** The decision is the deliverable; no code until it is made.

**Blocked on `PL-2FM6`, and why that is not a demotion (2026-09-08, `PL-YXXG`).**
The status is `blocked` rather than `needs-decision` so the edge is machine-
readable; the deliverable is still a decision, and this returns to
`needs-decision` when `PL-2FM6` (delete `RunHistory` and draw the chart from the
closed-form sampler) lands. `PL-2FM6`'s brief asks for exactly this ordering -
"the point-movement rate is its main input, and this item changes it" - and the
sizing formula below is written in the two quantities `PL-2FM6` replaces: it
anchors evaluation times to an absolute grid so a following window reuses all
but its newest column, and it places a column at every control event. Deciding
now would size the chart against a movement rate that is about to change. The
debt gate's own entry moved with this edit, from "Cleared before v0.5.0 begins"
to "Cleared by v0.5.0 itself".

**What the measurement leaves.** With option 2 gone, nothing changes the
per-point cost, so the only levers are how many points are drawn and how
often they change. That makes this item mostly a sizing question rather
than an architecture one: sustained traffic is about `2 * P^2 * T /
window_seconds` operations per second for `P` points across `T` traces,
since a rebuild costs `2PT` and the window crosses a bucket boundary every
`window / P` seconds. Options 3 and 4 remain, and both are larger than the
problem currently justifies.

**Prior art worth reading before deciding.** The *selection* half of this
problem is settled and the existing min/max envelope code already matches it:
M4 (Jugel, Jerzak, Hackenbroich, Markl, "M4: A Visualization-Oriented Time
Series Data Aggregation", PVLDB 7(10):797-808, 2014) groups a series into one
bucket per pixel column and keeps each column's min, max, first and last, and
proves the resulting line rendering is identical to plotting every point.
Largest-Triangle-Three-Buckets (Steinarsson, MSc thesis, University of
Iceland, 2013) is the other standard, optimizing perceived shape rather than
exactness — cited from general knowledge, not verified against the thesis.
`tsdownsample` (arXiv:2307.05389) surveys the current implementations. None of
them addresses the *transport* question above, which is this item's subject.

**Done when.** One of the options above is chosen and recorded, with the
reasoning, and either implemented or written into `ROADMAP.md` as intent.

**Decided: option 1 — accept it** (project owner, 2026-09-08). The chart goes
on patching one Flet control per plotted point. The ceiling is documented at
the lever rather than engineered around, and `CHART_COLUMN_BUDGET_PER_SERIES`
in `app/chart_series.py` is where it is written, because that is the number a
future session sizing the chart will be holding.

**What the two remaining options turned out to cost.** Both were measured on
2026-09-08 at the owner's request; `docs/WORKING_NOTES.md` § "Measured and
answered: a server-rendered chart is not the way out" carries the tables.

- **Option 3, render server-side.** The transport is better than this brief
  assumed - `flet_charts.MatplotlibChart` sends WebAgg frames over a dedicated
  `ft.DataChannel`, skipping the msgpack encode *and* the control walk - and it
  still loses. 44.4 ms a frame in the mode this chart is actually in, against
  about 10 ms today. Its cheap variant needs blitting, blitting needs fixed
  axes, and fixed axes means adopting option 4 as well; even then it is 9.6 ms
  at 1x and 34.8 ms at 2x, which any HiDPI display is. It also pulls numpy,
  against `docs/WORKING_NOTES.md` § "Decided: no numpy", and gives back
  `PL-KP7H`'s paused hover.
- **Option 4, a sweep display.** It buys *this* path nothing. `PL-YSZN`
  measured `page.update()` on a chart where nothing had changed at the cost of
  a full frame, linear in the point count and indifferent to how many moved. A
  sweep is O(1) in operations sent - which was `PL-Q197`'s bottleneck, and is
  what this brief's "domain-native and O(1)" was true of - and O(n) in the
  walk, which is today's. It remains a live idea as a *reading* change, and it
  is a prerequisite of option 3 rather than an alternative to it.

**Why this could be decided while `PL-2FM6` is open**, having been moved to
`blocked-by: PL-2FM6` by `PL-YXXG` two days earlier on the ground that
"the point-movement rate is its main input, and this item changes it". The
measurement says the movement rate is not an input to the cost that now
dominates - it was the input while the *client* was the bottleneck. What
`PL-2FM6` does change is where the drawn points come from, not how many
controls the chart holds, and the column budget still decides that. So option
1 is stable under it: the answer is the same before and after. The block is
removed rather than satisfied, and `PL-18ND` is what carried that finding.

**What would reopen this.** A scale the column budget cannot absorb - more
traces, a second plot, a faster cadence - or `PL-2QMK` becoming the binding
constraint, since a matplotlib figure rasterizes in any container and can be
asserted on in an ordinary test where a Flet chart cannot. The second is a
testability argument rather than a performance one and should be made on those
terms.
