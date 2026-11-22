---
id: PL-906T
title: tests/reference/test_coupled_dynamics.py still copies dated measurements that docs/VERIFICATION.md § 'Independent-solution test' also records (the oracle-step tables, the peak instants, the retired constants' figures); keep one record and point the other at it
status: done
feature: prose-quality
touches: tests/reference/test_coupled_dynamics.py, docs/VERIFICATION.md
added: 2026-11-22
closed: 2026-11-22
pr: 2243
verify: ! grep -qF '7.7470e-13' tests/reference/test_coupled_dynamics.py
---

**Problem.** tests/reference/test_coupled_dynamics.py still copies dated measurements that docs/VERIFICATION.md § 'Independent-solution test' also records (the oracle-step tables, the peak instants, the retired constants' figures); keep one record and point the other at it

**Found by** the session that closed `PL-TV7Q`, 2026-11-22. That item removed the measured margins of the two rounding limits and pointed the module at `docs/VERIFICATION.md` § "The tests and the figures behind the comparison". It kept the dated measurements that are the reason for a chosen value other than a limit: the oracle-step tables above `ORACLE_STEP_S`, the peak instants above `ENVELOPE_HORIZON_S` and in `_worst_error_over_phases`, the sevoflurane residuals at three step lengths above `SHIPPED_STEP_S`, and the figures of the retired splitting bound. `docs/VERIFICATION.md` records several of the same figures, so the two copies can drift apart.

**Done when.** Each of those figures has one home, and the other place points at it. An edit to an existing line under `tests/reference/` waits for the project owner's read.

**Done 2026-11-22**, on `claude/project-thread-v9awbd`, in the same pull request as `PL-TV7Q`. `docs/VERIFICATION.md` § "The tests and the figures behind the comparison" is now the one home for each measurement, and the test module points there.

1. **Moved into `docs/VERIFICATION.md`** (they were only in the test module): the retired splitting bound's figures, in a new bullet "What the earlier method's limits measured, and why they were retired"; the oracle-step tables, run times and Richardson figures, in a new bullet "Why the independent solution steps at 0.0125 s"; the sevoflurane residuals at three step lengths, in a new bullet "Rounding builds up with the number of steps"; that muscle never has the largest difference on the five runs, under "When the largest difference falls"; and the random runs' 68%, for `PL-S6R5`.
2. **Already in `docs/VERIFICATION.md`, and now only pointed at from the module:** the peak instants, in the comments above `ENVELOPE_HORIZON_S` and `SETTING_CHANGE_SCENARIOS`, the docstrings of `_worst_error_over_phases`, `test_the_shipped_step_reaches_the_pinned_reference_horizons` and `test_exact_step_matches_the_independent_solution_everywhere`; the split's worst error of 2.29e-4, beside both limits.
3. **Kept in the module:** the retired constants' own values (`SPLITTING_ERROR_BOUND_PER_STEP_SECOND = 2.8e-3`, `EXACT_SOLUTION_FLOOR = 1e-12`), which record the deleted code rather than a measurement; the derived figures beside the two limits and `RANDOMISED_FRACTION_ROUNDING`, which follow from arithmetic; and the 8.3e-4 re-pin movement above `PINNED_REFERENCE_STATES`, which `docs/VERIFICATION.md` does not copy.
4. **Corrected on the way:** the comment above `HORIZONS_S` called the 60 s residuals "a few units in the last place". At fractions of 0.01 to 0.05 they are tens to over a hundred units. It now says they are below 1e-15 after 60 steps.

No assertion, limit or expected value changed: the module's AST is identical to `origin/main`'s once every string is blanked.

Files checked: `docs/VERIFICATION.md`, `docs/MODEL.md`, `docs/PARAMETERS.md`, `docs/INTERFACE.md`, `README.md`, `src/` and `tests/`, by `grep -rn "7\.747\|3\.61e8\|7\.7470e-13\|2\.8935e-15\|39\.5 s"`. Each figure printed only in `docs/VERIFICATION.md`.

**Generator check.** An instance of the fact that `PL-GJ1W` (no one place states how far a computed value can be from the exact one) names: a measured rounding figure standing in for, or copied beside, the bound it should be checked against. That head is still open, so this is not a re-entry; it was found by `PL-TV7Q`, which is under the same head.
