---
id: PL-3JTH
title: The refusals for branching at a control event or a mark, which the view shows word for word after "Setting refused —", name the methods resumed_at, resumed_at_mark and resumed_here and print raw float seconds and Python lists such as [0.0, 45.300000000000004] s, where the selector and marks panel say "45.3s, on your mark" and "1m30s"
priority: P3
effort: S
status: done
classes: ux
feature: replay-findings
milestone: v0.6.23
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/branch_controls.py, src/anesthesia_sim/app/bookmarks.py, src/anesthesia_sim/app/qt_widgets.py, docs/INTERFACE.md, docs/ARCHITECTURE.md, tests/integration/controller, tests/integration/simulation_view, tests/unit/test_dashboard_frame.py, tests/unit/test_bookmarks.py
added: 2026-10-25
closed: 2026-11-23
pr: 2284
payoff: a learner whose branch press is refused reads instants in the panel's own form, not method names and raw floats
tests: tests/integration/controller/test_controller_branch_refusals.py::test_a_refused_branch_names_the_on_screen_control_and_a_formatted_instant
---

**Problem.** `_resume_point_at` and `_resume_point_at_mark` raise messages that name code methods and print unformatted seconds (`src/anesthesia_sim/app/controller.py`). `SimulationView._handle_fork` and `_handle_here_fork` put the message on screen through `refused_setting_notice` (`src/anesthesia_sim/app/simulation_view.py`). That adds the prefix "Setting refused — " (`src/anesthesia_sim/app/dashboard_frame.py`), although no setting was involved. The instants are not passed through `format_elapsed`, so they do not match the labels beside them.

**Why it matters.** This shows only when a press races a change that the panel has not yet redrawn. When it does, the learner reads method names they cannot act on and numbers like 45.300000000000004 beside a panel that says 45.3s. The fix is a branch-refusal wording that names the on-screen controls and formats each instant as the panel does.

**Done when.** A refused branch press shows a message that names the on-screen control, formats each instant with `format_elapsed`, and is not prefixed "Setting refused". `tests/integration/controller/` has `test_a_refused_branch_names_the_on_screen_control_and_a_formatted_instant`.

**Found by.** `PL-TBQS` reviewer replay on #1451, finding 1451 r01 F2, and the `PL-ZWXD` addendum entry for #1451, checked against main on 2026-10-25 by reading the code.

**Checked 2026-11-22** against `d4e8200`: partly done. Since `PL-SZ6G` (#2180) an instant is a `CaseInstant`, which is an `int`, so a refusal can no longer print a raw float such as 45.300000000000004. The rest is still there. `_refusal_here` and `_resume_point_at_mark` in `app/controller.py` still name `resumed_here`, `resumed_at` and `resumed_at_mark` and print the instant as "{elapsed_s} s" rather than through `format_elapsed`. `SimulationView._handle_fork` still shows the refusal through `refused_setting_notice`, whose `REFUSED_SETTING_TEMPLATE` opens "Setting refused —".

**Done 2026-11-23.** Each branch refusal now names the controls by their words on screen, "From", "Branch" and "Branch here", and gives each instant through `format_elapsed`, as the branch panel does. The view shows a refusal after "Branch not opened —" rather than "Setting refused —", because a refused branch changes no setting. The controls' words moved from `app/dashboard_frame.py` into a new module, `app/branch_controls.py`, which both the panel and the controller read, so a relabelled control cannot leave a refusal naming the old label. The prefix is a wording choice, so it was decided in this item and is a placeholder that a learner's misreading can reopen.

Regression test: `test_a_refused_branch_names_the_on_screen_control_and_a_formatted_instant` in `tests/integration/controller/test_controller_branch_refusals.py`. Run with `src/` from `origin/main` at `b3c16bb3` and the new `app/branch_controls.py` kept, it fails with `assert '"Branch here"' in 'this run is going, ... pause it, and resumed_here branches where it then stands'`. Documents checked: `docs/INTERFACE.md` (§ on branching, gains the refusal paragraph and its developer note), `docs/ARCHITECTURE.md` (lists the new module), `docs/MODEL.md` (holds nothing on branch controls).

**Mutation check.** `bin/docket verify --self PL-3JTH PL-CCVP` reported 41 survivors of the unit tests, all in refusal texts that only the controller and view tests read. One survivor from each of the nine functions was written into the source and run against `tests/integration/controller`, the branch and bookmark view tests and `tests/unit/test_bookmarks.py`. Seven were caught. The two that were not, the branch-of-a-branch refusal and the refusal to remove a mark that is not there, are now pinned whole by `test_a_branch_asked_for_a_branch_of_its_own_is_refused_whole` and `test_removing_a_mark_that_is_not_there_is_refused_in_the_panels_words`, and both mutants are then caught.
