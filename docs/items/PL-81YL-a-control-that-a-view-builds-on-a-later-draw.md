---
id: PL-81YL
title: A control that a View builds on a later draw, such as a run's dials built again after a halt in which they could not be built, is reached by Tab only after every Area and border, because nothing sets Tab's order again after that draw
priority: P3
effort: S
status: done
classes: defect, ux
feature: interface-design-review
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/views.py, tests/integration/test_layout_keyboard.py
deferred-from: v0.7.0 - captured after the freeze; keyboard order on a halt path only, and no displayed value is wrong
added: 2026-11-22
closed: 2026-11-22
pr: 2239
payoff: a control a View builds later still takes its place in Tab's reading order
tests: tests/integration/test_layout_keyboard.py::test_dials_built_again_after_a_halt_follow_the_parameters_chooser
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

**A second defect on the same path (2026-11-22).** Building the test found a
worse fault than the one this item names. `RunDials.show_dials` took the old
dials out of the row with `setParent(None)` before `deleteLater`. A widget
with no parent is a window of its own, and after the halt Qt showed that
window: once the event loop had run, `QApplication.topLevelWidgets()` held a
visible `ParameterControls` beside the dashboard, and it was the active window.
Tab then moved only among its four dials, which WCAG 2.2 Success Criterion
2.1.2, No Keyboard Trap, forbids. Once Qt deleted it, the keyboard focus was
lost altogether, and `QApplication.focusWidget()` returned `None`. What showed
it was not found: a Python override of `setVisible` on `ParameterControls` saw
no call. A layout rebuild through `AreaLayout.choose_view`, which takes widgets
out the same way in `area_layout.py`, left no stray window when probed, so the
other `setParent(None)` sites were left as they are.

**What was built.**

1. `RunDials.show_dials` now hides the old dials and leaves them in the row
   until Qt deletes them, so they never become a window.
2. `SimulationView._order_focus_if_owed` also sets Tab's order again when a
   focusable widget lacks a mark that `_order_focus` sets on every widget it
   places. The mark is a Qt property, so it belongs to the object and a widget
   built since never carries it. This reads the widgets themselves, as "What
   to do" asked, rather than a flag that each change must remember to set.
   `PL-2D9Z` is settled first: its crash was a fault in PySide6 6.11, and the
   upgrade to 6.12.0 removes it.
3. The cost, measured on 2026-11-22 with the shipped Default Workspace and one
   run: listing the 396 widgets and reading the mark took 0.81 ms per draw,
   against 3.8 ms for a whole draw. The dashboard draws every 0.2 s
   (`RENDER_INTERVAL_S`), so the check costs about 4 ms of each second.

**Regression test.**
`tests/integration/test_layout_keyboard.py::test_dials_built_again_after_a_halt_follow_the_parameters_chooser`
halts the run so that its dials cannot be built, checks that no window but the
dashboard is shown, builds the dials again, and walks Tab from the Parameters
chooser. A fresh dashboard reaches the Area's scroll box and then the four dials
from top to bottom, and so must this one. Before each fix, with
`QT_QPA_PLATFORM=offscreen uv run pytest -q tests/integration/test_layout_keyboard.py -k dials_built_again`:

1. Without the change to `show_dials`, it failed at the check for other
   windows, `assert [<...>] == [<...>]`: a second window was visible.
   Without that check, it failed with `assert None is not None` at the first
   Tab, because the focus had gone.
2. Without the order check, it failed at `assert stops[2:6] == sorted(dials, ...)`,
   because Tab reached the dials only after every Area and border.

**Generator check.** One instance of each. The order fault came from a flag
that was a second record of which widgets the dashboard holds; the check now
reads the widgets. The stray window came from one removal in `views.py`; the
one other removal on a layout change was probed and left no window.

**Documents checked.** `docs/INTERFACE.md` § "Color contrast, and the
standard this interface is held to" says every layout operation can be done
from the keyboard and that keyboard operation of the rest is planned. It states
no Tab order, so it needs no change. `docs/ARCHITECTURE.md`, `README.md` and
`docs/VERIFICATION.md` say nothing about Tab's order.
