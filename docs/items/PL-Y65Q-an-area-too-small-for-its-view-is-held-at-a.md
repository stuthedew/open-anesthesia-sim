---
id: PL-Y65Q
title: An Area too small for its View is held at a floor of header, rule, padding and one line, so its notice gets about 31 px: the body that states the size the View needs and the size the Area has gets 0 px of the 119-153 px it needs, and even the "Too small for ..." title gets 0 px
priority: P2
effort: S
status: ready
classes: defect, ux
feature: area-layout-sizing
touches: src/anesthesia_sim/app/area_layout.py, tests/integration/test_layout_adapter.py
added: 2026-10-25
payoff: a reader shown a too-small Area learns how much room its View needs, instead of seeing an empty strip
verify: grep -q 'def test_an_area_held_at_its_floor_shows_its_whole_notice' tests/integration/test_layout_adapter.py
recurrences: 2026-10-25 PL-C9XP
---

**Problem.** `_structural_minimum` sets the floor to the chooser's width and the header plus one line of height (`app/area_layout.py`). `settle` holds a too-small Area at that floor, and `frame.setMinimumSize` overrides the notice's own minimum. That happens when a kept neighbour takes the rest of a fixed window, and in the all-floors fallback. The adapter tests check only that each frame is at least its minimum.

**Why it matters.** `PL-K285`'s notice exists to tell the reader how much room the View needs. At the floor, the reader sees an empty strip, or part of a title, and no statement at all.

**Done when.** An Area held at its floor shows at least the notice's title and its statement of the size the View needs and the size the Area has. `tests/integration/test_layout_adapter.py` has `test_an_area_held_at_its_floor_shows_its_whole_notice`.

**Found by.** `PL-TBQS` reviewer replay on #1622, finding r01 F2, checked against main on 2026-10-25. Measured offscreen with `e_s_notice_floor.py` on the default dashboard's first two Areas. The floors were 168x58 and 143x58. The notice got 31 px of height. The title needed 34-51 px and the body needed 119-153 px, and both were laid out 0 px tall.

**Decided 2026-10-26: route B.** The project's coordinator chose it, under the owner's rule of 2026-10-18 that look, wording and placement are placeholders that Claude decides unless a required value's visibility is at stake. No clinical value is hidden here. This was not the owner's own decision. The weighing follows.

**The choice, as it was put (2026-10-26).** Any fix makes a too-small Area's floor taller, because the notice cannot be read in about 31 px. A taller floor means that, in a window too small for every View, a neighbour gives up its View sooner. Three routes were weighed:

- **A. The floor holds the whole notice.** That is the title and the full body, wrapped at the floor's width of about 140-170 px, so about 190 px more height. The notice reads in full, but a neighbour loses its View about 190 px sooner.
- **B. The floor holds the title and a short statement of the two sizes, such as "Needs 300 × 200 px; has 143 × 31 px."** That is about 50 px more height. The advice sentence ("Drag a border to enlarge it ...") shows only where the Area has room for it. The short statement changes `PL-DB5G` Q3's wording at the floor.
- **C. Keep the floor and let the notice scroll or cut off.** This was rejected, because a reader still sees no statement without acting.

**Recommendation: B.** It is the smallest floor that still says how much room the View needs, so a neighbour gives up its View least often. The cost is a second, shorter wording of the notice, which is used only where the full one cannot fit.
