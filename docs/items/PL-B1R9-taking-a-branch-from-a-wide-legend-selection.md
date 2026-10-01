---
id: PL-B1R9
title: Taking a branch from a wide legend selection draws two frames, the first from inside _rename_runs before the wash-in legend and the run names are told there are two runs
priority: P3
effort: S
status: ready
classes: defect, perf
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/qt_chart.py, tests/integration/test_simulation_view.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science: the extra frame is never painted
added: 2026-10-01
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

**Done when.** Taking a branch draws exactly one frame from any legend
selection, and a test takes a fork from the default selection and asserts that
`presented_frames` rose by one.
