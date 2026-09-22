---
id: PL-CNCF
title: controller.drawn_window costs 6.2 ms a frame at the shipped 150-column budget - 99% of the frame's read and about eighty times the simulation at 1x
priority: P2
effort: M
status: ready
classes: perf
feature: chart-readout
touches: src/anesthesia_sim/core/run_score.py, src/anesthesia_sim/app/controller.py, docs/MODEL.md
added: 2026-09-08
verify: grep -qF 'drawn_window costs' docs/MODEL.md && python3 tools/doc_check.py check
---

**Problem.** controller.drawn_window costs 6.2 ms a frame at the shipped 150-column budget - 99% of the frame's read and about eighty times the simulation at 1x

**Measured 2026-09-08**, on the 4-vCPU container `PL-YSZN` and `PL-QXSB` used,
against a 1 800 s run at the fitted 15-minute base, median of 40 calls:

| Call | Median |
| --- | ---: |
| `SimulationController.drawn_window`, 150 columns | 6.15 ms |
| ...at 600 columns | 9.69 ms |
| ...at 2 400 columns | 25.81 ms |
| fraction-to-percent conversion, six traces | 0.06 ms |
| `SimulationController.snapshot` | 0.02 ms |

So the whole of a frame's read is the score evaluation: 6.18 ms of 6.24 ms.
About 4.9 ms of it is fixed and about 8.7 us per column marginal.

**Why it matters, and it is two separate things.** The measurement lands on
a cost nobody had attributed, and it has one consequence for what the chart
may draw and a second for what the frame budget actually pays for.

**The column budget is now bounded here rather than by the toolkit.**
`CHART_COLUMN_BUDGET_PER_SERIES` is 150 because Flet charged ~24.5 us per
point control per frame whether or not the point moved (`PL-YSZN`). `PL-QXSB`
measured Qt drawing 648 000 points in 1.96 ms, which was read as "the budget
stops mattering". It does not: it stops being a *drawing* constraint and
becomes an evaluation one. Raising the budget fourfold costs 3.5 ms a frame,
and sixteenfold costs 20 ms - which at the 200 ms render budget is affordable
and at a 60 Hz ambition is not.

**At 1x the chart read is about eighty times the simulation.** A frame
advances two steps - 0.08 ms - and then spends 6.2 ms evaluating 150 columns
of a run it has already advanced. Inside Flet that is invisible under 26-45 ms
of `page.update()`, which is why nothing has reported it; on any toolkit
without a diff it is the whole frame.

**What it is not.** Not a defect in `PL-2FM6`, which bought exactness at
control changes that no selection over recorded samples could give
(`PL-4RBD` measured the old path at 0.32 MAC of departure at the 12-hour
base). This is the price of that, stated.

**Worth checking before sizing any fix**: whether `RunScore.evaluate_anchored`
re-propagates columns whose values cannot have changed. `PL-2FM6`'s brief
records that anchoring keeps the columns in fixed *positions* so that a steady
frame moves only the newest one; if the evaluation nonetheless recomputes all
150 every frame, the anchoring is buying stability without buying work, and
memoizing completed segments is the obvious lever.

**Done when** the per-frame evaluation cost is either reduced or recorded as
accepted with a number beside it, and `docs/MODEL.md`'s statement of what a
drawn window costs agrees with the measurement.

**Why it matters, and it survives the port.** This is the one frame cost in the
2026-09-08 measurements that is not Flet's. `controller.drawn_window` is the
score evaluation - `core/run_score.py` and the controller, no toolkit in it - so
the PySide6 port removes the 26-45 ms `page.update()` term and leaves this one
standing at 6.2 ms. Inside Flet it was invisible under the diff; on Qt it is
about 99% of the frame's read and roughly eighty times the simulation at 1x.

That inverts what the column budget means. `CHART_COLUMN_BUDGET_PER_SERIES` is
150 because Flet charged per point control; `PL-QXSB` measured Qt drawing 648 000
points in 1.96 ms, which was read as the budget ceasing to matter. It does not -
it stops being a *drawing* constraint and becomes an *evaluation* one, at about
8.7 us per column. Raising the budget fourfold costs 3.5 ms a frame and
sixteenfold costs 20 ms, which is affordable against a 200 ms render budget and
is not against a 60 Hz ambition. `PL-GS3R`'s chord-width rule, which makes the
column count a function of the selected span, is sized directly by this number.

