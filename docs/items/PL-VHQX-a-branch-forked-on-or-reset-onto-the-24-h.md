---
id: PL-VHQX
title: A branch forked on, or reset onto, the 24 h supported run length shows the limit banner's "Reset to start a new run.", and `start()` says "reset it to start a new run", but Reset returns that branch to the same 24:00:00 fork, so the only way out the screen names leads straight back
priority: P3
effort: S
status: ready
classes: ux, defect
feature: replay-findings
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/controller.py, tests/unit/test_dashboard_frame.py, tests/integration/test_controller.py
added: 2026-10-25
payoff: the way out the screen names from the supported-run-length stop actually leaves it on a branch
verify: grep -q 'def test_a_branch_on_the_supported_run_length_is_not_sent_to_a_reset_that_returns_it_there' tests/integration/test_controller.py
---

**Problem.** `SUPPORTED_LIMIT_NOTICE_TEMPLATE` (`dashboard_frame.py`) ends with "Reset to start a new run." for every run. `SimulationController.start()` (`controller.py`) says the same. A branch's Reset returns it to its fork (`controller.py`), and since `PL-5291` a branch on the limit stays there, stopped. `_resume_point` (`controller.py`) does not refuse a fork that leaves no step to take.

**Why it matters.** A learner who forks at a dial change made after the trunk reached 24 h gets a run that can never step. The banner then sends them to Reset, which shows them the same banner again. For a branch forked earlier, "start a new run" also misdescribes what Reset does, because Reset returns the branch to its fork. A fix refuses a fork with no step left, or words the exit for a branch, or both.

**Done when.** A branch that has no step left is never sent to a Reset that returns it to the same limit: the fork is refused, or the banner and `start()` name an exit that works for a branch. `tests/integration/test_controller.py` has `test_a_branch_on_the_supported_run_length_is_not_sent_to_a_reset_that_returns_it_there`.

**Found by.** `PL-TBQS` reviewer replay on #568, r05 F1 (r04 F4's Start half was fixed by `PL-5291`). Checked against main 2026-10-25 by reading the code and `tests/integration/test_controller.py`, whose helper `_assert_reads_as_stopped_at_the_supported_run_length` asserts this banner for a branch on the limit.
