---
id: PL-ZR49
title: A paused or halted run's instant closes one stretch and opens the next, and no record says which of the two a setting change or a mark edit made while standing there belongs to, so each branch door, the reset and the halt record answer it separately: eight members from 2026-09-20 to 2026-10-25
priority: P1
effort: L
status: ready
classes: defect, safety
feature: defect-review-2026-10
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/core/run_definition.py, tests/integration/test_controller.py, docs/MODEL.md
deferred-from: v0.7.0 - recorded as a generator head by PL-R4Y2's defect review on 2026-10-25; each member's safety finding was filed and placed by its own triage, and this head's work is the structure that stops the next one
added: 2026-10-25
payoff: every branch, reset and halt record states the settings and marks it was opened under, whichever door took it
verify: grep -q 'def test_every_door_at_a_paused_instant_agrees_after_an_edit_made_there' tests/integration/test_controller.py
root-cause-of: PL-3K9B, PL-2N43, PL-1ZQ4, PL-HSP8, PL-TNYP, PL-NRR6, PL-K5BS, PL-XV0D
generator: live - five of its eight members were filed on 2026-10-24 and 2026-10-25, and the one route chosen so far patches two doors
misread: Which stretch an edit made while a run stands on an instant belongs to: the closed or the open one
---

**Problem.** A paused or halted run's instant closes one stretch and opens the next, and no record says which of the two a setting change or a mark edit made while standing there belongs to, so each branch door, the reset and the halt record answer it separately: eight members from 2026-09-20 to 2026-10-25

**Evidence.** Found on 2026-10-25 by asking the generator question of the product defects filed since 2026-10-23. The 43 reviewer-replay findings that `PL-GTHP` filed at 21:59 UTC came after `PL-R4Y2`'s pass on `07ac5e0c`, so none of them had been asked. Eight items misread one fact:

- `PL-3K9B` (closed 2026-09-20): a time bookmark at exactly the fork instant reads `still_running` on the branch.
- `PL-2N43` (closed 2026-10-12): a mark added inside the halting step while the trunk stands on the halt reads `BEFORE_THIS_BRANCH` on one door and `PASSED` on another.
- `PL-1ZQ4` (closed 2026-10-18): a mark added after the step that crossed it is answered three ways by the trunk, a branch, and `fork_at`.
- `PL-HSP8`: a setting changed while standing on a halt is in force on the mark branch and the late halt branch, but not on the halt branch taken before the change.
- `PL-TNYP`: a branch taken at a keyframe opens after the trunk's change there, and no record on screen says so.
- `PL-NRR6`: a trunk change at the instant a branch was just taken replaces the stretch the branch's `opened_from` names.
- `PL-K5BS`: a branch reset after a setting change runs under settings that neither its record nor `opened_from` states.
- `PL-XV0D`: the halt record keeps marks by instant, so a removed and re-added mark leaves it naming the old one.

`PL-R4Y2`'s pass on 2026-10-25 saw the first three as "how a mark's standing is evaluated" and found they split three ways. One level up they share the fact below, and the five new members are the settings side of the same fact.

**The mechanism, in the code.** The instant where a run stands has two sides. One is the stretch the reaching step ran under, which is closed. The other is the stretch the next step will run under, which is still open to edits. Nothing represents that pair. Each reader picks a side on its own:

- `SimulationController._setting_at` (`app/controller.py`) treats a change at `elapsed_s <= instant_s` as in force, so it reads the open side.
- `RunDefinition.record_change` (`core/run_definition.py`) folds a change at an instant where a stretch has already opened into that stretch. It is right for a step not yet run, and it is wrong once a branch has been taken from that stretch.
- `_crossing_ending_at`, `_stand_on` and `_forget_unmarked` read the marks at the fork, at a reset, or by instant.
- `_open_at` records the current settings and clears the timeline.

`PL-HSP8`'s chosen route patches two doors (`_resume_point_at_mark` and `resumed_here`). That fixes one member and leaves the shape in place, as `PL-1ZQ4`'s fix did for the standings and not for the halt record (`PL-XV0D`).

**Why it matters.** A branch is how a learner tests "what if I had done X instead at this moment". When the branch silently opens on the other side of the decision, the two traces coincide or differ for a reason no record states. `CLAUDE.md`'s safety-critical standard requires every displayed value to be traceable to the settings that produced it, and `opened_from` plus the control record is that trace.

**Done when.** One record states, for the instant a run stands on, the settings and marks the reaching step was computed under, and every edit made while standing there. Every branch door, a branch's reset and the halt record read that record and compute neither side themselves. `tests/integration/test_controller.py` has `test_every_door_at_a_paused_instant_agrees_after_an_edit_made_there`, which takes every door at a paused instant before and after a setting change and a mark edit, and checks that the doors agree with `docs/MODEL.md`'s stated rule. The open members close under it, or each says why it stays.

**Generator check.** This item is the head. Its mechanism is still being handed members: five of eight were filed in the last two days, from a review of merged pull requests, so more of the same may already sit in merged code.
