---
id: PL-SGRS
title: test_qt_rendering.py's dashboard fixture builds SimulationView without case=, so the Branch section main.py ships is hidden from every headless rendering assertion
status: untriaged
touches: tests/integration/test_qt_rendering.py
added: 2026-10-01
---

**Problem.** test_qt_rendering.py's dashboard fixture builds SimulationView without case=, so the Branch section main.py ships is hidden from every headless rendering assertion

**Found 2026-10-01** during `PL-CQRL`. The module-scoped `dashboard` fixture in
`tests/integration/test_qt_rendering.py` builds `SimulationView((controller,))`.
`main()` builds `SimulationView((case.trunk,), case=case)` from a
`BranchedCase`, and calls `declare_application_colours` first.
`SimulationView` hides `_fork_section` when `case` is None, so the Branch
section - `From` and `Branch here`, below the bookmarks - is absent from every
frame this module asserts over. Its geometry checks (the row and the sidebar
inside the page, no readout clipped by its panel) have never seen the page
that ships.

The module docstring also says "the same grab a test reads is the screenshot
`docs/worker.md` tells a session how to write". Since `PL-CQRL` that procedure
is `.claude/skills/run-the-app/SKILL.md`, which builds with `BranchedCase` as
`main()` does, so the two grabs are no longer the same composition until the
fixture follows `main()`.
