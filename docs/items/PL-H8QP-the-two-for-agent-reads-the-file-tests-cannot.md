---
id: PL-H8QP
title: The two for_agent reads-the-file tests cannot fail when for_agent() stops reading a data file, because the core defaults equal the files' values, so docs/MODEL.md's claim that they catch it holds only for the fresh gas flow
priority: P1
effort: S
status: done
classes: safety, test
feature: machine-profile-framework
touches: tests/unit/test_circuit.py, tests/unit/test_alveolar.py, docs/MODEL.md
added: 2026-09-27
closed: 2026-10-03
payoff: a change that stops for_agent() reading the circuit volume or the alveolar values fails a test instead of passing on matching defaults
verify: grep -q 'def test_for_agent_builds_the_circuit_at_a_changed_machine_file_volume' tests/unit/test_circuit.py && grep -q 'def test_for_agent_builds_the_alveoli_at_changed_patient_file_values' tests/unit/test_alveolar.py
---

**Problem.** The two for_agent reads-the-file tests cannot fail when for_agent() stops reading a data file, because the core defaults equal the files' values, so docs/MODEL.md's claim that they catch it holds only for the fresh gas flow

**Found by PL-QW19's review, 2026-09-27, by mutation rather than argument.**
`test_for_agent_builds_the_circuit_at_the_machine_file_s_values`
(`tests/unit/test_circuit.py`) and
`test_for_agent_builds_the_alveoli_at_the_patient_file_s_values`
(`tests/unit/test_alveolar.py`) assert that a run built by
`AgentUptakeSystem.for_agent()` carries the data files' values. But
`BreathingCircuit`'s and `AlveolarCompartment`'s field defaults equal those
values (6.0 L, 2.5 L, 4.0 L/min), so a `for_agent()` that stopped passing them
and fell through to the defaults passes both tests. Patched to ignore the
machine file's volume, the reviewer ran `test_circuit`, `test_parameters`,
`test_simulation` and `test_wash_in`: 156 passed. The flow is the exception
since `PL-QW19`, whose
`test_a_profile_stating_its_startup_flow_opens_the_run_at_that_flow` builds a
run from a profile stating 2.0 L/min and fails under the same patch.

**Why it matters.** `docs/MODEL.md`'s paragraph "Each parameter file is the
single authority for its own values" rests on these tests: without them "every
provenance row in this table would silently become a claim about a file the
model no longer consults". `PL-QW19` corrected that paragraph to say the
guarantee holds for the flow only and points here for the other three.

**Fix.** The same shape as `PL-QW19`'s tests: parse the shipped file with the
value changed (a circuit volume of 3.3 L; an alveolar volume and ventilation
other than 2.5 L and 4.0 L/min), hand it to `for_agent()` by replacing the
loader it calls (`monkeypatch.setattr(uptake_system, ...)`, as
`tests/integration/test_controller.py` already does), and assert the run
carries the changed value. Then restore the paragraph's claim for all four.

**Reproduced 2026-09-28, in part.** `BreathingCircuit.circuit_volume_l`
defaults to 6.0 (`core/circuit.py`) and
`AlveolarCompartment.alveolar_ventilation_l_min` to 4.0 (`core/alveolar.py`),
the values the brief gives for the shipped files; the mutation run is the
reviewer's.

**Done when.** A test per file builds a run from a parsed file whose value
differs from the core default - a circuit volume of 3.3 L; an alveolar volume
and ventilation other than 2.5 L and 4.0 L/min - and asserts the run carries it,
and `docs/MODEL.md`'s paragraph claims the guarantee for all four values again.

**Built (2026-10-03).** Two tests now build a run from a parsed file stating
values off the core defaults, handed to `for_agent()` by replacing the loader
it calls, as `PL-QW19`'s profiles are:
`test_for_agent_builds_the_circuit_at_a_changed_machine_file_volume` (3.3 L,
49.5 s at the shipped 4.0 L/min) and
`test_for_agent_builds_the_alveoli_at_changed_patient_file_values` (3.0 L and
5.0 L/min, 36 s). The two shipped-file tests stay, as the pins on the 90 s and
37.5 s a learner reads off the early rise, with docstrings that no longer
claim they show the file was read. `docs/MODEL.md`'s paragraph names a guard
for each of the four values, the flow's being `PL-QW19`'s
`test_a_profile_stating_its_startup_flow_opens_the_run_at_that_flow`.

Measured by breaking each value's route through `for_agent()` in turn and
running `tests/unit` and `tests/integration`. Before, the brief was right only
for the alveolar volume, which nothing caught. The circuit volume was already
caught by `test_a_profile_omitting_the_default_fresh_gas_flow_falls_back_to_the_teaching_default`,
whose 8.0 L profile landed with `PL-QW19` itself (#1211), and the ventilation
by `tests/integration/test_controller.py::test_patient_defaults_come_from_the_data_file`
(`PL-017`), which the review's run of four files did not include; neither is
named for that job. After, each of the four fails the test the paragraph names
for it.
