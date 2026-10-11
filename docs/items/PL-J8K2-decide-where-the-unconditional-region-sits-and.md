---
id: PL-J8K2
title: Decide where the unconditional region sits and what it looks like, which every Workspace a learner builds has on screen
priority: P2
effort: S
status: done
classes: ux, planning
feature: interface-areas
touches: src/anesthesia_sim/app/, docs/items
added: 2026-10-11
closed: 2026-10-11
pr: 1395
payoff: the unconditional region sits where a tab visibly does not switch it, and costs the chart no more height than the laptop budget allows
verify: grep -qF 'Answered 2026-10-11' docs/items/PL-J8K2-decide-where-the-unconditional-region-sits-and.md
---

**Problem.** Decide where the unconditional region sits and what it looks like,
which every Workspace a learner builds has on screen. `ROADMAP.md` § "v0.6.0"
-> "Required scope" entry 20, member 7. Entry 7 (`PL-NWTM`, `PL-W54S`)
guarantees the region is outside the layout container and decides what it
carries: `docs/MODEL.md` § "Minimum displayed outputs"' invariant tier
(simulated time, playback rate, run state, halt reason, agent, and the run's
name once more than one window shows runs), the per-substance tier once in the
main window (the delivered concentration and the six compartments, in both
units, with 1 MAC stated), the control-input record itself (its chart marks are
conditional), and the always-on-screen disclaimer line. Nothing decides where
it goes.

**What it costs today, measured 2026-10-11** (offscreen, Fusion, "Sans Serif
9 pt" fallback, tree `1ee4e78e`, a 1366 by 700 client area, one run;
indicative, not the owner's font): title row 32 px, transport row 48, readout
row 122, disclaimer 15, page padding and spacing 80 - 297 px of the 700 before
any Area exists. The control-input record is a 320 px panel in today's sidebar.
A second run adds its own transport and readout rows, about 170 px more
(inferred from `run_view.py`'s per-run builders; the two-run measurement is
owed to `PL-84QX`).

## Design round 2026-10-11

**Q1. Where.** **Recommendation: a band across the top of the window, above
the Workspace tab strip, and one line across the foot.** The band holds, per
run, the transport row and the readout row; the foot holds the disclaimer as it
stands. Above the tab strip because a tab switches what is under it and not the
region (`PL-QW1Z` Q1); across the full width because the per-substance readouts
are seven panels wide and the budget (`PL-84QX`) has no height for a second row
of them. *Alternative refused:* a column for the whole region, Blender's
sidebar shape, in which the seven readouts stack to seven times 122 px.

**Q2. The title row.** **Recommendation: it goes.** The window's title bar
already carries the application name (`app/main.py`,
`setWindowTitle(APP_DISPLAY_NAME)`), and the 26 px in-page title restates it
at a cost of 44 px (the row and its spacing) that `PL-84QX`'s arithmetic shows
the chart cannot spare on a 1366 px laptop. Each run's version-and-model badge,
which is per run and is the traceability the clinical-output standard asks for,
moves to the right end of that run's transport row, beside the run state it
qualifies. The large-text requirement `tools/contrast_check.py` declares for
the title retires with it. *Alternative refused:* keeping the row and taking
the 44 px from the chart; the chart is the teaching payload and the title is
branding.

**Q3. The control-input record.** **Recommendation: the right column of the
band, at today's sidebar width, scrolling within itself with the overflow
sentence today's panel already carries.** The record is unconditional, so it
cannot be a View, which can be closed; a strip of its own under the readouts
would cost the band another panel's height; a column beside the readouts costs
width instead, which at 1366 px is 229 px off a row that `PL-Z4K6` already
asked whether seven columns should fill. That width question is `PL-W54S`'s
per-substance tier to settle and this item does not pre-empt it; what this
item decides is that the record stands beside the readouts, not under them.

**Q4. Look.** The band is the `BACKGROUND` canvas and its rows the `PANEL`
cards they are today, nothing new drawn: no frame around the region, no label
naming it, no rule between it and the tab strip beyond the strip's own
indicator. The region should look like the dashboard the learner already
knows, with the Areas arriving under it, so the one thing that changed is the
one thing they have to learn.

[superseded 2026-10-11: answered below, every recommendation ratified]
**Decision needed.** Q1-Q3 above: a band across the top above the tab strip and
a line across the foot (Q1); the title row goes and each run's badge moves into
its transport row (Q2); the control-input record as the band's right column
(Q3). Q4 is the session's call and is recorded rather than asked. Agreeing with
the recommendations ratifies the three.

**Done when.** Q1-Q4 are recorded with the owner's kind and date, this item
closes on that record, `PL-NWTM` builds the region to it, and `PL-W54S` takes
the width question of Q3 with its tier design.

**Why it matters.** The region is on screen in every Workspace a learner ever
builds and in every window; where it sits decides what a tab appears to
switch, and what it costs decides whether the chart fits on a laptop.

**Generator check.** A one-off, and work the owner asked for: one of the
members `ROADMAP.md` Required-scope entry 20 names, scoped on 2026-09-21
(`PL-M3X6`) and filed by its round on 2026-10-11. `touches` reaches
`docs/items` only because the item closes on its own record once answered; no
apparatus fact was misread.

## Answers 2026-10-11

**Answered 2026-10-11: Q1-Q3 ratified** (project owner, 2026-10-11, ratified,
over the alternatives each question names - a column for the whole region,
keeping the title row, and the record as a strip under the readouts), given in
the project thread as "Agree with recs" after the recommendations were put one
line each with the mock-up (https://claude.ai/artifact/3KmFvWB3nXmjLBHKogNiNE)
and the 1366 by 768 floor confirmed by the same word. This item closes on that
record; the build items named in its Done-when carry the look.
