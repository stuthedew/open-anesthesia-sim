---
id: PL-ZHTT
title: docs/MODEL.md says an exact solver leaves the fixed 0.1 s step unaffected, and that is false — the step's determinism justification does not survive the matrix exponential
priority: P1
effort: S
status: done
classes: science, docs
touches: docs/MODEL.md
added: 2026-09-05
closed: 2026-09-06
pr: 376
verify: python3 tools/doc_check.py check && grep -qF 'What a longer step still costs is **control resolution**' docs/MODEL.md
---

**Problem.** `docs/MODEL.md` § "Selected method (as implemented)" closes with:

> "The fixed 0.1 s step is unaffected either way. The playback multiplier is
> implemented as steps per tick with the step fixed at 0.1 s, and it is fixed
> there for *determinism* — removing the step-size divergence and the
> machine-speed dependence that make a run irreproducible on another computer —
> rather than for accuracy, so an exact solver does not change that design."

The stated justification does not hold once `PL-GS5X` lands. "Step-size
divergence" is a property of the operator split's `O(dt)` error: two step
sizes reach different answers because each step is wrong by an amount that
depends on its width. An exact propagator has no such error, so there is
nothing for a fixed step to protect against — `e^{A(t2-t1)}` is the same
answer however the interval is subdivided.

**Evidence.** Measured 2026-09-05 in a standard-library prototype assembling
`A` and `b` from the shipped `reference_adult.json` and `sevoflurane.json`,
exponentiated by scaling-and-squaring with a Pade-13 approximant (Higham 2005,
*SIAM J. Matrix Anal. Appl.* 26(4):1179-1193), against an independent RK4
integration at `h = 0.002 s`:

| Horizon, in one matrix exponential | worst \|closed form - RK4\| |
| --- | --- |
| 60 s | 6.8e-17 |
| 600 s | 2.1e-16 |
| 3600 s | 4.2e-16 |

and one 3600 s jump against 36 000 chained 0.1 s steps of the same propagator
differs by **1.6e-14** worst case across all six states — floating-point
composition order, not method error. For comparison, the shipped split's own
recorded disagreement against the same class of oracle is 5.2e-6 to 1.7e-5.

**Why it matters.** This is a safety-critical specification document making a
false statement about the numerical method, in the section a reader consults
to learn why the step is what it is. It is also load-bearing rather than
incidental: the sentence is why `PL-GS5X` is scoped as a readability change
alone, and it is the reason the run's storage architecture has never been
re-examined. `docs/MODEL.md` derives the two-decimal displayed precision from
the split's error at exactly 0.1 s, so an exact step also removes a live
constraint on what the interface is permitted to show — which the same
paragraph does not say.

Determinism is still a requirement, and is still satisfiable — but by a stated
*canonical evaluation rule* (one exponential per inter-event interval,
composed in order from t=0) rather than by a fixed step width. That rule is
stronger than what ships today, because it makes the reproducibility guarantee
a property of the structure rather than of every caller using the same `dt`.

**Where.** `docs/MODEL.md` § "Numerical method" → "Selected method (as
implemented)", final paragraph. Related: `PL-X9KD` re-derives the statements
the splitting error justifies; `PL-GS5X` owns the replacement.

**Done when.** The paragraph states what an exact propagator does and does not
change about the step, names the canonical evaluation rule as what carries
determinism in its place, and no longer asserts that the fixed step is
unaffected. If `PL-GS5X` has not yet landed, the correction is written as
conditional on it rather than as describing what ships.
