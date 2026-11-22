---
id: PL-TV7Q
title: Reference-test comments in tests/reference/test_coupled_dynamics.py and tests/reference/test_canonical_evaluation.py quote measured error margins that no test asserts, such as 'no inversions at all over 1 485 000 pair comparisons' and the 2026-09-07 separation table; best practice adopted on #2201 is to state the bound and keep a measurement only where a test asserts it
priority: P3
effort: M
status: ready
classes: defect
feature: floating-point-domain
touches: tests/reference/test_coupled_dynamics.py, docs/INTERFACE.md
deferred-from: v0.7.0 - present at the freeze, but it continues PL-GJ1W (one statement of how far a computed value can be from the exact one), which this gate defers, and is worked with it; no learner reads a test comment, and the figures in docs/INTERFACE.md agree with the 2026-11-21 measurement
added: 2026-11-22
payoff: A reader of a tolerance or of the readout-order claim is given only figures that a test keeps true.
---

**Problem.** Reference-test comments in tests/reference/test_coupled_dynamics.py and tests/reference/test_canonical_evaluation.py quote measured error margins that no test asserts, such as 'no inversions at all over 1 485 000 pair comparisons' and the 2026-09-07 separation table; best practice adopted on #2201 is to state the bound and keep a measurement only where a test asserts it

**Found 2026-11-22** while applying the owner's answer on #2201 (`PL-7M65`). Wilson et al. 2014 (PLoS Biol 12(1):e1001745, practice 5a) and PEP 8 § "Comments" support stating the bound and its reason in prose, and keeping a measured margin only where a test asserts it. #2201 applied that only to the sentences it touched. Two kinds remain. Some measured figures are only a margin, such as "no inversions at all over 1 485 000 pair comparisons", which `docs/INTERFACE.md` § "Displayed precision" also quotes. Others are the reason for a fitted tolerance, such as the 2026-09-07 table behind `WORST_FRACTION_SEPARATION` and `WORST_ACCUMULATOR_SEPARATION`. A fitted tolerance needs its measurement as its record, so the durable fix for those is a bound derived from the arithmetic, which the owner's rule of 2026-11-14 (`PL-GJ1W`) makes the standard. An edit under `tests/reference/` waits for the owner's read.

**Checked 2026-11-22**, at `d4e8200c`. Half of the title no longer holds. `#2180` deleted `tests/reference/test_canonical_evaluation.py`, and with it `WORST_FRACTION_SEPARATION`, `WORST_ACCUMULATOR_SEPARATION` and their 2026-09-07 table (`git show --stat d4e8200c` lists the file as 592 lines removed). The other half still holds. `grep -n "2026-09-07\|148 500" tests/reference/test_coupled_dynamics.py` prints the comments above `EXACT_STEP_ORACLE_TOLERANCE` and `HELD_RUN_ROUNDING_BOUND`, which still give 2026-09-07 tables measured at the 0.1 s step beside a table measured at the one-second step on 2026-11-21, and the comment above `MAX_INVERTED_GAP_IN_DISPLAY_COUNTS`. The count is now "no inversions at all over 148 500 pair comparisons", in the comment and in the docstring of the test that compares the pairs, and that test asserts the gap bound, not the count. `docs/INTERFACE.md` § "Comparing two readouts" quotes the same unasserted figures: "148 500 pairs of readings", "never disagreed", a largest differential of $`1.6\times10^{-14}`$ and a smallest gap of $`2.7\times10^{-11}`$. `#2180` brought the reversal bound there into line with the test, at $`8.0\times10^{-9}`$ counts, so `PL-VM4Q`'s stale figures are gone, and what is left of it is this item's.
<!-- absent: tests/reference/test_canonical_evaluation.py -->

**Why it matters.** A measured margin that no test asserts goes stale without any check failing. `PL-VM4Q` was that case: `docs/INTERFACE.md` still gave a differential of 1.1e-12, checked on 2026-10-17, after the test's own comment had moved to 2.06e-14. A reader who trusts a stale figure judges a tolerance by the wrong margin. A contributor judging how safe a reversal of two readouts is relies on `docs/INTERFACE.md`'s figures.

**Done when.** Each measured figure in `tests/reference/test_coupled_dynamics.py` and in `docs/INTERFACE.md` § "Comparing two readouts" is asserted by a test, is the dated reason for a tolerance that has no derived bound yet, or is gone. A table kept only as the record of a step length that no longer ships is gone. Each fitted tolerance that keeps its measurement has an item for its derived bound, as `PL-GFQD` is for `EXACT_STEP_ORACLE_TOLERANCE` and `HELD_RUN_ROUNDING_BOUND`.

**Generator check.** An instance of the fact that `PL-GJ1W` (no one place states how far a computed value can be from the exact one) names: how far a computed value can be from the exact one, and so what a comparison on it proves. A comment that quotes a measured margin stands in for the derived bound that head asks for. That head is still open, so this is not a re-entry.
