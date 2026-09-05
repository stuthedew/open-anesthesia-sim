---
id: PL-2LHF
title: The playback multiplier makes the chart's O(window) decimation cost reachable in minutes of wall clock, which PL-SSBP's frame-budget table was measured before
priority: P2
effort: M
status: needs-decision
classes: perf
feature: teachable-case
touches: src/anesthesia_sim/app/chart_downsampling.py, tests/unit/test_chart_downsampling.py, docs/items/PL-SSBP-add-the-chart-time-base-selector-with-15-30-and.md
added: 2026-09-05
---

**Problem.** `PL-SSBP` measured the chart's per-frame decimation cost on
2026-09-04 and recorded it as samples in the visible window: 144 000 samples
(4 h) at 62.6 ms/frame, and 432 000 (12 h) at 207.7 ms against a 200 ms
budget. Decimation rescans every sample in the window on every frame, so the
cost is O(window) rather than O(points drawn). That table was measured when
the only way to reach 432 000 samples was to sit in front of the application
for twelve hours, which made the last row a bound nobody would meet.

`PL-SN2C` shipped the playback multiplier the day after. At 300x, twelve
simulated hours takes 2.4 minutes of wall clock and four hours takes 48
seconds. The arithmetic in the table is unchanged and still correct; what
changed is that a reader can now reach its bottom row by accident, in a
sitting.

**Why it matters.** Nothing here is wrong on screen - the readouts stay
correct at every rate and the axis says which simulated seconds it shows -
so this is a responsiveness defect rather than a safety one. But it lands on
the one path where slowness reads as something else: a frame budget missed
while the clock is advancing at 300x leaves a chart that is stale against
readouts that are not, and a reader watching a fast run has no way to
distinguish "the display is behind" from "the model stopped moving". That is
the stale-state misreading `CLAUDE.md` names, arriving through frame rate.

Also worth stating for whoever picks this up: this is a *different* cost from
`PL-011` (bound the controller's concentration history), which is about the
memory an unbounded history holds. Bounding the history would cap this cost
as a side effect, but the two would be fixed differently - `PL-011` by
trimming what is kept, this by making decimation O(points drawn), which is
what `M4` grouping on a fixed index grid should already permit.

**Where.** `src/anesthesia_sim/app/chart_downsampling.py`, and `PL-SSBP`'s
own frame-budget table, which should say what wall-clock time each row now
corresponds to.

**Decision needed.** Whether to fix the cost or to state the bound. Making
decimation O(points drawn) - the M4 grouping on a fixed index grid the module
already cites - takes the window's sample count out of the frame budget for
good, and is a change to the chart's hot path in the middle of the milestone
that draws on it. Annotating `PL-SSBP`'s table with the wall-clock time each
row now takes at 300x costs a paragraph and leaves a 200 ms budget reachable in
2.4 minutes of sitting. The second is honest about the measurement and does
nothing about the staleness; the first is the real fix and is not free.

**Done when.** Either the per-frame decimation cost is independent of the
window's sample count, or `PL-SSBP`'s table carries the playback rate
alongside the sample count so the rows read as reachable rather than
theoretical - and the choice between those two is recorded.
