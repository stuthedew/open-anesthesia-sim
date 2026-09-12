---
id: PL-YLKR
title: Design what a chart tooltip says: fl_chart's default is a bare number, and PL-KP7H makes the tooltip a paused-only readout that a reader will actually stop and study
priority: P1
effort: M
status: ready
classes: safety, ux
feature: presentation-safety
touches: docs/MODEL.md, src/anesthesia_sim/app/chart_series.py, README.md
added: 2026-09-08
verify: python3 tools/doc_check.py check && grep -qF 'what the tooltip may show' docs/MODEL.md
---

**Problem.** Design what a chart tooltip says: fl_chart's default is a bare number, and PL-KP7H makes the tooltip a paused-only readout that a reader will actually stop and study

**Where this now stands.** `PL-KP7H` landed the hover as a paused-only
affordance: points carry no tooltip while the run plays, because Flet's diff
descends into one on every point on every frame, and get one back the moment
the run stops, where the render loop takes no frames and the cost is nil. So
the tooltip has changed character. It used to be something a reader might brush
past on a moving trace; it is now the thing they get by deliberately pausing to
look at a value, which is exactly when what it says has to be right.

What it says today is `flet_charts`' default, from a
`LineChartDataPointTooltip(text=None)` this application never writes into.

**Three things it owes a reader**, and the first is the one only this project
can know:

1. **That the point is not a sample.** Every drawn point is an M4
   representative — the minimum, maximum, first or last of its bucket — and at
   300x on a long run one point stands for roughly 120 recorded samples. A
   tooltip reporting a y value as the value at that instant is false precision
   of exactly the kind `CLAUDE.md` names.
2. **Units, compartment and agent.** A bare number in a grey box satisfies none
   of the traceability the safety-critical standard requires of a clinically
   meaningful displayed value.
3. **Its own resolution.** `docs/MODEL.md` § "Displayed precision" derives what
   the readouts may show; nothing derives what this may show, and it should be
   the same derivation or an explicitly different one with a reason.

**And that it exists at all.** A hover that answers only while paused is a
hidden mode: a reader who tries it during a run gets nothing and concludes the
chart is not interactive, so they never find it. Whatever the tooltip comes to
say, something on screen has to say the affordance is there — a caption that
changes on pause is the cheap version. This is part of the same design rather
than a separate item, because a tooltip nobody can find and one nobody can read
fail a reader identically.

**Done when** the tooltip's content is designed and implemented, `docs/MODEL.md`
carries the derivation of what it shows the way it does for the readouts, and
`README.md` says the affordance exists and when.

**Why it matters.** `PL-KP7H` changed what this affordance is. While the tooltip
appeared on a moving trace it was something a reader might brush past; it is now
what a reader gets by deliberately pausing to look at a value, which is exactly
the moment its contents have to be right. A number somebody stopped the
simulation to read is one they will act on.

The safety-relevant half is the first of the three above and it is the one no
report of "it works" can answer: a drawn point is an M4 representative - the
minimum, maximum, first or last of its bucket - and at 300x on a long run it
stands for roughly 120 recorded samples. Presenting it as the value at that
instant is false precision of the kind `CLAUDE.md` names, and it is invisible to
the reader, who has no way to tell a representative from a sample.

**The port changes the mechanism, not the design.** `PL-G59B` replaces fl_chart
with pyqtgraph, so whatever fl_chart's default prints stops mattering - but the
three obligations transfer whole, and so does the hidden-mode problem, since a
paused-only affordance is equally undiscoverable in either toolkit. Design it
once here and implement against whichever chart is live. `PL-7H0X` was dropped
into this item for that reason.
