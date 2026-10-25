---
id: PL-TPBH
title: While the trunk-Reset question (or a Workspace question) is open, the run behind it keeps stepping at the selected rate, and the window-modal dialog blocks the Pause button, so at 300× a learner who reads the question for ten seconds watches fifty simulated minutes pass that they cannot stop
priority: P3
effort: S
status: ready
classes: defect
feature: replay-findings
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/workspace_tabs.py, tests/integration/test_simulation_view.py
added: 2026-10-25
payoff: a learner reading a Reset question returns to the case where they left it, instead of finding that minutes of simulated time passed while the dialog blocked Pause
verify: grep -q 'def test_the_run_does_not_advance_while_a_reset_question_is_open' tests/integration/test_simulation_view.py
---

**Problem.** `NewCaseDialog` is window-modal (`qt_widgets.py`) and is shown with `open()` (in `run_view.py` for both questions, and likewise in `workspace_tabs.py`). `step_tick` never checks for an open question. `_restate_new_case_question` (`run_view.py`) states the behaviour ("The run is not paused while the question is open") and keeps the dialog's figures current, but no item records a decision to keep it.

**Why it matters.** While the question is open, the learner can neither pause nor change anything, yet the case moves on. At 300× each real second is five simulated minutes. A learner who presses "Keep" returns to a case that has moved past where they were thinking. Whether the run should pause while a question is open is a learner-visible behaviour, so the owner should decide it.

**Done when.** The owner has decided whether a run holds while a Reset or Workspace question is open. The recommendation is that it holds, and resumes as it was when the question closes. On that answer, `tests/integration/test_simulation_view.py` has `test_the_run_does_not_advance_while_a_reset_question_is_open`, which opens the trunk-Reset question on a running trunk and checks that simulated time does not move until the question closes. On the other answer, the decision is recorded in `docs/MODEL.md` and this item is closed with that test name unused.

**Found by.** `PL-TBQS` reviewer replay on #331, `PL-ZWXD`'s entry "a modal dialog does not pause the run". Checked against main 2026-10-25. Reproduced (`scripts/B_modal.py`): with a branch holding work, pressing the running trunk's Reset opened the question, and the trunk advanced from 6.0 s to 7.0 s in one second of wall clock with the dialog still modal.
