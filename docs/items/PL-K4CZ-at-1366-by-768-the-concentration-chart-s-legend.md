---
id: PL-K4CZ
title: At 1366 by 768 the concentration chart's legend and reference lines take more of its Area than the plot does: the plot widget is 228 px tall of a 480 px Area in Default and 120 px in Induction
status: done
feature: interface-design-review
added: 2026-11-22
closed: 2026-11-22
pr: 2218
tests: tests/integration/simulation_view/test_simulation_view_page.py::test_the_concentration_plot_takes_half_its_area_on_a_laptop, tests/integration/test_qt_chart.py::test_each_clinical_reference_entry_states_its_value_and_the_band_s_words_wrap, tests/integration/test_qt_widgets.py::test_a_flow_layout_gives_an_item_wider_than_the_row_the_row_s_width, tests/integration/simulation_view/test_simulation_view_page.py::test_the_1_mac_value_stays_on_screen_where_the_rows_above_the_plot_scroll
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

Measured offscreen at 1366 by 768, 10 minutes into a run, on `f8424d3`
against the branch. The plot widget, axes included, went from 209 px to
251 px of the 488 px Area in Default (43% to 51%), and from 180 px to 207 px
in Maintenance (37% to 42%). Induction is unchanged at 160 px of 307 px,
the plot's least height, with the rows above it scrolling in their own box.
Screenshots: `/mnt/project-files/v0.7.0/design-review/before-after/7-`, `8-`
and `9-chart-legend-*.png`.

Why Maintenance stays under half: its chart Area is 606 px wide, so the
six compartment entries take three rows and the heading two. The next lever
is the statement of the window ("whole run so far, 15 minutes shown"), which
could join the time axis's title below the plot and free one more row in
both chart Views. The side column was not taken: it would narrow a time
plot that is already 690 px wide at 1366 px, and it needs a layout that
switches with the Area's shape. Both are left for `PL-2V6V`'s grey-box
layouts.

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

Docs checked: `docs/INTERFACE.md` (§ "Minimum displayed outputs", the MAC-awake
band's two numbers; § "MAC-awake as a chart reference"; § "The chart's time
base"), `docs/MODEL.md` (no mention of where the reference values sit),
`README.md` and `docs/ARCHITECTURE.md` (neither describes the legend rows), and
the docstrings of `ConcentrationView`, `_KeyScroll`, `mac_awake_caption`,
`format_mac_awake_reference`, `FlowLayout` and `theme.CHART_KEY_LEAST_HEIGHT`.
