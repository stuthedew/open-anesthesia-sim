---
id: PL-YS8M
title: The Parameters View sits at the top right in the Default Workspace but under the chart on the left in Induction and Maintenance, so the controls move when the reader switches tabs
priority: P2
effort: S
status: done
classes: ux
feature: interface-design-review
touches: src/anesthesia_sim/data/workspaces/default.json, src/anesthesia_sim/data/workspaces/induction.json, src/anesthesia_sim/data/workspaces/maintenance.json, src/anesthesia_sim/data/workspaces/__init__.py, src/anesthesia_sim/app/qt_schematic.py
deferred-from: v0.7.0 - filed 2026-11-26, after the gate froze. Hazard not live, checked 2026-11-26 at 971a9cb9: the controls change place between tabs, but every value and control is on screen in each Workspace; it can still land before the cut
added: 2026-11-26
closed: 2026-11-26
pr: 2325
payoff: a reader switching Workspace tabs finds the setting controls in the same place every time
tests: tests/unit/test_layout_shipped.py::test_every_shipped_workspace_puts_the_parameter_controls_at_the_top_of_the_right_column, tests/integration/simulation_view/test_simulation_view_page.py::test_the_parameter_controls_stand_where_they_did_after_a_tab_switch, tests/integration/simulation_view/test_simulation_view_page.py::test_the_share_bar_is_never_on_screen_without_the_lines_that_name_its_segments
---

**Problem.** The Parameters View is the top-right Area of the Default
Workspace (`src/anesthesia_sim/data/workspaces/default.json`), but the strip
under the concentration chart on the left in the Induction and Maintenance
Workspaces. A reader who switches tabs finds the controls somewhere else. The
project owner found this on 2026-11-26 before his v0.7.0 test drive: "I don't
like how the controls move between tabs."

**Why it matters.** A reader who changes a setting after switching Workspaces has to search for the control first, and may reach for an empty place. The setting controls change the run, so they are the controls a reader most needs to find without looking.

**Best practice.** Read on 2026-11-26:

