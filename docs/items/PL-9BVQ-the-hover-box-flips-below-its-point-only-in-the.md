---
id: PL-9BVQ
title: The hover box flips below its point only in the top quarter of the axis, so on a plot shorter than about four box heights it runs off the top
status: untriaged
feature: interface-areas
added: 2026-10-19
---

**Problem.** `_HoverReadout.show_at` in `src/anesthesia_sim/app/qt_chart.py` places the hover box above its point unless the point is in the top quarter of the y axis (`anchor.value > 0.75 * y_top`). The test is a fraction of the axis, but the box has a fixed height in pixels, about 53 px for the F_A/F_I plot. So on a plot less than about four box heights tall, a point just under the top quarter puts the box partly above the plot.

**Found by** `tests/integration/test_qt_rendering.py::test_the_hover_box_stays_inside_the_plot_at_every_edge` while `PL-2KXB` (the Workspace tab strip) was being built. With the setting controls in an Area above the charts, the F_A/F_I plot was 160 px tall, and its "wash-in right" case drew the box from y = -8 px. The test now uses a layout without the setting controls, so it no longer covers a short plot.

**Why it matters.** A reader can drag an Area down to its View's least size, and the shipped Induction Workspace puts the F_A/F_I plot in half of the chart column. A hover box cut off at the top hides its first line, which names the run when two are drawn.

**Done when** the flip is decided in pixels: the box goes below its point whenever the space above the point is less than the box's height. A test draws the F_A/F_I plot at its least height and keeps every hover case inside the plot.
