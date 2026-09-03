---
id: PL-VYXP
title: AgentUptakeSystem.reset() anchors the mass-balance baseline to an implicit zero it does not itself establish
status: done
priority: P2
effort: S
classes: defect
touches: src/anesthesia_sim/core/uptake_system.py, tests/unit/test_uptake_system_failure.py
verify: uv run pytest tests/unit/test_uptake_system_failure.py && grep -q 'def test_reset_anchors_accounting_to_what_the_compartments_actually_hold' tests/unit/test_uptake_system_failure.py
added: 2026-09-02
closed: 2026-09-02
---

**Problem.** `AgentUptakeSystem.reset()` called
`self.agent_simulation_validator.reset()` with no argument, taking the
default `initial_agent_l=0.0`. The other construction path,
`__post_init__`, passes `initial_agent_l=self.total_stored_agent_l`
explicitly. The two disagreed about how the accounting anchor is
established, and `reset()`'s answer was correct only because the three
compartment `reset()`s happen to zero their stores and happen to run first.

**Why it matters, and how the audit overstated it.** The capture and the
audit that produced it both said this "fails open" - that a wrong anchor
would let the residual check validate a drifting system as clean. That was
argued rather than measured, and measuring it reversed the direction. With a
compartment retaining 0.05 L across `reset()`, the shipped code anchored at
0.0 and the very next check reported `unaccounted = -0.05 L` and
`passes_validation` False: an anchor that is too low makes the identity
short, so the check **fires** rather than staying quiet. It cannot mask a
real drift except within the accounting tolerance itself.

So this failed *closed*, which is the safe direction, and the finding is
smaller than it was first written up as - reseated from `safety` at P1 to
`defect` at P2 on that measurement. It is still worth closing. The residual
check is what halts a run and reports `AgentSimulationValidationError`, so a
mis-anchored one halts a run that is perfectly accounted for and blames the
numerics for an anchoring defect - the same shape as `PL-006`, where a
setter destroyed agent and the *next* step was blamed for it. A safety net
that stops a healthy run teaches a reader to distrust it.

No shipped compartment retains agent across `reset()`, so nothing was
reachable in the application. The defect was in what the code guarantees,
not in what it currently does.

**Where.** `src/anesthesia_sim/core/uptake_system.py`, `reset()`.

**Decision needed.** *Answered by the project owner, 2026-09-02: option 1.*
Make `reset()` symmetric with `__post_init__` -
`reset(initial_agent_l=self.total_stored_agent_l)` after clearing the
compartments. Bit-identical today, since that expression is exactly `0.0`;
immune to the reordering hazard tomorrow. The alternatives were to document
the ordering dependency instead, or to drop the finding with the reason
recorded.

**Done when.** The anchor is read back out of the compartments, and a test
fails against the old code: a compartment stand-in whose `reset()` leaves
agent behind must leave the validator anchored to that amount rather than to
zero.

**Done.** `reset()` passes `initial_agent_l=self.total_stored_agent_l`, with
the docstring recording the failure direction so the next reader does not
repeat the audit's mistake about it.
`test_reset_anchors_accounting_to_what_the_compartments_actually_hold`
reproduces the defect through a stand-in compartment and was watched failing
against the unfixed code with `assert 0.0 == 0.05`;
`test_reset_still_anchors_at_zero_when_every_compartment_clears` passes
either way by design, pinning the equivalence that makes the change safe to
take, so that a compartment which later stops clearing is caught as a change
in what an accounting period starts from rather than silently rewriting it.
