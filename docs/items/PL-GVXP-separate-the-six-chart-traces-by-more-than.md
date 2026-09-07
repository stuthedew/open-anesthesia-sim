---
id: PL-GVXP
title: Separate the six chart traces by more than colour, and meet contrast minima
priority: P2
effort: S
status: done
classes: defect, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/theme.py, tools/contrast_check.py, .claude/rules/ui-color.md, docs/MODEL.md, tests/unit/test_simulation_view.py, tests/unit/test_contrast_check.py
added: 2026-08-30
closed: 2026-09-07
verify: uv run pytest tests/unit/test_contrast_check.py tests/unit/test_simulation_view.py && grep -q 'def test_every_trace_contrast_clears_the_floor_in_all_four_vision_models' tests/unit/test_contrast_check.py && grep -q 'def test_no_two_chart_traces_are_separated_by_colour_alone' tests/unit/test_simulation_view.py
---

**Problem.** The six chart traces are separated by colour at luminance contrast
ratios of 1.01-1.26, and two of them share a line style. Measured from the
constants at `app/simulation_view.py:84-89`:

- Vessel-rich `#DC2626` against Fat `#64748B`: **1.01** for normal colour
  vision — indistinguishable by luminance, separated by hue alone.
- Circuit against Vessel-rich: **1.25** for normal colour vision, **1.01**
  under simulated dichromacy. Both are labelled "(solid)" in the legend at
  `:536` and `:541`, so for exactly the pair that collapses under CVD the
  redundant encoding is not redundant.
- Alveolar `#18A999` against the white panel: **2.93:1**, below WCAG's 3:1
  minimum for non-text graphical objects.

**Why it matters.** These six traces are what carries the science. The whole
lesson of the chart is reading one compartment against another — the vessel-rich
group rising fast while fat lags — and a reader who cannot tell which curve is
which reads the wrong compartment's value, which is a misreading of a clinical
quantity rather than an aesthetic complaint. `CLAUDE.md` treats a visually
attractive but misleading graph as a defect.

The project already did this analysis carefully once, for the *three*
agent-identification colours: `docs/MODEL.md:1126-1135` records the simulated
protanopia/deuteranopia/tritanopia contrasts, states that colour must never be
the only thing distinguishing two agents, and names the mitigation. The six
traces that carry the measurements got none of it.

**Where.** `app/simulation_view.py:84-89` (the six colour constants), `:536`
and `:541` (the legend's style labels); `app/theme.py`;
`docs/MODEL.md:1126-1135` for the standard the agent colours were held to.

**Scope note.** Do not conflate with PL-029 (surface the ISO 5360 colour
reference in the interface). That item concerns the three *agent-identification*
colours and their standard provenance, which are fixed by ISO 5360 and
deliberately kept even where separability suffers. This is a different set — the
six trace colours — with no provenance constraint at all, so they are free to be
chosen for separability.

**Approach.** Give every trace a distinct line style (or marker) so colour is
never the sole channel, as the agent colours already require; re-pick the six
colours for luminance separation as well as hue, and bring every trace to at
least 3:1 against the panel background. Pin the resulting contrast ratios in a
test the way the agent-colour claims are pinned, and record the analysis in
`docs/MODEL.md` beside the existing agent-colour section.

**Done when.** No two traces are distinguished by colour alone, no legend entry
claims a style another trace shares, every trace meets 3:1 against the panel,
the pairwise ratios under normal vision and simulated dichromacy are recorded in
`docs/MODEL.md`, and a test asserts them.

**Appended 2026-09-04 by `PL-ZRSP` (plot the F_A/F_I ratio).** The wash-in
plot that item added carries exactly one trace, in `ALVEOLAR_COLOR`, so it is
the one place in this interface where this item's arithmetic does *not* bind:
there is no six-way separation problem on a chart with a single line, and
nothing stops that line clearing SC 1.4.11's 3:1 against `PANEL` on its own.
It was left at `ALVEOLAR_COLOR` (2.93) deliberately, because the colour is
what says the trace is the alveolar compartment expressed against the one
filling it, and breaking that linkage to gain 0.07 of a ratio looked like the
worse trade. Worth revisiting as part of this item rather than separately: if
the palette pass gives the alveolar trace a colour that clears 3:1, both charts
get it and the question closes itself.

---

**Closed 2026-09-07.** All five "done when" clauses hold, and the palette half
was resolved in the opposite direction to the one this item's **Approach**
proposed. What follows is why, because the reasoning is the deliverable as much
as the diff is.

**Line styles: the vessel-rich trace took a sixth pattern, `even dash`
([6, 6]).** Equal mark and gap, which is the one rhythm no other trace has —
the other four dashed traces all draw more ink than gap. Circuit keeps `solid`.
Which style landed on which compartment is now derived from the colour matrix
rather than chosen: the pairs a reader can least separate by colour get the
marks they can most separate by shape, and the set's one confusable pair (the
2 px dots against the 4 px short dash) is spent on mixed venous against muscle,
the widest-separated pair of the six. `[8, 8]` was tried first for vessel-rich
and rejected — against the alveolar trace's `[10, 4]` it differed in mark
length alone, and those two sit at 1.08 under simulated deuteranopia.

