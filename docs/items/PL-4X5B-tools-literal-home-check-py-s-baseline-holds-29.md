---
id: PL-4X5B
title: tools/literal_home_check.py's baseline holds 29 bare layout literals in src/anesthesia_sim/app/ (14 in qt_widgets.py, 7 in qt_chart.py, among them 90 three times and 6 three times) and no open item names them
priority: P3
effort: M
status: done
classes: refactor
feature: one-source-of-truth
touches: src/anesthesia_sim/app/, tools/literal_home_check.py
added: 2026-10-19
closed: 2026-10-24
payoff: each layout spacing in the interface has one name, so changing it cannot leave a copy of the old value elsewhere on screen
verify: ! grep -qF '"src/anesthesia_sim/app/' tools/literal_home_check.py
---

**Problem.** tools/literal_home_check.py's baseline holds 29 bare layout literals in src/anesthesia_sim/app/ (14 in qt_widgets.py, 7 in qt_chart.py, among them 90 three times and 6 three times) and no open item names them

**Why it matters.** Each of these numbers is a spacing, margin or angle typed inline. Where one value is meant to match another, such as the three `90`s in `qt_chart.py`, nothing ties them together, so changing one leaves the others at the old value. `tools/literal_home_check.py` already refuses a new bare literal, so the baseline is the only place these copies can still live. It can only shrink, and no item was draining it.

**Checked 2026-10-24.** `BASELINE` holds six `src/anesthesia_sim/app/` keys with 29 entries in all: `chart_frame.py` 2, `dashboard_frame.py` 2, `qt_chart.py` 7, `qt_widgets.py` 14, `run_surfaces.py` 1 and `run_view.py` 3.

**Re-confirmed 2026-10-24, changed shape.** The 29 are not all layout spacings. Read against the tree, they are four kinds:

- Twelve, in `BookmarkDialog._build_layout` in `qt_widgets.py`, are row numbers and the full-width column span of the editor's two form grids. A named constant per row number would be a name for a position, which says nothing a reader can use. So the row and column of each widget come from where it is written in the form, and no number is written at all.
- Ten are spacings in pixels: four in the chart legend in `qt_chart.py`, two in the fork panel in `qt_widgets.py`, one between the setting sliders in `run_surfaces.py`, and three in the run's transport row and readout section in `run_view.py`. These become names in `app/theme.py`, which already holds every other spacing the interface draws.
- Three are `90`, pyqtgraph's angle for a vertical line, in `qt_chart.py`. They become one name in that module, because the convention is the toolkit's and not a display token.
- Four are in the two toolkit-free modules. `percent_axis_ticks` in `chart_frame.py` adds a `1e-9` rounding tolerance, which gets a name there. `nearest_wash_in_point` indexes a tuple at `3`, which unpacking the tuple removes. `slider_position` and `slider_value` in `dashboard_frame.py` raise `10.0` to a number of decimals, and `formatting.py` writes the same base in its three display resolutions, so the base gets one name in `formatting.py`.

**Done when** (rewritten 2026-10-24 for the four kinds above). No bare literal under `src/anesthesia_sim/app/` is left in `BASELINE`: each is a named constant, or gone where it was a position that the code's own order states. `BASELINE` in `tools/literal_home_check.py` has no `src/anesthesia_sim/app/` entry left. The interface looks the same before and after: the default run at 120 s, at a wide and a narrow width, and the bookmark editor, render to identical pixels.

**Generator check.** Bookkeeping. These are the baseline `tools/literal_home_check.py` recorded when it landed under `PL-40SJ`, so they are not new inflow, and nothing has added to them since.

**Done 2026-10-24.** Every value is unchanged, and the four renders named above are pixel-identical before and after. Three choices were the session's, and each is a placeholder until planned-milestone item 33's visual pass:

- Equal spacings share a name only where they are one quantity on screen. `LEGEND_LINE_SPACING` is the gap between two legend rows and also between the lines of a row that wraps, so a wrapped row is spaced like the rows around it. `CONTROL_ROW_SPACING` is the gap between controls on the transport row and on the Branch panel. The other equal values keep separate names: the 6 px between a swatch and its words is `LEGEND_SWATCH_SPACING`, and the 12 px between the sliders and the 12 px along the readout heading are `PARAMETER_SLIDER_SPACING` and `READOUT_HEADING_SPACING`.
- The spacings live in `app/theme.py`, even those that one module uses, because that file's display-tokens header names it the home of the interface's spacing constants. The line angles stay in `qt_chart.py`, because they are pyqtgraph's convention rather than a display choice.
- `DECIMAL_BASE` lives in `formatting.py`, beside the three display resolutions that are powers of it.
