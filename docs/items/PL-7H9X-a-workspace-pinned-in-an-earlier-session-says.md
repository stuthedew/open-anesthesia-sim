---
id: PL-7H9X
title: A Workspace pinned in an earlier session says 'Run 1 is not open.' while this session's Run 1 is open and named directly above it
status: untriaged
feature: interface-matches-its-spec
added: 2026-11-21
---

**Problem.** A Workspace pinned in an earlier session says 'Run 1 is not open.' while this session's Run 1 is open and named directly above it

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). A run's identity holds the session and the run's number, and `Workspace.shown_runs` compares both, so a Workspace pinned in an earlier session correctly shows no run. The name on screen is the number alone (`run_label` in `app/dashboard_frame.py`). Reproduction: pin the Default Workspace to `RunId(SessionToken("0" * 32), 1)`, open the window, take a branch in the Induction Workspace and return to Default. The open runs are 1 and 2. The run rows and readouts say "Run 1" and "Run 2", and all four Areas say "Run 1 is not open." and "This Workspace is pinned to Run 1, so its Views show no run." `test_a_pinned_run_that_is_not_open_is_stated_in_every_area_and_no_other_run_is_shown` checks this wording.

**Why it matters.** A learner who pinned a Workspace, closed the simulator and opened it again reads "Run 1 is not open." directly under the readouts of a run called Run 1. `docs/INTERFACE.md` gives this confusion as its reason for never reusing a run's name inside a session.

**Decided here, as a placeholder** (wording, 2026-11-21): when the pinned run belongs to an earlier session, the notice says so, for example "This Workspace is pinned to a run from an earlier session, which is not open." It does not print that run's number.

**Done when.** An Area of a Workspace pinned in an earlier session names no run number that an open run carries, and the test above checks the new wording.
