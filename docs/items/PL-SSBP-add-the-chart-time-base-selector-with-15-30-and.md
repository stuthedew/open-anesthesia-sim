---
id: PL-SSBP
title: Add the chart time-base selector with 15, 30 and 60 minute scales plus Fit run
priority: P2
effort: M
status: done
classes: ux, feature
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/chart_time_base.py, src/anesthesia_sim/app/formatting.py
added: 2026-08-25
closed: 2026-09-05
verify: uv run pytest tests/unit/test_simulation_view.py && grep -q 'def test_a_run_shorter_than_the_selected_time_base_shows_whole' tests/unit/test_simulation_view.py
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

**The upper scales once cost more per frame than the budget allowed.**
Decimation rescanned every sample in the visible window on every frame, so
the per-frame cost was O(window) rather than O(points drawn). Recorded here
as history, and attributed to `PL-011` (bound the controller's history) when
it was first written; the cost was decimation's rather than the history
buffer's, and `PL-D9WD` is what removed it. Measured 2026-09-04:

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
again. `PL-D9WD` is that cache.

**That cache landed on 2026-09-04, so the constraint is lifted.** Measured
over the whole chart frame - six traces plus the wash-in plot - the cost is
now 1.7 ms at five minutes, 2.8 ms at fifteen, 3.0 ms at an hour and 2.6 ms
at twelve, against the 200 ms frame budget: flat, because a frame reads
completed aggregates rather than the samples the window spans. Every scale
on the settled list is affordable, and there is no longer a reason to split
the upper ones out. What this item still owes the upper scales is its own:
`MAX_CHART_WINDOW_S` is 300 s today, so nothing above five minutes has been
rendered yet, and a twelve-hour axis has label and tick decisions a
five-minute one does not.

**Done when.** The user can choose a time base from a list, the chart window
takes that width, and a run shorter than the selected scale still shows whole.

**Built 2026-09-05, and what was decided along the way.** The selector lists
the settled 15 minutes to 12 hours plus "Fit run", per the owner's 2026-09-04
note above rather than the title's older 15/30/60 - the perf constraint that
split the upper scales out is lifted, and `ROADMAP.md`'s Required scope line
was updated to match. Three decisions the brief did not settle:

- **The ladder reaches below the selector's floor** - 1, 2 and 5 minutes,
  reachable by fitting and not by choosing. "Fit run" is the default and has
  to answer at ten seconds; a fifteen-minute axis would draw the whole of
  induction into the leftmost 3% of the plot.
- **"Fit run" always fits.** Past the widest rung the ladder doubles rather
  than holding at 12 h, so the mode never quietly shows part of a run under a
  name that claims the whole of it.
- **The axis label carries its own unit** (`0`, `3m`, `1h30m`, `12h`) rather
  than a bare number under a captioned unit. A bare `12` means twelve minutes
  on one time base and twelve hours on another and looks identical on both,
  and a reader who misses the caption has nothing in the label to correct
  them.
