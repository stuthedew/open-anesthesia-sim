---
id: PL-PHPZ
title: The page lays the Areas out at a size hint cached before the Views drew, so a View that fills in later leaves the Areas at their least height instead of the height they ask for
status: untriaged
feature: interface-areas
added: 2026-10-19
---

**Problem.** The dashboard's scrolling page lays out the Areas from the size hint that `AreaLayout` gave before any View had drawn. `ParameterControlsView` and `AccountingView` build their per-run copies on their first frame, which makes the Areas' hint taller. Nothing calls `updateGeometry` on `AreaLayout` then, so its parent layout keeps the old hint. The Areas therefore stand at their least height, `minimumSizeHint`, rather than the height they ask for.

**Measured** on 2026-10-19 with the setting controls in an Area above the charts, at 1600 x 1000: `AreaLayout.height()` was 1134 px and `sizeHint().height()` 1163 px, and the parent layout's item reported 1134 px. Calling `updateGeometry()` on the `AreaLayout` moved the page to 1149 px for a hint of 1148 px.

**Why it matters.** Nothing is cut off, because each Area still gets its View's need. But the page's height depends on whether the Views had drawn when it was laid out, which is hidden state, and `test_spare_height_goes_to_the_plots_and_not_to_the_readouts` had to drop its check of the preferred height to pass.

**Done when** `AreaLayout` tells its parent when its hint changes, for instance by calling `updateGeometry` after a refresh that built copies, and that test checks the preferred height again.
