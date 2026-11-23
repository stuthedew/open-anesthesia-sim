---
id: PL-Y6XR
title: layout/sizing.split_sizes and its border functions accept bounds with a different count from the fractions and return the wrong number of sizes: split_sizes((0.5, 0.5), (300, 0, 0), 400) returns three sizes for two children
status: untriaged
feature: interface-areas
added: 2026-11-23
filed-pr: 2281
---

**Problem.** layout/sizing.split_sizes and its border functions accept bounds with a different count from the fractions and return the wrong number of sizes: split_sizes((0.5, 0.5), (300, 0, 0), 400) returns three sizes for two children

**What happens.** `split_sizes`, `border_range` and `border_share` in `src/anesthesia_sim/layout/sizing.py` neither check nor document that `bounds` has one entry for each fraction. The strict `zip` in `_held_sizes` is the only guard, and it does not always run: `split_sizes((0.5, 0.5), (300, 0, 0), 400)` returns `(300, 100, 0)`, three sizes for two children. No caller passes such a mismatch today. Found on 2026-11-23 while sorting `PL-00Y5`'s survivors (`_held_sizes` mutants 12, 15 and 16, which no test can kill until the check exists).

Two smaller findings in the same function:

1. The branch of `_held_sizes` for a split where every child is held hands out the pixels left over beyond the bounds. It is reached only when the bounds fill the split exactly, so there are never any (mutant 67), and its comment describes a case that cannot happen.
2. `pixel_sizes` gives a tie to the earlier size only where the tie is exact in floating point. `split_sizes((1/49, 19/49, 9/49, 20/49), (11, 8, 3, 10), 35)` returns `(11, 9, 5, 10)`, where exact arithmetic and the stated rule give `(11, 10, 4, 10)`. The difference is one pixel, and no child falls below its bound.

**What to do.** Refuse bounds whose count differs from the fractions', at the top of each public function, with a message that gives both counts, and test it. Remove the empty branch or say why it stays. Decide whether the tie rule needs exact arithmetic, or reword it to say what the code does.
