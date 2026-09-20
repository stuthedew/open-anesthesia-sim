---
id: PL-CTD7
title: Detect a bookmark crossing inside the advance loop, with an explicit not-reached outcome
priority: P1
effort: M
status: needs-decision
classes: safety, feature, anticipated
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/core/simulation.py, tests/unit, docs/MODEL.md
added: 2026-09-06
payoff: stops a threshold halt landing up to 30 simulated seconds past the value the learner asked for, silently and differently depending on how fast they were running
---

**Problem.** A threshold bookmark ("stop when the vessel-rich group reaches 0.8
MAC") is only correct if the crossing is tested on every simulation step.
Testing it once per rendered frame overshoots by the whole frame's worth of
simulated time, and the faster the playback multiplier the worse it gets.

**`PL-NBWP` measured that "worse", and the number is larger than this item
assumed** (closed 2026-09-06, pull request 383). A tick advances its whole
burst with nothing between the steps, so the reachable grid is `multiplier x
0.1` s: 0.1 s at 1x, then 0.5, 2, 6 and 30 s. Per-frame detection would
therefore overshoot by up to **30 simulated seconds** at 300x, not by a vague
frame's worth, and `docs/MODEL.md` s "Supported simulation step" now carries
what one grid step of that costs a displayed compartment - percentage points
on an abrupt manoeuvre, against the hundredths the 1x tolerance is stated in.

**Why it matters - this is the safety half of bookmarks.** The overshoot is
silent and speed-dependent: the same bookmark halts at a different
concentration depending on how fast the learner was running, so the displayed
halt value is not the value that was asked for. That is a
presentation-correctness failure of the kind `CLAUDE.md` treats as
safety-critical, and it also breaks reproducibility of any branch taken from
that bookmark, because two branches nominally taken "at 0.8 MAC" would start
from different states.

**The halt must leave the run paused, and that requirement is `PL-NBWP`'s
consequence rather than this item's own.** A halt is detected *inside* the
loop, so it can land on the exact crossing step - finer than the grid any live
control change can reach. What the learner does next cannot: `PL-NBWP`
established that a setting changed while the run is playing first acts at a
tick boundary, so at 300x "halt at 0.8 MAC, then turn the vaporizer off" turns
it off up to 30 simulated seconds after the value the learner was looking at.
The displayed halt would be right and the action taken from it wrong, which is
the same presentation failure one step along. `PL-NBWP` documents the route -
pause, change, resume, because no steps are taken while paused and the setters
apply unconditionally - and a bookmark halt that pauses makes that route
automatic instead of something the learner has to know. So the halt pauses;
resuming is explicit.

**A threshold above a compartment's asymptote is never reached**, so the
outcome set is three-valued rather than two: reached, not reached within the
run-time cap, and still running. "Not reached" must read differently from
"reached" rather than the run stopping silently at the cap.

**Where.** The advance loop in `src/anesthesia_sim/app/controller.py`, and
whatever `core/simulation.py` has to expose for a per-step test that does not
put simulation logic in a UI callback. `docs/MODEL.md` records that a halt is
reported at the first step on which the threshold is crossed, and what that
means for the value displayed.

**Done when.** A crossing is detected on the step that crosses it at every
playback multiplier, asserted by test at 1x and 300x with the same halt state;
the run is left paused at the halt, asserted by test, so a control change made
from it is step-exact rather than landing on the next tick boundary; an
unreachable threshold ends in a distinct, visible not-reached outcome; and
`docs/MODEL.md` states the halt semantics and that a halt lands on an instant
finer than the control grid s "Supported simulation step" publishes.

## One case for the outcome set, found building `PL-LPLD` (2026-09-20)

A branch inherits its trunk's marks, because a mark is a question about what is
still to come and a comparison is two managements answering one question
(`SimulationController.resumed_at`, and `docs/ARCHITECTURE.md` § "What a branch
is"). So a **time bookmark lying before the branch's own fork instant comes
across with the rest, and the branch can never reach it going forward.**

It is inherited rather than dropped deliberately: dropping it would make the
trunk's list and the branch's disagree about what the case is marked at, which
is a worse thing for a comparison to have to explain than a row that cannot
fire. But nothing currently says so where the row is listed, and this item owns
the vocabulary that would - it is the fourth member of the reached /
not-reached-within-the-cap / still-running set, and unlike the other three it
is decidable statically from `ResumePoint.elapsed_s` rather than by running.

A MAC target has no equivalent case: a height is reachable from either side, so
a branch may cross one its trunk never did.

## No crossing direction, so one target can halt a run twice (2026-09-20)

The project owner removed the crossing direction from `MacTarget` on
2026-09-20 - "Don't need falling or rising for target" - so a target names a
compartment and a height and nothing else. A case taken up and back down
through 0.8 x MAC therefore crosses it twice, and a learner has no way to say
"only on the way up".

That makes **re-arming this item's question rather than a detail of it**: does
a target halt the run on every crossing, or once until it is re-armed? Both are
defensible and the choice is user-facing, so it belongs with the rest of this
item's outcome set rather than being settled by whichever loop is written
first. Nothing is broken today: nothing detects a crossing yet.

## Unblocked but not startable, 2026-09-20 (`PL-8G48`)

`PL-LPLD` (add time bookmarks and MAC targets as two separately listed
collections) closed as `#758`, so the blocker is gone and `bin/docket check`
reported this item as ready to promote. It goes to `needs-decision` instead,
because the two sections above - both written on 2026-09-20, after this item
was last triaged - put a user-facing question in front of the loop. The item
itself says the re-arming question "belongs with the rest of this item's outcome
set rather than being settled by whichever loop is written first", and writing
the detection loop is exactly what would settle it by accident.

**Decision needed.**

1. **Does a MAC target halt the run on every crossing, or once until it is
   re-armed?** With the crossing direction removed from `MacTarget` on
   2026-09-20, a target names a compartment and a height and nothing else, so a
   case taken up through 0.8 x MAC and back down crosses it twice. A halt leaves
   the run paused (established above, from `PL-NBWP`), so "every crossing" means
   a wash-out interrupts the learner a second time at a value they have already
   seen and acted on; "once until re-armed" means a learner who *wants* the
   downward crossing has to ask for it.

   **Recommendation: once until re-armed.** It keeps the simplification that
   removing the direction field bought - the learner never classifies a target
   as rising or falling - while putting the second halt behind a deliberate act
   rather than making it the default. Re-arming is also discoverable at no cost,
   because the run is already paused at that target's own row when the choice
   arises. The cost is one extra control and one extra state per target, and it
   is reversible: "every crossing" is the same loop with the re-arm flag pinned
   on.

**Decided in-session, under rule 14 of `.claude/rules/instruction-writing.md`:
the inherited-bookmark case gets its own outcome, rather than folding into
"not reached".** The section above leaves it open as the fourth member of the
set; it is recorded here as settled because the safety-critical standard
determines it rather than taste. A time bookmark lying before a branch's own
fork instant is unreachable **by construction** and is decidable statically from
`ResumePoint.elapsed_s`, without running anything. Reporting it as "not reached
within the run-time cap" would tell a learner that running longer might reach
it, which is false - a plausible-looking outcome that misrepresents what the
model can do, which `CLAUDE.md` forbids for a displayed value. So the outcome
set is four-valued: **reached**, **not reached within the cap**, **still
running**, and **unreachable from this branch's fork instant**. If the project
owner would rather it read differently, that is display copy and costs one line;
the requirement that it not read as the cap case is not a preference.

**The band moves to `P1`, and that is the status change rather than a
re-rating.** `check_gate_reentries` exempts a `safety` item from the P1 floor
only while `anticipated` **and** `status: blocked` hold together, so leaving
`blocked` is what returns this finding to the debt gate - the settled behavior
`PL-ZF2G` installed and `PL-JFQ3` applied, not a judgment made here. `docket
set` refused the move at `P2` in those words.

**Nothing is broken today** - nothing detects a crossing yet - so this is not a
live safety defect, and `anticipated` stays on the item to say so. The `safety`
class describes the overshoot hazard the detection loop is built to prevent, and
what has changed is that the question in front of it is now answerable.
