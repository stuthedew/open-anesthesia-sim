---
id: PL-J2TD
title: Open a live run at a canonical keyframe state with its clock re-based, which is what a fork resumes into
priority: P2
effort: M
status: ready
classes: feature, refactor
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/core, tests/unit, tests/integration
added: 2026-09-06
verify: uv run pytest tests/integration/test_controller.py && grep -q 'def test_a_fork_opens_at_a_keyframe_and_rebases_its_clock' tests/integration/test_controller.py
---

**Problem.** A branch has to become a *live run* rather than only a curve.
`RunDefinition` answers any instant of a recorded timeline in closed form, so
the state at a fork point is available and exact - but what comes back is a
state vector, not a running system. Nothing takes that state and opens a run
positioned at it, under a clock that starts where the fork was taken.

**Why it matters.** Every branch operation in v0.5.0 rests on this. `PL-TFX5`
forks a run and the learner then *manages* the branch differently, which means
advancing it; `PL-CTD7` detects a bookmark crossing **inside the advance
loop**, which presupposes a branch that advances. Without this, a fork produces
a second curve and nothing a learner can act on.

`docs/MODEL.md` § "The canonical evaluation rule" already names the two places
a plausible implementation loses its guarantee silently, and both are this
item's to hold:

- **A branch opens at a keyframe.** Restarting from the canonical state at an
  instant the parent has no keyframe for replaces one propagation over an
  interval with two over its halves - a different rounding of the same exact
  solution, measured at up to 5.3e-13 in an accumulator. Opening at a stretch
  boundary reproduces the parent bit for bit, which is what `PL-Z3W6` asserts
  element-wise rather than within a tolerance.
- **The child's clock is re-based by subtracting the fork instant**, never by
  the caller naming an offset, because that subtraction does not always
  round-trip: with a fork at 900 s, `(900.0 + 1e-6) - 900.0` is
  9.999999974752427e-07, so a child asked for its own `1e-6` propagates over a
  different interval from its parent and lands one unit in the last place away.

**Scope.** Internal only, and narrower than this item once was - see the
narrowing below. No resimulation driver: reaching the fork instant is
`RunDefinition.state_at`'s job and already done. No user-facing replay control,
which is planned item 10 behind item 9's save/load and out of scope for v0.5.0
(project owner, 2026-09-06).

**Where.** `src/anesthesia_sim/app/controller.py` - the seam between a
canonical state and a running system; `src/anesthesia_sim/core` for whatever
that needs exposed. Both mechanisms it composes exist already:
`RunDefinition.__init__` takes an opening state and refuses a `DisplayState` by
name, and `AgentUptakeSystem.capture_state` / `restore_state` seed a live
system at a state.

**Done when.** A run can be opened at a canonical keyframe state of another
run, with its clock re-based by subtraction, and advances from there by the
same path a live run takes - no second way to advance a run is introduced. A
run opened at an instant the parent holds no keyframe for is refused rather
than approximated. `tests/integration/test_controller.py` carries
`test_a_fork_opens_at_a_keyframe_and_rebases_its_clock`.

**Narrowed 2026-09-14 (project owner), on the analysis below.** The item read
"Apply a recorded control timeline to a run, so a point between samples is
reached by resimulation rather than restored", and asked for a driver that
shares the live advance path. Both halves of that are now wrong: `RunDefinition`
*is* an applied control timeline, and a stepping driver would forfeit the
exactness `PL-Z3W6` requires. What survives is the resumption, which is what
`ROADMAP.md` item 12's fork actually needs. The Required-scope bullet in
§ "v0.5.0 - the case you can branch" is re-worded with it.

**The original brief, kept because the narrowing is only legible against it.**
It read: the controller records a control-input timeline but nothing can
*apply* one, so a recorded timeline is a read-only record rather than something
a second run can be driven by; and it asked for a driver that, given a timeline
and a step count, produces the state the run had using the same code path a
live run uses, "so the two cannot diverge by construction". `PL-T691` delivered
that property by a different route, which is what the analysis below works out.

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

**The narrowing, as recommended and then taken.** Drop the resimulation
driver. The item becomes: a fork opens a live run at a canonical keyframe state with its clock re-based by
subtraction, seeded through `restore_state`, sharing the live advance path
*forward* from that point rather than re-driving it up to that point. That is
the residue this brief already names - "whatever a fork needs beyond a curve".
Against it: nothing found. The argument the brief records for keeping the
driver - "stepping is what a fork resumes into" - survives the narrowing
intact, because the narrowed item is what makes a branch resumable.

**What the owner decided, 2026-09-14: narrow.** The question put was whether
to, because `ROADMAP.md`'s Required scope entry for this item read "the
mechanism by which a point *between* recorded samples is reached at all", and
that sentence is wrong under the narrowing: such a point is reached by
`state_at`, and what this item supplies is the resumption. That bullet is
re-worded in the same change, which is what made this a scope edit and so the
owner's rather than a session's.

**And the `verify:` command is writable now, which it was not while the
question stood.** The brief said one could not be written because it would have
to name a driver that may not be built; with the driver dropped, what the work
owes is a named test. It was run before being recorded and exits 1 on this
tree - `tests/integration/test_controller.py` passes its 71 tests and the
`grep` finds nothing - which is the paired shape the `docket` skill asks for
rather than a bare `-k` that would select nothing and prove the same either
way.
