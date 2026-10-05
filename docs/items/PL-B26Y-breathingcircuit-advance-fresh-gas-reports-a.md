---
id: PL-B26Y
title: BreathingCircuit.advance_fresh_gas reports a nan exhaust at an admitted fresh-gas flow below about 2e-306 L/min, because the circuit's time constant overflows to inf there and its zero-flow branch tests == 0.0 only; core/__init__.py says the branch agrees with the general path bit for bit at the smallest denormal, which holds for the fraction and not for the exhaust
priority: P1
effort: S
status: done
classes: safety, defect
touches: src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/__init__.py, tests/unit/test_compartment_primitives.py
added: 2026-10-04
closed: 2026-10-05
pr: 1367
payoff: the circuit closed form can no longer hand a caller nan at a flow the model admits, and the package zero-flow claim becomes true of the exhaust as well as the fraction
verify: grep -q 'def test_the_circuit_exhaust_is_finite_where_its_time_constant_overflows' tests/unit/test_compartment_primitives.py
recurrences: 2026-10-05 PL-YT8N
---

**Problem.** BreathingCircuit.advance_fresh_gas reports a nan exhaust at an admitted fresh-gas flow below about 2e-306 L/min, because the circuit's time constant overflows to inf there and its zero-flow branch tests == 0.0 only; core/__init__.py says the branch agrees with the general path bit for bit at the smallest denormal, which holds for the fraction and not for the exhaust

**Measured 2026-10-04, in `PL-51B7`'s session.** `FreshGasFlow(5e-324)` and
`FreshGasFlow(1.1125369292536007e-308)` are both admitted. On the default
circuit each gives `time_constant_s == inf`, and `advance_fresh_gas(1.0)`
returns `exhausted_agent_l=nan`: the integral's
`(initial - delivered) * tau * (1 - fraction_remaining)` is
`x * inf * 0.0`. At 1e-300 L/min the time constant is 3.6e302 s and the
exhaust is finite, so the failing band is every flow for which
`60 * circuit_volume_l / flow` overflows, below about 2e-306 L/min for the
6 L circuit. `core/__init__.py`'s walk from zero upwards checked the fraction,
which does agree bit for bit there; `PL-79YX`'s "the denormal and overflow
cases were checked and behave the same way" has the same gap.

**Reach.** Not on a run's path. A run steps through
`AgentUptakeSystem.advance()`, whose accounting is the exhaust the dashboard
shows (`app/dashboard_frame.py`); `advance_fresh_gas` is the circuit's own
closed form, called by `BreathingCircuit.advance` and by tests.
`tests/unit/test_supported_range_edges.py` does not reach it, because the
circuit's own step takes a `float` rather than a `SimulationStep`: `PL-0GJC`
typed the run's step only, and a compartment's floor is `PL-WP52`'s question.

**Where.** `src/anesthesia_sim/core/circuit.py` (`advance_fresh_gas` and its
`== 0.0` branch), `src/anesthesia_sim/core/__init__.py` § "Zero flow is tested
with `== 0.0`, never against a tolerance", and
`tests/unit/test_compartment_primitives.py`, which re-runs that section's
numbers.

**Reproduced 2026-10-04, at triage.** On Python 3.14.7, against `main` at
`8cc0698d`,
`uv run python -c "from anesthesia_sim.core.uptake_system import AgentUptakeSystem; from anesthesia_sim.core.supported_ranges import FreshGasFlow; c = AgentUptakeSystem.default().circuit; [print(flow, c.set_fresh_gas_flow(FreshGasFlow(flow)) or c.time_constant_s, c.advance_fresh_gas(1.0)) for flow in (5e-324, 1.1125369292536007e-308, 1e-300)]"`
printed a time constant of `inf` and `exhausted_agent_l=nan` at both
`5e-324` and `1.1125369292536007e-308` L/min, the second beside a finite
`delivered_agent_l=3.708456430845e-312`, and at `1e-300` L/min a time
constant of `3.6e+302` s and an exhaust of `3.3333333333333334e-304` L, equal
to the agent delivered. Both flows were admitted by `FreshGasFlow` and by the
default circuit's setter. A run is not affected: the same default system set
to `FreshGasFlow(5e-324)` and stepped once through
`AgentUptakeSystem.advance(SimulationStep(0.1))` reported a fresh gas exchange
of exactly zero both ways and an agent balance that passed.

