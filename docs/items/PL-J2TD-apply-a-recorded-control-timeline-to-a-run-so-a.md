---
id: PL-J2TD
title: Apply a recorded control timeline to a run, so a point between samples is reached by resimulation rather than restored
priority: P2
effort: M
status: needs-decision
classes: feature, refactor
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/core, tests/unit, tests/integration
added: 2026-09-06
---

**Problem.** The controller records a control-input timeline (`ControlChange`
entries, v0.4.0) but nothing can *apply* one. A run advances only by the
settings a user changes as it goes, so a recorded timeline is a read-only
record rather than something a second run can be driven by.

**Why it matters.** This is planned-milestone item 8's replay half, and it is
the mechanism every branch operation in v0.5.0 rests on. A stored state lets a
run be *restored*; it does not let a point *between* stored states be reached,
because that needs the same inputs re-applied over the same interval. Without
it, "resimulate from the nearest prior point" - the fallback in every branching
design - cannot be implemented at all, and a branch could only ever be taken at
a point the store happens to hold.

**Scope.** Internal only. A user-facing replay control is planned item 10 and
stays behind item 9's save/load, which v0.5.0 puts out of scope (project owner,
2026-09-06). What this item delivers is a driver: given a timeline and a step
count, produce the state the run had, using the same code path a live run uses,
so the two cannot diverge by construction.

**Where.** `src/anesthesia_sim/app/controller.py` (the timeline and the advance
path), `src/anesthesia_sim/core` for whatever the driver needs exposed.

**Done when.** A recorded timeline can be applied to a fresh run and reproduces
the original run's state at every sampled point, asserted by test; and the
driver shares the advance path with a live run rather than reimplementing it.

**Open question, raised by `PL-T691` landing (2026-09-07).** That item makes
the timeline authoritative: `core/run_score.py` holds the settings in force at
each moment and answers any instant from them in closed form, and
`tests/integration/test_controller.py` already asserts most of the property
above - a run reproduced from its inputs, agreeing with the recorded samples
to 6.7e-16 as a fraction of one atmosphere over 1 201 samples and two setting
changes. What that does *not* deliver is this item's second clause: the score
reaches the answer analytically rather than by driving the same advance path a
live run takes.

**Decision needed.** Whether this item still delivers a resimulation driver
that shares the live advance path, now that `PL-T691` answers any instant
from the same timeline in closed form - or whether it narrows to whatever a
fork needs beyond a curve. It is a real choice rather than a formality. Against keeping it: with the exact propagator the two
paths solve the same equations over each stretch, so "cannot diverge by
construction" is now close to true without a driver, and a second way to
advance a run is a second thing to keep correct. For keeping it: stepping is
what a *fork* resumes into - a branch has to become a live run, not only a
curve - and the score answers instants rather than handing back a running
system. `ROADMAP.md` item 12 is what settles which of those v0.5.0 needs.

Until it is answered this item is not `ready`, because its `verify:` command
would have to name a driver that may not be built. Whoever takes it writes the
command with the work, per the `docket` skill.

**Answered against the source, 2026-09-14, and the recommendation is to
narrow it. Left `needs-decision` because narrowing it edits `ROADMAP.md`'s
Required scope, which is the project owner's.**

The brief says "`ROADMAP.md` item 12 is what settles which of those v0.5.0
needs". Item 12 is `PL-TFX5` - a run forks at any control-input event or
bookmark, flat rather than as a tree - and between it, the rule `PL-P1Z3`
landed, and what `PL-T691` actually built, the question is decided by the
repository rather than by preference. Three findings, each checked in the
source rather than in the prose describing it:

**1. The first clause of Done when is already delivered, by `RunDefinition`.**
`core/run_definition.py` *is* an applied control timeline: `record_change`
appends a stretch keyed at the run's own reach, whose opening keyframe is
`self._canonical_state_at(self._duration_s)`, and `state_at` answers any
instant as one propagation from the keyframe opening its stretch. The segment
list is the timeline and the states are derived from it. Building a driver to
reproduce a run from its inputs would build that a second time;
`tests/integration/test_controller.py` already asserts the property to
6.7e-16 as a fraction of one atmosphere over 1 201 samples.

**2. The second clause is now refused by the rule this milestone already
landed.** `docs/MODEL.md` § "The canonical evaluation rule" says every value
"stored, exported, replayed, compared against another run, or taken as the
state a branch opens from is taken canonically", and names `state_at` as that
path. A driver re-driving `SimulationState.advance` over a timeline composes a
*third* order of floating-point operations - N fixed steps, rather than one
propagation per stretch - so its answers are not bit-identical to the
canonical ones. The same section measures the gap: the single-instant path
sits within 1.8e-14 of the stepped run. `PL-Z3W6` requires a branch to
reproduce its parent **element-wise rather than within a tolerance**, so a
stepping driver could not be used for the one thing it was wanted for. This is
the determinism hazard `PL-P1Z3` exists to close, arriving as a new route to
the same instant.

**3. What a fork needs beyond a curve is named already, and it is not a
driver.** § "What this requires of a branch" gives exactly two conditions - the
branch opens at a keyframe, and the child's clock is re-based by subtracting
the fork instant rather than by the caller naming an offset - and both
mechanisms exist. `RunDefinition.__init__` takes an opening state and refuses a
`DisplayState` by name, which its docstring calls "a fork opening from a
drawing value". `AgentUptakeSystem.capture_state` / `restore_state` seed a live
system at a state. So a branch is: canonical state at a keyframe, a new
`RunDefinition` opened from it, an uptake system restored to it, and a clock
re-based by subtraction - after which the branch advances by the *existing*
live path, which is what `PL-CTD7` needs when it detects crossings inside the
advance loop.

**The live advance path does still exist**, which is worth stating because it
is the half a quick reading gets wrong. `SimulationController.advance` calls
`self._state.advance(simulation_step_s)` and *then*
`self._run_definition.advance_to(...)`; `docs/MODEL.md` says both records are
live in this release and are held to each other by the closed-form agreement
test. So the item's premise is not dissolved - a fork genuinely must produce
something advanceable. What has changed is that reaching the fork point no
longer needs stepping, and stepping to it would forfeit the exactness `PL-Z3W6`
requires.

**Recommended narrowing.** Drop the resimulation driver. The item becomes: a
fork opens a live run at a canonical keyframe state with its clock re-based by
subtraction, seeded through `restore_state`, sharing the live advance path
*forward* from that point rather than re-driving it up to that point. That is
the residue this brief already names - "whatever a fork needs beyond a curve".
Against it: nothing found. The argument the brief records for keeping the
driver - "stepping is what a fork resumes into" - survives the narrowing
intact, because the narrowed item is what makes a branch resumable.

**What the owner decides.** Whether to narrow, because `ROADMAP.md`'s Required
scope entry for this item reads "the mechanism by which a point *between*
recorded samples is reached at all", and that sentence becomes wrong under the
narrowing: such a point is reached by `state_at`, and what this item supplies
is the resumption. Editing that bullet is a scope edit.

No `verify:` command is written yet, deliberately: the brief already says one
cannot be, because it would have to name a driver that may not be built.
