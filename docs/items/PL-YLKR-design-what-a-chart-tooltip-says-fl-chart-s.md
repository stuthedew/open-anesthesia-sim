---
id: PL-YLKR
title: Design what a chart tooltip says: fl_chart's default is a bare number, and PL-KP7H makes the tooltip a paused-only readout that a reader will actually stop and study
status: untriaged
added: 2026-09-08
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
