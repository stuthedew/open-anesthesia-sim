---
id: PL-YXGX
title: The patient stores the agent's blood:gas partition coefficient four times, once in each tissue group and once in the venous pool, and nothing checks that the copies agree: PatientCompartments checks only that the perfusion fractions sum to 1, so a group built or written with a different coefficient gives a patient whose blood carries the agent at two solubilities, and the solver reads the venous copy for the lung and each group's own copy for its tissue:blood ratio (found building PL-N7MM)
status: untriaged
feature: one-source-of-truth
added: 2026-10-25
---

**Problem.** The patient stores the agent's blood:gas partition coefficient four times, once in each tissue group and once in the venous pool, and nothing checks that the copies agree: PatientCompartments checks only that the perfusion fractions sum to 1, so a group built or written with a different coefficient gives a patient whose blood carries the agent at two solubilities, and the solver reads the venous copy for the lung and each group's own copy for its tissue:blood ratio (found building PL-N7MM)

**Measured at review of #1827 (2026-10-25).** On a sevoflurane system, `system.patient.venous_blood = replace(system.patient.venous_blood, blood_gas_partition_coefficient=0.1)` is accepted while the three groups keep 0.65. The solver then reads 0.1 for the lung and 0.65 for each tissue:blood ratio. Agent is still conserved, so the accounting check does not halt the run, and the curves are plausible and wrong. A tissue group written onto the patient with a different coefficient is accepted the same way, since the patient checks a new group only against the perfusion-fraction sum.

**Where the coefficient should live (project owner's question, 2026-10-25).** The project owner asked whether this belongs to the one-source-of-truth feature, and whether the coefficient should live in the agent's own record and be read from there everywhere. Both answers are yes. The earlier recommendation in this item, to store it once on the patient, picked the wrong home and is replaced here.

The coefficient already has one source. `src/anesthesia_sim/data/agents/<agent>.json` stores it (0.65 for sevoflurane), and `parse_agent_parameters()` in `core/parameters.py` reads it into `AgentParameters.blood_gas_partition_coefficient`. The four copies are made afterwards, at one moment: `PatientCompartments.from_parameters()` in `core/patient.py` copies the agent's value into each of the three `TissueGroup`s and into the `VenousBloodCompartment`. From then on the solver reads two of the copies. `AgentUptakeSystem` in `core/uptake_system.py` takes the lung's blood:gas from the venous pool, and each tissue group divides its own tissue:gas by its own blood:gas to get its tissue:blood ratio (`core/tissue.py`).

**Recommendation.** Keep the agent record as the only home, and remove the runtime copies:

1. The tissue groups and the venous pool stop storing `blood_gas_partition_coefficient`. Whatever needs blood:gas reads it from the `AgentParameters` that the system was built for. The patient or the system holds that record, and the record is already validated once at parse.
2. Tissue:blood is derived once. `AgentParameters` already derives the three tissue:blood ratios as properties, and only `tests/unit/test_parameters.py` reads them. `TissueGroup.tissue_blood_partition_coefficient` derives the same ratio a second time. One of the two should go, so that the ratio has one formula.
3. A swap of the agent then means building a new system, which `AgentUptakeSystem` already requires for its parts (`PL-N7MM`).

Checking that four copies agree was considered and rejected. It would leave a nested write, such as `patient.venous_blood.blood_gas_partition_coefficient = 0.4`, that the patient cannot see, and it keeps the copies that cause the problem.

**What would change this.** Blood:gas is not a fixed property of the agent alone. Lerman et al. 1984 (Anesthesiology 61:139-43, doi:10.1097/00000542-198408000-00005, abstract read through PubMed 2026-10-25) measured isoflurane at 1.19 in newborns and 1.46 in adults aged 20 to 40, and found it correlated with serum albumin and triglycerides. Esper et al. 2015, which `data/agents/sevoflurane.json` already cites, found no significant correlation with age, body mass index, hemoglobin or hematocrit in adults aged 19 to 86. So a patient-specific blood:gas would matter mainly if the simulator models children. If it ever does, that value is a patient covariate applied to the agent's reference value. One function computes it once from the agent record and the patient record, and it is not stored again in each compartment. The recommendation above still holds.

`tests/unit/test_record_writes.py` lists `patient.venous_blood` and `TissueGroup.blood_gas_partition_coefficient` as `GAP` entries naming this item. Once the copies are removed, those entries are deleted, or they change to `ONCE` where a field remains. This touches `core/tissue.py` and `core/blood.py`, which `PL-QX2G` (a declared numerical range for volumes and partition coefficients) also changes, so it should run after that item lands.
