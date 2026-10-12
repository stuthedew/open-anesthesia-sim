---
id: PL-J39J
title: After a cardiac output written past set_cardiac_output halts the run, at the next step or at the Reset PL-M4M0 refuses, the cardiac output readout and dial show the written output beside compartment values and a chart computed at the old flows, under a banner saying the values shown are the last completed step; only the banner's own sentence names both figures (found reviewing PL-M4M0)
priority: P1
effort: S
status: blocked
classes: safety, defect
feature: cardiac-output-write-consistency
touches: src/anesthesia_sim/app/dashboard_frame.py, tests/integration/test_simulation_view.py
blocked-by: PL-KFNP
added: 2026-10-11
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
