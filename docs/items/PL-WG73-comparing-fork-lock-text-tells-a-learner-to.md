---
id: PL-WG73
title: COMPARING_FORK_LOCK_TEXT tells a learner to Reset the case, which labels no control - and the Reset they are likeliest to press discards the branch and leaves the lock standing
priority: P2
effort: S
status: done
classes: defect, ux
feature: two-run-attribution
milestone: v0.5.4
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/simulation_view.py, tests/unit/test_dashboard_frame.py, tests/integration/test_simulation_view.py, docs/ARCHITECTURE.md
added: 2026-09-20
closed: 2026-09-22
pr: 902
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

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2, because this milestone's own work created them", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood.

> **Recorded rather than silent**, which is what "The gate is a snapshot, not a moving target" requires of either disposition. The same adversarial review of `#784` found both of these entries, as it found `PL-25DD` above and `PL-LHBY` before it. Those two are admitted, and these two are deferred. The difference comes from the rule, not from a judgment about severity. Neither is classed `safety` or `science`, so neither gets the unconditional re-entry. They are then held to the presence test, and its result is no. `git log -S` dates both symbols to `d048aca` (2026-09-20), the pull request that built the fork control. That pull request was work done while implementing the milestone this gate protects, which is the case the rule names explicitly.

> - PL-WG73 (S) — **deferred 2026-09-21.** `COMPARING_FORK_LOCK_TEXT` sends the learner to "Reset the case" where the only Reset label in `app/` is `"Reset"`, and once a branch is drawn the two Reset buttons do opposite things: the trunk's ends the comparison, the branch's — the one the learner reaches for — discards everything simulated since the fork and leaves the lock standing. `defect`, `ux`. It costs the learner their branch's progress and a mode they cannot see the way out of; it displays no wrong clinical value, which is why it sits at `P2` and outside this gate.
