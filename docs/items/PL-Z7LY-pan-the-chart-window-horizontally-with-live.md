---
id: PL-Z7LY
title: Pan the chart window horizontally, with live-follow as an explicit state
priority: P3
effort: M
status: ready
classes: ux, feature
feature: chart-readout
touches: docs/INTERFACE.md, src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/chart_time_base.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/run_presentation.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/view_contract.py, src/anesthesia_sim/app/views.py, tests/integration/simulation_view/simulation_view_support.py, tests/integration/simulation_view/test_simulation_view_held_window.py, tests/integration/simulation_view/test_simulation_view_run_values.py, tests/integration/test_layout_adapter.py, tests/integration/test_qt_chart.py, tests/integration/test_view_contract.py, tests/unit/test_chart_frame.py, tests/unit/test_chart_time_base.py, tests/unit/test_dashboard_frame.py, tests/unit/test_run_presentation.py
added: 2026-08-25
verify: grep -qE 'def test_pan' tests/unit/test_chart_time_base.py
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

**Checked 2026-11-22** against `d4e8200`: still applies. The docstring of `following_window` in `src/anesthesia_sim/app/chart_time_base.py` still says panning away from the right edge is a separate item. `_plot` in `src/anesthesia_sim/app/qt_chart.py` still turns off mouse drag and wheel. The window is now computed in `src/anesthesia_sim/app/chart_frame.py`, which `touches:` does not name.

**Done 2026-11-23.** At a chosen width, an arrow either side of the
time-base selector steps a chart's window to a gridline at least one interval
earlier or later. A window moved earlier holds still while the run goes on. The
axis title then ends "held: not following the run", and a line under the
controls, in the warning colour, says "Showing 30m to 45m. The run is now at
50m." beside a "Follow the run" button. A step later that reaches the window
that follows the run ends the hold, and so do "Follow the run", "Fit run", a
Reset and an agent change. Pausing, resuming and a branch leave it held. The
held edge is not saved. Both chart Views have the controls (`_TimeWindow` in
`app/views.py`), and frames are now keyed by `ChartWindow`, the width with the
held edge, so two charts at one width but different holds get their own frames.

**Best practice read before the design (2026-11-23).**

1. Logz.io, Live Tail documentation,
   https://docs.logz.io/docs/open360/explore/live-tail/ (page read): "The
   state is always visible, so you know whether what you're looking at is
   current"; states "Live" and "viewing earlier"; "Jump to newest returns you
   to the live edge and resumes following." This set the always-visible held
   state and the one-click return.
2. MUI X Chat, scrolling behavior,
   https://mui.com/x/react-chat/behavior/scrolling/ (page read): auto-scroll
   stops when the reader scrolls away, a button returns to the newest, and
   following resumes at the bottom. This set "a step later that reaches the
   run follows it again".
3. Rockwell FactoryTalk ViewPoint ME help, "Pause a trend" (page read): a
   paused trend stops scrolling to new data while the data are still
   collected. This set "new samples do not move a held window".
4. GE Vernova, Proficy Operations Hub, "Move Around the Trend Chart",
   https://www.gevernova.com/software/documentation/opshub/version2025/windows/r_oh_trend_pan_zoom.html
   (page read): separate Live and Historical modes, and "if you are currently
   viewing trends during 1-2pm, you can scroll back in time to view
   12:45-1:45pm, then return to the current view", a quarter of the window
   per step. This set the step size, one to two gridline intervals.
5. Riley V., "Reducing Mode Errors Through Design", Aviation Today, 2005 (page
   read): "make the modes more obvious to prevent loss of mode awareness", and
   uncommanded mode changes are a common source of mode error. This set the
   warning-coloured line and the rule that only a reader's action or the
   loss of the held history ends a hold.

**Placement, measured 2026-11-23 at 1366 by 768.** The concentration View's
least width was set by its legend (488 px under DejaVu Sans), not by its
controls row (415 px), so the two 37 px arrows raised the least width only from
516 px to 533 px (486 to 528 px in the container's font), inside the narrowest
shipped Area, 576 px in Maintenance. Its height was unchanged (301 and 305 px).
The held line is conditional, so it adds about 22 px only while a window is
held, as the View's other advisories do (`PL-S6CP`). The step size, the arrow
glyphs, the wording and the warning colour are placeholders.

**Files checked in the docs sweep:** `docs/INTERFACE.md` (§ "The chart's time
base", updated), `docs/MODEL.md`, `docs/VERIFICATION.md`, `docs/ARCHITECTURE.md`,
`README.md` and `ROADMAP.md`. Only `ROADMAP.md` names panning, in a completed
milestone's out-of-scope list, which is a record and was left as it is.
