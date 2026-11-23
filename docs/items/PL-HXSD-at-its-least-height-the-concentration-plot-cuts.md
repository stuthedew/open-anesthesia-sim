---
id: PL-HXSD
title: At its least height the concentration plot cuts through the hover box's last value line when the time axis's title wraps or the desktop font is larger than the container's (box 113 px, plot 101.1 px at 400 px wide; box 120 px, plot 112.3 px with a 13-pixel font; measured offscreen 2026-11-23); make the box fit whole
priority: P1
effort: S
status: done
classes: ux, safety
feature: chart-readout
touches: src/anesthesia_sim/app/qt_chart.py, src/anesthesia_sim/app/theme.py, tests/integration/test_qt_chart.py, docs/INTERFACE.md
deferred-from: v0.7.0 - the gate items are done and the release waits on the owner's test drive; this is the next item of the chart-readout chain, so it lands in a patch release rather than holding the cut
added: 2026-11-23
closed: 2026-11-23
pr: 2276
filed-pr: 2274
tests: tests/integration/test_qt_chart.py::test_the_tallest_hover_box_is_drawn_whole_at_the_least_height, tests/integration/test_qt_chart.py::test_a_font_too_large_for_the_least_height_makes_the_chart_taller
---

**Problem.** At its least height the concentration plot cuts through the hover box's last value line when the time axis's title wraps or the desktop font is larger than the container's (box 113 px, plot 101.1 px at 400 px wide; box 120 px, plot 112.3 px with a 13-pixel font; measured offscreen 2026-11-23); make the box fit whole

**Found on 2026-11-23** while closing `PL-S0HP`. That item's test,
`test_the_tallest_hover_box_fits_the_plot_at_its_least_height` in
`tests/integration/test_qt_chart.py`, shows that the tallest box (the agent and
six value lines) fits the plot at `theme.CHART_LEAST_HEIGHT` in the
container's font (box 113.0 px, plot 113.1 px) and in DejaVu Sans, the CI
runners' font (box 106.0 px, plot 114.9 px). The container's font is 9 pt at a
logical 96 dpi, which is 12 px with a 14.5 px line. The same test with the
application font set to 13 px gave a box of 120.0 px and a plot of 112.3 px,
so the box's last value line is cut off by the plot's edge.

**The narrow plot.** Both blind reviews of `#2274` found the second case.
`ConcentrationView` writes the window into the time axis's title, such as
"simulated time, 15 minutes shown, centred on now during the preview", and
`_TimeAxisTitle` breaks it after a comma on a narrow axis. Each extra line
comes out of the data area. With that caption, at the 160 px least height,
the data area measured as follows (box 113.0 px in the container's font,
106.0 px in DejaVu Sans):

| plot width | container's font | DejaVu Sans |
| --- | --- | --- |
| 900 px | 113.1 px | 114.9 px |
| 600 px | 113.1 px | 114.9 px |
| 400 px | 101.1 px | 103.7 px |
| 300 px | 89.1 px | 92.5 px |

The concentration View's least width is 420 px, so its plot can be about
400 px wide. So in a narrow View the box does not fit in either font.

**Why it matters.** The cut falls through a row of digits that the learner is
reading, which is the misreading `PL-571L` fixed for the top tick label, where
a half-drawn "6" read as a "0". It needs the plot at its least height, a hover
where all six traces are in reach, and a narrow View or a larger font.

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

**Done when.** No value line of the hover box is ever drawn in part: the
tallest box fits whole at the least height on a plot 400 px wide with the
longest caption, and with a 13-pixel font, a test shows both, and the 1366 by
768 layouts are checked again. Growing `theme.CHART_LEAST_HEIGHT` alone does
not meet this. A 300 px plot loses two lines, and a taller least height costs
the 1366 by 768 layouts their slack in every View, not only the narrow ones.

**Generator check.** A one-off. It shares its cause with `PL-S6CP`: a height
measured in the container's font only. The `PL-S0HP` test now pins two fonts,
and this item adds the larger one.

