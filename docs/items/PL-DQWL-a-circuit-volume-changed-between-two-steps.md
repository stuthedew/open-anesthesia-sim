---
id: PL-DQWL
title: A circuit volume changed between two steps leaves the run's uptake system off the state its record stores for the second it has reached, so a deep copy or a pickle of that run is refused with a message that names resume_at, and a branch opened at that second would start from a different circuit fraction than the parent now holds; the app offers no mid-run volume control yet (found at blind review of PL-HXNL)
status: untriaged
feature: replay-findings
touches: src/anesthesia_sim/core/simulation.py, src/anesthesia_sim/core/circuit.py
added: 2026-11-22
---

**Problem.** A circuit volume changed between two steps leaves the run's uptake system off the state its record stores for the second it has reached, so a deep copy or a pickle of that run is refused with a message that names resume_at, and a branch opened at that second would start from a different circuit fraction than the parent now holds; the app offers no mid-run volume control yet (found at blind review of PL-HXNL)

**Found by.** The first blind review pass on `PL-HXNL`, 2026-11-22. The
reviewer stepped a sevoflurane run 20 s, then called
`system.circuit.set_circuit_volume` with 1.5 times the volume. The circuit
keeps its agent amount, so its fraction changes, and the system no longer
stands at the state that `StoredStates` holds for 20 s. `advance()` still
steps. Since `PL-HXNL`, `SimulationState.__setstate__` runs the constructor
with the stored states as the opening record, and the constructor's
`stands_at` check refuses the copy with a message that tells the caller to use
`resume_at`, which is not the cause.

**Why it matters.** No learner can reach it today: the interface sets the
circuit volume only when a run is built. A mid-run volume control, or a
branch opened at that second, would meet it. The refusal is the safe side of
the choice, so a learner would see an error rather than a wrong value.

**What a fix has to decide.** Whether a volume change between steps should be
recorded as a setting change, so the record holds the state the next step
starts from, or refused once a run has stepped.

## What was built (2026-11-22)

The fix refuses the change rather than recording it as a setting change.
`docs/MODEL.md` § "The four controls" calls the circuit volume and the
alveolar gas volume fixed parameters that are not controls, and
`docs/INTERFACE.md` says they cannot be changed during a run. Recording a
mid-run volume change would be a new control, which no teaching case has asked
for (`PL-GYH2`).

1. `SimulationState.advance` now checks, before it steps, that the uptake
   system still stands at the state the record holds for the second the run
   has reached (`AgentUptakeSystem.stands_at`, the check a branch's opening
   record already passes). If it does not, the step is refused with a
   `SimulationConfigurationError` that names the circuit volume, the alveolar
   gas volume and a compartment's contents, and says to reset the run or build
   a new one. Nothing moves: the clock, the record and the system stay as they
   were.
2. The check covers any change that moves the system off its record, not only
   the circuit volume: the alveolar gas volume, and contents written back with
   `restore_state`, are refused the same way. A control (fresh gas flow, the
   dial, ventilation, cardiac output) changes the next step's inputs and not the
   stored state, so it still takes effect at the next step.
3. The constructor's refusal of an opening record the system does not stand at
   now says, beside the branch's route through `resume_at`, that a copied or
   loaded run fails it when its circuit volume, alveolar gas volume or contents
   changed after its last step. That was the misleading message this item
   named.
4. `reset()` still applies a changed volume: the reset run's stored states
   match a fresh run built with the new volume, second for second.

**What the check costs.** `AgentUptakeSystem.stands_at` writes the stored state
into the system, compares, and puts back what it held. Measured in this
container on 2026-11-22, `SimulationController.advance` on a running
sevoflurane run took a median of 16.4 µs per step before the change and 28.5
µs after it, over five runs of 300 steps each. `MAXIMUM_STEPS_PER_TICK` is
1 000, so the largest tick now takes about 29 ms of its 100 ms, and the fastest
offered rate, 300 times real time, takes 30 steps. `docs/INTERFACE.md`'s figure
of about 53 µs per step, measured on 2026-10-26 on another machine, still
leaves 1 000 steps under the tick. A cheaper check would compare a copy of the
volumes with the system's, which is a second list of the values that turn a
fraction into an amount, and it would miss the next one added.

**The regression tests fail against the code before the fix.** With
`src/anesthesia_sim/core/simulation.py` stashed back to `origin/main`
949c26a6, `uv run pytest -q -p no:randomly tests/unit/test_simulation.py -k
"between_two_steps or put_back or reset_applies or cannot_be_copied"` gave 5
failed and 2 passed. The three step tests failed with "DID NOT RAISE
SimulationConfigurationError", and the two copy tests with "Regex pattern did
not match". The two that passed are the control test and the reset test, which
hold behavior the fix keeps.

**Docs checked.** `docs/MODEL.md` § "The four controls" (the two volumes
are fixed, unchanged and now enforced), `docs/INTERFACE.md` § "What is not
bounded this way" (one sentence added naming the refusal), `docs/VERIFICATION.md`
§ "Step atomicity" (about a rollback inside a step, which this does
not change), `docs/ARCHITECTURE.md` (no line describes this check).
