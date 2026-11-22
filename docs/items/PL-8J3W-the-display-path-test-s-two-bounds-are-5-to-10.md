---
id: PL-8J3W
title: The display-path test's two bounds are 5 to 10 times looser than the figures docs/INTERFACE.md prints: tighten them to the printed figures, or reword the sentence in docs/MODEL.md that says the test keeps those figures true
priority: P2
effort: S
status: dropped
classes: defect
feature: model-spec-accuracy
touches: tests/reference/test_canonical_evaluation.py, docs/MODEL.md
blocked-by: PL-SZ6G
deferred-from: v0.7.0 - captured after the freeze by the check of docs/MODEL.md against the code; it changes no displayed value, and it is not safety or science
added: 2026-11-21
closed: 2026-11-21
reason: PL-Z6C8 removed the display path and its test
payoff: the test that docs/MODEL.md says keeps the printed display-path figures true fails when a change moves one past the figure in print
---

**Problem.** The display-path test's two bounds are 5 to 10 times looser than the figures docs/INTERFACE.md prints: tighten them to the printed figures, or reword the sentence in docs/MODEL.md that says the test keeps those figures true

**Why it matters.** `docs/MODEL.md` tells a reader that a test keeps the printed display-path figures true. The test's bounds are looser than those figures, so a change that moves a figure past what `docs/INTERFACE.md` prints passes.

**Found by.** `PL-RMNP`, the check of `docs/MODEL.md` against the code, on 2026-11-21. It was the second part of `PL-076B` (two tests that check less than `docs/MODEL.md` says), and was split out on 2026-11-21 so that the first part could close.

**The gap.** § "Canonical evaluation test": "A test checks it against a bound for each quantity, so a change to how values are computed cannot silently move a figure that `docs/INTERFACE.md` prints." `docs/INTERFACE.md` § "The canonical evaluation rule" prints "less than a ten-millionth" of 0.1 L for the running totals, which is 1e-8 L, and "about a hundred-millionth of its 0.01% step" for a fraction, which is 1e-12. `tests/reference/test_canonical_evaluation.py` asserts `WORST_ACCUMULATOR_SEPARATION = 5e-8` and `WORST_FRACTION_SEPARATION = 1e-11`. The measured differences are 3.1e-9 L and 8.0e-13, so the printed figures are true today. A change could move the totals' difference to 4e-8 L, past the printed figure, and the test would pass. Either tighten the two bounds to the printed figures, or word the sentence as "cannot move the difference by more than an order of magnitude unnoticed". `PL-SZ6G` (a run's time as a whole number of seconds) will change the measured differences, so choose after it merges.

**Why it waits on `PL-SZ6G`.** That branch changes the step, so it changes the two measured differences, and it rewrites the test module. Choose between the two fixes once it has merged and the differences are measured again. Tightening an existing bound in a test under `tests/reference/` waits for the project owner's read.

**Done when.** The two bounds and the sentence about them agree.

**Generator check.** Split from an item that `PL-RMNP` (the check of `docs/MODEL.md` against the code) filed, a sweep that the owner asked for. The fact it misreads is whether a `docs/MODEL.md` sentence about what the model computes matches what it computes, which the head `PL-B6YV` (a document sentence about what the model computes, checked against the code) already states. It is counted under the sweep and is not a new head.

**Checked 2026-11-21: nothing left to do.** `PL-Z6C8` removed the display path and its test file, `tests/reference/test_canonical_evaluation.py`, so the two bounds this item would have tightened no longer exist. The chart draws the states a run stored.
<!-- absent: tests/reference/test_canonical_evaluation.py -->
