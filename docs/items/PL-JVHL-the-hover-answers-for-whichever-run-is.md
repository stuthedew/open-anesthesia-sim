---
id: PL-JVHL
title: The hover answers for whichever run is marginally nearer, so a 2 px hand movement silently swaps which run's value is read
priority: P1
effort: M
status: done
classes: safety, ux
feature: scenario-branching
milestone: v0.4.32
touches: src/anesthesia_sim/app/chart_frame.py, docs/MODEL.md, tests/unit/test_chart_frame.py
added: 2026-09-17
closed: 2026-09-20
pr: 743
payoff: a reader hovering a two-run chart stops silently reading the wrong run's concentration - the fat traces sit inside the hover radius together ~100% of the time, and the two values differ threefold
verify: grep -q 'def test_a_small_pointer_movement_never_swaps_which_run_the_hover_answers' tests/unit/test_chart_frame.py
---

**Problem.** The hover answers for whichever run is marginally nearer, so a 2 px hand movement silently swaps which run's value is read

`nearest_trace_point` and `nearest_wash_in_point` loop over every run on the
frame and keep the single globally nearest drawn point within
`HOVER_RADIUS_PIXELS` (12 logical px). With two runs on one axis the two runs'
points for the *same* compartment are frequently both inside that radius, so
which run answers is settled by arithmetic finer than a reader's hand — and
nothing in the box says which one won.

**Measured 2026-09-17**, reference adult on sevoflurane, trunk held at 1 MAC,
branch forked at 10 min, 60 min axis at 900 px wide and `theme.CHART_HEIGHT`
(360 px) tall, so 4.00 s/px and 0.0167 %/px. Share of the shared axis where
both runs' points for one compartment sit inside the 12 px radius, and share
where moving the pointer 2 px flips which run answers:

| Branch's management at the fork | Compartment | Both in radius | 2 px flips the run |
| --- | --- | ---: | ---: |
| doubled to 2 MAC | alveolar | 1.6% | 1.2% |
| doubled to 2 MAC | fat | 100% | 99.9% |
| raised to 1.25 MAC | alveolar | 8.5% | 8.4% |
| raised to 1.25 MAC | fat | 100% | 99.9% |
| vaporizer off | alveolar | 1.6% | 1.2% |
| vaporizer off | fat | 100% | 75.4% |

The fat row is 100% in every case, including against the widest management
difference available, because the percent axis is scaled by the alveolar peak
and the slow compartments are compressed near zero. The slow compartments are
what the chart exists to teach.

**Why it matters, and why it is consequential rather than cosmetic.** Of the hovers that could answer
for either run, the share that would print *different* text is 83.3–95.3%
(alveolar) and 43.8–81.4% (fat). Worked case, vaporizer off, fat at 3492 s:
`0.03%   0.02 ×MAC` or `0.01%   <0.01 ×MAC` depending on a 2 px movement — a
threefold difference in stored fat concentration between a run still carrying
agent and one 48 minutes into emergence.

**Not the same problem as `PL-MN4J`.** `PL-MN4J` decides whether the box
*names* the run. Naming it makes this flip visible rather than silent, which
is a large mitigation and the reason both sit under `scenario-branching` — but
it does not
make the hover answer for the curve the reader aimed at. That wants a
targeting rule: prefer the run whose curve the pointer is nearest along its
length, or require the pointer to be inside a run's own band, rather than
taking a global minimum over a set the reader cannot see.

**Where.** `src/anesthesia_sim/app/chart_frame.py` (`nearest_trace_point`,
`nearest_wash_in_point`); `docs/MODEL.md` § "The chart's hover readout".

**Found 2026-09-17** while measuring the case for `PL-MN4J`. Filed rather than
fixed: the fix is a change to the targeting rule, which that section derives,
and `CLAUDE.md`'s fix-now door admits neither a new test nor a decision.

