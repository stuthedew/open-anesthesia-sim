---
id: PL-PHPZ
title: The page lays the Areas out at a size hint cached before the Views drew, so a View that fills in later leaves the Areas at their least height instead of the height they ask for
priority: P3
effort: S
status: done
classes: defect, ux
feature: interface-areas
touches: src/anesthesia_sim/app/area_layout.py, tests/integration/test_simulation_view.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 triage pass
added: 2026-10-19
closed: 2026-10-19
pr: 1686
payoff: the page height no longer depends on whether the Views had drawn when it was laid out, so the Areas stand at the height they ask for
verify: grep -q 'def test_the_page_takes_the_height_the_areas_ask_for_after_the_views_draw' tests/integration/test_simulation_view.py
---

**Problem.** The dashboard's scrolling page lays out the Areas from the size hint that `AreaLayout` gave before any View had drawn. `ParameterControlsView` and `AccountingView` build their per-run copies on their first frame, which makes the Areas' hint taller. Nothing calls `updateGeometry` on `AreaLayout` then, so its parent layout keeps the old hint. The Areas therefore stand at their least height, `minimumSizeHint`, rather than the height they ask for.

**Measured** on 2026-10-19 with the setting controls in an Area above the charts, at 1600 x 1000: `AreaLayout.height()` was 1134 px and `sizeHint().height()` 1163 px, and the parent layout's item reported 1134 px. Calling `updateGeometry()` on the `AreaLayout` moved the page to 1149 px for a hint of 1148 px.

**Why it matters.** Nothing is cut off, because each Area still gets its View's need. But the page's height depends on whether the Views had drawn when it was laid out, which is hidden state, and `test_spare_height_goes_to_the_plots_and_not_to_the_readouts` had to drop its check of the preferred height to pass.

**Done when** `AreaLayout` tells its parent when its hint changes, for instance by calling `updateGeometry` after a refresh that built copies, and that test checks the preferred height again.

**Checked 2026-10-19.** In the default Workspace on `main` at `1e5cb9bd`, at
1400 by 1000 offscreen, `AreaLayout.height()` and `sizeHint().height()` were
both 665 px after one event-loop pass, so the default layout does not show the
gap. The case needs the setting controls in an Area above the charts, as the
measurement above used; this pass did not rebuild that layout, so that
measurement is still the evidence. `PL-4L8B` is the same mechanism on the
horizontal axis, reproduced the same day.

The test the work adds for that check is the one `verify:` names.

**Fixed 2026-10-19, with `PL-YJ21`.** `AreaLayout.follow_needs` calls
`updateGeometry` whenever a frame changes a View's need, and hands out the
layout requests that follow, so the page lays the Areas out at their current
hint before the frame returns. Measured in `_EVERY_VIEW` at 1400 by 1000, the
case the brief names: before the fix the Areas stood at 1179 px for a hint of
1241 px after the first frame, and at 1241 px for a hint of 1196 px after the
event loop ran. After it they stand at 1196 px for 1196 px at both moments.

`test_spare_height_goes_to_the_plots_and_not_to_the_readouts` checks the
preferred height again. The new
`test_the_page_takes_the_height_the_areas_ask_for_after_the_views_draw` fails
on the code before the fix with `assert 1179 == 1241`.
