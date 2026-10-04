---
id: PL-B26Y
title: BreathingCircuit.advance_fresh_gas reports a nan exhaust at an admitted fresh-gas flow below about 2e-306 L/min, because the circuit's time constant overflows to inf there and its zero-flow branch tests == 0.0 only; core/__init__.py says the branch agrees with the general path bit for bit at the smallest denormal, which holds for the fraction and not for the exhaust
status: untriaged
added: 2026-10-04
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
