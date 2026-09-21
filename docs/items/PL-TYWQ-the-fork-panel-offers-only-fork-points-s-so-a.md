---
id: PL-TYWQ
title: The fork panel offers only fork_points_s, so a learner stopped at their own bookmark still cannot branch there
priority: P2
effort: S
status: needs-decision
classes: feature
feature: scenario-branching
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/simulation_view.py, tests/unit, tests/integration, docs/ARCHITECTURE.md
added: 2026-09-20
payoff: closes the one sequence the interface cannot complete - mark a decision point, stop there, branch there - which is what v0.5.0's Definition of done asks for
---

**Problem.** The fork panel offers only fork_points_s, so a learner stopped at their own bookmark still cannot branch there

**Why it matters.** `ROADMAP.md`'s v0.5.0 Definition of done asks for "a branch
taken at any recorded control event **or bookmark**". `PL-B8MK` built the
bookmark half in the model - `SimulationController.resumed_at_halt` and
`BranchedCase.fork_at_halt` - and `PL-VKJW` built the panel a learner takes a
branch from, on the same day and on a different branch. Neither knows about
the other. The panel offers `BranchedCase.fork_points_s`, which is the trunk's
keyframes, and a bookmark halt deliberately adds nothing to that list: the
whole point of the route chosen is that marking a run records no keyframe and
so changes nothing the run computes.

So the capability exists and the control does not reach it. The sequence
`docs/ARCHITECTURE.md` § "How a learner takes one" describes - "a learner marks
the decision point and then forks there, which is the order the two panels are
read in" - is the one sequence the interface cannot complete: the learner
marks 45 s, the run stops at 45 s, and the fork panel offers induction and the
control events.

**Where it stands.** `app/dashboard_frame.py`'s `fork_offer` decides what the
panel shows and `app/qt_widgets.py`'s `ForkPanel` draws it; `app/simulation_view.py`
wires the choice to `BranchedCase.fork_at`. A halt is visible to all three
already - `snapshot().bookmark_halt` is what the transport reads to say the run
stopped on a mark - so nothing new has to be computed, only offered.

**Decision needed.** What shape the control takes, given that a bookmark fork
is available only while the run is standing on the halt. It is the owner's
because it is an affordance a learner sees appear and disappear.

**The design question is what the control says, not whether it can.** A halt
is a permission rather than a standing offer: taking a step clears it
(`docs/ARCHITECTURE.md` § "Where a branch may be taken"), so the affordance
appears and disappears with the run's state, where `fork_points_s` only grows.
Two shapes are worth weighing rather than one being obvious - a second control
beside the list, which says plainly that this fork is the one you are standing
on; or one list that gains a row while the run is halted, which is fewer
controls and a mode. `.claude/rules/expert-review.md` prefers the interface
that prevents the error, and the error here is forking at an instant the run is
no longer standing on.

**Done when.** A learner who marks an instant, watches the run stop there, and
asks to branch gets a branch at that instant, through the same panel they would
use for a control event; and what the panel shows while the run is *not*
standing on a halt cannot be mistaken for an offer to fork at a mark.

---

## Recommendation, 2026-09-21: the separate transient control, not the extra list row

Written into the brief rather than left in a reply, because this item is the
instrument and a reply is gone by the time the answer comes. **Not decided
here** - the item stays `needs-decision`, and the owner's answer is what closes
it.

**Recommended: a second control beside the list, present only while
`snapshot().bookmark_halt` holds, labelled with the instant it will fork at and
where that instant came from** - "Branch here: 45 s, your mark" rather than a
bare "Branch here". The permanent list is left exactly as it is.

Three grounds, in order of weight.

1. **A vanishing list row is a hidden mode change; a vanishing control is a
   visible one.** The two offers have different lifetimes - `fork_points_s`
   only grows and every row in it stays valid, while the halt fork is valid
   only while the run stands on the halt. A learner who reads the list, looks
   away, takes a step and looks back finds the list one row shorter, and the
   absence of a row is detectable only by comparison against a remembered list.
   A control that is either there or not is detectable on sight.
   `.claude/rules/expert-review.md` - "minimize hidden modes, surprising
   defaults, context-dependent behavior, and stale UI state" - is the rule, and
   a list whose membership silently changes meaning is the stale-state case.

2. **It is the disposition this milestone already took, one control over.**
   `PL-VKJW` refused a second fork while a comparison is shown rather than
   quietly swapping which branch is displayed, on the ground that the quiet
   swap is hidden state this project refuses; `ROADMAP.md`'s v0.5.0 Required
   scope records it. Making the transient offer visibly transient is the same
   judgment, and taking it differently here would leave the fork surface
   holding two opposite conventions.

3. **The cheaper-looking option is not actually cheaper.** A row added to the
   list has to carry the same "this one is the mark you are standing on"
   disambiguation the separate control carries in its label, *and* has to be
   visually distinguished from permanent rows so it does not read as one, *and*
   has to explain its own disappearance. That is more work than a second
   control, for a weaker result.

**What it costs, and it is real:** one more control on a panel that has one
today, in a milestone whose own out-of-scope list is already holding back a run
selector. The counter-case is the item's own - fewer controls, and a learner
who has stopped at a mark is looking at the fork panel anyway. If the owner
prefers the single list, the mitigation that keeps the Done-when clause
reachable is that the halt row must be rendered differently in kind rather than
merely labelled differently, and that is a chart-adjacent presentation decision
this project would normally want measured rather than asserted.

**What this recommendation does not touch.** Whether returning to a mark forks
or truncates is `PL-ZW0J`, is the owner's, and is deliberately downstream: they
asked on 2026-09-20 to revisit it after using the thing. This item is the route
to a branch at a marked instant, which both answers to `PL-ZW0J` need.
