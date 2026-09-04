---
id: PL-SSBP
title: Add the chart time-base selector with 15, 30 and 60 minute scales plus Fit run
priority: P2
effort: M
status: ready
classes: ux, feature
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py
added: 2026-08-25
---

**Problem.** PL-012 decided the chart gains a user-selected time base and
built only its default "Fit run" mode. The selector itself does not exist.

**Why it matters.** The selected duration is the width of the visible window,
which is what makes a long run inspectable at a chosen resolution. It also
subsumes zoom: choosing 15 minutes on a 30 minute run is zooming, so this
removes the need for a separate zoom feature.

**Where.** `app/simulation_view.py`.

**Notes.** ~~The full duration list is deliberately unsettled~~ — **settled by
the project owner, 2026-09-04: 15 minutes to 12 hours to start**, discrete
steps rather than free pan-and-zoom, geometrically spaced so each step is a
meaningful change rather than a nudge. Gas Man's own functionality is the
floor and the intent is to extend the allowed simulation duration past it, so
the list grows toward days and weeks later; nothing in the selector's design
should assume 12 hours is the end of it. "Fit run" stays the default. The
gridline interval must derive from the selected scale, never be fixed.

**The upper scales are blocked on `PL-011`, and that is new.** Decimation
currently rescans every sample in the visible window on every frame, so the
per-frame cost is O(window) rather than O(points drawn). Measured 2026-09-04:

| Scale | Samples in window | ms/frame | Share of the 200 ms budget |
| ---: | ---: | ---: | ---: |
| 15 min | 9 000 | 8.9 | 4% |
| 30 min | 18 000 | ~12 | 6% |
| 60 min | 36 000 | 15.9 | 8% |
| 4 h | 144 000 | 62.6 | 31% |
| 12 h | 432 000 | **207.7** | **104%** |

The three originally agreed scales are all comfortably affordable, so this
item can ship 15/30/60 plus "Fit run" as it stands. Anything past about an
hour cannot, until per-bucket extremes are computed once and kept instead of
rederived each frame — which `PL-Q197` made possible by anchoring buckets to
absolute sample index, since a completed bucket's extremes never change
again. `PL-D9WD` is that cache. Either split the upper scales out or take
`PL-D9WD` first; do not ship a selector offering a scale that stalls the
interface.

**Done when.** The user can choose a time base from a list, the chart window
takes that width, and a run shorter than the selected scale still shows whole.
