---
id: PL-Z0T3
title: dataclasses.replace() on PatientCompartments rewrites the tissue and venous flows of the original it shares those sub-objects with, because __post_init__ calls _update_blood_flows on them: a running system is left perfusing at the twin's cardiac output while its snapshot reports the old one, until the next step's tissue-sum check halts the run (found reviewing #1350)
priority: P1
effort: S
status: done
classes: safety, defect
touches: src/anesthesia_sim/core/patient.py, tests/unit/test_patient.py, tests/unit/test_supported_ranges.py, tests/unit/test_supported_range_edges.py
added: 2026-10-04
closed: 2026-10-05
pr: 1372
payoff: copying a patient can no longer rewrite a running patient's blood flow, so a run is never failed, or shown a setting as refused while holding it, because of a copy made elsewhere
verify: grep -q 'def test_replace_leaves_the_original_perfused_at_its_own_output' tests/unit/test_patient.py && ! grep -q 'stored_on != "patient"' tests/unit/test_supported_ranges.py
---

**Problem.** dataclasses.replace() on PatientCompartments rewrites the tissue and venous flows of the original it shares those sub-objects with, because __post_init__ calls _update_blood_flows on them: a running system is left perfusing at the twin's cardiac output while its snapshot reports the old one, until the next step's tissue-sum check halts the run (found reviewing #1350)

**Reproduced 2026-10-04** on `main` at `8f24fe78`:
`uv run python -c "from dataclasses import replace; from anesthesia_sim.core.uptake_system import AgentUptakeSystem; from anesthesia_sim.core.supported_ranges import CardiacOutput; from anesthesia_sim.core.simulation_step import SimulationStep; s = AgentUptakeSystem.default(); p = s.patient; replace(p, cardiac_output_l_min=CardiacOutput(10.0)); print(p.cardiac_output_l_min, [round(t.blood_flow_l_min, 2) for t in p.tissues], p.venous_blood.blood_flow_l_min); s.advance(SimulationStep(0.1))"`
printed `5.0 [7.6, 1.8, 0.6] 10.0`, then raised `SimulationNumericalError`
("the simulation step of 0.1 s could not be completed and was rolled back")
over the tissue-sum check's refusal ("the tissue groups are perfused
at 0.16666666666666666 L/s in total but cardiac output is 0.08333333333333333
L/s"). The original still records 5 L/min while its three tissue groups and
its venous pool are perfused at the copy's 10 L/min, and its next step is
refused as a numerical failure though nothing numerical failed. `#1354` does
not touch `patient.py`, `tissue.py`, `blood.py` or
`tests/unit/test_patient.py`, so the fault survives it.

**Why it matters.** Nothing in `src/` calls `replace` or `copy` on a
compartment, and a branch builds a new system from the data files rather than
copying its parent's, so no route reaches this from the interface. What
reaches it is a caller holding the patient, such as a notebook comparing two
cardiac outputs, a test or a later refactor, and what it costs that caller is
a system whose own record of its cardiac output no longer matches the flows
its equations read. No wrong value is displayed: the snapshot carries cardiac
output and no tissue flow, and the tissue-sum check refuses the step before
any value is computed from the rewritten flows. But the refusal blames the
numerics, and a setting changed through the controller after the copy fares
worse: on the same `main`, `set_fresh_gas_flow(FreshGasFlow(2.0))` on the
`SimulationController` wrote the circuit and then raised
`SimulationConfigurationError` from the same check while recording the
change, which the view shows as a refused setting, though the circuit and the
readout already held 2.0 L/min and the run's definition and timeline did not.
The cause is `__post_init__` writing each tissue's flow into sub-objects it
was handed; `.claude/rules/core-domain.md` puts the relation between those
flows and cardiac output on the record holding them, which can check it there
without writing into objects another record may share.
`test_a_bare_float_is_refused_wherever_a_flow_is_stored` in
`tests/unit/test_supported_ranges.py` already steps around this item: it
skips `replace` on the patient and cites `PL-Z0T3`.

**Done when.** After `replace(patient, cardiac_output_l_min=CardiacOutput(10.0))`
on a patient at 5 L/min, whether the copy is refused or built with flows of
its own, the original's tissue flows are still their perfusion fractions of
its 5 L/min, its venous flow is still 5 L/min and its system still steps; the
`stored_on != "patient"` exclusion in
`test_a_bare_float_is_refused_wherever_a_flow_is_stored`, and the comment
citing this item, are gone, so that test drives `replace` on the patient as on
the other two (it would pass today, since `require_cardiac_output` refuses a
bare `float` before any flow is written); and a test in
`tests/unit/test_patient.py` named
`test_replace_leaves_the_original_perfused_at_its_own_output` pins it.

**Fixed 2026-10-05.** `PatientCompartments.__post_init__` checks the relation
`docs/MODEL.md` § "Tissue groups" defines - each tissue group perfused at its
fraction of cardiac output, the venous pool at the whole of it - and writes
nothing, so a copy no longer reaches into the compartments it shares with the
original. `from_parameters` builds each compartment at its flow, and
`set_cardiac_output` still moves them together; both compute the product the
check does, so it compares exactly. The reproduction above now stops at the
copy, refused with `SimulationConfigurationError` naming the compartment, its
flow and the flow this patient's output gives it; the original keeps
`5.0 [3.8, 0.9, 0.3] 5.0` and steps. The refusal names `copy.deepcopy` and
`set_cardiac_output` as the way to a copy at another output, and
`test_a_deep_copy_takes_another_output_without_the_original` holds that route
to it; `test_rejects_a_venous_pool_perfused_at_another_output` covers the
venous branch, and the exclusion in
`test_a_bare_float_is_refused_wherever_a_flow_is_stored` is gone.

Refusing the copy was chosen over building it with compartments of its own (a
defensive copy in the constructor), which the Done when also allows. A copy
taken inside the constructor would leave a caller holding the tissue it passed
in reading one the patient no longer steps - a plausible zero where uptake
should be - and would be the only constructor in `core/` that copies what it
is handed. What stays is ordinary shallow-copy behaviour: a `replace` keeping
the output shares the original's compartments, so setting or stepping that
copy moves the original too, as with any mutable field `replace` copies. That
is Python's documented semantics rather than a defect of this class, and the
refusal points at the copy that has none.

`tests/unit/test_supported_range_edges.py` built its patient at each drawn
cardiac output with that same `replace`, and was refused once the check
landed; it now sets the output on a patient of its own (`_patient_at`, beside
the settings record's `_equation_settings_at`), so it joins `touches`.
