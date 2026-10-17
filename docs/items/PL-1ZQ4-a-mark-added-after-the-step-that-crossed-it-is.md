---
id: PL-1ZQ4
title: A mark added after the step that crossed it is answered three ways: the trunk reads a late MAC target as not reached where a branch opened on that step reads it reached, a mark added to a branch after it opened is never asked of its opening step, and fork_at at a keyframe the trunk halted on opens on no crossing where fork_here opens on the halt's
priority: P1
effort: M
status: needs-decision
classes: safety, defect
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/bookmarks.py, docs/MODEL.md, tests/integration/test_controller.py
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

**Reproduced again 2026-10-17 at triage**, on this tree (`b9b3c812`), with a
scratch script over `SimulationController` and `BranchedCase` (no Qt needed),
a 0.3 xMAC alveolar target and, for cases 2 and 3, a trunk halted by a
118.05 s time mark at 118.1 s and a late time mark at 118.03 s:

1. Plain pause at 118.1 s, target added afterwards: trunk `still_running`,
   `fork_here` branch `reached`.
2. Marks added before `fork_here`: time `passed`, target `reached`; added to
   both runs after it: time `before_this_branch`, target `still_running`.
3. After a setting change while standing on the halt (so 118.1 s is a
   keyframe) and the late marks added: `fork_at(118.1)` gives time
   `before_this_branch`, target `still_running`; `fork_here` gives `passed`,
   `reached`.

**Where `docs/MODEL.md` states what each answer would change**, checked
2026-10-17. The sentence "It is the branch the halt would have given" is in §
"The canonical evaluation rule", under the paragraph "Returning to a marked
instant the run has already passed is that fork taken late", which follows
"What this requires of a branch" in the same subsection rather than sitting
inside it. The definition every answer has to restate is in § "Halting on a
marked crossing": "**Reached** - a MAC target the run has halted on at least
once. Historical, ... A branch is the one exception and not a carry-over: it
opens *standing on* the crossing it was forked at." The recommended answer
rewrites that definition (a paused trunk would read "reached" for a height it
never halted on); the alternative rewrites the canonical-evaluation bullet and
`test_a_height_crossed_on_the_step_that_reached_a_passed_mark_is_stood_on_too`.
Either way `docs/MODEL.md` is in `touches`, which makes the item non-delegable.

**Near neighbour:** `PL-2N43` (closed) fixed the same "asked once, at the fork"
mechanism for a mark added inside the halting step *before* the fork, by
re-asking `_crossing_ending_at` against the marks as they stand; case 2 here is
that question asked after the fork instead, which nothing re-asks.

**Decision needed.** What a mark added after the step that crossed it reads on
the run standing on that step, which is learner-visible and which
`docs/MODEL.md` currently answers two ways (historical on the trunk, standing on
a branch). Two defensible answers: (a) one positional rule for every run and
every order - a run reads a mark lying inside the step it opened on (a branch)
or stands on (a paused trunk) as crossed by that step, asked of the marks as
they stand whenever the standings are read; or (b) MAC targets historical
everywhere, so a branch no longer opens standing on a crossing nobody halted
on. Case 3 resolves the same way under either: the trunk did halt there, so
`fork_at` at that keyframe opening on no crossing disagrees with both.

**Recommended.** (a), as the brief above argues: it is the reading `PL-3K9B`
already chose for time bookmarks - a word re-read from where the run stands
every time the row is drawn, rather than a record that has to be withdrawn -
extended to heights, and it keeps the counterfactual the mark door was built
on. (b) would undo that door's "the branch the halt would have given" guarantee
and the test that holds it.

**Done when** (written for the recommended answer; rewritten if the owner
chooses otherwise). `SimulationController`'s standings read a mark inside the
step a run opened on or stands on as crossed, asked of the marks as they stand
at the read, on the trunk and on every branch, and `fork_at` at a keyframe the
trunk is halted on opens on the same crossing `fork_here` does; all three cases
above then give one answer per mark whichever run is asked and whichever order
the mark and the branch came in. `docs/MODEL.md` § "Halting on a marked
crossing"'s "Reached" definition and § "The canonical evaluation rule"'s
bullet say so. A regression test in `tests/integration/test_controller.py`,
`test_a_mark_added_after_the_step_that_crossed_it_reads_alike_on_every_run`,
covers the three cases.
