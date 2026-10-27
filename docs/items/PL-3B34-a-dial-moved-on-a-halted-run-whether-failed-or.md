---
id: PL-3B34
title: A dial moved on a halted run, whether failed or stopped at the 24-hour supported run length, is applied to the core and recorded as a control change at the halt instant, so the settings readouts and the control-change record show a setting that no step ever ran under beside concentrations computed under the previous one, while the banner says the values shown are the last completed step
priority: P1
effort: M
status: done
classes: defect, ux, safety
feature: replay-findings
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/dashboard_frame.py, docs/MODEL.md, docs/ARCHITECTURE.md, tests/integration/test_controller.py, tests/integration/test_simulation_view.py, tests/unit/test_dashboard_frame.py
added: 2026-10-25
closed: 2026-10-27
pr: 1846
payoff: the settings shown beside a halted run's concentrations are the ones those concentrations were computed under, so a learner cannot pair a value with a setting no step ran
verify: grep -q 'def test_a_setting_changed_on_a_halted_run_is_not_shown_as_the_setting_its_values_ran_under' tests/integration/test_simulation_view.py
reenters: PL-X7D5
---

**Problem.** The controller's setters have no halt check
(`set_cardiac_output` and its siblings in `app/controller.py`). `RunView._apply_setting` forwards a setting
to a halted run like any other (`app/run_view.py`). Only the
transport and the agent selector change state on a halt
(`RunView._write_transport`). So after a run halts, moving the cardiac output
dial from 5.0 to 10.0 L/min is accepted. It adds a `ControlChange` at the
halt instant, and the settings readout then shows 10.0 L/min. Every
concentration on screen was computed at 5.0 L/min, and no later step will
integrate the change. Keeping the controls live is a ratified decision
(`docs/MODEL.md` § "Reasonably foreseeable misuse, and the hazards the presentation carries", `PL-V2HC`, 2026-10-12). Locking them is therefore not
the fix asked for here. What needs deciding is how such a change is recorded
and shown on a run that cannot step again.

**Why it matters.** The banner says "The values shown are the last completed
step". A learner reads those concentrations as the result at the setting
shown beside them, which is the stale-state misreading that the safety
standard names. The control-change record also claims an intervention at
24:00:00 that never acted on the patient. Every long run now ends in this
state.

**Done when.** A setting moved on a halted run, failed or stopped at the supported run length, is never shown beside the halted values as the setting they were computed under, and the control-change record does not claim it acted on the patient. The controls stay live. `tests/integration/test_simulation_view.py` has `test_a_setting_changed_on_a_halted_run_is_not_shown_as_the_setting_its_values_ran_under`, which halts a run at a shortened supported run length, moves the cardiac output dial, and checks the settings readout and the record.

**Found by.** `PL-TBQS` reviewer replay on #204, finding r06 F1, and on
#421, finding r04 F2. Checked against main on 2026-10-25. Reproduced with the
span shortened to 50 steps, as
`test_a_run_that_arrives_at_the_supported_run_length_under_its_own_timers_is_redrawn`
does. After the limit, `set_cardiac_output(CardiacOutput(10.0))` was
accepted and recorded `ControlChange(elapsed_s=5.0, …, previous_value=5.0,
new_value=10.0)`. A failed run did the same
(scripts/a6_settings_after_halt.py).

**Decision needed, 2026-10-26 (session on `claude/generator-head-state-consistency-o6wts7`, under the head `PL-J5GC`).** This brief asks how a change made on a stopped run is recorded and shown. That is behaviour a learner sees, so the project owner decides. The question: when a learner moves a dial on a run that has stopped, failed or at the 24-hour supported run length, what happens?

- **Option 1, recommended: the dial springs back, and the banner says why.** The controller refuses the change on a stopped run and records nothing. The dial returns to the setting that the stopped values ran under. The stopped-run banner gains one sentence, such as "A stopped run cannot take a new setting. Reset starts a new run and keeps every setting." The learner presses Reset, then sets the dial. Every setting on screen beside the stopped values is one they ran under. Nothing new is held. The cost is one Reset before adjusting, and a control that refuses every change while it looks enabled. The banner sentence explains that refusal.
- **Option 2: the dial keeps the new value as the next run's setting.** The stopped run's control-change record is left as it was. A line beside the moved dial says something like "For the next run - the values shown ran at 5.0 L/min". Reset then starts at the new value. The cost is a new state, a setting held for a run that does not exist yet, and a conditional line on each dial. The controller must also remember the settings the run stopped under.

