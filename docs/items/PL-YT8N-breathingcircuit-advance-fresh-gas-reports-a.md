---
id: PL-YT8N
title: BreathingCircuit.advance_fresh_gas reports a negative exhaust, as low as -3.3e-16 L, at admitted flows from 1e-15 to 1e-6 L/min, because 1 - exp(-dt/tau) loses its digits to cancellation when dt/tau is small; the exhaust it integrates cannot be negative (found fixing PL-B26Y)
status: untriaged
touches: src/anesthesia_sim/core/circuit.py, tests/unit/test_compartment_primitives.py
added: 2026-10-05
---

**Problem.** BreathingCircuit.advance_fresh_gas reports a negative exhaust, as low as -3.3e-16 L, at admitted flows from 1e-15 to 1e-6 L/min, because 1 - exp(-dt/tau) loses its digits to cancellation when dt/tau is small; the exhaust it integrates cannot be negative (found fixing PL-B26Y)

**Measured 2026-10-05, fixing `PL-B26Y`.** A 6 L circuit loaded to a fraction
of 1e-6 under a 100% dial, at `FreshGasFlow(1e-12)`, returns
`exhausted_agent_l=-3.3173277925717057e-16` from `advance_fresh_gas(0.1)`,
beside 1.67e-15 L delivered:
`uv run python -c "from anesthesia_sim.core.circuit import BreathingCircuit; from anesthesia_sim.core.concentration import Fraction, Percent; from anesthesia_sim.core.supported_ranges import FreshGasFlow; c = BreathingCircuit(circuit_volume_l=6.0, fresh_gas_flow_l_min=FreshGasFlow(1e-12), delivered_concentration_percent=Percent(100.0), inspired_partial_pressure_fraction=Fraction(1e-6)); print(c.advance_fresh_gas(0.1))"`.
`main` before that fix printed `-3.317327792571707e-16`. The exhaust it stands
for, the flow times the inspired fraction integrated over the step, is about
1.7e-21 L here and cannot be negative. A walk over flows from 5e-324 to 10
L/min, steps of 0.1, 1 and 60 s and three circuit states (the default one, the
one above, and a washout from 2%) found 11 negative exhausts in 126 finite
cases, all at flows from 1e-15 to 1e-6 L/min, the largest -3.3e-16 L. The
closed form before `PL-B26Y` and after it gave the same 11.

**Why.** `1.0 - exp(-dt/tau)` subtracts two numbers within an ulp of 1 when
`dt/tau` is small, so its absolute error is up to half an ulp of 1, about
5.6e-17, and the exhaust multiplies it by the circuit's volume: 6 L times that
is the 3.3e-16 L above. Where the washout the term stands for is smaller than
that, its sign is the rounding's.

**Reach.** As `PL-B26Y`'s: not a run's path, whose exhaust is
`AgentUptakeSystem.advance()`'s accounting, but the circuit's own closed form,
which `BreathingCircuit.advance`, a notebook or a test calls, and a negative
amount of agent folded into a balance is a plausible-looking wrong value.

**What a fix has to decide.** `-expm1(-dt/tau)` keeps the digits, but the
stored fraction is updated with `exp(-dt/tau)`, so using it in the exhaust
alone would trade the sign for a circuit balance that closes less well, by
about the same 3e-16 L. Using it in both would write the fraction update as
`i + (d - i) * -expm1(-dt/tau)` rather than `d + (i - d) * exp(-dt/tau)`, which
is exact at zero flow without a branch, and so would move the analysis
`src/anesthesia_sim/core/__init__.py` § "Zero flow is tested with `== 0.0`,
never against a tolerance" and `tests/unit/test_compartment_primitives.py` rest
on (`PL-79YX`), and `tissue.py` and `blood.py` update their fractions in the
same `d + (i - d) * exp(-dt/tau)` form.
