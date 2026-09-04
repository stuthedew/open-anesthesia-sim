---
id: PL-Q197
title: Running the app degrades to unresponsive after about a minute: sliders move but stop updating values
status: untriaged
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/chart_series.py, src/anesthesia_sim/app/chart_downsampling.py, tests/integration/test_chart_patching.py
added: 2026-09-04
---

**Problem.** Reported by the project owner, 2026-09-04, running `make run`
(`uv run anesthesia-sim`) locally. The app degrades progressively over roughly
a minute until it stops responding to input, while the simulation keeps
advancing at a crawl. Sliders still move under the pointer; their value
readouts stop updating.

The owner then observed the decisive fact: **the Flet (Flutter) client process
is pegged at 100% CPU while the Python process is not.** That rules out
per-tick simulation cost and points at the volume of UI state being pushed at
and re-rendered by the client.

**Diagnosis — measured, not inferred.** `tests/integration/test_chart_patching.py`
already provides a real `flet.messaging.connection.Connection` that serializes
outbound messages exactly as the WebSocket transport does. Counting the patch
operations in one steady-state render frame against run age, on that harness:

| Run age (s) | Drawn points/trace | Patch ops/frame | Ops/s at 5 Hz | Python ms/frame |
| ---: | ---: | ---: | ---: | ---: |
| 2 | 24 | 24 | 120 | 7.4 |
| 5 | 54 | 25 | 125 | 10.0 |
| 10 | 104 | 22 | 110 | 15.9 |
| 20 | 204 | 24 | 120 | 27.2 |
| 30 | 298 | 2708 | 13540 | 72.1 |
| 60 | 298 | 2681 | 13405 | 50.0 |
| 120 | 298 | 2659 | 13295 | 52.0 |
| 300 | 298 | 3583 | 17915 | 82.6 |
| 600 | 298 | 3523 | 17615 | 87.9 |

Client-bound patch traffic steps up about **150-fold** between 20 s and 30 s of
runtime, and the step lands exactly where theory puts it.

**Root cause.** `select_envelope_indices` returns `list(range(sample_count))`
while the visible window still fits inside `MAX_CHART_POINTS_PER_SERIES` (300).
At `SIMULATION_STEP_S = 0.1` that holds for the first 30 s, and over that span
the mapping from output slot to source sample is the identity: slot *i* always
holds sample *i*, so only newly appended points are dirty and a frame patches
about two dozen fields.

Past 30 s decimation activates, and it is **re-derived from scratch every
frame** over a window whose sample count has changed. Bucket boundaries are
computed as `(bucket * sample_count) // bucket_count`, so every boundary moves
whenever `sample_count` moves — which is every frame. Slot *i* therefore holds a
*different sample* each frame, and all 298 points x 6 traces x (x, y) come out
dirty. At 300 s essentially every coordinate of all 1 788 drawn points is
rewritten 5 times a second.

This defeats PL-010's in-place reuse rather than being caused by it. Reuse
removed the cost of *constructing* a point per sample per frame; it cannot
remove the patch, because the selection underneath it is unstable, so the wire
traffic is what a full rebuild would have sent.

The unresponsiveness is the second-order effect. `_run_render_timer` sleeps a
fixed `RENDER_INTERVAL_S = 0.2` and pushes a frame unconditionally, with no
back-pressure and no frame dropping. Once the client renders slower than 5 Hz,
the backlog grows without bound, displayed state falls further and further
behind, and slider readout patches queue behind thousands of chart patches. A
Flutter `Slider` animates its own thumb locally, which is why the thumb stays
live while its readout is frozen. Python stays off the pegged core because
50-88 ms of work per 200 ms budget is only 25-44% of one core.

**Why it matters.** The app is unusable within a minute, shorter than any
teaching case. It also crosses the safety-critical presentation line twice: a
slider whose position no longer matches the value driving the model displays a
control setting the simulation is not using, and a chart lagging seconds behind
the readouts beside it is the stale-picture failure
`tests/integration/test_chart_patching.py` was written to prevent — arriving
through latency instead of through a missed diff.

**Where.**

1. `src/anesthesia_sim/app/chart_downsampling.py` — `select_envelope_indices`
   is the root cause. Its bucket grid must be anchored so that a completed
   bucket keeps its membership as the run grows, instead of being recomputed
   against a moving `sample_count`.
2. `src/anesthesia_sim/app/simulation_view.py` — `_run_render_timer` needs to
   drop frames rather than queue them when the client is behind.
3. `src/anesthesia_sim/app/chart_series.py` — `redraw_series` is correct as
   written and is not the fault; it inherits an unstable selection.

**Done when.** Steady-state patch operations per frame stay bounded by a small
constant that does not grow with run age, with a regression test built on the
existing `_RecordingConnection` harness asserting that bound at several run
ages — the measurement above is already most of that test. Two properties
`chart_downsampling.py` documents as presentation-correctness requirements must
survive the change: every bucket's minimum and maximum are still drawn, so no
transient can be hidden, and the last recorded sample is still selected, so the
right-hand end of every trace still agrees with the numeric readouts. Input
must stay responsive over a run long enough to cover a teaching case.
