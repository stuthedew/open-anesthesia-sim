---
id: PL-8GLL
title: WORKING_NOTES' 88 B per-sample memory figure describes a per-step history PL-D9WD replaced, and PL-011's retention arithmetic rests on it
status: untriaged
added: 2026-09-05
---

**Problem.** WORKING_NOTES' 88 B per-sample memory figure describes a per-step history PL-D9WD replaced, and PL-011's retention arithmetic rests on it

**Why it matters.**

**Where.**

**Done when.**

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
