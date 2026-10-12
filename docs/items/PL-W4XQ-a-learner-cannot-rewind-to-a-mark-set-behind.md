---
id: PL-W4XQ
title: A learner cannot rewind to a mark set behind the clock: resumed_at refuses any instant that is not a keyframe and resumed_at_halt needs the run to be standing on the crossing, so marking 1 h while paused at 3 h gives a mark nothing can return to
priority: P2
effort: M
status: done
classes: feature
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/bookmarks.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/theme.py, docs/MODEL.md, docs/ARCHITECTURE.md, tests/integration/test_controller.py, tests/unit/test_bookmarks.py, tests/unit/test_dashboard_frame.py, tests/integration/test_simulation_view.py, docs/items/PL-ZW0J-returning-to-a-mark-truncates-the-run-at-that.md
added: 2026-09-20
closed: 2026-10-12
pr: 1451
payoff: makes a mark set behind the clock something a learner can return to, which is the act the owner described the feature for
verify: grep -q 'def test_a_mark_set_behind_the_clock_can_be_returned_to' tests/integration/test_controller.py
recurrences: 2026-09-21 PL-54V0
---

**Problem.** A learner cannot rewind to a mark set behind the clock: resumed_at refuses any instant that is not a keyframe and resumed_at_halt needs the run to be standing on the crossing, so marking 1 h while paused at 3 h gives a mark nothing can return to

**Raised by the project owner, 2026-09-20**, describing what a time bookmark is
for: "I'm paused at like 3 hours of anesthesia or whatever, and I want to see
what happened if I changed something earlier. So I might set a bookmark at say
1 hour or whatever, and then rewind to that specific point (or just use it as
an event note)."

**Measured the same day** against `4c282700`. A trunk was stepped to 30 min, a
fresh gas flow change recorded there, and stepped on to 3 h. `TimeBookmark`
at 3600.0 s was then added.

- `resumed_at(3600.0)` refuses: "this run holds no keyframe at 3600.0 s, so
  opening there would restart from two propagations where the run took one and
  would not reproduce it element-wise; it holds keyframes at [0.0, 1800.0] s."
- `resumed_at_halt()` refuses: the run is not standing on a crossing, because
  the mark was added after the clock had passed it, so no step ever crossed it.

So both doors are shut, and the marked instant is one nothing can return to.
The rest of the described behaviour already works: rewinding to the 30 min
keyframe gives a branch whose row for the 1 h mark is blank, and that branch
halts at exactly 3600.0 s - the "acts like a future bookmark" half needs
nothing.

**Why it matters.** The one act the owner described the feature *for* is the
one the model refuses. A mark a learner cannot return to is an event note, and
an event note is the lesser of the two things they asked for.

**It is not `PL-TYWQ`.** That item offers the fork the run is *standing on*
through the panel, which is the halt case. This is the case where no halt ever
happened, so there is nothing for a panel to offer and the refusal is in the
model.

**What it runs into.** `_resume_point_at`'s keyframe restriction is not
arbitrary: opening between two keyframes restarts from two propagations where
the run took one, which is the element-wise reproduction `ROADMAP.md` item 12
asks for. `PL-B8MK` bought the bookmark-halt fork by having the run *be* at the
fork with live state; a mark behind the clock has no such state.

**The reference implementation does not open at the mark at all, and that is
the route this item should take.** Philip JH, *Workbook for Gas Man®*
(Med Man Simulations, title page 2012-05-16), chapter 2 § "Using Bookmarks",
printed pages 22-23, and appendix E § "Replaying Simulations", printed pages
186-87: a Gas Man bookmark is a pause point rather than a record, `Rewind`
returns to time zero "keeping all the settings as they were throughout the
simulation", `Fast Fwd` "takes you immediately forward to the next Bookmark or
the end of the simulation", and "play and fast-forward are interrupted by
bookmarks, which cause an automatic pause". So the way a learner returns to a
mark behind the clock is to rewind to the opening and run forward until the
mark stops them.

That sidesteps the keyframe restriction entirely rather than paying it.
Replaying from this run's own opening is the identical propagation the run
already took, so it reproduces element-wise by construction - which is what
`_branch_from` already relies on when it replays a segment's settings and
refuses the branch if they do not reproduce. It is also cheap: 1 h of case at
the interface's 0.1 s step is 36,000 steps, and a 3 h run completes in seconds
in this engine.

