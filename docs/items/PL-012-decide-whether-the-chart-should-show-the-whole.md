---
id: PL-012
title: Decide whether the chart should show the whole run
priority: P2
effort: M
status: dropped
classes: ux
feature: chart-readout
touches: src/anesthesia_sim/app/simulation_view.py
added: 2026-08-23
closed: 2026-08-25
reason: Answered by the scoped v0.3.0 milestone rather than left open. ROADMAP.md's "Next milestone: v0.3.0 - the teachable case" settles it: the chart gets selectable 15, 30 and 60 minute scales plus a fit-the-run scale (PL-SSBP), so the run is viewable whole and windowed both. The question this item held open no longer has two sides.
---

**Problem.** The chart shows a scrolling 300 s window (`MAX_CHART_WINDOW_S`),
so on a run longer than five minutes the wash-in curve scrolls off the left
edge and cannot be seen again.

**Why it matters.** Sharper than first filed: this is a four-compartment
model, and what separates it from a toy is the separation of time scales.
Vessel-rich equilibrates in minutes, muscle over hours, fat over many hours.
Inside a 300 s window the fat and muscle traces are flat lines pinned near
zero forever, so three of the six traces are decorative and the phenomenon the
model exists to demonstrate is not merely inconvenient to see but unreachable.
PL-001 also removed the payload reason for the window: with decimation to a
fixed per-trace budget, a longer span costs nothing.

**Where.** `app/simulation_view.py` (`MAX_CHART_WINDOW_S`, `_refresh_view`,
`vertical_grid_lines`).

**Decided.** The chart gains a user-selected time base, and this item builds
its default mode.

The agreed end state is a control offering a list of durations — 15, 30 and
60 minutes to start, the full list to be settled later — plus a "Fit run"
entry. The selected duration is the width of the visible window: when the run
is longer, the user pans horizontally as they would across a document wider
than the screen; when the run is shorter or equal, the whole run is shown.
"Fit run" is the default, so a learner sees the complete curve without
discovering a control first.

A fixed-width window that pans is better than a continuously growing axis
because seconds-per-pixel stays constant, so trace slopes remain directly
comparable — a continuously rescaling axis changes apparent slope while the
underlying rate does not, which is a misleading visual encoding. It also
matches the sweep-speed control a clinician already reads, and it subsumes
zoom: choosing 15 minutes on a 30 minute run *is* zooming.

Two constraints the design must carry, recorded here because they are the
parts most easily lost:

- **Live-follow is an explicit, visible state.** While the window sits at the
  right edge it follows new samples; the moment the user pans away it stops
  following, says so unmistakably, and offers a one-click return to live.
  Without this, a panned-back window shows history while the readouts above it
  show now, and a learner reads stale values as current.
- **Gridline interval is derived, never fixed.** `vertical_grid_lines` is
  currently `interval=60`, which over a four-hour span is 240 lines and a
  solid block.

This item covers the "Fit run" mode only: pin `min_x` to 0, rescale `max_x` in
discrete labelled steps rather than continuously, derive the gridline interval
from the current step, and state the displayed span in the axis caption, which
currently reads "Vertical axis: percent | Horizontal axis: simulated seconds".
The scale selector and the pan/live-follow machinery are separate items.

**Done when.** The chart shows the whole run by default, its x-axis rescales
in discrete steps with a gridline interval derived from the current step, the
axis caption states the span actually shown, and the choice is recorded rather
than left as an artifact of an earlier payload limit.
