---
id: PL-ZK09
title: No test checks the halt reason stays on screen after a layout operation, or that a branched case's two-run display survives a split, join, close, swap or Workspace switch
priority: P2
effort: S
status: done
classes: test
feature: v0.6.0-done-check
touches: tests/integration/test_layout_safety.py
added: 2026-10-20
closed: 2026-10-20
pr: 1700
payoff: a layout change that hid the halt reason or broke compare mode fails a test instead of reaching a learner
verify: grep -q 'def test_a_halted_run_keeps_its_halt_reason_on_screen' tests/integration/test_layout_safety.py && grep -q 'def test_a_branched_case_keeps_both_runs_drawn' tests/integration/test_layout_safety.py
---

**Problem.** No test checks the halt reason stays on screen after a layout operation, or that a branched case's two-run display survives a split, join, close, swap or Workspace switch

**Why it matters.** `/mnt/project-files/v0.6.0/dod-check.md` holds the whole check of v0.6.0's Definition of done, run on 2026-10-20 before the cut. Its sixth bullet asks that a test asserts each unconditional value is still on screen after a split, a join, a close, a Workspace switch and a reload. `tests/integration/test_layout_safety.py`'s `_check` asserts the ancestor condition for every value, but its `_REQUIRED` set leaves out the halt reason, because its run never halts. So the halt reason is never checked for being on screen. Its ninth bullet asks for no learner-visible regression against v0.5.0, and no layout test builds a branched case, so nothing checks that two compared runs still draw and stay named after the layout is rearranged.

**Done when.** A test halts a run and asserts the halt reason is on screen after each layout operation, and a test builds a branched case and asserts both runs still draw, named, after a split, a join, a close, a swap and a Workspace switch.
