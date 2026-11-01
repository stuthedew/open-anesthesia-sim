---
id: PL-16BG
title: An Area's floor depends on the width it is drawn at, but layout/sizing.settle takes each floor as one fixed PixelSize and AreaLayout._floor defaults the width to 0, so each reader of an Area's drawn size or floor (the drag, the minimum size hint, the border warning, the split refusal) works it out again with its own width: six defects in eight days, four of them after the first fix
status: untriaged
feature: area-layout-sizing
touches: src/anesthesia_sim/layout/sizing.py, src/anesthesia_sim/app/area_layout.py
added: 2026-11-01
root-cause-of: PL-97WX, PL-C9XP, PL-MH5T, PL-XX18, PL-9Z74, PL-7DXG
generator: live - PL-MH5T and PL-XX18 were filed on 2026-10-27 against #1880's fix of PL-97WX, and PL-7DXG on 2026-11-01 while building PL-9Z74's; every reader added to AreaLayout chooses its own width for _floor, so the next one will too
misread: The size an Area is drawn at, and its least size, both of which depend on its drawn width
---

**Problem.** An Area's floor depends on the width it is drawn at, but layout/sizing.settle takes each floor as one fixed PixelSize and AreaLayout._floor defaults the width to 0, so each reader of an Area's drawn size or floor (the drag, the minimum size hint, the border warning, the split refusal) works it out again with its own width: six defects in eight days, four of them after the first fix

**Evidence, read on `main` at `8fc5b1c6` on 2026-11-01.** `settle` in
`src/anesthesia_sim/layout/sizing.py` takes `floors: Mapping[AreaId, PixelSize]`,
one fixed size per Area. A too-small Area's floor is not fixed: its notice
wraps at the width the Area is drawn at (`PL-9Z74`). `AreaLayout._settle` works
around this by calling `settle` twice, the second time with floors measured at
the first pass's widths. `AreaLayout._floor(area_id, drawn_width_px=0)` falls
back to the narrowest width when a caller passes none, and `_split_preview`
and `_split_operation` pass none, which is `PL-7DXG`. The drag
(`_drawn_position`), the minimum size hint and the border warning each work
out an Area's drawn size on their own path too.

The six members, each answered alone until now:

- `PL-97WX` (2026-10-25): the drag mapped the pointer linearly while the
  splitters drew `settle`'s held sizes.
- `PL-C9XP` (2026-10-25): the minimum size hint summed the Views' needs while
  `settle` holds an Area at the larger of need and floor.
- `PL-MH5T` (2026-10-27): a re-entry of `PL-97WX` in a window smaller than the
  floors.
- `PL-XX18` (2026-10-27): a re-entry of `PL-97WX`, the warning not turned for
  a neighbour held at its need.
- `PL-9Z74` (2026-10-27): the floor measured at the chooser's width.
- `PL-7DXG` (2026-11-01): the split refusal measures the floor at width 0.

`PL-R4Y2`'s pass of 2026-10-26 saw the first two and called them a lead with
fewer than three members. `PL-Y65Q` and `PL-QZ7Z` are `settle`'s own policy,
not this fact, and are left out.

**Why it matters.** Each fix so far moved one reader onto the drawn sizes and
left the others. A learner meets the result as a View blanked as "Too small"
when it would fit, or a split refused when both halves would fit. No clinical
value is affected.

**Done when.** One function or record states an Area's drawn size and its
floor at a given width. `settle` can hold a floor that depends on width, or
its caller gives it one measured at the drawn width in a single place.
`_floor` has no default width. The drag, the minimum size hint, the border
warning and the split refusal read that one source. A test fails if a new
caller computes a floor without a width. `PL-7DXG` closes with it.

**Generator check.** This is the head. No recorded head's `misread:` states
an Area's drawn size or floor. `PL-R0BJ`'s fact is what must fit at the
1366 by 700 reference window, which is a different fact.