**Done 2026-11-23.** Route 3, in a lighter form than the brief feared, with
route 1 kept as a floor. The box is now an item of the plot's scene rather
than of its view box, so the view box no longer clips it. `_HoverReadout.show`
in `src/anesthesia_sim/app/qt_chart.py` still keeps the box inside the plot
wherever the plot is as tall as the box, by the old rules. Where it is not,
the box is moved up until all of it is inside the chart widget, over the time
axis if need be. `_HoverReadout.hold_the_tallest_box` sets the plot's least
height to the larger of the theme height and the tallest box's height, and
gives the box the plot's font. Both charts call it again on a font change. At
the container's font, DejaVu Sans and 13 px the theme height is the larger,
so no least height changed: 160 px and 120 px in both fonts, measured
offscreen, and the page and layout tests (100) pass unchanged. No overlay
widget was needed, and `hover_box` reports the same pixels as before.

**Best practice, read 2026-11-23.** Each source was read through a fetch of
the page itself.

1. WCAG 2.1 Understanding SC 1.4.4 Resize Text
   (https://www.w3.org/WAI/WCAG21/Understanding/resize-text.html) asks that
   text resize to 200% "without loss of content or functionality", and lists
   failure F69, text "clipped, truncated or obscured". Shrinking the box's
   text (route 2) would cut content exactly when a reader enlarges the font,
   so it was rejected. The same reasoning is why the floor exists: the
   24-pixel case in the test is that 200%.
2. Carbon's tooltip guidance (https://carbondesignsystem.com/components/tooltip/usage/,
   § "Placement") asks that a tooltip "overlays other content and is not
   cut off by other surrounding components", and says "Do not cover related
   content that is essential to the user's tasks."
3. The Floating UI tutorial (https://floating-ui.com/docs/tutorial, §
   "Shift middleware") describes the standard remedy: the floating element is
   "shifted ... until it was fully in view". This fix is that shift, against
   the chart widget's edge.
4. Nielsen Norman Group's tooltip guidelines
   (https://www.nngroup.com/articles/tooltip-guidelines/, § "Additional
   Recommendations") say "When tooltips block the content they're related
   to, they cause users to repeat steps". The box therefore stays inside the
   plot where it fits, and covers the time axis's ticks and title only while
   a plot too short for it is hovered.

Route 1 alone (a least height that always gives the plot the box's height)
was set aside because the concentration View has about 9 px of height to
spare at 1366 by 768, and the narrow case needs 12 px in the container's
font.

**Found while testing.** The rectangle that `hover_box` reports stays whole
when something clips the box, so the `PL-S0HP` test passed while the box was
cut. It also hid a second cut: on the wide plot in the container's font the
box's top border sat 0.4 px above the plot and was clipped, which its 0.5 px
tolerance accepted. The new test reads the painted pixels of the box's top
and bottom edges.

**Regression check.** With `src/anesthesia_sim/app/qt_chart.py` reverted,
`uv run pytest tests/integration/test_qt_chart.py -k "tallest or too_large"`
fails 6 of 7 cases: "the box's top edge is 0% drawn" (wide, container
font), "the box's bottom edge is 9% drawn" (wide, 13 px), 16% (narrow,
container font), 1% (narrow, DejaVu Sans), 0% (narrow, 13 px), and
"assert 160 > 160" for the 24-pixel font. The wide DejaVu Sans case was
never cut and passes on both.

**Files checked.** `docs/INTERFACE.md` § "The chart's hover readout: what
the tooltip may show" (requirement added, developer note rewritten),
`src/anesthesia_sim/app/theme.py` (`CHART_LEAST_HEIGHT` comment), the
docstrings of `sizeHint`, `plot_area` and `_preferred_size` in
`src/anesthesia_sim/app/qt_chart.py`, and `tests/integration/test_qt_rendering.py`
(its placement tests still hold the box inside the plot where it fits; all
pass unchanged).
