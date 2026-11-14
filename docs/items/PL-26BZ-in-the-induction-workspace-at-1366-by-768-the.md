---
id: PL-26BZ
title: In the Induction Workspace at 1366 by 768 the wash-in View is 271 px of content in a 146 px Area, so 'Modelled, not measured' and the F_A/F_I plot are never on screen together: with the View at its top the plot shows 8 of its 80 px, and scrolled to the plot the line is above the Area; decide whether the plot carries the words itself, such as in its axis title, or the wash-in Area gets room for its whole View
priority: P1
effort: M
status: done
classes: safety, ux
feature: window-is-the-frame
touches: src/anesthesia_sim/app/views.py, src/anesthesia_sim/app/qt_chart.py, src/anesthesia_sim/app/area_layout.py, tests/integration/simulation_view, docs/INTERFACE.md
deferred-from: v0.7.0 - the gate's frozen list does not name it; it is a defect of #2134's unmerged branch, and is built on its own branch from that head
added: 2026-11-14
closed: 2026-11-14
pr: 2157
payoff: a learner never sees the predicted wash-in curve without the words that say it is modelled
verify: grep -q 'def test_the_wash_in_curve_is_never_on_screen_without_modelled' tests/integration/simulation_view/test_simulation_view_page.py
---

**Problem.** In the Induction Workspace at 1366 by 768 the wash-in View is 271 px of content in a 146 px Area, so 'Modelled, not measured' and the F_A/F_I plot are never on screen together: with the View at its top the plot shows 8 of its 80 px, and scrolled to the plot the line is above the Area; decide whether the plot carries the words itself, such as in its axis title, or the wash-in Area gets room for its whole View

**Found by** the adversarial review of `PL-CBYS`'s pull request `#2134`, on
2026-11-14, reproduced offscreen. The project owner chose on 2026-11-11 that
Induction's charts stay stacked, and the second mock-up showed the wash-in
Area scrolling about 122 px inside itself at this size. `#2134` moved the
line out of the box that scrolls above the plot, which keeps it in view
wherever the View fits its Area. Where the View is taller than its Area, no
order of rows puts both on screen. The safety standard requires the words
beside the plot (`PL-F9TQ`), so whether a learner may see the plot without
them is the owner's decision.

**Triaged, 2026-11-14, at the coordinator's request, to be built on its own
branch from `#2134`'s head.** Classed `safety`, because the standard requires
a modelled value to be told apart from a measurement on screen, and the
wash-in curve is a prediction.

**Done when.** "Modelled, not measured" is on screen whenever any part of the
wash-in curve is, in every shipped Workspace at 1366 by 768 and 1920 by 1080,
whatever the scroll position of the wash-in Area. A test scrolls the wash-in
View through its whole range at each size and fails if any part of the plot is
in view while the words are not.

**Why it matters.** A learner on a laptop who scrolls the wash-in Area to its
curve sees a predicted F_A/F_I trace with nothing beside it that says it is
modelled, which the safety standard names as a misleading display.

**Generator check.** A one-off: `#2134` let a View scroll inside its Area,
and this is the one required label that scrolling can separate from its plot.

**Closed, 2026-11-14, on `#2157`.** The wash-in View names "Modelled, not
measured" as its `pinned_row`, and its Area shows that row above the box that
scrolls the View. A new test scrolls the wash-in View through its whole range
in every shipped Workspace at 1366 by 768 and 1920 by 1080, and failed before
the fix at scroll 48 of 125 in Induction at 1366 by 768. The whole suite
passed: 12,521 tests, 3 skipped. The line now sits between the Area's header
and the View's heading, so the owner reads the change.
