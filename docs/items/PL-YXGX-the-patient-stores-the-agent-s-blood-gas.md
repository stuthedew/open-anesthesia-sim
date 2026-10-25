---
id: PL-YXGX
title: The patient stores the agent's blood:gas partition coefficient four times, once in each tissue group and once in the venous pool, and nothing checks that the copies agree: PatientCompartments checks only that the perfusion fractions sum to 1, so a group built or written with a different coefficient gives a patient whose blood carries the agent at two solubilities, and the solver reads the venous copy for the lung and each group's own copy for its tissue:blood ratio (found building PL-N7MM)
status: untriaged
added: 2026-10-25
---

**Problem.** The patient stores the agent's blood:gas partition coefficient four times, once in each tissue group and once in the venous pool, and nothing checks that the copies agree: PatientCompartments checks only that the perfusion fractions sum to 1, so a group built or written with a different coefficient gives a patient whose blood carries the agent at two solubilities, and the solver reads the venous copy for the lung and each group's own copy for its tissue:blood ratio (found building PL-N7MM)

**Measured at review of #1827 (2026-10-25).** On a sevoflurane system, `system.patient.venous_blood = replace(system.patient.venous_blood, blood_gas_partition_coefficient=0.1)` is accepted while the three groups keep 0.65. The solver then reads 0.1 for the lung and 0.65 for each tissue:blood ratio. Agent is still conserved, so the accounting check does not halt the run, and the curves are plausible and wrong. A tissue group written onto the patient with a different coefficient is accepted the same way, since the patient checks a new group only against the perfusion-fraction sum.

**Recommendation.** Store the coefficient once, on the patient, and have the tissue groups and the venous pool read it, per the one-source-of-truth principle in `CLAUDE.md`. Checking that four copies agree would leave a nested write, such as `patient.venous_blood.blood_gas_partition_coefficient = 0.4`, that the patient cannot see. `tests/unit/test_record_writes.py` lists the two fields as `GAP` entries naming this item, and those entries change to `ONCE` or `CHECKED` when it is done. This touches `core/tissue.py` and `core/blood.py`, which `PL-QX2G` also changes, so it should run after that item lands.
