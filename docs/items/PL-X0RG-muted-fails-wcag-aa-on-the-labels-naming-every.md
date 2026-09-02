---
id: PL-X0RG
title: MUTED fails WCAG AA on the labels naming every clinical readout
priority: P2
effort: S
status: ready
classes: defect, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/theme.py, tools/contrast_check.py
added: 2026-09-02
verify: python3 tools/contrast_check.py && ! grep -q '("MUTED", "PANEL")' tools/contrast_check.py
---

**Problem.** `app/theme.py:11` defines `MUTED = "#627D98"`. Measured by
`tools/contrast_check.py`, it reaches **4.28:1** against `PANEL` (`#FFFFFF`),
below WCAG 2.2 SC 1.4.3's 4.5:1 minimum for normal-size text. It is not
borderline decoration - it is the colour of:

- the label naming every metric readout (`app/simulation_view.py:532`), so the
  word identifying *which* clinical quantity a number is;
- the run-status text, "Paused" / "Running" (`:187`, `:684`);
- the chart's axis description, "Vertical axis: percent | Horizontal axis:
  simulated seconds" (`:556`), which is what makes the plot readable at all;
- the agent-accounting detail line (`:209`, `:211`).

**Why it matters.** The value is legible; the label saying what it means is
not, for a reader whose contrast sensitivity is reduced - which includes normal
ageing, not only diagnosed impairment. `CLAUDE.md` treats the correct number
with the wrong label as a safety failure; the correct number with an
*unreadable* label is the same class of problem, and the axis description is
the specific case where losing it changes what the plot appears to say.

The large-text exception does not rescue it. WCAG's threshold is 18pt, or 14pt
bold (18.66px); Flet's default text size is 14px, so even the bold status text
at `:187` is judged at 4.5:1.

**Approach.** Darken `MUTED` until it clears 4.5:1 on `PANEL`, keeping the
blue-grey hue that separates it from `INK` (`#243B53`, 11.50:1) - the point of
the constant is a visible hierarchy between label and value, and that survives
the change. Pick the value against the checker, which prints the measured
ratio, rather than by eye, and confirm `INK` stays clearly the stronger of the
two. `#F4F7FA` (the page background) needs checking too if any `MUTED` text
ever sits outside a panel; today all of it is on `PANEL`.

**Where.** `app/theme.py:11`; `tools/contrast_check.py`'s `KNOWN_SHORTFALLS`
(the entry for `("MUTED", "PANEL")`, which must be deleted in the same change -
the checker errors on a shortfall that starts passing).

**Done when.** `MUTED` on `PANEL` meets 4.5:1, the `KNOWN_SHORTFALLS` entry is
gone, and `make check` is green with one fewer tracked shortfall.
