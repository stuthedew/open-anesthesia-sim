---
id: PL-Z4MP
title: The controller keeps a set of time marks it halted on, which the clock check already answers since whole-second steps
priority: P2
effort: S
status: ready
classes: defect
feature: one-source-of-truth
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/bookmarks.py, tests/integration/controller/test_controller_marks.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no learner sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-23
filed-pr: 2281
payoff: only the clock decides whether a run has reached a time mark, so a mark cannot show Passed for an instant the run never reached
---

**Problem.** `SimulationController` keeps `_reached_instants_s`, the set of time-mark instants on which the run halted, in `src/anesthesia_sim/app/controller.py`. `_halt_on`, `_keep_crossings_stood_on`, `_forget_unmarked` and, since `PL-5GX4` (Undo after a mark is removed), `restore_mark` write it, and `bookmarks._time_bookmark_standing` asks it first, before the clock check `opened_at_s <= instant_s <= elapsed_s`. That docstring already says that since `PL-SZ6G` (whole-second steps) a halt lands on the marked instant itself, so the clock check gives the same answer, and that "The halt set is still asked first."

So two records answer one question, whether the run has been at a marked instant. Today they agree, which is why four mutants of the writes survive as equivalent in the mutation sort of `PL-00Y5`. A later change to one of the writes could make them disagree, and the halt set, being asked first, would then decide a time mark's standing (Passed or Still running) on its own. `_forget_unmarked` mutants 5 to 8 show the shape: when one mark was removed, each turned the standing of a mark that was left to Passed or Reached, for a mark the run had not reached.

**What to do.** Remove `_reached_instants_s`, its four writes, the `reached_instants_s` argument of `bookmark_standings` and `_time_bookmark_standing`, and the first case in that function's docstring, so that the clock alone decides a time mark's standing, as the docstring's own rule says. Check first that no other reader takes the set, and that the MAC-target halt record, which a height needs because a height has no clock time, is a separate field. `tests/integration/controller/test_controller_marks.py::test_removing_one_mark_leaves_the_standing_of_every_other_mark_as_it_was` holds the standings this change must keep.

**Why it matters.** Two records answer whether a run has been at a marked instant. Today they agree. A later change to one write could make them disagree, and the halt set, asked first, would then show a mark as Passed that the run has not reached.

**Done when.** The halt set and its writes are gone, the clock alone decides a time mark's standing, and the existing test of mark standings after a removal still passes.

**Generator check.** A second copy of a fact the clock already holds, left when `PL-SZ6G` made halts land on whole seconds. One-off; `one-source-of-truth` holds the family.

**Reproduced 2026-11-23.** `SimulationController._reached_instants_s` is still written in `src/anesthesia_sim/app/controller.py`.
