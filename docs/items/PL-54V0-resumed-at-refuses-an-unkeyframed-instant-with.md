---
id: PL-54V0
title: resumed_at refuses an unkeyframed instant with a reason resumed_at_halt disproves
priority: P2
effort: S
status: ready
classes: docs
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, tests/integration/test_controller.py
added: 2026-09-21
payoff: a reader meeting the fork refusal learns which door takes which instant, instead of an arithmetic limit the code beside it disproves - which would steer them into recording a keyframe at the fork and so changing the parent run
verify: ! grep -qF 'two propagations where the run took one' src/anesthesia_sim/app/controller.py
---

**Problem.** `SimulationController._resume_point_at` refuses a fork at an
instant the run holds no keyframe for, and the message gives the reason as
"opening there would restart from two propagations where the run took one and
would not reproduce it element-wise". Since `PL-B8MK`, `resumed_at_halt` forks
at exactly such an instant and *does* reproduce the parent element-wise, by
opening the definition at the keyframe at or before it. So the refusal's stated
reason names a construction the program no longer has to use.

**Why it matters.** The refusal itself is still right - a fork is taken where a
run stands, and `resumed_at` is the control-event door - but the reason is what
a reader learns the constraint from. An error message on a safety-critical path
that teaches a constraint the code beside it disproves is the presentation half
of the safety standard: the right refusal with the wrong explanation. It also
invites the wrong fix, since a reader who believes the stated reason will try to
record a keyframe at the fork, which is the route `PL-B8MK` measured and refused
because marking a run would change it.

**What the message should say instead** is why `resumed_at` is the wrong door
rather than why the arithmetic cannot be done: the run is not standing at that
instant, so there is no live state to seed a branch from and no step count to
continue, and a fork at a mark is reached through `resumed_at_halt`.

**Found by `PL-Z3W6`**, which asserted the arithmetic both ways in
`tests/reference/test_canonical_evaluation.py` and so had both routes in front
of it. Not fixed there: `src/anesthesia_sim/app/controller.py` is outside that
item's `touches`, and a changed error string wants the test that pins it changed
in the same commit, which is the close-out shape `PL-K4R5` describes.

**Where.** `src/anesthesia_sim/app/controller.py` (`_resume_point_at`), and
`tests/integration/test_controller.py`, which pins the current string.
**Classed `docs` rather than `safety`, and the call is worth stating because it
decides a gate disposition** (project owner, 2026-09-21, ratified, over classing
it `safety` and owing v0.5.0's gate a disposition for it). Filed `safety` first, which
made v0.5.0's gate owe it one - a `safety`-classed item re-enters the current
gate regardless of when it was captured. Read against the standard, `safety` is
the wrong class: nothing here can produce a wrong or misleading *clinical
value*. The refusal is correct and stays correct; only the sentence explaining
it is stale, and no number a learner could act on passes through it. That makes
it a wrong statement in a place a reader learns from, which is `docs`. Overrule
this if a refusal a learner can see counts as a warning the safety standard
reaches - it then needs a `### Declined to Gate` entry or a place in v0.5.0's
Required scope, and neither is a session's to write into a frozen list.

**Reproduced 2026-09-23, and the replacement above is itself wrong.** The
stale reason stands in three places in `src/anesthesia_sim/app/controller.py`:
the refusal in `_resume_point_at`, the `resumed_at` docstring's "It opens at a
keyframe or not at all" paragraph ("So an instant between two keyframes is
refused rather than approximated"), and `BranchedCase.fork_points_s`'s
docstring ("a fork taken anywhere else would restart from two propagations
where the run took one"). `test_an_instant_between_keyframes_is_refused_rather_than_approximated`
in `tests/integration/test_controller.py` carries it in its name and docstring.
But the wording proposed under **What the message should say instead** teaches
a second false constraint. `_resume_point_at_halt` seeds the fork from
`RunDefinition.state_at`, one propagation from the segment's opening keyframe,
never from the live state, and `state_at` answers any instant the run has
reached. `resumed_at` also opens at *past* keyframes, where the run is not
standing either. So neither "no live state to seed a branch from" nor "no step
count to continue" is why an unkeyframed instant is refused, since
`_resume_point` derives the step count from the instant. The true reason is the
door's scope. `resumed_at` opens at a recorded control event, `resumed_at_halt`
at a bookmark crossing the run stands on, and v0.5.0's definition of done asks
for exactly those two. An instant that is neither is not offered, and nothing
arithmetic makes it so.

**Done when.** The refusal says what it refuses: `resumed_at` opens at a
recorded control event, this run recorded none at that instant, here are the
ones it holds, and a fork at a mark is taken with `resumed_at_halt`. The
`resumed_at` and `fork_points_s` docstrings give the same reason, and the test
pins the new message under a name and docstring that no longer claim an
approximation. Whether `resumed_at` should *accept* any whole-step instant it
could now reproduce is a scope question for the branching milestone, not this
item.
