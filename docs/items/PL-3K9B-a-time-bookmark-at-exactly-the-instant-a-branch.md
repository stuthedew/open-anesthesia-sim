---
id: PL-3K9B
title: A time bookmark at exactly the instant a branch forked at reads still_running, which no step can make true
priority: P1
effort: S
status: done
classes: defect, safety
feature: scenario-branching
touches: src/anesthesia_sim/app/bookmarks.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/dashboard_frame.py, tests/unit/test_bookmarks.py, tests/unit/test_dashboard_frame.py, tests/integration/test_controller.py, docs/MODEL.md, docs/ARCHITECTURE.md
added: 2026-09-20
closed: 2026-09-20
payoff: stops the bookmark panel telling a learner to wait for a mark their branch is standing on and can never reach
verify: grep -q 'PASSED = ' src/anesthesia_sim/app/bookmarks.py && grep -q 'def test_a_mark_the_run_has_passed_does_not_read_as_still_reachable' tests/unit/test_bookmarks.py
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

**A is the common case rather than a coincidence.** A halt lands on the step
that crossed the mark, so the fork instant is `step_count x simulation_step_s`,
and every whole-second instant is exactly representable as a multiple of the
0.1 s step - **3 600 of 3 600** over 1 s to 3 600 s. A learner marking "45
seconds" or "five minutes" gets this row every time; the off-grid rows below
are what a typed tenth or hundredth gives.

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

**The same comparison is wrong on a trunk, without any branch at all.** A
`TimeBookmark(0.0)` on an ordinary run reads `still_running` forever, for the
identical arithmetic: the run opens at 0.0, `crossed_between` needs
`before_s < 0.0`, and no run's clock is ever negative. Measured 2026-09-20 on a
trunk stepped to 60 s. It is reachable by a learner marking induction, which is
a strange thing to mark and not an impossible one - and it means the fix is not
confined to branches, and that `BEFORE_THIS_BRANCH`'s displayed wording needs a
word that is true on a trunk. That wording is the one judgment inside the
recommended answer.

**It is `PL-B8MK`'s consequence rather than its defect.** The strict `<`, the
empty reached-sets and the test above all predate it. What changed is reach:
until a bookmark was forkable, a branch beginning on one of its own marks
needed the learner to have marked a control-event instant by coincidence. Now
it is what every fork at a mark does.

**Measured again 2026-09-20 against the same tree, and the root is wider than
these three.** Four further cases were run. Two of them involve no branch at
all, and the seeding recommended below reaches none of the four.

**D - a mark added behind a running trunk.** A trunk is stepped to 60 s; the
learner then marks 30 s. The row reads `still_running`, and still reads it at
180 s. Nothing refuses the act: `app/simulation_view.py`'s
`_add_time_bookmark` validates only what `TimeBookmark.__post_init__`
validates - finite and not negative - so an instant already behind the clock is
an ordinary entry. This is the common form of the defect rather than an edge of
it. Marking an instant you have just run past is what a learner does when
something interesting has already happened, and it produces exactly the row
`format_time_bookmark`'s docstring says it exists to prevent: "no row can be
drawn that quietly asserts a mark is still reachable without anybody having
asked the run."

**E - a branch taken at a control event, which seeding cannot reach.** Route
one (`resumed_at`) opens at a keyframe rather than at a crossing, so there is no
`BookmarkCrossing` to seed from. A trunk halted on a mark at 30.0 s, dialled,
then forked at the 30.0 s keyframe gives a branch whose row for that mark reads
`still_running` while the trunk's reads `reached` - case C's disagreement,
on a time bookmark, at the door that predates `PL-B8MK` entirely. A mark added
*on* such a branch at its own fork instant reads the same.

**F - a mark removed and re-added on a branch at its fork instant** reads
`still_running`: `_forget_unmarked` drops the reached entry when the mark goes,
and nothing puts it back when an equal one arrives.

**G - `reset()` on a branch discards the fork crossing.** A branch reset stands
at its fork with `bookmark_halt` at `None` and the fork mark back at
`still_running`, so seeding done at fork time has to survive a reset or the
defect returns on the first one. `_open_at` is reset's path as well as the
fork's, which is where that is cheapest to get right.

**What D to G change.** The common root is not the empty reached-sets. It is
that `still_running` is inferred from *absence from the halt set*, when the
question a one-way clock actually asks is whether the instant is still ahead of
the run. A run's clock only increases and never returns below `began_at_s`, so
a time bookmark is reachable if and only if the clock has not yet arrived at
it; everything at or behind the clock is behind the run, whatever put it there
- a fork, a control event, or a learner typing a number they had already passed.

**Decision needed.** What a time bookmark reads once the run's clock is at or
past it - whether it got there by being forked at the mark, by being forked at a
control event the mark sits on, or by the learner marking an instant the run had
already run past. It is the owner's because it is what a learner sees on the
bookmark panel, and because the honest answer redefines `MarkStanding.REACHED`.

**Recommended answer, superseding the one below in part.** Decide a time
bookmark's standing from the run's own clock rather than from the halt set
alone. A mark is `REACHED` when `began_at_s <= instant_s <= elapsed_s` - the run
has been at that instant - or when the halt set already holds it, which is what
carries case B, where the fork instant is one floating-point step past the mark
it crossed and no comparison against the clock can see it. Keep the seeding for
that case and for the MAC target, which has no clock to read and so needs the
crossing carried across the fork; carry it on `ResumePoint` rather than reading
the trunk's `_bookmark_halt`, so that `_open_at` seeds a fork and a reset
identically and `G` is closed with it. Keep `BEFORE_THIS_BRANCH` at its strict
`<` and at its present wording, which stays true: nothing lands in it that the
clock rule has not already claimed, so no wording has to be found that is true
on a trunk.

