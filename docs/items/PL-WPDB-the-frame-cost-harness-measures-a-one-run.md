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

**Next steps, handed off 2026-10-01 for context length** by the thread that
closed `PL-624C` and `PL-JS0X` on this branch (`claude/test-fixes-ir36rr`,
draft `#1260`). The design below was worked out against the tree and not yet
written; nothing of it is committed.

1. **Open the dashboard the way `main.py` does**: `case =
   BranchedCase(SimulationController())`, then `SimulationView((case.trunk,),
   case=case)`. The harness builds `SimulationView((controller,))` with no
   case, so since `PL-VKJW` it has not measured the branch control's refresh,
   which reads a trunk snapshot every frame (`_refresh_fork_panel`), and its
   docstring's "the setup is the one `main.py` performs" has stopped being
   true. That moves the one-run configuration too, so re-measure it.
2. **Add `runs: int = DEFAULT_RUNS` (1) to `measure()` and `--runs` to
   `main()`**, choices 1 to `MAX_DISPLAYED_RUNS` (`app/dashboard_frame.py`),
   with `measure()` refusing any other value with `ValueError`. Each run past
   the first is `case.fork_at(0.0)`, taken before the warm-up, started, and
   warmed through the same `warm_up_s` as the trunk; it reaches the view by
   `view.add_run(branch)`, the route `_handle_fork` takes. Forking at
   induction gives the branch as much recorded history as the trunk, so this
   is the dearest two-run frame at that warm-up: a branch forked later draws
   only from its fork instant (`test_the_branch_is_drawn_beside_the_trunk_on_one_time_axis`).
   Say so in the docstring.
3. **Each measured frame advances every run `per_frame` steps inside
   `advance_s`**, as each run's own step timer does in the application, and
   the closing elapsed-time check runs per run.
4. **`Measurement.runs`, recorded from `len(view.runs)`** - what the dashboard
   drew rather than what was asked - and named on the report's first line.
5. **Tests in `test_frame_cost.py`**: `test_the_harness_measures_a_two_run_dashboard`
   (this item's `verify:`) on its own module-scoped short fixture
   (`multiplier=1`, two frames, 30 s warm-up, `runs=2`), asserting
   `runs == 2`, one sample per frame and every stage finite; the existing
   configuration test also asserts `runs == 1`; the report names the run
   count; `runs` of 0 and of `MAX_DISPLAYED_RUNS + 1` are refused.
6. **Record both columns**: the harness at its defaults three times with
   `--runs 1` and three with `--runs 2`, in one container, medians of each,
   written into the module docstring beside `PL-ZG5J`'s dated 2026-09-19
   figures and into this item. Keep those figures, since the stage-3 argument
   rests on them; the docstring gives that paint as both 13.1 ms and 15.5 ms,
   which the rewrite should reconcile.

Then close this item with the work (`bin/docket set PL-WPDB --status done
--closed DATE`, then `bin/docket record 1260`), run `make check` and `bin/docket
verify --self PL-624C PL-JS0X PL-WPDB`, ask `bin/docket arm` (it holds on the
`tests/` read), mark `#1260` ready, write its body, and post the review summary.
The `PL-624C` and `PL-JS0X` commit messages carry the mutation checks that
summary should report, and `PL-B1R9` is the finding filed on the way.
