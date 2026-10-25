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
