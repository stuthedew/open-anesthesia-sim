---
id: PL-8GLL
title: WORKING_NOTES' 88 B per-sample memory figure describes a per-step history PL-D9WD replaced, and PL-011's retention arithmetic rests on it
priority: P2
effort: S
status: done
classes: defect, docs
milestone: v0.4.0
touches: docs/WORKING_NOTES.md
added: 2026-09-05
closed: 2026-09-05
pr: 344
verify: python3 tools/doc_check.py check && grep -qF '127.9 B per sample' docs/WORKING_NOTES.md
---

**Problem.** `docs/WORKING_NOTES.md`'s 2026-08-25 snapshot-versus-resimulation
measurement says "the per-step history is the expensive thing. 36 000 samples
per simulated hour, ~88-256 B each", sized against "one
`SimulationHistorySample` (88 B as an object)". A run has not been stored as
`SimulationHistorySample` objects since `PL-D9WD`: `RunHistory` keeps an
`array("d")` of times and one `M4AggregateCache` per series, and a sample is a
*row rebuilt on request* rather than a thing retained. `PL-W3DD` then made that
row a mapping of mappings, which is larger again as an object and still not
what is stored.

**Why it matters.** `PL-011` (bound the controller's concentration history) is
open and its retention arithmetic - single-digit MB per simulated hour, 2.3-6.6
GB at the 30-day cap the owner is considering - is read off this figure. If the
stored form's per-sample cost has changed, the number that decides whether a
ceiling is needed at all has changed with it. A wrong figure here is not
misleading about the model, but it is load-bearing for a decision.

**Where.** `docs/WORKING_NOTES.md` (the 2026-08-25 measurement, third bullet);
`app/controller.py` (`RunHistory.__init__`, what is actually retained);
`app/chart_downsampling.py` (`M4AggregateCache`, which holds the values and the
aggregate ladder over them). `PL-011` is what consumes the answer.

**First step.** Measure the retained bytes per sample as the run is now stored -
the elapsed array plus every series' cache, including the dyadic aggregate
ladder, which the old figure did not exist to cover - and record the new figure
beside the old one rather than over it: the note is a dated record of a
decision, and what changed it is part of the record.

**Found.** Sweeping the docs while closing `PL-W3DD`, 2026-09-05. The staleness
predates that item - `PL-D9WD` introduced it - which is why it is filed rather
than fixed there.

**Done 2026-09-05, while answering `PL-011` (bound the controller's
concentration history), whose arithmetic this figure fed.** Measured by
`tracemalloc` over a recorded `RunHistory`, marginal between 100 000 and
200 000 samples so the fixed overhead is out of it. **127.9 B per sample**, one
substance, seven series - confirming `PL-D9WD`'s 127 B and retiring the 88 B
this item was filed against.

Two things the measurement found that the item did not ask for, both recorded
in the note beside the figure they correct:

- **Half the cost is the aggregate ladder, not the samples.** 64.0 B is the
  elapsed array plus seven `array("d")` of values; 63.9 B is the M4 aggregates
  over them. `PL-011` was framed on the assumption that the raw record was the
  whole cost, so evicting it would bound memory; it removes half and leaves the
  growth linear. That is the half that changed `PL-011`'s answer.
- **The note's second figure was stale too.** It gives `SimulationState.advance`
  at 8.9 us per 0.1 s step; re-measured at **18.4 us** (200 000 steps in 3.67 s),
  so resimulating a day costs 15.9 s rather than 8 s. The bullet's conclusion -
  that resimulation is nearly free for the interactive case - survives at 2.0 s
  for a 3-hour run.

Recorded beside the 2026-08-25 measurements rather than over them, as the
**First step** asked: the note is a dated record of what that reasoning was
done from, and what moved the numbers is part of the record.
