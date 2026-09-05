---
id: PL-90Y6
title: The MAC-awake band draws as a line at any axis range the overpressure constraint allows
priority: P2
effort: M
status: done
classes: defect, ux
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/chart_series.py, docs/MODEL.md, tests/unit/test_simulation_view.py
added: 2026-09-04
closed: 2026-09-05
pr: 345
verify: uv run pytest tests/unit/test_simulation_view.py && grep -q 'def test_the_mac_awake_band_reads_as_an_interval_not_a_line' tests/unit/test_simulation_view.py
---

**Problem.** The MAC-awake band (`PL-F52R`) is drawn at the running agent's
population MAC-awake, one standard deviation either side of the published
mean. That spread is +/-0.05 MAC for sevoflurane and isoflurane and
+/-0.063 MAC for desflurane, so on the chart's 3 MAC axis the band spans
3.3 % of the plot height for sevoflurane and 4.2 % for desflurane. It draws
as a slightly thick line rather than as a band.

**Why it matters.** The band's *extent* is the encoding that says this is a
population value with real spread and not a threshold. `docs/MODEL.md`'s
"MAC-awake as a chart reference" chose a band rather than a line for exactly
that reason, and distinguishes it in kind from the 1 MAC line beside it,
which is a definitional anchor and correctly a line. Flattening the band into
a line erases the distinction the mark type was chosen to carry, and
`CLAUDE.md`'s "make uncertainty and model limitations visible rather than
allowing numerical precision or polished graphics to imply more certainty
than the model supports" is the standard it sits under. The band's own label
states the range in text, which is what keeps this an interpretability defect
rather than a safety one.

**Why this is not the axis's problem, measured.** This began as an appended
note on `PL-CC23` (scale the chart's vertical axis to the run) and was split
out when the arithmetic showed the axis cannot fix it (project owner,
2026-09-04). Band height as a fraction of plot height, against a shared
ceiling of K MAC:

| K | Band, % of plot | 1 MAC at | Overpressure range on the plot |
| --- | --- | --- | --- |
| 2.0 | 5.00-6.30 % | 50 % height | none - 1 MAC is at mid-plot |
| 2.5 | 4.00-5.04 % | 40 % height | to 2.5x |
| 3.0 (shipped) | 3.33-4.20 % | 33 % height | to 3x |
| 4.0 | 2.50-3.15 % | 25 % height | to 4x |

Two things follow. The ceiling that would make the band unambiguous is around
2 MAC, and there the 1 MAC line sits at mid-plot with no room for the
overpressure induction the chart has to be able to show - which is why 3 MAC
was chosen. And at 4 MAC sevoflurane's band is 2.50 % of the plot, *exactly
what it was on the old dial-maximum axis*, because sevoflurane's dial maximum
was already 4 MAC. So no axis choice available to this chart makes a
+/-0.05 MAC band read as a band.

**Approach.** The fix is at the mark rather than at the axis, and the
constraint is that the drawn extent must not misstate the data extent - a
band drawn thicker than +/-1 SD asserts a wider population spread than the
literature supports, which trades an interpretability defect for a
correctness one. Candidates, none yet chosen:

- Hatching or a texture inside the band, so the mark reads as an interval at
  any thickness while its edges stay at the true +/-1 SD.
- An explicit interval mark at one edge of the plot - a whisker or bracket
  drawn at the band's true height - which is the conventional encoding for a
  spread too small to fill.
- A minimum *stroke* on the band's two boundary lines rather than a minimum
  fill height, so the two edges stay individually visible and the fill
  between them keeps its true extent.

Whichever is taken, `tools/contrast_check.py` and `.claude/rules/ui-color.md`
constrain it: the band is drawn in the interface's own ink rather than in a
seventh hue, and whatever distinguishes it has to survive greyscale and
colour-vision deficiency, because it is an encoding that carries meaning.

**Done when.** The MAC-awake band is distinguishable in kind from the 1 MAC
line at the shipped axis range, for all three agents, without the drawn
extent overstating the published +/-1 SD; and `docs/MODEL.md`'s "MAC-awake as
a chart reference" states what the mark's geometry asserts.

**Worked.** The third candidate, and the first two were not close. The mark
was already a band in the data and a line in the geometry: one
`LineChartData` stroked at the upper edge, with `below_line_bgcolor` filling
down to a `below_line_cutoff_y` that nothing stroked. A stroked top over an
unstroked fill is a line with a shadow under it whatever the fill's extent,
which is why no axis range fixed it and why the measurement table above
holds. So the lower boundary is now stroked too - a second two-point series
built and moved exactly like the first - and the fill sits between them.

Both strokes stay on the published values, so the drawn extent is the data
extent and nothing is padded outward; a minimum drawn height would have made
the mark easier to read by asserting a wider population spread than the
sources support, which is this item's own constraint and the reason the
hatching and whisker candidates were not taken either. Hatching has no Flet
primitive and would have cost per-frame controls; a whisker at the plot edge
moves the spread away from the height traces cross, which is the relationship
`docs/MODEL.md` builds the whole reference on.

The legend swatch carried the same asymmetry - `border=Border(top=...)` over
the same fill - and is now ruled on both edges, because a swatch teaching one
mark for a chart drawing another is the defect arriving by the other door.

`docs/MODEL.md` § "MAC-awake as a chart reference" gains "The band's
geometry, and why it is two strokes rather than a thicker mark", carrying the
measured percentages with `derived:` markers against each agent's stored
spread.

*Not confirmed by screenshot, and that is an environment limit rather than a
skipped step:* the container cannot render the Flutter web app at all
(`PL-2QMK`). The geometry was photographed instead, from the shipped
constants - before and after, all three agents, and the narrowest band at 4x.
Before is one rule with a pale slab beneath it; after is two rules with a
tinted channel between them.
