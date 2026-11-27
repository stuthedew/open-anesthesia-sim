---
id: PL-PL6D
title: A layout join can take a chain of edges that reaches its region's edge for a cut, and move an Area that is not part of the join
priority: P3
effort: S
status: ready
classes: defect
feature: interface-areas
touches: src/anesthesia_sim/layout/model.py, tests/unit/test_layout_model.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-23
filed-pr: 2299
payoff: a join moves only the two Areas it joins
---

**Problem.** `_full_cuts` in `src/anesthesia_sim/layout/model.py` skips a leading edge within the tolerance of the region's own edge, comparing each edge with the region's edge alone. It also joins the edges of one line edge to edge, each within the tolerance of the last. So a line whose first edge is skipped can still be followed from a later edge that chains back to the region's edge, and taken as a cut. The join then stretches an Area across the strip that the skipped edge bounded, which the rectangles cannot hold, where a refusal was due.

**What happens.** In `column((0.5, 0.5), row((0.3, 1.3e-9, 0.7 - 1.3e-9), a1, a2, column((0.5, 0.5), a3, a4)), row((0.3 + 0.8e-9, 0.7 - 0.8e-9), a5, column((0.2, 0.8), a6, a7))))`, `join(4, 6)` moves the bottom of Area 2, which is not part of the join, from 0.5 to 0.6 of the window. Area 4 grows from 0.5 to 0.6 as the join intends. Area 2 is 1.3e-9 of the window wide, far less than a pixel, so nothing a user sees changes. The code before `PL-6YDJ` gives the same result. Found by `PL-6YDJ`'s blind review on 2026-11-23, and reproduced on that branch and on the code before it.

**What to do.** Decide a line's distance from the region's edge from the whole chain, so that a line is skipped when any of its edges lies within the tolerance of the region's edge, or refuse a join whose result moves an Area outside the pair. Add a test from the layout above that checks every Area's rectangle after the join, or the refusal.

**Why it matters.** A join can move an Area the reader did not touch. At the widths found it is far below a pixel, so no user sees it today, but the same rule at a larger width would move a View without warning.

**Done when.** A test from the layout above shows the join either leaves every Area outside the pair where it was or is refused.

**Generator check.** A one-off: a tolerance compared edge by edge instead of along the whole line.

**Reproduced 2026-11-23** by `PL-6YDJ`'s review, on that branch and on the code before it.
