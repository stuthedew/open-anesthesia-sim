---
id: PL-M85T
title: Three core class defaults restate data-file values (alveolar gas volume 2.5 L and ventilation 4.0 L/min in alveolar.py, circuit volume 6.0 L in circuit.py), and a fourth, the 100% maximum delivered concentration, matches no agent's vaporizer: decide whether they become required arguments
status: untriaged
feature: one-source-of-truth
added: 2026-10-19
---

**Problem.** Three class defaults in `core/` repeat values that the data files own. `AlveolarCompartment` defaults `gas_volume_l` to 2.5 L and `alveolar_ventilation_l_min` to 4.0 L/min, which `data/patients/reference_adult.json` stores as `alveolar_gas_volume_l` and `default_alveolar_ventilation_l_min`. `BreathingCircuit` defaults `circuit_volume_l` to 6.0 L, which `data/machines/reference_circle_system.json` stores. No check ties a default to its data value. Tests pin each side to the same literal separately, so changing the data file leaves the default behind without failing anything.

The fourth default is a different case. `BreathingCircuit.max_delivered_concentration_percent` defaults to 100%, and no agent file holds that value: the agent files hold 5% (isoflurane), 8% (sevoflurane) and 18% (desflurane). So this default does not restate a data value. It is a permissive placeholder: a circuit built without the argument accepts any dial setting up to 100%. The production path builds the circuit from the agent's data, so no shipped run uses the placeholder today. The decision is whether a placeholder like this should exist at all, under the safety-critical rule against silently substituting defaults.

Corrected at review on 2026-10-24. The worker's capture called all four "data-file values held equal only by tests", which is false for the 100% maximum.
