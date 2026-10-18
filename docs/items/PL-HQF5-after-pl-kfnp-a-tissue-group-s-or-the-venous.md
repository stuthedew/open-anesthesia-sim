---
id: PL-HQF5
title: After PL-KFNP a tissue group's or the venous pool's blood flow is still settable past its patient's cardiac output through TissueGroup.set_blood_flow and VenousBloodCompartment.set_blood_flow, which nothing in src/ but PatientCompartments._update_blood_flows calls, so the record PatientCompartments.__post_init__ refuses stays reachable by a caller mypy does not read and halts only at the next step or at Reset (PL-M4M0); decide whether a compartment's blood flow stays a field of its own that a caller can set (found in PL-KFNP's design round)
priority: P1
effort: M
status: done
classes: defect, refactor, safety
feature: cardiac-output-write-consistency
touches: src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/blood.py, src/anesthesia_sim/core/patient.py, src/anesthesia_sim/core/uptake_system.py, docs/MODEL.md, tests/unit/test_patient.py, tests/unit/test_tissue.py, tests/unit/test_blood.py, tests/unit/test_compartment_primitives.py, tests/unit/test_state_capture.py, tests/unit/test_uptake_system_failure.py, tests/integration/test_controller.py, tests/integration/test_simulation_view.py, src/anesthesia_sim/core/governing_equations.py, src/anesthesia_sim/app/controller.py, tests/unit/test_concentration.py, tests/unit/test_supported_range_edges.py, tests/unit/test_supported_ranges.py, src/anesthesia_sim/app/run_view.py, .claude/rules/core-domain.md
added: 2026-10-12
closed: 2026-10-18
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
output itself. The flow is stored a second time beside both, and only checks
keep the copies equal. `PatientCompartments._compartment_not_perfused_at`
checks every copy when the patient is built and when its output is assigned.
`UptakeEquationSettings` checks the tissues' copies at each step. Between
those moments a copy can disagree. No step reads the pool's copy, as measured
above. `PL-KFNP` refuses a write to the patient's output that the
compartments do not follow. This item removes the converse, a write to a
compartment's flow that the patient's output does not follow. `PL-KFNP`'s
design round re-scoped `PL-VCP4` and `PL-J39J` to a record reached this way,
and `#1488` closed both.

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

**Sequenced after `PL-KFNP`.** [superseded 2026-10-17: `PL-KFNP` closed in `#1488`. Its build re-pointed the helpers as this paragraph describes, so nothing is left to wait on.] That item's decided build re-points the two
`_with_stale_tissue_flows` helpers and
`test_a_stale_record_met_at_step_time_is_a_failed_step_stated_in_litres_per_minute`
to reach the stale record through a tissue's `set_blood_flow`, the route this
item removes. Built first, this would leave `PL-KFNP`'s Done-when naming a
method that no longer exists, so it waits on `PL-KFNP`.

**Reproduced 2026-10-17, a third half, in `PL-KFNP`'s build.** The tissue
half halts at the next step only when the flows stop summing to the output.
The settings record does not refuse flows moved between tissues with their
sum unchanged. The measurement used `SimulationController()` at its 5.0 L/min
output. After 50 steps of 0.1 s, `vessel_rich` was set to 4.3 L/min and
`muscle` to 0.4 L/min, where the patient's fractions give 3.8 and 0.9.
`equation_settings()` then builds, and 3,000 more steps run with no failure.
At 305 s the stepped alveolar fraction is 0.010472, and the run's definition
gives 0.009889. The readouts come from the steps and the chart comes from the
definition, so the two disagree on screen. Only the readouts are computed at
a perfusion that the patient does not state. The definition still holds the
flows recorded at the start, 3.8, 0.9 and 0.3 L/min, which are the patient's
fractions times 5.0. No shipped input reaches this half, as for the other
halves. But this half puts a wrong value on screen, where the others halt the
run or leave a copy that nothing reads. The triage pass's "not safety or
science" did not see this case. `docs/MODEL.md` § "Supported input ranges"
now describes it.

**Found 2026-10-17 by the reviews of `#1488`.** The clinical and state
reviews measured six more effects of stale flows. Deriving the flows removes
each of them.

- **A setting refused on a stale record is shown as if the run goes on.** In
  the review's run, the tissue flows summed to 6.0 L/min against an output of
  5.0. A fresh gas flow change from 4.0 to 3.0 L/min was then refused and
  written back (`PL-VCP4`). The status stayed "Running", and the banner said
  that the simulation was unchanged and still running its previous setting.
  The banner named neither the refused setting nor the repair, which is a
  cardiac output change. The next tick halted the run on the same record.
  Reset halts at once on the same refusal (`PL-M4M0`). The vaporizer dial and
  the ventilation behave the same way. On a paused run the notice stays up,
  with Start enabled.
- **The refused Reset's advice now points at a figure that no step ran at.**
  The halted run's banner offers Reset, and the same record refuses Reset.
  The refused Reset's text says that the two figures must agree, and to
  change the setting that it names. The natural reading is to set the cardiac
  output to the 6.0 L/min sum. Before `PL-KFNP`, the same text pointed back to
  the original 5.0. In fact any cardiac output change repairs the run.
- **A later setting change keeps the readouts and the chart apart.** After
  flows are moved with their sum unchanged, a fresh gas flow change builds a
  record that holds the moved flows. The definition starts its new segment
  from its own state at that moment, which is the chart's state and not the
  readouts'. Sixty seconds after a change at 305 s, the readout gave F_A
  1.153% and the chart gave 1.112%. The record also dates the perfusion change
  to the setting change. In another run the steps took the moved flows at
  5 s, and the record dated them to 55 s.
- **A fork opens at the chart's state.** Before any later setting change, a
  fork opens at the chart's state and not at the readouts'. In the review's
  run the trunk's readout gave F_A 0.558%, and the branch opened at 0.551%.
  After a later setting change, the fork is refused, because the branch would
  be rebuilt from flows that the run did not hold (`_disagreements_with`).
- **Reset adopts the moved flows.** After Reset, the readouts and the chart
  agree again. They agree on a perfusion of 4.3, 0.4 and 0.3 L/min, which no
  data file states, and nothing on screen shows it.
- **A cardiac output change to the same value reverses the disagreement.**
  Once a later setting change has recorded the moved flows, the definition
  holds 4.3, 0.4 and 0.3 L/min. Setting the cardiac output to its current
  5.0 L/min then sets the compartments back to 3.8, 0.9 and 0.3 L/min.
  `_record_control_change` records nothing for an unchanged value. The steps
  and the chart then disagree the other way round.

**Recommended.** Class this item `safety`, because its third half puts a
wrong value on screen. `CLAUDE.md`'s clinical-output standard counts that as
a safety failure. A `safety` class pins the item to `P1` and voids the reason
that its `deferred-from:` line gives. So the triage pass should settle the
priority and the gate placement in the same change.

**Answered 2026-10-17: classed `safety`** (project owner, 2026-10-17,
ratified, "Agree", over leaving it a `P2` defect deferred from Gate 2). The
project owner agreed with the recommendation above at 14:30Z (09:30 CDT), in
the thread for `#1488`. The item is now `P1`, and its `deferred-from:` line is
removed. It is on v0.6.0's frozen list, under the exception that admits a
`safety` finding whenever it is made (`ROADMAP.md` § "Debt gate: the frozen
list").

**Done when.** No compartment stores a blood flow that can disagree with its
patient's cardiac output: `TissueGroup.blood_flow_l_min`,
`VenousBloodCompartment.blood_flow_l_min` and both `set_blood_flow` methods are
gone. Every flow a run, a settings record or a closed form reads is formed
from `PatientCompartments.cardiac_output_l_min` (times the tissue's
`perfusion_fraction`, and unscaled for the pool) where it is read.
`_update_blood_flows` and `_compartment_not_perfused_at` go with the copies they
kept equal, and so do the constructor's and the assignment's refusals that use
it. Whether each compartment's standalone closed form (`advance`,
`time_constant_s`) takes the flow as an argument or reads it from its patient
is the build's call. Displayed and pinned values do not move: the reference
suite passes unchanged and a run at each agent's defaults is bit-identical
before and after. The tests that reached the stale record (`PL-M4M0`'s and
`PL-KFNP`'s helpers) reach their refusal another way, such as an
`UptakeEquationSettings` built with disagreeing flows, or are retired with a
reason where the record they built can no longer exist. `docs/MODEL.md`'s
account of tissue and venous flow, and § "Supported input ranges" on the ways
a flow gets in, say so. `PL-VCP4` and `PL-J39J` closed in
`#1488`, and their tests use the helpers named above. And
`test_a_compartment_blood_flow_is_the_patients_output_and_nothing_else` in
`tests/unit/test_patient.py` pins that changing the output moves every
compartment's flow and that no write moves one alone.

**Built, 2026-10-18.** The flows are derived, not stored.
`TissueGroup.blood_flow_l_min_at(cardiac_output)` is the one place
$`Q_i = f_iQ`$ is formed, and it takes a `CardiacOutput`, so a bare `float`
is refused. Each compartment's `time_constant_s` and `advance()` take the flow
as an argument, matching $`\tau_i = V_i\lambda_{i:b}/Q_i`$. The patient's
`_update_blood_flows`, `_compartment_not_perfused_at` and
`_require_rewrite_perfused_at` are gone, so a direct assignment of the cardiac
output, a copy, `dataclasses.replace` and a pickle now move every flow with
the output. The tests that reached the stale record now reach it by writing
the tissue fractions past their guard with `object.__setattr__`, which is the
only way left to make one. `PL-VCP4`'s controller test reaches the cardiac
output's restore that way, and `PL-Z0HN`'s Done-when asks for that.

Bit-identity: three agents (sevoflurane, desflurane, isoflurane) at their
defaults, 0.1 s steps for one hour, with the cardiac output set to 3.0 L/min
at 30 minutes. The state vector at every tenth of the run matched bit for bit
(`float.hex`) between the base `88960a11` and this change.

Regression proof (`.claude/rules/test-oracles.md` rule 6). On `88960a11`,
`fat.set_blood_flow(1.0)` on the default patient was accepted and left flows
of `[3.8, 0.9, 1.0]` against a cardiac output of 5.0 L/min. The new test, run
there with `PYTHONPATH=$BASE/src python -m pytest
tests/unit/test_patient.py -k blood_flow_is_the_patients_output`, fails with
`AssertionError: assert not True ... hasattr(TissueGroup(...), 'blood_flow_l_min')`.

Two findings filed rather than fixed: `PL-XRN8` (a setting written onto the
core past `SimulationController` moves the steps but not the run's
definition) and `PL-01GY` (the refused-Reset banner names a setting that no
longer repairs the mismatch).
