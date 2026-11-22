---
id: PL-MYK0
title: Docstrings and comments in three tests under tests/reference/ repeat five statements that docs/MODEL.md corrected on 2026-11-21
priority: P2
effort: S
status: ready
classes: defect
feature: model-spec-accuracy
touches: tests/reference/test_late_washout_against_published_fits.py, tests/reference/test_published_wash_in_and_elimination.py
blocked-by: PL-SZ6G
deferred-from: v0.7.0 - captured after the freeze by the check of docs/MODEL.md against the code; it changes no displayed value, and it is not safety or science
added: 2026-11-21
payoff: the docstrings of three published-data tests give the figures and reasons that the code and docs/MODEL.md give
---

**Problem.** Docstrings and comments in three tests under tests/reference/ repeat five statements that docs/MODEL.md corrected on 2026-11-21

**Why it matters.** A developer reads a test's docstring to learn what the test shows about the model. Each of these gives a figure or a reason that the code beside it, or `docs/MODEL.md`, contradicts.

**Found by.** `PL-RMNP`, the check of `docs/MODEL.md` against the code, on 2026-11-21. `PL-RMNP` corrected each statement in `docs/MODEL.md`. These were entries 1 to 5 of `PL-VF3H` (the same statements in docstrings and comments), and were split out on 2026-11-21 so that its other four entries could close.

1. `tests/reference/test_late_washout_against_published_fits.py`, module docstring: the amplitudes sum to "0.912-0.937". The largest sum is 0.93645, sevoflurane's, so the range is 0.912 to 0.936. The docstring and the failure message of `test_the_published_coefficients_sum_below_one_at_discontinuation` repeat 0.937.
2. The same module docstring: "Between 8 and 13 hours" the open-circuit tail is a third to a half of the mean curve. That range, 0.34 to 0.46, is each cohort's lowest point after the first hour. Over hours 8 to 13 the ratio runs from 0.34 to 0.66. The lowest point comes near hour 8 for desflurane and near hour 13 for the others. Sevoflurane's tail is lower only in the first half hour, at 0.36 near minute 19.
3. `tests/reference/test_published_wash_in_and_elimination.py`, docstring of `test_early_wash_in_matches_published_human_measurement`: desflurane runs "0.034 to 0.042" above its published curve from 1 to 10 minutes. The 7.5-minute point is 0.032 above, so the range is 0.032 to 0.042.
4. The same file, two comments. "The numeric value is in the methods text and is not held here (`PL-ZDWL`)": `docs/MODEL.md` says that neither paper reports a ventilation, and the closed item `PL-ZDWL` found the same. "x1.10 is not used, because desflurane passes it": desflurane fails the gate at ×1.10, and `docs/MODEL.md` gives the right reason, that ×1.10 is too close to desflurane's edge at ×1.097.
5. `tests/reference/test_canonical_evaluation.py`, module docstring: the accumulators show "to six decimals of a litre", and the two bounds differ because "their headroom differs by four orders". `app/formatting.py` shows the three amounts to 0.1 L (`_RUN_TOTAL_LITRE_DECIMALS = 1`). What differs by about four orders is the measured difference, 8.0e-13 of an atmosphere against 3.1e-9 L.
<!-- absent: tests/reference/test_canonical_evaluation.py -->

[superseded 2026-11-21] **Why it waits on `PL-SZ6G`** (a run's time as a whole number of seconds). That branch rewrites all three files, so a correction made now would conflict with it. A change to an existing line of a test under `tests/reference/` also waits for the project owner's read.

**Done when.** Each of the five agrees with the code beside it and with `docs/MODEL.md`.

**Generator check.** Split from an item that `PL-RMNP` (the check of `docs/MODEL.md` against the code) filed, a sweep that the owner asked for. The fact it misreads is whether a `docs/MODEL.md` sentence about what the model computes matches what it computes, which the head `PL-B6YV` (a document sentence about what the model computes, checked against the code) already states. It is counted under the sweep and is not a new head.

**Checked 2026-11-21:** point 5 no longer applies. `PL-Z6C8` deleted `tests/reference/test_canonical_evaluation.py`, so only the other files remain.
<!-- absent: tests/reference/test_canonical_evaluation.py -->
