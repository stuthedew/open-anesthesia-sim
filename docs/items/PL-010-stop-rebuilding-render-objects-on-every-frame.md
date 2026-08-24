---
id: PL-010
title: Stop rebuilding render objects on every frame
priority: P2
effort: S
status: ready
classes: perf
touches: src/anesthesia_sim/app/simulation_view.py
added: 2026-08-23
---

**Problem.** Two allocations repeat on every render tick.
`SimulationView._decimated_points` builds a fresh `fch.LineChartDataPoint`
for every drawn point (~8.4 us each, against ~0.43 us to mutate an existing
point's `x`/`y`); at the bounded 300 points per trace that is about 15 ms of
the ~17 ms frame. `_apply_agent_color_scheme` constructs a fresh
`ft.TextStyle` and `ft.Border` even when the selected agent has not changed,
which is almost every tick.
**Why it matters.** Headroom rather than a defect — the frame is already
well inside budget. It matters as headroom for PL-009, where a speed
multiplier raises the render rate.
**Where.** `app/simulation_view.py` (`_decimated_points`,
`_apply_agent_color_scheme`).
**First step.** The chart points need a live Flet client: confirm in-place
mutation actually repaints. PL-001 declined this win because a mutation
Flet's diff does not notice would leave the chart silently showing stale
data — a presentation-correctness failure, not a cosmetic one. The colour
objects need no client if they are precomputed per `AGENT_COLOR_SCHEMES`
entry at import time and still assigned every tick.
**Done when.** Frame cost is measurably reduced, a live client is confirmed
to repaint traces every frame, and switching agents still repaints both the
header badge and the dropdown.
