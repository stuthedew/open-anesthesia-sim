---
id: PL-X204
title: require_valid_agent_accounting() reads nothing from self, so it will judge another validator's result
status: untriaged
added: 2026-09-03
---

**Problem.** require_valid_agent_accounting() reads nothing from self, so it will judge another validator's result

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `AgentSimulationValidator.require_valid_agent_accounting()` is an
instance method that reads nothing from `self`. It takes an
`AgentSimulationValidationResult` and raises on it; the validator it is called
on is never consulted.

Two consequences, both about traceability rather than a wrong number today:

1. `validator_a.require_valid_agent_accounting(check_from_validator_b)` passes
   silently. Nothing holds the result being judged to the accounting period
   that produced it, and the exception it raises would report `initial=`,
   `delivered=` and `exhausted=` from a period the caller was not asking
   about.
2. The call site reads as though the validator is checking its own state,
   which is the thing a reader of a safety-critical guard would assume. The
   result carries the three totals precisely so it can be read on its own, so
   the signature and the reading disagree.

**Where.** `src/anesthesia_sim/core/agent_simulation_validation.py`,
`require_valid_agent_accounting()`.

**Approach, not settled.** A `@staticmethod`, or a module-level function, would
make the independence explicit and stop the misreading — but it drops the
possibility of (1) ever being caught. Checking the result against `self` would
close (1) instead, at the cost of the `check`/`require` split being usable the
way `core/simulation.py` uses it. Which of the two is right is the decision the
item wants; it is not a defect to fix mechanically.

**Found.** Reading the guard while writing `PL-B7ZV`'s boundary tests, which
call `require_valid_agent_accounting()` on a result they built and so had to
work out what it actually reads.
