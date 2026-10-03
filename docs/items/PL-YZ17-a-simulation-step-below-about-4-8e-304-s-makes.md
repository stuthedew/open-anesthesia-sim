---
id: PL-YZ17
title: A simulation step below about 4.8e-304 s makes maximum_step_count raise OverflowError, outside the simulator's exception hierarchy, because 86 400 s divided by the step overflows to infinity; require_supported_simulation_step accepts every positive finite step up to 0.1 s, so the model declares no smallest supported step
priority: P1
effort: S
status: done
classes: defect, science
feature: numerical-domain
touches: src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/core/simulation.py, docs/MODEL.md, tests/unit/test_uptake_system_failure.py, tests/unit/test_simulation.py, tests/reference/test_sevo_patient.py
added: 2026-10-03
closed: 2026-10-03
pr: 1306
payoff: no step the model accepts is fine enough for rounding to decide what a step changes, and none escapes the simulator's own errors
verify: grep -q 'def test_the_smallest_supported_step_lands_on_the_ceilings_solution' tests/reference/test_sevo_patient.py && uv run pytest tests/unit/test_uptake_system_failure.py tests/unit/test_simulation.py tests/reference/test_sevo_patient.py
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

**Done 2026-10-03: the model declares a floor, `MINIMUM_SIMULATION_STEP_S` =
1 ms, and `require_supported_simulation_step` refuses a finer step with
`SimulationConfigurationError`** before any run length is read from it. The
narrow fix would have closed the overflow and left about 300 decades of
unmeasured step accepted, and measurement showed that range is not merely
unmeasured: rounding is a growing share of what each step changes as the step
shrinks. Over 10 000 steps from 60 s into the default sevoflurane wash-in, the
worst relative error in what the alveolar, vessel-rich, muscle and fat
fractions changed by is 3.3e-12 at 1 ms, 7.2e-9 at 1 us, 1.0e-4 at 0.1 ns and
3.2e-1 at 10 fs, with nothing raised at any of them. So a floor is what the
safety-critical standard's "an obvious failure rather than a plausible number"
asks for, and the question left was only where.

1 ms because it is the finest step the solution has been shown to be the
shipped one at - the bottom of `PL-X9KD`'s sweep, and now driven by the
step-refinement gate, which requires a minute in 1 ms steps to land within
3e-14 of the 0.1 s solution (measured 2.4e-15) - and nothing in the tree runs
finer; the finest step any test takes is 0.02304 s. It also covers the brief's
second point: 24 h at 1 ms is 86 400 000 steps, far inside 2^53. The growth
has no knee, so the value is declared rather than derived, as the ceiling is.
**The value was chosen by this session on that measurement, not by the
project owner**, and `docs/MODEL.md` § "Supported simulation step" records it
that way, so ordinary evidence reopens it.

`PL-8H2R`'s tests that call `maximum_step_count` at 1e-12, 1e-300 and
5e-304 s still stand: they test the function as a pure one, below any step a
caller can now pass it. Filed `PL-WP52` for the one question this left open, a
compartment stepped on its own, which still accepts any positive step.
