---
id: PL-TPBH
title: While the trunk-Reset question (or a Workspace question) is open, the run behind it keeps stepping at the selected rate, and the window-modal dialog blocks the Pause button, so at 300× a learner who reads the question for ten seconds watches fifty simulated minutes pass that they cannot stop
priority: P3
effort: S
status: done
classes: defect
feature: replay-findings
milestone: v0.6.11
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/workspace_tabs.py, src/anesthesia_sim/app/qt_widgets.py, docs/MODEL.md, tests/integration/test_simulation_view.py
added: 2026-10-25
closed: 2026-10-31
pr: 1908
payoff: a learner reading a Reset question returns to the case where they left it, instead of finding that minutes of simulated time passed while the dialog blocked Pause
verify: grep -q 'def test_the_run_does_not_advance_while_a_reset_question_is_open' tests/integration/test_simulation_view.py
---

**Problem.** `NewCaseDialog` is window-modal (`qt_widgets.py`) and is shown with `open()` (in `run_view.py` for both questions, and likewise in `workspace_tabs.py`). `step_tick` never checks for an open question. `_restate_new_case_question` (`run_view.py`) states the behaviour ("The run is not paused while the question is open") and keeps the dialog's figures current, but no item records a decision to keep it.

**Why it matters.** While the question is open, the learner can neither pause nor change anything, yet the case moves on. At 300× each real second is five simulated minutes. A learner who presses "Keep" returns to a case that has moved past where they were thinking. Whether the run should pause while a question is open is a learner-visible behaviour, so the owner should decide it.

**Done when.** The owner has decided whether a run holds while a Reset or Workspace question is open. The recommendation is that it holds, and resumes as it was when the question closes. On that answer, `tests/integration/test_simulation_view.py` has `test_the_run_does_not_advance_while_a_reset_question_is_open`, which opens the trunk-Reset question on a running trunk and checks that simulated time does not move until the question closes. On the other answer, the decision is recorded in `docs/MODEL.md` and this item is closed with that test name unused.

**Found by.** `PL-TBQS` reviewer replay on #331, `PL-ZWXD`'s entry "a modal dialog does not pause the run". Checked against main 2026-10-25. Reproduced (`scripts/B_modal.py`): with a branch holding work, pressing the running trunk's Reset opened the question, and the trunk advanced from 6.0 s to 7.0 s in one second of wall clock with the dialog still modal.

**Answered 2026-10-31: the runs hold, then resume as they were** (project
owner, 2026-10-31, ratified, "Hold, then resume as it was" on this thread's
decision card, over letting the runs go on stepping).

**Built 2026-10-31.** `RunView.step_tick` takes no step while a predicate set
by `RunView.hold_while` returns True. The dashboard gives every run one
predicate, `SimulationView._a_question_is_open`, which reads the open dialogs
themselves: each run's Reset and new-case dialog, and the Workspace strip's
`question`. So the hold has no state of its own that could drift from the
dialogs, and a question about one run holds every run, since each question
blocks every Pause button. The hold changes nothing in the controller. It only
skips ticks, so the trajectory is the one an immediate answer would give, and
a run resumes in the state and at the playback rate it had. The bookmark
editor is not modal and holds nothing.

Two decisions the build took:

1. **The `PL-WM5P` rewrite of an open question stays**, as a guard. With every
   run held, the figures cannot change while a question is open. Removing the
   rewrite would save one callback per frame, but the question would go stale
   silently if a later change let a run move under it. The two `PL-WM5P` tests
   now move the controller directly instead of through ticks.
2. **The status line still says the run is running while it holds**
   (placeholder, under the 2026-10-18 rule on look and wording). The open
   question covers the window and is the visible reason the clock has stopped,
   and the hold ends when the question does.

**Blind review, 2026-11-01.** Both passes found the same should-fix fault.
The bookmark editor was shown with `QDialog.open()`, which makes a dialog
window-modal. So the editor blocked every Pause button while the runs went on
stepping, and the sentence saying it "is not modal" was false. The editor's
own docstring meant it to be non-modal, so it is now shown with `show()`, and
`test_the_bookmark_editor_is_not_modal_and_holds_no_run` checks that Pause
stays reachable. That test fails on the old `open()` call with "assert not
True" on `isModal()`. Pass 1 also raised an optional point: the status line
says "Running" while the runs hold. It stays as recorded above, a placeholder,
because the open question covers the window and is the visible reason the
clock has stopped.
