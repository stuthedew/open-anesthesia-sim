---
id: PL-MXMG
title: In a test worker that has already drawn other dashboards, the dashboard page measures 15 px taller for its first two paints and only then shrinks
priority: P3
effort: M
status: done
classes: defect, test
feature: interface-areas
milestone: v0.6.0
touches: src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/simulation_view.py, tests/integration/test_qt_rendering.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 triage pass
added: 2026-10-19
closed: 2026-10-19
pr: 1686
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

**Fixed 2026-10-19: the cause is `PL-YJ21`'s, and a reader could see it.**
`_RunCopies.follow` shows each per-run line of a chart and `_RunLines.show`
hides the ones with no text, in the same frame. Until Qt handed out the layout
requests those changes posted, the concentration chart still counted two
15 px lines, so the page measured taller and shrank a pass later. It is not
confined to a used test worker. In a fresh process on `main` at `2aab62b3`,
the `induction_dashboard` sequence gave page heights of 1490, 1550 and then
1535 px for every later paint. After the fix it is 1535 px from the first
frame. A reader would have seen the same shift on the first frames after a
Workspace opens. The fixture no longer paints until the page holds, and paints
once so that pyqtgraph's mapping is the one drawn.

`test_the_dashboard_page_keeps_its_height_from_its_first_paint` fails on the
code before the fix with `[1490, 1550, ...5, 1535, 1535] == [1490, 1490, ...]`.
