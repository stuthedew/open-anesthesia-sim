---
id: PL-1K9G
title: Which grid column a trace answers a hover at is decided in two dimensions, so a purely vertical 2 px move can change the instant a value is labelled with
status: untriaged
feature: compartment-trace-legibility
added: 2026-09-20
---

**Problem.** Which grid column a trace answers a hover at is decided in two dimensions, so a purely vertical 2 px move can change the instant a value is labelled with

**Found 2026-09-20 while closing `PL-0RZ0`** (the hover's compartment flip),
and not fixed there: it is a different mechanism, its own decision, and the
fix-now door admits neither a new test nor a decision.

`nearest_trace_point` keeps each `(run, compartment)`'s nearest drawn point by
`_pixel_distance`, which composes the time and percent axes. So where two grid
columns are near-equidistant in time, the pointer's *height* decides which of
them a trace answers at - and a 2 px move up or down can change the instant on
a value line while the value itself is unchanged. Observed on the branched
sevoflurane case at t = 1200 s: muscle answers at 19m56s and fat at 20m for the
same run under one pointer, and moving the pointer 2 px up moves muscle's line
to 20m.

**Why it is probably not the same defect.** `PL-0RZ0`'s failure was that the
box named a different *trace* - a value under the wrong label. Here the label
is right, the compartment is right, and only the instant moves, by one grid
column: 4 s on the 60-minute axis, 48 s on the 12-hour one. The value at the
two columns is usually equal to the displayed precision, which is why nothing
had noticed.

**Why it may still be one.** Across a control event or a steep kink, two
adjacent columns can differ by more than the displayed resolution, and then a
vertical hand movement changes a printed concentration with nothing in the box
moving except the instant - which is exactly the shape `PL-JVHL` and `PL-0RZ0`
both closed. Nobody has measured how often two adjacent drawn columns differ by
at least one displayed digit, and that measurement is the first step here
exactly as it was in `PL-0RZ0`.

**The obvious candidate fix, and its cost.** Choose the column by time alone -
the pointer names an instant, the trace answers at its nearest drawn instant -
and keep the pixel radius for deciding whether the trace answers at all. That
makes the instant a function of the pointer's x position only, which is what a
reader would predict. It would change which point some hovers report, so it
wants the same before-and-after scan `PL-0RZ0` ran rather than an argument.
