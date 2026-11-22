---
id: PL-S8FM
title: A circuit or alveolar volume written directly on the core and followed by a control change through SimulationController is adopted into the run's settings record without a refusal, so a run can go on under a volume that the docs call fixed for a run (found at blind review of PL-DQWL)
status: untriaged
feature: replay-findings
added: 2026-11-22
---

**Problem.** A circuit or alveolar volume written directly on the core and followed by a control change through SimulationController is adopted into the run's settings record without a refusal, so a run can go on under a volume that the docs call fixed for a run (found at blind review of PL-DQWL)

**Found by.** The first blind review pass on the second design of `PL-DQWL`,
2026-11-22. `SimulationController._record_control_change` records the whole
settings record that the core holds, which includes `circuit_volume_l` and
`alveolar_volume_l`. Its docstring says this is deliberate: the run
definition then matches the core again, whatever else had moved, and a
perfusion fraction written past its guard can still be written back
(`PL-VCP4`). So a volume written on the core and then followed by a dial
change is adopted. `SimulationState.advance` refuses the step only where the
change moved a fraction, which an empty compartment's change does not.

**Why it matters.** No interface control writes a volume, so a learner cannot
reach it. `docs/MODEL.md` § "The four controls" calls both volumes fixed for a
run, and a script against the controller could run under a volume that the
control timeline never shows.

**What a fix has to decide.** Whether `_record_control_change` refuses a
record whose fixed parameters differ from the recorded ones, and how that
keeps `PL-VCP4`'s write-back of a guarded field.