It costs one argument - the run's `elapsed_s`, alongside the `opened_at_s`
`BookmarkSet.standings` already takes - and one sentence of `REACHED`'s
docstring, which today reads "This run has halted on this mark at least once"
and would read that the run has been at it. **That is the judgment inside the
recommendation.** On a trunk the two coincide, because a run halts on every mark
it crosses; they part only where the run was already past the instant when the
mark arrived, and there "has been at it" is the one that is true and "has halted
on it" is the one no step can make true.

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

**What the reference implementation does, read 2026-09-20** (project owner,
who named it as the workflow to follow). Philip JH, *Workbook for Gas Man®*
(Med Man Simulations, title page 2012-05-16), chapter 2 § "Using Bookmarks",
printed pages 22-23; the Edit menu, printed pages 14-15; appendix E
§§ "Bookmarks" and "Replaying Simulations", printed pages 183 and 186-87:

- **A Gas Man bookmark is a pause point, not a record.** It "marks a particular
  point in time in the evolution of a simulation where one wishes to pause, or a
  point to which to return". It has no reached state at all - the program never
  displays one - and it pauses the run "whenever the simulation is run", on the
  original pass and on every replay alike.
- **A mark may be set behind the clock, and that is the designed case.** "You
  can pick any time earlier or later than the moment of the simulation you have
  paused", and set mid-experiment the dialog *defaults* to "that moment in the
  simulation minus one second", for the stated purpose: "Clicking Add will cause
  the playback to pause before any changes you make, allowing you to try
  different options on playback."
- **Returning to one is rewind-then-run, not opening at it.** `Rewind` goes to
  time zero "keeping all the settings as they were throughout the simulation";
  `Fast Fwd` "takes you immediately forward to the next Bookmark or the end".
- **A change made on the way back truncates the run**, after the program
  confirms intent, and "continuing to run the simulation beyond the change point
  extends the simulation with new, alternate results". The saved `.GAS` file is
  never touched - only the working copy.

**It is decisive for the word, not for the rule.** A standing that survives a
rewind as a historical claim would be false the moment the run is replayed: the
mark is ahead again and will stop the learner again. Gas Man avoids this by
having no such claim to make. So the rule recommended above stands - the answer
is the mark's position relative to this run's clock - and `REACHED` is the wrong
name for it, because "this run has halted on this mark at least once" is exactly
the historical reading a rewind falsifies.

**Revised recommendation: a distinct positional standing for a time bookmark,
and `REACHED` left alone.** Add one `MarkStanding` member - `PASSED`, rendered
"passed" - carrying the at-or-behind case, tested in this order: the seeded halt
set, then `began_at_s <= instant_s <= elapsed_s`, then `BEFORE_THIS_BRANCH` at
its strict `<`, then the cap, then blank. `REACHED` keeps its present meaning and
its present word, and serves MAC targets, where a height crossed is a genuine
fact about the trajectory and no clock can order it. The `MarkStanding` docstring
then says which members answer for which kind, as it already does for
`BEFORE_THIS_BRANCH`.

This is the fifth member the section above called a display feature that could
follow. It is not one: without it, adopting any rewind makes every passed row a
false claim, and the cost of the member is one enum entry and one string in
`MARK_STANDING_TEXT`.

**The owner is leaning to truncate-with-confirm** (2026-09-20, provisionally,
to be revisited after use; `PL-ZW0J`). That strengthens this recommendation
rather than complicating it. Truncation takes one run's clock *backwards in
place*, so a mark beyond the truncation point goes from passed back to
reachable and will stop the learner again - which is precisely the revocation a
historical `REACHED` cannot survive, and it happens on a single run rather than
between two. Whichever of the two meanings of "returning to a mark" the project
takes, the standing has to be positional; under truncation it has to be, sooner.

**Decided (project owner, 2026-09-20, ratified)**, over reusing `REACHED` for
the at-or-behind case, and over this brief's original answer of seeding the fork
crossing and reordering the existing four members. Add `PASSED` as a fifth
`MarkStanding` and decide a time bookmark from the run's own clock; `REACHED`
keeps its present meaning and its present word and serves MAC targets.

Ratified rather than specified: it was this session's recommendation agreed on
one read, so ordinary evidence - a measurement, a cost this case did not carry,
a constraint that appears later - is enough to put it back to the owner, and
"it is what the owner decided" does not defend it. The fork-versus-truncate
question it sits beside is *not* decided: `PL-ZW0J` carries the owner's leaning
to truncate-with-confirm, explicitly to be revisited after use.

**Done when.** No mark at or behind a run's own clock reads as still
reachable, on a trunk and on a branch alike and whichever door the branch came
through; the answer does not depend on whether the marked instant is exactly
representable as `step_count x simulation_step_s` - the four rows in the table
reaching one answer rather than two; a reset does not put a branch back into the
defect; and a test pins each of A to G, the MAC-target case included, where a
trunk and a branch currently disagree about the crossing that separated them.
