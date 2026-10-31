---
id: PL-NRR6
title: A branch can be taken at the keyframe where the paused trunk stands, but the trunk can still replace or delete that keyframe with another setting change at the same instant, after which the branch's `opened_from` names a stretch the trunk never ran and `trunk.resumed_at` refuses the instant the branch opened at
priority: P2
effort: S
status: done
classes: defect
feature: replay-findings
milestone: v0.6.9
touches: src/anesthesia_sim/app/controller.py, tests/integration/test_controller.py
added: 2026-10-25
closed: 2026-10-26
pr: 1844
payoff: a branch's provenance always names a stretch its parent actually ran, as the safety standard requires of every displayed value
verify: grep -q 'def test_a_trunk_change_at_a_forked_instant_keeps_the_branch_provenance_in_the_trunk' tests/integration/test_controller.py
recurrences: 2026-10-25 PL-TNYP withdrawn 2026-10-27 PL-8MRM
---

**Problem.** `_resume_point_at` (`controller.py`) accepts any keyframe, including the one at the trunk's current instant, which no step has closed yet. `RunDefinition.record_change` may still replace or collapse that stretch. Reproduced: trunk paused at 30.0 s, delivered set to 4%, branch taken at 30.0 s, trunk set back to 2%. The trunk's segments become `[(0.0, 2%)]`, and `branch.opened_from.segment in trunk.run_segments` is False. `trunk.resumed_at(30.0)` is then refused, and the message lists only `[0.0]`.

**Why it matters.** The branch runs at 4% from 30 s and claims that setting from a trunk stretch that no longer exists. Its provenance, which `CLAUDE.md` requires for every displayed value, now points at nothing in the parent. The fork panel stops offering an instant at which a branch already exists. A fix refuses a fork at the parent's open instant, or makes a trunk change at a forked instant open a new stretch instead of replacing the old one.

**Done when.** After a branch is taken at the paused trunk's own instant, a trunk change at that instant leaves `branch.opened_from.segment` in the trunk's run segments and `trunk.resumed_at` still accepts the fork instant, or the fork at the trunk's open instant is refused. `tests/integration/test_controller.py` has `test_a_trunk_change_at_a_forked_instant_keeps_the_branch_provenance_in_the_trunk`.

**Found by.** `PL-TBQS` reviewer replay on #568, finding r01 F2. Checked against main 2026-10-25, reproduced with `scripts/B_branch.py`.

**Closed 2026-10-26 by `PL-ZR49`, with one clause changed.** `tests/integration/test_controller.py::test_a_trunk_change_at_a_forked_instant_keeps_the_branch_provenance_in_the_trunk` checks that `branch.opened_from.segment` stays in the trunk's segments after the trunk sets the dial back, because the provenance is now the stretch the step reaching the fork ran under. The second clause, that `trunk.resumed_at` still accepts the fork instant, no longer applies: setting the dial back removes the trunk's keyframe there, because the trunk no longer changed anything at that instant. The instant stays offered by `here_fork_point` while the trunk stands there, and a branch taken there names a provenance equal to the first branch's, which the test checks.
