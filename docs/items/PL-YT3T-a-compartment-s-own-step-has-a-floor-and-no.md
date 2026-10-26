---
id: PL-YT3T
title: A compartment's own step has a floor and no ceiling, so BreathingCircuit.advance_fresh_gas at a step near 1e308 s, or at a circuit volume near 1e-310 L, overflows the time constants elapsed to inf and returns an exhaust of inf or nan without checking it
priority: P1
effort: S
status: done
classes: defect, safety
feature: floating-point-domain
touches: src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/simulation_step.py, src/anesthesia_sim/core/supported_ranges.py, src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/blood.py, docs/MODEL.md, tests/unit
blocked-by: PL-QX2G
added: 2026-10-25
closed: 2026-10-26
pr: 1861
payoff: a compartment stepped on its own refuses rather than returning an exhaust of inf or nan
verify: grep -q 'def test_a_step_past_the_run_length_is_refused_when_the_circuit_is_stepped_alone' tests/unit/test_circuit.py && grep -q 'def test_a_step_past_the_run_length_is_refused_when_a_tissue_is_stepped_alone' tests/unit/test_tissue.py && grep -q 'def test_a_step_past_the_run_length_is_refused_when_the_pool_is_stepped_alone' tests/unit/test_blood.py
---

**Problem.** A compartment's own step has a floor and no ceiling, so BreathingCircuit.advance_fresh_gas at a step near 1e308 s, or at a circuit volume near 1e-310 L, overflows the time constants elapsed to inf and returns an exhaust of inf or nan without checking it

**Where it is.** `require_at_least_the_smallest_step` gives a compartment's own `advance` a floor of `MINIMUM_SIMULATION_STEP_S` and no ceiling (`PL-WP52` declined the ceiling for a compartment). In `BreathingCircuit.advance_fresh_gas`, `time_constants_elapsed = admitted_gas_l / self.circuit_volume_l` overflows to `inf` at a step near 1e308 s, or at a circuit volume near 1e-310 L at 10 L/min and 0.1 s. Then `fresh_gas_out_l = self.circuit_volume_l * (time_constants_elapsed - fraction_replaced)` is `inf`, and the exhaust is `inf` during wash-in or `0.0 * inf`, which is `nan`, when the delivered fraction is at or below the circuit's. `FreshGasExchange` does not check either. Found by the `PL-58D7` inventory on 2026-10-25 by reading the code; not yet reproduced. The run path does not call `advance_fresh_gas`: only `BreathingCircuit.advance` and the tests do. The venous and tissue `advance` methods take the same unbounded step.

**What to do.** Give a compartment's own step the ceiling that makes these products finite, or refuse a non-finite result before it is returned. `PL-QX2G` bounds the circuit volume. Its envelope and this ceiling together have to keep `time_constants_elapsed` finite, so decide this ceiling from that envelope.

**Why it matters.** A compartment stepped on its own can return an exhaust of `nan` with no error, the kind of plausible-looking failure the safety-critical standard refuses.

**Done when.** No compartment `advance` can return a non-finite amount for any input it accepts, and a test shows the refusal at the edge of what it accepts.

**Generator check.** A member of the `floating-point-domain` feature, split from `PL-58D7`, the generator head.

**Reproduced and fixed, 2026-10-26.** On `0b0fb6f6`, a 0.01 L circuit at 10 L/min stepped by 1e308 s returned an exhaust of `nan` with the circuit at the dial's 2%, and of `inf` with the circuit empty. The circuit-volume half of the problem was already closed by `PL-QX2G`, whose envelope floor of 0.01 L leaves only the step.

The ceiling chosen is the supported run length, `MAXIMUM_ELAPSED_SIMULATION_TIME_S` (86 400 s), read from `core/supported_ranges.py` rather than declared again. One step cannot stand for more simulated time than the span over which the model is claimed to represent a patient. At that ceiling, the largest supported fresh gas flow in the smallest circuit the envelope admits elapses about 1.4e6 time constants, about 300 decades inside the float range. A purely numerical ceiling near 1e306 s was the alternative. It was not taken because it would be a number with no meaning of its own, chosen only to sit below the overflow. A refusal of a non-finite result after the fact was not taken either, because the ceiling makes such a result impossible for every accepted input, and the corner sweep in `PL-58D7` checks that.

`require_compartment_step` in `core/supported_ranges.py` now holds both bounds. It checks the floor through `require_at_least_the_smallest_step`, and `BreathingCircuit.advance_fresh_gas`, `TissueGroup.advance` and `VenousBloodCompartment.advance` each call it. The tissue groups and the venous pool already returned a finite amount at any finite step, because `exponential_approach` saturates at equilibrium. They take the same ceiling so that one statement says which steps a compartment accepts. `docs/MODEL.md` § "Supported simulation step" states the ceiling and its reason. The verify command was rewritten to name the three tests as written, because the brief named a test before it existed.