**Not a defect in `PL-2FM6`.** That change bought exactness at control changes
that no selection over recorded samples could give; this is the price of it,
stated rather than discovered later.

**The question this item asks is answered, by reading rather than by measuring
(2026-09-16).** "Worth checking before sizing any fix" above asks whether the
evaluation re-propagates columns whose values cannot have changed. It does.
`RunDefinition.evaluate_anchored` (`src/anesthesia_sim/core/run_definition.py:472`,
the module `PL-ZX12` renamed `run_score.py` to) allocates `states` fresh on
every call and walks every column in the window; nothing survives the call. The
anchoring `PL-2FM6` bought holds the column *times* still so the drawn points do
not all move each frame - it was never a claim that their *values* are reused.

**The cost has two terms, and which one dominates is a function of the budget.**
Inside one segment, consecutive grid columns are carried by a single propagator
over `spacing_s` and one matrix-vector product per column; a bound or an event
column breaks that run and `_state_from_opening` forms another propagator. Per
frame, then: one `matrix_exponential` per segment boundary in view at about
1.29 ms, and one chained product per drawn instant at about 6.2 us. Both figures
are `evaluate_anchored`'s own docstring, measured 2026-09-08 under `PL-2FM6`;
neither is re-measured here, and the split below is arithmetic over them rather
than a fresh profile.

At the 150-column budget this item measured, the fixed term dominates: 102 drawn
instants is about 0.6 ms of products beside about 5 ms of propagators, which is
what the "about 4.9 ms fixed" above is made of and implies two segments in view.
`PL-GS3R` then made the budget `max(150, ceil(plot_width_px) + 1)`, and the
per-instant term overtakes it well inside the range that change opened.

**`PL-PGZF` is this item's cost measured one level up, not a second finding.**
`assemble_chart_frame` reaches it through `_run_frame` ->
`SimulationController.drawn_window` -> `evaluate_anchored`
(`src/anesthesia_sim/app/chart_frame.py:645`, `src/anesthesia_sim/app/controller.py:852`),
so its table - 8.39 ms at 102 drawn instants, 11.80 at 601, 15.42 at 1 069, one
20-minute run with one dial change - is this item's own curve at the widened
budget. Its brief expects the fold: "`PL-R460` and `PL-CNCF` are the neighbours;
triage may well fold this into one of them." The residual over the two terms
above grows from about 2.6 ms to about 3.6 ms across that range, which is
`assemble_chart_frame`'s own per-instant packaging outside `drawn_window` and is
unattributed; a profile, not arithmetic, is what would place it.

**Memoizing is not free here, and the obstacle is a gated guarantee rather than
a preference.** `RunDefinition.state_at` documents that it is "a function of the
run definition and of nothing else - no cache, no memory of what was asked
before", gated by `tests/reference/test_canonical_evaluation.py` and stated in
`docs/MODEL.md` § "The canonical evaluation rule". A cache over a pure function
is observationally transparent and does not by itself break that; what would
break it is a key that cannot see the definition change underneath it, and
`record_change` offers two shapes that do exactly that. A second control moved
before the next step *replaces* the open segment's settings at the same opening
instant, leaving the segment count unchanged and the physics different; a dial
moved and moved back *deletes* the open segment, leaving the count lower. Either
one leaves `(segment index, instant)` - the obvious key - naming a state the run
was never computed under, which is `CLAUDE.md`'s plausible-but-incorrect value
rather than a stale pixel. So any fix owes its invalidation key against those
two shapes before its speed-up is worth measuring.

**`touches` above still names `core/run_score.py`, which `PL-ZX12` renamed.**
Left as it stands deliberately: `PL-RWBV` holds the re-point for eight open
items together, and names the consequence for this one - the real path,
`core/run_definition.py`, is in `protected_paths` and the stale spelling is not.
