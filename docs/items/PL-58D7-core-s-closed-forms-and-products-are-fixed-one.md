---
id: PL-58D7
title: core's closed forms and products are fixed one at a time at extreme inputs - overflow to inf, underflow to zero, cancellation and rounding at the wrong scale - because nothing states the floating-point domain each operation must hold: nine members from 2026-09-06 to 2026-10-17
priority: P1
effort: L
status: ready
classes: defect, refactor
feature: defect-review-2026-10
touches: src/anesthesia_sim/core, src/anesthesia_sim/data, docs/MODEL.md, tests/unit
blocked-by: PL-QX2G, PL-YT3T
deferred-from: v0.7.0 - recorded as a generator head by PL-R4Y2's defect review on 2026-10-25; each member's safety finding was filed and placed by its own triage, and this head's work is the structure that stops the next one
added: 2026-10-25
payoff: each core operation states and enforces the inputs on which its floating-point answer is correct, so an extreme input is refused at build rather than found as a nan or a negative uptake
verify: grep -rq 'def test_every_core_operation_refuses_inputs_outside_its_floating_point_domain' tests/unit && grep -rq 'def test_every_core_operation_holds_its_equations_at_every_envelope_corner' tests/unit
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

**Design round, 2026-10-25: state the domain once per input, not once per operation.** The brief as filed asked for a domain per operation. That shape repeats the generator. A domain written for one operation says nothing about the next operation someone adds, which is how each of the nine members was found. An inventory on 2026-10-25 listed 39 run-time operations in `core/` and every input that feeds them. The flows, the run's step, the case instant, the step count and the concentrations already have closed intervals, enforced once by a checked type. The members those inputs caused are fixed, and the inventory found no exposure left there. What remains comes from inputs bounded only by "positive and finite", and from two places with no upper bound at all:

- the circuit, alveolar, venous and tissue volumes and the blood:gas and tissue:gas partition coefficients, whose products and quotients still overflow, underflow or divide by zero (`PL-QX2G`);
- a compartment's own step, which has a floor and no ceiling (`PL-YT3T`);
- the number of samples one `RunDefinition` evaluation may produce (`PL-06LS`);
- the validator's running totals, summed without compensation over up to 8.64e7 steps (`PL-XST1`, a measurement first).

So the fix gives each input a declared numerical envelope, the way `MINIMUM_SIMULATION_STEP_S` already gives the step a floor. Each input is refused outside its envelope when it is built, as a checked type. Every product and quotient of inputs inside the envelope then stays many decades inside the float range, because the extremes of a product or quotient of positive inputs over a box lie at the box's corners. That is what stops the generator. An operation added later inherits the envelope without anyone writing a domain for it, and one sweep that runs every operation at every corner of the envelope tests it without anyone listing it.

Two members are not caught by a bound: `PL-YT8N`'s cancellation and `PL-XWFP`'s rounding at the wrong scale. Both are already fixed in `core/exponential_approach.py` and `BreathingCircuit.advance_fresh_gas`. The corner sweep is what would catch the next one of that kind, so it checks each result against what the equations require at that corner, not only that it is finite.

Recorded as the session's decision, not the owner's. It changes the mechanism and not the end state. Each input still has a stated domain, the constructors still refuse outside it, and a test still probes it.

**What is left for this item once its four members close.** Write the sweep. It takes the envelope's corners for every input, together with zero and the smallest positive subnormal for each flow that may be zero. At each corner it builds the system and each compartment, advances them by one step at the step's floor and at its ceiling, and evaluates a `RunDefinition` across the supported run length. Each result must be finite and non-negative, must close the mass balance within its tolerance, and must lie between its initial value and its equilibrium. Any refusal must be an error from `core/exceptions.py`. A second test builds every input one representable value past each edge of its envelope and expects a refusal. State the envelope in `docs/MODEL.md` § "Numerical method", in one table that reads its bounds from the module that holds them.

**Why it matters.** At an extreme input these operations returned nan, a negative uptake or a silently wrong concentration rather than refusing. The safety-critical standard prefers an obvious failure to a plausible-looking number, and each operation has had to be found separately.

**Done when.** `PL-QX2G`, `PL-YT3T`, `PL-06LS` and `PL-XST1` are closed. Every input to `core/` has a declared envelope, stated in `docs/MODEL.md` with its measurement and refused outside it when built. The corner sweep above and the refusal test past each edge pass.

**Generator check.** This item is the head.
