---
id: PL-CBYS
title: The page still scrolls at every common screen size, though PL-JG82's brief says v0.6.0 removes the page scroll: the Areas and the marks and branch section sit in one scrolling page, which measured offscreen on 2026-11-11 scrolls 414 px (Default) and 832 px (Induction) at 1366 by 768, and 102 px and 520 px at 1920 by 1080, so the Induction Workspace's wash-in chart opens below the fold; decide whether the Areas fill exactly the space between the unconditional region and the disclaimer, as a Blender window's Areas fill the window
priority: P2
effort: M
status: ready
classes: feature, ux
feature: window-is-the-frame
touches: src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/views.py, docs/MODEL.md, src/anesthesia_sim/app/view_registry.py, src/anesthesia_sim/app/theme.py, src/anesthesia_sim/app/qt_chart.py, src/anesthesia_sim/layout/sizing.py, src/anesthesia_sim/data/workspaces, README.md, docs/ARCHITECTURE.md, docs/interface-provenance.md, .claude/rules/ui-areas.md
deferred-from: v0.7.0 - the gate's frozen list does not name it, and it is built after PL-9YPR's pull request merges
added: 2026-11-11
payoff: every shipped Workspace fits the window on a laptop, so the Induction wash-in chart opens on screen and not below the fold
verify: grep -q 'def test_no_shipped_workspace_scrolls_the_page' tests/integration/test_simulation_view.py
---

**Problem.** The page still scrolls at every common screen size, though PL-JG82's brief says v0.6.0 removes the page scroll: the Areas and the marks and branch section sit in one scrolling page, which measured offscreen on 2026-11-11 scrolls 414 px (Default) and 832 px (Induction) at 1366 by 768, and 102 px and 520 px at 1920 by 1080, so the Induction Workspace's wash-in chart opens below the fold; decide whether the Areas fill exactly the space between the unconditional region and the disclaimer, as a Blender window's Areas fill the window

**Measured, offscreen font, 2026-11-11** (`main.open_dashboard`, one run at
5 minutes). "Room" is the height between the unconditional region and the
disclaimer. "Scroll" is the page scroll bar's range.

| Window | Workspace | Room | Areas drawn | Areas' minimum | Scroll |
| --- | --- | --- | --- | --- | --- |
| 1366 by 768 | Default | 515 px | 665 px | 591 px | 414 px |
| 1366 by 768 | Induction | 515 px | 1083 px | 999 px | 832 px |
| 1920 by 1080 | Default | 827 px | 665 px | 591 px | 102 px |
| 1920 by 1080 | Induction | 827 px | 1083 px | 999 px | 520 px |
| 2560 by 1440 | Default | 1187 px | 923 px | 591 px | 0 px |
| 2560 by 1440 | Induction | 1187 px | 1083 px | 999 px | 160 px |

Maintenance measured the same as Default at each size. No Area showed its
too-small notice at any size, because the page grows instead (`PL-K285` Q2:
"the dashboard's page is a `QScrollArea`, so it grows to that and scrolls").

**Why it is a departure from Blender.** In Blender the window's rectangle is
the layout: the Areas divide it exactly, and nothing scrolls at the window
level. Here the Areas' minimum heights add up to more than the window, the page
grows to hold them, and the marks and branch section (`PL-9YPR`) adds its
height under them. A Workspace is then a page a learner scrolls, and a border
drag changes the page's length as well as the Areas' shares.

**Decided: make the window the frame** (project owner, 2026-11-11, ratified,
over keeping the page that grows and scrolls, which `PL-K285` Q2 built). The
owner agreed to the session's recommendation, in three steps that each stand
alone:

1. Make the marks panel and the branch control Views (`PL-9YPR`), so nothing
   but Areas sits between the region and the disclaimer.
2. Give the Areas exactly the room between the region and the disclaimer. A
   View whose content needs more height than its Area scrolls inside its own
   Area, as a Blender editor scrolls its own regions.
