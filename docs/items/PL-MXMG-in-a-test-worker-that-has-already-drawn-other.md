---
id: PL-MXMG
title: In a test worker that has already drawn other dashboards, the dashboard page measures 15 px taller for its first two paints and only then shrinks
priority: P3
effort: M
status: ready
classes: defect, test
feature: interface-areas
touches: src/anesthesia_sim/app/, tests/integration/test_qt_rendering.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 triage pass
added: 2026-10-19
payoff: a pixel measurement in a rendering test no longer depends on which tests ran before it in the same worker
verify: grep -q 'def test_the_dashboard_page_keeps_its_height_from_its_first_paint' tests/integration/test_qt_rendering.py
---

**Problem.** `tests/integration/test_qt_rendering.py`'s `induction_dashboard` fixture builds a dashboard on its own "every View" Workspace at 1400 x 1000 px. When the test runs alone, the page's size holds from the first paint. When pytest-xdist puts it in a worker after `tests/integration/test_dark_appearance.py` and `tests/integration/test_workspace_tabs.py`, the page (`dashboardPage`) measured 1562 px tall for the first two paints and then 1547 px. The Areas lost those 15 px, and the concentration plot lost 8 px of them. Measured on `PL-L59K`'s branch after it merged `#1653`, 2026-10-19; `main` at `2026b35f` showed no failure in 8 runs of the same four files.

**What it broke.** `test_the_hover_box_stays_inside_the_plot_at_every_edge` measured the hover box before the shrink and painted it after, so the box moved 0.4 px and the test failed in about 3 of 10 runs. pyqtgraph's view box updates its data-to-pixel mapping only when it is next painted. `PL-L59K` now paints the fixture until the page's size has held for five paints, which made 12 of 12 runs pass.

**Still unknown.** What changes the page's least height a few paints late, and whether a reader ever sees the jump. A first guess is application-wide state left by an earlier test, such as a palette or font change delivered late. A Workspace switch in the running app is worth checking for the same jump.

**Done when** the cause is named, and either the page settles on its first paint or the late change is shown to be confined to the test suite.

**Why it matters.** A page whose height changes a few paints after it is
built makes every pixel measurement in a test depend on when it was taken,
which is what made the hover-box test fail in about 3 of 10 runs. If a reader
can see the same jump, a chart shifts under the pointer just after a
Workspace opens. `PL-4L8B` and `PL-PHPZ` both describe an Area's hint that
changes after the layout was sized, because a View fills in on its first
frame. This may be a third case of that mechanism. If the cause named here is
that one, record the three as a generator.

**Not reproduced by this pass (2026-10-19).** `PL-L59K` now paints the
`induction_dashboard` fixture until the page's size holds for five paints, so
the failing test no longer shows the jump. Reproducing it means measuring the
page's height at each of the first paints in a worker that has already run
`tests/integration/test_dark_appearance.py` and
`tests/integration/test_workspace_tabs.py`.

**How the work is proven.** The work adds a test that the page keeps its height from its
first paint. If the cause turns out to be confined to the test suite, rewrite
this Done-when and the `verify:` for that case before closing.
