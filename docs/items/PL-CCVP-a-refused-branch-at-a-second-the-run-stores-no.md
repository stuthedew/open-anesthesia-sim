---
id: PL-CCVP
title: A refused branch at a second the run stores no state for gives the instant in raw seconds ('121 s'), while the other branch refusals give it as the chart's elapsed time
priority: P3
effort: S
status: done
classes: ux
feature: replay-findings
touches: src/anesthesia_sim/app/controller.py, docs/INTERFACE.md, tests/integration/controller, tests/integration/simulation_view/test_simulation_view_branch_refusals.py
added: 2026-11-23
closed: 2026-11-23
pr: 2284
filed-pr: 2271
tests: tests/integration/simulation_view/test_simulation_view_branch_refusals.py::test_a_branch_the_case_refuses_is_reported_and_adds_no_run
---

**Problem.** `core/stored_states.py` raises "this run stores no state at {instant_s} s: ..." when a branch or a replay asks for a second the run holds no state for. The message reaches the branch panel through `refused_branch_notice`. Once `PL-3JTH` (the branch refusals name the on-screen control and the chart's time) merges, every other branch refusal gives its instant through `app/formatting.py`'s `format_elapsed`, as "2m" or "24h", the form the chart's time axis uses. This one still says "121 s", so a learner meets two forms of time in one panel.

**Why it was not fixed in `PL-3JTH`.** `core/` may not import `app/`, so the core message cannot call `format_elapsed`. Two routes: the controller catches the core refusal and re-raises it with the instant formatted, or the elapsed-time format moves to a module both layers may import. The second keeps one home for the format; read `docs/ARCHITECTURE.md` § "Layering" before choosing.

**Done when.** A refused branch at an unstored second names the instant in the same form as the other branch refusals, and a test drives that refusal through the branch panel.

**Done 2026-11-23**, in the same pull request as `PL-3JTH`, because that item's blind review (pass 2, F1) found this refusal contradicting the wording it added to `docs/INTERFACE.md`. `SimulationController._resume_point_at` (`app/controller.py`) catches the stored record's refusal and raises it again in the branch panel's terms: "this run has reached 2m, so it holds no state at 2m1s to branch from; choose an instant it has passed under "From" and press "Branch"". The test of which seconds the run holds stays in `StoredStates.state_at`, so no second copy of it exists. The core message keeps its seconds, because `core/` may not import `app/formatting.py` (`docs/ARCHITECTURE.md` § "Layering"). Other callers of `state_at` were not traced to the screen here.

Regression test: `test_a_branch_the_case_refuses_is_reported_and_adds_no_run` in `tests/integration/simulation_view/test_simulation_view_branch_refusals.py` now drives the refusal through the branch panel and requires "1m30s", the entry's own label. Against the controller before this fix it fails with `AssertionError: assert 'no state at 1m30s to branch from' in 'Branch not opened — this run stores no state at 90 s: ...'`. Documents checked: `docs/INTERFACE.md` (the refusal paragraph, reworded so that it names a control only where another control would open the branch), `docs/ARCHITECTURE.md` (no new module).

**Generator check.** The fact misread is which words a refusal raised under `app/` owes the learner who reads it in a panel. `PL-3JTH`, this item and `PL-72X2` are three instances in the branch refusals, and `PL-8QFW` is a fourth in the refused-setting banner, so this is a generator: a message written for a developer in `core/` or the controller reaches a panel verbatim, through `refused_branch_notice` or `refused_setting_notice` (`app/dashboard_frame.py`). `PL-XWCH` answered the same fact for the failure banners by putting the developer's text behind "Show details". The fix for the class is one shape for both notices, decided once, rather than a rewording of each message; it is not built here.
