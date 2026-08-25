---
id: PL-WRKL
title: Record the control-input timeline so a run can be replayed or forked
status: dropped
feature: scenario-branching
added: 2026-08-25
closed: 2026-08-25
reason: aspirational rather than actionable; the record's shape is decided by the scenario format it serves, so it was promoted to ROADMAP.md planned milestone 8 as a prerequisite of items 9 to 12
---

**Problem.** `SimulationController` records concentrations
(`_concentration_history`) but nothing records *why* they moved: the fresh
gas flow, vaporizer dial, ventilation, and cardiac output changes the user
made, and when. A run's inputs are unrecoverable once made.

**Why it matters.** This is the missing prerequisite under both replay and
forking, and it is easy to mistake for solved. A stored state snapshot lets
you *restore* a state; it does not let you reach a point between snapshots,
because that requires re-applying the same inputs over the same interval.
Without the input timeline, "resimulate from the nearest prior snapshot" —
the fallback in every snapshot-interval design — cannot be implemented at
all. It is also what makes a run reproducible and citable: a curve without
its input history is not a result anyone can check.

`ROADMAP.md`'s planned-milestone ordering already has this right: scenario
events (8) before save/load (9), replay (10), comparison (11), and forking
(12). This item is the queue's record of *why* that order is not negotiable.

**Where.** `app/controller.py` (every setter), and a new core-side record;
the timeline is scenario data, so it belongs with the state it describes, not
in the view.

**Done when.** Every control change is recorded with the simulated time it
took effect, and replaying the timeline from t=0 at the same step size
reproduces the run.
