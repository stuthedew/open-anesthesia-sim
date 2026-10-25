---
id: PL-HJKN
title: Each slot that reads or changes a run is put behind the halt gate by hand, so a slot that reads a refusing snapshot outside it raises out of the slot with no halt stated: six members from 2026-09-02 to 2026-10-12, four in two days
priority: P1
effort: M
status: ready
classes: defect, refactor
feature: defect-review-2026-10
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/controller.py, tests/integration/test_simulation_view.py
deferred-from: v0.7.0 - recorded as a generator head by PL-R4Y2's defect review on 2026-10-25; each member's safety finding was filed and placed by its own triage, and this head's work is the structure that stops the next one
added: 2026-10-25
payoff: a slot added later that reads a run outside the halt gate fails a test, so a refusing snapshot never escapes a slot with the run still reading Paused
verify: grep -q 'def test_every_slot_that_touches_a_run_passes_the_halt_gate' tests/integration/test_simulation_view.py
root-cause-of: PL-YK2V, PL-7DJK, PL-V2HC, PL-08SS, PL-F2T2, PL-M3M2
generator: live - four members on 2026-10-11 and 2026-10-12, the last closed 2026-10-19, and no test or type makes a new slot pass the halt gate
misread: Which slots that read or change a run must pass the halt gate
---

**Problem.** Each slot that reads or changes a run is put behind the halt gate by hand, so a slot that reads a refusing snapshot outside it raises out of the slot with no halt stated: six members from 2026-09-02 to 2026-10-12, four in two days

**The fact the members misread.** A run whose snapshot refuses must be halted, and the halt must be stated on screen. `SimulationView` and `RunView` meet that rule only where a slot routes its reads and writes through the halt gate, and each slot was routed by hand. So each slot left outside was found by a reviewer, one at a time:

- `PL-YK2V`: `_apply_setting` caught a narrower exception class than the timer paths.
- `PL-7DJK`: a refusing display value was shown as a failed step, half-drawn or not at all.
- `PL-V2HC`: the agent-change slot read `snapshot()` on a halted run.
- `PL-08SS`: the two fork slots read the new branch's snapshot outside the gate.
- `PL-F2T2`: the marks dialog's Remove read the reference run's snapshot outside the gate.
- `PL-M3M2`: a raise inside `_apply_setting`'s deferred refresh escaped, because only `apply()` sat inside the `try`.

**Why it is live.** Four of the six were filed on 2026-10-11 and 2026-10-12, and the last closed on 2026-10-19. A search on 2026-10-25 found no test or type that makes a new slot pass the gate: `test_every_dashboard_control_is_restated_on_a_halt` checks what a halt restates, not which slots reach the halt. `PL-X7D5` and `PL-5JTH` gave the screen one writer, which is the other half of the same rule and is spent.

**What to do.** Make the gate structural rather than remembered. For example, connect every slot that touches a run through one wrapper that catches the run's refusal and halts it, and add a test that enumerates the view's connected slots and fails on one that bypasses the wrapper. The test is what makes the next slot fail before review finds it.

**Why it matters.** A refusing snapshot that escapes a slot leaves the run reading Paused with no halt stated, so a learner reads a stale screen as the run's current state. That is the stale-state failure the safety-critical standard names, and each slot left outside the gate has had to be found by review.

**Done when.** Every slot that reads or changes a run passes through one gate by construction, and a test that enumerates the view's connected slots fails on any that bypasses it.

**Generator check.** This item is the head. The members' own safety findings were filed and placed by their own triage, so this item's work is the structure, not a re-fix.