So the routes are, best first: **replay from the opening to the marked
instant**; re-propagate from the nearest keyframe and declare what that costs;
record a keyframe when a mark is added behind the clock, which moves the run's
own later answers and is the failure `PL-B8MK` measured at 48 of 54 elements and
rejected; or refuse the act at entry rather than accepting a mark nothing can
use.

**Whichever route this takes, the fork instant is the step the run stopped
on, never the mark's typed value** (noted 2026-09-27 by `PL-LLBV`'s drop).
`SimulationController._resume_point` refuses any instant that is not exactly a
whole number of the run's steps. Typed straight into it, 12 767 of the 36 001
one-decimal times from 0 to 3600 s fail: `453 * 0.1` is 45.300000000000004,
not 45.3. The replay route gets this right by construction, because it forks at
the halt and the halt is read from the clock. A typed 45.3 s mark halts the run
at 45.300000000000004 s and forks there. The re-propagation route would not get
it right unless it snaps the mark to `round(t / step) * step` once, at the one
boundary that accepts it, where the learner can see the instant taken. The
guard stays exact, because the branch's step count rests on it.

**Re-confirmed 2026-10-12 against `4b6f9557`, and changed shape.** Both doors
still refuse, with the messages quoted above, so the problem stands. What has
gone is the obstacle. "What it runs into" below rests on `PL-B8MK` having needed
the run's live state at the fork, and it never did: `_resume_point_at_halt`
takes the fork state from `RunDefinition.state_at`, one propagation from the
keyframe opening the stretch, and opens the branch's definition at that keyframe
(`PL-54V0` found this on 2026-09-23). `state_at` answers any instant the run has
reached, so a mark behind the clock has exactly the state a halt fork opens
from. The guarantee carries over with it, because it rests on parent and branch
propagating from one keyframe and not on the run having stopped there:
`docs/MODEL.md` § "What this requires of a branch" measured 0 of 54 elements
differing at a fork between two keyframes.

That retires the ranking of routes below:

- **Replaying from the opening is that construction**, read through the closed
  form. § "The canonical evaluation rule" defines the state at an instant as one
  propagation from its stretch's keyframe, each keyframe composed from the
  opening, so evaluating the run's own definition at the mark is the replay,
  with no stepping. Re-stepping the live stepper from zero instead would hand
  the branch a chained live state, which the same section refuses as a branch's
  opening state, and would make one mark forked at its halt and forked later
  into two different branches.
- **Re-propagating from the nearest keyframe** has nothing to declare: it is
  the halt fork, and its divergence on the canonical path is zero.
- Recording a keyframe stays refused, for `PL-B8MK`'s reason, and refusing the
  act at entry is not needed.

**So the route is a third door, and it takes the mark itself.**
`SimulationController.resumed_at_mark(bookmark)`, kept by
`BranchedCase.fork_at_mark`, forks at the step that reaches the mark - the first
step instant at or past it, which is the instant a halt would have stopped on,
decided by `TimeBookmark.crossed_between`'s own rule rather than by rounding -
with the halt fork's construction, and refuses a mark the run has not passed or
does not hold. It takes a `TimeBookmark` rather than a float, so the typed-value
hazard below cannot be expressed: the fork instant comes from the step count and
nothing is snapped. `round(t / step) * step` would have been wrong as well as
visible, since it rounds a mark lying inside a step down to a step before it,
which no halt ever stops on. The interface lists each mark the trunk has passed
in the branch control's selector beside the control events, labelled with the
instant the branch opens at. The halt button stays, because a MAC target has no
instant to list.

**Done when.** A learner who marks an instant the run has already passed can
return to it, or is told at the moment of marking that they cannot and why; and
`docs/MODEL.md` states what returning to a marked instant reproduces and what it
does not.

`verify:` is the `grep` alone since 2026-10-12, as `PL-0HPV`'s reorder pass
asked: `-k returning_to_a_mark` never selected the test the `grep` names.

**Built 2026-10-12.** `resumed_at_mark`, `fork_at_mark` and `mark_fork_points`
as above, and the branch control's selector lists each passed mark as
"20m, on your mark". Measured the same day for `docs/MODEL.md`, on this brief's
case at its own scale (a change at 30 min, stepped to 3 h): the stepped live
compartment fractions a running trunk displays and the canonical states a branch
opens from differ by at most 4.9e-14 as a fraction, at probes from 60 s to 3 h.
Found while building it, and filed rather than fixed here: the halt door seeds
its branch from the halt's recorded crossing, so a mark added inside the halting
step reads as before that branch (`PL-2N43`); and the selector's width is a
constant tuned to one face (`PL-NC0D`).
