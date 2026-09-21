---
id: PL-Z3W6
title: Assert a branch reproduces its parent element-wise at every sampled point up to the branch point
priority: P1
effort: M
status: ready
classes: safety, science, test, anticipated
feature: scenario-branching
touches: tests/reference, tests/integration, docs/MODEL.md
added: 2026-09-06
payoff: puts the element-wise branch guarantee where this project checks arithmetic claims - against the reference solution rather than only through the app
verify: grep -q 'def test_a_fork_opening_between_two_keyframes_reproduces_its_parent' tests/reference/test_canonical_evaluation.py
---

**Problem.** A branch taken at time t must reproduce its parent's state exactly
at every recorded sample up to t - asserted element-wise, not within a
tolerance. Nothing asserts this today because nothing branches.

**Why it matters.** The entire purpose of forking is to attribute a difference
between two curves to the one setting that was changed. Two curves that diverge
*before* the branch point, by an amount nobody declared, destroy exactly that,
and the divergence is subtle: it will not show up in a nominal test and a
learner reading the comparison cannot see it.

**What the score architecture changes about this item.** Once `PL-T691` lands,
a branch's pre-branch history is the parent's own score rather than a
reproduction of it, so the property holds by construction. That does not retire
this item - it changes what it guards. A test that passes because the two
objects are the same object is exactly the test that would keep passing if a
later change quietly reintroduced a copy, so the assertion has to be written
against sampled *values* at the boundary, and against a branch taken between
recorded samples as well as on one.

**If exactness is unreachable** for some branch point, the divergence is
bounded, documented in `docs/MODEL.md`, and shown to the user rather than
implied to be absent. `docs/MODEL.md`'s "The reproducibility guarantee" already
names a different step size as outside its cover; this item states where a
branch sits relative to that.

**Where.** `tests/reference` and `tests/integration` for the assertions;
`docs/MODEL.md` for what is guaranteed and what is not.

**Done when.** A branch taken on a recorded sample and a branch taken between
two of them each reproduce the parent element-wise at every sampled point up to
the branch point, asserted by test; and `docs/MODEL.md` states the guarantee
and its limits.

**Its blocker moved from `PL-TFX5` to `PL-B8MK` on 2026-09-14**, when the
project owner split `PL-TFX5`'s bookmark clause out and `PL-TFX5` closed on the
control-event half. The fork mechanism this item asserts against now exists -
`SimulationController.resumed_at` and `BranchedCase` - so the first half of
Done when, "a branch taken on a recorded sample", is assertable today. The
second, "a branch taken between two of them", is not: an instant the run holds
no keyframe for is refused rather than approximated, and whether it stops being
refused - and by which of two measured routes - is `PL-B8MK`. Starting this
item before that answer would either assert half of what it promises or assert
the other half against a mechanism that may change shape.

`PL-TFX5` also measured what this item's tolerance language is about, which is
worth having before the assertions are written: a branch opened off a keyframe
disagrees with the run it claims to continue at essentially every later
instant, and `tests/unit/test_run_definition.py` now pins that as non-zero and
under 1e-12. That is the divergence this item's "where exactness is unreachable"
clause would have to bound and show.

## Promoted 2026-09-20, and most of it is already true

`PL-B8MK` closed the same day, so the blocker this item named is gone and the
half of `Done when` it was waiting for - "a branch taken between two of them" -
is buildable: a fork at a bookmark halt is precisely a fork at an instant the
run holds no keyframe for. Read against the tree, what is left is narrower than
the brief above, and the next session should not redo what is already pinned.

**Already asserted, in `tests/integration/test_controller.py`.** A branch taken
on a recorded sample reproduces its parent element-wise over 201 shared
instants (`test_a_branch_reproduces_its_parent_at_every_instant_they_share`,
from `PL-TFX5`). A branch taken *between* two, at a bookmark halt, reproduces
it over 301 shared instants while leaving the trunk element-for-element the
case it would have been unmarked
(`test_a_branch_taken_at_a_bookmark_reproduces_its_parent_without_changing_it`),
and over 601 under three orderings of a dial and a reset
(`test_two_reversible_acts_in_either_order_leave_one_branch`).

**Already stated, in `docs/MODEL.md` § "What this requires of a branch".** The
guarantee, which of its two conditions a bookmark fork relaxes and why the
guarantee survives it, and its limits: the one drawn column a bookmark branch
adds that its parent does not, and the drawn values at the columns they share
being equal to floating-point composition rather than bit for bit - 2 977 of
3 438 elements, worst 7.70e-16 as a fraction, against 0 of 382 canonically.

**What is left, and it is the reason this stays open.** The assertions above
are integration tests; `tests/reference/test_canonical_evaluation.py` holds the
keyframe case (`test_a_fork_opening_from_a_keyframe_reproduces_its_parent`) and
has no counterpart for a fork between two keyframes, which is the tree where
this project puts a claim it wants checked against the arithmetic rather than
against the app. And this item's "if exactness is unreachable" clause needs
answering rather than implementing: exactness *is* reachable on the canonical
path, so what `docs/MODEL.md` owes is the statement that the bound is zero
there and non-zero on the display path, which is now written - the clause asks
for a divergence to be shown to the user, and there is none to show. Say so and
close the clause rather than building a display for it.

**Banded `P1` on promotion**, which `docket check` holds every `safety`- or
`science`-classed item to outside `blocked`, and leaving `blocked` returns it
to the debt gate it was exempt from as `anticipated` (`PL-ZF2G`). The hazard is
not live: the property this item asserts holds today and is measured, so what
changed is that the assertion can be written where this project wants it, not
that anything displayed is wrong.
