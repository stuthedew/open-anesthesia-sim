---
id: PL-Z3W6
title: Assert a branch reproduces its parent element-wise at every sampled point up to the branch point
priority: P2
effort: M
status: blocked
blocked-by: PL-TFX5
classes: safety, science, test, anticipated
feature: scenario-branching
touches: tests/reference, tests/integration, docs/MODEL.md
added: 2026-09-06
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
