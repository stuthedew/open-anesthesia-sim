---
id: PL-MYK0
title: Docstrings and comments in three tests under tests/reference/ repeat five statements that docs/MODEL.md corrected on 2026-11-21
priority: P2
effort: S
status: done
classes: defect
feature: model-spec-accuracy
milestone: v0.6.21
touches: tests/reference/test_late_washout_against_published_fits.py, tests/reference/test_published_wash_in_and_elimination.py
blocked-by: PL-SZ6G
deferred-from: v0.7.0 - captured after the freeze by the check of docs/MODEL.md against the code; it changes no displayed value, and it is not safety or science
added: 2026-11-21
closed: 2026-11-22
pr: 2243
payoff: the docstrings of three published-data tests give the figures and reasons that the code and docs/MODEL.md give
verify: ! grep -qF 'tracks reading the value out of the methods text' tests/reference/test_published_wash_in_and_elimination.py
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

**Checked 2026-11-22** against `d4e8200`: partly done. The blocker `PL-SZ6G` closed with #2180. Point 3 is fixed: the docstring of `test_early_wash_in_matches_published_human_measurement` now reads "0.032 to 0.042". Point 5 went with the deleted file. Points 1, 2 and 4 are left. `tests/reference/test_late_washout_against_published_fits.py` still gives "0.912-0.937" in its module docstring and "0.912 to 0.937" in the docstring and failure message of `test_the_published_coefficients_sum_below_one_at_discontinuation`, and its module docstring still says "Between 8 and 13 hours it is a third to a half". `tests/reference/test_published_wash_in_and_elimination.py` still has both comments of point 4. The tail ratios of point 2 are model output, so measure them again on the whole-second tree before writing them.

**Done 2026-11-22**, on `claude/project-thread-v9awbd`. Each figure that `docs/VERIFICATION.md` already holds is now a pointer to it, not a fresher copy.

1. Point 1: the module docstring of `tests/reference/test_late_washout_against_published_fits.py` now says the amplitudes sum to less than 1 and points at `docs/VERIFICATION.md` § "The first 24 hours of elimination against the published mean curves" for each sum. The docstring of `test_the_published_coefficients_sum_below_one_at_discontinuation` says the same and names the 0.91 to 0.94 its assertion holds. Its failure message names that range and the section, in place of "0.912 to 0.937". The sums, recomputed from `PUBLISHED_FITS` on 2026-11-22: 0.93645, 0.91158, 0.92566 and 0.92735, so the section's "0.912 to 0.936" is right. The assertion is unchanged.
2. Point 2: the module docstring now says the open-circuit tail falls as low as a third to a half of the fitted value in every cohort after the first hour, and points at the same section for each cohort's lowest point. Re-measured on 2026-11-22 with the module's `_washout_curve(agent, "open circuit")` against each fit's `ratio_at`: lowest after the first hour 0.425 at 12.7 h (sevoflurane), 0.422 at 13.2 h (isoflurane, first study), 0.336 at 7.95 h (desflurane), 0.457 at 13.4 h (isoflurane, second study); over hours 8 to 13 the ratio runs from 0.336 to 0.655; sevoflurane's lowest in the first hour is 0.36 at minute 19. That matches the section as #2237 left it.
3. Point 4: in `tests/reference/test_published_wash_in_and_elimination.py`, the comment above `ApparatusDeadSpaceCase` now says neither paper reports the ventilation, pointing at `docs/VERIFICATION.md` § "Desflurane's residual, and why the parameter file was not changed". The docstring of `test_the_apparatus_dead_space_moves_every_cohort_together` made the same claim ("`PL-ZDWL` tracks reading the value out of the methods text") and is corrected the same way. The comment above `DETECTED_CHANGES` now says x1.10 is not used because it is too close to desflurane's edge at x1.097.
4. Points 3 and 5 were already settled, as the checks above record.

No assertion, tolerance or expected value changed in either file: each module's AST is identical to `origin/main`'s once every string is blanked.

Files checked: `docs/VERIFICATION.md`, `docs/MODEL.md`, `docs/PARAMETERS.md`, `docs/INTERFACE.md` and `README.md`, by `grep -rn "0\.937\|not held here\|tracks reading the value\|passes it: desflurane"`. None printed the old statements. `docs/PARAMETERS.md` printed one unrelated "is not held here", about a different source.
