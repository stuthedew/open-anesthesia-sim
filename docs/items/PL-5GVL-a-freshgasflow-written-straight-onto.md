---
id: PL-5GVL
title: A FreshGasFlow written straight onto BreathingCircuit.fresh_gas_flow_l_min past set_fresh_gas_flow is held to its type alone by __setattr__ (PL-LBQY), so one outside the machine's deliverable_fresh_gas_flow_range is admitted where the constructor and the setter refuse it through _require_deliverable_flow; it binds nothing while no shipped profile declares a range, and is the flow side of the range guard PL-19Y0 folded in from PL-HJ7L (found in PL-KFNP's design round)
status: untriaged
feature: parse-dont-validate
touches: src/anesthesia_sim/core/circuit.py, tests/unit/test_circuit.py
added: 2026-10-12
---

**Problem.** A FreshGasFlow written straight onto BreathingCircuit.fresh_gas_flow_l_min past set_fresh_gas_flow is held to its type alone by __setattr__ (PL-LBQY), so one outside the machine's deliverable_fresh_gas_flow_range is admitted where the constructor and the setter refuse it through _require_deliverable_flow; it binds nothing while no shipped profile declares a range, and is the flow side of the range guard PL-19Y0 folded in from PL-HJ7L (found in PL-KFNP's design round)