1. Nielsen Norman Group's consistency heuristic says to decide where page and
   button elements live and keep them in the same place on every page where
   that applies (Krause R, "Maintain Consistency and Adhere to Standards
   (Usability Heuristic #4)", 10 January 2021,
   https://www.nngroup.com/articles/consistency-and-standards/, full text).
2. Items that keep a fixed position are found again faster, because readers
   learn where they are (Gutwin C, Van Der Kamp M, Storring J, Cockburn A,
   Phillips C, "Testing the Limits of the Spatial Approach", Graphics Interface
   2020, https://graphicsinterface.org/wp-content/uploads/gi2020-22.pdf; full
   text read through section 5.1.2). Scarr et al., CHI 2013,
   doi:10.1145/2470654.2466430, reaches the same conclusion, but only its
   abstract was read.
3. Blender's manual page on workspaces could not be read: docs.blender.org
   refuses automated fetching.

**Measured 2026-11-26: both placements break a 1366 by 768 requirement.**
Each was tried in the shipped files and run against the laptop-screen tests.

1. Parameters under the chart in all three (only `default.json` changes). The
   Default plot falls to 160 px of a 337 px Area, below the half that
   `test_the_concentration_plot_takes_half_its_area_on_a_laptop` requires
   (`PL-K4CZ`), and the keyboard-resize test of the controls Area fails.
2. Parameters at the top of the right column in all three (Induction and
   Maintenance change). Induction's wash-in plot and Maintenance's share bar
   no longer fit on screen without scrolling, which
   `test_each_shipped_workspace_shows_its_lesson_whole_at_1366_by_768`
   requires (`PL-D5J4`).

**Decision needed.** Which cost to take is the owner's, because each changes what a
reader sees on the smallest supported screen. Recommendation: option 1. Its
cost is a shorter Default plot on a 1366 by 768 screen only, with everything
still on screen. Option 2 pushes a required part of two Views below the fold,
and hiding a value is worse than shrinking it. The Default plot's half-Area
bar would then be relaxed for that screen size, with the reason recorded.

**Answered 2026-11-26** (project owner, 2026-11-26, over putting the
controls under the chart and over leaving them as they were): the controls go
at the top of the right-hand column in every shipped Workspace, accepting that
at 1366 by 768 the wash-in plot and the share bar scroll inside their Areas.

**Built.** Induction and Maintenance now give the chart the left half at full
height, with the Parameters View first in the right-hand column. Induction's
column is 0.1, 0.65 and 0.25, which gives the wash-in plot room to fit whole
from 1440 by 900 up. Measured under both the container font and DejaVu Sans,
the font the test machines draw with: the wash-in plot and the share bar fit
whole at 1440 by 900 and 1920 by 1080, and scroll inside their Areas at 1366
by 768, because the Parameters, Bookmarks and Branch Areas each sit at their
least height there. The lesson test moved from 1366 by 768 to 1440 by 900 with
the owner's decision in its docstring. Two Induction tests whose setting was a
squeezed chart were updated: the chart now has the full height, so its legend
box no longer scrolls and its Area cannot grow further.

**Review, 2026-11-26.** Two blind review passes found five things, and all five were fixed on the branch.

1. The controls still moved. Default split the row 0.7 to 0.3 and the other two 0.5 to 0.5, so at 1920 by 1080 the controls' left edge moved by 376 px between tabs. Every shipped Workspace now splits the row 0.6 to 0.4. At 1920 by 1080 the Parameters Area is then 752 px wide at x 1152 in all three. At 1366 by 768 each right-hand column is as wide as its widest View needs: 541 px in Default, 640 in Induction and 720 in Maintenance (Inter; 550, 661 and 750 in DejaVu Sans). An exact match there would need every column at 750 px, and Default's chart at 600 px wide fails the rule that its plot takes at least half its Area (`PL-K4CZ`): measured 195 px of plot in a 482 px Area at 0.43 to 0.57. So the Area keeps its top and right edges at laptop sizes, and `test_the_parameter_controls_stand_where_they_did_after_a_tab_switch` checks the edges at both sizes and the whole Area at 1920 by 1080. It failed against the 0.7 and 0.5 shares.
2. Maintenance's share bar could be on screen without the lines that name its segments. At 1366 by 768 the schematic scrolled, and the Area's lower edge fell between the bar and its lines at 34 scroll positions. The bar and its lines are now the schematic's first rows under its name line. `test_the_share_bar_is_never_on_screen_without_the_lines_that_name_its_segments` failed against the old row order, at scroll 26 of 108. The two-run case predates this item and is `PL-P83G`.
3. The 1 MAC row test lost its premise when the chart got the full height. It now runs in Maintenance with a branch open at 1366 by 768, where the legend box scrolls (83 px in Inter, 78 in DejaVu Sans), and checks that it does.
4. The page scroll bar test's heights no longer straddled the height at which Induction with a branch stops needing the page to scroll. That height moved from about 1,060 px to 1,016 px (1,020 in DejaVu Sans), and the range is now 1,000 to 1,036.
5. The package docstring of `src/anesthesia_sim/data/workspaces/` described the old layouts. It now describes these.

The lesson test now runs at each size where the lesson fits with one run: Maintenance from 1366 by 768, Induction at 1440 by 900 and 1920 by 1080. Induction's wash-in plot scrolls at 1536 by 864 too. With a branch open, the Parameters Area grows to a second row, and the wash-in plot scrolls at every tested size. On `main` it fitted with a branch open. Its "modelled" line is pinned above the scroll box, so the plot is never on screen without it (`PL-26BZ`).

**Generator check.** No generator. The three shipped Workspaces were composed in separate items (`PL-KXTL`, `PL-L59K`), and nothing compared where they put the same View. The test this item adds is that comparison.

**Done when.** The Parameters View is in the same place
in every shipped Workspace, and a test fails if a shipped Workspace puts it
anywhere else.
