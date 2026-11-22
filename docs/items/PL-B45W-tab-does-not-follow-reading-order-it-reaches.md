---
id: PL-B45W
title: Tab does not follow reading order: it reaches the control-change record and the Workspace '+' button first, and the agent selector, Start, Reset, Playback and the four parameter dials only after every Area
priority: P2
effort: S
status: done
classes: defect, ux
feature: interface-design-review
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/workspace_tabs.py, src/anesthesia_sim/app/views.py, tests/integration/test_layout_keyboard.py, tests/integration/simulation_view/test_simulation_view_halt.py
deferred-from: v0.7.0 - captured after the freeze; keyboard order only, and no displayed value is wrong
added: 2026-11-22
closed: 2026-11-22
pr: 2219
payoff: a keyboard user reaches the run's controls first, then the Workspace tabs, then each Area with its own controls, and a new window starts on the agent selector
tests: tests/integration/test_layout_keyboard.py::test_a_new_window_starts_with_the_focus_on_the_first_run_s_agent_selector, tests/integration/test_layout_keyboard.py::test_tab_reaches_the_transport_then_the_tabs_then_each_area_in_reading_order, tests/integration/test_layout_keyboard.py::test_tab_keeps_reading_order_after_a_branch_and_after_a_pinned_run_is_unpinned
---

**Problem.** Tab does not follow reading order: it reaches the control-change record and the Workspace '+' button first, and the agent selector, Start, Reset, Playback and the four parameter dials only after every Area

**Go-ahead.** The design review that found this was approved by the project owner (project owner, 2026-11-22). It ran offscreen on `a7eb53f`, with screenshots of each Workspace and each View at 1366 by 768 and 1920 by 1080 in `/mnt/project-files/v0.7.0/design-review/`.

**What was measured.** Walking Qt's focus chain in the Default Workspace at
1366 by 768 gives this order: the control-change record's scroll area, the
page's scroll area, the Workspace "+" button, the three Workspace tabs, the
Concentrations Area (chooser, time base, the six trace check boxes, the plot),
the Parameters, Bookmarks and Branch choosers, three Area borders, then the
agent selector, Start, Reset and Playback, then the four parameter dials, Edit
bookmarks, and the Branch selector and button. The dials belong to the
Parameters Area but are reached about twenty stops after its chooser.

**Why it matters.** WCAG 2.2 Success Criterion 2.4.3, Focus Order (Level A),
says that "focusable components receive focus in an order that preserves
meaning and operability"
(https://github.com/w3c/wcag/blob/main/guidelines/sc/20/focus-order.html,
read 2026-11-22). A keyboard user who wants to start a run tabs past every
Area first, and a user who tabs to the Parameters Area does not reach its
dials next. The order comes from when each widget was built, not from
where it sits.

**What to do.** Set the chain each time the Areas are drawn: the
unconditional region from left to right (agent, Start, Pause, Reset,
Playback), the control-change record, the Workspace tabs and "+", then each
Area in reading order with its chooser followed by its View's own controls,
and the Area borders last. Blender gives no model for Tab here, so this
follows the platform's reading order.

**Done when.** A test walks the focus chain in each shipped Workspace and
finds the transport controls before any Area, and each View's controls
directly after its own chooser.

**What was built.** `SimulationView._order_focus` sets the order with
`QWidget.setTabOrder`: the run rows, the record of control changes, the
Workspace tabs and "+" (`WorkspaceTabs.focus_order`), then each Area in
reading order, its chooser first and its View's controls next
(`AreaLayout.focus_order`). The Area borders and the page's scroll area come
last. The order is set again after any draw that follows a change in which
widgets the dashboard holds: a run placed, a Workspace switched, or a View
replaced (`views_changed`). Each View builds its rows at its first draw, which
is why the order is set at the end of the draw rather than when the Areas are
built.

Two things the brief did not foresee.

1. Qt's `setTabOrder` ignores a pair whose first widget takes no focus, so the
   dashboard itself cannot head the order. Qt therefore still gave a new
   window's focus to the record of control changes. Qt's guide to keyboard
   focus says to call `setFocus` on the widget where focus should start
   (https://doc.qt.io/qt-6/focus.html, read 2026-11-22).
   `_focus_first_control` does that for the first run's first control, which
   is the agent selector. It runs at the dashboard's first show
   (`SimulationView.showEvent`), not while the dashboard is built, for the
   reason in the review paragraph below.
2. The first build listed the focusable widgets by walking Qt's focus chain
   with `nextInFocusChain`. With that walk on every draw,
   `test_every_layout_operation_is_reachable_from_the_keyboard` crashed with a
   segmentation fault several steps later, inside a pyqtgraph layout request.
   No single draw's walk caused it, and keeping every wrapper alive did not
   stop it. Listing the same widgets with `findChildren` does not crash, so the
   build uses that. The order within each part is then the widget tree's order,
   and the walk in the tests gives the same order as before. The crash itself
   is not explained, and `PL-2D9Z` records it.

**Independent review (2026-11-22).** One blind pass and two focused passes,
one on state and one on the tests, ran on the first version of this branch.
Three findings were real and are fixed here.

1. The app's own window did not start on the agent selector. `main()` builds
   the dashboard as a window of its own and then moves it into a
   `QMainWindow`, and Qt forgets the focus a widget was given when it moves to
   another window. The focus is now given at the first show, and the new-window
   test builds the window as `main()` does.
2. After the Workspace was pinned to Run 2 and unpinned, Tab reached Run 2's
   dials before Run 1's in the Parameters Area. Unpinning builds Run 1's dials
   again, and the widget tree holds a new widget after the older ones while the
   layout draws it in its old place. `_RunWidgets.follow` in
   `src/anesthesia_sim/app/views.py` now raises each run's widget in drawing
   order, which also puts the tree's children in that order (Qt's
   `QObject::children` documentation, https://doc.qt.io/qt-6/qobject.html#children,
   read 2026-11-22). A new test pins and unpins, and checks that Run 1's dials,
   which sit higher on screen, come first.
