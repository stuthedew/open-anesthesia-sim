---
id: PL-J2TD
title: Open a live run at a canonical keyframe state with its clock re-based, which is what a fork resumes into
priority: P2
effort: M
status: done
classes: feature, refactor
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/core, tests/unit, tests/integration, docs/MODEL.md
added: 2026-09-06
closed: 2026-09-14
pr: 568
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

---

## Session of 2026-09-14: the core half built, and one question put to the owner

**Built and pushed, because it is the same under either answer to the question
below.** `AgentUptakeSystem.resume_at(state, initial_agent_l)` stands a live
system at a canonical state; `governing_equations.require_canonical_state` is
the entry guard it now shares with `RunDefinition`, so the definition and the
live system cannot come to disagree about what a state is;
`tests/unit/test_resume_at.py` holds all of it. Not built: the controller entry
point, whose clock handling *is* the question.

**Four measurements taken this session, each against the source rather than
reasoned about.** They are recorded here because they were expensive to get and
each one decides something.

1. **The accounting anchor must be carried, not derived.** Deriving it as the
   value that closes the mass-balance identity exactly returns the canonical
   path's own conservation residual with its sign reversed. Across 72 keyframes
   - three agents, four dial instants, three flow instants - **16 of them, 22%,
   put it below zero**, worst -1.1e-13 L, and an anchor is an amount of agent
   that `AgentSimulationValidator` rightly refuses below zero. Carried instead,
   the residual stays inside the check, at 6.9e-14 L against 1e-12 L.
2. **A branch's definition opens from the parent's `Keyframe`, never from the
   seeded system's `state_vector()`.** A compartment stores an amount and
   derives its fraction back from its capacity, so the round trip is not the
   identity: over a 1e-6 grid across the first two percent of an atmosphere the
   **alveolar compartment returns a different float for 11.7% of fractions**,
   mixed venous for 11.6%, fat for 3.4% - and the circuit for none, which is
   what would let it survive a spot check. `SimulationController._build_state`
   opens the trunk's definition from `state_vector()`, correctly; copying that
   line at the fork would break `ROADMAP.md` item 12's element-wise
   reproduction on exactly those entries.
3. **A branch's settings are read off the parent's compartments in L/min, never
   recovered from a `RunSegment`.** The L/min to L/s conversion does not
   round-trip for **7 of 101 cardiac outputs** across the supported range,
   first at 1.9 L/min, because the per-tissue flows are derived before it.
   Captured as `PL-SM5V`.
4. **A `SimulationState` can be constructed already past the 24 h envelope** -
   `step_count=1_000_000, simulation_step_s=0.1` gives 27.8 h - and only the
   next `advance()` refuses. Unreachable from `src/` today; reachable the
   moment a branch is constructed mid-run. Captured as `PL-BMY5`.

**The question put to the project owner: what does a branch's clock read?**
Both arrangements subtract, and both are bit-identical to the parent at every
shared instant (0 of 6 probes differ, either way), so exactness does not decide
it. What differs is what the branch's own clock *says*.

- **As documented** - the branch's definition opens at zero and a caller asks
  it for `p - fork`. Then `SimulationState.step_count` restarts at zero, and
  three consequences follow: the branch gets **a fresh 24 h run-length
  envelope**, so a fork at 23 h can be advanced to 47 h of case time with every
  guard passing, in the regime `core/supported_ranges.py` argues the omitted
  metabolism dominates; the clock, every control-change stamp and the chart
  axis - which `format_elapsed` says "state one quantity one way" - are all
  early by the fork instant; and case time has to be reconstructed as
  `origin + n*step`, a running total that
  `docs/MODEL.md` § "Simulated time is a count of steps, not a running total"
  forbids for the trunk.
- **The alternative** - `RunDefinition` takes an optional `opened_at_s`, so the
  branch's definition opens *at* the fork instant carrying the parent's
  keyframe, and the branch's `SimulationState` continues the parent's step
  count. The run-length guard is then correct with no new code; the clock, the
  stamps and the axis all read case time with no new field and no new label;
  and there is no offset a caller could name, so the round-trip hazard
  `docs/MODEL.md` records - `(900.0 + 1e-6) - 900.0` is 9.999999974752427e-07 -
  becomes unrepresentable rather than guarded against.

