---
id: PL-5J1X
title: At 1366 by 768 with a branch open, the page scrolls in every shipped Workspace (150 px in Default, 206 in Induction, 223 in Maintenance, measured 2026-11-22), because the Parameters View then needs two rows of dials; the Default right column falls short by about 40 px, yet the page grows by 150, so check whether the sizing grows the page by more than the Areas' shortfall, and whether a two-run arrangement can avoid page scrolling (found in review of PL-D5J4)
status: done
feature: interface-design-review
added: 2026-11-22
closed: 2026-11-23
pr: 2282
tests: tests/integration/simulation_view/test_simulation_view_page.py::test_a_page_that_scrolls_grows_only_by_what_the_areas_lack
---

**Problem.** At 1366 by 768 with a branch open, the page scrolls in every shipped Workspace (150 px in Default, 206 in Induction, 223 in Maintenance, measured 2026-11-22), because the Parameters View then needs two rows of dials; the Default right column falls short by about 40 px, yet the page grows by 150, so check whether the sizing grows the page by more than the Areas' shortfall, and whether a two-run arrangement can avoid page scrolling (found in review of PL-D5J4)

**A related case, measured 2026-11-22 by `PL-S6CP`.** With one run, an advisory above the concentration plot (all traces hidden) grows the chart's Area to keep the plot whole, and the page then scrolls 47 px in Induction and in Maintenance at 1366 by 768. Default does not scroll. The chart's Area is in a column whose other Area, Parameters, is already at its least height, so the page takes the height.

**Answered, 2026-11-23.** Both questions were measured offscreen at 1366 by 768,
one run at 300 s with a branch taken at 60 s, on `main` at `83359d86`.

1. **The page grows by exactly what the Areas lack, and no more.** With a
   branch the region above the Areas grows 97 px (a second transport row, a
   second value in each readout card, a second control-changes card), so the
   Areas get 391 px below the Workspace tabs instead of 488. Default's right
   column needs 613 px (Parameters 323, Bookmarks 137, Branch 137 and two
   borders), and the page scrolls 222 px, which is 613 less 391. Induction and
   Maintenance need 690 px and scroll 299 px. The brief's "short by 40 px yet
   grows by 150" no longer reproduces. The new test
   `test_a_page_that_scrolls_grows_only_by_what_the_areas_lack` adds up each
   Area frame's least height along the layout tree, without reading the height
   the Areas report to the page, and holds the page's scroll range to the
   difference. Made to report 40 px more than the frames need, the Areas fail
   it in all three Workspaces ("assert 653 == 613" in Default).
2. **No two-run arrangement of the Areas avoids the page scroll at this
   size.** Induction's and Maintenance's concentration chart needs 344 px
   whole with two runs, which leaves 47 px of the 391 for the Parameters
   Area in the same column, and the Parameters View needs at least 137 px to
   show one run's row. Default's right column cannot hold two rows of dials
   (296 px) and the Bookmarks and Branch Areas at their least heights either.
   Compacting the two-run Parameters View into one card per setting would save
   about 116 px, and putting two runs' readouts side by side in each card
   about 58 px, so neither, nor both together, removes the scroll.
3. **The alternative was built as a prototype and measured, and it is
   worse.** `PL-CBYS` decided that the window is the frame (project owner,
   2026-11-11, ratified), and Blender's window never scrolls; each editor
   scrolls its own regions (`docs/interface-provenance.md`). The prototype
   kept the page fixed: where the window could not hold every View whole,
   the Parameters View and then the chart gave up their whole height and
   scrolled inside their own Areas, each given the most height that still let
   every Area show its View, and the Bookmarks View's least height came down
   to 80 px. The page then never scrolled, in either font. But Induction's
   plot showed only its top 50 px, the wash-in plot its top 30 px, and in
   Default the Parameters Area cut through Run 1's sliders. A reader then has
   to scroll three small Areas to read what one page scroll shows whole, and
   the plot that `PL-CBYS` kept long is the part hidden. The page scroll keeps
   every View whole and asks for one scroll of less than a third of a screen.
   Nielsen Norman Group measured 74% of viewing time within the first two
   screenfuls of a page (Fessenden, "Scrolling and Attention", 2018, updated 2019,
   https://www.nngroup.com/articles/scrolling-and-attention/, read 2026-11-23,
   full text), so content one short scroll below the fold is still seen.
   Baymard Institute found that a scrolling region inside a scrolling page
   hides content and hijacks the wheel (Holst, "Avoid Inline Scroll Areas",
   2014, https://baymard.com/blog/inline-scroll-areas, read 2026-11-23, full
   text);
   the Bookmarks View still scrolls inside the scrolling page here, which is
   the one cost the page scroll keeps.
4. **So the page scroll stays the fallback at this size,** as
   `docs/INTERFACE.md` § "Values that must stay reachable" already states:
   the page grows past the window only where the window is too small for every
   View's least height. The related one-run case from `PL-S6CP`, an advisory
   above the plot, is the same fallback for the same reason. Files checked
   for statements this changes: `docs/INTERFACE.md` (§ "Values that must stay
   reachable", § "The disclaimer line and the unconditional region are always
   in view"), `src/anesthesia_sim/data/workspaces/__init__.py`,
   `src/anesthesia_sim/app/view_registry.py`'s comments on the least heights.
   None needed a change.
