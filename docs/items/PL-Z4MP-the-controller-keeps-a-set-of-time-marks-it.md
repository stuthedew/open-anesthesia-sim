---
id: PL-Z4MP
title: The controller keeps a set of time marks it halted on, which the clock check already answers since whole-second steps
priority: P2
effort: S
status: done
classes: defect
feature: one-source-of-truth
touches: src/anesthesia_sim/app/bookmarks.py, src/anesthesia_sim/app/controller.py, tests/integration/controller/test_controller_marks.py, tests/unit/test_bookmarks.py, tests/unit/test_dashboard_frame.py, tests/unit/test_supported_range_edges.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no learner sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-23
closed: 2026-11-23
pr: 2304
filed-pr: 2281
payoff: a time mark's standing is decided by the run's clock alone, so a mark the panel shows as passed and the record kept when it is removed cannot disagree
tests: tests/integration/controller/test_controller_marks.py::test_a_removed_time_mark_records_whether_the_run_had_passed_it, tests/integration/controller/test_controller_marks.py::test_a_branch_returned_to_a_mark_opens_on_it_and_reads_it_as_passed
---

**Problem.** `SimulationController` keeps `_reached_instants_s`, the set of time-mark instants on which the run halted, in `src/anesthesia_sim/app/controller.py`. `_halt_on`, `_keep_crossings_stood_on`, `_forget_unmarked` and, since `PL-5GX4` (Undo after a mark is removed), `restore_mark` write it, and `bookmarks._time_bookmark_standing` asks it first, before the clock check `opened_at_s <= instant_s <= elapsed_s`. That docstring already says that since `PL-SZ6G` (whole-second steps) a halt lands on the marked instant itself, so the clock check gives the same answer, and that "The halt set is still asked first."

So two records answer one question, whether the run has been at a marked instant. Today they agree, which is why four mutants of the writes survive as equivalent in the mutation sort of `PL-00Y5`. A later change to one of the writes could make them disagree, and the halt set, being asked first, would then decide a time mark's standing (Passed or Still running) on its own. `_forget_unmarked` mutants 5 to 8 show the shape: when one mark was removed, each turned the standing of a mark that was left to Passed or Reached, for a mark the run had not reached.

**What to do.** Remove `_reached_instants_s`, its four writes, the `reached_instants_s` argument of `bookmark_standings` and `_time_bookmark_standing`, and the first case in that function's docstring, so that the clock alone decides a time mark's standing, as the docstring's own rule says. Check first that no other reader takes the set, and that the MAC-target halt record, which a height needs because a height has no clock time, is a separate field. `tests/integration/controller/test_controller_marks.py::test_removing_one_mark_leaves_the_standing_of_every_other_mark_as_it_was` holds the standings this change must keep.

**Why it matters.** Two records answer whether a run has been at a marked instant. Today they agree. A later change to one write could make them disagree, and the halt set, asked first, would then show a mark as Passed that the run has not reached.

**Done when.** `SimulationController` keeps no record of the instants at which a run halted on a time bookmark, and `_time_bookmark_standing` in `app/bookmarks.py` decides a time bookmark's standing from the run's opening instant and its clock alone. The standings that the mark tests pin, `test_removing_one_mark_leaves_the_standing_of_every_other_mark_as_it_was` among them, are unchanged, and a removed time bookmark's record still says whether the run had passed it.

**Generator check.** A one-off. The fact read twice is whether the run has been at a marked instant. Before `PL-SZ6G` a step could end past a mark, so the halt record was needed, and nothing removed it once every step ended on a whole second. No head's `misread:` in `bin/docket generators --misread` names a mark's standing or the halt record.

**Reproduced 2026-11-23.** `SimulationController._reached_instants_s` is still written in `src/anesthesia_sim/app/controller.py`.

**Checked before the removal, 2026-11-23.** The set had two readers: `bookmark_standings`, through `_reached_now`, and `remove_time_bookmark`, for `RemovedMark.reached`. The MAC target record is a separate field, `_reached_crossings`, which stays. The set could hold an instant outside `opened_at_s <= instant_s <= elapsed_s` only if a step could end after a mark it crossed. A step is one second (`SIMULATION_STEP_S`) and a mark is a whole number of seconds, so every halt, every branch's opening step and every restored mark falls inside that span, and a reset or an agent change clears the set as it moves the clock back. If a longer step ever returns, `test_a_branch_returned_to_a_mark_opens_on_it_and_reads_it_as_passed` (a mark at 47 s) fails, because the branch would open after its own mark. The `_time_bookmark_standing` docstring says so.

**Done 2026-11-23.** `_reached_instants_s` is gone, with its writes in `_halt_on`, `_keep_crossings_stood_on`, `_forget_unmarked`, `_forget_reached_marks` and `restore_mark`, the `_reached_instants` helper, and the `reached_instants_s` argument of `BookmarkSet.standings` and `_time_bookmark_standing`. `_reached_now` became `_heights_reached_now`, which returns the heights alone. `remove_time_bookmark` takes `RemovedMark.reached` from `_passed_time_bookmarks`, which reads the standings the bookmark panel shows, and `restore_mark` puts back a height's record only. `tests/integration/controller/test_controller_marks.py::test_a_removed_time_mark_records_whether_the_run_had_passed_it` pins that record: a run halted on a mark at 30 s and run on to 40 s records the mark at 30 s as passed and one at 600 s as not. The unit test of a halted instant's standing in `tests/unit/test_bookmarks.py` now gives the run's clock instead of a halt set. Documents checked: `docs/INTERFACE.md` § "What a mark's row reports", whose definitions of Passed and of Before this branch opened already describe the clock rule; and `docs/MODEL.md`, `docs/VERIFICATION.md`, `docs/ARCHITECTURE.md` and `README.md`, none of which describes the halt record.

**Blind review, 2026-11-23.** One pass. It found that the test this item names as the guard on the clock rule, `test_a_branch_returned_to_a_mark_opens_on_it_and_reads_it_as_passed`, marked 45 s and ran in steps of 10 s, so a step of 3, 5, 9, 15 or 45 s would still land on the mark and the test would pass while the rule had stopped holding. The test now marks 47 s, a prime, so no step longer than a second and shorter than the mark ends on it. Setting `SIMULATION_STEP_S` to 5 makes it fail.
