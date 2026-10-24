---
id: PL-BM6X
title: The branch panel's refusal notice outlives the case it was about: an agent change on the trunk starts a new case without emitting case_restarted, so 'Select an instant to branch at' stays on screen after the switch (reproduced offscreen by PL-K88Z's inventory)
priority: P2
effort: S
status: ready
classes: defect, ux
feature: one-source-of-truth
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_simulation_view.py
added: 2026-10-19
payoff: after an agent change the branch panel no longer shows a notice about the case before
verify: grep -q 'def test_an_agent_change_clears_the_fork_refusal_notice' tests/integration/test_simulation_view.py
---

**Problem.** The branch panel's refusal notice outlives the case it was about: an agent change on the trunk starts a new case without emitting case_restarted, so 'Select an instant to branch at' stays on screen after the switch (reproduced offscreen by PL-K88Z's inventory)

**Why it matters.** After the learner changes the agent, the branch panel still says "Select an instant to branch at" from the case before. The notice describes a case that is no longer on screen. That is the stale-state failure behind about 36 of the simulator's 91 product defects since 2026-09-25 (`PL-R4Y2`).

**Done when.** Changing the agent on the trunk clears the branch panel's refusal notice, whichever path starts the new case. A test named `test_an_agent_change_clears_the_fork_refusal_notice` in `tests/integration/test_simulation_view.py` fails on today's code and passes after the fix. `PL-WM5P`, which extends `PL-X7D5`'s single-writer guard to every surface that states run state, covers this kind of defect in general. This item fixes the reproduced instance, and can land before it or with it.

**Checked 2026-10-24.** Nothing under `src/` has changed since `PL-K88Z` reproduced this offscreen on 2026-10-23. `run_view.py` still emits `case_restarted` on a restart only, and `simulation_view.py` clears the panel from `_handle_case_restarted`.
