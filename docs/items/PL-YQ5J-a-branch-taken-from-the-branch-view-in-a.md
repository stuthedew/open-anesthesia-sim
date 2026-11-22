---
id: PL-YQ5J
title: A branch taken from the Branch View in a Workspace pinned to a run that is not open opens a comparison that no Area of that Workspace draws, and nothing on screen says where it went
priority: P2
status: done
classes: defect
feature: window-is-the-frame
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/dashboard_frame.py, tests/integration/test_workspace_tabs.py, tests/integration/test_interface_wording.py, tests/integration/approved_interface_strings.json, tests/integration/simulation_view/test_simulation_view_halt.py, docs/INTERFACE.md
deferred-from: v0.7.0 - a new problem, not present at the freeze (817a4d88, 2026-10-25): the Branch View became usable in a Workspace pinned to a run that is not open in #2231, built 2026-11-22; not live: checked 2026-11-22, #2231 has not merged
added: 2026-11-22
closed: 2026-11-22
pr: 2239
tests: tests/integration/test_workspace_tabs.py::test_a_branch_taken_in_a_workspace_pinned_to_a_run_that_is_not_open_says_where_it_went, tests/integration/test_workspace_tabs.py::test_a_branch_taken_in_a_workspace_pinned_to_the_trunk_says_so_until_it_is_unpinned
---

**Problem.** A branch taken from the Branch View in a Workspace pinned to a run that is not open opens a comparison that no Area of that Workspace draws, and nothing on screen says where it went

**Found 2026-11-22** by a blind review of `#2231`, the fourth pull request of `PL-RF2S`. That pull request fixed `PL-1D3Z`: a Workspace pinned to a run that is not open now still shows the Bookmarks View and the Branch View, so the Branch View's "Branch" and "Branch here" buttons are live there. Before it, the pin's notice covered the Branch View, and no branch could be taken from such a Workspace.

**What goes wrong.** A learner pins a Workspace to Run 2, then closes Run 2, and presses "Branch" or "Branch here" in that Workspace. The new branch opens as Run 3. The Workspace is still pinned to Run 2, so every Area that shows a run's values keeps saying "Run 2 is not open." `SimulationView._show_branch` then scrolls to `_chart_in_view()`, which is the plot of a `ConcentrationView` hidden under that notice. The comparison the learner branched to see is drawn in no Area of that Workspace, and nothing on screen says where it went.

**Why it matters.** The learner's action succeeds, but its result is out of sight, and the screen still states that the pinned run is not open. A learner can take the silence for a refused branch and branch again, or lose track of which runs exist.

**Decided 2026-11-22: route 1, the learner stays and is told** (session, on
best practice, under the owner's instruction of 2026-11-22 to research best
practice for every item that needs him and to ask only clinician calls; chosen
over switching the Workspace for the learner). Three sources were read in full
on 2026-11-22 through their own pages:

- WCAG 2.1 Understanding document for Success Criterion 3.2.2, On Input
  (https://www.w3.org/WAI/WCAG21/Understanding/on-input): "Changes of context
  are appropriate only when it is clear that such a change will happen in
  response to the user's action." A change of context includes a change of
  focus or "content that changes the meaning of the web page". Pressing
  "Branch" asks for a branch and does not make clear that the Workspace will
  change, so route 2 would be an unannounced change of context.
- WCAG 2.1 Understanding document for Success Criterion 4.1.3, Status Messages
  (https://www.w3.org/WAI/WCAG21/Understanding/status-messages): a status
  message is a "change in content that is not a change of context" that
  "provides information to the user on the success or results of an action".
  Its intent is to "make users aware of important changes in content that are
  not given focus, and to do so in a way that doesn't unnecessarily interrupt
  their work." That is route 1.
- Nielsen Norman Group, "Visibility of System Status"
  (https://www.nngroup.com/articles/visibility-system-status/): "Whenever users
  interact with a system, they need to know whether the interaction was
  successful."

**What was built.** The message is worked out from state, not set by the press,
so it can never be stale. `ComparedRuns` gains `pinned_away`, the run the
current Workspace is pinned to where that pin keeps the comparison off its
Views. `comparing_fork_lock_text`, the caption the Branch View shows in place of
the control at once after any branch, then adds
`COMPARISON_PINNED_AWAY_TEMPLATE`: "This Workspace is pinned to Run 2, so it
does not draw this comparison. Unpin it from the Workspace's tab to compare
Run 1 and Run 3." The wording is a placeholder, as `PL-2KXB` decides for the
pin's other text. The page now keeps that Branch View in view
(`SimulationView._kept_in_view`, renamed from `_chart_in_view`) rather than
scrolling to a chart hidden under the pin's notice.

**Generator check.** One instance, with the trunk-pinned case below as its
second form of the same fault. The cause is that the branch control and the
Views that draw its result live in separate Areas, and nothing related the pin
to the comparison. `ComparedRuns.pinned_away` is now that one record, read by
the caption and by the scroll, so no generator is left to fix.

**Found while fixing it, and fixed here.** A Workspace pinned to the trunk,
which is open, has the same fault: its Views draw the trunk alone, so a branch
taken there is drawn nowhere in it. `pinned_away` covers both, and the second
test holds it.

**Regression tests**, both failing on the code before the fix with
`assert False` at the caption check (`git stash` of `src/`, then
`QT_QPA_PLATFORM=offscreen uv run pytest -q tests/integration/test_workspace_tabs.py -k branch_taken`):
`test_a_branch_taken_in_a_workspace_pinned_to_a_run_that_is_not_open_says_where_it_went`
and `test_a_branch_taken_in_a_workspace_pinned_to_the_trunk_says_so_until_it_is_unpinned`.
`tests/integration/test_interface_wording.py` records the new caption at the
event point "branched in a pinned Workspace".

**Documents checked:** `docs/INTERFACE.md` § on the pin (a paragraph added),
`docs/ARCHITECTURE.md` "One comparison at a time" (still true),
`src/anesthesia_sim/app/simulation_view.py`'s module docstring (still true).
