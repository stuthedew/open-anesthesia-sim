---
id: PL-K4CZ
title: At 1366 by 768 the concentration chart's legend and reference lines take more of its Area than the plot does: the plot widget is 228 px tall of a 480 px Area in Default and 120 px in Induction
status: done
feature: interface-design-review
milestone: v0.6.20
added: 2026-11-22
closed: 2026-11-22
pr: 2218
tests: tests/integration/simulation_view/test_simulation_view_page.py::test_the_concentration_plot_takes_half_its_area_on_a_laptop, tests/integration/test_qt_chart.py::test_each_clinical_reference_entry_states_its_value_and_the_band_s_words_wrap, tests/integration/test_qt_widgets.py::test_a_flow_layout_gives_an_item_wider_than_the_row_the_row_s_width, tests/integration/simulation_view/test_simulation_view_page.py::test_the_1_mac_value_stays_on_screen_where_the_rows_above_the_plot_scroll, tests/integration/test_qt_chart.py::test_the_time_axis_title_states_the_window_and_breaks_only_after_a_comma, tests/integration/simulation_view/test_simulation_view_page.py::test_the_screen_walk_reads_the_mac_awake_entry_whole_where_its_words_wrap
---

**Problem.** At 1366 by 768 the concentration chart's legend and reference lines take more of its Area than the plot does: the plot widget is 228 px tall of a 480 px Area in Default and 120 px in Induction

**Go-ahead.** The design review that found this was approved by the project owner (project owner, 2026-11-22). It ran offscreen on `a7eb53f`, with screenshots of each Workspace and each View at 1366 by 768 and 1920 by 1080 in `/mnt/project-files/v0.7.0/design-review/`.

**What a learner sees.** Above the plot sit the caption, the 1 MAC line, the
MAC-awake line, the compartment check boxes in two or three wrapped rows, the
clinical references in two rows and the run record row, about 190 px in all at
1366 by 768 (`ws0-Default-1366x768.png`). The plot widget, axes included, is
228 px of a 480 px Area in Default and 120 px in Induction (measured offscreen).

**Why it matters.** The plot is the chart's reason to exist, and at the
smallest supported screen the text that explains it gets more height than it
does. The lines are required, so they cannot simply go. The question is
where they sit.

**What to do.** This is design input for the grey-box layouts in `PL-2V6V`.
Two directions to try there: a legend in one column beside the plot, which
uses the width the chart has spare at 1366 px, and folding the 1 MAC and
MAC-awake reference values into their legend rows so each fact is stated
once. Either must keep every value `docs/INTERFACE.md` § "Minimum displayed
outputs" requires on screen, which makes the final choice the owner's.

**Done when.** `PL-2V6V`'s layouts show the plot taking at least half the
chart Area at 1366 by 768 with every required line visible, or record why
not.

**Built 2026-11-22** (coordinator's direction: look and placement, decided in
the thread). The 1 MAC and MAC-awake values left their own lines above the
legend and moved into the legend entries for the line and the band. The 1 MAC
entry now reads "1 MAC sevoflurane = 2.0%, reference adult (alveolar, wide
dash)" and comes first, because the band's fraction is a fraction of it. The
band's entry reads "MAC-awake sevoflurane = 0.34 ×MAC (0.68%), band ±1 SD
0.58–0.78%; population, read against vessel-rich trace". Every value that
`docs/INTERFACE.md` § "Minimum displayed outputs" requires is still on screen,
each stated once in the View instead of twice, so the owner was not asked.

The band's entry is the legend's longest, at about 650 px. So its words wrap
in a narrow View rather than raise the View's least width: `FlowLayout` now
gives an item wider than its row the row's width and the height its words
need there. The words break only after a comma or a semicolon, so no value
is parted from its unit and no range from either edge.

The clinical references row is now the legend's first row, above the
compartments. Where the box above the plot is squeezed to its first rows, as
in Induction at 1366 by 768, the 1 MAC value stays on screen, as it did on
its own line.

The statement of the window shown ("whole run so far, 15 minutes shown")
left its own line above the legend, in both chart Views, and joined the time
axis's title: "simulated time, whole run so far, 15 minutes shown". On an axis
too narrow for one line, the title breaks after a comma, by the same rule as
the band's entry, so a span keeps its unit. The gap between legend lines went
from 6 px to 4 px (`theme.LEGEND_LINE_SPACING`, a placeholder until the
visual pass).

