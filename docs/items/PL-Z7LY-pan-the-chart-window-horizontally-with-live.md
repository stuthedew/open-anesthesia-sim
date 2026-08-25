---
id: PL-Z7LY
title: Pan the chart window horizontally, with live-follow as an explicit state
priority: P3
effort: M
status: ready
classes: ux, feature
feature: chart-readout
touches: src/anesthesia_sim/app/simulation_view.py
added: 2026-08-25
---

**Problem.** Once a selected time base is narrower than the run (PL-SSBP),
the user needs to move the window across the run the way they would scroll a
document wider than the screen.

**Why it matters.** The safety-relevant half is the mode, not the motion. On a
running simulation a panned-back window shows history while the readouts above
it show now, and a learner reads stale values as current — the stale-state
misinterpretation `CLAUDE.md` names directly.

**Where.** `app/simulation_view.py`.

**Notes.** Model the state as a window offset driven by an explicit control,
and treat drag as an additive input later: `flet-charts` 0.86 exposes no chart
gesture handling, a drag-only affordance is unusable by keyboard and awkward
on touch, and an offset value is unit-testable where a gesture is not. While
the window sits at the right edge it follows new samples; once panned away it
stops following, says so unmistakably, and offers one-click return to live.
Test the transitions, not just the happy path: pan while paused then resume,
reset mid-pan, agent switch mid-pan.

**Done when.** The window can be moved across the run, and whether it is live
or holding position is unmistakable at a glance and reversible in one click.
