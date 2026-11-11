---
id: PL-9YPR
title: The marks panel and the branch control sit under the Areas as fixed page sections (SimulationView._build_case_section, which calls their place a placeholder), not as Views, against the owner's 2026-09-16 rule that every main UI element is a View an Area can hold; they add their height to every Workspace and no Workspace can move or close them
priority: P2
effort: M
status: untriaged
classes: feature
feature: window-is-the-frame
touches: src/anesthesia_sim/app/views.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/view_contract.py, src/anesthesia_sim/app/view_registry.py, src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/data/workspaces/default.json, tests/integration/test_simulation_view.py
added: 2026-11-11
payoff: a learner can put the bookmarks and the branch control in any Area, or leave them out, and no fixed section under the Areas adds to the page's height
verify: grep -q 'def test_the_selected_branch_point_survives_the_branch_view_being_rebuilt' tests/integration/test_simulation_view.py
---

**Problem.** The marks panel and the branch control sit under the Areas as fixed page sections (SimulationView._build_case_section, which calls their place a placeholder), not as Views, against the owner's 2026-09-16 rule that every main UI element is a View an Area can hold; they add their height to every Workspace and no Workspace can move or close them

**Why it matters.** A learner on a laptop scrolls past the Areas to reach
the bookmarks and the branch control, and no Workspace can move, resize or
leave out either of them. They are the last two main elements that are not
Views, so the page cannot stop scrolling (`PL-CBYS`) while they stay under
the Areas.

**Done when.** The bookmarks and the branch control are Views that every
Area's chooser offers. Nothing sits between the Areas and the disclaimer.
The three shipped Workspaces show both Views. A test shows each View in three
Areas at once and checks that every copy follows the case.

**Generator check.** A one-off. `SimulationView._build_case_section` recorded
its own place as a placeholder when v0.6.0 built the Areas, and this item
finishes that work. No reader misread a fact.

**Progress, 2026-11-11: built, tested and swept. The reviews and the pull
request's text are left.**

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
- The dashboard keeps one selected branch point for the case, and every copy
  of the branch control shows it (`dashboard_frame.kept_fork_selection`). The
  first design, a selection in each copy, was replaced after review finding 1
  below.
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
  length then names Reset alone (review finding 2 below). Whether the banner
  should say where to find the branch View is left for the interface pass.

**Release note.** A layout saved before this change shows neither View until
the reader chooses one in an Area or uses "Reset this Workspace".

Still to do before this item closes:

0. Done, 2026-11-11. The eight tests that pinned the shipped Workspaces' old
   shape now expect the new one. Two things they showed:
   - In Default the chart's Area can no longer be closed. It sits beside a
     column of three Areas, so no single neighbour shares its whole edge, and
     its Close Area entry is unavailable. The same was already true of the
     Parameters Area in Induction. The layout-safety tests close the
     bookmarks' Area instead. A placeholder: whether Close Area should give
     the room to a whole column is left for the interface pass.
   - A dashboard built with no case builds no branch control, so two
     dark-appearance tests had stopped reaching the branch point's selector.
     Both now build the dashboard with a case, as `main` does.
1. Done, 2026-11-11: this item is triaged.
2. Done, 2026-11-11: the claimed group is triaged. `PL-CBYS` is now step 2,
   the build, and opens with the mock-up for the owner. `PL-4JCC` waits for
   it. `PL-5XVQ` holds two document edits. `PL-QKDV` is done and `PL-PKLR`
   dropped. `PL-62PF` is ready in the workflow lane.
3. Close out: the prose review and its trailer, two blind review passes, the
   owner's read and its trailer, the pull request's title and body through
   the copy editor, then mark `#2103` ready and arm it only when
   `bin/docket arm` says so.

**Review findings to act on before close-out, 2026-11-11.** Both blind review
passes ran on commit `c996a328e`. Their findings, with what is decided so far:

