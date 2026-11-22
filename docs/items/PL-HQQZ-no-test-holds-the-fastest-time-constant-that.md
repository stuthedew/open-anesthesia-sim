---
id: PL-HQQZ
title: No test holds the fastest time constant that docs/MODEL.md prints, 5.83 s at an alveolar ventilation of 9.32 L/min
priority: P2
effort: S
status: ready
classes: defect
feature: model-spec-accuracy
touches: docs/MODEL.md, tests/unit/test_governing_equations.py
blocked-by: PL-SZ6G
deferred-from: v0.7.0 - captured after the freeze by the check of docs/MODEL.md against the code; it changes no displayed value, and it is not safety or science
added: 2026-11-21
payoff: the fastest time constant that docs/MODEL.md compares the step with is computed by a test, so a change that moves it fails instead of leaving the old figure in print
---

**Problem.** No test holds the fastest time constant that docs/MODEL.md prints, 5.83 s at an alveolar ventilation of 9.32 L/min

**Why it matters.** § "Supported simulation step" judges the step against this figure. With no test, a change to the alveolar equation or to the supported ranges moves the fastest time constant, and the document keeps the old figure.

**Found by.** `PL-RMNP`, the check of `docs/MODEL.md` against the code, on 2026-11-21. The figures are true: the check reproduced a minimum of 5.83379 s, flat across 9.32, 9.325 and 9.33 L/min.

**The gap.** § "Alveolar gas" prints 5.83 s as the fastest time constant any supported setting gives, at an alveolar ventilation of 9.32 L/min, and § "Supported simulation step" compares the step with it. No file under `src/`, `tests/` or `tools/` holds either figure, and they are not in the section's table, so the table's test does not cover them. The search that found them is recorded only in the closed item `PL-JDX0`.

`PL-SZ6G` (a run's time as a whole number of seconds) rewrites the comparison that uses the 5.83 s: a 1 s step is about a sixth of it. Write the test after that merges. `PL-H94Q` (hold the numeric paragraphs of § "Numerical method" to tests) covers a different section.

**Done when.** A test re-derives the fastest time constant and the ventilation it occurs at from the model's own matrix, and the paragraph names the test.

**Generator check.** Filed by `PL-RMNP` (the check of `docs/MODEL.md` against the code), a sweep that the owner asked for. The fact it misreads is whether a `docs/MODEL.md` sentence about what the model computes matches what it computes, which the head `PL-B6YV` (a document sentence about what the model computes, checked against the code) already states. It is counted under the sweep and is not a new head.
