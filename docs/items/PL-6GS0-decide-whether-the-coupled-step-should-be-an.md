---
id: PL-6GS0
title: Decide whether the coupled step should be an exact matrix exponential rather than an operator split
priority: P2
effort: M
status: needs-decision
classes: planning
feature: numerical-domain
touches: docs/MODEL.md, ROADMAP.md, src/anesthesia_sim/core/respiratory_system.py
added: 2026-08-30
not-delegable: the next step is a decision about the numerical method, not code; no command can prove a decision, and the implementation it might authorize would edit `core/` and `docs/MODEL.md`, both protected paths.
---

**Problem.** The six-state coupled system is linear and time-invariant within
a step, because every setting is held piecewise-constant across it. A single
matrix exponential of the system matrix is therefore the *exact* solution of
the coupled system over that step, where the shipped first-order (Lie/Godunov)
operator split is not. That was the central architectural recommendation of the
v0.2.0 architecture review, and it has never been decided either way — the
review's own note deferred it, and the deferral has never been revisited.

**Why it matters.** Three things follow from an exact step, and none of them
is available today:

- The splitting error goes away rather than being bounded. `docs/MODEL.md`
  § "Selected method (as implemented)" documents it as \(O(\Delta t)\), and two
  release gates bound it empirically.
- `MAXIMUM_SIMULATION_STEP_S` stops being a model-fidelity limit. The
  applicability domain in `docs/MODEL.md` § "Supported simulation step" exists
  because the split degrades with step size; an exact step does not, so the
  guard PL-VP7N added (refuse a simulation step outside the operator split's
  applicability domain) would be enforcing a bound that no longer binds.
- It changes the answer to the playback-speed multiplier thread in
  `docs/WORKING_NOTES.md`, which is currently steps-per-tick precisely because
  a larger step is a model-fidelity question. Against an exact solver it is
  not one.

**Where.** The evidence is the measured comparison below, taken 2026-08-24 by
the retired review harness and carried here so that retiring it loses nothing.
Both columns are max-abs error across all six states against a from-scratch
RK4 oracle, at a 5% delivered fraction:

| agent | horizon | matrix exponential | pairwise split |
| --- | --- | --- | --- |
| sevoflurane | 60 s | 3.05e-16 | 7.01e-06 |
| sevoflurane | 3600 s | 3.22e-14 | 9.21e-06 |
| isoflurane | 60 s | 5.07e-16 | 1.41e-05 |
| isoflurane | 3600 s | 7.62e-15 | 1.68e-05 |
| desflurane | 60 s | 1.28e-16 | 7.14e-06 |
| desflurane | 3600 s | 4.77e-14 | 5.17e-06 |

The exponential was built by scaling-and-squaring in pure Python with no
dependencies, so adopting it adds no third-party numerical stack. The oracle
that produced the split column is now
`tests/reference/test_coupled_dynamics.py`; the exponential column has no
surviving implementation and would have to be rebuilt to be re-measured.

**Decision needed.** Adopt the exact matrix exponential as the coupled step,
decline it and keep the operator split, or defer it to a named milestone.

**The case against acting on it.** The split is not wrong
and nothing here is a defect: 1.7e-5 in a fraction is four orders of magnitude
below the precision anything is displayed at, and the two release gates prove
it stays there across the settings envelope. What an exact step buys is the
removal of a constraint, not the correction of an error — so this is worth
doing only if a larger step is wanted, which is the playback-multiplier
question. Doing it means a new numerical method in a safety-critical path,
`docs/MODEL.md` § "Numerical method" rewritten, and the pinned reference
vectors re-derived. Recommendation: leave the split in place and revisit this
when the playback multiplier is scoped, rather than as standalone work.

**Done when.** The project owner has decided to adopt the exponential, decline
it, or defer it explicitly to a named milestone, and `docs/MODEL.md`
§ "Selected method (as implemented)" records which — so the next reader finds
the answer rather than re-deriving the question. If adopted, this item is
replaced by scoped implementation items; it is not itself the implementation.

**Decided 2026-08-30: deferred, and the deferral is recorded.** The project
owner took the recommendation above - keep the operator split, and revisit the
exponential when a larger step is actually wanted rather than as standalone
work, the playback-speed multiplier being the case that would want it.

`docs/MODEL.md` § "Selected method (as implemented)" now carries "The exact
alternative, and why it is not taken": the linearity argument, the measured
comparison, the decision and its date, and the pointer back to this item for
the per-agent table. That is what this item's "Done when" asked for - the next
reader finds the answer rather than re-deriving the question - so the item is
closed rather than left open as a standing question.

It is deferred rather than declined. Reopen it, or supersede it with scoped
implementation items, if the playback multiplier is scoped in a form that wants
steps larger than `MAXIMUM_SIMULATION_STEP_S`; nothing else should reopen it,
because nothing else is wrong.