**Why it matters.** Nothing a learner sees carries it, since the dashboard's
exhaust is the run step's accounting, measured above. What it reaches is a
caller of the circuit's own closed form - a test, a notebook,
`BreathingCircuit.advance` - which is handed `nan` at a flow the model admits,
with no refusal, where `CLAUDE.md`'s standard asks for a correct value or an
obvious failure, and a `nan` folded into any sum, a mass balance included,
makes the sum `nan` too. `core/__init__.py`, where a reader of the
compartments is sent, says the branch agrees with the general path bit for bit
at the smallest denormal, which a reader takes to cover the exhaust the branch
exists to keep finite; the test re-running that walk,
`test_the_zero_flow_branch_agrees_with_the_limit_from_above`, compares the
stored agent and discards the exchange each step returns, which is how the
claim passed.

**Done when.** `BreathingCircuit.advance_fresh_gas` returns a finite exhaust
at every admitted flow, the small-flow limit of the general path: at
`FreshGasFlow(5e-324)` and `FreshGasFlow(1.1125369292536007e-308)`, where
`time_constant_s` overflows to `inf`, the exhaust is finite, nonnegative and
no more than the flow in litres per second times the step times the larger of
the inspired and delivered fractions, as the general path's is at 1e-300
L/min. `core/__init__.py` § "Zero flow is tested with `== 0.0`, never against
a tolerance" states what is true of the exhaust as well as the fraction across
its walk from zero, the flows whose time constant overflows included. A test
in `tests/unit/test_compartment_primitives.py` named
`test_the_circuit_exhaust_is_finite_where_its_time_constant_overflows` pins it
at both flows.

**Fixed 2026-10-05.** The closed form writes the exhaust as what was delivered
less what the circuit kept, `delivered - V (F_D - F_I0)(1 - exp(-dt/tau))`:
the flow times the integral of the inspired fraction, with the flow times the
time constant written as the circuit's volume. Nothing in it multiplies by the
time constant, so a flow small enough to overflow it gets an exhaust equal to
what was delivered, as 1e-300 L/min already did: 0 L at 5e-324 L/min, and
1.854e-311 L over 0.1 s at 1.1125369292536007e-308. Measured against the old
form: across three circuit states and steps of 0.1, 1 and 60 s, the 27
overflowing cases go from `nan` to finite; across four states, flows from
1e-300 to 10 L/min and steps up to 600 s, every other value moves only within
the rounding the old form already carried - at most 1.4e-11 relative from 0.1
to 10 L/min, and up to 6e-8 relative at 1e-6 L/min, where the exhaust is
itself mostly that rounding, since both forms lose digits in
`1 - exp(-dt/tau)`. The circuit's own balance closes as well or better: a
worst residual of 5.6e-17 L against 4.4e-16 L at 6 L/min.

Two other routes were refused. A branch on an infinite time constant guards a
factor the rewrite removes, as a second special case beside `== 0.0`. Widening
the `== 0.0` branch to the overflowing flows would also freeze the fraction
there, so the smallest denormal would land on the branch while 1e-300 lands
one rounding from it, which is the band
`test_the_zero_flow_branch_agrees_with_the_limit_from_above` says does not
exist.

`test_the_circuit_exhaust_is_finite_where_its_time_constant_overflows` pins
both flows for a circuit washing in and one at the dial, and failed in all four
cases on the old form, `nan` each time. The zero-flow walk now asserts the
agent each step reports moving as well as what each compartment stores, and on
the old form it failed for the circuit at 5e-324 L/min. With the fix, the
circuit's `== 0.0` branch is no longer what stops a `nan`: removed, the circuit
reports an exchange of zero and holds 6.000000000172534e-06 L where it held
6e-06, so the branch now buys an exact no-op, as the patient compartments' do.
`core/__init__.py`'s bullet and walk paragraph and the two test docstrings say
so.

`PL-YT8N`, filed from this fix, is the same expression's other weakness: at
flows from 1e-15 to 1e-6 L/min, `1 - exp(-dt/tau)` loses its digits and the
exhaust comes out as much as 3.3e-16 L below zero, in the old form and the new
alike. `docket new` recorded it as a recurrence of this item; it is a different
mechanism, cancellation rather than overflow.
