---
id: PL-2WVC
title: For up to one render tick after a dial click on a running run, the readouts and the compartment schematic show a later step than the charts, on main as on the PL-RF2S branch
priority: P2
effort: S
status: ready
classes: defect
feature: every-view-in-run-state-tests
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/simulation_view
deferred-from: v0.7.0 - present at the freeze, but it waits on PL-RF2S, whose third pull request fixes it and which is itself deferred to the next gate; each value shown is right for its own step, so it shows no wrong value
added: 2026-11-11
payoff: Every part of the screen shows the same step after a dial click, so a readout never disagrees with the chart beside it.
---

**Problem.** For up to one render tick after a dial click on a running run, the readouts and the compartment schematic show a later step than the charts, on main as on the PL-RF2S branch

**Found on 2026-11-11 by a review of `PL-RF2S`'s second pull request, and not
fixed there.** A dial click on a running run applies the setting and asks for a
frame at once. Until the next render tick, the run's readouts and the
compartment schematic show the step after the click, and both charts still
show the frame before it. The reviewer saw the same on `main` at `35294da61`
and on the branch at `70dbdc525`. Its script was
`repro5_readouts_ahead_of_chart.py` in that session's scratchpad, which does
not outlive the session.

**Where it may belong.** `PL-RF2S`'s third pull request puts the chart frame
for each window into the one value that the whole screen is drawn from. The
readouts and the charts would then come from one state on every draw. Triage
decides whether this item closes with that pull request or is dropped as a
difference of one tick (0.2 s) that no learner can act on.

**Checked 2026-11-22**, at `d4e8200c`. The lag is there by design. `SimulationView.present` in `app/simulation_view.py`, given `coalesce=True` by a dial change, hands every View the runs at once and leaves the charts to the render tick, which `RENDER_INTERVAL_S` in `app/dashboard_frame.py` sets at 0.2 s. The same split was present at the freeze: `git show 0947408:src/anesthesia_sim/app/run_view.py` already rewrote a run's own readouts at once on a coalesced change and left the frame to the render tick. `PL-RF2S` (drawing every View whole from one value) is still `ready`, and its third pull request has not landed.

**Why it matters.** For up to 0.2 s after a dial click, the readouts and the schematic show the step after the click while both charts still show the step before it. Each value is right for its own step, so nothing shown is wrong. But a learner comparing a readout with the end of a chart's curve in that moment sees two numbers that disagree. The screen should be drawn from one state.

**Done when.** After a dial click on a running run, the readouts, the schematic and the charts on every frame show the same step. A test reads all three in the frame after the click.

[superseded 2026-11-22: `PL-RF2S` closed and did not remove the lag; see "Checked 2026-11-22" below.] **Disposition, decided 2026-11-22.** Kept rather than dropped, and blocked on `PL-RF2S`. Its third pull request puts the chart frame into the one value the whole screen is drawn from, which removes this lag, and this item is the check that it does. Dropping it as a one-tick difference would leave nothing to confirm that.

**Generator check.** An instance of the fact that `PL-RF2S` states, "Which widgets state a run's current state, and that each is restated on every path that changes it". `PL-RF2S` is still open, so this is a member of that head rather than a re-entry.

**Checked 2026-11-22, when `PL-RF2S` closed with its fourth pull request.** Neither the third nor the fourth pull request removed the lag, so this item is not settled by them. `SimulationView.present(True)` in `app/simulation_view.py` still hands every View the runs with no frame, and `RunView._refresh_against_last_frame` in `app/run_view.py` still rewrites the run's own panel at once from the snapshot read after the change. A chart handed a tick with no frame keeps the frame it last drew, so for up to one render tick (0.2 s) the readouts, the dials, the schematic and the accounting panel show the step after the click and the charts the step before it. `PL-RF2S`'s new test (`test_every_registered_view_draws_a_state_alike_whatever_it_drew_before`) does not reach this case, because each state of its walk ends with a frame drawn at once.

What a fix would take. Every dial change reaches `RunView._apply_setting` with `coalesce=True` (`_handle_fresh_gas_flow_change` and the three beside it). The release of a held thumb already draws one frame at once (`test_a_dragged_slider_leaves_its_frame_to_the_render_tick`, `PL-R2YM`, `PL-5B1N`). A click on the groove, a key press and a wheel step are each one discrete input (`ParameterSlider`'s docstring in `app/qt_widgets.py`), and they are the ones that still wait for the render tick. A fix would draw a frame at once for those inputs, as a release does. Under Fusion, holding the button on the groove repeats the step, and each repeat would then draw a frame, which is the cost that coalescing avoids, so the fix has to keep repeats coalesced. It is a small change in `app/run_view.py` and `app/qt_widgets.py` with its tests, but it changes how often a frame is drawn while a learner holds a key or the groove, so it is not built under `PL-RF2S`.
