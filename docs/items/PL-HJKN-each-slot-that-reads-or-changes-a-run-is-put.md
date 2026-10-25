---
id: PL-HJKN
title: Each slot that reads or changes a run is put behind the halt gate by hand, so a slot that reads a refusing snapshot outside it raises out of the slot with no halt stated: six members from 2026-09-02 to 2026-10-12, four in two days
priority: P1
effort: M
status: ready
classes: defect, refactor
feature: defect-review-2026-10
touches: src/anesthesia_sim/app/halt_gate.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/controller.py, tests/integration/test_simulation_view.py, tests/unit/test_halt_gate.py, docs/ARCHITECTURE.md, docs/MODEL.md
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

**Design, 2026-10-25.** One decorator, `halt_gate` in a new `app/halt_gate.py`, wraps every slot of `RunView` and `SimulationView`. It runs the slot and, on any `Exception`, calls the view's `halt_for_slot(error)`: `RunView` halts its own run (`_halt_run`), and `SimulationView` halts every run (`_halt_every_run`). An exception raised by the halt itself still escapes after the halt is shown, as `PL-TLH4` decided. The wrapper passes a slot only as many signal arguments as the slot takes, because PySide6 6.11.2 hands a `*args` wrapper every argument of the signal (measured: a zero-argument slot on `rangeChanged` got two). It marks the function, so a test can ask whether a method is gated.

The hand gates then go, because the decorator does what each did: `_snapshot_for_a_control`, `_reference_snapshot_for_a_control`, the `try` in `present`, `render_tick` and `step_tick`, and `_apply_setting`'s generic branch and its `PL-M3M2` branch. `_apply_setting` keeps its `SimulationConfigurationError` branch, which is a refusal and not a halt. `_start_new_case` keeps its snapshot read before `set_agent`, so a refusing snapshot is a halt and not a refused setting (`PL-V2HC`). An exception does not cross a PySide6 `emit` (measured: the slot's raise is printed and `emit` returns), so `case_restarted` and `presentation_requested` need the gate on their receivers too.

`test_every_slot_that_touches_a_run_passes_the_halt_gate` parses both modules. A method of the view passes wherever it is handed, if it is gated. Handed to `.connect`, every other callback bypasses the gate, other than a `partial` of a gated method: a lambda, a bare function, another object's slot and a slot reached through an attribute of the view. Handed to any other call, a lambda or a local function bypasses it too, unless the call is to one of the view's own methods, which runs it at once. Each bypass must be listed in the test's exemptions, keyed by the callback's source text, with its reason: Qt's `dialog.deleteLater`, `_trunk_reset_question` and `_open_runs`, which return a value, the tab strip's `lambda: self.workspaces`, and the two `HaltRestatement` restatements, which run inside the halt path. An exemption that is no longer handed out, or that now passes the gate, fails too.

**Regression evidence, 2026-10-25.** With `run_view.py` and `simulation_view.py` taken from `origin/main` and the new tests kept, `uv run pytest tests/integration/test_simulation_view.py -k halt_gate` fails with `AssertionError: slots that bypass the halt gate:`, listing 29 bypasses, the first `RunView: self._agent_dropdown.currentIndexChanged.connect(self._handle_agent_change): _handle_agent_change does not pass the gate`. With `run_view.py` alone taken from `origin/main`, `-k no_try_guarded` fails with `assert False is True` on `controller.has_failed`: Pause raised, and the run never halted. Both pass on this branch, and so do the other 308 tests in that file.

**Blind review, 2026-10-25.** The two passes returned three findings. Both passes found the first defect below, so there are two defects, and both are fixed on this branch.

- Both passes found that a nested gate halted twice. When a gated slot calls another gated slot, as `_handle_fork` calls `present`, and stating the halt raises (`PL-TLH4`), the outer gate caught the halt's own exception and stated the whole halt again with it as the reason. `halt_gate` now marks an exception that `halt_for_slot` raised, and each outer gate passes it on. Before the fix, `uv run pytest tests/unit/test_halt_gate.py -k nested` failed with `Left contains one more item: 'the dials could not be written'`.
- Pass 1 found that the structural test let `connect(run.controller.pause)` through, and any lambda handed to a call other than `.connect`, such as `QTimer.singleShot`. The test now treats both as bypasses, as the paragraph above says. `test_the_halt_gate_check_finds_each_way_around_the_gate` runs the check on a class written with nine bypasses and five callbacks that pass. The check as first committed, applied to the same class by a scratch script, found 6 of the 9. It missed `button.clicked.connect(run.controller.pause)`, `timer.singleShot(0, lambda: self._gated())` and `timer.singleShot(0, local)`.
