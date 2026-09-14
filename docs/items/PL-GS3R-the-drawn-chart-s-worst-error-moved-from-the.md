---
id: PL-GS3R
title: The drawn chart's worst error moved from the control change to the steep early wash-in, and PL-4RBD's 0.32 MAC only fell to 0.26 MAC: uniform columns chord across the same width M4's buckets did
priority: P1
effort: M
status: needs-decision
classes: defect, safety
feature: teachable-case
touches: src/anesthesia_sim/core/run_definition.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/chart_frame.py, tests/unit/test_chart_frame.py, tests/unit/test_run_definition.py, docs/MODEL.md
verify: uv run pytest tests/unit/test_chart_time_base.py && grep -qF 'chord width' docs/MODEL.md
added: 2026-09-08
---

> **This ships with the Qt port, not before it.** The project owner decided
> 2026-09-10 that the fix waits for the Qt port (`PL-QXSB`, decided the same day);
> on Flet a wider budget costs frame time `PL-2FM6` had just given back, and
> after the port it is nearly free. `blocked-by` now says so, so nothing has to
> rely on a reader seeing this paragraph.

**Problem.** The drawn chart's worst error moved from the control change to the steep early wash-in, and PL-4RBD's 0.32 MAC only fell to 0.26 MAC: uniform columns chord across the same width M4's buckets did

**Why it matters.** `PL-4RBD` was re-banded `P1` `safety` on 0.32 MAC of
departure between the drawn trace and the run, and closed on the
understanding that evaluating columns removed it. Most of it is still there -
0.26 MAC at the 12 h base - and it has moved to the steep early wash-in,
which is the part of a case a learner is most likely to be studying. A trace
drawn below the run during induction, with nothing on screen saying the shape
between plotted points was inferred, is the presentation failure
`CLAUDE.md`'s clinical-output standard names rather than a fidelity
preference.

**Measured 2026-09-08, after `PL-2FM6` landed.** Same method as `PL-4RBD`'s
re-measurement - a real 12 h run at the envelope corner (FGF 10, V_A 12,
Q 10), sevoflurane 2% to 4% at t = 600 s, worst error of the drawn polyline
against the 0.1 s trace - but against the shipped evaluated columns rather
than against M4:

| Base | M4 alveolar | Evaluated alveolar | as MAC | worst at |
| --- | ---: | ---: | ---: | ---: |
| 15 min | 0.0124 pp | 0.0117 pp | 0.006 | t = 2.7 s |
| 1 h | 0.1005 pp | 0.0401 pp | 0.020 | t = 6.3 s |
| 4 h | 0.2145 pp | 0.1988 pp | 0.097 | t = 44.5 s |
| 12 h | 0.6467 pp | **0.5322 pp** | **0.260** | t = 85.8 s |

**What actually improved, and what did not.** `PL-2FM6` removed the *kink*
component: the worst error is no longer at the control change at t = 600 s,
which is `PL-4RBD`'s defect and is genuinely gone. It did **not** remove the
*curvature* component. Columns sit at the spacing the time base and the
column budget imply, and the chart rules a straight line between adjacent
columns - so at a 12 h base the chord spans about 290 s of a curve, which is
the same width M4's 4 096-sample bucket spanned. The error therefore fell
from 0.315 MAC to 0.260 MAC rather than to nothing.

**This corrects a claim made in `#488` and in `PL-4RBD`'s and `PL-2FM6`'s
close-out notes**, which said that most of the 0.65 pp was curvature "which
no selection of recorded extremes can reach" and that an evaluated column
therefore fixed both halves. The first half of that is true; the conclusion
does not follow, and the measurement above is what settles it. `docs/MODEL.md`
does not carry the error claim and needs no correction - it states the two
rules that place a column, both of which are accurate.