**The clock-disagreement figure is not the argument, and saying so matters.**
`origin + n*step` differs from the trunk's own `(k+n)*step` at the same instant,
worst measured 1.5e-11 s over the full envelope. That moves a compartment
fraction by at most 3.6e-14 and an accumulator by 7.2e-13 L, against displayed
resolutions of 1e-4 and 1e-6 L - harmless by six to nine orders. A
recommendation resting on it would be wrong.

**What the alternative costs, and one of it is a real guard rather than prose.**
`RunDefinition.__init__` gains a parameter (four lines); `docs/MODEL.md`'s
"What this requires of a branch" paragraph is nineteen lines and loses one of
its two bullets; `ROADMAP.md`'s Required-scope clause at 2589-2590 is re-worded,
which is why this is the owner's; `tests/reference/test_canonical_evaluation.py`'s
fork test gets shorter and strictly stronger; and this item's own title and
`verify:` grep name a test asserting the re-basing, so both change. Outside this
file, "re-based" appears in exactly three places in the repository.

The guard is not optional. `_require_within_run`'s lower bound is hard-coded to
`0.0`, so a definition opened at 600 s accepts an instant before its own
opening, `_segment_index_at` returns `-1`, Python indexes the **last** segment,
and `state_at(100.0)` returns a plausible state for an instant the branch never
existed at - measured at 0.005664 alveolar fraction, with
`evaluate_anchored(0, 500, 100)` drawing a *varying* curve across a span the
case spent at zero. Under the alternative that bound moves to the opening and
the failure becomes refusable; under the documented arrangement the analogous
error - handing a zero-based child a case instant once the branch is older than
the fork instant - is a legal, in-range, exact-but-wrong answer that no bounds
check can refuse, because both frames are legal non-negative floats inside the
run.

---

## Closed 2026-09-14

**Done when, against what shipped.** A run opens at a canonical keyframe state
of another run (`SimulationController.resumed_at`); its definition is re-based
by subtracting the fork instant, in `advance` and `drawn_window`; it advances
by the ordinary `advance()`, with no second way to move a run forward
introduced; an instant the parent holds no keyframe for is refused, naming the
keyframes it does hold; and
`tests/integration/test_controller.py::test_a_fork_opens_at_a_keyframe_and_rebases_its_clock`
carries the deliverable. The `verify:` command was run and exits 0.

**One judgment taken inside the approach rather than put to the owner, and
why.** The branch's *run clock* continues the case's step count. The 24 h
supported run length is enforced on that count alone, so a branch restarting it
is handed a fresh envelope - a fork at 23 h advanced to 47 h of case time with
every guard passing, in the regime `core/supported_ranges.py` argues the
omitted metabolism dominates. That is a wrong clinical claim rather than a
mechanism preference, which `CLAUDE.md`'s safety-critical standard puts outside
what a session weighs. It is also compatible with the described mechanism
rather than a substitution for it: `docs/MODEL.md`'s re-basing bullet
constrains the *definition's* clock, and the definition is re-based exactly as
written. § "What this requires of a branch" and § "Supported run length" now
say so, which they did not before.

**Filed rather than built:** `PL-SM5V` (settings cannot be recovered from a
`RunSegment`), `PL-BMY5` (a `SimulationState` constructs past the envelope),
`PL-2R2C` (a branch's drawn columns do not align with the trunk's),
`PL-ZMRT` (whether a branch's definition should open at the fork instant,
leaving one time frame - the owner's, and the evidence for it arrives with
`PL-B9PY`).

**Docs swept:** `docs/MODEL.md` (edited - the two sections above),
`ROADMAP.md` (checked: the Required-scope clause for this item describes what
shipped and needs no change), `docs/ARCHITECTURE.md` (checked: it describes
`SimulationController`'s run controls and snapshots, all still true; what a
branch *is* and what it shares with its parent is `PL-TFX5`'s to write there),
`README.md` (checked: no branch or fork claim). `make check` is green,
including the 100% branch-coverage gate on `core/`.
