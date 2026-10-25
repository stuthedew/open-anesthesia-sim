---
id: PL-YXGX
title: The patient stores the agent's blood:gas partition coefficient four times, once in each tissue group and once in the venous pool, and nothing checks that the copies agree: PatientCompartments checks only that the perfusion fractions sum to 1, so a group built or written with a different coefficient gives a patient whose blood carries the agent at two solubilities, and the solver reads the venous copy for the lung and each group's own copy for its tissue:blood ratio (found building PL-N7MM)
status: untriaged
added: 2026-10-25
---

**Problem.** The patient stores the agent's blood:gas partition coefficient four times, once in each tissue group and once in the venous pool, and nothing checks that the copies agree: PatientCompartments checks only that the perfusion fractions sum to 1, so a group built or written with a different coefficient gives a patient whose blood carries the agent at two solubilities, and the solver reads the venous copy for the lung and each group's own copy for its tissue:blood ratio (found building PL-N7MM)
