---
id: PL-GVXP
title: Separate the six chart traces by more than colour, and meet contrast minima
priority: P2
effort: S
status: ready
classes: defect, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/theme.py, docs/MODEL.md, tests/unit/test_simulation_view.py
added: 2026-08-30
verify: uv run pytest -k trace_contrast
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
