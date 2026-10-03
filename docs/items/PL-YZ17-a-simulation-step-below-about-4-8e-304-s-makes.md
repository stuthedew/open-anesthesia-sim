---
id: PL-YZ17
title: A simulation step below about 4.8e-304 s makes maximum_step_count raise OverflowError, outside the simulator's exception hierarchy, because 86 400 s divided by the step overflows to infinity; require_supported_simulation_step accepts every positive finite step up to 0.1 s, so the model declares no smallest supported step
status: untriaged
feature: numerical-domain
added: 2026-10-03
---

**Problem.** A simulation step below about 4.8e-304 s makes maximum_step_count raise OverflowError, outside the simulator's exception hierarchy, because 86 400 s divided by the step overflows to infinity; require_supported_simulation_step accepts every positive finite step up to 0.1 s, so the model declares no smallest supported step

**Found 2026-10-03** while fixing `PL-8H2R`. `maximum_step_count` opens with
`floor(86_400.0 / simulation_step_s)`, and at a step of `5e-324` the quotient
is `inf`, so `floor` raises `OverflowError: cannot convert float infinity to
integer`. `SimulationState(step_count=0, simulation_step_s=5e-324)` reaches it
through `require_supported_step_count`, after
`require_supported_simulation_step` has accepted the step. It was the same
before `PL-8H2R`, which neither widened nor narrowed the range: its search
raises only where the quotient itself overflows (measured over the first
2 000 floats above 4.8e-304 s, and 20 000 steps from 4.81e-304 to
9.6e-304 s). Nothing reaches it today: the application steps at 0.1 s only.

The narrow fix is to refuse such a step with `SimulationConfigurationError`.
The real question underneath is whether the model should declare a smallest
supported step at all, as it declares the largest - a step so small that 24
hours is more steps than a float counts exactly (about 9.6e-12 s, where the
count passes 2^53) already makes `elapsed_s` round the count before
multiplying. That is a declared bound, and so a recorded decision rather than
a guard added in passing.
