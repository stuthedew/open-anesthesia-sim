---
id: PL-2N43
title: resumed_at_halt seeds its branch from the halt's recorded crossing, so a time bookmark added inside the halting step while the trunk stands on the halt reads BEFORE_THIS_BRANCH on that branch, where resumed_at_mark reads the same mark PASSED (reproduced 2026-10-12: a 45.35 s mark halts at 45.4 s, a 45.33 s mark added while standing)
priority: P2
effort: S
status: done
classes: defect
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, tests/integration/test_controller.py
deferred-from: v0.6.0 - it closes with PL-Y2SL, a feature outside the gate whose door replaces resumed_at_halt, so it takes no gate work of its own
added: 2026-10-12
closed: 2026-10-12
pr: 1453
payoff: a branch taken where the trunk halted reads every mark the step crossed as passed, as the trunk does, so the two runs never give two accounts of one mark
verify: grep -q 'def test_a_mark_added_inside_the_halting_step_reads_passed_on_the_branch' tests/integration/test_controller.py
---

**Problem.** resumed_at_halt seeds its branch from the halt's recorded crossing, so a time bookmark added inside the halting step while the trunk stands on the halt reads BEFORE_THIS_BRANCH on that branch, where resumed_at_mark reads the same mark PASSED (reproduced 2026-10-12: a 45.35 s mark halts at 45.4 s, a 45.33 s mark added while standing)

**Why it matters.** The branch's bookmark rows would say the mark lies before
the branch began while the trunk, and a branch taken at the same mark through
`resumed_at_mark`, read it as passed: two accounts of one mark at one instant,
which is the stale-state misreading `.claude/rules/expert-review.md` names.

**Done when.** A time bookmark added inside the halting step while the trunk
stands on the halt reads PASSED on the branch taken there, as `resumed_at_mark`
reads it. `PL-Y2SL` closes it: its door reconstructs the crossing for the step
ending at the fork and replaces `resumed_at_halt`.
