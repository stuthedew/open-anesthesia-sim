---
id: PL-J2TD
title: Apply a recorded control timeline to a run, so a point between samples is reached by resimulation rather than restored
priority: P2
effort: M
status: blocked
blocked-by: PL-T691
classes: feature, refactor
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/core, tests/unit, tests/integration
added: 2026-09-06
---

**Problem.** The controller records a control-input timeline (`ControlChange`
entries, v0.4.0) but nothing can *apply* one. A run advances only by the
settings a user changes as it goes, so a recorded timeline is a read-only
record rather than something a second run can be driven by.

**Why it matters.** This is planned-milestone item 8's replay half, and it is
the mechanism every branch operation in v0.5.0 rests on. A stored state lets a
run be *restored*; it does not let a point *between* stored states be reached,
because that needs the same inputs re-applied over the same interval. Without
it, "resimulate from the nearest prior point" - the fallback in every branching
design - cannot be implemented at all, and a branch could only ever be taken at
a point the store happens to hold.

**Scope.** Internal only. A user-facing replay control is planned item 10 and
stays behind item 9's save/load, which v0.5.0 puts out of scope (project owner,
2026-09-06). What this item delivers is a driver: given a timeline and a step
count, produce the state the run had, using the same code path a live run uses,
so the two cannot diverge by construction.

**Where.** `src/anesthesia_sim/app/controller.py` (the timeline and the advance
path), `src/anesthesia_sim/core` for whatever the driver needs exposed.

**Done when.** A recorded timeline can be applied to a fresh run and reproduces
the original run's state at every sampled point, asserted by test; and the
driver shares the advance path with a live run rather than reimplementing it.
