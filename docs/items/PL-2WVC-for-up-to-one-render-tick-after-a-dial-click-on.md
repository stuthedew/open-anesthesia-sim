---
id: PL-2WVC
title: For up to one render tick after a dial click on a running run, the readouts and the compartment schematic show a later step than the charts, on main as on the PL-RF2S branch
priority: P2
effort: S
status: done
classes: defect
feature: every-view-in-run-state-tests
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/simulation_view
deferred-from: v0.7.0 - present at the freeze, but it waits on PL-RF2S, whose third pull request fixes it and which is itself deferred to the next gate; each value shown is right for its own step, so it shows no wrong value
added: 2026-11-11
closed: 2026-11-22
pr: 2257
payoff: Every part of the screen shows the same step after a dial click, so a readout never disagrees with the chart beside it.
tests: tests/integration/simulation_view/test_simulation_view_controls.py::test_one_input_on_a_dial_of_a_running_run_draws_every_part_of_the_screen_at_one_step
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

**Done 2026-11-22.** What was wrong: every dial change reached `RunView._apply_setting` with `coalesce=True`, whatever the input. So one key press, one wheel notch or one click on the track rewrote the run's own readouts at once, `SimulationView.present(True)` handed every View the runs with no frame, and both charts kept the frame they last drew until the render tick, up to 0.2 s later.

The fix tells one input apart from a held input's repeat, where the input arrives. `_SettingSlider` in `app/qt_widgets.py` sets `repeating` while Qt handles a held key's repeat (`QKeyEvent.isAutoRepeat`), a trackpad swipe after the event that began it, or the timer by which Qt repeats a press held on the track. `ParameterSlider.value_changed` now carries a `DialInput` beside the value: `DISCRETE`, `REPEAT`, or `RELEASE` for the value applied when a dragged thumb is let go. The kind travels through `ParameterControls.setting_requested`, `ViewRequests.setting` and `SimulationView._handle_setting_request` to `RunView.request_setting`, which coalesces only a `REPEAT` or a `RELEASE`. A `DISCRETE` input draws its frame at once, as Start or a refused setting already did. A `RELEASE` stays coalesced because `end_preview` draws the frame at once right after it, so a release still draws exactly one frame. A held thumb's movements, a held key and a press held on the track still draw on the render tick, so the dials respond as before and no frame is drawn for every repeat.

Why this route: it is the item's own sketch, and the input kind is known only at the slider. The alternatives were weaker. Drawing at once for every dial change would draw a frame for every repeat of a held key (about 30 a second). Deferring the readouts to the render tick as well would make the value beside the dial lag the dial (`PL-018`). What a learner sees: after one key press, wheel notch or click on the track, every part of the screen shows the new step at once. During a held key or held press, the readouts can still run up to one render tick ahead of the charts, as before.

Test: `tests/integration/simulation_view/test_simulation_view_controls.py::test_one_input_on_a_dial_of_a_running_run_draws_every_part_of_the_screen_at_one_step`, for an arrow key, a wheel notch and a click on the track. The run's last frame is at 0 s, the run takes 30 steps with no frame, and one input follows. It reads the readout clock, the schematic's heading and both charts' frames, and expects 30 s in each, written out by hand. Before the fix, `uv run pytest -q tests/integration/simulation_view/test_simulation_view_controls.py -k one_input_on_a_dial` failed all three cases with `AssertionError: assert {'readout clo...-in chart': 0} == {'readout clo... chart': 30.0}`, the differing items being `{'concentration chart': 0} != {'concentration chart': 30.0}` and `{'wash-in chart': 0} != {'wash-in chart': 30.0}`. `tests/integration/test_qt_widgets.py::test_each_applied_value_says_whether_one_input_or_a_repeat_applied_it` checks that each input is classed correctly, including a press held on the track for 700 ms under Fusion. `test_the_render_tick_draws_a_pending_change_while_the_run_is_stopped` now drives its owed frame with a held key's repeat, because a programmatic step is one input and draws at once. For the same reason, `test_a_dial_moved_in_one_view_sets_the_run_and_moves_the_dial_in_the_other` in `tests/integration/test_run_surfaces.py` and `test_a_dial_moved_in_a_workspace_pinned_to_the_second_run_sets_that_run_alone` in `tests/integration/test_workspace_tabs.py`, which check the tick that hands every View the runs with no frame, now move the dial with a held key's repeat, to 4.1 L/min rather than 7.0 L/min.

Files checked: `docs/INTERFACE.md` and `docs/ARCHITECTURE.md`, with `grep -n -i "coalesc\|render tick\|wheel\|key press\|click on the \(track\|groove\)\|discrete input\|PL-R2YM\|PL-018\|dragged\|held key\|repeat"`. `docs/ARCHITECTURE.md` line 958 ("a dragged dial still leaves the charts to the render tick") is still true, because a held thumb's preview is still coalesced. `docs/INTERFACE.md` § on a drag applying at release now says that one input draws the whole screen at once and a held input's repeats are drawn on the render tick. The docstrings of `SimulationView.present`, `RunView._apply_setting`, `RunView._refresh_against_last_frame`, `RunView.presentation_requested`, `ParameterSlider` and `_SettingSlider` were updated to match.
