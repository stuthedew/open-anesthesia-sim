---
id: PL-BDVM
title: The dashboard tests' helper _readout_secondary is defined and never called
priority: P3
effort: S
status: ready
classes: test
feature: unit-test-review
touches: tests/integration/simulation_view/simulation_view_support.py
added: 2026-11-14
payoff: either a lost check of the readouts second line is restored, or the dashboard tests lose a helper that each reader must first prove unused
---

**Problem.** The dashboard tests' helper _readout_secondary is defined and never called

**What happens.** Found 2026-11-14 while splitting the dashboard tests (`PL-1FPR`). `_readout_secondary` in `tests/integration/simulation_view/simulation_view_support.py` is defined once and called nowhere in `tests/` or `src/`. It was already uncalled in the file before the split, where `git show origin/main:tests/integration/test_simulation_view.py` holds the definition as its only mention. The split moved it unchanged, because that work changed no test code.

**Recommendation.** Find in `git log -S _readout_secondary` which change stopped calling it. Delete it if the check it served was retired on purpose, or restore the check if it was lost by accident.

**Checked 2026-11-22.** `_readout_secondary` is still defined in `tests/integration/simulation_view/simulation_view_support.py` and still called nowhere in `tests/` or `src/`. It was already uncalled at the freeze (`git show 0947408:tests/integration/test_simulation_view.py`). This checkout is a shallow clone, so `git log -S _readout_secondary` reaches back only to 2026-10-19 and cannot show which change stopped calling it. Each readout's second line is still read directly elsewhere: 25 lines in seven test files read `secondary_label`.

**Why it matters.** A helper that nobody calls can mark a check that was lost when a test was rewritten. If a test once read each readout's second line through it, that check may be gone. If not, it is dead code that each later reader must first prove unused.

**Done when.** Either the helper is gone, and this item names the change that stopped calling it and the tests that now cover what it read, or a restored test calls it for a check that was lost.

**Generator check.** The fact misread is whether a test helper still has a caller. No head states it, and the linter does not report an unused module-level function. This is a one-off.
