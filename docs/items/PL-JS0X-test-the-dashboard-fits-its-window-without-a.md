---
id: PL-JS0X
title: test_the_dashboard_fits_its_window_without_a_horizontal_scrollbar calls build_sidebar_panels a second time and then measures mapTo(page, ...) on panels that are not in the page, so its last two assertions are vacuous and the sidebar they claim to measure has been dismantled
priority: P2
effort: S
status: ready
classes: defect, test
feature: sidebar-panel-rebuild
touches: tests/integration/test_simulation_view.py
added: 2026-09-21
payoff: the test that claims the dashboard fits its window can fail when it does not
verify: grep -q 'def test_the_sidebar_panels_measured_are_the_ones_the_page_holds' tests/integration/test_simulation_view.py
---

**Problem.** test_the_dashboard_fits_its_window_without_a_horizontal_scrollbar calls build_sidebar_panels a second time and then measures mapTo(page, ...) on panels that are not in the page, so its last two assertions are vacuous and the sidebar they claim to measure has been dismantled

**Found 2026-09-21** while implementing `PL-C3GS`. The mechanism is `PL-N67T`:
the second `build_sidebar_panels()` call returns panels with no parent, so
`panel.mapTo(page, panel.rect().bottomRight()).x() <= page.width()` compares
coordinates that never reached the page and cannot fail. The test's name says
it checks the sidebar fits the window; those two lines check nothing, and the
same call strips the accounting and control-change labels out of the sidebar
the earlier assertions in the test have already measured.

**Fix.** Reach the panels already placed rather than building new ones - the
accounting panel is `run._accounting_heading_text.parent()` once `PL-C3GS` has
landed - or take whatever getter `PL-N67T` settles on.

**Why it matters.** A test whose name states a property and whose assertions
cannot fail is worse than no test. It is counted as coverage of the dashboard's
fit, it is what a later session will cite when it changes the layout, and it
goes on passing through whatever breaks that fit. The same call also strips the
accounting and control-change labels out of the sidebar mid-test, so the
assertions that ran before it measured a sidebar the assertions after it no
longer describe - the test is not merely weak at the end, it is incoherent
across its own length.

**Done when.** The two width assertions measure panels the shown page holds,
proved by an ancestry check against the view rather than by the panels having
just been built, and the test no longer calls `build_sidebar_panels` a second
time.
