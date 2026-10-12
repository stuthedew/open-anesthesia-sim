---
id: PL-1ZQ4
title: A mark added after the step that crossed it is answered three ways: the trunk reads a late MAC target as not reached where a branch opened on that step reads it reached, a mark added to a branch after it opened is never asked of its opening step, and fork_at at a keyframe the trunk halted on opens on no crossing where fork_here opens on the halt's
status: untriaged
feature: scenario-branching
added: 2026-10-12
---

**Problem.** A mark added after the step that crossed it is answered three ways: the trunk reads a late MAC target as not reached where a branch opened on that step reads it reached, a mark added to a branch after it opened is never asked of its opening step, and fork_at at a keyframe the trunk halted on opens on no crossing where fork_here opens on the halt's

**Found by the adversarial review of `PL-Y2SL`** (2026-10-12), each case
reproduced with a scratch script under the offscreen platform.

**Three answers to one question.** The step ending where a branch opens is
asked once, at the fork, which marks it crossed (`_crossing_ending_at`, shared
by `resumed_here` and `resumed_at_mark`), against the marks as they stand then.
That is "the branch the halt would have given" had the marks been set in time
(`docs/MODEL.md` § "What this requires of a branch"), and
`test_a_height_crossed_on_the_step_that_reached_a_passed_mark_is_stood_on_too`
holds it. Three readers answer differently:

1. **The trunk reads a MAC target historically.** A target added after the
   step that crossed its height is not in `_reached_crossings`, so the trunk
   reads it `still_running` while a branch opened on that step reads it
   `reached` - at a plain pause at 118.1 s, alveolar 0.30008 xMAC, target
   0.3: trunk `still_running`, branch `reached`, and still so 300 s on with
   the two states element-wise equal at 418.1 s. Time marks agree, because the
   trunk places them by its clock.
2. **A mark added to a branch after it opened is never asked of the opening
   step.** The view adds a mark to every run, so marking before or after
   branching gives different branch standings: on a halt, a 118.05 s time mark
   reads `passed` marked first and `before_this_branch` marked after; a 0.3
   xMAC target `reached` and `still_running`. Before `PL-Y2SL` the halt door
   gave `before_this_branch` and `still_running` in both orders.
3. **`fork_at` at a keyframe the trunk is halted on opens on no crossing**
   (`resumed_at` passes `crossing=None`, `PL-3K9B` case E), so a setting
   changed while standing on a halt makes the selector's keyframe row and the
   "Branch here" button open two branches at one instant that read the halted
   marks differently: time mark `before_this_branch` against `passed`, MAC
   target `still_running` against `reached`. Pre-existing: the halt door did
   the same.

**Why it matters.** Two accounts of one mark at one instant, and an account
that depends on the order of two acts, are the stale-state misreading
`.claude/rules/expert-review.md` names. Each needs the mark inside the single
step ending at the fork - about 2e-4 xMAC of alveolar rise at two minutes - so
they are rare, but the "Branch here" button is offered at every pause.

**The decision the fix needs, with a recommendation.** What a mark added after
the fact *means* on the trunk is the real question, and it is learner-visible.
Recommended: one rule for every run and every order - a run reads a mark lying
inside the step it opened on (a branch) or stands on (a paused trunk) as
crossed by that step, asked of the marks as they stand whenever the standings
are read rather than once at the fork - so the trunk's MAC reading joins the
branch's and the order stops mattering. The alternative, keeping MAC targets
historical everywhere, would undo the counterfactual the mark door was built
on and the test above holds.
