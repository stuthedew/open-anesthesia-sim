---
id: PL-Z4MP
title: The controller keeps a set of time marks it halted on, which the clock check already answers since whole-second steps
status: untriaged
feature: one-source-of-truth
added: 2026-11-23
filed-pr: 2281
---

**Problem.** `SimulationController` keeps `_reached_instants_s`, the set of time-mark instants on which the run halted, in `src/anesthesia_sim/app/controller.py`. `_halt_on`, `_keep_crossings_stood_on` and `_forget_unmarked` write it, and `bookmarks._time_bookmark_standing` asks it first, before the clock check `opened_at_s <= instant_s <= elapsed_s`. That docstring already says that since `PL-SZ6G` (whole-second steps) a halt lands on the marked instant itself, so the clock check gives the same answer, and that "The halt set is still asked first."

So two records answer one question, whether the run has been at a marked instant. Today they agree, which is why four mutants of the writes survive as equivalent in the mutation sort of `PL-00Y5`. A later change to one of the writes could make them disagree, and the halt set, being asked first, would then decide a time mark's standing (Passed or Still running) on its own. `_forget_unmarked` mutants 5 to 8 show the shape: when one mark was removed, each turned the standing of a mark that was left to Passed or Reached, for a mark the run had not reached.

**What to do.** Remove `_reached_instants_s`, its three writes, the `reached_instants_s` argument of `bookmark_standings` and `_time_bookmark_standing`, and the first case in that function's docstring, so that the clock alone decides a time mark's standing, as the docstring's own rule says. Check first that no other reader takes the set, and that the MAC-target halt record, which a height needs because a height has no clock time, is a separate field. `tests/integration/controller/test_controller_marks.py::test_removing_one_mark_leaves_the_standing_of_every_other_mark_as_it_was` holds the standings this change must keep.
