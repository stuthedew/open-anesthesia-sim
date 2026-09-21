---
id: PL-N67T
title: RunView.build_sidebar_panels constructs fresh panels on every call and reparents the run's live labels into them, so a second call silently strips the accounting and control-change panels out of the sidebar
priority: P2
effort: S
status: ready
classes: defect
feature: sidebar-panel-rebuild
touches: src/anesthesia_sim/app/run_view.py, tests/integration/test_simulation_view.py
added: 2026-09-21
payoff: calling build_sidebar_panels twice stops emptying the sidebar a learner is looking at
verify: grep -q 'def test_a_second_build_sidebar_panels_leaves_the_run_labels_on_screen' tests/integration/test_simulation_view.py
---

**Problem.** RunView.build_sidebar_panels constructs fresh panels on every call and reparents the run's live labels into them, so a second call silently strips the accounting and control-change panels out of the sidebar

**Measured 2026-09-21** while implementing `PL-C3GS`, against a shown
`SimulationView` over one run. After a second `run.build_sidebar_panels()`:
`run._agent_accounting_status_text.parent()` is a different widget, the new
panel's own `parent()` is `None`, `view.isAncestorOf(panel)` is `False`, and
`run._agent_accounting_status_text.isVisible()` is `False`. So the call does
not merely waste two frames - it moves the run's live labels into an orphan
and leaves the sidebar on screen empty of them.

**Why it matters.** The method reads as a getter and every other `build_*`
call site treats it as one. `SimulationView._place_run` calls it once, so the
running application is unaffected today; what it costs is a caller who cannot
see from the name that calling it twice dismantles the display, which is how
`PL-JS0X`'s vacuous assertions arrived.

**Fix, not yet decided.** Either return the panels built at construction, or
raise on a second call. The first makes the name honest; the second makes the
misuse loud. Both are cheap; which is right depends on whether a panel is ever
meant to be rebuilt for a relaid-out area (`.claude/rules/ui-areas.md`).

**Done when.** A second `build_sidebar_panels()` leaves the run's accounting and
control-change labels on screen and parented into the view - whether by handing
back the panels built at construction or by refusing the call - and a test in
`tests/integration/test_simulation_view.py` makes the second call and asserts
the labels are still shown.

**The fork above is the implementing session's to settle**, not a question to
carry back. Both answers are defensible, both are cheap, and the blast radius is
one class's internal contract. `.claude/rules/ui-areas.md` decides it on a read
rather than a preference: whether an area is ever relaid out is a fact about the
design, and the answer to that names which of the two is right.
