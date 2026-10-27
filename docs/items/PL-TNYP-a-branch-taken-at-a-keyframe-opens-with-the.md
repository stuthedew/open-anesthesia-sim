---
id: PL-TNYP
title: A branch taken at a keyframe opens with the trunk's change at that instant already applied, but the offer is labelled only "1m", the branch's record says no setting changed, and a later edit to the trunk at the same instant erases the trunk's only record of the change the branch runs under
priority: P2
effort: M
status: done
classes: defect, ux
feature: replay-findings
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/run_view.py, tests/unit/test_dashboard_frame.py, tests/integration/test_controller.py, docs/MODEL.md
added: 2026-10-25
closed: 2026-10-26
pr: 1844
payoff: when two runs part at a fork, some record on screen always says which setting change separates them
verify: grep -q 'def test_a_branch_taken_at_a_keyframe_keeps_a_record_of_the_setting_it_opened_under' tests/integration/test_controller.py
---

**Problem.** `fork_offer` labels a keyframe with `format_elapsed` alone, for example "1m" (`app/dashboard_frame.py`). `resumed_at` at that keyframe opens the branch after the trunk's change at that instant. The branch's own control timeline starts empty, so its record reads "No settings changed yet in this run." The trunk's settings stay live after the fork. If the learner then sets the trunk's dial back, or to a third value, at the same paused instant, `_record_control_change` rewrites or deletes that change and the keyframe. Then no record on screen states the setting the branch runs under.

**Why it matters.** The two curves part at the fork. The trunk's record shows either nothing at that instant or a different change, and the branch's record shows nothing. Only the branch's dial says why the runs differ. A learner can credit the difference to the wrong intervention. `PL-HSP8` will fix the here door and the mark door. It leaves the keyframe door as it is by decision, so this case stays open. The fix could state on the offer which side of the change the branch opens on, or record the setting the branch opened under in its own record.

**Done when.** A branch taken at a keyframe states, on screen and after any later trunk edit at that instant, the setting it opened under: on the offer, in its own record, or both. `tests/integration/test_controller.py` has `test_a_branch_taken_at_a_keyframe_keeps_a_record_of_the_setting_it_opened_under`, which reproduces the 60 s case and then sets the trunk back.

**Found by.** `PL-TBQS` reviewer replay on #784, findings r02 F1 and r04 F2, checked against main on 2026-10-25. Reproduced with `e_c_fork_same_instant.py` and `e_e_keyframe_side.py`. The trunk was paused at 60 s and set to 6 L/min, and the branch opened at 6 L/min with an empty timeline. The trunk was then set back to 4 L/min at 60 s, which left `fork_points_s` at `(0.0,)` and the trunk's timeline empty.

**Closed 2026-10-26 by `PL-ZR49`.** Every branch now takes its provenance from the stretch the step reaching its fork ran under, records how its settings differ from that stretch as a change at the fork, and reads its halt record from the step and the current marks. `tests/integration/test_controller.py::test_a_branch_taken_at_a_keyframe_keeps_a_record_of_the_setting_it_opened_under` checks this item's case, and `test_every_door_at_a_paused_instant_agrees_after_an_edit_made_there` checks it beside the other doors.
