---
id: PL-HSP8
title: Returning to a mark opens the branch with a setting the trunk changed at that instant already in force, so the 'on your mark' branch repeats the trunk's own decision, though docs/MODEL.md calls it the branch the halt would have given
priority: P1
effort: M
status: done
classes: defect, science
feature: replay-findings
touches: src/anesthesia_sim/app/controller.py, tests/integration/test_controller.py, docs/MODEL.md
added: 2026-10-24
closed: 2026-10-26
pr: 1844
payoff: a learner who returns to a decision point gets the state before their decision, so trying the alternative shows a real difference
verify: grep -q 'def test_a_change_made_on_the_halt_stays_the_trunks' tests/integration/test_controller.py
---

**Problem.** Returning to a mark opens the branch with a setting the trunk changed at that instant already in force, so the 'on your mark' branch repeats the trunk's own decision, though docs/MODEL.md calls it the branch the halt would have given

**Evidence.** All three panel reviewers and the generalist control in `PL-TCBJ`'s replay raised this independently on `#1451`, and a blind checker reproduced it at that merge commit. The sequence: a mark at 60 s halts the trunk at 2%, the learner turns the vaporizer to 0% while the trunk stands on the halt, and the trunk runs on. "1m, on your mark" then opens at 0%, while the halt branch taken before the change opened at 2%. On `origin/main` on 2026-10-24, `SimulationController._setting_at` in `app/controller.py` still takes a change at `elapsed_s <= instant_s` as in force, and `RunDefinition.segment_at` still picks the segment opening at the instant by `bisect_right`. So the fault looks present; it was not re-run on `main`.

**Why it matters.** A learner who returns to a decision point to try the alternative gets the trunk's own decision again, and the two traces coincide. `docs/MODEL.md` § the mark branch says "It is the branch the halt would have given" and that the two branches' provenance compares equal. A learner may conclude the decision made no difference.

**Done when.** The halt branch and `resumed_at_mark` open under the setting the reaching step was computed under, whether they are taken before or after a change made while standing on the halt; their provenance compares equal; `resumed_at` at the change's keyframe still opens after the change; and `docs/MODEL.md` states the case. `tests/integration/test_controller.py` has `test_a_change_made_on_the_halt_stays_the_trunks`, which changes the vaporizer while the trunk stands on the mark and checks all three doors.

**Reproduced 2026-10-24 on `main` at `91a98348`, and wider than reported.** The trunk ran at 2%. A mark at 60 s halted it at 60.0 s, and `resumed_here()` took the halt branch. The vaporizer was then set to 0% (recorded as `DELIVERED` at 60.0 s, from 2.0 to 0.0), and the trunk ran on to 120 s. The halt branch opened at 2.0%, in the segment opening at 0.0 s. `resumed_at_mark(mark)` opened at 0.0%, in the segment opening at 60.0 s. Both have `began_at_s` 60.0 and equal fork states, but their `opened_from` provenance does not compare equal. Two more doors also gave 0.0%: `resumed_here()` taken after the change while still standing on the halt, and `resumed_at(60.0)`. So the halt branch itself gives a different answer depending on whether it is taken before or after the change. In `docs/MODEL.md` § "The canonical evaluation rule", the bullet "It is the branch the halt would have given" says the mark branch is the halt's and that their whole provenance compares equal, and a later bullet says the trunk's later changes stay the trunk's. The code contradicts that stated intent.

**Route decided 2026-10-24 at triage: fix the halt and mark doors, and leave the keyframe door.** `resumed_at` at a keyframe deliberately opens inside the stretch that a control change starts, so `resumed_at(60.0)` giving 0% is that door's documented answer. The halt and the mark doors are defined differently, as the state the reaching step was computed under, before any change made while standing on the halt. So the narrow fix is in `_resume_point_at_mark` and `resumed_here`, which should open under the settings in force for the step that reached the instant. Changing `<=` to `<` in `_setting_at` and moving `segment_at` to `bisect_left` would also change the keyframe door, and is not the route. `docs/MODEL.md` gains one sentence saying that a change made while standing on a halt is the trunk's, and that the keyframe door opens after it.

**Checked 2026-10-25 (`PL-F2NX`, Gate 3's staleness sweep): still reproduces.** On `cc31bef7`, with the trunk at 2% and a mark at 60 s, the halt branch taken before a change to 0% opens at 2.0%. The halt branch taken after the change, while the trunk still stands on the halt, opens at 0.0%. So does `resumed_at_mark` once the trunk has run on to 120 s. The halt branch's `opened_from` still does not compare equal to the mark branch's, and `_setting_at` still takes a change at `elapsed_s <= instant_s` as in force.

**Closed 2026-10-26 by `PL-ZR49`.** Every branch now takes its provenance from the stretch the step reaching its fork ran under, records how its settings differ from that stretch as a change at the fork, and reads its halt record from the step and the current marks. `tests/integration/test_controller.py::test_a_change_made_on_the_halt_stays_the_trunks` checks this item's case, and `test_every_door_at_a_paused_instant_agrees_after_an_edit_made_there` checks it beside the other doors.
