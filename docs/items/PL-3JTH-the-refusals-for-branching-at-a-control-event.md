---
id: PL-3JTH
title: The refusals for branching at a control event or a mark, which the view shows word for word after "Setting refused —", name the methods resumed_at, resumed_at_mark and resumed_here and print raw float seconds and Python lists such as [0.0, 45.300000000000004] s, where the selector and marks panel say "45.3s, on your mark" and "1m30s"
priority: P3
effort: S
status: ready
classes: ux
feature: replay-findings
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/dashboard_frame.py, tests/integration/test_controller.py, tests/unit/test_dashboard_frame.py
added: 2026-10-25
payoff: a learner whose branch press is refused reads instants in the panel's own form, not method names and raw floats
verify: grep -q 'def test_a_refused_branch_names_the_on_screen_control_and_a_formatted_instant' tests/integration/test_controller.py
---

**Problem.** `_resume_point_at` and `_resume_point_at_mark` raise messages that name code methods and print unformatted seconds (`src/anesthesia_sim/app/controller.py`). `SimulationView._handle_fork` and `_handle_here_fork` put the message on screen through `refused_setting_notice` (`src/anesthesia_sim/app/simulation_view.py`). That adds the prefix "Setting refused — " (`src/anesthesia_sim/app/dashboard_frame.py`), although no setting was involved. The instants are not passed through `format_elapsed`, so they do not match the labels beside them.

**Why it matters.** This shows only when a press races a change that the panel has not yet redrawn. When it does, the learner reads method names they cannot act on and numbers like 45.300000000000004 beside a panel that says 45.3s. The fix is a branch-refusal wording that names the on-screen controls and formats each instant as the panel does.

**Done when.** A refused branch press shows a message that names the on-screen control, formats each instant with `format_elapsed`, and is not prefixed "Setting refused". `tests/integration/test_controller.py` has `test_a_refused_branch_names_the_on_screen_control_and_a_formatted_instant`.

**Found by.** `PL-TBQS` reviewer replay on #1451, finding 1451 r01 F2, and the `PL-ZWXD` addendum entry for #1451, checked against main on 2026-10-25 by reading the code.
