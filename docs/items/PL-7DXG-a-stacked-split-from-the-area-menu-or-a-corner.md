---
id: PL-7DXG
title: A stacked split from the Area menu or a corner drag still measures the floor its halves need with the notice wrapped at the floor's own width, so a wide Area's split is refused where each half could hold its notice: a 400 by 250 px Area's 121 px halves are refused against a 146 px floor, though the notice wrapped at 400 px needs 95 px (found building PL-9Z74)
priority: P2
effort: S
status: done
classes: defect
feature: area-layout-sizing
milestone: v0.6.13
touches: src/anesthesia_sim/app/area_layout.py, tests/integration/test_layout_adapter.py
added: 2026-11-01
closed: 2026-11-01
pr: 1922
payoff: a learner with a wide Area can split it top and bottom wherever each half can show the too-small notice
verify: uv run pytest -q tests/integration/test_layout_adapter.py::test_a_wide_area_splits_stacked_where_each_half_holds_the_notice_at_the_areas_width tests/integration/test_layout_adapter.py::test_a_stacked_split_is_refused_where_a_half_could_not_hold_the_notice_at_its_width
---

**Problem.** A stacked split from the Area menu or a corner drag still measures the floor its halves need with the notice wrapped at the floor's own width, so a wide Area's split is refused where each half could hold its notice: a 400 by 250 px Area's 121 px halves are refused against a 146 px floor, though the notice wrapped at 400 px needs 95 px (found building PL-9Z74)

**Why it matters.** `PL-9Z74` made the floor that `settle` holds a too-small
Area at wrap the notice at the width the Area is drawn at. The split refusal
in `AreaLayout._split_operation` and `_split_preview` still calls `_floor`
with no width, which wraps the notice at the floor's own width, the
narrowest an Area is drawn. So the two disagree about how tall a too-small
Area must be. A reader with a wide Area is refused a stacked split whose
halves would each show the too-small notice in full.

**Why it was not fixed in `PL-9Z74`.** Passing the half's width would allow
the split that `test_a_split_is_refused_where_a_half_could_not_hold_the_too_small_notice`
pins as refused. That test records `PL-Y65Q`'s decision, so changing it is a
change to a decided behaviour rather than part of the floor fix.

**Done when.** A stacked split is refused only where a half, at the Area's
width, could not hold its header and the too-small notice wrapped at that
width, and the test above is rewritten to a width at which the refusal
still holds.

**Built 2026-11-01 under `PL-16BG`.** `_split_operation` and `_split_preview`
ask `Floor.fits_in` of each part at the size the part would be drawn at, so a
stacked half's floor wraps the notice at the Area's width. The test named
above is rewritten as
`test_a_stacked_split_is_refused_where_a_half_could_not_hold_the_notice_at_its_width`,
at 150 by 250 px, where the notice wrapped at 150 px needs 146 px and each
half has 121 px. The refusal still holds there, and the test passes before and
after the fix.
`test_a_wide_area_splits_stacked_where_each_half_holds_the_notice_at_the_areas_width`
is the regression test for this item. Run against `main` at `2076f542` with
`src/` restored, it failed with `assert False` on the stacked split's
`available`.


**Generator check.** Explained by `PL-16BG`, whose `misread:` is this fact. That head closes in the same pull request.
