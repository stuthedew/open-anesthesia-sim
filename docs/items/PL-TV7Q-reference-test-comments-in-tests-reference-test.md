---
id: PL-TV7Q
title: Reference-test comments in tests/reference/test_coupled_dynamics.py and tests/reference/test_canonical_evaluation.py quote measured error margins that no test asserts, such as 'no inversions at all over 1 485 000 pair comparisons' and the 2026-09-07 separation table; best practice adopted on #2201 is to state the bound and keep a measurement only where a test asserts it
status: untriaged
added: 2026-11-22
---

**Problem.** Reference-test comments in tests/reference/test_coupled_dynamics.py and tests/reference/test_canonical_evaluation.py quote measured error margins that no test asserts, such as 'no inversions at all over 1 485 000 pair comparisons' and the 2026-09-07 separation table; best practice adopted on #2201 is to state the bound and keep a measurement only where a test asserts it

**Found 2026-11-22** while applying the owner's answer on #2201 (`PL-7M65`). Wilson et al. 2014 (PLoS Biol 12(1):e1001745, practice 5a) and PEP 8 § "Comments" support stating the bound and its reason in prose, and keeping a measured margin only where a test asserts it. #2201 applied that only to the sentences it touched. Two kinds remain. Some measured figures are only a margin, such as "no inversions at all over 1 485 000 pair comparisons", which `docs/INTERFACE.md` § "Displayed precision" also quotes. Others are the reason for a fitted tolerance, such as the 2026-09-07 table behind `WORST_FRACTION_SEPARATION` and `WORST_ACCUMULATOR_SEPARATION`. A fitted tolerance needs its measurement as its record, so the durable fix for those is a bound derived from the arithmetic, which the owner's rule of 2026-11-14 (`PL-GJ1W`) makes the standard. An edit under `tests/reference/` waits for the owner's read.

**Done when.** Each measured figure in those two files is asserted by a test, is the dated reason for a tolerance that has no derived bound yet, or is gone, and each fitted tolerance has an item for its derived bound.