Both were added after CI failed the half-Area test at 222 of 494 px. CI draws
with DejaVu Sans, which is wider than the container's Inter, so the compartment
entries take three rows there. The share depends on the font, so it was
measured under both, offscreen at 1366 by 768 after 300 s of a run, on
`b031612b` (main) against the branch:

| Workspace | Inter, before | Inter, after | DejaVu Sans, before | DejaVu Sans, after |
| --- | --- | --- | --- | --- |
| Default | 209 of 488 px (43%) | 280 (57%) | 196 of 494 px (40%) | 252 (51%) |
| Maintenance | 183 of 488 px (38%) | 256 (52%) | 196 of 494 px (40%) | 266 (54%) |
| Induction | 160 of 307 px (52%) | 160 (52%) | 160 of 307 px (52%) | 160 (52%) |

Liberation Sans, which has Arial's widths, gave 59% in Default and 55% in
Maintenance after the change. Induction holds the plot at its least height,
and the rows above it scroll in their own box. Screenshots:
`/mnt/project-files/v0.7.0/design-review/before-after/7-`, `8-` and
`9-chart-legend-*.png`, drawn with the container's Inter.

A side column for the legend was not taken: it would narrow a time plot that
is already about 690 px wide at 1366 px, and it needs a layout that switches
with the Area's shape. That is left for `PL-2V6V`'s grey-box layouts.

Regression test: `test_the_concentration_plot_takes_half_its_area_on_a_laptop`
fails on `f8424d3` with `assert (2 * 209) >= 488`.

Blind review, two passes. Both named the same fault: with the values moved
into a references row below the compartments, Induction's squeezed box
scrolled the 1 MAC value out of sight. Fixed by putting the references row
first; `test_the_1_mac_value_stays_on_screen_where_the_rows_above_the_plot_scroll`
fails on `201b184` with `assert (73 + 15) <= 41`. Pass 1 also found that Qt's
word wrap could end a line on "0.58–" or between "±1" and "SD". Fixed by
breaking only after a comma or a semicolon, and checked in
`test_each_clinical_reference_entry_states_its_value_and_the_band_s_words_wrap`.
The time axis's break is checked in
`test_the_time_axis_title_states_the_window_and_breaks_only_after_a_comma`.

Blind review of the time-axis change, two more passes. Pass 1 found that
pyqtgraph centres an axis title only when the axis is resized, so a new
window statement with as many lines as the old one stayed where the old one
began: 102 px off centre in the test, which now fails without the fix. Fixed
by calling the axis's resize handler after each new title. Pass 1 also found
that the dashboard's walk over what is on screen read the band entry's broken
text, so a check that the MAC-awake fraction is on screen would fail in a
narrow window. The clause-breaking label moved to `qt_widgets.py` as
`ClauseWrappingLabel`, and the walk reads its words on one line;
`test_the_screen_walk_reads_the_mac_awake_entry_whole_where_its_words_wrap`
fails without that. Pass 2 found that the label relaid out the legend on
every frame although its words had not changed; it now returns early, as
`QLabel.setText` does.

The odd Induction picture taken while redoing the screenshots, with the 1 MAC
entry cut short and the band beside it, was the capture taken before Qt had
finished laying the legend out. After the events were processed, both
entries sat where they belong.

Docs checked: `docs/INTERFACE.md` (§ "Minimum displayed outputs", the MAC-awake
band's two numbers; § "MAC-awake as a chart reference"; § "The chart's time
base", whose sentence on where the chart names the width now names the time
axis's title), `docs/MODEL.md` (no mention of where the reference values sit),
`README.md` and `docs/ARCHITECTURE.md` (neither describes the legend rows), and
the docstrings of `ConcentrationView`, `_KeyScroll`, `mac_awake_caption`,
`format_mac_awake_reference`, `FlowLayout`, `ClauseWrappingLabel`, `WashInView`, the window caption
templates in `dashboard_frame.py`, `theme.CHART_KEY_LEAST_HEIGHT` and
`theme.LEGEND_LINE_SPACING`.
