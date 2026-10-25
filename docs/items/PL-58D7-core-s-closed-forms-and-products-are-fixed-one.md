---
id: PL-58D7
title: core's closed forms and products are fixed one at a time at extreme inputs - overflow to inf, underflow to zero, cancellation and rounding at the wrong scale - because nothing states the floating-point domain each operation must hold: nine members from 2026-09-06 to 2026-10-17
priority: P1
effort: L
status: ready
classes: defect, refactor
feature: defect-review-2026-10
touches: src/anesthesia_sim/core, docs/MODEL.md, tests/unit
deferred-from: v0.7.0 - recorded as a generator head by PL-R4Y2's defect review on 2026-10-25; each member's safety finding was filed and placed by its own triage, and this head's work is the structure that stops the next one
added: 2026-10-25
payoff: each core operation states and enforces the inputs on which its floating-point answer is correct, so an extreme input is refused at build rather than found as a nan or a negative uptake
verify: grep -rq 'def test_every_core_operation_refuses_inputs_outside_its_floating_point_domain' tests/unit
root-cause-of: PL-3PRZ, PL-2MD9, PL-6QYJ, PL-8H2R, PL-B26Y, PL-YT8N, PL-XWFP, PL-FNH3, PL-8LQZ
generator: live - seven members filed 2026-10-03 to 2026-10-17, the last two closed 2026-10-19, each fixed for its own operation with no stated domain for the next
misread: The floating-point input domain on which each closed form and product in core gives a correct answer
---

**Problem.** core's closed forms and products are fixed one at a time at extreme inputs - overflow to inf, underflow to zero, cancellation and rounding at the wrong scale - because nothing states the floating-point domain each operation must hold: nine members from 2026-09-06 to 2026-10-17

**The fact the members misread.** Each closed form and product in `core/` has a range of inputs over which IEEE 754 doubles give a correct answer. The code assumed the supported ranges kept every operation inside that range, and at the extremes of what the constructors admit they did not:

- `PL-3PRZ`: the accounting guard stopped catching a tiny alveolar volume at 1e-300 L.
- `PL-2MD9`: the propagator's squarings amplified rounding in its constant state row to 2.28e+222.
- `PL-6QYJ`: chaining one exact propagator over a 1e-12 s spacing drew a change about 9e-3 wrong.
- `PL-8H2R`: `floor(span / step) * step` landed one float past 86,400 s, or one step short.
- `PL-B26Y`: the circuit time constant overflowed to inf below about 2e-306 L/min.
- `PL-YT8N`: `1 - exp(-dt/tau)` lost its digits to cancellation, giving a negative exhaust.
- `PL-XWFP`: the closed-form update rounded at the wrong scale, reporting uptake as a return.
- `PL-FNH3`: a volume times a partition coefficient overflowed to inf, and `inf * 0.0` gave nan.
- `PL-8LQZ`: the same product underflowed to 0.0, and a later division raised.

**Why it is live.** Seven of the nine were filed between 2026-10-03 and 2026-10-17, and the last two closed on 2026-10-19. Each fix guarded its own operation: `expm1` for one, a refusal at build for another. Nothing states, for each operation, the input domain on which it is correct, so the next operation is found the same way.

**What to do.** For each closed form and product in `core/`, state the input domain on which it is correct and how that domain was measured, and make the constructors refuse what falls outside it rather than relying on the clinical ranges to stay clear. `docs/MODEL.md` § "Numerical method" is where the domain is stated, and a test per operation probes both edges. This is core work, held to the safety-critical standard. Before building, check whether the `numerical-domain` feature already holds part of this.

**Why it matters.** At an extreme input these operations returned nan, a negative uptake or a silently wrong concentration rather than refusing. The safety-critical standard prefers an obvious failure to a plausible-looking number, and each operation has had to be found separately.

**Done when.** Each closed form and product in `core/` has a stated input domain with its measurement, the constructors refuse inputs outside it, and a test per operation probes both edges.

**Generator check.** This item is the head.
