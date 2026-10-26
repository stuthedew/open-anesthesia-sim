---
id: PL-B3YV
title: No unit test checks the field name in the error that record_external_agent_transfer raises for a refused transfer: mutating either require_nonnegative_finite name argument (to None, upper case or padded) survives tests/unit/test_agent_simulation_validation.py, so a refused delivered transfer could be reported as the exhausted one
priority: P2
effort: S
status: ready
classes: test
feature: tests-detect-wrong-values
touches: tests/unit/test_agent_simulation_validation.py
added: 2026-10-25
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
from its start on the field that was refused.
