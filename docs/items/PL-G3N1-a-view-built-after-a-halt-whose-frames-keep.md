---
id: PL-G3N1
title: A View built after a halt whose frames keep failing gets no tick, so a Bookmarks or Branch View chosen then stays blank with no words, where the fixed panels on main showed the restated marks (_CasePanelView.refresh builds its copy on the first tick; SimulationView._refresh_view never reaches AreaLayout.refresh on a failed frame)
priority: P3
effort: S
status: ready
classes: defect, ux
feature: window-is-the-frame
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/views.py
deferred-from: v0.7.0 - found after the gate's list was frozen, and it shows only when a View is chosen after a simulation error
added: 2026-11-11
payoff: a learner who opens the bookmarks or the branch control after a simulation error reads why the lists are withdrawn
verify: grep -q 'def test_a_case_view_chosen_after_a_failing_halt_shows_the_halted_words' tests/integration/test_simulation_view.py
---

**Problem.** A View built after a halt whose frames keep failing gets no tick, so a Bookmarks or Branch View chosen then stays blank with no words, where the fixed panels on main showed the restated marks (_CasePanelView.refresh builds its copy on the first tick; SimulationView._refresh_view never reaches AreaLayout.refresh on a failed frame)

**Why it matters.** After a simulation error the dashboard withdraws values
it can no longer stand behind and says so. A Bookmarks or Branch View that a
learner chooses in that state shows an empty rectangle with no explanation,
so the learner cannot tell a withdrawn list from an empty one.

**Done when.** A Bookmarks or Branch View chosen while every frame is failing
shows the halted state's words, as a copy that was on screen at the halt
does. A test chooses each View after a failing halt and checks its text.

**Generator check.** A one-off. `PL-9YPR` made the two case panels build on
their View's first tick, and a failing frame sends no tick. No reader misread
a fact.
