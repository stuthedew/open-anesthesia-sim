---
id: PL-026
title: Make the simulation step transactional so a halt leaves no partial state
priority: P1
effort: M
status: done
classes: safety, ux
touches: src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/blood.py, src/anesthesia_sim/core/agent_simulation_validation.py, src/anesthesia_sim/app/simulation_view.py, docs/MODEL.md
added: 2026-08-24
closed: 2026-09-02
pr: 204
---

**Problem.** PL-018 made a failed step halt the run and warn that "the values
shown may not reflect a completed step", but the metrics and chart traces are
still drawn at whatever value the abandoned step left them:
`AgentUptakeSystem.advance()` applies five sub-exchanges in sequence and a
guard can reject the fifth after the first four have mutated state.

**Why it matters.** `CLAUDE.md` prefers an obvious failure state to a
plausible-looking number when correctness cannot be established. The numbers
left on screen are an artifact of the order the operators were applied in -
step 5 having run against step 2's output - not evidence of where the model
broke down.

**Decision (2026-08-24).** Roll the step back rather than treat the display.
A run's dynamic state is eight floats, so rollback is cheap and explicit, and
the display question dissolves: the metrics keep showing the last completed
step, which is a real solution of the model. The diagnosis moves into the
`SimulationNumericalError` message, where it can name the invariant and the
step size a reader can act on.

**The state inventory.** The brief originally costed the transactional option
as "capturing and restoring six compartments plus the accounting validator on
every step", and that estimate is what pushed the item toward the two cheaper
options. It is wrong. Everything `advance()` mutates is eight floats:

| Where | Field |
| --- | --- |
| `BreathingCircuit` | `circuit_concentration_fraction` |
| `AlveolarCompartment` | `agent_amount_l` |
| `TissueGroup` (x3) | `agent_amount_l` |
| `VenousBloodCompartment` | `agent_amount_l` |
| `AgentSimulationValidator` | `delivered_agent_l`, `exhausted_agent_l` |

Everything else on those dataclasses is a setting or a parameter that a step
never touches. Eight reads before `_advance_step` and eight writes on the
failure path is free against a 0.1 s step, and it is explicit rather than
clever, which is what the safety-critical standard asks for.

**Rejected, both for the same reason.** Keeping the banner as the only cue,
and blanking or greying the metrics. Each leaves `core/` holding a state that
is not a solution of the model, and leaves the run resettable but not
resumable. The brief credited the partial numbers with teaching value; they do
not have it. A partially applied step is an artifact of the order the five
sub-exchanges were applied in — step 5 having run against step 2's output —
not evidence of where the model broke down. The diagnosis belongs in the
`SimulationNumericalError` message, where it can say which invariant failed at
which step size, and where a reader can act on it.

**The one real risk in rollback** is a snapshot that silently stops covering
everything: a field added to a compartment later, with no matching capture,
would leave a partial restore that looks like a complete one. That is why
capture belongs on each compartment rather than in `AgentUptakeSystem` — a
missing field is then a local, reviewable omission — and why the regression
test asserts bit-identical state rather than approximate agreement.

**Where.** `src/anesthesia_sim/core/uptake_system.py` (`advance`,
`_advance_step`) and the five classes holding dynamic state:
`src/anesthesia_sim/core/circuit.py`, `src/anesthesia_sim/core/alveolar.py`,
`src/anesthesia_sim/core/tissue.py`, `src/anesthesia_sim/core/blood.py`,
`src/anesthesia_sim/core/agent_simulation_validation.py`. Also
`src/anesthesia_sim/app/simulation_view.py` and `docs/MODEL.md`.

**First step.** Give each compartment `capture_state()` / `restore_state()`
over its own dynamic fields, rather than reaching into them from
`AgentUptakeSystem`. A field added later without its capture then fails
locally and visibly instead of leaving a partial restore that looks complete.

**Done when.** A failed step leaves every dynamic value bit-identical to its
pre-step value, a regression test asserts that rather than approximate
agreement, the diagnosis has moved into the `SimulationNumericalError`
message, and `docs/MODEL.md` and `advance()`'s docstring stop promising
partial state.

**Outcome (2026-09-02).** Built as decided. Each of the five classes carries
`capture_state()` / `restore_state()` over a frozen state record of its own
(`BreathingCircuitState` and so on); `AgentUptakeSystem.capture_state()`
composes them, and `advance()` captures before the step and restores on any
failure, so the rollback is wider than the guard it was written for — an
accounting failure or a `TypeError` from a later refactor leaves the same
partial step and gets the same treatment. Only a guard reached during the step
is restated as `SimulationNumericalError`; anything else re-raises unchanged,
so a programming error is not dressed up as a modelling failure and
`AgentSimulationValidationError` keeps its type.

One departure from the table above: `AgentSimulationValidator.initial_agent_l`
is captured as well, making nine values rather than eight. It anchors the
current accounting period and only `reset()` writes it, which is what makes it
run state rather than a setting under the same rule every other compartment
follows — and capturing it means the snapshot is self-consistent rather than
resting on an assumption about which methods a step can reach.

The risk named above is guarded deterministically rather than by review:
`tests/unit/test_state_capture.py` classifies every field of every compartment
as run state or setting, and fails when a new field is neither, when
`restore_state()` does not bring back exactly the run-state fields, or when
`reset()` and `capture_state()` disagree about which fields those are. All
three modes were mutation-tested against the finished code.

`docs/MODEL.md` gained a "Step atomicity" section under "Numerical method" and
an invariant beside the step-size one; `PL-KQKM` (MODEL.md's failed-step
paragraph disagreeing with the code) and `PL-YLZQ` (this item's reasoning
living in `docs/WORKING_NOTES.md`) are closed with it, the first because the
paragraph it corrects is now true in the stronger direction and the second
because finishing this item is what emptied that section.
