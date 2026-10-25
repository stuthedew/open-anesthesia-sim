---
id: PL-YT3T
title: A compartment's own step has a floor and no ceiling, so BreathingCircuit.advance_fresh_gas at a step near 1e308 s, or at a circuit volume near 1e-310 L, overflows the time constants elapsed to inf and returns an exhaust of inf or nan without checking it
priority: P1
effort: S
status: blocked
classes: defect, safety
feature: floating-point-domain
touches: src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/simulation_step.py, tests/unit
blocked-by: PL-QX2G
added: 2026-10-25
payoff: a compartment stepped on its own refuses rather than returning an exhaust of inf or nan
verify: grep -rq 'def test_a_compartment_step_refuses_a_step_whose_exchange_would_not_be_finite' tests/unit
---

**Problem.** A compartment's own step has a floor and no ceiling, so BreathingCircuit.advance_fresh_gas at a step near 1e308 s, or at a circuit volume near 1e-310 L, overflows the time constants elapsed to inf and returns an exhaust of inf or nan without checking it

**Where it is.** `require_at_least_the_smallest_step` gives a compartment's own `advance` a floor of `MINIMUM_SIMULATION_STEP_S` and no ceiling (`PL-WP52` declined the ceiling for a compartment). In `BreathingCircuit.advance_fresh_gas`, `time_constants_elapsed = admitted_gas_l / self.circuit_volume_l` overflows to `inf` at a step near 1e308 s, or at a circuit volume near 1e-310 L at 10 L/min and 0.1 s. Then `fresh_gas_out_l = self.circuit_volume_l * (time_constants_elapsed - fraction_replaced)` is `inf`, and the exhaust is `inf` during wash-in or `0.0 * inf`, which is `nan`, when the delivered fraction is at or below the circuit's. `FreshGasExchange` does not check either. Found by the `PL-58D7` inventory on 2026-10-25 by reading the code; not yet reproduced. The run path does not call `advance_fresh_gas`: only `BreathingCircuit.advance` and the tests do. The venous and tissue `advance` methods take the same unbounded step.

**What to do.** Give a compartment's own step the ceiling that makes these products finite, or refuse a non-finite result before it is returned. `PL-QX2G` bounds the circuit volume. Its envelope and this ceiling together have to keep `time_constants_elapsed` finite, so decide this ceiling from that envelope.

**Why it matters.** A compartment stepped on its own can return an exhaust of `nan` with no error, the kind of plausible-looking failure the safety-critical standard refuses.

**Done when.** No compartment `advance` can return a non-finite amount for any input it accepts, and a test shows the refusal at the edge of what it accepts.

**Generator check.** A member of the `floating-point-domain` feature, split from `PL-58D7`, the generator head.
