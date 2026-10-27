---
id: PL-B3YV
title: No unit test checks the field name in the error that record_external_agent_transfer raises for a refused transfer: mutating either require_nonnegative_finite name argument (to None, upper case or padded) survives tests/unit/test_agent_simulation_validation.py, so a refused delivered transfer could be reported as the exhausted one
priority: P2
effort: S
status: done
classes: test
feature: tests-detect-wrong-values
touches: tests/unit/test_agent_simulation_validation.py
added: 2026-10-25
closed: 2026-10-27
pr: 1874
payoff: a refused agent transfer's error names the transfer that was refused, and a test fails if it names the other
verify: grep -q 'def test_a_refused_transfer_names_its_own_field' tests/unit/test_agent_simulation_validation.py
---

**Problem.** No unit test checks the field name in the error that record_external_agent_transfer raises for a refused transfer: mutating either require_nonnegative_finite name argument (to None, upper case or padded) survives tests/unit/test_agent_simulation_validation.py, so a refused delivered transfer could be reported as the exhausted one

**Reproduced 2026-10-26.** Changing the first `require_nonnegative_finite`
name in `record_external_agent_transfer`
(`src/anesthesia_sim/core/agent_simulation_validation.py`) to
`"DELIVERED_AGENT_L"`, and then the second to `"EXHAUSTED_AGENT_L"`, left all 48
tests in `tests/unit/test_agent_simulation_validation.py` passing each
time. The tests at the totals' checks do anchor the field name, so only the
two per-transfer checks are unpinned.

**Why it matters.** The mass-balance check is how a run proves it has not
created or destroyed anaesthetic agent. An error that names the wrong transfer
sends whoever debugs it to the wrong input.

**Done when.** `tests/unit/test_agent_simulation_validation.py` has
`test_a_refused_transfer_names_its_own_field`. It refuses a negative delivered
transfer and then a negative exhausted one, and it matches each error message
from its start on the field that was refused. Each refusal comes from a
validator whose running total is already larger than the size of the negative
transfer, for example 2.0 L recorded and then -1.0 L. The running-total checks
use the same two field names, so on a fresh validator they raise the same
message, and the test would still pass with a per-transfer check deleted. With
that check deleted, a negative transfer smaller than the total is accepted and
silently lowers the total in the mass balance.

**Done 2026-10-27.** `test_a_refused_transfer_names_its_own_field` records
2.0 L delivered and 2.0 L exhausted, then refuses -1.0 L delivered and -1.0 L
exhausted in turn. It matches each message from its start on the refused
field's name, and checks that neither refusal changed the validator. The
running totals would still be 1.0 L, so only the per-transfer checks can
refuse these transfers.

The test was replayed against seven mutants of the two per-transfer checks in
`record_external_agent_transfer`, and it failed on every one. The command was
`uv run pytest -q tests/unit/test_agent_simulation_validation.py::test_a_refused_transfer_names_its_own_field`,
run once per mutant with the original source restored between runs.

| Mutant | Failing assertion |
| --- | --- |
| first name `"DELIVERED_AGENT_L"` | `Regex pattern did not match`, expected `^delivered_agent_l must be nonnegative and finite...` |
| second name `"EXHAUSTED_AGENT_L"` | `Regex pattern did not match`, expected `^exhausted_agent_l must be nonnegative and finite...` |
| first name `None` | `Regex pattern did not match`, expected `^delivered_agent_l ...` |
| second name `" exhausted_agent_l "` | `Regex pattern did not match`, expected `^exhausted_agent_l ...` |
| first name `"exhausted_agent_l"` | `Regex pattern did not match`, expected `^delivered_agent_l ...` |
| first check deleted | `DID NOT RAISE SimulationConfigurationError` |
| second check deleted | `DID NOT RAISE SimulationConfigurationError` |
