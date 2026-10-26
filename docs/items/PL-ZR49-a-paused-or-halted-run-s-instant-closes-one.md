---
id: PL-ZR49
title: A paused or halted run's instant closes one stretch and opens the next, and no record says which of the two a setting change or a mark edit made while standing there belongs to, so each branch door, the reset and the halt record answer it separately: eight members from 2026-09-20 to 2026-10-25
priority: P1
effort: L
status: ready
classes: defect, safety
feature: defect-review-2026-10
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/bookmarks.py, src/anesthesia_sim/core/run_definition.py, tests/integration/test_controller.py, tests/unit/test_run_definition.py, tests/unit/test_dashboard_frame.py, docs/MODEL.md, docs/ARCHITECTURE.md
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

**Design, 2026-10-26 (the session that claimed it, before any code).** Read from `controller.py` and `run_definition.py` on `main` at the claim.

*The record already exists, and the doors read past it.* `RunDefinition` holds both sides of every instant. `record_change` opens a keyframe only at `reached_s`, so every keyframe after the opening is an edit the learner made while the run stood there. A stretch whose opening is earlier than `reached_s` can no longer change. So, at an instant `t`, the closed side is the last segment opening strictly before `t`, and the open side is the segment `segment_at(t)` returns (`bisect_right`). The defect is that each reader picks a side for itself. `_setting_at` reads the control timeline with `<=`, which is a second copy of "what was in force at `t`". `segment_at` returns the open side. `_open_at` writes the current settings over the fork. `_forget_unmarked` and `_stand_on` keep a crossing by instant.

*The rule the build should make true.* Every branch opens its provenance on the closed side of its fork. Whatever differs from that side at the fork is recorded in the branch's own control timeline as a change at the fork, so the timeline and the run definition agree. The three doors then differ in one respect only, which edits at the fork they carry:

- `resumed_here` and `resumed_at_mark` carry none. A change made while standing on the instant stays the trunk's (`PL-HSP8`'s chosen route, and `docs/MODEL.md` § "The canonical evaluation rule", "It is the branch the halt would have given").
- `resumed_at(t)` carries the trunk's change at `t` and records it in the branch's own timeline. The branch still runs after the change, as decided for that door. But its `opened_from.segment` is now the closed stretch, which the trunk can never replace (`PL-NRR6`), and its record states the setting it runs under, whatever the trunk does at `t` later (`PL-TNYP`).
- `reset()` on a branch keeps the current settings, as § "Reset behavior" requires. It records each difference from the closed side as a change at the fork instead of clearing the timeline (`PL-K5BS`, its first option). The `_open_at` docstring's claim that the definition "always opens at the parent's stretch, under the parent's settings" then becomes true.

Element-wise reproduction survives. `_open_at` already opens the branch's definition at the closed stretch's keyframe, calls `advance_to(fork)` and then `record_change`. That forms the fork keyframe from `_canonical_state_at(fork)`, the same expression the trunk used. A keyframe door branch built this way is bit-identical to the trunk from `t` on.

*Marks.* `PL-1ZQ4` already decided, ratified, that a step's crossing is asked again with the current marks. So the halt record should store only the fact "this run stopped here because a step crossed a mark". `bookmark_halt` and `here_fork_point.stopped_on_mark` should derive which marks from that step and the current marks, as `_crossings_stood_on` does (`PL-XV0D`). A branch stores the same fact for its fork step, and `ResumePoint.crossing` and `_stand_on` then have no remaining reader.

*Build order.*

1. Add `RunDefinition.reaching_segment_at(instant_s)` with its unit tests. It returns the stretch the step that reached the instant ran under: the last segment opening strictly before it, or the first segment at the run's opening.
2. In `_branch_from`, build the branch from the closed segment's settings rather than `_setting_at`, and delete `_setting_at`. Check what `UptakeEquationSettings` holds for the dial and each flow first. If it cannot give the constructor its values exactly, keep a timeline read for the values and say why.
3. Make `_resume_point_here` and `_resume_point_at_mark` take the closed segment. Make `_resume_point_at` take the closed segment and pass the open side's settings to `_branch_from`, which applies them through the branch's setters after `_open_at`.
4. Have `reset()` on a branch replay the difference through the same path, without `_clear_control_timeline` wiping it.
5. Replace `_bookmark_halt`'s stored crossing with the stopped-on-a-crossing fact, and derive the crossing on read.
6. Write `test_every_door_at_a_paused_instant_agrees_after_an_edit_made_there`, plus each open member's named test. Update `docs/MODEL.md` § "The canonical evaluation rule" and § "Reset behavior", and the docstrings of `ResumePoint`, `_open_at`, `resumed_at` and `segment_at`.

