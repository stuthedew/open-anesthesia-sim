---
id: PL-744F
title: A whole View's Area is held at the height its View needs at the Area's least width, which overstates it at a wider drawn width; at 1366x768 with a branch, Induction's Parameters Area is held about 30 px taller than it needs, so the page scrolls that much more
status: done
feature: window-is-the-frame
added: 2026-11-23
closed: 2026-11-23
pr: 2286
filed-pr: 2282
tests: tests/integration/simulation_view/test_simulation_view_page.py::test_a_whole_view_is_held_at_the_height_it_needs_at_the_width_it_is_drawn, tests/integration/simulation_view/test_simulation_view_page.py::test_a_layout_drawn_again_keeps_its_sizes_where_the_page_scroll_bar_comes_and_goes, tests/integration/simulation_view/test_simulation_view_page.py::test_a_frame_that_changes_no_need_does_not_lay_the_areas_out_again
---

**Problem.** `AreaLayout._view_need` in `src/anesthesia_sim/app/area_layout.py`
measures a `whole` View's content height at the Area's least width, so that
the need does not depend on the last layout. An Area drawn wider than its
least width then needs fewer lines of wrapped text, but is still held at the
taller height. The page grows by the difference whenever the Areas do not fit
the window.

**Measured 2026-11-23** (Inter, 1366 by 768, a branch open, 300 s of one run),
by reading each whole View's least height at the width its Area is drawn:

| Workspace | View | Held, px | Needed at drawn width, px | Drawn width, px |
| --- | --- | --- | --- | --- |
| Induction | Parameters | 323 | 293 | 656 |
| Maintenance | Parameters | 323 | 293 | 592 |

So the page scrolls about 30 px more than the Views need in Induction and
Maintenance. Default's Branch Area, first listed here at 137 px held against
100 px needed, is held at the least height its registry entry declares, not
at a height measured at its least width, so it is not this defect. The blind review of `PL-5J1X` (hold the page's scroll to
what the Areas lack) found it.

**What a fix has to keep.** The need was measured at the least width so that
one settle gives the same sizes as the next. A need taken at the drawn width
can feed back: a shorter need can remove the page's scroll bar, which widens
the Areas, which shortens the need again. The widths of the Areas come from
their width needs and the window, not from their heights, so a second pass
that re-measures each whole View at the width the first pass drew it should
settle. The fix must show that it does, including at a page height where the
scroll bar just appears or disappears.

**Fixed, 2026-11-23.** `AreaLayout._settle` first lays the Areas out at
the widget's width and at a height tall enough for every need measured at
its least width, so no Area gives up its View for want of height. It then
measures each need again at the width that layout drew its Area
(`AreaLayout._narrowed`), and lays the Areas out at the widget's real size
with those needs. A need's width does not change with the width it is
measured at, so that layout keeps the same widths, and the heights it holds
are the heights the Views need at those widths. Where it would change a
width, the Areas are laid out with the needs at the least width, as before.
`follow_needs` compares the needs at the widths of the first layout with
the ones the settle measured there, so a View whose wrapped text changes at
its drawn width settles the Areas again, and a frame that changes nothing
does not.

Measured offscreen under Inter at 1366 by 768 with a branch open: the
Parameters Area in Induction and Maintenance is held at 293 px rather than
323 px, so those pages scroll 30 px less. Default is unchanged.

1. `test_a_whole_view_is_held_at_the_height_it_needs_at_the_width_it_is_drawn`
   works the Parameters View's least height out from its own Qt layout at
   its drawn width. It fails on the code before the fix with
   "assert 323 == (27 + 266)" in both Workspaces.
2. `test_a_layout_drawn_again_keeps_its_sizes_where_the_page_scroll_bar_comes_and_goes`
   draws Induction at nine window heights from 1,044 to 1,076 px, either side
   of 1,060 px, where the page's scroll bar disappears, and checks that a
   second frame draws every Area where the first did. A shorter need cannot
   feed back through the scroll bar into a different layout, because a View's
   height does not grow as its width grows.
3. `test_a_frame_that_changes_no_need_does_not_lay_the_areas_out_again`
   makes the layout refuse the narrowed needs every time, and checks that
   three frames that change nothing lay the Areas out no more. It fails on
   the code before the review fix below, with six settles in three frames.

**Blind review, 2026-11-23**, one pass. Both findings were fixed.

1. The first version read the widths from a layout at the widget's own
   height. Once the page had shrunk to the narrowed needs, that layout had
   too little height for the needs at the least width, so it could give an
   Area's View up as too small, change a width, and make the settle keep the
   taller needs. The page could then grow and shrink on alternate settles.
   The widths are now read from a layout tall enough for every need. A probe
   that put the Compartment schematic, Agent cost, Wash-in and Bookmarks Views
   into each Area of every shipped Workspace at 1366 by 768 with a branch
   found no layout that moved between frames, before or after the fix, so no
   test reproduces the reported sequence.
2. Where the narrowed needs were refused, `follow_needs` compared them with
   the needs the settle kept, found them unequal on every frame, and laid
   the whole page out again on every tick. Test 3 above holds it.

Files checked: `docs/INTERFACE.md` § "Values that must stay reachable" and
the layout sections (they state the page scroll as the fallback and give no
measured height), `docs/ARCHITECTURE.md` (names `area_layout.py` without its
sizing rule), and the comments in `app/view_registry.py` on `whole`. None
needed a change.
