---
id: PL-010
title: Stop rebuilding render objects on every frame
priority: P2
effort: S
status: done
classes: perf
feature: chart-readout
touches: src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py, tests/integration/test_chart_patching.py
added: 2026-08-23
closed: 2026-09-02
pr: 219
verify: uv run pytest tests/integration tests/unit/test_simulation_view.py && grep -q 'def test_a_frame_of_moved_points_reaches_the_client' tests/integration/test_chart_patching.py
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

**Outcome.** Both halves landed. The chart points are reused - `_redraw_series`
(formerly `_decimated_points`) overwrites the `x` and `y` of the points the
series already holds and only extends or truncates the list for the difference
in count - and the `ft.TextStyle` and `ft.Border` are built once per agent at
import time into `AGENT_RENDER_STYLES`, still assigned unconditionally every
tick.

The gate was cleared first, and against a real client rather than by reading
Flet's source: Chromium driving the `flet_web` server, with a trace advanced by
in-place mutation alone, repainted the moved line between frames, and the
session's own outbound messages carried one `Replace` operation per moved
coordinate. `tests/integration/test_chart_patching.py` is what keeps that true
without a browser - it drives a real `flet.messaging.session.Session` over a
recording connection that serializes exactly as the WebSocket transport does,
so a Flet upgrade that stopped reporting in-place mutation fails there rather
than silently freezing the chart.

**Measured** on this project's Python 3.14 environment, 400 frames at the
steady state the ceiling describes (a saturated 300 s window decimated to 298
points across six traces), before and after on the same harness:

| | before | after |
| --- | --- | --- |
| `_refresh_view` median | 16.603 ms | 2.646 ms |
| `_refresh_view` p95 | 24.996 ms | 3.407 ms |
| `_apply_agent_color_scheme` median | 20.378 us | 1.208 us |

The frame is 6.3x cheaper - 14.0 ms of headroom per render tick, which is what
PL-009's speed multiplier needs. The per-object costs behind it, measured here
rather than taken from the estimate above: 6.3 us to build one
`fch.LineChartDataPoint` against 0.8 us to move an existing one's `x` and `y`,
and 2.5 us and 2.6 us for one `ft.TextStyle` and one `ft.Border`.

