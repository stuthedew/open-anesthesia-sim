---
id: PL-X204
title: require_valid_agent_accounting() reads nothing from self, so it will judge a result from another accounting period
priority: P2
effort: S
status: ready
classes: refactor
feature: numerical-domain
touches: src/anesthesia_sim/core/agent_simulation_validation.py, src/anesthesia_sim/core/uptake_system.py, tests/unit/test_agent_simulation_validation.py
added: 2026-09-03
verify: uv run pytest tests/unit/test_agent_simulation_validation.py && grep -q 'def test_require_valid_agent_accounting_reads_the_validators_own_state' tests/unit/test_agent_simulation_validation.py
---

**Problem.** `AgentSimulationValidator.require_valid_agent_accounting()` is an
instance method that reads nothing from `self`. It takes an
`AgentSimulationValidationResult` and raises on it; the validator it is called
on is never consulted.

So `validator_a.require_valid_agent_accounting(check_from_validator_b)` passes
silently, and the exception it raises would report `initial=`, `delivered=` and
`exhausted=` from an accounting period the caller was not asking about.

**Why it matters.** Nothing produces a wrong number today — `uptake_system.py`
is the only production caller and it computes the result one line before
requiring it, from the same validator, with nothing mutating in between. The
problem is what the code claims. This is the guard that halts a run whose
numbers can no longer be trusted, and `CLAUDE.md`'s safety-critical standard
asks such a path to be traceable and explicit: a reader sees
`self.agent_simulation_validator.require_valid_agent_accounting(check)` and
takes it to mean the validator is checking its own accounting, which is the one
thing it does not do. A halt message describing the wrong period would be a
presentation failure by that same standard.

**Where.** `src/anesthesia_sim/core/agent_simulation_validation.py`,
`require_valid_agent_accounting()`; its only production caller is
`src/anesthesia_sim/core/uptake_system.py:354`.

**Approach — take the stored amount, not the result.** Change the signature to
`require_valid_agent_accounting(currently_stored_agent_l: float) ->
AgentSimulationValidationResult`: it computes the check from `self`, raises on
failure, and returns the result on success. `uptake_system.advance()` then
replaces its two lines with one and keeps the result it already returns in
`UptakeStepResult`.

This is what the call-site evidence makes available, and it is why the two
approaches the capture named both lose:

- **A static method or module function** makes the independence honest but
  leaves the mismatch permanently unreachable rather than impossible. It fixes
  the reading and not the contract.
- **Comparing the result's three totals against `self`** closes the mismatch
  but pays three float comparisons every step to catch a caller error, and
  turns a programming mistake into the same exception type as a conservation
  failure.

The read-only half stays exactly as it is. `check_agent_accounting()` and
`UptakeSystem.agent_simulation_validation` are read by `app/controller.py:222`
for display and by seventeen assertions across `tests/unit`, `tests/reference`
and `tests/integration`; measured 2026-09-03, so the split is load-bearing and
must survive. Only the `require` half changes.

**Done when.** `require_valid_agent_accounting()` computes its own check from
the validator's state, no caller can hand it a foreign result,
`tests/unit/test_agent_simulation_validation.py` carries
`test_require_valid_agent_accounting_reads_the_validators_own_state`, and the
existing display path and its seventeen assertions are untouched.

**Found.** Reading the guard while writing `PL-B7ZV`'s boundary tests, which
call `require_valid_agent_accounting()` on a result they build themselves and
so had to work out what it actually reads. Captured that session as an open
decision between the two approaches above; the call-site evidence that settles
it was gathered during triage.
