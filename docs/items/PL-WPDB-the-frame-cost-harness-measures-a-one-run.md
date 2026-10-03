---
id: PL-WPDB
title: The frame-cost harness measures a one-run dashboard, but v0.5.0 draws two runs on one chart, so the frame cost the branching milestone will actually pay is unmeasured
priority: P3
effort: S
status: done
classes: infra, perf
feature: frame-cost-harness
milestone: v0.5.21
touches: tests/benchmarks/frame_cost.py, tests/benchmarks/test_frame_cost.py
added: 2026-09-19
closed: 2026-10-01
pr: 1260
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

**Done 2026-10-01, on `claude/test-fixes-ir36rr` with `PL-624C` and `PL-JS0X`.**
The thread that closed those two worked out the design against the tree and
handed it off for context length; a second thread wrote it. `measure()` takes
`runs` (1 by default, up to `MAX_DISPLAYED_RUNS`) and `main()` takes `--runs`,
and a count the dashboard cannot draw is refused with `ValueError` before the
warm-up. The dashboard is opened as `main.py` opens it, a `BranchedCase` over a
fresh trunk and the view over that trunk with the case, so the branch control's
per-frame refresh is now measured too. Each run past the first is
`case.fork_at` at induction, taken before the warm-up and warmed alongside the
trunk, and reaches the shown dashboard by `view.add_run`. Each measured frame
advances every drawn run `steps_per_frame` steps, and the closing elapsed-time
check runs per run. `Measurement.runs` is counted on the dashboard and named on
the report's first line.

**One step the handoff did not have: the chart is scrolled into view before
measuring.** The event loop paints only what is in view, and at the harness's
1600 x 1000 window a second run's readouts push the concentration chart below
the fold. Measured with a probe under the offscreen platform: the one-run
chart spans y 520-880 of the 1000 px page viewport and the two-run chart
848-1208, and with the chart left there the two-run paint read 5.5 ms against
one run's 14.9 ms, three invocations each. That is the flattering direction the
harness exists to refuse, so `_bring_chart_into_view` scrolls the page with
`ensureWidgetVisible` and raises `RuntimeError` if the chart is still not
wholly in view. At this size it moves nothing on the one-run dashboard. A
reader comparing two runs scrolls to the chart, so that is the frame measured.
Taken as the clearly correct call rather than put to the owner; the layout
finding itself is filed separately.

**The two columns,** at the harness's defaults (300x, 20 frames, an hour of
warm-up), 2026-10-01 in the web container, medians over three invocations of
each, alternated:

| | advance | present | paint | frame | of 200 ms |
| --- | --- | --- | --- | --- | --- |
| one run | 12.8 ms | 16.8 ms | 14.2 ms | 44.2 ms | 22% |
| two runs | 25.1 ms | 30.2 ms | 13.7 ms | 68.9 ms | 34% |

The control (`settled_s`) read 0.17-0.27 ms throughout. The second run doubles
the simulation and nearly doubles the assembly. The paint holds level while
rasterizing a different chart: comparing caps it at two compartments a run
(`COMPARED_COMPARTMENT_CAP`), so it draws four curves where one run draws six,
the trunk's at 5 px where one run's are 2-3 px. `main`'s harness, without the
case, read 44.2 ms in the same container, so opening over a case moved the
one-run frame by less than the spread between invocations, and the move from
`PL-ZG5J`'s 40.4 ms of 2026-09-19 is the container or the tree since then.
`PL-ZG5J`'s figures stay in the docstring, since the stage-3 argument rests on
them; its stray 15.5 ms, the throwaway reading's paint, is gone from the
control paragraph.

**Tests,** in `tests/benchmarks/test_frame_cost.py`: a second module-scoped
fixture at 1x over a 30 s warm-up with `runs=2`;
`test_the_harness_measures_a_two_run_dashboard`; the configuration test also
asserts `runs == 1`; `test_the_report_names_how_many_runs_were_drawn`; and
`test_a_run_count_the_dashboard_cannot_draw_is_refused` for 0 and
`MAX_DISPLAYED_RUNS + 1`. Each fails under a matching break of the harness,
checked by mutation: the branch never added to the dashboard, only the first
run advanced each frame, the run-count check removed, and the scroll removed.
