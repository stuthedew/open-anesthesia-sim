---
id: PL-1D3Z
title: A Workspace pinned to a run that is no longer open hides the Bookmarks and Branch Views behind the pin's notice, though both belong to the case and show no single run; and while the pinned run is open their Area headers read that run's name (AreaFrame.show_pin, SimulationView._refresh_view's PinnedRunAbsent path). On main both panels stayed on screen in that state.
priority: P2
effort: M
status: ready
classes: defect, ux
feature: window-is-the-frame
touches: src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/view_contract.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/views.py
deferred-from: v0.7.0 - found after the gate's list was frozen, and it shows only in a Workspace pinned to a run that has closed
added: 2026-11-11
payoff: a learner who pinned a Workspace to a branch keeps the case's marks and branch control on screen after closing that branch
verify: grep -rq 'def test_the_case_views_stay_on_screen_in_a_workspace_pinned_to_a_closed_run' tests/integration/simulation_view/
---

**Problem.** A Workspace pinned to a run that is no longer open hides the Bookmarks and Branch Views behind the pin's notice, though both belong to the case and show no single run; and while the pinned run is open their Area headers read that run's name (AreaFrame.show_pin, SimulationView._refresh_view's PinnedRunAbsent path). On main both panels stayed on screen in that state.

**Why it matters.** The marks and the branch points belong to the case. A
learner who pinned a Workspace to a branch and then closed that branch loses
both lists from that Workspace until they unpin it, though nothing in either
list came from the closed run. Before `PL-9YPR` both panels sat below the
Areas and stayed on screen in that state.

**Done when.** A Bookmarks View and a Branch View in a pinned Workspace show
the case's marks and branch control whether or not the pinned run is open,
and their Area headers do not name the pinned run. A test builds that state
and checks both. Fixing it needs a View to say whether it shows one run or
the case, which is a change to the View contract.

**Generator check.** A one-off. `PL-9YPR` moved two case panels into Views,
and the pin was written when every View showed one run. No reader misread a
fact.
