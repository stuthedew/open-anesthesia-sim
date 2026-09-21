---
id: PL-JS0X
title: test_the_dashboard_fits_its_window_without_a_horizontal_scrollbar calls build_sidebar_panels a second time and then measures mapTo(page, ...) on panels that are not in the page, so its last two assertions are vacuous and the sidebar they claim to measure has been dismantled
status: untriaged
feature: sidebar-panel-rebuild
added: 2026-09-21
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
