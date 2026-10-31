---
id: PL-Y65Q
title: An Area too small for its View is held at a floor of header, rule, padding and one line, so its notice gets about 31 px: the body that states the size the View needs and the size the Area has gets 0 px of the 119-153 px it needs, and even the "Too small for ..." title gets 0 px
priority: P2
effort: S
status: done
classes: defect, ux
feature: area-layout-sizing
milestone: v0.6.9
touches: src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/view_registry.py, src/anesthesia_sim/layout/sizing.py, tests/integration/test_layout_adapter.py, tests/unit/test_view_registry.py
added: 2026-10-25
closed: 2026-10-26
pr: 1858
payoff: a reader shown a too-small Area learns how much room its View needs, instead of seeing an empty strip
verify: grep -q 'def test_an_area_held_at_its_floor_shows_its_whole_notice' tests/integration/test_layout_adapter.py
recurrences: 2026-10-25 PL-C9XP withdrawn 2026-10-27 PL-8MRM
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

## Done 2026-10-26

Route B is built. `AreaLayout._floor` now holds an Area that is too small for
its View at the height of its header, the notice's title and a short
statement of the two sizes, each wrapped at the floor's width. It measures that
height by laying the notice out in a probe that is never shown, so the floor
follows the font and the wrapping rather than an estimate. The floor is never
taller than the View's own need, because an Area given its need draws the View
and shows no notice. `view_registry.too_small_short_text` writes the short
statement, "Needs 300 by 200 px; has 170 by 119." The notice's body switches to
it only where the full notice does not fit the Area, so the advice sentence
still shows wherever there is room. The short wording is a placeholder,
decided under the owner's rule of 2026-10-18.

The floor costs more height than the item's estimate. At 170 px wide, the title
and the short statement each wrap to two lines, so the notice needs 119 px and
the floor is 146 px, not about 108. A neighbour therefore gives up its View
about 88 px sooner than before, in a window too small for every View.

`test_an_area_held_at_its_floor_shows_its_whole_notice` holds a Big view's
Area at its floor in a 170 by 300 px window. It checks that the Area is at its
floor, that it shows the title and the short statement, and that each label is
laid out at the height its wrapped text needs. On the old floor, the same Area
was 31 px tall below its header, and its notice's labels had no room.

A split is now refused where a half would be less than this floor, not only
where it would be less than the header and one line.
`test_a_split_is_refused_where_a_half_could_not_hold_the_too_small_notice`
pins it: a Big view's Area 250 px tall cannot be split top and bottom. Without
that, a split could leave two halves whose floors add up to more than the
split has, and the second would be pushed past the edge. The blind review
found it (pass 1, F1). Its F2, that the floor is measured at the chooser's
width even where the Area is drawn much wider, is filed as `PL-9Z74`.
