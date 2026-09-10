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

> **The Qt port (`v0.5.1`) moots or transforms this.** `ROADMAP.md` § "v0.5.1 -
> the interface moves to Qt" names this item under "Items this port moots or
> transforms". Read that entry before starting: the work may be thrown away by
> the port, or may be a different question after it. Found 2026-09-10.

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

**Half of this is answered, without a client** (2026-09-08, `PL-R2YM`).
"Whether it costs anything" is measured: the write itself is 3-4 ms of
`_refresh_view` and Flet's diff sends nothing for a same-value write, but the
`page.update()` each `on_change` triggered walked the whole control tree for
23-59 ms whether or not anything in it had moved. So the write-back was never
the cost and stays exactly as `PL-018` left it; what changed is that a
slider's frame is now coalesced onto the render tick.

What still needs a live client is the other half, and the change makes it
sharper rather than moot: **does a write-back landing mid-drag snap the
thumb**, now that it can arrive up to `RENDER_INTERVAL_S` after the pointer
moved rather than within the same event? `PL-2QMK` is why no session here can
answer it.
