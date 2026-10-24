---
id: PL-84G1
title: core/circuit.py set_circuit_volume checks the stored agent against the circuit volume by hand, with a vaguer message, instead of calling validation.require_room_for_the_agent_held as the alveolar, blood and tissue compartments do
priority: P3
effort: S
status: ready
classes: refactor
feature: one-source-of-truth
touches: src/anesthesia_sim/core/circuit.py, tests/unit/test_circuit.py
added: 2026-10-19
payoff: a refused circuit volume names the volume, the agent held and the room left, as the other three compartments' refusals already do
verify: grep -q 'require_room_for_the_agent_held' src/anesthesia_sim/core/circuit.py
---

**Problem.** core/circuit.py set_circuit_volume checks the stored agent against the circuit volume by hand, with a vaguer message, instead of calling validation.require_room_for_the_agent_held as the alveolar, blood and tissue compartments do

**Why it matters.** The circuit makes the same check as the alveolar compartment, the venous pool and each tissue group, but writes it by hand. Its error says only "circuit_volume_l is smaller than stored agent". The shared helper's error names the volume written, the agent held, the room left and the section of `docs/MODEL.md` that explains it. A reader of the circuit's error has to work those out. And a later change to the rule, such as a tolerance, would reach three compartments and miss the fourth.

**Done when.** `BreathingCircuit.set_circuit_volume` calls `validation.require_room_for_the_agent_held` with the circuit's capacity and its section of `docs/MODEL.md`. A test in `tests/unit/test_circuit.py` pins the new message, and the refused volume still leaves the circuit unchanged.

**Checked 2026-10-24.** `set_circuit_volume` in `src/anesthesia_sim/core/circuit.py` raises `SimulationConfigurationError("circuit_volume_l is smaller than stored agent")` by hand. `require_room_for_the_agent_held` is called from `alveolar.py`, `blood.py` and `tissue.py`, and not from `circuit.py`.
