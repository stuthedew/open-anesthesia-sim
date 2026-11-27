---
id: PL-FSRR
title: On any screen whose scale is not 100%, every chart line, dash and legend swatch is drawn thinner and shorter than specified, because the chart's pens are cosmetic and Qt draws a cosmetic pen's width in device pixels
priority: P2
effort: M
status: ready
classes: defect, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/qt_chart.py, ROADMAP.md, docs/INTERFACE.md, tests/integration/test_chart_screen_scale.py
added: 2026-11-27
filed-pr: 2332
payoff: a user on a Retina or scaled Windows screen sees each chart trace at the width and dash pattern that tells it apart from the others
---

**Problem.** On any screen whose scale is not 100%, every chart line, dash and legend swatch is drawn thinner and shorter than specified, because the chart's pens are cosmetic and Qt draws a cosmetic pen's width in device pixels

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

**Every scale, not only Retina.** Measured 2026-11-27 with
`out/pen_probe.py`, a 3 px pen drawn on a `QImage` at five device pixel ratios
with `QT_QPA_PLATFORM=offscreen`. In device-independent pixels the cosmetic pen
drew 3, 2.4, 2, 1.5 and 1 px at ratios 1, 1.25, 1.5, 2 and 3. A non-cosmetic
pen drew 3, 2.4, 2.67, 3 and 3: its width is kept, rounded to whole device
pixels without antialiasing. Windows offers 125% and 150% scales, so the fault
is not confined to Retina screens. The schematic and the other widgets draw
with non-cosmetic `QPen`s and are not affected.

**Why Qt does this, from its source.** `QPainterPrivate::updateMatrix` in
`qtbase/src/gui/painting/qpainter.cpp` (branch 6.10, read 2026-11-27) appends
`hidpiScaleTransform()`, a scale by the device's pixel ratio, to the painter's
matrix. `QPaintEngineEx::stroke` in `qpaintengineex.cpp` strokes a cosmetic
pen after mapping the path through that matrix, so the width is applied in
device pixels.

**What the platforms recommend, read 2026-11-27.**
1. Qt, https://doc.qt.io/qt-6/highdpi.html: "Qt applications generally operate
   in device-independent pixels." Qt 6 is per-monitor DPI aware by default on
   Windows, and its default scale-factor rounding policy is PassThrough, so a
   ratio of 1.25 or 1.75 reaches the application unrounded.
2. Qt, https://doc.qt.io/qt-6/qevent.html: `QEvent::DevicePixelRatioChange`
   (since Qt 6.6) is sent when "The devicePixelRatio has changed for this
   widget's or window's underlying backing store."
3. Microsoft, https://learn.microsoft.com/en-us/windows/win32/hidpi/high-dpi-desktop-application-development-on-windows:
   per-monitor v2 awareness is recommended, an application redraws when it
   moves between displays, and "search for hard-coded sizes in your codebase
   that assume a constant DPI".
4. Apple, https://developer.apple.com/library/archive/documentation/GraphicsAnimation/Conceptual/HighResolutionOSX/Explained/Explained.html:
   "You should refer to display dimensions only in points", and the backing
   scale factor "is influenced by the display on which it is placed".
5. pyqtgraph has no option for it. Discussion #2215,
   https://github.com/pyqtgraph/pyqtgraph/discussions/2215, asked in 2022
   whether line width should follow the scale factor and has no reply. The
   library's own `ScatterPlotItem.paint` reads `widget.devicePixelRatioF()` at
   paint time and rebuilds its symbol atlas when the ratio changes, which is
   the same pattern applied to its symbols.

**The approach (owner asked for the general solution, 2026-11-27).** Every
chart pen is built by one function from its width and dash pattern in
device-independent pixels and the drawing widget's current device pixel ratio.
A check refuses a cosmetic pen built anywhere else in `src/`. Each chart and
legend rebuilds its pens on `QEvent.DevicePixelRatioChange`. Tests render at
ratios 1, 1.25, 1.5, 2 and 3. A non-cosmetic pen was ruled out: the curves are
drawn in the plot's data coordinates, whose two axes scale differently, so a
non-cosmetic width would change with the axis ranges. An audit of `src/` for
other content in device pixels found none: the app ships no image or icon
file, font sizes set with `setPixelSize` are device-independent in Qt, and the
one `QImage` is a 1 by 1 buffer used to measure tick labels.

**Why it matters.** `docs/INTERFACE.md` § "The six compartment traces: what
separates them" specifies each trace's width and dash pattern in pixels, and
the dash pattern is the channel that separates traces for a reader with a
colour-vision deficiency. On a Retina screen the muscle trace's dotted pattern
of 2 on and 3 off at 2 px is drawn as 1 on and 1.5 off at 1 px, and the mixed
venous short dash as 2 on and 1.5 off. Those are the patterns least easy to
tell apart, drawn at half the size at which their separation was chosen.

**Done when.** At device pixel ratios of 1, 1.25, 1.5, 2 and 3 every chart
line, dash and legend swatch has the width and dash lengths that
`docs/INTERFACE.md` specifies, in device-independent pixels, and tests hold
it. Moving to a screen with another ratio redraws at the new ratio, and a test
holds that too.

**Generator check.** One-off: the first rendering at a ratio other than 1. The check that refuses a cosmetic pen built outside the one function stops the next instance.

**Built 2026-11-27.** `on_screen` in `src/anesthesia_sim/app/qt_chart.py`
multiplies a cosmetic pen's width by the device pixel ratio and returns a
non-cosmetic pen unchanged. Each plot's `_ScreenPens`, made by `_plot`, gives
every line its pen through `hold` and gives them all again on
`DevicePixelRatioChange` and on show. Qt sends that event to every child widget
of a window whose ratio changes (`sendChangeRecursively` in
`qtbase/src/widgets/kernel/qwidgetwindow.cpp`, branch 6.10, read 2026-11-27).
The legend swatches convert when they paint, at the ratio of
`painter.paintEngine().paintDevice()`, because `painter.device()` is the widget
itself even during a grab into an image. An axis's `setPen` also sets its
title's colour, so `_set_drawn_pen` puts the title's style back. `drawn_pen`
and `preview_pen` now return the pen as specified, in device-independent
pixels.

**Regression test, run against the code before the fix.** The tests need
`on_screen`, which the fix added. The variant without it paints the chart's own
`trace_pen` and a legend swatch onto an image at a ratio of 2, from a worktree
of `origin/main` at `9c475dc7`. It printed "CIRCUIT trace: specified 3 px,
painted 1.50 px at ratio 2.0" and "legend swatch: specified 3.0 px, painted
1.50 px at ratio 2.0". On this branch the same measurement is
`test_each_trace_is_painted_at_its_specified_width_at_every_screen_scale` and
`test_each_legend_swatch_is_painted_at_its_line_s_width_at_every_screen_scale`.

**Docs checked at close-out:** `docs/INTERFACE.md` § "The six compartment
traces: what separates them" (states the unit, and its note for developers
names the tests), `docs/ARCHITECTURE.md`, `README.md`, `docs/MODEL.md`,
`docs/VERIFICATION.md` (none describes how chart lines are drawn).
