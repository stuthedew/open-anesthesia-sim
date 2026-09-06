---
id: PL-74R0
title: core/ still holds four compartment-level advance methods that the coupled step no longer calls
status: untriaged
feature: numerical-domain
added: 2026-09-06
---

**Problem.** `PL-GS5X` replaced the five composed sub-steps with one exact
propagation, and `PL-LKRP` closed with it by deleting
`AlveolarCompartment.apply_blood_uptake`, whose only production caller was the
fifth of them. Four more mutators are in the same position and were left:

| Method | Production callers after `PL-GS5X` |
| --- | --- |
| `BreathingCircuit.advance_fresh_gas` | `BreathingCircuit.advance` and nothing else |
| `BreathingCircuit.advance` | none |
| `TissueGroup.advance` | `PatientCompartments.advance` and nothing else |
| `VenousBloodCompartment.advance` | `PatientCompartments.advance` and nothing else |
| `PatientCompartments.advance` | none |

Each advances one compartment against a fixed input, which was what a sub-step
of the split did. The coupled model no longer has such a thing: every rate is
evaluated from one state vector, and a caller who reached for
`tissue.advance()` would get a number that solves nothing in particular.

**Why they were not simply deleted with the rest.** Two reasons, and they point
opposite ways.

`BreathingCircuit.advance_fresh_gas` has a claim on staying:
`docs/MODEL.md` § "Breathing circuit" states its closed form as a documented
reduction of the model ("For constant input and no patient connection, the
exact v0.0.2 solution remains: ..."), and § "Required tests" requires the
preserved circuit reference tests that exercise it to keep passing.
`tests/reference/test_circuit_wash_in.py` is that gate.

The other four have no such claim - but each is covered by unit tests that
verify its own time constant against the analytic solution
(`tests/unit/test_tissue.py`, `test_blood.py`, `test_patient.py`), and deleting
them deletes that verification rather than moving it. Reaching the same
properties through the coupled system means zeroing the other flows and reading
one row, which is a weaker and less direct test than the one it would replace.

**The decision this needs.** Three options, and the middle one is probably
right:

1. Delete all four with their tests, on the ground that a public mutator that
   can advance a compartment outside the governing equations is a way to reach
   a state that solves nothing.
2. Keep them as documented compartment primitives, and say so in each
   docstring - that they are the single-compartment closed forms, not how a run
   advances - so a reader cannot mistake one for the model.
3. Keep the two whose closed forms `docs/MODEL.md` states and delete
   `PatientCompartments.advance`, which is the only one of the five that is a
   *composition* rather than one compartment's own solution.

**Where.** `core/circuit.py`, `core/tissue.py`, `core/blood.py`,
`core/patient.py`; `tests/unit/test_tissue.py`, `test_blood.py`,
`test_patient.py`, `test_circuit.py`; `tests/reference/test_circuit_wash_in.py`.
`PL-9SH6` renames across the same files and should be sequenced with whichever
answer is taken.

**Found.** Closing out `PL-GS5X`, 2026-09-06.