3. `findChildren` also returned the selectors' lists of choices, which are
   windows of their own. Qt refused each link into them with "QWidget::setTabOrder:
   'first' and 'second' must be in the same window". `_focusable_widgets` now
   leaves out widgets in another window.

A walk that ordered each widget's children by its layout was tried for the
second finding and dropped. It ended with "Internal C++ object (QScrollBar)
already deleted" while building the dashboard, and `PL-2D9Z` records that
beside the crash. The tests were also tightened: the run's controls and the
record of control changes are checked as an exact sequence, the Workspace tabs
and "+" as the stops between them and the first Area, and the Area borders as
coming after every stop inside an Area. A control that a View builds on a
later draw is still reached after the borders, which only a halt path reaches
today (`PL-81YL`). Two older focus losses that the review found, after a
rename and after a Split chosen with the keyboard, are `PL-24SN`.

**Docs sweep.** `docs/INTERFACE.md` § "Color contrast, and the standard this
interface is held to" still says that every layout operation can be done from
the keyboard and that keyboard operation of the rest of the interface is
planned, as `ROADMAP.md` planned item 20, and is not yet a commitment. That is
still true, so this fix adds no requirement there. `docs/ARCHITECTURE.md`'s
package map now says that `simulation_view.py` sets Tab's order and that
`area_layout.py`'s `focus_order` lists each Area's chooser and then its View's
controls. Its line for `workspace_tabs.py` is still true. The other lines that
`python3 tools/doc_check.py candidates --base origin/main` named, in
`ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/INTERFACE.md`,
`docs/interface-provenance.md`, `docs/WORKING_NOTES.md`, `docs/apparatus.md`,
`docs/mutation-testing.md` and `subprojects/docket/README.md`, name these
modules for other reasons, and none describes keyboard focus or Tab's order.

**Generator check.** One cause, one window. Qt orders Tab by when each widget
was built, and the dashboard builds its Areas before it places the runs and
builds each View's rows at its first draw. The two question dialogs build
their two buttons in the order they show them (`lay_out_question` in
`src/anesthesia_sim/app/qt_widgets.py`), so their build order is their reading
order. The bookmark editor's order already has a test
(`tests/integration/test_qt_widgets.py`). No other item shares the cause.

**Regression run on the code before the fix.** The new test file, copied
onto `f8424d330` (main before this change) and run with
`QT_QPA_PLATFORM=offscreen uv run pytest -q tests/integration/test_layout_keyboard.py -k "new_window_starts or reading_order"`,
fails all five tests: `5 failed, 20 deselected`.

1. `test_a_new_window_starts_with_the_focus_on_the_first_run_s_agent_selector`
   fails with `assert <PySide6.QtWidgets.QScrollArea(0x27b77160) at
   0x7f59cc212840> is <anesthesia_sim.app.qt_widgets.SelectorComboBox(0x2889c530)
   at 0x7f59cb003480>`: the record of control changes had the focus.
2. The three
   `test_tab_reaches_the_transport_then_the_tabs_then_each_area_in_reading_order`
   cases need `SimulationView._record_scroll`, which the fix added, and fail
   with `AttributeError: 'SimulationView' object has no attribute
   '_record_scroll'`. The variant without the exact run-region check, run on
   the same commit earlier the same day, failed each case at `assert
   all(_area_frame(stop) is None for stop in stops[:first_tab])` with `assert
   False`, because Tab reached Area controls before the Workspace tabs.
3. `test_tab_keeps_reading_order_after_a_branch_and_after_a_pinned_run_is_unpinned`
   fails in `_assert_areas_follow_their_choosers` with `assert not True`,
   because a chooser came after Tab had left the Areas.

On this branch with only the `raise_` in `_RunWidgets.follow` taken out, the
pin test fails at `assert max(dial_heights[:4]) < min(dial_heights[4:])` with
`assert 516 < 396`. With the focus given while building instead of at the
first show, the new-window test fails with the same `QScrollArea ... is
SelectorComboBox` message as on main.
