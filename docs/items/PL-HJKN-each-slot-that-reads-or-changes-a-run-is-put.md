---
id: PL-HJKN
title: Each slot that reads or changes a run is put behind the halt gate by hand, so a slot that reads a refusing snapshot outside it raises out of the slot with no halt stated: six members from 2026-09-02 to 2026-10-12, four in two days
priority: P1
effort: M
status: done
classes: defect, refactor
feature: defect-review-2026-10
milestone: v0.6.9
touches: src/anesthesia_sim/app/halt_gate.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/controller.py, tests/integration/test_simulation_view.py, tests/integration/test_controller.py, tests/unit/test_halt_gate.py, docs/ARCHITECTURE.md, docs/MODEL.md
deferred-from: v0.7.0 - recorded as a generator head by PL-R4Y2's defect review on 2026-10-25; each member's safety finding was filed and placed by its own triage, and this head's work is the structure that stops the next one
added: 2026-10-25
closed: 2026-10-25
pr: 1831
payoff: a slot added later that reads a run outside the halt gate fails a test, so a refusing snapshot never escapes a slot with the run still reading Paused
verify: grep -q 'def test_every_slot_that_touches_a_run_passes_the_halt_gate' tests/integration/test_simulation_view.py
root-cause-of: PL-YK2V, PL-7DJK, PL-V2HC, PL-08SS, PL-F2T2, PL-M3M2
generator: spent - every slot of RunView and SimulationView passes halt_gate, and test_every_slot_that_touches_a_run_passes_the_halt_gate fails on a new callback, signal keyword or Qt override that bypasses it
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

`test_every_slot_that_touches_a_run_passes_the_halt_gate` parses both modules. A method of the view passes wherever it is handed, if it is gated. Handed to `.connect`, every other callback bypasses the gate, other than a `partial` of a gated method: a lambda, a bare function, another object's slot and a slot reached through an attribute of the view. Handed to any other call, a lambda or a local function bypasses it too, unless the call is to one of the view's own methods, which runs it at once. A keyword argument named for a Qt signal, such as `clicked=`, and an argument after the first to `singleShot`, `callLater`, `addAction` or `QShortcut`, are judged as `.connect`'s argument is. A callback inside a tuple, list, dict or starred argument is judged too, and a method that overrides one of Qt's own, such as `keyPressEvent`, must pass the gate. Each bypass must be listed in the test's exemptions, keyed by the callback's source text, with its reason: Qt's `dialog.deleteLater`, `_trunk_reset_question` and `_open_runs`, which return a value, the tab strip's `lambda: self.workspaces`, and the two `HaltRestatement` restatements, which run inside the halt path. An exemption that is no longer handed out, or that now passes the gate, fails too.

**Regression evidence, 2026-10-25.** With `run_view.py` and `simulation_view.py` taken from `origin/main` and the new tests kept, `uv run pytest tests/integration/test_simulation_view.py -k halt_gate` fails with `AssertionError: slots that bypass the halt gate:`, listing 29 bypasses, the first `RunView: self._agent_dropdown.currentIndexChanged.connect(self._handle_agent_change): _handle_agent_change does not pass the gate`. With `run_view.py` alone taken from `origin/main`, `-k no_try_guarded` fails with `assert False is True` on `controller.has_failed`: Pause raised, and the run never halted. Both pass on this branch, and so do the other 308 tests in that file.

**Blind review, 2026-10-25.** The two passes returned three findings. Both passes found the first defect below, so there are two defects, and both are fixed on this branch.

- Both passes found that a nested gate halted twice. When a gated slot calls another gated slot, as `_handle_fork` calls `present`, and stating the halt raises (`PL-TLH4`), the outer gate caught the halt's own exception and stated the whole halt again with it as the reason. `halt_gate` now marks an exception that `halt_for_slot` raised, and each outer gate passes it on. Before the fix, `uv run pytest tests/unit/test_halt_gate.py -k nested` failed with `Left contains one more item: 'the dials could not be written'`.
- Pass 1 found that the structural test let `connect(run.controller.pause)` through, and any lambda handed to a call other than `.connect`, such as `QTimer.singleShot`. The test now treats both as bypasses, as the paragraph above says. `test_the_halt_gate_check_finds_each_way_around_the_gate` runs the check on a class written with bypasses and with callbacks that pass. That class then held nine bypasses and five callbacks that pass. The check as first committed, applied to the same class by a scratch script, found 6 of the 9. It missed `button.clicked.connect(run.controller.pause)`, `timer.singleShot(0, lambda: self._gated())` and `timer.singleShot(0, local)`.

