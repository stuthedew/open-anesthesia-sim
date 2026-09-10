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

> **This fix rides the Qt port (`v0.5.1`), not Flet.** `ROADMAP.md` § "v0.5.1 -
> the interface moves to Qt" names this item under "Fixes this port carries":
> the defect lives in code that milestone rewrites from scratch, so fixing it
> on Flet means writing the same lines twice. Project owner, 2026-09-10.

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

**Approach: candidate 1, and it is no longer conditional.** `PL-GVXP` closed on
2026-09-07 and answered the question this item was waiting on. The alveolar
trace now carries its own `ALVEOLAR_COLOR` in `app/simulation_view.py`, so
`ACCENT` is not a chart colour any more: darkening it moves the four slider
tracks and nothing else.

The reason the two split is worth carrying into the fix. A chart trace has to
clear 3:1 against the panel under simulated dichromacy as well as as displayed,
and has to stay separable from five sibling traces; a slider track has neither
constraint - it is one graphical object against the panel behind it. So the
value here is bounded by exactly one requirement, and picking it is a
one-dimensional problem.

So: darken `ACCENT` until it clears 3:1 on `PANEL`, keeping hue and saturation
as `ACCENT_TEXT` did (that constant is the same hue at 5.00:1, so the target
sits between the two). The rejected alternative was a fourth colour constant
for the sliders, which is now pointless - `ACCENT` *is* the sliders' constant.
The `KNOWN_SHORTFALLS` entry for `("ACCENT", "PANEL")` goes in the same change;
the checker errors on a shortfall that starts passing.

**Where.** `app/theme.py` (`ACCENT`); `app/simulation_view.py:320`, `:336`,
`:346`, `:356`; `tools/contrast_check.py`'s `KNOWN_SHORTFALLS`.

**Done when.** The slider active track meets 3:1 against the panel, the
shortfall entry is gone, and whichever route was taken is recorded so the next
reader knows whether `ACCENT` is still shared with the chart.

**Depends on.** Nothing. It sequenced after `PL-GVXP` (separate the six chart
traces by more than colour) to avoid picking a value that item would replace;
that item closed on 2026-09-07 and this one is unblocked.
