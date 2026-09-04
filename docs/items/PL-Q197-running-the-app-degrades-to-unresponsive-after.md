---
id: PL-Q197
title: Running the app degrades to unresponsive after about a minute: sliders move but stop updating values
priority: P1
effort: M
status: done
classes: defect, safety
touches: src/anesthesia_sim/app/chart_downsampling.py, src/anesthesia_sim/app/chart_series.py, tests/unit/test_chart_downsampling.py, tests/integration/test_chart_patching.py
added: 2026-09-04
closed: 2026-09-04
pr: 297
verify: uv run pytest tests/integration/test_chart_patching.py tests/unit/test_chart_downsampling.py && grep -q 'def test_a_growing_run_does_not_grow_the_traffic_it_sends' tests/integration/test_chart_patching.py
---

**Problem.** Reported by the project owner, 2026-09-04, running `make run`
locally. The app degraded progressively over roughly a minute until it stopped
responding to input, while the simulation kept advancing at a crawl. Sliders
still moved under the pointer; their value readouts stopped updating. The
owner then observed the decisive fact: the Flet (Flutter) client process was
pegged at 100% CPU while the Python process was not.

**Diagnosis — measured, not inferred.** `tests/integration/test_chart_patching.py`
already provided a real `flet.messaging.connection.Connection` that serializes
outbound messages exactly as the WebSocket transport does. Counting the patch
operations in one steady-state render frame against run age:

| Run age (s) | Drawn points/trace | Patch ops/frame | Ops/s at 5 Hz | Bytes/frame |
| ---: | ---: | ---: | ---: | ---: |
| 20 | 204 | 24 | 120 | 1 989 |
| 30 | 298 | 2 708 | 13 540 | 50 893 |
| 60 | 298 | 2 681 | 13 405 | 50 271 |
| 300 | 298 | 3 583 | 17 915 | 66 917 |

The cost was never the data. 50-67 kB a frame is roughly 250-330 kB/s, which
no modern machine should notice. It was that the data arrived as ~3 500
discrete control mutations, each of which the Dart side decodes, routes
through the control tree, marks dirty and repaints.

**Root cause.** `select_envelope_indices` returned `list(range(sample_count))`
while the visible window still fitted inside `MAX_CHART_POINTS_PER_SERIES`
(300) — the first 30 s at `SIMULATION_STEP_S = 0.1` — over which the mapping
from output slot to source sample is the identity, so only newly appended
points were dirty. Past 30 s decimation engaged, and its bucket boundaries
were `(bucket * sample_count) // bucket_count`: recomputed every frame against
a sample count that moved every frame. Every slot therefore held a *different
sample* each frame, and all 298 points x 6 traces x (x, y) came out dirty.

This defeated PL-010's in-place point reuse rather than being caused by it.
Reuse removed the cost of *constructing* a point per sample per frame; it
cannot remove the patch, because the selection underneath it was unstable.

The unresponsiveness followed: `_run_render_timer` pushes a frame every
`RENDER_INTERVAL_S` with no back-pressure, so once the client rendered slower
than 5 Hz the backlog grew without bound and slider readout patches queued
behind thousands of chart patches. A Flutter `Slider` repaints its own drag
locally, which is why the thumb stayed live while its readout froze.

**Fix.** Buckets are anchored to *absolute* sample index (`index_offset`)
rather than to position within the visible slice, so a bucket lying wholly
inside the window chooses the same sample on every frame and the client is
told nothing about it. Holding that anchor as the window grows needs the
bucket width to change in steps rather than continuously, so
`_stable_bucket_width` doubles — about eight rebuilds over a five-minute run
instead of five per second.

Measured after, over 80 consecutive frames:

| Run age (s) | Mean ops/frame | Peak | Mean ops/s | Was |
| ---: | ---: | ---: | ---: | ---: |
| 60 | 20 | 23 | 98 | 13 405 |
| 300 | 221 | 2 209 | 1 106 | 17 915 |
| 600 | 271 | 2 193 | 1 354 | ~17 600 |

**Deliberately not done.** Frame dropping was proposed and rejected by the
project owner: needing it at this workload would have been a red flag hiding
the defect rather than fixing it, and the measurements bore that out.

**Residual, and why it is a floor.** Past `MAX_CHART_WINDOW_S` the window
slides along a fixed grid, so it spans alternately `k` and `k + 1` buckets;
the count of chosen samples must change, and any change shifts every later
point one position along a positional list. One rebuild per bucket width
survives. Removing it needs either snapping the axis onto bucket boundaries
(which makes a smooth scroll jerk) or decimating from before `min_x` and
trusting the chart to clip — the latter was implemented, measured at only
1.7x better, and reverted rather than ship an unverifiable dependency on
fl_chart's clipping. `PL-YDKJ` carries the architectural question underneath
it.

**Cost paid.** The width ladder spends between half the point budget and all
of it, so a saturated trace now draws ~184 points where it drew 298. Both
documented presentation-correctness properties survive: every bucket's
minimum and maximum are still drawn, so no transient can be hidden, and the
last recorded sample is still selected, so the right-hand end of every trace
still agrees with the numeric readouts.

**Guards added.** `test_select_envelope_indices_holds_its_choices_as_the_run_grows`
and `test_select_envelope_indices_is_anchored_to_the_run_not_the_window` hold
the pure property; `test_a_growing_run_does_not_grow_the_traffic_it_sends` and
`test_a_scrolling_window_rebuilds_only_at_a_bucket_boundary` hold it end to end
in the units that actually saturated the client.
