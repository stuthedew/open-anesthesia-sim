---
id: PL-WM5P
title: Extend the run view's single-writer guard (PL-X7D5) to every surface that states run state, so no displayed run state has a second writer
priority: P2
effort: M
status: ready
classes: defect
feature: one-source-of-truth
touches: src/anesthesia_sim/app/, tests/integration/test_simulation_view.py
blocked-by: PL-K88Z
deferred-from: v0.6.0 - placed on ROADMAP.md's v0.6.x one-source-of-truth row, built after v0.6.0 ships (project owner, 2026-10-19, ratified, PL-2LB5)
added: 2026-10-19
payoff: no displayed run state has a second writer that can leave it stale after a halt
verify: grep -q 'def test_every_run_state_surface_outside_the_run_view_reads_alike_on_a_drawn_run_and_a_halted_one' tests/integration/test_simulation_view.py
---

**Problem.** Extend the run view's single-writer guard (PL-X7D5) to every surface that states run state, so no displayed run state has a second writer

**Why it matters.** Step 4 of `PL-2LB5` (the one-source-of-truth design round). Stale state after a halt is the simulator's largest defect cluster, about 36 of 91 product defects since 2026-09-25 (`PL-R4Y2`). Its cause is two writers of one displayed fact. `PL-X7D5` fixed the run view with one writer and a guard that checks every widget by default.

**Done when.** Every surface that states run state has one writer, a guard test fails on a second one, and the inventory (`PL-K88Z`) lists no remaining surface.

**Generator check.** Not a re-entry: it is a step of `PL-2LB5` (the one-source-of-truth design round), which widens the closed `PL-4S6C` at the project owner's ask, and no open generator head names this shape.

**What the inventory left, and what each became (2026-10-25).** `PL-K88Z`'s inventory named five surfaces outside the run view's guard. Each one is now settled:

- The open questions had a second writer. `NewCaseDialog` wrote its title, body and buttons once, when it opened. The trunk's Reset question uses the same dialog, and Reset stays enabled while the runs step, so a running branch left the question stating the instant it had run to when the reader pressed Reset. The run view now rewrites both questions on every refresh through `NewCaseDialog.show_question`, from the state that writes the readouts. `test_an_open_trunk_reset_question_follows_a_running_branch` fails without the fix. The agent selector is locked while a run steps, so the new-case question cannot go stale in the app as built. Its restate is kept so the dialog has one writer whether or not that lock stays, and `test_an_open_new_case_question_follows_a_running_run` checks it by bypassing the lock.
- The comparison panels outside the run view are now checked by `test_every_run_state_surface_outside_the_run_view_reads_alike_on_a_drawn_run_and_a_halted_one`. It changes the marks, the playback rate and the branch panel's refusal, and reads every widget on those surfaces by default, so a new one is checked without being listed. `test_the_surface_guard_fails_on_a_panel_only_a_frame_writes` shows that the guard fails on a panel that only a drawn frame writes.
- The readout row's playback rate was the second writer that `PL-P58M` removed in this branch.
- The bookmark editor's notice states the reader's last edit, not run state, so it has no run state to go stale and is left as it is.
- The area chart's pin is written from one stored pin state, and a halt does not change that state, so it already had one writer.
