---
id: PL-F2YS
title: The unconditional region opens a 1366 px laptop's readout row on four columns and stacks two runs' readouts in two rows where docs/MODEL.md pairs them in one, so compare mode leaves the chart below its 360 px minimum
priority: P1
effort: M
status: blocked
classes: defect, safety
feature: interface-areas
touches: src/anesthesia_sim/app/, tests/integration, docs/MODEL.md
blocked-by: PL-W9P6
added: 2026-10-18
payoff: a 1366 px laptop opens the seven readouts in one row, and two runs compared share one readout block as docs/MODEL.md specifies, so compare mode keeps the chart at its minimum or the shortfall reaches the owner
verify: grep -q 'def test_a_1366_px_window_opens_one_run_s_readout_row_on_seven_columns' tests/integration/test_simulation_view.py
---

**Problem.** The unconditional region divides its width and its height in ways
that two ratified decisions and `docs/MODEL.md` say it should not, and a 1366 px
laptop shows both. Measured on 2026-10-18 on the offscreen font, against
`SimulationView` at `origin/main` `4c068b29`:

- **The readout row opens on four columns at 1366 px.** With one run, a 1366 px
  window gives the region 1320 px. The control-change record column takes about
  306 px of it, so the readout column gets 1002 px, 3 px short of the 1005 px
  that seven across needs. One run first opens on seven at 1398 px. `PL-J8K2` Q3
  (project owner, 2026-10-11, ratified) put the record "at today's sidebar
  width", which is about 228 px at that window. The build gives it the
  box layout's 3:1 share instead, and `PL-Z4K6` (project owner, 2026-09-27,
  ratified) maximized the window so that this screen opens on seven.
- **Two runs' readouts take two rows.** Each `RunView` builds its own
  `ReadoutRow`, so compare mode stacks a second block of seven panels, and the
  region grows from 284 px to 400 px. `docs/MODEL.md` § "Minimum displayed
  outputs" says the opposite, as `PL-1XPX` decided on 2026-09-13: "Pairing the
  two values under one compartment label is what keeps that from doubling the
  block's height: it grows in width instead". The Qt port did not carry the
  pairing over, and no item recorded that.
- **So compare mode leaves the chart below its minimum.** `PL-84QX`'s budget
  (project owner, 2026-10-11, ratified) needs the concentration chart at no
  less than 360 px on a 1366 by 700 client area with the Areas' furniture in
  place. Its arithmetic left 215 px with two runs, and `ROADMAP.md` Required
  scope entry 20 handed compare mode to `PL-W54S` to settle. This item now
  carries that question, because `PL-W54S` is the per-window declaration and
  this is layout.

The `_build_unconditional_region` docstring in
`src/anesthesia_sim/app/simulation_view.py` still says "The seven readouts
still stand in one row beside it", which the first finding makes false.

**Why it matters.** The readout row is the one row `docs/MODEL.md` § "Displayed
precision" builds the ordinal comparison on, circuit leading alveoli leading
the tissues. A second block of seven panels doubles what a reader scans to
compare two runs, which is the reading `PL-1XPX` chose pairing to protect. And
a chart below its minimum in v0.6.0's tiled layout is not scrolled to but
refused (`PL-K285`), so compare mode on the commonest laptop would show a
refusal where the teaching payload belongs.

**Decided in the re-confirmation of `PL-W54S`, 2026-10-18** (session's call,
each restoring a decision already ratified rather than making a new one):

1. The record column takes the width `PL-J8K2` Q3 ratified, today's sidebar
   width, so the readout row gets the rest. The build measures that one run
   then opens on seven at 1366 px on the offscreen font.
2. The readouts pair two runs per compartment, one panel per compartment
   carrying both runs' values, each value naming its run in text, as
   `docs/MODEL.md` already specifies. Whether the two values sit side by side
   or one above the other is a placement call, and a placeholder
   (`.claude/rules/instruction-writing.md` rule 14). The build takes the one
   that keeps seven across at 1366 px if either does.
3. The build then measures compare mode on a 1366 by 700 client area against
   `PL-84QX`'s budget. If the chart still falls below 360 px, the shortfall
   and the options go to the project owner as a decision, with a
   recommendation, because the budget was his and lowering the chart's minimum
   was refused on 2026-10-11.

**Blocked by `PL-W9P6`.** That item builds the adapter that replaces the
splitters, and the sidebar width this item reads is a splitter's today. Both
change `app/simulation_view.py`'s layout code, so this one follows.

**Done when.** One run opens the readout row on seven columns in a 1366 px
window on the offscreen font, and a test asserts it from the row's own
reservation rather than a pixel figure; two runs show one readout block whose
panels name both runs; compare mode's chart height on 1366 by 700 is measured
and either meets `PL-84QX`'s 360 px or has gone to the owner; and the region's
docstring and `docs/MODEL.md` § "Displayed precision"'s dated measurement say
what the build shows.

*Scope.* `ROADMAP.md` § "v0.6.0 - the layout is the reader's" -> "Required
scope" entry 20, where compare mode was `PL-W54S`'s to settle.
