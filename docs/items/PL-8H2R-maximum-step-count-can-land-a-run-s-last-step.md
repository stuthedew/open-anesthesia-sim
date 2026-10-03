---
id: PL-8H2R
title: maximum_step_count can land a run's last step one float past 86 400 s for some computed step sizes, against its own docstring, so the step-count and time-axis bounds on the supported run length disagree there
status: untriaged
feature: numerical-domain
added: 2026-10-03
---

**Problem.** maximum_step_count can land a run's last step one float past 86 400 s for some computed step sizes, against its own docstring, so the step-count and time-axis bounds on the supported run length disagree there

**Measured 2026-10-03** while building `PL-73ZN` and `PL-BMY5` (#1292).
`maximum_step_count` is `floor(86_400.0 / simulation_step_s)`, and its
docstring says the last step "lands on `MAXIMUM_ELAPSED_SIMULATION_TIME_S` or
the largest simulated time below it". Floating-point division can round a
quotient lying just below a whole number up to it, and the product then lands
past the span: at a `simulation_step_s` of `0.07680000000000001` (computed as
`768 / 1_000_000 * 100`) the count is 1 125 000 and the last step's
`elapsed_s` is `86400.00000000001`. Nine such steps turned up among
`k / 1_000_000 * 100` for k up to 1000, all one doubling family from
`0.00030000000000000003`. None among the 111 111 literal decimal steps from
`1e-6` to `0.1` (`float("0.0768")` lands inside), and none among 2 000 000
uniform random steps in that range. The shipped 0.1 s lands exactly on
86 400.0, which `test_the_shipped_step_reaches_the_boundary_exactly` pins;
`test_the_last_supported_step_lands_inside_the_declared_span` checks seven
literal steps, so it cannot see this.

**Why it matters now.** Until `PL-73ZN` nothing compared an instant with the
span on the time axis, so the overshoot contradicted only a docstring. Now
`require_supported_case_instant` refuses a `RunDefinition` opening past
86 400.0 s while `require_supported_step_count` accepts the count that reaches
`86400.00000000001`, so a branch whose definition would open on the halted
instant of a run at such a step is refused. That is an obvious error rather
than a wrong number, and the application steps at 0.1 s only, so nothing
reaches it today.

**Candidate fix.** Step the count back while `count * simulation_step_s`
exceeds the span, with a regression test at `0.07680000000000001` that fails
today. It moves the halt one step earlier for such steps and for no other.
Once the two bounds agree, `RunDefinition.advance_to` could carry the same
guard as the opening; today that would turn this overshoot into a refusal
after the state had already stepped, which is why the reach is unguarded
(`advance_to`'s docstring).
