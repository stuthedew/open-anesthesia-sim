---
id: PL-DQL9
title: The uptake matrix takes the pulmonary blood:gas coefficient from the venous pool and each tissue's rate from that tissue's own blood:gas coefficient, and nothing requires the four to agree, so a mismatch makes the matrix create agent and halts the run as an AgentSimulationValidationError that blames the numerics for an inconsistent parameter set
priority: P1
effort: S
status: ready
classes: defect, science, safety
feature: replay-findings
touches: src/anesthesia_sim/core/governing_equations.py, src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/core/patient.py, tests/unit/test_governing_equations.py
added: 2026-10-25
payoff: an inconsistent parameter file is refused by name when it loads, instead of halting every run with an error that blames the numerics
verify: grep -q 'def test_settings_with_disagreeing_blood_gas_coefficients_are_refused' tests/unit/test_governing_equations.py
---

**Problem.** `AgentUptakeSystem.equation_settings` (`src/anesthesia_sim/core/uptake_system.py`) passes only `venous_blood.blood_gas_partition_coefficient` for the blood:gas term. Each tissue row uses `tissue.tissue_blood_partition_coefficient`, which divides by that tissue's own blood:gas coefficient. Neither `PatientCompartments` nor `UptakeEquationSettings` checks that the coefficients agree. Reproduced on main: raising the fat group's blood:gas coefficient by 1% (0.65 to 0.6565) halts sevoflurane on step 4 with `AgentSimulationValidationError`, relative error 3.8e-9.

**Why it matters.** The shipped files all hold 0.65, so no run fails today. A future agent or patient file with differing values would halt every run with an error that points at numerical accounting. The settings record already refuses tissue flows that do not sum to cardiac output, and this relation belongs beside that check. The alternative is to carry one blood:gas coefficient.

**Done when.** A settings record whose tissue rows and pulmonary term use different blood:gas coefficients is refused when it is built, with a `SimulationConfigurationError` naming the coefficients, or the model carries one blood:gas coefficient. `tests/unit/test_governing_equations.py` has `test_settings_with_disagreeing_blood_gas_coefficients_are_refused`.

**Found by.** `PL-TBQS` reviewer replay on #376, findings r02 F1 and r06 F1. Checked against main on 2026-10-25 with `scripts/c_core376.py Q`.
