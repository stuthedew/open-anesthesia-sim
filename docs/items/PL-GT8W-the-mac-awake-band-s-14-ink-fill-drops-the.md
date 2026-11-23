---
id: PL-GT8W
title: The MAC-awake band's 14% INK fill drops the alveolar trace from 3.61:1 to 2.82:1 and the muscle trace from 3.43:1 to 2.68:1 inside the band, below SC 1.4.11's 3:1, exactly where a learner compares crossings, and tools/contrast_check.py measures traces only against PANEL so make check cannot see it
priority: P2
effort: M
status: done
classes: ux
feature: replay-findings
milestone: v0.6.22
touches: src/anesthesia_sim/app/theme.py, tools/contrast_check.py, docs/MODEL.md
added: 2026-10-25
closed: 2026-11-23
pr: 2271
payoff: the traces stay legible exactly where a learner compares crossings, and the contrast check can see a fill that breaks that
tests: tests/unit/test_contrast_check.py::test_every_trace_clears_the_floor_inside_the_shipped_band, tests/unit/test_contrast_check.py::test_a_band_fill_that_drops_a_trace_below_the_floor_is_an_error, tests/unit/test_contrast_check.py::test_the_palette_derives_the_preview_composites_from_the_theme
---

**Problem.** `MAC_AWAKE_BAND_FILL_OPACITY = 0.14` (`src/anesthesia_sim/app/theme.py`) tints the band INK over a white panel. The composite is about #E0E4E7. Against it, on main's colours, alveolar measures 2.82:1 and muscle 2.68:1, against 3.61 and 3.43 on PANEL. The comment above it says the fill is light enough for six traces to stay legible across it. The `Requirement` table in `tools/contrast_check.py` measures every trace only on PANEL and the band only by its edge.

**Why it matters.** The band is where the alveolar and vessel-rich crossings are compared, so it is where trace legibility matters most. The check reports no shortfall while the fill creates two. A fix could lighten the fill, or add the band composite as a background that every trace is measured against.

**Done when.** Every compartment trace reaches 3:1 against the MAC-awake band's composite colour, and `tools/contrast_check.py` measures each trace against that composite as a background named "the MAC-awake band composite", so `make check` refuses a fill that drops a trace below 3:1.

**Found by.** `PL-TBQS` reviewer replay on #288, finding r05 F2. Checked against main on 2026-10-25 with the WCAG relative-luminance formula on the theme constants. Run `tools/contrast_check.py` to confirm once the composite is declared.

**Generator check.** Shares one fact with `PL-6W49`: `tools/contrast_check.py` measures each chart series only against `PANEL`, never against another series or a composite background the chart draws. Two items are not a generator, and a third would make one.

**Checked 2026-11-22** against `d4e8200`: still applies. `MAC_AWAKE_BAND_FILL_OPACITY` in `app/theme.py` is still 0.14 over `INK` (`#243B53`), and the composite on white is `#E0E4E7`. Recomputed with the WCAG formula, `ALVEOLAR_COLOR` (`#159789`) measures 3.61:1 on `PANEL` and 2.82:1 on the composite, and `MUSCLE_COLOR` (`#D17206`) 3.43:1 and 2.68:1. `tools/contrast_check.py` still measures every trace only on `PANEL`. The contrast section this item would update is now in `docs/INTERFACE.md`, not `docs/MODEL.md`.

**Done 2026-11-23.** WCAG 2.2's Understanding document for SC 1.4.11, read at source in this session, asks for 3:1 between a graphical object and the colours adjacent to it. Inside the MAC-awake band a trace is drawn on the band's fill over the panel, so that composite is the adjacent colour. `tools/contrast_check.py` now forms the composite from the theme's own colour and opacity, as Qt paints it, and holds every trace to 3:1 against it in all four vision models. The fill's opacity fell from 0.14 to 0.035, the most that keeps every trace at 3:1, so muscle, the lightest trace, is 3.03:1 under deuteranopia inside the band. The band's two edges are still drawn as `INK` strokes, which is what shows where the band lies.

Blind review pass 2 found the same fault in the preview region a drag shows: its `MUTED` fill at 0.10 left muscle at 2.83:1 inside the region and 2.68:1 where the region overlaps the band. The check now derives the region's fill over the panel, and the darker of its two stackings with the band, and holds every trace to 3:1 against both. With the band at 0.035 the region can take no fill that a reader could see: 0.015 already drops muscle to 2.98:1 over the band. So the region now has no fill, which its theme comment already called decoration; its edge and its label carry it.

Both passes also said the band's fill at 0.035 is hard to see, so the band reads as two rules. Not changed: the fill cannot be darker while the lightest trace stays at 3:1, and `PL-90Y6` chose two stroked edges because two strokes with a gap read as an interval at any thickness, so the strokes carry the band. Darkening the light traces to buy room would close the pairwise gaps that `PL-GVXP` already found at their limit.

Tests: `test_a_fill_over_the_panel_blends_the_stored_values`, `test_an_opacity_outside_zero_to_one_is_refused`, `test_the_palette_derives_the_band_composite_from_the_theme`, `test_the_palette_derives_the_preview_composites_from_the_theme`, `test_a_band_fill_that_drops_a_trace_below_the_floor_is_an_error` and `test_every_trace_clears_the_floor_inside_the_shipped_band`, all in `tests/unit/test_contrast_check.py`. Documents checked: `docs/INTERFACE.md` (§ "The MAC-awake band", the SC 1.4.11 paragraph and the preview region's paragraph, updated), `docs/MODEL.md` (holds no display colour), `.claude/rules/ui-color.md` (still true: it already says traces are measured against what they are drawn on).