3. Lower the concentration chart View's minimum height, 558 px with one run,
   by moving its legend and reference rows beside the plot or behind a
   disclosure. That is the visual pass's work (planned-milestone item 33).

What it costs: step 2 changes `PL-K285` Q2's ratified answer and what a
learner sees on a laptop, so it is the owner's decision. The Induction
Workspace's two stacked charts cannot both hold their present minimum in
515 px, so one of them scrolls inside its Area or the Workspace is recomposed.

**What the decision leaves to the building session.** No mock-up was shown
before the owner agreed, so the first build step renders the result beside
today's screen at 1366 by 768 and 1920 by 1080. How the Induction Workspace's
two charts share 515 px is still open: one chart scrolls inside its Area, or
the Workspace is recomposed. This item needs triage and a split into build
items for steps 1 and 2 before work starts.

**Triaged, 2026-11-11: this item is now step 2, the build.** Step 1 is
`PL-9YPR`, built on pull request `#2103`. Step 3 stays with the visual pass
(planned-milestone item 33).

**Why it matters.** On a 1366 by 768 laptop the Induction Workspace's wash-in
chart opens below the fold, and a border drag changes the page's length as
well as the Areas' shares. A learner arranges a page, where the design they
were promised is a window.

**Done when.** The session first renders a mock-up at 1366 by 768 and 1920 by
1080, Induction Workspace in both, and the owner has seen it. Then the Areas
take exactly the room between the unconditional region and the disclaimer,
the page scroll bar has no range at either size in any shipped Workspace, and
a View that needs more height than its Area scrolls inside the Area. The
scroll that `PL-9YPR` put inside `_CasePanelView` moves into the container.
`docs/MODEL.md` and `PL-K285`'s recorded answer are updated to match.

**Generator check.** A one-off. It reopens a ratified answer (`PL-K285` Q2)
on a measurement, and no reader misread a fact.

**The mock-up, 2026-11-11, and the question it raised.** Rendered from the
branch with a patch in the render script (scratch only, nothing built): the
Areas take exactly the room, a plot may shrink to 160 px (concentrations) or
120 px (wash-in), and a View taller than its Area scrolls inside it. Same run
in every picture, 2% sevoflurane at 5 minutes. Measured:

- At 1366 by 768 the Areas get 1334 by 488 px. The band of readouts, the tab
  strip and the disclaimer take the other 280 px of height.
- The concentration chart's heading, reference lines and legend take about
  250 px above its plot. The wash-in chart's take about 170 px.
- Induction as shipped, at 1366 by 768: the chart's Area has 261 px and the
  wash-in's has 173 px. Each chart scrolls inside its Area (151 px and
  128 px), and neither plot is on screen until the learner scrolls. Stacked,
  the two charts cannot both show a plot in 488 px whatever the plot's floor:
  the text above the two plots and the two Area headers take about 300 px.
- Induction with the charts side by side (shares 0.34, 0.25, 0.41), and the
  rule that a chart keeps its plot in view while the block above it scrolls
  on its own: both plots are on screen at 1366 by 768 (218 px and 164 px
  tall), and the legend blocks scroll 114 px and 41 px.
- At 1920 by 1080 nothing scrolls in either arrangement. Stacked gives plots
  about 1280 px wide; side by side gives plots about 540 px and 390 px wide
  and 380 px and 480 px tall.
- The Parameters View needs 590 px of width for its four controls in one row.
  In a quarter-width column at 1366 px it scrolls 50 px sideways. That is
  `PL-4JCC`'s to fix by letting the controls wrap.
- Maintenance at 1366 by 768: the schematic needs 358 px and its Area has
  137 px. It needs a taller Area, a placeholder choice for the building
  session.

**The question put to the owner, answered below.** Which Induction ships? A learner on a laptop sees one
of these when they open Induction.

- A. Charts side by side at every window size. Both curves are on screen at
  1366 by 768. On a large monitor each plot is narrower than today.
