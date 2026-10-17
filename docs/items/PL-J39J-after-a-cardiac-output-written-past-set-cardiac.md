---
id: PL-J39J
title: After a cardiac output written past set_cardiac_output halts the run, at the next step or at the Reset PL-M4M0 refuses, the cardiac output readout and dial show the written output beside compartment values and a chart computed at the old flows, under a banner saying the values shown are the last completed step; only the banner's own sentence names both figures (found reviewing PL-M4M0)
priority: P1
effort: S
status: done
classes: safety, defect
feature: cardiac-output-write-consistency
touches: src/anesthesia_sim/app/dashboard_frame.py, tests/integration/test_simulation_view.py
added: 2026-10-11
closed: 2026-10-17
pr: 1488
payoff: a halted run's cardiac output readout and dial show the output the values beside them were computed at, so no figure on screen states a run the model never ran
verify: grep -q 'def test_a_run_halted_on_tissue_flows_set_past_its_patient_shows_the_output_its_last_step_ran_at' tests/integration/test_simulation_view.py
---

**Problem.** After a cardiac output written past set_cardiac_output halts the run, at the next step or at the Reset PL-M4M0 refuses, the cardiac output readout and dial show the written output beside compartment values and a chart computed at the old flows, under a banner saying the values shown are the last completed step; only the banner's own sentence names both figures (found reviewing PL-M4M0)

**Reproduced 2026-10-11** at the `PL-M4M0` fold: after `CardiacOutput(6.0)`
written onto the patient past `set_cardiac_output` on a run whose flows sum
to 5.0, the halt that follows - the next step's restatement, or the Reset
`PL-M4M0` refuses - leaves the cardiac output readout and dial at 6.0 beside
compartment values and a chart computed at 5.0, under "The values shown are
the last completed step." The snapshot copies the patient's field, which
holds the written value; the flows hold the old one; no single figure is true
of the record. The banner's own sentence names both figures, which is the
whole mitigation today, and no test asserts the readout.

**Why it matters.** `CLAUDE.md`'s standard counts a correct number with the
wrong context as a safety failure, and a readout the model never ran at
beside values it did is that; the item `PL-M4M0` closed named this readout
among the half-reset run's symptoms and could fix only the half reset.

**Done when.** On a run halted for a record the flows and the output
disagree in, the cardiac output readout states the disagreement rather than
one of the two figures, or `PL-KFNP` makes the state unreachable; a test in
`tests/integration/test_simulation_view.py` pins whichever is chosen.

**Re-scoped 2026-10-12, in `PL-KFNP`'s design round.** [superseded 2026-10-17: `PL-KFNP`'s build measured this route. The readout it reaches matches the values beside it, as the outcome below explains.] Neither answer to
`PL-KFNP` makes this state unreachable: a tissue's or the venous pool's
`set_blood_flow` still sets a compartment's flow past the patient's output,
nothing in `src/` but `PatientCompartments._update_blood_flows` calls it, and
a caller `mypy` does not read can. Reached that way the readout shows the
output the dial was set to beside values computed at flows that do not sum to
it, which is still one of two disagreeing figures, so the fix above is
unchanged by the answer. It stays blocked on `PL-KFNP` because that build
re-points `_with_stale_tissue_flows` in
`tests/integration/test_simulation_view.py`, the helper this item's test
would use.

**Outcome, 2026-10-17** (`#1488`). The item closes by the second form that
its Done-when names, because `PL-KFNP` makes the state unreachable. The
re-scope above said it would not. Its reason was that the remaining route
shows the output the dial was set to beside values computed at flows that do
not sum to it. Measured, the route does not do that. A tissue's own
`set_blood_flow` changes no output, so the patient keeps the output that its
last completed step ran at. The next step builds a record at the stale flows,
and that record is refused before any step runs at them. The readout, the
dial, the compartment values and the run's definition all state 5.0, the
output those values were computed at. The chart is drawn from the definition.
Only the tissue flows disagree. They sum to 6.0, and no step ever ran at
them. The banner's sentence names them. No disagreement is left for the
readout to state, and stating one would put a second figure beside a true
one. The clinical review of `#1488` confirmed this. Its readouts equalled the
chart's last point to within 5e-15.

`test_a_run_halted_on_tissue_flows_set_past_its_patient_shows_the_output_its_last_step_ran_at`
pins the halt at the step and the refused Reset after it. It also pins that a
cardiac output written past `set_cardiac_output`, the route this item found,
is refused. It fails before `PL-KFNP` with DID NOT RAISE. The settings record
does not refuse the other half of the remaining route, flows moved between
tissues with their sum unchanged. There the readouts and the chart do
disagree, but not about the cardiac output, because the output shown is the
sum the run stepped at. That half is recorded on `PL-HQF5`.
