---
id: PL-QYBW
title: The chart's percent axis is scaled by the alveolar peak, so the slow compartments are compressed into 1-2 px and two runs' fat curves cannot be told apart by pointing
priority: P2
effort: M
status: needs-decision
classes: ux, defect
feature: compartment-trace-legibility
touches: src/anesthesia_sim/app/chart_frame.py, docs/MODEL.md
added: 2026-09-19
payoff: makes the slow compartments this simulator exists to teach visible on the chart that teaches them, instead of a flat line under 2 px
---

**Problem.** The chart's percent axis is scaled by the alveolar peak, so the slow compartments are compressed into 1-2 px and two runs' fat curves cannot be told apart by pointing

**Found 2026-09-19 while measuring `PL-JVHL`** (the hover answering for
whichever run is marginally nearer). That item is the symptom; this is the
mechanism underneath it.

`chart_axis_top_percent` scales the percent axis so the alveolar trace fills
it - `axis_top_percent` came out 6.00% on every case measured, against a fat
trace whose whole excursion is under 0.04%. At `theme.CHART_HEIGHT` (360 px)
that is 0.0167 %/px, so the six compartments the chart draws are not equally
readable: alveolar spans ~90 px and fat spans **under 2 px**.

**Measured 2026-09-19**, branched sevoflurane case, trunk held at 1 MAC,
fork at 10 min, the two runs' fat curves:

| Instant | Trunk | Branch (vaporizer off) | Apart on screen |
| ---: | ---: | ---: | ---: |
| 1200 s | 0.0086% | 0.0056% | 0.18 px |
| 2400 s | 0.0197% | 0.0062% | 0.81 px |
| 3492 s | 0.0300% | 0.0063% | 1.42 px |

**Why it matters.** Two consequences, and the second is the one that makes
this more than a legibility complaint:

1. **The compartments this chart exists to teach are the ones it draws
   least.** Fat and muscle are where the interesting behaviour of an inhaled
   agent lives - the slow filling that makes a long case different from a
   short one - and they are rendered as a flat line on the axis.
2. **Two runs' slow-compartment curves cannot be told apart by pointing.**
   At 0.2-1.4 px apart, no hover targeting rule can let a reader aim at one
   rather than the other, which is why `PL-JVHL`'s two candidate mechanisms
   both measured identically to the behaviour they were meant to replace.

**Not obviously a defect, which is why this is a captured finding rather than
a fix.** A shared axis is what makes the compartments comparable to each
other, and that comparison - alveolar above mixed venous above muscle above
fat - is a real teaching point that a per-compartment scale would destroy.
Any answer here has to keep it: a second axis for the slow compartments, a
log or split scale, or a separate detail view are all options with different
costs, and choosing between them is a design round rather than an edit.

**Scope.** Decide whether the chart keeps one percent axis; if not, what
replaces it and what the reader is told about the change of scale, which
`CLAUDE.md`'s safety-critical standard reaches directly - a curve whose scale
differs from its neighbour's and does not say so is a misleading visual
encoding.

**Decision needed.** Whether the chart keeps one shared percent axis for all
six compartments, and if it does not, what replaces it and what the reader is
told about the change of scale. The options carry different costs and none is
free:

1. **Keep the shared axis.** The comparison it buys - alveolar above mixed
   venous above muscle above fat, all on one scale - is a real teaching point
   and the ordering is itself the lesson. Cost: fat and muscle stay under 2 px
   and the slow filling this simulator exists to teach is invisible on the
   chart that teaches it; `PL-0RZ0` (the hover flipping which compartment
   answers) has no fix at all, because no targeting rule can separate traces
   0.2-1.4 px apart.
2. **A second axis for the slow compartments.** Recovers the detail. Cost: two
   curves on one plot at different scales is the misleading visual encoding
   `CLAUDE.md`'s safety-critical standard names, unless the change of scale is
   unmissable - so this option is only as good as its labelling, and the
   labelling is the hard part rather than the axis.
3. **A log or split scale.** One axis, all six legible. Cost: a log axis
   changes what "twice as much" looks like, which is the comparison a learner
   is being taught to make by eye; and a split scale has option 2's labelling
   problem with a discontinuity added.
4. **A separate detail view** for the slow compartments. Keeps the main chart
   honest and unchanged. Cost: the comparison across compartments moves to the
   reader's memory between two views, which is the thing option 1 exists to
   avoid, and it is the largest build of the four.

**This is the project owner's** rather than a session's: it changes what a
learner sees, and every option is defensible, which is the test rule 14 of
`.claude/rules/instruction-writing.md` sets. What is *not* theirs, and should be
in hand before they are asked, is the measurement `PL-0RZ0` owes - how much of
the chart's hoverable area has two compartments inside one hover radius - since
it sizes the cost of option 1.

**Done when.** The roadmap or this item records which axis treatment the chart
takes and what the reader is told about it, and either the chart implements it
or the decision is recorded with the reason the shared axis stays.
