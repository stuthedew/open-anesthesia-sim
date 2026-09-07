---
id: PL-P1Z3
title: State the canonical evaluation rule that carries determinism once the step is no longer fixed, and gate it
priority: P1
effort: M
status: done
classes: safety, science
feature: numerical-domain
touches: docs/MODEL.md, src/anesthesia_sim/core, tests/reference, docs/ARCHITECTURE.md
added: 2026-09-05
closed: 2026-09-07
pr: 435
verify: uv run pytest -q tests/reference && grep -q 'canonical evaluation' docs/MODEL.md
---

**Problem.** Determinism is currently carried by the fixed 0.1 s step:
every caller takes the same width, so every caller gets the same answer.
`PL-T691` removes that, because a propagator that accepts an interval can be
asked for the same instant by two different routes. Those routes do not agree
bit for bit. Measured 2026-09-05: one 3600 s jump against 36 000 chained 0.1 s
applications of the same propagator differ by **1.6e-14** worst case across the
six states — floating-point composition order, not method error, but a
difference all the same.

`CLAUDE.md` requires deterministic behavior for identical inputs, and
`ROADMAP.md` item 12 requires a fork to reproduce its parent element-wise
rather than within a tolerance. Neither survives "whatever path the caller
took".

**The rule.** State it in `docs/MODEL.md` as a guarantee, in these terms:

- **Canonical.** A keyframe is computed by exactly one matrix exponential per
  inter-event interval, composed in recording order from `t = 0`. Two
  evaluations of the same score at the same event boundary are bit-identical
  because they perform the identical sequence of operations. This is what a
  fork, a replay, a saved run and an export all read.
- **Display-only.** A chart column may be reached by chaining a reused
  propagator from its segment's keyframe. Drift measured at 6e-17 over 600
  columns, fourteen orders below the two-decimal readout. This path may never
  produce a keyframe, an exported value, or a fork's starting state.

The separation is the point: the cheap path is allowed precisely because it
cannot contaminate the canonical one.

**Why it matters.** This is the guarantee that makes a run citable. A curve
whose value depends on how the caller happened to walk to it is not a result
anyone can check, and `docs/MODEL.md` § "The reproducibility guarantee" already
states the property in its current form — it has to be restated in the new one
rather than quietly inherited.

**Done when.** `docs/MODEL.md` states the canonical rule and names the two
paths and what each may be used for; the code enforces the separation rather
than documenting it (the display path cannot return a value the canonical path
would store); and `tests/reference/` holds a test asserting element-wise
equality between a run evaluated straight through and the same run evaluated
via arbitrary intermediate queries. `PL-ZHTT` corrects the paragraph this
replaces.
