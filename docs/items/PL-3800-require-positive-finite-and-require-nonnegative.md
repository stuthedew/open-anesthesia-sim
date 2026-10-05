---
id: PL-3800
title: require_positive_finite and require_nonnegative_finite admit True (BreathingCircuit(circuit_volume_l=True) holds True, a 1 L circuit) and a Decimal (AlveolarCompartment(gas_volume_l=Decimal('2.5')) holds the Decimal), and refuse a str with math.isfinite's own TypeError, so every field they guard and SimulationStep, whose guard is built on the first, have the holes PL-LLMN closes for the flows and the concentrations; none is reachable from the interface; bring both guards to require_a_number in core/checked_number.py (found working PL-LLMN)
status: untriaged
feature: parse-dont-validate
touches: src/anesthesia_sim/core/validation.py, src/anesthesia_sim/core/simulation_step.py, tests/unit/test_validation.py, tests/unit/test_simulation_step.py
added: 2026-10-05
---

**Problem.** require_positive_finite and require_nonnegative_finite admit True (BreathingCircuit(circuit_volume_l=True) holds True, a 1 L circuit) and a Decimal (AlveolarCompartment(gas_volume_l=Decimal('2.5')) holds the Decimal), and refuse a str with math.isfinite's own TypeError, so every field they guard and SimulationStep, whose guard is built on the first, have the holes PL-LLMN closes for the flows and the concentrations; none is reachable from the interface; bring both guards to require_a_number in core/checked_number.py (found working PL-LLMN)
