---
id: PL-WMN7
title: No unit test pins how PatientCompartments.from_parameters maps each agent's tissue:gas coefficients onto the three tissue groups, so unit-tier detection of a mis-mapping rests on golden numbers measured from the code's own output
priority: P2
effort: S
status: done
classes: test
feature: tests-detect-wrong-values
touches: tests/unit/test_patient.py
added: 2026-10-17
closed: 2026-10-17
pr: 1513
payoff: a tissue group built with another group's or another agent's partition coefficient fails a unit test checked against the data files, not against golden numbers taken from the code's own output
verify: grep -q 'def test_each_tissue_group_takes_its_own_agents_coefficients' tests/unit/test_patient.py
---

**Problem.** No unit test pins how PatientCompartments.from_parameters maps each agent's tissue:gas coefficients onto the three tissue groups, so unit-tier detection of a mis-mapping rests on golden numbers measured from the code's own output

**Severity: medium.** Audit finding ORC-2 (unit tier), confirmed by the
adversarial verifier.

**Evidence.** Probe P1 swapped the vessel-rich and muscle tissue:gas
coefficients in `PatientCompartments.from_parameters`
(`src/anesthesia_sim/core/patient.py`). `pytest tests/unit` then gave 6
failures. Three were apparatus tests that fail on any scratch copy without
`.git`. The three simulator failures were:

- `test_changing_circuit_volume_mid_run_does_not_break_the_next_step` in
  `tests/unit/test_uptake_system_failure.py`, through `approx(0.048301285)`.
  Its comment says the value was "Re-measured 2026-09-07" from the code.
- `test_a_real_run_displays_a_filling_compartment_as_below_resolution` in
  `tests/unit/test_dashboard_frame.py`, through the '0.61%' and '<0.01%'
  readout pins.
- An incidental chord-error bound,
  `test_a_pixel_wide_chord_misses_an_extremum_by_under_the_readout_s_resolution`
  in `tests/unit/test_run_definition.py`.

The worker counted 97 failures in `tests/reference`; the verifier did not
re-run those. `test_builds_reference_patient_from_parameters` in
`tests/unit/test_patient.py` pins the volumes and flows. No test outside
`tests/reference` asserts a group's `tissue_gas_partition_coefficient` or
`tissue_blood_partition_coefficient` after `from_parameters`. The coefficient
pins in `tests/unit/test_parameters.py` test the loader, which does not
exercise the mapping. `test_governing_equations.py` builds its rows from its
own literal tissues.

**Why it matters.** At unit level, a mis-mapped clinical coefficient is caught
only by values copied from the code's own output. Had the mapping been wrong
when those values were measured, the unit tier would have certified the wrong
mapping, and a mutation run scores these kills as strong. Only the
published-data reference suite is an independent check of the mapping.

**Where.** `src/anesthesia_sim/core/patient.py` (`from_parameters`);
`tests/unit/test_patient.py`.

**Recommended test.** Extend `test_builds_reference_patient_from_parameters`
to assert, as literals typed from the data files, each group's
`tissue_gas_partition_coefficient` (sevoflurane 1.1, 2.4 and 34.0 for
vessel-rich, muscle and fat), `tissue_blood_partition_coefficient` (each of
those divided by 0.65) and `perfusion_fraction` (0.76, 0.18 and 0.06). Repeat
for desflurane (0.54, 0.97 and 13.0), so that a mapping which reads one
agent's values for every agent also fails.

**Done when.** Probe P1 fails a test in `tests/unit/test_patient.py`.

**Provenance.** A read-only test-effectiveness audit on 2026-10-17 found this.
The audit ran mutation testing with mutmut 3.8.0 over `core/` and four
presentation modules against the 33 simulator unit-test files (at
`b9b3c812`). It ran each real-gap survivor against the whole 5734-test
simulator suite (at `25ef454b`). It also used fault injection, stored-value
perturbation, oracle classification and regression-test replay, and an
adversarial second agent verified each finding. Its scratch files are not
durable, so the evidence is written out above. Symbols re-checked against
`9ea87a3c`.

**Fail-before, 2026-10-17.** `test_each_tissue_group_takes_its_own_agents_coefficients`
in `tests/unit/test_patient.py` runs once per agent: sevoflurane, desflurane
and isoflurane. For each it builds the reference patient with
`PatientCompartments.from_parameters` and asserts each group's name,
tissue:gas, blood:gas and tissue:blood coefficients and perfusion fraction,
and the venous pool's blood:gas coefficient. The coefficients and fractions
are literals typed from the data files, and the test divides tissue:gas by
blood:gas itself. It passes on the shipped code. Two mis-mappings were
applied to `src/anesthesia_sim/core/patient.py` and the command
`uv run pytest -q -p no:randomly tests/unit/test_patient.py` was run:

- Probe P1, the vessel-rich and muscle tissue:gas coefficients swapped:
  exit 1, with 3 failed and 14 passed. The sevoflurane case fails with
  `assert [2.4, 1.1, 34.0] == [1.1, 2.4, 34.0]`.
- Sevoflurane's blood:gas coefficient used for every agent
  (`blood_gas = 0.65` in place of `agent.blood_gas_partition_coefficient`):
  exit 1, with 2 failed and 15 passed. The desflurane case fails with
  `assert [0.65, 0.65, 0.65] == [0.42, 0.42, 0.42]`.

Both were reverted with `git checkout`. The brief recommended extending
`test_builds_reference_patient_from_parameters`; the item's `verify:` names a
new test, so the assertions went there, and the old test is unchanged.
