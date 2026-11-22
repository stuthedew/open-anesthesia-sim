---
id: PL-DQWL
title: A circuit volume changed between two steps leaves the run's uptake system off the state its record stores for the second it has reached, so a deep copy or a pickle of that run is refused with a message that names resume_at, and a branch opened at that second would start from a different circuit fraction than the parent now holds; the app offers no mid-run volume control yet (found at blind review of PL-HXNL)
status: done
feature: replay-findings
touches: src/anesthesia_sim/core/simulation.py, tests/unit/test_simulation.py, docs/INTERFACE.md, src/anesthesia_sim/app/chart_frame.py, tests/unit/test_record_writes.py
added: 2026-11-22
closed: 2026-11-22
pr: 2244
tests: tests/unit/test_simulation.py::test_a_circuit_volume_changed_between_two_steps_refuses_the_next_step, tests/unit/test_simulation.py::test_an_alveolar_gas_volume_changed_between_two_steps_refuses_the_next_step, tests/unit/test_simulation.py::test_contents_put_back_to_an_earlier_second_refuse_the_next_step, tests/unit/test_simulation.py::test_a_run_whose_circuit_volume_changed_after_its_last_step_cannot_be_copied
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

**Generator check.** The fact is which state a run's record holds for the
second it has reached, which the run-is-its-definition rule states: one stored
state per second, written by the step. This item was filed by the blind review
of `PL-HXNL`, which made copies run the constructor's check, so it is a found
gap in that check's reach rather than a fix that failed to hold, and no
`reenters:` is recorded.

## What was built (2026-11-22)

The fix refuses the change rather than recording it as a setting change.
`docs/MODEL.md` § "The four controls" calls the circuit volume and the alveolar
gas volume fixed parameters that are not controls, and `docs/INTERFACE.md`
says they cannot be changed during a run. Recording a mid-run volume change
would be a new control, which no teaching case has asked for (`PL-GYH2`).

1. `SimulationState` keeps the state its next step starts from, as the system
   held it when the run last stopped: its case state and compensation terms,
   read when the run opens, after each step and after a reset
   (`_resting_state`). `advance()` compares the system with it before it
   steps. If they differ, the step is refused with a
   `SimulationExecutionError` that names a volume or a compartment's contents
   and says to reset the run or build a new one. Nothing moves, and each later
   step is refused the same way until a reset.
2. The check covers any change that moves the state: the circuit volume and
   the alveolar gas volume while their compartment holds agent, and contents
   written back with `restore_state`. A control changes the next step's
   inputs and not the state, so it is accepted. So is a volume change while
   the compartment is empty, because its fraction stays 0 and the record
   still holds the run's state. The controller refuses a step after any
   setting change it did not record (`PL-XRN8`, checked by hand on
   2026-11-22: a circuit volume set through the controller's system after
   3 s gave "A setting was changed on the simulation core without
   SimulationController recording it").
3. The constructor's refusal of an opening record the system does not stand at
   now says, beside the branch's route through `resume_at`, that a copied or
   loaded run fails it when its circuit volume, alveolar gas volume or contents
   changed after its last step. That was the misleading message this item
   named.
4. `reset()` still applies a changed volume: the reset run's stored states
   match a fresh run built with the new volume, second for second.

**Blind review, two passes, on a first design.** The first design checked
`AgentUptakeSystem.stands_at` before each step, which writes the record's state
into the system and compares. Both passes rejected it, and the full suite
agreed (3 failed). Pass 1 F1 (should-fix): a system whose amounts do not
survive a fraction round trip in the last bit would be refused at its first
step. Pass 1 F2 (should-fix) and pass 2 F3 (optional), the same finding: the
check could not see a volume change in an empty compartment, so the docs
overclaimed. Pass 1 F3 (optional): the write and compare cost about 12 µs a
step. Pass 2 F1 (blocking): the write ran each compartment's guard outside the
step, so an injected compartment refusal escaped as the wrong exception, which
broke three failed-step tests. Pass 2 F2 (should-fix): a refusal that repeats
on every later step must be a `SimulationExecutionError`, as the controller's
matching check is. The second design above answers each: it writes nothing,
raises `SimulationExecutionError`, and the docs now say what it enforces and
name the controller's check for the rest.

**Blind review, two passes, on the second design.** Pass 1 F1 (optional):
the sentence added to `docs/INTERFACE.md` said the controller refuses a step
after any settings change it did not record, but a control change through the
controller adopts the whole settings record, a directly written volume
included. Fixed: the sentence now says the controller refuses a step when the
core's settings differ from the ones it last recorded, and the adoption is
filed as `PL-S8FM`. Pass 1 F2 (optional): a copy of a run opened from a system
whose amounts were written directly can be refused before its first step,
with a message that names a change that never happened. Fixed in part: the
message now says "for example". Placing the system at its stored state when
the run opens removed the refusal but broke a failed-step test, so the rest is
filed as `PL-P5W1`. Pass 1 F3 (optional): the step's refusal named only a
volume or contents change, although it also compares the agent accounting.
Fixed: the message names the accounting and a step taken on the uptake system
directly. Pass 2 F1 (optional): `docs/INTERFACE.md`'s paragraph on the
F_A/F_I crossing ceiling, and the matching docstring in `app/chart_frame.py`,
still said a circuit volume doubled between two steps doubles the ratio on the
chart. Fixed: both now say a run refuses that step while the circuit holds
agent, and the ceiling keeps its margin for a drawn column that lands on a
later state.

**What the check costs.** It reads the case state (1.2 µs) and the
compensation terms (0.6 µs) twice per step, measured in this container on
2026-11-22 as the minimum of ten runs of 2 000 calls. That is about 4 µs a
step, or 4 ms over the 1 000 steps of the largest tick. Whole-step timings in
this container varied from 37 to 55 µs between runs of the same code, too much
to resolve a difference that small.

**The regression tests fail against the code before the fix.** With
`src/anesthesia_sim/core/simulation.py` replaced by `origin/main` 949c26a6's,
`uv run pytest -q -p no:randomly tests/unit/test_simulation.py -k
"between_two_steps or put_back or reset_applies or cannot_be_copied or
holds_no_agent or already_holding"` gave 5 failed and 4 passed. The three
step tests failed with "DID NOT RAISE SimulationExecutionError", and the two
copy tests with "Regex pattern did not match". The four that passed hold
behaviour the fix keeps: a control, a reset, an empty compartment, and a run
opened from a system already holding agent.

**Docs checked.** `docs/MODEL.md` § "The four controls" (the two volumes are
fixed, unchanged), `docs/INTERFACE.md` § "What is not bounded this way" (one
sentence added on the run's refusal and the controller's), `docs/VERIFICATION.md`
§ "Step atomicity" (about a rollback inside a step, which this does not
change), `docs/INTERFACE.md`'s paragraph on the F_A/F_I crossing ceiling and
`app/chart_frame.py`'s matching docstring (both corrected),
`docs/ARCHITECTURE.md` (no line describes this check).
