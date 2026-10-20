---
id: PL-NNML
title: The dashboard page still scrolls at laptop window heights, so the use disclaimer is below the fold and scrolling to it moves the unconditional region out of view
priority: P1
effort: M
status: done
classes: safety
feature: v0.6.0-done-check
touches: src/anesthesia_sim/app/simulation_view.py, docs/MODEL.md, ROADMAP.md, tests/integration/test_simulation_view.py, tests/integration/test_qt_rendering.py
added: 2026-10-20
closed: 2026-10-20
pr: 1700
payoff: the use disclaimer and the time, run state, agent and concentrations stay in view at every window height, so no learner reads a value with its context scrolled away
verify: grep -q 'def test_the_region_and_the_use_disclaimer_stay_in_the_viewport' tests/integration/test_simulation_view.py
---

**Problem.** The dashboard page still scrolls at laptop window heights, so the use disclaimer is below the fold and scrolling to it moves the unconditional region out of view

**Why it matters.** `/mnt/project-files/v0.6.0/dod-check.md` holds the whole check of v0.6.0's Definition of done, run on 2026-10-20 before the cut. `docs/MODEL.md` § "Minimum displayed outputs" requires the unconditional values to be visible in every layout, and § "Where the educational-use disclaimer lives" says the use disclaimer is in view at every window height once the page stops scrolling. The page still scrolls: `SimulationView` lays the dashboard out inside a `QScrollArea`. Measured offscreen on 2026-10-20 at 1366 px wide, the page is 1087 px tall in the Default Workspace, so it scrolls 387 px at a 700 px window and 187 px at 900 px. In the Induction and Maintenance Workspaces it is 1505 px tall and scrolls 805, 605 and 405 px at windows 700, 900 and 1100 px high. At those heights the disclaimer at the foot is below the fold until the reader scrolls. Scrolling down to it, or taking a branch, which scrolls to the concentration chart, moves the region holding time, run state, agent and concentrations up out of view. This gap predates v0.6.0. No item tracked it once the tiled layout shipped without closing it.

**Done when.** At every supported window height the region and the use disclaimer stay in view, a test asserts both are inside the window at 700, 900 and 1100 px, scrolled and after a branch is taken, and `docs/MODEL.md` states the rule as met.

**Fix** (2026-10-20). The region now sits above the part of the dashboard that scrolls and the use disclaimer below it, so only the Workspace tabs, the Areas and the case's controls scroll (`SimulationView._build_page`). Making the Areas fill the window with no scrolling at all was the larger alternative. It was not taken, because it needs a decision on what happens when the shipped Workspaces' Area minimums do not fit, which the project owner wants to revisit separately.

**Regression test against the code before the fix.** `uv run pytest -q -p no:randomly tests/integration/test_simulation_view.py -k viewport`, with `simulation_view.py` at `fc94e996`, fails all 9 cases with, for example, `on opening: the disclaimer at PySide6.QtCore.QRect(16, 1484, 1320, 15) is not inside the PySide6.QtCore.QRect(0, 0, 1366, 900) window`. With the fix all 9 pass.
