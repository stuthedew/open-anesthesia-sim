---
id: PL-ZW0J
title: Returning to a mark truncates the run at that point after confirming intent, rather than forking, which is what Gas Man does and what the owner is leaning to
priority: P2
effort: M
status: needs-decision
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py, docs/MODEL.md, docs/ARCHITECTURE.md, tests/integration/test_controller.py
blocked-by: PL-W4XQ
deferred-from: v0.6.0 - blocked on PL-W4XQ when the gate froze and unblocked after it; the owner's call once both returns are in use, and not safety or science
added: 2026-09-20
---

**Problem.** Returning to a mark truncates the run at that point after confirming intent, rather than forking, which is what Gas Man does and what the owner is leaning to

**Why it matters.** It decides what the one act v0.5.0 is named for actually
does. Returning to a marked instant either keeps the run you came from, so two
managements sit on one axis and can be compared, or discards it, so the
comparison is the learner's memory. Both are defensible and they are not
recoverable from one another after the fact, so the choice has to be made
rather than fallen into.

**Raised by the project owner, 2026-09-20**, choosing between the two things
returning to a mark could mean: "I'm leaning truncate with confirm since I think
often you want to trial different things quickly and not necessarily a bunch of
forks. But lets revisit after i have time to play with".

**It is the reference implementation's behaviour.** Philip JH, *Workbook for
Gas Man®* (Med Man Simulations, title page 2012-05-16), appendix E
§ "Replaying Simulations", printed pages 186-87: a substantive change made
during replay - "such as making a change to cardiac output, or adjusting the
vaporizer" - "would invalidate the remainder of the previous experimental
timeline. When a user makes a substantive change (and Gas Man confirms the
user's intent), Gas Man truncates the simulation at the point of change.
Continuing to run the simulation beyond the change point extends the simulation
with new, alternate results". The confirm is part of it, not an embellishment.
So is the scope: only the working copy truncates, and "no changes are ever made
to a simulation saved on disk by virtue of actions taken during replay".

**Why Gas Man truncates, which is not this project's constraint.** It holds one
simulation per window, and its comparison mechanism is `Overlay` and multiple
windows rather than a branch. This project has `BranchedCase`, so keeping both
futures on one axis costs it nothing it does not already have - and the
workbook's own glossary (printed page 183) names comparison as what bookmarks
are *for*: "most helpful where issues of comparability arise - for example, to
compare outcomes given alternative settings at a particular point in the course
of anesthesia". Overlay is the compromise Gas Man makes to reach that, not the
goal. The session recommended fork-by-default over truncate-by-default on that
reasoning and the owner is leaning the other way; this item is the owner's
reading, to be settled after use.

**Blocked until the workflow exists to try.** The opinion this item waits on is
formed by using the thing: `PL-TYWQ` puts the fork at a mark in the panel, and
`PL-W4XQ` makes a mark set behind the clock returnable at all. Until both, there
is nothing to play with and the question cannot be answered from a description.

**What truncation costs that forking does not.** Taking the clock backwards in
place means the run's own records have to come back with it, and today none of
them can: `_reached_instants_s` and `_reached_crossings` only ever grow within a
run and are cleared wholesale by `_forget_reached_marks`; `_bookmark_halt`, the
control timeline and `RunDefinition`'s segments all describe a run that reached
further than the truncated one did. Each needs a defined answer at the
truncation point, and a mark beyond it has to go back to being reachable, which
is the property `PL-3K9B`'s decision turns on.

**Done when.** A learner who returns to a marked instant and changes a setting
is asked to confirm, the run is truncated there, and continuing extends it with
the alternate result; nothing the truncated run reports describes the discarded
future; and `docs/ARCHITECTURE.md` states which of the two meanings of
"returning to a mark" this build takes and why.

**Unblocked 2026-10-12 by `PL-W4XQ`, and now the owner's to answer.** Both
returns this item waited on exist: `PL-TYWQ` branches at the mark a run is
standing on, and `PL-W4XQ` branches at any time bookmark the trunk has passed,
from the same "From" selector as the control events. Both fork. So the thing to
play with is in the build, and the question is no longer hypothetical.

**Decision needed.** After using the two returns, should returning to a mark
keep forking - the trunk stays, the change is made on a branch drawn beside it -
or truncate the run there after a confirm, as Gas Man does?

**Recommended: keep the fork, and reopen only if using it shows the friction
the lean was about.** The worry behind the lean - trialling several things
quickly without a pile of forks - is already met without discarding anything:
a branch's own Reset returns it to its fork and leaves the comparison standing
(`docs/ARCHITECTURE.md` § "How a learner takes one, and how a comparison
ends"), so "try something else from the same point" is one press, and only one
comparison is ever on screen. Truncation would spend the original future to buy
that, and the comparison it discards is what v0.5.0 was named for. It also
costs what the paragraph above lists - every per-run record would need a
defined answer at the truncation point - which forking never pays. What would
change this: finding, in use, that the two-run cap or the trunk Reset's
"ends the comparison" is the thing in the way, which is a selector question
(`ROADMAP.md` § "Explicitly out of scope for v0.5.0") rather than a reason to
truncate.
