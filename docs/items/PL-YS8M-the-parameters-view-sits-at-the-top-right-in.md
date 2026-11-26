---
id: PL-YS8M
title: The Parameters View sits at the top right in the Default Workspace but under the chart on the left in Induction and Maintenance, so the controls move when the reader switches tabs
priority: P2
effort: S
status: needs-decision
classes: ux
feature: interface-design-review
touches: src/anesthesia_sim/data/workspaces/default.json
deferred-from: v0.7.0 - filed 2026-11-26, after the gate froze. Hazard not live, checked 2026-11-26 at 971a9cb9: the controls change place between tabs, but every value and control is on screen in each Workspace; it can still land before the cut
added: 2026-11-26
payoff: a reader switching Workspace tabs finds the setting controls in the same place every time
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

**Generator check.** No generator. The three shipped Workspaces were composed in separate items (`PL-KXTL`, `PL-L59K`), and nothing compared where they put the same View. The test this item adds is that comparison.

**Done when.** The Parameters View is in the same place
in every shipped Workspace, and a test fails if a shipped Workspace puts it
anywhere else.
