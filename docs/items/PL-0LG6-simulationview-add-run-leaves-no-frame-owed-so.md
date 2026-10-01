---
id: PL-0LG6
title: SimulationView.add_run leaves no frame owed, so a caller that does not present afterwards leaves the plot on the old run set while the legend already names the new one; both fork handlers present at once, so no shipped path reaches it
priority: P2
effort: S
status: ready
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_simulation_view.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
payoff: a run added to the dashboard is drawn on the next tick whoever adds it, so the plot can never lag the legend that names it
verify: grep -q 'def test_a_run_added_to_a_paused_dashboard_is_drawn_on_the_next_tick' tests/integration/test_simulation_view.py
---

**Problem.** SimulationView.add_run leaves no frame owed, so a caller that does not present afterwards leaves the plot on the old run set while the legend already names the new one; both fork handlers present at once, so no shipped path reaches it

**Found 2026-10-01** while fixing `PL-B1R9` (#1262). `add_run` places the run
and tells both legends and every run the new count through `_rename_runs`, and
draws nothing: its docstring promises the run "from the next frame on". The
legends change at once - the compare rows name both runs, and from a selection
wider than `COMPARED_COMPARTMENT_CAP` the trace legend unchecks all but the
capped pair - while the plot keeps the last frame it drew. Nothing marks a
frame owed, and `render_tick` draws only while a run is running or a frame is
owed, so on a paused dashboard the plot and the legend disagree until something
else presents.

No shipped path reaches it. `_handle_fork` and `_handle_halt_fork` call
`present(False)` straight after `add_run`, and the frame-cost harness presents
after it too. Before `PL-B1R9` a wide selection hid the gap, because the
legend's own announcement drew a frame from inside `add_run`; from a selection
already inside the cap it was there all along. `TraceLegend`'s docstring makes
its agreement with the plot "a property of the code rather than of somebody's
diligence", and today the dashboard half of that rests on every caller of a
public method remembering to present.

**Candidate fix.** `add_run` ends with `self.present(True)`, owing a frame
rather than drawing one. A fork still draws exactly once, because the handler's
`present(False)` discharges the owed frame (`present` clears the pending flag
before drawing), and a direct caller gets the frame on the next render tick
even while paused. `test_a_fork_from_the_default_selection_draws_one_frame`
already holds the once.

**Why it matters.** The plot and its legend are one display read together, and a legend naming two runs over a plot drawing one is the stale-state presentation error `CLAUDE.md`'s safety standard names. It is latent, since both fork handlers present at once, so the exposure is the next caller of a public method, and the fix is one line.

**Done when.** A test adds a run to a paused dashboard without presenting, runs
one `render_tick`, and finds both runs in the drawn frame; and taking a branch
still draws exactly one frame.

**Reproduced 2026-10-01.** `add_run` in `src/anesthesia_sim/app/simulation_view.py` makes no `present` call: an awk over the method matches only its docstring and its `return`.
