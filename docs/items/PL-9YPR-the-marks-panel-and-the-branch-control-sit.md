---
id: PL-9YPR
title: The marks panel and the branch control sit under the Areas as fixed page sections (SimulationView._build_case_section, which calls their place a placeholder), not as Views, against the owner's 2026-09-16 rule that every main UI element is a View an Area can hold; they add their height to every Workspace and no Workspace can move or close them
status: untriaged
feature: window-is-the-frame
added: 2026-11-11
---

**Problem.** The marks panel and the branch control sit under the Areas as fixed page sections (SimulationView._build_case_section, which calls their place a placeholder), not as Views, against the owner's 2026-09-16 rule that every main UI element is a View an Area can hold; they add their height to every Workspace and no Workspace can move or close them

**Progress, 2026-11-11: built, tested and swept. Triage, the reviews and the pull request's text are left. The session stopped here for length, not for the work.**

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
- Each of the two Views holds its rows in a scroll area of its own
  (`_CasePanelView.scroll_area`), so a long mark name that wraps is not
  clipped in a short Area. Step 2 of `PL-CBYS` moves that scroll into the
  container for every View.
- The 15 tests that pinned the old section now read the panels from the
  Views. Five new tests at the end of
  `tests/integration/test_simulation_view.py` show the kind in three Areas:
  every copy lists the case's marks, each branch control keeps its own point
  and a press branches at it, a failing frame withdraws the offer from every
  copy, a halt that cannot restate the marks hides them in every copy and in
  one built afterwards, and a copy built between frames shows the offer on
  screen. Each of six deliberate breaks to the writers in
  `app/simulation_view.py` failed at least one of the five (run 2026-11-11).
- Documents swept: `docs/ARCHITECTURE.md` (the map lines for
  `simulation_view.py`, `view_contract.py` and `views.py`; § "Where new code
  belongs"; the halt paragraph), `README.md` § "The window" (eight Views, and
  a line for each new one), `docs/MODEL.md` (one sentence on the banner at
  the supported run length), and the docstrings of `BookmarksPanel` and
  `ForkPanel`. `.claude/rules/ui-areas.md` and `docs/interface-provenance.md`
  name neither panel and needed no change.

**Placeholders decided by the session, 2026-11-11.**

- Where the two Views sit in each shipped Workspace, their titles
  ("Bookmarks", "Branch") and their 220 by 120 px minimum.
- A Workspace may leave the branch View out. The banner at the supported run
  length still names a branch as a way out when the case can take one,
  because every Area's View chooser offers the branch View. Whether the
  banner should say where to find it is left for the interface pass.

**Release note.** A layout saved before this change shows neither View until
the reader chooses one in an Area or uses "Reset this Workspace".

Still to do before this item closes:

0. Move eight more tests that pin the shipped Workspaces' old shape. The
   full check on commit `0eecaba84` ran 12,227 tests: 8 failed and 12,216
   passed (2026-11-11). Seven expect the shipped files as they were, and one
   still reads the removed attribute:
   - `tests/unit/test_layout_shipped.py`:
     `test_the_default_gives_the_chart_the_full_height_beside_the_parameter_controls`
     and `test_induction_shows_the_wash_in_chart` list each Workspace's kinds.
   - `tests/unit/test_layout_sizing.py`:
     `test_a_shipped_workspace_on_a_small_extent_names_its_too_small_areas_and_none_has_no_size`
     expects three Areas' sizes, and the file now has five.
   - `tests/integration/test_workspace_tabs.py`:
     `test_a_tab_switches_the_layout_and_leaves_the_run` lists the View
     classes shown.
   - `tests/integration/test_dark_appearance.py`:
     `test_a_selector_popup_draws_the_theme_rather_than_the_host_palette`
     counts four popups and finds three. Find out which selector it no longer
     reaches before changing the count, because the branch control's selector
     now sits in a scroll area.
   - `tests/integration/test_layout_safety.py`:
     `test_every_layout_operation_leaves_the_unconditional_set_on_screen` and
     `test_a_halted_run_keeps_its_halt_reason_on_screen` count three Areas
     after a split and find five.
     `test_a_branched_case_keeps_both_runs_drawn_and_named` reads
     `view._fork_panel`.

1. Triage this item: `**Why it matters.**`, `**Done when.**` and a
   `**Generator check.**` line in this brief, then priority, effort, classes,
   touches, `verify:` and `payoff:` with `bin/docket set`. A `verify:` that
   fits: `grep -q 'def test_each_branch_view_keeps_its_own_point' tests/integration/test_simulation_view.py`
   (it must be seen failing on `origin/main` first).
2. Triage the rest of the claimed group: `PL-CBYS` (this item is its step 1;
   its step 2 needs a mock-up at 1366 by 768 and 1920 by 1080, Induction
   Workspace in both, shown to the owner first), `PL-4JCC`, `PL-5XVQ`,
   `PL-QKDV` (drop `PL-PKLR`, correct one sentence in
   `docs/interface-provenance.md`) and `PL-62PF`.
3. Close out: the prose review and its trailer, two blind review passes, the
   owner's read and its trailer, the pull request's title and body through
   the copy editor, then mark `#2103` ready and arm it only when
   `bin/docket arm` says so.
