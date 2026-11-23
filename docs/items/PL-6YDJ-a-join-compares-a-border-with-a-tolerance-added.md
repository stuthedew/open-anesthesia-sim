---
id: PL-6YDJ
title: A join compares a border with a tolerance added in floating point, so an Area edge just inside the tolerance can be refused or moved
status: untriaged
feature: interface-areas
added: 2026-11-23
filed-pr: 2281
---

**Problem.** `_full_cuts` in `src/anesthesia_sim/layout/model.py` decides where a join may cut straight across a region. It tests `low + BORDER_ALIGNMENT_TOLERANCE < start < high - BORDER_ALIGNMENT_TOLERANCE` and `begin < at - BORDER_ALIGNMENT_TOLERANCE and end > at + BORDER_ALIGNMENT_TOLERANCE`. Each sum rounds, so the comparison is not the one the docstring states: "each by more than the tolerance". The rest of the model compares a difference with the tolerance, as `_close` does.

The mutation sort of `PL-00Y5` found it through four survivors of `_full_cuts` (mutants 9, 10, 11 and 29 at commit `0117c839`), which change only the comparison and which no input that is not 1e-9 from a border can tell apart. Two effects follow, each measured on the branch by the sorting worker:

1. When a split's edge lies between 0.25 and 0.5 of the window, an Area edge 1.0000000272e-9 from it counts as the same edge, so a join of two Areas that share a whole edge is refused as having no straight cut.
2. An Area that starts 1.00000004e-9 before a cut counts as not entered. The join then moves that Area's edge by more than the tolerance, and it stretched a 1.5e-9-wide Area from half to full height.

Only an Area about 1e-9 of the window wide is affected, and the adapter's pixel minimums stop a drag from making one. A layout file or a cut at that exact fraction can still reach it. No View that carries a required value is hidden by it.

**Fix.** Compare differences, as `_close` does: `start - low > TOL and high - start > TOL`, and `at - begin > TOL and end - at > TOL`. `tests/unit/test_layout_model.py::test_a_join_cuts_through_an_area_that_reaches_past_the_cut_by_less_than_the_tolerance` passes under that fix. Add a regression test for each of the two effects above, run against the code before the fix, as `.claude/rules/test-oracles.md` rule 6 says.
