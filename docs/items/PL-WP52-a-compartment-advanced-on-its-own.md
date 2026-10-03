---
id: PL-WP52
title: A compartment advanced on its own (BreathingCircuit.advance_fresh_gas, TissueGroup.advance, the blood compartment's advance) accepts any positive finite step, so it takes steps below MINIMUM_SIMULATION_STEP_S, where rounding is a growing share of what a step changes (measured on the coupled system, PL-YZ17); only AgentUptakeSystem.advance refuses them, and whether a compartment should too is undecided
status: untriaged
feature: numerical-domain
added: 2026-10-03
---

**Problem.** A compartment advanced on its own (BreathingCircuit.advance_fresh_gas, TissueGroup.advance, the blood compartment's advance) accepts any positive finite step, so it takes steps below MINIMUM_SIMULATION_STEP_S, where rounding is a growing share of what a step changes (measured on the coupled system, PL-YZ17); only AgentUptakeSystem.advance refuses them, and whether a compartment should too is undecided

**Found 2026-10-03** while declaring the floor in `PL-YZ17`. The floor
binds the run: `require_supported_simulation_step` is called by
`AgentUptakeSystem.advance()` and `SimulationState`, and a compartment is only
ever stepped at a run's step by the former, after the guard. A compartment
stepped on its own - `BreathingCircuit.advance_fresh_gas`,
`TissueGroup.advance`, the blood compartment's `advance` - checks only
`require_positive_finite`, so it takes 1e-14 s without complaint. The rounding
mechanism `PL-YZ17` measured on the coupled system (a third of the change
wrong at 1e-14 s) is not specific to coupling, so a compartment stepped that
finely presumably shares it; that is inferred, not measured.

The case for leaving it: a compartment stepped alone is a building block whose
caller owns the step, the way `docs/MODEL.md` § "Supported input ranges" argues
the ceiling does not bind one, and no test steps one alone below the 0.1 s
`tests/reference/test_circuit_wash_in.py` uses. The case for the guard: the compartments are public, and a notebook
stepping one finely gets a plausible number. Measure a compartment alone first;
the decision follows from whether it shares the coupled system's growth.
