---
id: PL-S8FM
title: A circuit or alveolar volume written directly on the core and followed by a control change through SimulationController is adopted into the run's settings record without a refusal, so a run can go on under a volume that the docs call fixed for a run (found at blind review of PL-DQWL)
status: done
feature: replay-findings
milestone: v0.6.21
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/run_view.py, tests/integration/controller/test_controller_run_definition.py, tests/integration/simulation_view/test_simulation_view_views.py, docs/INTERFACE.md
added: 2026-11-22
closed: 2026-11-22
pr: 2245
tests: tests/integration/controller/test_controller_run_definition.py::test_a_control_change_after_a_setting_written_past_the_controller_is_refused, tests/integration/simulation_view/test_simulation_view_views.py::test_a_run_holding_an_unrecorded_setting_draws_no_preview_while_its_thumb_is_held
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
reach it. `docs/INTERFACE.md` § "What is not bounded this way" says that
neither volume can be changed during a run, and a script against the controller could run under a volume that the
control timeline never shows.

**What a fix has to decide.** Whether `_record_control_change` refuses a
record whose fixed parameters differ from the recorded ones, and how that
keeps `PL-VCP4`'s write-back of a guarded field.

**What was built.** `SimulationController._change_setting` now calls
`_refuse_a_setting_after_an_unrecorded_one` before it applies anything. When
the settings on the core differ from the ones the controller last recorded,
and the core's settings record is itself consistent, the control change is
refused with the same `SimulationExecutionError` the controller's next step
gives (`_unrecorded_setting_error`). Nothing is written to the core, the run
definition or the control timeline. Where the core's settings record is
itself refused, such as a perfusion fraction written past its guard, the
check steps aside, so `PL-VCP4`'s write-back still repairs it. The refusal
covers every setting the existing step check covers, not only the two
volumes, because a dial written past the controller is adopted the same way.
A reset still starts a new run from the settings the core holds.

`SimulationController.preview_settings` makes the same check, and
`RunView.request_preview` draws no preview when it fails. Without that, a
held dial drew a predicted curve that its release would then refuse. The
second blind review pass found this gap, and
`tests/integration/simulation_view/test_simulation_view_views.py::test_a_run_holding_an_unrecorded_setting_draws_no_preview_while_its_thumb_is_held`
holds it. Against the first commit of this branch, 0bcd1cdb, it fails with
`assert (60.0, 90.0) is None` on the concentration chart's preview region.

**Why this design.** The choice was between refusing at the control change
and keeping the adoption. Two sources decide it. The second was added after
the merge, at the owner's question of 2026-11-22.

1. Meyer, Arkadova and Kogtenkov, "The concept of class invariant in
   object-oriented programming", arXiv:2109.06557v12, read in full through
   `pdftotext` on 2026-11-22. They name the "reference leak": an operation on
   one object breaks the invariant of another object that depends on it,
   without any of the second object's routines running. § 8.3 ("Weak rule,
   supply-side") lets a routine assume only the local part of its
   invariant on entry, so the routine itself must handle the case where the
   remote part does not hold. The paper calls this the best available rule.
   The controller's invariant is that its recorded settings are the core's,
   and the core is the other object. A write on the core is the reference
   leak, and a control change is a routine that must check the remote part
   before it relies on it.
2. `CLAUDE.md` § "Safety-critical clinical-output standard": do not silently
   substitute or coerce, and prefer an obvious failure to a plausible value.
   This decides how the controller deals with the broken invariant. Writing
   the recorded settings back over the core would undo a write without
   saying so, and adopting the core's settings would show a volume that
   `docs/INTERFACE.md` § "What is not bounded this way" says cannot be
   changed during a run. Refusing with an error that names the cause, and
   leaving a reset as the way out, does neither.

The preview follows the run view's own requirement, in
`RunView.request_preview`, that a value the run would refuse draws no preview.

**Regression test.** `tests/integration/controller/test_controller_run_definition.py::test_a_control_change_after_a_setting_written_past_the_controller_is_refused`,
over the four dials and both volumes, before the run starts and after 10 s.
Against `src/anesthesia_sim/app/controller.py` from `origin/main` 0a65c401
all twelve cases fail with `Failed: DID NOT RAISE SimulationExecutionError`.
Command: `uv run pytest -q -p no:randomly
tests/integration/controller/test_controller_run_definition.py -k
written_past_the_controller_is_refused`.

**Generator check.** The fact is which settings the run's record holds, and
its home is the controller's recorded settings key (`PL-XRN8`). The step
already read it, and the control change did not, so this is a second reader
that the first fix left out, found by review of `PL-DQWL`. No `reenters:` is
recorded.

**Docs checked.** `docs/INTERFACE.md` § "What is not bounded this way" now
says a control change is refused too. `docs/MODEL.md`, `docs/VERIFICATION.md` and `docs/PARAMETERS.md` make no claim about how a
written volume is handled, so none changed.
