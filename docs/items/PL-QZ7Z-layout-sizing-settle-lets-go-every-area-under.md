---
id: PL-QZ7Z
title: layout/sizing.settle lets go every Area under the first unheld split at once, and that split is always the root, so a window a few pixels short of the Views' needs blanks every View, including ones that would still fit if one Area gave way
priority: P2
effort: M
status: ready
classes: defect, ux
feature: area-layout-sizing
touches: src/anesthesia_sim/layout/sizing.py, tests/unit/test_layout_sizing.py, tests/integration/test_layout_adapter.py
added: 2026-10-25
payoff: a window a few pixels short no longer blanks every View, including the required accounting View
verify: grep -q 'def test_settle_releases_only_the_areas_that_must_give_way' tests/unit/test_layout_sizing.py
---

**Problem.** `apportion` lists a split as unheld before it visits the split's children, so `unheld[0]` is always the root. `settle` then drops every non-kept Area under it to its floor in one pass. If none is left, it drops every kept Area at once (`layout/sizing.py`). The docstring describes "the first such split's Areas". It does not say "every Area in the window".

**Why it matters.** Every Area counts as kept on first show and on any shrink of a fixed window. A small shortfall then turns every View into a "Too small" notice. That can include the required accounting View, even where releasing one Area would leave the others drawn.

**Done when.** `settle` releases Areas one at a time, or one split at a time from the deepest, until the rest fit, so a small shortfall blanks only the Areas that must give way. Its docstring says what it releases. `tests/unit/test_layout_sizing.py` has `test_settle_releases_only_the_areas_that_must_give_way`, covering the three cases in the brief.

**Found by.** `PL-TBQS` reviewer replay on #1622, findings r02 F2, r03 F3, r05 F2 and r06 F2, checked against main on 2026-10-25. Reproduced with `e_t_settle_all_at_once.py`, and none of these cases drew any View. A 0.2/0.4/0.4 column of three 300 px needs at 700 px, all kept, drew nothing, though two fit in 676 px. Two 300 px halves at 500 px, both kept, drew nothing, though 300 + 8 + 177 fits. A top Area over a row of two at 590 px drew nothing, kept or not.
