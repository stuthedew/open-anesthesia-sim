---
id: PL-7H9X
title: A Workspace pinned in an earlier session says 'Run 1 is not open.' while this session's Run 1 is open and named directly above it
priority: P3
effort: S
status: done
classes: defect
feature: interface-matches-its-spec
milestone: v0.6.19
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/view_registry.py, src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/workspace_tabs.py, docs/INTERFACE.md, tests/unit/test_dashboard_frame.py, tests/unit/test_view_registry.py, tests/integration/test_workspace_tabs.py, tests/integration/test_workspace_saving.py, tests/integration/test_layout_keyboard.py
added: 2026-11-21
closed: 2026-11-21
pr: 2191
payoff: A learner who reopens the simulator is not told that Run 1 is not open under the readouts of a run called Run 1
tests: tests/unit/test_dashboard_frame.py::test_a_pinned_run_of_an_earlier_session_is_named_without_its_number, tests/unit/test_dashboard_frame.py::test_a_pinned_run_is_named_only_in_a_session_given_by_its_token, tests/integration/test_workspace_tabs.py::test_a_pinned_run_that_is_not_open_is_stated_in_every_area_of_the_runs, tests/unit/test_view_registry.py::test_the_pinned_run_notice_is_titled_with_the_name_it_is_given, tests/unit/test_view_registry.py::test_a_name_that_starts_a_sentence_has_only_its_first_letter_raised
---

**Problem.** A Workspace pinned in an earlier session says 'Run 1 is not open.' while this session's Run 1 is open and named directly above it

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). A run's identity holds the session and the run's number, and `Workspace.shown_runs` compares both, so a Workspace pinned in an earlier session correctly shows no run. The name on screen is the number alone (`run_label` in `app/dashboard_frame.py`). Reproduction: pin the Default Workspace to `RunId(SessionToken("0" * 32), 1)`, open the window, take a branch in the Induction Workspace and return to Default. The open runs are 1 and 2. The run rows and readouts say "Run 1" and "Run 2", and all four Areas say "Run 1 is not open." and "This Workspace is pinned to Run 1, so its Views show no run." `test_a_pinned_run_that_is_not_open_is_stated_in_every_area_of_the_runs` checks this wording.

**Why it matters.** A learner who pinned a Workspace, closed the simulator and opened it again reads "Run 1 is not open." directly under the readouts of a run called Run 1. `docs/INTERFACE.md` gives this confusion as its reason for never reusing a run's name inside a session.

**Decided here, as a placeholder** (wording, 2026-11-21): when the pinned run belongs to an earlier session, the notice says so, for example "This Workspace is pinned to a run from an earlier session, which is not open." It does not print that run's number.

**Done when.** An Area of a Workspace pinned in an earlier session names no run number that an open run carries, and the test above checks the new wording.

**Built 2026-11-21.** `pinned_run_label` in `app/dashboard_frame.py` names a Workspace's pinned run from the pin and the token of the session that is running. A run of an earlier session is called "a run from an earlier session", without its number. The Area's notice, the Area's header and the Unpin entry of the Workspace tab's menu all take the name from it. The notice reads "A run from an earlier session is not open." and "This Workspace is pinned to a run from an earlier session, so its Views show no run. Unpin it from the Workspace's tab to show the runs that are open." The wording is a placeholder. A run of this session that has closed keeps its name ("Run 2 is not open."), because no number is given out twice in a session. `docs/INTERFACE.md` says so beside its description of the pin.

**Generator check.** One-off. The fact is which session a run's number belongs to. `run_label` renders the number alone, which is right for an open run, and the pin was the one caller that can hold a run of another session. Found by `PL-5FMC`, the check of the interface documents that the project owner asked for.

**Blind review, 2026-11-21.** Pass 1 found that the first version worked out the running session from the open runs, so with no run open it still gave the earlier session's number. The function now takes the session's own token (`RunIdentities.session`), and `WorkspaceTabs` and `tab_operations` are given it. A test reads the Unpin entry with no run open.
