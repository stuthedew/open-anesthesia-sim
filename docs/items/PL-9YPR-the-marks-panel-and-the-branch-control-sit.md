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
