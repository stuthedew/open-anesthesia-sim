---
id: PL-8H2R
title: maximum_step_count can land a run's last step one float past 86 400 s, or stop it one step short of 86 400 s, for some computed step sizes, so the step-count and time-axis bounds on the supported run length disagree there
status: untriaged
feature: numerical-domain
added: 2026-10-03
---

**Problem.** maximum_step_count can land a run's last step one float past 86 400 s, or stop it one step short of 86 400 s, for some computed step sizes, so the step-count and time-axis bounds on the supported run length disagree there

**Measured 2026-10-03** while building `PL-73ZN` and `PL-BMY5` (#1292), and
widened the same day by that pull request's two adversarial reviews.
`maximum_step_count` is `floor(86_400.0 / simulation_step_s)`, and its
docstring says the last step "lands on `MAXIMUM_ELAPSED_SIMULATION_TIME_S` or
the largest simulated time below it". Floating-point division breaks that in
both directions:

- **Overshoot.** A quotient lying just below a whole number rounds up to it,
  and the product then lands past the span: at a `simulation_step_s` of
  `0.07680000000000001` (computed as `768 / 1_000_000 * 100`) the count is
  1 125 000 and the last step's `elapsed_s` is `86400.00000000001`. Nine such
  steps among `k / 1_000_000 * 100` for k up to 1000, all one doubling family
  from `0.00030000000000000003`; 6 583 of the steps `0.1 / n` for n up to
  200 000, the first at n = 21. None among the 111 111 literal decimal steps
  from `1e-6` to `0.1` (`float("0.0768")` lands inside), and none among
  2 000 000 uniform random steps in that range.
- **Undershoot.** A quotient lying just above a whole number rounds down past
  it, so the count is one short of a step that lands exactly on the span: at
  `0.02304` the count is 3 749 999 and stops at `86399.97696`, while
  3 750 000 steps give exactly `86400.0`. 11 924 of the `0.1 / n` steps for n
  up to 200 000, and 13 of the 100 000 literal steps `ke-6` up to 0.1: the
  doubling family from `4.5e-5` (`9e-5`, `0.00018`, ... `0.02304`,
  `0.04608`, `0.09216`) and `0.084375`. None among the same steps computed
  as `k * 1e-6`, in either direction.

The shipped 0.1 s lands exactly on 86 400.0, which
`test_the_shipped_step_reaches_the_boundary_exactly` pins;
`test_the_last_supported_step_lands_inside_the_declared_span` checks seven
literal steps, so it sees neither direction.

**Why it matters now.** Until `PL-73ZN` nothing compared an instant with the
span on the time axis, so either direction contradicted only a docstring. Now
two bounds read it differently: `require_supported_step_count` reads the
count, as the step's guard does, and `require_supported_case_instant` reads the
instant. At an overshoot step a run halts at `86400.00000000001`, and the two
ways a branch is taken there disagree: a branch at a bookmark opens its
`RunDefinition` at the keyframe before and moves its reach to the halt, so it
is built; a branch at a control event opens its `RunDefinition` on the halt
itself, so it is refused. At an undershoot step the step-count guard refuses a
state built at the count that lands exactly on 86 400.0, while the case-instant
guard accepts that instant. Each is an obvious error rather than a wrong
number, and the application steps at 0.1 s only, so nothing reaches either
today.

**Candidate fix.** Return the largest count whose product with the step does
not exceed the span: step the floored count back while `count *
simulation_step_s` exceeds it, then forward while `(count + 1) *
simulation_step_s` does not. The product is monotone in the count, so that is
well defined, and it moves the halt only at steps where floor and product
disagree. Regression tests at `0.07680000000000001` and `0.02304` that fail
today; `test_a_run_may_be_built_where_stepping_stops_it_and_no_further`
already carries both steps and asserts only that the two count guards agree,
which stays true. #1292 left a `PL-8H2R` pointer at every sentence the fix
would make true again or let go: `maximum_step_count`'s and
`require_supported_step_count`'s docstrings, `require_supported_case_instant`'s,
`RunDefinition.advance_to`'s, and `docs/MODEL.md` § "Supported run length".
Once the bounds agree, `RunDefinition.advance_to` could carry the same guard as
the opening; today that would turn an overshoot into a refusal after the state
had already stepped, which is why the reach is unguarded (`advance_to`'s
docstring).
