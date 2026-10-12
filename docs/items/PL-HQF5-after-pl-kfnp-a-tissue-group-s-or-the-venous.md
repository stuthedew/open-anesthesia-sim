---
id: PL-HQF5
title: After PL-KFNP a tissue group's or the venous pool's blood flow is still settable past its patient's cardiac output through TissueGroup.set_blood_flow and VenousBloodCompartment.set_blood_flow, which nothing in src/ but PatientCompartments._update_blood_flows calls, so the record PatientCompartments.__post_init__ refuses stays reachable by a caller mypy does not read and halts only at the next step or at Reset (PL-M4M0); decide whether a compartment's blood flow stays a field of its own that a caller can set (found in PL-KFNP's design round)
status: untriaged
feature: cardiac-output-write-consistency
touches: src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/blood.py, src/anesthesia_sim/core/patient.py
added: 2026-10-12
---

**Problem.** After PL-KFNP a tissue group's or the venous pool's blood flow is still settable past its patient's cardiac output through TissueGroup.set_blood_flow and VenousBloodCompartment.set_blood_flow, which nothing in src/ but PatientCompartments._update_blood_flows calls, so the record PatientCompartments.__post_init__ refuses stays reachable by a caller mypy does not read and halts only at the next step or at Reset (PL-M4M0); decide whether a compartment's blood flow stays a field of its own that a caller can set (found in PL-KFNP's design round)

**Not `PL-KFNP` filed again.** `docket new` matched this to `PL-KFNP` on the
shared path and feature. `PL-KFNP` is the patient's own output field admitting
a write its compartments do not follow; this is the compartments' flow fields
admitting a write the patient's output does not follow, the door `PL-KFNP`'s
design round found either answer leaves, so the recurrence was withdrawn.
