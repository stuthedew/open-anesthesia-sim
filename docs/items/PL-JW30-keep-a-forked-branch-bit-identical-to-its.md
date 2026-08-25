---
id: PL-JW30
title: Keep a forked branch bit-identical to its parent up to the branch point
status: dropped
feature: scenario-branching
added: 2026-08-25
closed: 2026-08-25
reason: aspirational rather than actionable; it constrains work that does not exist yet, so it was promoted to ROADMAP.md planned milestone 12 as a required property of forking
---

**Problem.** If a branch is created by resimulating from a stored point while
its parent was simulated straight through, the two histories can differ
before the branch point by floating-point rounding — different accumulation
order for `elapsed_s`, a different step size, or a different number of steps
per frame.

**Why it matters.** The entire purpose of forking is to attribute a
difference between two curves to the one setting that was changed. Two curves
that diverge *before* the branch point, by an amount nobody declared,
undermine exactly that. It is subtle, it will not show up in a nominal test,
and a learner reading the comparison has no way to see it.

**Where.** Wherever restore-and-resimulate lands (PL-RRWV, PL-WRKL).

**Done when.** A branch taken at time t reproduces its parent's state exactly
at every recorded sample up to t — asserted by a regression test that
compares the two histories element-wise, not within a tolerance — or, if
exactness is not achievable, the divergence is bounded, documented in
`docs/MODEL.md`, and visible to the user rather than implied to be absent.
