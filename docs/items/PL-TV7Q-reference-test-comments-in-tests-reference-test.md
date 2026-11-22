---
id: PL-TV7Q
title: Reference-test comments in tests/reference/test_coupled_dynamics.py and tests/reference/test_canonical_evaluation.py quote measured error margins that no test asserts, such as 'no inversions at all over 1 485 000 pair comparisons' and the 2026-09-07 separation table; best practice adopted on #2201 is to state the bound and keep a measurement only where a test asserts it
priority: P3
effort: M
status: done
classes: defect
feature: floating-point-domain
touches: tests/reference/test_coupled_dynamics.py, docs/INTERFACE.md
deferred-from: v0.7.0 - present at the freeze, but it continues PL-GJ1W (one statement of how far a computed value can be from the exact one), which this gate defers, and is worked with it; no learner reads a test comment, and the figures in docs/INTERFACE.md agree with the 2026-11-21 measurement
added: 2026-11-22
closed: 2026-11-22
pr: 2243
payoff: A reader of a tolerance or of the readout-order claim is given only figures that a test keeps true.
verify: grep -qF "No test bounds the calculation error in a learner" docs/INTERFACE.md
---

**Problem.** Reference-test comments in tests/reference/test_coupled_dynamics.py and tests/reference/test_canonical_evaluation.py quote measured error margins that no test asserts, such as 'no inversions at all over 1 485 000 pair comparisons' and the 2026-09-07 separation table; best practice adopted on #2201 is to state the bound and keep a measurement only where a test asserts it

**Found 2026-11-22** while applying the owner's answer on #2201 (`PL-7M65`). Wilson et al. 2014 (PLoS Biol 12(1):e1001745, practice 5a) and PEP 8 § "Comments" support stating the bound and its reason in prose, and keeping a measured margin only where a test asserts it. #2201 applied that only to the sentences it touched. Two kinds remain. Some measured figures are only a margin, such as "no inversions at all over 1 485 000 pair comparisons", which `docs/INTERFACE.md` § "Displayed precision" also quotes. Others are the reason for a fitted tolerance, such as the 2026-09-07 table behind `WORST_FRACTION_SEPARATION` and `WORST_ACCUMULATOR_SEPARATION`. A fitted tolerance needs its measurement as its record, so the durable fix for those is a bound derived from the arithmetic, which the owner's rule of 2026-11-14 (`PL-GJ1W`) makes the standard. An edit under `tests/reference/` waits for the owner's read.

**Checked 2026-11-22**, at `d4e8200c`. Half of the title no longer holds. `#2180` deleted `tests/reference/test_canonical_evaluation.py`, and with it `WORST_FRACTION_SEPARATION`, `WORST_ACCUMULATOR_SEPARATION` and their 2026-09-07 table (`git show --stat d4e8200c` lists the file as 592 lines removed). The other half still holds. `grep -n "2026-09-07\|148 500" tests/reference/test_coupled_dynamics.py` prints the comments above `EXACT_STEP_ORACLE_TOLERANCE` and `HELD_RUN_ROUNDING_BOUND`, which still give 2026-09-07 tables measured at the 0.1 s step beside a table measured at the one-second step on 2026-11-21, and the comment above `MAX_INVERTED_GAP_IN_DISPLAY_COUNTS`. The count is now "no inversions at all over 148 500 pair comparisons", in the comment and in the docstring of the test that compares the pairs, and that test asserts the gap bound, not the count. `docs/INTERFACE.md` § "Comparing two readouts" quotes the same unasserted figures: "148 500 pairs of readings", "never disagreed", a largest differential of $`1.6\times10^{-14}`$ and a smallest gap of $`2.7\times10^{-11}`$. `#2180` brought the reversal bound there into line with the test, at $`8.0\times10^{-9}`$ counts, so `PL-VM4Q`'s stale figures are gone, and what is left of it is this item's.
<!-- absent: tests/reference/test_canonical_evaluation.py -->

**Why it matters.** A measured margin that no test asserts goes stale without any check failing. `PL-VM4Q` was that case: `docs/INTERFACE.md` still gave a differential of 1.1e-12, checked on 2026-10-17, after the test's own comment had moved to 2.06e-14. A reader who trusts a stale figure judges a tolerance by the wrong margin. A contributor judging how safe a reversal of two readouts is relies on `docs/INTERFACE.md`'s figures.

**Done when.** Each measured figure in `tests/reference/test_coupled_dynamics.py` and in `docs/INTERFACE.md` § "Comparing two readouts" is asserted by a test, is the dated reason for a tolerance that has no derived bound yet, or is gone. A table kept only as the record of a step length that no longer ships is gone. Each fitted tolerance that keeps its measurement has an item for its derived bound, as `PL-GFQD` is for `EXACT_STEP_ORACLE_TOLERANCE` and `HELD_RUN_ROUNDING_BOUND`.

