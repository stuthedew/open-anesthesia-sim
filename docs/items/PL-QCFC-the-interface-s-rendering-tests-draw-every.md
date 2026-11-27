---
id: PL-QCFC
title: The interface's rendering tests draw every screen at a device pixel ratio of 1, so nothing checks a layout at the ratio of 2 that a Retina Mac draws
priority: P3
effort: S
status: ready
classes: test, ux
touches: tests/integration/test_compartment_schematic_view.py
added: 2026-11-27
payoff: a layout fault that appears only on a Retina screen is caught by a test instead of on the owner's Mac
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
