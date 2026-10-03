---
id: PL-B1R9
title: Taking a branch from a wide legend selection draws two frames, the first from inside _rename_runs before the wash-in legend and the run names are told there are two runs
priority: P3
effort: S
status: done
classes: defect, perf
milestone: v0.5.21
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/qt_chart.py, tests/integration/test_simulation_view.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science: the extra frame is never painted
added: 2026-10-01
closed: 2026-10-01
pr: 1262
payoff: a branch costs one frame rather than two, and no frame is assembled from a run set half told that it has grown
verify: grep -q 'def test_a_fork_from_the_default_selection_draws_one_frame' tests/integration/test_simulation_view.py
---

**Problem.** Taking a branch from a wide legend selection draws two frames, the first from inside _rename_runs before the wash-in legend and the run names are told there are two runs

**Measured 2026-10-01** on `main` at `f6a146e4`, while working `PL-624C`, by
wrapping `SimulationView._refresh_view` and printing the stack of every frame
a fork drew. From the default legend selection, `_take_fork(view, 60.0)`
raises `presented_frames` by two:

1. `_handle_fork` -> `add_run` -> `_place_run` -> `_rename_runs` ->
   `self._legend.set_run_count(2)` -> `set_shown(drawn)`, because the default
   selection is wider than `COMPARED_COMPARTMENT_CAP` ->
   `visibility_changed.emit()` -> `_handle_trace_visibility_change` ->
   `present(False)`.
2. `_handle_fork`'s own `present(False)`.

The first frame is assembled while `_wash_in_legend` still holds a run count of
one and before `set_run_name` and `set_comparing` have reached either run, so it
is drawn from a run set only half told that it has grown. From a selection
already inside the cap the legend has nothing to announce, and the press draws
once.

**Why it matters.** Nothing wrong reaches the screen today: both frames are
drawn inside the click, before the event loop turns, so only the second is
painted. What it costs is a whole frame assembly thrown away on every fork, a
discrete action that draws twice where `PL-R2YM` says once, and a frame
assembled from an intermediate state, which `present`'s guard would turn into a
halt of every run if that state ever made assembly raise. Any later
`_rename_runs` caller whose change makes the legend cap a selection inherits the
same ordering.

It also costs a test its precision. `test_taking_a_fork_redraws_the_chart_without_prompting`
narrows the legend to the capped pair so that the press is the only thing that
can draw, because from the default selection the legend's redraw stands in for
the fork's own and hides its loss: with `_handle_fork`'s `present(False)`
removed, `test_the_branch_is_drawn_beside_the_trunk_on_one_time_axis` still
passed (verified 2026-10-01).

**Fix, not yet decided.** Either `_rename_runs` holds the legends'
announcements until it has finished and leaves the redraw to its caller, or
`set_run_count` stops announcing and every caller redraws. The first keeps the
change inside the view; the second changes a public method's contract.

**Decided 2026-10-01, by the session that fixed it: the second.**
`TraceLegend.set_run_count` no longer announces; `set_shown` still does, and
both hold the selection to the cap through `_check_exactly`. Three reasons.
`visibility_changed` was already documented as "Emitted after a reader shows
or hides a compartment", so the emission from `set_run_count` was the anomaly,
and the change makes the code say what the signal's contract already said.
Every caller already owes a frame for the larger change it is making - the
press that took a branch, the Reset that drops one, `main()` after the window
is shown - so the announcement was never the only thing that would draw. And
the first option, blocking the legend's signals inside `_rename_runs`, drops
the announcement rather than holding it, while `set_run_count` would go on
documenting one: two files describing one behaviour differently, and any
caller of `set_run_count` outside `_rename_runs` inheriting the early frame.
One consequence: `add_run` called directly no longer draws from a wide
selection, which its "from the next frame on" already allowed; no caller in
the tree relied on it.

**Verified 2026-10-01 by mutation**, with the fix in place.
`test_a_fork_from_the_default_selection_draws_one_frame` fails at both doors
with the announcement restored (two frames per press); at the keyframe door
with `_handle_fork`'s `present` removed, and at the halt door with
`_handle_halt_fork`'s; and on its run-set assertion alone with the
announcement restored and `_handle_fork`'s `present` removed - one frame, the
legend's, assembled while the wash-in legend counted one run and neither run
was named. `test_the_branch_is_drawn_beside_the_trunk_on_one_time_axis`, which
passed with `_handle_fork`'s `present` removed before the fix, now fails.

**Done when.** Taking a branch draws exactly one frame from any legend
selection, and a test takes a fork from the default selection and asserts that
`presented_frames` rose by one.
