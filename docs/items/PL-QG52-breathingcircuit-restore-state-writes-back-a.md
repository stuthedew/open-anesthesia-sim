---
id: PL-QG52
title: BreathingCircuit.restore_state writes back a captured fraction rather than an amount, so a restore after the circuit volume changed creates or destroys agent and the next step fails accounting
priority: P1
effort: S
status: ready
classes: defect, science
feature: replay-findings
touches: src/anesthesia_sim/core/circuit.py, tests/unit/test_state_capture.py
added: 2026-10-24
payoff: restoring a captured state can no longer create or destroy anaesthetic agent, before any feature lets the circuit volume change during a run
verify: grep -q 'def test_a_restore_after_a_circuit_volume_change_conserves_agent' tests/unit/test_state_capture.py
---

**Problem.** BreathingCircuit.restore_state writes back a captured fraction rather than an amount, so a restore after the circuit volume changed creates or destroys agent and the next step fails accounting

**Evidence.** Raised on `#204` by the panel's PK/PD and numerics reviewers and by both generalist runs, and reproduced by the blind checker at that merge: on the test `test_restoring_the_system_cannot_raise_on_a_state_a_run_produced`, a restore after a 6 L to 0.5 L volume change left 1.18e-4 L of the 1.33e-3 L stored, accounting failed, and the next `advance()` raised `AgentSimulationValidationError`. On `origin/main` on 2026-10-24, `BreathingCircuitState` still holds `inspired_partial_pressure_fraction`, and `BreathingCircuit.restore_state` shows no check of the volume. It was not re-run on `main`.

**Why it matters.** Every other compartment's captured state holds an amount, so a restore conserves agent. The circuit's holds a fraction, so a restore across a volume change silently creates or destroys agent, and the next step takes the blame. `advance()` cannot reach this today, but branches, rewinds and saved runs reuse capture and restore.

**Done when.** `BreathingCircuit.restore_state` either restores the captured amount of agent or refuses a restore onto a circuit whose volume differs from the captured one, and `tests/unit/test_state_capture.py` has `test_a_restore_after_a_circuit_volume_change_conserves_agent`, which restores after the volume change, asserts mass balance, and then advances once without an error.

**Reproduced 2026-10-24 on `main` at `91a98348`, through the core API only.** A sevoflurane run of ten 0.1 s steps held 1.3187e-3 L of agent in a 6 L circuit and 1.3260e-3 L in total. After `capture_state`, `circuit.set_circuit_volume(0.5)` kept the circuit's agent unchanged, so the volume setter conserves agent. `restore_state` then left 1.0989e-4 L in the circuit and 1.1718e-4 L in total. The next advance raised `AgentSimulationValidationError` with 1.2088e-3 L unaccounted (relative error 0.824). The fraction is stored at `BreathingCircuitState` (line 282 of `core/circuit.py`), and `restore_state` writes it back at line 756 with no check of the volume. The docstring at lines 266 to 270 already names the hazard. The existing test in `tests/unit/test_state_capture.py`, lines 380 to 407, restores after the volume change but never advances, so it passes.

**Reachable from the app? Not today.** The only automatic restores happen inside one call, in `AgentUptakeSystem.advance` and `resume_at`, and nothing changes the volume between capture and restore. `PL-GYH2` removed the controller's volume setter, so the app sets the volume once, in `_build_state`. A branch rebuilds the system with its volume first and then calls `resume_at`. So no learner can meet this now, but any later feature that changes the circuit volume during a run, or restores a saved run onto a different circuit, would silently create or destroy agent. That is why it is classed `science` and ranks `P1` despite being latent.
