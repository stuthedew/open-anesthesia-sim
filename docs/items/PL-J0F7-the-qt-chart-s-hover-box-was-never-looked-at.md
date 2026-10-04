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
verify: grep -q 'def test_the_hover_box_stays_inside_the_plot_at_every_edge' tests/integration/test_qt_rendering.py && uv run pytest tests/integration/test_qt_rendering.py
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

**Measured 2026-10-04, before the claim** (scratch scripts outside the tree,
against the shipped dashboard under the `offscreen` platform). About 50,000
hovers - every drawn point of one run and of two, at sevoflurane dials of 4.4,
5, 5.5, 6 and 8%, in the fitted window and in the chosen 15- and 30-minute
widths (the 15-minute one following, its newest point at the right edge), at
1600x1000 and 1024x768. Every painted box lay inside the plot, the view box's
scene rectangle. The one miss was a point exactly on the left edge of a
following window at 1024x768, where the box's left edge sat on the plot's and
the comparison failed by under 0.05 px, so the test compares with a sub-pixel
tolerance.

So the flip holds as built, and the work is the test and the screenshots
rather than a placement fix. The rule is fractional rather than size-aware - it
puts the box above whenever the anchor is at or below three quarters of the
axis, so a box taller than the remaining quarter would cross the top - but
nothing measured comes near it: the tallest box anywhere above the plot's middle
was 64 px, a two-run reading of four lines, against at least 80 px of room at
the theme's minimum plot height of 321 px; the 106 px seven-line box occurs only
at time zero, at the bottom left.

**Why nothing had exercised the flips.** The fixture in
`tests/integration/test_qt_rendering.py` runs 480 s into a 900 s fitted window,
and its highest trace is 2.2% on a 6% axis (`CHART_AXIS_TOP_MAC`, three times
sevoflurane's 2%), so it reaches neither the right edge nor the top quarter,
above 4.5%. The test needs its own run: a dial of 6 or 8% with the 15-minute
width chosen and the run past 15 minutes puts the newest point at the right
edge and the circuit trace through the top quarter.

**Colours.** Inside the box, inset past its border, the modal colour is exactly
`PANEL` (#FFFFFF), `INK` (#243B53) itself appears in every box's text (3 to 27
pixels at full coverage), and the rest are anti-aliasing blends, colour fringes
included.

**A trap for the test.** pyqtgraph 0.14.0's `TextItem.updateTransform` returns
at once while the item is hidden and is otherwise driven by the scene's
`sigPrepareForPaint`, so until the box has been painted its
`mapRectToScene(boundingRect())` can read thousands of pixels tall - 254x4165 px
before a grab, 390x78 px after. Measure after `chart.painted()`, which grabs and
so paints.

**Driving the pointer waits on `PL-TCR5`.** One `QTest.mouseMove` onto the plot
answers nothing and the next answers the previous position, so a test that
drives the pointer to an edge cannot pass while that lag stands. The two are
taken on one branch, `PL-TCR5`'s fix first; this item's test then moves the real
pointer, `QTest.mouseMove(chart._plot.viewport(), QPoint(*chart.plot_pixel(t, v)))`
and a `QTest.qWait` long enough for the 60 Hz proxy to deliver.
