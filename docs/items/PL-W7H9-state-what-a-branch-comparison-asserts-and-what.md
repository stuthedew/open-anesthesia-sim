---
id: PL-W7H9
title: State what a branch comparison asserts and what it does not, in docs/MODEL.md and docs/ARCHITECTURE.md
priority: P2
effort: S
status: blocked
blocked-by: PL-8PSW
classes: docs, safety, anticipated
feature: scenario-branching
touches: docs/MODEL.md, docs/ARCHITECTURE.md
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
