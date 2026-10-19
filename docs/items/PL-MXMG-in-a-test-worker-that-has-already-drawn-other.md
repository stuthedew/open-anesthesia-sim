---
id: PL-MXMG
title: In a test worker that has already drawn other dashboards, the dashboard page measures 15 px taller for its first two paints and only then shrinks
status: untriaged
feature: interface-areas
touches: src/anesthesia_sim/app/, tests/integration/test_qt_rendering.py
added: 2026-10-19
---

**Problem.** `tests/integration/test_qt_rendering.py`'s `induction_dashboard` fixture builds a dashboard on its own "every View" Workspace at 1400 x 1000 px. When the test runs alone, the page's size holds from the first paint. When pytest-xdist puts it in a worker after `tests/integration/test_dark_appearance.py` and `tests/integration/test_workspace_tabs.py`, the page (`dashboardPage`) measured 1562 px tall for the first two paints and then 1547 px. The Areas lost those 15 px, and the concentration plot lost 8 px of them. Measured on `PL-L59K`'s branch after it merged `#1653`, 2026-10-19; `main` at `2026b35f` showed no failure in 8 runs of the same four files.

**What it broke.** `test_the_hover_box_stays_inside_the_plot_at_every_edge` measured the hover box before the shrink and painted it after, so the box moved 0.4 px and the test failed in about 3 of 10 runs. pyqtgraph's view box updates its data-to-pixel mapping only when it is next painted. `PL-L59K` now paints the fixture until the page's size has held for five paints, which made 12 of 12 runs pass.

**Still unknown.** What changes the page's least height a few paints late, and whether a reader ever sees the jump. A first guess is application-wide state left by an earlier test, such as a palette or font change delivered late. A Workspace switch in the running app is worth checking for the same jump.

**Done when** the cause is named, and either the page settles on its first paint or the late change is shown to be confined to the test suite.
