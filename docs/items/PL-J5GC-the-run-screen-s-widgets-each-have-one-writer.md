---
id: PL-J5GC
title: The run screen's widgets each have one writer since PL-X7D5 and PL-WM5P, but nothing requires values shown together to come from one state, so a label, divisor or verdict can come from a different state than the value beside it: three members filed after PL-WM5P closed
priority: P1
effort: M
status: ready
classes: defect, safety
feature: defect-review-2026-10
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/controller.py, tests/integration/test_simulation_view.py
deferred-from: v0.7.0 - recorded as a generator head by PL-R4Y2's defect review on 2026-10-25; each member's safety finding was filed and placed by its own triage, and this head's work is the structure that stops the next one
added: 2026-10-25
payoff: a value and its divisor, setting or verdict are never shown from two different states
verify: grep -q 'def test_every_value_and_its_qualifiers_on_screen_come_from_one_state' tests/integration/test_simulation_view.py
root-cause-of: PL-6RJ0, PL-3B34, PL-HF4B
generator: live - three members were filed against main after PL-WM5P's fix merged, and its guard compares each widget with itself rather than a group with each other
misread: Which widgets state a run's current state, and that each is restated on every path that changes it
---

**Problem.** The run screen's widgets each have one writer since PL-X7D5 and PL-WM5P, but nothing requires values shown together to come from one state, so a label, divisor or verdict can come from a different state than the value beside it: three members filed after PL-WM5P closed

**Evidence.** Found on 2026-10-25 by asking the generator question of the product defects filed since 2026-10-23. `PL-WM5P` merged at 05:44 UTC on 2026-10-25 (`#1779`), giving every run-state surface one writer. The three members below were filed at 21:59 UTC the same day, each checked against `main` after that merge:

- `PL-6RJ0`: `RunView._write_settings` writes the "1 MAC sevoflurane = 2.0%" line from the current settings, on the halt path too. The readout cards whose ×MAC values it divides are written only in `refresh`, from the last drawn frame. After a halt that follows an agent change, the line names the new agent above the old agent's multiples.
- `PL-3B34`: a dial moved on a halted run is applied and recorded at the halt instant, so the settings readout shows a setting that no step ran under, beside concentrations computed under the previous one.
- `PL-HF4B`: a failed step is rolled back, so the accounting panel reads the restored "Valid" state under a banner that quotes the failed step's totals.

**The mechanism.** `PL-X7D5` and `PL-WM5P` made the rule "each widget has one writer", and their guard checks that a halted screen reads like a drawn one. Both hold here. What fails is a different rule: values shown together must come from one state. A label, a divisor or a verdict written from the current settings, the restored state or the failed step sits beside a value written from the last drawn frame. The guard compares each widget with itself across two screens, so it cannot see two widgets on one screen that disagree.

**Why it matters.** The 1 MAC line is the divisor of every ×MAC number in its row, and the settings readout is the context a learner reads a concentration under. A correct number under the wrong divisor or setting is the presentation failure `CLAUDE.md`'s safety-critical standard names.

**Done when.** Each group of widgets that qualifies one value is written from one state in one call: the readout cards with their 1 MAC line, the settings with the concentrations they produced, and the accounting verdict with the totals it judges. `tests/integration/test_simulation_view.py` has `test_every_value_and_its_qualifiers_on_screen_come_from_one_state`, a guard that fails on a group whose members come from two states. `PL-6RJ0`, `PL-3B34` and `PL-HF4B` close under it, or each says why it stays.

**Generator check.** This item is the head, as three post-close instances of `PL-X7D5`'s fact. Each member records `reenters: PL-X7D5`.

**Checked 2026-10-26, against `main` at `7391cf2f`.** The brief is still true. The session working it (branch `claude/generator-head-state-consistency-o6wts7`, draft `#1846`) claimed this head with `PL-3B34` and `PL-HF4B`, and stopped at its context budget before writing code. What it found:

- **The existing guard enforces the `PL-6RJ0` defect.** `test_every_run_state_widget_reads_alike_on_a_drawn_run_and_a_halted_one` requires every `RunView` widget that `FRAME_WIDGETS` does not name to read alike on a halted screen and on a drawn one. `_one_mac_text` and `_compartment_substance_text` are not named, so that test pins both to the run's record. A qualifier of a frame widget is itself a frame widget. So both join `FRAME_WIDGETS` with that reason, and the new guard checks them against the cards instead.
- **The readout group is three widgets, not two.** `_compartment_substance_text` ("Modelled concentrations: {agent}") names the substance of the same cards, on the same line as the 1 MAC line. After a halt that follows an agent change it names the new agent, and `test_a_halt_after_an_agent_change_names_one_agent` (`PL-1YDD`) asserts that. Moving only the 1 MAC line into `refresh` would put "Modelled concentrations: Desflurane" and "1 MAC sevoflurane = 2.0%" on one line. The heading and the 1 MAC line are written in the same call as `_readout_row.set_readouts`, from the same snapshot, and that `PL-1YDD` assertion changes. The subtitle, chip, selector and dial keep naming the run's agent. The undrawn-failure banner already says that the readouts are the last frame drawn.
- **"One state" cannot mean "one snapshot object".** After an accounting rollback, one snapshot carries the restored step's accounting beside the rejected step's failure reason. After a dial is moved on a halted run, one snapshot carries a setting that no step ran under beside the last step's values. A guard that compared the object each widget was written from would pass both defects. So the guard names, for each group in each scenario, the step that every member must describe, and works that step out from the scenario itself, as `.claude/rules/test-oracles.md` rule 2 asks. Each member's expected text is then built from that step with the same `dashboard_frame` function the view calls. That function is not what is under test. The choice of step is.
- **The guard's shape.** A table of groups. Each group lists its members as widget attribute paths, as `FRAME_WIDGETS` does, and gives a function from a step to each member's expected text. The scenarios are a drawn frame, a halt after an agent change, a raise from `setting_readouts` after `refresh` wrote the cards (both `PL-6RJ0`), a dial moved on a halted run (`PL-3B34`), and an accounting halt (`PL-HF4B`). The table is checked in both directions, as `FRAME_WIDGETS` is. Every widget that states a value or qualifies one is in a group or is named with the reason it qualifies nothing. So a widget added later fails until somebody classifies it.
- **Coordination.** `PL-6RJ0` is held by the Projects thread on `claude/project-thread-6rhott` (`#1840`), unstarted at 00:10 UTC. `send_message` to that thread and to its coordinator returned "not found" for both session ids, so the note above went to `#1840` as a comment. The guard's readout group fails on `main` until `PL-6RJ0` lands. So `#1840` merges first, or this branch merges its commit in.
- **`PL-3B34` is decided.** A stopped run refuses a dial change, records nothing, and the banner says Reset keeps every setting. Its brief records the decision. So in the guard's stopped-run scenario, the settings group must show the settings the stopped values ran under.

**Next, for the session that resumes this branch.** Place this head on v0.7.0's frozen list in `ROADMAP.md` with its date and reason, which `tools/doc_check.py check` asks for because the item is classed safety. Then write the guard and its group table first, and run it against `main` to record which groups fail there (`.claude/rules/test-oracles.md` rule 6). Then build `PL-HF4B` as its brief's design says. Then merge `PL-6RJ0` in once it is pushed, and build `PL-3B34` as its brief decides. Read `tests/integration/test_simulation_view.py` § `FRAME_WIDGETS` and `RunView.refresh`, `_write_statement` and `_write_settings` before the first edit.
