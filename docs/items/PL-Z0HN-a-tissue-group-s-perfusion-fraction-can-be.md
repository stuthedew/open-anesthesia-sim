---
id: PL-Z0HN
title: A tissue group's perfusion fraction can be changed on a built patient, and nothing checks that the fractions still sum to 1, so every later cardiac output change is refused, and its restore moves the tissue flows under a banner that says nothing changed (found reviewing PL-VCP4)
priority: P1
effort: M
status: done
classes: safety, defect
feature: cardiac-output-write-consistency
touches: src/anesthesia_sim/core/patient.py, src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/app/controller.py, tests/unit/test_patient.py, tests/integration/test_controller.py, docs/MODEL.md
added: 2026-10-17
closed: 2026-10-18
payoff: a perfusion fraction can no longer be changed on a built patient, so the tissue flows cannot drift from the cardiac output under a banner that says nothing changed
verify: grep -q 'def test_a_perfusion_fraction_written_on_a_built_patient_is_refused' tests/unit/test_patient.py
reenters: PL-KFNP
recurrences: 2026-10-18 PL-01GY
---

**Problem.** `TissueGroup.__setattr__` accepts a new `perfusion_fraction` on a
tissue group that already belongs to a patient. `PatientCompartments.__post_init__`
is the only check that the fractions sum to 1, and it runs only when the
patient is built. Neither the settings record nor the propagator cache reads
the fractions, so the run keeps stepping at the flows it had. The change shows
only when the cardiac output next changes, and then it cannot be undone.

**Reproduced 2026-10-17** by the state review of `#1488`, and again by the
session that built it. Start a default `SimulationController` and run 50 steps
of 0.1 s. Set `patient.vessel_rich.perfusion_fraction = 0.5`, so the fractions
sum to 0.74. Ten more steps run with no failure. Then call
`set_cardiac_output(CardiacOutput(6.0))`. The patient sets the tissue flows
from 6.0 times the fractions, which sum to 4.44 L/min, so the settings record
refuses the change. `PL-VCP4`'s restore then sets the flows from 5.0 times the
new fractions. The output is back at 5.0, but the vessel-rich flow has moved
from 3.8 to 2.5 L/min. Through `RunView`, the state review saw the banner say
"The simulation is unchanged and still running its previous setting." The next
step halts the run
with "the tissue groups are perfused at 3.7 L/min in total but cardiac output
is 5.0 L/min". No cardiac output can repair that record, because the fractions
no longer sum to 1. So the refused Reset's advice to change the setting it
names can never succeed.

No shipped control writes a perfusion fraction. This is not a regression: on
`main` before `#1488`, the same path also halted, with the patient left at 6.0
and the flows at 6.0 times the fractions.

**Why it matters.** The banner tells the reader that nothing changed, while
every tissue flow has moved. And the repair that the halt names cannot work,
so the run can only be abandoned.

**Two ways to fix it.** The first is to refuse a perfusion fraction written on
a built patient, at the write, as `PL-KFNP` did for the cardiac output. That
removes the state. The second is to refuse a cardiac output change in
`PatientCompartments.set_cardiac_output`, before anything moves, when the
fractions do not sum to 1. That keeps the restore exact, but it leaves the
fractions wrong.

**The cardiac output's restore has no test.** Its only known path is this one.
The state review replaced it with `lambda: None`, and the whole suite stayed
green (5717 passed). The other three setters' restores are tested by
`test_a_setting_the_record_refuses_leaves_the_run_on_its_previous_setting`.

**Done when.** A perfusion fraction change on a built patient cannot leave the
fractions summing to something other than 1, or a cardiac output change on such
a patient is refused before anything moves. A test pins the choice, and a test
reaches the cardiac output's restore or the item says why nothing can.

**Route chosen at triage, 2026-10-17: refuse the write.** The first route is
taken, as `PL-KFNP` did for the cardiac output. It removes the invalid state,
which this project prefers to warning about it (`.claude/rules/expert-review.md`,
"Favor interfaces that prevent errors"). The second route leaves the fractions
wrong and only stops one of their consequences. `PL-HQF5` asks the same question
for the blood flows, and its answer should not contradict this one.

**Generator check.** A re-entry of `PL-KFNP`'s mechanism at a sibling field: a
value on a built patient that takes part in the perfusion relation can be
written past the check in `PatientCompartments.__post_init__`.

**Built, 2026-10-18, with `PL-HQF5`.** `TissueGroup.perfusion_fraction` is
write-once. A second write is refused with a message that says the patient
checks its fractions only when it is built, and to build a new patient. The
patient also refuses a tissue group written onto a built patient unless the
fractions, with the replacement in place, still sum to 1. Copies and pickles
write the field once onto a new object, so they are accepted.
`test_a_perfusion_fraction_written_on_a_built_patient_is_refused` pins the
choice. `PL-VCP4`'s controller test now reaches the cardiac output's restore:
with the fractions written past their guard, a cardiac output change is
refused and the restore leaves the output, the flows, the segments and the
timeline unchanged.

Regression proof: on `88960a11`,
`vessel_rich.perfusion_fraction = 0.5` on the default patient was accepted and
left fractions of `[0.5, 0.18, 0.06]`. The new test, run there with
`PYTHONPATH=$BASE/src python -m pytest tests/unit/test_patient.py -k
perfusion_fraction_written_on_a_built`, fails with `Failed: DID NOT RAISE
SimulationConfigurationError`.
