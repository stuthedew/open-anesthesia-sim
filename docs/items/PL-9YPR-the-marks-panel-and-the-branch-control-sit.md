---
id: PL-9YPR
title: The marks panel and the branch control sit under the Areas as fixed page sections (SimulationView._build_case_section, which calls their place a placeholder), not as Views, against the owner's 2026-09-16 rule that every main UI element is a View an Area can hold; they add their height to every Workspace and no Workspace can move or close them
status: untriaged
feature: window-is-the-frame
added: 2026-11-11
---

**Problem.** The marks panel and the branch control sit under the Areas as fixed page sections (SimulationView._build_case_section, which calls their place a placeholder), not as Views, against the owner's 2026-09-16 rule that every main UI element is a View an Area can hold; they add their height to every Workspace and no Workspace can move or close them

**Progress, 2026-11-11: built, with 15 tests still to move. The session stopped here for length, not for the work.**

What the branch holds (commit led by this id, pull request `#2103`, a draft):

- `app/view_contract.py` gains `CaseSurfaces` (`build_bookmarks_panel`,
  `build_branch_control`) and `ViewTick.case`. `SimulationView` satisfies it.
  It keeps a list of the live copies of each panel, writes every copy on each
  frame, and restates every copy on a halt. A new copy is written with what
  the others show (`_marks_shown`, `_fork_offer_shown`).
- `app/views.py` gains `BookmarksView` and `BranchView`, both built on
  `_CasePanelView`, which builds its copy on the View's first tick. Over a
  dashboard with no case, `BranchView` shows `NO_CASE_TO_BRANCH_TEXT` and no
  control.
- `app/view_registry.py` registers the tags `bookmarks` ("Bookmarks") and
  `branch` ("Branch"). Both declare a 220 by 120 px minimum, a placeholder.
- `SimulationView._build_case_section` and `_section_divider` are gone, with
  `theme.SECTION_DIVIDER_HEIGHT` and the colour exemption for the divider in
  `tools/contrast_check.py`. `docs/MODEL.md` § "Color contrast" now names the
  line under each Area's header in the divider's place.
- Each copy of the branch control keeps its own selection. A press opens the
  branch at the point selected in the copy that was pressed.
- The three shipped Workspaces show both Views. Default and Induction stack
  Parameters, Bookmarks and Branch in the right-hand column. Maintenance puts
  Bookmarks and Branch in a row under Parameters. The placement is a
  placeholder (`PL-4JCC` is the item about the Parameters Area's height).
- Measured offscreen at 1920 by 1080 with one run at 5 minutes: the Default
  Workspace no longer scrolls (the page scrolled 102 px before).

Still to do before this item closes:

1. Move the 15 tests that pin the old arrangement. Run
   `tests/integration/test_simulation_view.py`,
   `tests/integration/test_agent_cost_view.py`,
   `tests/integration/test_compartment_schematic_view.py`,
   `tests/integration/test_layout_keyboard.py`,
   `tests/unit/test_contrast_check.py` and `tests/unit/test_view_registry.py`
   to list them. Their causes:
   - `test_agent_cost_view.py` and `test_compartment_schematic_view.py` still
     read `view._fork_panel`. Give each the helper that
     `test_simulation_view.py` has (`_fork_panel(view)`), and a layout that
     shows the branch View.
   - `test_simulation_view.py`'s `_drag_area_border` expects one row
     splitter, and the test layout `_EVERY_VIEW` now has two.
   - `test_a_dashboard_over_loose_runs_offers_no_branch_control` needs
     `QPushButton` imported.
   - `test_the_bookmark_panel_sits_outside_the_region_between_the_two_plots`
     asserts the marks sit in no Area. Assert instead that they sit in no
     chart View.
   - The test near "splitting and closing the chart area leaves the
     unconditional values where they were" compares the page's strings and
     now also finds the bookmarks' strings.
   - `test_the_shipped_gridline_is_exempt_in_each_of_its_five_uses`: four
     uses now. `test_view_registry.py`: add the two tags, and the two kinds
     to the shipped Workspaces' expected set.
     `test_layout_keyboard.py`: the shipped Default Workspace has four Areas.
   - `test_a_wrapped_mark_row_is_never_clipped` fails for a real reason. An
     Area gives its View the widget's minimum size hint, which does not count
     the lines a wrapped label needs at the Area's width. So a long mark name
     is clipped in the Bookmarks Area (75 px needed, 15 px given at 700 px
     wide). **Decided (session, 2026-11-11):** the fix is step 2 of `PL-CBYS`,
     where a View that needs more height scrolls inside its Area. Until that
     lands, `_CasePanelView` holds its panel in a scroll area of its own, and
     step 2 moves that scroll to the container for every View.
2. Add tests for what is new: two bookmarks Views list the same marks; two
   branch Views each keep their own selection and a press branches at the
   pressed copy's point; a View built after a halt shows the restated state;
   `halt_restatements` covers every live copy.
3. Sweep the documents: `docs/ARCHITECTURE.md` (the map's line for
   `simulation_view.py`, § "Where new code belongs" on the branch control and
   the bookmarks, and the sentence about "the case section below the Areas"),
   `.claude/rules/ui-areas.md`, `docs/interface-provenance.md`, `README.md`.
4. A reader's saved layout from before this change shows neither View until
   they choose one in an Area or use "Reset this Workspace". Say so in the
   release note line.
5. Triage the rest of the claimed group: `PL-CBYS` (this item is its step 1;
   its step 2 needs a mock-up shown to the owner first), `PL-4JCC`, `PL-5XVQ`,
   `PL-QKDV` (drop `PL-PKLR`, correct one sentence in
   `docs/interface-provenance.md`) and `PL-62PF`.
