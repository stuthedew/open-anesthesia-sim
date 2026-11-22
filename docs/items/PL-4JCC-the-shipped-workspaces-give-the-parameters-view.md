---
id: PL-4JCC
title: The shipped Workspaces give the Parameters View an Area far taller than its content: 590 by 665 px in Default and 590 by 1083 px in Induction for about 90 px of controls (measured offscreen at 1920 by 1080, 2026-11-11), while no shipped Workspace but Maintenance shows a third View
priority: P3
effort: S
status: ready
classes: ux
feature: window-is-the-frame
touches: src/anesthesia_sim/data/workspaces/default.json, src/anesthesia_sim/data/workspaces/induction.json, tests/integration/simulation_view/test_simulation_view_page.py
added: 2026-11-11
payoff: at 1920 by 1080 the chart beside the Parameters View gets the height that the controls do not use
verify: grep -q 'def test_the_parameters_area_is_not_far_taller_than_its_controls' tests/integration/simulation_view/test_simulation_view_page.py
---

**Problem.** The shipped Workspaces give the Parameters View an Area far taller than its content: 590 by 665 px in Default and 590 by 1083 px in Induction for about 90 px of controls (measured offscreen at 1920 by 1080, 2026-11-11), while no shipped Workspace but Maintenance shows a third View

[superseded 2026-11-14] **Triaged, 2026-11-11: waits for `PL-CBYS`.** Since `PL-9YPR`, the column
that held Parameters alone is shared with Bookmarks and Branch in Default and
Induction, so the Parameters Area is about a third of the height it was.
`PL-CBYS` then changes every Area's height again. Measure once that has
landed, and close this item if the Area is no longer far taller than its
controls. Where the Views sit is a placeholder that the session decides.

**Why it matters.** Empty panel beside a chart is room the chart could use.

**Generator check.** A one-off: a placement chosen before a third View
existed to share the column.