**Colours: two moved, and not for pairwise separation.** `ALVEOLAR_COLOR`
`#18A999` → `#159789` and `MUSCLE_COLOR` `#D97706` → `#D17206`. Each keeps its
hue and saturation exactly and is darkened to the lightest shade clearing 3.2:1
against the panel in all four vision models. The other four were left alone:
they already clear the floor everywhere, and moving them buys nothing that can
be measured.

**Re-picking the six for luminance separation was declined, on a measurement
rather than on taste.** `.claude/rules/ui-color.md` judgment 3 — written after
this item and naming it — already says a palette cannot fix trace separation,
so the search was run to put a number on it rather than to reopen the
question. Holding each hue and saturation fixed and searching lightness, the
best achievable worst-pair across the four vision models is **1.28**, and it is
reached only by driving four of the six traces to near-black. The ceiling
argument is also stronger than the one recorded before: the 3:1 floor against a
white panel caps every trace's luminance at 0.30, which brings the six-trace
bound from 1.84 down to **1.48**. Both numbers are less than half of SC
1.4.11's 3:1. Spending the palette's hue identity to move 1.01 to 1.28 would
have bought nothing and cost the thing that makes a trace nameable.

**One measurement in the problem statement above did not reproduce.** "Circuit
against Vessel-rich: 1.25 for normal colour vision, **1.01** under simulated
dichromacy" — the 1.25 is right, the 1.01 is not. Under Brettel 1997 that pair
measures 1.27 (protanopia), 1.31 (deuteranopia), 1.24 (tritanopia). The pairs
that do reach ~1.01 under simulation are vessel-rich against fat (1.02,
tritanopia) and mixed venous against fat (1.02, deuteranopia). The finding the
number was offered in support of is untouched — the pair was two solid lines at
1.24, which is nowhere near separable — but the figure itself was wrong and
the whole matrix is now computed rather than quoted.

**The checker gained the measurement, so none of this is prose again.**
`tools/contrast_check.py` now carries the Brettel 1997 projection (two
half-planes per deficiency, coefficients from libDaltonLens over Smith &
Pokorny 1975), a `TRACE_FLOOR` holding every trace to 3:1 against the panel in
all four models as a hard error, and a `--matrix` report across all four. That
floor immediately found a shortfall no normal-vision check could see:
`MUSCLE_COLOR` was 3.19:1 as displayed and **2.98:1** simulated for
deuteranopia. `docs/MODEL.md`'s existing claim about the ISO 5360 agent
colours under dichromacy was also wrong once measurable — it said 1.1-1.4 and
the values are 1.06 to 1.48 — and is corrected and pinned.

**The `ACCENT` question `PL-W8DQ` was waiting on is answered: no.** The
alveolar trace now carries its own constant. A trace has to clear the floor
under four vision models and stay separable from five siblings; a slider track
has neither constraint, and holding one value to both was the over-loading
`PL-30P6` began unwinding. `ACCENT` is no longer a chart colour, so `PL-W8DQ`
can take its route 1 — darken `ACCENT` itself — with nothing left to collide
with.

**Not fixed here, filed as `PL-THXF`:** the legend swatch is a solid bar for a
trace that is dashed, so the legend's own second channel is words only. That
matters more now that the words are six phrases rather than five, and it is a
legend-rendering change independent of everything above.

**The appended `PL-ZRSP` question closes itself, as that note predicted.** The
wash-in plot's single trace takes `ALVEOLAR_COLOR`, so it inherited the 2.93:1
and is fixed at the source; the linkage that says the trace is the alveolar
compartment did not have to be broken to get there.
