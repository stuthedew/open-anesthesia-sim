---
id: PL-K5BS
title: Resetting a branch after the learner changed a setting keeps the new setting, clears the branch's control timeline and writes the setting over the fork's opening stretch, so the branch runs under settings that neither its control record nor its `opened_from` provenance states, and the `_open_at` docstring's claim that the definition "always opens at the parent's stretch, under the parent's settings" is false at a control-event fork
priority: P2
effort: M
status: done
classes: defect
feature: replay-findings
milestone: v0.6.9
touches: src/anesthesia_sim/app/controller.py, docs/MODEL.md, tests/integration/test_controller.py
added: 2026-10-25
closed: 2026-10-26
pr: 1844
payoff: a reset branch can be rebuilt from its provenance and its record, and the screen says why its trace leaves the trunk's
verify: grep -q 'def test_a_branch_reset_after_a_setting_change_keeps_its_record_and_provenance_in_agreement' tests/integration/test_controller.py
---

**Problem.** `reset()` on a branch calls `_open_at` in `controller.py`. `_open_at` records the current settings at the fork and then clears the control timeline. At a control-event fork, the fork is the stretch's own opening, so the change replaces the parent's settings rather than following them. Reproduced: fork at 30 s with fresh gas flow 6 L/min, set 8, reset. The result is `control_timeline ()`, `run_segments [(30.0, 8.0)]`, `opened_from.segment` fresh gas flow 6.0, and `has_recorded_run False`.

**Why it matters.** The branch's trace leaves the trunk's at the fork, and nothing on the branch records why. Its control record is empty and it shows no mark of its own. Its provenance names 6 L/min, but it runs at 8. Anything that rebuilds a branch from `opened_from` plus its timeline, such as save, replay or an overlay, would rebuild a different run. `docs/MODEL.md` § "Reset behavior" says to preserve settings and clear the timeline, but it does not say what a branch's reset owes its parent. A fix records the difference from the fork's settings as a control change at the fork, or restores the fork's settings on a branch reset. Either one also needs `docs/MODEL.md` to say which.

**Done when.** A branch reset at a control-event fork runs under settings that its control record and `opened_from` agree on: either the difference from the fork's settings is recorded as a control change at the fork, or the reset restores the fork's settings. `docs/MODEL.md` § "Reset behavior" says which. `tests/integration/test_controller.py` has `test_a_branch_reset_after_a_setting_change_keeps_its_record_and_provenance_in_agreement`.

**Found by.** `PL-TBQS` reviewer replay on #568: r02 F1, r03 F1, r04 F1, r05 F2 and r06 F1. Checked against main 2026-10-25, reproduced with `scripts/B_branch.py`. `PL-B8MK` changed where the change is recorded, but at a control-event fork the fault remains.

**Closed 2026-10-26 by `PL-ZR49`.** Every branch now takes its provenance from the stretch the step reaching its fork ran under, records how its settings differ from that stretch as a change at the fork, and reads its halt record from the step and the current marks. `tests/integration/test_controller.py::test_a_branch_reset_after_a_setting_change_keeps_its_record_and_provenance_in_agreement` checks this item's case, and `test_every_door_at_a_paused_instant_agrees_after_an_edit_made_there` checks it beside the other doors.
