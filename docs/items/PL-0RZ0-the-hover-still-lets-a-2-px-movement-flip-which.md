---
id: PL-0RZ0
title: The hover still lets a 2 px movement flip which *compartment* answers where two compressed traces contend, which PL-JVHL fixed only for runs
status: untriaged
added: 2026-09-20
---

**Problem.** The hover still lets a 2 px movement flip which *compartment* answers where two compressed traces contend, which PL-JVHL fixed only for runs

`PL-JVHL` took the *run* out of the pointer's hands - every run inside
`HOVER_RADIUS_PIXELS` now answers - but it deliberately left distance settling
which **compartment** answers, because a reader aims at a curve and that is the
one thing distance is good for. The cause it names is untouched, though: the
percent axis is scaled by the alveolar peak, so the slow compartments are
compressed near zero, and two of *them* contend with each other exactly as two
runs' copies of one of them did.

**Where it bites.** `COMPARED_COMPARTMENT_CAP` is 2, so a reader comparing two
runs picks two compartments; picking muscle and fat puts two traces inside one
hover radius of each other for most of a run. The single-run chart has the same
exposure across all six. Measured incidentally on 2026-09-20 while closing
`PL-JVHL`: at 20 minutes on the branched sevoflurane case, the trunk's and the
branch's fat values land on the *same* pixel row of a 480 px plot - sub-pixel,
not merely close - which is the compression this turns on.

**Not measured, and that is the first step.** `PL-JVHL`'s own lesson is that
two of the three plausible targeting rules changed nothing once counted, so
this wants the same scan before any rule is proposed: the share of the
hoverable area where two *compartments* of one run sit inside the radius, and
the share of those where a 2 px move changes which one answers. If the numbers
are small, the honest answer is to record that and close it.

**Why it may be the axis rather than the targeting.** The same paragraph
`PL-JVHL` ends on applies here with more force: separating the compartments'
scales removes the contention at its source (`PL-QYBW`), and unlike the run
case there is no "answer for both" rule available - the box names one
compartment on line 2, and a reader aiming at muscle does not want fat's value
beside it. So the candidate rules are narrower: prefer the trace the pointer is
nearest *along its length*, prefer the one the reader most recently hovered, or
leave it and fix the axis.

**Where.** `src/anesthesia_sim/app/chart_frame.py` (`nearest_trace_point`, the
`aimed_at` selection); `docs/MODEL.md` § "Where more than one run answers"
states the current rule.

**Why it matters.** The same failure as `PL-JVHL`'s, one axis over: the box
prints a compartment name and a value, and a hand movement too small to aim
with changes which compartment that is. Fat and muscle at the same instant can
differ severalfold, and nothing in the box moves except the words a reader has
already read past.

**Done when.** The contention is measured, and either a targeting rule removes
the flip or the measurement is recorded and the item dropped in favour of
`PL-QYBW` (the shared percent axis compressing the slow compartments).
