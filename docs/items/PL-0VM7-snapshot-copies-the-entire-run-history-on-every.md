---
id: PL-0VM7
title: snapshot() copies the entire run history on every frame
status: ready
priority: P2
effort: S
classes: perf
feature: teachable-case
verify: uv run pytest tests/integration/test_controller.py && grep -q 'def test_a_frame_reads_only_the_window_it_draws' tests/integration/test_controller.py
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/chart_series.py
added: 2026-09-04
---

**Problem.** `SimulationController.snapshot` builds
`concentration_history=tuple(self._concentration_history)` — a full copy of
the run's entire sample list — and `_refresh_view` calls `snapshot()` on
every render frame. The copy is O(run length) and the render loop runs at
`RENDER_INTERVAL_S`, so the per-frame cost grows without bound for as long as
the simulation runs.

Measured 2026-09-04:

| History length | `snapshot()` | Share of a 200 ms frame at 5 Hz |
| ---: | ---: | ---: |
| 10 000 | 0.09 ms | 0.0% |
| 100 000 | 1.15 ms | 0.6% |
| 500 000 | 5.25 ms | 2.6% |

Linear, at roughly 10.5 us per thousand samples.

**Why it matters.** Invisible today and severe later, which is the shape of
defect worth recording before it bites. A one-hour case holds 36 000 samples
and costs about 0.4 ms a frame — nothing. The fast-forward feature the owner
wants (PL-011) makes runs days or weeks long: a week is 6 048 000 samples,
where the same copy is about 63 ms a frame, a third of the frame budget, and
allocates a fresh 48 MB tuple five times a second purely to be discarded.

It is also the wrong shape independent of cost. The view is handed the whole
run and then throws almost all of it away — `redraw_visible_window` slices to
the visible window and decimates that to at most
`MAX_CHART_POINTS_PER_SERIES` points. Nothing outside the window is ever
drawn, so nothing outside it needs to cross the boundary.

**Where.**

1. `src/anesthesia_sim/app/controller.py` — `snapshot()` and the
   `concentration_history` field of `SimulationSnapshot`.
2. `src/anesthesia_sim/app/chart_series.py` — `redraw_visible_window` is the
   only consumer, and it wants a window rather than a run.
3. `src/anesthesia_sim/app/simulation_view.py` — computes the window bounds
   it would pass.

**Approach.** Invert it: rather than the controller handing over the whole
run for the view to slice, the view asks for the window it is about to draw
and the controller answers with at most the points asked for. That makes the
read O(points drawn) instead of O(run length), removes the copy entirely, and
is the interface a tiered store (PL-011) would need anyway — so doing it
first makes that change additive rather than a rewrite.

Also fixes the smaller O(window) cost beside it: `redraw_series` builds a
`values` list over every visible sample, once per trace, per frame. Bounded
by the window today, unbounded if a future window is a week wide.

**Done when.** `snapshot()` performs no copy proportional to run length, the
per-frame cost of the render path is independent of how long the simulation
has run, and a test holds that — timing is too flaky to assert, so assert the
count of samples crossing the boundary instead.
