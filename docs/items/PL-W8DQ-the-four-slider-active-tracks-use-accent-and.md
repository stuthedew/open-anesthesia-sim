---
id: PL-W8DQ
title: The four slider active tracks use ACCENT and miss the non-text minimum
priority: P3
effort: S
status: ready
classes: defect, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/theme.py, src/anesthesia_sim/app/simulation_view.py, tools/contrast_check.py
added: 2026-09-02
verify: python3 tools/contrast_check.py && ! grep -q '("ACCENT", "PANEL"): ' tools/contrast_check.py
---

**Problem.** All four parameter sliders - fresh gas flow, delivered
concentration, alveolar ventilation and cardiac output - draw their active
track and thumb in `ACCENT` (`app/simulation_view.py:320`, `:336`, `:346`,
`:356`). Against the panel they sit on, `ACCENT` measures **2.93:1**, below
WCAG 2.2 SC 1.4.11's 3:1 for user-interface components. It misses by 0.07,
which is small enough that it would never be spotted by eye and large enough
that the criterion says it is not met.

**Why it matters.** The active track is how each slider shows where its value
sits in its range - the only continuous cue for a control whose numeric readout
is a separate element beside it. These four are the entire input surface of the
simulator: every value the model is run with is dialled here. A reader who
cannot see the filled portion against the unfilled has to fall back on the
readout, which turns a direct-manipulation control into a number they have to
read twice.

Found while doing `PL-30P6`, which took `ACCENT`'s other failing role - text -
and gave it a token of its own. This is the remaining half, and it is the reason
that split was worth making: one constant was carrying a text role at 4.5:1, a
trace role at 3:1 and a control role at 3:1, and no single value satisfies all
three.

**Approach.** Two candidates, and the choice depends on `PL-GVXP`:

1. **Darken `ACCENT` itself** until it clears 3:1 on the panel. It has only
   graphical roles now, so one value can serve both, and the change is one
   constant. But `ACCENT` is also `ALVEOLAR_COLOR`, so this moves a chart trace
   and `PL-GVXP` is re-picking those anyway - doing it here risks being undone.
2. **Give the sliders their own token.** Independent of `PL-GVXP`, at the cost
   of a fourth colour constant in a file `ROADMAP.md` item 24 wants
   consolidated.

Prefer (1) **after** `PL-GVXP` lands, and (2) only if that item concludes the
alveolar trace should keep a colour the sliders cannot use. Either way the
`KNOWN_SHORTFALLS` entry for `("ACCENT", "PANEL")` goes in the same change -
the checker errors on a shortfall that starts passing.

**Where.** `app/theme.py` (`ACCENT`); `app/simulation_view.py:320`, `:336`,
`:346`, `:356`; `tools/contrast_check.py`'s `KNOWN_SHORTFALLS`.

**Done when.** The slider active track meets 3:1 against the panel, the
shortfall entry is gone, and whichever route was taken is recorded so the next
reader knows whether `ACCENT` is still shared with the chart.

**Depends on.** Nothing hard, but sequencing after `PL-GVXP` (separate the six
chart traces by more than colour) avoids picking a value that item then
replaces.
