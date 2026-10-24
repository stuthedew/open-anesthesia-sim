---
id: PL-QG52
title: BreathingCircuit.restore_state writes back a captured fraction rather than an amount, so a restore after the circuit volume changed creates or destroys agent and the next step fails accounting
status: untriaged
feature: replay-findings
added: 2026-10-24
---

**Problem.** BreathingCircuit.restore_state writes back a captured fraction rather than an amount, so a restore after the circuit volume changed creates or destroys agent and the next step fails accounting

**Evidence.** Raised on `#204` by the panel's PK/PD and numerics reviewers and by both generalist runs, and reproduced by the blind checker at that merge: on the test `test_restoring_the_system_cannot_raise_on_a_state_a_run_produced`, a restore after a 6 L to 0.5 L volume change left 1.18e-4 L of the 1.33e-3 L stored, accounting failed, and the next `advance()` raised `AgentSimulationValidationError`. On `origin/main` on 2026-10-24, `BreathingCircuitState` still holds `inspired_partial_pressure_fraction`, and `BreathingCircuit.restore_state` shows no check of the volume. It was not re-run on `main`.

**Why it matters.** Every other compartment's captured state holds an amount, so a restore conserves agent. The circuit's holds a fraction, so a restore across a volume change silently creates or destroys agent, and the next step takes the blame. `advance()` cannot reach this today, but branches, rewinds and saved runs reuse capture and restore.

**Done when.** The behaviour is reproduced on `main`, and the circuit either captures its amount or refuses a restore onto a different volume. The test asserts mass balance after the restore.
