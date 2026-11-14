---
id: PL-BDVM
title: The dashboard tests' helper _readout_secondary is defined and never called
status: untriaged
feature: unit-test-review
added: 2026-11-14
---

**Problem.** The dashboard tests' helper _readout_secondary is defined and never called

**What happens.** Found 2026-11-14 while splitting the dashboard tests (`PL-1FPR`). `_readout_secondary` in `tests/integration/simulation_view/simulation_view_support.py` is defined once and called nowhere in `tests/` or `src/`. It was already uncalled in the file before the split, where `git show origin/main:tests/integration/test_simulation_view.py` holds the definition as its only mention. The split moved it unchanged, because that work changed no test code.

**Recommendation.** Find in `git log -S _readout_secondary` which change stopped calling it. Delete it if the check it served was retired on purpose, or restore the check if it was lost by accident.