**Done when.** A pointer movement of a few pixels cannot change which run the
hover answers for while both runs' points stay inside `HOVER_RADIUS_PIXELS` -
by preferring the run whose curve the pointer is nearest along its length, or by
requiring the pointer to be inside a run's own band, whichever the targeting
work settles on - a test in `tests/unit/test_chart_frame.py` drives the two-run
fat-compartment case that measures 100% ambiguous today, and `docs/MODEL.md`
§ "The chart's hover readout" states the rule the reader can rely on.

## Measured 2026-09-19: both candidate mechanisms above are refuted

**Neither of the two targeting rules the `Done when` names changes the
behaviour at all.** Scored against the branched sevoflurane case this item was
filed from - reference adult, trunk held at 1 MAC, fork at 10 min, 60-minute
axis 900 px wide and `theme.CHART_HEIGHT` (360 px) tall, reproducing the
recorded 4.00 s/px and 0.0167 %/px exactly - with the reader showing alveolar
and fat, which is the pair `COMPARED_COMPARTMENT_CAP` admits on a two-run
frame.

The metric is this item's own `Done when`, stated as a ratio: of the hovers
where **both** runs' points are inside `HOVER_RADIUS_PIXELS` before *and* after
a 2 px move, the share whose answering run changed.

| Targeting rule | fat, doubled to 2 MAC | fat, 1.25 MAC | fat, vaporizer off |
| --- | ---: | ---: | ---: |
| today: global nearest drawn point | 9.2% | 9.0% | 9.2% |
| **nearest curve along its length** | **9.2%** | **9.0%** | **9.2%** |
| **inside a run's own band (2 px)** | **9.2%** | **9.0%** | **9.2%** |
| **inside a run's own band (4 px)** | **9.2%** | **9.0%** | **9.2%** |
| distance, ties inside 2 px to run 1 | 0.0% | 0.0% | 0.0% |
| every run in radius answers | 0.0% | 0.0% | 0.0% |

Identical to the digit, on every case and on both compartments. Two reasons,
and each is a fact about this chart rather than about the implementation:

1. **"Nearest along its length" is the same number as "nearest drawn point"
   here.** The trace is drawn at one sample per ~4 s against a 12 px radius, so
   the pointer's distance to the polyline and to its nearest vertex differ by a
   small fraction of a pixel. The distinction those words draw is real on a
   sparse, steep curve and absent on this one.
2. **"Inside a run's own band" has to fall back to distance exactly where the
   defect lives.** Both runs' fat points are inside the 12 px radius over
   94.5-98.0% of the hoverable area, so the pointer is inside *both* bands
   almost always, and the rule then has to break the tie by the rule it was
   meant to replace.

**A stable tie-break fixes fat and makes alveolar worse.** Preferring the
lowest-numbered run where the two distances are within a tie window takes fat
to 0.0%, but on the alveolar trace of the 1.25 MAC case it moves the share of
contended axis columns that flip from 58.5% to **98.4%**: a tie window does not
remove the boundary, it adds a second one where the pointer crosses out of the
window. It also makes the branch's value unreachable wherever the curves are
within the window, which is most of the fat trace.

**The only rule measured at 0.0% everywhere is to stop choosing**: every run
whose point is inside the radius answers, and the readout carries a value line
per contended run. Nothing is then settled by which run is marginally nearer,
so no hand movement can swap it. Its non-zero number on the per-axis-column
metric (62.2%, alveolar, 1.25 MAC) is a different event - one run leaving the
radius, which the reader did deliberately and which the box shows by losing a
line, rather than a silent swap.

**The root cause is the shared percent axis, and it is worth naming
separately.** The slow compartments are compressed near zero because the axis
is scaled by the alveolar peak, which is what puts the two runs' fat curves
0.2-1.4 px apart. Separating the compartments' scales would make the curves
targetable and would remove this defect at its source, but it changes every
reading of the chart and is not this item's to take (`PL-QYBW`).

