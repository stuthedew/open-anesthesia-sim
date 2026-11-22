---
id: PL-81YL
title: A control that a View builds on a later draw, such as a run's dials built again after a halt in which they could not be built, is reached by Tab only after every Area and border, because nothing sets Tab's order again after that draw
priority: P3
effort: S
status: ready
classes: defect, ux
feature: interface-design-review
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_layout_keyboard.py
deferred-from: v0.7.0 - captured after the freeze; keyboard order on a halt path only, and no displayed value is wrong
added: 2026-11-22
payoff: a control a View builds later still takes its place in Tab's reading order
---

**Problem.** `SimulationView` sets Tab's order again only after a draw that
follows a run being placed, a Workspace change or a View being replaced
(`_owe_focus_order`). A View that builds a control on any other draw gets no
new order, and Qt puts a newly built widget at the end of the window's focus
chain. So Tab reaches that control after every Area, every Area border and
the page's scroll area.

**How it shows today.** The independent review of `PL-B45W` reproduced it on
2026-11-22. When `run_presentation.setting_readouts` cannot build a run's
setting readouts, the run halts and `RunDials.show_dials` deletes its four
dials. The first later draw that can build them builds them again, and Tab
then reaches them after the Area borders. The docstring of `setting_readouts`
says no shipped agent or patient profile causes that failure, so a learner
meets this only on that halt path.

**Why it matters.** A later View that builds a control on a later draw would
meet the same gap without any test failing. The order would read wrong to a
keyboard user, which is what `PL-B45W` fixed (WCAG 2.2 Success Criterion
2.4.3, Focus Order, as cited there).

**What to do.** Set the order again whenever the set of focusable widgets
changes, read from the widgets rather than from a flag that each change must
remember to set. The review measured the cost on 2026-11-22 with every View
shown and two runs: listing the widgets with `findChildren` took 0.66 ms over
586 children, one reorder took 1.8 ms over 69 focusable widgets, and one
frame took 6 ms. Listing the widgets on every draw creates many short-lived
Python wrappers, which is the pattern `PL-2D9Z` suspects in its crash. So
settle `PL-2D9Z` first, or pick a cheaper signal, such as each View reporting
that it built a control.

**Generator check.** One instance today. The cause is that the flag which says Tab's order is stale is a second record of which widgets the dashboard holds, and only three changes set it. `PL-B45W`'s pin finding came from the widget tree's order, a different record, and is fixed there.

**Done when.** A test halts a run so that its dials cannot be built, builds
them again, and finds them directly after the Parameters Area's chooser.