*Open at the time of writing.* At the run's opening, at step 0, no step has closed a stretch. A trunk edit at 0 after a branch was taken at 0 still replaces the opening stretch. Settle this in the build. Either take the opening stretch as both sides, since the opening state does not depend on the settings, or record the edit at 0 in the branch the same way. `PL-NRR6`'s case is at 30 s, so it does not depend on this choice.

**Build, 2026-10-26 (reset in place at 342k spend, before close-out).** Steps 1 to 6 of the build order are done on `claude/pl-zr49-iusum9`, in `cca420e4`, `e0985a95` and the commit that adds this paragraph.

- `RunDefinition.reaching_segment_at` returns the reaching stretch, with four unit tests in `tests/unit/test_run_definition.py`.
- Every door builds its `ResumePoint` from the reaching stretch. `_branch_from(resume_point, settings)` builds the branch from the settings record directly, and `_setting_at` is deleted: `UptakeEquationSettings` holds each value exactly as set and already as its checked type, so no timeline read was needed. `resumed_at` passes the open side's settings. `_open_at` records each difference from the reaching stretch as a change at the fork, in the run definition and, through the new `_record_in_timeline` (split out of `_record_control_change`), in the control timeline. Reset uses the same path.
- `SimulationSnapshot.opened_with` names the entries a branch opened with, and `has_recorded_run` compares the timeline with it, so a fresh keyframe branch and a reset branch still hold nothing to destroy (`PL-7TBQ`'s rule).
- The halt record is `_halt_crossing`: the current marks at the keys the stepped readings crossed when a trunk halted, plus what the step crosses when asked of the current marks canonically. `ResumePoint.crossing` and `_stand_on` are gone. **Placeholder decided here:** the stepped keys are kept because `tests/unit/test_bookmarks.py::test_a_run_that_settles_exactly_on_a_target_halts_once_and_then_advances` halts on a height a stepped reading lands on exactly, and the canonical reading missed it, which left a halted trunk naming no mark. A branch has no stepped readings of its parent, so in that edge case the trunk and a branch at the halt still disagree. Filed as `PL-QVBR`.
- **The step-0 question is settled as the first option:** the opening stretch is both sides, because the opening keyframe is a state no setting produced. `test_a_branch_at_the_case_s_opening_keeps_the_settings_it_opened_under` pins it.
- **`PL-NRR6`'s Done-when, second clause:** after the trunk sets the dial back, its keyframe at the fork is gone, so `resumed_at` no longer accepts that instant. The first clause holds (the provenance stays in the trunk's segments), and the instant stays offered by `here_fork_point` while the trunk stands there, with a provenance that compares equal to the branch's. The clause was written while the provenance named the keyframe. Close `PL-NRR6` with that reason.
- Tests: the head's `test_every_door_at_a_paused_instant_agrees_after_an_edit_made_there` and each member's named test are in `tests/integration/test_controller.py`, section "Edits made at a paused instant (PL-ZR49)". Seventeen existing tests that stated the old behaviour were rewritten to the rule, two renamed (`..._replaces_the_stretch_at_its_fork`, `..._opens_with_only_the_change_it_runs_under_in_its_timeline`), and `test_a_setting_changed_while_halted_makes_the_bookmark_fork_a_keyframe_fork` became `..._is_carried_only_by_the_keyframe_fork`, because it pinned `PL-HSP8`'s defect.
- Docs: `docs/MODEL.md` § "The canonical evaluation rule" gains the paragraph "An instant where a run stands has two sides", and four sentences there and in § "Reset behavior" are updated. `docs/ARCHITECTURE.md` § "What a branch inherits" and `app/bookmarks.py`'s module docstring are corrected.

**Left for the session that resumes, in order.**

1. Run the seven new tests against `c4123db3` (the code before the fix) and record each failing assertion here, as `.claude/rules/test-oracles.md` rule 6 asks. They use no interface the fix added.
2. Close-out step 8: `uv run python tools/new_prose.py`, and the fresh-reviewer subagent on its output.
3. Close-out step 6: the source diff is about 470 lines added under `src/`, so run independent adversarial passes (lifecycle and state, the domain invariants, what a displayed value could mislead, whether the new tests fail when the behaviour is inverted, dead code) and refute what they return.
4. `bin/docket set PL-ZR49 --status done --closed DATE`, and close `PL-HSP8`, `PL-TNYP`, `PL-NRR6`, `PL-K5BS` and `PL-XV0D` in the same commit, each with one line saying which test closes it. Retitle draft `#1844` to lead with all six ids first.
5. `bin/docket verify --self` with all six ids, until it prints `ACCEPT`, and sort any mutation survivor it prints (close-out step 7).
6. Mark `#1844` ready, per `.claude/skills/pull-request/SKILL.md`.
