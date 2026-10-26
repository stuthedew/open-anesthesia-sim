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