**Why this is a decision rather than the next commit.** Every rule that reaches
0.0% changes what the box *shows*, not merely which point it picks -
`docs/MODEL.md` § "The chart's hover readout" derives a three-line form at
length, and a fourth line is a change to a safety-critical display
specification. `CLAUDE.md`'s gate is a deliverable differing materially from
the one described, which this is, so it goes to the project owner rather than
being built and reported.

**Reproducing the harness**, since three details cost the measuring session
real time and none of them is visible from the call sites: a fork opens
**paused**, so `advance` is a no-op until `start()` is called on the branch; a
fork opens only at a **keyframe**, which only a setting that actually moves
records, so re-delivering the value already in force will not create one; and a
two-run frame draws `COMPARED_COMPARTMENT_CAP` (2) compartments, so the fat
trace is on the chart only when the reader has selected it.

**Not reproduced exactly.** On the item's own share-of-axis-columns metric this
run measured 29.8-72.3% for fat where the original recorded 75.4-99.9%. The
phenomenon is unambiguous either way; the gap is most likely the fresh-gas-flow
change this harness makes at the fork to record the keyframe, which the
original may have placed differently.

**Decision needed.** Which rule the hover uses where two runs contend, given
that both mechanisms this item originally named measure identically to the
behaviour they were meant to replace. Three answers, with what each costs:

- **(a) Every run inside the radius answers** - *recommended*. The only rule
  measured at 0.0% on every case and both compartments, and the only one that
  leaves both runs' values reachable. It costs a fourth line on the box while
  two runs contend, so `docs/MODEL.md` § "The chart's hover readout" gains a
  subsection deriving it beside the three-line form, and `HoverTarget` carries
  a value per contended run rather than one.
- **(b) Distance, with ties inside a window broken toward the trunk.** Keeps
  the three-line box exactly as specified. Takes fat to 0.0% but moves
  alveolar's contended-column flip share from 58.5% to 98.4%, and makes the
  branch's value unreachable across most of the fat trace - a displayed value
  that cannot be reached is worse than one that is hard to aim at.
- **(c) Leave the targeting alone and fix the axis compression** (`PL-QYBW`).
  Removes the cause rather than the symptom, and is the larger change: it
  alters every reading of the chart, so it is a roadmap question rather than
  this item's.

**Decided: (a), every run inside the radius answers** (project owner,
2026-09-19, ratified, over the stable tie-break in (b) and over deferring to
the axis-compression fix in (c)). Ratified on this session's recommendation
rather than specified, so `CLAUDE.md`'s lower bar to reopen applies: ordinary
evidence - a measurement, a cost the case did not carry - is enough, and the
case it rests on is the table above.

What that settles, and what it leaves to the session that builds it:

- **Settled.** Where more than one run has a drawn point inside
  `HOVER_RADIUS_PIXELS` for the hovered compartment, every one of them
  answers. Nothing is decided by which run is marginally nearer, which is what
  takes the flip rate to 0.0%.
- **Open, and a session's own.** How the box lays the runs out - the value
  lines' order, whether the compartment line is stated once above them or
  repeated per run, and what the box does at the three-run case the
  `COMPARED_COMPARTMENT_CAP` era does not yet reach. Those are phrasing and
  layout inside a decided rule, so they do not come back here.

Two constraints the build inherits rather than re-derives, both from
`docs/MODEL.md` § "The chart's hover readout":

1. **The qualifiers still precede the numbers.** That order carries the safety
   argument - a reader reaches a value through "modelled" and through the
   compartment it belongs to - so a multi-run box may not open with a column
   of numbers.
2. **Every number still goes through `app/formatting.py`.** `format_percent`,
   `format_mac_multiple` and `format_elapsed`, never the chart library's own
   formatter, with the below-resolution forms intact - the fat values this
   item turns on are exactly the ones that render `<0.01%`.

And the run must stay named per run, which `PL-MN4J` (the hover naming which
run it belongs to) decided on 2026-09-17 and this must not undo: with several
runs in one box the name is what attributes each line.
