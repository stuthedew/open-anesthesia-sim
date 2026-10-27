---
id: PL-DQL9
title: The uptake matrix takes the pulmonary blood:gas coefficient from the venous pool and each tissue's rate from that tissue's own blood:gas coefficient, and nothing requires the four to agree, so a mismatch makes the matrix create agent and halts the run as an AgentSimulationValidationError that blames the numerics for an inconsistent parameter set
priority: P1
effort: M
status: done
classes: defect, science, safety
feature: replay-findings
touches: src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/core/patient.py, src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/blood.py, docs/MODEL.md, tests/unit/test_patient.py, tests/unit/test_tissue.py, tests/unit/test_blood.py, tests/unit/test_record_writes.py, tests/unit/test_state_capture.py, tests/unit/test_numerical_envelope.py, tests/unit/test_numerical_envelope_sweep.py, tests/unit/test_compartment_primitives.py, tests/unit/test_concentration.py, tests/unit/test_uptake_system_failure.py, tests/integration/test_controller.py, tests/integration/test_simulation_view.py
added: 2026-10-25
closed: 2026-10-27
pr: 1881
payoff: the model can no longer hold two blood:gas coefficients, so a mismatched pool or tissue group can neither halt a run with an error that blames the numerics nor run silently on uptake curves that are wrong
verify: grep -q 'def test_a_patient_holds_one_blood_gas_coefficient' tests/unit/test_patient.py
---

**Problem.** `AgentUptakeSystem.equation_settings` (`src/anesthesia_sim/core/uptake_system.py`) passes only `venous_blood.blood_gas_partition_coefficient` for the blood:gas term. Each tissue row uses `tissue.tissue_blood_partition_coefficient`, which divides by that tissue's own blood:gas coefficient. Neither `PatientCompartments` nor `UptakeEquationSettings` checks that the coefficients agree. Reproduced on main: raising the fat group's blood:gas coefficient by 1% (0.65 to 0.6565) halts sevoflurane on step 4 with `AgentSimulationValidationError`, relative error 3.8e-9.

**Why it matters.** The shipped files all hold 0.65, so no run fails today. A future agent or patient file with differing values would halt every run with an error that points at numerical accounting. A replaced venous pool with a different value fails worse: the run continues and its uptake curves are wrong, as the fold-in below records. The settings record already refuses tissue flows that do not sum to cardiac output, and this relation belongs beside that check. The alternative is to carry one blood:gas coefficient.

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

**Done when.** A settings record whose tissue rows and pulmonary term use different blood:gas coefficients is refused when it is built, with a `SimulationConfigurationError` naming the coefficients, or the model carries one blood:gas coefficient. `tests/unit/test_patient.py` has `test_a_patient_holds_one_blood_gas_coefficient`, which shows that the groups store no copy, the pool's copy is written once, and a replaced pool at another coefficient is refused. The first route's test, `test_settings_with_disagreeing_blood_gas_coefficients_are_refused`, no longer applies: the settings record now receives one blood:gas coefficient and each tissue:blood quotient formed from it, so there is no pair left in it to disagree (rewritten on 2026-10-27, when the second route was built).

**Found by.** `PL-TBQS` reviewer replay on #376, findings r02 F1 and r06 F1. Checked against main on 2026-10-25 with `scripts/c_core376.py Q`.

**Folded in from `PL-YXGX` on 2026-10-26.** `PL-YXGX` filed the same four
copies from the patient's side, while building `PL-N7MM`. It adds two facts.
First, a `PatientCompartments` built directly with the fat group at blood:gas
2.0 and the rest at 0.65 is accepted, and so is a later write of 3.0 to one
group's `blood_gas_partition_coefficient`. So a check at construction alone
would still let a write make the copies disagree. Second, a mismatch does not
always halt the run. On a sevoflurane system, replacing the venous pool with
one at blood:gas 0.1, while the three groups keep 0.65, is accepted (measured
at review of `#1827`, 2026-10-25). The solver then reads 0.1 for the lung and
0.65 for each tissue:blood ratio. Agent is still conserved, so the accounting
check never fires, and the run gives uptake curves that look plausible and are
wrong. That silent case is the more dangerous one, and a check that only turns
the halt into a clearer error does not reach it.

`CLAUDE.md`'s one-source-of-truth principle says to fix a second copy by
replacing it with a read of its home. `PL-YXGX` recorded that home on
2026-10-25, answering the project owner's question: the agent record.
`data/agents/<agent>.json` stores the coefficient, and `parse_agent_parameters()`
reads it into `AgentParameters.blood_gas_partition_coefficient`.
`PatientCompartments.from_parameters()` then copies it into the four
compartments. `PL-YXGX` considered storing it once on the patient and replaced
that choice. **Recommended:** take the Done-when's second route. The tissue
groups and the venous pool stop storing the coefficient. Each tissue method
takes it as an argument, as the sizing paragraph above describes, and the
caller reads it from the `AgentParameters` the system was built for. The
tissue:blood ratio is then derived by one formula, not by both `AgentParameters`
and `TissueGroup`. The test for this route shows that a replaced venous pool or
tissue group cannot carry a different blood:gas coefficient.