**Measured after `PL-CBYS`, 2026-11-14** (offscreen font, one run at 300 s,
on `#2134`'s branch). The Parameters View's content needs 86 px. Its Area is
187 px tall at 1366 by 768 in every shipped Workspace, held at the View's
least height of 160 px plus the header. At 1920 by 1080 it is 266 px in
Default and Induction and 187 px in Maintenance, about 180 px more than the
controls in the first two. The Area is no longer the 665 px and 1083 px the
title records, but it is still about three times its content on a desktop
screen, so the item stays open.

**Done when.** At 1920 by 1080 the Parameters Area in Default and Induction
is no more than its View's least height plus the header, and the room it gives
up goes to the chart beside it. A test opens each shipped Workspace at that
size and checks the Area's height. The shares stay placeholders that the
building session decides.

**Checked 2026-11-22** against `d4e8200`: still applies. No commit since #2134, the branch the 2026-11-14 measurement was taken on, has changed `data/workspaces/`, so the Parameters Area should still be about 180 px taller than its controls at 1920 by 1080. No test named `test_the_parameters_area_is_not_far_taller_than_its_controls` exists.

**Built, 2026-11-22, with `PL-D5J4`, `PL-4JCC` and `PL-V4Q8` in one pull request.**
All three change the shipped Workspaces' splits and the Parameters View, so
they were measured and decided together, offscreen, at 1366 by 768 and 1920 by
1080, with one run at 300 s. The heights each lesson needs below its Area's
header, at 1366 by 768: the wash-in plot ends 236 px into its View, the share
bar 352 px into the schematic, and the Edit bookmarks button 134 px into the
Bookmarks View. The Areas get 488 px in all. So the wash-in chart cannot sit
under the concentration chart (whose least height is 280 px), and the
schematic cannot share its column with anything taller than the Branch View.

What changed, all of it placement and look, decided as placeholders:

1. Each setting card shows its value (and the delivered dial's MAC multiple)
   on a row of its own above the slider, so the slider takes the card's whole
   width. The slider is never shorter than `theme.PARAMETER_SLIDER_LEAST_LENGTH`,
   90 px. A longer least length makes the Parameters View wider than
   Maintenance leaves it beside the schematic at 1366 px: at 120 px and at
   100 px the page scrolled sideways there.
2. The Parameters View's declared least height is 110 px, its row measured at
   106 px, down from 160. The Branch View's is 60 px, its content measured at
   57 px, down from the shared 110.
3. Default: the chart at full height, and on the right Parameters (share 0.1,
   so held at its least height), Bookmarks and Branch. Induction: chart over
   Parameters on the left half, wash-in over Bookmarks beside Branch on the
   right half. Maintenance: chart over Parameters on the left half, schematic
   over Branch on the right half. Maintenance no longer shows the Bookmarks
   View, because the schematic needs 379 px of the 488 and the Bookmarks View
   needs 161 px to show its button. A reader brings it back with the View
   chooser.
4. The Parameters and Branch Views' registry entries set `whole`, so the
   adapter holds each Area at its View's whole content height where that is
   more than the declared least height (`area_layout._view_need`). Review
   found that with a branch open the Parameters View shows two rows of dials
   in 224 px, and a 110 px Area hid the second run's row in every Workspace.
   Main had shown both rows at 1920 by 1080. With `whole`, the Area grows to
   hold both rows; at 1366 by 768 the page may then grow and scroll, which is
   the existing rule for a window too small for every View's need.

Measured after, at 1366 by 768: the wash-in plot, the share bar and the Edit
bookmarks button are wholly on screen in each Workspace that shows them; the
shortest slider is 104 px (Default and Maintenance) and 128 px (Induction);
the Parameters Area is 110 px below its header in every Workspace at both
sizes. Still scrolled at 1366 by 768: the schematic's three lines under the
share bar (52 px), and 3 px of the Induction Bookmarks View under its button.
The concentration chart in Induction and Maintenance is 316 px below its
header, so its legend rows scroll in the box above the plot, as Induction's
did before.

Each new test failed on `f8424d3` (main before this branch), run with the
branch's test file and the least length written as 90:
`test_each_shipped_workspace_shows_its_lesson_whole_at_1366_by_768` failed
"the Edit bookmarks is not wholly on screen in Default", "the wash-in plot is
not wholly on screen in Induction", and for Maintenance on the set of widgets
shown; `test_the_parameters_area_is_not_far_taller_than_its_controls` failed
"assert 239 <= 160" in Default and Induction at 1920 by 1080; and
`test_every_parameter_slider_is_long_enough_to_drag_at_1366_by_768` failed
"assert 52 >= 90", "assert 52 >= 90" and "assert 84 >= 90".
`test_the_parameters_area_shows_both_runs_dials_once_a_branch_is_taken`
failed "assert 114 == 0" on this branch with `whole` set to `False` on both
entries. `test_a_narrow_setting_card_keeps_its_slider_long_enough_to_drag`
failed "cardiac_output, assert 88 >= 90" with the slider's least width
removed. `test_an_entry_refuses_a_whole_flag_that_is_not_a_bool` and
`test_only_the_parameters_and_branch_views_hold_their_whole_content` pin the
new field.

Docs checked: `docs/INTERFACE.md` (four "readout beside its slider"
sentences now say above, and § "F_A/F_I as a displayed ratio" now says the
plot is beside the chart), `docs/INTERFACE.md` § on reachable Views (the Parameters and Branch Views
never scroll), `docs/VERIFICATION.md` (one table row's "beside a dial" now
says above; the row moved there from `docs/MODEL.md` on main), the
docstrings and comments in `app/controller.py`, `app/dashboard_frame.py`,
`app/display_units.py`, `app/formatting.py`, `app/qt_chart.py`,
`app/qt_widgets.py` and `app/view_registry.py`, `README.md` (the bookmarks are in Default and Induction),
`src/anesthesia_sim/data/workspaces/__init__.py` (each Workspace's
arrangement), `docs/ARCHITECTURE.md` and `docs/interface-provenance.md` (no
statement about the shipped arrangements or the card layout).
