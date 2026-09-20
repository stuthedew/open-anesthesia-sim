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

**The title names the smaller half.** The same root reaches MAC targets too,
where the consequence is worse, and the item is all three cases below.

**Why it matters.** `MarkStanding.STILL_RUNNING` says, in its own docstring,
"The run can still reach this mark, and has not yet", and
`app/dashboard_frame.py` renders it as the bare row - indistinguishable from a
mark the run simply has not got to. `format_time_bookmark` states the
requirement being broken in terms: "no row can be drawn that quietly asserts a
mark is still reachable without anybody having asked the run." A branch taken
at a halt begins standing on the crossing it was taken at, and says that
crossing has not happened on this run.

**Measured 2026-09-20**, against the built fork (`PL-B8MK`,
`resumed_at_halt`). Three cases, one root.

**A - a time bookmark on the step grid, wrong and permanently so.** Mark at
30.0 s or 20.0 s; the run halts at exactly that instant; the branch reads
`still_running`. It can never read anything else:
`TimeBookmark.crossed_between` is `before_s < instant_s <= after_s`, the
branch's first `before_s` *is* the fork, and `before_s` only increases, so no
step the branch ever takes can cross it. Stepped 50 times after the fork, the
standing does not move.

**B - the same act, off the step grid, answered differently.** Mark at 45.3 s
or 12.7 s; the halt lands on the step that crossed it, at
45.300000000000004 s or 12.700000000000001 s; `instant_s < opened_at_s` is now
true and the row reads `before this branch opened`. Both rows render their
instant as `45.3s`. So one act - mark an instant, stop there, branch - gives
two different accounts depending on whether the number the learner typed is a
multiple of 0.1 in binary, with nothing behind the difference a reader could
learn.

| marked at | halted at | standing on the branch | branch can halt on it again |
| --- | --- | --- | --- |
| 30.0 | 30.0 | `still_running` | no |
| 45.3 | 45.300000000000004 | `before_this_branch` | no |
| 20.0 | 20.0 | `still_running` | no |
| 12.7 | 12.700000000000001 | `before_this_branch` | no |

**C - a MAC target, and the worst of the three by consequence.** A branch
forked where the alveolar compartment crossed 0.4 xMAC, advanced 300 s, stands
at 0.587 xMAC. The trunk's row for that target reads `reached`; the branch's
reads `still_running`. Two runs on one panel, disagreeing about the one instant
they share by construction - and the branch's whole identity is *the management
taken at 0.4 xMAC*. `_mac_target_standing` has no `BEFORE_THIS_BRANCH` case at
all, correctly (a height is reachable from either side), so nothing in its
vocabulary can say otherwise. Unlike A this is not permanent - bringing the
compartment back down through the target flips it to `reached` - but it is
wrong for the whole time the comparison is being read.

**Where it stands.** `app/bookmarks.py`'s two helpers are both right about
their inputs. `_time_bookmark_standing` is fed
`SimulationController.began_at_s`, which is the run's own beginning - zero on
a trunk and the fork on a branch. What is missing is upstream: a branch is a
freshly constructed controller, so `_reached_instants_s`, `_reached_crossings`
and `_bookmark_halt` are all empty, and `_branch_from` copies the trunk's
*marks* without recording that the branch opens standing on one of them.
`tests/unit/test_bookmarks.py`
`test_a_bookmark_at_the_fork_instant_itself_is_not_called_unreachable` pins
case A's answer, reasoning "The branch opens standing on it, so the run has not
been put past it". That reads as a decision taken on a session's own
recommendation rather than one the project owner specified, and the
measurements are ordinary evidence against it: standing *on* a mark and being
able to *reach* it are different claims, and only the second is what the row
asserts.

**It is `PL-B8MK`'s consequence rather than its defect.** The strict `<`, the
empty reached-sets and the test above all predate it. What changed is reach:
until a bookmark was forkable, a branch beginning on one of its own marks
needed the learner to have marked a control-event instant by coincidence. Now
it is what every fork at a mark does.

**Decision needed.** What a mark a branch was forked *at* should read, given
that the branch begins standing on that crossing and, for a time bookmark, can
never cross it again. It is the owner's because it is what a learner sees on
the bookmark panel the moment after they branch at a mark.

**Recommended answer.** Seed the branch with the crossing it was forked at -
`_reached_instants_s`, `_reached_crossings` and `_bookmark_halt` from
`resume_point`'s own crossing rather than from the trunk's history - and test
`REACHED` before `BEFORE_THIS_BRANCH` in `_time_bookmark_standing`. All three
cases then read `reached`, which is true of the branch in the only sense the
row asserts: it is standing on that crossing, which is what a halt leaves. It
needs no new vocabulary, and `_mac_target_standing` already tests reached
first, so case C needs only the seeding.

It is a deliberate exception to the rule `app/controller.py` states beside
`_reached_instants_s` - that what a run has *done* with the marks is the run's
product and is cleared wherever a new run begins - and the exception has a
reason: the crossing a branch was forked at is not something the trunk did, it
is where the branch *is*.

Two alternatives, named and not recommended. Widening
`_time_bookmark_standing`'s first comparison to `<=` fixes A and B in one
character and leaves C untouched, which is the case with the worst
consequence. A fifth `MarkStanding` naming the fork says more - the row would
read as the fork rather than as history - and costs a new member, its
rendering, and the argument `MarkStanding`'s docstring makes for each of the
four it has; it is a display feature rather than a correction, and can follow.

**Done when.** A mark a branch was forked at reads something the branch can
make true, for a time bookmark and a MAC target alike; the answer does not
depend on whether the marked instant is exactly representable as
`step_count x simulation_step_s` - the four rows in the table reaching one
answer rather than two; and a test pins the MAC-target case, where a trunk and
a branch currently disagree about the crossing that separated them.