**Why the worst error moved to the start of the run.** The steep early
wash-in is where curvature is highest: the circuit fills on its own time
constant (V/FGF = 36 s at FGF 10 with a 6 L circuit) while the alveolar
trace lags it. A uniform grid spends the same column width there as it does
across an hour of near-equilibrium, so it is least resolved exactly where the
trace is most interesting - which is also where a learner watching an
induction is looking.

**Decision needed.** Whether to buy resolution with more columns, with a
curvature-adaptive grid, or to accept 0.26 MAC and state the bound in
`docs/MODEL.md`. Three routes, and they are not equivalent:

1. **More columns at wide time bases.** Cheapest to state, and it trades
   directly against the frame: `CHART_COLUMN_BUDGET_PER_SERIES` times traces
   drawn times about 24.5 us is the chart's share of a frame (`PL-YSZN`,
   `PL-YDKJ`), so doubling columns roughly doubles that share. At 150 columns
   a saturated frame was 42.8 ms against a 200 ms budget, so there is room -
   but it buys a factor of four in the error for a factor of two in cost, and
   it helps everywhere rather than where the curvature is.
2. **Non-uniform columns, denser where the second derivative is large.** The
   right answer numerically, and the expensive one: the chained-propagator
   optimisation `evaluate_anchored` depends on requires uniform spacing
   within a segment, and a propagator is about 1.29 ms against 6.2 us for a
   chained product. A curvature-adaptive grid would need its own scheme -
   perhaps a fixed dyadic refinement near each segment opening, which keeps
   the spacing uniform *within* each refinement level.
3. **Accept it and say so.** 0.26 MAC at a 12 h base, in the steep early
   wash-in, on a trace whose whole purpose is showing the shape of an
   induction. `CLAUDE.md`'s standard asks that uncertainty be visible rather
   than that it be zero, so an accepted bound stated in `docs/MODEL.md` is a
   legitimate answer - but it is the project owner's to give, which is why
   this is `needs-decision` rather than `ready`.

**Done when.** The project owner has chosen a route; if 1 or 2, the drawn
polyline's worst departure is measured again at every rung of
`TIME_BASE_LADDER` and recorded in `docs/MODEL.md`; if 3, `docs/MODEL.md`
states the bound and where it sits.


## Route 1 priced on real hardware, 2026-09-10 (PL-X9T3, PL-55DH)

The project owner ran the `PL-55DH` Qt spike at 600 columns and read its
instrument panel. This does not decide the item - the choice is still the
owner's - but the cost half of route 1 is no longer an estimate.

**Route 1's cost model above is Flet's, and it is the one term Qt does not
have.** "`CHART_COLUMN_BUDGET_PER_SERIES` times traces drawn times about 24.5 us
is the chart's share of a frame" is `PL-YSZN`'s per-point-control diff charge,
paid whether or not the point moved. Measured on Qt, 300x, a two-hour window at
6 399 s so 600 columns yield 3 204 points over six traces:

| Stage | 150 columns, 294 points | 600 columns, 3 204 points |
| --- | ---: | ---: |
| `refresh` (the score evaluation) | 7.57 ms | 18.24 ms |
| `handoff` (Flet's `page.update`) | 0.67 ms | 1.69 ms |
| `paint` | 8.04 ms | 21.57 ms |
| **whole frame** | **27.3 ms** | **49.4 ms** |

**So route 1 costs 49.4 ms of a 200 ms budget on Qt**, and about 8.7 us per
drawn point across evaluation, handoff and paint together. On Flet the same
3 204 points would cost about 78 ms in the diff alone, before the Flutter client
renders anything - so route 1 is comfortable on one toolkit and marginal on the
other, and becomes untenable on Flet once `v0.5.0`'s second chart doubles the
control count.

**Two things this does not say.** The two readings differ in fill as well as in
columns (32% against 89% of the axis), so neither factor is isolated - what is
established is the cost at 3 204 drawn points, not a clean columns-only slope.
And the error half of route 1 is still this item's own arithmetic: quartering
the chord width quarters the error to roughly 0.016 MAC, which nothing here
measures.

**The fidelity is visible as well as computed.** At 600 columns the drawn
curves are recognisably smoother through the steep early wash-in, which is
where this item records the worst departure.

**Relevance to `PL-QXSB`.** This is the clearest case in which the toolkit
decision and a safety decision are the same decision: route 1 is the cheap way
out of 0.26 MAC, and whether it is affordable depends on which toolkit the
interface is on.


## Decided, 2026-09-10: route 1, and it is the chord width that is held

**The project owner chose route 1**, on the pricing above. `PL-QXSB` was decided
in the same breath - the interface moves to PySide6 + pyqtgraph - which is what
makes route 1 affordable rather than marginal.

**Route 1 as a flat raise is not the right shape, and this item said why.** The
criticism recorded above is that more columns "helps everywhere rather than
where the curvature is". A *fixed column budget* is what produces that: the
chord spans `span / columns`, so at 150 columns it is 6 s at the 15-minute base
and 288 s at the 12-hour one, and the error follows it - 0.006 MAC against
0.260 MAC. The budget is the wrong invariant.

**So hold the chord width instead.** Columns become a function of the selected
span rather than a constant, which spends them where the error is and leaves the
narrow bases untouched. `CHART_COLUMN_BUDGET_PER_SERIES` stops being a budget
and becomes a floor.

That is still route 1 - buy resolution with columns - rather than route 2's
curvature-adaptive grid, and it keeps `evaluate_anchored`'s uniform spacing
within a segment, which is the property the chained-propagator optimisation
depends on and which route 2 would have to give up.

**What the work owes**, unchanged from this item's own "Done when": the target
chord width chosen against the 0.01 pp the readout resolves, the drawn
polyline's worst departure re-measured at every rung of `TIME_BASE_LADDER`, and
both recorded in `docs/MODEL.md`.

**Sequencing is the one open question** and it is in the reply, not here: whether
this ships on Flet now - where the wider budget costs frame time the owner has
just got back - or after the port, where it is free. The design above is the same
under either answer.


## Sequenced after the port, 2026-09-10

**"PL-GS3R after port"** - the project owner, answering whether this ships on
Flet now or waits. It waits.

**Why that is not a P1 being parked.** On Flet the fix costs what it is worth:
3 204 drawn points is about 78 ms of diff alone against a 200 ms frame, before
the Flutter client renders anything - and the lag that spending would reintroduce
is the same lag the owner reports `PL-2FM6` removed and which `PL-QXSB` was
opened on. After the port the same fix is 49.4 ms including paint, measured. So
waiting buys the fix at a quarter of the cost, on a defect whose worst case needs
a 12-hour time base to reach.

**What is not waiting**: the design. It is settled above - hold the chord width
rather than the column count - and it is the same under either toolkit, so the
port does not change what gets built, only when.

**The status was a compromise for one day and is not any more.** `blocked` is
the accurate status and the store rejects it without a blocker; on 2026-09-10
the blocker was a milestone decided and not yet named, and `blocked-by` accepts
only a version `ROADMAP.md` places. The port was scoped the same day, so this
now carries the closest edge the store has.

**It is not an honest edge, and `PL-L09X` says why.** `blocked-by: <version>`
means blocked until that milestone is *scoped* - `PL-W8XP` built it for exactly
that - and the port is scoped, so `docket check` advises this item is "ready to
promote". It is not: it is fully designed and waiting for the port to *land*.
`blocked` is kept anyway because `bin/docket next` excludes blocked items, so
the `P1` ranking hazard is gone and the only route to promotion runs through a
groomer reading this brief. The standing false advisory is the price, and
`PL-L09X` carries it.

**The seam is in place, 2026-09-14 (`PL-G59B`).** `chart_frame.chart_columns`
is the one function the chord-width rule replaces: every frame asks it for
the column count of the axis width it is about to draw, and it answers
`CHART_COLUMN_BUDGET_PER_SERIES` at every rung until this item chooses the
target width and re-measures the departure. Deliberately left at the floor
rather than set here: the target width is to be chosen against the 0.01 pp
the readout resolves, the worst departure at the 12 h base is not quadratic
in the chord (0.0117, 0.0401, 0.199 and 0.532 pp at 6, 24, 96 and 288 s of
chord) because the chord that matters is the first one on a curve whose time
constant is 36 s, and the frame cost of the count that reaches 0.01 pp is not
measured on any hardware. That is this item's measurement, and the port did
not take it.

**Promoted to `ready`, 2026-09-14**, `PL-G59B` having closed. The seam is `chart_frame.chart_columns`; see the note above.

## Measured 2026-09-14, on `main` after the port (`#578`): the chord that reaches 0.01 pp, and what it costs

The measurement the port left to this item, taken on the shipped read path. A
12 h sevoflurane run at the envelope corner (FGF 10, V_A 12, Q 10 - the maxima
`core/supported_ranges.py` declares), delivered 2% -> 4% at t = 600 s, built as
a `RunDefinition` in closed form (`advance_to(600)`, `record_change`,
`advance_to(43 200)`), so nothing is stepped. Truth is `evaluate_anchored` at
0.1 s, the step the run advances by: 432 001 instants. The drawn polyline at
chord h is `evaluate_anchored(0, 43 200, h)` - the anchored grid plus every
event column, which is the union of what `SimulationController.drawn_window`
draws across every window at that spacing - ruled straight between adjacent
columns, as pyqtgraph rules it. Error is |polyline - truth| at every truth
instant, on all six drawn compartments, in the percentage points the readout is
in. Same method as the 2026-09-08 table, which it reproduces (0.0116 pp at 6 s
of chord; 0.532 pp on the alveolar trace at 290 s).

| Chord | Columns at 12 h | Worst, any trace | Alveolar | as MAC | Beyond 300 s of an opening | Beyond 600 s | Beyond 1 800 s |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 5 s | 8 641 | 0.0088 pp (alveolar, t = 2.3 s) | 0.0088 pp | 0.004 | 0.0000 | 0.0000 | 0.0000 |
| 6 s | 7 201 | 0.0116 pp (alveolar, t = 2.7 s) | 0.0116 pp | 0.006 | 0.0001 | 0.0000 | 0.0000 |
| 10 s | 4 321 | 0.0271 pp (circuit, t = 604.6 s) | 0.0226 pp | 0.011 | 0.0001 | 0.0000 | 0.0000 |
| 15 s | 2 881 | 0.0509 pp (circuit) | 0.0330 pp | 0.016 | 0.0003 | 0.0000 | 0.0000 |
| 18 s | 2 402 | 0.0665 pp (circuit) | 0.0368 pp | 0.018 | 0.0005 | 0.0001 | 0.0000 |
| 24 s | 1 801 | 0.0995 pp (circuit) | 0.0401 pp | 0.020 | 0.0009 | 0.0001 | 0.0000 |
| 36 s | 1 202 | 0.168 pp (circuit) | 0.0510 pp | 0.026 | 0.0018 | 0.0003 | 0.0000 |
| 72 s | 602 | 0.362 pp (circuit) | 0.124 pp | 0.062 | 0.0077 | 0.0011 | 0.0001 |
| 144 s | 302 | 0.627 pp (circuit) | 0.314 pp | 0.157 | 0.0251 | 0.0042 | 0.0003 |
| 290 s | 151 | 0.888 pp (circuit, t = 67.9 s) | 0.532 pp | 0.266 | 0.0665 | 0.0111 | 0.0011 |

The reference adult's own settings (FGF 4, V_A 4, Q 5), 1 MAC -> 2 MAC at
600 s, same run length: 0.0016 pp at 5 s of chord, 0.0109 at 15 s, 0.0472 at
36 s, and 0.556 pp on the circuit trace (0.206 pp on the alveolar, 0.10 MAC) at
290 s; beyond 1 800 s of an opening, 0.0011 pp at 290 s.

**Four things the table settles.**

1. **The circuit trace is the worst-drawn one, not the alveolar.** 0.888 pp at
   the 12 h base, against the 0.532 pp this item and `PL-4RBD` reported for the
   alveolar trace. The circuit is the compartment with the shortest time
   constant (V/FGF = 36 s at FGF 10), so it is where a chord departs most. The
   alveolar figure was right; it was never the worst.
2. **0.01 pp on every trace needs a chord of 5 s**; 6 s gives 0.0116 pp. At the
   12 h base that is 8 641 columns - 58 times the floor - and 17 281 at a fitted
   24 h run, the supported length.
3. **The error is at the openings and nowhere else.** Beyond 1 800 s of any
   segment opening the shipped 290 s chord departs by 0.0011 pp on either run,
   a tenth of the readout's resolution, and beyond 600 s by 0.011 at the
   corner and 0.025 at the reference settings. A uniform grid spends 99% of
   its columns where the error is 1e-3 pp.
4. **Route 1 at the target is not affordable as measured.** Closed-form
   evaluation of the 12 h window on the web container (`evaluate_anchored`,
   median of 7):

   | Columns | 1 change in view | 5 | 20 |
   | ---: | ---: | ---: | ---: |
   | 150 | 9.4 ms | 21.8 ms | 67.5 ms |
   | 600 | 11.2 ms | 23.1 ms | 66.7 ms |
   | 2 400 | 21.6 ms | 31.6 ms | 70.3 ms |
   | 8 640 | 59.7 ms | 67.7 ms | 105.6 ms |
   | 15 000 | 98.9 ms | 110.5 ms | 148.0 ms |

   About 5.8 us per column plus 1.29 ms per change in view. On the ported
   path itself, offscreen on the same container, a 6-trace frame costs
   7.3 ms of Python at 150 columns, 22.0 ms at 2 400 and 65.3 ms at 8 641
   (`assemble_chart_frame` plus `ConcentrationChart.draw`, the evaluation
   being 57 ms of the last figure), before the toolkit paints. Paint is the
   larger term, and it is only extrapolated: `PL-X9T3`'s two readings on the
   owner's own hardware - 8.04 ms at 294 points, 21.57 ms at 3 204 - are
   4.65 us per drawn point over a 6.7 ms floor, which puts the 51 846 points
   of six traces at 8 641 columns at about 250 ms of paint alone, and the
   frame at about 320 ms at the 12 h base and 630 ms at a 24 h fit, against
   the 200 ms budget. Extrapolated from two points and not measured; but the
   cost is linear in the span whatever the slope, and the ladder is meant to
   grow toward days (`PL-SSBP`).

**Desflurane moves every number above by a factor of five to seven** (same
method, same day). 0 -> 12% at the fast corner, then 6% at 600 s - an
overpressure induction the interface allows - departs by **5.52 pp on the
circuit trace and 3.83 pp on the alveolar, 0.64 MAC**, at the shipped 290 s
chord. 0.01 pp on the alveolar trace needs a **2 s** chord there (1 s: 0.0031,
2 s: 0.0113, 5 s: 0.0549 pp); 18 s of chord leaves 0.36 pp on the circuit and
0.25 pp on the alveolar (0.04 MAC). Beyond 1 800 s of an opening the 290 s chord
is within 0.0024 pp. The slow corner (FGF 0.5, V_A 2, Q 2, same steps) is
benign: 0.31 pp on the circuit at 290 s, 0.0118 pp at 24 s, 0.0015 beyond
1 800 s. So this item is banded on the wrong agent - the defect is 0.64 MAC,
not 0.26 - and a uniform chord that reaches 0.01 pp on every supported case is
2 s: 21 601 columns at 12 h, 130 000 drawn points.

**Decision needed, again: what fidelity the drawn line owes, and by which
mechanism.** Route 1 as decided on 2026-09-10 - hold the chord at the width
that reaches 0.01 pp - is 2 s of chord on the shipped envelope, and cannot be
afforded on any hardware this project has measured. Four ways out:

- **A. Hold the chord at the width that reaches 0.01 pp everywhere.** The
  decision as taken. Five lines in `chart_columns`; 21 601 columns at 12 h,
  43 201 at a 24 h fit; about 160 ms of Python and 600 ms of paint per frame
  on the figures above. Out of reach, and linear in the span.
- **B. Hold a chord up to a column ceiling, and state the residual above it.**
  The same five lines plus a ceiling. At 2 400 columns the 12 h base draws an
  18 s chord: 0.07 pp (sevoflurane) and 0.36 pp (desflurane) on the circuit
  trace, 0.04 pp / 0.25 pp (0.02 / 0.04 MAC) on the alveolar, stated in
  `docs/MODEL.md`; 22 ms of Python here and about 110 ms per frame at 12 h on
  the paint extrapolation. Leaves a stated numeric residual and no visual
  guarantee.
- **C. The coarse chord the span implies everywhere, plus a fine chord for the
  first stretch after every segment opening in view.** The route-2 sketch in
  this item's own brief, made concrete. Reaches 0.01 pp on every trace for
  every supported case, with the constants set by the worst of them: 2 s over
  1 800 s, which is 900 columns per opening as a single level, or about 125 per
  opening as a dyadic stack (2, 4, 8, 16, 32 s to 60, 120, 300, 600 and 1 800 s)
  at five propagators - 6.5 ms - per opening. Cost follows the openings in
  view rather than the span: five openings is about 4 650 columns single-level
  or 775 dyadic. Uniform spacing within each level, so the chained propagator
  holds; fine columns anchored to the opening, which does not move. Costs the
  evaluator a second spacing and a refinement span (`evaluate_anchored`,
  `drawn_window`, `chart_frame`), tests for the merged grid, and a re-measure
  of the constants whenever the envelope grows - a new agent, a wider dial.
- **D. Hold the chord at one pixel: columns are the plot's width in logical
  pixels, floored at 150.** Visually exact at every base by construction:
  within one pixel column a monotone stretch rasterises to the same vertical
  run whatever its shape, which is the property Jugel et al. 2014 (M4, held in
  `docs/references/` and already cited by the chart) prove. Numerically the
  line between two drawn points is still a chord - 1.2 pp on the circuit and
  0.25 pp on the alveolar at 12 h on the desflurane case at 1 000 px - stated
  in `docs/MODEL.md` as a bound no display reads: the hover answers only at
  drawn points, and nothing else reads between them. Cost is 1 000-1 400
  columns at every base: about 13 ms of Python here and 40 ms of paint on the
  owner's hardware on the extrapolation, twice today's chart cost, independent
  of the span, and the same for any agent, dial or future rung. Five lines in
  `chart_columns` plus the plot width passed into the frame the way the time
  base already is, and testable at the pixel level with
  `tests/integration/test_qt_chart.py`'s painted-image harness: the chart at
  the 12 h base against the same run drawn at a 0.1 s chord. A fixed count at
  the widest plot the interface draws is the same route without the plumbing,
  at a fixed cost.

**Recommendation: D.** It matches the failure mode - what a learner sees -
holds for every case by construction rather than by constants measured against
an envelope that grows, costs five lines, and is testable end to end in the
pixels it claims. A cannot be afforded; B leaves a residual and guarantees
nothing visually; C is the route if the *line itself* must be within 0.01 pp -
principled and cheap per opening, its constants the worst supported case's,
and the most code. Under every route the Flet dashboard keeps its 150 columns
until `PL-25KS` ports it and `PL-7SVX` removes it: its per-point charge is what
forbade the raise in the first place, and `chart_columns` is the Qt chart's.
