---
id: PL-WG73
title: COMPARING_FORK_LOCK_TEXT tells a learner to Reset the case, which labels no control - and the Reset they are likeliest to press discards the branch and leaves the lock standing
priority: P2
effort: S
status: ready
classes: defect, ux
feature: two-run-attribution
touches: src/anesthesia_sim/app/dashboard_frame.py, tests/unit/test_dashboard_frame.py, tests/integration/test_simulation_view.py
added: 2026-09-20
payoff: stops a learner losing their branch's simulated progress by following an instruction that names a control this interface does not have
verify: grep -q 'def test_the_comparison_lock_names_a_control_the_learner_can_press' tests/unit/test_dashboard_frame.py
---

**Problem.** COMPARING_FORK_LOCK_TEXT tells a learner to Reset the case, which labels no control - and the Reset they are likeliest to press discards the branch and leaves the lock standing

**Found 2026-09-20** by the adversarial review of `#784`, and upheld against
refutation. `PL-VKJW` is what made two runs reachable from a shipped entry
point for the first time, so this is that change's to answer rather than a
pre-existing gap.

**Why it matters.** Two failures in one sentence, and the second is the
expensive one.

`COMPARING_FORK_LOCK_TEXT` reads `"One comparison at a time. Reset the case to
end this one."`, and `RESET_LABEL` is `"Reset"` - the only Reset label in
`app/`. So the instruction names a control by a phrase no control carries, which
is the wayfinding failure `.claude/rules/expert-review.md` puts under "hidden
modes, surprising defaults" and error prevention over after-the-fact warning.

Worse, once a branch is drawn there are two Reset buttons and they do opposite
things. `test_resetting_the_trunk_ends_the_comparison` shows the trunk's Reset
is the one meant: it drops the branch, returns to one run and lifts the lock.
`test_resetting_a_branch_leaves_the_comparison_standing` shows the branch's -
the run the learner is trying to end, and so the one they reach for - returns it
to its fork, discarding everything simulated since, and leaves the lock exactly
where it was. The learner follows the instruction, loses their branch's
progress, and the control they were sent to press is still locked with the same
sentence under it.

**Not classed `safety`.** Nothing here displays a wrong or misattributed
clinical value; the cost is lost simulated work and a mode the learner cannot
get out of. That is human factors rather than the clinical-output floor, which
is why this sits at `P2` while its feature-mate `PL-LHBY` sits at `P1`.

**Verified 2026-09-20** against `src/anesthesia_sim/app/dashboard_frame.py`
lines holding `COMPARING_FORK_LOCK_TEXT` and `RESET_LABEL`, and against both
named tests in `tests/integration/test_simulation_view.py`.

**On the fix.** The text is the cheap half and probably not the whole answer:
naming the trunk's control ("Reset " + the trunk's run name, whatever the
learner sees on it) closes the mismatch, but a learner reading it beside the
branch still has to work out which button that is. Whether the branch's own
Reset should say what it will and will not do is the implementing session's
call. `tests/unit/test_dashboard_frame.py` already asserts `"Reset" in
COMPARING_FORK_LOCK_TEXT`, which is the assertion that let the mismatch through
and should be replaced rather than added to.

**Done when.** The comparison lock names a control the learner can actually
find, that control is the one that ends the comparison, and a test in
`tests/unit/test_dashboard_frame.py` holds the text to a label that exists
rather than to the bare word "Reset".
