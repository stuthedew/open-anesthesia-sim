---
id: PL-QCFC
title: The interface's rendering tests draw every screen at a device pixel ratio of 1, so nothing checks a layout at the ratio of 2 that a Retina Mac draws
priority: P3
effort: S
status: done
classes: test, ux
touches: tests/integration/test_chart_screen_scale.py
added: 2026-11-27
closed: 2026-11-27
pr: 2332
payoff: a layout fault that appears only on a Retina screen is caught by a test instead of on the owner's Mac
tests: tests/integration/test_chart_screen_scale.py::test_on_a_screen_at_each_scale_both_plots_stroke_every_line_at_its_width
---

**Problem.** The interface's rendering tests draw every screen at a device pixel ratio of 1, so nothing checks a layout at the ratio of 2 that a Retina Mac draws

**Where this comes from.** Lesson 43 of the owner's machine-control dashboard
project (2026-11-27, `PL-HWZK`). In that project the graphs grew two to three
times at device pixel ratios of 2 and 3 and hid the x axis. The lesson has no
published source; it is that project's own finding.

**What was seen here.** `tests/integration/test_compartment_schematic_view.py`
asserts that its grabbed image has a device pixel ratio of 1.0, and no test
under `tests/` sets another ratio. The owner's Mac draws at 2.

**What to do.** Render the Default Workspace offscreen once at a device pixel
ratio of 2, compare the layout with the render at 1, and record whether any
text, axis or required value moves, clips or changes size relative to its
Area. If something does, add a test that renders at 2.

**Why it matters.** Qt lays out in device-independent pixels, so most of the
interface should scale as a whole. The chart and the schematic paint their own
text and lines, and a fault there would reach a clinical value's label.

**Done when.** This item records the comparison, and a test at a ratio of 2
exists if the comparison found a difference.

**Generator check.** One-off: the first finding that no test renders at a ratio other than 1.

**Measured 2026-11-27.** The three shipped Workspaces were rendered offscreen
at 1366 by 768, at a device pixel ratio of 1 and of 2 (`QT_SCALE_FACTOR=2`),
after 10 minutes of the default sevoflurane run. Every visible widget kept the
same position and size: 260 in Default, 310 in Induction and 224 in
Maintenance. No text, axis or required value moved or clipped. The lines
painted inside the chart did change: each one, with its dashes and the legend
swatches, is drawn at half its width and length at a ratio of 2. That is
`PL-FSRR`, which carries the fix and the test at a ratio of 2. The pictures are
in `/mnt/project-files/v0.7.0/pl-qcfc-screens/`.

**Closed with `PL-FSRR`, 2026-11-27.** The test this item asked for is
`tests/integration/test_chart_screen_scale.py`. It renders the charts and their
legends at device pixel ratios of 1, 1.25, 1.5, 2 and 3, both into an image of
that ratio and in a child process run with `QT_SCALE_FACTOR` set, and checks
each line's painted width and dash length against its specified size. The
layout itself needed no test of its own, because the measurement above found
no widget that moved or changed size.

**Docs checked at close-out.** `docs/INTERFACE.md` § "The six compartment
traces: what separates them" (updated with `PL-FSRR`), `README.md` (no
mention of screen scale), `docs/VERIFICATION.md` (none).