**Adversarial review, 2026-10-25.** Three passes looked for different kinds of defect: lifecycle and state, coverage and tests, and the repository's rules, the documents and the screen after a halt. Each pass reproduced its findings with a scratch script.

- A raise in any slot of `SimulationView` now halts every run, and records that the dashboard failed, which withdraws every branch point until Reset. Two passes found this. It is kept: after an unexplained failure in the dashboard that draws every run, a branch drawn by the same dashboard could fail the same way, so withdrawing the offer is the obvious failure state. The other choice was to record a failed frame only from `present` and `render_tick`. That would leave branching offered after the marks editor or a Workspace switch had failed. The refusal used to say that the frame failed, which was false for such a slot. It now says that the dashboard failed.
- When `present_halt` raised, `_halt_run` asked for no frame, so the dashboard never restated "Branch here" over the halted trunk. It now asks for the frame either way.
- When the new-case question could not be built, the pending agent stayed recorded, so the agent selector put back every pick, even after Reset. The pending agent is now recorded only once the dialog is built.
- A refused Reset halted its run by hand inside the gated Reset slot, so when showing that halt raised, the gate halted the run again. The refusal now goes on to the gate, which is the only place in `RunView` where an exception becomes a halt.
- One raise in `_follow_chart`, set off while the halt drew its frame, started the halt again inside itself, 21 times and 6 deep. `SimulationView.halt_for_slot` now passes on an exception raised while every run is being halted.
- Docstrings that the change had made stale were corrected: the playback rate, `SimulationController.agent_id`, `_show_running_agent`, the two restatements, a test's docstring and the package map. `halt_gate`, `RunView.halt_for_slot` and `_halt_run` now say what they raise.

Each regression test failed on the code before its fix, run from a worktree of the branch at that point with the new test file: `-k names_the_dashboard` with `assert 'the frame th...the run first' == 'the dashboar...the run first'`, `-k withdraws_branch_here` with `assert False is True` on `here.isHidden()`, `-k selector_working_after_reset` with `assert 'sevoflurane' == 'desflurane'`, `-k halts_the_run_once` with `assert ['ValueError'] == ['SimulationConfigurationError']`, and `-k does_not_start_the_halt_again` with `assert 6 == 1`.

The coverage pass found no path in today's code by which Qt calls code that reads or changes a run without the gate. Of 33 mutants that change behaviour, 32 failed a test, and one is equivalent. It found two shapes that the check could not see, in code nobody has written yet. A slot handed to `QShortcut`, `addAction` or `singleShot`, or named as a constructor's signal keyword, was judged as a value, and so was a callback inside a tuple or a starred argument. A Qt override such as `keyPressEvent` was not looked at. Both are now checked, as the test paragraph above says. The bypass class now holds 16 bypasses. The check as committed before this fix found 9 of them, missing the override and the six new call shapes. A unit test also could not tell a keyword-only parameter from a positional one when the gate trims a signal's arguments. The mutant that counts keyword-only parameters as positional, `return len(kinds)` in `_positional_capacity`, survived the whole suite. `test_a_keyword_only_parameter_takes_no_signal_argument` now fails on it. The check still reads only each class's own source, so it cannot see a slot that a function outside the class connects, or a callback held in a variable before it is passed on.

**Close-out audit, 2026-10-25.** `bin/docket verify --self PL-HJKN` returned `ACCEPT` against `origin/main`, with `make check` passing. Its notes named the paths outside `touches` that this branch's own widening of `touches` declares, and `docs/MODEL.md` as a protected path that the branch changes. The change to `docs/MODEL.md` is one table row, which says how a halted run's agent selector is put back. No file this branch changes is one that mutmut mutates.
