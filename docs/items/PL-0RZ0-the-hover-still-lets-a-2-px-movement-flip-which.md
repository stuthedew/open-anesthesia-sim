---
id: PL-0RZ0
title: The hover still lets a 2 px movement flip which *compartment* answers where two compressed traces contend, which PL-JVHL fixed only for runs
priority: P1
effort: S
status: needs-decision
classes: safety, ux
feature: compartment-trace-legibility
touches: src/anesthesia_sim/app/chart_frame.py, docs/MODEL.md, tests/unit/test_chart_frame.py
added: 2026-09-20
payoff: stops the hover box naming fat's value under muscle's label when the reader's hand moves 2 px, where the two can differ severalfold
verify: grep -q 'def test_two_compartments_within_one_hover_radius' tests/unit/test_chart_frame.py
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

## Measured 2026-09-20: the contention is real, and one premise above is not

`PL-JVHL`'s geometry reproduced exactly - reference adult on sevoflurane, a
60-minute axis 900 px wide and `theme.CHART_HEIGHT` (360 px) tall, so 4.00 s/px
and 0.0167 %/px against an `axis_top_percent` of 6.00%. The trunk raises its
dial by half at 10 minutes, which is the keyframe a fork there needs and what
`tests/integration/test_qt_chart.py`'s own branched case does; the branch forks
at that instant under each of three managements. The scan walks every pixel of
the plot, and its selection was held against `nearest_trace_point` itself at
400 random pointer positions per case before any number below was kept.

Share of the hoverable area where two or more **compartments** have a drawn
point inside the 12 px radius, and - of the pointer pairs 2 px apart where both
positions are contended - the share whose aimed-at compartment changes:

| Chart | Compartments | Two or more in reach | 2 px flips the compartment |
| --- | --- | ---: | ---: |
| one run | all six | 37.0% | 12.7% |
| two runs, branch doubled to 2 MAC | muscle + fat | 15.2% | 9.3% |
| two runs, branch raised to 1.25 MAC | muscle + fat | 19.1% | 9.2% |
| two runs, branch's vaporizer off | muscle + fat | 45.7% | 7.5% |
| two runs, branch doubled to 2 MAC | mixed venous + vessel rich | 5.1% | 12.8% |
| two runs, branch raised to 1.25 MAC | mixed venous + vessel rich | 29.4% | 6.6% |
| two runs, branch's vaporizer off | mixed venous + vessel rich | 27.5% | 8.2% |
| two runs, branch doubled to 2 MAC | alveolar + fat | 0.5% | 13.6% |
| two runs, branch raised to 1.25 MAC | alveolar + fat | 0.5% | 13.6% |
| two runs, branch's vaporizer off | alveolar + fat | 24.0% | 6.7% |

**The flip changes the number, not only the word.** Across every case the two
compartments' values print differently on 99.9% of flips. For muscle against
fat the ratio is a median 17.1-17.9x and **every** flip is twofold or more; for
mixed venous against vessel rich it is 1.3x and none reaches twofold. So the
severalfold claim in `**Why it matters.**` above holds for the pair that
contends most, and is an overstatement for the pair beside it.

**And it is silent, which is the part that carries.** The box hangs from the
aimed-at point (`app/qt_chart.py`, `setPos(anchor.time_s, anchor.value)`), and
at a flip the two winning points are a median 0.9 px apart - 100% of them
within 2 px - so the box does not move. Worked case, branch's vaporizer off,
t = 1200 s, the pointer moved 2 px up the percent axis; the two boxes are the
same four lines at the same instant under the same run labels:

```
Modelled sevoflurane            Modelled sevoflurane
Fat                             Muscle
Run 1 · 20m   0.01%   0.01 ×MAC Run 1 · 20m   0.19%   0.09 ×MAC
Run 2 · 20m   0.01%  <0.01 ×MAC Run 2 · 20m   0.09%   0.05 ×MAC
```

**No compartment becomes unreachable, and that is worth recording because it
refutes the sharper complaint.** `docs/MODEL.md` already rules that "a
displayed value a reader cannot reach is worse than one that is hard to aim
at", which is what the near-tie tie-break was refused on. Measured here, every
compartment is answered for somewhere at 98% or more of the axis columns it is
drawn at - worst is muscle, unreachable at 2.0% of columns on the single-run
chart, and nothing else exceeds 1.2%. The defect is that the reader gets the
wrong trace, never that a trace cannot be got at.

### The premise that fails: "there is no answer-for-both rule available"

`**Why it may be the axis rather than the targeting.**` above rules the
`PL-JVHL` rule out on the grounds that the box names one compartment on line 2
and that a reader aiming at muscle does not want fat's value beside it. Two
measurements say otherwise.

1. **There is no aim to respect.** At a flip the two candidate points are a
   median 0.9 px apart. `PL-QYBW` states the same fact as its own second
   consequence: at that separation *no* targeting rule can let a reader aim at
   one trace rather than the other. A rule that picks is therefore picking
   arbitrarily, not honouring an aim.
2. **The box stays small.** Counting every `(run, compartment)` whose drawn
   point is inside the radius - which is what the rule would print - the box
   carries one value line on 21-93% of hovers, and never more than four on the
   two-run chart or three on the single-run six-compartment one:

| Chart | 1 line | 2 | 3 | 4 |
| --- | ---: | ---: | ---: | ---: |
| one run, all six | 63% | 25% | 12% | 0% |
| two runs, 2 MAC, muscle + fat | 58% | 32% | 4% | 6% |
| two runs, 1.25 MAC, muscle + fat | 21% | 66% | 2% | 11% |
| two runs, vaporizer off, muscle + fat | 47% | 16% | 23% | 14% |
| two runs, 1.25 MAC, mixed venous + vessel rich | 64% | 35% | 1% | 1% |
| two runs, vaporizer off, mixed venous + vessel rich | 71% | 28% | 1% | 0% |

The other two candidates this item names are refuted by `PL-JVHL`'s own
arguments, which transfer unchanged. **Nearest along its length** is the same
number as nearest drawn point on a trace sampled at about one point per pixel
against a 12 px radius. **Most recently hovered** is a tie window with memory:
it moves the boundary rather than removing it, exactly as the near-tie
tie-break did, and it makes the answer depend on the path the pointer took,
which is a hidden mode and a loss of the determinism the safety-critical
standard requires of a displayed value. A third, **preferring the compartment
higher in the trace table**, is worse than either: it would make fat
unreachable wherever muscle is inside the radius - up to 45.7% of the fat
trace - which is the failure `docs/MODEL.md` has already refused.

**Decision needed.** Whether to generalise the ratified run rule to
compartments, or to record the measurement above and drop this in favour of
`PL-QYBW` (the shared percent axis compressing the slow compartments).

The recommendation is to generalise it. Every `(run, compartment)` whose drawn
point is inside the radius answers; the three-line form stands exactly as
today whenever one compartment answers, which is most hovers; where more than
one answers, each value line names its compartment as it already names its
run. That is the only rule measured at zero, it is the rule this chart already
uses one axis over for the same cause, and its cost is the bounded box above.
It does not make `PL-QYBW` less worth doing - the axis is the source, and a
chart that draws fat in under 2 px is a legibility defect whatever the hover
says - but it is not blocked by it either, and the hover rule would still have
to be right after the axis changed.

Against it: this changes what a learner sees on a safety-relevant display, and
the cheaper reading is that a 12.7%-of-contended-pairs flip on a visible label
is tolerable until the axis is fixed. That reading is what the table above is
for.
