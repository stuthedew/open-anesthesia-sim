---
id: PL-6G8C
title: A docket wave command, so the current beat of the rolling-wave cadence is computed rather than recalled
priority: P2
effort: M
status: blocked
blocked-by: PL-RZ9Q
classes: infra
feature: planning-cadence
touches: subprojects/docket, ROADMAP.md
added: 2026-08-26
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
