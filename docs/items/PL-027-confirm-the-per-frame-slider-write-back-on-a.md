---
id: PL-027
title: Confirm the per-frame slider write-back on a live Flet client
priority: P2
effort: S
status: ready
classes: ux
feature: vaporizer-controls
touches: src/anesthesia_sim/app/simulation_view.py
added: 2026-08-24
---

**Problem.** PL-018 made `_refresh_view` write every parameter slider's
`value` from the snapshot, so a refused setting cannot leave a control
showing a dial position the simulation is not running at. During a run that
write happens on every render tick (5 Hz). Whether Flet's diff treats a
same-value write as a no-op, and whether a write landing mid-drag snaps the
thumb, was not verified: no live client was available in the session that
made the change.
**Why it matters.** The write-back itself is a presentation-correctness fix
and should stay. The unverified part is whether it costs anything or
interferes with dragging — the same class of unknown as PL-010, and worth
settling in the same sitting on a client.
**Where.** `app/simulation_view.py` (`_refresh_view`).
**First step.** Run the app, drag each slider through a full sweep during a
run, and watch for thumb snapping or lag; then check whether frame cost
changed measurably.
**Done when.** Dragging during a run is confirmed smooth on a live client,
or the write-back is narrowed to the cases that need it with the reason
recorded.
