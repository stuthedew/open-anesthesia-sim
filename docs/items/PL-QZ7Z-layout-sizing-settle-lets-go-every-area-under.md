---
id: PL-QZ7Z
title: layout/sizing.settle lets go every Area under the first unheld split at once, and that split is always the root, so a window a few pixels short of the Views' needs blanks every View, including ones that would still fit if one Area gave way
priority: P2
effort: M
status: done
classes: defect, ux
feature: area-layout-sizing
milestone: v0.6.9
touches: src/anesthesia_sim/layout/sizing.py, tests/unit/test_layout_sizing.py, tests/integration/test_layout_adapter.py
added: 2026-10-25
closed: 2026-10-27
pr: 1880
payoff: a window a few pixels short no longer blanks every View, including the required accounting View
verify: grep -q 'def test_settle_releases_only_the_areas_that_must_give_way' tests/unit/test_layout_sizing.py
---

**Problem.** `apportion` lists a split as unheld before it visits the split's children, so `unheld[0]` is always the root. `settle` then drops every non-kept Area under it to its floor in one pass. If none is left, it drops every kept Area at once (`layout/sizing.py`). The docstring describes "the first such split's Areas". It does not say "every Area in the window".

**Why it matters.** Every Area counts as kept on first show and on any shrink of a fixed window. A small shortfall then turns every View into a "Too small" notice. That can include the required accounting View, even where releasing one Area would leave the others drawn.

**Done when.** `settle` releases Areas one at a time, or one split at a time from the deepest, until the rest fit, so a small shortfall blanks only the Areas that must give way. Its docstring says what it releases. `tests/unit/test_layout_sizing.py` has `test_settle_releases_only_the_areas_that_must_give_way`, covering the three cases in the brief.

**Found by.** `PL-TBQS` reviewer replay on #1622, findings r02 F2, r03 F3, r05 F2 and r06 F2, checked against main on 2026-10-25. Reproduced with `e_t_settle_all_at_once.py`, and none of these cases drew any View. A 0.2/0.4/0.4 column of three 300 px needs at 700 px, all kept, drew nothing, though two fit in 676 px. Two 300 px halves at 500 px, both kept, drew nothing, though 300 + 8 + 177 fits. A top Area over a row of two at 590 px drew nothing, kept or not.

**Built (2026-10-27).** `settle` now drops the fewest Areas that must give way. It ranks the possible drops by the least shortfall reached, then the fewest kept Areas dropped, then the fewest Areas dropped, then the smallest share of the window, then the later Areas in reading order. It weighs every subset where the tree has at most ten Areas, which took about 12 ms in the worst case measured. A larger tree drops one Area at a time by the same ranking. A first build dropped one Area at a time for every tree, and both review passes on #1880 found layouts where that blanked two Views where one would do. The share tie-break is a placeholder chosen by the session: it blanks the View the reader gave the least room. A split whose new halves cannot both fit now blanks only the later half, not both.
