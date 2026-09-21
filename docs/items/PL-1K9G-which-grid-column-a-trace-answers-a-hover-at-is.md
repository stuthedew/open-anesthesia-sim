---
id: PL-1K9G
title: Which grid column a trace answers a hover at is decided in two dimensions, so a purely vertical 2 px move can change the instant a value is labelled with
priority: P2
effort: M
status: ready
classes: defect, ux
feature: compartment-trace-legibility
touches: src/anesthesia_sim/app/chart_frame.py, tests/unit/test_chart_frame.py
added: 2026-09-20
payoff: two compartments of one run stop being labelled with two different instants in one hover box, so a reader comparing them is comparing one moment
verify: grep -q 'def test_every_compartment_of_one_run_answers_at_one_instant' tests/unit/test_chart_frame.py
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

**Why it matters.** Two compartments of one run can be labelled with two
different instants inside one hover box, so a reader comparing muscle against
fat "at the same moment" is comparing 19m56s against 20m. `CLAUDE.md`'s
safety-critical standard counts that as a presentation failure in its own
right - the correct number with the wrong patient context - and across a
control event or a steep kink the concentration itself can move by more than
the displayed resolution under a purely vertical hand movement, which is the
shape `PL-JVHL` and `PL-0RZ0` both closed.

**The class is provisional on a measurement nobody has run, and that is stated
rather than assumed.** This is triaged `defect, ux` at `P2` because the value
at two adjacent columns is usually equal to the displayed precision, which is
why nothing had noticed. How often two adjacent drawn columns differ by at
least one displayed digit has not been counted. That count is this item's first
step, and a non-trivial answer reclassifies it `safety` at `P1` - at which
point it re-enters the current gate unconditionally under § "The cadence"
rather than sitting in the deferral written for it. Do not treat the present
class as a finding about the hazard; it is a finding about what has been
measured.

**Done when.** The count above has been run and recorded; and either the column
a trace answers at is a function of the pointer's x position alone - with the
pixel radius kept for deciding whether the trace answers at all - or the item
records why composing both axes is right, with the before-and-after scan
`PL-0RZ0` ran rather than an argument; and a test under
`tests/unit/test_chart_frame.py` holds that every compartment of one run
answers at one instant.
