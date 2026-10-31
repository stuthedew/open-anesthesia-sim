---
id: PL-QVBR
title: A MAC target that a stepped reading lands on exactly halts the trunk and reads reached there, while a branch opened on that step asks the canonical reading, which can lie about 1e-14 short, so the branch opens on no crossing and reads the target as still running
priority: P1
effort: M
status: ready
classes: defect, safety
feature: defect-review-2026-10
touches: src/anesthesia_sim/app/controller.py, tests/unit/test_bookmarks.py
added: 2026-10-26
payoff: a trunk and the branch opened on its halting step agree on whether the learner's MAC target was reached
verify: grep -q 'def test_a_branch_opened_on_a_halting_step_agrees_with_the_trunk' tests/unit/test_bookmarks.py
---

**Problem.** A MAC target that a stepped reading lands on exactly halts the trunk and reads reached there, while a branch opened on that step asks the canonical reading, which can lie about 1e-14 short, so the branch opens on no crossing and reads the target as still running

**Evidence.** Found by `PL-ZR49` on 2026-10-26, while deriving the halt record from the step. `tests/unit/test_bookmarks.py::test_a_run_that_settles_exactly_on_a_target_halts_once_and_then_advances` takes its height from a run's own stepped reading at 60 s, so the trunk lands on it exactly and halts. `SimulationController.advance` decides the halt from the stepped readings (`state_vector()` before and after the step). Every branch asks the same step through `_crossing_of_step`, from the canonical states (`RunDefinition.state_at`), which `docs/MODEL.md` § "The canonical evaluation rule" puts within about 4.9e-14 of the stepped ones. A halt record derived from the canonical step alone read `None` for that run. `PL-ZR49` therefore keeps what the stepped readings crossed on the halting step, by instant and height, beside the canonical crossing, which is what `bookmark_standings` already does with `_reached_crossings`. A branch has no stepped readings of its parent's step, so a branch opened on that step (`resumed_here`, `resumed_at_mark`, `resumed_at` at that instant) asks the canonical step only. It then opens on no crossing, and its standings read the target as not reached, while the trunk's read it as reached.

**Why it matters.** Two runs at one instant describe the same step in two ways, which is the disagreement `PL-ZR49` exists to remove, here from arithmetic rather than from a record. A learner types a height to two decimals, so a stepped reading equal to it to the last bit is a coincidence, and the canonical reading then has to fall on the other side. The likely cost is small, and the case is reachable.

**Done when.** One reading decides a crossing for both the halt and every branch, or `docs/MODEL.md` states the residual where it states the 4.9e-14 agreement. A test takes a height from a stepped reading, halts on it, branches there, and checks the trunk and the branch agree, or checks the stated residual.

**Seen again, 2026-10-26** (the lifecycle review of `PL-ZR49`'s change, from a random sequence of actions). The trunk is paused at 0.3 s, and a MAC target is added at the canonical alveolar reading there. The live reading is one unit in the last place lower. While the trunk stands at 0.3 s, the target reads reached. After Start, the trunk halts on the same target again at 0.4 s, from its stepped readings. A branch taken by "Branch here" at 0.4 s then has no halt record, while the trunk's offer says "stopped on your mark". The cause is the one above: the stepped and canonical readings lie on opposite sides of the height. This case adds a second symptom, a target that reads reached and then halts the run again one step later.

**Triage, 2026-10-31: the Done-when's second route is not taken.** Stating the
residual in `docs/MODEL.md` would leave a trunk and its branch disagreeing
about whether a learner's MAC target was reached. That is the disagreement
`PL-ZR49` exists to remove, so the first route is the clearly correct one:
one reading decides a crossing for the halt and for every branch.
`docs/MODEL.md` § "The canonical evaluation rule" already names the canonical
reading as the authority, so the work is to make the halt follow it, or to show
why it cannot.

**Generator check.** One-off. The fact is which of the two readings of one
step, stepped or canonical, decides a crossing. `PL-ZR49`'s change filed it on
the day that head closed, 2026-10-26, so it is that head's own finding and not
a re-entry. No head's `misread:` states this fact (`PL-R4Y2`'s triage,
2026-10-31).
