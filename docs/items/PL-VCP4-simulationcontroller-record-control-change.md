---
id: PL-VCP4
title: SimulationController._record_control_change builds the settings record after the setter has written, so on a run whose tissue flows no longer sum to the cardiac output every setting but the cardiac output is half applied: the compartment holds the new value and the dial reads it, the definition's open segment and the timeline keep the old one, and the banner says the simulation is unchanged and still running its previous setting (found reviewing PL-M4M0)
priority: P1
effort: S
status: ready
classes: safety, defect
feature: cardiac-output-write-consistency
touches: src/anesthesia_sim/app/controller.py, tests/integration/test_controller.py
added: 2026-10-11
payoff: a setting the core cannot record leaves its compartment, the run's definition and the timeline on the previous setting, so the banner's word that the simulation is unchanged is true
verify: grep -q 'def test_a_setting_the_record_refuses_leaves_the_run_on_its_previous_setting' tests/integration/test_controller.py
recurrences: 2026-10-12 PL-DTJQ
---

**Problem.** SimulationController._record_control_change builds the settings record after the setter has written, so on a run whose tissue flows no longer sum to the cardiac output every setting but the cardiac output is half applied: the compartment holds the new value and the dial reads it, the definition's open segment and the timeline keep the old one, and the banner says the simulation is unchanged and still running its previous setting (found reviewing PL-M4M0)

**Reproduced 2026-10-11** on `claude/pl-m4m0-refused-reset-halt-ez4g6z` at
the `PL-M4M0` fold, controller and view alike: start a run, advance fifty
steps, write `CardiacOutput(6.0)` onto
`controller._state.uptake_system.patient.cardiac_output_l_min`, then
`set_fresh_gas_flow(FreshGasFlow(3.0))`. The setter raised
`SimulationConfigurationError` ("the tissue groups are perfused at 5.0 L/min
in total but cardiac output is 6.0 L/min ..."), after which the circuit held
3.0, the definition's open segment still 4.0, the timeline nothing, and the
run was still running and not failed. Through
`RunView._handle_fresh_gas_flow_change(3.0)` the banner read "Setting refused
— ... The simulation is unchanged and still running its previous setting."
over a snapshot whose fresh gas flow was 3.0 and a definition whose was 4.0.

**Why it matters.** `_record_control_change`'s docstring says the core
raises before it is reached, which holds for a refused *value* and not for a
record refused on another field: the one place that means "the core accepted
a setting change" is reached after the compartment has changed. The dial and
the readout then show a value the run's definition does not hold, under a
banner saying the simulation is unchanged.

**Done when.** A setting the record refuses leaves the compartment holding
what it held, or the record is built before the setter writes, so the
banner's "unchanged" is true; a test in
`tests/integration/test_controller.py` pins it. `PL-KFNP` is the root, and
fixing it there makes this unreachable; this item stands for the case where
the write stays admitted.

**Re-scoped 2026-10-12, in `PL-KFNP`'s design round.** Neither answer to
`PL-KFNP` makes this record unreachable: a tissue's or the venous pool's
`set_blood_flow` still sets a compartment's flow past the patient's output,
nothing in `src/` but `PatientCompartments._update_blood_flows` calls it, and
a caller `mypy` does not read can. So the case this item stands for is a
record reached that way, the fix above is unchanged by the answer, and it
waited on `PL-KFNP` because that build re-points `_with_stale_tissue_flows`
in `tests/integration/test_controller.py`, the helper this item's test uses.
The wait ended on 2026-10-17, when the two were built on one branch.
