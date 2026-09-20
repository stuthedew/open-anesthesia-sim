---
id: PL-3K9B
title: A time bookmark at exactly the instant a branch forked at reads still_running, which no step can make true
priority: P1
effort: S
status: needs-decision
classes: defect, safety
feature: scenario-branching
touches: src/anesthesia_sim/app/bookmarks.py, tests/unit/test_bookmarks.py, tests/integration/test_controller.py
added: 2026-09-20
payoff: stops the bookmark panel telling a learner to wait for a mark their branch is standing on and can never reach
---

**Problem.** A time bookmark at exactly the instant a branch forked at reads still_running, which no step can make true

**Why it matters.** `MarkStanding.STILL_RUNNING` says, in its own docstring,
"The run can still reach this mark, and has not yet." On a branch standing at
a mark's own instant that is false and cannot become true:
`TimeBookmark.crossed_between` is `before_s < instant_s <= after_s`, the
branch's first `before_s` *is* the fork, and `before_s` only increases - so no
step the branch ever takes can cross it. The row invites a learner to wait for
something that cannot arrive, which is the exact failure
`NOT_REACHED_WITHIN_CAP` and `BEFORE_THIS_BRANCH` were each split out to
prevent. `app/dashboard_frame.py` renders it.

**Measured 2026-09-20**, on a default sevoflurane controller marked at one
instant, run until the mark halted it, and forked there with
`resumed_at_halt` (`PL-B8MK`). Each row then asked whether the branch can halt
on that mark again, by stepping it 50 times:

| marked at | halted at | standing on the branch | branch halts on it again |
| --- | --- | --- | --- |
| 30.0 | 30.0 | `still_running` | no |
| 45.3 | 45.300000000000004 | `before_this_branch` | no |
| 20.0 | 20.0 | `still_running` | no |
| 12.7 | 12.700000000000001 | `before_this_branch` | no |

**The second column is the whole of the difference, and it is arithmetic
rather than clinical.** A halt lands on the step that crossed the mark, so the
fork instant is `step_count x simulation_step_s`. Where the learner's typed
instant is exactly representable as that product the two are equal and
`instant_s < opened_at_s` is false; where it is not, the halt is one unit in
the last place later and the same comparison is true. So one act - mark an
instant, stop there, branch - gives two different rows depending on whether
the number the learner typed happens to be a multiple of 0.1 in binary, with
nothing behind the difference a reader could learn.

**Where it stands.** `app/bookmarks.py`'s `_time_bookmark_standing` opens with
`if bookmark.instant_s < opened_at_s`. It is fed
`SimulationController.began_at_s`, which is correct - the run's own beginning,
zero on a trunk and the fork on a branch - so the input is right and the
comparison is what is wrong. `tests/unit/test_bookmarks.py`
`test_a_bookmark_at_the_fork_instant_itself_is_not_called_unreachable` pins
the current answer, reasoning "The branch opens standing on it, so the run has
not been put past it". That reads as a decision taken on a session's own
recommendation rather than one the project owner specified, and the
measurement above is ordinary evidence against it: standing *on* a mark and
being able to *reach* it are different claims, and only the second is what the
row asserts.

**It is `PL-B8MK`'s consequence rather than its defect.** The strict `<` and
the test above both predate it. What changes is reachability: before a
bookmark was forkable, a mark sitting exactly on a branch's fork instant
needed the learner to have marked a control-event instant by coincidence.
Now it is what happens whenever a learner forks at a mark they typed in whole
tenths, which is most of them.

**Decision needed.** What a time bookmark standing at exactly a branch's fork
instant should read, given that no step of that branch can ever cross it. It
is the owner's because it is what a learner sees on the bookmark panel the
moment after they branch at a mark.

**Recommended answer.** Widen the first comparison to
`<=` and read `BEFORE_THIS_BRANCH` as "at or before this branch's fork
instant, so no step can reach it" - which is what that member's own docstring
already claims and what the measurement shows is true. It removes the
representability coin-flip in one comparison and needs no new vocabulary. The
alternative worth naming is a fifth standing for the mark a branch was taken
at, which says more - the row would read as the fork rather than as history -
and costs a new member, its rendering, and the argument `MarkStanding`'s
docstring makes for each of the four it has. Recommend the first; the second
is a display feature rather than a correction, and can follow it.

**Done when.** A time bookmark standing at exactly a branch's fork instant
reads something the branch can make true, `MarkStanding`'s vocabulary says
which and why, and a test asserts that the answer does not depend on whether
the marked instant is exactly representable - the four rows measured above
reaching one answer rather than two.
