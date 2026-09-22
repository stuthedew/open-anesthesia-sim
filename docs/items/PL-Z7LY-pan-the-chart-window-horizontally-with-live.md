---
id: PL-Z7LY
title: Pan the chart window horizontally, with live-follow as an explicit state
priority: P3
effort: M
status: ready
classes: ux, feature
feature: chart-readout
touches: src/anesthesia_sim/app/chart_time_base.py, src/anesthesia_sim/app/simulation_view.py
added: 2026-08-25
---

> **Groomed 2026-09-22 (`PL-Y4YG`): still owed; its precondition landed and
> one reason under Notes is gone.** `PL-SSBP` (done 2026-09-05) shipped the
> time-base selector, so the narrower-than-the-run case exists, and
> `following_window` in `app/chart_time_base.py` still says "Panning away from
> the right edge, and saying unmistakably that it has happened, is a separate
> item" - this one. The `flet-charts` reason is obsolete: the chart is
> pyqtgraph now, which does offer drag and wheel, and `_plot` in
> `app/qt_chart.py` turns both off deliberately, because "a plot a reader
> could drag off its labelled range would show a slope that meant something
> different from the one beside it". The explicit-offset design stands on that
> and on its other two reasons, keyboard and touch use and testability. Since
> v0.5.0 two runs can share the axis, so the transitions to test gain two: a
> branch taken mid-pan, and panning with a second run on the chart. `touches`
> names `app/chart_time_base.py` beside `app/simulation_view.py`, which builds
> the time-base control.

**Problem.** Once a selected time base is narrower than the run (PL-SSBP),
the user needs to move the window across the run the way they would scroll a
document wider than the screen.

**Why it matters.** The safety-relevant half is the mode, not the motion. On a
running simulation a panned-back window shows history while the readouts above
it show now, and a learner reads stale values as current — the stale-state
misinterpretation `CLAUDE.md` names directly.

**Where.** `app/simulation_view.py`.

**Notes.** Model the state as a window offset driven by an explicit control,
and treat drag as an additive input later: `flet-charts` 0.86 exposes no chart
gesture handling, a drag-only affordance is unusable by keyboard and awkward
on touch, and an offset value is unit-testable where a gesture is not. While
the window sits at the right edge it follows new samples; once panned away it
stops following, says so unmistakably, and offers one-click return to live.
Test the transitions, not just the happy path: pan while paused then resume,
reset mid-pan, agent switch mid-pan.

**Done when.** The window can be moved across the run, and whether it is live
or holding position is unmistakable at a glance and reversible in one click.
