---
id: PL-HXSD
title: At its least height the concentration plot cuts off the hover box's last value line when the desktop font is larger than the container's: with a 13-pixel font the box with every trace is 120 px and the plot's data area 112.3 px (measured offscreen 2026-11-23); make the box fit for any desktop font
priority: P2
effort: S
status: untriaged
classes: ux, safety
feature: chart-readout
touches: src/anesthesia_sim/app/qt_chart.py, tests/integration/test_qt_chart.py, docs/INTERFACE.md
deferred-from: v0.7.0 - it needs the window at its least height and a desktop font larger than the container's, measured only on a 13 px stand-in; the owner's test drive of v0.7.0 on a Mac can show whether it happens there
added: 2026-11-23
filed-pr: 2274
---

**Problem.** At its least height the concentration plot cuts off the hover box's last value line when the desktop font is larger than the container's: with a 13-pixel font the box with every trace is 120 px and the plot's data area 112.3 px (measured offscreen 2026-11-23); make the box fit for any desktop font

**Found on 2026-11-23** while closing `PL-S0HP`. That item's test,
`test_the_tallest_hover_box_fits_the_plot_at_its_least_height` in
`tests/integration/test_qt_chart.py`, shows that the tallest box (the agent and
six value lines) fits the plot at `theme.CHART_LEAST_HEIGHT` in the
container's font (box 113.0 px, plot 113.1 px) and in DejaVu Sans, the CI
runners' font (box 106.0 px, plot 114.9 px). The container's font is 9 pt at a
logical 96 dpi, which is 12 px with a 14.5 px line. The same test with the
application font set to 13 px gave a box of 120.0 px and a plot of 112.3 px,
so the box's last value line is cut off by the plot's edge.

**Why 13 px matters.** Apple's Human Interface Guidelines give 13 pt as
macOS's default text size and Body style, with a 16 pt line
(https://developer.apple.com/design/human-interface-guidelines/typography,
read 2026-11-23, the macOS text styles table). The owner works on a Mac. No
source read in this session says how Qt on macOS maps 13 pt to its
device-independent pixels: the Qt 6 and Qt 5 high-DPI pages give no macOS
logical DPI, and the only page that says 72 is a 2013 user post on
forum.qt.io. So 13 px is a stand-in for the Mac's font, not a measurement of
it. Measure on the owner's Mac if a route depends on the exact size.

**Routes weighed.**

1. Make the plot's least height follow the font, so the data area always
   holds the tallest box. The View's least height already follows its own
   layout (`PL-S6CP`), so the Areas would move with it. The cost is a taller
   chart at 1366 by 768 under a larger font.
2. Shrink the box's text where the box is taller than the plot. The layout
   is unchanged, and the cost is smaller text at the least height only.
3. Draw the box outside the plot, on an overlay above the chart. `PL-YJ7N`
   rejected this because pyqtgraph clips a view box's items, so it needs an
   overlay widget and changes what `hover_box` reports to every hover test.

**Done when.** The tallest box fits the plot at its least height for a desktop
font of at least 13 px, a test shows it, and the 1366 by 768 layouts are
checked again.

**Generator check.** A one-off. It shares its cause with `PL-S6CP`: a height
measured in the container's font only. The `PL-S0HP` test now pins two fonts,
and this item adds the larger one.
