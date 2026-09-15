---
id: PL-J0F7
title: The Qt chart's hover box was never looked at rendered: its placement flips near the window's right edge and the axis top, and nothing has confirmed the flip lands the box inside the plot or that INK on PANEL in a pg.TextItem is what is painted
priority: P2
effort: S
status: ready
classes: defect, ux
feature: qt-port
touches: src/anesthesia_sim/app/qt_chart.py, tests/integration/test_qt_rendering.py
added: 2026-09-14
verify: uv run pytest tests/integration/test_qt_rendering.py && grep -q 'def test_the_hover_box_stays_inside_the_plot_at_every_edge' tests/integration/test_qt_rendering.py
---

**Problem.** The Qt chart's hover box was never looked at rendered: its placement flips near the window's right edge and the axis top, and nothing has confirmed the flip lands the box inside the plot or that INK on PANEL in a pg.TextItem is what is painted

**Why it matters.** Two claims are being trusted without anyone having looked at
the result, and they fail in different ways. If the edge flip is wrong, the box
is clipped by the plot boundary at exactly the moment a reader is interrogating
the newest data - the right-hand edge is where a live run's pointer spends most
of its time - and a half-visible number is worse than no number, because the
digits that survive still read as a value. If `INK` on `PANEL` is not what a
`pg.TextItem` actually paints, the contrast the theme was chosen for is not the
contrast on screen, and `tools/contrast_check.py` cannot see it: that tool reads
declared constants out of `app/`, so a colour pyqtgraph substitutes at paint
time is invisible to it, which is the same blind spot `PL-97VB` recorded for
Material's disabled state.

Both are presentation correctness under `CLAUDE.md`'s standard rather than
polish, and neither is decidable from the source - the item is open because
somebody has to render it and look.

**Done when.** A headless rendering test drives the pointer to the right edge
and to the axis top and asserts the box's bounding rectangle lies inside the
plot's, the painted foreground and background of the `pg.TextItem` are read back
and checked against `INK` on `PANEL`, and a screenshot of each case has been
looked at by a person.
