---
id: PL-WPDB
title: The frame-cost harness measures a one-run dashboard, but v0.5.0 draws two runs on one chart, so the frame cost the branching milestone will actually pay is unmeasured
priority: P3
effort: S
status: ready
classes: infra, perf
feature: frame-cost-harness
touches: tests/benchmarks/frame_cost.py, tests/benchmarks/test_frame_cost.py
added: 2026-09-19
verify: grep -q 'def test_the_harness_measures_a_two_run_dashboard' tests/benchmarks/test_frame_cost.py
---

**Problem.** The frame-cost harness measures a one-run dashboard, but v0.5.0 draws two runs on one chart, so the frame cost the branching milestone will actually pay is unmeasured

**Why it matters.** `ROADMAP.md` § "v0.5.0 — the case you can branch" is a
milestone whose whole point is two runs on one axis, and
`app/dashboard_frame.py`'s `MAX_DISPLAYED_RUNS` is 2. `tests/benchmarks/frame_cost.py`
builds one `SimulationController`, so every number it prints is the cheaper
configuration: a second run adds its own readout row, its own control timeline
and a second set of traces on the shared chart, all inside the same 200 ms
`RENDER_INTERVAL_S` budget. The measured one-run frame is 40.4 ms of that
budget on this container (`PL-ZG5J`, 2026-09-19), so there is headroom — but
how much of it the second run spends is unknown, and a session deciding
whether v0.5.0 can afford something would be reading the wrong number.

**Not a defect in the harness.** `PL-ZG5J` deliberately measured what ships
today, and a two-run measurement made before the branching interface exists
would measure a guess at it.

**First step.** Once two runs can be driven together — `SimulationController.resumed_at`
already opens a branch — add a `--runs` argument to `measure()` and record
both columns. The report already carries the configuration it ran, so the
second is a parameter rather than a second harness.

**Done when.** `tests/benchmarks/frame_cost.py` can measure a two-run
dashboard and the frame split for it is recorded.
