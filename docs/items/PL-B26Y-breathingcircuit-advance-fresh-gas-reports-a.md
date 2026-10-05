---
id: PL-B26Y
title: BreathingCircuit.advance_fresh_gas reports a nan exhaust at an admitted fresh-gas flow below about 2e-306 L/min, because the circuit's time constant overflows to inf there and its zero-flow branch tests == 0.0 only; core/__init__.py says the branch agrees with the general path bit for bit at the smallest denormal, which holds for the fraction and not for the exhaust
priority: P1
effort: S
status: ready
classes: safety, defect
touches: src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/__init__.py, tests/unit/test_compartment_primitives.py
added: 2026-10-04
payoff: the circuit closed form can no longer hand a caller nan at a flow the model admits, and the package zero-flow claim becomes true of the exhaust as well as the fraction
verify: grep -q 'def test_the_circuit_exhaust_is_finite_where_its_time_constant_overflows' tests/unit/test_compartment_primitives.py
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
