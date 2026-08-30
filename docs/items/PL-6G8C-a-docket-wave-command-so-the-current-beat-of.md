---
id: PL-6G8C
title: A docket wave command, so the current beat of the rolling-wave cadence is computed rather than recalled
priority: P2
effort: M
status: done
classes: infra
feature: planning-cadence
milestone: v0.2.6
touches: subprojects/docket, ROADMAP.md
added: 2026-08-26
closed: 2026-08-29
commit: bff11d0
---

**Problem.** `ROADMAP.md` specifies a four-beat cadence per milestone — scope,
freeze the gate, clear it, implement — and nothing reports which beat the
project is on. The queue nags every session through `docket digest`; the
roadmap nags never. So a session answers "what next" from whatever ranks
highest in `docs/items/`, which is a good tool being asked a question above
its altitude.

**Why it matters.** Rolling out the wave — promoting the next coarse milestone
into a scoped one — is the only event that changes the plan. A process whose
plan cannot announce that event degrades into queue-mining, and the evidence
is already visible: `dev-tooling` sits at 1/21 while `chart-readout` is 0/4
and `teachable-case` is 0/11. Sessions do what is visible.

**Approach.** Every input is decidable from files on disk, so this is a
computation rather than a judgment:

- the current version, from `pyproject.toml`;
- which timeline row names it, from `PL-RZ9Q`'s grammar;
- whether the next milestone is scoped — does `ROADMAP.md` carry its four
  required subsections (Goal, Required scope, Definition of done, Explicitly
  out of scope)?
- whether its gate is frozen — does that section record a list of item ids?
- whether the gate is clear — item `status` in `docs/items/`, which is
  `PL-9CNQ`'s computation.

Those five compose into one answer: *clear the gate* / *implement* / *release*
/ *scope the next milestone*.

**Scope.** `docket wave` prints the current version, the timeline step, the
beat, and the next step's name. It computes; it decides nothing. Specifically
out of scope, per "Do not script the judgment": whether the prose around a
timeline row is still true, whether the gate *should* open, and whether a
scoped milestone is scoped *well*. A line that guessed at any of those would
be worse than no line, because its output would look authoritative.

**Depends on** `PL-RZ9Q` (the timeline grammar) for the step lookup, and reads
better with `PL-9CNQ` (a `docket gate` command) for the gate-clear count —
though it can ship reporting the gate as "recorded, N ids" before `PL-9CNQ`
lands, and gain the cleared/remaining split afterwards.

**Done when.** One command reports the beat from a given store and roadmap,
the output is stable for identical inputs, and regression tests over a fixture
cover each of the four beats plus the case where the next milestone is not
scoped at all.

**Context.** Design round with the project owner, 2026-08-26. The trigger is
the one part of rolling-wave planning this project did not already have; the
horizons, the elaboration ritual and the anti-early-elaboration rule were all
already in `ROADMAP.md`.

**Worked.** The grammar moved into `subprojects/docket/src/docket/roadmap.py`
rather than being duplicated or imported from `tools/`: `docket` is what
reasons about project state, `doc_check` is a checker that needs the same
rules, and both are standard-library only in a bare checkout, so the
dependency runs the way it should rather than inverting. `doc_check` inserts
the package path and imports it.

Two things the brief's five inputs did not settle, decided here:

- **The gate record, not the milestone section, decides the beat.** Testing
  each step's own section for the four scoping subsections reports v0.3.0 -
  whose entire content is the gate recorded under v0.4.0, and which says so -
  as unscoped work waiting to be written. So an open gate recorded under any
  unreleased milestone is the beat; the four-subsection test is what
  distinguishes a milestone wanting its list frozen from one wanting scoping,
  which is the only place it can decide anything.
- **A fifth outcome, `release`.** A clear gate below the milestone that
  recorded it is Gate 0's exception: the gate work ships as a version of its
  own, so the beat is to cut it, not to start the next milestone.

Gate entries are read as top-level bullets opening with an item id, which
gives 14 entries and 15 ids against the real file - the two numbers
`ROADMAP.md` states in prose. The paragraph naming what v0.4.0 clears itself
is left alone: it is a person's summary, and parsing it would mean parsing
sentences. `PL-9CNQ` (a `docket gate` command, so the frozen debt list is
computed rather than transcribed) still owns the inside/outside-scope split.

Reported against the real files: v0.2.5, step 1 of 9 (v0.3.0 - the
foundation), gate 14 entries / 6 cleared / 8 open, beat = clear the gate. The
roadmap's own transcribed count said 5 done and 9 remaining and named PL-042
among the remaining, which had closed since - so the count was replaced by a
pointer to the command rather than corrected.

Captured while here: `PL-T4YD` (surface the wave line in the session-start
digest, so the roadmap nags as the queue does).