The recommendation is Option 1. It adds no hidden state, and it keeps `PL-V2HC`'s reason for keeping the controls live: nothing is drawn disabled. The brief's "The controls stay live" fits either option. Under Option 1 the sliders are enabled but refuse, which is why this is put to the owner rather than decided here. The test the brief names fits either answer. A dial dragged into a halt (`PL-85LJ`) is a different path and is not changed by either option: that setting was applied before the run stopped, and the undrawn-failure banner says the readouts are the last frame drawn.

**Decided, 2026-10-26 (session decision, after the project owner questioned why it was offered as a choice).** Option 1: a stopped run refuses a dial change, records nothing, and the dial springs back. The stopped-run banner says that Reset starts a new run and keeps every setting. Option 2 added a held setting and a line on each dial in order to buy one fewer Reset click, so it was never a close choice. The owner's question assumed that Reset returns the dials to their defaults. It does not: `SimulationController.reset` keeps the settings, which is why the banner sentence names that.

**The two stopped states get different ways out (project owner, 2026-10-26).** The owner's words: "24 hour wall and failed run should be treated as different scenarios. One is expected behavior (24 hour run) and you can rewind and branch. A failed run would be a bug and unexpected behavior". Also: "if 24 hours and you rewind time, it should reflect what the dial was set to at that point". Two parts of this already hold. The status words and banners differ (`STATUS_SUPPORTED_LIMIT_TEXT`, `STATUS_FAILED_TEXT`, `halt_disposition`). A branch opened at an earlier instant starts each dial at its value at that instant, because `SimulationController._branch_from` reads `_setting_at`. What this item changes is the refusal's wording. Each stopped run names its own way out when a dial is moved on it:

- At the supported run length, the run ended as expected. The banner sends the learner back: branch at an earlier instant to try a different setting, where the dials show what they were set to then, or Reset.
- On a failed run, which is a fault, the banner keeps Reset as the way out.

On either stopped run, the dials show the settings in force at its last completed step.

**Build plan, 2026-10-26, for the session after the reset.** Check one risk first. `test_a_refused_reset_takes_once_the_cardiac_output_is_set_again` (`PL-M4M0`) sets the cardiac output on a run that a refused Reset failed, and then expects Reset to take. A setter that refuses on every failed run changes that path. Read that test and `test_a_refused_reset_names_no_setting_and_sends_the_reader_to_restart` together, and decide whether the refusal applies to that failure too. Then:

1. In `app/controller.py`, the four setters refuse on a stopped run, failed or at the supported run length, before they apply anything. They raise `SimulationConfigurationError`, which `RunView._apply_setting` already treats as a refused setting, so the dial is rewritten from the run and springs back, and nothing is recorded.
2. `notice` ranks a stopped run above a refused setting, so the refusal text never shows on a stopped run. So when a stopped run's view holds a refused setting, `notice` adds the stopped run's own way out to its banner. At the supported run length: branch at an earlier instant to try a different setting, where each dial shows its setting then, or Reset, which keeps every setting. On a failure: Reset starts a new run and keeps every setting. Check `halt_notice` too.
3. Tests: `test_a_setting_changed_on_a_halted_run_is_not_shown_as_the_setting_its_values_ran_under` in `tests/integration/test_simulation_view.py`, at a shortened supported run length and on a failed run, as `PL-J5GC`'s two dial-moved scenarios set them up. Add a controller test in `tests/integration/test_controller.py` that a setter on a stopped run raises and records nothing. Run both against `c2f66e41` and record the failures here. Put `PL-J5GC`'s two dial-moved scenarios back into its guard from `861243aa`, where they fail against `main` on the cardiac output dial (10.0 L/min where the stopped values ran at 5.0). They must then pass. Extend `PL-J5GC`'s row in `docs/MODEL.md` § "Reasonably foreseeable misuse, and the hazards the presentation carries" with the refused setting.


**Built, 2026-10-27.** The four setters in `app/controller.py` call `_refuse_a_setting_on_a_stopped_run` first. On a failed run or one standing at the supported run length, it raises `SimulationConfigurationError`, which names the setting, before anything is applied or recorded. `set_agent` is not refused, because it starts a new case and is a way out. `RunView._apply_setting` already treats the error as a refused setting, so the next frame writes the dial back from the run. `dashboard_frame._stopped_run_exit` now chooses the closing sentences of all three stopped-run banners. With no refused setting it is Reset, or the refused-Reset exit. With one, the refusal is stated in place of the exit, followed by that run's way out: "Reset to start a new run, which keeps every setting." after a failure, and a branch at an earlier instant or Reset at the supported run length. The run-length wording therefore ends with `{exit}` like the failure wordings. `halt_notice` takes the refused setting too, so a dial moved on a run whose frame is refused is stated as well. The wording is a placeholder.

