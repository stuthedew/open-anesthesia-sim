---
id: PL-X0RG
title: MUTED fails WCAG AA on the labels naming every clinical readout
priority: P2
effort: S
status: done
classes: defect, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/theme.py, tools/contrast_check.py, tests/unit/test_contrast_check.py, docs/MODEL.md
added: 2026-09-02
closed: 2026-09-02
verify: uv run pytest tests/unit/test_contrast_check.py && grep -q 'def test_muted_clears_the_text_minimum_on_both_surfaces' tests/unit/test_contrast_check.py
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
two.

**Correction, found while doing this.** The sentence that stood here said the
page background needed checking only "if any `MUTED` text ever sits outside a
panel; today all of it is on `PANEL`". That was wrong, and it was wrong because
it was written from the colour constants rather than from the widget tree.
`mount()` builds a top-level `Column` with no background of its own, so the
run-status word sits on `BACKGROUND` - which is the darker surface, and
therefore the binding one. `MUTED` measured **3.98:1** there against 4.28:1 on
the panel, so the failure was worse than the item claimed and the panel
measurement alone could not have sized it.

**Resolution.** `MUTED` is `#59728A`, a uniform darkening of `#627D98` that
leaves hue and saturation unchanged (210 deg, 0.355). It measures **5.00:1** on
`PANEL` and **4.65:1** on `BACKGROUND`, clearing AA on both with margin, and
`INK` remains far stronger (11.50 / 10.70) so the label-to-value hierarchy reads
as before.

`tools/contrast_check.py`'s requirement table was corrected in the same change:
it had assumed `PANEL` for the run-status colours, which measured pairs that
are not on screen while leaving the real ones unread. `MUTED`, `ACCENT` and
`WARNING` are now each declared against both surfaces they appear on, and
`test_the_run_status_text_is_checked_against_the_page_background` is the guard
against the assumption returning.

**Where.** `app/theme.py:11`; `tools/contrast_check.py`'s `KNOWN_SHORTFALLS`
(the entry for `("MUTED", "PANEL")`, which must be deleted in the same change -
the checker errors on a shortfall that starts passing).

**Done when.** `MUTED` on `PANEL` meets 4.5:1, the `KNOWN_SHORTFALLS` entry is
gone, and `make check` is green with one fewer tracked shortfall.
