---
id: PL-DQL9
title: The uptake matrix takes the pulmonary blood:gas coefficient from the venous pool and each tissue's rate from that tissue's own blood:gas coefficient, and nothing requires the four to agree, so a mismatch makes the matrix create agent and halts the run as an AgentSimulationValidationError that blames the numerics for an inconsistent parameter set
priority: P1
effort: M
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

**Sized on 2026-10-26 (#1864): the one-coefficient route is M, not S.** A
tissue group uses its blood:gas copy in four places: its tissue:blood
coefficient, `time_constant_s`, its standalone `advance`, and the envelope
check on a write of either coefficient. Removing the copy means passing the
blood's coefficient into those methods, as `blood_flow_l_min_at` takes the
cardiac output since `PL-HQF5`. That changes about 35 call sites in the tests.
The quotient check then moves to `PatientCompartments`, at build and when a
tissue group or the venous pool is replaced. A later direct write of the venous
pool's coefficient is refused when the settings record next forms each
tissue:blood quotient. Yielded from batch 5 so that it lands as its own pull
request, after `#1845` (which edits this brief) merges.

**Done when.** A settings record whose tissue rows and pulmonary term use different blood:gas coefficients is refused when it is built, with a `SimulationConfigurationError` naming the coefficients, or the model carries one blood:gas coefficient. `tests/unit/test_governing_equations.py` has `test_settings_with_disagreeing_blood_gas_coefficients_are_refused`.

**Found by.** `PL-TBQS` reviewer replay on #376, findings r02 F1 and r06 F1. Checked against main on 2026-10-25 with `scripts/c_core376.py Q`.

**Folded in from `PL-YXGX` on 2026-10-26.** `PL-YXGX` filed the same four
copies from the patient's side, while building `PL-N7MM`. It adds two facts.
First, a `PatientCompartments` built directly with the fat group at blood:gas
2.0 and the rest at 0.65 is accepted, and so is a later write of 3.0 to one
group's `blood_gas_partition_coefficient`. So a check at construction alone
would still let a write make the copies disagree. Second, `CLAUDE.md`'s
one-source-of-truth principle says to fix a second copy by replacing it with a
read of its home. **Recommended:** take the Done-when's second route, so the
patient carries one blood:gas coefficient and each tissue group reads it.