**The refused-Reset risk, decided.** A refused Reset always leaves the run failed (`RunView._reset_now` halts it), so the refusal applies there too. No dial is ever accepted on that run, and an agent switch, which starts a new case, is now the only setting that clears the refused-Reset exit. On that run the dial's refusal follows the refused-Reset exit and adds no Reset advice, because closing the application is the only way out left. `test_a_refused_reset_takes_once_the_cardiac_output_is_set_again` tested a path this change removes, so it became `test_a_refused_reset_takes_once_the_record_is_repaired_and_no_dial_lifts_its_exit`. `test_a_refused_reset_names_no_setting_and_sends_the_reader_to_restart`, which `PL-01GY`'s `verify:` names, keeps its name and now expects the refusal after the exit. A refusal made while the run was going is kept until a setting is accepted, as before, so it can appear on the stopped banner. The way out it is given there is still true, so no new state was added to clear it at the stop.

**A fork route this removes.** `test_a_branch_forked_where_a_dial_moved_on_the_supported_run_length_reads_as_stopped_there` branched at a keyframe that a dial made at 24:00:00 after the run stopped. That keyframe can no longer be made. The test became `test_no_dial_makes_a_keyframe_on_the_supported_run_length_to_branch_at`, and `resumed_here`'s docstring now names a mark on the limit as the one fork left there. `test_a_stopped_run_outranks_a_refused_setting_in_the_notice` asserted that a stopped banner never states a refused setting, which this change reverses. It now checks that the banner opens with the stopped run and states the refusal inside it, never as a refusal on a run that is still going.

**Run against the code before the fix (`99254fe3`), 2026-10-27.** The command was `PYTHONPATH=src pytest tests/integration/test_simulation_view.py tests/integration/test_controller.py tests/unit/test_dashboard_frame.py -k "halted_run_is_not_shown or stopped_run_refuses_every_setting or no_dial_makes_a_keyframe or refused_on_a_stopped_run or one_state"`, in a worktree of that commit with the new test files copied in. 14 failed and 4 passed. The four that passed are the guard's earlier scenarios.

- `test_a_setting_changed_on_a_halted_run_is_not_shown_as_the_setting_its_values_ran_under`, both cases: `{'dial 3': ('Cardiac output', '', 0, 100, 100, '10.0 L/min', ...)} != {'dial 3': ('Cardiac output', '', 0, 100, 50, '5.0 L/min', ...)}`.
- The guard's two restored scenarios: the same mismatch in the settings group.
- `test_a_stopped_run_refuses_every_setting_and_records_nothing`, all eight cases: `Failed: DID NOT RAISE SimulationConfigurationError`.
- `test_no_dial_makes_a_keyframe_on_the_supported_run_length_to_branch_at`: `DID NOT RAISE SimulationConfigurationError`.
- `test_a_setting_refused_on_a_stopped_run_is_stated_with_that_run_s_way_out`: `assert 'Simulation s...rt a new run.' == 'Simulation s...very setting.'`.

**Next, after the reset of 2026-10-27.** The close-out reviews for `#1846` are still owed, as `PL-J5GC`'s closing paragraph lists. Run them before marking `#1846` ready.

**Blind review, 2026-10-27.** Both blind passes on `#1846` named the same defect in the way out built here. At the supported run length, a refused dial's banner named a branch at an earlier instant whether or not one could be taken. While two runs are compared, `fork_offer` locks the branch control, so the banner sent the reader to a control the screen had replaced with its lock caption. A reader who refused a dial and then took a branch went on reading the instruction to branch. `notice`, `halt_notice` and `_stopped_run_exit` now take `branch_offered`, and `RunView._branch_offered` reads it from the comparison and from `SimulationController.fork_refusal`. While no branch can be taken, the run names Reset alone, with `RESET_SETTING_WAY_OUT_TEXT`, the text a failed run already gave. The default is False, so a caller that does not say names Reset, which is always offered. A branch on the chart is always compared with its trunk, so the comparison covers the branch's own refusal too.

The passes also named a branch forked on a mark at the limit, whose Reset returns it to the limit. That is `PL-VHQX`, which is open, and it is left there.

`test_a_setting_refused_at_the_supported_run_length_names_a_branch_only_while_one_can_be_taken` covers it. Against the code before the fix it failed at the second banner: `assert False` where the trunk's banner, after the branch was taken, still ended "...branch at an earlier instant, where each dial starts at what it was set to then, or Reset to start a new run, which keeps every setting." The unit test of the way out now checks both values of `branch_offered`.

The owner asked on 2026-10-27 why there are four dial setters. The answer found a gap in this item's own test: `test_a_stopped_run_refuses_every_setting_and_records_nothing` listed the four controls by hand, so a fifth control whose setter left out the refusal would have passed it. It now runs once for each `ControlInput`, so a fifth member fails it until it has a setter and a refusal.
