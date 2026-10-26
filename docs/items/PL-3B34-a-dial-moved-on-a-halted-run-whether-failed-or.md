---
id: PL-3B34
title: A dial moved on a halted run, whether failed or stopped at the 24-hour supported run length, is applied to the core and recorded as a control change at the halt instant, so the settings readouts and the control-change record show a setting that no step ever ran under beside concentrations computed under the previous one, while the banner says the values shown are the last completed step
priority: P1
effort: M
status: ready
classes: defect, ux, safety
feature: replay-findings
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/dashboard_frame.py, docs/MODEL.md, tests/integration/test_controller.py, tests/integration/test_simulation_view.py
added: 2026-10-25
payoff: the settings shown beside a halted run's concentrations are the ones those concentrations were computed under, so a learner cannot pair a value with a setting no step ran
verify: grep -q 'def test_a_setting_changed_on_a_halted_run_is_not_shown_as_the_setting_the_values_were_computed_under' tests/integration/test_simulation_view.py
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

**Done when.** A setting moved on a halted run, failed or stopped at the supported run length, is never shown beside the halted values as the setting they were computed under, and the control-change record does not claim it acted on the patient. The controls stay live. `tests/integration/test_simulation_view.py` has `test_a_setting_changed_on_a_halted_run_is_not_shown_as_the_setting_the_values_were_computed_under`, which halts a run at a shortened supported run length, moves the cardiac output dial, and checks the settings readout and the record.

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