**Review fix 2026-11-22**, after two blind review passes on #2243. § "Comparing two readouts" had said the 4e-13 limit applied everywhere and that a reversal could happen only at a crossing. It now gives three limits: 4e-13 for the five scripted runs of 600 s to 900 s and the nine random runs of 600 s, 1e-12 for the reference point held for an hour, and the derived `run_rounding(3, StepCount(86400))` = 1.53e-9 of the run's largest fraction for a 24 h session, which no test bounds. All three are more than five orders of magnitude below 0.01 percentage points. A reversal is possible wherever two compartments are almost equal: at a crossing, or where two converge, such as the circuit and the alveoli at zero cardiac output. The developer note and the section's opening sentence now say the same. The test's name `test_displayed_ordering_reverses_only_at_a_crossing` still says "crossing", and was left, because renaming a test is a code change this pull request does not make.

**Generator check.** An instance of the fact that `PL-GJ1W` (no one place states how far a computed value can be from the exact one) names: how far a computed value can be from the exact one, and so what a comparison on it proves. A comment that quotes a measured margin stands in for the derived bound that head asks for. That head is still open, so this is not a re-entry.

**Done 2026-11-22**, on `claude/project-thread-v9awbd`, together with `PL-GFQD` (the two rounding limits' reasons).

1. **Gone from `tests/reference/test_coupled_dynamics.py`:** both residual tables at the 0.1 s step (2026-09-07) and both at the one-second step (2026-11-21) beside `EXACT_STEP_ORACLE_TOLERANCE` and `HELD_RUN_ROUNDING_BOUND`; the 0.1 s and 0.025 s residual figures and the degradation figures in the same comments; the five per-trajectory figures in the docstring of `_envelope_corner` and three of them in `_unperfused_load_then_dial_off`; the three-ventilator-starts figures above `SETTING_CHANGE_SCENARIOS`; the 60 s residual range above `HORIZONS_S`; the inversion count "148 500 pair comparisons" above `MAX_INVERTED_GAP_IN_DISPLAY_COUNTS` and in the docstring of `test_displayed_ordering_reverses_only_at_a_crossing`; the randomised runs' worst figures in the docstring of `test_exact_step_matches_the_independent_solution_on_randomised_trajectories`; and the 68% figure above `RANDOMISED_FRACTION_ROUNDING`. Each place that relied on a figure now points at `docs/VERIFICATION.md` § "The tests and the figures behind the comparison", which holds the measurements.
2. **Kept, as the dated reason for a tolerance with no derived bound:** the subdivision spread behind both limits, in words, with its figures in `docs/VERIFICATION.md`. `PL-GFQD` records why neither limit can be the derived bound.
3. **Gone from `docs/INTERFACE.md` § "Comparing two readouts":** "148 500 pairs of readings", "never disagreed", the differential of 1.6e-14 and the smallest gap of 2.7e-11. The section now derives the claim: a reversal needs a true gap below twice the independent-solution test's limit, 8e-13 as a fraction, which occurs only at a crossing. The note for developers no longer says the third test "records the result".
4. **Left, and filed:** the dated measurements that are the reason for a chosen value other than a limit (the oracle-step tables, peak instants, the retired splitting bound's figures) stay in the test module, because the Done-when names only tolerances and they are the record behind their choices. `docs/VERIFICATION.md` holds several of them too, so `PL-906T` asks for one home each. `docs/INTERFACE.md` § "Why the readouts show two decimals" quotes 2026-09-06 figures outside this item's section; `PL-4FYN` holds it. `RANDOMISED_FRACTION_ROUNDING`'s comment calls 1e-14 "a few units in the last place", about 45; `PL-S6R5` holds it.

No assertion, limit or expected value changed: the module's AST is identical to `origin/main`'s once every string is blanked. One failure message changed its pointer from § "Displayed precision" to § "Comparing two readouts".

Files checked: `docs/INTERFACE.md`, `docs/VERIFICATION.md`, `docs/MODEL.md`, `docs/PARAMETERS.md`, `README.md`, `src/` and `tests/`, by `grep -rn "148 500\|1 485 000\|never disagreed"`. No other place quoted them.

**The owner's read, 2026-11-22.** The question was whether the explanations
inside the three checks against published data could be rewritten, with every
limit and expected value unchanged. The owner answered "research best
practice" at 20:52Z. Read in this session, in full text:

1. Google's documentation best practices
   (https://google.github.io/styleguide/docguide/best_practices.html). Under
   "Delete Dead Documentation": "Dead docs are bad. They misinform". Under
   "Minimum Viable Documentation": "Cut out everything unnecessary, including
   out-of-date, incorrect, or redundant information." Under "Duplication is
   Evil": link to the one guide instead of writing another. Under
   "Documentation is the Story of Your Code": inline comments exist to give
   "information that the code itself cannot contain, such as why the code is
   there."
2. *Software Engineering at Google*, chapter 12, "Unit Testing"
   (https://abseil.io/resources/swe-book/html/ch12.html). Under "Writing Clear
   Tests": "A clear test is one whose purpose for existing and reason for
   failing is immediately clear to the engineer diagnosing a failure." Under
   "Write Clear Failure Messages", the message should carry the important
   information. Under "DAMP, Not DRY", some duplication is acceptable in a test
   "so long as that duplication makes the test simpler and clearer". The
   copies removed here are dated measurements, not test setup, so that
   allowance does not cover them.

Each source supports the rewrite: the comments now give why each limit holds,
the stale measurements are gone, each figure is kept once and pointed at, and
the failure message that misstated its limit is corrected. The ASME V&V 40
subcommittee's slide deck was also read and says nothing on where
verification evidence should be recorded, so it is not relied on.
