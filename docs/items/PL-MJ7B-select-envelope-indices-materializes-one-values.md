---
id: PL-MJ7B
title: select_envelope_indices materializes one values list per trace per frame, and removing it is a constant-factor win the item that asked for it read as an asymptotic one
status: untriaged
added: 2026-09-04
---

**Problem.** `chart_series.redraw_series` builds `values = [value_for(sample)
for sample in visible]` once per trace per frame — six lists the length of
the visible window, five times a second, allocated only to be read by
`chart_downsampling.select_envelope_indices` and discarded. `PL-0VM7`'s
Approach asked for this to go, on the grounds that the cost is "unbounded if
a future window is a week wide". That reasoning does not hold, which is why
the change was not made with the rest of the item.

**Why it matters.** Two separate things, and only the first is real.

Measured 2026-09-04 against the saturated 3 001-sample window
(`MAX_CHART_WINDOW_S / SIMULATION_STEP_S`), per frame across all six traces:

| | Per trace | Six traces |
| --- | ---: | ---: |
| Today: `values` list, then `select_envelope_indices` | 0.192 ms | 1.14 ms |
| `values` list, bucket extremes cached in locals | 0.170 ms | — |
| No `values` list, bucket extremes cached in locals | 0.137 ms | 0.85 ms |

So the change is worth about 0.29 ms a frame, 0.14% of the 200 ms frame at
`RENDER_INTERVAL_S`. Real, and free of any correctness cost — the three
selections agree index for index.

What it is *not* is the fix its stated motivation asks for. Min/max envelope
decimation has to read every sample of every bucket to find that bucket's
extremes, so the scan is O(window) whether a list is materialized or not.
Removing the list changes the constant, never the exponent. A week-wide
window is 6 048 000 samples scanned six times a frame at 5 Hz: infeasible
under either version by three orders of magnitude. What that case needs is
bucket extremes maintained incrementally as samples are appended — O(1) per
recorded sample, O(buckets) per frame — which is the tiered store `PL-011`
carries, and which `SimulationController.history_window()` (added by
`PL-0VM7`) is already the interface for.

**Where.**

1. `src/anesthesia_sim/app/chart_series.py` — `redraw_series` builds the
   list, and uses it again to write each drawn point's `y`.
2. `src/anesthesia_sim/app/chart_downsampling.py` —
   `select_envelope_indices(values, max_points, index_offset)` would become
   generic over a sample sequence and an accessor, which is the shape
   `first_index_at_or_after` in the same module already has.
3. `tests/unit/test_chart_downsampling.py` — eighteen call sites pass plain
   float lists, and each would need an accessor.

**The decision this item is really about.** Whether 0.14% of a frame is worth
making a clean pure function over a value sequence into a generic one over
samples plus an accessor, and rewriting its eighteen test call sites.
`chart_downsampling.py` is `src/`, held to the specialist standard, and the
current signature is the simpler of the two. Caching the bucket extremes in
locals is the part with no such cost: it is internal to
`select_envelope_indices`, changes no signature and no test, and is worth
roughly 0.13 ms of the 0.29 ms on its own.

**Done when.** Either the split is taken — extremes cached, `values` list
kept — or the whole change is made deliberately with the trade above
recorded, or the item is dropped with the measurement as its reason.
