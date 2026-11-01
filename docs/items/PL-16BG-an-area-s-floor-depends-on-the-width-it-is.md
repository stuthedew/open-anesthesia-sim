---
id: PL-16BG
title: An Area's floor depends on the width it is drawn at, but layout/sizing.settle takes each floor as one fixed PixelSize and AreaLayout._floor defaults the width to 0, so each reader of an Area's drawn size or floor (the drag, the minimum size hint, the border warning, the split refusal) works it out again with its own width: six defects in eight days, four of them after the first fix
priority: P1
effort: M
status: done
classes: defect
feature: area-layout-sizing
touches: src/anesthesia_sim/layout/sizing.py, src/anesthesia_sim/app/area_layout.py, tests/unit/test_layout_sizing.py, tests/integration/test_layout_adapter.py, docs/ARCHITECTURE.md
added: 2026-11-01
closed: 2026-11-01
pr: 1922
payoff: a learner is never shown a View blanked as too small, or refused a split, because one reader of an Area's floor measured it at a width other than the one the Area is drawn at
verify: uv run pytest -q tests/unit/test_layout_sizing.py::test_a_floor_is_computed_only_at_a_width tests/unit/test_layout_sizing.py::test_settle_measures_a_too_small_areas_floor_at_the_width_it_draws_the_area tests/integration/test_layout_adapter.py::test_a_side_by_side_split_is_refused_where_a_narrower_half_could_not_hold_the_notice
root-cause-of: PL-97WX, PL-C9XP, PL-MH5T, PL-XX18, PL-9Z74, PL-7DXG
generator: spent - an Area's floor is now a layout.sizing.Floor whose at() takes the drawn width as a required argument, settle measures each floor at the width it draws the Area, and every AreaLayout reader goes through them, so a new reader cannot choose a width by default
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

**Built 2026-11-01.** `layout/sizing.py` now holds the one statement of an
Area's floor: a `Floor` record whose `at(drawn_width_px)` takes the width as a
required argument, and whose `fits_in(size)` reads the width from the size it
is given. `settle` takes a `Floor` for each Area and measures it at the width
it draws the Area. The two passes that `AreaLayout._settled` and
`_widths_held` ran in the adapter moved into `settle` unchanged, so they are
now tested without Qt. `drawn_bounds` measures each floor at its need's width,
which is the narrowest width at which an Area draws its View. The minimum size
hint reads that. `AreaLayout._floor` takes no width and returns a `Floor`.
The split refusal, for the Area menu and the corner drag alike, asks
`Floor.fits_in` of each part at the size the part would be drawn at
(`_parts_hold_the_floor`). The border warning's `_fits` reads each Area's least
size from `Fit.bounds` instead of reading it back from Qt. The drag
(`_drawn_position`) already read `Fit.bounds`, and still does.

The split refusal now also checks a side-by-side half's height against the
floor at the half's own width. Before, it compared that half's width alone. So
a 400 by 104 px Big view's Area is now refused a side-by-side split whose
196 px halves would need a 112 px floor. That is the same rule that `PL-Y65Q`
decided, applied on both axes.

`tests/unit/test_layout_sizing.py::test_a_floor_is_computed_only_at_a_width`
fails if `Floor.at` is given a default width again. mypy refuses a caller that
omits the width. Regression tests, each run against `main` at `2076f542` with
`src/` restored, where each failed:

- `tests/integration/test_layout_adapter.py::test_a_wide_area_splits_stacked_where_each_half_holds_the_notice_at_the_areas_width`
  failed with `assert False` on `_operation(..., 'Split top and bottom').available`,
  refusal "Not available: each half would be too small to hold its header and a
  notice." (`PL-7DXG`).
- `tests/integration/test_layout_adapter.py::test_a_side_by_side_split_is_refused_where_a_narrower_half_could_not_hold_the_notice`
  failed with `assert not True` on the side-by-side split's `available`.

One reader still works out an Area's drawn size on its own path. `_fits`
estimates it as the Area's share of the window minus one handle, rather than
from the apportionment the splitters draw. Moving it changes where a line drag
stops by about a handle's width, which two adapter tests pin as `PL-RQT1` Q3's
stop. So it is filed as `PL-501T` rather than changed here. It does not read a
floor, so it cannot re-enter this head's fact.
