---
id: PL-VYXP
title: AgentUptakeSystem.reset() anchors the mass-balance baseline to an implicit zero it does not itself establish
status: needs-decision
priority: P1
effort: S
classes: safety, defect
touches: src/anesthesia_sim/core/uptake_system.py, tests/unit/test_uptake_system_failure.py
added: 2026-09-02
---

**Problem.** `AgentUptakeSystem.reset()` calls
`self.agent_simulation_validator.reset()` with no argument, taking the
default `initial_agent_l=0.0`. The other construction path,
`__post_init__`, passes `initial_agent_l=self.total_stored_agent_l`
explicitly. The two disagree about how the accounting anchor is
established, and `reset()`'s answer is correct only because the three
compartment `reset()`s happen to zero their stores and happen to run first.

**Why it matters.** The mass-balance residual is this model's principal
numerical safety net: it is what raises `AgentSimulationValidationError` and
halts a run. Anchored to a baseline that no longer matches what the
compartments hold, it validates a drifting system as clean - it fails
*open*, and invisibly, because the check reports "valid" while doing so.
Nothing enforces either condition it depends on. `BreathingCircuitState`'s
own docstring already anticipates a step that changes circuit volume - a
bellows model - and a compartment that resets to a non-zero baseline is the
shape that breaks this silently.

Found in a read-only safety-critical audit, not from a failure in the field.
No current code path reaches the broken state.

**Where.** `src/anesthesia_sim/core/uptake_system.py`, `reset()` against
`__post_init__`.

**Decision needed.** Whether a latent failure with no reachable trigger is
worth a change to a working safety net. Three ways to go:

1. Make `reset()` symmetric with `__post_init__` -
   `reset(initial_agent_l=self.total_stored_agent_l)` after clearing the
   compartments. Bit-identical today, since that expression is exactly
   `0.0`; immune to the reordering hazard tomorrow. One line.
2. Leave the code and document the ordering dependency where `reset()` can
   be read, so the next person to add a compartment sees it.
3. Decide the hazard is hypothetical enough to drop, with the reason
   recorded so the audit finding is not re-raised.

Option 1 is what the audit recommended, on the principle that a check must
not rest on an invariant it does not itself establish. It is recorded here
as a recommendation, not as an agreed change.

**Done when.** The decision is recorded, and - if it is 1 or 2 - the change
has landed with a test that fails against today's code: a compartment stub
whose `reset()` leaves agent behind must leave the validator anchored to
that amount rather than to zero.
