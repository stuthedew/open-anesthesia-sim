---
id: PL-9BVQ
title: The hover box flips below its point only in the top quarter of the axis, so on a plot shorter than about four box heights it runs off the top
priority: P3
effort: S
status: done
classes: defect, ux
feature: interface-areas
milestone: v0.6.0
touches: src/anesthesia_sim/app/qt_chart.py, tests/integration/test_qt_rendering.py, tools/literal_home_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-10-19
closed: 2026-10-19
pr: 1673
payoff: a hover box on a short plot stays inside it, so its first line, which names the run when two are drawn, is never cut off
verify: grep -q 'def test_the_hover_box_stays_inside_a_plot_at_its_least_height' tests/integration/test_qt_rendering.py
---

**Problem.** `_HoverReadout.show_at` in `src/anesthesia_sim/app/qt_chart.py` places the hover box above its point unless the point is in the top quarter of the y axis (`anchor.value > 0.75 * y_top`). The test is a fraction of the axis, but the box has a fixed height in pixels, about 53 px for the F_A/F_I plot. So on a plot less than about four box heights tall, a point just under the top quarter puts the box partly above the plot.

**Found by** `tests/integration/test_qt_rendering.py::test_the_hover_box_stays_inside_the_plot_at_every_edge` while `PL-2KXB` (the Workspace tab strip) was being built. With the setting controls in an Area above the charts, the F_A/F_I plot was 160 px tall, and its "wash-in right" case drew the box from y = -8 px. The test now uses a layout without the setting controls, so it no longer covers a short plot.

**Why it matters.** A reader can drag an Area down to its View's least size, and the shipped Induction Workspace puts the F_A/F_I plot in half of the chart column. A hover box cut off at the top hides its first line, which names the run when two are drawn.

**Done when** the flip is decided in pixels: the box goes below its point whenever the space above the point is less than the box's height. A test draws the F_A/F_I plot at its least height and keeps every hover case inside the plot.

**Checked 2026-10-19:** still real on `main` at `6fd84bd5`: `_HoverReadout.show`
flipped on `anchor.value > 0.75 * y_top`. On a standalone F_A/F_I plot at its
least height, the plot inside its axes is 160 px tall and the box 53 px.

**Regression test against the code before the fix.**
`QT_QPA_PLATFORM=offscreen uv run pytest -q -p no:xdist
tests/integration/test_qt_rendering.py -k least_height` on `6fd84bd5` with the
new test added failed with `AssertionError: 42 of 60 boxes leave the plot`.

**Found in review, fixed here.** The pixel flip is worked out only when the
pointer moves or a frame is drawn. So a plot shrunk under a resting pointer
on a paused run kept the box where the tall plot had put it, with its top
13.6 px above the short plot. The old fraction rule had put that box below
its point. Each chart now places the hover again when its view box is
resized. `test_no_hover_box_is_left_outside_a_plot_that_shrinks_under_a_resting_pointer`
failed without the resize connection, with the box at y = -13.6 px against a
plot top at y = 1.0 px. The fix also removed the `0.75` that
`tools/literal_home_check.py` held as a baseline, so that line is deleted.
