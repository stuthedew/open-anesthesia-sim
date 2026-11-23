---
id: PL-6YDJ
title: A join compares a border with a tolerance added in floating point, so an Area edge just inside the tolerance can be refused or moved
priority: P3
effort: S
status: done
classes: defect
feature: interface-areas
touches: src/anesthesia_sim/layout/model.py, tests/unit/test_layout_model.py, docs/items/PL-PL6D-a-layout-join-can-take-a-chain-of-edges-that.md
added: 2026-11-23
closed: 2026-11-23
pr: 2299
filed-pr: 2281
payoff: a join decides a border just more than the tolerance from another the same way however the sum rounds, and refuses a result it cannot hold rather than failing
tests: tests/unit/test_layout_model.py::test_a_join_cuts_down_a_border_just_more_than_the_tolerance_inside_its_region, tests/unit/test_layout_model.py::test_a_join_cuts_no_area_that_begins_just_more_than_the_tolerance_before_the_cut, tests/unit/test_layout_model.py::test_a_join_that_would_round_an_area_down_to_the_tolerance_is_refused
---

**Problem.** `_full_cuts` in `src/anesthesia_sim/layout/model.py` decides where a join may cut straight across a region. It tests `low + BORDER_ALIGNMENT_TOLERANCE < start < high - BORDER_ALIGNMENT_TOLERANCE` and `begin < at - BORDER_ALIGNMENT_TOLERANCE and end > at + BORDER_ALIGNMENT_TOLERANCE`. Each sum rounds, so the comparison is not the one the docstring states: "each by more than the tolerance". The rest of the model compares a difference with the tolerance, as `_close` does.

The mutation sort of `PL-00Y5` found it through four survivors of `_full_cuts` (mutants 9, 10, 11 and 29 at commit `0117c839`), which change only the comparison and which no input that is not 1e-9 from a border can tell apart. Two effects follow, each measured on the branch by the sorting worker:

1. When a split's edge lies between 0.25 and 0.5 of the window, an Area edge 1.0000000272e-9 from it counts as the same edge, so a join of two Areas that share a whole edge is refused as having no straight cut.
2. An Area that starts 1.00000004e-9 before a cut counts as not entered. The join then moves that Area's edge by more than the tolerance, and it stretched a 1.5e-9-wide Area from half to full height.

Only an Area about 1e-9 of the window wide is affected, and the adapter's pixel minimums stop a drag from making one. A layout file or a cut at that exact fraction can still reach it. No View that carries a required value is hidden by it.

**Fix.** Compare differences, as `_close` does: `start - low > TOL and high - start > TOL`, and `at - begin > TOL and end - at > TOL`. `tests/unit/test_layout_model.py::test_a_join_cuts_through_an_area_that_reaches_past_the_cut_by_less_than_the_tolerance` passes under that fix. Add a regression test for each of the two effects above, run against the code before the fix, as `.claude/rules/test-oracles.md` rule 6 says.


**Done when.** `_full_cuts` in `layout/model.py` compares the difference between two edges with `BORDER_ALIGNMENT_TOLERANCE`, as `_close` does, in both of its checks, and a unit test for each of the two effects above fails on the code before the fix.

**Generator check.** A one-off. The fact misread is how this module compares two edges with the tolerance, which `_close` already states. `_full_cuts` wrote the comparison out again as a sum, and no other function in `layout/model.py` adds the tolerance to an edge. No head's `misread:` names the tolerance comparison.

**Done 2026-11-23.** `_clearly_before` in `layout/model.py`, beside `_close`, returns whether one edge lies before another by more than the tolerance, comparing their difference. `_full_cuts` uses it for both checks. Two tests in `tests/unit/test_layout_model.py` build the layouts that the sorting run measured, assert as premises that each case sits at the rounding edge, and check where every Area lies after the join, from rectangles worked out in the test. `test_a_join_cuts_down_a_border_just_more_than_the_tolerance_inside_its_region` fails on the code before the fix with "LayoutRefused: Area 3 and Area 5 cannot be joined: no straight cut divides the Areas the join would leave". `test_a_join_cuts_no_area_that_begins_just_more_than_the_tolerance_before_the_cut` fails there because Area 2's left edge moved to 0.30000000200000004, 1.0000000272e-9 from where it was; the same run also stretched Area 4 to the window's whole height. Documents checked: `docs/INTERFACE.md` (its join and tolerance sections state no comparison), `docs/ARCHITECTURE.md` and `docs/interface-provenance.md` (neither states how edges are compared).

**Blind review, 2026-11-23.** One pass. It found that the new comparison accepts a cut that leaves an Area a few units in the last place wider than the tolerance, and that the rebuilt splits, which store fractions, can place that Area's edges again no more than the tolerance apart. The result then raised `InvalidLayout` out of `join`, which an Area's menu does not catch, where the old comparison had refused the join. `join` now checks its result as `split` does, and refuses such a join with `LayoutRefused`. `test_a_join_that_would_round_an_area_down_to_the_tolerance_is_refused` nests the first test's layout two levels down, and on the code before that fix it fails with "InvalidLayout: in window 0, Area 2 is 9.999999717180685e-10 of the window wide". The pass also found that `_full_cuts` compares each leading edge with the region's own edge alone, while it joins the edges of a line one to the next, so a chain of edges that reaches the region's edge can still be taken as a cut. That is older than this change, moves an Area far less than a pixel wide, and is filed as `PL-PL6D`.
