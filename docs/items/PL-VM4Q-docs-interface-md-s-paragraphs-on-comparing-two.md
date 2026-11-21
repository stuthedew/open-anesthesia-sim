---
id: PL-VM4Q
title: docs/INTERFACE.md's paragraphs on comparing two readouts give 1.1e-12 as the largest calculation-error differential between two compartments and 1.0e-7 counts as the reversal bound, where tests/reference/test_coupled_dynamics.py now measures 2.06e-14 and derives 8e-9 counts from EXACT_STEP_ORACLE_TOLERANCE = 4e-13
status: untriaged
feature: interface-matches-its-spec
touches: docs/INTERFACE.md
added: 2026-11-21
---

**Problem.** docs/INTERFACE.md's paragraphs on comparing two readouts give 1.1e-12 as the largest calculation-error differential between two compartments and 1.0e-7 counts as the reversal bound, where tests/reference/test_coupled_dynamics.py now measures 2.06e-14 and derives 8e-9 counts from EXACT_STEP_ORACLE_TOLERANCE = 4e-13

**Found 2026-11-21** by the blind review of `PL-7M65` (#2201). `docs/INTERFACE.md`, in the paragraphs after "When a reader compares two readouts", says "the simulator's gap between any two compartments differed from the independent solution's by at most $`1.1\times10^{-12}`$ as a fraction" (checked 2026-10-17), and its note for developers says no reversal can occur above "$`1.0\times10^{-7}`$ counts of the last displayed digit". The comment above `MAX_INVERTED_GAP_IN_DISPLAY_COUNTS` in `tests/reference/test_coupled_dynamics.py`, re-measured 2026-11-21 for `PL-PH3N`, gives a largest pairwise differential of 2.06e-14 and a bound of 8e-9 counts, which is 2 × `EXACT_STEP_ORACLE_TOLERANCE` (4e-13) × 100 × 10². The document's figures predate the tighter tolerance. Changing a value in `docs/INTERFACE.md` needs the owner's read.

**Done when.** The two figures in `docs/INTERFACE.md` match the test's measurement and bound, with the date of the measurement.
