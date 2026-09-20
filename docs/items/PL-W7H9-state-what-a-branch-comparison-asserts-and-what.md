---
id: PL-W7H9
title: State what a branch comparison asserts and what it does not, in docs/MODEL.md and docs/ARCHITECTURE.md
priority: P2
effort: S
status: blocked
classes: docs, safety, anticipated
feature: scenario-branching
touches: docs/MODEL.md, docs/ARCHITECTURE.md
blocked-by: PL-8PSW, PL-XJ37
added: 2026-09-06
---

**Problem.** A side-by-side comparison of two branches makes a claim, and
nothing states what the claim is or where it stops.

**Why it matters.** A comparison is the most persuasive thing this simulator
draws: two curves, one difference, an obvious conclusion. That persuasiveness
is exactly why its limits have to be written down. A reader can otherwise take
"low flow woke this patient 12 minutes sooner" as a result about patients
rather than about one parameter set, one reference adult, and a model with no
inter-individual variability at all.

**What has to be stated.**

- What two branches share - patient, agent, parameter set, model version, and
  every control value up to the branch point - and what therefore *can* be
  attributed to the settings that differ.
- That the pre-branch history is identical by construction rather than by
  measurement, and what that does and does not guarantee after the branch
  point.
- That neither branch is a prediction for a patient: the model has one
  reference adult and no inter-individual variability, so a difference between
  branches is a property of the model, not an expected clinical difference.
- Any divergence bound `PL-Z3W6` could not eliminate.

**Where.** `docs/MODEL.md` (a subsection beside the reproducibility guarantee)
and `docs/ARCHITECTURE.md` (what a branch is, structurally).

**Done when.** Both documents carry the statements above, and the interface
does not assert anything about a comparison that they do not support.

## Groomed 2026-09-20 under `PL-JFQ3`: `PL-8PSW` removed one prerequisite; the hazard is not live

**The question this item was groomed to answer.** `PL-JFQ3` (the nine blocked
items whose blockers have closed) singles this one out, because since `PL-ZF2G`
the `anticipated` carve-out in `tools/doc_check.py`'s `check_gate_reentries`
holds only while `anticipated` and `status: blocked` hold *together*. Promoting
this item is therefore the event that returns a `safety`-classed finding to the
debt gate, and the question is whether `PL-8PSW` closing made its hazard live
or merely removed one prerequisite.

**It removed one prerequisite. The hazard is not live.** The hazard here is a
*reader* taking two curves as a claim about patients, and no reader can reach
two curves. Checked against the tree on 2026-09-20:

- `PL-8PSW` (overlay two branches on one time axis) landed the drawing:
  `SimulationView` is documented as "The dashboard over one or two runs on one
  agent", and `docs/MODEL.md:181` records the two-run hover conventions as
  shipped.
- `src/anesthesia_sim/app/main.py` constructs `SimulationView((controller,))` —
  one run — and its own docstring opens "The application entry point: one run,
  one window, two timers".
- Neither `main.py` nor `simulation_view.py` mentions `branch`, `BranchedCase`
  or `ResumePoint` at all. `grep -rnE 'branch|BranchedCase|ResumePoint'` over
  both returns nothing. Nothing in the shipped application opens a fork.

So `PL-8PSW` made a comparison *drawable*, not *reachable*, and a statement
about what a comparison asserts has no reader until a learner can take one.

**The real blocker, now declared.** `PL-XJ37` (nothing in v0.5.0's scope lets a
learner take a fork or select between runs, and `SimulationView`'s run set is
fixed at construction) is `needs-decision` and is the item that makes a
comparison reachable. It is written into `blocked-by` beside `PL-8PSW`, which
is kept because the sequence is the record: this item waited on the overlay,
the overlay landed, and it now waits on the route to it.

**What that costs, recorded rather than claimed away.** The carve-out holds
only while this stays `blocked`, so the moment `PL-XJ37` resolves, this item
becomes a live `safety` finding that `checks.py` pins to `P1` — and the
promotion is a grooming pass, not an automatic consequence. That window is
`PL-ZF2G`'s own accepted cost and is unchanged by this pass; what has changed
is that the edge now names something open, so the advisory that would have
carried it is no longer firing against a closed blocker.

**One thing this pass did *not* find, and it is worth saying.** Neither
document carries the statements this item asks for. `docs/MODEL.md`'s only "not
a prediction for the patient" sentence (line 5639) is about the MAC-awake band,
a different claim; `docs/ARCHITECTURE.md` § "What a branch is" describes the
structure in full and states what a branch *guarantees* without stating what a
comparison of two of them does not. Nothing here is overtaken, so the work is
intact and waiting.
