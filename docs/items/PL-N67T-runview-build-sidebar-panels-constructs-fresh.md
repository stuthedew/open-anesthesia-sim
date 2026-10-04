---
id: PL-N67T
title: RunView.build_sidebar_panels constructs fresh panels on every call and reparents the run's live labels into them, so a second call silently strips the accounting and control-change panels out of the sidebar
priority: P2
effort: S
status: done
classes: defect
feature: sidebar-panel-rebuild
touches: src/anesthesia_sim/app/run_view.py, tests/integration/test_simulation_view.py, docs/items/PL-KZR1-runview-s-build-methods-are-split-between.md, src/anesthesia_sim/app/theme.py, tools/literal_home_check.py
added: 2026-09-21
closed: 2026-10-04
pr: 1336
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

**Built (2026-10-04): the panels are handed back.** `.claude/rules/ui-areas.md`
answers the fork: a view is to be lifted into areas a reader splits, resizes,
closes or replaces, so a layout being rearranged will ask a run for its panels
again and put them somewhere else. Placing the same widget again moves it,
which is what that needs. A method that refused a second call would refuse the
move, and one that built new panels strips the old ones, as this item found.
So `RunView.__init__` lays the two panels out once, through
`_lay_out_sidebar_panels`, and `build_sidebar_panels` returns them. The
overflow label loses the `setParent(self)` that kept it from opening a window
of its own before its panel existed: it sits in the panel from construction.

`test_a_second_build_sidebar_panels_leaves_the_run_labels_on_screen` makes the
second call. It holds every sidebar label to being shown and inside the shared
column before the call and after it, and the two panels handed back to being
the two placed. On the old method it failed at the first label, "a second call
took a run label off screen"; on the new one it passes. Two test docstrings
that described the old method in the present tense now use the past.

Moving the layout code took its bare `4`, the control-change panel's row
spacing, into a scope `tools/literal_home_check.py` had no baseline entry for,
and that baseline only shrinks. So the spacing is named instead,
`CONTROL_TIMELINE_ROW_SPACING` in `app/theme.py`, and the stale entry is
deleted: 43 bare literals now, from 44. Both files are declared in `touches`.

**What measuring added (2026-10-04, against a shown `SimulationView` over one
run).** A second call whose result was dropped did more than strip the labels.
The orphan panels were Python-owned, so garbage collection deleted them and
the run's live labels with them, and any later write to one raises
`RuntimeError`: `_agent_accounting_status_text` read as deleted. Now the panels
are the run's own, and kept or dropped, the label stays on screen.

The other three `build_*` methods that lay the run's live widgets into a new
container on every call, `build_transport_row`, `build_readout_section` and
`build_parameter_controls`, do the same. With the second result kept, the
Start button, the substance heading and the fresh gas flow slider each went
off screen; with it dropped, each was deleted. That is `PL-KZR1`'s to fix, and
this commit rewrote its brief to say so. It also set that item `ready` and
raised it to `P2`, the band this item held for the same defect.
