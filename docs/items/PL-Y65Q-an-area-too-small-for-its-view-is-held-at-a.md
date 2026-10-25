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
