---
id: PL-HQF5
title: After PL-KFNP a tissue group's or the venous pool's blood flow is still settable past its patient's cardiac output through TissueGroup.set_blood_flow and VenousBloodCompartment.set_blood_flow, which nothing in src/ but PatientCompartments._update_blood_flows calls, so the record PatientCompartments.__post_init__ refuses stays reachable by a caller mypy does not read and halts only at the next step or at Reset (PL-M4M0); decide whether a compartment's blood flow stays a field of its own that a caller can set (found in PL-KFNP's design round)
priority: P2
effort: M
status: blocked
classes: defect, refactor
feature: cardiac-output-write-consistency
touches: src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/blood.py, src/anesthesia_sim/core/patient.py, src/anesthesia_sim/core/uptake_system.py, docs/MODEL.md, tests/unit/test_patient.py, tests/unit/test_tissue.py, tests/unit/test_blood.py, tests/unit/test_compartment_primitives.py, tests/unit/test_state_capture.py, tests/unit/test_uptake_system_failure.py, tests/integration/test_controller.py, tests/integration/test_simulation_view.py
blocked-by: PL-KFNP
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-12
payoff: a tissue's or the venous pool's blood flow can no longer disagree with the patient's cardiac output, so no record the core refuses, and no silent second copy of the output, can be built
verify: grep -q 'def test_a_compartment_blood_flow_is_the_patients_output_and_nothing_else' tests/unit/test_patient.py
---

**Problem.** After PL-KFNP a tissue group's or the venous pool's blood flow is still settable past its patient's cardiac output through TissueGroup.set_blood_flow and VenousBloodCompartment.set_blood_flow, which nothing in src/ but PatientCompartments._update_blood_flows calls, so the record PatientCompartments.__post_init__ refuses stays reachable by a caller mypy does not read and halts only at the next step or at Reset (PL-M4M0); decide whether a compartment's blood flow stays a field of its own that a caller can set (found in PL-KFNP's design round)

**Not `PL-KFNP` filed again.** `docket new` matched this to `PL-KFNP` on the
shared path and feature. `PL-KFNP` is the patient's own output field admitting
a write its compartments do not follow; this is the compartments' flow fields
admitting a write the patient's output does not follow, the door `PL-KFNP`'s
design round found either answer leaves, so the recurrence was withdrawn.

**Reproduced 2026-10-17** on this tree (`b9b3c812`), on
`AgentUptakeSystem.for_agent("sevoflurane")` at its 5.0 L/min output. Two
halves, and they fail differently:

- **The tissue half halts at the next step, as the title says.**
  `patient.tissues[0].set_blood_flow(7.6)` (twice its 3.8) is accepted, and
  `equation_settings()` then refuses with "the tissue groups are perfused at
  8.8 L/min in total but cardiac output is 5.0 L/min".
- **The venous half halts nowhere, which the title does not say.**
  `patient.venous_blood.set_blood_flow(99.0)` is accepted,
  `equation_settings()` builds, and 600 steps of 0.1 s at a 2% dial run to
  completion with the pool holding 99.0 L/min (and a `time_constant_s` of
  0.74 s) beside a cardiac output of 5.0. The run is right, because
  `UptakeEquationSettings` reads the patient's output and never the pool's
  flow; the pool's field is a second copy of the cardiac output that the run
  does not read and nothing keeps equal to it.

Nothing under `src/` calls either `set_blood_flow` but
`PatientCompartments._update_blood_flows`, no control reaches one, and no
display reads a compartment's flow or time constant (`git grep` over
`src/anesthesia_sim/app/`), so no shipped input reaches either half; that is
what sets the band below `PL-KFNP`'s.

**Why it matters.** A compartment's blood flow is not a fact of its own: it is
the patient's cardiac output times the tissue's `perfusion_fraction`, which the
same `TissueGroup` already stores, and for the venous pool it is the cardiac
output itself. Stored a second time beside both, it is held equal only by
`PatientCompartments.__post_init__`'s `_require_perfused_at` at construction and
by `UptakeEquationSettings` at each step for the tissues, and for the pool by
nothing after construction, as measured above. `PL-KFNP` closes the patient's
side of the door; this is the compartments' side, and while it stands
`PL-VCP4` and `PL-J39J` stay reachable through it (`PL-KFNP`'s design round
re-scoped both to a record reached this way).

**Whose decision, and the answer.** The title asks whether a compartment's
blood flow stays a field of its own that a caller can set. That is not the
owner's question on rule 14's test: no learner sees a compartment's flow, the
project's purpose does not turn on it, and the safety outcome is the same or
better under every answer that closes the door. `PL-KFNP`'s own answer records
the owner asking why that sibling question was theirs at all, and `PL-JZV8` was
filed so the next one is not labelled so. Of the three answers, one is clearly
correct. Keeping the field and recording the door leaves a second copy of the
cardiac output that disagrees silently on the venous side. Keeping it but
making the setter private still leaves a direct write to the field, which
`PL-19Y0` holds to sign and finiteness only. Deriving it removes the second
copy, so the record `__post_init__` refuses cannot be built. That is
`CLAUDE.md`'s one-source-of-truth principle ("a hard coding principle",
project owner, 2026-10-12) and `.claude/rules/expert-review.md`'s preference
for interfaces that prevent an error over ones that warn after it. Counted per
the same file's "what undoing it would cost": about 40 references to a
compartment's flow across ten test files, plus seven in each of `tissue.py`
and `blood.py`, ten in `patient.py` and two in `uptake_system.py`, and each
test added before this lands is one more to re-point. So it is decided here:
derive it.

**Sequenced after `PL-KFNP`.** That item's decided build re-points the two
`_with_stale_tissue_flows` helpers and
`test_a_stale_record_met_at_step_time_is_a_failed_step_stated_in_litres_per_minute`
to reach the stale record through a tissue's `set_blood_flow`, the route this
item removes. Built first, this would leave `PL-KFNP`'s Done-when naming a
method that no longer exists, so it waits on `PL-KFNP`.

**Done when.** No compartment stores a blood flow that can disagree with its
patient's cardiac output: `TissueGroup.blood_flow_l_min`,
`VenousBloodCompartment.blood_flow_l_min` and both `set_blood_flow` methods are
gone. Every flow a run, a settings record or a closed form reads is formed
from `PatientCompartments.cardiac_output_l_min` (times the tissue's
`perfusion_fraction`, and unscaled for the pool) where it is read.
`_update_blood_flows` and `_require_perfused_at` go with the copies they kept
equal. Whether each compartment's standalone closed form (`advance`,
`time_constant_s`) takes the flow as an argument or reads it from its patient
is the build's call. Displayed and pinned values do not move: the reference
suite passes unchanged and a run at each agent's defaults is bit-identical
before and after. The tests that reached the stale record (`PL-M4M0`'s and
`PL-KFNP`'s helpers) reach their refusal another way, such as an
`UptakeEquationSettings` built with disagreeing flows, or are retired with a
reason where the record they built can no longer exist. `docs/MODEL.md`'s
account of tissue and venous flow, and § "Supported input ranges" on the ways
a flow gets in, say so. `PL-VCP4` and `PL-J39J` are re-read against the result
and closed or dropped where their premise has gone. And
`test_a_compartment_blood_flow_is_the_patients_output_and_nothing_else` in
`tests/unit/test_patient.py` pins that changing the output moves every
compartment's flow and that no write moves one alone.
