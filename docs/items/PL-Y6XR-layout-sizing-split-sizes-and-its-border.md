---
id: PL-Y6XR
title: layout/sizing.split_sizes and its border functions accept bounds with a different count from the fractions and return the wrong number of sizes: split_sizes((0.5, 0.5), (300, 0, 0), 400) returns three sizes for two children
priority: P3
effort: S
status: done
classes: defect
feature: interface-areas
touches: src/anesthesia_sim/layout/sizing.py, tests/unit/test_layout_sizing.py
added: 2026-11-23
closed: 2026-11-23
pr: 2297
filed-pr: 2281
payoff: a caller that passes the wrong number of size limits for a split is refused with both counts, rather than given sizes for children that do not exist
tests: tests/unit/test_layout_sizing.py::test_a_split_refuses_bounds_that_are_not_one_for_each_child
---

**Problem.** layout/sizing.split_sizes and its border functions accept bounds with a different count from the fractions and return the wrong number of sizes: split_sizes((0.5, 0.5), (300, 0, 0), 400) returns three sizes for two children

**What happens.** `split_sizes`, `border_range` and `border_share` in `src/anesthesia_sim/layout/sizing.py` neither check nor document that `bounds` has one entry for each fraction. The strict `zip` in `_held_sizes` is the only guard, and it does not always run: `split_sizes((0.5, 0.5), (300, 0, 0), 400)` returns `(300, 100, 0)`, three sizes for two children. No caller passes such a mismatch today. Found on 2026-11-23 while sorting `PL-00Y5`'s survivors (`_held_sizes` mutants 12, 15 and 16, which no test can kill until the check exists).

Two smaller findings in the same function:

1. The branch of `_held_sizes` for a split where every child is held hands out the pixels left over beyond the bounds. It is reached only when the bounds fill the split exactly, so there are never any (mutant 67), and its comment describes a case that cannot happen.
2. `pixel_sizes` gives a tie to the earlier size only where the tie is exact in floating point. `split_sizes((1/49, 19/49, 9/49, 20/49), (11, 8, 3, 10), 35)` returns `(11, 9, 5, 10)`, where exact arithmetic and the stated rule give `(11, 10, 4, 10)`. The difference is one pixel, and no child falls below its bound.

**What to do.** Refuse bounds whose count differs from the fractions', at the top of each public function, with a message that gives both counts, and test it. Remove the empty branch or say why it stays. Decide whether the tie rule needs exact arithmetic, or reword it to say what the code does.


**Done when.** `split_sizes`, `border_range` and `border_share` refuse `bounds` whose count differs from the fractions', with a `ValueError` whose message gives both counts, and a test checks all three with a longer and a shorter `bounds`. `_held_sizes` has no branch for pixels left over once every child is held, and a comment says why there are none. The docstring of `pixel_sizes` says what its tie rule does in floating point.

**Generator check.** A one-off. The fact misread is how many bounds a split's caller passes, which only the strict `zip` in `_held_sizes` checked, and only on one path. No head's `misread:` names an argument count, and `apportion`, the one caller, builds one bound for each child.

**Done 2026-11-23.** `_require_one_bound_each` in `layout/sizing.py` refuses the mismatch at the top of `split_sizes` and `border_range`, and `border_share` reaches it through `border_range`. Each docstring names the `ValueError`. `tests/unit/test_layout_sizing.py::test_a_split_refuses_bounds_that_are_not_one_for_each_child` checks all three functions with three bounds and with one bound for two children. Against the code before the fix, the case of three bounds fails with "DID NOT RAISE ValueError", and the case of one bound fails because the strict `zip` raised a message that names no count. The branch of `_held_sizes` for a split whose every child is held is removed. A comment there gives the reason: the last children to be held each had a share less than their bound, which leaves no pixels over unless the bounds need more than the split has, a case the function has already returned from. `test_a_split_exactly_as_long_as_its_childrens_bounds_gives_each_child_its_bound` still covers that path. The tie rule of `pixel_sizes` now says that an exact tie in floating point goes to the earlier size, and that two shares that would tie in exact arithmetic go to whichever lost more in floating point. Exact arithmetic was not taken, because the stored fractions are floats, so the shares that tie in exact arithmetic, such as 19/49 and 9/49, are not the values the function is given. `test_pixel_sizes_give_a_left_over_pixel_to_the_earlier_of_two_equal_losses` pins the exact-tie half. Documents checked: `docs/INTERFACE.md` (its only tie rule is the hover's, which this does not touch), `docs/ARCHITECTURE.md` and `docs/interface-provenance.md` (neither states the rounding rule).

**Blind review, 2026-11-23.** One pass, which reported no findings.
