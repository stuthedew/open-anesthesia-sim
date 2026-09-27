---
id: PL-H8QP
title: The two for_agent reads-the-file tests cannot fail when for_agent() stops reading a data file, because the core defaults equal the files' values, so docs/MODEL.md's claim that they catch it holds only for the fresh gas flow
status: untriaged
feature: machine-profile-framework
touches: tests/unit/test_circuit.py, tests/unit/test_alveolar.py, docs/MODEL.md
added: 2026-09-27
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
