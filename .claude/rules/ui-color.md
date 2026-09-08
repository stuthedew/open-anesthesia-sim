---
paths:
  - "/src/anesthesia_sim/app/**"
---

# Picking a color in this interface

The target is **WCAG 2.2 Level AA**. `docs/MODEL.md` § "Color contrast, and the
standard this interface is held to" is the full statement — version, level, the
two places this project holds itself higher, and the criteria deliberately
deferred. Read it before changing a color; this file is only what a session
needs at the moment it picks one.

**`tools/contrast_check.py` decides the ratios, and `make check` runs it.** Do
not measure a ratio by hand, quote one in a comment, or reason about whether a
pair "looks fine" — run the tool, which prints the measured value for every
declared pair. What follows is only the half it cannot decide.

**`tools/agent_identity_check.py` decides one thing the ratios cannot reach: no
control carrying agent identity may be *rendered* disabled** (project owner,
2026-09-08). Flet/Material substitutes its own disabled-content grey for the
colour you set, and that grey is declared in no source file, so the requirement
above keeps measuring a pair that has stopped being drawn — which is what
`PL-61WW` was. A control may be `disabled` where it is also
`visible = not <the same expression>`, since it then draws nothing; otherwise
carry the identity in a control with no disabled state, as
`_running_agent_display` does. A control given an agent colour where it is
constructed must also be written by `_apply_agent_color_scheme`, which is what
keeps the checked set complete.

## The four judgments the tool leaves to you

1. **A new color is added to `REQUIREMENTS` in the same change that introduces
   it.** The tool checks the pairs it is given and knows nothing about the ones
   it is not, so a color added without an entry is unchecked while looking
   checked. Name the pair it actually appears against — read the source and
   confirm which background it is drawn on, rather than assuming `PANEL` — the
   criterion, and the reason in a few words.

   **Cite the code by symbol, in backticks, and never by line number.** The
   reason is the entry, and the entry is how a later reviewer finds what it
   defends; a line number stops leading there on the next edit to `app/` and
   says nothing when it stops. Write the method or attribute the color is set
   on — `` `_status_text` ``, `` `_build_metric_panel` `` — bare, so `` `mount` ``
   rather than `` `mount()` ``. The tool refuses a line number and resolves
   every symbol you name against `app/theme.py` and `app/simulation_view.py`,
   so a rename fails `make check` instead of rotting quietly (`PL-GJDW`).

2. **Color is never the only channel carrying a distinction.** SC 1.4.1 is the
   floor; the real reason is stronger and specific to this application. ISO 5360
   Table 2 footnote b makes displaying an agent color an obligation to display
   the *correct* one, so a second cue is what stops a mis-seen color becoming a
   mis-identified agent. The agent name accompanies the color everywhere. Any
   new encoding that carries meaning by color needs its own second channel —
   text, shape, line style, or position.

3. **Chart traces need a non-color channel as a matter of arithmetic, not
   taste.** Contrast composes along a bounded axis, so no arrangement of six
   traces gives every pair more than 21^(1/5) ≈ 1.84 — and once each must also
   clear 3:1 against the white panel, which caps its luminance, no more than
   **1.48**. Re-picking the palette cannot fix trace separation, and a change
   that tries to is solving the wrong problem: `PL-GVXP` searched the space with
   hue and saturation held and reached 1.28 across four vision models, at the
   price of driving four of the six traces to near-black. Run `python3
   tools/contrast_check.py --matrix` for both bounds and the measured pairs.
   That item sets this bar.

   **Pairwise separation is this project's bar and not the criterion's, and the
   distinction is load-bearing** (`PL-JX0Z`). SC 1.4.11 asks each line for 3:1
   against its *background*, which `tools/contrast_check.py` is what enforces;
   its pairwise matrix is reported and deliberately fails nothing. The
   Understanding document's own line-graph example says so in terms — *"The
   lines should have 3:1 contrast against their background, but as there is
   little overlap with other lines they do not need to contrast with each other
   or the graduated lines"* — and elsewhere allows the "law of continuity" to
   ignore **minor** overlaps. Both carve-outs are conditioned on an absence of
   overlap this chart does not have: six compartment traces start together,
   converge toward equilibrium and cross through wash-in and washout, which is
   the lesson rather than an accident. So the bar is an exceedance that the
   standard's own condition supports here, rather than either a requirement or
   an arbitrary strictness — do not relax it by citing the criterion, and do not
   defend it by misquoting the criterion. `docs/MODEL.md` § "Color contrast, and
   the standard this interface is held to" carries it, in the list of bars this
   interface holds itself to above AA.

   **The floor against the panel is a different question, and it is worth
   re-picking a color for.** It binds each trace alone rather than pairwise, so
   it is reachable — and it is checked under simulated dichromacy as well as as
   displayed, which is how `MUSCLE_COLOR` was caught passing at 3.19:1 on screen
   and failing at 2.98:1 for a deuteranope. Failing traces are an error rather
   than a `KNOWN_SHORTFALLS` entry.

4. **A standard-fixed color is not yours to change.** The three agent
   identification colors are fixed by ISO 5360:2016 Table 2, and
   `app/theme.py`'s header records the provenance chain and why it cannot move.
   Where such a color fails a contrast requirement, fix the presentation around
   it — a border, a different surface — never the color. `PL-2SVR` is the worked
   example.

## The shortfall list is not a suppression list

`KNOWN_SHORTFALLS` records pairs that fail today, each against the item that
closes it. It exists so a gap is visible and owned rather than living in a
comment nobody re-measures. Two rules keep it honest:

- **Never add an entry to make a change go green.** An entry is for a shortfall
  you are tracking, not one you are introducing. A new color that cannot meet
  its minimum is a color to reconsider, not to excuse.
- **Deleting an entry is part of fixing it.** The tool reports a listed
  shortfall that starts passing as an error, so a fix that leaves its excuse
  behind fails `make check`.
