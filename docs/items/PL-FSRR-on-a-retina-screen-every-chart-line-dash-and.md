---
id: PL-FSRR
title: On a Retina screen every chart line, dash and legend swatch is drawn at half its specified width and length, because the chart's pens are cosmetic and Qt draws a cosmetic pen's width in device pixels
status: untriaged
feature: presentation-safety
added: 2026-11-27
filed-pr: 2332
---

**Problem.** On a Retina screen every chart line, dash and legend swatch is drawn at half its specified width and length, because the chart's pens are cosmetic and Qt draws a cosmetic pen's width in device pixels

**How it was found.** `PL-QCFC` rendered the three shipped Workspaces offscreen
at 1366 by 768, once at a device pixel ratio of 1 and once at 2
(`QT_SCALE_FACTOR=2`), after 10 minutes of the default sevoflurane run, on
2026-11-27. Every visible widget had the same position and size at both
ratios: 260 in Default, 310 in Induction and 224 in Maintenance. The lines
painted inside the chart did not keep their size. At a ratio of 2 the circuit
trace is half as thick in device-independent pixels as at 1, and every dash
and gap is half as long. The legend swatches shrink the same way, so the key
still matches the plot. The pictures are in
`/mnt/project-files/v0.7.0/pl-qcfc-screens/`.

**Why it happens.** `pg.mkPen` builds a cosmetic pen, and every chart pen goes
through it (`dashed_pen` in `src/anesthesia_sim/app/qt_chart.py`). Qt's QPen
documentation (https://doc.qt.io/qt-6/qpen.html, read 2026-11-27) says:
"Cosmetic pens are used to draw strokes that have a constant width regardless
of any transformations applied to the QPainter they are used with." The
scaling from device-independent to device pixels is one of those
transformations, so a 3 px pen paints 3 device pixels, which is 1.5 px on a
Retina screen. Qt states a dash pattern in units of the pen's width, so the
dashes halve with it. pyqtgraph 0.14.0 does nothing about this for pens: a
search of its source for `devicePixelRatio` finds handling only for scatter
symbols, images and OpenGL. The measurement was made in emulation. It matches
Qt's documented rule, and the owner's Mac draws at a ratio of 2.

**Why it matters.** `docs/INTERFACE.md` § "The six compartment traces: what
separates them" specifies each trace's width and dash pattern in pixels, and
the dash pattern is the channel that separates traces for a reader with a
colour-vision deficiency. On a Retina screen the muscle trace's dotted pattern
of 2 on and 3 off at 2 px is drawn as 1 on and 1.5 off at 1 px, and the mixed
venous short dash as 2 on and 1.5 off. Those are the patterns least easy to
tell apart, drawn at half the size at which their separation was chosen.

**What a fix needs.** Each chart pen's width multiplied by the device pixel
ratio of the widget that draws it. Qt then scales the dash pattern with the
width. The legend swatches need the same scaling, so the key keeps matching
the plot. The pens must be rebuilt when the window moves to a screen with
another ratio, such as from a Retina laptop to an external monitor. A test
renders the chart at a ratio of 2 and asserts that a trace's drawn thickness,
in device-independent pixels, matches the one at a ratio of 1.

**Done when.** At a device pixel ratio of 2 every chart line, dash and legend
swatch has the width and dash lengths that `docs/INTERFACE.md` specifies, in
device-independent pixels. A test at a ratio of 2 holds it, and moving to a
screen with another ratio redraws at the new ratio.

**Generator check.** One-off: the first rendering at a ratio other than 1.