1. Both passes, should-fix, real: a branch View's selected instant lives only
   in that copy's `ForkPanel`, and `BranchView.save_state` saves only the
   version. A Workspace switch, or choosing another View and then Branch again,
   builds a new copy whose first fill selects induction at 0 s, so the next
   press of Branch opens the branch there. To fix: save the selected point in
   the View's state, restore it only where the offer still holds it, and leave
   nothing selected otherwise (`ForkPanel.set_offer`'s rule, `PL-J12Z`). Add
   the regression test.
2. Both passes, should-fix, real: `RunView._branch_offered` is true whenever
   the dashboard holds a case (`SimulationView._place_run` passes
   `branch_control=self._case is not None`), so a run stopped at the supported
   length tells the learner to branch while no Area shows the Branch View. To
   fix: offer the branch in the banner only while a branch control is on
   screen, and update `docs/MODEL.md`'s sentence if its wording changes.
3. Pass 2, should-fix, rejected: layouts saved before this change show
   neither new View. Not migrated: adding Areas to a layout a reader arranged
   changes what they saved, both Views are in every Area's chooser, and
   "Reset this Workspace" restores the shipped arrangement. The owner is told
   in the reply, because a layout saved on the owner's machine is the one
   known case.
4. Pass 1, optional, not yet checked: a bookmarks or branch View chosen while
   every frame fails gets no tick, so it stays empty (`_CasePanelView.refresh`
   builds its copy on the first tick).
5. Pass 1, optional, not yet checked: one refusal ("Select an instant to
   branch at") is written into every copy of the branch control, including a
   copy that shows an instant selected (`SimulationView._show_fork_offer`).

Still running when this was written: three focused review passes (lifecycle
and state; what a learner sees; tests and dead code), whose reports arrive as
messages, and the copy edit of the branch's 70 changed passages, whose output
is `copy.txt` in the session's scratchpad. `PL-5XVQ` (Maximize Area's two
document entries) closed on this branch, so its two paragraphs need the copy
editor too.

**The focused pass on what a learner sees, 2026-11-11.** It reproduced
findings 1, 2 and 4 above with scripts, and added three. Its scripts and
pictures are under `review-b/` in the session's scratchpad.

6. Not yet checked, likely real: a refused branch writes its reason
   (`ForkPanel.notice`, the panel's last row) below the fold. At 1366 by 768
   in Default the reason is off the page, and in Maintenance it is below the
   View's own scroll, while the Branch button stays in view. Step 2
   (`PL-CBYS`) changes the room each Area has, so decide there or here
   whether the reason moves beside the button.
7. Not yet checked: in a Workspace pinned to a run that is no longer open,
   the Bookmarks and Branch Areas show the pin's notice instead of their
   Views, though both belong to the case and show no single run
   (`AreaFrame.show_pin`). While the pinned run is open, their headers read
   that run's name.
8. Not yet checked: the Branch View's declared minimum width (220 px in
   `view_registry.py`) is less than its control row needs (about 308 px), so
   at the narrowest Area a border drag reaches the Branch button is out of
   sight behind a sideways scroll.

**Findings 1, 2 and 5 fixed, 2026-11-11.** The selected branch point is now
one value that the dashboard keeps for the case
(`dashboard_frame.kept_fork_selection`), and every copy of the control shows
it. A per-copy selection, the first design, was refuted by finding 1: it died
with its copy. Saving it in the View's state was weighed and refused, because
a Workspace file outlives the case and would restore an instant of a case
that no longer exists. With one selection, no copy can show an instant beside
a refusal that says none is selected, which was finding 5. The banner of a
run stopped at the supported length names a branch only while a branch
control is on screen (`SimulationView._branch_control_shown`). Four tests
were added and each fails against the code without the fixes. The test
`test_each_branch_view_keeps_its_own_point...` is gone with the design it
checked, so the item's `verify:` now names
`test_the_selected_branch_point_survives_the_branch_view_being_rebuilt`.
Findings 4, 6, 7 and 8 are still to check.

**The other findings, 2026-11-11.** Finding 6 is fixed: the refusal's reason
is now the row directly under the selector and above "Branch here", with a
test of that order. Finding 7 is `PL-1D3Z` (a pinned Workspace whose run is
gone hides both case Views) and finding 4 is `PL-G3N1` (a View built after a
failing halt stays blank). Both need a change to what a View is told, which
is more than a fix on this branch. Finding 8, the branch View's declared
minimum width, is recorded in `PL-CBYS`, which sets the room each Area gets.

**The tests-and-dead-code pass, 2026-11-11.** It mutated the change in a
scratch copy and reported eight findings. One is fixed here: commit
`44939bde6` handed `RunView` the method `_branch_control_shown` without the
halt gate, and the test that every handed-out callback passes the gate failed
on it. The method returns whether an Area shows a branch control and reads no
run, so it is now on that test's list of callbacks that need no gate, with
that reason. The seven still to act on before close-out:

1. `_CasePanelView`'s no-case sentence can be shown beside a working branch
   control and no test fails. The test of the shipped dashboard over a case
   must also check that the sentence is hidden. The loose-runs test takes its
   expected words from the constant under test.
2. `_branch_control_shown` reduced to "a copy exists" passes every test. A
   copy that exists and is not drawn needs a test.
3. The titles and minimum sizes of the `BOOKMARKS` and `BRANCH` registry
   entries are not pinned by a test.
4. Nothing tests that a bookmarks copy built between frames shows the marks
   listed now. The branch control has that test.
5. `clear_scroll_area_stylesheet` changes no pixel under the declared
   palette. Give it a test of what it prevents, or remove it.
6. `test_the_bookmark_panel_sits_outside_the_region_between_the_two_plots`
   can no longer fail on what its name says.
7. `SimulationView._build_page` keeps a `middle_column` wrapper that now
   holds one widget.

The reviewer's scripts and logs are under `review-c/` in the session's
scratchpad.

**All seven acted on, 2026-11-11.** Findings 1, 2, 3, 4 and 6 are test
changes in `tests/integration/test_simulation_view.py`. Finding 2's test
hides the Branch View to reach a control that exists and is not drawn, the
state `PL-1D3Z` describes. Finding 5: `clear_scroll_area_stylesheet` is
removed, because under the palette the application declares the scroll area
already paints the panel colour. Finding 7: the tab strip and the Areas now
sit directly in the scrolling part of the page.

**The mutation check, 2026-11-11.** Seven mutants of the changed functions,
all caught by the unit tests, none surviving. It ran in a scratch copy with
`PL-GP8G`'s fix to the mutation run applied there only, because without that
fix the run stops before its first mutant. A fix of this session's to the
same line was withdrawn when `PL-GP8G` turned up on another branch. Not
mutated: seven changed module-level lines of `app/dashboard_frame.py`.
