---
id: PL-VM4Q
title: docs/INTERFACE.md's paragraphs on comparing two readouts give 1.1e-12 as the largest calculation-error differential between two compartments and 1.0e-7 counts as the reversal bound, where tests/reference/test_coupled_dynamics.py now measures 2.06e-14 and derives 8e-9 counts from EXACT_STEP_ORACLE_TOLERANCE = 4e-13
status: dropped
feature: interface-matches-its-spec
touches: docs/INTERFACE.md
added: 2026-11-21
closed: 2026-11-22
reason: Already done by #2180 (d4e8200c): docs/INTERFACE.md no longer gives 1.1e-12 or 1.0e-7 (it now gives 1.6e-14 and the 8.0e-9 bound the test derives); what its done-when still asked for, quoting no measured differential that no test asserts, is now part of PL-TV7Q
---

**Problem.** docs/INTERFACE.md's paragraphs on comparing two readouts give 1.1e-12 as the largest calculation-error differential between two compartments and 1.0e-7 counts as the reversal bound, where tests/reference/test_coupled_dynamics.py now measures 2.06e-14 and derives 8e-9 counts from EXACT_STEP_ORACLE_TOLERANCE = 4e-13

**Found 2026-11-21** by the blind review of `PL-7M65` (#2201). `docs/INTERFACE.md`, in the paragraphs after "When a reader compares two readouts", says "the simulator's gap between any two compartments differed from the independent solution's by at most $`1.1\times10^{-12}`$ as a fraction" (checked 2026-10-17), and its note for developers says no reversal can occur above "$`1.0\times10^{-7}`$ counts of the last displayed digit". The comment above `MAX_INVERTED_GAP_IN_DISPLAY_COUNTS` in `tests/reference/test_coupled_dynamics.py`, re-measured 2026-11-21 for `PL-PH3N`, gives a largest pairwise differential of 2.06e-14 and a bound of 8e-9 counts, which is 2 × `EXACT_STEP_ORACLE_TOLERANCE` (4e-13) × 100 × 10². The document's figures predate the tighter tolerance. Changing a value in `docs/INTERFACE.md` needs the owner's read.

**Recommendation, 2026-11-22.** State the bound and drop the measured differential. The owner asked for best practice on this question for #2201 ("Whatever best practice is. Look it up", 2026-11-22), and the answer applied there was to keep a measured margin only where a test asserts it. Wilson et al. 2014 (PLoS Biol 12(1):e1001745, practice 5a) call assertions "executable documentation" that a reader "can be sure … are accurate and up to date", PEP 8 says "Comments that contradict the code are worse than no comments", and the owner's rule of 2026-11-14 (`PL-GJ1W`) makes the derived bound the standard, with the measurement kept as a check. The 1.1e-12 figure is the evidence: no test asserts it, and it went stale.

**Done when.** `docs/INTERFACE.md` gives the reversal bound as the test derives it from `EXACT_STEP_ORACLE_TOLERANCE`, and quotes no measured differential that no test asserts.

**Generator check.** Not owed an answer beyond this: the work landed elsewhere before triage, so it is closed rather than worked.
