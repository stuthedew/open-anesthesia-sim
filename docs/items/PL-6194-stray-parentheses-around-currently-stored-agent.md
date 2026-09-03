---
id: PL-6194
title: Stray parentheses around currently_stored_agent_l in the accounting result
status: untriaged
added: 2026-09-03
---

**Problem.** Stray parentheses around currently_stored_agent_l in the accounting result

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `check_agent_accounting()` builds its result with
`currently_stored_agent_l=(currently_stored_agent_l)` — parentheses around a
bare name, doing nothing. Every other field on the same call is plain.

Trivial, and filed only because the file is safety-critical: a reader who
knows the standard this project holds `core/` to will stop on a redundant
construct and look for the reason, and there is none. `ruff format` leaves it
alone, so nothing will remove it on its own.

**Where.** `src/anesthesia_sim/core/agent_simulation_validation.py`, in the
`AgentSimulationValidationResult(...)` construction.

**Found.** Reading the guard while writing `PL-B7ZV`'s boundary tests.
