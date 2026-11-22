---
id: PL-YQ5J
title: A branch taken from the Branch View in a Workspace pinned to a run that is not open opens a comparison that no Area of that Workspace draws, and nothing on screen says where it went
priority: P2
status: untriaged
classes: defect
feature: window-is-the-frame
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/views.py, src/anesthesia_sim/app/qt_widgets.py
deferred-from: v0.7.0 - a new problem, not present at the freeze (817a4d88, 2026-10-25): the Branch View became usable in a Workspace pinned to a run that is not open in #2231, built 2026-11-22; not live: checked 2026-11-22, #2231 has not merged
added: 2026-11-22
---

**Problem.** A branch taken from the Branch View in a Workspace pinned to a run that is not open opens a comparison that no Area of that Workspace draws, and nothing on screen says where it went

**Found 2026-11-22** by a blind review of `#2231`, the fourth pull request of `PL-RF2S`. That pull request fixed `PL-1D3Z`: a Workspace pinned to a run that is not open now still shows the Bookmarks View and the Branch View, so the Branch View's "Branch" and "Branch here" buttons are live there. Before it, the pin's notice covered the Branch View, and no branch could be taken from such a Workspace.

**What goes wrong.** A learner pins a Workspace to Run 2, then closes Run 2, and presses "Branch" or "Branch here" in that Workspace. The new branch opens as Run 3. The Workspace is still pinned to Run 2, so every Area that shows a run's values keeps saying "Run 2 is not open." `SimulationView._show_branch` then scrolls to `_chart_in_view()`, which is the plot of a `ConcentrationView` hidden under that notice. The comparison the learner branched to see is drawn in no Area of that Workspace, and nothing on screen says where it went.

**Why it matters.** The learner's action succeeds, but its result is out of sight, and the screen still states that the pinned run is not open. A learner can take the silence for a refused branch and branch again, or lose track of which runs exist.

**Open choice, which a learner would see.** Two routes reach the same end, and the choice between them changes what the learner sees, so it is the owner's:

1. Name the outcome in the control's own text while the Workspace is pinned to a run that is not open, for example that the branch opens in another Workspace. The learner stays where they are and is told where the comparison goes.
2. Take the learner to a Workspace that shows both runs once the branch opens, such as an unpinned Workspace. The comparison is on screen at once, at the cost of changing the Workspace under the learner.

**Done when.** After a branch is taken from a Workspace pinned to a run that is not open, the learner either sees the comparison or reads on screen where it is. A test builds that state, takes the branch and checks the chosen outcome.