- B. Charts stacked, as shipped. On a large monitor the plots are wide. At
  1366 by 768 neither curve is on screen until the learner scrolls inside
  each Area.

**Recommendation:** A. Induction exists to show the wash-in beside the
concentrations, and B hides both curves on the commonest laptop size. A
learner with a large monitor can drag the charts into a stack and save that
layout; a learner on a laptop cannot make room that is not there. Either
answer gets the plot-stays-in-view rule for both charts, which the session
decides as a placeholder.

**Decided: the charts stay stacked and the concentration chart keeps its
long time axis** (project owner, 2026-11-11: "I like the long graph of the
main anesthetic. Not side by side"). The owner chose this after seeing both
mock-ups, against the session's recommendation of A. It is specified, so it
reopens only on a compelling argument.

**What the session decides inside that answer, as placeholders.** A second
mock-up, sent to the owner the same day, shows these on Induction:

- The concentration chart keeps its plot on screen. Its legend block
  scrolls in its own box above the plot.
- At 1366 by 768 the two stacked charts need about 520 px and the Areas have
  488 px. The concentration chart gets the room its plot needs (300 px in the
  mock-up, plot 160 px). The wash-in Area gets the rest (126 px) and scrolls
  122 px inside itself. A learner who wants the wash-in curve scrolls that
  Area, drags the border between the two, or uses Maximize Area once
  `PL-VJD2` builds it.
- At 1920 by 1080 nothing scrolls. The wash-in plot is short there (about
  70 px in the first mock-up), so the build gives it a larger share of the
  column's height.
- The Areas report only their floors, so the page never scrolls.

**From the review of `PL-9YPR`, 2026-11-11.** The branch View declares a
minimum width of 220 px in `view_registry.py`, and its row of selector and
button needs about 308 px. At the narrowest Area a border drag reaches, the
Branch button is behind a sideways scroll. Set the declared minimum from what
the row needs when this item decides the room each Area gets.

**Build plan, 2026-11-11, from reading the code before any edit.** Nothing is
built yet. The plan keeps one rule for every View, so no View gets a
capability of its own.

1. **What an Area's need means.** `AreaLayout._view_need` in
   `app/area_layout.py` returns the larger of the registry's declared minimum
   and the widget's Qt minimum. Change it to return the declared minimum
   alone. The declared minimum becomes the least room in which a View is
   shown at all. In a smaller Area the too-small notice still shows. Between
   the declared minimum and the widget's Qt minimum, the View scrolls inside
   its Area. `layout/sizing.py` needs no change to its logic, only to the
   sentences of its module docstring that say a View is never clipped and
   that a host grows to hold every need.
2. **The scroll inside each Area.** `AreaFrame` wraps a View, and not an
   `AreaNotice`, in a scroll area of its own. Keep `frame.content` as the
   View, because 44 test lines read it, and show or hide the wrapper where
   the frame now shows or hides `content`. The wrapper must size the View to
   the larger of its viewport and the View's `minimumSizeHint`. A plain
   `QScrollArea` with `setWidgetResizable(True)` gives a height-for-width
   layout its preferred height, so the wash-in View scrolled more than it
   needed in the mock-up. The mock-up's `Fit` class in the scratch script
   overrode `resizeEvent` to do the sizing, and the build does the same.
   Remove the scroll area inside `views._CasePanelView`.
3. **What the Areas tell the page.** `AreaLayout._settle` reports
   `minimum_extent` of the needs through `minimumSizeHint`, and the page's
   scroll area grows to it. Report the `minimum_extent` of each Area's floor
   at the floor's own width instead. The page then never grows past the
   window while the floors fit, and `settle` shows the too-small notice in an
   Area that cannot have its need, as it already does in a host that cannot
   grow. The page's scroll area stays as the fallback for a window smaller
   than the floors, so `SimulationView`'s code that keeps the chart in view
   stays as it is.
4. **The two charts.** In `views.ConcentrationView` and `views.WashInView`,
   move the time-axis caption, the reference lines, the legend and the
   hidden-trace and capped-trace lines into one box that scrolls above the
   plot (least height 34 px in the mock-up, vertical policy Maximum, stretch
   2 against the plot's 3). Add a least plot height to `app/theme.py`, 160 px
   for the concentration plot and 120 px for the wash-in plot, and use it in
   `qt_chart.py` where the plot's minimum height is now `CHART_HEIGHT` and
   `WASH_IN_CHART_HEIGHT`. The preferred heights stay.
5. **Declared minimums in `app/view_registry.py`, as placeholders.** The
   concentration chart's height is what its folded layout needs with one run,
   about 300 px, to be measured. Every other View is 120 px high. The Branch
   View's width is what its row needs, about 308 px. Rewrite the module
   docstring's paragraph on the declared size and `RegisteredView.minimum`.
6. **Shipped Workspaces in `data/workspaces/`.** Induction's left column is
   0.6 and 0.4 now. Give the wash-in a larger share so its plot is not short
   at 1920 by 1080, and check that at 1366 by 768 the chart is held at its
   need and the wash-in scrolls inside its Area. Give Maintenance's schematic
   a taller Area (it needs 358 px). Measure all three Workspaces at both
   sizes and put the table here.
7. **Tests.** The page's scroll bar has no range in any shipped Workspace at
   1366 by 768 and 1920 by 1080. A View taller than its Area scrolls inside
   the Area and stays shown. An Area below its declared minimum still shows
   the notice. The concentration plot is on screen in Induction at 1366 by
   768. A View kept across a split is still shown in its new frame. Tests
   that give a View its need through the widget's minimum size, and not
   through the registry, change to declare it.
8. **Documents.** `docs/MODEL.md`, `README.md` § "The window",
   `docs/ARCHITECTURE.md`, `docs/interface-provenance.md`,
   `.claude/rules/ui-areas.md` answer 4, and a dated note in `PL-K285` that
   its Q2 answer changed here.

The second mock-up's script is not in the repository. It patched
`AreaLayout._content_for` and `_view_need` and the two chart Views'
constructors, as steps 1, 2 and 4 describe.

**Built so far, 2026-11-11 (commit `cb76d6cb1`), and where the build left the
plan.** Steps 1, 2, 4, 5 and 6 are built. Step 3 was not built, and steps 7 and
8 are still to do.

1. **Step 3 is dropped: the page can still grow.** `AreaLayout` still reports
   the sum of the Areas' needs to the page, as `PL-K285` Q2 decided. The needs
   are now small, so the page does not grow at 1366 by 768 or 1920 by 1080.
   Reporting only the floors would have shown a too-small notice in place of a
   View in a small window. `docs/MODEL.md` § "Minimum displayed outputs" says
   that a reader who chooses a View "sees the view itself, never only a notice
   that the area is too small", and the agent accounting must stay reachable
   that way. So `PL-K285` Q2's answer is not changed, and step 8 needs no note
   in `PL-K285`.
2. **An Area's least width comes from its View's content** (step 1 changed).
   The need is the declared height, and the larger of the declared width and
   the least width of the View's widget plus the scroll bar's width. With the
   declared width alone, the Parameters row of four controls scrolled sideways
   in a 331 px Area. A declared number for that row would also be a second
   copy of a width that depends on the font. `PL-4JCC` (the Parameters row
   wraps) then narrows the Area with no change to the registry.
3. **The chart Views** (step 4). `views._KeyScroll` holds the statement of the
   window, the reference values and the legend, and scrolls them above the
   plot. Its least height is `theme.CHART_KEY_LEAST_HEIGHT`, 36 px, which
   shows the first two rows. The advisories stay outside the box: no traces
   shown, traces capped, traces above the axis, unmarked control changes and
   the wash-in state lines. The mock-up had the first two inside it. They are
   conditional text, and a reader must see one as soon as it applies.
4. **Placeholders chosen** (steps 5 and 6): least plot heights 160 px and
   120 px; least View height 120 px, except the concentration chart at 280 px
   (its content measured 275 px offscreen) and Parameters at 160 px (one run's
   row of controls); Maintenance's right column 0.52, 0.2, 0.28, so the
   schematic has its 358 px at 1920 by 1080. Induction's 0.6 and 0.4 are
   kept, because the concentration plot needs the height to separate six
   traces and the wash-in plot has one trace.
5. **Measured offscreen at 300 s of one run, 2026-11-11.** The page's scroll
   range is 0 in all three Workspaces at both sizes, and no View scrolls
   sideways.

   | Window | Workspace | Views that scroll inside their Area |
   | --- | --- | --- |
   | 1366 by 768 | Default | Bookmarks, by 24 px |
   | 1366 by 768 | Induction | Wash-in by 85 px, Bookmarks by 24 px |
   | 1366 by 768 | Maintenance | Schematic by 228 px, Bookmarks by 29 px |
   | 1920 by 1080 | Default, Induction, Maintenance | none |

**Still to do.**

- Step 7, tests. The whole suite was started after `cb76d6cb1` and its result
  is not yet read. Expect failures where a test gives a View its need through
  the widget's minimum height, where a test reads `scroll_area` on the
  Bookmarks or Branch View (removed), and where a test expects a plot of 360
  or 200 px. New tests: the plan's list, with "the page grows only where the
  window is too small for the needs" in place of the notice test.
- Step 8, documents. `docs/MODEL.md`: the sentence "The page grows to give the
  view the space it needs" in § "Minimum displayed outputs" (add that a View
  taller than its Area scrolls inside it), and "the 360 px plot" in the
  paragraph on the linear percent axis (say it is the plot's preferred height,
  and that the plot is 160 px at its least). `README.md` § "The window",
  `docs/ARCHITECTURE.md`, `docs/interface-provenance.md`,
  `.claude/rules/ui-areas.md` answer 4, and `layout/sizing.py`'s module
  docstring (its sentence "never clipped" still holds; say the View scrolls).
- `tools/contrast_check.py` and the dark-appearance test have not been run
  against `stylesheets.clear_scroll_area_stylesheet`.
- The scratch script that measures the table above is not in the repository.
  It opens the dashboard with `main.open_dashboard`, switches Workspaces with
  `view._tabs.activate(index)`, and reads
  `view._page_scroll.verticalScrollBar().maximum()` and each
  `AreaFrame.view_scroll`'s scroll bars.

**The whole suite at `cb76d6cb1`, 2026-11-11:** 12,281 passed, 12 failed and
8 errored. Each needs reading before it is changed: a test may be right and
the build wrong.

- `tests/integration/test_layout_adapter.py`:
  `test_a_layout_of_one_area_is_its_view_alone`,
  `test_a_view_the_new_layout_does_not_hold_leaves_the_container`,
  `test_every_area_has_a_header_whose_chooser_names_its_view`,
  `test_the_header_and_the_rule_are_the_chrome_these_tests_allow_for`.
- `tests/integration/test_layout_keyboard.py`:
  `test_the_controls_area_has_its_least_width_from_the_first_frame`.
- `tests/integration/test_qt_rendering.py`:
  `test_the_hover_reports_the_drawn_state_on_the_shipped_chart`,
  `test_the_hover_box_stays_inside_a_plot_at_its_least_height`.
- `tests/integration/test_simulation_view.py`:
  `test_the_page_stops_holding_the_chart_once_the_reader_scrolls`,
  `test_the_hover_readout_states_the_agent_compartment_and_both_units`,
  `test_every_control_that_paints_its_own_content_declares_a_foreground`,
  `test_spare_height_goes_to_the_plots_and_not_to_the_readouts`,
  `test_the_page_takes_the_height_the_areas_ask_for_after_the_views_draw`.
- All eight tests in `tests/benchmarks/test_frame_cost.py` errored. Whether
  they also error on `main` is not checked.
