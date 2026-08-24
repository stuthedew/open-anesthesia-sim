---
id: PL-019
title: Remove `BreathingCircuit`'s agent-unaware delivered-concentration default
priority: P3
effort: S
status: ready
classes: refactor
touches: src/anesthesia_sim/core/circuit.py, tests/reference/test_multi_agent.py, tests/reference/test_sevo_patient.py, tests/unit/test_circuit.py
added: 2026-08-24
---

**Problem.** `BreathingCircuit.delivered_concentration_fraction` defaults to
`0.08`, a sevoflurane-shaped literal on a class that knows nothing about
agents. Since PL-015 the circuit also carries a vaporizer maximum, so
`BreathingCircuit(max_delivered_concentration_fraction=0.05)` raises unless
the caller remembers to pass a deliverable concentration too.
**Why it matters.** Not a defect: the raise is the intended fail-closed
behavior, and every agent-aware path goes through
`RespiratorySystem.for_agent()`, which sets both values from the data file.
It is a rough edge for a direct core caller, and one more agent-unaware
literal of the kind PL-017 removed from the controller.
**Where.** `core/circuit.py`, `tests/unit/test_circuit.py`,
`tests/reference/test_multi_agent.py`, `tests/reference/test_sevo_patient.py`.
**First step.** Decide the default: `0.0` (vaporizer off, always valid,
but changes what a bare `BreathingCircuit()` simulates and so touches the
reference tests that rely on the 8% start) or no default at all.
**Done when.** Constructing a circuit with a vaporizer maximum below 8%
does not require remembering a second argument, and the reference tests
state their delivered concentration explicitly.
